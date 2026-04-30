# PRICE · Release Workflow

Este documento describe el proceso semanal para generar y publicar los Reportes **CheckRates** y **RatesNoDispo** de Supply Optimization · PriceTravel.

> **Versión actual: v1.6 · Etapa 2** (Abr 2026) · Horizontalización + Severity simétrico. Ver changelog al final.

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
├── rates-nodispo/
│   ├── _template/
│   │   └── Template_RatesNoDispo_Reporte.html
│   ├── week-16/
│   │   ├── Editorial/RatesNoDispo_Reporte_Editorial_Week16.html
│   │   └── Analisis/Analisis_Rates_NoDispo_7d.xlsx
│   └── week-17/
│       ├── Editorial/RatesNoDispo_Reporte_Editorial_Week17.html
│       └── Analisis/Analisis_Rates_NoDispo_7d.xlsx
├── checkrates/
│   ├── _template/
│   │   └── Template_Checkrates_Reporte.html
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
├── mail/                                      (NO se publica en Pages)
└── docs/
    └── README.md                               (este archivo)
```

#### URLs públicas

- **Hub interno**: `https://analytics-desk.netlify.app/`
- **RatesNoDispo**: `https://federicochurches.github.io/Price/rates-nodispo/week-NN/Editorial/RatesNoDispo_Reporte_Editorial_WeekNN.html`
- **CheckRates**: `https://federicochurches.github.io/Price/checkrates/week-NN/Editorial/CheckRates_Reporte_Editorial_WeekNN.html`

---

## 🚀 Workflow semanal (Lunes)

#### Paso 1 · Recibir datasets

El equipo envía los archivos Excel de la semana:
```
Rates_NoDispo_W<NN>.xlsx     (pestañas: Canasta ALL · B2C · OP · UOP)
CheckRates_W<NN>.xlsx        (pestañas: TOTALES · Canal B2C · Canal OP · Canal UOP)
```

#### Paso 2 · Organizar datasets originales

```bash
python scripts/organize_datasets.py 17 ~/Downloads/Rates_NoDispo_W17.xlsx ~/Downloads/CheckRates_W17.xlsx
```

#### Paso 3 · Generar reportes de la semana

```bash
python scripts/prepare_week.py 17 ~/Downloads/CheckRates_W17.xlsx
```

#### Paso 4 · Revisar visualmente (checklist 10 min)

Ver guías editoriales en `_manual/`.

**RatesNoDispo — puntos clave:**
- P80 benchmark: `Trafico >= quantile(0.8)` del dataset total
- RPM benchmark global P80: calculado semanalmente (W17 = 2.60)
- No Dispo benchmark P80: calculado semanalmente (W17 = 3.6%)
- Colores: B2C=pink (#EA0074) · OP=celeste (#4FC3F4) · CUG=violeta (#5C469C)
- Filtros F3/F4/F5 canastas: n≥3 hoteles · bkgs≥5 · tráfico≥500K para hoteles
- WoW por canasta: disponible desde W16 dataset (cada hoja tiene canastas)
- F4 sin delta WoW (outlier estadístico por cambio brusco de NoDispo)

**CheckRates — puntos clave:**
- Por Corporativo: CK ≥ 500 · n ≥ 3 hoteles
- Menor Conv Rate: CK ≥ 2.000 · Bookings ≥ 3
- Colores: B2C=pink (#EA0074) · OP=violeta (#5C469C) · CUG=celeste (#4FC3F4)

#### Paso 5 · Commit y Push (GitHub Desktop)

**RatesNoDispo:**
```
RatesNoDispo · Week 17 · 20-26 Abr 2026
```
Archivos:
- `rates-nodispo/week-17/Editorial/RatesNoDispo_Reporte_Editorial_Week17.html`
- `rates-nodispo/week-17/Analisis/Analisis_Rates_NoDispo_7d.xlsx`
- `datasets/rates-nodispo/week-17/Rates_NoDispo_W17.xlsx`

**CheckRates:**
```
CheckRates · Week 17 · 20-26 Abr 2026
```
Archivos:
- `checkrates/week-17/Editorial/CheckRates_Reporte_Editorial_Week17.html`
- `checkrates/week-17/Analisis/Analisis_Checkrates_7d.xlsx`
- `datasets/checkrates/week-17/CheckRates_W17.xlsx`

#### Paso 6 · Actualizar Hub de Netlify

Actualizar las cards de CheckRates y RatesNoDispo con la URL de la nueva semana.

#### Paso 7 · Enviar email

```bash
python scripts/send_email.py 17
```

---

## 🎨 Reglas de diseño · NO modificar sin actualizar la guía

#### Convenciones globales

| Elemento | Regla |
|---|---|
| **Canasta B2C** | Color `#EA0074` (magenta) en ambos reportes |
| **Canasta OP** | Color `#5C469C` (violeta) en ambos reportes |
| **Canasta CUG** | Color `#4FC3F4` (cyan) en ambos reportes |
| **Severity (Etapa 2)** | 5 niveles unificados · paleta consistente entre reportes |
| **Plan de Acción** | Numeración simple 1–10 (sin códigos QW/MP/ES) |

#### Severity · paleta Etapa 2

| Nivel | Color | Uso |
|---|---|---|
| Exitosa / Saludable | cyan `#4FC3F4` | "Está bien" |
| Por debajo / Revisar | violeta `#5C469C` | "Hay que mirar" |
| Crítica | magenta soft `#EA0074` + bg | "Atención" (solo Conv Rate CheckRates) |
| Crítica Severa | magenta solid `#EA0074` | "Urgente" |
| Súper Crítica | negro `#161616` | "Máxima gravedad" (solo Eficacia) |
| Sin Conversión | gris medio `#888780` | "Sin actividad · auditar" (solo Conv Rate CheckRates) |

#### RatesNoDispo · reglas específicas

| Elemento | Regla |
|---|---|
| P80 threshold | `Trafico >= quantile(0.8)` del dataset total |
| RPM benchmark global | Calculado semanalmente (W17 = 2.60) |
| Filtro F3 canastas | n≥3 hoteles corp · bkgs≥5 |
| Filtro F4 canastas | tráfico hotel ≥ 500K |
| WoW canastas | Disponible desde W16 — F4 sin delta (outlier) |
| Severity (5 niveles) | 0-3.8% · 3.8-5.3% · 5.3-20% · 20-79% · 80-100% |

#### CheckRates · reglas específicas

| Elemento | Regla |
|---|---|
| **Conv Rate (Etapa 2)** | `Bookings ÷ Successful CheckRates × 100` (BK/Suc · no BK/CK) |
| Por Corporativo | CK ≥ 500 · n ≥ 3 hoteles |
| Menor Conv Rate | CK ≥ 2.000 · Bookings ≥ 3 |
| Severity Eficacia (5 niveles) | 100-95 · 95-80 · 80-60 · 60-20 · 20-0 |
| Severity Conv Rate (5 niveles) | ≥1.74 · 1-1.74 · 0.5-1 · &lt;0.5 · BKGS=0 |

---

## 📊 Destinatarios del email

| Campo | Valor |
|---|---|
| **De** | `federico.iglesias@pricetravel.com` |
| **Asunto** | `Supply Optimization · Reporte [CheckRates/RatesNoDispo] Week-NN` |
| **Para** | rafael.durand, bellanira.hernandez, maria.alejandra.rico, javier.parra, alonso.mis, ingrid.kuhnne, david.gamboa, hugo.ascencio, ext.jesus.lizarraga, alejandro.flores, gabriela.guerra, barbara.rodriguez |

---

## 📅 Calendario de releases

| Week | Periodo | RatesNoDispo | CheckRates |
|---|---|---|---|
| 16 | 13–19 Abr 2026 | ✅ Publicado | ✅ Publicado |
| 17 | 20–26 Abr 2026 | ✅ Publicado · 🔄 Re-publicado Etapa 2 | ✅ Publicado · 🔄 Re-publicado Etapa 2 |
| 18 | 27 Abr – 3 May 2026 | ⏳ Próximo (formato Etapa 2 nativo) | ⏳ Próximo (formato Etapa 2 nativo) |

---

## 📝 Changelog

#### v1.6 · Etapa 2 (2026-04-30) · Horizontalización + Severity simétrico
**Cambios estructurales mayores aplicados a templates · W17 republicados · guías editoriales · mails · hub:**

- **Severity simplificado**:
  - CheckRates: §02 unifica Eficacia + Conv Rate en una sola sección con 2 columnas. Reduce de 13 a 12 secciones.
  - Eficacia → 5 niveles (Crítica + Muy Crítica → **Crítica Severa**).
  - Conv Rate → 5 niveles (Buena + Excelente → **Saludable** · Súper + Muy Crítica → **Crítica Severa**).
  - RND: 5 niveles (mantiene 13 secciones · solo 1 dimensión).
- **Paleta unificada**: Saludable + Exitosa ambos en cyan `#4FC3F4`. Sin Conversión en gris medio `#888780` (no negro).
- **9 layouts horizontalizados (opciones A–I)**:
  - A: Severity 2 cols (CheckRates)
  - B: Severity por Corp · 1 tabla unificada con Diagnóstico (CheckRates)
  - C: Análisis por Canasta · 3 cards horizontales (ambos)
  - D: Resumen Ejecutivo 2 cols (5+5 findings) (ambos)
  - E: Plan numerado 1–10 sin prefijos QW/MP/ES (ambos)
  - F: Pareo de tablas en grid 2x2 + tabla wide en canastas (ambos)
  - G: Hero · 3 alertas horizontales LV (ambos)
  - H: Resumen Ej. de canasta · 3 columnas (ambos)
  - I: Banners Excel compactos · 1 línea (ambos · 6 banners por reporte)
- **Hero Variante B**: bajada de 1 línea + 2 KPI cards con tabs CSS-only (Por Canasta · Por Corp · Por Hotel) + 3 alertas horizontales + banner Excel compacto.
  - CheckRates Hero: Eficacia + Conv Rate (tabs por Hotel)
  - RND Hero: NoDispo Rate + Conv Rate RPM (card RPM tab por Destino)
- **Plan numerado simple**: `QW1/MP1/ES1` → `1, 2, 3, ..., 10`. Prioridades temporales (Acción Rápida · Mediano Plazo · Estratégico) se mantienen visualmente vía CSS pero sin código de prefijo.
- **Bugfix W17 RND publicado**: HTML tenía 290 líneas zombie tras `</body>` con sección Método duplicada. Resuelto.
- **Templates con placeholders**: 589 (CheckRates) · 607 (RND) placeholders documentados.

#### v1.5 · W18 (2026-04-29) · Bloque Editorial Mayor

- **Eje 5 · Sección Método rediseñada**: prosa larga → tarjetas categorizadas (6 CheckRates · 5 RND).
- **Eje 5.5 · Terminología**: `CK Únicos` / `CheckRates Únicos` → `CheckRates`.
- **Eje 5.6 · Conv Rate corregido**: `Bookings ÷ Successful CheckRates` (BK/Suc · no BK/CK).
- **Eje 5.7 · Severity Eficacia rangos invertidos**: rangos en términos de Eficacia directa (no %Errors).
- **Eje 5.8 · Sort orders estandarizados**: cada tabla con sort default explícito + reglas anti-bug.
- **Eje 6.1 · §09 Análisis por Canasta**: nueva sección con tabla resumen comparativa.
- **Eje 6.2 · Vocabulario Clusters & Prioridades**:
  - Cluster del hotel: Optimizable · Conv Rate Crítico · Connectivity Issue · Tráfico Anómalo · Bajo Volumen
  - Prioridad temporal: Acción Rápida · Mediano Plazo · Estratégico

#### Historial previo

- **v1.2** (2026-04-28): Week 17 RatesNoDispo. Resúmenes ejecutivos por canasta con RPM, WoW, F3-F5 card format. Plan de Acción QW1-QW6 · MP1-MP6 · ES2. Reglas P80 + filtros F4 tráfico≥500K documentados.
- **v1.1** (2026-04-28): Week 17 CheckRates. Umbrales D (CK≥2K·Bkgs≥3), colores canasta definidos.
- **v1.0** (2026-04-27): Release inicial Week 16. Estructura por canastas integrada.
