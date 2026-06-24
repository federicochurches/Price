"""
excel_rnd.py · W26+ · Excel Rates No Dispo
Por canasta (7 hojas): Severity | País ND | Dest ND | Corp ND |
             Hot Críticos | Hot Bajo Rend | Hot Sin Conv
W26: IPM eliminado de Availability — solo se reporta %NoDispo.
     Hoteles: 3 bandas AR (banda por %NoDispo) desde el df hotel completo por canasta · Top 500
"""
import pickle, os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from engine import banda_nodispo

VOL_NUM = os.getenv('VOL_NUM', '21')
PERIODO = os.getenv('PERIODO', '19-25 mayo 2026')
OUTPUTS = os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs')

with open(os.getenv('PICKLE_RND', f'rnd_w{VOL_NUM}_data.pkl'), 'rb') as f:
    D = pickle.load(f)

TAB_ND  = D['TAB_NoDispo']
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
WOW_UP  = fill('EAF3DE');  WOW_UP_F  = fnt('2F6C34', bold=True)
WOW_DN  = fill('FCE8E6');  WOW_DN_F  = fnt('C0392B', bold=True)
WOW_NEU = fill('F2EEE6');  WOW_NEU_F = fnt('8A8377', bold=True)

def apply_wow(ws, row, col, val_pp, invert=False):
    cell = ws.cell(row, col)
    if val_pp is None or (isinstance(val_pp, float) and pd.isna(val_pp)):
        cell.value='—'; cell.font=WOW_NEU_F; cell.fill=WOW_NEU; cell.border=BD
        cell.alignment=Alignment(horizontal='center'); return
    is_up = float(val_pp) >= 0
    is_good = (is_up and not invert) or (not is_up and invert)
    s = '▲' if is_up else '▼'
    cell.value = f'{s}{abs(round(float(val_pp),2))}'.replace('.', ',')
    cell.fill  = WOW_UP if is_good else WOW_DN
    cell.font  = WOW_UP_F if is_good else WOW_DN_F
    cell.border = BD; cell.alignment = Alignment(horizontal='center')

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
def write_severity(ws, df, can_label, m_curr=None, m_prev=None):
    title(ws, f'{can_label} · Severity Rates No Dispo W{VOL_NUM}', f'W{VOL_NUM} · {PERIODO}')
    r = 4
    # WoW KPI global — solo %NoDispo (W26: IPM eliminado)
    if m_curr and m_prev:
        nd_curr=m_curr.get('pct_nodispo',0); nd_prev=m_prev.get('pct_nodispo',0)
        nd_wow=(nd_curr-nd_prev)*100 if nd_prev else None
        ws.cell(r,1,'KPI Global').font=fnt(RND,11,True); r+=1
        r=mk_hdr(ws,r,['Métrica',f'W{int(VOL_NUM)-1}',f'W{VOL_NUM}','WoW'])
        ws.cell(r,1,'%NoDispo').font=Font(name='Arial',size=10,bold=True); ws.cell(r,1).border=BD
        ws.cell(r,2,round(nd_prev,4) if nd_prev else None).border=BD; ws.cell(r,2).number_format='0.00%'; ws.cell(r,2).alignment=Alignment(horizontal='center')
        ws.cell(r,3,round(nd_curr,4) if nd_curr else None).border=BD; ws.cell(r,3).number_format='0.00%'; ws.cell(r,3).alignment=Alignment(horizontal='center')
        apply_wow(ws,r,4,nd_wow,invert=True); r+=2
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
    autofit(ws,[22,12,12])

# ── Top ND ────────────────────────────────────────────────────────────────────
ND_COLS = ['Nombre','Severity NoDispo','Tráfico','Bookings','%NoDispo','WoW ND','GB USD']

def write_nd(ws, df, t, name_col):
    title(ws, t, 'Ordenado por %NoDispo DESC (peor primero) · Top 500')
    if df is None or len(df)==0: ws.cell(1,1,'Sin datos'); return
    df_s = df.sort_values('%NoDispo', ascending=False).head(500)
    r = mk_hdr(ws, 4, ND_COLS)
    for _, row in df_s.iterrows():
        nd  = sf(row.get('%NoDispo'))
        bk  = int(sf(row.get('Bookings')) or 0); trf = int(sf(row.get('Trafico')) or 0)
        gb  = sf(row.get('gb_usd')); wow_nd = sf(row.get('NoDispo_WoW_pp'))
        bnd = banda_nodispo(nd) if nd is not None else '—'
        nm  = str(row.get(name_col,'—'))
        vals=[nm, bnd, trf, bk, round(nd,4) if nd else None,
              fmt_wow(wow_nd), round(gb,2) if gb else None]
        mk_row(ws, r, vals, 2, bnd)
        if nd: ws.cell(r,5).number_format='0.00%'
        nd_wow_v = sf(row.get('NoDispo_WoW_pp'))
        apply_wow(ws,r,6,nd_wow_v,invert=True)
        r+=1
    autofit(ws,[35,18,12,10,10,10,10])

# ── Split por banda AR (Críticos / Bajo Rendimiento / Sin Conversión) ──────────
# Banda por %NoDispo (métrica primaria del reporte). Sin Conversión = Bookings==0.
def band_split_nd(df):
    empty = pd.DataFrame()
    if df is None or len(df)==0: return empty, empty, empty
    d = df.copy()
    bk = d['Bookings'].fillna(0) if 'Bookings' in d.columns else pd.Series(0, index=d.index)
    # Recalcular la banda igual que el display (banda_nodispo sobre sf(%NoDispo))
    # para que la hoja de banda y la columna Severity coincidan siempre.
    bcol = d['%NoDispo'].apply(lambda v: banda_nodispo(sf(v)) if sf(v) is not None else '—')
    crit = d[(bk>0) & bcol.isin(['Crítica','Súper Crítica'])]
    bajo = d[(bk>0) & bcol.isin(['Revisar','Aceptable'])]
    sinc = d[bk==0]
    return crit, bajo, sinc

def hotel_source_rnd(can, can_id):
    """df hotel completo (con bandas+WoW): Global = p80_hotel · canasta = CANASTA[c]['p80_hotel']/['p80']."""
    if can_id is None:
        return D.get('p80_hotel', pd.DataFrame())
    src = can.get('p80_hotel')
    if src is None: src = can.get('p80')
    return src if src is not None else TAB_ND.get('hotel', pd.DataFrame())

# ── Canastas ──────────────────────────────────────────────────────────────────
CANASTAS = [
    ('global', 'Global',     None),
    ('b2c',    'B2C',        'B2C'),
    ('op',     'Opaco',      'B2B-OP'),
    ('cug',    'Ultra Opaco','CUG'),
]

wb = Workbook(); wb.remove(wb.active)

CANASTAS_M = {
    'global': ('global_w21','global_w20'),
    'b2c':    ('B2C_w21','B2C_w20'),
    'op':     ('B2B (OP)_w21','B2B (OP)_w20'),
    'cug':    ('CUG (UOP)_w21','CUG (UOP)_w20'),
}
for can_key, can_label, can_id in CANASTAS:
    can = CANASTA.get(can_id, CANASTA.get(can_key, {}))
    m_keys = CANASTAS_M.get(can_key, ('global_w21','global_w20'))
    m_curr = D['M'].get(m_keys[0], D['M'].get('global_w21',{}))
    m_prev = D['M'].get(m_keys[1], D['M'].get('global_w20',{}))
    px  = can_label[:3]

    # p80_hotel para severity
    p80_can = can.get('p80_hotel', can.get('p80', D.get('p80_hotel', D.get('df18'))))
    if p80_can is None: p80_can = D.get('p80_hotel', D.get('df18'))

    # ── 1. Severity
    ws=wb.create_sheet(f'{px}-Severity'); ws.sheet_properties.tabColor=RND
    write_severity(ws, p80_can, can_label, m_curr, m_prev)

    # ── Dimensiones por canasta (agg_corp/agg_dest/agg_pais del CANASTA_DATA)
    # Para Global se usan los TAB_ND globales; para canastas específicas los agg_* del pickle
    if can_id is None:
        # Global: usar TABs globales
        df_pais = TAB_ND.get('pais', pd.DataFrame())
        df_dest = TAB_ND.get('destino', pd.DataFrame())
        df_corp = TAB_ND.get('corp', pd.DataFrame())
    else:
        # Canasta específica: usar agg_* calculados por canasta en calc_rnd.py
        df_pais = can.get('agg_pais', TAB_ND.get('pais', pd.DataFrame()))
        df_dest = can.get('agg_dest', TAB_ND.get('destino', pd.DataFrame()))
        df_corp = can.get('agg_corp', TAB_ND.get('corp', pd.DataFrame()))

    # ── 2. País ND
    ws=wb.create_sheet(f'{px}-País ND'); ws.sheet_properties.tabColor=RND
    write_nd(ws, df_pais, f'{can_label} · Top Países %NoDispo W{VOL_NUM}', 'PaisDestino')

    # ── 3. Destino ND
    ws=wb.create_sheet(f'{px}-Dest ND'); ws.sheet_properties.tabColor=RND
    write_nd(ws, df_dest, f'{can_label} · Top Destinos %NoDispo W{VOL_NUM}', 'Destino')

    # ── 4. Corp ND
    ws=wb.create_sheet(f'{px}-Corp ND'); ws.sheet_properties.tabColor=RND
    write_nd(ws, df_corp, f'{can_label} · Top Corp %NoDispo W{VOL_NUM}', 'CorpName')

    # ── 8-10. Hotel por banda AR (Críticos / Bajo Rendimiento / Sin Conversión) · banda por %NoDispo
    hotel_src = hotel_source_rnd(can, can_id)
    crit, bajo, sinc = band_split_nd(hotel_src)
    for df_b, blabel in [(crit, 'Críticos'), (bajo, 'Bajo Rend'), (sinc, 'Sin Conv')]:
        ws=wb.create_sheet(f'{px}-Hot {blabel}'); ws.sheet_properties.tabColor=RND
        write_nd(ws, df_b, f'{can_label} · Hotel {blabel} (banda %NoDispo) W{VOL_NUM}', 'Hotel')

out = f'{OUTPUTS}/Analisis_RatesNoDispo_W{VOL_NUM}.xlsx'
wb.save(out)
n = len(wb.sheetnames)
print(f'✅ Excel RND: {out}')
print(f'   {n} hojas: {" | ".join(wb.sheetnames[:8])}...')
