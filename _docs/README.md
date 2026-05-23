# _scripts · Pipeline de generación de reportes

Pipeline Python para generar los Reportes Editoriales (HTML), Excels de Análisis, Hub index y ZIP de release a partir de los datasets crudos semanales.

---

## 📋 Inventario de archivos

### Cálculo y agregación
| Archivo | Función |
|---|---|
| `engine.py` | Funciones core: bandas (`banda_nodispo`, `banda_rpm`, `banda_eficacia`, `banda_convrate`), agregaciones, Pareto P80, channel grupo |
| `render_helpers.py` | Helpers de formato: `fmt_int_es`, `fmt_pct2`, `fmt_num2`, `fmt_big`, `clean_hotel_name`, `truncate`, `banda_pill`, `gauge_5levels`, `wow_box` |
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

## 🔍 Searchbox cliente-side · Estado post W20 sesiones 7–13

### Cobertura final (26 searchboxes)

| Sección | CR | RND |
|---|---|---|
| Hero KPI card Eficacia/NoDispo | ✅ dentro de la card | ✅ dentro de la card |
| Hero KPI card ConvRate/IPM | ✅ dentro de la card | ✅ dentro de la card |
| Análisis por hotel (global) | ✅ `sb-cr-hotel` | ✅ `sb-rnd-hotel` |
| Análisis por dimensión (global) | ✅ `sb-cr-dim` | ✅ `sb-rnd-dim` |
| Canastas KPI card Ef/NoDispo × 3 | ✅ 3 sb | ✅ 3 sb |
| Canastas KPI card CV/IPM × 3 | ✅ 3 sb | ✅ 3 sb |
| Canastas hotel tabla × 3 | ✅ 3 sb | ✅ 3 sb |
| Canastas dim tabla × 3 | ✅ 3 sb | ✅ 3 sb |

### Comportamiento final

- **Solo filtra en el tab activo**: `getActiveRows()` usa `getComputedStyle(panel).display !== 'none'`
- **Top 100 en DOM**: 10 visibles al abrir; 90 accesibles vía search (`data-row-idx`, `sb-hidden`)
- **Cross-tab limpio**: al cambiar pestaña, el search se limpia automáticamente (listener `change`)
- **Sin dropdown**: el autocomplete fue eliminado — solo filtrado inline (más limpio)
- **Case-insensitive + sin acentos**: `normalize('NFD')` — `"cancun"` matchea `"Cancún"`
- **Búsqueda por nombre**: atributo `data-hist-label` en cada fila (primera columna)

### Arquitectura de las filas interactivas

Cada fila de tabla lleva estos atributos para el doble funcionamiento (search + histórico):

```html
<div class="sb-hidden"         <!-- oculta si i >= 10 al cargar -->
     data-row-idx="11"         <!-- posición 0-based dentro del tab -->
     data-hist-label="Cancún"  <!-- para search y label histórico -->
     data-hist-w21="2.81"      <!-- valor semana actual (×100 para %) -->
     data-hist-w20="2.48"      <!-- valor semana anterior -->
     style="cursor:pointer;...">
```

Para RND, filas de hotel y dim añaden también:
```html
     data-hist-ipm-w21="1097"
     data-hist-ipm-w20="657"
```

---

## 🃏 Cards KPI Hero · Layout post W20 sesiones 7–13

### Estructura de cada card (3 secciones visuales)

```
┌─────────────────────────────────────────┐
│ KPI label                               │  ← 10px uppercase muted
│ Valor grande   [BADGE]·Target           │  ← 40px / badge paleta D
│ ▓▓▓░░░░░░░░░░░ (gauge 5 niveles 6px)   │  ← height:6px, opacity:1
│ ┌ W20 ─┬─ WoW ─┬─ W19 ─┐              │
│ └──────┴───────┴────────┘              │  ← wow_box compacto
│ ─────────────────────────────────────── │
│ DESTINO│CORP│HOTEL│CHANNEL│CANASTA      │  ← radio tabs CSS puro
│ [Buscar en estas pestañas...]           │  ← sb-input inline
│ 1. Monterrey   59,99% ↓30,8            │  ← 10 visibles, 90 sb-hidden
│ 2. Ishigaki    68,83% ↑1,5             │
│ ...                                     │
│ ─────────────────────────────────────── │
│ EVOLUCIÓN HISTÓRICA · Global            │  ← módulo histórico
│ [curva W16-W20] [métricas 5W]          │
│ [sparkline global vs target]            │
└─────────────────────────────────────────┘
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
| P3 | Cards KPI canasta: filas de tab en 2 columnas no muestran header por columna (solo 1 header global) | `render_cr_p3.py`, `render_rnd_p3.py` |
| P4 | RND `tab_panel_hotel` en canastas usa `BANDA_COLORS` que puede no estar importado si el pickle cambia | `render_rnd_p3.py` |
| P5 | `extract_hist_data.py` pendiente (actualización automática de `historico_data.py`) | nuevo archivo |

**Última actualización:** Mayo 2026 · post W20 sesiones 7-13 · UI/UX completo + Searchbox + Top 100


