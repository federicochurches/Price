"""
render_mail_v3.py · Mail semanal Supply Optimization
v6.0 · W26 · TABLE-BASED LAYOUT (compatibilidad Gmail/Outlook/Apple Mail)
- Reescrito 100% con <table> + estilos inline — Gmail/Outlook ignoran <style> y CSS Grid/Flex
- Header: PriceTravel + badge Week NN (fondo negro)
- Fila 1: Status Contratación (netnew + PP + Gap)
- Fila 2: % No Disponibilidad por tier (Primarios / Secundarios / Terciarios)
- Fila 3: Performance (Conv Rate · % de Éxito · Bookability)
- Bloque editorial configurable por semana
- 3 CTAs: Hub · Supply · Inventario
- Todos los colores hardcodeados inline (compatibilidad mail clients)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
from pathlib import Path

# ── CONFIG SEMANAL ────────────────────────────────────────────────────────────
WEEK       = os.getenv('WEEK',      'W26')
PERIODO    = os.getenv('PERIODO',   '23–29 jun 2026')
VOL_NUM    = os.getenv('VOL_NUM',   '26')
PICKLE_RND = os.getenv('PICKLE_RND', f'rnd_w{VOL_NUM}_data.pkl')
PICKLE_CR  = os.getenv('PICKLE_CR',  f'cr_w{VOL_NUM}_data.pkl')
PICKLE_BK  = os.getenv('PICKLE_BK',  f'bk_w{VOL_NUM}_data.pkl')

# Texto editorial — editar cada semana
HIGHLIGHTS = os.getenv('MAIL_HIGHLIGHTS', '')

# Inventory
INV_NETNEW      = int(os.getenv('INV_NETNEW',      '0'))
INV_NETNEW_WOW  = int(os.getenv('INV_NETNEW_WOW',  '0'))   # delta vs semana anterior
INV_PP          = int(os.getenv('INV_PP',           '0'))
INV_GAP         = int(os.getenv('INV_GAP',          '0'))
INV_PCT_AVANCE  = float(os.getenv('INV_PCT_AVANCE', '0'))
INV_TARGET      = int(os.getenv('INV_TARGET',       '70000'))

OUTPUTS_DIR = os.getenv('OUTPUTS_DIR')
if not OUTPUTS_DIR or not os.path.isdir(OUTPUTS_DIR):
    # Claude (Linux): /mnt/user-data/outputs · Local (Windows): carpeta del script (raíz del repo)
    OUTPUTS_DIR = '/mnt/user-data/outputs' if os.path.isdir('/mnt/user-data/outputs') else str(Path(__file__).parent)
OUT_FILE    = f'{OUTPUTS_DIR}/Mail_{WEEK}.html'

WEEK_NUM      = WEEK.replace('W', '').zfill(2)
WEEK_NUM_INT  = int(VOL_NUM)
WEEK_PREV_INT = WEEK_NUM_INT - 1

URL_BASE   = 'https://analytics-desk.netlify.app'
URL_HUB    = URL_BASE
URL_SUPPLY = f'{URL_BASE}/reports/week-{WEEK_NUM}/SUPPLY_{WEEK}.html'
URL_INV    = f'{URL_BASE}/inventory/week-{WEEK_NUM}/INVENTORY_{WEEK}.html'

FONT = "'Helvetica Neue',Arial,sans-serif"

# ── Cargar pickles ────────────────────────────────────────────────────────────
with open(PICKLE_RND, 'rb') as f: DR = pickle.load(f)
with open(PICKLE_CR,  'rb') as f: DC = pickle.load(f)

try:
    with open(PICKLE_BK, 'rb') as f: DB = pickle.load(f)
    HAS_BK = True
except Exception: HAS_BK = False

# ── Helpers ───────────────────────────────────────────────────────────────────
def es(x, decimals=2):
    """Formato español: 3.340,50 → '3.340,50'"""
    if isinstance(x, float):
        s = f'{x:,.{decimals}f}'
        return s.replace(',', '|').replace('.', ',').replace('|', '.')
    return f'{int(x):,}'.replace(',', '.')

def fmt_int(x): return f'{int(x):,}'.replace(',', '.')

def wow_str(val, decimals=2, suffix='pp', invert=False):
    arrow = '▼' if val < 0 else '▲'
    sign  = '' if val < 0 else '+'
    return f'{arrow} {sign}{es(abs(val), decimals)}{suffix}'

def wow_colors(val, invert=False):
    good = (val < 0) if invert else (val >= 0)
    if good:
        return '#E1F5EE', '#1A6B4A'
    return '#FFE5E3', '#C0392B'

def wow_badge(val, decimals=2, suffix='pp', invert=False):
    bg, fg = wow_colors(val, invert)
    txt = wow_str(val, decimals, suffix, invert)
    # Inline-block span dentro de una <td> — funciona en todos los clientes
    return (
        f'<span style="display:inline-block;font-size:11px;font-weight:700;'
        f'padding:3px 8px;border-radius:10px;white-space:nowrap;'
        f'background-color:{bg};color:{fg};'
        f'font-family:{FONT};">{txt}</span>'
    )

def banda_badge(label, bg_color):
    return (
        f'<span style="display:inline-block;font-size:10px;font-weight:700;'
        f'padding:3px 9px;border-radius:3px;color:#ffffff;'
        f'background-color:{bg_color};'
        f'font-family:{FONT};">{label}</span>'
    )

# Colores de banda
BANDA_COLOR = {
    'Exitosa':       '#1A6B4A',
    'Aceptable':     '#FBBF24',
    'Revisar':       '#F97316',
    'Crítica':       '#C0392B',
    'Súper Crítica': '#2D2828',
    'Sin Conversión':'#8A8377',
}

def _banda_nd(pct):
    if pct < 3:   return 'Exitosa'
    if pct < 5:   return 'Aceptable'
    if pct < 20:  return 'Revisar'
    if pct < 60:  return 'Crítica'
    return 'Súper Crítica'

def _banda_ef(ef):
    if ef >= 97:  return 'Exitosa'
    if ef >= 93:  return 'Aceptable'
    if ef >= 85:  return 'Revisar'
    if ef >= 60:  return 'Crítica'
    return 'Súper Crítica'

def _banda_cv(cv):
    if cv >= 2.5: return 'Exitosa'
    if cv >= 1.5: return 'Aceptable'
    if cv >= 0.8: return 'Revisar'
    return 'Crítica'

def _banda_bk(bk):
    return _banda_ef(bk)  # mismos rangos que % de Éxito

# ── Métricas RND ──────────────────────────────────────────────────────────────
mr  = DR['M'][f'global_w{WEEK_NUM_INT}']
mr0 = DR['M'][f'global_w{WEEK_PREV_INT}']

rnd_pct     = mr['pct_nodispo'] * 100
rnd_pct_wow = (mr['pct_nodispo'] - mr0['pct_nodispo']) * 100

nd_tiers = DR.get('nd_por_tier', {})
tier_primario   = nd_tiers.get('PRIMARIO',   {})
tier_secundario = nd_tiers.get('SECUNDARIO', {})
tier_terciario  = nd_tiers.get('TERCIARIO',  {})

def _tier_val(t):  return t.get('pct_nodispo', rnd_pct)
def _tier_wow(t):  return t.get('wow_pp', 0.0)

nd_p   = _tier_val(tier_primario)
nd_p_w = _tier_wow(tier_primario)
nd_s   = _tier_val(tier_secundario)
nd_s_w = _tier_wow(tier_secundario)
nd_t   = _tier_val(tier_terciario)
nd_t_w = _tier_wow(tier_terciario)

# ── Métricas CR ───────────────────────────────────────────────────────────────
mc  = DC['M'][f'global_w{WEEK_NUM_INT}']
mc0 = DC['M'][f'global_w{WEEK_PREV_INT}']

cr_ef     = mc['eficacia']   * 100
cr_cv     = mc['conv_rate']  * 100
cr_ef_wow = (mc['eficacia']  - mc0['eficacia'])  * 100
cr_cv_wow = (mc['conv_rate'] - mc0['conv_rate']) * 100

# ── Bookability ───────────────────────────────────────────────────────────────
if HAS_BK:
    bk_val  = float(DB['bk_global']) * 100
    bk_prev = float(DB.get('bk_prev', 0)) * 100
    bk_wow  = bk_val - bk_prev if bk_prev > 0.1 else 0.0
else:
    bk_val, bk_wow = 0.0, 0.0

# ── Contratación ──────────────────────────────────────────────────────────────
HAS_INV = INV_PP > 0

if not HAS_INV:
    import re as _re_inv
    for _ip in [f'inventory/week-{WEEK_NUM}/INVENTORY_{WEEK}.html',
                f'inventory/week-{WEEK_NUM_INT}/INVENTORY_W{WEEK_NUM_INT}.html']:
        if os.path.exists(_ip):
            try:
                _ih = open(_ip, encoding='utf-8', errors='ignore').read()
                def _icard(cid):
                    m = _re_inv.search(r'id="' + cid + r'"[^>]*>\s*([\d.,]+)', _ih)
                    return m.group(1) if m else None
                _pp, _gap, _av = _icard('card-pp'), _icard('card-gap'), _icard('card-avance')
                if _pp:
                    INV_PP         = int(_pp.replace('.', '').replace(',', ''))
                    INV_NETNEW     = int(_gap.replace('.', '').replace(',', '')) if _gap else 0
                    INV_PCT_AVANCE = float(_av.replace(',', '.')) if _av else round(INV_PP / INV_TARGET * 100, 1)
                    INV_GAP        = max(INV_TARGET - INV_PP, 0)
                    HAS_INV        = True
                    print(f'  [inv] KPIs auto-cargados de {_ip}: PP={INV_PP} netnew={INV_NETNEW} avance={INV_PCT_AVANCE}%')
            except Exception as _e:
                print(f'  [inv] auto-carga falló: {_e}')
            break

# ── Bandas calculadas ──────────────────────────────────────────────────────────
_b_p = _banda_nd(nd_p)
_b_s = _banda_nd(nd_s)
_b_t = _banda_nd(nd_t)

_b_cv = _banda_cv(cr_cv)
_b_ef = _banda_ef(cr_ef)
_b_bk = _banda_bk(bk_val) if HAS_BK else 'Sin datos'

_inv_wow_sign = '+' if INV_NETNEW_WOW >= 0 else ''
_inv_wow_arrow = '▲' if INV_NETNEW_WOW >= 0 else '▼'
_inv_wow_bg = '#E1F5EE' if INV_NETNEW_WOW >= 0 else '#FFE5E3'
_inv_wow_fg = '#1A6B4A' if INV_NETNEW_WOW >= 0 else '#C0392B'
_inv_wow_lbl = f'{_inv_wow_arrow} {_inv_wow_sign}{INV_NETNEW_WOW} vs W{WEEK_PREV_INT}'

# ════════════════════════════════════════════════════════════════════════════
# HELPERS DE TABLA (reemplazan los divs flex/grid)
# ════════════════════════════════════════════════════════════════════════════

def sec_header(dot_color, label):
    """Header de sección: punto de color + label uppercase. Tabla de 1 fila."""
    return f'''
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0;">
  <tr>
    <td style="padding:16px 20px 8px 20px;font-family:{FONT};">
      <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background-color:{dot_color};margin-right:7px;"></span>
      <span style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#8A8377;font-family:{FONT};">{label}</span>
    </td>
  </tr>
</table>'''

def kpi_triple(cells):
    """
    3 celdas KPI lado a lado usando <table> con 3 <td width=33%>.
    cells = lista de dicts: {name, value, wow_html, banda_label, accent}
    """
    tds = []
    for i, c in enumerate(cells):
        border_color = c.get('accent', '#E8E2DA') if i == 0 else '#E8E2DA'
        banda_lbl = c['banda_label']
        banda_bg  = BANDA_COLOR.get(banda_lbl, '#8A8377')
        tds.append(f'''
    <td valign="top" width="33%" style="padding:12px 10px 16px 14px;border-left:3px solid {border_color};font-family:{FONT};">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#8A8377;font-family:{FONT};margin-bottom:6px;">{c['name']}</div>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td style="font-size:24px;font-weight:700;letter-spacing:-.02em;color:#161616;font-family:{FONT};padding-right:8px;">{c['value']}</td>
        <td>{c['wow_html']}</td>
      </tr></table>
      <div style="margin-top:8px;">{banda_badge(banda_lbl, banda_bg)}</div>
    </td>''')
    return f'''
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0;">
  <tr>{''.join(tds)}</tr>
</table>'''

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE CONTRATACIÓN (tabla 3 columnas: hero + 2 subs)
# ════════════════════════════════════════════════════════════════════════════
if HAS_INV:
    _inv_block = f'''
{sec_header('#4FC3F4', 'Status Contratación')}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0;border-top:1px solid #EDEAE4;">
  <tr>
    <td valign="middle" width="40%" style="padding:14px 16px 16px 14px;border-left:3px solid #4FC3F4;border-right:1px solid #EDEAE4;font-family:{FONT};">
      <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#8A8377;font-family:{FONT};margin-bottom:6px;">Incorporados esta semana</div>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td style="font-size:28px;font-weight:800;color:#161616;font-family:{FONT};padding-right:8px;">+{fmt_int(INV_NETNEW)}</td>
        <td><span style="display:inline-block;font-size:11px;font-weight:700;padding:3px 8px;border-radius:10px;white-space:nowrap;background-color:{_inv_wow_bg};color:{_inv_wow_fg};font-family:{FONT};">{_inv_wow_lbl}</span></td>
      </tr></table>
    </td>
    <td valign="middle" width="30%" style="padding:14px 14px 16px;border-right:1px solid #EDEAE4;font-family:{FONT};">
      <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#8A8377;font-family:{FONT};margin-bottom:6px;">Producto Propio</div>
      <div style="font-size:19px;font-weight:700;color:#161616;font-family:{FONT};">{fmt_int(INV_PP)}</div>
      <div style="font-size:10px;color:#8A8377;font-family:{FONT};margin-top:2px;">{es(INV_PCT_AVANCE, 1)}% avance</div>
    </td>
    <td valign="middle" width="30%" style="padding:14px 14px 16px;font-family:{FONT};">
      <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#8A8377;font-family:{FONT};margin-bottom:6px;">Gap Target</div>
      <div style="font-size:19px;font-weight:700;color:#161616;font-family:{FONT};">{fmt_int(INV_GAP)}</div>
      <div style="font-size:10px;color:#8A8377;font-family:{FONT};margin-top:2px;">Target {fmt_int(INV_TARGET)}</div>
    </td>
  </tr>
</table>'''
else:
    _inv_block = ''

# ════════════════════════════════════════════════════════════════════════════
# EDITORIAL
# ════════════════════════════════════════════════════════════════════════════
_editorial_html = ''
if HIGHLIGHTS:
    _editorial_html = f'''
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0;border-top:1px solid #EDEAE4;">
  <tr>
    <td style="padding:16px 20px 18px;font-family:{FONT};">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#8A8377;font-family:{FONT};margin-bottom:9px;">Highlights de la semana</div>
      <div style="font-size:13px;color:#333333;line-height:1.6;font-family:{FONT};">{HIGHLIGHTS}</div>
    </td>
  </tr>
</table>'''

# ════════════════════════════════════════════════════════════════════════════
# FILA NoDispo (tabla 3 columnas)
# ════════════════════════════════════════════════════════════════════════════
_nd_row = kpi_triple([
    {'name':'Destinos Primarios',   'value':es(nd_p,2)+'%', 'wow_html':wow_badge(nd_p_w, invert=True), 'banda_label':_b_p, 'accent':'#EA0074'},
    {'name':'Destinos Secundarios', 'value':es(nd_s,2)+'%', 'wow_html':wow_badge(nd_s_w, invert=True), 'banda_label':_b_s},
    {'name':'Destinos Terciarios',  'value':es(nd_t,2)+'%', 'wow_html':wow_badge(nd_t_w, invert=True), 'banda_label':_b_t},
])

# ════════════════════════════════════════════════════════════════════════════
# FILA Performance (tabla 3 columnas, 2 o 3 celdas según HAS_BK)
# ════════════════════════════════════════════════════════════════════════════
_perf_cells = [
    {'name':'Conv Rate',  'value':es(cr_cv,2)+'%', 'wow_html':wow_badge(cr_cv_wow), 'banda_label':_b_cv, 'accent':'#5C469C'},
    {'name':'% de Éxito', 'value':es(cr_ef,2)+'%', 'wow_html':wow_badge(cr_ef_wow), 'banda_label':_b_ef},
]
if HAS_BK:
    _perf_cells.append({'name':'Bookability', 'value':es(bk_val,1)+'%', 'wow_html':wow_badge(bk_wow), 'banda_label':_b_bk})
_perf_row = kpi_triple(_perf_cells)

# ════════════════════════════════════════════════════════════════════════════
# CTA BUTTONS (tabla, no flex)
# ════════════════════════════════════════════════════════════════════════════
_cta_btn = lambda url, label, bg, fg: (
    f'<td style="padding:0 4px 6px 0;">'
    f'<a href="{url}" style="display:inline-block;padding:10px 16px;font-size:11px;font-weight:700;'
    f'letter-spacing:.02em;text-decoration:none;color:{fg};background-color:{bg};font-family:{FONT};">{label}</a>'
    f'</td>'
)

# ════════════════════════════════════════════════════════════════════════════
# MAIL COMPLETO — tabla raíz único, todo inline
# ════════════════════════════════════════════════════════════════════════════
mail_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="x-apple-disable-message-reformatting">
<title>Weekly KPIs Supply · {WEEK}</title>
</head>
<body style="margin:0;padding:0;background-color:#B8B0A4;font-family:{FONT};">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#B8B0A4;">
<tr><td align="center" style="padding:24px 12px 40px;">

<div style="background:#FFF8E1;border-left:4px solid #F2B90B;padding:14px 18px;margin-bottom:20px;font-size:12px;line-height:1.55;font-family:{FONT};max-width:640px;text-align:left;">
  <strong style="color:#8A6300;">Cómo enviar:</strong>
  Click adentro del área blanca · Ctrl+A · Ctrl+C · pegar en Gmail/Outlook.<br>
  Verificá la URL de los botones y agregá destinatarios en CCO antes de enviar.
</div>

<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#8A8377;margin:14px 0 5px;font-family:{FONT};max-width:640px;text-align:left;">Asunto</div>
<div style="background:#fff;border:1px solid #C9C1B0;padding:11px 15px;font-size:15px;font-weight:600;font-family:{FONT};max-width:640px;text-align:left;">Weekly KPIs Supply · {WEEK} · Disponibilidad, Conectividades &amp; Performance</div>

<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#8A8377;margin:14px 0 5px;font-family:{FONT};max-width:640px;text-align:left;">Preheader</div>
<div style="background:#fff;border:1px solid #C9C1B0;padding:11px 15px;font-size:14px;font-family:{FONT};max-width:640px;text-align:left;">NoDispo Primarios {es(nd_p,2)}% · % de Éxito {es(cr_ef,2)}% · Conv Rate {es(cr_cv,2)}% · Bookability {es(bk_val,1)}%</div>

<hr style="border:none;border-top:2px dashed #C9C1B0;margin:28px auto;max-width:640px;">
<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#8A8377;margin:14px 0 5px;font-family:{FONT};max-width:640px;text-align:left;">Cuerpo (copiar desde acá ↓)</div>
<p style="font-size:11px;color:#8A8377;margin:6px 0 16px;font-style:italic;font-family:{FONT};max-width:640px;text-align:left;">Click adentro del recuadro blanco · Ctrl+A · Ctrl+C · Ctrl+V en el compose.</p>

<!-- DRAFT_BODY_START -->
<table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0" style="max-width:640px;width:100%;background-color:#ffffff;font-family:{FONT};">

  <!-- HEADER -->
  <tr>
    <td style="border-top:3px solid #161616;border-bottom:1px solid #E8E2DA;padding:18px 20px 14px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td valign="middle">
            <div style="font-size:9px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:#8A8377;margin-bottom:4px;font-family:{FONT};">Weekly KPIs</div>
            <div style="font-size:22px;font-weight:800;letter-spacing:-.02em;color:#161616;line-height:1;font-family:{FONT};">PriceTravel</div>
          </td>
          <td valign="middle" align="right" width="140">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="right"><tr>
              <td style="background-color:#161616;padding:8px 14px;text-align:right;">
                <span style="font-size:14px;font-weight:800;color:#ffffff;line-height:1.3;display:block;font-family:{FONT};">Week {VOL_NUM}</span>
                <span style="font-size:9px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#ffffff;display:block;font-family:{FONT};">{PERIODO}</span>
              </td>
            </tr></table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- STRIPE -->
  <tr><td style="height:3px;background-color:#EA0074;font-size:0;line-height:0;">&nbsp;</td></tr>

  <!-- CONTRATACIÓN -->
  <tr><td>{_inv_block}</td></tr>

  <!-- NoDispo -->
  <tr><td>
    {sec_header('#EA0074', '% No Disponibilidad')}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-bottom:14px;">{_nd_row}</td></tr></table>
  </td></tr>

  <!-- Performance -->
  <tr><td>
    {sec_header('#5C469C', 'Performance')}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-bottom:14px;">{_perf_row}</td></tr></table>
  </td></tr>

  <!-- Editorial -->
  <tr><td>{_editorial_html}</td></tr>

  <!-- CTA -->
  <tr>
    <td style="background-color:#F5F1EB;border-top:1px solid #E0D9CF;padding:18px 20px;">
      <p style="font-size:11px;color:#555555;line-height:1.55;margin:0 0 12px;font-family:{FONT};">Encontrá los findings completos por Hotel, Corporativo y Destinos. Descargá el Análisis de tu cluster: Destinos México, Destinos US, CALA, Cuentas Estratégicas y Global Accounts.<br>Resumen Ejecutivo y Plan de Acción en el Hub.</p>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        {_cta_btn(URL_HUB, '→ Hub Supply Optimization', '#161616', '#ffffff')}
        {_cta_btn(URL_SUPPLY, f'→ Disponibilidad &amp; Conectividades {WEEK}', '#EA0074', '#ffffff')}
        {_cta_btn(URL_INV, f'→ Inventario {WEEK}', '#4FC3F4', '#161616')}
      </tr></table>
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="background-color:#F5F1EB;border-top:1px solid #C9C1B0;padding:12px 20px;text-align:center;">
      <span style="font-size:11px;color:#8A8377;font-family:{FONT};">PriceTravel · Supply Optimization · <strong>{WEEK}</strong> · {PERIODO} · Vol. {VOL_NUM}</span>
    </td>
  </tr>

</table>
<!-- DRAFT_BODY_END -->

</td></tr>
</table>

</body>
</html>'''

# ── Guardar ───────────────────────────────────────────────────────────────────
out = Path(OUT_FILE)
out.write_text(mail_html, encoding='utf-8')
print(f'Mail {WEEK} v6.0 (table-based) → {out}')
print(f'Tamaño: {len(mail_html):,} chars')

_script_dir = Path(__file__).parent
_email_dir  = _script_dir / '_email' / f'week-{WEEK_NUM}'
_email_dir.mkdir(parents=True, exist_ok=True)
_email_dst  = _email_dir / f'Mail_{WEEK}.html'
_email_dst.write_text(mail_html, encoding='utf-8')
print(f'  → copia en _email/week-{WEEK_NUM}/ ✓')
