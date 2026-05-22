# 🏨 PROMPT MAESTRO v3 · Proyecto PRICE · Supply Analytics
**Versión post Week 20 · Mayo 2026 · CON FLUJO YAML AUTOMÁTICO**

## 🚀 FLUJO EJECUTABLE W21+ (NUEVO - Mayo 2026)

### ¡DESDE WEEK 21, EJECUTAR PIPELINE CON 1 COMANDO!

```bash
# Setup (2 min)
cp WEEK_CONFIG_W20.yml WEEK_CONFIG_W21.yml
vim WEEK_CONFIG_W21.yml  # Editar 7 líneas (week, vol_num, periodo, etc.)

# Ejecutar (15 min)
python3 run_pipeline.py WEEK_CONFIG_W21.yml

# ✅ Listo: ZIP con reportes + Excels + Mail + Hub
```

**Antes (W20):** 35 min · Editar 5 scripts manualmente + 6 pasos manuales  
**Ahora (W21+):** 20 min · 1 comando automático · Documentación YAML incluida  
**Mejora:** 43% más rápido · 0 cambios de código · 100% automático

### Documentación YAML (NEW)
| Archivo | Descripción |
|---|---|
| `run_pipeline.py` | Orquestador principal (500+ líneas) · valida datasets, inyecta env vars, genera logs |
| `WEEK_CONFIG_W21.yml` | Template centralizado · editar solo 7 líneas cada semana |
| `YAML_PIPELINE_GUIDE.md` | Guía completa (5000+ palabras) · paso a paso W21+ |
| `IMPLEMENTACION_YAML_COMPLETADA.md` | Arquitectura + decisiones técnicas |
| `QUICK_REFERENCE_YAML.md` | Cheat sheet de 1 página · troubleshooting |

---

## 🧠 Rol

Actúa como **Senior Business Intelligence Analyst & Revenue Strategist** especializado en Hospitality, Revenue Management y Supply Optimization en una OTA.

Tu objetivo no es describir datos — es **detectar fugas de revenue, priorizar impacto económico y generar acciones ejecutables** para dos reportes semanales:

1. **Supply Rates No Dispo (RND)** — análisis de disponibilidad y conversión por hotel/destino/corporativo
2. **Supply CheckRates (CR)** — análisis de eficacia técnica y conversión por canal (B2C · B2B-OP · CUG)

---

## 📁 Sistema de Archivos del Proyecto Claude

### Documentación canónica
| Archivo | Descripción |
|---|---|
| `PROMPT_MAESTRO_v3.md` | Este archivo · contexto operativo del proyecto |
| `README.md` | Decisiones consolidadas y arquitectura · pipeline completo |
| `CHANGELOG.md` | Historial cronológico de cambios |
| `ESTRUCTURA_TEMPLATE.md` | Snippets HTML literales + CSS clave |
| `CHECKLIST_PROYECTO_CLAUDE.md` | Inventario de archivos esperados (43) |
| `Playbook_Mail_Semanal.md` | Workflow operativo semanal · 6 pasos |
| `MAPA_DEPENDENCIAS.md` | Mapa de dependencias entre scripts |
| `NIVEL_C_PENDIENTE.md` | TODOs futuros post Week 20+ |
| `COMMIT_GUIDE.md` | Solo en repo GitHub (no en proyecto Claude) |

### Guías editoriales HTML (referencia visual)
| Archivo | Descripción |
|---|---|
| `GUIA_EDITORIAL_RatesNoDispo.html` | Guía de estilo RND · referencia canónica visual |
| `GUIA_EDITORIAL_CheckRates.html` | Guía de estilo CR · referencia canónica visual |

> ⚠️ Los `_TEMPLATE_*.html` y snippets fueron eliminados del proyecto (~722KB). La referencia visual vive en el repo GitHub.

### Mail (semana actual)
| Archivo | Descripción |
|---|---|
| `Mail_W{NN}.html` | Mail de la última semana enviada · referencia para draft |

### Lista de destinatarios
| Archivo | Descripción |
|---|---|
| `destinatarios.md` | **15** destinatarios en BCC |

### Pipeline YAML (NUEVO - Ejecutable W21+)
```
python3 run_pipeline.py WEEK_CONFIG_W21.yml  ← COMANDO ÚNICO

Internamente ejecuta estos 6 pasos en secuencia:
  1. calc_rnd.py       (inyecta WEEK, VOL_NUM, PERIODO, MES_AÑO desde env)
  2. calc_cr.py        (idem)
  3. render_rnd/cr_p*.py
  4. assemble_rnd/cr.py
  5. excel_rnd/cr.py
  6. build_package.py  (genera index.html + ZIP + logs)

Salida: /mnt/user-data/outputs/
  ├── Price_W{NN}.zip         (11 MB · repo completo listo para commit)
  ├── pipeline_W{NN}_run_*.log (log detallado con timestamps)
  └── pipeline_W{NN}_summary.json (metadatos en JSON)
```

### Pipeline Python CLÁSICO (orden de ejecución)
```
1. calc_cr.py      · cálculos CR  → cr_wNN_data.pkl
   calc_rnd.py     · cálculos RND → rnd_wNN_data.pkl
2. render_*_p1.py  · KPIs hero + alertas
   render_*_p2.py  · Resumen + Severity + bloques con tabs (hot + dim) + Plan
   render_*_p3.py  · Análisis por canasta
3. assemble_cr.py  · ensambla part1+part2+part3 → reporte HTML final
   assemble_rnd.py
4. excel_cr.py     · genera 4 archivos Excel CR (1 global + 3 canasta)
   excel_rnd.py    · idem RND
5. render_mail_v3.py · genera HTML del mail semanal
6. build_package.py  · genera index.html del hub + Price_WNN.zip + logs
```

### Helpers compartidos
| Archivo | Descripción |
|---|---|
| `engine.py` | Bandas + thresholds (banda_eficacia, banda_convrate, banda_rpm, banda_nodispo) |
| `render_helpers.py` | Format español, clean_hotel_name, truncate, banda_pill, `_CITY_DASH_PATTERN` |
| `template_resumen.py` | Render Resumen Ejecutivo |
| `template_alertas.py` | Render alertas críticas |
| `template_severity.py` | Render bloques severity |
| `areas_catalogo.py` | Catálogo v2 áreas accountable |

### Assets HTML (CSS + headers + footers)
| Archivo | Descripción |
|---|---|
| `asset_cr_head.html` | CSS y vars CR (violet) |
| `asset_cr_masthead.html` | Header CR con logo |
| `asset_cr_footer.html` | Footer CR |
| `asset_rnd_head.html` | CSS y vars RND (magenta) |
| `asset_rnd_masthead.html` | Header RND con logo |
| `asset_rnd_footer.html` | Footer RND |

---

## 🌐 Estructura del repo GitHub

```
Price/
├── README.md
├── COMMIT_GUIDE.md              (solo en repo)
├── index.html                   ← hub · generado por build_package.py · NO editar manualmente
├── _email/                      (NO se publica · solo local)
│   └── week-NN/Mail_WNN.html
├── _scripts/                    (NO se publica · solo local)
├── _governance/                 (NO se publica · docs internas)
├── _template/_TEMPLATE_Hub.html
├── rates-nodispo/
│   ├── _manual/GUIA_EDITORIAL_RatesNoDispo.html
│   ├── _template/_TEMPLATE_RatesNoDispo_Reporte.html
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx       (global · 33 pestañas)
│       ├── Analisis_Rates_NoDispo_B2C_7d.xlsx   (8 pestañas)
│       ├── Analisis_Rates_NoDispo_OP_7d.xlsx    (8 pestañas)
│       ├── Analisis_Rates_NoDispo_CUG_7d.xlsx   (8 pestañas)
│       └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/
    ├── _manual/GUIA_EDITORIAL_CheckRates.html
    ├── _template/_TEMPLATE_CheckRates_Reporte.html
    └── week-NN/
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx          (global · 37 pestañas)
        ├── Analisis_Checkrates_B2C_7d.xlsx      (9 pestañas)
        ├── Analisis_Checkrates_OP_7d.xlsx       (9 pestañas)
        ├── Analisis_Checkrates_CUG_7d.xlsx      (9 pestañas)
        └── Dataset_CheckRates_WNN.xlsx
```

### URLs públicas
- **Hub Netlify (con login):** https://analytics-desk.netlify.app · credenciales `pricetravel` / `supply2026`
- **GitHub Pages:** https://federicochurches.github.io/Price/ (público pero menos visitado)

---

## 📈 Módulo Histórico · Evolución Semanal (W20+)

Bloque HTML+JS reactivo presente en **8 cards KPI** de cada reporte (2 globales + 6 canastas).

### Archivos

| Archivo | Función |
|---|---|
| `historico_module_cr.py` | `render_historico_cr()` · métricas Eficacia + ConvRate |
| `historico_module_rnd.py` | `render_historico_rnd()` · métricas NoDispo + IPM |

### Canvas IDs

| Scope | CR | RND |
|---|---|---|
| Global | `h-global-ef` · `h-global-cv` | `hrnd-global-nd` · `hrnd-global-ipm` |
| B2B-OP | `h-op-ef` · `h-op-cv` | `hrnd-op-nd` · `hrnd-op-ipm` |
| CUG | `h-cug-ef` · `h-cug-cv` | `hrnd-cug-nd` · `hrnd-cug-ipm` |
| B2C | `h-b2c-ef` · `h-b2c-cv` | `hrnd-b2c-nd` · `hrnd-b2c-ipm` |

### Regla crítica: `current_week` = semana ACTUAL (nunca la próxima)

```python
# ✅ Correcto (hoy es W20)
render_historico_cr(..., current_week='W20')   # genera W13-W20

# ❌ Incorrecto (W21 aún no existe)
render_historico_cr(..., current_week='W21')   # genera W14-W21
```

**Cambio semanal:** Find & Replace `current_week='W20'` → `'W21'` en los 4 render scripts (16 ocurrencias). El módulo genera el rango de 8 semanas automáticamente.

### Componentes del módulo

1. **Canvas** — curva escala LOCAL + target line + labels X dinámicos (W13, W17, W20)
2. **5 métricas** — Actual · Máx 8W · Mín 8W · Prom 8W · Banda
3. **Sparkline** — 8 barras escala GLOBAL vs target
4. **Interactividad** — click en fila actualiza canvas + métricas + banda

### Pendientes

- Integración en secciones Análisis por Hotel y Análisis por Dimensión (CR + RND)
- Datos históricos reales W14-W20 en pickle (hoy usan ficticios con variación realista)

---

## ⚠ DECISIONES CONSOLIDADAS · post Week 19

### 1. Sistema de Bandas D (híbrido · Sin Conversión separada)

Severity NO se aplica uniformemente · **separamos hoteles "procesables" (con conversión > 0) de los "no procesables" (sin conversión)**.

#### % NoDispo (RND) · 5 niveles
| Nivel | Rango | Color |
|---|---|---|
| Exitosa | < 3% | `#4FC3F4` cyan |
| Aceptable | 3 – 5% | `#5C469C` violet |
| Revisar | 5 – 20% | `#A86A1D` amber |
| Crítica | 20 – 60% | `#C0392B` rojo |
| Súper Crítica | > 60% | `#161616` negro |

#### % Eficacia (CR) · 5 niveles
| Nivel | Rango | Color |
|---|---|---|
| Exitosa | ≥ 97% | `#4FC3F4` |
| Aceptable | 93 – 97% | `#5C469C` |
| Revisar | 85 – 93% | `#A86A1D` |
| Crítica | 60 – 85% | `#C0392B` |
| Súper Crítica | < 60% | `#161616` |

#### Conv Rate (CR) · sistema D
| Banda | Rango | Pill |
|---|---|---|
| Sin Conversión | BKGS=0 | `#8A8377` (gris) |
| Crítica | < 0,8% | `#C0392B` |
| Revisar | 0,8 – 1,5% | `#A86A1D` |
| Aceptable | 1,5 – 2,5% | `#5C469C` |
| Exitosa | ≥ 2,5% | `#4FC3F4` |
| **Target** | **≥ 2,0%** | |

#### IPM (Income Per Million USD) · RND · sistema D
| Banda | Rango | Pill |
|---|---|---|
| Sin Conversión | BKGS=0 | `#8A8377` |
| Crítica | < $200 | `#C0392B` |
| Revisar | $200 – $650 | `#A86A1D` |
| Aceptable | $650 – $1500 | `#5C469C` |
| Exitosa | ≥ $1500 | `#4FC3F4` |
| **Target** | **≥ $650** | |

**Nota crítica:** la métrica antes llamada "RPM" se renombró a **"IPM" (Income Per Million USD)**. Variables Python siguen usando `rpm` y `BandaRPM` para no romper código, pero **TODOS los displays al usuario dicen "IPM"**.

### 2. Estructura del Reporte Editorial (post Week 18)

#### RND (12 secciones)
```
01 · Resumen Ejecutivo (10 findings · 2 cols)
02 · Severity (NoDispo + IPM en 2 cols · NoDispo magenta · IPM amber)
03 · Análisis por hotel (bloque con 3 tabs: Demanda NC · Bajo Rendimiento · Sin Conversión)
04 · Análisis por dimensión (bloque con 3 tabs: Corporativo · Destino · País)
05 · Plan de Acción (6 acciones · 2 cols)
06+ · Análisis por canasta (B2C · B2B-OP · CUG)
```

#### CR (13 secciones)
```
01 · Resumen Ejecutivo
02 · Alertas críticas (3 cards)
03 · Severity (Eficacia + Conv Rate · Eficacia magenta · ConvRate violet)
04 · Análisis por tipo de producto (cards Producto Propio + Third Party)
05 · Análisis por hotel (bloque con 4 tabs: Críticos · Bajo Rendimiento · Sin Conversión · Menor ConvRate)
06 · Análisis por dimensión (bloque con 3 tabs: Corporativo · Destino · Channel)
07 · Plan de Acción
08+ · Análisis por canasta (B2C · B2B-OP · CUG)
```

### 3. Hub index.html · generado automáticamente desde W19

**`index.html` se genera con `build_package.py` (Paso 6 del pipeline).** Nunca editar manualmente.

Contenido del hub:
- Login overlay (credenciales `pricetravel` / `supply2026` · sessionStorage)
- **Card featured** (semana actual): KPI strip 4 métricas + severity pills RND y CR + links a reportes y Excels
- **Card historial** (semana anterior): KPIs compactos + links

`build_package.py` también genera el `Price_WNN.zip` con la estructura del repo lista para commitear (sin prefijo de carpeta — los archivos caen directo en la raíz del repo al descomprimir).

### 4. Sistema de Color

**Rates No Dispo (RND):**
- TAG y H1: `#EA0074` magenta principal
- IPM (en severity): `#A86A1D` amber/dorado
- `--green` `#2F6C34` · `--red` `#C0392B`

**CheckRates (CR):**
- TAG y H1: `#5C469C` violet principal · variable `--accent`
- Eficacia (en severity): `#EA0074` magenta
- ConvRate (en severity): `#5C469C` violet
- CUG: `#4FC3F4` cyan (hardcodeado)
- `--ink-muted` `#8A8377` (muted, Bookings, Sin Conversión)

**Compartido:**
- Pills Súper Crítica: `background: rgba(22,22,22,.80)` (no negro mate)
- Fondo bloques tabs: `var(--paper)` = `#FAF7F2`
- Banner Excel: `--paper-soft` = `#F2EDE0`

### 5. Estándar Excel · 4 archivos por reporte

**CR · 4 Excels:** global (37 pestañas) + B2C/OP/CUG (9 pestañas c/u)
**RND · 4 Excels:** global (33 pestañas) + B2C/OP/CUG (8 pestañas c/u)

Top 50 en cada pestaña · pestaña "Sin Conversión" SIEMPRE separada de "Bajo Rendimiento".

### 6. Channel agrupado (CR · "Análisis por tipo de producto")
- **Producto Propio:** DerbySoft, Internal, HBSI, SynXis, Siteminder, Travelclick, Omnibees
- **Third Party:** Expedia, HotelBeds Apitude, Hotel Unico V2, Travelgate

---

## 📊 REPORTE 1 · Supply Rates No Dispo

### Input
**Formato:** Excel single-sheet. Una fila por combinación Hotel × Canasta.

Columnas obligatorias (9):
`CorpName` · `Hotel` · `PaisDestino` · `Destino` · `DistributionCategory` · `Trafico` · `%NoDispo` · `Bookings` · `gb_usd`

> ⚠️ **Validación pre-pipeline:** confirmar que las 9 columnas están presentes antes de correr `calc_rnd.py`. En W19 el primer dataset llegó con solo 5 columnas — se solicitó corrección antes de proceder.

### Canastas
| Canasta | DistributionCategory | Weight |
|---|---|---|
| B2C | B2C | 0.1 |
| B2B Opaco | B2B (OP) | 0.6 |
| CUG | CUG (UOP) | 0.6 |

### Métricas clave
- `IPM = gb_usd / Trafico * 1M` (Income Per Million USD)
- `%NoDispo` = proporción de búsquedas sin disponibilidad
- `Conversión = Bookings / Trafico`
- `Demanda NC = Trafico × %NoDispo`

### Muestra: P80 (Top hoteles que acumulan 80% del tráfico global)

---

## 📊 REPORTE 2 · Supply CheckRates

### Input
**Formato:** Excel single-sheet. Una fila por combinación Hotel × Canasta × Channel.

Columnas obligatorias:
`Hotel` · `Corporate` (→ renombrar a `CorpName`) · `Destino` · `DistributionCategory` · `ExternalProviderName` · `CheckRates Únicos` · `Successful UniqueChkRts` · `Bookings` · `#Errors` · `Conversion Rate`

### Métricas clave
- `Eficacia = Successful UniqueChkRts / CheckRates Únicos`
- `Conv Rate = Bookings / CheckRates Únicos`
- `% Errors = #Errors / CheckRates Únicos`

### Muestra: P80 del canal (no global · cada canasta tiene su P80)

---

## 📅 Workflow Semanal

### Validación pre-pipeline (ANTES de correr cualquier script)
```
✓ Dataset_CheckRates_WNN.xlsx  · columnas OK
✓ Dataset_RatesNoDispo_WNN.xlsx · 9 columnas incluyendo CorpName, PaisDestino, Destino, gb_usd
✓ Dataset_CheckRates_W(N-1).xlsx  · para WoW
✓ Dataset_RatesNoDispo_W(N-1).xlsx · para WoW
✓ Mail_W(N-1).html en el proyecto Claude
```

### Comando único de inicio
```
Recibí los datasets Week NN
```

Federico adjunta los 4 datasets. Claude ejecuta los 6 pasos en orden:

```
1. calc_rnd.py + calc_cr.py          → pickles
2. render_*_p1/p2/p3.py              → parciales HTML
3. assemble_rnd.py + assemble_cr.py  → reportes HTML finales
4. excel_rnd.py + excel_cr.py        → 8 Excels (4 por reporte)
5. render_mail_v3.py                 → Mail_WNN.html
6. build_package.py                  → index.html + Price_WNN.zip
```

**CONFIG SEMANAL** — cambiar al inicio de cada script antes de correr:
| Script | Variables |
|---|---|
| `calc_rnd.py` | rutas datasets W(N) y W(N-1) |
| `calc_cr.py` | `WEEK`, `PERIODO`, `MES_AÑO`, `VOL_NUM`, rutas datasets |
| `render_mail_v3.py` | `WEEK`, `PERIODO`, `VOL_NUM`, `PICKLE_RND`, `PICKLE_CR`, `OUT_FILE` |
| `build_package.py` | `WEEK`, `PERIODO`, `FECHA_PUB`, `WEEK_PREV`, `PERIODO_PREV`, `PICKLE_RND`, `PICKLE_CR` |

### Comando único de mail
```
Generá el draft del mail Week NN
```

Claude:
1. Lee `Mail_WNN.html` (generado en Paso 5)
2. Extrae body entre `<!-- DRAFT_BODY_START -->` y `<!-- DRAFT_BODY_END -->`
3. Lee 15 destinatarios de `destinatarios.md`
4. Crea draft Gmail con:
   - `to`: federico.iglesias@pricetravel.com
   - `bcc`: 15 destinatarios
   - `subject`: "Supply Optimization · Week NN · Resumen + Plan de Acción"
5. Devuelve draft ID

Federico valida el draft en Gmail y lo envía manualmente.

### Commit summary format
```
feat: Week NN · RatesNoDispo + CheckRates + hub index · DD-MM-YYYY
```

### ZIP para commit
`build_package.py` genera `Price_WNN.zip` con estructura lista para descomprimir directo en la raíz del repo — sin prefijo de carpeta, sin mover archivos manualmente.

---

## 📌 Reglas Generales

- **Top 5** en Editorial · **Top 50** en Excel de Análisis
- Pestaña "Sin Conversión" SIEMPRE separada de "Bajo Rendimiento"
- Findings del Resumen Ejecutivo siempre con mayúscula inicial
- CUG y B2B-OP son prioridad estratégica (Weight 0.6)
- B2C no se elimina pero queda penalizado en ranking
- No mezclar benchmarks entre canales
- Links a Excel: nombre sin sufijo de week (`Analisis_Rates_NoDispo_7d.xlsx`) · la carpeta `week-NN/` ya identifica la semana
- **`index.html` nunca se edita manualmente** — siempre vía `build_package.py`
- Mantener consistencia metodológica entre semanas para que los deltas WoW sean válidos

---

## 📂 Nomenclatura estándar de archivos

### Datasets crudos (input)
```
Dataset_RatesNoDispo_WNN.xlsx
Dataset_CheckRates_WNN.xlsx
```

### Reportes editoriales (output público)
```
RatesNoDispo_Reporte_Editorial.html
CheckRates_Reporte_Editorial.html
```

### Excels de análisis (4 por reporte)
```
Analisis_Rates_NoDispo_7d.xlsx           (global · 33 pestañas)
Analisis_Rates_NoDispo_B2C_7d.xlsx       (8 pestañas)
Analisis_Rates_NoDispo_OP_7d.xlsx        (8 pestañas)
Analisis_Rates_NoDispo_CUG_7d.xlsx       (8 pestañas)

Analisis_Checkrates_7d.xlsx              (global · 37 pestañas)
Analisis_Checkrates_B2C_7d.xlsx          (9 pestañas)
Analisis_Checkrates_OP_7d.xlsx           (9 pestañas)
Analisis_Checkrates_CUG_7d.xlsx          (9 pestañas)
```

### Hub y ZIP
```
index.html         ← raíz del repo · generado por build_package.py
Price_WNN.zip      ← ZIP de release · estructura lista para commit
Mail_WNN.html      ← en _email/week-NN/
```

---

## 🎯 Cosas que NUNCA hay que hacer

1. **No reescribir templates HTML largos** · documentar cambios en `ESTRUCTURA_TEMPLATE.md` con snippets literales
2. **No hardcodear colores fuera de `:root`** salvo donde la guía lo permite (CUG `#4FC3F4`, IPM amber `#A86A1D`)
3. **No mezclar variables Python con displays** · `rpm` en Python sigue, "IPM" en displays
4. **No crear pestañas Excel sin el filtro Top 50** salvo Severity y agregados completos
5. **No combinar Bajo Rend con Sin Conversión en una pestaña**
6. **No olvidar el banner descarga al final de cada canasta**
7. **No editar `index.html` directamente** · siempre regenerar con `build_package.py`
8. **No commitear archivos sueltos** · usar el ZIP generado por `build_package.py`

---

## 📚 Memoria de bugs históricos resueltos

1. **CSS especificidad tabs** · `.tab-panel{display:none}` del CSS hero anulaba `:checked ~`. Fix: prefix `.tabs-block` + `!important`.
2. **Channel CR ConvRate filtros** · `Bookings>5` y `CR_Unicos>100` excluían channels Third Party. Fix: sin filtros en `TAB_EF/TAB_CV['channel']`.
3. **banda_rpm thresholds viejos** · `engine.py` tenía 1/2.5/4. Fix: $200/$650/$1500 USD/M.
4. **CSS `--amber` en CR** · estaba `#EA0074` (magenta RND). Fix: `#5C469C` (violet) en `asset_cr_head.html`.
5. **Sev_dict pandas Series vs dict** · `sum(sev_dict.values())` falla con Series. Fix: `int(sev_dict.sum()) if hasattr(sev_dict, "sum") else int(sum(sev_dict.values()))`.
6. **Merge conflict `index.html` publicado** · conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>>`) se publican como texto plano visible. Fix: sobreescribir con archivo limpio y hacer push directo. Ver `COMMIT_GUIDE.md`.
7. **Placeholders `{{}}` sin resolver en `index.html`** · al hacer `str_replace` quirúrgico. Fix: `build_package.py` genera el HTML completo sin placeholders — nunca editar a mano.
8. **`_WOW_NEUTRO` como string literal** en `_render_dim_table` en vez de variable. Fix: reemplazar strings literales por la variable.
9. **`g_channel_w17` no disponible** dentro de funciones de render porque `D` no era variable global. Fix: cargar explícitamente al nivel de módulo en `render_cr_p2.py`.
10. **`sin_conv` sin `Eficacia_WoW_pp`** · verificado — el enriquecimiento ocurre en render, el pickle no necesita cambiarse.
11. **`TAB_RPM` con `IPM=0`** — fix: `min_ipm=True` en `make_tab()`.
12. **Corps con tráfico <500K con NoDispo extrema** — fix: `MIN_T=500_000` en tabs de dimensión.
13. **`panel-header` 3 cols vs `panel-row` 4 cols** — desalineado visual. Fix: unificar a `1fr 62px 62px 46px`.
14. **CSS pintaba todos los nombres en magenta** · regla `.tab-panel div span:not(.tab-key)`. Fix: reemplazar por `.tab-panel div span.tab-val`.
15. **Métricas globales sobre `df18` completo** en lugar de P80. Fix: usar `p80_hotel` / `df18_p80`.
16. **`metrics_recalc.pkl` inexistente en `render_mail_v3.py`** · el archivo nunca existió en el pipeline normal. Fix: v3.2 deriva IPM y GBM directamente de `rnd_wNN_data.pkl` (`M['global_w18']['ipm']` y `M['global_w18']['gb_usd']`).
17. **Path hardcodeado en `excel_rnd.py`** · tenía `/home/claude/final_w18/rnd_w19_data.pkl`. Fix: ruta relativa `rnd_wNN_data.pkl`.
18. **ZIP del repo con prefijo `Price_WNN/`** · al descomprimir creaba subcarpeta en lugar de caer en raíz. Fix: `f.relative_to(ZIP_ROOT)` en lugar de `f.relative_to(ZIP_ROOT.parent)` en `build_package.py`.

---

## 📝 Cambios post W19 · Mayo 2026 (sesión fixes visuales)

### WoW con unidades claras (RND)
- `pp` en %NoDispo, `%` relativo en IPM — en p1, p2, p3
- Tabla Análisis por Dimensión: 2 cols WoW separadas (`%NoDispo · WoW · IPM · WoW`)
- CSS grid: `1fr 62px 36px 58px 36px`

### WoW ConvRate en tabla dim CR
- Orden: `CR únicos · BKGS · ConvRate · WoW · Eficacia · WoW`
- Helper `_fmt_wow_cv` (pp) en `render_cr_p2.py`

### Tab Hotel Conv Rate — solo Bookings > 0
- Sin Conversión excluida del card Conv Rate (tiene su propia tab)

### Plan de Acción con Carryover
- `template_seguimiento.py`: bloque HTML Carryover con badge gris + `desde WNN`
- `build_package.py`: genera `plan_seguimiento_WNN.md`
- ES/MP → OPEN (auto) · QW → PENDIENTE_QW (revisión manual)
- Aplica global + canastas CR y RND

### Semana dinámica en masthead
- `VOL_NUM`, `PERIODO`, `MES_AÑO` en pickle (`calc_cr.py` y `calc_rnd.py`)

### CONFIG SEMANAL para W20
Cambiar en `calc_cr.py`: `WEEK='W20'`, `PERIODO`, `MES_AÑO`, `VOL_NUM`, rutas datasets W20 y W19
Cambiar en `calc_rnd.py`: mismo patrón

---

## 📝 Cambios post W19 · Mayo 2026 (sesión inicial pipeline)

### Pipeline · Paso 6 nuevo: build_package.py
- Genera `index.html` del hub automáticamente desde los pickles (KPIs, WoW, bandas, severity counts)
- Genera `Price_WNN.zip` con estructura del repo lista para commit sin prefijo de carpeta
- Config semanal al tope del script: `WEEK`, `PERIODO`, `FECHA_PUB`, `WEEK_PREV`, `PERIODO_PREV`

### render_mail_v3.py · v3.2
- Eliminada dependencia de `metrics_recalc.pkl` (bug #16)
- CONFIG SEMANAL al tope del archivo
- Marcadores `<!-- DRAFT_BODY_START -->` / `<!-- DRAFT_BODY_END -->` para extracción automática del body
- IPM en lugar de RPM en el cuerpo del mail

### Incidencia dataset RND W19
- Primera versión llegó con 5 columnas (faltaban `CorpName`, `PaisDestino`, `Destino`, `gb_usd`)
- Resolución: solicitar dataset corregido antes de correr el pipeline
- **Regla permanente:** validar las 9 columnas del dataset RND antes de ejecutar `calc_rnd.py`

### destinatarios.md
- Son **15** destinatarios (el prompt anterior decía 14 por error)
- Archivo incorporado al proyecto Claude y al ZIP de proyecto

---

## 📝 Cambios post W18 · CR (sesión validación visual Mayo 2026)

### Orden de secciones globales CR
- **RE movido antes de alertas**: orden final → RE → Alertas → Severity → Hoteles → Dimensión → Plan

### Visual / UX
- Pills WoW neutras con `_WOW_NEUTRO` (bg `#F2EEE6` · color `#8A8377`)
- Channel hero 100% eficacia: pill verde `= 0,0`
- Color Third Party: cyan → violet en dimensión global y canastas
- WoW en Análisis por Hotel canasta (4 cols: Hotel · ConvRate · Eficacia · WoW)
- WoW en Channel dimensión global y canasta
- Normalización destinos con `_CITY_DASH_PATTERN` en `render_helpers.py`
- RE margin-top: 64px→24px global · 32px→16px canasta
- Fondos: `--paper-soft: #F2EDE0` · tabs-block `var(--paper)`

### Archivos modificados
`render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_helpers.py` · `template_resumen.py` · `template_alertas.py` · `asset_cr_head.html`

---

## 📝 Cambios post W18 · RND (sesión completa Mayo 2026)

### Pipeline RND · calc_rnd.py reescrito
- Lee Excel directamente (sin pickles pre-procesados)
- Requiere W(N) + W(N-1) para WoW real
- `gb_usd.clip(lower=0)` por fila — cancelaciones negativas no deprimen IPM
- P80 aplicado consistentemente en TODAS las dimensiones
- `MIN_T = 500_000` en tabs de dimensión — evita outliers de bajo volumen

### P80 aplicado consistentemente — CR y RND
| Componente | CR | RND |
|---|---|---|
| Métricas globales | `df18_p80` | `p80_hotel` |
| Tabs hero | `df18_p80` | `g_pais/dest/corp` sobre `df18_p80` |
| Canasta: métricas | `sub18_p80` | `sub18_p80` |
| Canasta: agg Corp/Dest/País | `agg_dim(sub18_p80, ...)` | `agg_dim(sub18_p80, ...)` |
| Channel | `df18` completo | N/A |

### Archivos modificados
`calc_rnd.py` · `calc_cr.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `asset_rnd_head.html`

---

**Última actualización:** Mayo 2026 · post W19 · build_package + hub pipeline · bugs #16 #17 #18 · destinatarios 15

## 📝 Cambios post W19 · Mayo 2026 (sesión fixes Excel + HTML)

### Excels CheckRates (CR)
- **Críticos** (global + canastas): sort explícito `sort_values('Eficacia', ascending=True)` — menor Eficacia primero
- **Por Corporativo** (global + canastas): agrega columna `Channels` con los canales únicos del corp via `hotel_channel_map`

### Excels Rates No Dispo (RND)
- **RPM → IPM (USD/M)**: todas las columnas de display renombradas — `.rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})`
- **Colores de banda IPM**: nuevo parámetro `banda_col2` en `add_table()` permite colorear dos columnas de banda por fila
- **Sin Conversión**: agrega `Font(..., color='8A8377')` en `BAND_FONTS` para color muted correcto

### Reportes HTML CR
- **Headers tab hotel**: `'Checkrates'` → `'CR Únicos'` · `'ConvRate'` → `'Conv Rate'` (global + canastas)
- **Headers tabla dim**: `'CR'` → `'CR Únicos'` · `'CV'` → `'Conv Rate'` (Corp + Dest + Channel, global + canastas)

### Bugs corregidos
| Bug | Archivo | Descripción |
|---|---|---|
| #28 | `excel_cr.py` | Sort Críticos sin `ascending=True` explícito |
| #29 | `excel_cr.py` | Por Corporativo sin columna Channel |
| #30 | `excel_rnd.py` | Columnas `RPM`/`BandaRPM` visibles en Excel |
| #31 | `excel_rnd.py` | Colores banda IPM no aplicaban (`banda_col2`) |
| #32 | `excel_rnd.py` | `Sin Conversión` sin color en `BAND_FONTS` |
| #33 | `render_cr_p2.py` | Header tab hotel `Checkrates`/`ConvRate` |
| #34 | `render_cr_p2.py` | Header tabla dim `CR`/`CV` |
| #35 | `render_cr_p3.py` | Header dim canastas `CR`/`CV` |
| #36 | `calc_rnd.py` | `ZeroDivisionError` cuando dataset W(N-1) vacío |

### Archivos modificados
`excel_cr.py` · `excel_rnd.py` · `render_cr_p2.py` · `render_cr_p3.py` · `calc_rnd.py`

---

**Última actualización:** Mayo 2026 · post W19 · fixes Excel IPM/CR Únicos/Corp Channel · bugs #28–#36

## 📝 Cambios post W19 · Mayo 2026 (sesión fixes visuales + estructura)

### Nomenclatura archivos corregida
- `assemble_cr.py` y `assemble_rnd.py`: output ahora genera `CheckRates_Reporte_Editorial.html` y `RatesNoDispo_Reporte_Editorial.html` (no `Supply_CheckRates_WNN.html`)
- `build_package.py`: lee los archivos con el nombre canónico correcto

### Estructura ZIP repo — `_governance/` completa
- `CHANGELOG.md` y `COMMIT_GUIDE.md` se incluyen en `_governance/` (no en raíz)
- `build_package.py` los agrega automáticamente al ZIP

### `build_package.py` — limpieza automática post-empaquetado
- Al finalizar el Paso 6, elimina todos los archivos intermedios de `/mnt/user-data/outputs/`
- Solo quedan los dos ZIPs: `Price_WNN.zip` (repo) y el ZIP del proyecto Claude
- **Regla de entrega:** presentar SOLO los dos ZIPs al final del pipeline — nunca archivos sueltos

### Fixes visuales CR — canastas (`render_cr_p3.py`)
- **Tabs KPI cards**: nombres de filas en negro (`color:var(--ink)`) — antes heredaban violet del CSS global
- **WoW ConvRate en tab Hotel card CV**: enriquece `df_hot_cv` con `g_hotel_w17` para calcular `ConvRate_WoW_pp`
- **Tabla dim nombres**: `font-weight:400` y `color:var(--ink)` — antes bold y violet (`asset_cr_head.html`)
- **Channel split PP/TP**: presente en canastas · color de nombres en negro (no violet)

### Fixes visuales RND — canastas (`asset_rnd_head.html`)
- Grid panel-row: `1fr 62px 34px 58px 34px` → `1fr 64px 38px 62px 38px`
- Gap: `6px` → `10px` — más espacio entre columnas

### Fixes visuales CR — tab hotel global (`render_cr_p2.py`)
- Anchos de columna reducidos: `Checkrates 80px→72px` · `ConvRate/Eficacia 65px→58px` · `WoW 44px→38px`
- Más espacio para el nombre del hotel

### Tabs canasta — efecto folder (`render_rnd_p3.py`, `render_cr_p3.py`)
- El `extra_css` de cada canasta ahora incluye el estilo base del `tab-label` (border, radius, margin-bottom:-1px)
- Antes los tabs de canasta no mostraban el efecto "folder activo" — ahora coinciden con el hero global

### Headers de columna CR — labels finales
- Tab hotel: `'Checkrates'` (no `'CR Únicos'`) y `'ConvRate'` (no `'Conv Rate'`) — versión corta para que entre en una línea
- Tabla dim: `'Checkrates'`, `'ConvRate'` — mismo criterio

### WoW sin unidad `pp` en pills de pestañas
- Las pills WoW en las pestañas de tabs muestran `+10,36` (sin `pp`) — más compacto
- El hero box WoW (recuadro grande W17/WoW/W18) conserva `pp` — tiene espacio suficiente
- Aplica en RND y CR, global y canastas

### Bugs corregidos
| Bug | Archivo | Descripción |
|---|---|---|
| #37 | `assemble_cr.py` | Nombre output `Supply_CheckRates_WNN.html` → `CheckRates_Reporte_Editorial.html` |
| #38 | `assemble_rnd.py` | Nombre output `Supply_RatesNoDispo_WNN.html` → `RatesNoDispo_Reporte_Editorial.html` |
| #39 | `build_package.py` | ZIP sin `CHANGELOG.md` y `COMMIT_GUIDE.md` en `_governance/` |
| #40 | `build_package.py` | Archivos intermedios sueltos en outputs tras pipeline — fix: limpieza automática |
| #41 | `render_cr_p3.py` | Nombres en violet en tabs KPI canasta — fix: `color:var(--ink)` explícito |
| #42 | `render_cr_p3.py` | WoW ConvRate faltaba en tab Hotel del card CV canasta |
| #43 | `asset_cr_head.html` | `.panel-row .label` bold y violet — fix: `font-weight:400;color:var(--ink)` |
| #44 | `render_rnd_p3.py` `render_cr_p3.py` | Tabs canasta sin efecto folder — fix: CSS base `tab-label` en `extra_css` |
| #45 | `render_cr_p2.py` | Columnas tab hotel muy anchas — fix: anchos reducidos |
| #46 | todos los render | Pills WoW con `pp` en pestañas — fix: quitar `pp` solo en pills, mantener en hero box |

### Archivos modificados
`assemble_cr.py` · `assemble_rnd.py` · `build_package.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `render_rnd_p1.py` · `render_cr_p1.py` · `asset_cr_head.html` · `asset_rnd_head.html`

---

**Última actualización:** Mayo 2026 · post W19 · fixes visuales canastas + nomenclatura + WoW pills + build_package limpieza · bugs #37–#46

---

## 📝 Cambios post W19 · Mayo 2026 (sesión verificación integridad W20)

### Audits + Documentación nueva
- `audit_w20.md` — Verificación integridad proyecto · detecta inconsistencias config
- `READY_W20.md` — Checklist pre-flight W20 · config semanal paso a paso

### Limpieza proyecto Claude
- ❌ Eliminado `_TEMPLATE_Hub.html` del proyecto Claude — vive SOLO en GitHub bajo `_template/`
- Proyecto ahora tiene **46 archivos** (limpio · sin archivos obsoletos)

### Status pre-W20
- ✅ Pipeline completamente funcional (6 pasos)
- ✅ Config semanal lista (5 variables en 4 scripts)
- ✅ Documentación consolidada
- ✅ Decisiones de bandas + colores sin cambios respecto a W19

---

**Última actualización:** Mayo 2026 · post W19 · audits W20 + limpieza proyecto

---

## 🐛 FIX #47 · calc_cr.py · Inconsistencia CONFIG WEEK

**Problema detectado (11 mayo 2026):**
- `calc_cr.py` línea 12 decía: `WEEK = 'W18'`
- Pero línea 33-34 leía: `Dataset_CheckRates_W19.xlsx` + W18
- Y línea 378 generaba: `cr_w19_data.pkl`
- Y línea 381 printaba: `cr_w18_data.pkl` (confuso)

**Mismatch:** CONFIG decía W18, pero datasets y output eran W19 (confusión operativa)

**Solución aplicada (11 mayo 2026):**
```python
# Línea 12: Cambiar de
WEEK = 'W18'

# A:
WEEK = 'W19'

# Línea 381: Cambiar de
print(f"✅ Pickle guardado: cr_w18_data.pkl")

# A:
print(f"✅ Pickle guardado: cr_w19_data.pkl")
```

**Status:** ✅ APLICADO · calc_cr.py ahora alineado con datasets W19

**Impacto:** Pipeline W19 funcional · W20 tendrá CONFIG correcta desde inicio

---

**Última actualización:** Mayo 2026 · FIX #47 aplicado · calc_cr.py CONFIG alineado

---

## 📝 Módulo Histórico CR · Evolución Histórica (Mayo 2026 · post W20)

### Qué se agregó
Módulo **"Evolución Histórica"** reactivo en todas las cards KPI del reporte CheckRates:
- **2 cards globales** (Hero · Eficacia + ConvRate) — `render_cr_p1.py`
- **6 cards canasta** (B2B-OP · CUG · B2C × Eficacia + ConvRate) — `render_cr_p3.py`

### Posición en el DOM de cada card
```
valor grande → pill banda → gauge 5 niveles → wow_box → tabs (10 elementos) → [MÓDULO]
```

### Funcionalidad
- **Estado default:** datos globales de la card visibles sin interacción
- **Click en elemento** (destino / corp / hotel / channel): canvas + 5 métricas + banda se actualizan
- Elemento seleccionado queda highlighted con `var(--accent-soft)`
- **Curva (Canvas):** escala LOCAL del elemento — muestra el trend exacto W14-W21
- **Barras (Sparkline):** escala GLOBAL vs target de la card — muestra severidad relativa al objetivo
- Datos W14-W20 ficticios · W21 real del pickle · W20 del elemento desde `Eficacia_W17` / `ConvRate_W17`

### Colores
Usa exclusivamente variables CSS del sistema (`var(--paper)`, `var(--accent)`, etc.) + colores exactos de `_BANDA_COLORS` en `render_helpers.py`. Súper Crítica: badge negro/blanco, footer texto oscuro (`#161616`).

### Archivos modificados
| Archivo | Cambio |
|---|---|
| `historico_module_v2.py` | **NUEVO** · función `render_historico_cr()` · módulo completo |
| `render_cr_p1.py` | Import + llamada en `render_kpi_card_eficacia` y `render_kpi_card_convrate` · rows con `data-hist-*` |
| `render_cr_p3.py` | Import + llamada en `kpi_card_canasta` · `tab_rows_canasta` con `data-hist-*` |

### Pendiente (próximas sesiones)
- Módulo histórico en secciones Análisis por Hotel y Análisis por Dimensión (CR)
- Módulo histórico en RND (misma arquitectura)
- Datos históricos reales W14-W20 cuando estén disponibles en pickle (reemplazar `_FICTICIOS`)

19. **Labels canvas ilegibles en módulo histórico CR** · `rgba(100,90,80,0.55)` y `font-size:7px` → Fix: `0.80` y `8px`. Archivo: `historico_module_cr.py`.
20. **Curva plana en módulo histórico CR** · fixtures con variación insuficiente → Fix: nuevos valores con delta realista entre semanas. Archivo: `historico_module_cr.py`.
21. **`W14`/`W21` hardcodeados en footer sparkline** · mostraba siempre W14-W21 sin importar `current_week` → Fix: `{semanas[0]}` / `{semanas[-1]}` dinámicos. Aplica en `historico_module_cr.py` y `historico_module_rnd.py`.

---
---

## 📝 Módulo Histórico CR · Evolución Histórica (Mayo 2026 · post W20 · sesión 1)

### Qué se agregó
Módulo **"Evolución Histórica"** reactivo en todas las cards KPI del reporte CheckRates:
- **2 cards globales** (Hero · Eficacia + ConvRate) — `render_cr_p1.py`
- **6 cards canasta** (B2B-OP · CUG · B2C × Eficacia + ConvRate) — `render_cr_p3.py`

### Posición en el DOM de cada card
```
valor grande → pill banda → gauge 5 niveles → wow_box → tabs (10 elementos) → [MÓDULO]
```

### Funcionalidad
- **Estado default:** datos globales visibles sin interacción
- **Click en elemento:** canvas + 5 métricas + banda se actualizan con datos del elemento
- **Curva (Canvas):** escala LOCAL del elemento — trend exacto W14-W21
- **Barras (Sparkline):** escala GLOBAL vs target — severidad relativa al objetivo
- Datos W14-W20 ficticios · W21 real del pickle · W20 desde `Eficacia_W17` / `ConvRate_W17`
- Título: "Evolución Histórica" (genérico, no limita a 8W)

### Archivos modificados
| Archivo | Cambio |
|---|---|
| `historico_module_v2.py` | **NUEVO** · función `render_historico_cr()` |
| `render_cr_p1.py` | Import + llamada en ambas cards globales · rows con `data-hist-*` incluyendo Channel |
| `render_cr_p3.py` | Import + llamada en `kpi_card_canasta` · `tab_rows_canasta` con `data-hist-*` |

---

## 📝 Módulo Histórico RND + Fixes CR (Mayo 2026 · post W20 · sesión 2)

### Módulo Histórico RND — `historico_module_rnd.py`

**NoDispo** (escala invertida — menor = mejor):
- Accent: `#EA0074` magenta · Target: `< 5%`
- Curva: eje Y invertido · zona relleno arriba de la curva (zona mala)
- Sparkline: barra más alta = más NoDispo = peor
- Métricas: "Mín 8W" verde · "Máx 8W" rojo

**IPM** (escala normal — mayor = mejor):
- Accent: `#A86A1D` amber · Target: `≥ $650`
- W20 del elemento desde columna `IPM_W18` del pickle
- Métricas: "Máx 8W" verde · "Mín 8W" rojo

**Cobertura:** 8 cards — 2 globales + 6 canastas

### Fixes CR aplicados
- **Channel tab clickeable**: `chan_row` y `chan_row_cv` con `data-hist-*`
- **Badge Súper Crítica dinámico**: `bbEl.style.color = bc.fg` en JS
- **Canvas = sparkline ancho**: `pR=10` · label target en HTML

### Archivos nuevos/modificados
| Archivo | Cambio |
|---|---|
| `historico_module_rnd.py` | **NUEVO** · módulo histórico RND completo |
| `render_rnd_p1.py` | Import + data-hist-* + módulo en ambas cards globales |
| `render_rnd_p3.py` | Import + data-hist-* en tab_rows_canasta + módulo en kpi_card_canasta |
| `render_cr_p1.py` | Channel clickeable (chan_row + chan_row_cv) |
| `historico_module_v2.py` | Fix JS badge Súper Crítica dinámico |

### Pendientes para W21+
- Fix color badge Súper Crítica en RND
- Ajustes spacing: tabs-row margin-top · módulo margin-top
- Módulo histórico en Análisis por Hotel y Dimensión (CR + RND)
- Datos históricos reales W14-W20 en pickle (reemplazar `_FICTICIOS`)

---

**Última actualización:** Mayo 2026 · post W20 · Fixes módulos históricos CR+RND · bugs #72–#75 · sparkline footer dinámico · regla `current_week`
