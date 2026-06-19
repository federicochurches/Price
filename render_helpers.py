"""
Generador del reporte editorial RatesNoDispo W18
Sistema bandas D · post W17
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import numpy as np
from engine import *

# ============ CONFIG W18 ============
WEEK_NUM = os.getenv('WEEK', 'W20')
PERIODO  = "27 abr – 3 may 2026"
PERIODO_LABEL = "Lunes 27 De Abril De 2026"
MES_AÑO  = "Mayo 2026"
VOL_NUM  = "18"
ACCENT   = "#EA0074"  # magenta RND

# ============ HELPER: limpiar nombre de hotel ============
def _kpi_ver_mas_btn(target_class='rows-more'):
    """Botón Ver más canónico — mismo estilo para todos los paneles KPI."""
    _sq = "'"
    _oc = '{'
    _cc = '}'
    _cls = target_class
    return (
        '<button class="kpi-more-btn"'
        ' style="display:block;width:100%;margin-top:4px;'
        'font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;'
        'background:none;border:1px solid var(--rule);color:var(--ink-muted);'
        'padding:6px 16px;cursor:pointer;border-radius:3px;user-select:none;"'
        ' onclick="(function(el){'
        'var exp=el.getAttribute(' + _sq + 'data-exp' + _sq + ')!==' + _sq + '1' + _sq + ';'
        'el.setAttribute(' + _sq + 'data-exp' + _sq + ',exp?' + _sq + '1' + _sq + ':' + _sq + '0' + _sq + ');'
        'var p=el.closest(' + _sq + '.kpi-tab-rows' + _sq + ');if(!p)p=el.parentNode;'
        'p.querySelectorAll(' + _sq + '.' + _cls + _sq + ').forEach(function(r){'
        'r.style.setProperty(' + _sq + 'display' + _sq + ',exp?' + _sq + 'grid' + _sq + ':' + _sq + 'none' + _sq + ',' + _sq + 'important' + _sq + ');'
        '});'
        'el.textContent=exp?' + _sq + 'Ver menos ▴' + _sq + ':' + _sq + 'Ver más ▾' + _sq + ';'
        '})(this)">'
        'Ver más ▾</button>'
    )


def clean_hotel_name(name):
    """Quita prefijo de ID '(NNNNNN) - ' del nombre del hotel.
    Ejemplo: '(102572) - Hyatt Grand Central' → 'Hyatt Grand Central'
    Si no matchea el patrón, devuelve el nombre original.
    """
    import re
    if not isinstance(name, str): return str(name)
    m = re.match(r'^\(\d+\)\s*-\s*(.+)$', name.strip())
    return m.group(1).strip() if m else name

# ============ HELPERS DE COLOR PARA BANDAS ============
BANDA_COLORS = {
    # Paleta D · única fuente de verdad · sincronizada con BANDAS.md
    # bg=fondo badge · fg=texto badge · bd=borde badge · bar=color barra de progreso severity
    'Exitosa':       {'bg':'#E1F5EE', 'fg':'#1A6B4A', 'bd':'#1D9E75', 'bar':'#1A6B4A'},
    'Aceptable':     {'bg':'#FEF9C3', 'fg':'#713F12', 'bd':'#FCD34D', 'bar':'#FCD34D'},
    'Revisar':       {'bg':'#FED7AA', 'fg':'#C2410C', 'bd':'#F97316', 'bar':'#F97316'},
    'Crítica':       {'bg':'#FCE4F1', 'fg':'#99162B', 'bd':'#C0392B', 'bar':'#C0392B'},
    'Súper Crítica': {'bg':'#E8E6E3',  'fg':'#2D2828', 'bd':'#9B2222', 'bar':'#8A8377'},
    'Sin Conversión':{'bg':'#F2EEE6', 'fg':'#5F5E5A', 'bd':'#8A8377', 'bar':'#8A8377'},
}

def _mini_badge(bnd):
    """Badge de banda inline 8px."""
    if not bnd or not isinstance(bnd, str): return ''
    bc = BANDA_COLORS.get(bnd, {})
    bg = bc.get('bg', '#F2EEE6'); fg = bc.get('fg', '#5F5E5A')
    return f'<span class="sev-badge" style="background:{bg};color:{fg};">{bnd}</span>'

def mini_badge(bnd):
    return _mini_badge(bnd)

def banda_pill(banda, target=None, font_size='11px'):
    """Renderiza pill de severity · estilo compacto · target opcional embebido.
    Si se pasa target, se muestra como '· Target X%' a la derecha del nombre.
    """
    c = BANDA_COLORS.get(banda, BANDA_COLORS['Sin Conversión'])
    bg = c['bg']
    fg = c['fg']
    bd = c['bd']
    banda_upper = banda.upper()
    inner = banda_upper
    if target:
        inner = (f'{banda_upper}'
                 f'<span style="font-weight:500;opacity:.75;margin-left:8px;letter-spacing:.02em;text-transform:none;">'
                 f'· Target {target}</span>')
    return (f'<span style="display:inline-flex;align-items:center;font-size:{font_size};font-weight:700;letter-spacing:.04em;'
            f'text-transform:uppercase;padding:6px 12px;border-radius:3px;background:{bg};color:{fg};'
            f'border:1px solid {bd};white-space:nowrap;">{inner}</span>')


def target_caption(target_text, font_size='11px'):
    """Caption gris fino para mostrar target debajo del badge.
    Después de W20 sesión 8 el target va EMBEBIDO en banda_pill,
    por lo que esta función devuelve string vacío para mantener compatibilidad."""
    return ''


def gauge_5levels(banda_actual, niveles_rnd_or_cr='nodispo'):
    """Gauge bar 5 niveles · height:6px · opacity:1 uniforme · BANDAS.md
    Colores: Súper Crítica rojo oscuro · Crítica rojo · Revisar naranja · Aceptable amarillo · Exitosa verde
    La banda activa se identifica por el badge/pill arriba, no por el gauge.
    """
    if niveles_rnd_or_cr == 'nodispo':
        levels = [
            ('Súper Crítica', '#8A8377'),
            ('Crítica',       '#C0392B'),
            ('Revisar',       '#F97316'),
            ('Aceptable',     '#FCD34D'),
            ('Exitosa',       '#1A6B4A'),
        ]
    elif niveles_rnd_or_cr == 'rpm':
        levels = [
            ('Sin Conversión', '#8A8377'),
            ('Crítica',        '#C0392B'),
            ('Revisar',        '#F97316'),
            ('Aceptable',      '#FCD34D'),
            ('Exitosa',        '#1A6B4A'),
        ]
    elif niveles_rnd_or_cr == 'eficacia':
        levels = [
            ('Súper Crítica', '#8A8377'),
            ('Crítica',       '#C0392B'),
            ('Revisar',       '#F97316'),
            ('Aceptable',     '#FCD34D'),
            ('Exitosa',       '#1A6B4A'),
        ]
    elif niveles_rnd_or_cr == 'convrate':
        levels = [
            ('Sin Conversión', '#8A8377'),
            ('Crítica',        '#C0392B'),
            ('Revisar',        '#F97316'),
            ('Aceptable',      '#FCD34D'),
            ('Exitosa',        '#1A6B4A'),
        ]
    cells = []
    for nombre, color in levels:
        cells.append(f'<div style="flex:1;background:{color};height:6px;opacity:1;"></div>')
    return '<div style="display:flex;gap:2px;margin-top:10px;">' + ''.join(cells) + '</div>'

def wow_box(curr_label, curr_str, wow_str, wow_color, accent_color,
            week_num=None, week_prev=None, compact=False):
    # Dynamic week labels from env if not passed explicitly
    import os as _os
    _wn = int(_os.getenv('VOL_NUM', '20'))
    if week_num is None: week_num = f'W{_wn}'
    if week_prev is None: week_prev = f'W{_wn-1}'
    """Caja W(N-1) / WoW / W(N).

    compact=False → global (margin-top:8px, padding:5px, font:15px, gap:6px, bg:paper-soft)
    compact=True  → canastas (margin-top:14px, padding:8px, font:16px, gap:8px, bg:paper)
    Los valores compact son los de la antigua wow_box_canasta — ahora unificados aquí.
    """
    if wow_color == '#2F6C34':   wow_bg = '#E0F0E2'
    elif wow_color == '#C0392B': wow_bg = '#FCE4F1'
    else:                        wow_bg = '#F2EEE6'
    mt  = '14px' if compact else '8px'
    pad = '8px 4px' if compact else '5px 4px'
    fs  = '16px'    if compact else '15px'
    gap = '8px'     if compact else '6px'
    p   = '8px'     if compact else '6px'
    br  = '4px'     if compact else '3px'
    outer_bg = 'var(--paper-soft)'  # both compact and global use paper-soft for contrast
    cell_br  = '3px' if compact else '2px'
    lbl_fs   = '9px' if compact else '8px'
    return (
        f'<div style="margin-top:{mt};background:{outer_bg};border-radius:{br};padding:{p};display:flex;align-items:stretch;gap:{gap};">'
        f'<div style="flex:1;text-align:center;background:var(--paper);padding:{pad};border-radius:{cell_br};">'
          f'<div style="font-size:{lbl_fs};letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">{week_prev}</div>'
          f'<div style="font-size:{fs};font-weight:700;color:var(--ink-soft);margin-top:2px;">{curr_label}</div>'
        f'</div>'
        f'<div style="flex:1;text-align:center;background:var(--paper);padding:{pad};border-radius:{cell_br};">'
          f'<div style="font-size:{lbl_fs};letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">{week_num}</div>'
          f'<div style="font-size:{fs};font-weight:700;color:{accent_color};margin-top:2px;">{curr_str}</div>'
        f'</div>'
        f'<div style="flex:1;text-align:center;background:{wow_bg};padding:{pad};border-radius:{cell_br};">'
          f'<div style="font-size:{lbl_fs};letter-spacing:.08em;text-transform:uppercase;color:{wow_color};font-weight:700;">WoW</div>'
          f'<div style="font-size:{fs};font-weight:700;color:{wow_color};margin-top:2px;">{wow_str}</div>'
        f'</div>'
      f'</div>'
    )

def truncate(txt, n=42):
    if pd.isna(txt): return '-'
    s = str(txt).strip()
    return s if len(s) <= n else s[:n-1].strip() + '…'

def fmt_big(x):
    """Formato compacto (3,5M, 580K)"""
    if pd.isna(x) or x == 0: return '0'
    x = abs(x)
    if x >= 1_000_000_000: return f'{x/1_000_000_000:.1f}B'.replace('.', ',')
    if x >= 1_000_000:     return f'{x/1_000_000:.1f}M'.replace('.', ',')
    if x >= 1_000:         return f'{x/1_000:.1f}K'.replace('.', ',')
    return f'{int(x):,}'.replace(',', '.')

def fmt_pct_short(x):
    if pd.isna(x): return '-'
    return f'{x*100:.1f}%'.replace('.', ',')

def fmt_pct2(x):
    import math
    if pd.isna(x) or (isinstance(x, float) and math.isinf(x)): return '—'
    return f'{x*100:.2f}%'.replace('.', ',')

def fmt_num2(x):
    """Formatea número sin decimales (para IPM)."""
    try:
        v = float(x)
        return f'{int(round(v)):,}'.replace(',','.')
    except:
        return '—'
def fmt_int_es(x):
    if pd.isna(x): return '-'
    return f'{int(round(x)):,}'.replace(',', '.')

# ── Normalización de nombres de país para display en tabs ─────────────────────
_PAIS_REPLACEMENTS = {
    'Estados Unidos de América': 'United States',
    'Estados Unidos':            'United States',
    'Reino Unido':               'UK',
    'Gran Bretaña (UK)':         'UK',
    'Gran Bretaña':              'UK',
    'República Dominicana':      'R. Dominicana',
    'Emiratos Árabes Unidos':    'Emirates',
}

def clean_pais_name(name, max_len=22):
    """Normaliza nombres de país largos para display en tabs y trunca."""
    if not name:
        return name
    for old, new in _PAIS_REPLACEMENTS.items():
        if old in name:
            name = name.replace(old, new)
            break
    return truncate(name, max_len)

# ── Normalización de nombres de corporativo ───────────────────────────────────
_CORP_REPLACEMENTS = {
    'Hyatt Inclusive Collection': 'HIC',
    'Caesars Entertainment':      'Caesars',
    'MGM Resorts':                'MGM',
}

def clean_corp_name(name, max_len=28):
    """Normaliza nombres de corporativo para display en tabs y trunca.
    Reglas activas:
      · 'Hyatt Inclusive Collection' → 'HIC'
    """
    if not name:
        return name
    for old, new in _CORP_REPLACEMENTS.items():
        if old in str(name):
            name = str(name).replace(old, new)
            break
    return truncate(str(name), max_len)

# ── Normalización de nombres de destino ───────────────────────────────────────
import re as _re
_DESTINO_PATTERN = _re.compile(
    r'^(Las Vegas|Los Angeles|New York|San Francisco|San Diego|San Antonio'
    r'|Salt Lake City|Kansas City|Oklahoma City|Mexico City|Quebec City'
    r'|Cape Town|Hong Kong|Chicago|Miami|Boston|Seattle|Denver|Phoenix'
    r'|Atlanta|Dallas|Houston|Orlando|Nashville|Minneapolis|Portland'
    r'|Washington|Baltimore|Detroit|Cleveland|Pittsburgh|Tampa|Austin)\s*\(.*?\)',
    _re.IGNORECASE
)
# Mapa específico de destinos compuestos → nombre corto
_DESTINO_MAP = {
    'Mexico City - Central Mexico': 'Mexico City',
    'Mexico City (and vicinity)':   'Mexico City',
}
# Sufijos a eliminar de destinos (con excepciones para topónimos que incluyen Area)
_AREA_EXCEPTIONS = {'El Cairo', 'Dubai', 'Istanbul', 'Abu Dhabi', 'Adjara', 'Ras Al Khaimah'}
_AREA_SUFFIX = _re.compile(
    r'\s+Area$|\s+Area\s*,.*$|\s+Metropolitan Area$|\s+Region$|\s+Province$|\s+District$',
    _re.IGNORECASE
)

# Destinos compuestos "Ciudad - Descripción" → solo "Ciudad"
_CITY_DASH_PATTERN = _re.compile(r'^([A-Za-zÀ-ÿ]+)\s*-\s*.{8,}$')

def clean_destino_name(name, max_len=28):
    """Normaliza nombres de destino:
    · 'Las Vegas (and vicinity), NV, US' → 'Las Vegas'
    · 'Toronto Area' → 'Toronto'
    · 'Bourgas - South Black Sea Coast Area' → 'Bourgas'
    · 'Mexico City - Central Mexico' → 'Mexico City'
    · 'Gargano - Foggia Area' → 'Gargano - Foggia'
    """
    if not name:
        return name
    s = str(name).strip()
    # Mapa directo de destinos compuestos conocidos
    for k, v in _DESTINO_MAP.items():
        if k in s:
            return truncate(v, max_len)
    # Patrón ciudad (and vicinity)
    m = _DESTINO_PATTERN.match(s)
    if m:
        s = m.group(1)
    else:
        # Quitar sufijo Area / Region / etc. salvo excepciones
        if not any(exc in s for exc in _AREA_EXCEPTIONS):
            s = _AREA_SUFFIX.sub('', s).strip()
        # Destinos "Ciudad - Descripción larga" → solo "Ciudad"
        m2 = _CITY_DASH_PATTERN.match(s)
        if m2:
            s = m2.group(1)
    return truncate(s, max_len)


def searchbox_html(input_id, scope_selector, placeholder="Buscar hotel, destino, corporativo..."):
    """Genera HTML del searchbox para insertar antes de un bloque de tablas.
    El JS en asset_*_head.html toma data-sb-scope automaticamente.
    
    input_id        : ID unico del input (ej. 'sb-cr-hotel')
    scope_selector  : selector CSS del bloque cuyas filas filtrar (ej. '#hoteles-block')
    placeholder     : texto del placeholder
    """
    return (
        f'<div class="sb-wrap">'
        f'<input class="sb-input" type="text" id="{input_id}" '
        f'placeholder="{placeholder}" '
        f'data-sb-scope="{scope_selector}" '
        f'autocomplete="off" spellcheck="false">'
        f'</div>'
    )


# ── NUEVAS FUNCIONES · Plan A+D · W21 ────────────────────────────────────────

def tab_column_header(cols, widths):
    """Header de columnas para tabs de KPI cards (global y canastas).

    cols   : lista de strings — nombres de columnas después de la col de nombre.
             La primera celda (nombre del elemento) siempre queda vacía.
             Ejemplo: ['Severity', 'Eficacia', 'WoW']
    widths : string de grid-template-columns.
             Ejemplo: 'minmax(0,1fr) 80px 54px 40px'

    Uso:
        tab_column_header(['Severity','Eficacia','WoW'], 'minmax(0,1fr) 80px 54px 40px')
        tab_column_header(['Severity','%NoDispo','WoW'],  'minmax(0,1fr) 72px 54px 40px')
    """
    _lbl_left  = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);text-align:left;padding:2px 0 4px;'
    _lbl_right = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);text-align:right;padding:2px 0 4px;'
    _LEFT_COLS = {'Severity','severity'}
    spans = '<span></span>' + ''.join(
        f'<span style="{_lbl_left if c in _LEFT_COLS else _lbl_right}">{c}</span>' for c in cols
    )
    return (
        f'<div style="display:grid;grid-template-columns:{widths};'
        f'gap:6px;padding:2px 0 4px;border-bottom:1px solid var(--rule);margin-bottom:2px;">'
        f'{spans}</div>'
    )


def make_wow_pill_row(wow_v, is_mejora_si_positivo=True, threshold=0.005):
    """Pill WoW compacta para filas de tabs de KPI cards.

    Unifica el sistema CR (inline-style) con el sistema RND (CSS class).
    Retorna un <em class="wow-pill ..."> — las clases .wow-pill.nd/up/dn
    deben estar definidas en los assets CSS (asset_cr_head y asset_rnd_head).

    wow_v                : float o None — delta en las unidades de la métrica
    is_mejora_si_positivo: True  → Eficacia/ConvRate/IPM (subir es bueno)
                           False → NoDispo (bajar es bueno)
    threshold            : delta mínimo para mostrar cambio (default 0.005)
    """
    import math
    if wow_v is None or (isinstance(wow_v, float) and (math.isnan(wow_v) or math.isinf(wow_v))):
        return '<em class="wow-pill nd">—</em>'
    v = float(wow_v)
    if abs(v) < threshold:
        return '<em class="wow-pill nd">—</em>'
    mejora = (v > 0) == is_mejora_si_positivo
    cls    = 'dn' if mejora else 'up'
    arrow  = '↑' if v > 0 else '↓'
    txt    = f'{arrow}{abs(v):.1f}'.replace('.', ',')
    return f'<em class="wow-pill {cls}">{txt}</em>'



def wow_pill_html(wow_val, unit='pp', prefix_pos='↑', prefix_neg='↓'):
    """Pill WoW redondeada con fondo semántico (V1).

    wow_val : float con el delta (positivo = mejora para Eficacia/ConvRate/IPM,
              negativo = mejora para NoDispo). El caller decide el signo correcto
              antes de llamar: pasar wow_val ya "orientado" (+ = verde, - = rojo).
    unit    : sufijo de unidad ('pp', '%', '$', '')
    
    Para métricas donde SUBIR es malo (NoDispo), invertir el signo antes de llamar:
        wow_pill_html(-wow_nd_val)   # NoDispo sube → rojo

    Retorna HTML de un <span> pill inline.
    Casos especiales:
      · abs(val) < 0.005 → neutro (gris)
      · val > 0          → verde (mejora)
      · val < 0          → rojo  (empeora)
    """
    import math
    if wow_val is None or (isinstance(wow_val, float) and math.isnan(wow_val)):
        return (f'<span style="display:inline-flex;align-items:center;gap:2px;'
                f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;'
                f'background:#F2EEE6;color:#8A8377;">—</span>')
    v = float(wow_val)
    if abs(v) < 0.005:
        return (f'<span style="display:inline-flex;align-items:center;gap:2px;'
                f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;'
                f'background:#F2EEE6;color:#8A8377;">— 0,0{unit}</span>')
    if v > 0:
        bg, fg, arrow = '#EAF3DE', '#2F6C34', prefix_pos
    else:
        bg, fg, arrow = '#FCE8E6', '#C0392B', prefix_neg
    val_str = f'{abs(v):.1f}'.replace('.', ',')
    return (f'<span style="display:inline-flex;align-items:center;gap:2px;'
            f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;'
            f'background:{bg};color:{fg};">{arrow} {val_str}{unit}</span>')


def searchbox_pill_html(input_id, accent_color='#5C469C', placeholder='Buscar…',
                        count_id=None):
    """Pill searchbox para insertar dentro de .tabs-row en cards KPI (Prop A).

    Produce el bloque .sb-pill-wrap completo con:
      · pill redondeada con ícono de búsqueda
      · input sin borde visible (fusionado en la pill)
      · botón X para limpiar (visible solo cuando hay texto)
      · badge contador opcional (count_id = ID del <span> que muestra "N / total")
    """
    count_html = ''
    if count_id:
        count_html = (f'<span id="{count_id}" class="sb-pill-count" '
                      f'style="font-size:9px;font-weight:700;color:var(--ink-muted);'
                      f'background:var(--rule-soft);padding:2px 7px;border-radius:10px;'
                      f'white-space:nowrap;transition:all .15s;"></span>')
    clear_id = input_id + '-clear'
    return (
        f'<div class="sb-pill-wrap" style="display:flex;align-items:center;'
        f'gap:7px;padding:0 4px 0 0;">'
        f'<div class="sb-pill" style="display:flex;align-items:center;gap:5px;'
        f'background:var(--paper-soft);border:1px solid var(--rule);border-radius:20px;'
        f'padding:3px 8px 3px 8px;transition:border-color .15s,box-shadow .15s;">'
        f'<svg width="12" height="12" viewBox="0 0 24 24" fill="none" '
        f'stroke="var(--ink-muted)" stroke-width="2.5" stroke-linecap="round" '
        f'stroke-linejoin="round" style="flex-shrink:0;" aria-hidden="true">'
        f'<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
        f'<input type="text" id="{input_id}" placeholder="{placeholder}" '
        f'data-sb-pill="true" data-sb-pill-accent="{accent_color}" '
        f'data-sb-count-id="{count_id or ""}" data-sb-clear-id="{clear_id}" '
        f'autocomplete="off" spellcheck="false" '
        f'style="background:none;border:none;outline:none;font-size:10px;'
        f'font-family:inherit;color:var(--ink);width:100px;caret-color:{accent_color};" '
        f'onfocus="var p=this.closest(\'.sb-pill\');p.style.borderColor=\'{accent_color}\';'
        f'p.style.boxShadow=\'0 0 0 2px {accent_color}1A\';" '
        f'onblur="if(!this.value){{var p=this.closest(\'.sb-pill\');'
        f'p.style.borderColor=\'\';p.style.boxShadow=\'\';}}">'
        f'<button id="{clear_id}" type="button" '
        f'style="display:none;background:none;border:none;cursor:pointer;padding:0 2px;'
        f'line-height:1;color:var(--ink-muted);font-size:13px;flex-shrink:0;" '
        f'title="Limpiar búsqueda" aria-label="Limpiar búsqueda">×</button>'
        f'</div>'
        f'{count_html}'
        f'</div>'
    )


def searchbox_header_html(input_id, accent_color='#5C469C', placeholder='Buscar…',
                           th_id=None):
    """Searchbox integrado en el primer <th> de una tabla (Prop D).
    Mismo estilo pill que las cards KPI (border-radius:20px, botón X).
    """
    clear_id = input_id + '-clear'
    return (
        f'<div style="display:flex;align-items:center;">'
        f'<div class="sb-pill" style="display:inline-flex;align-items:center;gap:4px;'
        f'background:var(--paper-soft);border:1px solid var(--rule);border-radius:20px;'
        f'padding:3px 8px 3px 8px;transition:border-color .15s,box-shadow .15s;min-width:0;">'
        f'<svg width="12" height="12" viewBox="0 0 24 24" fill="none" '
        f'stroke="var(--ink-muted)" stroke-width="2.5" stroke-linecap="round" '
        f'stroke-linejoin="round" style="flex-shrink:0;" aria-hidden="true">'
        f'<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
        f'<input type="text" id="{input_id}" placeholder="" '
        f'data-sb-table="true" '
        f'autocomplete="off" spellcheck="false" '
        f'style="background:none;border:none;outline:none;font-size:10px;'
        f'font-family:inherit;color:var(--ink);width:100px;'
        f'caret-color:{accent_color};" '
        f'onfocus="var p=this.closest(\'.sb-pill\');p.style.borderColor=\'{accent_color}\';'
        f'p.style.boxShadow=\'0 0 0 2px {accent_color}1A\';" '
        f'onblur="if(!this.value){{var p=this.closest(\'.sb-pill\');'
        f'p.style.borderColor=\'\';p.style.boxShadow=\'\';}}">'
        f'<button id="{clear_id}" type="button" '
        f'style="display:none;background:none;border:none;cursor:pointer;padding:0 2px;'
        f'line-height:1;color:var(--ink-muted);font-size:12px;flex-shrink:0;" '
        f'title="Limpiar búsqueda" aria-label="Limpiar búsqueda" '
        f'onclick="var i=document.getElementById(\'{input_id}\');i.value=\'\';'
        f'i.dispatchEvent(new Event(\'input\'));this.style.display=\'none\';">×</button>'
        f'</div>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REFACTOR P9 · Helpers centralizados CR+RND · W22
# Objetivo: un cambio en top_n o en la estructura de fila → 1 sola línea aquí
# ═══════════════════════════════════════════════════════════════════════════════

# ── Constante única de top N visible ────────────────────────────────────────────
KPI_TOP_N = 5    # ← filas visibles por defecto; 5 más expandibles hasta 10


def render_traf_wow_pill_pct(pct_delta, font_size='8px'):
    """Pill WoW de tráfico expresado como % de cambio.

    pct_delta : float — variación porcentual (ej. +12.3 o -5.8)
    Usado para tráfico CR (CR_Unicos_WoW_pp ya viene escalado ×100 en pp,
    pero como % de cambio sobre el volumen anterior).
    """
    import math
    if pct_delta is None or (isinstance(pct_delta, float) and (math.isnan(pct_delta) or math.isinf(pct_delta))):
        return f'<span style="color:var(--ink-muted);font-size:10px;">—</span>'
    delta = float(pct_delta)
    if abs(delta) < 0.01:
        return f'<span style="color:var(--ink-muted);font-size:10px;">—</span>'
    arrow = '▲' if delta > 0 else '▼'
    bg    = '#EAF3DE' if delta > 0 else '#FCE8E6'
    fg    = '#2F6C34' if delta > 0 else '#C0392B'
    txt   = f'{arrow}{abs(delta):.1f}%'.replace('.', ',')
    return (f'<em style="font-style:normal;font-size:{font_size};font-weight:700;'
            f'padding:1px 4px;border-radius:3px;background:{bg};color:{fg};white-space:nowrap;">{txt}</em>')


def render_traf_wow_pill_abs(abs_delta, font_size='8px'):
    """Pill WoW de tráfico expresado como delta absoluto (para CR_Unicos_WoW_pp / 100)."""
    import math
    if abs_delta is None or (isinstance(abs_delta, float) and (math.isnan(abs_delta) or math.isinf(abs_delta))):
        return f'<span style="color:var(--ink-muted);font-size:10px;">—</span>'
    delta = float(abs_delta)
    if abs(delta) < 0.5:
        return f'<span style="color:var(--ink-muted);font-size:10px;">—</span>'
    arrow = '▲' if delta > 0 else '▼'
    bg    = '#EAF3DE' if delta > 0 else '#FCE8E6'
    fg    = '#2F6C34' if delta > 0 else '#C0392B'
    txt   = f'{arrow}{fmt_int_es(int(abs(delta)))}'
    return (f'<em style="font-style:normal;font-size:{font_size};font-weight:700;'
            f'padding:1px 4px;border-radius:3px;background:{bg};color:{fg};white-space:nowrap;">{txt}</em>')


def render_traf_line_cr(cr_current, cr_prev=None):
    """Línea 'Tráfico: 746.111 ↑pill' para cards CR.

    cr_current : int/float — CR Únicos semana actual
    cr_prev    : int/float o None — CR Únicos semana anterior (para WoW %)
    """
    pill = ''
    if cr_prev and float(cr_prev) > 0:
        pct = (float(cr_current) - float(cr_prev)) / float(cr_prev) * 100
        pill = render_traf_wow_pill_pct(pct)
    return (f'<div style="margin-top:4px;display:flex;align-items:center;gap:6px;'
            f'font-size:10px;color:var(--ink-muted);">'
            f'<span style="color:var(--ink-soft);">'
            f'<strong style="font-weight:700;color:var(--ink);">Tráfico:</strong> '
            f'{fmt_int_es(int(cr_current))}</span>'
            f'{pill}</div>')


def render_traf_line_rnd(trafico_current, trafico_prev=None):
    """Línea 'Tráfico: 12,2B ↑pill' para cards RND."""
    pill = ''
    if trafico_prev and float(trafico_prev) > 0:
        pct = (float(trafico_current) - float(trafico_prev)) / float(trafico_prev) * 100
        pill = render_traf_wow_pill_pct(pct)
    return (f'<div style="margin-top:4px;display:flex;align-items:center;gap:6px;'
            f'font-size:10px;color:var(--ink-muted);">'
            f'<strong style="font-weight:700;color:var(--ink);">Tráfico:</strong> '
            f'{fmt_big(trafico_current)}'
            f'{pill}</div>')


def _resolve_label(r, t_key, index_cols=None):
    """Extrae (raw_lab, lab, corp_sub) de un row según t_key.

    t_key: 'hotel' | 'corp' | 'destino' | 'pais' | 'canasta' | str
    Centraliza la lógica de etiquetado que estaba duplicada 4× en los p1.
    """
    _corp_sub = ''
    cols = index_cols or (r.index if hasattr(r, 'index') else [])
    if t_key == 'hotel':
        raw_lab = str(r['Hotel'])
        lab     = truncate(clean_hotel_name(raw_lab), 38)
        _corp_sub = truncate(str(r.get('CorpName', '')), 20) if 'CorpName' in cols else ''
    elif t_key == 'corp':
        raw_lab = str(r['CorpName'])
        lab     = truncate(clean_corp_name(raw_lab), 36)
    elif t_key == 'destino':
        raw_lab = str(r['Destino'])
        lab     = clean_destino_name(raw_lab, 36)
    elif t_key == 'pais':
        raw_lab = str(r['PaisDestino'])
        lab     = clean_pais_name(raw_lab, max_len=30)
    elif t_key == 'canasta':
        raw_lab = str(r['Canasta'])
        lab     = raw_lab
    else:
        # fallback genérico
        raw_lab = str(r.get(t_key, t_key))
        lab     = truncate(raw_lab, 32)
    return raw_lab, lab, _corp_sub


def build_kpi_tab_rows(df_t, t_key, cfg):
    """Genera el HTML de filas para un panel de tab de KPI card.

    Parámetros
    ----------
    df_t    : DataFrame ya filtrado y ordenado para este tab
    t_key   : str — 'hotel', 'corp', 'destino', 'pais', 'canasta'
    cfg     : dict con claves:
        val_col       str  — nombre de la columna de la métrica principal
        val_fmt       fn   — función de formato del valor (ej. fmt_pct2)
        hist_scale    fn   — transforma val → float para data-hist-w21
                             ej. lambda v: round(v*100, 4)   (para %)
                             ej. lambda v: round(v, 2)        (para IPM $)
        hist_prev_col str  — columna del valor anterior (para data-hist-w20)
        banda_fn      fn   — función de banda (ej. banda_eficacia)
        banda_col     str  — columna pre-calculada de banda (o '' para calcular)
        traf_col      str  — columna de tráfico (ej. 'CR_Unicos', 'Trafico')
        traf_fmt      fn   — función de formato del tráfico
        traf_wow_col  str  — columna de WoW del tráfico
        traf_wow_type str  — 'abs' | 'pct'  (cómo interpretar traf_wow_col)
        wow_col       str  — columna de WoW de la métrica (ej. 'Eficacia_WoW_pp')
        wow_is_pos    bool — True si subir = mejorar (Eficacia, ConvRate, IPM)
                             False si bajar = mejorar (NoDispo)
        grid_cols     str  — grid-template-columns (ej. 'minmax(0,1fr) 80px 56px 52px 54px 48px')
        top_n         int  — filas visibles (default: KPI_TOP_N)
        val_prefix    str  — prefijo del valor formateado (ej. '$' para IPM)

    Devuelve (top_html, rest_html) — filas visibles y ocultas separadas,
    para que el caller decida si agrega header y cómo.
    """
    import math as _math
    top_n      = cfg.get('top_n', KPI_TOP_N)
    val_col    = cfg['val_col']
    val_fmt    = cfg['val_fmt']
    hist_scale = cfg.get('hist_scale', lambda v: round(float(v) * 100, 4))
    hist_prev  = cfg.get('hist_prev_col', '')
    banda_fn   = cfg.get('banda_fn', None)
    banda_col  = cfg.get('banda_col', '')
    traf_col   = cfg.get('traf_col', '')
    traf_fmt   = cfg.get('traf_fmt', fmt_int_es)
    traf_wow_c = cfg.get('traf_wow_col', '')
    traf_wow_t = cfg.get('traf_wow_type', 'pct')   # 'abs' | 'pct'
    wow_col    = cfg.get('wow_col', '')
    wow_is_pos = cfg.get('wow_is_pos', True)
    grid_cols    = cfg['grid_cols']
    val_prefix   = cfg.get('val_prefix', '')
    show_severity = cfg.get('show_severity', True)

    top_html = rest_html = ''

    for i, r in df_t.iterrows():
        raw_lab, lab, corp_sub = _resolve_label(r, t_key)

        # Valor principal
        val = r.get(val_col)
        try:
            _val_f = float(val)
            if _math.isnan(_val_f) or _math.isinf(_val_f):
                val = None
        except (TypeError, ValueError):
            val = None
        val_str = (val_prefix + val_fmt(val)) if val is not None else '—'

        # Banda + badge
        _bnd = ''
        if banda_col and banda_col in r.index:
            _bnd = r[banda_col]
        if not _bnd and val is not None and banda_fn:
            _bnd = banda_fn(val)
        bc   = BANDA_COLORS.get(_bnd, BANDA_COLORS['Sin Conversión'])
        badge = (f'<span class="sev-badge" style="background:{bc["bg"]};color:{bc["fg"]};">'
                 f'{_bnd}</span>')

        # Datos históricos
        _hist_w21 = hist_scale(val) if val is not None else 0
        _hist_w20 = _hist_w21
        if hist_prev:
            _prev_raw = r.get(hist_prev)
            try:
                _pf = float(_prev_raw)
                if not _math.isnan(_pf) and not _math.isinf(_pf):
                    _hist_w20 = hist_scale(_pf)
            except (TypeError, ValueError):
                pass

        # Tráfico
        traf_str = '—'
        if traf_col:
            _tv = r.get(traf_col)
            try:
                _tvf = float(_tv)
                if not _math.isnan(_tvf):
                    traf_str = traf_fmt(int(_tvf))
            except (TypeError, ValueError):
                pass

        # WoW tráfico
        traf_wow_pill = '<span style="color:var(--ink-muted);font-size:10px;">—</span>'
        if traf_wow_c:
            _tw = r.get(traf_wow_c)
            try:
                _twf = float(_tw)
                if not _math.isnan(_twf) and not _math.isinf(_twf):
                    if traf_wow_t == 'abs':
                        traf_wow_pill = render_traf_wow_pill_abs(_twf / 100)
                    else:
                        traf_wow_pill = render_traf_wow_pill_pct(_twf)
            except (TypeError, ValueError):
                pass

        # WoW métrica
        wow_pill = ''
        if wow_col and t_key not in ('canasta',):
            _wv = r.get(wow_col)
            try:
                _wvf = float(_wv)
                if not _math.isnan(_wvf) and not _math.isinf(_wvf):
                    wow_pill = make_wow_pill_row(_wvf, is_mejora_si_positivo=wow_is_pos)
                else:
                    wow_pill = '<em class="wow-pill nd">—</em>'
            except (TypeError, ValueError):
                wow_pill = '<em class="wow-pill nd">—</em>'

        # Visibilidad
        _EXPAND_N = 10  # filas visibles al expandir
        if i < top_n:
            _cls = ''
            _display = 'grid'
        elif i < _EXPAND_N:
            _cls = 'rows-more'
            _display = 'none'
        else:
            _cls = 'sb-hidden'
            _display = 'grid'  # display controlado por sb-hidden CSS

        _row = (
            f'<div class="{_cls}" data-row-idx="{i}"'
            f' data-hist-w21="{_hist_w21}" data-hist-w20="{_hist_w20}" data-hist-label="{raw_lab}"'
            f' style="display:{_display};grid-template-columns:{grid_cols};align-items:center;gap:6px;'
            f'width:100%;padding:6px 0;border-bottom:1px solid var(--rule-soft);'
            f'cursor:pointer;transition:background .12s;">'
            f'<div style="min-width:0;overflow:hidden;">'
            f'<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis;display:block;">{i+1}. {lab}</span>'
            + (f'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;'
               f'overflow:hidden;text-overflow:ellipsis;display:block;">{corp_sub}</span>'
               if corp_sub else '')
            + f'</div>'
            + (f'<div style="display:flex;align-items:center;justify-content:flex-start;'
               f'min-width:0;overflow:hidden;">{badge}</div>'
               if show_severity else '')
            + f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);'
            f'font-variant-numeric:tabular-nums;white-space:nowrap;">{traf_str}</span>'
            f'<div style="text-align:right;white-space:nowrap;">{traf_wow_pill}</div>'
            f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);'
            f'font-variant-numeric:tabular-nums;white-space:nowrap;">{val_str}</span>'
            f'<div style="text-align:right;white-space:nowrap;">{wow_pill}</div>'
            f'</div>'
        )

        if i < top_n:
            top_html += _row
        else:
            rest_html += _row

    return top_html, rest_html


def build_kpi_tab_panel(df_t, t_key, cfg, panel_tabs_spec=None):
    """Construye el <div class="tab-panel"> completo para un tab de KPI card.

    Si t_key no es 'channel' ni 'canasta', agrega el tab_column_header.
    Devuelve el string HTML del panel.

    panel_tabs_spec : dict con claves opcionales:
        'headers' : list[str] — encabezados de columna
        'widths'  : str       — grid-template-columns para el header
    Por defecto se infieren de cfg['grid_cols'] + cfg['col_labels'].
    """
    if t_key == 'channel':
        # El canal se maneja externamente (split PP/TP) — devolver vacío
        # El caller es responsable de construir el panel de canal
        return ''

    top_html, rest_html = build_kpi_tab_rows(df_t, t_key, cfg)

    if t_key != 'canasta' and panel_tabs_spec:
        headers = panel_tabs_spec.get('headers', [])
        widths  = panel_tabs_spec.get('widths', cfg['grid_cols'])
        _hdr = tab_column_header(headers, widths) if headers else ''
        _more_btn = _kpi_ver_mas_btn(target_class='rows-more') if rest_html else ''
        panel_html = f'<div class="kpi-tab-rows">{_hdr}{top_html}{rest_html}{_more_btn}</div>'
    else:
        panel_html = top_html + rest_html

    hidden_style = ' style="display:none;"' if t_key not in ('destino',) else ''
    return f'<div class="tab-panel" data-tab="{t_key}"{hidden_style}>{panel_html}</div>'


# ═══════════════════════════════════════════════════════════════════════════════
# REFACTOR P10 · Helpers compartidos CR+RND · p2 · W22
# ═══════════════════════════════════════════════════════════════════════════════

def es_pct(v):
    """Convierte fracción → '93,15%'. Usado en tablas AR."""
    return f'{v*100:.2f}%'.replace('.', ',')

def es_int(v):
    """Entero con punto de miles español: 746.111"""
    return f'{int(v):,}'.replace(',', '.')

def es_pct2(v):
    """Ya viene en %, no multiplica: '1,57%'. Para CV y values ya escalados."""
    return f'{v:.2f}%'.replace('.', ',') if isinstance(v, float) else str(v)

def es_ipm(v):
    """IPM formateado: '$834'"""
    return f'${int(v):,}'.replace(',', '.')

def banda_colors(banda):
    """Devuelve (bg, fg) desde BANDA_COLORS. Centraliza el lookup."""
    bc = BANDA_COLORS.get(banda, BANDA_COLORS['Sin Conversión'])
    return bc['bg'], bc['fg']

def wow_arrow(pp):
    """▲1,2 / ▼0,5 / — para WoW en pp. Compartido CR+RND."""
    import math as _m
    if pp is None or (isinstance(pp, float) and (_m.isnan(pp) or _m.isinf(pp))):
        return '—'
    if pp > 0: return f'▲{abs(pp):.1f}'.replace('.', ',')
    if pp < 0: return f'▼{abs(pp):.1f}'.replace('.', ',')
    return '—'

def wow_arrow_abs(delta):
    """▲746.111 / ▼12.345 para WoW de tráfico (delta absoluto, no pp)."""
    import math as _m
    if delta is None or (isinstance(delta, float) and (_m.isnan(delta) or _m.isinf(delta))):
        return '—'
    formatted = f'{int(abs(delta)):,}'.replace(',', '.')
    if delta > 0: return f'▲{formatted}'
    if delta < 0: return f'▼{formatted}'
    return '—'

def sev_badge_html_p2(banda):
    """Badge de banda para tablas AR (p2). Usa <b> con sev-badge class."""
    bbg, bfg = banda_colors(banda)
    return (f'<b class="sev-badge" style="background:{bbg};color:{bfg};'
            f'font-size:8px;padding:2px 6px;text-transform:uppercase;'
            f'outline:1px solid rgba(0,0,0,.12);">{banda}</b>')


# ═══════════════════════════════════════════════════════════════════════════════
# REFACTOR P10 (cont.) · canasta_tab_rows + build_card_rows · W22
# ═══════════════════════════════════════════════════════════════════════════════

def canasta_tab_rows(df, dim_col, cfg):
    """Genera filas HTML para tabs de canastas (p3 CR y RND).

    Reemplaza tab_rows_canasta() duplicada en render_cr_p3.py y render_rnd_p3.py.

    cfg keys:
        val_col       str  — columna de la métrica ('Eficacia', '%NoDispo', 'IPM', etc.)
        val_fmt       fn   — función de formato del valor (fmt_pct2, fmt_num2, etc.)
        val_prefix    str  — prefijo del valor ('', '$')
        hist_scale    fn   — transforma val → float para data-hist-w21
        hist_prev_col str  — columna del valor anterior
        banda_fn      fn   — función de banda
        banda_col     str  — columna pre-calculada de banda
        wow_fn        fn   — fn(r) → html de la pill WoW (None = make_wow_pill_row automático)
        wow_col       str  — columna de WoW (si wow_fn es None)
        wow_is_pos    bool — True si subir = mejorar
        traf_col      str  — columna de tráfico extra ('' = sin tráfico)
        traf_fmt      fn   — función de formato del tráfico
        grid_cols     str  — grid-template-columns
        metric_lbl    str  — label de la columna métrica en el header
        col_headers   list — lista de labels de columnas (después de nombre)
                             ['Severity', 'Tráfico', 'Métrica', 'WoW']
        tab_key       str  — usado para is_simple check
        parse_hotel   bool — si True, genera sub-label con CorpName
    """
    import math as _m
    top5 = next5 = rest = ''

    val_col     = cfg['val_col']
    val_fmt     = cfg.get('val_fmt', fmt_pct2)
    val_prefix  = cfg.get('val_prefix', '')
    hist_scale  = cfg.get('hist_scale', lambda v: round(float(v) * 100, 4))
    hist_prev   = cfg.get('hist_prev_col', '')
    banda_fn    = cfg.get('banda_fn', None)
    banda_col   = cfg.get('banda_col', '')
    wow_fn      = cfg.get('wow_fn', None)
    wow_col     = cfg.get('wow_col', '')
    wow_is_pos  = cfg.get('wow_is_pos', True)
    traf_col    = cfg.get('traf_col', '')
    traf_fmt    = cfg.get('traf_fmt', fmt_big)
    grid_cols   = cfg['grid_cols']
    tab_key     = cfg.get('tab_key', '')
    parse_hotel = cfg.get('parse_hotel', False)

    for i, r in df.iterrows():
        # ── Label ────────────────────────────────────────────────────────────
        raw_lab = str(r[dim_col])
        if parse_hotel:
            lab = truncate(raw_lab, 28)
        elif dim_col == 'PaisDestino':
            lab = clean_pais_name(raw_lab, max_len=24)
        elif dim_col == 'Destino':
            lab = clean_destino_name(raw_lab, 28)
        elif dim_col == 'CorpName':
            lab = truncate(clean_corp_name(raw_lab), 28)
        elif dim_col == 'Hotel':
            lab = truncate(clean_hotel_name(raw_lab), 28)
        else:
            lab = truncate(raw_lab, 28)

        corp_sub = ''
        if parse_hotel and 'CorpName' in r.index:
            corp_sub = truncate(clean_corp_name(str(r.get('CorpName', ''))), 24)

        # ── Valor ────────────────────────────────────────────────────────────
        val = r.get(val_col, 0)
        try:
            _vf = float(val)
            if _m.isnan(_vf) or _m.isinf(_vf):
                val = None
        except (TypeError, ValueError):
            val = None

        _val_is_nan = val is None
        val_str = (val_prefix + val_fmt(val)) if val is not None else '—'

        # ── Banda + badge ─────────────────────────────────────────────────────
        _bnd = ''
        if not parse_hotel:
            if banda_col and banda_col in r.index:
                _bnd = r[banda_col]
            if not _bnd and val is not None and banda_fn:
                _bnd = banda_fn(val)
        _badge = _mini_badge(_bnd)

        # ── Histórico ─────────────────────────────────────────────────────────
        _w21 = hist_scale(val) if val is not None else 0
        _w20 = _w21
        if hist_prev:
            _prev = r.get(hist_prev)
            try:
                _pf = float(_prev)
                if not _m.isnan(_pf) and not _m.isinf(_pf):
                    _w20 = hist_scale(_pf)
            except (TypeError, ValueError):
                pass

        # ── WoW pill ──────────────────────────────────────────────────────────
        if wow_fn:
            wow_html = wow_fn(r)
        elif wow_col:
            wow_html = make_wow_pill_row(
                r.get(wow_col) if wow_col in r.index else None,
                is_mejora_si_positivo=wow_is_pos
            )
        else:
            wow_html = '<em class="wow-pill nd">—</em>'

        # ── Tráfico extra (RND) ───────────────────────────────────────────────
        traf_str = ''
        if traf_col:
            _tv = r.get(traf_col)
            try:
                _tvf = float(_tv)
                if not _m.isnan(_tvf):
                    traf_str = traf_fmt(_tvf)
            except (TypeError, ValueError):
                pass

        # ── Visibilidad ───────────────────────────────────────────────────────
        if i < 5:   _cls = ''
        elif i < 10: _cls = 'rows-more'
        else:        _cls = 'sb-hidden'

        _no_data = 'opacity:.45;pointer-events:none;' if _val_is_nan else ''

        # ── Nombre cell ───────────────────────────────────────────────────────
        if parse_hotel:
            _name_cell = (
                f'<div style="min-width:0;overflow:hidden;">'
                f'<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;'
                f'overflow:hidden;text-overflow:ellipsis;display:block;">{i+1}. {lab}</span>'
                + (f'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;'
                   f'overflow:hidden;text-overflow:ellipsis;display:block;">{corp_sub}</span>'
                   if corp_sub else '')
                + f'</div>'
            )
        else:
            _name_cell = (
                f'<span style="font-size:11px;font-weight:600;color:var(--ink);'
                f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;">'
                f'{i+1}. {lab}</span>'
            )

        # ── Tráfico td (solo si hay traf_col) ────────────────────────────────
        _traf_td = (
            f'<span style="text-align:right;font-size:11px;color:var(--ink-muted);'
            f'font-variant-numeric:tabular-nums;">{traf_str}</span>'
        ) if traf_col else ''

        _row = (
            f'<div class="{_cls}" data-row-idx="{i}" '
            f'data-hist-w21="{_w21}" data-hist-w20="{_w20}" data-hist-label="{raw_lab}"'
            f' style="display:grid;grid-template-columns:{grid_cols};align-items:center;gap:4px;'
            f'padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;'
            f'transition:background .12s;{_no_data}">'
            f'{_name_cell}'
            f'<div style="display:flex;align-items:center;">'
            f'{_badge if not _val_is_nan else ""}</div>'
            f'{_traf_td}'
            f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);'
            f'font-variant-numeric:tabular-nums;">{val_str}</span>'
            f'{wow_html}</div>'
        )

        if i < 5:    top5  += _row
        elif i < 10: next5 += _row
        else:        rest  += _row

    # ── Ver más btn ───────────────────────────────────────────────────────────
    is_simple = tab_key in ('canasta', 'channel', 'provider')
    ver_mas_btn = ''
    if len(df) > 5 and not is_simple:
        ver_mas_btn = _kpi_ver_mas_btn(target_class='rows-more')

    # ── Header de columnas ────────────────────────────────────────────────────
    _hdr = ''
    if not is_simple:
        col_headers = cfg.get('col_headers', ['Severity', cfg.get('metric_lbl','Métrica'), 'WoW'])
        _spans = '<span></span>' + ''.join(
            f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;'
            f'color:var(--ink-muted);text-align:{"left" if h=="Severity" else "right"};padding:2px 0;">'
            f'{h}</span>'
            for h in col_headers
        )
        _hdr = (
            f'<div style="display:grid;grid-template-columns:{grid_cols};'
            f'gap:4px;padding:2px 0 4px;border-bottom:1px solid var(--rule);margin-bottom:2px;">'
            f'{_spans}</div>'
        )

    return f'<div class="kpi-tab-rows">{_hdr}{top5}{next5}</div>{rest}{ver_mas_btn}'


def build_card_rows(df, t_key, cfg):
    """Genera array de rows para CR_CARD_TABS / RND_CARD_TABS.

    Reemplaza _build_card_rows_ef y _build_card_rows_cv en render_cr_p1.py.

    cfg keys:
        val_col       str  — columna de la métrica
        val_scale     fn   — transforma val → val_pct para el array JS
        banda_fn      fn   — función de banda
        banda_col     str  — columna pre-calculada de banda
        traf_col      str  — columna de tráfico (CR_Unicos, Trafico)
        traf_wow_col  str  — columna de WoW tráfico
        traf_wow_scale fn  — transforma traf_wow → delta para JS
        wow_col       str  — columna de WoW de la métrica
        hist_prev_col str  — columna del valor anterior
    """
    import math as _m
    NAME_COLS = {
        'hotel':   ('Hotel',    lambda r: truncate(clean_hotel_name(str(r.get('Hotel',''))), 38)),
        'corp':    ('CorpName', lambda r: truncate(clean_corp_name(str(r.get('CorpName',''))), 36)),
        'destino': ('Destino',  lambda r: clean_destino_name(str(r.get('Destino','')), 36)),
        'pais':    ('PaisDestino', lambda r: clean_pais_name(str(r.get('PaisDestino','')), 30)),
    }
    val_col      = cfg['val_col']
    val_scale    = cfg.get('val_scale', lambda v: round(float(v)*100, 2))
    banda_fn     = cfg.get('banda_fn', None)
    banda_col    = cfg.get('banda_col', '')
    traf_col     = cfg.get('traf_col', '')
    traf_wow_col = cfg.get('traf_wow_col', '')
    traf_wow_scl = cfg.get('traf_wow_scale', lambda v: round(float(v)/100, 0))
    wow_col      = cfg.get('wow_col', '')
    hist_prev    = cfg.get('hist_prev_col', '')

    _, name_fn = NAME_COLS.get(t_key, ('?', lambda r: str(r.get('Hotel', '?'))[:36]))
    sub_fn = (lambda r: truncate(str(r.get('CorpName','')), 20)
              if 'CorpName' in r.index else '') if t_key == 'hotel' else (lambda r: '')

    rows = []
    for _, r in df.iterrows():
        lab = name_fn(r)
        sub = sub_fn(r)
        val = r.get(val_col)
        try:
            _vf = float(val)
            if _m.isnan(_vf) or _m.isinf(_vf): val = None
        except (TypeError, ValueError): val = None

        val_pct = val_scale(val) if val is not None else None

        bnd = ''
        if banda_col and banda_col in r.index: bnd = r[banda_col]
        if not bnd and val is not None and banda_fn: bnd = banda_fn(val)
        bc = BANDA_COLORS.get(bnd, {})

        traf = r.get(traf_col) if traf_col else None
        try:
            traf = int(float(traf)) if traf is not None and not _m.isnan(float(traf)) else None
        except (TypeError, ValueError): traf = None

        traf_wow = r.get(traf_wow_col) if traf_wow_col else None
        try:
            traf_wow = traf_wow_scl(traf_wow) if traf_wow is not None and not _m.isnan(float(traf_wow)) else None
        except (TypeError, ValueError): traf_wow = None

        wow = r.get(wow_col) if wow_col else None
        try:
            wow = round(float(wow), 2) if wow is not None and not _m.isnan(float(wow)) else None
        except (TypeError, ValueError): wow = None

        hist_w21 = val_scale(val) if val is not None else 0
        hist_w20 = hist_w21
        if hist_prev:
            _prev = r.get(hist_prev)
            try:
                _pf = float(_prev)
                if not _m.isnan(_pf): hist_w20 = val_scale(_pf)
            except (TypeError, ValueError): pass

        rows.append([
            lab, sub,
            bc.get('bg','#F2EEE6'), bc.get('fg','#5F5E5A'), bnd,
            traf, traf_wow, val_pct, wow,
            round(hist_w21, 4), round(hist_w20, 4),
        ])
    return rows
