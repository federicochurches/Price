# Estructura del Reporte Editorial · post Week 18

Cada reporte (RND y CR) sigue exactamente esta estructura. Si modificás la estructura, actualizá este archivo Y los templates HTML correspondientes.

---

## Orden de secciones · GLOBAL

```
┌───────────────────────────────────────────────────────────┐
│ MASTHEAD (header)                                         │
│   • Tag del reporte · Week NN · período                   │
│   • Logo PriceTravel · "Supply Optimization"              │
├───────────────────────────────────────────────────────────┤
│ MÉTRICAS GLOBALES INLINE                                  │
│   "X CR únicos · Y hoteles · Z Bookings · N hoteles P80"  │
├───────────────────────────────────────────────────────────┤
│ HERO · 2 KPI CARDS                                        │
│   ┌─ Card KPI principal ────┐ ┌─ Card KPI secundario ──┐  │
│   │  % grande               │ │  % grande              │  │
│   │  Pill banda + target    │ │  Pill banda + target   │  │
│   │  Gauge bar 5 niveles    │ │  Gauge bar 5 niveles   │  │
│   │  W18 / WoW / W17        │ │  W18 / WoW / W17       │  │
│   │  Tabs: País · Destino · │ │  Tabs: ...             │  │
│   │       Corp · Hotel ·    │ │                        │  │
│   │       Channel · Canasta │ │                        │  │
│   └─────────────────────────┘ └────────────────────────┘  │
├───────────────────────────────────────────────────────────┤
│ ALERTAS · CASOS CRÍTICOS DE LA SEMANA                     │
│   3 cards: Hoteles · Destinos · Channels (CR) o Corp (RND)│
├───────────────────────────────────────────────────────────┤
│ 🎯 RESUMEN EJECUTIVO                                      │
│   Card border-top 3px negro, fondo paper-soft             │
│   Grid 2 columnas · 5+5 findings                          │
│   Cada finding: N° + valor numérico destacado +           │
│                <strong>Título</strong> Descripción         │
├───────────────────────────────────────────────────────────┤
│ SEVERIDAD · 2 columnas                                    │
│   Eficacia/NoDispo + ConvRate/RPM con barras horizontales │
├───────────────────────────────────────────────────────────┤
│ TOP 5/10 LISTINGS por sección                             │
│   • Demanda No Convertida (RND) o Hoteles Críticos (CR)   │
│   • Bajo Rendimiento (Top 10 a 2 cols)                    │
│   • Sin Conversión (Top 10 a 2 cols, separada)            │
│   • Por Corporativo                                        │
│   • Por Destino / Por País                                 │
├───────────────────────────────────────────────────────────┤
│ PLAN DE ACCIÓN                                            │
│   6 acciones · 2 columnas (3+3) · catálogo Áreas v2       │
│   Quick Win · Mid Priority · Estratégica                  │
├───────────────────────────────────────────────────────────┤
│ ANÁLISIS POR CANASTA                                      │
│   <details> colapsables: B2B Opaco · CUG · B2C            │
│   (cada uno con su propio bloque interno)                 │
└───────────────────────────────────────────────────────────┘
```

---

## Orden de secciones · DENTRO DE CANASTA

Cada `<details class="canasta-block">` contiene:

```
1. KPI BLOCK (Eficacia + ConvRate o %NoDispo + RPM compactos)
2. ALERTAS · Casos Críticos · Canasta X (3 cards)
3. 🎯 RESUMEN EJECUTIVO · Canasta X (10 findings · 2 cols)
4. SEVERIDAD (Eficacia + ConvRate · 2 cols con barras)
5. TABS POR DIMENSIÓN (Destino · Corp · Hotel · Channel/País · 10 a 2 cols)
6. TOP 10 BAJO RENDIMIENTO · Canasta X (5+5)
7. TOP 10 SIN CONVERSIÓN · Canasta X (5+5)
8. 📝 SÍNTESIS EJECUTIVA (texto narrativo corto)
9. PLAN DE ACCIÓN · Canasta X (6 acciones · 2 cols)
```

---

## Estructura del Resumen Ejecutivo (CRÍTICO)

El template literal del Resumen Ejecutivo es **NO NEGOCIABLE**:

```html
<!-- Header overline pequeño · FUERA del card -->
<div style="margin-top:64px;font-size:11px;...">
  <span style="color:{ACCENT};">🎯</span><span>Resumen Ejecutivo</span>
</div>

<!-- Card con border-top 3px negro y fondo paper-soft -->
<div style="padding:28px 32px;background:var(--paper-soft);
            border:1px solid var(--rule);border-top:3px solid #161616;
            border-radius:6px;">
  <div class="exec-2cols" style="display:grid;
                                  grid-template-columns:1fr 1fr;
                                  gap:14px 28px;">
    <!-- Columna 1 · findings 1–5 -->
    <ol style="list-style:none;padding:0;margin:0;">
      <li style="display:flex;gap:10px;align-items:baseline;
                 font-size:12.5px;line-height:1.55;
                 color:var(--ink-soft);margin-bottom:14px;">
        <span style="width:18px;...">1.</span>
        <span style="min-width:55px;color:{ACCENT};
                     font-size:13px;font-variant-numeric:tabular-nums;">
          VALOR_DESTACADO
        </span>
        <span style="flex:1;">
          <strong>Título</strong> Descripción.
        </span>
      </li>
      ...
    </ol>
    <!-- Columna 2 · findings 6–10 -->
    <ol>...</ol>
  </div>
</div>
```

Reglas:
- Header overline FUERA del card · text-transform uppercase · letter-spacing wide
- Card SIEMPRE con `border-top:3px solid #161616`
- Grid 2 columnas, gap `14px 28px`
- Findings = lista de 10 dicts con `{numero, titulo, desc}`
- NO usar highlights `.hl` (eso era el formato viejo, deprecado en Week 18)
- El **valor numérico destacado** va en color del reporte (#EA0074 RND / #5C469C CR) y `font-variant-numeric: tabular-nums`

---

## Helpers Python · post Week 18

| Helper | Función |
|---|---|
| `template_resumen.py` | `render_resumen_ejecutivo(findings, accent_color, scope)` |
| `template_alertas.py` | `render_alertas_block(scope_text, accent, card_h, card_d, card_c)` |
| `template_severity.py` | `render_severity_2cols(left_block, right_block)` con `LEVELS_*` predefinidos |

Estos helpers reemplazan la lógica que antes se construía inline en los renderers, y replican el snippet HTML literal del template (`_template/_TEMPLATE_*.html`).

---

## Snippets de referencia

Los archivos en `_scripts/snippets/` son extracciones literales del template, copiadas como referencia para los helpers:
- `snippet_resumen_global_cr.html`
- `snippet_resumen_global_rnd.html`
- `snippet_alertas_canasta.html`
- `snippet_alertas_canasta_rnd.html`

> **Cuando el usuario reporta "no toma el template", lo primero es ABRIR el template HTML directamente y comparar el snippet generado contra el snippet del template.** No asumir desde el output visual.

---

## 📂 Ubicación de templates en el repo

> **Convención post Week 18:** `_template/` raíz es **solo para el Hub**. Cada reporte tiene su propio `_template/` y `_manual/` dentro de su carpeta.

```
Price/
├── _template/_TEMPLATE_Hub.html
├── rates-nodispo/
│   ├── _template/_TEMPLATE_RatesNoDispo_Reporte.html
│   └── _manual/GUIA_EDITORIAL_RatesNoDispo.html
└── checkrates/
    ├── _template/_TEMPLATE_CheckRates_Reporte.html
    └── _manual/GUIA_EDITORIAL_CheckRates.html
```

Cuando el pipeline necesite leer el template, el path es:
- RND: `rates-nodispo/_template/_TEMPLATE_RatesNoDispo_Reporte.html`
- CR: `checkrates/_template/_TEMPLATE_CheckRates_Reporte.html`
- Hub: `_template/_TEMPLATE_Hub.html`

---

## 🔄 Reorganización Week 18 (mejora post lanzamiento)

A partir de Week 18 (sesión cierre · post mejoras de canasta), las **secciones globales** del editorial pasan de **6 secciones apiladas** a **2 bloques con tabs**:

### RND · estructura actualizada

```
Sección 01 · Resumen Ejecutivo (sin cambio)
Sección 02 · Severidad (NoDispo + IPM en 2 cols, sin cambio)

Sección 03 · Análisis por hotel (NUEVO · 3 tabs)
   ├── Tab DEMANDA NC   · Top 10 hoteles con mayor demanda no convertida
   ├── Tab BAJO REND    · Top 10 hoteles con BKGS>0 y IPM Crítica/Revisar
   └── Tab SIN CONV     · Top 10 hoteles con BKGS=0 (cohorte estructural)

Sección 04 · Por dimensión (NUEVO · 3 tabs)
   ├── Tab CORPORATIVO  · Top 10 corporativos por tráfico
   ├── Tab DESTINO      · Top 10 destinos por tráfico
   └── Tab PAÍS         · Top 10 países por tráfico

Sección 05 · Plan de Acción (sin cambio)
Sección 06+ · Análisis por canasta (sin cambio · 3 canastas)
```

### CR · estructura actualizada

```
Sección 01 · Resumen Ejecutivo
Sección 02 · Severidad (Eficacia + Conv Rate en 2 cols)
Sección 03 · Channel agrupado (Producto Propio · Third Party · sin cambio)

Sección 04 · Análisis por hotel (NUEVO · 4 tabs)
   ├── Tab CRÍTICOS        · peor Eficacia con BKGS>0
   ├── Tab BAJO REND       · alto volumen + ConvRate Crítica/Revisar
   ├── Tab SIN CONV        · BKGS=0
   └── Tab MENOR CONVRATE  · Top 10 peores conversores absolutos

Sección 05 · Por dimensión (NUEVO · 3 tabs)
   ├── Tab CORPORATIVO  · Top 10 corp por CR únicos
   ├── Tab DESTINO      · Top 10 destinos por CR únicos
   └── Tab CHANNEL      · split Producto Propio + Third Party (todos los channels)

Sección 06 · Plan de Acción
Sección 07+ · Análisis por canasta (3 canastas)
```

---

## Snippet literal · estructura de bloque con tabs

```html
<section id="por-hotel">
  <div class="section-head">
    <div>
      <div class="section-num">Sección 03</div>
      <h2 class="section-title">Análisis por hotel</h2>
      <span class="section-subtitle">Top 10 · 3 ópticas analíticas</span>
      <p class="section-kicker">Descripción general del bloque...</p>
    </div>
  </div>
  
  <div class="tabs-block">
    <input checked id="tab-h-dnc" name="tabs-h" type="radio">
    <input id="tab-h-br" name="tabs-h" type="radio">
    <input id="tab-h-sc" name="tabs-h" type="radio">
    
    <div class="tabs-row">
      <label class="tab-label" for="tab-h-dnc">Demanda NC</label>
      <label class="tab-label" for="tab-h-br">Bajo Rendimiento</label>
      <label class="tab-label" for="tab-h-sc">Sin Conversión</label>
    </div>
    
    <div class="tab-panels">
      <div class="tab-panel" data-tab="dnc">
        <p class="tab-kicker">Kicker específico del tab activo...</p>
        <!-- Tabla Top 10 a 2 columnas (5 izq / 5 der) -->
      </div>
      <!-- ... más paneles -->
    </div>
  </div>
  
  <div class="detail-callout">
    <div>
      <div class="lbl">Detalle completo</div>
      <div class="msg">El Top 50 de cada óptica está en pestañas separadas del Excel adjunto.</div>
    </div>
    <a class="badge-link" href="Analisis_..._7d.xlsx">Excel ↗</a>
  </div>
</section>
```

### CSS clave para los tabs

```css
.tabs-block{border:1px solid var(--rule);background:var(--paper-soft);border-radius:6px;padding:18px 22px;}
.tabs-block .tab-panel{display:none;}
.tabs-block #tab-h-dnc:checked ~ .tab-panels .tab-panel[data-tab="dnc"]{display:block !important;}
/* Importante: !important + selector con .tabs-block prefix porque .tab-panel{display:none} */
/* del CSS hero tiene mismo nivel de especificidad y aparece después en la cascada. */
```

### Implementación en código

- `render_rnd_p2.py` → `render_bloque_hoteles()` y `render_bloque_dimensiones()` (bloques globales)
- `render_rnd_p3.py` → `render_canasta_block()` — cada canasta replica la estructura global:
  - KPI cards con gauge 5 niveles + tabs (País · Destino · Corp · Hotel) + pills WoW
  - Resumen Ejecutivo con pills de banda y delta WoW
  - Bloque Análisis por Hotel (3 tabs: Demanda No Convertida · Bajo Rendimiento · Sin Conversión)
  - Bloque Análisis por Dimensión (3 tabs: Corporativo · Destino · País)
  - Síntesis · Plan de Acción · Banner Excel
- `render_cr_p2.py` → `render_bloque_hoteles_cr()` y `render_bloque_dimensiones_cr()`
- `asset_rnd_head.html` y `asset_cr_head.html` → CSS de los tabs

---

## 📥 Banner de descarga por canasta (post Week 18)

Cada bloque de canasta termina con un banner minimalista de descarga del Excel filtrado:

```html
<!-- Justo después del Plan de Acción de la canasta, antes del cierre </div></details> -->
<div style="margin-top:24px;padding:14px 18px;background:var(--paper-soft);
            border:1px solid var(--rule);border-radius:4px;
            display:flex;align-items:center;justify-content:space-between;gap:16px;">
  <div style="font-size:12px;color:var(--ink-soft);line-height:1.4;">
    <span style="font-size:13px;color:var(--ink);">📥</span>
    &nbsp;&nbsp;Descargar análisis completo · 
    <strong style="color:#EA0074;">Canasta {short}</strong>
    <span style="display:inline-block;margin-left:8px;font-size:11px;color:var(--ink-muted);">
      N pestañas · Top 50 por dimensión
    </span>
  </div>
  <a href="Analisis_{tipo}_{B2C|OP|CUG}_7d.xlsx" 
     style="display:inline-block;padding:6px 14px;background:#EA0074;color:#fff;
            font-size:11px;font-weight:600;text-decoration:none;border-radius:3px;
            letter-spacing:.04em;text-transform:uppercase;">Excel ↗</a>
</div>
```

### Naming convention de Excels por canasta

| Reporte | Canasta | Filename |
|---|---|---|
| CR  | B2C       | `Analisis_Checkrates_B2C_7d.xlsx` |
| CR  | B2B Opaco | `Analisis_Checkrates_OP_7d.xlsx`  |
| CR  | CUG       | `Analisis_Checkrates_CUG_7d.xlsx` |
| RND | B2C       | `Analisis_Rates_NoDispo_B2C_7d.xlsx` |
| RND | B2B Opaco | `Analisis_Rates_NoDispo_OP_7d.xlsx`  |
| RND | CUG       | `Analisis_Rates_NoDispo_CUG_7d.xlsx` |

