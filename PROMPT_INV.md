# 🏨 PROMPT INV · Hotel Inventory · Supply Analytics HUB
**Versión v20 · Junio 2026 · calc_inv.py → INVENTORY_WNN.html + 3 JSONs externos + Analisis_Inventory_WNN.xlsx**

---

## 🧠 Rol y Contexto

Módulo **Hotel Inventory** del Supply Analytics HUB de PriceTravel.
Script principal: `calc_inv.py` → genera `INVENTORY_WNN.html` (~7.5MB) + 3 JSONs externos + `Analisis_Inventory_WNN.xlsx`.
Dataset: `dataHoteles_contratos.xlsx` (header=1, 571K+ rows)

---

## 📊 Universo y KPIs (W25)

| Métrica | Valor W25 |
|---|---|
| Sistema | 306.388 |
| Sin contrato | 821 — **excluidos siempre** |
| **Universo con contrato** | **305.567** |
| Producto Propio (SP+H) | 58.990 · 19.3% |
| Third Party | 246.577 · Target 2026 | 70.000 |
| Gap | 11.010 · Avance | 84.3% |
| Ritmo necesario | ~408 / sem |
| Independientes sin directo | 237.429 · Destinos | 11.574 |

**Variables Python canónicas:** `N` · `pp` · `solo_propio` · `hybrid` · `solo_terc` · `gap` · `SEMANAS_RESTANTES` · `ritmo_nec`

**Filtros de datos:**
- `header=1` en `pd.read_excel` (fila 0 es metadata)
- `TipoHotel != 'sincontrato'` → excluye sin contrato
- TipoHotel normalization (`TIPO_NORM`): `'solo tercero'→'sólo terceros'`, `'solo propio'→'sólo propio'`
- TipoHotel map (`TIPO_MAP`): `'sólo propio'→Solo Propio`, `'Propio_con_tercero'→Hybrid`, `'sólo terceros'→Third Party`

---

## 🏗️ Arquitectura HTML y Outputs (W25+)

### Config semanal
```python
WEEK          = "W26"
WEEK_NUM      = 26
VOL_NUM       = "26"
YEAR_ACTUAL   = 2026
SNAPSHOT_DATE = "29 de Junio de 2026"
INPUT_FILE    = "dataHoteles_contratos.xlsx"
OUTPUT_FILE   = f"INVENTORY_{WEEK}.html"
OUTPUT_DIR    = Path(f"week-{WEEK_NUM:02d}")
TARGET_PROPIO = 70_000
```

### Outputs (W25+) — 4 archivos por semana
| Archivo | Tamaño aprox | Contenido |
|---|---|---|
| `INVENTORY_WNN.html` | ~7.5MB | Reporte interactivo |
| `hotel_by_week_WNN.json` | ~0.5MB | Drill semanal YTD (solo SP+HY) |
| `hist_dim_WNN.json` | ~3.5MB | `dim_hotel_packed` + `dim_ch` + `dim_tipo` |
| `corp_dest_WNN.json` | ~1.1MB | Filtro corp×destino |
| `Analisis_Inventory_WNN.xlsx` | — | 5 hojas análisis |

**Todos se commitean juntos con `commit_inv.py`.**

---

## 🔑 Arquitectura JSON externos on-demand (W25+ · CANÓNICO)

### Reducción de tamaño conseguida
| Versión | HTML | Notas |
|---|---|---|
| Pre-W25 | 44MB | HOTEL_BY_WEEK inline |
| W25-hbw | 13MB | hotel_by_week externo |
| W25-histdim | 7.5MB | hist_dim + corp_dest + CH_DRILL_DATA eliminado |

### URLs de los JSONs (CANÓNICO — raw.githubusercontent.com)
```python
_HBW_JSON_URL      = f"https://raw.githubusercontent.com/federicochurches/Price/main/inventory/week-{WEEK_NUM:02d}/hotel_by_week_{WEEK}.json"
_HIST_DIM_JSON_URL = f"https://raw.githubusercontent.com/federicochurches/Price/main/inventory/week-{WEEK_NUM:02d}/hist_dim_{WEEK}.json"
_CORP_DEST_JSON_URL = f"https://raw.githubusercontent.com/federicochurches/Price/main/inventory/week-{WEEK_NUM:02d}/corp_dest_{WEEK}.json"
```
⚠️ **Netlify devuelve 403 en archivos `.json`** — siempre usar `raw.githubusercontent.com`.

### Loaders JS (patrón canónico)
Cada JSON tiene su loader `_load**(cb)`:
- `_loadHotelByWeek(cb)` — carga `hotel_by_week_WNN.json` al hacer drill semanal
- `_loadHistDim(cb)` — carga `hist_dim_WNN.json` al inicializar el gráfico histórico
- `_loadCorpDest(cb)` — carga `corp_dest_WNN.json` al activar filtro de destino

**Patrón:** si datos ya cargados → `cb()` inmediato. Si no → fetch + cola de callbacks + flag `_loading`.

### `_loadHistDim` — estructura del JSON
```json
{
  "dim_hotel_packed": { "W": [...], "M": [...], "R": [...], "T": [...], "data": [[...]] },
  "dim_ch":   [...],
  "dim_tipo": [...]
}
```
JS rehidrata `dim_hotel_packed` en `HIST.dim_hotel` al cargar.

### `hotel_by_week` — solo SP+HY
```python
hotel_by_week = {k: [r for r in v if r['t'] in ('SP','HY')]
                 for k, v in _hotel_by_week_raw.items()
                 if k.startswith(str(datetime.date.today().year))}
```
Solo hoteles Producto Propio, solo semanas del año actual.

### `CH_DRILL_DATA` — eliminado (código muerto)
Variable de 557KB que se definía pero nunca se usaba. Eliminada en W25.

---

## 🔗 Filtro cruzado dest→corp (W25 · CANÓNICO)

`CORP_DEST_DATA` se carga on-demand con `_loadCorpDest(cb)`.
En `hApplyFilter`: si hay `activeDests` y `CORP_DEST_DATA === null` → llama `_loadCorpDest` y re-ejecuta.
Normalización NFD en ambos lados del lookup para manejar acentos (México, Mérida, etc.).

---

## ⏳ Loading screen (W25+)

Blur semitransparente sobre el contenido real — el usuario ve la página esfumada detrás.
Logo + barra de progreso + texto "LOADING" fijo. Sin card blanca.
Se oculta con `window.load` (cuando el JS termina de ejecutarse).

```html
<div id="inv-loading" style="position:fixed;inset:0;backdrop-filter:blur(6px);background:rgba(248,244,236,0.55);...">
  <img src="{LOGO_B64}" ...>
  <div id="inv-loading-bar" ...></div>
  <div>LOADING</div>
</div>
```

**Pendiente W26:** separar JS a archivo externo con `defer` → el loader desaparecería en ~1s en lugar de ~10s.

---

## ⚠️ Regla de workflow para `calc_inv.py` (Opción B · CANÓNICO)

**`calc_inv.py` se corre siempre desde el clon local de Fede. Claude NO lo modifica en el repo directamente.**

Flujo correcto para cambios en `calc_inv.py`:
1. Claude entrega el archivo completo para descarga (o diff exacto)
2. Fede reemplaza su archivo local
3. Fede corre `python calc_inv.py` → genera HTML + JSONs
4. Fede corre `python commit_inv.py` → commitea todo al repo

**Flujo completo de Inventory:**
```powershell
cd C:\Users\federico.iglesias\Price\inventory
Remove-Item week-NN\INVENTORY_WNN.html   # IMPRESCINDIBLE
python calc_inv.py
python commit_inv.py
```

`commit_inv.py` detecta la semana automáticamente y sube los 4 archivos (HTML + 3 JSONs).

---

## 🃏 KPI Bar — 4 cards

**Card 1 — "Inventario de Hoteles"** (antes "Total Hotel Inventory"): muestra `N` hoteles con contrato activo.

**Card GAP (W26+ · DINÁMICA):** muestra los hoteles PP agregados esa semana, leídos en tiempo de generación desde `week_netnew.get(snapshot_yw, 0)` (mismo criterio que las barras del gráfico semanal). **Ya NO es hardcoded** — cierra el pendiente histórico de actualizarla a mano cada semana. El valor se imprime en consola al correr: `[KPI] Netnew 2026-WNN (card-gap): N hoteles PP...`.
La línea JS que sobreescribía `card-gap` con el gap *calculado* (target − pp) sigue comentada.
Color del valor: **`#4FC3F4` cyan**. Barra y label también en cyan.

---

## 💊 Pills de dimensión — orden canónico (W25+)

`CHANNEL | CORPORATIVO | REGIÓN | DESTINO`

nth-child JS: Channel=1, Corp=2, Región=3, Destino=4.
Región es la activa por defecto al cargar.

---

## 🏨 Masthead (W26+)

- **H1:** `<span color:var(--accent)>Inventario</span>` — sin el viejo "State of PriceTravel Product"
- **Subtitle eliminado:** ya no aparece la línea "N hoteles con contrato activo · Target 2026: …"
- **Título sección histórico:** "Evolución Histórica del Inventario". **Sin sufijo "· Producto Propio"** (W26): la dimensión default `pp` ya NO agrega sufijo. Solo `sp`/`hy` muestran "· Solo Propio"/"· Hybrid" en los drills. Fix en los dos builders del título: `_labels` (sin la key `pp`) + `suffix = (val && val !== 'Producto Propio')`.

---

## 🔀 Layout lado a lado · Navegador + Detalle (W26+ · CANÓNICO)

La Zona "Evolución Histórica del Inventario" usa un layout de **2 columnas** (`#ud-split`, flex):
- **Izquierda (47%) · Navegador de dimensiones** (`#ud-main-content`): tabla compacta **Región · Total · P. Propio · Third P. · % Propio**. Se ocultan por CSS las columnas Solo P. (`th-sp`/`td-sp`) y Hybrid (`th-hy`/`td-hy`); `vs Global` ya estaba oculta. Anchos explícitos (28/15/15/16/26%) para empacar las numéricas a la izquierda y dar aire limpio a %Propio (sin el overlap del bar que daba `table-layout:fixed` cuando la columna quedaba angosta).
- **Derecha (53%) · Detalle de hoteles** (`#ud-hotel-panel`): siempre visible, con **empty-state** (`:empty::before`) "Seleccioná una fila…" hasta que se clickea una región/corp/destino. Forzado `display:block!important` para que el empty-state se vea aunque el render lo deje en `display:none`.

**Implementación (CANÓNICO):**
- La estructura `#ud-split` (con `<div class="layoutC-col">` izq/der + `.layoutC-colhead` "Dimensiones"/"Detalle de Hoteles") se **emite directo** en el f-string de `build_html` (no se arma por JS). `#ud-gap-content`/`#ud-ch-content` quedan **fuera** del split (vistas alternativas).
- CSS y JS viven en **`LAYOUTC_CSS`** y **`LAYOUTC_JS`** (strings planos, NO f-string, definidos antes de `build_html`; insertados vía `{LAYOUTC_CSS}` en `<style>` y `{LAYOUTC_JS}` antes de `</body>`). Mantenerlos planos evita el escapado de llaves.
- **Alineación de headers** (`LAYOUTC_JS`): el header de la tabla de hoteles arranca más abajo (meta-línea + searchbox arriba). Un JS mide el offset del `#hw-thead` derecho y aplica ese `margin-top` a `#ud-main-content` para que los renglones de nombres de columna queden en la misma línea. Se re-alinea con `MutationObserver` sobre `#ud-hotel-panel` (cambio de selección) y en `resize`. En `<1000px` (apilado) no aplica offset.
- **Badge de tipo** (`_renderHotelList` + `_renderPPPanel`): la columna TIPO se ensancha a 20% (Hotel 30→27%) + `white-space:nowrap` para que "Solo Propio"/"Third Party" no se partan en 2 líneas.
- **Searchbox** del panel de hoteles: ancho completo (`flex:1 0 100%`) en su propia línea, debajo de la meta-línea (antes quedaba a la derecha con `margin-left:auto` y se apretaba en la columna angosta).
- **Responsive:** `#ud-split` colapsa a columna en `<1000px`.

⚠️ Cualquier cambio de columnas/anchos del navegador o del badge se aplica en `LAYOUTC_CSS`; el badge nowrap aplica a **ambas** funciones de render vía el scope `#ud-hotel-panel`.

---

## 📋 Tabla de Detalle de Hoteles (W26+) — CANÓNICO

Aplica a ambas funciones JS: `_renderHotelList` (drill semanal) y `_renderPPPanel` (panel PP).

### Columnas y orden
`Hotel · Corporativo · Región · Destino · Tipo`

El `#` de numeración va **inline dentro de la celda Hotel** como `<span class="hw-n">` — sin columna separada.

### Sort
Todos los headers tienen `onclick="_hwSortBy(col, this)"`. La función `_hwSortBy` es global (definida una sola vez antes de `_renderHotelList`) y:
- Lee `data-h`, `data-c`, `data-r`, `data-d`, `data-t` de cada `tr[data-hw]`
- Ordena y reordena filas en el tbody
- Renumera automáticamente el `.hw-n` de cada fila
- Actualiza el indicador `↑`/`↓`/`↕` en el `#hw-thead`

### Badge de Tipo
Pill con dot de color + label. Colores:
- Solo Propio: bg `#E0F7FE` · color `#0277A8` · dot `#0277A8`
- Hybrid: bg `#EDE8F7` · color `#5C469C` · dot `#5C469C`
- Third Party: bg `#F0EBE2` · color `#8A8377` · dot `#8A8377`

### `table-layout: fixed` · anchos de columna
`30% · 18% · 13% · 22% · 17%`

### Empty state (W26+)
Si `filtered.length === 0` tras aplicar todos los filtros, `_renderHotelList` muestra:
> "Sin hoteles Producto Propio en W{N} · {AÑO} para esta selección."
y retorna sin renderizar tabla. Ejemplo: corporativo con 0 hoteles nuevos en esa semana.

---

## 🔍 Diagnóstico "Sin Clasificar" (W26+)

Al correr `calc_inv.py`, imprime en consola cuántos hoteles tienen destino sin clasificar (nan, vacío, o variantes de "sin clasificar") y en qué regiones. Útil para detectar datos sucios antes de commitear.

```
[DIAG] Hoteles con destino sin clasificar: N · Regiones: ...
```

---

## 🔢 Sort en tablas Corp y Destino (W26+)

Las tablas de la Zona 4 (Corporativo y Destino) tienen headers clickeables con `↕`/`↑`/`↓`:
- **Corp:** `corpSortCol(key, th)` + `corpSortTotal()` — ordena por nombre, Solo Propio, Hybrid, Third Party o Total
- **Dest:** `destSortCol(key, th)` + `destSortTotal()` — ordena por nombre, P. Propio, Third Party o Total
- Ambas renumeran automáticamente el orden visual tras el sort

---

## 💻 Ejecución local

```powershell
cd C:\Users\federico.iglesias\Price\inventory
Remove-Item week-NN\INVENTORY_WNN.html
python calc_inv.py
python commit_inv.py
```

`commit_inv.py` sube automáticamente:
- `inventory/week-NN/INVENTORY_WNN.html`
- `inventory/week-NN/hotel_by_week_WNN.json`
- `inventory/week-NN/hist_dim_WNN.json`
- `inventory/week-NN/corp_dest_WNN.json`

---

## 🐛 Bugs cerrados

| Bug | Descripción | Semana |
|---|---|---|
| HTML 44MB | HOTEL_BY_WEEK inline → JSON externo on-demand | W25-hbw |
| Filtro región México (idx<10) | `hApplyFilter` ocultaba destinos idx≥48 | W25-inv-filter |
| NFD acentos México/Mérida | normalize('NFD') en lookup corp×dest | W25-inv-filter |
| Tabla hoteles columnas viejas | # separado, Región/Destino/Corp desordenado, sin sort, tipo como texto coloreado | W26-inv-ui |
| Sort tablas Corp y Dest | Headers sin sort | W26-inv-ui |
| Masthead subtítulo | "N hoteles · Target 2026" eliminado | W26-inv-ui |
| Card Gap gris | 44 en gris `#6A6A6A` → cyan `#4FC3F4` | W26-inv-ui |
| CH_DRILL_DATA 557KB | Código muerto eliminado | W25-perf |
| dim_ch + dim_tipo inline | Movidos a hist_dim JSON externo | W25-perf |
| Loading screen opaco | Reemplazado por blur semitransparente | W25-perf |
| onclick SyntaxError `_hwSortBy` | `onclick="_hwSortBy('h',this)"` dentro de string JS rompía el script → cambiado a `this.dataset.col` | W26-inv-ui |
| JSONs 403 Netlify | Netlify bloquea `.json` → URLs migradas a `raw.githubusercontent.com` | W26-inv-ui |
| `drDestsNorm` faltaba en `udRowClick` | Al clickear filtro con semana activa, `_renderHotelList` recibía solo 7 args → destino nunca filtraba | W26-inv-bugs |
| Panel hoteles con 0 hoteles | Corporativo con total=0 mostraba todos los hoteles de la semana → empty state | W26-inv-bugs |
| `FileNotFoundError` JSONs semana nueva | `OUTPUT_DIR.mkdir` estaba en L4819 (al escribir HTML) pero los 3 JSONs se escriben antes → carpeta `week-NN/` nueva no existía. Fix: `mkdir(parents=True, exist_ok=True)` ANTES de la 1ª escritura de JSON. Latente desde W22 (carpetas previas ya existían) | W26-layout |
| card-gap hardcoded | `44` fijo → dinámico `week_netnew.get(snapshot_yw,0)` | W26-layout |
| Título "· Producto Propio" | sufijo redundante en la dimensión default → removido (solo sp/hy muestran sufijo) | W26-layout |
| Bar %Propio montado sobre Hybrid | navegador compacto con `table-layout:fixed` daba %Propio ~85px y el bar (94px) se desbordaba a la izquierda → anchos explícitos % | W26-layout |
| Badge "Solo Propio" en 2 líneas | columna TIPO angosta en layout lado a lado → TIPO 20% + `white-space:nowrap` | W26-layout |
| Searchbox apretado a la derecha | `margin-left:auto;width:260px` en columna angosta → `flex:1 0 100%` (ancho completo, línea propia) | W26-layout |
| Headers de tablas desalineados | meta+search empujaban el header de hoteles → JS mide offset y aplica `margin-top` a `#ud-main-content` | W26-layout |

---


---

## 🗺 Mapeo de Destinos Sin Clasificar (`dest_mapping.py`) -- W26+

### Problema
~2.823 hoteles en el dataset tienen `Destino = NaN/SinClasificar`. El modulo de inventario los excluye del breakdown dimensional.

### Solucion canonica
`dest_mapping.py` en `inventory/` -- diccionario `Hotel -> Destino` que se aplica automaticamente al cargar el dataset.
**Solo pisa hoteles sin destino valido** -- si el dataset nuevo ya trae un destino correcto, no lo toca.

### Estado W26
| Fuente | Hoteles |
|---|---|
| Auto-mapper (keyword en nombre) | ~932 |
| Revision manual (Fede) | ~406 |
| **Total mapeados** | **~1.338** |
| Sin mapear (nombres genericos) | ~1.485 |

### Workflow para completar el mapeo
```powershell
cd C:\Users\federico.iglesias\Price\inventory
py extract_sinclasificar.py extract   # genera hoteles_sinclasificar.xlsx
# Completar columna Destino_sugerido en el Excel
py extract_sinclasificar.py build     # convierte Excel -> dest_mapping.py
py calc_inv.py
py commit_inv.py
```

### Archivos
- `inventory/dest_mapping.py` -- diccionario persistente, commitear al repo tras cada update
- `inventory/extract_sinclasificar.py` -- extrae sin clasificar + convierte Excel -> dict

### Regla critica
`dest_mapping.py` **NO pisa destinos ya validos en el dataset** -- si W27 trae el destino correcto para un hotel, se respeta.

---

## 📋 Pendientes

- [ ] W27: separar JS a archivo externo con `defer` → loading <1s
- [x] ~~W26: actualizar valor hardcoded GAP~~ → card-gap dinámica (W26-layout)
- [x] ~~W26: actualizar CONFIG semanal~~ → WEEK=W26, SNAPSHOT_DATE=29-Jun (W26-layout)
- [ ] Investigar bug de deselección de filtros (comportamiento no documentado aún)
- [ ] Layout lado a lado en modos GAP/Channel: cuando se activa "Sin Contrat." o un channel, `#ud-main-content` se oculta y el split queda con la columna izq vacía (no validado — modos secundarios)

---

**Última actualización:** v20 · W26-layout · 29-06-2026
**Cambios v20 (W26-layout):** CONFIG → W26 (snapshot 29-Jun) · **card-gap dinámica** (`week_netnew[snapshot_yw]`) + print `[KPI] Netnew` · **fix `mkdir` carpeta nueva** (JSONs fallaban en semana nueva) · **título histórico sin "· Producto Propio"** · **Layout lado a lado** (navegador compacto Región·Total·P.Propio·Third P.·%Propio izq + detalle hoteles der, `LAYOUTC_CSS`/`LAYOUTC_JS`, alineación de headers por JS, empty-state, badge nowrap + TIPO 20%, searchbox full-width). Validado sobre HTML real W26 vía patch antes de portar al generador.
**Cambios v19.2:** URLs JSONs → `raw.githubusercontent.com` (Netlify devuelve 403 en .json) · Bug `drDestsNorm` faltaba como 8° arg en `udRowClick` (week+region+dest no filtraba hoteles) · Empty state `_renderHotelList` cuando `filtered.length === 0` (Opción A — panel muestra mensaje en lugar de todos los hoteles)
**Cambios v19.1 (sesión anterior):** onclick `_hwSortBy` sin args string (evita SyntaxError JS) · URLs JSONs a raw.githubusercontent.com
**Cambios v19:** Masthead H1 → "Inventario" · subtitle eliminado · "Evolución Histórica del Inventario" · card Gap cyan · "Inventario de Hoteles" · tabla detalle hoteles rediseñada (# inline, Hotel|Corp|Región|Destino|Tipo, badge tipo, sort 5 cols, `_hwSortBy` global) · sort tablas Corp+Dest · diagnóstico `[DIAG]`
