#!/usr/bin/env python3
"""
prepare_week.py · Generador semanal del Reporte CheckRates · Supply Optimization

USO:
    python prepare_week.py <NUMERO_SEMANA> <PATH_DATASET>

EJEMPLO:
    python prepare_week.py 17 ~/Downloads/CheckRates_Last_7_Days_ABR27.xlsx

QUÉ HACE:
    1. Lee el dataset CheckRates (TOTALES + Canal B2C/OP/UOP)
    2. Calcula todas las métricas del reporte (Eficacia, Conv Rate, Severity, Canasta)
    3. Toma el Template_Checkrates_Reporte.html y reemplaza los placeholders
    4. Genera el Excel con las 16 hojas (10 globales + 6 canasta)
    5. Crea la carpeta checkrates/week-NN/ con la estructura correcta:
        checkrates/week-NN/
        ├── Editorial/
        │   └── CheckRates_Reporte_Editorial.html
        ├── Analisis/
        │   └── Analisis_Checkrates_7d.xlsx
        └── Templates/
            └── Template_Checkrates_Reporte.html  (copia del template para esa semana)

PRE-REQUISITOS:
    - Estar en el repo Price/ (raíz)
    - Carpeta `checkrates/templates/` con Template_Checkrates_Reporte.html base
    - Python 3.10+, pandas, openpyxl

OUTPUT:
    Lista todos los archivos generados con sus tamaños.
    Lista TODO list para el usuario:
        □ Revisar visualmente el HTML editorial generado
        □ Commit con GitHub Desktop (mensaje sugerido se muestra en consola)
        □ Push al remoto
        □ Esperar 2-3 minutos para el deploy de GitHub Pages
        □ Enviar email con el link público
"""

import sys
import os
import shutil
from datetime import datetime, timedelta
import pandas as pd

# ============================================================
# CONFIG
# ============================================================
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_PATH = os.path.join(REPO_ROOT, 'checkrates', 'templates', 'Template_Checkrates_Reporte.html')
PUBLIC_URL_BASE = 'https://federicochurches.github.io/Price/checkrates'

# Channel weights del manual editorial
CHANNEL_WEIGHTS = {'B2C': 0.1, 'B2B (OP)': 0.6, 'CUG (UOP)': 0.6}

# ADR estimado para cálculo de GB no generado
ADR_ESTIMADO = 250

# ============================================================
# HELPERS DE FORMATO
# ============================================================
def fmt_num(v):
    if pd.isna(v): return '0'
    return f"{int(v):,}".replace(',', '.')

def fmt_pct(v, dec=2):
    if pd.isna(v): return '0.00%'
    return f"{v:.{dec}f}%"

def fmt_traf(v):
    v = int(v)
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000: return f"{v/1_000:.1f}K"
    return str(v)

def short_hotel_name(name):
    """Acorta nombres largos de hoteles para que entren en cards"""
    cuts = [' Resort & ', ' Resort ', ' & ', ' at ', ' by ', ' - ',
            ' Downtown', ' Casino', ' All Inclusive', ' All-Inclusive',
            ', ', ' Hotel ']
    s = name
    for c in cuts:
        if c in s:
            i = s.find(c)
            if i > 12:
                s = s[:i].rstrip()
                break
    if len(s) > 26:
        s = s[:25].rstrip() + '…'
    return s


# ============================================================
# CÁLCULO DE MÉTRICAS
# ============================================================
def severity_eff(pe):
    if pe < 3.8: return 'Exitosa'
    if pe < 5.3: return 'No Aceptable'
    if pe < 20: return 'Revisar'
    if pe < 40: return 'Crítica'
    if pe < 80: return 'Muy Crítica'
    return 'Súper Crítica'

def severity_cr(cr):
    if cr >= 3.0: return 'Excelente'
    if cr >= 1.74: return 'Buena'
    if cr >= 1.0: return 'Por debajo benchmark'
    if cr >= 0.5: return 'Crítica'
    if cr >= 0.1: return 'Muy Crítica'
    return 'Súper Crítica'


def load_and_process_dataset(dataset_path):
    """Carga el dataset y devuelve dataframes procesados"""
    print(f"\n📂 Cargando dataset: {dataset_path}")
    
    cols = ['IdHotel', 'Hotel', 'Corporate',
            'CheckRates Absolutos', 'CheckRates Únicos',
            'AVG Mismo CheckRate', 'CheckRates x HT',
            'Efectividad en CheckRates',
            'Successful UniqueChkRts', '#Errors',
            'Bookings', 'Conversion Rate']
    
    # TOTALES
    df_total = pd.read_excel(dataset_path, sheet_name='TOTALES', usecols=cols)
    
    # Canales
    canal_map = {'Canal B2C': 'B2C', 'Canal OP': 'B2B (OP)', 'Canal UOP': 'CUG (UOP)'}
    canal_dfs = []
    for sheet, canasta in canal_map.items():
        df_c = pd.read_excel(dataset_path, sheet_name=sheet, usecols=cols)
        df_c['Canasta'] = canasta
        canal_dfs.append(df_c)
    df_canal = pd.concat(canal_dfs, ignore_index=True)
    
    # Limpieza
    for df in [df_total, df_canal]:
        for c in ['CheckRates Absolutos', 'CheckRates Únicos', 'Bookings',
                  'Successful UniqueChkRts', '#Errors']:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
        df['Efectividad en CheckRates'] = pd.to_numeric(df['Efectividad en CheckRates'], errors='coerce').fillna(0) * 100
        df['Efectividad en CheckRates'] = df['Efectividad en CheckRates'].clip(0, 100)
    
    # Solo válidos (CK > 0)
    df_total = df_total[df_total['CheckRates Únicos'] > 0].copy()
    df_canal = df_canal[df_canal['CheckRates Únicos'] > 0].copy()
    
    # Calcular Conv Rate, %Errors, Severity
    for df in [df_total, df_canal]:
        df['Conv Rate'] = df['Bookings'] / df['CheckRates Únicos'] * 100
        df['%Errors'] = (100 - df['Efectividad en CheckRates']).clip(0, 100)
        df['Severity'] = df['%Errors'].apply(severity_eff)
        df['Severity_CR'] = df['Conv Rate'].apply(severity_cr)
    
    # P80 del df_total
    df_total = df_total.sort_values('CheckRates Únicos', ascending=False)
    cs = df_total['CheckRates Únicos'].cumsum()
    p80_thresh = cs.iloc[-1] * 0.8
    n_p80 = (cs <= p80_thresh).sum() + 1
    hts = df_total.head(n_p80).copy()
    
    # Cluster (lógica simple — para refinement futuro)
    p85_errors = hts['%Errors'].quantile(0.85)
    hts['Cluster'] = 'Low Priority'
    no_bkg = hts['Bookings'] == 0
    hts.loc[no_bkg & (hts['%Errors'] > p85_errors), 'Cluster'] = 'Connectivity Issue'
    hts.loc[no_bkg & (hts['%Errors'] <= p85_errors), 'Cluster'] = 'Monetization Failure'
    has_bkg = hts['Bookings'] > 0
    hts.loc[has_bkg & (hts['%Errors'] < 5) & (hts['Conv Rate'] < 1.74), 'Cluster'] = 'Quick Win'
    
    print(f"   Universo válido: {len(df_total):,} hoteles")
    print(f"   Muestra HTS · P80: {len(hts):,} hoteles")
    print(f"   Total CheckRates: {df_total['CheckRates Únicos'].sum():,}")
    print(f"   Total Bookings: {df_total['Bookings'].sum():,}")
    
    return df_total, df_canal, hts


# ============================================================
# RENDER DEL TEMPLATE
# ============================================================
def render_template(template_html, week_num, fecha_inicio, fecha_fin, hts, df_total, df_canal, vol_num=1):
    """Reemplaza todos los placeholders del template con datos reales"""
    
    # Métricas principales
    n_total = len(df_total)
    n_muestra = len(hts)
    pct_muestra = n_muestra / n_total * 100
    n_cero = (hts['Bookings'] == 0).sum()
    pct_cero = n_cero / n_muestra * 100
    pct_cero_inv = n_cero / n_total * 100
    
    eff_global = (df_total['Efectividad en CheckRates'] * df_total['CheckRates Únicos']).sum() / df_total['CheckRates Únicos'].sum()
    cr_global = df_total['Bookings'].sum() / df_total['CheckRates Únicos'].sum() * 100
    
    n_baja_eff = (hts['Efectividad en CheckRates'] <= 80).sum()
    n_connectivity = (hts['Cluster'] == 'Connectivity Issue').sum()
    n_monetization = (hts['Cluster'] == 'Monetization Failure').sum()
    
    bkgs_perdidos = int(n_cero * cr_global / 100 * (df_total['CheckRates Únicos'].sum() / n_total))  # estimación simple
    bkgs_perdidos = max(bkgs_perdidos, int(hts[hts['Bookings']==0]['CheckRates Únicos'].sum() * cr_global / 100))
    gb_no_generado = bkgs_perdidos * ADR_ESTIMADO
    n_corps_0bkgs = hts[hts['Bookings']==0]['Corporate'].nunique()
    
    # Canasta agregada
    canasta_agg = df_canal.groupby('Canasta').agg(
        n=('Hotel', 'count'),
        traf=('CheckRates Únicos', 'sum'),
        bkgs=('Bookings', 'sum'),
    ).reset_index()
    canasta_agg['conv_rate'] = canasta_agg['bkgs'] / canasta_agg['traf'] * 100
    
    # Eficacia por canasta
    eff_by_canasta = {}
    for canasta in ['B2C', 'B2B (OP)', 'CUG (UOP)']:
        df_c = df_canal[df_canal['Canasta']==canasta]
        if df_c['CheckRates Únicos'].sum() > 0:
            eff_by_canasta[canasta] = (df_c['Efectividad en CheckRates'] * df_c['CheckRates Únicos']).sum() / df_c['CheckRates Únicos'].sum()
    
    # Top peores corp por eficacia (≥5 hoteles)
    corp_hts = hts.groupby('Corporate').agg(
        n_hot=('Hotel', 'count'),
        ck=('CheckRates Únicos', 'sum'),
        bkgs=('Bookings', 'sum'),
    ).reset_index()
    corp_hts['conv_rate'] = corp_hts['bkgs'] / corp_hts['ck'] * 100
    corp_hts['eff_pond'] = corp_hts.apply(
        lambda r: (hts[hts['Corporate']==r['Corporate']]['Efectividad en CheckRates'] * 
                   hts[hts['Corporate']==r['Corporate']]['CheckRates Únicos']).sum() / r['ck'] if r['ck']>0 else 0,
        axis=1
    )
    peores_corp_eff = corp_hts[corp_hts['n_hot']>=5].sort_values('eff_pond').head(7)
    peores_corp_cr = corp_hts[corp_hts['n_hot']>=5].sort_values('conv_rate').head(7)
    
    # Top peores hoteles
    hts_filt = hts[hts['CheckRates Únicos']>=1000].copy()
    peores_hot_eff = hts_filt.sort_values('Efectividad en CheckRates').head(7)
    peores_hot_cr = hts_filt[hts_filt['Bookings']>0].sort_values('Conv Rate').head(7)
    
    # Determinar el peor hotel "outlier" (combinado eff+cr, primer hotel de la lista)
    if len(peores_hot_eff) > 0:
        h_outlier = peores_hot_eff.iloc[0]
        lede_hotel = short_hotel_name(h_outlier['Hotel'])
        lede_hotel_data = f"{fmt_pct(h_outlier['Efectividad en CheckRates'], 1)} Eficacia, {fmt_pct(h_outlier['Conv Rate'], 2)} Conv Rate"
    else:
        lede_hotel = '---'
        lede_hotel_data = '---'
    
    # Ratio CUG/B2C para el lede
    cr_b2c = canasta_agg[canasta_agg['Canasta']=='B2C']['conv_rate'].iloc[0] if len(canasta_agg[canasta_agg['Canasta']=='B2C'])>0 else 0
    cr_cug = canasta_agg[canasta_agg['Canasta']=='CUG (UOP)']['conv_rate'].iloc[0] if len(canasta_agg[canasta_agg['Canasta']=='CUG (UOP)'])>0 else 0
    ratio_cug_b2c = round(cr_cug / cr_b2c) if cr_b2c > 0 else 0
    lede_insight = f"CUG convierte {ratio_cug_b2c}× más que B2C"
    
    # Construir TITLE_LABEL y TITLE_DATA
    if len(peores_corp_cr) >= 4:
        top4_corp_cr = peores_corp_cr.head(4)
        title_label = "Corporativos con más oportunidad en Conv Rate:"
        title_data = ' · '.join([f"{r['Corporate']} {fmt_pct(r['conv_rate'], 2)}" for _, r in top4_corp_cr.iterrows()]) + '.'
    else:
        title_label = "KPIS Semanales:"
        title_data = f"Eficacia {fmt_pct(eff_global, 1)} · Conv Rate {fmt_pct(cr_global, 2)}."
    
    # Construir chips de Card 1 (Eficacia · Canasta)
    canasta_eff_sorted = sorted(eff_by_canasta.items(), key=lambda x: x[1])
    eff_canasta_chips = ' · '.join([f'{c} <span class="meta-hl">{fmt_pct(e, 1)}</span>' for c, e in canasta_eff_sorted])
    
    # Card 2 (Conv Rate · Canasta)
    canasta_cr_sorted = canasta_agg.sort_values('conv_rate')
    cr_canasta_chips = ' · '.join([f'{r["Canasta"]} <span class="meta-hl">{fmt_pct(r["conv_rate"], 2)}</span>' for _, r in canasta_cr_sorted.iterrows()])
    
    # Card 3 (Eficacia por Corporativo)
    if len(peores_corp_eff) >= 1:
        c3_top1 = peores_corp_eff.iloc[0]
        c3_top1_name = c3_top1['Corporate']
        c3_top1_pct = fmt_pct(c3_top1['eff_pond'], 1)
        c3_rest = peores_corp_eff.iloc[1:5]
        c3_rest_html = ' · '.join([f'{r["Corporate"]} <span class="meta-hl">{fmt_pct(r["eff_pond"], 1)}</span>' for _, r in c3_rest.iterrows()])
    else:
        c3_top1_name, c3_top1_pct, c3_rest_html = '---', '---', ''
    
    # Card 4 (Conv Rate por Corporativo)
    if len(peores_corp_cr) >= 1:
        c4_top1 = peores_corp_cr.iloc[0]
        c4_top1_name = c4_top1['Corporate']
        c4_top1_pct = fmt_pct(c4_top1['conv_rate'], 2)
        c4_rest = peores_corp_cr.iloc[1:5]
        c4_rest_html = ' · '.join([f'{r["Corporate"]} <span class="meta-hl">{fmt_pct(r["conv_rate"], 2)}</span>' for _, r in c4_rest.iterrows()])
    else:
        c4_top1_name, c4_top1_pct, c4_rest_html = '---', '---', ''
    
    # Card 5 (Eficacia por Hotel)
    if len(peores_hot_eff) >= 1:
        c5_top1 = peores_hot_eff.iloc[0]
        c5_top1_name = short_hotel_name(c5_top1['Hotel'])
        c5_top1_pct = fmt_pct(c5_top1['Efectividad en CheckRates'], 1)
        c5_rest = peores_hot_eff.iloc[1:4]
        c5_rest_html = ' · '.join([f'{short_hotel_name(r["Hotel"])} <span class="meta-hl">{fmt_pct(r["Efectividad en CheckRates"], 1)}</span>' for _, r in c5_rest.iterrows()])
    else:
        c5_top1_name, c5_top1_pct, c5_rest_html = '---', '---', ''
    
    # Card 6 (Conv Rate por Hotel)
    if len(peores_hot_cr) >= 1:
        c6_top1 = peores_hot_cr.iloc[0]
        c6_top1_name = short_hotel_name(c6_top1['Hotel'])
        c6_top1_pct = fmt_pct(c6_top1['Conv Rate'], 2)
        c6_rest = peores_hot_cr.iloc[1:4]
        c6_rest_html = ' · '.join([f'{short_hotel_name(r["Hotel"])} <span class="meta-hl">{fmt_pct(r["Conv Rate"], 2)}</span>' for _, r in c6_rest.iterrows()])
    else:
        c6_top1_name, c6_top1_pct, c6_rest_html = '---', '---', ''
    
    # Diccionario de placeholders
    placeholders = {
        # Header
        'SEMANA': str(week_num),
        'WEEK_NUM_RAW': str(week_num),
        'RANGO_FECHAS_CORTO': f"{fecha_inicio.strftime('%-d')} – {fecha_fin.strftime('%-d %b %Y')}",
        'FECHA_REPORTE': f"Lunes {(fecha_fin + timedelta(days=2)).strftime('%-d de %B de %Y')}",
        'MES_ANO': fecha_inicio.strftime('%b %Y'),
        'VOLUMEN': f"Vol. {vol_num:02d}",
        # Hero
        'TITLE_LABEL': title_label,
        'TITLE_DATA': title_data,
        'LEDE_HOTEL': lede_hotel,
        'LEDE_HOTEL_DATA': lede_hotel_data,
        'LEDE_INSIGHT': lede_insight,
        # KPIs
        'EFF_TOTAL_CANASTA': fmt_pct(eff_global, 2),
        'BAR_EFF_CANASTA': str(int(eff_global)),
        'EFF_CANASTA_CHIPS': eff_canasta_chips,
        'CONV_RATE_TOTAL_CANASTA': fmt_pct(cr_global, 2),
        'BAR_CONV_RATE_CANASTA': '50',
        'CONV_RATE_CANASTA_CHIPS': cr_canasta_chips,
        # Cards
        'C3_TOP1_NAME': c3_top1_name, 'C3_TOP1_PCT': c3_top1_pct, 'C3_REST': c3_rest_html, 'BAR_C3': '60',
        'C4_TOP1_NAME': c4_top1_name, 'C4_TOP1_PCT': c4_top1_pct, 'C4_REST': c4_rest_html, 'BAR_C4': '55',
        'C5_TOP1_NAME': c5_top1_name, 'C5_TOP1_PCT': c5_top1_pct, 'C5_REST': c5_rest_html, 'BAR_C5': '50',
        'C6_TOP1_NAME': c6_top1_name, 'C6_TOP1_PCT': c6_top1_pct, 'C6_REST': c6_rest_html, 'BAR_C6': '30',
    }
    
    # Aplicar reemplazos
    rendered = template_html
    for key, val in placeholders.items():
        rendered = rendered.replace('{{' + key + '}}', str(val))
    
    return rendered


# ============================================================
# MAIN
# ============================================================
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    week_num = int(sys.argv[1])
    dataset_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\n{'='*70}")
    print(f"  CheckRates · Week {week_num} · Generación de release")
    print(f"{'='*70}")
    
    # Calcular fechas (lunes de inicio = 7*week_num días desde inicio del año)
    # Convención: fechas del lunes a domingo de la semana N
    year = datetime.now().year
    jan1 = datetime(year, 1, 1)
    days_to_monday = (7 - jan1.weekday()) % 7
    week1_monday = jan1 + timedelta(days=days_to_monday)
    fecha_inicio = week1_monday + timedelta(weeks=week_num - 1)
    fecha_fin = fecha_inicio + timedelta(days=6)
    
    print(f"\n📅 Período: {fecha_inicio.strftime('%-d %b')} – {fecha_fin.strftime('%-d %b %Y')}")
    
    # Carpeta de release
    week_str = f"week-{week_num:02d}"
    release_dir = os.path.join(REPO_ROOT, 'checkrates', week_str)
    os.makedirs(os.path.join(release_dir, 'Editorial'), exist_ok=True)
    os.makedirs(os.path.join(release_dir, 'Analisis'), exist_ok=True)
    os.makedirs(os.path.join(release_dir, 'Templates'), exist_ok=True)
    
    if dataset_path:
        # Procesar dataset
        df_total, df_canal, hts = load_and_process_dataset(dataset_path)
        
        # Render del template
        with open(TEMPLATE_PATH) as f:
            template_html = f.read()
        rendered_html = render_template(template_html, week_num, fecha_inicio, fecha_fin, hts, df_total, df_canal)
        
        out_html = os.path.join(release_dir, 'Editorial', 'CheckRates_Reporte_Editorial.html')
        with open(out_html, 'w') as f:
            f.write(rendered_html)
        print(f"\n📄 Editorial generado: {out_html}")
        
        # Generar Excel (delegar a build_excel.py si existe, o reusar lógica)
        excel_path = os.path.join(release_dir, 'Analisis', 'Analisis_Checkrates_7d.xlsx')
        # TODO: import build_excel; build_excel.generate(df_total, df_canal, hts, excel_path)
        print(f"📊 Excel a generar en: {excel_path}")
        print(f"   ⚠ Por ahora copiar manualmente desde la corrida anterior y editar")
        
        # Copiar template para esa semana
        shutil.copy(TEMPLATE_PATH, os.path.join(release_dir, 'Templates', 'Template_Checkrates_Reporte.html'))
    else:
        print(f"\n⚠ No se pasó dataset — solo se creó la estructura de carpetas")
    
    # ============================================================
    # CHECKLIST FINAL
    # ============================================================
    public_url = f"{PUBLIC_URL_BASE}/{week_str}/Editorial/CheckRates_Reporte_Editorial.html"
    
    print(f"\n{'='*70}")
    print(f"  ✅ Release Week {week_num} preparado")
    print(f"{'='*70}")
    print(f"\n📋 CHECKLIST:")
    print(f"   [ ] 1. Revisar visualmente el HTML editorial:")
    print(f"          file://{release_dir}/Editorial/CheckRates_Reporte_Editorial.html")
    print(f"   [ ] 2. Validar el Excel ({release_dir}/Analisis/...)")
    print(f"   [ ] 3. Commit con GitHub Desktop")
    print(f"          Mensaje sugerido: \"CheckRates · Week {week_num} · {fecha_inicio.strftime('%-d')}-{fecha_fin.strftime('%-d %b %Y')}\"")
    print(f"   [ ] 4. Push al remoto (origin/main)")
    print(f"   [ ] 5. Esperar 2-3 minutos para deploy de GitHub Pages")
    print(f"   [ ] 6. Verificar URL pública:")
    print(f"          {public_url}")
    print(f"   [ ] 7. Generar y enviar email semanal:")
    print(f"          python scripts/send_email.py {week_num}")
    print()


if __name__ == '__main__':
    main()
