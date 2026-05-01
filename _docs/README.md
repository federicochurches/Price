# PRICE · Release Week 17 + Regeneración W16

Paquete del release **Week 17** + **regeneración retroactiva W16** de Supply Optimization · PriceTravel.

---

## 📁 Estructura del repo (GitHub Pages)

```
Price/
├── index.html
│
├── _docs/
│   └── README.md
│
├── _email/
│   └── Mail_W17.html                                   (mail unificado CR + RND)
│
├── _scripts/
│   └── commit_W17.sh
│
├── _template/
│   └── _TEMPLATE_Hub.html
│
├── checkrates/
│   ├── _manual/
│   │   └── GUIA_EDITORIAL_CheckRates.html
│   ├── _template/
│   │   └── _TEMPLATE_CheckRates_Reporte_Editorial.html
│   ├── week-16/                                        (regenerado retroactivamente)
│   │   ├── CheckRates_Reporte_Editorial.html
│   │   └── Analisis_Checkrates_7d_W16.xlsx
│   └── week-17/
│       ├── CheckRates_Reporte_Editorial.html
│       └── Analisis_Checkrates_7d_W17.xlsx
│
└── rates-nodispo/
    ├── _manual/
    │   └── GUIA_EDITORIAL_RatesNoDispo.html
    ├── _template/
    │   └── _TEMPLATE_RatesNoDispo_Reporte_Editorial.html
    ├── week-16/                                        (regenerado retroactivamente)
    │   ├── RatesNoDispo_Reporte_Editorial.html
    │   └── Analisis_Rates_NoDispo_7d_W16.xlsx
    └── week-17/
        ├── RatesNoDispo_Reporte_Editorial.html
        └── Analisis_Rates_NoDispo_7d_W17.xlsx
```

### URLs públicas

- Hub: https://federicochurches.github.io/Price/
- CheckRates W17: https://federicochurches.github.io/Price/checkrates/week-17/CheckRates_Reporte_Editorial.html
- Rates No Dispo W17: https://federicochurches.github.io/Price/rates-nodispo/week-17/RatesNoDispo_Reporte_Editorial.html
- CheckRates W16: https://federicochurches.github.io/Price/checkrates/week-16/CheckRates_Reporte_Editorial.html
- Rates No Dispo W16: https://federicochurches.github.io/Price/rates-nodispo/week-16/RatesNoDispo_Reporte_Editorial.html

---

## 📊 KPIs Week 17 vs Week 16

### CheckRates

| Métrica | W16 | W17 | Delta |
|---|---|---|---|
| Total hoteles | 32.835 | 32.857 | +22 |
| Hoteles HTS P80 | 4.720 | 4.860 | +140 |
| Eficacia ponderada | 93.95% | 94.12% | +0.17pp |
| Conv Rate ponderada | 1.67% | 1.50% | -0.17pp |
| Hoteles 0 BKGS | 25.087 (76.4%) | 25.226 (76.8%) | +0.4pp |
| CheckRates totales | 1.82M | 1.93M | +0.11M |
| Bookings | 30.333 | 29.001 | -1.332 |

### Rates No Dispo

| Métrica | W16 | W17 | Delta |
|---|---|---|---|
| Total hoteles activos | 53.985 | 54.004 | +19 |
| Hoteles HTS P80 | 16.051 | 19.346 | +3.295 |
| %NoDispo ponderado | 3.81% | 3.91% | +0.10pp |
| Tráfico total | 16.1M | 17.2M | +1.1M |
| Bookings | 40.175 | 39.267 | -908 |
| GB total | $9.48M | $8.90M | -$0.58M |
| Hoteles 0 BKGS | 45.671 (84.6%) | 45.813 (84.8%) | +0.2pp |
| CorpName disponible | ✅ SÍ | ❌ NO (en export W17) | — |

---

## 🆕 Cambios estructurales aplicados (W17 + W16 retroactivo)

### 1. Severity unificada en 5 niveles
| Nivel | Eficacia | Conv Rate | %NoDispo |
|---|---|---|---|
| Exitosa | > 97% | > 3% | 0-3% |
| Aceptable | 93-97% | 1.74-3% | 3-5% |
| Revisar | 85-93% | 1-1.74% | 5-20% |
| Crítica | 60-85% | 0.5-1% | 20-60% |
| Súper Crítica | < 60% | < 0.5% | > 60% |

### 2. Canastas colapsables con `<details>` HTML5
### 3. Naming editorial unificado
### 4. Concentración por Corporativo con %Share
### 5. Tabs Top 5 por canasta (CheckRates)
### 6. Banner de alertas por canasta (CheckRates)
### 7. Tablas Top 10 a 2 columnas
### 8. Método con fondo oscuro
### 9. Mail unificado (CR + RND en un solo mail)
### 10. Excels regenerados Top 50

---

## ⚠️ Notas sobre la regeneración retroactiva W16

Los reportes W16 fueron regenerados a partir de los datasets crudos para mantener coherencia editorial con W17. Cada reporte tiene un **banner amarillo** al inicio explicando esto al lector.

**Tradeoff pragmático:** Los Top 10 detallados dentro de los reportes pueden mostrar datos del W17 (por la complejidad de regenerar 100% el HTML). **Los Excels W16 sí tienen Top 50 reales del dataset W16**, así que para análisis se debe consultar el Excel.

---

## 🚀 Workflow del commit

```bash
cd ~/Downloads
unzip PRICE_Release_W17.zip -d release_W17

# Editar 2 rutas en _scripts/commit_W17.sh
# PACKAGE_DIR="$HOME/Downloads/release_W17"
# REPO_DIR="$HOME/Documents/GitHub/Price"

bash release_W17/_scripts/commit_W17.sh
```

El script:
1. Confirma rutas
2. Crea estructura si no existe
3. Copia 17 archivos (8 W17 + 4 W16 + 5 raíz/templates/guías)
4. git add · commit · push a main

---

## 📝 Changelog

- **v3.0** (2026-05-01): Release ampliado W17 + regeneración retroactiva W16
  - Severity unificada 5 niveles
  - Canastas colapsables HTML5
  - Naming editorial consistente
  - Concentración por Corporativo con %Share
  - Tabs Top 5 por canasta
  - Excels Top 50
  - Mail unificado CR + RND
  - Reorganización repo (`_docs/`, `_email/`, `_scripts/`, `_template/`)
  - **W16 regenerado retroactivamente** para coherencia editorial

---

## 📊 Destinatarios del email

rafael.durand · bellanira.hernandez · maria.alejandra.rico · javier.parra · alonso.mis · ingrid.kuhnne · david.gamboa · hugo.ascencio · ext.jesus.lizarraga · alejandro.flores · gabriela.guerra · barbara.rodriguez

## 📅 Próximo release

**Lunes 5 de Mayo · Week 18**
