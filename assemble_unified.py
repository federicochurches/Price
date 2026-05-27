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
_nd_val  = DR.get('M',{}).get(f'global_w{VOL_NUM}',{}).get('nodispo', 0.0263)

HIST_CR_PANEL  = _rh('cr',  'eficacia', _bef(_ef_val), _ef_val, 'hcr-panel-ef')
HIST_RND_PANEL = _rh('rnd', 'nodispo',  _bnd(_nd_val), _nd_val, 'hrnd-panel-nd')
HIST_CR_DIM    = _rh('cr',  'eficacia', _bef(_ef_val), _ef_val, 'hcr-dim-ef')
HIST_RND_DIM   = _rh('rnd', 'nodispo',  _bnd(_nd_val), _nd_val, 'hrnd-dim-nd')

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
    """Retorna array de 5 valores [W17,W18,W19,W20,W21] para canvas."""
    base = _HD.get(mode, {}).get(metric, {}).get(canasta, [])
    if actual_val is not None and len(base) == 4:
        return base + [actual_val]
    return base

# Cargar valores actuales del pickle para el 5° punto
import pickle as _pkl
with open(f'cr_w21_data.pkl', 'rb') as _f:
    _D_cr = _pkl.load(_f)
with open(f'rnd_w21_data.pkl', 'rb') as _f:
    _D_rnd = _pkl.load(_f)

_M_cr  = _D_cr.get('M', {})
_M_rnd = _D_rnd.get('M', {})

_HIST_CR_PY = {
    # Canvas de las cards KPI (global) — IDs fijos en el DOM
    'hcr-global-ef': {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w21',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'hcr-global-cv': {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get('global_w21',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    # Canvas del panel de análisis (por canasta)
    'hcr-panel-ef':  {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w21',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    # Canvas de dimensiones
    'hcr-dim-ef':    {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w21',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    # Canvas por canasta (para w22_setMode cuando cambia canasta)
    'h-global-ef':   {'vals': _hist_vals('cr','eficacia','global', round(_M_cr.get('global_w21',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-global-cv':   {'vals': _hist_vals('cr','convrate','global', round(_M_cr.get('global_w21',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-op-ef':       {'vals': _hist_vals('cr','eficacia','op',     round(_M_cr.get('B2B (OP)_w21',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-op-cv':       {'vals': _hist_vals('cr','convrate','op',     round(_M_cr.get('B2B (OP)_w21',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-cug-ef':      {'vals': _hist_vals('cr','eficacia','cug',    round(_M_cr.get('CUG (UOP)_w21',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-cug-cv':      {'vals': _hist_vals('cr','convrate','cug',    round(_M_cr.get('CUG (UOP)_w21',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
    'h-b2c-ef':      {'vals': _hist_vals('cr','eficacia','b2c',    round(_M_cr.get('B2C_w21',{}).get('eficacia',0)*100,2)), 'target': 97.0},
    'h-b2c-cv':      {'vals': _hist_vals('cr','convrate','b2c',    round(_M_cr.get('B2C_w21',{}).get('conv_rate',0)*100,2)), 'target': 2.5},
}

_HIST_RND_PY = {
    'hrnd-global-nd':  {'vals': _hist_vals('rnd','nodispo','global', round(_M_rnd.get('global_w21',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-global-ipm': {'vals': _hist_vals('rnd','ipm','global',     round(_M_rnd.get('global_w21',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-op-nd':      {'vals': _hist_vals('rnd','nodispo','op',     round(_M_rnd.get('B2B (OP)_w21',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-op-ipm':     {'vals': _hist_vals('rnd','ipm','op',         round(_M_rnd.get('B2B (OP)_w21',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-cug-nd':     {'vals': _hist_vals('rnd','nodispo','cug',    round(_M_rnd.get('CUG (UOP)_w21',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-cug-ipm':    {'vals': _hist_vals('rnd','ipm','cug',        round(_M_rnd.get('CUG (UOP)_w21',{}).get('rpm',0),0)), 'target': 650.0},
    'hrnd-b2c-nd':     {'vals': _hist_vals('rnd','nodispo','b2c',    round(_M_rnd.get('B2C_w21',{}).get('pct_nodispo',0)*100,2)), 'target': 3.0},
    'hrnd-b2c-ipm':    {'vals': _hist_vals('rnd','ipm','b2c',        round(_M_rnd.get('B2C_w21',{}).get('rpm',0),0)), 'target': 650.0},
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
    '<style>\n' + open('/mnt/project/demo_css_w22.css', encoding='utf-8').read() + '\n</style>\n'
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

/* Listener del panel — registrado en document para capturar clicks en w22-th/w22-td */
document.addEventListener('click', function(e) {
  var row = e.target.closest ? e.target.closest('[data-hist-w21]') : null;
  if (!row) return;
  var tbody = row.closest('tbody');
  if (!tbody || (tbody.id !== 'w22-th' && tbody.id !== 'w22-td')) return;

  var label = row.getAttribute('data-hist-label') || '';
  var w21   = parseFloat(row.getAttribute('data-hist-w21'));
  var w20   = parseFloat(row.getAttribute('data-hist-w20'));
  if (isNaN(w21)) return;
  if (isNaN(w20)) w20 = w21;

  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
  var isPh = tbody.id === 'w22-th';
  var cid  = isPh ? (isCR ? 'hcr-panel-ef' : 'hrnd-panel-nd')
                  : (isCR ? 'hcr-dim-ef'   : 'hrnd-dim-nd');

  /* Segundo click → deseleccionar y volver a Global */
  var isAlreadySelected = row.getAttribute('data-selected') === '1';
  tbody.querySelectorAll('[data-hist-w21]').forEach(function(r){
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
    W22_CANVAS_CFG[id] = {vals: nv, semanas: oc.semanas || ['W17','W18','W19','W20','W21'], metric: oc.metric};
  }
  _updateCfg(cid);

  /* Forzar onmousemove en ambos canvas con closure sobre los vals correctos */
  [cid, globalCid].forEach(function(id) {
    var canvasEl = document.getElementById(id);
    if (!canvasEl) return;
    (function(capturedId, capturedW21, capturedW20){
      var sems = ['W17','W18','W19','W20','W21'];
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

SWITCHER = f'''<div style="padding-top:20px;">
<div class="w22-seg">
  <button class="w22-seg-btn on" id="mode-cr" onclick="w22_setMode('cr',this)">CheckRates</button>
  <button class="w22-seg-btn" id="mode-rnd" onclick="w22_setMode('rnd',this)">Rates No Dispo</button>
</div>
</div>
<div id="w22-filter-wrap" style="margin-top:16px;">
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
<div class="section-head"><div>
<h2 class="section-title">Alertas Críticas</h2>
<span class="section-subtitle" id="w22-alertas-sub" style="color:var(--accent)">Peor Eficacia + Peor ConvRate · canasta activa</span>
</div></div>
<div id="w22-alertas" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;"></div>
</section>

<section style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Análisis de Rendimiento</h2>
<span class="section-subtitle" style="color:var(--accent)">Top hoteles y dimensiones · canasta activa</span>
</div></div>
<div class="vsw" style="display:flex;align-items:stretch;border:1px solid var(--rule);border-bottom:none;background:var(--paper-soft);">
  <div style="display:flex;align-items:center;padding:0 16px;font-size:9px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-muted);border-right:1px solid var(--rule);white-space:nowrap;min-width:72px;">Vista</div>
  <div class="v-chip on" id="vch-h" style="display:flex;align-items:center;gap:6px;padding:0 22px;height:38px;font-size:10px;font-weight:700;text-transform:uppercase;cursor:pointer;border-right:1px solid var(--rule);background:var(--paper);color:var(--ink);" onclick="w22_setView('hotel')">🏨&nbsp;&nbsp;Por Hotel</div>
  <div class="v-chip" id="vch-d" style="display:flex;align-items:center;gap:6px;padding:0 22px;height:38px;font-size:10px;font-weight:700;text-transform:uppercase;cursor:pointer;border-right:1px solid var(--rule);color:var(--ink-muted);" onclick="w22_setView('dim')">📊&nbsp;&nbsp;Por Dimensión</div>
</div>
<div id="w22-ph" style="border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);">
  <div class="tabs-row" style="margin-top:0;">
    <label class="tab-label tab-label-active" onclick="w22_setHotelTab('crit',this)" id="w22-tab-lbl-1">Críticos</label>
    <label class="tab-label" onclick="w22_setHotelTab('br',this)" id="w22-tab-lbl-2">Bajo Rendimiento</label>
    <label class="tab-label" onclick="w22_setHotelTab('sc',this)" id="w22-tab-lbl-3">Sin Conversión</label>
    <label class="tab-label" onclick="w22_setHotelTab('cv',this)" id="w22-tab-lbl-4">Menor ConvRate</label>
    {SB_PANEL_TH}
  </div>
  <div style="padding-top:14px;">
    <table style="width:100%;border-collapse:collapse;table-layout:fixed;">
      <colgroup>
        <col/><col style="width:100px"/><col style="width:64px"/><col style="width:44px"/>
        <col style="width:68px"/><col style="width:44px"/><col style="width:84px"/><col style="width:44px"/>
      </colgroup>
      <thead><tr style="border-bottom:2px solid var(--accent);">
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);text-align:left;padding:6px 0 6px 12px;" id="w22-th-lbl-hotel">Hotel</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:left;padding:6px 4px;">Severity</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 4px;" id="w22-th-col3">Tráfico</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 2px;">WoW↕</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 4px;" id="w22-th-col4">Eficacia</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 2px;">WoW↕</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 4px;" id="w22-th-col5">Conv Rate</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 8px 6px 2px;">WoW↕</th>
      </tr></thead>
      <tbody id="w22-th"></tbody>
    </table>
    <div style="text-align:center;margin-top:10px;">
      <button id="w22-th-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:7px 20px;cursor:pointer;border-radius:3px;"></button>
    </div>
  </div>
  <div id="w22-panel-hist-cr"  style="margin-top:16px;display:block;">{HIST_CR_PANEL}</div>
  <div id="w22-panel-hist-rnd" style="margin-top:16px;display:none;">{HIST_RND_PANEL}</div>
</div>
<div id="w22-pd" style="display:none;border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);">
  <div class="tabs-row" style="margin-top:0;margin-bottom:14px;">
    <label class="tab-label tab-label-active" onclick="w22_setDim('corp');w22_iTab(this);" id="w22-dim-lbl-corp">Corporativo</label>
    <label class="tab-label" onclick="w22_setDim('dest');w22_iTab(this);" id="w22-dim-lbl-dest">Destino</label>
    <label class="tab-label" onclick="w22_setDim('chan');w22_iTab(this);" id="w22-dim-lbl-chan">Canal</label>
    {SB_PANEL_TD}
  </div>
  <table style="width:100%;border-collapse:collapse;table-layout:fixed;">
    <colgroup>
      <col/><col style="width:100px"/><col style="width:64px"/><col style="width:44px"/>
      <col style="width:68px"/><col style="width:44px"/><col style="width:84px"/><col style="width:44px"/>
    </colgroup>
    <thead><tr style="border-bottom:2px solid var(--accent);">
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);text-align:left;padding:6px 0 6px 12px;" id="w22-th-dim">Corporativo</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:left;padding:6px 4px;">Severity</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 4px;" id="w22-td-col3">Tráfico</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 2px;">WoW↕</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 4px;" id="w22-td-col4">Eficacia</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 2px;">WoW↕</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 4px;" id="w22-td-col5">ConvRate</th>
        <th style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:6px 8px 6px 2px;">WoW↕</th>
      </tr></thead>
    <tbody id="w22-td"></tbody>
  </table>
  <div style="text-align:center;margin-top:10px;">
    <button id="w22-td-more" style="display:none;font-family:'Geist',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--rule);color:var(--ink-muted);padding:7px 20px;cursor:pointer;border-radius:3px;"></button>
  </div>
  <div id="w22-panel-dim-hist-cr"  style="margin-top:16px;display:block;">{HIST_CR_DIM}</div>
  <div id="w22-panel-dim-hist-rnd" style="margin-top:16px;display:none;">{HIST_RND_DIM}</div>
</div>
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
    
    console.log('✓ HIST_CR y HIST_RND configurados para tooltip');
}
</script>
'''
    + GLOBAL_PANEL_SCRIPT
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
