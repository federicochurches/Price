# `editorial_engine.py` — Diseño Formal
**Proyecto PRICE · Supply Analytics · Diseño pre-W26**
**Fecha:** 25-06-2026 · Estado: APROBADO — pendiente implementación

---

## 1. Propósito

Fuente única de verdad para la generación de **Resumen Ejecutivo** y **Plan de Acción**
en los reportes CR y RND. Reemplaza la lógica duplicada que hoy vive en:

- `render_cr_p2.py` → `build_cr_cv()` (Sistema A — interactivo JS)
- `render_rnd_p2.py` → `build_rnd_cv()` (Sistema A)
- `render_cr_p3.py` → `_build_canasta_findings_cr()` (Sistema B — editorial HTML)
- `render_rnd_p3.py` → `_build_canasta_findings_rnd()` (Sistema B)

Después de la migración, esos cuatro sitios pasan a ser wrappers de una línea
que llaman a `editorial_engine`.

---

## 2. Modelo causal — principio rector

El RE y el Plan diagnostican **causas**, no consecuencias.
La ConvRate baja nunca aparece como finding aislado — siempre se muestra la causa.

```
CR Eficacia SC+C    → causa técnica de baja ConvRate
                      acción: escalamiento técnico / connectivity

CR Bookability SC+C → causa técnica de baja ConvRate
                      acción: revisión interface / provider

CR Eficacia/BK Exitosa + ConvRate baja
                    → EXCLUIDO del RE/Plan
                      problema de tarifa / posicionamiento / demand fit
                      vive en tablas de severity, no en el ejecutivo

RND NoDispo SC+C    → causa directa de no conversión
                      acción: apertura cupos / escalamiento disponibilidad

RND NoDispo Exitosa/Aceptable + ConvRate baja
                    → EXCLUIDO del RE/Plan
                      problema de pricing / paridad
                      vive en tablas de severity, no en el ejecutivo
```

**CR y RND son independientes.** Un hotel puede aparecer en ambos RE
simultáneamente — CR diagnostica el problema técnico, RND el de disponibilidad.
No hay prioridad entre reportes: son dimensiones distintas del mismo problema,
atendidas por equipos distintos.

---

## 3. Principios de diseño

### 3.1 Universo
Solo hoteles con banda **Súper Crítica** o **Crítica** en la métrica **causa**
entran al RE y al Plan.

```
CR universo RE/Plan = hoteles SC+C en Eficacia  ∪  hoteles SC+C en Bookability
RND universo RE/Plan = hoteles SC+C en NoDispo
```

Las bandas Revisar/Aceptable/Exitosa/Sin Conversión quedan fuera del RE y Plan.

### 3.2 Unidad atómica
El score se calcula siempre a nivel **Hotel**. Las dimensiones superiores
(Corp, Destino, País) se derivan del score del hotel — nunca al revés.

```
score_hotel   → unidad de cálculo
score_corp    = max(score_hotel) de sus hoteles en universo SC+C
score_destino = max(score_corp)  de sus corps en universo SC+C
score_pais    = max(score_destino)  (solo RND)
```

`max()` y no `sum()` — identifica el punto de falla más grave,
no el destino con más hoteles malos acumulados.

### 3.3 Atribución causal
El RE menciona la dimensión agregada como impacto,
el Plan apunta siempre al nivel más atómico accionable.

```
RE finding:   "Destino Cancún — NoDispo 45% (driver: Hotel X · Corp Y)"
Plan acción:  → target = Hotel X  (no el destino)
```

Regla de atribución por Corp:
- Corp con **1 hotel** en SC+C  → acción sobre el **Hotel** (más accionable)
- Corp con **N > 1 hoteles** en SC+C → acción sobre el **Corp** (agrupa el problema)

Destino y País aparecen solo como contexto, nunca como target de acción.

### 3.4 Deduplicación
Si un Hotel ya está representado por su Corp en el RE → no se duplica el Hotel.
Si el Corp ya está representado en el finding del Destino → no se duplica el Corp.
La cadena causal se muestra una sola vez.

### 3.5 WoW como bonus de urgencia (asimétrico)
```
empeoró esta semana (WoW negativo en CR / positivo en RND NoDispo)
    → bonus_wow = +0.10 al score

mejoró esta semana
    → bonus_wow = 0.0  (sin penalización — sigue siendo SC+C)

sin datos WoW
    → bonus_wow = 0.0  (neutro)
```
Un hotel en SC que mejoró 2pp sigue siendo SC — no desaparece del RE.

### 3.6 Calidad de canasta (solo CR)
El tráfico B2C está inflado por bots y consultas de baja intención.
OP y CUG son tráfico de mayor calidad comercial.
El volumen se ajusta antes de normalizar:

```python
CANASTA_QUALITY = {
    'b2c':    0.3,   # descuento fuerte — ruido de bots
    'op':     0.8,   # calidad media-alta
    'cug':    1.0,   # calidad máxima — sin descuento
    'global': 0.6,   # mix aproximado
}
```

**En RND no aplica ajuste de canasta** — el Tráfico refleja búsquedas
reales sin disponibilidad respuesta, no hay ruido de bots equivalente.

### 3.7 Volumen por reporte y métrica

```python
VOL_COL = {
    # CR — CR_Unicos ajustado por calidad de canasta
    'eficacia':    'CR_Unicos',   # × CANASTA_QUALITY[scope]
    'convrate':    'CR_Unicos',   # × CANASTA_QUALITY[scope]
    'bookability': 'Bookings',    # Bookings reales, sin ajuste

    # RND — Tráfico crudo (búsquedas sin respuesta = el problema)
    'nodispo':     'Trafico',
}
```

### 3.8 Acciones condicionales
Las acciones del Plan solo se generan si su condición de datos se cumple.
Mejor 3 acciones reales que 6 con 3 vacías o irrelevantes.

---

## 4. Modelo de scoring

### 4.1 Score de hotel (unidad atómica)

```python
def score_hotel(row, vol_max, metric, scope, report_type):
    """
    row:         fila de DataFrame (hotel en universo SC+C)
    vol_max:     máximo de volumen ajustado en el universo SC+C
    metric:      'eficacia' | 'bookability' | 'nodispo'
    scope:       'global' | 'b2c' | 'op' | 'cug'
    report_type: 'cr' | 'rnd'
    """

    # --- Volumen (ajustado por calidad si CR) ---
    vol_raw = row[VOL_COL[metric]]
    quality = CANASTA_QUALITY[scope] if report_type == 'cr' and metric != 'bookability' else 1.0
    vol_ajustado = vol_raw * quality
    vol_norm = vol_ajustado / vol_max if vol_max > 0 else 0.0

    # --- Severidad ---
    sev_idx = 1.0 if row['banda'] == 'Súper Crítica' else 0.6

    # --- Bonus WoW (asimétrico) ---
    wow_val = row.get(WOW_COL[metric])
    if wow_val is None or pd.isna(wow_val):
        bonus_wow = 0.0
    elif report_type == 'rnd':
        bonus_wow = 0.10 if wow_val > 0 else 0.0   # NoDispo sube = empeora
    else:
        bonus_wow = 0.10 if wow_val < 0 else 0.0   # Eficacia/BK baja = empeora

    # --- Score final ---
    return (
        0.60 * vol_norm   +   # volumen dominante
        0.30 * sev_idx    +   # SC pesa más que Crítico
        0.10 * bonus_wow      # bonus urgencia WoW
    )
```

### 4.2 Derivación de dimensiones superiores

```python
def _derive_dim(df_hotels_sc_c, dim_col, vol_col, quality=1.0):
    """
    Agrega hoteles SC+C por dimensión.
    score_dim = max(score_hotel) — punto de falla más grave.
    n_hoteles_sc_c = conteo para regla de atribución.
    """
    if len(df_hotels_sc_c) == 0 or dim_col not in df_hotels_sc_c.columns:
        return pd.DataFrame()

    return (
        df_hotels_sc_c
        .groupby(dim_col)
        .agg(
            score         = ('score',     'max'),
            n_hoteles_sc_c= ('Hotel',     'count'),
            vol_total     = (vol_col,     'sum'),
            # hotel driver = el que tiene el mayor score en este dim
            hotel_driver  = ('Hotel',     lambda x: x.loc[df_hotels_sc_c.loc[x.index, 'score'].idxmax()]),
            corp_driver   = ('CorpName',  lambda x: x.loc[df_hotels_sc_c.loc[x.index, 'score'].idxmax()]),
        )
        .reset_index()
        .sort_values('score', ascending=False)
    )
```

### 4.3 Tablas de constantes

```python
WOW_COL = {
    'eficacia':    'Eficacia_WoW_pp',
    'convrate':    'ConvRate_WoW_pp',
    'bookability': 'Bookability_WoW_pp',
    'nodispo':     'NoDispo_WoW_pp',
}

BANDA_COL = {
    'eficacia':    'BandaEficacia',
    'convrate':    'BandaConvRate',
    'bookability': 'BandaBookability',
    'nodispo':     'BandaNoDispo',
}

BANDAS_SC_C = {'Súper Crítica', 'Crítica'}

# Umbrales mínimos de volumen
# REVISABLES después del primer run W26
UMBRAL_MIN_CR  = 100      # CR_Unicos mínimos para acción QW hotel CR
UMBRAL_MIN_RND = 10_000   # Tráfico mínimo para acción QW hotel RND
UMBRAL_PAIS    = 100_000  # Tráfico mínimo para acción País RND
N_MIN_COHORTE  = 3        # Hoteles mínimos para acción MP de saneamiento
```

---

## 5. API pública

### 5.1 `build_findings(payload, report_type, scope)`

```python
def build_findings(payload, report_type, scope='global'):
    """
    Genera lista de exactamente 10 findings para el Resumen Ejecutivo.
    Ordenados por score descendente (posiciones #1 global y #10 P80 son fijas).

    Retorna list[dict] — siempre 10 items.
    Cada item: {'numero': str, 'titulo': str, 'desc': str, 'score': float}
    """
```

**Finders CR — en orden de prioridad base:**

```
#1  (fijo)   _find_eficacia_global      Eficacia global del scope + banda
#2           _find_n_hoteles_ef_sc_c    N hoteles SC+C Eficacia
#3           _find_n_hoteles_bk_sc_c    N hoteles SC+C Bookability (si hay datos BK)
#4           _find_top_hotel_ef         Hotel #1 score Eficacia + cadena causal
#5           _find_top_hotel_bk         Hotel #1 score Bookability (si distinto de #4)
#6           _find_top_corp_ef          Corp #1 score Eficacia (si N>1 hoteles)
#7           _find_top_destino_ef       Destino #1 score Eficacia + hotel driver
#8           _find_top_channel_ef       Channel #1 score Eficacia
#9           _find_wow_deterioro_cr     Entidad con mayor deterioro WoW (si existe)
#10 (fijo)   _find_universo_p80         N hoteles P80 — cierre
```

**Finders RND — en orden de prioridad base:**

```
#1  (fijo)   _find_nodispo_global       NoDispo global + banda + WoW
#2           _find_n_hoteles_nd_sc_c    N hoteles SC+C NoDispo
#3           _find_top_hotel_nd         Hotel #1 score NoDispo + cadena causal
#4           _find_top_corp_nd          Corp #1 score NoDispo (si N>1 hoteles)
#5           _find_top_destino_nd       Destino #1 score + hotel driver
#6           _find_top_pais_nd          País #1 score + destino driver
#7           _find_top_channel_nd       Channel #1 score NoDispo
#8           _find_wow_deterioro_rnd    Entidad con mayor deterioro WoW
#9           _find_ipm_contexto         IPM global — contexto de impacto revenue
#10 (fijo)   _find_universo_p80_rnd     N hoteles P80 — cierre
```

**Reordenamiento:** findings #2–#9 se reordenan por score descendente.
Findings #1 y #10 tienen posición fija.

**Formato de cadena causal en el finding:**
```
titulo: "Destino Cancún — NoDispo 45,2%"
desc:   "Driver: Hotel Iberostar Cancún (Iberostar) · 2,3M búsquedas · SC ↑+8,3pp WoW"
```

---

### 5.2 `build_action_plan(payload, report_type, scope)`

```python
def build_action_plan(payload, report_type, scope='global'):
    """
    Genera 3–6 acciones para el Plan de Acción.
    Solo se generan si su condición de datos se cumple.
    Ordenadas por score dentro de cada categoría (QW → MP → ES).

    Cada item:
    {
        'c':       'qw' | 'mp' | 'es',
        'o':       str,           # de areas_catalogo.py
        'a':       str,           # texto generado desde datos
        't':       str,           # tag corto
        'p':       str,           # plazo
        'metrica': str,           # métrica objetivo
        'score':   float,         # heredado del hotel/corp target
        'target':  str,           # Hotel o Corp al que apunta
    }
    """
```

**Acciones CR y sus condiciones:**

```
[QW-1] Escalar hotel #1 Eficacia SC+C
        condición: hotel SC+C Eficacia con CR_Unicos*quality >= UMBRAL_MIN_CR
        owner:     supply_optimization
        target:    hotel con mayor score Eficacia
        texto:     "Escalar {Hotel} ({Corp}) — Eficacia {val}% con {cr} CR únicos
                    en canasta {scope}. Driver técnico de baja ConvRate."
        plazo:     "W{N}"
        metrica:   "Eficacia > 85%"

[QW-2] Escalar hotel #1 Bookability SC+C  (si distinto de QW-1)
        condición: hotel SC+C Bookability con Bookings >= UMBRAL_MIN_CR
        owner:     supply_optimization_tps
        target:    hotel con mayor score Bookability
        texto:     "Diagnóstico interface {Hotel} ({Corp}) — Bookability {val}%
                    con {bk} bookings afectados. Revisar provider y configuración."
        plazo:     "W{N}"
        metrica:   "Bookability > 97%"

[MP-1] Saneamiento cohorte SC+C Eficacia
        condición: n_ef_sc_c >= N_MIN_COHORTE
        owner:     supply_optimization
        target:    "{n} hoteles Crítica+ Eficacia"
        texto:     "Plan de saneamiento para {n} hoteles SC+C de Eficacia
                    en {scope}. Target: {n//2} hoteles a banda Revisar."
        plazo:     "3 semanas"
        metrica:   "{n//2} hoteles a Revisar"

[MP-2] Revisión ConvRate vs target
        condición: cv_global < 0.015  (Revisar o peor)
                   Y ef_global >= 0.93  (Eficacia no es el driver)
                   → solo aparece si el problema NO es Eficacia/BK
        owner:     supply_comercial_wholesale
        texto:     "ConvRate {scope} en {val}% — Eficacia sana indica
                    problema de tarifa/paridad. Revisión comercial."
        plazo:     "2 semanas"
        metrica:   "ConvRate ≥ 2,5%"

[ES-1] Corp con mayor concentración hoteles SC+C Eficacia
        condición: corp con n_hoteles_sc_c >= N_MIN_COHORTE
        owner:     supply_comercial_supply_optimization
        target:    corp con más hoteles SC+C
        texto:     "{Corp} concentra {n} hoteles SC+C de Eficacia en {scope}.
                    Escalamiento KAM + revisión técnica por cuenta."
        plazo:     "Q3"
        metrica:   "-50% hoteles SC+C en corp"

[ES-2] Channel peor Eficacia SC+C
        condición: channel en SC+C Eficacia
        owner:     supply_comercial_wholesale
        target:    channel con menor Eficacia
        texto:     "Channel {channel} en banda {banda} — Eficacia {val}%.
                    Auditoría técnica y renegociación SLA."
        plazo:     "Q3"
        metrica:   "Eficacia > 93%"
```

**Acciones RND y sus condiciones:**

```
[QW-1] Escalar hotel #1 NoDispo SC+C
        condición: hotel SC+C NoDispo con Trafico >= UMBRAL_MIN_RND
        owner:     supply_comercial_supply_optimization
        target:    hotel con mayor score NoDispo
        texto:     "Escalar {Hotel} ({Corp}) — NoDispo {val}% con {traf}
                    búsquedas perdidas. Apertura cupos urgente."
        plazo:     "W{N}"
        metrica:   "NoDispo < 20%"

[QW-2] Corp SC+C con más hoteles NoDispo afectados
        condición: corp con n_hoteles_sc_c >= 2
        owner:     supply_optimization_tps
        target:    corp con más hoteles SC+C NoDispo
        texto:     "{Corp} tiene {n} hoteles SC+C de NoDispo en {scope}.
                    Revisión de cupos y paridad por cuenta."
        plazo:     "W{N}"
        metrica:   "NoDispo < 20% en todos"

[MP-1] Saneamiento cohorte SC+C NoDispo
        condición: n_nd_sc_c >= N_MIN_COHORTE
        owner:     supply_optimization
        texto:     "Plan de saneamiento para {n} hoteles SC+C de NoDispo
                    en {scope}. Target: {n//2} hoteles a banda Revisar."
        plazo:     "3 semanas"
        metrica:   "{n//2} hoteles a Revisar"

[MP-2] IPM bajo + NoDispo como driver
        condición: ipm_global < 650
                   Y n_nd_sc_c >= N_MIN_COHORTE
                   → IPM bajo explicado por NoDispo alta, no por pricing
        owner:     supply_comercial_wholesale
        texto:     "IPM {scope} en ${val} — NoDispo SC+C es el driver
                    de revenue perdido. Resolver disponibilidad antes de
                    intervención comercial."
        plazo:     "2 semanas"
        metrica:   "IPM ≥ $650 post-saneamiento"

[ES-1] Destino #1 NoDispo SC+C
        condición: destino SC+C con Trafico >= UMBRAL_MIN_RND
        owner:     supply_comercial_supply_optimization
        target:    destino con mayor score NoDispo
        texto:     "Destino {Destino} — NoDispo agregada {val}%
                    (driver: {Hotel} · {Corp}). Estrategia de apertura
                    de destino."
        plazo:     "Q3"
        metrica:   "NoDispo destino < 5%"

[ES-2] País SC+C con mayor volumen afectado
        condición: país SC+C con Trafico >= UMBRAL_PAIS
        owner:     supply_comercial_wholesale
        target:    país con mayor score NoDispo
        texto:     "País {País} — {n} destinos SC+C NoDispo · {traf}
                    búsquedas perdidas. Revisión contractual regional."
        plazo:     "Q3"
        metrica:   "NoDispo país < 5%"
```

---

### 5.3 `build_carryover(payload_curr, payload_prev, report_type)`

```python
def build_carryover(payload_curr, payload_prev, report_type):
    """
    Hoteles que persisten en SC+C esta semana respecto a la anterior.
    Retorna [] si payload_prev es None.
    Máximo 5 items, ordenados por score descendente.

    Formato: "{Hotel} ({Corp}) — persiste en {banda} · WoW {wow_pp}pp"
    """
```

Detección de persistencia: hotel en SC+C esta semana con `|WoW_pp| < 0.5pp`
— no hubo cambio significativo → ya estaba en SC+C la semana anterior.

---

## 6. Estructura del payload

### 6.1 Payload CR

```python
{
    # Métricas globales del scope
    'ef_global':  float,    # Eficacia global
    'cv_global':  float,    # ConvRate global
    'ef_wow':     float,    # WoW Eficacia en pp (NaN si no disponible)
    'cv_wow':     float,    # WoW ConvRate en pp

    # Universo SC+C — ya filtrados y con score calculado
    'hoteles_ef_sc_c':   pd.DataFrame,  # SC+C Eficacia · col 'score' incluida
    'hoteles_bk_sc_c':   pd.DataFrame,  # SC+C Bookability · puede estar vacío

    # Dimensiones derivadas (via _derive_dim)
    'corps_ef_sc_c':     pd.DataFrame,  # cols: CorpName, score, n_hoteles_sc_c, hotel_driver
    'dests_ef_sc_c':     pd.DataFrame,  # cols: Destino, score, n_hoteles_sc_c, hotel_driver, corp_driver
    'channels_ef_sc_c':  pd.DataFrame,  # cols: ExternalProviderName, score, n_hoteles_sc_c

    # Conteos
    'n_ef_sc_c':  int,
    'n_bk_sc_c':  int,
    'n_p80':      int,

    # Metadata
    'scope':         str,   # 'global' | 'b2c' | 'op' | 'cug'
    'canasta_label': str,   # 'Global' | 'B2C' | 'Opaco' | 'Ultra Opaco'
    'week_num':      int,
    'week_prev':     int,
}
```

### 6.2 Payload RND

```python
{
    # Métricas globales
    'nd_global':  float,
    'ipm_global': float,
    'nd_wow':     float,    # pp (positivo = empeora)
    'ipm_wow':    float,    # % cambio

    # Universo SC+C
    'hoteles_nd_sc_c':   pd.DataFrame,  # SC+C NoDispo · col 'score' incluida

    # Dimensiones derivadas
    'corps_nd_sc_c':     pd.DataFrame,
    'dests_nd_sc_c':     pd.DataFrame,
    'paises_nd_sc_c':    pd.DataFrame,
    'channels_nd_sc_c':  pd.DataFrame,

    # Conteos
    'n_nd_sc_c':  int,
    'n_p80':      int,

    # Metadata (igual que CR)
    'scope':         str,
    'canasta_label': str,
    'week_num':      int,
    'week_prev':     int,
}
```

### 6.3 Columnas requeridas en DataFrames de hoteles SC+C

```
Hotel, CorpName, Destino
PaisDestino          (solo RND)
ExternalProviderName (solo CR — channel)
[métrica principal]  Eficacia | Bookability | %NoDispo
[volumen]            CR_Unicos | Bookings | Trafico
[wow_pp]             Eficacia_WoW_pp | Bookability_WoW_pp | NoDispo_WoW_pp
banda                'Súper Crítica' | 'Crítica'
score                float — calculado por score_hotel()
```

---

## 7. Archivos afectados

| Archivo | Cambio |
|---|---|
| `editorial_engine.py` | **NUEVO** — fuente única |
| `render_cr_p2.py` | `build_cr_cv()` → wrapper 3 líneas |
| `render_rnd_p2.py` | `build_rnd_cv()` → wrapper 3 líneas |
| `render_cr_p3.py` | `_build_canasta_findings_cr()` + plan → wrappers |
| `render_rnd_p3.py` | `_build_canasta_findings_rnd()` + plan → wrappers |
| `engine.py` | Sin cambios (bandas centralizadas aquí) |
| `areas_catalogo.py` | Sin cambios (owners centralizados aquí) |
| `template_resumen.py` | Sin cambios (render HTML correcto) |

---

## 8. Estrategia de implementación (W26)

```
Paso 1  Crear editorial_engine.py
        · constantes (CANASTA_QUALITY, VOL_COL, WOW_COL, umbrales)
        · score_hotel()
        · _derive_dim()
        · _build_payload() CR y RND
        Validar: payload se construye sin errores desde pickle W26

Paso 2  build_findings CR
        Validar: output idéntico al actual antes de activar reordenamiento

Paso 3  build_findings RND
        Validar: finding #5 corregido (bug canal NoDispo)

Paso 4  build_action_plan CR + RND
        Validar: condiciones reales, sin acciones vacías

Paso 5  build_carryover
        Validar: retorna [] sin WoW disponible

Paso 6  Migrar render_cr_p2.py → wrapper
        Validar: HTML visualmente idéntico a W25

Paso 7  Migrar render_rnd_p2.py → wrapper

Paso 8  Migrar render_cr_p3.py + render_rnd_p3.py → wrappers

Paso 9  Pipeline W26 completo
```

**Regla de validación (regla #39 PROMPT_CORE):**
En pasos 2–5, el engine reproduce el output actual antes de introducir
cambios de contenido. Los cambios de lógica (scoring reordenado,
nuevos findings, acciones condicionales) se activan solo después
de verificar que la base es correcta.

---

## 9. Pendiente post-W26

- **Activar reordenamiento por score** en RE (fase C completa)
- **Bookability en RE/Plan** — payload ya incluye `hoteles_bk_sc_c`,
  finders BK diferidos a sesión post-W26
- **Carryover enriquecido** — detección exacta cuando haya
  2+ semanas de historial en pickle
- **Revisión de umbrales** — `UMBRAL_MIN_CR`, `UMBRAL_MIN_RND`,
  `UMBRAL_PAIS`, `N_MIN_COHORTE` ajustables después del primer run
- **Rediseño visual Plan de Acción** en `SUPPLY_WNN.html` —
  sesión dedicada separada

---

*Documento generado: 25-06-2026*
*Decisiones aprobadas por Federico Iglesias · implementación en W26*
