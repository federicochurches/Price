"""
excel_rnd.py · W21+ · Excel Rates No Dispo estructura completa
Por canasta: Severity | País ND | País IPM | Dest ND | Dest IPM |
             Corp ND | Corp IPM | Hotel ND Críticos | Hotel ND Bajo Rend |
             Hotel ND Sin Conv | Hotel ND Súper Crítica | Hotel IPM |
             Dim Corp ND | Dim Corp IPM | Dim Dest ND | Dim Dest IPM
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
CANASTA = D['CANASTA']

RND = 'EA0074'
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

def sf(v):
    try: f=float(v); return None if pd.isna(f) else f
    except: return None

def title(ws, t, sub=''):
    ws.cell(1,1,t).font = fnt(RND,13,True)
    if sub: ws.cell(2,1,sub).font = fnt('666666')

def mk_hdr(ws, row, cols):
    for c,lbl in enumerate(cols,1):
        cell=ws.cell(row,c,lbl)
        cell.font=fnt(white=True,bold=True); cell.fill=fill(RND)
        cell.alignment=Alignment(horizontal='center'); cell.border=BD
    ws.auto_filter.ref=f'A{row}:{get_column_letter(len(cols))}{row}'
    return row+1

def mk_row(ws, row, vals, sev_col=2, banda=None):
    for c,v in enumerate(vals,1):
        cell=ws.cell(row,c,v)
        cell.font=Font(name='Arial',size=10); cell.border=BD
        cell.alignment=Alignment(horizontal='left' if c==1 else 'center')
    if banda and banda in BFILL:
        ws.cell(row,sev_col).fill=BFILL[banda]
        ws.cell(row,sev_col).font=BFONT[banda]

def autofit(ws, widths):
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w

def fmt_wow(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return '—'
    s='▲' if float(v)>=0 else '▼'; return f'{s}{abs(round(float(v),2))}'.replace('.',',')

# ── Severity ──────────────────────────────────────────────────────────────────
def write_severity(ws, df, can_label):
    title(ws, f'{can_label} · Severity Rates No Dispo W{VOL_NUM}', f'W{VOL_NUM} · {PERIODO}')
    r = 4
    # NoDispo severity
    ws.cell(r,1,'Severity %NoDispo').font=fnt(RND,11,True); r+=1
    r=mk_hdr(ws, r, ['Severity','Hoteles','% del Total'])
    sev_nd={}
    for _, row in df.iterrows():
        nd=sf(row.get('%NoDispo'))
        if nd is not None: b=banda_nodispo(nd); sev_nd[b]=sev_nd.get(b,0)+1
    total=sum(sev_nd.values()) or 1
    for b in ['Exitosa','Aceptable','Revisar','Crítica','Súper Crítica']:
        n=sev_nd.get(b,0)
        cell=ws.cell(r,1,b); ws.cell(r,2,n); ws.cell(r,3,round(n/total,4))
        ws.cell(r,3).number_format='0.0%'
        if b in BFILL: cell.fill=BFILL[b]; cell.font=BFONT[b]
        for c in range(1,4): ws.cell(r,c).border=BD
        r+=1
    r+=1
    # IPM severity
    ws.cell(r,1,'Severity IPM').font=fnt(RND,11,True); r+=1
    r=mk_hdr(ws, r, ['Severity','Hoteles','% del Total'])
    sev_ipm={}
    for _, row in df.iterrows():
        ipm=sf(row.get('IPM',row.get('RPM'))); bk=int(sf(row.get('Bookings')) or 0)
        if ipm is not None: b=banda_rpm(ipm,bk); sev_ipm[b]=sev_ipm.get(b,0)+1
    total=sum(sev_ipm.values()) or 1
    for b in ['Exitosa','Aceptable','Revisar','Crítica','Sin Conversión']:
        n=sev_ipm.get(b,0)
        cell=ws.cell(r,1,b); ws.cell(r,2,n); ws.cell(r,3,round(n/total,4))
        ws.cell(r,3).number_format='0.0%'
        if b in BFILL: cell.fill=BFILL[b]; cell.font=BFONT[b]
        for c in range(1,4): ws.cell(r,c).border=BD
        r+=1
    autofit(ws,[22,12,12])

# ── Top ND ────────────────────────────────────────────────────────────────────
ND_COLS = ['Nombre','Severity NoDispo','Severity IPM','Tráfico','Bookings',
           '%NoDispo','WoW ND','IPM','WoW IPM','GB USD']

def write_nd(ws, df, t, name_col):
    title(ws, t, 'Ordenado por %NoDispo DESC (peor primero) · Top 100')
    if df is None or len(df)==0: ws.cell(1,1,'Sin datos'); return
    df_s = df.sort_values('%NoDispo', ascending=False).head(100)
    r = mk_hdr(ws, 4, ND_COLS)
    for _, row in df_s.iterrows():
        nd  = sf(row.get('%NoDispo')); ipm = sf(row.get('IPM',row.get('RPM')))
        bk  = int(sf(row.get('Bookings')) or 0); trf = int(sf(row.get('Trafico')) or 0)
        gb  = sf(row.get('gb_usd')); wow_nd = sf(row.get('NoDispo_WoW_pp')); wow_ipm = sf(row.get('IPM_WoW_pp'))
        bnd = banda_nodispo(nd) if nd is not None else '—'
        bipm= banda_rpm(ipm,bk) if ipm is not None else '—'
        nm  = str(row.get(name_col,'—'))
        vals=[nm, bnd, bipm, trf, bk, round(nd,4) if nd else None,
              fmt_wow(wow_nd), round(ipm,2) if ipm else None, fmt_wow(wow_ipm),
              round(gb,2) if gb else None]
        mk_row(ws, r, vals, 2, bnd)
        if nd: ws.cell(r,6).number_format='0.00%'
        if ipm: ws.cell(r,8).number_format='$#,##0'
        r+=1
    autofit(ws,[35,18,14,12,10,10,10,10,10,10])

# ── Top IPM ───────────────────────────────────────────────────────────────────
IPM_COLS = ['Nombre','Severity IPM','Severity NoDispo','Tráfico','Bookings',
            'IPM','WoW IPM','%NoDispo','WoW ND','GB USD']

def write_ipm(ws, df, t, name_col):
    title(ws, t, 'Ordenado por IPM ASC (peor primero) · Top 100')
    if df is None or len(df)==0: ws.cell(1,1,'Sin datos'); return
    ipm_col='IPM' if 'IPM' in df.columns else 'RPM'
    df_s = df[df['Bookings']>0].sort_values(ipm_col, ascending=True).head(100)
    r = mk_hdr(ws, 4, IPM_COLS)
    for _, row in df_s.iterrows():
        nd  = sf(row.get('%NoDispo')); ipm = sf(row.get(ipm_col))
        bk  = int(sf(row.get('Bookings')) or 0); trf = int(sf(row.get('Trafico')) or 0)
        gb  = sf(row.get('gb_usd')); wow_nd = sf(row.get('NoDispo_WoW_pp')); wow_ipm = sf(row.get('IPM_WoW_pp'))
        bnd = banda_nodispo(nd) if nd is not None else '—'
        bipm= banda_rpm(ipm,bk) if ipm is not None else '—'
        nm  = str(row.get(name_col,'—'))
        vals=[nm, bipm, bnd, trf, bk, round(ipm,2) if ipm else None,
              fmt_wow(wow_ipm), round(nd,4) if nd else None, fmt_wow(wow_nd),
              round(gb,2) if gb else None]
        mk_row(ws, r, vals, 2, bipm)
        if ipm: ws.cell(r,6).number_format='$#,##0'
        if nd: ws.cell(r,8).number_format='0.00%'
        r+=1
    autofit(ws,[35,14,18,12,10,10,10,10,10,10])

# ── Canastas ──────────────────────────────────────────────────────────────────
CANASTAS = [
    ('global', 'Global',     None),
    ('b2c',    'B2C',        'B2C'),
    ('op',     'Opaco',      'B2B-OP'),
    ('cug',    'Ultra Opaco','CUG'),
]

wb = Workbook(); wb.remove(wb.active)

for can_key, can_label, can_id in CANASTAS:
    can = CANASTA.get(can_id, CANASTA.get(can_key, {}))
    px  = can_label[:3]

    # p80_hotel para severity
    p80_can = can.get('p80_hotel', can.get('p80', D.get('p80_hotel', D.get('df18'))))
    if p80_can is None: p80_can = D.get('p80_hotel', D.get('df18'))

    # ── 1. Severity
    ws=wb.create_sheet(f'{px}-Severity'); ws.sheet_properties.tabColor=RND
    write_severity(ws, p80_can, can_label)

    # ── 2-3. País ND / IPM
    df_pais = TAB_ND.get('pais', pd.DataFrame())
    ws=wb.create_sheet(f'{px}-País ND'); ws.sheet_properties.tabColor=RND
    write_nd(ws, df_pais, f'{can_label} · Top Países %NoDispo W{VOL_NUM}', 'PaisDestino')
    ws=wb.create_sheet(f'{px}-País IPM'); ws.sheet_properties.tabColor=RND
    write_ipm(ws, df_pais, f'{can_label} · Top Países IPM W{VOL_NUM}', 'PaisDestino')

    # ── 4-5. Destino ND / IPM
    df_dest = TAB_ND.get('destino', pd.DataFrame())
    ws=wb.create_sheet(f'{px}-Dest ND'); ws.sheet_properties.tabColor=RND
    write_nd(ws, df_dest, f'{can_label} · Top Destinos %NoDispo W{VOL_NUM}', 'Destino')
    ws=wb.create_sheet(f'{px}-Dest IPM'); ws.sheet_properties.tabColor=RND
    write_ipm(ws, df_dest, f'{can_label} · Top Destinos IPM W{VOL_NUM}', 'Destino')

    # ── 6-7. Corp ND / IPM
    df_corp = TAB_ND.get('corp', pd.DataFrame())
    ws=wb.create_sheet(f'{px}-Corp ND'); ws.sheet_properties.tabColor=RND
    write_nd(ws, df_corp, f'{can_label} · Top Corp %NoDispo W{VOL_NUM}', 'CorpName')
    ws=wb.create_sheet(f'{px}-Corp IPM'); ws.sheet_properties.tabColor=RND
    write_ipm(ws, df_corp, f'{can_label} · Top Corp IPM W{VOL_NUM}', 'CorpName')

    # ── 8-11. Hotel por categoría
    hotel_cats_nd = [
        ('top_dnc',  'ND Sin Conv'),
        ('top_br',   'ND Bajo Rend'),
        ('top_sc',   'ND Súper Crítica'),
        ('top_hot',  'ND Top %NoDispo'),
    ]
    for cat_key, cat_label in hotel_cats_nd:
        df_cat = can.get(cat_key, TAB_ND.get('hotel', pd.DataFrame()))
        ws=wb.create_sheet(f'{px}-{cat_label[:12]}'); ws.sheet_properties.tabColor=RND
        write_nd(ws, df_cat, f'{can_label} · Hotel {cat_label} W{VOL_NUM}', 'Hotel')

    ws=wb.create_sheet(f'{px}-Hot IPM'); ws.sheet_properties.tabColor=RND
    write_ipm(ws, can.get('top_hot_rpm', TAB_IPM.get('hotel', pd.DataFrame())),
              f'{can_label} · Hotel Top IPM W{VOL_NUM}', 'Hotel')

    # ── 12-15. Dimensión Corp y Dest
    for df_nd, df_ipm, nc, suf in [
        (TAB_ND.get('corp'), TAB_IPM.get('corp'), 'CorpName', 'Corp'),
        (TAB_ND.get('destino'), TAB_IPM.get('destino'), 'Destino', 'Dest'),
    ]:
        ws=wb.create_sheet(f'{px}-Dim {suf} ND'); ws.sheet_properties.tabColor=RND
        write_nd(ws, df_nd, f'{can_label} · AR Dim {suf} %NoDispo W{VOL_NUM}', nc)
        ws=wb.create_sheet(f'{px}-Dim {suf} IPM'); ws.sheet_properties.tabColor=RND
        write_ipm(ws, df_ipm, f'{can_label} · AR Dim {suf} IPM W{VOL_NUM}', nc)

out = f'{OUTPUTS}/Analisis_RatesNoDispo_W{VOL_NUM}.xlsx'
wb.save(out)
n = len(wb.sheetnames)
print(f'✅ Excel RND: {out}')
print(f'   {n} hojas: {" | ".join(wb.sheetnames[:8])}...')
