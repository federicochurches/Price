# CheckRates · Release Workflow

Este documento describe el proceso semanal para generar y publicar el Reporte CheckRates de Supply Optimization · PriceTravel.

---

## 📁 Estructura del repo

```
Price/                                          (repo público de GitHub Pages)
├── _manual/
│   ├── GUIA_EDITORIAL_RatesNoDispo.html        (guía editorial Rates No Dispo)
│   └── GUIA_EDITORIAL_CheckRates.html          (guía editorial CheckRates)
├── datasets/                                   (datasets originales — fuente)
│   ├── rates-nodispo/
│   │   └── week-NN/Rates_NoDispo_WNN.xlsx
│   └── checkrates/
│       └── week-NN/CheckRates_WNN.xlsx
├── rates-nodispo/                              (reporte hermano)
│   ├── week-16/...
│   └── week-17/...
├── checkrates/                                 (este reporte)
│   ├── _template/
│   │   └── Template_Checkrates_Reporte_W18.html
│   ├── week-16/
│   │   ├── Editorial/CheckRates_Reporte_Editorial_Week16.html
│   │   └── Analisis/Analisis_Checkrates_7d.xlsx
│   └── week-17/
│       ├── Editorial/CheckRates_Reporte_Editorial_Week17.html
│       └── Analisis/Analisis_Checkrates_7d.xlsx
├── scripts/                                    (NO se publica en Pages — solo local)
│   ├── prepare_week.py
│   ├── organize_datasets.py
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
- **Reporte HTML**: `https://federicochurches.github.io/Price/checkrates/week-NN/Editorial/CheckRates_Reporte_Editorial_WeekNN.html`
- **Excel**: `https://federicochurches.github.io/Price/checkrates/week-NN/Analisis/Analisis_Checkrates_7d.xlsx`

---

## 🚀 Workflow semanal (Lunes)

### Paso 1 · Recibir el dataset

El equipo de Wholesale envía el archivo Excel de la semana:
```
CheckRates_Last_7_Days_<MES><DIA>.xlsx
```

Pestañas esperadas: **TOTALES**, **Canal B2C**, **Canal OP**, **Canal UOP**.

### Paso 2 · Organizar dataset original

```bash
python scripts/organize_datasets.py 17 ~/Downloads/Rates_NoDispo_W17.xlsx ~/Downloads/CheckRates_W17.xlsx
```

Copia los datasets crudos a `datasets/checkrates/week-17/CheckRates_W17.xlsx`.

### Paso 3 · Generar archivos de la semana

```bash
python scripts/prepare_week.py 17 ~/Downloads/CheckRates_W17.xlsx
```

Crea:
```
checkrates/week-17/
├── Editorial/CheckRates_Reporte_Editorial_Week17.html
└── Analisis/Analisis_Checkrates_7d.xlsx
```

### Paso 4 · Revisar visualmente (checklist 10 min)

Ver `_manual/GUIA_EDITORIAL_CheckRates.html` → sección 09 · Checklist de review.

Puntos clave:
- Hero: Eficacia + Conv Rate + hotel crítico actualizados
- Resumen Ejecutivo: 10 findings con datos de la semana
- Colores de canasta: B2C=pink (#EA0074) · OP=violeta (#5C469C) · CUG=celeste (#4FC3F4)
- Por Corporativo: CK ≥ 500 · n ≥ 3 (sin micro-corporativos)
- Menor Conv Rate: CK ≥ 2.000 · Bookings ≥ 3

### Paso 5 · Commit y Push (GitHub Desktop)

**Mensaje de commit estándar:**
```
CheckRates · Week 17 · 20-26 Abr 2026
```

Archivos a commitear:
- `_manual/GUIA_EDITORIAL_CheckRates.html` (solo si cambió)
- `checkrates/_template/Template_Checkrates_Reporte_W18.html` (solo si cambió)
- `checkrates/week-17/Editorial/CheckRates_Reporte_Editorial_Week17.html`
- `checkrates/week-17/Analisis/Analisis_Checkrates_7d.xlsx`
- `datasets/checkrates/week-17/CheckRates_W17.xlsx`

### Paso 6 · Actualizar hub de Netlify

Actualizar la card de CheckRates para que apunte a la URL de la nueva semana.

### Paso 7 · Enviar email

```bash
python scripts/send_email.py 17
```

Genera los archivos en `email/output/` y abre Gmail compose pre-armado.

---

## 📊 Destinatarios del email CheckRates

| Campo | Valor |
|---|---|
| **De** | `federico.iglesias@pricetravel.com` |
| **Asunto** | `Supply Optimization · Reporte CheckRates Week-NN` |
| **Para** | rafael.durand, bellanira.hernandez, maria.alejandra.rico, javier.parra, alonso.mis, ingrid.kuhnne, david.gamboa, hugo.ascencio, ext.jesus.lizarraga, alejandro.flores, gabriela.guerra, barbara.rodriguez |

---

## 🎨 Reglas de diseño · NO modificar sin actualizar la guía

| Elemento | Regla |
|---|---|
| Canasta B2C | Color `#EA0074` — TODO: nombres, valores, barras, headers, bordes |
| Canasta OP | Color `#5C469C` — TODO |
| Canasta CUG | Color `#4FC3F4` — TODO |
| Por Corporativo | Filtro: CK ≥ 500 · n ≥ 3 hoteles |
| Menor Conv Rate | Filtro: CK ≥ 2.000 · Bookings ≥ 3 |
| Severity canasta | Datos propios de cada canasta (no del global) |

Ver guía completa en `_manual/GUIA_EDITORIAL_CheckRates.html`.

---

## 📅 Calendario de releases

| Week | Periodo | Estado |
|---|---|---|
| 16 | 13–19 Abr 2026 | ✅ Publicado |
| 17 | 20–26 Abr 2026 | ✅ Publicado |
| 18 | 27 Abr – 3 May 2026 | ⏳ Próximo |

---

## ❓ Troubleshooting

### El deploy de GitHub Pages no se actualiza
Esperar 5 min después del push. Hard refresh (Ctrl+Shift+R).

### Los datos no coinciden con el dataset
Verificar que `prepare_week.py` haya leído las pestañas correctas: TOTALES + Canal B2C/OP/UOP.

### Colores incorrectos en canastas
Regenerar las secciones de canasta con `render_subsections(dfc, cc)` desde el pickle.
Ver `_manual/GUIA_EDITORIAL_CheckRates.html` → sección 02.

---

## 📝 Changelog

- **v1.0** (2026-04-27): Release inicial Week 16. Estructura por canastas integrada.
- **v1.1** (2026-04-28): Week 17. Umbrales D (CK≥2K·Bkgs≥3), colores canasta definidos, render_subsections unificado.
