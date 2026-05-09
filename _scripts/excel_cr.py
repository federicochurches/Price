"""
Excel Análisis CR W18 · 17 pestañas Top 50 (estructura post-Fix #9 y #11)
Ficha Técnica + Severity (2) + Top 50 listings (4) + Por Corp/Destino/Channel (3) +
Menor Conv Rate + Plan Acción + Canastas (Críticos+BajoRend × 3 = 6) = 17
"""
import pickle, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from engine import banda_eficacia, banda_convrate

with open('cr_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']; CANASTA = D['CANASTA']
sev_ef_p80 = D['sev_ef_p80']; sev_cv_p80 = D['sev_cv_p80']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']
g_corp = D['g_corp']; g_channel = D['g_channel']; g_grupo = D['g_grupo']

wb = Workbook()
wb.remove(wb.active)

# Estilos
HEADER_FILL = PatternFill(start_color='0080A8', end_color='0080A8', fill_type='solid')
HEADER_FONT = Font(name='Arial', size=10, bold=True, color='FFFFFF')
TITLE_FONT  = Font(name='Arial', size=14, bold=True, color='0080A8')
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
BAND_FONTS = {'Súper Crítica': Font(name='Arial', size=10, bold=True, color='FFFFFF')}

def add_title(ws, title, subtitle=''):
    ws['A1'] = title
    ws['A1'].font = TITLE_FONT
    if subtitle:
        ws['A2'] = subtitle
        ws['A2'].font = META_FONT
    ws['A3'] = f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")} · W18 · 27 abr – 3 may 2026'
    ws['A3'].font = META_FONT

def add_table(ws, df, start_row=5, num_formats=None, banda_col=None):
    if num_formats is None: num_formats = {}
    cols = list(df.columns)
    for j, c in enumerate(cols, 1):
        cell = ws.cell(row=start_row, column=j, value=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER
    for i, (_, r) in enumerate(df.iterrows(), 1):
        for j, c in enumerate(cols, 1):
            val = r[c]
            cell = ws.cell(row=start_row+i, column=j, value=val if not pd.isna(val) else '')
            cell.font = DATA_FONT
            cell.border = BORDER
            if c in num_formats:
                cell.number_format = num_formats[c]
            if banda_col and c == banda_col and val in BAND_FILLS:
                cell.fill = BAND_FILLS[val]
                if val in BAND_FONTS:
                    cell.font = BAND_FONTS[val]
    for j, c in enumerate(cols, 1):
        max_len = max([len(str(c))] + [len(str(r[c])) if not pd.isna(r[c]) else 0 for _, r in df.iterrows()])
        ws.column_dimensions[get_column_letter(j)].width = min(max_len + 3, 50)
    ws.freeze_panes = ws.cell(row=start_row+1, column=1)

# ==================== 1. SEVERITY EFICACIA ====================
ws2 = wb.create_sheet('Severity Eficacia')
add_title(ws2, 'Severity · Eficacia', f'P80 · {len(p80_hotel)} hoteles · target ≥ 97%')
total = int(sev_ef_p80.sum())
data = []
for n in ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']:
    rng = {'Súper Crítica':'<60%','Crítica':'60-85%','Revisar':'85-93%','Aceptable':'93-97%','Exitosa':'≥97%'}[n]
    cnt = int(sev_ef_p80.get(n,0))
    data.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total})
add_table(ws2, pd.DataFrame(data), start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')

# ==================== 2. SEVERITY CONVRATE ====================
ws3 = wb.create_sheet('Severity ConvRate')
add_title(ws3, 'Severity · ConvRate', f'P80 · {len(p80_hotel)} hoteles · target ≥ 2,5%')
total = int(sev_cv_p80.sum())
data = []
for n in ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']:
    rng = {'Sin Conversión':'BKGS=0','Crítica':'<0,8%','Revisar':'0,8-1,5%','Aceptable':'1,5-2,5%','Exitosa':'≥2,5%'}[n]
    cnt = int(sev_cv_p80.get(n,0))
    data.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total})
add_table(ws3, pd.DataFrame(data), start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')

# ==================== 4. HOTELES CRÍTICOS Top 50 ====================
ws4 = wb.create_sheet('Críticos')
add_title(ws4, 'Top 50 · Hoteles Críticos',
          'Hoteles del P80 con BKGS>0 · peor Eficacia · ordenado por Eficacia ↑')
mask = (p80_hotel['Bookings']>0) & (p80_hotel['BandaEficacia'].isin(['Crítica','Súper Crítica']))
df_crit = p80_hotel[mask].sort_values('Eficacia').head(50).reset_index(drop=True)
df_crit.insert(0, 'Rk', range(1, len(df_crit)+1))
add_table(ws4, df_crit[['Rk','Hotel','CorpName','Destino','CR_Unicos','Successful','Bookings','Eficacia','ConvRate','BandaEficacia']],
          start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
          banda_col='BandaEficacia')

# ==================== 5. BAJO RENDIMIENTO Top 50 ====================
ws5 = wb.create_sheet('Bajo Rendimiento')
add_title(ws5, 'Top 50 · Bajo Rendimiento',
          'Hoteles del P80 con BKGS>0 y ConvRate Crítica/Revisar · ordenado por CR únicos ↓')
mask = (p80_hotel['Bookings']>0) & (p80_hotel['BandaConvRate'].isin(['Crítica','Revisar']))
df_br = p80_hotel[mask].sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
df_br.insert(0, 'Rk', range(1, len(df_br)+1))
add_table(ws5, df_br[['Rk','Hotel','CorpName','Destino','CR_Unicos','Bookings','Eficacia','ConvRate','BandaConvRate']],
          start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0'},
          banda_col='BandaConvRate')

# ==================== 6. SIN CONVERSIÓN Top 50 ====================
ws6 = wb.create_sheet('Sin Conversión')
add_title(ws6, 'Top 50 · Sin Conversión',
          'Hoteles del P80 con BKGS=0 · cohorte estructural separada de Severity · ordenado por CR ↓')
df_sc = p80_hotel[p80_hotel['Bookings']==0].sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
df_sc.insert(0, 'Rk', range(1, len(df_sc)+1))
add_table(ws6, df_sc[['Rk','Hotel','CorpName','Destino','CR_Unicos','Successful','Eficacia','BandaEficacia']],
          start_row=5, num_formats={'Eficacia':'0.00%','CR_Unicos':'#,##0','Successful':'#,##0'},
          banda_col='BandaEficacia')

# ==================== 7. POR CORPORATIVO Top 50 ====================
ws7 = wb.create_sheet('Por Corporativo')
add_title(ws7, 'Top 50 · Por Corporativo', 'Agregado por CorpName · ordenado por CR únicos ↓')
df_corp = g_corp.sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
df_corp.insert(0,'Rk', range(1, len(df_corp)+1))
add_table(ws7, df_corp[['Rk','CorpName','CR_Unicos','Successful','Bookings','Eficacia','ConvRate','BandaEficacia','BandaConvRate']],
          start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
          banda_col='BandaEficacia')

# ==================== 8. POR DESTINO Top 50 (Fix #9 NUEVO) ====================
ws8 = wb.create_sheet('Por Destino')
add_title(ws8, 'Top 50 · Por Destino', 'Agregado por Destino · ordenado por CR únicos ↓')
g_dest = g_hotel.groupby('Destino').agg(
    CR_Unicos=('CR_Unicos','sum'),
    Successful=('Successful','sum'),
    Bookings=('Bookings','sum'),
    Hoteles=('Hotel','nunique')
).reset_index()
g_dest['Eficacia'] = g_dest['Successful']/g_dest['CR_Unicos'].replace(0,1)
g_dest['ConvRate'] = g_dest['Bookings']/g_dest['CR_Unicos'].replace(0,1)
g_dest['BandaEficacia'] = g_dest['Eficacia'].apply(banda_eficacia)
g_dest['BandaConvRate'] = g_dest.apply(lambda r: banda_convrate(r['ConvRate'], r['Bookings']), axis=1)
g_dest = g_dest.sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
g_dest.insert(0,'Rk', range(1, len(g_dest)+1))
add_table(ws8, g_dest[['Rk','Destino','Hoteles','CR_Unicos','Bookings','Eficacia','ConvRate','BandaEficacia','BandaConvRate']],
          start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0'},
          banda_col='BandaEficacia')

# ==================== 9. POR CHANNEL (Fix #9 NUEVO) ====================
ws9 = wb.create_sheet('Por Channel')
add_title(ws9, 'Por Channel · todos los providers',
          'Agregado por ExternalProviderName · 11 channels')
df_chan = g_channel.sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
df_chan.insert(0,'Rk', range(1, len(df_chan)+1))
add_table(ws9, df_chan[['Rk','ExternalProviderName','Grupo','CR_Unicos','Successful','Bookings','Eficacia','ConvRate','BandaEficacia','BandaConvRate']] if 'Grupo' in df_chan.columns else df_chan,
          start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
          banda_col='BandaEficacia')

# ==================== 10. MENOR CONV RATE Top 50 ====================
ws10 = wb.create_sheet('Menor Conv Rate')
add_title(ws10, 'Top 50 · Menor Conv Rate',
          'Hoteles del P80 con BKGS>0 · ordenado por ConvRate ↑')
mask = (p80_hotel['Bookings']>0)
df_mc = p80_hotel[mask].sort_values('ConvRate').head(50).reset_index(drop=True)
df_mc.insert(0, 'Rk', range(1, len(df_mc)+1))
add_table(ws10, df_mc[['Rk','Hotel','CorpName','Destino','CR_Unicos','Bookings','Eficacia','ConvRate','BandaConvRate']],
          start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0'},
          banda_col='BandaConvRate')

# ==================== 11. PLAN DE ACCIÓN ====================
ws11 = wb.create_sheet('Plan de Acción')
add_title(ws11, 'Plan de Acción · W18 (CR)',
          'Acciones priorizadas · 6 acciones (2 Quick Wins + 2 Mid + 2 Estratégicas)')
plan_data = [
    {'#':'QW1','Owner':'Tech · Supply','Cluster':'Quick Win','Plazo':'5 días',
     'Acción':f'Escalar {int(sev_ef_p80.get("Súper Crítica",0))} hoteles Súper Críticos de Eficacia (P80, <60%)',
     'Métrica':'Eficacia > 85%','Detalle':'Empezar por Las Vegas Hilton at Resorts World (8,63% Eficacia)'},
    {'#':'QW2','Owner':'Tech · Account','Cluster':'Quick Win','Plazo':'1 semana',
     'Acción':'Diagnóstico técnico Top 10 Sin Conversión',
     'Métrica':'Bookings > 0','Detalle':'1.342 hoteles P80 con BKGS=0 · revisar mapping, paridad, inventario'},
    {'#':'MP1','Owner':'Comercial · Tech','Cluster':'Mid Priority','Plazo':'2 semanas',
     'Acción':'Auditar canal Third Party (ConvRate 0,29% Crítica)',
     'Métrica':'ConvRate > 0,8%','Detalle':'Revisar paridad de tarifas y velocidad de Expedia, HotelBeds Apitude'},
    {'#':'MP2','Owner':'Supply · BI','Cluster':'Mid Priority','Plazo':'3 semanas',
     'Acción':f'Plan saneamiento {int(sev_ef_p80.get("Crítica",0)+sev_ef_p80.get("Súper Crítica",0))} hoteles Crítica/Súper Crítica',
     'Métrica':f'{int((sev_ef_p80.get("Crítica",0)+sev_ef_p80.get("Súper Crítica",0))*0.5)} a Revisar',
     'Detalle':'Priorizar canasta CUG (mejor ConvRate) y B2B-OP (volumen)'},
    {'#':'ES1','Owner':'Supply · Tech · KAM','Cluster':'Estratégica','Plazo':'Q3',
     'Acción':f'Reducir cohorte Sin Conversión P80 ({int(sev_cv_p80.get("Sin Conversión",0))} hoteles)',
     'Métrica':'-25% vs baseline','Detalle':'Proyecto trimestral remediación técnica + comercial'},
    {'#':'ES2','Owner':'Producto · Pricing','Cluster':'Estratégica','Plazo':'Q3',
     'Acción':'Revisión integral producto B2C (ConvRate Crítica 0,50%)',
     'Métrica':'ConvRate > 1,5%','Detalle':'Pricing, UX, mapping, fee structure'},
]
df_plan = pd.DataFrame(plan_data)
add_table(ws11, df_plan, start_row=5)

# ==================== CANASTAS · 9 pestañas por canasta ====================
def add_canasta_sheets(wb_target, c_key, c, prefix=None):
    """Agrega las 9 pestañas de una canasta al workbook target.
    Si prefix=None, usa 'Canasta {short}' (para Excel global).
    Si prefix='', usa nombres más cortos sin prefix (para Excel solo-canasta).
    """
    short = c['short']
    p = prefix if prefix is not None else f'Canasta {short} · '
    
    # 1. Severity Eficacia
    ws_se = wb_target.create_sheet(f'{p}Sev Ef' if prefix is not None else f'Canasta {short} · Sev Ef')
    add_title(ws_se, f'Canasta {short} · Severity Eficacia',
              f'{c["name"]} · P80 · target ≥ 97%')
    sev_dict = c.get('sev_ef', {})
    total_se = int(sev_dict.sum()) if hasattr(sev_dict, 'sum') else (sum(sev_dict.values()) or 1)
    data_se = []
    for n in ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']:
        rng = {'Súper Crítica':'<60%','Crítica':'60-85%','Revisar':'85-93%','Aceptable':'93-97%','Exitosa':'≥97%'}[n]
        cnt = int(sev_dict.get(n,0))
        data_se.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total_se})
    add_table(ws_se, pd.DataFrame(data_se), start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')
    
    # 2. Severity ConvRate
    ws_sc = wb_target.create_sheet(f'{p}Sev CV' if prefix is not None else f'Canasta {short} · Sev CV')
    add_title(ws_sc, f'Canasta {short} · Severity Conv Rate',
              f'{c["name"]} · P80 · target ≥ 2,5%')
    sev_dict2 = c.get('sev_cv', {})
    total_sc = int(sev_dict2.sum()) if hasattr(sev_dict2, 'sum') else (sum(sev_dict2.values()) or 1)
    data_sc = []
    for n in ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']:
        rng = {'Sin Conversión':'BKGS=0','Crítica':'<0,8%','Revisar':'0,8-1,5%','Aceptable':'1,5-2,5%','Exitosa':'≥2,5%'}[n]
        cnt = int(sev_dict2.get(n,0))
        data_sc.append({'Banda':n,'Rango':rng,'Hoteles':cnt,'%':cnt/total_sc})
    add_table(ws_sc, pd.DataFrame(data_sc), start_row=5, num_formats={'%':'0.0%'}, banda_col='Banda')
    
    # 3. Críticos
    ws_c = wb_target.create_sheet(f'{p}Críticos' if prefix is not None else f'Canasta {short} · Críticos')
    add_title(ws_c, f'Canasta {short} · Top 50 Críticos',
              f'{c["name"]} · BKGS>0 · peor Eficacia · ordenado ↑')
    df_c = c['agg_hotel'].copy()
    mask = (df_c['Bookings']>0) & (df_c['BandaEficacia'].isin(['Crítica','Súper Crítica']))
    df_c = df_c[mask].sort_values('Eficacia').head(50).reset_index(drop=True)
    df_c.insert(0,'Rk', range(1, len(df_c)+1))
    add_table(ws_c, df_c[['Rk','Hotel','CorpName','Destino','CR_Unicos','Successful','Bookings','Eficacia','ConvRate','BandaEficacia']],
              start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
              banda_col='BandaEficacia')
    
    # 4. Bajo Rendimiento
    ws_b = wb_target.create_sheet(f'{p}BajoRend' if prefix is not None else f'Canasta {short} · BajoRend')
    add_title(ws_b, f'Canasta {short} · Top 50 Bajo Rendimiento',
              f'{c["name"]} · BKGS>0 · ConvRate Crítica/Revisar · ordenado por CR ↓')
    df_b = c['agg_hotel'].copy()
    mask = (df_b['Bookings']>0) & (df_b['BandaConvRate'].isin(['Crítica','Revisar']))
    df_b = df_b[mask].sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
    df_b.insert(0,'Rk', range(1, len(df_b)+1))
    add_table(ws_b, df_b[['Rk','Hotel','CorpName','Destino','CR_Unicos','Bookings','Eficacia','ConvRate','BandaConvRate']],
              start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0'},
              banda_col='BandaConvRate')
    
    # 5. Sin Conversión
    ws_sn = wb_target.create_sheet(f'{p}Sin Conv' if prefix is not None else f'Canasta {short} · Sin Conv')
    add_title(ws_sn, f'Canasta {short} · Top 50 Sin Conversión',
              f'{c["name"]} · BKGS=0 · ordenado por CR ↓ · cohorte estructural')
    df_sn = c['agg_hotel'].copy()
    df_sn = df_sn[df_sn['Bookings']==0].sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
    df_sn.insert(0,'Rk', range(1, len(df_sn)+1))
    add_table(ws_sn, df_sn[['Rk','Hotel','CorpName','Destino','CR_Unicos','Successful','Bookings','Eficacia','BandaEficacia']],
              start_row=5, num_formats={'Eficacia':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
              banda_col='BandaEficacia')
    
    # 6. Por Corporativo
    ws_co = wb_target.create_sheet(f'{p}Por Corp' if prefix is not None else f'Canasta {short} · Por Corp')
    add_title(ws_co, f'Canasta {short} · Por Corporativo',
              f'{c["name"]} · Top 50 corp · ordenado por CR únicos ↓')
    df_co = c['agg_corp'].copy().sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
    df_co.insert(0,'Rk', range(1, len(df_co)+1))
    cols_co = [col for col in ['Rk','CorpName','CR_Unicos','Successful','Bookings','Eficacia','ConvRate','BandaEficacia','BandaConvRate'] if col in df_co.columns]
    add_table(ws_co, df_co[cols_co], start_row=5,
              num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
              banda_col='BandaEficacia')
    
    # 7. Por Destino
    ws_de = wb_target.create_sheet(f'{p}Por Destino' if prefix is not None else f'Canasta {short} · Por Destino')
    add_title(ws_de, f'Canasta {short} · Por Destino',
              f'{c["name"]} · Top 50 destinos · ordenado por CR únicos ↓')
    df_de = c['agg_destino'].copy().sort_values('CR_Unicos', ascending=False).head(50).reset_index(drop=True)
    df_de.insert(0,'Rk', range(1, len(df_de)+1))
    cols_de = [col for col in ['Rk','Destino','CR_Unicos','Successful','Bookings','Eficacia','ConvRate','BandaEficacia','BandaConvRate'] if col in df_de.columns]
    add_table(ws_de, df_de[cols_de], start_row=5,
              num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
              banda_col='BandaEficacia')
    
    # 8. Por Channel
    ws_ch = wb_target.create_sheet(f'{p}Por Channel' if prefix is not None else f'Canasta {short} · Por Channel')
    add_title(ws_ch, f'Canasta {short} · Por Channel',
              f'{c["name"]} · todos los channels · ordenado por CR únicos ↓')
    df_ch = c['agg_channel'].copy().sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    df_ch.insert(0,'Rk', range(1, len(df_ch)+1))
    cols_ch = [col for col in ['Rk','ExternalProviderName','CR_Unicos','Successful','Bookings','Eficacia','ConvRate','BandaEficacia','BandaConvRate'] if col in df_ch.columns]
    add_table(ws_ch, df_ch[cols_ch], start_row=5,
              num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0','Successful':'#,##0'},
              banda_col='BandaEficacia')
    
    # 9. Menor Conv Rate
    ws_mc = wb_target.create_sheet(f'{p}Menor CR' if prefix is not None else f'Canasta {short} · Menor CR')
    add_title(ws_mc, f'Canasta {short} · Top 50 Menor Conv Rate',
              f'{c["name"]} · BKGS>0 · peor ConvRate · ordenado ↑')
    df_mc = c['agg_hotel'].copy()
    df_mc = df_mc[df_mc['Bookings']>0].sort_values('ConvRate').head(50).reset_index(drop=True)
    df_mc.insert(0,'Rk', range(1, len(df_mc)+1))
    add_table(ws_mc, df_mc[['Rk','Hotel','CorpName','Destino','CR_Unicos','Bookings','Eficacia','ConvRate','BandaConvRate']],
              start_row=5, num_formats={'Eficacia':'0.00%','ConvRate':'0.00%','CR_Unicos':'#,##0','Bookings':'#,##0'},
              banda_col='BandaConvRate')

# Agregar pestañas al Excel global
for c_key in ['B2C','B2B-OP','CUG']:
    add_canasta_sheets(wb, c_key, CANASTA[c_key])

# Save Excel global
out = '/mnt/user-data/outputs/Analisis_CheckRates_W18.xlsx'
wb.save(out)
print(f'Excel CR escrito: {out}')
print(f'Pestañas: {len(wb.sheetnames)}')

# === Generar 3 Excels solo-canasta ===
from openpyxl import Workbook as WB2
canasta_filename = {'B2C':'B2C','B2B-OP':'OP','CUG':'CUG'}
for c_key in ['B2C','B2B-OP','CUG']:
    wb_c = WB2()
    wb_c.remove(wb_c.active)  # Sacar Sheet por default
    add_canasta_sheets(wb_c, c_key, CANASTA[c_key], prefix='')
    out_c = f'/mnt/user-data/outputs/Analisis_CheckRates_{canasta_filename[c_key]}_W18.xlsx'
    wb_c.save(out_c)
    print(f'  ✓ Excel canasta {canasta_filename[c_key]}: {len(wb_c.sheetnames)} pestañas')
for s in wb.sheetnames: print(f'  - {s}')
