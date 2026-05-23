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
| `COMMIT_GUIDE.md` | En `_docs/` · workflow de commit semanal |

> ⚠️ **Eliminado en W20 sesión 4:** las guías editoriales HTML (`GUIA_EDITORIAL_*.html`) y los templates (`_TEMPLATE_*.html`) eran legado — los reportes se generan 100% en runtime desde los scripts `render_*.py`. Si hay que revisar el HTML/CSS de algún componente, leer directamente el código del render correspondiente.

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
| `render_helpers.py` | Format español, clean_hotel_name, truncate, banda_pill, `_CITY_DASH_PATTERN`, `wow_pill_html`, `searchbox_pill_html`, `searchbox_header_html`, `mini_badge`, `target_caption` |
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
├── _docs/                       (NO se publica · docs internas · README, CHANGELOG, BANDAS, PROMPT_MAESTRO, COMMIT_GUIDE, etc.)
├── _seguimiento/                (carryover semanal de plan_seguimiento_WNN.md)
├── rates-nodispo/
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx       (global · 33 pestañas)
│       ├── Analisis_Rates_NoDispo_B2C_7d.xlsx   (8 pestañas)
│       ├── Analisis_Rates_NoDispo_OP_7d.xlsx    (8 pestañas)
│       ├── Analisis_Rates_NoDispo_CUG_7d.xlsx   (8 pestañas)
│       └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/
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

### Ventana histórica: 5 semanas reales (post W20 sesión 6)

Los datos históricos viven en `_scripts/historico_data.py` con valores reales W16-W20 extraídos de los pickles. El parámetro `current_week` de los módulos ya no se usa (deprecated): la ventana viene fija desde `SEMANAS = ['W16', 'W17', 'W18', 'W19', 'W20']`.

**val_actual ahora es la semana ACTUAL** del reporte (W20), no la próxima. El módulo agrega ese valor al final de la serie histórica automáticamente.

**Plan de extensión a 8 semanas reales** (~3 semanas):

| Semana actual | Acción | Ventana |
|---|---|---|
| W21 | Editar `HIST_DATA` agregando valor W20 + renombrar `SEMANAS` | 6 semanas |
| W22 | Idem agregando W21 | 7 semanas |
| W23 | Idem agregando W22 → **alcanza 8 reales** · fijar como ventana móvil | 8 semanas |
| W24+ | Ventana móvil: descartar la más antigua + agregar la nueva | 8 reales |

**Util pendiente:** `extract_hist_data.py` para automatizar el append desde los pickles.

### Componentes del módulo

1. **Canvas** — curva escala LOCAL + target line + labels X dinámicos ({semanas[0]}, {semanas[-1]})
2. **5 métricas** — Actual · Máx 5W · Mín 5W · Prom 5W · Banda
3. **Sparkline** — N barras (= len(SEMANAS)) escala GLOBAL vs target
4. **Interactividad** — click en fila actualiza canvas + métricas + banda

### Pendientes

- Util `extract_hist_data.py` para automatizar la actualización semanal del histórico
- Cuando llegue W23: revisión visual de la curva con 8 semanas reales

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
03 · Análisis por hotel (bloque con 4 tabs: Demanda NC · Bajo Rendimiento · Sin Conversión · Críticos)
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
- Pills Súper Crítica: `background: #A32D2D` · texto `#FCEBEB` (rojo oscuro · no negro opaco)
- Accent IPM en módulos históricos RND: `#4FC3F4` (Arctic Blue corporativo) — único uso de cyan
- Accent NoDispo en módulos históricos RND: `#EA0074` (magenta)
- **Exitosa:** `#085041` verde teal en TODO el sistema — barras, pills, gauge, `--green` CSS
- **Gauge 5 niveles:** todas las barras `height:6px · opacity:1` — uniforme, sin transparencia
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
22. **IPM accent `#A86A1D` reemplazado por `#7C2D12`** en fix de paleta global → afectaba `ACCENT_HEX` de módulos IPM en HTML. Fix: reemplazo quirúrgico por `#4FC3F4` solo en contexto IPM.
23. **No había forma de volver a Global** en módulo histórico tras seleccionar elemento → Fix: label "Global" clickeable + click en fila activa hace toggle/reset.
24. **Módulos históricos clonados sin listeners** — los módulos `hrnd-hotel-nd/ipm` y `hrnd-dim-nd/ipm` eran copias del global generado antes de que se agregaran `hist-update`/`hist-reset`. Fix: listeners inyectados directamente en los 4 módulos del HTML.
25. **`data-hist-nd="0.0"` en todas las filas** — la extracción de %NoDispo e IPM del HTML renderizado no matcheaba el patrón de spans. Fix: regex actualizado para extraer valores reales de cada fila.
26. **Exitosa turquesa `#4FC3F4` en severity** — la variable `--green:#4FC3F4` en el CSS head + colores hardcodeados en barras de progreso y pills. Fix: `--green:#085041` + replace de `#4FC3F4` en barras/pills de Exitosa. El cyan queda solo para CUG y IPM accent en RND.
27. **Gauge grosor inconsistente** — iteraciones con `height:3px/4px/8px` generaban barras desproporcionadas. Fix definitivo: todas las barras `height:6px · opacity:1` — mismo grosor, colores sólidos puros. → Fix: label "Global" clickeable + click en fila activa hace toggle/reset. · mostraba siempre W14-W21 sin importar `current_week` → Fix: `{semanas[0]}` / `{semanas[-1]}` dinámicos. Aplica en `historico_module_cr.py` y `historico_module_rnd.py`.

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

## 📝 Cambios post W20 · Mayo 2026 (sesión 3 · Fixes visuales módulos históricos + colores severity)

### Sistema de colores severity — correcciones definitivas

**Exitosa:** `#4FC3F4` (cyan) → `#085041` (verde teal) en todos los contextos:
- Barras de progreso del severity principal
- Pills de banda Exitosa
- Variable CSS `--green: #4FC3F4` → `--green: #085041` en `asset_cr_head.html` y `asset_rnd_head.html`
- Gauge de 5 niveles en `render_helpers.py` (4 ocurrencias)
- `template_severity.py` para tablas Severity (5 ocurrencias)
- `historico_module_v2.py` `_BANDA_COLORS` dict

**Súper Crítica:** `#161616` (negro) → `#A32D2D` (rojo oscuro) en pills (no en barras del gauge, que siguen negras).

**Gauge de 5 niveles:** todas las barras `height:6px · opacity:1` — mismo grosor, colores sólidos puros, sin transparencia. La banda activa se identifica por la pill encima, no por el gauge.

### Cyan `#4FC3F4` queda SOLO en 2 lugares válidos
1. `IPM_ACCENT` en `historico_module_rnd.py` (Arctic Blue corporativo, accent visual IPM)
2. Label "🔌 Third Party" en `render_cr_p1.py` líneas 197, 338 (color identitario Third Party CR)

### Módulos históricos Análisis por Hotel y Dimensión (RND)
- Resuelto problema de listeners faltantes: los módulos clonados `hrnd-hotel-nd/ipm` y `hrnd-dim-nd/ipm` ahora escuchan eventos `hist-update` y `hist-reset` correctamente
- Click en fila actualiza canvas + métricas + banda
- Click en label "Global" vuelve a vista por defecto

### Archivos modificados
`render_helpers.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `historico_module_v2.py` · `historico_module_rnd.py` · `template_severity.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `snippet_alertas_canasta.html` · `snippet_alertas_canasta_rnd.html`

### Pendientes que quedaron al cierre
- Módulo histórico en secciones Análisis por Hotel y Dimensión (CR) — pendiente desde W20 (cerrado en sesión 4)
- Datos históricos reales W14-W20 en pickle (siguen ficticios)

---

## 📝 Cambios post W20 · Mayo 2026 (sesión 4 · Módulo histórico CR hotel/dim + Reformulación badges Opción D)

### Feature 1 · Módulo histórico CR en Análisis por hotel + Análisis por dimensión

Pendiente cerrado: portar el módulo histórico de RND a las dos secciones equivalentes en CR.

**Implementación:**
- Nueva función `render_historico_seccion_cr(canvas_id_ef, canvas_id_cv, banda_ef, val_ef, banda_cv, val_cv)` en `render_cr_p2.py` (análoga a `render_historico_seccion_rnd`)
- Listeners `hist-update` / `hist-reset` agregados a `historico_module_v2.py` para que el módulo CR pueda ser controlado desde wrappers externos (backward-compatible con el listener interno de `.kpi-card` de Hero/canastas)
- Parámetro opcional `with_hist=True` en `render_top_table_cr` y `_render_dim_table`: enriquece filas con `data-hist-w21/w20/cv-w21/cv-w20/label` + `cursor:pointer`
- Integración en `render_bloque_hoteles_cr` y `render_bloque_dimensiones_cr` con canvas IDs `hcr-hotel-ef/cv` y `hcr-dim-ef/cv`

**UX:** click en fila de tabla → ambos módulos (Ef + CV) se actualizan en sincronía. Re-click → reset a Global. Aislamiento: clicks en sección NO afectan cards hero y viceversa.

### Feature 2 · Reformulación badges severity (Opción D + paleta D)

Cierre del cambio que se había perdido en un revert. **Estilo Opción D** aplicado uniformemente a TODOS los badges del sistema:

```css
font-size: 13px              (canastas: 11px)
font-weight: 700
letter-spacing: .04em
text-transform: uppercase
padding: 10px 22px
border-radius: 3px
border: 1px solid {bd}
text-align: center
```

**Texto del badge:** solo nombre de banda en mayúsculas. **El "Target X%" ya NO va dentro del badge** — se renderiza como caption gris separado debajo, mediante nueva función helper `target_caption(target_text, font_size='11px')` en `render_helpers.py`.

**Función `banda_pill()` refactor:** el parámetro `target` se mantiene en la firma por compatibilidad pero se ignora (el target ahora se inyecta vía `target_caption()` por separado).

**Módulo histórico CR:** además del estilo Opción D, se quitó:
- La palabra "Banda" como label arriba del badge en la box principal
- El prefijo "Banda: " del footer (ahora dice solo `EXITOSA`, `REVISAR`, etc. en mayúsculas)

El módulo histórico RND ya estaba correcto desde sesión 2 — no requirió cambios en este barrido.

### Bugs corregidos
| Bug | Archivo(s) | Descripción |
|---|---|---|
| #81 | `render_helpers.py` | `banda_pill()` rediseñada · estilo Opción D · padding 10px 22px · font 13px · text-align center |
| #82 | `render_helpers.py` | Nueva función `target_caption()` para mostrar target separado del badge |
| #83 | `render_cr_p1.py`, `render_rnd_p1.py`, `render_cr_p3.py`, `render_rnd_p3.py` | Hero + canastas usan `pill_with_target` (pill + caption) en lugar de pill con target embebido |
| #84 | `historico_module_v2.py` | Quitar label "Banda" arriba del badge en módulo histórico CR |
| #85 | `historico_module_v2.py` | Footer del módulo histórico CR: quitar prefijo "Banda: " · mostrar solo nombre en mayúsculas |
| #86 | `historico_module_v2.py` JS | `updateMetrics()`: `el.textContent = banda.toUpperCase()` en lugar de `'Banda: ' + banda` |
| #87 | `render_helpers.py` `gauge_5levels` | Exitosa cyan `#4FC3F4` → verde teal `#085041` en 4 variantes (nodispo, rpm, eficacia, convrate) |
| #88 | `render_cr_p2.py` | Exitosa cyan → verde en 3 lugares (severity gauges) + fallback `#E8F7FD` → `#E1F5EE` |
| #89 | `render_rnd_p2.py` | Exitosa cyan → verde en 4 lugares (severity gauges + tablas dim) |
| #90 | `render_rnd_p3.py` | COLORS canastas Exitosa cyan → verde |
| #91 | `template_severity.py` | Exitosa bg/fg cyan → verde teal en 5 lugares |
| #92 | `asset_cr_head.html`, `asset_rnd_head.html` | Var CSS `--green` y `--green-soft` cyan → verde · `exec-mini-card.qw` border cyan → verde |
| #93 | `snippet_alertas_canasta*.html` (+ duplicados en `snippets/`) | `border-top:3px solid` cyan → verde |

### Archivos modificados
`render_helpers.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `historico_module_v2.py` · `template_severity.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `snippet_alertas_canasta.html` · `snippet_alertas_canasta_rnd.html` · `snippets/snippet_alertas_canasta*.html` (duplicados)

### Documentación actualizada
`_docs/BANDAS.md` (reescrito completo con paleta D + estilo Opción D + thresholds + cyan excepciones)

### Pendientes que quedan abiertos
- ~~Decisión sobre `_docs/CHANGELOG.md` duplicado~~ (resuelto W20s4: `_governance/` eliminado, canon vive en `_docs/CHANGELOG.md`)
- Validación visual final del reporte CR W20 regenerado con badges Opción D
- Regenerar reporte RND W20 con los mismos cambios
- Datos históricos reales W14-W20 en pickle (reemplazar `_FICTICIOS`)
- Restaurar search box (tarea conocida desde sesiones huérfanas)

---

**Última actualización:** Mayo 2026 · post W20 sesión 4 · módulo histórico CR hotel+dim + Opción D badges + paleta D Exitosa verde + sin "Banda" label + target caption separado · bugs #81–#93

---

## 📝 Cambios post W20 · Mayo 2026 (sesión 5 · Tab Críticos RND + Searchbox cobertura completa)

### Tab "Críticos" en Análisis por hotel RND (4ª óptica)

La sección Análisis por hotel RND tenía solo 3 tabs (Demanda NC · Bajo Rendimiento · Sin Conversión). Faltaba la 4ª óptica: **hoteles con `BandaNoDispo` en Crítica o Súper Crítica** (`%NoDispo > 20%`).

**Implementación:**
- `_scripts/asset_rnd_head.html`: agregado `tab-h-crit` al CSS (selectores de visibilidad de panel y tab activo).
- `_scripts/render_rnd_p2.py`:
  - Bloque `cols_crit` + `df_crit_all` filtrando `p80_hotel` por `BandaNoDispo ∈ ['Crítica','Súper Crítica']`, sorted desc por `%NoDispo`, top 50.
  - Input `<input id="tab-h-crit">` + label `<label for="tab-h-crit">Críticos</label>` agregados al bloque de tabs.
  - Panel `crit` agregado al string `panels`.
  - Subtítulo de sección: "3 ópticas analíticas" → **"4 ópticas analíticas"**.

**Resultado validado W20:** 358 hoteles del P80 (337 Crítica + 21 Súper Crítica). Top 1: Grand Hyatt Istanbul 93.22%.

### Searchbox cliente-side · cobertura completa

El searchbox ya existía como helper en `render_helpers.py` + JS auto-attach en assets head. Esta sesión cerró el último gap: el filtrado en las **canastas colapsables**.

**Cambios:**
- `_scripts/render_cr_p3.py` y `render_rnd_p3.py`:
  - Filas `panel-row` enriquecidas con `data-hist-label="{label}"`
  - Bloques hotel/dim de cada canasta: `id="canasta-{idx_str}-{hotel|dim}-{cr|rnd}"` + `searchbox_html(...)`

**Cobertura final: 18 searchboxes (9 por reporte):**
- Hero KPI cards
- Análisis por hotel
- Análisis por dimensión
- Canastas B2C/OP/CUG × hotel+dim (6)

**Comportamiento:**
- Filtrado **instantáneo** cliente-side
- **Case-insensitive y sin acentos** (NFD normalize)
- **Contador** dinámico: `"X de Y visibles"` al filtrar
- Color focus por reporte: magenta RND, violet CR
- Búsqueda solo en **primera columna** (`data-hist-label`)

### Bugs reportados verificados

Auditoría completa con playwright:

| Bug reportado | Diagnóstico |
|---|---|
| `Uncaught SyntaxError: Unexpected token 'else'` × 6 | **Falso positivo** — ya resuelto en commits previos (0 errores JS verificados) |
| Severity cards con transparencia | **Falso positivo** — paleta D con colores sólidos |
| Módulos históricos no aparecen en RND | **Falso positivo** — 8 módulos funcionando |
| Severity canastas sin paleta D | **Falso positivo** — paleta D aplicada |
| Tab Críticos faltante en Análisis por hotel RND | **REAL** — corregido |

### Archivos modificados
`_scripts/asset_rnd_head.html` · `_scripts/render_rnd_p2.py` · `_scripts/render_cr_p3.py` · `_scripts/render_rnd_p3.py` · `rates-nodispo/week-20/RatesNoDispo_Reporte_Editorial.html` · `checkrates/week-20/CheckRates_Reporte_Editorial.html`

### Commits
- `05bd9c7` · fix(rnd): agregar tab Críticos en Análisis por hotel (4ª óptica)
- `86a9bef` · feat(canastas): searchbox en Análisis por hotel + dim de cada canasta CR/RND

### Pendientes
- Datos históricos reales W14-W20 en pickle (hoy `_FICTICIOS`)
- Persistencia de filtro searchbox entre tabs (decisión pendiente)
- Validar pipeline completo con datasets W21 cuando llegue la semana

---

---

## 📝 Cambios post W20 · Mayo 2026 (sesión 6 · Histórico real W16-W20 + Limpieza legacy)

### Histórico real W16-W20 reemplaza `_FICTICIOS`

Generados pickles W16-W20 desde datasets reales y extraídos KPIs globales a `_scripts/historico_data.py`.

**Adapter para W16/W17 RND** (estructura distinta):
- W16/W17: 4 sheets (`Canasta ALL` + B2C + OP + UOP) → usar `Canasta ALL`
- W17 bug: columna `html` mal nombrada → renombrar a `CorpName`
- W18+: 1 sheet `Sheet1`

**Nuevo módulo `historico_data.py`:**
```python
HIST_DATA = {
    'cr':  {'eficacia':{...}, 'convrate':{...}},
    'rnd': {'nodispo':{...},  'ipm':{...}}
}
SEMANAS = ['W16', 'W17', 'W18', 'W19', 'W20']

def get_serie(reporte, metrica, scope, val_actual):
    """Devuelve serie [W16..val_actual] desde HIST_DATA + W{current}."""
```

**Cambios en módulos históricos:**
- `historico_module_v2.py` (CR) y `historico_module_rnd.py` (RND): eliminado dict `_FICTICIOS`, importan `get_serie` y `SEMANAS`
- Ventana: 8 semanas (W14-W21) → **5 semanas reales (W16-W20)**
- Cambio conceptual: `val_actual` es la semana ACTUAL del reporte, NO la próxima
- Labels: `8W` → `5W` (Máx, Mín, Prom)
- Footer eje X dinámico: `{semanas[0]}` / `{semanas[-1]}`

**Decisión: ventana de 5 semanas reales (Opción A)** — datos auditables > más puntos. Plan de evolución natural a 8 reales en ~3 semanas (W23).

### Limpieza legacy: `_scripts/{lib,snippets,templates}/` (-1522 líneas)

Eliminados archivos del pipeline anterior no usados por código vivo:
- `_scripts/lib/` (5 archivos) · `_scripts/snippets/` (4 duplicados) · `_scripts/snippet_*.html` (4 en raíz) · `_scripts/templates/mail_template.html`

Estado final `_scripts/`: **44 archivos** (antes 58).

### ZIP del proyecto Claude · `proyecto_claude_W20.zip`

Empaquetado limpio para reemplazar el proyecto en claude.ai:
- 259 KB · 51 archivos
- `_docs/` (7 .md) + `_scripts/` (43) + `destinatarios.md`
- Sin HTMLs generados, sin pickles, sin datasets, sin __pycache__

### Datos reales W16-W20 visibles

| Métrica | W16 | W17 | W18 | W19 | W20 |
|---|---|---|---|---|---|
| CR Eficacia global | 93.27% | 93.58% | 93.71% | 93.30% | 92.75% |
| CR ConvRate global | 1.29% | 1.15% | 1.02% | 1.14% | 1.19% |
| RND %NoDispo global | 3.69% | 3.63% | 2.84% | 2.31% | 2.81% |
| RND IPM global | $661 | $574 | $524 | $499 | $1.097 |

### Commits sesión 6

- `c2c1226` · feat(w20s6): histórico real W16-W20 reemplaza `_FICTICIOS`
- `abc031a` · refactor(w20s6): eliminar legacy `_scripts/{lib,snippets,templates}/`

### Pendientes

- Util `extract_hist_data.py` para automatizar la actualización del histórico
- Auditar el salto IPM W19→W20 ($499→$1097) — ¿real o ruido?
- Revocar PAT GitHub al final de las sesiones

---

**Última actualización:** Mayo 2026 · post W20 sesión 6 · Histórico real W16-W20 + ventana 5W + cleanup legacy

---

## 📝 Cambios post W20 · Mayo 2026 (sesiones 7–13 · UI/UX completo + Searchbox + Top 100)

### Resumen de sesiones

| Sesión | Commits | Cambio principal |
|---|---|---|
| s7 | `0116d4e`, `3d0eb7a` | UI minimalista inicial, autocomplete, severity |
| s8 | `41fcdef` | Rediseño completo: footer fuera, RE/Plan compactos, badge al lado |
| s9 | `0645a93` | Searchbox dentro de cards + Top 100 en DOM |
| s10 | `a1e52f7`, `7e6f2c5` | Gauge paleta D, severity paleta D, cards menos altas, canastas interactivas, banners Excel |
| s11 | `9d7cfa1` | Top 100 hotel/dim global+canastas, searchbox canastas, estilos 11px, badges paleta D |
| s12 | `5e27145` | RND tabs ancho, click canasta CR, cards más compactas, label hist muted, search limpia al cambiar tab |
| s13 | `3e5ebd2` | Cross-tab search correcto, severity RND paleta D, top 100 RND hotel/dim, canastas RND interactivas |

### Cards KPI hero — estructura final

3 secciones visuales dentro del mismo contenedor:
1. **KPI + gauge + badge/WoW**: valor 40px + badge paleta D + gauge 6px + wow_box compacto
2. **Searchbox + pestañas**: `sb-input` inline debajo de las tabs; 10 visibles / 90 sb-hidden
3. **Evolución Histórica**: módulo `historico_module_v2/rnd` reactivo

Sizing: `font-size:40px` hero / `36px` canastas · `padding:12px 16px` card.

### Searchbox — reglas de funcionamiento final

- **Solo tab activo**: `getActiveRows()` usa `getComputedStyle(panel).display !== 'none'`
- **Top 100 en DOM**: `data-row-idx` en cada fila; primeras 10 sin `sb-hidden`
- **Al cambiar tab**: el searchbox se limpia (listener `change` en radios)
- **Sin dropdown**: filtrado inline únicamente
- **Cross-tab**: el JS opera solo sobre el panel CSS-visible

### Layout tablas hotel y dimensión

```
Col izq: filas 1-5 + su header
Col der: filas 6-10 (visibles) + filas 11-100 (sb-hidden)
Al buscar → gridTemplateColumns:1fr (lista única)
```

### Severity RND — estado correcto

`render_rnd_p2.py render_severities_combinadas` usa el dict `BADGE_COLORS` con:
- `Súper Crítica: bg=#A32D2D, fg=#FCEBEB` (sólida)
- Resto: bg pastel / fg texto oscuro (conforme BANDAS.md)

### Análisis por tipo de producto

**Eliminado de PART2 CR** (`CHAN_AGR` removido de `PART2`). La función `render_channel_agrupado()` existe pero no se incluye en el ensamblado.

### Bugs pendientes para W21

| # | Descripción |
|---|---|
| P1 | Canastas RND: eje X histórico muestra "undefined" |
| P2 | Canasta CR dim: click no siempre actualiza histórico |
| P3 | Cards KPI canasta: filas de tab sin header por columna |
| P4 | `BANDA_COLORS` puede no estar disponible en `render_rnd_p3.py` |
| P5 | `extract_hist_data.py` pendiente |

### Archivos modificados en sesiones 7–13 (completo)

```
_scripts/calc_cr.py              TOP → head(100) para todos los pools
_scripts/calc_rnd.py             TOP → head(100) + corps/destinos/paises → 100
_scripts/render_cr_p1.py         Card layout 3 secciones, sb-input, font 40px, <span> accent
_scripts/render_cr_p2.py         render_top_table_cr + _render_panel + _render_dim_table actualizados
_scripts/render_cr_p3.py         tab_panel_hotel/dim 2 cols, searchbox, listener hist, render_historico_seccion_cr local
_scripts/render_rnd_p1.py        Card layout 3 secciones, sb-input, font 40px
_scripts/render_rnd_p2.py        render_top_table + _render_panel + _render_dim_table_rnd + severity paleta D
_scripts/render_rnd_p3.py        tab_panel_hotel 2 cols+badge+corp, listener hist, render_historico_seccion_rnd local
_scripts/historico_module_v2.py  Label "Global" → var(--ink-muted)
_scripts/historico_module_rnd.py Label "Global" → var(--ink-muted)
_scripts/render_helpers.py       gauge_5levels: height 6px, opacity 1, sin labels, sin Conversión #8A8377
_scripts/template_resumen.py     <strong> → <span> en titulo de finding
_scripts/template_severity.py    render_severity_row paleta D canónica
_scripts/asset_cr_head.html      display:block tabs activos, getActiveRows, clear-on-change, kpi-card box-sizing
_scripts/asset_rnd_head.html     display:block tabs activos (era grid 1fr 1fr), getActiveRows, idem
```

---

**Última actualización:** Mayo 2026 · post W20 sesiones 7-13 · commits s7→s13 · UI/UX + Searchbox + Histórico completo


---

## 📝 Cambios post W20 · Mayo 2026 (sesiones 14-15 · Fixes visuales batch 2)

### Badges en listas KPI — regla definitiva
- **SÍ badge**: Destino · Corp · País · Channel · Canasta — en KPI cards globales y canastas
- **NO badge**: Hotel — suprimido en `render_cr_p1/p3.py` y `render_rnd_p1/p3.py` (flag `t_key == 'hotel'` o `parse_hotel`)
- Badge en **análisis por dimensión** → tab Channel: `render_chan_table` en `render_bloque_dimensiones_cr` incluye `mini_badge(BandaEficacia)` al lado del nombre
- `_mini_badge` y `mini_badge` centralizados en `render_helpers.py` (accesibles vía `from render_helpers import *`)

### Paleta D — Aceptable naranja definitivo
- `gauge_5levels`: Aceptable `#5C469C` (violet incorrecto) → `#F59E0B` (naranja sólido)
- `historico_module_v2.py`: Aceptable violet → `bg:#FEF3C7 fg:#92400E` (naranja pastel)
- Revisar: `#D4A878` (ocre) → `#F59E0B` (naranja sólido) ya desde sesión 13

### Opción C searchbox — especificación definitiva
- `.sb-inline-wrap`: `position:relative` + `border-left:1px solid var(--rule)` + padding
- `.sb-inline`: `width:120px` + `font-size:10px` + transición en `:focus`
- `.sb-clear-btn`: `position:absolute;right:4px;top:50%` — visible solo cuando `input.value` no vacío
- `buildLabels()`: construye labels desde `getActiveRows(false)` — solo tab activo, sin cross-card
- Implementado en: análisis por hotel (4 tabs), análisis por dimensión (3 tabs), KPI cards (inline)

### Canastas en KPI cards globales
- `panel_html = col1 + col2 + rest` para `t_key in ('canasta', 'channel')` — ya no usa el vacío `rows_html`
- Las 3 canastas (B2C · CUG · B2B OP) ahora visibles en el tab Canasta de ambas cards globales

### Análisis por dimensión · tab Channel
- `render_chan_table`: badge de banda inline al lado del nombre del canal
- Badge se calcula como `r.get('BandaEficacia','') or banda_eficacia(ef_val)`

### Archivos modificados (sesiones 14-15)
`render_helpers.py` · `historico_module_v2.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p3.py` · `asset_cr_head.html` · `asset_rnd_head.html`

---

**Última actualización:** 23 Mayo 2026 · post W20 s14-15 · badges hotel suprimido · Aceptable naranja · Opción C searchbox definitivo · mini_badge centralizado
---

## 📝 Cambios post W20 · Mayo 2026 (sesión 15+ · Searchbox Prop A+D + wow_pill V1)

### Sistema de searchbox — 3 modos JS (migración completa)

Rediseño del sistema de búsqueda inline. Antes: un único `sb-inline-wrap` compartido entre todos los tabs de un bloque → filtraba cross-tab. Ahora: un searchbox **por contexto** con lógica de aislamiento.

#### Nuevas funciones en `render_helpers.py`

| Función | Uso |
|---|---|
| `wow_pill_html(delta, unit, prefix_pos, prefix_neg)` | Pill verde/rojo/gris border-radius:20px |
| `searchbox_pill_html(input_id, accent_color, placeholder, count_id)` | Pill en tabs-row de KPI cards (Prop A) |
| `searchbox_header_html(input_id, accent_color, placeholder, th_id)` | Header integrado en col1 de tabla (Prop D) |

#### Regla definitiva: cero duplicación

- **KPI cards (hero + canastas)** → `searchbox_pill_html()` al final de `tabs_labels`
- **Tablas hotel + dim (global + canastas)** → `searchbox_header_html()` como primera columna del `<div>` header
- **`sb-inline-wrap` en `tabs-row` de bloques** → **eliminados** (eran el único searchbox antes)

#### wow_pill V1 en KPI-top

```python
# En kpi_card_canasta y cards hero, debajo del badge:
_wow_pp = wow_pill_html(delta, unit='pp')          # CR: Eficacia / ConvRate
_wow_rnd = wow_pill_html(-delta, unit='pp',         # RND NoDispo: invertida
                          prefix_pos='↓', prefix_neg='↑')
```

La pill aparece en `display:flex;align-items:flex-end` junto al valor grande y el badge, con caption "vs sem. ant." delante.

#### JS Engine W21 en `asset_*_head.html`

Tres funciones de auto-attach:
- `attachPill()` — para `[data-sb-pill]`: filtra panel activo, reset al cambiar tab
- `attachTable()` — para `[data-sb-table]`: filtra `[data-lbl]` en bloque padre
- `attachSearchbox()` — modo legado `[data-sb-scope]`: sin cambios de interfaz, + empty state + fix A2

**fix A1:** empty state `"Sin resultados para «query»"` cuando ninguna fila coincide.  
**fix A2:** al cambiar tab, input se vacía y grid resetea a `1fr 1fr`.

#### data-lbl en filas de tabla

Las filas de tablas hotel ahora llevan `data-lbl="hotel corp"` y las de dim `data-lbl="nombre"` para que `attachTable` (Prop D) filtre por ese atributo.

### Commits de esta sesión
- `b121f55` · feat(W20s): searchbox Prop A+D + wow_pill V1 · CR+RND global+canastas
- `97e9d07` · regen(W20): reportes editoriales CR+RND con searchbox Prop A+D · wow_pill V1

### Archivos modificados
`render_helpers.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `render_cr_p1.py` · `render_rnd_p1.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_cr_p3.py` · `render_rnd_p3.py`

---

**Última actualización:** Mayo 2026 · post W20 sesión 15+ · Searchbox Prop A+D + wow_pill V1 · 3 modos JS engine

