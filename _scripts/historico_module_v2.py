"""
render_historico_cr — Módulo histórico reactivo v4.
- Título: "Evolución Histórica"
- Sin pill WoW delta en el header
- Badge Súper Crítica: bg oscuro + texto blanco
- Footer texto siempre legible sobre fondo claro (usa fg_footer distinto de fg_badge en SC)
- Barras: escala global de la card (valor vs techo global = target o max P90)
- Curvas: escala local del elemento seleccionado
"""
import json as _json

# ── Colores exactos del sistema D (render_helpers.py) ─────────────────────────
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


def render_historico_cr(metric_type, banda_actual, val_actual, canvas_id,
                         hist_vals=None, global_ceil=None):
    """
    metric_type : 'eficacia' | 'convrate'
    banda_actual: string banda actual (sistema D)
    val_actual  : float [0,1]
    canvas_id   : ID único del canvas
    hist_vals   : lista 7 floats W14-W20 en % (None = ficticios)
    global_ceil : techo global para las barras (ej: 97.0 para eficacia).
                  Si None, usa el target.
    """
    target = 97.0 if metric_type == 'eficacia' else 2.5
    bar_ceil = global_ceil if global_ceil is not None else target

    _FICTICIOS = {
        'eficacia': {
            'global': [91.8, 92.3, 92.7, 92.1, 93.0, 93.4, 93.8],
            'op':     [93.1, 93.8, 94.2, 93.6, 94.5, 94.8, 95.1],
            'cug':    [94.5, 95.0, 95.3, 94.8, 95.6, 95.9, 96.2],
            'b2c':    [88.2, 89.1, 88.7, 89.5, 90.1, 90.4, 91.0],
        },
        'convrate': {
            'global': [1.18, 1.14, 1.22, 1.19, 1.15, 1.20, 1.24],
            'op':     [1.42, 1.38, 1.51, 1.45, 1.39, 1.47, 1.52],
            'cug':    [2.31, 2.28, 2.45, 2.38, 2.51, 2.44, 2.58],
            'b2c':    [0.61, 0.58, 0.64, 0.62, 0.59, 0.63, 0.66],
        },
    }

    scope = 'global'
    for k in ('op', 'cug', 'b2c'):
        if k in canvas_id:
            scope = k; break

    w14_w20      = hist_vals if hist_vals else _FICTICIOS[metric_type][scope]
    w21_val      = round(val_actual * 100, 2)
    vals_default = w14_w20 + [w21_val]
    semanas      = ['W14', 'W15', 'W16', 'W17', 'W18', 'W19', 'W20', 'W21']

    v_min  = min(vals_default); v_max = max(vals_default)
    v_avg  = sum(vals_default) / len(vals_default)
    v_curr = vals_default[-1]; v_prev = vals_default[-2]
    delta  = v_curr - v_prev

    bc       = _BANDA_COLORS.get(banda_actual, _BANDA_COLORS['Sin Conversión'])
    b_fg     = bc['fg']
    b_bg     = bc['bg']
    b_bd     = bc['bd']
    b_footer = bc['footer']  # siempre legible sobre fondo claro

    # ── Sparkline: escala global (barras vs techo global) ─────────────────────
    def _sparkbars(vals, ceil):
        bars = ''
        for i, v in enumerate(vals):
            ratio  = min(v / ceil, 1.0) if ceil > 0 else 0.5
            height = max(int(2 + 16 * ratio), 2)
            alpha  = round(0.20 + 0.75 * ratio, 2)
            if i == 7:
                bg = 'var(--accent)'
            else:
                bg = f'rgba(92,70,156,{alpha})'
            bars += (f'<div style="flex:1;background:{bg};'
                     f'height:{height}px;border-radius:1px 1px 0 0;" '
                     f'title="{semanas[i]}: {v:.2f}%"></div>')
        return bars

    spark_html = _sparkbars(vals_default, bar_ceil)

    # Serializar para JS
    vals_json        = _json.dumps(vals_default)
    semanas_json     = _json.dumps(semanas)
    banda_colors_js  = _json.dumps(_BANDA_COLORS_JS)
    base_ratios      = [round(v / (w14_w20[-1] + 0.0001), 6) for v in w14_w20[:6]]
    base_ratios_json = _json.dumps(base_ratios)

    return f'''<div id="hist-{canvas_id}"
     style="margin-top:16px;padding:12px 14px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;">

  <!-- Header: título + label elemento seleccionado -->
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
    <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">
      Evolución Histórica ·
      <span id="hist-{canvas_id}-label" style="color:var(--accent);font-weight:700;">Global</span>
    </span>
  </div>

  <!-- Canvas: curva escala LOCAL del elemento -->
  <div style="width:100%;height:76px;">
    <canvas id="{canvas_id}" style="display:block;width:100%;height:76px;"></canvas>
  </div>

  <!-- 5 métricas -->
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px;margin-top:10px;">
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Actual</div>
      <div id="hist-{canvas_id}-actual" style="font-size:13px;font-weight:700;color:var(--accent);margin-top:2px;">{v_curr:.2f}%</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Máx 8W</div>
      <div id="hist-{canvas_id}-max" style="font-size:13px;font-weight:700;color:#2F6C34;margin-top:2px;">{v_max:.2f}%</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Mín 8W</div>
      <div id="hist-{canvas_id}-min" style="font-size:13px;font-weight:700;color:#C0392B;margin-top:2px;">{v_min:.2f}%</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Prom 8W</div>
      <div id="hist-{canvas_id}-avg" style="font-size:13px;font-weight:700;color:var(--ink);margin-top:2px;">{v_avg:.2f}%</div>
    </div>
    <div id="hist-{canvas_id}-banda-box"
         style="text-align:center;padding:6px 2px;border-radius:3px;background:{b_bg};border:1px solid {b_bd};">
      <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:{b_fg};">Banda</div>
      <div id="hist-{canvas_id}-banda" style="font-size:10px;font-weight:700;color:{b_fg};margin-top:2px;line-height:1.2;">{banda_actual}</div>
    </div>
  </div>

  <!-- Sparkline: barras escala GLOBAL (vs techo card) -->
  <div style="margin-top:10px;">
    <div style="font-size:7px;color:var(--ink-muted);font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">
      Posición vs target global
    </div>
    <div id="hist-{canvas_id}-spark"
         style="display:flex;align-items:flex-end;gap:2px;height:18px;">{spark_html}</div>
    <div style="display:flex;justify-content:space-between;margin-top:2px;">
      <span style="font-size:7px;color:var(--ink-muted);">W14</span>
      <span style="font-size:7px;color:var(--accent);font-weight:700;">W21</span>
    </div>
  </div>

  <!-- Footer -->
  <div style="display:flex;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:1px solid var(--rule-soft);">
    <span id="hist-{canvas_id}-banda-footer" style="font-size:8px;font-weight:700;color:{b_footer};">Banda: {banda_actual}</span>
    <span id="hist-{canvas_id}-trend-footer" style="font-size:8px;color:var(--ink-muted);">Target: ≥{int(target) if target == int(target) else target}%</span>
  </div>
</div>

<script>
(function(){{
  var CID         = '{canvas_id}';
  var METRIC      = '{metric_type}';
  var TARGET      = {target};
  var BAR_CEIL    = {bar_ceil};
  var SEMANAS     = {semanas_json};
  var VALS_DEF    = {vals_json};
  var BASE_RATIOS = {base_ratios_json};
  var BC          = {banda_colors_js};

  // ── Banda según valor ────────────────────────────────────────────────────
  function getBanda(pct) {{
    var v = pct / 100;
    if (METRIC === 'eficacia') {{
      if (v >= 0.97)  return 'Exitosa';
      if (v >= 0.93)  return 'Aceptable';
      if (v >= 0.85)  return 'Revisar';
      if (v >= 0.60)  return 'Crítica';
      return 'Súper Crítica';
    }} else {{
      if (v === 0)    return 'Sin Conversión';
      if (v >= 0.025) return 'Exitosa';
      if (v >= 0.015) return 'Aceptable';
      if (v >= 0.008) return 'Revisar';
      return 'Crítica';
    }}
  }}

  // ── Serie histórica para elemento clickeado ──────────────────────────────
  function buildSerie(w21, w20) {{
    var serie = BASE_RATIOS.map(function(r) {{
      return parseFloat((r * w20).toFixed(2));
    }});
    serie.push(parseFloat(w20.toFixed(2)));
    serie.push(parseFloat(w21.toFixed(2)));
    return serie;
  }}

  // ── Canvas: escala LOCAL del elemento ────────────────────────────────────
  function drawCanvas(vals) {{
    var el = document.getElementById(CID);
    if (!el) return;
    var dpr = window.devicePixelRatio || 1;
    var W   = Math.max(el.parentElement.offsetWidth - 2, 100);
    var H   = 76;
    el.width  = W * dpr; el.height = H * dpr;
    el.style.width = W + 'px'; el.style.height = H + 'px';
    var ctx = el.getContext('2d');
    ctx.scale(dpr, dpr);
    var n = vals.length;
    var pL=10, pR=34, pT=8, pB=18, cw=W-pL-pR, ch=H-pT-pB;
    // Escala local
    var vMin = Math.min.apply(null, vals) * 0.995;
    var vMax = Math.max(Math.max.apply(null, vals), TARGET) * 1.005;
    function xOf(i) {{ return pL + (i / (n-1)) * cw; }}
    function yOf(v) {{ return pT + ch - (v - vMin) / (vMax - vMin) * ch; }}

    // Línea target
    var ty = yOf(TARGET);
    ctx.save(); ctx.setLineDash([3, 4]);
    ctx.strokeStyle = 'rgba(92,70,156,0.28)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pL, ty); ctx.lineTo(pL + cw, ty); ctx.stroke();
    ctx.restore();
    ctx.fillStyle = 'rgba(92,70,156,0.45)';
    ctx.font = '7px Geist,sans-serif'; ctx.textAlign = 'left';
    ctx.fillText('T:' + TARGET + '%', pL + cw + 3, ty + 3);

    // Área relleno
    var grad = ctx.createLinearGradient(0, pT, 0, pT + ch);
    grad.addColorStop(0, 'rgba(92,70,156,0.18)');
    grad.addColorStop(1, 'rgba(92,70,156,0)');
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    ctx.lineTo(xOf(n-1), pT+ch); ctx.lineTo(xOf(0), pT+ch);
    ctx.closePath(); ctx.fill();

    // Línea
    ctx.strokeStyle = '#5C469C'; ctx.lineWidth = 1.75;
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(xOf(0), yOf(vals[0]));
    for (var i=1; i<n; i++) ctx.lineTo(xOf(i), yOf(vals[i]));
    ctx.stroke();

    // Puntos con intensidad creciente
    for (var i=0; i<n; i++) {{
      var isLast = (i === n-1);
      var alpha  = isLast ? 1 : (0.25 + 0.55 * (i / (n-1)));
      ctx.beginPath();
      ctx.arc(xOf(i), yOf(vals[i]), isLast ? 3.5 : 2, 0, Math.PI * 2);
      ctx.fillStyle = isLast ? '#5C469C' : 'rgba(92,70,156,' + alpha.toFixed(2) + ')';
      ctx.fill();
      if (isLast) {{ ctx.strokeStyle = '#F8F4EC'; ctx.lineWidth = 1.5; ctx.stroke(); }}
    }}

    // Labels eje X
    ctx.font = '7px Geist,sans-serif'; ctx.textAlign = 'center';
    for (var i=0; i<n; i++) {{
      if (i === 0 || i === Math.floor(n/2) || i === n-1) {{
        ctx.fillStyle = i === n-1 ? '#5C469C' : 'rgba(100,90,80,0.55)';
        ctx.fillText(SEMANAS[i], xOf(i), H - 3);
      }}
    }}
  }}

  // ── Sparkline: escala GLOBAL (vs techo card) ─────────────────────────────
  function updateSpark(vals) {{
    var spEl = document.getElementById('hist-' + CID + '-spark');
    if (!spEl) return;
    var html = '';
    vals.forEach(function(v, i) {{
      var ratio  = Math.min(v / BAR_CEIL, 1.0);
      var h      = Math.max(Math.round(2 + 16 * ratio), 2);
      var alpha  = (0.20 + 0.75 * ratio).toFixed(2);
      var isLast = (i === vals.length - 1);
      var bg     = isLast ? 'var(--accent)' : 'rgba(92,70,156,' + alpha + ')';
      html += ('<div style="flex:1;background:' + bg + ';height:' + h +
               'px;border-radius:1px 1px 0 0;" title="' + SEMANAS[i] + ': ' +
               v.toFixed(2) + '%"></div>');
    }});
    spEl.innerHTML = html;
  }}

  // ── Actualizar métricas DOM ──────────────────────────────────────────────
  function updateMetrics(vals, label) {{
    var vMin  = Math.min.apply(null, vals);
    var vMax  = Math.max.apply(null, vals);
    var vAvg  = vals.reduce(function(a,b){{return a+b;}}, 0) / vals.length;
    var vCurr = vals[vals.length - 1];
    var banda = getBanda(vCurr);
    var bc    = BC[banda] || BC['Sin Conversión'];

    function fmt(v) {{ return v.toFixed(2).replace('.', ',') + '%'; }}

    // Label elemento
    var lEl = document.getElementById('hist-' + CID + '-label');
    if (lEl) lEl.textContent = label || 'Global';

    // Métricas
    var el;
    el = document.getElementById('hist-' + CID + '-actual');
    if (el) el.textContent = fmt(vCurr);
    el = document.getElementById('hist-' + CID + '-max');
    if (el) el.textContent = fmt(vMax);
    el = document.getElementById('hist-' + CID + '-min');
    if (el) el.textContent = fmt(vMin);
    el = document.getElementById('hist-' + CID + '-avg');
    if (el) el.textContent = fmt(vAvg);

    // Badge banda
    var bbEl = document.getElementById('hist-' + CID + '-banda-box');
    var bEl  = document.getElementById('hist-' + CID + '-banda');
    if (bbEl) {{
      bbEl.style.background   = bc.bg;
      bbEl.style.color        = bc.fg;
      bbEl.style.borderColor  = bc.fg;
    }}
    if (bEl) {{ bEl.textContent = banda; bEl.style.color = bc.fg; }}

    // Footer: usa bc.footer (siempre legible sobre fondo claro)
    el = document.getElementById('hist-' + CID + '-banda-footer');
    if (el) {{ el.textContent = 'Banda: ' + banda; el.style.color = bc.footer; }}
    el = document.getElementById('hist-' + CID + '-trend-footer');
    if (el) el.innerHTML = 'Target: ≥' + TARGET + '%';

    updateSpark(vals);
  }}

  // ── Clicks en rows ───────────────────────────────────────────────────────
  function attachListeners() {{
    var histEl = document.getElementById('hist-' + CID);
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

      card.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
        r.style.background = '';
      }});
      row.style.background = 'var(--accent-soft)';

      var serie = buildSerie(w21, isNaN(w20) ? w21 : w20);
      drawCanvas(serie);
      updateMetrics(serie, lbl);
    }});
  }}

  // ── Init ─────────────────────────────────────────────────────────────────
  function init() {{
    drawCanvas(VALS_DEF);
    updateMetrics(VALS_DEF, 'Global');
    attachListeners();
  }}

  // Listeners de eventos custom (se registran siempre, no dependen de readyState)
  // Permiten que un wrapper externo (módulo de sección) actualice este canvas
  document.addEventListener('hist-update', function(e) {{
    if (e.detail.cid !== CID) return;
    var w_curr = e.detail.w_curr;
    var w_prev = (e.detail.w_prev !== undefined) ? e.detail.w_prev : w_curr;
    var lbl    = e.detail.label || '';
    if (isNaN(w_curr)) return;
    var serie = buildSerie(w_curr, isNaN(w_prev) ? w_curr : w_prev);
    drawCanvas(serie);
    updateMetrics(serie, lbl);
  }});
  document.addEventListener('hist-reset', function(e) {{
    if (e.detail.cid !== CID) return;
    drawCanvas(VALS_DEF);
    updateMetrics(VALS_DEF, 'Global');
  }});

  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', init);
  else
    requestAnimationFrame(init);
}})();
</script>'''

