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
    # Paleta D · única fuente de verdad · sincronizada con BANDAS.md
    # bg=fondo badge · fg=texto badge · bd=borde badge · bar=color barra de progreso severity
    'Exitosa':       {'bg':'#E1F5EE', 'fg':'#1A6B4A', 'bd':'#1D9E75', 'bar':'#1A6B4A'},
    'Aceptable':     {'bg':'#FEF9C3', 'fg':'#713F12', 'bd':'#FCD34D', 'bar':'#FCD34D'},
    'Revisar':       {'bg':'#FED7AA', 'fg':'#C2410C', 'bd':'#F97316', 'bar':'#F97316'},
    'Crítica':       {'bg':'#FCE4F1', 'fg':'#99162B', 'bd':'#C0392B', 'bar':'#C0392B'},
    'Súper Crítica': {'bg':'#EDECEC', 'fg':'#4A3F3F', 'bd':'#9B2222', 'bar':'#C0392B'},
    'Sin Conversión':{'bg':'#F2EEE6', 'fg':'#5F5E5A', 'bd':'#8A8377', 'bar':'#8A8377'},
}

def _mini_badge(bnd):
    """Badge de banda inline 8px."""
    if not bnd or not isinstance(bnd, str): return ''
    bc = BANDA_COLORS.get(bnd, {})
    bg = bc.get('bg', '#F2EEE6'); fg = bc.get('fg', '#5F5E5A')
    return f'<span style="flex-shrink:0;font-size:8px;font-weight:700;padding:1px 4px;border-radius:2px;background:{bg};color:{fg};text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;">{bnd}</span>'

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
            ('Súper Crítica', '#C0392B'),
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
            ('Súper Crítica', '#C0392B'),
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
        f'<div class="sb-pill-wrap" style="margin-left:auto;display:flex;align-items:center;'
        f'gap:7px;padding:0 8px 5px 12px;border-left:1px solid var(--rule-soft);">'
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
        f'<div class="sb-pill" style="display:inline-flex;align-items:center;gap:4px;'
        f'background:var(--paper-soft);border:1px solid var(--rule);border-radius:20px;'
        f'padding:2px 6px;transition:border-color .15s,box-shadow .15s;min-width:0;">'
        f'<svg width="10" height="10" viewBox="0 0 24 24" fill="none" '
        f'stroke="var(--ink-muted)" stroke-width="2.5" stroke-linecap="round" '
        f'stroke-linejoin="round" style="flex-shrink:0;" aria-hidden="true">'
        f'<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
        f'<input type="text" id="{input_id}" placeholder="" '
        f'data-sb-table="true" '
        f'autocomplete="off" spellcheck="false" '
        f'style="background:none;border:none;outline:none;font-size:10px;'
        f'font-family:inherit;color:var(--ink);width:48px;min-width:0;'
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
    )
