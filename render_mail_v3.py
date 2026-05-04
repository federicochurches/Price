"""
Mail W18 v3.1 · Estructura ejecutiva con catálogo de Áreas Accountable v2
Cambios vs v3:
- Reemplazo de áreas viejas por las 4 áreas accountable confirmadas:
  * Supply Optimization
  * Supply Optimization / TPS
  * Supply Comercial / Supply Optimization
  * Supply Comercial / Wholesale
- "W18" → "Week 18" / "W17" → "Week 17" en texto narrativo
"""
import pickle
from pathlib import Path

with open('rnd_w18_data.pkl','rb') as f:
    DR = pickle.load(f)
with open('cr_w18_data.pkl','rb') as f:
    DC = pickle.load(f)
with open('metrics_recalc.pkl','rb') as f:
    REC = pickle.load(f)

# === RND ===
mr_old = DR['M']['global_w18']
mr17_old = DR['M']['global_w17']

rnd_pct = mr_old['pct_nodispo']*100
rnd_pct_wow = (mr_old['pct_nodispo']-mr17_old['pct_nodispo'])*100

rnd_rpm_w18 = REC['m18']['rpm_reservas']
rnd_rpm_w17 = REC['m17']['rpm_reservas']
rnd_rpm_wow = (rnd_rpm_w18/rnd_rpm_w17-1)*100
rnd_gbm_w18 = REC['m18']['gbm_usd']
rnd_gbm_w17 = REC['m17']['gbm_usd']
rnd_gbm_wow = (rnd_gbm_w18/rnd_gbm_w17-1)*100

rnd_p80 = len(DR['p80_hotel'])
rnd_n_supc = int(DR['sev_nd'].get('Súper Crítica',0))
rnd_n_critmas = int(DR['sev_nd'].get('Crítica',0)+DR['sev_nd'].get('Súper Crítica',0))
rnd_n_sin_conv = int(DR['sev_rpm'].get('Sin Conversión',0))
rnd_pct_sin_conv = rnd_n_sin_conv/rnd_p80*100

cug18 = DR['M']['CUG (UOP)_w18']
cug17 = DR['M']['CUG (UOP)_w17']
cug_gbm_w18 = cug18['gb_usd']/cug18['trafico']*1_000_000
cug_gbm_w17 = cug17['gb_usd']/cug17['trafico']*1_000_000
cug_gbm_wow = (cug_gbm_w18/cug_gbm_w17-1)*100

# === CR ===
mc = DC['M']['global_w18']; mc17 = DC['M']['global_w17']
cr_ef = mc['eficacia']*100
cr_cv = mc['conv_rate']*100
cr_ef_wow = (mc['eficacia']-mc17['eficacia'])*100
cr_cv_wow = (mc['conv_rate']-mc17['conv_rate'])*100
cr_p80 = len(DC['p80_hotel'])
cr_n_supc = int(DC['sev_ef_p80'].get('Súper Crítica',0))
cr_n_critmas = int(DC['sev_ef_p80'].get('Crítica',0)+DC['sev_ef_p80'].get('Súper Crítica',0))
cr_n_sin_conv = int(DC['sev_cv_p80'].get('Sin Conversión',0))
cr_pct_sin_conv = cr_n_sin_conv/cr_p80*100
g_tp = DC['g_grupo'][DC['g_grupo']['Grupo']=='Third Party'].iloc[0]
g_pp = DC['g_grupo'][DC['g_grupo']['Grupo']=='Producto Propio'].iloc[0]

def es(x, decimals=2):
    if isinstance(x, float):
        s = f'{x:,.{decimals}f}'
        return s.replace(',','|').replace('.',',').replace('|','.')
    return f'{int(x):,}'.replace(',','.')

URL_BASE = 'https://analytics-desk.netlify.app'
URL_CR = f'{URL_BASE}/checkrates/week-18/CheckRates_Reporte_Editorial.html'
URL_RND = f'{URL_BASE}/rates-nodispo/week-18/RatesNoDispo_Reporte_Editorial.html'
URL_HUB = URL_BASE + '/'

mail_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Mail Supply Optimization Week 18 · v3.1</title>
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 24px; color: #161616; line-height: 1.55; background: #F8F4EC; }}
  .instructions {{ background: #FFF8E1; border-left: 4px solid #F2B90B; padding: 16px 20px; margin-bottom: 32px; font-size: 13px; border-radius: 4px; }}
  .instructions strong {{ color: #B07A00; }}
  .field-label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #8A8377; margin-bottom: 6px; margin-top: 16px; }}
  .field-box {{ background: #fff; border: 1px solid #C9C1B0; padding: 12px 16px; margin-bottom: 8px; font-size: 14px; }}
  .field-box.subject {{ font-size: 15px; font-weight: 600; }}
  hr.divider {{ border: none; border-top: 2px dashed #C9C1B0; margin: 32px 0; }}
  .copy-tip {{ font-size: 12px; color: #8A8377; margin-top: 8px; font-style: italic; }}
  
  /* Mail body */
  .mail-body {{ background: #fff; border: 1px solid #E5E0D2; padding: 36px 40px; font-size: 14px; line-height: 1.6; }}
  .mail-body h1 {{ font-size: 19px; font-weight: 700; letter-spacing: -0.01em; margin: 0 0 4px; color: #161616; }}
  .mail-body .subhead {{ font-size: 12px; color: #8A8377; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-bottom: 24px; }}
  .mail-body h2 {{ font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em; padding-bottom: 8px; margin: 28px 0 14px; color: #161616; border-bottom: 1px solid #C9C1B0; }}
  .mail-body p {{ margin: 12px 0; }}
  .mail-body strong {{ color: #161616; }}
  
  .hl-rnd {{ color: #EA0074; font-weight: 700; }}
  .hl-cr {{ color: #5C469C; font-weight: 700; }}
  .delta-down {{ color: #C0392B; font-weight: 700; }}
  .delta-up {{ color: #2E7D32; font-weight: 700; }}
  
  .cta-row {{ display: flex; gap: 10px; margin: 18px 0 4px; flex-wrap: wrap; }}
  .cta {{ display: inline-block; color: #fff !important; padding: 9px 16px; text-decoration: none !important; font-weight: 600; border-radius: 4px; font-size: 12px; letter-spacing: 0.02em; }}
  .cta-cr {{ background: #5C469C; }}
  .cta-rnd {{ background: #EA0074; }}
  .cta-hub {{ background: #161616; }}
  
  .exec-summary {{ background: #FAFAFA; border-left: 3px solid #161616; padding: 18px 22px; margin: 18px 0 24px; font-size: 14px; }}
  .exec-summary p {{ margin: 0 0 10px; }}
  .exec-summary p:last-child {{ margin-bottom: 0; }}
  
  .glossary-note {{ background: #EDE8F7; border-left: 3px solid #5C469C; padding: 14px 18px; margin: 14px 0 24px; font-size: 12.5px; color: #4A4A4A; }}
  .glossary-note strong {{ color: #5C469C; }}
  .credentials-box {{ background: #FFF8E1; border-left: 4px solid #F2B90B; padding: 14px 18px; margin: 18px 0 24px; font-size: 13px; }}
  .credentials-box strong {{ color: #B07A00; }}
  .credentials-box code {{ background: #fff; padding: 2px 8px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 13px; color: #161616; border: 1px solid #E5DCC0; }}
  
  /* Plan de Acción · agrupado por Área Accountable */
  .area-group {{ margin-bottom: 22px; }}
  .area-header {{ display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 2px solid #EAEAEA; flex-wrap: wrap; }}
  .area-name {{ font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em; color: #161616; background: #EAEAEA; padding: 4px 10px; border-radius: 3px; }}
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
  .src-cr {{ background: #EDE8F7; color: #5C469C; }}
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
  3. Pegá (Ctrl+V) en el body del compose de Gmail/Outlook. El formato (bold, links, badges) se mantiene.<br>
  4. Verificá las URLs y agregá los 12 destinatarios en CCO (ver destinatarios.md).
</div>

<div class="field-label">De (remitente)</div>
<div class="field-box">PriceTravel · Supply Optimization</div>

<div class="field-label">Asunto</div>
<div class="field-box subject">Supply Optimization · Week 18 · Resumen + Plan de Acción</div>

<div class="field-label">Preheader</div>
<div class="field-box">RND % de No Disponibilidad {es(rnd_pct,2)}% (Aceptable). CR Eficacia {es(cr_ef,2)}% · Conv Rate {es(cr_cv,2)}% (Revisar). Plan de Acción consolidado por Área Accountable.</div>

<hr class="divider">

<div class="field-label">Cuerpo del mail (copiar desde acá ↓)</div>
<p class="copy-tip">Click adentro del recuadro blanco · Ctrl+A · Ctrl+C · Ctrl+V en el compose.</p>

<div class="mail-body">
<!-- DRAFT_BODY_START -->

<h1>Supply Optimization · Week 18</h1>
<div class="subhead">27 Abr – 3 May 2026 · Vol. 04</div>

<p>Hola equipo,</p>

<p>Esta semana cambiamos el formato para enfocarlo en los accionables: <strong>Resumen Ejecutivo + Plan de Acción consolidado por Área Accountable</strong>. El detalle (Findings, Hoteles Específicos, Corporativos y Destinos, Análisis por Canasta, KPIs por dimensión) los encontrarán accediendo al Hub de Supply Optimization.</p>

<div class="credentials-box">
<strong>🔐 Acceso al Hub Supply Optimization</strong><br>
Usuario: <code>pricetravel</code> &nbsp;·&nbsp; Password: <code>supply2026</code>
</div>

<!-- ====================================================================== -->
<!-- GLOSARIO DE MÉTRICAS ACTUALIZADO                                          -->
<!-- ====================================================================== -->

<div class="glossary-note">
<strong>Cambio de glosario aplicado en este mail.</strong> Hasta Week 17 reportábamos "RPM" como GB / Tráfico × 1M (la métrica monetaria). Desde Week 18 separamos en dos métricas distintas:<br>
&nbsp;• <strong>RPM</strong> = <em>Reservas Por Millón</em> = Bookings / Tráfico × 1M (Week 18: <strong>{es(rnd_rpm_w18,2)}</strong>)<br>
&nbsp;• <strong>GBM</strong> = <em>Gross Booking por Millón</em> (USD) = GB / Tráfico × 1M (Week 18: <strong>${es(rnd_gbm_w18,2)}</strong>)<br>
Los deltas WoW se calculan contra Week 17 recalculado con la nueva definición. Los reportes Week 18 publicados conservan la nomenclatura original; la transición completa se aplica desde Week 19.
</div>

<!-- ====================================================================== -->
<!-- RESUMEN EJECUTIVO DE LA SEMANA                                            -->
<!-- ====================================================================== -->

<h2>📌 Resumen Ejecutivo de la Semana</h2>

<div class="exec-summary">
<p><strong>RND:</strong> <span class="hl-rnd">% de No Disponibilidad mejora a {es(rnd_pct,2)}%</span> (<span class="delta-up">▼ {es(abs(rnd_pct_wow),2)}pp WoW</span>) y entra en banda Aceptable, primera vez que se acerca al target &lt;3%. Pero <strong>RPM cae a {es(rnd_rpm_w18,2)} reservas/M</strong> (<span class="delta-down">{es(rnd_rpm_wow,1)}% WoW</span>) y <strong>GBM baja a ${es(rnd_gbm_w18,2)}/M</strong> (<span class="delta-down">{es(rnd_gbm_wow,1)}% WoW</span>) — la mejora en disponibilidad no se está traduciendo en GB.</p>

<p><strong>CR:</strong> Eficacia estable en <span class="hl-cr">{es(cr_ef,2)}%</span> (<span class="delta-up">+{es(cr_ef_wow,2)}pp</span>) pero <strong>Conv Rate baja a {es(cr_cv,2)}%</strong> (<span class="delta-down">{es(cr_cv_wow,2)}pp</span>) y queda en banda Revisar. El volumen de check-rates crece +6,3% pero los Bookings retroceden -2,2%.</p>

<p><strong>Foco de la semana:</strong> (1) <strong>Channel Third Party en banda Crítica</strong> (Conv Rate {es(g_tp["ConvRate"]*100,2)}% vs Producto Propio {es(g_pp["ConvRate"]*100,2)}%) — brecha sistémica que requiere auditoría. (2) <strong>Cohorte Sin Conversión estructural</strong>: {rnd_pct_sin_conv:.0f}% del P80 RND y {cr_pct_sin_conv:.0f}% del P80 CR sin Bookings — diagnóstico técnico/contractual, no de eficacia. (3) <strong>{rnd_n_supc + cr_n_supc} hoteles Súper Críticos</strong> entre ambos reportes para escalar esta semana.</p>
</div>

<!-- ====================================================================== -->
<!-- PLAN DE ACCIÓN CONSOLIDADO · POR ÁREA ACCOUNTABLE                       -->
<!-- ====================================================================== -->

<h2>🎯 Plan de Acción Consolidado · por Área Accountable</h2>

<p style="font-size: 12px; color: #8A8377; margin-bottom: 18px;">Acciones agrupadas por Área Accountable. Cada acción indica horizonte (<strong style="color:#2F6C34">QW</strong> Quick Win &lt;1 semana · <strong style="color:#A86A1D">MP</strong> Mid Priority 2-4 semanas · <strong style="color:#5C469C">ES</strong> Estratégica trimestre) y reporte de origen (<strong style="color:#EA0074">RND</strong> · <strong style="color:#5C469C">CR</strong>).</p>

<!-- SUPPLY OPTIMIZATION -->
<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Optimization</span>
    <span class="area-count">3 acciones</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-qw">QW</span>
    <div>
      <div class="action-text">Escalar <strong>{cr_n_supc} hoteles Súper Críticos de Eficacia</strong> en P80 (&lt;60%) — empezar por Las Vegas Hilton at Resorts World y Conrad LV.<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 5 días · Métrica: Eficacia &gt; 85%</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Plan de saneamiento para <strong>{es(cr_n_critmas)} hoteles Crítica/Súper Crítica</strong> de Eficacia (CR) · priorizar canastas <strong>CUG y B2B-OP</strong> (weight 0,6).<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 3 semanas · Métrica: 50% migrado a Revisar</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Plan de saneamiento para <strong>{es(rnd_n_critmas)} hoteles Crítica/Súper Crítica</strong> de % de No Disponibilidad (RND) · separar por canasta y trabajar primero CUG y B2B-OP.<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: 3 semanas · Métrica: 50% migrado a Revisar</div>
    </div>
  </div>
</div>

<!-- SUPPLY OPTIMIZATION / TPS -->
<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Optimization / TPS</span>
    <span class="area-count">3 acciones</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-qw">QW</span>
    <div>
      <div class="action-text">Diagnóstico técnico Top 10 <strong>Sin Conversión</strong> de alto tráfico (RND y CR) — revisar mapping, paridad, inventario, tarifas.<span class="src src-rnd">RND</span><span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 1 semana · Métrica: Bookings &gt; 0 · Universo: {es(rnd_n_sin_conv)} hoteles RND + {es(cr_n_sin_conv)} hoteles CR sin Bookings</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-qw">QW</span>
    <div>
      <div class="action-text">Escalar <strong>{rnd_n_supc} hoteles Súper Críticos de % de No Disponibilidad</strong> (&gt;60%) — primer foco de remediación técnica.<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: 5 días · Métrica: % de No Disponibilidad &lt; 20%</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Auditar canal <strong>Third Party</strong> (Conv Rate {es(g_tp["ConvRate"]*100,2)}% banda Crítica) — revisar paridad de tarifas y latencia con Expedia y HotelBeds Apitude.<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: 2 semanas · Métrica: Conv Rate &gt; 0,8%</div>
    </div>
  </div>
</div>

<!-- SUPPLY COMERCIAL / SUPPLY OPTIMIZATION -->
<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Comercial / Supply Optimization</span>
    <span class="area-count">1 acción</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-es">ES</span>
    <div>
      <div class="action-text">Reducir <strong>cohorte Sin Conversión</strong> en P80 — proyecto trimestral de remediación técnica + comercial coordinado entre RND y CR.<span class="src src-rnd">RND</span><span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: Q3 · Métrica: -25% a -30% vs baseline · Universo total: {es(rnd_n_sin_conv + cr_n_sin_conv)} hoteles</div>
    </div>
  </div>
</div>

<!-- SUPPLY COMERCIAL / WHOLESALE -->
<div class="area-group">
  <div class="area-header">
    <span class="area-name">Supply Comercial / Wholesale</span>
    <span class="area-count">3 acciones</span>
  </div>
  <div class="action-item">
    <span class="action-tag tag-mp">MP</span>
    <div>
      <div class="action-text">Revisión de <strong>RPM y GBM en CUG</strong> (canasta de mayor weight con caída pronunciada · GBM ${es(cug_gbm_w18,2)} vs ${es(cug_gbm_w17,2)} W17, deterioro {es(cug_gbm_wow,1)}% WoW).<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: 2 semanas · Métrica: GBM ≥ $650 (banda Aceptable)</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-es">ES</span>
    <div>
      <div class="action-text">Revisión integral del producto <strong>B2C</strong> (Conv Rate Crítica {es(DC["M"]["B2C_w18"]["conv_rate"]*100,2)}%) — pricing, UX, mapping, fee structure.<span class="src src-cr">CR</span></div>
      <div class="action-meta">Plazo: Q3 · Métrica: Conv Rate &gt; 1,5%</div>
    </div>
  </div>
  <div class="action-item">
    <span class="action-tag tag-es">ES</span>
    <div>
      <div class="action-text">Definir <strong>SLAs de % de No Disponibilidad por corporativo</strong> — Top 10 corp por tráfico con cláusulas de severity-based pricing.<span class="src src-rnd">RND</span></div>
      <div class="action-meta">Plazo: Q3 · Métrica: SLAs firmados con Top 10 corp</div>
    </div>
  </div>
</div>

<!-- ====================================================================== -->
<!-- LINKS A REPORTES                                                         -->
<!-- ====================================================================== -->

<h2>🔍 Detalle completo en el Hub</h2>

<div class="reports-row">
<p>El detalle completo (Findings, Hoteles Específicos, Corporativos y Destinos, Análisis por Canasta, KPIs por dimensión, Severity, Channel agrupado) está disponible en el Hub de Supply Optimization y los reportes editoriales. Excels Top 50 también disponibles para descarga.</p>
<div class="cta-row">
  <a href="{URL_HUB}" class="cta cta-hub">→ Hub Supply Optimization</a>
  <a href="{URL_CR}" class="cta cta-cr">→ Reporte CheckRates</a>
  <a href="{URL_RND}" class="cta cta-rnd">→ Reporte Rates No Dispo</a>
</div>
<p style="margin-top: 12px; font-size: 12px;">Excels Top 50 adjuntos · CR: 17 pestañas · RND: 13 pestañas</p>
</div>

<p style="margin-top: 24px;">Cualquier feedback sobre el nuevo formato del mail (más ejecutivo, foco en accionables) o sobre el cambio de glosario lo agradecemos — respondé este mismo hilo.</p>

<p style="margin-top: 12px;">Próxima publicación: <strong>lunes 12 de mayo (Week 19)</strong>.</p>

<div class="footer">
Recibís este mail porque sos parte del equipo de Supply Optimization. Cada lunes enviamos el deep-dive de la semana anterior.<br><br>
<strong>PriceTravel · Supply Optimization · Week 18 · 27 Abr – 3 May 2026 · Vol. 04</strong>
</div>

<!-- DRAFT_BODY_END -->
</div>

</body>
</html>
'''

out = Path('/mnt/user-data/outputs/Mail_W18.html')
out.write_text(mail_html, encoding='utf-8')
print(f'Mail Week 18 v3.1 con catálogo nuevo: {out}')
print(f'Tamaño: {len(mail_html):,} chars')
