---
title: "Content Capital · Programa · Entrega de Servicio y Operaciones L10 — Automatización de Onboarding"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Entrega de Servicio y Operaciones"
instructor: "\"Juan\"/\"Juani\" de operaciones (se presenta como \"Juan\"; mismo instructor de L4, inferencia)"
lesson: 10
duration: "15:55"
date_ingested: 2026-09-26
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/ent-entrega-de-servicio/10-automatizacion-de-onboarding.md
tags: [content-capital, cc-ent, operaciones, onboarding, automatizacion, crm, contratos]
status: active
---

## En una línea

Dos automatizaciones en Zapier eliminan casi todo el trabajo manual del onboarding: **(1)** una respuesta de formulario carga los datos del cliente en el CRM y le envía el contrato por PandaDoc; **(2)** la firma de ese contrato le da acceso a los cursos privados de Skool y avisa en el Discord del equipo con un link de descarga del contrato, para archivarlo en el CRM.

Instructor: **"Juan"** (00:00, "Juan y nuevamente por acá"). Es el mismo "Juani" de L4 (contratos) y el "Juan" de operaciones que nombra L3; inferencia por voz y temario.

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:14 | Objetivo: sacar la mayor parte de las tareas manuales del onboarding con dos automatizaciones. |
| 00:26 | **Automatización 1**: se dispara con un formulario (ellos usan Typeform; sirve Google Forms o cualquiera que conecte con Zapier). Carga el CRM y crea el contrato que le llega al mail al cliente. |
| 00:59 | **Automatización 2**: se dispara cuando el cliente firma. Le da accesos (invitación a Skool al mismo mail del contrato) y manda un mensaje al Discord del equipo. |
| 01:27 | Por qué el aviso en Discord: quien baja y sube los contratos al CRM no tiene que entrar a PandaDoc; toca un link y se descarga. |
| 01:45 | **Cuándo aplica la parte 1**: contrato igual para todos (oferta de precio fijo) o pocas ofertas con una plantilla cada una. Con tres plantillas, se arma la automatización tres veces. |
| 02:06 | Agencia con ofertas 100% personalizadas (cada una con otro precio): la parte 1 no sirve porque cada contrato es a medida. La parte 2 sí, aunque puede requerir variantes si no todos reciben los mismos accesos. |
| 02:53 | Estructura: respuesta al formulario → **ramificación** (paths) en dos: cargar el CRM (ellos usan Airtable; sirve Google Sheets) y mandar el contrato al mail que dejó el cliente. |
| 03:19 | Las preguntas del formulario dependen del servicio: mail, teléfono y todo lo que sirva a futuro. |
| 03:48 | Arranca la demo desde cero. Zapier es no-code; recomienda consultar a ChatGPT (incluso pasándole capturas) cuando se traben. |
| 04:34 | Hace la demo con Google Forms porque "la mayor parte" lo usará. **Disparador** = Google Forms, evento "nueva respuesta"; se conecta la cuenta y se elige el formulario. |
| 05:35 | Paso de **paths**: se suman las ramas que hagan falta. Cada rama puede tener una condición (filtro); sin condición, corre siempre. |
| 06:37 | Rama CRM: recomienda Airtable ("van a tener una clase"), sirve cualquiera. Acción "create record": se conecta la cuenta, base y tabla, y se mapea cada columna del CRM con la respuesta del formulario. |
| 07:43 | Si una respuesta viene con formato feo (fechas, teléfonos), se agrega un paso previo de **formateo**. Usa la IA de Zapier escribiéndole lo que quiere; le resulta más rápido que buscar opciones. |
| 09:19 | Rama contrato: usan **PandaDoc** porque permite automatizarlo; otra plataforma que probaron no daba esa conexión "al menos" cuando la evaluaron. Acción "create document". |
| 10:05 | Requisito: tener creada antes la **plantilla** en PandaDoc (se explica en otra clase). Se completan mail del destinatario y nombre, separado con otro formateo porque el cliente escribe su nombre completo. |
| 10:52 | Si necesitan algo más, agregan otra rama. |
| 11:05 | **Automatización 2**: disparador PandaDoc con evento "documento completado" (antes era "documento creado"), mismo template. |
| 11:47 | Ramificación doble. Rama izquierda: Skool, acción "invite member". Ventaja: solo entra quien ya firmó. |
| 12:16 | Para elegir a qué cursos accede, en Skool los cursos tienen que ser **privados**. |
| 12:39 | Rama derecha (no 100% necesaria): mensaje al canal del equipo en Discord con nombre del cliente y link al PDF. Un clic lo descarga y se sube al CRM. |
| 13:14 | Por qué archivar el contrato en el CRM: ante un problema con un cliente, se busca, se baja y se muestra "esto es lo que habíamos acordado". |
| 14:29 | Balance: les ahorró muchísimas tareas manuales y eliminó "al 100%" los errores (según el instructor). Recomienda mejorarlo y adaptarlo. |
| 15:08 | Aviso: el plan más barato de PandaDoc no conecta con Zapier; hace falta el intermedio. Con volumen alto, lo considera rentable. |

## Frameworks que aparecen

- [[entrega-de-servicio-onboarding-offboarding]] (ampliar: el onboarding de L3 automatizado; el acceso se da recién después de la firma)
- [[operaciones-roles-sops-finanzas]] (ampliar: software mínimo Airtable + Zapier + PandaDoc + Skool + Discord, ahora con el flujo concreto)
- [[content-capital-ent-l04-gestion-de-contratos]] (la plantilla de PandaDoc que esta clase da por hecha)
- Nuevo propuesto: automatización del onboarding con formulario → CRM → contrato → accesos

## Ejemplos mostrados en pantalla

- **00:20-01:45** — Diagrama de las dos automatizaciones (formulario → CRM + contrato; firma → Skool + Discord).
- **03:48-10:52** — Demo en Zapier de la automatización 1 (Google Forms, paths, Airtable, formateo con IA, PandaDoc). Los nombres de campos y columnas solo se ven en pantalla.
- **08:07** — Ejemplo de fecha antes y después del formateo (el formato exacto solo se ve en pantalla).
- **11:05-14:29** — Configuración de la automatización 2 (PandaDoc "documento completado", Skool "invite member", mensaje a Discord con link al PDF).

## Tareas y herramientas

- Zapier (disparadores, paths, formateo, IA de formateo); Typeform o Google Forms; Airtable (o Google Sheets) como CRM; PandaDoc (plan intermedio); Skool con cursos privados; Discord del equipo.
- Plantilla de contrato creada en PandaDoc antes de armar el zap (10:05).
- Columna de contrato en el CRM para cada cliente (13:14).

## Citas clave

- Zapier "es No Code": no hace falta saber programar. (04:02)
- El contrato en el CRM sirve para decir "esto es lo que habíamos acordado". (13:26)

## Lo que no se procesó

- Los precios de ejemplo de ofertas personalizadas (02:13) solo ilustran que cada contrato cambia; se omiten.
- La otra plataforma de firma que probaron sale ininteligible (09:33); se omite.
- La afirmación de que eliminó el 100% de los errores es del instructor, sin datos.
