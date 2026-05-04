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
