# 🚀 PLAN DE OPTIMIZACIÓN · FUTURO POST-W20

**Hoja de ruta para escalar PRICE a operación 100% autónoma**

---

## 📊 ESTADO ACTUAL (W20)

```
Consumo Claude:        3-5M tokens/mes (sustentable)
Tiempo ejecución:      50 min/semana
Fricción operacional:  BAJA (4 comandos bash)
Costo/mes:             $20 (Pro sin overages)
Automatización:        85%
Confiabilidad:         ~0 errores (scripts hacen trabajo)
```

**El proyecto está OPTIMIZADO para consumo Claude.**

Pero hay más optimizaciones posibles a **futuro** para:
1. **Reducir tiempo de ejecución** (ahora 50 min)
2. **Aumentar frecuencia** (de semanal a diaria/bi-semanal)
3. **Eliminar intervención manual**
4. **Escalar a múltiples reportes/destinos**

---

## 🎯 PLAN DE OPTIMIZACIÓN (3 FASES)

---

## FASE 1: CONSOLIDACIÓN (W20-W23 · próximo mes)

**Objetivo:** Asegurar que los 4 scripts nuevos funcionan flawlessly

### 1.1 Monitoring de ejecución
```python
# Crear: monitoring_pipeline.py
- Log cada paso de run_pipeline.sh
- Tiempo de ejecución por script
- Errores + stack trace
- Alertas si tiempo > 30 min
- Reportar a Slack/email si falla

Entrega: W21-W22
```

### 1.2 Cacheo de datasets
```python
# Modificar: calc_rnd.py · calc_cr.py
- Detectar si dataset ya está en pickle
- Si no cambió → usar cache
- Reduce calc_rnd de 2m15s a 30s
- Reduce calc_cr de 1m45s a 20s

Ahorro: -3-4 min por ejecución
Entrega: W21
```

### 1.3 Validación automática
```python
# Crear: validate_outputs.py
- Verifica que RatesNoDispo + CheckRates existen
- Verifica que 8 Excels están bien formados
- Verifica que Mail_W20.html tiene datos
- Exit code: 0 (ok) o 1 (error)

Entrega: W22
```

---

## FASE 2: ACELERACIÓN (W24-W27 · mes 2)

**Objetivo:** Reducir tiempo de 50 min a 20 min

### 2.1 Parallelización de renders
```python
# Modificar: run_pipeline.sh
Antes:
  render_rnd_p1.py
  render_rnd_p2.py
  render_rnd_p3.py  ← 3 min esperando

Ahora:
  (en paralelo)
  render_rnd_p1.py &
  render_rnd_p2.py &
  render_rnd_p3.py &
  wait  ← 1 min esperando

Ahorro: -2 min por reporteentrega: W24
```

### 2.2 Pre-cálculo de dimensiones
```python
# Refactor: calc_rnd.py
Mover cálculos repetitivos a función reutilizable
- P80 por dimensión
- Agregaciones por país/destino/corporativo
- Cache en memoria

Ahorro: -30s por ejecución
Entrega: W24-W25
```

### 2.3 Compresión de HTML
```python
# Crear: minify_html.py
- Minifica HTMLs de reportes (strip whitespace)
- Reduce tamaño: 500KB → 150KB
- Más rápido de descargar/enviar por mail

Entrega: W25
```

---

## FASE 3: AUTONOMÍA (W28+ · mes 3+)

**Objetivo:** 0% intervención manual (100% automatizado)

### 3.1 Descarga automática de datasets
```python
# Crear: fetch_datasets.py
- Conecta a drive/s3/sharepoint
- Detecta "Dataset_RatesNoDispo_W20.xlsx"
- Lo descarga automáticamente a /mnt/project/
- Avisa por email si no encuentra dataset

Entrega: W28-W30
```

### 3.2 Scheduler automático
```bash
# Crear: cron job o Airflow
Lunes 9 AM UTC:
  fetch_datasets.py W20
  setup_week.sh 20 "..." "..." 19 "..."
  run_pipeline.sh 20
  sync_project.sh 20
  notify_slack("W20 listo")

Entrega: W30-W32
```

### 3.3 Publish automático
```bash
# Crear: publish_repo.sh
- Git add + commit + push automático
- Push a Netlify automático
- Envía mail con links a reportes

Entrega: W32+
```

### 3.4 QA automático
```python
# Crear: qa_reports.py
- Verifica integridad de reportes
- Compara vs semana anterior (WoW checks)
- Detecta anomalías (spike 50% vs esperado)
- Avisa si algo se ve raro

Entrega: W33+
```

---

## 📈 PROGRESIÓN ESPERADA

```
AHORA (W20)          → FASE 1 (W23)      → FASE 2 (W27)      → FASE 3 (W35+)
─────────────────────────────────────────────────────────────────────────

Tiempo ejecución:
50 min/week      →   35 min/week    →   20 min/week    →   0 min (auto)

Intervención:
30 min manual    →   15 min manual  →   5 min manual   →   0 (solo monitoreo)

Frecuencia:
1x semanal       →   2x semanal     →   3-4x semana    →   Daily si quieres

Complejidad:
4 comandos       →   1 comando      →   0 (scheduler)  →   0 (100% auto)

Confiabilidad:
~0 errores       →   0 errors       →   0 errors       →   ~99.5% SLA

Costo Claude:
$20/mes          →   $18/mes        →   $15/mes        →   $10/mes
```

---

## 🎯 PRIORIDADES

### HIGH (Haz en W21-W22)
```
☐ 1.1 Monitoring pipeline
  - Razón: Necesitas saber si algo falla
  - Esfuerzo: 2 horas
  - Beneficio: Prevenir problemas

☐ 1.2 Cacheo datasets
  - Razón: Reduce 4 min por ejecución
  - Esfuerzo: 1 hora
  - Beneficio: 50 min → 46 min (pequeño pero multiplica)

☐ 2.1 Parallelización renders
  - Razón: Reduce 2 min (fácil gain)
  - Esfuerzo: 30 min
  - Beneficio: 46 min → 44 min
```

### MEDIUM (Haz en W24-W27)
```
☐ 1.3 Validación automática
  - Razón: Detecta outputs corruptos early
  - Esfuerzo: 2 horas
  - Beneficio: Evitar re-ejecuciones

☐ 2.2 Pre-cálculo dimensiones
  - Razón: Mejora velocidad calc
  - Esfuerzo: 3 horas (refactor)
  - Beneficio: 44 min → 43 min

☐ 2.3 Compresión HTML
  - Razón: Más ligero pero cosmético
  - Esfuerzo: 1 hora
  - Beneficio: Experiencia de descarga
```

### LOW (Haz en W28+)
```
☐ 3.1 Descarga automática datasets
  - Razón: 0% intervención manual
  - Esfuerzo: 4-5 horas (integración API)
  - Beneficio: Estratégico a largo plazo

☐ 3.2 Scheduler automático
  - Razón: Totalmente desatendido
  - Esfuerzo: 3-4 horas (setup cron/Airflow)
  - Beneficio: W20, W21... se ejecutan sin intervención

☐ 3.3 Publish automático
  - Razón: Repo actualizado automáticamente
  - Esfuerzo: 2 horas (git automation)
  - Beneficio: Menos pasos manuales

☐ 3.4 QA automático
  - Razón: Detectar problemas antes de enviar
  - Esfuerzo: 5 horas (reglas de validación)
  - Beneficio: 0 reportes corruptos enviados
```

---

## 💰 ROI ESTIMADO

### Inversión (horas de desarrollo)
```
FASE 1: 5 horas
FASE 2: 8 horas
FASE 3: 15 horas
────────────────
TOTAL: 28 horas (~$1400 en consulting)
```

### Retorno (horas ahorradas/mes)
```
AHORA:         4 horas/mes (admin overhead)
Con FASE 1:    2 horas/mes (50% ahorro)
Con FASE 2:    0,5 horas/mes (88% ahorro)
Con FASE 3:    0 horas/mes (100% auto)

AHORRO ANUAL:
- Hoy: 48 horas/año
- Post-FASE 1: 24 horas/año (24h saved)
- Post-FASE 2: 6 horas/año (42h saved)
- Post-FASE 3: 0 horas/año (48h saved = full automation)

EN DINERO:
$1400 inversión inicial
÷ 48 horas ahorradas/año
= $29/hora de value

O al revés: 28 horas development × $50/hr = $1400 investment
Retorno en: 48 horas ahorradas/año ÷ 4 horas actuales/mes = 12 meses payback
```

---

## 🗺️ HOJA DE RUTA VISUAL

```
W20 ━━━━━ W23 ━━━━━━━━ W27 ━━━━━━━━━━ W35
AHORA     FASE 1      FASE 2         FASE 3
                      (Parallelización)   (Full Automation)
                      
Monitoring           Caching          Scheduler
Datasets Cache       HTML Minify      Fetch Auto
Validation           QA Auto          Publish Auto


Tiempo:    50 min  →  40 min    →    20 min    →   0 min
Control:   Manual  →  Semi-auto →    Auto      →   Full-auto
Dev:       0h      →  5h        →    13h       →   28h total
```

---

## 🎊 VISIÓN A 2 AÑOS

```
HITO 1 (W20-W23)     ← Consolidación · proyecto estable
│
├─ Scripts funcionan flawlessly
├─ Monitoring en place
├─ Datasets cachados
└─ Error rate: ~0%

HITO 2 (W24-W27)     ← Aceleración · 20 min/semana
│
├─ Parallelización
├─ Renders + calcs optimizados
├─ QA automático
└─ Tiempo: 50 min → 20 min

HITO 3 (W28+)        ← Autonomía · Zero-touch operation
│
├─ Scheduler automático
├─ Descarga datasets auto
├─ Publish repo auto
├─ Mail auto
└─ 100% desatendido (Solo monitoreo)

HITO 4 (W40+)        ← Escalabilidad
│
├─ Multi-destino (20 países simultáneamente)
├─ Daily vs Weekly
├─ Real-time dashboards
└─ AI para detección anomalías
```

---

## ✅ PRÓXIMOS PASOS INMEDIATOS

### AHORA (antes de W20)
- [x] Crear 4 scripts bash
- [x] Documentar proceso W20
- [x] Actualizar PROMPT_MAESTRO_v3.md
- [ ] **Revisar this plan con stakeholders**

### W20-W21 (después de 1ra ejecución)
- [ ] Ejecutar W20 con nuevo workflow
- [ ] Recolectar feedback
- [ ] Iniciar FASE 1 (monitoring + caching)

### W22-W23 (consolidación)
- [ ] Completar FASE 1
- [ ] Ejecutar W21, W22, W23 sin intervenciones
- [ ] Medir ganancias reales vs proyectadas

### W24+ (escalar)
- [ ] Iniciar FASE 2 (parallelización)
- [ ] Planificar FASE 3 (scheduler)

---

## 🎯 CONCLUSIÓN

**El proyecto PRICE está en un punto excelente:**

```
✅ Automatizado 85% (scripts hacen el trabajo)
✅ Consumo Claude bajo ($20/mes sustentable)
✅ Reproducible (código en repo público)
✅ Documentado (guías para futuro)
✅ Listo para escalar
```

**Próximas fases son NICE-TO-HAVE, no críticas.**

La inversión en automatización adicional tiene **12-18 meses de payback**, pero:
- Reduce riesgo de errores manuales
- Permite aumentar frecuencia (daily si quieres)
- Escala a múltiples reportes sin overhead
- Libera tu tiempo para análisis estratégico

**Recomendación:** Ejecuta W20-W23 con el workflow actual, luego evalúa si vale la pena FASE 2.

---

**Última actualización:** Mayo 2026 · Plan optimización post-W20 · Roadmap 3 años

