# 🏨 PROMPT INV · Hotel Inventory · Supply Analytics HUB
**Versión v15.0 · Junio 2026 · calc_inv.py → INVENTORY_WNN.html + Analisis_Inventory_WNN.xlsx**

---

## 🧠 Rol y Contexto

Módulo **Hotel Inventory** del Supply Analytics HUB de PriceTravel.
Script principal: `calc_inv.py` → genera `INVENTORY_WNN.html` (~5MB) + `Analisis_Inventory_WNN.xlsx`.
Dataset: `dataHoteles_contratos.xlsx` (header=1, 571K+ rows)

---

## 📊 Universo y KPIs

| Métrica | Valor W23 |
|---|---|
| Sistema | 318.005 |
| Sin contrato | 837 — **excluidos siempre** |
| **Universo con contrato** | **317.168** |
| Producto Propio (SP+H) | 58.966 · 18.6% |
| Solo Propio | 4.794 · Hybrid | 54.172 |
| Third Party | 258.202 · Target 2026 | 70.000 |
| Gap | 11.034 · Avance | 84.2% |
| Ritmo necesario | ~380 / sem |
| Independientes sin directo | 248.290 · Destinos | 11.672 |

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
3. **Evolución Histórica del Producto** — gráfico Chart.js (sección renombrada desde W23)
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

## 📈 Evolución Histórica del Producto (W23+, antes "Crecimiento Histórico")

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

### Drill por semana → tabla de distribución (W23 — NUEVO)

Click en una barra de semana del gráfico histórico reescribe la **tabla de distribución** con los hoteles nuevos de esa semana.

**Funciones (en `calc_inv.py`, scope global, script final):**
| Función | Rol |
|---|---|
| `hDrillWeek(yw)` | Entry point. Si ya hay drill en esa semana → reset. Filtra `dim_hotel` por `(r.w\|\|r.yw)===yw`, agrupa por `udDim` activa |
| `_snapTbody()` | Guarda `ud-tbody.innerHTML` original en `window._tbodyOrig` antes del primer drill |
| `_renderDrillTable(rows, label, dim)` | Reescribe `ud-tbody`. keyMap `{reg:'r', corp:'c', dest:'d'}`. Columnas: Total/PP/SP/HY/TP + %barra cyan |
| `_renderDrillPill(label)` | Pone pill "Nuevos WNN ×" en `hf-active-pills`. Click en × → `hDrillWeekReset()` |
| `hDrillWeekReset()` | Restaura `_tbodyOrig`, limpia `_drillYw`, quita pill |

**onClick del chart:** `onClickFn = (evt,els)=>{...hDrillWeek(row.yw)}` en la rama semanal de `hRender`.
El `onClick` del chart usa `if (evt.native) evt.native.stopPropagation()` (Chart.js no pasa evento DOM nativo).

**Soporte modo GAP (SIN CONTRAT):** `_gapMode()` detecta si `ud-gap-content` está visible. `_drillTbody()` devuelve `gap-tbody` o `ud-tbody` según el modo. En GAP las columnas son Sin Directo (=Third Party) / Con Directo (=Prod Propio). `hDrillWeekReset()` restaura `_tbodyOrig` o `_gapTbodyOrig` según corresponda.

**Recuperado de:** `INVENTORY_W22_FINAL_1.html` — el drill nunca estuvo en `calc_inv.py` de W22fix (rama sem dejaba `onClickFn=null`). Portado a keys compactas en W23.

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
| B31 | `HIST.dim` sin campo `dest` — groupby no incluía `Destino` | W22-fix |
| B32 | `hGetDim()` no filtraba por `dest` en rama channel activo | W22-fix |
| B33 | Hoteles sin `FechaCreación` no aparecen en `HIST.dim` → gráfico vacío aunque existan | W22-fix |
| B34 | `hGetCurrentTotal()` usaba `HIST.dim` último snapshot → devolvía 0 para hoteles sin historia | W22-fix |
| B35 | `apply_tipo_override` definida después de su primer uso → NameError silencioso | W22-fix |
| B36 | Columna `Expedia` (propio) no estaba en `ALL_CHANNELS` → hoteles ignorados en snapshot | W22-fix |
| B37 | Línea histórica plana con filtro de tipo — `sparseMap[r.yw]` daba undefined (dim compacto usa key `w`) → fix `r.w||r.yw` | W23 |
| B38 | Acum filtrado arrancaba en 0 con PROD. PROPIO — `before` vacío y `totalInSubset-inRange=0` → `HIST.actual_by_tipo` como base | W23 |
| B39 | `evt.stopPropagation is not a function` — Chart.js pasa su propio evento → fix `evt.native.stopPropagation()` | W23 |
| B40 | `activeRegions`/`activeTipo` not defined en `hRender` — vars solo existían en `hGetDim` → redefinir local con `_activeR/_activeC/_activeCh/_activeTipo` | W23 |
| B41 | Drill por semana no actualizaba tabla de distribución — nunca existió en W22fix ni HTML W22 (rama sem dejaba `onClickFn=null`); recuperado de `INVENTORY_W22_FINAL_1.html` y portado a keys compactas | W23 |
| B42 | `dim_hotel` sin destino — drill por destino imposible → agregado `d` (Destino) al groupby y compact | W23 |
| B43 | Tabla GAP destacaba Con Directo en cyan — debía ser Sin Directo (el gap) → swap th-pp/td-pp | W23 |
| B44 | Pill PROD. PROPIO no se veía activa al cargar / color violeta → `--pill-on-bg:#E1F5EE` verde + activación en `_tryInit` | W23 |
| B45 | HTML 43MB → 12.4MB — `dim_ch` filtrado a 2 años, snapshot eliminado, índices compactos | W23 |
| B46 | Pills activas mezcladas/desalineadas — todas las pills seleccionadas van en una fila, color verde uniforme (`#E1F5EE`/`#1A6B4A`); botón de menú mantiene color de categoría | W23 |
| B47 | Pill del drill (`_renderDrillPill`) salía violeta → cambiada a verde como las demás pills activas | W23 |
| B48 | Drill no actualizaba tabla en SIN CONTRAT — escribía en `ud-tbody` (oculto en modo GAP) → `_gapMode()`/`_drillTbody()` detectan modo y escriben en `gap-tbody` con columnas Sin Directo/Con Directo | W23 |
| B49 | Columna VS GLOBAL visible — faltaba clase `td-vs` en: header/celda GAP, fila GLOBAL de tabla principal, y celdas del drill (normal + GAP). Regla: TODA celda de la última columna debe llevar `td-vs` (el CSS `display:none` ya existe) | W23 |
| B50/P6 | Channel View Third Party — agregada columna `% Gap` junto a Hoteles (% de hoteles solo-terceros vs total inventario), con barra cyan; ambas columnas % Gap mismo formato | W23 |
| B51 | Sort Destino/Corp con filtro activo ignoraba el filtro | W23-inv-bugs |
| B52 | Orden pills dimensión incorrecto (Región→Corp→Dest→Channel) | W23-inv-bugs |
| B53 | Pill corp persiste al limpiar / card PP muestra valor incorrecto | W23-inv-bugs |
| B54 | Gráfico channel mostraba acumulado histórico en lugar de total real | W23-inv-bugs |
| B55 | Pico artificial en gráfico al filtrar región/corp | W23-inv-bugs |
| B56 | "Ver 10 más" aparecía dentro de la lista con filtro activo | W23-inv-bugs |
| B57 | Third Party no clickeable en Channel View JS | W23-inv-bugs |
| B58 | Hotel Unico V2 sin datos en gráfico — mismatch nombre tabla↔dim_ch | W23-inv-bugs |
| B59 | RateFox sin datos en gráfico — no estaba en CHANNELS_TERCERO | W23-inv-bugs |
| B60–B62 | Third Party sin destinos / % Gap vacío / Avg Dest vacío al cambiar pill | W23-inv-bugs |
| B63 | Tabla Channel no sincroniza con pill PP/SP/HY — CH_DATA["pp"] faltaba | W23-inv-bugs |
| B64 | Card PP muestra valor filtrado tras limpiar — updateCards no llamado | W23-inv-bugs |

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
- Outputs: `inventory/week-NN/INVENTORY_WNN.html` + `Analisis_Inventory_WNN.xlsx`
- Commit message: `feat: Inventory WNN · descripción · DD-MM-YYYY`

## 💻 Ejecución local desde PowerShell

**Método recomendado (W24+): `run_inv.py`** — wrapper que valida entorno, versión del script,
tamaño del HTML, y commitea por Git Tree API (no GitHub Desktop). Resuelve todos los puntos
de fricción de W23.

```powershell
cd C:\Users\federico.iglesias\Price\inventory
# 1. Editar CONFIG en calc_inv.py (WEEK, WEEK_NUM, VOL_NUM, SNAPSHOT_DATE, INPUT_FILE)
# 2. Copiar el nuevo dataset de contratos a esta carpeta
python run_inv.py            # corre + verifica (NO commitea — default seguro)
python run_inv.py --commit   # corre + verifica + commitea HTML por Git Tree API
```

`run_inv.py` hace 6 pasos verificados:
1. Valida CWD (falla si estás en la carpeta equivocada), dataset de input, token
2. Verifica que calc_inv.py tenga los 4 fixes canónicos (VS GLOBAL, % Gap, _ppRatio, optimización) — evita correr versión vieja
3. Borra el HTML viejo (calc_inv.py no regenera si existe)
4. Corre calc_inv.py
5. Verifica tamaño del HTML (alerta >15MB, error >25MB) + sin celdas VS GLOBAL sueltas
6. Commit por Git Tree API + verifica tamaño en el repo (lo que Netlify sirve)

**Método manual (alternativa):**
```powershell
cd C:\Users\federico.iglesias\Price\inventory
Remove-Item week-NN\INVENTORY_WNN.html   # IMPRESCINDIBLE: no regenera si existe
python calc_inv.py
# Commit del HTML: SIEMPRE por Git Tree API, NUNCA GitHub Desktop (ver abajo)
```

**Config semanal en `calc_inv.py`:**
```python
WEEK          = "W23"
WEEK_NUM      = 23
VOL_NUM       = "23"
SNAPSHOT_DATE = "9 de Junio de 2026"
INPUT_FILE    = "dataHoteles_contratos.xlsx"
```

### ⚠️ GitHub Desktop falla con archivos grandes (aprendizaje W23)
- GitHub Desktop **falla silenciosamente** al pushear el `INVENTORY_WNN.html` (~12MB): el commit
  aparece en el historial pero sube la versión vieja o un puntero vacío. En W23 el repo quedó
  sirviendo el HTML de 44MB sin optimizar pese a que el commit "existía".
- **Solución:** commitear el HTML grande SIEMPRE por Git Tree API (`run_inv.py --commit` lo hace solo).
- Síntoma a vigilar: loading page lenta en Netlify → verificar tamaño real en el repo:
  `curl -sI https://raw.githubusercontent.com/federicochurches/Price/main/inventory/week-NN/INVENTORY_WNN.html | grep content-length`
  (debe dar ~12-13MB, no ~44MB).

## 🎨 Decisiones visuales (W22+)

- **Rojo:** `#FF3B30` — reemplaza `#C0392B` en todo el HTML
- **Loading screen:** overlay cyan `#4FC3F4` — mismo patrón Supply
- **Footer:** botón "← Volver al Hub" — `href="../../index.html"`
- **OUTPUT_DIR:** `Path(f"week-{WEEK_NUM:02d}")` — outputs en subcarpeta automática

---

**Última actualización:** v15.1 · W23 · 11 Jun 2026

**Cambios v13:**
- Masthead idéntico al Supply (shell padding-top, masthead-inner, border-bottom rule, logo 40px)
- Sección renombrada "Evolución Histórica del Producto"
- Chart revamp: Combo Violet `#5C469C` / Cyan `#4FC3F4` · área dinámica proporcional a PP ratio · sin puntos intermedios · punto final único · label dinámico Variación semanal/mensual/anual · ejes reforzados weight:700
- `dest_grp` incluye `solo_propio` + `hybrid` — filas destino muestran desglose real
- GLOBAL row orden corregido: Total | PP | Solo P. | Hybrid | Third P.
- Límite rows DOM subido a 1000 (dest_grp y dest_mkt)
- `gapSyncDim` two-pass con `visibleCount` — muestra primeros 10 que califican
- `data-con-directo` + `data-sin-directo` en gap-dest-row
- `hGetDim()` fuente condicional: HIST.dim si channel activo, HIST.dim_hotel si no
- Searchbox fallback por `data-dest-name` + delay dinámico
- B23–B30 cerrados

**Cambios v15 (W23):**
- **Optimización de tamaño 43MB → 12.4MB**: snapshot eliminado, índices compactos (`dim_ch`/`dim_tipo`/`dim_hotel`) con keys cortas, `dim_ch` filtrado a 2 años
- **Drill por semana → tabla de distribución** (NUEVO, recuperado de W22_FINAL y portado): `hDrillWeek` + `_snapTbody`/`_renderDrillTable`/`_renderDrillPill`/`hDrillWeekReset`
- `dim_hotel` ahora incluye destino (`d`) — habilita drill por destino
- `HIST.actual_by_tipo` — base real del acum para filtro solo-tipo (línea no plana)
- Fix `sparseMap` con `r.w||r.yw` (keys compactas)
- Fix `evt.native.stopPropagation()` para Chart.js
- Pill PROD. PROPIO verde (`#E1F5EE`/`#1A6B4A`) + activación en `_tryInit`
- Tabla GAP: destacar Sin Directo en cyan (era Con Directo)
- Pills activas en una fila, verde uniforme; drill-pill verde; botón menú mantiene color categoría
- Drill funciona en modo SIN CONTRAT (`_gapMode`/`_drillTbody`, escribe en `gap-tbody`)
- Columna VS GLOBAL eliminada también en tabla GAP (`th-vs`/`td-vs`)
- `_ppRatio` dinámico (`{pp}/{N}`) — limpieza para W24
- B37–B49 cerrados


## Decisiones UI (W22 final)
- Pills contratación: solo **PROD. PROPIO** y **SIN CONTRAT.** — Solo Propio y Hybrid eliminadas (detalle visible en columnas de tabla)
- Tooltip gráfico histórico: fondo `rgba(253,252,249,0.92)` (beige tenue), texto `#333132`, sin color boxes
- VS GLOBAL: columna eliminada permanentemente — `th-vs, td-vs { display:none!important }`
- col-show CSS: solo resaltado del header con `rgba(79,195,244,.12)` — no oculta columnas
- Default al cargar: PROD. PROPIO activo (`hFTipo = 'Prod. Propio'` en `_tryInit`) + agregado a `udActiveFilters` + `hRenderActivePills()` para mostrar el chip verde
- **Pills activas (W23)**: todas en una sola fila (`hf-active-pills`), color verde uniforme (`border #1A6B4A`, `bg #E1F5EE`). Los botones del menú mantienen su color de categoría (contratación violeta `#EDE8F7`). La pill del drill también es verde.
- Git Tree API obligatorio para HTML > 1MB

## 🏢 Reglas de negocio — Clasificación corp+channel

`CORP_CHANNEL_TIPO_OVERRIDE` en `calc_inv.py` — lugar canónico para overrides:
```python
CORP_CHANNEL_TIPO_OVERRIDE = {
    ('Marriott', 'Expedia'): 'Hybrid',  # Marriott+Expedia = Producto Propio
}
```
Aplica sobre `dim_ch`, `dim_tipo` y `dim_hotel`. Agregar aquí cualquier nueva excepción.

## ⚠️ Arquitectura de optimización de tamaño (W23 — CANÓNICO)

El `HIST.snapshot` original (región×corp×dest×tipo×channel×semana, ~80K rows → HTML 40-43MB) fue **eliminado**.
Reemplazado por 3 índices compactos con keys cortas:

| Índice | Keys compactas | Agrupación | Uso |
|---|---|---|---|
| `dim_ch` | `w,m,t,ch,n` | yw×ym×ch_tipo×channel (sin región/corp) | filtro channel — filtrado a últimos 2 años |
| `dim_tipo` | `w,m,t,n` | yw×ym×ch_tipo | filtro solo-tipo (sin región/corp) |
| `dim_hotel` | `w,m,r,c,d,t,n` | yw×ym×region×corp×dest×ch_tipo | filtro región/corp/dest + **drill por semana** |

Donde: `w`=yw, `m`=ym, `r`=region, `c`=corp, `d`=dest, `t`=ch_tipo, `ch`=channel, `n`=count.

**Tamaño resultante:** ~12.4MB (con destino en dim_hotel) — vs 40-43MB del snapshot. Sigue requiriendo GitHub Desktop (>1MB).

**Regla crítica:** el JS lee keys compactas. Siempre usar `r.w||r.yw` (nunca solo `r.yw`) al construir `sparseMap` o agregar — el dim compacto usa `w`, no `yw`. Olvidar esto produce línea histórica plana (sparseMap vacío).

## Pendientes próxima sesión
- P7: Columnas tabla — resaltar header columna activa según pill (parcialmente resuelto)
- Hotel Unico V2 sin datos en gráfico histórico
- Validar Marriott+Expedia en destino donde sí exista esa combinación en el dataset
- Optimizar HIST.snapshot para reducir tamaño del HTML
