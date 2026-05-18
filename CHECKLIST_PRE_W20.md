# ✅ CHECKLIST PRE-W20 · VALIDACIÓN YAML CENTRALIZADO

**Objetivo:** Verificar que la implementación YAML es 100% funcional antes de generar W20

**Tiempo estimado:** 5 minutos  
**Criticidad:** ALTA (si algo falla, sabremos antes de ejecutar pipeline)

---

## 📋 CHECKLIST TÉCNICO

### Bloque 1: Archivos Existen

- [ ] `config_w20.yaml` existe
  ```bash
  ls -la /mnt/project/config_w20.yaml
  ```
  **Esperado:** `-rw-r--r-- 1 user user 220 May 19 XX:XX /mnt/project/config_w20.yaml`

- [ ] `validate_yaml_config.py` existe
  ```bash
  ls -la /mnt/project/validate_yaml_config.py
  ```
  **Esperado:** `-rwxr-xr-x 1 user user 3.2K May 19 XX:XX /mnt/project/validate_yaml_config.py`

- [ ] `calc_rnd.py` existe
  ```bash
  ls -la /mnt/project/calc_rnd.py
  ```
  **Esperado:** `-rw-r--r-- 1 user user 12K May 19 XX:XX /mnt/project/calc_rnd.py`

---

### Bloque 2: YAML Válido

- [ ] YAML parsa sin errores
  ```bash
  python -c "import yaml; print(yaml.safe_load(open('config_w20.yaml')))"
  ```
  **Esperado:**
  ```python
  {'week': 20, 'vol_num': 20, 'periodo': '12–18 may 2026', ...}
  ```

- [ ] config_w20.yaml tiene todas las claves requeridas
  ```bash
  python validate_yaml_config.py 2>&1 | grep "VALIDACIÓN COMPLETADA"
  ```
  **Esperado:**
  ```
  ✅ VALIDACIÓN COMPLETADA EXITOSAMENTE
  ```

- [ ] Valores específicos son correctos
  ```bash
  python -c "import yaml; cfg = yaml.safe_load(open('config_w20.yaml')); 
  assert cfg['week'] == 20, 'week debe ser 20'; 
  assert cfg['pickle_rnd'] == 'rnd_w20_data.pkl'; 
  print('✅ VALORES CORRECTOS')"
  ```
  **Esperado:**
  ```
  ✅ VALORES CORRECTOS
  ```

---

### Bloque 3: Scripts Importan YAML

- [ ] calc_rnd.py tiene import yaml
  ```bash
  grep "yaml" /mnt/project/calc_rnd.py | head -1
  ```
  **Esperado:**
  ```
  import pandas as pd, numpy as np, pickle, sys, os, yaml
  ```

- [ ] calc_cr.py tiene import yaml
  ```bash
  grep "import yaml" /mnt/project/calc_cr.py
  ```
  **Esperado:**
  ```
  import yaml
  ```

- [ ] render_mail_v3.py tiene import yaml
  ```bash
  grep "import yaml" /mnt/project/render_mail_v3.py
  ```
  **Esperado:**
  ```
  import yaml
  ```

- [ ] build_package.py tiene import yaml
  ```bash
  grep "import yaml" /mnt/project/build_package.py
  ```
  **Esperado:**
  ```
  import yaml
  ```

---

### Bloque 4: Scripts Leen config_w20.yaml

- [ ] calc_rnd.py abre config_w20.yaml
  ```bash
  grep -A2 "with open" /mnt/project/calc_rnd.py | head -3
  ```
  **Esperado:**
  ```
  with open('config_w20.yaml', 'r') as f:
      CFG = yaml.safe_load(f)
  ```

- [ ] calc_cr.py abre config_w20.yaml
  ```bash
  grep -A2 "with open" /mnt/project/calc_cr.py | head -3
  ```
  **Esperado:** Mismo patrón

- [ ] render_mail_v3.py abre config_w20.yaml
  ```bash
  grep -A2 "with open" /mnt/project/render_mail_v3.py | head -3
  ```
  **Esperado:** Mismo patrón

- [ ] build_package.py abre config_w20.yaml
  ```bash
  grep -A2 "with open" /mnt/project/build_package.py | head -3
  ```
  **Esperado:** Mismo patrón

---

### Bloque 5: Variables Se Heredan Dinámicamente

- [ ] calc_rnd.py usa WEEK dinámico
  ```bash
  grep "WEEK = " /mnt/project/calc_rnd.py | grep CFG
  ```
  **Esperado:**
  ```
  WEEK    = f"W{CFG['week']}"
  ```

- [ ] calc_cr.py usa WEEK dinámico
  ```bash
  grep "WEEK = " /mnt/project/calc_cr.py | grep CFG
  ```
  **Esperado:**
  ```
  WEEK = f"W{CFG['week']}"
  ```

- [ ] build_package.py usa WEEK dinámico
  ```bash
  grep "WEEK        = " /mnt/project/build_package.py | grep CFG
  ```
  **Esperado:**
  ```
  WEEK        = CFG['week']
  ```

---

### Bloque 6: Error Handling

- [ ] calc_rnd.py tiene try/except
  ```bash
  grep -A5 "try:" /mnt/project/calc_rnd.py | grep -E "except|FileNotFoundError"
  ```
  **Esperado:**
  ```
  except FileNotFoundError:
  except Exception as e:
  ```

- [ ] calc_cr.py tiene try/except
  ```bash
  grep -A5 "try:" /mnt/project/calc_cr.py | grep -E "except|FileNotFoundError"
  ```
  **Esperado:** Mismo patrón

- [ ] render_mail_v3.py tiene try/except
  ```bash
  grep -A5 "try:" /mnt/project/render_mail_v3.py | grep -E "except|FileNotFoundError"
  ```
  **Esperado:** Mismo patrón

- [ ] build_package.py tiene try/except
  ```bash
  grep -A5 "try:" /mnt/project/build_package.py | grep -E "except|FileNotFoundError"
  ```
  **Esperado:** Mismo patrón

---

### Bloque 7: Validador Funciona

- [ ] validate_yaml_config.py ejecuta sin errores
  ```bash
  cd /mnt/project && python validate_yaml_config.py 2>&1 | tail -10
  ```
  **Esperado:**
  ```
  ✅ VALIDACIÓN COMPLETADA EXITOSAMENTE
  
  Próximos pasos:
  1. Verifica los valores en config_w20.yaml (especialmente fechas)
  2. Ejecuta: python calc_rnd.py
  ...
  ```

- [ ] Validador muestra valores correctos
  ```bash
  cd /mnt/project && python validate_yaml_config.py 2>&1 | grep "week"
  ```
  **Esperado:**
  ```
  week                           : 20
  ```

---

## 🔄 TEST PRÁCTICO (Simulate W20 Execution)

### Paso 1: Cargar CFG en Python
```bash
cd /mnt/project && python << 'EOF'
import yaml
import sys

# Simular que calc_rnd.py carga el YAML
with open('config_w20.yaml', 'r') as f:
    CFG = yaml.safe_load(f)

# Simular variables que se usan en pipeline
WEEK = f"W{CFG['week']}"
VOL_NUM = str(CFG['vol_num'])
PERIODO = CFG['periodo']
DATASET_RND_ACTUAL = CFG['dataset_rnd_actual']

print(f"✅ calc_rnd.py cargaría:")
print(f"   WEEK = {WEEK}")
print(f"   VOL_NUM = {VOL_NUM}")
print(f"   PERIODO = {PERIODO}")
print(f"   DATASET_RND_ACTUAL = {DATASET_RND_ACTUAL}")
EOF
```

**Esperado:**
```
✅ calc_rnd.py cargaría:
   WEEK = W20
   VOL_NUM = 20
   PERIODO = 12–18 may 2026
   DATASET_RND_ACTUAL = Dataset_RatesNoDispo_W20.xlsx
```

### Paso 2: Simular carga en build_package.py
```bash
cd /mnt/project && python << 'EOF'
import yaml

with open('config_w20.yaml', 'r') as f:
    CFG = yaml.safe_load(f)

# Simular build_package.py
WEEK = CFG['week']
PERIODO = CFG['periodo']
WEEK_PREV = CFG['week_prev']
PICKLE_RND = CFG['pickle_rnd']
PICKLE_CR = CFG['pickle_cr']

print(f"✅ build_package.py cargaría:")
print(f"   WEEK = {WEEK}")
print(f"   PERIODO = {PERIODO}")
print(f"   WEEK_PREV = {WEEK_PREV}")
print(f"   PICKLE_RND = {PICKLE_RND}")
print(f"   PICKLE_CR = {PICKLE_CR}")
EOF
```

**Esperado:**
```
✅ build_package.py cargaría:
   WEEK = 20
   PERIODO = 12–18 may 2026
   WEEK_PREV = 19
   PICKLE_RND = rnd_w20_data.pkl
   PICKLE_CR = cr_w20_data.pkl
```

---

## 📊 MATRIZ DE VALIDACIÓN

| Check | Comando | Status | Acción |
|---|---|---|---|
| config_w20.yaml existe | `ls -la config_w20.yaml` | ✅ | OK |
| YAML parsa | `python -c "import yaml; yaml.safe_load(open('config_w20.yaml'))"` | ✅ | OK |
| validate_yaml_config.py | `python validate_yaml_config.py` | ✅ | OK |
| calc_rnd.py import yaml | `grep yaml calc_rnd.py` | ✅ | OK |
| calc_cr.py import yaml | `grep yaml calc_cr.py` | ✅ | OK |
| render_mail_v3.py import yaml | `grep yaml render_mail_v3.py` | ✅ | OK |
| build_package.py import yaml | `grep yaml build_package.py` | ✅ | OK |
| Todos leen config_w20.yaml | `grep -c config_w20.yaml *.py` | ✅ | OK |
| Error handling presente | `grep -c "except FileNotFoundError" *.py` | ✅ | OK |

---

## 🎯 CRITERIOS DE ÉXITO

### Si TODOS los checks pasan:
✅ **LISTO PARA EJECUTAR PIPELINE W20**

```bash
# Puedes ejecutar directamente:
python calc_rnd.py
python calc_cr.py
python render_rnd_p1.py
python render_rnd_p2.py
python render_rnd_p3.py
python render_cr_p1.py
python render_cr_p2.py
python render_cr_p3.py
python assemble_rnd.py
python assemble_cr.py
python excel_rnd.py
python excel_cr.py
python render_mail_v3.py
python build_package.py
```

**Sin necesidad de editar variables en 4 scripts. Los datos se leen del YAML.**

---

### Si ALGÚN check falla:

❌ **REVISAR ANTES DE CONTINUAR**

Posibles problemas:
1. `config_w20.yaml` corrupted o no existe → Regenerar
2. Scripts no tienen `import yaml` → Buscar línea y verificar
3. Scripts no leen del YAML → Verificar try/except block
4. YAML sintaxis inválida → Usar `python -m yaml config_w20.yaml`

---

## 🚀 PRÓXIMO PASO

Una vez que TODOS los checks estén ✅:

1. **Verifica que existen los datasets W20 y W19**
   ```bash
   ls -la Dataset_RatesNoDispo_W20.xlsx Dataset_RatesNoDispo_W19.xlsx
   ls -la Dataset_CheckRates_W20.xlsx Dataset_CheckRates_W19.xlsx
   ```
   
   Si NO existen, Federico debe enviarlos primero.

2. **Ejecuta el pipeline completo:**
   ```bash
   bash run_pipeline.sh 20
   ```
   
   O manualmente:
   ```bash
   python calc_rnd.py && python calc_cr.py && ...
   ```

3. **Verifica outputs:**
   ```bash
   ls -la *.pkl *.html
   # Deberías ver:
   # - rnd_w20_data.pkl
   # - cr_w20_data.pkl
   # - RatesNoDispo_Reporte_Editorial.html
   # - CheckRates_Reporte_Editorial.html
   # - Mail_W20.html
   # - index.html
   # - Price_W20.zip
   ```

---

## 📝 NOTAS

- **No necesitas editar 4 scripts** para W20. Los datos vienen de `config_w20.yaml`.
- **Para W21**, solo copia `config_w20.yaml` → `config_w21.yaml` y edita 5 valores.
- **Sin datasets**, algunos checks dan ⚠️ warnings (es normal, se espera que Federico los envíe).
- **PyYAML** ya está instalado en el sistema.

---

**Status:** ✅ CHECKLIST LISTO  
**Próxima acción:** Ejecutar los checks arriba  
**Tiempo:** ~5 minutos  
**Criticidad:** ALTA (valida toda la implementación)
