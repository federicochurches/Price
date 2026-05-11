# Playbook · Workflow Semanal · PRICE Supply Analytics

---

## 📅 Calendario

- **Día de publicación:** lunes
- **Hora target:** antes de las 11:00 AM Cancún (UTC-5)
- **Datasets:** disponibles el lunes temprano o el viernes anterior

---

## 🔢 Pipeline completo · 6 pasos

### Pre-flight · antes de empezar

```
✓ Dataset_CheckRates_WNN.xlsx disponible en uploads
✓ Dataset_RatesNoDispo_WNN.xlsx disponible en uploads  ← validar que tiene 9 columnas
✓ Dataset_CheckRates_W(N-1).xlsx disponible (para WoW)
✓ Dataset_RatesNoDispo_W(N-1).xlsx disponible (para WoW)
✓ Mail_W(N-1).html está en el proyecto Claude
```

> **Validación dataset RND:** columnas obligatorias = `CorpName`, `PaisDestino`, `Destino`, `Hotel`, `DistributionCategory`, `Trafico`, `%NoDispo`, `Bookings`, `gb_usd`. Si faltan, solicitar dataset corregido antes de continuar.

---

### Paso 1 · Cálculo

```
Comando Claude: "Recibí los datasets Week NN"
```

Claude ejecuta:
```python
python calc_rnd.py   # Dataset W(N) + W(N-1) → rnd_wNN_data.pkl
python calc_cr.py    # Dataset W(N) + W(N-1) → cr_wNN_data.pkl
```

**Actualizar en cada script antes de correr:**
- `calc_rnd.py`: rutas `Dataset_RatesNoDispo_WNN.xlsx` y `Dataset_RatesNoDispo_W(N-1).xlsx`
- `calc_cr.py`: `WEEK`, `PERIODO`, `MES_AÑO`, `VOL_NUM`, rutas datasets

---

### Paso 2 · Render HTML

```python
python render_rnd_p1.py  # → part1_rnd.html
python render_rnd_p2.py  # → part2_rnd.html
python render_rnd_p3.py  # → part3_rnd.html
python render_cr_p1.py   # → part1_cr.html
python render_cr_p2.py   # → part2_cr.html
python render_cr_p3.py   # → part3_cr.html
```

---

### Paso 3 · Ensamblado

```python
python assemble_rnd.py   # → Supply_RatesNoDispo_WNN.html
python assemble_cr.py    # → Supply_CheckRates_WNN.html
```

---

### Paso 4 · Excel

```python
python excel_rnd.py      # → Analisis_Rates_NoDispo_7d.xlsx + B2C/OP/CUG
python excel_cr.py       # → Analisis_Checkrates_7d.xlsx + B2C/OP/CUG
```

---

### Paso 5 · Mail

```python
python render_mail_v3.py  # → Mail_WNN.html
```

**Actualizar en `render_mail_v3.py` antes de correr:**
`WEEK`, `PERIODO`, `VOL_NUM`, `PICKLE_RND`, `PICKLE_CR`, `OUT_FILE`

---

### Paso 6 · Hub + ZIP ← OBLIGATORIO desde W19

```python
python build_package.py  # → index.html + Price_WNN.zip
```

**Actualizar en `build_package.py` antes de correr:**
`WEEK`, `PERIODO`, `FECHA_PUB`, `WEEK_PREV`, `PERIODO_PREV`, `PICKLE_RND`, `PICKLE_CR`

**Qué genera:**
- `index.html` — hub actualizado con KPIs extraídos automáticamente del pickle, card W(N) featured + card W(N-1) en historial
- `Price_WNN.zip` — ZIP con estructura del repo lista para commit:
  ```
  Price_WNN/
  ├── index.html
  ├── checkrates/week-NN/  (5 archivos)
  ├── rates-nodispo/week-NN/  (5 archivos)
  └── _email/week-NN/Mail_WNN.html
  ```

> ⚠️ **Nunca editar `index.html` directamente** — se regenera automáticamente en cada ejecución y sobreescribirá cualquier cambio manual.

---

## 📨 Flujo del mail

```
Comando Claude: "Generá el draft del mail Week NN"
```

Claude:
1. Lee `Mail_WNN.html` (generado en Paso 5)
2. Extrae body entre `<!-- DRAFT_BODY_START -->` y `<!-- DRAFT_BODY_END -->`
3. Crea draft en Gmail con subject `Supply Optimization · Week NN · Resumen + Plan de Acción`
4. BCC: 14 destinatarios de `destinatarios.md`

Federico valida el draft en Gmail y lo envía manualmente.

---

## 📦 Commit a GitHub

Con el ZIP del Paso 6, descomprimirlo en el repo local y commitear:

```bash
# Descomprimir respetando la estructura
unzip Price_WNN.zip -d /ruta/al/repo/

# Commit
git add .
git commit -m "feat: Week NN · RatesNoDispo + CheckRates + hub index · DD-MM-YYYY"
git push origin main
```

**Validación post-commit** (esperar 1-2 min al deploy de Netlify):
- [ ] Hub muestra Week NN como featured
- [ ] KPIs correctos en la card (no hay placeholders `{{}}`)
- [ ] Links a reportes funcionan
- [ ] Login funciona con `pricetravel` / `supply2026`
- [ ] Cards W(N-1) en historial tienen links válidos

---

## 🔄 Actualización del proyecto Claude post-semana

Subir al proyecto Claude (reemplazando versiones anteriores):
- `Mail_WNN.html` ← nuevo mail generado
- `build_package.py` ← si se actualizó la config
- `render_mail_v3.py` ← si se actualizó
- `CHANGELOG.md` ← con entrada Week NN

---

## ⚠️ Gestión de duplicados en el proyecto Claude

El proyecto Claude NO reemplaza archivos — los duplica. Para evitar acumulación:
1. Antes de subir archivos actualizados → borrar los viejos del proyecto
2. Una vez por mes → borrar todo y subir el ZIP completo limpio (42 archivos)
3. Señal de alerta: proyecto con >55 archivos = hay duplicados
