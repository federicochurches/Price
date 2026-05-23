# Sistema de Bandas · Paleta D · Vigente desde Week 20

Las bandas dividen los hoteles del P80 en 5 niveles de severidad por cada métrica. La paleta de colores se actualizó en Week 20 a la **Paleta D** (más contrastada, sin cyan en severity), y los badges adoptaron el estilo **Opción D** (font 13px, padding generoso, mayúsculas centradas, sin "Target" dentro del badge).

---

## Paleta D · colores definitivos

| Banda | Texto (fg) | Fondo (bg) | Border (bd) |
|---|---|---|---|
| **Exitosa** | `#085041` verde teal | `#E1F5EE` | `#1D9E75` |
| **Aceptable** | `#3C3489` violet oscuro | `#EDE8F7` | `#5C469C` |
| **Revisar** | `#7C2D12` naranja oscuro | `#FFEDD5` | `#F97316` naranja vibrante |
| **Crítica** | `#99162B` rojo oscuro | `#FCE4F1` | `#C0392B` |
| **Súper Crítica** | `#FCEBEB` rojo muy claro (texto) | `#A32D2D` rojo oscuro | `#791F1F` |
| **Sin Conversión** | `#5F5E5A` gris oscuro | `#F2EEE6` | `#8A8377` |

> **Súper Crítica** es la única banda con **fondo sólido + texto claro** (las demás son texto oscuro + fondo claro).

---

## Estilo Opción D · badge pill

Todos los badges de banda (Hero KPIs, módulos históricos, tablas Severity, pills en filas) usan el mismo estilo:

```
font-size: 13px           (canastas: 11px)
font-weight: 700
letter-spacing: .04em
text-transform: uppercase
padding: 10px 22px
border-radius: 3px
border: 1px solid {bd}
text-align: center
```

El texto del badge es **solo el nombre de la banda en mayúsculas**. El target ya no va dentro del badge — se renderiza como caption gris debajo:

```html
<span class="badge">REVISAR</span>
<div class="target-caption">Target ≥ 97%</div>
```

Función: `banda_pill(banda, target=None, font_size='13px')` en `_scripts/render_helpers.py`.  
Caption: `target_caption(target_text, font_size='11px')` en `_scripts/render_helpers.py`.

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

> IPM = Gross Booking USD por millón de búsquedas = `gb_usd / Trafico × 1.000.000`  
> Renombrada desde "RPM" en Week 18. Variables Python siguen llamándose `rpm`/`BandaRPM` por compatibilidad, displays usan "IPM".

| Banda | Rango |
|---|---|
| Exitosa | ≥ $1500 |
| Aceptable | $650 – $1500 |
| Revisar | $200 – $650 |
| Crítica | < $200 |
| Sin Conversión | BKGS = 0 |

**Target global:** ≥ $650 (banda Aceptable o mejor)

> **Bug fix Week 18:** Antes la función `banda_rpm()` usaba thresholds 1/2.5/4 (cuando la métrica era reservas/M). Cualquier valor RPM > 4 caía en Exitosa, dando lecturas incorrectas. Corregido a thresholds 200/650/1500 USD/M consistentes con la métrica actual.

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

Sin Conversión **NO es la peor banda** — es una **cohorte estructural separada**. Los hoteles con `BKGS=0` requieren diagnóstico técnico/contractual (mapping, paridad, inventario) y NO entran en la severity normal.

**Por qué:** antes el ~60% de hoteles caía en "Súper Crítica" porque tenían BKGS=0, saturando la severity. Ahora Severity se aplica solo a los procesables (BKGS > 0) y Sin Conversión queda como un canal de remediación distinto.

**Aplica a:** Conv Rate (CR) e IPM (RND). En %NoDispo y Eficacia no aplica porque esas métricas se calculan sin depender de bookings.

---

## Gauge de 5 niveles · regla definitiva

Todas las barras del gauge: `height:6px · opacity:1` — colores sólidos puros, grosor uniforme. **Sin transparencia.** La banda activa se identifica por la pill encima, no por el gauge.

Colores del gauge (independientes del bd del badge):
- Súper Crítica: `#161616` negro
- Crítica: `#C0392B` rojo
- Revisar: `#D4A878` ámbar suave
- Aceptable: `#5C469C` violet
- Exitosa: `#085041` verde teal

Implementación: `gauge_5levels(banda_actual, niveles_rnd_or_cr)` en `_scripts/render_helpers.py`.

---

## Excepciones · cyan `#4FC3F4` se mantiene SOLO en 2 lugares

Tras Week 20 sesión 3 + sesión 4, el cyan `#4FC3F4` se eliminó de toda referencia a "Exitosa" y queda exclusivamente como acento corporativo en:

1. **`IPM_ACCENT`** en módulos históricos RND (`_scripts/historico_module_rnd.py` línea 10) — Arctic Blue corporativo, accent visual del módulo IPM
2. **Label "🔌 Third Party"** en sección por channel CR (`_scripts/render_cr_p1.py` líneas 197, 338) — color identitario de la familia Third Party

Cualquier otro `#4FC3F4` en el código es un bug a corregir.

---

## Implementación · archivos canónicos

| Archivo | Qué define |
|---|---|
| `_scripts/engine.py` | Funciones `banda_nodispo()`, `banda_rpm()`, `banda_eficacia()`, `banda_convrate()` con thresholds |
| `_scripts/render_helpers.py` | `BANDA_COLORS` dict + `banda_pill()` + `target_caption()` + `gauge_5levels()` |
| `_scripts/historico_module_v2.py` | `_BANDA_COLORS` local (CR, debe coincidir con render_helpers) |
| `_scripts/historico_module_rnd.py` | `_BANDA_COLORS` local (RND, debe coincidir) + `IPM_ACCENT` cyan corporativo |
| `_scripts/template_severity.py` | Tablas Severity con `{'label','rango','count','bg','fg'}` |
| `_scripts/asset_cr_head.html` | CSS vars `--green` y `--green-soft` |
| `_scripts/asset_rnd_head.html` | CSS vars `--green` y `--green-soft` |
| `_scripts/excel_cr.py` · `_scripts/excel_rnd.py` | Etiquetas de Severity en Excel |

---

## Cambios de bandas en sesiones recientes

### Week 20 · sesión 4 (post-revert) · Mayo 2026

- **Estilo Opción D** aplicado a TODOS los badges (Hero, módulos históricos, severity, pills)
- Target X% sale del badge → caption gris separado debajo
- Quitado "Banda" como label arriba del badge en módulo histórico CR (ya estaba bien en RND)
- Quitado "Banda: XXX" del footer del módulo histórico CR

### Week 20 · sesión 3 · Mayo 2026

- **Exitosa cyan `#4FC3F4` → verde teal `#085041`** en gauges, pills, var `--green` CSS
- **Súper Crítica negro → rojo oscuro `#A32D2D`** en pills (no en gauge bar, que sigue negro)
- **Gauge `height:6px opacity:1`** uniforme

### Week 20 · sesión 2 · Mayo 2026

- Paleta D commiteada: Aceptable violet más oscuro, Revisar naranja vibrante, Crítica rojo más oscuro
- Súper Crítica con fondo sólido + texto claro

---

**Última actualización:** Mayo 2026 · post W20 sesión 4 · Paleta D + Opción D + Exitosa verde teal + Sin "Banda" label + target separado del badge
