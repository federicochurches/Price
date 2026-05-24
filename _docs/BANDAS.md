# Sistema de Bandas · Paleta D · Vigente desde Week 20

Las bandas dividen los hoteles del P80 en 5 niveles de severidad por cada métrica. La paleta de colores se actualizó en Week 20 a la **Paleta D** y los badges adoptaron el estilo **Opción D** (mayúsculas, sin target dentro del badge).

---

## Paleta D · colores definitivos · ÚNICA FUENTE: `render_helpers.BANDA_COLORS`

> ⚠️ **Regla de oro:** Los colores de bandas NUNCA se hardcodean fuera de `BANDA_COLORS` en `render_helpers.py`. Cualquier otro dict local de colores de banda en el código es un bug.

| Banda | fg (texto) | bg (fondo) | bd (borde) | bar (barra severity) |
|---|---|---|---|---|
| **Exitosa** | `#1A6B4A` verde | `#E1F5EE` verde claro | `#1D9E75` | `#1A6B4A` |
| **Aceptable** | `#713F12` ámbar oscuro | `#FEF9C3` amarillo claro | `#FCD34D` | `#FCD34D` |
| **Revisar** | `#C2410C` naranja oscuro | `#FED7AA` naranja claro | `#F97316` | `#F97316` |
| **Crítica** | `#99162B` rojo oscuro | `#FCE4F1` rosado claro | `#C0392B` | `#C0392B` |
| **Súper Crítica** | `#FFFFFF` blanco | `#161616` negro | `#DC2626` | `#DC2626` |
| **Sin Conversión** | `#5F5E5A` gris oscuro | `#F2EEE6` crema | `#8A8377` | `#8A8377` |

> **Súper Crítica** es la única banda con **fondo sólido oscuro + texto blanco**.  
> Las demás son texto oscuro + fondo claro (pastel).

### Nota sobre divergencia histórica
BANDAS.md previo (post W20 s3) documentaba colores que nunca llegaron al código (Exitosa `#085041`, Aceptable `#3C3489`, Súper Crítica `#A32D2D`). Esta versión refleja la realidad del código a partir de W21.

---

## Gauge de 5 niveles · regla definitiva

Todas las barras: `height:8px · border-radius:2px` — colores sólidos puros, sin transparencia.  
Barra Revisar: `#F97316` (naranja) ≠ barra Aceptable: `#FCD34D` (amarillo) — **son diferentes**.  
Implementación: `gauge_5levels(banda_actual, tipo)` en `render_helpers.py`.

---

## Estilo Opción D · badge pill

Todos los badges de banda (Hero KPIs, módulos históricos, tablas Severity, pills inline):

```
font-size: 11px–13px (13px hero · 11px canastas · 9px severity rows)
font-weight: 700
letter-spacing: .04–.06em
text-transform: uppercase
padding: según contexto
border-radius: 2–3px
border: 1px solid {bd}
```

El texto del badge es **solo el nombre de la banda en mayúsculas**. El target va como caption gris separado.

Función: `banda_pill(banda, target=None, font_size='11px')` en `render_helpers.py`.

---

## Rangos por métrica

### % de No Disponibilidad (RND)

| Banda | Rango |
|---|---|
| Exitosa | < 3% |
| Aceptable | 3 – 5% |
| Revisar | 5 – 20% |
| Crítica | 20 – 60% |
| Súper Crítica | > 60% |

**Target global:** < 3% (banda Exitosa)

### IPM · Income Per Million USD (RND)

> IPM = `gb_usd / Trafico × 1.000.000`  
> Variables Python usan `rpm`/`BandaRPM` por compatibilidad; displays dicen "IPM".

| Banda | Rango |
|---|---|
| Exitosa | ≥ $650 |
| Aceptable | $500 – $649 |
| Revisar | $200 – $499 |
| Crítica | < $200 |
| Sin Conversión | BKGS = 0 |

**Target global:** ≥ $650 (banda Aceptable o mejor)

### Eficacia (CR)

| Banda | Rango |
|---|---|
| Exitosa | ≥ 97% |
| Aceptable | 93 – 97% |
| Revisar | 85 – 93% |
| Crítica | 60 – 85% |
| Súper Crítica | < 60% |

**Target global:** ≥ 97% (banda Exitosa)

### Conv Rate (CR)

| Banda | Rango |
|---|---|
| Exitosa | ≥ 2,5% |
| Aceptable | 1,5 – 2,5% |
| Revisar | 0,8 – 1,5% |
| Crítica | < 0,8% |
| Sin Conversión | BKGS = 0 |

**Target global:** ≥ 2,5% (banda Exitosa)

---

## Sistema D · "Sin Conversión" como cohorte aparte

Sin Conversión **NO es la peor banda** — es una **cohorte estructural separada** (BKGS=0, requiere diagnóstico técnico, no severidad). Aplica a Conv Rate (CR) e IPM (RND).

---

## Implementación · archivos canónicos

| Archivo | Qué define |
|---|---|
| `render_helpers.py` | **`BANDA_COLORS`** · dict maestro · `banda_pill()` · `gauge_5levels()` · `target_caption()` |
| `template_severity.py` | `LEVELS_*` · `make_severity_levels()` · `render_severity_block()` · importa de `render_helpers` |
| `historico_module_v2.py` | `_BANDA_COLORS` local (CR) · debe coincidir con `render_helpers` |
| `historico_module_rnd.py` | `_BANDA_COLORS` local (RND) · debe coincidir · `IPM_ACCENT=#4FC3F4` es excepción válida |
| `engine.py` | Funciones `banda_nodispo()` · `banda_rpm()` · `banda_eficacia()` · `banda_convrate()` |
| `asset_cr_head.html` | CSS vars `--green:#1A6B4A` · `--green-soft:#E1F5EE` |
| `asset_rnd_head.html` | CSS vars `--green:#1A6B4A` · `--green-soft:#E1F5EE` |

---

## Excepciones · cyan `#4FC3F4` en 2 lugares únicamente

1. `IPM_ACCENT` en `historico_module_rnd.py` — Arctic Blue corporativo, accent módulo IPM
2. Label "🔌 Third Party" en `render_cr_p1.py` — color identitario Third Party

Cualquier otro `#4FC3F4` es un bug.

---

## Checklist anti-regresión · aplicar en cada sesión de cambios de color

```bash
# Verificar que no quedan dicts locales de color de banda:
grep -rn "BADGE_COLORS\|SOLID = {" _scripts/*.py

# Verificar que no quedan fg=FFFFFF para todos (solo Súper Crítica lo tiene):
grep -rn "fg.*FFFFFF.*else.*FFFFFF" _scripts/*.py

# Verificar que Revisar y Aceptable tienen colores distintos en gauge:
grep -n "Revisar\|Aceptable" _scripts/render_helpers.py | grep "#FCD34D"

# Verificar cyan fuera de contextos permitidos:
grep -rn "#4FC3F4" _scripts/*.py | grep -v "historico_module_rnd\|IPM_ACCENT\|Third Party"

# Verificar que barra Súper Crítica no usa #161616 (el fondo):
grep -rn "bar.*161616\|161616.*bar" _scripts/*.py
```

---

**Última actualización:** Mayo 2026 · post W20 · alineación BANDAS.md con código real · paleta efectiva W21+
