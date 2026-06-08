"""
render_mail_v3.py · Mail semanal Supply Optimization
v4.0 · W23 · Rediseño visual completo
- Header oscuro con logo PriceTravel
- KPI cards grandes: Availability (RND) + Connectivities (CR)
- Sin saludo, sin alertas, sin plan de acción
- Un solo CTA → Connectivities & Hotel Availability
- Mención explícita de descarga Excel Top 500
Lee directamente de rnd_wNN_data.pkl y cr_wNN_data.pkl
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
from pathlib import Path

# ── CONFIG SEMANAL ────────────────────────────────────────────────────────────
# Lee desde env vars (run_pipeline.py) o fallback a hardcodeado
WEEK      = os.getenv('WEEK', 'W23')
PERIODO   = os.getenv('PERIODO', '2–8 jun 2026')
VOL_NUM   = os.getenv('VOL_NUM', '23')
PICKLE_RND = os.getenv('PICKLE_RND', f'rnd_w{VOL_NUM}_data.pkl')
PICKLE_CR  = os.getenv('PICKLE_CR',  f'cr_w{VOL_NUM}_data.pkl')

# Derivar número de semana
WEEK_NUM      = WEEK.replace('W','').zfill(2)
WEEK_NUM_INT  = int(VOL_NUM)
WEEK_PREV_INT = WEEK_NUM_INT - 1

# Output path
OUTPUTS_DIR = os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs')
OUT_FILE    = f'{OUTPUTS_DIR}/Mail_{WEEK}.html'

URL_BASE    = 'https://analytics-desk.netlify.app'
URL_REPORT  = f'{URL_BASE}/reports/week-{WEEK_NUM}/supply_w{WEEK_NUM}'
# ─────────────────────────────────────────────────────────────────────────────

with open(PICKLE_RND, 'rb') as f:
    DR = pickle.load(f)
with open(PICKLE_CR, 'rb') as f:
    DC = pickle.load(f)

# === RND (Availability) ===
mr18  = DR['M'][f'global_w{WEEK_NUM_INT}']
mr17  = DR['M'][f'global_w{WEEK_PREV_INT}']

rnd_pct     = mr18['pct_nodispo'] * 100
rnd_pct_wow = (mr18['pct_nodispo'] - mr17['pct_nodispo']) * 100

rnd_ipm_w18 = mr18['ipm']
rnd_ipm_w17 = mr17['ipm'] if mr17['ipm'] > 0 else 1
rnd_ipm_wow = (rnd_ipm_w18 / rnd_ipm_w17 - 1) * 100

rnd_p80        = len(DR['p80_hotel'])
rnd_n_supc     = int(DR['sev_nd'].get('Súper Crítica', 0))
rnd_n_critmas  = int(DR['sev_nd'].get('Crítica', 0) + DR['sev_nd'].get('Súper Crítica', 0))
rnd_n_sin_conv = int(DR['sev_rpm'].get('Sin Conversión', 0))

# Banda IPM para gauge
def _ipm_banda(ipm):
    if ipm >= 1500: return ('#1A6B4A', 90)
    if ipm >= 650:  return ('#1A6B4A', 60)
    if ipm >= 200:  return ('#F97316', 35)
    return ('#C0392B', 15)

def _ipm_label(ipm):
    if ipm >= 1500: return 'Exitosa'
    if ipm >= 650:  return 'Aceptable'
    if ipm >= 200:  return 'Revisar'
    return 'Crítica'

# Banda NoDispo para gauge
def _nd_banda(pct):
    if pct < 3:   return ('#1A6B4A', max(int(pct / 3 * 30), 5))
    if pct < 5:   return ('#FCD34D', 45)
    if pct < 20:  return ('#F97316', 65)
    if pct < 60:  return ('#C0392B', 80)
    return ('#991B1B', 95)

def _nd_label(pct):
    if pct < 3:  return 'Exitosa'
    if pct < 5:  return 'Aceptable'
    if pct < 20: return 'Revisar'
    if pct < 60: return 'Crítica'
    return 'Súper Crítica'

# === CR (Connectivities) ===
mc   = DC['M'][f'global_w{WEEK_NUM_INT}']
mc17 = DC['M'][f'global_w{WEEK_PREV_INT}']

cr_ef     = mc['eficacia'] * 100
cr_cv     = mc['conv_rate'] * 100
cr_ef_wow = (mc['eficacia'] - mc17['eficacia']) * 100
cr_cv_wow = (mc['conv_rate'] - mc17['conv_rate']) * 100
cr_p80    = len(DC['p80_hotel'])
cr_n_supc = int(DC['sev_ef_p80'].get('Súper Crítica', 0))

g_tp = DC['g_grupo'][DC['g_grupo']['Grupo'] == 'Third Party'].iloc[0]
g_pp = DC['g_grupo'][DC['g_grupo']['Grupo'] == 'Producto Propio'].iloc[0]

# Banda Eficacia para gauge
def _ef_banda(ef):
    if ef >= 97:   return ('#1A6B4A', 90)
    if ef >= 93:   return ('#FCD34D', 60)
    if ef >= 85:   return ('#F97316', 40)
    if ef >= 60:   return ('#C0392B', 25)
    return ('#991B1B', 10)

def _ef_label(ef):
    if ef >= 97:  return 'Exitosa'
    if ef >= 93:  return 'Aceptable'
    if ef >= 85:  return 'Revisar'
    if ef >= 60:  return 'Crítica'
    return 'Súper Crítica'

# Banda Conv Rate para gauge
def _cv_banda(cv):
    if cv >= 2.5:  return ('#1A6B4A', 90)
    if cv >= 1.5:  return ('#FCD34D', 65)
    if cv >= 0.8:  return ('#F97316', 40)
    return ('#C0392B', 20)

def _cv_label(cv):
    if cv >= 2.5:  return 'Exitosa'
    if cv >= 1.5:  return 'Aceptable'
    if cv >= 0.8:  return 'Revisar'
    return 'Crítica'

# ── Helpers formato español ───────────────────────────────────────────────────
def es(x, decimals=2):
    if isinstance(x, float):
        s = f'{x:,.{decimals}f}'
        return s.replace(',', '|').replace('.', ',').replace('|', '.')
    return f'{int(x):,}'.replace(',', '.')

def delta_cls(val, invert=False):
    """invert=True → positivo es malo (ej: NoDispo)"""
    if invert:
        return 'wow-down' if val > 0 else 'wow-up'
    return 'wow-up' if val >= 0 else 'wow-down'

def delta_arrow(val):
    return '▲' if val >= 0 else '▼'

def wow_str(val, decimals=2, suffix='pp', invert=False):
    """Devuelve HTML del span WoW con clase y flecha correctas."""
    cls = delta_cls(val, invert=invert)
    arrow = delta_arrow(val if not invert else -val)
    return f'<span class="kpi-wow {cls}">{arrow} {es(abs(val), decimals)}{suffix} WoW</span>'

# ── Logo PriceTravel (mismo PNG que build_package.py) ─────────────────────────
_LOGO_B64 = "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"

# Valores calculados para los gauges
nd_color, nd_pct_gauge = _nd_banda(rnd_pct)
nd_label = _nd_label(rnd_pct)
ipm_color, ipm_pct_gauge = _ipm_banda(rnd_ipm_w18)
ipm_label = _ipm_label(rnd_ipm_w18)
ef_color, ef_pct_gauge = _ef_banda(cr_ef)
ef_label = _ef_label(cr_ef)
cv_color, cv_pct_gauge = _cv_banda(cr_cv)
cv_label = _cv_label(cr_cv)

# ─────────────────────────────────────────────────────────────────────────────

mail_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Weekly KPIs Supply · {WEEK}</title>
<style>
  /* ── CHROME PREVISUALIZACIÓN ── */
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 24px; color: #161616; line-height: 1.55; background: #E8E2DA; }}
  .instructions {{ background: #FFF8E1; border-left: 4px solid #F2B90B; padding: 14px 18px; margin-bottom: 20px; font-size: 12px; line-height: 1.55; }}
  .instructions strong {{ color: #8A6300; }}
  .field-label {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; color: #8A8377; margin: 14px 0 5px; }}
  .field-box {{ background: #fff; border: 1px solid #C9C1B0; padding: 11px 15px; font-size: 14px; }}
  .field-box.subject {{ font-size: 15px; font-weight: 600; }}
  hr.divider {{ border: none; border-top: 2px dashed #C9C1B0; margin: 28px 0; }}
  .copy-tip {{ font-size: 11px; color: #8A8377; margin: 6px 0 16px; font-style: italic; }}

  /* ── MAIL ── */
  .mail-wrap {{ box-shadow: 0 4px 20px rgba(0,0,0,.12); }}

  .mail-header {{ background: #161616; padding: 20px 30px 18px; display: flex; align-items: center; justify-content: space-between; flex-wrap: nowrap; gap: 12px; }}
  .mail-logo {{ font-size: 17px; font-weight: 800; letter-spacing: -.02em; color: #fff; flex-shrink: 0; }}
  .mail-header-right {{ text-align: right; }}
  .mail-header-week {{ font-size: 10px; font-weight: 700; letter-spacing: .15em; text-transform: uppercase; color: #8A8377; }}
  .mail-header-period {{ font-size: 10px; color: #5A5550; margin-top: 2px; }}
  .accent-stripe {{ height: 3px; background: linear-gradient(90deg, #EA0074 0%, #5C469C 100%); }}

  .mail-body {{ background: #fff; padding: 30px 30px 26px; font-size: 14px; line-height: 1.6; color: #161616; }}
  .mail-lede {{ margin: 0 0 26px; font-size: 13px; color: #444; border-left: 3px solid #E0D9CF; padding-left: 14px; line-height: 1.6; }}

  .section-title {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .14em; color: #8A8377; margin: 0 0 12px; padding-bottom: 7px; border-bottom: 1px solid #E0D9CF; display: flex; align-items: center; gap: 7px; }}
  .dot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}
  .dot-rnd {{ background: #EA0074; }}
  .dot-cr  {{ background: #5C469C; }}

  .kpi-section {{ margin-bottom: 28px; }}
  .kpi-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  .kpi-card {{ border: 1px solid #E5E0D2; padding: 15px 17px; background: #FAFAF8; position: relative; overflow: hidden; }}
  .kpi-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; }}
  .kpi-card.rnd::before {{ background: #EA0074; }}
  .kpi-card.cr::before  {{ background: #5C469C; }}
  .kpi-label {{ font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; color: #8A8377; margin-bottom: 5px; }}
  .kpi-value {{ font-size: 26px; font-weight: 700; line-height: 1; letter-spacing: -.02em; color: #161616; margin-bottom: 5px; }}
  .kpi-value.rnd-color {{ color: #EA0074; }}
  .kpi-value.cr-color  {{ color: #5C469C; }}
  .kpi-wow {{ display: inline-flex; align-items: center; gap: 3px; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 2px; }}
  .wow-down {{ background: #FDE8E8; color: #C0392B; }}
  .wow-up   {{ background: #E2F5E9; color: #1A6B4A; }}
  .kpi-gauge {{ margin-top: 9px; height: 4px; background: #E8E2DA; border-radius: 2px; overflow: hidden; }}
  .kpi-gauge-fill {{ height: 100%; border-radius: 2px; }}
  .kpi-sub {{ margin-top: 5px; font-size: 11px; color: #8A8377; line-height: 1.4; }}

  .cta-section {{ background: #F5F1EB; border: 1px solid #E0D9CF; padding: 18px 20px; margin-top: 24px; }}
  .cta-section p {{ margin: 0 0 13px; font-size: 13px; color: #555; line-height: 1.55; }}
  .cta {{ display: inline-block; padding: 10px 18px; font-size: 11px; font-weight: 700; text-decoration: none; letter-spacing: .04em; color: #fff !important; background: #161616; }}

  .mail-footer {{ background: #F5F1EB; border-top: 1px solid #C9C1B0; padding: 14px 30px; font-size: 11px; color: #8A8377; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px; }}
  .mail-footer strong {{ color: #5A5550; }}

  @media (max-width: 480px) {{
    body {{ padding: 12px 8px 40px; }}
    .mail-header {{ padding: 14px 18px 12px; gap: 8px; }}
    .mail-logo {{ font-size: 15px; }}
    .mail-header-week {{ font-size: 9px; white-space: nowrap; }}
    .mail-header-period {{ font-size: 9px; white-space: nowrap; }}
    .mail-body {{ padding: 18px 16px 18px; }}
    .mail-lede {{ font-size: 13px; padding-left: 12px; margin-bottom: 20px; }}
    .section-title {{ font-size: 9px; margin-bottom: 10px; }}
    .kpi-grid {{ grid-template-columns: 1fr; gap: 8px; }}
    .kpi-card {{ padding: 13px 15px; }}
    .kpi-value {{ font-size: 24px; }}
    .kpi-sub {{ font-size: 11px; }}
    .kpi-section {{ margin-bottom: 20px; }}
    .cta-section {{ padding: 14px 15px; margin-top: 18px; }}
    .cta-section p {{ font-size: 12px; }}
    .cta {{ display: block; text-align: center; padding: 12px 16px; font-size: 12px; }}
    .mail-footer {{ padding: 11px 18px; flex-direction: column; gap: 2px; text-align: center; }}
  }}
</style>
</head>
<body>

<div class="instructions">
  <strong>Cómo enviar:</strong>
  Click adentro del área blanca · Ctrl+A · Ctrl+C · pegar en Gmail/Outlook. El formato se preserva.<br>
  Verificá la URL del botón y agregá destinatarios en CCO antes de enviar.
</div>

<div class="field-label">Asunto</div>
<div class="field-box subject">Weekly KPIs Supply · {WEEK} · Connectivities &amp; Hotel Availability</div>

<div class="field-label">Preheader</div>
<div class="field-box">Availability {es(rnd_pct,2)}% NoDispo · IPM ${es(rnd_ipm_w18,0)} · Connectivities Eficacia {es(cr_ef,2)}% · Conv Rate {es(cr_cv,2)}%</div>

<hr class="divider">

<div class="field-label">Cuerpo (copiar desde acá ↓)</div>
<p class="copy-tip">Click adentro del recuadro blanco · Ctrl+A · Ctrl+C · Ctrl+V en el compose.</p>

<!-- DRAFT_BODY_START -->
<div class="mail-wrap">

  <div class="mail-header">
    <div class="mail-logo">PriceTravel</div>
    <div class="mail-header-right">
      <div class="mail-header-week">Weekly KPIs {WEEK}</div>
      <div class="mail-header-period">{PERIODO} · Vol. {VOL_NUM}</div>
    </div>
  </div>
  <div class="accent-stripe"></div>

  <div class="mail-body">

    <p class="mail-lede">
      Resumen de KPIs Connectivities + Availability + Conv Rate {WEEK}.
      El detalle completo — incluyendo descarga del Excel con el Top 500 de hoteles — está disponible en el Hub de Supply Optimization.
    </p>

    <!-- Availability (RND) -->
    <div class="kpi-section">
      <div class="section-title">
        <span class="dot dot-rnd"></span>
        Availability · Métricas globales
      </div>
      <div class="kpi-grid">
        <div class="kpi-card rnd">
          <div class="kpi-label">% No Disponibilidad</div>
          <div class="kpi-value rnd-color">{es(rnd_pct,2)}%</div>
          {wow_str(rnd_pct_wow, invert=True)}
          <div class="kpi-gauge"><div class="kpi-gauge-fill" style="width:{nd_pct_gauge}%;background:{nd_color};"></div></div>
          <div class="kpi-sub">Banda {nd_label} · {rnd_n_supc} Súper Críticos · {rnd_n_critmas} Críticos o peor</div>
        </div>
        <div class="kpi-card rnd">
          <div class="kpi-label">IPM (USD / millón búsquedas)</div>
          <div class="kpi-value">${es(rnd_ipm_w18,0)}</div>
          {wow_str(rnd_ipm_wow, decimals=1, suffix='%', invert=False)}
          <div class="kpi-gauge"><div class="kpi-gauge-fill" style="width:{ipm_pct_gauge}%;background:{ipm_color};"></div></div>
          <div class="kpi-sub">Banda {ipm_label} · Target ≥ $650</div>
        </div>
      </div>
    </div>

    <!-- Connectivities (CR) -->
    <div class="kpi-section">
      <div class="section-title">
        <span class="dot dot-cr"></span>
        Connectivities · Métricas globales
      </div>
      <div class="kpi-grid">
        <div class="kpi-card cr">
          <div class="kpi-label">Eficacia</div>
          <div class="kpi-value cr-color">{es(cr_ef,2)}%</div>
          {wow_str(cr_ef_wow)}
          <div class="kpi-gauge"><div class="kpi-gauge-fill" style="width:{ef_pct_gauge}%;background:{ef_color};"></div></div>
          <div class="kpi-sub">Banda {ef_label} · {cr_n_supc} Súper Críticos · Target ≥ 97%</div>
        </div>
        <div class="kpi-card cr">
          <div class="kpi-label">Conv Rate</div>
          <div class="kpi-value">{es(cr_cv,2)}%</div>
          {wow_str(cr_cv_wow)}
          <div class="kpi-gauge"><div class="kpi-gauge-fill" style="width:{cv_pct_gauge}%;background:{cv_color};"></div></div>
          <div class="kpi-sub">Banda {cv_label} · TP: {es(g_tp["ConvRate"]*100,2)}% vs PP: {es(g_pp["ConvRate"]*100,2)}%</div>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="cta-section">
      <p>Findings completos, Hoteles, Corporativos, Destinos y Análisis por Canasta en el Hub.
      Desde el reporte podés descargar el <strong>Excel con el Top 500 de hoteles</strong> para cada métrica.</p>
      <a href="{URL_REPORT}" class="cta">→ Connectivities &amp; Hotel Availability {WEEK}</a>
    </div>

  </div>

  <div class="mail-footer">
    <span>PriceTravel · Supply Optimization · <strong>{WEEK}</strong> · {PERIODO}</span>
    <span>Vol. {VOL_NUM}</span>
  </div>

</div>
<!-- DRAFT_BODY_END -->

</body>
</html>
'''

out = Path(OUT_FILE)
out.write_text(mail_html, encoding='utf-8')
print(f'Mail {WEEK} v4.0: {out}')
print(f'Tamaño: {{len(mail_html):,}} chars')
