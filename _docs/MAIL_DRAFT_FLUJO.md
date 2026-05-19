# Flujo · Envío del Mail Semanal

**Última actualización:** Mayo 2026 · post W19  
**Estado Gmail MCP:** pendiente de activación · usar flujo manual hasta entonces

---

## Flujo activo: Manual (desde browser)

### Paso 1 · Claude genera el HTML del mail

En la sesión del pipeline, después del Paso 5:

```
Mail_WNN.html generado en /mnt/user-data/outputs/
```

Descargarlo desde los outputs de Claude.

### Paso 2 · Abrir el HTML en el browser

Abrí `Mail_WNN.html` en Chrome o Firefox. Vas a ver el mail formateado completo con colores, badges QW/MP/ES y los CTAs.

### Paso 3 · Copiar el cuerpo del mail

Dentro del recuadro blanco del mail:
- **Ctrl+A** (seleccionar todo el contenido del recuadro)
- **Ctrl+C** (copiar)

> ⚠️ Seleccioná solo el área blanca del mail, no todo el HTML. El recuadro blanco es el deliverable — lo que está afuera son instrucciones de uso.

### Paso 4 · Componer en Gmail

1. Abrí **Gmail** → **Nuevo mensaje** (o **Redactar**)
2. **Para (To):** `federico.iglesias@pricetravel.com`
3. **CCO (BCC):** pegar los 15 destinatarios:

```
rafael.durand@pricetravel.com, bellanira.hernandez@pricetravel.com, maria.alejandra.rico@pricetravel.com, javier.parra@pricetravel.com, alonso.mis@pricetravel.com, ingrid.kuhnne@pricetravel.com, david.gamboa@pricetravel.com, hugo.ascencio@pricetravel.com, ext.jesus.lizarraga@pricetravel.com, alejandro.flores@pricetravel.com, gabriela.guerra@pricetravel.com, barbara.rodriguez@pricetravel.com, jordi.pena@pricetravel.com, sergio.sanchez@pricetravel.com, monica.delateja@pricetravel.com
```

4. **Asunto:** `Supply Optimization · Week NN · Resumen + Plan de Acción`
5. Hacé click en el **body del compose** y pegá **(Ctrl+V)**

El formato HTML (colores, badges, links) se mantiene al pegar desde el browser.

### Paso 5 · Validar antes de enviar

- ✅ Asunto correcto con número de semana
- ✅ BCC visible con 15 destinatarios
- ✅ Cuerpo con formato (colores violet/magenta, badges QW/MP/ES)
- ✅ CTAs apuntan a Netlify (`analytics-desk.netlify.app`)
- ✅ Links a reportes del hub funcionando
- ✅ Credenciales del hub visibles en el cuerpo (`pricetravel` / `supply2026`)

### Paso 6 · Enviar

Click **Enviar** sin tocar nada más del body. Si Gmail "limpia" el formato al hacer click adentro, cerrar sin guardar, volver al Paso 3 y esta vez pegar directamente sin editar nada.

---

## 🔐 Credenciales del Hub (incluir en el mail)

El cuerpo del mail ya incluye las credenciales dentro del bloque de detalle del Hub:

```
Hub:      https://analytics-desk.netlify.app/
Usuario:  pricetravel
Password: supply2026
```

> Si la contraseña cambia: actualizar en `render_mail_v3.py` (CONFIG SEMANAL) y en este archivo.

---

## 🔗 URLs de los reportes (Week NN)

```
Hub:  https://analytics-desk.netlify.app/
CR:   https://analytics-desk.netlify.app/checkrates/week-NN/CheckRates_Reporte_Editorial.html
RND:  https://analytics-desk.netlify.app/rates-nodispo/week-NN/RatesNoDispo_Reporte_Editorial.html
```

---

## 🗓 Calendario de envío

- **Día:** lunes (cierre semanal)
- **Hora target:** antes de las 11:00 AM Cancún (UTC-5)
- **Frecuencia:** semanal · 52 envíos al año

---

## Flujo futuro: Gmail MCP (pendiente)

Cuando el conector Gmail esté activo en Claude, el flujo reemplaza el manual:

```
Comando: "Generá el draft del mail Week NN"
```

Claude:
1. Lee `Mail_WNN.html` desde outputs
2. Extrae body entre `<!-- DRAFT_BODY_START -->` y `<!-- DRAFT_BODY_END -->`
3. Lee 15 destinatarios de `destinatarios.md`
4. Crea draft Gmail:
   - To: `federico.iglesias@pricetravel.com`
   - BCC: 15 destinatarios
   - Asunto: `Supply Optimization · Week NN · Resumen + Plan de Acción`
   - Body HTML completo
5. Devuelve Draft ID

Para activar Gmail MCP: Configuración de Claude → Conectores → Gmail → Conectar con cuenta Google.  
Soporte: https://support.claude.ai

### Pre-requisitos cuando Gmail MCP esté activo
| # | Item |
|---|---|
| 1 | `Mail_WNN.html` generado por `render_mail_v3.py` |
| 2 | Reportes publicados en Netlify |
| 3 | Conector Gmail activo en la sesión |
| 4 | `destinatarios.md` en el proyecto Claude |
