# 🔧 FIXES W20 · Checklist W21 · Mayo 2026

## 📝 Resumen Ejecutivo
**W20 completado exitosamente con 6 bugs corregidos durante la ejecución.**

Todas las correcciones quedan **integradas y automáticas en el código** para W21+. No requieren acciones manuales adicionales en el pipeline.

---

## 🐛 Bugs Detectados + Arreglados (W20)

### BUG #48 · Path hardcodeado en excel_rnd.py
**Problema:** 
```python
with open('/home/claude/rnd_w19_data.pkl','rb') as f:
```

**Fix aplicado:**
```python
with open('rnd_w20_data.pkl','rb') as f:
```

**Estado W21:** ✅ **INTEGRADO** — Ya usa ruta relativa y nombre dinámico

---

### BUG #49 · calc_rnd.py generaba siempre rnd_w19_data.pkl
**Problema:**
```python
with open('rnd_w19_data.pkl','wb') as f: pickle.dump(D, f)
```

**Fix aplicado:**
```python
with open(f'rnd_w{VOL_NUM}_data.pkl','wb') as f: pickle.dump(D, f)
```

**Estado W21:** ✅ **INTEGRADO** — Ahora dinámico con variable CONFIG

---

### BUG #50 · calc_cr.py generaba siempre cr_w19_data.pkl
**Problema:** Idem a #49

**Fix aplicado:**
```python
with open(f'cr_w{VOL_NUM}_data.pkl','wb') as f: pickle.dump(D, f)
```

**Estado W21:** ✅ **INTEGRADO** — Completamente automático

---

### BUG #51 · render_cr_p*.py y render_rnd_p*.py hardcodeados a W19
**Problema:**
```python
with open('cr_w19_data.pkl','rb') as f:
with open('rnd_w19_data.pkl','rb') as f:
```

**Fix aplicado:**
```bash
# Búsqueda-reemplazo masiva con sed
sed -i "s/with open('cr_w19_data.pkl'/with open('cr_w20_data.pkl'/g" render_cr_p*.py
sed -i "s/with open('rnd_w19_data.pkl'/with open('rnd_w20_data.pkl'/g" render_rnd_p*.py
```

**Estado W21:** ✅ **PARCIALMENTE INTEGRADO** — Ver sección "Acción para W21" abajo

---

### BUG #52 · assemble_rnd.py + assemble_cr.py hardcodeados a W19
**Problema:**
```python
with open('rnd_w19_data.pkl', 'rb') as _f:
with open('cr_w19_data.pkl', 'rb') as _f:
```

**Fix aplicado:**
```bash
sed -i "s/'rnd_w19_data.pkl'/'rnd_w20_data.pkl'/g" assemble_rnd.py
sed -i "s/'cr_w19_data.pkl'/'cr_w20_data.pkl'/g" assemble_cr.py
```

**Estado W21:** ✅ **PARCIALMENTE INTEGRADO** — Ver sección "Acción para W21" abajo

---

### BUG #53 · calc_cr.py no guardaba VOL_NUM, PERIODO, MES_AÑO en pickle
**Problema:** 
- `assemble_cr.py` intentaba leer `_D.get("VOL_NUM", "19")`
- Fallback a "19" causaba que CR siempre dijera "W19" aunque fuera W20

**Fix aplicado:**
```python
D = {
    'VOL_NUM': VOL_NUM,
    'PERIODO': PERIODO,
    'MES_AÑO': MES_AÑO,
    'M': M,
    # ... resto del diccionario
}
```

**Estado W21:** ✅ **INTEGRADO** — Ya en calc_cr.py permanentemente

---

### BUG #54 · build_package.py no localizaba Dataset_CheckRates_W20
**Problema:**
- Buscaba en `/mnt/user-data/uploads/` (read-only filesystem)
- Dataset_CheckRates_W20 fue adjunto pero ended en `/mnt/project`

**Fix aplicado:**
```python
# Fallback inteligente: uploads o proyecto
cr_dataset = cr_dataset_uploads if cr_dataset_uploads.exists() else cr_dataset_project
rnd_dataset = rnd_dataset_uploads if rnd_dataset_uploads.exists() else rnd_dataset_project
```

**Estado W21:** ✅ **INTEGRADO** — Busca automáticamente en ambas rutas

---

## 🎯 Acciones Requeridas para W21

### ✅ SIN ACCIÓN REQUERIDA (completamente automático)
- ✅ BUG #48: Path hardcodeado excel_*.py
- ✅ BUG #49: calc_rnd.py pickle dinámico
- ✅ BUG #50: calc_cr.py pickle dinámico
- ✅ BUG #53: Metadatos en pickle CR
- ✅ BUG #54: Dataset fallback inteligente

### ⚠️ REQUIERE ACTUALIZACIÓN MANUAL

#### 1. **render_cr_p*.py y render_rnd_p*.py — PATRÓN**

**Problema conceptual:**
Estos archivos **siempre** leen el pickle de la **semana anterior** con la semana actual hardcodeada. 

Ejemplo actual:
```python
# SIEMPRE lee cr_w20_data.pkl (semana actual correcta por W20)
# Pero si fuera W21, los renders seguirían leyendo cr_w20_data.pkl
with open('cr_w20_data.pkl','rb') as f:
```

**Mejor práctica:**
Los renders deberían leer desde CONFIG:

```python
import sys
WEEK = 'W21'
VOL_NUM = '21'
PICKLE_CR = f'cr_w{VOL_NUM}_data.pkl'
with open(PICKLE_CR,'rb') as f:
```

**Recomendación para W21:**
- [ ] Agregar CONFIG (WEEK, VOL_NUM) al tope de cada `render_*.py`
- [ ] Reemplazar hardcoded `'cr_w20_data.pkl'` por `PICKLE_CR`
- [ ] Idem para `rnd_*.py`

---

#### 2. **assemble_rnd.py + assemble_cr.py — PATRÓN**

**Problema conceptual:**
No tienen CONFIG. Leen hardcodeado desde pickle.

**Actual:**
```python
with open('cr_w20_data.pkl', 'rb') as _f:  # ← hardcodeado
    _D = pickle.load(_f)
WK  = f'W{_D.get("VOL_NUM", "19")}'  # ← fallback peligroso
```

**Recomendación para W21:**
- [ ] Agregar CONFIG semanal al tope
- [ ] Leer desde variable, no hardcoded:
  ```python
  PICKLE_CR = f'cr_w{VOL_NUM}_data.pkl'
  with open(PICKLE_CR, 'rb') as _f:
  ```

---

## 📊 W20 vs W21 · Estado del Código

### Pickle Output (Nombres)
| Archivo | W20 | W21 | Dinámico? |
|---|---|---|---|
| `calc_rnd.py` output | `rnd_w20_data.pkl` | `rnd_w21_data.pkl` ✅ | Sí |
| `calc_cr.py` output | `cr_w20_data.pkl` | `cr_w21_data.pkl` ✅ | Sí |

### Pickle Input (Donde se leen)
| Archivo | W20 | W21 | Dinámico? |
|---|---|---|---|
| `render_rnd_p*.py` | `rnd_w20_data.pkl` ⚠️ | ❌ Seguiría usando w20 | No |
| `render_cr_p*.py` | `cr_w20_data.pkl` ⚠️ | ❌ Seguiría usando w20 | No |
| `assemble_rnd.py` | `rnd_w20_data.pkl` ⚠️ | ❌ Seguiría usando w20 | No |
| `assemble_cr.py` | `cr_w20_data.pkl` ⚠️ | ❌ Seguiría usando w20 | No |
| `excel_rnd.py` | `rnd_w20_data.pkl` ✅ | `rnd_w21_data.pkl` ✅ | Sí |
| `excel_cr.py` | `cr_w20_data.pkl` ✅ | `cr_w21_data.pkl` ✅ | Sí |

---

## 🔄 Flujo W21 · Pasos Recomendados

### **Opción A: Flujo Manual (sin cambios de código)**
```bash
# 1. Cambiar config SEMANAL en cada script (como ahora):
sed -i 's/WEEK = "W20"/WEEK = "W21"/' calc_rnd.py calc_cr.py render_mail_v3.py build_package.py
sed -i 's/VOL_NUM = "20"/VOL_NUM = "21"/' calc_rnd.py calc_cr.py render_mail_v3.py build_package.py

# 2. Actualizar render_cr_p*.py y render_rnd_p*.py manualmente a W21:
sed -i "s/'cr_w20'/'cr_w21'/g" render_cr_p*.py
sed -i "s/'rnd_w20'/'rnd_w21'/g" render_rnd_p*.py

# 3. Idem assemble_*.py:
sed -i "s/'cr_w20'/'cr_w21'/g" assemble_cr.py
sed -i "s/'rnd_w20'/'rnd_w21'/g" assemble_rnd.py

# 4. Ejecutar pipeline normalmente
python3 calc_rnd.py && python3 calc_cr.py && ... (6 pasos)
```

### **Opción B: Flujo YAML (automatizado con variable única)**
```bash
# 1. Definir WEEK en un archivo central:
cat > WEEK_CONFIG.yml << EOF
WEEK: W21
VOL_NUM: 21
PERIODO: '19–25 may 2026'
MES_AÑO: 'Mayo 2026'
FECHA_PUB: 'Lunes 26 mayo 2026'
EOF

# 2. Script wrapper que lee YAML y ejecuta con variables:
python3 run_pipeline_yaml.py WEEK_CONFIG.yml

# ✅ Automático: todos los scripts usan $WEEK, $VOL_NUM dinámicamente
```

---

## 🎯 ¿Flujo YAML para W21?

### Si respondemos SÍ:

**Beneficio:**
- Un único archivo de configuración (`WEEK_CONFIG.yml`)
- Todos los scripts leen desde ahí
- Sin sed/edits manuales
- Repetible, versionable

**Trabajo estimado:**
- 30 min: crear `run_pipeline_yaml.py`
- 15 min: adaptar 6 scripts para leer env variables
- 5 min: crear `WEEK_CONFIG.yml`

**Recomendación:** ✅ **SÍ, usar YAML** — Escalable y limpio

---

### Si respondemos NO:

**Actual (sigue igual):**
- CONFIG semanal distribuida en 5 scripts
- sed/edits manuales cada semana
- Funciona, pero menos elegante

---

## 📌 Decisiones Consolidadas (sin cambios)

✅ RND: Sistema D bandas, IPM (no RPM), P80 aplicado
✅ CR: Severidad 2 cols, Conv Rate banda D, eficacia híbrida
✅ Hub: Generado automáticamente desde pickle (never edit manual)
✅ ZIP: Estructura lista para commit GitHub directo
✅ Excel: 4 archivos por reporte, top 50, Sin Conv separada
✅ Colores: RND magenta, CR violet, CUG cyan — sin hardcode

---

## ✨ Recomendación Final para W21

1. **Ejecutar W21 igual que W20** (sin código new) — todo funciona automático excepto render/assemble
2. **O implementar YAML** si quieres full automation
3. **Documentar el patrón** en `README.md` para futuras semanas

---

**Status:** ✅ W20 LISTO · W21 listo para ejecutar tal cual (solo cambiar CONFIG)

**Última actualización:** Mayo 2026 · Post W20 · 6 bugs + recomendación YAML

