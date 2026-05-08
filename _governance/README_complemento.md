# Complemento Week 18 · Reorganización secciones globales con tabs

## Cambio aplicado

Las 6 secciones globales apiladas se consolidaron en 2 bloques con tabs:

**RND:**
- Sección 03 · Análisis por hotel (3 tabs · Demanda NC · Bajo Rend · Sin Conv)
- Sección 04 · Por dimensión (3 tabs · Corp · Destino · País)

**CR:**
- Sección 04 · Análisis por hotel (4 tabs · Críticos · Bajo Rend · Sin Conv · Menor ConvRate)
- Sección 05 · Por dimensión (3 tabs · Corp · Destino · Channel con split PP/TP)

Reduce ~40% la altura del editorial. Channel agrupado se mantiene como sección independiente.

## Archivos a actualizar en el proyecto

### Pipeline (6 archivos)
- `render_rnd_p1.py` · regenerado p1 (mismo CSS embebido del head)
- `render_rnd_p2.py` · funciones nuevas `render_bloque_hoteles()` + `render_bloque_dimensiones()`
- `render_cr_p1.py` · idem
- `render_cr_p2.py` · funciones `render_bloque_hoteles_cr()` + `render_bloque_dimensiones_cr()`
- `asset_rnd_head.html` · CSS de los tabs nuevos (`!important` para vencer base)
- `asset_cr_head.html` · idem

### Documentación (3 archivos)
- `ESTRUCTURA_TEMPLATE.md` · agregada estructura nueva + snippet HTML literal + CSS clave
- `CHANGELOG.md` · entrada nueva con before/after, beneficios, trade-offs
- `README.md` · actualizado el bloque "Secciones del Reporte Editorial"

### Guías editoriales (2 archivos)
- `GUIA_EDITORIAL_RatesNoDispo.html` · agregado bloque violeta con la nueva estructura
- `GUIA_EDITORIAL_CheckRates.html` · idem

## Bug encontrado y resuelto

CSS especificidad: la regla `.tab-panel{display:none}` del CSS hero original tenía la misma especificidad que `:checked ~ .tab-panels .tab-panel[data-tab="x"]{display:block}`. Por orden de cascada, `display:none` ganaba.

**Fix:** prefijar con `.tabs-block` Y usar `!important` en la regla de los nuevos tabs. Documentado en `ESTRUCTURA_TEMPLATE.md` para futuros casos.

## Validación post-deploy

1. Abrir reporte RND → sección 03 "Análisis por hotel" debe tener 3 tabs clicables
2. Click en BAJO REND → cambia el panel sin recargar página
3. Sección 04 "Por dimensión" → tabs Corp/Destino/País
4. Lo mismo en CR · sección 04 (4 tabs incluyendo Menor ConvRate)
5. Channel agrupado (cards comparadoras PP vs TP) debe seguir visible como sección 03 en CR
