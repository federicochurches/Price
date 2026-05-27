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
  var dd = data();
  var rows = tab === 'br' ? (dd.hotels_br || dd.hotels) :
             tab === 'sc' ? (dd.hotels_sc || dd.hotels) :
             tab === 'cv' ? (dd.hotels_cv || dd.hotels) :
             (dd.hotels_crit || dd.hotels);
  w22_renderTable('w22-th', 'w22-th-more', rows, false);
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
      return '<div style="display:flex;align-items:center;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--rule-soft);gap:6px;">'
        +'<span style="font-size:11px;font-weight:600;color:var(--ink);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+nombre+'</span>'
        +'<span>'+badge+'</span>'
        +'<span style="font-size:11px;font-weight:700;color:var(--ink);white-space:nowrap;font-variant-numeric:tabular-nums;">'+_fmtPct(val_pct)+'</span>'
        +'<span>'+mw+'</span>'
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
