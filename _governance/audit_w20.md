# 🔍 Audit de Integridad · Proyecto PRICE W20

## 📊 Inventario de archivos

**Total actual:** 47 archivos
**Esperado (checklist):** 42 archivos
**Diferencia:** +5 archivos (hay duplicados o archivos no previstos)

### Archivos no contemplados en checklist (5)
1. ❌ `_TEMPLATE_Hub.html` — Debería estar SOLO en GitHub bajo `_template/`
2. ✅ `template_seguimiento.py` — Correcto (agregado post-W19, parte de helpers)
3. ✅ `destinatarios.md` — Correcto (15 destinatarios · parte del sistema)
4. ✅ `Mail_W19.html` — Correcto (referencia de semana anterior)
5. ✅ `COMMIT_GUIDE.md` — Correcto (aunque checklist decía "solo en repo", ahora está en `_governance/` al ZIP)

**Limpieza necesaria:** Eliminar `_TEMPLATE_Hub.html` del proyecto Claude.

---

## 🔧 CONFIG SEMANAL ACTUAL (OBSOLETO · ESTÁ EN W19)

### calc_rnd.py
- `WEEK = 'W19'` · `VOL_NUM = '19'` · `PERIODO = '5–11 may 2026'`
- Lee: `Dataset_RatesNoDispo_W19.xlsx` (W19) + `Dataset_RatesNoDispo_W18.xlsx` (W18)
- Output: `rnd_w19_data.pkl`

### calc_cr.py
- `WEEK = 'W18'` · `VOL_NUM = '18'` · `PERIODO = '27 abr – 3 may 2026'`
- Lee: `Dataset_CheckRates_W19.xlsx` (W19) + `Dataset_CheckRates_W18.xlsx` (W18)
- Output: `cr_w18_data.pkl` ⚠️ NOTA: Sale con nombre W18 aunque procesa W19

### render_mail_v3.py
Ver línea 1-50...

### build_package.py
- `WEEK = 19` · `PERIODO = '5–11 may 2026'` · `FECHA_PUB = 'Lunes 12 mayo 2026'`
- `WEEK_PREV = 18` · `PERIODO_PREV = '27 abr – 3 may 2026'`
- Lee: `rnd_w19_data.pkl` + `cr_w19_data.pkl`
- Output: `index.html` + `Price_W19.zip`

---

## ⚠️ PROBLEMAS DETECTADOS

### 1. INCONSISTENCIA CRITICA: calc_cr.py output
`calc_cr.py` genera `cr_w18_data.pkl` (nombre W18) pero procesa datasets W19 + W18.
**Impacto:** `build_package.py` busca `cr_w19_data.pkl` (línea 26-27) → **ERROR FileNotFoundError**

### 2. Incompatibilidad de WEEK entre scripts
- `calc_cr.py`: `WEEK='W18'` · genera `cr_w18_data.pkl`
- `calc_rnd.py`: `WEEK='W19'` · genera `rnd_w19_data.pkl`
- `build_package.py`: busca `cr_w19_data.pkl` + `rnd_w19_data.pkl`
- `render_mail_v3.py`: leerá pickles con esos nombres

**Solución:** Alinear todos a W19:
- `calc_cr.py` → `WEEK='W19'`, `PICKLE_OUTPUT='cr_w19_data.pkl'`
- Los demás ya están alineados

### 3. Archivo obsoleto: `_TEMPLATE_Hub.html`
**Regla:** vive SOLO en GitHub bajo `_template/`, no en el proyecto Claude.
**Acción:** Eliminar de este proyecto.

---

## 🎯 CONFIG PARA PASAR A W20

### Paso 1: Limpiar archivos obsoletos
- ❌ Eliminar `_TEMPLATE_Hub.html` del proyecto

### Paso 2: Actualizar calc_rnd.py
```
WEEK     = 'W20'
VOL_NUM  = '20'
PERIODO  = '12–18 may 2026'  ← ajustar fechas
MES_AÑO  = 'Mayo 2026'

df18 = load_rnd('Dataset_RatesNoDispo_W20.xlsx', 20)
df17 = load_rnd('Dataset_RatesNoDispo_W19.xlsx', 19)
```

### Paso 3: Actualizar calc_cr.py
```
WEEK = 'W20'
PERIODO = '12–18 may 2026'  ← ajustar fechas
MES_AÑO = 'Mayo 2026'
VOL_NUM = '20'

df18 = load_and_clean('Dataset_CheckRates_W20.xlsx')  # W20
df17 = load_and_clean('Dataset_CheckRates_W19.xlsx')  # W19
```

**⚠️ IMPORTANTE:** Al final, antes del `if __name__ == '__main__':`, asegurar:
```python
pickle_out = 'cr_w20_data.pkl'
with open(pickle_out, 'wb') as f:
    pickle.dump(D, f)
```

### Paso 4: Actualizar build_package.py
```
WEEK        = 20
PERIODO     = '12–18 may 2026'
FECHA_PUB   = 'Lunes 19 mayo 2026'

WEEK_PREV        = 19
PERIODO_PREV     = '5–11 may 2026'
WEEK_PREV2       = 18
PERIODO_PREV2    = '27 abr – 3 may 2026'

PICKLE_RND  = 'rnd_w20_data.pkl'
PICKLE_CR   = 'cr_w20_data.pkl'
```

### Paso 5: Actualizar render_mail_v3.py
```
WEEK = 'W20'
PERIODO = '12–18 may 2026'
VOL_NUM = '20'

PICKLE_RND = 'rnd_w20_data.pkl'
PICKLE_CR = 'cr_w20_data.pkl'
OUT_FILE = 'Mail_W20.html'
```

### Paso 6: Actualizar Mail_W{NN}.html en proyecto
- Reemplazar `Mail_W19.html` con el que se publicó de W19
- Dejar como referencia para draft de W20

---

## ✅ CHECKLIST PRE-PIPELINE W20

- [ ] Eliminar `_TEMPLATE_Hub.html` del proyecto
- [ ] Actualizar `calc_rnd.py` con W20
- [ ] Actualizar `calc_cr.py` con W20
- [ ] Actualizar `build_package.py` con W20
- [ ] Actualizar `render_mail_v3.py` con W20
- [ ] Confirmar datasets disponibles:
  - `Dataset_RatesNoDispo_W20.xlsx`
  - `Dataset_RatesNoDispo_W19.xlsx`
  - `Dataset_CheckRates_W20.xlsx`
  - `Dataset_CheckRates_W19.xlsx`
- [ ] Ejecutar pipeline 1-6 en orden

