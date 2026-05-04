# Flujo · Generación del Draft del Mail Semanal

**Vigente desde:** Week 19 (mayo 2026)  
**Reemplaza:** flujo W17 con preview manual + KPIs pegados en chat  
**Aprobado por:** Federico, sesión 4-may-2026

---

## 🎯 Comando único

Para generar el draft semanal en Gmail, en una nueva conversación con Claude:

```
Generá el draft del mail Week NN
```

(reemplazá `NN` por el número de semana)

---

## ⚙️ Qué hace Claude internamente

1. **Lee el body fuente:** `_email/week-NN/Mail_WNN.html` (generado previamente por `render_mail_v3.py` con datos del pickle)
2. **Extrae el body HTML** entre los marcadores `<!-- DRAFT_BODY_START -->` y `<!-- DRAFT_BODY_END -->`
3. **Lee destinatarios** desde `destinatarios.md` (lista de 14 mails)
4. **Inyecta credenciales del hub** (Netlify) que NO viven en el archivo HTML del repo, solo en el draft
5. **Llama a `Gmail:create_draft`** con:
   - To: `federico.iglesias@pricetravel.com`
   - BCC: 14 destinatarios
   - Asunto: `Supply Optimization · Week NN · Resumen + Plan de Acción`
   - HTML body completo
6. **Devuelve el Draft ID** para confirmar

---

## 📋 Pre-requisitos antes de pedir el draft

| # | Item | Cómo validar |
|---|---|---|
| 1 | Pickles generados | `calc_cr.py` y `calc_rnd.py` ya corridos |
| 2 | Mail HTML generado | existe `_email/week-NN/Mail_WNN.html` |
| 3 | Reportes publicados en Netlify | URLs del hub funcionando |
| 4 | Conector Gmail conectado en Claude | tools `Gmail:create_draft` disponible |
| 5 | `destinatarios.md` actualizado | 14 mails confirmados |

Si falta el item 2, primero correr:
```bash
python render_mail_v3.py
```

---

## 🔧 Cambios técnicos requeridos en `render_mail_v3.py`

Para que el flujo sistémico funcione, el archivo `Mail_WNN.html` debe tener estos marcadores HTML al inicio y fin del body real (lo que va dentro del recuadro blanco del preview):

```html
<!-- DRAFT_BODY_START -->
<h1>Supply Optimization · Week NN</h1>
...
<div class="footer">...</div>
<!-- DRAFT_BODY_END -->
```

Esto permite a Claude extraer el body sin parsear depth de divs (que es frágil).

**TODO Week 19:** modificar `render_mail_v3.py` para que escriba estos marcadores automáticamente al inicio/fin del bloque que va dentro de `.mail-body`.

---

## 🔐 Credenciales del Hub

El hub Netlify requiere login. Las credenciales se inyectan en un bloque amarillo dentro del draft:

```
Usuario:  pricetravel
Password: supply2026
```

> Estas credenciales viven SOLO en el draft (inyectadas al momento), nunca en el archivo HTML del repo. Si la pass cambia, actualizar `_governance/MAIL_DRAFT_FLUJO.md` (este archivo) y el snippet en `render_mail_v3.py`.

---

## 🔗 URLs del mail

Los CTAs apuntan al hub Netlify (con login) y a los reportes editoriales:

```
Hub:     https://analytics-desk.netlify.app/
CR:      https://analytics-desk.netlify.app/checkrates/week-NN/CheckRates_Reporte_Editorial.html
RND:     https://analytics-desk.netlify.app/rates-nodispo/week-NN/RatesNoDispo_Reporte_Editorial.html
```

> **Nota:** GitHub Pages (`federicochurches.github.io/Price`) es el repositorio fuente para edición y backup, pero el hub público para el equipo es Netlify con login.

---

## 📤 Después del draft

1. Abrir Gmail → Borradores
2. Buscar el draft con asunto `Supply Optimization · Week NN · Resumen + Plan de Acción`
3. **NO hacer click adentro del cuerpo** (Gmail puede limpiar el HTML)
4. Validar:
   - ✅ Asunto correcto
   - ✅ BCC con 14 destinatarios
   - ✅ Cuerpo con formato (colores violet/magenta, badges QW/MP/ES)
   - ✅ Bloque amarillo de credenciales visible
   - ✅ CTAs apuntan a Netlify (no GitHub Pages)
5. Click **Enviar** sin tocar nada más

---

## 🚨 Si el formato se rompe al abrir el draft

Gmail a veces "limpia" el HTML cuando hacés click adentro del cuerpo. Si pasa:

1. Cerrar el draft sin guardar
2. Pedir a Claude: `Regenerá el draft del mail Week NN`
3. Esta vez: abrir y enviar inmediatamente, sin tocar el cuerpo

---

## 📝 Variantes del comando

| Comando | Resultado |
|---|---|
| `Generá el draft del mail Week NN` | Crea draft con datos del pickle/HTML existente |
| `Mostrame el preview del mail Week NN` | Solo muestra screenshot del body, no crea draft |
| `Regenerá el draft Week NN` | Sobrescribe (en realidad crea uno nuevo) |
| `Listame los drafts pendientes` | Usa `Gmail:list_drafts` |

---

## 🗓 Calendario de envío

- **Día:** lunes (cierre semanal)
- **Hora target:** antes de las 11:00 AM Cancún (UTC-5)
- **Frecuencia:** semanal · 52 envíos al año
