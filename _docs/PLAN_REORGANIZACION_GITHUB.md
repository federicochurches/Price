#!/bin/bash

################################################################################
# PLAN DE ACCIÓN · REORGANIZAR REPO GITHUB
#
# Este documento describe paso a paso cómo reorganizar el repo GitHub
# desde la estructura actual (65+ archivos en raíz) a la nueva estructura
# (modular con _scripts/, _docs/, _helpers/, etc.)
#
# TIEMPO ESTIMADO: 30 minutos
# RIESGO: BAJO (todo está backeado)
#
################################################################################

echo "
================================================================================
📋 PLAN DE ACCIÓN · REORGANIZAR REPO GITHUB
================================================================================

OBJETIVO: Mover 59 archivos de raíz a carpetas (_scripts/, _docs/, etc.)
ESTADO ACTUAL: Raíz con 65+ archivos
ESTADO FINAL: Raíz limpia con ~3-5 archivos + 5 carpetas organizadas

================================================================================
🔄 PASO 1 · DESCOMPRIMIR ZIP EN REPO LOCAL
================================================================================

El ZIP Price_W20.zip ya tiene la estructura CORRECTA.
Solo necesitas descomprimirlo en tu repo local.

COMANDOS:

  cd /ruta/del/repo/Price
  
  # Verificar estado actual (antes)
  git status
  
  # Descomprimir ZIP (sobreescribe archivos)
  unzip -o /mnt/user-data/outputs/Price_W20.zip
  
  # Ver cambios
  git status

RESULTADO ESPERADO:
  - 59 archivos modificados/añadidos
  - Carpetas creadas: _scripts/, _docs/, _helpers/, _assets/, _config/
  - Archivos movidos de raíz a carpetas
  - index.html y otros en raíz (sin cambios)

================================================================================
📊 PASO 2 · REVISAR CAMBIOS (ANTES DE COMMITEAR)
================================================================================

REVISAR QUÉ SE MOVIÓ:

  git status

DEBERÍAS VER ALGO COMO:
  deleted: calc_rnd.py
  deleted: render_rnd_p1.py
  ...
  
  new file: _scripts/calc_rnd.py
  new file: _scripts/render_rnd_p1.py
  ...
  
  new file: _docs/PROMPT_MAESTRO_v3.md
  ...

REVISAR CAMBIOS EN DETALLE:

  git diff --name-status

VERIFICAR ESTRUCTURA NUEVA:

  ls -la _scripts/ | head
  ls -la _docs/ | head
  ls -la _helpers/ | head
  ls -la _assets/ | head
  ls -la _config/ | head

================================================================================
✅ PASO 3 · VERIFICAR QUE NO HAY PROBLEMAS
================================================================================

VERIFICAR INTEGRIDAD DE ARCHIVOS:

  # Contar archivos
  find . -type f -not -path './.git/*' | wc -l
  
  # Verificar que los archivos importantes existen
  test -f _scripts/run_pipeline.py && echo "✅ run_pipeline.py OK"
  test -f _scripts/calc_rnd.py && echo "✅ calc_rnd.py OK"
  test -f _docs/PROMPT_MAESTRO_v3.md && echo "✅ PROMPT_MAESTRO OK"
  test -f _docs/YAML_PIPELINE_GUIDE.md && echo "✅ YAML_PIPELINE_GUIDE OK"
  test -f _helpers/engine.py && echo "✅ engine.py OK"
  test -f _assets/asset_rnd_head.html && echo "✅ asset_rnd_head.html OK"
  test -f _config/WEEK_CONFIG_W21.yml && echo "✅ WEEK_CONFIG_W21.yml OK"
  test -f index.html && echo "✅ index.html OK"
  test -f README.md && echo "✅ README.md OK"

VERIFICAR QUE LOS ARCHIVOS ANTIGUOS NO ESTÁN EN RAÍZ:

  # Esto debería estar VACÍO (no encontrar archivos en raíz)
  ls -la *.py 2>/dev/null | head -5
  ls -la *.md 2>/dev/null | grep -v README | head -5

VERIFICAR ARCHIVOS EN CARPETAS:

  # Debería haber múltiples archivos aquí
  ls -la _scripts/ | wc -l
  ls -la _docs/ | wc -l

================================================================================
📝 PASO 4 · AGREGAR CAMBIOS A GIT
================================================================================

AGREGAR TODOS LOS CAMBIOS:

  git add .

VERIFICAR QUE TODO SE AGREGÓ:

  git status
  
  # Debería mostrar todos los archivos en "Changes to be committed"

AGREGAR SOLO ARCHIVOS ESPECÍFICOS (si prefieres):

  # Agregar por carpeta
  git add _scripts/
  git add _docs/
  git add _helpers/
  git add _assets/
  git add _config/
  
  # Agregar archivos eliminados de raíz
  git add -u .

================================================================================
💬 PASO 5 · CREAR COMMIT CON MENSAJE CLARO
================================================================================

OPCIÓN A · COMMIT SIMPLE:

  git commit -m "refactor: reorganizar proyecto en estructura modular

- Mover scripts a _scripts/ (calc, render, assemble, excel, build, pipeline)
- Mover documentación a _docs/ (21 documentos .md)
- Mover helpers a _helpers/ (engine, templates, helpers)
- Mover assets a _assets/ (headers, footers, guías)
- Mover config a _config/ (WEEK_CONFIG_*.yml)
- Mantener checkrates/, rates-nodispo/, _governance/, _email/ sin cambios
- Actualizar imports en 15 scripts
- Limpiar raíz (de 65+ a ~3-5 archivos)
- Agregar documentación YAML (YAML_PIPELINE_GUIDE, etc.)
- Agregar script bash (regenerate_zip.sh)

New structure ready for W21+ YAML automation pipeline."

OPCIÓN B · COMMIT CON BREAKING CHANGE (si prefieres):

  git commit -m "refactor!: reorganizar proyecto estructura modular

BREAKING CHANGE: Archivos movidos a carpetas (se mantiene compatibilidad)

- Scripts: / → _scripts/
- Docs: / → _docs/
- Helpers: / → _helpers/
- Assets: / → _assets/
- Config: / → _config/

Agrega YAML automation pipeline (W21+ ready).
Estructura limpia y profesional para GitHub.

Closes #ISSUE_NUMBER"

OPCIÓN C · SQUASH COMMITS (si hay muchos cambios previos):

  git rebase -i HEAD~N  # N = número de commits a squash
  # Luego marca como "squash" los commits a combinar

================================================================================
🚀 PASO 6 · PUSH A GITHUB
================================================================================

VERIFICAR QUE NO HAY CONFLICTOS:

  git log origin/main..main  # Commits locales no pusheados
  git status

PUSH A MAIN:

  git push origin main

PUSH A RAMA ALTERNATIVA (si quieres revisión primero):

  git push origin -u feature/reorganize-structure
  # Luego crear Pull Request en GitHub

VERIFICAR EN GITHUB:

  # Abre en navegador:
  https://github.com/federicochurches/Price
  
  # Debería verse:
  - Raíz limpia (index.html, README.md, .gitignore)
  - Carpetas: _scripts/, _docs/, _helpers/, _assets/, _config/
  - Carpetas existentes: checkrates/, rates-nodispo/, _governance/, _email/

================================================================================
🔍 PASO 7 · VERIFICAR CAMBIOS EN GITHUB
================================================================================

EN GITHUB WEB:

  1. Ve a https://github.com/federicochurches/Price
  
  2. Verifica que en raíz solo hay:
     ✅ index.html
     ✅ README.md
     ✅ .gitignore
     
  3. Verifica que hay carpetas nuevas:
     ✅ _scripts/
     ✅ _docs/
     ✅ _helpers/
     ✅ _assets/
     ✅ _config/
     
  4. Verifica que cada carpeta tiene sus archivos:
     _scripts/ → 25 archivos (calc_rnd.py, render_*.py, etc.)
     _docs/ → 21 documentos (.md)
     _helpers/ → 7 helpers (engine.py, template_*.py, etc.)
     _assets/ → 8 assets (asset_*.html, GUIA_*.html)
     _config/ → 2 configs (WEEK_CONFIG_*.yml)

VERIFICAR EN COMMITS:

  git log --oneline | head -5
  
  Debería mostrar tu nuevo commit al top

VERIFICAR CAMBIOS:

  https://github.com/federicochurches/Price/commit/[HASH]
  
  Debería mostrar +59 -59 (reorganización)

================================================================================
⚠️ SI ALGO SALE MAL · ROLLBACK
================================================================================

DESHACER ÚLTIMO COMMIT (local, no pushed):

  git reset --soft HEAD~1   # Mantiene los cambios
  git reset --hard HEAD~1   # Descarta los cambios (⚠️ DESTRUCTIVO)

DESHACER PUSH (después de push):

  git revert HEAD  # Crea un nuevo commit que deshace el anterior
  git push origin main

RESTAURAR DESDE BACKUP:

  # Si tienes backup local del repo
  cd /ruta/backup
  git checkout -f main
  
  # O espera a que GitHub guarde la historia
  git reflog  # Ver todos los cambios históricos

================================================================================
✅ CHECKLIST FINAL
================================================================================

ANTES DE PUSH:
  [ ] Descomprimió ZIP en repo local
  [ ] Revisó cambios con git status
  [ ] Verificó que archivos correctos están en carpetas
  [ ] Verificó que raíz está limpia
  [ ] Agregó cambios con git add .
  [ ] Creó commit descriptivo
  [ ] Verificó que no hay merge conflicts

DESPUÉS DE PUSH:
  [ ] Push completado sin errores
  [ ] Verificó en GitHub que estructura es correcta
  [ ] Verificó que commits aparecen en GitHub
  [ ] Verificó que ramas están sincronizadas

LISTO PARA W21:
  [ ] Estructura reorganizada en GitHub
  [ ] ZIP nuevo descargado localmente
  [ ] Está listo para ejecutar W21 sin cambios

================================================================================
🎯 RESUMEN RÁPIDO
================================================================================

COMANDO ÚNICO (después de descomprimir):

  cd /ruta/del/repo/Price
  unzip -o /mnt/user-data/outputs/Price_W20.zip
  git add .
  git commit -m \"refactor: reorganizar proyecto estructura modular\"
  git push origin main

TIEMPO: ~5 minutos (si todo va bien)

RESULTADO: 
  ✅ Repo GitHub con estructura profesional
  ✅ 59 archivos reorganizados
  ✅ Raíz limpia (3-5 archivos vs 65+)
  ✅ Listo para W21+

================================================================================

¿PREGUNTAS O DUDAS?

Si algo no sale bien:
  1. Revisa el PASO en el que estés atascado
  2. Verifica que ejecutaste el comando exactamente
  3. Si nada funciona, puedes hacer rollback (PASO 7)
  4. El repo GitHub siempre tiene history, no se pierde nada

================================================================================
"
