"""
render_mail_v3.py · Mail semanal Supply Optimization
v5.0 · W26 · Nuevo layout visual
- Header: PriceTravel + badge Week NN (fondo negro)
- Fila 1: Status Contratación (netnew + PP + Gap)
- Fila 2: % No Disponibilidad por tier (Primarios / Secundarios / Terciarios)
- Fila 3: Performance (Conv Rate · Eficacia · Bookability)
- Bloque editorial configurable por semana
- 3 CTAs: Hub · Supply · Inventario
- Todos los colores críticos hardcodeados inline (compatibilidad mail clients)
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
    """Devuelve el valor del WoW como string con flecha."""
    if invert:
        good = val < 0
    else:
        good = val >= 0
    arrow = '▼' if val < 0 else '▲'
    sign  = '' if val < 0 else '+'
    return f'{arrow} {sign}{es(abs(val), decimals)}{suffix}'

def wow_colors(val, invert=False):
    """Devuelve (bg, fg) para el badge WoW."""
    good = (val < 0) if invert else (val >= 0)
    if good:
        return '#E1F5EE', '#1A6B4A'
    return '#FFE5E3', '#C0392B'

def wow_badge(val, decimals=2, suffix='pp', invert=False):
    bg, fg = wow_colors(val, invert)
    txt = wow_str(val, decimals, suffix, invert)
    return (
        f'<span style="display:inline-block;font-size:8px;font-weight:700;'
        f'padding:2px 6px;border-radius:10px;white-space:nowrap;'
        f'background-color:{bg};color:{fg};'
        f'font-family:\'Helvetica Neue\',Arial,sans-serif;">{txt}</span>'
    )

def banda_badge(label, bg_color):
    return (
        f'<span style="display:inline-block;font-size:7px;font-weight:700;'
        f'padding:2px 7px;border-radius:3px;color:#ffffff;'
        f'background-color:{bg_color};align-self:flex-start;'
        f'font-family:\'Helvetica Neue\',Arial,sans-serif;">{label}</span>'
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
    return _banda_ef(bk)  # mismos rangos que Eficacia

# ── Métricas RND ──────────────────────────────────────────────────────────────
mr  = DR['M'][f'global_w{WEEK_NUM_INT}']
mr0 = DR['M'][f'global_w{WEEK_PREV_INT}']

rnd_pct     = mr['pct_nodispo'] * 100
rnd_pct_wow = (mr['pct_nodispo'] - mr0['pct_nodispo']) * 100

# NoDispo por tier — requiere nd_por_tier en el pickle (W26+)
# Fallback: mostrar global si no hay tiers
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

# Auto-cargar KPIs de inventory del INVENTORY_WNN.html si no vienen por env.
# calc_supply NO pasa INV_* → sin esto la card de Contratación desaparece al regenerar.
# Los IDs card-pp / card-gap (netnew semanal) / card-avance son estables en el reporte de Inventory.
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

# ── CSS compartido ────────────────────────────────────────────────────────────
CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  background: #B8B0A4; padding: 24px 12px 40px; color: #161616;
}
.instructions {
  background: #FFF8E1; border-left: 4px solid #F2B90B;
  padding: 14px 18px; margin-bottom: 20px;
  font-size: 12px; line-height: 1.55;
}
.instructions strong { color: #8A6300; }
.field-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .12em; color: #8A8377; margin: 14px 0 5px;
}
.field-box {
  background: #fff; border: 1px solid #C9C1B0;
  padding: 11px 15px; font-size: 14px;
}
.field-box.subject { font-size: 15px; font-weight: 600; }
hr.divider { border: none; border-top: 2px dashed #C9C1B0; margin: 28px 0; }
.copy-tip { font-size: 11px; color: #8A8377; margin: 6px 0 16px; font-style: italic; }
.mail {
  max-width: 640px; margin: 0 auto;
  background: #ffffff; box-shadow: 0 4px 20px rgba(0,0,0,.14);
  font-family: 'Helvetica Neue', Arial, sans-serif;
}
.m-hdr {
  border-top: 3px solid #161616; border-bottom: 1px solid #E8E2DA;
  padding: 14px 20px 12px;
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
}
.m-eyebrow {
  font-size: 8px; font-weight: 700; letter-spacing: .15em;
  text-transform: uppercase; color: #8A8377; margin-bottom: 3px;
}
.m-brand { font-size: 20px; font-weight: 800; letter-spacing: -.02em; color: #161616; line-height: 1; }
.m-stripe { height: 2px; background: linear-gradient(90deg, #EA0074 50%, #5C469C 50%); }
.m-sec { border-top: 1px solid #EDEAE4; }
.m-sec-hdr { padding: 9px 20px 0; display: flex; align-items: center; gap: 7px; }
.m-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; display: inline-block; }
.m-sec-lbl {
  font-size: 8px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .13em; color: #8A8377;
}
.m-triple { display: grid; grid-template-columns: 1fr 1fr 1fr; padding: 0 20px; }
.m-cell {
  padding: 10px 8px 14px 12px; border-left: 3px solid #E8E2DA;
  display: flex; flex-direction: column; gap: 5px;
}
.m-cell-name {
  font-size: 8px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .1em; color: #8A8377;
}
.m-val-row { display: flex; align-items: baseline; gap: 7px; flex-wrap: wrap; }
.m-val { font-size: 20px; font-weight: 700; line-height: 1; letter-spacing: -.02em; color: #161616; }
.m-inv-row {
  display: grid; grid-template-columns: auto 1fr 1fr;
  border-top: 1px solid #EDEAE4; margin: 0 20px;
}
.m-inv-hero {
  padding: 10px 14px 12px 12px; border-right: 1px solid #EDEAE4;
  border-left: 3px solid #4FC3F4;
  display: flex; flex-direction: column; justify-content: center; gap: 4px;
}
.m-inv-sub {
  padding: 10px 12px 12px; border-right: 1px solid #EDEAE4;
  display: flex; flex-direction: column; justify-content: center; gap: 2px;
}
.m-inv-sub:last-child { border-right: none; }
.m-inv-lbl {
  font-size: 7px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #8A8377;
}
.m-inv-val { font-size: 15px; font-weight: 700; color: #161616; line-height: 1; }
.m-inv-note { font-size: 8px; color: #8A8377; }
.m-editorial { padding: 14px 20px 16px; border-top: 1px solid #EDEAE4; }
.m-editorial-lbl {
  font-size: 8px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .13em; color: #8A8377; margin-bottom: 8px;
}
.m-editorial p { font-size: 12px; color: #333333; line-height: 1.65; }
.m-cta { background: #F5F1EB; border-top: 1px solid #E0D9CF; padding: 14px 20px; }
.m-cta p { font-size: 10px; color: #555555; line-height: 1.55; margin-bottom: 10px; }
.m-cta-btns { display: flex; gap: 6px; flex-wrap: wrap; }
.m-ftr { background: #F5F1EB; border-top: 1px solid #C9C1B0; padding: 10px 20px; text-align: center; }
.m-ftr-txt { font-size: 10px; color: #8A8377; }
@media (max-width: 480px) {
  body { padding: 0; background: #ffffff; }
  .mail { box-shadow: none; }
  .m-hdr { padding: 9px 14px 8px; }
  .m-brand { font-size: 16px; }
  .m-sec-hdr { padding: 7px 14px 0; }
  .m-triple { padding: 0 14px; }
  .m-cell { padding: 7px 5px 10px 9px; }
  .m-val { font-size: 15px; }
  .m-inv-row { grid-template-columns: 1fr 1fr 1fr; margin: 0 14px; }
  .m-inv-hero { padding: 7px 8px 9px 10px; }
  .m-inv-sub { padding: 7px 6px 9px 8px; }
  .m-inv-val { font-size: 12px; }
  .m-inv-note { font-size: 7px; }
  .m-editorial { padding: 12px 14px 14px; }
  .m-editorial p { font-size: 11px; }
  .m-cta { padding: 10px 14px; }
  .m-ftr { padding: 7px 14px; }
}
"""

# ── Helper: celda KPI ─────────────────────────────────────────────────────────
def _kpi_cell(name, value_str, wow_html, banda_label, accent_color=None, first=False):
    border = f'border-left-color:{accent_color};' if (first and accent_color) else ''
    return f'''
      <div class="m-cell" style="{border}">
        <div class="m-cell-name">{name}</div>
        <div class="m-val-row">
          <div class="m-val">{value_str}</div>
          {wow_html}
        </div>
        {banda_badge(banda_label, BANDA_COLOR.get(banda_label, '#8A8377'))}
      </div>'''

# ── HTML del mail ─────────────────────────────────────────────────────────────
# Fila 2: NoDispo tiers
_b_p = _banda_nd(nd_p)
_b_s = _banda_nd(nd_s)
_b_t = _banda_nd(nd_t)

# Fila 3: Performance
_b_cv = _banda_cv(cr_cv)
_b_ef = _banda_ef(cr_ef)
_b_bk = _banda_bk(bk_val) if HAS_BK else 'Sin datos'

# Contratación WoW
_inv_wow_sign = '+' if INV_NETNEW_WOW >= 0 else ''
_inv_wow_arrow = '▲' if INV_NETNEW_WOW >= 0 else '▼'
_inv_wow_bg = '#E1F5EE' if INV_NETNEW_WOW >= 0 else '#FFE5E3'
_inv_wow_fg = '#1A6B4A' if INV_NETNEW_WOW >= 0 else '#C0392B'
_inv_wow_lbl = f'{_inv_wow_arrow} {_inv_wow_sign}{INV_NETNEW_WOW} vs W{WEEK_PREV_INT}'

# Editorial
_editorial_html = ''
if HIGHLIGHTS:
    _editorial_html = f'''
  <div class="m-editorial">
    <div class="m-editorial-lbl">Highlights de la semana</div>
    <p>{HIGHLIGHTS}</p>
  </div>'''

# Bloque contratación
if HAS_INV:
    _inv_block = f'''
  <div class="m-sec">
    <div class="m-sec-hdr">
      <span class="m-dot" style="background-color:#4FC3F4;"></span>
      <span class="m-sec-lbl">Status Contratación</span>
    </div>
    <div class="m-inv-row">
      <div class="m-inv-hero">
        <div class="m-inv-lbl">Incorporados esta semana</div>
        <div style="display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;">
          <span style="font-size:22px;font-weight:800;color:#161616;line-height:1;font-family:'Helvetica Neue',Arial,sans-serif;">+{fmt_int(INV_NETNEW)}</span>
          <span style="display:inline-block;font-size:8px;font-weight:700;padding:2px 6px;border-radius:10px;white-space:nowrap;background-color:{_inv_wow_bg};color:{_inv_wow_fg};font-family:'Helvetica Neue',Arial,sans-serif;">{_inv_wow_lbl}</span>
        </div>
      </div>
      <div class="m-inv-sub">
        <div class="m-inv-lbl">Producto Propio</div>
        <div class="m-inv-val">{fmt_int(INV_PP)}</div>
        <div class="m-inv-note">{es(INV_PCT_AVANCE, 1)}% avance</div>
      </div>
      <div class="m-inv-sub">
        <div class="m-inv-lbl">Gap Target</div>
        <div class="m-inv-val">{fmt_int(INV_GAP)}</div>
        <div class="m-inv-note">Target {fmt_int(INV_TARGET)}</div>
      </div>
    </div>
  </div>'''
else:
    _inv_block = ''

mail_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly KPIs Supply · {WEEK}</title>
<style>{CSS}</style>
</head>
<body>

<div class="instructions">
  <strong>Cómo enviar:</strong>
  Click adentro del área blanca · Ctrl+A · Ctrl+C · pegar en Gmail/Outlook.<br>
  Verificá la URL de los botones y agregá destinatarios en CCO antes de enviar.
</div>

<div class="field-label">Asunto</div>
<div class="field-box subject">Weekly KPIs Supply · {WEEK} · Disponibilidad, Conectividades &amp; Performance</div>

<div class="field-label">Preheader</div>
<div class="field-box">NoDispo Primarios {es(nd_p,2)}% · Eficacia {es(cr_ef,2)}% · Conv Rate {es(cr_cv,2)}% · Bookability {es(bk_val,1)}%</div>

<hr class="divider">
<div class="field-label">Cuerpo (copiar desde acá ↓)</div>
<p class="copy-tip">Click adentro del recuadro blanco · Ctrl+A · Ctrl+C · Ctrl+V en el compose.</p>

<!-- DRAFT_BODY_START -->
<div class="mail">

  <!-- HEADER -->
  <div class="m-hdr">
    <div>
      <div class="m-eyebrow">Weekly KPIs</div>
      <div class="m-brand">PriceTravel</div>
    </div>
    <div style="background-color:#161616;padding:6px 12px;text-align:right;flex-shrink:0;">
      <span style="font-size:13px;font-weight:800;color:#ffffff;line-height:1;display:block;font-family:'Helvetica Neue',Arial,sans-serif;">Week {VOL_NUM}</span>
      <span style="font-size:7px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#8A8377;display:block;margin-top:2px;font-family:'Helvetica Neue',Arial,sans-serif;">{PERIODO}</span>
    </div>
  </div>
  <div class="m-stripe"></div>

  {_inv_block}

  <!-- FILA 2 · NoDispo por tier -->
  <div class="m-sec">
    <div class="m-sec-hdr">
      <span class="m-dot" style="background-color:#EA0074;"></span>
      <span class="m-sec-lbl">% No Disponibilidad</span>
    </div>
    <div class="m-triple">
      {_kpi_cell('Destinos Primarios',   es(nd_p,2)+'%', wow_badge(nd_p_w, invert=True), _b_p, '#EA0074', first=True)}
      {_kpi_cell('Destinos Secundarios', es(nd_s,2)+'%', wow_badge(nd_s_w, invert=True), _b_s)}
      {_kpi_cell('Destinos Terciarios',  es(nd_t,2)+'%', wow_badge(nd_t_w, invert=True), _b_t)}
    </div>
  </div>

  <!-- FILA 3 · Performance -->
  <div class="m-sec" style="border-bottom:none;">
    <div class="m-sec-hdr">
      <span class="m-dot" style="background-color:#5C469C;"></span>
      <span class="m-sec-lbl">Performance</span>
    </div>
    <div class="m-triple">
      {_kpi_cell('Conv Rate', es(cr_cv,2)+'%', wow_badge(cr_cv_wow), _b_cv, '#5C469C', first=True)}
      {_kpi_cell('Eficacia',  es(cr_ef,2)+'%', wow_badge(cr_ef_wow), _b_ef)}
      {_kpi_cell('Bookability', es(bk_val,1)+'%', wow_badge(bk_wow), _b_bk) if HAS_BK else ''}
    </div>
  </div>

  {_editorial_html}

  <!-- CTA -->
  <div class="m-cta">
    <p>Encontrá los findings completos por Hotel, Corporativo y Destinos. Descargá el Análisis de tu cluster: Destinos México, Destinos US, CALA, Cuentas Estratégicas y Global Accounts.<br>Resumen Ejecutivo y Plan de Acción en el Hub.</p>
    <div class="m-cta-btns">
      <a href="{URL_HUB}" style="display:inline-block;padding:8px 13px;font-size:9px;font-weight:700;letter-spacing:.04em;text-decoration:none;color:#ffffff;background-color:#161616;font-family:'Helvetica Neue',Arial,sans-serif;">→ Hub Supply Optimization</a>
      <a href="{URL_SUPPLY}" style="display:inline-block;padding:8px 13px;font-size:9px;font-weight:700;letter-spacing:.04em;text-decoration:none;color:#ffffff;background-color:#EA0074;font-family:'Helvetica Neue',Arial,sans-serif;">→ Disponibilidad &amp; Conectividades {WEEK}</a>
      <a href="{URL_INV}" style="display:inline-block;padding:8px 13px;font-size:9px;font-weight:700;letter-spacing:.04em;text-decoration:none;color:#161616;background-color:#4FC3F4;font-family:'Helvetica Neue',Arial,sans-serif;">→ Inventario {WEEK}</a>
    </div>
  </div>

  <!-- Footer -->
  <div class="m-ftr">
    <span class="m-ftr-txt">PriceTravel · Supply Optimization · <strong>{WEEK}</strong> · {PERIODO} · Vol. {VOL_NUM}</span>
  </div>

</div>
<!-- DRAFT_BODY_END -->

</body>
</html>'''

# ── Guardar ───────────────────────────────────────────────────────────────────
out = Path(OUT_FILE)
out.write_text(mail_html, encoding='utf-8')
print(f'Mail {WEEK} v5.0 → {out}')
print(f'Tamaño: {len(mail_html):,} chars')

# Copia en _email/week-NN/
_script_dir = Path(__file__).parent
_email_dir  = _script_dir / '_email' / f'week-{WEEK_NUM}'
_email_dir.mkdir(parents=True, exist_ok=True)
_email_dst  = _email_dir / f'Mail_{WEEK}.html'
_email_dst.write_text(mail_html, encoding='utf-8')
print(f'  → copia en _email/week-{WEEK_NUM}/ ✓')
