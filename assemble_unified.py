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
# Bookability pickle — opcional (puede no existir en pipelines anteriores)
_bk_path = os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
if os.path.exists(_bk_path):
    with open(_bk_path, 'rb') as _f:
        DB = pickle.load(_f)
else:
    DB = None

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
# Histórico Bookability para card AR3
if DB is not None:
    _bk_vals = [DB['hist_by_week'][w]['bk'] * 100 for w in ['W16','W17','W18','W19','W20','W21','W22','W23'] if w in DB['hist_by_week']]
    _bk_val_curr = _bk_vals[-1] if _bk_vals else 98.43
    _bk_banda_str = DB.get('banda_global', 'Exitosa').capitalize()
    HIST_BK_PANEL = _rh('bk', 'bookability', _bk_banda_str, DB.get('bk_global', 0), 'h-ar3-bk-global')
else:
    HIST_BK_PANEL = ''

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

def _strip_last_script(html):
    """Elimina el último <script>…</script> del HTML (ya embebido en FOOTER_JS)."""
    matches = list(_re.finditer(r'<script>(.*?)</script>', html, _re.DOTALL))
    if not matches:
        return html
    last = matches[-1]
    return html[:last.start()] + html[last.end():]

_cr_data_js  = _extract_last_script(p2_cr)
_rnd_data_js = _extract_last_script(p2_rnd)

# ── Pre-definir HIST_CR y HIST_RND con datos históricos ──────────────────────
# Se inyectan ANTES de demo_js_main.js para que w22_redrawCanvas los encuentre
from historico_data import HIST_DATA as _HD, SEMANAS as _HSEM
import json as _json

# ── Semanas históricas dinámicas (ventana móvil, última = semana actual) ──
# Fuente única de verdad: historico_data.SEMANAS (p.ej. W17-W24). Reemplaza los
# hardcodeos W16-W23 de _SEMANAS_HIST / AR3 / fallbacks (se auto-ajusta cada semana).
_SEM_JS = _json.dumps(list(_HSEM))
_SEM_BASE = int(str(_HSEM[0])[1:]) if _HSEM else 17
# Serie BK real por semana (W17-W24) desde el pickle — fuente autoritativa, última = W24
try:
    _AR3_BK = [round(DB['hist_by_week'][w]['bk'] * 100, 2) for w in _HSEM if DB and w in DB.get('hist_by_week', {})]
except Exception:
    _AR3_BK = []
_AR3_BK_JS = _json.dumps(_AR3_BK) if _AR3_BK else None

def _hist_vals(mode, metric, canasta, actual_val=None):
    """Retorna array de 7 valores [W16,W17,W18,W19,W20,W21,W22] para canvas."""
    base = _HD.get(mode, {}).get(metric, {}).get(canasta, [])
    if actual_val is not None and len(base) >= 1:
        return base + [actual_val]
    return base

# Cargar valores actuales del pickle para el 5° punto
# DC y DR ya cargados arriba desde los pickles correctos
import pickle as _pkl
_D_cr  = DC
_D_rnd = DR

_M_cr  = _D_cr.get('M', {})
_M_rnd = _D_rnd.get('M', {})

_HIST_CR_PY = {
    'hcr-global-ef': {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'hcr-global-cv': {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'hcr-panel-ef':  {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'hcr-panel-cv':  {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'hcr-dim-ef':    {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'hcr-dim-cv':    {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-global-ef':   {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-global-cv':   {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get(f'global_w{VOL_NUM}',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-op-ef':       {'vals': _hist_vals('cr','eficacia','op',     round(_M_cr.get(f'B2B (OP)_w{VOL_NUM}',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-op-cv':       {'vals': _hist_vals('cr','convrate','op',     round(_M_cr.get(f'B2B (OP)_w{VOL_NUM}',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-cug-ef':      {'vals': _hist_vals('cr','eficacia','cug',    round(_M_cr.get(f'CUG (UOP)_w{VOL_NUM}',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-cug-cv':      {'vals': _hist_vals('cr','convrate','cug',    round(_M_cr.get(f'CUG (UOP)_w{VOL_NUM}',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-b2c-ef':      {'vals': _hist_vals('cr','eficacia','b2c',    round(_M_cr.get(f'B2C_w{VOL_NUM}',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-b2c-cv':      {'vals': _hist_vals('cr','convrate','b2c',    round(_M_cr.get(f'B2C_w{VOL_NUM}',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
}

_HIST_RND_PY = {
    'hrnd-global-nd':   {'vals': _hist_vals('rnd','nodispo','global', round(_M_rnd.get(f'global_w{VOL_NUM}',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-global-ipm':  {'vals': _hist_vals('rnd','ipm','global',     round(_M_rnd.get(f'global_w{VOL_NUM}',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-panel-nd':    {'vals': _hist_vals('rnd','nodispo','global', round(_M_rnd.get(f'global_w{VOL_NUM}',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-panel-ipm':   {'vals': _hist_vals('rnd','ipm','global',     round(_M_rnd.get(f'global_w{VOL_NUM}',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-dim-nd':      {'vals': _hist_vals('rnd','nodispo','global', round(_M_rnd.get(f'global_w{VOL_NUM}',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-dim-ipm':     {'vals': _hist_vals('rnd','ipm','global',     round(_M_rnd.get(f'global_w{VOL_NUM}',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-op-nd':       {'vals': _hist_vals('rnd','nodispo','op',     round(_M_rnd.get(f'B2B (OP)_w{VOL_NUM}',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-op-ipm':      {'vals': _hist_vals('rnd','ipm','op',         round(_M_rnd.get(f'B2B (OP)_w{VOL_NUM}',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-cug-nd':      {'vals': _hist_vals('rnd','nodispo','cug',    round(_M_rnd.get(f'CUG (UOP)_w{VOL_NUM}',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-cug-ipm':     {'vals': _hist_vals('rnd','ipm','cug',        round(_M_rnd.get(f'CUG (UOP)_w{VOL_NUM}',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-b2c-nd':      {'vals': _hist_vals('rnd','nodispo','b2c',    round(_M_rnd.get(f'B2C_w{VOL_NUM}',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-b2c-ipm':     {'vals': _hist_vals('rnd','ipm','b2c',        round(_M_rnd.get(f'B2C_w{VOL_NUM}',{}).get('rpm',0),0)), 'target': 650.0},
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
    '<style>\n' + open('demo_css_w22.css', encoding='utf-8').read() + '\n' + '\n/* ═══════════════════════════════════════════════════\n   MOBILE RESPONSIVE · W22+\n   Breakpoints: 600px (teléfono), 400px (teléfono chico)\n   ═══════════════════════════════════════════════════ */\n@media (max-width: 600px) {\n\n  /* Shell */\n  .shell { padding: 0 16px; }\n\n  /* Masthead */\n  .hero h1 { font-size: clamp(24px, 7vw, 32px) !important; }\n  .hero-brand { flex-wrap: wrap; gap: 8px; }\n  .hero-brand-logo { max-width: 140px; }\n  .hero-brand-title { font-size: clamp(13px, 3.5vw, 18px); }\n\n  /* Switcher CR/RND */\n  .report-switcher { padding: 10px 16px 0; margin: 0 -16px; }\n  .switcher-btn { padding: 8px 14px; font-size: 10px; letter-spacing: .07em; }\n  .back-hub { font-size: 10px; padding: 6px 10px; }\n\n  /* Canasta tabs — scroll horizontal sin corte */\n  .canasta-tabs .tabs-row {\n    flex-wrap: nowrap;\n    overflow-x: auto;\n    -webkit-overflow-scrolling: touch;\n    scrollbar-width: none;\n    padding-bottom: 1px;\n  }\n  .canasta-tabs .tabs-row::-webkit-scrollbar { display: none; }\n  .canasta-tabs .tab-label {\n    padding: 8px 12px;\n    font-size: 9px;\n    white-space: nowrap;\n    flex-shrink: 0;\n  }\n\n  /* KPI cards — apilar verticalmente */\n  .kpis-hero { grid-template-columns: 1fr !important; gap: 12px !important; }\n  .kpi-card { padding: 16px; }\n  .kpi-val { font-size: clamp(32px, 10vw, 52px) !important; }\n\n  /* Tabs de dim (DESTINO/CORP/HOTEL/CHANNEL) */\n  .kpi-tab-labels {\n    flex-wrap: nowrap;\n    overflow-x: auto;\n    -webkit-overflow-scrolling: touch;\n    scrollbar-width: none;\n  }\n  .kpi-tab-labels::-webkit-scrollbar { display: none; }\n  .kpi-tab-label { font-size: 9px; padding: 6px 10px; white-space: nowrap; flex-shrink: 0; }\n\n  /* Tabla AR — ocultar col WoW en mobile para que quepan las celdas clave */\n  .ar-table td:nth-child(4),\n  .ar-table th:nth-child(4),\n  .ar-table td:nth-child(6),\n  .ar-table th:nth-child(6) { display: none; }\n  .ar-table td, .ar-table th { font-size: 10px; padding: 5px 4px; }\n  .sev-badge { font-size: 8px; padding: 2px 5px; }\n\n  /* Canvas histórico */\n  canvas { max-width: 100%; }\n  .hist-canvas-wrap { overflow-x: auto; }\n\n  /* Hero meta */\n  .hero-meta { grid-template-columns: 1fr 1fr !important; }\n\n  /* Searchbox */\n  .sb-wrap { max-width: 100%; }\n  .sb-input { font-size: 12px; }\n\n  /* Section head */\n  .section-head { flex-wrap: wrap; gap: 8px; }\n  .section-title { font-size: clamp(16px, 5vw, 22px); }\n\n  /* Masthead flex — mobile */\n  .masthead-inner { flex-direction: column; align-items: flex-start; gap: 8px; }\n  .masthead-left { min-width: 0; }\n  .masthead-left > div:first-child { font-size: 22px !important; white-space: nowrap; }\n  .masthead-right { flex-shrink: 0; }\n  .masthead-logo { height: 32px !important; }\n  .masthead-sub { font-size: 9px; }\n\n  /* Footer descargas — apilar botones */\n  .footer-downloads { flex-direction: column; gap: 8px; }\n  .footer-downloads a { width: 100%; text-align: center; box-sizing: border-box; }\n\n  /* Severity row — mobile: ocultar col rango */\n  .sev-row { grid-template-columns: minmax(90px,auto) 1fr 52px 40px !important; }\n  .sev-row span:nth-child(2) { display: none; }\n\n  /* Evitar scroll horizontal global */\n  body, .shell { overflow-x: hidden; }\n}\n\n@media (max-width: 400px) {\n  .shell { padding: 0 12px; }\n  .report-switcher { padding: 8px 12px 0; margin: 0 -12px; }\n  .switcher-btn { padding: 7px 10px; font-size: 9px; }\n  .kpi-val { font-size: clamp(28px, 9vw, 40px) !important; }\n  .canasta-tabs .tab-label { padding: 7px 10px; font-size: 8.5px; }\n}\n' + '\n/* ── Card BK Availability sync · CSS puro (W23+) ── */\nbody[data-ar-mode=\'rnd\'] #kpicard-ar3 { display: none !important; }\nbody[data-ar-mode=\'rnd\'] .ar-cards-grid { grid-template-columns: 1fr 1fr !important; }\n\n/* ── KPI Cards EF/CV: panels controlados por JS pills (W24+) ── */\n#kpi-ef-panels .tab-panel,\n#kpi-cv-panels .tab-panel,\n#kpi-bk-panels .tab-panel { display: none !important; }\n#kpi-ef-panels .tab-panel[data-tab=\'destino\'],\n#kpi-cv-panels .tab-panel[data-tab=\'destino\'],\n#kpi-bk-panels .tab-panel[data-tab=\'destino\'] { display: block !important; }\n\n/* RND NoDispo/IPM panels (W24+) · default pais */\n#kpi-nd-panels .tab-panel,\n#kpi-ipm-panels .tab-panel { display: none !important; }\n#kpi-nd-panels .tab-panel[data-tab=\'pais\'],\n#kpi-ipm-panels .tab-panel[data-tab=\'pais\'] { display: block !important; }\n\n/* Searchbox AR/KPI: el match supera la paginacion (sb-hidden/rows-more) - W24 */\n.sb-hidden.sb-search-hit, .rows-more.sb-search-hit, .sb-search-hit { display: grid !important; }\n\n</style>\n'
    + '<script>\n'
    + f'var _VOL_NUM = {int(VOL_NUM)};\n'
    + _cr_data_js + '\n'
    + _rnd_data_js + '\n'
    + _HIST_INIT_JS + '\n'      # ← HIST_CR y HIST_RND definidos ANTES de demo_js_main.js
    + open('demo_js_main.js', encoding='utf-8').read() + '\n'
    + open('js_override.js', encoding='utf-8').read().replace(
        'var _SEMANAS_HIST = ["W16","W17","W18","W19","W20","W21","W22","W23"];',
        f'var _SEMANAS_HIST = {_SEM_JS};')
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
/* _SEMANAS_HIST definida en js_override.js (embebida antes de este script) */
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
      var sem = (tipCfg.semanas && tipCfg.semanas.length === vals.length) ? tipCfg.semanas[best] : (_SEMANAS_HIST[best] || ('W'+(16+best)));
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

/* W23+: Manejar click en filas de cards KPI (EF/CV/BK) para actualizar su histórico global */
function _handleKpiCardHistClick(e, row, kpiRows) {
  /* Si la vista activa es corp/destino → filtro cruzado, no histórico */
  var card = row.closest('.kpi-card');
  if (!card) return;
  var cardId = card.id || '';
  var cardKey = cardId === 'kpicard-ef' ? 'ef' : cardId === 'kpicard-cv' ? 'cv' : cardId === 'kpicard-bk' ? 'bk' : cardId === 'kpicard-nd' ? 'nd' : cardId === 'kpicard-ipm' ? 'ipm' : null;
  if (cardKey && typeof _kpiView !== 'undefined') {
    var view = _kpiView[cardKey] || 'destino';
    if (view === 'corp' || view === 'destino' || view === 'pais') {
      /* Delegar al filtro cruzado (corp/dest/pais) */
      var cfKey = (view === 'corp') ? 'corp' : (view === 'pais') ? 'pais' : 'dest';
      var val   = row.getAttribute('data-hist-label') || '';
      if (val && typeof _kpiCrossFilter !== 'undefined') {
        var isAlreadySel = (_kpiCrossFilter[cardKey][cfKey] === val);
        _kpiCrossFilter[cardKey][cfKey] = isAlreadySel ? null : val;
        /* Mantener orden de selección para los cross-pills */
        var _o = _kpiCrossFilter[cardKey]._order || (_kpiCrossFilter[cardKey]._order = []);
        var _oi = _o.indexOf(cfKey);
        if (isAlreadySel) { if (_oi >= 0) _o.splice(_oi, 1); }       /* deselect → quitar */
        else { if (_oi >= 0) _o.splice(_oi, 1); _o.push(cfKey); }    /* select → al final */
        /* Paint de fila — igual que histórico */
        var _accent = (cardKey === 'bk') ? '#333132' : (cardKey === 'nd' || cardKey === 'ipm') ? '#EA0074' : '#5C469C';
        var _accentAlpha = (cardKey === 'bk') ? 'rgba(51,49,50,0.07)' : (cardKey === 'nd' || cardKey === 'ipm') ? 'rgba(234,0,116,0.07)' : 'rgba(92,70,156,0.07)';
        kpiRows.querySelectorAll('[data-hist-w21]').forEach(function(r) {
          r.style.background = ''; r.style.boxShadow = ''; r.removeAttribute('data-selected');
        });
        if (!isAlreadySel) {
          row.style.background = _accentAlpha;
          row.style.boxShadow = 'inset 3px 0 0 ' + _accent;
          row.setAttribute('data-selected', '1');
        }
        _kpiCrossFilterPillsRender(cardKey);
        _kpiPillRender(cardKey);
        /* Bug 5: al seleccionar una dimensión (país/corp/destino), actualizar la gráfica histórica
           con el valor de esa entidad (W24 = hist_w21, W23 = W24 − WoW). */
        var _cidMap = {nd:'hrnd-global-nd', ipm:'hrnd-global-ipm', ef:'hcr-global-ef', cv:'hcr-global-cv', bk:'h-bk-global'};
        var _cid2 = _cidMap[cardKey];
        if (_cid2) {
          if (isAlreadySel) {
            document.dispatchEvent(new CustomEvent('hist-reset', {detail: {cid: _cid2}}));
            var _lblR = document.getElementById('hist-' + _cid2 + '-label');
            if (_lblR) _lblR.textContent = 'Global';
          } else {
            var _wc = parseFloat(row.getAttribute('data-hist-w21'));
            var _wowAttr = parseFloat(row.getAttribute('data-hist-wow'));
            if (!isNaN(_wc)) {
              var _wp = !isNaN(_wowAttr) ? (_wc - _wowAttr) : _wc;
              document.dispatchEvent(new CustomEvent('hist-update', {detail: {cid: _cid2, w_curr: _wc, w_prev: _wp, label: val}}));
              var _lblU = document.getElementById('hist-' + _cid2 + '-label');
              if (_lblU) _lblU.textContent = val;
            }
          }
        }
      }
      return; /* No continuar con el histórico */
    }
  }
  var cardId = card.id || '';
  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';

  /* Cards AR (ar1/ar2): si la vista es cross-filter (corp/dest/hotel, o país en RND),
     el handler dim AR ya hace pill + selección + gráfica. No duplicar acá — si seguimos,
     el chequeo de data-selected confunde la selección recién puesta con un segundo click
     y resetea todo (bug: pill aparece pero fila/gráfica se borran). */
  if (cardId === 'kpicard-ar1' || cardId === 'kpicard-ar2') {
    var _arN = (cardId === 'kpicard-ar1') ? 1 : 2;
    var _arV = (typeof _arPillView !== 'undefined') ? (_arPillView[_arN] || 'hotel') : 'hotel';
    if (_arV === 'corp' || _arV === 'dest' || _arV === 'hotel' || (_arV === 'chan' && !isCR)) {
      return;
    }
  }

  /* Mapear card → canvas histórico global */
  var cid;
  if      (cardId === 'kpicard-ef')  cid = 'hcr-global-ef';
  else if (cardId === 'kpicard-cv')  cid = 'hcr-global-cv';
  else if (cardId === 'kpicard-bk')  cid = 'h-bk-global';
  else if (cardId === 'kpicard-nd')  cid = 'hrnd-global-nd';
  else if (cardId === 'kpicard-ipm') cid = 'hrnd-global-ipm';
  /* Cards AR de Rendimiento */
  else if (cardId === 'kpicard-ar1') cid = isCR ? 'hcr-panel-ef' : 'hrnd-panel-nd';
  else if (cardId === 'kpicard-ar2') cid = isCR ? 'hcr-panel-cv' : 'hrnd-panel-ipm';
  else if (cardId === 'kpicard-ar3') cid = 'h-bk-global';
  else return;

  var label = row.getAttribute('data-hist-label') || '';
  var w_curr = parseFloat(row.getAttribute('data-hist-w21'));
  var w_prev = parseFloat(row.getAttribute('data-hist-w20'));
  if (isNaN(w_curr)) return;
  if (isNaN(w_prev)) w_prev = w_curr;

  /* Toggle: segundo click en la misma fila → volver a Global */
  var isSelected = row.getAttribute('data-selected') === '1';
  kpiRows.querySelectorAll('[data-hist-w21]').forEach(function(r){
    r.style.background = ''; r.style.boxShadow = ''; r.removeAttribute('data-selected');
  });

  if (isSelected) {
    document.dispatchEvent(new CustomEvent('hist-reset', {detail: {cid: cid}}));
    return;
  }

  /* Color de acento según card */
  var accent = (cardId === 'kpicard-bk' || cardId === 'kpicard-ar3') ? '#333132'
             : (cardId === 'kpicard-nd' || cardId === 'kpicard-ipm') ? '#EA0074'
             : '#5C469C';
  var accentAlpha = (cardId === 'kpicard-bk' || cardId === 'kpicard-ar3') ? 'rgba(51,49,50,0.12)'
                  : (cardId === 'kpicard-nd' || cardId === 'kpicard-ipm') ? 'rgba(234,0,116,0.12)'
                  : 'rgba(92,70,156,0.12)';

  row.setAttribute('data-selected', '1');
  row.style.background = accentAlpha;
  row.style.boxShadow = 'inset 3px 0 0 ' + accent;

  /* Disparar hist-update para que historico_module redibuje el canvas global */
  document.dispatchEvent(new CustomEvent('hist-update', {
    detail: {cid: cid, w_curr: w_curr, w_prev: w_prev, label: label}
  }));
  var lblEl = document.getElementById('hist-' + cid + '-label');
  if (lblEl) lblEl.textContent = label;
}

/* ── Pills de navegación para cards AR (Vista + Filtro) ──────────────── */
var _arPillView = {1: 'hotel', 2: 'hotel'};
var _arPillFilt = {1: 'crit',  2: 'crit'};

function ar_setPillView(n, view, el) {
  _arPillView[n] = view;
  var isCR_m = !(typeof W !== 'undefined' && W.mode === 'rnd');
  var acc_bg  = isCR_m ? '#EDE8F7' : '#FCE4F1';
  var acc_fg  = isCR_m ? '#5C469C' : '#99162B';
  var acc_bd  = isCR_m ? '#5C469C' : '#EA0074';
  ['hotel','corp','dest','chan'].forEach(function(v) {
    var pill = document.getElementById('ar'+n+'-v-'+v);
    if (!pill) return;
    var active = (v === view);
    pill.style.background  = active ? acc_bg : 'transparent';
    pill.style.color       = active ? acc_fg : 'var(--ink-muted)';
    pill.style.borderColor = active ? acc_bd : 'var(--rule)';
  });
  /* Fila de filtro de severidad (Críticos/Bajo Rend./Sin Conv.): solo visible en vista Hotel */
  var hfilt = document.getElementById('ar'+n+'-hfilt');
  if (hfilt) hfilt.style.display = (view === 'hotel') ? '' : 'none';
  _arPillRender(n);
}

function ar_setPillFilt(n, filt, el) {
  _arPillFilt[n] = filt;
  ['crit','br','sc'].forEach(function(f) {
    var pill = document.getElementById('ar'+n+'-f-'+f);
    if (!pill) return;
    var active = (f === filt);
    pill.style.background  = active ? '#E8E6E3' : 'transparent';
    pill.style.color       = active ? '#333132' : 'var(--ink-muted)';
    pill.style.borderColor = active ? '#8A8377' : 'var(--rule)';
  });
  _arPillRender(n);
}

function _arPillRender(n) {
  var view = _arPillView[n] || 'hotel';
  var filt = _arPillFilt[n] || 'crit';
  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';

  var rows;
  if (view === 'hotel') {
    /* Vista hotel: usar filtro */
    var tabMap = {crit:'crit', br:'br', sc:'sc'};
    rows = _arRows(n, tabMap[filt] || 'crit');
  } else if (view === 'chan') {
    /* Vista channel: usar _arRenderChan */
    if (isCR) { _arRenderChan(n); return; }
    rows = _arDimRows(n, 'chan');
  } else {
    /* Vista corp/dest: dimensión */
    var dimMap = {corp:'corp', dest:'dest'};
    rows = _arDimRows(n, dimMap[view] || 'corp');
  }

  /* Usar el tbody unificado ar{n}-th */
  ar_renderTable(n, 'ar'+n+'-th', 'ar'+n+'-th-more', rows);
}

/* Wrapper de compatibilidad: el JS existente aún llama ar_setView/ar_setHotelTab/ar_setDim */
function ar_setView(n, view) {
  var map = {hotel:'hotel', dim:'corp'};
  var el = document.getElementById('ar'+n+'-v-' + (view==='hotel'?'hotel':'corp'));
  ar_setPillView(n, map[view] || view, el);
}
function ar_setHotelTab(n, tab, el_unused) {
  var map = {crit:'crit', br:'br', sc:'sc', cv:'crit'};
  var pill = document.getElementById('ar'+n+'-f-'+(map[tab]||'crit'));
  ar_setPillFilt(n, map[tab]||'crit', pill);
}
function ar_setDim(n, dim, el_unused) {
  var pill = document.getElementById('ar'+n+'-v-'+dim);
  ar_setPillView(n, dim, pill);
}

/* ── Pills de navegación para cards AR (Vista + Filtro) — FIN ──────── */
/* ══════════════════════════════════════════════════
   PILLS DE FILTRO · CARDS KPI (EF / CV)
   Misma lógica que ar_setPillFilt/ar_setPillView
   ══════════════════════════════════════════════════ */

var _kpiView = {ef: 'destino', cv: 'destino', bk: 'destino', nd: 'pais', ipm: 'pais'};

function kpi_setView(card, view, el) {
  _kpiView[card] = view;
  /* Primera línea (dimensión): activa = color de sección relleno · inactiva = outline · activa MAYÚSCULA — W24 */
  var _isRnd = (card === 'nd' || card === 'ipm');
  var sec_col = _isRnd ? '#EA0074' : '#5C469C';   /* violet CR / magenta RND */
  var sec_bg  = _isRnd ? '#FCE4F1' : '#EDE8F7';   /* relleno claro para la activa */

  /* Actualizar estilos de pills de vista (CR: destino/corp/hotel/channel · RND: pais/destino/corp/hotel) */
  ['pais','destino','corp','hotel','channel'].forEach(function(v) {
    var pill = document.getElementById('kpi-'+card+'-v-'+v);
    if (!pill) return;
    var active = (v === view);
    pill.style.background    = active ? sec_bg : 'transparent';
    pill.style.color         = sec_col;
    pill.style.borderColor   = sec_col;
    pill.style.textTransform = 'uppercase';
  });

  /* Mostrar/ocultar paneles */
  var panelsEl = document.getElementById('kpi-'+card+'-panels');
  if (panelsEl) {
    panelsEl.querySelectorAll('.tab-panel').forEach(function(p) {
      p.style.setProperty('display', (p.getAttribute('data-tab') === view) ? 'block' : 'none', 'important');
    });
  }

  /* Mostrar pills de filtro solo en vista hotel */
  var hfilt = document.getElementById('kpi-'+card+'-hfilt');
  if (hfilt) hfilt.style.display = 'none';  /* KPI cards no usan filtro de severidad (es de AR) */
  /* Aplicar cross-filter (corp/dest) en la vista recién mostrada */
  if (typeof _kpiPillRender === 'function') _kpiPillRender(card);
  /* Botón Ver más es estático (onclick inline) — no requiere JS dinámico */
}

var _kpiPillFilt = {ef: 'crit', cv: 'crit'};

function kpi_setPillFilt(card, filt, el) {
  _kpiPillFilt[card] = filt;
  ['crit','br','sc'].forEach(function(f) {
    var pill = document.getElementById('kpi-'+card+'-f-'+f);
    if (!pill) return;
    var active = (f === filt);
    pill.style.background  = active ? '#E8E6E3' : 'transparent';
    pill.style.color       = active ? '#333132' : 'var(--ink-muted)';
    pill.style.borderColor = active ? '#8A8377' : 'var(--rule)';
  });
  _kpiPillRender(card);
}

/* ── Paginación del subconjunto filtrado por cross-filter (W24) ──
   Cuando hay filtro cruzado activo, mostramos top N de los que matchean y
   ocultamos el resto bajo un botón "Ver más" dedicado (clase cf-extra). */
function _cfSetupMoreBtn(container, extra) {
  if (!container) return;
  var norm = container.querySelector('.kpi-more-btn');
  if (norm) norm.style.display = 'none';   /* ocultar paginación normal mientras hay filtro */
  var btn = container.querySelector('.cf-more-btn');
  if (extra <= 0) { if (btn) btn.style.display = 'none'; return; }
  if (!btn) {
    btn = document.createElement('button');
    btn.className = 'cf-more-btn';
    btn.style.cssText = "display:block;width:100%;margin-top:4px;margin-bottom:18px;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;user-select:none;";
    container.appendChild(btn);
  }
  btn.style.display = '';
  btn.textContent = 'Ver más \u25BE';
  btn.setAttribute('data-exp', '0');
  btn.onclick = function() {
    var exp = btn.getAttribute('data-exp') !== '1';
    btn.setAttribute('data-exp', exp ? '1' : '0');
    container.querySelectorAll('.cf-extra').forEach(function(r) {
      r.style.setProperty('display', exp ? 'grid' : 'none', 'important');
    });
    btn.textContent = exp ? 'Ver menos \u25B4' : 'Ver más \u25BE';
  };
}
function _cfRestoreMoreBtn(container) {
  if (!container) return;
  var btn = container.querySelector('.cf-more-btn');
  if (btn) btn.style.display = 'none';
  container.querySelectorAll('.cf-extra').forEach(function(r) { r.classList.remove('cf-extra'); });
  var norm = container.querySelector('.kpi-more-btn');
  if (norm) { norm.style.display = ''; norm.setAttribute('data-exp', '0'); norm.textContent = 'Ver más \u25BE'; }
}

/* ── B (W24): Pool completo de hoteles RND para cross-filter →hotel ──────────
   El universo RND es ~21K hoteles; volcarlos al DOM (como P15 en CR) serían
   +29MB. En su lugar viven en RND_HOTEL_POOL (JSON compacto). Cuando hay un
   cross-filter activo en la vista hotel de nd/ipm, el JS arma SOLO el
   subconjunto cruzado on-demand y reemplaza el panel hotel. Al limpiar el
   cross-filter se restaura el estático cacheado. Resuelve C/D. */
var _rndHotelOrigHTML = {};   /* cache del innerHTML estático por card (nd/ipm) */

/* ── Config del motor lazy de hoteles · genérico CR + RND (W24) ──────────────
   Layout del pool por reporte (índices de campo) + métricas (val/banda/wow,
   orden, grid). CR unifica sobre este motor — antes el pool de CR vivía en el
   DOM (~4MB); ahora compacto en CR_HOTEL_POOL y on-demand igual que RND. */
var _HOTEL_POOL_CFG = {
  rnd: {
    poolVar:'RND_HOTEL_POOL', bandNamesVar:'_RND_BAND_NAMES',
    corpIdx:1, destIdx:2, paisIdx:3, trafIdx:4, trafWowIdx:5,
    metrics:{
      nd: {valIdx:6, bandIdx:7,  wowIdx:8,  sortDesc:true,  requireVal:false, grid:'minmax(0,1fr) 72px 52px 74px 46px'},
      ipm:{valIdx:9, bandIdx:10, wowIdx:11, sortDesc:false, requireVal:true,  grid:'minmax(0,1fr) 72px 52px 74px 46px'}
    }
  },
  cr: {
    poolVar:'CR_HOTEL_POOL', bandNamesVar:'_CR_BAND_NAMES',
    corpIdx:1, destIdx:2, paisIdx:-1, trafIdx:3, trafWowIdx:4,
    metrics:{
      ef:{valIdx:5, bandIdx:6, wowIdx:7,  sortDesc:false, requireVal:false, grid:'minmax(0,1fr) 80px 56px 54px 48px'},
      cv:{valIdx:8, bandIdx:9, wowIdx:10, sortDesc:false, requireVal:false, grid:'minmax(0,1fr) 80px 56px 68px 40px'}
    }
  }
};

function _poolToCardRow(h, report, metric) {
  /* pool row compacto → array de 14 campos que entiende _cardRow */
  var cfg = _HOTEL_POOL_CFG[report], m = cfg.metrics[metric];
  var val = h[m.valIdx], bidx = h[m.bandIdx], wow = h[m.wowIdx];
  var bnames = (typeof window !== 'undefined') ? window[cfg.bandNamesVar] : null;
  var bname = (bnames && bnames[bidx] != null) ? bnames[bidx] : 'Sin Conversión';
  var bc = (typeof _AR_BANDA_C !== 'undefined' && _AR_BANDA_C[bname])
           ? _AR_BANDA_C[bname] : {bg:'#8A8377', fg:'#FFFFFF'};
  var corp = h[cfg.corpIdx], dest = h[cfg.destIdx];
  var pais = (cfg.paisIdx >= 0) ? h[cfg.paisIdx] : '';
  return [ h[0], corp, bc.bg, bc.fg, bname,
           h[cfg.trafIdx], h[cfg.trafWowIdx], val, wow, val, val,
           corp, dest, pais ];
}

/* Wrapper RND (back-compat con el cableado B existente) */
function _rndPoolToCardRow(h, metric) { return _poolToCardRow(h, 'rnd', metric); }

function _lazyHotelRender(report, card, cf, container) {
  var cfg = _HOTEL_POOL_CFG[report];
  if (!cfg || !container) return false;
  var pool = (typeof window !== 'undefined') ? window[cfg.poolVar] : null;
  if (!pool || !pool.length) return false;
  var m = cfg.metrics[card];
  if (!m) return false;
  var _N = _kpiNormCF;
  var nCorp = cf.corp ? _N(cf.corp) : '';
  var nDest = cf.dest ? _N(cf.dest) : '';
  var nPais = (cfg.paisIdx >= 0 && cf.pais) ? _N(cf.pais) : '';
  var bands = cf.bands || null;                  /* filtro por banda (vista sin cross-filter, CR) */
  var nHotel = cf.hotel ? _N(cf.hotel) : '';     /* hotel exacto (selección del searchbox) */
  var bnames = (typeof window !== 'undefined') ? window[cfg.bandNamesVar] : null;
  /* 1· filtrar el pool */
  var matched = [];
  for (var i = 0; i < pool.length; i++) {
    var h = pool[i];
    if (m.requireVal && h[m.valIdx] == null) continue;
    if (nHotel) { if (_N(h[0]) !== nHotel) continue; }
    if (bands) {
      var _bn = (bnames && bnames[h[m.bandIdx]] != null) ? bnames[h[m.bandIdx]] : 'Sin Conversión';
      if (bands.indexOf(_bn) < 0) continue;
    }
    if (nCorp && _N(h[cfg.corpIdx]).indexOf(nCorp) < 0) continue;
    if (nDest && _N(h[cfg.destIdx]).indexOf(nDest) < 0) continue;
    if (nPais && _N(h[cfg.paisIdx]).indexOf(nPais) < 0) continue;
    matched.push(h);
  }
  /* 2· ordenar peor primero (sortDesc por métrica en config) */
  var vi = m.valIdx;
  matched.sort(m.sortDesc
    ? function(a,b){ return (b[vi]||0) - (a[vi]||0); }
    : function(a,b){ return (a[vi]||0) - (b[vi]||0); });
  /* 3· cachear el estático una vez para restaurar al limpiar el filtro */
  if (_rndHotelOrigHTML[card] == null) _rndHotelOrigHTML[card] = container.innerHTML;
  /* 4· filas: 5 visibles + 5 cf-extra (cap 10) + resto sb-hidden (buscable, tope 300) */
  var grid = m.grid;
  var SEARCH_CAP = 300;
  var lim = Math.min(matched.length, SEARCH_CAP);
  var html = '';
  for (var k = 0; k < lim; k++) {
    var arr = _poolToCardRow(matched[k], report, card);
    var disp, cls;
    if (k < _KPI_TOP_N) { disp = 'grid'; cls = ''; }
    else if (k < _KPI_TOP_N + 5) { disp = 'none'; cls = 'cf-extra'; }
    else { disp = 'none'; cls = 'sb-hidden'; }
    html += _cardRow(arr, k, false, grid, disp, cls);
  }
  if (!html) html = '<div style="padding:14px 0;font-size:11px;color:var(--ink-muted);">Sin hoteles para esta combinación.</div>';
  /* preservar el header (primer hijo sin data-hist-label) al reemplazar las filas */
  var headerHTML = '';
  var _fc = container.firstElementChild;
  if (_fc && !_fc.hasAttribute('data-hist-label')) headerHTML = _fc.outerHTML;
  container.innerHTML = headerHTML + html;
  /* 5· botón Ver más para las cf-extra (máx 5) */
  var nExtra = Math.max(0, Math.min(matched.length, _KPI_TOP_N + 5) - _KPI_TOP_N);
  _cfSetupMoreBtn(container, nExtra);
  return true;
}

/* Wrapper RND (back-compat con el cableado B existente) */
function _rndLazyHotelRender(card, cf, container) { return _lazyHotelRender('rnd', card, cf, container); }

function _rndHotelRestore(card, container) {
  if (_rndHotelOrigHTML[card] != null && container) {
    container.innerHTML = _rndHotelOrigHTML[card];
    _rndHotelOrigHTML[card] = null;
  }
}

function _kpiPillRender(card) {
  /* Tab activa: leer del estado _kpiView (refactor pills W24 — ya no hay radios) */
  var activeTab = (typeof _kpiView !== 'undefined' && _kpiView[card]) ? _kpiView[card] : 'hotel';
  /* normalizar 'destino' (las vistas usan destino/corp/hotel/channel) */

  /* ── Cross-filter en vistas NO-hotel (corp/destino/pais) — W24 RND ──
     Cuando la vista activa es corp/destino/pais y hay un cross-filter activo
     (incluido País→Destino), filtrar las filas de ESE panel. */
  (function _crossFilterNonHotel(){
    if (activeTab === 'hotel' || activeTab === 'channel') return;
    var _cf = (typeof _kpiCrossFilter !== 'undefined') ? (_kpiCrossFilter[card] || {}) : {};
    var _panelsEl = document.getElementById('kpi-' + card + '-panels');
    if (!_panelsEl) return;
    var _panel = _panelsEl.querySelector('[data-tab="' + activeTab + '"]');
    if (!_panel) return;
    var _N = _kpiNormCF;
    var _MEM = (typeof RND_MEMBERSHIP !== 'undefined') ? RND_MEMBERSHIP : {corpDest:{}, corpPais:{}};
    function _memArr(mapObj, corp){
      var arr = mapObj[corp];
      if (arr) return arr;
      for (var k in mapObj){ if (_N(k) === _N(corp)) return mapObj[k]; }
      return null;
    }
    function _corpHasDest(corp, dest){
      var arr = _memArr(_MEM.corpDest||{}, corp); if(!arr) return false;
      for (var i=0;i<arr.length;i++){ if(_N(arr[i]) === _N(dest)) return true; } return false;
    }
    function _corpHasPais(corp, pais){
      var arr = _memArr(_MEM.corpPais||{}, corp); if(!arr) return false;
      for (var i=0;i<arr.length;i++){ if(_N(arr[i]) === _N(pais)) return true; } return false;
    }
    /* NO auto-filtro: la dimensión propia NO se filtra a sí misma (se resalta la fila seleccionada
       pero las demás siguen visibles). Solo filtran las dimensiones CRUZADAS. */
    var _anyFilter = (activeTab === 'destino' && (_cf.pais || _cf.corp))
                  || (activeTab === 'pais'    && _cf.corp)
                  || (activeTab === 'corp'    && (_cf.dest || _cf.pais));
    var _rows = _panel.querySelectorAll('[data-hist-label]');
    var _rowsContainer = _panel.querySelector('.kpi-tab-rows') || _panel;
    if (!_anyFilter) {
      /* sin filtro cruzado → restaurar paginación normal, PERO preservar:
         (a) la fila seleccionada (data-selected) y (b) el estado expandido del "Ver más"
         para no colapsar la lista cuando el usuario clickea una fila en posición 6-10
         (bug B: el click disparaba este restore y colapsaba el Ver más, ocultando la fila). */
      var _moreBtn = _rowsContainer.querySelector('.kpi-more-btn');
      var _wasExpanded = !!(_moreBtn && _moreBtn.getAttribute('data-exp') === '1');
      _rows.forEach(function(row){
        row.classList.remove('cf-extra');
        var _isSb = row.classList.contains('sb-hidden');
        var _isMore = row.classList.contains('rows-more');
        if (row.getAttribute('data-selected') === '1') row.style.setProperty('display', 'grid', 'important');
        else if (!_isSb && !_isMore) row.style.setProperty('display', 'grid');
        else if (_isMore && _wasExpanded) row.style.setProperty('display', 'grid', 'important');
        else row.style.removeProperty('display');
      });
      /* ocultar el botón cf si quedó, pero NO resetear el estado expandido del botón normal */
      var _cfBtn = _rowsContainer.querySelector('.cf-more-btn');
      if (_cfBtn) _cfBtn.style.display = 'none';
      if (_moreBtn) _moreBtn.style.display = '';
      return;
    }
    /* Con filtro cruzado → paginar el subconjunto que matchea */
    var _shown = 0, _extra = 0;
    _rows.forEach(function(row){
      row.classList.remove('cf-extra');
      var _label = row.getAttribute('data-hist-label') || '';
      var _rowPais = row.getAttribute('data-cf-pais') || '';
      var _ok = true;
      if (activeTab === 'destino') {
        if (_cf.pais) _ok = _ok && (_N(_rowPais).indexOf(_N(_cf.pais)) >= 0);   /* País→Destino */
        if (_cf.corp) _ok = _ok && _corpHasDest(_cf.corp, _label);              /* Corp→Destino */
      } else if (activeTab === 'pais') {
        if (_cf.corp) _ok = _ok && _corpHasPais(_cf.corp, _label);              /* Corp→País */
      } else if (activeTab === 'corp') {
        if (_cf.dest) _ok = _ok && _corpHasDest(_label, _cf.dest);              /* Destino→Corp */
        if (_cf.pais) _ok = _ok && _corpHasPais(_label, _cf.pais);              /* País→Corp */
      }
      if (_ok) {
        _shown++;
        if (_shown <= _KPI_TOP_N) { row.style.setProperty('display', 'grid', 'important'); }
        else if (_shown <= _KPI_TOP_N + 5) { row.classList.add('cf-extra'); row.style.setProperty('display', 'none', 'important'); _extra++; }
        else { row.style.setProperty('display', 'none', 'important'); }   /* cap 10: más allá → oculto, no expandible (buscable por searchbox) */
      } else {
        row.style.setProperty('display', 'none', 'important');
      }
    });
    _cfSetupMoreBtn(_rowsContainer, _extra);
  })();

  /* Filtros de banda para el tab hotel */
  var filt = _kpiPillFilt[card] || 'crit';
  var bandMap = {
    ef: {
      crit: ['Crítica','Súper Crítica'],
      br:   ['Revisar','Aceptable'],
      sc:   ['Sin Conversión']
    },
    cv: {
      crit: ['Crítica','Súper Crítica'],
      br:   ['Revisar','Aceptable'],
      sc:   ['Sin Conversión']
    }
  };
  var activeBands = (bandMap[card] && bandMap[card][filt]) ? bandMap[card][filt] : [];

  /* Aplicar filtro solo en tab hotel — ocultar/mostrar filas por banda */
  var panelsId = 'kpi-' + card + '-panels';
  var panelsEl = document.getElementById(panelsId);
  if (!panelsEl) return;

  /* Encontrar el tab-panel data-tab="hotel" */
  var hotelPanel = panelsEl.querySelector('[data-tab="hotel"]');
  if (!hotelPanel) return;

  /* Las filas son divs con data-banda (inyectado por _injectHistAttrs o por _kpiInjectBandas) */
  var rows = hotelPanel.querySelectorAll('[data-banda]');
  if (!rows.length) {
    /* Fallback: intentar re-inyectar bandas desde CR_CARD_TABS */
    _kpiInjectBandas(card, hotelPanel);
    rows = hotelPanel.querySelectorAll('[data-banda]');
  }

  /* Cross filter activo */
  var cf = (typeof _kpiCrossFilter !== 'undefined') ? (_kpiCrossFilter[card] || {}) : {};
  var _hotelCont = hotelPanel.querySelector('.kpi-tab-rows') || hotelPanel;

  /* Solo manipular las filas del panel hotel cuando la vista activa ES hotel.
     En otras vistas el panel hotel está oculto y se recalcula al cambiar de vista. */
  if (activeTab === 'hotel') {
    var _hasCf = !!(cf.corp || cf.dest || cf.pais);
    var _hasBand = !!(activeBands && activeBands.length);
    /* B (W24): RND nd/ipm → el panel hotel se sirve del pool completo on-demand.
       Con cross-filter: render lazy del subconjunto cruzado (cubre los 21K).
       Sin cross-filter: si antes se reemplazó, restaurar el estático y salir. */
    var _isRnd = (card === 'nd' || card === 'ipm');
    if (_isRnd && _hasCf) { _rndLazyHotelRender(card, cf, _hotelCont); return; }
    if (_isRnd && _rndHotelOrigHTML[card] != null) { _rndHotelRestore(card, _hotelCont); return; }
    /* CR (W24): ef/cv unifican sobre el MISMO motor lazy que RND. Con cross-filter →
       subconjunto cruzado del pool (ignora banda); sin cross-filter → vista por banda
       (crit/br/sc) desde el pool. Reemplaza el manejo de filas en-DOM (P15, ~4MB). */
    var _isCR = (card === 'ef' || card === 'cv');
    /* Solo la canasta GLOBAL usa el pool lazy (3582 hoteles). Las per-canasta (b2c/op/cug)
       siguen por el camino DOM con sus ~100 filas de CR_CARD_TABS[canasta]. */
    var _canG = (typeof W === 'undefined') || !W.canasta || W.canasta === 'global';
    if (_isCR && _canG) {
      if (_hasCf) { _lazyHotelRender('cr', card, cf, _hotelCont); }
      else { _lazyHotelRender('cr', card, {bands: activeBands}, _hotelCont); }
      return;
    }
    if (!_hasCf) {
      /* Sin cross-filter → comportamiento original (filtro de banda CR o paginación normal) */
      _cfRestoreMoreBtn(_hotelCont);
      rows.forEach(function(row) {
        row.classList.remove('cf-extra');
        var isSbHidden = row.classList.contains('sb-hidden');
        if (_hasBand) {
          var banda = row.getAttribute('data-banda') || '';
          row.style.setProperty('display', activeBands.indexOf(banda) >= 0 ? 'grid' : 'none', 'important');
        } else {
          if (!isSbHidden && !row.classList.contains('rows-more')) row.style.setProperty('display', 'grid');
          else row.style.removeProperty('display');
        }
      });
    } else {
      /* Con cross-filter → mostrar TODOS los hoteles del corp/dest/país (ignorar banda,
         igual que RND No Dispo). Paginar el subconjunto que matchea. */
      var _sh = 0, _ex = 0;
      rows.forEach(function(row) {
        row.classList.remove('cf-extra');
        var rowCorp = row.getAttribute('data-cf-corp') || '';
        var rowDest = row.getAttribute('data-cf-dest') || '';
        var rowPais2 = row.getAttribute('data-cf-pais') || '';
        var okCf = (!cf.corp || _kpiNormCF(rowCorp).indexOf(_kpiNormCF(cf.corp)) >= 0)
                && (!cf.dest || _kpiNormCF(rowDest).indexOf(_kpiNormCF(cf.dest)) >= 0)
                && (!cf.pais || _kpiNormCF(rowPais2).indexOf(_kpiNormCF(cf.pais)) >= 0);
        if (okCf) {
          _sh++;
          if (_sh <= _KPI_TOP_N) { row.style.setProperty('display', 'grid', 'important'); }
          else { row.classList.add('cf-extra'); row.style.setProperty('display', 'none', 'important'); _ex++; }
        } else {
          row.style.setProperty('display', 'none', 'important');
        }
      });
      _cfSetupMoreBtn(_hotelCont, _ex);
    }
  }

  /* cntEl del searchbox se maneja por el SB nativo — no intervenir */
}

function _kpiInjectBandas(card, hotelPanel) {
  /* Inyectar data-banda en las filas del tab hotel desde CR_CARD_TABS */
  if (typeof CR_CARD_TABS === 'undefined') return;
  var canasta = (typeof W !== 'undefined') ? (W.canasta || 'global') : 'global';
  var metric = card === 'ef' ? 'ef' : 'cv';
  var tabData = CR_CARD_TABS[canasta] && CR_CARD_TABS[canasta][metric]
              ? CR_CARD_TABS[canasta][metric]['hotel']
              : null;
  if (!tabData || !tabData.length) return;
  /* Las filas del DOM son divs dentro del tab-panel, en orden */
  var divRows = Array.from(hotelPanel.querySelectorAll('.kpi-tab-rows > div, .kpi-tab-rows [data-hist-w21]'));
  divRows.forEach(function(divRow, i) {
    if (i < tabData.length) {
      var row = tabData[i];
      var banda = row[4] || '';  /* índice 4 = banda */
      divRow.setAttribute('data-banda', banda);
    }
  });
}

/* Hook: mostrar/ocultar pill row cuando cambia el tab de dim */
/* Los tabs usan radio inputs — observar cambios con event delegation */
document.addEventListener('change', function(e) {
  var t = e.target;
  if (!t || t.tagName !== 'INPUT' || t.type !== 'radio') return;
  var name = t.name || '';
  var card = null;
  if (name === 'tabs-ef') card = 'ef';
  else if (name === 'tabs-cv') card = 'cv';
  if (!card) return;
  /* Mostrar pill row solo en tab hotel */
  var parts = t.id.split('-');
  var activeTab = parts[parts.length - 1];
  var hfilt = document.getElementById('kpi-' + card + '-hfilt');
  if (hfilt) hfilt.style.display = (activeTab === 'hotel') ? 'flex' : 'none';
});

/* ── Pills KPI — FIN ── */
/* ══════════════════════════════════════════════════
   FILTRO CRUZADO · CARDS KPI — igual que AR
   Estado, render de pills, clear y event delegation
   ══════════════════════════════════════════════════ */

var _kpiCrossFilter = {
  ef: {corp: null, dest: null, channel: null, _order: []},
  cv: {corp: null, dest: null, channel: null, _order: []},
  bk: {corp: null, dest: null, channel: null, _order: []},
  nd: {corp: null, dest: null, pais: null, channel: null, _order: []},
  ipm: {corp: null, dest: null, pais: null, channel: null, _order: []}
};

function _kpiNormCF(s) {
  return String(s||'').trim().toLowerCase()
    .replace(/[áàä]/g,'a').replace(/[éèë]/g,'e')
    .replace(/[íìï]/g,'i').replace(/[óòö]/g,'o')
    .replace(/[úùü]/g,'u').replace(/ñ/g,'n');
}

function _kpiCrossFilterPillsRender(card) {
  var container = document.getElementById('kpi-'+card+'-cross-pills');
  if (!container) return;
  var f = _kpiCrossFilter[card];
  if (!f) return;

  /* Cross-pills: en CR (Connectivities: ef/cv/bk) van en VIOLETA (acento CR);
     en RND (nd/ipm) van en VERDE. El magenta/violeta de nav queda para la pill activa. */
  var _isCR = (card === 'ef' || card === 'cv' || card === 'bk');
  var GR_BG = '#E1F5EE';
  var GR_FG = '#1A6B4A';
  var GR_BD = '#1A6B4A';

  var _pill = function(type, label) {
    return '<span class="kpi-cross-pill"'
      +' data-cross-card="'+card+'" data-cross-type="'+type+'"'
      +' style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px 3px 10px;'
      +'border-radius:20px;font-size:9px;font-weight:700;background:'+GR_BG+';color:'+GR_FG+';'
      +'border:1px solid '+GR_BD+';white-space:nowrap;cursor:pointer;">'
      +label+' <span style="font-size:11px;opacity:.65;">&#x00D7;</span></span>';
  };

  /* Orden de selección: recorrer _order (orden de click). Fallback: corp, dest, pais, channel */
  var html = '';
  var order = (f._order && f._order.length) ? f._order : ['corp','dest','pais','channel'];
  order.forEach(function(type){
    if (type === 'corp' && f.corp) html += _pill('corp', f.corp);
    if (type === 'dest' && f.dest) html += _pill('dest', f.dest);
    if (type === 'pais' && f.pais) html += _pill('pais', f.pais);
    if (type === 'channel' && f.channel) html += _pill('channel', f.channel);
  });

  container.innerHTML = html;
  container.style.display = html ? 'flex' : 'none';
}

function _kpiCrossFilterClear(card, type) {
  if (!_kpiCrossFilter[card]) return;
  var _o = _kpiCrossFilter[card]._order || [];
  if (type) {
    _kpiCrossFilter[card][type] = null;
    var _oi = _o.indexOf(type);
    if (_oi >= 0) _o.splice(_oi, 1);
  } else {
    _kpiCrossFilter[card] = {corp: null, dest: null, pais: null, channel: null, _order: []};
  }
  /* Limpiar el resaltado de las filas seleccionadas de esta card (quedaban marcadas al quitar la pill) */
  var _panelsEl = document.getElementById('kpi-' + card + '-panels');
  if (_panelsEl) {
    _panelsEl.querySelectorAll('[data-selected]').forEach(function(r){
      r.style.background = ''; r.style.boxShadow = ''; r.removeAttribute('data-selected');
    });
  }
  /* Resetear la gráfica histórica de esta card a Global (W24) — al deseleccionar */
  var _cidMapClr = {ef:'hcr-global-ef', cv:'hcr-global-cv', bk:'h-bk-global', nd:'hrnd-global-nd', ipm:'hrnd-global-ipm'};
  var _cidClr = _cidMapClr[card];
  if (_cidClr) {
    try { document.dispatchEvent(new CustomEvent('hist-reset', {detail:{cid:_cidClr}})); } catch(e){}
    var _lblClr = document.getElementById('hist-' + _cidClr + '-label'); if (_lblClr) _lblClr.textContent = 'Global';
  }
  _kpiCrossFilterPillsRender(card);
  _kpiPillRender(card);
}

/* Event delegation: click en pill × para limpiar filtro cruzado KPI */
document.addEventListener('click', function(e) {
  var cpill = e.target.closest('.kpi-cross-pill');
  if (!cpill) return;
  var cc = cpill.getAttribute('data-cross-card');
  var ct = cpill.getAttribute('data-cross-type');
  if (cc && ct) _kpiCrossFilterClear(cc, ct);
});

/* ── Selección de CHANNEL en cards KPI (ef/cv/nd/ipm) — W24 ──
   Las filas channel (.chan-wrap .bk-row) no están en .kpi-tab-rows ni en -chan-div,
   así que el listener global no las cubría. Aquí: actualizar gráfica global + pill + highlight. */
document.addEventListener('click', function(e) {
  if (e.target.closest('[data-sort-key]')) return;            /* ignorar headers de sort */
  var row = e.target.closest('.chan-wrap .bk-row');
  if (!row) row = e.target.closest('.chan-wrap [data-hist-w21]');
  if (!row) return;
  var cardEl = row.closest('[id^="kpicard-"]');
  if (!cardEl) return;
  var ck = cardEl.id.replace('kpicard-','');
  if (['ef','cv','nd','ipm'].indexOf(ck) < 0) return;         /* solo cards KPI (bk y AR tienen su propio handler) */
  /* Evitar que historico_module (bubble) re-limpie la selección de la fila channel */
  e.stopPropagation();
  var gmap = {ef:'hcr-global-ef', cv:'hcr-global-cv', nd:'hrnd-global-nd', ipm:'hrnd-global-ipm'};
  var cid = gmap[ck];
  var chanWrap = row.closest('.chan-wrap');
  var label = row.getAttribute('data-hist-label') || row.getAttribute('data-lbl') || '';
  var w21 = parseFloat(row.getAttribute('data-hist-w21'));
  var w20 = parseFloat(row.getAttribute('data-hist-w20'));
  if (isNaN(w21)) return;
  if (isNaN(w20)) w20 = w21;
  var already = row.getAttribute('data-selected') === '1';
  if (chanWrap) chanWrap.querySelectorAll('.bk-row, [data-hist-w21]').forEach(function(r){ r.style.background=''; r.removeAttribute('data-selected'); });
  var _f = (typeof _kpiCrossFilter !== 'undefined') ? _kpiCrossFilter[ck] : null;
  if (already) {
    if (_f) { _f.channel = null; var _o = _f._order || []; var _i = _o.indexOf('channel'); if (_i >= 0) _o.splice(_i,1); _kpiCrossFilterPillsRender(ck); }
    document.dispatchEvent(new CustomEvent('hist-reset', {detail:{cid:cid}}));
    var lblR = document.getElementById('hist-'+cid+'-label'); if (lblR) lblR.textContent = 'Global';
    return;
  }
  row.style.background = 'var(--accent-soft)';
  row.setAttribute('data-selected','1');
  if (_f) {
    _f.channel = label;
    var _o2 = _f._order || (_f._order = []);
    if (_o2.indexOf('channel') < 0) _o2.push('channel');
    _kpiCrossFilterPillsRender(ck);
  }
  document.dispatchEvent(new CustomEvent('hist-update', {detail:{cid:cid, w_curr:w21, w_prev:w20, label:label}}));
  var lblU = document.getElementById('hist-'+cid+'-label'); if (lblU) lblU.textContent = label;
}, true);

/* El filtro cruzado persiste al cambiar de vista — igual que AR */

/* ── Filtro cruzado KPI — FIN ── */



/* Listener del panel — captura clicks en w22-th/w22-td, cards AR y channel divs */
document.addEventListener('click', function(e) {
  var row = e.target.closest ? e.target.closest('[data-hist-w21]') : null;
  if (!row) return;

  /* Determinar contenedor: tbody (tablas), div canal, o .kpi-tab-rows (cards KPI W23+) */
  var tbody = row.closest('tbody');
  var chanDiv = row.closest('[id$="-chan-div"]');
  var kpiRows = row.closest('.kpi-tab-rows');
  var container = tbody || chanDiv || kpiRows;
  if (!container) return;

  /* W23+: Si la fila está en una card KPI (.kpi-tab-rows), manejar aparte */
  if (kpiRows && !tbody && !chanDiv) {
    _handleKpiCardHistClick(e, row, kpiRows);
    return;
  }

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
    r.style.background = ''; r.style.boxShadow = ''; r.removeAttribute('data-selected');
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
    W22_CANVAS_CFG[id] = {vals: nv, semanas: oc.semanas || _SEMANAS_HIST, metric: oc.metric};
  }
  _updateCfg(cid);

  /* Forzar onmousemove en ambos canvas con closure sobre los vals correctos */
  [cid, globalCid].forEach(function(id) {
    var canvasEl = document.getElementById(id);
    if (!canvasEl) return;
    (function(capturedId, capturedW21, capturedW20){
      var sems = _SEMANAS_HIST;
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
        tip.textContent = (sems[best]||_SEMANAS_HIST[best]||('W'+(16+best)))+': '+fmtVal;
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
            /* CR: leer de CR_D (CR_HOTELS eliminado — era duplicado de estos mismos arrays) */
            var d2 = (typeof CR_D !== 'undefined') ? (CR_D[canasta] || CR_D.global || {}) : {};
            var dg = (typeof CR_D !== 'undefined') ? (CR_D.global || {}) : {};
            var key2 = (tabMapCR[idx] || tabMapCR[0]).dataKey;
            return d2[key2] || dg[key2] || d2.hotels || [];
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


# ── Datos JS para card 3 Bookability ──────────────────────────────────────
def _bk_rows(top_df, col_name, n=5):
    """Genera rows JS para la tabla de la card 3 BK."""
    import json as _j
    rows = []
    for _, r in top_df.head(n).iterrows():
        bk_val  = r['Bookability']
        bk_fmt  = f"{bk_val*100:.2f}%"
        books   = int(r.get('Books', 0))
        wow_pp  = r.get('BK_WoW_pp', None)
        wow_fmt = f"{wow_pp*100:+.2f}" if wow_pp is not None and not _np.isnan(wow_pp) else '—'
        from engine import banda_eficacia as _bef
        banda   = _bef(bk_val)
        rows.append({
            'lab':   str(r[col_name]),
            'books': books,
            'val':   bk_fmt,
            'wow':   wow_fmt,
            'banda': banda,
        })
    return rows

import numpy as _np

if DB is not None:
    _bk_global = DB.get('bk_global', 0)
    _bk_prev   = DB.get('bk_prev',   0)
    _bk_wow    = DB.get('bk_wow',    0)
    _bk_books  = DB.get('books_global', 0)
    _bk_banda  = DB.get('banda_global', 'exitosa')

    # Prov: usar g_provider completo (todos los canales con MIN_BOOKS >= 5)
    # sin filtro min_books=50 que excluye canales con pocos bookings BK
    _bk_prov_df    = DB.get('g_provider', DB['TOP_PROVIDER'])
    _bk_prov_rows  = _bk_rows(_bk_prov_df, 'Provider', n=len(_bk_prov_df))
    _bk_dest_rows  = _bk_rows(DB['TOP_DEST'],     'Destino',  n=100)
    _bk_corp_rows  = _bk_rows(DB['TOP_CORP'],     'CorpName', n=100)
    _bk_hotel_rows = _bk_rows(DB['TOP_HOTEL'],    'Hotel',    n=100)

    # Generar lookup de WoW TRX para card BK
    import json as _json2
    def _bk_trx_wow_lookup(df, col, key_col):
        """Genera dict {label: wow_pct} para WoW de TRX en card BK."""
        result = {}
        for _, r in df.iterrows():
            wow_pct = r.get('Books_WoW_pct', None)
            if wow_pct is not None and not _np.isnan(wow_pct):
                result[str(r[key_col])] = f"{wow_pct:+.4f}"
        return result

    _bk_trx_wow = {
        'destino': _bk_trx_wow_lookup(DB.get('g_dest',  DB.get('TOP_DEST',  _np.array([]))), 'Destino',  'Destino'),
        'corp':    _bk_trx_wow_lookup(DB.get('g_corp',  DB.get('TOP_CORP',  _np.array([]))), 'CorpName', 'CorpName'),
        'hotel':   _bk_trx_wow_lookup(DB.get('g_hotel', DB.get('TOP_HOTEL', _np.array([]))), 'Hotel',    'Hotel'),
    }
    BK_TRX_WOW_JS = f"var _BK_TRX_WOW = {_json2.dumps(_bk_trx_wow, ensure_ascii=False)};\n"

    BK_JS_DATA = f"""
var BK_DATA = {{
  global: {{
    bk:    '{_bk_global*100:.2f}%',
    bk_prev: '{_bk_prev*100:.2f}%',
    bk_wow:  {_bk_wow*100:.4f},
    books: '{_bk_books:,}'.replace(',','.'),
    banda: '{_bk_banda}',
  }},
  prov:  {_json2.dumps(_bk_prov_rows,  ensure_ascii=False)},
  dest:  {_json2.dumps(_bk_dest_rows,  ensure_ascii=False)},
  corp:  {_json2.dumps(_bk_corp_rows,  ensure_ascii=False)},
  hotel: {_json2.dumps(_bk_hotel_rows, ensure_ascii=False)},
  banda_colors: {{
    'exitosa':   ['#1A6B4A','#FFFFFF'],
    'aceptable': ['#FBBF24','#FFFFFF'],
    'revisar':   ['#F97316','#FFFFFF'],
    'critica':   ['#C0392B','#FFFFFF'],
    'sc':        ['#2D2828','#FFFFFF'],
    'sinconv':   ['#8A8377','#FFFFFF'],
  }},
}};
"""
else:
    BK_JS_DATA = "var BK_DATA = null;\n"

BK_SORT_JS = """
/* bkSort — ordenamiento clickeable de la card BK */
window.bkSort = function(el) {
    var key = el.getAttribute('data-sort-key');
    var hdr = el.parentNode;
    var curDir = el.getAttribute('data-sort-dir') || '';
    var newDir = curDir === 'desc' ? 'asc' : 'desc';
    hdr.querySelectorAll('[data-sort-key]').forEach(function(h) {
        h.removeAttribute('data-sort-dir');
        var arr = h.querySelector('.bk-arrow');
        if (arr) { arr.textContent = '↕'; arr.style.opacity = '.4'; }
    });
    el.setAttribute('data-sort-dir', newDir);
    var arrow = el.querySelector('.bk-arrow');
    if (arrow) { arrow.textContent = newDir === 'desc' ? '↓' : '↑'; arrow.style.opacity = '1'; }
    var panel = hdr.closest('[data-tab]');
    if (!panel) return;
    var sortFn = function(a, b) {
        var av, bv;
        if (key === 'lbl') {
            av = a.getAttribute('data-lbl') || '';
            bv = b.getAttribute('data-lbl') || '';
            return newDir === 'desc' ? bv.localeCompare(av) : av.localeCompare(bv);
        }
        av = parseFloat(a.getAttribute('data-' + key) || '0');
        bv = parseFloat(b.getAttribute('data-' + key) || '0');
        return newDir === 'desc' ? bv - av : av - bv;
    };
    /* W23: estructura nueva — filas .bk-row directas (sin wrappers), con clases
       bk-more (filas 6-10) y bk-sb-hidden (11+). Agrupar por parent directo (PP/TP en channel). */
    var allRowEls = Array.prototype.slice.call(panel.querySelectorAll('.bk-row'));
    var groups = []; /* {container, rows} */
    allRowEls.forEach(function(r) {
        var c = r.parentNode;
        var g = groups.find(function(x){ return x.container === c; });
        if (!g) { g = { container: c, rows: [] }; groups.push(g); }
        g.rows.push(r);
    });
    /* Para cada grupo, ordenar y re-asignar clases/visibilidad según posición.
       Sistema unificado con EF/CV: clases rows-more (6-10) / sb-hidden (11+),
       data-row-idx por posición, preservado tras el sort. */
    groups.forEach(function(grp) {
        grp.rows.sort(sortFn);
        var moreBtn = grp.container.querySelector(':scope > .kpi-more-btn');
        var isExpanded = moreBtn && moreBtn.getAttribute('data-exp') === '1';
        /* Quitar todas las filas del container */
        grp.rows.forEach(function(r){ if(r.parentNode) r.parentNode.removeChild(r); });
        var beforeEl = moreBtn;
        grp.rows.forEach(function(r, i) {
            /* Re-asignar data-row-idx según nueva posición */
            r.setAttribute('data-row-idx', i);
            /* Resetear clases de posición (sistema unificado) */
            r.classList.remove('rows-more');
            r.classList.remove('sb-hidden');
            r.classList.remove('bk-more');
            r.classList.remove('bk-sb-hidden');
            if (i < 5) {
                /* Top 5 — visible */
                r.style.setProperty('display', 'grid', 'important');
            } else if (i < 10) {
                /* 6-10 — expandible con Ver más */
                r.classList.add('rows-more');
                r.style.setProperty('display', isExpanded ? 'grid' : 'none', 'important');
            } else {
                /* 11+ — buscable pero oculta */
                r.classList.add('sb-hidden');
                r.style.setProperty('display', 'none', 'important');
            }
            if (beforeEl) grp.container.insertBefore(r, beforeEl);
            else grp.container.appendChild(r);
        });
    });
};
"""

AR3_CANVAS_JS = '''
(function(){
  var CID = 'h-ar3-bk-global', IS_INVERTED = false, METRIC = 'bookability', TARGET = 97.0, BAR_CEIL = 100.0, SCALE_FLOOR = 93.0;
  var SEMANAS = ["W16", "W17", "W18", "W19", "W20", "W21", "W22", "W23"], VALS_DEF = [98.28, 98.44, 98.22, 98.26, 98.17, 98.25, 98.40, 98.43], BC = {"Exitosa": {"bg": "#1A6B4A", "fg": "#FFFFFF", "footer": "#FFFFFF"}, "Aceptable": {"bg": "#FBBF24", "fg": "#FFFFFF", "footer": "#FFFFFF"}, "Revisar": {"bg": "#F97316", "fg": "#FFFFFF", "footer": "#FFFFFF"}, "Cr\u00edtica": {"bg": "#C0392B", "fg": "#FFFFFF", "footer": "#FFFFFF"}, "S\u00faper Cr\u00edtica": {"bg": "#2D2828", "fg": "#FFFFFF", "footer": "#FFFFFF"}, "Sin Conversi\u00f3n": {"bg": "#8A8377", "fg": "#FFFFFF", "footer": "#FFFFFF"}};
  /* W23+: Registrar la serie canónica (8 puntos correctos) en objeto global dedicado.
     El tooltip OVERRIDE lee de aquí con máxima prioridad, evitando datos viejos de W22_CANVAS_CFG. */
  if (typeof window !== 'undefined') {
    if (!window._HIST_CANON) window._HIST_CANON = {};
    window._HIST_CANON[CID] = { semanas: SEMANAS.slice(), vals: VALS_DEF.slice(), metric: METRIC };
  }
  var ACCENT_HEX = '#333132', ACCENT_RGB = '51,49,50';
  
  function getBanda(v) {
    if (METRIC === 'eficacia' || METRIC === 'bookability') { var pct = v / 100; if (pct >= 0.97) return 'Exitosa'; if (pct >= 0.93) return 'Aceptable'; if (pct >= 0.85) return 'Revisar'; if (pct >= 0.60) return 'Crítica'; return 'Súper Crítica'; }
    if (METRIC === 'convrate') { var pct = v / 100; if (pct === 0) return 'Sin Conversión'; if (pct < 0.008) return 'Crítica'; if (pct < 0.015) return 'Revisar'; if (pct <= 0.025) return 'Aceptable'; return 'Exitosa'; }
    if (METRIC === 'nodispo') { var pct = v / 100; if (pct < 0.03) return 'Exitosa'; if (pct <= 0.05) return 'Aceptable'; if (pct <= 0.20) return 'Revisar'; if (pct <= 0.60) return 'Crítica'; return 'Súper Crítica'; }
    if (v === 0) return 'Sin Conversión'; if (v < 200) return 'Crítica'; if (v < 650) return 'Revisar'; if (v <= 1500) return 'Aceptable'; return 'Exitosa';
  }
  
  function fmtVal(v) { return METRIC === 'ipm' ? '$' + v.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',') : v.toFixed(2) + '%'; }
  
  /* Thresholds por métrica */
  var THS = METRIC === 'eficacia' ? [97, 93, 85, 60] :
            METRIC === 'convrate' ? [2.5, 1.5, 0.8] :
            METRIC === 'nodispo' ? [3.0, 5.0, 20.0, 60.0] : [650, 500, 199];
  var THS_SORTED = THS.slice().sort(function(a, b) { return a - b; });
  
  /* Distancia ordinal: cuántas bandas de distancia al target */
  function ordinalDist(mid, target, thresholds, invert) {
    if (!invert) {
      if (mid >= target) return 0;
      return thresholds.filter(function(t) { return t > mid && t <= target; }).length;
    } else {
      if (mid <= target) return 0;
      return thresholds.filter(function(t) { return t < mid && t >= target; }).length;
    }
  }
  
  /* Color de semáforo por distancia ordinal */
  var SEMAFORO_PALETTE = [
    {line: '#1A6B4A', fg: '#0F5132', label: '≥ target'},
    {line: '#D97706', fg: '#92400E', label: '–1 banda'},
    {line: '#C2410C', fg: '#9A3412', label: '–2 bandas'},
    {line: '#BE123C', fg: '#9F1239', label: '–3+ bandas'}
  ];
  function getSemaforoColor(dist) {
    return SEMAFORO_PALETTE[Math.min(dist, 3)];
  }
  
  /* Formato de label de threshold */
  function fmtThLabel(t) {
    return METRIC === 'ipm' ? '$' + t.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',') :
           METRIC === 'nodispo' ? t.toFixed(1) + '%' : t.toFixed(t < 10 ? 1 : 0) + '%';
  }
  
  /* Formato de label de target */
  function fmtTarget() {
    return METRIC === 'ipm' ? 'T:$' + TARGET.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',') :
           (METRIC === 'eficacia' || METRIC === 'bookability') ? 'T:' + TARGET.toFixed(0) + '%' : 'T:' + TARGET.toFixed(1) + '%';
  }
  
  var _lastWidth = 0;  /* Ancho válido del último drawCanvas exitoso */
  function drawCanvas(vals) {
    currentVals = vals;  /* recordar último estado para re-draws automáticos */
    var el = document.getElementById(CID), ctx = el ? el.getContext('2d', {willReadFrequently: false}) : null;
    if (!ctx) return;
    /* W23: usar offsetWidth medido ahora; si es 0, reutilizar el último válido o el del padre */
    var _ow = el.offsetWidth;
    if (!_ow && el.parentElement) _ow = el.parentElement.offsetWidth;
    if (!_ow) _ow = _lastWidth;   /* último ancho válido */
    if (!_ow) _ow = 360;          /* fallback absoluto */
    _lastWidth = _ow;             /* guardar para próxima vez */
    var _oh = el.offsetHeight || 100;
    el.width = _ow; el.height = _oh; ctx.clearRect(0, 0, el.width, el.height);
    var W = el.width, H = el.height, n = vals.length;
    var pL=6, pR=4, pT=8, pB=18;  /* pR mínimo — labels de target se dibujan dentro del área */
    var cw = W-pL-pR, ch = H-pT-pB;
    /* Escala v5: umbral adyacente incluido solo si dist ≤ 1×i_range */
    var i_min = Math.min(Math.min.apply(null, vals), TARGET, SCALE_FLOOR);
    var i_max = Math.max(Math.max.apply(null, vals), TARGET);
    var i_range = (i_max - i_min) || (i_max * 0.05) || 1.0;
    var ths_s = THS_SORTED.slice();  /* thresholds ordenados */
    var below = ths_s.filter(function(t) { return t < i_min; });
    var above = ths_s.filter(function(t) { return t > i_max; });
    var adj_below = below.length ? below[below.length-1] : null;
    var adj_above = above.length ? above[0] : null;
    var anchor_min = i_min, anchor_max = i_max;
    if (adj_below !== null && (i_min - adj_below) <= i_range) anchor_min = adj_below;
    if (adj_above !== null && (adj_above - i_max) <= i_range) anchor_max = adj_above;
    var pad = i_range * 0.35;  /* W23+: más padding para que puntos abruptos no queden pegados al borde */
    var canvas_min = anchor_min - pad, canvas_max = anchor_max + pad;
    var dR = canvas_max - canvas_min + 0.0001;
    var xOf = function(i) { return pL + (i/(n-1))*cw; };
    var yOf = function(v) { return pT + ch - (v-canvas_min)/dR*ch; };
    /* Líneas de umbral visibles (sin fondos de banda) */
    var visible_ths = THS.filter(function(t) { return t > canvas_min && t < canvas_max && t !== TARGET; }).sort(function(a,b){return b-a;});
    visible_ths.forEach(function(t) {
      var ty = yOf(t);
      var dist = ordinalDist(t+(IS_INVERTED?-0.001:0.001), TARGET, THS, IS_INVERTED);
      var sc = getSemaforoColor(dist);
      ctx.save();
      ctx.strokeStyle = sc.line; ctx.lineWidth = 0.75; ctx.globalAlpha = 0.60;
      ctx.setLineDash([3,3]);
      ctx.beginPath(); ctx.moveTo(pL, ty); ctx.lineTo(pL+cw, ty); ctx.stroke();
      ctx.setLineDash([]);
      ctx.font = '6.5px Geist,system-ui,sans-serif';
      ctx.fillStyle = sc.fg; ctx.globalAlpha = 0.85;
      ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.textAlign = 'right'; ctx.fillText(fmtThLabel(t), W-2, ty); ctx.textAlign = 'left';
      ctx.restore();
    });
    /* Línea target verde */
    var tY = yOf(TARGET);
    ctx.save();
    ctx.strokeStyle = '#1A6B4A'; ctx.lineWidth = 1.5; ctx.globalAlpha = 0.80;
    ctx.setLineDash([4,3]);
    ctx.beginPath(); ctx.moveTo(pL, tY); ctx.lineTo(pL+cw, tY); ctx.stroke();
    ctx.setLineDash([]);
    ctx.font = 'bold 7px Geist,system-ui,sans-serif';
    ctx.fillStyle = '#1A6B4A'; ctx.globalAlpha = 0.95;
    ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.textAlign = 'right'; ctx.fillText(fmtTarget(), W-2, tY); ctx.textAlign = 'left';
    ctx.restore();
    /* Area fill gradiente en color de la serie */
    ctx.save();
    var grad = ctx.createLinearGradient(0, pT, 0, pT+ch);
    grad.addColorStop(0, 'rgba('+ACCENT_RGB+',0.40)');
    grad.addColorStop(1, 'rgba('+ACCENT_RGB+',0.04)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    ctx.lineTo(xOf(n-1), pT+ch); ctx.lineTo(xOf(0), pT+ch);
    ctx.closePath(); ctx.fill(); ctx.restore();
    /* Línea de datos */
    ctx.save();
    ctx.strokeStyle = ACCENT_HEX; ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    ctx.stroke(); ctx.restore();
    /* Puntos en la serie — todos visibles */
    for (var i = 0; i < n; i++) { 
      var isLast = (i === n - 1); 
      ctx.fillStyle = ACCENT_HEX;
      ctx.globalAlpha = 1.0; 
      ctx.beginPath(); 
      ctx.arc(xOf(i), yOf(vals[i]), isLast ? 3.5 : 2.5, 0, 2 * Math.PI); 
      ctx.fill(); 
      if (isLast) { ctx.strokeStyle = '#FDFCF9'; ctx.lineWidth = 1.5; ctx.stroke(); }
    }
    /* Actualizar W22_CANVAS_CFG para que el tooltip use vals correctos */
    if (typeof W22_CANVAS_CFG !== 'undefined') W22_CANVAS_CFG[CID] = {vals: vals, semanas: SEMANAS, metric: METRIC};
    /* Actualizar también _HIST_CANON con los vals actuales (puede ser una serie de item específico) */
    if (typeof window !== 'undefined' && window._HIST_CANON && window._HIST_CANON[CID]) {
      window._HIST_CANON[CID].vals = vals.slice();
    }
  }
  
  function updateMetrics(vals, lbl) {
    var vMin = Math.min.apply(null, vals), vMax = Math.max.apply(null, vals), vAvg = vals.reduce(function(a,b){return a+b;},0)/vals.length, vCurr = vals[vals.length-1];
    var banda = getBanda(vCurr), bc = BC[banda] || BC['Sin Conversión'];
    var el = document.getElementById('hist-'+CID+'-label'); if (el) el.textContent = lbl || 'Global';
    el = document.getElementById('hist-'+CID+'-actual'); if (el) el.textContent = fmtVal(vCurr);
    el = document.getElementById('hist-'+CID+'-best'); if (el) el.textContent = fmtVal(IS_INVERTED ? vMin : vMax);
    el = document.getElementById('hist-'+CID+'-worst'); if (el) el.textContent = fmtVal(IS_INVERTED ? vMax : vMin);
    el = document.getElementById('hist-'+CID+'-avg'); if (el) el.textContent = fmtVal(vAvg);
    var bbEl = document.getElementById('hist-'+CID+'-banda-box'), bEl = document.getElementById('hist-'+CID+'-banda');
    if (bbEl) { bbEl.style.background = bc.bg; bbEl.style.borderColor = bc.fg; bbEl.style.color = bc.fg; }
    if (bEl) { bEl.textContent = banda; bEl.style.color = bc.fg; }
    el = document.getElementById('hist-'+CID+'-banda-footer'); if (el) { el.textContent = banda.toUpperCase(); el.style.color = bc.footer; el.style.background = bc.bg; }
    /* Actualizar el valor grande de la card siempre — usa vCurr (W21) actual */
    var kvMap = {'hcr-global-ef': 'w21-kv-ef', 'hcr-global-cv': 'w21-kv-cv',
                 'hrnd-global-nd': 'w21-kv-nd', 'hrnd-global-ipm': 'w21-kv-rpm'};
    var kvId = kvMap[CID];
    if (kvId) {
      var kvEl = document.getElementById(kvId);
      if (kvEl) { kvEl.textContent = fmtVal(vCurr); }
    }
  }
  
  var currentVals = VALS_DEF.slice();  /* mutable — guarda el último estado dibujado */
  function buildSerie(w_c, w_p) { var s = VALS_DEF.slice(); s[s.length-1] = w_c; s[s.length-2] = w_p; return s; }
  
  function attachListeners() {
    /* Solo maneja click en el label del histórico para volver a Global.
       La selección de filas la maneja js_override document-level listener
       que dispara hist-update/hist-reset correctamente. */
    var hEl = document.getElementById('hist-'+CID), card = hEl ? hEl.closest('.kpi-card') : null;
    if (!card) return;
    var lblEl = document.getElementById('hist-'+CID+'-label');
    if (lblEl) lblEl.addEventListener('click', function() {
      card.querySelectorAll('[data-hist-w20],[data-hist-w21]').forEach(function(r) { r.style.background = ''; r.style.boxShadow = ''; r.removeAttribute('data-selected'); });
      drawCanvas(VALS_DEF); updateMetrics(VALS_DEF, 'Global');
      lblEl.textContent = 'Global';
    });
  }
  
  function _cardWidth() {
    /* Ancho de la kpi-card que contiene el canvas — visible aunque canvas esté en display:none */
    var el = document.getElementById(CID);
    if (!el) return 0;
    var p = el.parentElement;
    while (p) { if (p.offsetWidth > 50) return p.offsetWidth; p = p.parentElement; }
    return 0;
  }

  function _tryDraw() {
    var el = document.getElementById(CID);
    if (!el) return false;
    var ow = el.offsetWidth || _cardWidth() || _lastWidth;
    if (ow > 50) { _lastWidth = ow; drawCanvas(currentVals); return true; }
    return false;
  }

  function init() {
    updateMetrics(VALS_DEF, 'Global'); attachListeners();
    var el = document.getElementById(CID);
    if (el) {
      var det = el.closest('details');
      if (det) det.addEventListener('toggle', function() { if (det.open) requestAnimationFrame(_tryDraw); });
      var drawn = false;
      /* Observar la CARD (que sí es visible) no el canvas (que está en display:none) */
      var anchor = el.closest('.kpi-card') || el.parentElement;
      if (typeof IntersectionObserver !== 'undefined' && anchor) {
        new IntersectionObserver(function(entries) { entries.forEach(function(entry) {
          if (entry.isIntersecting) { requestAnimationFrame(function() { if(_tryDraw()) drawn=true; }); }
        }); }, {threshold: 0.01}).observe(anchor);
      }
      /* Fallback por si el observer no dispara */
      [300, 800, 2000].forEach(function(d) {
        setTimeout(function() { if (!drawn && _tryDraw()) drawn = true; }, d);
      });
    }
    document.addEventListener('change', function(e) {
      if (e.target.type !== 'radio') return;
      requestAnimationFrame(function() { requestAnimationFrame(_tryDraw); });
    });
  }
  
  document.addEventListener('hist-update', function(e) {
    if (e.detail.cid !== CID) return;
    var s = buildSerie(e.detail.w_curr, e.detail.w_prev);
    var lbl = e.detail.label || '';
    /* Doble rAF: el primer frame inicia el layout, el segundo lo tiene disponible */
    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        drawCanvas(s);
        updateMetrics(s, lbl);
      });
    });
  });
  document.addEventListener('hist-reset', function(e) {
    if (e.detail.cid !== CID) return;
    requestAnimationFrame(function() { drawCanvas(VALS_DEF); updateMetrics(VALS_DEF, 'Global'); });
  });
  
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else requestAnimationFrame(init);
  
  /* Exponer función de redraw con nuevo accent para cambio de canasta */
  window['histRedraw_'+CID] = function(newAccent, newVals) {
    if (newAccent) {
      var _rgbMap = (typeof RGB !== 'undefined') ? RGB : {
        '#5C469C':'92,70,156','#EA0074':'234,0,116','#FCB000':'252,176,0',
        '#4FC3F4':'79,195,244','#1A6B4A':'26,107,74','#333132':'51,49,50'
      };
      ACCENT_HEX = newAccent;
      ACCENT_RGB = _rgbMap[newAccent] || '92,70,156';
    }
    var vals = newVals || currentVals;
    drawCanvas(vals); updateMetrics(vals, 'Global');
  };
})();
'''

AR_SB_PATCH_JS = '''
/* W23+: Searchbox con autocomplete para cards AR */
(function() {
  function norm(s) { return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,''); }
  function _attachArSb(inputId, containerId) {
    var input = document.getElementById(inputId);
    if (!input) return;
    var clearBtn = document.getElementById(input.getAttribute('data-sb-clear-id')||inputId+'-clear');
    /* Re-obtener el container por ID en cada operación (las filas se re-renderizan dentro) */
    function _cont() { return document.getElementById(containerId); }
    function filter() {
      var container = _cont();
      if (!container) return;
      var q = norm(input.value.trim());
      container.querySelectorAll('[data-hist-label]').forEach(function(r) {
        var match = !q || norm(r.getAttribute('data-hist-label')||'').indexOf(q) >= 0;
        if (q) {
          if (match) {
            r.classList.add('sb-search-hit');
            r.style.setProperty('display', 'grid', 'important');
          } else {
            r.classList.remove('sb-search-hit');
            r.style.setProperty('display', 'none', 'important');
          }
        } else {
          r.classList.remove('sb-search-hit');
          if (!r.classList.contains('sb-hidden') && !r.classList.contains('rows-more')) r.style.setProperty('display', 'grid');
          else r.style.removeProperty('display');
        }
      });
      if (clearBtn) clearBtn.style.display = q ? 'inline-block' : 'none';
    }
    function buildDD(q) {
      var container = _cont();
      if (!container) return;
      var qn = norm(q);
      var dd = document.getElementById(inputId+'-dd');
      if (!dd) { dd=document.createElement('div'); dd.id=inputId+'-dd'; dd.style.cssText="position:fixed;z-index:9999;background:var(--paper);border:1px solid var(--rule);border-radius:4px;box-shadow:0 4px 12px rgba(0,0,0,.12);min-width:200px;max-height:240px;overflow-y:auto;"; document.body.appendChild(dd); }
      if (!qn) { dd.style.display='none'; dd.innerHTML=''; return; }
      var seen={}, labels=[];
      container.querySelectorAll('[data-hist-label]').forEach(function(r){ var l=r.getAttribute('data-hist-label'); if(l&&!seen[l]){seen[l]=true;labels.push(l);} });
      var matches=labels.filter(function(l){return norm(l).indexOf(qn)>=0;}).slice(0,8);
      if(!matches.length){dd.style.display='none';dd.innerHTML='';return;}
      dd.innerHTML=matches.map(function(l){return '<div class="sb-suggestion" data-value="'+l+'" style="padding:7px 12px;cursor:pointer;font-size:11px;color:var(--ink);border-bottom:1px solid var(--rule-soft);">'+l+'</div>';}).join('');
      var rect=input.getBoundingClientRect(); dd.style.left=rect.left+'px'; dd.style.top=(rect.bottom+4)+'px'; dd.style.width=Math.max(rect.width+60,200)+'px'; dd.style.display='block';
      dd.querySelectorAll('.sb-suggestion').forEach(function(el){
        el.onmousedown=function(e){e.preventDefault();input.value=el.getAttribute('data-value');filter();dd.style.display='none';input.focus();};
        el.onmouseover=function(){el.style.background='var(--paper-soft)';}; el.onmouseout=function(){el.style.background='';};
      });
    }
    input.oninput=function(){filter();buildDD(input.value);};
    if(clearBtn) clearBtn.onclick=function(){input.value='';filter();var dd=document.getElementById(inputId+'-dd');if(dd)dd.style.display='none';};
    input.onblur=function(){setTimeout(function(){var dd=document.getElementById(inputId+'-dd');if(dd)dd.style.display='none';},150);};
  }
  /* W25 (#8): Searchbox de cards KPI (sb-kpi-{ef,cv,bk,nd,ipm}) — DELEGADO.
     Antes intentado con input.oninput, pero las cards KPI re-renderizan su región
     (tabs-row) y borraban el handler → oninput quedaba null. Con delegación a nivel
     document sobrevive al re-render. Filtra el panel de la VISTA ACTIVA (_kpiView[card]);
     al seleccionar dispara el click real de la fila (reusa _handleKpiCardHistClick:
     cross-filter + highlight + gráfica), limpia el query, repagina y fija la fila visible. */
  var _KPI_SB_CARDS = ['ef', 'cv', 'bk', 'nd', 'ipm'];
  /* Fix B (#8 rev): la fila seleccionada en posición 6-10 se re-colapsaba porque
     el botón "Ver más" y los re-renders ponen inline display:none !important sobre
     las .rows-more (pisa el sb-search-hit). Pin + MutationObserver: re-fija la fila
     seleccionada ante CUALQUIER re-render o colapso. */
  var _kpiSbPinned = {};
  function _kpiSbRepin(card) {
    var label = _kpiSbPinned[card]; if (!label) return;
    var panels = document.getElementById('kpi-' + card + '-panels'); if (!panels) return;
    /* refijar en TODOS los paneles (la vista activa puede cambiar) */
    panels.querySelectorAll('[data-hist-label]').forEach(function(r) {
      if (r.getAttribute('data-hist-label') !== label) return;
      /* solo actuar si está oculta — evita loop con el observer de atributos */
      if (r.classList.contains('sb-search-hit') && r.style.getPropertyValue('display') === 'grid') return;
      r.classList.add('sb-search-hit');
      r.style.setProperty('display', 'grid', 'important');
    });
  }
  var _kpiSbMO = (typeof MutationObserver !== 'undefined') ? new MutationObserver(function() {
    for (var i = 0; i < _KPI_SB_CARDS.length; i++) { if (_kpiSbPinned[_KPI_SB_CARDS[i]]) _kpiSbRepin(_KPI_SB_CARDS[i]); }
  }) : null;
  function _kpiSbObserve() {
    if (!_kpiSbMO) return;
    _KPI_SB_CARDS.forEach(function(c) {
      var el = document.getElementById('kpi-' + c + '-panels');
      if (el) _kpiSbMO.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['style', 'class'] });
    });
  }
  function _kpiSbCardOf(input) {
    if (!input || !input.id || input.id.indexOf('sb-kpi-') !== 0) return null;
    var c = input.id.replace('sb-kpi-', '');
    return _KPI_SB_CARDS.indexOf(c) >= 0 ? c : null;
  }
  function _kpiSbPanel(card) {
    var view = (typeof _kpiView !== 'undefined' && _kpiView[card]) ? _kpiView[card] : 'destino';
    var panels = document.getElementById('kpi-' + card + '-panels');
    if (!panels) return null;
    return panels.querySelector('[data-tab="' + view + '"]');
  }
  function _kpiSbRows(card) { var p = _kpiSbPanel(card); return p ? p.querySelectorAll('[data-hist-label]') : []; }
  function _kpiSbFilter(card, input) {
    var q = norm(input.value.trim());
    _kpiSbPinned[card] = null;   /* nueva búsqueda → invalidar pin anterior */
    var clearBtn = document.getElementById('sb-kpi-' + card + '-clear');
    _kpiSbRows(card).forEach(function(r) {
      var match = !q || norm(r.getAttribute('data-hist-label') || '').indexOf(q) >= 0;
      if (q) {
        if (match) { r.classList.add('sb-search-hit'); r.style.setProperty('display', 'grid', 'important'); }
        else { r.classList.remove('sb-search-hit'); r.style.setProperty('display', 'none', 'important'); }
      } else {
        r.classList.remove('sb-search-hit');
        if (!r.classList.contains('sb-hidden') && !r.classList.contains('rows-more')) r.style.setProperty('display', 'grid');
        else r.style.removeProperty('display');
      }
    });
    if (clearBtn) clearBtn.style.display = q ? 'inline-block' : 'none';
  }
  function _kpiSbDD(card) { return document.getElementById('sb-kpi-' + card + '-dd'); }
  /* W24: el searchbox en vista hotel sugiere desde el pool completo (CR/RND), no solo el DOM */
  function _kpiSbPoolFor(card) {
    /* solo canasta global usa el pool (per-canasta van por DOM con CR_CARD_TABS[canasta]) */
    var _canG = (typeof W === 'undefined') || !W.canasta || W.canasta === 'global';
    if (!_canG) return null;
    if (card === 'ef' || card === 'cv') return 'cr';
    if (card === 'nd' || card === 'ipm') return 'rnd';
    return null;
  }
  function _kpiSbBuildDD(card, input) {
    var qn = norm(input.value);
    var dd = _kpiSbDD(card);
    if (!dd) { dd = document.createElement('div'); dd.id = 'sb-kpi-' + card + '-dd'; dd.style.cssText = "position:fixed;z-index:9999;background:var(--paper);border:1px solid var(--rule);border-radius:4px;box-shadow:0 4px 12px rgba(0,0,0,.12);min-width:200px;max-height:240px;overflow-y:auto;"; document.body.appendChild(dd); }
    if (!qn) { dd.style.display = 'none'; dd.innerHTML = ''; return; }
    var view = (typeof _kpiView !== 'undefined' && _kpiView[card]) ? _kpiView[card] : 'destino';
    var _pc = (view === 'hotel') ? _kpiSbPoolFor(card) : null;
    var matches = [];
    if (_pc && typeof _HOTEL_POOL_CFG !== 'undefined' && window[_HOTEL_POOL_CFG[_pc].poolVar]) {
      /* vista hotel → sugerir desde el pool completo (alcanza CUALQUIER hotel, no solo el DOM) */
      var pool = window[_HOTEL_POOL_CFG[_pc].poolVar], seen = {};
      for (var i = 0; i < pool.length && matches.length < 8; i++) {
        var l = pool[i][0];
        if (l && !seen[l] && norm(l).indexOf(qn) >= 0) { seen[l] = true; matches.push(l); }
      }
    } else {
      var seen2 = {}, labels = [];
      _kpiSbRows(card).forEach(function(r) { var l = r.getAttribute('data-hist-label'); if (l && !seen2[l]) { seen2[l] = true; labels.push(l); } });
      matches = labels.filter(function(l) { return norm(l).indexOf(qn) >= 0; }).slice(0, 8);
    }
    if (!matches.length) { dd.style.display = 'none'; dd.innerHTML = ''; return; }
    dd.innerHTML = matches.map(function(l) { return '<div class="sb-suggestion" data-kpi-card="' + card + '" data-value="' + l + '" style="padding:7px 12px;cursor:pointer;font-size:11px;color:var(--ink);border-bottom:1px solid var(--rule-soft);">' + l + '</div>'; }).join('');
    var rect = input.getBoundingClientRect(); dd.style.left = rect.left + 'px'; dd.style.top = (rect.bottom + 4) + 'px'; dd.style.width = Math.max(rect.width + 60, 200) + 'px'; dd.style.display = 'block';
  }
  function _kpiSbSelect(card, label) {
    var input = document.getElementById('sb-kpi-' + card);
    if (input) input.value = '';
    var dd = _kpiSbDD(card); if (dd) dd.style.display = 'none';
    var p = _kpiSbPanel(card); if (!p) return;
    var view = (typeof _kpiView !== 'undefined' && _kpiView[card]) ? _kpiView[card] : 'destino';
    var _pc = (view === 'hotel') ? _kpiSbPoolFor(card) : null;
    var target = null;
    function _find() { target = null; p.querySelectorAll('[data-hist-label]').forEach(function(r) { if (!target && r.getAttribute('data-hist-label') === label) target = r; }); }
    _find();
    /* vista hotel + pool: si el hotel no está en el DOM (lazy), renderizarlo desde el pool */
    if (!target && _pc) {
      var cont = p.querySelector('.kpi-tab-rows') || p;
      _lazyHotelRender(_pc, card, { hotel: label }, cont);
      _find();
    }
    if (!target) return;
    /* disparar el click real de la fila (cross-filter en otras vistas + pill + highlight + gráfica) */
    target.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    /* Filtrar el panel activo a SOLO la fila elegida. Evita la "lista enorme" y la deja
       SIEMPRE visible sin pelear con la paginación. _showOnly se re-aplica tras el re-render
       del click; el observer (_kpiSbRepin) la mantiene. */
    _kpiSbPinned[card] = label;
    function _showOnly() {
      var p2 = _kpiSbPanel(card); if (!p2) return;
      /* si el hotel no quedó tras el re-render del click, re-renderizarlo desde el pool */
      var has = false;
      p2.querySelectorAll('[data-hist-label]').forEach(function(r) { if (r.getAttribute('data-hist-label') === label) has = true; });
      if (!has && _pc) { var c2 = p2.querySelector('.kpi-tab-rows') || p2; _lazyHotelRender(_pc, card, { hotel: label }, c2); }
      p2.querySelectorAll('[data-hist-label]').forEach(function(r) {
        if (r.getAttribute('data-hist-label') === label) {
          r.classList.add('sb-search-hit');
          r.style.setProperty('display', 'grid', 'important');
          if (r.scrollIntoView) try { r.scrollIntoView({ block: 'nearest' }); } catch (e) {}
        } else {
          r.classList.remove('sb-search-hit');
          r.style.setProperty('display', 'none', 'important');
        }
      });
      var cb = document.getElementById('sb-kpi-' + card + '-clear'); if (cb) cb.style.display = 'inline-block';
    }
    _showOnly();
    setTimeout(_showOnly, 80);
    setTimeout(_showOnly, 260);
  }
  document.addEventListener('input', function(e) {
    var card = _kpiSbCardOf(e.target); if (!card) return;
    /* Solo dropdown — NO filtrar el panel en vivo (eso mostraba la "lista enorme").
       El panel se filtra a la fila elegida recién al seleccionar una sugerencia. */
    _kpiSbBuildDD(card, e.target);
  });
  document.addEventListener('mousedown', function(e) {
    var sug = e.target.closest ? e.target.closest('.sb-suggestion[data-kpi-card]') : null;
    if (!sug) return; e.preventDefault();
    _kpiSbSelect(sug.getAttribute('data-kpi-card'), sug.getAttribute('data-value'));
  });
  document.addEventListener('click', function(e) {
    var btn = e.target.closest ? e.target.closest('[id^="sb-kpi-"][id$="-clear"]') : null;
    if (!btn) return;
    var card = btn.id.replace('sb-kpi-', '').replace('-clear', '');
    if (_KPI_SB_CARDS.indexOf(card) < 0) return;
    var input = document.getElementById('sb-kpi-' + card); if (input) input.value = '';
    _kpiSbPinned[card] = null;
    var dd = _kpiSbDD(card); if (dd) dd.style.display = 'none';
    btn.style.display = 'none';
    /* Restaurar la paginación normal del panel activo (deshacer el filtro-a-uno):
       top-5 visible, resto oculto, luego re-aplicar cross-filter si está activo. */
    var p = _kpiSbPanel(card);
    if (p) {
      var _n = 0;
      p.querySelectorAll('[data-hist-label]').forEach(function(r) {
        r.classList.remove('sb-search-hit');
        if (r.classList.contains('sb-hidden') || r.classList.contains('rows-more')) r.style.setProperty('display', 'none', 'important');
        else r.style.setProperty('display', 'grid', 'important');
      });
    }
    if (typeof _kpiPillRender === 'function') _kpiPillRender(card);
  });
  document.addEventListener('focusout', function(e) {
    var card = _kpiSbCardOf(e.target); if (!card) return;
    setTimeout(function() { var dd = _kpiSbDD(card); if (dd) dd.style.display = 'none'; }, 150);
  });
  function attachArSearchboxes(){_attachArSb('sb-ar1','ar1-th');_attachArSb('sb-ar2','ar2-th');_attachArSb('ar3-sb','ar3-tbody');}
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',function(){setTimeout(attachArSearchboxes,800);setTimeout(_kpiSbObserve,900);});}
  else{setTimeout(attachArSearchboxes,800);setTimeout(_kpiSbObserve,900);}
  /* A (#8 rev): el switch CR↔RND re-renderiza las cards AR y borra el .oninput del
     searchbox AR (sb-ar1/sb-ar2/ar3-sb) → en RND no desplegaba el autocomplete.
     Re-cablear tras cada cambio de modo (delegado sobre los botones del switcher). */
  document.addEventListener('click', function(e){
    var btn = e.target.closest ? e.target.closest('[onclick*="w22_setMode"]') : null;
    if (!btn) return;
    setTimeout(attachArSearchboxes, 350);
  });
})();
'''

AR3_MODE_JS = '''
/* ── Ocultar card 3 (BK) en modo RND y ajustar grid ── */
(function() {
  function _syncCard3(mode) {
    var card3 = document.getElementById('kpicard-ar3');
    var grid  = document.querySelector('.ar-cards-grid');
    if (!card3 || !grid) return;
    if (mode === 'rnd') {
      card3.style.display = 'none';
      grid.style.gridTemplateColumns = '1fr 1fr';
    } else {
      card3.style.display = '';
      grid.style.gridTemplateColumns = 'repeat(3,1fr)';
    }
    /* Switcher local AR — solo clase .on, sin inline style (CSS maneja el negro) */
    var arBtnCr  = document.getElementById('ar-btn-cr');
    var arBtnRnd = document.getElementById('ar-btn-rnd');
    if (arBtnCr)  { arBtnCr.classList.toggle('on',  mode !== 'rnd'); arBtnCr.style.background  = ''; arBtnCr.style.color = ''; }
    if (arBtnRnd) { arBtnRnd.classList.toggle('on', mode === 'rnd'); arBtnRnd.style.background = ''; arBtnRnd.style.color = ''; }
  }
  document.addEventListener('mode-changed', function(e) {
    _syncCard3(e.detail && e.detail.mode);
  });
  /* Estado inicial */
  setTimeout(function() {
    var mode = (typeof W !== 'undefined') ? W.mode : 'cr';
    _syncCard3(mode);
    document.body.setAttribute('data-ar-mode', mode);
  }, 100);
  /* Exponer globalmente para llamada directa desde w22_setMode */
  window._syncCard3 = _syncCard3;
})();

/* w22_setMode consolidada en js_override.js (W23-bk-s3)
   data-ar-mode y _syncCard3 se manejan ahí directamente */
'''
CHAN_SORT_EFCV_JS = '''
/* ══ Channel EF/CV: sort + selección de fila (unificado con BK · W24) ══
   Reusa window.bkSort (sort genérico por data-{key}). Script separado para
   no depender de que js_override.js llegue al final. */
(function initChannelSortEFCV() {
  function _attach() {
    var done = true;
    ['ef','cv'].forEach(function(metric) {
      var card = document.getElementById('kpicard-'+metric);
      if (!card) { done = false; return; }
      if (card._chanSortAttached) return;
      card._chanSortAttached = true;
      card.addEventListener('click', function(e) {
        var sp = e.target.closest('[data-sort-key]');
        if (sp && card.contains(sp)) {
          var panel = sp.closest('[data-tab]');
          if (panel && panel.getAttribute('data-tab') === 'channel') {
            if (typeof window.bkSort === 'function') window.bkSort(sp);
            return;
          }
        }
        var row = e.target.closest('.bk-row');
        if (row && card.contains(row)) {
          var panel2 = row.closest('[data-tab]');
          if (panel2 && panel2.getAttribute('data-tab') === 'channel') {
            var wasSel = row.getAttribute('data-selected') === '1';
            card.querySelectorAll('.bk-row').forEach(function(r){
              r.style.background = ''; r.style.boxShadow = ''; r.removeAttribute('data-selected');
            });
            if (!wasSel) {
              row.style.background = '#EDE8F7';
              row.setAttribute('data-selected', '1');
            }
          }
        }
      });
    });
    return done;
  }
  var _tries = 0;
  (function _retry(){
    if (_attach() || _tries++ > 40) return;
    setTimeout(_retry, 100);
  })();
})();
'''

# AR3 histórico BK: inyectar semanas dinámicas + serie BK real (W17-W24, última = W24)
# Reemplaza el hardcodeo W16-W23 (labels stale) y la serie BK vieja por el dato real del pickle.
if _AR3_BK_JS:
    AR3_CANVAS_JS = AR3_CANVAS_JS.replace(
        'var SEMANAS = ["W16", "W17", "W18", "W19", "W20", "W21", "W22", "W23"], VALS_DEF = [98.28, 98.44, 98.22, 98.26, 98.17, 98.25, 98.40, 98.43]',
        f'var SEMANAS = {_SEM_JS}, VALS_DEF = {_AR3_BK_JS}')

GLOBAL_PANEL_SCRIPT = '<script>' + AR3_MODE_JS + '</script>\n<script>' + AR3_CANVAS_JS + '</script>\n<script>' + AR_SB_PATCH_JS + '</script>\n<script>' + TAB_BINDING_JS + '</script>\n<script>' + PANEL_LISTENER_JS + '</script>\n<script>' + BK_JS_DATA + '</script>\n<script>' + BK_TRX_WOW_JS + '</script>\n<script>' + BK_SORT_JS + '</script>\n<script>' + CHAN_SORT_EFCV_JS + '</script>\n'

SECTION_DIVIDER = ''  # W21+ — sin divisor

SWITCHER = f'''<div style="padding-top:10px;">
<div class="w22-seg">
  <button class="w22-seg-btn on" id="mode-cr" onclick="w22_setMode('cr',this)">Connectivities</button>
  <button class="w22-seg-btn" id="mode-rnd" onclick="w22_setMode('rnd',this)">Availability</button>
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
    <div class="cfb-kpi-item" style="display:flex;flex-direction:column;align-items:center;text-align:center;">
      <div class="cfb-kpi-lbl" id="w22-strip-lbl1">Eficacia</div>
      <div class="cfb-kpi-val" id="w22-strip-ef" style="color:#5C469C;">—</div>
      <span class="sev-badge" id="w22-strip-ef-band" style="font-size:8px;font-weight:700;padding:2px 8px;text-transform:uppercase;letter-spacing:.04em;outline:1px solid rgba(0,0,0,.12);display:inline-block;white-space:nowrap;border-radius:2px;margin-top:2px;">—</span>
    </div>
    <div class="cfb-sep"></div>
    <div class="cfb-kpi-item" style="display:flex;flex-direction:column;align-items:center;text-align:center;">
      <div class="cfb-kpi-lbl" id="w22-strip-lbl2">Conv Rate</div>
      <div class="cfb-kpi-val" id="w22-strip-cv" style="color:#5C469C;">—</div>
      <span class="sev-badge" id="w22-strip-cv-band" style="font-size:8px;font-weight:700;padding:2px 8px;text-transform:uppercase;letter-spacing:.04em;outline:1px solid rgba(0,0,0,.12);display:inline-block;white-space:nowrap;border-radius:2px;margin-top:2px;">—</span>
    </div>
    <div class="cfb-sep"></div>
    <div class="cfb-kpi-item" id="w22-strip-bk-item" style="display:flex;flex-direction:column;align-items:center;text-align:center;">
      <div class="cfb-kpi-lbl">Bookability</div>
      <div class="cfb-kpi-val" id="w22-strip-bk" style="color:#333132;">—</div>
      <span class="sev-badge" id="w22-strip-bk-band" style="font-size:8px;font-weight:700;padding:2px 8px;text-transform:uppercase;letter-spacing:.04em;outline:1px solid rgba(0,0,0,.12);display:inline-block;white-space:nowrap;border-radius:2px;margin-top:2px;">—</span>
    </div>
    <div class="cfb-sep" id="w22-strip-bk-sep"></div>
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
      onclick="w22_setMode('cr',document.getElementById('mode-cr'))">Connectivities</button>
    <button class="w22-seg-btn" id="ar-btn-rnd"
      onclick="w22_setMode('rnd',document.getElementById('mode-rnd'))">Availability</button>
  </div>
</div>


<!-- Grid 3 cards: Eficacia · Conv Rate · Bookability -->
<div class="ar-cards-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">

  <!-- ── CARD 1: Eficacia / NoDispo ── -->
  <div class="kpi-card" id="kpicard-ar1" style="border:1px solid var(--rule);padding:0;border-radius:3px;background:var(--paper);">
    <!-- Header título -->
    <div style="padding:12px 16px 0;">
      <div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;" id="ar-card1-lbl">Eficacia</div>
      <div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
        <div>
          <div id="ar-kpi-1" style="font-size:36px;font-weight:700;letter-spacing:-.02em;color:var(--accent);line-height:1;">—</div>

        </div>
        <div style="padding-top:4px;"><span id="ar1-badge" class="sev-badge" style="font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:6px 12px;border-radius:3px;display:inline-flex;align-items:center;white-space:nowrap;">—</span></div>
      </div>
      <div id="ar1-gauge" style="display:flex;gap:2px;margin-top:10px;"></div>
      <div id="ar1-wowbox" style="margin-top:8px;background:var(--paper-soft);border-radius:3px;padding:6px;display:flex;align-items:stretch;gap:6px;"></div>
    </div>


    <!-- Pills + searchbox card 1 -->
    <div style="padding:10px 16px 0;">
      <!-- AR hotel-only: pills de vista removidas (A1) -->
      <div id="ar1-hfilt" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;"><span id="ar1-f-crit" class="ar1-fpill" onclick="ar_setPillFilt(1,'crit',this)" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid #8A8377;background:#E8E6E3;color:#333132;">Críticos</span><span id="ar1-f-br" class="ar1-fpill" onclick="ar_setPillFilt(1,'br',this)" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid var(--rule);background:transparent;color:var(--ink-muted);">Bajo Rend.</span><span id="ar1-f-sc" class="ar1-fpill" onclick="ar_setPillFilt(1,'sc',this)" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid var(--rule);background:transparent;color:var(--ink-muted);">Sin Conv.</span></div>
      <div id="ar1-cross-pills" style="display:none;flex-wrap:wrap;gap:6px;margin-top:6px;margin-bottom:2px;"></div>
      <div style="display:flex;justify-content:flex-start;margin-bottom:6px;">
        <div class="sb-pill" style="display:flex;align-items:center;gap:5px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:20px;padding:3px 10px;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="sb-ar1" placeholder="Buscar…" data-sb-pill="true" data-sb-pill-accent="#5C469C" data-sb-count-id="cnt-ar1" data-sb-clear-id="sb-ar1-clear" autocomplete="off" spellcheck="false" style="background:none;border:none;outline:none;font-size:11px;color:var(--ink);width:100px;font-family:'Geist',sans-serif;"/>
          <button id="sb-ar1-clear" type="button" style="display:none;background:none;border:none;cursor:pointer;padding:0;line-height:1;color:var(--ink-muted);font-size:13px;">×</button>
        </div>
      </div>
    </div>
    <!-- Filas -->
    <div id="ar1-rows-wrap" style="padding:0 16px 0;">
      <div id="ar1-th" class="kpi-tab-rows"></div>
      <div style="text-align:center;margin-top:4px;padding:0 16px;" id="ar1-more-wrap"><button id="ar1-th-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;width:100%;margin-top:4px;">Ver más ▾</button></div>
    </div>
        <!-- Canvas histórico card 1 -->
    <div style="padding:0 16px 16px;">
      <div id="ar1-hist-cr" style="margin-top:12px;display:block;">{HIST_CR_PANEL}</div>
      <div id="ar1-hist-rnd" style="margin-top:12px;display:none;">{HIST_RND_PANEL}</div>
    </div>
  </div>

  <!-- ── CARD 2: Conv Rate / IPM ── -->
  <div class="kpi-card" id="kpicard-ar2" style="border:1px solid var(--rule);padding:0;border-radius:3px;background:var(--paper);">
    <!-- Header título -->
    <div style="padding:12px 16px 0;">
      <div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;" id="ar-card2-lbl">Conv Rate</div>
      <div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
        <div>
          <div id="ar-kpi-2" style="font-size:36px;font-weight:700;letter-spacing:-.02em;color:var(--accent);line-height:1;">—</div>

        </div>
        <div style="padding-top:4px;"><span id="ar2-badge" class="sev-badge" style="font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:6px 12px;border-radius:3px;display:inline-flex;align-items:center;white-space:nowrap;">—</span></div>
      </div>
      <div id="ar2-gauge" style="display:flex;gap:2px;margin-top:10px;"></div>
      <div id="ar2-wowbox" style="margin-top:8px;background:var(--paper-soft);border-radius:3px;padding:6px;display:flex;align-items:stretch;gap:6px;"></div>
    </div>


    <!-- Pills + searchbox card 2 -->
    <div style="padding:10px 16px 0;">
      <!-- AR hotel-only: pills de vista removidas (A1) -->
      <div id="ar2-hfilt" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;"><span id="ar2-f-crit" class="ar2-fpill" onclick="ar_setPillFilt(2,'crit',this)" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid #8A8377;background:#E8E6E3;color:#333132;">Críticos</span><span id="ar2-f-br" class="ar2-fpill" onclick="ar_setPillFilt(2,'br',this)" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid var(--rule);background:transparent;color:var(--ink-muted);">Bajo Rend.</span><span id="ar2-f-sc" class="ar2-fpill" onclick="ar_setPillFilt(2,'sc',this)" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid var(--rule);background:transparent;color:var(--ink-muted);">Sin Conv.</span></div>
      <div id="ar2-cross-pills" style="display:none;flex-wrap:wrap;gap:6px;margin-top:6px;margin-bottom:2px;"></div>
      <div style="display:flex;justify-content:flex-start;margin-bottom:6px;">
        <div class="sb-pill" style="display:flex;align-items:center;gap:5px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:20px;padding:3px 10px;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="sb-ar2" placeholder="Buscar…" data-sb-pill="true" data-sb-pill-accent="#5C469C" data-sb-count-id="cnt-ar2" data-sb-clear-id="sb-ar2-clear" autocomplete="off" spellcheck="false" style="background:none;border:none;outline:none;font-size:11px;color:var(--ink);width:100px;font-family:'Geist',sans-serif;"/>
          <button id="sb-ar2-clear" type="button" style="display:none;background:none;border:none;cursor:pointer;padding:0;line-height:1;color:var(--ink-muted);font-size:13px;">×</button>
        </div>
      </div>
    </div>
    <!-- Filas -->
    <div id="ar2-rows-wrap" style="padding:0 16px 0;">
      <div id="ar2-th" class="kpi-tab-rows"></div>
      <div style="text-align:center;margin-top:4px;padding:0 16px;" id="ar2-more-wrap"><button id="ar2-th-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;width:100%;margin-top:4px;">Ver más ▾</button></div>
    </div>
        <!-- Canvas histórico card 2 -->
    <div style="padding:0 16px 16px;">
      <div id="ar2-hist-cr" style="margin-top:12px;display:block;">{HIST_CR_PANEL_CV}</div>
      <div id="ar2-hist-rnd" style="margin-top:12px;display:none;">{HIST_RND_PANEL_IPM}</div>
    </div>
  </div>

  <!-- ── CARD 3: Bookability ── -->
  <div class="kpi-card" id="kpicard-ar3" style="border:1px solid var(--rule);padding:0;border-radius:3px;background:var(--paper);">
    <!-- Header título -->
    <div style="padding:12px 16px 0;">
      <div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;" id="ar-card3-lbl">Bookability</div>
      <div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
        <div>
          <div id="ar-kpi-3" style="font-size:36px;font-weight:700;letter-spacing:-.02em;color:#333132;line-height:1;">—</div>

        </div>
        <div style="padding-top:4px;"><span id="ar3-badge" class="sev-badge" style="font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:6px 12px;border-radius:3px;display:inline-flex;align-items:center;white-space:nowrap;">—</span></div>
      </div>
      <div id="ar3-gauge" style="display:flex;gap:2px;margin-top:10px;"></div>
      <div id="ar3-wowbox" style="margin-top:8px;background:var(--paper-soft);border-radius:3px;padding:6px;display:flex;align-items:stretch;gap:6px;"></div>
    </div>
    <!-- Pills + searchbox card 3 BK -->
    <div style="padding:10px 16px 0;">
      <!-- AR hotel-only: pills de vista removidas (A1) -->
      <div id="ar3-htab-row" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;"><span id="ar3-htab-crit" class="ar3-htab-pill" onclick="ar3_setHotelTab('crit')" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid #8A8377;background:#E8E6E3;color:#333132;">Críticos</span><span id="ar3-htab-br" class="ar3-htab-pill" onclick="ar3_setHotelTab('br')" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid var(--rule);background:transparent;color:var(--ink-muted);">Bajo Rend.</span><span id="ar3-htab-sc" class="ar3-htab-pill" onclick="ar3_setHotelTab('sc')" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;border:1px solid var(--rule);background:transparent;color:var(--ink-muted);">Sin Conv.</span></div>
      <div style="display:flex;justify-content:flex-start;margin-bottom:6px;" id="ar3-sb-wrap">
        <div class="sb-pill" style="display:flex;align-items:center;gap:5px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:20px;padding:3px 10px;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="ar3-sb" placeholder="Buscar…" data-sb-pill="true" data-sb-pill-accent="#5C469C" data-sb-count-id="cnt-ar3" data-sb-clear-id="ar3-sb-clear" autocomplete="off" spellcheck="false" style="background:none;border:none;outline:none;font-size:11px;color:var(--ink);width:100px;font-family:'Geist',sans-serif;"/>
          <button id="ar3-sb-clear" type="button" style="display:none;background:none;border:none;cursor:pointer;padding:0;line-height:1;color:var(--ink-muted);font-size:13px;">×</button>
        </div>
      </div>
    </div>
    <!-- Panel tabla -->
    <div id="ar3-panel" style="padding:0 16px 0;">
      <div id="ar3-tbody" class="kpi-tab-rows" style="padding-top:4px;"></div>
      <div style="margin-top:4px;">
        <button id="ar3-more-btn" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:6px 16px;cursor:pointer;border-radius:3px;width:100%;margin-top:4px;">Ver más ▾</button>
      </div>
    </div>
    <div style="padding:0 16px 16px;">
      <div id="ar3-hist-bk" style="margin-top:12px;display:block;">{HIST_BK_PANEL}</div>
    </div>
    </div><!-- /grid 3 cards -->
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
    <div id="supply-loading-bar" style="width:0%;height:100%;background:#EA0074;border-radius:2px;transition:width .4s ease;"></div>
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
    + _strip_last_script(p2_cr) + '\n'   # severity CR (script datos ya en FOOTER_JS)
    + p3_cr + '\n'
    + '</section>\n'  # cierra section-cr (abierta por p1_cr)
    + '</div>\n'      # cierra w22-kpis-cr
    + '<div id="w22-kpis-rnd" style="display:none;">\n'
    + p1_rnd + '\n'
    + _strip_last_script(p2_rnd) + '\n'  # severity RND (script datos ya en FOOTER_JS)
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
    + '''
<script>
/* ═══════════════════════════════════════════════════════════════════
   OVERRIDE DEFINITIVO DEL TOOLTIP HISTÓRICO (W23+)
   Reemplaza TODOS los onmousemove de los canvas históricos con una
   única función que calcula la semana correctamente desde el número
   real de puntos en VALS_DEF. Corre al final, después de todos los
   demás bindings, así que gana.
   ═══════════════════════════════════════════════════════════════════ */
(function() {
  /* Semanas base — la última semana es la actual */
  var SEMANAS_FULL = (typeof _SEMANAS_HIST !== 'undefined' && _SEMANAS_HIST.length)
    ? _SEMANAS_HIST
    : ["W16","W17","W18","W19","W20","W21","W22","W23"];

  function _tip() {
    var t = document.getElementById('w22-canvas-tip');
    if (!t) {
      t = document.createElement('div');
      t.id = 'w22-canvas-tip';
      t.style.cssText = 'position:fixed;pointer-events:none;display:none;background:#333132;color:#fff;font-size:10px;font-weight:700;padding:4px 8px;border-radius:3px;z-index:99999;white-space:nowrap;';
      document.body.appendChild(t);
    }
    return t;
  }

  /* Obtener los valores (vals) de un canvas. PRIORIDAD MÁXIMA: _HIST_CANON
     (registrado por historico_module con los VALS_DEF correctos de 8 puntos).
     W22_CANVAS_CFG puede tener datos viejos de 5-7 puntos por demo_js_main. */
  function _getVals(cid) {
    if (typeof window._HIST_CANON !== 'undefined' && window._HIST_CANON[cid] && window._HIST_CANON[cid].vals) {
      return window._HIST_CANON[cid].vals;
    }
    if (typeof W22_CANVAS_CFG !== 'undefined' && W22_CANVAS_CFG[cid] && W22_CANVAS_CFG[cid].vals) {
      return W22_CANVAS_CFG[cid].vals;
    }
    if (typeof HIST_CR !== 'undefined' && HIST_CR[cid] && HIST_CR[cid].vals) return HIST_CR[cid].vals;
    if (typeof HIST_RND !== 'undefined' && HIST_RND[cid] && HIST_RND[cid].vals) return HIST_RND[cid].vals;
    return null;
  }

  /* Obtener las semanas canónicas de un canvas desde _HIST_CANON */
  function _getSemanas(cid) {
    if (typeof window._HIST_CANON !== 'undefined' && window._HIST_CANON[cid] && window._HIST_CANON[cid].semanas) {
      return window._HIST_CANON[cid].semanas;
    }
    return null;
  }

  function _getMetric(cid) {
    if (typeof W22_CANVAS_CFG !== 'undefined' && W22_CANVAS_CFG[cid] && W22_CANVAS_CFG[cid].metric) {
      return W22_CANVAS_CFG[cid].metric;
    }
    if (cid.indexOf('ipm') > -1) return 'ipm';
    if (cid.indexOf('cv') > -1 || cid.indexOf('convrate') > -1) return 'convrate';
    if (cid.indexOf('nd') > -1 || cid.indexOf('nodispo') > -1) return 'nodispo';
    if (cid.indexOf('bk') > -1) return 'bookability';
    return 'eficacia';
  }

  /* Mapear índice de punto → etiqueta de semana.
     CLAVE: la última semana de SEMANAS_FULL corresponde al ÚLTIMO punto (vals.length-1).
     Entonces alineamos por la derecha: el punto i corresponde a
     SEMANAS_FULL[SEMANAS_FULL.length - vals.length + i] */
  function _semForIndex(i, n, cid) {
    /* Si el canvas tiene sus propias semanas registradas y coinciden en longitud, usarlas */
    var canonSems = cid ? _getSemanas(cid) : null;
    if (canonSems && canonSems.length === n) {
      return canonSems[i] || ('W' + (16 + i));
    }
    /* Sino, alinear por la derecha: último punto = última semana */
    var offset = SEMANAS_FULL.length - n;
    var idx = offset + i;
    if (idx >= 0 && idx < SEMANAS_FULL.length) return SEMANAS_FULL[idx];
    return 'W' + (16 + i);
  }

  function _fmtVal(val, metric) {
    if (metric === 'ipm') {
      return '$' + Math.round(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    return val.toFixed(2) + '%';
  }

  function _bindCanvas(el) {
    if (!el || el._tipOverride) return;
    el._tipOverride = true;
    var cid = el.id;

    el.addEventListener('mousemove', function(e) {
      var vals = _getVals(cid);
      if (!vals || !vals.length) return;
      var rect = el.getBoundingClientRect();
      var mx = e.clientX - rect.left;
      var w = rect.width;
      var n = vals.length;
      /* Encontrar el punto más cercano */
      var best = -1, bestDx = 9999;
      for (var i = 0; i < n; i++) {
        var px = (i / (n - 1)) * w;
        var dx = Math.abs(px - mx);
        if (dx < bestDx) { bestDx = dx; best = i; }
      }
      if (best < 0 || bestDx > 40) { _tip().style.display = 'none'; return; }
      var metric = _getMetric(cid);
      var sem = _semForIndex(best, n, cid);
      var t = _tip();
      t.textContent = sem + ': ' + _fmtVal(vals[best], metric);
      t.style.display = 'block';
      /* Posicionar el tooltip SOBRE el punto del canvas (no en el cursor) para que
         siempre quede dentro/cerca de la gráfica, no flotando lejos */
      var pointX = rect.left + (best / (n - 1)) * w;
      var pointY = rect.top;  /* arriba del canvas */
      /* Medir el ancho del tooltip para centrarlo sobre el punto */
      var tipW = t.offsetWidth || 70;
      var leftPx = pointX - (tipW / 2);
      /* Clamp horizontal para no salirse de la pantalla */
      if (leftPx < 4) leftPx = 4;
      if (leftPx + tipW > window.innerWidth - 4) leftPx = window.innerWidth - tipW - 4;
      t.style.left = leftPx + 'px';
      t.style.top = (pointY - 30) + 'px';
      /* Detener otros listeners (los viejos con semanas incorrectas) */
      e.stopImmediatePropagation();
    }, true);  /* capture = corre PRIMERO, antes que otros listeners */

    el.addEventListener('mouseleave', function() {
      var t = document.getElementById('w22-canvas-tip');
      if (t) t.style.display = 'none';
    }, true);
  }

  function _bindAll() {
    /* Todos los canvas históricos conocidos */
    var ids = ['hcr-global-ef','hcr-global-cv','h-bk-global','hrnd-global-nd','hrnd-global-ipm',
               'hcr-panel-ef','hcr-panel-cv','hrnd-panel-nd','hrnd-panel-ipm',
               'h-bk-panel','h-bk-dim','hcr-dim-ef','hcr-dim-cv'];
    ids.forEach(function(id) {
      var el = document.getElementById(id);
      if (el) _bindCanvas(el);
    });
    /* También cualquier canvas dentro de un módulo histórico */
    document.querySelectorAll('canvas[id^="h-"], canvas[id^="hcr-"], canvas[id^="hrnd-"]').forEach(_bindCanvas);
  }

  /* Bind repetido para capturar canvas que se crean tarde */
  [200, 600, 1200, 2500, 4000].forEach(function(d) { setTimeout(_bindAll, d); });
  window.addEventListener('load', function() { setTimeout(_bindAll, 300); });
  if (document.readyState !== 'loading') _bindAll();
  else document.addEventListener('DOMContentLoaded', _bindAll);
})();
</script>
'''
    + f'''
<div class="footer-bar" style="width:100%;margin:40px 0 0;padding:20px 24px;background:var(--paper);border-top:1px solid var(--rule);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;box-sizing:border-box;">
  <div class="footer-downloads" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
    <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--ink-muted);">Descargas W{VOL_NUM}</span>
    <a href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{VOL_NUM}/Analisis_CheckRates_W{VOL_NUM}.xlsx" style="font-size:11px;font-weight:700;color:#fff;text-decoration:none;padding:7px 16px;background:var(--ink);border-radius:3px;">⬇ Excel CheckRates</a>
    <a href="https://raw.githubusercontent.com/federicochurches/Price/main/rates-nodispo/week-{VOL_NUM}/Analisis_RatesNoDispo_W{VOL_NUM}.xlsx" style="font-size:11px;font-weight:700;color:#fff;text-decoration:none;padding:7px 16px;background:var(--ink);border-radius:3px;">⬇ Excel Rates No Dispo</a>
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

# ── Auditoría del HTML (composición · duplicados · presupuesto · huérfanos) ──
# No fatal: si check_html falla por cualquier motivo, el build ya está escrito.
try:
    import check_html
    check_html.report(str(out))
except Exception as _e:
    print(f'[check_html] aviso: no se pudo correr la auditoría ({_e})')

