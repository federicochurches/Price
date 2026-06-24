# 🔧 REFACTOR P9 · Centralización CR/RND · CERRADO W22
**Fecha cierre:** 2026-05-26

## Estado: ✅ COMPLETADO

### Lo que se hizo

#### 1. `render_helpers.py` — funciones nuevas agregadas

| Función | Propósito |
|---|---|
| `KPI_TOP_N = 10` | **Constante única** para top visible — 1 línea para cambiar |
| `render_traf_wow_pill_pct(pct_delta)` | Pill WoW de tráfico expresado como % |
| `render_traf_wow_pill_abs(abs_delta)` | Pill WoW de tráfico expresado como delta absoluto |
| `render_traf_line_cr(cr_current, cr_prev)` | Línea "Tráfico: 746.111 ↑pill" para CR |
| `render_traf_line_rnd(trafico_current, trafico_prev)` | Línea "Tráfico: 12,2B ↑pill" para RND |
| `_resolve_label(r, t_key)` | Extrae (raw_lab, lab, corp_sub) según t_key — centraliza lógica de etiquetado |
| `build_kpi_tab_rows(df_t, t_key, cfg)` | Genera HTML de filas con `cfg` dict — el corazón del refactor |
| `build_kpi_tab_panel(df_t, t_key, cfg, spec)` | Construye `<div class="tab-panel">` completo |

#### 2. `render_cr_p1.py`
- Loop Eficacia reemplazado por dict `_EF_CFG` + llamada a `build_kpi_tab_panel()`
- Loop ConvRate reemplazado por dict `_CV_CFG` + llamada a `build_kpi_tab_panel()`
- `_cr_trafico_line()` delegada a `render_traf_line_cr()`
- Duplicado inline de traf_line en `render_kpi_card_eficacia` eliminado
- **−138 líneas** (791 → 653)

#### 3. `render_rnd_p1.py`
- Loop NoDispo reemplazado por dict `_ND_CFG` + llamada a `build_kpi_tab_panel()`
- Loop IPM reemplazado por dict `_IPM_CFG` + llamada a `build_kpi_tab_panel()`
- Ambas `_traf_line` inline reemplazadas por `render_traf_line_rnd()`
- **−80 líneas** (538 → 458)

### Criterio de éxito cumplido

Un cambio en `KPI_TOP_N` (hoy `10`) requiere modificar **1 sola línea** en `render_helpers.py`. ✅

### Nota de diseño — tabs "channel" y "canasta"

Los tabs `channel` (CR) y `canasta` (ambos) conservan su lógica ad-hoc porque:
- `channel` necesita split PP/TP con grid diferente (4 cols vs 6)
- `canasta` no tiene WoW por fila ni filtro de corpus

`build_kpi_tab_panel()` devuelve `''` si `t_key == 'channel'`, delegando al caller.

---
> P9 movido a HISTORIAL_SESIONES como bug cerrado.

---

## Panel AR — Patrones canónicos (W22 post-pipeline)

### Top N en panel AR y Excels
- **`head(1000)`** en todos los tabs de hotel y dimensiones — `render_cr_p2.py`, `render_rnd_p2.py`, `render_rnd_p3.py`, `excel_cr.py`, `excel_rnd.py`
- El DOM carga hasta 1.000 rows; `_KPI_TOP_N=5` controla cuántos son visibles por defecto

### Searchbox panel AR (`render_cr_p2.py` + `js_override.js`)
- HTML: dos pills inline en `render_analisis_rendimiento()` — `sb-panel-th` (hotel) y `sb-panel-td` (dim)
- JS: handler `initPanelSearch()` en `js_override.js` — **no** usar `attachPill` de `asset_shared_head` (necesita `.kpi-card`)
- Filtra `[data-hist-label]` en el tbody activo · se limpia al cambiar tab · se re-init al cambiar canasta/modo

### Clicks en rows 6-1000 (`js_override.js`)
- `_injectHistAttrs` solo inyecta en render inicial → rows-more sin `data-hist-w21`
- Fix: patch de `_moreBtn` agrega inyección al expandir usando `tbody._lastRows`
- `tbody._lastRows` se guarda en cada `w22_renderTable`

### Persistencia selección entre pestañas (`js_override.js`)
- `_selectedPanelLabel` guarda label del hotel/dim seleccionado
- Cada `w22_renderTable` re-aplica highlight si label existe en nuevos rows
- Segundo click, cambio de canasta o modo → limpia `_selectedPanelLabel`

### Excel RND — dimensiones por canasta (`excel_rnd.py`)
- Para canasta `Global` (`can_id is None`): usar `TAB_ND`/`TAB_IPM` globales
- Para B2C/OP/CUG: usar `can.get('agg_pais')`, `can.get('agg_dest')`, `can.get('agg_corp')` del pickle
- `calc_rnd.py` ya calcula estas dimensiones por canasta en `CANASTA_DATA`

---

## Motor lazy de hoteles · Patrón unificado CR+RND (W24)

Las KPI cards sirven el panel hotel desde un **pool compacto** (NO en DOM) en vez de volcar miles de filas. Una sola función para ambos reportes.

### Dónde tocar qué
| Pieza | Archivo | Qué hace |
|---|---|---|
| `_HOTEL_POOL_CFG` {cr, rnd} | `assemble_unified.py` | Config por reporte: `poolVar`, `bandNamesVar`, índices corp/dest/país, y `metrics[card]` con `valIdx`/`bandIdx`/`wowIdx`/`sortDesc`/`requireVal`/`grid` |
| `_poolToCardRow(h, report, metric)` | `assemble_unified.py` | Convierte fila de pool → fila de `_cardRow` |
| `_lazyHotelRender(report, card, cf, container)` | `assemble_unified.py` | Filtra el pool (`cf.corp/dest/pais` cross-filter · `cf.bands` banda · `cf.hotel` exacto) → ordena → reconstruye panel (5 vis + 5 cf-extra + resto `sb-hidden`, cap 300) |
| `CR_HOTEL_POOL` (`_build_cr_hotel_pool_json`) | `render_cr_p1.py` | 3.582 hoteles CR, 11 campos `[lab,corp,dest,cru,cru_wow,ef_pct,ef_b,ef_wow,cv_pct,cv_b,cv_wow]` |
| `RND_HOTEL_POOL` (`_build_rnd_hotel_pool_json`) | `render_rnd_p1.py` | 21.183 hoteles RND, 12 campos (incluye país) |

### Reglas del patrón
- **Solo canasta global usa pool.** Per-canasta (b2c/op/cug) van por DOM con `CR_CARD_TABS[canasta]` (~100 c/u). Guarda `_canG` en `_kpiPillRender` (rama `_isCR`) y en `_kpiSbPoolFor`. Motivo: el pool es global; `w22_renderCardTabs`→`_kpiSortAttach` saltea listas vacías y NO llama `_kpiPillRender`.
- **El default no se vacía, se reduce a banda crit.** `CR_CARD_TABS['global'][ef/cv]['hotel']` = solo crit (el `_kpiSortAttach` lo necesita en carga y cambio de canasta). El estático de `render_cr_p1.py` es `head(5)` (solo estructura). El lazy reemplaza al entrar al tab / cross-filter / searchbox.
- **Searchbox pool-aware:** `_kpiSbBuildDD` sugiere desde el pool; `_kpiSbSelect` renderiza el hotel desde el pool si falta en el DOM. Aplica a CR y RND en vista hotel + canasta global.
- **Wrappers RND** (`_rndLazyHotelRender`/`_rndPoolToCardRow`) delegan en las genéricas — no duplicar lógica.

### Pendiente (opcional)
Lazy-ificar las **AR cards CR** (`CR_D` ~2,0MB + `CR_HOTELS` ~0,88MB ≈ ~3MB) — tienen su propio searchbox y estructura; B tampoco lo hizo en RND.



## W25-hist-entity · 24-06-2026

### Nuevos dicts históricos por entidad
- `build_hist_entity.py` ahora genera: corp, dest, **hotel**, **provider** para CR; corp, dest, **hotel** para RND
- `CR_HOTEL_HIST`: 6024 hoteles W18-W24; clave = nombre sin prefijo `(ID) -`
- `CR_PROVIDER_HIST`: 10 providers W18-W24 (DerbySoft, SynXis, HBSI, etc.)
- `RND_HOTEL_HIST`: hoteles RND (generado en pipeline, no en W25 directo)
- Para W26+: pipeline los genera automáticamente; no requiere intervención manual

### Lookup histórico — prioridad en handlers
```
Hotel view (KPI + AR):  CR_HOTEL_HIST[nombre] → fallback CR_CORP_HIST[corp]
Channel view (EF/CV):   CR_PROVIDER_HIST[label][ck].concat([w25])
Dest view:              CR_DEST_HIST[nombre] o CR_DEST_HIST[nombre + ' Area']
Corp view:              CR_CORP_HIST[corp]
```

### Pattern: lookup con fallback +Area
El 87% de `CR_DEST_HIST` tiene sufijo ` Area` que los labels del HTML no tienen.
Solución en `assemble_unified.py`:
```javascript
var _eKey = _hDict[_eName] ? _eName
           : (_hDict[_eName + ' Area'] ? _eName + ' Area'
           : (_hDict[_eName.replace(/ Area$/, '')] ? _eName.replace(/ Area$/, '') : null));
```
