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
    'Exitosa':       {'bg':'#E1F5EE', 'fg':'#085041', 'bd':'#1D9E75'},
    'Aceptable':     {'bg':'#FEF3C7', 'fg':'#92400E', 'bd':'#F59E0B'},
    'Revisar':       {'bg':'#FFEDD5', 'fg':'#7C2D12', 'bd':'#F97316'},
    'Crítica':       {'bg':'#FCE4F1', 'fg':'#99162B', 'bd':'#C0392B'},
    'Súper Crítica': {'bg':'#FECACA', 'fg':'#7F1D1D', 'bd':'#DC2626'},
    'Sin Conversión':{'bg':'#F2EEE6', 'fg':'#5F5E5A', 'bd':'#8A8377'},
}

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
    """Gauge bar 5 niveles · height:6px · opacity:1 uniforme · BANDAS.md"""
    if niveles_rnd_or_cr == 'nodispo':
        levels = [
            ('Súper Crítica', '#161616'),
            ('Crítica',       '#C0392B'),
            ('Revisar',       '#D4A878'),
            ('Aceptable',     '#5C469C'),
            ('Exitosa',       '#085041'),
        ]
    elif niveles_rnd_or_cr == 'rpm':
        levels = [
            ('Sin Conversión', '#8A8377'),
            ('Crítica',        '#C0392B'),
            ('Revisar',        '#D4A878'),
            ('Aceptable',      '#5C469C'),
            ('Exitosa',        '#085041'),
        ]
    elif niveles_rnd_or_cr == 'eficacia':
        levels = [
            ('Súper Crítica', '#161616'),
            ('Crítica',       '#C0392B'),
            ('Revisar',       '#D4A878'),
            ('Aceptable',     '#5C469C'),
            ('Exitosa',       '#085041'),
        ]
    elif niveles_rnd_or_cr == 'convrate':
        levels = [
            ('Sin Conversión', '#8A8377'),
            ('Crítica',        '#C0392B'),
            ('Revisar',        '#D4A878'),
            ('Aceptable',      '#5C469C'),
            ('Exitosa',        '#085041'),
        ]
    cells = []
    for nombre, color in levels:
        # Banda activa: borde inferior marcado; todas opacity:1
        active_style = 'border-bottom:2px solid var(--ink);' if nombre == banda_actual else ''
        cells.append(f'<div style="flex:1;background:{color};height:6px;opacity:1;{active_style}"></div>')
    return '<div style="display:flex;gap:2px;margin-top:10px;">' + ''.join(cells) + '</div>'

def wow_box(curr_label, curr_str, wow_str, wow_color, accent_color, week_num='W20', week_prev='W19'):
    """Caja compacta W20/WoW/W19."""
    if wow_color == '#2F6C34':   wow_bg = '#E0F0E2'
    elif wow_color == '#C0392B': wow_bg = '#FCE4F1'
    else:                        wow_bg = '#F2EEE6'
    return (
        f'<div style="margin-top:8px;background:var(--paper-soft);border-radius:3px;padding:6px;display:flex;align-items:stretch;gap:6px;">'
        f'<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;">'
          f'<div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">{week_num}</div>'
          f'<div style="font-size:15px;font-weight:700;color:{accent_color};margin-top:1px;letter-spacing:-.01em;">{curr_str}</div>'
        f'</div>'
        f'<div style="flex:1;text-align:center;background:{wow_bg};padding:5px 4px;border-radius:2px;">'
          f'<div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:{wow_color};font-weight:700;">WoW</div>'
          f'<div style="font-size:15px;font-weight:700;color:{wow_color};margin-top:1px;letter-spacing:-.01em;">{wow_str}</div>'
        f'</div>'
        f'<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;">'
          f'<div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">{week_prev}</div>'
          f'<div style="font-size:15px;font-weight:700;color:var(--ink-soft);margin-top:1px;letter-spacing:-.01em;">{curr_label}</div>'
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
    if pd.isna(x): return '-'
    return f'{x:,.2f}'.replace(',', '|').replace('.', ',').replace('|', '.')

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
