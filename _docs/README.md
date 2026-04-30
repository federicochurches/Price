# PRICE · Release Workflow

Este documento describe el proceso semanal para generar y publicar los Reportes **CheckRates** y **RatesNoDispo** de Supply Optimization · PriceTravel.

---

## 📁 Estructura del repo

```
Price/                                          (repo público de GitHub Pages)
├── _manual/
│   ├── GUIA_EDITORIAL_RatesNoDispo.html        (guía editorial Rates No Dispo)
│   └── GUIA_EDITORIAL_CheckRates.html          (guía editorial CheckRates)
├── datasets/                                   (datasets originales — fuente)
│   ├── rates-nodispo/
│   │   └── week-NN/Rates_NoDispo_WNN.xlsx
│   └── checkrates/
│       └── week-NN/CheckRates_WNN.xlsx
├── rates-nodispo/
│   ├── _template/
│   │   └── Template_RatesNoDispo_Reporte.html
│   ├── week-16/
│   │   ├── Editorial/RatesNoDispo_Reporte_Editorial_Week16.html
│   │   └── Analisis/Analisis_Rates_NoDispo_7d.xlsx
│   └── week-17/
│       ├── Editorial/RatesNoDispo_Reporte_Editorial_Week17.html
│       └── Analisis/Analisis_Rates_NoDispo_7d.xlsx
├── checkrates/
│   ├── _template/
│   │   └── Template_Checkrates_Reporte.html
│   ├── week-16/
│   │   ├── Editorial/CheckRates_Reporte_Editorial_Week16.html
│   │   └── Analisis/Analisis_Checkrates_7d.xlsx
│   └── week-17/
│       ├── Editorial/CheckRates_Reporte_Editorial_Week17.html
│       └── Analisis/Analisis_Checkrates_7d.xlsx
├── scripts/                                    (NO se publica en Pages — solo local)
│   ├── prepare_week.py
│   ├── organize_datasets.py
│   └── send_email.py
├── email/                                      (NO se publica en Pages)
└── docs/
    └── README.md                               (este archivo)
```

### URLs públicas

- **Hub interno**: `https://analytics-desk.netlify.app/`
- **RatesNoDispo**: `https://federicochurches.github.io/Price/rates-nodispo/week-NN/Editorial/RatesNoDispo_Reporte_Editorial_WeekNN.html`
- **CheckRates**: `https://federicochurches.github.io/Price/checkrates/week-NN/Editorial/CheckRates_Reporte_Editorial_WeekNN.html`

---

## 🚀 Workflow semanal (Lunes)

### Paso 1 · Recibir datasets

El equipo envía los archivos Excel de la semana:
```
Rates_NoDispo_W<NN>.xlsx     (pestañas: Canasta ALL · B2C · OP · UOP)
CheckRates_W<NN>.xlsx        (pestañas: TOTALES · Canal B2C · Canal OP · Canal UOP)
```

### Paso 2 · Organizar datasets originales

```bash
python scripts/organize_datasets.py 17 ~/Downloads/Rates_NoDispo_W17.xlsx ~/Downloads/CheckRates_W17.xlsx
```

### Paso 3 · Generar reportes de la semana

```bash
python scripts/prepare_week.py 17 ~/Downloads/CheckRates_W17.xlsx
```

### Paso 4 · Revisar visualmente (checklist 10 min)

Ver guías editoriales en `_manual/`.

**RatesNoDispo — puntos clave:**
- P80 benchmark: `Trafico >= quantile(0.8)` del dataset total
- RPM benchmark global P80: calculado semanalmente (W17 = 2.60)
- No Dispo benchmark P80: calculado semanalmente (W17 = 3.6%)
- Colores: B2C=pink (#EA0074) · OP=celeste (#4FC3F4) · CUG=violeta (#5C469C)
- Filtros F3/F4/F5 canastas: n≥3 hoteles · bkgs≥5 · tráfico≥500K para hoteles
- WoW por canasta: disponible desde W16 dataset (cada hoja tiene canastas)
- F4 sin delta WoW (outlier estadístico por cambio brusco de NoDispo)

**CheckRates — puntos clave:**
- Por Corporativo: CK ≥ 500 · n ≥ 3 hoteles
- Menor Conv Rate: CK ≥ 2.000 · Bookings ≥ 3
- Colores: B2C=pink (#EA0074) · OP=violeta (#5C469C) · CUG=celeste (#4FC3F4)

### Paso 5 · Commit y Push (GitHub Desktop)

**RatesNoDispo:**
```
RatesNoDispo · Week 17 · 20-26 Abr 2026
```
Archivos:
- `rates-nodispo/week-17/Editorial/RatesNoDispo_Reporte_Editorial_Week17.html`
- `rates-nodispo/week-17/Analisis/Analisis_Rates_NoDispo_7d.xlsx`
- `datasets/rates-nodispo/week-17/Rates_NoDispo_W17.xlsx`

**CheckRates:**
```
CheckRates · Week 17 · 20-26 Abr 2026
```
Archivos:
- `checkrates/week-17/Editorial/CheckRates_Reporte_Editorial_Week17.html`
- `checkrates/week-17/Analisis/Analisis_Checkrates_7d.xlsx`
- `datasets/checkrates/week-17/CheckRates_W17.xlsx`

### Paso 6 · Actualizar Hub de Netlify

Actualizar las cards de CheckRates y RatesNoDispo con la URL de la nueva semana.

### Paso 7 · Enviar email

```bash
python scripts/send_email.py 17
```

---

## 🎨 Reglas de diseño · NO modificar sin actualizar la guía

### RatesNoDispo

| Elemento | Regla |
|---|---|
| Canasta B2C | Color `#EA0074` (pink) — TODO: nombres, valores, barras, headers, bordes |
| Canasta OP | Color `#4FC3F4` (celeste) — TODO |
| Canasta CUG | Color `#5C469C` (violeta) — TODO |
| P80 threshold | `Trafico >= quantile(0.8)` del dataset total |
| Filtro F3 canastas | n≥3 hoteles corp · bkgs≥5 |
| Filtro F4 canastas | tráfico hotel ≥ 500K |
| WoW canastas | Disponible desde W16 — F4 sin delta (outlier) |
| Plan de Acción COD | QW=pink soft · MP=violeta soft · ES=papel neutro |

### CheckRates

| Elemento | Regla |
|---|---|
| Canasta B2C | Color `#EA0074` — TODO |
| Canasta OP | Color `#5C469C` — TODO |
| Canasta CUG | Color `#4FC3F4` — TODO |
| Por Corporativo | CK ≥ 500 · n ≥ 3 hoteles |
| Menor Conv Rate | CK ≥ 2.000 · Bookings ≥ 3 |

---

## 📊 Destinatarios del email

| Campo | Valor |
|---|---|
| **De** | `federico.iglesias@pricetravel.com` |
| **Asunto** | `Supply Optimization · Reporte [CheckRates/RatesNoDispo] Week-NN` |
| **Para** | rafael.durand, bellanira.hernandez, maria.alejandra.rico, javier.parra, alonso.mis, ingrid.kuhnne, david.gamboa, hugo.ascencio, ext.jesus.lizarraga, alejandro.flores, gabriela.guerra, barbara.rodriguez |

---

## 📅 Calendario de releases

| Week | Periodo | RatesNoDispo | CheckRates |
|---|---|---|---|
| 16 | 13–19 Abr 2026 | ✅ Publicado | ✅ Publicado |
| 17 | 20–26 Abr 2026 | ✅ Publicado | ✅ Publicado |
| 18 | 27 Abr – 3 May 2026 | ⏳ Próximo | ⏳ Próximo |

---

## 📝 Changelog

- **v1.0** (2026-04-27): Release inicial Week 16. Estructura por canastas integrada.
- **v1.1** (2026-04-28): Week 17 CheckRates. Umbrales D (CK≥2K·Bkgs≥3), colores canasta definidos.
- **v1.2** (2026-04-28): Week 17 RatesNoDispo. Resúmenes ejecutivos por canasta con RPM, WoW, F3-F5 card format. Plan de Acción QW1-QW6 · MP1-MP6 · ES2. Reglas P80 + filtros F4 tráfico≥500K documentados.
- **v1.3** (2026-04-29): **Eje 5 · Método rediseñado** en ambos reportes. Sección 13 convertida de prosa larga a tarjetas categorizadas con chip + título + cuerpo + acción. RatesNoDispo: 5 tarjetas (DATA · MÉTRICA · LIMPIEZA · MAPEO · MÉTODO). CheckRates: 6 tarjetas (CANASTA · DATA · UMBRAL · MÉTRICA · THRESHOLD · MÉTODO). Bug HTML resuelto en RatesNoDispo W17 (sección 13 duplicada + bloque zombie post-`</html>`, ~290 líneas eliminadas). Templates con placeholders `{{...}}` para datos numéricos del Método. Variable CSS `--verde:#2F6C34` agregada al `:root` de CheckRates para chip-clean.
- **v1.4** (2026-04-29): **Bloque editorial mayor pre-W18** — 5 ejes paralelos:
  - **Eje 5.5 · Terminología CheckRates**: `CheckRates Únicos` / `CK Únicos` reemplazado por `CheckRates` en todo el editorial. El campo del dataset mantiene su nombre original. Documentado en guía CheckRates §4.
  - **Eje 5.6 · Conv Rate corregido (CheckRates)**: nueva fórmula `Bookings ÷ Successful CheckRates` (BK/Suc) en lugar de `BK / CheckRates`. Aísla la conversión comercial pura del problema técnico de Eficacia. **Aplica desde W18**; W17 publicado queda histórico con la fórmula vieja. Documentado en guía CheckRates §6 con nota explícita sobre la transición.
  - **Eje 5.7 · Severity Eficacia rangos invertidos**: rangos en términos de Eficacia directa (Exitosa 100–95%, Súper Crítica 20–0%). Renombrado nivel 2: "No Aceptable" → **"Por debajo del Rango"**. Headers explícitos en las 3 tablas Severity (Nivel · Rango · Distribución · Hoteles · %).
  - **Eje 5.8 · Sort orders estandarizados**: cada tabla tiene su sort default obligatorio documentado en las guías §7.5. Sub-tablas de canastas explicitan visualmente el sort en el `h3`. Sumadas 2 reglas anti-bug (sort consistency + sin duplicados) y 2 ítems al checklist pre-publicación. Cambio: §05 CheckRates Bajo Rendimiento ahora ordena por Conv Rate ↑ (antes CheckRates ↓). Cambio: §05 RatesNoDispo Por Corporativo ahora ordena por GB Proyectado ↓ (antes % 0 BKGS ↓).
  - **Eje 6.1 · §09 Análisis por Canasta (CheckRates)**: nueva sección con tabla resumen comparativa de las 3 canastas (CheckRates · Eficacia · BKGS · Conv Rate · % Sin BKGS · Cluster dominante). Renumeración: Plan §09 → §08, canastas detalle a §10/§11/§12.
  - **§05 RatesNoDispo · columna nueva GB Proyectado**: estimación de upside no realizado · `Tráfico × RPM_global`. RPM_global recalculado cada semana sobre el dataset HTS · P80 (W17 ≈ $3.97/k búsquedas).
  - **Mini-fix W17 RND publicado**: regenerada §03 Demanda No Convertida que tenía bug de duplicados (The STRAT × 2) + sort partido en sub-bloques. La tabla corregida tiene 10 hoteles únicos ordenados estrictamente por Tráfico ↓.
- **v1.5** (2026-04-29): **Eje 6.2 · Vocabulario Clusters & Prioridades**. Separación clara de dos ejes que antes se mezclaban en chips visualmente idénticos (`Quick Win` se usaba como cluster Y como prioridad temporal). Vocabulario nuevo:
  - **Cluster del hotel** (5 chips): `Optimizable` · `Conv Rate Crítico` · `Connectivity Issue` · `Tráfico Anómalo` · `Bajo Volumen`
  - **Prioridad temporal** (3 chips): `Acción Rápida` · `Mediano Plazo` · `Estratégico`
  - Aplicado al template CheckRates (13 reemplazos) + guía CheckRates §7.6 nueva con definiciones canónicas + checklist con 2 ítems nuevos.
  - `Connectivity Issue` se mantiene en inglés por decisión explícita (track record con el equipo · asimetría aceptada con los otros 4 nombres en castellano).

---

## 🏷 Vocabulario de Clusters · referencia rápida

**Cluster del hotel** (qué TIENE el hotel · aparece en chips de tablas):

| Cluster | Criterio | Diagnóstico |
|---|---|---|
| **Optimizable** | Eficacia ≥ 95% · Conv Rate sano · vol. significativo | Ya funciona — un ajuste lo mejora |
| **Conv Rate Crítico** | Eficacia ≥ 95% · Conv Rate < 0.5% | Motor OK · conversión mal · problema comercial |
| **Connectivity Issue** | Eficacia < 60% sostenida | Problema técnico · API/integración falla |
| **Tráfico Anómalo** | Volumen alto + 0 BKGS sostenido | Patrón inusual · validar antes de juzgar |
| **Bajo Volumen** | CheckRates < threshold canasta | Poca señal · no es prioridad |

**Prioridad temporal** (cuándo HACER · aparece en Plan de Acción):

| Prioridad | Horizonte |
|---|---|
| **Acción Rápida** | < 7 días |
| **Mediano Plazo** | 2–4 semanas |
| **Estratégico** | Trimestre |

> ⚠️ Los dos ejes son **independientes**. Un hotel "Optimizable" puede tener una acción "Mediano Plazo" asociada. El cluster describe el hotel, la prioridad describe el horizonte de la acción.

---

## 📐 Sort orders canónicos · referencia rápida

### CheckRates

| Sección | Sort default |
|---|---|
| §04 Hoteles Críticos | Ranking compuesto Eficacia + Conv Rate ↑ |
| §05 Bajo Rendimiento | Conv Rate ↑ |
| §06 Severity por Corporativo | % Críticos+ ↓ |
| §07 Menor Conv Rate | Conv Rate ↑ |

### RatesNoDispo

| Sección | Sort default |
|---|---|
| §03 Demanda No Convertida | Tráfico ↓ |
| §04 Bajo Rendimiento | Conv RPM ↑ |
| §05 Por Corporativo | **GB Proyectado ↓** (W18+) |
| §06 Por Destino | GB ↓ |
| §07 Por País | GB ↓ |

### Sub-tablas de canastas

Cada canasta explicita su sort default visualmente en el `h3` con un `<span>` complementario:

```html
<h3>Bajo Rendimiento · Top 5 <span>— ordenado por Conv Rate ↑</span></h3>
```

### Reglas anti-bug (W18+)

- **Sort consistency**: el sort default debe aplicarse al conjunto completo de filas, no a sub-bloques concatenados. Si una tabla se construye en dos pasos, re-ordenar el conjunto antes de renderizar.
- **Sin duplicados**: cada hotel/corporativo/destino aparece una sola vez por tabla.

---

## 📐 Reglas de la sección 13 · Método

La sección de crítica metodológica al final de cada Reporte Editorial sigue ahora un formato canónico de **tarjetas categorizadas** (no prosa larga).

### Estructura por tarjeta

| Elemento | Detalle |
|---|---|
| **Chip de categoría** | Etiqueta breve en mayúsculas con color por categoría |
| **Card title** | 4–8 palabras · enuncia el problema en una frase |
| **Card body** | 1–3 líneas máx · datos concretos (placeholders en template) |
| **Card action** | Línea al pie con `→` · acción concreta (verbo + objeto) |

### Categorías y chips

| Chip class | Categoría | Color | Cuándo usar |
|---|---|---|---|
| `chip-canasta` | CANASTA · Iteración | violeta-claro #6B21A8 | Cambios estructurales en análisis por canasta |
| `chip-data` | COBERTURA · Data | pink #EA0074 | Faltantes/inconsistencias en columnas |
| `chip-clean` | LIMPIEZA · Outliers / UMBRAL · Filtro | verde #2F6C34 | Tratamiento de extremos, refunds, thresholds |
| `chip-metric` | DEFINICIÓN · Métrica | violeta #5C469C | Métrica con definición ambigua |
| `chip-mapping` | TAXONOMÍA · Mapeo / THRESHOLD · Relevancia | naranja #A86A1D | Renombres, mínimos de muestra |
| `chip-method` | SEVERITY · Método | celeste #0288D1 | Mejoras al método de cálculo o segmentación |

### Layout

- Grid 2 columnas en desktop · 1 en mobile (breakpoint 720px)
- Cantidad: **4 a 6 tarjetas** · si pasa de 6, reagrupar
- La tarjeta de mayor peso narrativo lleva clase `wide` (ocupa las 2 columnas) — usualmente la última

### Qué NO va en las tarjetas

- ❌ Configuraciones (weights, thresholds, % global) → en este README o guía editorial
- ❌ Notas metodológicas largas → en documentación, no en el Editorial
- ❌ Fórmulas de Final Score / DQS / Impact Ajustado → en sección 6 de cada guía
- ❌ Top X tablas con datos → eso es análisis, no la sección 13

### Placeholders en templates

Los templates editoriales (`_TEMPLATE_*_Reporte_Editorial.html`) usan `{{PLACEHOLDER}}` en los datos numéricos para que cada lunes se reemplacen con los valores de la semana en curso.

**RatesNoDispo (13 placeholders en Método):** `{{HOTELES_TOTAL}}` · `{{HOTELES_CON_GB}}` · `{{COBERTURA_GB_PCT}}` · `{{RPM_GLOBAL}}` · `{{HOTELES_ADR_NEG}}` · `{{HOTELES_GB_NEG}}` · `{{EJEMPLO_HOTEL_NEG_1/2}}` · `{{EJEMPLO_GB_NEG_1/2}}` · `{{CORPNAME_NATIVOS}}` · `{{CORPNAME_PARSEADOS}}` · `{{NEXT_WEEK}}`

**CheckRates (12 placeholders en Método):** `{{WEEK_NUM}}` · `{{P20_ERRORS_PCT}}` · `{{CR_GLOBAL}}` · `{{EJEMPLO_CORP}}` · `{{EJEMPLO_CORP_HOTELES/CK/BKGS}}` · `{{HOTELES_SIN_CONV}}` · `{{HOTELES_SUPER_CRIT}}` · `{{HOTELES_SUPER_CRIT_OLD}}` · `{{PCT_SUPER_CRIT_OLD}}` · `{{NEXT_WEEK}}`
