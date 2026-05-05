"""
Renderer RND parte 3: Análisis por Canasta (B2C, B2B-OP, CUG)
Cards colapsables con KPIs hero + tabs Top 5
"""
import pickle, pandas as pd, numpy as np
from engine import *
from render_helpers import *

with open('rnd_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; CANASTA = D['CANASTA']

with open('asset_rnd_footer.html') as f: FOOTER = f.read()

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
        return f'{sign}{v:.2f}pp'.replace('.',',')
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
    
    def card_for(card_title, icon, nd_obj, rpm_obj, label_field):
        if nd_obj is None or rpm_obj is None:
            return ''
        sub_nd = render_alert_subcell(
            '% NoDispo', '#EA0074', '#FCE4F1',
            truncate(clean_hotel_name(str(nd_obj[label_field])), 22) if label_field=='Hotel' else truncate(str(nd_obj[label_field]),22),
            f'{nd_obj["%NoDispo"]*100:.2f}%'.replace('.',','),
            '#EA0074'
        )
        sub_rpm = render_alert_subcell(
            'IPM', '#5C469C', '#EDE8F7',
            truncate(clean_hotel_name(str(rpm_obj[label_field])), 22) if label_field=='Hotel' else truncate(str(rpm_obj[label_field]),22),
            f'${fmt_num2(rpm_obj["RPM"])}',
            '#5C469C'
        )
        return render_alert_card(card_title, icon, accent_color, sub_nd, sub_rpm)
    
    card_h = card_for('Hoteles', '🏨', c.get('alert_h_nd'), c.get('alert_h_rpm'), 'Hotel')
    card_d = card_for('Destinos', '📍', c.get('alert_d_nd'), c.get('alert_d_rpm'), 'Destino')
    card_co = card_for('Corp', '🏢', c.get('alert_co_nd'), c.get('alert_co_rpm'), 'CorpName')
    
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
    
    n_crit = c['n_critica']
    n_p80 = len(c['p80'])
    n_sc = (c['p80']['Bookings']==0).sum()
    n_sc_total = (c['agg_hotel']['Bookings']==0).sum()
    
    # KPI hero (versión compacta para canasta)
    pill_nd = banda_pill(banda_nd, target='&lt; 3%', font_size='9px')
    pill_rp = banda_pill(banda_rp, target='≥ $650', font_size='9px')
    
    wow_color_nd = '#2F6C34' if pct_wow < 0 else '#C0392B'
    wow_color_rp = '#2F6C34' if rpm_wow > 0 else '#C0392B'
    wow_str_nd = (f'↓ {pct_wow:+.2f}pp' if pct_wow < 0 else (f'↑ +{pct_wow:.2f}pp' if pct_wow > 0 else '= 0,00pp')).replace('.', ',')
    wow_str_rp = (f'↑ {rpm_wow:+.1f}%' if rpm_wow > 0 else (f'↓ {rpm_wow:+.1f}%' if rpm_wow < 0 else '= 0%')).replace('.', ',')
    
    kpi_block = f'''<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 24px;">
<div style="border:1px solid var(--rule);padding:16px 18px;border-radius:3px;background:var(--paper);">
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">% No Dispo</div>
<div style="display:flex;align-items:baseline;gap:12px;margin-top:6px;">
<div style="font-size:36px;font-weight:600;color:#EA0074;letter-spacing:-.02em;">{fmt_pct2(pct_w18)}</div>
{pill_nd}
</div>
<div style="margin-top:10px;display:flex;gap:12px;font-size:11px;color:var(--ink-soft);">
<span>Week 17: <strong>{fmt_pct2(pct_w17)}</strong></span>
<span style="color:{wow_color_nd};font-weight:700;">{wow_str_nd}</span>
</div>
</div>
<div style="border:1px solid var(--rule);padding:16px 18px;border-radius:3px;background:var(--paper);">
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">IPM <span style="font-weight:500;text-transform:none;letter-spacing:0;color:var(--ink-soft);">· Income Per Million USD</span></div>
<div style="display:flex;align-items:baseline;gap:12px;margin-top:6px;">
<div style="font-size:36px;font-weight:600;color:#EA0074;letter-spacing:-.02em;">${fmt_num2(rpm_w18)}</div>
{pill_rp}
</div>
<div style="margin-top:10px;display:flex;gap:12px;font-size:11px;color:var(--ink-soft);">
<span>Week 17: <strong>${fmt_num2(rpm_w17)}</strong></span>
<span style="color:{wow_color_rp};font-weight:700;">{wow_str_rp}</span>
</div>
</div>
</div>'''
    
    # === ALERTAS Críticas dentro de canasta ===
    alertas_canasta_html = _render_canasta_alertas_rnd(c)
    
    # === RESUMEN EJECUTIVO dentro de canasta · 10 findings 2 cols ===
    findings = _build_canasta_findings_rnd(c)
    resumen_canasta_html = render_resumen_ejecutivo(
        findings, accent_color='#EA0074', scope='canasta',
        header_title=f'Resumen Ejecutivo · Canasta {c["short"]}'
    )
    
    # === SEVERIDAD dentro de canasta · 2 cols ===
    levels_nd = make_severity_levels(c['sev_nd'], LEVELS_NODISPO)
    levels_rpm = make_severity_levels(c['sev_rpm'], LEVELS_RPM)
    sev_block_nd = render_severity_block('% NoDispo', '●', '#EA0074', levels_nd, n_p80)
    sev_block_rpm = render_severity_block('IPM (Income Per Million USD)', '●', '#EA0074', levels_rpm, n_p80)
    severity_canasta_html = render_severity_2cols(sev_block_nd, sev_block_rpm)
    
    # === Tabs (Destino, Corp, Hotel, País) — Top 10 a 2 columnas, borde folder ===
    def panel_inner_rnd(df, dim_col, dim_label, parse_hotel=False, start_idx=0):
        rows = f'<div class="panel-header"><span>{dim_label}</span><span>%NoDispo</span><span>BKGS</span></div>'
        for i, r in df.iterrows():
            raw = r[dim_col]
            label = clean_hotel_name(raw) if parse_hotel else raw
            label = truncate(label, 28)
            rows += (f'<div class="panel-row">'
                     f'<span class="label">{start_idx + i + 1}. {label}</span>'
                     f'<span class="efic">{fmt_pct2(r["%NoDispo"])}</span>'
                     f'<span class="cr">{fmt_int_es(r["Bookings"])}</span>'
                     f'</div>')
        return rows
    
    def tab_panel(t_key, df_full, dim_col, dim_label, parse_hotel=False):
        df_top10 = df_full.head(10).reset_index(drop=True)
        df1 = df_top10.iloc[:5].reset_index(drop=True)
        df2 = df_top10.iloc[5:10].reset_index(drop=True)
        col1 = panel_inner_rnd(df1, dim_col, dim_label, parse_hotel, start_idx=0)
        col2 = panel_inner_rnd(df2, dim_col, dim_label, parse_hotel, start_idx=5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div class="tab-panel-c" data-tab="{t_key}">{body}</div>'
    
    tabs_html = f'''<h3 style="font-size:15px;font-weight:600;margin:32px 0 12px;color:var(--ink);">Tabs por dimensión</h3>
<div class="canasta-tabs canasta-tabs-{idx_str}" style="margin:8px 0 24px;">
<input checked="" id="tab-{idx_str}-destino" name="tabs-{idx_str}" type="radio"/>
<input id="tab-{idx_str}-corp" name="tabs-{idx_str}" type="radio"/>
<input id="tab-{idx_str}-hotel" name="tabs-{idx_str}" type="radio"/>
<input id="tab-{idx_str}-pais" name="tabs-{idx_str}" type="radio"/>
<div class="tabs-row">
<label class="tab-label tab-folder" for="tab-{idx_str}-destino">Destino</label>
<label class="tab-label tab-folder" for="tab-{idx_str}-corp">Corporativo</label>
<label class="tab-label tab-folder" for="tab-{idx_str}-hotel">Hotel</label>
<label class="tab-label tab-folder" for="tab-{idx_str}-pais">País</label>
</div>
<div class="tab-panels" style="border-top:1px solid var(--rule);padding-top:16px;">
{tab_panel('destino', c['top_dest'], 'Destino', 'Destino')}
{tab_panel('corp', c['top_corp'], 'CorpName', 'Corporativo')}
{tab_panel('hotel', c['top_hot'], 'Hotel', 'Hotel', parse_hotel=True)}
{tab_panel('pais', c['top_pais'], 'PaisDestino', 'País')}
</div>
</div>'''
    
    extra_css = f'''<style>
.canasta-tabs-{idx_str} input#tab-{idx_str}-destino:checked ~ .tabs-row label[for="tab-{idx_str}-destino"],
.canasta-tabs-{idx_str} input#tab-{idx_str}-corp:checked ~ .tabs-row label[for="tab-{idx_str}-corp"],
.canasta-tabs-{idx_str} input#tab-{idx_str}-hotel:checked ~ .tabs-row label[for="tab-{idx_str}-hotel"],
.canasta-tabs-{idx_str} input#tab-{idx_str}-pais:checked ~ .tabs-row label[for="tab-{idx_str}-pais"]{{
  color:var(--ink);background:var(--paper);border-color:var(--rule);border-bottom-color:var(--paper);
}}
.canasta-tabs-{idx_str} input#tab-{idx_str}-destino:checked ~ .tab-panels .tab-panel-c[data-tab="destino"],
.canasta-tabs-{idx_str} input#tab-{idx_str}-corp:checked ~ .tab-panels .tab-panel-c[data-tab="corp"],
.canasta-tabs-{idx_str} input#tab-{idx_str}-hotel:checked ~ .tab-panels .tab-panel-c[data-tab="hotel"],
.canasta-tabs-{idx_str} input#tab-{idx_str}-pais:checked ~ .tab-panels .tab-panel-c[data-tab="pais"]{{display:block;}}
.canasta-tabs-{idx_str} .tab-panel-c .panel-row .label{{color:#EA0074;}}
.canasta-tabs-{idx_str} .tab-panel-c .panel-row .cr{{color:var(--ink);}}
</style>'''
    
    # === Bajo Rendimiento + Sin Conversión a 10 en 2 columnas ===
    def render_top10_2cols_rnd(df, title, val_left_label, val_left_col, val_right_label=None, val_right_col=None):
        if len(df) == 0: return ''
        df = df.head(10).reset_index(drop=True)
        df1 = df.iloc[:5].reset_index(drop=True)
        df2 = df.iloc[5:10].reset_index(drop=True)
        
        def render_col(sub, start_idx):
            cols_grid = '1fr 70px 60px 60px' if val_right_col else '1fr 70px 60px'
            html = ''
            for i, r in sub.iterrows():
                cells = (f'<div><div style="color:#EA0074;font-weight:600;line-height:1.3;">{start_idx+i+1}. {truncate(clean_hotel_name(r["Hotel"]),28)}</div>'
                         f'<div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;">{r["CorpName"]}</div></div>'
                         f'<span style="text-align:right;color:#EA0074;font-weight:600;">{fmt_big(r["Trafico"])}</span>')
                if val_left_col == '%NoDispo':
                    cells += f'<span style="text-align:right;color:var(--ink);font-weight:600;">{fmt_pct2(r["%NoDispo"])}</span>'
                else:
                    cells += f'<span style="text-align:right;color:var(--ink);font-weight:600;">{fmt_int_es(r[val_left_col])}</span>'
                if val_right_col:
                    if val_right_col == 'RPM':
                        cells += f'<span style="text-align:right;color:#EA0074;font-weight:600;">${fmt_num2(r["RPM"])}</span>'
                    else:
                        cells += f'<span style="text-align:right;color:#EA0074;font-weight:600;">{fmt_num2(r[val_right_col])}</span>'
                html += f'<div style="display:grid;grid-template-columns:{cols_grid};gap:8px;padding:6px 0;border-bottom:1px solid var(--rule-soft);font-size:11px;">{cells}</div>'
            return html
        
        col1 = render_col(df1, 0)
        col2 = render_col(df2, 5) if len(df2)>0 else ''
        body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;"><div>{col1}</div><div>{col2}</div></div>'
                if col2 else f'<div>{col1}</div>')
        return f'<div style="margin-top:24px;"><h3 style="font-size:13px;font-weight:700;color:#EA0074;text-transform:uppercase;letter-spacing:.10em;margin:0 0 10px;">{title}</h3>{body}</div>'
    
    bajo_rows = render_top10_2cols_rnd(c['bajo_rend'], f'Top 10 · Bajo Rendimiento · Canasta {c["short"]}', 'BKGS', 'Bookings', 'IPM', 'RPM')
    sin_rows = render_top10_2cols_rnd(c['sin_conv'], f'Top 10 · Sin Conversión · Canasta {c["short"]}', '%NoDispo', '%NoDispo')
    
    # === Síntesis ejecutiva ===
    n_critmas_local = c['sev_nd'].get('Súper Crítica',0) + c['sev_nd'].get('Crítica',0)
    pct_critmas = n_critmas_local / max(n_p80,1) * 100
    pct_sc = n_sc_total / max(len(c['agg_hotel']),1) * 100
    
    sintesis_html = f'''<div style="margin-top:32px;padding:16px 20px;background:var(--paper-soft);border-left:3px solid #EA0074;border-radius:3px;font-size:13px;line-height:1.55;color:var(--ink-soft);">
<div style="font-size:10px;font-weight:700;color:#EA0074;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">📝 Síntesis ejecutiva</div>
Canasta {c["short"]} con {fmt_int_es(n_p80)} hoteles P80. <strong>{fmt_int_es(n_critmas_local)} en Severity Crítica+ por %NoDispo</strong> ({f"{pct_critmas:.1f}".replace(".",",")}% del P80) y <strong>{fmt_int_es(int(n_sc_total))} sin conversión</strong> ({f"{pct_sc:.1f}".replace(".",",")}% del total). %NoDispo {fmt_pct2(pct_w18)} (banda {m18["banda_nodispo"]}) y IPM ${fmt_num2(rpm_w18)} (banda {m18["banda_rpm"]}). Las acciones del Plan siguiente ordenan por horizonte (Quick Win → Estratégica) y Área Accountable.
</div>'''
    
    # === Plan de Acción (mantengo estructura existente, ya está en 2 cols) ===
    canasta_label = c['short']
    weight_str = '0,1' if 'B2C' in c['name'] else '0,6'
    h_top_dnc = c['top_hot'].iloc[0] if len(c['top_hot']) > 0 else None
    h_top_sc = c['sin_conv'].iloc[0] if len(c['sin_conv']) > 0 else None
    
    plan_canasta_rows = ''
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
    
    plan_canasta_html = f'''<div style="margin-top:24px;">
<h3 style="font-size:13px;font-weight:700;color:#EA0074;text-transform:uppercase;letter-spacing:.10em;margin:0 0 10px;">Plan de Acción · canasta {canasta_label}</h3>
<div class="action-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{plan_canasta_rows}</div>
</div>'''
    
    return f'''{extra_css}<details class="canasta-block">
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
{tabs_html}


{sintesis_html}
{plan_canasta_html}
</div>
</details>
'''

# Build
CANASTA_SECTION = '''<section id="por-canasta">
<div class="section-head">
<div>
<div class="section-num">Sección 11</div>
<h2 class="section-title">Análisis por canasta</h2>
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
