---
name: sistema-de-marca
description: Construye o ordena una marca de punta a punta con evidencia, en tres etapas con una decisión de la persona entre cada una: estrategia (a quién, qué promesa), dirección visual con vistas previas que quedan como referencia fija, e identidad final (logo y sistema). Complementa a brand-onboarding (ficha) y logo (5 propuestas). Usar cuando digan "armá mi marca", "sistema de marca", "posicionamiento y identidad" o al reordenar una marca a medias.
role: creative-director
files: []
---

# sistema-de-marca — de la idea a una identidad que se puede usar

Esta skill es el método completo. Las piezas sueltas ya existen: `brand-onboarding` arma la ficha `brand.json`, `logo` hace la ronda de 5 propuestas. Aquí se decide **en qué orden** y **con qué evidencia**.

## Delegación
- Estrategia y decisiones: creative-director. Composición de las vistas previas: dp-cinematographer. Textos: copywriter.
- Claude Code: use the Agent tool with subagent_type `creative-director`.
- Codex: adopt the `creative-director` role from AGENTS.md.

## Paso 0 — Qué hay ya
Anotar lo que la persona trae (hechos, materiales, decisiones, límites) y lo que falta. No rehacer lo que ya funciona: si hay identidad, entrar en la etapa que falta. Marcar cada entregable como `aplica`, `no aplica`, `ya existe` o `no se sabe`, con una razón.

## Evidencia antes de decidir
Cada afirmación importante se marca `hecho`, `inferencia` o `hipótesis`, con su fuente y la fecha en que se miró. Aprobar una decisión no convierte una hipótesis en hecho. Nunca inventar investigación, dolores del cliente, precios de la competencia, disponibilidad de un nombre ni resultados. Para salud, nutrición, finanzas o seguridad, llevar una lista de afirmaciones con su respaldo antes de escribir texto público.

## Etapa 1 — Estrategia (decisión 1)
Descubrir: para quién, qué problema resuelve, en qué se diferencia, qué competencia hay (buscar de verdad con `web-research`). Salida: público, promesa, posicionamiento y tono, en una página. **Parar y pedir que la persona elija o corrija.** Un hueco en el mercado es una observación hasta que un cliente real diga que le importa.

## Etapa 2 — Dirección visual con vistas previas (decisión 2)
No se inventa una solución final desde texto. Orden: **inventario → elegir o juntar referencias → extraer → piloto → aceptar → escalar**.
1. Juntar 2 o 3 direcciones distintas como **vistas previas reales** (imágenes con la skill `imagen`, o referencias que traiga la persona), cada una con su color, tipografía libre, tipo de imagen y qué evita.
2. La persona elige una. Esa vista queda guardada como **referencia fija** (`.kit-personal/brands/<marca>/referencia/`) con su nombre, qué se adopta y qué se excluye.
3. Extraer solo lo que se ve: geometría, jerarquía, tipografía, espaciado, relación de colores. Todo lo demás es inferencia y se marca.
4. Un piloto (una pieza real) contra esa referencia. Recién con el piloto aceptado se escala a un lote.
Si hay que generar imágenes de pago, estimar antes cuántas, con qué servicio y el costo máximo; no generar hasta que la persona apruebe esa cifra.

## Etapa 3 — Identidad (decisión 3)
Con la dirección elegida: logo con la skill `logo` (ronda de 5), ficha con `brand-onboarding`, y reglas de uso (colores, tipografías, qué nunca). Aprobación por pieza, con su alcance. Aprobar una pieza no autoriza un lote, ni publicar, ni imprimir.

## Nombre (solo si sigue abierto)
Generar muchos, filtrar los viables y revisar cada uno en fuentes públicas con el resultado `sin conflicto visto`, `riesgo detectado` o `no concluyente` (una fuente inaccesible es no concluyente). Esto no es un dictamen legal: decirlo.

## Si cambia algo después
Si aparece evidencia nueva o cambia una decisión aprobada, anotar qué cambió, qué piezas toca y qué decisiones siguen firmes. Reabrir solo lo afectado; no rehacer todo.

## Reglas
- Nunca copiar el estilo de una marca ajena real; las referencias son para entender el mecanismo.
- Ningún dato personal de terceros en las fichas.
