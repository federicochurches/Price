# Price · HUB Supply Optimization

Repo de reportes semanales · `Supply Rates No Dispo` y `Supply CheckRates` · publicados en GitHub Pages.

URL pública: `https://federicochurches.github.io/Price/`

---

## Estructura del repo

```
Price/                                          (repo público de GitHub Pages)
├── README.md                                   (este archivo)
├── index.html                                  (hub de navegación)
├── .gitignore
│
├── _email/                                     (NO se publica · solo local)
│   ├── week-NN/Mail_WNN.html
│   ├── Playbook_Mail_Semanal.md
│   └── destinatarios.md
│
├── _scripts/                                   (NO se publica · solo local)
│   ├── lib/
│   ├── templates/
│   ├── commit_release.py
│   ├── release_week.py
│   └── send_email.py
│
├── _template/                                  (template del Hub)
│   └── _TEMPLATE_Hub.html
│
├── rates-nodispo/
│   ├── _manual/
│   │   └── GUIA_EDITORIAL_RatesNoDispo.html    (guía editorial RND · ⭐ actualizada W17)
│   ├── _template/
│   │   └── _TEMPLATE_RatesNoDispo_Reporte.html (template RND · ⭐ sin bugs estructurales)
│   ├── week-16/
│   │   ├── RatesNoDispo_Reporte_Editorial.html (reporte editorial)
│   │   ├── Analisis_Rates_NoDispo_7d.xlsx      (excel de análisis · Top 50)
│   │   └── Rates_NoDispo_W16.xlsx              (dataset crudo · fuente)
│   └── week-17/
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx
│       └── Rates_NoDispo_W17.xlsx
│
└── checkrates/
    ├── _manual/
    │   └── GUIA_EDITORIAL_CheckRates.html      (guía editorial CR · ⭐ actualizada W17)
    ├── _template/
    │   └── _TEMPLATE_CheckRates_Reporte.html   (template CR · con banners Excel)
    ├── week-16/
    │   ├── CheckRates_Reporte_Editorial.html
    │   ├── Analisis_Checkrates_7d.xlsx
    │   └── CheckRates_W16.xlsx
    └── week-17/
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx
        └── CheckRates_W17.xlsx
```

### URLs públicas

- **Hub interno**: `https://analytics-desk.netlify.app/`
- **RatesNoDispo**: `https://federicochurches.github.io/Price/rates-nodispo/week-NN/RatesNoDispo_Reporte_Editorial.html`
- **CheckRates**: `https://federicochurches.github.io/Price/checkrates/week-NN/CheckRates_Reporte_Editorial.html`

---

## ⚠ Decisiones consolidadas · post W17

> Antes de hacer cambios al template o reportes, leer la **Guía Editorial** completa: `rates-nodispo/_manual/GUIA_EDITORIAL_RatesNoDispo.html` y `checkrates/_manual/GUIA_EDITORIAL_CheckRates.html`

### Bandas Severity · sistema D · post W17

**Lógica D (híbrida) · documentada en post-W17:**

Severity NO se aplica uniformemente · separamos hoteles "procesables" (con conversión > 0) de los "no procesables" (sin conversión). Los hoteles con BKGS = 0 son **categoría operativa aparte**: requieren tratamiento estructural distinto (revisar conectividad API, contratos, demanda real).

**% NoDispo (sigue igual · 5 niveles):**
| Nivel | Rango |
|---|---|
| Exitosa | < 3% |
| Aceptable | 3 – 5% |
| Revisar | 5 – 20% |
| Crítica | 20 – 60% |
| Súper Crítica | > 60% |

**Conv Rate / RPM · sistema D:**

| Reporte | Métrica | Sin Conversión | Crítica | Revisar | Aceptable | Exitosa | **Target** |
|---|---|---|---|---|---|---|---|
| **RND** | RPM | BKGS = 0 (informativo) | < 1 | 1 – 2,5 | 2,5 – 4 | > 4 | **≥ 3,0** |
| **CR** | Conv Rate | BKGS = 0 (informativo) | < 0,8% | 0,8 – 1,5% | 1,5 – 2,5% | > 2,5% | **≥ 2,0%** |

**Justificación de targets:**
- **RND · RPM ≥ 3,0**: mediana de hoteles que sí convierten (3,82). Realista: ~28% ya están sobre. Aspiracional: empuja al cluster Revisar (1-2,5) hacia arriba.
- **CR · Conv Rate ≥ 2,0%**: cerca de la mediana Con Conversión (1,67%). Realista: ~35% ya superan. Industria: 1,5-3% es saludable.

**¿Por qué Sin Conversión es categoría aparte?**
Antes 60% de hoteles caían en "Súper Crítica" porque tenían BKGS = 0. Esto saturaba la severity y hacía que el reporte fuera poco accionable: nadie escala 9.000 hoteles. Ahora Sin Conversión se reporta como métrica operativa (cohorte estructural · diagnóstico técnico/contractual) y Severity se aplica solo a los que sí convierten · permitiendo priorizar acciones de pricing/optimización.

**Cómo se aplica en visualizaciones:**
- En tablas Severity: "Sin Conversión" aparece como primera fila con pill gris (`#8A8377`), seguido de un separador horizontal antes de las bandas Severity propias
- En kpis-hero cards: pill severity refleja el estado del hotel ponderado · target visible debajo
- En gauge bar (CR): 5 bandas (Súper Crítica · Crítica · Revisar · Aceptable · Exitosa) · "Sin Conversión" no se incluye en gauge porque no aplica

### Estructura kpis-hero · regla crítica

**Card global y de canasta** (RND y CR) tienen 2 cards directas con tabs estilo folder:

- Card 1: % Eficacia (CR) o %NoDispo (RND) con pill severity + gauge bar 5 niveles + WoW + tabs (País · Destino · Corp · Hotel · Channel/Canasta)
- Card 2: Conv Rate (CR) o RPM (RND) con pill severity + gauge bar 5 niveles + WoW + tabs

### Tabs sistema folder

- Inputs radio escondidos con prefijo `tab-{seccion}-{tab}`
- Labels con `border-radius: 6px 6px 0 0` · efecto folder cuando active
- En CR canasta: prefijo `tab-cb-{canasta}-{side}-{tab}` · 6 grupos (3 canastas × 2 cards)

### Channel agrupado · Producto Propio vs Third Party

- **Producto Propio:** DerbySoft, Internal, HBSI, SynXis, Siteminder, Travelclick, Omnibees
- **Third Party:** Expedia, HotelBeds Apitude, Hotel Unico V2, Travelgate

### Sistema de color

**Rates No Dispo:**
- `--accent` `#1E5A8C` (no usado en TAG · usar magenta)
- `--amber` / TAG `#EA0074` magenta
- TAG corp en H1: `#F277AC` (magenta más claro · diferenciación destinos vs corp)
- `--green` `#2F6C34`
- `--red` `#C0392B`

**CheckRates:**
- `--accent` `#5C469C` violet (TAG, valores clave, destinos H1)
- TAG corp en H1: `#9580C9` (violet más claro)
- `--amber` `#EA0074` magenta (Severity Eficacia, %Errors)
- `--green` / CUG `#4FC3F4` cyan
- `--ink-muted` `#8A8377` (CheckRates, Bookings, Sin Conversión)

### Reglas obligatorias

- **Top 5** en Editorial · **Top 50** en Excel de Análisis (post W17 · antes era Top 20)
- Pestaña "Sin Conversión" SEPARADA de "Bajo Rendimiento" en Excel
- Findings del Resumen Ejecutivo SIEMPRE empiezan con mayúscula
- Resumen Ejecutivo: 10 findings · 2 columnas · post-Alerts en cada `<details>` de canasta
- Nunca hardcodear colores fuera de `:root` excepto donde la guía lo permite (CUG `#4FC3F4`)
- CUG y B2B-OP son prioridad estratégica (Weight 0.6)
- Links a Excel: usar nombre sin sufijo de week (ej. `Analisis_Rates_NoDispo_7d.xlsx`) · la carpeta `week-NN/` ya identifica la semana

---

## Workflow semanal

1. Recibir datasets Week-NN · guardarlos en `{seccion}/week-NN/`
2. Correr análisis Python → métricas por sección
3. Generar Excel de Análisis (Top 50 por pestaña + Sin Conversión separada)
4. Poblar Template con datos nuevos → Reporte Editorial
5. Commit GitHub: agregar `rates-nodispo/week-NN/` y `checkrates/week-NN/` con los 3 archivos
6. Actualizar `index.html` con links Week-NN
7. Generar mail desde `_email/week-NN/Mail_WNN.html` (reemplazar placeholders)
8. Enviar a lista de destinatarios (12 personas en BCC)

### Commit summary format
`fix: datos Week-NN · RatesNoDispo + CheckRates · sistema bandas D · [fecha]`

---

## Action items pendientes para W18

> Pedirle al equipo de data:
> - **RND W18**: dataset crudo con `CorpName` en cada pestaña de canasta (no solo en Canasta ALL)
> - **CR W18**: dataset crudo con columna `Destino` en cada fila

Sin estos datos, hay que hacer recovery vía join Hotel→CorpName y Hotel→Destino del W16 (proxy menos preciso).

---

**Última actualización:** 1 mayo 2026 · post W17 · sistema bandas D + targets + tabs folder + Channel agrupado + Top 50
