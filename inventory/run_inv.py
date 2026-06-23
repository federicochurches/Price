"""
run_inv.py — Wrapper transparente del pipeline Hotel Inventory
═══════════════════════════════════════════════════════════════════

Resuelve los puntos de fricción detectados en W23 (vigente para W24+):
  1. Correr desde la carpeta equivocada       → valida CWD antes de arrancar
  2. El script no regenera si el HTML existe   → borra el HTML viejo automáticamente
  3. Versiones desincronizadas del calc_inv.py → verifica fixes canónicos antes de correr
  4. Push de archivos grandes falla silencioso → commitea por Git Tree API (no GitHub Desktop)
  5. HTML sin optimizar (44MB) servido en prod → verifica tamaño y compara con el repo

USO:
    cd C:\\Users\\federico.iglesias\\Price\\inventory
    python run_inv.py              # corre + verifica, NO commitea (default seguro)
    python run_inv.py --commit     # corre + verifica + commitea HTML por Git Tree API

Cada paso imprime qué hizo y verifica el resultado antes de seguir.
Si algo falla, se detiene con un mensaje claro indicando dónde y por qué.
"""

import sys
import os
import re
import json
import base64
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG del repo (no cambia entre semanas)
# ─────────────────────────────────────────────
REPO          = "federicochurches/Price"
BRANCH        = "main"
REPO_SUBPATH  = "inventory"                 # ruta dentro del repo donde vive calc_inv.py
TOKEN_PATH    = Path("../text3.txt")        # el token vive en la raíz del repo
SIZE_WARN_MB  = 15.0                         # alerta si el HTML supera esto (optimización rota)
SIZE_HARD_MB  = 25.0                         # error duro: algo está muy mal

# Fixes canónicos que el calc_inv.py DEBE tener (verificación de versión)
CANONICAL_CHECKS = {
    "VS GLOBAL ocultas (sin <td>—</td> sin clase)":
        lambda s: '<td>—</td>' not in s,
    "% Gap junto a Hoteles (header Third Party)":
        lambda s: 'Hoteles</th><th>% Gap</th><th>Destinos</th><th>% Gap</th>' in s,
    "_ppRatio dinámico (no hardcodeado)":
        lambda s: '{pp} / {N}' in s,
    "snapshot eliminado (optimización presente)":
        lambda s: 'dim_ch' in s and 'dim_hotel' in s and 'HIST.snapshot' not in s,
}

C_OK   = "\033[92m"   # verde
C_WARN = "\033[93m"   # amarillo
C_ERR  = "\033[91m"   # rojo
C_DIM  = "\033[90m"   # gris
C_END  = "\033[0m"

def _c(txt, color):
    # Windows PowerShell moderno soporta ANSI; si no, queda el texto plano
    return f"{color}{txt}{C_END}"

def step(n, total, msg):
    print(f"\n{_c(f'[{n}/{total}]', C_DIM)} {msg}")

def ok(msg):
    print(f"   {_c('✓', C_OK)} {msg}")

def warn(msg):
    print(f"   {_c('⚠', C_WARN)} {msg}")

def die(msg):
    print(f"\n{_c('✗ ABORTADO:', C_ERR)} {msg}\n")
    sys.exit(1)


# ─────────────────────────────────────────────
# PASO 1 — Validar entorno
# ─────────────────────────────────────────────
def validate_environment():
    step(1, 6, "Validando entorno...")
    cwd = Path.cwd()

    # 1a. ¿Estamos en inventory/? (debe existir calc_inv.py acá)
    calc = cwd / "calc_inv.py"
    if not calc.exists():
        die(f"No encuentro calc_inv.py en {cwd}\n"
            f"   Estás en la carpeta equivocada. Corré primero:\n"
            f"   cd C:\\Users\\federico.iglesias\\Price\\{REPO_SUBPATH}")
    ok(f"calc_inv.py encontrado en {cwd.name}/")

    # 1b. Leer CONFIG (WEEK, WEEK_NUM, INPUT_FILE)
    src = calc.read_text(encoding="utf-8")
    def _cfg(key, cast=str):
        m = re.search(rf'^{key}\s*=\s*"?([^"#\n]+)"?', src, re.M)
        if not m:
            die(f"No pude leer {key} del CONFIG de calc_inv.py")
        return cast(m.group(1).strip().strip('"'))
    week     = _cfg("WEEK")
    week_num = _cfg("WEEK_NUM", int)
    inp      = _cfg("INPUT_FILE")
    ok(f"CONFIG: WEEK={week} · WEEK_NUM={week_num} · INPUT_FILE={inp}")

    # 1c. ¿Existe el dataset de input?
    if not (cwd / inp).exists():
        die(f"No encuentro el dataset de input '{inp}' en {cwd}\n"
            f"   Copiá el archivo de contratos a esta carpeta antes de correr.")
    ok(f"Dataset de input '{inp}' presente")

    # 1d. ¿El token es legible? (solo si vamos a commitear)
    if "--commit" in sys.argv:
        if not TOKEN_PATH.exists():
            die(f"No encuentro el token en {TOKEN_PATH.resolve()}")
        token = TOKEN_PATH.read_text(encoding="utf-8-sig").strip()
        if not token.startswith("ghp_") and not token.startswith("github_pat_"):
            warn("El token no tiene el prefijo esperado (ghp_ / github_pat_)")
        ok("Token GitHub legible")

    return week, week_num, src


# ─────────────────────────────────────────────
# PASO 2 — Verificar versión del calc_inv.py
# ─────────────────────────────────────────────
def verify_script_version(src):
    step(2, 6, "Verificando que calc_inv.py tenga todos los fixes canónicos...")
    fails = []
    for name, check in CANONICAL_CHECKS.items():
        if check(src):
            ok(name)
        else:
            fails.append(name)
            warn(f"FALTA: {name}")
    if fails:
        die(f"El calc_inv.py NO tiene {len(fails)} fix(es) canónico(s).\n"
            f"   Estás por correr una versión vieja. Reemplazá el archivo por la\n"
            f"   última versión antes de continuar.")
    ok("Todos los fixes canónicos presentes — versión correcta")


# ─────────────────────────────────────────────
# PASO 3 — Limpiar HTML viejo
# ─────────────────────────────────────────────
def clean_old_output(week, week_num):
    step(3, 6, "Limpiando output viejo...")
    out_dir  = Path(f"week-{week_num:02d}")
    out_html = out_dir / f"INVENTORY_{week}.html"
    if out_html.exists():
        size_mb = out_html.stat().st_size / 1024 / 1024
        out_html.unlink()
        ok(f"Borrado {out_html} ({size_mb:.1f} MB) — calc_inv.py no regenera si existe")
    else:
        ok(f"No había {out_html} previo")
    return out_dir, out_html


# ─────────────────────────────────────────────
# PASO 4 — Correr calc_inv.py
# ─────────────────────────────────────────────
def run_calc():
    step(4, 6, "Corriendo calc_inv.py...")
    print(_c("   ─── salida de calc_inv.py ───", C_DIM))
    result = subprocess.run(
        [sys.executable, "calc_inv.py"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    for line in (result.stdout or "").splitlines():
        print(f"   {C_DIM}│{C_END} {line}")
    if result.returncode != 0:
        print(_c("   ─── stderr ───", C_ERR))
        for line in (result.stderr or "").splitlines():
            print(f"   {C_ERR}│{C_END} {line}")
        die(f"calc_inv.py terminó con error (returncode={result.returncode})")
    ok("calc_inv.py terminó sin errores")


# ─────────────────────────────────────────────
# PASO 5 — Verificar output generado
# ─────────────────────────────────────────────
def verify_output(out_html):
    step(5, 6, "Verificando el HTML generado...")
    if not out_html.exists():
        die(f"calc_inv.py corrió pero no generó {out_html}")
    size_mb = out_html.stat().st_size / 1024 / 1024
    if size_mb >= SIZE_HARD_MB:
        die(f"El HTML pesa {size_mb:.1f} MB (límite duro {SIZE_HARD_MB} MB).\n"
            f"   La optimización está rota — revisá que dim_ch/dim_hotel estén compactos\n"
            f"   y que HIST.snapshot NO se esté generando.")
    if size_mb >= SIZE_WARN_MB:
        warn(f"El HTML pesa {size_mb:.1f} MB (esperado ~12 MB). "
             f"Revisá la optimización, pero se puede continuar.")
    else:
        ok(f"HTML generado: {out_html} ({size_mb:.1f} MB)")

    # Verificación de contenido (que los fixes hayan quedado en el output)
    html = out_html.read_text(encoding="utf-8", errors="ignore")
    if '<td>—</td>' in html:
        warn("Hay celdas <td>—</td> sin clase td-vs en el HTML (columna VS GLOBAL visible)")
    else:
        ok("Sin columna VS GLOBAL suelta en el HTML")
    return size_mb


# ─────────────────────────────────────────────
# PASO 6 — Commit por Git Tree API
# ─────────────────────────────────────────────
def _api(method, url, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        die(f"GitHub API {method} {url.split('/repos/')[-1]} → HTTP {e.code}\n   {body[:300]}")


def commit_via_tree_api(week, week_num, out_html, local_size_mb):
    step(6, 6, "Commiteando HTML por Git Tree API (método confiable para archivos grandes)...")
    token = TOKEN_PATH.read_text(encoding="utf-8-sig").strip()
    repo_path = f"{REPO_SUBPATH}/week-{week_num:02d}/INVENTORY_{week}.html"

    # 1. HEAD ref
    head = _api("GET", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}", token)
    head_sha = head["object"]["sha"]
    ok(f"HEAD: {head_sha[:8]}")

    # 2. base tree
    commit = _api("GET", f"https://api.github.com/repos/{REPO}/git/commits/{head_sha}", token)
    base_tree = commit["tree"]["sha"]

    # 3. blob (archivo en base64)
    content_b64 = base64.b64encode(out_html.read_bytes()).decode()
    blob = _api("POST", f"https://api.github.com/repos/{REPO}/git/blobs", token,
                {"content": content_b64, "encoding": "base64"})
    blob_sha = blob["sha"]
    ok(f"Blob creado: {blob_sha[:8]} ({local_size_mb:.1f} MB)")

    # 4. tree
    tree = _api("POST", f"https://api.github.com/repos/{REPO}/git/trees", token, {
        "base_tree": base_tree,
        "tree": [{"path": repo_path, "mode": "100644", "type": "blob", "sha": blob_sha}],
    })

    # 5. commit
    msg = f"feat: Inventory {week} HTML ({local_size_mb:.1f}MB) via run_inv.py"
    new_commit = _api("POST", f"https://api.github.com/repos/{REPO}/git/commits", token, {
        "message": msg, "tree": tree["sha"], "parents": [head_sha],
    })
    ok(f"Commit: {new_commit['sha'][:8]} — \"{msg}\"")

    # 6. update ref
    _api("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}", token,
         {"sha": new_commit["sha"], "force": False})
    ok(f"Rama {BRANCH} actualizada")

    # 7. Verificar tamaño en el repo (lo que Netlify va a servir)
    print(f"   {C_DIM}Verificando tamaño en el repo...{C_END}")
    raw_url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{repo_path}"
    req = urllib.request.Request(raw_url, method="HEAD")
    req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req) as r:
            repo_bytes = int(r.headers.get("content-length", 0))
        repo_mb = repo_bytes / 1024 / 1024
        if abs(repo_mb - local_size_mb) < 0.2:
            ok(f"Repo confirmado: {repo_mb:.1f} MB (coincide con el local)")
        else:
            warn(f"Repo tiene {repo_mb:.1f} MB vs local {local_size_mb:.1f} MB — "
                 f"puede ser caché de GitHub, reintentá en 1 min")
    except Exception as e:
        warn(f"No pude verificar el tamaño en el repo ({e}). Verificá manualmente.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    do_commit = "--commit" in sys.argv
    print(_c("\n═══ run_inv.py · Pipeline Hotel Inventory ═══", C_OK))
    if not do_commit:
        print(_c("   modo: correr + verificar (sin commit). Usá --commit para subir al repo.", C_DIM))

    week, week_num, src = validate_environment()
    verify_script_version(src)

    # Backup automático del dataset (copia local con número de semana)
    import shutil as _shutil
    _inp = _cfg("INPUT_FILE") if True else "dataHoteles_contratos.xlsx"
    _backup = Path(f"dataHoteles_contratos_{week}.xlsx")
    _inp_path = Path(_inp)
    if _inp_path.exists() and not _backup.exists():
        _shutil.copy2(_inp_path, _backup)
        ok(f"Backup creado: {_backup.name} ({_backup.stat().st_size/1024/1024:.1f} MB)")
    elif _backup.exists():
        ok(f"Backup ya existe: {_backup.name}")

    out_dir, out_html = clean_old_output(week, week_num)
    run_calc()
    size_mb = verify_output(out_html)

    if do_commit:
        commit_via_tree_api(week, week_num, out_html, size_mb)
        print(_c(f"\n✅ {week} generado y commiteado. Netlify redeploya en ~1-2 min.", C_OK))
    else:
        print(_c(f"\n✅ {week} generado y verificado localmente.", C_OK))
        print(_c(f"   Para subir al repo: python run_inv.py --commit", C_DIM))
    print()


if __name__ == "__main__":
    main()

