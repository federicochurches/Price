"""
build_package.py · Paso 6 del pipeline semanal
Genera index.html del hub + ZIP con estructura del repo lista para commit.

Uso:
    python build_package.py

CONFIG SEMANAL — solo cambiar este bloque cada semana:
"""
import pickle, zipfile, shutil
import sys, os
from pathlib import Path

# Agregar raíz del proyecto a sys.path (para imports de _helpers/)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Imports desde _helpers/
try:
    from _helpers.template_seguimiento import generar_archivo_seguimiento
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from template_seguimiento import generar_archivo_seguimiento

# ── CONFIG SEMANAL ────────────────────────────────────────────────────────────
# Lee desde env vars (run_pipeline.py) o fallback a hardcodeado
WEEK        = int(os.getenv('VOL_NUM', '21'))
PERIODO     = os.getenv('PERIODO', '19–25 may 2026')
FECHA_PUB   = os.getenv('FECHA_PUB', 'Lunes 26 mayo 2026')

WEEK_PREV        = int(os.getenv('VOL_NUM_PREV', '20')) if os.getenv('VOL_NUM_PREV') else WEEK - 1
PERIODO_PREV     = os.getenv('PERIODO_PREV', '12–18 may 2026')
WEEK_PREV2       = WEEK_PREV - 1
PERIODO_PREV2    = '5–11 may 2026'  # Fallback simple

PICKLE_RND  = os.getenv('PICKLE_RND', f'rnd_w{WEEK}_data.pkl')
PICKLE_CR   = os.getenv('PICKLE_CR', f'cr_w{WEEK}_data.pkl')
PICKLE_BK   = os.getenv('PICKLE_BK', f'bk_w{WEEK}_data.pkl')

OUTPUTS     = Path(os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs'))
SCRIPT_DIR  = Path(__file__).parent
PROJECT     = Path(os.getenv('PROJECT_DIR', '/mnt/project'))
# ─────────────────────────────────────────────────────────────────────────────

WEEK_STR       = f'week-{WEEK}'
WEEK_PREV_STR  = f'week-{WEEK_PREV}'
WEEK_PREV2_STR = f'week-{WEEK_PREV2}'
SEMANA         = f'Week {WEEK}'
SEMANA_PREV    = f'Week {WEEK_PREV}'
SEMANA_PREV2   = f'Week {WEEK_PREV2}'

# ── Cargar KPIs desde pickles ─────────────────────────────────────────────────
with open(PICKLE_RND, 'rb') as f:
    DR = pickle.load(f)
with open(PICKLE_CR, 'rb') as f:
    DC = pickle.load(f)

try:
    with open(PICKLE_BK, 'rb') as f:
        DB = pickle.load(f)
    bk_global = DB.get('bk_global', None)
    bk_wow    = DB.get('bk_wow', None)
except Exception:
    bk_global = None
    bk_wow    = None

mr   = DR['M'][f'global_w{WEEK}']
mr17 = DR['M'][f'global_w{WEEK_PREV}']
mc   = DC['M'][f'global_w{WEEK}']
mc17 = DC['M'][f'global_w{WEEK_PREV}']

rnd_pct  = mr['pct_nodispo'] * 100
cr_ef    = mc['eficacia'] * 100
cr_cv    = mc['conv_rate'] * 100

sev_nd  = DR['sev_nd']
sev_ef  = DC['sev_ef_p80']
rnd_supc = int(sev_nd.get('Súper Crítica', 0))
rnd_crit = int(sev_nd.get('Crítica', 0))
cr_supc  = int(sev_ef.get('Súper Crítica', 0))
cr_crit  = int(sev_ef.get('Crítica', 0))

def es(x, d=2):
    s = f'{x:,.{d}f}'
    return s.replace(',', '|').replace('.', ',').replace('|', '.')

# Logo PriceTravel · extraído de calc_inv.py · no regenerar
_LOGO_B64 = "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"


# ── Generar index.html del hub ─────────────────────────────────────────────────
def build_index():
    nd_meta = (
        f'{len(DR["p80_hotel"]):,} hoteles P80 · '
        f'%NoDispo {es(rnd_pct)}% · '
        f'GB ${es(mr["gb_usd"]/1e6, 2)}M · '
        f'{rnd_supc} Súper Críticos / {rnd_crit} Críticos'
    )
    ck_meta = (
        f'{len(DC["p80_hotel"]):,} hoteles P80 · '
        f'Eficacia {es(cr_ef)}% · '
        f'Conv Rate {es(cr_cv)}% · '
        f'{cr_supc} Súper Críticos / {cr_crit} Críticos eficacia'
    )

    # KPI WoW strings
    rnd_wow      = (rnd_pct - mr17['pct_nodispo']*100)
    cr_ef_wow    = (cr_ef - mc17['eficacia']*100)
    cr_cv_wow    = (cr_cv - mc17['conv_rate']*100)
    rnd_wow_str      = f'+{rnd_wow:.2f}pp'   if rnd_wow >= 0   else f'{rnd_wow:.2f}pp'
    cr_ef_wow_str    = f'+{cr_ef_wow:.2f}pp' if cr_ef_wow >= 0 else f'{cr_ef_wow:.2f}pp'
    cr_cv_wow_str    = f'+{cr_cv_wow:.2f}pp' if cr_cv_wow >= 0 else f'{cr_cv_wow:.2f}pp'
    # Colores WoW pre-calculados
    def _wc(v): return ("#1A6B4A","#E1F5EE") if v>=0 else ("#FF3B30","#FFE5E3")
    def _wb(v,s): fg,bg=_wc(v); return f'<div style="font-size:9px;font-weight:700;color:{fg};background:{bg};padding:1px 6px;border-radius:10px;display:inline-block;margin-top:2px;">{s}</div>'
    wow_ef  = _wb(cr_ef_wow,  cr_ef_wow_str)
    wow_cv  = _wb(cr_cv_wow,  cr_cv_wow_str)
    wow_nd  = _wb(rnd_wow,    rnd_wow_str)
    # BK WoW (graceful — solo si el pickle está disponible)
    if bk_global is not None and bk_wow is not None:
        bk_wow_pp  = bk_wow * 100
        bk_wow_str = f'+{bk_wow_pp:.2f}pp' if bk_wow_pp >= 0 else f'{bk_wow_pp:.2f}pp'
        wow_bk     = _wb(bk_wow_pp, bk_wow_str)
        bk_val_str = f'{bk_global*100:.1f}%'
    else:
        wow_bk     = ''
        bk_val_str = '—'

    # Inventory KPIs W25 (from INVENTORY_W25.html · calc_inv.py run)
    inv_n      = '305.567'   # Sistema W25 (tipificados: PP + Third Party, excl. sin_contrato)
    inv_pp_n   = '58.990'    # Producto Propio (Solo Propio + Hybrid)
    inv_gap    = '11.010'    # Gap vs Target 70K
    inv_avance = f'{round(58990/70000*100, 1):.1f}%'  # % avance = 84.3%

    # Inventory WoW (W25 vs W24 · netnew real del chart = 44 hoteles nuevos en W25)
    _inv_n_d   = 305567 - 309016   # −3449 (cambio en total tipificados)
    _inv_pp_d  = 44                # netnew W25 real (no PP diff que incluye cambios de dataset)
    _inv_gap_d = -44               # gap cierra en 44
    def _inv_fmt(v): return f'+{v:,}'.replace(',', '.') if v >= 0 else f'{v:,}'.replace(',', '.')
    # PP badge: % de crecimiento = 44 nuevos / PP semana anterior (58.892)
    _pp_prev   = 58892
    _pp_pct    = round(_inv_pp_d / _pp_prev * 100, 2) if _pp_prev else 0
    _pp_pct_str = f'+{_pp_pct:.2f}%' if _pp_pct >= 0 else f'{_pp_pct:.2f}%'
    wow_inv_pp  = _wb(_inv_pp_d, _pp_pct_str)
    # Avance badge: delta en pp de avance % (84.27% - 84.13% = +0.14pp)
    _av_prev   = round(_pp_prev / 70000 * 100, 2)   # avance W24 = 84.13%
    _av_curr   = round(58990    / 70000 * 100, 2)    # avance W25 = 84.27%
    _av_delta  = round(_av_curr - _av_prev, 2)
    _av_str    = f'+{_av_delta:.2f}pp' if _av_delta >= 0 else f'{_av_delta:.2f}pp'
    wow_inv_gap = _wb(_av_delta, _av_str)
    wow_inv_n   = _wb(_inv_n_d, _inv_fmt(_inv_n_d))


    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PriceTravel · Supply Optimization</title>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--paper:#F8F4EC;--ink:#161616;--muted:#8A8377;--rule:#C9C1B0;--rule-soft:#E0D9CF;--rnd:#EA0074;--cr:#5C469C;--inv:#4FC3F4;--white:#ffffff;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Geist',sans-serif;background:var(--paper);color:var(--ink);min-height:100vh;display:flex;align-items:center;justify-content:center;}}
#lock{{width:100%;max-width:420px;padding:0;display:flex;flex-direction:column;min-height:100vh;justify-content:center;position:relative;}}
.lock-bg-accent{{position:fixed;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#EA0074 0%,#5C469C 100%);z-index:10;}}
.lock-inner{{padding:48px 40px 40px;background:var(--paper);}}
.lock-logo-wrap{{margin-bottom:20px;}}
.lock-logo-wrap img{{height:40px;display:block;filter:saturate(0) brightness(0);}}
.lock-headline{{font-size:12px;color:var(--muted);font-weight:400;margin-bottom:28px;line-height:1.5;}}
.lock-form-group{{margin-bottom:12px;position:relative;}}
.lock-label{{display:block;font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}}
.lock-field{{width:100%;padding:13px 16px;border:1px solid var(--rule);background:var(--white);font-family:'Geist',sans-serif;font-size:15px;color:var(--ink);outline:none;border-radius:0;transition:border-color .15s;}}
.lock-field:focus{{border-color:#EA0074;}}
.lock-field::placeholder{{color:#BDB8B0;}}
.lock-btn{{width:100%;padding:15px;background:var(--ink);color:#fff;border:none;font-family:'Geist',sans-serif;font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;cursor:pointer;transition:background .15s;margin-top:4px;}}
.lock-btn:hover{{background:#EA0074;}}
.lock-btn:active{{transform:scale(.99);}}
.lock-error{{font-size:11px;color:#FF3B30;margin-top:10px;display:none;padding:10px 14px;border-left:3px solid #FF3B30;background:rgba(192,57,43,.06);font-weight:500;}}
.lock-footer{{padding:18px 40px;border-top:1px solid var(--rule);display:flex;justify-content:space-between;align-items:center;}}
.lock-footer-tag{{font-size:10px;color:var(--muted);}}
.lock-footer-url{{font-size:10px;color:var(--muted);}}
@media(max-width:480px){{.lock-inner{{padding:36px 24px 28px;}}.lock-footer{{padding:14px 24px;}}}}
#hub{{display:none;width:100%;max-width:1060px;padding:36px 40px 60px;}}
.hub-header{{border-top:3px solid var(--ink);border-bottom:1px solid var(--rule);padding-top:14px;padding-bottom:16px;margin-bottom:32px;display:flex;justify-content:space-between;align-items:center;gap:20px;}}
.hub-tag{{display:inline-block;background:#5C469C;color:#FFFFFF;padding:3px 9px;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;border-radius:3px;margin-bottom:6px;}}
.hub-title{{font-size:26px;font-weight:800;letter-spacing:-.02em;line-height:1.1;}}
.hub-sub{{font-size:12px;color:var(--muted);margin-top:4px;}}
.hub-logo{{display:flex;align-items:center;}}
.section-label{{font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:10px;display:flex;align-items:center;gap:6px;}}
.section-dot{{width:6px;height:6px;border-radius:50%;display:inline-block;}}
.hub-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:10px;}}.hub-grid.inactive{{grid-template-columns:repeat(auto-fit,minmax(260px,1fr));}}
.rpt-card{{background:var(--paper);border:1px solid var(--rule);border-radius:4px;color:var(--ink);display:flex;flex-direction:column;transition:border-color .15s,box-shadow .15s;overflow:hidden;cursor:pointer;position:relative;min-width:0;}}
.rpt-card.card-active:hover{{border-color:var(--ink);box-shadow:0 2px 8px rgba(0,0,0,.08);}}
.rpt-card.card-active[data-no-link="1"]:hover{{border-color:var(--rule);box-shadow:none;}}
.rpt-card.card-inactive{{background:#F0EBE2;cursor:default;}}
.rpt-card.card-inactive .rpt-card-top,.rpt-card.card-inactive .rpt-pills{{position:relative;z-index:0;}}
.dim-overlay{{position:absolute;inset:0;backdrop-filter:blur(1.5px);-webkit-backdrop-filter:blur(1.5px);background:rgba(240,235,226,0.35);z-index:1;pointer-events:none;}}
.lock-chip{{position:absolute;top:10px;right:10px;z-index:3;border:none;border-radius:20px;padding:3px 10px;font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:#EDEAE4;color:#6B6861;}}.lock-chip-gray{{background:#EDEAE4;color:#6B6861;}}
.rpt-card-top{{padding:18px 18px 14px;flex:1;}}
.rpt-accent{{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;font-size:9px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;margin-bottom:10px;border-radius:3px;}}
.rpt-kpis{{display:flex;gap:20px;margin-top:10px;flex-wrap:wrap;}}
.rpt-kpi{{display:flex;flex-direction:column;gap:4px;}}
.rpt-kpi-label{{font-size:9px;color:var(--muted);}}
.rpt-kpi-val{{font-size:13px;font-weight:700;color:var(--ink);}}
.rpt-kpi-wow{{font-size:9px;color:#FF3B30;}}
.rpt-desc{{font-size:12px;color:var(--muted);line-height:1.5;margin-top:6px;}}
.rpt-progress{{margin-top:10px;}}
.rpt-progress-bar{{height:3px;background:var(--rule-soft);border-radius:2px;overflow:hidden;}}
.rpt-progress-fill{{height:100%;border-radius:2px;}}
.rpt-progress-label{{font-size:9px;color:var(--muted);margin-top:3px;}}
.rpt-pills{{padding:10px 18px;border-top:1px solid var(--rule);display:flex;align-items:center;justify-content:space-between;}}
.rpt-pills-left{{display:flex;align-items:center;gap:5px;}}
.rpt-pills-label{{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-right:2px;}}
.pill{{font-size:10px;font-weight:600;padding:2px 8px;border:1px solid var(--rule);border-radius:20px;text-decoration:none;color:var(--muted);background:transparent;transition:border-color .12s,color .12s;}}
.pill:hover{{color:var(--ink);border-color:var(--ink);}}
.pill.active{{color:var(--white);border-color:transparent;}}
.rpt-dl{{font-size:9px;font-weight:600;padding:2px 8px;border:1px solid var(--rule);border-radius:3px;color:var(--muted);text-decoration:none;}}
.aw{{font-weight:600;}}
.ap{{font-size:11px;color:var(--muted);}}
</style>
</head>
<body>

<!-- ══ LOCK SCREEN ══ -->
<div id="lock">
  <div class="lock-bg-accent"></div>
  <div class="lock-inner">
    <div class="lock-logo-wrap">
      <img src="data:image/png;base64,{_LOGO_B64}" alt="PriceTravel" class="dark-invert">
    </div>
    <div class="lock-headline">Acceso restringido al equipo de Supply.<br>Ingresá tus credenciales para continuar.</div>
    <div class="lock-form-group">
      <label class="lock-label" for="user">Usuario</label>
      <input type="text" id="user" class="lock-field" placeholder="tu.usuario" autocomplete="username" />
    </div>
    <div class="lock-form-group">
      <label class="lock-label" for="pass">Contraseña</label>
      <input type="password" id="pass" class="lock-field" placeholder="••••••••" autocomplete="current-password" />
    </div>
    <button class="lock-btn" onclick="checkAuth()">Ingresar →</button>
    <div class="lock-error" id="error">Usuario o contraseña incorrectos. Intentá de nuevo.</div>
  </div>
  <div class="lock-footer">
    <span class="lock-footer-tag">analytics-desk.netlify.app</span>
    <span class="lock-footer-url">{SEMANA}</span>
  </div>
</div>

<!-- ══ HUB ══ -->
<div id="hub">
  <div class="hub-header">
    <div>
      <div class="hub-tag">{SEMANA}</div>
      <div class="hub-title"><span style="color:#5C469C;">Hub</span> <span style="color:#333132;">Supply Optimization</span></div>
      <div class="hub-sub">{SEMANA} · {PERIODO}</div>
    </div>
    <div class="hub-logo">
      <img src="data:image/png;base64,{_LOGO_B64}" alt="PriceTravel" style="height:40px;display:block;filter:saturate(0) brightness(0);">
    </div>
  </div>
  <div class="hub-grid" style="margin-bottom:20px;">

    <div class="rpt-card card-active" onclick="location.href='reports/{WEEK_STR}/SUPPLY_W{WEEK}.html'">
      <div class="rpt-card-top">
        <span class="rpt-accent" style="background:#EDEAE4;color:#6B6861;">Activo</span>
        <div style="font-size:13px;font-weight:700;margin-bottom:2px;color:var(--ink);">Connectivities Health &amp; Hotel Availability</div>
        <div class="rpt-desc">CheckRates · Rates No Dispo · Eficacia técnica y disponibilidad por canal y corporativo.</div>
        <div class="rpt-kpis">\n          <div class="rpt-kpi"><div class="rpt-kpi-label">Eficacia CR</div><div class="rpt-kpi-val">{cr_ef:.1f}%</div>{wow_ef}</div>\n          <div class="rpt-kpi"><div class="rpt-kpi-label">Conv Rate</div><div class="rpt-kpi-val">{cr_cv:.2f}%</div>{wow_cv}</div>\n          <div class="rpt-kpi"><div class="rpt-kpi-label" style="font-weight:700;">BK</div><div class="rpt-kpi-val">{bk_val_str}</div>{wow_bk}</div>\n          <div class="rpt-kpi"><div class="rpt-kpi-label">%NoDispo</div><div class="rpt-kpi-val">{rnd_pct:.2f}%</div>{wow_nd}</div>\n        </div>
      </div>
      <div class="rpt-pills">
        <div class="rpt-pills-left">
          <span class="rpt-pills-label">Historial</span>
          <span class="pill active" style="background:var(--ink);border-color:var(--ink);">{SEMANA}</span>
          <a href="reports/{WEEK_PREV_STR}/SUPPLY_W{WEEK_PREV}.html" class="pill" onclick="event.stopPropagation()">W{WEEK_PREV}</a>
          <a href="reports/{WEEK_PREV2_STR}/SUPPLY_W{WEEK_PREV2}.html" class="pill" onclick="event.stopPropagation()">W{WEEK_PREV2}</a>
        </div>
        <a href="checkrates/week-{WEEK}/Analisis_CheckRates_W{WEEK}.xlsx" onclick="event.stopPropagation()" class="rpt-dl">⬇ CR</a>
      </div>
    </div>

    <div class="rpt-card card-active" onclick="location.href='inventory/{WEEK_STR}/INVENTORY_W{WEEK}.html'" style="cursor:pointer;">
      <div class="rpt-card-top">
        <span class="rpt-accent" style="background:#EDEAE4;color:#6B6861;">Beta</span>
        <div style="font-size:13px;font-weight:700;margin-bottom:2px;color:var(--ink);">Hotel Inventory PriceTravel</div>
        <div class="rpt-desc">Universo de contratos · Producto Propio · Gap vs target 2026 · Crecimiento histórico.</div>
        <div class="rpt-kpis">
          <div class="rpt-kpi"><div class="rpt-kpi-label">Total</div><div class="rpt-kpi-val">{inv_n}</div>{wow_inv_n}</div>
          <div class="rpt-kpi"><div class="rpt-kpi-label">P. Propio</div><div class="rpt-kpi-val">{inv_pp_n}</div>{wow_inv_pp}</div>
          <div class="rpt-kpi"><div class="rpt-kpi-label">Avance 2026</div><div class="rpt-kpi-val">{inv_avance}</div>{wow_inv_gap}</div>
        </div>
      </div>
      <div class="rpt-pills">
        <div class="rpt-pills-left">
          <span class="rpt-pills-label">Historial</span>
          <span class="pill active" style="background:var(--ink);border-color:var(--ink);">{SEMANA}</span>
          <a href="inventory/{WEEK_PREV_STR}/INVENTORY_W{WEEK_PREV}.html" class="pill" onclick="event.stopPropagation()">W{WEEK_PREV}</a>
          <a href="inventory/{WEEK_PREV2_STR}/INVENTORY_W{WEEK_PREV2}.html" class="pill" onclick="event.stopPropagation()">W{WEEK_PREV2}</a>
        </div>
        <a href="inventory/{WEEK_STR}/Analisis_Inventory_W{WEEK}.xlsx" onclick="event.stopPropagation()" class="rpt-dl">⬇ Excel</a>
      </div>
    </div>
  </div>

  <!-- ── Card Excels Regionales ── -->
  <div class="hub-grid" style="margin-bottom:20px;grid-template-columns:1fr;">
    <div class="rpt-card card-active" data-no-link="1">
      <div class="rpt-card-top">
        <span class="rpt-accent" style="background:#EDEAE4;color:#6B6861;">Activo</span>
        <div style="font-size:13px;font-weight:700;margin-bottom:2px;color:var(--ink);">Excels Regionales</div>
        <div class="rpt-desc">CheckRates · Rates No Dispo · por región comercial · W{WEEK}</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:12px;">
          <div style="background:var(--paper-soft);border:1px solid var(--rule);border-radius:3px;overflow:hidden;">
            <div style="font-size:10px;font-weight:700;padding:6px 10px;border-bottom:1px solid var(--rule);color:var(--ink);">🇲🇽 MX</div>
            <div style="display:flex;">
              <a href="https://raw.githubusercontent.com/federicochurches/Price/main/rates-nodispo/week-{WEEK}/regional/Analisis_RND_Mexico_W{WEEK}.xlsx" onclick="event.stopPropagation()" style="flex:1;font-size:9px;font-weight:700;color:#EA0074;text-decoration:none;padding:5px 8px;border-right:1px solid var(--rule);text-align:center;">RND ↓</a>
              <a href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{WEEK}/regional/Analisis_CR_Mexico_W{WEEK}.xlsx"  onclick="event.stopPropagation()" style="flex:1;font-size:9px;font-weight:700;color:#5C469C;text-decoration:none;padding:5px 8px;text-align:center;">CR ↓</a>
            </div>
          </div>
          <div style="background:var(--paper-soft);border:1px solid var(--rule);border-radius:3px;overflow:hidden;">
            <div style="font-size:10px;font-weight:700;padding:6px 10px;border-bottom:1px solid var(--rule);color:var(--ink);">🇺🇸 US</div>
            <div style="display:flex;">
              <a href="https://raw.githubusercontent.com/federicochurches/Price/main/rates-nodispo/week-{WEEK}/regional/Analisis_RND_US_W{WEEK}.xlsx"     onclick="event.stopPropagation()" style="flex:1;font-size:9px;font-weight:700;color:#EA0074;text-decoration:none;padding:5px 8px;border-right:1px solid var(--rule);text-align:center;">RND ↓</a>
              <a href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{WEEK}/regional/Analisis_CR_US_W{WEEK}.xlsx"          onclick="event.stopPropagation()" style="flex:1;font-size:9px;font-weight:700;color:#5C469C;text-decoration:none;padding:5px 8px;text-align:center;">CR ↓</a>
            </div>
          </div>
          <div style="background:var(--paper-soft);border:1px solid var(--rule);border-radius:3px;overflow:hidden;">
            <div style="font-size:10px;font-weight:700;padding:6px 10px;border-bottom:1px solid var(--rule);color:var(--ink);">🌎 CALA</div>
            <div style="display:flex;">
              <a href="https://raw.githubusercontent.com/federicochurches/Price/main/rates-nodispo/week-{WEEK}/regional/Analisis_RND_CALA_W{WEEK}.xlsx"   onclick="event.stopPropagation()" style="flex:1;font-size:9px;font-weight:700;color:#EA0074;text-decoration:none;padding:5px 8px;border-right:1px solid var(--rule);text-align:center;">RND ↓</a>
              <a href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{WEEK}/regional/Analisis_CR_CALA_W{WEEK}.xlsx"        onclick="event.stopPropagation()" style="flex:1;font-size:9px;font-weight:700;color:#5C469C;text-decoration:none;padding:5px 8px;text-align:center;">CR ↓</a>
            </div>
          </div>
        </div>
      </div>
      <div class="rpt-pills">
        <div class="rpt-pills-left">
          <span class="rpt-pills-label">Semana</span>
          <span class="pill active" style="background:var(--ink);border-color:var(--ink);">{SEMANA}</span>
        </div>
      </div>
    </div>
  </div>

  <div class="hub-grid inactive" style="margin-bottom:20px;">

    <div class="rpt-card card-inactive">
      <div class="dim-overlay"></div>
      <div class="lock-chip">En construcción</div>
      <div class="rpt-card-top">
        <span class="rpt-accent" style="background:#EDEAE4;color:#6B6861;">En construcción &nbsp;·&nbsp; RateCode Inventory</span>
        <div style="font-size:13px;font-weight:700;margin-bottom:2px;color:var(--ink);">RateCode Inventory</div>
        <div class="rpt-desc">Inventario de rate codes por hotel y channel. Paridad y cobertura tarifaria.</div>
        <div class="rpt-progress">
          <div class="rpt-progress-bar"><div class="rpt-progress-fill" style="width:15%;background:var(--muted);"></div></div>
          <div class="rpt-progress-label">Definición de scope en progreso</div>
        </div>
      </div>
      <div class="rpt-pills" style="justify-content:flex-end;"><span style="font-size:9px;color:var(--muted);">Sin dataset aún</span></div>
    </div>

    <div class="rpt-card card-inactive">
      <div class="dim-overlay"></div>
      <div class="lock-chip">En construcción</div>
      <div class="rpt-card-top">
        <span class="rpt-accent" style="background:#EDEAE4;color:#6B6861;">En construcción &nbsp;·&nbsp; Troubleshooting</span>
        <div style="font-size:13px;font-weight:700;margin-bottom:2px;color:var(--ink);">Supply Troubleshooting</div>
        <div class="rpt-desc">Dashboard tickets Rocket Chat · 75 tickets · Feb–May 2026 · 4 tipos de cuenta · 8 tipos de consulta.</div>
        <div class="rpt-progress">
          <div class="rpt-progress-bar"><div class="rpt-progress-fill" style="width:60%;background:var(--muted);"></div></div>
          <div class="rpt-progress-label">Dashboard listo · pendiente integración Hub</div>
        </div>
      </div>
      <div class="rpt-pills" style="justify-content:flex-end;"><span style="font-size:9px;color:var(--muted);">Extracción local vía Python</span></div>
    </div>
  </div>
  <div class="hub-grid inactive" style="margin-bottom:28px;">

    <div class="rpt-card card-inactive" style="opacity:.55;">
      <div class="dim-overlay"></div>
      <div class="lock-chip lock-chip-gray">Backlog</div>
      <div class="rpt-card-top">
        <span class="rpt-accent" style="background:#EDEAE4;color:#6B6861;">Backlog · Strategy</span>
        <div style="font-size:13px;font-weight:700;margin-bottom:2px;color:var(--ink);">Optimization Strategy Layer</div>
        <div class="rpt-desc">Síntesis cross-módulo · recomendaciones priorizadas · cruza CR, RND e Inventory.</div>
      </div>
      <div class="rpt-pills" style="justify-content:flex-end;"><span style="font-size:9px;color:var(--muted);">Sin dataset · sin diseño</span></div>
    </div>

    <div class="rpt-card card-inactive" style="opacity:.55;">
      <div class="dim-overlay"></div>
      <div class="lock-chip lock-chip-gray">Backlog</div>
      <div class="rpt-card-top">
        <span class="rpt-accent" style="background:#EDEAE4;color:#6B6861;">Backlog · Alertas</span>
        <div style="font-size:13px;font-weight:700;margin-bottom:2px;color:var(--ink);">Alertas</div>
        <div class="rpt-desc">Alertas proactivas automáticas · hoteles bajo threshold · flags por canal y corporativo.</div>
      </div>
      <div class="rpt-pills" style="justify-content:flex-end;"><span style="font-size:9px;color:var(--muted);">Sin dataset · sin diseño</span></div>
    </div>
  </div>

  <!-- ── Footer Hub · links regionales ── -->
  <div style="border-top:1px solid var(--rule);margin-top:8px;padding:16px 0 4px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
    <span style="font-size:9px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:var(--muted);">Excels Regionales W{WEEK}</span>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
      <span style="font-size:9px;color:var(--muted);font-weight:600;">MX</span>
      <a href="https://raw.githubusercontent.com/federicochurches/Price/main/rates-nodispo/week-{WEEK}/regional/Analisis_RND_Mexico_W{WEEK}.xlsx" style="font-size:9px;font-weight:700;color:#EA0074;text-decoration:none;border:1px solid #EA0074;border-radius:3px;padding:2px 7px;">RND ↓</a>
      <a href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{WEEK}/regional/Analisis_CR_Mexico_W{WEEK}.xlsx"   style="font-size:9px;font-weight:700;color:#5C469C;text-decoration:none;border:1px solid #5C469C;border-radius:3px;padding:2px 7px;">CR ↓</a>
      <span style="color:var(--rule);">|</span>
      <span style="font-size:9px;color:var(--muted);font-weight:600;">US</span>
      <a href="https://raw.githubusercontent.com/federicochurches/Price/main/rates-nodispo/week-{WEEK}/regional/Analisis_RND_US_W{WEEK}.xlsx"    style="font-size:9px;font-weight:700;color:#EA0074;text-decoration:none;border:1px solid #EA0074;border-radius:3px;padding:2px 7px;">RND ↓</a>
      <a href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{WEEK}/regional/Analisis_CR_US_W{WEEK}.xlsx"        style="font-size:9px;font-weight:700;color:#5C469C;text-decoration:none;border:1px solid #5C469C;border-radius:3px;padding:2px 7px;">CR ↓</a>
      <span style="color:var(--rule);">|</span>
      <span style="font-size:9px;color:var(--muted);font-weight:600;">CALA</span>
      <a href="https://raw.githubusercontent.com/federicochurches/Price/main/rates-nodispo/week-{WEEK}/regional/Analisis_RND_CALA_W{WEEK}.xlsx"  style="font-size:9px;font-weight:700;color:#EA0074;text-decoration:none;border:1px solid #EA0074;border-radius:3px;padding:2px 7px;">RND ↓</a>
      <a href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{WEEK}/regional/Analisis_CR_CALA_W{WEEK}.xlsx"      style="font-size:9px;font-weight:700;color:#5C469C;text-decoration:none;border:1px solid #5C469C;border-radius:3px;padding:2px 7px;">CR ↓</a>
    </div>
  </div>

</div>

<script>
const CREDS = {{ user: 'pricetravel', pass: 'supply2026' }};
const SESSION_KEY = 'pt_analytics_auth';
function checkAuth() {{
  const u = document.getElementById('user').value.trim().toLowerCase();
  const p = document.getElementById('pass').value;
  if (u === CREDS.user && p === CREDS.pass) {{
    localStorage.setItem(SESSION_KEY, '1');
    showHub();
  }} else {{
    document.getElementById('error').style.display = 'block';
  }}
}}
function showHub() {{
  document.getElementById('lock').style.display = 'none';
  document.getElementById('hub').style.display = 'block';
  document.body.style.alignItems = 'flex-start';
}}
if (localStorage.getItem(SESSION_KEY)) showHub();
document.addEventListener('keydown', e => {{ if (e.key === 'Enter') checkAuth(); }});


</script>
</body>
</html>"""
    return html


# ── Escribir index.html ───────────────────────────────────────────────────────
index_html = build_index()
index_path = OUTPUTS / 'index.html'
index_path.write_text(index_html, encoding='utf-8')
# Copia en SCRIPT_DIR para que el ZIP builder la encuentre (y persista para commit)
(SCRIPT_DIR / 'index.html').write_text(index_html, encoding='utf-8')
print(f'✅ index.html generado · {len(index_html):,} chars')


# ── Generar archivo de seguimiento para la próxima semana ────────────────────
SEGUIMIENTO_ITEMS_RND = [
    {'cluster':'QW','report':'RND','text':f'Escalar {rnd_supc} hoteles Súper Críticos %NoDispo (>60%) — remediación técnica urgente'},
    {'cluster':'QW','report':'AMBOS','text':'Diagnóstico técnico Top 10 Sin Conversión de alto tráfico — mapping, paridad, inventario'},
    {'cluster':'MP','report':'RND','text':f'Saneamiento {rnd_crit + rnd_supc} hoteles Crítica/Súper Crítica %NoDispo — priorizar CUG y B2B-OP'},
    {'cluster':'ES','report':'RND','text':'Reducir cohorte Sin Conversión en P80 — proyecto trimestral técnico + comercial'},
    {'cluster':'ES','report':'RND','text':'Definir SLAs de %NoDispo por corporativo — Top 10 corp por tráfico'},
]
SEGUIMIENTO_ITEMS_CR = [
    {'cluster':'QW','report':'CR','text':f'Escalar {cr_supc} hoteles Súper Críticos de Eficacia (<60%) — revisión técnica conectividad'},
    {'cluster':'QW','report':'CR','text':'Auditar canal Third Party — paridad tarifas y latencia con Expedia y HotelBeds'},
    {'cluster':'MP','report':'CR','text':f'Saneamiento {cr_crit + cr_supc} hoteles Crítica/Súper Crítica Eficacia — CUG y B2B-OP primero'},
    {'cluster':'ES','report':'CR','text':'Revisión integral B2C (Conv Rate Crítica) — pricing, UX, mapping, fee structure'},
]
SEGUIMIENTO_ITEMS = SEGUIMIENTO_ITEMS_RND + SEGUIMIENTO_ITEMS_CR

seg_dir = OUTPUTS / '_seguimiento'
seg_dir.mkdir(parents=True, exist_ok=True)
seguimiento_path = seg_dir / f'plan_seguimiento_W{WEEK}.md'
generar_archivo_seguimiento(SEGUIMIENTO_ITEMS, f'W{WEEK}', seguimiento_path)
print(f'✅ plan_seguimiento_W{WEEK}.md generado · {len(SEGUIMIENTO_ITEMS)} items OPEN')

# ── Armar ZIP con estructura del repo ─────────────────────────────────────────
# Estructura exacta del repo GitHub (W21+):
#
# Price/
# ├── index.html
# ├── _email/week-NN/Mail_WNN.html
# ├── _docs/
# │   ├── CHANGELOG.md
# │   └── COMMIT_GUIDE.md
# ├── _seguimiento/plan_seguimiento_WNN.md   ← carryover semanal
# ├── reports/week-NN/                        ← W21+ HTML unificado
# │   └── SUPPLY_WNN.html
# ├── inventory/week-NN/                       ← Hotel Inventory
# │   ├── INVENTORY_WNN.html
# │   └── Analisis_Inventory_WNN.xlsx
# ├── checkrates/week-NN/                      ← solo Excels + Dataset
# │   ├── Analisis_CheckRates_WNN.xlsx
# │   └── Dataset_CheckRates_WNN.xlsx
# └── rates-nodispo/week-NN/                   ← solo Excels + Dataset
#     ├── Analisis_RatesNoDispo_WNN.xlsx
#     └── Dataset_RatesNoDispo_WNN.xlsx

ZIP_ROOT = Path(f'/home/claude/Price_W{WEEK}')
if ZIP_ROOT.exists():
    shutil.rmtree(ZIP_ROOT)
ZIP_ROOT.mkdir(parents=True)

# Crear todas las carpetas necesarias
for d in [
    ZIP_ROOT / 'reports'      / WEEK_STR,   # W21+ HTML unificado
    ZIP_ROOT / 'checkrates'   / WEEK_STR,   # solo Excels + Dataset
    ZIP_ROOT / 'rates-nodispo' / WEEK_STR,  # solo Excels + Dataset
    ZIP_ROOT / 'inventory'     / WEEK_STR,  # Hotel Inventory HTML + Excel
    ZIP_ROOT / '_email'        / WEEK_STR,
    ZIP_ROOT / '_seguimiento',
    ZIP_ROOT / '_docs',
]:
    d.mkdir(parents=True, exist_ok=True)

# Datasets crudos (input) — se copian desde uploads si existen
UPLOADS = Path(os.getenv('UPLOADS_DIR', '/mnt/user-data/uploads'))

# Intentar desde uploads, si no, desde proyecto
cr_dataset_uploads = UPLOADS / f'Dataset_CheckRates_W{WEEK}.xlsx'
cr_dataset_project = PROJECT / f'Dataset_CheckRates_W{WEEK}.xlsx'
cr_dataset = cr_dataset_uploads if cr_dataset_uploads.exists() else cr_dataset_project

rnd_dataset_uploads = UPLOADS / f'Dataset_RatesNoDispo_W{WEEK}.xlsx'
rnd_dataset_project = PROJECT / f'Dataset_RatesNoDispo_W{WEEK}.xlsx'
rnd_dataset = rnd_dataset_uploads if rnd_dataset_uploads.exists() else rnd_dataset_project

files = {
    # ── index.html (raíz) ──────────────────────────────────────────────────
    SCRIPT_DIR / 'index.html':
        ZIP_ROOT / 'index.html',

    # ── _email ──────────────────────────────────────────────────────────────
    # render_mail_v3.py escribe a _email/week-NN/ directamente (W25+);
    # fallback: raíz del repo (corridas anteriores donde OUT_FILE era la raíz)
    (SCRIPT_DIR / '_email' / WEEK_STR / f'Mail_W{WEEK}.html'
     if (SCRIPT_DIR / '_email' / WEEK_STR / f'Mail_W{WEEK}.html').exists()
     else OUTPUTS / f'Mail_W{WEEK}.html'):
        ZIP_ROOT / '_email' / WEEK_STR / f'Mail_W{WEEK}.html',

    # ── _seguimiento ────────────────────────────────────────────────────────
    OUTPUTS / '_seguimiento' / f'plan_seguimiento_W{WEEK}.md':
        ZIP_ROOT / '_seguimiento' / f'plan_seguimiento_W{WEEK}.md',

    # ── reports/week-NN · HTML unificado (W21+) ───────────────────────────
    OUTPUTS / f'SUPPLY_W{WEEK}.html':
        ZIP_ROOT / 'reports' / WEEK_STR / f'SUPPLY_W{WEEK}.html',

    # ── checkrates/week-NN · Excel consolidado ────────────────────────────
    OUTPUTS / f'Analisis_CheckRates_W{WEEK}.xlsx':
        ZIP_ROOT / 'checkrates' / WEEK_STR / f'Analisis_CheckRates_W{WEEK}.xlsx',

    # ── rates-nodispo/week-NN · Excel consolidado ─────────────────────────
    OUTPUTS / f'Analisis_RatesNoDispo_W{WEEK}.xlsx':
        ZIP_ROOT / 'rates-nodispo' / WEEK_STR / f'Analisis_RatesNoDispo_W{WEEK}.xlsx',

    # ── inventory/week-NN · script + HTML + Excel ─────────────────────────
    SCRIPT_DIR / 'inventory' / 'calc_inv.py':
        ZIP_ROOT / 'inventory' / 'calc_inv.py',
    OUTPUTS / f'INVENTORY_W{WEEK}.html':
        ZIP_ROOT / 'inventory' / WEEK_STR / f'INVENTORY_W{WEEK}.html',
    OUTPUTS / f'Analisis_Inventory_W{WEEK}.xlsx':
        ZIP_ROOT / 'inventory' / WEEK_STR / f'Analisis_Inventory_W{WEEK}.xlsx',
}

# Agregar datasets crudos si están disponibles
if cr_dataset.exists():
    files[cr_dataset] = ZIP_ROOT / 'checkrates' / WEEK_STR / f'Dataset_CheckRates_W{WEEK}.xlsx'
if rnd_dataset.exists():
    files[rnd_dataset] = ZIP_ROOT / 'rates-nodispo' / WEEK_STR / f'Dataset_RatesNoDispo_W{WEEK}.xlsx'

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
            zf.write(f, f.relative_to(ZIP_ROOT))

print(f'\n✅ ZIP generado: {zip_path}')
print(f'   Tamaño: {zip_path.stat().st_size / 1024:.0f} KB')
if missing:
    print(f'\n⚠️  Faltantes: {missing}')

print(f'\n📦 Estructura del ZIP:')
with zipfile.ZipFile(zip_path, 'r') as zf:
    for name in sorted(zf.namelist()):
        info = zf.getinfo(name)
        print(f'   {name}  ({info.file_size/1024:.0f} KB)')

print(f'\n✅ build_package.py completado · Week {WEEK}')
print(f'   Commit: "feat: Week {WEEK} · Supply unificado + Excels consolidados · {PERIODO}"')

# ── Limpiar outputs intermedios (quedan solo los dos ZIPs) ────────────────────
CLEANUP = [
    OUTPUTS / f'SUPPLY_W{WEEK}.html',
    OUTPUTS / f'Analisis_CheckRates_W{WEEK}.xlsx',
    OUTPUTS / f'Analisis_RatesNoDispo_W{WEEK}.xlsx',
    OUTPUTS / f'Mail_W{WEEK}.html',
    OUTPUTS / 'index.html',
    OUTPUTS / f'plan_seguimiento_W{WEEK}.md',
]
cleaned = 0
for f in CLEANUP:
    if f.exists():
        f.unlink()
        cleaned += 1

# Limpiar part*.html del directorio de trabajo (intermedios del render)
SCRIPT_DIR = Path(__file__).parent
PART_FILES = [
    'part1_cr.html', 'part2_cr.html', 'part3_cr.html',
    'part1_rnd.html', 'part2_rnd.html', 'part3_rnd.html',
]
for fname in PART_FILES:
    p = SCRIPT_DIR / fname
    if p.exists():
        p.unlink()
        cleaned += 1

if cleaned:
    print(f'\n🧹 Limpiados {cleaned} archivos intermedios de outputs/ y directorio de trabajo')
print(f'   Outputs finales: Price_W{WEEK}.zip · ProyectoClaude_PRICE_WNN.zip')
