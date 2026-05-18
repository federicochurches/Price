# 🚀 Flujo YAML · Pipeline Automático para W21+

## Resumen Rápido

**Antes (W20):** Editar 5 scripts, ejecutar 6 pasos manualmente
**Ahora (W21+):** 1 comando

```bash
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

---

## ¿Qué cambió?

### Arquitectura

```
                    ┌─────────────────────┐
                    │ WEEK_CONFIG.yml     │
                    │ (configuración      │
                    │  centralizada)      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ run_pipeline.py     │
                    │ (orquestador)       │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
      calc_rnd.py        calc_cr.py      render_*.py
      (env vars)         (env vars)       (env vars)
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Pickles W21 + W20   │
                    │ (datos calculados)  │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
      assemble_*.py    excel_*.py      render_mail_v3.py
      (env vars)       (env vars)       (env vars)
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ HTML + ZIP + Mail   │
                    │ (deliverables)      │
                    └─────────────────────┘
```

### Variables de Entorno

El `run_pipeline.py` **exporta automáticamente** estas variables a todos los scripts:

```bash
WEEK=W21
VOL_NUM=21
PERIODO="19–25 may 2026"
MES_AÑO="Mayo 2026"
FECHA_PUB="Lunes 26 mayo 2026"
WEEK_PREV=W20
VOL_NUM_PREV=20
PERIODO_PREV="12–18 may 2026"
PICKLE_RND=rnd_w21_data.pkl
PICKLE_CR=cr_w21_data.pkl
PROJECT_DIR=/mnt/project
OUTPUTS_DIR=/mnt/user-data/outputs
UPLOADS_DIR=/mnt/user-data/uploads
```

Cada script **lee desde el entorno**, con fallback a hardcodeado:

```python
# calc_rnd.py (ejemplo)
WEEK = os.getenv('WEEK', 'W20')  # Lee W21 del entorno, si no existe usa W20
VOL_NUM = os.getenv('VOL_NUM', '20')
PERIODO = os.getenv('PERIODO', '12–18 may 2026')
```

---

## 📋 Flujo W21 Paso a Paso

### 1. Adjuntar datasets (Federico)

```
/mnt/user-data/uploads/
  ├── Dataset_RatesNoDispo_W21.xlsx   ← nuevo
  ├── Dataset_RatesNoDispo_W20.xlsx   ← anterior (WoW)
  ├── Dataset_CheckRates_W21.xlsx     ← nuevo
  └── Dataset_CheckRates_W20.xlsx     ← anterior (WoW)
```

### 2. Actualizar WEEK_CONFIG.yml (2 min)

```bash
# Crear nueva config para W21 basada en W20:
cp WEEK_CONFIG_W20.yml WEEK_CONFIG_W21.yml

# Editar valores:
vim WEEK_CONFIG_W21.yml
  # Cambiar:
  # week: 21
  # vol_num: "21"
  # periodo: "19–25 may 2026"
  # mes_año: "Mayo 2026"
  # fecha_pub: "Lunes 26 mayo 2026"
  # week_prev: 20
  # periodo_prev: "12–18 may 2026"
  # week_prev2: 19
  # periodo_prev2: "5–11 may 2026"
```

### 3. Ejecutar pipeline (10 min)

```bash
cd /mnt/project
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

**Output:**
```
================================================================================
🚀 PIPELINE SUPPLY OPTIMIZATION · W21
================================================================================
Config: WEEK_CONFIG_W21.yml
WEEK=W21 VOL_NUM=21

================================================================================
📊 VALIDACIÓN DE DATASETS
================================================================================
✓ Dataset_RatesNoDispo_W21.xlsx en /uploads
✓ Dataset_CheckRates_W21.xlsx en /uploads
✓ Dataset_RatesNoDispo_W20.xlsx en /uploads
✓ Dataset_CheckRates_W20.xlsx en /uploads
✅ Todos los datasets validados

================================================================================
🔧 CONFIGURACIÓN
================================================================================
WEEK=W21
VOL_NUM=21
PERIODO=19–25 may 2026
MES_AÑO=Mayo 2026
FECHA_PUB=Lunes 26 mayo 2026
WEEK_PREV=W20
VOL_NUM_PREV=20
PERIODO_PREV=12–18 may 2026
PICKLE_RND=rnd_w21_data.pkl
PICKLE_CR=cr_w21_data.pkl
PROJECT_DIR=/mnt/project
OUTPUTS_DIR=/mnt/user-data/outputs
UPLOADS_DIR=/mnt/user-data/uploads
✅ Variables de entorno configuradas

================================================================================
▶️  INICIANDO PIPELINE · 8 PASOS
================================================================================

[1/8] Ejecutando: 1. CALC RND
✅ 1. CALC RND completado

[2/8] Ejecutando: 2. CALC CR
✅ 2. CALC CR completado

[3/8] Ejecutando: 3. RENDER RND + CR
✅ 3. RENDER RND + CR completado

[4/8] Ejecutando: 4. ASSEMBLE RND + CR
✅ 4. ASSEMBLE RND + CR completado

[5/8] Ejecutando: 5. EXCEL RND + CR
✅ 5. EXCEL RND + CR completado

[6/8] Ejecutando: 6. MAIL + HUB
✅ 6. MAIL + HUB completado

================================================================================
📋 RESUMEN
================================================================================
✅ PIPELINE COMPLETADO EXITOSAMENTE
   Week: 21
   Período: 19–25 may 2026
   ZIP: /mnt/user-data/outputs/Price_W21.zip
   Log: /mnt/user-data/outputs/pipeline_W21_run_20260526_120000.log
   Summary JSON: /mnt/user-data/outputs/pipeline_W21_summary.json

✅ ¡LISTO PARA COMMIT A GITHUB!
```

### 4. Commit a GitHub (3 min)

```bash
# Descomprimir ZIP
cd /repo/Price
unzip /mnt/user-data/outputs/Price_W21.zip

# Revisar archivos
git status

# Commit
git add .
git commit -m "feat: Week 21 · RatesNoDispo + CheckRates + hub · 19–25 may 2026"
git push origin main
```

---

## 📂 Estructura de Archivos

```
/mnt/project/
├── run_pipeline.py                ← NUEVO · Orquestador
├── WEEK_CONFIG_W21.yml            ← NUEVO · Config W21
├── calc_rnd.py                    ← Actualizado (env vars)
├── calc_cr.py                     ← Actualizado (env vars)
├── render_mail_v3.py              ← Actualizado (env vars)
├── build_package.py               ← Actualizado (env vars)
├── render_rnd_p*.py               ← Actualizado (env vars)
├── render_cr_p*.py                ← Actualizado (env vars)
├── assemble_*.py                  ← Actualizado (env vars)
├── excel_*.py                     ← Actualizado (env vars)
└── ... (resto sin cambios)

/mnt/user-data/outputs/
├── Price_W21.zip                  ← ZIP final para GitHub
├── pipeline_W21_run_*.log         ← Log detallado
└── pipeline_W21_summary.json      ← Resumen en JSON
```

---

## 🔧 Troubleshooting

### Error: "❌ Archivo no encontrado: WEEK_CONFIG.yml"

```bash
# Verificar que el archivo existe:
ls -lh /mnt/project/WEEK_CONFIG_W21.yml

# Si no existe, crear desde template:
cp /mnt/project/WEEK_CONFIG_W20.yml /mnt/project/WEEK_CONFIG_W21.yml
```

### Error: "Dataset incompletos. Abortando."

El script verifica 4 datasets **antes** de ejecutar pipeline:
- `Dataset_RatesNoDispo_W21.xlsx` ✓
- `Dataset_CheckRates_W21.xlsx` ✓
- `Dataset_RatesNoDispo_W20.xlsx` ✓
- `Dataset_CheckRates_W20.xlsx` ✓

```bash
# Si faltan, adjuntarlos a /mnt/user-data/uploads/
ls -lh /mnt/user-data/uploads/Dataset_*

# O copiar desde /mnt/project si están ahí:
cp /mnt/project/Dataset_CheckRates_W21.xlsx /mnt/user-data/uploads/
```

### Paso falló: "❌ 5. EXCEL RND + CR"

Excel es **non-critical** — el pipeline continúa. Revisar log:

```bash
cat /mnt/user-data/outputs/pipeline_W21_run_*.log | grep -A 20 "EXCEL"
```

Usuales:
- Memoria insuficiente (archivos muy grandes)
- Permisos en carpeta outputs

### Paso falló: "❌ 2. CALC CR" (CRÍTICO)

Pipeline **aborta**. Revisar log para causa:

```bash
tail -100 /mnt/user-data/outputs/pipeline_W21_run_*.log
```

Usuales:
- Dataset_CheckRates_W21.xlsx corrupto o con columnas faltantes
- Formato diferente al esperado

---

## 📊 Resumen JSON

Cada ejecución genera un JSON con metadatos:

```bash
cat /mnt/user-data/outputs/pipeline_W21_summary.json
```

Output:
```json
{
  "status": "SUCCESS",
  "week": 21,
  "vol_num": "21",
  "periodo": "19–25 may 2026",
  "zip_path": "/mnt/user-data/outputs/Price_W21.zip",
  "log_path": "/mnt/user-data/outputs/pipeline_W21_run_20260526_120000.log",
  "timestamp": "2026-05-26T12:00:00.123456"
}
```

Útil para:
- Integración con sistemas externos
- Auditoría de ejecuciones
- Automatización futura (CI/CD)

---

## ⏱️ Timeline Estimado

| Paso | Tiempo |
|---|---|
| Adjuntar 4 datasets | 5 min |
| Editar WEEK_CONFIG.yml | 2 min |
| Ejecutar `run_pipeline.py` | 10-15 min |
| Revisar logs + descargar ZIP | 2 min |
| Descomprimir + commit GitHub | 3 min |
| **TOTAL** | **~25 min** |

**Antes (W20):** 35 min (incluyendo edits en 5 scripts)
**Ahora (W21+):** 25 min (todo automático)

---

## 🎯 W22 y futuro

Para W22, solo necesitas:

1. **Adjuntar 4 datasets**
2. **Copiar config W21:**
   ```bash
   cp WEEK_CONFIG_W21.yml WEEK_CONFIG_W22.yml
   ```
3. **Editar 7 líneas en YAML:**
   - `week: 22`
   - `vol_num: "22"`
   - `periodo: "..."` (nuevas fechas)
   - `fecha_pub: "..."` (nuevo lunes)
   - `week_prev: 21`
   - `periodo_prev: "19–25 may 2026"`
   - `week_prev2: 20`

4. **Ejecutar:**
   ```bash
   python3 run_pipeline.py WEEK_CONFIG_W22.yml
   ```

**¡Hecho en 25 minutos!**

---

## Notas Técnicas

### Fallbacks

Todos los scripts tienen fallbacks a hardcodeado. Si env vars no se establecen:

```python
WEEK = os.getenv('WEEK', 'W20')  # Usa W20 si no hay env var
```

Esto permite ejecutar scripts **manualmente** para debugging:

```bash
# Sin run_pipeline.py (usa hardcodeado W20)
python3 calc_rnd.py

# Con run_pipeline.py (usa env var W21)
WEEK=W21 python3 calc_rnd.py
```

### Log Files

Se generan **dos logs**:
- `.log` — log detallado con timestamps y toda la salida
- `_summary.json` — metadatos en formato JSON

---

**¡Listo! W21+ es 100% automático con YAML. No requiere editar código.**

