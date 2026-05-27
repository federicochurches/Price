
var W={mode:'cr',canasta:'global',view:'hotel',dim:'corp',reOpen:false};
/* CR_CV, RND_CV, CR_D, RND_D, CR_AL, RND_AL, CR_HOTELS se inyectan desde part2_cr/part2_rnd */

function g(id){return document.getElementById(id);}
function cv(){return W.mode==='cr'?CR_CV[W.canasta]:RND_CV[W.canasta];}
function data(){return W.mode==='cr'?CR_D[W.canasta]:RND_D[W.canasta];}
function al(){return W.mode==='cr'?CR_AL[W.canasta]:RND_AL[W.canasta];}

/* trow — genera HTML de fila para Análisis de Rendimiento
   CR  (11 elem): [nombre, bbg, bfg, banda, CR, ef, cv, wow_up, wow_ef_str, wow_cv_str, wow_cr_str]
   RND (11 elem): [nombre, bbg, bfg, banda, tráfico, %nd, ipm, wow_up, wow_nd_str, wow_ipm_str, '—']
   Layout 8 cols: Nombre | Banda | Tráfico | WoW↕ | Métrica1 | WoW↕ | Métrica2 | WoW↕
*/
function trow(r){
 var nameCell='<td style="padding:8px 0 8px 12px;font-size:12px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="'+r[0]+'">'+r[0]+'</td>';
 var badgeCell='<td style="padding:8px 6px;text-align:left;white-space:nowrap;"><span class="sev-badge" style="background:'+r[1]+';color:'+r[2]+';font-size:7px;font-weight:700;padding:2px 5px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);white-space:nowrap;">'+r[3]+'</span></td>';
 var tdR=function(v){return '<td style="padding:8px 6px;text-align:right;font-size:12px;font-weight:600;color:var(--ink);white-space:nowrap;">'+v+'</td>';};
 
 /* Genera pill WoW con color verde/rojo según dirección y si mejora = positivo o negativo */
 function wowPill(str, isGood){
  if(!str||str==='—') return '<td style="padding:8px 6px;text-align:right;"><span style="color:var(--ink-muted);font-size:10px;">—</span></td>';
  var up = str.charAt(0)==='▲'||str.charAt(0)==='+';
  var good = isGood ? up : !up;  /* isGood=true: ▲ = bueno; isGood=false: ▲ = malo (NoDispo) */
  var bg = good?'#EAF3DE':'#FCE8E6';
  var fg = good?'#2F6C34':'#C0392B';
  /* Limpiar label: quitar 'pp' de WoW Eficacia/ConvRate/NoDispo */
  var label = str.replace(/pp$/,'').replace(/,00$/,'').trim();
  return '<td style="padding:8px 6px;text-align:right;"><em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 5px;border-radius:3px;background:'+bg+';color:'+fg+';white-space:nowrap;">'+label+'</em></td>';
 }
 
 if(W.mode==='rnd'){
  /* RND: [0]nombre [1]bbg [2]bfg [3]banda [4]tráfico [5]%nd [6]ipm [7]wow_up [8]wow_nd [9]wow_ipm [10]'—' */
  return '<tr style="border-bottom:1px solid var(--rule-soft);">'
   +nameCell+badgeCell
   +tdR(r[4])
   +wowPill(r[10]||'—', true)   /* WoW Tráfico — ▲ = bueno */
   +tdR(r[5])
   +wowPill(r[8]||'—', false)   /* WoW NoDispo — ▲ = malo */
   +tdR(r[6])
   +wowPill(r[9]||'—', true)    /* WoW IPM — ▲ = bueno */
   +'</tr>';
 }
 
 /* CR: [0]nombre [1]bbg [2]bfg [3]banda [4]CR [5]ef [6]cv [7]wow_up [8]wow_ef [9]wow_cv [10]wow_cr */
 return '<tr style="border-bottom:1px solid var(--rule-soft);">'
  +nameCell+badgeCell
  +tdR(r[4])
  +wowPill(r[10]||'—', true)   /* WoW Tráfico — ▲ = bueno */
  +tdR(r[5])
  +wowPill(r[8]||'—', true)    /* WoW Eficacia — ▲ = bueno */
  +tdR(r[6])
  +wowPill(r[9]||'—', true)    /* WoW Conv Rate — ▲ = bueno */
  +'</tr>';
}

/* Actualizar headers de tabla según modo */
function w22_updateTableHeaders(){
 var modeCR = W.mode === 'cr';
 var hh = modeCR
  ? ['Hotel','Severity','Tráfico','WoW↕','Eficacia','WoW↕','Conv Rate','WoW↕']
  : ['Hotel','Severity','Tráfico','WoW↕','%NoDispo','WoW↕','IPM','WoW↕'];
 var dh = modeCR
  ? ['Dimensión','Severity','Tráfico','WoW↕','Eficacia','WoW↕','Conv Rate','WoW↕']
  : ['Dimensión','Severity','Tráfico','WoW↕','%NoDispo','WoW↕','IPM','WoW↕'];

 [['#w22-ph thead tr', hh], ['#w22-pd thead tr', dh]].forEach(function(pair){
  var tr = document.querySelector(pair[0]);
  if(!tr) return;
  var cells = tr.querySelectorAll('th');
  pair[1].forEach(function(lbl,i){
   if(!cells[i]) return;
   cells[i].style.display='';
   cells[i].textContent = lbl;
   /* WoW cols: right-align, smaller */
   if(lbl==='WoW↕'){
    cells[i].style.textAlign='right';
    cells[i].style.fontSize='9px';
    cells[i].style.color='var(--ink-muted)';
   }
  });
 });
 
 /* Actualizar label "Canal" → "Channel" en tab de dimensiones */
 var chanLabel = document.querySelector('#w22-pd .tabs-row label:last-child, #w22-pd label[onclick*="chan"]');
 if(chanLabel && chanLabel.textContent.trim()==='Por Canal'){
  chanLabel.textContent = 'Por Channel';
 }
 /* Colgroup: todas las cols visibles */
 document.querySelectorAll('#w22-ph colgroup col:last-child, #w22-pd colgroup col:last-child').forEach(function(col){
  col.style.display='';
 });
}

function w22_renderTable(tbodyId, btnId, rows, open){
 var tbody=g(tbodyId);if(!tbody)return;
 tbody.innerHTML=rows.slice(0,10).map(function(r){
  return trow(r);
 }).join('');
 var btn=g(btnId);
 if(btn) btn.style.display='none';
}
function w22_renderRE(open){
 W.reOpen=open;
 var d=data(), col=cv().col;
 var el=g('w22-re-list');if(!el)return;
 el.innerHTML=d.re.map(function(r,i){
  var h=(i>=5&&!W.reOpen)?' style="display:none;"':'';
  return '<li'+h+' style="position:relative;padding:16px 0 16px 80px;border-bottom:1px solid var(--rule);font-size:15px;line-height:1.55;">'
   +'<span style="font-size:12px;color:var(--ink-muted);font-weight:500;position:absolute;left:0;top:20px;">'+(i<9?'0'+(i+1):i+1)+'</span>'
   +'<strong style="display:block;font-size:22px;font-weight:700;color:'+col+';letter-spacing:-.02em;margin-bottom:4px;">'+r.n+'</strong>'
   +'<span style="font-weight:600;color:var(--ink);">'+r.t+'</span> '
   +'<span style="color:var(--ink-muted);font-size:14px;">'+r.d+'</span></li>';
 }).join('');
 var btn=g('w22-re-btn');if(btn)btn.textContent=W.reOpen?'Ver menos ↑':'Ver 5 más ↓';
}
function w22_toggleRE(){w22_renderRE(!W.reOpen);}

function w22_renderAlertas(){
 var rows=al()||[];
 if(!Array.isArray(rows))rows=[];
 var el=g('w22-alertas');if(!el)return;
 var ef_lbl=W.mode==='cr'?'Peor Eficacia':'Mayor NoDispo';
 var cv_lbl=W.mode==='cr'?'Peor ConvRate':'Menor IPM';
 el.innerHTML=rows.map(function(r){
  return '<div style="border:1px solid var(--rule);padding:14px;background:var(--paper);">'
   +'<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--accent);margin-bottom:12px;">'+r[0]+' '+r[1]+'</div>'
   +'<div style="background:var(--paper-soft);border:1px solid var(--rule);padding:10px 12px;margin-bottom:8px;border-left:3px solid #EA0074;">'
   +'<div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);margin-bottom:3px;">'+ef_lbl+'</div>'
   +'<div style="font-size:11px;font-weight:600;color:var(--ink);">'+r[2]+'</div>'
   +'<div style="font-size:13px;font-weight:700;color:#EA0074;margin-top:2px;">'+r[3]+'</div></div>'
   +'<div style="background:var(--paper-soft);border:1px solid var(--rule);padding:10px 12px;border-left:3px solid var(--accent);">'
   +'<div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);margin-bottom:3px;">'+cv_lbl+'</div>'
   +'<div style="font-size:11px;font-weight:600;color:var(--ink);">'+r[4]+'</div>'
   +'<div style="font-size:13px;font-weight:700;color:var(--accent);margin-top:2px;">'+r[5]+'</div></div></div>';
 }).join('');
}

function w22_update(){
 var c=cv(), col=c.col, d=data();

 /* Strip */
 var s1=g('w22-strip-ef');if(s1){s1.textContent=c.ef;s1.style.color=col;}
 var s2=g('w22-strip-cv');if(s2){s2.textContent=c.cv;s2.style.color=col;}
 var sb=g('w22-strip-band');if(sb){sb.style.background=c.bbg;sb.style.color=c.bfg;sb.textContent=c.band;}
 /* Labels del strip según modo */
 var l1=g('w22-strip-lbl1'),l2=g('w22-strip-lbl2');
 if(W.mode==='cr'){if(l1)l1.textContent='Eficacia';if(l2)l2.textContent='Conv Rate';}
 else{if(l1)l1.textContent='NoDispo';if(l2)l2.textContent='IPM';}

 /* KPI cards W21 */
 var kef=g('w21-kv-ef');if(kef){kef.textContent=c.ef;kef.style.color=col;}
 var kcv=g('w21-kv-cv');if(kcv){kcv.textContent=c.cv;kcv.style.color=col;}
 var hef=g('w21-hist-ef');if(hef)hef.style.color=col;
 var hcv=g('w21-hist-cv');if(hcv)hcv.style.color=col;

 /* Chips */
 document.querySelectorAll('.c-chip').forEach(function(el){
  var a=el.classList.contains('active');
  el.style.borderBottomColor=a?col:'transparent';
  el.style.color=a?col:'';el.style.background=a?'var(--paper)':'';
 });

 /* Tablas — usar hotels_crit (CR) o hotels_dnc (RND) como tab inicial */
 var hotel_rows = W.mode==='rnd'
   ? (d.hotels_dnc || d.hotels || [])
   : (d.hotels_crit || d.hotels || []);
 w22_renderTable('w22-th','w22-th-more',hotel_rows,false);
 /* Renderizar dimensión activa (por defecto corp) */
 var dim_key = W.dim || 'corp';
 var dim_data = d[dim_key+'s'] || d.dims || [];
 w22_renderTable('w22-td','w22-td-more',dim_data,false);
 
 /* Sincronizar barra local de Análisis de Rendimiento */
 (function(){
  var accent_col = col;
  /* Switcher local AR — color fijo del modo, no de la canasta */
  var modeCol = W.mode==='cr' ? '#5C469C' : '#EA0074';
  var arSeg = g('ar-seg');
  if(arSeg) arSeg.style.border = '1.5px solid ' + modeCol;
  ['ar-btn-cr','ar-btn-rnd'].forEach(function(id){
   var btn = g(id); if(!btn) return;
   var isCurrent = (id === 'ar-btn-'+W.mode);
   btn.classList.toggle('on', isCurrent);
   btn.style.background = isCurrent ? modeCol : '';
   btn.style.color = isCurrent ? '#fff' : '';
   if(id==='ar-btn-cr') btn.style.borderRight = '1.5px solid ' + modeCol;
  });
  /* Chips canasta AR — misma lógica que el loop de .c-chip */
  ['global','b2c','op','cug'].forEach(function(c){
   var chip = g('ar-chip-'+c); if(!chip) return;
   var isCurrent = c === (W.canasta||'global');
   chip.classList.toggle('active', isCurrent);
   chip.style.borderBottomColor = isCurrent ? accent_col : 'transparent';
   chip.style.color = isCurrent ? accent_col : '';
   chip.style.background = isCurrent ? 'var(--paper)' : '';
  });
  /* KPIs inline de la barra AR — mismos valores que la barra principal */
  var lbl1 = g('ar-strip-lbl1'), lbl2 = g('ar-strip-lbl2');
  var ef   = g('ar-strip-ef'),   cv   = g('ar-strip-cv');
  var band = g('ar-strip-band');
  var mainEf   = g('w22-strip-ef'),   mainCv  = g('w22-strip-cv');
  var mainBand = g('w22-strip-band'), mainL1  = g('w22-strip-lbl1'), mainL2 = g('w22-strip-lbl2');
  if(lbl1 && mainL1) lbl1.textContent = mainL1.textContent;
  if(lbl2 && mainL2) lbl2.textContent = mainL2.textContent;
  if(ef && mainEf){ ef.textContent = mainEf.textContent; ef.style.color = accent_col; }
  if(cv && mainCv){ cv.textContent = mainCv.textContent; cv.style.color = accent_col; }
  if(band && mainBand){
   band.textContent = mainBand.textContent;
   band.style.background = mainBand.style.background;
   band.style.color = mainBand.style.color;
  }
 })();

 /* Re-mostrar panels de Análisis según modo */
 var phCR  = g('w22-panel-hist-cr');
 var phRND = g('w22-panel-hist-rnd');
 var pdCR  = g('w22-panel-dim-hist-cr');
 var pdRND = g('w22-panel-dim-hist-rnd');
 var isCR  = W.mode === 'cr';
 if(phCR)  { phCR.style.display  = isCR ? 'grid' : 'none'; }
 if(phRND) { phRND.style.display = isCR ? 'none' : 'grid'; }
 if(pdCR)  { pdCR.style.display  = isCR ? 'grid' : 'none'; }
 if(pdRND) { pdRND.style.display = isCR ? 'none' : 'grid'; }

 /* Actualizar headers de tabla según modo */
 w22_updateTableHeaders();
 
 /* Re-renderizar cards KPI CR con datos de la canasta activa */
 if(W.mode === 'cr' && typeof w22_renderCardTabs === 'function') {
   w22_renderCardTabs(W.canasta || 'global');
 }

 /* RE + Alertas + Plan */
 w22_renderRE(false);
 w22_renderAlertas();

 var pg=g('w22-pg');
 if(pg)pg.innerHTML=d.plan.map(function(p){
  var bc=p.c==='qw'?'#2F6C34':p.c==='mp'?'#A86A1D':'var(--accent)';
  var bgc=p.c==='qw'?'#E0F0E2':p.c==='mp'?'#FFF4E0':'var(--accent-soft)';
  return '<div style="background:var(--paper);border:1px solid var(--rule);border-left:3px solid '+bc+';padding:10px 14px;border-radius:3px;">'
   +'<div style="display:inline-block;font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:'+bc+';background:'+bgc+';padding:3px 8px;border-radius:2px;margin-bottom:6px;">'+p.o+'</div>'
   +'<div style="font-size:12px;line-height:1.4;color:var(--ink-soft);">'+p.a+'</div>'
   +'<div style="display:flex;gap:10px;margin-top:7px;font-size:10px;color:var(--ink-muted);">'
   +'<span style="font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-soft);background:var(--paper-soft);padding:2px 7px;border-radius:2px;font-size:9px;">'+p.t+'</span>'
   +'<span><strong style="font-size:8px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-soft);margin-right:3px;">Plazo</strong>'+p.p+'</span></div></div>';
 }).join('');

 var co=g('w22-co');
 if(co)co.innerHTML=d.co.map(function(c,i){
  return '<div style="font-size:12px;color:var(--ink-soft);padding:6px 0;border-bottom:1px solid var(--rule-soft);display:flex;gap:10px;">'
   +'<span style="font-size:10px;font-weight:700;color:var(--ink-muted);min-width:18px;">'+(i+1)+'.</span><span>'+c+'</span></div>';
 }).join('');

 /* Canvas */
 w22_redrawCanvas(col);
 w22_recolorSparks(col);
 /* Re-aplicar con delay para que los IIFE del módulo histórico estén listos */
 setTimeout(function(){ w22_recolorSparks(cv().col); }, 200);
}

function w22_setMode(m, el){
 W.mode=m; W.canasta='global'; W.reOpen=false;
 /* Segmented control — colores dinámicos según modo */
 var modeCol=m==='cr'?'#5C469C':'#EA0074';
 var seg=document.querySelector('.w22-seg');
 if(seg){seg.style.border='1.5px solid '+modeCol;seg.style.borderRadius='4px';}
 var btns=document.querySelectorAll('.w22-seg-btn');
 btns.forEach(function(c,i){
  c.classList.remove('on');
  c.style.background='';c.style.color='';
  if(i===0)c.style.borderRight='1.5px solid '+modeCol;
 });
 el.classList.add('on');
 el.style.background=modeCol;el.style.color='#fff';
 /* Masthead report-tag */
 var tag=document.getElementById('w22-report-tag');
 if(tag){tag.textContent=m==='cr'?'CheckRates':'RatesNoDispo';tag.style.background=modeCol;}
 /* Mostrar/ocultar bloques KPI */
 var cr_block=g('kpis-hero-section');
 var rnd_block=g('w22-rnd-block');
 if(cr_block)cr_block.style.display=m==='cr'?'':'none';
 if(rnd_block)rnd_block.style.display=m==='rnd'?'':'none';
 /* Reset canasta chips */
 document.querySelectorAll('.c-chip').forEach(function(x){
  x.classList.remove('active');x.style.borderBottomColor='transparent';x.style.color='';x.style.background='';
 });
 var gc=g('chip-global');if(gc)gc.classList.add('active');
 w22_update();
 /* Reiniciar tabs y disparar evento para TAB_BINDING */
 if(typeof window._reinitTabs==='function') setTimeout(window._reinitTabs, 80);
 document.dispatchEvent(new CustomEvent('mode-changed', {detail:{mode:m}}));
}

function w22_setC(c,el){
 W.canasta=c; W.reOpen=false;
 document.querySelectorAll('.c-chip').forEach(function(x){
  x.classList.remove('active');x.style.borderBottomColor='transparent';x.style.color='';x.style.background='';
 });
 el.classList.add('active');
 w22_update();
 if(typeof window._reinitTabs==='function') setTimeout(window._reinitTabs, 80);
}
function w22_setView(v){
 W.view=v;
 var ph=g('w22-ph'),pd=g('w22-pd'),vh=g('vch-h'),vd=g('vch-d');
 if(ph)ph.style.display=v==='hotel'?'block':'none';
 if(pd)pd.style.display=v==='dim'?'block':'none';
 if(vh){vh.classList.toggle('on',v==='hotel');vh.style.background=v==='hotel'?'var(--paper)':'';vh.style.color=v==='hotel'?'var(--ink)':'var(--ink-muted)';}
 if(vd){vd.classList.toggle('on',v==='dim');vd.style.background=v==='dim'?'var(--paper)':'';vd.style.color=v==='dim'?'var(--ink)':'var(--ink-muted)';}
}
function w22_setDim(d){
 W.dim = d;
 var l={corp:'Corporativo',dest:'Destino',chan:'Channel'};
 var th=g('w22-th-dim');if(th)th.textContent=l[d]||'Corporativo';
 w22_update();
}
function w22_iTab(el){
 var row=el.parentElement;
 row.querySelectorAll('label').forEach(function(t){
  t.classList.remove('active');
  t.style.background='';t.style.color='';t.style.border='';t.style.borderBottom='';t.style.marginBottom='';
 });
 el.classList.add('active');
 el.style.background='var(--paper)';el.style.color='var(--accent)';
 el.style.border='1px solid var(--rule)';el.style.borderBottom='1px solid var(--paper)';
 el.style.marginBottom='-1px';
}

/* Recolorear spark bars del histórico y todos los elementos de acento */
function w22_recolorSparks(accent){
 var accentRgb=RGB[accent]||'92,70,156';
 
 /* IDs de spark containers para las cards KPI + panel análisis */
 var sparkIds = W.mode==='cr'
   ? ['hist-hcr-global-ef-spark','hist-hcr-global-cv-spark',
      'hist-hcr-panel-ef-spark','hist-hcr-panel-cv-spark',
      'hist-hcr-dim-ef-spark','hist-hcr-dim-cv-spark']
   : ['hist-hrnd-global-nd-spark','hist-hrnd-global-ipm-spark',
      'hist-hrnd-panel-nd-spark','hist-hrnd-panel-ipm-spark',
      'hist-hrnd-dim-nd-spark','hist-hrnd-dim-ipm-spark'];
 
 sparkIds.forEach(function(sid){
  var el=g(sid);if(!el)return;
  var bars=el.querySelectorAll('div');
  var n=bars.length;
  bars.forEach(function(bar,i){
   var isLast=(i===n-1);
   if(isLast){bar.style.background=accent;}
   else{
    var h=parseInt(bar.style.height)||8;
    var alpha=Math.round((0.25+0.70*(h-4)/14)*100)/100;
    bar.style.background='rgba('+accentRgb+','+alpha+')';
   }
  });
 });
 
 /* Actualizar etiqueta "W21" (último label de semana) en módulo histórico */
 var semanaSpans = document.querySelectorAll('[id^="hist-hcr-global-"] + * span:last-child, [id^="hist-hrnd-global-"] + * span:last-child');
 
 /* Recolorear el valor "Actual" en los módulos históricos CR activos */
 var actualIds = W.mode==='cr'
   ? ['hist-hcr-global-ef-actual','hist-hcr-global-cv-actual',
      'hist-hcr-panel-ef-actual','hist-hcr-panel-cv-actual',
      'hist-hcr-dim-ef-actual','hist-hcr-dim-cv-actual']
   : ['hist-hrnd-global-nd-actual','hist-hrnd-global-ipm-actual',
      'hist-hrnd-panel-nd-actual','hist-hrnd-panel-ipm-actual',
      'hist-hrnd-dim-nd-actual','hist-hrnd-dim-ipm-actual'];
 actualIds.forEach(function(aid){
  var el=g(aid);if(el)el.style.color=accent;
 });
 
 /* Redibujar canvas del módulo histórico con el nuevo color de canasta */
 var canasta = W.canasta || 'global';
 if(W.mode==='cr' && typeof HIST_CR_BY_CANASTA !== 'undefined') {
  var efVals = HIST_CR_BY_CANASTA[canasta] && HIST_CR_BY_CANASTA[canasta].ef ? HIST_CR_BY_CANASTA[canasta].ef.vals : null;
  var cvVals = HIST_CR_BY_CANASTA[canasta] && HIST_CR_BY_CANASTA[canasta].cv ? HIST_CR_BY_CANASTA[canasta].cv.vals : null;
  var fnEf = window['histRedraw_hcr-global-ef'];
  var fnCv = window['histRedraw_hcr-global-cv'];
  if(typeof fnEf === 'function') setTimeout(function(){fnEf(accent, efVals);}, 20);
  if(typeof fnCv === 'function') setTimeout(function(){fnCv(accent, cvVals);}, 20);
  /* También canvas del panel y dimensión */
  var fnPanel = window['histRedraw_hcr-panel-ef'];
  var fnPanelCv = window['histRedraw_hcr-panel-cv'];
  var fnDim   = window['histRedraw_hcr-dim-ef'];
  var fnDimCv = window['histRedraw_hcr-dim-cv'];
  if(typeof fnPanel   === 'function') setTimeout(function(){fnPanel(accent, efVals);}, 30);
  if(typeof fnPanelCv === 'function') setTimeout(function(){fnPanelCv(accent, cvVals);}, 30);
  if(typeof fnDim     === 'function') setTimeout(function(){fnDim(accent, efVals);}, 30);
  if(typeof fnDimCv   === 'function') setTimeout(function(){fnDimCv(accent, cvVals);}, 30);
 } else if(W.mode==='rnd' && typeof HIST_RND_BY_CANASTA !== 'undefined') {
  var ndVals  = HIST_RND_BY_CANASTA[canasta] && HIST_RND_BY_CANASTA[canasta].nd  ? HIST_RND_BY_CANASTA[canasta].nd.vals  : null;
  var ipmVals = HIST_RND_BY_CANASTA[canasta] && HIST_RND_BY_CANASTA[canasta].ipm ? HIST_RND_BY_CANASTA[canasta].ipm.vals : null;
  var fnNd  = window['histRedraw_hrnd-global-nd'];
  var fnIpm = window['histRedraw_hrnd-global-ipm'];
  if(typeof fnNd  === 'function') setTimeout(function(){fnNd(accent, ndVals);},  20);
  if(typeof fnIpm === 'function') setTimeout(function(){fnIpm(accent, ipmVals);}, 20);
  /* También canvas del panel y dimensión */
  var fnPanelR   = window['histRedraw_hrnd-panel-nd'];
  var fnPanelIpm = window['histRedraw_hrnd-panel-ipm'];
  var fnDimR     = window['histRedraw_hrnd-dim-nd'];
  var fnDimIpm   = window['histRedraw_hrnd-dim-ipm'];
  if(typeof fnPanelR   === 'function') setTimeout(function(){fnPanelR(accent, ndVals);}, 30);
  if(typeof fnPanelIpm === 'function') setTimeout(function(){fnPanelIpm(accent, ipmVals);}, 30);
  if(typeof fnDimR     === 'function') setTimeout(function(){fnDimR(accent, ndVals);}, 30);
  if(typeof fnDimIpm   === 'function') setTimeout(function(){fnDimIpm(accent, ipmVals);}, 30);
 }
}
/* Canvas */
var RGB={'#333132':'51,49,50','#5C469C':'92,70,156','#EA0074':'234,0,116','#FCB000':'252,176,0','#4FC3F4':'79,195,244','#1A6B4A':'26,107,74'};
/* Tooltip state */
var W22_CANVAS_PTS={};
var W22_CANVAS_CFG={};
var W22_TOOLTIP=null;
function w22_getTooltip(){
 if(!W22_TOOLTIP){
  var t=document.createElement('div');
  t.id='w22-canvas-tip';
  t.style.cssText='position:fixed;pointer-events:none;display:none;background:var(--ink);color:#fff;font-size:10px;font-weight:700;padding:4px 8px;border-radius:3px;z-index:9999;white-space:nowrap;letter-spacing:.02em;';
  document.body.appendChild(t);
  W22_TOOLTIP=t;
 }
 return W22_TOOLTIP;
}
function w22_bindCanvasTip(el,cid,cfg,pts){
 W22_CANVAS_PTS[cid]=pts;
 W22_CANVAS_CFG[cid]=cfg;
 el.onmousemove=function(e){
  /* Usar siempre W22_CANVAS_CFG/PTS actuales — permiten actualización tras click */
  var liveCfg=W22_CANVAS_CFG[cid]||cfg;
  var rect=el.getBoundingClientRect();
  var mx=e.clientX-rect.left;
  var tip=w22_getTooltip();
  /* Recalcular pts con ancho real del canvas */
  var w=rect.width||el.offsetWidth||400;
  var vals=liveCfg.vals;
  var livePts=vals.map(function(v,i){return{x:(i/(vals.length-1))*w};});
  var best=-1,bestDx=9999;
  livePts.forEach(function(p,i){var dx=Math.abs(p.x-mx);if(dx<bestDx){bestDx=dx;best=i;}});
  if(best<0||bestDx>40){tip.style.display='none';return;}
  var sem=liveCfg.semanas?liveCfg.semanas[best]:('W'+(17+best));
  var val=vals[best];
  var fmtVal=liveCfg.metric==='ipm'?('$'+val.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g,',')):val.toFixed(2)+'%';
  tip.textContent=sem+': '+fmtVal;
  tip.style.display='block';
  tip.style.left=(e.clientX+10)+'px';
  tip.style.top=(e.clientY-28)+'px';
 };
 el.onmouseleave=function(){
  var tip=w22_getTooltip();tip.style.display='none';
 };
}
/* Canvas manejados por el IIFE del módulo histórico — NO redibujar desde aquí */
var HIST_MODULE_CANVAS = {
  'hcr-global-ef': true, 'hcr-global-cv': true,
  'hrnd-global-nd': true, 'hrnd-global-ipm': true
};

/* Datos históricos por canasta — inyectados desde Python como HIST_CR_BY_CANASTA y HIST_RND_BY_CANASTA */

function w22_redrawCanvas(accent){
 var rgb=RGB[accent]||'92,70,156';
 var hist=W.mode==='cr'?(typeof HIST_CR!=='undefined'?HIST_CR:{}):(typeof HIST_RND!=='undefined'?HIST_RND:{});
 
 /* Sobrescribir datos de canvas KPI global con los de la canasta activa */
 if(W.mode==='cr' && HIST_CR_BY_CANASTA[W.canasta]) {
   var cdata = HIST_CR_BY_CANASTA[W.canasta];
   if(cdata.ef) hist['hcr-global-ef'] = cdata.ef;
   if(cdata.cv) hist['hcr-global-cv'] = cdata.cv;
 }
 
 Object.keys(hist).forEach(function(cid){
  /* Saltear canvas manejados por el IIFE del módulo histórico */
  if(HIST_MODULE_CANVAS[cid]) return;
  var cfg=hist[cid],el=g(cid);if(!el||!el.getContext)return;
  el.width=el.offsetWidth||400;el.height=76;
  var ctx=el.getContext('2d'),vals=cfg.vals,h=el.height-10;
  var mn=Math.min.apply(null,vals),mx=Math.max.apply(null,vals),dR=mx-mn+0.0001;
  var pts=vals.map(function(v,i){return{x:(i/(vals.length-1))*el.width,y:el.height-((v-mn)/dR*h+5)};});
  var tY=el.height-((cfg.target-mn)/dR*h+5);
  ctx.clearRect(0,0,el.width,el.height);
  ctx.strokeStyle='rgba(0,0,0,0.15)';ctx.lineWidth=1;ctx.setLineDash([3,2]);
  ctx.beginPath();ctx.moveTo(0,tY);ctx.lineTo(el.width,tY);ctx.stroke();ctx.setLineDash([]);
  ctx.beginPath();ctx.moveTo(pts[0].x,el.height);ctx.lineTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);
  ctx.lineTo(pts[pts.length-1].x,el.height);ctx.closePath();
  ctx.fillStyle='rgba('+rgb+',0.12)';ctx.fill();
  ctx.strokeStyle=accent;ctx.lineWidth=2;ctx.lineCap='round';ctx.lineJoin='round';
  ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);ctx.stroke();
  for(var i=0;i<pts.length;i++){
   var last=i===pts.length-1;
   ctx.fillStyle=last?accent:'rgba('+rgb+',0.5)';ctx.globalAlpha=last?1:0.5;
   ctx.beginPath();ctx.arc(pts[i].x,pts[i].y,last?3:2,0,2*Math.PI);ctx.fill();ctx.globalAlpha=1;
  }
  /* Bind tooltip */
  var tipCfg={vals:cfg.vals,semanas:['W17','W18','W19','W20','W21'],metric:cid.indexOf('cv')>-1?'convrate':cid.indexOf('ipm')>-1?'ipm':cid.indexOf('nd')>-1?'nodispo':'eficacia'};
  w22_bindCanvasTip(el,cid,tipCfg,pts);
 });
}

/* w22_update() movido al final de js_override.js para que _cardRow esté definida */
/* w22_update(); */(function(d){setTimeout(function(){var col=cv().col;w22_redrawCanvas(col);w22_recolorSparks(col);},d);});
window.addEventListener('resize',function(){setTimeout(function(){w22_redrawCanvas(cv().col);},100);});
/* Tooltip en canvas del IIFE W21 */
setTimeout(function(){
 Object.keys(HIST_CR).forEach(function(cid){
  var el=document.getElementById(cid);if(!el)return;
  var cfg=HIST_CR[cid];
  var tipCfg={vals:cfg.vals,semanas:['W17','W18','W19','W20','W21'],
   metric:cid.indexOf('cv')>-1?'convrate':'eficacia'};
  function rebind(){
   var w=el.offsetWidth||400,hh=76,lh=hh-10;
   var mn=Math.min.apply(null,cfg.vals),mx=Math.max.apply(null,cfg.vals),dR=mx-mn+0.0001;
   var pts=cfg.vals.map(function(v,i){return{x:(i/(cfg.vals.length-1))*w,y:hh-((v-mn)/dR*lh+5)};});
   w22_bindCanvasTip(el,cid,tipCfg,pts);
  }
  rebind();setTimeout(rebind,600);setTimeout(rebind,1400);
 });
},1000);
