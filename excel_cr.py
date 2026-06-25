"""
excel_cr.py · W26+ · Excel CheckRates — estructura simplificada
5 hojas: Maestra | Críticos | Bajo Rendimiento | Sin Conversión | Severity

Maestra: una fila por Hotel × Canasta (4 canastas) con todas las columnas filtrables
         Métricas: Eficacia + WoW Ef + Banda Ef + ConvRate + WoW CV + Bookability + Bookings
Bandas: nivel hotel Global, banda por Eficacia (métrica primaria)
        Columnas extra de exposición: banda del hotel en cada canasta (B2C / Opaco / Ultra Opaco)
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
M       = D['M']
p80_all = D['p80_hotel'].copy()
hcm     = D.get('hotel_channel_map', {})

# Bookability del pickle BK si está disponible
try:
    import pickle as _pkl
    _bk_path = os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
    with open(_bk_path, 'rb') as _f:
        _BK = _pkl.load(_f)
    BK_HOTEL = _BK.get('BK_HOTEL', {})   # {hotel: {canasta: bk_pct}}
except Exception:
    BK_HOTEL = {}

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
    ws.cell(1, 1, t).font = fnt(CR, 13, True)
    if sub: ws.cell(2, 1, sub).font = fnt('666666')

def mk_hdr(ws, row, cols):
    for c, lbl in enumerate(cols, 1):
        cell = ws.cell(row, c, lbl)
        cell.font = fnt(white=True, bold=True)
        cell.fill = fill(CR)
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

def fmt_pct(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    return round(float(v), 4)

# ── Fuentes de datos por canasta ──────────────────────────────────────────────
CANASTAS_DEF = [
    ('global', 'Global',      None,     None),
    ('b2c',    'B2C',         'B2C',    'B2C'),
    ('op',     'Opaco',       'B2B-OP', 'B2B-OP'),
    ('cug',    'Ultra Opaco', 'CUG',    'CUG'),
]

def hotel_src_cr(can_id):
    """df hotel de la canasta con Eficacia, ConvRate, Bookings, Channel."""
    if can_id is None:
        df = p80_all.copy()
    elif 'DistributionCategory' in p80_all.columns:
        df = p80_all[p80_all['DistributionCategory'] == can_id].copy()
    else:
        can = CANASTA.get(can_id, {})
        df = (can.get('p80_hotel') or can.get('p80') or p80_all).copy()
    if 'Channel' not in df.columns and 'Hotel' in df.columns:
        df['Hotel_c'] = df['Hotel'].apply(clean)
        df['Channel'] = df['Hotel_c'].map(hcm_clean).fillna('—')
    return df

def get_bk_hotel(hotel_name, can_label):
    """Bookability de un hotel en una canasta (del pickle BK si está disponible)."""
    h = BK_HOTEL.get(hotel_name, {})
    if h:
        return h.get(can_label, h.get('Global', None))
    return None

# ── Hoja Maestra ──────────────────────────────────────────────────────────────
MAESTRA_COLS = [
    'Destino', 'Corporativo', 'Hotel', 'Channel', 'Canasta',
    'CR Únicos', 'WoW CR', 'Eficacia', 'WoW Ef', 'Banda Ef',
    'Conv Rate', 'WoW CV', 'Bookability', 'Bookings'
]

def write_maestra(ws):
    title(ws, f'Maestra CR · CheckRates W{VOL_NUM}',
          f'Una fila por Hotel × Canasta · {PERIODO} · Filtrar por cualquier columna')
    r = mk_hdr(ws, 4, MAESTRA_COLS)

    for can_key, can_label, can_id, can_dist in CANASTAS_DEF:
        df = hotel_src_cr(can_dist)
        if df is None or len(df) == 0: continue

        for _, row in df.iterrows():
            ef   = fmt_pct(row.get('Eficacia'))
            cv   = fmt_pct(row.get('ConvRate'))
            bk   = int(row.get('Bookings', 0)) if pd.notna(row.get('Bookings', 0)) else 0
            cru  = int(row.get('CR_Unicos', 0)) if pd.notna(row.get('CR_Unicos', 0)) else 0
            bef  = banda_eficacia(ef) if ef is not None else '—'
            bcv  = banda_convrate(cv, bk) if cv is not None else '—'
            hotel   = clean(str(row.get('Hotel', '—')))
            channel = str(row.get('Channel', '—'))
            destino = str(row.get('Destino', '—'))
            corp    = str(row.get('CorpName', row.get('Corp', '—')))
            bk_pct  = get_bk_hotel(hotel, can_label)

            # Cols 1-5: dimensiones
            for ci, val in enumerate([destino, corp, hotel, channel, can_label], 1):
                mk_cell(ws, r, ci, val, align='left')
            # Col 6: CR Únicos
            mk_cell(ws, r, 6, cru)
            # Col 7: WoW CR
            apply_wow(ws, r, 7, sf(row.get('CR_WoW_pct')), invert=False)
            # Col 8: Eficacia
            c = ws.cell(r, 8, ef)
            c.border = BD; c.alignment = Alignment(horizontal='center')
            if ef is not None: ws.cell(r, 8).number_format = '0.00%'
            # Col 9: WoW Ef
            apply_wow(ws, r, 9, sf(row.get('Eficacia_WoW_pp')), invert=False)
            # Col 10: Banda Ef (coloreada)
            mk_cell(ws, r, 10, bef, bef, is_sev=True)
            # Col 11: Conv Rate
            c2 = ws.cell(r, 11, cv)
            c2.border = BD; c2.alignment = Alignment(horizontal='center')
            if cv is not None: ws.cell(r, 11).number_format = '0.00%'
            # Col 12: WoW CV
            apply_wow(ws, r, 12, sf(row.get('ConvRate_WoW_pp')), invert=False)
            # Col 13: Bookability
            c3 = ws.cell(r, 13, round(bk_pct, 4) if bk_pct is not None else None)
            c3.border = BD; c3.alignment = Alignment(horizontal='center')
            if bk_pct is not None: ws.cell(r, 13).number_format = '0.00%'
            # Col 14: Bookings
            mk_cell(ws, r, 14, bk)
            r += 1

    autofit(ws, [22, 22, 40, 18, 14, 10, 10, 10, 10, 18, 10, 10, 10, 10])

# ── Hojas de banda (Críticos / Bajo Rendimiento / Sin Conversión) ─────────────
BANDA_COLS = [
    'Destino', 'Corporativo', 'Hotel', 'Channel',
    'CR Únicos', 'Eficacia', 'WoW Ef', 'Conv Rate', 'WoW CV',
    'Bookability', 'Bookings',
    'Banda Global', 'B2C', 'Opaco', 'Ultra Opaco'
]

def band_split_ef(df):
    empty = pd.DataFrame()
    if df is None or len(df) == 0: return empty, empty, empty
    d = df.copy().reset_index(drop=True)
    bk   = d['Bookings'].fillna(0) if 'Bookings' in d.columns else pd.Series(0, index=d.index)
    bcol = d['Eficacia'].apply(
        lambda v: banda_eficacia(round(float(v), 4)) if pd.notna(v) else '—'
    )
    crit = d[(bk > 0) & bcol.isin(['Crítica', 'Súper Crítica'])]
    bajo = d[(bk > 0) & bcol.isin(['Revisar', 'Aceptable'])]
    sinc = d[bk == 0]
    return crit.reset_index(drop=True), bajo.reset_index(drop=True), sinc.reset_index(drop=True)

def build_banda_lookup_cr():
    """dict: {hotel_name: {can_label: banda_ef}}"""
    lookup = {}
    for can_key, can_label, can_id, can_dist in CANASTAS_DEF:
        if can_dist is None: continue
        df = hotel_src_cr(can_dist)
        if df is None or len(df) == 0: continue
        for _, row in df.iterrows():
            h  = clean(str(row.get('Hotel', '')))
            ef = fmt_pct(row.get('Eficacia'))
            b  = banda_eficacia(ef) if ef is not None else '—'
            if h not in lookup: lookup[h] = {}
            lookup[h][can_label] = b
    return lookup

def write_banda(ws, df_banda, sheet_title, banda_lookup):
    title(ws, sheet_title,
          f'Hoteles Global · banda por Eficacia · {PERIODO} · Top 500')
    if df_banda is None or len(df_banda) == 0:
        ws.cell(4, 1, 'Sin datos'); return

    df_s = df_banda.sort_values('Eficacia', ascending=True).head(500)
    r = mk_hdr(ws, 4, BANDA_COLS)

    # Merge ConvRate_WoW_pp si no está
    tab_cv_g = TAB_CV.get('global', {})
    if 'ConvRate_WoW_pp' not in df_s.columns and tab_cv_g.get('hotel') is not None:
        df_s = df_s.merge(
            tab_cv_g['hotel'][['Hotel', 'ConvRate_WoW_pp']], on='Hotel', how='left'
        )

    for _, row in df_s.iterrows():
        ef   = fmt_pct(row.get('Eficacia'))
        cv   = fmt_pct(row.get('ConvRate'))
        bk   = int(row.get('Bookings', 0)) if pd.notna(row.get('Bookings', 0)) else 0
        cru  = int(row.get('CR_Unicos', 0)) if pd.notna(row.get('CR_Unicos', 0)) else 0
        bef  = banda_eficacia(ef) if ef is not None else '—'
        hotel   = clean(str(row.get('Hotel', '—')))
        channel = str(row.get('Channel', '—'))
        destino = str(row.get('Destino', '—'))
        corp    = str(row.get('CorpName', row.get('Corp', '—')))
        bk_pct  = get_bk_hotel(hotel, 'Global')

        # Exposición cruzada
        b2c = banda_lookup.get(hotel, {}).get('B2C', '—')
        op  = banda_lookup.get(hotel, {}).get('Opaco', '—')
        cug = banda_lookup.get(hotel, {}).get('Ultra Opaco', '—')

        for ci, val in enumerate([destino, corp, hotel, channel], 1):
            mk_cell(ws, r, ci, val, align='left')
        mk_cell(ws, r, 5, cru)
        c = ws.cell(r, 6, ef)
        c.border = BD; c.alignment = Alignment(horizontal='center')
        if ef is not None: ws.cell(r, 6).number_format = '0.00%'
        apply_wow(ws, r, 7, sf(row.get('Eficacia_WoW_pp')), invert=False)
        c2 = ws.cell(r, 8, cv)
        c2.border = BD; c2.alignment = Alignment(horizontal='center')
        if cv is not None: ws.cell(r, 8).number_format = '0.00%'
        apply_wow(ws, r, 9, sf(row.get('ConvRate_WoW_pp')), invert=False)
        c3 = ws.cell(r, 10, round(bk_pct, 4) if bk_pct is not None else None)
        c3.border = BD; c3.alignment = Alignment(horizontal='center')
        if bk_pct is not None: ws.cell(r, 10).number_format = '0.00%'
        mk_cell(ws, r, 11, bk)
        mk_cell(ws, r, 12, bef, bef, is_sev=True)
        mk_cell(ws, r, 13, b2c, b2c, is_sev=True)
        mk_cell(ws, r, 14, op,  op,  is_sev=True)
        mk_cell(ws, r, 15, cug, cug, is_sev=True)
        r += 1

    autofit(ws, [22, 22, 40, 18, 10, 10, 10, 10, 10, 10, 10, 18, 14, 14, 14])

# ── Hoja Severity ─────────────────────────────────────────────────────────────
def write_severity(ws):
    title(ws, f'Severity CR W{VOL_NUM}', f'Resumen ejecutivo por Destino, Corporativo y Channel · {PERIODO}')
    m_curr = M.get(f'global_w{VOL_NUM}', M.get('global_w21', {}))
    m_prev = M.get(f'global_w{int(VOL_NUM)-1}', M.get('global_w20', {}))

    ef_curr = m_curr.get('eficacia', 0); ef_prev = m_prev.get('eficacia', 0)
    cv_curr = m_curr.get('conv_rate', 0); cv_prev = m_prev.get('conv_rate', 0)
    ef_wow  = (ef_curr - ef_prev) * 100 if ef_prev else None
    cv_wow  = (cv_curr - cv_prev) * 100 if cv_prev else None

    r = 4
    ws.cell(r, 1, 'KPI Global').font = fnt(CR, 11, True); r += 1
    r = mk_hdr(ws, r, ['Métrica', f'W{int(VOL_NUM)-1}', f'W{VOL_NUM}', 'WoW'])
    for label, prev, curr, wow in [
        ('Eficacia', ef_prev, ef_curr, ef_wow),
        ('Conv Rate', cv_prev, cv_curr, cv_wow),
    ]:
        ws.cell(r, 1, label).font = Font(name='Arial', size=10, bold=True)
        ws.cell(r, 1).border = BD
        ws.cell(r, 2, round(prev, 4) if prev else None).border = BD
        ws.cell(r, 3, round(curr, 4) if curr else None).border = BD
        ws.cell(r, 2).number_format = '0.00%'; ws.cell(r, 2).alignment = Alignment(horizontal='center')
        ws.cell(r, 3).number_format = '0.00%'; ws.cell(r, 3).alignment = Alignment(horizontal='center')
        apply_wow(ws, r, 4, wow, invert=False)
        r += 1
    r += 1

    # Severity distribución
    sev_ef, sev_cv = {}, {}
    for _, row in p80_all.iterrows():
        ef = fmt_pct(row.get('Eficacia'))
        cv = fmt_pct(row.get('ConvRate'))
        bk = int(row.get('Bookings', 0)) if pd.notna(row.get('Bookings', 0)) else 0
        if ef is not None: b = banda_eficacia(ef); sev_ef[b] = sev_ef.get(b, 0) + 1
        if cv is not None: b = banda_convrate(cv, bk); sev_cv[b] = sev_cv.get(b, 0) + 1

    for label, sev, orden in [
        ('Severity Eficacia', sev_ef,
         ['Exitosa', 'Aceptable', 'Revisar', 'Crítica', 'Súper Crítica']),
        ('Severity Conv Rate', sev_cv,
         ['Exitosa', 'Aceptable', 'Revisar', 'Crítica', 'Sin Conversión']),
    ]:
        ws.cell(r, 1, label).font = fnt(CR, 11, True); r += 1
        r = mk_hdr(ws, r, ['Severity', 'Hoteles', '% del Total'])
        total = sum(sev.values()) or 1
        for b in orden:
            n = sev.get(b, 0)
            mk_cell(ws, r, 1, b, b, is_sev=True, align='center')
            ws.cell(r, 1).border = BD
            ws.cell(r, 2, n).border = BD; ws.cell(r, 2).alignment = Alignment(horizontal='center')
            ws.cell(r, 3, round(n/total, 4)).number_format = '0.0%'
            ws.cell(r, 3).border = BD; ws.cell(r, 3).alignment = Alignment(horizontal='center')
            r += 1
        r += 1

    # Top Destinos EF+CV
    tab_ef_g = TAB_EF.get('global', {})
    tab_cv_g = TAB_CV.get('global', {})
    df_dest_ef = tab_ef_g.get('destino')
    if df_dest_ef is not None and len(df_dest_ef) > 0:
        ws.cell(r, 1, 'Top Destinos · Eficacia ASC').font = fnt(CR, 11, True); r += 1
        r = mk_hdr(ws, r, ['Destino', 'Banda Ef', 'Banda CV', 'CR Únicos', 'Eficacia', 'WoW Ef', 'Conv Rate', 'WoW CV', 'Bookings'])
        df_cv_dest = tab_cv_g.get('destino')
        df_merged = df_dest_ef.sort_values('Eficacia', ascending=True).head(30).copy()
        if df_cv_dest is not None and 'ConvRate_WoW_pp' in df_cv_dest.columns:
            df_merged = df_merged.merge(df_cv_dest[['Destino', 'ConvRate', 'ConvRate_WoW_pp']], on='Destino', how='left', suffixes=('', '_cv'))
        for _, row in df_merged.iterrows():
            ef = fmt_pct(row.get('Eficacia'))
            cv = fmt_pct(row.get('ConvRate'))
            bk = int(row.get('Bookings', 0)) if pd.notna(row.get('Bookings', 0)) else 0
            cru = int(row.get('CR_Unicos', 0)) if pd.notna(row.get('CR_Unicos', 0)) else 0
            bef = banda_eficacia(ef) if ef is not None else '—'
            bcv = banda_convrate(cv, bk) if cv is not None else '—'
            mk_cell(ws, r, 1, str(row.get('Destino', '—')), align='left')
            mk_cell(ws, r, 2, bef, bef, is_sev=True)
            mk_cell(ws, r, 3, bcv, bcv, is_sev=True)
            mk_cell(ws, r, 4, cru)
            c = ws.cell(r, 5, ef); c.border = BD; c.alignment = Alignment(horizontal='center')
            if ef is not None: ws.cell(r, 5).number_format = '0.00%'
            apply_wow(ws, r, 6, sf(row.get('Eficacia_WoW_pp')), invert=False)
            c2 = ws.cell(r, 7, cv); c2.border = BD; c2.alignment = Alignment(horizontal='center')
            if cv is not None: ws.cell(r, 7).number_format = '0.00%'
            apply_wow(ws, r, 8, sf(row.get('ConvRate_WoW_pp')), invert=False)
            mk_cell(ws, r, 9, bk)
            r += 1
        r += 1

    # Top Corp EF+CV
    df_corp_ef = tab_ef_g.get('corp')
    if df_corp_ef is not None and len(df_corp_ef) > 0:
        ws.cell(r, 1, 'Top Corporativos · Eficacia ASC').font = fnt(CR, 11, True); r += 1
        r = mk_hdr(ws, r, ['Corporativo', 'Banda Ef', 'Banda CV', 'CR Únicos', 'Eficacia', 'WoW Ef', 'Conv Rate', 'WoW CV', 'Bookings'])
        df_cv_corp = tab_cv_g.get('corp')
        df_merged2 = df_corp_ef.sort_values('Eficacia', ascending=True).head(30).copy()
        if df_cv_corp is not None and 'ConvRate_WoW_pp' in df_cv_corp.columns:
            df_merged2 = df_merged2.merge(df_cv_corp[['CorpName', 'ConvRate', 'ConvRate_WoW_pp']], on='CorpName', how='left', suffixes=('', '_cv'))
        for _, row in df_merged2.iterrows():
            ef = fmt_pct(row.get('Eficacia'))
            cv = fmt_pct(row.get('ConvRate'))
            bk = int(row.get('Bookings', 0)) if pd.notna(row.get('Bookings', 0)) else 0
            cru = int(row.get('CR_Unicos', 0)) if pd.notna(row.get('CR_Unicos', 0)) else 0
            bef = banda_eficacia(ef) if ef is not None else '—'
            bcv = banda_convrate(cv, bk) if cv is not None else '—'
            mk_cell(ws, r, 1, str(row.get('CorpName', '—')), align='left')
            mk_cell(ws, r, 2, bef, bef, is_sev=True)
            mk_cell(ws, r, 3, bcv, bcv, is_sev=True)
            mk_cell(ws, r, 4, cru)
            c = ws.cell(r, 5, ef); c.border = BD; c.alignment = Alignment(horizontal='center')
            if ef is not None: ws.cell(r, 5).number_format = '0.00%'
            apply_wow(ws, r, 6, sf(row.get('Eficacia_WoW_pp')), invert=False)
            c2 = ws.cell(r, 7, cv); c2.border = BD; c2.alignment = Alignment(horizontal='center')
            if cv is not None: ws.cell(r, 7).number_format = '0.00%'
            apply_wow(ws, r, 8, sf(row.get('ConvRate_WoW_pp')), invert=False)
            mk_cell(ws, r, 9, bk)
            r += 1
        r += 1

    # Channel
    df_ch = tab_ef_g.get('channel')
    if df_ch is not None and len(df_ch) > 0:
        ws.cell(r, 1, 'Channel · Eficacia ASC').font = fnt(CR, 11, True); r += 1
        r = mk_hdr(ws, r, ['Channel', 'Banda Ef', 'Banda CV', 'CR Únicos', 'Eficacia', 'WoW Ef', 'Conv Rate', 'WoW CV', 'Bookings'])
        df_ch_cv = tab_cv_g.get('channel')
        df_ch_m = df_ch.sort_values('Eficacia', ascending=True).copy()
        if df_ch_cv is not None and 'ConvRate_WoW_pp' in df_ch_cv.columns:
            df_ch_m = df_ch_m.merge(df_ch_cv[['ExternalProviderName', 'ConvRate_WoW_pp']], on='ExternalProviderName', how='left')
        for _, row in df_ch_m.iterrows():
            ef = fmt_pct(row.get('Eficacia'))
            cv = fmt_pct(row.get('ConvRate'))
            bk = int(row.get('Bookings', 0)) if pd.notna(row.get('Bookings', 0)) else 0
            cru = int(row.get('CR_Unicos', 0)) if pd.notna(row.get('CR_Unicos', 0)) else 0
            bef = banda_eficacia(ef) if ef is not None else '—'
            bcv = banda_convrate(cv, bk) if cv is not None else '—'
            mk_cell(ws, r, 1, str(row.get('ExternalProviderName', '—')), align='left')
            mk_cell(ws, r, 2, bef, bef, is_sev=True)
            mk_cell(ws, r, 3, bcv, bcv, is_sev=True)
            mk_cell(ws, r, 4, cru)
            c = ws.cell(r, 5, ef); c.border = BD; c.alignment = Alignment(horizontal='center')
            if ef is not None: ws.cell(r, 5).number_format = '0.00%'
            apply_wow(ws, r, 6, sf(row.get('Eficacia_WoW_pp')), invert=False)
            c2 = ws.cell(r, 7, cv); c2.border = BD; c2.alignment = Alignment(horizontal='center')
            if cv is not None: ws.cell(r, 7).number_format = '0.00%'
            apply_wow(ws, r, 8, sf(row.get('ConvRate_WoW_pp')), invert=False)
            mk_cell(ws, r, 9, bk)
            r += 1

    autofit(ws, [28, 18, 18, 10, 10, 10, 10, 10, 10])

# ── Build workbook ────────────────────────────────────────────────────────────
wb = Workbook(); wb.remove(wb.active)
banda_lookup = build_banda_lookup_cr()
df_global = hotel_src_cr(None)
crit, bajo, sinc = band_split_ef(df_global)

ws = wb.create_sheet('Maestra'); ws.sheet_properties.tabColor = CR
write_maestra(ws)

ws = wb.create_sheet('Críticos'); ws.sheet_properties.tabColor = 'C0392B'
write_banda(ws, crit, f'Críticos · CR W{VOL_NUM}', banda_lookup)

ws = wb.create_sheet('Bajo Rendimiento'); ws.sheet_properties.tabColor = 'F97316'
write_banda(ws, bajo, f'Bajo Rendimiento · CR W{VOL_NUM}', banda_lookup)

ws = wb.create_sheet('Sin Conversión'); ws.sheet_properties.tabColor = '8A8377'
write_banda(ws, sinc, f'Sin Conversión · CR W{VOL_NUM}', banda_lookup)

ws = wb.create_sheet('Severity'); ws.sheet_properties.tabColor = CR
write_severity(ws)

out = f'{OUTPUTS}/Analisis_CheckRates_W{VOL_NUM}.xlsx'
wb.save(out)
print(f'✅ Excel CR: {out}')
print(f'   {len(wb.sheetnames)} hojas: {" | ".join(wb.sheetnames)}')
