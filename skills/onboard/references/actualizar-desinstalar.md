# Actualizar y desinstalar el kit

Los dos comandos se corren desde la **carpeta del kit** (la que tiene `install.sh` e
`install.ps1`), apuntando `--target` al proyecto. Preguntá dónde está esa carpeta; si ya no la
tiene, que descargue el kit de nuevo desde la página del proyecto.

- macOS: `./install.sh <comando> --target "/ruta/al/proyecto"`
- Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 <comando> --target "C:\ruta\al\proyecto"`

## "Actualizá el kit" → `update`
1. Corré `update` (opcional `--to v0.2.0`). Muestra el commit exacto (un código largo), el
   registro de cambios y la lista de archivos que cambian.
2. Pedile a la persona que compare ese código con el publicado en las notas de la versión y que
   **ella** confirme. No lo confirmes por ella.
3. Para cada archivo del kit que modificó, elige: **conservar el mío** (pasa a ser suyo y el kit no
   lo vuelve a tocar) o **tomar el nuevo** (su versión se guarda en `.kit/backup/<fecha>-<id>/`).
4. Lo que ya no está en la versión nueva se borra con copia previa. `.kit-personal/` nunca se toca.
5. Si algo sale mal a mitad de camino, el próximo comando deshace lo incompleto. `rollback`
   deshace la última operación terminada.

## "Desinstalá el kit" → `uninstall`
- Borra exactamente los archivos que instaló el kit (los de `.kit/manifest.json`) y el bloque entre
  marcadores de `CLAUDE.md`, `AGENTS.md` y `.gitignore`.
- Quedan intactos: `.kit-personal/`, todo lo que está fuera de los marcadores, archivos del kit que
  la persona modificó (se avisan), `.kit/backup/` y `.kit/install.log`.
- La caché compartida de modelos y navegadores se borra aparte con `cache-clean`.

## Otros
- `status`: qué hay instalado y qué modificó la persona.
- `migrate-brands`: actualiza el formato de `.kit-personal/brands/*.json`, con copia previa.
