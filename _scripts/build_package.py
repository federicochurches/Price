"""
build_package.py · Paso 6 del pipeline semanal
Genera index.html del hub + ZIP con estructura completa del repo

Uso:
    python build_package.py

CONFIG SEMANAL — solo cambiar esto cada semana:
"""
import pickle, zipfile, shutil
from pathlib import Path

# ── CONFIG SEMANAL ────────────────────────────────────────────────────────────
WEEK        = 19          # número entero
PERIODO     = '5–11 may 2026'
FECHA_PUB   = 'Lunes 12 mayo 2026'

# Semana anterior (para historial en el hub)
WEEK_PREV        = 18
PERIODO_PREV     = '27 abr – 3 may 2026'

# Pickles (generados por calc_*.py)
PICKLE_RND  = 'rnd_w19_data.pkl'
PICKLE_CR   = 'cr_w19_data.pkl'

# Outputs del pipeline (generados por assemble_*.py y excel_*.py)
OUTPUTS     = Path('/mnt/user-data/outputs')
# ─────────────────────────────────────────────────────────────────────────────

WEEK_STR      = f'week-{WEEK}'
WEEK_PREV_STR = f'week-{WEEK_PREV}'
WEEK_LABEL    = f'W{WEEK}'

# ── Cargar KPIs desde pickles ─────────────────────────────────────────────────
with open(PICKLE_RND, 'rb') as f:
    DR = pickle.load(f)
with open(PICKLE_CR, 'rb') as f:
    DC = pickle.load(f)

mr   = DR['M']['global_w18']   # W actual
mr17 = DR['M']['global_w17']   # W anterior
mc   = DC['M']['global_w18']
mc17 = DC['M']['global_w17']

# RND
rnd_pct     = mr['pct_nodispo'] * 100
rnd_pct_wow = (mr['pct_nodispo'] - mr17['pct_nodispo']) * 100
rnd_ipm     = mr['ipm']
rnd_ipm_wow = (rnd_ipm / mr17['ipm'] - 1) * 100 if mr17['ipm'] > 0 else 0
rnd_band_nd  = mr['banda_nd']
rnd_band_ipm = mr['banda_rpm']   # variable interna sigue siendo rpm

sev_nd  = DR['sev_nd']
rnd_supc   = int(sev_nd.get('Súper Crítica', 0))
rnd_crit   = int(sev_nd.get('Crítica', 0))
rnd_rev    = int(sev_nd.get('Revisar', 0))
rnd_acep   = int(sev_nd.get('Aceptable', 0))
rnd_exit   = int(sev_nd.get('Exitosa', 0))

# CR
cr_ef      = mc['eficacia'] * 100
cr_ef_wow  = (mc['eficacia'] - mc17['eficacia']) * 100
cr_cv      = mc['conv_rate'] * 100
cr_cv_wow  = (mc['conv_rate'] - mc17['conv_rate']) * 100

sev_ef = DC['sev_ef_p80']
cr_supc  = int(sev_ef.get('Súper Crítica', 0))
cr_crit  = int(sev_ef.get('Crítica', 0))
cr_rev   = int(sev_ef.get('Revisar', 0))
cr_acep  = int(sev_ef.get('Aceptable', 0))
cr_exit  = int(sev_ef.get('Exitosa', 0))

# Prev week (from pickles — mismos datos como W17 del siguiente ciclo)
rnd_pct_prev = mr17['pct_nodispo'] * 100
rnd_ipm_prev = mr17['ipm']
cr_ef_prev   = mc17['eficacia'] * 100
cr_cv_prev   = mc17['conv_rate'] * 100

# ── Helpers ───────────────────────────────────────────────────────────────────
def es(x, d=2):
    s = f'{x:,.{d}f}'
    return s.replace(',', '|').replace('.', ',').replace('|', '.')

def wow_cls(val, invert=False):
    if invert:
        return 'wow-up' if val < 0 else ('wow-flat' if val == 0 else 'wow-down')
    return 'wow-up' if val > 0 else ('wow-flat' if val == 0 else 'wow-down')

def wow_arrow(val, invert=False):
    effective = -val if invert else val
    return '▲' if effective > 0 else ('▼' if effective < 0 else '—')

def band_css(band):
    m = {
        'Exitosa': 'band-exitosa',
        'Aceptable': 'band-aceptable',
        'Revisar': 'band-revisar',
        'Crítica': 'band-critica',
        'Súper Crítica': 'band-superc',
    }
    return m.get(band, 'band-revisar')


# ── Generar index.html ────────────────────────────────────────────────────────
def build_index():
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Supply Analytics Hub · PriceTravel</title>
<style>
  :root {{
    --ink:#161616; --ink-soft:#4A4540; --ink-muted:#8A8377;
    --paper:#FAF7F2; --paper-soft:#F2EDE0;
    --rule:#C9C1B0; --rule-soft:#E5E0D2;
    --magenta:#EA0074; --violet:#5C469C; --cyan:#4FC3F4;
    --amber:#A86A1D; --green:#2F6C34; --red:#C0392B;
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Helvetica Neue',Arial,sans-serif;background:var(--paper);color:var(--ink);line-height:1.5;min-height:100vh;}}

  /* ── Login ── */
  #login-overlay{{position:fixed;inset:0;z-index:9999;background:#161616;display:flex;align-items:center;justify-content:center;}}
  .login-box{{background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:40px 48px;width:360px;text-align:center;}}
  .login-logo{{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:24px;}}
  .login-box h2{{font-size:20px;font-weight:700;margin-bottom:6px;}}
  .login-box p{{font-size:13px;color:var(--ink-muted);margin-bottom:28px;}}
  .login-box input{{width:100%;padding:10px 14px;margin-bottom:12px;border:1px solid var(--rule);border-radius:4px;font-size:14px;background:#fff;color:var(--ink);}}
  .login-box input:focus{{outline:2px solid var(--violet);border-color:var(--violet);}}
  .login-box button{{width:100%;padding:11px;background:var(--ink);color:#fff;border:none;border-radius:4px;font-size:13px;font-weight:700;letter-spacing:.04em;cursor:pointer;margin-top:4px;transition:background .15s;}}
  .login-box button:hover{{background:#2a2a2a;}}
  .login-error{{font-size:12px;color:var(--red);margin-top:10px;display:none;}}

  /* ── Layout ── */
  .hub-wrap{{max-width:960px;margin:0 auto;padding:0 32px 80px;}}

  /* ── Header ── */
  .hub-header{{padding:40px 0 32px;border-bottom:1px solid var(--rule);margin-bottom:48px;display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap;}}
  .hub-kicker{{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:8px;}}
  .hub-title{{font-size:28px;font-weight:800;letter-spacing:-.02em;line-height:1.1;}}
  .hub-sub{{font-size:13px;color:var(--ink-muted);margin-top:6px;}}
  .hub-header-right{{font-size:12px;color:var(--ink-muted);text-align:right;line-height:1.7;}}
  .hub-header-right strong{{color:var(--ink);}}

  /* ── Section label ── */
  .section-label{{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid var(--rule-soft);}}

  /* ── Featured card ── */
  .featured-card{{background:#fff;border:1px solid var(--rule);border-top:4px solid var(--ink);border-radius:6px;padding:32px 36px;margin-bottom:48px;cursor:pointer;transition:box-shadow .15s,border-color .15s;}}
  .featured-card:hover{{box-shadow:0 4px 16px rgba(0,0,0,.08);border-color:var(--ink-soft);}}
  .featured-top{{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;flex-wrap:wrap;margin-bottom:28px;}}
  .featured-week{{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:4px;}}
  .featured-title{{font-size:22px;font-weight:800;letter-spacing:-.02em;color:var(--ink);line-height:1.2;}}
  .featured-period{{font-size:12px;color:var(--ink-muted);margin-top:4px;}}
  .featured-badge{{display:inline-block;padding:4px 12px;font-size:10px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;border-radius:20px;background:var(--ink);color:#fff;white-space:nowrap;align-self:flex-start;}}

  /* ── KPI strip ── */
  .kpi-strip{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--rule-soft);border:1px solid var(--rule-soft);border-radius:4px;overflow:hidden;margin-bottom:28px;}}
  .kpi-cell{{background:var(--paper-soft);padding:14px 16px;}}
  .kpi-label{{font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px;}}
  .kpi-value{{font-size:20px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums;line-height:1.1;}}
  .kpi-wow{{font-size:11px;font-weight:600;margin-top:3px;}}
  .kpi-band{{font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-top:4px;padding:2px 7px;border-radius:2px;display:inline-block;}}

  .color-rnd{{color:var(--magenta);}} .color-cr{{color:var(--violet);}}
  .color-ipm{{color:var(--amber);}}  .color-cv{{color:var(--violet);}}
  .band-exitosa{{background:rgba(79,195,244,.15);color:#0B7CA8;}}
  .band-aceptable{{background:rgba(92,70,156,.15);color:var(--violet);}}
  .band-revisar{{background:rgba(168,106,29,.15);color:var(--amber);}}
  .band-critica{{background:rgba(192,57,43,.15);color:var(--red);}}
  .band-superc{{background:rgba(22,22,22,.15);color:var(--ink);}}
  .wow-up{{color:var(--green);}} .wow-down{{color:var(--red);}} .wow-flat{{color:var(--ink-muted);}}

  /* ── Severity pills ── */
  .sev-group{{margin-bottom:24px;}}
  .sev-group-label{{font-size:9px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:8px;}}
  .sev-strip{{display:flex;gap:6px;flex-wrap:wrap;}}
  .sev-pill{{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:4px 10px;border-radius:3px;display:flex;align-items:center;gap:5px;}}
  .sev-pill .sev-n{{font-size:13px;font-weight:800;font-variant-numeric:tabular-nums;}}
  .sev-label{{font-size:9px;letter-spacing:.08em;}}
  .sev-groups-row{{display:flex;gap:32px;flex-wrap:wrap;margin-bottom:24px;}}

  /* ── Report links ── */
  .report-links{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;}}
  .report-btn{{display:inline-flex;align-items:center;gap:6px;padding:9px 16px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;transition:opacity .15s;cursor:pointer;}}
  .report-btn:hover{{opacity:.85;}}
  .btn-cr{{background:var(--violet);color:#fff;}} .btn-rnd{{background:var(--magenta);color:#fff;}}
  .report-btn-ghost{{display:inline-flex;align-items:center;gap:6px;padding:9px 16px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;border:1px solid var(--rule);color:var(--ink-soft);transition:border-color .15s,color .15s;cursor:pointer;}}
  .report-btn-ghost:hover{{border-color:var(--ink);color:var(--ink);}}

  /* ── History grid ── */
  .history-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}}
  @media(max-width:600px){{.history-grid{{grid-template-columns:1fr;}}}}
  .history-card{{background:#fff;border:1px solid var(--rule-soft);border-radius:6px;padding:20px 22px;cursor:pointer;transition:box-shadow .15s,border-color .15s;}}
  .history-card:hover{{box-shadow:0 2px 10px rgba(0,0,0,.06);border-color:var(--rule);}}
  .hcard-week{{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:4px;}}
  .hcard-period{{font-size:12px;color:var(--ink-muted);margin-bottom:14px;}}
  .hcard-kpis{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;}}
  .hcard-kpi{{display:flex;flex-direction:column;gap:2px;}}
  .hcard-kpi-label{{font-size:9px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;}}
  .hcard-kpi-value{{font-size:16px;font-weight:700;letter-spacing:-.01em;font-variant-numeric:tabular-nums;}}
  .hcard-links{{display:flex;gap:8px;flex-wrap:wrap;}}
  .hcard-link{{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;padding:5px 10px;border-radius:3px;transition:opacity .15s;}}
  .hcard-link:hover{{opacity:.8;}}
  .hlink-cr{{background:rgba(92,70,156,.12);color:var(--violet);}}
  .hlink-rnd{{background:rgba(234,0,116,.10);color:var(--magenta);}}

  /* ── Footer ── */
  .hub-footer{{margin-top:64px;padding-top:20px;border-top:1px solid var(--rule-soft);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}}
  .hub-footer-left{{font-size:11px;color:var(--ink-muted);line-height:1.6;}}
  .hub-footer-right{{font-size:11px;color:var(--ink-muted);}}
</style>
</head>
<body>

<!-- ── Login overlay ── -->
<div id="login-overlay">
  <div class="login-box">
    <div class="login-logo">PriceTravel · Supply Analytics</div>
    <h2>Acceso al Hub</h2>
    <p>Reportes semanales de Supply Optimization</p>
    <input type="text" id="login-user" placeholder="Usuario" autocomplete="username">
    <input type="password" id="login-pass" placeholder="Contraseña" autocomplete="current-password">
    <button onclick="doLogin()">Ingresar →</button>
    <div class="login-error" id="login-error">Usuario o contraseña incorrectos.</div>
  </div>
</div>

<!-- ── Hub content ── -->
<div class="hub-wrap" id="hub-content" style="display:none;">

  <header class="hub-header">
    <div>
      <div class="hub-kicker">PriceTravel · Supply Optimization</div>
      <div class="hub-title">Supply Analytics Hub</div>
      <div class="hub-sub">Rates No Dispo · CheckRates · Semana actual: <strong>Week {WEEK}</strong></div>
    </div>
    <div class="hub-header-right">
      <strong>Última publicación</strong><br>
      Week {WEEK} · {PERIODO}<br>
      {FECHA_PUB}
    </div>
  </header>

  <!-- ── Featured: W{WEEK} ── -->
  <div class="section-label">Semana actual</div>

  <div class="featured-card" onclick="window.location='checkrates/{WEEK_STR}/CheckRates_Reporte_Editorial.html'">

    <div class="featured-top">
      <div>
        <div class="featured-week">Week {WEEK}</div>
        <div class="featured-title">Supply Optimization · {PERIODO}</div>
        <div class="featured-period">Análisis semanal · Rates No Dispo + CheckRates · P80 global</div>
      </div>
      <span class="featured-badge">Publicado</span>
    </div>

    <div class="kpi-strip">
      <div class="kpi-cell">
        <div class="kpi-label color-rnd">% No Dispo</div>
        <div class="kpi-value color-rnd">{es(rnd_pct)}%</div>
        <div class="kpi-wow {wow_cls(rnd_pct_wow, invert=True)}">{wow_arrow(rnd_pct_wow, invert=True)} {es(abs(rnd_pct_wow))}pp WoW</div>
        <span class="kpi-band {band_css(rnd_band_nd)}">{rnd_band_nd}</span>
      </div>
      <div class="kpi-cell">
        <div class="kpi-label color-ipm">IPM (USD)</div>
        <div class="kpi-value" style="color:var(--amber);">${es(rnd_ipm, 0)}</div>
        <div class="kpi-wow {wow_cls(rnd_ipm_wow)}">{wow_arrow(rnd_ipm_wow)} {es(abs(rnd_ipm_wow), 1)}% WoW</div>
        <span class="kpi-band {band_css(rnd_band_ipm)}">{rnd_band_ipm}</span>
      </div>
      <div class="kpi-cell">
        <div class="kpi-label color-cr">Eficacia CR</div>
        <div class="kpi-value color-cr">{es(cr_ef)}%</div>
        <div class="kpi-wow {wow_cls(cr_ef_wow)}">{wow_arrow(cr_ef_wow)} {es(abs(cr_ef_wow))}pp WoW</div>
        <span class="kpi-band {band_css('Aceptable')}">Aceptable</span>
      </div>
      <div class="kpi-cell">
        <div class="kpi-label color-cv">Conv Rate</div>
        <div class="kpi-value color-cv">{es(cr_cv)}%</div>
        <div class="kpi-wow {wow_cls(cr_cv_wow)}">{wow_arrow(cr_cv_wow)} {es(abs(cr_cv_wow))}pp WoW</div>
        <span class="kpi-band {band_css('Revisar')}">Revisar</span>
      </div>
    </div>

    <div class="sev-groups-row">
      <div class="sev-group">
        <div class="sev-group-label">RND · Severity %NoDispo · P80</div>
        <div class="sev-strip">
          <div class="sev-pill" style="background:rgba(22,22,22,.80);color:#fff;"><span class="sev-n">{rnd_supc:,}</span><span class="sev-label">Súper Crit.</span></div>
          <div class="sev-pill" style="background:rgba(192,57,43,.15);color:var(--red);"><span class="sev-n">{rnd_crit:,}</span><span class="sev-label">Crítica</span></div>
          <div class="sev-pill" style="background:rgba(168,106,29,.15);color:var(--amber);"><span class="sev-n">{rnd_rev:,}</span><span class="sev-label">Revisar</span></div>
          <div class="sev-pill" style="background:rgba(92,70,156,.12);color:var(--violet);"><span class="sev-n">{rnd_acep:,}</span><span class="sev-label">Aceptable</span></div>
          <div class="sev-pill" style="background:rgba(79,195,244,.15);color:#0B7CA8;"><span class="sev-n">{rnd_exit:,}</span><span class="sev-label">Exitosa</span></div>
        </div>
      </div>
      <div class="sev-group">
        <div class="sev-group-label">CR · Severity Eficacia · P80</div>
        <div class="sev-strip">
          <div class="sev-pill" style="background:rgba(22,22,22,.80);color:#fff;"><span class="sev-n">{cr_supc:,}</span><span class="sev-label">Súper Crit.</span></div>
          <div class="sev-pill" style="background:rgba(192,57,43,.15);color:var(--red);"><span class="sev-n">{cr_crit:,}</span><span class="sev-label">Crítica</span></div>
          <div class="sev-pill" style="background:rgba(168,106,29,.15);color:var(--amber);"><span class="sev-n">{cr_rev:,}</span><span class="sev-label">Revisar</span></div>
          <div class="sev-pill" style="background:rgba(92,70,156,.12);color:var(--violet);"><span class="sev-n">{cr_acep:,}</span><span class="sev-label">Aceptable</span></div>
          <div class="sev-pill" style="background:rgba(79,195,244,.15);color:#0B7CA8;"><span class="sev-n">{cr_exit:,}</span><span class="sev-label">Exitosa</span></div>
        </div>
      </div>
    </div>

    <div class="report-links" onclick="event.stopPropagation()">
      <a class="report-btn btn-cr"  href="checkrates/{WEEK_STR}/CheckRates_Reporte_Editorial.html">→ CheckRates W{WEEK}</a>
      <a class="report-btn btn-rnd" href="rates-nodispo/{WEEK_STR}/RatesNoDispo_Reporte_Editorial.html">→ Rates No Dispo W{WEEK}</a>
      <a class="report-btn-ghost"   href="checkrates/{WEEK_STR}/Analisis_Checkrates_7d.xlsx">↓ Excel CR (37 pests.)</a>
      <a class="report-btn-ghost"   href="rates-nodispo/{WEEK_STR}/Analisis_Rates_NoDispo_7d.xlsx">↓ Excel RND (33 pests.)</a>
    </div>

  </div><!-- /featured-card -->

  <!-- ── Historial ── -->
  <div class="section-label" style="margin-top:8px;">Historial</div>
  <div class="history-grid">

    <div class="history-card" onclick="window.location='checkrates/{WEEK_PREV_STR}/CheckRates_Reporte_Editorial.html'">
      <div class="hcard-week">Week {WEEK_PREV}</div>
      <div class="hcard-period">{PERIODO_PREV}</div>
      <div class="hcard-kpis">
        <div class="hcard-kpi">
          <span class="hcard-kpi-label color-rnd">% No Dispo</span>
          <span class="hcard-kpi-value color-rnd">{es(rnd_pct_prev)}%</span>
        </div>
        <div class="hcard-kpi">
          <span class="hcard-kpi-label color-ipm">IPM</span>
          <span class="hcard-kpi-value" style="color:var(--amber);">${es(rnd_ipm_prev, 0)}</span>
        </div>
        <div class="hcard-kpi">
          <span class="hcard-kpi-label color-cr">Eficacia</span>
          <span class="hcard-kpi-value color-cr">{es(cr_ef_prev)}%</span>
        </div>
        <div class="hcard-kpi">
          <span class="hcard-kpi-label color-cv">Conv Rate</span>
          <span class="hcard-kpi-value color-cv">{es(cr_cv_prev)}%</span>
        </div>
      </div>
      <div class="hcard-links" onclick="event.stopPropagation()">
        <a class="hcard-link hlink-cr"  href="checkrates/{WEEK_PREV_STR}/CheckRates_Reporte_Editorial.html">CheckRates →</a>
        <a class="hcard-link hlink-rnd" href="rates-nodispo/{WEEK_PREV_STR}/RatesNoDispo_Reporte_Editorial.html">Rates No Dispo →</a>
      </div>
    </div>

    <div class="history-card" style="opacity:.4;cursor:default;pointer-events:none;">
      <div class="hcard-week">Week {WEEK_PREV - 1}</div>
      <div style="font-size:12px;color:var(--ink-muted);margin-top:8px;">No disponible en este hub.</div>
    </div>

  </div><!-- /history-grid -->

  <footer class="hub-footer">
    <div class="hub-footer-left">
      <strong>PriceTravel · Supply Optimization</strong><br>
      Última actualización: Week {WEEK} · {PERIODO}
    </div>
    <div class="hub-footer-right">analytics-desk.netlify.app</div>
  </footer>

</div><!-- /hub-wrap -->

<script>
(function(){{
  if(sessionStorage.getItem('hub_auth')==='1'){{
    document.getElementById('login-overlay').style.display='none';
    document.getElementById('hub-content').style.display='block';
  }}
  document.getElementById('login-pass').addEventListener('keydown',function(e){{
    if(e.key==='Enter') doLogin();
  }});
}})();
function doLogin(){{
  var u=document.getElementById('login-user').value.trim();
  var p=document.getElementById('login-pass').value.trim();
  if(u==='pricetravel'&&p==='supply2026'){{
    sessionStorage.setItem('hub_auth','1');
    document.getElementById('login-overlay').style.display='none';
    document.getElementById('hub-content').style.display='block';
  }}else{{
    document.getElementById('login-error').style.display='block';
  }}
}}
</script>
</body>
</html>"""
    return html


# ── Escribir index.html ───────────────────────────────────────────────────────
index_html = build_index()
index_path = OUTPUTS / 'index.html'
index_path.write_text(index_html, encoding='utf-8')
print(f'✅ index.html generado · {len(index_html):,} chars')


# ── Armar ZIP con estructura del repo ────────────────────────────────────────
ZIP_ROOT = Path(f'/home/claude/Price_W{WEEK}')
ZIP_ROOT.mkdir(parents=True, exist_ok=True)

dirs = [
    ZIP_ROOT / 'checkrates' / WEEK_STR,
    ZIP_ROOT / 'rates-nodispo' / WEEK_STR,
    ZIP_ROOT / '_email' / WEEK_STR,
]
for d in dirs:
    d.mkdir(parents=True, exist_ok=True)

files = {
    OUTPUTS / 'Supply_CheckRates_W19.html':        ZIP_ROOT / 'checkrates' / WEEK_STR / 'CheckRates_Reporte_Editorial.html',
    OUTPUTS / 'Analisis_Checkrates_7d.xlsx':        ZIP_ROOT / 'checkrates' / WEEK_STR / 'Analisis_Checkrates_7d.xlsx',
    OUTPUTS / 'Analisis_Checkrates_B2C_7d.xlsx':    ZIP_ROOT / 'checkrates' / WEEK_STR / 'Analisis_Checkrates_B2C_7d.xlsx',
    OUTPUTS / 'Analisis_Checkrates_OP_7d.xlsx':     ZIP_ROOT / 'checkrates' / WEEK_STR / 'Analisis_Checkrates_OP_7d.xlsx',
    OUTPUTS / 'Analisis_Checkrates_CUG_7d.xlsx':    ZIP_ROOT / 'checkrates' / WEEK_STR / 'Analisis_Checkrates_CUG_7d.xlsx',
    OUTPUTS / 'Supply_RatesNoDispo_W19.html':       ZIP_ROOT / 'rates-nodispo' / WEEK_STR / 'RatesNoDispo_Reporte_Editorial.html',
    OUTPUTS / 'Analisis_Rates_NoDispo_7d.xlsx':     ZIP_ROOT / 'rates-nodispo' / WEEK_STR / 'Analisis_Rates_NoDispo_7d.xlsx',
    OUTPUTS / 'Analisis_Rates_NoDispo_B2C_7d.xlsx': ZIP_ROOT / 'rates-nodispo' / WEEK_STR / 'Analisis_Rates_NoDispo_B2C_7d.xlsx',
    OUTPUTS / 'Analisis_Rates_NoDispo_OP_7d.xlsx':  ZIP_ROOT / 'rates-nodispo' / WEEK_STR / 'Analisis_Rates_NoDispo_OP_7d.xlsx',
    OUTPUTS / 'Analisis_Rates_NoDispo_CUG_7d.xlsx': ZIP_ROOT / 'rates-nodispo' / WEEK_STR / 'Analisis_Rates_NoDispo_CUG_7d.xlsx',
    OUTPUTS / f'Mail_W{WEEK}.html':                 ZIP_ROOT / '_email' / WEEK_STR / f'Mail_W{WEEK}.html',
    OUTPUTS / 'index.html':                         ZIP_ROOT / 'index.html',
}

print('\nCopiando archivos al ZIP...')
missing = []
for src, dst in files.items():
    if src.exists():
        shutil.copy2(src, dst)
        print(f'  ✓ {dst.relative_to(ZIP_ROOT)}')
    else:
        missing.append(src.name)
        print(f'  ✗ FALTA: {src.name}')

zip_path = OUTPUTS / f'Price_W{WEEK}.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(ZIP_ROOT.rglob('*')):
        if f.is_file():
            zf.write(f, f.relative_to(ZIP_ROOT.parent))

print(f'\n✅ ZIP generado: {zip_path}')
print(f'   Tamaño: {zip_path.stat().st_size / 1024:.0f} KB')
print(f'   Archivos: {sum(1 for _ in ZIP_ROOT.rglob("*") if _.is_file())}')
if missing:
    print(f'\n⚠️  Faltantes (no incluidos en ZIP): {missing}')

print(f'\n📦 Estructura del ZIP:')
with zipfile.ZipFile(zip_path, 'r') as zf:
    for name in sorted(zf.namelist()):
        info = zf.getinfo(name)
        print(f'   {name}  ({info.file_size/1024:.0f} KB)')

print(f'\n✅ build_package.py completado · Week {WEEK}')
print(f'   Próximo paso: commit con mensaje:')
print(f'   "feat: Week {WEEK} · RatesNoDispo + CheckRates + hub index · {PERIODO}"')
