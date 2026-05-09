"""
Renderer CR parte 3: Análisis por Canasta (B2C, B2B-OP, CUG)
Cards colapsables con KPIs Eficacia/ConvRate + tabs WoW + RE con pills + bloques hotel/dimensión
Post W19 · port del patrón RND p3
"""
import pickle, pandas as pd, numpy as np
from engine import *
from render_helpers import *

with open('cr_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; CANASTA = D['CANASTA']

CR_ACCENT = '#5C469C'

PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']

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
    """Pill de banda con colores del sistema D."""
    c = BANDA_COLORS.get(nombre, BANDA_COLORS['Sin Conversión'])
    bg = 'rgba(22,22,22,.80)' if nombre == 'Súper Crítica' else c['bg']
    fg = '#FFFFFF' if nombre == 'Súper Crítica' else c['fg']
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
        return f'{sign}{v:.2f}pp'.replace('.',',')
    def es_pct1(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.1f}%'.replace('.',',')
    def es_int(v): return fmt_int_es(int(v))

    findings = [
        {'numero': es_pct(ef*100,2),
         'titulo': f'Eficacia · banda {m18["banda_eficacia"]}',
         'desc': f'Tasa de éxito de CheckRates en canasta {canasta_label}. WoW {es_pp(ef_wow)} · target ≥ 97%.'},
        {'numero': es_pct(cv*100,2),
         'titulo': f'Conv Rate · banda {m18["banda_convrate"]}',
         'desc': f'Bookings / CR únicos en canasta {canasta_label}. WoW {es_pp(cv_wow)} · target ≥ 2,5%.'},
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
            truncate(clean_hotel_name(str(ef_obj[name_col])) if name_col=='Hotel' else str(ef_obj[name_col]), 22),
            fmt_pct2(ef_obj['Eficacia']), '#EA0074'
        )
        sub_cv = render_alert_subcell(
            'ConvRate', CR_ACCENT, '#EDE8F7',
            truncate(clean_hotel_name(str(cv_obj[name_col])) if name_col=='Hotel' else str(cv_obj[name_col]), 22),
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
        return f'''<div style="margin-top:14px;background:var(--paper-soft);border-radius:4px;padding:8px;display:flex;align-items:stretch;gap:8px;">
<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W17</div>
  <div style="font-size:16px;font-weight:700;color:var(--ink-soft);margin-top:2px;">{v17}</div>
</div>
<div style="flex:1;text-align:center;background:var(--paper);padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);font-weight:700;">W18</div>
  <div style="font-size:16px;font-weight:700;color:{accent};margin-top:2px;">{v18}</div>
</div>
<div style="flex:1;text-align:center;background:{bg_wow};padding:8px 4px;border-radius:3px;">
  <div style="font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:{wow_color};font-weight:700;">WoW</div>
  <div style="font-size:16px;font-weight:700;color:{wow_color};margin-top:2px;">{wow_str}</div>
</div>
</div>'''

    # ── Tab rows con pills WoW ────────────────────────────────────────────────
    def tab_rows_canasta(df, dim_col, parse_hotel=False, wow_map=None, val_col='Eficacia', is_cv=False):
        rows_l, rows_r = '', ''
        df10 = df.head(10).reset_index(drop=True)
        for i, r in df10.iterrows():
            raw = r[dim_col]
            if parse_hotel:
                lab = truncate(clean_hotel_name(raw), 26)
            elif dim_col == 'CorpName':
                lab = truncate(clean_corp_name(raw), 26)
            else:
                lab = truncate(str(raw), 26)
            val = r[val_col] if val_col in r.index else 0
            val_str = fmt_pct2(val)
            apply_wow = wow_map is not None and not parse_hotel
            pill = get_pill_wow(str(raw), wow_map) if apply_wow else ''
            cell = (f'<div style="display:grid;grid-template-columns:1fr 52px 44px;align-items:baseline;">'
                    f'<strong style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{i+1}. {lab}</strong>'
                    f'<span style="text-align:right;">{val_str}</span>'
                    f'{pill}</div>')
            if i < 5:
                rows_l += cell
            else:
                rows_r += cell
        if rows_r:
            return (f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
                    f'<div>{rows_l}</div><div>{rows_r}</div></div>')
        return rows_l

    # ── KPI card con gauge + wow + tabs ──────────────────────────────────────
    def kpi_card_canasta(metric, val18, val17, banda, pill_target, wow_str, wow_color,
                          gauge_tipo, tab_configs, card_id=''):
        pill   = banda_pill(banda, target=pill_target, font_size='9px')
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
            panel_html = tab_rows_canasta(df_t, dim_col, parse_hotel, wm, val_col)
            panels += f'<div class="tab-panel" data-tab="{tk}">{panel_html}</div>'
        return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:18px 20px;border-radius:3px;background:var(--paper);">
{tabs_inputs}
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">{metric}</div>
<div style="font-size:42px;font-weight:600;letter-spacing:-.02em;color:{CR_ACCENT};line-height:1;margin-top:4px;">{v18str}</div>
<div style="margin-top:10px;">{pill}</div>
{gauge}
{wb}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;flex-wrap:wrap;border-bottom:1px solid var(--rule);padding:0 0 0 4px;">{tabs_labels}</div>
<div class="tab-panels">{panels}</div>
</div>'''

    # Datos para tabs de KPI
    p80 = c['p80']
    agg_corp = c['agg_corp']
    agg_dest = c['agg_destino'] if 'agg_destino' in c else c['g_dest']
    agg_chan  = c['agg_channel']

    df_dest_ef = agg_dest.sort_values('Eficacia').head(10).reset_index(drop=True)
    df_corp_ef = agg_corp.sort_values('Eficacia').head(10).reset_index(drop=True)
    df_hot_ef  = p80.sort_values('Eficacia').head(10).reset_index(drop=True)
    df_dest_cv = agg_dest.sort_values('ConvRate').head(10).reset_index(drop=True)
    df_corp_cv = agg_corp.sort_values('ConvRate').head(10).reset_index(drop=True)
    df_hot_cv  = p80.sort_values('ConvRate').head(10).reset_index(drop=True)

    tabs_ef = [
        ('destino', 'Destino', df_dest_ef, None),
        ('corp',    'Corp',    df_corp_ef, None),
        ('hotel',   'Hotel',   df_hot_ef,  None),
    ]
    tabs_cv = [
        ('destino', 'Destino', df_dest_cv, None),
        ('corp',    'Corp',    df_corp_cv, None),
        ('hotel',   'Hotel',   df_hot_cv,  None),
    ]

    card_ef = kpi_card_canasta('Eficacia', ef_w18, ef_w17, banda_ef, '≥ 97%',
                                wow_str_ef, wow_color_ef, 'eficacia', tabs_ef,
                                card_id=f'{idx_str}-ef')
    card_cv = kpi_card_canasta('Conv Rate', cv_w18, cv_w17, banda_cv, '≥ 2,5%',
                                wow_str_cv, wow_color_cv, 'convrate', tabs_cv,
                                card_id=f'{idx_str}-cv')

    kpi_block = f'<div class="kpis-hero" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 24px;">{card_ef}{card_cv}</div>'

    # ── Alertas ───────────────────────────────────────────────────────────────
    alertas_canasta_html = _render_canasta_alertas_cr(c, CR_ACCENT)

    # ── Resumen Ejecutivo con pills ───────────────────────────────────────────
    findings_raw = _build_canasta_findings_cr(c)
    for i, f in enumerate(findings_raw):
        titulo = f['titulo']; desc = f['desc']
        if i == 0:  # Eficacia
            titulo = f'Eficacia · {pill_b(banda_ef)}'
            desc   = f'{pill_d(wow_str_ef, ef_wow > 0)} · {desc}'
        elif i == 1:  # Conv Rate
            titulo = f'Conv Rate · {pill_b(banda_cv)}'
            desc   = f'{pill_d(wow_str_cv, cv_wow > 0)} · {desc}'
        findings_raw[i] = {**f, 'titulo': titulo, 'desc': desc}

    resumen_canasta_html = render_resumen_ejecutivo(
        findings_raw, accent_color=CR_ACCENT, scope='canasta',
        header_title=f'Resumen Ejecutivo · Canasta {c["short"]}'
    )

    # ── Severity ──────────────────────────────────────────────────────────────
    levels_ef  = make_severity_levels(c['sev_ef'],  LEVELS_EFICACIA)
    levels_cv  = make_severity_levels(c['sev_cv'],  LEVELS_CONVRATE)
    sev_blk_ef = render_severity_block('Eficacia',  '●', '#EA0074', levels_ef, n_p80)
    sev_blk_cv = render_severity_block('Conv Rate', '●', CR_ACCENT, levels_cv, n_p80)
    severity_canasta_html = render_severity_2cols(sev_blk_ef, sev_blk_cv)

    # ── Bloque Hotel · 3 tabs: Críticos · Bajo Rend · Sin Conv ───────────────
    def panel_inner_cr(df, dim_col, dim_label, parse_hotel=False, start_idx=0):
        rows = f'<div class="panel-header"><span>{dim_label}</span><span>Eficacia</span><span>BKGS</span></div>'
        for i, r in df.iterrows():
            raw = r[dim_col]
            if parse_hotel:
                label = truncate(clean_hotel_name(raw), 28)
            elif dim_col == 'CorpName':
                label = truncate(clean_corp_name(raw), 28)
            else:
                label = truncate(str(raw), 28)
            rows += (f'<div class="panel-row">'
                     f'<span class="label">{start_idx+i+1}. {label}</span>'
                     f'<span class="efic">{fmt_pct2(r["Eficacia"])}</span>'
                     f'<span class="cr">{fmt_int_es(r["Bookings"])}</span>'
                     f'</div>')
        return rows

    def tab_panel_hotel(t_key, df_full, parse_hotel=False):
        df10 = df_full.head(10).reset_index(drop=True)
        df1  = df10.iloc[:5].reset_index(drop=True)
        df2  = df10.iloc[5:10].reset_index(drop=True)
        col1 = panel_inner_cr(df1, 'Hotel', 'Hotel', parse_hotel, start_idx=0)
        col2 = panel_inner_cr(df2, 'Hotel', 'Hotel', parse_hotel, start_idx=5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'

    df_crit_c = p80[(p80['Bookings']>0)&(p80['BandaEficacia'].isin(['Crítica','Súper Crítica']))].sort_values('Eficacia').head(10).reset_index(drop=True)
    df_br_c   = p80[(p80['Bookings']>0)&(p80['BandaConvRate'].isin(['Crítica','Revisar']))].sort_values('CR_Unicos', ascending=False).head(10).reset_index(drop=True)
    df_sc_c   = p80[p80['Bookings']==0].sort_values('CR_Unicos', ascending=False).head(10).reset_index(drop=True)

    bloque_hotel_html = f'''<div style="margin:32px 0 0;">
<div style="font-size:11px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:var(--ink);margin:0 0 10px;">🏨 Análisis por Hotel</div>
<div class="tabs-block" style="background:#F6EFE0;border:1px solid var(--rule);border-radius:8px;padding:16px;">
<input checked id="tab-{idx_str}-h-crit" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-h-br" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-h-sc" name="tabs-{idx_str}-h" style="display:none;" type="radio"/>
<div class="tabs-row" style="display:flex;gap:2px;margin-bottom:12px;border-bottom:1px solid var(--rule);padding-bottom:0;">
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
</div>'''

    # ── Bloque Dimensión · 3 tabs: Corp · Destino · Channel ──────────────────
    def tab_panel_dim_cr(t_key, df_full, dim_col, dim_label):
        df10 = df_full.head(10).reset_index(drop=True)
        df1  = df10.iloc[:5].reset_index(drop=True)
        df2  = df10.iloc[5:10].reset_index(drop=True)
        col1 = panel_inner_cr(df1, dim_col, dim_label, parse_hotel=False, start_idx=0)
        col2 = panel_inner_cr(df2, dim_col, dim_label, parse_hotel=False, start_idx=5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'

    df_corp_dim = agg_corp.sort_values('CR_Unicos', ascending=False).head(10).reset_index(drop=True)
    df_dest_dim = agg_dest.sort_values('CR_Unicos', ascending=False).head(10).reset_index(drop=True)

    # Channel split PP/TP
    df_pp = agg_chan[agg_chan['ExternalProviderName'].isin(PRODUCTO_PROPIO)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    df_tp = agg_chan[agg_chan['ExternalProviderName'].isin(THIRD_PARTY)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)

    def panel_inner_chan(df, color):
        rows = f'<div class="panel-header" style="color:{color};"><span>Channel</span><span>Eficacia</span><span>BKGS</span></div>'
        for i, r in df.head(10).reset_index(drop=True).iterrows():
            rows += (f'<div class="panel-row">'
                     f'<span class="label">{i+1}. {truncate(r["ExternalProviderName"],24)}</span>'
                     f'<span class="efic">{fmt_pct2(r["Eficacia"])}</span>'
                     f'<span class="cr">{fmt_int_es(r["Bookings"])}</span>'
                     f'</div>')
        return rows

    panel_chan = (
        f'<div class="tab-panel-c" data-tab="channel">'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">'
        f'<div><div style="font-size:10px;font-weight:700;color:{CR_ACCENT};letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>'
        f'{panel_inner_chan(df_pp, CR_ACCENT)}</div>'
        f'<div><div style="font-size:10px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>'
        f'{panel_inner_chan(df_tp, "#4FC3F4")}</div>'
        f'</div></div>'
    )

    bloque_dim_html = f'''<div style="margin:32px 0 32px;">
<div style="font-size:11px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:var(--ink);margin:0 0 6px;">📊 Análisis por Dimensión</div>
<div class="tabs-block" style="background:#F6EFE0;border:1px solid var(--rule);border-radius:8px;padding:8px 16px 16px;">
<input checked id="tab-{idx_str}-d-corp" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-d-dest" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<input id="tab-{idx_str}-d-channel" name="tabs-{idx_str}-d" style="display:none;" type="radio"/>
<div class="tabs-row" style="display:flex;gap:2px;margin-bottom:12px;border-bottom:1px solid var(--rule);padding-bottom:0;">
<label class="tab-label" for="tab-{idx_str}-d-corp">Corporativo</label>
<label class="tab-label" for="tab-{idx_str}-d-dest">Destino</label>
<label class="tab-label" for="tab-{idx_str}-d-channel">Channel</label>
</div>
<div class="tab-panels">
{tab_panel_dim_cr('corp', df_corp_dim, 'CorpName', 'Corporativo')}
{tab_panel_dim_cr('dest', df_dest_dim, 'Destino',  'Destino')}
{panel_chan}
</div>
</div>
</div>'''

    # ── CSS dinámico por canasta ──────────────────────────────────────────────
    extra_css = f'''<style>
#tab-{idx_str}-h-crit:checked ~ .tabs-row label[for="tab-{idx_str}-h-crit"],
#tab-{idx_str}-h-br:checked   ~ .tabs-row label[for="tab-{idx_str}-h-br"],
#tab-{idx_str}-h-sc:checked   ~ .tabs-row label[for="tab-{idx_str}-h-sc"],
#tab-{idx_str}-d-corp:checked    ~ .tabs-row label[for="tab-{idx_str}-d-corp"],
#tab-{idx_str}-d-dest:checked    ~ .tabs-row label[for="tab-{idx_str}-d-dest"],
#tab-{idx_str}-d-channel:checked ~ .tabs-row label[for="tab-{idx_str}-d-channel"]{{
  background:var(--paper);color:{CR_ACCENT};border:1px solid var(--rule);border-bottom:1px solid var(--paper);
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
</div>'''

    # ── Banner Excel ──────────────────────────────────────────────────────────
    file_map = {'op':'OP','cug':'CUG','b2c':'B2C'}
    file_suffix = file_map.get(idx_str, 'B2C')
    excel_url = f'Analisis_Checkrates_{file_suffix}_7d.xlsx'
    banner = f'''<div style="margin-top:24px;padding:14px 18px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
<div style="font-size:12px;color:var(--ink-soft);line-height:1.4;">
<span style="font-size:13px;color:var(--ink);">📥</span>
&nbsp;&nbsp;Descargar análisis completo · <strong style="color:{CR_ACCENT};">Canasta {c["short"]}</strong>
<span style="display:inline-block;margin-left:8px;font-size:11px;color:var(--ink-muted);">9 pestañas · Top 50 por dimensión</span>
</div>
<a href="{excel_url}" style="display:inline-block;padding:6px 14px;background:{CR_ACCENT};color:#fff;font-size:11px;font-weight:600;text-decoration:none;border-radius:3px;letter-spacing:.04em;text-transform:uppercase;">Excel ↗</a>
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
<h2 class="section-title">Análisis por canasta</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">B2C · B2B-OP · CUG</span>
<p class="section-kicker">Métricas, severidad y casos críticos por canasta. CUG y B2B-OP tienen weight 0,6 (prioridad estratégica). B2C tiene weight 0,1 pero no se elimina del análisis.</p>
</div>
</div>
'''
for idx_key, c_key in [('op','B2B-OP'),('cug','CUG'),('b2c','B2C')]:
    CANASTA_SECTION += render_canasta_block(CANASTA[c_key], idx_str=idx_key)
CANASTA_SECTION += '</section>\n'

with open('part3_cr.html','w') as f:
    f.write(CANASTA_SECTION)
print(f"Part 3 CR escrito: {len(CANASTA_SECTION):,} chars")
