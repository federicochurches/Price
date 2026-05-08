# Mapa de Dependencias · Proyecto PRICE
# Consultar SIEMPRE antes de cerrar un cambio

## RND — Tabs / Hero (cards KPI)
- render_rnd_p1.py
- asset_rnd_head.html
- _TEMPLATE_RatesNoDispo_Reporte.html
- GUIA_EDITORIAL_RatesNoDispo.html
- RatesNoDispo_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## RND — Alertas globales
- render_rnd_p1.py
- template_alertas.py
- GUIA_EDITORIAL_RatesNoDispo.html
- RatesNoDispo_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## RND — Resumen Ejecutivo global
- render_rnd_p2.py
- template_resumen.py
- GUIA_EDITORIAL_RatesNoDispo.html
- RatesNoDispo_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## RND — Severity global
- render_rnd_p2.py
- template_severity.py
- engine.py (si cambian bandas)
- BANDAS.md (si cambian bandas)
- GUIA_EDITORIAL_RatesNoDispo.html
- RatesNoDispo_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## RND — Análisis por canasta (p3)
- render_rnd_p3.py
- GUIA_EDITORIAL_RatesNoDispo.html
- RatesNoDispo_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## RND — Cálculos / métricas
- calc_rnd.py
- engine.py (si cambian bandas o thresholds)
- BANDAS.md (si cambian bandas)
- GUIA_EDITORIAL_RatesNoDispo.html
- CHANGELOG.md

## CR — Tabs / Hero
- render_cr_p1.py
- asset_cr_head.html
- _TEMPLATE_CheckRates_Reporte.html
- GUIA_EDITORIAL_CheckRates.html
- CheckRates_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## CR — Alertas globales
- render_cr_p1.py
- template_alertas.py
- GUIA_EDITORIAL_CheckRates.html
- CheckRates_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## CR — Resumen Ejecutivo global
- render_cr_p2.py
- template_resumen.py
- GUIA_EDITORIAL_CheckRates.html
- CheckRates_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## Helpers compartidos (render_helpers, engine, areas_catalogo)
- render_helpers.py / engine.py / areas_catalogo.py
- render_rnd_p1.py + p2.py + p3.py
- render_cr_p1.py + p2.py + p3.py
- GUIA_EDITORIAL_RatesNoDispo.html
- GUIA_EDITORIAL_CheckRates.html
- CHANGELOG.md

## Hub
- _TEMPLATE_Hub.html
- index.html
- build_package.py
- CHANGELOG.md

## CSS / Colores RND
- asset_rnd_head.html
- _TEMPLATE_RatesNoDispo_Reporte.html
- GUIA_EDITORIAL_RatesNoDispo.html
- RatesNoDispo_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## CSS / Colores CR
- asset_cr_head.html
- _TEMPLATE_CheckRates_Reporte.html
- GUIA_EDITORIAL_CheckRates.html
- CheckRates_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## Excel
- excel_rnd.py / excel_cr.py
- GUIA_EDITORIAL correspondiente
- CHANGELOG.md

## Mail
- render_mail_v3.py
- mail_template.html
- Playbook_Mail_Semanal.md
- CHANGELOG.md

---

## 🔍 Validaciones obligatorias antes de cerrar cada cambio

### Para cambios de label / nomenclatura (ej: "Demanda NC" → "Demanda No Convertida")
Buscar con `grep -rn "término viejo" /mnt/project/` y actualizar TODOS los archivos que lo referencien:
- Scripts Python (`render_*.py`, `calc_*.py`, `excel_*.py`)
- Assets HTML (`asset_*.html`)
- Templates (`_TEMPLATE_*.html`) — **verificar si el label está hardcodeado o viene del pipeline**. Si viene del pipeline, el template no necesita cambios en el label, pero sí en los ejemplos de datos (ej: nombres de país en tabs de ejemplo)
- Guías editoriales (`GUIA_EDITORIAL_*.html`)
- Documentación (`PROMPT_MAESTRO_v3.md`, `ESTRUCTURA_TEMPLATE.md`, `README_complemento.md`, `CHANGELOG.md`)
- Reporte editorial publicado (`*_Reporte_Editorial.html`)

**Regla para templates:** los labels de tabs y las acciones del Plan de Acción vienen del pipeline (`render_rnd_p2.py`), no del template HTML. El template solo tiene CSS y ejemplos de datos. Verificar siempre si hay datos de ejemplo hardcodeados (nombres de país, hoteles, destinos) que también necesiten normalización.

### Para cambios de CSS / colores
- Verificar que NO hay selectores que sobreescriban el nuevo estilo
- Probar con HTML de prueba mínimo antes de aplicar al reporte completo
- Reconstruir siempre desde el original limpio — nunca acumular patches sobre patches

### Para cambios en Plan de Acción
Además de los archivos del mapa principal, verificar:
- `PROMPT_MAESTRO_v3.md` — sección de estructura del reporte
- `GUIA_EDITORIAL_CheckRates.html` — si menciona el plan en contexto compartido
- `_TEMPLATE_RatesNoDispo_Reporte.html` — **NO** requiere cambios (acciones vienen del pipeline, no del template)

### Script de verificación rápida
Ejecutar al final de cada cambio antes de entregar archivos:

```python
checks = {
    'archivo.py': ['string_1', 'string_2'],
    'guia.html':  ['string_1'],
}
for path, patterns in checks.items():
    with open(f"/mnt/user-data/outputs/{path}") as f: c = f.read()
    fails = [p for p in patterns if p not in c]
    print(f"{'✅' if not fails else '❌'} {path}" + (f": falta {fails}" if fails else ""))
```

### Regla general
**Antes de cerrar cualquier cambio:** correr `grep -rn "término_clave" /mnt/project/` para detectar referencias no actualizadas en archivos que no son parte del flujo habitual.
