"""
render_historico_cr — Módulo histórico reactivo v5 (W20 sesión 6).
- Datos reales W16-W20 (extraídos de pickles cr_w{16-20}_data.pkl)
- Ventana de 5 semanas (W16-W20) → el último valor es la semana actual del reporte
- Título: "Evolución Histórica"
- Sin pill WoW delta en el header
- Badge Súper Crítica: bg gris claro + texto gris oscuro (suavizado)
- Footer texto siempre legible sobre fondo claro (usa fg_footer distinto de fg_badge en SC)
- Barras: escala global de la card (valor vs techo global = target o max P90)
- Curvas: escala local del elemento seleccionado
"""
import json as _json
from historico_data import get_serie, SEMANAS

# ── Colores exactos del sistema D (render_helpers.py) ─────────────────────────
_BANDA_COLORS = {
    # Paleta D · sincronizada con render_helpers.BANDA_COLORS
    'Exitosa':        {'bg': '#E1F5EE', 'fg': '#1A6B4A', 'bd': '#1D9E75',  'bar': '#1A6B4A',  'footer': '#1A6B4A'},
    'Aceptable':      {'bg': '#FEF9C3', 'fg': '#713F12', 'bd': '#FCD34D',  'bar': '#FCD34D',  'footer': '#713F12'},
    'Revisar':        {'bg': '#FED7AA', 'fg': '#C2410C', 'bd': '#F97316',  'bar': '#F97316',  'footer': '#C2410C'},
    'Crítica':        {'bg': '#FCE4F1', 'fg': '#99162B', 'bd': '#C0392B',  'bar': '#C0392B',  'footer': '#99162B'},
    'Súper Crítica':  {'bg': '#EDECEC', 'fg': '#4A3F3F', 'bd': '#9B2222',  'bar': '#C0392B',  'footer': '#4A3F3F'},
    'Sin Conversión': {'bg': '#F2EEE6', 'fg': '#5F5E5A', 'bd': '#8A8377',  'bar': '#8A8377',  'footer': '#5F5E5A'},
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
    val_actual  : float [0,1] (valor de la semana ACTUAL del reporte, ej. W20)
    canvas_id   : ID único del canvas (su sufijo determina el scope: -global-, -op-, -cug-, -b2c-)
    hist_vals   : DEPRECATED — se ignora. Los valores históricos vienen de historico_data.HIST_DATA.
                  Mantenido para compatibilidad de firma con render_historico_seccion_cr.
    global_ceil : techo global para las barras (ej: 97.0 para eficacia).
                  Si None, usa el target.
    """
    target = 97.0 if metric_type == 'eficacia' else 2.5
    bar_ceil = global_ceil if global_ceil is not None else target

    # Determinar scope desde el canvas_id
    scope = 'global'
    for k in ('op', 'cug', 'b2c'):
        if k in canvas_id:
            scope = k; break

    # Serie completa W16-W20 desde datos reales (val_actual es W20)
    w_current_val = round(val_actual * 100, 2)
    vals_default  = get_serie('cr', metric_type, scope, w_current_val)
    semanas       = list(SEMANAS)   # ['W16','W17','W18','W19','W20']
    n_weeks       = len(semanas)
    idx_current   = n_weeks - 1     # índice del último valor (semana actual)

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
            if i == idx_current:
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
    # base_ratios: ratios de cada semana histórica vs la última, para escalar al click
    base_ratios      = [round(v / (vals_default[-1] + 0.0001), 6) for v in vals_default[:-1]]
    base_ratios_json = _json.dumps(base_ratios)

    return f'''<div id="hist-{canvas_id}"
     style="margin-top:8px;padding:10px 12px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;">

  <!-- Header: título + label elemento seleccionado -->
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
    <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">
      Evolución Histórica ·
      <span id="hist-{canvas_id}-label" style="color:var(--ink-muted);font-weight:600;">Global</span>
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
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Máx 5W</div>
      <div id="hist-{canvas_id}-max" style="font-size:13px;font-weight:700;color:#2F6C34;margin-top:2px;">{v_max:.2f}%</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Mín 5W</div>
      <div id="hist-{canvas_id}-min" style="font-size:13px;font-weight:700;color:#C0392B;margin-top:2px;">{v_min:.2f}%</div>
    </div>
    <div style="text-align:center;padding:6px 2px;background:var(--paper);border-radius:3px;border:1px solid var(--rule-soft);">
      <div style="font-size:8px;color:var(--ink-muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Prom 5W</div>
      <div id="hist-{canvas_id}-avg" style="font-size:13px;font-weight:700;color:var(--ink);margin-top:2px;">{v_avg:.2f}%</div>
    </div>
    <div id="hist-{canvas_id}-banda-box"
         style="display:flex;align-items:center;justify-content:center;text-align:center;padding:10px 6px;border-radius:3px;background:{b_bg};border:1px solid {b_bd};">
      <div id="hist-{canvas_id}-banda" style="font-size:11px;font-weight:700;color:{b_fg};line-height:1.2;text-transform:uppercase;letter-spacing:.04em;">{banda_actual.upper()}</div>
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
      <span style="font-size:7px;color:var(--ink-muted);">{semanas[0]}</span>
      <span style="font-size:7px;color:var(--accent);font-weight:700;">{semanas[-1]}</span>
    </div>
  </div>

  <!-- Footer -->
  <div style="display:flex;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:1px solid var(--rule-soft);">
    <span id="hist-{canvas_id}-banda-footer" style="font-size:8px;font-weight:700;color:{b_footer};text-transform:uppercase;letter-spacing:.04em;">{banda_actual.upper()}</span>
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
  // Estado de puntos para tooltip
  var pointsCache = [];

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
    pointsCache = [];
    for (var i=0; i<n; i++) {{
      var isLast = (i === n-1);
      var alpha  = isLast ? 1 : (0.25 + 0.55 * (i / (n-1)));
      var px = xOf(i), py = yOf(vals[i]);
      pointsCache.push({{x: px, y: py, val: vals[i], semana: SEMANAS[i]}});
      ctx.beginPath();
      ctx.arc(px, py, isLast ? 3.5 : 2, 0, Math.PI * 2);
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

  // Tooltip al hover
  function attachTooltip() {{
    var el = document.getElementById(CID);
    if (!el) return;
    // Crear tooltip si no existe
    var tt = el.parentElement.querySelector('.hist-tooltip-' + CID);
    if (!tt) {{
      tt = document.createElement('div');
      tt.className = 'hist-tooltip-' + CID;
      tt.style.cssText = 'position:absolute;pointer-events:none;background:var(--paper);color:var(--ink);border:1px solid var(--rule);padding:4px 8px;border-radius:3px;font-size:10px;font-weight:600;letter-spacing:.02em;white-space:nowrap;transform:translate(-50%,-115%);z-index:50;display:none;box-shadow:0 2px 6px rgba(0,0,0,.08);';
      el.parentElement.style.position = 'relative';
      el.parentElement.appendChild(tt);
    }}
    el.addEventListener('mousemove', function(e) {{
      var rect = el.getBoundingClientRect();
      var mx = e.clientX - rect.left;
      var my = e.clientY - rect.top;
      // Encontrar punto más cercano (radio detección 14px)
      var best = null, bestDist = 14;
      for (var i=0; i<pointsCache.length; i++) {{
        var p = pointsCache[i];
        var d = Math.sqrt((p.x-mx)*(p.x-mx) + (p.y-my)*(p.y-my));
        if (d < bestDist) {{ bestDist = d; best = p; }}
      }}
      if (best) {{
        tt.textContent = best.semana + ' · ' + best.val.toFixed(2).replace('.', ',') + '%';
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
    if (bEl) {{ bEl.textContent = banda.toUpperCase(); bEl.style.color = bc.fg; }}

    // Footer: usa bc.footer (siempre legible sobre fondo claro)
    el = document.getElementById('hist-' + CID + '-banda-footer');
    if (el) {{ el.textContent = banda.toUpperCase(); el.style.color = bc.footer; }}
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

      // TOGGLE: si la fila ya estaba seleccionada, reset a Global
      var wasSelected = row.classList.contains('hist-selected');
      card.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
        r.style.background = '';
        r.classList.remove('hist-selected');
      }});

      if (wasSelected) {{
        // Reset: volver a Global
        drawCanvas(VALS_DEF);
        updateMetrics(VALS_DEF, 'Global');
        return;
      }}

      row.style.background = 'var(--accent-soft)';
      row.classList.add('hist-selected');

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
    attachTooltip();

    var el = document.getElementById(CID);
    if (!el) return;

    // Redibujar si el canvas está dentro de un <details> cerrado al cargar
    var det = el.closest('details');
    if (det) {{
      det.addEventListener('toggle', function() {{
        if (det.open) {{ requestAnimationFrame(function() {{ drawCanvas(VALS_DEF); }}); }}
      }});
    }}

    // Redibujar cuando el canvas sale de un panel CSS oculto (tabs display:none → block)
    // Útil para cards dentro de tabs-block o kpi-card con radio inputs
    if (typeof IntersectionObserver !== 'undefined') {{
      var drawn = false;
      var obs = new IntersectionObserver(function(entries) {{
        entries.forEach(function(entry) {{
          if (entry.isIntersecting && !drawn) {{
            drawn = true;
            requestAnimationFrame(function() {{ drawCanvas(VALS_DEF); }});
            obs.disconnect();
          }}
        }});
      }}, {{ threshold: 0.01 }});
      obs.observe(el);
    }} else {{
      // Fallback: redibujar varias veces en el primer segundo
      var t = 0;
      var delays = [50, 200, 500, 1000];
      delays.forEach(function(d) {{ setTimeout(function() {{ drawCanvas(VALS_DEF); }}, d); }});
    }}

    // Listener adicional para tabs CSS: cuando cualquier radio cambia, redibujar
    // (los tabs usan display:none → block via CSS puro, sin eventos del DOM en el canvas)
    document.addEventListener('change', function(e) {{
      if (e.target.type !== 'radio') return;
      var el2 = document.getElementById(CID);
      if (!el2) return;
      // Solo si el canvas va a estar visible (parentElement tiene offsetWidth > 0)
      requestAnimationFrame(function() {{
        var w = el2.parentElement ? el2.parentElement.offsetWidth : 0;
        if (w > 10) {{ drawCanvas(VALS_DEF); }}
      }});
    }});
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

