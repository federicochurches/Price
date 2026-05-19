"""
Excel Análisis RND · 13 pestañas Top 100
Estructura post W17: Ficha Técnica + Severity (2) + Top 100 listings (5) +
Por Corp/Dest/País (3) + Plan Acción + Canastas Bajo Rend (3) = 13
"""
import pickle
import os, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

with open(os.getenv('PICKLE_RND', 'rnd_w20_data.pkl'),'rb') as _f:
    D = pickle.load(_f)
M = D['M']; TOP = D['TOP']; CANASTA = D['CANASTA']
sev_nd = D['sev_nd']; sev_rpm = D['sev_rpm']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']

wb = Workbook()
wb.remove(wb.active)

# Estilos
HEADER_FILL = PatternFill(start_color='EA0074', end_color='EA0074', fill_type='solid')
HEADER_FONT = Font(name='Arial', size=10, bold=True, color='FFFFFF')
TITLE_FONT  = Font(name='Arial', size=14, bold=True, color='EA0074')
META_FONT   = Font(name='Arial', size=10, color='666666')
DATA_FONT   = Font(name='Arial', size=10)
THIN = Side(border_style='thin', color='DDDDDD')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
BAND_FILLS = {
    'Exitosa':       PatternFill(start_color='E8F7FD', end_color='E8F7FD', fill_type='solid'),
    'Aceptable':     PatternFill(start_color='EDE8F7', end_color='EDE8F7', fill_type='solid'),
    'Revisar':       PatternFill(start_color='FFF4E0', end_color='FFF4E0', fill_type='solid'),
    'Crítica':       PatternFill(start_color='FCE4F1', end_color='FCE4F1', fill_type='solid'),
    'Súper Crítica': PatternFill(start_color='161616', end_color='161616', fill_type='solid'),
    'Sin Conversión':PatternFill(start_color='F2EEE6', end_color='F2EEE6', fill_type='solid'),
}
BAND_FONTS = {
    'Súper Crítica': Font(name='Arial', size=10, bold=True, color='FFFFFF'),
    'Sin Conversión': Font(name='Arial', size=10, color='8A8377'),
}

def add_title(ws, title, subtitle=''):
    ws['A1'] = title
    ws['A1'].font = TITLE_FONT
    if subtitle:
        ws['A2'] = subtitle
        ws['A2'].font = META_FONT
    ws['A3'] = f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")} · W18 · 27 abr – 3 may 2026'
    ws['A3'].font = META_FONT

def add_table(ws, df, start_row=5, num_formats=None, banda_col=None, banda_col2=None):
    """Escribe DF con headers y formatos. banda_col y banda_col2 aplican color fill por banda."""
    if num_formats is None: num_formats = {}
    cols = list(df.columns)
    # Header
    for j, c in enumerate(cols, 1):
        cell = ws.cell(row=start_row, column=j, value=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER
    # Data
    for i, (_, r) in enumerate(df.iterrows(), 1):
        for j, c in enumerate(cols, 1):
            val = r[c]
            cell = ws.cell(row=start_row+i, column=j, value=val if not pd.isna(val) else '')
            cell.font = DATA_FONT
            cell.border = BORDER
            if c in num_formats:
                cell.number_format = num_formats[c]
            # Aplicar color fill/font a columnas de banda
            band_val = None
            if banda_col and c == banda_col and val in BAND_FILLS:
                band_val = val
            elif banda_col2 and c == banda_col2 and val in BAND_FILLS:
                band_val = val
            if band_val:
                cell.fill = BAND_FILLS[band_val]
                if band_val in BAND_FONTS:
                    cell.font = BAND_FONTS[band_val]
    # Auto width
    for j, c in enumerate(cols, 1):
        max_len = max([len(str(c))] + [len(str(r[c])) if not pd.isna(r[c]) else 0 for _, r in df.iterrows()])
        ws.column_dimensions[get_column_letter(j)].width = min(max_len + 3, 50)
    # Freeze
    ws.freeze_panes = ws.cell(row=start_row+1, column=1)

# ==================== HOJA 1: SEVERITY %NoDispo ====================
ws2 = wb.create_sheet('Severity %NoDispo')
add_title(ws2, 'Severity · %NoDispo', f'P80 · {len(p80_hotel)} hoteles · target <3%')
total = int(sum(sev_nd.values()))
data = []
for n in ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']:
    rng = {'Súper Crítica':'>60%','Crítica':'20-60%','Revisar':'5-20%','Aceptable':'3-5%','Exitosa':'<3%'}[n]
    cnt = int(sev_nd[n])
    data.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total})
df_sev = pd.DataFrame(data)
add_table(ws2, df_sev, start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')

# ==================== HOJA 2: SEVERITY IPM (Income Per Million USD) ====================
ws3 = wb.create_sheet('Severity IPM')
add_title(ws3, 'Severity · IPM (Income Per Million USD)', f'P80 · {len(p80_hotel)} hoteles · target ≥ $650')
total_rpm = int(sum(sev_rpm.values()))
data = []
for n in ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']:
    rng = {'Sin Conversión':'BKGS=0','Crítica':'<$200','Revisar':'$200-$650','Aceptable':'$650-$1500','Exitosa':'≥$1500'}[n]
    cnt = int(sev_rpm[n])
    data.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total_rpm})
df_rpm = pd.DataFrame(data)
add_table(ws3, df_rpm, start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')

# ==================== HOJA 4: DEMANDA NO CONVERTIDA Top 100 ====================
ws4 = wb.create_sheet('Demanda No Convertida')
add_title(ws4, 'Top 100 · Demanda No Convertida',
          'Hoteles del P80 con mayor volumen de búsquedas perdidas (TraficoNoDispo)')
df_dnc = p80_hotel.sort_values('DemandaNoConvertida', ascending=False).head(100).reset_index(drop=True)
df_dnc.insert(0, 'Rk', range(1, len(df_dnc)+1))
df_dnc_out = df_dnc[['Rk','Hotel','CorpName','PaisDestino','Destino','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM','DemandaNoConvertida']].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
add_table(ws4, df_dnc_out,
          start_row=5, num_formats={'%NoDispo':'0.00%','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0','Trafico':'#,##0','DemandaNoConvertida':'#,##0'},
          banda_col='BandaNoDispo', banda_col2='Banda IPM')

# ==================== HOJA 5: BAJO RENDIMIENTO Top 100 ====================
ws5 = wb.create_sheet('Bajo Rendimiento')
add_title(ws5, 'Top 100 · Bajo Rendimiento',
          'Hoteles del P80 con BKGS>0 pero IPM en banda Crítica/Revisar (<$650) · ordenado por tráfico ↓')
mask_proc = (p80_hotel['Bookings']>0) & (p80_hotel['BandaRPM'].isin(['Crítica','Revisar']))
df_br = p80_hotel[mask_proc].sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
df_br.insert(0, 'Rk', range(1, len(df_br)+1))
df_br_out = df_br[['Rk','Hotel','CorpName','PaisDestino','Destino','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaRPM']].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
add_table(ws5, df_br_out,
          start_row=5, num_formats={'%NoDispo':'0.00%','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0','Trafico':'#,##0'},
          banda_col='BandaNoDispo', banda_col2='Banda IPM')

# ==================== HOJA 6: SIN CONVERSIÓN Top 100 ====================
ws6 = wb.create_sheet('Sin Conversión')
add_title(ws6, 'Top 100 · Sin Conversión',
          'Hoteles del P80 con BKGS=0 · cohorte estructural separada de Severity · ordenado por tráfico ↓')
df_sc = p80_hotel[p80_hotel['Bookings']==0].sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
df_sc.insert(0, 'Rk', range(1, len(df_sc)+1))
add_table(ws6, df_sc[['Rk','Hotel','CorpName','PaisDestino','Destino','Trafico','%NoDispo','BandaNoDispo']],
          start_row=5, num_formats={'%NoDispo':'0.00%','Trafico':'#,##0'},
          banda_col='BandaNoDispo')

# ==================== HOJA 7: POR CORPORATIVO Top 100 ====================
ws7 = wb.create_sheet('Por Corporativo')
add_title(ws7, 'Top 100 · Por Corporativo', 'Agregado por CorpName · ordenado por tráfico ↓')
g_corp = g_hotel.groupby('CorpName').agg(
    Trafico=('Trafico','sum'),
    Bookings=('Bookings','sum'),
    gb_usd=('gb_usd','sum'),
    TraficoNoDispo=('TraficoNoDispo','sum'),
    Hoteles=('Hotel','nunique')
).reset_index()
g_corp['%NoDispo'] = g_corp['TraficoNoDispo'] / g_corp['Trafico']
g_corp['RPM'] = g_corp['gb_usd'] / g_corp['Trafico'] * 1_000_000
g_corp['ConvRate'] = g_corp['Bookings'] / g_corp['Trafico']
from .._helpers.engine import banda_nodispo, banda_rpm
g_corp['BandaNoDispo'] = g_corp['%NoDispo'].apply(banda_nodispo)
g_corp['BandaRPM'] = g_corp.apply(lambda r: banda_rpm(r['RPM'], r['Bookings']), axis=1)
g_corp = g_corp.sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
g_corp.insert(0,'Rk', range(1, len(g_corp)+1))
g_corp_out = g_corp[['Rk','CorpName','Hoteles','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM']].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
add_table(ws7, g_corp_out,
          start_row=5, num_formats={'%NoDispo':'0.00%','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0','Trafico':'#,##0'},
          banda_col='BandaNoDispo', banda_col2='Banda IPM')

# ==================== HOJA 8: POR DESTINO Top 100 ====================
ws8 = wb.create_sheet('Por Destino')
add_title(ws8, 'Top 100 · Por Destino', 'Agregado por Destino · ordenado por tráfico ↓')
g_dest = g_hotel.groupby('Destino').agg(
    Trafico=('Trafico','sum'),
    Bookings=('Bookings','sum'),
    gb_usd=('gb_usd','sum'),
    TraficoNoDispo=('TraficoNoDispo','sum'),
    Hoteles=('Hotel','nunique')
).reset_index()
g_dest['%NoDispo'] = g_dest['TraficoNoDispo']/g_dest['Trafico']
g_dest['RPM'] = g_dest['gb_usd']/g_dest['Trafico']*1_000_000
g_dest['BandaNoDispo'] = g_dest['%NoDispo'].apply(banda_nodispo)
g_dest['BandaRPM'] = g_dest.apply(lambda r: banda_rpm(r['RPM'], r['Bookings']), axis=1)
g_dest = g_dest.sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
g_dest.insert(0,'Rk', range(1, len(g_dest)+1))
g_dest_out = g_dest[['Rk','Destino','Hoteles','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM']].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
add_table(ws8, g_dest_out,
          start_row=5, num_formats={'%NoDispo':'0.00%','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0','Trafico':'#,##0'},
          banda_col='BandaNoDispo', banda_col2='Banda IPM')

# ==================== HOJA 9: POR PAÍS Top 100 ====================
ws9 = wb.create_sheet('Por País')
add_title(ws9, 'Top 100 · Por País', 'Agregado por PaisDestino · ordenado por tráfico ↓')
g_pais = g_hotel.groupby('PaisDestino').agg(
    Trafico=('Trafico','sum'),
    Bookings=('Bookings','sum'),
    gb_usd=('gb_usd','sum'),
    TraficoNoDispo=('TraficoNoDispo','sum'),
    Hoteles=('Hotel','nunique')
).reset_index()
g_pais['%NoDispo'] = g_pais['TraficoNoDispo']/g_pais['Trafico']
g_pais['RPM'] = g_pais['gb_usd']/g_pais['Trafico']*1_000_000
g_pais['BandaNoDispo'] = g_pais['%NoDispo'].apply(banda_nodispo)
g_pais['BandaRPM'] = g_pais.apply(lambda r: banda_rpm(r['RPM'], r['Bookings']), axis=1)
g_pais = g_pais.sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
g_pais.insert(0,'Rk', range(1, len(g_pais)+1))
g_pais_out = g_pais[['Rk','PaisDestino','Hoteles','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM']].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
add_table(ws9, g_pais_out,
          start_row=5, num_formats={'%NoDispo':'0.00%','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0','Trafico':'#,##0'},
          banda_col='BandaNoDispo', banda_col2='Banda IPM')

# ==================== HOJA 10: PLAN DE ACCIÓN ====================
ws10 = wb.create_sheet('Plan de Acción')
add_title(ws10, 'Plan de Acción · W18',
          'Acciones priorizadas por área owner · 6 acciones (2 Quick Wins + 2 Mid + 2 Estratégicas)')
plan_data = [
    {'#':'QW1','Owner':'Supply · KAM','Cluster':'Quick Win','Plazo':'5 días',
     'Acción':f'Escalar {int(sev_nd["Súper Crítica"])} hoteles Súper Críticos del P80 (%NoDispo >60%)',
     'Métrica':'%NoDispo < 20%','Detalle':'Empezar por casos de mayor tráfico en TOP demanda no convertida'},
    {'#':'QW2','Owner':'Tech · Account','Cluster':'Quick Win','Plazo':'1 semana',
     'Acción':'Diagnóstico técnico Top 10 Sin Conversión de alto tráfico',
     'Métrica':'Conv Rate > 0','Detalle':'Revisar mapping, paridad, tarifas. 11.954 hoteles P80 con BKGS=0.'},
    {'#':'MP1','Owner':'Supply · BI','Cluster':'Mid Priority','Plazo':'3 semanas',
     'Acción':f'Plan saneamiento {int(sev_nd["Crítica"]+sev_nd["Súper Crítica"])} hoteles Crítica/Súper Crítica',
     'Métrica':f'{int((sev_nd["Crítica"]+sev_nd["Súper Crítica"])*0.5)} migrados a Revisar',
     'Detalle':'Separar por canasta · trabajar primero CUG y B2B-OP (weight 0,6)'},
    {'#':'MP2','Owner':'Pricing · Supply','Cluster':'Mid Priority','Plazo':'2 semanas',
     'Acción':'Revisión IPM en CUG (deterioro WoW)',
     'Métrica':'IPM > $650','Detalle':'Canasta de mayor weight con caída pronunciada en revenue'},
    {'#':'ES1','Owner':'Supply · Tech · KAM','Cluster':'Estratégica','Plazo':'Q3',
     'Acción':'Reducir cohorte Sin Conversión P80 (11.954 hoteles)',
     'Métrica':'-30% vs baseline','Detalle':'Proyecto trimestral remediación técnica + comercial'},
    {'#':'ES2','Owner':'Comercial · Legal','Cluster':'Estratégica','Plazo':'Q3',
     'Acción':'Definir SLAs %NoDispo por corporativo',
     'Métrica':'SLAs firmados','Detalle':'Top 10 corp por tráfico · cláusulas severity-based pricing'},
]
df_plan = pd.DataFrame(plan_data)
add_table(ws10, df_plan, start_row=5)

# ==================== CANASTAS · 8 pestañas por canasta ====================
def add_canasta_sheets_rnd(wb_target, key, c, prefix=None):
    """Agrega las 8 pestañas de una canasta al workbook target.
    Si prefix=None, usa 'Canasta {short}' (para Excel global).
    Si prefix='', usa nombres cortos sin prefix (para Excel solo-canasta).
    """
    short = c['short']
    p = prefix if prefix is not None else f'Canasta {short} · '
    full_name = lambda base: f'{p}{base}' if prefix is not None else f'Canasta {short} · {base}'
    
    # 1. Severity NoDispo
    ws_se = wb_target.create_sheet(full_name('Sev ND'))
    add_title(ws_se, f'Canasta {short} · Severity %NoDispo',
              f'{c["name"]} · P80 · target <3%')
    sev_dict = c.get('sev_nd', {})
    total_se = sum(sev_dict.values()) or 1
    data_se = []
    for n in ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']:
        rng = {'Súper Crítica':'>60%','Crítica':'20-60%','Revisar':'5-20%','Aceptable':'3-5%','Exitosa':'<3%'}[n]
        cnt = int(sev_dict.get(n,0))
        data_se.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total_se})
    add_table(ws_se, pd.DataFrame(data_se), start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')
    
    # 2. Severity IPM
    ws_si = wb_target.create_sheet(full_name('Sev IPM'))
    add_title(ws_si, f'Canasta {short} · Severity IPM (USD/M)',
              f'{c["name"]} · P80 · target ≥ $650')
    sev_dict2 = c.get('sev_rpm', {})
    total_si = sum(sev_dict2.values()) or 1
    data_si = []
    for n in ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']:
        rng = {'Sin Conversión':'BKGS=0','Crítica':'<$200','Revisar':'$200-$650','Aceptable':'$650-$1500','Exitosa':'≥$1500'}[n]
        cnt = int(sev_dict2.get(n,0))
        data_si.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total_si})
    add_table(ws_si, pd.DataFrame(data_si), start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')
    
    # 3. Bajo Rendimiento
    ws = wb_target.create_sheet(full_name('BajoRend'))
    add_title(ws, f'Canasta {short} · Top 100 Bajo Rendimiento',
              f'{c["name"]} · BKGS>0 · ordenado por tráfico ↓')
    df_c = c['agg_hotel'].copy()
    df_c['ConvRate'] = df_c['Bookings'] / df_c['Trafico'].replace(0, 1)
    df_c['BandaRPM'] = df_c.apply(lambda r: banda_rpm(r['RPM'], r['Bookings']), axis=1)
    mask = (df_c['Bookings']>0) & (df_c['BandaRPM'].isin(['Crítica','Revisar']))
    df_c = df_c[mask].sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
    df_c.insert(0,'Rk', range(1, len(df_c)+1))
    cols_show = ['Rk','Hotel','CorpName','PaisDestino','Destino','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM']
    cols_show = [c2 for c2 in cols_show if c2 in df_c.columns]
    df_c_out = df_c[cols_show].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
    add_table(ws, df_c_out, start_row=5,
              num_formats={'%NoDispo':'0.00%','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0','Trafico':'#,##0'},
              banda_col='BandaNoDispo', banda_col2='Banda IPM')
    
    # 4. Sin Conversión
    ws_sn = wb_target.create_sheet(full_name('Sin Conv'))
    add_title(ws_sn, f'Canasta {short} · Top 100 Sin Conversión',
              f'{c["name"]} · BKGS=0 · ordenado por tráfico ↓ · cohorte estructural')
    df_sn = c['agg_hotel'].copy()
    df_sn = df_sn[df_sn['Bookings']==0].sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
    df_sn.insert(0,'Rk', range(1, len(df_sn)+1))
    cols_sn = ['Rk','Hotel','CorpName','PaisDestino','Destino','Trafico','Bookings','%NoDispo','BandaNoDispo']
    cols_sn = [c2 for c2 in cols_sn if c2 in df_sn.columns]
    add_table(ws_sn, df_sn[cols_sn], start_row=5,
              num_formats={'%NoDispo':'0.00%','Trafico':'#,##0'},
              banda_col='BandaNoDispo')
    
    # 5. Demanda No Convertida
    ws_dn = wb_target.create_sheet(full_name('Demanda No Convertida'))
    add_title(ws_dn, f'Canasta {short} · Top 100 Demanda No Convertida',
              f'{c["name"]} · tráfico × %NoDispo · ordenado por demanda perdida ↓')
    df_dn = c['agg_hotel'].copy()
    df_dn['DemandaNC'] = df_dn['Trafico'] * df_dn['%NoDispo']
    df_dn = df_dn.sort_values('DemandaNC', ascending=False).head(100).reset_index(drop=True)
    df_dn.insert(0,'Rk', range(1, len(df_dn)+1))
    cols_dn = [col for col in ['Rk','Hotel','CorpName','PaisDestino','Destino','Trafico','%NoDispo','DemandaNC','Bookings','RPM','BandaNoDispo'] if col in df_dn.columns]
    df_dn_out = df_dn[cols_dn].rename(columns={'RPM':'IPM (USD/M)'})
    add_table(ws_dn, df_dn_out, start_row=5,
              num_formats={'%NoDispo':'0.00%','Trafico':'#,##0','DemandaNC':'#,##0','IPM (USD/M)':'$#,##0'},
              banda_col='BandaNoDispo')
    
    # 6. Por Corporativo
    ws_co = wb_target.create_sheet(full_name('Por Corp'))
    add_title(ws_co, f'Canasta {short} · Por Corporativo',
              f'{c["name"]} · Top 100 corp · ordenado por tráfico ↓')
    df_co = c['agg_corp'].copy().sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
    df_co.insert(0,'Rk', range(1, len(df_co)+1))
    cols_co = [col for col in ['Rk','CorpName','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM'] if col in df_co.columns]
    df_co_out = df_co[cols_co].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
    add_table(ws_co, df_co_out, start_row=5,
              num_formats={'%NoDispo':'0.00%','Trafico':'#,##0','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0'},
              banda_col='BandaNoDispo', banda_col2='Banda IPM')
    
    # 7. Por Destino
    ws_de = wb_target.create_sheet(full_name('Por Destino'))
    add_title(ws_de, f'Canasta {short} · Por Destino',
              f'{c["name"]} · Top 100 destinos · ordenado por tráfico ↓')
    df_de = c['agg_dest'].copy().sort_values('Trafico', ascending=False).head(100).reset_index(drop=True)
    df_de.insert(0,'Rk', range(1, len(df_de)+1))
    cols_de = [col for col in ['Rk','Destino','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM'] if col in df_de.columns]
    df_de_out = df_de[cols_de].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
    add_table(ws_de, df_de_out, start_row=5,
              num_formats={'%NoDispo':'0.00%','Trafico':'#,##0','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0'},
              banda_col='BandaNoDispo', banda_col2='Banda IPM')
    
    # 8. Por País
    ws_pa = wb_target.create_sheet(full_name('Por País'))
    add_title(ws_pa, f'Canasta {short} · Por País',
              f'{c["name"]} · todos los países · ordenado por tráfico ↓')
    df_pa = c['agg_pais'].copy().sort_values('Trafico', ascending=False).reset_index(drop=True)
    df_pa.insert(0,'Rk', range(1, len(df_pa)+1))
    cols_pa = [col for col in ['Rk','PaisDestino','Trafico','Bookings','gb_usd','%NoDispo','RPM','BandaNoDispo','BandaRPM'] if col in df_pa.columns]
    df_pa_out = df_pa[cols_pa].rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})
    add_table(ws_pa, df_pa_out, start_row=5,
              num_formats={'%NoDispo':'0.00%','Trafico':'#,##0','gb_usd':'$#,##0','IPM (USD/M)':'$#,##0'},
              banda_col='BandaNoDispo', banda_col2='Banda IPM')

# Agregar pestañas al Excel global
for key in ['b2c','op','cug']:
    add_canasta_sheets_rnd(wb, key, CANASTA[key])

# Save Excel global
out = '/mnt/user-data/outputs/Analisis_Rates_NoDispo_7d.xlsx'
wb.save(out)
print(f'Excel RND escrito: {out}')
print(f'Pestañas: {len(wb.sheetnames)}')

# === Generar 3 Excels solo-canasta ===
from openpyxl import Workbook as WB2
canasta_filename = {'b2c':'B2C','op':'OP','cug':'CUG'}
for key in ['b2c','op','cug']:
    wb_c = WB2()
    wb_c.remove(wb_c.active)
    add_canasta_sheets_rnd(wb_c, key, CANASTA[key], prefix='')
    out_c = f'/mnt/user-data/outputs/Analisis_Rates_NoDispo_{canasta_filename[key]}_7d.xlsx'
    wb_c.save(out_c)
    print(f'  ✓ Excel canasta {canasta_filename[key]}: {len(wb_c.sheetnames)} pestañas')
for s in wb.sheetnames: print(f'  - {s}')
