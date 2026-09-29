---
title: "Discord para equipo y clientes: dos servidores, categoría por cliente, roles y canales con avisos automáticos (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-ent-l20, cc-ent-l21]
source_count: 2
created: 2026-09-26
updated: 2026-09-26
tags: [content-capital, cc-ent, framework, checklist, plantilla, operaciones, equipo, clientes, discord, comunidad, automatizacion]
status: developing
---

## En una línea

Desde el principio, **dos servidores**: uno de **clientes** (con una categoría privada por cliente, donde también está el equipo) y otro **solo del equipo** (una categoría por área). En ambos, **roles** escalonados según el organigrama, **invitaciones de un solo uso** y **canales que reciben avisos automáticos** (agendas, archivos, pagos, vencimientos) que etiquetan a quien tiene que actuar.

## Qué es y por qué funciona (según el curso)

- Discord permite servidores, miembros y permisos distintos por persona. Hay quien usa Slack; ellos usan Discord ([[content-capital-ent-l21-discord-para-gestion-de-clientes|ENT L21]] 00:14).
- Lo dicta **"Juani"** (L21 00:00; grafía de su comunidad dudosa). L20 no se presenta, pero remite a L21: probablemente es él (inferencia).
- **Un solo servidor** sirve al principio, pero con varios clientes y equipo grande hay que cuidar tanto los permisos que se arriesga filtrar información al cliente ([[content-capital-ent-l20-discord-para-gestion-de-equipo|ENT L20]] 00:00).
- **Roles**, "lo más sensible": definen qué ve y qué hace cada miembro (L21 02:13).
- **El servidor como base de datos**: cada área recibe avisos automáticos y las etiquetas suenan en el teléfono; así toman acción inmediata en tareas que antes se les pasaban (L20 06:32–07:02).
- **Valor percibido**: el canal de agendas deja al cliente ver cuántas llamadas le llegan por día, semana y mes (L21 08:10).
- L6 ya recomendaba Discord como canal interno ([[gestion-y-contratacion-de-equipo]]).

## Cuándo usarlo / cuándo no

- **Usarlo** en servicios con entrega continua y equipo (agencia, consultoría DFY o DWY).
- **Dos servidores**: desde el principio, según la recomendación (L20 00:42).
- **Canal de agendas del cliente**: muy útil desde cinco o seis clientes (L21 08:10).
- **Depende de la disciplina**: si nadie lo mantiene ordenado, no funciona (L21 08:42).

## Pasos

### A. Servidor de clientes (L21)

1. **Crear el servidor** "para un club o comunidad", con imagen y nombre del negocio (L21 00:48).
2. **Una categoría privada por cliente** (ejemplo: "Juan Pérez") con un **chat general** (L21 01:43).
3. **Roles** en ajustes del servidor (L21 02:53–03:45):
   - **founder**: permiso de administrador (el máximo);
   - **administrador**: gerentes, customer success, operaciones; puede gestionar roles;
   - **por puesto** (setter, closer, editor): ve canales y manda mensajes, pero no gestiona roles.
4. **Permisos de la categoría** (L21 04:36): administradores siempre; setters a todos los clientes o no, "depende".
5. **Canales internos** del cliente: chat setter y chat editor (L21 05:00). Al chat general se suma al **cliente como persona**, no como rol, con su setter y su editor.
6. **Acceso fino** (L21 05:34): a un canal se da acceso a todo un rol o solo a la persona asignada a ese cliente.
7. **Invitación** (L21 06:08): mandar el link editado para **un solo uso**; así nadie más entra con el mismo link.
8. **Canal "agendas"** (L21 07:24): Calendly conectado con **Zapier o Make** publica cada llamada agendada con nombre, teléfono, mail y respuestas de precalificación.
9. **Bots** según necesidad: buscar si existe uno antes de construir (L21 06:55). Emojis delante de cada nombre (L21 08:42).
10. **Registrar el usuario de Discord** de cada cliente en el [[crm-de-clientes]], para verificar que solo estén los que pagaron ([[content-capital-ent-l18-crm-clientes|ENT L18]] 02:25).

### B. Servidor del equipo (L20)

1. **Servidor aparte** (ejemplo: "agencia X team"); aplica todo lo del de clientes (L20 00:55).
2. **Categoría por área**: producto, operaciones, ventas y las que tenga el negocio, cada una con su **chat** para no irse a WhatsApp; más un **general** para lo que cruza áreas (L20 01:30–02:02).
3. **Categoría de agendas**: un canal por setter; Calendly publica cada llamada. El setter deja ahí datos útiles antes de la llamada (L20 02:59–03:39). Las agendas de clientes van en el otro servidor.
4. **Categoría de editores**: un canal por editor; aviso con **etiqueta** cuando se sube un archivo a su carpeta de Drive, y otro cuando lo pasa a terminado (L20 04:00).
5. **Pagos**: Stripe o PayPal avisan cuando entra un pago a quien tiene que saberlo (L20 04:46).
6. **Vencimientos**: aviso cuando a un cliente le falta una semana para terminar (L20 06:32). Dispara renovación u offboarding ([[entrega-de-servicio-onboarding-offboarding]], [[backend-upsell-y-ascension-de-clientes]]).
7. **Roles**: founder y administrador "base siempre", más **un rol por área** (L20 05:03).
8. **Categorías privadas por área**: cada una visible solo para su rol y administradores; un director comercial puede ser administrador, un closer no ve producto (L20 05:36). Motivo: privacidad y no distraer (L20 06:12).

## Plantilla para llenar

```
SERVIDOR CLIENTES
Roles: founder (admin) · administrador (gestiona roles) · ______ · ______ (sin gestionar roles)
Por cliente → categoría privada "[Nombre]":
   #general (cliente como persona + setter + editor)
   #chat-setter (acceso: [rol | persona])   #chat-editor (acceso: [rol | persona])
   #agendas (Calendly → Zapier/Make)
Invitación: link de uso único   Usuario de Discord cargado en CRM: s/n

SERVIDOR EQUIPO
Áreas: producto · operaciones · ventas · ______  (+ #general)
Canales automáticos:
   agendas-[setter]  ← Calendly
   editor-[nombre]   ← Drive (subido / terminado), con etiqueta
   pagos             ← Stripe / PayPal
   vencimientos      ← cliente a 7 días de terminar
Roles: founder · administrador · [rol por área]   Categoría privada por área: s/n
```

## Ejemplos del curso desarmados

| Caso (min) | Qué muestra | Lectura |
|---|---|---|
| Categoría "Juan Pérez" con general, chat setter y chat editor (L21 01:43–05:00) | Categoría por cliente | Todo lo del cliente en un lugar, con permisos por canal |
| Link editado a un solo uso (L21 06:08) | Invitación | El cliente no puede compartir el acceso |
| "Agenda Juan", "agenda Pedro" (L20 02:59) | Canal por setter | Cada llamada llega a quien la toma |
| Archivo subido a la carpeta del editor que lo etiqueta (L20 04:00) | Aviso automático | Suena en el teléfono, no se pierde |
| Closer que no ve la categoría de producto (L20 05:36) | Categoría privada | Privacidad y foco |

## Errores comunes

- Un solo servidor con varios clientes y equipo grande: riesgo de filtrar información (L20 00:25).
- Link de invitación reutilizable que el cliente puede pasar (L21 06:08; el curso no lo marca como error, es implícito).
- Dar a todos permiso de administrador en vez de permisos escalonados (L21 03:45).
- Conversaciones de área en WhatsApp, sin registro (L20 02:02).
- No mantener el orden: el sistema depende de la disciplina (L21 08:42).

## Checklist para agentes

```
[ ] ¿Hay dos servidores: clientes y equipo?
[ ] ¿Cada cliente tiene su categoría privada con chat general y chats internos?
[ ] ¿El cliente está sumado como persona, no como rol?
[ ] ¿Los roles siguen el organigrama (founder > administrador > puestos)?
[ ] ¿Solo founder tiene permiso de administrador total?
[ ] ¿Las invitaciones son de un solo uso?
[ ] ¿El usuario de Discord de cada cliente está en el CRM de clientes?
[ ] ¿El equipo tiene categoría por área, privada, más un general?
[ ] ¿Agendas, archivos, pagos y vencimientos llegan como aviso con etiqueta?
[ ] ¿Existe canal de agendas del cliente si le llevás llamadas?
```

## Fuentes

- [[content-capital-ent-l21-discord-para-gestion-de-clientes]] 00:14–09:15 (servidor de clientes, roles, invitaciones, agendas).
- [[content-capital-ent-l20-discord-para-gestion-de-equipo]] 00:00–07:23 (dos servidores, áreas, avisos automáticos, roles).
- Relacionadas: [[operaciones-roles-sops-finanzas]] (roles, organigrama y software), [[entrega-de-servicio-onboarding-offboarding]] (accesos y offboarding), [[crm-de-clientes]], [[comunidad-en-skool]], [[gestion-y-contratacion-de-equipo]], [[comunicacion-con-clientes]], [[situaciones-delicadas-y-reembolsos]] (L7 ubica a los clientes pesadilla arriba de todo en Discord; [[content-capital-ent-l07-situaciones-delicadas]]).
- Inferencia mía: la plantilla junta las dos clases en un solo esquema.

## Tensiones internas del curso

- **Automatizaciones sin receta.** L20 muestra los canales pero no cómo se arma cada aviso; la herramienta (Zapier o Make) aparece recién en L21, que remite a otro programa ("la incubadora", no identificado).
- **Precio de Make.** "10 dólares al mes" es una cifra hablada y puede haber cambiado (L21 08:10).
- **Setters en todos los clientes o no.** Queda en "depende" (L21 04:36), sin criterio.
