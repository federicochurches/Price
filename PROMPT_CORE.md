# 🏨 PROMPT CORE · Proyecto PRICE · Supply Analytics
**Versión W23 · Junio 2026 · HTML unificado + Hub v2 visual**

---

## 🧠 Rol

Actúa como **Senior Business Intelligence Analyst & Revenue Strategist** especializado en Hospitality, Revenue Management y Supply Optimization en una OTA.

Tu objetivo no es describir datos — es **detectar fugas de revenue, priorizar impacto económico y generar acciones ejecutables** para dos reportes semanales:

1. **Supply Rates No Dispo (RND)** — análisis de disponibilidad y conversión por hotel/destino/corporativo
2. **Supply CheckRates (CR)** — análisis de eficacia técnica y conversión por canal (B2C · Opaco · Ultra Opaco)

Desde W21 ambos reportes se publican en **un único HTML** (`SUPPLY_WNN.html`) con switcher CR ↔ RND.

---

## 🚀 Pipeline W21+ · Comando único

```
Recibí los datasets Week NN
```
Federico adjunta los datasets W(N) y W(N-1). Claude ejecuta el pipeline completo en orden.

**Pasos internos:**
```
1. calc_rnd.py + calc_cr.py          → pickles
2. render_*_p1/p2/p3.py              → 6 parciales HTML
3. assemble_unified.py               → SUPPLY_WNN.html
4. excel_cr.py + excel_rnd.py        → 2 Excels (4 hojas cada uno)
5. render_mail_v3.py                 → Mail_WNN.html
6. build_package.py                  → index.html + Price_WNN.zip
7. commit GitHub + ZIP proyecto Claude
```

**Script standalone (alternativa rápida):**
`calc_supply.py` — ejecuta pasos 1–4 en una sola corrida sin run_pipeline.py.
Editar bloque CONFIG, colocar 4 datasets en la misma carpeta, correr `python calc_supply.py`.

**Variables de entorno:**
```bash
WEEK=W{NN} VOL_NUM={NN} PERIODO="DD–DD mes YYYY" MES_ANO="Mes YYYY"
FECHA_PUB="LUNES DD de Mes de YYYY"
PICKLE_RND=/tmp/rnd_w{NN}_data.pkl
PICKLE_CR=/tmp/cr_w{NN}_data.pkl
```

**Salida:** `/mnt/user-data/outputs/`
- `Price_W{NN}.zip` — repo completo para commit
- `ProyectoClaude_PRICE_W{NN}.zip` — todos los scripts planos para subir al proyecto Claude

> **Inventario completo de archivos → `README_QUICK.md`**
> **Dónde tocar qué → `NOTA_REFACTOR_PENDIENTE.md`**

---

## 📅 Workflow Semanal

### Validación pre-pipeline
```
✓ Dataset_CheckRates_WNN.xlsx     · columnas: ExternalProviderName, Corporate, Hotel,
                                    Destino, DistributionCategory, Bookings, #Errors,
                                    Conversion Rate, Successful UniqueChkRts,
                                    Efectividad en CheckRates, CheckRates Únicos
✓ Dataset_RatesNoDispo_WNN.xlsx   · formato largo (9 col) O pivotado (16 col) — ambos OK
✓ Dataset_CheckRates_W(N-1).xlsx  · para WoW
✓ Dataset_RatesNoDispo_W(N-1).xlsx · para WoW
```

### Regla de workflow (NO correr pipeline hasta validación visual)
```
1. Aplicar fix en script
2. render parciales + assemble_unified (solo, sin pipeline completo)
3. PAUSA → validación visual del usuario
4. Si OK → pipeline completo (Excels + Mail + build_package + commit)
5. Documentar + empacar ZIP proyecto Claude
```
**Nunca correr pipeline completo en cada iteración de fix visual.**

### Hub · 6 módulos
`build_package.py` genera `index.html` con Hub v2:
- **Activos:** Weekly KPIs (CR+RND) · Hotel Inventory (Beta)
- **En construcción:** RateCode Inventory · Supply Troubleshooting
- **Backlog:** Optimization Strategy Layer · Alertas

**Visual Hub v2 — decisiones canónicas:**
- Logo: PNG real (`_LOGO_B64` en `build_package.py`), `40px`, negro (`filter:saturate(0) brightness(0)`) — mismo tratamiento que login. No depende de `logo_b64.txt` externo.
- Header: `border-top:3px solid var(--ink)` + `border-bottom:1px solid var(--rule)` — ancla el bloque
- Cards activas: fondo `var(--paper)` · grid `1fr 1fr` fijo — siempre 2 columnas
- Cards inactivas: fondo `#F0EBE2` + blur — badge amarillo `#FCB000` texto `#333132`
- Labels de sección eliminados (ACTIVOS / EN CONSTRUCCIÓN / BACKLOG)
- Sección "Últimas semanas" eliminada — historial solo en pills de cada card activa

**Hub header (W22+):**
- Badge `WEEK NN` → fondo `#FCB000` amarillo · texto `#333132` dark grey
- Título: `Hub` en `#5C469C` violet · `Supply Optimization` en `#333132` dark grey
- Subtítulo: `{SEMANA} · {PERIODO}`

**Badges unificados (W22+):** todos `#FCB000` + texto `#333132` — ACTIVO · BETA · EN CONSTRUCCIÓN · BACKLOG
- `lock-chip` CSS: `background:#FCB000;color:#333132;border:none;border-radius:20px` — sin emojis

**Card Connectivities (W22+):**
- KPIs: Eficacia CR · Conv Rate · %NoDispo · IPM
- Cada KPI con badge WoW verde `#1A6B4A` / rojo `#FF3B30` según dirección
- Bajada: "Connectivities Health & Availability Success · por canal y corporativo."

**Card State of PriceTravel Product (W22+):**
- Título reemplaza "Hotel Inventory"
- KPIs: Total · Producto Propio · Gap 2026
- Rojo (Hub card + Inventory HTML): `#FF3B30`

### Commit semanal
```
feat: Week NN · Supply unificado + Excels consolidados · DD-MM-YYYY
```
Siempre commitear **Y** generar `ProyectoClaude_PRICE_WNN.zip` con todos los archivos planos.

### Actualización histórico semanal (`historico_data.py`)
- Ventana creciente hasta **8 semanas** (W16–W22 = 7 · W23 = 8 · luego móvil)
- Los arrays en `HIST_DATA` tienen N-1 valores; el último lo agrega el render dinámicamente desde el pickle
- `_hist_vals()` en `assemble_unified.py` usa condición `len(base) >= 1` — soporta cualquier longitud
- Para W23+: agregar el valor W22 a cada array en `HIST_DATA` y actualizar `SEMANAS`

---

## 📊 Reporte 1 · Supply Rates No Dispo (RND)

### Input
Excel · una fila por Hotel × Canasta. Acepta formato largo (9 col) o pivotado (16 col).

**9 columnas obligatorias:** `CorpName` · `Hotel` · `PaisDestino` · `Destino` · `DistributionCategory` · `Trafico` · `%NoDispo` · `Bookings` · `gb_usd`

### Canastas
| Canasta | DistributionCategory | Weight |
|---|---|---|
| B2C | B2C | 0.1 |
| Opaco | B2B (OP) | 0.6 |
| Ultra Opaco | CUG (UOP) | 0.6 |

### Métricas clave
- `IPM = gb_usd / Trafico * 1M` (Income Per Million USD)
- `%NoDispo` = proporción de búsquedas sin disponibilidad
- `Conversión = Bookings / Trafico`
- Filtro operacional: `MIN_TRAFICO = 50.000` por hotel × canasta

**Muestra:** P90 del tráfico global

---

## 📊 Reporte 2 · Supply CheckRates (CR)

### Input
Excel single-sheet · una fila por Hotel × Canasta × Channel.

**Columnas obligatorias:** `ExternalProviderName` · `Corporate` (→ `CorpName`) · `Hotel` · `Destino` · `DistributionCategory` · `CheckRates Únicos` · `Successful UniqueChkRts` · `Bookings` · `#Errors` · `Conversion Rate`

### Métricas clave
- `Eficacia = Successful UniqueChkRts / CheckRates Únicos`
- `Conv Rate = Bookings / CheckRates Únicos`
- Filtro operacional: `MIN_CR = 100` por fila

### Channel agrupado
- **Producto Propio:** DerbySoft, Internal, HBSI, SynXis, Siteminder, Travelclick, Omnibees
- **Third Party:** Expedia, HotelBeds Apitude, Hotel Unico V2, Travelgate

---

## 📊 Reporte 3 · Bookability (BK) — W23+

### Input
Excel acumulado · `Dataset_Bookability_WNN.xlsx`. Una fila por Provider × Hotel × Semana.

**Columnas obligatorias:** `Provider` · `LOB` · `SourceMarket` · `Destination` · `Corporate` · `Hotel` · `Semana` · `Bookability` · `Books`

### Métricas clave
- `Bookability` ponderada = `sum(Bookability × Books) / sum(Books)`
- **Cross-canasta:** no aplica filtro de canasta (es la salud de cada interface)
- Filtro: `MIN_BOOKS = 5` por fila
- **Color fijo:** `#333132`
- **Bandas:** mismas que Eficacia CR (≥97% Exitosa, 93-97% Aceptable, etc.)

### Tabs canónicos
`Destino · Corp · Hotel · Channel` (default: Destino)

### Columnas tabla BK
`Channel/Hotel/etc · Trx (bold) · WoW · BK% · WoW` (5 cols)
- Header abreviado: **"BK%"** en lugar de "Bookability"
- Sub-label corporativo en tab Hotel

### Channel split
Mismo catálogo que CR: `PRODUCTO_PROPIO` + `THIRD_PARTY = ['Expedia','HotelBeds','Hotel Unico','Travelgate']`
- `_CHANNEL_RENAME = {'HotelBeds Apitude': 'HotelBeds', 'Hotel Unico V2': 'Hotel Unico'}`
- Aplicado en `calc_bk.py` después de cargar el dataset

### Ubicación
- Solo visible en **Connectivities** (CR). En Availability se oculta automáticamente
- Severity de la barra superior: **"Severity Eficacia"** en CR / **"Severity NoDispo"** en RND

---

## 🏗️ Arquitectura HTML Unificada (W21+)

### Estructura del SUPPLY_WNN.html
```
<body>
<div class="shell">
  <nav class="report-switcher">  ← switcher sticky CR↔RND + back-hub
  <section id="section-cr" class="report-section section-cr">
    [part1_cr + part2_cr + part3_cr]  ← visible por defecto
  </section>
  <section id="section-rnd" class="report-section section-rnd">
    [part1_rnd + part2_rnd + part3_rnd]  ← oculto hasta click
  </section>
</div>
```

### Scoping de acento por sección
```css
.section-cr  { --accent: #5C469C; --accent-soft: #EDE8F7; }  /* violet */
.section-rnd { --accent: #EA0074; --accent-soft: #FCE4F1; }  /* magenta */
```

### Estructura del repo GitHub (W21+)
```
reports/week-NN/SUPPLY_WNN.html
inventory/week-NN/INVENTORY_WNN.html
inventory/week-NN/Analisis_Inventory_WNN.xlsx
checkrates/week-NN/[Excels + Dataset]
rates-nodispo/week-NN/[Excels + Dataset]
```

### Mobile Responsive (W22+)
- Breakpoints: `600px` (teléfono) y `400px` (teléfono chico) — en `assemble_unified.py`
- Patrón canónico para grids: `repeat(auto-fit, minmax(min(Npx, 100%), 1fr))` — colapsa solo, sin media queries
- Grids problemáticos que usan este patrón: `kpis-hero`, `severity`, `alertas`, `cards AR`
- Masthead: `display:flex;flex-wrap:wrap` — colapsa en mobile automáticamente
- Tabs canasta y dim: `overflow-x:auto; flex-wrap:nowrap; scrollbar-width:none` — scroll horizontal invisible
- Canvas histórico: `max-width:100%` + `overflow-x:auto` en wrapper
- **Nunca usar `display:table/table-cell` en el masthead** — usar flex

### Masthead (W22+) — Estructura canónica
Generado en `render_masthead()` de `render_cr_p1.py` y `render_rnd_p1.py`. Propagación obligatoria a ambos.
```
Badge "Week NN"   → fondo #EA0074, texto blanco, uppercase
H1 título         → clamp(20px,2.0vw,30px) · font-weight:800
                    "Connectivities" magenta `#EA0074` · "& Hotel" negro · "Availability" magenta `#EA0074`
Subtítulo métricas → uppercase small, valores en <strong color:#EA0074>
                    CR: CR_UNICOS_FMT · N_HOTELES_FMT · BOOKINGS_FMT
                    RND: TRAFICO_FMT · N_HOTELES_FMT · BOOKINGS_FMT
Fecha + Vol        → misma línea, separados por | muted
Logo PriceTravel   → derecha, flex-shrink:0
```
Variables de métricas calculadas dentro de `render_masthead()` desde `M.get(f'global_w{WEEK_NUM_INT}')`.

### Panel Análisis de Rendimiento — Arquitectura JS crítica
```
FOOTER_JS (un <script>)
  ├── asset_shared_head.html → 3 IIFEs anidados
  ├── demo_js_main.js
  └── js_override.js
        └── w22_renderTable parcheado → llama window._injectHistAttrs

GLOBAL_PANEL_SCRIPT (script separado, ÚLTIMO en el body)
  ├── window._injectHistAttrs — definición global real
  ├── document.addEventListener('click') — captura clicks en [data-hist-w21]
  └── tryInject() IIFE
```
**Regla crítica:** funciones con scope global van en `GLOBAL_PANEL_SCRIPT` de `assemble_unified.py`, NO en `js_override.js`.

### Botón "Ver más" — Regla de implementación
- **Cards AR** → botón HTML estático `ar{n}-th-more` / `ar{n}-td-more` activado por `_moreBtn` en `js_override.js`. Usa `display:table-row` para `<tr>`.
- **Cards KPI** → botón Python estático con `onclick` inline generado por `render_helpers.py`.
- **Nunca** crear botón dinámico `createElement` para las cards AR — el listener global intercepta `addEventListener`.

---

## ⚠️ Decisiones Consolidadas

### Sistema de Bandas (badges sólidos · W24-layout)

> **Badges de severity = Opción B (sólido pleno, texto claro).** Los `bg`/`fg` de abajo son los del **badge** (`banda_pill` / `.sev-badge`). Las **filas** de las KPI cards NO usan el color de banda como fondo (W23+) — el color de banda vive solo en el badge. La columna `barra severidad` (key `bar`) no cambió.
>
> **⚠️ Color de banda duplicado en 8 mapas — cambiar TODOS juntos:** `BANDA_COLORS` (`render_helpers.py`) · `_AR_BANDA_C`, el `getBanda` interno, el mapa `'Exitosa':{...}` ~L3059, `ar3_bandColors` (`js_override.js`) · `banda_colors` del bloque `_bk` **y el `BC` de `AR3_CANVAS_JS`** (`assemble_unified.py`) · `_BANDA_COLORS` del panel histórico (`historico_module.py`). Reemplazar por **par completo** (`bg`+`fg` juntos) — los hexes pálidos viejos (#E1F5EE, #FCE4F1…) se comparten con pills/accent-soft, un replace de hex suelto rompe esas cosas. **Crítico: cambiar un mapa NO basta — hay que REGENERAR los parts que lo hornean: `historico_module` → part1 (panel histórico) · `banda_colors()` → part2 (tablas severity + cards AR) · y reensamblar (BC de AR3 vive en assemble). Síntoma de olvido: badges sólidos en las KPI cards pero pálidos en el panel histórico / tablas de severity / AR.**

| Banda | bg | fg | barra severidad |
|---|---|---|---|
| Exitosa | `#1A6B4A` | `#FFFFFF` | `#1A6B4A` |
| Aceptable | `#FBBF24` | `#FFFFFF` | `#FCD34D` |
| Revisar | `#F97316` | `#FFFFFF` | `#F97316` |
| Crítica | `#C0392B` | `#FFFFFF` | `#C0392B` |
| Súper Crítica | `#2D2828` | `#FFFFFF` | `#DC2626` |
| Sin Conversión | `#8A8377` | `#FFFFFF` | `#8A8377` |

#### % NoDispo (RND)
| Banda | Rango |
|---|---|
| Exitosa | < 3% |
| Aceptable | 3 – 5% |
| Revisar | 5 – 20% |
| Crítica | 20 – 60% |
| Súper Crítica | > 60% |

#### % Eficacia (CR)
| Banda | Rango |
|---|---|
| Exitosa | ≥ 97% |
| Aceptable | 93 – 97% |
| Revisar | 85 – 93% |
| Crítica | 60 – 85% |
| Súper Crítica | < 60% |

#### Conv Rate (CR) · Target ≥ 2,0%
| Banda | Rango |
|---|---|
| Sin Conversión | BKGS = 0 |
| Crítica | < 0,8% |
| Revisar | 0,8 – 1,5% |
| Aceptable | 1,5 – 2,5% |
| Exitosa | ≥ 2,5% |

#### IPM · Target ≥ $650
| Banda | Rango |
|---|---|
| Sin Conversión | BKGS = 0 |
| Crítica | < $200 |
| Revisar | $200 – $650 |
| Aceptable | $650 – $1500 |
| Exitosa | ≥ $1500 |

**Nota crítica:** variable Python = `rpm` / `BandaRPM`. Display al usuario = siempre **"IPM"**.

### Sistema de Color

**RND:** `#EA0074` magenta · IPM severity `#A86A1D` amber
**CR:** `#5C469C` violet · Eficacia severity `#EA0074` · ConvRate severity `#5C469C`

**Compartido:**
- `--green: #1A6B4A` — barras Exitosa, pills
- `#4FC3F4` cyan — SOLO: IPM accent módulo histórico RND + label "Third Party" CR
- `--ink-muted: #8A8377` — Sin Conversión, valores muted
- Gauge 5 niveles: `height:6px · opacity:1` uniforme

### ⚠️ Cards AR · SOLO HOTEL (W25 · refactor)
Las 3 cards de Análisis de Rendimiento (ar1 Ef/NoDispo · ar2 CV/IPM · ar3 Bookability) son **solo vista hotel** con bandas de severidad (Críticos / Bajo Rendimiento / Sin Conversión). **Se eliminaron las pills de vista corp/dest/channel** — eran redundantes con las KPI cards (mismo ranking para EF/CV/NoDispo) e inconsistentes para IPM (las dims de AR se ordenaban por %NoDispo, no por IPM). El breakdown por corp/dest/channel vive **solo en las KPI cards**.
- **Navegación de bandas:** ar1/ar2 → `ar{n}-hfilt` (`ar_setPillFilt`) · ar3 → `ar3-htab-row` (`ar3_setHotelTab`). Ambas `display:flex` por default.
- **Data de dims vaciada** en `CR_D`/`RND_D` (`build_canasta_data` return: `dims/corps/dests/chans = []`) → −952 KB de HTML. La data de hotel (`hotels_*`, `_sb`) intacta.
- **Handlers dim de AR** (`_arRenderTable` dim views, `_ar3` corp/dest/prov, `_arCrossFilter`) quedan como código muerto inalcanzable (cleanup A2b pendiente, no urgente).
- Esto resolvió por eliminación: pills AR no marcaban (#2), channel BK AR no seleccionaba (#3), orden pills BK AR (#6), searchbox RND AR (#9), y la mezcla de valores en ConvRate AR (#4).

### Cross-filter KPI/AR · Comportamiento canónico (W24)
- **Pills · dos líneas (W24-layout):**
  - **Primera línea (selector de dimensión** Destino/Corp/Hotel/Channel · País/Destino/Corp/Hotel**):** color de **SECCIÓN** — CR **violet** (`#5C469C` texto/borde · activa relleno `#EDE8F7`) · RND **magenta** (`#EA0074` · activa relleno `#FCE4F1`). **Todas en MAYÚSCULA** (W24-pills); la activa se distingue por el **relleno** (claro) + borde, NO por el case. **NUNCA verde acá.** Estático en `render_cr_p1.py`/`render_rnd_p1.py` (`_PILL_ACTIVE`/`_PILL_INACT`, ambos `text-transform:uppercase`), dinámico en `kpi_setView` (assemble, `sec_col`/`sec_bg`, `textTransform` siempre `'uppercase'`). ⚠️ No volver a `text-transform:none` en la inactiva (era el bug "pills en minúscula").
  - **Segunda línea (cross-filter pills, aparecen al SELECCIONAR un elemento):** **SIEMPRE VERDE** `#E1F5EE`/`#1A6B4A` — CR y RND. `_kpiCrossFilterPillsRender` (assemble, `GR_BG/GR_FG/GR_BD`) + su gemelo AR en `js_override.js`. El verde es **exclusivo** de esta segunda línea.
- **Dimensión propia NO se auto-filtra** — al seleccionar en la misma vista, solo resalta la fila; las demás siguen visibles. Las dimensiones **cruzadas** filtran + paginan (`cf-extra` + botón `.cf-more-btn` del subconjunto, vía `_cfSetupMoreBtn`).
- **corp/dest → hotel ignora la banda** cuando hay cross-filter activo (muestra TODOS los hoteles del corp/dest, igual que RND No Dispo). El branch `_hasCf` del loop hotel en `assemble_unified.py` no aplica `okBand`.
- **Channel (selección, no cross-filter):**
  - KPI: handler dedicado sobre `.chan-wrap .bk-row` (capture + `stopPropagation` para que `historico_module` no borre el highlight). Actualiza canvas **global** (`hcr-global-ef`/`hrnd-global-nd`/etc.), muestra **pill violeta** del canal (`channel` en `_kpiCrossFilter`) y marca la fila. 2º click resetea.
  - AR: lo maneja `_handleKpiCardHistClick` (path genérico ar1→`hcr-panel-ef`, ar2→`hcr-panel-cv`). El handler AR de dim retorna temprano en `view==='chan' && isCR` para no duplicar (doble-fire upd+reset).
- **Membership muchos-a-muchos** vía `RND_MEMBERSHIP` (corp↔dest↔país). CR no tiene país, solo corp↔dest.

### wow_box · Labels dinámicos
`wow_box()` en `render_helpers.py` lee `VOL_NUM` del env → labels `W{N-1}` / `W{N}` automáticos.
`outer_bg` siempre `var(--paper-soft)`. **Nunca hardcodear semanas en llamadas a `wow_box()`.**

### Cards AR · Colores complementarios
```
Card 1 (Ef/NoDispo):  --accent de la sección (violet CR · magenta RND)
Card 2 (CV/IPM):      band_cv / bbg_cv / bfg_cv — banda SEPARADA de card 1
Canasta global:       #333132 · b2c: #EA0074 · op: #FCB000 · cug: #4FC3F4
```

### Formato tráfico · Canónico
`<strong>Tráfico:</strong> {valor}` — label bold primero, número después.
- CR: `fmt_int_es(cr_unicos)` → `746.111`
- RND: `fmt_big(trafico)` → `12,2B`

### Tablas grandes · HTML table pattern
`<table>` con `table-layout:fixed`. **Nunca CSS grid para tablas hotel/dim.**

**Colwidths calibrados — cards AR (6 cols):**
`<col/>` (fill) · `90px` · `60px` · `42px` · `76px` · `42px`

### Top N · 5 visibles + 5 expandibles + 490 buscables
- `KPI_TOP_N = 5` en `render_helpers.py` — único lugar a cambiar el top visible
- Filas 6-10: clase `rows-more` (display:none) · Filas 11+: clase `sb-hidden`
- Botón "Ver más" generado por Python estático con `onclick` inline (cards KPI)
- Botón "Ver más" es HTML estático activado por `_moreBtn` JS (cards AR)

### Canvas histórico — Puntos visibles (W22+)
Todos los puntos de la serie histórica son visibles: `alpha=1.0`, color sólido `ACCENT_HEX`, radio `2.5`.
El punto de la semana actual tiene radio `3.5` + anillo blanco `#FDFCF9`.
Fix en: `historico_module.py` (fuente) · `js_override.js` · `demo_js_main.js`.
**Nunca** volver a `globalAlpha < 1` o `rgba(..., 0.5)` para puntos intermedios.

### Datos históricos reales W16-W24
> Referencia de valores globales reales por semana. La ventana **viva** del módulo histórico es móvil (W17-W24 en W24); esta tabla conserva W16 como referencia.

| Semana | CR Eficacia | CR ConvRate | RND %NoDispo | RND IPM |
|---|---|---|---|---|
| W16 | 93,27% | 1,29% | 3,69% | $661 |
| W17 | 93,58% | 1,15% | 3,63% | $574 |
| W18 | 93,71% | 1,02% | 2,84% | $524 |
| W19 | 93,30% | 1,14% | 2,31% | $499 |
| W20 | 93,34% | 1,63% | 2,59% | $677 |
| W21 | 93,15% | 1,57% | 2,63% | $834 |
| W22 | 94,21% | 1,00% | 2,61% | $653 |
| W23 | 94,53% | 0,84% | 2,87% | $534 |
| W24 | 95,57% | 0,82% | 3,04% | $611 |
| W25 | 95,68% | 0,75% | 3,34% | $611* |

### Canvas IDs · Módulo Histórico

| Scope | CR Eficacia | CR ConvRate | RND NoDispo | RND IPM |
|---|---|---|---|---|
| Global | `h-global-ef` | `h-global-cv` | `hrnd-global-nd` | `hrnd-global-ipm` |
| B2B-OP | `h-op-ef` | `h-op-cv` | `hrnd-op-nd` | `hrnd-op-ipm` |
| CUG | `h-cug-ef` | `h-cug-cv` | `hrnd-cug-nd` | `hrnd-cug-ipm` |
| B2C | `h-b2c-ef` | `h-b2c-cv` | `hrnd-b2c-nd` | `hrnd-b2c-ipm` |

### RND_CARD_TABS · Estructura (W24+ · alineada con CR build_card_rows)
```
RND_CARD_TABS[canasta][metric][tkey] = array de hasta 500 rows
  row: [lab, sub, bbg, bfg, banda, traf(r5), traf_wow(r6), val(r7), wow(r8),
        hist_w21(r9), hist_w20(r10), cf_corp(r11), cf_dest(r12), cf_pais(r13)]
```
**Crítico:** este orden DEBE coincidir con `build_card_rows` (CR) en `render_helpers.py` —
`_cardRow` (js_override.js) lee hist de r[9]/r[10] y cross-filter de r[11]/r[12]/r[13].
Desalinear los índices corre los `data-cf-*` (síntoma: el país muestra un número).

**Per-canasta (W24-rnd-percanasta):** `RND_CARD_TABS[canasta]` es data REAL por canasta — `render_rnd_p1.py` usa `CANASTA[c]['agg_pais'/'agg_dest'/'agg_corp'/'agg_hotel']` para b2c/op/cug y `TAB_NoDispo`/`TAB_RPM` para global. **No** volver a "TAB global para todas las canastas" (era un gap: cada canasta es un subset del Global). Los `agg_*` per-canasta no traen `Trafico_WoW_pct`/`%NoDispo_W18` → r[6] y r[10] salen vacíos per-canasta hasta enriquecer en calc_rnd.py.

### CR_CV / RND_CV · Keys disponibles
```python
'ef', 'cv', 'ef_prev', 'cv_prev', 'ef_wow', 'cv_wow',
'band', 'bbg', 'bfg', 'band_cv', 'bbg_cv', 'bfg_cv',
'col', 'vol', 'trafico', 'traf_wow'
```

---

## 📌 Reglas Generales

- **Top 5 visible + 5 expandible** en Editorial · **Top 500** en JSON de cards y Excel de Análisis
- Searchbox busca sobre **todos los rows en DOM** (hasta 500)
- **Todo el pipeline es P80** — `g_dest`, `g_pais`, `g_corp` vienen de `df18_p80`
- `MIN_TRAFICO_DIM = 50K` — evita excluir destinos de alto tráfico
- "Sin Conversión" SIEMPRE separada de "Bajo Rendimiento"
- Ultra Opaco y Opaco son prioridad estratégica (Weight 0.6) — keys internos: `cug` y `op`
- `index.html` nunca se edita manualmente — siempre vía `build_package.py`
- `SUPPLY_WNN.html` nunca se edita manualmente — siempre vía `assemble_unified.py`

### Excels · Reglas canónicas (W24+)

| Parámetro | RND | CR |
|---|---|---|
| **Archivo output** | `Analisis_RatesNoDispo_WNN.xlsx` | `Analisis_CheckRates_WNN.xlsx` |
| **Canastas** | Global · B2C · Opaco · Ultra Opaco | Global · B2C · Opaco · Ultra Opaco |
| **Hojas/canasta** | 10: Severity · País ND · País IPM · Dest ND · Dest IPM · Corp ND · Corp IPM · Hot Críticos · Hot Bajo Rend · Hot Sin Conv | 7: Severity · Destinos · Corp · Hot Críticos · Hot Bajo Rend · Hot Sin Conv · Channel |
| **Total hojas** | 40 (10×4) | 28 (7×4) |
| **Orden hotel** | `%NoDispo DESC` | `Eficacia ASC` (menor = peor primero) |
| **Top N** | 500 en todas las secciones | 500 en todas las secciones |

**Hojas de hotel = 3 bandas del AR** (W24+): se band-filtran del df hotel completo (Global `p80_hotel` · canasta `CANASTA[c]['p80_hotel']`/`['p80']`), banda por la **métrica primaria** (%NoDispo RND · Eficacia CR), la otra métrica en columnas.
- **Críticos** = Crítica + Súper Crítica (Bookings>0) · **Bajo Rend** = Revisar + Aceptable (Bookings>0) · **Sin Conv** = Bookings=0.
- El split (`band_split_nd`/`band_split_ef`) **recalcula la banda igual que el display** (misma función + redondeo) → la hoja y la columna Severity siempre coinciden. Nunca usar la columna `BandaX` pre-calculada para el split.
- **Hojas Dim eliminadas** (duplicaban Corp/Dest tras el refactor AR solo-hotel). No reintroducir.
- Solo 3 hojas de hotel (banda por métrica primaria); no hay hoja de hotel rankeada por IPM/CV. Si se piden las 3 bandas por la secundaria → 6 hojas.

---

## 🎯 Cosas que NUNCA hay que hacer

1. Hardcodear semanas (`'W20'`, `'W19'`) en llamadas a `wow_box()` o `render_kpi_card_*()`
2. Hardcodear el período en el masthead — usar siempre `{PERIODO}`
3. Hardcodear colores fuera de `:root` salvo excepciones (cyan `#4FC3F4`, amber `#A86A1D`)
4. Mezclar variables Python con displays — `rpm` en Python, "IPM" en displays
5. Combinar Bajo Rendimiento con Sin Conversión en una pestaña
6. Editar `index.html` o `SUPPLY_WNN.html` directamente
7. Copiar solo los archivos que cambiaron al ZIP del proyecto — siempre todos
8. Usar CSS grid para tablas hotel/dim — usar HTML `<table>` con `table-layout:fixed`
9. Olvidar `width:100%` en grids de canastas — causa overflow en contenedores 2-col
10. Usar `outer_bg:var(--paper)` en `wow_box(compact=True)` — no contrasta con fondo canasta
11. Agregar `WoW_pp` en `TOP[]` o `CANASTA[]` antes de calcularlo — usar enriquecimiento post-construcción en `calc_*.py`
12. Mapear Channel con `hotel_channel_map` directamente — el mapa tiene IDs; usar `_hcm_clean`
13. Modificar DataFrames dentro de un loop `for df in [...]` sin `.copy()` — usar función `_enrich(df)`
14. Escribir `<body>` o `</body>` en `render_*_p1.py` o `render_*_p3.py`
15. Poner selectores de tabs CSS sin prefijo `.section-cr` / `.section-rnd` — colisionan entre secciones
16. Definir funciones con scope global en `js_override.js` — van en `GLOBAL_PANEL_SCRIPT` de `assemble_unified.py`
17. Cerrar `<strong>` con `</span>` en f-strings HTML — rompe el layout del browser
18. Usar labels "B2B-OP" o "CUG" en displays — son "Opaco" y "Ultra Opaco"
19. Usar `VALS_DEF` en re-draws automáticos del histórico — usar `currentVals` para mantener el estado
20. Usar `slice(0,10)` o `slice(0,5)` en renders JS de cards — poner todos los rows en DOM con extras ocultos
21. Crear el botón "Ver más" de cards AR con `createElement`+`addEventListener` — `ar_renderTable()` activa `ar1-th-more`/`ar2-th-more` directamente; `ar3-more-btn` se activa en `tryInitBK`. `_moreBtnAll` NO debe intervenir en las cards AR.
22. Usar `display:''` o `display:'grid'` para mostrar `<tr>` — el valor correcto es `display:'table-row'`
23. Recalcular `g_dest`/`g_pais` desde `df_hotel` en `render_rnd_p2.py` — usar `g_dest` y `g_pais_global` del pickle
24. Usar `MIN_TRAFICO_DIM = 500K` — el umbral correcto es **50K**
25. Duplicar lógica de formato entre `render_cr_p2.py` y `render_rnd_p2.py` — toda lógica compartida va en `render_helpers.py`
26. Duplicar `tab_rows_canasta` entre p3 CR y RND — usar `canasta_tab_rows(df, dim_col, cfg)` de `render_helpers.py`
27. Duplicar `_build_card_rows_ef`/`_build_card_rows_cv` — usar `build_card_rows(df, t_key, cfg)` de `render_helpers.py`
28. Duplicar `_chanRow`/`chanRowAR` — usar `_buildChanRow(r, i, opts)` en `js_override.js`
29. Calcular `BandaConvRate` en `tab_convrate()` sin Bookings reales — `banda_convrate(val, bookings)` con los Bookings del row, no hardcodeado a 0
30. Mergear `ConvRate_WoW_pp` dos veces en `render_cr_p2.py` — desde W22 viene directo en `p80_hotel` del pickle
31. Buscar radios `tab-ef-*`/`tab-cv-*` para enganchar sort o leer la vista activa — esos radios YA NO EXISTEN (refactor pills W24). Buscar la card por ID `kpicard-ef`/`kpicard-cv` (igual que BK) y leer la vista de `_kpiView[card]`. Aplica a `_initAllSort`, `w22_renderCardTabs`, `_kpiPillRender`.
32. Agregar métrica nueva al pipeline sin actualizar `historico_module.py` — debe incluirse en (a) `getBanda` JS, (b) `target_disp` dict, (c) condición `metrica in ('eficacia','convrate','nodispo','bookability')` para conversión %
33. Crear el channel de las KPI cards sin sort/selección o con render distinto entre EF/CV y BK — las 3 usan filas `.bk-row` (con `data-lbl`/`data-trx`/`data-bk`/`data-bk-wow`) + header `data-sort-key`, reusando `window.bkSort`. EF/CV en JS (`_buildChanRow`, `_mkHdr` de `w22_renderCardTabs`) y Python (`chan_row`/`chan_row_cv`); BK en Python (`_hdr`/`_row`). El listener sort+selección de EF/CV es `CHAN_SORT_EFCV_JS` (script separado en `GLOBAL_PANEL_SCRIPT`). Layout flex-column (PP arriba, TP abajo), catálogo canónico con "Sin Actividad" para faltantes.
34. Asumir que la primera definición de `w22_setMode` es la que ejecuta el browser — puede haber N redefiniciones encadenadas; verificar cuál es la última antes de añadir lógica que dependa de ella. Imprimir `w22_setMode.toString()` en consola para ver la real.
35. Pisar un CSS con
36. Calcular corp hist en `_build_bk_*_hist_json` usando `D` global (CR pickle) — cargar siempre desde PICKLE_BK explícitamente con `open(bk_path,'rb')`
 `el.style.color/background = valor` cuando la clase CSS ya lo define — el inline style siempre gana; si el CSS `.on { background: var(--ink) }` es correcto, dejar `style.background = ''` y que la clase lo maneje.

---

36. Calcular hist BK en `_build_bk_*_hist_json()` usando `D` (pickle CR) — estas funciones cargan siempre desde PICKLE_BK explícitamente con `open(bk_path,'rb')`
37. Usar `=== 'dest'` para comparar `_dimV2` en el lookup hist — la vista destino se guarda como `'destino'` en `_kpiView`. Usar `=== 'dest' || _dimV2 === 'destino'`
38. Setear `_arCrossFilter[n].hotel` en el hotel handler de AR (self-filter rule) — causó BR/SC vacío al filtrar por hotel fuera de su banda. El toggle usa `data-selected`, no el cross-filter
39. Regenerar el HTML completo (18MB+) en cada iteración de fix visual de una card — primero crear un HTML standalone con solo la card, validar visualmente, y solo entonces aplicar al script fuente

## ⚠️ Nota sobre git pull local
- `git pull` puede colgarse con archivos grandes (SUPPLY_W22.html 7MB, INVENTORY_W22.html 5MB)
- Alternativa rápida: `git fetch origin && git reset --hard origin/main`
- Los datasets locales no se pierden con reset (están en .gitignore)
- **Encoding Windows**: `render_cr_p1.py` y `render_rnd_p1.py` usan `encoding='utf-8'` en el `open()` de escritura

## 📋 Pendientes próxima sesión (actualizados 25-06-2026, post W26-rnd-ar-card)

Por valor/orden sugerido:

1. ~~**Merge `feat/rnd-ar-card` → `main`**~~ ✅ Mergeado a main · 25-06-2026.
2. **Pipeline W26 normal** — `build_hist_entity.py` ya genera hotel+provider; `calc_bk.py` genera `provider_hist_bk`. Pipeline completo 8 pasos.
3. ~~**Ocultar card NoDispo del panel AR compartido en modo RND**~~ ✅ Implementado · 25-06-2026.
4. **Mail W26** — generar con `render_mail_v3.py` tras el pipeline.
5. **Cleanup #4 — código muerto** — `check_html` lista 32 IDs huérfanos (`w22-*`, handlers AR dim `ar1/2-col-m`/`ar3-th-dim`/etc.).
6. **Reconciliar `PROMPT_INV.md`** — actualizar con valores W25 reales.

✅ **Card AR NoDispo (RND)** — implementada y validada visualmente en `feat/rnd-ar-card`.
✅ **Re-run `calc_inv.py` W25** — completado.
✅ **Mail W25** — enviado, no requiere acción.
<<<<<<< HEAD
✅ **Inventory W25 filter bug** — `hApplyFilter` corregido en HTML parcheado; `calc_inv.py` ya tenía la lógica correcta.
✅ **calc_inv.py** — versión local completa commiteada al repo (HOTEL_BY_WEEK, PP_HOTEL_PACKED, filtros cruzados, CORP_DEST_DATA).
=======
✅ **Inventory W25 filter bug** — corregido.
✅ **calc_inv.py** — versión local completa commiteada al repo.
>>>>>>> 2797b32 (docs: W26-rnd-ar-card · PROMPT_CORE + HISTORIAL_SESIONES actualizados · 25-06-2026)

**Cómo retomar:** merge `feat/rnd-ar-card` → `main`, después recibir datasets W26 → pipeline completo.

**Dataset histórico BK reutilizable:** en W26+, si hay nuevo acumulado, subir `Dataset_bookability_historico.xlsx` y correr `calc_bk.py`.
## 🐛 Bugs pendientes

> **P1–P14 cerrados · B68–B69 cerrados W24 — no quedan bugs de lógica abiertos.**
>
> **RESUELTO (P15 · cobertura de pool CR · opción A):** el panel hotel de CR KPI ahora incluye el **pool completo** (3582 hoteles, todas las bandas) como `sb-hidden`. `tab_eficacia`/`tab_convrate` en `calc_cr.py` ya no capean (`TAB_EF['hotel']`/`TAB_CV['hotel']` = pool completo); `build_card_rows` cap 1000→4000; el render estático en `render_cr_p1.py` queda capeado a top-1000 (el JS lo reemplaza con el JSON completo, así no infla el HTML). Resultado: corp→hotel y searchbox de CR KPI alcanzan cualquier corp/hotel (ej. Iberostar, banda Exitosa). **Solo aplica a CR KPI ef+cv.** ~~Pendiente backlog: extender pool completo a RND KPI nd/ipm~~ → **RESUELTO (B · W24, ver abajo).**
>
> **RESUELTO (B · cobertura de pool RND · cross-filter →hotel — cierra C/D):** el universo hotel de RND es ~21K (vs 3582 en CR), así que volcarlo al DOM como P15 serían +29MB. En su lugar vive en `RND_HOTEL_POOL` (JSON compacto ~2,9MB, NO en DOM), emitido por `_build_rnd_hotel_pool_json()` en `render_rnd_p1.py` (formato 12 campos, banda como índice). En la vista hotel de nd/ipm con cross-filter activo, `_rndLazyHotelRender(card, cf, container)` (assemble) filtra el pool por corp/dest/país, ordena (nd %NoDispo desc · ipm IPM asc), y reconstruye el panel: **5 visibles + 5 cf-extra (cap 10) + resto `sb-hidden` buscable (tope 300)**. Al limpiar el filtro `_rndHotelRestore` repone el estático cacheado. Reusa `_cardRow` vía `_rndPoolToCardRow`. Cobertura corp/país/dest →hotel pasó de ~50% a **100% (nd)** / **70-75% (ipm, máximo posible — el resto no tiene IPM)**. Los cruces que NO tocan hotel (país→corp, dest→corp, etc.) ya funcionaban vía membership. **cap-10 también aplicado al cross-filter NON-hotel** (loop `_crossFilterNonHotel`: top-5 + 5 cf-extra + resto oculto). ~~Pendiente (opcional): variante size-neutral + unificar CR sobre el mismo motor lazy para recuperar ~4MB de DOM~~ → **CR unificado RESUELTO (W24-cr-lazy-unify, ver abajo).**
>
> **RESUELTO (W24-cr-lazy-unify · CR sobre el motor lazy + recorte −4MB):** el motor de RND se generalizó a `_lazyHotelRender(report, card, cf, container)` con config `_HOTEL_POOL_CFG` {cr, rnd} (índices de campo/métrica/orden/grid por reporte); `_rndLazyHotelRender`/`_rndPoolToCardRow` quedaron como wrappers. El motor filtra por **cross-filter** (corp/dest/país), **banda** (`cf.bands`, vista sin cf) y **hotel exacto** (`cf.hotel`, searchbox). CR ef/cv se sirven de `CR_HOTEL_POOL` (3.582, ~0,39MB, emitido por `_build_cr_hotel_pool_json()` en `render_cr_p1.py`, 11 campos). **Solo la canasta global usa el pool** (guarda `_canG` en `_kpiPillRender` y `_kpiSbPoolFor`); las per-canasta (b2c/op/cug, ~100 c/u) siguen por DOM con `CR_CARD_TABS[canasta]`. **Searchbox pool-aware** (`_kpiSbBuildDD`/`_kpiSbSelect` sugieren y renderizan desde el pool en vista hotel — CR y RND) → alcanza cualquier hotel sin tenerlo en el DOM. Recorte: estático `head(1000)→head(5)` + hotel global de `CR_CARD_TABS` `3582→banda crit` (ef 281 / cv 867, el default que `_kpiSortAttach` renderiza en carga/cambio de canasta). **HTML 22→16,99MB (−5MB).** Lazy-ificar AR cards CR (pendiente original `CR_D` 2,0MB + `CR_HOTELS` 0,88MB): **Opción A HECHA (W24-A-dedup)** — `CR_HOTELS` eliminado (−0,87MB, duplicado muerto). **Opción B HECHA (W24-B-sbdedup)** — el bloat real de `CR_D` eran los `_sb` duplicados 4× (globales); deduplicados a `CR_D.global` (−0,84MB). El resto de B (band arrays globales ~318KB → pool) **NO se hizo a propósito**: mala relación riesgo/beneficio (toca el formato de fila de las AR cards validadas; per-canasta 538KB se queda en DOM igual que las KPI cards). RND (`RND_D` ~5,6MB) sigue como follow-up análogo (sus `_sb` probablemente también están duplicados por canasta → mismo patrón de dedup aplicable).
> P5 cerrado W23: `extract_hist_data.py` creado. P12: filtro cruzado Corp+Dest. P13: ConvRate WoW. P14: card BK en Availability.
> B68 cerrado W24: `js_override.js` L1 slash suelto → SyntaxError Chrome (script creció 2MB en W24, cambió contexto de parseo).
> B69 cerrado W24: botón "Ver más" duplicado/faltante en cards AR — `ar_renderTable()` es fuente de verdad para AR1/AR2; `ar3-more-btn` activado directamente.
>
> W22: dataset CR sin columna `Successful UniqueChkRts` — `calc_cr.py` la deriva automáticamente (compatibilidad permanente).
---

## 🗂️ Gestión del Proyecto Claude

### Archivos del proyecto Claude (W23+)
El proyecto Claude solo necesita **4 archivos**. Todos los scripts del pipeline viven en el repo GitHub y se clonan automáticamente con `session_init.py`.

| Archivo | Por qué está en el proyecto |
|---|---|
| `PROMPT_CORE.md` | Contexto inicial — Claude lo lee antes del clone |
| `PROMPT_INV.md` | Instrucciones pipeline Inventory |
| `calc_inv.py` | Pipeline INV — Claude lo necesita para correr Inventory (pipeline distinto al de Supply) |
| `text3.txt` | Token GitHub — leído automáticamente por `session_init.py` |

> `run_inv.py` y todos los scripts de Supply (`calc_supply.py`, `render_*.py`, etc.) viven en el repo y se clonan con `session_init.py`. No subirlos al proyecto.

**Docs** (`HISTORIAL_SESIONES.md`, `NOTA_REFACTOR_PENDIENTE.md`, `BANDAS.md`, `README_QUICK.md`, `COMMIT_GUIDE.md`) — están en el repo, se clonan solos. No subirlos al proyecto.

**Scripts del pipeline** (`calc_inv.py`, `run_inv.py`, `calc_supply.py`, `render_*.py`, etc.) — todos en el repo. `session_init.py` los clona. No subirlos al proyecto.

### Estructura del repo GitHub (W22+)
```
Price/
  ├── 📄 Scripts pipeline PRICE (raíz) — calc_*.py, render_*.py, assemble_unified.py, etc.
  ├── 📁 inventory/
  │     ├── calc_inv.py              ← pipeline Inventory
  │     └── week-NN/INVENTORY_WNN.html + Analisis_Inventory_WNN.xlsx
  ├── 📁 reports/week-NN/SUPPLY_WNN.html
  ├── 📁 checkrates/week-NN/Excels + Dataset
  └── 📁 rates-nodispo/week-NN/Excels + Dataset
```

### GitHub API — archivos grandes
- **Archivos > 1MB:** usar siempre Git Tree API (`POST /git/blobs` → `POST /git/trees` → `POST /git/commits` → `PATCH /git/refs/heads/main`)
- La Contents API (`PUT /contents/`) falla silenciosamente — commit aparece pero contenido queda vacío
- **GitHub Desktop también falla silenciosamente con archivos grandes** (aprendizaje W23): el commit aparece en el historial pero sube la versión vieja o un puntero vacío. En W23 el repo quedó sirviendo `INVENTORY_W23.html` de 44MB pese a que el commit "existía". Síntoma: loading page lenta en Netlify. Verificar tamaño real: `curl -sI raw.githubusercontent.com/.../INVENTORY_WNN.html | grep content-length`
- **Para Inventory:** usar `inventory/run_inv.py --commit` — wrapper que valida entorno/versión/tamaño y commitea el HTML por Git Tree API automáticamente. Resuelve los puntos de fricción de W23 (carpeta equivocada, versión vieja, HTML no borrado, push fallido).
- Afecta: `SUPPLY_WNN.html` (~10MB desde W23), `INVENTORY_WNN.html` (~12MB desde W23, optimizado de 43MB)
- **Archivos `.xlsx`:** Netlify devuelve 403 — usar siempre `raw.githubusercontent.com` para links de descarga (ya corregido en `assemble_unified.py` desde W23)

### Ejecución local desde PowerShell
Tanto el pipeline PRICE como el de Inventory se pueden correr localmente:
```powershell
# PRICE — desde la raíz del repo
# Copiar los 4 datasets a la raíz antes de correr
python calc_supply.py

# Inventory — desde la carpeta inventory/
cd inventory
python calc_inv.py
```

### Re-pipeline en Claude sin pickles W(N-1)

Si Claude no tiene los pickles de la semana anterior:
1. Los datasets W(N-1) están en el repo: `checkrates/week-NN/` y `rates-nodispo/week-NN/`
2. Copiarlos a la raíz y correr `calc_cr.py` + `calc_rnd.py` con env vars de W(N-1)
3. Luego correr `calc_supply.py` normal con W(N)

### ZIP del proyecto (pre-W23, deprecado)
~~`ProyectoClaude_PRICE_WNN.zip`~~ — ya no se genera. Los scripts viven en el repo.

### Canal · Catálogo canónico
```
Producto Propio: DerbySoft · Internal · HBSI · SynXis · Siteminder · Travelclick · Omnibees
Third Party:     Expedia · HotelBeds Apitude · Hotel Unico V2 · Travelgate
```
- Channels sin datos → "sin actividad" `opacity:0.45` · Orden: peor eficacia primero → inactivos al final

---

<<<<<<< HEAD
**Última actualización:** W25-inv-corp-dest · 24-06-2026 (**CORP_DEST_DATA** — filtro corp×destino en Inventory: agregado dataset Python + bloque JS en `hApplyFilter`. Visibilidad de filas funciona (15 corps correctos), actualización de valores pendiente de validación en sesión dedicada.)

**Última actualización previa:** W25-inv-filter · 24-06-2026 (**Inventory W25 filter bug** — `hApplyFilter` línea 2548: `idx < 10` ocultaba destinos de México (idx≥48) aunque pasaran el filtro de región. Fix: `(activeRegion || idx < 10 || isSel)`. Segunda causa: normalización unicode corrupta en `_nr3` por PowerShell. Ambos bugs corregidos en HTML parcheado. `calc_inv.py` ya tenía la lógica correcta — no se modificó.)
=======
**Última actualización:** W26-rnd-ar-card · 25-06-2026 (**Card AR NoDispo en RND — 2 cards lado a lado en HERO + fix pipeline** — `render_ar_card_nodispo()` en `render_rnd_p1.py`: espejo de KPI card con pills de banda (Críticos/Bajo Rend./Sin Conv.) + 3 paneles hotel filtrados. Fixes: `.reset_index(drop=True)` en splits de banda (tabla vacía), headline negro `var(--ink)`, pills outline magenta igual que KPI, `min-height:48px` para alto uniforme entre cards. Canvas `hrnd-arcard-nd` (único, sin colisión). Cableado JS: `kpicard-ar-nd` reconocido en `_handleKpiCardHistClick`, click desde KPI y AR actualizan `hrnd-arcard-nd`. `RND_PAIS_HIST` nuevo dict: `build_rnd_hist()` agrega bucket `pais`, emitido en `_build_rnd_hist_json()`, lookup en JS cuando `_dimV2==='pais'` → sparkline W18-W25 al clickear país. CSS residual layout 2-zonas eliminado. `calc_supply.py`: paso `[11/10] inventory` eliminado. Branch `feat/rnd-ar-card` — pendiente merge a main. Fix `calc_supply.py`: copia `SUPPLY_WNN.html` a `reports/week-NN/` ANTES de `build_package` (que limpia la raíz) + commit automático a GitHub vía Git Tree API al final del pipeline [paso 11].)

**Última actualización previa:** W25-inv-corp-dest · 24-06-2026 (**CORP_DEST_DATA** — filtro corp×destino en Inventory: agregado dataset Python + bloque JS en `hApplyFilter`. Visibilidad de filas funciona (15 corps correctos), actualización de valores pendiente de validación en sesión dedicada.)
>>>>>>> 2797b32 (docs: W26-rnd-ar-card · PROMPT_CORE + HISTORIAL_SESIONES actualizados · 25-06-2026)

**Última actualización previa:** W25-visual · 24-06-2026 (**Mejoras visuales W25** — (1) Channels col TRX 52/56px→68px (Tráfico en 1 línea). (2) AR BK sin WoW TRX (grid 5cols→4cols). (3) Severity RND solo %NoDispo (sin IPM). (4) AR1 RND sparkline side-by-side (`#ar1-hist-cr-wrap` abajo CR / `#ar1-hist-wrap` 210px RND). (5) Excels mejorados: Corp+Destino en tabs hotel RND · AR Consolidado CR+RND (3 bandas top500). (6) `render_historico_svg.py`: SVG `overflow:hidden` + container overflow:hidden — evita desborde del halo del último punto. (7) Cards KPI NoDispo: múltiples iteraciones de rediseño descartadas → revert a layout W24 sin IPM. **Lección:** rediseño de cards complejas requiere HTML standalone para validación visual antes de tocar scripts.)

**Última actualización previa:** W25-sparkline-hist · 23-06-2026 (**Sparklines W19-W23 reales en todas las cards + fill coloreado por banda** — (1) `BK_CORP_HIST` 124 corps + `BK_HOTEL_HIST` 2.964 hoteles + `BK_DEST_HIST` 2.485 destinos generados desde dataset histórico BK (W18-W24); `render_cr_p1.py` los emite en 3 funciones separadas que cargan desde PICKLE_BK (no `D` que es CR). (2) `render_historico_svg.py`: fill coloreado por banda — n-1 segmentos trapezoidales con `getBanda(vals[i]).c` al 13% opacidad, reemplaza fill neutro ACCENT. Regenerar TANTO `render_cr_p1.py` como `render_rnd_p1.py` al modificar. (3) `_isHotelRow = data-cf-corp !== '' && data-cf-corp !== data-hist-label` en `_handleKpiCardHistClick` — detecta hotel rows y saltea el bloque cross-filter (que trataba nombre de hotel como corp → lookup fallaba → solo W24-W25 actualizaban). Para hotel view: usa `CR_CORP_HIST/RND_CORP_HIST[data-cf-corp][metric]` como proxy. (4) Fix `'destino' vs 'dest'`: `_kpiView` guarda `'destino'` pero lookup comparaba `=== 'dest'` — corregido con `=== 'dest' || === 'destino'` en CR, RND y BK. (5) AR hotel handler en `js_override.js`: toggle usa `data-selected` en lugar de `_arCrossFilter.hotel` (self-filter rule — setear cross-filter.hotel causaba BR/SC vacío al filtrar por hotel fuera de su banda); agrega lookup `CR_CORP_HIST[data-cf-corp][metric]`. (6) AR1/AR2 early return restaurado en `_handleKpiCardHistClick` para hotel view — evita conflicto entre los dos handlers (comportamiento invertido del doble click). Cobertura hist W18-W24: corp (63 CR / 111 RND / 124 BK) · dest (1054 CR / 3052 RND / 2485 BK) · hotel (proxy corp CR/RND · directo BK_HOTEL_HIST 2964 hoteles).)

**Última actualización previa:** W25-hist-corp-fix · 23-06-2026 (**canvas histórico corp funcional** — `window['histUpdate_'+CID]` expuesto desde cada canvas IIFE en `historico_module.py`; corp handler en `assemble_unified.py` lo llama con setTimeout(50ms) en lugar de dispatch de evento. Root cause del diagnóstico lento: al modificar `historico_module.py`, regenerar **TODOS** los scripts que lo importan (`render_cr_p1.py`, `render_rnd_p1.py`, `assemble_unified.py`) — si solo se regenera uno, los canvases del otro quedan con la versión vieja. El canvas SÍ actualizaba; la ilusión de "no cambio" era similitud de datos entre corps en el mismo rango de eficacia.)
**Anterior:** W24-pills · 22-06-2026 (**pills de dimensión inactivas → MAYÚSCULA** — las pills del selector de dimensión (Destino/Corp/Hotel/Channel · País/Destino/Corp/Hotel) usaban `text-transform:none` en la **inactiva** (decisión W24-layout: activa MAYÚS / inactiva title-case), lo que Fede veía "en minúscula". Pidió **todas en mayúscula**; la activa se distingue por el **relleno**, no por el case. Cambiado `text-transform:none → uppercase` en `_PILL_INACT`/`_PI` de `render_cr_p1.py` (3) y `render_rnd_p1.py` (2) + `kpi_setView` en `assemble_unified.py` (`textTransform` ya no `active ? 'uppercase' : 'none'`, **siempre** `'uppercase'` — si no, al cambiar de dimensión volvían a title-case). ⚠️ **Casi-regresión:** el `sed` tocó por error el subtítulo del IPM (`render_rnd_p1.py` L334, `· Income Per Million · GB USD por millón`, que va en `none` a propósito) → **revertido a `none`**. Verificado: 0 pills inactivas con `none`, subtítulo IPM intacto. Regenerado part1 CR+RND (`VOL_NUM=24`) + reensamblado. NO se tocaron las tabs de canasta (`.c-chip`, ya uppercase) ni las pills de banda AR (Críticos/Bajo Rend/Sin Conv). Validado visual Fede. Archivos: `render_cr_p1.py`, `render_rnd_p1.py`, `assemble_unified.py`, `reports/week-24/SUPPLY_W24.html`.)

**Última actualización previa:** W24-histbadges · 22-06-2026 (**badges Opción B propagados al panel histórico + tablas de severity + cards AR · Aceptable texto blanco · calc_inv reconciliado** — el fix de Opción B se había aplicado a las KPI cards pero **faltaban 3 superficies** que usan mapas/parts distintos: (1) **panel histórico** — `historico_module.py` `_BANDA_COLORS` ya estaba en Opción B en la fuente pero **nunca se commiteó ni se regeneró el HTML** (el commit W24-layout horneó part1 con el módulo viejo); regenerado part1 → badges box+footer sólidos. (2) **tablas de severity** (`render_severity` en p2, vía `banda_colors()`) y **cards AR** (`sev_badge_html_p2`) — part2 se había generado **antes** de migrar `BANDA_COLORS` y no se regeneró; regenerado part2. (3) **`BC` de `AR3_CANVAS_JS`** (`assemble_unified.py`) seguía pálido — migrado a Opción B. Además **Aceptable fg #5C3A00 → #FFFFFF (blanco)** en los 8 mapas (Fede lo pidió "blanco como las otras"; **ojo:** blanco sobre el ámbar `#FBBF24` es contraste bajo, queda flojo — si molesta, oscurecer el bg a ~`#D97706`). Todo uppercase (ya tenían `text-transform`). Diff vs publicado: **236 líneas, 100% colores de banda**, sin tocar datos/métricas/labels. **Aprendizaje:** cambiar un mapa de banda exige regenerar los parts que lo hornean (part1 histórico / part2 severity+AR) + reensamblar (AR3); olvidarlo deja badges pálidos solo en esas superficies — y **`VOL_NUM=24` es obligatorio al regenerar parts** (si no, `wow_box` sale W19/W20). En paralelo: `inventory/calc_inv.py` repo reconciliado a W24 (commit `1a698eb0`, cierra pendiente de divergencia). Validado: diff quirúrgico + visual Fede. Archivos: `historico_module.py`, `render_helpers.py`, `js_override.js`, `assemble_unified.py`, `reports/week-24/SUPPLY_W24.html`.)
**Anterior:** W24-layout · 21-06-2026 (**badges sólidos + esquema de pills 2-líneas + tabs simétricas + severity sin target** — (1) **Badges de severity → Opción B (sólido pleno, texto claro)**: bg saturado + texto blanco/oscuro (Exitosa #1A6B4A/blanco · Aceptable #FBBF24/#5C3A00 · Revisar #F97316/blanco · Crítica #C0392B/blanco · Súper Crítica #2D2828/blanco · Sin Conv #8A8377/blanco). El color de banda estaba duplicado en **6 mapas** (BANDA_COLORS Python + 5 JS) → migrados TODOS por **par completo** (bg+fg juntos, nunca hex suelto: los pálidos viejos #E1F5EE/#FCE4F1 se comparten con pills/accent-soft). (2) **Pills en 2 líneas** (Fede aclaró el esquema): **primera línea** (selector de dimensión) = color de **sección** (CR violet `#5C469C`/relleno `#EDE8F7` · RND magenta `#EA0074`/relleno `#FCE4F1`; activa relleno+MAYÚSCULA, inactiva outline+title) — NUNCA verde; **segunda línea** (cross-filter, aparece al SELECCIONAR un elemento) = **SIEMPRE verde** `#E1F5EE`/`#1A6B4A` (CR y RND). Antes: primera línea activa en verde (mal) + cross CR en violet. (3) **Tabs de canasta simétricas** (`.c-chip` `flex:1`+`justify-content:center`) + estiran al alto de la barra (`height:54px`→`min-height:54px`, +`:last-child` sin border-right). (4) **Severity badges sin target** (`banda_pill` ya no renderiza `· Target`; el "Target: Bookings" del masthead es otro elemento, intacto). Validado jsdom (badges B con texto blanco, primera línea = sección, cross verde, 0 errores) + visual Fede. Sin cambio de tamaño (solo strings de color/estilo). Archivos: `demo_css_w22.css`, `render_helpers.py`, `render_cr_p1.py`, `render_rnd_p1.py`, `assemble_unified.py`, `js_override.js`.)
**Última actualización previa:** W24-rnd-percanasta · 21-06-2026 (**desglose per-canasta real de las KPI cards RND + dedup `_sb` RND (−1,21MB)** — el `check_html` destapó que `RND_CARD_TABS` era byte-idéntico en las 4 canastas: `render_rnd_p1.py` usaba el `TAB_NoDispo`/`TAB_RPM` **global** para todas ("por ahora global"), un **gap funcional** (cada canasta es un subset del Global por DistributionCategory y debía desglosar). Fix: el build ahora usa los `agg_pais`/`agg_dest`/`agg_corp`/`agg_hotel` **per-canasta** del pickle (`CANASTA[c]`; global sigue con `TAB_*`) → b2c/op/cug muestran su slice real (b2c top Grecia vs global Dinamarca). **Caveat:** los `agg_*` per-canasta no traen `Trafico_WoW_pct` (ni `agg_hotel` el `%NoDispo_W18`) → el WoW de tráfico y el mini-hist del tab hotel salen vacíos per-canasta; nd/ipm + su WoW + banda completos (enriquecer en calc_rnd.py = follow-up). En paralelo: dedup de los `_sb` de RND (globales por diseño, 4× idénticos) a `RND_D.global` — `_arRows` lee `_sbData` de CR_D.global/RND_D.global según modo. RND_D 5,83→4,54MB. Validado jsdom (4 hashes distintos per-canasta, `_sb` ausente en per-canasta, RND `_arRows` 4 canastas OK, CR intacto 180/180) + visual Fede. **Arco de sesión: 22→14,99MB (−7MB).** Dups que quedan (intra-canasta `hotels==hotels_dnc`, `hotels_sc==hotels_ipm_sc` ~700KB) — más delicados, no urgentes.)
**Última actualización previa:** W24-check-html · 21-06-2026 (**`check_html.py` — auditoría automática del HTML en cada build** — enganchado al final de `assemble_unified.py` (no fatal). 4 chequeos: (1) COMPOSICIÓN (peso de cada `var` top-level, ordenado, % del total); (2) DUPLICADOS (blobs byte-idénticos por md5 emitidos ≥2× — es lo que habría cazado `CR_HOTELS` y los `_sb` 4× desde el día uno); (3) PRESUPUESTO (total + delta vs baseline local `.html_budget.json`, gitignored); (4) HUÉRFANOS (`getElementById('X')` literales sin `id="X"` en el DOM · `onclick="fn("` sin `function fn`). Barrido inicial sobre W24: detectó **~4,44MB de duplicación casi toda en RND** (`RND_CARD_TABS` 4× = 806KB + sub-arrays nd/ipm 4×; `RND_D._sb` 4× = sc_sb 514KB+dnc_sb 486KB+br_sb 321KB; internos `hotels==hotels_dnc`, `hotels_sc==hotels_ipm_sc` ~180KB c/u; `BK_CARD_TABS` 4×) y **32 IDs huérfanos** confirmando el código muerto (panel `w22-*` completo + elementos AR dim `ar1/2-col-m`/`ar3-th-dim`/etc.). Próximo: dedup RND (~3MB, mismo patrón de bajo riesgo que la B de CR) + cleanup #4 verificable contra la lista de huérfanos.)
**Última actualización previa:** W24-B-sbdedup · 21-06-2026 (**dedup de los pools `_sb` del searchbox (−0,84MB)** — al medir `CR_D` para el port al pool (Opción B del lazy AR), el bloat real eran los `_sb` (crit_sb/br_sb/sc_sb) **duplicados 4×**: son globales (se construyen de `g_hotel`, no de la canasta) e idénticos por md5 en las 4 canastas. Ahora se emiten solo en `CR_D['global']` (`render_cr_p2.py` los borra de b2c/op/cug tras `build_cr_d`) y `_arRows` (js_override) los lee de `CR_D.global` vía `_sbData` (CR; RND sin tocar, lee su propio `_sb`). Resultado idéntico (searchbox AR alcanza los mismos hoteles en toda canasta). HTML 17,87→16,99MB. Validado jsdom (`_sb` ausente en per-canasta, `_arRows` global 180/645/968 igual, b2c crit=180 con 175 extras del `_sb` global, RND intacto) + visual Fede · **resto de B NO se hizo** (band arrays globales ~318KB → pool: mala relación riesgo/beneficio, toca el formato de fila de las AR cards validadas; per-canasta 538KB se queda en DOM igual que KPI). Arco de sesión: 22→17,9 (lazy KPI)→17,87 (A)→16,99 (B), −5MB.)
**Última actualización previa:** W24-A-dedup · 21-06-2026 (**elimina duplicación `CR_HOTELS` (−0,87MB)** — `CR_HOTELS` era una copia de los arrays hotel de `CR_D` (hotels/crit/br/sc/cv) extraída en render_cr_p2; su único consumidor era el `getRows` del panel w22 "Análisis de Rendimiento", **que ya no existe en el DOM** (reemplazado por las AR cards). Quitado el branch en `assemble_unified.py` (cae al fallback `CR_D` + fallback global de la key) + dejado de emitir en `render_cr_p2.py` + comentario en `demo_js_main.js`. Las AR cards y `data()` ya leían `CR_D` directo, sin cambio. HTML 17,9→17,87MB. Validado jsdom (CR_HOTELS undefined, `_arRows` 180/645/968/1000, per-canasta b2c OK, 0 errores) + visual Fede · **es la Opción A** del pendiente lazy AR CR; **Opción B** (portar arrays hotel de `CR_D` ~1,9MB al pool + recablear 15+ sitios) queda como sesión dedicada · tabla "Datos históricos reales" del CORE extendida a W16-W24)
**Última actualización previa:** W24-hist-semanas · 21-06-2026 (**histórico W17-W24 dinámico + serie BK alineada al dato real** — `_SEMANAS_HIST` (estaba hardcodeado W16-W23, pisaba los labels de TODOS los tooltips) ahora se inyecta desde `historico_data.SEMANAS` (ventana móvil, última = semana actual; W25 se auto-ajusta) · la serie BK de `historico_data` estaba **corrida una semana** vs el dato real del pickle → alineada a `hist_by_week` (W17-W24 = [98.44 … 98.67]); aplica a `historico_data.py` (BK global), al canvas `AR3_CANVAS_JS` (SEMANAS+VALS_DEF inyectados dinámicos desde `hist_by_week`) y a la card BK `h-bk-global` (render_cr_p1) — ahora ambos canvas BK coinciden · validado jsdom (los 10 canvas con sem W17-W24, BK 98.44→98.67 consistente) + visual Fede · **pendiente #4** (cleanup A2b handlers dim muertos de AR) diferido al refactor AR cards #1)
**Última actualización previa:** W24-cr-lazy-unify · 21-06-2026 (**CR unificado sobre el motor lazy de RND** — el hotel de las KPI cards CR (ef/cv) ahora se sirve del pool compacto `CR_HOTEL_POOL` (3.582 hoteles, ~0,39MB, NO en DOM) con la MISMA función genérica que RND. `_lazyHotelRender(report, card, cf, container)` + `_HOTEL_POOL_CFG` {cr, rnd} · filtros del motor: cross-filter (corp/dest/país) + banda (vista sin cf) + hotel exacto (searchbox) · **searchbox pool-aware** en CR y RND (alcanza cualquier hotel sin tenerlo en el DOM, vía `_kpiSbPoolFor`) · estático CR `head(1000)→head(5)` + hotel global de `CR_CARD_TABS` `3582→banda crit` (ef 281 / cv 867; per-canasta b2c/op/cug intactas por DOM, ~100 c/u) · **HTML 22→17,9MB (−4,1MB)** · solo canasta global usa pool (guarda `_canG`); per-canasta sigue DOM · validado jsdom (paridad exacta de bandas, cross-filter, per-canasta, searchbox alcanza Exitosa fuera del crit, RND intacto) + visual Fede · **pendiente:** lazy-ificar AR cards CR (`CR_D` 2,0MB + `CR_HOTELS` 0,88MB ≈ ~3MB más))
**Última actualización previa:** W24-rnd-pool-B · 21-06-2026 (**C/D RESUELTOS** — cross-filter →hotel en RND KPI nd/ipm vía pool completo lazy `RND_HOTEL_POOL` (21.183 hoteles, JSON compacto 2,9MB, NO en DOM) + `_rndLazyHotelRender`/`_rndHotelRestore` · cobertura corp/país/dest →hotel 50%→100% (nd) / 70-75% (ipm) · **cap-10** en cross-filter hotel y non-hotel (5 visibles + 5 cf-extra + resto buscable) · HTML 19→22MB · validado jsdom (0 errores, NH ipm 0→1 hotel, restore OK) + visual Fede)
**Última actualización previa:** W24-ar-hotel-only · 20-06-2026 (P15 RESUELTO opción A: pool completo CR KPI ef/cv 3582 hoteles · **refactor AR SOLO HOTEL** — eliminadas pills de vista corp/dest/channel en las 3 cards AR, data dims vaciada −952KB, resuelve #2/#3/#4/#6/#9 · #7 semanas dinámicas vía _VOL_NUM · #1 pill channel BK KPI · 10/10 bugs resueltos · #8 searchbox KPI cableado vía DELEGACIÓN de eventos a nivel document (sobrevive al re-render de las cards; filtra panel de vista activa _kpiView[card], al seleccionar dispara click real de la fila → cross-filter+highlight+gráfica, limpia query y fija fila visible))
**Última actualización previa:** W24-rnd-kpi · 20-06-2026 (KPI cards RND migradas a pills + 6 bugs cross-filter/searchbox: filtro País→Destino, click hotel grafica, pills severidad AR en hotel, AR cards distintas por IPM, searchbox AR en vistas dim · array RND_CARD_TABS alineado a índices de CR · canvas redraw con try/catch global)
**Pipeline W24-rnd-kpi:** 2 KPI cards RND (NoDispo/IPM) migradas de radios CSS a pills verdes · `RND_CARD_TABS` realineado (hist r9/r10, cf r11/r12/r13) · `_crossFilterNonHotel` filtra panel de vista activa + País→Destino · `g_dest` enriquecido con país en `calc_rnd.py` · `_arDimRows` card 2 RND ordena por IPM · searchbox AR unificado con clase `.sb-search-hit{display:grid !important}` (dos handlers oninput) · `w22_redrawCanvas` envuelto en try/catch (no corta `w22_setMode`)
**Última actualización previa:** W24-kpi-unify · 20-06-2026 (KPI cards: 3 cards unificadas sobre `_kpiSortAttach` + channel con sort/selección · pills verdes · cross-filter hotel por corp/dest · catálogo channels unificado · paso 10 copia HTML a reports/)
**Pipeline W24-kpi-unify:** las 3 KPI cards (EF/CV/BK) 100% unificadas · pills activas VERDES `#1A6B4A` · cross-pills orden de selección · channel con sort+selección en las 3 (filas `.bk-row` + `bkSort`) · catálogo channels canónico + RateFox · cross-filter hotel por `data-cf-corp`/`data-cf-dest` · límite 1000 filas buscables · paso 10 en calc_supply copia HTML a reports/week-NN
**Pipeline W23-bk:** Bookability como 3ª card cross-canasta · sort clickable con flechas ↕/↑/↓ · Channel unificado flex-column · Severity Eficacia/NoDispo dinámico · BK oculto en Availability
**Última limpieza:** W22-pre — 50 reglas → 35 · sección archivos eliminada · arquitectura en `NOTA_REFACTOR_PENDIENTE.md`
**Pipeline W22:** histórico W16–W22 (7pts) · fix puntos canvas · compatibilidad dataset CR sin Successful · mobile responsive · header redesign
**Pipeline W23:** histórico W16–W23 (8pts) · fix display:table-row filas 6-10 · fix border-bottom rows-more · calc_supply.py pipeline completo 8 pasos
**Pipeline W24:** histórico W17–W24 (8pts, ventana móvil) · B68 js_override L1 SyntaxError · B69 Ver más duplicado/faltante cards AR · estandarización botones Ver más · RateFox Third Party
**Post-W22:** Hub visual · badges amarillo FCB000 · loading screens · session_init.py · inventory/calc_inv.py en repo · Connectivities magenta + Availability magenta · footer unificado beige · State of PriceTravel Product · Evolución Histórica del Producto · rojo `#FF3B30`

---

## Mantenimiento del PROMPT_CORE

1. **Máximo 35 reglas** en "Cosas que NUNCA" — al llegar al límite, hacer pasada de limpieza
2. **No duplicar** — si una regla está en el código, puede eliminarse del CORE
3. **Lecciones aprendidas → HISTORIAL** · El CORE solo tiene "qué hacer"
4. **Revisión periódica** — cada ~4 commits importantes

---

## 📋 Mantenimiento de documentación — triggers por archivo

Claude valida estos triggers al final de cada sesión **sin que Federico lo pida**.

| Archivo | Actualizar cuando... |
|---|---|
| `PROMPT_CORE.md` | Se cierra un bug · cambia arquitectura · nueva regla · limpieza periódica |
| `HISTORIAL_SESIONES.md` | **Siempre** al final de sesión con cambios de código o bugs cerrados |
| `NOTA_REFACTOR_PENDIENTE.md` | Cambia la arquitectura · nueva función centralizada · nuevo patrón de cambio |
| `README_QUICK.md` | Cambia estructura del repo · nuevas URLs · métricas de la semana publicada |
| `BANDAS.md` | Solo si cambian thresholds o paleta de colores |
| `COMMIT_GUIDE.md` | Solo si cambia el proceso de commit o estructura del repo |

### Checklist de cierre de sesión

Al terminar cualquier sesión con cambios, Claude debe verificar:

```
□ PROMPT_CORE.md — ¿hay nuevas reglas? ¿colores? ¿arquitectura nueva?
□ PROMPT_INV.md — ¿cambió algo de Inventory?
□ HISTORIAL_SESIONES.md — agregar entrada con: contexto, cambios, archivos modificados
□ Revisar el reporte de check_html del último build — ¿duplicados nuevos? ¿huérfanos nuevos? ¿delta de tamaño inesperado?
□ Verificar que build_package.py refleja TODOS los cambios visuales de la sesión
□ Regenerar index.html desde build_package.py y verificar el HTML antes de commitear
□ ZIP del proyecto Claude — regenerar SOLO después de todo lo anterior
□ Commit GitHub — incluir docs + scripts actualizados
```

**Regla crítica:** El ZIP del proyecto Claude se genera ÚLTIMO, después de verificar
que todos los cambios están en los scripts y en los docs. Nunca antes.

**Si Claude no propone este checklist al cerrar sesión, Federico puede pedirlo con:** `"checklist de cierre"`


**Última actualización:** W25-sparkline-hist · 23-06-2026 (**Sparklines W19-W23 reales en todas las cards + fill coloreado por banda**

**Hist datasets (BK):** `BK_CORP_HIST` (124 corps) + `BK_HOTEL_HIST` (2.964 hoteles) + `BK_DEST_HIST` (2.485 destinos) generados desde `Dataset_bookability_historico.xlsx`. Emitidos por `render_cr_p1.py` (_build_bk_*_hist_json, cada uno carga desde PICKLE_BK). En W26+: `calc_bk.py` los genera automáticamente del dataset acumulado.

**Fill coloreado (`render_historico_svg.py`):** en lugar de fill neutro ACCENT+7%, ahora n-1 segmentos trapezoidales coloreados con `getBanda(vals[i]).c` al 13% opacidad. Aplica a todos los SVG sparklines: `h-bk-*`, `hcr-*`, `hrnd-*`. Regenerar `render_cr_p1.py` Y `render_rnd_p1.py` al cambiar este archivo.

**_isHotelRow (`assemble_unified.py`):** `data-cf-corp !== '' && data-cf-corp !== data-hist-label` detecta hotel rows. Si es hotel, se saltea el bloque cross-filter (que trataba el nombre del hotel como corp → lookup fallaba). Para hotel view en cualquier card KPI: usa `CR_CORP_HIST/RND_CORP_HIST[data-cf-corp][metric]` como proxy histórico.

**'destino' vs 'dest' mismatch:** `_kpiView` guarda `'destino'` pero el lookup comparaba `=== 'dest'`. Fix: `(_dimV2 === 'dest' || _dimV2 === 'destino')` en los lookups de CR, RND y BK.

**AR hotel handler (`js_override.js`):** toggle usa `data-selected` (no `_arCrossFilter.hotel`). Self-filter rule: hotel view NO setea cross-filter hotel (causaba BR/SC vacío). Lookup corp hist: `CR_CORP_HIST/RND_CORP_HIST[data-cf-corp][metric]` en el handler.

**AR1/AR2 early return:** restaurado en `_handleKpiCardHistClick` para hotel view (evita conflicto con el handler de js_override → comportamiento invertido del doble click).

**Cobertura hist W18-W24:** Corp (63 CR / 111 RND / 124 BK) · Dest (1054 CR / 3052 RND / 2485 BK) · Hotel (proxy corp para CR/RND · directo BK_HOTEL_HIST).

)

