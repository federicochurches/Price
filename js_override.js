/
  /* Reset filtros cruzados al cambiar canasta */
  if (typeof _arCrossFilter !== 'undefined') {
    _arCrossFilter = {1:{corp:null,dest:null}, 2:{corp:null,dest:null}};
    if (typeof _arCrossFilterPillsRender === 'function') { _arCrossFilterPillsRender(1); _arCrossFilterPillsRender(2); }
  }
* Semanas históricas — definida aquí para garantizar disponibilidad antes de cualquier uso */
var _SEMANAS_HIST = ["W16","W17","W18","W19","W20","W21","W22","W23"];

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
        ctx.fillStyle = last?accent:'rgba('+rgb+',1)'; ctx.globalAlpha = 1;
        ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3.5:2.5,0,2*Math.PI); ctx.fill();
      }
      /* Bind tooltip RND */
      if (typeof w22_bindCanvasTip === 'function') {
        var metric_rnd = cid.indexOf('ipm')>-1?'ipm':'nodispo';
        w22_bindCanvasTip(el, cid, {vals:cfg.vals, semanas:_SEMANAS_HIST, metric:metric_rnd}, pts);
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
        ctx.fillStyle = last?accent:'rgba('+rgb2+',1)'; ctx.globalAlpha = 1;
        ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3.5:2.5,0,2*Math.PI); ctx.fill();
      }
      /* Bind tooltip CR panel */
      if (typeof w22_bindCanvasTip === 'function') {
        var metric_cr = cid.indexOf('cv')>-1?'convrate':'eficacia';
        w22_bindCanvasTip(el, cid, {vals:cfg.vals, semanas:_SEMANAS_HIST, metric:metric_cr}, pts);
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

  /* Segmented control — siempre negro independiente del modo */
  var seg = document.querySelector('.w22-seg');
  if(seg){ seg.style.border=''; seg.style.borderRadius=''; } /* usar CSS base */
  var btns = document.querySelectorAll('.w22-seg-btn');
  btns.forEach(function(b,i){
    b.classList.remove('on');
    b.style.background=''; b.style.color='';
    if(i===0) b.style.borderRight=''; /* usar CSS base */
  });
  el.classList.add('on');
  el.style.background = ''; el.style.color = ''; /* dejar que CSS .on lo maneje */

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

  /* Bookability — solo visible en CR (Connectivities), oculto en RND (Availability) */
  var bkItemDisplay = (m === 'cr') ? '' : 'none';
  ['w22-strip-bk-item', 'w22-strip-bk-sep', 'ar-strip-bk-item', 'ar-strip-bk-sep'].forEach(function(id){
    var el = document.getElementById(id);
    if (el) el.style.display = bkItemDisplay;
  });

  /* Severity label — cambiar según métrica de referencia */
  var sevLbl = (m === 'cr') ? 'Severity Eficacia' : 'Severity NoDispo';
  var sevLblEls = ['w22-strip-sev-lbl', 'ar-strip-sev-lbl'];
  sevLblEls.forEach(function(id){
    var el = document.getElementById(id);
    if (el) el.textContent = sevLbl;
  });

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
  /* Side-effects adicionales — consolidados desde monkey-patches previos */
  /* Reset sort state */
  if (typeof _SS !== 'undefined') _SS = {};
  /* Reset filtros cruzados al cambiar modo CR↔RND */
  if (typeof _arCrossFilter !== 'undefined') {
    _arCrossFilter = {1:{corp:null,dest:null}, 2:{corp:null,dest:null}};
    if (typeof _arCrossFilterPillsRender === 'function') { _arCrossFilterPillsRender(1); _arCrossFilterPillsRender(2); }
  }
  /* Reset panel selection */
  if (typeof _selectedPanelLabel !== 'undefined') _selectedPanelLabel = null;
  if (typeof _selectedPanelTbody !== 'undefined') _selectedPanelTbody = null;
  /* Re-init panel search (150ms) */
  setTimeout(function(){ if (typeof _initPanelSearch === 'function') _initPanelSearch(); }, 150);
  /* Re-init sort (400ms) */
  setTimeout(function(){
    if (typeof _initAllSort === 'function') _initAllSort();
    if (typeof _arSortInit  === 'function') _arSortInit();
  }, 400);
  /* Sync card3 AR (250ms) — después de todos los renders */
  var _m2 = m;
  setTimeout(function() {
    if (typeof window._syncCard3 === 'function') window._syncCard3(_m2);
    document.body.setAttribute('data-ar-mode', _m2);
  }, 250);
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


/* w22_update() se llama al final del archivo cuando _cardRow ya está definida */
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
                   'hcr-panel-ef','hrnd-panel-nd','hcr-dim-ef','hrnd-dim-nd',
                   'h-bk-global','h-bk-panel','h-bk-dim'];
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
      /* SIEMPRE usar _SEMANAS_HIST — todos los canvas comparten las mismas 8 semanas (W16-W23).
         cfg.semanas puede estar desfasado por timing de registro, así que lo ignoramos. */
      var sems = (_SEMANAS_HIST && _SEMANAS_HIST.length === vals.length) ? _SEMANAS_HIST
               : (cfg.semanas && cfg.semanas.length === vals.length ? cfg.semanas : _SEMANAS_HIST);
      var val = vals[best];
      var fmtVal = cfg.metric === 'ipm'
        ? ('$' + Math.round(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','))
        : val.toFixed(2) + '%';
      var semLabel = sems[best] || ('W' + (16 + best));
      tip.textContent = semLabel + ': ' + fmtVal;
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

/* NOTA: El listener de filas KPI (EF/CV) lo maneja historico_module.attachListeners
   directamente en cada card — incluye selección, deselección (2º click) y highlight.
   NO duplicar aquí para evitar conflictos. */

/* ── Event delegation para histórico de la card BOOKABILITY ────────────────
   Las filas BK (.bk-row) tienen data-lbl, data-bk (fracción 0-1), data-bk-wow.
   Click → actualiza el canvas h-bk-global con el BK% de ese item. */
document.addEventListener('click', function(e) {
  /* No disparar si el click fue en un header de sort */
  if (e.target.closest('[data-sort-key]')) return;
  var row = e.target.closest('.bk-row');
  if (!row) return;
  var bkCard = document.getElementById('kpicard-bk');
  if (!bkCard || !bkCard.contains(row)) return;

  /* Función para volver a la serie GLOBAL del histórico BK */
  function _bkResetGlobal() {
    bkCard.querySelectorAll('.bk-row').forEach(function(r){ r.style.background = ''; r.removeAttribute('data-selected'); });
    /* Disparar hist-reset para que el módulo redibuje con VALS_DEF (global) */
    document.dispatchEvent(new CustomEvent('hist-reset', { detail: { cid: 'h-bk-global' } }));
    var lblEl = document.getElementById('hist-h-bk-global-label');
    if (lblEl) lblEl.textContent = 'Global';
  }

  /* SEGUNDO CLICK en la fila ya seleccionada → deseleccionar y volver a global */
  if (row.getAttribute('data-selected') === '1') {
    _bkResetGlobal();
    return;
  }

  var label = row.getAttribute('data-lbl') || '';
  var bkFrac = parseFloat(row.getAttribute('data-bk') || '0');  /* fracción 0-1 */
  var bkWow = parseFloat(row.getAttribute('data-bk-wow') || '0');  /* delta pp en fracción */
  if (isNaN(bkFrac)) return;

  var bkPct = bkFrac * 100;  /* convertir a % */
  var bkPrev = bkPct - (bkWow * 100);  /* valor de la semana anterior */

  /* Highlight + marcar como seleccionada */
  bkCard.querySelectorAll('.bk-row').forEach(function(r){ r.style.background = ''; r.removeAttribute('data-selected'); });
  row.style.background = 'var(--accent-soft)';
  row.setAttribute('data-selected', '1');

  /* Disparar hist-update para el canvas BK */
  document.dispatchEvent(new CustomEvent('hist-update', {
    detail: { cid: 'h-bk-global', w_curr: bkPct, w_prev: bkPrev, label: label }
  }));

  var labelEl = document.getElementById('hist-h-bk-global-label');
  if (labelEl) labelEl.textContent = label;
});

/* ── Event delegation para histórico del panel (cards AR — tbody) ──────────── */
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
    ctx.fillStyle=last?accent:'rgba('+rgb+',1)'; ctx.globalAlpha=1;
    ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3.5:2.5,0,2*Math.PI); ctx.fill();
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
    ctx.fillStyle=last?accent:'rgba('+rgb+',1)'; ctx.globalAlpha=1;
    ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3.5:2.5,0,2*Math.PI); ctx.fill();
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
    ctx.fillStyle=last?accent:'rgba('+rgb+',1)'; ctx.globalAlpha=1;
    ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,last?3.5:2.5,0,2*Math.PI); ctx.fill();
  }
});
/* ── w22_renderCardTabs — re-renderiza los tabs de las cards KPI CR por canasta ── */
/* ── w22_renderRNDCardTabs — re-renderiza los tabs de las cards KPI RND por canasta ── */
function w22_renderRNDCardTabs(canasta) {
  var RND_TABS = (typeof RND_CARD_TABS !== 'undefined') ? RND_CARD_TABS : null;
  if (!RND_TABS) return;
  var tabs = RND_TABS[canasta] || RND_TABS['global'] || {};
  var grids = { 'nd': 'minmax(0,1fr) 76px 52px 44px 54px 36px', 'ipm': 'minmax(0,1fr) 76px 52px 44px 54px 36px' };
  var hdrs  = { 'nd': ['Severity','Tráfico','WoW','%NoDispo','WoW'], 'ipm': ['Severity','Tráfico','WoW','IPM','WoW'] };
  var _ll = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);text-align:left;padding:2px 0 4px;';
  var _lr = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);text-align:right;padding:2px 0 4px;';
  ['nd','ipm'].forEach(function(metric) {
    var tabPrefix = metric === 'nd' ? 'nd' : 'rpm';
    ['pais','destino','corp','hotel'].forEach(function(tkey) {
      var allRows = ((tabs[metric]||{})[tkey])||[];
      if (!allRows.length) return;
      var radioEl = document.getElementById('tab-'+tabPrefix+'-'+tkey);
      if (!radioEl) return;
      var card = radioEl.closest('.kpi-card'); if (!card) return;
      var panel = card.querySelector('[data-tab="'+tkey+'"]'); if (!panel) return;
      var kpiRows = panel.querySelector('.kpi-tab-rows'); if (!kpiRows) return;
      var grid = grids[metric];
      var hdrSpans = '<span></span>' + hdrs[metric].map(function(h){
        return '<span style="'+(h==='Severity'?_ll:_lr)+'">'+h+'</span>';
      }).join('');
      var hdrHtml = '<div style="display:grid;grid-template-columns:'+grid+';gap:6px;padding:2px 0 4px;border-bottom:1px solid var(--rule);margin-bottom:2px;">'+hdrSpans+'</div>';
      var isEf = (metric === 'nd');
      var rowsHtml = allRows.map(function(r,idx){
        var disp = idx>=_KPI_EXPAND_N ? 'none' : idx>=_KPI_TOP_N ? 'none' : 'grid';
        var cls  = idx>=_KPI_EXPAND_N ? 'sb-hidden' : idx>=_KPI_TOP_N ? 'rows-more' : '';
        return _cardRow(r, idx, isEf, grid, disp, cls);
      }).join('');
      kpiRows.innerHTML = hdrHtml + rowsHtml;
      _moreBtn(kpiRows);
    });
  });
}

function _fmtInt(n){ if(n==null) return '—'; return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.'); }
function _fmtCompact(n){
  if(n==null||isNaN(n)) return '—';
  n = Math.abs(Number(n));
  if(n>=1e9) return (n/1e9).toFixed(1).replace('.',',')+' B';
  if(n>=1e6) return (n/1e6).toFixed(1).replace('.',',')+' M';
  if(n>=1e3) return (n/1e3).toFixed(1).replace('.',',')+' K';
  return Math.round(n).toString();
}
function _fmtPct(n){ if(n==null) return '—'; return n.toFixed(2).replace('.',',')+'%'; }
function _pill(v, bg, fg){ return v==null?'<span style="color:var(--ink-muted);font-size:10px;">—</span>':'<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+bg+';color:'+fg+';white-space:nowrap;">'+v+'</em>'; }
function _wowInt(delta){ if(delta==null) return null; var abs=Math.round(Math.abs(delta)); return (delta>0?'▲':'▼')+_fmtInt(abs); }
function _wowPct(pp){ if(pp==null) return null; var abs=Math.abs(pp); return (pp>0?'▲':'▼')+abs.toFixed(2).replace('.',','); }

function _cardRow(r, idx, isEf, grid){
  /* r: [lab,sub,bbg,bfg,banda, cr_u,cr_wow_delta, val_pct, wow_pp, hist_w21, hist_w20] */
  var lab=r[0], sub=r[1], bbg=r[2], bfg=r[3], banda=r[4];
  var cr_u=r[5], cr_wow_delta=r[6], val_pct=r[7], wow_pp=r[8];
  var hist_w21=r[9]||0, hist_w20=r[10]||hist_w21;
  /* W23+: sin columna severity — grid de 5 cols (sin la columna del badge) */
  var gridCols = grid || (isEf ? 'minmax(0,1fr) 80px 56px 54px 48px'
                                : 'minmax(0,1fr) 80px 56px 68px 40px');
  /* badge sev removido — la card no muestra severity en filas */
  var cr_str = (typeof cr_u === 'string' && /[KMBkmb]/.test(cr_u)) ? cr_u : _fmtCompact(cr_u);
  /* WoW tráfico — para RND r[6] es % (pct), para CR es delta int */
  var tw, tw_bg, tw_fg, tw_pill;
  if (cr_wow_delta != null && !isNaN(cr_wow_delta)) {
    var tw_up = cr_wow_delta > 0;
    tw_bg = tw_up ? '#EAF3DE' : '#FCE8E6';
    tw_fg = tw_up ? '#2F6C34' : '#C0392B';
    /* Si el valor es pequeño (< 100) es un % → mostrar con signo; si es grande es int delta */
    var tw_abs = Math.abs(cr_wow_delta);
    tw = (tw_up?'▲':'▼') + _fmtCompact(tw_abs);
    tw_pill = _pill(tw, tw_bg, tw_fg);
  } else {
    tw_pill = _pill(null, '', '');
  }
  /* WoW métrica */
  var mw = _wowPct(wow_pp);
  var mw_up = wow_pp!=null && (isEf ? wow_pp>0 : wow_pp>0);
  var mw_bg = wow_pp!=null&&mw_up?'#EAF3DE':'#FCE8E6';
  var mw_fg = wow_pp!=null&&mw_up?'#2F6C34':'#C0392B';
  var mw_pill = _pill(mw, mw_bg, mw_fg);
  var nameSpan='<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">'+(idx+1)+'. '+lab+'</span>'
    +(sub?'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">'+sub+'</span>':'');
  var _display = (typeof arguments[4]==='string') ? arguments[4] : 'grid';
  var _cls = (typeof arguments[5]==='string') ? ' class="'+arguments[5]+'"' : '';
  return '<div'+_cls+' data-row-idx="'+idx+'" data-hist-w21="'+hist_w21+'" data-hist-w20="'+hist_w20+'" data-hist-label="'+lab+'"'
    +' style="display:'+_display+';grid-template-columns:'+gridCols+';align-items:center;gap:6px;'
    +'width:100%;padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
    +'<div style="min-width:0;overflow:hidden;">'+nameSpan+'</div>'
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
  
  /* destino / corp / hotel — el render completo (filas + header con sort) lo hace _kpiSortAttach
     al final de esta función. Aquí NO renderizamos para evitar doble-render y reset del sort. */
  
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

    /* Completar con catálogo canónico — channels sin datos = Sin Actividad */
    var CATALOG_PP = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees'];
    var CATALOG_TP = ['Expedia','HotelBeds','Hotel Unico','Travelgate'];
    function _inactive(name){ return [name,'#F2EEE6','#8A8377','Sin Actividad','—','—',null]; }
    var pp_names = pp.map(function(r){ return r[0]; });
    var tp_names = tp.map(function(r){ return r[0]; });
    CATALOG_PP.forEach(function(n){ if(!pp_names.some(function(p){ return p.toLowerCase().indexOf(n.toLowerCase())>=0; })) pp.push(_inactive(n)); });
    CATALOG_TP.forEach(function(n){ if(!tp_names.some(function(p){ return p.toLowerCase().indexOf(n.toLowerCase())>=0; })) tp.push(_inactive(n)); });

    /* Row canal — función unificada para KPI card y AR card (P10)
       opts.cardN : número de card AR (undefined para KPI card)
       opts.w20   : incluir data-hist-w20 (true para AR card)              */
    var acc = (typeof cv==='function') ? cv().col : '#5C469C';
    var pp_html = pp.map(function(r,i){ return _buildChanRow(r,i,{}); }).join('');
    var tp_html = tp.map(function(r,i){ return _buildChanRow(r,i,{}); }).join('');
    var _mkHdr = function(label){return '<div style="display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;align-items:center;gap:6px;padding:4px 0;border-bottom:2px solid '+acc+';margin-bottom:2px;">'+'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);">Channel</span>'+'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;">Trx</span>'+'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:'+acc+';text-align:right;">'+label+'</span>'+'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;">WoW</span>'+'</div>';};
    /* Label de métrica según card (Eficacia / Conv Rate) */
    var metricLbl = (card && card.id === 'kpicard-cv') ? 'Conv Rate' : 'Eficacia';
    /* Layout BK style: PP arriba, TP abajo (flex column) */
    panel.innerHTML = '<div class="chan-wrap" style="display:flex;flex-direction:column;gap:14px;width:100%;">'
      +'<div><div style="font-size:9px;font-weight:700;color:'+acc+';letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>'+_mkHdr(metricLbl)+pp_html+'</div>'
      +'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>'+_mkHdr(metricLbl)+tp_html+'</div>'
      +'</div>';
    if(typeof window._injectHistAttrs==='function') window._injectHistAttrs(card);
  });
  
  /* W23+: Attach sort listeners después de renderizar tabs */
  ['ef','cv'].forEach(function(metric){
    var suffix = metric==='ef' ? '-ef-' : '-cv-';
    ['destino','corp','hotel'].forEach(function(tkey){
      var radioEl = document.getElementById('tab'+suffix+tkey);
      if (!radioEl) return;
      var card = radioEl.closest('.kpi-card');
      if (!card) return;
      var allRows = (tabs[metric]||{})[tkey]||[];
      if (!allRows.length) return;
      _kpiSortAttach(card, tkey, metric, allRows);
    });
  });
}

/* ═══ Función unificada de fila de canal — usada en KPI cards y AR cards (P10) ═══
   r       : [nombre, bbg, bfg, banda, cr_u, val_pct, wow_pp_raw]
   i       : índice 0-based
   opts    : { cardN: int|undefined, w20: bool }
             cardN → agrega data-hist-card para AR cards
             w20   → agrega data-hist-w20 calculado desde WoW
*/
function _buildChanRow(r, i, opts) {
  opts = opts || {};
  var nombre=r[0], banda=r[3], cr_u=r[4], val_pct=r[5], wow_pp_raw=r[6];
  var isInactive = banda === 'Sin Actividad';
  var wow_pp = (wow_pp_raw!=null && wow_pp_raw!=='—' && wow_pp_raw!=='')
    ? parseFloat(String(wow_pp_raw).replace(/[^0-9,.\-]/g,'').replace(',','.')) : null;
  /* TRX formateado */
  var trxStr = (cr_u!=null && cr_u!=='—' && cr_u!=='')
    ? (typeof cr_u === 'string' && /[KMBkmb]/.test(cr_u) ? cr_u : _fmtCompact(cr_u))
    : '—';
  /* WoW métrica pill */
  var mw_up = wow_pp!=null&&!isNaN(wow_pp)&&wow_pp>0;
  var mw = (wow_pp!=null&&!isNaN(wow_pp))
    ? _pill((wow_pp>0?'+':'')+wow_pp.toFixed(2).replace('.',',')+'pp', mw_up?'#EAF3DE':'#FCE8E6', mw_up?'#2F6C34':'#C0392B')
    : '<span style="color:var(--ink-muted);font-size:10px;">—</span>';
  var displayVal = val_pct || '—';
  var metNum = parseFloat(String(val_pct).replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
  var wowNum = (wow_pp!=null&&!isNaN(wow_pp)) ? Math.abs(wow_pp) : 0;
  var w20num = (wow_pp!=null&&!isNaN(wow_pp)) ? (mw_up ? metNum-wowNum : metNum+wowNum) : metNum;
  /* data-hist attrs */
  var histAttrs = 'data-hist-w21="'+metNum+'" data-hist-label="'+nombre+'"';
  if (opts.w20)   histAttrs += ' data-hist-w20="'+w20num+'"';
  if (opts.cardN) histAttrs += ' data-hist-card="'+opts.cardN+'"';
  /* Grid 4 cols como BK: nombre · TRX · valor · WoW (sin WoW Trx, no disponible aquí) */
  var rowStyle = isInactive
    ? 'display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);width:100%;opacity:0.45;'
    : 'display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;width:100%;';
  var nameStyle = 'font-size:11px;font-weight:600;color:'+(isInactive?'var(--ink-muted)':'var(--ink)')+';overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;min-width:0;';
  var trxStyle  = 'text-align:right;font-size:11px;font-weight:700;color:'+(isInactive?'var(--ink-muted)':'var(--ink)')+';font-variant-numeric:tabular-nums;';
  var valStyle  = 'text-align:right;font-size:11px;font-weight:700;color:'+(isInactive?'var(--ink-muted)':'var(--ink)')+';white-space:nowrap;font-variant-numeric:tabular-nums;';
  if (isInactive) {
    return '<div '+histAttrs+' style="'+rowStyle+'">'
      +'<span style="'+nameStyle+'">'+nombre+'</span>'
      +'<span style="font-size:9px;color:var(--ink-muted);font-style:italic;grid-column:2/-1;text-align:right;">sin actividad</span>'
      +'</div>';
  }
  return '<div '+histAttrs+' style="'+rowStyle+'">'
    +'<span style="'+nameStyle+'">'+nombre+'</span>'
    +'<span style="'+trxStyle+'">'+trxStr+'</span>'
    +'<span style="'+valStyle+'">'+displayVal+'</span>'
    +'<div style="text-align:right;">'+mw+'</div>'
    +'</div>';
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
    return _arFilterApply(rows || [], n);
  } else {
    /* Card 2: Conv Rate (CR) ordenado por conv rate ASC / IPM (RND) ordenado por IPM ASC */
    var rows2;
    if (isCR) {
      /* Card 2 BR/SC: mismo pool que card 1 pero re-ordenado por ConvRate (r[6]) ASC */
      var _br2 = (dd.hotels_br || dd.hotels || []).slice().sort(function(a,b){ return parseFloat(String(a[6]||'0').replace('%','').replace(',','.')) - parseFloat(String(b[6]||'0').replace('%','').replace(',','.')); });
      /* Sin Conv: todos tienen CV=0; card 2 ordena por Tráfico DESC */
      var _sc2 = (dd.hotels_sc || dd.hotels || []).slice().sort(function(a,b){
        var parse=function(s){return parseFloat(String(s||'0').replace(/[KMB]$/,function(x){return x==='K'?'000':x==='M'?'000000':'000000000';}).replace(/[^0-9.]/g,''))||0;};
        return parse(b[4])-parse(a[4]); /* tráfico DESC */
      });
      rows2 = tab === 'br' ? _br2 :
              tab === 'sc' ? _sc2 :
              (dd.hotels_cv || dd.hotels_crit || dd.hotels);
    } else {
      rows2 = tab === 'br' ? (dd.hotels_br  || dd.hotels) :
              tab === 'sc' ? (dd.hotels_sc  || dd.hotels) :
              (dd.hotels_dnc || dd.hotels_crit || dd.hotels);
    }
    return _arFilterApply(rows2 || [], n);
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

  /* W23+: Layout vertical (PP arriba, TP abajo) + header con columnas — mismo estilo cards KPI */
  var pp_html = pp.map(function(r,i){ return _buildChanRow(r,i,{cardN:n,w20:true}); }).join('');
  var tp_html = tp.map(function(r,i){ return _buildChanRow(r,i,{cardN:n,w20:true}); }).join('');
  var metricLbl;
  if (isCR) metricLbl = (n === 1) ? 'Eficacia' : 'Conv Rate';
  else      metricLbl = (n === 1) ? '%NoDispo' : 'IPM';
  var _mkHdr = function(lbl){
    return '<div style="display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;'
      +'align-items:center;gap:6px;padding:4px 0;border-bottom:2px solid '+acc+';margin-bottom:2px;">'
      +'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);">Channel</span>'
      +'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;">Trx</span>'
      +'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:'+acc+';text-align:right;">'+lbl+'</span>'
      +'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;">WoW</span>'
      +'</div>';
  };
  var html = '<div style="display:flex;flex-direction:column;gap:14px;padding:8px 0;width:100%;">'
    +'<div><div style="font-size:9px;font-weight:700;color:'+acc+';letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">\uD83C\uDFE0 Producto Propio</div>'+_mkHdr(metricLbl)+pp_html+'</div>'
    +'<div><div style="font-size:9px;font-weight:700;color:'+cyan+';letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">\uD83D\uDD0C Third Party</div>'+_mkHdr(metricLbl)+tp_html+'</div>'
    +'</div>';

  /* Escribir en ar{n}-th (kpi-tab-rows) — mismo contenedor que las otras vistas */
  var container = document.getElementById('ar'+n+'-th');
  if (!container) return;
  container.innerHTML = html;

  /* Ocultar Ver más (no aplica para Channel) */
  var moreWrap = document.getElementById('ar'+n+'-more-wrap');
  if (moreWrap) moreWrap.innerHTML = '';
}

function _arDimRows(n, dim) {
  var dd = data();
  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
  if (dim === 'chan') return dd.chans || dd.dims || [];
  if (dim === 'dest') {
    /* Card 2 en CR: destinos por ConvRate ASC */
    if (n === 2 && isCR && dd.dests_cv) return dd.dests_cv;
    return dd.dests || dd.dims || [];
  }
  /* Corp */
  if (n === 2 && isCR && dd.corps_cv) return dd.corps_cv;
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
    var isCR_upd = (typeof W !== 'undefined') && W.mode === 'cr';
    if (_arDim[n] === 'chan' && isCR_upd) {
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
  /* Re-enganchar sort después de cambiar pestaña hotel */
  setTimeout(function(){ _arSortAttach(n, 'ar'+n+'-th', 'ar'+n+'-th-more'); }, 50);
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
      if (isCR) {
        /* CR: Channel con layout PP/TP */
        if (table) table.style.display = 'none';
        _arRenderChan(n);
      } else {
        /* RND: País — tabla simple con datos de dd.chans (países) */
        if (chanDiv) chanDiv.style.display = 'none';
        if (table) table.style.display = '';
        var drows = _arDimRows(n, 'chan');
        ar_renderTable(n, 'ar'+n+'-td', 'ar'+n+'-td-more', drows);
      }
    } else {
      if (table)   table.style.display   = '';
      if (chanDiv) chanDiv.style.display  = 'none';
      var drows = _arDimRows(n, dim);
      ar_renderTable(n, 'ar'+n+'-td', 'ar'+n+'-td-more', drows);
    }
    /* Re-enganchar sort después de cambiar dimensión */
    setTimeout(function(){ _arSortAttach(n, 'ar'+n+'-td', 'ar'+n+'-td-more'); }, 50);
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
/* Patch w22_update — disparar ar_update después de que el DOM esté actualizado */
var _origW22Update = w22_update;
w22_update = function() {
  _origW22Update.apply(this, arguments);
  ar_update(); /* sincrónicamente — el DOM ya está actualizado */
  setTimeout(_moreBtnAll, 50);
};

/* Inicializar al cargar — después de w22_update() final */

/* ── trow para cards AR: 6 cols, solo la métrica de la card ── */
function trow_ar(r, card, idx) {
 /* Genera div grid igual que _cardRow de las KPI */
 var isCR = W.mode === 'cr';
 var metVal = card === 1 ? r[5] : r[6]; /* ef_val o cv_val — string '12,59%' */
 var metNum = parseFloat(String(metVal||'0').replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
 var wowStr = card === 1 ? (r[8]||'—') : (r[9]||'—'); /* ya tiene ▲/▼ */
 var isUp = wowStr.charAt(0)==='▲';
 var delta = parseFloat(String(wowStr).replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
 var w20num = (wowStr && wowStr!=='—') ? (isUp ? metNum-delta : metNum+delta) : metNum;
 var histAttr = 'data-hist-w21="'+metNum+'" data-hist-w20="'+w20num+'" data-hist-label="'+r[0]+'" data-hist-card="'+card+'"';
 /* Grid 5 cols: nombre · tráfico · wow · métrica · wow — igual KPI */
 var grid = 'minmax(0,1fr) 80px 56px 72px 48px';
 var num = idx != null ? (idx<10?'0':'')+idx+'. ' : '';
 /* Nombre */
 var nameSpan = '<div style="min-width:0;overflow:hidden;"><span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">'+num+r[0]+'</span>'
   +(r[13]?'<span style="font-size:9px;color:var(--ink-muted);display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'+r[13]+'</span>':'')+'</div>';
 /* Tráfico */
 var trafSpan = '<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;">'+r[4]+'</span>';
 /* WoW tráfico */
 function wPill(str, good_if_up) {
  if(!str||str==='—') return '<span style="color:var(--ink-muted);font-size:10px;text-align:right;">—</span>';
  var up = str.charAt(0)==='▲'||str.charAt(0)==='+';
  var good = good_if_up ? up : !up;
  var lbl = str.replace(/pp$/,'').trim(); /* mantener ▲/▼ */
  return '<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+(good?'#EAF3DE':'#FCE8E6')+';color:'+(good?'#2F6C34':'#C0392B')+';white-space:nowrap;display:block;text-align:right;">'+lbl+'</em>';
 }
 /* WoW tráfico — convertir delta absoluto a % relativo */
 var _wt10 = r[10] || '—';
 var wowTraf;
 if (_wt10 === '—' || !_wt10) {
   wowTraf = wPill('—', true);
 } else {
   var _wt_up = _wt10.charAt(0) === '▲';
   var _wt_delta = parseFloat(_wt10.replace(/[^0-9.,]/g,'').replace(',','.')) || 0;
   /* Parsear tráfico actual */
   var _traf_str = String(r[4]||'0').replace(',','.').replace(/K$/i,'000').replace(/M$/i,'000000').replace(/B$/i,'000000000');
   var _traf_curr = parseFloat(_traf_str.replace(/[^0-9.]/g,'')) || 0;
   var _traf_prev = _wt_up ? _traf_curr - _wt_delta : _traf_curr + _wt_delta;
   var _pct = _traf_prev > 0 ? (_wt_delta / _traf_prev * 100) : 0;
   var _pct_str = (_wt_up ? '▲' : '▼') + _pct.toFixed(1).replace('.',',') + '%';
   wowTraf = wPill(_pct_str, true);
 }
 /* Métrica */
 var metSpan = '<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;">'+(metVal!=null?metVal:'—')+'</span>';
 /* WoW métrica — r[8]=ef_wow, r[9]=cv_wow (strings con ▲/▼) */
 var wowMet = isCR
   ? (card===1 ? wPill(r[8]||'—',true) : wPill(r[9]||'—',true))
   : (card===1 ? wPill(r[8]||'—',false): wPill(r[9]||'—',true));
 return '<div '+histAttr+' style="display:grid;grid-template-columns:'+grid+';align-items:center;gap:6px;width:100%;padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
   +nameSpan+trafSpan+wowTraf+metSpan+wowMet+'</div>';
}

/* Render tabla AR con trow_ar */
function ar_renderTable(n, tbodyId, btnId, rows) {
 /* Escribir en div.kpi-tab-rows — igual que las cards KPI */
 var wrap = document.getElementById('ar'+n+'-rows-wrap');
 var container = wrap ? wrap.querySelector('#ar'+n+'-th') : document.getElementById(tbodyId);
 if (!container) return;

 /* Header de columnas — igual al de KPI */
 var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
 var metLbl = n===1 ? (isCR?'Eficacia':'%NoDispo') : (isCR?'Conv Rate':'IPM');
 var grid = 'minmax(0,1fr) 80px 56px 72px 48px';
 var _s = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);';
 var _mkSH = function(lbl, col, acc) {
   var state = _arSortState[n] || {};
   var _d = state.dir || (state.asc?'asc':'desc');
   var ico = state.col===col && _d!=='orig' ? (_d==='asc'?' <span style="font-size:8px;">↑</span>':' <span style="font-size:8px;">↓</span>') : ' <span style="opacity:.35;font-size:8px;">↕</span>';
   var colStyle = acc ? 'color:var(--accent);' : '';
   return '<span onclick="_arSort('+n+',\''+col+'\')" style="'+_s+'text-align:right;padding:2px 0 4px;cursor:pointer;user-select:none;'+colStyle+'">'+lbl+ico+'</span>';
 };
 var hdr = '<div style="display:grid;grid-template-columns:'+grid+';gap:6px;padding:2px 0 4px;border-bottom:1px solid var(--rule);margin-bottom:2px;">'
   +'<span></span>'
   +_mkSH('Tráfico','traf',false)
   +'<span style="'+_s+'text-align:right;padding:2px 0 4px;">WoW</span>'
   +_mkSH(metLbl,'met',true)
   +'<span style="'+_s+'text-align:right;padding:2px 0 4px;">WoW</span>'
   +'</div>';

 var rowsHtml = rows.map(function(item,i){
   /* Soportar tanto {r, origPos} como array plano */
   var r = (item && item.r !== undefined) ? item.r : item;
   var origPos = (item && item.origPos !== undefined) ? item.origPos : (i+1);
   var html = trow_ar(r, n, origPos);
   if(i >= _KPI_EXPAND_N) {
     /* Reemplazar display:grid por display:none y agregar clase sb-hidden */
     html = html.replace(/^(<div)/, '$1 class="sb-hidden"')
                .replace('display:grid', 'display:none');
   } else if(i >= _KPI_TOP_N) {
     html = html.replace(/^(<div)/, '$1 class="rows-more"')
                .replace('display:grid', 'display:none');
   }
   return html;
 }).join('');

 container.innerHTML = hdr + rowsHtml;

 /* Botón Ver más — activar botón estático directamente sin destruirlo */
 var _staticMoreBtn = document.getElementById('ar'+n+'-th-more');
 if (_staticMoreBtn) {
   if (rows.length > _KPI_TOP_N) {
     _staticMoreBtn.style.display = '';
     _staticMoreBtn.textContent = 'Ver más ▾';
     _staticMoreBtn.setAttribute('data-exp','0');
     (function(btn, container) {
       btn.onclick = function() {
         var exp = btn.getAttribute('data-exp') !== '1';
         btn.setAttribute('data-exp', exp ? '1' : '0');
         container.querySelectorAll('.rows-more').forEach(function(r) {
           r.style.setProperty('display', exp ? 'grid' : 'none', 'important');
         });
         btn.textContent = exp ? 'Ver menos ▴' : 'Ver más ▾';
       };
     })(_staticMoreBtn, document.getElementById('ar'+n+'-th'));
   } else {
     _staticMoreBtn.style.display = 'none';
   }
 }

 /* Conectar searchbox sb-ar{n} */
 var sbN = document.getElementById('sb-ar'+n);
 if (sbN) {
   var clrN = document.getElementById('sb-ar'+n+'-clear');
   sbN.oninput = function() {
     var q = sbN.value.toLowerCase();
     container.querySelectorAll('[data-hist-label]').forEach(function(row) {
       var lbl = (row.getAttribute('data-hist-label')||'').toLowerCase();
       var match = lbl.indexOf(q) >= 0;
       if (!q) {
         /* Sin filtro: restaurar visibilidad original */
         row.style.display = (row.classList.contains('rows-more') || row.classList.contains('sb-hidden')) ? 'none' : 'grid';
       } else {
         row.style.display = match ? 'grid' : 'none';
       }
     });
     if (clrN) clrN.style.display = q ? 'inline' : 'none';
   };
   if (clrN) {
     clrN.onclick = function() { sbN.value = ''; sbN.oninput(); };
   }
 }
}

/* KPI headers completos de las cards AR */
/* ══════════════════════════════════════════════════════════════
   ar_updateKPIs — refactorizado W23-bk-s3
   Un solo flujo para CR y RND — los modos difieren solo en config
   ══════════════════════════════════════════════════════════════ */

/* Config por modo: qué canvas leer, qué targets mostrar, dirección del WoW */
var _AR_MODE_CFG = {
  cr: {
    hist_ef:     'hcr-global-ef',
    hist_cv:     'hcr-global-cv',
    ef_target:   '· Target ≥ 97%',
    cv_target:   '· Target ≥ 2,5%',
    ef_good_up:  true,   /* eficacia: más alto = mejor */
    cv_good_up:  true,   /* conv rate: más alto = mejor */
    cv_is_ipm:   false,
  },
  rnd: {
    hist_ef:     'hrnd-global-nd',
    hist_cv:     'hrnd-global-ipm',
    ef_target:   '· Target < 3%',
    cv_target:   '· Target ≥ $650',
    ef_good_up:  false,  /* NoDispo: más bajo = mejor */
    cv_good_up:  true,   /* IPM: más alto = mejor */
    cv_is_ipm:   true,
  }
};

/* Paleta de bandas compartida */
var _AR_BANDA_C = {
  'Exitosa':       {bg:'#E1F5EE', fg:'#1A6B4A'},
  'Aceptable':     {bg:'#FEF9C3', fg:'#713F12'},
  'Revisar':       {bg:'#FED7AA', fg:'#C2410C'},
  'Crítica':       {bg:'#FCE4F1', fg:'#99162B'},
  'Súper Crítica': {bg:'#E8E6E3', fg:'#2D2828'},
  'Sin Conversión':{bg:'#F2EEE6', fg:'#5F5E5A'},
};

/* Leer y normalizar los datos de KPI para el modo activo */
function _arReadKpiData(cdata, cfg) {
  var HIST = W.mode === 'cr' ? (typeof HIST_CR !== 'undefined' ? HIST_CR : {})
                              : (typeof HIST_RND !== 'undefined' ? HIST_RND : {});
  var d = {
    ef21:'—', ef20:'—', efWow:null, efBanda:'—',
    efBandaBg:'#F2EEE6', efBandaFg:'#5F5E5A',
    cv21:'—', cv20:'—', cvWow:null, cvBanda:'—',
    cvBandaBg:'#F2EEE6', cvBandaFg:'#5F5E5A',
    vol:'—', trafico:'—', trafWow:null,
  };

  /* EF (Eficacia o NoDispo) */
  if (cdata.ef_prev != null) {
    d.ef20 = cdata.ef_prev; d.ef21 = cdata.ef; d.efWow = cdata.ef_wow;
  } else {
    var ef_g = HIST[cfg.hist_ef] || {};
    if (ef_g.vals && ef_g.vals.length >= 2) {
      var ev = ef_g.vals;
      d.ef21 = ev[ev.length-1].toFixed(2).replace('.',',')+' %';
      d.ef20 = ev[ev.length-2].toFixed(2).replace('.',',')+' %';
      d.efWow = ev[ev.length-1] - ev[ev.length-2];
    }
    if (cdata.ef) d.ef21 = cdata.ef;
  }

  /* CV (ConvRate o IPM) */
  if (cdata.cv_prev != null) {
    d.cv20 = cdata.cv_prev; d.cv21 = cdata.cv; d.cvWow = cdata.cv_wow;
  } else {
    var cv_g = HIST[cfg.hist_cv] || {};
    if (cv_g.vals && cv_g.vals.length >= 2) {
      var iv = cv_g.vals;
      if (cfg.cv_is_ipm) {
        d.cv21 = '$'+Math.round(iv[iv.length-1]).toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.');
        d.cv20 = '$'+Math.round(iv[iv.length-2]).toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.');
      } else {
        d.cv21 = iv[iv.length-1].toFixed(2).replace('.',',')+' %';
        d.cv20 = iv[iv.length-2].toFixed(2).replace('.',',')+' %';
      }
      d.cvWow = iv[iv.length-1] - iv[iv.length-2];
    }
    if (cdata.cv) d.cv21 = cdata.cv;
  }

  /* Bandas — fuente de verdad: cdata.band / cdata.band_cv (del pickle) */
  if (cdata.band) {
    d.efBanda   = cdata.band;
    d.efBandaBg = cdata.bbg || d.efBandaBg;
    d.efBandaFg = cdata.bfg || d.efBandaFg;
  } else {
    var bc1 = _AR_BANDA_C[d.efBanda] || _AR_BANDA_C['Sin Conversión'];
    d.efBandaBg = bc1.bg; d.efBandaFg = bc1.fg;
  }
  if (cdata.band_cv) {
    d.cvBanda   = cdata.band_cv;
    d.cvBandaBg = cdata.bbg_cv || d.cvBandaBg;
    d.cvBandaFg = cdata.bfg_cv || d.cvBandaFg;
  } else {
    var bc2 = _AR_BANDA_C[d.cvBanda] || _AR_BANDA_C['Sin Conversión'];
    d.cvBandaBg = bc2.bg; d.cvBandaFg = bc2.fg;
  }

  /* Vol, tráfico */
  if (cdata.vol)      d.vol      = cdata.vol;
  if (cdata.trafico)  d.trafico  = cdata.trafico;
  if (cdata.traf_wow) d.trafWow  = cdata.traf_wow;

  return d;
}

/* Aplicar datos al DOM de una card AR (n=1 o n=2) */
function _arApplyCard(n, kpiId, badgeId, gaugeId, wowBoxId,
                      kpiVal, badgeVal, badgeBg, badgeFg,
                      w20, w21, wow, wowGoodUp, acc,
                      vol, trafico, trafWow, GAUGE_COLORS,
                      wPill, wPillSm, gauge, wowBox) {
  var k = document.getElementById(kpiId);
  if (k) { k.textContent = kpiVal.replace(' %','%'); k.style.color = acc; }
  var v = document.getElementById('ar'+n+'-vol'); if (v) v.textContent = vol;
  var wp = document.getElementById('ar'+n+'-wow-pill');
  if (wp) wp.innerHTML = wPill(wow, wowGoodUp);
  var tr = document.getElementById('ar'+n+'-trafico');
  if (tr) tr.innerHTML = '<strong style="color:var(--ink);">Tráfico:</strong> ' + trafico;
  var tw = document.getElementById('ar'+n+'-trafico-wow');
  if (tw) tw.innerHTML = trafWow != null ? wPillSm(trafWow, true) : '';
  var b = document.getElementById(badgeId);
  if (b) { b.textContent = (badgeVal && badgeVal!=='—' ? badgeVal : '');
           b.style.background = badgeBg; b.style.color = badgeFg;
           b.style.border = '1px solid '+badgeFg+'44'; }
  var g = document.getElementById(gaugeId);
  if (g) g.innerHTML = gauge(GAUGE_COLORS);
  var wb = document.getElementById(wowBoxId);
  if (wb) wb.innerHTML = wowBox(w20, kpiVal.replace(' %','%'), wow, wowGoodUp, acc);
}

/* Orquestador principal */
function ar_updateKPIs() {
  var isCR = W.mode === 'cr';
  var acc  = (typeof cv === 'function') ? cv().col : '#5C469C';
  var cdata = (typeof cv === 'function') ? cv() : {};
  var cfg  = _AR_MODE_CFG[W.mode] || _AR_MODE_CFG.cr;
  var d    = _arReadKpiData(cdata, cfg);

  var GAUGE_COLORS = ['#8A8377','#C0392B','#F97316','#FCD34D','#1A6B4A'];

  /* Helpers inline */
  function wPill(val, goodIfUp) {
    if (val == null || isNaN(val)) return '';
    var up = val > 0;
    var good = goodIfUp ? up : !up;
    var bg = good ? '#EAF3DE' : '#FCE8E6';
    var fg = good ? '#2F6C34' : '#C0392B';
    return '<span style="display:inline-flex;align-items:center;gap:2px;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;background:'+bg+';color:'+fg+';">'+(up?'↑':'↓')+' '+Math.abs(val).toFixed(2).replace('.',',')+'</span>';
  }
  function wPillSm(val, goodIfUp) {
    if (val == null || isNaN(val)) return '';
    var up = val > 0;
    var good = goodIfUp ? up : !up;
    var bg = good ? '#EAF3DE' : '#FCE8E6';
    var fg = good ? '#2F6C34' : '#C0392B';
    return '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:'+bg+';color:'+fg+';white-space:nowrap;">'+(up?'↑':'↓')+' '+Math.abs(val).toFixed(1).replace('.',',')+'%</em>';
  }
  function gauge(colors) {
    return colors.map(function(c){ return '<div style="flex:1;background:'+c+';height:6px;opacity:1;"></div>'; }).join('');
  }
  function wowBox(w20, w21, wow, goodIfUp, acc) {
    var wowGood = goodIfUp ? (parseFloat(wow) > 0) : (parseFloat(wow) < 0);
    var wBg = wowGood ? '#E0F0E2' : '#FCE8E6';
    var wFg = wowGood ? '#2F6C34' : '#C0392B';
    var wowTxt = (parseFloat(wow) > 0 ? '↑ +' : '↓ ') + parseFloat(wow).toFixed(2).replace('.',',');
    var wPrev = (typeof W !== 'undefined') ? 'W'+(parseInt(W.mode==='cr'?'22':'22')) : 'W22';
    var wCurr = (typeof W !== 'undefined') ? 'W'+(parseInt(W.mode==='cr'?'23':'23')) : 'W23';
    return '<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;"><div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">'+wPrev+'</div><div style="font-size:14px;font-weight:700;color:var(--ink-soft);margin-top:2px;">'+w20+'</div></div>'
      +'<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;"><div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">'+wCurr+'</div><div style="font-size:14px;font-weight:700;margin-top:2px;color:'+acc+';">'+w21+'</div></div>'
      +'<div style="flex:1;text-align:center;background:'+wBg+';padding:5px 4px;border-radius:2px;"><div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:'+wFg+';font-weight:700;">WoW</div><div style="font-size:14px;font-weight:700;color:'+wFg+';margin-top:2px;">'+wowTxt+'</div></div>';
  }

  /* Card 1: EF / NoDispo */
  _arApplyCard(1,'ar-kpi-1','ar1-badge','ar1-gauge','ar1-wowbox',
    d.ef21, d.efBanda, d.efBandaBg, d.efBandaFg,
    d.ef20, d.ef21, d.efWow, cfg.ef_good_up, acc,
    d.vol, d.trafico, d.trafWow, GAUGE_COLORS,
    wPill, wPillSm, gauge, wowBox);

  /* Card 2: CV / IPM */
  var cvBanda2   = cdata.band_cv   || d.cvBanda;
  var cvBandaBg2 = cdata.bbg_cv    || d.cvBandaBg;
  var cvBandaFg2 = cdata.bfg_cv    || d.cvBandaFg;
  _arApplyCard(2,'ar-kpi-2','ar2-badge','ar2-gauge','ar2-wowbox',
    d.cv21, cvBanda2, cvBandaBg2, cvBandaFg2,
    d.cv20, d.cv21, d.cvWow, cfg.cv_good_up, acc,
    d.vol, d.trafico, d.trafWow, GAUGE_COLORS,
    wPill, wPillSm, gauge, wowBox);

  /* Badges del strip de KPIs */
  function _parsePct(s) {
    if (typeof s === 'number') return s;
    return parseFloat(String(s||'').replace('%','').replace(',','.'));
  }
  function _banda(val, metric) {
    var p = val / 100;
    if (metric === 'ef' || metric === 'bk') {
      if (p >= 0.97) return {lbl:'Exitosa',     bg:'#E1F5EE',fg:'#1A6B4A'};
      if (p >= 0.93) return {lbl:'Aceptable',   bg:'#FEF9C3',fg:'#7B6F00'};
      if (p >= 0.85) return {lbl:'Revisar',     bg:'#FED7AA',fg:'#C2410C'};
      if (p >= 0.60) return {lbl:'Crítica',     bg:'#FCCDD9',fg:'#99162B'};
      return               {lbl:'Súper Crítica',bg:'#E8E6E3',fg:'#2D2828'};
    }
    if (metric === 'cv') {
      if (p <= 0)     return {lbl:'Sin Conv.',  bg:'#F2EEE6',fg:'#5F5E5A'};
      if (p < 0.008)  return {lbl:'Crítica',    bg:'#FCCDD9',fg:'#99162B'};
      if (p < 0.015)  return {lbl:'Revisar',    bg:'#FED7AA',fg:'#C2410C'};
      if (p <= 0.025) return {lbl:'Aceptable',  bg:'#FEF9C3',fg:'#7B6F00'};
      return               {lbl:'Exitosa',    bg:'#E1F5EE',fg:'#1A6B4A'};
    }
    return {lbl:'—',bg:'#F2EEE6',fg:'#5F5E5A'};
  }
  function _applyBand(id, val, metric) {
    var el = document.getElementById(id); if (!el || isNaN(val)) return;
    var b = _banda(val, metric);
    el.textContent = b.lbl;
    el.style.background = b.bg; el.style.color = b.fg;
    el.style.outline = '1px solid '+b.fg+'55';
  }
  _applyBand('w22-strip-ef-band', _parsePct(d.ef21), 'ef');
  _applyBand('w22-strip-cv-band', _parsePct(d.cv21), 'cv');
  /* BK badge se maneja en tryInitBK */
}


/* ══════════════════════════════════════════════════════════════
   FILTRO CRUZADO — AR cards (P12)
   Estado independiente por card. Corp y Dest en AND.
   r[11]=CorpName, r[12]=Destino en rows de hotel (desde W24).
   Activar: click en fila Corp/Dest mientras view=corp/dest.
   Desactivar: click en × del pill activo.
   Reset: cambio de modo CR↔RND o de canasta.
   ══════════════════════════════════════════════════════════════ */

var _arCrossFilter = {1: {corp:null, dest:null}, 2: {corp:null, dest:null}};

function _arNormCF(s) {
  return String(s||'').trim().toLowerCase()
    .replace(/[áàä]/g,'a').replace(/[éèë]/g,'e')
    .replace(/[íìï]/g,'i').replace(/[óòö]/g,'o')
    .replace(/[úùü]/g,'u').replace(/ñ/g,'n');
}

function _arFilterApply(rows, n) {
  var f = _arCrossFilter[n];
  if (!f || (!f.corp && !f.dest)) return rows;
  return rows.filter(function(r) {
    if (f.corp && _arNormCF(r[11]||'').indexOf(_arNormCF(f.corp)) < 0) return false;
    if (f.dest && _arNormCF(r[12]||'').indexOf(_arNormCF(f.dest)) < 0) return false;
    return true;
  });
}

function _arCrossFilterPillsRender(n) {
  var container = document.getElementById('ar'+n+'-cross-pills');
  if (!container) return;
  var f = _arCrossFilter[n];
  var isCR = (typeof W !== 'undefined') && W.mode === 'cr';
  var acc = isCR ? '#5C469C' : '#EA0074';
  var accBg = isCR ? '#EDE8F7' : '#FCE4F1';
  var html = '';
  var _pill = function(type, label, bg, fg, border) {
    return '<span class="ar-cross-pill" data-cross-n="'+n+'" data-cross-type="'+type+'"'
      +' style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px 3px 10px;'
      +'border-radius:20px;font-size:9px;font-weight:700;background:'+bg+';color:'+fg+';'
      +'border:1px solid '+border+';white-space:nowrap;cursor:pointer;">'
      +label+' <span style="font-size:11px;opacity:.65;">&#x00D7;</span></span>';
  };
  if (f.corp) html += _pill('corp', 'Corp: '+f.corp, accBg, acc, acc);
  if (f.dest) html += _pill('dest', 'Dest: '+f.dest, '#E1F5EE', '#2F6C34', '#2F6C34');
  container.innerHTML = html;
  container.style.display = html ? 'flex' : 'none';
}

/* Limpiar un filtro */
function _arCrossFilterClear(n, type) {
  if (type) { _arCrossFilter[n][type] = null; }
  else       { _arCrossFilter[n] = {corp:null, dest:null}; }
  _arCrossFilterPillsRender(n);
  _arPillRender(n);
}

/* Event delegation: pills × y clicks en filas Corp/Dest */
document.addEventListener('click', function(e) {
  /* Click en pill × — eliminar ese filtro */
  var pill = e.target.closest('.ar-cross-pill');
  if (pill) {
    var cn = parseInt(pill.getAttribute('data-cross-n'));
    var ct = pill.getAttribute('data-cross-type');
    if (cn && ct) _arCrossFilterClear(cn, ct);
    return;
  }
  /* Click en fila de dim — activar filtro si vista es corp o dest */
  var dimRow = e.target.closest('[data-hist-label]');
  if (!dimRow) return;
  /* ¿En qué card está el div? */
  var cn = 0;
  for (var ni = 1; ni <= 2; ni++) {
    var _c = document.getElementById('ar'+ni+'-th');
    if (_c && _c.contains(dimRow)) { cn = ni; break; }
  }
  if (!cn) return;
  /* Solo actuar si la vista activa es corp o dest */
  var view = (typeof _arPillView !== 'undefined') ? (_arPillView[cn] || 'hotel') : 'hotel';
  if (view !== 'corp' && view !== 'dest') return;
  var val = dimRow.getAttribute('data-hist-label') || '';
  if (!val) return;
  /* Toggle: si ya está activo con ese valor, quitar */
  _arCrossFilter[cn][view] = (_arCrossFilter[cn][view] === val) ? null : val;
  _arCrossFilterPillsRender(cn);
  _arPillRender(cn);
});

/* ══════════════════════════════════════════════════
   ORDENAMIENTO POR COLUMNA
   ══════════════════════════════════════════════════ */

function _sv(s){
  if(s==null||s===false||s===true) return null;
  s=String(s).trim().replace(/\$/g,'').replace(/%/g,'').trim();
  if(!s||s==='—'||s==='-') return null;
  /* Detectar sufijos K/M/B antes de parsear */
  var mult=1;
  var su=s.toUpperCase();
  if(/[KMB]$/.test(su)){
    var last=su[su.length-1];
    if(last==='K') mult=1e3;
    else if(last==='M') mult=1e6;
    else if(last==='B') mult=1e9;
    s=s.slice(0,-1); /* quitar sufijo */
  }
  if(s.indexOf(',')!==-1){s=s.replace(/\./g,'').replace(',','.');}
  else{s=s.replace(/\.(?=\d{3}(?:\.|$))/g,'');}
  var n=parseFloat(s); return isNaN(n)?null:n*mult;
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

/* ── renderTopN — renderiza todos los rows, top N visibles, resto sb-hidden ──
   El searchbox ya tiene lógica para mostrar todos cuando hay query (ri<TOP_N check).
   Aquí ponemos TODO en el DOM para que el search opere sobre los 500. */
var _KPI_TOP_N = 5;   /* filas visibles por defecto */

/* Aplicar _moreBtn a todos los paneles activos después del render inicial */
function _moreBtnAll() {
  document.querySelectorAll('.kpi-tab-rows').forEach(function(el) {
    /* Solo si tiene rows-more y no tiene ya el botón */
    if (el.querySelector('.rows-more') && !el.querySelector('.kpi-more-btn')) {
      _moreBtn(el);
    }
  });
  /* También para las tablas AR */
  [1,2].forEach(function(n) {
    ['th','td'].forEach(function(t) {
      var tbodyId = 'ar'+n+'-'+t;
      var tbody = document.getElementById(tbodyId);
      if (!tbody) return;
      var wrap = tbody.closest('table');
      if (wrap && wrap.parentNode) {
        if (wrap.querySelector('.rows-more') && !wrap.parentNode.querySelector('.kpi-more-btn')) {
          _moreBtn(wrap.parentNode, tbodyId);
        }
      }
    });
  });
}
var _KPI_EXPAND_N = 10; /* filas visibles tras expandir */

/* ── Ver más / menos botón para cards KPI ── */
function _moreBtn(containerEl, tbodyId) {
  /* Preferir el botón HTML estático si existe (más confiable que createElement) */
  var staticBtn = containerEl.querySelector('button[id$="-more"]');
  if (staticBtn) {
    /* Activar el botón estático si hay rows-more */
    var moreRows = tbodyId
      ? (document.getElementById(tbodyId) || containerEl).querySelectorAll('.rows-more')
      : containerEl.querySelectorAll('.rows-more');
    if (!moreRows.length) { staticBtn.style.display = 'none'; return; }
    staticBtn.style.display = '';
    staticBtn.textContent = 'Ver más ▾';
    staticBtn.setAttribute('data-exp', '0');
    /* onclick inline robusto — usa el tbodyId para localizar las filas */
    var sid = tbodyId || staticBtn.id.replace('-more','');
    staticBtn.setAttribute('onclick', [
      '(function(btn){',
      '  var exp=btn.getAttribute("data-exp")!=="1";',
      '  btn.setAttribute("data-exp",exp?"1":"0");',
      '  var tb=document.getElementById("' + sid + '");',
      '  var rows=tb?tb.querySelectorAll(".rows-more"):[];',
      '  Array.prototype.forEach.call(rows,function(r){',
      '    var show=exp?(r.tagName==="TR"?"table-row":"grid"):"none";',
      '    r.style.setProperty("display",show,"important");',
      '    if(exp&&r.tagName==="TR"){r.style.borderBottom="1px solid var(--rule-soft)";r.style.cursor="pointer";}',
      '  });',
      '  btn.textContent=exp?"Ver menos ▴":"Ver más ▾";',
      '})(this)'
    ].join(''));
    return;
  }
  /* Fallback: crear botón dinámico si no hay estático */
  if (containerEl.querySelector('.kpi-more-btn')) return;
  var moreRows2 = containerEl.querySelectorAll('.rows-more');
  if (!moreRows2.length) return;
  var btn = document.createElement('div');
  btn.className = 'kpi-more-btn';
  btn.style.cssText = 'margin:8px 0 2px;border-top:1px solid var(--rule-soft);color:var(--ink-muted);font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;padding:8px 0 2px;text-align:center;user-select:none;';
  btn.textContent = 'Ver más ▾';
  var sid2 = tbodyId || '';
  btn.setAttribute('onclick', [
    '(function(btn){',
    '  var exp=btn.getAttribute("data-exp")!=="1";',
    '  btn.setAttribute("data-exp",exp?"1":"0");',
    '  var p=btn.parentNode;',
    '  var rows=p?p.querySelectorAll(".rows-more"):[];',
    '  Array.prototype.forEach.call(rows,function(r){',
    '    var d=exp?(r.tagName==="TR"?"table-row":"grid"):"none";',
    '    r.style.setProperty("display",d,"important");',
      '    if(exp&&r.tagName==="TR"){r.style.borderBottom="1px solid var(--rule-soft)";r.style.cursor="pointer";}',
    '  });',
    '  btn.textContent=exp?"Ver menos ▴":"Ver más ▾";',
    '})(this)'
  ].join(''));
  containerEl.appendChild(btn);
}

function _renderAllRows(rows, renderFn) {
  return rows.map(function(item, i) {
    var html = renderFn(item, i);
    /* Marcar los que van más allá del top visible como sb-hidden */
    if (i >= _KPI_TOP_N) {
      html = html.replace(/^(<div|<tr)/, '$1 class="sb-hidden" style="display:none;"');
      /* Si ya tiene class, agregamos sb-hidden */
      if (html.indexOf('sb-hidden') === -1) {
        html = html.replace(/^(<div[^>]*?)>/, '$1 class="sb-hidden" style="display:none;">');
      }
    }
    return html;
  }).join('');
}

/* ══ SORT CARDS KPI — sobre CR_CARD_TABS / RND_CARD_TABS (100 rows) ══ */
/* Row CR y RND: [lab, sub, bbg, bfg, banda, traf(r[5]), cr_wow(r[6]), val(r[7]), wow_pp(r[8]), ...] */
/* W23+: mapeo col header → índice en array r.
   Header EF/CV: [<span vacío=nombre>, Tráfico(col1), WoW(col2), Métrica(col3), WoW(col4)]
   Array r: [nombre(0), sub(1), bbg(2), bfg(3), banda(4), traf(5), traf_wow(6), val(7), val_wow(8), ...]
   El nombre (span vacío) NO tiene data-sort-col, así que col1 = primera columna visible = Tráfico = r[5] */
var _KPI_RCOLS_CR  = {1:5, 2:6, 3:7, 4:8};
var _KPI_RCOLS_RND = {1:5, 2:6, 3:7, 4:8};
var _KPI_RCOLS = _KPI_RCOLS_CR;

/* Grid CSS por métrica — para que _cardRow use el correcto según la card */
var _KPI_GRID = {
  ef:  'minmax(0,1fr) 80px 56px 54px 48px',
  cv:  'minmax(0,1fr) 80px 56px 68px 40px',
  nd:  'minmax(0,1fr) 76px 52px 44px 54px 36px',
  ipm: 'minmax(0,1fr) 76px 52px 44px 54px 36px',
};

function _kpiSortAttach(card, tkey, metricKey, allRows100) {
  var panel = card.querySelector('[data-tab="'+tkey+'"]');
  if (!panel) return;

  var isEf = (metricKey === 'ef' || metricKey === 'nd');
  var grid  = _KPI_GRID[metricKey] || _KPI_GRID['ef'];
  var key   = (card.id||'c')+'_'+metricKey+'_'+tkey;
  /* Guardar SIEMPRE las filas actuales para que el listener las use */
  panel._kpiSortRows = allRows100;
  panel._kpiSortKey  = key;
  panel._kpiSortIsEf = isEf;
  panel._kpiSortGrid = grid;
  if (!_SS[key]) _SS[key] = {col:null, dir:'orig'};

  /* Función que aplica el sort activo (o el orden original) y renderiza */
  function _applySort() {
    var st = _SS[key];
    var sorted = allRows100.slice().map(function(r, origIdx){ return {r:r, origPos:origIdx+1}; });
    if (st.col != null && st.dir && st.dir !== 'orig') {
      var ri = _KPI_RCOLS_CR[st.col];
      if (ri != null) {
        sorted.sort(function(a,b){
          var va = a.r[ri], vb = b.r[ri];
          if (ri === 0) {
            var sa = (va||'').toString(), sb = (vb||'').toString();
            return st.dir === 'asc' ? sa.localeCompare(sb) : sb.localeCompare(sa);
          }
          va = _sv(va); vb = _sv(vb);
          if(va==null&&vb==null) return 0;
          if(va==null) return 1; if(vb==null) return -1;
          return st.dir==='asc' ? va-vb : vb-va;
        });
      }
    }
    _kpiSortRender(panel, sorted, st.col, st.dir, isEf, grid, key, allRows100);
  }
  panel._kpiApplySort = _applySort;

  /* Si ya tiene listener activo, solo re-renderizar manteniendo el sort activo */
  if (panel._kpiSortActive) {
    _applySort();
    return;
  }
  panel._kpiSortActive = true;

  /* Render inicial */
  _applySort();

  /* Event delegation en el panel — UN solo listener permanente */
  if (!panel._kpiSortListenerAttached) {
    panel._kpiSortListenerAttached = true;
    panel.addEventListener('click', function(e) {
      var sp = e.target.closest('[data-sort-col]');
      if (!sp) return;
      var rc = panel.querySelector('.kpi-tab-rows');
      if (!rc || !rc.contains(sp)) return;
      var i = parseInt(sp.getAttribute('data-sort-col'));
      if (_KPI_RCOLS_CR[i] == null) return;
      var k = panel._kpiSortKey;
      var st = _SS[k] || {col:null, dir:'orig'};
      var dir = (st.col === i) ? _nd(st.dir) : 'asc';
      _SS[k] = {col:i, dir:dir};
      /* Re-aplicar sort usando la función guardada (siempre usa allRows100 actuales) */
      if (typeof panel._kpiApplySort === 'function') panel._kpiApplySort();
    });
  }
}

/* Función standalone de render para KPI sort — reutilizable */
function _kpiSortRender(panel, sorted10, activeCol, dir, isEf, grid, key, allRows100) {
  var rc = panel.querySelector('.kpi-tab-rows');
  if (!rc) return;
  var metricKey = key.split('_')[1] || 'ef';
  var _ll = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);text-align:left;padding:2px 0 4px;';
  var _lr = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);text-align:right;padding:2px 0 4px;';
  var hdrLabels = {
    ef:  ['Tráfico','WoW','Eficacia','WoW'],
    cv:  ['Tráfico','WoW','Conv Rate','WoW'],
    nd:  ['Severity','Tráfico','WoW','%NoDispo','WoW'],
    ipm: ['Severity','Tráfico','WoW','IPM','WoW'],
  };
  var labels = hdrLabels[metricKey] || hdrLabels.ef;
  var hdrSpans = '<span></span>' + labels.map(function(h, i){
    var isActive = (i+1 === activeCol) && dir && dir !== 'orig';
    var baseStyle = h === 'Severity' ? _ll : _lr;
    var extra = isActive ? 'color:var(--accent);' : '';
    var arrow = isActive
      ? ' <em class="kpi-sort-arrow" style="font-style:normal;opacity:1;color:var(--accent);">'+(dir==='desc'?'↓':'↑')+'</em>'
      : ' <em class="kpi-sort-arrow" style="font-style:normal;opacity:.4;">↕</em>';
    return '<span style="'+baseStyle+extra+'cursor:pointer;user-select:none;" data-sort-col="'+(i+1)+'">'+h+arrow+'</span>';
  }).join('');
  var hdrHtml = '<div style="display:grid;grid-template-columns:'+grid+';gap:6px;padding:2px 0 4px;border-bottom:1px solid var(--rule);margin-bottom:2px;" data-sort-hdr="1">'+hdrSpans+'</div>';
  var rowsHtml = sorted10.map(function(item,i){
    var disp = i>=_KPI_EXPAND_N ? 'none' : i>=_KPI_TOP_N ? 'none' : 'grid';
    var cls  = i>=_KPI_EXPAND_N ? 'sb-hidden' : i>=_KPI_TOP_N ? 'rows-more' : '';
    return _cardRow(item.r, item.origPos-1, isEf, grid, disp, cls);
  }).join('');
  rc.innerHTML = hdrHtml + rowsHtml;
  _moreBtn(rc);
}

/* Mapeo de metricKey → sufijo de tab ID y clave en TABS */
var _METRIC_DEFS = {
  'ef':  {suffix:'-ef-',  tabKeys:['nd','ef'], tabs_key:'ef'},
  'cv':  {suffix:'-cv-',  tabKeys:['nd','cv'], tabs_key:'cv'},
  'nd':  {suffix:'-nd-',  tabKeys:['pais','destino','corp','hotel'], tabs_key:'nd'},
  'ipm': {suffix:'-rpm-', tabKeys:['pais','destino','corp','hotel'], tabs_key:'ipm'},
};

function _initAllSort() {
  var mode    = (typeof W!=='undefined') ? W.mode    : 'cr';
  var canasta = (typeof W!=='undefined') ? (W.canasta||'global') : 'global';

  /* Resetear flags para forzar re-enganche */
  document.querySelectorAll('[data-tab]').forEach(function(p){ p._sortKey = null; });
  document.querySelectorAll('thead').forEach(function(t){ t._sortKey = null; });

  if (mode === 'cr') {
    /* CR: cards Eficacia + ConvRate */
    var CR_TABS = (typeof CR_CARD_TABS!=='undefined') ? CR_CARD_TABS : null;
    if (!CR_TABS) return;
    var tabs = CR_TABS[canasta] || CR_TABS['global'] || {};
    ['ef','cv'].forEach(function(metric){
      var suffix = metric==='ef' ? '-ef-' : '-cv-';
      ['destino','corp','hotel'].forEach(function(tkey){
        var allRows = (tabs[metric]||{})[tkey]||[];
        if (!allRows.length) return;
        var radioEl = document.getElementById('tab'+suffix+tkey);
        if (!radioEl) return;
        var card = radioEl.closest('.kpi-card');
        if (!card) return;
        _kpiSortAttach(card, tkey, metric, allRows);
      });
    });
  } else {
    /* RND: cards NoDispo + IPM — buscar tabs en los panels RND */
    /* Los tabs RND usan IDs tab-nd-* y tab-rpm-* */
    var RND_TABS = (typeof RND_CARD_TABS!=='undefined') ? RND_CARD_TABS : null;
    /* Si RND_CARD_TABS no existe, intentar enganchar directamente del DOM */
    ['nd','rpm'].forEach(function(tabPrefix){
      var metricKey = tabPrefix === 'nd' ? 'nd' : 'ipm';
      ['pais','destino','corp','hotel'].forEach(function(tkey){
        var radioEl = document.getElementById('tab-'+tabPrefix+'-'+tkey);
        if (!radioEl) return;
        var card = radioEl.closest('.kpi-card');
        if (!card) return;
        /* allRows: leer de RND_CARD_TABS si existe, sino tabla vacía */
        var allRows = RND_TABS ? ((RND_TABS[canasta]||RND_TABS['global']||{})[metricKey]||{})[tkey]||[] : [];
        /* Con allRows vacío el sort opera sobre el DOM pero sin re-render JS */
        _kpiSortAttach(card, tkey, metricKey, allRows);
      });
    });
  }
}

/* ══ SORT CARDS AR — lee 100 rows directamente de data() en cada click ══ */
/* th-idx → row-array-idx */
var _AR_SORT_MAP = {2:4}; /* tráfico: th[2] → r[4] */
/* métrica: th[4] → r[5] (card1) o r[6] (card2) — se calcula al enganchar */

/* ── Sort clickeable para cards AR 1/2 (sistema div-grid W23+) ── */
var _arSortState = {};
function _arSort(n, col) {
  var prev = _arSortState[n] || {col:null, dir:'orig'};
  /* 3 estados: orig→asc→desc→orig (igual que KPI cards) */
  var dir = (prev.col === col) ? _nd(prev.dir) : 'asc';
  _arSortState[n] = {col:col, dir:dir};
  /* Obtener filas según view/filt */
  var view = _arPillView[n] || 'hotel';
  var filt = _arPillFilt[n] || 'crit';
  var rows;
  if (view === 'hotel') {
    var tabMap = {crit:'crit', br:'br', sc:'sc'};
    rows = _arRows(n, tabMap[filt] || 'crit');
  } else if (view === 'chan') { return; }
  else { rows = _arDimRows(n, view); }
  /* Asignar origPos (posición en dataset original) */
  var rowsWithOrig = rows.map(function(r, i){ return {r: r, origPos: i+1}; });
  if (dir !== 'orig') {
    var colIdx = col === 'traf' ? 4 : (n===1 ? 5 : 6);
    rowsWithOrig = rowsWithOrig.slice().sort(function(a, b) {
      var va = parseFloat(String(a.r[colIdx]||'0').replace(/[KkMmBb]$/,function(m){return m.toUpperCase()==='K'?'000':m.toUpperCase()==='M'?'000000':'000000000';}).replace(/[^0-9.]/g,'')) || 0;
      var vb = parseFloat(String(b.r[colIdx]||'0').replace(/[KkMmBb]$/,function(m){return m.toUpperCase()==='K'?'000':m.toUpperCase()==='M'?'000000':'000000000';}).replace(/[^0-9.]/g,'')) || 0;
      return dir === 'asc' ? va-vb : vb-va;
    });
  }
  ar_renderTable(n, 'ar'+n+'-th', 'ar'+n+'-th-more', rowsWithOrig);
}


function _arPillRender(n) {
  /* Resetear sort al cambiar pill → vuelve al orden original del dataset */
  _arSortState[n] = {col:null, dir:'orig'};
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


function _arSortAttach(n, tbodyId, btnId) {
  var tbody = document.getElementById(tbodyId); if (!tbody) return;
  var table = tbody.closest('table'); if (!table) return;
  var thead = table.querySelector('thead'); if (!thead) return;

  /* Remover listener anterior si existe */
  if (thead._sortAbort) { thead._sortAbort.abort(); }
  var ac = (typeof AbortController !== 'undefined') ? new AbortController() : null;
  thead._sortAbort = ac;
  thead._sortKey = tbodyId;

  var key = tbodyId;
  if (!_SS[key]) _SS[key] = {col:null, dir:'orig'};
  var rmap = {2:4, 4:(n===1?5:6)};
  var isHotelTbody = tbodyId === 'ar'+n+'-th';

  /* Marcar columnas ordenables */
  var ths = Array.from(thead.querySelectorAll('th'));
  ths.forEach(function(th, i) {
    if (rmap[i] != null) {
      th.style.cursor = 'pointer';
      th.setAttribute('data-sort-col', i);
    }
  });
  _markSortable(ths, _SS[key].col, _SS[key].dir);

  /* Event delegation en thead */
  var listenerOpts = ac ? {signal: ac.signal} : {};
  thead.addEventListener('click', function(e) {
    var th = e.target.closest('[data-sort-col]');
    if (!th) return;
    var colIdx = parseInt(th.getAttribute('data-sort-col'));
    var rowIdx = rmap[colIdx];
    if (rowIdx == null) return;

    var st = _SS[key];
    var dir = (st.col === colIdx) ? _nd(st.dir) : 'asc';
    _SS[key] = {col:colIdx, dir:dir};

    /* Leer rows actuales dinámicamente */
    var allRows = isHotelTbody ? _arRows(n, _arHTab[n]) : _arDimRows(n, _arDim[n]);
    var sorted = allRows.slice().map(function(r, origIdx){
      return {r:r, origPos: origIdx+1};
    });
    if (dir !== 'orig') {
      sorted.sort(function(a,b){
        var va=_sv(a.r[rowIdx]), vb=_sv(b.r[rowIdx]);
        if(va==null&&vb==null) return 0;
        if(va==null) return 1; if(vb==null) return -1;
        return dir==='asc' ? va-vb : vb-va;
      });
    }
    var tbEl = document.getElementById(tbodyId);
    if (tbEl) {
      tbEl.innerHTML = sorted.map(function(item,i){
        var html = trow_ar(item.r, n, item.origPos);
        if(i >= _KPI_EXPAND_N) {
      html = html.replace(/^(<tr)/, '$1 class="sb-hidden" style="display:none;"');
    } else if(i >= _KPI_TOP_N) {
      html = html.replace(/^(<tr)/, '$1 class="rows-more" style="display:none;"');
    }
        return html;
      }).join('');
      /* Actualizar botón Ver más tras re-render */
      var tbl = tbEl.closest('table');
      if (tbl && tbl.parentNode) {
        var existing = tbl.parentNode.querySelector('.kpi-more-btn');
        if (existing) existing.remove();
        _moreBtn(tbl.parentNode, tbodyId);
      }
    }
    _markSortable(Array.from(thead.querySelectorAll('th')), colIdx, dir);
  }, listenerOpts);
}

/* Enganchar sort en las cards AR — llamado tras cada render */
function _arSortInit() {
  [1,2].forEach(function(n){
    _arSortAttach(n, 'ar'+n+'-th', 'ar'+n+'-th-more');
    _arSortAttach(n, 'ar'+n+'-td', 'ar'+n+'-td-more');
  });
}

/* Patch ar_renderTable — re-enganchar sort después de render */
var _origART = ar_renderTable;
ar_renderTable = function(n, tbodyId, btnId, rows) {
  _origART(n, tbodyId, btnId, rows);
  /* Limpiar flag para que _arSortAttach re-enganche en el nuevo thead */
  var tbody = document.getElementById(tbodyId);
  if (tbody) { var t = tbody.closest('table'); if (t && t.querySelector('thead')) t.querySelector('thead')._sortKey = null; }
  setTimeout(function(){ _arSortAttach(n, tbodyId, btnId); }, 10);
};

/* ── Render inicial — DESPUÉS de que _cardRow y w22_renderCardTabs están definidas ── */
var _origSC_s = w22_setC;
w22_setC = function(c,el){
  _origSC_s(c,el);
  _SS = {};
  setTimeout(function(){ _initAllSort(); _arSortInit(); }, 400);
};

/* Render inicial aquí para garantizar que _cardRow ya existe */
w22_update();
setTimeout(_moreBtnAll, 300); /* Botones Ver más después del render inicial */

/* Sort inicial — después de w22_update() para que el DOM esté listo */
setTimeout(function(){ _initAllSort(); _arSortInit(); }, 200);

/* ══════════════════════════════════════════════════════════════════════
   FIX 1 — Searchbox panel AR (w22-ph / w22-pd)
   Opera sobre [data-hist-label] en w22-th y w22-td.
   Se re-inicializa en cada cambio de canasta/modo.
   ══════════════════════════════════════════════════════════════════════ */
(function initPanelSearch() {
  function _normStr(s) { return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,''); }

  function _attachPanelSb(inputId, tbodyId, countId, clearId) {
    var input   = document.getElementById(inputId);
    var countEl = document.getElementById(countId);
    var clearBtn= document.getElementById(clearId);
    if (!input) return;

    function _filter() {
      var q = _normStr(input.value.trim());
      var tbody = document.getElementById(tbodyId);
      if (!tbody) return;
      var rows = tbody.querySelectorAll('[data-hist-label]');
      var vis = 0, total = rows.length;
      rows.forEach(function(r, i) {
        var match = !q || _normStr(r.getAttribute('data-hist-label')||'').indexOf(q) >= 0;
        if (q) {
          if (match) {
            r.classList.remove('sb-hidden'); r.classList.remove('rows-more');
            r.style.setProperty('display','table-row','important'); vis++;
          } else {
            r.style.setProperty('display','none','important');
          }
        } else {
          /* Sin query: restaurar visibilidad original por índice */
          var ri = parseInt(r.getAttribute('data-row-idx')||String(i));
          if (ri < _KPI_TOP_N) {
            r.classList.remove('sb-hidden'); r.classList.remove('rows-more');
            r.style.setProperty('display','table-row','important'); vis++;
          } else if (ri < _KPI_EXPAND_N) {
            /* rows-more — visibles solo si el botón está expandido */
            var btn = document.getElementById(tbodyId + '-more');
            var expanded = btn && btn.getAttribute('data-exp') === '1';
            if (expanded) { r.style.setProperty('display','table-row','important'); vis++; }
            else { r.classList.add('rows-more'); r.style.setProperty('display','none','important'); }
          } else {
            r.classList.add('sb-hidden'); r.style.setProperty('display','none','important');
          }
        }
      });
      if (clearBtn) clearBtn.style.display = q ? 'inline-block' : 'none';
      if (countEl) {
        if (q) { countEl.textContent = vis + ' / ' + total; countEl.className = 'sb-pill-count has-q'; }
        else   { countEl.textContent = ''; countEl.className = 'sb-pill-count'; }
      }
    }

    /* Limpiar handler anterior si existe */
    if (input._panelSbAttached) { input.removeEventListener('input', input._panelSbHandler); }
    input._panelSbHandler = function() { _filter(); };
    input._panelSbAttached = true;
    input.addEventListener('input', input._panelSbHandler);

    if (clearBtn) {
      clearBtn.onclick = function() { input.value = ''; _filter(); input.focus(); };
    }

    /* Exponer para que otros patches puedan re-filtrar tras render */
    window['_panelSbFilter_' + tbodyId] = _filter;
  }

  function _initPanelSearch() {
    _attachPanelSb('sb-panel-th', 'w22-th', 'cnt-panel-th', 'sb-panel-th-clear');
    _attachPanelSb('sb-panel-td', 'w22-td', 'cnt-panel-td', 'sb-panel-td-clear');
  }

  /* Limpiar searchbox y contador al cambiar tab de hotel o dim */
  function _clearPanelSb(inputId, countId) {
    var inp = document.getElementById(inputId);
    var cnt = document.getElementById(countId);
    if (inp) { inp.value = ''; }
    if (cnt) { cnt.textContent = ''; cnt.className = 'sb-pill-count'; }
    var clr = document.getElementById(inputId + '-clear');
    if (clr) clr.style.display = 'none';
  }

  /* Re-correr _injectHistAttrs Y re-lanzar filtro tras cada render de tabla */
  var _origRT_sb = w22_renderTable;
  w22_renderTable = function(tbodyId, btnId, rows, open) {
    _origRT_sb(tbodyId, btnId, rows, open);
    /* Limpiar searchbox al re-renderizar (cambio de tab) */
    if (tbodyId === 'w22-th') _clearPanelSb('sb-panel-th', 'cnt-panel-th');
    if (tbodyId === 'w22-td') _clearPanelSb('sb-panel-td', 'cnt-panel-td');
  };

  /* Init con retry hasta que los inputs existan */
  (function tryInit() {
    if (document.getElementById('sb-panel-th')) { _initPanelSearch(); }
    else { setTimeout(tryInit, 100); }
  })();

  /* Re-init al cambiar modo CR↔RND o canasta */
    var _origSC_sb = w22_setC;
  w22_setC = function(c, el) { _origSC_sb(c, el); setTimeout(_initPanelSearch, 150); };
})();

/* ══════════════════════════════════════════════════════════════════════
   FIX 2 — Clicks en rows 6-1000 (rows-more / sb-hidden)
   _injectHistAttrs solo corre en render inicial. Los rows-more
   no tienen data-hist-w21 hasta que se hacen visibles.
   Patch: inyectar attrs también al expandir con "Ver más".
   ══════════════════════════════════════════════════════════════════════ */
(function patchMoreBtnInject() {
  /* Interceptar _moreBtn para agregar inyección de hist attrs al expand */
  var _origMoreBtn = _moreBtn;
  _moreBtn = function(containerEl, tbodyId) {
    _origMoreBtn(containerEl, tbodyId);
    /* Buscar el botón recién configurado y wrappear su onclick */
    var sid = tbodyId || '';
    var btn = containerEl.querySelector('button[id="' + sid + '-more"]') ||
              containerEl.querySelector('button[id$="-more"]');
    if (!btn) return;
    var prevOnclick = btn.getAttribute('onclick') || '';
    if (prevOnclick.indexOf('_injectAfterExpand') >= 0) return; /* ya patcheado */
    /* Agregar llamada a inject después del expand */
    btn.setAttribute('onclick', prevOnclick +
      ';(function(){' +
      '  var tb=document.getElementById("' + sid + '");' +
      '  if(!tb||typeof window._injectHistAttrs!=="function") return;' +
      '  var trs=tb.querySelectorAll("tr");' +
      '  /* Re-inyectar solo los que faltan (sin data-hist-w21) */' +
      '  var allRows=tb._lastRows||[];' +
      '  trs.forEach(function(tr,i){' +
      '    if(tr.getAttribute("data-hist-w21")) return;' +
      '    var r=allRows[i]; if(!r) return;' +
      '    tr.setAttribute("data-hist-label", r[0]||"");' +
      '    tr.setAttribute("data-row-idx", String(i));' +
      '    tr.style.cursor="pointer";' +
      '    var v=parseFloat((r[5]||"0").toString().replace(/[^0-9,.]/g,"").replace(",","."));' +
      '    if(!isNaN(v)){tr.setAttribute("data-hist-w21",String(v));}' +
      '  });' +
      '  /* Re-filtrar searchbox si hay query activo */' +
      '  if(tb.id==="w22-th"&&typeof window._panelSbFilter_w22_th==="function") window._panelSbFilter_w22_th();' +
      '  if(tb.id==="w22-td"&&typeof window._panelSbFilter_w22_td==="function") window._panelSbFilter_w22_td();' +
      '})();'
    );
  };

  /* Guardar _lastRows en cada render para que el inject los encuentre */
  var _origRT_rows = w22_renderTable;
  w22_renderTable = function(tbodyId, btnId, rows, open) {
    var tb = document.getElementById(tbodyId);
    if (tb) tb._lastRows = rows;
    _origRT_rows(tbodyId, btnId, rows, open);
  };
})();

/* ══════════════════════════════════════════════════════════════════════
   FIX 3 — Persistencia de selección entre pestañas del panel AR
   Al cambiar tab (Críticos → Bajo Rendimiento), w22_renderTable
   re-escribe el tbody y se pierde el highlight.
   Guardamos _selectedPanelLabel y lo re-aplicamos tras cada render.
   ══════════════════════════════════════════════════════════════════════ */
(function patchPanelSelection() {
  var _selectedPanelLabel = null; /* label del hotel/dim seleccionado */
  var _selectedPanelTbody = null; /* 'w22-th' o 'w22-td' */

  /* Capturar selección en el click listener existente */
  var _origClickHandler = null; /* El listener ya está en GLOBAL_PANEL_SCRIPT */
  /* Hookear con un listener adicional en capture phase */
  document.addEventListener('click', function(e) {
    var row = e.target.closest ? e.target.closest('[data-hist-w21]') : null;
    if (!row) return;
    var tbody = row.closest('tbody');
    if (!tbody) return;
    if (tbody.id !== 'w22-th' && tbody.id !== 'w22-td') return;

    var label = row.getAttribute('data-hist-label') || '';
    var isAlready = row.getAttribute('data-selected') === '1';
    if (isAlready) {
      /* Segundo click = deseleccionar */
      _selectedPanelLabel = null;
      _selectedPanelTbody = null;
    } else {
      _selectedPanelLabel = label;
      _selectedPanelTbody = tbody.id;
    }
  }, true); /* capture — antes del listener principal */

  /* Re-aplicar selección tras cada w22_renderTable */
  var _origRT_sel = w22_renderTable;
  w22_renderTable = function(tbodyId, btnId, rows, open) {
    _origRT_sel(tbodyId, btnId, rows, open);
    if (!_selectedPanelLabel || tbodyId !== _selectedPanelTbody) return;
    /* Buscar la fila con el mismo label y re-aplicar highlight */
    setTimeout(function() {
      var tbody = document.getElementById(tbodyId);
      if (!tbody) return;
      var accent = (typeof cv === 'function') ? cv().col : '#5C469C';
      var accentAlpha = accent === '#EA0074' ? 'rgba(234,0,116,0.07)' :
                        accent === '#FCB000' ? 'rgba(252,176,0,0.10)' :
                        accent === '#4FC3F4' ? 'rgba(79,195,244,0.10)' :
                        'rgba(92,70,156,0.07)';
      /* Limpiar selección previa */
      tbody.querySelectorAll('[data-selected="1"]').forEach(function(r) {
        r.style.background = ''; r.removeAttribute('data-selected');
      });
      /* Aplicar en la fila que coincide */
      var trs = tbody.querySelectorAll('[data-hist-label]');
      trs.forEach(function(tr) {
        if (tr.getAttribute('data-hist-label') === _selectedPanelLabel) {
          tr.setAttribute('data-selected', '1');
          tr.style.background = accentAlpha;
        }
      });
    }, 20);
  };

  /* Limpiar selección al cambiar canasta o modo */
    var _origSC_sel = w22_setC;
  w22_setC = function(c, el) {
    _selectedPanelLabel = null; _selectedPanelTbody = null;
    _origSC_sel(c, el);
  };
})();

/* ══════════════════════════════════════════════════
   CARD 3 — BOOKABILITY
   ar3_renderTable(view, htab)
   ar3_setView(view)
   ar3_setHotelTab(htab)
   ══════════════════════════════════════════════════ */

var _ar3_view  = 'hotel';
var _ar3_htab  = 'crit';

function ar3_fmt(v) {
  return typeof v === 'number' ? (v * 100).toFixed(2) + '%' : String(v || '—');
}

function ar3_bandColors(banda) {
  var k = (banda||'').toLowerCase().replace(/[áàä]/g,'a').replace(/[éè]/g,'e').replace(/[íì]/g,'i').replace(/[ó]/g,'o').replace(/[ú]/g,'u').replace(/\s+/g,'').replace('crítica','critica').replace('superc','sc').replace('súperc','sc').replace('sincon','sinconv').replace('sinconv.','sinconv');
  var map = {
    exitosa:   ['#E1F5EE','#1A6B4A'],
    aceptable: ['#FEF9C3','#713F12'],
    revisar:   ['#FED7AA','#C2410C'],
    critica:   ['#FCE4F1','#99162B'],
    sc:        ['#E8E6E3','#2D2828'],
    sinconv:   ['#F2EEE6','#5F5E5A'],
  };
  return map[k] || map[(banda||'').toLowerCase()] || ['#F2EEE6','#5F5E5A'];
}

function ar3_bandLabel(banda) {
  var k = (banda||'').toLowerCase();
  var map = {exitosa:'Exitosa',aceptable:'Aceptable',revisar:'Revisar',
             crítica:'Crítica',critica:'Crítica',sc:'Súper Crítica','súper crítica':'Súper Crítica','super critica':'Súper Crítica',sinconv:'Sin Conv.','sin conversión':'Sin Conv.'};
  return map[k] || banda || '—';
}


/* Sort para card 3 (BK) */
var _ar3SortState = {col:null, asc:true};
function _ar3Sort(col) {
  /* 3 estados: orig→asc→desc→orig (igual que KPI cards) */
  var prevDir = (_ar3SortState && _ar3SortState.col === col) ? _ar3SortState.dir : 'orig';
  var dir = _nd(prevDir);
  _ar3SortState = {col:col, dir:dir, asc:(dir==='asc')};
  ar3_renderTable(_ar3_view, _ar3_htab, _ar3SortState);
}

function ar3_renderTable(view, htab) {
  if (typeof BK_DATA === 'undefined' || !BK_DATA) return;
  _ar3_view = view || _ar3_view;
  _ar3_htab = htab || _ar3_htab;

  /* Channel (prov): usar render con split PP/TP */
  if (_ar3_view === 'prov') { _ar3_renderChan(); return; }

  var rows = BK_DATA[_ar3_view] || [];
  var tbody = document.getElementById('ar3-tbody');
  var thDim = document.getElementById('ar3-th-dim');
  if (!tbody) return;

  // Actualizar header de columna
  var dimLabels = {prov:'Provider', dest:'Destino', corp:'Corporativo', hotel:'Hotel'};
  if (thDim) thDim.textContent = dimLabels[_ar3_view] || _ar3_view;

  // Filtrar por banda según htab
  var bandMap = {crit: ['critica','sc'], br: ['revisar','aceptable'], sc: ['sinconv']};
  var activeBands = bandMap[_ar3_htab] || [];

  // Ordenar según sortState o peor BK primero por defecto
  var _ss3 = arguments[2] || _ar3SortState || {col:null, asc:true};
  /* Añadir origPos (posición original en dataset) ANTES del sort */
  var rowsWithPos = rows.map(function(r, i){ return {r: r, origPos: i + 1}; });
  /* Respetar 3 estados: orig=sin sort, asc, desc */
  var _dir3 = _ss3.dir || (_ss3.asc ? 'asc' : 'desc');
  if (_dir3 !== 'orig') {
    rowsWithPos.sort(function(a, b){
      var va, vb;
      if (_ss3.col === 'trx') {
        va = a.r.books || 0; vb = b.r.books || 0;
      } else {
        va = parseFloat(String(a.r.val||'0').replace('%','').replace(',','.')) || 0;
        vb = parseFloat(String(b.r.val||'0').replace('%','').replace(',','.')) || 0;
      }
      return _dir3 === 'asc' ? va-vb : vb-va;
    });
  }

  // Filtrar
  /* Normalizar banda para comparación sin acentos/mayúsculas */
  function _normBanda(b) {
    var s=(b||'').toLowerCase();
    s=s.replace(/[íì]/g,'i').replace(/[áà]/g,'a')
       .replace(/[éè]/g,'e').replace(/[óò]/g,'o').replace(/[úùü]/g,'u');
    if(s==='s\u00faper cr\u00edtica'||s==='super critica') return 'sc';
    if(s==='sin conversi\u00f3n'||s==='sin conversion') return 'sinconv';
    return s;
  }
  var filteredWithPos = rowsWithPos.filter(function(item){ return activeBands.indexOf(_normBanda(item.r.banda)) >= 0; });
  /* Sin Conv: BK_DATA nunca tiene esa banda → no usar fallback, mostrar vacío */
  var _isSinConv = (_ar3_htab === 'sc');
  if (filteredWithPos.length === 0 && !_isSinConv) filteredWithPos = rowsWithPos;
  /* Renumerar localmente dentro del subset filtrado (1, 2, 3...) */
  filteredWithPos = filteredWithPos.map(function(item, i){ return {r: item.r, origPos: i + 1}; });
  /* alias para hasMore check */
  var filtered = filteredWithPos;

  /* Grid igual a cards 1/2: nombre · Books · WoW · BK% · WoW */
  var grid = 'minmax(0,1fr) 56px 44px 72px 48px';
  var _s = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);';
  var _mk3SH = function(lbl, col, acc) {
    var state = _ar3SortState || {};
    var _d3 = state.dir || (state.asc?'asc':'desc');
    var ico = state.col===col && _d3!=='orig' ? (_d3==='asc'?' <span style="font-size:8px;">↑</span>':' <span style="font-size:8px;">↓</span>') : ' <span style="opacity:.35;font-size:8px;">↕</span>';
    var cStyle = acc ? 'color:#333132;' : '';
    return '<span onclick="_ar3Sort(\''+col+'\')" style="'+_s+'text-align:right;padding:2px 0 4px;cursor:pointer;user-select:none;'+cStyle+'">'+lbl+ico+'</span>';
  };
  var hdr = '<div style="display:grid;grid-template-columns:'+grid+';gap:6px;padding:2px 0 4px;border-bottom:1px solid var(--rule);margin-bottom:2px;">'
    +'<span></span>'
    +_mk3SH('Trx','trx',false)
    +'<span style="'+_s+'text-align:right;padding:2px 0 4px;">WoW</span>'
    +_mk3SH('BK%','bk',true)
    +'<span style="'+_s+'text-align:right;padding:2px 0 4px;">WoW</span>'
    +'</div>';

  function wPill(v) {
    if (!v || v === '—') return '<span style="color:var(--ink-muted);font-size:10px;text-align:right;">—</span>';
    var up = v.charAt(0) === '▲' || v.charAt(0) === '+';
    var lbl = v.replace(/pp$/,'').trim();
    return '<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+(up?'#EAF3DE':'#FCE8E6')+';color:'+(up?'#2F6C34':'#C0392B')+';white-space:nowrap;display:block;text-align:right;">'+lbl+'</em>';
  }

  var html = hdr;
  filteredWithPos.forEach(function(item, i) {
    var r = item.r;
    var cls = i >= _KPI_EXPAND_N ? 'sb-hidden' : i >= _KPI_TOP_N ? 'rows-more' : '';
    var disp = (i >= _KPI_TOP_N) ? 'display:none;' : '';
    var _bkNum = parseFloat(String(r.val||'0').replace('%','').replace(',','.')) || 0;
    var _bkWow = parseFloat(String(r.wow||'0').replace(/[^0-9.,+-]/g,'').replace(',','.')) || 0;
    var _bkPrev = _bkNum - _bkWow;
    html += '<div class="'+cls+'" data-lbl="'+r.lab+'" data-hist-w21="'+_bkNum+'" data-hist-w20="'+_bkPrev+'" data-hist-label="'+r.lab+'" data-hist-card="3" style="display:grid;grid-template-columns:'+grid+';align-items:center;gap:6px;width:100%;padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;'+disp+'">'
      +'<div style="min-width:0;overflow:hidden;"><span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">'
        +(String(item.origPos).padStart(2,'0'))+'. '+r.lab
      +'</span></div>'
      +'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;">'+r.books+'</span>'
      +wPill((typeof _BK_TRX_WOW !== 'undefined' && _BK_TRX_WOW[_ar3_view === 'dest' ? 'destino' : _ar3_view] && _BK_TRX_WOW[_ar3_view === 'dest' ? 'destino' : _ar3_view][r.lab] !== undefined) ? (parseFloat(_BK_TRX_WOW[_ar3_view === 'dest' ? 'destino' : _ar3_view][r.lab]) >= 0 ? '▲' : '▼') + Math.abs(parseFloat(_BK_TRX_WOW[_ar3_view === 'dest' ? 'destino' : _ar3_view][r.lab])).toFixed(1).replace('.',',') + '%' : '—')
      +'<span style="text-align:right;font-size:11px;font-weight:700;color:#333132;font-variant-numeric:tabular-nums;">'+r.val+'</span>'
      +wPill(r.wow||'—')
      +'</div>';
  });

  tbody.innerHTML = html;

  /* Ver más — activar botón estático ar3-th-more igual que ar1/ar2 */
  var _ar3MoreWrap = document.getElementById('ar3-more-wrap');
  if (_ar3MoreWrap) {
    _moreBtn(_ar3MoreWrap, 'ar3-tbody');
  }

  // Searchbox AR3
  var sb = document.getElementById('ar3-sb');
  if (sb && !sb._connected) {
    sb._connected = true;
    var clr3 = document.getElementById('ar3-sb-clear');
    sb.oninput = function() {
      var q = sb.value.toLowerCase();
      tbody.querySelectorAll('[data-lbl]').forEach(function(row){
        var lbl   = (row.getAttribute('data-lbl')||'').toLowerCase();
        var match = lbl.indexOf(q) >= 0;
        if (!q) {
          /* Sin filtro: mostrar top-5, ocultar rows-more y sb-hidden */
          row.style.display = (row.classList.contains('rows-more') || row.classList.contains('sb-hidden')) ? 'none' : 'grid';
        } else {
          row.style.display = match ? 'grid' : 'none';
        }
      });
      if (clr3) clr3.style.display = q ? 'inline' : 'none';
    };
    if (clr3) {
      clr3.onclick = function() { sb.value = ''; sb.oninput(); };
    }
  }
}


function _ar3_renderChan() {
  if (typeof BK_DATA === 'undefined' || !BK_DATA) return;
  var provs = BK_DATA.prov || [];
  var PROPIO = ['SynXis','HBSI','DerbySoft','Internal','Siteminder','Travelclick','Omnibees'];
  var THIRD  = ['Expedia','HotelBeds','Hotel Unico','Travelgate','HotelBeds Apitude','Hotel Unico V2'];
  var pp = provs.filter(function(r){ return PROPIO.indexOf(r.lab) >= 0; });
  var tp = provs.filter(function(r){ return THIRD.indexOf(r.lab) >= 0; });

  var acc  = '#333132', cyan = '#4FC3F4';
  var grid = 'minmax(0,1fr) 56px 72px 48px';
  var _s   = 'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);';

  function mkHdr(lbl) {
    return '<div style="display:grid;grid-template-columns:'+grid+';align-items:center;gap:6px;padding:4px 0;border-bottom:2px solid '+lbl+';margin-bottom:2px;">'
      +'<span style="'+_s+'">Channel</span>'
      +'<span style="'+_s+'text-align:right;">TRX</span>'
      +'<span style="'+_s+'text-align:right;color:'+lbl+';">BK%</span>'
      +'<span style="'+_s+'text-align:right;">WoW</span>'
      +'</div>';
  }

  function mkRow(r) {
    var up = parseFloat(r.wow||'0') >= 0;
    var wpill = '<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+(up?'#EAF3DE':'#FCE8E6')+';color:'+(up?'#2F6C34':'#C0392B')+';white-space:nowrap;display:block;text-align:right;">'+(up?'▲':'▼')+Math.abs(parseFloat(r.wow||0)).toFixed(2)+'</em>';
    return '<div style="display:grid;grid-template-columns:'+grid+';align-items:center;gap:6px;padding:6px 0;border-bottom:1px solid var(--rule-soft);">'
      +'<span style="font-size:11px;font-weight:600;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+r.lab+'</span>'
      +'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);">'+r.books+'</span>'
      +'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);">'+r.val+'</span>'
      +wpill
      +'</div>';
  }

  var html = '<div style="display:flex;flex-direction:column;gap:14px;padding:8px 0;width:100%;">'
    +'<div><div style="font-size:9px;font-weight:700;color:'+acc+';letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>'+mkHdr(acc)+pp.map(mkRow).join('')+'</div>'
    +'<div><div style="font-size:9px;font-weight:700;color:'+cyan+';letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>'+mkHdr(cyan)+tp.map(mkRow).join('')+'</div>'
    +'</div>';

  var container = document.getElementById('ar3-tbody');
  if (!container) return;
  container.innerHTML = html;
  var moreBtn = document.getElementById('ar3-more-btn');
  if (moreBtn) moreBtn.style.display = 'none';
}

function ar3_setView(view) {
  /* Resetear sort al cambiar dimensión */
  _ar3SortState = {col:null, dir:'orig', asc:true};
  _ar3_view = view;
  ['prov','dest','corp','hotel'].forEach(function(v) {
    var btn = document.getElementById('ar3-vbk-' + v);
    if (!btn) return;
    var active = (v === view);
    btn.style.background  = active ? '#EDE8F7' : 'transparent';
    btn.style.color       = active ? '#5C469C' : 'var(--ink-muted)';
    btn.style.borderColor = active ? '#5C469C' : 'var(--rule)';
  });
  /* Mostrar fila de htab (Críticos/Bajo Rend/Sin Conv) solo en vista hotel */
  var htabRow = document.getElementById('ar3-htab-row');
  if (htabRow) htabRow.style.display = (view === 'hotel') ? '' : 'none';
  ar3_renderTable(_ar3_view, _ar3_htab, _ar3SortState);
}

function ar3_setHotelTab(htab) {
  /* Resetear sort al cambiar filtro de banda */
  _ar3SortState = {col:null, dir:'orig', asc:true};
  _ar3_htab = htab;
  ['crit','br','sc'].forEach(function(t) {
    var btn = document.getElementById('ar3-htab-' + t);
    if (!btn) return;
    var active = (t === htab);
    btn.style.background  = active ? '#E8E6E3' : 'transparent';
    btn.style.color       = active ? '#333132' : 'var(--ink-muted)';
    btn.style.borderColor = active ? '#8A8377' : 'var(--rule)';
  });
  ar3_renderTable(_ar3_view, _ar3_htab, _ar3SortState);
}

function ar3_showMore() {
  var hidden = document.querySelectorAll('#ar3-tbody tr.ar3-more');
  hidden.forEach(function(tr){ tr.style.display = 'table-row'; });
  var btn = document.getElementById('ar3-more-btn');
  if (btn) btn.style.display = 'none';
}

/* Inicializar card BK cuando el DOM esté listo */
(function tryInitBK() {
  if (typeof BK_DATA === 'undefined' || !BK_DATA) {
    setTimeout(tryInitBK, 100); return;
  }
  var d = BK_DATA.global;
  var k3 = document.getElementById('ar-kpi-3');
  if (!k3) { setTimeout(tryInitBK, 100); return; }

  k3.textContent = d.bk;

  /* Vol compacto (mismo formato que cards 1/2) */
  var v3 = document.getElementById('ar3-vol');
  if (v3) {
    var bk_compact = d.books >= 1000000 ? (d.books/1000000).toFixed(1).replace('.',',')+'M'
                   : d.books >= 1000 ? (d.books/1000).toFixed(1).replace('.',',')+'K'
                   : String(d.books);
    v3.textContent = bk_compact;
  }
  /* Trx con formato entero */
  var b3 = document.getElementById('ar3-books');
  if (b3) b3.textContent = String(d.books).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  /* WoW de books en pill */
  var bw3 = document.getElementById('ar3-books-wow');
  if (bw3 && d.bk_wow !== undefined) {
    var isUp = d.bk_wow >= 0;
    bw3.innerHTML = '<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:'+(isUp?'#EAF3DE':'#FCE8E6')+';color:'+(isUp?'#2F6C34':'#C0392B')+';white-space:nowrap;">'+(isUp?'▲':'▼')+Math.abs(d.bk_wow*100).toFixed(1).replace('.',',')+'%</em>';
  }

  var bc = ar3_bandColors(d.banda);
  var badge3 = document.getElementById('ar3-badge');
  if (badge3) {
    badge3.textContent = ar3_bandLabel(d.banda);
    badge3.style.background = bc[0]; badge3.style.color = bc[1];
    badge3.style.border = '1px solid ' + bc[1] + '44';
  }
  /* Badge BK en barra de KPIs — usar banda directa de BK_DATA.global */
  var _bkBandEl = document.getElementById('w22-strip-bk-band');
  if (_bkBandEl) {
    _bkBandEl.textContent = ar3_bandLabel(d.banda);
    _bkBandEl.style.background = bc[0];
    _bkBandEl.style.color = bc[1];
    _bkBandEl.style.outline = '1px solid ' + bc[1] + '55';
  }

  /* Mismo gauge que cards 1/2: 5 niveles, todos opacity:1 */
  var GAUGE_BK = ['#8A8377','#C0392B','#F97316','#FCD34D','#1A6B4A'];
  var g3 = document.getElementById('ar3-gauge');
  if (g3) {
    g3.innerHTML = GAUGE_BK.map(function(c){
      return '<div style="flex:1;background:'+c+';height:6px;opacity:1;"></div>';
    }).join('');
  }

  var wp3 = document.getElementById('ar3-wow-pill');
  if (wp3) {
    var isUp = d.bk_wow >= 0;
    wp3.innerHTML = '<em class="wow-pill '+(isUp?'up':'dn')+'" style="margin-left:0;">'+(isUp?'&uarr;':'&darr;')+' '+Math.abs(d.bk_wow).toFixed(2).replace('.',',')+'</em>';
  }

  var wb3 = document.getElementById('ar3-wowbox');
  if (wb3) {
    var isUp = d.bk_wow >= 0;
    var wowFmt = (isUp ? '+' : '') + d.bk_wow.toFixed(2).replace('.',',');
    wb3.innerHTML =
      '<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;"><div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W22</div><div style="font-size:15px;font-weight:700;margin-top:2px;color:var(--ink-soft);">'+d.bk_prev+'</div></div>'+
      '<div style="flex:1;text-align:center;background:var(--paper);padding:5px 4px;border-radius:2px;"><div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W23</div><div style="font-size:15px;font-weight:700;margin-top:2px;color:#333132;">'+d.bk+'</div></div>'+
      '<div style="flex:1;text-align:center;background:'+(isUp?'#E0F0E2':'#FCE4F1')+';padding:5px 4px;border-radius:2px;"><div style="font-size:8px;letter-spacing:.08em;text-transform:uppercase;color:'+(isUp?'#2F6C34':'#99162B')+';font-weight:700;">WoW</div><div style="font-size:15px;font-weight:700;margin-top:2px;color:'+(isUp?'#2F6C34':'#99162B')+';">'+wowFmt+'</div></div>';
  }

  var stripBK = document.getElementById('w22-strip-bk'); if (stripBK) stripBK.textContent = d.bk;
  var arStripBK = document.getElementById('ar-strip-bk'); if (arStripBK) arStripBK.textContent = d.bk;

  /* W23+: actualizar badges de severidad individuales para cada métrica */
  function _updateBandBadge(badgeId, val, metric) {
    var el = document.getElementById(badgeId);
    if (!el) return;
    /* getBanda devuelve banda según métrica */
    var banda = _getBandaForMetric(val, metric);
    var colors = {
      'Exitosa': {bg:'#E1F5EE', fg:'#1A6B4A'},
      'Aceptable': {bg:'#FEF9C3', fg:'#7B6F00'},
      'Revisar': {bg:'#FED7AA', fg:'#C2410C'},
      'Crítica': {bg:'#FCCDD9', fg:'#99162B'},
      'Súper Crítica': {bg:'#FFCCCC', fg:'#D32F2F'},
      'Sin Conversión': {bg:'#F5F5F5', fg:'#666'},
    };
    var c = colors[banda] || {bg:'#F5F5F5', fg:'#666'};
    el.textContent = banda;
    el.style.background = c.bg;
    el.style.color = c.fg;
  }

  function _getBandaForMetric(val, metric) {
    var pct = val / 100;
    if (metric === 'eficacia' || metric === 'bookability') {
      if (pct >= 0.97) return 'Exitosa';
      if (pct >= 0.93) return 'Aceptable';
      if (pct >= 0.85) return 'Revisar';
      if (pct >= 0.60) return 'Crítica';
      return 'Súper Crítica';
    }
    if (metric === 'convrate') {
      if (pct === 0) return 'Sin Conversión';
      if (pct < 0.008) return 'Crítica';
      if (pct < 0.015) return 'Revisar';
      if (pct <= 0.025) return 'Aceptable';
      return 'Exitosa';
    }
    if (metric === 'nodispo') {
      pct = val / 100;
      if (pct < 0.03) return 'Exitosa';
      if (pct <= 0.05) return 'Aceptable';
      if (pct <= 0.20) return 'Revisar';
      if (pct <= 0.60) return 'Crítica';
      return 'Súper Crítica';
    }
    return 'Aceptable';
  }

  /* Actualizar badges individuales.
     d = BK_DATA[canasta] (no tiene .ef/.cv) → usar CR_CV para EF/CV.
     Los valores en CR_CV son strings ('94,53%') — parsear a float para la banda. */
  function _parseKpiPct(s) {
    if (typeof s === 'number') return s;
    if (!s) return NaN;
    /* '94,53%' → 94.53 */
    return parseFloat(String(s).replace('%','').replace(',','.'));
  }
  var _crCv = (typeof CR_CV !== 'undefined' && CR_CV[W.canasta]) ? CR_CV[W.canasta] : {};
  var _bkCanasta = (typeof BK_DATA !== 'undefined' && BK_DATA[W.canasta]) ? BK_DATA[W.canasta] : d;
  _updateBandBadge('w22-strip-ef-band', _parseKpiPct(_crCv.ef), 'eficacia');
  _updateBandBadge('w22-strip-cv-band', _parseKpiPct(_crCv.cv), 'convrate');
  _updateBandBadge('w22-strip-bk-band', _parseKpiPct(_bkCanasta.bk), 'bookability');
  _updateBandBadge('ar-strip-ef-band', _parseKpiPct(_crCv.ef), 'eficacia');
  _updateBandBadge('ar-strip-cv-band', _parseKpiPct(_crCv.cv), 'convrate');
  _updateBandBadge('ar-strip-bk-band', _parseKpiPct(_bkCanasta.bk), 'bookability');

  ar3_renderTable('hotel', 'crit');
  /* Ocultar tab Sin Conv en BK — la banda sinconv no existe en BK_DATA */
  var _scTab = document.getElementById('ar3-htab-sc');
  if (_scTab) _scTab.style.display = 'none';
  
  /* W23+: Tabs BK — JS driven (los radios están dentro de kpi-card, no son hermanos de .tab-panels) */
  (function() {
    var BK_TABS = ['destino', 'corp', 'hotel', 'channel'];
    /* Encontrar la kpi-card de BK — la que contiene tab-bk-destino */
    var bkCard = document.getElementById('kpicard-bk');
    if (!bkCard) {
      var r0 = document.getElementById('tab-bk-destino');
      if (r0) bkCard = r0.closest('.kpi-card');
    }
    if (!bkCard) return;

    var panels = bkCard.querySelector('#kpi-bk-panels');
    if (!panels) return;

    function _activateBKTab(tabKey) {
      /* Mostrar/ocultar panels */
      BK_TABS.forEach(function(t) {
        var p = panels.querySelector('[data-tab="' + t + '"]');
        if (p) p.style.display = (t === tabKey) ? '' : 'none';
      });
      /* Actualizar estilo de TODOS los labels tab-bk-* en la card */
      BK_TABS.forEach(function(t) {
        var lbls = bkCard.querySelectorAll('label[for="tab-bk-' + t + '"]');
        lbls.forEach(function(lbl) {
          var isActive = (t === tabKey);
          lbl.style.color = isActive ? 'var(--accent)' : '';
          lbl.style.borderBottom = isActive ? '2px solid var(--accent)' : '';
          lbl.style.fontWeight = isActive ? '700' : '';
        });
      });
      /* Marcar radio para compatibilidad con CSS */
      var radio = document.getElementById('tab-bk-' + tabKey);
      if (radio) radio.checked = true;
    }

    /* Attach click en TODOS los labels con for=tab-bk-* (sin importar en qué tabs-row están) */
    BK_TABS.forEach(function(tabKey) {
      var lbls = bkCard.querySelectorAll('label[for="tab-bk-' + tabKey + '"]');
      lbls.forEach(function(lbl) {
        lbl.style.cursor = 'pointer';
        lbl.addEventListener('click', function(e) {
          e.preventDefault();
          _activateBKTab(tabKey);
        });
      });
    });

    /* Estado inicial: mostrar solo destino */
    _activateBKTab('destino');

    /* Event delegation robusto para sort BK — captura clicks en headers [data-sort-key]
       aunque el onclick inline falle por cualquier razón */
    bkCard.addEventListener('click', function(e) {
      var sp = e.target.closest('[data-sort-key]');
      if (!sp) return;
      if (!bkCard.contains(sp)) return;
      /* Llamar bkSort si existe (la función global de assemble_unified) */
      if (typeof window.bkSort === 'function') {
        window.bkSort(sp);
      }
    });
  })();
})();
