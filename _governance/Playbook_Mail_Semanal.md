# Playbook Semanal · Mail Supply Optimization

Guía operativa para el envío del mail unificado cada lunes (cierre semanal).

**Vigente desde:** Week 19 (mayo 2026)  
**Reemplaza:** versión W17 con preview iterativo y KPIs pegados en chat

---

## ⏱ Tiempo estimado: 5 minutos

(antes era 10-15 minutos · el flujo nuevo elimina la iteración manual del preview)

---

## ✅ Antes de empezar — checklist

- [ ] Reportes CheckRates y RatesNoDispo de la semana publicados en Netlify
- [ ] URLs funcionando:
  - `https://analytics-desk.netlify.app/checkrates/week-NN/CheckRates_Reporte_Editorial.html`
  - `https://analytics-desk.netlify.app/rates-nodispo/week-NN/RatesNoDispo_Reporte_Editorial.html`
- [ ] Pipeline ya generó `Mail_WNN.html` en `_email/week-NN/`
- [ ] Conector Gmail conectado en Claude (verificar herramienta `Gmail:create_draft`)

---

## 🚀 Workflow

### Paso 1 — Abrir Claude

Abrir nueva conversación en claude.ai con acceso al proyecto PRICE.

### Paso 2 — Comando único

Pegale a Claude:

```
Generá el draft del mail Week NN
```

(reemplazá `NN` por el número de semana actual)

Claude internamente:
1. Lee `_email/week-NN/Mail_WNN.html` desde el proyecto
2. Extrae el body HTML entre marcadores `<!-- DRAFT_BODY_START -->` y `<!-- DRAFT_BODY_END -->`
3. Lee los 14 destinatarios desde `destinatarios.md`
4. Inyecta credenciales del hub Netlify (`pricetravel` / `supply2026`)
5. Llama a `Gmail:create_draft` con el HTML completo
6. Devuelve el Draft ID

### Paso 3 — Verificar en Gmail

1. Andá a `gmail.com → Borradores`
2. **Abrí el draft** (asunto: `Supply Optimization · Week NN · Resumen + Plan de Acción`)
3. **NO hagas click adentro del cuerpo del mail** (Gmail tiende a "limpiar" el HTML)
4. Verificá:
   - ✅ Asunto correcto
   - ✅ BCC con 14 destinatarios
   - ✅ Cuerpo con formato (colores violet/magenta, badges QW/MP/ES, links)
   - ✅ Bloque amarillo de credenciales visible
   - ✅ CTAs apuntan a `analytics-desk.netlify.app/...`
5. Si todo OK → click en **Enviar** sin tocar nada más

### Paso 4 — Si el formato se rompe

1. **Cerrá sin guardar**
2. Pedile a Claude: `Regenerá el draft del mail Week NN`
3. Esta vez: **abrí y enviá inmediatamente**, sin tocar el cuerpo

### Paso 5 — Después del envío

- Confirmá que el mail se envió (Enviados de Gmail)
- Marcá la entrega en tu tracking interno (si aplica)

---

## 🗂 Variantes del comando

| Comando | Resultado |
|---|---|
| `Generá el draft del mail Week NN` | Crea draft con datos del pickle/HTML existente |
| `Mostrame el preview del mail Week NN` | Solo screenshot del body, NO crea draft |
| `Regenerá el draft Week NN` | Crea draft nuevo (no modifica el viejo) |
| `Listame los drafts pendientes` | Usa `Gmail:list_drafts` |

---

## 🔄 Flujo viejo W17 (deprecado)

> Antes pegabas KPIs en chat, Claude iteraba preview, vos validabas cada vuelta antes de crear el draft.
> 
> El nuevo flujo asume que `render_mail_v3.py` ya generó el HTML correcto desde el pickle. Si necesitás cambiar contenido del mail (KPIs, copy, plan), tocá `render_mail_v3.py` o el HTML directamente y re-pedí el draft.

---

## 📋 Estructura fija del mail (no cambia semana a semana)

| Sección | Contenido |
|---|---|
| **Header** | "Supply Optimization · Week NN" + "fecha · Vol. NN" |
| **Saludo** | "Hola equipo," + intro al formato |
| **Bloque credenciales** | Amarillo · usuario `pricetravel` · password `supply2026` |
| **Glosario** | Bloque violeta · cambio RPM/GBM (post W18) |
| **Resumen Ejecutivo** | 3 párrafos: RND · CR · Foco de la semana |
| **Plan de Acción consolidado** | Por Área Accountable v2 (4 áreas) · QW · MP · ES |
| **Detalle en el Hub** | 3 CTAs: Hub · CR · RND |
| **Próximos pasos** | Próxima publicación + invitación a feedback |
| **Footer** | "Recibís este mail..." + firma con week/vol |

---

## 🎨 Reglas tipográficas

- ✅ `CheckRates` (no `CK`)
- ✅ `Conv Rate` (no `CR` para la métrica)
- ✅ `BKGS` (no `Bk`, `Bkgs`)
- ✅ `Canasta` (no `Canal`)
- ✅ `% de No Disponibilidad` (no `%NoDispo` en texto narrativo)
- ✅ `RPM` (Reservas Por Millón) y `GBM` (Gross Booking USD/M) como métricas separadas

## 🎨 Convención de colores

- B2C → magenta `#EA0074`
- OP → violet `#5C469C`
- CUG → cyan `#4FC3F4`
- Deltas positivos → verde `#2F6C34`
- Deltas negativos → rojo `#C0392B`

---

## 🔐 Credenciales

- ✅ Las credenciales del hub van **solo en el draft de Gmail** (inyectadas por Claude al momento)
- ❌ NO van en el archivo HTML del repo
- Si la pass cambia, actualizar `_governance/MAIL_DRAFT_FLUJO.md` y avisar en próximo mail

---

## 📬 Destinatarios (14 personas en BCC)

Ver `destinatarios.md` para la lista actualizada. Si cambian destinatarios, editar ese archivo y Claude leerá la nueva lista en el próximo draft.

---

## 🗓 Calendario

- **Día:** lunes (cierre semanal)
- **Hora target:** antes de las 11:00 AM Cancún (UTC-5)
- **Frecuencia:** semanal · 52 envíos al año

---

## Última actualización

W18 · 4 mayo 2026 · Vol. 04 · flujo `Gmail:create_draft` MCP
