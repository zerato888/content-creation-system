---
title: "Configuración de Meta Business, píxel y API de conversiones (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-pag-l01, cc-pag-l02, cc-pag-l03, cc-pag-l05, cc-pag-l09, cc-pag-l13]
source_count: 6
created: 2026-09-25
updated: 2026-09-25
tags: [content-capital, cc-pag, framework, checklist, plantilla, anuncios, meta-ads, pixel, conversion, adquisicion]
status: developing
---

## En una línea

Antes de gastar un dólar en anuncios, se arma la base en el **Administrador comercial** (fanpage → cuentas vinculadas → portfolio → cuenta publicitaria → pago → 2FA), se instala el **píxel junto con la API de conversiones**, se registra la conversión real de la landing y se mantiene el conjunto de datos actualizado (atribución, dominios autorizados, dominio verificado).

## Qué es y por qué funciona (según el curso)

- **Administrador comercial, no "Promocionar".** El botón Promocionar solo segmenta por intereses, no deja elegir objetivo ni testear conjuntos, es más caro y trae seguidores de baja calidad ([[content-capital-pag-l01-introduccion-publicidad-paga|PAG L1]] 03:56–04:27).
- **Meta Business Suite "funciona muy pero muy mal"**: se configura desde business.facebook.com → Administrador comercial. Se distinguen por el título de la pestaña (PAG L1 15:48–16:45; repetido en [[content-capital-pag-l02-pixel-de-meta|PAG L2]] 03:18 y [[content-capital-pag-l05-audiencias|PAG L5]] 23:37).
- **La cuenta publicitaria es escasa**: Meta "ya casi no da cuentas nuevas", hay que cuidarla "como oro". País, divisa y zona horaria no se pueden cambiar después (PAG L1 23:47, 26:03).
- **Datos reales = menos baneos.** Una fanpage completa y la información del negocio cargada permiten que Meta verifique que la empresa es real (PAG L1 07:16–10:45, 37:30). Sin 2FA, Meta "no te va a parar de perseguir" (PAG L1 34:20).
- **El píxel es una "cámara de vigilancia"** de las acciones valiosas en la web (PAG L2 00:53). Sirve para tres cosas: públicos personalizados y similares (retargeting), anuncios de conversión y saber qué anuncio generó cada venta (PAG L2 01:43).
- **La API de conversiones** es la conexión directa web–Meta. Existe porque Apple dejó elegir no ser rastreado por el píxel; recupera esos eventos (PAG L1 49:45–50:44; PAG L2 11:20).
- **Mandar a Meta solo el lead calificado** hace que la campaña busque ese perfil. Nico Bartolomé lo hace con el evento Schedule filtrado desde GoHighLevel ([[content-capital-pag-l09-proceso-pre-call-automatizaciones|PAG L9]] 17:40–28:30).

## Cuándo usarlo / cuándo no

- **Siempre**, antes de la primera campaña propia o de un cliente. Sin píxel alimentado no hay lookalikes ni retargeting (PAG L5 37:10).
- **Cuándo repasar**: cuando aparecen eventos duplicados o datos que llegan de dominios ajenos, se hace la "actualización" del píxel ([[content-capital-pag-l03-actualizacion-en-el-pixel|PAG L3]] 00:00–00:26).
- **Filtro de lead calificado**: cuando la landing tiene un formulario con preguntas de calificación. Con pocos datos por mes no conviene disparar la API recién después de la llamada: con 15-30 eventos al mes Meta no optimiza (PAG L9 67:00, según el resumen de la lección).
- **No usar** el botón Promocionar salvo para ganar seguidores ("Visitar perfil") (PAG L1 04:27).
- **Frontera del rol**: el *trafficker* configura, crea y optimiza campañas, reporta y asesora el copy. No crea contenido, no gestiona redes, no contesta DMs ni edita (PAG L1 01:34–02:06). Ver [[modelos-de-servicio-dfy-dwy-diy]].

## Pasos

1. **Requisitos**: Facebook personal, una página donde seas administrador e Instagram profesional (PAG L1 06:51).
2. **Fanpage completa**: web, teléfono, mail, ubicación, horarios, foto de perfil y portada (PAG L1 07:16–10:45).
3. **Vincular WhatsApp Business** (el personal no deja) **e Instagram** desde Panel para profesionales → Configuración → Cuentas vinculadas (PAG L1 10:45–13:35).
4. **Crear un portfolio comercial** en business.facebook.com → Administrador comercial. No usar la cuenta publicitaria personal; hay un límite de portfolios por persona (PAG L1 13:44–17:25).
5. **Cargar los activos**, primero los marcados en rojo (obligatorios): personas, páginas, cuentas publicitarias, Instagram, WhatsApp, conjuntos de datos, dominios, pagos (PAG L1 17:27–18:05). Cuidado con dar **control total** a un socio: puede borrar el portfolio y tocar las tarjetas (PAG L1 18:22). Si la página ya la tiene otro negocio, pedirle que la desvincule (PAG L1 22:12).
6. **Crear la cuenta publicitaria** con país, zona horaria y divisa igual a la del medio de pago; asignarla al Instagram y a las personas (PAG L1 23:19–26:03, 30:36). Si falla la conexión, reintentar: "le pasa a todos" (PAG L1 27:48).
7. **Activar 2FA** en la cuenta personal: foto de perfil → Configuración y privacidad → Contraseña y seguridad → Autenticación en dos pasos → Google Authenticator (PAG L1 35:39).
8. **Completar la información del negocio** para la verificación (PAG L1 37:30).
9. **Revisar las políticas** antes de crear creativos (ver Errores comunes) (PAG L1 38:10–47:37).
10. **Crear el conjunto de datos**: Orígenes de datos → Conjuntos de datos → Agregar (nombre = negocio + fecha) → "Conectar píxel de Meta y API de conversiones" → Instalar código manualmente → copiar (PAG L2 03:01–03:53).
11. **Instalar el código**: en Tiendanube, Configuración → Códigos externos → Facebook. Si la web está hecha en código, pedir el contacto del programador del cliente (PAG L2 04:36, 12:20). Activar **coincidencias avanzadas automáticas** (PAG L2 05:52).
12. **Configurar la API de conversiones**: eventos (carrito, iniciar pago, información de pago, compra, suscripción, registro, contacto, programar) con IP, nombre, apellido, mail y teléfono. Asignarse a uno mismo y al "Conversions API System User" en Personas (PAG L2 09:37–11:04).
13. **Asignar la cuenta publicitaria al píxel** (Activos conectados → Asignar activos) (PAG L2 11:37).
14. **Registrar la conversión de la landing** con el evento **Cliente potencial**, sin valor salvo que haya checkout (PAG L2 15:22):
    - sin thank you page → "Registrar botón nuevo" sobre el CTA (PAG L2 14:03);
    - con thank you page → "Registrar una URL", regla "la URL **contiene**" + una palabra identificable (gracias, thank-you-page, bienvenido) (PAG L2 16:17–17:17).
15. **Verificar**: Events Manager → Probar eventos, más la extensión Meta Pixel Helper; el ID debe coincidir con el de Meta. Que tarde en mostrar datos es normal (PAG L2 06:39–09:25, 19:18).
16. **Actualización del píxel** (PAG L3 00:34–03:16):
    - activar "Extender subidas de atribuciones" (90 días);
    - crear la **lista de dominios autorizados** (el resto se bloquea);
    - si no hay dominio: Seguridad de marca → Dominios → agregar la home y verificar;
    - vincular el dominio a la fanpage.
17. **Evento de lead calificado (opcional, con GoHighLevel)** (PAG L9 19:40–28:30):
    - en Meta: píxel → Configuración → "Generar identificador de acceso" (token) + ID del píxel;
    - en GHL: acción FB Conversion API, *Funnel event* (landing → VSL → agenda) o *Lead event* (formulario sin calendario), nombre de evento Schedule;
    - filtro if/else sobre el campo del formulario ("¿puede invertir?" = sí). Pocos filtros, no "87 filtros" (PAG L9 28:40).
    - En la campaña, el evento de conversión del conjunto es ese agendamiento; no usar conversiones personalizadas (PAG L9 19:40–21:10).

## Plantilla para llenar

```
── BASE DE LA CUENTA ─────────────────────────────────────────────
[ ] Facebook personal con 2FA (Google Authenticator)
[ ] Fanpage: web · teléfono · mail · ubicación · horarios · perfil · portada
[ ] WhatsApp Business vinculado        [ ] Instagram profesional vinculado
[ ] Portfolio comercial creado en Administrador comercial (NO Business Suite)
[ ] Personas: ______ (rol: ______ ; control total SOLO a: ______)
[ ] Cuenta publicitaria: país ____ · zona horaria ____ · divisa ____ (= la del medio de pago)
[ ] Medio de pago cargado           [ ] Información del negocio completa
[ ] Políticas revisadas para el rubro: ______ (¿salud, finanzas, cripto, +18?)

── PÍXEL + API ───────────────────────────────────────────────────
Nombre del conjunto de datos: [NEGOCIO] – [DD/MM]
[ ] "Píxel de Meta y API de conversiones" (no solo píxel)
[ ] Instalado en: [Tiendanube | código propio vía programador | GHL]
[ ] Coincidencias avanzadas automáticas: ON
[ ] Eventos API: carrito · iniciar pago · info de pago · compra · suscripción · registro · contacto · programar
[ ] Personas: yo + "Conversions API System User"
[ ] Cuenta publicitaria asignada al píxel
[ ] Conversión de la landing: evento Cliente potencial
      [ ] por botón (sin thank you page)   [ ] por URL "contiene" = ______
[ ] Probar eventos OK   [ ] Pixel Helper OK (ID coincide)

── ACTUALIZACIÓN ─────────────────────────────────────────────────
[ ] Extender subidas de atribuciones (90 días)
[ ] Lista de dominios autorizados: ______
[ ] Dominio verificado en Seguridad de marca y vinculado a la fanpage

── LEAD CALIFICADO (opcional) ────────────────────────────────────
Pregunta filtro del formulario: ______ = "sí"
Evento enviado: Schedule · tipo: [Funnel event | Lead event]
```

## Ejemplos del curso desarmados

| Ejemplo (min) | Qué muestra | Qué enseña |
|---|---|---|
| Cuenta de prueba en pesos argentinos (PAG L1 24:28) | Cuenta publicitaria con país, zona y divisa elegidos al crearla | Esos tres datos quedan fijos; solo el pago se cambia |
| Tienda de joyas de prueba (PAG L2 09:09) | Pixel Helper muestra PageView, ViewContent, AddToCart, InitiateCheckout | Verificar que el ID del píxel instalado sea el mismo que en Meta |
| Landing de coaching fitness (PAG L2 15:45) | Pop-up "Configurar evento": Cliente potencial, "No incluir el valor" | En servicios sin checkout, la conversión no lleva valor |
| Landing de VSL que agenda (PAG L2 19:50) | Agenda una reunión, salta a la thank you page y aparece Cliente potencial | La conversión real es el agendamiento, no el clic |
| Llamadas con VSL a USD 3-5, ~90% calificadas (PAG L9 19:00) | Anécdota del instructor con la API filtrada | Según el curso, filtrar lo que se manda a Meta mejora la calidad del lead |

## Errores comunes

- Configurar desde Meta Business Suite o anunciar con Promocionar (PAG L1 03:56, 15:48).
- Cargar datos falsos o incompletos en la fanpage y el negocio (PAG L1 07:16, 37:30).
- Elegir una divisa distinta a la del medio de pago (PAG L1 23:19).
- Dar control total a cualquiera (PAG L1 18:22).
- Instalar solo el píxel sin la API de conversiones (PAG L2 03:53).
- No registrar la conversión de la landing: el píxel no siempre toma los botones como conversión (PAG L2 12:58).
- Usar "es igual a" en vez de "contiene" en la regla de URL (PAG L2 17:17).
- Olvidar activar el seguimiento del conjunto de datos en el anuncio: "si no, no va a funcionar nada" ([[content-capital-pag-l13-embudo-a-vsl|PAG L13]] 17:56).
- Llenar el filtro de calificación de condiciones: con pocos datos Meta no optimiza (PAG L9 28:40).
- Anunciar algo que viola políticas: menores, delitos, odio, productos ilegales en la región, desinformación, fraudes (préstamos, empleo con cobro adelantado, apuestas, inversiones con retorno garantizado, Ponzi), cloaking; alcohol, salud y finanzas solo +18, sin autopercepción negativa ni cuerpo ideal; cripto con permiso escrito. Infringirlas deja la cuenta irrecuperable (PAG L1 38:10–46:30).

## Checklist para agentes

```
[ ] ¿La cuenta se configuró desde Administrador comercial (no Business Suite ni Promocionar)?
[ ] ¿La fanpage y la información del negocio tienen datos reales y completos?
[ ] ¿Hay 2FA activa en el perfil personal que administra?
[ ] ¿La divisa de la cuenta publicitaria coincide con la del medio de pago?
[ ] ¿Se instaló "píxel + API de conversiones", no solo el píxel?
[ ] ¿La conversión real de la landing (agendar / registrarse) está registrada como evento?
[ ] ¿Probar eventos y Pixel Helper confirman los eventos con el ID correcto?
[ ] ¿Hay lista de dominios autorizados y dominio verificado?
[ ] Si hay formulario con calificación: ¿se manda a Meta solo el lead calificado, con pocos filtros?
[ ] ¿El creativo y la oferta pasan las políticas del rubro?
```

## Fuentes

- Base: [[content-capital-pag-l01-introduccion-publicidad-paga]] 01:34–47:37 (rol, cuenta, políticas) y 48:15–51:26 (glosario del píxel y la API).
- [[content-capital-pag-l02-pixel-de-meta]] (instalación, API, eventos de landing).
- [[content-capital-pag-l03-actualizacion-en-el-pixel]] (atribución, dominios).
- [[content-capital-pag-l05-audiencias]] 37:10–38:48 (el píxel como origen de públicos; retención de 180 días).
- [[content-capital-pag-l09-proceso-pre-call-automatizaciones]] 17:40–28:30, 66:30–69:40 (evento Schedule filtrado desde GHL).
- [[content-capital-pag-l13-embudo-a-vsl]] 02:17, 11:13, 17:56 (evento Cliente potencial y seguimiento en la campaña).
- Inferencia mía: el orden en un solo recorrido y la plantilla. El curso lo reparte en varias clases.
- Conexiones: los eventos que se configuran acá los usan [[embudo-pago-a-dm]] (conversaciones) y [[embudo-pago-a-vsl]] (Cliente potencial / Schedule).

## Tensiones internas del curso

- **Atribución de 90 días.** El aviso que se lee en pantalla limita la extensión a eventos offline de tienda física; Nico Donovan la presenta como algo general (PAG L3 01:21). Tratarla como dudosa.
- **Evento de la landing.** Donovan recomienda Cliente potencial por botón o URL (PAG L2 15:22); Bartolomé manda Schedule por API desde GHL y pide no usar conversiones personalizadas (PAG L9 19:40–21:10). No se contradicen del todo: son dos stacks distintos. Conviene no disparar los dos para la misma acción (inferencia: duplicaría eventos, que es justo lo que PAG L3 00:00 quiere evitar).
- **Filtrar antes o después de la llamada.** Filtrar por formulario puede fallar porque la gente miente; filtrar después de la llamada da muy pocos datos (PAG L9 63:00, 67:00). El curso no cierra cuál elegir.
