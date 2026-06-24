"""render_historico_svg.py — Panel SVG sin tooltip para evolución histórica W21+."""
import json as _json
from historico_data import get_serie, SEMANAS as _SEMANAS_DEF

_BANDA_JS = {
    'eficacia': "function(v){if(v>=97)return{c:'#1A6B4A',k:'Exitosa'};if(v>=93)return{c:'#FBBF24',k:'Aceptable'};if(v>=85)return{c:'#F97316',k:'Revisar'};if(v>=60)return{c:'#C0392B',k:'Cr\\u00edtica'};return{c:'#2D2828',k:'S\\u00fap. Cr\\u00edtica'};}",
    'nodispo':  "function(v){if(v<3)return{c:'#1A6B4A',k:'Exitosa'};if(v<5)return{c:'#FBBF24',k:'Aceptable'};if(v<20)return{c:'#F97316',k:'Revisar'};if(v<60)return{c:'#C0392B',k:'Cr\\u00edtica'};return{c:'#2D2828',k:'S\\u00fap. Cr\\u00edtica'};}",
    'ipm':      "function(v){if(v>=1500)return{c:'#1A6B4A',k:'Exitosa'};if(v>=650)return{c:'#FBBF24',k:'Aceptable'};if(v>=200)return{c:'#F97316',k:'Revisar'};return{c:'#C0392B',k:'Cr\\u00edtica'};}",
    'convrate': "function(v){if(v>=2.5)return{c:'#1A6B4A',k:'Exitosa'};if(v>=1.5)return{c:'#FBBF24',k:'Aceptable'};if(v>=0.8)return{c:'#F97316',k:'Revisar'};return{c:'#C0392B',k:'Cr\\u00edtica'};}",
    'bookability': "function(v){if(v>=97)return{c:'#1A6B4A',k:'Exitosa'};if(v>=93)return{c:'#FBBF24',k:'Aceptable'};if(v>=85)return{c:'#F97316',k:'Revisar'};if(v>=60)return{c:'#C0392B',k:'Cr\\u00edtica'};return{c:'#2D2828',k:'S\\u00fap. Cr\\u00edtica'};}",
}
_FMT_JS = {
    'ipm': "function(v){return '$'+Math.round(v);}",
}
_ACCENT = {
    'cr':  '#5C469C',
    'rnd': '#EA0074',
    'bk':  '#333132',
}
_REPORTE_MAP = {'cr': 'cr', 'rnd': 'rnd', 'bk': 'bk'}


def render_historico_svg(reporte, metrica, banda_actual, val_actual, canvas_id):
    """Genera panel histórico SVG con valores siempre visibles. Sin canvas, sin tooltip."""
    semanas = list(_SEMANAS_DEF)
    # Escalar val_actual igual que historico_module.py
    if metrica in ('eficacia', 'convrate', 'nodispo', 'bookability'):
        val_scaled = round(float(val_actual) * 100, 2)
    else:
        val_scaled = round(float(val_actual), 1)
    serie = get_serie(reporte, metrica, 'global', val_scaled)
    vals_def = []
    for v in serie:
        vals_def.append(round(float(v), 4) if v is not None else None)
    # Rellenar nulls
    for i in range(len(vals_def)):
        if vals_def[i] is None:
            vals_def[i] = vals_def[i-1] if i > 0 else 0.0

    accent = _ACCENT.get(reporte, '#5C469C')
    get_banda = _BANDA_JS.get(metrica, _BANDA_JS['eficacia'])
    fmt_val   = _FMT_JS.get(metrica, "function(v){return v.toFixed(1)+'%';}")

    cid       = canvas_id
    vals_json = _json.dumps(vals_def)
    sems_json = _json.dumps(semanas)

    # buildSerie JS — reutiliza la misma lógica que antes
    build_serie_js = """function buildSerie(wc,wp,wa,ha){
    var n=VD.length;
    if(ha&&ha.length===n){
      var s=ha.slice();
      for(var i=0;i<n;i++){
        if(s[i]===null||isNaN(s[i])){
          var l=null,r=null;
          for(var j=i-1;j>=0;j--){if(s[j]!==null&&!isNaN(s[j])){l=s[j];break;}}
          for(var k=i+1;k<n;k++){if(s[k]!==null&&!isNaN(s[k])){r=s[k];break;}}
          s[i]=l!==null?l:(r!==null?r:(isNaN(wc)?VD[n-1]:wc));
        }
      }
      return s;
    }
    var w25=(!isNaN(wa)&&wa>0)?wa:(isNaN(wc)?VD[VD.length-1]:wc);
    var w24=isNaN(wp)?w25:wp;
    /* Sin historia completa del hotel (solo tenemos W24-W25):
       usar el valor actual como baseline para W18-W23, así el gráfico
       cambia COMPLETAMENTE al ir hotel por hotel — no solo los últimos 2 pts. */
    var base=!isNaN(w25)?w25:VD[VD.length-1];
    var s=[];
    for(var i=0;i<VD.length-2;i++){s.push(base);}
    s.push(w24);s.push(w25);return s;
  }"""

    render_panel_js = """function renderPanel(vals,lbl){
    if(!el)return;
    var n=vals.length,W=320,SH=58;
    var mn=Math.min.apply(null,vals),mx=Math.max.apply(null,vals);
    var pad=(mx-mn)*0.18||3;mn-=pad;mx+=pad;var rng=mx-mn||1;
    function yOf(v){return SH-4-((v-mn)/rng)*(SH-10);}
    function xOf(i){return (i/(n-1))*W;}
    var pp=vals.map(function(v,i){return xOf(i).toFixed(1)+','+yOf(v).toFixed(1);});
    var aD='M'+pp[0]+' '+pp.slice(1).map(function(p){return 'L'+p;}).join(' ')+
            ' L'+xOf(n-1).toFixed(1)+','+SH+' L0,'+SH+' Z';
    var dots=vals.map(function(v,i){
      var b=getBanda(v),cx=xOf(i).toFixed(1),cy=yOf(v).toFixed(1),last=(i===n-1);
      var r=last?5.5:4,sw=last?2:1.5;
      var d='<circle cx="'+cx+'" cy="'+cy+'" r="'+r+'" fill="'+b.c+'" stroke="#FDFCF9" stroke-width="'+sw+'"/>';
      if(last)d+='<circle cx="'+cx+'" cy="'+cy+'" r="8" fill="none" stroke="'+b.c+'" stroke-width="1" stroke-opacity="0.25"/>';
      return d;
    }).join('');
    var svg='<svg viewBox="0 0 320 '+SH+'" width="100%" style="display:block;overflow:visible;margin-bottom:6px">'+
      '<path d="'+aD+'" fill="'+ACCENT+'" fill-opacity="0.07"/>'+
      '<polyline points="'+pp.join(' ')+'" fill="none" stroke="'+ACCENT+'" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'+
      dots+'</svg>';
    var cells=vals.map(function(v,i){
      var b=getBanda(v),wk=SEM[i]||('W'+(i+18)),last=(i===n-1);
      return '<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px">'+
        '<div style="font-size:9px;color:#B0A898">'+wk+'</div>'+
        '<div style="width:9px;height:9px;border-radius:50%;background:'+b.c+'"></div>'+
        '<div style="font-size:9.5px;font-weight:'+(last?800:600)+';color:'+b.c+'">'+fmtVal(v)+'</div>'+
        '</div>';
    }).join('');
    var dr='<div style="display:flex;gap:0;margin-bottom:8px">'+cells+'</div>';
    var cur=vals[n-1],hi=Math.max.apply(null,vals),lo=Math.min.apply(null,vals);
    var avg=Math.round(vals.reduce(function(a,b){return a+b;},0)/n*10)/10;
    var bC=getBanda(cur),bH=getBanda(hi),bL=getBanda(lo);
    /* Stat badge: estilo inspirado en el pill WoW de las cards */
    function sb(lb,v,bg,fg){
      return '<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px">'+
        '<div style="font-size:7.5px;color:#B0A898;text-transform:uppercase;letter-spacing:.06em">'+lb+'</div>'+
        '<div style="background:'+bg+';color:'+fg+';border-radius:4px;padding:2px 6px;font-size:10px;font-weight:700;white-space:nowrap">'+fmtVal(v)+'</div>'+
        '</div>';}
    /* Soft backgrounds: hex con 20% opacidad simulado mezclando con #FDFCF9 */
    function _soften(hex){
      var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
      var br=253,bg_=252,bb=249; /* #FDFCF9 */
      return 'rgb('+Math.round(r*.22+br*.78)+','+Math.round(g*.22+bg_*.78)+','+Math.round(b*.22+bb*.78)+')';}
    var sfBg=_soften(bC.c),mxBg=_soften(bH.c),mnBg=_soften(bL.c);
    var sf='<div style="display:flex;gap:5px;border-top:1px solid #E8E4DC;padding-top:8px;align-items:flex-end">'+
      sb('Actual',cur,sfBg,bC.c)+sb('M\u00e1x',hi,mxBg,bH.c)+sb('M\u00edn',lo,mnBg,bL.c)+sb('Prom',avg,'#EEE9E2','#333132')+
      '<div style="flex:1;display:flex;align-items:flex-end;justify-content:flex-end">'+
        '<div style="background:'+bC.c+';color:#fff;border-radius:4px;padding:2px 7px;font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.04em">'+bC.k+'</div>'+
      '</div></div>';
    var lblEl=document.getElementById('hist-'+CID+'-label');
    if(lblEl&&lbl)lblEl.textContent=lbl;
    el.innerHTML=svg+dr+sf;
  }"""

    iife = (
        "(function(){"
        "var CID='" + cid + "';"
        "var VD=" + vals_json + ";"
        "var SEM=" + sems_json + ";"
        "var ACCENT='" + accent + "';"
        "var el=document.getElementById(CID);"
        "var getBanda=" + get_banda + ";"
        "var fmtVal=" + fmt_val + ";"
        + build_serie_js
        + render_panel_js
        + "window['histUpdate_'+CID]=function(wc,wp,wa,lbl,ha){el=document.getElementById(CID);renderPanel(buildSerie(wc,wp,wa,ha),lbl||'');};"
        "document.addEventListener('hist-update',function(e){"
          "if(e.detail.cid!==CID)return;"
          "if(!e.detail.hist_arr&&window._corpHist&&window._corpHist[CID]){"
            "var ch=window._corpHist[CID];renderPanel(buildSerie(0,0,0,ch.arr),ch.lbl||'');return;}"
          "renderPanel(buildSerie(e.detail.w_curr,e.detail.w_prev,e.detail.w_actual,e.detail.hist_arr||null),e.detail.label||'');"
        "});"
        "document.addEventListener('hist-reset',function(e){"
          "if(e.detail.cid!==CID)return;renderPanel(VD,'Global');});"
        "if(document.readyState==='loading'){"
          "document.addEventListener('DOMContentLoaded',function(){renderPanel(VD,'Global');});"
        "}else{renderPanel(VD,'Global');}"
        "})();"
    )

    return f'<div id="{cid}" style="width:100%;"></div>\n<script>{iife}</script>\n'
