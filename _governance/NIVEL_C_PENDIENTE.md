# 📋 NIVEL C · Pendientes para Week 19

> **Decisión post W18:** los archivos correctos para esta semana se publicaron como Nivel B (deliverables + hub + README). Los templates y guías editoriales NO se actualizaron en W18 para dar tiempo a recoger feedback de los 12 destinatarios sobre el nuevo formato antes de cristalizar la documentación de proceso.
> 
> **Aplicar en W19** una vez tengamos respuestas/observaciones del equipo.

---

## ✅ Aplicado en W18 (Nivel B)

- Carpetas `rates-nodispo/week-18/` y `checkrates/week-18/` creadas con sus 3 archivos cada una (reporte editorial + Excel análisis + dataset crudo)
- Carpeta `_email/week-18/` con `Mail_W18.html` (estructura ejecutiva: resumen + plan acción consolidado por owner)
- `index.html` actualizado con cards W18 activas y W17 movido al archivo
- `README.md` del repo actualizado con W18 y nota sobre vigencia del sistema de bandas D
- Reportes editoriales y Excels generados con los 11 fixes post-W17 aplicados (sistema bandas D, badge owner protagonista, plan acción dentro de canasta, capitalización findings, Excels 17/13 pestañas, etc.)

## 🔧 Pendiente para W19 (Nivel C)

### 1. Actualizar templates HTML

**`_template/_TEMPLATE_Hub.html`**
- Validar si la estructura de cards y archivo sigue funcionando bien después de tener varias semanas con el formato nuevo
- Considerar mostrar 4-5 semanas en archivo (no solo 2) ahora que la cadencia es estable

**`rates-nodispo/_template/_TEMPLATE_RatesNoDispo_Reporte.html`**
- Refactorizar para reflejar la estructura W18:
  - Plan de Acción con badge owner como protagonista (no Quick Win/Cluster arriba)
  - Bloque "Plan de Acción · canasta {X}" dentro de cada `<details>` de canasta
  - Findings del Resumen Ejecutivo capitalizados desde el template
  - CSS de `.action-row` con `action-owner-badge` y `action-meta-bottom`
- Considerar si los placeholders existentes siguen sirviendo o conviene rehacerlos

**`checkrates/_template/_TEMPLATE_CheckRates_Reporte.html`**
- Mismas refactorizaciones que RND
- Asegurar que el bloque "Channel agrupado" (Producto Propio vs Third Party) esté en el template
- Tab Channel debe traer todos los providers (Omnibees etc · Fix #6)

### 2. Actualizar guías editoriales

**`rates-nodispo/_manual/GUIA_EDITORIAL_RatesNoDispo.html`**
- Documentar el sistema de bandas D · 5 niveles separando Sin Conversión
- Documentar la regla "Plan de Acción dentro de cada canasta"
- Documentar formato Excel estándar 13 pestañas
- Actualizar el ejemplo de Plan de Acción con la nueva estructura (owner arriba)

**`checkrates/_manual/GUIA_EDITORIAL_CheckRates.html`**
- Mismas actualizaciones que RND
- Documentar Channel agrupado (Producto Propio vs Third Party)
- Documentar formato Excel estándar 17 pestañas (vs 14 anterior)
- Documentar regla "Tab Channel debe traer todos los providers"

### 3. Actualizar playbook del mail

**`Playbook_Mail_Semanal.md`**
- Documentar el nuevo formato ejecutivo del mail (vs el formato W17 con KPI strips + 5 hallazgos por reporte)
- Estructura: Resumen ejecutivo + Plan de acción consolidado por owner + Links a reportes
- Plantilla de "Foco de la semana" como lead-in al plan de acción
- Decision: agrupar acciones por owner (no por horizonte) cuando aplican a la misma cohorte cross-reporte

### 4. Decisiones a validar con feedback W18

Antes de cristalizar la documentación, recoger respuestas a:

- ¿El nuevo mail ejecutivo es más útil que el formato W17?
- ¿La división por owner (Tech, Supply, Comercial, Pricing-Producto) tiene sentido para el equipo o conviene otra agrupación?
- ¿Los reportes editoriales completos (con KPIs hero, 10 findings, severity, etc.) se siguen leyendo o quedan como referencia profunda?
- ¿Falta alguna dimensión de análisis recurrente que no esté en los Excels? (ej. cohort de hoteles nuevos vs maduros)

---

## 📝 Acción específica para Week 19

1. **Lunes W19 (12 mayo):** revisar respuestas/feedback al mail W18
2. **Aplicar refactor de templates + guías + playbook** según feedback
3. **Commit `feat: Nivel C · templates y guías post W18 feedback`**
4. **Actualizar este documento** con el cambio de status

---

**Generado:** Mayo 2026 · post W18  
**Próxima revisión:** Lunes 12 de mayo (Week 19)
