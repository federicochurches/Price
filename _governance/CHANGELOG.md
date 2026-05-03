# 📝 CHANGELOG · Prompt Maestro PRICE

Histórico de versiones del prompt maestro y decisiones consolidadas del proyecto.

---

## v2 · Mayo 2026 (post W17)

### Cambios mayores

#### Sistema de bandas Severity
- **Antes:** 5 niveles uniformes (Exitosa / A Revisar / Crítica / Muy Crítica / Súper Crítica) aplicados a todos los hoteles
- **Ahora:** Sistema D híbrido · Sin Conversión separada como cohorte estructural + 4 bandas D para los hoteles con conversión > 0
- **Razón:** antes 60% de hoteles caían en "Súper Crítica" porque tenían BKGS=0 · saturaba la severity y hacía que el reporte fuera poco accionable

#### Targets operativos definidos
- RND · RPM ≥ 3,0 (mediana de hoteles que sí convierten)
- CR · Conv Rate ≥ 2,0% (banda Aceptable)
- CR · Eficacia ≥ 97% (banda Exitosa)

#### Estructura visual del reporte editorial
- **H1 narrativo:** 2 líneas alineadas al margen (`display:block`) con destinos y corp en color principal del reporte
- **CR:** usar "concentración en X" (sin "crítica")
- **Pills Súper Crítica:** transparencia 80% (`rgba(22,22,22,.80)`) en lugar de negro mate sólido
- **KPIs hero:** 2 cards directas con tabs estilo folder (radio inputs ocultos + labels con border-radius)

#### Channel agrupado en CR
- **Producto Propio:** DerbySoft, Internal, HBSI, SynXis, Siteminder, Travelclick, Omnibees
- **Third Party:** Expedia, HotelBeds Apitude, Hotel Unico V2, Travelgate

#### Estándar Excel de Análisis
- **Top 50** en cada pestaña (antes Top 20)
- **Pestaña "Sin Conversión" SIEMPRE separada** de "Bajo Rendimiento"
- **CR · 14 pestañas estándar** (a partir de W18)
- **RND · 12-13 pestañas estándar**

#### Estructura del repo
- Sin subcarpetas `Editorial/` ni `Analisis/` dentro de `week-NN/`
- Archivos sueltos directamente en `week-NN/`
- Templates dentro de cada sección (`_template/`)
- Manuales dentro de cada sección (`_manual/`)
- Solo el template del Hub vive en `/_template/` raíz

### Reglas generales agregadas
- Findings del Resumen Ejecutivo siempre con mayúscula inicial
- Resumen Ejecutivo: 10 findings · 2 columnas · post-Alerts en cada `<details>` de canasta
- Links a Excel sin sufijo de week (la carpeta `week-NN/` ya identifica la semana)
- Mantener consistencia metodológica entre semanas para que los deltas WoW sean válidos

### Action items para data team
- **RND:** dataset crudo con `CorpName` en cada pestaña de canasta (no solo en Canasta ALL)
- **CR:** dataset crudo con columna `Destino` en cada fila

---

## v1 · Pre-W17

### Estado original del prompt

- 5 niveles de severity uniformes
- Top 20 en Excel de análisis
- Sin targets operativos definidos
- Channel CR no agrupado
- Estructura del repo con subcarpetas Editorial/Analisis (después se simplificó)
- H1 a una sola línea
- Pestañas Excel sin separar "Sin Conversión"

---

## 🔄 Proceso para futuros cambios

Cuando se decida un cambio importante:

1. **Discutirlo** en el chat semanal correspondiente
2. **Aplicarlo** al reporte de esa semana
3. **Documentarlo** acá en CHANGELOG (versión nueva)
4. **Actualizar** PROMPT_MAESTRO.md
5. **Actualizar** el prompt del proyecto Claude
6. **Actualizar** el README del repo si afecta estructura
7. **Actualizar** las guías editoriales si afecta estilo

### Cuándo bumpear versión
- **v2.x** (cambio menor): ajuste de color, texto, formato
- **v3** (cambio mayor): nuevo sistema de bandas, nuevo reporte, cambio estructural

---

**Última actualización:** Mayo 2026 · post W17
