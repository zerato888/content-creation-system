---
title: "CRM de clientes: una fila por cliente durante todo su ciclo de vida (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-ent-l18, cc-ent-l11]
source_count: 2
created: 2026-09-26
updated: 2026-09-26
tags: [content-capital, cc-ent, framework, checklist, plantilla, operaciones, crm, clientes]
status: developing
---

## En una línea

El **CRM de clientes** guarda a cada cliente que ya pagó, de principio a fin: datos de contacto, fecha de inicio, usuario de Discord, link al contrato, monto y **etapa** del programa. Se puede tener en Airtable, pero para arrancar alcanza con Google Sheets; las columnas se suman con el uso.

## Qué es y por qué funciona (según el curso)

- Es distinto del CRM de ventas: aquel sigue leads y llamadas ([[crm-de-ventas-en-planilla]]); este sigue clientes durante todo su ciclo de vida ([[content-capital-ent-l18-crm-clientes|ENT L18]] 00:00).
- **Eficiencia operativa**: si hay que mandarle un archivo, el correo ya está; no hay que pedírselo (L18 00:25).
- **Mejor atención**: no preguntarle diez veces lo mismo (L18 00:55).
- "No cuesta mucho hacerlo" (L18 00:25).
- El instructor no se presenta; el estilo y el cierre coinciden con "Juani" de operaciones (inferencia).
- Ellos usan **Airtable**: vistas, métricas en interfaces y automatizaciones, como mandar un correo cuando se cumple una condición (L18 01:08). La clase enseña Sheets porque al principio hay gastos más importantes (L18 01:39).
- Sheets replica "prácticamente todo"; la diferencia es estética, "lo de menos" al comenzar (L18 06:44).

## Cuándo usarlo / cuándo no

- **Usarlo** desde el primer cliente de un negocio de servicios: el alta en el CRM es parte del onboarding ([[entrega-de-servicio-onboarding-offboarding]]).
- **Pasar a Airtable** cuando hagan falta vistas, interfaces o automatizaciones (inferencia a partir de L18 01:08–01:39).
- **No reemplaza** al CRM de ventas: los leads que no compraron van en el otro.

## Pasos

1. **Elegí la herramienta**: Google Sheets (gratis) o Airtable (L18 01:39, 04:49).
2. **Cargá las columnas base** (L18 02:09–03:37):
   - nombre, correo, teléfono;
   - fecha de inicio;
   - **usuario de Discord**: la entrega vive en gran parte en Discord, y con esta columna verifican que solo estén los que pagaron (L18 02:25; ver [[discord-para-equipo-y-clientes]]);
   - **link al contrato firmado**: si hay un problema con una cláusula, se revisa ahí y se conversa (L18 02:43);
   - **monto pagado** en formato moneda;
   - **etapa** como selección única.
3. **Poné el tipo de dato correcto** a cada columna: texto, casilla, fórmula, moneda, teléfono, fecha, porcentaje (L18 03:01, 05:52).
4. **Armá la etapa** (L18 03:37, 05:52): en un servicio de tres meses, etapa 1, 2 y 3, una por mes. En Sheets: clic derecho → menú desplegable → opciones con colores → copiar hacia abajo. La etapa conecta con [[camino-del-cliente]].
5. **Sumá columnas por mejora continua** según el tipo de servicio: no es lo mismo paid media que adquisición o contenido (L18 04:14; [[mejora-continua-del-servicio]]).
6. **Cargalo en el onboarding** de cada cliente nuevo (alta en CRM, [[entrega-de-servicio-onboarding-offboarding]]). El alta automática desde un formulario se trata en [[content-capital-ent-l10-automatizacion-de-onboarding|ENT L10]].

## Plantilla para llenar

```
| Nombre | Correo | Teléfono | Fecha inicio | Usuario Discord | Contrato (link) | Monto pagado | Etapa        | (+ columnas propias) |
|--------|--------|----------|--------------|-----------------|-----------------|--------------|--------------|----------------------|
|        |        |          | dd/mm/aaaa   |                 | https://...     | USD ___      | [1 | 2 | 3]  |                      |

Tipos: texto · texto · teléfono · fecha · texto · link · moneda · desplegable con colores
Columnas a sumar según el servicio: ______________________
```

## Ejemplos del curso desarmados

| Caso (min) | Columna | Lectura |
|---|---|---|
| Mandar un archivo sin pedir el correo (L18 00:25) | Correo | Eficiencia |
| Verificar que en Discord solo haya clientes que pagaron (L18 02:25) | Usuario de Discord | Control de accesos |
| Problema con una cláusula (L18 02:43) | Contrato | Se revisa el documento firmado antes de hablar |
| Servicio de 3 meses con etapas 1-3 (L18 03:37) | Etapa | Saber en qué fase está cada uno con muchos clientes |

## Errores comunes

- Mezclar leads y clientes en el mismo CRM (inferencia a partir de la distinción de L18 00:00).
- Pedirle al cliente datos que ya dio (L18 00:25).
- No registrar el usuario de Discord y perder el control de quién tiene acceso (L18 02:25).
- Esperar a tener Airtable para empezar: Sheets alcanza (L18 06:44).
- Querer todas las columnas desde el día uno en vez de sumarlas con el uso (L18 04:14).

## Checklist para agentes

```
[ ] ¿Está separado del CRM de ventas?
[ ] ¿Tiene nombre, correo, teléfono, fecha de inicio, usuario de Discord, contrato, monto y etapa?
[ ] ¿La etapa es un desplegable (selección única)?
[ ] ¿Cada columna tiene su tipo de dato?
[ ] ¿El alta en el CRM está en el onboarding de cada cliente?
[ ] ¿Los usuarios de Discord coinciden con los clientes que pagaron?
[ ] ¿Hay columnas propias del tipo de servicio, sumadas por mejora continua?
```

## Fuentes

- [[content-capital-ent-l18-crm-clientes]] 00:00–06:53 (todo el CRM de clientes, Airtable y Sheets).
- [[content-capital-ent-l11-mejora-continua-metricas]] 07:28 (Juani mejora un CRM para que los clientes lo entiendan).
- Relacionadas: [[crm-de-ventas-en-planilla]] (el de leads), [[gohighlevel-stack-crm]] (otra opción de CRM, no mencionada en la clase), [[operaciones-roles-sops-finanzas]] (M1 recomienda Airtable), [[entrega-de-servicio-onboarding-offboarding]], [[camino-del-cliente]], [[discord-para-equipo-y-clientes]], [[mejora-continua-del-servicio]].
- Inferencia mía: la plantilla en tabla ordena las columnas que la clase arma en vivo.

## Tensiones internas del curso

- **Casilla "pesadilla".** L7 pide marcar en el CRM a los clientes pesadilla ([[content-capital-ent-l07-situaciones-delicadas]]; ver [[situaciones-delicadas-y-reembolsos]]), pero L18 no incluye esa columna.
- **Airtable vs. Sheets.** M1 recomienda Airtable como software mínimo; L18 dice que Sheets alcanza. Se leen como etapas: Sheets para arrancar, Airtable al crecer (inferencia).
