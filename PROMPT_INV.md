# 🏨 PROMPT INV · Hotel Inventory · Supply Analytics HUB
**Versión v17.0 · Junio 2026 · calc_inv.py → INVENTORY_WNN.html + hotel_by_week_WNN.json + Analisis_Inventory_WNN.xlsx**

---

## 🧠 Rol y Contexto

Módulo **Hotel Inventory** del Supply Analytics HUB de PriceTravel.
Script principal: `calc_inv.py` → genera `INVENTORY_WNN.html` (~13MB) + `hotel_by_week_WNN.json` (~6.3MB) + `Analisis_Inventory_WNN.xlsx`.
Dataset: `dataHoteles_contratos.xlsx` (header=1, 571K+ rows)

---

## 📊 Universo y KPIs

| Métrica | Valor W23 |
|---|---|
| Sistema | 309.052 |
| Sin contrato | 820 — **excluidos siempre** |
| **Universo con contrato** | **308.232** |
| Producto Propio (SP+H) | 58.888 · 19.1% |
| Solo Propio | 5.078 · Hybrid | 53.810 |
| Third Party | 249.344 · Target 2026 | 70.000 |
| Gap | 11.112 · Avance | 84.1% |
| Ritmo necesario | ~383 / sem |
| Independientes sin directo | 240.119 · Destinos | 11.636 |

**Variables Python canónicas:** `N` · `pp` · `solo_propio` · `hybrid` · `solo_terc` · `gap` · `SEMANAS_RESTANTES` · `ritmo_nec`

**Filtros de datos:**
- `header=1` en `pd.read_excel` (fila 0 es metadata)
- `TipoHotel != 'sincontrato'` → excluye sin contrato
- TipoHotel normalization (`TIPO_NORM`): `'solo tercero'→'sólo terceros'`, `'solo propio'→'sólo propio'`
- TipoHotel map (`TIPO_MAP`): `'sólo propio'→Solo Propio`, `'Propio_con_tercero'→Hybrid`, `'sólo terceros'→Third Party`
- `df_tp = df[TipoHotel=='sólo terceros']` · `df_pp = df[TipoHotel.isin(['sólo propio','Propio_con_tercero'])]`

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

### Outputs (W25+)
1. `INVENTORY_WNN.html` — reporte interactivo **~13MB** (reducido de 44MB, ver sección HOTEL_BY_WEEK)
2. `hotel_by_week_WNN.json` — datos de drill semanal YTD, **~6.3MB**, cargado on-demand via fetch
3. `Analisis_Inventory_WNN.xlsx` — 5 hojas: Resumen · Por Región · Por Corporativo · Por Destino · Por Channel

### Estructura de secciones HTML
1. **Masthead** — estructura idéntica a Supply PRICE
2. **KPI Bar** — 4 cards en grid
3. **Evolución Histórica del Producto** — gráfico Chart.js
4. **Distribución y Exploración** — tabla unificada con pills integradas
5. **Sin Contratación Directa (GAP)** — tabla separada activada por pill
6. **Channel View** — vista por canal de conectividad
7. **Footer** — botón descarga Excel

---

## 🔑 Arquitectura HOTEL_BY_WEEK on-demand (W25 · CANÓNICO)

### Problema resuelto
`HOTEL_BY_WEEK` era un dict inline en el HTML (803 semanas × 305K registros → **44MB**).
Imposible de commitear por Git Tree API y lento de cargar.

### Solución implementada
**JSON externo** cargado async por fetch. El HTML emite el loader JS; el JSON se sirve desde raw.githubusercontent.com.

**En `calc_inv.py`:**
```python
# 1. Filtrar solo semanas YTD (año actual)
hotel_by_week_ytd = {k: v for k, v in raw.items() if k.startswith(str(datetime.date.today().year))}

# 2. Exportar como JSON separado
import json as _json_hbw, os as _os_hbw
json_path = OUTPUT_DIR / f"hotel_by_week_{WEEK}.json"
with open(json_path, 'w', encoding='utf-8') as _f:
    _json_hbw.dump(hotel_by_week_ytd, _f, ensure_ascii=False)

# 3. En el HTML emitir loader en vez de datos inline
_HBW_JSON_URL = f"https://raw.githubusercontent.com/federicochurches/Price/main/inventory/week-{WEEK_NUM:02d}/hotel_by_week_{WEEK}.json"
```

**JS emitido en el HTML:**
```js
const HOTEL_BY_WEEK_URL = '{_HBW_JSON_URL}';
let HOTEL_BY_WEEK = null;
let _hbwCallbacks = [];
function _loadHotelByWeek(cb) {
  if (HOTEL_BY_WEEK) { cb(HOTEL_BY_WEEK); return; }
  _hbwCallbacks.push(cb);
  if (_hbwCallbacks.length > 1) return;
  fetch(HOTEL_BY_WEEK_URL).then(r=>r.json()).then(data=>{
    HOTEL_BY_WEEK = data;
    _hbwCallbacks.forEach(fn=>fn(data));
    _hbwCallbacks = [];
  });
}
```

**Todos los usos de `HOTEL_BY_WEEK[yw]` → `_loadHotelByWeek(function(_hbw){ ... _hbw[yw] ... })`**

**Resultado:** HTML 44MB → **13MB** (70% reducción). JSON ~6.3MB (25 semanas YTD).

### ⚠️ Reglas críticas
- **NUNCA** volver a `const HOTEL_BY_WEEK = {json.dumps(...)}` inline — pesa >20MB en base64
- El JSON y el HTML deben commitearse juntos al repo (misma carpeta `inventory/week-NN/`)
- El JSON es ~6.3MB → commitable por Git Tree API. El HTML (~13MB) también es commitable vía Python (no curl — límite de args del shell)

---

## 🔗 Filtro cruzado dest→corp (W25 · CANÓNICO)

### Bugs resueltos en esta sesión
| Bug | Root cause | Fix |
|---|---|---|
| Filtro México + Mérida no filtraba corporativos | `CORP_DEST_DATA` no se emitía en el HTML | Agregar emisión del dict en `calc_inv.py` |
| `_destCorpsSet` devolvía todos los corps | Usaba `CORP_DEST_MAP` (histórico) en vez de hoteles reales | Usar `CORP_DEST_DATA[corp,dest]` con lookup normalizado |
| Acentos NFD en México/Mérida causaban mismatch | `includes()` es exact-match, no normaliza | Normalizar con `.normalize('NFD').replace(/[\u0300-\u036f]/g,'')` en ambos lados |
| `hDrillWeek` no filtraba por destino activo | Faltaba `_drDests` en el loop de rows | Agregar `drDestsNorm` al filtro de `_renderHotelList` |

### CORP_DEST_DATA — implementación
```python
# En calc_inv.py — emitir después de CORP_REG_DATA
CORP_DEST_DATA_dict = {
    f"{corp},{dest}": {'sp': int(grp['sp'].sum()), 'hy': int(grp['hy'].sum()), 'tp': int(grp['tp'].sum())}
    for (corp, dest), grp in df.groupby(['Corporativo', 'Destino'])
}
# En el HTML:
f"const CORP_DEST_DATA = {json.dumps(CORP_DEST_DATA_dict, cls=NpEncoder)};"
```

### Lookup normalizado NFD
```js
// Cache de normalización O(1)
window._CORP_DEST_NORM = {};
function _nrCD(s) {
  if (!_CORP_DEST_NORM[s]) _CORP_DEST_NORM[s] = (s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  return _CORP_DEST_NORM[s];
}

// En hApplyFilter — visibilidad corp-rows
function _hasCorpInDest(corpName, activeDests) {
  return activeDests.some(d => {
    const key = `${corpName},${d}`;
    const keyN = `${_nrCD(corpName)},${_nrCD(d)}`;
    // buscar en CORP_DEST_DATA con normalización
    for (const [k,v] of Object.entries(CORP_DEST_DATA)) {
      if (_nrCD(k) === keyN && (v.sp+v.hy+v.tp) > 0) return true;
    }
    return false;
  });
}
```

---

## 🏗️ Masthead — Estructura canónica (W23+)

Idéntica al Supply PRICE — misma arquitectura de 3 bloques:

```html
<div class="masthead-top-rule">        ← barra negra 3px
<div class="masthead-inner">           ← badge + h1 + logo | border-bottom:1px solid var(--rule)
  <div class="masthead-week">WEEK NN   ← pill cyan #4FC3F4, border-radius:3px (no redondeado)
  <h1> clamp(20px,2.0vw,30px)          ← "State of PriceTravel Product"
  <img class="masthead-logo" h:40px>   ← logo color con transparencia
<div class="masthead-sub">             ← fecha | vol | border-bottom:3px solid var(--ink)
```

---

## 🃏 KPI Bar — 4 cards

**Card 1:** Total `N` (cyan) · PP · Third Party
**Card 2:** Target (cyan) · Avance % (green) · Gap (rojo `#FF3B30`)
**Card 3:** Gap por Corporativo — barra roja gap% (7 cadenas, excl. AA-Independent)
**Card 4:** Gap por Región — mismo layout

---

## 📈 Evolución Histórica del Producto (W23+)

### Chart — Combo Violet/Cyan

**Dataset 1 — Acumulado (línea):** `#5C469C` violet · área dinámica proporcional a PP ratio
**Dataset 2 — Variación (barras):** `rgba(79,195,244, 0.55)` cyan

### Controles
1. Toggle Por Año / Por Mes / Por Semana
2. Dropdowns Año / Mes / Semana
3. Pills Dimensión: `Región | Corporativo | Destino | Channel`
4. Pills Tipo: `Todos | Prod. Propio | Solo Propio | Hybrid | Sin Contrat.`
5. Searchbox autocomplete
6. `#hf-active-pills` — pills activas encima del gráfico

### `hGetDim()` — fuente de datos condicional
```js
if (activeChannels.length > 0) {
  return HIST.dim.filter(r => ... && activeChannels.includes(r.channel) ...)
} else {
  return HIST.dim_hotel.filter(r => ...)
}
```

---

## 🗂️ Distribución y Exploración

### Pills — dos filas
**Fila 1 (Dimensión):** `Región | Corporativo | Destino | Channel` — fondo sólido cyan
**Fila 2 (Contratación):** `Todos | Prod. Propio | Sin Contrat.` — fondo sólido violet · Sin Contrat. en rojo

### Columnas — TODAS SIEMPRE VISIBLES
Los CSS `col-show-XX` NO ocultan otras columnas. Solo resaltan el header activo.

### VS GLOBAL — eliminada permanentemente
`th-vs, td-vs { display:none!important }` — no reintroducir.

---

## ⚙️ Arquitectura de índices compactos (W23 · CANÓNICO)

`HIST.snapshot` (~80K rows → 40-43MB) fue eliminado. Reemplazado por:

| Índice | Keys | Agrupación | Uso |
|---|---|---|---|
| `dim_ch` | `w,m,t,ch,n` | yw×ym×ch_tipo×channel | filtro channel |
| `dim_tipo` | `w,m,t,n` | yw×ym×ch_tipo | filtro solo-tipo |
| `dim_hotel` | `w,m,r,c,d,t,n` | yw×ym×region×corp×dest×ch_tipo | filtro región/corp/dest + drill |

**Regla crítica:** usar `r.w||r.yw` (nunca solo `r.yw`) al construir `sparseMap` — el dim compacto usa `w`, no `yw`.

---

## 💻 Ejecución local

```powershell
cd C:\Users\federico.iglesias\Price\inventory
# 1. Editar CONFIG en calc_inv.py (WEEK, WEEK_NUM, VOL_NUM, SNAPSHOT_DATE, INPUT_FILE)
# 2. Copiar dataset de contratos a esta carpeta
python calc_inv.py
```

**Outputs generados en `week-NN/`:**
- `INVENTORY_WNN.html` (~13MB)
- `hotel_by_week_WNN.json` (~6.3MB)
- `Analisis_Inventory_WNN.xlsx`

**Commit:** SIEMPRE por Git Tree API (Python), NUNCA GitHub Desktop.
Ambos archivos (HTML + JSON) deben commitearse juntos.

```python
# Patrón correcto — usar Python para blobs grandes (curl falla con args >8MB)
with open('INVENTORY_WNN.html', 'rb') as f:
    content = base64.b64encode(f.read()).decode('utf-8')
# POST /git/blobs con payload Python, no curl
```

---

## 🏢 Reglas de negocio

### Clasificación corp+channel
`CORP_CHANNEL_TIPO_OVERRIDE` en `calc_inv.py` — lugar canónico para overrides:
```python
CORP_CHANNEL_TIPO_OVERRIDE = {
    ('Marriott', 'Expedia'): 'Hybrid',  # Marriott+Expedia = Producto Propio
}
```

---

## 🐛 Bugs cerrados

| Bug | Descripción | Semana |
|---|---|---|
| B23–B64 | Ver versiones anteriores del PROMPT_INV | W22–W23 |
| filtro región México (idx<10) | `hApplyFilter` ocultaba destinos de México (idx≥48) aunque pasaran el filtro. Fix: `(activeRegion \|\| idx < 10 \|\| isSel)` | W25-inv-filter |
| normalización NFD `_nr3` | PowerShell corrompía el regex unicode en el HTML. Fix: emit directo desde Python sin pasar por PowerShell `Out-File` | W25-inv-filter |
| `CORP_DEST_DATA` no emitido | Variable JS referenciada pero nunca generada en Python | W25-inv-corp-dest |
| Todos los corps visibles con dest activo | `_destCorpsSet` usaba CORP_DEST_MAP histórico en vez de hoteles reales del dest | W25-inv-corp-dest |
| Acentos NFD en México/Mérida | `includes()` es exact-match, falla con caracteres acentuados NFD | W25-inv-corp-dest |
| `hDrillWeek` no filtraba por destino | Faltaba `_drDests` en loop de rows | W25-inv-corp-dest |
| HTML 44MB → 13MB | `HOTEL_BY_WEEK` inline reemplazado por JSON externo on-demand | W25-inv-hbw |

---

## 📋 Pendientes

- [ ] Validar filtro México + Mérida en Netlify (W25 · 25-06-2026)
- [ ] Actualizar valores KPI W25 en PROMPT_INV (universo, gap, ritmo)
- [ ] Wiring `ch_by_region` y `REG_TOTALS` para Inventory region-filtered channel view (stash descartado)
- [ ] `run_inv.py` — actualizar checks para nueva arquitectura on-demand (JSON separado)

---

## 🔑 Token y Commit GitHub

- **`text3.txt`** en el proyecto Claude — token GitHub PAT
- Path del repo: `federicochurches/Price` · branch `main`
- Outputs: `inventory/week-NN/INVENTORY_WNN.html` + `inventory/week-NN/hotel_by_week_WNN.json` + `Analisis_Inventory_WNN.xlsx`
- Commit message: `fix/feat: Inventory WNN · descripción · DD-MM-YYYY`

---

**Última actualización:** v17.0 · W25-inv-hbw · 25-06-2026
**Cambios v17:** HOTEL_BY_WEEK on-demand (HTML 44→13MB) · fix filtro dest→corp NFD México/Mérida · CORP_DEST_DATA emitido · hDrillWeek con filtro destino · arquitectura JSON externo documentada
