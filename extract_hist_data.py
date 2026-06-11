"""
extract_hist_data.py · Extrae KPIs de los pickles semanales y actualiza historico_data.py

Uso:
    python extract_hist_data.py              # dry-run: muestra valores sin escribir
    python extract_hist_data.py --apply      # actualiza historico_data.py en disco
    python extract_hist_data.py --week 24    # sobreescribir número de semana

El script:
1. Lee los pickles CR, RND y BK de la semana actual (usa VOL_NUM del entorno o --week)
2. Extrae las 4 métricas × 4 scopes (global, op, cug, b2c) = hasta 16 valores
3. Desplaza la ventana histórica: descarta la semana más antigua, agrega la nueva
4. Escribe historico_data.py con los arrays actualizados

Ventana: máximo 8 semanas. Al llegar a 8 se descarta la primera (móvil).
"""

import os, sys, pickle, re, argparse
from pathlib import Path

# ── Args ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Actualiza historico_data.py con KPIs del pickle semanal")
parser.add_argument("--apply",  action="store_true", help="Escribir cambios en historico_data.py")
parser.add_argument("--week",   type=int, default=None, help="Número de semana (ej. 24). Default: VOL_NUM del env")
parser.add_argument("--dir",    default=".", help="Directorio donde buscar los pickles (default: .)")
args = parser.parse_args()

SCRIPT_DIR = Path(__file__).parent
HIST_FILE  = SCRIPT_DIR / "historico_data.py"

# ── Número de semana ──────────────────────────────────────────────────────────
week_num = args.week or int(os.getenv("VOL_NUM", "0"))
if not week_num:
    print("❌ Indicar el número de semana con --week NN o setear VOL_NUM en el entorno.")
    sys.exit(1)

search_dir = Path(args.dir)
print(f"📦 Extrayendo KPIs de W{week_num} (directorio: {search_dir.resolve()})")

# ── Cargar pickles ────────────────────────────────────────────────────────────
def find_pickle(prefix):
    """Busca el pickle por prefijo en search_dir."""
    for p in search_dir.glob(f"{prefix}*w{week_num}*.pkl"):
        return p
    for p in search_dir.glob(f"{prefix}*{week_num}*.pkl"):
        return p
    return None

def load_pickle(prefix, label):
    path = find_pickle(prefix)
    if path is None:
        print(f"  ⚠  Pickle {label} no encontrado en {search_dir} (patrón: {prefix}*w{week_num}*.pkl)")
        return None
    with open(path, "rb") as f:
        d = pickle.load(f)
    print(f"  ✅ {label}: {path.name}")
    return d

D_cr  = load_pickle("cr_w",  "CR")
D_rnd = load_pickle("rnd_w", "RND")
D_bk  = load_pickle("bk_w",  "BK")

if not D_cr or not D_rnd:
    print("❌ Pickles CR y RND son obligatorios.")
    sys.exit(1)

# ── Extraer KPIs ──────────────────────────────────────────────────────────────
M_cr  = D_cr.get("M", {})
M_rnd = D_rnd.get("M", {})

# Mapa de scope → key en M
SCOPE_KEYS_CR = {
    "global": f"global_w{week_num}",
    "b2c":    f"B2C_w{week_num}",
    "op":     f"B2B-OP_w{week_num}",
    "cug":    f"CUG_w{week_num}",
}
SCOPE_KEYS_RND = {
    "global": f"global_w{week_num}",
    "b2c":    f"B2C_w{week_num}",
    "op":     f"B2B-OP_w{week_num}",
    "cug":    f"CUG_w{week_num}",
}

def safe_get(d, key, subkey, default=None):
    return d.get(key, {}).get(subkey, default)

extracted = {
    "cr": {
        "eficacia": {},
        "convrate": {},
    },
    "rnd": {
        "nodispo": {},
        "ipm": {},
    },
    "bk": {
        "bookability": {},
    },
}

print(f"\n📊 Valores extraídos para W{week_num}:")

for scope, key in SCOPE_KEYS_CR.items():
    ef = safe_get(M_cr, key, "eficacia")
    cv = safe_get(M_cr, key, "conv_rate")
    if ef is not None:
        extracted["cr"]["eficacia"][scope] = round(ef * 100, 4)
    if cv is not None:
        extracted["cr"]["convrate"][scope] = round(cv * 100, 4)
    print(f"  CR  {scope:8}: Eficacia={ef*100:.2f}% | ConvRate={cv*100:.4f}%" if ef is not None else f"  CR  {scope}: ⚠ sin datos")

for scope, key in SCOPE_KEYS_RND.items():
    nd  = safe_get(M_rnd, key, "pct_nodispo") or safe_get(M_rnd, key, "nodispo")
    ipm = safe_get(M_rnd, key, "ipm") or safe_get(M_rnd, key, "rpm")
    if nd is not None:
        extracted["rnd"]["nodispo"][scope] = round(nd * 100, 4)
    if ipm is not None:
        extracted["rnd"]["ipm"][scope] = round(ipm, 2)
    print(f"  RND {scope:8}: NoDispo={nd*100:.2f}% | IPM=${ipm:.0f}" if nd is not None else f"  RND {scope}: ⚠ sin datos")

if D_bk:
    bk = D_bk.get("bk_global")
    if bk is not None:
        extracted["bk"]["bookability"]["global"] = round(bk * 100, 4)
        print(f"  BK  global  : Bookability={bk*100:.2f}%")

# ── Leer historico_data.py actual ─────────────────────────────────────────────
if not HIST_FILE.exists():
    print(f"\n❌ No se encontró {HIST_FILE}")
    sys.exit(1)

hist_src = HIST_FILE.read_text(encoding="utf-8")

# ── Importar HIST_DATA y SEMANAS actuales ────────────────────────────────────
exec_ns = {}
exec(hist_src, exec_ns)
HIST_DATA = exec_ns["HIST_DATA"]
SEMANAS   = exec_ns["SEMANAS"]
MAX_SEMANAS = 8

print(f"\n📅 Semanas actuales: {SEMANAS}")

new_week_label = f"W{week_num}"
if new_week_label in SEMANAS:
    print(f"⚠  W{week_num} ya está en SEMANAS — se sobreescribirá el último valor.")
    # Quitar la última entrada y re-agregar
    SEMANAS = SEMANAS[:-1]

# Ventana móvil: si ya tenemos MAX_SEMANAS, descartar la primera
if len(SEMANAS) >= MAX_SEMANAS:
    descartada = SEMANAS[0]
    SEMANAS = SEMANAS[1:]
    print(f"  → Ventana completa: descartando {descartada}")

SEMANAS_NEW = SEMANAS + [new_week_label]
print(f"  → Nueva ventana: {SEMANAS_NEW}")

# ── Actualizar arrays en HIST_DATA ───────────────────────────────────────────
def update_arrays(hist_data, extracted, semanas_old):
    """Añade el nuevo valor al final de cada array y descarta el primero si ventana llena."""
    cambios = []
    for reporte, metricas in extracted.items():
        for metrica, scopes in metricas.items():
            for scope, new_val in scopes.items():
                base = hist_data.get(reporte, {}).get(metrica, {}).get(scope)
                if base is None:
                    cambios.append(f"  ⚠ {reporte}.{metrica}.{scope}: no existe en HIST_DATA — omitido")
                    continue
                old_len = len(base)
                # Si ya tiene tantos valores como semanas_old → agregar al final
                # Si tiene más (ya se actualizó antes) → sobreescribir último
                if len(base) > len(semanas_old):
                    base = base[:-1]  # quitar el último (se va a reemplazar)
                # Ventana móvil: si ya en MAX_SEMANAS-1, descartar primero
                if len(base) >= MAX_SEMANAS - 1:
                    base = base[1:]
                base = base + [new_val]
                hist_data[reporte][metrica][scope] = base
                cambios.append(f"  ✅ {reporte}.{metrica}.{scope}: {old_len} → {len(base)} vals, último={new_val}")
    return cambios

cambios = update_arrays(HIST_DATA, extracted, SEMANAS)
for c in cambios:
    print(c)

# ── Regenerar historico_data.py ──────────────────────────────────────────────
def format_arr(arr, indent=12):
    sp = " " * indent
    items = ", ".join(f"{v}" for v in arr)
    return f"[{items}]"

semanas_str   = "[" + ", ".join(f"'{s}'" for s in SEMANAS_NEW) + "]"
header_labels = "  ".join(SEMANAS_NEW[:-1])  # sin la última (es la semana actual, dinámica)

new_src_lines = [
    '"""',
    'historico_data.py · Datos históricos reales para módulos de evolución histórica.',
    '',
    'Generado automáticamente por extract_hist_data.py.',
    f'Última actualización: W{week_num}',
    '',
    'Estructura:',
    '    HIST_DATA[reporte][metrica][scope] = array de valores históricos',
    '    La semana actual se agrega dinámicamente desde el pickle en runtime.',
    '',
    'Scopes: global · op (B2B-OP) · cug (CUG/UOP) · b2c',
    '"""',
    '',
    f'SEMANAS = {semanas_str}',
    '',
    'HIST_DATA = {',
]

for reporte, metricas in HIST_DATA.items():
    new_src_lines.append(f"    '{reporte}': {{")
    for metrica, scopes in metricas.items():
        new_src_lines.append(f"        '{metrica}': {{")
        for scope, arr in scopes.items():
            new_src_lines.append(f"            '{scope}': {format_arr(arr)},")
        new_src_lines.append("        },")
    new_src_lines.append("    },")

new_src_lines.append("}")
new_src_lines.append("")

# Preservar las funciones (get_serie, etc.) del archivo original
fn_start = hist_src.find("\n\ndef ")
if fn_start > 0:
    new_src_lines.append("")
    new_src_lines.append(hist_src[fn_start:].strip())
    new_src_lines.append("")

new_src = "\n".join(new_src_lines)

# ── Dry-run o apply ───────────────────────────────────────────────────────────
if args.apply:
    HIST_FILE.write_text(new_src, encoding="utf-8")
    print(f"\n✅ historico_data.py actualizado ({len(new_src):,} chars)")
else:
    print(f"\n📋 DRY-RUN — historico_data.py NO modificado")
    print(f"   Ejecutar con --apply para escribir los cambios")
    print(f"\n--- Preview SEMANAS ---")
    print(f"  SEMANAS = {SEMANAS_NEW}")
    print(f"\n--- Preview global CR ---")
    print(f"  eficacia: {HIST_DATA['cr']['eficacia']['global']}")
    print(f"  convrate: {HIST_DATA['cr']['convrate']['global']}")
    print(f"\n--- Preview global RND ---")
    print(f"  nodispo:  {HIST_DATA['rnd']['nodispo']['global']}")
    print(f"  ipm:      {HIST_DATA['rnd']['ipm']['global']}")
    if "bk" in HIST_DATA and "bookability" in HIST_DATA["bk"]:
        print(f"\n--- Preview global BK ---")
        print(f"  bookability: {HIST_DATA['bk']['bookability']['global']}")
