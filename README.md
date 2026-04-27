# 📊 Proyecto PRICE · Supply Analytics

**PriceTravel · Supply Optimization**
Reportes semanales de disponibilidad y conversión para el equipo de Supply.

---

## 📁 Estructura del Repositorio

```
PRICE/
  _editorial/
    GUIA_EDITORIAL_Supply_Analytics.html   ← Guía de estilo única para ambos reportes
  _templates/
    Template_RatesNoDispo_Reporte.html
    Template_Checkrates_Reporte.html
    Template_Index.html
  mail/
    email_rates_nodispo_template.html
    email_checkrates_template.html
  rates-nodispo/
    week-NN/
      Editorial/   → RatesNoDispo_Reporte_Editorial.html
      Analisis/    → Analisis_Rates_NoDispo_7d.xlsx
  checkrates/
    week-NN/
      Editorial/   → checkrates_reporte_editorial.html
      Analisis/    → Analisis_Checkrates_7d.xlsx
  index.html
  README.md
```

---

## 📋 Reportes

### 1 · Supply Rates No Dispo
Analiza disponibilidad y conversión por hotel, destino, país y corporativo.

**Dataset de entrada:**
`CorpName · Hotel · PaisDestino · Destino · DistributionCategory · Trafico · %NoDispo · Bookings · gb_usd`

**Métricas clave:**
- `RPM = gb_usd / Trafico * 1M`
- `%NoDispo = NoDispo / Trafico`
- `Conversión = Bookings / Trafico`
- `Efectividad = 1 − %NoDispo`

**Severity %NoDispo:**
| Nivel | Rango |
|---|---|
| Exitosa | 0–5% |
| A Revisar | 5–20% |
| Crítica | 20–40% |
| Muy Crítica | 40–60% |
| Súper Crítica | >60% |

---

### 2 · Supply CheckRates
Analiza eficacia técnica y conversión por canal (B2C · B2B-OP · CUG).

**Dataset de entrada:**
`IdHotel · Hotel · CorpName · Canal · CheckRates Únicos · AVG Mismo CheckRate · CheckRates x HT · Efectividad · Bookings · Conversion Rate`

**Channel Weights:**
| Canal | Weight |
|---|---|
| B2C | 0.1 |
| B2B (OP) | 0.6 |
| CUG (UOP) | 0.6 |

**Severity Eficacia (%Errors):**
| Nivel | Rango |
|---|---|
| Exitosa | 0–3.8% |
| No Aceptable | 3.8–5.3% |
| Revisar | 5.3–20% |
| Crítica | 20–40% |
| Muy Crítica | 40–79% |
| Súper Crítica | 80–99% |

**Severity Conv Rate:**
| Nivel | Rango |
|---|---|
| Excelente | ≥3% |
| Buena | 1.74–3% |
| Por debajo benchmark | 1–1.74% |
| Crítica | 0.5–1% |
| Muy Crítica | 0.1–0.5% |
| Súper Crítica | <0.1% |

---

## 🎨 Sistema de Color

### Rates No Dispo
| Variable CSS | Hex | Uso |
|---|---|---|
| `--accent` | `#1E5A8C` | Valores clave · Conv RPM · TOTAL Severity |
| `--amber` | `#A86A1D` | Bajo Rendimiento · %NoDispo · Severity |
| `--green` | `#2F6C34` | Por Destino · GB positivo |
| `--red` | `#C0392B` | Semáforo crítico |
| `--ink-muted` | `#8A8377` | Valores secundarios · neutros |
| `--paper` | `#F8F4EC` | Fondo principal |

### CheckRates
| Variable CSS | Hex | Uso |
|---|---|---|
| `--accent` | `#5C469C` | Eficacia · Conv Rate · TOTAL Severity Conv Rate |
| `--amber` | `#EA0074` | Bajo Rendimiento · %Errors · Severity Eficacia |
| `--green` | `#4FC3F4` | Canasta CUG (color propio) |
| `--ink-muted` | `#8A8377` | CheckRates · Bkgs · columnas neutras |
| `--paper` | `#F8F4EC` | Fondo principal |

### Reglas de color por columna · CheckRates
| Sección | Columna | Color |
|---|---|---|
| Hoteles Críticos · Bajo Rendimiento | Eficacia + Conv Rate | `--accent` |
| Hoteles Críticos · Bajo Rendimiento | CheckRates | `--ink-muted` |
| Menor Conv Rate | Eficacia + Conv Rate | `--accent` |
| Severity Eficacia | Súper/Muy Crit/Crit/Total | `--amber` |
| Severity Conv Rate | TOTAL | `--accent` |
| Severity Conv Rate | Resto | `--ink-muted` |
| Canasta CUG · todas las tablas | Valores clave | `#4FC3F4` hardcodeado |

---

## 📐 Reglas Editoriales

| Regla | Valor |
|---|---|
| Filas en Editorial | **Top 5** por sección |
| Filas en Excel de Análisis | **Top 20** por pestaña |
| Muestra HTS | Hoteles P80 del tráfico global |
| Colores | Siempre variables CSS — nunca hardcodeados (excepción: CUG `#4FC3F4`) |
| Canastas | B2C · B2B-OP · CUG en ambos reportes |
| Prioridad estratégica | CUG y B2B-OP (Weight 0.6) > B2C (Weight 0.1) |

---

## 📅 Flujo Semanal

```
1. Recibir datasets Week-NN (2 archivos xlsx)
2. Correr análisis → métricas por sección
3. Generar Excel de Análisis (Top 20 por pestaña)
4. Poblar Template → Reporte Editorial
5. Commit: rates-nodispo/week-NN/ + checkrates/week-NN/
6. Actualizar index.html con links Week-NN
7. Generar mails (reemplazar {{WEEK_NUM}} y {{LINK_REPORTE}})
8. Enviar a lista de destinatarios
```

### Commit format
```
fix: datos Week-NN · RatesNoDispo + CheckRates · [fecha]
```

---

## 👥 Destinatarios

| Nombre | Email |
|---|---|
| Rafael Durand Gutierrez | rafael.durand@pricetravel.com |
| Bellanira Hernandez Garcia | bellanira.hernandez@pricetravel.com |
| Maria Alejandra Rico | maria.rico@pricetravel.com |
| Javier Parra Ladrón de Guevara | javier.parra@pricetravel.com |
| Alonso Mis Perez | alonso.mis@pricetravel.com |
| Ingrid Dayanna Hernandez Kuhnne | ingrid.kuhnne@pricetravel.com |
| David Carrillo Gamboa | david.gamboa@pricetravel.com |
| Hugo Iván Ascencio Martínez | hugo.ascencio@pricetravel.com |
| Ext Jesus Lizarraga | ext.jesus.lizarraga@pricetravel.com |
| Alejandro Flores | alejandro.flores@pricetravel.com |
| Gabriela Guerra | gabriela.guerra@pricetravel.com |
| Barbara Rodriguez | barbara.rodriguez@pricetravel.com |

---

## 🔐 Acceso al Reporte

**URL:** via `index.html` · Card 1 (RatesNoDispo) · Card 2 (CheckRates)
**Usuario:** pricetravel
**Contraseña:** supply2026

---

## 📌 Archivos del Proyecto (permanentes)

```
GUIA_EDITORIAL_Supply_Analytics.html
Template_RatesNoDispo_Reporte.html
Template_Checkrates_Reporte.html
Template_Index.html
Analisis_Rates_NoDispo_7d.xlsx         ← referencia de estructura
Analisis_Checkrates_7d.xlsx            ← referencia de estructura
email_rates_nodispo_template.html
email_checkrates_template.html
index.html
PROMPT_MAESTRO_PRICE.md
README.md
```

---

*Supply Optimization · PriceTravel · Actualizado Week 16 · 2026*
