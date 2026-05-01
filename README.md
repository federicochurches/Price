# PRICE · Release Workflow

Este documento describe el proceso semanal para generar y publicar los Reportes **CheckRates** y **RatesNoDispo** de Supply Optimization · PriceTravel.

---

## 📁 Estructura del repo

```
Price/                                          (repo público de GitHub Pages)
├── README.md                                   (este archivo)
├── _editorial/
│   ├── GUIA_EDITORIAL_RatesNoDispo.html        (guía editorial RND · ⭐ actualizada W17)
│   └── GUIA_EDITORIAL_CheckRates.html          (guía editorial CR)
├── _template/
│   ├── _TEMPLATE_RatesNoDispo_Reporte.html     (template RND · ⭐ sin bugs estructurales)
│   └── _TEMPLATE_CheckRates_Reporte.html       (template CR · con banners Excel)
├── datasets/                                   (datasets originales — fuente)
│   ├── rates-nodispo/week-NN/Rates_NoDispo_WNN.xlsx
│   └── checkrates/week-NN/CheckRates_WNN.xlsx
├── rates-nodispo/
│   ├── week-16/
│   │   ├── Editorial/RatesNoDispo_Reporte_Editorial.html
│   │   └── Analisis/Analisis_Rates_NoDispo_7d.xlsx
│   └── week-17/
│       ├── Editorial/RatesNoDispo_Reporte_Editorial.html
│       └── Analisis/Analisis_Rates_NoDispo_7d.xlsx
├── checkrates/
│   └── week-17/
│       ├── Editorial/CheckRates_Reporte_Editorial.html
│       └── Analisis/Analisis_Checkrates_7d.xlsx
├── _scripts/                                   (NO se publica — solo local)
│   ├── prepare_week.py
│   ├── organize_datasets.py
│   └── send_email.py
└── _email/                                     (NO se publica)
    └── week-NN/Mail_WNN.html
```

### URLs públicas

- **Hub interno**: `https://analytics-desk.netlify.app/`
- **RatesNoDispo**: `https://federicochurches.github.io/Price/rates-nodispo/week-NN/Editorial/RatesNoDispo_Reporte_Editorial.html`
- **CheckRates**: `https://federicochurches.github.io/Price/checkrates/week-NN/Editorial/CheckRates_Reporte_Editorial.html`

---

## ⚠ Decisiones consolidadas · post W17

> Antes de hacer cambios al template o reportes, leer la **Guía Editorial** completa: `_editorial/GUIA_EDITORIAL_RatesNoDispo.html`

### Bandas Severity definitivas

**% NoDispo (5 niveles):**
| Nivel | Rango |
|---|---|
| Exitosa | < 3% |
| Aceptable | 3 – 5% |
| Revisar | 5 – 20% |
| Crítica | 20 – 60% |
| Súper Crítica | > 60% |

**Conv Rate RPM (5 niveles):**
| Nivel | Rango |
|---|---|
| Exitosa | > 3 |
| Aceptable | 1,74 – 3 |
| Revisar | 1 – 1,74 |
| Crítica | 0,5 – 1 |
| Súper Crítica | < 0,5 |

### Estructura kpis-hero · regla crítica

Card NoDispo y Card RPM deben ser **2 hijos directos** del div `.kpis-hero`. Si la 2da card queda anidada dentro de la 1ra (bug detectado en W17), el grid colapsa a 1 columna. Validar con BeautifulSoup antes de cada release (ver Validación al final).

### Tabs por card · listas DIFERENCIADAS

| Pestaña | Card NoDispo | Card RPM |
|---|---|---|
| País | peor %NoDispo ponderado | peor RPM ponderado |
| Destino | destinos con más hoteles críticos en P80 | peor RPM (BKGS>0, tráfico>5M) |
| Corp | peor %NoDispo (filtro tráfico>50M) | peor RPM (BKGS>0, tráfico>10M) |
| Hotel | peor %NoDispo en P80 | peor RPM con BKGS>0 |
| Canasta | B2C, OP, CUG con su %NoDispo | B2C, OP, CUG con su RPM |

### TAG header

- RND: magenta `#EA0074` ✅
- CR: violeta `#5C469C` ✅
- **Nunca usar #5C469C en RND**

### Resumen Ejecutivo por Canasta

10 findings en 2 columnas dentro de cada `<details>` (B2C, OP, CUG). Posición: **inmediatamente después de Alerts · Casos Críticos**, no al final del details.

### Sección "Análisis por Canasta" · ELIMINADA

`<section id="por-canasta">` fue eliminada por redundancia con "Detalle por Canasta". **NO recrear**.

---

## 🚀 Workflow semanal (Lunes)

### Paso 1 · Recibir datasets

```
Rates_NoDispo_W<NN>.xlsx     (pestañas: Canasta ALL · B2C · OP · UOP)
CheckRates_W<NN>.xlsx        (pestañas: TOTALES · Canal B2C · Canal OP · Canal UOP)
```

### Paso 2 · Validación de columnas datasets

**RND debe tener:**
- ✅ `CorpName` (sin `-`) · sin esto requiere recovery del W previo (~99% coverage)
- ✅ `Hotel` · `PaisDestino` · `Destino`
- ✅ `Trafico` · `%NoDispo` (decimal · 0.07 = 7%) · `Bookings` · `gb_usd`

**CR debe tener:**
- ✅ `Destino` · sin esto la tab País del CR no funciona

### Paso 3 · Organizar datasets originales

```bash
python _scripts/organize_datasets.py NN ~/Downloads/Rates_NoDispo_WNN.xlsx ~/Downloads/CheckRates_WNN.xlsx
```

### Paso 4 · Generar reportes

Tomar el TEMPLATE limpio (`_template/_TEMPLATE_*`), copiar a `week-NN/Editorial/`, y reemplazar valores hardcoded con datos de la semana. Validar estructura antes de commit (paso 6).

### Paso 5 · Generar Excel de Análisis

11 pestañas obligatorias para RND:

1. Ficha Técnica
2. Severity NoDispo
3. Demanda No Convertida
4. Bajo Rendimiento
5. Por Corporativo
6. Por Destino
7. Por País
8. Plan de Acción
9. Canasta B2C · Bajo Rendimiento
10. Canasta OP · Bajo Rendimiento
11. Canasta CUG · Bajo Rendimiento

Cada pestaña con Top 20.

### Paso 6 · Validación pre-release (checklist 2 min)

```python
from bs4 import BeautifulSoup
import re

with open('rates-nodispo/week-NN/Editorial/RatesNoDispo_Reporte_Editorial.html') as f:
    html = f.read()

# 1. Balance HTML
opens = len(re.findall(r'<div\b[^>]*>', html))
closes = len(re.findall(r'</div\s*>', html))
assert opens == closes

# 2. kpis-hero con 2 cards directas
soup = BeautifulSoup(html, 'lxml')
kpis_hero = soup.find('div', class_='kpis-hero')
cards = [c for c in kpis_hero.children if c.name == 'div' and 'kpi-card' in c.get('class', [])]
assert len(cards) == 2

# 3. TAG en magenta (RND) o violeta (CR)
tag_rule = re.search(r'\.report-tag\{[^}]*\}', html).group(0)
assert '#EA0074' in tag_rule  # para RND

# 4. Sin sección obsoleta
assert 'id="por-canasta"' not in html

# 5. 3 details con Resumen Ejecutivo
section = soup.find('section', id='canastas-detail')
assert len(section.find_all('details')) == 3

print("✓ OK")
```

### Paso 7 · Commit y Push

```
fix: editoriales W<NN> · datos validados

- RND W<NN>: kpis-hero validado · 2 cards directas
- Pestañas Destino/Corp diferenciadas (NoDispo vs RPM)
- TAG header magenta correcta
- Resumen Ejecutivo 10 findings 2 cols post-Alerts en cada canasta
- Excel Análisis con 11 pestañas Top 20
```

### Paso 8 · Actualizar Hub de Netlify

Actualizar cards CheckRates y RatesNoDispo con URL de la nueva semana.

### Paso 9 · Enviar email

```bash
python _scripts/send_email.py NN
```

---

## 🎨 Sistema de Color · Rates No Dispo

| Variable | Hex | Uso |
|---|---|---|
| --magenta | `#EA0074` | TAG · valores principales · pill Crítica |
| --violet | `#5C469C` | Pill Aceptable · banda gauge Aceptable |
| --accent | `#1E5A8C` | Conv RPM · TOTAL Severity |
| --amber | `#A86A1D` | Bajo Rendimiento · severity atención |
| --green | `#2F6C34` | Por Destino · GB positivo |
| --ink-muted | `#8A8377` | Valores secundarios · neutros |

⚠ **NO usar #5C469C como TAG en RND** · ese color es de CheckRates.

## 🎨 Sistema de Color · Check Rates

| Variable | Hex | Uso |
|---|---|---|
| --accent | `#5C469C` | TAG · Eficacia · Conv Rate · TOTAL |
| --amber | `#EA0074` | Bajo Rendimiento · %Errors · Severity Eficacia |
| --green | `#4FC3F4` | Canasta CUG (color propio) |
| --ink-muted | `#8A8377` | CheckRates · Bookings · neutros |

---

## 📊 Destinatarios del email

| Campo | Valor |
|---|---|
| **De** | `federico.iglesias@pricetravel.com` |
| **Asunto** | `Supply Optimization · Reporte [CheckRates+RatesNoDispo] Week-NN` |
| **Para** | rafael.durand, bellanira.hernandez, maria.alejandra.rico, javier.parra, alonso.mis, ingrid.kuhnne, david.gamboa, hugo.ascencio, ext.jesus.lizarraga, alejandro.flores, gabriela.guerra, barbara.rodriguez |

---

## 📅 Calendario de releases

| Week | Periodo | RatesNoDispo | CheckRates |
|---|---|---|---|
| 16 | 13–19 Abr 2026 | ✅ v2.0 | ⚠ pendiente regenerar |
| 17 | 20–26 Abr 2026 | ✅ v2.0 | ✅ v2.0 |
| 18 | 27 Abr – 3 May 2026 | ⏳ Próximo | ⏳ Próximo |

---

## 📝 Changelog

- **v1.0** (2026-04-27): Release inicial W16. Estructura por canastas.
- **v1.1** (2026-04-28): W17 CheckRates. Umbrales D, colores canasta definidos.
- **v1.2** (2026-04-28): W17 RND. Resúmenes ejecutivos por canasta con RPM, WoW.
- **v2.0** (2026-05-01): **Release mayor · estructura validada y bugs resueltos**:
  - kpis-hero con 2 cards directas (era 1 columna)
  - Pestañas Destino/Corp diferenciadas (NoDispo vs RPM)
  - Card RPM Corp ahora muestra RPM (era #críticos)
  - H1 narrativo alineado con pestaña Corp · RIU/Iberostar/Melia
  - Detalle por Canasta: 10 findings 2 cols post-Alerts
  - TAG header magenta correcta (#EA0074)
  - Sección Análisis por Canasta eliminada (redundante)
  - CR W17: H1 narrativo + 4 banners Excel + tabs reordenadas
  - Templates RND/CR actualizados con estructura validada
  - Guía Editorial RND con decisiones consolidadas
  - Excels Análisis RND con 11 pestañas Top 20

## ⚠ Acciones para W18

Pedir al equipo de data:
- **RND W18 con `CorpName` correcta** (sin `-`) · evita recovery manual
- **CR W18 con `Destino`** · habilita la tab País del CheckRates

