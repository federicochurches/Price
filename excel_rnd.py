"""
excel_rnd.py · W21+ · Excel Rates No Dispo con estructura completa
Pestañas por canasta: Severity KPI1 | Severity KPI2 | País EF | País IPM |
                      Destino ND | Destino IPM | Corp ND | Corp IPM |
                      Hotel ND | Hotel IPM | AR-Hotel ND | AR-Hotel IPM |
                      AR-Dim ND | AR-Dim IPM
"""
import pickle, os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from engine import banda_nodispo, banda_rpm

VOL_NUM = os.getenv('VOL_NUM', '21')
PERIODO = os.getenv('PERIODO', '19-25 mayo 2026')
OUTPUTS = os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs')

with open(os.getenv('PICKLE_RND', f'rnd_w{VOL_NUM}_data.pkl'), 'rb') as f:
    D = pickle.load(f)

TAB_ND  = D['TAB_NoDispo']
TAB_IPM = D['TAB_RPM']
df_all  = D['df18'].copy() if 'df18' in D else D['p80_hotel'].copy()

# ── Estilos ──────────────────────────────────────────────────────────────────
RND = 'EA0074'
HF  = PatternFill(start_color=RND, end_color=RND, fill_type='solid')
HFt = Font(name='Arial', size=10, bold=True, color='FFFFFF')
TF  = Font(name='Arial', size=13, bold=True, color=RND)
SF  = Font(name='Arial', size=10, color='666666')
DF  = Font(name='Arial', size=10)
T   = Side(border_style='thin', color='DDDDDD')
BD  = Border(left=T, right=T, top=T, bottom=T)

BAND_FILLS = {
    'Exitosa':        PatternFill(start_color='E1F5EE', end_color='E1F5EE', fill_type='solid'),
    'Aceptable':      PatternFill(start_color='FEF9C3', end_color='FEF9C3', fill_type='solid'),
    'Revisar':        PatternFill(start_color='FED7AA', end_color='FED7AA', fill_type='solid'),
    'Crítica':        PatternFill(start_color='FCE4F1', end_color='FCE4F1', fill_type='solid'),
    'Súper Crítica':  PatternFill(start_color='E8E6E3', end_color='E8E6E3', fill_type='solid'),
    'Sin Conversión': PatternFill(start_color='F2EEE6', end_color='F2EEE6', fill_type='solid'),
}
BAND_FONTS = {
    'Exitosa':        Font(name='Arial', size=10, color='1A6B4A', bold=True),
    'Aceptable':      Font(name='Arial', size=10, color='713F12', bold=True),
    'Revisar':        Font(name='Arial', size=10, color='C2410C', bold=True),
    'Crítica':        Font(name='Arial', size=10, color='99162B', bold=True),
    'Súper Crítica':  Font(name='Arial', size=10, color='2D2828', bold=True),
    'Sin Conversión': Font(name='Arial', size=10, color='5F5E5A', bold=True),
}

def safe_float(v):
    try:
        f = float(v)
        return None if pd.isna(f) else f
    except: return None

def hdr(ws, row, cols):
    for c, label in enumerate(cols, 1):
        cell = ws.cell(row=row, column=c, value=label)
        cell.font = HFt; cell.fill = HF
        cell.alignment = Alignment(horizontal='center'); cell.border = BD
    return row + 1

def data_row(ws, row, vals, banda=None):
    for c, v in enumerate(vals, 1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.font = DF; cell.border = BD
        cell.alignment = Alignment(horizontal='left' if c == 1 else 'center')
    if banda and banda in BAND_FILLS:
        b_cell = ws.cell(row=row, column=2)
        b_cell.fill = BAND_FILLS[banda]
        b_cell.font = BAND_FONTS[banda]

def write_severity(ws, df, title, nd_col='%NoDispo', ipm_col='IPM', bk_col='Bookings'):
    ws.cell(row=1, column=1, value=title).font = TF
    ws.cell(row=2, column=1, value=f'W{VOL_NUM} · {PERIODO}').font = SF
    r = 4
    # Severity NoDispo
    ws.cell(row=r, column=1, value='Severity % NoDispo').font = Font(name='Arial', size=11, bold=True, color=RND)
    r += 1
    r = hdr(ws, r, ['Banda', 'Registros', '% del Total'])
    sev_nd = {}
    for _, row in df.iterrows():
        nd = safe_float(row.get(nd_col))
        if nd is not None:
            b = banda_nodispo(nd)
            sev_nd[b] = sev_nd.get(b, 0) + 1
    total_nd = sum(sev_nd.values()) or 1
    for banda in ['Exitosa','Aceptable','Revisar','Crítica','Súper Crítica']:
        n = sev_nd.get(banda, 0)
        cell = ws.cell(row=r, column=1, value=banda)
        ws.cell(row=r, column=2, value=n)
        ws.cell(row=r, column=3, value=round(n/total_nd, 4))
        ws.cell(row=r, column=3).number_format = '0.0%'
        if banda in BAND_FILLS: cell.fill = BAND_FILLS[banda]; cell.font = BAND_FONTS[banda]
        for c in range(1,4): ws.cell(row=r, column=c).border = BD
        r += 1
    r += 1
    # Severity IPM
    ws.cell(row=r, column=1, value='Severity IPM').font = Font(name='Arial', size=11, bold=True, color=RND)
    r += 1
    r = hdr(ws, r, ['Banda', 'Registros', '% del Total'])
    sev_ipm = {}
    for _, row in df.iterrows():
        ipm = safe_float(row.get(ipm_col, row.get('RPM')))
        bk  = int(safe_float(row.get(bk_col)) or 0)
        if ipm is not None:
            b = banda_rpm(ipm, bk)
            sev_ipm[b] = sev_ipm.get(b, 0) + 1
    total_ipm = sum(sev_ipm.values()) or 1
    for banda in ['Exitosa','Aceptable','Revisar','Crítica','Sin Conversión']:
        n = sev_ipm.get(banda, 0)
        cell = ws.cell(row=r, column=1, value=banda)
        ws.cell(row=r, column=2, value=n)
        ws.cell(row=r, column=3, value=round(n/total_ipm, 4))
        ws.cell(row=r, column=3).number_format = '0.0%'
        if banda in BAND_FILLS: cell.fill = BAND_FILLS[banda]; cell.font = BAND_FONTS[banda]
        for c in range(1,4): ws.cell(row=r, column=c).border = BD
        r += 1
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 12

def write_nd(ws, df, title, name_col):
    ws.cell(row=1, column=1, value=title).font = TF
    ws.cell(row=2, column=1, value='Ordenado por %NoDispo DESC (peor primero) · Top 100').font = SF
    df_s = df.sort_values('%NoDispo', ascending=False).head(100)
    r = hdr(ws, 4, [name_col, 'Banda NoDispo', 'Tráfico', 'Bookings', '%NoDispo', 'WoW pp', 'IPM', 'GB USD'])
    for _, row in df_s.iterrows():
        nd  = safe_float(row.get('%NoDispo'))
        ipm = safe_float(row.get('IPM', row.get('RPM')))
        bk  = int(safe_float(row.get('Bookings')) or 0)
        trf = int(safe_float(row.get('Trafico')) or 0)
        wow = safe_float(row.get('NoDispo_WoW_pp'))
        gb  = safe_float(row.get('gb_usd'))
        bnd = banda_nodispo(nd) if nd is not None else '—'
        vals = [row.get(name_col,'—'), bnd, trf, bk,
                round(nd,4) if nd else None,
                round(wow,4) if wow else None,
                round(ipm,2) if ipm else None,
                round(gb,2) if gb else None]
        data_row(ws, r, vals, bnd)
        if nd: ws.cell(row=r, column=5).number_format = '0.00%'
        if wow: ws.cell(row=r, column=6).number_format = '+0.00%;-0.00%;0.00%'
        if ipm: ws.cell(row=r, column=7).number_format = '$#,##0'
        r += 1
    ws.column_dimensions['A'].width = 35
    for i, w in enumerate([16,14,10,10,10,10], 2):
        ws.column_dimensions[get_column_letter(i)].width = w

def write_ipm(ws, df, title, name_col):
    ws.cell(row=1, column=1, value=title).font = TF
    ws.cell(row=2, column=1, value='Ordenado por IPM ASC (peor primero) · Top 100').font = SF
    df_s = df[df['Bookings'] > 0].sort_values('IPM' if 'IPM' in df.columns else 'RPM', ascending=True).head(100)
    ipm_col = 'IPM' if 'IPM' in df.columns else 'RPM'
    r = hdr(ws, 4, [name_col, 'Banda IPM', 'Tráfico', 'Bookings', 'IPM', 'WoW IPM', '%NoDispo', 'GB USD'])
    for _, row in df_s.iterrows():
        nd  = safe_float(row.get('%NoDispo'))
        ipm = safe_float(row.get(ipm_col))
        bk  = int(safe_float(row.get('Bookings')) or 0)
        trf = int(safe_float(row.get('Trafico')) or 0)
        wow = safe_float(row.get('IPM_WoW_pp'))
        gb  = safe_float(row.get('gb_usd'))
        bnd = banda_rpm(ipm, bk) if ipm is not None else '—'
        vals = [row.get(name_col,'—'), bnd, trf, bk,
                round(ipm,2) if ipm else None,
                round(wow,2) if wow else None,
                round(nd,4) if nd else None,
                round(gb,2) if gb else None]
        data_row(ws, r, vals, bnd)
        if ipm: ws.cell(row=r, column=5).number_format = '$#,##0'
        if nd: ws.cell(row=r, column=7).number_format = '0.00%'
        r += 1
    ws.column_dimensions['A'].width = 35
    for i, w in enumerate([14,14,10,10,10,10], 2):
        ws.column_dimensions[get_column_letter(i)].width = w

# ── Canastas ─────────────────────────────────────────────────────────────────
CANASTAS = [
    ('global', 'Global',     None),
    ('b2c',    'B2C',        'B2C'),
    ('op',     'Opaco',      'B2B (OP)'),
    ('cug',    'Ultra Opaco','CUG (UOP)'),
]

wb = Workbook()
wb.remove(wb.active)

for can_key, can_label, distrib_filter in CANASTAS:
    # Filtrar df_all para esta canasta
    if distrib_filter and 'DistributionCategory' in df_all.columns:
        df_can = df_all[df_all['DistributionCategory'] == distrib_filter].copy()
    else:
        df_can = df_all.copy()

    prefix = can_label[:3]

    # 1. Severity (NoDispo + IPM juntos en una hoja)
    ws = wb.create_sheet(f'{prefix}-Severity')
    ws.sheet_properties.tabColor = RND
    write_severity(ws, df_can, f'{can_label} · Severity W{VOL_NUM}')

    # 2-3. País NoDispo / IPM
    df_pais = TAB_ND.get('pais', pd.DataFrame())
    if len(df_pais) > 0:
        ws = wb.create_sheet(f'{prefix}-País NoDispo')
        ws.sheet_properties.tabColor = RND
        write_nd(ws, df_pais, f'{can_label} · Top Países %NoDispo W{VOL_NUM}', 'PaisDestino')
        ws = wb.create_sheet(f'{prefix}-País IPM')
        ws.sheet_properties.tabColor = RND
        write_ipm(ws, df_pais, f'{can_label} · Top Países IPM W{VOL_NUM}', 'PaisDestino')

    # 4-5. Destino NoDispo / IPM
    df_dest = TAB_ND.get('destino', pd.DataFrame())
    if len(df_dest) > 0:
        ws = wb.create_sheet(f'{prefix}-Dest NoDispo')
        ws.sheet_properties.tabColor = RND
        write_nd(ws, df_dest, f'{can_label} · Top Destinos %NoDispo W{VOL_NUM}', 'Destino')
        ws = wb.create_sheet(f'{prefix}-Dest IPM')
        ws.sheet_properties.tabColor = RND
        write_ipm(ws, df_dest, f'{can_label} · Top Destinos IPM W{VOL_NUM}', 'Destino')

    # 6-7. Corp NoDispo / IPM
    df_corp = TAB_ND.get('corp', pd.DataFrame())
    if len(df_corp) > 0:
        ws = wb.create_sheet(f'{prefix}-Corp NoDispo')
        ws.sheet_properties.tabColor = RND
        write_nd(ws, df_corp, f'{can_label} · Top Corp %NoDispo W{VOL_NUM}', 'CorpName')
        ws = wb.create_sheet(f'{prefix}-Corp IPM')
        ws.sheet_properties.tabColor = RND
        write_ipm(ws, df_corp, f'{can_label} · Top Corp IPM W{VOL_NUM}', 'CorpName')

    # 8-9. Hotel NoDispo / IPM
    df_hotel = TAB_ND.get('hotel', pd.DataFrame())
    if len(df_hotel) > 0:
        ws = wb.create_sheet(f'{prefix}-Hotel NoDispo')
        ws.sheet_properties.tabColor = RND
        write_nd(ws, df_hotel, f'{can_label} · Top Hoteles %NoDispo W{VOL_NUM}', 'Hotel')
        ws = wb.create_sheet(f'{prefix}-Hotel IPM')
        ws.sheet_properties.tabColor = RND
        write_ipm(ws, df_hotel, f'{can_label} · Top Hoteles IPM W{VOL_NUM}', 'Hotel')

    # 10-11. AR Dimensión (dest + corp combinados) NoDispo / IPM
    df_dim_nd  = pd.concat([
        TAB_ND.get('destino', pd.DataFrame()).assign(**{'Dimensión': lambda x: x.get('Destino', x.index)}),
        TAB_ND.get('corp', pd.DataFrame()).assign(**{'Dimensión': lambda x: x.get('CorpName', x.index)})
    ], ignore_index=True) if len(TAB_ND.get('destino', pd.DataFrame())) > 0 else pd.DataFrame()

    if len(df_dim_nd) > 0:
        # Agregar columna Dimensión correctamente
        df_dest_d = TAB_ND.get('destino', pd.DataFrame()).copy()
        df_corp_d = TAB_ND.get('corp', pd.DataFrame()).copy()
        if 'Destino' in df_dest_d.columns: df_dest_d['Dimensión'] = df_dest_d['Destino']
        if 'CorpName' in df_corp_d.columns: df_corp_d['Dimensión'] = df_corp_d['CorpName']
        df_dim = pd.concat([df_dest_d, df_corp_d], ignore_index=True)
        ws = wb.create_sheet(f'{prefix}-Dim NoDispo')
        ws.sheet_properties.tabColor = RND
        write_nd(ws, df_dim, f'{can_label} · AR Dimensión %NoDispo W{VOL_NUM}', 'Dimensión')
        ws = wb.create_sheet(f'{prefix}-Dim IPM')
        ws.sheet_properties.tabColor = RND
        write_ipm(ws, df_dim, f'{can_label} · AR Dimensión IPM W{VOL_NUM}', 'Dimensión')

out = f'{OUTPUTS}/Analisis_RatesNoDispo_W{VOL_NUM}.xlsx'
wb.save(out)
print(f'✅ Excel RND escrito: {out}')
print(f'   {len(wb.sheetnames)} hojas: {" | ".join(wb.sheetnames[:6])}...')
