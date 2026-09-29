---
title: "Clonación con IA: avatar de video sobre audio real (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-cre-l21]
source_count: 1
created: 2026-09-26
updated: 2026-09-26
tags: [content-capital, cc-cre, framework, checklist, plantilla, avatar, ia, produccion, formatos, grabacion, audio, anuncios, angulos, automatizacion]
status: developing
---

## En una línea

Clonarse es entrenar un **avatar de video** con la imagen y los gestos de una persona real, que mueve los labios sobre un **audio grabado por esa persona**. Según el curso sirve para **escalar lo que ya está validado** (velocidad, volumen, calidad de estudio constante), no para validar ni para crear criterio. La voz no se clona: se graba.

> **Límite de uso (regla de el autor del kit, no del curso).** Esta página describe lo que enseña la clase. Los agentes solo aplican esto con **consentimiento explícito** de la persona clonada y respetando las verificaciones y avisos de cada plataforma. Ver "Checklist para agentes".

## Qué es y por qué funciona (según el curso)

- Lo dicta el manager de operaciones del equipo en una **clase en vivo** (se oye "heros"; puede ser Eros). Antes tuvo un software de clonación, el que Ramiro mostraba en sus videos ([[content-capital-cre-l21-clonacion-con-ia|CRE L21]] 01:51).
- **Qué se clona**: la imagen y los gestos de una persona real (el ejemplo es Ramiro) como avatar con sincronización de labios. La voz no: se sube un audio real, por ejemplo uno que Ramiro manda por WhatsApp (CRE L21 16:35).
- **"La IA no clona el criterio"** (CRE L21 02:20). Piezas del contenido: **ángulo**, **oferta**, **guion/copy**, **formato**, **edición** y **ejecución** (02:27). El clon solo resuelve parte de la ejecución. Ver [[angulos-de-comunicacion]].
- **Lo que sí da** (CRE L21 03:24–04:19):
  - **velocidad**: un ángulo que funciona se convierte en mucho contenido rápido;
  - **volumen**: "grabar 100 videos en un rato";
  - **consistencia de marca** y calidad de estudio sin montar el set (clonaron a Ramiro en varios estudios; después graba un audio desde la cama);
  - piezas puntuales rápidas (webinar, anuncios) y sostener el nivel de producción en el tiempo.
- **Lo que no da** (CRE L21 04:24): el ángulo, el guion que vende, la **conexión** con la audiencia y la **autoridad inicial**. A Ramiro le funciona por su posición en el mercado; no es lo mismo alguien sin cara conocida (04:48).
- **Por qué no clonar la voz**: en español ningún motor la hace bien (en inglés, algo mejor); un dataset de voz que no se note es difícil y caro. La voz grabada con el teléfono conserva las expresiones características y no cuesta tanto (CRE L21 08:01–09:00).
- **Modelos distintos**: los de clonación no son los de efectos especiales; en una de las plataformas se combinan sobre el clon (CRE L21 23:19).

**Herramientas (nombres dudosos por el audio):**

- "Haitian"/"Hagen": suena a **HeyGen** (inferencia: empresa establecida, verificación de identidad, API limitada). El instructor dice que lleva 4-5 años haciendo clones ahí (CRE L21 09:10).
- "Hashi": **empresa argentina** con modelo propio; grafía no confirmable. La prefiere: "muchísimo mejor", más flexible y con API abierta (09:10, 14:26, 29:23). En varios tramos la transcripción escribe "Haitian" cuando habla de esta.
- Voz sintética, si igual se usa: la mejor plataforma suena a **ElevenLabs** (inferencia, 24:47); en el chat se nombra Fish Audio (29:04).

## Cuándo usarlo / cuándo no

**Filtro de etapa** (CRE L21 05:25–06:45):

- **No clonarse** si todavía no validaste, no sabés qué contenido vende, no sos consistente grabando, no podés nombrar ángulos que funcionan ni sabés de qué contenido llegan tus clientes. No vale la pena pagar herramientas. Ver [[deteccion-de-angulos-ganadores-trazabilidad]].
- **"Si estás en rojo"**, el trabajo del mes es volver a los módulos anteriores y a las consultorías (06:45).
- **Sí**, si ya sabés qué vende: probar copys sobre un ángulo que funciona, variar formatos, y sobre todo **anuncios en masa** o contenido que necesitás en mucha cantidad (05:54, 07:45). Ver [[testeo-y-escalado-de-creativos-meta-ads]].
- **Branding validado**: si ya tenés un look que funciona (Ramiro siempre graba con gorrita), montar un set con eso y clonarlo (06:21).

**Qué formatos se clonan** (CRE L21 07:00): cámara fija, plano medio, misma energía y ritmo. Un formato con objeto en la mano (el "iPad" de Ramiro) es muy difícil. "Si vos no tenés eso validado, no sirve absolutamente nada" (07:41). Ver [[formatos-rotacion-sin-quemar]].

## Pasos

1. **Pasar el filtro de etapa** (arriba). Si no pasa, no seguir.
2. **Elegir el formato clonable** y, si hay branding validado, montar el set con ese look (CRE L21 06:21, 07:00).
3. **Grabar el material de entrenamiento** (CRE L21 09:56–10:41, 13:55):
   - video de **1 a 10 minutos** hablando; no importa el contenido (puede leer un texto mirando a cámara);
   - mirar siempre a cámara, gestos naturales;
   - sin objetos (o tenerlo todo el tiempo); no agarrar ni dejar cosas; no taparse la cara con las manos;
   - **arrancar hablando**: cortar los segundos en que entrás o te sentás.
   - Base de grabación: [[grabacion-celular-luz-encuadre-audio]].
4. **Si la plataforma depende mucho del dataset** ("Haitian"): grabar con **dos cámaras a la vez** (una de frente a 90° y otra de costado a 75°), entrenar dos modelos y alternar ángulos en la edición para disimular la sincronización (CRE L21 12:03–13:37). Allí el resultado depende "100% del material" y exige avatar en **4K** para el motor premium (11:38, 17:44).
5. **Grabar el audio real** de cada pieza (teléfono, WhatsApp) y subirlo; "la voz no la clonen, la graban" (CRE L21 09:00, 16:35).
6. **Configurar el render**: desactivar los agregados del motor, que dejan el video "muy plástico"; usar el motor premium (CRE L21 17:10–17:44). Recortar el sobrante de audio para dejar solo cuando habla (21:25).
7. **Editar con subtítulos** y, si hay dos modelos, alternar frente/costado (CRE L21 12:25).
8. **Automatizar** si hay volumen: elegir plataforma con API; la argentina la tiene abierta y la otra limita su mejor modelo (CRE L21 14:26, 28:12).
9. **Si igual se clona la voz** (desaconsejado): buen micrófono, ritmo y tono estables, entre **20 minutos y 2 horas** de grabación; "ningún motor pasa por humano" (CRE L21 24:07).

## Plantilla para llenar

```
FILTRO DE ETAPA
Ángulos ganadores que puedo nombrar: 1) ____ 2) ____ 3) ____   (si no hay → no clonar)
¿Sé de qué contenido llegan mis clientes? [sí/no]   ¿Grabo consistente? [sí/no]
USO: [anuncios en masa | variantes de copy sobre ángulo validado | variar formato | pieza puntual]
CONSENTIMIENTO de la persona clonada (por escrito): [ ] fecha ____ alcance ____

FORMATO CLONABLE: cámara fija [ ] plano medio [ ] misma energía [ ] sin objeto en mano [ ]
MATERIAL DE ENTRENAMIENTO
Duración: ___ min (1-10)  Mira a cámara [ ]  Sin objetos [ ]  Manos lejos de la cara [ ]
Arranca hablando (sin entrada/sentada) [ ]  Cámaras: frente 90° [ ] costado 75° [ ]  4K [ ]
POR PIEZA
Audio real grabado por la persona [ ]   Agregados del motor OFF [ ]   Subtítulos [ ]
Aviso de contenido IA donde corresponda [ ]   Marca de agua/etiqueta de la plataforma intacta [ ]
```

## Ejemplos del curso desarmados

| Ejemplo (min) | Qué muestra | Lectura |
|---|---|---|
| Ramiro clonado en varios estudios; graba un audio desde la cama (CRE L21 03:46) | Calidad de estudio sin set | Uso de escala con marca validada |
| Mismo copy, clon de frente y de costado, fondo azul (CRE L21 12:25–13:37) | Dos ángulos alternados | "Muchísimo más dinámico"; disimula la sincronización |
| Clon mal entrenado (CRE L21 18:52–19:50) | El original entraba caminando, se sentaba, agarraba un libro, no miraba a cámara | "Se ve malísimo" y repite la entrada del video original |
| Formato "iPad" de Ramiro (CRE L21 07:00) | Objeto en la mano | Formato no clonable |
| Test con el crudo de un reel que anduvo (CRE L21 10:58) | Mismo video, otro copy u otra persona | Saber si funcionaba el formato o el copy (él no recomienda validar con IA) |

## Errores y riesgos

**Errores que marca el curso:**

- Clonarse "en rojo", antes de validar (CRE L21 05:25, 06:45).
- Dataset mal grabado: modelo irrecuperable, mala sincronización de labios (11:38, 18:52).
- Dejar activados los agregados del motor: video "muy plástico" (17:10).
- Clonar la voz en español esperando que no se note (08:10, 24:14).
- Esperar conexión o autoridad del clon (04:24).

**Prácticas del curso que chocan con los límites de uso** (se registran, no se recomiendan):

- **Elegir plataforma por no verificar identidad.** Presenta como ventaja que "Hashi" logra el mismo nivel "sin el problema de la validación" (CRE L21 09:51, 13:55) y trata la verificación de "Haitian" para clonar a otro como un trámite engorroso, sobre todo para el "shadow operator" que opera el contenido de otro (09:28, 15:13, 18:14).
- **Sacar la marca de agua**: en la demo indica desactivarla (CRE L21 17:28).
- **Avatares de personas que no existen** para vender un infoproducto con una marca personal ficticia: lo ve "bastante positivo" (CRE L21 19:56).
- **Que la audiencia no distinga la IA**: menciona nichos donde "capaz que pasa" (CRE L21 24:26). La clase no habla de consentimiento ni de avisar que el video es IA.

## Checklist para agentes

**Límites obligatorios (regla de uso de el autor del kit, igual que "no es consejo médico" en salud).** Un agente solo aplica esta página si:

```
[ ] Hay CONSENTIMIENTO EXPLÍCITO de la persona clonada (imagen, gestos y, si aplica, voz),
    para este uso concreto. Sin consentimiento → no se clona, sin excepciones.
[ ] Se completan las VERIFICACIONES DE IDENTIDAD que pida la plataforma. No se elige una
    plataforma porque no verifica ni se buscan atajos para saltearla.
[ ] NO se quitan marcas de agua ni etiquetas de la plataforma para ocultar que es IA.
[ ] NO se crean avatares de personas inexistentes presentados como reales para vender.
[ ] Se agrega AVISO de contenido generado por IA donde la plataforma o la ley lo pidan.
```

Checklist del método (según el curso), después de pasar los límites:

```
[ ] ¿Pasa el filtro de etapa (ángulos ganadores nombrables, contenido validado, consistencia)?
[ ] ¿El uso es escalar lo validado (anuncios en masa, variantes de copy), no validar?
[ ] ¿El formato es clonable (cámara fija, plano medio, sin objeto en mano)?
[ ] ¿El material de entrenamiento cumple: 1-10 min, mira a cámara, sin objetos, arranca hablando?
[ ] Si la plataforma depende del dataset: ¿dos cámaras (90° y 75°) y 4K?
[ ] ¿El audio es real, grabado por la persona (no voz clonada)?
[ ] ¿Agregados del motor desactivados? ¿Subtítulos?
[ ] ¿El ángulo, el guion y la oferta los puso una persona, no el clon?
```

## Fuentes

- Base: [[content-capital-cre-l21-clonacion-con-ia]] (completa, 00:00–30:13). Clase en vivo sin capturas: los pasos de las plataformas y varios nombres dependen de lo que se ve en pantalla.
- Inferencia mía: la plantilla, la tabla de desarme y la identificación de herramientas (HeyGen, ElevenLabs) por contexto.
- Los límites de uso son una regla de el autor del kit para los agentes, no contenido del curso.
- Relacionadas: [[angulos-de-comunicacion]] · [[deteccion-de-angulos-ganadores-trazabilidad]] · [[testeo-y-escalado-de-creativos-meta-ads]] · [[formatos-rotacion-sin-quemar]] · [[grabacion-celular-luz-encuadre-audio]].

## Tensiones internas del curso

- **"No validar con IA" vs. el test del crudo.** Dice que no recomienda validar con IA y, en el mismo tramo, propone usar el clon para ver si funcionaba el formato o el copy (CRE L21 10:58). Lectura posible: sirve para aislar una variable de algo que ya anduvo, no para validar desde cero (inferencia).
- **Conexión vs. avatares ficticios.** Dice que un clon no genera conexión ni autoridad inicial (04:24) y después ve positivo vender con un avatar de una persona que no existe (19:56). La clase no lo resuelve; los límites de uso lo excluyen.
- **La verificación como molestia.** El curso trata la verificación de identidad como un costo operativo (09:28, 09:51); para los agentes es un requisito (ver límites).
- **Voz.** "La voz no la clonen" (09:00), pero da buenas prácticas para clonarla (24:07) y recomienda voces de stock argentinas "si igual querés" (21:38).
- **Datos del instructor sin verificar**: 4-5 años haciendo clones, contenido con IA para marcas grandes (29:23), "grabar 100 videos en un rato".
