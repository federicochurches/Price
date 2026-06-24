"""
build_hist_entity.py
====================
Agrega métricas históricas reales por corp/dest desde los datasets semanales.

CR  → Eficacia (ef), ConvRate (cv)
RND → %NoDispo (nd), IPM (ipm)

Retorna dicts con la forma:
  {
    'corp': { 'CorpName': { 'W18': {'ef': X, 'cv': X}, 'W19': {...}, ... } },
    'dest': { 'Destino':  { 'W18': {'ef': X, 'cv': X}, ... } },
  }

Uso desde calc_cr.py / calc_rnd.py:
  from build_hist_entity import build_cr_hist, build_rnd_hist
  CR_HIST  = build_cr_hist(week_nums=range(18, VOL_NUM), base_dir='.')
  RND_HIST = build_rnd_hist(week_nums=range(18, VOL_NUM), base_dir='.')
"""

import os
import pandas as pd
import numpy as np

MIN_CR      = 100
MIN_TRAFICO = 50_000

CANAL_VALIDO = {'B2C', 'B2B (OP)', 'CUG (UOP)'}


def _safe_div(num, den):
    if den and not np.isnan(float(den)) and float(den) != 0:
        return float(num) / float(den)
    return None


def _wkey(wn):
    return f'W{wn:02d}'


# ── CR ─────────────────────────────────────────────────────────────────────────

def _load_cr_week(path):
    df = pd.read_excel(path)
    df = df.rename(columns={
        'Corporate':               'CorpName',
        'CheckRates Únicos':       'CR_Unicos',
        'Successful UniqueChkRts': 'Successful',
    })
    if 'Successful' not in df.columns and 'Efectividad en CheckRates' in df.columns:
        df['CR_Unicos'] = pd.to_numeric(df.get('CR_Unicos', 0), errors='coerce').fillna(0)
        df['Successful'] = df['CR_Unicos'] * pd.to_numeric(
            df['Efectividad en CheckRates'], errors='coerce').fillna(0)

    for col in ('CR_Unicos', 'Successful', 'Bookings'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'DistributionCategory' in df.columns:
        df = df[df['DistributionCategory'].isin(CANAL_VALIDO)].copy()

    df = df[df['CR_Unicos'] >= MIN_CR].copy()
    return df


def build_cr_hist(week_nums, base_dir='.'):
    """Eficacia y ConvRate reales por corp/dest, semanas week_nums (excluye la semana actual)."""
    result = {'corp': {}, 'dest': {}, 'hotel': {}, 'provider': {}}

    for wn in week_nums:
        path = os.path.join(base_dir,
            f'checkrates/week-{wn:02d}/Dataset_CheckRates_W{wn:02d}.xlsx')
        if not os.path.exists(path):
            continue
        try:
            df = _load_cr_week(path)
        except Exception as e:
            print(f"  [hist CR] W{wn:02d} error: {e}")
            continue

        wk = _wkey(wn)

        for dim_col, bucket in [('CorpName', 'corp'), ('Destino', 'dest'),
                                 ('Hotel', 'hotel'), ('ExternalProviderName', 'provider')]:
            if dim_col not in df.columns:
                continue
            min_cr_dim = MIN_CR if bucket != 'hotel' else 50  # hoteles: umbral más bajo
            grp = df.groupby(dim_col, as_index=False).agg(
                CR_Unicos  = ('CR_Unicos',  'sum'),
                Successful = ('Successful', 'sum'),
                Bookings   = ('Bookings',   'sum'),
            )
            grp = grp[grp['CR_Unicos'] >= min_cr_dim]
            for _, row in grp.iterrows():
                name = str(row[dim_col]).strip()
                # Hoteles: limpiar prefijo "(ID) - " → solo nombre
                if bucket == 'hotel' and name.startswith('('):
                    import re as _re
                    name = _re.sub(r'^\(\d+\)\s*-\s*', '', name).strip()
                ef = _safe_div(row['Successful'], row['CR_Unicos'])
                cv = _safe_div(row['Bookings'],   row['CR_Unicos'])
                result[bucket].setdefault(name, {})[wk] = {
                    'ef': round(ef, 6) if ef is not None else None,
                    'cv': round(cv, 6) if cv is not None else None,
                }

    print(f"  [hist CR] corps={len(result['corp'])}  dests={len(result['dest'])}  hotels={len(result.get('hotel',{}))}  providers={len(result.get('provider',{}))}")
    return result


# ── RND ────────────────────────────────────────────────────────────────────────

def _load_rnd_week(path, wn):
    """Reutiliza la lógica de calc_rnd.load_rnd (soporta pivotado y largo)."""
    raw = pd.read_excel(path, header=None, nrows=2)
    is_pivoted = (len(raw.columns) >= 16 and
                  any(str(v) in ['B2B (OP)', 'B2C', 'CUG (UOP)'] for v in raw.iloc[0].values))

    if is_pivoted:
        canastas = raw.iloc[0].tolist()
        metricas = raw.iloc[1].tolist()
        df_raw   = pd.read_excel(path, header=None, skiprows=2)
        df_raw.columns = metricas
        id_cols  = ['CorpName', 'Destino', 'Hotel', 'PaisDestino']
        cat_groups = {}
        for i, cat in enumerate(canastas):
            cat = str(cat).strip()
            if cat in CANAL_VALIDO:
                metric = str(metricas[i]).strip()
                cat_groups.setdefault(cat, {})[metric] = i
        rows = []
        for cat, col_map in cat_groups.items():
            sub = df_raw[id_cols].copy()
            sub['DistributionCategory'] = cat
            for metric, col_idx in col_map.items():
                sub[metric] = df_raw.iloc[:, col_idx].values
            rows.append(sub)
        if not rows:
            return pd.DataFrame()
        df = pd.concat(rows, ignore_index=True)
        df = df[~((pd.to_numeric(df.get('Trafico', 0), errors='coerce').fillna(0) == 0) &
                  (df['CorpName'].astype(str).str.strip() == '-'))].copy()
    else:
        df = pd.read_excel(path)
        if df.columns[0] != 'CorpName':
            df = df.rename(columns={df.columns[0]: 'CorpName'})

    df = df[df['DistributionCategory'].isin(CANAL_VALIDO)].copy()
    df['CorpName'] = df['CorpName'].astype(str).str.strip()
    df['Destino']  = df['Destino'].astype(str).str.strip().str.replace(r'\s+Area\b', '', regex=True).str.strip()
    df = df[df['Destino'].str.lower().str.replace(' ', '') != 'sinclasificar'].copy()

    for col in ('Trafico', 'Bookings', 'gb_usd', '%NoDispo'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'TraficoNoDispo' not in df.columns:
        df['TraficoNoDispo'] = df['Trafico'] * df['%NoDispo']

    return df


def build_rnd_hist(week_nums, base_dir='.'):
    """%NoDispo e IPM reales por corp/dest, semanas week_nums."""
    result = {'corp': {}, 'dest': {}, 'hotel': {}}

    for wn in week_nums:
        path = os.path.join(base_dir,
            f'rates-nodispo/week-{wn:02d}/Dataset_RatesNoDispo_W{wn:02d}.xlsx')
        if not os.path.exists(path):
            continue
        try:
            df = _load_rnd_week(path, wn)
        except Exception as e:
            print(f"  [hist RND] W{wn:02d} error: {e}")
            continue

        wk = _wkey(wn)

        for dim_col, bucket in [('CorpName', 'corp'), ('Destino', 'dest'), ('Hotel', 'hotel')]:
            if dim_col not in df.columns:
                continue
            grp = df.groupby(dim_col, as_index=False).agg(
                Trafico        = ('Trafico',        'sum'),
                TraficoNoDispo = ('TraficoNoDispo',  'sum'),
                Bookings       = ('Bookings',        'sum'),
                gb_usd         = ('gb_usd',          'sum'),
            )
            min_traf_dim = MIN_TRAFICO if bucket != 'hotel' else 50_000
            grp = grp[grp['Trafico'] >= min_traf_dim]
            for _, row in grp.iterrows():
                name = str(row[dim_col]).strip()
                if bucket == 'hotel' and name.startswith('('):
                    import re as _re_rnd
                    name = _re_rnd.sub(r'^\(\d+\)\s*-\s*', '', name).strip()
                nd  = _safe_div(row['TraficoNoDispo'], row['Trafico'])
                ipm = _safe_div(row['gb_usd'],         row['Trafico'])
                if ipm is not None:
                    ipm = ipm * 1_000_000
                # IPM negativo = cancelaciones > revenue: registrar como None
                result[bucket].setdefault(name, {})[wk] = {
                    'nd':  round(nd,  6) if nd  is not None else None,
                    'ipm': round(ipm, 0) if (ipm is not None and ipm >= 0) else None,
                }

    print(f"  [hist RND] corps={len(result['corp'])}  dests={len(result['dest'])}  hotels={len(result.get('hotel', {}))}")
    return result
