"""
Renderer CR parte 3: Análisis por Canasta (B2C, B2B-OP, CUG)
Cards colapsables con KPIs Eficacia/ConvRate + tabs WoW + RE con pills + bloques hotel/dimensión
Post W19 · port del patrón RND p3
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
import os, pandas as pd, numpy as np

# Setup paths
# (path setup ya hecho arriba)
# (path setup ya hecho arriba)
from engine import *
from render_helpers import *
def _fmt_wow_cv(v):
    """WoW ConvRate en pp — verde si sube."""
    import math
    if v is None or (isinstance(v,float) and (math.isnan(v) or math.isinf(v))) or abs(v) < 0.001:
        return '<em class="wow-pill nd">—</em>'
    mejora = v > 0
    cls = 'dn' if mejora else 'up'
    arrow = '↑' if v > 0 else '↓'
    return f'<em class="wow-pill {cls}">{arrow}{abs(v):.2f}</em>'.replace('.',',')
from template_seguimiento import render_seguimiento_block

with open('asset_cr_footer.html') as f: FOOTER = f.read()

with open(os.getenv('PICKLE_CR', 'cr_w20_data.pkl'),'rb') as f:
    D = pickle.load(f)
M = D['M']; CANASTA = D['CANASTA']

# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────


WEEK_NUM_CR   = D.get('VOL_NUM', '19')
WEEK_PREV_CR  = str(int(WEEK_NUM_CR) - 1)
SEGUIMIENTO_FILE_CR = f'_seguimiento/plan_seguimiento_W{WEEK_PREV_CR}.md'
df18 = D.get('df18', None)
df17 = D.get('df17', None)
hotel_channel_map_global = D.get('hotel_channel_map', {})
g_channel_w17 = D.get('g_channel_w17', None)

from historico_module_v2 import render_historico_cr

def _mini_badge(bnd):
    if not bnd or not isinstance(bnd, str): return ''
    bc = BANDA_COLORS.get(bnd, {})
    bg = bc.get('bg', '#F2EEE6'); fg = bc.get('fg', '#5F5E5A')
    return f'<span style="flex-shrink:0;font-size:8px;font-weight:700;padding:1px 4px;border-radius:2px;background:{bg};color:{fg};text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;">{bnd}</span>'


def render_historico_seccion_cr(canvas_id_ef, canvas_id_cv, banda_ef, val_ef, banda_cv, val_cv):
    """Módulo histórico doble (Ef + CV) para secciones de análisis en canastas."""
    html_ef = render_historico_cr('eficacia', banda_ef, val_ef, canvas_id_ef)
    html_cv = render_historico_cr('convrate', banda_cv, val_cv, canvas_id_cv)
    js = f"""<script>
(function() {{
  var section = document.getElementById('hist-{canvas_id_ef}-container');
  if (!section) return;
  // Subir hasta el bloque canasta-*-hotel o canasta-*-dim, luego section o details
  var parent = section.parentElement;
  while (parent && !parent.id?.match(/^canasta-.*-(hotel|dim)-/) && parent.tagName !== 'SECTION' && parent.tagName !== 'DETAILS' && parent !== document.body) {{
    parent = parent.parentElement;
  }}
  if (!parent) parent = document.body;
  function resetToGlobal() {{
    parent.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
      r.style.background = ''; r.removeAttribute('data-selected-hist');
    }});
    document.dispatchEvent(new CustomEvent('hist-reset', {{detail: {{cid: '{canvas_id_ef}'}}}}));
    document.dispatchEvent(new CustomEvent('hist-reset', {{detail: {{cid: '{canvas_id_cv}'}}}}));
  }}
  parent.addEventListener('click', function(e) {{
    var row = e.target.closest('[data-hist-w21]');
    if (!row) return;
    if (e.target.closest('[id^="hist-"]')) return;
    if (row.getAttribute('data-selected-hist') === '1') {{ resetToGlobal(); return; }}
    var ef_curr = parseFloat(row.getAttribute('data-hist-w21'));
    var ef_prev = parseFloat(row.getAttribute('data-hist-w20') || ef_curr);
    var cv_curr = parseFloat(row.getAttribute('data-hist-cv-w21') || ef_curr);
    var cv_prev = parseFloat(row.getAttribute('data-hist-cv-w20') || cv_curr);
    var lbl = row.getAttribute('data-hist-label') || '';
    parent.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
      r.style.background = ''; r.removeAttribute('data-selected-hist');
    }});
    row.setAttribute('data-selected-hist', '1');
    row.style.background = 'var(--accent-soft)';
    document.dispatchEvent(new CustomEvent('hist-update', {{detail: {{cid: '{canvas_id_ef}', w_curr: ef_curr, w_prev: ef_prev, label: lbl}}}}));
    document.dispatchEvent(new CustomEvent('hist-update', {{detail: {{cid: '{canvas_id_cv}', w_curr: cv_curr, w_prev: cv_prev, label: lbl}}}}));
  }});
}})();
</script>"""
    return f'''<div id="hist-{canvas_id_ef}-container" style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;margin-bottom:8px;">
  <div>{html_ef}</div><div>{html_cv}</div>
</div>{js}'''

CR_ACCENT = '#5C469C'

PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']


# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

# ── Helpers de pills WoW ─────────────────────────────────────────────────────
def get_pill_wow(name, wow_map):
    """wow_map: dict {nombre: (texto, mejora)} · mejora=True → verde."""
    for key, (txt, mejora) in wow_map.items():
        if key.lower() in str(name).lower() or str(name).lower() in key.lower():
            if txt is None:
                return '<em class="wow-pill nd">—</em>'
            color = '#2F6C34' if mejora else '#C0392B'
            bg    = '#EAF3DE' if mejora else '#FCE8E6'
            return (f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;'
                    f'border-radius:3px;background:{bg};color:{color};vertical-align:middle;margin:0 2px;">{txt}</span>')
    return '<em class="wow-pill nd">—</em>'

def pill_b(nombre):
    """Pill de banda con colores SÓLIDOS (paleta D)."""
    c = BANDA_COLORS.get(nombre, BANDA_COLORS['Sin Conversión'])
    # Badge sólido: bg = color sólido de banda, texto blanco/claro
    bg = c['fg']  # color sólido oscuro de banda
    fg = '#FCEBEB' if nombre == 'Súper Crítica' else '#FFFFFF'
    return (f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;'
            f'border-radius:2px;background:{bg} !important;color:{fg} !important;'
            f'text-transform:uppercase;letter-spacing:.05em;vertical-align:middle;margin:0 2px;">{nombre}</span>')

def pill_d(texto, mejora):
    """Pill de delta WoW (verde=mejora, rojo=deterioro)."""
    color = '#2F6C34' if mejora else '#C0392B'
    bg    = '#EAF3DE' if mejora else '#FCE8E6'
    return (f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;'
            f'border-radius:3px;background:{bg};color:{color};vertical-align:middle;margin:0 2px;">{texto}</span>')


# ── Findings del RE de canasta ────────────────────────────────────────────────
def _build_canasta_findings_cr(c):
    """10 findings para RE dentro de canasta CR."""
    m18 = c['m18']; m17 = c['m17']
    ef   = m18['eficacia'];   ef17  = m17['eficacia']
    cv   = m18['conv_rate'];  cv17  = m17['conv_rate']
    ef_wow = (ef - ef17) * 100
    cv_wow = (cv - cv17) * 100
    n_p80  = len(c['p80'])
    n_critmas_ef = int(c['sev_ef'].get('Crítica',0) + c['sev_ef'].get('Súper Crítica',0))
    n_supcrit_ef = int(c['sev_ef'].get('Súper Crítica',0))
    n_sc  = int(c['sev_cv'].get('Sin Conversión',0))
    n_crit_cv = int(c['sev_cv'].get('Crítica',0))
    canasta_label = c['short']

    h_worst_ef = c['p80'][(c['p80']['Bookings']>0)&(c['p80']['Eficacia']>0)].sort_values('Eficacia').iloc[0] if (c['p80']['Bookings']>0).any() else None
    h_worst_cv = c['p80'][c['p80']['Bookings']>0].sort_values('ConvRate').iloc[0] if (c['p80']['Bookings']>0).any() else None
    h_top_sc   = c['p80'][c['p80']['Bookings']==0].sort_values('CR_Unicos', ascending=False).iloc[0] if (c['p80']['Bookings']==0).any() else None

    top_corp_pool = c['agg_corp'].sort_values('CR_Unicos', ascending=False)
    top1_corp = top_corp_pool.iloc[0] if len(top_corp_pool)>0 else None
    top2_corp = top_corp_pool.iloc[1] if len(top_corp_pool)>1 else None
    top3_corp = top_corp_pool.iloc[2] if len(top_corp_pool)>2 else None

    def es_pct(v, dec=2): return f'{v:.{dec}f}%'.replace('.',',')
    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}'.replace('.',',')
    def es_pct1(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.1f}%'.replace('.',',')
    def es_int(v): return fmt_int_es(int(v))

    findings = [
        {'numero': es_pct(ef*100,2),
         'titulo': f'Eficacia · banda {m18["banda_eficacia"]}',
         'desc': f'Tasa de éxito de CheckRates en canasta {canasta_label}. Target ≥ 97%.'},
        {'numero': es_pct(cv*100,2),
         'titulo': f'Conv Rate · banda {m18["banda_convrate"]}',
         'desc': f'Bookings / CR únicos en canasta {canasta_label}. Target ≥ 2,5%.'},
        {'numero': es_int(n_critmas_ef),
         'titulo': 'Hoteles Severity Eficacia Crítica+',
         'desc': f'Eficacia &lt; 85% · {n_supcrit_ef} Súper Críticos requieren escalamiento técnico inmediato.'},
        {'numero': es_int(n_sc),
         'titulo': 'Hoteles P80 Sin Conversión (BKGS=0)',
         'desc': f'{es_pct(n_sc/max(n_p80,1)*100,1)} del P80 sin convertir · cohorte estructural · diagnóstico técnico/contractual.'},
        {'numero': es_int(n_crit_cv),
         'titulo': 'Hoteles Severity ConvRate Crítica',
         'desc': f'Conv Rate &lt; 0,8% · revisar pricing, posicionamiento y matching técnico.'},
    ]

    if h_worst_ef is not None:
        findings.append({
            'numero': es_pct(h_worst_ef['Eficacia']*100,2),
            'titulo': f'{truncate(clean_hotel_name(h_worst_ef["Hotel"]),28)} · peor Eficacia',
            'desc': f'{fmt_int_es(h_worst_ef["CR_Unicos"])} CR · {h_worst_ef["CorpName"]} · escalamiento individual prioritario.'
        })
    if top1_corp is not None and top2_corp is not None:
        corps_str = top1_corp["CorpName"]
        if top3_corp is not None:
            corps_str += f', {top2_corp["CorpName"]} y {top3_corp["CorpName"]}'
        else:
            corps_str += f' y {top2_corp["CorpName"]}'
        findings.append({
            'numero': fmt_int_es(top1_corp["CR_Unicos"]),
            'titulo': f'{clean_corp_name(top1_corp["CorpName"])} · líder volumen CR',
            'desc': f'Junto con {clean_corp_name(top2_corp["CorpName"])} concentran el grueso del volumen en {canasta_label}.'
        })
    if h_worst_cv is not None:
        findings.append({
            'numero': es_pct(h_worst_cv['ConvRate']*100,2),
            'titulo': f'{truncate(clean_hotel_name(h_worst_cv["Hotel"]),28)} · peor ConvRate',
            'desc': f'{fmt_int_es(h_worst_cv["CR_Unicos"])} CR · {h_worst_cv["CorpName"]} · falla sistémica de conversión.'
        })
    if h_top_sc is not None:
        findings.append({
            'numero': fmt_int_es(h_top_sc["CR_Unicos"]),
            'titulo': f'{truncate(clean_hotel_name(h_top_sc["Hotel"]),28)} · #1 Sin Conv',
            'desc': f'CR sin convertir · {h_top_sc["CorpName"]} · primer caso para revisión técnica esta semana.'
        })
    findings.append({
        'numero': es_int(n_p80),
        'titulo': 'Hoteles P80 analizados',
        'desc': f'Universo de análisis · base estable para diagnóstico de la canasta {canasta_label}.'
    })
    while len(findings) < 10:
        findings.append({'numero': '—', 'titulo': 'Dato no disponible', 'desc': 'Cohorte insuficiente para finding adicional esta semana.'})
    return findings[:10]


# ── Alertas dentro de canasta CR ──────────────────────────────────────────────
def _render_canasta_alertas_cr(c, accent_color=CR_ACCENT):
    from template_alertas import render_alertas_block, render_alert_card, render_alert_subcell

    p80 = c['p80']
    # Peor Eficacia con BKGS>0
    ef_pool = p80[(p80['Bookings']>0)&(p80['Eficacia']>0)].sort_values('Eficacia')
    h_ef = ef_pool.iloc[0] if len(ef_pool)>0 else None
    # Peor ConvRate con BKGS>0
    cv_pool = p80[p80['Bookings']>0].sort_values('ConvRate')
    h_cv = cv_pool.iloc[0] if len(cv_pool)>0 else None

    # Destinos
    g_d = p80.groupby('Destino').agg(CR_Unicos=('CR_Unicos','sum'),Bookings=('Bookings','sum'),Successful=('Successful','sum')).reset_index()
    g_d['Eficacia']  = g_d['Successful']/g_d['CR_Unicos']
    g_d['ConvRate']  = g_d['Bookings']/g_d['CR_Unicos']
    d_ef = g_d[(g_d['Bookings']>0)&(g_d['Eficacia']>0)].sort_values('Eficacia').iloc[0] if len(g_d[(g_d['Bookings']>0)&(g_d['Eficacia']>0)])>0 else g_d.iloc[0]
    d_cv = g_d[g_d['Bookings']>0].sort_values('ConvRate').iloc[0] if len(g_d[g_d['Bookings']>0])>0 else g_d.iloc[0]

    # Channels
    g_ch = p80.groupby('CorpName').agg(CR_Unicos=('CR_Unicos','sum'),Bookings=('Bookings','sum'),Successful=('Successful','sum')).reset_index()
    g_ch['Eficacia']  = g_ch['Successful']/g_ch['CR_Unicos']
    g_ch['ConvRate']  = g_ch['Bookings']/g_ch['CR_Unicos']
    ch_ef = g_ch[(g_ch['Bookings']>0)&(g_ch['Eficacia']>0)].sort_values('Eficacia').iloc[0] if len(g_ch[(g_ch['Bookings']>0)])>0 else g_ch.iloc[0]
    ch_cv = g_ch[g_ch['Bookings']>0].sort_values('ConvRate').iloc[0] if len(g_ch[g_ch['Bookings']>0])>0 else g_ch.iloc[0]

    def alert_card_cr(title, icon, ef_obj, cv_obj, name_col):
        if ef_obj is None or cv_obj is None: return ''
        sub_ef = render_alert_subcell(
            'Eficacia', '#EA0074', '#FCE4F1',
            truncate(clean_hotel_name(str(ef_obj[name_col])) if name_col=='Hotel' else (clean_destino_name(str(ef_obj[name_col])) if name_col=='Destino' else str(ef_obj[name_col])), 22),
            fmt_pct2(ef_obj['Eficacia']), '#EA0074'
        )
        sub_cv = render_alert_subcell(
            'ConvRate', CR_ACCENT, '#EDE8F7',
            truncate(clean_hotel_name(str(cv_obj[name_col])) if name_col=='Hotel' else (clean_destino_name(str(cv_obj[name_col])) if name_col=='Destino' else str(cv_obj[name_col])), 22),
            fmt_pct2(cv_obj['ConvRate']), CR_ACCENT
        )
        return render_alert_card(title, icon, accent_color, sub_ef, sub_cv)

    card_h  = alert_card_cr('Hoteles',  '🏨', h_ef,  h_cv,  'Hotel')
    card_d  = alert_card_cr('Destinos', '📍', d_ef,  d_cv,  'Destino')
    card_co = alert_card_cr('Corp',     '🏢', ch_ef, ch_cv, 'CorpName')

    return render_alertas_block(
        f'Alertas · Casos Críticos · Canasta {c["short"]}',
        accent_color, card_h, card_d, card_co
    )


# ── render_canasta_block principal ────────────────────────────────────────────
def render_canasta_block(canasta_data, idx_str='b2c'):
    from template_resumen import render_resumen_ejecutivo
    from template_severity import render_severity_block, render_severity_2cols, make_severity_levels, LEVELS_EFICACIA, LEVELS_CONVRATE

    c   = canasta_data
    m18 = c['m18']; m17 = c['m17']
    ef_w18 = m18['eficacia'];  ef_w17 = m17['eficacia']
    cv_w18 = m18['conv_rate']; cv_w17 = m17['conv_rate']
    ef_wow = (ef_w18 - ef_w17) * 100
    cv_wow = (cv_w18 - cv_w17) * 100

    banda_ef = banda_eficacia(ef_w18)
    banda_cv = banda_convrate(cv_w18, m18['bookings'])

    n_p80      = len(c['p80'])
    n_sc_total = int((c['agg_hotel']['Bookings']==0).sum())
    n_critmas_local = int(c['sev_ef'].get('Crítica',0) + c['sev_ef'].get('Súper Crítica',0))

    wow_color_ef = '#2F6C34' if ef_wow > 0 else '#C0392B'
    wow_color_cv = '#2F6C34' if cv_wow > 0 else '#C0392B'
    wow_str_ef = (f'↑ +{ef_wow:.2f}pp' if ef_wow > 0 else f'↓ {ef_wow:.2f}pp').replace('.', ',')
    wow_str_cv = (f'↑ +{cv_wow:.2f}pp' if cv_wow > 0 else f'↓ {cv_wow:.2f}pp').replace('.', ',')

    # ── WoW box ──────────────────────────────────────────────────────────────
    def wow_box_canasta(v17, v18, wow_str, wow_color, accent):
        bg_wow = '#E0F0E2' if wow_color == '#2F6C34' else '#FCE4F1'
        return f'''<div style="margin-top:14px;background:var(--paper);border-radius:4px;padding:8px;display:flex;align-items:stretch;gap:8px;">
<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W{WEEK_NUM_INT-1}</div>
  <div style="font-size:16px;font-weight:700;color:var(--ink-soft);margin-top:2px;">{v17}</div>
</div>
<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W{WEEK_NUM_INT}</div>
  <div style="font-size:16px;font-weight:700;color:{accent};margin-top:2px;">{v18}</div>
</div>
<div style="flex:1;text-align:center;background:{bg_wow};padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:{wow_color};font-weight:700;">WoW</div>
  <div style="font-size:16px;font-weight:700;color:{wow_color};margin-top:2px;">{wow_str}</div>
</div>
</div>'''

    # ── Tab rows con pills WoW ────────────────────────────────────────────────
    def tab_rows_canasta(df, dim_col, parse_hotel=False, wow_col=None, val_col='Eficacia', is_cv=False, tab_key=''):
        top5 = next5 = rest = ''
        for i, r in df.iterrows():
            raw = r[dim_col]
            raw_lab = str(raw)
            if parse_hotel:
                lab = truncate(clean_hotel_name(raw_lab), 28)
            elif dim_col == 'CorpName':
                lab = truncate(clean_corp_name(raw_lab), 28)
            elif dim_col == 'Destino':
                lab = clean_destino_name(raw_lab, 28)
            else:
                lab = truncate(raw_lab, 28)
            val = r[val_col] if val_col in r.index else 0
            val_str = fmt_pct2(val)
            import math
            wow_pill = '<em style="font-style:normal;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;text-align:center;display:block;min-width:32px;">—</em>'
            if wow_col and wow_col in r.index:
                try:
                    wow_v = r[wow_col]
                    if wow_v == wow_v and wow_v is not None and not math.isnan(float(wow_v)) and abs(wow_v) >= 0.005:
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'
                        wb2 = '#EAF3DE' if mejora else '#FCE8E6'
                        arrow = '↑' if wow_v > 0 else '↓'
                        wow_txt = f'{arrow}{abs(wow_v):.1f}'.replace('.', ',')
                        wow_pill = f'<em style="font-style:normal;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb2};color:{wc};text-align:center;display:block;min-width:32px;">{wow_txt}</em>'
                except: pass
            import math as _math_cell
            _w21 = round(float(val) * 100, 4) if val and not _math_cell.isnan(float(val)) else 0
            _w20_col = val_col.replace('Eficacia','Eficacia_W17').replace('ConvRate','ConvRate_W17')
            _w20_raw = r.get(_w20_col, None) if hasattr(r, 'get') else None
            try:
                _w20 = round(float(_w20_raw) * 100, 4) if _w20_raw is not None and not _math_cell.isnan(float(_w20_raw)) else _w21
            except: _w20 = _w21
            _bnd3 = '' if parse_hotel else (
                r.get('BandaConvRate' if is_cv else 'BandaEficacia', '') if ('BandaConvRate' in r.index or 'BandaEficacia' in r.index) else '')
            if not _bnd3 and val and not parse_hotel:
                _bnd3 = banda_convrate(val, int(r.get('Bookings',0))) if is_cv else banda_eficacia(val)
            _badge3 = _mini_badge(_bnd3)
            if i < 5: _cls3 = ''
            elif i < 10: _cls3 = 'rows-more'
            else: _cls3 = 'sb-hidden'
            _row3 = (f'<div class="{_cls3}" data-row-idx="{i}" data-hist-w21="{_w21}" data-hist-w20="{_w20}" data-hist-label="{raw_lab}"'
                     f' style="display:grid;grid-template-columns:minmax(0,1fr) 72px 46px 36px;align-items:center;gap:4px;'
                     f'padding:4px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                     f'<span style="font-size:11px;font-weight:600;color:var(--accent);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;">{i+1}. {lab}</span>'
                     f'<div style="display:flex;align-items:center;">{_badge3}</div>'
                     f'<span style="font-size:11px;text-align:right;font-variant-numeric:tabular-nums;">{val_str}</span>'
                     f'{wow_pill}</div>')
            if i < 5: top5 += _row3
            elif i < 10: next5 += _row3
            else: rest += _row3
        has_more = len(df) > 5 and not parse_hotel  # hotel también tiene ver más
        # Canasta y channel no tienen ver más (pocos elementos)
        is_simple = tab_key in ('canasta', 'channel', 'provider')
        ver_mas_btn = ''
        if has_more and not is_simple:
            ver_mas_btn = (f'<button class="rows-toggle" data-panel="{tab_key}" '
                           f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                           f'font-size:10px;font-weight:600;color:var(--accent);letter-spacing:.04em;'
                           f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                           f'<span class="toggle-label">Ver 5 más</span> '
                           f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
        return f'<div class="kpi-tab-rows">{top5}{next5}</div>{rest}{ver_mas_btn}'

    # ── KPI card con gauge + wow + tabs ──────────────────────────────────────
    def kpi_card_canasta(metric, val18, val17, banda, pill_target, wow_str, wow_color,
                          gauge_tipo, tab_configs, card_id=''):
        pill   = banda_pill(banda, target=pill_target, font_size='11px')
        pill_with_target = pill + target_caption(pill_target, font_size='10px')
        gauge  = gauge_5levels(banda, gauge_tipo)
        v18str = fmt_pct2(val18)
        v17str = fmt_pct2(val17)
        wb     = wow_box_canasta(v17str, v18str, wow_str, wow_color, CR_ACCENT)
        tabs_inputs = ''.join(
            f'<input {"checked " if i==0 else ""}id="tab-{card_id}-{tk}" name="tabs-{card_id}" style="display:none;" type="radio"/>'
            for i,(tk,_,_,_) in enumerate(tab_configs)
        )
        tabs_labels = ''.join(
            f'<label class="tab-label" for="tab-{card_id}-{tk}">{tl}</label>'
            for tk, tl, _, _ in tab_configs
        )
        panels = ''
        for tk, tl, df_t, wm in tab_configs:
            dim_col = {'destino':'Destino','corp':'CorpName','hotel':'Hotel','channel':'ExternalProviderName'}.get(tk, tk)
            parse_hotel = tk == 'hotel'
            val_col = 'ConvRate' if 'cv' in card_id else 'Eficacia'
            # wm es ahora el nombre de la columna WoW (string) o None
            panel_html = tab_rows_canasta(df_t, dim_col, parse_hotel, wow_col=wm, val_col=val_col, tab_key=tk)
            panels += f'<div class="tab-panel" data-tab="{tk}">{panel_html}</div>'
        metric_type_hist = 'convrate' if 'cv' in card_id else 'eficacia'
        hist_mod = render_historico_cr(metric_type_hist, banda, val18, f'hcr-{card_id}')
        sb_id = f'sb-kpi-{card_id}'
        panels_id = f'kpi-{card_id}-panels'
        _wow_pp = wow_pill_html(float(wow_str.replace(',','.').replace('pp','').replace('%','').strip().lstrip('↑↓=+').strip()) * (1 if '↑' in wow_str else -1 if '↓' in wow_str else 0), unit='pp') if wow_str and wow_str not in ('—',) else wow_pill_html(None)
        return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);">
{tabs_inputs}
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">{metric}</div>
<div style="margin-top:4px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
<div style="font-size:36px;font-weight:600;letter-spacing:-.02em;color:{CR_ACCENT};line-height:1;">{v18str}</div>
<div style="display:flex;flex-direction:column;gap:6px;padding-bottom:3px;">
{pill_with_target}
<div style="display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">vs sem. ant. {_wow_pp}</div>
</div>
</div>
{gauge}
{wb}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;border-bottom:1px solid var(--rule);padding:0 0 0 4px;align-items:flex-end;">{tabs_labels}{searchbox_pill_html(sb_id, accent_color='#5C469C', placeholder='Buscar…', count_id=f'cnt-{card_id}')}</div>
<div id="{panels_id}" class="tab-panels">{panels}</div>
{hist_mod}
</div>'''

    # Datos para tabs de KPI
    p80 = c['p80']
    agg_corp = c['agg_corp']
    agg_dest = c['agg_destino'] if 'agg_destino' in c else c['g_dest']
    agg_chan  = c['agg_channel']

    # Filtro P50 para excluir volumen insignificante
    p50_d = agg_dest['CR_Unicos'].quantile(0.50)
    p50_h = p80['CR_Unicos'].quantile(0.50)

    # Merge WoW con refs globales W17
    ref_corp_w17 = D.get('g_corp_w17', None)
    ref_dest_w17 = D.get('g_dest_w17', None)

    def add_wow_to_tab(df, dim_col, metric_col, ref_w17, wow_col):
        if ref_w17 is None: return df
        df = df.merge(ref_w17[[dim_col, wow_col.replace('_WoW_pp','_W17')]], on=dim_col, how='left')
        ref_val_col = wow_col.replace('_WoW_pp','_W17')
        df[wow_col] = (df[metric_col] - df[ref_val_col]) * 100
        return df

    # Corp sin filtro P50: mismo universo que Excel de canasta
    d_ef = agg_dest[(agg_dest['CR_Unicos']>=p50_d) & (agg_dest['Eficacia']>0)].sort_values('Eficacia').head(100).reset_index(drop=True)
    d_ef = add_wow_to_tab(d_ef, 'Destino', 'Eficacia', ref_dest_w17, 'Eficacia_WoW_pp')
    c_ef = agg_corp.sort_values('Eficacia').head(100).reset_index(drop=True)
    c_ef = add_wow_to_tab(c_ef, 'CorpName', 'Eficacia', ref_corp_w17, 'Eficacia_WoW_pp')
    h_ef = p80[p80['CR_Unicos']>=p50_h].sort_values('Eficacia').head(100).reset_index(drop=True)

    d_cv = agg_dest[(agg_dest['CR_Unicos']>=p50_d) & (agg_dest['Bookings']>0)].sort_values('ConvRate').head(100).reset_index(drop=True)
    d_cv = add_wow_to_tab(d_cv, 'Destino', 'ConvRate', ref_dest_w17, 'ConvRate_WoW_pp')
    c_cv = agg_corp.sort_values('ConvRate').head(100).reset_index(drop=True)
    c_cv = add_wow_to_tab(c_cv, 'CorpName', 'ConvRate', ref_corp_w17, 'ConvRate_WoW_pp')
    h_cv = p80[p80['CR_Unicos']>=p50_h].sort_values('ConvRate').head(100).reset_index(drop=True)
    # Enriquecer h_cv con WoW ConvRate desde g_hotel_w17
    _hw17 = D.get('g_hotel_w17', None)
    if _hw17 is not None and 'Hotel' in h_cv.columns and 'ConvRate_W17' in _hw17.columns:
        h_cv = h_cv.merge(_hw17[['Hotel','ConvRate_W17']], on='Hotel', how='left')
        h_cv['ConvRate_WoW_pp'] = (h_cv['ConvRate'] - h_cv['ConvRate_W17']) * 100

    df_dest_ef = d_ef; df_corp_ef = c_ef; df_hot_ef = h_ef
    df_dest_cv = d_cv; df_corp_cv = c_cv; df_hot_cv = h_cv

    # Channel para tabs de canasta — mergear con g_channel_w17 para WoW
    g_chan = c.get('agg_channel', c.get('g_chan', None))
    if g_chan is not None and len(g_chan) > 0:
        g_chan = g_chan.copy()
        g_chan['BandaEficacia'] = g_chan['Eficacia'].apply(banda_eficacia)
        g_chan['BandaConvRate'] = g_chan.apply(lambda r: banda_convrate(r['ConvRate'], r['Bookings']), axis=1)
        # Merge WoW desde g_channel_w17 global
        if g_channel_w17 is not None:
            w17_cols = ['ExternalProviderName','Eficacia_W17']
            if 'ConvRate_W17' in g_channel_w17.columns: w17_cols.append('ConvRate_W17')
            g_chan = g_chan.merge(g_channel_w17[w17_cols], on='ExternalProviderName', how='left')
            g_chan['Eficacia_WoW_pp'] = (g_chan['Eficacia'] - g_chan['Eficacia_W17']) * 100
            if 'ConvRate_W17' in g_chan.columns:
                g_chan['ConvRate_WoW_pp'] = (g_chan['ConvRate'] - g_chan['ConvRate_W17']) * 100
        df_chan_ef = g_chan.sort_values('Eficacia').head(10).reset_index(drop=True)
        df_chan_cv = g_chan[g_chan['Bookings']>0].sort_values('ConvRate').head(10).reset_index(drop=True)
        has_chan = True
    else:
        df_chan_ef = df_chan_cv = None
        has_chan = False

    tabs_ef = [
        ('destino', 'Destino', df_dest_ef, 'Eficacia_WoW_pp'),
        ('corp',    'Corp',    df_corp_ef, 'Eficacia_WoW_pp'),
        ('hotel',   'Hotel',   df_hot_ef,  None),
    ]
    if has_chan: tabs_ef.append(('channel', 'Channel', df_chan_ef, 'Eficacia_WoW_pp'))

    tabs_cv = [
        ('destino', 'Destino', df_dest_cv, 'ConvRate_WoW_pp'),
        ('corp',    'Corp',    df_corp_cv, 'ConvRate_WoW_pp'),
        ('hotel',   'Hotel',   df_hot_cv,  'ConvRate_WoW_pp'),
    ]
    if has_chan: tabs_cv.append(('channel', 'Channel', df_chan_cv, 'ConvRate_WoW_pp'))

    card_ef = kpi_card_canasta('Eficacia', ef_w18, ef_w17, banda_ef, '≥ 97%',
                                wow_str_ef, wow_color_ef, 'eficacia', tabs_ef,
                                card_id=f'{idx_str}-ef')
    card_cv = kpi_card_canasta('ConvRate', cv_w18, cv_w17, banda_cv, '≥ 2,5%',
                                wow_str_cv, wow_color_cv, 'convrate', tabs_cv,
                                card_id=f'{idx_str}-cv')

    kpi_block = f'<div class="kpis-hero" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 24px;">{card_ef}{card_cv}</div>'

    # ── Alertas ───────────────────────────────────────────────────────────────
    alertas_canasta_html = _render_canasta_alertas_cr(c, CR_ACCENT)

    # ── Resumen Ejecutivo con pills ───────────────────────────────────────────
    findings_raw = _build_canasta_findings_cr(c)

    # Calcular bandas necesarias para findings 3-10
    banda_crit_ef  = 'Crítica'
    banda_sc       = 'Sin Conversión'
    banda_crit_cv  = 'Crítica'

    for i, f in enumerate(findings_raw):
        titulo = f['titulo']; desc = f['desc']
        if i == 0:  # Eficacia
            titulo = f'Eficacia · {pill_b(banda_ef)}'
            desc   = f'{pill_d(wow_str_ef, ef_wow > 0)} · {desc}'
        elif i == 1:  # Conv Rate
            titulo = f'Conv Rate · {pill_b(banda_cv)}'
            desc   = f'{pill_d(wow_str_cv, cv_wow > 0)} · {desc}'
        elif i == 2:  # Hoteles Severity Crítica+
            titulo = f'Hoteles Severity Eficacia · {pill_b("Crítica")}+'
        elif i == 3:  # Sin Conversión
            titulo = f'Hoteles P80 · {pill_b("Sin Conversión")} (BKGS=0)'
        elif i == 4:  # ConvRate Crítica
            titulo = f'Hoteles Severity ConvRate · {pill_b("Crítica")}'
        elif i == 5 and 'peor Eficacia' in titulo:  # Hotel peor Eficacia
            bnd_h = banda_eficacia(c['p80'][(c['p80']['Bookings']>0)&(c['p80']['Eficacia']>0)].sort_values('Eficacia').iloc[0]['Eficacia']) if (c['p80']['Bookings']>0).any() else 'Crítica'
            titulo = titulo.replace('· peor Eficacia', f'· peor Eficacia {pill_b(bnd_h)}')
        elif i == 7 and 'peor ConvRate' in titulo:  # Hotel peor ConvRate
            bnd_cv_h = banda_convrate(c['p80'][c['p80']['Bookings']>0].sort_values('ConvRate').iloc[0]['ConvRate'], 1) if (c['p80']['Bookings']>0).any() else 'Crítica'
            titulo = titulo.replace('· peor ConvRate', f'· peor ConvRate {pill_b(bnd_cv_h)}')
        elif i == 8 and '#1 Sin Conv' in titulo:  # Hotel #1 Sin Conv
            titulo = titulo.replace('· #1 Sin Conv', f'· {pill_b("Sin Conversión")}')
        findings_raw[i] = {**f, 'titulo': titulo, 'desc': desc}

    resumen_canasta_html = render_resumen_ejecutivo(
        findings_raw, accent_color=CR_ACCENT, scope='canasta',
        header_title=f'Resumen Ejecutivo · Canasta {c["short"]}'
    )

    # ── Severity ──────────────────────────────────────────────────────────────
    levels_ef  = make_severity_levels(c['sev_ef'],  LEVELS_EFICACIA)
    levels_cv  = make_severity_levels(c['sev_cv'],  LEVELS_CONVRATE)
    sev_blk_ef = render_severity_block('Eficacia',  '●', '#EA0074', levels_ef, n_p80)
    sev_blk_cv = render_severity_block('ConvRate', '●', CR_ACCENT, levels_cv, n_p80)
    severity_canasta_html = render_severity_2cols(sev_blk_ef, sev_blk_cv)

    # ── Bloque Hotel · 3 tabs: Críticos · Bajo Rend · Sin Conv ───────────────
    hotel_channel_map = hotel_channel_map_global

    def panel_inner_cr(df, dim_col, dim_label, parse_hotel=False, start_idx=0):
        rows = f'<div class="panel-header"><span>{dim_label}</span><span>ConvRate</span><span>Eficacia</span><span>WoW</span></div>'
        for i, r in df.iterrows():
            raw = r[dim_col]
            if parse_hotel:
                label = truncate(clean_hotel_name(raw), 28)
                corp = clean_corp_name(r.get('CorpName',''))
                chan = hotel_channel_map.get(raw, '')
                sub = f'{corp} · {chan}' if chan and chan != corp else corp
            elif dim_col == 'CorpName':
                label = truncate(clean_corp_name(raw), 28)
                sub = ''
            elif dim_col == 'Destino':
                label = clean_destino_name(raw, 28)
                sub = ''
            else:
                label = truncate(str(raw), 28)
                sub = ''
            sub_html = f'<div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.06em;margin-top:1px;">{sub}</div>' if sub else ''
            # WoW Eficacia
            import math
            try:
                wow_v = r.get('Eficacia_WoW_pp', None) if hasattr(r, 'get') else r['Eficacia_WoW_pp']
                if wow_v is None or (isinstance(wow_v, float) and math.isnan(wow_v)): raise ValueError
                if abs(wow_v) >= 0.005:
                    mejora = wow_v > 0
                    wc = '#2F6C34' if mejora else '#C0392B'
                    wb = '#EAF3DE' if mejora else '#FCE8E6'
                    arrow = '↑' if wow_v > 0 else '↓'
                    wow_html = f'<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb};color:{wc};">{arrow}{abs(wow_v):.1f}'.replace('.', ',') + '</em>'
                else:
                    wow_html = '<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
            except:
                wow_html = '<em style="font-style:normal;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
            # Calcular data-hist W21/W20 para módulo histórico reactivo (CR canasta)
            import math as _m
            _ef21 = round(float(r['Eficacia']) * 100, 4) if r.get('Eficacia') is not None and not _m.isnan(float(r['Eficacia'])) else 0
            _ef20_raw = r.get('Eficacia_W17', None)
            _ef20 = round(float(_ef20_raw) * 100, 4) if _ef20_raw is not None and not _m.isnan(float(_ef20_raw)) else _ef21
            _cv_val = r.get('ConvRate', None)
            _cv21 = round(float(_cv_val) * 100, 4) if _cv_val is not None and not _m.isnan(float(_cv_val)) else 0
            _cv20_raw = r.get('ConvRate_W17', None)
            _cv20 = round(float(_cv20_raw) * 100, 4) if _cv20_raw is not None and not _m.isnan(float(_cv20_raw)) else _cv21
            rows += (f'<div class="panel-row" data-hist-label="{label}" '
                     f'data-hist-w21="{_ef21}" data-hist-w20="{_ef20}" '
                     f'data-hist-cv-w21="{_cv21}" data-hist-cv-w20="{_cv20}" '
                     f'style="cursor:pointer;transition:background .12s;">'
                     f'<span class="label"><div>{start_idx+i+1}. {label}</div>{sub_html}</span>'
                     f'<span class="efic">{fmt_pct2(r["ConvRate"]) if "ConvRate" in r.index else "—"}</span>'
                     f'<span class="efic">{fmt_pct2(r["Eficacia"])}</span>'
                     f'<span class="cr">{wow_html}</span>'
                     f'</div>')
        return rows

    def tab_panel_hotel(t_key, df_full, parse_hotel=False):
        """Genera panel con 2 cols explícitas (1-5 izq, 6-10 der) + filas 11-100 sb-hidden.
        Las sb-hidden quedan fuera del grid 2-col para que el JS las active en lista plana."""
        grid = '1fr 48px 48px 38px'
        sb_hid = f'sb-{idx_str}-h-{t_key}'
        def header_html(with_sb=False):
            first_col = (searchbox_header_html(sb_hid, accent_color=CR_ACCENT,
                                               placeholder='Hotel…',
                                               th_id=f'th-{sb_hid}')
                         if with_sb else
                         f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{CR_ACCENT};">Hotel</span>')
            return (f'<div style="display:grid;grid-template-columns:{grid};gap:8px;padding:0;border-bottom:2px solid {CR_ACCENT};margin-bottom:2px;">'
                    f'{first_col}'
                    f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:9px 0;">ConvRate</span>'
                    f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:9px 0;">Eficacia</span>'
                    f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;padding:9px 0;">WoW</span>'
                    f'</div>')

        col1 = col2 = ''
        hidden_rows = ''
        df_full = df_full.reset_index(drop=True)
        import math as _mh
        for i, r in df_full.iterrows():
            hotel_name = truncate(clean_hotel_name(r.get('Hotel') or '-'), 28)
            sub = clean_corp_name(r.get('CorpName',''))
            sub_html = f'<div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.05em;">{sub}</div>' if sub else ''
            ef_val = r.get('Eficacia', 0)
            cv_val = r.get('ConvRate', 0)
            ef_curr = round(float(ef_val)*100, 4) if ef_val and not _mh.isnan(float(ef_val)) else 0
            ef_prev = ef_curr - float(r.get('Eficacia_WoW_pp', 0) or 0)
            cv_curr = round(float(cv_val)*100, 4) if cv_val and not _mh.isnan(float(cv_val)) else 0
            cv_prev = cv_curr - float(r.get('ConvRate_WoW_pp', 0) or 0)
            wow_v = r.get('Eficacia_WoW_pp', None)
            if wow_v is not None and not (isinstance(wow_v, float) and _mh.isnan(float(wow_v))) and abs(wow_v) >= 0.005:
                mejora = wow_v > 0
                wc = '#2F6C34' if mejora else '#C0392B'
                wb2 = '#EAF3DE' if mejora else '#FCE8E6'
                arrow = '↑' if wow_v > 0 else '↓'
                wow_html = f'<em style="font-style:normal;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb2};color:{wc};">{arrow}{abs(wow_v):.1f}</em>'.replace('.',',')
            else:
                wow_html = '<em style="font-style:normal;font-size:9px;color:var(--ink-muted);">—</em>'
            row_html = (f'<div data-row-idx="{i}"'
                        f' data-hist-w21="{ef_curr}" data-hist-w20="{round(ef_prev,4)}"'
                        f' data-hist-cv-w21="{cv_curr}" data-hist-cv-w20="{round(cv_prev,4)}"'
                        f' data-hist-label="{hotel_name}"'
                        f' data-lbl="{hotel_name} {r.get("CorpName","")}"'
                        f' style="display:grid;grid-template-columns:{grid};gap:8px;align-items:center;padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                        f'<div><div style="font-size:11px;font-weight:600;color:{CR_ACCENT};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{i+1}. {hotel_name}</div>{sub_html}</div>'
                        f'<span style="text-align:right;font-size:11px;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_pct2(cv_val)}</span>'
                        f'<span style="text-align:right;font-size:11px;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_pct2(ef_val)}</span>'
                        f'{wow_html}</div>')
            if i < 5:
                col1 += row_html
            elif i < 10:
                col2 += row_html
            else:
                # Filas 11-100: sb-hidden, fuera del grid 2-col, lista plana
                hidden_rows += row_html.replace('<div data-row-idx=', '<div class="sb-hidden" data-row-idx=', 1)

        grid2 = f'<div class="kpi-tab-rows" style="display:grid;grid-template-columns:1fr 1fr;gap:0 24px;">'
        grid2 += f'<div>{header_html(with_sb=True)}{col1}</div>'
        grid2 += f'<div>{header_html()}{col2}</div>'
        grid2 += f'</div>'
        inner = grid2 + hidden_rows
        return f'<div class="tab-panel-c" data-tab="{t_key}">{inner}</div>'
    g_hot_w17 = D.get('g_hotel_w17', None)
    def _add_hotel_wow(df_h):
        if g_hot_w17 is None or 'Hotel' not in df_h.columns: return df_h
        out = df_h.merge(g_hot_w17[['Hotel','Eficacia_W17']], on='Hotel', how='left')
        out['Eficacia_WoW_pp'] = (out['Eficacia'] - out['Eficacia_W17']) * 100
        return out

    df_crit_c = _add_hotel_wow(p80[(p80['Bookings']>0)&(p80['BandaEficacia'].isin(['Crítica','Súper Crítica']))].sort_values('Eficacia').head(100).reset_index(drop=True))
    df_br_c   = _add_hotel_wow(p80[(p80['Bookings']>0)&(p80['BandaConvRate'].isin(['Crítica','Revisar']))].sort_values('CR_Unicos', ascending=False).head(100).reset_index(drop=True))
    df_sc_c   = _add_hotel_wow(p80[p80['Bookings']==0].sort_values('CR_Unicos', ascending=False).head(100).reset_index(drop=True))

    banda_ef_c = banda_eficacia(c['m18']['eficacia'])
    banda_cv_c = banda_convrate(c['m18']['conv_rate'], c['m18']['bookings'])
    hist_hotel_canasta = render_historico_seccion_cr(
        f'hcr-{idx_str}-hotel-ef', f'hcr-{idx_str}-hotel-cv',
        banda_ef_c, c['m18']['eficacia'],
        banda_cv_c, c['m18']['conv_rate']
    )
    bloque_hotel_html = f'''<div id="canasta-{idx_str}-hotel-cr" style="margin:32px 0 0;">
<h3 style="font-size:22px;font-weight:600;letter-spacing:-.01em;color:var(--ink);margin:0 0 12px;display:flex;align-items:center;gap:8px;"><span style="font-size:20px;">🏨</span> Análisis por hotel</h3>
<div class="tabs-block" style="background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:16px;">
<input checked id="tab-{idx_str}-h-crit" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-h-br" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-h-sc" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<div class="tabs-row" style="display:flex;gap:2px;border-bottom:1px solid var(--rule);padding-bottom:0;margin-bottom:12px;align-items:flex-end;">
<label class="tab-label" for="tab-{idx_str}-h-crit">Críticos</label>
<label class="tab-label" for="tab-{idx_str}-h-br">Bajo Rendimiento</label>
<label class="tab-label" for="tab-{idx_str}-h-sc">Sin Conversión</label>
</div>
<div class="tab-panels">
{tab_panel_hotel('crit', df_crit_c, parse_hotel=True)}
{tab_panel_hotel('br',   df_br_c,   parse_hotel=True)}
{tab_panel_hotel('sc',   df_sc_c,   parse_hotel=True)}
</div>
</div>
{hist_hotel_canasta}
</div>'''

    # ── Bloque Dimensión · 3 tabs: Corp · Destino · Channel ──────────────────
    def dim_table_with_wow(df, dim_col, dim_label, start_idx=0, sb_id=None):
        """Tabla dimensión unificada: estilos alineados con global, badges paleta D.
        sb_id: si se pasa, primera columna del header es searchbox integrado (Prop D).
        """
        import math
        grid = 'minmax(0,1fr) 68px 56px 62px 36px 62px 36px'
        headers = [dim_label, 'Checkrates', 'BKGS', 'ConvRate', 'WoW', 'Eficacia', 'WoW']
        rows = f'<div style="display:grid;grid-template-columns:{grid};gap:6px;padding:0;border-bottom:2px solid {CR_ACCENT};margin-bottom:2px;">'
        for idx_h, h in enumerate(headers):
            if idx_h == 0 and sb_id:
                rows += searchbox_header_html(sb_id, accent_color=CR_ACCENT,
                                               placeholder=f'{dim_label}…',
                                               th_id=f'th-{sb_id}')
            else:
                align = 'left' if h == dim_label else 'right'
                color = CR_ACCENT if h == dim_label else 'var(--ink-muted)'
                rows += f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{color};text-align:{align};padding:9px 0;">{h}</span>'
        rows += '</div>'
        for i, r in df.iterrows():
            row_idx = start_idx + i
            raw = r[dim_col]
            if dim_col == 'CorpName': lab = truncate(clean_corp_name(raw), 22)
            elif dim_col == 'Destino': lab = clean_destino_name(raw, 22)
            else: lab = truncate(str(raw), 22)
            bnd = banda_eficacia(r['Eficacia'])
            c_bnd = BANDA_COLORS.get(bnd, BANDA_COLORS['Sin Conversión'])
            if bnd == 'Súper Crítica':
                bg = '#FECACA'; fg = '#7F1D1D'
            else:
                bg = c_bnd['bg']; fg = c_bnd['fg']
            pill_banda = (f'<span style="display:inline-block;font-size:8px;font-weight:700;padding:1px 5px;border-radius:2px;'
                         f'background:{bg};color:{fg};text-transform:uppercase;letter-spacing:.04em;flex-shrink:0;">{bnd}</span>')
            try:
                wow_v = r['Eficacia_WoW_pp']
                if wow_v != wow_v or math.isnan(float(wow_v)): wow_v = None
            except (KeyError, TypeError, ValueError): wow_v = None
            if wow_v is not None and abs(wow_v) >= 0.005:
                mejora = wow_v > 0
                wc = '#2F6C34' if mejora else '#C0392B'
                wb = '#EAF3DE' if mejora else '#FCE8E6'
                arrow = '↑' if wow_v > 0 else '↓'
                wow_cell = f'<span style="text-align:right;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb};color:{wc};">{arrow}{abs(wow_v):.1f}</span>'.replace('.',',')
            else:
                wow_cell = f'<em style="font-style:normal;display:inline-block;font-size:9px;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
            cv_val = r.get('ConvRate', None)
            cv_str = fmt_pct2(cv_val) if cv_val is not None and not (isinstance(cv_val, float) and math.isnan(cv_val)) else '—'
            ef_curr = round(float(r['Eficacia'])*100, 4)
            ef_prev = ef_curr - float(wow_v or 0)
            cv_curr = round(float(cv_val or 0)*100, 4)
            cv_wow = r.get('ConvRate_WoW_pp', 0)
            try: cv_wow_f = float(cv_wow) if cv_wow == cv_wow else 0
            except: cv_wow_f = 0
            cv_prev = cv_curr - cv_wow_f
            hidden_cls = ' sb-hidden' if row_idx >= 10 else ''
            tbl_attr = f' data-lbl="{lab}"' if sb_id else ''
            rows += (f'<div class="{hidden_cls.strip()}" data-row-idx="{row_idx}"'
                     f' data-hist-w21="{ef_curr}" data-hist-w20="{round(ef_prev,4)}"'
                     f' data-hist-cv-w21="{cv_curr}" data-hist-cv-w20="{round(cv_prev,4)}"'
                     f' data-hist-label="{lab}"{tbl_attr}'
                     f' style="display:grid;grid-template-columns:{grid};gap:6px;align-items:center;padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                     f'<div style="display:flex;align-items:center;gap:4px;font-size:11px;font-weight:600;color:{CR_ACCENT};min-width:0;">'
                     f'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row_idx+1}. {lab}</span>{pill_banda}</div>'
                     f'<span style="text-align:right;font-size:11px;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_int_es(r["CR_Unicos"])}</span>'
                     f'<span style="text-align:right;font-size:11px;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_int_es(r["Bookings"])}</span>'
                     f'<span style="text-align:right;font-size:11px;color:var(--ink);font-variant-numeric:tabular-nums;">{cv_str}</span>'
                     f'{_fmt_wow_cv(r.get("ConvRate_WoW_pp", float("nan")))}'
                     f'<span style="text-align:right;font-size:11px;color:{CR_ACCENT};font-weight:600;font-variant-numeric:tabular-nums;">{fmt_pct2(r["Eficacia"])}</span>'
                     f'{wow_cell}</div>')
        return rows

    def tab_panel_dim_cr(t_key, df_full, dim_col, dim_label, ref_w17=None):
        sb_id_dim = f'sb-{idx_str}-d-{t_key}'
        df100 = df_full.head(100).reset_index(drop=True)
        if ref_w17 is not None and dim_col in ref_w17.columns:
            df100 = df100.merge(ref_w17[[dim_col, 'Eficacia_W17']], on=dim_col, how='left')
            df100['Eficacia_WoW_pp'] = (df100['Eficacia'] - df100['Eficacia_W17']) * 100
        rows_html = dim_table_with_wow(df100, dim_col, dim_label, start_idx=0, sb_id=sb_id_dim)
        body = f'<div class="kpi-tab-rows" style="display:grid;grid-template-columns:1fr 1fr;gap:0 24px;">{rows_html}</div>'
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'

    # Datos W17 de canasta para WoW — usar refs globales del pickle
    g_corp_w17_local = D.get('g_corp_w17', None)
    g_dest_w17_local = D.get('g_dest_w17', None)

    # Filtrar por canasta si es posible, sino usar global
    def make_ref_canasta_w17(dim_col):
        """Crea ref W17 filtrada por canasta desde el pickle."""
        key = 'g_corp_w17' if dim_col == 'CorpName' else 'g_dest_w17'
        ref = D.get(key, None)
        if ref is None: return None
        # ref ya tiene Eficacia_W17 calculada globalmente — usarla directo
        return ref

    ref_corp = make_ref_canasta_w17('CorpName')
    ref_dest = make_ref_canasta_w17('Destino')

    df_corp_dim = agg_corp.sort_values('CR_Unicos', ascending=False).head(100).reset_index(drop=True)
    df_dest_dim = agg_dest.sort_values('CR_Unicos', ascending=False).head(100).reset_index(drop=True)

    # Merge WoW channel con g_channel_w17 global
    g_ch_w17_local = D.get('g_channel_w17', None)
    def add_chan_wow(df_ch):
        if g_ch_w17_local is None: return df_ch
        out = df_ch.merge(g_ch_w17_local[['ExternalProviderName','Eficacia_W17']], on='ExternalProviderName', how='left')
        out['Eficacia_WoW_pp'] = (out['Eficacia'] - out['Eficacia_W17']) * 100
        return out

    df_pp = add_chan_wow(agg_chan[agg_chan['ExternalProviderName'].isin(PRODUCTO_PROPIO)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True))
    df_tp = add_chan_wow(agg_chan[agg_chan['ExternalProviderName'].isin(THIRD_PARTY)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True))

    def panel_inner_chan(df, color):
        import math
        has_wow = 'Eficacia_WoW_pp' in df.columns
        grid = '1fr 65px 60px 65px 45px' if has_wow else '1fr 65px 60px 65px'
        rows = f'<div style="display:grid;grid-template-columns:{grid};gap:6px;padding:5px 0;border-bottom:2px solid {color};margin-bottom:4px;">'
        for h in (['Channel','Checkrates','BKGS','Eficacia','WoW'] if has_wow else ['Channel','Checkrates','BKGS','Eficacia']):
            align = 'left' if h == 'Channel' else 'right'
            c_h = color if h == 'Channel' else 'var(--ink-muted)'
            rows += f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{c_h};text-align:{align};">{h}</span>'
        rows += '</div>'
        for i, r in df.head(10).reset_index(drop=True).iterrows():
            ef_val = r.get('Eficacia', None)
            ef_str = fmt_pct2(ef_val) if ef_val is not None and not (isinstance(ef_val, float) and (math.isnan(ef_val) or math.isinf(ef_val))) else '—'
            wow_html = ''
            if has_wow:
                try:
                    wow_v = r['Eficacia_WoW_pp']
                    if wow_v != wow_v or math.isnan(float(wow_v)): raise ValueError
                    if ef_val is not None and abs(float(ef_val) - 1.0) < 0.0001:
                        wow_html = '<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 3px;border-radius:3px;background:#EAF3DE;color:#2F6C34;text-align:center;">= 0,0</em>'
                    elif abs(wow_v) >= 0.005:
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'
                        wb = '#EAF3DE' if mejora else '#FCE8E6'
                        arrow = '↑' if wow_v > 0 else '↓'
                        txt = f'{arrow}{abs(wow_v):.1f}'.replace('.', ',')
                        wow_html = f'<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 3px;border-radius:3px;background:{wb};color:{wc};text-align:center;">{txt}</em>'
                    else:
                        wow_html = '<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 3px;border-radius:3px;background:#F2EEE6;color:#8A8377;text-align:center;">—</em>'
                except:
                    wow_html = '<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 3px;border-radius:3px;background:#F2EEE6;color:#8A8377;text-align:center;">—</em>'
            rows += (f'<div style="display:grid;grid-template-columns:{grid};gap:6px;align-items:center;padding:5px 0;border-bottom:1px solid var(--rule-soft);font-size:11px;">'
                     f'<span style="font-weight:600;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{i+1}. {truncate(r["ExternalProviderName"],20)}</span>'
                     f'<span style="text-align:right;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_int_es(r["CR_Unicos"])}</span>'
                     f'<span style="text-align:right;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_int_es(r["Bookings"])}</span>'
                     f'<span style="text-align:right;color:{color};font-weight:600;font-variant-numeric:tabular-nums;">{ef_str}</span>'
                     f'{wow_html}</div>')
        return rows

    panel_chan = (
        f'<div class="tab-panel-c" data-tab="channel">'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">'
        f'<div><div style="font-size:10px;font-weight:700;color:{CR_ACCENT};letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>'
        f'{panel_inner_chan(df_pp, CR_ACCENT)}</div>'
        f'<div><div style="font-size:10px;font-weight:700;color:var(--ink-muted);letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>'
        f'{panel_inner_chan(df_tp, CR_ACCENT)}</div>'
        f'</div></div>'
    )

    hist_dim_canasta = render_historico_seccion_cr(
        f'hcr-{idx_str}-dim-ef', f'hcr-{idx_str}-dim-cv',
        banda_ef_c, c['m18']['eficacia'],
        banda_cv_c, c['m18']['conv_rate']
    )
    bloque_dim_html = f'''<div id="canasta-{idx_str}-dim-cr" style="margin:32px 0 32px;">
<h3 style="font-size:22px;font-weight:600;letter-spacing:-.01em;color:var(--ink);margin:24px 0 12px;display:flex;align-items:center;gap:8px;"><span style="font-size:20px;">📊</span> Análisis por dimensión</h3>
<div class="tabs-block" style="background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:8px 16px 16px;">
<input checked id="tab-{idx_str}-d-corp" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-d-dest" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-d-channel" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<div class="tabs-row" style="display:flex;gap:2px;border-bottom:1px solid var(--rule);padding-bottom:0;margin-bottom:12px;align-items:flex-end;">
<label class="tab-label" for="tab-{idx_str}-d-corp">Corporativo</label>
<label class="tab-label" for="tab-{idx_str}-d-dest">Destino</label>
<label class="tab-label" for="tab-{idx_str}-d-channel">Channel</label>
</div>
<div class="tab-panels">
{tab_panel_dim_cr('corp', df_corp_dim, 'CorpName', 'Corporativo', ref_w17=ref_corp)}
{tab_panel_dim_cr('dest', df_dest_dim, 'Destino',  'Destino', ref_w17=ref_dest)}
{panel_chan}
</div>
</div>
{hist_dim_canasta}
</div>'''

    # ── CSS dinámico por canasta ──────────────────────────────────────────────
    extra_css = f'''<style>
/* Base tab-label estado inactivo — asegura efecto folder en canastas */
#tab-{idx_str}-h-crit ~ .tabs-row label[for^="tab-{idx_str}-h-"],
#tab-{idx_str}-d-corp  ~ .tabs-row label[for^="tab-{idx_str}-d-"]{{
  padding:8px 14px;font-size:10px;font-weight:600;color:var(--ink-muted);text-transform:uppercase;
  letter-spacing:.06em;cursor:pointer;border-radius:6px 6px 0 0;
  border:1px solid transparent;border-bottom:none;user-select:none;
  transition:all .15s;margin-bottom:-1px;display:inline-block;
}}
/* Tab activo — estilo folder conectado */
#tab-{idx_str}-h-crit:checked ~ .tabs-row label[for="tab-{idx_str}-h-crit"],
#tab-{idx_str}-h-br:checked   ~ .tabs-row label[for="tab-{idx_str}-h-br"],
#tab-{idx_str}-h-sc:checked   ~ .tabs-row label[for="tab-{idx_str}-h-sc"],
#tab-{idx_str}-d-corp:checked    ~ .tabs-row label[for="tab-{idx_str}-d-corp"],
#tab-{idx_str}-d-dest:checked    ~ .tabs-row label[for="tab-{idx_str}-d-dest"],
#tab-{idx_str}-d-channel:checked ~ .tabs-row label[for="tab-{idx_str}-d-channel"]{{
  background:var(--paper);color:{CR_ACCENT};font-weight:700;
  border:1px solid var(--rule);border-bottom:1px solid var(--paper);
}}
#tab-{idx_str}-h-crit:checked ~ .tab-panels .tab-panel-c[data-tab="crit"],
#tab-{idx_str}-h-br:checked   ~ .tab-panels .tab-panel-c[data-tab="br"],
#tab-{idx_str}-h-sc:checked   ~ .tab-panels .tab-panel-c[data-tab="sc"],
#tab-{idx_str}-d-corp:checked    ~ .tab-panels .tab-panel-c[data-tab="corp"],
#tab-{idx_str}-d-dest:checked    ~ .tab-panels .tab-panel-c[data-tab="dest"],
#tab-{idx_str}-d-channel:checked ~ .tab-panels .tab-panel-c[data-tab="channel"]{{display:block !important;}}
/* KPI tabs canasta */
#tab-{idx_str}-ef-destino:checked ~ .tab-panels .tab-panel[data-tab="destino"],
#tab-{idx_str}-ef-corp:checked    ~ .tab-panels .tab-panel[data-tab="corp"],
#tab-{idx_str}-ef-hotel:checked   ~ .tab-panels .tab-panel[data-tab="hotel"],
#tab-{idx_str}-cv-destino:checked ~ .tab-panels .tab-panel[data-tab="destino"],
#tab-{idx_str}-cv-corp:checked    ~ .tab-panels .tab-panel[data-tab="corp"],
#tab-{idx_str}-cv-hotel:checked   ~ .tab-panels .tab-panel[data-tab="hotel"]{{display:block !important;}}
#tab-{idx_str}-ef-destino:checked ~ .tabs-row label[for="tab-{idx_str}-ef-destino"],
#tab-{idx_str}-ef-corp:checked    ~ .tabs-row label[for="tab-{idx_str}-ef-corp"],
#tab-{idx_str}-ef-hotel:checked   ~ .tabs-row label[for="tab-{idx_str}-ef-hotel"],
#tab-{idx_str}-cv-destino:checked ~ .tabs-row label[for="tab-{idx_str}-cv-destino"],
#tab-{idx_str}-cv-corp:checked    ~ .tabs-row label[for="tab-{idx_str}-cv-corp"],
#tab-{idx_str}-cv-hotel:checked   ~ .tabs-row label[for="tab-{idx_str}-cv-hotel"]{{
  background:var(--paper);color:{CR_ACCENT};border:1px solid var(--rule);border-bottom:1px solid var(--paper);
}}
</style>'''

    # ── Plan de Acción ────────────────────────────────────────────────────────
    canasta_label = c['short']
    h_top_crit = df_crit_c.iloc[0] if len(df_crit_c)>0 else None
    h_top_sc   = df_sc_c.iloc[0]   if len(df_sc_c)>0   else None

    plan_rows = ''
    if h_top_crit is not None:
        plan_rows += (
            f'<div class="action-row qw">'
            f'<div class="action-owner-badge">Supply Optimization</div>'
            f'<div class="accion">Escalar caso Crítico de canasta {canasta_label}: <strong>{truncate(clean_hotel_name(h_top_crit["Hotel"]),38)}</strong> ({h_top_crit["CorpName"]}) con Eficacia {fmt_pct2(h_top_crit["Eficacia"])} y {fmt_int_es(h_top_crit["CR_Unicos"])} CR.</div>'
            f'<div class="action-meta-bottom"><span class="cluster-tag">Quick Win</span><span class="meta-item"><strong>Plazo</strong> 5 días</span><span class="meta-item"><strong>Métrica</strong> Eficacia &gt; 85%</span></div>'
            f'</div>'
        )
    if h_top_sc is not None:
        plan_rows += (
            f'<div class="action-row qw">'
            f'<div class="action-owner-badge">Supply Optimization / TPS</div>'
            f'<div class="accion">Diagnóstico técnico de <strong>{truncate(clean_hotel_name(h_top_sc["Hotel"]),38)}</strong> ({fmt_int_es(h_top_sc["CR_Unicos"])} CR sin BKGS) en canasta {canasta_label} · revisar mapping y paridad.</div>'
            f'<div class="action-meta-bottom"><span class="cluster-tag">Quick Win</span><span class="meta-item"><strong>Plazo</strong> 1 semana</span><span class="meta-item"><strong>Métrica</strong> Bookings &gt; 0</span></div>'
            f'</div>'
        )
    plan_rows += (
        f'<div class="action-row mp">'
        f'<div class="action-owner-badge">Supply Optimization</div>'
        f'<div class="accion">Plan de saneamiento para <strong>{fmt_int_es(n_critmas_local)} hoteles Crítica+</strong> de Eficacia en canasta {canasta_label}.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority</span><span class="meta-item"><strong>Plazo</strong> 3 semanas</span><span class="meta-item"><strong>Métrica</strong> {int(n_critmas_local*0.5)} a Revisar</span></div>'
        f'</div>'
        f'<div class="action-row mp">'
        f'<div class="action-owner-badge">Supply Comercial / Wholesale</div>'
        f'<div class="accion">Revisión de ConvRate de canasta {canasta_label} (actual {fmt_pct2(cv_w18)}) frente al target ≥ 2,5%.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority</span><span class="meta-item"><strong>Plazo</strong> 2 semanas</span><span class="meta-item"><strong>Métrica</strong> ConvRate ↑</span></div>'
        f'</div>'
        f'<div class="action-row es">'
        f'<div class="action-owner-badge">Supply Comercial / Supply Optimization</div>'
        f'<div class="accion">Reducir <strong>cohorte Sin Conversión</strong> de canasta {canasta_label} ({fmt_int_es(n_sc_total)} hoteles) · proyecto trimestral de remediación.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Estratégica</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> -25% vs baseline</span></div>'
        f'</div>'
        f'<div class="action-row es">'
        f'<div class="action-owner-badge">Supply Comercial / Wholesale</div>'
        f'<div class="accion">Auditar canales de mayor share en canasta {canasta_label} y optimizar paridad/latencia con principales corp.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Estratégica</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> Eficacia &gt; 95%</span></div>'
        f'</div>'
    )

    plan_canasta_html = f'''<div style="margin-top:48px;padding-top:40px;border-top:1px solid var(--rule);">
<h3 style="font-size:13px;font-weight:700;color:{CR_ACCENT};text-transform:uppercase;letter-spacing:.10em;margin:0 0 10px;">Plan de Acción · canasta {canasta_label}</h3>
<div class="action-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{plan_rows}</div>
{render_seguimiento_block(SEGUIMIENTO_FILE_CR, accent_color=CR_ACCENT)}
</div>'''

    # ── Banner Excel ──────────────────────────────────────────────────────────
    file_map = {'op':'OP','cug':'CUG','b2c':'B2C'}
    file_suffix = file_map.get(idx_str, 'B2C')
    excel_url = f'Analisis_Checkrates_{file_suffix}_7d.xlsx'
    banner = f'''<div class="detail-callout">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de cada óptica está en pestañas separadas del Excel adjunto · <strong>Canasta {c["short"]}</strong>.</div></div>
<a class="badge-link" href="{excel_url}">Excel ↗</a>
</div>'''

    return f'''{extra_css}<details class="canasta-block" style="margin-bottom:32px;">
<summary>
<div class="summary-title">
<h2>Canasta {c["short"]}</h2>
<span class="section-subtitle">{c["name"]}</span>
</div>
<span class="toggle-arrow"><span class="label"></span><span class="icon"></span></span>
</summary>
<div class="canasta-content">
{kpi_block}
{alertas_canasta_html}
{resumen_canasta_html}
{severity_canasta_html}
{bloque_hotel_html}
{bloque_dim_html}
{plan_canasta_html}
{banner}
</div>
</details>
'''


# ── Build ─────────────────────────────────────────────────────────────────────
CANASTA_SECTION = f'''<section id="por-canasta">
<div class="section-head">
<div>
<div class="section-num">Sección 12</div>
<h2 class="section-title">📦 Análisis por canasta</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">B2C · B2B-OP · CUG</span>
<p class="section-kicker">Métricas, severidad y casos críticos por canasta. CUG y B2B-OP tienen weight 0,6 (prioridad estratégica). B2C tiene weight 0,1 pero no se elimina del análisis.</p>
</div>
</div>
'''
for idx_key, c_key in [('op','B2B-OP'),('cug','CUG'),('b2c','B2C')]:
    CANASTA_SECTION += render_canasta_block(CANASTA[c_key], idx_str=idx_key)
CANASTA_SECTION += '</section>\n'
CANASTA_SECTION += FOOTER

with open('part3_cr.html','w') as f:
    f.write(CANASTA_SECTION)
print(f"Part 3 CR escrito: {len(CANASTA_SECTION):,} chars")
