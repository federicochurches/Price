# CHANGELOG · Reportes Supply Optimization

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
