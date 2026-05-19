# 📋 NIVEL C · Pendientes para Week 19

> **Decisión post Week 18:** los archivos correctos para esta semana se publicaron como Nivel B (deliverables + hub + README). Los templates y guías editoriales NO se actualizaron en Week 18 para dar tiempo a recoger feedback de los 12 destinatarios sobre el nuevo formato + glosario nuevo + catálogo de Áreas Accountable antes de cristalizar la documentación de proceso.
> 
> **Aplicar en Week 19** una vez tengamos respuestas/observaciones del equipo.

---

## ✅ Aplicado en Week 18 (Nivel B)

### Deliverables
- Carpetas `rates-nodispo/week-18/` y `checkrates/week-18/` con sus 3 archivos cada una
- Carpeta `_email/week-18/` con `Mail_W18.html` (estructura ejecutiva v3.1 con catálogo nuevo)
- `index.html` actualizado con cards Week 18 activas y Week 17 movido al archivo
- `README.md` del repo actualizado con Week 18, glosario nuevo de métricas y catálogo de Áreas Accountable v2
- `areas_catalogo.py` con catálogo definitivo

### Reportes editoriales Week 18
Fixes aplicados durante el ciclo de auditoría visual:

**Bandas D · 5 niveles:**
- Sin Conversión separada de Severity (cohorte estructural · BKGS=0)
- Severity con cuartiles del P80 procesable

**Layout y estilos:**
- Numeración de secciones cambió de "01" aislado a "SECCIÓN 01" overline pequeño
- Section subtitles con color del reporte (violet en CR, magenta en RND)
- Plan de acción · CSS reescrito (badge owner arriba, cluster/plazo/métrica abajo)
- Fondos sin pintar en plan acción (border-left coloreado por horizonte)
- WoW box · bg dinámico (verde mejora, rojo deterioro)
- Truncado nombres ampliado de 26 → 38 chars
- Tabs hero KPIs: 5 items en 1 columna
- Por Corporativo / Por Destino / Por País / Por Channel: 10 items en 2 columnas (5+5)
- Channel agrupado · paleta corp (Producto Propio violet + Third Party cyan)
- Por Channel · split visual Producto Propio + Third Party como sub-tablas

**Datos:**
- Filtro RPM>0 en alertas RND (excluir refunds/contracargos negativos)
- Filtro Bookings>0 y Eficacia>0 en alertas CR (excluir hoteles sin actividad)
- Filtro RPM>0 en bajo rendimiento canasta RND
- Filtro Bookings>0 y Eficacia>0 en críticos canasta CR
- Función `clean_hotel_name()` para parsear "(NNNNNN) - Nombre" → "Nombre"
- 19 invocaciones de clean_hotel_name en alertas, críticos, bajo rend, sin conv, plan, findings

**CSS bug fix:**
- Tabs CR no se renderizaban (el CSS del head usaba prefijos viejos `tab-nd-`/`tab-rpm-` mientras los inputs usaban `tab-ef-`/`tab-cv-`)

**Texto narrativo:**
- "W18" → "Week 18" / "W17" → "Week 17" en kickers, findings y referencias
- Mantenido "W18"/"W17" solo en widgets compactos (WoW boxes)

### Mail Week 18 v3.1 (innovaciones)
- Estructura ejecutiva: Resumen + Plan Consolidado por Área Accountable
- Glosario nuevo introducido con nota explicativa:
  - **RPM** = Reservas Por Millón = `Bookings/Trafico × 1M`
  - **GBM** = Gross Booking por Millón = `gb_usd/Trafico × 1M`
  - "%NoDispo" → "% de No Disponibilidad"
  - "owner" → "Área Accountable"
- Bandas calibradas con cuartiles del P80 procesable Week 18
- Deltas WoW recalculados con métricas nuevas (Week 17 recalculado)
- Plan agrupado por las 4 áreas accountable confirmadas

### Catálogo de Áreas Accountable · v2 (definitivo)
| Área | Acciones aplicadas |
|---|---|
| Supply Optimization | Escalamiento Súper Críticos, saneamiento severity |
| Supply Optimization / TPS | Diagnóstico Sin Conversión, auditoría Third Party |
| Supply Comercial / Supply Optimization | Cohorte Sin Conv (proyectos Q), casos críticos volumen |
| Supply Comercial / Wholesale | RPM/GBM por canasta, SLAs corporativos, B2C revisión |

## 🔧 Pendiente para Week 19 (Nivel C)

### 1. Actualizar templates HTML

**`_template/_TEMPLATE_Hub.html`**
- Validar si la estructura sigue funcionando bien después de varias semanas
- Considerar mostrar 4-5 semanas en archivo (no solo 2)

**`rates-nodispo/_template/_TEMPLATE_RatesNoDispo_Reporte.html`**
- Refactorizar con estructura Week 18 (badge owner, plan dentro de canasta, etc.)
- **Aplicar glosario nuevo:** RPM = Reservas/M, GBM = GB/M
- Recalibrar bandas según calibración del README
- CSS de `.action-row` con badge owner arriba
- Numeración "SECCIÓN NN" como overline
- 10 items en 2 columnas en secciones Por Corp / Por Destino / Por País

**`checkrates/_template/_TEMPLATE_CheckRates_Reporte.html`**
- Mismas refactorizaciones
- Por Channel · split Producto Propio + Third Party como sub-tablas
- Tab Channel debe traer todos los providers (no Top 5)

### 2. Actualizar guías editoriales

**`rates-nodispo/_manual/GUIA_EDITORIAL_RatesNoDispo.html`**
- Documentar sistema bandas D · 5 niveles separando Sin Conversión
- Documentar regla "Plan de Acción dentro de cada canasta"
- Documentar formato Excel estándar 13 pestañas
- **Documentar glosario nuevo de métricas (RPM, GBM)**
- **Documentar catálogo de Áreas Accountable v2**
- Documentar regla `clean_hotel_name()` para nombres con prefijo ID

**`checkrates/_manual/GUIA_EDITORIAL_CheckRates.html`**
- Mismas actualizaciones
- Documentar Channel agrupado (Producto Propio vs Third Party)
- Documentar formato Excel 17 pestañas (vs 14 anterior)
- Documentar split de Channel en sección dedicada

### 3. Engine code

**`engine.py` · funciones de bandas**
- Actualizar `banda_rpm()` para usar definición nueva (RPM = Reservas/M, no monetario)
- Crear nueva `banda_gbm()` con thresholds calibrados
- Actualizar `metrics_rnd_global()` para devolver ambas métricas
- Actualizar `aggregate_rnd()` para calcular ambas
- Migrar `clean_hotel_name()` desde render_helpers a engine para uso global

### 4. Actualizar playbook del mail

**`Playbook_Mail_Semanal.md`**
- Documentar formato ejecutivo del mail
- Estructura: Resumen + Plan consolidado por Área Accountable + Links Hub
- Plantilla "Foco de la semana"
- Decision: agrupar acciones por Área cuando aplican a la misma cohorte cross-reporte
- **Glosario nuevo de métricas como referencia rápida**
- **Catálogo de Áreas Accountable v2 como referencia rápida**

### 5. Decisiones a validar con feedback Week 18

Antes de cristalizar la documentación, recoger respuestas a:

- ¿El nuevo mail ejecutivo es más útil que el formato Week 17?
- ¿La división por las 4 Áreas Accountable (Supply Optimization, Supply Optimization / TPS, Supply Comercial / Supply Optimization, Supply Comercial / Wholesale) tiene sentido?
- ¿El nuevo glosario (RPM = Reservas, GBM = GB) es más claro o crea confusión?
- ¿Las bandas calibradas (RPM 2-4-7, GBM $200-$650-$1500) son apropiadas para los targets del negocio?
- ¿Falta alguna área en el catálogo de Áreas Accountable?
- ¿Falta alguna dimensión en los Excels?

---

## 📝 Acción específica para Week 19

1. **Lunes Week 19 (12 mayo):** revisar respuestas/feedback al mail Week 18
2. **Aplicar refactor completo** de templates + guías + engine + playbook
3. **Regenerar reportes Week 18 si fuera necesario** con nuevas bandas y glosario (decision pending)
4. **Commit `feat: Nivel C · templates y guías post Week 18 feedback`**

---

**Generado:** Mayo 2026 · post Week 18  
**Próxima revisión:** Lunes 12 de mayo (Week 19)
