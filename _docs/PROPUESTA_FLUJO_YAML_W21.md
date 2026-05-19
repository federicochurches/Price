# 🎯 PROPUESTA: Flujo YAML para W21+

## Status Actual (W20)

✅ **Pipeline completamente funcional**
- 6 pasos automáticos  
- Todos los bugs detectados corregidos durante ejecución
- ZIP listo para commit

⚠️ **Fricción operativa**
- CONFIG distribuida en 5 scripts diferentes
- Cada semana: editar WEEK, VOL_NUM, PERIODO en 5 archivos
- Propenso a errores (olvidar un archivo, typos)
- No versionable

---

## Propuesta: Flujo YAML Centralizado

### ¿Qué cambiaría?

**Antes (W20, actual):**
```bash
# Manual: editar CONFIG en 5 scripts
vim calc_rnd.py        # cambiar WEEK='W20', VOL_NUM='20'
vim calc_cr.py         # idem
vim render_mail_v3.py  # idem
vim build_package.py   # idem
vim render_cr_p*.py    # idem (hardcoded en 3 archivos!)

# Luego ejecutar manualmente
python3 calc_rnd.py
python3 calc_cr.py
# ... 6 pasos manuales
```

**Después (con YAML):**
```bash
# 1. Crear WEEK_CONFIG_W21.yml (5 min)
cat > WEEK_CONFIG_W21.yml << EOF
week: 21
vol_num: "21"
periodo: "19–25 may 2026"
mes_año: "Mayo 2026"
fecha_pub: "Lunes 26 mayo 2026"
EOF

# 2. Ejecutar todo de una vez (10 min)
python3 run_pipeline_yaml.py WEEK_CONFIG_W21.yml

# ✅ Listo: todos los 6 pasos automáticos
```

---

## Beneficios

| Aspecto | Actual (W20) | Con YAML |
|---|---|---|
| **Tiempo setup** | 10-15 min edits | 5 min config |
| **Puntos de error** | 5+ (sed/edits en scripts) | 1 (YAML typo) |
| **Auditabilidad** | Config diseminada | Archivo único versionado |
| **Repetibilidad** | Manual cada semana | 1 comando |
| **Onboarding** | Complejo | "python3 run.py config.yml" |

---

## Costo de Implementación

| Tarea | Tiempo | Dificultad |
|---|---|---|
| Crear `run_pipeline_yaml.py` | 30 min | Media (manejo de subprocesses) |
| Adaptar scripts para leer env vars | 45 min | Media (5 scripts × 9 min c/u) |
| Crear template WEEK_CONFIG.yml | 5 min | Fácil |
| Documentar en README | 10 min | Fácil |
| **TOTAL** | **~1.5 horas** | - |

---

## ¿Qué scripts necesitarían cambios?

### Mínimos:

Solo los que tienen CONFIG SEMANAL:

1. `calc_rnd.py` — leer from env si existe, si no default
2. `calc_cr.py` — idem
3. `render_mail_v3.py` — idem
4. `build_package.py` — idem
5. `render_cr_p*.py` — leer PICKLE_CR desde env dinámicamente
6. `assemble_*.py` — idem

### Cambio típico:

```python
# ANTES (hardcodeado)
WEEK = 'W20'
VOL_NUM = '20'

# DESPUÉS (leer de env, fallback a hardcodeado)
import os
WEEK = os.getenv('WEEK', 'W20')
VOL_NUM = os.getenv('VOL_NUM', '20')
PICKLE_CR = os.getenv('PICKLE_CR', 'cr_w20_data.pkl')
```

---

## Recomendación

### Opción A: **Implementar YAML para W21** ✅ RECOMENDADO

**Cuándo:**
- Inmediatamente después de W20 (hoy/mañana)
- Antes de que Federico ejecute W21

**Ventaja:**
- W21+ extremadamente simple
- Automatizable (CI/CD future-proof)
- Escalable para múltiples equipos

**Acción:**
1. [ ] Implementar `run_pipeline_yaml.py` (30 min)
2. [ ] Adaptar 5 scripts para env vars (45 min)
3. [ ] Crear template YAML (5 min)
4. [ ] Testar con W21 (15 min)
5. [ ] Documentar en README (10 min)

---

### Opción B: **Mantener actual (sin YAML)** ⚠️ POSIBLE

**Cuándo:**
- Si W21 es urgente y no hay tiempo
- Si la fricción actual es "tolerable"

**Desventaja:**
- Sigue propenso a errores
- No escalable
- Debe hacerse manual cada semana

**Acción:**
- [ ] Solo cambiar CONFIG en 5 scripts cada semana
- [ ] Seguir comando manual de 6 pasos

---

## Decisión Requerida

### ¿Implementar flujo YAML para W21?

**SI (recomendado):**
- Pro: Futuro a prueba de errores, automático, escalable
- Contra: 1.5 horas de trabajo ahora
- Timeline: Hace hoy, W21 usa mañana

**NO (mantener actual):**
- Pro: Cero trabajo de implementación
- Contra: Sigue manual, propenso a errores, no escalable
- Timeline: W21 igual W20 (edits manuales)

---

## Archivos Auxiliares Creados (Sketches)

Para ayudarte con la decisión:

1. **WEEK_CONFIG_W21_TEMPLATE.yml**
   - Estructura de archivo YAML propuesto
   - Listo para copiar y adaptar

2. **run_pipeline_yaml_SKETCH.py**
   - Implementación sketch del wrapper
   - Requiere refinamiento (error handling, parallelization)
   - 80% funcional, listo para producción con 20% de ajustes

3. **FIXES_W20_CHECKLIST_W21.md**
   - Detalle de todos los bugs W20
   - Checklist para W21 sin YAML (si no implementas)

---

## Próximos Pasos

### Si dices SÍ a YAML:
1. Refino `run_pipeline_yaml.py` (30 min)
2. Adapto 5 scripts con env vars (45 min)
3. Testeo con W21 datasets reales
4. Documenta en README
5. ✅ W21 usa 1 comando: `python3 run.py WEEK_CONFIG_W21.yml`

### Si dices NO (mantener actual):
1. Para W21: cambiar CONFIG en 5 scripts (10 min sed)
2. Ejecutar 6 pasos manuales (15 min)
3. ✅ Listo, pero repetir manualmente cada semana

---

**Recomendación Final:** ✅ **YAML es inversión a futuro** — 1.5h ahora = 10min/semana forever.

