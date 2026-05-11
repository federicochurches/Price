# Mapa de Dependencias · Proyecto PRICE
# Consultar SIEMPRE antes de cerrar un cambio

## RND — Tabs / Hero (cards KPI)
- render_rnd_p1.py
- asset_rnd_head.html
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
- GUIA_EDITORIAL_CheckRates.html
- CheckRates_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## CR — Alertas globales
- render_cr_p2.py  ← post W18: alertas movidas de p1 a p2
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

## Hub · index.html  ← EXPANDIDO post W19
- **build_package.py** ← fuente canónica del hub · NUNCA editar index.html directamente
- rnd_wNN_data.pkl  (input · generado por calc_rnd.py)
- cr_wNN_data.pkl   (input · generado por calc_cr.py)
- index.html        (output · generado automáticamente · va a raíz del repo)
- CHANGELOG.md
- README.md (sección "Hub · index.html")
- MAPA_DEPENDENCIAS.md (esta sección)
- CHECKLIST_PROYECTO_CLAUDE.md

### Qué genera build_package.py
1. Lee pickles → extrae KPIs, WoW, bandas, severity counts
2. Genera `index.html` con:
   - Login overlay (pricetravel / supply2026)
   - Card featured W(N): KPI strip + severity pills RND + CR + links reportes/Excels
   - Card historial W(N-1): KPIs compactos + links
3. Escribe index.html en `/mnt/user-data/outputs/`
4. Arma ZIP con estructura completa del repo

### Cuándo actualizar build_package.py
- **Siempre (config):** cambiar `WEEK`, `PERIODO`, `FECHA_PUB`, `WEEK_PREV`, `PERIODO_PREV`
- **Si cambia el diseño del hub:** editar función `build_index()` dentro de build_package.py
- **Si cambian las credenciales del hub:** buscar `pricetravel` / `supply2026` en build_package.py

### Lo que NO hay que hacer
- ❌ Editar `index.html` directamente — se sobreescribe en cada ejecución
- ❌ Commitear `index.html` generado a mano — siempre vía build_package.py
- ❌ Hardcodear KPIs en el HTML — siempre derivar del pickle

## CSS / Colores RND
- asset_rnd_head.html
- GUIA_EDITORIAL_RatesNoDispo.html
- RatesNoDispo_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## CSS / Colores CR
- asset_cr_head.html
- GUIA_EDITORIAL_CheckRates.html
- CheckRates_Reporte_Editorial.html (W actual)
- CHANGELOG.md

## Excel
- excel_rnd.py / excel_cr.py
- GUIA_EDITORIAL correspondiente
- CHANGELOG.md

## Mail
- render_mail_v3.py  ← v3.2 · sin dependencia metrics_recalc.pkl
- Playbook_Mail_Semanal.md
- MAIL_DRAFT_FLUJO.md
- CHANGELOG.md

## ZIP / Release
- build_package.py  ← genera ZIP + index.html
- README.md (sección "Estructura del ZIP")
- COMMIT_GUIDE.md
- CHANGELOG.md

---

## 🔍 Validaciones obligatorias antes de cerrar cada cambio

### Para cambios de label / nomenclatura
Buscar con `grep -rn "término viejo" /mnt/project/` y actualizar TODOS los archivos que lo referencien:
- Scripts Python (`render_*.py`, `calc_*.py`, `excel_*.py`, `build_package.py`)
- Assets HTML (`asset_*.html`)
- Guías editoriales (`GUIA_EDITORIAL_*.html`)
- Documentación (`PROMPT_MAESTRO_v3.md`, `ESTRUCTURA_TEMPLATE.md`, `README.md`, `CHANGELOG.md`)

### Para cambios de CSS / colores
- Verificar que NO hay selectores que sobreescriban el nuevo estilo
- Para el hub: los colores de `build_package.py` deben coincidir con `asset_*_head.html`

### Para cambios en el hub (build_package.py)
1. Editar función `build_index()` dentro de `build_package.py`
2. Correr `python build_package.py` para validar que genera HTML válido
3. Actualizar esta sección del MAPA_DEPENDENCIAS.md
4. Actualizar README.md sección "Hub"

### Script de verificación rápida
```python
checks = {
    'build_package.py': ['build_index', 'WEEK', 'PERIODO', 'PICKLE_RND', 'PICKLE_CR'],
    'render_mail_v3.py': ['WEEK', 'PERIODO', 'PICKLE_RND', 'PICKLE_CR'],
}
for path, patterns in checks.items():
    with open(f"/mnt/project/{path}") as f: c = f.read()
    fails = [p for p in patterns if p not in c]
    print(f"{'✅' if not fails else '❌'} {path}" + (f": falta {fails}" if fails else ""))
```

### Regla general
**Antes de cerrar cualquier cambio:** correr `grep -rn "término_clave" /mnt/project/` para detectar referencias no actualizadas.
