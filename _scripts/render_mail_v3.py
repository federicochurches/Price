"""
render_mail_v3.py · Mail semanal Supply Optimization
v3.2 · post W19 · sin dependencia de metrics_recalc.pkl
Lee directamente de rnd_wNN_data.pkl y cr_wNN_data.pkl
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
from pathlib import Path

# ── CONFIG SEMANAL ────────────────────────────────────────────────────────────
# Lee desde env vars (run_pipeline.py) o fallback a hardcodeado
WEEK      = os.getenv('WEEK', 'W20')
PERIODO   = os.getenv('PERIODO', '11–17 may 2026')
VOL_NUM   = os.getenv('VOL_NUM', '20')
PICKLE_RND = os.getenv('PICKLE_RND', f'rnd_w{VOL_NUM}_data.pkl')
PICKLE_CR  = os.getenv('PICKLE_CR', f'cr_w{VOL_NUM}_data.pkl')

# Derivar número de semana
WEEK_NUM  = WEEK.replace('W','').zfill(2)

# Output path
OUTPUTS_DIR = os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs')
OUT_FILE   = f'{OUTPUTS_DIR}/Mail_{WEEK}.html'

URL_BASE  = 'https://federicochurches.github.io/Price'
URL_CR    = f'{URL_BASE}/checkrates/week-{WEEK_NUM}/CheckRates_Reporte_Editorial.html'
URL_RND   = f'{URL_BASE}/rates-nodispo/week-{WEEK_NUM}/RatesNoDispo_Reporte_Editorial.html'
URL_HUB   = URL_BASE + '/'
# ─────────────────────────────────────────────────────────────────────────────

with open(PICKLE_RND, 'rb') as f:
    DR = pickle.load(f)
with open(PICKLE_CR, 'rb') as f:
    DC = pickle.load(f)

# === RND ===
mr18  = DR['M']['global_w20']
mr17  = DR['M']['global_w19']

rnd_pct     = mr18['pct_nodispo'] * 100
rnd_pct_wow = (mr18['pct_nodispo'] - mr17['pct_nodispo']) * 100

# IPM (Income Per Million) — derivado del pickle, no de metrics_recalc
rnd_ipm_w18 = mr18['ipm']
rnd_ipm_w17 = mr17['ipm'] if mr17['ipm'] > 0 else 1
rnd_ipm_wow = (rnd_ipm_w18 / rnd_ipm_w17 - 1) * 100

rnd_gbm_w18 = mr18['gb_usd']
rnd_gbm_w17 = mr17['gb_usd'] if mr17['gb_usd'] > 0 else 1
rnd_gbm_wow = (rnd_gbm_w18 / rnd_gbm_w17 - 1) * 100

rnd_p80        = len(DR['p80_hotel'])
rnd_n_supc     = int(DR['sev_nd'].get('Súper Crítica', 0))
rnd_n_critmas  = int(DR['sev_nd'].get('Crítica', 0) + DR['sev_nd'].get('Súper Crítica', 0))
rnd_n_sin_conv = int(DR['sev_rpm'].get('Sin Conversión', 0))
rnd_pct_sin_conv = rnd_n_sin_conv / rnd_p80 * 100

cug18       = DR['M']['CUG (UOP)_w20']
cug17       = DR['M']['CUG (UOP)_w19']
cug_ipm_w18 = cug18['gb_usd'] / cug18['trafico'] * 1_000_000 if cug18['trafico'] > 0 else 0
cug_ipm_w17 = cug17['gb_usd'] / cug17['trafico'] * 1_000_000 if cug17['trafico'] > 0 else 1
cug_ipm_wow = (cug_ipm_w18 / cug_ipm_w17 - 1) * 100

# === CR ===
mc   = DC['M']['global_w20']
mc17 = DC['M']['global_w19']

cr_ef       = mc['eficacia'] * 100
cr_cv       = mc['conv_rate'] * 100
cr_ef_wow   = (mc['eficacia'] - mc17['eficacia']) * 100
cr_cv_wow   = (mc['conv_rate'] - mc17['conv_rate']) * 100
cr_p80      = len(DC['p80_hotel'])
cr_n_supc   = int(DC['sev_ef_p80'].get('Súper Crítica', 0))
cr_n_critmas  = int(DC['sev_ef_p80'].get('Crítica', 0) + DC['sev_ef_p80'].get('Súper Crítica', 0))
cr_n_sin_conv = int(DC['sev_cv_p80'].get('Sin Conversión', 0))
cr_pct_sin_conv = cr_n_sin_conv / cr_p80 * 100

g_tp = DC['g_grupo'][DC['g_grupo']['Grupo'] == 'Third Party'].iloc[0]
g_pp = DC['g_grupo'][DC['g_grupo']['Grupo'] == 'Producto Propio'].iloc[0]

b2c_cv = DC['M']['B2C_w20']['conv_rate'] * 100

# ── Helper formato español ────────────────────────────────────────────────────
def es(x, decimals=2):
    if isinstance(x, float):
        s = f'{x:,.{decimals}f}'
        return s.replace(',', '|').replace('.', ',').replace('|', '.')
    return f'{int(x):,}'.replace(',', '.')

# ── Delta helpers ─────────────────────────────────────────────────────────────
def delta_cls(val, invert=False):
    """invert=True → positivo es malo (ej: NoDispo)"""
    if invert:
        return 'delta-down' if val > 0 else 'delta-up'
    return 'delta-up' if val >= 0 else 'delta-down'

def delta_arrow(val):
    return '▲' if val >= 0 else '▼'

# ─────────────────────────────────────────────────────────────────────────────

mail_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Mail Supply Optimization {WEEK} · v3.2</title>
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 24px; color: #161616; line-height: 1.55; background: #F8F4EC; }}
  .instructions {{ background: #FFF8E1; border-left: 4px solid #F2B90B; padding: 16px 20px; margin-bottom: 32px; font-size: 13px; border-radius: 4px; }}
  .instructions strong {{ color: #B07A00; }}
  .field-label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #8A8377; margin-bottom: 6px; margin-top: 16px; }}
  .field-box {{ background: #fff; border: 1px solid #C9C1B0; padding: 12px 16px; margin-bottom: 8px; font-size: 14px; }}
  .field-box.subject {{ font-size: 15px; font-weight: 600; }}
  hr.divider {{ border: none; border-top: 2px dashed #C9C1B0; margin: 32px 0; }}
  .copy-tip {{ font-size: 12px; color: #8A8377; margin-top: 8px; font-style: italic; }}

  .mail-body {{ background: #fff; border: 1px solid #E5E0D2; padding: 36px 40px; font-size: 14px; line-height: 1.6; }}
  .mail-body h1 {{ font-size: 19px; font-weight: 700; letter-spacing: -0.01em; margin: 0 0 4px; color: #161616; }}
  .mail-body .subhead {{ font-size: 12px; color: #8A8377; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-bottom: 24px; }}
  .mail-body h2 {{ font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em; padding-bottom: 8px; margin: 28px 0 14px; color: #161616; border-bottom: 1px solid #C9C1B0; }}
  .mail-body p {{ margin: 12px 0; }}
  .mail-body strong {{ color: #161616; }}

  .hl-rnd {{ color: #EA0074; font-weight: 700; }}
  .hl-cr  {{ color: #5C469C; font-weight: 700; }}
  .delta-down {{ color: #C0392B; font-weight: 700; }}
  .delta-up   {{ color: #2E7D32; font-weight: 700; }}

  .cta-row {{ display: flex; gap: 10px; margin: 18px 0 4px; flex-wrap: wrap; }}
  .cta {{ display: inline-block; color: #fff !important; padding: 9px 16px; text-decoration: none !important; font-weight: 600; border-radius: 4px; font-size: 12px; letter-spacing: 0.02em; }}
  .cta-cr  {{ background: #5C469C; }}
  .cta-rnd {{ background: #EA0074; }}
  .cta-hub {{ background: #161616; }}

  .exec-summary {{ background: #FAFAFA; border-left: 3px solid #161616; padding: 18px 22px; margin: 18px 0 24px; font-size: 14px; }}
  .exec-summary p {{ margin: 0 0 10px; }}
  .exec-summary p:last-child {{ margin-bottom: 0; }}

  .area-group {{ margin-bottom: 22px; }}
  .area-header {{ display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 2px solid #EAEAEA; flex-wrap: wrap; }}
  .area-name  {{ font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em; color: #161616; background: #EAEAEA; padding: 4px 10px; border-radius: 3px; }}
  .area-count {{ font-size: 11px; color: #8A8377; font-weight: 600; }}

  .action-item {{ display: grid; grid-template-columns: 60px 1fr; gap: 14px; padding: 10px 0; border-bottom: 1px solid #F0EBDF; align-items: start; }}
  .action-item:last-child {{ border-bottom: none; }}
  .action-tag {{ font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 6px; border-radius: 2px; text-align: center; line-height: 1.3; }}
  .tag-qw {{ background: #E0F0E2; color: #2F6C34; }}
  .tag-mp {{ background: #FFF4E0; color: #A86A1D; }}
  .tag-es {{ background: #EDE8F7; color: #5C469C; }}
  .action-text {{ font-size: 13px; line-height: 1.5; }}
  .action-text .src {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 1px 5px; border-radius: 2px; margin-left: 6px; vertical-align: middle; }}
  .src-rnd {{ background: #FCE4F1; color: #EA0074; }}
  .src-cr  {{ background: #EDE8F7; color: #5C469C; }}
  .action-meta {{ font-size: 11px; color: #8A8377; margin-top: 3px; }}

  .reports-row {{ background: #FAFAFA; border: 1px solid #EDE8E0; border-radius: 6px; padding: 18px 22px; margin: 24px 0 12px; }}
  .reports-row p {{ margin: 0 0 10px; font-size: 13px; color: #8A8377; }}

  .footer {{ border-top: 1px solid #C9C1B0; padding-top: 18px; margin-top: 32px; font-size: 12px; color: #8A8377; line-height: 1.5; }}
</style>
</head>
<body>

<div class="instructions">
  <strong>Cómo enviar este mail:</strong><br>
  1. Copiá el "Asunto" y pegalo en el campo asunto del compose.<br>
  2. Hacé click adentro del área blanca, seleccioná todo (Ctrl+A) y copiá (Ctrl+C).<br>
  3. Pegá (Ctrl+V) en el body del compose de Gmail/Outlook. El formato se mantiene.<br>
  4. Verificá las URLs y agregá los destinatarios en CCO (ver destinatarios.md).
</div>

<div class="field-label">Asunto</div>
<div class="field-box subject">Supply Optimization · {WEEK} · Resumen + Plan de Acción</div>

<div class="field-label">Preheader</div>
<div class="field-box">RND % de No Disponibilidad {es(rnd_pct,2)}%. CR Eficacia {es(cr_ef,2)}% · Conv Rate {es(cr_cv,2)}%. Plan de Acción consolidado por Área Accountable.</div>

<hr class="divider">

<div class="field-label">Cuerpo del mail (copiar desde acá ↓)</div>
<p class="copy-tip">Click adentro del recuadro blanco · Ctrl+A · Ctrl+C · Ctrl+V en el compose.</p>

<!-- DRAFT_BODY_START -->
<div class="mail-body">

<h1>Supply Optimization · {WEEK}</h1>
<div class="subhead">{PERIODO} · Vol. {VOL_NUM}</div>

<p>Hola equipo,</p>

<p>Resumen ejecutivo + Plan de Acción de la semana. El detalle completo (Findings, Hoteles, Corporativos, Destinos, Análisis por Canasta) está en el Hub.</p>

<h2>📌 Resumen Ejecutivo</h2>

<div class="exec-summary">
<p><strong>RND:</strong> <span class="hl-rnd">% de No Disponibilidad {es(rnd_pct,2)}%</span>
  (<span class="{delta_cls(rnd_pct_wow, invert=True)}">{delta_arrow(-rnd_pct_wow)} {es(abs(rnd_pct_wow),2)}pp WoW</span>).
  IPM {es(rnd_ipm_w18,0)} USD/M
  (<span class="{delta_cls(rnd_ipm_wow)}">{delta_arrow(rnd_ipm_wow)} {es(abs(rnd_ipm_wow),1)}% WoW</span>).
  <strong>{rnd_n_supc} hoteles Súper Críticos</strong> · {rnd_n_critmas} en Crítica o peor ·
  {rnd_pct_sin_conv:.0f}% del P80 sin Bookings.</p>

<p><strong>CR:</strong> Eficacia <span class="hl-cr">{es(cr_ef,2)}%</span>
  (<span class="{delta_cls(cr_ef_wow)}">+{es(cr_ef_wow,2)}pp</span>).
  Conv Rate <strong>{es(cr_cv,2)}%</strong>
  (<span class="{delta_cls(cr_cv_wow)}">{es(cr_cv_wow,2)}pp</span>) — banda Revisar.
  <strong>{cr_n_supc} hoteles Súper Críticos</strong> eficacia ·
  Third Party Conv Rate {es(g_tp["ConvRate"]*100,2)}% vs Producto Propio {es(g_pp["ConvRate"]*100,2)}%.</p>

<p><strong>Prioridades:</strong> {rnd_n_supc + cr_n_supc} hoteles Súper Críticos entre ambos reportes ·
  brecha Third Party sistémica ·
  cohorte Sin Conversión ({es(rnd_n_sin_conv)} RND + {es(cr_n_sin_conv)} CR).</p>
</div>

<h2>🎯 Plan de Acción · por Área Accountable</h2>

<p style="font-size: 12px; color: #8A8377; margin-bottom: 18px;">
  <strong style="color:#2F6C34">QW</strong> Quick Win &lt;1 semana ·
  <strong style="color:#A86A1D">MP</strong> Mid Priority 2-4 semanas ·
  <strong style="color:#5C469C">ES</strong> Estratégica trimestre
</p>

<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Optimization</span>
    <span class="area-count">3 acciones</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-qw">QW</span>
    <div>
      <div class="action-text">Escalar <strong>{cr_n_supc} hoteles Súper Críticos de Eficacia</strong> (&lt;60%) — revisión técnica de conectividad y errores.<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 5 días · Métrica: Eficacia &gt; 85%</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Plan de saneamiento <strong>{es(cr_n_critmas)} hoteles Crítica/Súper Crítica</strong> de Eficacia · priorizar CUG y B2B-OP (weight 0,6).<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 3 semanas · Métrica: 50% migrado a Revisar</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Plan de saneamiento <strong>{es(rnd_n_critmas)} hoteles Crítica/Súper Crítica</strong> de % NoDispo · CUG y B2B-OP primero.<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: 3 semanas · Métrica: 50% migrado a Revisar</div>
    </div>
  </div>
</div>

<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Optimization / TPS</span>
    <span class="area-count">3 acciones</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-qw">QW</span>
    <div>
      <div class="action-text">Diagnóstico técnico Top 10 <strong>Sin Conversión</strong> de alto tráfico — mapping, paridad, inventario, tarifas.<span class="src src-rnd">RND</span><span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 1 semana · Universo: {es(rnd_n_sin_conv)} RND + {es(cr_n_sin_conv)} CR sin Bookings</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-qw">QW</span>
    <div>
      <div class="action-text">Escalar <strong>{rnd_n_supc} hoteles Súper Críticos de % NoDispo</strong> (&gt;60%) — remediación técnica urgente.<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: 5 días · Métrica: % NoDispo &lt; 20%</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Auditar canal <strong>Third Party</strong> (Conv Rate {es(g_tp["ConvRate"]*100,2)}% banda Crítica) — paridad tarifas y latencia con Expedia y HotelBeds.<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 2 semanas · Métrica: Conv Rate &gt; 0,8%</div>
    </div>
  </div>
</div>

<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Comercial / Supply Optimization</span>
    <span class="area-count">1 acción</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-es">ES</span>
    <div>
      <div class="action-text">Reducir <strong>cohorte Sin Conversión en P80</strong> — proyecto trimestral de remediación técnica + comercial coordinado RND y CR.<span class="src src-rnd">RND</span><span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: Q3 · Métrica: -25% vs baseline · Universo: {es(rnd_n_sin_conv + cr_n_sin_conv)} hoteles</div>
    </div>
  </div>
</div>

<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Comercial / Wholesale</span>
    <span class="area-count">3 acciones</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Revisión de <strong>IPM en CUG</strong> (mayor weight · IPM ${es(cug_ipm_w18,0)} vs ${es(cug_ipm_w17,0)} semana anterior · {es(cug_ipm_wow,1)}% WoW).<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: 2 semanas · Métrica: IPM ≥ $650 (banda Aceptable)</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-es">ES</span>
    <div>
      <div class="action-text">Revisión integral del producto <strong>B2C</strong> (Conv Rate Crítica {es(b2c_cv,2)}%) — pricing, UX, mapping, fee structure.<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: Q3 · Métrica: Conv Rate &gt; 1,5%</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-es">ES</span>
    <div>
      <div class="action-text">Definir <strong>SLAs de % NoDispo por corporativo</strong> — Top 10 corp por tráfico con cláusulas de severity-based pricing.<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: Q3 · Métrica: SLAs firmados con Top 10 corp</div>
    </div>
  </div>
</div>

<h2>🔍 Detalle en el Hub</h2>

<div class="reports-row">
<p>Findings completos, Hoteles, Corporativos, Destinos, Análisis por Canasta, KPIs por dimensión, Severity y Channel en el Hub. Excels Top 50 disponibles para descarga en cada reporte.</p>
<div class="cta-row">
  <a href="{URL_HUB}" class="cta cta-hub">→ Hub Supply Optimization</a>
  <a href="{URL_CR}" class="cta cta-cr">→ Reporte CheckRates</a>
  <a href="{URL_RND}" class="cta cta-rnd">→ Reporte Rates No Dispo</a>
</div>
<p style="margin-top: 12px; font-size: 12px;">Hub con login: analytics-desk.netlify.app · usuario: pricetravel · clave: supply2026</p>
</div>

<div class="footer">
Recibís este mail porque sos parte del equipo de Supply Optimization. Cada lunes publicamos el análisis de la semana anterior.<br><br>
<strong>PriceTravel · Supply Optimization · {WEEK} · {PERIODO} · Vol. {VOL_NUM}</strong>
</div>

</div>
<!-- DRAFT_BODY_END -->

</body>
</html>
'''

out = Path(OUT_FILE)
out.write_text(mail_html, encoding='utf-8')
print(f'Mail {WEEK} v3.2: {out}')
print(f'Tamaño: {len(mail_html):,} chars')
