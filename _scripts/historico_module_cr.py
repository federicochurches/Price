"""
historico_module_cr.py — Módulo histórico reactivo para CheckRates (CR).
Dos métricas con colores del sistema:
  - Eficacia: escala normal (mayor = mejor), target ≥ 97%, accent magenta #EA0074
  - ConvRate: escala normal (mayor = mejor), target ≥ 2,0%, accent violet #5C469C
  
FIXES W20:
  1. Labels Canvas: alpha 0.55 → 0.80, font-size 7px → 8px (legibilidad)
  2. Semanas dinámicas: parametrizar week_current para evitar W21 en W20
  3. Datos ficticios más realistas con variabilidad
  4. Asegurar 8 semanas (W13-W20 para W20 actual, W14-W21 para W21 actual, etc.)
"""
import json as _json

CR_ACCENT_EFICACIA = '#EA0074'   # magenta (mismo que RND)
CR_ACCENT_CONVRATE = '#5C469C'   # violet principal CR

# Colores del sistema D (idénticos a render_helpers.py)
_BANDA_COLORS = {
    'Exitosa':        {'bg': '#E1F5EE', 'fg': '#085041', 'bd': '#1D9E75',  'footer': '#085041'},
    'Aceptable':      {'bg': '#EDE8F7', 'fg': '#3C3489', 'bd': '#5C469C',  'footer': '#3C3489'},
    'Revisar':        {'bg': '#FFEDD5', 'fg': '#7C2D12', 'bd': '#F97316',  'footer': '#7C2D12'},
    'Crítica':        {'bg': '#FCE4F1', 'fg': '#99162B', 'bd': '#C0392B',  'footer': '#99162B'},
    'Súper Crítica':  {'bg': '#A32D2D', 'fg': '#FCEBEB', 'bd': '#791F1F',  'footer': '#FCEBEB'},
    'Sin Conversión': {'bg': '#F2EEE6', 'fg': '#5F5E5A', 'bd': '#8A8377',  'footer': '#5F5E5A'},
}
_BANDA_COLORS_JS = {
    k: {'bg': v['bg'], 'fg': v['fg'], 'footer': v['footer']}
    for k, v in _BANDA_COLORS.items()
}


def render_historico_cr(metric_type, banda_actual, val_actual, canvas_id,
                         current_week='W20', hist_vals=None, global_ceil=None):
    """
    IMPORTANTE: current_week debe ser la semana ACTUAL, NO la próxima.
    Ejemplo: Si hoy es W20, pasar 'W20' (no 'W21')
    El módulo genera 8 semanas: W(N-7) a W(N)
    """
    """
    metric_type    : 'eficacia' | 'convrate'
    banda_actual   : string banda sistema D
    val_actual     : float — Eficacia en [0,1] para eficacia, % para convrate (ej: 2.15)
    canvas_id      : ID único del canvas (ej: 'h-global-ef', 'h-op-cv')
    current_week   : 'W20' o 'W21', etc. (para generar semanas correctas)
    hist_vals      : lista 8 floats W(N-7)-W(N) (real del pickle, si disponible)
    global_ceil    : techo para sparkline (default: 1.0 para eficacia, 3.5 para convrate)
    """
    is_eficacia = metric_type == 'eficacia'
    target      = 0.97  if is_eficacia else 2.0    # ≥ 97% Eficacia | ≥ 2,0% ConvRate
    bar_ceil    = global_ceil if global_ceil is not None else (1.0 if is_eficacia else 3.5)
    accent      = CR_ACCENT_EFICACIA if is_eficacia else CR_ACCENT_CONVRATE

    # ── Generar semanas dinámicas ───────────────────────────────────────────
    # Extraer número de week (ej: 'W20' → 20)
    try:
        week_num = int(current_week[1:])
    except:
        week_num = 20
    
    # Generar 8 semanas previas (ej: W20 actual → W13-W20)
    week_start = week_num - 7
    semanas = [f'W{week_start + i}' for i in range(8)]  # W13-W20 si current_week='W20'

    # ── Datos ficticios más realistas (variabilidad que simula realidad) ───
    # Si no hay hist_vals, usar fixtures
    _FICTICIOS = {
        'eficacia': {
            'global': [0.9650, 0.9680, 0.9625, 0.9710, 0.9695, 0.9720, 0.9685, 0.9740],
            'op':     [0.9820, 0.9840, 0.9805, 0.9860, 0.9835, 0.9870, 0.9845, 0.9895],
            'cug':    [0.9520, 0.9550, 0.9480, 0.9590, 0.9560, 0.9605, 0.9570, 0.9620],
            'b2c':    [0.9380, 0.9420, 0.9350, 0.9480, 0.9450, 0.9510, 0.9470, 0.9530],
        },
        'convrate': {
            'global': [1.72, 1.85, 1.68, 1.95, 1.80, 2.05, 1.90, 2.15],
            'op':     [2.10, 2.25, 2.05, 2.35, 2.20, 2.45, 2.30, 2.55],
            'cug':    [1.45, 1.60, 1.40, 1.70, 1.55, 1.80, 1.65, 1.90],
            'b2c':    [1.20, 1.35, 1.15, 1.45, 1.30, 1.55, 1.40, 1.65],
        },
    }

    scope = 'global'
    for k in ('op', 'cug', 'b2c'):
        if k in canvas_id:
            scope = k; break

    w13_w20 = hist_vals if hist_vals else _FICTICIOS[metric_type][scope]

    # Convertir val_actual a la unidad de display
    if is_eficacia:
        # Eficacia: val en [0,1] → mostrar en %
        w_curr_val   = round(val_actual * 100, 2)
        vals_default = [round(v * 100, 2) for v in w13_w20]  # todo en %
        fmt_val      = lambda v: f'{v:.2f}%'
        target_disp  = '≥ 97%'
        unit         = '%'
    else:
        # ConvRate: val ya en %
        w_curr_val   = round(float(val_actual), 2)
        vals_default = [round(v, 2) for v in w13_w20]  # todo en %
        fmt_val      = lambda v: f'{v:.2f}%'
        target_disp  = '≥ 2,0%'
        unit         = '%'

    v_min  = min(vals_default); v_max = max(vals_default)
    v_avg  = sum(vals_default) / len(vals_default)
    v_curr = vals_default[-1];  v_prev = vals_default[-2]
    delta  = v_curr - v_prev

    bc       = _BANDA_COLORS.get(banda_actual, _BANDA_COLORS['Sin Conversión'])
    b_fg     = bc['fg']; b_bg = bc['bg']; b_bd = bc['bd']; b_footer = bc['footer']

    # Sparkline: escala global (Eficacia y ConvRate ambas: mayor = mejor)
    def _sparkbars(vals):
        bars = ''
        for i, v in enumerate(vals):
            ratio = min(v / (bar_ceil * 100), 1.0) if bar_ceil > 0 else 0.5
            height = max(int(2 + 16 * ratio), 2)
            alpha  = round(0.20 + 0.75 * ratio, 2)
            bg     = accent if i == 7 else f'rgba({_hex_to_rgb(accent)},{alpha})'
            bars += (f'<div style="flex:1;background:{bg};height:{height}px;'
                     f'border-radius:1px 1px 0 0;" title="{semanas[i]}: {fmt_val(v)}"></div>')
        return bars

    def _hex_to_rgb(h):
        h = h.lstrip('#')
        return ','.join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))

    spark_html = _sparkbars(vals_default)

    # Métricas iniciales
    actual_str = fmt_val(v_curr)
    max_str    = fmt_val(v_max)
    min_str    = fmt_val(v_min)
    avg_str    = fmt_val(v_avg)

    # Serializar para JS
    vals_json        = _json.dumps(vals_default)
    semanas_json     = _json.dumps(semanas)
    banda_colors_js  = _json.dumps(_BANDA_COLORS_JS)
    base_ratios      = [round(v / (w13_w20[-1] + 0.0001), 6) for v in w13_w20[:7]]
    base_ratios_json = _json.dumps(base_ratios)

    # Canvas: target en %
    canvas_target = target * 100 if is_eficacia else target

    return f'''<div id="hist-{canvas_id}"
     style="margin-top:16px;padding:12px 14px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;">

  <!-- Header -->
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
    <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">
      Evolución Histórica ·
      <span id="hist-{canvas_id}-label" style="color:{accent};font-weight:700;">Global</span>
    </span>
  </div>

  <!-- Canvas -->
  <div style="width:100%;height:76px;">
    <canvas id="{canvas_id}" style="display:block;width:100%;height:76px;"></canvas>
  </div>

  <!-- 5 métricas -->
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px;margin-top:10px;">
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Actual</div>
      <div id="hist-{canvas_id}-actual" style="font-size:13px;font-weight:700;color:{accent};margin-top:2px;">{actual_str}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Máx 8W</div>
      <div id="hist-{canvas_id}-best" style="font-size:13px;font-weight:700;color:#2F6C34;margin-top:2px;">{max_str}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Mín 8W</div>
      <div id="hist-{canvas_id}-worst" style="font-size:13px;font-weight:700;color:#C0392B;margin-top:2px;">{min_str}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Prom 8W</div>
      <div id="hist-{canvas_id}-avg" style="font-size:13px;font-weight:700;color:var(--ink);margin-top:2px;">{avg_str}</div>
    </div>
    <div id="hist-{canvas_id}-banda-box"
         style="text-align:center;padding:6px 2px;border-radius:3px;background:{b_bg};border:1px solid {b_bd};">
      <div id="hist-{canvas_id}-banda" style="font-size:11px;font-weight:700;color:{b_fg};margin-top:2px;line-height:1.2;text-transform:uppercase;letter-spacing:.04em;">{banda_actual.upper()}</div>
    </div>
  </div>

  <!-- Sparkline: escala global -->
  <div style="margin-top:10px;">
    <div style="font-size:7px;color:var(--ink-muted);font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">
      Posición vs target global
    </div>
    <div id="hist-{canvas_id}-spark"
         style="display:flex;align-items:flex-end;gap:2px;height:18px;">{spark_html}</div>
    <div style="display:flex;justify-content:space-between;margin-top:2px;">
      <span style="font-size:7px;color:var(--ink-muted);">{semanas[0]}</span>
      <span style="font-size:7px;color:var(--ink-muted);">Target</span>
      <span style="font-size:7px;color:var(--ink-muted);">{semanas[-1]}</span>
    </div>
  </div>

  <!-- Footer -->
  <div id="hist-{canvas_id}-banda-footer"
       style="margin-top:8px;padding:8px;background:var(--paper);border-radius:3px;font-size:9px;color:{b_footer};font-weight:600;text-align:center;">
    {banda_actual.upper()}
  </div>

  <script>
(function() {{
  var CID        = '{canvas_id}';
  var METRIC_TYPE = '{metric_type}';
  var IS_EF      = METRIC_TYPE === 'eficacia';
  var ACCENT_HEX = '{accent}';
  var TARGET     = {canvas_target};
  var BAR_CEIL   = {bar_ceil * 100};
  var VALS_DEF   = {vals_json};
  var SEMANAS    = {semanas_json};
  var BC         = {banda_colors_js};
  var ACCENT_RGB = '{_hex_to_rgb(accent)}';
  var BASE_RATIOS = {base_ratios_json};

  function fmtVal(v) {{
    return '{fmt_val(0)}'.replace('0.00', v.toFixed(2));
  }}

  function getBanda(v) {{
    if (IS_EF) {{
      if (v >= 97) return 'Exitosa';
      if (v >= 93) return 'Aceptable';
      if (v >= 85) return 'Revisar';
      if (v >= 60) return 'Crítica';
      return 'Súper Crítica';
    }} else {{
      if (v >= 2.0) return 'Exitosa';
      if (v >= 1.5) return 'Aceptable';
      if (v >= 0.8) return 'Revisar';
      if (v > 0)   return 'Crítica';
      return 'Sin Conversión';
    }}
  }}

  function buildSerie(w_curr, w_prev) {{
    var w_idx = VALS_DEF.length - 1;
    var serie = VALS_DEF.slice(0, w_idx).concat([w_curr]);
    if (isNaN(w_prev)) w_prev = w_curr;
    return serie;
  }}

  // ── Canvas: escala LOCAL (Eficacia y ConvRate: mayor = arriba = mejor) ───
  function drawCanvas(vals) {{
    var el = document.getElementById(CID);
    if (!el) return;
    var dpr = window.devicePixelRatio || 1;
    var W   = Math.max(el.parentElement.offsetWidth - 2, 100);
    var H   = 76;
    el.width = W*dpr; el.height = H*dpr;
    el.style.width = W+'px'; el.style.height = H+'px';
    var ctx = el.getContext('2d');
    ctx.scale(dpr, dpr);
    var n = vals.length;
    var pL=10, pR=38, pT=8, pB=18, cw=W-pL-pR, ch=H-pT-pB;

    // Ambos: mayor = mejor, así que valor mayor arriba
    var vMin = Math.min.apply(null,vals);
    var vMax = Math.max.apply(null,vals);
    vMax = Math.max(vMax, TARGET) * 1.005;
    vMin = vMin * 0.995;

    function xOf(i) {{ return pL + (i/(n-1)) * cw; }}
    function yOf(v) {{
      return pT + ch - (v - vMin) / (vMax - vMin) * ch;
    }}

    // Línea target
    var ty = yOf(TARGET);
    ctx.save(); ctx.setLineDash([3,4]);
    ctx.strokeStyle = 'rgba(' + ACCENT_RGB + ',0.30)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pL,ty); ctx.lineTo(pL+cw,ty); ctx.stroke();
    ctx.restore();
    ctx.fillStyle = 'rgba(' + ACCENT_RGB + ',0.50)';
    ctx.font = '8px Geist,sans-serif'; ctx.textAlign = 'left';
    var tLabel = IS_EF ? 'T:97%' : 'T:2%';
    ctx.fillText(tLabel, pL+cw+3, ty+3);

    // Área relleno
    var grad = ctx.createLinearGradient(0, pT, 0, pT+ch);
    var r = parseInt(ACCENT_HEX.slice(1,3),16);
    var g = parseInt(ACCENT_HEX.slice(3,5),16);
    var b = parseInt(ACCENT_HEX.slice(5,7),16);
    grad.addColorStop(0, 'rgba('+r+','+g+','+b+',0.16)');
    grad.addColorStop(1, 'rgba('+r+','+g+','+b+',0)');
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    ctx.lineTo(xOf(n-1), pT+ch); ctx.lineTo(xOf(0), pT+ch);
    ctx.closePath(); ctx.fill();

    // Línea
    ctx.strokeStyle = ACCENT_HEX; ctx.lineWidth = 1.75;
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    ctx.stroke();

    // Puntos
    for (var i=0; i<n; i++) {{
      var isLast = (i === n-1);
      var alpha  = isLast ? 1 : (0.25 + 0.55*(i/(n-1)));
      ctx.beginPath();
      ctx.arc(xOf(i), yOf(vals[i]), isLast ? 3.5 : 2, 0, Math.PI*2);
      ctx.fillStyle = isLast ? ACCENT_HEX : 'rgba('+r+','+g+','+b+','+alpha.toFixed(2)+')';
      ctx.fill();
      if (isLast) {{ ctx.strokeStyle='#F8F4EC'; ctx.lineWidth=1.5; ctx.stroke(); }}
    }}

    // Labels X (MEJORADO: más legible)
    ctx.font = '8px Geist,sans-serif'; ctx.textAlign = 'center';
    for (var i=0; i<n; i++) {{
      if (i===0 || i===Math.floor(n/2) || i===n-1) {{
        ctx.fillStyle = i===n-1 ? ACCENT_HEX : 'rgba(100,90,80,0.80)';  // ← 0.80 en lugar de 0.55
        ctx.fillText(SEMANAS[i], xOf(i), H-3);
      }}
    }}
  }}

  // ── Sparkline: escala GLOBAL ───────────────────────────────────────────
  function updateSpark(vals) {{
    var spEl = document.getElementById('hist-'+CID+'-spark');
    if (!spEl) return;
    var html = '';
    vals.forEach(function(v, i) {{
      var ratio  = Math.min(v / BAR_CEIL, 1.0);
      var h      = Math.max(Math.round(2 + 16*ratio), 2);
      var alpha  = (0.20 + 0.75*ratio).toFixed(2);
      var isLast = (i === vals.length-1);
      var bg     = isLast ? ACCENT_HEX : 'rgba('+ACCENT_RGB+','+alpha+')';
      html += '<div style="flex:1;background:'+bg+';height:'+h+'px;border-radius:1px 1px 0 0;" title="'+SEMANAS[i]+': '+fmtVal(v)+'"></div>';
    }});
    spEl.innerHTML = html;
  }}

  // ── Actualizar métricas DOM ────────────────────────────────────────────
  function updateMetrics(vals, label) {{
    var vMin  = Math.min.apply(null, vals);
    var vMax  = Math.max.apply(null, vals);
    var vAvg  = vals.reduce(function(a,b){{return a+b;}},0)/vals.length;
    var vCurr = vals[vals.length-1];
    var banda = getBanda(vCurr);
    var bc    = BC[banda] || BC['Sin Conversión'];

    var lEl = document.getElementById('hist-'+CID+'-label');
    if (lEl) lEl.textContent = label || 'Global';

    var el;
    el = document.getElementById('hist-'+CID+'-actual');
    if (el) el.textContent = fmtVal(vCurr);
    el = document.getElementById('hist-'+CID+'-best');
    if (el) el.textContent = fmtVal(vMax);
    el = document.getElementById('hist-'+CID+'-worst');
    if (el) el.textContent = fmtVal(vMin);
    el = document.getElementById('hist-'+CID+'-avg');
    if (el) el.textContent = fmtVal(vAvg);

    var bbEl = document.getElementById('hist-'+CID+'-banda-box');
    var bEl  = document.getElementById('hist-'+CID+'-banda');
    if (bbEl) {{ bbEl.style.background=bc.bg; bbEl.style.borderColor=bc.fg; bbEl.style.color=bc.fg; }}
    if (bEl)  {{ bEl.textContent=banda; bEl.style.color=bc.fg; }}

    el = document.getElementById('hist-'+CID+'-banda-footer');
    if (el) {{ el.textContent=banda.toUpperCase(); el.style.color=bc.footer; }}

    updateSpark(vals);
  }}

  // ── Clicks ────────────────────────────────────────────────────────────
  function attachListeners() {{
    var histEl = document.getElementById('hist-'+CID);
    if (!histEl) return;
    var card = histEl.closest('.kpi-card');
    if (!card) return;
    function resetToGlobal() {{
      card.querySelectorAll('[data-hist-w20],[data-hist-w21]').forEach(function(r) {{
        r.style.background=''; r.removeAttribute('data-selected');
      }});
      updateMetrics(VALS_DEF, 'Global');
      updateSpark(VALS_DEF);
    }}
    card.addEventListener('click', function(e) {{
      // Detectar dinámicamente: buscar data-hist-w20, data-hist-w19, etc.
      var row = e.target.closest('[data-hist-w20],[data-hist-w21]');
      if (!row) return;
      
      // Prioridad: data-hist-w20 (actual W20), fallback a data-hist-w21
      var w_curr = parseFloat(row.getAttribute('data-hist-w20') || row.getAttribute('data-hist-w21'));
      var w_prev = parseFloat(row.getAttribute('data-hist-w19') || row.getAttribute('data-hist-w20') || w_curr);
      var lbl = row.getAttribute('data-hist-label') || '';
      if (isNaN(w_curr)) return;
      
      card.querySelectorAll('[data-hist-w20],[data-hist-w21]').forEach(function(r) {{ r.style.background=''; }});
      row.style.background = 'var(--accent-soft)';
      var serie = buildSerie(w_curr, isNaN(w_prev) ? w_curr : w_prev);
      drawCanvas(serie);
      updateMetrics(serie, lbl);
    }});
  }}

  // ── Init ──────────────────────────────────────────────────────────────
  function init() {{
    drawCanvas(VALS_DEF);
    updateMetrics(VALS_DEF, 'Global');
    attachListeners();
  }}
  if (document.readyState==='loading')
    document.addEventListener('DOMContentLoaded', init);
  else
    requestAnimationFrame(init);
}})();
</script>'''
