"""
historico_module_rnd.py — Módulo histórico reactivo para RND (v2 W20 sesión 6).
- Datos reales W16-W20 (extraídos de pickles rnd_w{16-20}_data.pkl)
- Ventana de 5 semanas (W16-W20) → el último valor es la semana actual del reporte
Dos métricas con lógica diferenciada:
  - NoDispo: escala INVERTIDA (menor = mejor), target < 5%, accent magenta #EA0074
  - IPM:     escala normal (mayor = mejor), target ≥ $650, accent cyan #4FC3F4 (Arctic Blue)
"""
import json as _json
from historico_data import get_serie, SEMANAS

RND_ACCENT  = '#EA0074'   # magenta principal RND
IPM_ACCENT  = '#4FC3F4'   # cyan corporativo (Arctic Blue) · acento IPM

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


def render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id,
                          current_week='W20', hist_vals=None, global_ceil=None):
    """
    metric_type  : 'nodispo' | 'ipm'
    banda_actual : string banda actual (sistema D)
    val_actual   : float (nodispo: [0,1]; ipm: USD/M directo) — valor de la semana ACTUAL
    canvas_id    : ID único del canvas (su sufijo determina el scope: -global-, -op-, -cug-, -b2c-)
    current_week : DEPRECATED — se ignora. Las semanas vienen de historico_data.SEMANAS.
    hist_vals    : DEPRECATED — se ignora. Los valores históricos vienen de historico_data.HIST_DATA.
    global_ceil  : techo global para las barras.
    """
    is_nodispo = metric_type == 'nodispo'
    target     = 0.05  if is_nodispo else 650.0   # < 5% NoDispo | ≥ $650 IPM
    bar_ceil   = global_ceil if global_ceil is not None else (0.60 if is_nodispo else 3000.0)
    accent     = RND_ACCENT if is_nodispo else IPM_ACCENT

    # Semanas desde historico_data (ventana fija W16-W20)
    semanas    = list(SEMANAS)   # ['W16','W17','W18','W19','W20']
    n_weeks    = len(semanas)
    idx_current = n_weeks - 1

    # Determinar scope desde canvas_id
    scope = 'global'
    for k in ('op', 'cug', 'b2c'):
        if k in canvas_id:
            scope = k; break

    # Convertir val_actual a la unidad de display y obtener serie completa
    # nodispo: val en [0,1] → mostrar en %, hist ya en %
    # ipm: val ya en USD/M, hist en USD/M
    if is_nodispo:
        w_current_val = round(val_actual * 100, 2)
        vals_default  = get_serie('rnd', 'nodispo', scope, w_current_val)
        vals_default  = [round(v, 2) for v in vals_default]
        fmt_val       = lambda v: f'{v:.2f}%'
        target_disp   = '< 5%'
        unit          = '%'
    else:
        w_current_val = round(float(val_actual), 1)
        vals_default  = get_serie('rnd', 'ipm', scope, w_current_val)
        vals_default  = [round(v, 1) for v in vals_default]
        fmt_val       = lambda v: f'${v:,.0f}'
        target_disp   = '≥ $650'
        unit          = ' USD/M'

    semanas_list = semanas

    v_min  = min(vals_default); v_max = max(vals_default)
    v_avg  = sum(vals_default) / len(vals_default)
    v_curr = vals_default[-1];  v_prev = vals_default[-2]
    delta  = v_curr - v_prev

    bc       = _BANDA_COLORS.get(banda_actual, _BANDA_COLORS['Sin Conversión'])
    b_fg     = bc['fg']; b_bg = bc['bg']; b_bd = bc['bd']; b_footer = bc['footer']

    # Sparkline: escala global
    # NoDispo invertida: barra más alta = peor (más NoDispo)
    # IPM normal: barra más alta = mejor
    def _sparkbars(vals):
        bars = ''
        for i, v in enumerate(vals):
            if is_nodispo:
                # Invertido: más NoDispo → barra más alta y más intensa
                ratio = min(v / (bar_ceil * 100), 1.0) if bar_ceil > 0 else 0.5
            else:
                ratio = min(v / bar_ceil, 1.0) if bar_ceil > 0 else 0.5
            height = max(int(2 + 16 * ratio), 2)
            alpha  = round(0.20 + 0.75 * ratio, 2)
            bg     = accent if i == idx_current else f'rgba({_hex_to_rgb(accent)},{alpha})'
            bars += (f'<div style="flex:1;background:{bg};height:{height}px;'
                     f'border-radius:1px 1px 0 0;" title="{semanas_list[i]}: {fmt_val(v)}"></div>')
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
    semanas_json     = _json.dumps(semanas_list)
    banda_colors_js  = _json.dumps(_BANDA_COLORS_JS)
    base_ratios      = [round(v / (vals_default[-1] + 0.0001), 6) for v in vals_default[:-1]]
    base_ratios_json = _json.dumps(base_ratios)

    # Canvas: para NoDispo invertimos la lectura (target arriba = malo)
    # línea target: en nodispo aparece abajo (lo bueno), en IPM arriba
    canvas_target = target * 100 if is_nodispo else target

    return f'''<div id="hist-{canvas_id}"
     style="margin-top:16px;padding:12px 14px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;">

  <!-- Header -->
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
    <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">
      Evolución Histórica ·
      <span id="hist-{canvas_id}-label" style="color:var(--ink-muted);font-weight:600;cursor:pointer;text-decoration:underline dotted;text-underline-offset:2px;" title="Ver datos globales">Global</span>
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
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">{"Mín 5W" if is_nodispo else "Máx 5W"}</div>
      <div id="hist-{canvas_id}-best" style="font-size:13px;font-weight:700;color:#2F6C34;margin-top:2px;">{fmt_val(v_min) if is_nodispo else fmt_val(v_max)}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">{"Máx 5W" if is_nodispo else "Mín 5W"}</div>
      <div id="hist-{canvas_id}-worst" style="font-size:13px;font-weight:700;color:#C0392B;margin-top:2px;">{fmt_val(v_max) if is_nodispo else fmt_val(v_min)}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Prom 5W</div>
      <div id="hist-{canvas_id}-avg" style="font-size:13px;font-weight:700;color:var(--ink);margin-top:2px;">{avg_str}</div>
    </div>
    <div id="hist-{canvas_id}-banda-box"
         style="display:flex;align-items:center;justify-content:center;text-align:center;padding:6px 2px;border-radius:3px;background:{b_bg};border:1px solid {b_bd};">
      <div id="hist-{canvas_id}-banda" style="font-size:11px;font-weight:700;color:{b_fg};margin-top:2px;line-height:1.2;text-transform:uppercase;letter-spacing:.04em;">{banda_actual.upper()}</div>
    </div>
  </div>

  <!-- Sparkline: escala global -->
  <div style="margin-top:10px;">
    <div style="font-size:7px;color:var(--ink-muted);font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">
      {"Severidad vs universo global (↑ más NoDispo)" if is_nodispo else "Posición vs target global"}
    </div>
    <div id="hist-{canvas_id}-spark"
         style="display:flex;align-items:flex-end;gap:2px;height:18px;">{spark_html}</div>
    <div style="display:flex;justify-content:space-between;margin-top:2px;">
      <span style="font-size:7px;color:var(--ink-muted);">{semanas[0]}</span>
      <span style="font-size:7px;color:{accent};font-weight:700;">{semanas[-1]}</span>
    </div>
  </div>

  <!-- Footer -->
  <div style="display:flex;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:1px solid var(--rule-soft);">
    <span id="hist-{canvas_id}-banda-footer" style="font-size:8px;font-weight:700;color:{b_footer};">{banda_actual.upper()}</span>
    <span id="hist-{canvas_id}-trend-footer" style="font-size:8px;color:var(--ink-muted);">Target: {target_disp}</span>
  </div>
</div>

<script>
(function(){{
  var CID        = '{canvas_id}';
  var METRIC     = '{metric_type}';
  var IS_ND      = {str(is_nodispo).lower()};
  var TARGET     = {canvas_target};
  var BAR_CEIL   = {bar_ceil * 100 if is_nodispo else bar_ceil};
  var ACCENT_HEX = '{accent}';
  var SEMANAS    = {semanas_json};
  var VALS_DEF   = {vals_json};
  var BASE_RATIOS= {base_ratios_json};
  var BC         = {banda_colors_js};

  // ── Banda según valor ──────────────────────────────────────────────────
  function getBanda(val) {{
    if (IS_ND) {{
      var pct = val / 100;
      if (pct > 0.60) return 'Súper Crítica';
      if (pct > 0.20) return 'Crítica';
      if (pct > 0.05) return 'Revisar';
      if (pct > 0.03) return 'Aceptable';
      return 'Exitosa';
    }} else {{
      if (val === 0)   return 'Sin Conversión';
      if (val < 199)   return 'Crítica';
      if (val < 500)   return 'Revisar';
      if (val < 650)   return 'Aceptable';
      return 'Exitosa';
    }}
  }}

  function hexToRgb(h) {{
    h = h.replace('#','');
    return parseInt(h.slice(0,2),16)+','+parseInt(h.slice(2,4),16)+','+parseInt(h.slice(4,6),16);
  }}
  var ACCENT_RGB = hexToRgb(ACCENT_HEX);

  function fmtVal(v) {{
    if (IS_ND) return v.toFixed(2).replace('.',',') + '%';
    return '$' + Math.round(v).toLocaleString('es-AR');
  }}

  // ── Serie para elemento clickeado ─────────────────────────────────────
  function buildSerie(w21, w20) {{
    var serie = BASE_RATIOS.map(function(r) {{
      return parseFloat((r * w20).toFixed(2));
    }});
    serie.push(parseFloat(w20.toFixed(2)));
    serie.push(parseFloat(w21.toFixed(2)));
    return serie;
  }}

  // Estado de puntos para tooltip
  var pointsCache = [];

  // ── Canvas: escala LOCAL ───────────────────────────────────────────────
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

    // NoDispo: invertimos Y (menor valor = arriba = bueno)
    var vMin = Math.min.apply(null,vals);
    var vMax = Math.max.apply(null,vals);
    if (IS_ND) {{
      // incluir target en el rango para que sea visible
      vMin = Math.min(vMin, TARGET) * 0.99;
      vMax = vMax * 1.005;
    }} else {{
      vMax = Math.max(vMax, TARGET) * 1.005;
      vMin = vMin * 0.995;
    }}

    function xOf(i) {{ return pL + (i/(n-1)) * cw; }}
    function yOf(v) {{
      // NoDispo: valor menor → más arriba (mejor)
      // IPM: valor mayor → más arriba (mejor)
      if (IS_ND) {{
        return pT + (v - vMin) / (vMax - vMin) * ch;  // invertido
      }} else {{
        return pT + ch - (v - vMin) / (vMax - vMin) * ch;
      }}
    }}

    // Línea target
    var ty = yOf(TARGET);
    ctx.save(); ctx.setLineDash([3,4]);
    ctx.strokeStyle = 'rgba(' + ACCENT_RGB + ',0.30)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pL,ty); ctx.lineTo(pL+cw,ty); ctx.stroke();
    ctx.restore();
    ctx.fillStyle = 'rgba(' + ACCENT_RGB + ',0.50)';
    ctx.font = '8px Geist,sans-serif'; ctx.textAlign = 'left';
    var tLabel = IS_ND ? 'T:5%' : 'T:$650';
    ctx.fillText(tLabel, pL+cw+3, ty+3);

    // Área relleno
    var grad = ctx.createLinearGradient(0, pT, 0, pT+ch);
    var r = parseInt(ACCENT_HEX.slice(1,3),16);
    var g = parseInt(ACCENT_HEX.slice(3,5),16);
    var b = parseInt(ACCENT_HEX.slice(5,7),16);
    grad.addColorStop(0, 'rgba('+r+','+g+','+b+',0.16)');
    grad.addColorStop(1, 'rgba('+r+','+g+','+b+',0)');
    // NoDispo: relleno hacia abajo (zona mala = abajo)
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    if (IS_ND) {{
      ctx.lineTo(xOf(n-1), pT); ctx.lineTo(xOf(0), pT);
    }} else {{
      ctx.lineTo(xOf(n-1), pT+ch); ctx.lineTo(xOf(0), pT+ch);
    }}
    ctx.closePath(); ctx.fill();

    // Línea
    ctx.strokeStyle = ACCENT_HEX; ctx.lineWidth = 1.75;
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    ctx.stroke();

    // Puntos
    pointsCache = [];
    for (var i=0; i<n; i++) {{
      var isLast = (i === n-1);
      var alpha  = isLast ? 1 : (0.25 + 0.55*(i/(n-1)));
      var px = xOf(i), py = yOf(vals[i]);
      pointsCache.push({{x: px, y: py, val: vals[i], semana: SEMANAS[i]}});
      ctx.beginPath();
      ctx.arc(px, py, isLast ? 3.5 : 2, 0, Math.PI*2);
      ctx.fillStyle = isLast ? ACCENT_HEX : 'rgba('+r+','+g+','+b+','+alpha.toFixed(2)+')';
      ctx.fill();
      if (isLast) {{ ctx.strokeStyle='#F8F4EC'; ctx.lineWidth=1.5; ctx.stroke(); }}
    }}

    // Labels X
    ctx.font = '8px Geist,sans-serif'; ctx.textAlign = 'center';
    for (var i=0; i<n; i++) {{
      if (i===0 || i===Math.floor(n/2) || i===n-1) {{
        ctx.fillStyle = i===n-1 ? ACCENT_HEX : 'rgba(100,90,80,0.80)';  // ← 0.80 (más legible)
        ctx.fillText(SEMANAS[i], xOf(i), H-3);
      }}
    }}
  }}

  // Tooltip al hover
  function attachTooltip() {{
    var el = document.getElementById(CID);
    if (!el) return;
    var tt = el.parentElement.querySelector('.hist-tooltip-' + CID);
    if (!tt) {{
      tt = document.createElement('div');
      tt.className = 'hist-tooltip-' + CID;
      tt.style.cssText = 'position:absolute;pointer-events:none;background:#161616;color:#FAF7F2;padding:5px 9px;border-radius:3px;font-size:10px;font-weight:600;letter-spacing:.02em;white-space:nowrap;transform:translate(-50%,-115%);z-index:50;display:none;box-shadow:0 2px 6px rgba(0,0,0,.20);';
      el.parentElement.style.position = 'relative';
      el.parentElement.appendChild(tt);
    }}
    el.addEventListener('mousemove', function(e) {{
      var rect = el.getBoundingClientRect();
      var mx = e.clientX - rect.left;
      var my = e.clientY - rect.top;
      var best = null, bestDist = 14;
      for (var i=0; i<pointsCache.length; i++) {{
        var p = pointsCache[i];
        var d = Math.sqrt((p.x-mx)*(p.x-mx) + (p.y-my)*(p.y-my));
        if (d < bestDist) {{ bestDist = d; best = p; }}
      }}
      if (best) {{
        var fmtVal;
        if (IS_ND) {{
          fmtVal = best.val.toFixed(2).replace('.', ',') + '%';
        }} else {{
          fmtVal = '$' + best.val.toFixed(0).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, '.');
        }}
        tt.textContent = best.semana + ' · ' + fmtVal;
        tt.style.left = best.x + 'px';
        tt.style.top = best.y + 'px';
        tt.style.display = 'block';
        el.style.cursor = 'crosshair';
      }} else {{
        tt.style.display = 'none';
        el.style.cursor = 'default';
      }}
    }});
    el.addEventListener('mouseleave', function() {{ tt.style.display = 'none'; el.style.cursor = 'default'; }});
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
    // best = mín para nodispo, máx para ipm
    el = document.getElementById('hist-'+CID+'-best');
    if (el) el.textContent = fmtVal(IS_ND ? vMin : vMax);
    el = document.getElementById('hist-'+CID+'-worst');
    if (el) el.textContent = fmtVal(IS_ND ? vMax : vMin);
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
      card.querySelectorAll('[data-hist-w20],[data-hist-w21]').forEach(function(r) {{ r.style.background=''; r.removeAttribute('data-selected'); }});
      drawCanvas(VALS_DEF);
      updateMetrics(VALS_DEF, 'Global');
      updateSpark(VALS_DEF);
    }}
    card.addEventListener('click', function(e) {{
      if (e.target.id === 'hist-'+CID+'-label') {{ resetToGlobal(); return; }}
      var row = e.target.closest('[data-hist-w21]');
      if (!row) return;
      if (row.getAttribute('data-selected') === '1') {{ resetToGlobal(); return; }}
      var w21 = parseFloat(row.getAttribute('data-hist-w21'));
      var w20 = parseFloat(row.getAttribute('data-hist-w20') || w21);
      var lbl = row.getAttribute('data-hist-label') || '';
      if (isNaN(w21)) return;
      card.querySelectorAll('[data-hist-w21]').forEach(function(r) {{ r.style.background=''; r.removeAttribute('data-selected'); }});
      row.setAttribute('data-selected','1');
      row.style.background = 'var(--accent-soft)';
      var serie = buildSerie(w21, isNaN(w20) ? w21 : w20);
      drawCanvas(serie);
      updateMetrics(serie, lbl);
    }});
  }}

  // ── Init ──────────────────────────────────────────────────────────────
  function init() {{
    drawCanvas(VALS_DEF);
    updateMetrics(VALS_DEF, 'Global');
    attachListeners();
    attachTooltip();
    // Redibujar si el canvas está dentro de un <details> cerrado al cargar
    var el = document.getElementById(CID);
    if (el) {{
      var det = el.closest('details');
      if (det) {{
        det.addEventListener('toggle', function() {{
          if (det.open) {{ requestAnimationFrame(function() {{ drawCanvas(VALS_DEF); }}); }}
        }});
      }}
    }}
  }}

  // Listeners de eventos custom (se registran siempre, no dependen de readyState)
  document.addEventListener('hist-update', function(e) {{
    if (e.detail.cid !== CID) return;
    var w_curr = e.detail.w_curr;
    var w_prev = e.detail.w_prev;
    var lbl    = e.detail.label || '';
    var vals   = VALS_DEF.slice();
    vals[vals.length-1] = w_curr;
    vals[vals.length-2] = w_prev;
    drawCanvas(vals);
    updateSpark(vals);
    updateMetrics(vals, lbl);
  }});
  document.addEventListener('hist-reset', function(e) {{
    if (e.detail.cid !== CID) return;
    drawCanvas(VALS_DEF);
    updateSpark(VALS_DEF);
    updateMetrics(VALS_DEF, 'Global');
  }});

  // Arranque del módulo: si el DOM aún está cargando esperamos, si no lo iniciamos ya
  if (document.readyState==='loading')
    document.addEventListener('DOMContentLoaded', init);
  else
    requestAnimationFrame(init);
}})();
</script>'''

