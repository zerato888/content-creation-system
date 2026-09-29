# Hooks del harness: dos reglas duras

Un *hook* del harness es un comando que el programa (no el modelo) ejecuta en un evento del ciclo de vida:
al iniciar la sesión, antes o después de una herramienta, al enviar un prompt, al cerrar. Se configuran en JSON
(`.claude/settings.json` para el proyecto; el archivo global, para toda la máquina). Ver `hooks/README.md` del kit.

## Regla 1: un hook global de "prompt enviado" falla abierto, sin excepción
Corre en **cada** prompt de **cualquier** carpeta. Si sale con un código distinto de 0, puede bloquear todos los
prompts de la máquina. Ante entrada inválida (JSON malformado, campo faltante, error propio): una advertencia por
stderr, **no tocar nada y salir con 0**. Su salida estándar se agrega como contexto y no pisa el prompt.

## Regla 2: un modo persistente necesita un hook, no una skill
Una skill es texto que se lee una vez: no sostiene estado entre turnos y el "modo activado" se desvanece sin aviso.
El patrón que funciona (`/modo on|off`):
- El hook interpreta el comando con coincidencia **exacta** del prompt recortado, para que un texto pegado que lo
  mencione no cambie el estado.
- Escribe un archivo de estado y **reinyecta el contrato completo** en cada turno.
- El estado va **por identificador de sesión**: varias sesiones a la vez se contaminarían con un archivo único. El
  identificador se valida (forma de UUID) antes de usarlo como nombre de archivo.
- Nada de limpieza por antigüedad: borraría el modo de una sesión viva pero quieta.

## Otras notas
- Un hook de tipo `prompt` solo es válido en eventos que ya tienen conversación (por ejemplo, después de compactar
  o al cerrar); en el inicio de sesión usá un hook de tipo comando.
- Los hooks del proyecto en Codex no corren hasta que se revisan y se confían con `/hooks`; la confianza se ata al
  contenido, así que hay que repetirla tras cada edición y en cada máquina.
- Una regla que solo vive en un archivo de instrucciones se ignora en silencio; si algo tiene que cumplirse
  siempre, se hace cumplir con un hook.
