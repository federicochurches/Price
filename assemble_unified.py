"""
assemble_unified.py · W21+ · Ensamblador HTML único Supply
Genera: SUPPLY_W{NN}.html
Estructura: HEAD → body → switcher → section-cr (p1+p2+p3 CR) → section-rnd (p1+p2+p3 RND) → cierre

Reemplaza: assemble_cr.py + assemble_rnd.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
from pathlib import Path

# ── Config desde env vars ──────────────────────────────────────────────────
VOL_NUM   = os.getenv('VOL_NUM', '21')
OUTPUTS   = Path(os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs'))
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# ── Leer semana de los pickles ─────────────────────────────────────────────
with open(os.getenv('PICKLE_CR', f'cr_w{VOL_NUM}_data.pkl'), 'rb') as _f:
    DC = pickle.load(_f)
with open(os.getenv('PICKLE_RND', f'rnd_w{VOL_NUM}_data.pkl'), 'rb') as _f:
    DR = pickle.load(_f)

WK      = f'W{VOL_NUM}'

# ── Histórico para panel Análisis de Rendimiento ──────────────────────────
import sys as _sys
_sys.path.insert(0, str(SCRIPT_DIR))
from historico_module import render_historico as _rh
from engine import banda_eficacia as _bef, banda_nodispo as _bnd
from render_helpers import searchbox_pill_html as _sbph

_ef_val  = DC.get('M',{}).get(f'global_w{VOL_NUM}',{}).get('eficacia', 0.9315)
_cv_val  = DC.get('M',{}).get(f'global_w{VOL_NUM}',{}).get('conv_rate', 0.0157)
_nd_val  = DR.get('M',{}).get(f'global_w{VOL_NUM}',{}).get('nodispo', 0.0263)
_ipm_val = DR.get('M',{}).get(f'global_w{VOL_NUM}',{}).get('rpm', 834.0)

from engine import banda_convrate as _bcv, banda_rpm as _brpm

HIST_CR_PANEL     = _rh('cr',  'eficacia', _bef(_ef_val), _ef_val, 'hcr-panel-ef')
HIST_CR_PANEL_CV  = _rh('cr',  'convrate', _bcv(_cv_val, 1), _cv_val, 'hcr-panel-cv')
HIST_RND_PANEL    = _rh('rnd', 'nodispo',  _bnd(_nd_val), _nd_val, 'hrnd-panel-nd')
HIST_RND_PANEL_IPM= _rh('rnd', 'ipm',      _brpm(_ipm_val, 1), _ipm_val, 'hrnd-panel-ipm')
HIST_CR_DIM       = _rh('cr',  'eficacia', _bef(_ef_val), _ef_val, 'hcr-dim-ef')
HIST_CR_DIM_CV    = _rh('cr',  'convrate', _bcv(_cv_val, 1), _cv_val, 'hcr-dim-cv')
HIST_RND_DIM      = _rh('rnd', 'nodispo',  _bnd(_nd_val), _nd_val, 'hrnd-dim-nd')
HIST_RND_DIM_IPM  = _rh('rnd', 'ipm',      _brpm(_ipm_val, 1), _ipm_val, 'hrnd-dim-ipm')

SB_PANEL_TH = _sbph('sb-panel-th', accent_color='#5C469C', placeholder='Buscar…', count_id='cnt-panel-th')
SB_PANEL_TD = _sbph('sb-panel-td', accent_color='#5C469C', placeholder='Buscar…', count_id='cnt-panel-td')
MES     = DC.get('MES_AÑO', 'Mayo 2026')
PERIODO = DC.get('PERIODO', '')

# ── Leer parciales ─────────────────────────────────────────────────────────
p1_cr = Path('./part1_cr.html').read_text(encoding='utf-8')
p2_cr = Path('./part2_cr.html').read_text(encoding='utf-8')
p3_cr = Path('./part3_cr.html').read_text(encoding='utf-8')

p1_rnd = Path('./part1_rnd.html').read_text(encoding='utf-8')
p2_rnd = Path('./part2_rnd.html').read_text(encoding='utf-8')
p3_rnd = Path('./part3_rnd.html').read_text(encoding='utf-8')

# ── Resolver {{SHARED_HEAD}} en asset_supply_head.html ────────────────────
supply_head_path = SCRIPT_DIR / 'asset_supply_head.html'
shared_head_path = SCRIPT_DIR / 'asset_shared_head.html'

HEAD = supply_head_path.read_text(encoding='utf-8')
if shared_head_path.exists() and '{{SHARED_HEAD}}' in HEAD:
    HEAD = HEAD.replace('{{SHARED_HEAD}}', shared_head_path.read_text(encoding='utf-8'))

# ── Reemplazar placeholders ────────────────────────────────────────────────
def replace_ph(s):
    return (s
            .replace('{{WEEK_NUM}}', WK)
            .replace('{{MES_AÑO}}', MES)
            .replace('{{VOL_NUM}}', VOL_NUM)
            .replace('{{PERIODO}}', PERIODO))

HEAD   = replace_ph(HEAD)
p1_cr  = replace_ph(p1_cr);  p2_cr  = replace_ph(p2_cr);  p3_cr  = replace_ph(p3_cr)
p1_rnd = replace_ph(p1_rnd); p2_rnd = replace_ph(p2_rnd); p3_rnd = replace_ph(p3_rnd)

# ── Extraer masthead (una sola vez, arriba del switcher) ───────────────────
import re as _re2
_mh = _re2.search(r'(<header class="masthead">.*?</header>)', p1_cr, _re2.DOTALL)
MASTHEAD = _mh.group(1) if _mh else ''
p1_cr  = _re2.sub(r'<header class="masthead">.*?</header>', '', p1_cr,  flags=_re2.DOTALL)
p1_rnd = _re2.sub(r'<header class="masthead">.*?</header>', '', p1_rnd, flags=_re2.DOTALL)

# ── URL del hub (para back-link) ───────────────────────────────────────────
URL_HUB = 'https://analytics-desk.netlify.app'

# ── SVG flecha izquierda ───────────────────────────────────────────────────
ARROW_LEFT = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none" '
              'xmlns="http://www.w3.org/2000/svg">'
              '<path d="M8.5 3L4.5 7L8.5 11" stroke="currentColor" '
              'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
              '</svg>')

# ── Footer de JS compartido (TOC observer + switcher) ─────────────────────
# Extraer el bloque <script> de datos de cada p2
import re as _re

def _extract_last_script(html):
    matches = list(_re.finditer(r'<script>(.*?)</script>', html, _re.DOTALL))
    return matches[-1].group(1) if matches else ''

_cr_data_js  = _extract_last_script(p2_cr)
_rnd_data_js = _extract_last_script(p2_rnd)

# ── Pre-definir HIST_CR y HIST_RND con datos históricos ──────────────────────
# Se inyectan ANTES de demo_js_main.js para que w22_redrawCanvas los encuentre
from historico_data import HIST_DATA as _HD
import json as _json

def _hist_vals(mode, metric, canasta, actual_val=None):
    """Retorna array de 7 valores [W16,W17,W18,W19,W20,W21,W22] para canvas."""
    base = _HD.get(mode, {}).get(metric, {}).get(canasta, [])
    if actual_val is not None and len(base) >= 1:
        return base + [actual_val]
    return base

# Cargar valores actuales del pickle para el 5° punto
import pickle as _pkl
with open(f'cr_w22_data.pkl', 'rb') as _f:
    _D_cr = _pkl.load(_f)
with open(f'rnd_w22_data.pkl', 'rb') as _f:
    _D_rnd = _pkl.load(_f)

_M_cr  = _D_cr.get('M', {})
_M_rnd = _D_rnd.get('M', {})

_HIST_CR_PY = {
    'hcr-global-ef': {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w22',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'hcr-global-cv': {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get('global_w22',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'hcr-panel-ef':  {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w22',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'hcr-panel-cv':  {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get('global_w22',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'hcr-dim-ef':    {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w22',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'hcr-dim-cv':    {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get('global_w22',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-global-ef':   {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w22',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-global-cv':   {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get('global_w22',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-op-ef':       {'vals': _hist_vals('cr','eficacia','op',     round(_M_cr.get('B2B (OP)_w22',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-op-cv':       {'vals': _hist_vals('cr','convrate','op',     round(_M_cr.get('B2B (OP)_w22',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-cug-ef':      {'vals': _hist_vals('cr','eficacia','cug',    round(_M_cr.get('CUG (UOP)_w22',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-cug-cv':      {'vals': _hist_vals('cr','convrate','cug',    round(_M_cr.get('CUG (UOP)_w22',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-b2c-ef':      {'vals': _hist_vals('cr','eficacia','b2c',    round(_M_cr.get('B2C_w22',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-b2c-cv':      {'vals': _hist_vals('cr','convrate','b2c',    round(_M_cr.get('B2C_w22',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
}

_HIST_RND_PY = {
    'hrnd-global-nd':   {'vals': _hist_vals('rnd','nodispo','global', round(_M_rnd.get('global_w22',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-global-ipm':  {'vals': _hist_vals('rnd','ipm','global',     round(_M_rnd.get('global_w22',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-panel-nd':    {'vals': _hist_vals('rnd','nodispo','global', round(_M_rnd.get('global_w22',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-panel-ipm':   {'vals': _hist_vals('rnd','ipm','global',     round(_M_rnd.get('global_w22',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-dim-nd':      {'vals': _hist_vals('rnd','nodispo','global', round(_M_rnd.get('global_w22',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-dim-ipm':     {'vals': _hist_vals('rnd','ipm','global',     round(_M_rnd.get('global_w22',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-op-nd':       {'vals': _hist_vals('rnd','nodispo','op',     round(_M_rnd.get('B2B (OP)_w22',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-op-ipm':      {'vals': _hist_vals('rnd','ipm','op',         round(_M_rnd.get('B2B (OP)_w22',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-cug-nd':      {'vals': _hist_vals('rnd','nodispo','cug',    round(_M_rnd.get('CUG (UOP)_w22',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-cug-ipm':     {'vals': _hist_vals('rnd','ipm','cug',        round(_M_rnd.get('CUG (UOP)_w22',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-b2c-nd':      {'vals': _hist_vals('rnd','nodispo','b2c',    round(_M_rnd.get('B2C_w22',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-b2c-ipm':     {'vals': _hist_vals('rnd','ipm','b2c',        round(_M_rnd.get('B2C_w22',{}).get('rpm',0),0)), 'target': 650.0},
}

_HIST_CR_BY_CANASTA_PY = {
    'global': {
        'ef':  _HIST_CR_PY.get('hcr-global-ef'),
        'cv':  _HIST_CR_PY.get('hcr-global-cv'),
    },
    'b2c': {
        'ef':  _HIST_CR_PY.get('h-b2c-ef'),
        'cv':  _HIST_CR_PY.get('h-b2c-cv'),
    },
    'op': {
        'ef':  _HIST_CR_PY.get('h-op-ef'),
        'cv':  _HIST_CR_PY.get('h-op-cv'),
    },
    'cug': {
        'ef':  _HIST_CR_PY.get('h-cug-ef'),
        'cv':  _HIST_CR_PY.get('h-cug-cv'),
    },
}

_HIST_RND_BY_CANASTA_PY = {
    'global': {
        'nd':  _HIST_RND_PY.get('hrnd-global-nd'),
        'ipm': _HIST_RND_PY.get('hrnd-global-ipm'),
    },
    'b2c': {
        'nd':  _HIST_RND_PY.get('hrnd-b2c-nd'),
        'ipm': _HIST_RND_PY.get('hrnd-b2c-ipm'),
    },
    'op': {
        'nd':  _HIST_RND_PY.get('hrnd-op-nd'),
        'ipm': _HIST_RND_PY.get('hrnd-op-ipm'),
    },
    'cug': {
        'nd':  _HIST_RND_PY.get('hrnd-cug-nd'),
        'ipm': _HIST_RND_PY.get('hrnd-cug-ipm'),
    },
}

_HIST_INIT_JS = (
    f'var HIST_CR={_json.dumps(_HIST_CR_PY)};\n'
    f'var HIST_RND={_json.dumps(_HIST_RND_PY)};\n'
    f'var HIST_CR_BY_CANASTA={_json.dumps(_HIST_CR_BY_CANASTA_PY)};\n'
    f'var HIST_RND_BY_CANASTA={_json.dumps(_HIST_RND_BY_CANASTA_PY)};\n'
)

FOOTER_JS = (
    '<style>\n' + open('demo_css_w22.css', encoding='utf-8').read() + '\n' + '\n/* ═══════════════════════════════════════════════════\n   MOBILE RESPONSIVE · W22+\n   Breakpoints: 600px (teléfono), 400px (teléfono chico)\n   ═══════════════════════════════════════════════════ */\n@media (max-width: 600px) {\n\n  /* Shell */\n  .shell { padding: 0 16px; }\n\n  /* Masthead */\n  .hero h1 { font-size: clamp(24px, 7vw, 32px) !important; }\n  .hero-brand { flex-wrap: wrap; gap: 8px; }\n  .hero-brand-logo { max-width: 140px; }\n  .hero-brand-title { font-size: clamp(13px, 3.5vw, 18px); }\n\n  /* Switcher CR/RND */\n  .report-switcher { padding: 10px 16px 0; margin: 0 -16px; }\n  .switcher-btn { padding: 8px 14px; font-size: 10px; letter-spacing: .07em; }\n  .back-hub { font-size: 10px; padding: 6px 10px; }\n\n  /* Canasta tabs — scroll horizontal sin corte */\n  .canasta-tabs .tabs-row {\n    flex-wrap: nowrap;\n    overflow-x: auto;\n    -webkit-overflow-scrolling: touch;\n    scrollbar-width: none;\n    padding-bottom: 1px;\n  }\n  .canasta-tabs .tabs-row::-webkit-scrollbar { display: none; }\n  .canasta-tabs .tab-label {\n    padding: 8px 12px;\n    font-size: 9px;\n    white-space: nowrap;\n    flex-shrink: 0;\n  }\n\n  /* KPI cards — apilar verticalmente */\n  .kpis-hero { grid-template-columns: 1fr !important; gap: 12px !important; }\n  .kpi-card { padding: 16px; }\n  .kpi-val { font-size: clamp(32px, 10vw, 52px) !important; }\n\n  /* Tabs de dim (DESTINO/CORP/HOTEL/CHANNEL) */\n  .kpi-tab-labels {\n    flex-wrap: nowrap;\n    overflow-x: auto;\n    -webkit-overflow-scrolling: touch;\n    scrollbar-width: none;\n  }\n  .kpi-tab-labels::-webkit-scrollbar { display: none; }\n  .kpi-tab-label { font-size: 9px; padding: 6px 10px; white-space: nowrap; flex-shrink: 0; }\n\n  /* Tabla AR — ocultar col WoW en mobile para que quepan las celdas clave */\n  .ar-table td:nth-child(4),\n  .ar-table th:nth-child(4),\n  .ar-table td:nth-child(6),\n  .ar-table th:nth-child(6) { display: none; }\n  .ar-table td, .ar-table th { font-size: 10px; padding: 5px 4px; }\n  .sev-badge { font-size: 8px; padding: 2px 5px; }\n\n  /* Canvas histórico */\n  canvas { max-width: 100%; }\n  .hist-canvas-wrap { overflow-x: auto; }\n\n  /* Hero meta */\n  .hero-meta { grid-template-columns: 1fr 1fr !important; }\n\n  /* Searchbox */\n  .sb-wrap { max-width: 100%; }\n  .sb-input { font-size: 12px; }\n\n  /* Section head */\n  .section-head { flex-wrap: wrap; gap: 8px; }\n  .section-title { font-size: clamp(16px, 5vw, 22px); }\n\n  /* Masthead flex — mobile */\n  .masthead-inner { flex-direction: column; align-items: flex-start; gap: 8px; }\n  .masthead-left { min-width: 0; }\n  .masthead-left > div:first-child { font-size: 22px !important; white-space: nowrap; }\n  .masthead-right { flex-shrink: 0; }\n  .masthead-logo { height: 32px !important; }\n  .masthead-sub { font-size: 9px; }\n\n  /* Footer descargas — apilar botones */\n  .footer-downloads { flex-direction: column; gap: 8px; }\n  .footer-downloads a { width: 100%; text-align: center; box-sizing: border-box; }\n\n  /* Severity row — mobile: ocultar col rango */\n  .sev-row { grid-template-columns: minmax(90px,auto) 1fr 52px 40px !important; }\n  .sev-row span:nth-child(2) { display: none; }\n\n  /* Evitar scroll horizontal global */\n  body, .shell { overflow-x: hidden; }\n}\n\n@media (max-width: 400px) {\n  .shell { padding: 0 12px; }\n  .report-switcher { padding: 8px 12px 0; margin: 0 -12px; }\n  .switcher-btn { padding: 7px 10px; font-size: 9px; }\n  .kpi-val { font-size: clamp(28px, 9vw, 40px) !important; }\n  .canasta-tabs .tab-label { padding: 7px 10px; font-size: 8.5px; }\n}\n' + '\n</style>\n'
    + '<script>\n'
    + _cr_data_js + '\n'
    + _rnd_data_js + '\n'
    + _HIST_INIT_JS + '\n'      # ← HIST_CR y HIST_RND definidos ANTES de demo_js_main.js
    + open('/mnt/project/demo_js_main.js', encoding='utf-8').read() + '\n'
    + open('/mnt/project/js_override.js', encoding='utf-8').read()
    + '\n</script>'
)

# Script global separado — listener del panel replicando el patron de las cards
PANEL_LISTENER_JS = '''
/* window._injectHistAttrs — disponible globalmente */
window._injectHistAttrs = function(tbodyId, rows) {
  var tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  var trs = tbody.querySelectorAll('tr');
  trs.forEach(function(tr, i) {
    var r = rows[i]; if (!r) return;
    var name   = r[0] || '';
    var w21str = r[5] || '—';
    var wow    = r[8] || '—';
    var w21num = parseFloat(w21str.replace(/[^0-9,.]/g,'').replace(',','.'));
    if (isNaN(w21num)) return;
    var w20num = w21num;
    if (wow && wow !== '—') {
      var isUp  = wow.charAt(0) === '\u25b2';
      var delta = parseFloat(wow.replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
      w20num = isUp ? w21num - delta : w21num + delta;
    }
    tr.setAttribute('data-hist-label', name);
    tr.setAttribute('data-hist-w21',   w21num);
    tr.setAttribute('data-hist-w20',   w20num);
    tr.style.cursor = 'pointer';
  });
};

/* Patch w22_bindCanvasTip — recalcular pts con ancho real en cada mousemove */
/* Esto debe estar en script global para acceder a W22_CANVAS_CFG y w22_getTooltip */
(function patchBindCanvasTip(){
  if (typeof w22_bindCanvasTip !== 'function') {
    setTimeout(patchBindCanvasTip, 50); return;
  }
  var _orig = w22_bindCanvasTip;
  w22_bindCanvasTip = function(el, cid, cfg, pts) {
    /* Guardar cfg en el elemento para acceso en hover */
    el._tipCfg = cfg;
    /* Llamar original para registrar en W22_CANVAS_CFG/PTS */
    _orig(el, cid, cfg, pts);
    /* Sobreescribir onmousemove para recalcular pts con ancho real */
    el.onmousemove = function(e) {
      var rect = el.getBoundingClientRect();
      if (!rect || rect.width === 0) return;
      var mx = e.clientX - rect.left;
      var tip = (typeof w22_getTooltip === 'function') ? w22_getTooltip() : null;
      if (!tip) return;
      var tipCfg = el._tipCfg || cfg;
      var vals = tipCfg.vals;
      var w = rect.width;
      var livePts = vals.map(function(v,i){
        return {x: (i/(vals.length-1)) * w};
      });
      var best = -1, bestDx = 9999;
      livePts.forEach(function(p,i){ var dx=Math.abs(p.x-mx); if(dx<bestDx){bestDx=dx;best=i;} });
      if (best < 0 || bestDx > 60) { tip.style.display='none'; return; }
      var sem = tipCfg.semanas ? tipCfg.semanas[best] : ('W'+(17+best));
      var val = vals[best];
      var fmtVal = tipCfg.metric === 'ipm'
        ? ('$' + Math.round(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','))
        : val.toFixed(2) + '%';
      tip.textContent = sem + ': ' + fmtVal;
      tip.style.display = 'block';
      tip.style.left = (e.clientX + 10) + 'px';
      tip.style.top  = (e.clientY - 28) + 'px';
    };
    el.onmouseleave = function(){
      var tip = (typeof w22_getTooltip === 'function') ? w22_getTooltip() : null;
      if (tip) tip.style.display = 'none';
    };
  };
})();

/* Listener del panel — captura clicks en w22-th/w22-td, cards AR y channel divs */
document.addEventListener('click', function(e) {
  var row = e.target.closest ? e.target.closest('[data-hist-w21]') : null;
  if (!row) return;

  /* Determinar contenedor: tbody (tablas) o div canal (ar{n}-chan-div) */
  var tbody = row.closest('tbody');
  var chanDiv = row.closest('[id$="-chan-div"]');
  var container = tbody || chanDiv;
  if (!container) return;

  var validIds = ['w22-th','w22-td','ar1-th','ar1-td','ar2-th','ar2-td',
                  'ar1-chan-div','ar2-chan-div'];
  if (validIds.indexOf(container.id) === -1) return;

  /* Inferir card y cid desde el id del contenedor */
  var containerId = container.id;
  var cardNum = containerId.indexOf('ar1') === 0 ? '1' :
                containerId.indexOf('ar2') === 0 ? '2' : null;
  var card = row.getAttribute('data-hist-card') || cardNum;

  var label = row.getAttribute('data-hist-label') || '';
  var w21   = parseFloat(row.getAttribute('data-hist-w21'));
  var w20   = parseFloat(row.getAttribute('data-hist-w20'));
  if (isNaN(w21)) return;
  if (isNaN(w20)) w20 = w21;

  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
  var cid;
  if (card === '1') {
    cid = isCR ? 'hcr-panel-ef' : 'hrnd-panel-nd';
  } else if (card === '2') {
    cid = isCR ? 'hcr-panel-cv' : 'hrnd-panel-ipm';
  } else {
    var isPh = containerId === 'w22-th';
    cid = isPh ? (isCR ? 'hcr-panel-ef' : 'hrnd-panel-nd')
               : (isCR ? 'hcr-dim-ef'   : 'hrnd-dim-nd');
  }

  /* Segundo click → deseleccionar y volver a Global */
  var isAlreadySelected = row.getAttribute('data-selected') === '1';
  container.querySelectorAll('[data-hist-w21]').forEach(function(r){
    r.style.background = ''; r.removeAttribute('data-selected');
  });

  if (isAlreadySelected) {
    /* Restaurar datos globales */
    document.dispatchEvent(new CustomEvent('hist-reset', {detail: {cid: cid}}));
    return;
  }

  /* Obtener color de la canasta activa */
  var accent = (typeof cv === 'function') ? cv().col : '#5C469C';
  var accentAlpha = accent === '#333132' ? 'rgba(51,49,50,0.07)' :
                    accent === '#EA0074' ? 'rgba(234,0,116,0.07)' :
                    accent === '#FCB000' ? 'rgba(252,176,0,0.10)' :
                    accent === '#4FC3F4' ? 'rgba(79,195,244,0.10)' :
                    'rgba(92,70,156,0.07)';

  /* Highlight fila seleccionada con color de canasta */
  row.setAttribute('data-selected', '1');
  row.style.background = accentAlpha;

  /* Disparar hist-update para el canvas del panel */
  document.dispatchEvent(new CustomEvent('hist-update', {
    detail: {cid: cid, w_curr: w21, w_prev: w20, label: label}
  }));

  /* Redibujar canvas del panel con color de canasta activa */
  var fnPanel = window['histRedraw_' + cid];
  if (typeof fnPanel === 'function') {
    setTimeout(function(){ fnPanel(accent, null); }, 30);
  }

  /* Actualizar W22_CANVAS_CFG */
  function _updateCfg(id) {
    if (typeof W22_CANVAS_CFG === 'undefined' || !W22_CANVAS_CFG[id]) return;
    var oc = W22_CANVAS_CFG[id];
    var nv = oc.vals.slice();
    nv[nv.length-1] = w21;
    nv[nv.length-2] = w20;
    W22_CANVAS_CFG[id] = {vals: nv, semanas: oc.semanas || ['W16','W17','W18','W19','W20','W21','W22'], metric: oc.metric};
  }
  _updateCfg(cid);

  /* Forzar onmousemove en ambos canvas con closure sobre los vals correctos */
  [cid, globalCid].forEach(function(id) {
    var canvasEl = document.getElementById(id);
    if (!canvasEl) return;
    (function(capturedId, capturedW21, capturedW20){
      var sems = ['W16','W17','W18','W19','W20','W21','W22'];
      canvasEl.onmousemove = function(e) {
        var cfg = W22_CANVAS_CFG[capturedId];
        if (!cfg) return;
        var rect = canvasEl.getBoundingClientRect();
        var mx = e.clientX - rect.left;
        var tip = w22_getTooltip ? w22_getTooltip() : null;
        if (!tip) return;
        var w = rect.width || 400;
        var vals = cfg.vals;
        var best = -1, bestDx = 9999;
        vals.forEach(function(v,i){
          var px = (i/(vals.length-1))*w;
          var dx = Math.abs(px-mx);
          if(dx<bestDx){bestDx=dx;best=i;}
        });
        if(best<0||bestDx>40){tip.style.display='none';return;}
        var val = vals[best];
        var fmtVal = cfg.metric==='ipm'
          ? ('$'+Math.round(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g,','))
          : val.toFixed(2)+'%';
        tip.textContent = (sems[best]||('W'+(17+best)))+': '+fmtVal;
        tip.style.display='block';
        tip.style.left=(e.clientX+10)+'px';
        tip.style.top=(e.clientY-28)+'px';
      };
      canvasEl.onmouseleave = function(){
        var tip = w22_getTooltip ? w22_getTooltip() : null;
        if(tip) tip.style.display='none';
      };
    })(id, w21, w20);
  });
});

/* Inyectar inmediatamente en las filas ya renderizadas */
(function tryInject(){
  if (typeof w22_renderTable === 'undefined' || typeof data === 'undefined') {
    setTimeout(tryInject, 50); return;
  }
  var dd = data();
  var hrows = (dd.hotels_crit || dd.hotels_dnc || dd.hotels || []);
  var drows = (dd.dims || []);
  window._injectHistAttrs('w22-th', hrows);
  window._injectHistAttrs('w22-td', drows);
})();
'''

# Script para vincular pestañas de hotel con datos
TAB_BINDING_JS = '''
(function() {
    /* Mapa de pestañas por modo */
    var tabMapCR  = [
        { dataKey: 'hotels_crit' },
        { dataKey: 'hotels_br'   },
        { dataKey: 'hotels_sc'   },
        { dataKey: 'hotels_cv'   }
    ];
    var tabMapRND = [
        { dataKey: 'hotels_dnc' },
        { dataKey: 'hotels_br'  },
        { dataKey: 'hotels_sc'  }
    ];
    
    function getRows(idx) {
        var mode = (typeof W !== 'undefined') ? W.mode : 'cr';
        var canasta = (typeof W !== 'undefined') ? (W.canasta || 'global') : 'global';
        if (mode === 'rnd') {
            var d = (typeof RND_D !== 'undefined') ? (RND_D[canasta] || RND_D.global || {}) : {};
            var key = (tabMapRND[idx] || tabMapRND[0]).dataKey;
            return d[key] || d.hotels || [];
        } else {
            /* CR: usar CR_HOTELS para tabs filtrados */
            if (typeof CR_HOTELS !== 'undefined' && CR_HOTELS[canasta]) {
                var key = (tabMapCR[idx] || tabMapCR[0]).dataKey;
                return CR_HOTELS[canasta][key] || CR_HOTELS.global[key] || [];
            }
            var d2 = (typeof CR_D !== 'undefined') ? (CR_D[canasta] || CR_D.global || {}) : {};
            var key2 = (tabMapCR[idx] || tabMapCR[0]).dataKey;
            return d2[key2] || d2.hotels || [];
        }
    }
    
    function initTabs() {
        var ph = document.getElementById('w22-ph');
        if (!ph) return;
        var labels = ph.querySelectorAll('label');
        if (!labels.length) return;
        
        /* Cargar tab inicial */
        var rows0 = getRows(0);
        if (rows0.length) w22_renderTable('w22-th', 'w22-th-more', rows0, false);
        
        /* Vincular clicks */
        labels.forEach(function(label, idx) {
            label.addEventListener('click', function() {
                labels.forEach(function(l) { l.classList.remove('active'); });
                label.classList.add('active');
                var rows = getRows(idx);
                if (rows.length) w22_renderTable('w22-th', 'w22-th-more', rows, false);
            });
        });
    }
    
    /* Re-inicializar cuando cambia el modo CR ↔ RND */
    document.addEventListener('mode-changed', function() {
        setTimeout(initTabs, 50);
    });
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function(){ setTimeout(initTabs, 50); });
    } else {
        setTimeout(initTabs, 50);
    }
    
    /* Exponer para que w22_setMode pueda reinicializar */
    window._reinitTabs = initTabs;
})();
'''

GLOBAL_PANEL_SCRIPT = '<script>' + TAB_BINDING_JS + '</script>\n<script>' + PANEL_LISTENER_JS + '</script>\n'

SECTION_DIVIDER = ''  # W21+ — sin divisor

SWITCHER = f'''<div style="padding-top:10px;">
<div class="w22-seg">
  <button class="w22-seg-btn on" id="mode-cr" onclick="w22_setMode('cr',this)">CheckRates</button>
  <button class="w22-seg-btn" id="mode-rnd" onclick="w22_setMode('rnd',this)">Rates No Dispo</button>
</div>
</div>
<div id="w22-filter-wrap" style="margin-top:8px;">
<div class="cfb">
  <div class="cfb-lbl">Canasta</div>
  <div class="cfb-chips">
    <div class="c-chip active" id="chip-global" onclick="w22_setC('global',this)">Global</div>
    <div class="c-chip" id="chip-b2c"    onclick="w22_setC('b2c',this)">B2C</div>
    <div class="c-chip" id="chip-op"     onclick="w22_setC('op',this)">Opaco</div>
    <div class="c-chip" id="chip-cug"    onclick="w22_setC('cug',this)">Ultra Opaco</div>
  </div>
  <div class="cfb-kpi">
    <div class="cfb-kpi-item">
      <div class="cfb-kpi-lbl" id="w22-strip-lbl1">Eficacia</div>
      <div class="cfb-kpi-val" id="w22-strip-ef" style="color:#5C469C;">—</div>
    </div>
    <div class="cfb-sep"></div>
    <div class="cfb-kpi-item">
      <div class="cfb-kpi-lbl" id="w22-strip-lbl2">Conv Rate</div>
      <div class="cfb-kpi-val" id="w22-strip-cv" style="color:#5C469C;">—</div>
    </div>
    <div class="cfb-sep"></div>
    <div class="cfb-kpi-item">
      <div class="cfb-kpi-lbl">Severity</div>
      <span class="sev-badge" id="w22-strip-band" style="font-size:9px;font-weight:700;padding:3px 9px;text-transform:uppercase;letter-spacing:.04em;outline:1px solid rgba(0,0,0,.12);display:inline-block;margin-top:3px;">—</span>
    </div>
  </div>
</div>
</div>'''

# ── Contenedores compartidos (una sola vez, fuera de section-cr / section-rnd) ──
# El JS los reescribe según modo (CR/RND) y canasta activa
SHARED_CONTAINERS = f'''
<section style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head" style="margin-bottom:16px;"><div>
<h2 class="section-title">Análisis de Rendimiento</h2>
<span class="section-subtitle" style="color:var(--accent)">Top hoteles y dimensiones · canasta activa</span>
</div></div>

<!-- Switcher CR/RND — mismo componente w22-seg que el de las cards -->
<div style="margin-bottom:4px;">
  <div class="w22-seg" id="ar-seg">
    <button class="w22-seg-btn on" id="ar-btn-cr"
      onclick="w22_setMode('cr',document.getElementById('mode-cr'))">CheckRates</button>
    <button class="w22-seg-btn" id="ar-btn-rnd"
      onclick="w22_setMode('rnd',document.getElementById('mode-rnd'))">Rates No Dispo</button>
  </div>
</div>
<!-- Barra de canastas — misma .cfb que la barra de cards, con IDs ar-* -->
<div id="ar-filter-wrap" style="margin-bottom:16px;">
<div class="cfb">
  <div class="cfb-lbl">Canasta</div>
  <div class="cfb-chips">
    <div class="c-chip active" id="ar-chip-global" onclick="w22_setC('global',document.getElementById('chip-global'))">Global</div>
    <div class="c-chip"        id="ar-chip-b2c"    onclick="w22_setC('b2c',document.getElementById('chip-b2c'))">B2C</div>
    <div class="c-chip"        id="ar-chip-op"     onclick="w22_setC('op',document.getElementById('chip-op'))">Opaco</div>
    <div class="c-chip"        id="ar-chip-cug"    onclick="w22_setC('cug',document.getElementById('chip-cug'))">Ultra Opaco</div>
  </div>
  <div class="cfb-kpi">
    <div class="cfb-kpi-item">
      <div class="cfb-kpi-lbl" id="ar-strip-lbl1">Eficacia</div>
      <div class="cfb-kpi-val" id="ar-strip-ef" style="color:#5C469C;">—</div>
    </div>
    <div class="cfb-sep"></div>
    <div class="cfb-kpi-item">
      <div class="cfb-kpi-lbl" id="ar-strip-lbl2">Conv Rate</div>
      <div class="cfb-kpi-val" id="ar-strip-cv" style="color:#5C469C;">—</div>
    </div>
    <div class="cfb-sep"></div>
    <div class="cfb-kpi-item">
      <div class="cfb-kpi-lbl">Severity</div>
      <span class="sev-badge" id="ar-strip-band" style="font-size:9px;font-weight:700;padding:3px 9px;text-transform:uppercase;letter-spacing:.04em;outline:1px solid rgba(0,0,0,.12);display:inline-block;margin-top:3px;">—</span>
    </div>
  </div>
</div>
</div>

<!-- Grid 2 cards: Métrica 1 (Ef/ND) + Métrica 2 (CV/IPM) -->
<div class="ar-cards-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:14px;">

  <!-- ── CARD 1: Eficacia / NoDispo ── -->
  <div class="kpi-card" style="border:1px solid var(--rule);padding:0;border-radius:3px;background:var(--paper);">
    <!-- Header título -->
    <div style="padding:12px 16px 0;">
      <div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;" id="ar-card1-lbl">Eficacia</div>
      <div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
        <div>
          <div id="ar-kpi-1" style="font-size:36px;font-weight:700;letter-spacing:-.02em;color:var(--accent);line-height:1;">—</div>
          <div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">Vol. <span id="ar1-vol">—</span> · vs sem. ant. <span id="ar1-wow-pill"></span></div>
          <div style="margin-top:4px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);"><span id="ar1-trafico" style="font-weight:600;color:var(--ink-soft);">—</span><span id="ar1-trafico-wow"></span></div>
        </div>
        <div style="padding-top:4px;"><span id="ar1-badge" class="sev-badge" style="font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:6px 12px;border-radius:3px;display:inline-flex;align-items:center;white-space:nowrap;">—</span></div>
      </div>
      <div id="ar1-gauge" style="display:flex;gap:2px;margin-top:10px;"></div>
      <div id="ar1-wowbox" style="margin-top:8px;background:var(--paper-soft);border-radius:3px;padding:6px;display:flex;align-items:stretch;gap:6px;"></div>
    </div>
    <!-- Nivel 1: Por Hotel / Por Dimensión — formato folder -->
    <div class="tabs-row" style="gap:2px;border-bottom:1px solid var(--rule);padding:0 0 0 4px;align-items:flex-end;margin-top:10px;margin-bottom:0;">
      <div id="ar1-vch-h" onclick="ar_setView(1,'hotel')"
        class="tab-label tab-label-active" style="border-radius:6px 6px 0 0;cursor:pointer;">🏨 Por Hotel</div>
      <div id="ar1-vch-d" onclick="ar_setView(1,'dim')"
        class="tab-label" style="border-radius:6px 6px 0 0;cursor:pointer;">📊 Por Dimensión</div>
    </div>
    <!-- Panel Por Hotel card 1 -->
    <div id="ar1-ph" style="padding:12px 16px 0;">
      <div class="tabs-row" style="margin-top:0;margin-bottom:10px;">
        <label class="tab-label tab-label-active" onclick="ar_setHotelTab(1,'crit',this)" id="ar1-tab-1">Críticos</label>
        <label class="tab-label" onclick="ar_setHotelTab(1,'br',this)"   id="ar1-tab-2">Bajo Rend.</label>
        <label class="tab-label" onclick="ar_setHotelTab(1,'sc',this)"   id="ar1-tab-3">Sin Conv.</label>
        <label class="tab-label" onclick="ar_setHotelTab(1,'cv',this)"   id="ar1-tab-4" id="ar1-tab-cv">Menor CV</label>
      </div>
      <table style="width:100%;border-collapse:collapse;table-layout:fixed;">
        <colgroup><col/><col style="width:90px"/><col style="width:60px"/><col style="width:42px"/><col style="width:76px"/><col style="width:42px"/></colgroup>
        <thead><tr style="border-bottom:2px solid var(--accent);">
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);text-align:left;padding:5px 0 5px 8px;" id="ar1-th-lbl">Hotel</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:left;padding:5px 4px;">Severity</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;">Tráfico</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 2px;">WoW</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;" id="ar1-col-m">Eficacia</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 6px 5px 2px;">WoW</th>
        </tr></thead>
        <tbody id="ar1-th"></tbody>
      </table>
      <div style="text-align:center;margin-top:8px;">
        <button id="ar1-th-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;"></button>
      </div>
    </div>
    <!-- Panel Por Dimensión card 1 -->
    <div id="ar1-pd" style="display:none;padding:12px 16px 0;">
      <div class="tabs-row" style="margin-top:0;margin-bottom:10px;">
        <label class="tab-label tab-label-active" onclick="ar_setDim(1,'corp');w22_iTab(this);" id="ar1-dim-corp">Corporativo</label>
        <label class="tab-label" onclick="ar_setDim(1,'dest');w22_iTab(this);" id="ar1-dim-dest">Destino</label>
        <label class="tab-label" onclick="ar_setDim(1,'chan');w22_iTab(this);" id="ar1-dim-chan">Channel</label>
      </div>
      <table style="width:100%;border-collapse:collapse;table-layout:fixed;">
        <colgroup><col/><col style="width:90px"/><col style="width:60px"/><col style="width:42px"/><col style="width:76px"/><col style="width:42px"/></colgroup>
        <thead><tr style="border-bottom:2px solid var(--accent);">
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);text-align:left;padding:5px 0 5px 8px;" id="ar1-td-lbl">Corporativo</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:left;padding:5px 4px;">Severity</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;">Tráfico</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 2px;">WoW</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;" id="ar1-td-col-m">Eficacia</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 6px 5px 2px;">WoW</th>
        </tr></thead>
        <tbody id="ar1-td"></tbody>
      </table>
      <div style="text-align:center;margin-top:8px;">
        <button id="ar1-td-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;"></button>
      </div>
    </div>
    <!-- Canvas histórico card 1 -->
    <div style="padding:0 16px 16px;">
      <div id="ar1-hist-cr" style="margin-top:12px;display:block;">{HIST_CR_PANEL}</div>
      <div id="ar1-hist-rnd" style="margin-top:12px;display:none;">{HIST_RND_PANEL}</div>
    </div>
  </div>

  <!-- ── CARD 2: Conv Rate / IPM ── -->
  <div class="kpi-card" style="border:1px solid var(--rule);padding:0;border-radius:3px;background:var(--paper);">
    <!-- Header título -->
    <div style="padding:12px 16px 0;">
      <div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;" id="ar-card2-lbl">Conv Rate</div>
      <div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
        <div>
          <div id="ar-kpi-2" style="font-size:36px;font-weight:700;letter-spacing:-.02em;color:var(--accent);line-height:1;">—</div>
          <div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">Vol. <span id="ar2-vol">—</span> · vs sem. ant. <span id="ar2-wow-pill"></span></div>
          <div style="margin-top:4px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);"><span id="ar2-trafico" style="font-weight:600;color:var(--ink-soft);">—</span><span id="ar2-trafico-wow"></span></div>
        </div>
        <div style="padding-top:4px;"><span id="ar2-badge" class="sev-badge" style="font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:6px 12px;border-radius:3px;display:inline-flex;align-items:center;white-space:nowrap;">—</span></div>
      </div>
      <div id="ar2-gauge" style="display:flex;gap:2px;margin-top:10px;"></div>
      <div id="ar2-wowbox" style="margin-top:8px;background:var(--paper-soft);border-radius:3px;padding:6px;display:flex;align-items:stretch;gap:6px;"></div>
    </div>
    <!-- Nivel 1: Por Hotel / Por Dimensión — formato folder -->
    <div class="tabs-row" style="gap:2px;border-bottom:1px solid var(--rule);padding:0 0 0 4px;align-items:flex-end;margin-top:10px;margin-bottom:0;">
      <div id="ar2-vch-h" onclick="ar_setView(2,'hotel')"
        class="tab-label tab-label-active" style="border-radius:6px 6px 0 0;cursor:pointer;">🏨 Por Hotel</div>
      <div id="ar2-vch-d" onclick="ar_setView(2,'dim')"
        class="tab-label" style="border-radius:6px 6px 0 0;cursor:pointer;">📊 Por Dimensión</div>
    </div>
    <!-- Panel Por Hotel card 2 -->
    <div id="ar2-ph" style="padding:12px 16px 0;">
      <div class="tabs-row" style="margin-top:0;margin-bottom:10px;">
        <label class="tab-label tab-label-active" onclick="ar_setHotelTab(2,'crit',this)" id="ar2-tab-1">Críticos</label>
        <label class="tab-label" onclick="ar_setHotelTab(2,'br',this)"   id="ar2-tab-2">Bajo Rend.</label>
        <label class="tab-label" onclick="ar_setHotelTab(2,'sc',this)"   id="ar2-tab-3">Sin Conv.</label>
        <label class="tab-label" onclick="ar_setHotelTab(2,'cv',this)"   id="ar2-tab-4">Menor CV</label>
      </div>
      <table style="width:100%;border-collapse:collapse;table-layout:fixed;">
        <colgroup><col/><col style="width:90px"/><col style="width:60px"/><col style="width:42px"/><col style="width:76px"/><col style="width:42px"/></colgroup>
        <thead><tr style="border-bottom:2px solid var(--accent);">
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);text-align:left;padding:5px 0 5px 8px;" id="ar2-th-lbl">Hotel</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:left;padding:5px 4px;">Severity</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;">Tráfico</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 2px;">WoW</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;" id="ar2-col-m">Conv Rate</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 6px 5px 2px;">WoW</th>
        </tr></thead>
        <tbody id="ar2-th"></tbody>
      </table>
      <div style="text-align:center;margin-top:8px;">
        <button id="ar2-th-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;"></button>
      </div>
    </div>
    <!-- Panel Por Dimensión card 2 -->
    <div id="ar2-pd" style="display:none;padding:12px 16px 0;">
      <div class="tabs-row" style="margin-top:0;margin-bottom:10px;">
        <label class="tab-label tab-label-active" onclick="ar_setDim(2,'corp');w22_iTab(this);" id="ar2-dim-corp">Corporativo</label>
        <label class="tab-label" onclick="ar_setDim(2,'dest');w22_iTab(this);" id="ar2-dim-dest">Destino</label>
        <label class="tab-label" onclick="ar_setDim(2,'chan');w22_iTab(this);" id="ar2-dim-chan">Channel</label>
      </div>
      <table style="width:100%;border-collapse:collapse;table-layout:fixed;">
        <colgroup><col/><col style="width:90px"/><col style="width:60px"/><col style="width:42px"/><col style="width:76px"/><col style="width:42px"/></colgroup>
        <thead><tr style="border-bottom:2px solid var(--accent);">
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);text-align:left;padding:5px 0 5px 8px;" id="ar2-td-lbl">Corporativo</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:left;padding:5px 4px;">Severity</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;">Tráfico</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 2px;">WoW</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 4px;" id="ar2-td-col-m">Conv Rate</th>
          <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:5px 6px 5px 2px;">WoW</th>
        </tr></thead>
        <tbody id="ar2-td"></tbody>
      </table>
      <div style="text-align:center;margin-top:8px;">
        <button id="ar2-td-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;"></button>
      </div>
    </div>
    <!-- Canvas histórico card 2 -->
    <div style="padding:0 16px 16px;">
      <div id="ar2-hist-cr" style="margin-top:12px;display:block;">{HIST_CR_PANEL_CV}</div>
      <div id="ar2-hist-rnd" style="margin-top:12px;display:none;">{HIST_RND_PANEL_IPM}</div>
    </div>
  </div>

</div><!-- /grid 2 cards -->
</section>

<section style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Resumen Ejecutivo</h2>
<span class="section-subtitle" style="color:var(--accent)">Canasta activa · 10 findings</span>
</div></div>
<ol class="exec-bullets" id="w22-re-list"></ol>
<div class="re-wrap"><button class="re-btn" id="w22-re-btn" onclick="w22_toggleRE()">Ver 5 más ↓</button></div>
</section>

<section style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Plan de Acción</h2>
<span class="section-subtitle" id="w22-plan-sub" style="color:var(--accent)">Canasta activa · W{VOL_NUM}</span>
</div></div>
<div class="p-grid" id="w22-pg" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px;"></div>
<div style="margin-top:14px;padding:14px 18px;background:var(--paper-soft);border:1px solid var(--rule);border-left:3px solid var(--ink-muted);">
  <div style="font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:10px;">Carryover W{int(VOL_NUM)-1}</div>
  <div id="w22-co"></div>
</div>
</section>
'''

final = (
    '<!DOCTYPE html>\n<html lang="es">\n'
    + HEAD + '\n'
    + '<body>\n'
    + '''<div id="supply-loading" style="position:fixed;inset:0;background:#F8F4EC;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:9999;gap:20px;">
  <img src="data:image/png;base64,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" alt="PriceTravel" style="height:36px;filter:saturate(0) brightness(0);opacity:.85;">
  <div style="width:120px;height:2px;background:#C9C1B0;border-radius:2px;overflow:hidden;">
    <div id="supply-loading-bar" style="width:0%;height:100%;background:#161616;border-radius:2px;transition:width .4s ease;"></div>
  </div>
  <div style="font-size:9px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#8A8377;">LOADING</div>
</div>
<script>
(function(){
  var bar = document.getElementById('supply-loading-bar');
  var pct = 0;
  var iv = setInterval(function(){
    pct = Math.min(pct + (90-pct)*0.08 + 0.5, 90);
    if(bar) bar.style.width = pct.toFixed(1)+'%';
  }, 80);
  window.addEventListener('load', function(){
    clearInterval(iv);
    if(bar) bar.style.width = '100%';
    setTimeout(function(){
      var el = document.getElementById('supply-loading');
      if(el){ el.style.opacity='0'; el.style.transition='opacity .3s'; setTimeout(function(){ el.style.display='none'; },300); }
    }, 150);
  });
})();
</script>
'''
    + '<div class="shell">\n'
    + MASTHEAD + '\n'
    + SWITCHER + '\n'
    # ── KPI heroes (se muestran/ocultan con el modo) ──
    + '<div id="w22-kpis-cr">\n'
    + p1_cr + '\n'
    + p2_cr + '\n'   # severity CR + JSON CR
    + p3_cr + '\n'
    + '</section>\n'  # cierra section-cr (abierta por p1_cr)
    + '</div>\n'      # cierra w22-kpis-cr
    + '<div id="w22-kpis-rnd" style="display:none;">\n'
    + p1_rnd + '\n'
    + p2_rnd + '\n'  # severity RND + JSON RND
    + p3_rnd + '\n'
    + '</section>\n'  # cierra section-rnd (abierta por p1_rnd)
    + '</div>\n'      # cierra w22-kpis-rnd
    # ── Contenedores compartidos (una sola vez) ──
    + SHARED_CONTAINERS
    + '\n</div>\n'   # cierra shell
    + FOOTER_JS
    + '''
<script>
// Configurar HIST_CR y HIST_RND para tooltip
if (typeof HIST_DATA !== 'undefined') {
    window.HIST_CR = {};
    window.HIST_RND = {};
    
    // Mapear datos CR
    if (HIST_DATA.cr && HIST_DATA.cr.eficacia) {
        window.HIST_CR['h-global-ef'] = { vals: HIST_DATA.cr.eficacia.global, metric: 'eficacia' };
        window.HIST_CR['h-global-cv'] = { vals: HIST_DATA.cr.convrate.global, metric: 'convrate' };
        window.HIST_CR['h-op-ef'] = { vals: HIST_DATA.cr.eficacia.op, metric: 'eficacia' };
        window.HIST_CR['h-op-cv'] = { vals: HIST_DATA.cr.convrate.op, metric: 'convrate' };
        window.HIST_CR['h-cug-ef'] = { vals: HIST_DATA.cr.eficacia.cug, metric: 'eficacia' };
        window.HIST_CR['h-cug-cv'] = { vals: HIST_DATA.cr.convrate.cug, metric: 'convrate' };
        window.HIST_CR['h-b2c-ef'] = { vals: HIST_DATA.cr.eficacia.b2c, metric: 'eficacia' };
        window.HIST_CR['h-b2c-cv'] = { vals: HIST_DATA.cr.convrate.b2c, metric: 'convrate' };
    }
    
    // Mapear datos RND
    if (HIST_DATA.rnd && HIST_DATA.rnd.nodispo) {
        window.HIST_RND['hrnd-global-nd'] = { vals: HIST_DATA.rnd.nodispo.global, metric: 'nodispo' };
        window.HIST_RND['hrnd-global-ipm'] = { vals: HIST_DATA.rnd.ipm.global, metric: 'ipm' };
        window.HIST_RND['hrnd-op-nd'] = { vals: HIST_DATA.rnd.nodispo.op, metric: 'nodispo' };
        window.HIST_RND['hrnd-op-ipm'] = { vals: HIST_DATA.rnd.ipm.op, metric: 'ipm' };
        window.HIST_RND['hrnd-cug-nd'] = { vals: HIST_DATA.rnd.nodispo.cug, metric: 'nodispo' };
        window.HIST_RND['hrnd-cug-ipm'] = { vals: HIST_DATA.rnd.ipm.cug, metric: 'ipm' };
        window.HIST_RND['hrnd-b2c-nd'] = { vals: HIST_DATA.rnd.nodispo.b2c, metric: 'nodispo' };
        window.HIST_RND['hrnd-b2c-ipm'] = { vals: HIST_DATA.rnd.ipm.b2c, metric: 'ipm' };
    }
    
    /* HIST_CR y HIST_RND configurados para tooltip */
}
</script>
'''
    + GLOBAL_PANEL_SCRIPT
    + f'''
<div class="footer-bar" style="width:100%;margin:40px 0 0;padding:20px 24px;background:var(--paper);border-top:1px solid var(--rule);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;box-sizing:border-box;">
  <div class="footer-downloads" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
    <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--ink-muted);">Descargas W{VOL_NUM}</span>
    <a href="../../checkrates/week-{VOL_NUM}/Analisis_CheckRates_W{VOL_NUM}.xlsx" style="font-size:11px;font-weight:700;color:#fff;text-decoration:none;padding:7px 16px;background:var(--ink);border-radius:3px;">⬇ Excel CheckRates</a>
    <a href="../../rates-nodispo/week-{VOL_NUM}/Analisis_RatesNoDispo_W{VOL_NUM}.xlsx" style="font-size:11px;font-weight:700;color:#fff;text-decoration:none;padding:7px 16px;background:var(--ink);border-radius:3px;">⬇ Excel Rates No Dispo</a>
  </div>
  <a href="../../index.html" style="font-size:12px;font-weight:700;color:var(--ink);text-decoration:none;">← Volver al Hub</a>
</div>
'''
    + '\n</body>\n</html>\n'
)

# ── Guardar ────────────────────────────────────────────────────────────────
OUTPUTS.mkdir(parents=True, exist_ok=True)
out = OUTPUTS / f'SUPPLY_W{VOL_NUM}.html'
out.write_text(final, encoding='utf-8')
size_kb = out.stat().st_size / 1024
print(f'✅ SUPPLY_{WK} ensamblado: {out}')
print(f'   Tamaño: {size_kb:.0f} KB · {len(final):,} chars')
print(f'   CR: {len(p1_cr)+len(p2_cr)+len(p3_cr):,} chars')
print(f'   RND: {len(p1_rnd)+len(p2_rnd)+len(p3_rnd):,} chars')
