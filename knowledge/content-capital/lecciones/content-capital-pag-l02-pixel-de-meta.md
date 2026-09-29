---
title: "Content Capital · Programa · Adquisición Pagos L2 — Píxel de META"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Sistemas de Adquisición Pagos"
instructor: "Nicolás Donovan (coach de anuncios)"
lesson: 2
duration: "21:09"
date_ingested: 2026-09-25
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/pag-adquisicion-pagos/02-pixel-de-meta.md
captures_path: ~/Documents/Deliverables/General/docs/Content-Capital/capturas/programa/pag-adquisicion-pagos/02/
tags: [content-capital, cc-pag, pixel, meta-ads, anuncios, conversion, audiencias]
status: active
---

## En una línea

El píxel es una "cámara de vigilancia" que registra las acciones valiosas en la web. Se crea como **conjunto de datos** con píxel + **API de conversiones**, se instala en e-commerce (Tiendanube) o en una landing, se verifica con Events Manager y Pixel Helper, y en las landings se registran **eventos personalizados** por botón o por URL de thank you page (evento "Cliente potencial"). Instructor: **Nicolás Donovan** (00:00).

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Módulo del píxel: qué es, para qué sirve y cómo instalarlo en e-commerce y landing page. |
| 00:29 | Es un código que se pega en la web, pero conviene pensarlo como cámara de vigilancia de las acciones valiosas. |
| 01:00 | **Eventos estándar** (vienen por defecto): ver contenido, comprar, suscribirse, buscar, iniciar pago, cliente potencial, agregar información de pago, contactar, agregar al carrito. |
| 01:28 | **Eventos personalizados**: se crean a mano, p. ej. por URL. A veces no hacen falta, pero sirven para casos puntuales. |
| 01:43 | Usos: (1) públicos personalizados y similares, retargeting de quienes entraron, agregaron al carrito o compraron; (2) anuncios de conversión; (3) saber qué anuncio generó cada venta y cuánto dinero. |
| 02:29 | El proceso es igual para e-commerce y landing. Solo cambia si la página está hecha en código o en una plataforma (Tiendanube). |
| 03:01 | Administrador comercial → Orígenes de datos → Conjuntos de datos → Agregar. Nombre = negocio + fecha de creación. |
| 03:18 | Otra vez: salir de Meta Business Suite y trabajar en la configuración del Administrador comercial. |
| 03:53 | Elegir "Conectar píxel de Meta y API de conversiones" (no solo el píxel) → "Instalar código manualmente" → copiar el código. |
| 04:36 | Tiendanube: Configuración → Códigos externos → al final, sección Facebook → pegar el código y guardar. |
| 05:52 | Volver al píxel y activar **coincidencias avanzadas automáticas**. |
| 06:06 | Abrir la herramienta de configuración de eventos para verificar el tracking. |
| 06:39 | **Probar eventos**: pegar la URL de la home en Events Manager y navegar la tienda (ver producto, carrito, iniciar compra). |
| 07:41 | Aparecen ver contenido, agregar al carrito e iniciar pago: el píxel está bien instalado. |
| 08:01 | Verificación simple: extensión de Chrome **Meta Pixel Helper**. Muestra PageView, ViewContent, AddToCart, InitiateCheckout. |
| 09:09 | Comprobar que el ID del píxel que muestra Pixel Helper sea el mismo que figura en Meta. |
| 09:23 | Si los eventos no aparecen enseguida no está mal instalado: tarda en recibir datos. |
| 09:37 | **API de conversiones**: seleccionar agregar al carrito, iniciar pago, agregar información de pago, comprar, suscribirse, completar registro, contactar, programar. |
| 10:20 | Datos por evento: IP del cliente, nombre, apellido, correo y teléfono. Configurar evento por evento. |
| 11:04 | Conjunto de datos → Personas: asignarse a uno mismo y al "Conversions API System User". |
| 11:20 | La API sirve para rastrear mejor los movimientos de usuarios con Apple. |
| 11:37 | Asignar activos: vincular la cuenta publicitaria al píxel (Activos conectados → Asignar activos → Cuentas publicitarias). |
| 12:20 | **Landing page**: si está hecha en código, pedir al cliente el contacto del programador. "No busquen solucionar todo, busquen ser más eficientes." |
| 12:58 | En landings hay que configurar eventos personalizados: el píxel no siempre toma los botones como conversión. Dos opciones: botón o URL. |
| 13:18 | Ruta: Administrar eventos → Configuración → Configuración de eventos → Abrir herramienta de configuración de eventos. |
| 14:03 | **Sin thank you page**: pegar la URL de la landing, abrir el sitio web, "Registrar botón nuevo" y tocar el botón de conversión. |
| 15:22 | Evento recomendado: **Cliente potencial**. Sin checkout: "No incluir el valor". Con checkout: elegir un valor en la página. |
| 16:12 | Confirmar → Finalizar configuración. |
| 16:17 | **Con thank you page**: la URL debe contener una palabra identificable ("thank-you-page", "gracias-por-agendar", "bienvenido"). |
| 17:17 | Registrar una URL → evento Cliente potencial → regla "la URL **contiene**" (no "es igual a") + la palabra → confirmar. |
| 18:07 | Leer bien la URL para elegir qué palabra identifica la thank you page. |
| 19:18 | Cierre: Administrar eventos → Probar eventos para confirmar el tracking. |
| 19:50 | Prueba con la landing de VSL de Mati: agenda una reunión, salta a la thank you page y aparece "Cliente potencial". |
| 20:50 | Cierre. |

## Frameworks que aparecen

- [[configuracion-meta-business-y-pixel]] (nuevo)
- [[audiencias-meta-por-temperatura]] (nuevo; usos del píxel para retargeting, 01:43)
- [[metodos-y-tuberia-de-adquisicion]] (el evento Cliente potencial al agendar es el tramo de llamada del embudo a VSL; inferencia)

## Ejemplos mostrados en pantalla

- **00:16** — Portada "EL PIXEL DE META" (Google Doc).
- **03:45** — Config. de empresa → Conjuntos de datos: modal "Crear un conjunto de datos" con campo de nombre. Lista con píxeles de Mati ("Mati pixel - 02/07", etc.).
- **06:27** — Doc: "Vamos a ir nuevamente al administrador de la web > Más canales de venta > Mi tiendanube > Tocamos el apartado que dice 'Ir a mi tiendanube'".
- **09:09** — Doc: "Lo que vamos a comprobar es que en la Extensión de Pixel helper, vamos a ver que el ID del pixel que está instalado, sea el mismo ID que el que tenemos en Meta". Captura de tienda de joyas de prueba.
- **11:43** — Doc: "Nos damos acceso al pixel y también le asignamos acceso al 'Conversions API System User'. También, vamos a asignarle activos al pixel. Entonces, tocamos 'Asignar activos'".
- **13:25** — Doc: "Pueden haber 2 opciones: … un botón personalizado o una URL personalizada", más la ruta a la herramienta de configuración de eventos.
- **15:45** — Landing "[marca fitness de un cliente]" ("Transforma tu cuerpo, mejora tu vida", botón "Agenda una llamada gratis"). Pop-up "Configurar evento": tipo "Cliente potencial", "Incluir valor y divisa" con las opciones "Elegir valor en la página" y "No incluir el valor", divisa USD.
- **16:40** — Doc: "Copiamos y pegamos la URL de la Thank You Page, fíjense que esta dirección contenga palabras como 'Thank-you-page' o 'Gracias-por-agendar'. Son ejemplos, puede decir cualquier cosa…".

## Tareas y herramientas

- Crear conjunto de datos (píxel + API de conversiones), instalarlo, activar coincidencias avanzadas, configurar eventos de la API, asignar personas y activos.
- En landing: registrar un evento Cliente potencial por botón o por URL de thank you page.
- Herramientas: Events Manager (Administrador de eventos, Probar eventos), extensión Meta Pixel Helper, Tiendanube (Códigos externos).

## Citas clave

- El píxel "actúa como si fuera una cámara de vigilancia". (00:53)
- "No busquen solucionar todo, sino que busquen ser más eficientes." (12:45)
- Si los eventos no aparecen enseguida, "no es que está mal instalado". (09:25)

## Lo que no se procesó

- La configuración de la API de conversiones (09:37-11:04) se ve solo en el doc; los nombres de los eventos se toman del audio.
- La transcripción confunde "Tiendanube" ("Tiena Nubes") y "Administrador de eventos" ("menstrual de eventos").
- No se copian IDs de píxeles, negocios ni cuentas visibles en pantalla.
