"""
historico_module.py — Módulo histórico reactivo unificado (W21+).
Consolida historico_module_v2.py (CR) + historico_module_rnd.py (RND).

Una única función render_historico() genera canvas y JS para todas las métricas:
  CR:  'eficacia' (%) | 'convrate' (%)
  RND: 'nodispo' (%, escala invertida) | 'ipm' (USD/M)
"""
import json as _json
from historico_data import get_serie, SEMANAS

METRIC_CONFIGS = {
    ('cr', 'eficacia'): {'target': 97.0, 'unit': '%', 'invert': False, 'accent': '#5C469C', 'accent_rgb': '92,70,156', 'bar_ceil': 97.0},
    ('cr', 'convrate'): {'target': 2.5, 'unit': '%', 'invert': False, 'accent': '#5C469C', 'accent_rgb': '92,70,156', 'bar_ceil': 2.5},
    ('rnd', 'nodispo'): {'target': 0.05, 'unit': '%', 'invert': True, 'accent': '#EA0074', 'accent_rgb': '234,0,116', 'bar_ceil': 0.60},
    ('rnd', 'ipm'): {'target': 650.0, 'unit': ' USD/M', 'invert': False, 'accent': '#4FC3F4', 'accent_rgb': '79,195,244', 'bar_ceil': 3000.0},
    ('bk',  'bookability'): {'target': 97.0, 'unit': '%', 'invert': False, 'accent': '#333132', 'accent_rgb': '51,49,50', 'bar_ceil': 100.0},
}

_BANDA_COLORS = {
    'Exitosa': {'bg': '#E1F5EE', 'fg': '#1A6B4A', 'bd': '#1D9E75', 'footer': '#1A6B4A'},
    'Aceptable': {'bg': '#FEF9C3', 'fg': '#713F12', 'bd': '#FCD34D', 'footer': '#713F12'},
    'Revisar': {'bg': '#FED7AA', 'fg': '#C2410C', 'bd': '#F97316', 'footer': '#C2410C'},
    'Crítica': {'bg': '#FCE4F1', 'fg': '#99162B', 'bd': '#C0392B', 'footer': '#99162B'},
    'Súper Crítica': {'bg': '#EDECEC', 'fg': '#4A3F3F', 'bd': '#9B2222', 'footer': '#4A3F3F'},
    'Sin Conversión': {'bg': '#F2EEE6', 'fg': '#5F5E5A', 'bd': '#8A8377', 'footer': '#5F5E5A'},
}
_BANDA_COLORS_JS = {k: {'bg': v['bg'], 'fg': v['fg'], 'footer': v['footer']} for k, v in _BANDA_COLORS.items()}

def render_historico(reporte, metrica, banda_actual, val_actual, canvas_id, global_ceil=None):
    """Genera módulo histórico unificado para CR y RND (W21+)."""
    cfg = METRIC_CONFIGS.get((reporte, metrica))
    if not cfg:
        raise ValueError(f"Métrica desconocida: ({reporte}, {metrica})")
    
    target = cfg['target']
    bar_ceil = global_ceil if global_ceil is not None else cfg['bar_ceil']
    accent = cfg['accent']
    accent_rgb = cfg['accent_rgb']
    is_inverted = cfg['invert']
    unit = cfg['unit']
    
    semanas = list(SEMANAS)
    idx_current = len(semanas) - 1
    
    scope = 'global'
    for k in ('op', 'cug', 'b2c'):
        if k in canvas_id:
            scope = k
            break
    
    # val_actual viene como fracción (0.0263) del pickle → convertir a % (2.63)
    # Los valores históricos en HIST_DATA están en % para comparar en misma escala
    # IPM ya viene en $ directamente (no necesita conversión)
    if metrica in ('eficacia', 'convrate', 'nodispo', 'bookability'):
        w_current_val = round(val_actual * 100, 2)
    else:
        w_current_val = round(val_actual, 1)
    vals_default = get_serie(reporte, metrica, scope, w_current_val)
    vals_default = [round(v, 2 if metrica in ('eficacia', 'convrate', 'nodispo', 'bookability') else 1) for v in vals_default]
    
    fmt_val = (lambda v: f'{v:.2f}%') if unit == '%' else (lambda v: f'${v:,.0f}')
    
    v_min, v_max = min(vals_default), max(vals_default)
    v_avg = sum(vals_default) / len(vals_default)
    v_curr = vals_default[-1]
    
    bc = _BANDA_COLORS.get(banda_actual, _BANDA_COLORS['Sin Conversión'])
    
    def _sparkbars(vals):
        bars = ''
        _spark_max = max(vals) if max(vals) > 0 else 1
        _spark_min = min(vals)
        _spark_range = _spark_max - _spark_min if _spark_max != _spark_min else _spark_max
        for i, v in enumerate(vals):
            # Mayor valor → barra más alta (NoDispo: mayor=peor=más visible; IPM: mayor=mejor=más visible)
            ratio = (v - _spark_min) / _spark_range
            height = max(int(4 + 14 * ratio), 4)
            alpha = round(0.25 + 0.70 * ratio, 2)
            bg = accent if i == idx_current else (f'rgba({accent_rgb},{alpha})' if accent_rgb else f'rgba(92,70,156,{alpha})')
            bars += f'<div style="flex:1;background:{bg};height:{height}px;border-radius:1px 1px 0 0;" title="{semanas[i]}: {fmt_val(v)}"></div>'
        return bars
    
    spark_html = _sparkbars(vals_default)
    
    vals_json = _json.dumps(vals_default)
    semanas_json = _json.dumps(semanas)
    banda_colors_js = _json.dumps(_BANDA_COLORS_JS)
    
    best_label = "Mín 5W" if is_inverted else "Máx 5W"
    worst_label = "Máx 5W" if is_inverted else "Mín 5W"
    best_val = v_min if is_inverted else v_max
    worst_val = v_max if is_inverted else v_min
    
    target_disp = {'eficacia': '≥ 97%', 'convrate': '≥ 2,5%', 'nodispo': '< 5%', 'ipm': '≥ $650', 'bookability': '≥ 97%'}.get(metrica, 'Target')
    is_inverted_str = 'true' if is_inverted else 'false'
    
    return f'''<div id="hist-{canvas_id}" style="margin-top:auto;padding:10px 8px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;width:100%;box-sizing:border-box;">
  <div style="height:8px;"></div>
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
    <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">
      Evolución Histórica · <span id="hist-{canvas_id}-label" style="color:var(--ink-muted);font-weight:600;">Global</span>
    </span>
  </div>
  <div style="width:100%;height:100px;"><canvas id="{canvas_id}" style="display:block;width:100%;height:100px;"></canvas></div>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px;margin-top:10px;">
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Actual</div>
      <div id="hist-{canvas_id}-actual" style="font-size:13px;font-weight:700;color:{accent};margin-top:2px;">{fmt_val(v_curr)}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">{best_label}</div>
      <div id="hist-{canvas_id}-best" style="font-size:13px;font-weight:700;color:#2F6C34;margin-top:2px;">{fmt_val(best_val)}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">{worst_label}</div>
      <div id="hist-{canvas_id}-worst" style="font-size:13px;font-weight:700;color:#C0392B;margin-top:2px;">{fmt_val(worst_val)}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Prom 5W</div>
      <div id="hist-{canvas_id}-avg" style="font-size:13px;font-weight:700;color:var(--ink);margin-top:2px;">{fmt_val(v_avg)}</div>
    </div>
    <div id="hist-{canvas_id}-banda-box" style="display:flex;align-items:center;justify-content:center;text-align:center;padding:6px 2px;border-radius:3px;background:{bc['bg']};border:1px solid {bc['bd']};">
      <div id="hist-{canvas_id}-banda" style="font-size:11px;font-weight:700;color:{bc['fg']};margin-top:2px;line-height:1.2;text-transform:uppercase;letter-spacing:.04em;">{banda_actual.upper()}</div>
    </div>
  </div>
  <div style="margin-top:10px;">
    <div style="font-size:7px;color:var(--ink-muted);font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">{"Severidad vs universo global (↑ más NoDispo)" if is_inverted else "Posición vs target global"}</div>
    <div id="hist-{canvas_id}-spark" style="display:flex;align-items:flex-end;gap:2px;height:18px;">{spark_html}</div>
    <div style="position:relative;height:14px;margin-top:2px;">
      {''.join(
        f'<span style="position:absolute;left:{i/(len(semanas)-1)*100:.1f}%;transform:translateX(-50%);font-size:7px;font-weight:700;color:{'var(--ink)' if i==len(semanas)-1 else 'var(--ink-muted)'};">{s}</span>'
        if i == 0 or i == len(semanas)-1 else ''
        for i, s in enumerate(semanas)
      )}
    </div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:1px solid var(--rule-soft);">
    <span id="hist-{canvas_id}-banda-footer" style="font-size:8px;font-weight:700;color:{bc['footer']};background:{bc['bg']};padding:2px 6px;border-radius:2px;text-transform:uppercase;letter-spacing:.04em;">{banda_actual.upper()}</span>
    <span id="hist-{canvas_id}-trend-footer" style="font-size:8px;color:var(--ink-muted);">Target: {target_disp}</span>
  </div>
</div>

<script>
(function(){{
  var CID = '{canvas_id}', IS_INVERTED = {is_inverted_str}, METRIC = '{metrica}', TARGET = {target}, BAR_CEIL = {bar_ceil};
  var SEMANAS = {semanas_json}, VALS_DEF = {vals_json}, BC = {banda_colors_js};
  /* W23+: Registrar la serie canónica (8 puntos correctos) en objeto global dedicado.
     El tooltip OVERRIDE lee de aquí con máxima prioridad, evitando datos viejos de W22_CANVAS_CFG. */
  if (typeof window !== 'undefined') {{
    if (!window._HIST_CANON) window._HIST_CANON = {{}};
    window._HIST_CANON[CID] = {{ semanas: SEMANAS.slice(), vals: VALS_DEF.slice(), metric: METRIC }};
  }}
  var ACCENT_HEX = '{accent}', ACCENT_RGB = {f"'{accent_rgb}'" if accent_rgb else 'null'};
  
  function getBanda(v) {{
    if (METRIC === 'eficacia' || METRIC === 'bookability') {{ var pct = v / 100; if (pct >= 0.97) return 'Exitosa'; if (pct >= 0.93) return 'Aceptable'; if (pct >= 0.85) return 'Revisar'; if (pct >= 0.60) return 'Crítica'; return 'Súper Crítica'; }}
    if (METRIC === 'convrate') {{ var pct = v / 100; if (pct === 0) return 'Sin Conversión'; if (pct < 0.008) return 'Crítica'; if (pct < 0.015) return 'Revisar'; if (pct <= 0.025) return 'Aceptable'; return 'Exitosa'; }}
    if (METRIC === 'nodispo') {{ var pct = v / 100; if (pct < 0.03) return 'Exitosa'; if (pct <= 0.05) return 'Aceptable'; if (pct <= 0.20) return 'Revisar'; if (pct <= 0.60) return 'Crítica'; return 'Súper Crítica'; }}
    if (v === 0) return 'Sin Conversión'; if (v < 200) return 'Crítica'; if (v < 650) return 'Revisar'; if (v <= 1500) return 'Aceptable'; return 'Exitosa';
  }}
  
  function fmtVal(v) {{ return METRIC === 'ipm' ? '$' + v.toFixed(0).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ',') : v.toFixed(2) + '%'; }}
  
  /* Thresholds por métrica */
  var THS = METRIC === 'eficacia' ? [97, 93, 85, 60] :
            METRIC === 'convrate' ? [2.5, 1.5, 0.8] :
            METRIC === 'nodispo' ? [3.0, 5.0, 20.0, 60.0] : [650, 500, 199];
  var THS_SORTED = THS.slice().sort(function(a, b) {{ return a - b; }});
  
  /* Distancia ordinal: cuántas bandas de distancia al target */
  function ordinalDist(mid, target, thresholds, invert) {{
    if (!invert) {{
      if (mid >= target) return 0;
      return thresholds.filter(function(t) {{ return t > mid && t <= target; }}).length;
    }} else {{
      if (mid <= target) return 0;
      return thresholds.filter(function(t) {{ return t < mid && t >= target; }}).length;
    }}
  }}
  
  /* Color de semáforo por distancia ordinal */
  var SEMAFORO_PALETTE = [
    {{line: '#1A6B4A', fg: '#0F5132', label: '≥ target'}},
    {{line: '#D97706', fg: '#92400E', label: '–1 banda'}},
    {{line: '#C2410C', fg: '#9A3412', label: '–2 bandas'}},
    {{line: '#BE123C', fg: '#9F1239', label: '–3+ bandas'}}
  ];
  function getSemaforoColor(dist) {{
    return SEMAFORO_PALETTE[Math.min(dist, 3)];
  }}
  
  /* Formato de label de threshold */
  function fmtThLabel(t) {{
    return METRIC === 'ipm' ? '$' + t.toFixed(0).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ',') :
           METRIC === 'nodispo' ? t.toFixed(1) + '%' : t.toFixed(t < 10 ? 1 : 0) + '%';
  }}
  
  /* Formato de label de target */
  function fmtTarget() {{
    return METRIC === 'ipm' ? 'T:$' + TARGET.toFixed(0).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ',') :
           (METRIC === 'eficacia' || METRIC === 'bookability') ? 'T:' + TARGET.toFixed(0) + '%' : 'T:' + TARGET.toFixed(1) + '%';
  }}
  
  var _lastWidth = 0;  /* Ancho válido del último drawCanvas exitoso */
  function drawCanvas(vals) {{
    currentVals = vals;  /* recordar último estado para re-draws automáticos */
    var el = document.getElementById(CID), ctx = el ? el.getContext('2d', {{willReadFrequently: false}}) : null;
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
    var i_min = Math.min(Math.min.apply(null, vals), TARGET);
    var i_max = Math.max(Math.max.apply(null, vals), TARGET);
    var i_range = (i_max - i_min) || (i_max * 0.05) || 1.0;
    var ths_s = THS_SORTED.slice();  /* thresholds ordenados */
    var below = ths_s.filter(function(t) {{ return t < i_min; }});
    var above = ths_s.filter(function(t) {{ return t > i_max; }});
    var adj_below = below.length ? below[below.length-1] : null;
    var adj_above = above.length ? above[0] : null;
    var anchor_min = i_min, anchor_max = i_max;
    if (adj_below !== null && (i_min - adj_below) <= i_range) anchor_min = adj_below;
    if (adj_above !== null && (adj_above - i_max) <= i_range) anchor_max = adj_above;
    var pad = i_range * 0.35;  /* W23+: más padding para que puntos abruptos no queden pegados al borde */
    var canvas_min = anchor_min - pad, canvas_max = anchor_max + pad;
    var dR = canvas_max - canvas_min + 0.0001;
    var xOf = function(i) {{ return pL + (i/(n-1))*cw; }};
    var yOf = function(v) {{ return pT + ch - (v-canvas_min)/dR*ch; }};
    /* Líneas de umbral visibles (sin fondos de banda) */
    var visible_ths = THS.filter(function(t) {{ return t > canvas_min && t < canvas_max && t !== TARGET; }}).sort(function(a,b){{return b-a;}});
    visible_ths.forEach(function(t) {{
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
    }});
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
    for (var i = 0; i < n; i++) {{ 
      var isLast = (i === n - 1); 
      ctx.fillStyle = ACCENT_HEX;
      ctx.globalAlpha = 1.0; 
      ctx.beginPath(); 
      ctx.arc(xOf(i), yOf(vals[i]), isLast ? 3.5 : 2.5, 0, 2 * Math.PI); 
      ctx.fill(); 
      if (isLast) {{ ctx.strokeStyle = '#FDFCF9'; ctx.lineWidth = 1.5; ctx.stroke(); }}
    }}
    /* Actualizar W22_CANVAS_CFG para que el tooltip use vals correctos */
    if (typeof W22_CANVAS_CFG !== 'undefined') W22_CANVAS_CFG[CID] = {{vals: vals, semanas: SEMANAS, metric: METRIC}};
    /* Actualizar también _HIST_CANON con los vals actuales (puede ser una serie de item específico) */
    if (typeof window !== 'undefined' && window._HIST_CANON && window._HIST_CANON[CID]) {{
      window._HIST_CANON[CID].vals = vals.slice();
    }}
  }}
  
  function updateMetrics(vals, lbl) {{
    var vMin = Math.min.apply(null, vals), vMax = Math.max.apply(null, vals), vAvg = vals.reduce(function(a,b){{return a+b;}},0)/vals.length, vCurr = vals[vals.length-1];
    var banda = getBanda(vCurr), bc = BC[banda] || BC['Sin Conversión'];
    var el = document.getElementById('hist-'+CID+'-label'); if (el) el.textContent = lbl || 'Global';
    el = document.getElementById('hist-'+CID+'-actual'); if (el) el.textContent = fmtVal(vCurr);
    el = document.getElementById('hist-'+CID+'-best'); if (el) el.textContent = fmtVal(IS_INVERTED ? vMin : vMax);
    el = document.getElementById('hist-'+CID+'-worst'); if (el) el.textContent = fmtVal(IS_INVERTED ? vMax : vMin);
    el = document.getElementById('hist-'+CID+'-avg'); if (el) el.textContent = fmtVal(vAvg);
    var bbEl = document.getElementById('hist-'+CID+'-banda-box'), bEl = document.getElementById('hist-'+CID+'-banda');
    if (bbEl) {{ bbEl.style.background = bc.bg; bbEl.style.borderColor = bc.fg; bbEl.style.color = bc.fg; }}
    if (bEl) {{ bEl.textContent = banda; bEl.style.color = bc.fg; }}
    el = document.getElementById('hist-'+CID+'-banda-footer'); if (el) {{ el.textContent = banda.toUpperCase(); el.style.color = bc.footer; el.style.background = bc.bg; }}
    /* Actualizar el valor grande de la card siempre — usa vCurr (W21) actual */
    var kvMap = {{'hcr-global-ef': 'w21-kv-ef', 'hcr-global-cv': 'w21-kv-cv',
                 'hrnd-global-nd': 'w21-kv-nd', 'hrnd-global-ipm': 'w21-kv-rpm'}};
    var kvId = kvMap[CID];
    if (kvId) {{
      var kvEl = document.getElementById(kvId);
      if (kvEl) {{ kvEl.textContent = fmtVal(vCurr); }}
    }}
  }}
  
  var currentVals = VALS_DEF.slice();  /* mutable — guarda el último estado dibujado */
  function buildSerie(w_c, w_p) {{ var s = VALS_DEF.slice(); s[s.length-1] = w_c; s[s.length-2] = w_p; return s; }}
  
  function attachListeners() {{
    /* Solo maneja click en el label del histórico para volver a Global.
       La selección de filas la maneja js_override document-level listener
       que dispara hist-update/hist-reset correctamente. */
    var hEl = document.getElementById('hist-'+CID), card = hEl ? hEl.closest('.kpi-card') : null;
    if (!card) return;
    var lblEl = document.getElementById('hist-'+CID+'-label');
    if (lblEl) lblEl.addEventListener('click', function() {{
      card.querySelectorAll('[data-hist-w20],[data-hist-w21]').forEach(function(r) {{ r.style.background = ''; r.removeAttribute('data-selected'); }});
      drawCanvas(VALS_DEF); updateMetrics(VALS_DEF, 'Global');
      lblEl.textContent = 'Global';
    }});
  }}
  
  function _cardWidth() {{
    /* Ancho de la kpi-card que contiene el canvas — visible aunque canvas esté en display:none */
    var el = document.getElementById(CID);
    if (!el) return 0;
    var p = el.parentElement;
    while (p) {{ if (p.offsetWidth > 50) return p.offsetWidth; p = p.parentElement; }}
    return 0;
  }}

  function _tryDraw() {{
    var el = document.getElementById(CID);
    if (!el) return false;
    var ow = el.offsetWidth || _cardWidth() || _lastWidth;
    if (ow > 50) {{ _lastWidth = ow; drawCanvas(currentVals); return true; }}
    return false;
  }}

  function init() {{
    updateMetrics(VALS_DEF, 'Global'); attachListeners();
    var el = document.getElementById(CID);
    if (el) {{
      var det = el.closest('details');
      if (det) det.addEventListener('toggle', function() {{ if (det.open) requestAnimationFrame(_tryDraw); }});
      var drawn = false;
      /* Observar la CARD (que sí es visible) no el canvas (que está en display:none) */
      var anchor = el.closest('.kpi-card') || el.parentElement;
      if (typeof IntersectionObserver !== 'undefined' && anchor) {{
        new IntersectionObserver(function(entries) {{ entries.forEach(function(entry) {{
          if (entry.isIntersecting) {{ requestAnimationFrame(function() {{ if(_tryDraw()) drawn=true; }}); }}
        }}); }}, {{threshold: 0.01}}).observe(anchor);
      }}
      /* Fallback por si el observer no dispara */
      [300, 800, 2000].forEach(function(d) {{
        setTimeout(function() {{ if (!drawn && _tryDraw()) drawn = true; }}, d);
      }});
    }}
    document.addEventListener('change', function(e) {{
      if (e.target.type !== 'radio') return;
      requestAnimationFrame(function() {{ requestAnimationFrame(_tryDraw); }});
    }});
  }}
  
  document.addEventListener('hist-update', function(e) {{
    if (e.detail.cid !== CID) return;
    var s = buildSerie(e.detail.w_curr, e.detail.w_prev);
    var lbl = e.detail.label || '';
    /* Doble rAF: el primer frame inicia el layout, el segundo lo tiene disponible */
    requestAnimationFrame(function() {{
      requestAnimationFrame(function() {{
        drawCanvas(s);
        updateMetrics(s, lbl);
      }});
    }});
  }});
  document.addEventListener('hist-reset', function(e) {{
    if (e.detail.cid !== CID) return;
    requestAnimationFrame(function() {{ drawCanvas(VALS_DEF); updateMetrics(VALS_DEF, 'Global'); }});
  }});
  
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else requestAnimationFrame(init);
  
  /* Exponer función de redraw con nuevo accent para cambio de canasta */
  window['histRedraw_'+CID] = function(newAccent, newVals) {{
    if (newAccent) {{
      var _rgbMap = (typeof RGB !== 'undefined') ? RGB : {{
        '#5C469C':'92,70,156','#EA0074':'234,0,116','#FCB000':'252,176,0',
        '#4FC3F4':'79,195,244','#1A6B4A':'26,107,74','#333132':'51,49,50'
      }};
      ACCENT_HEX = newAccent;
      ACCENT_RGB = _rgbMap[newAccent] || '92,70,156';
    }}
    var vals = newVals || currentVals;
    drawCanvas(vals); updateMetrics(vals, 'Global');
  }};
}})();
</script>'''
