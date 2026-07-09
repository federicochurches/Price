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

    # Bonus WoW (asimétrico — solo empeora sube el score). bonus_wow es un
    # indicador 0/1; el peso de 10% se aplica una sola vez, en el return.
    wow_val = row.get(WOW_COL.get(metric, ''), None)
    if _nan(wow_val):
        bonus_wow = 0.0
    elif report_type == 'rnd':
        bonus_wow = 1.0 if float(wow_val) > 0 else 0.0   # NoDispo sube = empeora
    else:
        bonus_wow = 1.0 if float(wow_val) < 0 else 0.0   # Eficacia baja = empeora

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

    # Corps — mostrar la CANTIDAD DE HOTELES del cohorte (pedido Fede · W26),
    # con fallback al formato métrica·volumen si no viene n_hoteles_sc_c.
    if corps is not None and len(corps):
        corp_col = 'CorpName' if 'CorpName' in corps.columns else corps.columns[0]
        _hasn_c = 'n_hoteles_sc_c' in corps.columns
        rows = [
            (str(r[corp_col])[:30],
             (f"{int(r['n_hoteles_sc_c'])} hoteles" if (_hasn_c and pd.notna(r.get('n_hoteles_sc_c')))
              else f'{val_fn(r)} \u00b7 {vol_fn(r)}'))
            for _, r in corps.head(max_rows).iterrows()
        ]
        sections += _drill_section('Corps', _COL_CORPS, rows)

    # Destinos — idem (cantidad de hoteles)
    if dests is not None and len(dests):
        dest_col = 'Destino' if 'Destino' in dests.columns else dests.columns[0]
        _hasn_d = 'n_hoteles_sc_c' in dests.columns
        rows = [
            (str(r[dest_col])[:28],
             (f"{int(r['n_hoteles_sc_c'])} hoteles" if (_hasn_d and pd.notna(r.get('n_hoteles_sc_c')))
              else f'{val_fn(r)} \u00b7 {vol_fn(r)}'))
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


def _drill_cd(dfh, report_type, scope='global', n=5, sort_col=None, ascending=True,
              val_fn=None, vol_fn=None, vol_col=None, pre_corps=None, pre_dests=None,
              topn_dims=False):
    """Drill completo Corps + Destinos + Hoteles desde un df de hoteles.
    - pre_corps/pre_dests: dims ya derivadas del payload (se usan si vienen).
    - Si no vienen, se derivan del propio df (agregando 'score' si falta).
    - topn_dims=True (PA): las dims Corps/Destinos se derivan SOLO de los n hoteles
      mostrados (no del cohorte completo) → el conteo es "sobre los 5", no sobre el total.
    Las val_fn/vol_fn por defecto resuelven tanto filas de hotel
    (Eficacia/%NoDispo · CR_Unicos/Trafico) como de dimensión (val_driver/vol_total)."""
    if dfh is None or not len(dfh):
        return ''
    d = dfh.copy()
    if sort_col and sort_col in d.columns:
        d = d.sort_values(sort_col, ascending=ascending)
    metric = 'nodispo' if report_type == 'rnd' else 'eficacia'
    vc = vol_col or ('Trafico' if report_type == 'rnd' else 'CR_Unicos')
    # PA: forzar derivación desde los n hoteles mostrados (ignora pre_corps/pre_dests del cohorte)
    if topn_dims:
        pre_corps = pre_dests = None
        dim_src = d.head(n)
    else:
        dim_src = d
    corps, dests = pre_corps, pre_dests
    if corps is None or dests is None:
        dd = dim_src
        if 'score' not in dd.columns:
            try:
                dd = _add_scores(dd, metric, scope, report_type, vol_col=vc)
            except Exception:
                dd = dd.copy(); dd['score'] = 0.0
        if corps is None and 'CorpName' in dd.columns:
            corps = _derive_dim(dd, 'CorpName', vc)
        if dests is None and 'Destino' in dd.columns:
            dests = _derive_dim(dd, 'Destino', vc)
    if val_fn is None:
        if report_type == 'rnd':
            val_fn = lambda r: _pct(r.get('%NoDispo', r.get('val_driver', 0)) or 0)
        else:
            val_fn = lambda r: _pct(r.get('Eficacia', r.get('val_driver', 0)) or 0)
    if vol_fn is None:
        if report_type == 'rnd':
            vol_fn = lambda r: _traf(r.get('Trafico', r.get('vol_total', 0)) or 0)
        else:
            vol_fn = lambda r: f'{_cr(r.get("CR_Unicos", r.get("vol_total", 0)) or 0)} CR'
    return _build_drill(
        corps=corps if (corps is not None and len(corps)) else None,
        dests=dests if (dests is not None and len(dests)) else None,
        hotels=d.head(n),
        val_fn=val_fn, vol_fn=vol_fn, report_type=report_type,
    )


def _drill_spread(spread_h, df_all=None, n=5, topn=None):
    """Drill del spread inter-canasta (Corps + Destinos + Hoteles).
    spread20_hotels solo trae Hotel + nd_* + spread_pp → se enriquece con
    CorpName/Destino desde df_all (match por nombre limpio de hotel).
    topn (PA): agrupa Corps/Destinos solo sobre los topn hoteles mostrados."""
    if spread_h is None or not len(spread_h):
        return ''
    d = spread_h.copy()
    if 'spread_pp' in d.columns:
        d = d.sort_values('spread_pp', ascending=False)
    # PA: dims sobre los topn hoteles mostrados · RE: sobre todo el cohorte
    d_dim = d.head(topn) if topn else d
    corps_rows, dests_rows = [], []
    if df_all is not None and len(df_all) and 'Hotel' in df_all.columns:
        meta_cols = [c for c in ['Hotel', 'CorpName', 'Destino'] if c in df_all.columns]
        meta = df_all[meta_cols].copy()
        meta['_hk'] = meta['Hotel'].apply(lambda x: clean_hotel_name(str(x)))
        meta = meta.drop_duplicates('_hk')
        d_dim = d_dim.copy()
        d_dim['_hk'] = d_dim['Hotel'].apply(lambda x: clean_hotel_name(str(x)))
        keep = [c for c in ['_hk', 'CorpName', 'Destino'] if c in meta.columns]
        dm = d_dim.merge(meta[keep], on='_hk', how='left')
        if 'CorpName' in dm.columns:
            g = (dm.dropna(subset=['CorpName'])
                   .groupby('CorpName')['spread_pp'].agg(['size', 'max'])
                   .reset_index().sort_values('max', ascending=False))
            corps_rows = [(str(r['CorpName'])[:30],
                           f"{int(r['size'])} hoteles \u00b7 m\u00e1x {r['max']:.0f}pp".replace('.', ','))
                          for _, r in g.head(n).iterrows()]
        if 'Destino' in dm.columns:
            g2 = (dm.dropna(subset=['Destino'])
                    .groupby('Destino')['spread_pp'].agg(['size', 'max'])
                    .reset_index().sort_values('max', ascending=False))
            dests_rows = [(str(r['Destino'])[:28],
                           f"{int(r['size'])} hoteles \u00b7 m\u00e1x {r['max']:.0f}pp".replace('.', ','))
                          for _, r in g2.head(n).iterrows()]
    hotels_rows = [
        (clean_hotel_name(str(r.get('Hotel', '\u2014')))[:30],
         f"{r.get('spread_pp', 0):.0f}pp".replace('.', ','))
        for _, r in d.head(n).iterrows()
    ]
    out = _drill_section('Corps', _COL_CORPS, corps_rows)
    out += _drill_section('Destinos', _COL_DESTS, dests_rows)
    out += _drill_section('Hoteles', _COL_HOTELES, hotels_rows)
    return out


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
        # Las keys reales del pickle CR son 'B2C'/'B2B-OP'/'CUG' (no 'b2c'/'op'/'cug')
        scope_key_cr = {'b2c': 'B2C', 'op': 'B2B-OP', 'cug': 'CUG'}
        c_data = canasta_data.get(scope_key_cr.get(scope, scope), {})
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
    if scope == 'global':
        sev_ef = D.get('sev_ef_p80', {})
        sev_cv = D.get('sev_cv_p80', {})
    else:
        sev_ef = c_data.get('sev_ef', D.get('sev_ef_p80', {}))
        sev_cv = c_data.get('sev_cv', D.get('sev_cv_p80', {}))

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

    # ── Cohorte "0 Reservas y sin problemas de disponibilidad" ──────────────────
    _GOOD_ND = {'Exitosa', 'Aceptable'}   # %NoDispo ≤ 5% → disponibilidad sana
    zero_ok_hotels = pd.DataFrame()
    if len(df) and 'Bookings' in df.columns and 'BandaNoDispo' in df.columns:
        _bk0 = pd.to_numeric(df['Bookings'], errors='coerce').fillna(0) == 0
        _m = _bk0 & df['BandaNoDispo'].isin(_GOOD_ND)
        zero_ok_hotels = df[_m].copy()
        if len(zero_ok_hotels) and 'Trafico' in zero_ok_hotels.columns:
            zero_ok_hotels = zero_ok_hotels.sort_values('Trafico', ascending=False)
    n_zero_ok = len(zero_ok_hotels)

    # ── Spread de NoDispo entre canastas (>20pp) — concepto global ──────────────
    spread20_hotels = pd.DataFrame()
    n_spread20 = 0
    try:
        cdat = D.get('CANASTA', {})
        parts = []
        for ck in ['b2c', 'op', 'cug']:
            cp = cdat.get(ck, {}).get('p80')
            if isinstance(cp, pd.DataFrame) and 'Hotel' in cp.columns and '%NoDispo' in cp.columns:
                tmp = cp[['Hotel', '%NoDispo']].copy()
                tmp['Hotel'] = tmp['Hotel'].apply(lambda x: clean_hotel_name(str(x)))
                tmp = (tmp.groupby('Hotel', as_index=False)['%NoDispo'].mean()
                          .rename(columns={'%NoDispo': f'nd_{ck}'}))
                parts.append(tmp)
        if len(parts) >= 2:
            from functools import reduce
            merged = reduce(lambda a, b: a.merge(b, on='Hotel', how='outer'), parts)
            nd_cols = [c for c in merged.columns if c.startswith('nd_')]
            present = merged[nd_cols].notna().sum(axis=1)
            merged['spread_pp'] = (merged[nd_cols].max(axis=1) - merged[nd_cols].min(axis=1)) * 100
            sp = merged[(present >= 2) & (merged['spread_pp'] > 20)].copy()
            spread20_hotels = sp.sort_values('spread_pp', ascending=False)
            n_spread20 = len(spread20_hotels)
    except Exception:
        pass

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
        'zero_ok_hotels':    zero_ok_hotels,
        'n_zero_ok':         n_zero_ok,
        'spread20_hotels':   spread20_hotels,
        'n_spread20':        n_spread20,
        'sev_nd':            sev_nd,
        'sev_rpm':           sev_rpm,
        'scope':             scope,
        'canasta_label':     canasta_label,
        'week_num':          WEEK_NUM,
        'week_prev':         WEEK_PREV,
    }


# ── Findings CR ───────────────────────────────────────────────────────────────

def _finding(numero, titulo, desc=''):
    # El título del RE trae la cantidad de hoteles adelante (pedido Fede · W26):
    # "4 Hoteles con Performance de 0%". numero = conteo del cohorte.
    _t = f'{numero} {titulo}' if (numero not in (None, '', '—')) else titulo
    return {'n': numero, 't': _t, 'd': desc}


def build_findings_cr(payload):
    """CR · Resumen Ejecutivo — formato canónico limpio (igual que RND).
       1) Hoteles con Performance Crítica  (banda Crítica + Súper Crítica)
       2) Hoteles con 0 Conversión  (Bookings=0 con CheckRates)
       3) Hoteles con Bookability Crítica  (solo Global, si hay BK)
       Cada finding lleva su drilldown de hoteles embebido.
    """
    scope  = payload['scope']
    lbl    = payload['canasta_label']
    n_ef   = payload['n_ef_sc_c']
    n_bk   = payload['n_bk_sc_c']
    df_all = payload.get('df_all', pd.DataFrame())
    df_ef  = payload['hoteles_ef_sc_c']
    df_bk  = payload['hoteles_bk_sc_c']
    corps_ef = payload.get('corps_ef_sc_c')
    dests_ef = payload.get('dests_ef_sc_c')

    # Umbral "Performance OK" (Eficacia ≥ 85%, fuera de Crítica/Súper Crítica)
    _OK_EF = 0.85

    # Cohorte Performance de 0%: Eficacia == 0 con CheckRates (todos los CR fallan)
    df_p0 = pd.DataFrame()
    if len(df_all) and 'Eficacia' in df_all.columns and 'CR_Unicos' in df_all.columns:
        df_p0 = df_all[(df_all['Eficacia'] <= 0) & (df_all['CR_Unicos'] > 0)].copy()
        if len(df_p0):
            df_p0 = df_p0.sort_values('CR_Unicos', ascending=False)
    n_p0 = len(df_p0)

    # Cohorte sin reserva con Performance OK: Bookings=0 · CR>0 · Eficacia ≥ 85%
    df_zero_ok = pd.DataFrame()
    if len(df_all) and 'Bookings' in df_all.columns:
        m0 = (df_all['Bookings'] == 0)
        if 'CR_Unicos' in df_all.columns:
            m0 = m0 & (df_all['CR_Unicos'] > 0)
        if 'Eficacia' in df_all.columns:
            m0 = m0 & (df_all['Eficacia'] >= _OK_EF)
        df_zero_ok = df_all[m0].copy()
        if len(df_zero_ok) and 'CR_Unicos' in df_zero_ok.columns:
            df_zero_ok = df_zero_ok.sort_values('CR_Unicos', ascending=False)
    n_zero_ok = len(df_zero_ok)

    # Drill #1 (Performance de 0%): dims derivadas del cohorte
    drill1 = _drill_cd(df_p0, 'cr', scope, sort_col='CR_Unicos', ascending=False)
    # Drill #2 (sin reserva + Performance OK): dims derivadas del cohorte
    drill2 = _drill_cd(df_zero_ok, 'cr', scope, sort_col='CR_Unicos', ascending=False)

    findings = [
        _finding(
            str(n_p0),
            'Hoteles con Performance de 0%',
            f'Performance 0% (todos los CheckRates fallan) en {lbl} · falla total de conectividad · '
            'escalamiento técnico prioritario.'
            + (f'<br>{drill1}' if drill1 else '')
        ),
        _finding(
            str(n_zero_ok),
            'Hoteles con ninguna reserva y Performance OK',
            f'Performance buena (≥85%) pero 0 bookings en {lbl} · revisar tarifa, paridad y competitividad.'
            + (f'<br>{drill2}' if drill2 else '')
        ),
    ]

    # Item cross-canasta (Bookability): solo a nivel Global
    if scope == 'global' and n_bk > 0:
        drill3 = _drill_cd(
            df_bk, 'cr', scope, sort_col='Bookability', ascending=True, vol_col='Bookings',
            val_fn=lambda r: _pct(r.get('Bookability', r.get('val_driver', 0)) or 0),
            vol_fn=lambda r: f'{int(r.get("Bookings", r.get("vol_total", 0)) or 0):,} bkgs'.replace(',', '.'),
        )
        findings.append(_finding(
            str(n_bk),
            'Hoteles con Bookability Crítica',
            'Banda Crítica o Súper Crítica de Bookability · falla de interface o provider · '
            'diagnóstico técnico.'
            + (f'<br>{drill3}' if drill3 else '')
        ))

    return findings


# ── Findings RND ──────────────────────────────────────────────────────────────

def build_findings_rnd(payload):
    """RND · Resumen Ejecutivo — formato canónico W25 (3 findings).
       1) Hoteles con Tasa de No Dispo Crítica  (banda Crítica + Súper Crítica)
       2) Hoteles con 0 Reservas y sin problemas de disponibilidad
       3) Hoteles con variación de NoDispo > 20pp entre canastas  (solo Global)
       Cada finding lleva su drilldown de hoteles embebido (igual que CR).
    """
    scope      = payload['scope']
    lbl        = payload['canasta_label']
    n_sc_c     = payload['n_nd_sc_c']
    n_zero_ok  = payload.get('n_zero_ok', 0)
    n_spread20 = payload.get('n_spread20', 0)
    df_sc_c    = payload.get('hoteles_nd_sc_c', pd.DataFrame())
    zero_ok    = payload.get('zero_ok_hotels', pd.DataFrame())
    spread_h   = payload.get('spread20_hotels', pd.DataFrame())
    corps_nd   = payload.get('corps_nd_sc_c')
    dests_nd   = payload.get('dests_nd_sc_c')

    # Drill #1 (NoDispo Crítica): dims pre-derivadas del payload (corp+dest+hotel)
    drill1 = _drill_cd(df_sc_c, 'rnd', scope, sort_col='%NoDispo', ascending=False,
                       pre_corps=corps_nd, pre_dests=dests_nd)
    # Drill #2 (0 Reservas): dims derivadas del propio cohorte
    drill2 = _drill_cd(zero_ok, 'rnd', scope, sort_col='%NoDispo', ascending=False)

    findings = [
        _finding(
            str(n_sc_c),
            'Hoteles con Tasa de No Dispo Crítica',
            f'Banda Crítica o Súper Crítica (%NoDispo > 20%) en {lbl} · apertura de cupos prioritaria.'
            + (f'<br>{drill1}' if drill1 else '')
        ),
        _finding(
            str(n_zero_ok),
            'Hoteles con 0 Reservas y sin problemas de disponibilidad',
            'Disponibilidad sana (%NoDispo ≤ 5%) pero 0 bookings · revisar conversión y competitividad.'
            + (f'<br>{drill2}' if drill2 else '')
        ),
    ]

    # Item cross-canasta: solo aplica a nivel Global
    if scope == 'global':
        df_all_sp = payload.get('df_all', pd.DataFrame())
        drill3 = _drill_spread(spread_h, df_all_sp) if len(spread_h) else ''
        findings.append(_finding(
            str(n_spread20),
            'Hoteles con variación de NoDispo mayor a 20pp entre canastas',
            'Disponibilidad inconsistente entre B2C / Opaco / Ultra Opaco · '
            'revisar segmentación de tráfico con Wholesale.'
            + (f'<br>{drill3}' if drill3 else '')
        ))

    return findings


# ── Action Plan CR ────────────────────────────────────────────────────────────

def build_action_plan_cr(payload):
    """CR · Plan de Acción — formato canónico limpio (igual que RND)."""
    from areas_catalogo import AREAS_CATALOGO

    scope  = payload['scope']
    lbl    = payload['canasta_label']
    wn     = payload['week_num']
    n_bk   = payload['n_bk_sc_c']
    df_all = payload.get('df_all', pd.DataFrame())
    df_ef  = payload['hoteles_ef_sc_c']
    df_bk  = payload['hoteles_bk_sc_c']
    corps_ef = payload.get('corps_ef_sc_c')
    dests_ef = payload.get('dests_ef_sc_c')

    def area(key):
        return AREAS_CATALOGO.get(key, {}).get('label', key).split('/')[0].strip()

    _OK_EF, _EXITOSA_EF = 0.85, 0.97
    actions = []

    # PA-1 · Corregir los 5 hoteles con Performance de 0% (Eficacia == 0, CR>0)
    df_p0 = pd.DataFrame()
    if len(df_all) and 'Eficacia' in df_all.columns and 'CR_Unicos' in df_all.columns:
        df_p0 = df_all[(df_all['Eficacia'] <= 0) & (df_all['CR_Unicos'] > 0)].copy()
        if len(df_p0):
            df_p0 = df_p0.sort_values('CR_Unicos', ascending=False)
    actions.append({
        'c': 'qw', 'o': area('supply_optimization'),
        'a': 'Corregir los 5 hoteles con Performance de 0%.',
        't': 'Conectividad', 'p': f'W{wn}', 'metrica': 'Performance > 0%',
        'score': 1.0, 'target': '5 hoteles',
        '_sub': _drill_cd(df_p0.head(5), 'cr', scope, topn_dims=True, sort_col='CR_Unicos', ascending=False),
    })

    # PA-2 · Corregir los 5 hoteles con peor Performance (Eficacia > 0, excluye los 0%)
    worst = pd.DataFrame()
    if len(df_all) and 'Eficacia' in df_all.columns:
        poolw = df_all[df_all['Eficacia'] > 0].copy()
        if 'CR_Unicos' in poolw.columns:
            poolw = poolw[poolw['CR_Unicos'] >= UMBRAL_MIN_CR]
        poolw = poolw.sort_values('Eficacia', ascending=True)
        worst = poolw.head(5)
    if len(worst):
        actions.append({
            'c': 'qw', 'o': area('supply_optimization_tps'),
            'a': 'Corregir los 5 hoteles con peor Performance.',
            't': 'Conectividad', 'p': f'W{wn}', 'metrica': 'Performance \u2265 85%',
            'score': 0.9, 'target': '5 hoteles',
            '_sub': _drill_cd(worst, 'cr', scope, topn_dims=True, sort_col='Eficacia', ascending=True),
        })

    # PA-3 · Corregir los 5 hoteles con 0 Conversión y buen Performance
    df_zero_ok = pd.DataFrame()
    if len(df_all) and 'Bookings' in df_all.columns:
        m0 = (df_all['Bookings'] == 0)
        if 'CR_Unicos' in df_all.columns:
            m0 = m0 & (df_all['CR_Unicos'] > 0)
        if 'Eficacia' in df_all.columns:
            m0 = m0 & (df_all['Eficacia'] >= _OK_EF)
        df_zero_ok = df_all[m0].copy()
        if len(df_zero_ok) and 'CR_Unicos' in df_zero_ok.columns:
            df_zero_ok = df_zero_ok.sort_values('CR_Unicos', ascending=False)
    actions.append({
        'c': 'mp', 'o': area('supply_comercial_wholesale'),
        'a': 'Corregir los 5 hoteles con 0 Conversión y buen Performance.',
        't': 'Conversión', 'p': '2 semanas', 'metrica': 'Generar primeras reservas',
        'score': 0.7, 'target': '5 hoteles',
        '_sub': _drill_cd(df_zero_ok.head(5), 'cr', scope, topn_dims=True, sort_col='CR_Unicos', ascending=False),
    })

    # PA-4 · Analizar los hoteles con Performance exitosa pero sin conversión
    df_zero_exitosa = pd.DataFrame()
    if len(df_all) and 'Bookings' in df_all.columns and 'Eficacia' in df_all.columns:
        me = (df_all['Bookings'] == 0) & (df_all['Eficacia'] >= _EXITOSA_EF)
        if 'CR_Unicos' in df_all.columns:
            me = me & (df_all['CR_Unicos'] > 0)
        df_zero_exitosa = df_all[me].copy()
        if len(df_zero_exitosa) and 'CR_Unicos' in df_zero_exitosa.columns:
            df_zero_exitosa = df_zero_exitosa.sort_values('CR_Unicos', ascending=False)
    actions.append({
        'c': 'mp', 'o': area('supply_optimization'),
        'a': 'Analizar los hoteles con Performance exitosa pero sin conversión.',
        't': 'Análisis', 'p': '2 semanas', 'metrica': 'Diagnóstico tarifa/paridad',
        'score': 0.5, 'target': lbl,
        '_sub': _drill_cd(df_zero_exitosa, 'cr', scope, topn_dims=True, sort_col='CR_Unicos', ascending=False),
    })

    # PA-5 · Auditar las interfaces con Bookability crítica — solo Global
    if scope == 'global' and len(df_bk):
        sub5 = _drill_cd(
            df_bk, 'cr', scope, topn_dims=True, sort_col='Bookability', ascending=True, vol_col='Bookings',
            val_fn=lambda r: _pct(r.get('Bookability', r.get('val_driver', 0)) or 0),
            vol_fn=lambda r: f'{int(r.get("Bookings", r.get("vol_total", 0)) or 0):,} bkgs'.replace(',', '.'),
        )
        actions.append({
            'c': 'es', 'o': area('supply_optimization_tps'),
            'a': 'Auditar las interfaces con Bookability crítica.',
            't': 'Bookability', 'p': 'Q3', 'metrica': 'Bookability \u2265 97%',
            'score': 0.4, 'target': f'{n_bk} hoteles', '_sub': sub5,
        })

    return actions


# ── Action Plan RND ───────────────────────────────────────────────────────────

def build_action_plan_rnd(payload):
    """RND · Plan de Acción — formato canónico W25 (5 acciones)."""
    from areas_catalogo import AREAS_CATALOGO

    scope      = payload['scope']
    lbl        = payload['canasta_label']
    wn         = payload['week_num']
    df         = payload.get('df_all', pd.DataFrame())
    corps      = payload['corps_nd_sc_c']
    dests_nd   = payload.get('dests_nd_sc_c')
    zero_ok    = payload.get('zero_ok_hotels', pd.DataFrame())
    spread_h   = payload.get('spread20_hotels', pd.DataFrame())
    n_spread20 = payload.get('n_spread20', 0)

    def area(key):
        return AREAS_CATALOGO.get(key, {}).get('label', key).split('/')[0].strip()

    actions = []

    # PA-1 · Corregir los 5 hoteles con más problemas de disponibilidad
    worst = pd.DataFrame()
    pool = pd.DataFrame()
    if len(df) and '%NoDispo' in df.columns:
        pool = df.copy()
        if 'Trafico' in pool.columns:
            pool = pool[pool['Trafico'] >= 1000]    # piso anti-ruido de micro-tráfico
        pool = pool.sort_values('%NoDispo', ascending=False)
        worst = pool.head(5)
    actions.append({
        'c': 'qw', 'o': area('supply_comercial_supply_optimization'),
        'a': 'Corregir los 5 hoteles con más problemas de disponibilidad.',
        't': 'Disponibilidad', 'p': f'W{wn}', 'metrica': 'NoDispo < 20%',
        'score': 1.0, 'target': '5 hoteles',
        '_sub': _drill_cd(worst, 'rnd', scope, topn_dims=True, pre_corps=corps, pre_dests=dests_nd),
    })

    # PA-2 · Corregir los siguientes 5 hoteles (6-10) con más problemas — sin importar el corporativo
    worst2 = pool.iloc[5:10] if len(pool) > 5 else pd.DataFrame()
    if len(worst2):
        actions.append({
            'c': 'qw', 'o': area('supply_optimization_tps'),
            'a': 'Corregir los siguientes 5 hoteles con más problemas de disponibilidad.',
            't': 'Disponibilidad', 'p': f'W{wn}', 'metrica': 'NoDispo < 20%',
            'score': 0.9, 'target': '5 hoteles',
            '_sub': _drill_cd(worst2, 'rnd', scope, topn_dims=True, pre_corps=corps, pre_dests=dests_nd),
        })

    # PA-3 · Corregir los 5 hoteles con 0 Reservas y sin problemas de disponibilidad
    actions.append({
        'c': 'mp', 'o': area('supply_comercial_wholesale'),
        'a': 'Corregir los 5 hoteles con 0 Reservas y sin problemas de disponibilidad.',
        't': 'Conversión', 'p': '2 semanas', 'metrica': 'Generar primeras reservas',
        'score': 0.7, 'target': '5 hoteles',
        '_sub': _drill_cd(zero_ok, 'rnd', scope, topn_dims=True, sort_col='%NoDispo', ascending=False),
    })

    # PA-4 · Analizar los hoteles con disponibilidad pero sin conversión
    actions.append({
        'c': 'mp', 'o': area('supply_optimization'),
        'a': 'Analizar los hoteles con disponibilidad pero sin conversión.',
        't': 'Análisis', 'p': '2 semanas', 'metrica': 'Diagnóstico tarifa/paridad',
        'score': 0.5, 'target': lbl,
        '_sub': _drill_cd(zero_ok, 'rnd', scope, topn_dims=True, sort_col='%NoDispo', ascending=False),
    })

    # PA-5 · Revisar con Wholesale la segmentación de tráfico (spread entre canastas) — solo Global
    if scope == 'global':
        sub5 = _drill_spread(spread_h, df, topn=5) if len(spread_h) else ''
        actions.append({
            'c': 'es', 'o': area('supply_comercial_wholesale'),
            'a': f'Revisar con Wholesale la segmentación de tráfico en estos {n_spread20} hoteles '
                 f'con spread de No Disponibilidad de 20pp entre canastas.',
            't': 'Segmentación', 'p': 'Q3', 'metrica': 'Reducir spread < 20pp',
            'score': 0.4, 'target': f'{n_spread20} hoteles', '_sub': sub5,
        })

    return actions


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
    banda_col = 'BandaEficacia' if report_type == 'cr' else 'BandaNoDispo'
    hotel_col = 'Hotel'
    if hotel_col not in df_curr.columns:
        return []

    # Sets de corps por grupo de cuenta → área responsable real (no hardcodear)
    try:
        import accounts_config as _AC
        _gad = getattr(_AC, 'GLOBAL_ACCOUNTS', {})
        _ced = getattr(_AC, 'CUENTAS_ESTRATEGICAS', {})
        _ga = set(_gad.get('corps', [])) if isinstance(_gad, dict) else set(_gad)
        _ce = set(_ced.get('corps', [])) if isinstance(_ced, dict) else set(_ced)
    except Exception:
        _ga, _ce = set(), set()

    def _carry_area(corp, banda):
        if corp in _ga or corp in _ce:
            return 'Supply Comercial / Supply Optimization'   # cuenta gestionada
        if str(banda).startswith('S\u00faper'):                # Súper Crítica → escalación
            return 'Supply Optimization / TPS'
        return 'Supply Optimization'

    prev_wn = str(payload_prev.get('week_num', '') or '')
    ref_lbl = f'Desde W{prev_wn}' if prev_wn else 'Semana previa'
    prev_hotels = set(df_prev[hotel_col].apply(clean_hotel_name).tolist()) if hotel_col in df_prev.columns else set()

    def _carry_link(row):
        """Nombre de la acción del PA (semana previa) a la que el hotel está vinculado,
        según su cohorte. RND → disponibilidad · CR → Performance (0% o peor)."""
        if report_type == 'rnd':
            return 'Corregir los 5 hoteles con m\u00e1s problemas de disponibilidad'
        ef = row.get('Eficacia', None)
        try:
            if ef is not None and float(ef) <= 0:
                return 'Corregir los 5 hoteles con Performance de 0%'
        except (TypeError, ValueError):
            pass
        return 'Corregir los 5 hoteles con peor Performance'

    result = []

    for _, row in df_curr.iterrows():
        hotel_nm = clean_hotel_name(str(row.get(hotel_col, '')))
        if hotel_nm in prev_hotels:
            corp  = str(row.get('CorpName', '') or '').strip() or '\u2014'
            dest  = str(row.get('Destino', '') or '').strip()
            banda = row.get(banda_col, '')
            ref   = f'{corp} \u00b7 {dest}' if dest else corp
            result.append({
                't':    hotel_nm,                    # título (hotel)
                'a':    ref,                         # referencia: corporativo · destino
                'sub':  ref_lbl,                     # referencia temporal (Desde WNN)
                'o':    _carry_area(corp, banda),    # área responsable derivada
                'link': _carry_link(row),            # acción del PA previo a la que está vinculado
            })
            if len(result) >= 5:
                break

    return result


# ── Función de conveniencia: genera re/plan/co para build_canasta_data ────────

def build_editorial_cr(D, scope='global', bk_data=None, payload_prev=None, D_prev=None):
    """
    Función de conveniencia para usar desde render_cr_p2.py.
    Retorna (re_items, plan, co) listos para insertar en CR_D[scope].
    D_prev: pickle CR de la semana anterior (para carryover). Si se pasa,
    el payload previo se construye internamente para el mismo scope.
    """
    try:
        payload = build_payload_cr(D, scope=scope, bk_data=bk_data)
        if payload_prev is None and D_prev is not None:
            try:
                payload_prev = build_payload_cr(D_prev, scope=scope)
            except Exception:
                payload_prev = None
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


def build_editorial_rnd(D, scope='global', payload_prev=None, D_prev=None):
    """
    Función de conveniencia para usar desde render_rnd_p2.py.
    Retorna (re_items, plan, co) listos para insertar en RND_D[scope].
    D_prev: pickle RND de la semana anterior (para carryover).
    """
    try:
        payload  = build_payload_rnd(D, scope=scope)
        if payload_prev is None and D_prev is not None:
            try:
                payload_prev = build_payload_rnd(D_prev, scope=scope)
            except Exception:
                payload_prev = None
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
