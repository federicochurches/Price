"""
editorial_engine.py · Proyecto PRICE · W26+
Fuente única de verdad para RE (Resumen Ejecutivo) y PA (Plan de Acción).
Diseño aprobado: EDITORIAL_ENGINE_DESIGN.md · 25-06-2026

API pública:
  build_payload_cr(D, scope)    → payload CR
  build_payload_rnd(D, scope)   → payload RND
  build_findings(payload, report_type)    → list[dict] (10 items para RE)
  build_action_plan(payload, report_type) → list[dict] (3-6 items para PA)
  build_carryover(payload_curr, payload_prev, report_type) → list[dict]

Formato de retorno RE/PA es compatible con demo_js_main.js (d = HTML drilldown,
_parseDrill renderiza secciones Corps/Destinos/Hoteles).
"""

import math
import numpy as np
import pandas as pd

from engine import (
    banda_nodispo, banda_eficacia, banda_convrate, banda_rpm
)
from render_helpers import (
    clean_hotel_name, fmt_big, fmt_int_es, es_pct, es_int,
    banda_colors, sev_badge_html_p2, wow_arrow
)

# ── Constantes ────────────────────────────────────────────────────────────────

CANASTA_QUALITY = {
    'b2c':    0.3,   # ruido de bots — descuento fuerte
    'op':     0.8,
    'cug':    1.0,
    'global': 0.6,
}

VOL_COL = {
    'eficacia':    'CR_Unicos',
    'convrate':    'CR_Unicos',
    'bookability': 'Bookings',
    'nodispo':     'Trafico',
}

WOW_COL = {
    'eficacia':    'Eficacia_WoW_pp',
    'convrate':    'ConvRate_WoW_pp',
    'bookability': 'Bookability_WoW_pp',
    'nodispo':     'NoDispo_WoW_pp',
}

BANDA_COL = {
    'eficacia':    'BandaEficacia',
    'convrate':    'BandaConvRate',
    'bookability': 'BandaBookability',
    'nodispo':     'BandaNoDispo',
}

BANDAS_SC_C = {'Súper Crítica', 'Crítica'}

# Umbrales mínimos de volumen
UMBRAL_MIN_CR  = 100       # CR_Unicos mínimos para acción QW hotel CR
UMBRAL_MIN_RND = 10_000    # Tráfico mínimo para acción QW hotel RND
UMBRAL_PAIS    = 100_000   # Tráfico mínimo para acción País RND
N_MIN_COHORTE  = 3         # Hoteles mínimos para acción MP de saneamiento

# Colores de drilldown (para _parseDrill en demo_js_main.js)
_COL_CORPS   = '#5C469C'
_COL_DESTS   = '#185FA5'
_COL_HOTELES = '#EA0074'

# ── Helpers locales ───────────────────────────────────────────────────────────

def _nan(v):
    return v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))

def _sev(banda):
    return sev_badge_html_p2(banda)

def _pct(v, dec=2):
    if _nan(v): return '—'
    return f'{float(v)*100:.{dec}f}%'.replace('.', ',')

def _ipm(v):
    if _nan(v): return '—'
    return f'${float(v):,.0f}'.replace(',', '.')

def _traf(v):
    if _nan(v): return '—'
    return fmt_big(float(v))

def _cr(v):
    if _nan(v): return '—'
    try: return fmt_int_es(int(float(v)))
    except: return '—'

# ── Scoring ───────────────────────────────────────────────────────────────────

def score_hotel(row, vol_max, metric, scope='global', report_type='cr'):
    """
    Score de hotel (0-1) para priorización en RE/Plan.
    Solo aplicar sobre universo SC+C.
    """
    if vol_max is None or vol_max == 0:
        return 0.0

    # Volumen
    vol_raw = row.get(VOL_COL[metric], 0) or 0
    quality = CANASTA_QUALITY.get(scope, 0.6) if (report_type == 'cr' and metric != 'bookability') else 1.0
    vol_norm = min((float(vol_raw) * quality) / float(vol_max), 1.0)

    # Severidad
    banda = row.get(BANDA_COL.get(metric, ''), '')
    sev_idx = 1.0 if banda == 'Súper Crítica' else 0.6

    # Bonus WoW (asimétrico — solo empeora sube el score)
    wow_val = row.get(WOW_COL.get(metric, ''), None)
    if _nan(wow_val):
        bonus_wow = 0.0
    elif report_type == 'rnd':
        bonus_wow = 0.10 if float(wow_val) > 0 else 0.0   # NoDispo sube = empeora
    else:
        bonus_wow = 0.10 if float(wow_val) < 0 else 0.0   # Eficacia baja = empeora

    return 0.60 * vol_norm + 0.30 * sev_idx + 0.10 * bonus_wow


def _add_scores(df, metric, scope, report_type, vol_col=None):
    """Agrega columna 'score' al DataFrame in-place. Retorna df con score."""
    df = df.copy()
    vc = vol_col or VOL_COL.get(metric, 'CR_Unicos')
    quality = CANASTA_QUALITY.get(scope, 0.6) if (report_type == 'cr' and metric != 'bookability') else 1.0
    vol_max = float(df[vc].max()) * quality if vc in df.columns and len(df) else 1.0
    if vol_max == 0:
        vol_max = 1.0
    df['score'] = df.apply(lambda r: score_hotel(r, vol_max, metric, scope, report_type), axis=1)
    return df.sort_values('score', ascending=False)


# ── Dimensiones derivadas ─────────────────────────────────────────────────────

def _derive_dim(df_sc_c, dim_col, vol_col='CR_Unicos'):
    """
    Agrega hoteles SC+C por dimensión.
    score_dim = max(score_hotel) — punto de falla más grave.
    """
    if len(df_sc_c) == 0 or dim_col not in df_sc_c.columns or 'score' not in df_sc_c.columns:
        return pd.DataFrame()
    result = []
    for dim_val, grp in df_sc_c.groupby(dim_col):
        best_idx = grp['score'].idxmax()
        best = grp.loc[best_idx]
        result.append({
            dim_col:           dim_val,
            'score':           float(grp['score'].max()),
            'n_hoteles_sc_c':  len(grp),
            'vol_total':       float(grp[vol_col].sum()) if vol_col in grp.columns else 0.0,
            'hotel_driver':    str(best.get('Hotel', '—')),
            'corp_driver':     str(best.get('CorpName', '—')),
            'val_driver':      float(best.get('_main_metric', best.get('%NoDispo', best.get('Eficacia', 0))) or 0),
        })
    return pd.DataFrame(result).sort_values('score', ascending=False) if result else pd.DataFrame()


# ── Drilldown HTML ────────────────────────────────────────────────────────────

def _drill_section(label, color, rows, max_rows=5):
    """
    Genera una sección de drilldown compatible con _parseDrill() de demo_js_main.js.
    rows: list of (name, value_str) tuples.
    """
    if not rows:
        return ''
    items_html = ''.join(
        f'<div><strong>{r[0]}</strong> · {r[1]}</div>'
        for r in rows[:max_rows]
    )
    return (
        f'<div style="border-left:3px solid {color};padding:4px 8px;margin:3px 0;">'
        f'<span style="font-size:8px;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:.08em;color:{color};">{label}</span>'
        f'{items_html}'
        f'</div>'
    )


def _build_drill(corps=None, dests=None, hotels=None,
                 corps_col='CR_Unicos', dests_col='CR_Unicos', hotels_col='CR_Unicos',
                 val_fn=None, vol_fn=None, max_rows=5, report_type='cr'):
    """
    Construye el HTML de drilldown para el campo 'd' del RE/Plan.
    val_fn(row) → str · función para formatear la métrica de cada fila.
    vol_fn(row) → str · función para formatear el volumen.
    """
    if val_fn is None:
        if report_type == 'rnd':
            val_fn = lambda r: _pct(r.get('%NoDispo', r.get('val_driver', 0)))
        else:
            val_fn = lambda r: _pct(r.get('Eficacia', r.get('val_driver', 0)))
    if vol_fn is None:
        if report_type == 'rnd':
            vol_fn = lambda r: _traf(r.get('Trafico', r.get('vol_total', 0)))
        else:
            vol_fn = lambda r: _cr(r.get('CR_Unicos', r.get('vol_total', 0)))

    sections = ''

    # Corps
    if corps is not None and len(corps):
        corp_col = 'CorpName' if 'CorpName' in corps.columns else corps.columns[0]
        rows = [
            (str(r[corp_col])[:30], f'{val_fn(r)} · {vol_fn(r)}')
            for _, r in corps.head(max_rows).iterrows()
        ]
        sections += _drill_section('Corps', _COL_CORPS, rows)

    # Destinos
    if dests is not None and len(dests):
        dest_col = 'Destino' if 'Destino' in dests.columns else dests.columns[0]
        rows = [
            (str(r[dest_col])[:28], f'{val_fn(r)} · {vol_fn(r)}')
            for _, r in dests.head(max_rows).iterrows()
        ]
        sections += _drill_section('Destinos', _COL_DESTS, rows)

    # Hoteles
    if hotels is not None and len(hotels):
        hotel_col = 'Hotel' if 'Hotel' in hotels.columns else hotels.columns[0]
        rows = [
            (clean_hotel_name(str(r[hotel_col]))[:30], f'{val_fn(r)} · {vol_fn(r)}')
            for _, r in hotels.head(max_rows).iterrows()
        ]
        sections += _drill_section('Hoteles', _COL_HOTELES, rows)

    return sections


# ── Build Payload CR ──────────────────────────────────────────────────────────

def build_payload_cr(D, scope='global', bk_data=None):
    """
    Construye payload CR desde pickle D para el scope indicado.

    D: dict del pickle CR (cr_wNN_data.pkl)
    scope: 'global' | 'b2c' | 'op' | 'cug'
    bk_data: dict del pickle BK (opcional, para Bookability)
    """
    WEEK_NUM = int(D.get('VOL_NUM', '25'))
    WEEK_PREV = WEEK_NUM - 1

    # Métricas globales del scope
    scope_key_map = {
        'global': f'global_w{WEEK_NUM}',
        'b2c':    f'B2C_w{WEEK_NUM}',
        'op':     f'B2B (OP)_w{WEEK_NUM}',
        'cug':    f'CUG (UOP)_w{WEEK_NUM}',
    }
    prev_key_map = {
        'global': f'global_w{WEEK_PREV}',
        'b2c':    f'B2C_w{WEEK_PREV}',
        'op':     f'B2B (OP)_w{WEEK_PREV}',
        'cug':    f'CUG (UOP)_w{WEEK_PREV}',
    }
    M = D.get('M', {})
    m_curr = M.get(scope_key_map.get(scope, f'global_w{WEEK_NUM}'), {})
    m_prev = M.get(prev_key_map.get(scope, f'global_w{WEEK_PREV}'), {})

    ef_global = float(m_curr.get('eficacia', 0) or 0)
    cv_global  = float(m_curr.get('conv_rate', 0) or 0)
    ef_prev   = float(m_prev.get('eficacia', 0) or 0)
    cv_prev   = float(m_prev.get('conv_rate', 0) or 0)
    ef_wow    = (ef_global - ef_prev) * 100 if ef_prev else float('nan')
    cv_wow    = (cv_global - cv_prev) * 100 if cv_prev else float('nan')

    # DataFrame de hoteles del scope
    if scope == 'global':
        df = D.get('p80_hotel', pd.DataFrame()).copy()
    else:
        canasta_data = D.get('CANASTA', {})
        scope_key_rnd = {'b2c': 'b2c', 'op': 'op', 'cug': 'cug'}
        c_data = canasta_data.get(scope_key_rnd.get(scope, scope), {})
        df = c_data.get('p80', D.get('p80_hotel', pd.DataFrame())).copy()

    if df is None or len(df) == 0:
        df = pd.DataFrame()

    # Columna hotel limpia
    if 'Hotel' in df.columns:
        df['Hotel'] = df['Hotel'].apply(lambda x: clean_hotel_name(str(x)))

    # Asegurar BandaEficacia
    if 'BandaEficacia' not in df.columns and 'Eficacia' in df.columns:
        df['BandaEficacia'] = df['Eficacia'].apply(banda_eficacia)
    if 'BandaConvRate' not in df.columns and 'ConvRate' in df.columns and 'Bookings' in df.columns:
        df['BandaConvRate'] = df.apply(lambda r: banda_convrate(r['ConvRate'], r.get('Bookings', 1)), axis=1)

    # Universo SC+C (Eficacia)
    hoteles_ef_sc_c = pd.DataFrame()
    if 'BandaEficacia' in df.columns and 'Bookings' in df.columns:
        mask = df['BandaEficacia'].isin(BANDAS_SC_C) & (df['Bookings'] > 0)
        hoteles_ef_sc_c = df[mask].copy()
        if len(hoteles_ef_sc_c):
            hoteles_ef_sc_c['_main_metric'] = hoteles_ef_sc_c.get('Eficacia', pd.Series([0]*len(hoteles_ef_sc_c)))
            hoteles_ef_sc_c = _add_scores(hoteles_ef_sc_c, 'eficacia', scope, 'cr')

    # Dimensiones derivadas
    corps_ef_sc_c = pd.DataFrame()
    dests_ef_sc_c = pd.DataFrame()
    channels_ef_sc_c = pd.DataFrame()
    if len(hoteles_ef_sc_c):
        corps_ef_sc_c = _derive_dim(hoteles_ef_sc_c, 'CorpName', 'CR_Unicos')
        if 'Destino' in hoteles_ef_sc_c.columns:
            dests_ef_sc_c = _derive_dim(hoteles_ef_sc_c, 'Destino', 'CR_Unicos')
        chan_col = 'ExternalProviderName' if 'ExternalProviderName' in hoteles_ef_sc_c.columns else None
        if chan_col:
            channels_ef_sc_c = _derive_dim(hoteles_ef_sc_c, chan_col, 'CR_Unicos')

    # Bookability SC+C (si hay datos BK)
    hoteles_bk_sc_c = pd.DataFrame()
    if bk_data is not None:
        df_bk = bk_data.get('p80_hotel_bk', bk_data.get('p80_hoteles_bk', pd.DataFrame()))
        if isinstance(df_bk, pd.DataFrame) and len(df_bk):
            if 'BandaBookability' not in df_bk.columns and 'Bookability' in df_bk.columns:
                df_bk['BandaBookability'] = df_bk['Bookability'].apply(
                    lambda v: 'Súper Crítica' if v < 0.60 else
                              'Crítica'       if v < 0.85 else
                              'Revisar'       if v < 0.93 else
                              'Aceptable'     if v < 0.97 else 'Exitosa'
                )
            mask_bk = df_bk.get('BandaBookability', pd.Series([''] * len(df_bk))).isin(BANDAS_SC_C)
            if mask_bk.any():
                hoteles_bk_sc_c = df_bk[mask_bk].copy()
                if 'Hotel' in hoteles_bk_sc_c.columns:
                    hoteles_bk_sc_c['Hotel'] = hoteles_bk_sc_c['Hotel'].apply(lambda x: clean_hotel_name(str(x)))
                hoteles_bk_sc_c['_main_metric'] = hoteles_bk_sc_c.get('Bookability', pd.Series([0]*len(hoteles_bk_sc_c)))
                hoteles_bk_sc_c = _add_scores(hoteles_bk_sc_c, 'bookability', scope, 'cr', vol_col='Bookings')

    # Severity
    sev_ef = D.get('sev_ef_p80', {})
    sev_cv = D.get('sev_cv_p80', {})

    canasta_label = {'global': 'Global', 'b2c': 'B2C', 'op': 'Opaco', 'cug': 'Ultra Opaco'}.get(scope, scope.title())

    return {
        'ef_global':         ef_global,
        'cv_global':         cv_global,
        'ef_wow':            ef_wow,
        'cv_wow':            cv_wow,
        'hoteles_ef_sc_c':   hoteles_ef_sc_c,
        'hoteles_bk_sc_c':   hoteles_bk_sc_c,
        'corps_ef_sc_c':     corps_ef_sc_c,
        'dests_ef_sc_c':     dests_ef_sc_c,
        'channels_ef_sc_c':  channels_ef_sc_c,
        'n_ef_sc_c':         len(hoteles_ef_sc_c),
        'n_bk_sc_c':         len(hoteles_bk_sc_c),
        'n_p80':             len(df),
        'df_all':            df,            # todos los hoteles del scope
        'sev_ef':            dict(sev_ef),
        'sev_cv':            dict(sev_cv),
        'scope':             scope,
        'canasta_label':     canasta_label,
        'week_num':          WEEK_NUM,
        'week_prev':         WEEK_PREV,
    }


# ── Build Payload RND ─────────────────────────────────────────────────────────

def build_payload_rnd(D, scope='global'):
    """
    Construye payload RND desde pickle D para el scope indicado.
    D: dict del pickle RND (rnd_wNN_data.pkl)
    """
    WEEK_NUM = int(D.get('VOL_NUM', '25'))
    WEEK_PREV = WEEK_NUM - 1

    scope_key_map = {
        'global': f'global_w{WEEK_NUM}',
        'b2c':    f'B2C_w{WEEK_NUM}',
        'op':     f'B2B (OP)_w{WEEK_NUM}',
        'cug':    f'CUG (UOP)_w{WEEK_NUM}',
    }
    prev_key_map = {
        'global': f'global_w{WEEK_PREV}',
        'b2c':    f'B2C_w{WEEK_PREV}',
        'op':     f'B2B (OP)_w{WEEK_PREV}',
        'cug':    f'CUG (UOP)_w{WEEK_PREV}',
    }
    M = D.get('M', {})
    m_curr = M.get(scope_key_map.get(scope, f'global_w{WEEK_NUM}'), {})
    m_prev = M.get(prev_key_map.get(scope, f'global_w{WEEK_PREV}'), {})

    nd_global  = float(m_curr.get('pct_nodispo', m_curr.get('nodispo', 0)) or 0)
    ipm_global = float(m_curr.get('ipm', m_curr.get('rpm', 0)) or 0)
    nd_prev    = float(m_prev.get('pct_nodispo', m_prev.get('nodispo', 0)) or 0)
    ipm_prev   = float(m_prev.get('ipm', m_prev.get('rpm', 0)) or 0)
    nd_wow     = (nd_global - nd_prev) * 100 if nd_prev else float('nan')
    ipm_wow    = (ipm_global - ipm_prev) if ipm_prev else float('nan')

    # DataFrame hoteles del scope
    if scope == 'global':
        df = D.get('p80_hotel', D.get('df18_p80', pd.DataFrame())).copy()
    else:
        canasta_data = D.get('CANASTA', {})
        c_data = canasta_data.get(scope, {})
        df = c_data.get('p80', D.get('p80_hotel', pd.DataFrame())).copy()

    if df is None or len(df) == 0:
        df = pd.DataFrame()

    if 'Hotel' in df.columns:
        df['Hotel'] = df['Hotel'].apply(lambda x: clean_hotel_name(str(x)))

    # Asegurar BandaNoDispo
    if 'BandaNoDispo' not in df.columns and '%NoDispo' in df.columns:
        df['BandaNoDispo'] = df['%NoDispo'].apply(banda_nodispo)

    # Asegurar WoW column si no existe
    if 'NoDispo_WoW_pp' not in df.columns and '%NoDispo' in df.columns:
        g_prev = D.get('g_hotel_w17', D.get('df17_p80', None))
        if g_prev is not None and 'Hotel' in g_prev.columns and '%NoDispo' in g_prev.columns:
            _prev = g_prev[['Hotel','%NoDispo']].copy()
            _prev.columns = ['Hotel', 'NoDispo_prev']
            df = df.merge(_prev, on='Hotel', how='left')
            df['NoDispo_WoW_pp'] = (df['%NoDispo'] - df.get('NoDispo_prev', df['%NoDispo'])) * 100

    # Universo SC+C
    hoteles_nd_sc_c = pd.DataFrame()
    if 'BandaNoDispo' in df.columns:
        mask = df['BandaNoDispo'].isin(BANDAS_SC_C)
        hoteles_nd_sc_c = df[mask].copy()
        if len(hoteles_nd_sc_c):
            hoteles_nd_sc_c['_main_metric'] = hoteles_nd_sc_c.get('%NoDispo', pd.Series([0]*len(hoteles_nd_sc_c)))
            hoteles_nd_sc_c = _add_scores(hoteles_nd_sc_c, 'nodispo', scope, 'rnd', vol_col='Trafico')

    # Dimensiones derivadas
    corps_nd_sc_c  = pd.DataFrame()
    dests_nd_sc_c  = pd.DataFrame()
    paises_nd_sc_c = pd.DataFrame()
    if len(hoteles_nd_sc_c):
        if 'CorpName' in hoteles_nd_sc_c.columns:
            corps_nd_sc_c = _derive_dim(hoteles_nd_sc_c, 'CorpName', 'Trafico')
        if 'Destino' in hoteles_nd_sc_c.columns:
            dests_nd_sc_c = _derive_dim(hoteles_nd_sc_c, 'Destino', 'Trafico')
        if 'PaisDestino' in hoteles_nd_sc_c.columns:
            paises_nd_sc_c = _derive_dim(hoteles_nd_sc_c, 'PaisDestino', 'Trafico')

    # Severity
    sev_nd  = dict(D.get('sev_nd_p80', {}))
    sev_rpm = dict(D.get('sev_rpm_p80', {}))

    # Destinos Exitosa (<3%) — para contexto positivo
    dests_exitosa = pd.DataFrame()
    if 'BandaNoDispo' in df.columns and 'Destino' in df.columns:
        _g_dest = df.groupby('Destino').agg(
            Trafico=('Trafico', 'sum'),
            nd_sum=('%NoDispo', lambda x: (x * df.loc[x.index, 'Trafico'].values).sum() if 'Trafico' in df.columns else x.sum()),
        ).reset_index()
        if 'Trafico' in _g_dest.columns:
            _g_dest['%NoDispo_dest'] = _g_dest['nd_sum'] / _g_dest['Trafico'].replace(0, 1)
            _g_dest = _g_dest[_g_dest['%NoDispo_dest'] < 0.03].sort_values('Trafico', ascending=False)
            dests_exitosa = _g_dest.head(5)

    canasta_label = {'global': 'Global', 'b2c': 'B2C', 'op': 'Opaco', 'cug': 'Ultra Opaco'}.get(scope, scope.title())

    return {
        'nd_global':         nd_global,
        'ipm_global':        ipm_global,
        'nd_wow':            nd_wow,
        'ipm_wow':           ipm_wow,
        'hoteles_nd_sc_c':   hoteles_nd_sc_c,
        'corps_nd_sc_c':     corps_nd_sc_c,
        'dests_nd_sc_c':     dests_nd_sc_c,
        'paises_nd_sc_c':    paises_nd_sc_c,
        'dests_exitosa':     dests_exitosa,
        'n_nd_sc_c':         len(hoteles_nd_sc_c),
        'n_p80':             len(df),
        'df_all':            df,
        'sev_nd':            sev_nd,
        'sev_rpm':           sev_rpm,
        'scope':             scope,
        'canasta_label':     canasta_label,
        'week_num':          WEEK_NUM,
        'week_prev':         WEEK_PREV,
    }


# ── Findings CR ───────────────────────────────────────────────────────────────

def _finding(numero, titulo, desc=''):
    return {'n': numero, 't': titulo, 'd': desc}


def build_findings_cr(payload):
    """
    Genera lista de 10 findings para Resumen Ejecutivo CR.
    Posiciones #1 (global) y #10 (P80) son fijas.
    #2-#9 se generan según datos disponibles y se ordenan por relevancia.
    """
    ef     = payload['ef_global']
    cv     = payload['cv_global']
    ef_wow = payload['ef_wow']
    cv_wow = payload['cv_wow']
    n_ef   = payload['n_ef_sc_c']
    n_bk   = payload['n_bk_sc_c']
    n_p80  = payload['n_p80']
    scope  = payload['scope']
    lbl    = payload['canasta_label']
    wn     = payload['week_num']
    sev_ef = payload['sev_ef']

    df_ef  = payload['hoteles_ef_sc_c']
    df_bk  = payload['hoteles_bk_sc_c']
    corps  = payload['corps_ef_sc_c']
    dests  = payload['dests_ef_sc_c']
    chans  = payload['channels_ef_sc_c']

    banda_ef_global = banda_eficacia(ef)
    banda_cv_global = banda_convrate(cv, 1 if cv > 0 else 0)

    # Finding #1 (fijo) — Performance global
    sfx_wow = f' {wow_arrow(ef_wow)} WoW' if not _nan(ef_wow) else ''
    f1 = _finding(
        _pct(ef),
        f'Performance {lbl} · {_sev(banda_ef_global)}',
        f'Error Rate global en canasta {lbl}. Target ≥ 97%.{sfx_wow}'
    )

    # Finding #10 (fijo) — P80
    f10 = _finding(
        str(n_p80),
        'Hoteles P80 analizados',
        f'Universo de análisis · base estable para diagnóstico {lbl} W{wn}.'
    )

    middle = []

    # f2: N hoteles SC+C Eficacia
    n_sc_ef = int(sev_ef.get('Súper Crítica', 0))
    n_c_ef  = int(sev_ef.get('Crítica', 0))
    if n_ef > 0:
        middle.append(_finding(
            str(n_ef),
            f'Hoteles {lbl} · Error Rate {_sev("Crítica")}+',
            f'{n_sc_ef} Súper Críticos requieren escalamiento técnico inmediato · '
            f'{n_c_ef} Críticos en plan de saneamiento.'
        ))

    # f3: N hoteles SC+C Bookability
    if n_bk > 0:
        middle.append(_finding(
            str(n_bk),
            f'Hoteles {lbl} · Bookability {_sev("Crítica")}+',
            f'Bookability crítica indica falla de interface ó provider · requiere diagnóstico técnico.'
        ))

    # f4: Hotel #1 score Eficacia + drilldown
    if len(df_ef):
        h = df_ef.iloc[0]
        hotel_nm = clean_hotel_name(str(h.get('Hotel', '—')))
        corp_nm  = str(h.get('CorpName', '—'))
        ef_val   = float(h.get('Eficacia', 0) or 0)
        cr_val   = h.get('CR_Unicos', 0) or 0
        # drilldown: Corp + 3 hoteles SC+C del mismo corp
        corp_hotels = df_ef[df_ef['CorpName'] == corp_nm].head(3)
        drill = _build_drill(
            corps=corps.head(3) if len(corps) else None,
            hotels=corp_hotels if len(corp_hotels) > 1 else df_ef.head(3),
            val_fn=lambda r: _pct(r.get('Eficacia', r.get('val_driver', 0))),
            vol_fn=lambda r: f'{_cr(r.get("CR_Unicos", r.get("vol_total", 0)))} CR',
            report_type='cr'
        )
        middle.append(_finding(
            _pct(ef_val),
            f'{hotel_nm[:35]} · Error Rate crítico {_sev(banda_eficacia(ef_val))}',
            f'{_cr(cr_val)} CR únicos · {corp_nm} · escalamiento individual prioritario.<br>{drill}'
        ))

    # f5: Hotel #1 score Bookability (si distinto del de Eficacia)
    if len(df_bk):
        top_ef_hotel = clean_hotel_name(str(df_ef.iloc[0].get('Hotel', ''))) if len(df_ef) else ''
        h_bk = df_bk.iloc[0]
        bk_nm = clean_hotel_name(str(h_bk.get('Hotel', '—')))
        if bk_nm != top_ef_hotel:
            bk_val = float(h_bk.get('Bookability', 0) or 0)
            bk_bkgs = int(h_bk.get('Bookings', 0) or 0)
            middle.append(_finding(
                _pct(bk_val),
                f'{bk_nm[:35]} · Bookability {_sev("Crítica" if bk_val < 0.85 else "Revisar")}',
                f'{bk_bkgs:,} bookings afectados · {h_bk.get("CorpName","—")} · '
                f'revisar interface y configuración de provider.'.replace(',', '.')
            ))

    # f6: Corp #1 score Eficacia (si N>1 hoteles)
    if len(corps):
        top_corp = corps.iloc[0]
        corp_nm  = str(top_corp.get('CorpName', '—'))
        n_h      = int(top_corp.get('n_hoteles_sc_c', 0))
        if n_h >= 2:
            drill_corp = _build_drill(
                hotels=df_ef[df_ef['CorpName'] == corp_nm].head(5) if len(df_ef) else None,
                val_fn=lambda r: _pct(r.get('Eficacia', r.get('val_driver', 0))),
                vol_fn=lambda r: f'{_cr(r.get("CR_Unicos", r.get("vol_total", 0)))} CR',
                report_type='cr'
            )
            middle.append(_finding(
                str(n_h),
                f'{corp_nm[:30]} · concentración {_sev("Crítica")}+',
                f'{n_h} hoteles con Error Rate crítico en {lbl} · escalamiento KAM recomendado.<br>{drill_corp}'
            ))

    # f7: Destino #1 score Eficacia + hotel driver
    if len(dests):
        top_dest = dests.iloc[0]
        dest_nm  = str(top_dest.get('Destino', '—'))
        h_drv    = str(top_dest.get('hotel_driver', '—'))
        c_drv    = str(top_dest.get('corp_driver', '—'))
        vol_dest = float(top_dest.get('vol_total', 0))
        dest_hotels = df_ef[df_ef.get('Destino', pd.Series([''] * len(df_ef))) == dest_nm].head(5) if 'Destino' in df_ef.columns else pd.DataFrame()
        drill_dest = _build_drill(
            dests=dests.head(3) if len(dests) else None,
            hotels=dest_hotels if len(dest_hotels) else df_ef.head(3),
            val_fn=lambda r: _pct(r.get('Eficacia', r.get('val_driver', r.get('%NoDispo_dest', 0)))),
            vol_fn=lambda r: f'{_cr(r.get("CR_Unicos", r.get("vol_total", 0)))} CR',
            report_type='cr'
        )
        middle.append(_finding(
            _cr(vol_dest),
            f'{dest_nm[:30]} · Destino con mayor concentración Error Rate',
            f'Driver: {h_drv[:30]} · {c_drv} · {_cr(vol_dest)} CR únicos.<br>{drill_dest}'
        ))

    # f8: Channel #1 score Eficacia
    if len(chans):
        top_chan = chans.iloc[0]
        chan_nm  = str(top_chan.get('ExternalProviderName', top_chan.iloc[0] if len(top_chan) else '—'))
        n_h_chan = int(top_chan.get('n_hoteles_sc_c', 0))
        banda_chan_ef = banda_eficacia(float(top_chan.get('val_driver', 0.7)))
        middle.append(_finding(
            str(n_h_chan),
            f'{chan_nm[:30]} · Channel con mayor Error Rate {_sev(banda_chan_ef)}',
            f'{n_h_chan} hoteles SC+C en este canal · auditoría técnica recomendada.'
        ))

    # f9: WoW deterioro (si hay dato y empeoró)
    if not _nan(ef_wow) and ef_wow < -0.3:
        middle.append(_finding(
            wow_arrow(ef_wow),
            f'Performance {lbl} deterioró WoW',
            f'Performance cayó {abs(ef_wow):.2f}pp vs semana anterior · revisar cambios de configuración recientes.'.replace('.', ',')
        ))
    elif not _nan(cv_wow) and cv_wow < -0.1:
        middle.append(_finding(
            wow_arrow(cv_wow),
            f'Conv Rate {lbl} deterioró WoW',
            f'Conv Rate cayó {abs(cv_wow):.2f}pp vs semana anterior.'.replace('.', ',')
        ))

    # Ordenar middle por relevancia (sin scores en estos, solo por orden de generación)
    # Los más importantes ya están al inicio
    while len(middle) < 8:
        # Padding con datos de severity si faltan findings
        n_rev = int(sev_ef.get('Revisar', 0))
        n_sin_conv = int(payload['sev_cv'].get('Sin Conversión', 0)) if 'sev_cv' in payload else 0
        if n_rev > 0 and len(middle) < 8:
            middle.append(_finding(
                str(n_rev),
                f'Hoteles {lbl} en banda Revisar',
                f'Performance entre 85-93% · objetivo: llevar a Aceptable antes de W{wn+2}.'
            ))
        if n_sin_conv > 0 and len(middle) < 8:
            middle.append(_finding(
                str(n_sin_conv),
                f'Hoteles Sin Conversión en {lbl}',
                'BKGS=0 · cohorte estructural · diagnóstico técnico-contractual urgente.'
            ))
        if len(middle) < 8:
            middle.append(_finding('—', 'Cohorte insuficiente', 'Sin findings adicionales esta semana.'))

    findings = [f1] + middle[:8] + [f10]
    return findings[:10]


# ── Findings RND ──────────────────────────────────────────────────────────────

def build_findings_rnd(payload):
    """
    Genera lista de 10 findings para Resumen Ejecutivo RND.
    Posiciones #1 y #10 son fijas.
    """
    nd     = payload['nd_global']
    ipm    = payload['ipm_global']
    nd_wow = payload['nd_wow']
    n_nd   = payload['n_nd_sc_c']
    n_p80  = payload['n_p80']
    scope  = payload['scope']
    lbl    = payload['canasta_label']
    wn     = payload['week_num']
    sev_nd = payload['sev_nd']

    df_nd   = payload['hoteles_nd_sc_c']
    corps   = payload['corps_nd_sc_c']
    dests   = payload['dests_nd_sc_c']
    paises  = payload['paises_nd_sc_c']
    dests_ok = payload.get('dests_exitosa', pd.DataFrame())

    banda_nd_global = banda_nodispo(nd)
    banda_ipm_gl    = banda_rpm(ipm, 1 if ipm > 0 else 0)

    sfx_wow = f' {wow_arrow(nd_wow)} WoW' if not _nan(nd_wow) else ''

    # Finding #1 (fijo) — NoDispo global
    f1 = _finding(
        _pct(nd),
        f'Tasa No Dispo {lbl} · {_sev(banda_nd_global)}',
        f'Búsquedas sin disponibilidad respuesta en {lbl}. Target < 3%.{sfx_wow}'
    )

    # Finding #10 (fijo) — P80
    f10 = _finding(
        str(n_p80),
        'Hoteles P80 analizados',
        f'Universo de análisis · base estable para diagnóstico {lbl} W{wn}.'
    )

    middle = []

    # f2: N hoteles SC+C NoDispo
    n_sc_nd = int(sev_nd.get('Súper Crítica', 0))
    n_c_nd  = int(sev_nd.get('Crítica', 0))
    if n_nd > 0:
        middle.append(_finding(
            str(n_nd),
            f'Hoteles {lbl} · Tasa No Dispo {_sev("Crítica")}+',
            f'{n_sc_nd} Súper Críticos (NoDispo >60%) · {n_c_nd} Críticos (20-60%) · apertura urgente de cupos.'
        ))

    # f3: Hotel #1 score NoDispo + drilldown Corp/Destino
    if len(df_nd):
        h = df_nd.iloc[0]
        hotel_nm = clean_hotel_name(str(h.get('Hotel', '—')))
        corp_nm  = str(h.get('CorpName', '—'))
        nd_val   = float(h.get('%NoDispo', 0) or 0)
        traf_val = h.get('Trafico', 0) or 0
        corp_hotels = df_nd[df_nd['CorpName'] == corp_nm].head(3) if 'CorpName' in df_nd.columns else pd.DataFrame()
        drill = _build_drill(
            corps=corps.head(3) if len(corps) else None,
            dests=dests.head(3) if len(dests) else None,
            hotels=corp_hotels if len(corp_hotels) > 1 else df_nd.head(3),
            val_fn=lambda r: _pct(r.get('%NoDispo', r.get('val_driver', r.get('%NoDispo_dest', 0)))),
            vol_fn=lambda r: _traf(r.get('Trafico', r.get('vol_total', 0))),
            report_type='rnd'
        )
        middle.append(_finding(
            _pct(nd_val),
            f'{hotel_nm[:35]} · Tasa No Dispo Crítica {_sev(banda_nodispo(nd_val))}',
            f'{_traf(traf_val)} búsquedas sin disponibilidad · {corp_nm} · escalamiento urgente.<br>{drill}'
        ))

    # f4: Corp #1 score NoDispo (si N>1 hoteles)
    if len(corps):
        top_corp = corps.iloc[0]
        corp_nm  = str(top_corp.get('CorpName', '—'))
        n_h      = int(top_corp.get('n_hoteles_sc_c', 0))
        if n_h >= 2:
            corp_hotels = df_nd[df_nd['CorpName'] == corp_nm].head(5) if 'CorpName' in df_nd.columns else pd.DataFrame()
            drill_corp = _build_drill(
                hotels=corp_hotels if len(corp_hotels) else df_nd.head(5),
                val_fn=lambda r: _pct(r.get('%NoDispo', r.get('val_driver', 0))),
                vol_fn=lambda r: _traf(r.get('Trafico', r.get('vol_total', 0))),
                report_type='rnd'
            )
            middle.append(_finding(
                str(n_h),
                f'{corp_nm[:30]} · {n_h} hoteles Tasa No Dispo Crítica+',
                f'Revisión de cupos y paridad por cuenta KAM.<br>{drill_corp}'
            ))

    # f5: Destino #1 score NoDispo + hotel driver
    if len(dests):
        top_dest = dests.iloc[0]
        dest_nm  = str(top_dest.get('Destino', '—'))
        h_drv    = str(top_dest.get('hotel_driver', '—'))
        c_drv    = str(top_dest.get('corp_driver', '—'))
        vol_dest = float(top_dest.get('vol_total', 0))
        drill_dest = _build_drill(
            dests=dests.head(3) if len(dests) else None,
            hotels=df_nd[df_nd.get('Destino', pd.Series([''] * len(df_nd))) == dest_nm].head(5) if 'Destino' in df_nd.columns else None,
            val_fn=lambda r: _pct(r.get('%NoDispo', r.get('val_driver', r.get('%NoDispo_dest', 0)))),
            vol_fn=lambda r: _traf(r.get('Trafico', r.get('vol_total', 0))),
            report_type='rnd'
        )
        middle.append(_finding(
            _traf(vol_dest),
            f'{dest_nm[:30]} · Destino con mayor tráfico sin disponibilidad',
            f'Driver: {h_drv[:30]} ({c_drv}) · estrategia de apertura de destino.<br>{drill_dest}'
        ))

    # f6: País #1 score NoDispo (si hay datos de país y volumen suficiente)
    if len(paises):
        top_pais = paises.iloc[0]
        pais_nm  = str(top_pais.get('PaisDestino', '—'))
        n_d_pais = int(top_pais.get('n_hoteles_sc_c', 0))  # aquí hoteles por país
        vol_pais = float(top_pais.get('vol_total', 0))
        if vol_pais >= UMBRAL_PAIS:
            middle.append(_finding(
                _traf(vol_pais),
                f'{pais_nm[:25]} · País con mayor tráfico NoDispo Crítica+',
                f'{n_d_pais} hoteles SC+C en {pais_nm} · revisión contractual regional recomendada.'
            ))

    # f7: IPM contexto de impacto revenue
    if ipm > 0:
        middle.append(_finding(
            _ipm(ipm),
            f'IPM {lbl} · {_sev(banda_ipm_gl)}',
            f'Ingreso Por Millón de búsquedas en {lbl}. '
            f'{"NoDispo alta es el driver principal de revenue perdido." if n_nd >= N_MIN_COHORTE else "Benchmark de impacto económico."}'
        ))

    # f8: Destinos Exitosa (positivo)
    if len(dests_ok) > 0:
        n_ok = len(dests_ok)
        middle.append(_finding(
            str(n_ok),
            f'Destinos con disponibilidad Exitosa (<3%) en {lbl}',
            f'Referencia de buena práctica · mantener operación estable.'
        ))

    # f9: WoW deterioro
    if not _nan(nd_wow) and nd_wow > 0.2:
        middle.append(_finding(
            wow_arrow(nd_wow),
            f'Tasa No Dispo {lbl} empeoró WoW',
            f'NoDispo sube {nd_wow:.2f}pp vs semana anterior · identificar causa raíz.'.replace('.', ',')
        ))

    # Padding
    while len(middle) < 8:
        n_rev = int(sev_nd.get('Revisar', 0))
        n_sin = int(sev_nd.get('Sin Conversión', payload.get('sev_rpm', {}).get('Sin Conversión', 0)))
        if n_rev > 0 and len(middle) < 8:
            middle.append(_finding(
                str(n_rev),
                f'Hoteles {lbl} · NoDispo Revisar (5-20%)',
                f'Monitorear evolución · potencial deterioro a Crítica si no se interviene.'
            ))
        if n_sin > 0 and len(middle) < 8:
            middle.append(_finding(
                str(n_sin),
                f'Hoteles {lbl} Sin Conversión (BKGS=0)',
                'Sin booking · cohorte de diagnóstico técnico/contractual.'
            ))
        if len(middle) < 8:
            middle.append(_finding('—', 'Cohorte insuficiente', 'Sin findings adicionales esta semana.'))

    findings = [f1] + middle[:8] + [f10]
    return findings[:10]


# ── Action Plan CR ────────────────────────────────────────────────────────────

def build_action_plan_cr(payload):
    """
    Genera 3-6 acciones para Plan de Acción CR.
    Solo se incluyen acciones cuyas condiciones de datos se cumplen.
    """
    from areas_catalogo import AREAS_CATALOGO

    ef     = payload['ef_global']
    cv     = payload['cv_global']
    n_ef   = payload['n_ef_sc_c']
    n_bk   = payload['n_bk_sc_c']
    scope  = payload['scope']
    lbl    = payload['canasta_label']
    wn     = payload['week_num']
    df_ef  = payload['hoteles_ef_sc_c']
    df_bk  = payload['hoteles_bk_sc_c']
    corps  = payload['corps_ef_sc_c']
    chans  = payload['channels_ef_sc_c']

    def area(key):
        return AREAS_CATALOGO.get(key, {}).get('label', key).split('/')[0].strip()

    actions = []

    # QW-1: Escalar hotel #1 Eficacia SC+C
    if len(df_ef):
        h = df_ef.iloc[0]
        cr_unicos = float(h.get('CR_Unicos', 0) or 0)
        if cr_unicos >= UMBRAL_MIN_CR:
            hotel_nm = clean_hotel_name(str(h.get('Hotel', '—')))
            corp_nm  = str(h.get('CorpName', '—'))
            ef_val   = float(h.get('Eficacia', 0) or 0)
            banda_h  = banda_eficacia(ef_val)
            # Drilldown: top 5 hoteles SC+C del mismo corp
            corp_h = df_ef[df_ef['CorpName'] == corp_nm].head(5) if 'CorpName' in df_ef.columns else pd.DataFrame()
            sub = _build_drill(
                corps=corps.head(3) if len(corps) else None,
                hotels=corp_h if len(corp_h) > 1 else df_ef.head(3),
                val_fn=lambda r: _pct(r.get('Eficacia', r.get('val_driver', 0))),
                vol_fn=lambda r: f'{_cr(r.get("CR_Unicos", r.get("vol_total", 0)))} CR',
                report_type='cr'
            )
            actions.append({
                'c':      'qw',
                'o':      area('supply_optimization'),
                'a':      f'Escalar {hotel_nm[:50]} ({corp_nm}) — Error Rate {_pct(ef_val)} {_sev(banda_h)} '
                          f'con {_cr(cr_unicos)} CR únicos en {lbl}. Driver técnico de baja ConvRate.',
                't':      'Conectividad',
                'p':      f'W{wn}',
                'metrica': 'Error Rate > 85%',
                'score':  float(df_ef.iloc[0].get('score', 0)),
                'target': hotel_nm,
                '_sub':   sub,
            })

    # QW-2: Escalar hotel #1 Bookability SC+C (si distinto de QW-1)
    if len(df_bk):
        top_ef_hotel = clean_hotel_name(str(df_ef.iloc[0].get('Hotel', ''))) if len(df_ef) else ''
        h_bk = df_bk.iloc[0]
        bk_nm   = clean_hotel_name(str(h_bk.get('Hotel', '—')))
        bk_bkgs = float(h_bk.get('Bookings', 0) or 0)
        if bk_nm != top_ef_hotel and bk_bkgs >= UMBRAL_MIN_CR:
            bk_val  = float(h_bk.get('Bookability', 0) or 0)
            corp_bk = str(h_bk.get('CorpName', '—'))
            actions.append({
                'c':      'qw',
                'o':      area('supply_optimization_tps'),
                'a':      f'Diagnóstico interface {bk_nm[:50]} ({corp_bk}) — Bookability {_pct(bk_val)} '
                          f'con {int(bk_bkgs):,} bookings afectados. Revisar provider y configuración.'.replace(',', '.'),
                't':      'Bookability',
                'p':      f'W{wn}',
                'metrica': 'Bookability > 97%',
                'score':  float(df_bk.iloc[0].get('score', 0)),
                'target': bk_nm,
                '_sub':   '',
            })

    # MP-1: Saneamiento cohorte SC+C Eficacia
    if n_ef >= N_MIN_COHORTE:
        target_n = n_ef // 2
        actions.append({
            'c':      'mp',
            'o':      area('supply_optimization'),
            'a':      f'Plan de saneamiento para {n_ef} hoteles SC+C de Error Rate en {lbl}. '
                      f'Target: {target_n} hoteles a banda Revisar.',
            't':      'Saneamiento',
            'p':      '3 semanas',
            'metrica': f'{target_n} hoteles a Revisar',
            'score':  0.5,
            'target': f'{n_ef} hoteles',
            '_sub':   '',
        })

    # MP-2: ConvRate baja sin problema de Eficacia/BK
    if cv < 0.015 and ef >= 0.93 and n_bk == 0:
        actions.append({
            'c':      'mp',
            'o':      area('supply_comercial_wholesale'),
            'a':      f'Conv Rate {lbl} en {_pct(cv)} — Error Rate sana indica problema de tarifa/paridad. '
                      f'Revisión comercial urgente.',
            't':      'Paridad',
            'p':      '2 semanas',
            'metrica': 'Conv Rate ≥ 2,5%',
            'score':  0.4,
            'target': lbl,
            '_sub':   '',
        })

    # ES-1: Corp con mayor concentración hoteles SC+C
    if len(corps):
        top_corp = corps.iloc[0]
        corp_nm  = str(top_corp.get('CorpName', '—'))
        n_h      = int(top_corp.get('n_hoteles_sc_c', 0))
        if n_h >= N_MIN_COHORTE:
            corp_h = df_ef[df_ef['CorpName'] == corp_nm].head(5) if 'CorpName' in df_ef.columns and len(df_ef) else pd.DataFrame()
            sub_corp = _build_drill(
                hotels=corp_h if len(corp_h) else None,
                val_fn=lambda r: _pct(r.get('Eficacia', r.get('val_driver', 0))),
                vol_fn=lambda r: f'{_cr(r.get("CR_Unicos", r.get("vol_total", 0)))} CR',
                report_type='cr'
            )
            actions.append({
                'c':      'es',
                'o':      area('supply_comercial_supply_optimization'),
                'a':      f'{corp_nm} concentra {n_h} hoteles SC+C de Error Rate en {lbl}. '
                          f'Escalamiento KAM + revisión técnica por cuenta.',
                't':      'KAM',
                'p':      'Q3',
                'metrica': f'-50% hoteles SC+C en {corp_nm}',
                'score':  float(top_corp.get('score', 0)),
                'target': corp_nm,
                '_sub':   sub_corp,
            })

    # ES-2: Channel peor Error Rate SC+C
    if len(chans):
        top_chan = chans.iloc[0]
        chan_col = 'ExternalProviderName' if 'ExternalProviderName' in top_chan.index else top_chan.index[0]
        chan_nm  = str(top_chan.get(chan_col, top_chan.iloc[0] if len(top_chan) else '—'))
        val_c    = float(top_chan.get('val_driver', 0.7) or 0)
        actions.append({
            'c':      'es',
            'o':      area('supply_comercial_wholesale'),
            'a':      f'Channel {chan_nm} en banda {banda_eficacia(val_c)} — Error Rate {_pct(val_c)}. '
                      f'Auditoría técnica y renegociación SLA.',
            't':      'Channel SLA',
            'p':      'Q3',
            'metrica': 'Error Rate > 93%',
            'score':  float(top_chan.get('score', 0)),
            'target': chan_nm,
            '_sub':   '',
        })

    return actions[:6]


# ── Action Plan RND ───────────────────────────────────────────────────────────

def build_action_plan_rnd(payload):
    """
    Genera 3-6 acciones para Plan de Acción RND.
    """
    from areas_catalogo import AREAS_CATALOGO

    nd      = payload['nd_global']
    ipm     = payload['ipm_global']
    n_nd    = payload['n_nd_sc_c']
    scope   = payload['scope']
    lbl     = payload['canasta_label']
    wn      = payload['week_num']
    df_nd   = payload['hoteles_nd_sc_c']
    corps   = payload['corps_nd_sc_c']
    dests   = payload['dests_nd_sc_c']
    paises  = payload['paises_nd_sc_c']

    def area(key):
        return AREAS_CATALOGO.get(key, {}).get('label', key).split('/')[0].strip()

    actions = []

    # QW-1: Escalar hotel #1 NoDispo SC+C
    if len(df_nd):
        h = df_nd.iloc[0]
        traf = float(h.get('Trafico', 0) or 0)
        if traf >= UMBRAL_MIN_RND:
            hotel_nm = clean_hotel_name(str(h.get('Hotel', '—')))
            corp_nm  = str(h.get('CorpName', '—'))
            nd_val   = float(h.get('%NoDispo', 0) or 0)
            banda_h  = banda_nodispo(nd_val)
            corp_h   = df_nd[df_nd['CorpName'] == corp_nm].head(5) if 'CorpName' in df_nd.columns else pd.DataFrame()
            sub = _build_drill(
                corps=corps.head(3) if len(corps) else None,
                dests=dests.head(3) if len(dests) else None,
                hotels=corp_h if len(corp_h) > 1 else df_nd.head(3),
                val_fn=lambda r: _pct(r.get('%NoDispo', r.get('val_driver', 0))),
                vol_fn=lambda r: _traf(r.get('Trafico', r.get('vol_total', 0))),
                report_type='rnd'
            )
            actions.append({
                'c':      'qw',
                'o':      area('supply_comercial_supply_optimization'),
                'a':      f'Escalar {hotel_nm[:50]} ({corp_nm}) — Tasa No Dispo {_pct(nd_val)} {_sev(banda_h)} '
                          f'con {_traf(traf)} búsquedas sin disponibilidad. Apertura de cupos urgente.',
                't':      'Disponibilidad',
                'p':      f'W{wn}',
                'metrica': 'NoDispo < 20%',
                'score':  float(df_nd.iloc[0].get('score', 0)),
                'target': hotel_nm,
                '_sub':   sub,
            })

    # QW-2: Corp SC+C con más hoteles NoDispo
    if len(corps):
        top_corp = corps.iloc[0]
        corp_nm  = str(top_corp.get('CorpName', '—'))
        n_h      = int(top_corp.get('n_hoteles_sc_c', 0))
        if n_h >= 2:
            corp_h = df_nd[df_nd['CorpName'] == corp_nm].head(5) if 'CorpName' in df_nd.columns and len(df_nd) else pd.DataFrame()
            sub_corp = _build_drill(
                hotels=corp_h if len(corp_h) else None,
                val_fn=lambda r: _pct(r.get('%NoDispo', r.get('val_driver', 0))),
                vol_fn=lambda r: _traf(r.get('Trafico', r.get('vol_total', 0))),
                report_type='rnd'
            )
            actions.append({
                'c':      'qw',
                'o':      area('supply_optimization_tps'),
                'a':      f'{corp_nm} tiene {n_h} hoteles con Tasa No Dispo Crítica+ en {lbl}. '
                          f'Revisión de cupos y paridad por cuenta.',
                't':      'Cupos',
                'p':      f'W{wn}',
                'metrica': 'NoDispo < 20% en todos',
                'score':  float(top_corp.get('score', 0)),
                'target': corp_nm,
                '_sub':   sub_corp,
            })

    # MP-1: Saneamiento cohorte SC+C NoDispo
    if n_nd >= N_MIN_COHORTE:
        target_n = n_nd // 2
        actions.append({
            'c':      'mp',
            'o':      area('supply_optimization'),
            'a':      f'Plan de saneamiento para {n_nd} hoteles con Tasa No Dispo Crítica+ en {lbl}. '
                      f'Target: {target_n} hoteles a banda Revisar.',
            't':      'Saneamiento',
            'p':      '3 semanas',
            'metrica': f'{target_n} hoteles a Revisar',
            'score':  0.5,
            'target': f'{n_nd} hoteles',
            '_sub':   '',
        })

    # MP-2: IPM bajo + NoDispo como driver
    if ipm < 650 and n_nd >= N_MIN_COHORTE:
        actions.append({
            'c':      'mp',
            'o':      area('supply_comercial_wholesale'),
            'a':      f'IPM {lbl} en {_ipm(ipm)} — Tasa No Dispo Crítica+ es el driver de revenue perdido. '
                      f'Resolver disponibilidad antes de intervención comercial.',
            't':      'Revenue',
            'p':      '2 semanas',
            'metrica': f'IPM ≥ $650 post-saneamiento',
            'score':  0.4,
            'target': lbl,
            '_sub':   '',
        })

    # ES-1: Destino #1 NoDispo SC+C
    if len(dests):
        top_dest = dests.iloc[0]
        dest_nm  = str(top_dest.get('Destino', '—'))
        vol_dest = float(top_dest.get('vol_total', 0))
        h_drv    = str(top_dest.get('hotel_driver', '—'))
        c_drv    = str(top_dest.get('corp_driver', '—'))
        if vol_dest >= UMBRAL_MIN_RND:
            dest_h = df_nd[df_nd.get('Destino', pd.Series([''] * len(df_nd))) == dest_nm].head(5) if 'Destino' in df_nd.columns else pd.DataFrame()
            sub_dest = _build_drill(
                dests=dests.head(3) if len(dests) else None,
                hotels=dest_h if len(dest_h) else df_nd.head(3),
                val_fn=lambda r: _pct(r.get('%NoDispo', r.get('val_driver', r.get('%NoDispo_dest', 0)))),
                vol_fn=lambda r: _traf(r.get('Trafico', r.get('vol_total', 0))),
                report_type='rnd'
            )
            actions.append({
                'c':      'es',
                'o':      area('supply_comercial_supply_optimization'),
                'a':      f'Destino {dest_nm} — Tasa No Dispo Crítica (driver: {h_drv[:25]} · {c_drv}). '
                          f'Estrategia de apertura de destino.',
                't':      'Destino',
                'p':      'Q3',
                'metrica': 'NoDispo destino < 5%',
                'score':  float(top_dest.get('score', 0)),
                'target': dest_nm,
                '_sub':   sub_dest,
            })

    # ES-2: País SC+C con mayor volumen afectado
    if len(paises):
        top_pais = paises.iloc[0]
        pais_nm  = str(top_pais.get('PaisDestino', '—'))
        vol_pais = float(top_pais.get('vol_total', 0))
        n_h_pais = int(top_pais.get('n_hoteles_sc_c', 0))
        if vol_pais >= UMBRAL_PAIS:
            actions.append({
                'c':      'es',
                'o':      area('supply_comercial_wholesale'),
                'a':      f'País {pais_nm} — {n_h_pais} hoteles con Tasa No Dispo Crítica+ · {_traf(vol_pais)} '
                          f'búsquedas sin disponibilidad. Revisión contractual regional.',
                't':      'País',
                'p':      'Q3',
                'metrica': 'NoDispo país < 5%',
                'score':  float(top_pais.get('score', 0)),
                'target': pais_nm,
                '_sub':   '',
            })

    return actions[:6]


# ── Carryover ─────────────────────────────────────────────────────────────────

def build_carryover(payload_curr, payload_prev=None, report_type='cr'):
    """
    Detecta hoteles que persisten en SC+C respecto a la semana anterior.
    Retorna [] si payload_prev es None.
    Máximo 5 items.
    """
    if payload_prev is None:
        return []

    df_curr = payload_curr.get('hoteles_ef_sc_c' if report_type == 'cr' else 'hoteles_nd_sc_c', pd.DataFrame())
    df_prev = payload_prev.get('hoteles_ef_sc_c' if report_type == 'cr' else 'hoteles_nd_sc_c', pd.DataFrame())

    if len(df_curr) == 0 or len(df_prev) == 0:
        return []

    wow_col = 'Eficacia_WoW_pp' if report_type == 'cr' else 'NoDispo_WoW_pp'
    hotel_col = 'Hotel'
    if hotel_col not in df_curr.columns:
        return []

    prev_hotels = set(df_prev[hotel_col].apply(clean_hotel_name).tolist()) if hotel_col in df_prev.columns else set()
    result = []

    for _, row in df_curr.iterrows():
        hotel_nm = clean_hotel_name(str(row.get(hotel_col, '')))
        if hotel_nm in prev_hotels:
            wow_val = row.get(wow_col, None)
            wow_str = wow_arrow(wow_val) if not _nan(wow_val) else '—'
            banda   = row.get('BandaEficacia' if report_type == 'cr' else 'BandaNoDispo', '—')
            corp    = str(row.get('CorpName', '—'))
            result.append({
                'a':      f'{hotel_nm} ({corp}) — persiste en {_sev(banda)} · WoW {wow_str}',
                'o':      'Supply Optimization',
                'estado': 'Persistente',
            })
            if len(result) >= 5:
                break

    return result


# ── Función de conveniencia: genera re/plan/co para build_canasta_data ────────

def build_editorial_cr(D, scope='global', bk_data=None, payload_prev=None):
    """
    Función de conveniencia para usar desde render_cr_p2.py.
    Retorna (re_items, plan, co) listos para insertar en CR_D[scope].
    """
    try:
        payload = build_payload_cr(D, scope=scope, bk_data=bk_data)
        re_items = build_findings_cr(payload)
        plan     = build_action_plan_cr(payload)
        co       = build_carryover(payload, payload_prev, 'cr')
        # Normalizar formato de re_items al formato del JS (n/t/d en lugar de numero/titulo/desc)
        re_out = [{'n': f.get('n', f.get('numero', '')),
                   't': f.get('t', f.get('titulo', '')),
                   'd': f.get('d', f.get('desc', ''))} for f in re_items]
        return re_out, plan, co
    except Exception as e:
        import traceback
        print(f'[editorial_engine] build_editorial_cr ERROR scope={scope}: {e}')
        traceback.print_exc()
        return [], [], []


def build_editorial_rnd(D, scope='global', payload_prev=None):
    """
    Función de conveniencia para usar desde render_rnd_p2.py.
    Retorna (re_items, plan, co) listos para insertar en RND_D[scope].
    """
    try:
        payload  = build_payload_rnd(D, scope=scope)
        re_items = build_findings_rnd(payload)
        plan     = build_action_plan_rnd(payload)
        co       = build_carryover(payload, payload_prev, 'rnd')
        re_out   = [{'n': f.get('n', f.get('numero', '')),
                     't': f.get('t', f.get('titulo', '')),
                     'd': f.get('d', f.get('desc', ''))} for f in re_items]
        return re_out, plan, co
    except Exception as e:
        import traceback
        print(f'[editorial_engine] build_editorial_rnd ERROR scope={scope}: {e}')
        traceback.print_exc()
        return [], [], []
