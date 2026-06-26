# 🏨 PROMPT INV · Hotel Inventory · Supply Analytics HUB
**Versión v18.0 · Junio 2026 · calc_inv.py → INVENTORY_WNN.html + 3 JSONs externos + Analisis_Inventory_WNN.xlsx**

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
WEEK          = "W25"
WEEK_NUM      = 25
VOL_NUM       = "25"
YEAR_ACTUAL   = 2026
SNAPSHOT_DATE = "16 de Junio de 2026"
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

### URLs de los JSONs
```python
_HBW_JSON_URL      = f"https://analytics-desk.netlify.app/inventory/week-{WEEK_NUM:02d}/hotel_by_week_{WEEK}.json"
_HIST_DIM_JSON_URL = f"https://analytics-desk.netlify.app/inventory/week-{WEEK_NUM:02d}/hist_dim_{WEEK}.json"
_CORP_DEST_JSON_URL = f"https://analytics-desk.netlify.app/inventory/week-{WEEK_NUM:02d}/corp_dest_{WEEK}.json"
```

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

**Card GAP (W25+):** muestra hoteles agregados esa semana (valor hardcoded en `calc_inv.py`), NO el gap calculado.
La línea JS que sobreescribía `card-gap` con el gap calculado está comentada.

---

## 💊 Pills de dimensión — orden canónico (W25+)

`CHANNEL | CORPORATIVO | REGIÓN | DESTINO`

nth-child JS: Channel=1, Corp=2, Región=3, Destino=4.
Región es la activa por defecto al cargar.

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
| CORP_DEST_DATA no emitido | Variable JS referenciada pero no generada | W25-inv-corp-dest |
| CH_DRILL_DATA 557KB | Código muerto eliminado | W25-perf |
| dim_ch + dim_tipo inline | Movidos a hist_dim JSON externo | W25-perf |
| Loading screen opaco | Reemplazado por blur semitransparente | W25-perf |

---

## 📋 Pendientes

- [ ] W26: separar JS a archivo externo con `defer` → loading <1s
- [ ] W26: actualizar valor hardcoded GAP (44) con hoteles reales de W26
- [ ] W26: actualizar CONFIG semanal (WEEK=W26, SNAPSHOT_DATE, etc.)

---

**Última actualización:** v18.0 · W25-perf · 26-06-2026
**Cambios v18:** CH_DRILL_DATA eliminado (−557KB) · dim_ch+dim_tipo → hist_dim externo · hotel_by_week solo SP+HY · loading blur semitransparente · pills orden CHANNEL|CORP|REG|DEST · card GAP = hoteles semana · Opción B documentada · commit_inv.py con 4 archivos
