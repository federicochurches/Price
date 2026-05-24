# CHANGELOG · Proyecto PRICE · Supply Analytics

---
---
## Fix batch post-W20 · 24 Mayo 2026 · UI/UX bugs 7 issues

### Cambios
| Fix | Reporte | Descripción |
|---|---|---|
| ConvRate sin bold | CR | Dim tables global (p2) y canastas (p3) — `color:var(--ink-muted)` |
| WoW ConvRate en dim canastas | CR | `tab_panel_dim_cr` ahora merges `ConvRate_W17` para calcular WoW |
| Severity text-align:left | CR+RND | Header de `dim_table_with_wow` y equivalente RND |
| parse_hotel=False | CR+RND | Canastas no parsean nombre hotel — código `(123456)` ya no visible |
| Channel clickeable | CR | Tab channel en canastas: `data-hist-label` + `cursor:pointer` |
| Tráfico en hotel canastas | RND | Columna Tráfico añadida, grid expandido a 5 cols |
| IPM badge violeta | RND | Alertas global: `#EDE9F8` violet (no `#FEF9C3` amarillo) |

### Commit
`8a2f6cc8c4cf` — fix(ui): 7 fixes UI W20

### Archivos modificados
`render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p3.py`

## Fix/Cambio · W20 · 24 May 2026

**Descripción:** Fix batch UI: ConvRate sin bold, WoW ConvRate dim canastas CR, Severity left-align, parse_hotel=False, Channel clickeable CR, Tráfico col RND hotel canastas, IPM badge violeta alertas RND

## Pipeline W20 · Mayo 2026 · 11–17 may 2026

**Fecha publicación:** LUNES 18 DE MAYO DE 2026  
**Tipo:** Pipeline completo (6 pasos)

### KPIs W20

| Métrica | W19 | W20 | WoW |
|---|---|---|---|
| **%NoDispo** | 2,48% | 2,81% | +0,33pp |
| **IPM** | $657 | $1.194 | +81,7% |
| **Eficacia** | 93,46% | 92,75% | -0,71pp |
| **Conv Rate** | 1,16% | 1,19% | +0,03pp |

Hoteles P80 RND: 19.456 · CR: 2.080 · CR únicos: 1.492.747

### Outputs generados

| Archivo | Descripción |
|---|---|
| `RatesNoDispo_Reporte_Editorial.html` | Reporte editorial RND W20 |
| `CheckRates_Reporte_Editorial.html` | Reporte editorial CR W20 |
| `Analisis_Rates_NoDispo_7d.xlsx` + 3 canastas | Excel RND global + B2C/OP/CUG |
| `Analisis_Checkrates_7d.xlsx` + 3 canastas | Excel CR global + B2C/OP/CUG |
| `Mail_W20.html` | Mail semanal |
| `index.html` | Hub actualizado |
| `Price_W20.zip` | ZIP repo listo para commit |

## Cambio · Mayo 2026 · Automatización docs + commit en pipeline

### Contexto
Los pasos 7 (docs) y 8 (commit + ZIP) son ahora parte del pipeline automático.

### Scripts nuevos

| Script | Descripción |
|---|---|
| `update_docs.py` | Paso 7 · actualiza CHANGELOG + README + PROMPT_MAESTRO con KPIs del pickle · modo `pipeline` y `fix` |
| `github_commit.py` | Paso 8 · commit vía GitHub API + ZIP del proyecto Claude · reemplaza `commit_release.py` |

### Cambios en `run_pipeline.py`
- Agregados **Paso 7: UPDATE DOCS** y **Paso 8: COMMIT + ZIP** como pasos non-critical
- Paso 8 se activa si hay `github_token` en el YAML o `GITHUB_TOKEN` en el entorno
- Si no hay token, el paso 8 se saltea con aviso (no bloquea el pipeline)

### Uso del token en YAML
```yaml
# WEEK_CONFIG_W21.yml
github_token: ghp_xxx   # Opcional — si no está, agregar manualmente vía env
```

### Uso standalone de los nuevos scripts
```bash
# Solo docs (ej: después de un fix puntual)
python3 update_docs.py --week 21 --periodo "18–24 may 2026" --tipo fix --descripcion "Fix searchbox"

# Commit completo (pipeline)
python3 github_commit.py --week 21 --periodo "18–24 may 2026" --token ghp_xxx

# Commit de fix puntual
python3 github_commit.py --week 21 --tipo fix --mensaje "Fix badges canastas" --token ghp_xxx
```

### Archivos modificados
`run_pipeline.py` · `update_docs.py` (nuevo) · `github_commit.py` (nuevo)

## Week 20 · Mayo 2026 · Sesiones 7–13 · UI/UX completo + Searchbox interactivo + Top 100

### Resumen ejecutivo de cambios

Las sesiones 7–13 completaron la transformación visual y funcional del pipeline post-W20. Los cambios se agrupan en cuatro áreas:

1. **Arquitectura UI/UX**: minimalismo, cards compactas, layout 3 secciones, badges paleta D
2. **Interactividad**: searchbox en todas las tablas, top 100 en DOM, cross-tab correcto
3. **Histórico reactivo**: canastas + hotel + dimensión, listener de click en todos los contextos
4. **Correcciones RND**: severity, hotel/dim top 100, tab-panel display

---

### ✨ Sesión 7 · UI minimalista + Autocomplete dropdown

**Commits:** `0116d4e`, `3d0eb7a`

- Searchbox con autocomplete dropdown basado en `data-hist-label`
- Severity badges revisados (inicio de paleta D)
- Alineación columnas por-hotel y Críticos primero en tab order RND
- Eliminadas barras Metodología / Brecha / Interpretación

---

### ✨ Sesión 8 · Rediseño UI minimalista completo

**Commit:** `41fcdef`

- Footer global eliminado
- RE y Plan compactos (sin bold en contenido → `<span>` reemplaza `<strong>`)
- Badge de banda al lado del valor grande (no debajo)
- Canastas: sin searchbox aún (se cierra en s9-s11)
- Títulos de sección de canastas = mismos que globales (h3 22px)
- Secciones sin bajadas descriptivas (solo título + subtítulo)

---

### ✨ Sesión 9 · Searchbox dentro de cards hero + Top 100 DOM

**Commit:** `0645a93`

- Searchbox inline dentro de cada card (Eficacia, ConvRate, NoDispo, IPM)
- `calc_cr.py` / `calc_rnd.py`: tabs hero → `head(100)` (era 10)
- DOM: 100 filas por tab; 10 visibles al abrir (`sb-hidden` en filas 11-100)
- `data-row-idx` en cada fila para preservar el límite al limpiar el search
- Layout: `display:grid;grid-template-columns:1fr 1fr` en `.kpi-tab-rows`
- JS filter: `getActiveRows()` limita al panel visible; `gridTemplateColumns: 1fr` al buscar

---

### ✨ Sesión 10 · Gauge, Severity, RE/Plan, Banners Excel, Canastas

**Commits:** `a1e52f7`, `7e6f2c5`

**Gauge (BANDAS.md):**
- `height:6px · opacity:1` — uniforme, sólido, sin transparencia ni labels de texto
- Sin Conversión: `#8A8377` (era negro)
- Banda activa: `border-bottom:2px solid var(--ink)` en vez de opacidad diferencial

**Severity (paleta D canónica):**
- `template_severity.py` + `render_cr_p2.py`: bg pastel / fg oscuro (no invertido)
- Súper Crítica: `#A32D2D` (granate sólido) + `#FCEBEB` (texto claro)

**RE y Plan:**
- `template_resumen.py`: `<strong>` → `<span>` en título de finding
- `.action-row .accion strong { font-weight:400 }` en CSS

**Banners Excel:**
- `.detail-callout`: `padding:12px 16px` (unificado global y canastas)
- `.badge-link`: color accent + border-radius:3px (no fondo negro)

**Canastas interactivas:**
- `render_cr_p3.py`: searchbox inline en `kpi_card_canasta`
- `render_rnd_p3.py`: idem
- `render_historico_seccion_cr/rnd` definidos localmente en p3
- Módulos histórico en bloque hotel + dimensión de canastas CR/RND

**Regressions (7e6f2c5):**
- `box-sizing:border-box;width:100%` en `.kpi-card`
- `column-count:2` → `display:grid;grid-template-columns:1fr 1fr` (column-count conflicta con display:grid en hijos)
- `sb-cr-hero` / `sb-rnd-hero` eliminados (searchboxes fuera de cards)
- Análisis por tipo de producto eliminado de PART2 CR
- Tab-panel activo: `display:block` (no `display:grid 1fr 1fr` que causaba el truncamiento)

---

### ✨ Sesión 11 · Top 100 hotel/dim global+canastas + Searchbox canastas + Estilos unificados

**Commit:** `9d7cfa1`

**Top 100 en análisis por hotel y por dimensión global:**
- `calc_cr.py TOP`: criticos/bajo_rend/sin_conv/menor_cv/corps_10/destinos → `head(100)`
- `render_cr_p2.py render_top_table_cr`: `data-row-idx`, `sb-hidden` (10 visibles)
- `render_cr_p2.py _render_panel_top_table_cr`: wrapper `kpi-tab-rows grid 2 cols`
- `render_cr_p2.py panel_for_dim`: `head(100)`, wrapper `kpi-tab-rows`
- `render_cr_p2.py _render_dim_table`: `data-row-idx`, `sb-hidden`, badges paleta D

**Estilos unificados (font-size:11px):**
- `render_top_table_cr`, `_render_dim_table`, `tab_panel_hotel`, `panel_inner_rnd` → `font-size:11px`
- CSS: `.kpi-tab-rows [data-hist-label] { font-size:11px }`

**Badges paleta D en tablas dimensión:**
- `_render_dim_table` CR: Súper Crítica `#A32D2D`/`#FCEBEB`; resto `bg=c['bg']`/`fg=c['fg']`
- `dim_table_with_wow` CR p3: idem — eliminado bg=fg invertido anterior

**Searchbox en tablas hotel y dimensión de canastas CR y RND:**
- `input.sb-input` con `data-sb-scope` en `bloque_hotel_html` y `bloque_dim_html`
- `tab_panel_dim_cr/rnd`: `head(100)`, wrapper `kpi-tab-rows grid 2 cols`
- `panel_inner_rnd`: `data-row-idx`, `sb-hidden`, display:grid unificado

**tab_panel_hotel CR canasta:** reescrito con 100 filas, estilos unificados.

---

### ✨ Sesión 12 · RND tabs ancho, click canasta, cards compactas, colores, search por pestaña

**Commit:** `5e27145`

**RND card tabs: truncamiento (1....)**
- Causa: CSS `display:grid 1fr 1fr` en tab-panel activo hacía el panel de 267px, y el `kpi-tab-rows` interno recibía solo 1fr de eso (~133px)
- Fix: `asset_rnd_head.html` — tab-panel activo → `display:block`

**Canasta hotel CR: click no pintaba el elemento activo**
- `render_cr_p3.py render_historico_seccion_cr`: `parent` sube por DOM hasta el bloque `canasta-*-hotel/dim`
- Listener excluye `[id^="hist-"]` en lugar de `.kpi-card`

**tab_panel_hotel CR canasta: 2 cols explícitas con header propio**
- Col izq (hoteles 1-5) + col der (6-10+), cada una con su header: HOTEL | CONVRATE | EFICACIA | WOW

**CR hero card tabs: `<strong>` negro → `<span color:var(--accent)>`**

**Módulo histórico: label "Global" con menos contraste**
- `historico_module_v2.py` + `historico_module_rnd.py`: `var(--accent)` 700 → `var(--ink-muted)` 600

**Cards más compactas:**
- `render_cr/rnd_p1.py`: `font-size:48→40px`, `padding:18 20→12 16px`
- Canastas: `42→36px`, padding idem

**Search se limpia al cambiar pestaña:**
- Listener `change` en radio inputs limpia el `input.sb-input` y hace reset de filas

---

### ✨ Sesión 13 · Cross-tab search, severity RND paleta D, top 100 RND, canastas RND

**Commit:** `3e5ebd2`

**Cross-tab search corregido:**
- `getActiveRows()`: detecta el panel activo con `window.getComputedStyle(panel).display !== 'none'`
- `filter()` opera solo sobre el panel activo
- Dropdown autocomplete eliminado — solo filtrado inline
- Clear-on-tab-change: listener `change` en radios limpia sb y resetea filas al tab activo

**RND severity: paleta D canónica:**
- `render_severities_combinadas`: dict `BADGE_COLORS` con bg pastel / fg oscuro
- Súper Crítica: `bg:#A32D2D` / `fg:#FCEBEB` (sólida); resto bg pastel

**RND hotel/dim global: top 100:**
- `calc_rnd.py`: demanda_nc/bajo_rend/sin_conv/corps_10/destinos_10/paises_10 → `head(100)`
- `render_rnd_p2.py render_top_table`: `data-row-idx`, `sb-hidden`, `data-hist-label`
- `_render_panel_top_table`: wrapper `kpi-tab-rows grid 2 cols`
- `panel_for_dim` RND: `head(100)`, wrapper
- `_render_dim_table_rnd`: `data-row-idx`, `sb-hidden`, badges paleta D, `11px`

**Canastas RND: hotel con corp + badge, 2 cols explícitas con header:**
- `tab_panel_hotel`: col izq 1-5 + col der 6-10+, cada col con header Hotel | %NoDispo | IPM | WoW
- Corp sub-line + badge paleta D en cada fila

**Canastas RND: listener click corregido:**
- `render_historico_seccion_rnd`: mismo fix que CR (parent por DOM, excluye `[id^=hist-]`)

---


---
## Week 20 · 23 Mayo 2026 · Sesión 6 · Histórico real W16-W20 + Limpieza legacy + Decisión ventana 5W

### ✨ Histórico real W16-W20 (reemplaza `_FICTICIOS`)

Datos extraídos de pickles `cr_w{16-20}_data.pkl` y `rnd_w{16-20}_data.pkl` generados desde los datasets reales W16-W20.

**Adapter para W16/W17 RND** (estructura distinta a W18+):
- W16: 4 sheets (`Canasta ALL` + 3 individuales) → usar `Canasta ALL`
- W17: idem + columna `html` mal nombrada → renombrar a `CorpName`
- W18-W20: 1 sola sheet `Sheet1` (sin cambios)

**Nuevo módulo:** `_scripts/historico_data.py`
- `HIST_DATA[reporte][metrica][scope]` con valores W16-W19 hardcoded
- Función `get_serie(reporte, metrica, scope, val_actual)` agrega W20 dinámicamente
- Scopes: `global`, `op`, `cug`, `b2c`
- Métricas: `cr/eficacia`, `cr/convrate`, `rnd/nodispo`, `rnd/ipm`

**Cambios en módulos históricos:**
- `historico_module_v2.py` (CR): eliminado `_FICTICIOS`, importa `get_serie`
- `historico_module_rnd.py` (RND): idem
- Ventana cambiada de 8 semanas (W14-W21) a 5 semanas (W16-W20)
- `val_actual` ahora es la semana ACTUAL del reporte (W20), no la próxima (W21) — corrección conceptual
- Labels actualizados: `8W` → `5W` (Máx, Mín, Prom)
- Footer eje X dinámico (`{semanas[0]}` y `{semanas[-1]}`)

**Datos reales visibles W16-W20:**

| Métrica | W16 | W17 | W18 | W19 | W20 | Tendencia |
|---|---|---|---|---|---|---|
| CR Eficacia global | 93.27% | 93.58% | 93.71% | 93.30% | 92.75% | ↘ |
| CR ConvRate global | 1.29% | 1.15% | 1.02% | 1.14% | 1.19% | V invertida |
| RND %NoDispo global | 3.69% | 3.63% | 2.84% | 2.31% | 2.81% | ↘ con leve repunte |
| RND IPM global | $661 | $574 | $524 | $499 | $1.097 | ↗ salto W20 |

**Commit:** `c2c1226`

### 📐 Decisión arquitectónica · Ventana histórica de 5 semanas (Opción A)

Como solo se tienen pickles confiables W16-W20, **se decide mantener una ventana de 5 semanas reales** en lugar de completar a 8 con ficticios marcados.

**Razonamiento:**
1. El reporte es para Supply Optimization (equipo decisor) — datos ficticios en gráficos de decisión = riesgo de pérdida de credibilidad
2. 5 semanas son suficientes para detectar tendencias (mejoras sostenidas, saltos, V invertidas)
3. Es temporal: en ~3 semanas (W23) la ventana llegará naturalmente a 8 semanas reales
4. Eliminar `_FICTICIOS` fue trabajo intencional — no volver atrás

**Plan de evolución de la ventana:**
- **W21**: agregar W21 al pickle → editar `historico_data.HIST_DATA` agregando el valor W20 a cada scope (W20 deja de venir dinámicamente del render porque pasa a ser histórico) y renombrar `SEMANAS` a `['W16', 'W17', 'W18', 'W19', 'W20', 'W21']` (6 semanas)
- **W22**: mismo patrón (7 semanas)
- **W23**: alcanza 8 semanas reales → fijar `len(SEMANAS)=8` permanente, ventana móvil descartando la semana más antigua

**Util pendiente para próxima sesión (no urgente):**
- Script `extract_hist_data.py` que tome los pickles W16-W{N} y regenere `historico_data.py` automáticamente. Hoy se actualiza a mano.

### 🧹 Limpieza legacy: `_scripts/{lib,snippets,templates}/`

Eliminados los últimos archivos del pipeline anterior (no usados por código vivo):

| Eliminado | Archivos | Razón |
|---|---|---|
| `_scripts/lib/` | 5 archivos (.py) | Pipeline actual está en `_scripts/*.py` directos |
| `_scripts/snippets/` | 4 archivos (.html) | Duplicados exactos de raíz |
| `_scripts/snippet_*.html` (raíz) | 4 archivos | 0 referencias en código vivo |
| `_scripts/templates/mail_template.html` | 1 archivo | Reemplazado por `render_mail_v3.py` |

Total: **-14 archivos, -1522 líneas**. Estado final `_scripts/`: 44 archivos.

**Commit:** `abc031a`

### 📦 ZIP del proyecto Claude · `proyecto_claude_W20.zip`

Empaquetado limpio para reemplazar el contenido del proyecto en claude.ai (259 KB, 51 archivos):
- `_docs/` (7 .md): PROMPT_MAESTRO, README, CHANGELOG, BANDAS, COMMIT_GUIDE, AREAS_ACCOUNTABLE, INVENTARIO
- `_scripts/` (43 archivos): pipeline completo + assets HTML
- `destinatarios.md`: BCC del mail semanal

Sin HTMLs generados, sin pickles, sin datasets, sin pycache.

---

## Week 20 · 23 Mayo 2026 · Sesión 5 · Tab Críticos RND + Searchbox cobertura completa

### ✨ Feature 1 · 4ª óptica "Críticos" en Análisis por hotel RND

La sección Análisis por hotel RND tenía solo 3 tabs (Demanda No Convertida · Bajo Rendimiento · Sin Conversión). Faltaba la 4ª óptica: **hoteles con `BandaNoDispo` en Crítica o Súper Crítica** (`%NoDispo > 20%`).

**Cambios:**
- `_scripts/asset_rnd_head.html`: agregado `tab-h-crit` al CSS (selectores de visibilidad de panel y tab activo).
- `_scripts/render_rnd_p2.py`:
  - Nuevo bloque `cols_crit` + `df_crit_all` filtrando `p80_hotel` por `BandaNoDispo` ∈ `['Crítica','Súper Crítica']`, sorted desc por `%NoDispo`, top 50.
  - Input radio `tab-h-crit` + label "Críticos" agregado al bloque de tabs.
  - Panel `crit` agregado al string `panels` con kicker contextual (total Críticos + Súper Críticos).
  - Subtítulo de sección: "3 ópticas analíticas" → **"4 ópticas analíticas"**.

**Resultado validado:** Tab Críticos renderiza con 358 hoteles del P80 (337 Crítica + 21 Súper Crítica). Top 1 W20: Grand Hyatt Istanbul 93.22%.

**Commit:** `05bd9c7` · fix(rnd): agregar tab Críticos en Análisis por hotel (4ª óptica)

### 🔍 Feature 2 · Searchbox cliente-side cobertura completa CR + RND

El searchbox ya existía como helper (`render_helpers.searchbox_html`) + JS auto-attach en `asset_*_head.html`. Esta sesión cerró el último gap: el filtrado en las **canastas colapsables**.

**Cambios:**
- `_scripts/render_cr_p3.py`:
  - Filas `panel-row` enriquecidas con `data-hist-label="{label}"` (para que el JS de filtrado pueda matchear).
  - Bloque Análisis por hotel: `id="canasta-{idx_str}-hotel-cr"` + searchbox "Buscar hotel..."
  - Bloque Análisis por dimensión: `id="canasta-{idx_str}-dim-cr"` + searchbox "Buscar corporativo, destino o channel..."
- `_scripts/render_rnd_p3.py`: mismos cambios análogos para canastas RND.

**Cobertura final:** **18 searchboxes funcionales (9 por reporte):**
- Hero KPI cards (1)
- Análisis por hotel (1)
- Análisis por dimensión (1)
- Canastas B2C/OP/CUG × hotel+dim (6)

**Comportamiento:**
- Filtrado **instantáneo** cliente-side (input event)
- **Case-insensitive y sin acentos** (NFD normalize) — `"cancun"` matchea `"Cancún"`
- **Contador** dinámico: `"X de Y visibles"` al filtrar, `"Y filas"` en estado base
- Color focus por reporte: **magenta** RND `#EA0074`, **violet** CR `#5C469C`
- Búsqueda solo en la **primera columna** (nombre de hotel/destino/corp/channel) vía `data-hist-label`

**Validación playwright:** `"hyatt"` → 86→1 en RND, 66→2 en CR, sin errores JS.

**Commit:** `86a9bef` · feat(canastas): searchbox en Análisis por hotel + dim de cada canasta CR/RND

### 🧹 Diagnóstico de bugs reportados

Auditoría completa de los 5 bugs reportados al inicio de la sesión:

| Bug reportado | Diagnóstico |
|---|---|
| `Uncaught SyntaxError: Unexpected token 'else'` × 6 | **Falso positivo** — ya estaba arreglado en commits previos (`ba41f26`, `8727103`). 0 errores JS verificados con playwright en HTMLs W20 actuales. |
| Severity cards con transparencia | **Falso positivo** — paleta D aplicada con colores sólidos (verificado visualmente). |
| Módulos históricos no aparecen en RND | **Falso positivo** — 8 módulos históricos RND funcionando (2 globales + 6 canastas). |
| Severity canastas sin paleta D | **Falso positivo** — paleta D aplicada correctamente en canastas. |
| Tab Críticos faltante en Análisis por hotel RND | **REAL** — corregido (Feature 1 de esta sesión). |

### 📦 Estado final repo

3 commits push en `main` esta sesión:
```
86a9bef feat(canastas): searchbox en Análisis por hotel + dim de cada canasta CR/RND
05bd9c7 fix(rnd): agregar tab Críticos en Análisis por hotel (4ª óptica)
[+ docs update commit]
```

### 🔜 Pendientes futuros

- Datos históricos reales W14-W20 en pickle (hoy `_FICTICIOS` en `historico_module_v2.py` y `historico_module_rnd.py`)
- Validar pipeline completo con datasets W21 cuando llegue la semana
- Persistencia de filtro searchbox entre tabs (decisión pendiente)
- Revocar PAT GitHub al final de toda la sesión

---
## Week 20 · 23 Mayo 2026 · Sesión 4 · Módulo histórico CR hotel/dim + Reformulación badges Opción D

### ✨ Feature 1 · Módulo histórico CR en Análisis por hotel + Análisis por dimensión

Pendiente cerrado de sesión 3: portar el módulo histórico de RND a las dos secciones equivalentes en CR.

**Nueva función:** `render_historico_seccion_cr(canvas_id_ef, canvas_id_cv, banda_ef, val_ef, banda_cv, val_cv)` en `render_cr_p2.py` (análoga a `render_historico_seccion_rnd`).

**Modificado:** `historico_module_v2.py` ahora registra listeners `hist-update` y `hist-reset` SIEMPRE (fuera del bloque `readyState`), permitiendo que wrappers externos disparen actualizaciones del canvas. Backward-compatible con el listener interno de `.kpi-card` (Hero y canastas siguen funcionando).

**Parámetro opcional:** `with_hist=True` en `render_top_table_cr` y `_render_dim_table` enriquece cada fila con `data-hist-w21/w20/cv-w21/cv-w20/label` + `cursor:pointer`.

**Integración:**
- `render_bloque_hoteles_cr` → canvas IDs `hcr-hotel-ef` y `hcr-hotel-cv` (debajo de los 4 tabs Críticos/BajoRend/SinConv/MenorCV)
- `render_bloque_dimensiones_cr` → canvas IDs `hcr-dim-ef` y `hcr-dim-cv` (debajo de los 3 tabs Corp/Destino/Channel)

**UX:** click en fila de tabla actualiza ambos módulos (Eficacia + ConvRate) sincronizadamente. Re-click resetea a Global. Aislamiento total: clicks en sección NO afectan cards hero y viceversa.

**Commit:** `6a0c38e` · feat(cr): módulo histórico reactivo en Análisis por hotel y por dimensión

### 🎨 Feature 2 · Reformulación badges severity (Opción D + paleta D)

Cierre del cambio que se había perdido en un revert. **Estilo Opción D** aplicado uniformemente a TODOS los badges del sistema (Hero, módulos históricos, severity tablas, pills en filas).

**Nuevo estilo:**
```css
font-size: 13px              /* canastas: 11px */
font-weight: 700
letter-spacing: .04em
text-transform: uppercase
padding: 10px 22px
border-radius: 3px
border: 1px solid {bd}
text-align: center
```

**Cambios funcionales:**
- Texto del badge: SOLO nombre de banda en mayúsculas (sin "· Target X%")
- Nueva función `target_caption(target_text, font_size='11px')` en `render_helpers.py` para renderizar el target como caption gris separado debajo del badge
- `banda_pill()` refactorizada: parámetro `target` se mantiene en firma por compatibilidad pero se ignora

**Módulo histórico CR:**
- Quitado el label "Banda" como title arriba del badge (línea 138 vieja del `_BANDA_COLORS` box)
- Quitado el prefijo "Banda: " del footer — ahora muestra solo `EXITOSA`, `REVISAR`, etc. en mayúsculas
- JS `updateMetrics()`: `el.textContent = banda.toUpperCase()` en lugar de `'Banda: ' + banda`

El módulo histórico RND ya estaba correcto desde sesión 2 — no requirió cambios.

### 🔧 Fix barrido · Cyan `#4FC3F4` → Verde teal `#085041` en Exitosa

Sesión 3 había aplicado el fix solo a `BANDA_COLORS` del `render_helpers.py`. Quedaron 22 referencias hardcodeadas a cyan que se escaparon. **Esta sesión barrió todas:**

| Archivo | Lugares | Tipo |
|---|---|---|
| `render_helpers.py` | 4 ocurrencias (`gauge_5levels` variantes) | Hardcoded Exitosa color |
| `render_cr_p2.py` | 3 ocurrencias + fallback bg `#E8F7FD` → `#E1F5EE` | Severity gauges + fallback |
| `render_rnd_p2.py` | 4 ocurrencias (severity + tablas dim) | Hardcoded Exitosa |
| `render_rnd_p3.py` | 1 (COLORS canastas) | Hardcoded |
| `template_severity.py` | 5 ocurrencias (Severity tables) | bg/fg de banda Exitosa |
| `historico_module_v2.py` | 1 (`_BANDA_COLORS['Exitosa']`) | Dict de colores módulo CR |
| `asset_cr_head.html` · `asset_rnd_head.html` | Var CSS `--green` y `--green-soft` + `exec-mini-card.qw` border | CSS |
| `snippet_alertas_canasta.html` + `_rnd.html` (+ duplicados en `snippets/`) | `border-top:3px solid` | CSS inline |

**Cyan `#4FC3F4` queda SOLO en 2 lugares válidos:**
1. `IPM_ACCENT` en `historico_module_rnd.py` línea 10 (Arctic Blue corporativo, accent visual IPM)
2. Label "🔌 Third Party" en `render_cr_p1.py` líneas 197, 338 (color identitario familia Third Party CR)

### 📋 Bugs corregidos #81–#93
- #81 `banda_pill()` rediseñada · estilo Opción D
- #82 Nueva función helper `target_caption()`
- #83 Hero + canastas usan `pill_with_target` (pill + caption separado)
- #84 Módulo histórico CR: quitar label "Banda" arriba del badge
- #85 Módulo histórico CR footer: quitar prefijo "Banda: "
- #86 JS `updateMetrics()` `historico_module_v2.py`: textContent solo nombre en mayúsculas
- #87 `gauge_5levels` Exitosa cyan → verde (4 variantes)
- #88 `render_cr_p2.py` Exitosa cyan → verde (3) + fallback bg cyan → verde
- #89 `render_rnd_p2.py` Exitosa cyan → verde (4)
- #90 `render_rnd_p3.py` COLORS canastas Exitosa cyan → verde
- #91 `template_severity.py` Exitosa bg/fg cyan → verde teal (5)
- #92 Var CSS `--green` y `--green-soft` cyan → verde + `exec-mini-card.qw` border
- #93 Snippets alertas canasta border-top cyan → verde

### 🗂 Archivos modificados
**Código:** `render_helpers.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `historico_module_v2.py` · `template_severity.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `snippet_alertas_canasta.html` · `snippet_alertas_canasta_rnd.html` · `snippets/snippet_alertas_canasta*.html` (duplicados)

**Documentación:** `_docs/BANDAS.md` (reescrito completo) · `_docs/PROMPT_MAESTRO_v3.md` (sesión 3 + 4 documentadas)

### ⏸ Pendientes que quedan abiertos
- Validación visual final del reporte CR W20 regenerado con badges Opción D
- Regenerar reporte RND W20 con los mismos cambios
- Datos históricos reales W14-W20 en pickle (reemplazar `_FICTICIOS`)
- ~~Decisión sobre `_docs/CHANGELOG.md` duplicado~~ ✅ resuelto: `_governance/` eliminado, canon unificado en `_docs/CHANGELOG.md`
- Restaurar search box (tarea conocida desde sesiones huérfanas previas)
- Commit + push de los cambios de esta sesión

### 🚫 Bugs descartados en esta sesión
- Bug 2 · CR canasta dim números pegados (sesión 4 inicial): descartado tras verificar que pertenecía a una rama huérfana de un revert
- Bug 4 · Search box no revela (sesión 4 inicial): descartado por misma razón
- Bug 5 · RND sin search en hotel (sesión 4 inicial): descartado por misma razón

---
## Week 20 · 22 Mayo 2026 · Sesión 3 · Fixes visuales módulos históricos + colores severity

### 🎨 Sistema de colores severity — correcciones

**Exitosa:** `#4FC3F4` (cyan) → `#085041` (verde teal) en todos los contextos:
- Barras de progreso del severity principal
- Pills de banda Exitosa
- Variable CSS `--green: #4FC3F4` → `--green: #085041`
- Gauge de 5 niveles del módulo histórico

**Súper Crítica:** `#161616` (negro) → `#A32D2D` (rojo oscuro) en gauges

**Gauge de 5 niveles:** todas las barras `height:6px · opacity:1` — mismo grosor, colores sólidos puros, sin transparencia

### ✨ Módulos históricos Análisis por Hotel y Dimensión (RND) — funcionalidad completa

**Problema raíz resuelto:** los módulos clonados (`hrnd-hotel-nd/ipm`, `hrnd-dim-nd/ipm`) no tenían los listeners `hist-update` y `hist-reset` que permiten que el click en una fila actualice el canvas.

**Fixes aplicados:**
- Listeners `hist-update` y `hist-reset` agregados a los 4 módulos clonados directamente en el HTML
- `data-hist-nd` e `data-hist-ipm` con valores reales extraídos del HTML (antes eran `0.0`)
  - Hotel: %NoDispo real de cada fila (ej. `39.5%`, `56.33%`)
  - Dimensión: %NoDispo e IPM real de cada corporativo/destino/país
- Canvas IDs correctos: `hrnd-hotel-nd`, `hrnd-hotel-ipm`, `hrnd-dim-nd`, `hrnd-dim-ipm`
- Balance de divs corregido (eliminación de `</div>` huérfano en línea 5151)

### 🔧 Fixes de usabilidad módulo histórico

- **Badge banda centrado** vertical y horizontal: `display:flex;align-items:center;justify-content:center;min-height:44px`
- **`resetToGlobal` scope fix:** función definida antes del `addEventListener` en `attachListeners()`
- **Reset a Global:** click en label "GLOBAL" o en fila activa resetea la vista (inline fix en módulos clonados)
- **Severity → Severity** (mayúscula) en ambos reportes

### 🗂 Archivos modificados
`CheckRates_Reporte_Editorial.html` · `RatesNoDispo_Reporte_Editorial.html`

---
## Week 20 · 22 Mayo 2026 · Fixes visuales + módulo histórico en secciones RND

### 🎨 Nueva paleta sistema de bandas D

Rediseño completo de colores en `render_helpers.py`, `historico_module_cr.py` y `historico_module_rnd.py`:

| Banda | Antes | Ahora |
|---|---|---|
| Exitosa | Celeste `#0D7A99` | Verde teal `#085041` |
| Aceptable | Violet `#5C469C` | Violet oscuro `#3C3489` |
| Revisar | Marrón `#A86A1D` | Naranja `#7C2D12` / `#F97316` |
| Crítica | Rojo `#C0392B` | Rojo oscuro `#99162B` |
| Súper Crítica | Negro `rgba(22,22,22,.80)` | Rojo `#A32D2D` / texto `#FCEBEB` |

Aplicado en Python (3 archivos) y en los 2 HTMLs W20 (458 reemplazos CR + 380 RND).

### 🎨 IPM accent → cyan corporativo `#4FC3F4`

`historico_module_rnd.py`: `IPM_ACCENT` cambia de `#A86A1D` (amber viejo) a `#4FC3F4` (Arctic Blue corporativo).

Consistencia final:

| Reporte | Métrica 1 | Métrica 2 |
|---|---|---|
| CheckRates | Eficacia → magenta `#EA0074` | ConvRate → violet `#5C469C` |
| RatesNoDispo | NoDispo → magenta `#EA0074` | IPM → cyan `#4FC3F4` |

### ✨ Módulo histórico en Análisis por Hotel y Dimensión (RND)

**`render_rnd_p2.py`** — nueva función `render_historico_seccion_rnd()`:
- Módulo doble (NoDispo + IPM lado a lado) debajo del tabs-block en cada sección
- Cada fila de hotel y dimensión tiene `data-hist-nd`, `data-hist-ipm`, `data-hist-nd-prev`, `data-hist-ipm-prev`, `data-hist-label`
- Click en cualquier fila de cualquier tab actualiza ambos módulos vía `CustomEvent` (`hist-update`)
- Click en "Global" o en fila activa resetea a vista global (`hist-reset`)
- Canvas IDs: `hrnd-hotel-nd`, `hrnd-hotel-ipm`, `hrnd-dim-nd`, `hrnd-dim-ipm`

**`historico_module_rnd.py`** — nuevos listeners:
- `hist-update`: recibe `{cid, w_curr, w_prev, label}` → redibuja canvas + métricas
- `hist-reset`: resetea a datos globales

### 🔧 Fixes de usabilidad · módulo histórico

- Label "Global" clickeable (subrayado punteado + `cursor:pointer`) → resetea a vista global
- Click en fila ya seleccionada → deselecciona y resetea (toggle)
- Aplica en `historico_module_cr.py` y `historico_module_rnd.py` + los 2 HTMLs W20

### 📝 Fixes editoriales

- `Severidad` → `Severity` en ambos reportes (7 reemplazos)
- Footer eliminado en RND para consistencia con CR
- Semanas canvas W14-W21 → W13-W20 en los HTMLs (fix aplicado directo en HTML)

### 🗂 Archivos modificados
`render_rnd_p2.py` · `render_helpers.py` · `historico_module_cr.py` · `historico_module_rnd.py` · `CheckRates_Reporte_Editorial.html` · `RatesNoDispo_Reporte_Editorial.html`

---
## Week 20 · 22 Mayo 2026 · Fixes módulos históricos CR + RND

### 🐛 Bugs corregidos

| Bug | Archivo | Descripción |
|---|---|---|
| #72 | `historico_module_cr.py` | Labels canvas en `rgba(100,90,80,0.55)` y `font-size:7px` → `0.80` y `8px` (legibles) |
| #73 | `historico_module_cr.py` | Datos ficticios con variación insuficiente → fixtures con variación realista W(N-7)-W(N) |
| #74 | `historico_module_cr.py` | `W14`/`W21` hardcodeados en footer sparkline → `{semanas[0]}` / `{semanas[-1]}` dinámicos |
| #75 | `historico_module_rnd.py` | `W14`/`W21` hardcodeados en footer sparkline → `{semanas[0]}` / `{semanas[-1]}` dinámicos |

### 📐 Detalle

**Fix #72-#73 (CR):** El canvas mostraba labels ilegibles (gris pálido, fuente diminuta) y la curva aparecía casi plana por insuficiente variación en los datos ficticios. Fix: alpha `0.55 → 0.80`, font `7px → 8px`, nuevos fixtures con delta realista por semana.

**Fix #74 (CR) + #75 (RND):** El footer del sparkline mostraba siempre `W14 ... W21` hardcodeado, independientemente de `current_week`. Fix: se reemplaza por `{semanas[0]}` y `{semanas[-1]}`, que se calculan dinámicamente a partir de `current_week`. Con `current_week='W20'` → muestra `W13 ... W20`.

### ⚠️ Regla operativa: `current_week` = semana ACTUAL

Al integrar los módulos en los render scripts, usar siempre la semana que se está reportando:
- Hoy W20 → `current_week='W20'` → genera W13-W20
- Próximo lunes W21 → `current_week='W21'` → genera W14-W21

### 🗂 Archivos modificados
`historico_module_cr.py` · `historico_module_rnd.py`

---
## Week 20 · 21 Mayo 2026 · Módulo Histórico RND + Fixes CR

### ✨ Feature: Módulo Histórico Reactivo en RatesNoDispo

**Nuevo archivo:** `historico_module_rnd.py`
- Función `render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id, hist_vals, global_ceil)`
- Dos métricas diferenciadas:
  - `nodispo`: escala invertida (menor = mejor) · accent magenta `#EA0074` · target `< 5%`
  - `ipm`: escala normal (mayor = mejor) · accent amber `#A86A1D` · target `≥ $650`
- Canvas curva escala LOCAL + sparkline escala GLOBAL vs target
- Label target en HTML (esquina sup. derecha) — no dibujado dentro del canvas
- `pR=10` en canvas para igualar ancho con sparkline
- Interactivo: click en elemento actualiza canvas, métricas y banda

**Modificado:** `render_rnd_p1.py`
- Import `historico_module_rnd`
- `render_kpi_card_nodispo`: rows con `data-hist-*` · módulo después de `.tab-panels`
- `render_kpi_card_rpm`: idem · W20 del elemento desde `IPM_W18`

**Modificado:** `render_rnd_p3.py`
- Import `historico_module_rnd`
- `tab_rows_canasta`: rows con `data-hist-*` para NoDispo e IPM
- `kpi_card_canasta`: módulo inyectado después de `{panels}` · antes de `{js_tabs}`

**Cobertura RND:** 8 cards — 2 globales + 6 canastas

### 🐛 Fixes CR

**`render_cr_p1.py`** — Channel tab ahora clickeable:
- `chan_row` (Eficacia): agrega `data-hist-*` + `cursor:pointer`
- `chan_row_cv` (ConvRate): idem · W20 desde `ConvRate_W17`
- Bug corregido: `rows_pp` undefined tras edición — restaurado en ambas funciones

**`historico_module_v2.py`** — Badge Súper Crítica dinámico:
- JS `updateMetrics`: agrega `bbEl.style.color = bc.fg`

### 📐 Fix visual: canvas = sparkline ancho
- `pR` reducido de `38` a `10` en `historico_module_rnd.py`
- Label target movido a HTML posicionado

### ⏳ Pendientes registrados
- Fix color badge Súper Crítica en RND
- Ajustes spacing: tabs-row margin-top · módulo margin-top
- Módulo histórico en Análisis por Hotel y Dimensión (CR + RND)
- Datos históricos reales W14-W20 en pickle

---

## Week 20 · 21 Mayo 2026 · Módulo Histórico CR · "Evolución Histórica"

### ✨ Feature: Módulo Histórico Reactivo en CheckRates

**Nuevo archivo:** `historico_module_v2.py`
- Función `render_historico_cr()` — genera bloque HTML+JS completo
- Canvas con curva de tendencia (escala local) + sparkline (escala global vs target)
- 5 métricas: Actual · Máx 8W · Mín 8W · Prom 8W · Banda
- Interactivo: click en cualquiera de los 10 elementos del tab actualiza el módulo
- Colores del sistema D exactos · Súper Crítica badge negro/blanco · footer texto oscuro
- Título: "Evolución Histórica"

**Modificado:** `render_cr_p1.py`
- Import `historico_module_v2`
- `render_kpi_card_eficacia` y `render_kpi_card_convrate`: módulo después de `.tab-panels`
- Rows de tabs con `data-hist-w21`, `data-hist-w20`, `data-hist-label`
- `chan_row` y `chan_row_cv`: Channel tab clickeable

**Modificado:** `render_cr_p3.py`
- Import `historico_module_v2`
- `kpi_card_canasta`: módulo después de `.tab-panels`
- `tab_rows_canasta`: rows con `data-hist-*`

**Cobertura CR:** 8 cards — 2 globales + 6 canastas (B2B-OP · CUG · B2C × Eficacia + ConvRate)

---


## Week 20 · 21 Mayo 2026 · Módulo Histórico CR · "Evolución Histórica"

### ✨ Feature: Módulo Histórico Reactivo en CheckRates

**Nuevo archivo:** `historico_module_v2.py`
- Función `render_historico_cr()` — genera bloque HTML+JS completo
- Canvas con curva de tendencia (escala local) + sparkline (escala global vs target)
- 5 métricas: Actual · Máx 8W · Mín 8W · Prom 8W · Banda
- Interactivo: click en cualquiera de los 10 elementos del tab actualiza el módulo
- Colores del sistema D exactos (`render_helpers.py BANDA_COLORS`)
- Súper Crítica: badge negro/blanco · footer texto oscuro (legible sobre fondo claro)
- Título: "Evolución Histórica" (genérico, no limita a 8W)

**Modificado:** `render_cr_p1.py`
- Import `historico_module_v2`
- `render_kpi_card_eficacia`: módulo inyectado después de `.tab-panels`
- `render_kpi_card_convrate`: idem
- Rows de tabs con `data-hist-w21`, `data-hist-w20`, `data-hist-label`

**Modificado:** `render_cr_p3.py`
- Import `historico_module_v2`
- `kpi_card_canasta`: módulo inyectado después de `.tab-panels`
- `tab_rows_canasta`: rows con `data-hist-*` attrs

**Cobertura:** 8 cards — 2 globales (Hero) + 6 canastas (B2B-OP · CUG · B2C × Eficacia + ConvRate)

**Pendiente:**
- Módulo en Análisis por Hotel + Dimensión (CR)
- Módulo en RND (misma arquitectura)
- Datos históricos reales cuando estén en pickle

---

## Week 20 · 19 Mayo 2026 · MIN_CR=100 + Metodología consolidada + Fixes críticos

### 🎯 Cambios Arquitectónicos (CRÍTICOS)

**MIN_CR = Universo operacionalmente relevante:**
- ✅ `calc_cr.py` línea 62: `MIN_CR = 100` (hoteles con ≥100 CheckRates/semana)
- ✅ `calc_rnd.py` línea 85: `MIN_TRAFICO = 50000` (equivalente en RND)
- ✅ Filtro aplicado ANTES de calcular percentiles (P90)
- ✅ Elimina ruido de hoteles pequeños, una métrica única y honesta
- ✅ Impacto: Iberostar OP ahora consistente (99.25%, 3 hoteles ≥100 CR)

**P90 + Nota de Metodología:**
- ✅ `assemble_cr.py`: Agrega caja informativa sobre P90 + MIN_CR
- ✅ `assemble_rnd.py`: Idem
- ✅ Documentación clara en reportes HTML

**Destinatarios actualizados:**
- ✅ `destinatarios.md`: 28 personas (15 originales + 13 nuevos)

---

## Week 20 · 19 Mayo 2026 · Fixes críticos + creación de nuevos scripts

### 🐛 Bugs corregidos (8 total)

| Bug | Archivo | Descripción |
|---|---|---|
| #60 | `render_helpers.py` | `WEEK_NUM = "W18"` hardcodeado → `os.getenv('WEEK', 'W20')` dinámico |
| #63 | `render_*_p*.py` | Imports relativos (`from .._scripts.engine`) → absolutos (`sys.path.insert()` + `from engine`) |
| #64 | `render_rnd_p3.py`, `render_cr_p3.py` | `wow_box_canasta()` con W17/W18 hardcodeados → variables dinámicas `W{WEEK_NUM_INT-1}` / `W{WEEK_NUM_INT}` |
| #65 | Todos `render_*.py` | Keys pickle `M['global_w18']` hardcodeadas → alias dinámico `M['global_current']` post-load |
| #66 | `asset_rnd_masthead.html` | Fecha `<span>Lunes 27 De Abril De 2026</span>` hardcodeada → eliminada (permite dinamismo) |
| #67 | `assemble_rnd.py`, `assemble_cr.py` | Headers con "Week 18" en lugar de "Week 20" → sed masivo post-render |
| #68 | `calc_rnd.py` | **CRÍTICO:** `banda_rpm()` se aplicaba solo con IPM, sin parámetro `Bookings` → nunca retornaba "Sin Conversión" (11.463 hoteles perdidos) → fix: `lambda r: banda_rpm(r['IPM'], r['Bookings'])` en líneas 53 y 66 |
| #69 | `calc_rnd.py`, `calc_cr.py` | Imports relativos → absolutos: `from engine import banda_nodispo, banda_rpm` |
| #70 | `calc_rnd.py`, `calc_cr.py` | Paths datasets hardcodeados (carpeta actual) → absolutos `/mnt/user-data/uploads/` + fallback `/mnt/project/` |
| #71 | `calc_rnd.py`, `calc_cr.py` | Pickles guardados en carpeta actual → absolutos `/mnt/project/rnd_w{VOL_NUM}_data.pkl` |

### 🆕 Scripts nuevos

| Script | Descripción | Status |
|---|---|---|
| `excel_rnd_canastas.py` | Genera 3 Excels por canasta (B2C, OP, CUG) para RND · 8 pestañas c/u | ✅ Creado + testeado |
| `excel_cr_canastas.py` | Genera 3 Excels por canasta (B2C, OP, CUG) para CR · 9 pestañas c/u | ✅ Creado + testeado |

### 📝 Documentación nueva

| Archivo | Descripción |
|---|---|
| `FIXES_W20_FINAL.md` | Guía completa de todos los bugs, cambios permanentes y checklist para W21+ |

### 🗂 Archivos modificados

**Scripts de cálculo:**
- `calc_rnd.py` (líneas 6, 37, 53, 66, ~315)
- `calc_cr.py` (líneas 10, 39, 387)

**Scripts de render:**
- `render_rnd_p1.py` (imports, alias dinámicos)
- `render_rnd_p2.py` (imports, alias dinámicos)
- `render_rnd_p3.py` (imports, alias dinámicos, wow_box_canasta)
- `render_cr_p1.py` (imports, alias dinámicos)
- `render_cr_p2.py` (imports, alias dinámicos)
- `render_cr_p3.py` (imports, alias dinámicos, wow_box_canasta)

**Scripts de ensamble y Excel:**
- `assemble_rnd.py` (footer, headers fixes)
- `assemble_cr.py` (footer, headers fixes)
- `excel_rnd.py` (sin cambios críticos)
- `excel_cr.py` (sin cambios críticos)

**Assets:**
- `asset_rnd_masthead.html` (fecha hardcodeada eliminada)

**Helpers:**
- `engine.py` (banda_rpm confirmada correcta)
- `render_helpers.py` (WEEK_NUM dinámico)

### ✅ Validaciones finales W20

- ✅ Week 20 en todos los headers
- ✅ Fechas correctas: 12–18 may 2026
- ✅ **Sin Conversión: 11.463 hoteles (61.0% del P80)** ← BUG #68 corregido
- ✅ Severity IPM suma correctamente: 11.463 + 1.580 + 1.356 + 1.683 + 2.706 = 18.788
- ✅ IPM $1.183,30 = Aceptable ($650-$1500) ← Correcto
- ✅ 8 Excels generados (4 RND + 4 CR)
- ✅ Top 100 en RND canastas (10 + 40 extra)
- ✅ Top 10 en CR canastas
- ✅ WoW blocks dinámicos (W20 vs W19)

### 📊 Outputs W20 finales

**HTMLs:** 2
- `RatesNoDispo_Reporte_Editorial.html` (473 KB)
- `CheckRates_Reporte_Editorial.html` (611 KB)

**Excels:** 8
- `Analisis_Rates_NoDispo_7d.xlsx` + B2C/OP/CUG (4 total)
- `Analisis_Checkrates_7d.xlsx` + B2C/OP/CUG (4 total)

**Pickles:** 2
- `rnd_w20_data.pkl` (61 MB)
- `cr_w20_data.pkl` (20 MB)

### 🔍 Impacto

- **Criticidad:** 🔴 Alta (Bug #68 afectaba 11.463 hoteles del P80)
- **Alcance:** Global (todos los reports RND) + Canastas (B2C/OP/CUG)
- **Permanencia:** Todos los fixes son estructurales, NO se repiten en W21+

### 📋 Checklist para W21+

Ver `FIXES_W20_FINAL.md` para checklist completo de validación y configuración.

---



### 🐛 Bug corregido

| Bug | Archivo | Descripción |
|---|---|---|
| #47 | `calc_cr.py` | CONFIG decía WEEK='W18' pero generaba cr_w19_data.pkl · desalineamiento — fix: WEEK='W19' + print message correcto |

**Problema detectado:** En audit pre-W20, calc_cr.py tenía CONFIG WEEK='W18' pero leía datasets W19 y generaba cr_w19_data.pkl. Mismatch confuso.

**Solución:** 
- Línea 12: `WEEK = 'W18'` → `WEEK = 'W19'`
- Línea 381: print message → `cr_w19_data.pkl`

**Status:** ✅ Aplicado · calc_cr.py ahora 100% alineado con pipeline W19

**Impacto:** Zero impacto en W19 (pipeline funcional por casualidad). W20 comenzará con CONFIG correcta desde inicio.

### 📝 Archivos modificados
`calc_cr.py` · `PROMPT_MAESTRO_v3.md`

---

## Post W19 · Mayo 2026 · sesión fixes Excel + HTML

### 🐛 Bugs corregidos

| Bug | Archivo | Descripción |
|---|---|---|
| #28 | `excel_cr.py` | Pestañas Críticos no ordenadas por Eficacia ↑ — fix: `sort_values('Eficacia', ascending=True)` global + canastas |
| #29 | `excel_cr.py` | `Por Corporativo` (global + canastas) sin columna Channel — fix: groupby `hotel_channel_map` → columna `Channels` con valores únicos |
| #30 | `excel_rnd.py` | Columnas `RPM` y `BandaRPM` visibles en Excel — fix: `.rename()` → `IPM (USD/M)` y `Banda IPM` en todas las hojas |
| #31 | `excel_rnd.py` | Colores de banda IPM no se aplicaban — fix: `banda_col2` en `add_table()` para colorear dos columnas de banda por fila |
| #32 | `excel_rnd.py` | `Sin Conversión` sin color en `BAND_FONTS` — fix: `Font(..., color='8A8377')` |
| #33 | `render_cr_p2.py` | Header tab hotel `'Checkrates'` → `'CR Únicos'`, `'ConvRate'` → `'Conv Rate'` (5 ocurrencias) |
| #34 | `render_cr_p2.py` | Header tabla dim `'CR'` → `'CR Únicos'`, `'CV'` → `'Conv Rate'` (Corp + Dest + Channel) |
| #35 | `render_cr_p3.py` | Header dim canastas `'CR'` → `'CR Únicos'`, `'CV'` → `'Conv Rate'` |
| #36 | `calc_rnd.py` | `ZeroDivisionError` en print final cuando dataset W18 vacío — fix: guard `if t17>0` |

### 🗂 Archivos modificados
`excel_cr.py` · `excel_rnd.py` · `render_cr_p2.py` · `render_cr_p3.py` · `calc_rnd.py`

---
## Week 19 · Mayo 2026 · sesión fixes visuales + features

### 🐛 Bugs corregidos

| Bug | Archivo | Descripción |
|---|---|---|
| #16 | `render_mail_v3.py` | Dependencia de `metrics_recalc.pkl` inexistente |
| #17 | `excel_rnd.py` | Path hardcodeado `/home/claude/final_w18/rnd_w19_data.pkl` |
| #18 | `build_package.py` | ZIP con prefijo `Price_WNN/` |
| #19 | `calc_rnd.py` | `df17` cargaba W19 en lugar de W18 — WoW era 0 |
| #20 | `render_rnd_p1.py` | Card IPM: condición `ipm_w17 > 0` siempre False (columna `IPM_W17` inexistente) |
| #21 | `render_rnd_p3.py` | `_enrich_wow` buscaba `IPM_W17` en vez de `IPM_W18` |
| #22 | `render_rnd_p1/p2/p3.py` | WoW IPM en USD absoluto (`↑$105`) — fix: convertir a % |
| #23 | `render_rnd_p1/p2/p3.py` | WoW %NoDispo sin unidad (`+4,58`) — fix: sufijo `pp` |
| #24 | `render_cr/rnd_p1.py` | Header masthead "Week 18" hardcodeado — fix: leer `VOL_NUM` del pickle |
| #25 | `render_cr_p2.py` | `_fmt_wow_cv` faltaba — syntax error en concatenación |
| #26 | `calc_cr.py` | Pickle salía como `cr_w18_data.pkl` — fix: `cr_w19_data.pkl` |
| #27 | `calc_cr.py` | `df17` buscaba `Dataset_CheckRates_W17.xlsx` inexistente — fix: W18 |

### ✨ Nuevas features

#### WoW con unidades claras en RND (global + canastas)
- `%NoDispo WoW` siempre con sufijo `pp`
- `IPM WoW` en porcentaje relativo (no USD absoluto)
- Aplica en p1 (hero), p2 (dim global), p3 (canastas)

#### Tabla Análisis por Dimensión RND — 2 columnas WoW separadas
- Orden: `Nombre · %NoDispo · WoW · IPM · WoW`
- Grid: `1fr 62px 36px 58px 36px`
- `asset_rnd_head.html` CSS actualizado

#### WoW ConvRate en tabla Análisis por Dimensión CR
- Orden: `Nombre · CR únicos · BKGS · ConvRate · WoW · Eficacia · WoW`
- Grid: `1fr 80px 60px 68px 38px 68px 38px`
- Helper `_fmt_wow_cv` (pp) en `render_cr_p2.py`

#### Tab Hotel Conv Rate — filtro Sin Conversión
- Solo `Bookings > 0` — Sin Conversión tiene su tab propia
- Fix en `render_cr_p1.py` y `calc_cr.py`

#### Plan de Acción + Sistema Carryover
- `template_seguimiento.py`: genera bloque HTML de carryover
- `build_package.py`: genera `plan_seguimiento_WNN.md`
- Lógica: ES/MP → `## OPEN` (auto), QW → `## PENDIENTE_QW` (revisión manual)
- Visual: separador "📋 Carryover", badge `CARRYOVER` gris, badge `desde WNN`
- Aplica en global + canastas de CR y RND

#### Estructura ZIP repo corregida
- `_governance/_seguimiento/plan_seguimiento_WNN.md`
- Datasets crudos incluidos automáticamente

#### Semana dinámica en masthead
- `VOL_NUM`, `PERIODO`, `MES_AÑO` almacenados en pickle y leídos en render p1

### 📊 KPIs W19 (valores finales post-fixes)
| Métrica | W19 | WoW |
|---|---|---|
| % NoDispo (P80) | 2,42% | ▼ 0,55pp |
| IPM (P80) | $597 | ▼ 7,4% |
| Eficacia CR (P80) | 93,88% | ▼ 0,25pp |
| Conv Rate CR (P80) | 1,32% | ▲ 0,05pp |

### 🗂 Archivos modificados
`calc_cr.py` · `calc_rnd.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `asset_rnd_head.html` · `build_package.py` · `template_seguimiento.py` · `MAIL_DRAFT_FLUJO.md`

---

## Week 19 · Mayo 2026 · sesión inicial pipeline

### Nuevas features
- `build_package.py` Paso 6: genera `index.html` hub + `Price_WNN.zip`
- `render_mail_v3.py` v3.2: sin `metrics_recalc.pkl`, CONFIG SEMANAL, marcadores DRAFT

### Fixes
- `excel_rnd.py` path pickle · ZIP sin prefijo de carpeta

### Incidencia dataset RND
- Primera versión con 5 columnas → solicitado corregido antes de pipeline

---

## Week 18 · Mayo 2026

### Bugs #8–#15 corregidos (ver versiones anteriores)
### Features CR: WoW neutro, Third Party violet, WoW hotel canasta y channel
### Features RND: calc_rnd reescrito, WoW real, MIN_T=500K, 4 cols panel-row

---

## Week 17 · Abril 2026
- Bandas D, Sin Conversión separada, pills Súper Crítica, Channel agrupado CR, tabs hero

---

## [W20-s14] · 23 Mayo 2026 · Fixes visuales UI/UX batch 2

### Fixes aplicados
- **Aceptable naranja**: `gauge_5levels` y `historico_module_v2.py` actualizados → `#F59E0B` sólido en todos los contextos (el violet `#5C469C` era incorrecto)
- **Badge hotel suprimido**: KPI cards CR y RND — tabs Hotel no muestran badge de banda (ruido visual). Afecta `render_cr_p1.py`, `render_rnd_p1.py`, `render_cr_p3.py`, `render_rnd_p3.py`
- **Badge channel en dimensiones CR**: `render_chan_table` en `render_bloque_dimensiones_cr` ahora muestra badge `BandaEficacia` al lado del nombre del canal
- **`_mini_badge` y `mini_badge` en render_helpers**: funciones centralizadas accesibles vía `from render_helpers import *`
- **Opción C searchbox**: `position:relative` en `.sb-inline-wrap`, input ancho `120px` (antes `88px`)
- **Canastas en KPI cards globales**: `panel_html = col1 + col2 + rest` (en lugar del vacío `rows_html`) — corrige que B2B (OP) no aparecía en el tab Canasta
- **Header repetido al final de tablas de análisis**: `show_header=False` en `hidden_rows` — fix aplicado en `render_top_table_cr` y `render_top_table`
- **IPM sin decimales**: `es_num2()` local retorna `int(round(v))` en `render_rnd_p2.py` y `render_rnd_p3.py`
- **Botón × para limpiar searchbox**: CSS `.sb-clear-btn` + JS `clearBtn` en `attachSearchbox`; elemento `<button>` inyectado en 14 `sb-inline-wrap`
- **Autocomplete solo tab activo**: `buildLabels()` usa `getActiveRows(false)` — evita cross-card contamination
- **Doble wrapper div en canastas RND**: eliminado div duplicado en `kpi_card_canasta` return
- **REVISAR naranja**: `gauge_5levels` → `#F59E0B` sólido (antes ocre `#D4A878`)
- **Orden col1(1-5)/col2(6-10)**: KPI cards globales y canastas — `_render_panel_top_table_cr/rnd` y `tab_rows_canasta`
- **Badges en todas las listas**: todas las dimensiones (corp/dest/hotel/país/channel/canasta) con badge de banda

### Archivos modificados
`render_helpers.py` · `historico_module_v2.py` · `historico_module_rnd.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `template_severity.py`


---

## [W20-s15+] · 23 Mayo 2026 · Searchbox Prop A+D + wow_pill V1

### 🔍 Searchbox — migración a Prop A + Prop D (3 modos JS)

Rediseño completo del sistema de búsqueda cliente-side. Objetivo: eliminar duplicación y tener un único punto de entrada por contexto.

#### 3 modos de searchbox (JS Engine W21)

| Modo | Trigger | Dónde |
|---|---|---|
| **Pill** (Prop A) | `input[data-sb-pill]` | KPI cards hero + canastas — pill redondeada en `tabs-row` |
| **Header** (Prop D) | `input[data-sb-table]` | Bloques hotel + dim — integrado en primera columna del header de tabla |
| **Legado** | `input[data-sb-scope]` | Compatibilidad retroactiva (sin cambios) |

#### Nuevas funciones en `render_helpers.py`

```python
wow_pill_html(wow_val, unit='pp', prefix_pos='↑', prefix_neg='↓')
# Pill verde/rojo/gris border-radius:20px según signo del delta

searchbox_pill_html(input_id, accent_color, placeholder, count_id)
# Genera .sb-pill-wrap para tabs-row de KPI cards (Prop A)

searchbox_header_html(input_id, accent_color, placeholder, th_id)
# Genera .sb-th para primera columna del header de tabla (Prop D)
```

#### wow_pill V1 — pill semántica en KPI-top

La pill WoW ahora aparece junto al valor principal (debajo del badge de banda) en todas las cards KPI hero y canastas. Lógica de orientación:

| Métrica | Verde si | Implementación |
|---|---|---|
| Eficacia / ConvRate / IPM | Delta > 0 (sube) | `wow_pill_html(delta)` |
| %NoDispo | Delta < 0 (baja) | `wow_pill_html(-delta, prefix_pos='↓', prefix_neg='↑')` |

#### IDs canónicos post-migración

**Global — bloques hotel y dim (Prop D, uno por tab):**
| Tab | CR | RND |
|---|---|---|
| Hotel Críticos | `sb-h-crit` | `sb-rh-crit` |
| Hotel Bajo Rend | `sb-h-br` | `sb-rh-br` |
| Hotel Sin Conv | `sb-h-sc` | `sb-rh-sc` |
| Hotel Menor CV | `sb-h-mcv` | — |
| Hotel DNC | — | `sb-rh-dnc` |
| Dim Corporativo | `sb-d-corp` | `sb-rd-corp` |
| Dim Destino | `sb-d-dest` | `sb-rd-dest` |
| Dim Channel | — (no filtrable) | — |
| Dim País | — | `sb-rd-pais` |

**Canastas (por `idx_str` = `op` / `cug` / `b2c`):**
| Contexto | CR | RND |
|---|---|---|
| KPI card Ef/NoDispo | `sb-kpi-{idx}-ef` | `sb-kpi-{idx}-nd` |
| KPI card CV/IPM | `sb-kpi-{idx}-cv` | `sb-kpi-{idx}-ipm` |
| Hotel tab-key | `sb-{idx}-h-{t_key}` | `sb-{idx}-rh-{t_key}` |
| Dim tab-key | `sb-{idx}-d-{t_key}` | `sb-{idx}-rd-{t_key}` |

#### Cambios eliminados (IDs legacy)
Los `sb-inline-wrap` con IDs `sb-cr-hotel`, `sb-cr-dim`, `sb-rnd-hotel`, `sb-rnd-dim`, `sb-{idx}-hotel`, `sb-{idx}-dim` fueron eliminados de los `tabs-row` de bloque. El JS legado (`data-sb-scope`) sigue funcionando para las KPI cards que lo usen.

#### Regla definitiva: cero duplicación
- `sb-inline-wrap` exteriores en `tabs-row` de bloque → **eliminados**
- Cards KPI → `searchbox_pill_html` (Prop A, pill en la fila de tabs)
- Tablas hotel + dim → `searchbox_header_html` en col1 de header (Prop D)

#### data-lbl en filas
Todas las filas de tablas hotel y dim ahora llevan `data-lbl="nombre corp"` para que `attachTable` (modo Prop D) filtre por ese atributo en lugar de `data-hist-label`.

### 🎨 fix A1 · Empty state visible
Cuando ninguna fila coincide con la búsqueda, aparece un mensaje `Sin resultados para «query»` en vez de tabla vacía silenciosa.

### 🎨 fix A2 · Reset grid al cambiar tab
El listener `change` en radios limpia todos los inputs de searchbox y resetea el grid a `1fr 1fr` al cambiar de pestaña.

### 📁 Archivos modificados
`render_helpers.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `render_cr_p1.py` · `render_rnd_p1.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_cr_p3.py` · `render_rnd_p3.py`

### Commits
- `b121f55` · feat(W20s): searchbox Prop A+D + wow_pill V1 · CR+RND global+canastas
- `97e9d07` · regen(W20): reportes editoriales CR+RND con searchbox Prop A+D · wow_pill V1


---

## W20 · Post-sesión 15+ · Fixes UI/UX · Mayo 2026

### 🐛 Bugs corregidos (commits b63591f → 4289f22)

| # | Commit | Descripción |
|---|---|---|
| 48 | b63591f | Audit colores severity: `#EDE8F7` (violeta Aceptable viejo) → `#FEF9C3` en p3 + `#085041` (verde viejo) → `#1A6B4A` en módulos históricos |
| 49 | b63591f | `attachTable` bug raíz: `var dropdown` declarado DESPUÉS del `clearBtn` listener → `dropdown=undefined` en runtime. Fix: declarar antes. CR+RND |
| 50 | 1b6c53e | Badge NoDispo ausente en tab Hotel (RND): exclusión `if t_key == 'hotel'` eliminada de `_bnd_nd` en `render_rnd_p1.py` |
| 51 | 1b6c53e | Resumen Ejecutivo: títulos sin bold → `font-weight:600` en `<span>` de `render_finding` (`template_resumen.py`) |
| 52 | 1b6c53e | Análisis por hotel horizontal: `attachSearchbox` sobreescribía `gridTemplateColumns:1fr 1fr` en todos los `.kpi-tab-rows`. Fix: eliminar esa línea de JS en ambos assets |
| 53 | 1b6c53e | Análisis por dimensión a 2 columnas: `render_top_dimension` y `panel_for_dim` en CR y RND pasaban `df1` (5 filas) en lugar de `df_all` (10). Fix: tabla única con `rows-more` en filas 5-9 |
| 54 | 6f00853 | `.canasta-alert-bar` background `#EDE8F7` → `var(--paper-soft)` en `asset_cr_head.html` |
| 55 | 6f00853 | `render_rnd_p3.py` dict `SOLID`: `Exitosa #085041→#1A6B4A`, `Aceptable #5C469C→#713F12`, `Revisar #A86A1D→#C2410C`, `Súper Crítica #161616→#7F1D1D` (corregido luego a `#FFFFFF`) |
| 56 | 3785bff | `attachPill` reescritura limpia: código huérfano del `showEmpty` (cleanup anterior) dejaba llaves desbalanceadas que cerraban la función antes del bloque `var dropdown` + `buildDD` → autocomplete no funcionaba. Fix: reescritura completa sin código huérfano, 1 listener `input` unificado |
| 57 | 7c2c556 | Barra de progreso Revisar: `#D4A878` (ocre) → `#F97316` (naranja) en `render_cr_p2.py` (3x) y `render_rnd_p2.py` (4x). Los badges bg/fg ya eran correctos |
| 58 | 7c2c556 | Layout horizontal análisis por hotel y dimensión: wrappers `<div>` sin clase tomaban `display:flex` del selector `.tab-panel > div:not(...)`. Fix: `class="tbl-wrap"` + `:not(.tbl-wrap)` en selector + `.tbl-wrap{display:block}` en ambos assets |
| 59 | 4289f22 | Súper Crítica rosa → negro sólido: `#FECACA`/`#7F1D1D`/`#FCEBEB` → `bg:#161616 fg:#FFFFFF` en 8 archivos (`render_cr_p2`, `render_rnd_p2`, `template_severity`, `render_helpers.BANDA_COLORS`, `render_cr_p3`, `render_rnd_p3`, `historico_module_v2`, `historico_module_rnd`) |

### 📋 Paleta canónica definitiva (post sesión Mayo 2026)

| Banda | bg | fg | bd/barra |
|---|---|---|---|
| Exitosa | `#E1F5EE` | `#1A6B4A` | `#1A6B4A` |
| Aceptable | `#FEF9C3` | `#713F12` | `#FCD34D` |
| Revisar | `#FED7AA` | `#C2410C` | `#F97316` |
| Crítica | `#FCE4F1` | `#99162B` | `#C0392B` |
| Súper Crítica | `#161616` | `#FFFFFF` | `#DC2626` |
| Sin Conversión | `#F2EEE6` | `#5F5E5A` | `#8A8377` |

### ⚠️ Pendientes para próxima sesión

- Colores en canastas CR y RND (p3) — no verificados visualmente
- Módulo histórico: validar que Súper Crítica aparece negro en canvas/sparkline
- Top 100 en análisis por hotel y dimensión: verificar que "Ver 5 más" funciona correctamente en todas las tabs
- `extract_hist_data.py` para automatizar actualización del histórico W21+

### 📁 Archivos modificados en esta sesión

`asset_cr_head.html` · `asset_rnd_head.html` · `render_cr_p1.py` · `render_rnd_p1.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_cr_p3.py` · `render_rnd_p3.py` · `template_resumen.py` · `template_severity.py` · `render_helpers.py` · `historico_module_v2.py` · `historico_module_rnd.py`


---

## Sesión post-W20 · Mayo 2026 · Refactoring Global vs Canastas (Sprint A + B + fixes visuales)

### Contexto
Sesión de análisis, refactoring y fixes de consistencia visual/funcional entre el reporte global (p1/p2) y las canastas (p3), aplicada sobre CR y RND. Incluye 3 commits: pipeline W20 regenerado, fixes layout KPI cards, y fixes Análisis por Hotel/Dimensión.

**Commits:**
- `8e934bdf` · feat: Week 20 · RatesNoDispo + CheckRates + hub index · 11-17 may 2026 (pipeline completo + scripts sprint)
- `b3daea6a` · fix(kpi-cards): igualar layout top-section global vs canastas CR+RND
- `e61c87ce` · fix(canastas): igualar Análisis por Hotel y Dimensión con global CR+RND

---

### Sprint A · Fixes rápidos (Bugs detectados en análisis de divergencias)

| Bug | Archivo(s) | Descripción |
|---|---|---|
| A | `render_cr_p3.py`, `render_rnd_p3.py` | Headers de columna (`Severity / Métrica / WoW`) faltaban en tabs de KPI cards de canastas → agregado en `tab_rows_canasta` |
| B | `render_cr_p1.py` | Caption `"vs sem. ant."` faltaba en hero global CR (Eficacia + ConvRate) → agregado con pill WoW inline |
| C | `render_cr_p3.py` | `wow_pill_html` parseaba `wow_str` con string manipulation frágil → reemplazado por parámetro `wow_delta` (float) directo en `kpi_card_canasta` |
| J | `render_cr_p3.py`, `render_rnd_p3.py` | Regex del listener `render_historico_seccion_cr/rnd` no matcheaba `canasta-{idx}-hotel-cr` (requería guión extra) → quitar guión final del grupo |

---

### Sprint B · Centralización de helpers en `render_helpers.py`

#### Nuevas funciones

| Función | Descripción |
|---|---|
| `tab_column_header(cols, widths)` | Header de columnas para tabs de KPI cards — reemplaza 4 strings `_tab_hdr` hardcodeados en p1 CR y RND |
| `make_wow_pill_row(wow_v, is_mejora_si_positivo, threshold)` | Pill WoW compacta para filas de tabs — unifica el sistema CR (inline styles) con RND (CSS classes) |
| `wow_box(..., compact=False/True)` | Parámetro `compact` añadido — elimina `wow_box_canasta()` local de CR p3 y RND p3 |

#### `wow_box(compact=True)` — elimina duplicación
- `wow_box_canasta()` local en `render_cr_p3.py` y `render_rnd_p3.py` **eliminada**
- `kpi_card_canasta()` en ambos usa `wow_box(..., compact=True)` con semanas dinámicas

#### `tab_column_header()` — reemplaza hardcoded headers
- CR p1: `_tab_hdr` Eficacia (`1fr 80px 54px 40px`) y ConvRate (`1fr 80px 68px 40px`)
- RND p1: `_tab_hdr` NoDispo (`1fr 72px 54px 40px`) e IPM (`1fr 72px 54px 40px`)
- CR p3 y RND p3: `tab_rows_canasta` ahora inyecta header vía esta función

#### `make_wow_pill_row()` — unificación pills CR→RND
- CR p1 (tabs destino/corp/hotel Eficacia + ConvRate): migrado de 8 líneas de `<em style=...>` inline
- CR p3 `tab_rows_canasta`: idem

---

### Fix searchbox canastas — scope aislado (CR p3)

**Problema raíz:** las cards KPI de canastas CR usaban `<div class="tab-panel">` genérico. El CSS del asset head activa panels con selector `~ .tab-panels .tab-panel[data-tab="destino"]` sin scope → el `getActivePanel()` del searchbox podía encontrar el panel del global en lugar del de la canasta.

**Solución:** migrar panels de canastas CR al patrón JS aislado de RND:
- Panels: `class="tab-panel"` → `class="tp-{card_id}"` con `display:none` inicial
- Activación: CSS radio → JS scoped a `id="kpi-{card_id}"`
- `getActivePanel()` en ambos asset heads: detecta primero panels `.tp-*` (JS-activados) antes de recurrir a `.tab-panel` (CSS-activados)
- `initPanel` también inicializa panels `.tp-*` al cargar

**Archivos:** `render_cr_p3.py` · `asset_cr_head.html` · `asset_rnd_head.html`

---

### Fix layout KPI cards — igualar global vs canastas

Todas las cards KPI (hero global + canastas) ahora tienen el mismo layout:

| Propiedad | Antes (canastas) | Ahora |
|---|---|---|
| `font-size` valor | `36px` | `40px` |
| `align-items` fila top | `center` | `flex-start` |
| `gap` fila top | `12px` | `14px` |
| Badge + "vs sem ant" | columna vertical | valor grande + badge a la derecha, "vs sem ant" debajo del número |
| `tabs-row` clase (RND) | sin clase, `gap:0` | `class="tabs-row"`, `gap:2px` |
| `panels` div clase (RND) | sin `class` | `class="tab-panels"` |

Bonus: "vs sem. ant." agregado al **global RND** (solo lo tenía CR global).

---

### Fix Análisis por Hotel y por Dimensión — canastas CR + RND

#### Análisis por Hotel

| Sección | Antes | Ahora |
|---|---|---|
| CR hotel — Severity | No había columna separada | Columna `Severity` con badge paleta D · grid `1fr 80px 58px 58px 38px` |
| RND hotel — Severity | Badge inline dentro del nombre | Columna `Severity` separada · grid `1fr 80px 62px 36px 58px 36px` |
| RND hotel — columnas | Hotel · %NoDispo · IPM · WoW | Hotel · **Severity** · %NoDispo · **WoW** · IPM · **WoW IPM** |

#### Análisis por Dimensión

| Sección | Antes | Ahora |
|---|---|---|
| CR dim — Severity | Inline dentro del nombre (badge + label) | Columna `Severity` separada · grid con columna extra `80px` |
| RND dim — Severity | Badge inline | Columna `Severity` separada · grid con columna extra `80px` |
| CR dim — visibilidad | 10 filas visibles, resto `sb-hidden` | **5 visible + 5 `rows-more` + 90 `sb-hidden`** |
| RND dim — visibilidad | Idem | Idem |
| Botón "Ver 5 más" | No existía en dim de canastas | **Agregado** en CR y RND canastas |

### Archivos modificados
`render_helpers.py` · `render_cr_p1.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p3.py` · `asset_cr_head.html` · `asset_rnd_head.html`

---

## Sesión W20 · Mayo 2026 · Fixes UI/UX + Pipeline W20 con WoW real

### Contexto
Sesión de fixes visuales y UI/UX extensa antes de ejecutar el pipeline W20 final con datasets W19 reales. 13 commits aplicados el 24/05/2026.

### Bugs corregidos

| # | Commit | Archivo(s) | Descripción |
|---|---|---|---|
| 60 | 0d17c28d | `render_helpers.py` | Searchbox header: `width:120px→72px`, `padding:3px→2px 6px`, `svg:12→10px` — primera reducción |
| 61 | 0020be6c | `render_rnd_p2.py` | Badge Severity como columna en `_render_dim_table_rnd` — grid `1fr 62px→1fr 72px 62px`, header "Severity" separado del nombre |
| 62 | 0020be6c | `render_cr_p2.py` | Badge Severity como columna en `_render_dim_table_cr` — grid actualizado, header "Severity" independiente |
| 63 | 0020be6c | `render_cr_p2.py` | Searchbox `padding:4px 0` y `align-items:end` en header de tabla dimensión CR para separarlo de la línea |
| 64 | 610a9f23 | `render_helpers.py` | Searchbox header: igualar a pill → `width:48px` (en route hacia 100px final) |
| 65 | 5d4b5713 | `render_cr_p1.py` | Headers de columna (Severity/Eficacia/WoW) en tabs de cards KPI hero CR |
| 66 | b01b5834 | `render_rnd_p1.py` | Headers de columna (%NoDispo/IPM/WoW) en tabs de cards KPI hero RND |
| 67 | 58cd2082 | `render_rnd_p2.py` | `margin-top:48px` en `<section id="severity-combinada">` — separación visual RE/Severity en RND |
| 68 | 3716844c | `template_resumen.py` | `font-weight:400` en div card del RE — cancela herencia bold del header-overline |
| 69 | da51e4b3 | `asset_cr_head.html` | Eliminar regla CSS amber genérica: `.tab-panel div span:not(.tab-key){color:var(--amber)}` → `.tab-panel div span.tab-val` (más específica, no afecta kpi-tab-rows) |
| 70 | 34a5b69e | `render_helpers.py` | Searchbox header: `width:100px`, `padding:3px 8px`, `svg:12px` — igualar exactamente a searchbox pill |
| 71 | 956c55e0 | `render_cr_p1.py` | Grid Conv Rate: `54px→68px` en header y filas — "Conv Rate" cabe en una línea |
| 72 | df137426 | `render_rnd_p1.py` | Headers RND corregidos: card izquierda (NoDispo) → `%NoDispo`, card derecha (IPM) → `IPM` (estaban al revés) |
| 73 | 65f89f39 | `render_rnd_p2.py` | `cols_dnc`, `cols_sc`, `cols_crit` en análisis hotel RND: agregar columnas IPM + WoW (antes solo tenían %NoDispo) |
| 74 | a64115d4 | `asset_cr_head.html` | Eliminar segunda instancia de la regla CSS: `.tab-panel div span{color:#5C469C !important}` — esta tenía `!important` y ganaba sobre cualquier inline style, causando que todos los valores en tabs aparecieran en violeta |
| 75 | 049b6fb6 | `render_helpers.py` | Searchbox header: envolver `sb-pill` en `<div style="display:flex;align-items:center;">` — sin este wrapper el pill se estiraba al 100% de la primera columna del grid |

### Cambios de diseño/arquitectura

#### Severity como columna independiente
Badge de banda movido de inline-junto-al-nombre a **columna separada** en todas las tablas de análisis:
- CR: análisis por hotel (4 tabs) y análisis por dimensión
- RND: análisis por hotel (4 tabs: Críticos, Demanda NC, Bajo Rendimiento, Sin Conversión) y análisis por dimensión

#### Headers de columna en tabs de cards KPI
Agregado header de columna antes de las filas de datos en los tabs:
- CR hero: `'' | Severity | Eficacia | WoW` y `'' | Severity | Conv Rate | WoW`
- RND hero: `'' | Severity | %NoDispo | WoW` y `'' | Severity | IPM | WoW`

#### Top 50 → Top 100
Todos los callouts de descarga Excel actualizados: 8 instancias en CR (p2+p3) y RND (p2+p3).

#### Searchbox estandarizado
`searchbox_header_html` (tablas análisis) ahora usa exactamente los mismos parámetros de tamaño que `searchbox_pill_html` (tabs de cards KPI): svg 12px, padding 3px 8px, input 100px, wrapper div flex.

### Paleta canónica actualizada

**Súper Crítica** cambiada de negro sólido a gris cálido pastel (mayo 2026):
| | Antes | Ahora |
|---|---|---|
| bg | `#161616` negro | `#EDECEC` gris claro cálido |
| fg | `#FFFFFF` blanco | `#4A3F3F` gris oscuro cálido |
| bd | `#DC2626` | `#9B2222` |
| bar | `#DC2626` | `#C0392B` |

### Pipeline W20 ejecutado (24/05/2026)
- Datasets: W20 + W19 (WoW real por primera vez)
- WoW RND: %NoDispo W19=2,33% → W20=2,74% (+0,41pp)
- WoW CR: Eficacia W19=93,30% → W20=92,75% (−0,55pp), ConvRate W19=1,14% → W20=1,19% (+0,05pp)

### Archivos modificados en esta sesión
`asset_cr_head.html` · `render_helpers.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `template_resumen.py` · `template_severity.py` · `historico_module_v2.py` · `historico_module_rnd.py`

