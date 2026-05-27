"""
excel_cr.py · W21+ · Excel CheckRates estructura completa
Por canasta: Severity | Destino EF | Destino CV | Corp EF | Corp CV |
             Hotel EF | Hotel CV | AR-Dim EF | AR-Dim CV
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

CANASTA = D['CANASTA']
TAB_EF  = D['TAB_EF_BY_CANASTA']
TAB_CV  = D['TAB_CV_BY_CANASTA']

def clean(name):
    return re.sub(r'^\(\d+\)\s*-\s*', '', str(name)).strip() if name else name

# ── Estilos
CR = '5C469C'; RW = 'EA0074'
def fill(c): return PatternFill(start_color=c, end_color=c, fill_type='solid')
def font(c='000000', sz=10, bold=False, white=False):
    return Font(name='Arial', size=sz, bold=bold, color='FFFFFF' if white else c)
T  = Side(border_style='thin', color='DDDDDD')
BD = Border(left=T, right=T, top=T, bottom=T)

BFILL = {
    'Exitosa':       fill('E1F5EE'), 'Aceptable':     fill('FEF9C3'),
    'Revisar':       fill('FED7AA'), 'Crítica':        fill('FCE4F1'),
    'Súper Crítica': fill('E8E6E3'), 'Sin Conversión': fill('F2EEE6'),
}
BFONT = {
    'Exitosa':       font('1A6B4A',bold=True), 'Aceptable':     font('713F12',bold=True),
    'Revisar':       font('C2410C',bold=True), 'Crítica':        font('99162B',bold=True),
    'Súper Crítica': font('2D2828',bold=True), 'Sin Conversión': font('5F5E5A',bold=True),
}

def mk_hdr(ws, r, cols, color=CR):
    hf = fill(color)
    for c, lbl in enumerate(cols, 1):
        cell = ws.cell(row=r, column=c, value=lbl)
        cell.font = font(white=True, bold=True); cell.fill = hf
        cell.alignment = Alignment(horizontal='center'); cell.border = BD
    return r + 1

def mk_row(ws, r, vals, banda=None):
    for c, v in enumerate(vals, 1):
        cell = ws.cell(row=r, column=c, value=v)
        cell.font = Font(name='Arial', size=10); cell.border = BD
        cell.alignment = Alignment(horizontal='left' if c==1 else 'center')
    if banda and banda in BFILL:
        ws.cell(row=r, column=2).fill = BFILL[banda]
        ws.cell(row=r, column=2).font = BFONT[banda]

def title(ws, t, sub=''):
    ws.cell(row=1, column=1, value=t).font = Font(name='Arial', size=13, bold=True, color=CR)
    if sub: ws.cell(row=2, column=1, value=sub).font = Font(name='Arial', size=10, color='666666')

def sev_table(ws, sev_ef, sev_cv, can_label):
    title(ws, f'{can_label} · Severity W{VOL_NUM}', f'W{VOL_NUM} · {PERIODO}')
    r = 4
    ws.cell(row=r, column=1, value='Severity Eficacia').font = Font(name='Arial', size=11, bold=True, color=CR); r+=1
    r = mk_hdr(ws, r, ['Banda', 'Hoteles', '% Total']); total = sum(sev_ef.values()) or 1
    for b in ['Exitosa','Aceptable','Revisar','Crítica','Súper Crítica']:
        n = int(sev_ef.get(b, 0))
        cell = ws.cell(row=r, column=1, value=b)
        ws.cell(row=r, column=2, value=n); ws.cell(row=r, column=3, value=round(n/total,4))
        ws.cell(row=r, column=3).number_format = '0.0%'
        if b in BFILL: cell.fill = BFILL[b]; cell.font = BFONT[b]
        for c in range(1,4): ws.cell(row=r,column=c).border = BD
        r += 1
    r += 1
    ws.cell(row=r, column=1, value='Severity Conv Rate').font = Font(name='Arial', size=11, bold=True, color=CR); r+=1
    r = mk_hdr(ws, r, ['Banda', 'Hoteles', '% Total']); total = sum(sev_cv.values()) or 1
    for b in ['Exitosa','Aceptable','Revisar','Crítica','Sin Conversión']:
        n = int(sev_cv.get(b, 0))
        cell = ws.cell(row=r, column=1, value=b)
        ws.cell(row=r, column=2, value=n); ws.cell(row=r, column=3, value=round(n/total,4))
        ws.cell(row=r, column=3).number_format = '0.0%'
        if b in BFILL: cell.fill = BFILL[b]; cell.font = BFONT[b]
        for c in range(1,4): ws.cell(row=r,column=c).border = BD
        r += 1
    ws.column_dimensions['A'].width = 18; ws.column_dimensions['B'].width = 12; ws.column_dimensions['C'].width = 12

def top100_ef(ws, df, t, name_col):
    title(ws, t, 'Ordenado por Eficacia ASC (peor primero) · Top 100')
    if df is None or len(df) == 0: return
    df_s = df.sort_values('Eficacia', ascending=True).head(100)
    r = mk_hdr(ws, 4, [name_col, 'Banda Eficacia', 'CR Únicos', 'Bookings', 'Eficacia', 'Conv Rate', 'Banda CV'])
    for _, row in df_s.iterrows():
        ef = float(row['Eficacia']) if pd.notna(row.get('Eficacia')) else None
        cv = float(row['ConvRate']) if pd.notna(row.get('ConvRate')) else None
        bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
        cru= int(row.get('CR_Unicos',0)) if pd.notna(row.get('CR_Unicos',0)) else 0
        bef= banda_eficacia(ef) if ef is not None else '—'
        bcv= banda_convrate(cv, bk) if cv is not None else '—'
        mk_row(ws, r, [clean(row.get(name_col,'—')), bef, cru, bk, ef, cv, bcv], bef)
        if ef: ws.cell(row=r,column=5).number_format='0.00%'
        if cv: ws.cell(row=r,column=6).number_format='0.00%'
        r += 1
    ws.column_dimensions['A'].width=35; ws.column_dimensions['B'].width=16
    for i,w in enumerate([12,10,12,12,14],3): ws.column_dimensions[get_column_letter(i)].width=w

def top100_cv(ws, df, t, name_col):
    title(ws, t, 'Ordenado por Conv Rate ASC (peor primero) · Top 100')
    if df is None or len(df) == 0: return
    df_s = df.sort_values('ConvRate', ascending=True).head(100)
    r = mk_hdr(ws, 4, [name_col, 'Banda CV', 'CR Únicos', 'Bookings', 'Conv Rate', 'Eficacia', 'Banda Eficacia'])
    for _, row in df_s.iterrows():
        ef = float(row['Eficacia']) if pd.notna(row.get('Eficacia')) else None
        cv = float(row['ConvRate']) if pd.notna(row.get('ConvRate')) else None
        bk = int(row.get('Bookings',0)) if pd.notna(row.get('Bookings',0)) else 0
        cru= int(row.get('CR_Unicos',0)) if pd.notna(row.get('CR_Unicos',0)) else 0
        bef= banda_eficacia(ef) if ef is not None else '—'
        bcv= banda_convrate(cv, bk) if cv is not None else '—'
        mk_row(ws, r, [clean(row.get(name_col,'—')), bcv, cru, bk, cv, ef, bef], bcv)
        if cv: ws.cell(row=r,column=5).number_format='0.00%'
        if ef: ws.cell(row=r,column=6).number_format='0.00%'
        r += 1
    ws.column_dimensions['A'].width=35; ws.column_dimensions['B'].width=14
    for i,w in enumerate([12,10,12,12,14],3): ws.column_dimensions[get_column_letter(i)].width=w

# ── Canastas ──────────────────────────────────────────────────────────────────
CANASTAS = [
    ('global', 'Global',     'global'),
    ('b2c',    'B2C',        'B2C'),
    ('op',     'Opaco',      'B2B-OP'),
    ('cug',    'Ultra Opaco','CUG'),
]

wb = Workbook(); wb.remove(wb.active)

for can_key, can_label, can_id in CANASTAS:
    can = CANASTA.get(can_id, CANASTA.get(can_key, {}))
    sev_ef = dict(can.get('sev_ef', {})) if can.get('sev_ef') is not None else {}
    sev_cv = dict(can.get('sev_cv', {})) if can.get('sev_cv') is not None else {}

    tab_ef = TAB_EF.get(can_key, TAB_EF.get('global', {}))
    tab_cv = TAB_CV.get(can_key, TAB_CV.get('global', {}))
    p80    = can.get('p80')

    px = can_label[:3]

    # Severity
    ws = wb.create_sheet(f'{px}-Severity'); ws.sheet_properties.tabColor = CR
    sev_table(ws, sev_ef, sev_cv, can_label)

    # Destino
    for df, fn, suf in [(tab_ef.get('destino'), top100_ef, 'Ef'), (tab_cv.get('destino'), top100_cv, 'CV')]:
        ws = wb.create_sheet(f'{px}-Dest {suf}'); ws.sheet_properties.tabColor = CR
        fn(ws, df, f'{can_label} · Top Destinos {suf} W{VOL_NUM}', 'Destino')

    # Corp
    for df, fn, suf in [(tab_ef.get('corp'), top100_ef, 'Ef'), (tab_cv.get('corp'), top100_cv, 'CV')]:
        ws = wb.create_sheet(f'{px}-Corp {suf}'); ws.sheet_properties.tabColor = CR
        fn(ws, df, f'{can_label} · Top Corp {suf} W{VOL_NUM}', 'CorpName')

    # Hotel (AR Hotel)
    for df, fn, suf in [(tab_ef.get('hotel'), top100_ef, 'Ef'), (tab_cv.get('hotel'), top100_cv, 'CV')]:
        ws = wb.create_sheet(f'{px}-Hotel {suf}'); ws.sheet_properties.tabColor = CR
        fn(ws, df, f'{can_label} · Top Hoteles {suf} W{VOL_NUM}', 'Hotel')

    # AR Dimensión (dest + corp combinados)
    for tab, fn, suf in [(tab_ef, top100_ef, 'Ef'), (tab_cv, top100_cv, 'CV')]:
        df_dest = tab.get('destino', pd.DataFrame())
        df_corp = tab.get('corp', pd.DataFrame())
        if len(df_dest) > 0 and len(df_corp) > 0:
            dd = df_dest.copy(); cc = df_corp.copy()
            if 'Destino' in dd.columns: dd['Nombre'] = dd['Destino']
            if 'CorpName' in cc.columns: cc['Nombre'] = cc['CorpName']
            df_dim = pd.concat([dd, cc], ignore_index=True)
            ws = wb.create_sheet(f'{px}-Dim {suf}'); ws.sheet_properties.tabColor = CR
            fn(ws, df_dim, f'{can_label} · AR Dimensión {suf} W{VOL_NUM}', 'Nombre')

out = f'{OUTPUTS}/Analisis_CheckRates_W{VOL_NUM}.xlsx'
wb.save(out)
n = len(wb.sheetnames)
print(f'✅ Excel CR escrito: {out}')
print(f'   {n} hojas: {" | ".join(wb.sheetnames)}')
