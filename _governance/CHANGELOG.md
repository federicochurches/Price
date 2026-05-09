# CHANGELOG · Reportes Supply Optimization

## Week 19 · Mayo 2026 · Pack de mejoras pre-release

### 📐 Estructura de canastas RND igualada al global
- **KPI cards de canasta:** gauge bar 5 niveles + wow_box (W17/W18/WoW) + tabs (País · Destino · Corp · Hotel) con pills WoW. Antes eran cards compactas sin gauge ni tabs.
- **Resumen Ejecutivo de canasta:** findings #1 y #2 con pills de banda y pills de delta WoW, igual que el global.
- **Bloque Análisis por Hotel:** 3 tabs (Demanda No Convertida · Bajo Rendimiento · Sin Conversión) reemplaza listados estáticos.
- **Bloque Análisis por Dimensión:** 3 tabs (Corporativo · Destino · País) reemplaza "Tabs por dimensión" anterior.
- **CSS `.tabs-block`** base agregado a `asset_rnd_head.html`. Selectores inline en `render_rnd_p3.py`.

### 🎨 Cambios visuales

- **Hub `index.html`:** eliminado `.rpt-name` (repetía el nombre del reporte ya visible en la pill). `.rpt-week` subido a 15px/700 como título visual. Fondo cards y archivo-links cambiado de `#fff` a `#F8F4EC` (paper cálido, consistente con los reportes).
- **Alertas globales RND:** pills IPM diferenciadas de %NoDispo. %NoDispo = magenta (`#EA0074`/`#FCE4F1`). IPM = amber (`#A86A1D`/`#FEF3E2`). Antes ambas eran magenta.
- **Alertas globales RND:** nombres de hotel/destino/corp en una sola línea (`white-space:nowrap; overflow:hidden; text-overflow:ellipsis`). Evita cards asimétricas.
- **Resumen Ejecutivo global RND:** pills de banda inline en lugar de texto plano (ej. `banda Aceptable` → pill visual). Pills de delta WoW con color semántico (verde=mejora, rojo=deterioro). Mayúscula después de cada `·`. Finding #6 → RIU como corp con mayor %NoDispo + delta WoW + transversalidad canastas. Finding #9 → hoteles con NoDispo >90% (Hard Rock London, Rixos Radamis, Grand Hyatt Istanbul) + Iberostar 61,12%.
- **Tabs KPI hero RND:** delta WoW por ítem en tabs País, Destino y Corp (no en Hotel ni Canasta). Sistema de pills `<em>` con 3 clases: `wow-pill up` (rojo, deterioro), `wow-pill dn` (verde, mejora), `wow-pill nd` (gris "—", sin dato W17). Layout de filas cambiado de `flex` a `grid` con columnas fijas `1fr 52px 44px` para alineación perfecta.
- **Normalización nombres de país:** `Estados Unidos de América` → `United States`, `Reino Unido` → `United Kingdom`, `República Dominicana` → `R. Dominicana`, `Emiratos Árabes Unidos` → `Emirates`. Función `clean_pais_name()` centralizada en `render_helpers.py`.

### 🔧 Cambios de cálculo

- **`calc_rnd.py`:** TAB_NoDispo y TAB_RPM enriquecidos con columnas WoW (`NoDispo_WoW_pp`, `RPM_WoW_pct`) via merge con aggregates W17 por dimensión.

### 🐛 Bugs corregidos

- **CSS `em.wow-pill`:** el selector `.tab-panel div span` con `!important` sobreescribía el color de las pills. Fix: cambiar pills de `<span>` a `<em>` + definir colores en clases CSS `em.wow-pill.up/dn/nd` con `!important`.
- **Selector CSS amber:** agregadas exclusiones `:not(.wow-pill):not(.wow-spacer)` en ambas ocurrencias del selector en `asset_rnd_head.html` y templates.

### 📁 Archivos modificados

`render_helpers.py` · `calc_rnd.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `asset_rnd_head.html` · `_TEMPLATE_RatesNoDispo_Reporte.html` · `_TEMPLATE_Hub.html` · `GUIA_EDITORIAL_RatesNoDispo.html` · `index.html` (hub W18)

---

## Week 18 · Mayo 2026

### 🐛 Bugs corregidos

- **Severity RPM mostraba "Exitosa" para $479,70 con target ≥$650.** La función `banda_rpm()` en `_scripts/engine.py` usaba thresholds viejos (1/2.5/4) cuando la métrica ya era GBM USD/M. Corregido a thresholds **200/650/1500** consistentes con la métrica actual. Distribución resultante en P80 RND W18: Sin Conversión 11.954 · Crítica 1.706 · Revisar 1.732 · Aceptable 1.684 · Exitosa 1.616 (antes todos caían en Exitosa porque cualquier RPM > 4 superaba el umbral viejo).

### ✨ Nuevas features

- **Estructura completa de canasta** según template editorial. Cada `<details>` de canasta ahora incluye: KPI block · Alertas Críticas (3 cards) · Resumen Ejecutivo (10 findings 2 cols) · Severidad (2 cols con barras) · Tabs por dimensión (10 a 2 cols, borde estilo folder) · Top 10 Bajo Rendimiento (5+5) · Top 10 Sin Conversión (5+5) · Síntesis ejecutiva · Plan de Acción (6 acciones 2 cols).
- **Helpers Python nuevos** que replican snippets HTML literales del template:
  - `_scripts/template_resumen.py` · render_resumen_ejecutivo()
  - `_scripts/template_alertas.py` · render_alertas_block()
  - `_scripts/template_severity.py` · render_severity_2cols() + LEVELS predefinidos
- **Tabs estilo folder** en hero y dentro de canastas (border-radius 6px 6px 0 0).
- **Channel split en hero CR** (Producto Propio + Third Party) tanto en card Eficacia como ConvRate.
- **Tab Hotel parseado** con `clean_hotel_name()` (sin prefijos `(NNNNNN) -`) en hero, alertas, tabs canasta y todos los listados.
- **Documentación completa** en `_governance/`: BANDAS · AREAS_ACCOUNTABLE · ESTRUCTURA_TEMPLATE · CHANGELOG.

### 🎨 Cambios visuales

- **H1 narrativo eliminado del hero.** Antes ocupaba 2 líneas con "Eficacia de X% y Conversion Rate de Y% · concentración en...". Ahora el reporte arranca directo con la línea de métricas globales y los 2 cards.
- **Header masthead "W18" → "Week 18"** (más legible, font-size 32→26px).
- **Card RPM hero RND** ahora muestra: "RPM · Gross Booking USD por millón de búsquedas" + valor con símbolo $ + Target ≥ $650.
- **Pestaña "Ficha Técnica" eliminada de Excel** de análisis (RND y CR). Los Excels ahora arrancan directo en Severity.
- **Plan de Acción a 2 columnas** (3+3 acciones) tanto global como por canasta. Antes era 1 columna larga.
- **Sin Conversión a 10 items en 2 columnas** (5+5). Antes era 5 items en 1 columna.
- **Bajo Rendimiento a 10 items en 2 columnas** (5+5). Antes era 5 items en 1 columna.

### 🔧 Cambios de cálculo

- **Métrica RPM redefinida:** ahora es `gb_usd / Trafico × 1.000.000` (Gross Booking USD por millón). Antes era `Bookings / Trafico × 1.000.000` (reservas por millón). Bandas y target actualizados en consecuencia.
- **Catálogo de Áreas Accountable consolidado a v2** (4 áreas). 24 reemplazos aplicados en planes de acción global y por canasta.
- **Bajo Rendimiento RND** ahora se filtra por "RPM > 0 + RPM < P50 procesable" en vez de banda Crítica/Revisar (que con la calibración vieja capturaba mayormente refunds).
- **Sin Conversión** queda como cohorte estructural separada, no parte de la severity ConvRate / RPM.

### 📐 Cambios estructurales

- **Resumen Ejecutivo reescrito** siguiendo estructura literal del template: header overline pequeño "🎯 Resumen Ejecutivo" fuera del card, card con border-top 3px negro y fondo paper-soft, grid 2 columnas, cada finding con número + valor destacado en color + título-descripción. Sin highlights `.hl`.
- **Alertas Críticas dentro de cada canasta** (no solo en hero global).
- **Tabs canasta** con borde estilo folder (border-radius 6px 6px 0 0).
- **CSS canasta tabs** unificado con CSS hero tabs.

### 🗂 Documentación nueva

- `README.md` actualizado con glosario, catálogo Áreas v2, estructura del repo y workflow.
- `_governance/BANDAS.md` · sistema de bandas calibrado.
- `_governance/AREAS_ACCOUNTABLE.md` · catálogo v2 + mapeo desde v1.
- `_governance/ESTRUCTURA_TEMPLATE.md` · estructura exacta del editorial.
- `_governance/CHANGELOG.md` · este archivo.
- `_scripts/README.md` · cómo correr el pipeline.

---

## Week 17 · Abril 2026

(no aplicaba changelog formal)

- Sistema de bandas D introducido
- Sin Conversión separada como cohorte aparte
- Plantillas H1 narrativo a 2 líneas
- Pills Súper Crítica con transparencia 80%
- Channel agrupado en CR (Producto Propio vs Third Party)

---

## 📌 Pendientes para Week 19

- **Eliminar duplicación de outputs.** El pipeline genera 4 archivos preview en `/mnt/user-data/outputs/` con nombres `Supply_*_W18.html` y `Analisis_*_W18.xlsx` que son idénticos a los del repo. Para Week 19, los renderers y excel writers deben escribir directo con el nombre estándar del repo:
  - `Supply_RatesNoDispo_W18.html` → `RatesNoDispo_Reporte_Editorial.html`
  - `Supply_CheckRates_W18.html` → `CheckRates_Reporte_Editorial.html`
  - `Analisis_Rates_NoDispo_W18.xlsx` → `Analisis_Rates_NoDispo_7d.xlsx`
  - `Analisis_CheckRates_W18.xlsx` → `Analisis_Checkrates_7d.xlsx`
  
  Tocar: `assemble_cr.py`, `assemble_rnd.py`, `excel_cr.py`, `excel_rnd.py`, `build_package.py`.

---

## 🆕 Mejora · Reorganización secciones globales (post Week 18)

**Fecha:** 5 mayo 2026 (sesión continuación Week 18)

### Antes
6 secciones globales apiladas en cada reporte (RND y CR), cada una con su `<h2>`, kicker y tabla multi-columna. Resultado: ~1200px de scroll vertical solo en globales.

### Ahora
2 bloques con tabs por reporte:

**RND:**
- Sección 03 · Análisis por hotel · 3 tabs (Demanda NC · Bajo Rend · Sin Conv)
- Sección 04 · Por dimensión · 3 tabs (Corp · Destino · País)

**CR:**
- Sección 04 · Análisis por hotel · 4 tabs (Críticos · Bajo Rend · Sin Conv · Menor ConvRate)
- Sección 05 · Por dimensión · 3 tabs (Corp · Destino · Channel con split PP/TP)

### Beneficios
- Reduce ~40% la altura del reporte editorial
- Misma información disponible (Top 10 a 2 cols)
- Tab Channel del bloque dimensión integra el split Producto Propio + Third Party que antes era sección separada
- Channel agrupado (cards comparadoras PP vs TP) se mantiene como sección independiente porque NO es un listado, es un comparador

### Trade-offs aceptados
- Ctrl+F en el navegador solo encuentra contenido del tab activo (mitigado por Excel Top 50 con todo)
- Imprimir sale solo la tab activa (mitigado: nadie imprime el editorial, los Excels son el deliverable de detalle)

### Archivos modificados
- `render_rnd_p2.py` · funciones `render_bloque_hoteles()` y `render_bloque_dimensiones()` reemplazan las 6 funciones viejas
- `render_cr_p2.py` · idem con `_cr` suffix
- `asset_rnd_head.html` y `asset_cr_head.html` · CSS de los tabs nuevos (especificidad con `!important` para vencer regla base `.tab-panel{display:none}`)

### CSS clave aprendido
La regla `.tab-panel{display:none}` del CSS hero original tiene la misma especificidad que la regla `:checked ~ .tab-panels .tab-panel[data-tab="x"]{display:block}`. Como CSS prioriza la última declarada en orden, el `display:none` ganaba. Solución: prefijar con `.tabs-block` Y usar `!important`. Documentado en ESTRUCTURA_TEMPLATE.md.

---

## 🎨 Pack visual CR · Post Week 19 · Mayo 2026

**Equivalente al pack RND de la misma sesión. Iguala el nivel visual de CheckRates al de RatesNoDispo.**

### Nuevos archivos
- **`asset_cr_head.html`** (nuevo): CSS base CR independiente. Deriva de `asset_rnd_head.html` con adaptaciones:
  - `--accent:#5C469C` (violet), `--accent-soft:#EDE8F7`
  - `--amber:#5C469C` (no se usa en CR como amber/dorado)
  - `report-tag` background violet
  - Tabs hero activos en violet (no magenta)
  - 4 selectores de tabs-block hoteles CR: `tab-h-crit`, `tab-h-br`, `tab-h-sc`, `tab-h-mcv`
  - 3 selectores de tabs-block dimensiones CR: `tab-d-corp`, `tab-d-dest`, `tab-d-chan` (Channel, no País)
  - `section {margin-bottom:64px}` uniforme
  - `.hero {padding:16px 0 24px; border-bottom:none; margin-bottom:0}`

### Cambios en archivos existentes
| Archivo | Cambios |
|---|---|
| `render_cr_p1.py` | Nombres hotel + subtítulo en cards alertas con `white-space:nowrap; overflow:hidden; text-overflow:ellipsis` |
| `render_cr_p2.py` | Pills severity `!important` (global severity + pills inline de `_render_dim_table`) · Iconos `🏨` y `📊` en títulos de bloques globales · `border-top:1px solid var(--rule); padding-top:48px` en severity, por-hotel, por-dimension · `clean_corp_name()` en `_render_dim_table` |
| `render_cr_p3.py` | Icono `📊 Análisis por dimensión` en tabs de canasta · Plan de Acción con `margin-top:48px; padding-top:40px; border-top:1px solid var(--rule)` · `margin-bottom:32px` en `<details class="canasta-block">` · `clean_corp_name()` en `panel_inner` |
| `template_severity.py` | `background:{banda_bg} !important; color:{banda_fg} !important` en `render_severity_row()` · Aplica a ambos reportes RND y CR |
| `GUIA_EDITORIAL_CheckRates.html` | Bloque de actualizaciones post Week 19 documentado |

### Decisiones
- **Síntesis ejecutiva se mantiene en CR** (no se eliminó como en RND; la inestabilidad de renderizado no se reproduce en CR con su estructura actual)
- **`template_severity.py` es compartido** entre RND y CR — el `!important` mejora ambos reportes simultáneamente
- **Magenta `#EA0074` sigue en CR** para el subtítulo de "% Eficacia" en la severity combinada (color semántico de la métrica, no del reporte)

---

## 🗂 Excel CR · Columna Channel Principal · Post Week 19

### Qué se agregó
Columna **"Channel"** (channel principal por hotel) en todas las pestañas con granularidad de hotel individual, en el Excel global y en los 3 Excels de canasta.

### Pestañas afectadas (CR únicamente)
**Global (`Analisis_Checkrates_7d.xlsx`):**
- `Críticos` — posición 5 (entre Destino y CR_Unicos)
- `Bajo Rendimiento` — posición 5
- `Sin Conversión` — posición 5
- `Menor Conv Rate` — posición 5

**Por canasta (`Analisis_Checkrates_{B2C|OP|CUG}_7d.xlsx`):**
- `Críticos`, `BajoRend`, `Sin Conv`, `Menor CR` — misma posición 5

Pestañas NO afectadas (agregadas, no tienen nivel hotel): `Severity Eficacia`, `Severity ConvRate`, `Por Corporativo`, `Por Destino`, `Por Channel`, `Plan de Acción`.

### Lógica de cálculo
`build_hotel_channel_map()` en `excel_cr.py` opera en 3 intentos en cascada:
1. **`D['df_hotel_channel']`** en el pickle (si `calc_cr.py` lo exporta — la forma más limpia)
2. **Dataset Excel crudo** (`Dataset_CheckRates_W*.xlsx`) si está en el directorio de trabajo — agrupa por `Hotel × ExternalProviderName` y toma el de mayor `CR_Unicos`
3. **Fallback `'N/D'`** si ninguna fuente está disponible

### Integración recomendada con calc_cr.py
Para que la Opción 1 funcione, agregar al final de `calc_cr.py` antes del `pickle.dump`:
```python
# Channel principal por hotel (para Excel CR)
df_hc = df.groupby(['Hotel','ExternalProviderName'])['CheckRates Únicos'].sum().reset_index()
df_hc.columns = ['Hotel','ExternalProviderName','CR_Unicos']
D['df_hotel_channel'] = df_hc
```
