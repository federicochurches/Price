# _scripts · Pipeline de generación de reportes

Pipeline Python para generar los Reportes Editoriales (HTML), Excels de Análisis, Hub index y ZIP de release a partir de los datasets crudos semanales.

---

## 📌 Última semana publicada

**Week 20 · 11-17 may 2026 · May 2026**


## 📊 Estado del pipeline · Week 20 (ejecutado 24/05/2026)

| Métrica | W19 | W20 | WoW |
|---|---|---|---|
| Eficacia CR global | 93,30% | 92,75% | −0,55pp |
| ConvRate CR global | 1,14% | 1,19% | +0,05pp |
| %NoDispo RND global | 2,33% | 2,74% | +0,41pp |
| IPM RND global | 99 | .217 | +144% |
| Hoteles P80 CR | — | 2.080 | — |
| Hoteles P80 RND | — | 19.456 | — |

**Datasets W20:**  (72.282 filas) +  (149.349 filas)  
**Datasets W19:**  (67.444 filas) +  (157.994 filas)

---

## 🎨 Paleta canónica de bandas (post W20 sesión Mayo 2026)

**Fuente de verdad:** `BANDA_COLORS` en `render_helpers.py`

| Banda | bg | fg | bd/barra | Notas |
|---|---|---|---|---|
| Exitosa | `#E1F5EE` | `#1A6B4A` | `#1A6B4A` | Verde teal |
| Aceptable | `#FEF9C3` | `#713F12` | `#FCD34D` | Amarillo |
| Revisar | `#FED7AA` | `#C2410C` | `#F97316` | Naranja |
| Crítica | `#FCE4F1` | `#99162B` | `#C0392B` | Rosa/rojo |
| Súper Crítica | `#EDECEC` | `#4A3F3F` | `#9B2222` bd / `#C0392B` bar | Gris cálido (no negro) |
| Sin Conversión | `#F2EEE6` | `#5F5E5A` | `#8A8377` | Gris muted |

**Reglas de uso:**
- El **badge** (pill de banda) usa `bg` + `fg`
- La **barra de progreso** en Severity usa `bd/barra`
- `#5C469C` (violet) es el accent de CR — válido en subheads, tabs, accent. NO en severity
- `#EA0074` (magenta) es el accent de RND — igual
- `#4FC3F4` (cyan) es SOLO para IPM accent en módulos históricos RND y label Third Party en CR

## 🔧 Sistema JS de searchbox (post W20 sesión 15+)

**Tres modos — un input por contexto:**

| Modo | Atributo | Dónde |
|---|---|---|
| Pill (Prop A) | `data-sb-pill` | KPI cards hero + canastas |
| Header (Prop D) | `data-sb-table` | Tablas hotel + dim |
| Legado | `data-sb-scope` | Compatibilidad |

**Funciones JS en assets:**
- `attachPill(input)` — filtra `[data-hist-label]` en panel activo + dropdown autocomplete
- `attachTable(input)` — filtra `[data-lbl]` en wrapper `.tbl-wrap` + dropdown autocomplete
- `attachSearchbox(scope, id, counter)` — modo legado

**Regla crítica de layout:** Los wrappers de tablas deben tener `class="tbl-wrap"` para evitar que el selector `.tab-panel > div:not(...)` les aplique `display:flex`. El CSS define `.tbl-wrap{display:block}`.


---

## 📋 Inventario de archivos

### Cálculo y agregación
| Archivo | Función |
|---|---|
| `engine.py` | Funciones core: bandas (`banda_nodispo`, `banda_rpm`, `banda_eficacia`, `banda_convrate`), agregaciones, Pareto P80, channel grupo |
| `render_helpers.py` | Helpers de formato y UI: `fmt_int_es`, `fmt_pct2`, `fmt_num2`, `fmt_big`, `clean_hotel_name`, `truncate`, `banda_pill`, `gauge_5levels`, `wow_box`, `wow_pill_html`, `searchbox_pill_html`, `searchbox_header_html`, `mini_badge`, `target_caption` |
| `calc_rnd.py` | Calcula métricas globales y por canasta RND → guarda `rnd_wNN_data.pkl` |
| `calc_cr.py` | Calcula métricas globales y por canasta CR → guarda `cr_wNN_data.pkl` |
| `areas_catalogo.py` | Catálogo Áreas Accountable v2 + función de mapeo |

### Renderers HTML por sección
| Archivo | Genera |
|---|---|
| `render_rnd_p1.py` | Masthead + Hero KPI + Alertas globales (RND) → `part1_rnd.html` |
| `render_rnd_p2.py` | Resumen Ejecutivo + Severity + Análisis por hotel + Dimensión (con módulos históricos) + Plan (RND) → `part2_rnd.html` |
| `render_rnd_p3.py` | Análisis por Canasta RND (B2B-OP · CUG · B2C) → `part3_rnd.html` |
| `render_cr_p1.py` | Masthead + Hero KPI Eficacia/ConvRate (CR) → `part1_cr.html` |
| `render_cr_p2.py` | Resumen Ejecutivo + Alertas + Severity + Análisis por hotel + Dimensión + Plan (CR) → `part2_cr.html` |
| `render_cr_p3.py` | Análisis por Canasta CR → `part3_cr.html` |

### Helpers de template
| Archivo | Función |
|---|---|
| `template_resumen.py` | `render_resumen_ejecutivo(findings, accent_color, scope, header_title)` |
| `template_alertas.py` | `render_alertas_block(scope_text, accent, card_h, card_d, card_c)` |
| `template_severity.py` | `render_severity_block(...)` + `render_severity_2cols(...)` + `LEVELS_*` predefinidos |
| `historico_module_v2.py` | `render_historico_cr(metric_type, banda_actual, val_actual, canvas_id, current_week)` — módulo Evolución Histórica para CheckRates (Eficacia + ConvRate) · usado en Hero, canastas, hotel, dim |
| `historico_module_rnd.py` | `render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id, current_week)` — módulo Evolución Histórica para RatesNoDispo (NoDispo + IPM) · usado en Hero, canastas, hotel, dim |

### Ensamblado y Excel
| Archivo | Genera |
|---|---|
| `assemble_rnd.py` | Une part1+part2+part3 RND + footer → `Supply_RatesNoDispo_WNN.html` |
| `assemble_cr.py` | Une part1+part2+part3 CR + footer → `Supply_CheckRates_WNN.html` |
| `excel_rnd.py` | 4 Excels RND (global 33 pests. + 3 canasta 8 pests. c/u) |
| `excel_cr.py` | 4 Excels CR (global 37 pests. + 3 canasta 9 pests. c/u) |

### Mail, hub y package
| Archivo | Genera |
|---|---|
| `render_mail_v3.py` | Mail semanal HTML (`Mail_WNN.html`) |
| `build_package.py` | **index.html del hub** + ZIP con estructura completa del repo listo para commit |

---

---

## 📈 Módulos Históricos · Evolución Semanal (W20+)

Bloque HTML+JS reactivo que muestra la tendencia de 8 semanas de una métrica dentro de cada card KPI.

### Cobertura (12 módulos por reporte tras sesión 4)

| Scope | CR (Eficacia + ConvRate) | RND (NoDispo + IPM) |
|---|---|---|
| **Global** (Hero) | `hcr-global-ef` · `hcr-global-cv` | `hrnd-global-nd` · `hrnd-global-ipm` |
| **B2B-OP** (canasta) | `hcr-op-ef` · `hcr-op-cv` | `hrnd-op-nd` · `hrnd-op-ipm` |
| **CUG** (canasta) | `hcr-cug-ef` · `hcr-cug-cv` | `hrnd-cug-nd` · `hrnd-cug-ipm` |
| **B2C** (canasta) | `hcr-b2c-ef` · `hcr-b2c-cv` | `hrnd-b2c-nd` · `hrnd-b2c-ipm` |
| **Análisis por hotel** | `hcr-hotel-ef` · `hcr-hotel-cv` ✅ W20s4 | `hrnd-hotel-nd` · `hrnd-hotel-ipm` |
| **Análisis por dimensión** | `hcr-dim-ef` · `hcr-dim-cv` ✅ W20s4 | `hrnd-dim-nd` · `hrnd-dim-ipm` |

### Componentes de cada módulo

- **Canvas** — curva de tendencia con escala LOCAL al elemento, target line, labels X dinámicos
- **5 métricas** — Actual · Máx 8W · Mín 8W · Prom 8W · Banda
- **Sparkline** — 8 barras en escala GLOBAL vs target
- **Interactividad** — click en cualquier fila de la tabla actualiza canvas, métricas y banda

### Uso en render scripts

```python
from historico_module_v2 import render_historico_cr

hist_html = render_historico_cr(
    metric_type='eficacia',   # 'eficacia' | 'convrate'
    banda_actual='Exitosa',
    val_actual=0.9740,        # float [0,1] para eficacia; float % para convrate
    canvas_id='hcr-global-ef',
    current_week='W20'        # ← SIEMPRE la semana actual, nunca la próxima
)
```

```python
from historico_module_rnd import render_historico_rnd

hist_html = render_historico_rnd(
    metric_type='nodispo',    # 'nodispo' | 'ipm'
    banda_actual='Revisar',
    val_actual=0.0820,        # float [0,1] para nodispo; float USD/M para ipm
    canvas_id='hrnd-global-nd',
    current_week='W20'        # ← SIEMPRE la semana actual, nunca la próxima
)
```

### Wrapper de sección (Análisis por hotel + Análisis por dimensión)

Para las secciones que necesitan 2 módulos lado a lado (Eficacia + ConvRate, o NoDispo + IPM), existe un wrapper que conecta los clicks de filas con eventos custom:

```python
# CR (en render_cr_p2.py)
hist_section_cr = render_historico_seccion_cr(
    canvas_id_ef='hcr-hotel-ef',
    canvas_id_cv='hcr-hotel-cv',
    banda_ef=..., val_ef=...,
    banda_cv=..., val_cv=...,
)

# RND (en render_rnd_p2.py)
hist_section_rnd = render_historico_seccion_rnd(
    canvas_id_nd='hrnd-hotel-nd',
    canvas_id_ipm='hrnd-hotel-ipm',
    banda_nd=..., val_nd=...,
    banda_ipm=..., val_ipm=...,
)
```

Los módulos escuchan eventos `hist-update` y `hist-reset` disparados por el wrapper externo cuando el usuario clickea una fila con atributos `data-hist-*`.

### Ventana histórica · 5 semanas reales (post W20 sesión 6)

Los módulos históricos usan una **ventana fija de 5 semanas reales** definida en `_scripts/historico_data.py`:

```python
SEMANAS = ['W16', 'W17', 'W18', 'W19', 'W20']  # ventana actual
```

**Decisión de diseño:** se prefirió 5 semanas reales antes que 8 con ficticios marcados. Razón: datos auditables en un reporte de decisión > más puntos en la curva.

**Plan de evolución (cómo extender la ventana cuando lleguen W21+):**

| Semana actual | Acción | Ventana final |
|---|---|---|
| **W21** (próxima) | Editar `historico_data.HIST_DATA`: agregar valor W20 a cada array, renombrar `SEMANAS` a `[W16..W21]` | 6 semanas |
| **W22** | Idem · agregar W21 a HIST_DATA · SEMANAS = `[W16..W22]` | 7 semanas |
| **W23** | Idem · agregar W22 · SEMANAS = `[W16..W23]` | **8 semanas reales** |
| **W24+** | Ventana móvil de 8: descartar la semana más antigua y agregar la nueva | 8 semanas reales |

**Para extraer los datos de cada semana nueva**, ejecutar `calc_cr.py` y `calc_rnd.py` con la semana correspondiente y leer del pickle:
- CR: `M['global_w{N}']['eficacia']` y `['conv_rate']` (multiplicar por 100)
- RND: `M['global_w{N}']['pct_nodispo']` (multiplicar por 100) y calcular IPM = `gb_usd / trafico * 1M`
- Repetir para canastas: `M['B2B (OP)_w{N}']`, `M['CUG (UOP)_w{N}']`, `M['B2C_w{N}']`

**Util pendiente** (no urgente): `extract_hist_data.py` que automatice este append leyendo todos los pickles W16-W{current}.

**val_actual conceptual:** desde sesión 6, `val_actual` que reciben los módulos históricos es el valor de la **semana ACTUAL** del reporte (no la próxima). El módulo lo agrega como último punto de la serie automáticamente.

**Gauge de 5 niveles:** todas las barras `height:6px · opacity:1` — colores sólidos puros, grosor uniforme. La banda activa se identifica por la pill encima, no por el gauge.

### Estilo de badges severity (post W20 sesión 4)

Todos los badges del sistema usan el **estilo Opción D**:
- `font-size: 13px` (canastas: 11px)
- `padding: 10px 22px`
- `border: 1px solid {bd}`
- `text-transform: uppercase`
- `text-align: center`

El texto del badge es **solo el nombre de la banda en mayúsculas**. El target se muestra como caption gris separado debajo, vía `target_caption()` en `render_helpers.py`.

Ver `_docs/BANDAS.md` para la paleta D completa y todos los detalles del sistema.

---


---

## 🔍 Searchbox cliente-side · Estado post W20 sesión 15+

### 3 modos de searchbox (JS Engine W21 · `asset_*_head.html`)

| Modo | Trigger HTML | Contexto |
|---|---|---|
| **Pill** (Prop A) | `input[data-sb-pill]` | KPI cards hero + canastas — pill redondeada en `tabs-row` |
| **Header** (Prop D) | `input[data-sb-table]` | Bloques hotel + dim — integrado en primera columna del header |
| **Legado** | `input[data-sb-scope]` | Compatibilidad retroactiva |

El modo Pill filtra solo el tab activo (`.tp-* display!='none'`). El modo Header filtra `[data-lbl]` dentro del `.tbl-wrap` correspondiente. Ambos muestran empty state y resetean al cambiar tab.

### Regla de unicidad: cero duplicación

Un solo punto de búsqueda por contexto:
- **Cards KPI** → `searchbox_pill_html()` en la fila de tabs (Prop A)
- **Tablas hotel + dim** → `searchbox_header_html()` en col1 del header (Prop D)
- **`sb-inline-wrap` en `tabs-row` de bloques** → eliminados

### Cobertura (26 searchboxes)

| Sección | CR | RND |
|---|---|---|
| Hero KPI card Eficacia/NoDispo | ✅ Prop A `sb-kpi-*-ef/nd` | ✅ Prop A |
| Hero KPI card ConvRate/IPM | ✅ Prop A `sb-kpi-*-cv/ipm` | ✅ Prop A |
| Análisis por hotel (global) · 4 tabs CR / 4 RND | ✅ Prop D por tab | ✅ Prop D por tab |
| Análisis por dimensión (global) · Corp+Dest | ✅ Prop D | ✅ Prop D |
| Canastas KPI card Ef/NoDispo × 3 | ✅ Prop A | ✅ Prop A |
| Canastas KPI card CV/IPM × 3 | ✅ Prop A | ✅ Prop A |
| Canastas hotel tabla × 3 tabs × 3 canastas | ✅ Prop D | ✅ Prop D |
| Canastas dim tabla × 2 tabs × 3 canastas | ✅ Prop D | ✅ Prop D |

### Comportamiento

- **Solo filtra tab activo** — ningún modo contamina otros tabs ni otras cards
- **Top 100 en DOM** — 10 visibles al abrir; 90 accesibles vía search (`sb-hidden`)
- **Cross-tab limpio** — al cambiar pestaña: input se vacía, grid resetea a `1fr 1fr`
- **Empty state** (fix A1) — `"Sin resultados para «query»"` si nada coincide
- **Case-insensitive + sin acentos** — `normalize('NFD')` — `"cancun"` matchea `"Cancún"`
- **Búsqueda por** — `data-lbl` (Prop D) o `data-hist-label` (legacy/pill)

### Arquitectura de las filas

```html
<!-- Tablas hotel (render_top_table_cr/rnd, tab_panel_hotel) -->
<div class="sb-hidden"
     data-row-idx="11"
     data-hist-label="Cancún"
     data-lbl="Grand Hyatt Cancún GRUPO RIU"
     data-hist-w21="2.81" data-hist-w20="2.48"
     style="cursor:pointer;...">

<!-- Tablas dim (añaden data-lbl con nombre de dimensión) -->
<div data-lbl="RIU Hotels & Resorts"
     data-hist-label="RIU Hotels & Resorts" ...>

<!-- RND: también llevan IPM -->
     data-hist-ipm-w21="1097" data-hist-ipm-w20="657"
```

### IDs canónicos

**Global · bloques hotel y dim (Prop D, uno por tab):**

| Tab | CR | RND |
|---|---|---|
| Hotel Críticos | `sb-h-crit` | `sb-rh-crit` |
| Hotel Bajo Rend | `sb-h-br` | `sb-rh-br` |
| Hotel Sin Conv | `sb-h-sc` | `sb-rh-sc` |
| Hotel Menor CV/DNC | `sb-h-mcv` | `sb-rh-dnc` |
| Dim Corporativo | `sb-d-corp` | `sb-rd-corp` |
| Dim Destino | `sb-d-dest` | `sb-rd-dest` |
| Dim País | — | `sb-rd-pais` |

**Canastas (por `idx_str` = `op` / `cug` / `b2c`):**

| Contexto | CR | RND |
|---|---|---|
| KPI Ef/NoDispo | `sb-kpi-{idx}-ef` | `sb-kpi-{idx}-nd` |
| KPI CV/IPM | `sb-kpi-{idx}-cv` | `sb-kpi-{idx}-ipm` |
| Hotel tab t_key | `sb-{idx}-h-{t_key}` | `sb-{idx}-rh-{t_key}` |
| Dim tab t_key | `sb-{idx}-d-{t_key}` | `sb-{idx}-rd-{t_key}` |

---

## 🃏 Cards KPI Hero · Layout post W20 sesiones 7–13

### Estructura de cada card (3 secciones visuales)

```
┌─────────────────────────────────────────┐
│ KPI label                               │  ← 10px uppercase muted
│ Valor grande   [BADGE]                  │  ← 40px / badge paleta D
│                Target X%               │  ← target_caption() separado
│                vs sem. ant. ↑ +0,8     │  ← wow_pill V1 verde/rojo/gris
│ ▓▓▓░░░░░░░░░░░ (gauge 5 niveles 6px)   │  ← height:6px, opacity:1
│ ┌ W20 ─┬─ WoW ─┬─ W19 ─┐              │
│ └──────┴───────┴────────┘              │  ← wow_box compacto
│ ─────────────────────────────────────── │
│ DESTINO│CORP│HOTEL│CHANNEL│CANASTA [🔍] │  ← tabs + pill searchbox Prop A
│ 1. Monterrey   59,99% ↓30,8            │  ← 10 visibles, 90 sb-hidden
│ 2. Ishigaki    68,83% ↑1,5             │
│ ...                                     │
│ ─────────────────────────────────────── │
│ EVOLUCIÓN HISTÓRICA · Global            │  ← módulo histórico
│ [curva W16-W20] [métricas 5W]          │
│ [sparkline global vs target]            │
└─────────────────────────────────────────┘
```

### wow_pill V1 (post W20s15)

Pill semántica verde/rojo/gris junto al valor principal:

```python
# En render_helpers.py
wow_pill_html(delta, unit='pp', prefix_pos='↑', prefix_neg='↓')
# Verde si delta>0, rojo si delta<0, gris si ~0 o None

# Orientación por métrica:
# NoDispo (bajar = bueno): pasar -delta con prefix invertidos
wow_pill_html(-delta, unit='pp', prefix_pos='↓', prefix_neg='↑')
```

### Sizing

| Elemento | CR hero | CR canasta | RND hero | RND canasta |
|---|---|---|---|---|
| Valor grande | `40px` | `36px` | `40px` | `36px` |
| Padding card | `12px 16px` | `12px 16px` | `12px 16px` | `12px 16px` |
| Tabs superiores | 5 (destino/corp/hotel/channel/canasta) | 4 (destino/corp/hotel/channel) | 5 (pais/destino/corp/hotel/canasta) | 4 |
| Filas por tab en DOM | 100 | 100 | 100 | 100 |
| Filas visibles al abrir | 10 | 10 | 10 | 10 |

---

## 📊 Análisis por hotel y por dimensión · Layout post W20 sesión 11+

### Layout de las tablas (2 columnas explícitas con header)

Cada panel de tab muestra:
- **Col izq**: filas 1-5 con su propio header
- **Col der**: filas 6-10 (visibles) + filas 11-100 (`sb-hidden`)
- Al buscar: `gridTemplateColumns` colapsa a `1fr`; el search filtra solo el tab activo

```python
# Patrón de generación (render_top_table_cr, _render_dim_table, tab_panel_hotel)
for i, r in df.iterrows():
    hidden = ' sb-hidden' if i >= 10 else ''
    row_html = f'<div class="{hidden.strip()}" data-row-idx="{i}" data-hist-label="..." ...>'
```

### IDs canónicos de scope para searchbox

| Sección | CR | RND |
|---|---|---|
| Hotel global | `#por-hotel` | `#por-hotel` |
| Dim global | `#por-dimension` | `#por-dimension` |
| Hotel canasta OP | `#canasta-op-hotel-cr` | `#canasta-op-hotel-rnd` |
| Dim canasta OP | `#canasta-op-dim-cr` | `#canasta-op-dim-rnd` |
| Hotel canasta CUG | `#canasta-cug-hotel-cr` | `#canasta-cug-hotel-rnd` |
| Dim canasta B2C | `#canasta-b2c-dim-cr` | `#canasta-b2c-dim-rnd` |

---

## 🎨 Sistema de colores · Estado definitivo post W20 sesión 13

### Severity · Paleta D canónica (badges + tablas)

| Banda | bg | fg (texto) | barra distribución |
|---|---|---|---|
| Exitosa | `#E1F5EE` | `#085041` | `#085041` |
| Aceptable | `#EDE8F7` | `#3C3489` | `#5C469C` |
| Revisar | `#FFEDD5` | `#7C2D12` | `#D4A878` |
| Crítica | `#FCE4F1` | `#99162B` | `#C0392B` |
| Súper Crítica | `#A32D2D` | `#FCEBEB` | `#A32D2D` |
| Sin Conversión | `#F2EEE6` | `#5F5E5A` | `#8A8377` |

### Gauge de 5 niveles (barras de KPI)

| Banda | color |
|---|---|
| Súper Crítica | `#161616` negro |
| Crítica | `#C0392B` rojo |
| Revisar | `#D4A878` ámbar suave |
| Aceptable | `#5C469C` violet |
| Exitosa | `#085041` verde teal |

`height:6px · opacity:1` · La banda activa se identifica con `border-bottom:2px solid var(--ink)`.

### Excepción cyan

`#4FC3F4` (Arctic Blue) solo en:
1. `IPM_ACCENT` en `historico_module_rnd.py`
2. Label "🔌 Third Party" en `render_cr_p1.py`

---

## 🐛 Bugs pendientes al cierre de W20 sesiones 7–13

Los siguientes bugs quedaron abiertos para atender en W21:

| # | Descripción | Archivo(s) |
|---|---|---|
| P1 | En canastas RND el histórico de hotel/dim muestra "undefined" en eje X | `render_rnd_p3.py`, `historico_module_rnd.py` |
| P2 | Canasta CR dim: al hacer click en fila no actualiza siempre el histórico (el listener de hotel/dim compite con el listener interno de `.kpi-card`) | `render_cr_p3.py` |
| P3 | ~~Cards KPI canasta: filas de tab sin header por columna~~ **RESUELTO** en W20s15 — Prop D integra el searchbox en el header de col1 | — |
| P4 | RND `tab_panel_hotel` en canastas usa `BANDA_COLORS` que puede no estar importado si el pickle cambia | `render_rnd_p3.py` |
| P5 | `extract_hist_data.py` pendiente (actualización automática de `historico_data.py`) | nuevo archivo |

**Última actualización:** Mayo 2026 · post W20 sesión 15+ · Searchbox Prop A+D + wow_pill V1 · 3 modos JS · IDs canónicos actualizados



---

## UI/UX Post W20 — Decisiones consolidadas

### Badges en listas KPI
- **Mostrar badge**: Destino · Corp · País · Channel · Canasta
- **NO mostrar badge**: Hotel (demasiado ruido visual)
- Badge = pill 8px con color de banda (paleta D canónica)

### Opción C — Searchbox inline en tabs-row
- Campo vive a la derecha de los tabs, separado por divisor vertical `border-left:1px solid var(--rule)`
- Ancho `120px` en reposo; lupa SVG como icono visual
- Botón × (`.sb-clear-btn`) para limpiar filtro activo — CSS `position:absolute;right:4px`
- Autocomplete via `buildLabels()` que solo lee el tab activo (`getActiveRows(false)`)

### Paleta D definitiva — colores sólidos para gauges y badges
| Banda | bg | fg |
|---|---|---|
| Exitosa | `#085041` | `#FFFFFF` |
| Aceptable | `#F59E0B` | `#FFFFFF` |
| Revisar | `#F59E0B` | `#FFFFFF` |
| Crítica | `#FCE4F1` | `#99162B` |
| Súper Crítica | `#FECACA` | `#7F1D1D` |
| Sin Conversión | `#F2EEE6` | `#5F5E5A` |

**Nota**: Aceptable y Revisar comparten el naranja `#F59E0B` en el gauge. El badge de Aceptable usa `bg:#FEF3C7 fg:#92400E` (pastel naranja).

## 🤖 Automatización del pipeline (W21+)

### Flujo completo en 1 comando

```bash
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

El pipeline tiene **8 pasos** (los 6 de siempre + 2 nuevos):

| Paso | Script | Descripción |
|---|---|---|
| 1–6 | _(existentes)_ | calc → render → assemble → excel → mail → hub |
| **7** | `update_docs.py` | Actualiza CHANGELOG + README + PROMPT_MAESTRO con KPIs reales del pickle |
| **8** | `github_commit.py` | Commit vía GitHub API + ZIP del proyecto Claude |

Pasos 7 y 8 son **non-critical** — si fallan no abortan el pipeline.

### Activar el commit automático (Paso 8)

Agregar al YAML de config:
```yaml
github_token: ghp_xxx   # Token GitHub con permisos de escritura al repo
```

O exportar antes de correr:
```bash
export GITHUB_TOKEN=ghp_xxx
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

### Para fixes puntuales (fuera de pipeline)

```bash
# 1. Actualizar docs
python3 update_docs.py --week 21 --tipo fix \
  --descripcion "Fix Severity en canastas" \
  --commits "abc123,def456"

# 2. Commitear
python3 github_commit.py --week 21 --tipo fix \
  --mensaje "fix(canastas): Severity + rows-more dim" \
  --token ghp_xxx
```

### Scripts de automatización

| Script | Uso |
|---|---|
| `update_docs.py` | Actualiza los 3 docs · modo `pipeline` (con KPIs) o `fix` (cambio puntual) |
| `github_commit.py` | Commit vía API · reemplaza `commit_release.py` · también genera ZIP del proyecto Claude |
| `run_pipeline.py` | Orquestador · llama a update_docs y github_commit automáticamente |


## 🔧 Regla de mantenimiento: Global vs Canastas (post-W20)

### Principio general
Los componentes visuales están centralizados en `render_helpers.py`. Los cambios se propagan automáticamente a p1 (global) y p3 (canastas).

### Qué tocar según el tipo de cambio

| Tipo de cambio | Archivos a editar |
|---|---|
| Visual puro (padding, color, font-size, spacing) | Solo `render_helpers.py` → heredado por p1 y p3 |
| Datos (nueva columna, nueva métrica) | `calc_*.py` + `render_*_p1.py` + `render_*_p3.py` (siempre los dos) |
| Estructura de tabs (agregar/quitar tab) | `asset_*_head.html` (CSS selector) + p1 + p3 |
| Módulo histórico | `historico_module_v2.py` o `historico_module_rnd.py` + verificar IDs únicos en p1 y p3 |

### Checklist antes de commitear
```
[ ] ¿El cambio visual usa helper centralizado o se duplicó?
[ ] ¿Se revisó tanto p1 (global) como p3 (canastas) para CR y RND?
[ ] ¿Los column grids de filas de tabs siguen el estándar?
[ ] ¿Las pills WoW en filas usan make_wow_pill_row() o CSS class?
[ ] ¿Los headers de columna están en TODOS los tab panels?
```

### Helpers centralizados en `render_helpers.py`

| Helper | Uso | Reemplaza |
|---|---|---|
| `tab_column_header(cols, widths)` | Header `Severity / Métrica / WoW` en tabs KPI | Strings `_tab_hdr` hardcodeados en p1 |
| `make_wow_pill_row(wow_v, ...)` | Pill WoW en filas de tabs | Bloques `<em style=...>` inline duplicados |
| `wow_box(..., compact=False/True)` | WoW box global y canastas | `wow_box_canasta()` local eliminada de p3 |
| `wow_pill_html(wow_val, unit)` | Pill WoW grande (hero) | — |
| `banda_pill(banda, target)` | Badge de banda | — |
| `gauge_5levels(banda, tipo)` | Gauge visual 5 niveles | — |
| `searchbox_pill_html(...)` | Searchbox en tabs-row de KPI cards | — |
| `searchbox_header_html(...)` | Searchbox en header de tablas análisis | — |

### Patrón de tabs en canastas KPI (CR)
Desde post-W20, las cards KPI de canastas CR usan activación **JS** en lugar de CSS radio selector global:
- Panels: `class="tp-{card_id}"` con `display:none` inicial
- `getActivePanel()` en `asset_cr_head.html` detecta primero `.tp-*` para aislar el scope del searchbox
- El patrón original de RND p3 (JS) se adoptó en CR p3 para evitar contaminación entre canastas y global

### Estructura columnas estándar (post-W20)

**Análisis por Hotel — canastas CR:**
`Hotel | Severity (80px) | ConvRate (58px) | Eficacia (58px) | WoW (38px)`

**Análisis por Hotel — canastas RND:**
`Hotel | Severity (80px) | %NoDispo (62px) | WoW (36px) | IPM (58px) | WoW IPM (36px)`

**Análisis por Dimensión — canastas CR:**
`Nombre | Severity (80px) | Checkrates (68px) | BKGS (56px) | ConvRate (62px) | WoW (36px) | Eficacia (62px) | WoW (36px)`

**Análisis por Dimensión — canastas RND:**
`Nombre | Severity (80px) | %NoDispo (62px) | WoW (38px) | IPM (62px) | WoW (38px)`

**Visibilidad filas (global y canastas):**
- KPI tabs: 10 en DOM, 5 visible · 5 `rows-more` · 90 `sb-hidden`
- Análisis hotel: 100 en DOM, 5 visible · 5 `rows-more` · 90 `sb-hidden` + botón "Ver 5 más"
- Análisis dimensión: 100 en DOM, 5 visible · 5 `rows-more` · 90 `sb-hidden` + botón "Ver 5 más"


