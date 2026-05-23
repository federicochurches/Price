# Commit Guide · post Week 18

## Comando estándar de release

```bash
# Desde la raíz del repo Price/
cp -r W{NN}_Package/* .
git add .
git commit -m "feat: datos Week-NN · RatesNoDispo + CheckRates · sistema bandas D · DD-mes-YYYY"
git push origin main
```

## ⚠️ Regla crítica: siempre pushear el ZIP completo

Claude entrega un ZIP con **todos los archivos del repo** — no solo el HTML editorial.
Si solo pusheas el `RatesNoDispo_Reporte_Editorial.html`, Netlify publica el HTML nuevo
pero los scripts Python, templates, governance y guías quedan desactualizados.

**Procedimiento correcto:**

```bash
# 1. Descomprimir el ZIP de Claude en la raíz del repo
unzip -o PRICE_pack_W19_FULL.zip -d /ruta/a/Price/

# 2. Verificar qué cambió
git status

# 3. Agregar todo y commitear
git add .
git commit -m "feat: pack W19 · RND editorial + scripts + governance"
git push origin main
```

**Archivos que Claude actualiza en cada pack:**

| Archivo | Qué cambia |
|---|---|
| `rates-nodispo/week-NN/RatesNoDispo_Reporte_Editorial.html` | Reporte editorial con datos de la semana |
| `checkrates/week-NN/CheckRates_Reporte_Editorial.html` | Ídem CheckRates |
| `index.html` | Hub con nueva card de la semana |
| `_scripts/render_rnd_p*.py` | Pipeline RND si hubo cambios de lógica |
| `_scripts/render_cr_p*.py` | Pipeline CR ídem |
| `_docs/CHANGELOG.md` | Entry de la semana |
| `_docs/PROMPT_MAESTRO_v3.md` | Si hubo cambios de sistema |

**Si Claude entrega dos ZIPs** (ej. `PRICE_pack_W19.zip` y `PRICE_pack_W19_FULL.zip`),
usar siempre el `_FULL` — contiene todos los archivos, no solo el reporte.

## ⚠️ Riesgo de merge conflict · index.html

`index.html` es el único archivo que Claude genera Y que puede tener cambios
locales previos en el repo. Si hay divergencia entre ambas versiones, GitHub
publica el archivo **con los conflict markers crudos visibles** en producción
(texto `<<<<<<< HEAD`, `=======`, `>>>>>>>` renderizado en el HTML).

**Regla:** antes de hacer push de un `index.html` generado por Claude,
verificar que no hay cambios pendientes:

```bash
git status   # no debe mostrar index.html como modified/ahead
```

Si hay conflict, la solución más rápida es sobreescribir directamente:

```bash
cp /ruta/al/index_limpio.html index.html
git add index.html
git commit -m "fix: resolve conflict index.html"
git push origin main
```

> **Nunca hacer merge de `index.html` con conflict markers sin resolver —
> el HTML se publica con los markers como texto plano visible.**

## Estructura del repo (post Week 18)

```
Price/
├── README.md
├── index.html
├── _template/                                  # SOLO hub
│   └── _TEMPLATE_Hub.html
├── _docs/                                      # docs canónicas
├── _seguimiento/                               # carryover semanal
│   ├── BANDAS.md
│   ├── AREAS_ACCOUNTABLE.md
│   ├── ESTRUCTURA_TEMPLATE.md
│   ├── CHANGELOG.md
│   └── COMMIT_GUIDE.md                        ← este archivo
├── _scripts/                                   # pipeline Python
├── _email/                                     # mails (no se publica)
├── rates-nodispo/
│   ├── _template/_TEMPLATE_RatesNoDispo_Reporte.html
│   ├── _manual/GUIA_EDITORIAL_RatesNoDispo.html
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx
│       └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/
    ├── _template/_TEMPLATE_CheckRates_Reporte.html
    ├── _manual/GUIA_EDITORIAL_CheckRates.html
    └── week-NN/
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx
        └── Dataset_CheckRates_WNN.xlsx
```

## Validación post-commit · checklist visual

Esperar 1-2 min a que GitHub Pages / Netlify actualicen, luego verificar:

**Hub (`index.html`)**
- [ ] Header muestra `Week NN · DD Mes – DD Mes YYYY` (sin placeholders `{{}}` visibles)
- [ ] Lock footer muestra `Week NN` (no `{{SEMANA}}`)
- [ ] Cards clickeables navegan al reporte correcto
- [ ] Pills de historial W17/W16 funcionan con `event.stopPropagation()`
- [ ] No hay texto `<<<<<<< HEAD`, `=======` ni `>>>>>>>` visible en la página

> **Si aparecen placeholders `{{}}` o conflict markers:** el `index.html` se subió
> sin resolver. Sobreescribir con el archivo limpio generado por Claude y hacer push.

**Reporte RND**
- [ ] Header `Week NN`
- [ ] Card IPM con banda correcta · target ≥ $650
- [ ] Análisis por canasta: Alertas + Resumen + Severity + Síntesis + Plan

**Reporte CR**
- [ ] Header `Week NN`
- [ ] Card Eficacia + ConvRate con bandas correctas
- [ ] Análisis por canasta completo

## Mail

Abrir `_email/week-NN/Mail_WNN.html` · usar comando `Generá el draft del mail Week NN`
para crear el draft en Gmail vía Claude. Validar y enviar manualmente.
