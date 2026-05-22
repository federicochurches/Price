"""
historico_module_rnd.py — Módulo histórico reactivo para RND.
Dos métricas con lógica diferenciada:
  - NoDispo: escala INVERTIDA (menor = mejor), target < 5%, accent magenta #EA0074
  - IPM:     escala normal (mayor = mejor), target ≥ $650, accent amber #A86A1D
"""
import json as _json

RND_ACCENT  = '#EA0074'   # magenta principal RND
IPM_ACCENT  = '#A86A1D'   # amber IPM

# Colores del sistema D (idénticos a render_helpers.py)
_BANDA_COLORS = {
    'Exitosa':        {'bg': '#E8F7FD', 'fg': '#0D7A99', 'bd': '#4FC3F4',  'footer': '#0D7A99'},
    'Aceptable':      {'bg': '#EDE8F7', 'fg': '#5C469C', 'bd': '#5C469C',  'footer': '#5C469C'},
    'Revisar':        {'bg': '#FFF4E0', 'fg': '#A86A1D', 'bd': '#D4A878',  'footer': '#A86A1D'},
    'Crítica':        {'bg': '#FCE4F1', 'fg': '#C0392B', 'bd': '#C0392B',  'footer': '#C0392B'},
    'Súper Crítica':  {'bg': '#161616', 'fg': '#FFFFFF', 'bd': '#161616',  'footer': '#161616'},
    'Sin Conversión': {'bg': '#F2EEE6', 'fg': '#8A8377', 'bd': '#8A8377',  'footer': '#8A8377'},
}
_BANDA_COLORS_JS = {
    k: {'bg': v['bg'], 'fg': v['fg'], 'footer': v['footer']}
    for k, v in _BANDA_COLORS.items()
}


def render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id,
                          current_week='W20', hist_vals=None, global_ceil=None):
    """
    IMPORTANTE: current_week debe ser la semana ACTUAL, NO la próxima.
    Ejemplo: Si hoy es W20, pasar 'W20' (no 'W21')
    El módulo genera 8 semanas: W(N-7) a W(N)
    """
    is_nodispo = metric_type == 'nodispo'
    target     = 0.05  if is_nodispo else 650.0   # < 5% NoDispo | ≥ $650 IPM
    bar_ceil   = global_ceil if global_ceil is not None else (0.60 if is_nodispo else 3000.0)
    accent     = RND_ACCENT if is_nodispo else IPM_ACCENT

    # ── Generar semanas dinámicas ───────────────────────────────────────────
    # Extraer número de week (ej: 'W20' → 20)
    try:
        week_num = int(current_week[1:])
    except:
        week_num = 20
    
    # Generar 8 semanas previas (ej: W20 actual → W13-W20)
    week_start = week_num - 7
    semanas = [f'W{week_start + i}' for i in range(8)]  # W13-W20 si current_week='W20'

    # Datos ficticios W(N-7)-W(N)
    _FICTICIOS = {
        'nodispo': {
            'global': [8.2, 7.8, 8.5, 8.1, 7.9, 8.3, 8.0, 7.9],
            'op':     [9.1, 8.8, 9.3, 8.9, 9.0, 9.2, 8.8, 8.9],
            'cug':    [6.5, 6.2, 6.8, 6.4, 6.3, 6.6, 6.5, 6.4],
            'b2c':    [5.1, 4.9, 5.3, 5.0, 5.2, 5.1, 4.8, 5.0],
        },
        'ipm': {
            'global': [820, 840, 810, 860, 830, 850, 870, 845],
            'op':     [920, 940, 910, 960, 930, 950, 970, 955],
            'cug':    [1100, 1120, 1090, 1140, 1110, 1130, 1150, 1135],
            'b2c':    [580, 600, 570, 610, 590, 605, 615, 605],
        },
    }

    scope = 'global'
    for k in ('op', 'cug', 'b2c'):
        if k in canvas_id:
            scope = k; break

    w13_w20 = hist_vals if hist_vals else _FICTICIOS[metric_type][scope]

    # Convertir val_actual a la unidad de display
    # nodispo: val en [0,1] → mostrar en %, hist en %
    # ipm: val ya en USD/M
    if is_nodispo:
        w20_val      = round(val_actual * 100, 2)
        vals_default = [round(v, 2) for v in w13_w20]  # todo en %, 8 valores
        vals_default[-1] = w20_val  # reemplazar último con valor actual
        fmt_val      = lambda v: f'{v:.2f}%'
        target_disp  = '< 5%'
        unit         = '%'
    else:
        w20_val      = round(float(val_actual), 1)
        vals_default = [round(v, 1) for v in w13_w20]  # todo en USD/M, 8 valores
        vals_default[-1] = w20_val  # reemplazar último con valor actual
        fmt_val      = lambda v: f'${v:,.0f}'
        target_disp  = '≥ $650'
        unit         = ' USD/M'

    semanas_list = semanas  # usar semanas generadas dinámicamente

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
            bg     = accent if i == 7 else f'rgba({_hex_to_rgb(accent)},{alpha})'
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
    base_ratios      = [round(v / (w13_w20[-1] + 0.0001), 6) for v in w13_w20[:7]]
    base_ratios_json = _json.dumps(base_ratios)

    # Canvas: para NoDispo invertimos la lectura (target arriba = malo)
    # línea target: en nodispo aparece abajo (lo bueno), en IPM arriba
    canvas_target = target * 100 if is_nodispo else target

    return f'''<div id="hist-{canvas_id}"
     style="margin-top:6px;padding:12px 14px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;">

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
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">{"Mín 8W" if is_nodispo else "Máx 8W"}</div>
      <div id="hist-{canvas_id}-best" style="font-size:13px;font-weight:700;color:#2F6C34;margin-top:2px;">{fmt_val(v_min) if is_nodispo else fmt_val(v_max)}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">{"Máx 8W" if is_nodispo else "Mín 8W"}</div>
      <div id="hist-{canvas_id}-worst" style="font-size:13px;font-weight:700;color:#C0392B;margin-top:2px;">{fmt_val(v_max) if is_nodispo else fmt_val(v_min)}</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Prom 8W</div>
      <div id="hist-{canvas_id}-avg" style="font-size:13px;font-weight:700;color:var(--ink);margin-top:2px;">{avg_str}</div>
    </div>
    <div id="hist-{canvas_id}-banda-box"
         style="text-align:center;padding:6px 2px;border-radius:3px;background:{b_bg};border:1px solid {b_bd};">
      <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:{b_fg};">Banda</div>
      <div id="hist-{canvas_id}-banda" style="font-size:10px;font-weight:700;color:{b_fg};margin-top:2px;line-height:1.2;">{banda_actual}</div>
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
    <span id="hist-{canvas_id}-banda-footer" style="font-size:8px;font-weight:700;color:{b_footer};">Banda: {banda_actual}</span>
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
    for (var i=0; i<n; i++) {{
      var isLast = (i === n-1);
      var alpha  = isLast ? 1 : (0.25 + 0.55*(i/(n-1)));
      ctx.beginPath();
      ctx.arc(xOf(i), yOf(vals[i]), isLast ? 3.5 : 2, 0, Math.PI*2);
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
    if (el) {{ el.textContent='Banda: '+banda; el.style.color=bc.footer; }}

    updateSpark(vals);
  }}

  // ── Clicks ────────────────────────────────────────────────────────────
  function attachListeners() {{
    var histEl = document.getElementById('hist-'+CID);
    if (!histEl) return;
    var card = histEl.closest('.kpi-card');
    if (!card) return;
    card.addEventListener('click', function(e) {{
      var row = e.target.closest('[data-hist-w21]');
      if (!row) return;
      var w21 = parseFloat(row.getAttribute('data-hist-w21'));
      var w20 = parseFloat(row.getAttribute('data-hist-w20') || w21);
      var lbl = row.getAttribute('data-hist-label') || '';
      if (isNaN(w21)) return;
      card.querySelectorAll('[data-hist-w21]').forEach(function(r) {{ r.style.background=''; }});
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
  }}
  if (document.readyState==='loading')
    document.addEventListener('DOMContentLoaded', init);
  else
    requestAnimationFrame(init);
}})();
</script>'''

