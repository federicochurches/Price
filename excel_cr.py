"""
excel_cr.py · W21+ · 44 hojas (11 × 4 canastas)
Por canasta: Severity | Top Destinos | Top Corp | Hot Críticos | Hot Bajo Rend |
             Hot Sin Conv | Hot Menor CV | Channel | Dim Corp | Dim Dest | (WoW KPIs en Severity)
"""
import pickle, os, re
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from engine import banda_eficacia, banda_convrate

VOL_NUM = os.getenv('VOL_NUM', '21')
PERIODO = os.getenv('PERIODO', '19-25 mayo 2026')
OUTPUTS = os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs')

with open(os.getenv('PICKLE_CR', f'cr_w{VOL_NUM}_data.pkl'), 'rb') as f:
    D = pickle.load(f)

CANASTA  = D['CANASTA']
TAB_EF   = D['TAB_EF_BY_CANASTA']
TAB_CV   = D['TAB_CV_BY_CANASTA']
M        = D['M']
p80_all  = D['p80_hotel'].copy()
hcm      = D.get('hotel_channel_map', {})

def clean(n):
    return re.sub(r'^\(\d+\)\s*-\s*', '', str(n)).strip() if n else str(n)

hcm_clean = {clean(k): v for k, v in hcm.items()}
p80_all['Hotel']   = p80_all['Hotel'].apply(clean)
p80_all['Channel'] = p80_all['Hotel'].map(hcm_clean).fillna('—')

# ── Estilos ───────────────────────────────────────────────────────────────────
CR = '5C469C'
def fill(c): return PatternFill(start_color=c, end_color=c, fill_type='solid')
def fnt(c='000000', sz=10, bold=False, white=False):
    return Font(name='Arial', size=sz, bold=bold, color='FFFFFF' if white else c)
T  = Side(border_style='thin', color='CCCCCC')
BD = Border(left=T, right=T, top=T, bottom=T)

BFILL = {
    'Exitosa':       fill('E1F5EE'), 'Aceptable':     fill('FEF9C3'),
    'Revisar':       fill('FED7AA'), 'Crítica':        fill('FCE4F1'),
    'Súper Crítica': fill('E8E6E3'), 'Sin Conversión': fill('F2EEE6'),
}
BFONT = {
    'Exitosa':       fnt('1A6B4A',bold=True), 'Aceptable':     fnt('713F12',bold=True),
    'Revisar':       fnt('C2410C',bold=True), 'Crítica':        fnt('99162B',bold=True),
    'Súper Crítica': fnt('2D2828',bold=True), 'Sin Conversión': fnt('5F5E5A',bold=True),
}
# WoW pills — verde si positivo Eficacia (más alto = mejor), rojo si negativo
WOW_UP   = fill('EAF3DE');  WOW_UP_F   = fnt('2F6C34', bold=True)
WOW_DN   = fill('FCE8E6');  WOW_DN_F   = fnt('C0392B', bold=True)
WOW_NEU  = fill('F2EEE6');  WOW_NEU_F  = fnt('8A8377', bold=True)

def apply_wow(ws, row, col, val_pp, invert=False):
    """Colorea celda WoW: verde=mejora, rojo=empeora. invert=True para métricas donde subir es malo."""
    cell = ws.cell(row, col)
    if val_pp is None or (isinstance(val_pp, float) and pd.isna(val_pp)):
        cell.value = '—'; cell.font = WOW_NEU_F; cell.fill = WOW_NEU; cell.border = BD; return
    is_up = float(val_pp) >= 0
    is_good = (is_up and not invert) or (not is_up and invert)
    s = '▲' if is_up else '▼'
    cell.value = f'{s}{abs(round(float(val_pp),2))}'.replace('.', ',')
    cell.fill  = WOW_UP if is_good else WOW_DN
    cell.font  = WOW_UP_F if is_good else WOW_DN_F
    cell.border = BD
    cell.alignment = Alignment(horizontal='center')

def title(ws, t, sub=''):
    ws.cell(1,1,t).font = fnt(CR, 13, True)
    if sub: ws.cell(2,1,sub).font = fnt('666666')

def mk_hdr(ws, row, cols):
    for c, lbl in enumerate(cols, 1):
        cell = ws.cell(row, c, lbl)
        cell.font = fnt(white=True, bold=True); cell.fill = fill(CR)
        cell.alignment = Alignment(horizontal='center'); cell.border = BD
    ws.auto_filter.ref = f'A{row}:{get_column_letter(len(cols))}{row}'
    return row + 1

def mk_cell(ws, row, col, val, banda=None, is_sev=False, align='center'):
    cell = ws.cell(row, col, val)
    cell.font = Font(name='Arial', size=10)
    cell.border = BD
    cell.alignment = Alignment(horizontal=align)
    if is_sev and banda and banda in BFILL:
        cell.fill = BFILL[banda]; cell.font = BFONT[banda]

def fmt_pct(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    return round(float(v), 4)

def fmt_wow_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    return float(v)

def autofit(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ── Severity con WoW de KPIs globales ────────────────────────────────────────
def write_severity(ws, df, can_label, m_curr, m_prev):
    title(ws, f'{can_label} · Severity CheckRates W{VOL_NUM}', f'W{VOL_NUM} · {PERIODO}')

    # WoW KPIs globales
    ef_curr = m_curr.get('eficacia', 0); ef_prev = m_prev.get('eficacia', 0)
    cv_curr = m_curr.get('conv_rate', 0); cv_prev = m_prev.get('conv_rate', 0)
    ef_wow  = (ef_curr - ef_prev) * 100 if ef_prev else None
    cv_wow  = (cv_curr - cv_prev) * 100 if cv_prev else None

    r = 4
    ws.cell(r, 1, 'KPI Global').font = fnt(CR, 11, True); r+=1
    r = mk_hdr(ws, r, ['Métrica', f'W{int(VOL_NUM)-1}', f'W{VOL_NUM}', 'WoW'])
    for label, prev, curr, wow, inv in [
        ('Eficacia', ef_prev, ef_curr, ef_wow, False),
        ('Conv Rate', cv_prev, cv_curr, cv_wow, False),
    ]:
        ws.cell(r, 1, label).font = Font(name='Arial', size=10, bold=True); ws.cell(r,1).border=BD
        ws.cell(r, 2, round(prev,4) if prev else None).border=BD
        ws.cell(r, 3, round(curr,4) if curr else None).border=BD
        ws.cell(r, 2).number_format='0.00%'; ws.cell(r,3).number_format='0.00%'
        ws.cell(r, 2).alignment=Alignment(horizontal='center')
        ws.cell(r, 3).alignment=Alignment(horizontal='center')
        apply_wow(ws, r, 4, wow, invert=inv)
        r += 1

    r += 1
    # Severity tables
    sev_ef, sev_cv = {}, {}
    for _, row in df.iterrows():
        ef = fmt_pct(row.get('Eficacia'))
        cv = fmt_pct(row.get('ConvRate'))
        bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
        if ef is not None: b=banda_eficacia(ef); sev_ef[b]=sev_ef.get(b,0)+1
        if cv is not None: b=banda_convrate(cv,bk); sev_cv[b]=sev_cv.get(b,0)+1

    for label, sev, orden in [
        ('Severity Eficacia', sev_ef, ['Exitosa','Aceptable','Revisar','Crítica','Súper Crítica']),
        ('Severity Conv Rate', sev_cv, ['Exitosa','Aceptable','Revisar','Crítica','Sin Conversión']),
    ]:
        ws.cell(r,1,label).font=fnt(CR,11,True); r+=1
        r=mk_hdr(ws, r, ['Severity','Hoteles','% del Total'])
        total=sum(sev.values()) or 1
        for b in orden:
            n=sev.get(b,0)
            mk_cell(ws, r, 1, b, b, is_sev=True, align='center')
            ws.cell(r,1).border=BD
            ws.cell(r,2,n).border=BD; ws.cell(r,2).alignment=Alignment(horizontal='center')
            ws.cell(r,3,round(n/total,4)).number_format='0.0%'; ws.cell(r,3).border=BD
            ws.cell(r,3).alignment=Alignment(horizontal='center')
            r+=1
        r+=1
    autofit(ws,[20,12,12,12])

# ── Tabla combinada EF+CV ─────────────────────────────────────────────────────
COLS_COMBINED = ['Nombre','Sev Eficacia','Sev Conv Rate','CR Únicos','Bookings',
                 'Eficacia','WoW Ef','Conv Rate','WoW CV']

def write_combined(ws, df_ef, df_name_col, title_str, extra_cols=None):
    """Top 100 ordenado por Eficacia ASC con ambas métricas + severity coloreada."""
    title(ws, title_str, 'Ordenado por Eficacia ASC (peor primero) · Top 100')
    if df_ef is None or len(df_ef)==0: ws.cell(4,1,'Sin datos'); return
    df_s = df_ef.sort_values('Eficacia', ascending=True).head(100).copy()
    all_cols = COLS_COMBINED + (list(extra_cols.keys()) if extra_cols else [])
    r = mk_hdr(ws, 4, all_cols)
    for _, row in df_s.iterrows():
        ef = fmt_pct(row.get('Eficacia'))
        cv = fmt_pct(row.get('ConvRate'))
        bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
        cru= int(row.get('CR_Unicos',0)) if pd.notna(row.get('CR_Unicos',0)) else 0
        bef= banda_eficacia(ef) if ef is not None else '—'
        bcv= banda_convrate(cv,bk) if cv is not None else '—'
        wow_ef = fmt_wow_str(row.get('Eficacia_WoW_pp'))
        wow_cv = fmt_wow_str(row.get('ConvRate_WoW_pp'))

        # Nombre
        mk_cell(ws,r,1, clean(str(row.get(df_name_col,'—'))), align='left')
        # Severity EF (coloreada)
        mk_cell(ws,r,2, bef, bef, is_sev=True)
        # Severity CV (coloreada)
        mk_cell(ws,r,3, bcv, bcv, is_sev=True)
        # CR Únicos, Bookings
        mk_cell(ws,r,4, cru); mk_cell(ws,r,5, bk)
        # Eficacia
        c = ws.cell(r,6, ef); c.border=BD; c.alignment=Alignment(horizontal='center')
        if ef: ws.cell(r,6).number_format='0.00%'
        # WoW Eficacia (coloreada: subir Ef = bueno)
        apply_wow(ws,r,7, wow_ef, invert=False)
        # Conv Rate
        c2=ws.cell(r,8, cv); c2.border=BD; c2.alignment=Alignment(horizontal='center')
        if cv: ws.cell(r,8).number_format='0.00%'
        # WoW Conv Rate (coloreada: subir CV = bueno)
        apply_wow(ws,r,9, wow_cv, invert=False)
        # Extra cols (Channel, Destino, Corp)
        if extra_cols:
            for ci, col_name in enumerate(extra_cols.values(), 10):
                mk_cell(ws,r,ci, str(row.get(col_name,'—')), align='left')
        r += 1
    widths = [40,16,16,10,10,10,10,10,10]
    if extra_cols: widths += [15]*len(extra_cols)
    autofit(ws, widths)

# ── Channel unificado ─────────────────────────────────────────────────────────
def write_channel(ws, df_ef, df_cv, can_label):
    title(ws, f'{can_label} · Channel W{VOL_NUM}', 'Eficacia y Conv Rate por canal')
    if df_ef is None or len(df_ef)==0: ws.cell(4,1,'Sin datos'); return
    # Merge EF + CV
    df = df_ef.copy()
    if df_cv is not None and 'ConvRate_WoW_pp' in df_cv.columns:
        df = df.merge(df_cv[['ExternalProviderName','ConvRate_WoW_pp']], on='ExternalProviderName', how='left')
    df_s = df.sort_values('Eficacia', ascending=True)
    cols = ['Channel','Sev Eficacia','Sev Conv Rate','CR Únicos','Bookings',
            'Eficacia','WoW Ef','Conv Rate','WoW CV']
    r = mk_hdr(ws, 4, cols)
    for _, row in df_s.iterrows():
        ef = fmt_pct(row.get('Eficacia'))
        cv = fmt_pct(row.get('ConvRate'))
        bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
        cru= int(row.get('CR_Unicos',0)) if pd.notna(row.get('CR_Unicos',0)) else 0
        bef= banda_eficacia(ef) if ef is not None else '—'
        bcv= banda_convrate(cv,bk) if cv is not None else '—'
        chan = str(row.get('ExternalProviderName','—'))
        mk_cell(ws,r,1, chan, align='left')
        mk_cell(ws,r,2, bef, bef, is_sev=True)
        mk_cell(ws,r,3, bcv, bcv, is_sev=True)
        mk_cell(ws,r,4, cru); mk_cell(ws,r,5, bk)
        c=ws.cell(r,6,ef); c.border=BD; c.alignment=Alignment(horizontal='center')
        if ef: ws.cell(r,6).number_format='0.00%'
        apply_wow(ws,r,7, fmt_wow_str(row.get('Eficacia_WoW_pp')), invert=False)
        c2=ws.cell(r,8,cv); c2.border=BD; c2.alignment=Alignment(horizontal='center')
        if cv: ws.cell(r,8).number_format='0.00%'
        apply_wow(ws,r,9, fmt_wow_str(row.get('ConvRate_WoW_pp')), invert=False)
        r+=1
    autofit(ws,[22,16,16,10,10,10,10,10,10])

# ── Canastas ──────────────────────────────────────────────────────────────────
CANASTAS = [
    ('global', 'Global',     None,      'global',   'global_w21',    'global_w20'),
    ('b2c',    'B2C',        'B2C',     'B2C',      'B2C_w21',       'B2C_w20'),
    ('op',     'Opaco',      'B2B-OP',  'B2B-OP',   'B2B (OP)_w21', 'B2B (OP)_w20'),
    ('cug',    'Ultra Opaco','CUG',     'CUG',      'CUG (UOP)_w21','CUG (UOP)_w20'),
]

wb = Workbook(); wb.remove(wb.active)

for can_key, can_label, can_id, can_tab, m_curr_key, m_prev_key in CANASTAS:
    can    = CANASTA.get(can_id, CANASTA.get(can_key, {}))
    tab_ef = TAB_EF.get(can_key, TAB_EF.get('global',{}))
    tab_cv = TAB_CV.get(can_key, TAB_CV.get('global',{}))
    m_curr = M.get(m_curr_key, M.get(f'global_w{VOL_NUM}', {}))
    m_prev = M.get(m_prev_key, M.get(f'global_w{int(VOL_NUM)-1}', {}))
    px     = can_label[:3]

    # p80 con channel
    if can_id and 'DistributionCategory' in p80_all.columns:
        df_can = p80_all[p80_all['DistributionCategory']==can_id].copy()
    else:
        df_can = p80_all.copy()

    def add_ch(df):
        if df is None or len(df)==0: return df
        df2 = df.copy()
        if 'Channel' not in df2.columns and 'Hotel' in df2.columns:
            df2['Hotel_c'] = df2['Hotel'].apply(clean)
            df2['Channel'] = df2['Hotel_c'].map(hcm_clean).fillna('—')
        return df2

    # 1. Severity + WoW KPIs
    ws=wb.create_sheet(f'{px}-Severity'); ws.sheet_properties.tabColor=CR
    write_severity(ws, df_can, can_label, m_curr, m_prev)

    # 2. Top Destinos (EF+CV combinado)
    ws=wb.create_sheet(f'{px}-Destinos'); ws.sheet_properties.tabColor=CR
    write_combined(ws, tab_ef.get('destino'), 'Destino', f'{can_label} · Top Destinos W{VOL_NUM}')

    # 3. Top Corp
    ws=wb.create_sheet(f'{px}-Corp'); ws.sheet_properties.tabColor=CR
    write_combined(ws, tab_ef.get('corp'), 'CorpName', f'{can_label} · Top Corporativos W{VOL_NUM}')

    # 4-7. Hotel por categoría (EF+CV+Channel)
    extra = {'Channel':'Channel','Destino':'Destino','Corp':'CorpName'}
    cat_map = [
        ('top_crit','Hot Críticos',   'Críticos'),
        ('top_br',  'Hot Bajo Rend',  'Bajo Rendimiento'),
        ('top_sc',  'Hot Sin Conv',   'Sin Conversión'),
        ('top_mcv', 'Hot Menor CV',   'Menor Conv Rate'),
    ]
    for cat_key_h, tab_name, cat_label in cat_map:
        df_cat = can.get(cat_key_h, tab_ef.get('hotel'))
        df_cat = add_ch(df_cat)
        ws=wb.create_sheet(f'{px}-{tab_name}'); ws.sheet_properties.tabColor=CR
        write_combined(ws, df_cat, 'Hotel',
                       f'{can_label} · Hotel {cat_label} W{VOL_NUM}', extra_cols=extra)

    # 8. Channel unificado
    ws=wb.create_sheet(f'{px}-Channel'); ws.sheet_properties.tabColor=CR
    write_channel(ws, tab_ef.get('channel'), tab_cv.get('channel'), can_label)

    # 9. Dim Corp (EF+CV)
    ws=wb.create_sheet(f'{px}-Dim Corp'); ws.sheet_properties.tabColor=CR
    write_combined(ws, tab_ef.get('corp'), 'CorpName',
                   f'{can_label} · AR Dim Corporativo W{VOL_NUM}')

    # 10. Dim Destino (EF+CV)
    ws=wb.create_sheet(f'{px}-Dim Dest'); ws.sheet_properties.tabColor=CR
    write_combined(ws, tab_ef.get('destino'), 'Destino',
                   f'{can_label} · AR Dim Destino W{VOL_NUM}')

out = f'{OUTPUTS}/Analisis_CheckRates_W{VOL_NUM}.xlsx'
wb.save(out)
print(f'✅ Excel CR: {out}')
print(f'   {len(wb.sheetnames)} hojas: {" | ".join(wb.sheetnames[:11])}...')
