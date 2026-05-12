# 📝 TEXTO EXACTO A AGREGAR EN PROMPT_MAESTRO_v3.md

---

## 🎯 UBICACIÓN EN EL ARCHIVO

Al **FINAL del archivo** PROMPT_MAESTRO_v3.md, **después** de la última línea de "Última actualización", agrega esto:

---

## 📋 TEXTO A COPIAR Y PEGAR

```markdown
## 📝 Cambios post W19 · Mayo 2026 (sesión corrección arquitectura repo/proyecto)

### Corrección crítica: Arquitectura repo vs Proyecto Claude

**Versión anterior (INCORRECTA):**
```
❌ Scripts bash NO van al repo
❌ Solo en proyecto Claude (local)
❌ Repo contiene solo Python + outputs
```

**Versión correcta (AHORA):**
```
✅ Scripts bash SÍ van al repo (en _scripts/)
✅ Documentación operacional va al repo (en _governance/)
✅ El repo es la fuente única de verdad
✅ El proyecto Claude es un espejo para ejecutar localmente
```

### Estructura definida

#### REPO GITHUB · federicochurches/Price
```
_governance/
├── PROMPT_MAESTRO_v3.md
├── audit_wXX.md
├── READY_wXX.md
├── STATUS_FINAL_wXX.md
├── INSTRUCCIONES_FINALES_wXX.md
└── ... (documentación oficial)

_scripts/
├── setup_week.sh          ← VA AL REPO
├── run_pipeline.sh        ← VA AL REPO
├── package_project.sh     ← VA AL REPO
├── sync_project.sh        ← VA AL REPO
├── calc_rnd.py
├── calc_cr.py
├── render_*.py (6)
├── assemble_*.py (2)
├── excel_*.py (2)
├── build_package.py
└── ... (pipeline core)

rates-nodispo/week-NN/ · checkrates/week-NN/
├── Reportes HTML editoriales
├── 4 Excels por reporte
└── Datasets crudos
```

#### PROYECTO CLAUDE · /mnt/project/
```
Espejo exacto del repo:
- Todos los scripts (Python + Bash)
- Toda la documentación
- Se mantiene sincronizado con repo

Flujo:
1. Cambios en repo GitHub
2. git push origin main
3. bash sync_project.sh NN  (en proyecto Claude)
4. Proyecto actualizado ✅
```

### Implicaciones para W20+

**Pipeline W20 y siguientes:**
```
1. Recibir datasets W20
2. bash setup_week.sh 20 "PERIODO" "MES" 19 "PERIODO_PREV"
3. bash run_pipeline.sh 20
4. Validar outputs (HTML + Excel)
5. cd Price/ && git add . && git push
6. bash sync_project.sh 20 (para actualizar proyecto Claude)
```

**No hay iteración manual entre repo y proyecto.**
**Es automatizada vía sync_project.sh**

### Cambios en PROMPT_MAESTRO_v3.md

Las secciones anteriores que mencionaban:
```
❌ "setup_week.sh solo en proyecto Claude"
❌ "run_pipeline.sh no va al repo"
```

**Han sido reemplazadas por esta arquitectura correcta** que refleja la realidad del proyecto PRICE.

---

Última actualización: Mayo 2026 · post W19 · corrección arquitectura repo/proyecto · definición estructura definitiva para W20+
```

---

## 📌 INSTRUCCIONES DE EDICIÓN

### Opción A: Copiar el texto completo
1. Copia todo lo que está en los 3 bloques de código (```markdown...```)
2. Ve a PROMPT_MAESTRO_v3.md en el proyecto Claude
3. Baja hasta el final del archivo
4. Busca la última línea que dice "**Última actualización:**"
5. Después de esa línea, pega el texto nuevo

### Opción B: Usar str_replace en Claude
```
old_str: "**Última actualización:** Mayo 2026 · post W19 · fixes visuales canastas + nomenclatura + WoW pills + build_package limpieza · bugs #37–#46"

new_str: "**Última actualización:** Mayo 2026 · post W19 · fixes visuales canastas + nomenclatura + WoW pills + build_package limpieza · bugs #37–#46

## 📝 Cambios post W19 · Mayo 2026 (sesión corrección arquitectura repo/proyecto)

### Corrección crítica: Arquitectura repo vs Proyecto Claude

**Versión anterior (INCORRECTA):**
```
❌ Scripts bash NO van al repo
❌ Solo en proyecto Claude (local)
❌ Repo contiene solo Python + outputs
```

**Versión correcta (AHORA):**
```
✅ Scripts bash SÍ van al repo (en _scripts/)
✅ Documentación operacional va al repo (en _governance/)
✅ El repo es la fuente única de verdad
✅ El proyecto Claude es un espejo para ejecutar localmente
```

### Estructura definida

#### REPO GITHUB · federicochurches/Price
```
_governance/
├── PROMPT_MAESTRO_v3.md
├── audit_wXX.md
├── READY_wXX.md
├── STATUS_FINAL_wXX.md
├── INSTRUCCIONES_FINALES_wXX.md
└── ... (documentación oficial)

_scripts/
├── setup_week.sh          ← VA AL REPO
├── run_pipeline.sh        ← VA AL REPO
├── package_project.sh     ← VA AL REPO
├── sync_project.sh        ← VA AL REPO
├── calc_rnd.py
├── calc_cr.py
├── render_*.py (6)
├── assemble_*.py (2)
├── excel_*.py (2)
├── build_package.py
└── ... (pipeline core)

rates-nodispo/week-NN/ · checkrates/week-NN/
├── Reportes HTML editoriales
├── 4 Excels por reporte
└── Datasets crudos
```

#### PROYECTO CLAUDE · /mnt/project/
```
Espejo exacto del repo:
- Todos los scripts (Python + Bash)
- Toda la documentación
- Se mantiene sincronizado con repo

Flujo:
1. Cambios en repo GitHub
2. git push origin main
3. bash sync_project.sh NN  (en proyecto Claude)
4. Proyecto actualizado ✅
```

### Implicaciones para W20+

**Pipeline W20 y siguientes:**
```
1. Recibir datasets W20
2. bash setup_week.sh 20 "PERIODO" "MES" 19 "PERIODO_PREV"
3. bash run_pipeline.sh 20
4. Validar outputs (HTML + Excel)
5. cd Price/ && git add . && git push
6. bash sync_project.sh 20 (para actualizar proyecto Claude)
```

**No hay iteración manual entre repo y proyecto.**
**Es automatizada vía sync_project.sh**

### Cambios en PROMPT_MAESTRO_v3.md

Las secciones anteriores que mencionaban:
```
❌ \"setup_week.sh solo en proyecto Claude\"
❌ \"run_pipeline.sh no va al repo\"
```

**Han sido reemplazadas por esta arquitectura correcta** que refleja la realidad del proyecto PRICE.

---

Última actualización: Mayo 2026 · post W19 · corrección arquitectura repo/proyecto · definición estructura definitiva para W20+"
```

---

## ✅ VERIFICACIÓN

Después de pegar, verifica que:
1. ✅ El texto se vea formateado correctamente (títulos grandes, listas, bloques de código)
2. ✅ No hay espacios faltantes entre secciones
3. ✅ La última línea dice "Última actualización: Mayo 2026 · post W19 · corrección arquitectura..."

---

## 🎯 RESUMEN

**Qué estás agregando:**
- Corrección de arquitectura repo vs proyecto
- Estructura definida definitiva
- Flujo automatizado para W20+
- Clarificación de qué va dónde

**Por qué:**
- Tu repo ya está bien diseñado (reproducible, público)
- Mi recomendación anterior era incorrecta
- Este texto aclara la verdad para futuro

**Cuándo:**
- Ahora, antes de generar ZIP final para W20
