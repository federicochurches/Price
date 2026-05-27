"""
excel_cr.py · W21+ · Excel CheckRates estructura completa
Por canasta: Severity | Dest EF | Dest CV | Corp EF | Corp CV |
             Hotel Críticos | Hotel Bajo Rend | Hotel Sin Conv | Hotel Menor CV |
             Channel EF | Channel CV |
             Dim Corp EF | Dim Corp CV | Dim Dest EF | Dim Dest CV
"""
import pickle, os, re
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.filters import AutoFilter
from engine import banda_eficacia, banda_convrate

VOL_NUM = os.getenv('VOL_NUM', '21')
PERIODO = os.getenv('PERIODO', '19-25 mayo 2026')
OUTPUTS = os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs')

with open(os.getenv('PICKLE_CR', f'cr_w{VOL_NUM}_data.pkl'), 'rb') as f:
    D = pickle.load(f)

CANASTA  = D['CANASTA']
TAB_EF   = D['TAB_EF_BY_CANASTA']
TAB_CV   = D['TAB_CV_BY_CANASTA']
p80_all  = D['p80_hotel'].copy()
hcm      = D.get('hotel_channel_map', {})

def clean(n):
    return re.sub(r'^\(\d+\)\s*-\s*', '', str(n)).strip() if n else n

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

SEVA = 'Severity Eficacia'; SEVC = 'Severity Conv Rate'
BANDA_ORDER_EF = ['Exitosa','Aceptable','Revisar','Crítica','Súper Crítica']
BANDA_ORDER_CV = ['Exitosa','Aceptable','Revisar','Crítica','Sin Conversión']

def title(ws, t, sub=''):
    ws.cell(1,1, t).font = fnt(CR, 13, True)
    if sub: ws.cell(2,1, sub).font = fnt('666666')

def mk_hdr(ws, row, cols, ncols=None):
    """Escribe header con fondo violeta y activa autofilter."""
    for c, lbl in enumerate(cols, 1):
        cell = ws.cell(row, c, lbl)
        cell.font = fnt(white=True, bold=True)
        cell.fill = fill(CR)
        cell.alignment = Alignment(horizontal='center')
        cell.border = BD
    n = ncols or len(cols)
    ws.auto_filter.ref = f'A{row}:{get_column_letter(n)}{row}'
    return row + 1

def mk_row(ws, row, vals, sev_col=2, banda=None):
    for c, v in enumerate(vals, 1):
        cell = ws.cell(row, c, v)
        cell.font = Font(name='Arial', size=10)
        cell.border = BD
        cell.alignment = Alignment(horizontal='left' if c==1 else 'center')
    if banda and banda in BFILL:
        ws.cell(row, sev_col).fill = BFILL[banda]
        ws.cell(row, sev_col).font = BFONT[banda]

def fmt_pct(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return None
    return round(float(v), 4)

def fmt_pct_str(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return '—'
    return f'{float(v)*100:.2f}%'.replace('.',',')

def autofit(ws, col_widths):
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ── Severity ──────────────────────────────────────────────────────────────────
def write_severity(ws, df, can_label):
    title(ws, f'{can_label} · Severity CheckRates W{VOL_NUM}', f'W{VOL_NUM} · {PERIODO}')
    r = 4
    # Calcular severity desde df
    sev_ef, sev_cv = {}, {}
    for _, row in df.iterrows():
        ef = fmt_pct(row.get('Eficacia'))
        cv = fmt_pct(row.get('ConvRate'))
        bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
        if ef is not None: b = banda_eficacia(ef); sev_ef[b] = sev_ef.get(b,0)+1
        if cv is not None: b = banda_convrate(cv,bk); sev_cv[b] = sev_cv.get(b,0)+1
    # Severity Eficacia
    ws.cell(r,1,'Severity Eficacia').font = fnt(CR,11,True); r+=1
    r = mk_hdr(ws, r, ['Severity','Hoteles','% del Total'], 3)
    total = sum(sev_ef.values()) or 1
    for b in BANDA_ORDER_EF:
        n = sev_ef.get(b,0)
        mk_row(ws, r, [b, n, round(n/total,4)], 1, b)
        ws.cell(r,3).number_format='0.0%'; r+=1
    r+=1
    # Severity Conv Rate
    ws.cell(r,1,'Severity Conv Rate').font = fnt(CR,11,True); r+=1
    r = mk_hdr(ws, r, ['Severity','Hoteles','% del Total'], 3)
    total = sum(sev_cv.values()) or 1
    for b in BANDA_ORDER_CV:
        n = sev_cv.get(b,0)
        mk_row(ws, r, [b, n, round(n/total,4)], 1, b)
        ws.cell(r,3).number_format='0.0%'; r+=1
    autofit(ws,[20,12,12])

# ── Top 100 genérico Eficacia ASC ─────────────────────────────────────────────
def write_top(ws, df, t, name_col, extra_cols=None):
    """Escribe Top 100 ordenado por Eficacia ASC. extra_cols = dict {header: col_name}"""
    if df is None or len(df)==0: ws.cell(1,1,'Sin datos').font=fnt('999999'); return
    title(ws, t, 'Ordenado por Eficacia ASC (peor primero) · Top 100')
    df_s = df.sort_values('Eficacia', ascending=True).head(100).copy()
    # Columnas base
    # Columnas base — WoW solo para Eficacia (CR_Unicos_WoW no es % usable)
    base_cols = [name_col,'Severity Eficacia','Severity Conv Rate','CR Únicos','Bookings',
                 'Eficacia','WoW Ef pp','Conv Rate']
    if extra_cols:
        all_cols = base_cols + list(extra_cols.keys())
    else:
        all_cols = base_cols
    r = mk_hdr(ws, 4, all_cols)
    for _, row in df_s.iterrows():
        ef = fmt_pct(row.get('Eficacia'))
        cv = fmt_pct(row.get('ConvRate'))
        bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
        cru= int(row.get('CR_Unicos',0)) if pd.notna(row.get('CR_Unicos',0)) else 0
        bef= banda_eficacia(ef) if ef is not None else '—'
        bcv= banda_convrate(cv,bk) if cv is not None else '—'
        wow_ef = row.get('Eficacia_WoW_pp')
        def fmt_wow(v):
            if v is None or (isinstance(v,float) and pd.isna(v)): return '—'
            s = '▲' if float(v)>=0 else '▼'; return f'{s}{abs(round(float(v),2))}'.replace('.',',')
        vals = [clean(row.get(name_col,'—')), bef, bcv, cru, bk, ef, fmt_wow(wow_ef), cv]
        if extra_cols:
            for col_name in extra_cols.values():
                vals.append(row.get(col_name,'—'))
        mk_row(ws, r, vals, 2, bef)
        if ef: ws.cell(r,6).number_format='0.00%'
        if cv: ws.cell(r,8).number_format='0.00%'
        r+=1
    widths = [38,16,16,10,10,10,10,10]
    if extra_cols: widths += [14]*len(extra_cols)
    autofit(ws, widths)

# ── Canastas ──────────────────────────────────────────────────────────────────
CANASTAS = [
    ('global', 'Global',     None, 'global'),
    ('b2c',    'B2C',        'B2C', 'B2C'),
    ('op',     'Opaco',      'B2B-OP', 'B2B-OP'),
    ('cug',    'Ultra Opaco','CUG', 'CUG'),
]

wb = Workbook(); wb.remove(wb.active)

for can_key, can_label, can_id, can_tab in CANASTAS:
    can   = CANASTA.get(can_id, CANASTA.get(can_key, {}))
    tab_ef = TAB_EF.get(can_key, TAB_EF.get('global',{}))
    tab_cv = TAB_CV.get(can_key, TAB_CV.get('global',{}))
    px    = can_label[:3]

    # Construir p80 con channel para esta canasta
    if can_id and 'DistributionCategory' in p80_all.columns:
        df_can = p80_all[p80_all['DistributionCategory']==can_id].copy()
    else:
        df_can = p80_all.copy()

    # Agregar channel a TAB_EF hotel si no lo tiene
    def add_channel(df):
        if df is None or len(df)==0: return df
        df2 = df.copy()
        if 'Channel' not in df2.columns and 'Hotel' in df2.columns:
            df2['Hotel_clean'] = df2['Hotel'].apply(clean)
            df2['Channel'] = df2['Hotel_clean'].map(hcm_clean).fillna('—')
        return df2

    # ── 1. Severity
    ws = wb.create_sheet(f'{px}-Severity'); ws.sheet_properties.tabColor=CR
    write_severity(ws, df_can, can_label)

    # ── 2-3. Destino
    for df, suf in [(tab_ef.get('destino'), 'EF'), (tab_cv.get('destino'), 'CV')]:
        ws = wb.create_sheet(f'{px}-Dest {suf}'); ws.sheet_properties.tabColor=CR
        write_top(ws, df, f'{can_label} · Top Destinos W{VOL_NUM}', 'Destino')

    # ── 4-5. Corp
    for df, suf in [(tab_ef.get('corp'), 'EF'), (tab_cv.get('corp'), 'CV')]:
        ws = wb.create_sheet(f'{px}-Corp {suf}'); ws.sheet_properties.tabColor=CR
        write_top(ws, df, f'{can_label} · Top Corporativos W{VOL_NUM}', 'CorpName')

    # ── 6-9. Hotel por categoría (con channel)
    hotel_cats = [
        ('top_crit', 'Críticos'),
        ('top_br',   'Bajo Rendimiento'),
        ('top_sc',   'Sin Conversión'),
        ('top_mcv',  'Menor Conv Rate'),
    ]
    for cat_key, cat_label in hotel_cats:
        df_cat = can.get(cat_key)
        if df_cat is None or len(df_cat)==0:
            df_cat = tab_ef.get('hotel')
        df_cat = add_channel(df_cat)
        ws = wb.create_sheet(f'{px}-Hot {cat_label[:6]}'); ws.sheet_properties.tabColor=CR
        write_top(ws, df_cat, f'{can_label} · Hotel {cat_label} W{VOL_NUM}', 'Hotel',
                  extra_cols={'Channel':'Channel','Destino':'Destino','Corp':'CorpName'})

    # ── 10-11. Channel
    for df, suf in [(tab_ef.get('channel'), 'EF'), (tab_cv.get('channel'), 'CV')]:
        ws = wb.create_sheet(f'{px}-Chan {suf}'); ws.sheet_properties.tabColor=CR
        if df is not None and len(df)>0:
            title(ws, f'{can_label} · Channel {suf} W{VOL_NUM}', 'Ordenado por Eficacia ASC')
            df_s = df.sort_values('Eficacia', ascending=True)
            cols = ['Channel','Severity Eficacia','Severity Conv Rate','CR Únicos','Bookings','Eficacia','Conv Rate']
            r = mk_hdr(ws, 4, cols)
            for _, row in df_s.iterrows():
                ef = fmt_pct(row.get('Eficacia'))
                cv = fmt_pct(row.get('ConvRate'))
                bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
                cru= int(row.get('CR_Unicos',0)) if pd.notna(row.get('CR_Unicos',0)) else 0
                bef= banda_eficacia(ef) if ef is not None else '—'
                bcv= banda_convrate(cv,bk) if cv is not None else '—'
                chan = row.get('ExternalProviderName', row.get('Channel','—'))
                mk_row(ws, r, [chan, bef, bcv, cru, bk, ef, cv], 2, bef)
                if ef: ws.cell(r,6).number_format='0.00%'
                if cv: ws.cell(r,7).number_format='0.00%'
                r+=1
            autofit(ws,[20,16,16,10,10,10,10])

    # ── 12-15. Dimensión Corp y Dest (con channel donde aplique)
    for tab, dim_key, name_col, suf in [
        (tab_ef,'corp','CorpName','Corp EF'), (tab_cv,'corp','CorpName','Corp CV'),
        (tab_ef,'destino','Destino','Dest EF'), (tab_cv,'destino','Destino','Dest CV'),
    ]:
        ws = wb.create_sheet(f'{px}-Dim {suf[:7]}'); ws.sheet_properties.tabColor=CR
        write_top(ws, tab.get(dim_key), f'{can_label} · AR Dimensión {suf} W{VOL_NUM}', name_col)

out = f'{OUTPUTS}/Analisis_CheckRates_W{VOL_NUM}.xlsx'
wb.save(out)
n = len(wb.sheetnames)
print(f'✅ Excel CR: {out}')
print(f'   {n} hojas: {" | ".join(wb.sheetnames[:8])}...')
