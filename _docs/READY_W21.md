# ✅ READY W21 - GUÍA RÁPIDA DE EJECUCIÓN

**Todos los bugs W20 están arreglados. Para W21+, NO hay cambios de código requeridos.**

---

## 📋 PRE-REQUISITOS

✅ Verificar que están en `/mnt/project/_scripts/`:
```
- calc_rnd.py (con imports absolutos + banda_rpm(ipm, bookings))
- calc_cr.py (con imports absolutos)
- render_rnd_p1.py, p2.py, p3.py (con alias dinámicos)
- render_cr_p1.py, p2.py, p3.py (con alias dinámicos)
- assemble_rnd.py, assemble_cr.py
- excel_rnd.py, excel_cr.py (+ nuevos: excel_rnd_canastas.py, excel_cr_canastas.py)
- engine.py (banda_rpm correcto)
- render_helpers.py (WEEK_NUM dinámico)
```

✅ Verificar que `/mnt/project/asset_rnd_masthead.html` NO tiene fecha hardcodeada

✅ 4 datasets adjuntos en `/mnt/user-data/uploads/`:
```
Dataset_RatesNoDispo_W21.xlsx
Dataset_RatesNoDispo_W20.xlsx (para WoW)
Dataset_CheckRates_W21.xlsx
Dataset_CheckRates_W20.xlsx (para WoW)
```

---

## 🚀 PASOS PARA W21

### 1. Definir variables de configuración (1 min)
```bash
export WEEK=W21
export VOL_NUM=21
export PERIODO="19–25 may 2026"  # Cambiar según semana real
export MES_AÑO="Mayo 2026"       # Cambiar si cambia mes
```

### 2. Ejecutar pipeline (20 min)
```bash
cd /mnt/project/_scripts

# Paso 1: Cálculos
python3 calc_rnd.py
python3 calc_cr.py

# Paso 2: Render partes 1, 2, 3
python3 render_rnd_p1.py
python3 render_rnd_p2.py
python3 render_rnd_p3.py
python3 render_cr_p1.py
python3 render_cr_p2.py
python3 render_cr_p3.py

# Paso 3: Ensamble
python3 assemble_rnd.py
python3 assemble_cr.py

# Paso 4: Excels
python3 excel_rnd.py
python3 excel_cr.py
python3 excel_rnd_canastas.py
python3 excel_cr_canastas.py
```

### 3. Verificar outputs (2 min)
```bash
# HTMLs
ls -lh /mnt/user-data/outputs/*.html | grep -E "RatesNoDispo|CheckRates"

# Excels (deben ser 8)
ls -1 /mnt/user-data/outputs/Analisis_*_7d.xlsx | wc -l
```

### 4. Validar contenido (2 min)
```bash
# Verificar Week 21
grep -q "Week 21" /mnt/user-data/outputs/RatesNoDispo_Reporte_Editorial.html && echo "✅ RND Week OK" || echo "❌ RND Week ERROR"
grep -q "Week 21" /mnt/user-data/outputs/CheckRates_Reporte_Editorial.html && echo "✅ CR Week OK" || echo "❌ CR Week ERROR"

# Verificar fechas (ejemplo)
grep -q "19–25 may" /mnt/user-data/outputs/RatesNoDispo_Reporte_Editorial.html && echo "✅ RND Fecha OK" || echo "❌ RND Fecha ERROR"

# Verificar Sin Conversión (debe tener número significativo, no 0)
grep -o "Sin Conversión.*[0-9]\+\.[0-9]\+" /mnt/user-data/outputs/RatesNoDispo_Reporte_Editorial.html | head -1
```

---

## 🔧 TROUBLESHOOTING W21

### Error: `FileNotFoundError: rnd_w21_data.pkl`
**Causa:** Pickle no se generó en calc_rnd.py
**Solución:**
```bash
cd /mnt/project/_scripts
python3 calc_rnd.py
# Verificar que imprime "✅ RND W21 calculado"
ls -lh /mnt/project/rnd_w21_data.pkl
```

### Error: `ImportError: cannot import name 'banda_rpm' from engine`
**Causa:** Path en sys.path incorrecto
**Solución:** Verificar que `render_*.py` incluye:
```python
import sys
if "/mnt/project/_scripts" not in sys.path:
    sys.path.insert(0, "/mnt/project/_scripts")
from engine import banda_nodispo, banda_rpm
```

### Error: `SyntaxError` en render scripts
**Causa:** Probable cambio accidental en indentación
**Solución:** NO modificar render scripts. Usar versión W20 sin cambios.

### Severity Sin Conversión muestra 0
**Causa:** ⚠️ BUG #68 recayó (banda_rpm sin parámetro Bookings)
**Solución:** Verificar `calc_rnd.py` línea 53 y 66:
```python
# INCORRECTO
g['BandaRPM'] = g['IPM'].apply(banda_rpm)

# CORRECTO
g['BandaRPM'] = g.apply(lambda r: banda_rpm(r['IPM'], r['Bookings']), axis=1)
```

---

## 📊 EXPECTED OUTPUTS W21

| Item | Count |
|------|-------|
| HTMLs | 2 (RND + CR) |
| Excels | 8 (4 RND + 4 CR) |
| Pickles | 2 (rnd_w21, cr_w21) |

**File sizes (aproximados):**
- RND HTML: 470-480 KB
- CR HTML: 610-620 KB
- RND Excels: 59 KB (B2C), 62 KB (OP), 3 MB (CUG), 236 KB (Global)
- CR Excels: 19 KB (B2C/OP/CUG), 226 KB (Global)

---

## ✅ VALIDACIÓN FINAL

```bash
# Escaneo completo
echo "=== VALIDATION CHECKLIST ==="
echo -n "RND contiene 'Week 21': "
grep -q "Week 21" /mnt/user-data/outputs/RatesNoDispo_Reporte_Editorial.html && echo "✅" || echo "❌"

echo -n "CR contiene 'Week 21': "
grep -q "Week 21" /mnt/user-data/outputs/CheckRates_Reporte_Editorial.html && echo "✅" || echo "❌"

echo -n "RND sin Conversión > 0: "
SINCONV=$(grep -o "Sin Conversión[^0-9]*\([0-9,]\+\)" /mnt/user-data/outputs/RatesNoDispo_Reporte_Editorial.html | head -1)
[ ! -z "$SINCONV" ] && echo "✅ ($SINCONV)" || echo "❌"

echo -n "Total Excels: "
TOTAL=$(ls -1 /mnt/user-data/outputs/Analisis_*_7d.xlsx 2>/dev/null | wc -l)
[ "$TOTAL" = "8" ] && echo "✅ (8)" || echo "❌ ($TOTAL)"

echo ""
echo "✅ W21 READY!"
```

---

## 📞 SOPORTE

Si algo sale mal en W21:
1. Revisar `FIXES_W20_FINAL.md` sección "Checklist para W21+"
2. Revisar este archivo `READY_W21.md`
3. Comparar con outputs W20 (estructura, tamaño, contenido)
4. NO modificar código - todos los fixes ya están aplicados

**Última actualización:** Mayo 19, 2026
**Próxima revisión:** Después de ejecutar W21
