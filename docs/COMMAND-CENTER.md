# Command Center

## Instalación

El Command Center no es una skill: no aparece en `catalog.json` (que solo lista skills y roles) y
no se elige. Viene siempre con el kit: el instalador copia la carpeta `cc/` entera (menos sus
pruebas) a `.kit/cc/`. El onboarding escribe tu configuración en `.kit-personal/cc.config.json`
partiendo de `.kit/cc/config/defaults.json` y tus respuestas (marcas, marca personal, Vida
Personal, zona horaria, partes prendidas, meta semanal). Nunca guarda claves.

### Siempre encendido (opcional, con tu permiso)

```
./install.sh service on --target <tu proyecto>      # Windows: .\install.ps1 service on --target ...
./install.sh service status --target <tu proyecto>
./install.sh service off --target <tu proyecto>
```

- Mac: un LaunchAgent en `~/Library/LaunchAgents/com.contentkit.cc.<id del proyecto>.plist`.
  Arranca al iniciar sesión y `KeepAlive` lo vuelve a levantar si se cae.
- Windows: una tarea programada al iniciar sesión con el mismo nombre, que se reinicia sola si falla.
- Corre `python .kit/launch.py serve --no-print-url` (con `.kit/venv` si existe). Es lo único
  que el kit escribe fuera del proyecto; queda anotado en `.kit/manifest.json` y `uninstall` lo quita.
- Mientras corre, `update` y `uninstall` esperan: `uninstall` apaga el servicio primero (te pregunta).

## Backend (el servidor)

### Qué es

Un programa chico que corre en tu computadora y le da datos a las pantallas del
Command Center: tus tareas, tus guiones, el Content Lab, tu racha semanal y tu
Vida Personal. No usa internet salvo que prendas las métricas conectadas. Solo
usa Python, sin librerías extra.

### Dónde vive cada cosa

- Tu configuración: `.kit-personal/cc.config.json`. Es tuya: el kit nunca la pisa.
- Tus datos: `.kit-personal/data/` (tareas, vida, racha, Lab y guiones).
- El programa: `.kit/cc/server/` y las reglas de la configuración en `.kit/cc/config/`.
- Las pantallas: `.kit/cc/web/` (en el repo, `cc/web/`).

### Cómo se prende

```
python .kit/launch.py serve
```

Imprime un enlace para abrir en el navegador. Ese enlace sirve **una sola vez** y
**vence en 60 segundos**. Si ya está corriendo de fondo, pedí un enlace nuevo con:

```
python .kit/launch.py open --browser
```

### Tu configuración

Todo lo personal está en `cc.config.json`, nunca en el código. Si falta un dato,
se usa el valor por defecto. Si un dato está mal escrito, se ignora ese dato (y
solo ese) y la pantalla de salud avisa cuántos ignoró. Nunca se rompe.

- `brands`: tus marcas. Cada una tiene `id`, `name`, `task_prefix` (letras de las
  tareas, por ejemplo `CAN` da `CAN-1`), `accent` (color), `logo`, `kind`
  (`brand` o `personal-brand`) y un conector de métricas opcional.
- `toggles`: qué partes están prendidas. Por defecto solo Vida Personal y lo básico
  de creador. Apagadas: `agentic` (mapa del Agentic OS), `produccion_avanzada`,
  `biblioteca`, `metricas`, `marcas_extra` (tus otras marcas) y `subtitulos`
  (Estudio de subtítulos). Se prenden y apagan desde el botón «Módulos» de la pantalla,
  sin recargar: ese botón cambia solo `toggles` en tu archivo y deja todo lo demás igual.
- `vida`: moneda, tipo de cambio, meta de ingreso, hábitos (con sus días),
  pagos fijos, ingresos fijos e hitos. Todo empieza vacío.
- `locale`: zona horaria, idioma y formato de fecha. "Hoy" sigue tu zona horaria.
- `creator`: meta semanal de videos (3) y días de gracia (1).

Cambiar la configuración no pide reiniciar: el servidor la vuelve a leer sola.
Una parte apagada responde "no existe", igual que una dirección inventada.

### La racha semanal

Cada vez que tocás «Ya grabé» suma un video a tu semana (de lunes a domingo). La
semana está cumplida con 3 videos (o tu meta). La racha cuenta semanas cumplidas
seguidas. Si un video se te pasa al lunes y era justo el que le faltaba a la
semana anterior, cuenta para esa semana (eso es el día de gracia). La semana en
curso nunca te rompe la racha mientras todavía podés cumplirla.

Después de publicar, anotás las vistas a las 48 horas. El domingo, el sistema te
dice qué hook ganó esa semana.

### Traducción fiel (marca personal)

Cuando pegás una referencia en otro idioma, el sistema prepara un paquete con el
texto original y una regla estricta: traducir fiel, sin giro, sin agregar ni
quitar ideas y sin meter la voz de nadie. El agente escribe la traducción y el
servidor solo acepta los campos permitidos; si viene algo de más, no guarda nada.

### Seguridad (lo que hace solo)

- Solo escucha en tu propia computadora (`127.0.0.1`). Nadie de tu red lo ve.
- El puerto lo elige el sistema y queda anotado en `.kit/cc.port`.
- Sin el enlace de un solo uso no entra nadie; después usa una cookie de sesión
  que el navegador no deja leer a otras páginas.
- Otra página abierta en tu navegador no puede cambiar tus datos: los cambios
  exigen que el pedido venga de la propia pantalla del Command Center.
- Ningún pedido puede leer ni escribir fuera de tus carpetas de datos.
- Tus claves de Metricool o Zernio se guardan en el llavero del sistema, nunca en
  archivos, y el servidor no las muestra ni las anota.

### Métricas conectadas (opcional)

Prendé `metricas` y en la marca poné el conector:

- Metricool: `"metrics": {"provider": "metricool", "account": {"blog_id": "...", "user_id": "..."}}`
  y la clave `METRICOOL_API_KEY` en el llavero (ver `engines/kit_secrets.py`).
- Zernio: `"metrics": {"provider": "zernio", "account": {"handle": "@tu.cuenta"}}`
  y la clave `ZERNIO_API_KEY`.

Sin conector, cargás las vistas a mano.

### Para quien programa

- Tareas por consola: `python -m cc.server.tasks --target . add "Grabar intro" --ecosystem <id-de-marca>`
  (con `.kit` como carpeta actual). Las marcas y prefijos salen de la configuración;
  una marca nueva no necesita migrar nada. `vida` es el espacio fijo de Vida Personal.
- Hitos por marca: tareas de esa marca con `area` = `hito`.
- Rutas: `GET /api/status`, `/api/config`, `/api/tasks`, `/api/guiones`,
  `/api/lab/items?brand=`, `/api/creator/summary`, `/api/life/*`… Todo cambio es
  `POST` con JSON. La lista completa está en `GET_ROUTES` y `POST_ROUTES` de
  `.kit/cc/server/app.py`, con el módulo al que pertenece cada una.
- Pruebas: `python -m pytest -q tests/test_cc_*.py`.

## Pantallas (la interfaz)

### Qué ves

El menú se arma solo con tu configuración: no hay marcas escritas en el código.

- **Inicio**: tu racha semanal, qué hacer ahora, tus videos grabados (ahí anotás las
  vistas a las 48 horas) y el hook que ganó la semana.
- **Ideas y Content Lab**: pegás un link o una transcripción, tu agente escribe el
  análisis y la traducción fiel, y vos editás tu versión. En «Mis ideas» anotás las tuyas.
- **Guion y grabación**: compositor con 3 estructuras y el banco de hooks, 3 versiones del
  hook, teleprompter (se abre en otra pestaña) y el botón «Ya grabé».
- **Tablero**: Idea / Guion listo / Publicado. El modo avanzado agrega la columna Grabado.
- **Una pantalla por marca**: tareas, hitos (tareas con `area` = `hito`) y, con `metricas`
  prendido, las métricas conectadas.
- **Vida Personal**: ingresos contra tu meta, pagos fijos, compras, metas; tareas, hábitos
  de la semana, constancia de 30 días e hitos.
- Con su interruptor: **Producción** (`produccion_avanzada`), **Biblioteca** (`biblioteca`)
  **Agentic OS** (`agentic`) y **Estudio de subtítulos** (`subtitulos`). Se prenden desde «Módulos»
  y el menú cambia al instante.
- **Estudio de subtítulos**: copiá tus clips en `.kit-personal/data/captions/`, transcribilos (Whisper,
  en tu compu), corregí palabras, elegí base y hook (el hook puede ir en 2 o 3 líneas parejas, con
  tamaño y espacio por línea), mirá la vista previa sobre el video y exportá: subtítulos `.srt`,
  el video con subtítulos puestos, o (avanzado) una capa transparente ProRes 4444. Las exportaciones
  quedan en `out/` dentro de esa carpeta y tus presets en `presets/`. Exportar video pide ffmpeg con
  libass; si falta, el estudio lo dice.

Moneda, idioma y zona horaria salen de tu configuración. Si la configuración tiene datos
que se ignoraron, arriba aparece un aviso con la lista.

### Para quien programa

- Código en `cc/web/` del repo; se instala en `.kit/cc/web/`, que es la única carpeta que
  el servidor publica.
- Módulos ES sin librerías: `app.js` (menú y rutas por `#vista`), `lib.js` (ayudas),
  `views/*.js` (una por pantalla, cada una exporta `render(root, ctx)`), `teleprompter.*`.
- Seguridad: cero scripts o estilos en línea (CSP `'self'`); todo texto va con
  `textContent`/`value`; no se arma HTML con strings. `tests/test_cc_ui_static.py` lo
  revisa, y `tests/test_cc_ui_serve.py` levanta el servidor real con la interfaz.
- Tipografías: JetBrains Mono y Sora (OFL). `install --fonts` las baja (con tu permiso, hash
  fijado en `presets/captions/fonts.lock.json`) a `.kit/fonts/`, y el servidor las sirve en
  `/fonts/<archivo>.woff2` (solo woff2, solo esa carpeta). Sin ellas, usa las del sistema.
- Banco de hooks: `GET /api/hooks-bank` lee `.kit/presets/hooks/hooks-bank.json`.
- Logos: en la pantalla de cada marca, «Subir logo» (PNG, JPG o WEBP, hasta 1 MB; se revisa el
  contenido, no el nombre). Se guarda en `.kit-personal/data/logos/` y se sirve en
  `GET /api/brand/logo?brand=<id>`. Sin logo, se muestran las iniciales.
- Guion ↔ tarjeta: «Escribir guion» desde una idea guarda el código de la tarjeta (`task_code`) en
  el guion; «Ya grabé» mueve esa tarjeta, aunque cambies el título. Los guiones viejos sin código
  siguen funcionando.
