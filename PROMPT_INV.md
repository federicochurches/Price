# 🏨 PROMPT INV · Hotel Inventory · Supply Analytics HUB
**Versión v13.0 · Junio 2026 · calc_inv.py → INVENTORY_WNN.html + Analisis_Inventory_WNN.xlsx**

---

## 🧠 Rol y Contexto

Módulo **Hotel Inventory** del Supply Analytics HUB de PriceTravel.
Script principal: `calc_inv.py` → genera `INVENTORY_WNN.html` (~5MB) + `Analisis_Inventory_WNN.xlsx`.
Dataset: `dataHoteles_contratos.xlsx` (header=1, 571K+ rows)

---

## 📊 Universo y KPIs

| Métrica | Valor W23 |
|---|---|
| Sistema (HtActive=1) | 314.719 |
| Sin contrato (sincontrato) | 5.128 — **excluidos siempre** |
| **Universo con contrato** | **309.591** |
| Producto Propio (SP+H) | 53.097 · 17.2% |
| Solo Propio | 4.746 · Hybrid | 48.351 |
| Third Party | 256.494 · Target 2026 | 70.000 |
| Gap | 16.903 · Avance | 75.9% |
| Ritmo necesario | ~583 / sem |
| Independientes sin directo | 246.275 · Destinos | 11.698 |

**Variables Python canónicas:** `N` · `pp` · `solo_propio` · `hybrid` · `solo_terc` · `gap` · `SEMANAS_RESTANTES` · `ritmo_nec`

**Filtros de datos:**
- `header=1` en `pd.read_excel` (fila 0 es metadata)
- `TipoHotel != 'sincontrato'` → excluye sin contrato
- TipoHotel normalization (`TIPO_NORM`): `'solo tercero'→'sólo terceros'`, `'solo propio'→'sólo propio'`
- TipoHotel map (`TIPO_MAP`): `'sólo propio'→Solo Propio`, `'Propio_con_tercero'→Hybrid`, `'sólo terceros'→Third Party`
- `df_tp = df[TipoHotel=='sólo terceros']` · `df_pp = df[TipoHotel.isin(['sólo propio','Propio_con_tercero'])]`

---

## 🏗️ Arquitectura HTML

### Config semanal
```python
WEEK          = "W23"
WEEK_NUM      = 23
YEAR_ACTUAL   = 2026
SNAPSHOT_DATE = "2 de Junio de 2026"
INPUT_FILE    = "dataHoteles_contratos.xlsx"
OUTPUT_FILE   = f"INVENTORY_{WEEK}.html"
TARGET_PROPIO = 70_000
```

### Outputs
1. `INVENTORY_WNN.html` — reporte interactivo (~5MB)
2. `Analisis_Inventory_WNN.xlsx` — 5 hojas: Resumen · Por Región · Por Corporativo · Por Destino · Por Channel

### Estructura de secciones HTML
1. **Masthead** — estructura idéntica a Supply PRICE
2. **KPI Bar** — 4 cards en grid
3. **Evolución Histórica** — gráfico Chart.js (sección renombrada desde W23)
4. **Distribución y Exploración** — tabla unificada con pills integradas
5. **Sin Contratación Directa (GAP)** — tabla separada activada por pill
6. **Channel View** — vista por canal de conectividad
7. **Footer** — botón descarga Excel

---

## 🎨 Masthead — Estructura canónica (W23+)

Idéntica al Supply PRICE — misma arquitectura de 3 bloques:

```html
<div class="masthead-top-rule">        ← barra negra 3px
<div class="masthead-inner">           ← badge + h1 + logo | border-bottom:1px solid var(--rule)
  <div class="masthead-week">WEEK 23   ← pill cyan #4FC3F4, border-radius:3px (no redondeado)
  <h1> clamp(20px,2.0vw,30px)          ← "State of PriceTravel Product"
  <img class="masthead-logo" h:40px>   ← logo color con transparencia
<div class="masthead-sub">             ← fecha | vol | border-bottom:3px solid var(--ink)
```

**CSS clave:**
- `.shell { padding: 32px 48px 80px }` — espacio sobre la barra negra
- `.masthead-inner { padding: 14px 0 12px }` — aire del bloque principal
- `.kpi-bar { margin-top: 24px }` — separación de cards del sub-header
- `.masthead-logo { height: 40px }` — logo color RGBA 518×126px

---

## 🃏 KPI Bar — 4 cards

**Card 1:** Total `N` (cyan) · PP · Third Party
**Card 2:** Target (cyan) · Avance % (green) · Gap (rojo)
**Card 3:** Gap por Corporativo — barra roja gap% (7 cadenas, excl. AA-Independent)
**Card 4:** Gap por Región — mismo layout
Labels → `color:var(--ink-muted)`

---

## 📈 Evolución Histórica (W23+, antes "Crecimiento Histórico")

### Chart — Combo Violet/Cyan (W23+)

**Dataset 1 — Acumulado (línea):**
- Color: `#5C469C` violet
- `borderWidth: 2.5`, `tension: 0.42`
- **Sin puntos intermedios** — `pointRadius: acum.map((_,i) => i===acum.length-1 ? 6 : 0)`
- Punto final con `pointBorderColor: '#F5F0E8'`, `pointBorderWidth: 2.5`
- **Área dinámica** — gradiente cuya opacidad escala con ratio PP/Total:
  ```js
  const _ppRatio = pp / N;  // 17.2% en W23
  const _alphaTop = Math.min(0.42, 0.10 + _ppRatio * 1.6);
  // grad: rgba(92,70,156, _alphaTop) → rgba(92,70,156, 0.01)
  ```

**Dataset 2 — Variación (barras):**
- Color: `rgba(79,195,244, 0.55)` cyan
- `barPercentage: 0.45`
- **Label dinámico** según nivel activo:
  ```js
  hLevel==='sem' ? 'Variación semanal' : hLevel==='mes' ? 'Variación mensual' : 'Variación anual'
  ```

**Ejes Y — reforzados (W23+):**
- Izquierdo: título `'Hoteles acumulados'` · `font-size:10, weight:700` · color `#5C469C`
- Derecho: título dinámico `'Variación semanal/mensual/anual'` · `font-size:10, weight:700` · color `#4FC3F4`
- Ticks izquierdo en violet, ticks derecho en cyan

### Controles
1. Toggle Por Año / Por Mes / Por Semana
2. Dropdowns Año / Mes / Semana — "Todos" como default
3. Pills Dimensión: `Región | Corporativo | Destino | Channel`
4. Pills Tipo: `Contratación | Prod. Propio | Solo Propio | Hybrid | Sin Contrat.`
5. Searchbox autocomplete — busca destinos, corporativos, regiones
6. `#hf-active-pills` — pills activas encima del gráfico
7. `× Limpiar` — visible solo cuando `hIsFiltered()` es true

### `hGetDim()` — lógica de fuente de datos
```js
if (activeChannels.length > 0) {
  // canal activo → usar HIST.dim (hotel×canal)
  // corp+channel: hoteles del corp QUE TIENEN ese canal (no intersección)
  return HIST.dim.filter(r => ... && activeChannels.includes(r.channel) ...)
} else {
  // sin canal → HIST.dim_hotel (un row por hotel, sin duplicar)
  return HIST.dim_hotel.filter(r => ...)
}
```

### Searchbox autocomplete — reglas críticas
- `_applyAutocompleteSelection`: evalúa `alreadyDest` ANTES de llamar `udToggleDim`
- Delay: 300ms si switch de dim, 80ms si ya en dest
- Fallback por `data-dest-name` si `data-row-idx` no encuentra el row
- Limite de rows en DOM: **1000** (`dest_grp.head(1000)` y `dest_mkt.head(1000)`)

---

## 🗂️ Distribución y Exploración

### Pills — dos filas
**Fila 1 (Dimensión):** `Región | Corporativo | Destino | Channel` — fondo sólido cyan
**Fila 2 (Contratación):** `Todos | Prod. Propio | Solo Propio | Hybrid | Sin Contrat.` — fondo sólido violet · Sin Contrat. en rojo

### Columnas — TODAS SIEMPRE VISIBLES
Los CSS `col-show-XX` NO ocultan otras columnas. Solo resaltan el header activo.

| Columna | Color | Clase |
|---|---|---|
| Dimensión | `var(--ink)` bold | — |
| Sub-label región (Destino) | `var(--ink-muted)` 10px | `<div>` debajo |
| Total | `var(--ink)` | `td-tot` |
| P. Propio | cyan `#4FC3F4` | `td-pp` |
| Solo P. | `var(--green)` | `td-sp` |
| Hybrid | `var(--violet)` | `td-hy` |
| Third P. | `var(--ink)` | `td-tp` |
| % P.Propio | barra cyan | `pct_bar_html()` |
| vs Global | verde/rojo + barra | `vs_bar_html()` |

### dest_grp — aggregation (W23+)
```python
dest_grp = df.groupby(['Destino','Region_display']).agg(
    total        = ('IdHotel','count'),
    prod_propio  = ('TipoHotel', lambda x: ((x=='sólo propio')|(x=='Propio_con_tercero')).sum()),
    solo_propio  = ('TipoHotel', lambda x: (x=='sólo propio').sum()),   # ← W23: agregado
    hybrid       = ('TipoHotel', lambda x: (x=='Propio_con_tercero').sum()),  # ← W23: agregado
    solo_tercero = ('TipoHotel', lambda x: (x=='sólo terceros').sum()),
).reset_index()
```
Las filas de destino muestran `solo_propio` y `hybrid` reales (no `—` hardcodeado).

### GLOBAL row — orden correcto (W23+)
```html
GLOBAL | N (total) | pp (P.Propio) | solo_propio | hybrid | solo_terc | pct_bar | —
```
Antes tenía `pp` en posición de total — corregido en W23.

### Límites de rows en DOM
- `corp_grp.head(200)` · `dest_grp.head(1000)` · `dest_mkt.head(1000)`
- Acapulco está en posición ~564 en dest_mkt — por eso el límite mínimo es 1000

### Headers ordenables
- Total: `udSortTotal()`
- PP/SP/Hybrid: `udSortCol('td-pp')` / `('td-sp')` / `('td-hy')`

---

## 🚫 Sin Contratación Directa (GAP view — W23+)

### `gapSyncDim()` — lógica two-pass (W23+)
Cuando `soloSinContrat` está activo (pill "Sin Contrat." seleccionada):
```js
// Dos pasadas — muestra los primeros 10 rows que pasen el filtro
// independientemente de su rowIdx original
let visibleCount = 0;
destRows.forEach(r => {
  const passesContrat = !soloSinContrat || conD === 0;  // con_directo=0
  const passesReg     = !activeReg.length || activeReg.includes(rowReg);
  if (!passesContrat || !passesReg) { r.style.display = 'none'; return; }
  // Muestra primeros 10 calificados, sin importar posición original
  r.style.display = visibleCount < 10 ? '' : 'none';
  if (visibleCount < 10) visibleCount++;
});
```

### data attributes en gap-dest-row (W23+)
```html
<tr class="gap-dest-row" data-row-idx="{i}" data-region="{reg}"
    data-con-directo="{con_d}" data-sin-directo="{sin_d}">
```
El filtro `soloSinContrat` usa `r.dataset.conDirecto` para ocultar destinos con PP.

---

## 📊 Excel — `Analisis_Inventory_WNN.xlsx`

| Hoja | Contenido | Orden |
|---|---|---|
| Resumen | KPIs: N, pp, solo_propio, hybrid, solo_terc, target, avance, gap, ritmo | — |
| Por Región | Todos los hoteles · channels como Sí/No | Por región |
| Por Corporativo | Idem | Por corp + hotel |
| Por Destino | Idem | Por destino + hotel |
| Por Channel | 1 fila por hotel × channel activo | Por channel + corp + hotel |

Headers: bold blanco sobre `#333132`. Auto-width columnas (max 45 chars).

---

## ⚙️ JS — Funciones críticas

| Función | Descripción |
|---|---|
| `_tryInit()` | Init con retry; `hInit()`; inicia con `udContent('all')` |
| `hInit()` | Init gráfico; `hPopulateWeeks(2026, null)`; fallback Por Año |
| `hGetDim()` | Fuente de datos según filtros activos — HIST.dim si channel, HIST.dim_hotel si no |
| `hRender()` | Renderiza Chart.js con Combo Violet/Cyan; label dinámico según `hLevel` |
| `hPopulateWeeks(yr, mo)` | Popula `sel-week`; `disabled=false` |
| `hRenderActivePills()` | `hf-active-pills` + `btn-limpiar` + `udSyncBadges()` |
| `udSyncBadges()` | Sistema unificado — Set dedup, todas las pills activas cyan |
| `hClearFilter(key)` | Quita filtro individual, llama `hRenderActivePills()` |
| `udContent(id, btn)` | Métrica; segundo click = reset; resalta header; inicia con 'all' |
| `udSetDim(dim, btn)` | Cambia dimensión activa; limpia searchbox; llama `hApplyFilter()` |
| `udToggleDim(dim, btn)` | Segundo click sobre dim activa = no-op |
| `udSortCol(colClass)` | Ordena filas por columna asc/desc |
| `udRowClick(type,val,el)` | Toggle filtro fila; `udSyncBadges()` + `gapSyncDim()` |
| `udToggleGap(btn)` | Toggle Sin Contrat. Directa |
| `gapSyncDim()` | Two-pass — filtra gap table por filtros activos + soloSinContrat |
| `chDrill(channel, row)` | Click channel → filtra histórico; badge cyan; sin pill de dimensión |
| `_applyAutocompleteSelection(it)` | Selección del dropdown — delay dinámico, fallback por destName |

---

## 🎨 Paleta

| Elemento | Color |
|---|---|
| Badge WEEK masthead | `#4FC3F4` cyan pill `border-radius:3px` |
| Acento principal (accent) | `#4FC3F4` cyan |
| Combos (borde + texto, siempre) | `#4FC3F4` cyan |
| Pills activas / badges | `#4FC3F4` cyan |
| Chart — curva acumulado | `#5C469C` violet con área dinámica |
| Chart — barras variación | `rgba(79,195,244,0.55)` cyan |
| Chart — eje izquierdo | `#5C469C` violet |
| Chart — eje derecho | `#4FC3F4` cyan |
| Métricas PP/SP/Hybrid (pills) | `#1A6B4A` verde |
| Sin Contrat. Directa (pill) | `#C0392B` rojo |
| vs Global positivo | `var(--green)` |
| vs Global negativo | `#C0392B` |
| Fondo row activa | `#E0F4FD` |
| Third Party % Gap | `#C0392B` rojo bold |
| Violet acento tabla | `#5C469C` / `#EDE8F7` |

---

## 🐛 Bugs cerrados

| # | Descripción | Sesión |
|---|---|---|
| B1–B8 | Ver v10.0 | — |
| B9 | Mes mostraba `—` | v10 |
| B10 | Semanas vacías | v10 |
| B11 | Meses solo Ene-Mar | v10 |
| B12 | Diciembre aparecía | v10 |
| B13 | Channel click abría drill de hoteles | v11 |
| B14 | Pills duplicadas — refactor a `udSyncBadges()` | v11 |
| B15 | `ud-f-region`/`ud-search` huérfanos | v11 |
| B16 | Columnas SP/Hybrid/TP ocultas | v11 |
| B17 | Texto combo gris | v11 |
| B18 | `max_avg_dest` UnboundLocalError | v11 |
| B19 | Pill dimensión activa en Channel view | v11 |
| B20 | Marriott/Paris duplicados en pills | v11 |
| B21 | `× Limpiar` visible sin filtros | v11 |
| B22 | RateFox marcado como Residual | v11 |
| B23 | `hGetDim()` con corp+channel retornaba vacío (Iberostar+DerbySoft) — fuente condicional | W23 |
| B24 | Acapulco no encontrado — límite `head(500)` excluía posición 564 → subido a 1000 | W23 |
| B25 | "SIN CONTRAT." mostraba tabla vacía — `gapSyncDim` two-pass con `visibleCount` | W23 |
| B26 | "SIN CONTRAT." mostraba destinos CON directo — faltaba `data-con-directo` en rows | W23 |
| B27 | `solo_propio`/`hybrid` mostraban `—` en filas destino — faltaban en `dest_grp` agg | W23 |
| B28 | GLOBAL row tenía `pp` en columna Total — orden de columnas corregido | W23 |
| B29 | Placeholder searchbox decía "hotel" — no hay dim hotel | W23 |
| B30 | `soloSinContrat` oculta destinos con `con_directo > 0` pero primeros 10 del DOM eran todos PP → two-pass fix | W23 |

---

## 📋 Pendientes

- [ ] Deploy a nueva plataforma de hosting
- [ ] Integrar con pipeline semanal PRICE
- [ ] Commit W23 a GitHub (`inventory/week-23/`)
- [ ] Validar pill dedup con múltiples selecciones simultáneas

---

## 🔑 Token y Commit GitHub

- **`text2.txt`** en el proyecto Claude — token GitHub PAT
- Path del repo: `federicochurches/Price` · branch `main`
- Outputs: `inventory/week-23/INVENTORY_W23.html` + `Analisis_Inventory_W23.xlsx`
- Commit message: `feat: Inventory W23 · Revamp visual chart · UI fixes · Jun 2026`

---

**Última actualización:** v13.0 · W23 · Junio 2026

**Cambios v13:**
- Masthead idéntico al Supply (shell padding-top, masthead-inner, border-bottom rule, logo 40px)
- Sección renombrada "Evolución Histórica"
- Chart revamp: Combo Violet `#5C469C` / Cyan `#4FC3F4` · área dinámica proporcional a PP ratio · sin puntos intermedios · punto final único · label dinámico Variación semanal/mensual/anual · ejes reforzados weight:700
- `dest_grp` incluye `solo_propio` + `hybrid` — filas destino muestran desglose real
- GLOBAL row orden corregido: Total | PP | Solo P. | Hybrid | Third P.
- Límite rows DOM subido a 1000 (dest_grp y dest_mkt)
- `gapSyncDim` two-pass con `visibleCount` — muestra primeros 10 que califican
- `data-con-directo` + `data-sin-directo` en gap-dest-row
- `hGetDim()` fuente condicional: HIST.dim si channel activo, HIST.dim_hotel si no
- Searchbox fallback por `data-dest-name` + delay dinámico
- B23–B30 cerrados
