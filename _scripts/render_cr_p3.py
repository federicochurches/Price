"""
Renderer CR W18 parte 3: Análisis por Canasta (B2C, B2B-OP, CUG)
Cards colapsables con KPIs Eficacia/ConvRate + tabs Top 5
"""
import pickle, pandas as pd, numpy as np
from engine import *
from render_helpers import *

with open('cr_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; CANASTA = D['CANASTA']

CR_ACCENT = '#5C469C'

def _build_canasta_findings(c):
    """Construye 10 findings para Resumen Ejecutivo dentro de canasta CR."""
    m18 = c['m18']; m17 = c['m17']
    ef = m18['eficacia']; cv = m18['conv_rate']
    ef17 = m17['eficacia']; cv17 = m17['conv_rate']
    ef_wow = (ef-ef17)*100; cv_wow = (cv-cv17)*100
    n_p80 = len(c['p80'])
    n_critmas_ef = c['sev_ef'].get('Súper Crítica',0) + c['sev_ef'].get('Crítica',0)
    n_supcrit_ef = c['sev_ef'].get('Súper Crítica',0)
    n_sc = c['sev_cv'].get('Sin Conversión',0)
    n_crit_cv = c['sev_cv'].get('Crítica',0)
    
    canasta_label = c['short']
    weight_label = {'B2C':'0,1','B2B Opaco':'0,3','CUG':'0,6'}.get(canasta_label, '—')
    
    h_top_ef_pool = c['p80'][(c['p80']['Bookings']>0) & (c['p80']['Eficacia']>0)]
    h_worst_ef = h_top_ef_pool.sort_values('Eficacia').iloc[0] if len(h_top_ef_pool)>0 else None
    h_worst_cv = h_top_ef_pool.sort_values('ConvRate').iloc[0] if len(h_top_ef_pool)>0 else None
    
    top_corp_pool = c['agg_corp'][c['agg_corp']['CR_Unicos']>500].sort_values('CR_Unicos', ascending=False)
    top1_corp = top_corp_pool.iloc[0] if len(top_corp_pool)>0 else None
    top2_corp = top_corp_pool.iloc[1] if len(top_corp_pool)>1 else None
    top3_corp = top_corp_pool.iloc[2] if len(top_corp_pool)>2 else None
    
    top_chan_pool = c['agg_channel'][c['agg_channel']['Bookings']>0].sort_values('CR_Unicos', ascending=False)
    top1_chan = top_chan_pool.iloc[0] if len(top_chan_pool)>0 else None
    
    def es_pct(v, dec=2): return f'{v:.{dec}f}%'.replace('.',',')
    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}pp'.replace('.',',')
    def es_int(v): return fmt_int_es(int(v))
    
    findings = [
        {'numero': es_pct(ef*100,2),
         'titulo': f'Eficacia · banda {m18["banda_eficacia"]}',
         'desc': f'Tasa de respuestas sin error en canasta {canasta_label}. WoW {es_pp(ef_wow)} · weight estratégico {weight_label}.'},
        {'numero': es_pct(cv*100,2),
         'titulo': f'Conv Rate · banda {m18["banda_convrate"]}',
         'desc': f'Bookings por CheckRate en {canasta_label}. WoW {es_pp(cv_wow)} · benchmark global 1,38%.'},
        {'numero': es_int(n_sc),
         'titulo': 'Hoteles con 0 BKGS',
         'desc': f'{es_pct(n_sc/n_p80*100,1)} del P80 sin convertir en {canasta_label}. Cohorte estructural · revisar pricing y conectividad.'},
        {'numero': es_int(n_critmas_ef),
         'titulo': 'Hoteles Severity Eficacia Crítica+',
         'desc': f'Eficacia &lt; 85% · diagnóstico técnico urgente. {n_supcrit_ef} Súper Críticos son los casos más urgentes.'},
        {'numero': es_int(n_crit_cv),
         'titulo': 'Hoteles Severity Conv Rate Crítica',
         'desc': f'Conv Rate &lt; 0,8% · revisión comercial. Probable issue de pricing/competitividad.'},
    ]
    if h_worst_ef is not None:
        findings.append({
            'numero': es_pct(h_worst_ef['Eficacia']*100,2),
            'titulo': f'{truncate(clean_hotel_name(h_worst_ef["Hotel"]),28)} · peor Eficacia',
            'desc': f'Caso emblemático de {canasta_label} · {es_int(h_worst_ef["CR_Unicos"])} CR · {h_worst_ef["CorpName"]} · escalamiento individual prioritario.'
        })
    if top1_corp is not None and top2_corp is not None and top3_corp is not None:
        findings.append({
            'numero': 'Top 3',
            'titulo': f'<strong>{top1_corp["CorpName"]}, {top2_corp["CorpName"]} y {top3_corp["CorpName"]}</strong>',
            'desc': f'Concentración crítica de hoteles en {canasta_label} · revisión técnica + comercial prioritaria.'
        })
    if h_worst_cv is not None:
        findings.append({
            'numero': es_pct(h_worst_cv['ConvRate']*100,2),
            'titulo': f'{truncate(clean_hotel_name(h_worst_cv["Hotel"]),28)} · peor Conv Rate',
            'desc': f'{es_int(h_worst_cv["CR_Unicos"])} CR · {h_worst_cv["CorpName"]} · falla sistémica de conversión.'
        })
    if top1_chan is not None:
        findings.append({
            'numero': es_int(top1_chan['CR_Unicos']),
            'titulo': f'{top1_chan["ExternalProviderName"]} · channel líder',
            'desc': f'Eficacia {es_pct(top1_chan["Eficacia"]*100,2)} · Conv Rate {es_pct(top1_chan["ConvRate"]*100,2)} · concentración del esfuerzo Supply.'
        })
    findings.append({
        'numero': es_int(n_p80),
        'titulo': 'Hoteles P80 analizados',
        'desc': f'Universo de análisis · base estable para diagnóstico de la canasta {canasta_label}.'
    })
    # Asegurar 10 elementos
    while len(findings) < 10:
        findings.append({'numero': '—', 'titulo': 'Dato no disponible', 'desc': 'Cohorte insuficiente para finding adicional esta semana.'})
    return findings[:10]


def _render_canasta_alertas(c, accent_color):
    """Alertas Críticas dentro de canasta CR · 3 cards."""
    from template_alertas import render_alertas_block, render_alert_card, render_alert_subcell
    
    def card_for(card_title, icon, ef_obj, cv_obj, ef_label_field, cv_label_field):
        if ef_obj is None or cv_obj is None:
            return ''
        sub_ef = render_alert_subcell(
            'Eficacia', '#EA0074', '#FCE4F1',
            truncate(clean_hotel_name(str(ef_obj[ef_label_field])), 22) if ef_label_field=='Hotel' else truncate(str(ef_obj[ef_label_field]),22),
            f'{ef_obj["Eficacia"]*100:.2f}%'.replace('.',','),
            '#EA0074'
        )
        sub_cv = render_alert_subcell(
            'Conv Rate', '#5C469C', '#EDE8F7',
            truncate(clean_hotel_name(str(cv_obj[cv_label_field])), 22) if cv_label_field=='Hotel' else truncate(str(cv_obj[cv_label_field]),22),
            f'{cv_obj["ConvRate"]*100:.2f}%'.replace('.',','),
            '#5C469C'
        )
        return render_alert_card(card_title, icon, accent_color, sub_ef, sub_cv)
    
    card_h = card_for('Hoteles', '🏨', c.get('alert_h_ef'), c.get('alert_h_cv'), 'Hotel', 'Hotel')
    card_d = card_for('Destinos', '📍', c.get('alert_d_ef'), c.get('alert_d_cv'), 'Destino', 'Destino')
    card_c = card_for('Channels', '🔌', c.get('alert_c_ef'), c.get('alert_c_cv'), 'ExternalProviderName', 'ExternalProviderName')
    
    return render_alertas_block(
        f'Alertas · Casos Críticos · Canasta {c["short"]}',
        accent_color, card_h, card_d, card_c
    )


def render_canasta_block(canasta_data, idx_str='b2c'):
    from template_resumen import render_resumen_ejecutivo
    from template_severity import render_severity_block, render_severity_2cols, make_severity_levels, LEVELS_EFICACIA, LEVELS_CONVRATE
    
    c = canasta_data
    m18 = c['m18']; m17 = c['m17']
    ef_w18 = m18['eficacia']; ef_w17 = m17['eficacia']
    cv_w18 = m18['conv_rate']; cv_w17 = m17['conv_rate']
    ef_wow = (ef_w18 - ef_w17) * 100
    cv_wow = (cv_w18 - cv_w17) * 100
    
    banda_ef = banda_eficacia(ef_w18)
    banda_cv = banda_convrate(cv_w18, m18['bookings'])
    
    n_crit = c['n_critica']
    n_p80 = len(c['p80'])
    n_sc_total = (c['agg_hotel']['Bookings']==0).sum()
    
    # === KPI block (Eficacia + ConvRate) ===
    pill_ef = banda_pill(banda_ef, target='≥ 97%', font_size='9px')
    pill_cv = banda_pill(banda_cv, target='≥ 2,5%', font_size='9px')
    
    wow_color_ef = '#2F6C34' if ef_wow > 0 else '#C0392B'
    wow_color_cv = '#2F6C34' if cv_wow > 0 else '#C0392B'
    if ef_wow > 0: wow_str_ef = f'↑ +{ef_wow:.2f}pp'.replace('.', ',')
    elif ef_wow < 0: wow_str_ef = f'↓ {ef_wow:.2f}pp'.replace('.', ',')
    else: wow_str_ef = '= 0,00pp'
    if cv_wow > 0: wow_str_cv = f'↑ +{cv_wow:.2f}pp'.replace('.', ',')
    elif cv_wow < 0: wow_str_cv = f'↓ {cv_wow:.2f}pp'.replace('.', ',')
    else: wow_str_cv = '= 0,00pp'
    
    kpi_block = f'''<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 24px;">
<div style="border:1px solid var(--rule);padding:16px 18px;border-radius:3px;background:var(--paper);">
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Eficacia</div>
<div style="display:flex;align-items:baseline;gap:12px;margin-top:6px;">
<div style="font-size:36px;font-weight:600;color:{CR_ACCENT};letter-spacing:-.02em;">{fmt_pct2(ef_w18)}</div>
{pill_ef}
</div>
<div style="margin-top:10px;display:flex;gap:12px;font-size:11px;color:var(--ink-soft);">
<span>Week 17: <strong>{fmt_pct2(ef_w17)}</strong></span>
<span style="color:{wow_color_ef};font-weight:700;">{wow_str_ef}</span>
</div>
</div>
<div style="border:1px solid var(--rule);padding:16px 18px;border-radius:3px;background:var(--paper);">
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">ConvRate</div>
<div style="display:flex;align-items:baseline;gap:12px;margin-top:6px;">
<div style="font-size:36px;font-weight:600;color:{CR_ACCENT};letter-spacing:-.02em;">{fmt_pct2(cv_w18)}</div>
{pill_cv}
</div>
<div style="margin-top:10px;display:flex;gap:12px;font-size:11px;color:var(--ink-soft);">
<span>Week 17: <strong>{fmt_pct2(cv_w17)}</strong></span>
<span style="color:{wow_color_cv};font-weight:700;">{wow_str_cv}</span>
</div>
</div>
</div>'''
    
    # === ALERTAS Críticas dentro de canasta · 3 cards ===
    alertas_canasta_html = _render_canasta_alertas(c, CR_ACCENT)
    
    # === RESUMEN EJECUTIVO dentro de canasta · 10 findings 2 cols ===
    findings = _build_canasta_findings(c)
    resumen_canasta_html = render_resumen_ejecutivo(
        findings, accent_color=CR_ACCENT, scope='canasta',
        header_title=f'Resumen Ejecutivo · Canasta {c["short"]}'
    )
    
    # === SEVERIDAD dentro de canasta · 2 cols ===
    levels_ef = make_severity_levels(c['sev_ef'], LEVELS_EFICACIA)
    levels_cv = make_severity_levels(c['sev_cv'], LEVELS_CONVRATE)
    sev_block_ef = render_severity_block('% Eficacia', '●', '#EA0074', levels_ef, n_p80)
    sev_block_cv = render_severity_block('Conv Rate', '●', CR_ACCENT, levels_cv, n_p80)
    severity_canasta_html = render_severity_2cols(sev_block_ef, sev_block_cv)
    
    # === Tabs Top 10 por dimensión (con borde folder) ===
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']
    
    def panel_inner(df, dim_col, dim_label, val_col, val_label, parse_hotel=False, start_idx=0):
        rows = f'<div class="panel-header"><span>{dim_label}</span><span>{val_label}</span><span>BKGS</span></div>'
        for i, r in df.iterrows():
            raw = r[dim_col]
            label = clean_hotel_name(raw) if parse_hotel else (clean_corp_name(raw) if dim_col=="CorpName" else raw)
            label = truncate(label, 28)
            rows += (f'<div class="panel-row">'
                     f'<span class="label">{start_idx + i + 1}. {label}</span>'
                     f'<span class="efic">{fmt_pct2(r[val_col])}</span>'
                     f'<span class="cr">{fmt_int_es(r["Bookings"])}</span>'
                     f'</div>')
        return rows
    
    def tab_panel_2cols(t_key, df_full, dim_col, dim_label, parse_hotel=False, val_col='Eficacia', val_label='Eficacia'):
        df_top10 = df_full.head(10).reset_index(drop=True)
        df1 = df_top10.iloc[:5].reset_index(drop=True)
        df2 = df_top10.iloc[5:10].reset_index(drop=True)
        col1 = panel_inner(df1, dim_col, dim_label, val_col, val_label, parse_hotel, start_idx=0)
        col2 = panel_inner(df2, dim_col, dim_label, val_col, val_label, parse_hotel, start_idx=5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'
    
    def tab_panel_channel_split(t_key, df_full):
        df_pp = df_full[df_full['ExternalProviderName'].isin(PRODUCTO_PROPIO)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
        df_tp = df_full[df_full['ExternalProviderName'].isin(THIRD_PARTY)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
        head_pp = '<div style="font-size:10px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>'
        head_tp = '<div style="font-size:10px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>'
        col_pp = head_pp + panel_inner(df_pp, 'ExternalProviderName', 'Channel', 'Eficacia', 'Eficacia')
        col_tp = head_tp + (panel_inner(df_tp, 'ExternalProviderName', 'Channel', 'Eficacia', 'Eficacia') if len(df_tp)>0 else '<div style="font-size:11px;color:var(--ink-muted);">Sin channels Third Party para esta canasta</div>')
        body = f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col_pp}</div><div>{col_tp}</div></div>'
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'
    
    tabs_html = f'''<h3 style="font-size:15px;font-weight:600;margin:32px 0 12px;color:var(--ink);">📊 Análisis por dimensión</h3>
<div class="canasta-tabs canasta-tabs-{idx_str}" style="margin:8px 0 24px;">
<input checked="" id="tab-cb-{idx_str}-destino" name="tabs-cb-{idx_str}" type="radio"/>
<input id="tab-cb-{idx_str}-corp" name="tabs-cb-{idx_str}" type="radio"/>
<input id="tab-cb-{idx_str}-hotel" name="tabs-cb-{idx_str}" type="radio"/>
<input id="tab-cb-{idx_str}-channel" name="tabs-cb-{idx_str}" type="radio"/>
<div class="tabs-row">
<label class="tab-label tab-folder" for="tab-cb-{idx_str}-destino">Destino</label>
<label class="tab-label tab-folder" for="tab-cb-{idx_str}-corp">Corporativo</label>
<label class="tab-label tab-folder" for="tab-cb-{idx_str}-hotel">Hotel</label>
<label class="tab-label tab-folder" for="tab-cb-{idx_str}-channel">Channel</label>
</div>
<div class="tab-panels" style="border-top:1px solid var(--rule);padding-top:16px;">
{tab_panel_2cols('destino', c['top_dest'], 'Destino', 'Destino')}
{tab_panel_2cols('corp', c['top_corp'], 'CorpName', 'Corporativo')}
{tab_panel_2cols('hotel', c['top_hot'], 'Hotel', 'Hotel', parse_hotel=True)}
{tab_panel_channel_split('channel', c['top_chan'])}
</div>
</div>'''
    
    extra_css = f'''<style>
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-destino:checked ~ .tabs-row label[for="tab-cb-{idx_str}-destino"],
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-corp:checked ~ .tabs-row label[for="tab-cb-{idx_str}-corp"],
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-hotel:checked ~ .tabs-row label[for="tab-cb-{idx_str}-hotel"],
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-channel:checked ~ .tabs-row label[for="tab-cb-{idx_str}-channel"]{{
  color:var(--ink);background:var(--paper);border-color:var(--rule);border-bottom-color:var(--paper);
}}
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-destino:checked ~ .tab-panels .tab-panel-c[data-tab="destino"],
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-corp:checked ~ .tab-panels .tab-panel-c[data-tab="corp"],
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-hotel:checked ~ .tab-panels .tab-panel-c[data-tab="hotel"],
.canasta-tabs-{idx_str} input#tab-cb-{idx_str}-channel:checked ~ .tab-panels .tab-panel-c[data-tab="channel"]{{display:block;}}
.canasta-tabs-{idx_str} .tab-panel-c .panel-row .label{{color:{CR_ACCENT};}}
.canasta-tabs-{idx_str} .tab-panel-c .panel-row .cr{{color:var(--ink);}}
</style>'''
    
    # === Bajo Rendimiento + Sin Conversión a 10 en 2 columnas ===
    def render_top10_2cols(df, title, accent, value1_label, value1_col, value2_label=None, value2_col=None):
        if len(df) == 0: return ''
        df = df.head(10).reset_index(drop=True)
        df1 = df.iloc[:5].reset_index(drop=True)
        df2 = df.iloc[5:10].reset_index(drop=True)
        
        def render_col(sub, start_idx):
            cols_grid = '1fr 70px 60px 60px' if value2_col else '1fr 70px 60px'
            html = ''
            for i, r in sub.iterrows():
                cells = (f'<div><div style="color:{accent};font-weight:600;line-height:1.3;">{start_idx+i+1}. {truncate(clean_hotel_name(r["Hotel"]),28)}</div>'
                         f'<div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;">{r["CorpName"]}</div></div>'
                         f'<span style="text-align:right;color:{accent};font-weight:600;">{fmt_int_es(r["CR_Unicos"])}</span>'
                         f'<span style="text-align:right;color:var(--ink);font-weight:600;">{fmt_pct2(r[value1_col])}</span>')
                if value2_col:
                    cells += f'<span style="text-align:right;color:{accent};font-weight:600;">{fmt_pct2(r[value2_col])}</span>'
                html += f'<div style="display:grid;grid-template-columns:{cols_grid};gap:8px;padding:6px 0;border-bottom:1px solid var(--rule-soft);font-size:11px;">{cells}</div>'
            return html
        
        col1 = render_col(df1, 0)
        col2 = render_col(df2, 5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div style="margin-top:24px;"><h3 style="font-size:13px;font-weight:700;color:{accent};text-transform:uppercase;letter-spacing:.10em;margin:0 0 10px;">{title}</h3>{body}</div>'
    
    bajo_rows = render_top10_2cols(c['bajo'], f'Top 10 · Bajo Rendimiento · Canasta {c["short"]}', CR_ACCENT, 'Eficacia', 'Eficacia', 'Conv Rate', 'ConvRate')
    sin_rows = render_top10_2cols(c['sin_conv'], f'Top 10 · Sin Conversión · Canasta {c["short"]}', CR_ACCENT, 'Eficacia', 'Eficacia')
    
    # === Síntesis ejecutiva (texto narrativo corto antes del Plan) ===
    sintesis_text = (
        f'<strong>Lectura {c["short"]}:</strong> {n_p80:,} hoteles P80 · {n_critmas_str} en Severity Crítica+ ({pct_critmas_str}) · '
        f'{n_sc_total:,} sin conversión ({pct_sc_str}). '
        f'Eficacia {fmt_pct2(ef_w18)} ({m18["banda_eficacia"]}) y Conv Rate {fmt_pct2(cv_w18)} ({m18["banda_convrate"]}). '
        f'Las acciones siguientes ordenan por horizonte (Quick Win → Estratégica) y Área Accountable.'
    ).format() if False else None  # placeholder, se construye abajo
    
    n_critmas_ef_local = c['sev_ef'].get('Súper Crítica',0) + c['sev_ef'].get('Crítica',0)
    pct_critmas = n_critmas_ef_local / max(n_p80,1) * 100
    pct_sc = n_sc_total / max(n_p80,1) * 100
    
    sintesis_html = f'''<div style="margin-top:32px;padding:16px 20px;background:var(--paper-soft);border-left:3px solid {CR_ACCENT};border-radius:3px;font-size:13px;line-height:1.55;color:var(--ink-soft);">
<div style="font-size:10px;font-weight:700;color:{CR_ACCENT};letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">📝 Síntesis ejecutiva</div>
Canasta {c["short"]} con {fmt_int_es(n_p80)} hoteles P80. <strong>{fmt_int_es(n_critmas_ef_local)} en Severity Crítica+</strong> ({f"{pct_critmas:.1f}".replace(".",",")}%) y <strong>{fmt_int_es(int(n_sc_total))} sin conversión</strong> ({f"{pct_sc:.1f}".replace(".",",")}%). Eficacia {fmt_pct2(ef_w18)} (banda {m18["banda_eficacia"]}) y Conv Rate {fmt_pct2(cv_w18)} (banda {m18["banda_convrate"]}). Las acciones del Plan siguiente ordenan por horizonte (Quick Win → Estratégica) y Área Accountable.
</div>'''
    
    # === Plan de Acción dentro de la canasta · 6 acciones · 2 columnas ===
    canasta_label = c['short']
    h_top_crit = c['critic'].iloc[0] if len(c['critic']) > 0 else None
    h_top_sc = c['sin_conv'].iloc[0] if len(c['sin_conv']) > 0 else None
    
    plan_canasta_rows = ''
    if h_top_crit is not None:
        plan_canasta_rows += (
            f'<div class="action-row qw">'
            f'<div class="action-owner-badge">Supply Optimization</div>'
            f'<div class="accion">Escalar caso Crítico de canasta {canasta_label}: <strong>{truncate(clean_hotel_name(h_top_crit["Hotel"]),38)}</strong> ({h_top_crit["CorpName"]}) con Eficacia {fmt_pct2(h_top_crit["Eficacia"])} y {fmt_int_es(h_top_crit["CR_Unicos"])} CR.</div>'
            f'<div class="action-meta-bottom"><span class="cluster-tag">Quick Win</span><span class="meta-item"><strong>Plazo</strong> 5 días</span><span class="meta-item"><strong>Métrica</strong> Eficacia &gt; 85%</span></div>'
            f'</div>'
        )
    if h_top_sc is not None:
        plan_canasta_rows += (
            f'<div class="action-row qw">'
            f'<div class="action-owner-badge">Supply Optimization / TPS</div>'
            f'<div class="accion">Diagnóstico técnico de <strong>{truncate(clean_hotel_name(h_top_sc["Hotel"]),38)}</strong> ({fmt_int_es(h_top_sc["CR_Unicos"])} CR sin BKGS) en canasta {canasta_label} · revisar mapping y paridad.</div>'
            f'<div class="action-meta-bottom"><span class="cluster-tag">Quick Win</span><span class="meta-item"><strong>Plazo</strong> 1 semana</span><span class="meta-item"><strong>Métrica</strong> Bookings &gt; 0</span></div>'
            f'</div>'
        )
    plan_canasta_rows += (
        f'<div class="action-row mp">'
        f'<div class="action-owner-badge">Supply Optimization</div>'
        f'<div class="accion">Plan de saneamiento para los <strong>{fmt_int_es(n_critmas_ef_local)} hoteles Crítica+</strong> de Eficacia en canasta {canasta_label}.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority</span><span class="meta-item"><strong>Plazo</strong> 3 semanas</span><span class="meta-item"><strong>Métrica</strong> {int(n_critmas_ef_local*0.5)} a Revisar</span></div>'
        f'</div>'
    )
    plan_canasta_rows += (
        f'<div class="action-row mp">'
        f'<div class="action-owner-badge">Supply Comercial / Wholesale</div>'
        f'<div class="accion">Revisión de ConvRate de canasta {canasta_label} (actual {fmt_pct2(cv_w18)}) frente al target ≥ 2,5%.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority</span><span class="meta-item"><strong>Plazo</strong> 2 semanas</span><span class="meta-item"><strong>Métrica</strong> ConvRate ↑</span></div>'
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
        f'<div class="accion">Auditar canales de mayor share en canasta {canasta_label} y optimizar paridad/latencia con principales corp.</div>'
        f'<div class="action-meta-bottom"><span class="cluster-tag">Estratégica</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> Eficacia &gt; 95%</span></div>'
        f'</div>'
    )
    
    plan_canasta_html = f'''<div style="margin-top:48px;padding-top:40px;border-top:1px solid var(--rule);">
<h3 style="font-size:13px;font-weight:700;color:{CR_ACCENT};text-transform:uppercase;letter-spacing:.10em;margin:0 0 10px;">Plan de Acción · canasta {canasta_label}</h3>
<div class="action-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{plan_canasta_rows}</div>
</div>'''
    
    # Banner minimalista de descarga · Excel filtrado por canasta
    canasta_filename_map = {'b2c':'B2C', 'op':'OP', 'cug':'CUG'}
    file_suffix = canasta_filename_map.get(idx_str, 'B2C')
    excel_canasta_url = f'Analisis_Checkrates_{file_suffix}_7d.xlsx'
    banner_descarga_canasta = f'''<div style="margin-top:24px;padding:14px 18px;background:var(--paper-soft);border:1px solid var(--rule);border-radius:4px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
<div style="font-size:12px;color:var(--ink-soft);line-height:1.4;">
<span style="font-size:13px;color:var(--ink);">📥</span>
&nbsp;&nbsp;Descargar análisis completo · <strong style="color:{CR_ACCENT};">Canasta {c['short']}</strong>
<span style="display:inline-block;margin-left:8px;font-size:11px;color:var(--ink-muted);">9 pestañas · Top 50 por dimensión</span>
</div>
<a href="{excel_canasta_url}" style="display:inline-block;padding:6px 14px;background:{CR_ACCENT};color:#fff;font-size:11px;font-weight:600;text-decoration:none;border-radius:3px;letter-spacing:.04em;text-transform:uppercase;">Excel ↗</a>
</div>'''
    
    return f'''{extra_css}<details class="canasta-block" style="margin-bottom:32px;">
<summary>
<div class="summary-title">
<h2>Canasta {c['short']}</h2>
<span class="section-subtitle">{c['name']}</span>
</div>
<span class="toggle-arrow"><span class="label"></span><span class="icon"></span></span>
</summary>
<div class="canasta-content">
{kpi_block}
{alertas_canasta_html}
{resumen_canasta_html}
{severity_canasta_html}
{tabs_html}


{sintesis_html}
{plan_canasta_html}
{banner_descarga_canasta}
</div>
</details>
'''

# Build
CANASTA_SECTION = f'''<section id="por-canasta">
<div class="section-head">
<div>
<div class="section-num">Sección 12</div>
<h2 class="section-title">Análisis por canasta</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">B2C · B2B-OP · CUG</span>
<p class="section-kicker">Métricas, severidad y casos críticos por canasta. CUG es la única en banda Aceptable de ConvRate; B2C en Crítica.</p>
</div>
</div>
'''
for idx_key, c_key in [('op','op'),('cug','cug'),('b2c','b2c')]:
    CANASTA_SECTION += render_canasta_block(CANASTA[c_key], idx_str=idx_key)
CANASTA_SECTION += '</section>\n'

# Cierre con script (después se agrega footer en assembler)
SCRIPT_CIERRE = '''
<script>
const sections = document.querySelectorAll('section[id]');
const tocLinks = document.querySelectorAll('.toc a');
if (tocLinks.length > 0) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        tocLinks.forEach(l => l.classList.remove('active'));
        const a = document.querySelector('.toc a[href="#' + entry.target.id + '"]');
        if(a) a.classList.add('active');
      }
    });
  }, {rootMargin:'-30% 0px -60% 0px'});
  sections.forEach(s => observer.observe(s));
  tocLinks.forEach(l => l.addEventListener('click', e => {
    e.preventDefault();
    document.querySelector(l.getAttribute('href'))?.scrollIntoView({behavior:'smooth'});
  }));
}
</script>

</body>
</html>
'''

with open('part3_cr.html','w') as f:
    f.write(CANASTA_SECTION + '\n</div>\n' + SCRIPT_CIERRE)
print(f"Part 3 CR escrito: {len(CANASTA_SECTION + SCRIPT_CIERRE):,} chars")
