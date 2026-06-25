"""
excel_rnd.py · W26+ · Excel Rates No Dispo — estructura simplificada
5 hojas: Maestra | Críticos | Bajo Rendimiento | Sin Conversión | Severity

Maestra: una fila por Hotel × Canasta (4 canastas) con todas las columnas filtrables
         Métricas: %NoDispo + WoW ND + Banda ND + %Conv + WoW CV + Bookings + Tráfico
Bandas: nivel hotel Global, banda por %NoDispo (métrica primaria)
        Columnas extra de exposición: banda del hotel en cada canasta (B2C / Opaco / Ultra Opaco)
IPM eliminado — no se reporta en ninguna hoja (W26+)
"""
import pickle, os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from engine import banda_nodispo, banda_convrate

VOL_NUM = os.getenv('VOL_NUM', '21')
PERIODO = os.getenv('PERIODO', '19-25 mayo 2026')
OUTPUTS = os.getenv('OUTPUTS_DIR', '/mnt/user-data/outputs')

with open(os.getenv('PICKLE_RND', f'rnd_w{VOL_NUM}_data.pkl'), 'rb') as f:
    D = pickle.load(f)

TAB_ND  = D['TAB_NoDispo']
CANASTA = D['CANASTA']
M       = D['M']

RND = 'EA0074'

# ── Estilos ───────────────────────────────────────────────────────────────────
def fill(c): return PatternFill(start_color=c, end_color=c, fill_type='solid')
def fnt(c='000000', sz=10, bold=False, white=False):
    return Font(name='Arial', size=sz, bold=bold, color='FFFFFF' if white else c)
T  = Side(border_style='thin', color='CCCCCC')
BD = Border(left=T, right=T, top=T, bottom=T)

BFILL = {
    'Exitosa':       fill('1A6B4A'), 'Aceptable':     fill('FBBF24'),
    'Revisar':       fill('F97316'), 'Crítica':        fill('C0392B'),
    'Súper Crítica': fill('2D2828'), 'Sin Conversión': fill('8A8377'),
}
BFONT = {
    'Exitosa':       fnt(white=True, bold=True), 'Aceptable':     fnt(white=True, bold=True),
    'Revisar':       fnt(white=True, bold=True), 'Crítica':        fnt(white=True, bold=True),
    'Súper Crítica': fnt(white=True, bold=True), 'Sin Conversión': fnt(white=True, bold=True),
}
WOW_UP   = fill('EAF3DE'); WOW_UP_F   = fnt('2F6C34', bold=True)
WOW_DN   = fill('FCE8E6'); WOW_DN_F   = fnt('C0392B', bold=True)
WOW_NEU  = fill('F2EEE6'); WOW_NEU_F  = fnt('8A8377', bold=True)

def sf(v):
    try: f = float(v); return None if pd.isna(f) else f
    except: return None

def title(ws, t, sub=''):
    ws.cell(1, 1, t).font = fnt(RND, 13, True)
    if sub: ws.cell(2, 1, sub).font = fnt('666666')

def mk_hdr(ws, row, cols):
    for c, lbl in enumerate(cols, 1):
        cell = ws.cell(row, c, lbl)
        cell.font = fnt(white=True, bold=True)
        cell.fill = fill(RND)
        cell.alignment = Alignment(horizontal='center')
        cell.border = BD
    ws.auto_filter.ref = f'A{row}:{get_column_letter(len(cols))}{row}'
    return row + 1

def mk_cell(ws, row, col, val, banda=None, is_sev=False, align='center', fmt=None):
    cell = ws.cell(row, col, val)
    cell.font = Font(name='Arial', size=10)
    cell.border = BD
    cell.alignment = Alignment(horizontal=align)
    if fmt: cell.number_format = fmt
    if is_sev and banda and banda in BFILL:
        cell.fill = BFILL[banda]
        cell.font = BFONT[banda]

def apply_wow(ws, row, col, val_pp, invert=False):
    cell = ws.cell(row, col)
    if val_pp is None or (isinstance(val_pp, float) and pd.isna(val_pp)):
        cell.value = '—'; cell.font = WOW_NEU_F; cell.fill = WOW_NEU
        cell.border = BD; cell.alignment = Alignment(horizontal='center'); return
    is_up = float(val_pp) >= 0
    is_good = (is_up and not invert) or (not is_up and invert)
    s = '▲' if is_up else '▼'
    cell.value = f'{s}{abs(round(float(val_pp), 2))}'.replace('.', ',')
    cell.fill = WOW_UP if is_good else WOW_DN
    cell.font = WOW_UP_F if is_good else WOW_DN_F
    cell.border = BD; cell.alignment = Alignment(horizontal='center')

def autofit(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ── Fuentes de datos por canasta ──────────────────────────────────────────────
CANASTAS_DEF = [
    ('global', 'Global',      None),
    ('b2c',    'B2C',         'B2C'),
    ('op',     'Opaco',       'B2B-OP'),
    ('cug',    'Ultra Opaco', 'CUG'),
]

def hotel_src(can_id):
    """df hotel de la canasta (con %NoDispo, Bookings, Trafico, WoW)."""
    if can_id is None:
        return D.get('p80_hotel', pd.DataFrame())
    can = CANASTA.get(can_id, {})
    src = can.get('p80_hotel')
    if src is None:
        src = can.get('p80')
    return src if src is not None else TAB_ND.get('hotel', pd.DataFrame())

def get_banda_hotel(hotel_name, can_id):
    """Banda %NoDispo de un hotel en una canasta específica."""
    df = hotel_src(can_id)
    if df is None or len(df) == 0: return '—'
    row = df[df['Hotel'] == hotel_name]
    if len(row) == 0: return '—'
    nd = sf(row.iloc[0].get('%NoDispo'))
    return banda_nodispo(nd) if nd is not None else '—'

# ── Hoja Maestra ──────────────────────────────────────────────────────────────
MAESTRA_COLS = [
    'País', 'Destino', 'Corporativo', 'Hotel',
    'Canasta', 'Tráfico', 'WoW Tráfico', '%NoDispo', 'WoW ND', 'Banda ND',
    '%Conv', 'WoW CV', 'Bookings'
]

def write_maestra(ws):
    title(ws, f'Maestra RND · Rates No Dispo W{VOL_NUM}',
          f'Una fila por Hotel × Canasta · {PERIODO} · Filtrar por cualquier columna')
    r = mk_hdr(ws, 4, MAESTRA_COLS)

    for can_key, can_label, can_id in CANASTAS_DEF:
        df = hotel_src(can_id)
        if df is None or len(df) == 0: continue
        df = df.copy()
        for _, row in df.iterrows():
            nd  = sf(row.get('%NoDispo'))
            bk  = int(sf(row.get('Bookings')) or 0)
            trf = int(sf(row.get('Trafico')) or 0)
            wow_nd = sf(row.get('NoDispo_WoW_pp'))
            # Conv = Bookings / Trafico
            conv = bk / trf if trf > 0 else None
            wow_cv = sf(row.get('ConvRate_WoW_pp') if 'ConvRate_WoW_pp' in row.index else None)
            bnd_nd = banda_nodispo(nd) if nd is not None else '—'

            pais    = str(row.get('PaisDestino', row.get('Pais', '—')))
            destino = str(row.get('Destino', '—'))
            corp    = str(row.get('CorpName', row.get('Corp', '—')))
            hotel   = str(row.get('Hotel', '—'))

            # Col 1-4: dimensiones (left-aligned)
            for ci, val in enumerate([pais, destino, corp, hotel], 1):
                mk_cell(ws, r, ci, val, align='left')
            # Col 5: Canasta
            mk_cell(ws, r, 5, can_label)
            # Col 6: Tráfico
            mk_cell(ws, r, 6, trf)
            # Col 7: WoW Tráfico
            apply_wow(ws, r, 7, sf(row.get('Trafico_WoW_pct')), invert=False)
            # Col 8: %NoDispo
            c = ws.cell(r, 8, round(nd, 4) if nd is not None else None)
            c.border = BD; c.alignment = Alignment(horizontal='center')
            if nd is not None: ws.cell(r, 8).number_format = '0.00%'
            # Col 9: WoW ND
            apply_wow(ws, r, 9, wow_nd, invert=True)
            # Col 10: Banda ND (coloreada)
            mk_cell(ws, r, 10, bnd_nd, bnd_nd, is_sev=True)
            # Col 11: %Conv
            c2 = ws.cell(r, 11, round(conv, 4) if conv is not None else None)
            c2.border = BD; c2.alignment = Alignment(horizontal='center')
            if conv is not None: ws.cell(r, 11).number_format = '0.00%'
            # Col 12: WoW CV
            apply_wow(ws, r, 12, wow_cv, invert=False)
            # Col 13: Bookings
            mk_cell(ws, r, 13, bk)
            r += 1

    autofit(ws, [16, 22, 22, 40, 14, 10, 10, 10, 10, 18, 10, 10, 10])

# ── Hojas de banda (Críticos / Bajo Rendimiento / Sin Conversión) ─────────────
# Una fila por hotel Global. Columnas de exposición cruzada por canasta.
BANDA_COLS = [
    'País', 'Destino', 'Corporativo', 'Hotel',
    'Tráfico', '%NoDispo', 'WoW ND', '%Conv', 'WoW CV', 'Bookings',
    'Banda Global', 'B2C', 'Opaco', 'Ultra Opaco'
]

def band_split_nd(df):
    empty = pd.DataFrame()
    if df is None or len(df) == 0: return empty, empty, empty
    d = df.copy().reset_index(drop=True)
    bk   = d['Bookings'].fillna(0) if 'Bookings' in d.columns else pd.Series(0, index=d.index)
    bcol = d['%NoDispo'].apply(lambda v: banda_nodispo(sf(v)) if sf(v) is not None else '—')
    crit = d[(bk > 0) & bcol.isin(['Crítica', 'Súper Crítica'])]
    bajo = d[(bk > 0) & bcol.isin(['Revisar', 'Aceptable'])]
    sinc = d[bk == 0]
    return crit.reset_index(drop=True), bajo.reset_index(drop=True), sinc.reset_index(drop=True)

# Construir lookup de banda por hotel × canasta (para columnas de exposición)
def build_banda_lookup():
    """Devuelve dict: {hotel_name: {can_label: banda_str}}"""
    lookup = {}
    for can_key, can_label, can_id in CANASTAS_DEF:
        if can_id is None: continue  # Global no va en exposición cruzada
        df = hotel_src(can_id)
        if df is None or len(df) == 0: continue
        for _, row in df.iterrows():
            h = str(row.get('Hotel', ''))
            nd = sf(row.get('%NoDispo'))
            b = banda_nodispo(nd) if nd is not None else '—'
            if h not in lookup: lookup[h] = {}
            lookup[h][can_label] = b
    return lookup

def write_banda(ws, df_banda, sheet_title, banda_lookup):
    title(ws, sheet_title,
          f'Hoteles Global · banda por %NoDispo · {PERIODO} · Top 500')
    if df_banda is None or len(df_banda) == 0:
        ws.cell(4, 1, 'Sin datos'); return

    df_s = df_banda.sort_values('%NoDispo', ascending=False).head(500)
    r = mk_hdr(ws, 4, BANDA_COLS)

    for _, row in df_s.iterrows():
        nd   = sf(row.get('%NoDispo'))
        bk   = int(sf(row.get('Bookings')) or 0)
        trf  = int(sf(row.get('Trafico')) or 0)
        conv = bk / trf if trf > 0 else None
        wow_nd = sf(row.get('NoDispo_WoW_pp'))
        wow_cv = sf(row.get('ConvRate_WoW_pp') if 'ConvRate_WoW_pp' in row.index else None)
        bnd_g  = banda_nodispo(nd) if nd is not None else '—'
        hotel  = str(row.get('Hotel', '—'))

        region  = str(row.get('Region', row.get('Region_display', '—')))
        pais    = str(row.get('PaisDestino', row.get('Pais', '—')))
        destino = str(row.get('Destino', '—'))
        corp    = str(row.get('CorpName', row.get('Corp', '—')))

        # Exposición cruzada
        b2c = banda_lookup.get(hotel, {}).get('B2C', '—')
        op  = banda_lookup.get(hotel, {}).get('Opaco', '—')
        cug = banda_lookup.get(hotel, {}).get('Ultra Opaco', '—')

        for ci, val in enumerate([region, pais, destino, corp, hotel], 1):
            mk_cell(ws, r, ci, val, align='left')
        mk_cell(ws, r, 5, trf)
        c = ws.cell(r, 6, round(nd, 4) if nd is not None else None)
        c.border = BD; c.alignment = Alignment(horizontal='center')
        if nd is not None: ws.cell(r, 6).number_format = '0.00%'
        apply_wow(ws, r, 7, wow_nd, invert=True)
        c2 = ws.cell(r, 8, round(conv, 4) if conv is not None else None)
        c2.border = BD; c2.alignment = Alignment(horizontal='center')
        if conv is not None: ws.cell(r, 8).number_format = '0.00%'
        apply_wow(ws, r, 9, wow_cv, invert=False)
        mk_cell(ws, r, 10, bk)
        mk_cell(ws, r, 11, bnd_g, bnd_g, is_sev=True)
        mk_cell(ws, r, 12, b2c,  b2c,  is_sev=True)
        mk_cell(ws, r, 13, op,   op,   is_sev=True)
        mk_cell(ws, r, 14, cug,  cug,  is_sev=True)
        r += 1

    autofit(ws, [16, 22, 22, 40, 10, 10, 10, 10, 10, 10, 18, 14, 14, 14])

# ── Hoja Severity ─────────────────────────────────────────────────────────────
def write_severity(ws):
    title(ws, f'Severity RND W{VOL_NUM}', f'Resumen ejecutivo por Destino y Corporativo · {PERIODO}')
    m_curr = M.get(f'global_w{VOL_NUM}', M.get('global_w21', {}))
    m_prev = M.get(f'global_w{int(VOL_NUM)-1}', M.get('global_w20', {}))

    r = 4
    # KPI Global
    nd_curr = m_curr.get('pct_nodispo', 0); nd_prev = m_prev.get('pct_nodispo', 0)
    nd_wow  = (nd_curr - nd_prev) * 100 if nd_prev else None
    ws.cell(r, 1, 'KPI Global').font = fnt(RND, 11, True); r += 1
    r = mk_hdr(ws, r, ['Métrica', f'W{int(VOL_NUM)-1}', f'W{VOL_NUM}', 'WoW'])
    ws.cell(r, 1, '%NoDispo').font = Font(name='Arial', size=10, bold=True)
    ws.cell(r, 1).border = BD
    ws.cell(r, 2, round(nd_prev, 4) if nd_prev else None).border = BD
    ws.cell(r, 2).number_format = '0.00%'; ws.cell(r, 2).alignment = Alignment(horizontal='center')
    ws.cell(r, 3, round(nd_curr, 4) if nd_curr else None).border = BD
    ws.cell(r, 3).number_format = '0.00%'; ws.cell(r, 3).alignment = Alignment(horizontal='center')
    apply_wow(ws, r, 4, nd_wow, invert=True); r += 2

    # Severity por distribución
    df_hotel = D.get('p80_hotel', pd.DataFrame())
    sev_nd = {}
    for _, row in df_hotel.iterrows():
        nd = sf(row.get('%NoDispo'))
        if nd is not None:
            b = banda_nodispo(nd); sev_nd[b] = sev_nd.get(b, 0) + 1
    total = sum(sev_nd.values()) or 1

    ws.cell(r, 1, 'Severity %NoDispo · Hoteles Global').font = fnt(RND, 11, True); r += 1
    r = mk_hdr(ws, r, ['Severity', 'Hoteles', '% del Total'])
    for b in ['Exitosa', 'Aceptable', 'Revisar', 'Crítica', 'Súper Crítica']:
        n = sev_nd.get(b, 0)
        mk_cell(ws, r, 1, b, b, is_sev=True, align='center')
        ws.cell(r, 1).border = BD
        ws.cell(r, 2, n).border = BD; ws.cell(r, 2).alignment = Alignment(horizontal='center')
        ws.cell(r, 3, round(n/total, 4)).number_format = '0.0%'
        ws.cell(r, 3).border = BD; ws.cell(r, 3).alignment = Alignment(horizontal='center')
        r += 1
    r += 1

    # Top Destinos por %NoDispo
    df_dest = TAB_ND.get('destino', pd.DataFrame())
    if df_dest is not None and len(df_dest) > 0:
        ws.cell(r, 1, 'Top Destinos · %NoDispo DESC').font = fnt(RND, 11, True); r += 1
        r = mk_hdr(ws, r, ['Destino', 'Banda', 'Tráfico', '%NoDispo', 'WoW ND', '%Conv', 'Bookings'])
        for _, row in df_dest.sort_values('%NoDispo', ascending=False).head(30).iterrows():
            nd  = sf(row.get('%NoDispo'))
            bk  = int(sf(row.get('Bookings')) or 0)
            trf = int(sf(row.get('Trafico')) or 0)
            conv = bk / trf if trf > 0 else None
            bnd = banda_nodispo(nd) if nd is not None else '—'
            mk_cell(ws, r, 1, str(row.get('Destino', '—')), align='left')
            mk_cell(ws, r, 2, bnd, bnd, is_sev=True)
            mk_cell(ws, r, 3, trf)
            c = ws.cell(r, 4, round(nd, 4) if nd is not None else None)
            c.border = BD; c.alignment = Alignment(horizontal='center')
            if nd is not None: ws.cell(r, 4).number_format = '0.00%'
            apply_wow(ws, r, 5, sf(row.get('NoDispo_WoW_pp')), invert=True)
            c2 = ws.cell(r, 6, round(conv, 4) if conv is not None else None)
            c2.border = BD; c2.alignment = Alignment(horizontal='center')
            if conv is not None: ws.cell(r, 6).number_format = '0.00%'
            mk_cell(ws, r, 7, bk)
            r += 1
        r += 1

    # Top Corp por %NoDispo
    df_corp = TAB_ND.get('corp', pd.DataFrame())
    if df_corp is not None and len(df_corp) > 0:
        ws.cell(r, 1, 'Top Corporativos · %NoDispo DESC').font = fnt(RND, 11, True); r += 1
        r = mk_hdr(ws, r, ['Corporativo', 'Banda', 'Tráfico', '%NoDispo', 'WoW ND', '%Conv', 'Bookings'])
        for _, row in df_corp.sort_values('%NoDispo', ascending=False).head(30).iterrows():
            nd  = sf(row.get('%NoDispo'))
            bk  = int(sf(row.get('Bookings')) or 0)
            trf = int(sf(row.get('Trafico')) or 0)
            conv = bk / trf if trf > 0 else None
            bnd = banda_nodispo(nd) if nd is not None else '—'
            mk_cell(ws, r, 1, str(row.get('CorpName', '—')), align='left')
            mk_cell(ws, r, 2, bnd, bnd, is_sev=True)
            mk_cell(ws, r, 3, trf)
            c = ws.cell(r, 4, round(nd, 4) if nd is not None else None)
            c.border = BD; c.alignment = Alignment(horizontal='center')
            if nd is not None: ws.cell(r, 4).number_format = '0.00%'
            apply_wow(ws, r, 5, sf(row.get('NoDispo_WoW_pp')), invert=True)
            c2 = ws.cell(r, 6, round(conv, 4) if conv is not None else None)
            c2.border = BD; c2.alignment = Alignment(horizontal='center')
            if conv is not None: ws.cell(r, 6).number_format = '0.00%'
            mk_cell(ws, r, 7, bk)
            r += 1

    autofit(ws, [28, 18, 12, 10, 10, 10, 10])

# ── Build workbook ────────────────────────────────────────────────────────────
wb = Workbook(); wb.remove(wb.active)
banda_lookup = build_banda_lookup()
df_global = hotel_src(None)
crit, bajo, sinc = band_split_nd(df_global)

ws = wb.create_sheet('Maestra'); ws.sheet_properties.tabColor = RND
write_maestra(ws)

ws = wb.create_sheet('Críticos'); ws.sheet_properties.tabColor = 'C0392B'
write_banda(ws, crit, f'Críticos · RND W{VOL_NUM}', banda_lookup)

ws = wb.create_sheet('Bajo Rendimiento'); ws.sheet_properties.tabColor = 'F97316'
write_banda(ws, bajo, f'Bajo Rendimiento · RND W{VOL_NUM}', banda_lookup)

ws = wb.create_sheet('Sin Conversión'); ws.sheet_properties.tabColor = '8A8377'
write_banda(ws, sinc, f'Sin Conversión · RND W{VOL_NUM}', banda_lookup)

ws = wb.create_sheet('Severity'); ws.sheet_properties.tabColor = RND
write_severity(ws)

out = f'{OUTPUTS}/Analisis_RatesNoDispo_W{VOL_NUM}.xlsx'
wb.save(out)
print(f'✅ Excel RND: {out}')
print(f'   {len(wb.sheetnames)} hojas: {" | ".join(wb.sheetnames)}')
