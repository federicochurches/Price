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
