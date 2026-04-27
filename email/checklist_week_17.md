# Checklist · CheckRates Week 17

Lunes 27 de abril 2026 · Ciclo 20-26 Abr

---

## ⏰ Antes de empezar

- [ ] Recibí el dataset `CheckRates_Last_7_Days_<MMDD>.xlsx` del equipo de Wholesale
- [ ] Tengo abierto el repo `Price/` en GitHub Desktop
- [ ] Estoy logueado en Gmail con `federico.iglesias@pricetravel.com`

---

## 🛠️ Generación

- [ ] **Paso 1** · Ejecutar el script de generación:
  ```bash
  cd /path/to/Price
  python scripts/prepare_week.py 17 ~/Downloads/CheckRates_Last_7_Days_<MMDD>.xlsx
  ```

- [ ] **Paso 2** · Validar los archivos generados:
  - [ ] `checkrates/week-17/Editorial/CheckRates_Reporte_Editorial.html` (~235 KB)
  - [ ] `checkrates/week-17/Analisis/Analisis_Checkrates_7d.xlsx` (~38 KB)
  - [ ] `checkrates/week-17/Templates/Template_Checkrates_Reporte.html` (~88 KB)

- [ ] **Paso 3** · Revisar visualmente el HTML editorial:
  ```bash
  open checkrates/week-17/Editorial/CheckRates_Reporte_Editorial.html
  ```
  - [ ] Hero (Week 17, fechas correctas)
  - [ ] 6 cards con datos coherentes
  - [ ] Resumen Ejecutivo con 10 bullets
  - [ ] §02 Severity Eficacia + §03 Severity Conv Rate
  - [ ] §04 Hoteles Críticos · combinado
  - [ ] §05–§08 con datos reales
  - [ ] §10 B2C, §11 B2B, §12 CUG con sub-secciones completas
  - [ ] Botones "VER EXCEL" linkean a `week-17/Analisis/...`

---

## 📤 Publicación

- [ ] **Paso 4** · Commit en GitHub Desktop:
  - Mensaje: `CheckRates · Week 17 · 20-26 Abr 2026`
  - [ ] Click en "Commit to main"
  - [ ] Click en "Push origin"

- [ ] **Paso 5** · Esperar 2-3 minutos al deploy de GitHub Pages

- [ ] **Paso 6** · Verificar URL pública:
  ```
  https://federicochurches.github.io/Price/checkrates/week-17/Editorial/CheckRates_Reporte_Editorial.html
  ```

- [ ] **Paso 7** · Actualizar la card de CheckRates en el hub Netlify (`analytics-desk.netlify.app`):
  - [ ] Apuntar al URL nuevo de Week 17

---

## 📧 Envío del email

- [ ] **Paso 8** · Generar el paquete del email:
  ```bash
  python scripts/send_email.py 17
  ```

- [ ] **Paso 9** · Abrir el archivo de links:
  ```
  email/output/checkrates_week_17_links.txt
  ```

- [ ] **Paso 10** · Copiar el primer URL (Opción A) y pegarlo en el navegador

- [ ] **Paso 11** · Gmail abre con todo pre-cargado:
  - [ ] Asunto: `Supply Optimization · Reporte CheckRates Week-17`
  - [ ] 10 destinatarios
  - [ ] Cuerpo con el link al hub
  - [ ] Sin errores tipográficos

- [ ] **Paso 12** · Apretar **Enviar**

---

## ✅ Cierre

- [ ] Confirmar recepción del email (mismo Federico recibe copia automática)
- [ ] Marcar Week 17 como ✅ Publicado en `docs/README.md` (sección "Calendario de releases")
- [ ] Cerrar la corrida

---

## 🚨 Si algo sale mal

| Problema | Solución |
|---|---|
| `prepare_week.py` falla con KeyError | Verificar que el dataset tenga las 4 pestañas: TOTALES + Canal B2C + Canal OP + Canal UOP |
| El HTML editorial muestra datos incorrectos | Revisar consola del script — los KPIs se imprimen al final |
| GitHub Pages no actualiza | Hard refresh (Cmd+Shift+R) + esperar 5 minutos extra |
| Link de Gmail abre vacío | Usar Opción B del archivo de links + pegar cuerpo manual |
| El cuerpo del mail tiene caracteres raros | Verificar que se esté usando UTF-8 en Gmail compose |

---

## 📞 Contacto

- Federico Iglesias · federico.iglesias@pricetravel.com
