#!/usr/bin/env python3
"""
update_docs.py · Actualización automática de docs antes del commit PRICE

Actualiza 5 archivos en /tmp (que luego van al commit y al ZIP):
  - PROMPT_CORE.md       → tabla de datos históricos + última actualización
  - HISTORIAL_SESIONES.md → agrega entrada de sesión (pipeline o fix)
  - README_QUICK.md       → bloque "Última semana publicada" con KPIs y URLs
  - CHANGELOG_NIVEL3.md  → entrada pipeline/fix con KPIs WoW
  - historico_data.py    → SEMANAS + arrays HIST_DATA (solo en modo pipeline)

Uso:
    python3 update_docs.py --week 21 --periodo "18-24 may 2026" --tipo pipeline
    python3 update_docs.py --week 21 --tipo fix --mensaje "Fix Canal CR"

Se llama automáticamente desde github_commit.py antes del ZIP y commit.
"""

import argparse
import pickle
import os
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_pickle(path):
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None

def _pct(v):   return f"{v:.2f}%".replace('.', ',')
def _usd(v):   return f"${v:,.0f}".replace(',', '.')
def _pp(v):    return f"{v:+.2f}pp".replace('.', ',')


def _find(filename, scripts_dir):
    """Busca el archivo en scripts_dir primero, luego en el project dir."""
    for d in [Path(scripts_dir), SCRIPT_DIR]:
        p = d / filename
        if p.exists():
            return p
    return Path(scripts_dir) / filename  # fallback (se creará)


# ── Extracción de KPIs ───────────────────────────────────────────────────────

def extract_kpis(week_num, scripts_dir):
    """Extrae KPIs globales y por canasta de los pickles W{N} y W{N-1}."""
    kpis = {}
    rnd = _load_pickle(Path(scripts_dir) / f'rnd_w{week_num}_data.pkl')
    cr  = _load_pickle(Path(scripts_dir) / f'cr_w{week_num}_data.pkl')

    if rnd:
        M = rnd.get('M', {})
        cur  = M.get(f'global_w{week_num}', {})
        prev = M.get(f'global_w{week_num-1}', {})
        nd   = cur.get('pct_nodispo', 0) * 100
        nd_p = prev.get('pct_nodispo', 0) * 100
        ipm  = cur.get('rpm', cur.get('ipm', 0))
        ipm_p = prev.get('rpm', prev.get('ipm', 0))
        kpis['rnd_nd']      = _pct(nd)
        kpis['rnd_nd_prev'] = _pct(nd_p)
        kpis['rnd_nd_wow']  = _pp(nd - nd_p)
        kpis['rnd_ipm']     = _usd(ipm)
        kpis['rnd_ipm_prev']= _usd(ipm_p)
        kpis['rnd_ipm_wow'] = f"{(ipm-ipm_p)/max(ipm_p,1)*100:+.1f}%".replace('.',',')

        # Por canasta (para historico_data)
        kpis['rnd_canastas'] = {}
        for dist, label in [('B2B (OP)','op'),('CUG (UOP)','cug'),('B2C','b2c')]:
            c_cur = M.get(f'{dist}_w{week_num}', {})
            kpis['rnd_canastas'][label] = {
                'nd':  round(c_cur.get('pct_nodispo', 0) * 100, 2),
                'ipm': round(c_cur.get('rpm', c_cur.get('ipm', 0)), 0),
            }
        kpis['rnd_canastas']['global'] = {
            'nd': round(nd, 2), 'ipm': round(ipm, 0)
        }

    if cr:
        p80 = cr.get('p80_hotel', None)
        df18 = cr.get('df18', None)
        if p80 is not None and not p80.empty:
            import pandas as pd
            ef  = p80['Successful'].sum() / max(p80['CR_Unicos'].sum(), 1) * 100
            cv  = p80['Bookings'].sum()   / max(p80['CR_Unicos'].sum(), 1) * 100
            kpis['cr_ef']  = _pct(ef)
            kpis['cr_cv']  = _pct(cv)

            # WoW desde df18 (semana anterior)
            if df18 is not None:
                suc_col = next((c for c in df18.columns if 'Successful UniqueChkRts' in c), None)
                cr_col  = next((c for c in df18.columns if 'CR_Unicos' in c), None)
                if suc_col and cr_col:
                    ef_p = df18[suc_col].sum() / max(df18[cr_col].sum(), 1) * 100
                    cv_p = df18['Bookings'].sum() / max(df18[cr_col].sum(), 1) * 100
                    kpis['cr_ef_prev'] = _pct(ef_p)
                    kpis['cr_cv_prev'] = _pct(cv_p)
                    kpis['cr_ef_wow']  = _pp(ef - ef_p)
                    kpis['cr_cv_wow']  = _pp(cv - cv_p)

            # Por canasta
            kpis['cr_canastas'] = {'global': {'ef': round(ef,2), 'cv': round(cv,2)}}
            can_map = cr.get('CANASTA', {})
            for can, label in [('B2B-OP','op'),('CUG','cug'),('B2C','b2c')]:
                p80c = can_map.get(can, {}).get('p80', None)
                if p80c is not None and not p80c.empty:
                    ef_c = p80c['Successful'].sum() / max(p80c['CR_Unicos'].sum(),1) * 100
                    cv_c = p80c['Bookings'].sum()   / max(p80c['CR_Unicos'].sum(),1) * 100
                    kpis['cr_canastas'][label] = {'ef': round(ef_c,2), 'cv': round(cv_c,2)}

    return kpis


# ── historico_data.py ────────────────────────────────────────────────────────

def update_historico(week_num, kpis, scripts_dir):
    """Agrega W{N-1} a los arrays y actualiza SEMANAS para que W{N} sea el dinámico."""
    path = _find('historico_data.py', scripts_dir)
    if not path.exists():
        print(f"  ⚠️  historico_data.py no encontrado en {scripts_dir}")
        return

    with open(path) as f:
        c = f.read()

    # Leer SEMANAS actual
    m = re.search(r"SEMANAS\s*=\s*\[([^\]]+)\]", c)
    if not m:
        print("  ⚠️  SEMANAS no encontrado en historico_data.py")
        return

    semanas = [s.strip().strip('"\'') for s in m.group(1).split(',')]
    last_in_hist = semanas[-1]   # ej. "W21" → el dinámico
    new_week_label = f"W{week_num}"

    if last_in_hist == new_week_label:
        print(f"  ℹ️  historico_data.py ya está actualizado para W{week_num}")
        return

    # La semana a agregar a los arrays es la anterior (W{N-1} = last_in_hist)
    prev_week = week_num - 1
    prev_label = f"W{prev_week}"

    # Verificar que la última semana en SEMANAS es la anterior
    if last_in_hist != prev_label:
        print(f"  ⚠️  SEMANAS[-1]={last_in_hist}, esperado {prev_label} — salteando historico")
        return

    # Construir nuevas SEMANAS (ventana deslizante, descartar la primera)
    new_semanas = semanas[1:] + [new_week_label]

    # Valores a insertar (W{N-1} — ya está en el pickle como val_actual de la semana pasada)
    # Usamos los kpis extraídos del df18 del pickle actual
    rnd_c = kpis.get('rnd_canastas', {})
    cr_c  = kpis.get('cr_canastas', {})

    def _insert(c, key_path, new_val):
        """Inserta new_val al final del array HIST_DATA[...][...][scope] y quita el primero."""
        pattern = re.compile(
            r"('" + key_path[0] + r"'\s*:\s*\{[^}]*'" + key_path[1] + r"'\s*:\s*\{[^}]*'" + key_path[2] + r"'\s*:\s*\[)([^\]]+)(\])",
            re.DOTALL
        )
        # Más simple: buscar por línea
        return c

    # Reemplazar todo el bloque HIST_DATA con los nuevos valores
    # Leer valores actuales desde el archivo
    hist_match = re.search(r'HIST_DATA\s*=\s*(\{.*?\n\})', c, re.DOTALL)
    if not hist_match:
        print("  ⚠️  HIST_DATA no encontrado")
        return

    # Parsear arrays actuales con regex por scope
    def get_arr(text, reporte, metrica, scope):
        pat = re.compile(
            rf"'(?:{reporte})'\s*:.*?'(?:{metrica})'\s*:.*?'(?:{scope})'\s*:\s*\[([^\]]+)\]",
            re.DOTALL
        )
        m2 = pat.search(text)
        if not m2: return []
        return [float(x.strip()) for x in m2.group(1).split(',')]

    hist_block = hist_match.group(1)

    # Rotar arrays: quitar primero, agregar nuevo valor W{N-1}
    def rotate(arr, new_val):
        return arr[1:] + [new_val]

    # Valores W{N-1} que insertamos (son los que ya estaban como "actuales" de la semana pasada)
    # Para RND: los tenemos en kpis['rnd_canastas'] (vienen del pickle actual via df18)
    # Para CR: los tenemos en kpis['cr_canastas'] (df18 del pickle actual)
    rnd_vals = {
        'global': (rnd_c.get('global',{}).get('nd', None), rnd_c.get('global',{}).get('ipm', None)),
        'op':     (rnd_c.get('op',{}).get('nd', None),     rnd_c.get('op',{}).get('ipm', None)),
        'cug':    (rnd_c.get('cug',{}).get('nd', None),    rnd_c.get('cug',{}).get('ipm', None)),
        'b2c':    (rnd_c.get('b2c',{}).get('nd', None),    rnd_c.get('b2c',{}).get('ipm', None)),
    }
    cr_vals = {
        'global': (cr_c.get('global',{}).get('ef', None), cr_c.get('global',{}).get('cv', None)),
        'op':     (cr_c.get('op',{}).get('ef', None),     cr_c.get('op',{}).get('cv', None)),
        'cug':    (cr_c.get('cug',{}).get('ef', None),    cr_c.get('cug',{}).get('cv', None)),
        'b2c':    (cr_c.get('b2c',{}).get('ef', None),    cr_c.get('b2c',{}).get('cv', None)),
    }

    if any(v[0] is None for v in rnd_vals.values()) or any(v[0] is None for v in cr_vals.values()):
        print(f"  ⚠️  KPIs W{prev_week} incompletos — historico_data.py no actualizado")
        return

    # Construir nuevo contenido
    scopes = ['global', 'op', 'cug', 'b2c']

    def fmt_arr(arr): return '[' + ', '.join(str(v) for v in arr) + ']'

    new_hist = f"""HIST_DATA = {{
    'cr': {{
        'eficacia': {{"""
    for sc in scopes:
        arr = get_arr(hist_block, 'cr', 'eficacia', sc)
        new_arr = rotate(arr, cr_vals[sc][0]) if arr else [cr_vals[sc][0]]
        new_hist += f"\n            '{sc}': {fmt_arr(new_arr)},"
    new_hist += "\n        },\n        'convrate': {"
    for sc in scopes:
        arr = get_arr(hist_block, 'cr', 'convrate', sc)
        new_arr = rotate(arr, cr_vals[sc][1]) if arr else [cr_vals[sc][1]]
        new_hist += f"\n            '{sc}': {fmt_arr(new_arr)},"
    new_hist += "\n        },\n    },\n    'rnd': {\n        'nodispo': {"
    for sc in scopes:
        arr = get_arr(hist_block, 'rnd', 'nodispo', sc)
        new_arr = rotate(arr, rnd_vals[sc][0]) if arr else [rnd_vals[sc][0]]
        new_hist += f"\n            '{sc}': {fmt_arr(new_arr)},"
    new_hist += "\n        },\n        'ipm': {"
    for sc in scopes:
        arr = get_arr(hist_block, 'rnd', 'ipm', sc)
        new_arr = rotate(arr, rnd_vals[sc][1]) if arr else [rnd_vals[sc][1]]
        new_hist += f"\n            '{sc}': {fmt_arr(new_arr)},"
    new_hist += "\n        },\n    },\n}"

    # Actualizar SEMANAS y HIST_DATA en el contenido
    new_semanas_str = '[' + ', '.join(f'"{s}"' for s in new_semanas) + ']'
    c = re.sub(r'SEMANAS\s*=\s*\[[^\]]+\]', f'SEMANAS = {new_semanas_str}', c)
    c = re.sub(r'HIST_DATA\s*=\s*\{.*?\n\}', new_hist, c, flags=re.DOTALL)

    # Actualizar comentario de ventana y docstring
    c = re.sub(r'Serie real W\d+-W\d+', f'Serie real {new_semanas[0]}-{new_semanas[-2]}', c)
    c = re.sub(r'W{N} es el dinámico.*', f'{new_week_label} es el dinámico desde el pickle en runtime.', c)

    with open(path, 'w') as f:
        f.write(c)
    print(f"  ✅ historico_data.py: SEMANAS {new_semanas} · W{prev_week} incorporado · W{week_num} dinámico")


# ── PROMPT_CORE.md ───────────────────────────────────────────────────────────

def update_prompt_core(week_num, periodo, mes_anio, kpis, tipo, mensaje, scripts_dir):
    path = _find('PROMPT_CORE.md', scripts_dir)
    if not path.exists(): return

    with open(path) as f: c = f.read()

    # Actualizar tabla de datos históricos si hay KPIs
    if tipo == 'pipeline' and kpis.get('rnd_nd') and kpis.get('cr_ef'):
        # Buscar la tabla histórica y agregar la fila de la semana actual
        nd  = kpis['rnd_nd']
        ipm = kpis['rnd_ipm']
        ef  = kpis['cr_ef']
        cv  = kpis['cr_cv']
        nueva_fila = f"| W{week_num} | {ef} | {cv} | {nd} | {ipm} |"

        # Si la fila de W{week_num} ya existe, reemplazarla
        if f'| W{week_num} |' in c:
            c = re.sub(rf'\| W{week_num} \|[^\n]+', nueva_fila, c)
        else:
            # Insertar después de la última fila de la tabla histórica
            m = re.search(r'(\| W\d+ \|[^\n]+\n)(?!\| W)', c)
            if m:
                c = c[:m.end()] + nueva_fila + '\n' + c[m.end():]

    # Actualizar última línea
    suffix = f"W{week_num} ({tipo}) · {mes_anio}"
    if mensaje:
        suffix += f" · {mensaje[:60]}"
    c = re.sub(r'\*\*Última actualización:\*\*.+', f'**Última actualización:** {suffix}', c)

    with open(path, 'w') as f: f.write(c)
    print(f"  ✅ PROMPT_CORE.md actualizado")


# ── HISTORIAL_SESIONES.md ────────────────────────────────────────────────────

def update_historial(week_num, periodo, mes_anio, kpis, tipo, mensaje, scripts_dir):
    path = _find('HISTORIAL_SESIONES.md', scripts_dir)
    if not path.exists(): return

    with open(path) as f: c = f.read()

    c = c.rstrip()
    # Quitar la última línea de "Última actualización" para reemplazarla
    idx = c.rfind('**Última actualización:**')
    c = c[:idx].rstrip()

    fecha = datetime.now().strftime('%d %b %Y')

    if tipo == 'pipeline':
        kpi_tabla = ''
        if kpis.get('rnd_nd'):
            kpi_tabla = f"""
| Métrica | W{week_num-1} | W{week_num} | WoW |
|---|---|---|---|
| RND %NoDispo | {kpis.get('rnd_nd_prev','—')} | {kpis.get('rnd_nd','—')} | {kpis.get('rnd_nd_wow','—')} |
| RND IPM | {kpis.get('rnd_ipm_prev','—')} | {kpis.get('rnd_ipm','—')} | {kpis.get('rnd_ipm_wow','—')} |
| CR Eficacia | {kpis.get('cr_ef_prev','—')} | {kpis.get('cr_ef','—')} | {kpis.get('cr_ef_wow','—')} |
| CR ConvRate | {kpis.get('cr_cv_prev','—')} | {kpis.get('cr_cv','—')} | {kpis.get('cr_cv_wow','—')} |
"""
        nueva = f"""

---

## Pipeline W{week_num} · {mes_anio} · {fecha}

**Período:** {periodo}  
**Tipo:** Pipeline completo
{kpi_tabla}
### Archivos generados
`RatesNoDispo_Reporte_Editorial.html` · `CheckRates_Reporte_Editorial.html` · 8 Excels · `Mail_W{week_num}.html` · `index.html` · `Price_W{week_num}.zip`

**Última actualización:** W{week_num} (pipeline) · {mes_anio} · {periodo}
"""
    else:
        nueva = f"""

---

## Fix · W{week_num} · {fecha}

**Descripción:** {mensaje}

### Archivos modificados
_(ver commit en GitHub)_

**Última actualización:** W{week_num} (fix) · {mes_anio} · {mensaje[:60]}
"""

    c += nueva
    with open(path, 'w') as f: f.write(c)
    print(f"  ✅ HISTORIAL_SESIONES.md actualizado")


# ── README_QUICK.md ──────────────────────────────────────────────────────────

def update_readme_quick(week_num, periodo, mes_anio, kpis, tipo, scripts_dir):
    path = _find('README_QUICK.md', scripts_dir)
    if not path.exists(): return

    with open(path) as f: c = f.read()

    MARKER = '## 📌 Última semana publicada'
    bloque = f"""## 📌 Última semana publicada

**W{week_num} · {periodo} · {mes_anio}**

"""
    if tipo == 'pipeline' and kpis.get('rnd_nd'):
        bloque += f"""| Métrica | Valor | WoW |
|---|---|---|
| RND %NoDispo | {kpis.get('rnd_nd','—')} | {kpis.get('rnd_nd_wow','—')} |
| RND IPM | {kpis.get('rnd_ipm','—')} | {kpis.get('rnd_ipm_wow','—')} |
| CR Eficacia | {kpis.get('cr_ef','—')} | {kpis.get('cr_ef_wow','—')} |
| CR ConvRate | {kpis.get('cr_cv','—')} | {kpis.get('cr_cv_wow','—')} |

🔗 [Hub](https://analytics-desk.netlify.app) · [RND W{week_num}](https://federicochurches.github.io/Price/rates-nodispo/week-{week_num}/RatesNoDispo_Reporte_Editorial.html) · [CR W{week_num}](https://federicochurches.github.io/Price/checkrates/week-{week_num}/CheckRates_Reporte_Editorial.html)

"""

    if MARKER in c:
        start = c.index(MARKER)
        rest = c[start + len(MARKER):]
        end_rel = rest.find('\n## ')
        if end_rel == -1:
            c = c[:start] + bloque
        else:
            c = c[:start] + bloque + rest[end_rel:]
    else:
        # Insertar al inicio
        c = bloque + '\n---\n\n' + c

    with open(path, 'w') as f: f.write(c)
    print(f"  ✅ README_QUICK.md actualizado")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Actualiza docs PRICE antes del commit')
    parser.add_argument('--week',        type=int, required=True)
    parser.add_argument('--periodo',     type=str, default='')
    parser.add_argument('--mes-anio',    type=str, default='')
    parser.add_argument('--tipo',        type=str, default='pipeline', choices=['pipeline','fix'])
    parser.add_argument('--mensaje',     type=str, default='')
    parser.add_argument('--scripts-dir', type=str, default='/tmp')
    parser.add_argument('--skip-historico', action='store_true',
                        help='No actualizar historico_data.py (para fixes)')
    args = parser.parse_args()

    week_num    = args.week
    periodo     = args.periodo or f'W{week_num}'
    mes_anio    = args.mes_anio or datetime.now().strftime('%B %Y')
    scripts_dir = args.scripts_dir

    print(f"\n{'='*55}")
    print(f"  📝 UPDATE DOCS · W{week_num} · {args.tipo.upper()}")
    print(f"{'='*55}\n")

    # Extraer KPIs del pickle
    kpis = {}
    if args.tipo == 'pipeline':
        kpis = extract_kpis(week_num, scripts_dir)
        if kpis.get('rnd_nd'):
            print(f"  📊 KPIs: RND {kpis['rnd_nd']} | IPM {kpis['rnd_ipm']} | CR Ef {kpis.get('cr_ef','?')} | CV {kpis.get('cr_cv','?')}")
        else:
            print(f"  ⚠️  Pickles no encontrados — KPIs omitidos")

    # Actualizar cada doc
    update_prompt_core(week_num, periodo, mes_anio, kpis, args.tipo, args.mensaje, scripts_dir)
    update_historial(week_num, periodo, mes_anio, kpis, args.tipo, args.mensaje, scripts_dir)
    update_readme_quick(week_num, periodo, mes_anio, kpis, args.tipo, scripts_dir)

    if args.tipo == 'pipeline' and not args.skip_historico:
        update_historico(week_num, kpis, scripts_dir)

    print(f"\n  ✅ Docs actualizados para W{week_num}")


if __name__ == '__main__':
    main()
