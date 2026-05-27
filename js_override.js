/* Parchear w22_redrawCanvas para incluir HIST_RND */
var _origRedraw = w22_redrawCanvas;
w22_redrawCanvas = function(accent){
  /* Dibujar canvas CR (original) */
  _origRedraw(accent);
  /* Dibujar canvas RND si modo es rnd */
  if(W.mode === 'rnd'){
    var rgb = RGB[accent] || '234,0,116';
    Object.keys(HIST_RND).forEach(function(cid){
      var cfg = HIST_RND[cid];
      var el = document.getElementById(cid);
      if(!el || !el.getContext) return;
      el.width = el.offsetWidth || 400; el.height = 76;
      var ctx = el.getContext('2d');
      var vals = cfg.vals; var h = el.height - 10;
      var mn = Math.min.apply(null,vals), mx = Math.max.apply(null,vals), dR = mx-mn+0.0001;
      var pts = vals.map(function(v,i){ return {x:(i/(vals.length-1))*el.width, y:el.height-((v-mn)/dR*h+5)}; });
      var tY = el.height - ((cfg.target-mn)/dR*h+5);
      ctx.clearRect(0,0,el.width,el.height);
      ctx.strokeStyle='rgba(0,0,0,0.15)'; ctx.lineWidth=1; ctx.setLineDash([3,2]);
      ctx.beginPath(); ctx.moveTo(0,tY); ctx.lineTo(el.width,tY); ctx.stroke(); ctx.setLineDash([]);
      ctx.beginPath(); ctx.moveTo(pts[0].x,el.height); ctx.lineTo(pts[0].x,pts[0].y);
      for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y);
      ctx.lineTo(pts[pts.length-1].x,el.height); ctx.closePath();
      ctx.fillStyle='rgba('+rgb+',0.12)'; ctx.fill();
      ctx.strokeStyle=accent; ctx.lineWidth=2; ctx.lineCap='round'; ctx.lineJoin='round';
      ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
      for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.stroke();
      for(var i=0;i<pts.length;i++){
        var last = i===pts.length-1;
        ctx.fillStyle = last?accent:'rgba('+rgb+',0.5)'; ctx.globalAlpha = last?1:0.5;
        ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3:2,0,2*Math.PI); ctx.fill(); ctx.globalAlpha=1;
      }
      /* Bind tooltip RND */
      if (typeof w22_bindCanvasTip === 'function') {
        var metric_rnd = cid.indexOf('ipm')>-1?'ipm':'nodispo';
        w22_bindCanvasTip(el, cid, {vals:cfg.vals, semanas:['W17','W18','W19','W20','W21'], metric:metric_rnd}, pts);
      }
    });
  }
  /* También redibujar canvas del panel CR cuando modo=cr */
  if(W.mode === 'cr'){
    var rgb2 = RGB[accent] || '92,70,156';
    ['hcr-panel-ef','hcr-panel-cv','hcr-dim-ef'].forEach(function(cid){
      var cfg = HIST_CR[cid]; if(!cfg) return;
      var el = document.getElementById(cid);
      if(!el || !el.getContext) return;
      el.width = el.offsetWidth || 400; el.height = 76;
      var ctx = el.getContext('2d');
      var vals = cfg.vals; var h = el.height - 10;
      var mn = Math.min.apply(null,vals), mx = Math.max.apply(null,vals), dR = mx-mn+0.0001;
      var pts = vals.map(function(v,i){ return {x:(i/(vals.length-1))*el.width, y:el.height-((v-mn)/dR*h+5)}; });
      var tY = el.height - ((cfg.target-mn)/dR*h+5);
      ctx.clearRect(0,0,el.width,el.height);
      ctx.strokeStyle='rgba(0,0,0,0.15)'; ctx.lineWidth=1; ctx.setLineDash([3,2]);
      ctx.beginPath(); ctx.moveTo(0,tY); ctx.lineTo(el.width,tY); ctx.stroke(); ctx.setLineDash([]);
      ctx.beginPath(); ctx.moveTo(pts[0].x,el.height); ctx.lineTo(pts[0].x,pts[0].y);
      for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y);
      ctx.lineTo(pts[pts.length-1].x,el.height); ctx.closePath();
      ctx.fillStyle='rgba('+rgb2+',0.12)'; ctx.fill();
      ctx.strokeStyle=accent; ctx.lineWidth=2; ctx.lineCap='round'; ctx.lineJoin='round';
      ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
      for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.stroke();
      for(var i=0;i<pts.length;i++){
        var last = i===pts.length-1;
        ctx.fillStyle = last?accent:'rgba('+rgb2+',0.5)'; ctx.globalAlpha = last?1:0.5;
        ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3:2,0,2*Math.PI); ctx.fill(); ctx.globalAlpha=1;
      }
      /* Bind tooltip CR panel */
      if (typeof w22_bindCanvasTip === 'function') {
        var metric_cr = cid.indexOf('cv')>-1?'convrate':'eficacia';
        w22_bindCanvasTip(el, cid, {vals:cfg.vals, semanas:['W17','W18','W19','W20','W21'], metric:metric_cr}, pts);
      }
    });
  }
};

/* Patch cv() y data() para que usen las vars correctas según modo */
function cv(){
  var cv_data = W.mode==='cr' ? CR_CV : RND_CV;
  return cv_data[W.canasta] || cv_data['global'];
}
function data(){
  var d_data = W.mode==='cr' ? CR_D : RND_D;
  return d_data[W.canasta] || d_data['global'];
}
function al(){
  var al_data = W.mode==='cr' ? CR_AL : RND_AL;
  return al_data[W.canasta] || al_data['global'];
}

/* Patch w22_setDim — cambiar datos de tabla dimensión según Corp/Dest/Chan */
var _currentDim = 'corp';

function _renderChanSplit(dd) {
  var tbody = document.getElementById('w22-td');
  var btnMore = document.getElementById('w22-td-more');
  if (!tbody) return;
  if (btnMore) btnMore.style.display = 'none';
  var pp = dd.chans_pp || [];
  var tp = dd.chans_tp || [];
  var accent = W.mode === 'cr' ? '#5C469C' : '#EA0074';
  var cyan = '#4FC3F4';
  function headerRow(label, col) {
    return '<tr><td colspan="7" style="padding:8px 0 4px 12px;font-size:9px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:'+col+';border-bottom:2px solid '+col+';border-top:1px solid var(--rule-soft);">'+label+'</td></tr>';
  }
  var html = '';
  if (pp.length) {
    html += headerRow('\uD83C\uDFE0 Producto Propio', accent);
    pp.forEach(function(r){ html += trow(r); });
  }
  if (tp.length) {
    html += headerRow('\uD83D\uDD0C Third Party', cyan);
    tp.forEach(function(r){ html += trow(r); });
  }
  tbody.innerHTML = html;
}

w22_setDim = function(d) {
  _currentDim = d;
  var l = {corp:'Corporativo', dest:'Destino', chan:'Channel'};
  var thd = document.getElementById('w22-th-dim');
  if (thd) thd.textContent = l[d] || 'Corporativo';
  var dd = data();
  if (d === 'chan') {
    _renderChanSplit(dd);
    /* Chan usa tabla propia — inyectar en ella */
    setTimeout(function(){ if(typeof window._injectHistAttrs==="function") window._injectHistAttrs('w22-td', dd.chans || dd.dims); }, 20);
  } else {
    var rows = d === 'dest' ? (dd.dests || dd.dims) : (dd.corps || dd.dims);
    w22_renderTable('w22-td', 'w22-td-more', rows, false);
    if(typeof window._injectHistAttrs==="function") window._injectHistAttrs('w22-td', rows);
  }
};

/* Estado tab hotel activa */
var _currentHotelTab = 'crit';

function w22_setHotelTab(tab, el) {
  _currentHotelTab = tab;
  var ph = document.getElementById('w22-ph');
  if (ph) {
    ph.querySelectorAll('.tabs-row label').forEach(function(l) {
      l.classList.remove('tab-label-active');
    });
  }
  if (el) { el.classList.add('tab-label-active'); }
  var dd = data();
  var rows = tab === 'br' ? (dd.hotels_br || dd.hotels) :
             tab === 'sc' ? (dd.hotels_sc || dd.hotels) :
             tab === 'cv' ? (dd.hotels_cv || dd.hotels) :
             (dd.hotels_crit || dd.hotels);
  w22_renderTable('w22-th', 'w22-th-more', rows, false);
  if (typeof window._injectHistAttrs === 'function') window._injectHistAttrs('w22-th', rows);
}

/* Inyectar atributos hist en render inicial */
setTimeout(function(){
  var dd = data();
  var hrows = (dd.hotels_crit || dd.hotels);
  if(typeof window._injectHistAttrs==="function") window._injectHistAttrs('w22-th', hrows);
  if(typeof window._injectHistAttrs==="function") window._injectHistAttrs('w22-td', dd.dims);
}, 200);

/* _injectHistAttrs — agrega data-hist-* numericos en TRs */
window._injectHistAttrs = function _injectHistAttrs(tbodyId, rows) {
  var tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  var trs = tbody.querySelectorAll('tr');
  trs.forEach(function(tr, i) {
    var r = rows[i]; if (!r) return;
    var name   = r[0] || '';
    var w21str = r[5] || '—';
    var wow    = r[8] || '—';
    /* Extraer numero puro de w21 */
    var w21num = parseFloat(w21str.replace(/[^0-9,.]/g,'').replace(',','.'));
    if (isNaN(w21num)) return;
    /* Calcular w20 desde WoW */
    var w20num = w21num;
    if (wow && wow !== '—') {
      var isUp  = wow.charAt(0) === '▲';
      var delta = parseFloat(wow.replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
      w20num = isUp ? w21num - delta : w21num + delta;
    }
    tr.setAttribute('data-hist-label', name);
    tr.setAttribute('data-hist-w21',   w21num);
    tr.setAttribute('data-hist-w20',   w20num);
    tr.style.cursor = 'pointer';
  });
}

/* Header de columna y estilo de tab se manejan en TAB_BINDING_JS */

/* Patch w22_renderTable — auto-inject data-hist-* después de cada render */
var _origRenderTable = w22_renderTable;
w22_renderTable = function(tbodyId, btnId, rows, open) {
  _origRenderTable(tbodyId, btnId, rows, open);
  if (tbodyId === 'w22-th' || tbodyId === 'w22-td') {
    if (typeof window._injectHistAttrs === 'function') {
      window._injectHistAttrs(tbodyId, rows);
    }
  }
};

/* Patch w22_update — respetar _currentHotelTab y _currentDim */
var _origUpdate = typeof w22_update === 'function' ? w22_update : null;
w22_update = function(){
  if(_origUpdate) _origUpdate();
  var c = cv(); var col = c.col;
  /* Repintar valores KPI con color de canasta */
  if(W.mode === 'cr'){
    var kef = document.getElementById('w21-kv-ef');
    var kcv = document.getElementById('w21-kv-cv');
    if(kef){ kef.textContent = c.ef; kef.style.color = col; }
    if(kcv){ kcv.textContent = c.cv; kcv.style.color = col; }
  } else {
    var knd  = document.getElementById('w21-kv-nd');
    var krpm = document.getElementById('w21-kv-rpm');
    if(knd)  { knd.textContent  = c.ef; knd.style.color  = col; }
    if(krpm) { krpm.textContent = c.cv; krpm.style.color = col; }
  }
  var dd = data();
  /* Re-aplicar tab de hotel */
  var hrows = _currentHotelTab === 'br' ? (dd.hotels_br || dd.hotels) :
              _currentHotelTab === 'sc' ? (dd.hotels_sc || dd.hotels) :
              _currentHotelTab === 'cv' ? (dd.hotels_cv || dd.hotels) :
              (dd.hotels_crit || dd.hotels_dnc || dd.hotels);
  w22_renderTable('w22-th', 'w22-th-more', hrows, false);
  if(typeof window._injectHistAttrs==="function") window._injectHistAttrs('w22-th', hrows);
  /* Re-aplicar dimensión activa */
  if (_currentDim === 'chan') {
    _renderChanSplit(dd);
  } else {
    var drows = _currentDim === 'dest' ? (dd.dests || dd.dims) : (dd.corps || dd.dims);
    w22_renderTable('w22-td', 'w22-td-more', drows, false);
    if(typeof window._injectHistAttrs==="function") window._injectHistAttrs('w22-td', drows);
  }
  var l = {corp:'Corporativo', dest:'Destino', chan:'Channel'};
  var thd = document.getElementById('w22-th-dim');
  if(thd) thd.textContent = l[_currentDim] || 'Corporativo';
};

/* Patch w22_setMode — manejar KPI heroes con nuestros IDs */
var _origSetMode = w22_setMode;
w22_setMode = function(m, el) {
  /* Actualizar estado */
  W.mode = m; W.canasta = 'global'; W.reOpen = false;

  /* Segmented control */
  var modeCol = m==='cr' ? '#5C469C' : '#EA0074';
  var seg = document.querySelector('.w22-seg');
  if(seg){ seg.style.border='1.5px solid '+modeCol; seg.style.borderRadius='4px'; }
  var btns = document.querySelectorAll('.w22-seg-btn');
  btns.forEach(function(b,i){
    b.classList.remove('on');
    b.style.background=''; b.style.color='';
    if(i===0) b.style.borderRight='1.5px solid '+modeCol;
  });
  el.classList.add('on');
  el.style.background = modeCol; el.style.color = '#fff';

  /* Accent CSS global */
  var root = document.documentElement;
  if(m==='cr'){
    root.style.setProperty('--accent','#5C469C');
    root.style.setProperty('--accent-soft','#EDE8F7');
  } else {
    root.style.setProperty('--accent','#EA0074');
    root.style.setProperty('--accent-soft','#FCE4F1');
  }

  /* KPI heroes — mostrar/ocultar bloques */
  var cr_kpi  = document.getElementById('w22-kpis-cr');
  var rnd_kpi = document.getElementById('w22-kpis-rnd');
  if(cr_kpi)  cr_kpi.style.display  = m==='cr'  ? 'block' : 'none';
  if(rnd_kpi) rnd_kpi.style.display = m==='rnd' ? 'block' : 'none';

  /* Severity — mostrar la del modo activo */
  var sev_cr  = document.getElementById('w22-sev-cr');
  var sev_rnd = document.getElementById('w22-sev-rnd');
  if(sev_cr)  sev_cr.style.display  = m==='cr'  ? '' : 'none';
  if(sev_rnd) sev_rnd.style.display = m==='rnd' ? '' : 'none';

  /* Subtitle alertas */
  var sub = document.getElementById('w22-alertas-sub');
  if(sub) sub.textContent = m==='cr'
    ? 'Peor Eficacia + Peor ConvRate \u00b7 canasta activa'
    : 'Mayor NoDispo + Menor IPM \u00b7 canasta activa';

  /* Tab labels análisis de rendimiento */
  var t1=document.getElementById('w22-tab-lbl-1');
  var t2=document.getElementById('w22-tab-lbl-2');
  var t3=document.getElementById('w22-tab-lbl-3');
  var t4=document.getElementById('w22-tab-lbl-4');
  if(m==='cr'){
    if(t1) t1.textContent='Cr\u00edticos';
    if(t2) t2.textContent='Bajo Rendimiento';
    if(t3) t3.textContent='Sin Conversi\u00f3n';
    if(t4){ t4.style.display=''; t4.textContent='Menor ConvRate'; }
  } else {
    if(t1) t1.textContent='Demanda No Convertida';
    if(t2) t2.textContent='Bajo Rendimiento';
    if(t3) t3.textContent='Sin Conversi\u00f3n';
    if(t4) t4.style.display='none';
  }

  /* Headers tabla análisis de rendimiento */
  var th3=document.getElementById('w22-th-col3');
  var th4=document.getElementById('w22-th-col4');
  var th5=document.getElementById('w22-th-col5');
  var td3=document.getElementById('w22-td-col3');
  var td4=document.getElementById('w22-td-col4');
  var td5=document.getElementById('w22-td-col5');
  if(m==='cr'){
    if(th3)th3.textContent='Tráfico';  if(th4)th4.textContent='Eficacia'; if(th5)th5.textContent='ConvRate';
    if(td3)td3.textContent='Tráfico';  if(td4)td4.textContent='Eficacia'; if(td5)td5.textContent='ConvRate';
  } else {
    if(th3)th3.textContent='Tráfico';  if(th4)th4.textContent='NoDispo';  if(th5)th5.textContent='IPM';
    if(td3)td3.textContent='Tráfico';  if(td4)td4.textContent='NoDispo';  if(td5)td5.textContent='IPM';
  }

  /* Swap histórico del panel según modo */
  ['w22-panel-hist-cr','w22-panel-dim-hist-cr'].forEach(function(id){
    var el=document.getElementById(id); if(el) el.style.display=m==='cr'?'block':'none';
  });
  ['w22-panel-hist-rnd','w22-panel-dim-hist-rnd'].forEach(function(id){
    var el=document.getElementById(id); if(el) el.style.display=m==='rnd'?'block':'none';
  });

  /* Tab dim Channel ↔ País según modo */
  var dimChan = document.getElementById('w22-dim-lbl-chan');
  if(dimChan) dimChan.textContent = m==='cr' ? 'Channel' : 'País';

  /* Plan subtitle */
  var psub = document.getElementById('w22-plan-sub');
  if(psub) psub.textContent = (m==='cr'?'CheckRates':'Rates No Dispo') + ' \u00b7 canasta activa';

  /* Reset chips */
  document.querySelectorAll('.c-chip').forEach(function(x){
    x.classList.remove('active');
    x.style.borderBottomColor='transparent'; x.style.color=''; x.style.background='';
  });
  var gc = document.getElementById('chip-global');
  if(gc) gc.classList.add('active');

  /* Render */
  w22_update();
};

/* Inicializar KPI heroes al cargar — CR visible, RND oculto */
(function(){
  var cr_kpi  = document.getElementById('w22-kpis-cr');
  var rnd_kpi = document.getElementById('w22-kpis-rnd');
  if(cr_kpi)  cr_kpi.style.display  = 'block';
  if(rnd_kpi) rnd_kpi.style.display = 'none';
  /* Severity inicial: CR visible */
  var sev_cr  = document.getElementById('w22-sev-cr');
  var sev_rnd = document.getElementById('w22-sev-rnd');
  if(sev_cr)  sev_cr.style.display  = '';
  if(sev_rnd) sev_rnd.style.display = 'none';
})();

/* Patch w22_iTab — solo clases, sin inline styles que pisan !important */
var _origITab = w22_iTab;
w22_iTab = function(el) {
  var row = el.parentElement;
  row.querySelectorAll('label').forEach(function(t){
    t.classList.remove('tab-label-active');
    t.removeAttribute('style');
  });
  el.classList.add('tab-label-active');
};


/* Disparar render inicial */
w22_update();
/* Reemplazar w22_setView completamente — usar !important vía style */
w22_setView = function(v) {
  W.view = v;
  var ph = document.getElementById('w22-ph');
  var pd = document.getElementById('w22-pd');
  var vh = document.getElementById('vch-h');
  var vd = document.getElementById('vch-d');
  /* Usar !important override directo */
  if(ph) ph.setAttribute('style', (v==='hotel' ? 'display:block!important;' : 'display:none!important;') + 'border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);');
  if(pd) pd.setAttribute('style', (v==='dim'   ? 'display:block!important;' : 'display:none!important;') + 'border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);');
  if(vh){ vh.classList.toggle('on', v==='hotel'); vh.style.background=v==='hotel'?'var(--paper)':''; vh.style.color=v==='hotel'?'var(--ink)':'var(--ink-muted)'; }
  if(vd){ vh.classList.toggle('on', v==='dim');   vd.style.background=v==='dim'  ?'var(--paper)':''; vd.style.color=v==='dim'  ?'var(--ink)':'var(--ink-muted)'; }
};
/* Parchear onmousemove de todos los canvas para usar W22_CANVAS_CFG dinámicamente */
/* Interceptar tooltip — guardar último canvas hoveado y forzar valor correcto */
var _lastHoveredCid = null;
document.addEventListener('mousemove', function(e) {
  var el = e.target;
  if (el && el.tagName === 'CANVAS' && el.id) {
    _lastHoveredCid = el.id;
  }
}, true);

/* Hookear textContent del tooltip */
function _hookTooltip() {
  var tip = (typeof w22_getTooltip === 'function') ? w22_getTooltip() : null;
  if (!tip || tip._hooked) return;
  tip._hooked = true;
  /* Guardar referencia al setter original */
  var nativeDesc = Object.getOwnPropertyDescriptor(Node.prototype, 'textContent');
  Object.defineProperty(tip, 'textContent', {
    get: function() { return nativeDesc.get.call(this); },
    set: function(v) {
      var cid = _lastHoveredCid;
      if (cid && typeof W22_CANVAS_CFG !== 'undefined' && W22_CANVAS_CFG[cid]) {
        /* Parsear "W21: 93.15%" para obtener el índice de la semana */
        var m = String(v).match(/^(W\d+):/);
        if (m) {
          var semIdx = parseInt(m[1].substring(1), 10) - 17;
          var cfg = W22_CANVAS_CFG[cid];
          if (semIdx >= 0 && semIdx < cfg.vals.length) {
            var val = cfg.vals[semIdx];
            var fmtVal = cfg.metric === 'ipm'
              ? ('$' + Math.round(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','))
              : val.toFixed(2) + '%';
            v = m[1] + ': ' + fmtVal;
          }
        }
      }
      nativeDesc.set.call(this, v);
    },
    configurable: true
  });
}
[100, 300, 600, 1200].forEach(function(t) { setTimeout(_hookTooltip, t); });
window.addEventListener('load', function() { setTimeout(_hookTooltip, 100); });

var _patchedCanvases = {};
function _patchCanvasTooltips() {
  var canvasIds = ['hcr-global-ef','hcr-global-cv','hrnd-global-nd','hrnd-global-ipm',
                   'hcr-panel-ef','hrnd-panel-nd','hcr-dim-ef','hrnd-dim-nd'];
  canvasIds.forEach(function(cid) {
    if (_patchedCanvases[cid]) return;
    var el = document.getElementById(cid);
    if (!el) return;
    _patchedCanvases[cid] = true;
    /* addEventListener('mousemove', ..., true) en CAPTURE phase + stopImmediatePropagation
       para ganar a CUALQUIER otro listener registrado en el canvas */
    el.addEventListener('mousemove', function(e) {
      var cfg = W22_CANVAS_CFG[cid];
      if (!cfg || !cfg.vals) return;
      var rect = el.getBoundingClientRect();
      if (!rect || rect.width === 0) return;
      var mx = e.clientX - rect.left;
      var tip = (typeof w22_getTooltip === 'function') ? w22_getTooltip() : null;
      if (!tip) return;
      var vals = cfg.vals;
      var w = rect.width;
      var best = -1, bestDx = 9999;
      vals.forEach(function(v, i) {
        var px = (i / (vals.length - 1)) * w;
        var dx = Math.abs(px - mx);
        if (dx < bestDx) { bestDx = dx; best = i; }
      });
      if (best < 0 || bestDx > 40) { tip.style.display = 'none'; return; }
      var sems = cfg.semanas || ['W17','W18','W19','W20','W21'];
      var val = vals[best];
      var fmtVal = cfg.metric === 'ipm'
        ? ('$' + Math.round(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','))
        : val.toFixed(2) + '%';
      tip.textContent = (sems[best] || ('W' + (17 + best))) + ': ' + fmtVal;
      tip.style.display = 'block';
      tip.style.left = (e.clientX + 10) + 'px';
      tip.style.top = (e.clientY - 28) + 'px';
      /* PARAR otros listeners en el mismo elemento */
      e.stopImmediatePropagation();
    }, true);  /* CAPTURE phase - corre PRIMERO */
    el.addEventListener('mouseleave', function() {
      var tip = (typeof w22_getTooltip === 'function') ? w22_getTooltip() : null;
      if (tip) tip.style.display = 'none';
    }, true);
  });
}
[300, 600, 1200, 2000, 3000].forEach(function(t) { setTimeout(_patchCanvasTooltips, t); });
window.addEventListener('load', function() { setTimeout(_patchCanvasTooltips, 500); });

/* Forzar vista hotel en múltiples momentos */
w22_setView('hotel');
[100, 300, 600, 1000, 2000].forEach(function(t){ setTimeout(function(){ w22_setView(W.view||'hotel'); }, t); });
window.addEventListener('load', function(){
  w22_setView(W.view||'hotel');
  /* Redibujar canvas del panel con ancho real una vez visible */
  setTimeout(function(){ var col=cv().col; w22_redrawCanvas(col); }, 500);
});

/* ── Event delegation para histórico del panel ─────────────────────────── */
document.addEventListener('click', function(e) {
  var tr = e.target.closest('tr[data-hist-label]');
  if (!tr) return;
  var tbody = tr.closest('tbody');
  if (!tbody || (tbody.id !== 'w22-th' && tbody.id !== 'w22-td')) return;

  var label  = tr.getAttribute('data-hist-label') || '';
  var w21str = tr.getAttribute('data-hist-w21') || '—';
  var accent = cv ? cv().col : '#5C469C';

  /* Highlight */
  tbody.querySelectorAll('tr').forEach(function(r){ r.style.background = ''; });
  tr.style.background = 'var(--accent-soft)';

  /* Canvas activo */
  var isHotel = tbody.id === 'w22-th';
  var isCR    = W && W.mode === 'cr';
  var canvasId = isHotel
    ? (isCR ? 'hcr-panel-ef'  : 'hrnd-panel-nd')
    : (isCR ? 'hcr-dim-ef'    : 'hrnd-dim-nd');

  var histObj = isCR ? HIST_CR : HIST_RND;
  var cfg = histObj[canvasId]; if (!cfg) return;

  /* Parsear valor W21 */
  function parseVal(s) {
    if (!s || s === '—') return null;
    return parseFloat(s.replace(/[^\d,.]/g,'').replace(',','.')) || null;
  }
  var v21 = parseVal(w21str); if (v21 === null) return;
  var newVals = cfg.vals.slice(0,-1).concat([v21]);

  /* Actualizar label */
  var labelEl = document.getElementById('hist-' + canvasId + '-label');
  if (labelEl) labelEl.textContent = label;

  /* Redibujar canvas */
  var el = document.getElementById(canvasId);
  if (!el || !el.getContext) return;
  var rgb = RGB[accent] || '92,70,156';
  el.width = el.offsetWidth || 400; el.height = 76;
  var ctx = el.getContext('2d');
  var vals = newVals; var hh = el.height - 10;
  var mn = Math.min.apply(null,vals), mx = Math.max.apply(null,vals), dR = mx-mn+0.0001;
  var pts = vals.map(function(v,i){ return {x:(i/(vals.length-1))*el.width, y:el.height-((v-mn)/dR*hh+5)}; });
  var tY  = el.height - ((cfg.target-mn)/dR*hh+5);
  ctx.clearRect(0,0,el.width,el.height);
  ctx.strokeStyle='rgba(0,0,0,0.15)'; ctx.lineWidth=1; ctx.setLineDash([3,2]);
  ctx.beginPath(); ctx.moveTo(0,tY); ctx.lineTo(el.width,tY); ctx.stroke(); ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(pts[0].x,el.height); ctx.lineTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y);
  ctx.lineTo(pts[pts.length-1].x,el.height); ctx.closePath();
  ctx.fillStyle='rgba('+rgb+',0.12)'; ctx.fill();
  ctx.strokeStyle=accent; ctx.lineWidth=2; ctx.lineCap='round'; ctx.lineJoin='round';
  ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.stroke();
  for(var i=0;i<pts.length;i++){
    var last=i===pts.length-1;
    ctx.fillStyle=last?accent:'rgba('+rgb+',0.5)'; ctx.globalAlpha=last?1:0.5;
    ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3:2,0,2*Math.PI); ctx.fill(); ctx.globalAlpha=1;
  }
});

/* ── Event delegation para historico del panel ── */
document.addEventListener('click', function(e) {
  var tr = e.target.closest ? e.target.closest('tr[data-hist-label]') : null;
  if (!tr) return;
  var tbody = tr.closest('tbody');
  if (!tbody || (tbody.id !== 'w22-th' && tbody.id !== 'w22-td')) return;

  var label  = tr.getAttribute('data-hist-label') || '';
  var w21str = tr.getAttribute('data-hist-w21') || '—';
  var accent = (typeof cv === 'function') ? cv().col : '#5C469C';

  /* Highlight */
  tbody.querySelectorAll('tr').forEach(function(r){ r.style.background = ''; });
  tr.style.background = 'var(--accent-soft)';

  /* Canvas activo segun modo y vista */
  var isHotel = tbody.id === 'w22-th';
  var isCR    = W && W.mode === 'cr';
  var canvasId = isHotel
    ? (isCR ? 'hcr-panel-ef' : 'hrnd-panel-nd')
    : (isCR ? 'hcr-dim-ef'   : 'hrnd-dim-nd');

  var histObj = isCR ? HIST_CR : HIST_RND;
  var cfg = histObj ? histObj[canvasId] : null; if (!cfg) return;

  /* Parsear W21 */
  var v21 = parseFloat(w21str.replace(/[^0-9,.]/g,'').replace(',','.')); 
  if (isNaN(v21)) return;
  var newVals = cfg.vals.slice(0,-1).concat([v21]);

  /* Label del canvas */
  var labelEl = document.getElementById('hist-' + canvasId + '-label');
  if (labelEl) labelEl.textContent = label;

  /* Redibujar */
  var el = document.getElementById(canvasId);
  if (!el || !el.getContext) return;
  var rgb = (typeof RGB !== 'undefined' && RGB[accent]) ? RGB[accent] : '92,70,156';
  el.width = el.offsetWidth || 400; el.height = 76;
  var ctx = el.getContext('2d');
  var hh = el.height - 10;
  var mn = Math.min.apply(null,newVals), mx = Math.max.apply(null,newVals), dR = mx-mn+0.0001;
  var pts = newVals.map(function(v,i){ return {x:(i/(newVals.length-1))*el.width, y:el.height-((v-mn)/dR*hh+5)}; });
  var tY  = el.height - ((cfg.target-mn)/dR*hh+5);
  ctx.clearRect(0,0,el.width,el.height);
  ctx.strokeStyle='rgba(0,0,0,0.15)'; ctx.lineWidth=1; ctx.setLineDash([3,2]);
  ctx.beginPath(); ctx.moveTo(0,tY); ctx.lineTo(el.width,tY); ctx.stroke(); ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(pts[0].x,el.height); ctx.lineTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y);
  ctx.lineTo(pts[pts.length-1].x,el.height); ctx.closePath();
  ctx.fillStyle='rgba('+rgb+',0.12)'; ctx.fill();
  ctx.strokeStyle=accent; ctx.lineWidth=2; ctx.lineCap='round'; ctx.lineJoin='round';
  ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.stroke();
  for(var i=0;i<pts.length;i++){
    var last=i===pts.length-1;
    ctx.fillStyle=last?accent:'rgba('+rgb+',0.5)'; ctx.globalAlpha=last?1:0.5;
    ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3:2,0,2*Math.PI); ctx.fill(); ctx.globalAlpha=1;
  }
});

/* ── KPI-card tabs (W21+) ──────────────────────────────────────────────── */
(function(){
  var PREFIXES = ['tab-ef','tab-cv','tab-nd','tab-rpm'];
  var _inited = new WeakSet();  /* evitar doble init por card */

  function showTab(card, prefix, key){
    card.querySelectorAll('.tab-panels .tab-panel').forEach(function(p){ p.style.display='none'; });
    var panel = card.querySelector('.tab-panels .tab-panel[data-tab="'+key+'"]');
    if(panel) panel.style.display = 'block';
    card.querySelectorAll('.tabs-row label').forEach(function(l){ l.classList.remove('tab-label-active'); });
    var lbl = card.querySelector('.tabs-row label[for="'+prefix+'-'+key+'"]');
    if(lbl) lbl.classList.add('tab-label-active');
  }

  function initCard(card){
    if(_inited.has(card)) return;  /* ya inicializada */
    var prefix = null;
    for(var i=0;i<PREFIXES.length;i++){
      if(card.querySelector('input[id^="'+PREFIXES[i]+'"]')){ prefix=PREFIXES[i]; break; }
    }
    if(!prefix) return;
    _inited.add(card);

    /* Estado inicial */
    var checked = card.querySelector('input[id^="'+prefix+'"]:checked');
    if(checked) showTab(card, prefix, checked.id.replace(prefix+'-',''));

    /* Un solo listener por label */
    card.querySelectorAll('.tabs-row label').forEach(function(lbl){
      lbl.addEventListener('click', function(){
        var f = lbl.getAttribute('for');
        if(!f || !f.startsWith(prefix)) return;
        setTimeout(function(){
          var inp = document.getElementById(f);
          if(inp && inp.checked) showTab(card, prefix, f.replace(prefix+'-',''));
        }, 20);
      });
    });
  }

  function initAll(){
    document.querySelectorAll('.kpi-card').forEach(initCard);
  }

  /* Correr una vez con delay suficiente para que w22_update ya haya pintado */
  setTimeout(initAll, 300);
  window.addEventListener('load', initAll);
})();

/* ── Event delegation para historico del panel ── */
document.addEventListener('click', function(e) {
  var tr = e.target.closest ? e.target.closest('tr[data-hist-label]') : null;
  if (!tr) return;
  var tbody = tr.closest('tbody');
  if (!tbody || (tbody.id !== 'w22-th' && tbody.id !== 'w22-td')) return;

  var label  = tr.getAttribute('data-hist-label') || '';
  var w21str = tr.getAttribute('data-hist-w21') || '—';
  var accent = (typeof cv === 'function') ? cv().col : '#5C469C';

  /* Highlight */
  tbody.querySelectorAll('tr').forEach(function(r){ r.style.background = ''; });
  tr.style.background = 'var(--accent-soft)';

  /* Canvas activo segun modo y vista */
  var isHotel = tbody.id === 'w22-th';
  var isCR    = W && W.mode === 'cr';
  var canvasId = isHotel
    ? (isCR ? 'hcr-panel-ef' : 'hrnd-panel-nd')
    : (isCR ? 'hcr-dim-ef'   : 'hrnd-dim-nd');

  var histObj = isCR ? HIST_CR : HIST_RND;
  var cfg = histObj ? histObj[canvasId] : null; if (!cfg) return;

  /* Parsear W21 */
  var v21 = parseFloat(w21str.replace(/[^0-9,.]/g,'').replace(',','.'));
  if (isNaN(v21)) return;
  var newVals = cfg.vals.slice(0,-1).concat([v21]);

  /* Label del canvas */
  var labelEl = document.getElementById('hist-' + canvasId + '-label');
  if (labelEl) labelEl.textContent = label;

  /* Redibujar */
  var el = document.getElementById(canvasId);
  if (!el || !el.getContext) return;
  var rgb = (typeof RGB !== 'undefined' && RGB[accent]) ? RGB[accent] : '92,70,156';
  el.width = el.offsetWidth || 400; el.height = 76;
  var ctx = el.getContext('2d');
  var hh = el.height - 10;
  var mn = Math.min.apply(null,newVals), mx = Math.max.apply(null,newVals), dR = mx-mn+0.0001;
  var pts = newVals.map(function(v,i){ return {x:(i/(newVals.length-1))*el.width, y:el.height-((v-mn)/dR*hh+5)}; });
  var tY  = el.height - ((cfg.target-mn)/dR*hh+5);
  ctx.clearRect(0,0,el.width,el.height);
  ctx.strokeStyle='rgba(0,0,0,0.15)'; ctx.lineWidth=1; ctx.setLineDash([3,2]);
  ctx.beginPath(); ctx.moveTo(0,tY); ctx.lineTo(el.width,tY); ctx.stroke(); ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(pts[0].x,el.height); ctx.lineTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y);
  ctx.lineTo(pts[pts.length-1].x,el.height); ctx.closePath();
  ctx.fillStyle='rgba('+rgb+',0.12)'; ctx.fill();
  ctx.strokeStyle=accent; ctx.lineWidth=2; ctx.lineCap='round'; ctx.lineJoin='round';
  ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.stroke();
  for(var i=0;i<pts.length;i++){
    var last=i===pts.length-1;
    ctx.fillStyle=last?accent:'rgba('+rgb+',0.5)'; ctx.globalAlpha=last?1:0.5;
    ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3:2,0,2*Math.PI); ctx.fill(); ctx.globalAlpha=1;
  }
});
/* ── w22_renderCardTabs — re-renderiza los tabs de las cards KPI CR por canasta ── */
function _fmtInt(n){ if(n==null) return '—'; return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.'); }
function _fmtPct(n){ if(n==null) return '—'; return n.toFixed(2).replace('.',',')+'%'; }
function _pill(v, bg, fg){ return v==null?'<span style="color:var(--ink-muted);font-size:10px;">—</span>':'<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+bg+';color:'+fg+';white-space:nowrap;">'+v+'</em>'; }
function _wowInt(delta){ if(delta==null) return null; var abs=Math.round(Math.abs(delta)); return (delta>0?'▲':'▼')+_fmtInt(abs); }
function _wowPct(pp){ if(pp==null) return null; var abs=Math.abs(pp); return (pp>0?'▲':'▼')+abs.toFixed(2).replace('.',','); }

function _cardRow(r, idx, isEf){
  /* r: [lab,sub,bbg,bfg,banda, cr_u,cr_wow_delta, val_pct, wow_pp, hist_w21, hist_w20] */
  var lab=r[0], sub=r[1], bbg=r[2], bfg=r[3], banda=r[4];
  var cr_u=r[5], cr_wow_delta=r[6], val_pct=r[7], wow_pp=r[8];
  var hist_w21=r[9]||0, hist_w20=r[10]||hist_w21;
  var badge='<span class="sev-badge" style="background:'+bbg+';color:'+bfg+';font-size:7px;font-weight:700;padding:2px 5px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);white-space:nowrap;">'+banda+'</span>';
  var cr_str = _fmtInt(cr_u);
  /* WoW tráfico */
  var tw = _wowInt(cr_wow_delta);
  var tw_bg = cr_wow_delta!=null&&cr_wow_delta>0?'#EAF3DE':'#FCE8E6';
  var tw_fg = cr_wow_delta!=null&&cr_wow_delta>0?'#2F6C34':'#C0392B';
  var tw_pill = _pill(tw, tw_bg, tw_fg);
  /* WoW métrica */
  var mw = _wowPct(wow_pp);
  var mw_up = wow_pp!=null && (isEf ? wow_pp>0 : wow_pp>0);
  var mw_bg = wow_pp!=null&&mw_up?'#EAF3DE':'#FCE8E6';
  var mw_fg = wow_pp!=null&&mw_up?'#2F6C34':'#C0392B';
  var mw_pill = _pill(mw, mw_bg, mw_fg);
  var nameSpan='<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">'+(idx+1)+'. '+lab+'</span>'
    +(sub?'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">'+sub+'</span>':'');
  return '<div data-row-idx="'+idx+'" data-hist-w21="'+hist_w21+'" data-hist-w20="'+hist_w20+'" data-hist-label="'+lab+'"'
    +' style="display:grid;grid-template-columns:minmax(0,1fr) 80px 56px 52px 54px 48px;align-items:center;gap:6px;'
    +'padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
    +'<div style="min-width:0;overflow:hidden;">'+nameSpan+'</div>'
    +'<div style="display:flex;align-items:center;justify-content:flex-start;">'+badge+'</div>'
    +'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;white-space:nowrap;">'+cr_str+'</span>'
    +'<div style="text-align:right;white-space:nowrap;">'+tw_pill+'</div>'
    +'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;white-space:nowrap;">'+_fmtPct(val_pct)+'</span>'
    +'<div style="text-align:right;white-space:nowrap;">'+mw_pill+'</div>'
    +'</div>';
}

function w22_renderCardTabs(canasta){
  if(typeof CR_CARD_TABS === 'undefined') return;
  var tabs = CR_CARD_TABS[canasta] || CR_CARD_TABS['global'];
  if(!tabs) return;
  
  /* destino / corp / hotel */
  ['ef','cv'].forEach(function(metric){
    var isEf = metric==='ef';
    var suffix = isEf ? '-ef-' : '-cv-';
    ['destino','corp','hotel'].forEach(function(tkey){
      var rows = (tabs[metric]||{})[tkey]||[];
      var radioEl = document.getElementById('tab'+suffix+tkey);
      if(!radioEl) return;
      var card = radioEl.closest('.kpi-card');
      if(!card) return;
      var panel = card.querySelector('[data-tab="'+tkey+'"]');
      if(!panel) return;
      var rowsHtml = rows.slice(0,10).map(function(r,i){ return _cardRow(r,i,isEf); }).join('');
      var kpiRows = panel.querySelector('.kpi-tab-rows');
      if(kpiRows){
        var header = kpiRows.querySelector('div:first-child');
        kpiRows.innerHTML = (header?header.outerHTML:'') + rowsHtml;
      } else {
        panel.innerHTML = rowsHtml;
      }
      if(typeof window._injectHistAttrs === 'function') window._injectHistAttrs(card);
    });
  });
  
  /* channel — layout especial: PP / TP en dos columnas */
  ['ef','cv'].forEach(function(metric){
    var isEf = metric==='ef';
    var suffix = isEf ? '-ef-' : '-cv-';
    var chanKey = metric+'_chan';
    var chanData = tabs[chanKey] || {};
    var pp = chanData.pp || [], tp = chanData.tp || [];
    var radioEl = document.getElementById('tab'+suffix+'channel');
    if(!radioEl) return;
    var card = radioEl.closest('.kpi-card');
    if(!card) return;
    var panel = card.querySelector('[data-tab="channel"]');
    if(!panel) return;
    
    /* [nombre, bbg, bfg, banda, cr_u, val_pct, wow_pp] */
    function _chanRow(r, i){
      var nombre=r[0], bbg=r[1], bfg=r[2], banda=r[3], cr_u=r[4], val_pct=r[5], wow_pp=r[6];
      var badge='<span class="sev-badge" style="background:'+bbg+';color:'+bfg+';font-size:7px;font-weight:700;padding:2px 5px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);white-space:nowrap;">'+banda+'</span>';
      var mw_up = wow_pp!=null&&wow_pp>0;
      var mw_bg = mw_up?'#EAF3DE':'#FCE8E6';
      var mw_fg = mw_up?'#2F6C34':'#C0392B';
      var mw = wow_pp!=null?_pill((wow_pp>0?'▲':'▼')+Math.abs(wow_pp).toFixed(2).replace('.',','), mw_bg, mw_fg):'<span style="color:var(--ink-muted)">—</span>';
      return '<div style="display:grid;grid-template-columns:minmax(0,1fr) 90px 60px 44px;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);">'
        +'<span style="font-size:11px;font-weight:600;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+nombre+'</span>'
        +'<div style="display:flex;align-items:center;justify-content:flex-start;">'+badge+'</div>'
        +'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);white-space:nowrap;font-variant-numeric:tabular-nums;">'+_fmtPct(val_pct)+'</span>'
        +'<div style="text-align:right;">'+mw+'</div>'
        +'</div>';
    }
    var pp_html = pp.map(_chanRow).join('');
    var tp_html = tp.map(_chanRow).join('');
    panel.innerHTML = '<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
      +'<div><div style="font-size:9px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>'+pp_html+'</div>'
      +'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>'+tp_html+'</div>'
      +'</div>';
  });
}

/* ═══ Funciones de las dos cards de Análisis de Rendimiento ═══ */

/* Estado por card */
var _arView  = {1:'hotel', 2:'hotel'};
var _arHTab  = {1:'crit',  2:'crit'};
var _arDim   = {1:'corp',  2:'corp'};

/* Obtener filas para card n según modo, canasta y tab */
function _arRows(n, tab) {
  var dd = data();
  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
  if (n === 1) {
    /* Card 1: Eficacia (CR) / NoDispo (RND) — usa hotels_crit/br/sc/cv */
    var rows = tab === 'br' ? (dd.hotels_br || dd.hotels) :
               tab === 'sc' ? (dd.hotels_sc || dd.hotels) :
               tab === 'cv' ? (dd.hotels_cv || dd.hotels) :
               (dd.hotels_crit || dd.hotels);
    return rows || [];
  } else {
    /* Card 2: Conv Rate (CR) / IPM (RND) — mismos tabs pero ordenados por cv/ipm */
    var rows2 = tab === 'br' ? (dd.hotels_br || dd.hotels) :
                tab === 'sc' ? (dd.hotels_sc || dd.hotels) :
                tab === 'cv' ? (dd.hotels_cv || dd.hotels) :
                (dd.hotels_crit || dd.hotels);
    return rows2 || [];
  }
}

/* Render canal con split PP/TP en 2 columnas para las cards AR */
function _arRenderChan(n) {
  var dd = data();
  var pp = dd.chans_pp || [];
  var tp = dd.chans_tp || [];
  var acc = (typeof cv === 'function') ? cv().col : '#5C469C';
  var cyan = '#4FC3F4';
  var isCR = W.mode === 'cr';

  /* Cada fila: div clickeable con data-hist para el histórico */
  function chanRowAR(r, origIdx) {
    var nombre=r[0], bbg=r[1], bfg=r[2], banda=r[3], cr_u=r[4], val_pct=r[5], wow_pp_raw=r[6];
    /* wow_pp puede ser string '1,31%' o número — normalizar */
    var wow_pp = (wow_pp_raw != null && wow_pp_raw !== '—' && wow_pp_raw !== '')
      ? parseFloat(String(wow_pp_raw).replace(/[^0-9,.\-]/g,'').replace(',','.'))
      : null;
    var badge = '<span class="sev-badge" style="background:'+bbg+';color:'+bfg+';font-size:7px;font-weight:700;padding:2px 5px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);white-space:nowrap;">'+banda+'</span>';
    var mw_up = wow_pp!=null && !isNaN(wow_pp) && wow_pp>0;
    var mw = (wow_pp!=null && !isNaN(wow_pp))
      ? '<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+(mw_up?'#EAF3DE':'#FCE8E6')+';color:'+(mw_up?'#2F6C34':'#C0392B')+';white-space:nowrap;">'+(wow_pp>0?'▲':'▼')+Math.abs(wow_pp).toFixed(2).replace('.',',')+'</em>'
      : '<span style="color:var(--ink-muted)">—</span>';
    var displayVal = val_pct || '—';
    var metNum = parseFloat(String(val_pct).replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
    var wowNum = (wow_pp!=null && !isNaN(wow_pp)) ? Math.abs(wow_pp) : 0;
    var w20num = (wow_pp!=null && !isNaN(wow_pp)) ? (mw_up ? metNum-wowNum : metNum+wowNum) : metNum;
    var histAttrs = 'data-hist-w21="'+metNum+'" data-hist-w20="'+w20num+'" data-hist-label="'+nombre+'" data-hist-card="'+n+'"';
    var isInactive = banda === 'Sin Actividad';
    var rowStyle = isInactive
      ? 'display:grid;grid-template-columns:minmax(0,1fr) 90px 60px 44px;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);width:100%;opacity:0.45;'
      : 'display:grid;grid-template-columns:minmax(0,1fr) 90px 60px 44px;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;width:100%;';
    return '<div '+histAttrs+' style="'+rowStyle+'">'
      +'<span style="font-size:11px;font-weight:600;color:'+(isInactive?'var(--ink-muted)':'var(--ink)')+';overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;min-width:0;">'+(origIdx<10?'0'+origIdx:origIdx)+'. '+nombre+'</span>'
      +'<div style="display:flex;align-items:center;justify-content:flex-start;">'+(isInactive?'<span style="font-size:9px;color:var(--ink-muted);font-style:italic;">sin actividad</span>':badge)+'</div>'
      +'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink-muted);white-space:nowrap;font-variant-numeric:tabular-nums;">'+displayVal+'</span>'
      +'<div style="text-align:right;">'+mw+'</div>'
      +'</div>';
  }

  var pp_html = pp.map(function(r,i){ return chanRowAR(r,i+1); }).join('');
  var tp_html = tp.map(function(r,i){ return chanRowAR(r,i+1); }).join('');
  var html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:8px 0;">'
    +'<div><div style="font-size:9px;font-weight:700;color:'+acc+';letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">\uD83C\uDFE0 Producto Propio</div>'+pp_html+'</div>'
    +'<div><div style="font-size:9px;font-weight:700;color:'+cyan+';letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">\uD83D\uDD0C Third Party</div>'+tp_html+'</div>'
    +'</div>';

  /* Ocultar la tabla y mostrar el div de canal */
  var pd = document.getElementById('ar'+n+'-pd');
  if (!pd) return;
  var table = pd.querySelector('table');
  var btn   = document.getElementById('ar'+n+'-td-more');
  if (table) table.style.display = 'none';
  if (btn)   btn.style.display   = 'none';

  /* Usar o crear el div canal */
  var chanDiv = document.getElementById('ar'+n+'-chan-div');
  if (!chanDiv) {
    chanDiv = document.createElement('div');
    chanDiv.id = 'ar'+n+'-chan-div';
    pd.appendChild(chanDiv);
  }
  chanDiv.innerHTML = html;
  chanDiv.style.display = '';
  /* Enganchar clicks en las filas del channel */
  if (typeof window._injectHistAttrs === 'function') {
    window._injectHistAttrs(chanDiv.closest('.ar-card') || chanDiv.parentElement);
  }
}

function _arDimRows(n, dim) {
  var dd = data();
  if (dim === 'chan') return dd.chans || dd.dims || [];
  if (dim === 'dest') return dd.dests || dd.dims || [];
  return dd.corps || dd.dims || [];
}

/* Render tabla de una card */
function _arRenderTable(n, view) {
  var v = view || _arView[n];
  if (v === 'hotel') {
    /* Asegurar tabla visible, chanDiv oculto */
    var pd = document.getElementById('ar'+n+'-pd');
    if (pd) { var cd = document.getElementById('ar'+n+'-chan-div'); if(cd) cd.style.display='none'; }
    /* Asegurar que la tabla hotel es visible */
    var ph = document.getElementById('ar'+n+'-ph');
    if (ph) {
      var tbl = ph.querySelector('table'); if(tbl) tbl.style.display='';
    }
    var rows = _arRows(n, _arHTab[n]);
    ar_renderTable(n, 'ar'+n+'-th', 'ar'+n+'-th-more', rows);
  } else {
    if (_arDim[n] === 'chan') {
      _arRenderChan(n);
    } else {
      /* Restaurar tabla, ocultar chanDiv */
      var pd2 = document.getElementById('ar'+n+'-pd');
      if (pd2) {
        var tbl = pd2.querySelector('table'); if(tbl) tbl.style.display='';
        var cd2 = document.getElementById('ar'+n+'-chan-div'); if(cd2) cd2.style.display='none';
      }
      var drows = _arDimRows(n, _arDim[n]);
      ar_renderTable(n, 'ar'+n+'-td', 'ar'+n+'-td-more', drows);
    }
  }
}

/* Cambiar vista hotel/dim de una card */
function ar_setView(n, v) {
  _arView[n] = v;
  var ph  = document.getElementById('ar'+n+'-ph');
  var pd  = document.getElementById('ar'+n+'-pd');
  var vch = document.getElementById('ar'+n+'-vch-h');
  var vcd = document.getElementById('ar'+n+'-vch-d');
  if (ph) ph.style.display = v === 'hotel' ? '' : 'none';
  if (pd) pd.style.display = v === 'dim'   ? '' : 'none';
  if (vch) { vch.classList.toggle('tab-label-active', v==='hotel'); }
  if (vcd) { vcd.classList.toggle('tab-label-active', v==='dim');   }
  _arRenderTable(n, v);
}

/* Cambiar sub-pestaña hotel de una card */
function ar_setHotelTab(n, tab, el) {
  _arHTab[n] = tab;
  var ph = document.getElementById('ar'+n+'-ph');
  if (ph) ph.querySelectorAll('.tab-label').forEach(function(l){ l.classList.remove('tab-label-active'); });
  if (el) { el.classList.add('tab-label-active'); }
  var rows = _arRows(n, tab);
  ar_renderTable(n, 'ar'+n+'-th', 'ar'+n+'-th-more', rows);
}

/* Cambiar dimensión de una card */
function ar_setDim(n, dim) {
  _arDim[n] = dim;
  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
  var dimLabelMap = {corp:'Corporativo', dest:'Destino', chan: isCR ? 'Channel' : 'País'};
  var lbl = document.getElementById('ar'+n+'-td-lbl');
  if (lbl) lbl.textContent = dimLabelMap[dim] || 'Corporativo';

  /* Mostrar/ocultar tabla vs div canal */
  var pd = document.getElementById('ar'+n+'-pd');
  if (pd) {
    var table   = pd.querySelector('table');
    var btn     = document.getElementById('ar'+n+'-td-more');
    var chanDiv = document.getElementById('ar'+n+'-chan-div');
    if (dim === 'chan') {
      if (table) table.style.display = 'none';
      _arRenderChan(n);
    } else {
      if (table)   table.style.display   = '';
      if (chanDiv) chanDiv.style.display  = 'none';
      var drows = _arDimRows(n, dim);
      ar_renderTable(n, 'ar'+n+'-td', 'ar'+n+'-td-more', drows);
    }
  }
}

/* Actualizar etiquetas de las cards según modo CR/RND */
function ar_updateLabels() {
  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
  var lbl1 = document.getElementById('ar-card1-lbl');
  var lbl2 = document.getElementById('ar-card2-lbl');
  var col1 = document.getElementById('ar1-col-m');
  var col2 = document.getElementById('ar2-col-m');
  var tdc1 = document.getElementById('ar1-td-col-m');
  var tdc2 = document.getElementById('ar2-td-col-m');
  if (lbl1) lbl1.textContent = isCR ? 'Eficacia' : '%NoDispo';
  if (lbl2) lbl2.textContent = isCR ? 'Conv Rate' : 'IPM';
  if (col1) col1.textContent = isCR ? 'Eficacia' : '%NoDispo';
  if (col2) col2.textContent = isCR ? 'Conv Rate' : 'IPM';
  if (tdc1) tdc1.textContent = isCR ? 'Eficacia' : '%NoDispo';
  if (tdc2) tdc2.textContent = isCR ? 'Conv Rate' : 'IPM';
  /* Pestaña Canal → Channel (CR) o País (RND) */
  var chanLabel = isCR ? 'Channel' : 'País';
  [1,2].forEach(function(n){
    var el = document.getElementById('ar'+n+'-dim-chan');
    if (el) el.textContent = chanLabel;
  });
  /* Canvas hist: mostrar CR o RND según modo */
  ['ar1-hist-cr','ar2-hist-cr'].forEach(function(id){
    var el = document.getElementById(id); if(el) el.style.display = isCR ? 'block' : 'none';
  });
  ['ar1-hist-rnd','ar2-hist-rnd'].forEach(function(id){
    var el = document.getElementById(id); if(el) el.style.display = isCR ? 'none' : 'block';
  });
}

/* Inicializar y re-renderizar las dos cards */
function ar_update() {
  ar_updateLabels();
  ar_updateKPIs();
  /* Guardar labels seleccionados antes de re-renderizar */
  var sel = {};
  [1,2].forEach(function(n){
    ['th','td'].forEach(function(t){
      var tbody = document.getElementById('ar'+n+'-'+t);
      if (!tbody) return;
      var selRow = tbody.querySelector('[data-selected="1"]');
      if (selRow) sel['ar'+n+'-'+t] = selRow.getAttribute('data-hist-label');
    });
  });
  _arRenderTable(1);
  _arRenderTable(2);
  /* Restaurar estilos de vista activa */
  [1,2].forEach(function(n){ ar_setView(n, _arView[n]); });
  /* Re-seleccionar elementos que estaban seleccionados */
  setTimeout(function(){
    Object.keys(sel).forEach(function(tbodyId){
      var label = sel[tbodyId];
      var tbody = document.getElementById(tbodyId);
      if (!tbody || !label) return;
      var rows = tbody.querySelectorAll('[data-hist-label]');
      var acc = (typeof cv === 'function') ? cv().col : '#5C469C';
      var accentAlpha = acc === '#333132' ? 'rgba(51,49,50,0.07)' :
                        acc === '#EA0074' ? 'rgba(234,0,116,0.07)' :
                        acc === '#FCB000' ? 'rgba(252,176,0,0.10)' :
                        acc === '#4FC3F4' ? 'rgba(79,195,244,0.10)' :
                        'rgba(92,70,156,0.07)';
      rows.forEach(function(r){
        if (r.getAttribute('data-hist-label') === label) {
          r.setAttribute('data-selected','1');
          r.style.background = accentAlpha;
        }
      });
    });
  }, 30);
}

/* Hook en w22_update para re-renderizar AR */
var _origW22Update = w22_update;
w22_update = function() {
  _origW22Update.apply(this, arguments);
  setTimeout(ar_update, 10);
};

/* Inicializar al cargar */
setTimeout(ar_update, 100);

/* ── trow para cards AR: 6 cols, solo la métrica de la card ── */
function trow_ar(r, card, idx) {
 /* data-hist para canvas histórico */
 var isCR = W.mode === 'cr';
 var metVal = card === 1 ? r[5] : r[6];
 var metNum = parseFloat(String(metVal).replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
 var wowStr = card === 1 ? (r[8]||'—') : (r[9]||'—');
 var isUp = wowStr.charAt(0)==='▲';
 var delta = parseFloat(wowStr.replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
 var w20num = (wowStr && wowStr!=='—') ? (isUp ? metNum-delta : metNum+delta) : metNum;
 var histAttr = 'data-hist-w21="'+metNum+'" data-hist-w20="'+w20num+'" data-hist-label="'+r[0]+'" data-hist-card="'+card+'"';
 var num = idx != null ? '<span style="font-size:10px;font-weight:700;color:var(--ink-muted);min-width:18px;margin-right:4px;">'+(idx<10?'0'+idx:idx)+'.</span>' : '';
 var nameCell = '<td style="padding:7px 0 7px 8px;font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="'+r[0]+'">'+num+r[0]+'</td>';
 var badgeCell = '<td style="padding:7px 4px;text-align:left;white-space:nowrap;"><span class="sev-badge" style="background:'+r[1]+';color:'+r[2]+';font-size:7px;font-weight:700;padding:2px 5px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);white-space:nowrap;">'+r[3]+'</span></td>';
 var tdR = function(v){ return '<td style="padding:7px 4px;text-align:right;font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;">'+v+'</td>'; };
 function pill(str, isGood){
  if(!str||str==='—') return '<td style="padding:7px 2px;text-align:right;"><span style="color:var(--ink-muted);font-size:10px;">—</span></td>';
  var up = str.charAt(0)==='▲'||str.charAt(0)==='+';
  var good = isGood ? up : !up;
  var label = str.replace(/pp$/,'').replace(/,00$/,'').trim();
  return '<td style="padding:7px 2px;text-align:right;"><em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+(good?'#EAF3DE':'#FCE8E6')+';color:'+(good?'#2F6C34':'#C0392B')+';white-space:nowrap;">'+label+'</em></td>';
 }
 var cells;
 if (isCR) {
  cells = card===1
   ? nameCell+badgeCell+tdR(r[4])+pill(r[10]||'—',true)+tdR(r[5])+pill(r[8]||'—',true)
   : nameCell+badgeCell+tdR(r[4])+pill(r[10]||'—',true)+tdR(r[6])+pill(r[9]||'—',true);
 } else {
  cells = card===1
   ? nameCell+badgeCell+tdR(r[4])+pill(r[10]||'—',true)+tdR(r[5])+pill(r[8]||'—',false)
   : nameCell+badgeCell+tdR(r[4])+pill(r[10]||'—',true)+tdR(r[6])+pill(r[9]||'—',true);
 }
 return '<tr '+histAttr+' style="border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'+cells+'</tr>';
}

/* Render tabla AR con trow_ar — top 10 fijo */
function ar_renderTable(n, tbodyId, btnId, rows) {
 var tbody = document.getElementById(tbodyId);
 if (!tbody) return;
 tbody.innerHTML = rows.slice(0, 10).map(function(r,i){ return trow_ar(r, n, i+1); }).join('');
 /* Ocultar siempre el botón Ver más */
 var btn = document.getElementById(btnId);
 if (btn) btn.style.display = 'none';
}

/* KPI headers completos de las cards AR */
function ar_updateKPIs() {
 var isCR = W.mode === 'cr';
 var canasta = W.canasta || 'global';
 var acc = (typeof cv === 'function') ? cv().col : '#5C469C';
 var cdata = (typeof cv === 'function') ? cv() : {};

 /* Función helper: pill WoW */
 function wPill(val, isMejoraSiPositivo) {
  if (val == null || isNaN(val)) return '';
  var up = val > 0;
  var good = isMejoraSiPositivo ? up : !up;
  var bg = good ? '#EAF3DE' : '#FCE8E6';
  var fg = good ? '#2F6C34' : '#C0392B';
  var arrow = up ? '↑' : '↓';
  var txt = arrow + ' ' + Math.abs(val).toFixed(2).replace('.',',');
  return '<span style="display:inline-flex;align-items:center;gap:2px;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;background:'+bg+';color:'+fg+';">'+txt+'</span>';
 }

 /* Función helper: pill % WoW pequeño */
 function wPillSm(val, isMejoraSiPositivo) {
  if (val == null || isNaN(val)) return '';
  var up = val > 0;
  var good = isMejoraSiPositivo ? up : !up;
  var bg = good ? '#EAF3DE' : '#FCE8E6';
  var fg = good ? '#2F6C34' : '#C0392B';
  var arrow = up ? '↑' : '↓';
  var txt = arrow + ' ' + Math.abs(val).toFixed(1).replace('.',',') + '%';
  return '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:'+bg+';color:'+fg+';white-space:nowrap;">'+txt+'</em>';
 }

 /* Función helper: gauge 5 barras */
 function gauge(colors) {
  return colors.map(function(c){ return '<div style="flex:1;background:'+c+';height:6px;opacity:1;"></div>'; }).join('');
 }

 /* Función helper: wow box W20/W21/WoW */
 function wowBox(w20, w21, wow, wowIsGood, acc) {
  var wowGood = wowIsGood ? (parseFloat(wow) > 0) : (parseFloat(wow) < 0);
  var wBg = wowGood ? '#E0F0E2' : '#FCE8E6';
  var wFg = wowGood ? '#2F6C34' : '#C0392B';
  var wPrev = (typeof W !== 'undefined') ? 'W'+(parseInt(W.mode==='cr'?'21':'21')-1) : 'W20';
  var wCurr = 'W21';
  var wowTxt = (parseFloat(wow) > 0 ? '↑ +' : '↓ ') + parseFloat(wow).toFixed(2).replace('.',',');
  return '<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;">'
   +'<div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">'+wPrev+'</div>'
   +'<div style="font-size:14px;font-weight:700;color:var(--ink-soft);margin-top:2px;">'+w20+'</div></div>'
   +'<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;">'
   +'<div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">'+wCurr+'</div>'
   +'<div style="font-size:14px;font-weight:700;margin-top:2px;" style="color:'+acc+'">'+w21+'</div></div>'
   +'<div style="flex:1;text-align:center;background:'+wBg+';padding:5px 4px;border-radius:2px;">'
   +'<div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:'+wFg+';font-weight:700;">WoW</div>'
   +'<div style="font-size:14px;font-weight:700;color:'+wFg+';margin-top:2px;">'+wowTxt+'</div></div>';
 }

 var GAUGE_COLORS = ['#8A8377','#C0392B','#F97316','#FCD34D','#1A6B4A'];

 /* Leer datos de HIST_CR / HIST_RND */
 var ef21='—', ef20='—', efWow=null, efBanda='—', efBandaBg='#F2EEE6', efBandaFg='#5F5E5A', efTarget='';
 var cv21='—', cv20='—', cvWow=null, cvBanda='—', cvBandaBg='#F2EEE6', cvBandaFg='#5F5E5A', cvTarget='';
 var vol='—', trafico='—', trafWow=null;

 if (isCR && typeof HIST_CR !== 'undefined') {
  var ef_e = HIST_CR['hcr-panel-ef'] || HIST_CR['hcr-global-ef'] || {};
  var cv_e = HIST_CR['hcr-panel-cv'] || HIST_CR['hcr-global-cv'] || {};
  if (ef_e.vals && ef_e.vals.length >= 2) {
   var ev = ef_e.vals; ef21 = ev[ev.length-1].toFixed(2).replace('.',',')+' %'; ef20 = ev[ev.length-2].toFixed(2).replace('.',',')+' %';
   efWow = ev[ev.length-1] - ev[ev.length-2];
  }
  if (cv_e.vals && cv_e.vals.length >= 2) {
   var cv_v = cv_e.vals; cv21 = cv_v[cv_v.length-1].toFixed(2).replace('.',',')+' %'; cv20 = cv_v[cv_v.length-2].toFixed(2).replace('.',',')+' %';
   cvWow = cv_v[cv_v.length-1] - cv_v[cv_v.length-2];
  }
  /* Banda y datos del cv() actual */
  if (cdata.ef) { ef21 = cdata.ef+'%'; }
  if (cdata.cv) { cv21 = cdata.cv+'%'; }
  if (cdata.banda_ef) { efBanda = cdata.banda_ef; }
  if (cdata.banda_cv) { cvBanda = cdata.banda_cv; }
  if (cdata.vol)      { vol = cdata.vol; }
  if (cdata.trafico)  { trafico = cdata.trafico; }
  if (cdata.traf_wow) { trafWow = cdata.traf_wow; }
  efTarget = '· Target ≥ 97%'; cvTarget = '· Target ≥ 2,5%';
  /* Colores banda Eficacia */
  var BANDA_C = {
   'Exitosa':      {bg:'#E1F5EE',fg:'#1A6B4A'},
   'Aceptable':    {bg:'#FEF9C3',fg:'#713F12'},
   'Revisar':      {bg:'#FED7AA',fg:'#C2410C'},
   'Crítica':      {bg:'#FCE4F1',fg:'#99162B'},
   'Súper Crítica':{bg:'#E8E6E3',fg:'#2D2828'},
   'Sin Conversión':{bg:'#F2EEE6',fg:'#5F5E5A'}
  };
  var bc1 = BANDA_C[efBanda] || BANDA_C['Sin Conversión'];
  efBandaBg = bc1.bg; efBandaFg = bc1.fg;
  var bc2 = BANDA_C[cvBanda] || BANDA_C['Sin Conversión'];
  cvBandaBg = bc2.bg; cvBandaFg = bc2.fg;
 } else if (!isCR && typeof HIST_RND !== 'undefined') {
  var nd_e  = HIST_RND['hrnd-panel-nd']  || HIST_RND['hrnd-global-nd']  || {};
  var ipm_e = HIST_RND['hrnd-panel-ipm'] || HIST_RND['hrnd-global-ipm'] || {};
  if (nd_e.vals && nd_e.vals.length >= 2) {
   var nv = nd_e.vals; ef21 = nv[nv.length-1].toFixed(2).replace('.',',')+' %'; ef20 = nv[nv.length-2].toFixed(2).replace('.',',')+' %';
   efWow = nv[nv.length-1] - nv[nv.length-2];
  }
  if (ipm_e.vals && ipm_e.vals.length >= 2) {
   var iv = ipm_e.vals;
   cv21 = '$'+Math.round(iv[iv.length-1]).toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.');
   cv20 = '$'+Math.round(iv[iv.length-2]).toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.');
   cvWow = iv[iv.length-1] - iv[iv.length-2];
  }
  if (cdata.ef) { ef21 = cdata.ef; } if (cdata.cv) { cv21 = cdata.cv; }
  if (cdata.banda_ef) { efBanda = cdata.banda_ef; } if (cdata.banda_cv) { cvBanda = cdata.banda_cv; }
  if (cdata.vol)      { vol = cdata.vol; } if (cdata.trafico) { trafico = cdata.trafico; }
  efTarget = '· Target < 3%'; cvTarget = '· Target ≥ $650';
 }

 /* Aplicar a card 1 */
 var k1 = document.getElementById('ar-kpi-1');
 if (k1) { k1.textContent = ef21.replace(' %','%'); k1.style.color = acc; }
 var v1 = document.getElementById('ar1-vol'); if (v1) v1.textContent = vol;
 var wp1 = document.getElementById('ar1-wow-pill'); if (wp1) wp1.innerHTML = wPill(efWow, !isCR ? false : true);
 var tr1 = document.getElementById('ar1-trafico');
 if (tr1) tr1.innerHTML = '<strong style="color:var(--ink);">Tráfico:</strong> ' + trafico;
 var tw1 = document.getElementById('ar1-trafico-wow');
 if (tw1) tw1.innerHTML = cdata.traf_wow != null ? wPillSm(cdata.traf_wow, true) : '';
 var b1 = document.getElementById('ar1-badge');
 if (b1) { b1.textContent = efBanda + ' ' + efTarget; b1.style.background = efBandaBg; b1.style.color = efBandaFg; b1.style.border = '1px solid '+efBandaFg+'44'; }
 var g1 = document.getElementById('ar1-gauge'); if (g1) g1.innerHTML = gauge(GAUGE_COLORS);
 var wb1 = document.getElementById('ar1-wowbox'); if (wb1) wb1.innerHTML = wowBox(ef20, ef21.replace(' %','%'), efWow, !isCR ? false : true, acc);

 /* Aplicar a card 2 */
 var k2 = document.getElementById('ar-kpi-2');
 if (k2) { k2.textContent = cv21.replace(' %','%'); k2.style.color = acc; }
 var v2 = document.getElementById('ar2-vol'); if (v2) v2.textContent = vol;
 var wp2 = document.getElementById('ar2-wow-pill'); if (wp2) wp2.innerHTML = wPill(cvWow, true);
 var tr2 = document.getElementById('ar2-trafico');
 if (tr2) tr2.innerHTML = '<strong style="color:var(--ink);">Tráfico:</strong> ' + trafico;
 var tw2 = document.getElementById('ar2-trafico-wow');
 if (tw2) tw2.innerHTML = cdata.traf_wow != null ? wPillSm(cdata.traf_wow, true) : '';
 var b2 = document.getElementById('ar2-badge');
 var cvBanda2 = cdata.band_cv || cvBanda;
 var cvBandaBg2 = cdata.bbg_cv || cvBandaBg;
 var cvBandaFg2 = cdata.bfg_cv || cvBandaFg;
 if (b2) { b2.textContent = cvBanda2 + ' ' + cvTarget; b2.style.background = cvBandaBg2; b2.style.color = cvBandaFg2; b2.style.border = '1px solid '+cvBandaFg2+'44'; }
 var g2 = document.getElementById('ar2-gauge'); if (g2) g2.innerHTML = gauge(GAUGE_COLORS);
 var wb2 = document.getElementById('ar2-wowbox'); if (wb2) wb2.innerHTML = wowBox(cv20, cv21.replace(' %','%'), cvWow, true, acc);
}

/* ══════════════════════════════════════════════════
   ORDENAMIENTO POR COLUMNA
   ══════════════════════════════════════════════════ */

function _sv(s){
  if(s==null||s===false||s===true) return null;
  s=String(s).trim().replace(/\$/g,'').replace(/%/g,'').trim();
  if(!s||s==='—'||s==='-') return null;
  if(s.indexOf(',')!==-1){s=s.replace(/\./g,'').replace(',','.');}
  else{s=s.replace(/\.(?=\d{3}(?:\.|$))/g,'');}
  var n=parseFloat(s); return isNaN(n)?null:n;
}
function _nd(d){return d==='orig'||d==null?'asc':d==='asc'?'desc':'orig';}
var _SS={};

/* ── Indicador en cursor, no en texto ──────────────────────────
   Usamos cursor para mostrar el estado: pointer siempre,
   color del acento para la col activa. Sin tocar el textContent. */
function _markSortable(els, activeIdx, dir) {
  els.forEach(function(el, i) {
    el.style.cursor = 'pointer';
    el.style.textDecoration = (i===activeIdx && dir && dir!=='orig') ? 'underline' : '';
    el.style.color = (i===activeIdx && dir && dir!=='orig') ? 'var(--accent)' : '';
    el.title = i===activeIdx && dir==='asc' ? '↑ Ascendente (click para Descendente)'
             : i===activeIdx && dir==='desc'? '↓ Descendente (click para Original)'
             : 'Ordenar';
  });
}

/* ══ SORT CARDS KPI — sobre CR_CARD_TABS / RND_CARD_TABS (100 rows) ══ */
var _KPI_RCOLS = {2:5, 4:7}; /* span-header-idx → row-array-idx */

function _kpiSortAttach(card, tkey, isEf, allRows100) {
  var panel = card.querySelector('[data-tab="'+tkey+'"]');
  if (!panel) return;
  var rc = panel.querySelector('.kpi-tab-rows');
  if (!rc) return;
  var hdr = rc.firstElementChild; if (!hdr) return;
  /* Guard: verificar que hdr es el header row, no un row de datos */
  if (hdr.hasAttribute('data-row-idx') || hdr.hasAttribute('data-hist-label')) return;
  var hspans = Array.from(hdr.querySelectorAll('span'));
  if (hspans.length < 5) return; /* header tiene al menos 6 spans */
  var key = (card.id||tkey)+'_'+(isEf?'ef':'cv')+'_'+tkey;
  if (!_SS[key]) _SS[key] = {col:null, dir:'orig'};
  _markSortable(hspans, _SS[key].col, _SS[key].dir);

  hspans.forEach(function(sp, i) {
    if (_KPI_RCOLS[i] == null) return;
    var newSp = sp.cloneNode(true);
    sp.parentNode.replaceChild(newSp, sp);
    newSp.style.cursor = 'pointer';
    newSp.addEventListener('click', function() {
      var st = _SS[key];
      var dir = (st.col===i) ? _nd(st.dir) : 'asc';
      _SS[key] = {col:i, dir:dir};
      var ri = _KPI_RCOLS[i];
      var sorted = allRows100.slice().map(function(r, origIdx){
        return {r:r, origPos: origIdx+1};
      });
      if (dir !== 'orig') {
        sorted.sort(function(a,b){
          var va=_sv(a.r[ri]),vb=_sv(b.r[ri]);
          if(va==null&&vb==null) return 0;
          if(va==null) return 1; if(vb==null) return -1;
          return dir==='asc'?va-vb:vb-va;
        });
      }
      var rowsHtml = sorted.slice(0,10).map(function(item){
        return _cardRow(item.r, item.origPos-1, isEf); /* idx-1 porque _cardRow hace idx+1 */
      }).join('');
      rc.innerHTML = (hdr ? hdr.outerHTML : '') + rowsHtml;
      if (typeof window._injectHistAttrs==='function') window._injectHistAttrs(card);
      setTimeout(function(){_kpiSortAttach(card,tkey,isEf,allRows100);},15);
    });
  });
}

function _initAllSort() {
  var mode = (typeof W!=='undefined') ? W.mode : 'cr';
  var canasta = (typeof W!=='undefined') ? (W.canasta||'global') : 'global';
  var TABS = mode==='cr' ? (typeof CR_CARD_TABS!=='undefined'?CR_CARD_TABS:null)
                         : (typeof RND_CARD_TABS!=='undefined'?RND_CARD_TABS:null);
  if (!TABS) return;
  var tabs = TABS[canasta] || TABS['global'] || {};
  ['ef','cv'].forEach(function(metric){
    var isEf = metric==='ef';
    var suffix = isEf?'-ef-':'-cv-';
    ['destino','corp','hotel'].forEach(function(tkey){
      var allRows = (tabs[metric]||{})[tkey]||[];
      if (!allRows.length) return;
      var radioEl = document.getElementById('tab'+suffix+tkey);
      if (!radioEl) return;
      var card = radioEl.closest('.kpi-card');
      if (!card) return;
      _kpiSortAttach(card, tkey, isEf, allRows);
    });
  });
}

/* ══ SORT CARDS AR — lee 100 rows directamente de data() en cada click ══ */
/* th-idx → row-array-idx */
var _AR_SORT_MAP = {2:4}; /* tráfico: th[2] → r[4] */
/* métrica: th[4] → r[5] (card1) o r[6] (card2) — se calcula al enganchar */

function _arSortAttach(n, tbodyId, btnId) {
  var tbody = document.getElementById(tbodyId); if (!tbody) return;
  var table = tbody.closest('table'); if (!table) return;
  var ths = Array.from(table.querySelectorAll('thead th'));
  var key = tbodyId;
  if (!_SS[key]) _SS[key] = {col:null, dir:'orig'};
  var rmap = {2:4, 4:(n===1?5:6)};
  _markSortable(ths, _SS[key].col, _SS[key].dir);
  var isHotelTbody = tbodyId === 'ar'+n+'-th';

  ths.forEach(function(th, i) {
    if (rmap[i] == null) return;
    var newTh = th.cloneNode(true);
    th.parentNode.replaceChild(newTh, th);
    newTh.style.cursor = 'pointer';
    /* IIFE para capturar i correctamente */
    (function(colIdx){
      var rowIdx = rmap[colIdx];
      newTh.addEventListener('click', function() {
        /* Leer estado actual */
        var st = _SS[key];
        var dir = (st.col===colIdx) ? _nd(st.dir) : 'asc';
        _SS[key] = {col:colIdx, dir:dir};
        /* Obtener todos los rows del source */
        var allRows = isHotelTbody
          ? _arRows(n, _arHTab[n])
          : _arDimRows(n, _arDim[n]);
        /* sort: n=n col=colIdx ri=rowIdx dir=dir allRows=allRows.length */
        /* Ordenar */
        var sorted = allRows.slice().map(function(r, origIdx){
          return {r:r, origPos: origIdx+1}; /* guardar posición original 1-based */
        });
        if (dir !== 'orig') {
          sorted.sort(function(a,b){
            var va=_sv(a.r[rowIdx]), vb=_sv(b.r[rowIdx]);
            if(va==null&&vb==null) return 0;
            if(va==null) return 1; if(vb==null) return -1;
            return dir==='asc' ? va-vb : vb-va;
          });
        }
        /* Escribir top 10 con numeración original */
        var tbEl = document.getElementById(tbodyId);
        if (tbEl) {
          tbEl.innerHTML = sorted.slice(0,10).map(function(item){
            return trow_ar(item.r, n, item.origPos);
          }).join('');
        }
        /* Re-enganchar */
        setTimeout(function(){ _arSortAttach(n, tbodyId, btnId); }, 20);
      });
    })(i);
  });
}

/* Enganchar sort en las cards AR — llamado tras cada render */
function _arSortInit() {
  [1,2].forEach(function(n){
    _arSortAttach(n, 'ar'+n+'-th', 'ar'+n+'-th-more');
    _arSortAttach(n, 'ar'+n+'-td', 'ar'+n+'-td-more');
  });
}

/* Patch ar_renderTable */
var _origART = ar_renderTable;
ar_renderTable = function(n, tbodyId, btnId, rows) {
  _origART(n, tbodyId, btnId, rows);
  setTimeout(function(){ _arSortAttach(n, tbodyId, btnId); }, 50);
};

/* ── Render inicial — DESPUÉS de que _cardRow y w22_renderCardTabs están definidas ── */
setTimeout(function(){ _initAllSort(); _arSortInit(); }, 1500);
var _origSC_s = w22_setC;
w22_setC = function(c,el){
  _origSC_s(c,el);
  _SS = {};
  setTimeout(function(){ _initAllSort(); _arSortInit(); }, 400);
};
var _origSM_s = w22_setMode;
w22_setMode = function(m,el){
  _origSM_s(m,el);
  _SS = {};
  setTimeout(function(){ _initAllSort(); _arSortInit(); }, 400);
};

/* Render inicial aquí para garantizar que _cardRow ya existe */
w22_update();
