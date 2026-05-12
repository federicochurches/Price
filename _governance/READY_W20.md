# 🚀 PROYECTO PRICE · LISTO PARA W20

**Fecha de revisión:** 12 mayo 2026
**Estado:** 95% LISTO · 1 limpieza necesaria

---

## ✅ STATUS DE INTEGRIDAD

| Aspecto | Status | Detalles |
|---|---|---|
| Documentación | ✅ Completa | 10 archivos · PROMPT_MAESTRO_v3.md actualizado |
| Guías editoriales | ✅ Vigentes | RND + CR · referencia canónica visual |
| Pipeline core | ✅ Funcional | 6 pasos · todos alineados a W19 |
| Helpers | ✅ Actualizados | `template_seguimiento.py` integrado post-W19 |
| Assets HTML | ✅ Vigentes | CSS + colores correctos · W19 compatible |
| Archivos auxiliares | ⚠️ LIMPIEZA | `_TEMPLATE_Hub.html` debe eliminarse |

---

## ⚠️ UNA LIMPIEZA NECESARIA

### Eliminar archivo obsoleto
```bash
rm /mnt/project/_TEMPLATE_Hub.html
```

**Por qué:** Este archivo vive SOLO en GitHub bajo `_template/`, nunca en el proyecto Claude. 
Su presencia causa confusión y no se necesita para el pipeline.

**Después de eliminar:** Proyecto tendrá **46 archivos** (1 menos de lo actual).

---

## 📋 CONFIG SEMANAL PARA W20

Para pasar de W19 → W20, cambiar estas 5 variables en 4 scripts:

### 1️⃣ `calc_rnd.py` (líneas 24-28)
```python
WEEK     = 'W20'           # ← cambiar de W19
VOL_NUM  = '20'            # ← cambiar de 19
PERIODO  = '12–18 may 2026'  # ← ajustar fechas
MES_AÑO  = 'Mayo 2026'     # ← puede quedar igual
```

**Datasets esperados:**
- `Dataset_RatesNoDispo_W20.xlsx` (W20 actual)
- `Dataset_RatesNoDispo_W19.xlsx` (W19 anterior para WoW)

### 2️⃣ `calc_cr.py` (líneas 12-15)
```python
WEEK = 'W20'               # ← cambiar de W18
PERIODO = '12–18 may 2026' # ← ajustar fechas
MES_AÑO = 'Mayo 2026'      # ← puede quedar igual
VOL_NUM = '20'             # ← cambiar de 18
```

**Datasets esperados:**
- `Dataset_CheckRates_W20.xlsx` (W20 actual)
- `Dataset_CheckRates_W19.xlsx` (W19 anterior para WoW)

**Nota:** El output pickle es correcto: `cr_w19_data.pkl` está hardcodeado en línea 378. 
Para W20, se generará `cr_w20_data.pkl` automáticamente. ✅

### 3️⃣ `build_package.py` (líneas 16-27)
```python
WEEK        = 20                    # ← cambiar de 19
PERIODO     = '12–18 may 2026'     # ← ajustar fechas
FECHA_PUB   = 'Lunes 19 mayo 2026' # ← ajustar fecha publicación

WEEK_PREV        = 19               # ← cambiar de 18
PERIODO_PREV     = '5–11 may 2026' # ← ajustar fechas
WEEK_PREV2       = 18               # ← cambiar de 17
PERIODO_PREV2    = '27 abr – 3 may 2026'  # ← ajustar fechas

PICKLE_RND  = 'rnd_w20_data.pkl'   # ← cambiar de W19
PICKLE_CR   = 'cr_w20_data.pkl'    # ← cambiar de W19
```

### 4️⃣ `render_mail_v3.py` (líneas ~20-30 · verificar)
```python
WEEK = 'W20'               # ← cambiar de W19
PERIODO = '12–18 may 2026' # ← ajustar fechas
VOL_NUM = '20'             # ← cambiar de 19

PICKLE_RND = 'rnd_w20_data.pkl'  # ← cambiar de W19
PICKLE_CR = 'cr_w20_data.pkl'    # ← cambiar de W19
OUT_FILE = 'Mail_W20.html'       # ← cambiar de W19
```

### 5️⃣ `Mail_W20.html` en proyecto (DESPUÉS de Paso 5)
Una vez que `render_mail_v3.py` genera `Mail_W20.html`, subirlo al proyecto 
para que sea la referencia de la próxima semana.

---

## 🔄 WORKFLOW PIPELINE W20

```
1. Recibir 4 datasets (W20 + W19) de Federico
2. Verificar validación pre-pipeline:
   ✓ Dataset_RatesNoDispo_W20.xlsx  (9 columnas)
   ✓ Dataset_RatesNoDispo_W19.xlsx  (9 columnas)
   ✓ Dataset_CheckRates_W20.xlsx
   ✓ Dataset_CheckRates_W19.xlsx
3. Actualizar las 5 variables en 4 scripts (arriba)
4. Ejecutar pipeline 6 pasos:
   python calc_rnd.py     → rnd_w20_data.pkl
   python calc_cr.py      → cr_w20_data.pkl
   python render_rnd_p1.py + render_rnd_p2.py + render_rnd_p3.py
   python render_cr_p1.py + render_cr_p2.py + render_cr_p3.py
   python assemble_rnd.py  → RatesNoDispo_Reporte_Editorial.html
   python assemble_cr.py   → CheckRates_Reporte_Editorial.html
   python excel_rnd.py     → 4 Excels RND
   python excel_cr.py      → 4 Excels CR
   python render_mail_v3.py → Mail_W20.html
   python build_package.py  → index.html + Price_W20.zip
5. Subir Mail_W20.html al proyecto Claude
6. Subir Price_W20.zip al repo GitHub
```

---

## 🎯 PRE-FLIGHT CHECKLIST W20

```
ANTES DE EMPEZAR:
- [ ] Eliminar _TEMPLATE_Hub.html del proyecto
- [ ] Confirmar que calc_cr.py línea 378 tiene cr_w19_data.pkl (verificado ✅)
- [ ] Tener los 4 datasets en /mnt/user-data/uploads/
- [ ] Leer PROMPT_MAESTRO_v3.md completo

DURANTE PIPELINE:
- [ ] Cambiar 5 variables en 4 scripts
- [ ] Ejecutar pasos 1-6 en orden
- [ ] Verificar que cada paso genera output esperado
- [ ] Revisar HTML previamente en navegador

DESPUÉS DE PIPELINE:
- [ ] Agregar bloque Week 20 en CHANGELOG.md
- [ ] Subir Mail_W20.html al proyecto
- [ ] Generar draft Gmail (via MAIL_DRAFT_FLUJO.md)
- [ ] Comprar Price_W20.zip al repo
```

---

## 📊 MÉTRICAS CONFIRMADAS W19 (última de referencia)

Estos valores están almacenados en los pickles W19 y se usarán como base para WoW W20:

**RND:**
- Global %NoDispo W19: verificar en `rnd_w19_data.pkl['M']['global_w18']`
- Global IPM W19: verificar en mismo lugar
- Cambios WoW vs W18: se calculan en render_rnd_p1.py + p2.py

**CR:**
- Global Eficacia W19: verificar en `cr_w19_data.pkl['M']['global_w18']`
- Global Conv Rate W19: verificar en mismo lugar
- Cambios WoW vs W18: se calculan en render_cr_p1.py + p2.py

---

## 🚨 COSAS QUE NO PUEDEN FALTAR

1. **Validación de 9 columnas RND:** CorpName · Hotel · PaisDestino · Destino · DistributionCategory · Trafico · %NoDispo · Bookings · gb_usd
2. **Validación de datasets:** no pueden tener ceros en las columnas de denominador (Trafico, CR_Unicos)
3. **WoW válido:** W(N-1) debe ser completo · si está vacío, WoW sale como `_WOW_NEUTRO`
4. **Bandas:** verificadas en engine.py · no requieren cambios para W20
5. **Colores:** verificados en assets CSS · no requieren cambios para W20
6. **Hub login:** credenciales `pricetravel` / `supply2026` · hardcodeadas en `build_package.py`

---

**Status final:** ✅ LISTO PARA W20 (tras eliminar _TEMPLATE_Hub.html)

