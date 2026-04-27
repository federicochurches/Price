# CheckRates · Release Workflow

Este documento describe el proceso semanal para generar y publicar el Reporte CheckRates de Supply Optimization · PriceTravel.

---

## 📁 Estructura del repo

```
Price/                                          (repo público de GitHub Pages)
├── rates-nodispo/                              (reporte hermano)
│   ├── week-15/...
│   └── week-16/...
├── checkrates/                                 (este reporte)
│   ├── templates/
│   │   └── Template_Checkrates_Reporte.html    (template base — solo se modifica si cambia el diseño)
│   ├── week-16/
│   │   ├── Editorial/
│   │   │   └── CheckRates_Reporte_Editorial.html
│   │   ├── Analisis/
│   │   │   └── Analisis_Checkrates_7d.xlsx
│   │   └── Templates/
│   │       └── Template_Checkrates_Reporte.html
│   ├── week-17/...                             (se genera cada semana)
│   └── week-NN/...
├── scripts/                                    (NO se publica en Pages — solo local)
│   ├── prepare_week.py
│   └── send_email.py
├── email/                                      (NO se publica en Pages)
│   ├── CheckRates_Mail_Template.txt
│   ├── CheckRates_Mail_Template.html
│   └── output/                                 (gitignore — se regenera)
└── docs/
    └── README.md                               (este archivo)
```

### URL pública

- **Hub interno** (con login): `https://analytics-desk.netlify.app/`
- **Reporte HTML** (sin login): `https://federicochurches.github.io/Price/checkrates/week-NN/Editorial/CheckRates_Reporte_Editorial.html`
- **Excel** (sin login): `https://federicochurches.github.io/Price/checkrates/week-NN/Analisis/Analisis_Checkrates_7d.xlsx`

---

## 🚀 Workflow semanal (Lunes)

### Paso 1 · Recibir el dataset

El equipo de Wholesale envía el archivo Excel de la semana:
```
CheckRates_Last_7_Days_<MES><DIA>.xlsx
```

Pestañas esperadas: **TOTALES**, **Canal B2C**, **Canal OP**, **Canal UOP**.

### Paso 2 · Generar archivos de la semana

Desde la raíz del repo:

```bash
python scripts/prepare_week.py <NUMERO_SEMANA> <PATH_DATASET>
```

Ejemplo:
```bash
python scripts/prepare_week.py 17 ~/Downloads/CheckRates_Last_7_Days_ABR27.xlsx
```

Esto crea:
```
checkrates/week-17/
├── Editorial/CheckRates_Reporte_Editorial.html
├── Analisis/Analisis_Checkrates_7d.xlsx
└── Templates/Template_Checkrates_Reporte.html
```

### Paso 3 · Revisar visualmente

Abrí el HTML editorial localmente:
```bash
open checkrates/week-17/Editorial/CheckRates_Reporte_Editorial.html
```

Verificá:
- Hero (título, lede, 6 cards)
- Resumen Ejecutivo (10 bullets)
- Las 13 secciones cargan datos
- Las 3 canastas (B2C, B2B, CUG) tienen sub-secciones completas
- Los hrefs del botón "VER EXCEL" apuntan a `https://federicochurches.github.io/Price/checkrates/week-17/Analisis/...`

### Paso 4 · Commit y Push (GitHub Desktop)

1. Abrir GitHub Desktop con el repo `Price`
2. En el panel "Changes" verás:
   - `checkrates/week-17/Editorial/CheckRates_Reporte_Editorial.html`
   - `checkrates/week-17/Analisis/Analisis_Checkrates_7d.xlsx`
   - `checkrates/week-17/Templates/Template_Checkrates_Reporte.html`
3. **Mensaje de commit estándar**:
   ```
   CheckRates · Week 17 · 20-26 Abr 2026
   ```
4. Click en "Commit to main"
5. Click en "Push origin"

### Paso 5 · Verificar deploy de GitHub Pages

Esperar ~2-3 minutos y abrir:
```
https://federicochurches.github.io/Price/checkrates/week-17/Editorial/CheckRates_Reporte_Editorial.html
```

Si el deploy es exitoso, el HTML se ve igual que en local.

### Paso 6 · Actualizar el hub de Netlify

Si hay un hub central en Netlify con cards a cada reporte, actualizar la card de CheckRates para que apunte a la URL de la nueva semana:
```
https://federicochurches.github.io/Price/checkrates/week-17/Editorial/CheckRates_Reporte_Editorial.html
```

### Paso 7 · Enviar email

```bash
python scripts/send_email.py 17
```

Esto genera 3 archivos en `email/output/`:
- `checkrates_week_17_mail.txt` — cuerpo plano
- `checkrates_week_17_mail.html` — cuerpo HTML enriquecido
- `checkrates_week_17_links.txt` — links de Gmail compose pre-armado

**Para enviar el mail**:

1. Asegurate de estar logeado en Gmail con `federico.iglesias@pricetravel.com`
2. Abrí el archivo `checkrates_week_17_links.txt`
3. Copiá el primer URL (Opción A) y pegalo en el navegador
4. Gmail abre con destinatarios + asunto + cuerpo pre-cargados
5. Revisá rápido y apretá Enviar

Si el link Opción A es muy largo y el navegador lo trunca:
- Usá el link Opción B (solo destinatarios + asunto)
- Copiá el cuerpo desde `checkrates_week_17_mail.txt`
- Pegalo manualmente en el cuerpo del mail

---

## 📊 Datos del email (modificables en `scripts/send_email.py`)

| Campo | Valor |
|---|---|
| **De** | `federico.iglesias@pricetravel.com` |
| **Asunto** | `Supply Optimization · Reporte CheckRates Week-NN` |
| **Para** (10 destinatarios) | rafael.durand, bellanira.hernandez, maria.rico, javier.parra, alonso.mis, daniela.madrigal, ingrid.kuhnne, david.gamboa, hugo.ascencio, ext.jesus.lizarraga |
| **CC / BCC** | (vacíos) |

Para modificar destinatarios, editar la lista `DESTINATARIOS` en `scripts/send_email.py`.

---

## 🛠️ Mantenimiento

### Modificar el diseño del reporte
Editar `checkrates/templates/Template_Checkrates_Reporte.html`. Los placeholders se reemplazan automáticamente por `prepare_week.py`.

### Modificar el cuerpo del email
Editar `email/CheckRates_Mail_Template.txt` y `email/CheckRates_Mail_Template.html`.

### Cambiar destinatarios
Editar la lista `DESTINATARIOS` en `scripts/send_email.py`.

### Cambiar asunto
Editar `SUBJECT_TEMPLATE` en `scripts/send_email.py`.

---

## 📅 Calendario de releases

| Week | Periodo | Estado |
|---|---|---|
| 16 | 13–19 Abr 2026 | ✅ Publicado |
| 17 | 20–26 Abr 2026 | ⏳ Próximo |
| 18 | 27 Abr – 3 May 2026 | — |
| ... | ... | ... |

---

## ❓ Troubleshooting

### El deploy de GitHub Pages no se actualiza
- Esperar 5 minutos después del push (a veces tarda)
- Hacer hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
- Verificar en GitHub.com → Settings → Pages que el branch sea correcto

### El link de Gmail abre vacío
- Verificar que estés logeado en Gmail con la cuenta correcta
- Si el link es muy largo, usar la Opción B (link corto + pegar cuerpo manual)

### Los datos del HTML no coinciden con el dataset
- Verificar que `prepare_week.py` haya leído las pestañas correctas (TOTALES + Canal B2C/OP/UOP)
- Revisar consola del script para ver KPIs calculados
- Si los datos del dataset cambian de formato, actualizar `prepare_week.py`

---

## 📝 Changelog

- **v1.0** (2026-04-27): Release inicial Week 16. Estructura por canastas integrada, 13 secciones, 16 hojas Excel.
