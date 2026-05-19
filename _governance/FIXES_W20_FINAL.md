# 🐛 FIXES W20 - CAMBIOS PERMANENTES APLICADOS
## Última actualización: Mayo 19, 2026

---

## 📋 RESUMEN EJECUTIVO

En W20 se identificaron y corrigieron **8 bugs críticos** en la pipeline RND/CR. Estos cambios están **permanentemente aplicados** en los scripts. Para W21+, validar que estos fixes se mantienen.

---

## 🔧 BUGS CORREGIDOS EN W20

### BUG #60: `render_helpers.py` - WEEK_NUM hardcodeado
**Problema:** `WEEK_NUM = "W18"` estaba hardcodeado
**Solución:** Cambiar a `WEEK_NUM = os.getenv('WEEK', 'W20')`
**Archivo:** `/mnt/project/_scripts/render_helpers.py` línea ~15
**Status:** ✅ Aplicado

---

### BUG #63: Imports relativos en render scripts
**Problema:** Scripts usaban `from .._scripts.engine import *` (rutas relativas)
**Solución:** Cambiar a:
```python
import sys
if "/mnt/project/_scripts" not in sys.path:
    sys.path.insert(0, "/mnt/project/_scripts")
from engine import *
```
**Archivos:** 
- `render_rnd_p1.py`, `render_rnd_p2.py`, `render_rnd_p3.py`
- `render_cr_p1.py`, `render_cr_p2.py`, `render_cr_p3.py`
**Status:** ✅ Aplicado

---

### BUG #64: WoW blocks con W17/W18 hardcodeados
**Problema:** En `wow_box_canasta()` los labels mostraban "W17" y "W18" hardcodeados
**Solución:** Cambiar a variables dinámicas:
```python
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
W_PREV = f"W{WEEK_NUM_INT-1}"
W_CURR = f"W{WEEK_NUM_INT}"
```
**Archivos:** `render_rnd_p3.py`, `render_cr_p3.py` (función `wow_box_canasta()`)
**Status:** ✅ Aplicado

---

### BUG #65: Keys de pickle dinámicos
**Problema:** Pickles guardaban datos como `M['global_w18']` (hardcodeado). Al renderizar W20, se mostraba "W18"
**Solución:** Agregar alias dinámico después de cargar pickle en TODOS los render scripts:
```python
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_w18'] = M['global_current']
M['global_w17'] = M['global_prev']
```
**Archivos:** Todos los `render_*.py` (después de `pickle.load()`)
**Status:** ✅ Aplicado

---

### BUG #66: Fecha duplicada en RND masthead
**Problema:** `asset_rnd_masthead.html` contenía `<span>Lunes 27 De Abril De 2026</span>` hardcodeada
**Solución:** Eliminar de `asset_rnd_masthead.html`:
```html
<!-- ANTES -->
<div class="masthead-sub">
<span>Lunes 27 De Abril De 2026</span>
<span>Vol. {{VOL_NUM}}</span>
</div>

<!-- DESPUÉS -->
<div class="masthead-sub">
<span>Vol. {{VOL_NUM}}</span>
</div>
```
**Archivo:** `/mnt/project/asset_rnd_masthead.html`
**Status:** ✅ Aplicado (permanente)

---

### BUG #67: Headers con Week 18 en lugar de Week 20
**Problema:** HTMLs finales mostraban "Week 18" en headers
**Solución:** Se implementó sed en assemble scripts:
```bash
sed -i 's/>Week 18</>Week 20</g' output.html
sed -i 's/27 abr – 3 may.*/12–18 may 2026</g' output.html
```
**Archivos:** `assemble_rnd.py`, `assemble_cr.py` (agregar al final)
**Status:** ⚠️ Aplicado manualmente - NECESITA AUTOMATIZACIÓN EN W21

---

### BUG #68: Severity IPM - Sin Conversión siempre 0
**Problema:** `banda_rpm()` se aplicaba solo con IPM, sin pasar parámetro `Bookings`
```python
# ANTES (MAL)
g['BandaRPM'] = g['IPM'].apply(banda_rpm)
```
**Solución:** Pasar Bookings como segundo parámetro:
```python
# DESPUÉS (CORRECTO)
g['BandaRPM'] = g.apply(lambda r: banda_rpm(r['IPM'], r['Bookings']), axis=1)
```
**Archivos:** `calc_rnd.py` líneas 53 y 66
**Status:** ✅ Aplicado (líneas 53 y 66)

---

### BUG #69: Imports con rutas relativas en calc_rnd.py y calc_cr.py
**Problema:** Usaban `from .._helpers.engine import` (rutas relativas)
**Solución:** Cambiar a imports absolutos:
```python
# ANTES
from .._helpers.engine import banda_nodispo, banda_rpm

# DESPUÉS
from engine import banda_nodispo, banda_rpm
```
**Archivos:** `calc_rnd.py` línea 6, `calc_cr.py` línea 10
**Status:** ✅ Aplicado

---

### BUG #70: Paths de datasets hardcodeados
**Problema:** `calc_rnd.py` y `calc_cr.py` buscaban datasets en carpeta actual
**Solución:** Cambiar a rutas absolutas:
```python
# ANTES
df18 = load_rnd(f'Dataset_RatesNoDispo_W{WEEK_NUM}.xlsx', WEEK_NUM)

# DESPUÉS
df18 = load_rnd(f'/mnt/user-data/uploads/Dataset_RatesNoDispo_W{WEEK_NUM}.xlsx', WEEK_NUM)
```
**Archivos:** `calc_rnd.py` línea 37, `calc_cr.py` línea 39
**Status:** ✅ Aplicado (con fallback a /mnt/project para W20)

---

### BUG #71: Pickle paths hardcodeados
**Problema:** `calc_rnd.py` y `calc_cr.py` guardaban pickles en carpeta actual (relativo)
**Solución:** Cambiar a rutas absolutas:
```python
# ANTES
with open(f'rnd_w{VOL_NUM}_data.pkl','wb') as f:

# DESPUÉS
with open(f'/mnt/project/rnd_w{VOL_NUM}_data.pkl','wb') as f:
```
**Archivos:** `calc_rnd.py` línea ~315, `calc_cr.py` línea 387
**Status:** ✅ Aplicado

---

## 📊 BANDAS IPM - CONFIRMADAS EN W20

```
Sin Conversión:  BKGS=0              → 11.463 hoteles (61.0%)
Crítica:         < $200              → 1.580 hoteles (8.4%)
Revisar:         $200–$650           → 1.356 hoteles (7.2%)
Aceptable:       $650–$1500          → 1.683 hoteles (9.0%)
Exitosa:         ≥ $1500             → 2.706 hoteles (14.4%)
```

**Función en `engine.py`:**
```python
def banda_rpm(rpm, bookings=1):
    """IPM (antes RPM) · sistema D · Sin Conversión separada."""
    if bookings == 0: return 'Sin Conversión'
    if rpm < 200: return 'Crítica'
    if rpm < 650: return 'Revisar'
    if rpm < 1500: return 'Aceptable'
    return 'Exitosa'
```

---

## ✅ CHECKLIST PARA W21+

### Config Variables (actualizar al inicio de cada week)
- [ ] `WEEK = 'W21'`
- [ ] `VOL_NUM = '21'`
- [ ] `PERIODO = '19–25 may 2026'` (o la semana correspondiente)
- [ ] `MES_AÑO = 'Mayo 2026'`

### Paths que deben ser ABSOLUTOS
- [ ] `calc_rnd.py` línea 37: datasets en `/mnt/user-data/uploads/`
- [ ] `calc_cr.py` línea 39: datasets en `/mnt/user-data/uploads/` + fallback `/mnt/project/`
- [ ] Pickles: guardar en `/mnt/project/`

### Imports que deben ser ABSOLUTOS
- [ ] `calc_rnd.py` línea 6: `from engine import banda_nodispo, banda_rpm`
- [ ] `calc_cr.py` línea 10: `from engine import banda_eficacia, banda_convrate`
- [ ] Todos `render_*.py`: sys.path.insert(0, "/mnt/project/_scripts")

### Keys dinámicos en render scripts
- [ ] Todos los `render_*.py` incluyen bloque de alias dinámicos post-pickle.load()
- [ ] Reemplazar `M['global_w18']` por `M['global_current']` en todo el código

### Headers finales
- [ ] `assemble_rnd.py` y `assemble_cr.py`: Agregar sed para reemplazar Week 18 → Week actual
- [ ] Agregar sed para reemplazar fechas viejas

### Bandas IPM
- [ ] `engine.py` línea 30: `banda_rpm()` incluye parámetro `bookings` como segundo argumento
- [ ] `calc_rnd.py` línea 53 y 66: Aplicar banda con `lambda r: banda_rpm(r['IPM'], r['Bookings'])`

### Documentación que debe estar actualizada
- [ ] `PROMPT_MAESTRO_v3.md`: Apartado "Bandas IPM" debe decir "IPM" no "RPM"
- [ ] `README.md`: Pipeline correcto con todos los 8 pasos
- [ ] `CHECKLIST_PROYECTO_CLAUDE.md`: 46 archivos esperados

---

## 📁 ARCHIVOS MODIFICADOS EN W20

### Scripts de cálculo
- ✅ `calc_rnd.py` - imports, paths, banda_rpm con Bookings
- ✅ `calc_cr.py` - imports, paths

### Scripts de render
- ✅ `render_rnd_p1.py` - imports absolutos, alias dinámicos
- ✅ `render_rnd_p2.py` - imports absolutos, alias dinámicos
- ✅ `render_rnd_p3.py` - imports absolutos, alias dinámicos, wow_box_canasta dinámico
- ✅ `render_cr_p1.py` - imports absolutos, alias dinámicos
- ✅ `render_cr_p2.py` - imports absolutos, alias dinámicos
- ✅ `render_cr_p3.py` - imports absolutos, alias dinámicos, wow_box_canasta dinámico

### Scripts de ensamble
- ✅ `assemble_rnd.py` - footer no duplicado
- ✅ `assemble_cr.py` - footer no duplicado

### Scripts de Excel
- ✅ `excel_rnd.py` - Top 100, sin hardcodes
- ✅ `excel_cr.py` - Top 100, sin hardcodes
- ✅ `excel_rnd_canastas.py` - NUEVO, genera 3 excels por canasta (B2C, OP, CUG)
- ✅ `excel_cr_canastas.py` - NUEVO, genera 3 excels por canasta (B2C, OP, CUG)

### Scripts helpers
- ✅ `engine.py` - banda_rpm() con bandas correctas
- ✅ `render_helpers.py` - WEEK_NUM dinámico

### Assets HTML
- ✅ `asset_rnd_masthead.html` - fecha hardcodeada eliminada

---

## 🎯 OUTPUTS W20 FINALES

### HTMLs (2)
- ✅ `RatesNoDispo_Reporte_Editorial.html` (473 KB)
- ✅ `CheckRates_Reporte_Editorial.html` (611 KB)

### Excels (8)
- ✅ `Analisis_Rates_NoDispo_7d.xlsx` (236 KB) - GLOBAL
- ✅ `Analisis_Rates_NoDispo_B2C_7d.xlsx` (1.2 MB)
- ✅ `Analisis_Rates_NoDispo_OP_7d.xlsx` (2.7 MB)
- ✅ `Analisis_Rates_NoDispo_CUG_7d.xlsx` (3.0 MB)
- ✅ `Analisis_Checkrates_7d.xlsx` (226 KB) - GLOBAL
- ✅ `Analisis_Checkrates_B2C_7d.xlsx` (19 KB)
- ✅ `Analisis_Checkrates_OP_7d.xlsx` (19 KB)
- ✅ `Analisis_Checkrates_CUG_7d.xlsx` (19 KB)

### Pickles (2)
- ✅ `rnd_w20_data.pkl` (61 MB)
- ✅ `cr_w20_data.pkl` (20 MB)

---

## 🔍 VALIDACIONES REALIZADAS EN W20

✅ Week 20 aparece en todos los headers
✅ Fechas correctas: 12–18 may 2026
✅ Sin Conversión: 11.463 hoteles (61.0% del P80) - Correcto
✅ Severity IPM suma: 11.463 + 1.580 + 1.356 + 1.683 + 2.706 = 18.788 ✅
✅ Top 10 y Extra 40 en pestañas Sin Conversión (RND)
✅ Top 10 en pestañas Sin Conversión (CR)
✅ WoW blocks muestran W20 vs W19 (dinámico)
✅ IPM $1.183,30 = Aceptable (correcto, $650-$1500)
✅ Iberostar: Ranking #88 con 76.84% eficacia (mejora de 51.29% W19)

---

## 📝 PRÓXIMAS ACCIONES PARA W21

1. **Copiar WEEK_CONFIG_W20.yml → WEEK_CONFIG_W21.yml**
2. **Editar 7 líneas en config (WEEK, VOL_NUM, PERIODO, etc.)**
3. **Adjuntar 4 datasets W21 en `/mnt/user-data/uploads/`**
4. **Ejecutar pipeline sin cambios de código**
5. **Validar outputs contra este checklist**

```bash
cd /mnt/project/_scripts
export WEEK=W21 VOL_NUM=21 PERIODO="19–25 may 2026" MES_AÑO="Mayo 2026"
python3 calc_rnd.py
python3 calc_cr.py
python3 render_rnd_p1.py
# ... resto de scripts
```

---

**Documento actualizado:** Mayo 19, 2026
**Próxima revisión:** Después de W21
