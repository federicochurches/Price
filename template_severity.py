"""
template_severity.py · Bloques Severity para canastas CR y RND
Paleta D · BANDA_COLORS de render_helpers es la ÚNICA fuente de verdad de colores.

API:
  make_severity_levels(sev_dict, levels_def)         → lista de tuplas con datos + colores
  render_severity_block(titulo, icon, accent, levels, total)  → HTML de un bloque col
  render_severity_2cols(blk1, blk2)                  → wrapper grid 2 cols

Constantes:
  LEVELS_EFICACIA, LEVELS_CONVRATE, LEVELS_NODISPO, LEVELS_RPM
  Cada item: (nombre_banda, rango_label)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_helpers import BANDA_COLORS, fmt_int_es

# ── Definiciones de niveles por métrica ──────────────────────────────────────
# Solo nombre y rango; los colores siempre vienen de BANDA_COLORS

LEVELS_EFICACIA = [
    ('Súper Crítica', '&lt; 60%'),
    ('Crítica',       '60–85%'),
    ('Revisar',       '85–93%'),
    ('Aceptable',     '93–97%'),
    ('Exitosa',       '≥ 97%'),
]

LEVELS_CONVRATE = [
    ('Sin Conversión', 'BKGS=0'),
    ('Crítica',        '&lt; 0,8%'),
    ('Revisar',        '0,8–1,5%'),
    ('Aceptable',      '1,5–2,5%'),
    ('Exitosa',        '≥ 2,5%'),
]

LEVELS_NODISPO = [
    ('Súper Crítica', '&gt; 60%'),
    ('Crítica',       '20–60%'),
    ('Revisar',       '5–20%'),
    ('Aceptable',     '3–5%'),
    ('Exitosa',       '&lt; 3%'),
]

LEVELS_RPM = [
    ('Sin Conversión', 'BKGS=0'),
    ('Crítica',        '&lt; $200'),
    ('Revisar',        '$200–$499'),
    ('Aceptable',      '$500–$649'),
    ('Exitosa',        '≥ $650'),
]


def make_severity_levels(sev_dict, levels_def):
    """
    Combina sev_dict (conteos por banda) con levels_def (lista de tuplas nombre+rango)
    y añade los colores desde BANDA_COLORS.

    Retorna lista de dicts:
      [{'name': str, 'rng': str, 'n': int, 'pct': float,
        'bg': str, 'fg': str, 'bar': str}, ...]
    """
    total = int(sev_dict.sum()) if hasattr(sev_dict, 'sum') else int(sum(sev_dict.values()))
    rows = []
    for nombre, rng in levels_def:
        n = int(sev_dict.get(nombre, 0))
        pct = n / total * 100 if total else 0
        bc = BANDA_COLORS.get(nombre, BANDA_COLORS['Sin Conversión'])
        rows.append({
            'name': nombre,
            'rng':  rng,
            'n':    n,
            'pct':  pct,
            'bg':   bc['bg'],
            'fg':   bc['fg'],
            'bar':  bc['bar'],
            'total': total,
        })
    return rows


def render_severity_block(titulo, icon, accent_color, levels, total):
    """
    Renderiza un bloque de severity vertical (una columna).

    titulo       : texto del subheader (ej. 'Eficacia', '% NoDispo')
    icon         : símbolo decorativo (ej. '●')
    accent_color : color del subheader
    levels       : lista de dicts de make_severity_levels()
    total        : total de hoteles del bloque
    """
    rows_html = ''
    for row in levels:
        bar_w = max(min(row['pct'], 100), 0.5)
        rows_html += (
            f'<div style="display:grid;grid-template-columns:120px 70px 1fr 55px 42px;'
            f'gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--rule-soft);">'
            f'<span style="display:inline-block;padding:3px 8px;'
            f'background:{row["bg"]};color:{row["fg"]};'
            f'font-size:9px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.06em;text-align:center;">{row["name"]}</span>'
            f'<span style="font-size:10px;color:var(--ink-muted);'
            f'font-variant-numeric:tabular-nums;">{row["rng"]}</span>'
            f'<div style="height:8px;background:var(--paper-soft);position:relative;border-radius:2px;">'
            f'<div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;'
            f'background:{row["bar"]};border-radius:2px;"></div></div>'
            f'<span style="font-weight:600;text-align:right;'
            f'font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(row["n"])}</span>'
            f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);'
            f'font-size:10px;">{row["pct"]:.1f}%</span>'
            f'</div>'
        )

    return (
        f'<div>'
        f'<h3 style="font-size:11px;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:.10em;color:{accent_color};margin:0 0 10px;">'
        f'{icon} {titulo} · {fmt_int_es(total)} hoteles</h3>'
        f'{rows_html}'
        f'</div>'
    )


def render_severity_2cols(blk1, blk2):
    """Wrapper grid 2 columnas para dos bloques de severity."""
    return (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">'
        f'{blk1}'
        f'{blk2}'
        f'</div>'
    )
