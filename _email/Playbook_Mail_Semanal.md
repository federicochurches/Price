# Playbook Semanal · Mail Supply Optimization

Guía paso a paso para enviar el mail unificado cada lunes (cierre semanal).

---

## ⏱ Tiempo estimado: 10-15 minutos

---

## Antes de empezar — checklist

- [ ] Reportes CheckRates y RatesNoDispo de la semana ya publicados en Netlify
- [ ] URLs de los reportes funcionando:
  - `https://analytics-desk.netlify.app/checkrates/week-NN/CheckRates_Reporte_Editorial.html`
  - `https://analytics-desk.netlify.app/rates-nodispo/week-NN/RatesNoDispo_Reporte_Editorial.html`
- [ ] Tener a mano los KPIs y top hallazgos de la semana (del Excel de análisis)

---

## Workflow

### Paso 1 — Abrir Claude

Abrir nueva conversación con Claude (claude.ai). Conectar Gmail si no está.

### Paso 2 — Indicarle a Claude

Pegale este mensaje:

```
Hola Claude. Necesito enviar el mail semanal del HUB Supply Optimization · Week NN
(YY al ZZ de [mes]).

KPIs CheckRates:
- Eficacia: XX.XX% [delta]
- Conv Rate: X.XX% [delta WoW]
- HTS P80: NNNN hoteles · NNN.NNN CheckRates · NNN BKGS
- Por canasta: B2C XX% · OP XX% · CUG XX%

KPIs RatesNoDispo:
- GB perdido: $X.XM [delta]
- Hoteles con 0 BKGS: NNNNN [delta]
- Top destinos %NoDispo: [Destino1] XX% · [Destino2] XX% · [Destino3] XX%
- Menor RPM por Corp: [Corp1] X.XX · [Corp2] X.XX · [Corp3] X.XX

Top hallazgos CheckRates: [pegar 4 bullets]
Top hallazgos RatesNoDispo: [pegar 4 bullets]
Análisis por canasta RatesNoDispo: [pegar 3 bullets B2C/OP/CUG]
Plan de acción CheckRates: [pegar 5 bullets QW/MP]
Plan de acción RatesNoDispo: [pegar 5 bullets QW/MP/ES]

Lede principal sugerido: [escribir 2-3 frases con titulares de impacto]

Por favor:
1. Generá un preview HTML para revisar en navegador
2. Cuando esté OK, creá el draft en Gmail con:
   - To: federico.iglesias@pricetravel.com
   - BCC: ver _email/destinatarios.md
   - Credenciales del hub embebidas en bloque destacado
   - Asunto: Supply Optimization · Week NN · Rates No Dispo y CheckRates
```

### Paso 3 — Iterar el preview

Claude te genera un PREVIEW HTML. Lo descargás, lo abrís en el navegador y revisás:

- ¿KPIs correctos?
- ¿Hallazgos bien explicados?
- ¿Plan de acción claro?
- ¿URLs apuntan a la semana correcta?
- ¿Próxima publicación con la fecha correcta?

Si algo no está bien → le decís a Claude qué cambiar y genera PREVIEW v2, v3, etc.

### Paso 4 — Crear draft final

Cuando el preview esté OK, le pedís a Claude que cree el draft en Gmail. El draft incluye **automáticamente las credenciales del hub** (usuario: pricetravel · password: supply2026).

### Paso 5 — Verificar en Gmail (sin tocar el cuerpo)

1. Andá a `gmail.com → Borradores`
2. **Abrí el draft** para verlo
3. **NO hagas click adentro del cuerpo del mail** (Gmail tiende a "limpiar" el HTML)
4. Verificá:
   - ✅ Asunto correcto
   - ✅ BCC con los 12 destinatarios
   - ✅ Cuerpo con formato (colores, badges, links)
   - ✅ Bloque amarillo de credenciales visible
5. Si todo OK → click en **Enviar** (avión de papel) sin tocar nada más

### Paso 6 — Si el formato se rompe

Si entrás al draft y el HTML se "limpia" (texto plano):
1. **Cerrá sin guardar**
2. Pedile a Claude que cree el draft de nuevo
3. Esta vez: **abrí y enviá inmediatamente**, sin tocar el cuerpo

### Paso 7 — Después del envío

- Confirmá que el mail se envió (Enviados de Gmail)
- Marcá la entrega en tu tracking interno

---

## Estructura fija del mail (no cambia semana a semana)

| Sección | Contenido |
|---|---|
| **Header** | "PriceTravel · Supply Optimization" + "Week NN · HUB Supply Optimization" |
| **Lede** | 2-3 frases con titulares de impacto |
| **Saludo** | "Hola equipo," + "Compartimos en el HUB los Weekly Reports..." |
| **CTAs** | 2 botones: CheckRates (violeta) + Rates No Dispo (magenta) |
| **Credenciales** | Bloque amarillo con usuario/password |
| **Sección CheckRates** | KPIs + Top hallazgos + Plan de acción |
| **Separador** | Línea divisoria |
| **Sección Rates No Dispo** | KPIs + Top hallazgos + Análisis por canasta + Plan de acción |
| **Separador** | Línea divisoria |
| **Próximos pasos** | 4 bullets fijos |
| **CTAs (repetidos)** | Para reforzar el call-to-action |
| **Footer** | "Reciben este mail..." + "PriceTravel · Supply Optimization · Week NN..." |

---

## Reglas obligatorias

### Tipografía
- ✅ `CheckRates` (no `CK`)
- ✅ `Conv Rate` (no `CR`)
- ✅ `BKGS` (no `Bk`, `Bkgs`)
- ✅ `Canasta` (no `Canal`)
- ✅ `Casos Críticos` (no `Outliers`)

### Convención de colores
- B2C → magenta `#EA0074`
- OP → violeta `#5C469C`
- CUG → celeste `#4FC3F4`
- Deltas positivos → verde `#2E7D32`
- Deltas negativos → rojo `#C0392B`

### Privacidad de credenciales
- ✅ Las credenciales van **solo en el draft de Gmail** (inyectadas al momento)
- ❌ NO van en el archivo HTML del repo
- Si la pass cambia, actualizá las instrucciones del prompt — no el archivo del repo

---

## Destinatarios (12 personas en BCC)

```
rafael.durand@pricetravel.com
bellanira.hernandez@pricetravel.com
maria.alejandra.rico@pricetravel.com
javier.parra@pricetravel.com
alonso.mis@pricetravel.com
ingrid.kuhnne@pricetravel.com
david.gamboa@pricetravel.com
hugo.ascencio@pricetravel.com
ext.jesus.lizarraga@pricetravel.com
alejandro.flores@pricetravel.com
gabriela.guerra@pricetravel.com
barbara.rodriguez@pricetravel.com
```

Si cambian destinatarios, actualizar también `_email/destinatarios.md`.

---

## Última actualización

W17 · 28 Abril 2026 · Vol. 02
