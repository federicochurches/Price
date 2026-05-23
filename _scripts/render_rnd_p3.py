"""
Renderer RND parte 3: Análisis por Canasta (B2C, B2B-OP, CUG)
Cards colapsables con KPIs hero + tabs Top 5
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
import os, pandas as pd, numpy as np
from engine import *
from render_helpers import *

from historico_module_rnd import render_historico_rnd

with open(os.getenv('PICKLE_RND', 'rnd_w20_data.pkl'),'rb') as f:
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


with open('asset_rnd_footer.html') as f: FOOTER = f.read()


# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

def _build_canasta_findings_rnd(c):
    """10 findings para Resumen Ejecutivo dentro de canasta RND."""
    m18 = c['m18']; m17 = c['m17']
    pct = m18['pct_nodispo']; rpm_v = m18['rpm']
    pct17 = m17['pct_nodispo']; rpm17_v = m17['rpm']
    pct_wow = (pct-pct17)*100
    rpm_wow = (rpm_v/rpm17_v-1)*100 if rpm17_v else 0
    n_p80 = len(c['p80'])
    n_critmas_nd = c['sev_nd'].get('Súper Crítica',0) + c['sev_nd'].get('Crítica',0)
    n_supcrit_nd = c['sev_nd'].get('Súper Crítica',0)
    n_sc = c['sev_rpm'].get('Sin Conversión',0)
    n_crit_rpm = c['sev_rpm'].get('Crítica',0)
    
    canasta_label = c['short']
    weight_label = {'B2C':'0,1','B2B Opaco':'0,3','CUG':'0,6'}.get(canasta_label, '—')
    
    h_top_dnc_pool = c['p80'].sort_values('Trafico', ascending=False)
    h_top_dnc = h_top_dnc_pool.iloc[0] if len(h_top_dnc_pool)>0 else None
    h_worst_nd_pool = c['p80'][c['p80']['Trafico']>c['p80']['Trafico'].quantile(0.50)]
    h_worst_nd = h_worst_nd_pool.sort_values('%NoDispo', ascending=False).iloc[0] if len(h_worst_nd_pool)>0 else None
    h_worst_rpm_pool = c['p80'][(c['p80']['Bookings']>0) & (c['p80']['RPM']>0)]
    h_worst_rpm = h_worst_rpm_pool.sort_values('RPM').iloc[0] if len(h_worst_rpm_pool)>0 else None
    
    top_corp_pool = c['agg_corp'][c['agg_corp']['Trafico']>5_000_000].sort_values('Trafico', ascending=False)
    top1_corp = top_corp_pool.iloc[0] if len(top_corp_pool)>0 else None
    top2_corp = top_corp_pool.iloc[1] if len(top_corp_pool)>1 else None
    
    def es_pct(v, dec=2): return f'{v:.{dec}f}%'.replace('.',',')
    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}'.replace('.',',')
    def es_pct1(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.1f}%'.replace('.',',')
    def es_int(v): return fmt_int_es(int(v))
    def es_num2(v): return fmt_num2(v)
    
    findings = [
        {'numero': es_pct(pct*100,2),
         'titulo': f'% NoDispo · banda {m18["banda_nodispo"]}',
         'desc': f'Tasa de búsquedas sin disponibilidad en canasta {canasta_label}. WoW {es_pp(pct_wow)} · weight estratégico {weight_label}.'},
        {'numero': '$' + es_num2(rpm_v),
         'titulo': f'IPM (Income Per Million USD) · banda {m18["banda_rpm"]}',
         'desc': f'Income Per Million · GB USD por millón en {canasta_label}. WoW {es_pct1(rpm_wow)} · target ≥ $650.'},
        {'numero': es_int(n_critmas_nd),
         'titulo': 'Hoteles Severity %NoDispo Crítica+',
         'desc': f'%NoDispo &gt; 20% · {n_supcrit_nd} Súper Críticos requieren escalamiento técnico inmediato.'},
        {'numero': es_int(n_sc),
         'titulo': 'Hoteles P80 Sin Conversión (BKGS=0)',
         'desc': f'{es_pct(n_sc/max(n_p80,1)*100,1)} del P80 sin convertir · cohorte estructural · diagnóstico técnico/contractual, no de eficacia.'},
        {'numero': es_int(n_crit_rpm),
         'titulo': 'Hoteles Severity IPM Crítica',
         'desc': f'IPM &lt; $200 · revisar pricing, posicionamiento y velocidad de respuesta · evitar escalamiento a Sin Conv.'},
    ]
    if h_worst_nd is not None:
        findings.append({
            'numero': es_pct(h_worst_nd['%NoDispo']*100,2),
            'titulo': f'{truncate(clean_hotel_name(h_worst_nd["Hotel"]),28)} · peor %NoDispo',
            'desc': f'{fmt_big(h_worst_nd["Trafico"])} búsquedas · {h_worst_nd["CorpName"]} · escalamiento individual prioritario.'
        })
    if top1_corp is not None and top2_corp is not None:
        findings.append({
            'numero': fmt_big(top1_corp["Trafico"]),
            'titulo': f'<strong>{top1_corp["CorpName"]}</strong> · líder tráfico',
            'desc': f'Junto con {top2_corp["CorpName"]} concentran el grueso del volumen en {canasta_label} · concentración crítica.'
        })
    if h_worst_rpm is not None:
        findings.append({
            'numero': '$' + es_num2(h_worst_rpm['RPM']),
            'titulo': f'{truncate(clean_hotel_name(h_worst_rpm["Hotel"]),28)} · peor IPM',
            'desc': f'BKGS {int(h_worst_rpm["Bookings"])} · {h_worst_rpm["CorpName"]} · pricing y matching técnico requieren revisión.'
        })
    if h_top_dnc is not None:
        findings.append({
            'numero': fmt_big(h_top_dnc["Trafico"]),
            'titulo': f'{truncate(clean_hotel_name(h_top_dnc["Hotel"]),28)} · #1 tráfico',
            'desc': f'%NoDispo {es_pct(h_top_dnc["%NoDispo"]*100,2)} · {h_top_dnc["CorpName"]} · caso de mayor palanca de impacto.'
        })
    findings.append({
        'numero': es_int(n_p80),
        'titulo': 'Hoteles P80 analizados',
        'desc': f'Universo de análisis · base estable para diagnóstico de la canasta {canasta_label}.'
    })
    while len(findings) < 10:
        findings.append({'numero': '—', 'titulo': 'Dato no disponible', 'desc': 'Cohorte insuficiente para finding adicional esta semana.'})
    return findings[:10]


def _render_canasta_alertas_rnd(c, accent_color='#EA0074'):
    """Alertas Críticas dentro de canasta RND · 3 cards (Hoteles · Destinos · Corp)."""
    from template_alertas import render_alertas_block, render_alert_card, render_alert_subcell

    p80 = c['p80']
    agg_dest = c.get('agg_dest', None)
    agg_corp = c.get('agg_corp', None)

    def worst_nd(df, col):
        return df.sort_values('%NoDispo', ascending=False).iloc[0] if len(df) > 0 else None

    def worst_ipm(df, col):
        sub = df[df.get('IPM', df.get('RPM', 0).__class__(0)) > 0] if 'IPM' in df.columns else df
        if len(sub) == 0: sub = df
        return sub[sub['IPM'] > 0].sort_values('IPM', ascending=True).iloc[0] if len(sub[sub['IPM'] > 0]) > 0 else None

    def card_for(card_title, icon, df, label_col, label_fn=None):
        nd_obj  = worst_nd(df, label_col)
        rpm_obj = worst_ipm(df, label_col)
        if nd_obj is None or rpm_obj is None:
            return ''
        lbl_nd  = label_fn(nd_obj[label_col])  if label_fn else truncate(str(nd_obj[label_col]), 22)
        lbl_rpm = label_fn(rpm_obj[label_col]) if label_fn else truncate(str(rpm_obj[label_col]), 22)
        sub_nd = render_alert_subcell(
            '% NoDispo', '#EA0074', '#FCE4F1', lbl_nd,
            f'{nd_obj["%NoDispo"]*100:.2f}%'.replace('.',','), '#EA0074'
        )
        ipm_val = max(rpm_obj.get('IPM', rpm_obj.get('RPM', 0)), 0)
        sub_rpm = render_alert_subcell(
            'IPM', '#5C469C', '#EDE8F7', lbl_rpm,
            f'${fmt_num2(ipm_val)}', '#5C469C'
        )
        return render_alert_card(card_title, icon, accent_color, sub_nd, sub_rpm)

    card_h  = card_for('Hoteles',  '🏨', p80, 'Hotel',
                        lambda x: truncate(clean_hotel_name(str(x)), 22))
    card_d  = card_for('Destinos', '📍', agg_dest, 'Destino',
                        lambda x: clean_destino_name(str(x), 22)) if agg_dest is not None else ''
    card_co = card_for('Corp',     '🏢', agg_corp, 'CorpName',
                        lambda x: clean_corp_name(str(x), 22)) if agg_corp is not None else ''

    return render_alertas_block(
        f'Alertas · Casos Críticos · Canasta {c["short"]}',
        accent_color, card_h, card_d, card_co
    )


def render_canasta_block(canasta_data, idx_str='b2c'):
    from template_resumen import render_resumen_ejecutivo
    from template_severity import render_severity_block, render_severity_2cols, make_severity_levels, LEVELS_NODISPO, LEVELS_RPM

    c = canasta_data
    m18 = c['m18']; m17 = c['m17']
    pct_w18 = m18['pct_nodispo']; pct_w17 = m17['pct_nodispo']
    rpm_w18 = m18['rpm']; rpm_w17 = m17['rpm']
    pct_wow = (pct_w18 - pct_w17) * 100
    rpm_wow = (rpm_w18/rpm_w17 - 1) * 100 if rpm_w17 else 0

    banda_nd = banda_nodispo(pct_w18)
    banda_rp = banda_rpm(rpm_w18, m18['bookings'])

    n_p80 = len(c['p80'])
    n_sc = (c['p80']['Bookings']==0).sum()
    n_sc_total = (c['agg_hotel']['Bookings']==0).sum()

    # ── Helpers pills ────────────────────────────────────────────────────────
    def get_pill(name, wow_map):
        for key, (txt, mejora) in wow_map.items():
            if key.lower() in name.lower() or name.lower() in key.lower():
                if txt is None:
                    return '<em class="wow-pill nd">—</em>'
                return f'<em class="wow-pill {"dn" if mejora else "up"}">{txt}</em>'
        return '<em class="wow-pill nd">—</em>'

    # WoW por dimensión de canasta (datos del merge en calc_rnd)
    tab_nd  = c.get('tab_nd',  {})   # dict con keys pais/destino/corp → DataFrame con NoDispo_WoW_pp
    tab_rpm = c.get('tab_rpm', {})   # idem con RPM_WoW_pct

    # ── KPI cards con gauge + wow_box + tabs ─────────────────────────────────
    def wow_box_canasta(v17, v18, wow_str, wow_color, accent):
        return f'''<div style="margin-top:14px;background:var(--paper);border-radius:4px;padding:8px;display:flex;align-items:stretch;gap:8px;">
<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W{WEEK_NUM_INT-1}</div>
  <div style="font-size:16px;font-weight:700;color:var(--ink-soft);margin-top:2px;">{v17}</div>
</div>
<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W{WEEK_NUM_INT}</div>
  <div style="font-size:16px;font-weight:700;color:{accent};margin-top:2px;">{v18}</div>
</div>
<div style="flex:1;text-align:center;background:{'#E0F0E2' if wow_color=='#2F6C34' else '#FCE4F1'};padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:{wow_color};font-weight:700;">WoW</div>
  <div style="font-size:16px;font-weight:700;color:{wow_color};margin-top:2px;">{wow_str}</div>
</div>
</div>'''

    def gauge_canasta(banda, tipo):
        return gauge_5levels(banda, tipo)

    def tab_rows_canasta(df, dim_col, parse_hotel=False, wow_map=None, val_col='%NoDispo', val_prefix='', is_rpm=False):
        """Genera filas de tab con grid 1fr 52px 44px + pills WoW real desde NoDispo_WoW_pp."""
        import math
        rows_l, rows_r = '', ''
        df10 = df.head(10).reset_index(drop=True)  # máximo 10, siempre
        for i, r in df10.iterrows():
            raw = r[dim_col]
            if parse_hotel:
                lab = truncate(clean_hotel_name(str(raw)), 22)
            elif dim_col == 'PaisDestino':
                lab = clean_pais_name(str(raw), max_len=20)
            elif dim_col == 'Destino':
                lab = clean_destino_name(str(raw), 20)
            elif dim_col == 'CorpName':
                lab = clean_corp_name(str(raw), 22)
            else:
                lab = truncate(str(raw), 22)
            val = r.get(val_col, 0)
            if is_rpm:
                val = max(val, 0)  # sin negativos
                val_str = f'${fmt_num2(val)}'
            else:
                val_str = fmt_pct2(val)
            # WoW directo desde columna NoDispo_WoW_pp o IPM_WoW_pp
            wow_col = 'IPM_WoW_pp' if is_rpm else 'NoDispo_WoW_pp'
            wow_v = r.get(wow_col, None)
            if wow_v is None or (isinstance(wow_v,float) and (math.isnan(wow_v) or math.isinf(wow_v))):
                wow_html = '<em class="wow-pill nd">—</em>'
            elif is_rpm:
                ipm_base = r.get('IPM_W18', 0)
                if abs(wow_v) < 1 or ipm_base <= 0:
                    wow_html = '<em class="wow-pill nd">—</em>'
                else:
                    wow_pct = (wow_v / ipm_base) * 100
                    mejora = wow_pct > 0
                    cls = 'dn' if mejora else 'up'
                    wow_html = f'<em class="wow-pill {cls}">{"↑" if wow_pct>0 else "↓"}{abs(wow_pct):.1f}%</em>'.replace('.',',')
            else:
                if abs(wow_v) < 0.05:
                    wow_html = '<em class="wow-pill nd">—</em>'
                else:
                    mejora = wow_v < 0  # bajar NoDispo = mejora
                    cls = 'dn' if mejora else 'up'
                    wow_html = f'<em class="wow-pill {cls}">{"↓" if wow_v<0 else "↑"}{abs(wow_v):.2f}</em>'.replace('.',',')
            import math as _mrnd
            if is_rpm:
                _w21h = round(float(max(val,0)), 2)
                _w20h_raw = r.get('IPM_W18', r.get('IPM_W17', None))
                try: _w20h = round(float(_w20h_raw),2) if _w20h_raw is not None and not _mrnd.isnan(float(_w20h_raw)) else _w21h
                except: _w20h = _w21h
            else:
                _w21h = round(float(val)*100, 4) if val and not _mrnd.isnan(float(val)) else 0
                _w20h_raw = r.get('NoDispo_W17', None)
                try: _w20h = round(float(_w20h_raw)*100,4) if _w20h_raw is not None and not _mrnd.isnan(float(_w20h_raw)) else _w21h
                except: _w20h = _w21h
            cell = (f'<div style="display:grid;grid-template-columns:1fr 52px 44px;align-items:baseline;gap:4px;cursor:pointer;border-radius:3px;transition:background .12s;"'
                    f' data-hist-w21="{_w21h}" data-hist-w20="{_w20h}" data-hist-label="{lab}">'
                    f'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;color:var(--ink);font-weight:400;">{i+1}. {lab}</span>'
                    f'<span style="text-align:right;font-size:11px;">{val_str}</span>'
                    f'{wow_html}</div>')
            if i < 5:
                rows_l += cell
            else:
                rows_r += cell
        if rows_r:
            return (f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:14px;">'
                    f'<div>{rows_l}</div><div>{rows_r}</div></div>')
        return rows_l

    def kpi_card_canasta(metric, val18, val17, banda, pill_target, wow_str, wow_color,
                          gauge_tipo, df_tabs, tab_configs, prefix='', card_id=''):
        pill = banda_pill(banda, target=pill_target, font_size='11px')
        pill_with_target = pill + target_caption(pill_target, font_size='10px')
        gauge = gauge_canasta(banda, gauge_tipo)
        val18_str = fmt_pct2(val18) if prefix == '' else f'${fmt_num2(val18)}'
        val17_str = fmt_pct2(val17) if prefix == '' else f'${fmt_num2(val17)}'
        wb = wow_box_canasta(val17_str, val18_str, wow_str, wow_color, '#EA0074')

        # CSS + JS para pestaña activa — JS es más robusto dentro de divs anidados
        js_tabs = f'''<script>
(function(){{
  var card = document.getElementById('kpi-{card_id}');
  if(!card) return;
  var inputs = card.querySelectorAll('input[name="tabs-{card_id}"]');
  function activate(inp){{
    card.querySelectorAll('.tp-{card_id}').forEach(function(p){{p.style.display='none';}});
    card.querySelectorAll('label[for^="tab-{card_id}"]').forEach(function(l){{
      l.style.color='';l.style.borderColor='transparent';l.style.background='';
    }});
    var panel = card.querySelector('.tp-{card_id}[data-tab="'+inp.dataset.tab+'"]');
    if(panel) panel.style.display='block';
    var lbl = card.querySelector('label[for="'+inp.id+'"]');
    if(lbl){{lbl.style.color='#EA0074';lbl.style.borderColor='#EA0074';lbl.style.background='var(--paper)';}}
  }}
  inputs.forEach(function(inp){{
    inp.addEventListener('change',function(){{activate(inp);}});
  }});
  var first = card.querySelector('input[checked]')||inputs[0];
  if(first) activate(first);
}})();
</script>'''

        tabs_inputs = ''.join(
            f'<input {"checked " if i==0 else ""}id="tab-{card_id}-{tk}" data-tab="{tk}" name="tabs-{card_id}" style="display:none;" type="radio"/>'
            for i,(tk,_,_,_,_) in enumerate(tab_configs)
        )
        tabs_labels = ''.join(
            f'<label class="tab-label" for="tab-{card_id}-{tk}">{tl}</label>'
            for tk, tl, _, _, _ in tab_configs
        )
        panels = ''
        for tk, tl, df_t, wm, is_rpm in tab_configs:
            dim_col = {'pais':'PaisDestino','destino':'Destino','corp':'CorpName','hotel':'Hotel'}.get(tk, tk)
            parse_hotel = tk == 'hotel'
            val_col = 'RPM' if is_rpm else '%NoDispo'
            panel_html = tab_rows_canasta(df_t, dim_col, parse_hotel, wm, val_col, prefix, is_rpm)
            panels += f'<div class="tp-{card_id}" data-tab="{tk}" style="display:none;margin-top:10px;">{panel_html}</div>'

        metric_type_hist = 'ipm' if prefix != '' else 'nodispo'
        hist_mod = render_historico_rnd(metric_type_hist, banda, val18, f'hrnd-{card_id}')
        return f'''<div class="kpi-card" id="kpi-{card_id}" style="border:1px solid var(--rule);padding:18px 20px;border-radius:3px;background:var(--paper);">
{tabs_inputs}
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">{metric}</div>
<div style="font-size:42px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;margin-top:4px;">{val18_str}</div>
<div style="margin-top:10px;">{pill_with_target}</div>
{gauge}
{wb}
<div style="display:flex;gap:0;margin-top:14px;border-bottom:1px solid var(--rule);">{tabs_labels}</div>
{panels}
{hist_mod}
{js_tabs}
</div>'''

    # Datos de tabs para canasta — con WoW desde agg_corp/dest/pais
    def _enrich_wow(df_tab, df_agg, col):
        """Merge WoW desde agg si no está en df_tab."""
        if 'NoDispo_WoW_pp' not in df_tab.columns and 'NoDispo_WoW_pp' in df_agg.columns:
            df_tab = df_tab.merge(df_agg[[col,'NoDispo_WoW_pp']].drop_duplicates(col), on=col, how='left')
        if 'IPM_WoW_pp' not in df_tab.columns and 'IPM_W18' in df_agg.columns:
            if 'IPM_W18' not in df_tab.columns:
                df_tab = df_tab.merge(df_agg[[col,'IPM_W18']].drop_duplicates(col), on=col, how='left')
            if 'IPM' in df_tab.columns:
                df_tab['IPM_WoW_pp'] = df_tab['IPM'] - df_tab.get('IPM_W18', df_tab['IPM'])
        return df_tab

    agg_dest = c.get('agg_dest', D['g_dest'])
    agg_corp = c.get('agg_corp', D['g_corp'])
    agg_pais = c.get('agg_pais', D['g_pais'])

    MIN_T = 500_000  # mínimo tráfico para tabs de dimensión

    df_dest = _enrich_wow(agg_dest[agg_dest['Trafico']>=MIN_T].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True), agg_dest, 'Destino')
    df_corp = _enrich_wow(agg_corp[agg_corp['Trafico']>=MIN_T].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True), agg_corp, 'CorpName')
    df_hot  = c['p80'].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True)
    df_pais = _enrich_wow(agg_pais[agg_pais['Trafico']>=MIN_T].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True), agg_pais, 'PaisDestino')
    df_dest_rpm = _enrich_wow(agg_dest[(agg_dest['IPM']>0)&(agg_dest['Trafico']>=MIN_T)].sort_values('IPM').head(10).reset_index(drop=True), agg_dest, 'Destino')
    df_corp_rpm = _enrich_wow(agg_corp[(agg_corp['IPM']>0)&(agg_corp['Trafico']>=MIN_T)].sort_values('IPM').head(10).reset_index(drop=True), agg_corp, 'CorpName')
    df_hot_rpm  = c['p80'][(c['p80']['Bookings']>0)&(c['p80']['IPM']>0)].sort_values('IPM').head(10).reset_index(drop=True)
    df_pais_rpm = _enrich_wow(agg_pais[(agg_pais['IPM']>0)&(agg_pais['Trafico']>=MIN_T)].sort_values('IPM').head(10).reset_index(drop=True), agg_pais, 'PaisDestino')

    wow_nd_dest = tab_nd.get('destino', {}); wow_nd_corp = tab_nd.get('corp', {}); wow_nd_pais = tab_nd.get('pais', {})
    wow_rpm_dest = tab_rpm.get('destino', {}); wow_rpm_corp = tab_rpm.get('corp', {}); wow_rpm_pais = tab_rpm.get('pais', {})

    wow_color_nd = '#2F6C34' if pct_wow < 0 else '#C0392B'
    wow_color_rp = '#2F6C34' if rpm_wow > 0 else '#C0392B'
    wow_str_nd = (f'↓ {abs(pct_wow):.2f}pp' if pct_wow < 0 else f'↑ +{pct_wow:.2f}pp').replace('.', ',')
    wow_str_rp = (f'↑ +{rpm_wow:.1f}%' if rpm_wow > 0 else f'↓ {rpm_wow:.1f}%').replace('.', ',')

    tabs_nd = [
        ('pais',    'País',    df_pais,     wow_nd_pais,  False),
        ('destino', 'Destino', df_dest,     wow_nd_dest,  False),
        ('corp',    'Corp',    df_corp,     wow_nd_corp,  False),
        ('hotel',   'Hotel',   df_hot,      None,         False),
    ]
    tabs_rpm = [
        ('pais',    'País',    df_pais_rpm, wow_rpm_pais, True),
        ('destino', 'Destino', df_dest_rpm, wow_rpm_dest, True),
        ('corp',    'Corp',    df_corp_rpm, wow_rpm_corp, True),
        ('hotel',   'Hotel',   df_hot_rpm,  None,         True),
    ]

    card_nd  = kpi_card_canasta('% de No Dispo', pct_w18, pct_w17, banda_nd, '&lt; 3%',
                                 wow_str_nd, wow_color_nd, 'nodispo', df_dest, tabs_nd,
                                 prefix='', card_id=f'{idx_str}-nd')
    card_rpm = kpi_card_canasta('IPM · Income Per Million USD', rpm_w18, rpm_w17, banda_rp, '≥ $650',
                                 wow_str_rp, wow_color_rp, 'rpm', df_dest_rpm, tabs_rpm,
                                 prefix='$', card_id=f'{idx_str}-rpm')

    kpi_block = f'<div class="kpis-hero" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 24px;">{card_nd}{card_rpm}</div>'
    
    # === ALERTAS Críticas dentro de canasta ===
    alertas_canasta_html = _render_canasta_alertas_rnd(c)

    # === RESUMEN EJECUTIVO con pills de banda y WoW ===
    def pill_b(nombre):
        COLORS = {'Exitosa':('#085041','#E1F5EE'),'Aceptable':('#5C469C','#EDE8F7'),
                  'Revisar':('#A86A1D','#FFF4E0'),'Crítica':('#C0392B','#FCE4F1'),
                  'Súper Crítica':('#ffffff','rgba(22,22,22,.80)'),'Sin Conv':('#8A8377','#F2EEE6')}
        ct, cb = COLORS.get(nombre, ('#161616','#F2EEE6'))
        return (f'<span style="display:inline-block;font-size:9px;font-weight:700;letter-spacing:.05em;'
                f'text-transform:uppercase;padding:2px 7px;border-radius:3px;'
                f'background:{cb} !important;color:{ct} !important;'
                f'vertical-align:middle;margin:0 2px;">{nombre}</span>')
    def pill_d(texto, mejora):
        color = '#2F6C34' if mejora else '#C0392B'
        bg    = '#EAF3DE' if mejora else '#FCE8E6'
        return (f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;'
                f'border-radius:3px;background:{bg};color:{color};vertical-align:middle;margin:0 2px;">{texto}</span>')

    findings_raw = _build_canasta_findings_rnd(c)
    # Enriquecer findings con pills
    for i, f in enumerate(findings_raw):
        titulo = f['titulo']; desc = f['desc']
        if i == 0:  # %NoDispo
            titulo = f'% NoDispo · {pill_b(banda_nd)}'
            desc = f'{pill_d(wow_str_nd, pct_wow<0)} · {desc}'
        elif i == 1:  # IPM
            titulo = f'IPM · {pill_b(banda_rp)}'
            desc = f'{pill_d(wow_str_rp, rpm_wow>0)} · {desc}'
        # Mayúscula después de ·
        desc = '. '.join(s.strip().capitalize() if j>0 else s for j,s in enumerate(desc.split('. ')))
        findings_raw[i] = {**f, 'titulo': titulo, 'desc': desc}

    resumen_canasta_html = render_resumen_ejecutivo(
        findings_raw, accent_color='#EA0074', scope='canasta',
        header_title=f'Resumen Ejecutivo · Canasta {c["short"]}'
    )

    # === SEVERIDAD ===
    levels_nd  = make_severity_levels(c['sev_nd'],  LEVELS_NODISPO)
    levels_rpm = make_severity_levels(c['sev_rpm'], LEVELS_RPM)
    sev_block_nd  = render_severity_block('🚨 % NoDispo', '●', '#EA0074', levels_nd,  n_p80)
    sev_block_rpm = render_severity_block('🚨 IPM (Income Per Million USD)', '●', '#EA0074', levels_rpm, n_p80)
    severity_canasta_html = render_severity_2cols(sev_block_nd, sev_block_rpm)

    # === ANÁLISIS POR HOTEL · 3 tabs (Demanda No Convertida · Bajo Rend · Sin Conv) ===
    def panel_inner_rnd(df, dim_col, dim_label, parse_hotel=False, start_idx=0):
        import math
        rows = f'<div class="panel-header"><span>{dim_label}</span><span>%NoDispo</span><span>WoW</span><span>IPM</span><span>WoW</span></div>'
        for i, r in df.iterrows():
            raw = r[dim_col]
            if parse_hotel:
                label = truncate(clean_hotel_name(raw), 26)
            elif dim_col == 'PaisDestino':
                label = clean_pais_name(raw)
            elif dim_col == 'Destino':
                label = clean_destino_name(raw, 26)
            elif dim_col == 'CorpName':
                label = clean_corp_name(raw)
            else:
                label = truncate(str(raw), 26)
            # IPM sin negativos
            ipm_val = max(r.get('RPM', r.get('IPM', 0)), 0)
            # WoW %NoDispo
            wow_v = r.get('NoDispo_WoW_pp', None)
            if wow_v is None or (isinstance(wow_v,float) and (math.isnan(wow_v) or math.isinf(wow_v))) or abs(wow_v) < 0.05:
                wow_html = '<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
            else:
                mejora = wow_v < 0
                wc = '#2F6C34' if mejora else '#C0392B'
                wb = '#EAF3DE' if mejora else '#FCE8E6'
                wow_html = f'<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb};color:{wc};">{"↓" if wow_v<0 else "↑"}{abs(wow_v):.2f}</em>'.replace('.',',')
            # WoW IPM
            ipm_base = r.get('IPM_W18', 0)
            wow_ipm_v = r.get('IPM_WoW_pp')
            if wow_ipm_v is not None and not (isinstance(wow_ipm_v,float) and math.isnan(wow_ipm_v)) and ipm_base > 0:
                wow_pct = (wow_ipm_v / ipm_base) * 100
                if abs(wow_pct) >= 0.5:
                    wc2 = '#2F6C34' if wow_pct > 0 else '#C0392B'
                    wb2 = '#EAF3DE' if wow_pct > 0 else '#FCE8E6'
                    wow_ipm_html = f'<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb2};color:{wc2};">{"↑" if wow_pct>0 else "↓"}{abs(wow_pct):.1f}%</em>'.replace('.',',')
                else:
                    wow_ipm_html = '<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
            else:
                wow_ipm_html = '<em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'

            rows += (f'<div class="panel-row">'
                     f'<span class="label">{start_idx+i+1}. {label}</span>'
                     f'<span class="efic">{fmt_pct2(r["%NoDispo"])}</span>'
                     f'<span class="cr">{wow_html}</span>'
                     f'<span class="cr">${fmt_num2(ipm_val)}</span>'
                     f'<span class="cr">{wow_ipm_html}</span>'
                     f'</div>')
        return rows

    def tab_panel_hotel(t_key, df_full, dim_col, dim_label, parse_hotel=False):
        df10 = df_full.head(10).reset_index(drop=True)
        df1  = df10.iloc[:5].reset_index(drop=True)
        df2  = df10.iloc[5:10].reset_index(drop=True)
        col1 = panel_inner_rnd(df1, dim_col, dim_label, parse_hotel, start_idx=0)
        col2 = panel_inner_rnd(df2, dim_col, dim_label, parse_hotel, start_idx=5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'

    df_dnc_c = c['p80'].copy()
    df_dnc_c['DemandaNoConvertida'] = df_dnc_c['Trafico'] * df_dnc_c['%NoDispo']
    df_dnc_c = df_dnc_c.sort_values('DemandaNoConvertida', ascending=False).head(10).reset_index(drop=True)
    df_br_c  = c.get('bajo_rend',  c['p80'][(c['p80']['Bookings']>0)&(c['p80']['RPM']>0)].sort_values('RPM').head(10))
    df_sc_c  = c.get('sin_conv',   c['p80'][c['p80']['Bookings']==0].sort_values('Trafico', ascending=False).head(10))

    bloque_hotel_html = f'''<div id="canasta-{idx_str}-hotel-rnd" style="margin:32px 0 0;">
<div style="font-size:11px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:var(--ink);margin:0 0 10px;">🏨 Análisis por Hotel</div>
{searchbox_html(f'sb-rnd-canasta-{idx_str}-hotel', f'#canasta-{idx_str}-hotel-rnd', 'Buscar hotel...')}
<div class="tabs-block" style="background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:16px;">
<input checked id="tab-{idx_str}-h-dnc" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-h-br" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-h-sc" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<div class="tabs-row" style="display:flex;gap:2px;margin-bottom:12px;border-bottom:1px solid var(--rule);padding-bottom:0;">
<label class="tab-label" for="tab-{idx_str}-h-dnc">Demanda No Convertida</label>
<label class="tab-label" for="tab-{idx_str}-h-br">Bajo Rendimiento</label>
<label class="tab-label" for="tab-{idx_str}-h-sc">Sin Conversión</label>
</div>
<div class="tab-panels">
{tab_panel_hotel('dnc', df_dnc_c, 'Hotel', 'Hotel', parse_hotel=True)}
{tab_panel_hotel('br',  df_br_c,  'Hotel', 'Hotel', parse_hotel=True)}
{tab_panel_hotel('sc',  df_sc_c,  'Hotel', 'Hotel', parse_hotel=True)}
</div>
</div>
</div>'''

    # === ANÁLISIS POR DIMENSIÓN · 3 tabs (Corp · Destino · País) ===
    def tab_panel_dim(t_key, df_full, dim_col, dim_label):
        df10 = df_full.head(10).reset_index(drop=True)
        df1  = df10.iloc[:5].reset_index(drop=True)
        df2  = df10.iloc[5:10].reset_index(drop=True)
        col1 = panel_inner_rnd(df1, dim_col, dim_label, parse_hotel=False, start_idx=0)
        col2 = panel_inner_rnd(df2, dim_col, dim_label, parse_hotel=False, start_idx=5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'

    df_corp_dim = c['agg_corp'].sort_values('Trafico', ascending=False).head(10).reset_index(drop=True)
    df_dest_dim = c['agg_dest'].sort_values('Trafico', ascending=False).head(10).reset_index(drop=True) if 'agg_dest' in c else df_dest
    df_pais_dim = c['agg_pais'].sort_values('Trafico', ascending=False).head(10).reset_index(drop=True) if 'agg_pais' in c else df_pais

    bloque_dim_html = f'''<div id="canasta-{idx_str}-dim-rnd" style="margin:32px 0 32px;">
<div style="font-size:11px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:var(--ink);margin:0 0 6px;">📊 Análisis por Dimensión</div>
{searchbox_html(f'sb-rnd-canasta-{idx_str}-dim', f'#canasta-{idx_str}-dim-rnd', 'Buscar corporativo, destino o país...')}
<div class="tabs-block" style="background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:8px 16px 16px;">
<input checked id="tab-{idx_str}-d-corp" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-d-dest" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-d-pais" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<div class="tabs-row" style="display:flex;gap:2px;margin-bottom:12px;border-bottom:1px solid var(--rule);padding-bottom:0;">
<label class="tab-label" for="tab-{idx_str}-d-corp">Corporativo</label>
<label class="tab-label" for="tab-{idx_str}-d-dest">Destino</label>
<label class="tab-label" for="tab-{idx_str}-d-pais">País</label>
</div>
<div class="tab-panels">
{tab_panel_dim('corp', df_corp_dim, 'CorpName', 'Corporativo')}
{tab_panel_dim('dest', df_dest_dim, 'Destino',  'Destino')}
{tab_panel_dim('pais', df_pais_dim, 'PaisDestino', 'País')}
</div>
</div>
</div>'''

    # CSS tabs de canasta para hotel y dimensión
    extra_css = f'''<style>
/* Base tab-label estado inactivo — asegura efecto folder en canastas */
#tab-{idx_str}-h-dnc ~ .tabs-row label[for^="tab-{idx_str}-h-"],
#tab-{idx_str}-d-corp ~ .tabs-row label[for^="tab-{idx_str}-d-"]{{
  padding:8px 14px;font-size:10px;font-weight:600;color:var(--ink-muted);text-transform:uppercase;
  letter-spacing:.06em;cursor:pointer;border-radius:6px 6px 0 0;
  border:1px solid transparent;border-bottom:none;user-select:none;
  transition:all .15s;margin-bottom:-1px;display:inline-block;
}}
/* Tab activo — estilo folder conectado */
#tab-{idx_str}-h-dnc:checked ~ .tabs-row label[for="tab-{idx_str}-h-dnc"],
#tab-{idx_str}-h-br:checked ~ .tabs-row label[for="tab-{idx_str}-h-br"],
#tab-{idx_str}-h-sc:checked ~ .tabs-row label[for="tab-{idx_str}-h-sc"],
#tab-{idx_str}-d-corp:checked ~ .tabs-row label[for="tab-{idx_str}-d-corp"],
#tab-{idx_str}-d-dest:checked ~ .tabs-row label[for="tab-{idx_str}-d-dest"],
#tab-{idx_str}-d-pais:checked ~ .tabs-row label[for="tab-{idx_str}-d-pais"]{{
  background:var(--paper);color:#EA0074;font-weight:700;
  border:1px solid var(--rule);border-bottom:1px solid var(--paper);
}}
#tab-{idx_str}-h-dnc:checked ~ .tab-panels .tab-panel-c[data-tab="dnc"],
#tab-{idx_str}-h-br:checked  ~ .tab-panels .tab-panel-c[data-tab="br"],
#tab-{idx_str}-h-sc:checked  ~ .tab-panels .tab-panel-c[data-tab="sc"],
#tab-{idx_str}-d-corp:checked ~ .tab-panels .tab-panel-c[data-tab="corp"],
#tab-{idx_str}-d-dest:checked ~ .tab-panels .tab-panel-c[data-tab="dest"],
#tab-{idx_str}-d-pais:checked ~ .tab-panels .tab-panel-c[data-tab="pais"]{{display:block !important;}}
/* KPI tabs canasta */
.kpi-card input[id*="{idx_str}-nd-"]:checked ~ .tabs-row label[for*="{idx_str}-nd-"],
.kpi-card input[id*="{idx_str}-rpm-"]:checked ~ .tabs-row label[for*="{idx_str}-rpm-"]{{
  background:var(--paper);color:#EA0074;border:1px solid var(--rule);border-bottom:1px solid var(--paper);
}}
.kpi-card input[id^="tab-{idx_str}-nd-"]:checked ~ .tab-panels .tab-panel[data-tab="pais"],
.kpi-card input[id^="tab-{idx_str}-nd-destino"]:checked ~ .tab-panels .tab-panel[data-tab="destino"],
.kpi-card input[id^="tab-{idx_str}-nd-corp"]:checked   ~ .tab-panels .tab-panel[data-tab="corp"],
.kpi-card input[id^="tab-{idx_str}-nd-hotel"]:checked  ~ .tab-panels .tab-panel[data-tab="hotel"],
.kpi-card input[id^="tab-{idx_str}-rpm-pais"]:checked   ~ .tab-panels .tab-panel[data-tab="pais"],
.kpi-card input[id^="tab-{idx_str}-rpm-destino"]:checked ~ .tab-panels .tab-panel[data-tab="destino"],
.kpi-card input[id^="tab-{idx_str}-rpm-corp"]:checked   ~ .tab-panels .tab-panel[data-tab="corp"],
.kpi-card input[id^="tab-{idx_str}-rpm-hotel"]:checked  ~ .tab-panels .tab-panel[data-tab="hotel"]{{display:block !important;}}
</style>'''
    
    # === Bajo Rendimiento + Sin Conversión a 10 en 2 columnas ===
    def _fmt_wow_nd(v):
        """WoW para %NoDispo: verde si baja."""
        import math
        if v is None or (isinstance(v,float) and (math.isnan(v) or math.isinf(v))) or abs(v) < 0.05:
            return '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
        mejora = v < 0
        wc = '#2F6C34' if mejora else '#C0392B'
        wb = '#EAF3DE' if mejora else '#FCE8E6'
        return f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb};color:{wc};">{"↓" if v<0 else "↑"}{abs(v):.2f}'.replace('.',',') + '</em>'

    def _fmt_wow_ipm(v_abs, ipm_prev=0):
        """WoW para IPM en %: verde si sube. v_abs=diferencia absoluta USD, ipm_prev=base."""
        import math
        if v_abs is None or (isinstance(v_abs,float) and (math.isnan(v_abs) or math.isinf(v_abs))) or ipm_prev <= 0:
            return '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
        v = (v_abs / ipm_prev) * 100  # convertir a %
        if abs(v) < 0.5: return '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
        mejora = v > 0
        wc = '#2F6C34' if mejora else '#C0392B'
        wb = '#EAF3DE' if mejora else '#FCE8E6'
        return f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb};color:{wc};">{"↑" if v>0 else "↓"}{abs(v):.1f}%</em>'.replace('.',',',-1)

    def render_top10_2cols_rnd(df, title, mode='dnc'):
        """mode: dnc | br | sc"""
        if len(df) == 0: return ''
        df = df.head(10).reset_index(drop=True)
        df1 = df.iloc[:5].reset_index(drop=True)
        df2 = df.iloc[5:10].reset_index(drop=True)

        def render_col(sub, start_idx):
            # Columnas según modo: Tráfico · métrica · WoW
            cols_grid = '1fr 70px 65px 44px'
            html = ''
            for i, r in sub.iterrows():
                hotel_name = truncate(clean_hotel_name(r['Hotel']), 26)
                corp = r.get('CorpName','')
                cells = (f'<div><div style="color:#EA0074;font-weight:600;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{start_idx+i+1}. {hotel_name}</div>'
                         f'<div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;">{clean_corp_name(corp)}</div></div>'
                         f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_big(r["Trafico"])}</span>')
                if mode == 'dnc':
                    cells += f'<span style="text-align:right;color:#EA0074;font-weight:600;">{fmt_pct2(r["%NoDispo"])}</span>'
                    cells += _fmt_wow_nd(r.get('NoDispo_WoW_pp'))
                elif mode == 'br':
                    cells += f'<span style="text-align:right;color:#EA0074;font-weight:600;">${fmt_num2(max(r.get("RPM",r.get("IPM",0)),0))}</span>'
                    cells += _fmt_wow_ipm(r.get('IPM_WoW_pp'), ipm_prev=r.get('IPM_W18', 0))
                elif mode == 'sc':
                    cells += f'<span style="text-align:right;color:#EA0074;font-weight:600;">{fmt_pct2(r["%NoDispo"])}</span>'
                    cells += _fmt_wow_nd(r.get('NoDispo_WoW_pp'))
                html += f'<div style="display:grid;grid-template-columns:{cols_grid};gap:6px;padding:6px 0;border-bottom:1px solid var(--rule-soft);font-size:11px;">{cells}</div>'
            return html

        col1 = render_col(df1, 0)
        col2 = render_col(df2, 5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div style="margin-top:24px;"><h3 style="font-size:13px;font-weight:700;color:#EA0074;text-transform:uppercase;letter-spacing:.10em;margin:0 0 10px;">{title}</h3>{body}</div>'

    bajo_rows = render_top10_2cols_rnd(c.get('bajo_rend', c['p80'][(c['p80']['Bookings']>0)].sort_values('IPM').head(10)), f'Top 10 · Bajo Rendimiento · Canasta {c["short"]}', mode='br')
    sin_rows  = render_top10_2cols_rnd(c.get('sin_conv',  c['p80'][c['p80']['Bookings']==0].sort_values('Trafico',ascending=False).head(10)), f'Top 10 · Sin Conversión · Canasta {c["short"]}', mode='sc')
    dnc_rows  = render_top10_2cols_rnd(c.get('demanda_nc', c.get('top_dnc', c['p80'].sort_values('DemandaNoConvertida',ascending=False).head(10))), f'Top 10 · Demanda No Convertida · Canasta {c["short"]}', mode='dnc')
    
    # === Plan de Acción (mantengo estructura existente, ya está en 2 cols) ===
    canasta_label = c['short']
    weight_str = '0,1' if 'B2C' in c['name'] else '0,6'
    h_top_dnc = c['top_hot'].iloc[0] if len(c['top_hot']) > 0 else None
    h_top_sc = c['sin_conv'].iloc[0] if len(c['sin_conv']) > 0 else None
    
    plan_canasta_rows = ''
    sev_c = c.get('sev_nd', {})
    n_critmas_local = int(sev_c.get('Crítica', 0) + sev_c.get('Súper Crítica', 0))
    rpm_w18 = c['m18'].get('rpm', c['m18'].get('ipm', 0))
    if h_top_dnc is not None:
        plan_canasta_rows += (
            f'<div class="action-row qw">'
            f'<div class="action-owner-badge">Supply Comercial / Supply Optimization</div>'
            f'<div class="accion">Escalar el caso #1 de tráfico de canasta {canasta_label}: <strong>{truncate(clean_hotel_name(h_top_dnc["Hotel"]),32)}</strong> ({h_top_dnc["CorpName"]}) con %NoDispo {fmt_pct2(h_top_dnc["%NoDispo"])}.</div>'
            f'<div class="action-meta-bottom"><span class="cluster-tag">Quick Win</span><span class="meta-item"><strong>Plazo</strong> 5 días</span><span class="meta-item"><strong>Métrica</strong> %ND &lt; 20%</span></div>'
            f'</div>'
        )
    if h_top_sc is not None:
        plan_canasta_rows += (
            f'<div class="action-row qw">'
            f'<div class="action-owner-badge">Supply Optimization / TPS</div>'
            f'<div class="accion">Diagnóstico técnico de <strong>{truncate(clean_hotel_name(h_top_sc["Hotel"]),32)}</strong> ({fmt_big(h_top_sc["Trafico"])} búsquedas, 0 BKGS) · revisar mapping y paridad en canasta {canasta_label}.</div>'
            f'<div class="action-meta-bottom"><span class="cluster-tag">Quick Win</span><span class="meta-item"><strong>Plazo</strong> 1 semana</span><span class="meta-item"><strong>Métrica</strong> Conv Rate &gt; 0</span></div>'
            f'</div>'
        )
    plan_canasta_rows += (
        f'<div class="action-row mp">'
        f'<div class="action-owner-badge">Supply Optimization</div>'
        f'<div class="accion">Plan de saneamiento para los <strong>{fmt_int_es(n_critmas_local)} hoteles Crítica+</strong> de %NoDispo en canasta {canasta_label} (weight {weight_str}).</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority</span><span class="meta-item"><strong>Plazo</strong> 3 semanas</span><span class="meta-item"><strong>Métrica</strong> {int(n_critmas_local*0.5)} a Revisar</span></div>'
        f'</div>'
    )
    plan_canasta_rows += (
        f'<div class="action-row mp">'
        f'<div class="action-owner-badge">Supply Comercial / Wholesale</div>'
        f'<div class="accion">Revisión de IPM en canasta {canasta_label} (actual ${fmt_num2(rpm_w18)}) frente al target ≥ $650 · validar pricing y disponibilidad.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority</span><span class="meta-item"><strong>Plazo</strong> 2 semanas</span><span class="meta-item"><strong>Métrica</strong> IPM ≥ $650</span></div>'
        f'</div>'
    )
    plan_canasta_rows += (
        f'<div class="action-row es">'
        f'<div class="action-owner-badge">Supply Comercial / Supply Optimization</div>'
        f'<div class="accion">Reducir <strong>cohorte Sin Conversión</strong> de canasta {canasta_label} ({fmt_int_es(int(n_sc_total))} hoteles) · proyecto trimestral de remediación.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Estratégica</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> -25% vs baseline</span></div>'
        f'</div>'
    )
    plan_canasta_rows += (
        f'<div class="action-row es">'
        f'<div class="action-owner-badge">Supply Comercial / Wholesale</div>'
        f'<div class="accion">Revisión de tarifas y condiciones contractuales con Top 10 corp de canasta {canasta_label} para alinear severity-based pricing.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Estratégica</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> SLAs firmados</span></div>'
        f'</div>'
    )
    
    plan_canasta_html = f'''<div style="margin-top:48px;padding-top:40px;border-top:1px solid var(--rule);">
<h3 style="font-size:13px;font-weight:700;color:#EA0074;text-transform:uppercase;letter-spacing:.10em;margin:0 0 10px;">Plan de Acción · canasta {canasta_label}</h3>
<div class="action-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{plan_canasta_rows}</div>
</div>'''
    
    # Banner minimalista de descarga · Excel filtrado por canasta
    canasta_filename_map = {'b2c':'B2C', 'op':'OP', 'cug':'CUG'}
    file_suffix = canasta_filename_map.get(idx_str, 'B2C')
    excel_canasta_url = f'Analisis_Rates_NoDispo_{file_suffix}_7d.xlsx'
    banner_descarga_canasta = f'''<div style="margin-top:24px;padding:14px 18px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
<div style="font-size:12px;color:var(--ink-soft);line-height:1.4;">
<span style="font-size:13px;color:var(--ink);">📥</span>
&nbsp;&nbsp;Descargar análisis completo · <strong style="color:#EA0074;">Canasta {c['short']}</strong>
<span style="display:inline-block;margin-left:8px;font-size:11px;color:var(--ink-muted);">8 pestañas · Top 50 por dimensión</span>
</div>
<a href="{excel_canasta_url}" style="display:inline-block;padding:6px 14px;background:#EA0074;color:#fff;font-size:11px;font-weight:600;text-decoration:none;border-radius:3px;letter-spacing:.04em;text-transform:uppercase;">Excel ↗</a>
</div>'''
    
    return f'''{extra_css}<details class="canasta-block" style="margin-bottom:32px;">
<summary>
<div class="summary-title">
<h2>Canasta {c['short']}</h2>
<span class="section-subtitle">{c['name']} · weight {0.1 if 'B2C' in c['name'] else 0.6}</span>
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
{banner_descarga_canasta}
</div>
</details>
'''

# Build
CANASTA_SECTION = '''<section id="por-canasta">
<div class="section-head">
<div>
<div class="section-num">Sección 11</div>
<h2 class="section-title">📦 Análisis por canasta</h2>
<span class="section-subtitle" style="color:#EA0074">B2C · B2B-OP · CUG</span>
<p class="section-kicker">Métricas, severidad y casos críticos por canasta. CUG y B2B-OP tienen weight 0,6 (prioridad estratégica). B2C tiene weight 0,1 pero no se elimina del análisis.</p>
</div>
</div>
'''
for idx_key, c_key in [('op','op'),('cug','cug'),('b2c','b2c')]:  # OP primero por relevancia
    CANASTA_SECTION += render_canasta_block(CANASTA[c_key], idx_str=idx_key)
CANASTA_SECTION += '</section>\n'

# Cierre
CIERRE = f'''
{FOOTER}
</body>
</html>
'''

with open('part3_rnd.html','w') as f:
    f.write(CANASTA_SECTION + '\n</div>\n' + CIERRE)
print(f"Part 3 RND escrito: {len(CANASTA_SECTION + CIERRE):,} chars")
