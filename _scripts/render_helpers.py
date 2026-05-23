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
    'Aceptable':     {'bg':'#EDE8F7', 'fg':'#3C3489', 'bd':'#5C469C'},
    'Revisar':       {'bg':'#FFEDD5', 'fg':'#7C2D12', 'bd':'#F97316'},
    'Crítica':       {'bg':'#FCE4F1', 'fg':'#99162B', 'bd':'#C0392B'},
    'Súper Crítica': {'bg':'#A32D2D', 'fg':'#FCEBEB', 'bd':'#791F1F'},
    'Sin Conversión':{'bg':'#F2EEE6', 'fg':'#5F5E5A', 'bd':'#8A8377'},
}

def banda_pill(banda, target=None, font_size='13px'):
    """Renderiza pill de severity · estilo Opción D (paleta D)
    El parámetro `target` se mantiene por compatibilidad de firma pero se IGNORA
    (decisión post W20 sesión 4: target va como caption separado, no dentro del badge).
    """
    c = BANDA_COLORS.get(banda, BANDA_COLORS['Sin Conversión'])
    bg = c['bg']
    fg = c['fg']
    bd = c['bd']
    # Mapear nombre de banda a versión mayúscula con espacios correctos
    banda_upper = banda.upper()
    return (f'<span style="display:inline-block;font-size:{font_size};font-weight:700;letter-spacing:.04em;'
            f'text-transform:uppercase;padding:10px 22px;border-radius:3px;background:{bg};color:{fg};'
            f'border:1px solid {bd};text-align:center;">{banda_upper}</span>')


def target_caption(target_text, font_size='11px'):
    """Caption gris fino para mostrar target debajo del badge.
    Reemplaza la parte '· Target X%' que antes iba dentro del pill."""
    return (f'<div style="font-size:{font_size};font-weight:500;color:var(--ink-muted);'
            f'letter-spacing:.02em;margin-top:6px;">Target {target_text}</div>')


def gauge_5levels(banda_actual, niveles_rnd_or_cr='nodispo'):
    """Render gauge bar 5 niveles para %NoDispo"""
    if niveles_rnd_or_cr == 'nodispo':
        levels = [
            ('Súper Crítica', '> 60%',    '#161616'),
            ('Crítica',       '20–60%',  '#C0392B'),
            ('Revisar',       '5–20%',   '#D4A878'),
            ('Aceptable',     '3–5%',    '#5C469C'),
            ('Exitosa',       '< 3%',    '#085041'),
        ]
    elif niveles_rnd_or_cr == 'rpm':
        levels = [
            ('Sin Conversión', 'BKGS=0',      '#161616'),
            ('Crítica',        '< $199',      '#C0392B'),
            ('Revisar',        '$200–$499',   '#D4A878'),
            ('Aceptable',      '$500–$649',   '#5C469C'),
            ('Exitosa',        '≥ $650',      '#085041'),
        ]
    elif niveles_rnd_or_cr == 'eficacia':
        levels = [
            ('Súper Crítica', '< 60%',    '#161616'),
            ('Crítica',       '60–85%',  '#C0392B'),
            ('Revisar',       '85–93%',  '#D4A878'),
            ('Aceptable',     '93–97%',  '#5C469C'),
            ('Exitosa',       '≥ 97%',   '#085041'),
        ]
    elif niveles_rnd_or_cr == 'convrate':
        levels = [
            ('Sin Conversión', 'BKGS=0',     '#161616'),
            ('Crítica',        '< 0,8%',    '#C0392B'),
            ('Revisar',        '0,8–1,5%',  '#D4A878'),
            ('Aceptable',      '1,5–2,5%',  '#5C469C'),
            ('Exitosa',        '> 2,5%',    '#085041'),
        ]
    cells = []
    for nombre, rango, color in levels:
        active = 'opacity:1;' if nombre == banda_actual else 'opacity:.30;'
        cells.append(f'<div style="flex:1;background:{color};height:8px;{active}"></div>')
    bar = '<div style="display:flex;gap:2px;margin-top:14px;">' + ''.join(cells) + '</div>'
    labels = '<div style="display:flex;justify-content:space-between;font-size:9px;color:var(--ink-muted);margin-top:2px;line-height:1.2;font-weight:600;">'
    for nombre, rango, _ in levels:
        labels += f'<span style="flex:1;text-align:center;padding:0 2px;">{nombre}</span>'
    labels += '</div>'
    return bar + labels

def wow_box(curr_label, curr_str, wow_str, wow_color, accent_color, week_num='W20', week_prev='W19'):
    """Caja con W18 actual + WoW + W17 prev. bg de WoW va con el wow_color."""
    # Mapeo color → bg suave
    if wow_color == '#2F6C34':       # verde
        wow_bg = '#E0F0E2'
    elif wow_color == '#C0392B':     # rojo
        wow_bg = '#FCE4F1'
    else:                            # gris/flat
        wow_bg = '#F2EEE6'
    return (
        f'<div style="margin-top:14px;background:var(--paper-soft);border-radius:4px;padding:8px;display:flex;align-items:stretch;gap:8px;">'
        f'<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">'
          f'<div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">{week_num}</div>'
          f'<div style="font-size:18px;font-weight:700;color:{accent_color};margin-top:2px;letter-spacing:-.01em;">{curr_str}</div>'
        f'</div>'
        f'<div style="flex:1;text-align:center;background:{wow_bg};padding:8px 4px;border-radius:3px;">'
          f'<div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:{wow_color};font-weight:700;">WoW</div>'
          f'<div style="font-size:18px;font-weight:700;color:{wow_color};margin-top:2px;letter-spacing:-.01em;">{wow_str}</div>'
        f'</div>'
        f'<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">'
          f'<div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">{week_prev}</div>'
          f'<div style="font-size:18px;font-weight:700;color:var(--ink-soft);margin-top:2px;letter-spacing:-.01em;">{curr_label}</div>'
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
