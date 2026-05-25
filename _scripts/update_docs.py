#!/usr/bin/env python3
"""
update_docs.py · Paso 7 del pipeline PRICE
Actualiza CHANGELOG.md, README.md y PROMPT_CORE.md con los datos de la semana actual.

Uso standalone:
    python3 update_docs.py --week 21 --periodo "18–24 may 2026" --tipo pipeline
    python3 update_docs.py --week 21 --tipo fix --descripcion "Fix searchbox canastas"

Desde run_pipeline.py:
    Se llama automáticamente con los datos del config YAML.

Modos:
    pipeline   → bloque completo con KPIs reales del pickle + archivos generados
    fix        → bloque de fix/cambio puntual (sin KPIs)

Nota: PROMPT_CORE.md reemplaza a PROMPT_MAESTRO_v3.md desde W21 (optimización tokens).
      HISTORIAL_SESIONES.md contiene el historial de sesiones W16-W20 (solo en Knowledge,
      no se actualiza automáticamente — es arqueología, no contexto operativo).
"""

import argparse
import pickle
import os
import sys
from pathlib import Path
from datetime import datetime

# ── RUTAS ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent

def _find_doc(name):
    """Busca el doc en el directorio del script o en _docs/."""
    for candidate in [SCRIPT_DIR / name, SCRIPT_DIR / '_docs' / name]:
        if candidate.exists():
            return candidate
    return SCRIPT_DIR / name  # fallback: crear en raíz

def _load_pickle(path):
    """Carga pickle, retorna dict o None."""
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None

def _fmt_pct(v):
    return f"{v*100:.2f}%".replace('.', ',')

def _fmt_usd(v):
    return f"${v:,.0f}".replace(',', '.')

def _fmt_int(v):
    return f"{int(v):,}".replace(',', '.')

def extract_kpis(week_num, script_dir):
    """Extrae KPIs reales de los pickles de la semana."""
    rnd_pkl = script_dir / f'rnd_w{week_num}_data.pkl'
    cr_pkl  = script_dir / f'cr_w{week_num}_data.pkl'
    kpis = {}

    D_rnd = _load_pickle(rnd_pkl)
    if D_rnd:
        M = D_rnd.get('M', {})
        gw = M.get(f'global_w{week_num}', M.get('global_current', {}))
        gw_prev = M.get(f'global_w{week_num-1}', M.get('global_prev', {}))
        nd   = gw.get('pct_nodispo', 0)
        nd_p = gw_prev.get('pct_nodispo', 0)
        ipm  = gw.get('ipm', gw.get('rpm', 0))
        ipm_p = gw_prev.get('ipm', gw_prev.get('rpm', 0))
        kpis['rnd_nodispo']  = _fmt_pct(nd)
        kpis['rnd_nodispo_prev'] = _fmt_pct(nd_p)
        kpis['rnd_nodispo_wow']  = f"{(nd - nd_p)*100:+.2f}pp".replace('.', ',')
        kpis['rnd_ipm']      = _fmt_usd(ipm)
        kpis['rnd_ipm_prev'] = _fmt_usd(ipm_p)
        kpis['rnd_ipm_wow']  = f"{(ipm - ipm_p) / max(ipm_p, 1) * 100:+.1f}%".replace('.', ',')
        kpis['rnd_hoteles']  = _fmt_int(len(D_rnd.get('p80_hotel', [])))

    D_cr = _load_pickle(cr_pkl)
    if D_cr:
        M = D_cr.get('M', {})
        gw = M.get(f'global_w{week_num}', M.get('global_current', {}))
        gw_prev = M.get(f'global_w{week_num-1}', M.get('global_prev', {}))
        ef   = gw.get('eficacia', 0)
        ef_p = gw_prev.get('eficacia', 0)
        cv   = gw.get('conv_rate', 0)
        cv_p = gw_prev.get('conv_rate', 0)
        kpis['cr_eficacia']  = _fmt_pct(ef)
        kpis['cr_eficacia_prev'] = _fmt_pct(ef_p)
        kpis['cr_eficacia_wow']  = f"{(ef - ef_p)*100:+.2f}pp".replace('.', ',')
        kpis['cr_convrate']  = _fmt_pct(cv)
        kpis['cr_convrate_prev'] = _fmt_pct(cv_p)
        kpis['cr_convrate_wow']  = f"{(cv - cv_p)*100:+.2f}pp".replace('.', ',')
        kpis['cr_unicos']    = _fmt_int(gw.get('cr_unicos', 0))
        kpis['cr_hoteles']   = _fmt_int(len(D_cr.get('p80_hotel', [])))

    return kpis

# ─────────────────────────────────────────────────────────────────────────────
# CHANGELOG
# ─────────────────────────────────────────────────────────────────────────────
def update_changelog(path, week_num, vol_num, periodo, mes_anio, fecha_pub, kpis, tipo, descripcion, commits):
    path = Path(path)
    content = path.read_text(encoding='utf-8') if path.exists() else ''

    if tipo == 'pipeline':
        kpi_block = ''
        if kpis:
            kpi_block = f"""
### KPIs W{week_num}

| Métrica | W{week_num-1} | W{week_num} | WoW |
|---|---|---|---|
| **%NoDispo** | {kpis.get('rnd_nodispo_prev','—')} | {kpis.get('rnd_nodispo','—')} | {kpis.get('rnd_nodispo_wow','—')} |
| **IPM** | {kpis.get('rnd_ipm_prev','—')} | {kpis.get('rnd_ipm','—')} | {kpis.get('rnd_ipm_wow','—')} |
| **Eficacia** | {kpis.get('cr_eficacia_prev','—')} | {kpis.get('cr_eficacia','—')} | {kpis.get('cr_eficacia_wow','—')} |
| **Conv Rate** | {kpis.get('cr_convrate_prev','—')} | {kpis.get('cr_convrate','—')} | {kpis.get('cr_convrate_wow','—')} |

Hoteles P80 RND: {kpis.get('rnd_hoteles','—')} · CR: {kpis.get('cr_hoteles','—')} · CR únicos: {kpis.get('cr_unicos','—')}
"""
        commits_block = ''
        if commits:
            commits_block = '\n### Commits\n' + '\n'.join(f'- `{c}`' for c in commits) + '\n'

        block = f"""## Pipeline W{week_num} · {mes_anio} · {periodo}

**Fecha publicación:** {fecha_pub}  
**Tipo:** Pipeline completo (6 pasos)
{kpi_block}
### Outputs generados

| Archivo | Descripción |
|---|---|
| `RatesNoDispo_Reporte_Editorial.html` | Reporte editorial RND W{week_num} |
| `CheckRates_Reporte_Editorial.html` | Reporte editorial CR W{week_num} |
| `Analisis_Rates_NoDispo_7d.xlsx` + 3 canastas | Excel RND global + B2C/OP/CUG |
| `Analisis_Checkrates_7d.xlsx` + 3 canastas | Excel CR global + B2C/OP/CUG |
| `Mail_W{week_num}.html` | Mail semanal |
| `index.html` | Hub actualizado |
| `Price_W{week_num}.zip` | ZIP repo listo para commit |
{commits_block}
"""
    else:  # fix / cambio
        commits_block = ''
        if commits:
            commits_block = '\n**Commits:** ' + ' · '.join(f'`{c}`' for c in commits) + '\n'

        block = f"""## Fix/Cambio · W{week_num} · {datetime.now().strftime('%d %b %Y')}

**Descripción:** {descripcion}
{commits_block}
"""

    # Insertar antes del primer bloque existente
    insert_pos = content.find('\n## ')
    if insert_pos == -1:
        content = content.rstrip() + '\n\n' + block
    else:
        content = content[:insert_pos+1] + block + content[insert_pos+1:]

    path.write_text(content, encoding='utf-8')
    print(f"  ✅ CHANGELOG actualizado: {path}")

# ─────────────────────────────────────────────────────────────────────────────
# README
# ─────────────────────────────────────────────────────────────────────────────
def update_readme(path, week_num, vol_num, periodo, mes_anio, kpis, tipo):
    path = Path(path)
    content = path.read_text(encoding='utf-8') if path.exists() else ''

    # Actualizar (o insertar) el bloque "## 📌 Última semana publicada"
    MARKER_START = '## 📌 Última semana publicada'
    MARKER_END   = '\n## '

    new_block = f"""## 📌 Última semana publicada

**Week {week_num} · {periodo} · {mes_anio}**

"""
    if kpis and tipo == 'pipeline':
        new_block += f"""| Métrica | Valor | WoW |
|---|---|---|
| %NoDispo | {kpis.get('rnd_nodispo','—')} | {kpis.get('rnd_nodispo_wow','—')} |
| IPM | {kpis.get('rnd_ipm','—')} | {kpis.get('rnd_ipm_wow','—')} |
| Eficacia CR | {kpis.get('cr_eficacia','—')} | {kpis.get('cr_eficacia_wow','—')} |
| Conv Rate CR | {kpis.get('cr_convrate','—')} | {kpis.get('cr_convrate_wow','—')} |

URLs: [Hub](https://analytics-desk.netlify.app) · [CR](https://federicochurches.github.io/Price/checkrates/week-{week_num}/CheckRates_Reporte_Editorial.html) · [RND](https://federicochurches.github.io/Price/rates-nodispo/week-{week_num}/RatesNoDispo_Reporte_Editorial.html)
"""

    if MARKER_START in content:
        start = content.index(MARKER_START)
        # Find end of this section (next ## or EOF)
        rest = content[start + len(MARKER_START):]
        end_rel = rest.find('\n## ')
        if end_rel == -1:
            content = content[:start] + new_block
        else:
            content = content[:start] + new_block + content[start + len(MARKER_START) + end_rel:]
    else:
        # Prepend before first ## section
        pos = content.find('\n## ')
        if pos == -1:
            content = new_block + content
        else:
            content = content[:pos+1] + new_block + content[pos+1:]

    path.write_text(content, encoding='utf-8')
    print(f"  ✅ README actualizado: {path}")

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT CORE (reemplaza PROMPT_MAESTRO_v3.md desde W21)
# ─────────────────────────────────────────────────────────────────────────────
def update_prompt_core(path, week_num, periodo, mes_anio, kpis, tipo, descripcion, commits):
    path = Path(path)
    content = path.read_text(encoding='utf-8') if path.exists() else ''

    if tipo == 'pipeline':
        commits_block = ''
        if commits:
            commits_block = '\n**Commits:** ' + ' · '.join(f'`{c[:8]}`' for c in commits) + '\n'

        kpi_line = ''
        if kpis:
            kpi_line = (
                f"- RND: NoDispo {kpis.get('rnd_nodispo','—')} ({kpis.get('rnd_nodispo_wow','—')}) "
                f"· IPM {kpis.get('rnd_ipm','—')} ({kpis.get('rnd_ipm_wow','—')})\n"
                f"- CR: Eficacia {kpis.get('cr_eficacia','—')} ({kpis.get('cr_eficacia_wow','—')}) "
                f"· ConvRate {kpis.get('cr_convrate','—')} ({kpis.get('cr_convrate_wow','—')})\n"
            )

        block = f"""
---

## 📝 Pipeline W{week_num} · {mes_anio} (ejecutado {datetime.now().strftime('%d/%m/%Y')})

**Período:** {periodo}  
**Tipo:** Pipeline completo (7 pasos: calc → render → assemble → excel → mail → hub → docs)

{kpi_line}{commits_block}
### Archivos modificados
`rnd_w{week_num}_data.pkl` · `cr_w{week_num}_data.pkl` · `RatesNoDispo_Reporte_Editorial.html` · `CheckRates_Reporte_Editorial.html` · 8 Excels · `Mail_W{week_num}.html` · `index.html`

---

**Última actualización:** {mes_anio} · Pipeline W{week_num} · {periodo}
"""
    else:
        commits_block = ''
        if commits:
            commits_block = f"\n**Commits:** {' · '.join(f'`{c[:8]}`' for c in commits)}\n"

        block = f"""
---

## 📝 Cambios · {datetime.now().strftime('%d %b %Y')} · W{week_num}

**Descripción:** {descripcion}
{commits_block}
### Archivos modificados
_(ver CHANGELOG para detalle)_

---

**Última actualización:** {datetime.now().strftime('%B %Y')} · {descripcion[:60]}
"""

    # Append al final (después de la última línea)
    content = content.rstrip() + '\n' + block

    path.write_text(content, encoding='utf-8')
    print(f"  ✅ PROMPT_CORE actualizado: {path}")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Actualiza documentación del proyecto PRICE')
    parser.add_argument('--week',        type=int,  required=True,  help='Número de semana (ej: 21)')
    parser.add_argument('--vol-num',     type=str,  default=None,   help='Vol num (default = week)')
    parser.add_argument('--periodo',     type=str,  default='',     help='Período (ej: "18–24 may 2026")')
    parser.add_argument('--mes-anio',    type=str,  default='',     help='Mes y año (ej: "Mayo 2026")')
    parser.add_argument('--fecha-pub',   type=str,  default='',     help='Fecha publicación larga')
    parser.add_argument('--tipo',        type=str,  default='pipeline',
                        choices=['pipeline', 'fix'], help='Tipo de actualización')
    parser.add_argument('--descripcion', type=str,  default='',     help='Descripción (para tipo=fix)')
    parser.add_argument('--commits',     type=str,  default='',     help='SHA commits separados por coma')
    parser.add_argument('--docs-dir',    type=str,  default=None,   help='Directorio donde están los docs')
    parser.add_argument('--scripts-dir', type=str,  default=None,   help='Directorio donde están los pickles')
    args = parser.parse_args()

    week_num = args.week
    vol_num  = args.vol_num or str(week_num)
    periodo  = args.periodo or f'W{week_num}'
    mes_anio = args.mes_anio or datetime.now().strftime('%B %Y')
    fecha_pub = args.fecha_pub or datetime.now().strftime('%A %d de %B de %Y').upper()
    commits  = [c.strip() for c in args.commits.split(',') if c.strip()] if args.commits else []

    docs_dir    = Path(args.docs_dir)    if args.docs_dir    else SCRIPT_DIR
    scripts_dir = Path(args.scripts_dir) if args.scripts_dir else SCRIPT_DIR

    print(f"\n{'='*60}")
    print(f"  📝 UPDATE DOCS · W{week_num} · {periodo}")
    print(f"{'='*60}\n")

    # Extraer KPIs del pickle (solo para pipeline)
    kpis = {}
    if args.tipo == 'pipeline':
        kpis = extract_kpis(week_num, scripts_dir)
        if kpis:
            print(f"  📊 KPIs extraídos del pickle W{week_num}")
        else:
            print(f"  ⚠️  No se encontraron pickles W{week_num} — KPIs vacíos")

    # Actualizar los 3 docs
    update_changelog(
        _find_doc('CHANGELOG.md') if not args.docs_dir else docs_dir / 'CHANGELOG.md',
        week_num, vol_num, periodo, mes_anio, fecha_pub, kpis, args.tipo, args.descripcion, commits
    )
    update_readme(
        _find_doc('README.md') if not args.docs_dir else docs_dir / 'README.md',
        week_num, vol_num, periodo, mes_anio, kpis, args.tipo
    )
    update_prompt_core(
        _find_doc('PROMPT_CORE.md') if not args.docs_dir else docs_dir / 'PROMPT_CORE.md',
        week_num, periodo, mes_anio, kpis, args.tipo, args.descripcion, commits
    )

    print(f"\n✅ Documentación actualizada para W{week_num}")
    print(f"   Siguiente paso: python3 github_commit.py --week {week_num} --periodo \"{periodo}\"")

if __name__ == '__main__':
    main()
