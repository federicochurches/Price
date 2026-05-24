"""
Renderer RND parte 2: Resumen Ejecutivo, Severity, Top 5
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
import os, pandas as pd, numpy as np
from engine import *
from render_helpers import *
from historico_module_rnd import render_historico_rnd
from template_seguimiento import render_seguimiento_block

with open(os.getenv('PICKLE_RND', 'rnd_w20_data.pkl'),'rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']; TAB_NoDispo = D['TAB_NoDispo']; TAB_RPM = D['TAB_RPM']

# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

CANASTA = D['CANASTA']; sev_nd = D['sev_nd']; sev_rpm = D['sev_rpm']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']

WEEK_NUM      = D.get('VOL_NUM', '19')
WEEK_PREV_NUM = str(int(WEEK_NUM) - 1)
SEGUIMIENTO_FILE = f'_seguimiento/plan_seguimiento_W{WEEK_PREV_NUM}.md'

# ============ RESUMEN EJECUTIVO · 10 findings ============

# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

def build_findings():
    """Genera 10 findings con estructura template: numero + titulo + desc."""
    pct = M['global_current']['pct_nodispo']; pct17 = M['global_w17']['pct_nodispo']
    rpm = M['global_current']['rpm']; rpm17 = M['global_w17']['rpm']
    bk = M['global_current']['bookings']; bk17 = M['global_w17']['bookings']
    gb = M['global_current']['gb_usd']; gb17 = M['global_w17']['gb_usd']
    
    pct_wow = (pct - pct17) * 100
    rpm_wow = (rpm/rpm17 - 1) * 100
    bk_wow = (bk/bk17 - 1) * 100
    
    n_p80 = len(p80_hotel)
    n_supcrit = sev_nd['Súper Crítica']
    n_critmas = sev_nd['Crítica'] + sev_nd['Súper Crítica']
    n_sin_conv = sev_rpm['Sin Conversión']
    n_critica_rpm = sev_rpm['Crítica']
    pct_sin_conv = n_sin_conv/n_p80*100
    
    dnc_p80_total = p80_hotel['DemandaNoConvertida'].sum()
    dnc_global = (g_hotel['Trafico']*g_hotel['%NoDispo']).sum()
    pct_dnc_p80 = dnc_p80_total/dnc_global*100
    
    by_corp = g_hotel.groupby('CorpName').agg(DNC=('DemandaNoConvertida','sum'), TR=('Trafico','sum'), BK=('Bookings','sum')).reset_index()
    by_corp = by_corp.sort_values('DNC', ascending=False)
    top1_corp = by_corp.iloc[0]
    
    by_dest = g_hotel.groupby('Destino').agg(DNC=('DemandaNoConvertida','sum'), TR=('Trafico','sum')).reset_index()
    by_dest['pctND'] = by_dest['DNC']/by_dest['TR']
    by_dest = by_dest.sort_values('DNC', ascending=False).head(3)
    
    cb = M[f'B2C_w{WEEK_NUM_INT}']; co = M[f'B2B (OP)_w{WEEK_NUM_INT}']; cu = M[f'CUG (UOP)_w{WEEK_NUM_INT}']
    cug_rpm_wow = (cu['rpm']/M[f'CUG (UOP)_w{WEEK_PREV_INT}']['rpm']-1)*100
    
    h0 = TOP['sin_conv'].iloc[0]
    
    def es_pct(v, dec=2):
        return f'{v:.{dec}f}%'.replace('.',',')
    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}'.replace('.',',')
    def es_pct1(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.1f}%'.replace('.',',')
    def es_num2(v):
        try: return f'{int(round(float(v))):,}'.replace(',','.')
        except: return '—'
    
    def pill_banda(banda, target=''):
        bc = BANDA_COLORS.get(banda, BANDA_COLORS['Sin Conversión'])
        tgt = f' <span style="font-weight:400;opacity:.8;font-size:8px;">· {target}</span>' if target else ''
        return (f'<span style="display:inline-block;font-size:9px;font-weight:700;letter-spacing:.04em;'
                f'text-transform:uppercase;padding:2px 7px;border-radius:3px;'
                f'background:{bc["bg"]};color:{bc["fg"]};border:1px solid {bc["bd"]};">{banda}{tgt}</span>')

    def pill_wow_nd(v):
        """Pill WoW para %NoDispo: verde si baja."""
        if abs(v) < 0.05: return ''
        mejora = v < 0
        col = '#2F6C34' if mejora else '#C0392B'
        bg  = '#EAF3DE' if mejora else '#FCE8E6'
        txt = f'{"↓" if v<0 else "↑"}{abs(v):.2f}'.replace('.',',')
        return f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 6px;border-radius:3px;background:{bg};color:{col};">{txt}</span>'

    def pill_wow_ipm(v):
        """Pill WoW para IPM: verde si sube."""
        if abs(v) < 0.5: return ''
        mejora = v > 0
        col = '#2F6C34' if mejora else '#C0392B'
        bg  = '#EAF3DE' if mejora else '#FCE8E6'
        txt = f'{"↑" if v>0 else "↓"}{abs(v):.1f}%'.replace('.',',')
        return f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 6px;border-radius:3px;background:{bg};color:{col};">{txt}</span>'

    findings = [
        {'numero': es_pct(pct*100,2),
         'titulo': f'%NoDispo global · {pill_banda(M[f'global_w{WEEK_NUM_INT}']["banda_nd"],"&lt;3%")} {pill_wow_nd(pct_wow)}',
         'desc': 'Primera vez que se acerca a la zona Exitosa tras semanas en Revisar — mejora estructural sostenida.'},
        {'numero': '$' + es_num2(rpm),
         'titulo': f'IPM · {pill_banda(M[f'global_w{WEEK_NUM_INT}']["banda_rpm"],"≥$650")} {pill_wow_ipm(rpm_wow)}',
         'desc': f'Sigue por debajo del target ≥$650. Bookings {es_pct1(bk_wow)} WoW anticipa presión adicional.'},
        {'numero': fmt_big(dnc_p80_total),
         'titulo': 'Demanda no convertida en P80',
         'desc': f'{f"{pct_dnc_p80:.0f}".replace(".",",")}% del total ({fmt_big(dnc_global)}) en los {fmt_int_es(n_p80)} hoteles del P80 · concentración estructural.'},
        {'numero': fmt_int_es(n_critmas),
         'titulo': f'Hoteles P80 Severity Crítica+ · {pill_banda("Crítica")}',
         'desc': f'{es_pct(n_critmas/n_p80*100,1)} del P80 · {n_supcrit} Súper Críticos requieren escalamiento inmediato a Supply.'},
        {'numero': fmt_int_es(n_sin_conv),
         'titulo': f'Hoteles Sin Conversión · {pill_banda("Sin Conversión")}',
         'desc': f'{es_pct(pct_sin_conv,1)} del P80 · cohorte estructural · diagnóstico técnico/contractual. {fmt_int_es(n_critica_rpm)} adicionales en Crítica IPM.'},
        {'numero': fmt_big(top1_corp["DNC"]),
         'titulo': f'{clean_corp_name(top1_corp["CorpName"])} · líder demanda perdida',
         'desc': 'Búsquedas no convertidas en P80 · escalamiento KAM directo, mayor palanca disponible esta semana.'},
        {'numero': es_pct(by_dest.iloc[0]["pctND"]*100,2),
         'titulo': f'{clean_destino_name(by_dest.iloc[0]["Destino"],28)} · destino crítico',
         'desc': f'{fmt_big(by_dest.iloc[0]["DNC"])} búsquedas no convertidas · concentra fugas de high-traffic markets.'},
        {'numero': '$' + es_num2(cu['rpm']),
         'titulo': f'CUG · IPM {pill_banda(cu["banda_rpm"])} {pill_wow_ipm(cug_rpm_wow)}',
         'desc': f'Canasta weight 0,6 · deterioro IPM pese a mejora en %NoDispo ({es_pct(cu["pct_nodispo"]*100,2)}) · atención prioritaria.'},
        {'numero': es_pct(co['pct_nodispo']*100,2),
         'titulo': f'B2B-OP · %NoDispo {pill_banda(co["banda_nodispo"])}',
         'desc': f'IPM ${es_num2(co["rpm"])} ({pill_banda(co["banda_rpm"])}) · canasta más sólida · refleja calidad del producto opaco premium.'},
        {'numero': fmt_big(h0["Trafico"]),
         'titulo': f'{truncate(clean_hotel_name(h0["Hotel"]),28)} · #1 Sin Conv',
         'desc': f'{h0["CorpName"]} · {fmt_big(h0["Trafico"])} búsquedas sin conversión · primera fila para revisión técnica.'},
    ]
    return findings

def render_resumen_ej():
    """Resumen Ejecutivo · estructura template literal."""
    from template_resumen import render_resumen_ejecutivo
    findings = build_findings()
    return render_resumen_ejecutivo(findings, accent_color='#EA0074', scope='global')

# ============ SECCIÓN SEVERITY %NoDispo ============
def render_severity_nodispo():
    levels = [
        ('Súper Crítica','&gt; 60%','#DC2626'),
        ('Crítica','20–60%','#C0392B'),
        ('Revisar','5–20%','#F97316'),
        ('Aceptable','3–5%','#FCD34D'),
        ('Exitosa','&lt; 3%','#1A6B4A'),
    ]
    total = int(sev_nd.sum())
    rows = ''
    for name, rng, bar_color in levels:
        n = int(sev_nd[name])
        pct = n/total*100 if total else 0
        bar_w = max(min(pct, 100), 0.5)
        # Badge paleta D: BANDA_COLORS es la única fuente de verdad
        bc = BANDA_COLORS.get(name, BANDA_COLORS['Sin Conversión'])
        badge_bg = bc['bg']; badge_fg = bc['fg']
        rows += (f'<div style="display:grid;grid-template-columns:110px 70px 1fr 65px 50px;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--rule-soft);">'
                 f'<span style="display:inline-block;padding:3px 8px;background:{badge_bg};color:{badge_fg};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                 f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                 f'<div style="height:8px;background:var(--paper-soft);position:relative;border-radius:2px;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{bar_color};border-radius:2px;"></div></div>'
                 f'<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(n)}</span>'
                 f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct:.1f}%</span>'
                 f'</div>')
    
    n_critmas = int(sev_nd['Crítica'] + sev_nd['Súper Crítica'])
    n_supc = int(sev_nd['Súper Crítica'])
    n_exito = int(sev_nd['Exitosa'])
    
    return f'''<section id="severity-nodispo">
<div class="section-head">
<div>
<div class="section-num">Sección 02</div>
<h2 class="section-title">🚨 Severity · % NoDispo</h2>
<span class="section-subtitle" style="color:#EA0074">P80 · {fmt_int_es(total)} hoteles</span>
<p class="section-kicker">Distribución de hoteles del Top tráfico (P80) por nivel de %NoDispo. El target es &lt;3% (banda Exitosa).</p>
</div>
</div>
<div>{rows}</div>
</section>
'''.replace('.','.',2)

# ============ SECCIÓN SEVERITY · NoDispo + IPM combinada en 2 cols ============
def render_severities_combinadas():
    """Severity %NoDispo + IPM lado a lado · una sola sección."""
    
    def render_table(sev_dict, levels_data, accent='#EA0074', fmt_label='pct'):
        total = int(sev_dict.sum()) if hasattr(sev_dict, "sum") else int(sum(sev_dict.values()))
        rows = ''
        for name, rng, _ in levels_data:
            n = int(sev_dict.get(name, 0))
            pct = n/total*100 if total else 0
            bar_w = max(min(pct, 100), 0.5)
            # Badge paleta D: BANDA_COLORS es la única fuente de verdad (importado de render_helpers)
            bc = BANDA_COLORS.get(name, BANDA_COLORS['Sin Conversión'])
            rows += (f'<div style="display:grid;grid-template-columns:120px 80px 1fr 60px 45px;gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--rule-soft);">'
                     f'<span style="display:inline-block;padding:3px 8px;background:{bc["bg"]};color:{bc["fg"]};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                     f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                     f'<div style="height:8px;background:var(--paper-soft);position:relative;border-radius:2px;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{bc["bar"]};border-radius:2px;"></div></div>'
                     f'<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(n)}</span>'
                     f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct:.1f}%</span>'
                     f'</div>')
        return rows, total
    
    levels_nd = [
        ('Súper Crítica','&gt; 60%','#161616'),
        ('Crítica','20–60%','#C0392B'),
        ('Revisar','5–20%','#F97316'),
        ('Aceptable','3–5%','#FCD34D'),
        ('Exitosa','&lt; 3%','#1A6B4A'),
    ]
    levels_ipm = [
        ('Sin Conversión','BKGS=0','#8A8377'),
        ('Crítica','< $199','#C0392B'),
        ('Revisar','$200–$499','#F97316'),
        ('Aceptable','$500–$649','#FCD34D'),
        ('Exitosa','≥ $650','#1A6B4A'),
    ]
    
    rows_nd, total_nd = render_table(sev_nd, levels_nd)
    rows_ipm, total_ipm = render_table(sev_rpm, levels_ipm)
    
    n_critmas = int(sev_nd['Crítica'] + sev_nd['Súper Crítica'])
    n_sc = int(sev_rpm['Sin Conversión'])
    n_crit_ipm = int(sev_rpm['Crítica'])
    n_proc = total_ipm - n_sc
    
    return f'''<section id="severity-combinada">
<div class="section-head">
<div>
<div class="section-num">Sección 02</div>
<h2 class="section-title">🚨 Severity</h2>
<span class="section-subtitle" style="color:#EA0074">P80 · {fmt_int_es(total_nd)} hoteles</span>
<p class="section-kicker">Distribución de hoteles del Top tráfico (P80) por nivel de %NoDispo (target &lt;3%) e IPM (Income Per Million USD · target ≥ $650). Sin Conversión es cohorte aparte (BKGS=0); Severity IPM se aplica solo a procesables.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#EA0074;margin:0 0 12px;">% No Disponibilidad</h3>
{rows_nd}
</div>
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#EA0074;margin:0 0 12px;">IPM (USD)</h3>
{rows_ipm}
</div>
</div>
</section>
'''

# ============ SECCIÓN TOP 5 (Demanda No Convertida, Bajo Rendimiento, Sin Conversión, Por Corp/Dest/Pais) ============
def render_top_table(title, num, df, cols_def, accent_color='#EA0074', subtitle='', kicker='', show_header=True, sb_id=None):
    """Top 100: primeras 10 visibles, resto sb-hidden, estilos unificados 11px.
    sb_id: si se pasa y show_header=True, primera columna del header es searchbox integrado (Prop D).
    """
    grid = ' '.join(c['width'] for c in cols_def).strip()
    if show_header:
        _hd = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:0 0 6px 0;border-bottom:2px solid {accent_color};margin-bottom:2px;">'
        for idx_c, c in enumerate(cols_def):
            if idx_c == 0 and sb_id:
                _hd += searchbox_header_html(sb_id, accent_color=accent_color,
                                              placeholder='Hotel o corporativo…',
                                              th_id=f'th-{sb_id}')
            else:
                h_align = c.get('align','right')
                color = accent_color if c.get('key') in ('hotel','label') else 'var(--ink-muted)'
                _hd += f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{color};text-align:{h_align};padding:9px 0;">{c["label"]}</span>'
        _hd += '</div>'
        header = _hd
    else:
        header = ''
    
    rows = header
    for i, r in df.iterrows():
        row_cells = ''
        for c in cols_def:
            align = c.get('align','right')
            val = c['fmt'](r) if callable(c['fmt']) else c['fmt']
            if c.get('key') == 'hotel':
                hotel_name = truncate(r.get('Hotel') or r.get('Destino') or r.get('CorpName') or r.get('PaisDestino') or '-', 36)
                sub = r.get('CorpName','')
                row_cells += (f'<div>'
                              f'<div style="font-size:11px;font-weight:600;color:{accent_color};line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{r.get("Hotel","")}">{i+1}. {hotel_name}</div>'
                              f'<div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.05em;margin-top:1px;">{sub}</div>'
                              f'</div>')
            else:
                row_cells += f'<span style="text-align:{align};color:var(--ink);font-size:11px;font-variant-numeric:tabular-nums;">{val}</span>'
        nd_curr  = round(float(r.get('%NoDispo', 0)) * 100, 4)
        nd_prev  = round(float(r.get('NoDispo_W18', nd_curr/100)*100 if '%NoDispo' in r.index else nd_curr), 4)
        ipm_curr = round(max(float(r.get('IPM', r.get('RPM', 0))), 0), 1)
        ipm_prev = round(max(float(r.get('IPM_W18', ipm_curr)), 0), 1)
        lbl = truncate(r.get('Hotel') or r.get('Destino') or r.get('CorpName') or r.get('PaisDestino') or '-', 28)
        hist_attrs = (f' data-hist-w21="{nd_curr}" data-hist-w20="{nd_prev}"'
                      f' data-hist-ipm-w21="{ipm_curr}" data-hist-ipm-w20="{ipm_prev}"'
                      f' data-hist-label="{lbl}"')
        tbl_attr = f' data-lbl="{lbl} {r.get("CorpName","")}"' if sb_id else ''
        if i < 5: hidden = ''
        elif i < 10: hidden = ' rows-more'
        else: hidden = ' sb-hidden'
        rows += (f'<div{hist_attrs}{tbl_attr} class="{hidden.strip()}" data-row-idx="{i}"'
                 f' style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;'
                 f'padding:7px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                 f'{row_cells}</div>')
    # Botón Ver 5 más si hay filas rows-more
    if len(df) > 5:
        rows += (f'<button class="rows-toggle" '
                 f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                 f'font-size:10px;font-weight:600;color:{accent_color};letter-spacing:.04em;'
                 f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                 f'<span class="toggle-label">Ver 5 más</span> '
                 f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
    return rows

def render_demanda_nc():
    df1 = TOP['demanda_nc']
    df2 = TOP['demanda_nc_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'dnc','label':'Pérdidas','width':'80px','fmt':lambda r:fmt_big(r['DemandaNoConvertida'])},
    ]
    col1 = render_top_table('','',df1,cols)
    # ajustar índices del df2
    
    return f'''<section id="demanda-nc" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 04</div>
<h2 class="section-title">🔍 Demanda no convertida</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · ordenado por búsquedas perdidas ↓</span>
<p class="section-kicker">Hoteles con mayor volumen absoluto de búsquedas que se perdieron por NoDispo. Combina tráfico × %NoDispo. Top 1: <strong>{truncate(df1.iloc[0]["Hotel"],38)}</strong> ({fmt_big(df1.iloc[0]["DemandaNoConvertida"])} búsquedas perdidas).</p>
</div>
</div>
<div>{col1}</div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Demanda No Convertida</strong> está en la pestaña <em>«Demanda No Convertida»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_bajo_rend():
    df1 = TOP['bajo_rend']
    df2 = TOP['bajo_rend_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'bk','label':'BKGS','width':'55px','fmt':lambda r:fmt_int_es(r['Bookings'])},
        {'key':'rpm','label':'IPM','width':'70px','fmt':lambda r:fmt_num2(r['RPM'])},
    ]
    import pandas as _pd; df_all = _pd.concat([df1, df2]).reset_index(drop=True)
    col1 = render_top_table('','',df_all,cols)
    
    return f'''<section id="bajo-rendimiento" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 05</div>
<h2 class="section-title">📉 Bajo rendimiento</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · alto tráfico · IPM Crítica/Revisar · ordenado por tráfico ↓</span>
<p class="section-kicker">Hoteles del P80 con bookings &gt; 0 pero IPM en banda Crítica/Revisar — están convirtiendo, pero el income por millón de búsquedas no llega al target ≥ $650.</p>
</div>
</div>
<div>{col1}</div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Bajo Rendimiento</strong> está en la pestaña <em>«Bajo Rendimiento»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_no_convierten():
    df1 = TOP['sin_conv']
    df2 = TOP['sin_conv_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'dest','label':'Destino','width':'120px','fmt':lambda r:truncate(r['Destino'],18)},
    ]
    import pandas as _pd; df_all = _pd.concat([df1, df2]).reset_index(drop=True)
    col1 = render_top_table('','',df_all,cols) if len(df2)>0 else ''
    n_total_sc = (p80_hotel['Bookings']==0).sum()
    
    body = f'<div>{col1}</div>'
    
    return f'''<section id="sin-conversion" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 06</div>
<h2 class="section-title">⭕ Sin conversión</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · alto tráfico · 0 BKGS · ordenado por tráfico ↓</span>
<p class="section-kicker">{fmt_int_es(n_total_sc)} hoteles del P80 con cero bookings. Cohorte estructural: requiere diagnóstico técnico (errores de carga, mapping) o contractual (paridad, tarifas). No incluye en Severity de Conv Rate.</p>
</div>
</div>
{body}
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Sin Conversión</strong> está en la pestaña <em>«Sin Conversión»</em> del Excel adjunto · separada de Bajo Rendimiento.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def _render_dim_table_rnd(df, dim_col, dim_label, start_idx=0, sb_id=None):
    """Tabla RND: 100 filas, 10 visibles, resto sb-hidden. Badges paleta D. 11px.
    sb_id: si se pasa, primera columna del header es searchbox integrado (Prop D).
    Badge de banda: BandaNoDispo en todas las dimensiones (Corp, Destino, País).
    """
    import math
    RND_ACCENT = '#EA0074'
    grid = '1fr 62px 36px 58px 36px'
    headers = [dim_label, '%NoDispo', 'WoW', 'IPM', 'WoW']

    # Header con o sin searchbox
    hrow = f'<div style="display:grid;grid-template-columns:{grid};gap:8px;padding:0;border-bottom:2px solid {RND_ACCENT};margin-bottom:2px;">'
    for idx_h, h in enumerate(headers):
        if idx_h == 0 and sb_id:
            hrow += searchbox_header_html(sb_id, accent_color=RND_ACCENT,
                                           placeholder=f'{dim_label}…',
                                           th_id=f'th-{sb_id}')
        else:
            align = 'left' if h == dim_label else 'right'
            color = RND_ACCENT if h == dim_label else 'var(--ink-muted)'
            hrow += f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{color};text-align:{align};padding:9px 0;">{h}</span>'
    hrow += '</div>'
    rows = hrow

    for i, r in df.iterrows():
        row_idx = start_idx + i
        bnd = r.get('BandaNoDispo', '')
        bc_bnd = BANDA_COLORS.get(bnd, BANDA_COLORS['Sin Conversión'])
        pill = (f'<span style="display:inline-block;font-size:8px;font-weight:700;padding:1px 5px;border-radius:2px;'
                f'background:{bc_bnd["bg"]};color:{bc_bnd["fg"]};text-transform:uppercase;letter-spacing:.04em;margin-left:4px;flex-shrink:0;">{bnd}</span>')
        if dim_col == 'PaisDestino': raw_label = clean_pais_name(r[dim_col])
        elif dim_col == 'Destino': raw_label = clean_destino_name(r[dim_col], 26)
        elif dim_col == 'CorpName': raw_label = clean_corp_name(r[dim_col])
        else: raw_label = r[dim_col]
        ipm_val = max(r.get('IPM', r.get('RPM', 0)), 0)
        
        def _wow_pill(v, invert=False, pct_base=None, is_pct_val=True):
            if v is None or (isinstance(v,float) and (math.isnan(v) or math.isinf(v))):
                return '<em class="wow-pill nd">—</em>'
            val = (v / pct_base * 100) if (pct_base and pct_base > 0 and not is_pct_val) else v
            if abs(val) < 0.05: return '<em class="wow-pill nd">—</em>'
            mejora = (val < 0) if invert else (val > 0)
            cls = 'dn' if mejora else 'up'
            arrow = '↓' if val < 0 else '↑'
            txt = f'{arrow}{abs(val):.1f}%'.replace('.', ',')
            return f'<em class="wow-pill {cls}">{txt}</em>'

        wow_nd  = _wow_pill(r.get('NoDispo_WoW_pp'), invert=True, is_pct_val=True)
        ipm_base = r.get('IPM_W18', 0)
        wow_ipm = _wow_pill(r.get('IPM_WoW_pp'), invert=False, pct_base=ipm_base, is_pct_val=False)

        cells = (f'<div style="display:flex;align-items:center;gap:2px;overflow:hidden;">'
                 f'<span style="font-size:11px;font-weight:600;color:{RND_ACCENT};overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row_idx+1}. {truncate(raw_label,26)}</span>{pill}</div>'
                 f'<span style="text-align:right;font-size:11px;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_pct2(r["%NoDispo"])}</span>'
                 f'<span style="text-align:right;">{wow_nd}</span>'
                 f'<span style="text-align:right;font-size:11px;color:var(--ink);font-variant-numeric:tabular-nums;">${fmt_num2(ipm_val)}</span>'
                 f'<span style="text-align:right;">{wow_ipm}</span>')
        nd_curr  = round(float(r.get('%NoDispo', 0)) * 100, 4)
        nd_prev  = round(float(r.get('NoDispo_W18', nd_curr/100)*100 if '%NoDispo' in r.index else nd_curr), 4)
        ipm_curr = round(max(ipm_val, 0), 1)
        ipm_prev = round(max(float(r.get('IPM_W18', ipm_curr)), 0), 1)
        hist_attrs = (f' data-hist-w21="{nd_curr}" data-hist-w20="{nd_prev}"'
                      f' data-hist-ipm-w21="{ipm_curr}" data-hist-ipm-w20="{ipm_prev}"'
                      f' data-hist-label="{truncate(raw_label, 28)}"')
        tbl_attr = f' data-lbl="{raw_label}"' if sb_id else ''
        if row_idx < 5: hidden = ''
        elif row_idx < 10: hidden = ' rows-more'
        else: hidden = ' sb-hidden'
        rows += (f'<div{hist_attrs}{tbl_attr} class="{hidden.strip()}" data-row-idx="{row_idx}"'
                 f' style="display:grid;grid-template-columns:{grid};gap:8px;align-items:center;'
                 f'padding:7px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                 f'{cells}</div>')
    # Botón Ver 5 más si hay filas rows-more
    if len(df) > 5:
        rows += (f'<button class="rows-toggle" '
                 f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                 f'font-size:10px;font-weight:600;color:#EA0074;letter-spacing:.04em;'
                 f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                 f'<span class="toggle-label">Ver 5 más</span> '
                 f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
    return rows

def render_top_dimension(num, title, df_full, dim_col, dim_label, kicker, key='hotel'):
    """Top 10 a 1 columna con Ver 5 más por destino/corp/país RND."""
    df_top10 = df_full.head(10).reset_index(drop=True)
    
    col1 = _render_dim_table_rnd(df_top10, dim_col, dim_label, start_idx=0)
    body = f'<div>{col1}</div>'
    
    return f'''<section id="top-{key}" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección {num}</div>
<h2 class="section-title">{icon} {title}</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · ordenado por tráfico ↓</span>
<p class="section-kicker">{kicker}</p>
</div>
</div>
{body}
</section>
'''

# ============ SECCIÓN PLAN DE ACCIÓN ============
def render_plan_accion():
    # Datos de los top problemas
    h_sc = TOP['sin_conv'].iloc[0]
    h_dnc = TOP['demanda_nc'].iloc[0]
    h_br = TOP['bajo_rend'].iloc[0]
    
    n_sc = (p80_hotel['Bookings']==0).sum()
    n_critmas = sev_nd['Crítica'] + sev_nd['Súper Crítica']
    
    # Badge superior = ÁREA OWNER · cluster (QW/MP/ES) va abajo (Fix #8)
    cug_rpm_wow = (M[f"CUG (UOP)_w{WEEK_NUM_INT}"]["rpm"]/M[f"CUG (UOP)_w{WEEK_PREV_INT}"]["rpm"]-1)*100
    
    def action(owner, cluster, code, plazo, accion, metrica):
        cluster_class = {'Quick Win':'qw','Mid Priority':'mp','Estratégica':'es'}.get(cluster,'qw')
        return f'''<div class="action-row {cluster_class}">
<div class="action-owner-badge">{owner}</div>
<div class="accion">{accion}</div>
<div class="action-meta-bottom">
<span class="cluster-tag">{cluster} · {code}</span>
<span class="meta-item"><strong>Plazo</strong> {plazo}</span>
<span class="meta-item"><strong>Métrica</strong> {metrica}</span>
</div>
</div>'''
    
    rows = ''
    rows += action('Supply Comercial / Supply Optimization', 'Quick Win', 'QW1', '5 días',
                   f'Escalar los <strong>{int(sev_nd["Súper Crítica"])} hoteles Súper Críticos</strong> del P80 (%NoDispo &gt;60%) · empezar por <strong>{truncate(clean_hotel_name(h_dnc["Hotel"]),38)}</strong> y similares.',
                   '%NoDispo &lt; 20%')
    rows += action('Supply Optimization / TPS', 'Quick Win', 'QW2', '1 semana',
                   f'Diagnóstico técnico Top 10 <strong>Sin Conversión</strong> de alto tráfico · revisar mapping, paridad, tarifas. Empezar por <strong>{truncate(clean_hotel_name(h_sc["Hotel"]),38)}</strong> ({fmt_big(h_sc["Trafico"])} búsquedas).',
                   'Conv Rate &gt; 0')
    rows += action('Supply Optimization', 'Mid Priority', 'MP1', '3 semanas',
                   f'Plan de saneamiento para <strong>{fmt_int_es(n_critmas)} hoteles Crítica/Súper Crítica</strong> de %NoDispo · separar por canasta y trabajar primero CUG y B2B-OP (weight 0,6).',
                   f'{int(n_critmas*0.5)} migrados a Revisar')
    rows += action('Supply Comercial / Wholesale', 'Mid Priority', 'MP2', '2 semanas',
                   f'Revisión de IPM en <strong>CUG</strong> ({fmt_num2(M[f"CUG (UOP)_w{WEEK_NUM_INT}"]["rpm"])}, {cug_rpm_wow:+.1f}% WoW) · canasta de mayor weight con deterioro pronunciado en GB.'.replace('+,','+').replace('.', ',', 1),
                   'IPM &gt; 600')
    rows += action('Supply Comercial / Supply Optimization', 'Estratégica', 'ES1', 'Q3',
                   f'Reducir <strong>cohorte Sin Conversión</strong> en P80 ({fmt_int_es(n_sc)} hoteles, {n_sc/len(p80_hotel)*100:.0f}% del P80) · proyecto trimestral de remediación técnica + comercial.',
                   '-30% vs baseline')
    rows += action('Supply Comercial / Wholesale', 'Estratégica', 'ES2', 'Q3',
                   'Definir <strong>SLAs de %NoDispo por corporativo</strong> para Top 10 corp por tráfico · contratos con cláusulas de severity-based pricing.',
                   'SLAs firmados')
    rows += action('Supply Optimization', 'Quick Win', 'QW3', '1 semana',
                   f'Investigar si el %NoDispo de <strong>RIU ({fmt_pct2(TAB_NoDispo["corp"].iloc[0]["%NoDispo"] if "RIU" in TAB_NoDispo["corp"]["CorpName"].values else 0.191)})</strong> se debe a bloqueos de contrato y si el patrón es transversal en B2C · B2B-OP · CUG o concentrado en una canasta específica.',
                   '%NoDispo RIU &lt; 10%')
    rows += action('Supply Comercial / Supply Optimization', 'Mid Priority', 'MP3', '2 semanas',
                   '<strong>Deep Dive Iberostar</strong> · segundo corporativo con mayor %NoDispo · analizar causas (bloqueos, tarifas, paridad) y definir plan de saneamiento por canasta con Supply Comercial.',
                   '%NoDispo Iberostar &lt; 5%')
    rows += action('Wholesale', 'Estratégica', 'ES3', 'Q3',
                   'Resolver la forma en que <strong>Wholesale sirve hoteles a las agencias</strong> para evitar que consulten hoteles y/o contratos no disponibles para cotizar · reducir tráfico inválido estructural.',
                   'Tráfico inválido &lt; 15%')
    rows += action('Wholesale', 'Estratégica', 'ES4', 'Q3',
                   'Identificar y separar el <strong>tráfico de bots del tráfico orgánico</strong> generado por agencias · con foco en canasta B2C que concentra mayor ruido en métricas de %NoDispo e IPM.',
                   'Bots identificados y filtrados')
    
    seguimiento_html = render_seguimiento_block(SEGUIMIENTO_FILE, accent_color='#EA0074')

    return f'''<section id="plan-accion">
<div class="section-head">
<div>
<div class="section-num">Sección 10</div>
<h2 class="section-title">📋 Plan de acción</h2>
<span class="section-subtitle" style="color:#EA0074">Acciones priorizadas · agrupadas por Área Accountable</span>
<p class="section-kicker">El badge superior identifica al Área Accountable de cada acción. La etiqueta de horizonte (Quick Win · Mid Priority · Estratégica) y el código de seguimiento van debajo.</p>
</div>
</div>
<div class="action-grid">{rows}</div>
{seguimiento_html}
</section>
'''

def render_historico_seccion_rnd(canvas_id_nd, canvas_id_ipm,
                                  banda_nd, val_nd,
                                  banda_ipm, val_ipm,
                                  current_week='W20'):
    """
    Módulo histórico doble (NoDispo + IPM) para secciones de análisis.
    Un módulo por sección — se actualiza al clickear cualquier fila de la tabla.
    canvas_id_nd  : ej. 'hrnd-hotel-nd'
    canvas_id_ipm : ej. 'hrnd-hotel-ipm'
    """
    html_nd  = render_historico_rnd('nodispo', banda_nd,  val_nd,  canvas_id_nd,  current_week)
    html_ipm = render_historico_rnd('ipm',     banda_ipm, val_ipm, canvas_id_ipm, current_week)

    # Wrapper con JS que conecta clicks de filas con data-hist-* al módulo
    js = f"""
<script>
(function() {{
  var section = document.getElementById('hist-{canvas_id_nd}-container') ||
                document.getElementById('hist-{canvas_id_ipm}-container');
  if (!section) return;
  var parent = section.closest('section') || document.body;

  function resetToGlobal() {{
    parent.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
      r.style.background = ''; r.removeAttribute('data-selected-hist');
    }});
    // Disparar reset en ambos módulos históricos
    var evND  = new CustomEvent('hist-reset', {{detail: {{cid: '{canvas_id_nd}'}}}});
    var evIPM = new CustomEvent('hist-reset', {{detail: {{cid: '{canvas_id_ipm}'}}}});
    document.dispatchEvent(evND);
    document.dispatchEvent(evIPM);
  }}

  parent.addEventListener('click', function(e) {{
    // Click en label Global de cualquiera de los dos módulos
    if (e.target.id === 'hist-{canvas_id_nd}-label' ||
        e.target.id === 'hist-{canvas_id_ipm}-label') {{
      resetToGlobal(); return;
    }}
    var row = e.target.closest('[data-hist-w21]');
    if (!row) return;
    if (row.getAttribute('data-selected-hist') === '1') {{ resetToGlobal(); return; }}

    var nd_curr  = parseFloat(row.getAttribute('data-hist-w21'));
    var nd_prev  = parseFloat(row.getAttribute('data-hist-w20') || nd_curr);
    var ipm_curr = parseFloat(row.getAttribute('data-hist-ipm-w21'));
    var ipm_prev = parseFloat(row.getAttribute('data-hist-ipm-w20') || ipm_curr);
    var lbl = row.getAttribute('data-hist-label') || '';

    parent.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
      r.style.background = ''; r.removeAttribute('data-selected-hist');
    }});
    row.setAttribute('data-selected-hist', '1');
    row.style.background = 'var(--accent-soft)';

    // Emitir eventos para que cada módulo actualice su canvas
    document.dispatchEvent(new CustomEvent('hist-update', {{detail: {{
      cid: '{canvas_id_nd}', w_curr: nd_curr, w_prev: nd_prev, label: lbl
    }}}}));
    document.dispatchEvent(new CustomEvent('hist-update', {{detail: {{
      cid: '{canvas_id_ipm}', w_curr: ipm_curr, w_prev: ipm_prev, label: lbl
    }}}}));
  }});
}})();
</script>"""

    return f'''<div id="hist-{canvas_id_nd}-container"
     style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px;margin-bottom:8px;">
  <div>{html_nd}</div>
  <div>{html_ipm}</div>
</div>{js}'''


# ============ NUEVO · BLOQUES CON TABS (post Week 18 mejora) ============
def _render_panel_top_table(df, cols, idx_offset=0, sb_id=None):
    """Panel: top 5 visible, filas 6-10 rows-more, filas 11-100 sb-hidden.
    Todas las filas llevan data-lbl para que attachTable las encuentre y pueda
    buscar sobre el pool completo de 100.
    sb_id: si se pasa, header integra searchbox_header_html (Prop D).
    """
    df = df.reset_index(drop=True)
    # Una sola llamada con todo el df: render_top_table asigna clases sb-hidden/rows-more
    # y genera data-lbl para TODAS las filas cuando recibe sb_id
    full_table = render_top_table('', '', df, cols, sb_id=sb_id)
    return f'<div class="tbl-wrap">{full_table}</div>'

def render_bloque_hoteles():
    """Sección 03 · 3 tabs: Demanda No Convertida · Bajo Rend · Sin Conv."""
    # Demanda No Convertida
    def _fmt_wow_rnd(v, mejora_si_negativo=False):
        """Pill WoW para RND: verde si baja %NoDispo, rojo si sube."""
        import math
        if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
            return '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
        if abs(v) < 0.05:
            return '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'
        # Para %NoDispo: bajar es bueno (verde si negativo)
        # Para IPM: subir es bueno (verde si positivo)
        if mejora_si_negativo:
            mejora = v < 0
        else:
            mejora = v > 0
        wc = '#2F6C34' if mejora else '#C0392B'
        wb = '#EAF3DE' if mejora else '#FCE8E6'
        arrow = '↓' if v < 0 else '↑'
        txt = f'{arrow}{abs(v):.2f}'.replace('.', ',')
        return f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{wb};color:{wc};">{txt}</em>'

    cols_dnc = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'wow','label':'WoW','width':'50px','fmt':lambda r:_fmt_wow_rnd(r.get('NoDispo_WoW_pp'), mejora_si_negativo=True)},
    ]
    df_dnc = TOP['demanda_nc'].reset_index(drop=True)
    panel_dnc = _render_panel_top_table(df_dnc, cols_dnc, sb_id='sb-rh-dnc')
    top1_dnc = df_dnc.iloc[0]
    kicker_dnc = f'Hoteles con mayor volumen absoluto de búsquedas que se perdieron por NoDispo. Combina tráfico × %NoDispo. Top 1: <strong>{truncate(top1_dnc["Hotel"],38)}</strong> ({fmt_big(top1_dnc["DemandaNoConvertida"])} búsquedas perdidas).'
    
    # Bajo Rendimiento
    cols_br = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'rpm','label':'IPM','width':'70px','fmt':lambda r:fmt_num2(max(r.get('RPM',r.get('IPM',0)),0))},
        {'key':'wow','label':'WoW','width':'50px','fmt':lambda r:_fmt_wow_rnd((r['IPM_WoW_pp']/r['IPM_W18']*100) if r.get('IPM_WoW_pp') is not None and r.get('IPM_W18',0)>0 else None, mejora_si_negativo=False)},
    ]
    df_br = TOP['bajo_rend'].reset_index(drop=True)
    panel_br = _render_panel_top_table(df_br, cols_br, sb_id='sb-rh-br')
    kicker_br = 'Hoteles del P80 con bookings &gt; 0 pero IPM en banda Crítica/Revisar — están convirtiendo, pero el income por millón de búsquedas no llega al target ≥ $650.'
    
    # Sin Conversión
    cols_sc = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'wow','label':'WoW','width':'50px','fmt':lambda r:_fmt_wow_rnd(r.get('NoDispo_WoW_pp'), mejora_si_negativo=True)},
    ]
    df_sc = TOP['sin_conv'].reset_index(drop=True)
    panel_sc = _render_panel_top_table(df_sc, cols_sc, sb_id='sb-rh-sc')
    n_total_sc = (p80_hotel['Bookings']==0).sum()
    kicker_sc = f'{fmt_int_es(n_total_sc)} hoteles del P80 con cero bookings. Cohorte estructural: requiere diagnóstico técnico (errores de carga, mapping) o contractual (paridad, tarifas). No incluye en Severity de IPM.'
    
    # Críticos: hoteles con BandaNoDispo en Crítica o Súper Crítica (>20% NoDispo)
    cols_crit = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'wow','label':'WoW','width':'50px','fmt':lambda r:_fmt_wow_rnd(r.get('NoDispo_WoW_pp'), mejora_si_negativo=True)},
    ]
    df_crit_all = p80_hotel[p80_hotel['BandaNoDispo'].isin(['Crítica','Súper Crítica'])].sort_values('%NoDispo', ascending=False).reset_index(drop=True)
    df_crit = df_crit_all.head(100).reset_index(drop=True)
    df_crit.index = range(len(df_crit))
    panel_crit = _render_panel_top_table(df_crit, cols_crit, sb_id='sb-rh-crit')
    n_crit_total = len(df_crit_all)
    n_supcrit = (p80_hotel['BandaNoDispo'] == 'Súper Crítica').sum()
    kicker_crit = f'{fmt_int_es(n_crit_total)} hoteles del P80 con %NoDispo &gt; 20% (banda Crítica+). De estos, <strong>{n_supcrit} son Súper Críticos</strong> (&gt; 60%) — primer foco de escalamiento inmediato a Supply.'
    
    panels = (
        f'<div class="tab-panel" data-tab="crit"><p class="tab-kicker">{kicker_crit}</p>{panel_crit}</div>'
        f'<div class="tab-panel" data-tab="dnc"><p class="tab-kicker">{kicker_dnc}</p>{panel_dnc}</div>'
        f'<div class="tab-panel" data-tab="br"><p class="tab-kicker">{kicker_br}</p>{panel_br}</div>'
        f'<div class="tab-panel" data-tab="sc"><p class="tab-kicker">{kicker_sc}</p>{panel_sc}</div>'
    )
    
    hist_hotel = render_historico_seccion_rnd(
        canvas_id_nd  = 'hrnd-hotel-nd',
        canvas_id_ipm = 'hrnd-hotel-ipm',
        banda_nd  = banda_nodispo(M['global_current']['pct_nodispo']),
        val_nd    = M['global_current']['pct_nodispo'],
        banda_ipm = banda_rpm(M['global_current']['rpm'], M['global_current']['bookings']),
        val_ipm   = M['global_current']['rpm'],
        current_week = f"W{WEEK_NUM_INT}",
    )

    return f'''<section id="por-hotel" style="margin-bottom:64px;">
<div class="section-head">
<div>
<div class="section-num">Sección 03</div>
<h2 class="section-title">🏨 Análisis por hotel</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · 4 ópticas analíticas</span>
<p class="section-kicker">Hoteles del P80 vistos desde tres ángulos: demanda no convertida, bajo rendimiento de IPM, y sin conversión. Cada óptica responde a un tipo distinto de fuga de revenue.</p>
</div>
</div>
<div class="tabs-block">
<input checked id="tab-h-crit" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-dnc" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-br" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-sc" name="tabs-h" style="display:none" type="radio"/>
<div class="tabs-row" style="align-items:flex-end;">
<label class="tab-label" for="tab-h-crit">Críticos</label>
<label class="tab-label" for="tab-h-dnc">Demanda No Convertida</label>
<label class="tab-label" for="tab-h-br">Bajo Rendimiento</label>
<label class="tab-label" for="tab-h-sc">Sin Conversión</label>
</div>
<div class="tab-panels">{panels}</div>
</div>
{hist_hotel}
<div class="detail-callout" style="margin-top:18px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de cada óptica (Demanda No Convertida · Bajo Rendimiento · Sin Conversión) está en pestañas separadas del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_bloque_dimensiones():
    """Sección 04 · 3 tabs: Corporativo · Destino · País."""
    
    def panel_for_dim(df_full, dim_col, dim_label, sb_id=None):
        df100 = df_full.head(100).reset_index(drop=True)
        rows_html = _render_dim_table_rnd(df100, dim_col, dim_label, start_idx=0, sb_id=sb_id)
        return f'<div class="tbl-wrap">{rows_html}</div>'
    
    panel_corp = panel_for_dim(TOP['corps_10'], 'CorpName', 'Corporativo', sb_id='sb-rd-corp')
    panel_dest = panel_for_dim(TOP['destinos_10'], 'Destino', 'Destino', sb_id='sb-rd-dest')
    panel_pais = panel_for_dim(TOP['paises_10'], 'PaisDestino', 'País', sb_id='sb-rd-pais')
    
    # Kickers
    top_corp = TOP['corps'].iloc[0]
    top_dest = TOP['destinos'].iloc[0]
    top_pais = TOP['paises'].iloc[0]
    k_corp = f'Distribución por corporativo. <strong>{top_corp["CorpName"]}</strong> lidera tráfico ({fmt_big(top_corp["Trafico"])}) con %NoDispo {fmt_pct2(top_corp["%NoDispo"])} y IPM ${fmt_num2(top_corp["RPM"])}.'
    k_dest = f'Distribución por destino. <strong>{top_dest["Destino"]}</strong> concentra {fmt_big(top_dest["Trafico"])} en búsquedas con %NoDispo {fmt_pct2(top_dest["%NoDispo"])} (banda {top_dest["BandaNoDispo"]}).'
    k_pais = f'Distribución por país. <strong>{clean_pais_name(top_pais["PaisDestino"], max_len=50)}</strong> concentra {fmt_big(top_pais["Trafico"])} de búsquedas con %NoDispo {fmt_pct2(top_pais["%NoDispo"])}.'
    
    panels = (
        f'<div class="tab-panel" data-tab="corp"><p class="tab-kicker">{k_corp}</p>{panel_corp}</div>'
        f'<div class="tab-panel" data-tab="dest"><p class="tab-kicker">{k_dest}</p>{panel_dest}</div>'
        f'<div class="tab-panel" data-tab="pais"><p class="tab-kicker">{k_pais}</p>{panel_pais}</div>'
    )
    
    hist_dim = render_historico_seccion_rnd(
        canvas_id_nd  = 'hrnd-dim-nd',
        canvas_id_ipm = 'hrnd-dim-ipm',
        banda_nd  = banda_nodispo(M['global_current']['pct_nodispo']),
        val_nd    = M['global_current']['pct_nodispo'],
        banda_ipm = banda_rpm(M['global_current']['rpm'], M['global_current']['bookings']),
        val_ipm   = M['global_current']['rpm'],
        current_week = f"W{WEEK_NUM_INT}",
    )

    return f'''<section id="por-dimension" style="margin-bottom:64px;">
<div class="section-head">
<div>
<div class="section-num">Sección 04</div>
<h2 class="section-title">📊 Análisis por dimensión</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 agregados · ordenado por tráfico ↓</span>
<p class="section-kicker">Distribución del tráfico P80 por corporativo, destino y país. Identifica concentraciones de demanda y patrones por dimensión geográfica.</p>
</div>
</div>
<div class="tabs-block">
<input checked id="tab-d-corp" name="tabs-d" style="display:none" type="radio"/>
<input id="tab-d-dest" name="tabs-d" style="display:none" type="radio"/>
<input id="tab-d-pais" name="tabs-d" style="display:none" type="radio"/>
<div class="tabs-row" style="align-items:flex-end;">
<label class="tab-label" for="tab-d-corp">Corporativo</label>
<label class="tab-label" for="tab-d-dest">Destino</label>
<label class="tab-label" for="tab-d-pais">País</label>
</div>
<div class="tab-panels">{panels}</div>
</div>
{hist_dim}
</section>
'''

# Render parte 2 completa
RESUMEN = render_resumen_ej()
SEV_COMBINADA = render_severities_combinadas()

# === NUEVO · 2 bloques con tabs (reemplazan 6 secciones apiladas) ===
BLOQUE_HOTELES = render_bloque_hoteles()
BLOQUE_DIM = render_bloque_dimensiones()

PLAN_ACCION = render_plan_accion()

PART2 = RESUMEN + SEV_COMBINADA + BLOQUE_HOTELES + BLOQUE_DIM + PLAN_ACCION

with open('part2_rnd.html','w') as f:
    f.write(PART2)
print(f"Part 2 RND escrito: {len(PART2):,} chars")
