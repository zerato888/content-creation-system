// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Ideas y Content Lab (marca personal): paste a link or a transcript -> analysis -> faithful
// translation editor; plus your own ideas (tasks at stage "idea").
import {
  api, brandPicker, button, card, copyText, el, empty, errorLine, formatDate, inlineAdd, input, masthead,
  noBrand, pills, safe, select, toast,
} from "../lib.js";

const TIPOS = [["reel", "Reel / video corto"], ["carrusel", "Carrusel"], ["youtube", "Video largo"]];
const state = { tab: "referencias", open: null, packet: null };

const q = (brand) => `brand=${encodeURIComponent(brand.id)}`;

function newReference(brand, reload) {
  const box = card("Pegá un video o una transcripción", "Nueva referencia");
  const url = input("url", { placeholder: "Link del video (opcional)" });
  const tipo = select(TIPOS, "reel");
  const tema = input("text", { placeholder: "¿De qué trata? (una frase)" });
  const transcript = input("textarea", { placeholder: "Pegá acá la transcripción (opcional si pegaste el link)" });
  transcript.rows = 6;
  const save = button("Guardar referencia", "btn btn--primary", async () => {
    if (!url.value.trim() && !transcript.value.trim()) return toast("Pegá un link o una transcripción", "error");
    save.disabled = true;
    try {
      const { item } = await api("/api/lab/item", {
        brand: brand.id, tipo: tipo.value, tema: tema.value.trim() || url.value.trim(),
        origen: { url: url.value.trim() }, transcript_original: transcript.value,
      });
      state.open = item.id;
      toast("Referencia guardada");
      reload();
    } catch (e) { save.disabled = false; toast(e.message, "error"); }
  });
  box.append(url, tipo, tema, transcript, save,
    el("p", "hint", "El análisis lo escribe tu agente: pedile «analizá mi última referencia del Content Lab»."));
  return box;
}

function itemCard(item) {
  const b = el("button", `item-card${item.archivada ? " is-archived" : ""}`);
  b.type = "button";
  b.append(el("span", "label", item.tipo), el("strong", "", item.tema || item.id),
    el("span", "muted", formatDate((item.creado || "").slice(0, 10))));
  b.addEventListener("click", () => { state.open = item.id; state.packet = null; b.dispatchEvent(new CustomEvent("reopen", { bubbles: true })); });
  return b;
}

function analysis(item) {
  const box = card("Análisis", "Qué tiene este video");
  const rows = [["Tema", item.tema], ["Resumen", item.resumen_original], ["Ángulo", item.angulo],
    ["Hook original", item.hook_original?.ejemplo], ["Fórmula del hook", item.hook_original?.formula]];
  const shown = rows.filter(([, v]) => v);
  if (!shown.length && !(item.estructura?.sections || []).length) {
    box.append(empty("Todavía sin análisis. Pedíselo a tu agente."));
  }
  shown.forEach(([k, v]) => { const p = el("p", "kv"); p.append(el("span", "label", k), el("span", "", v)); box.append(p); });
  const sections = item.estructura?.sections || [];
  if (sections.length) {
    const ol = el("ol", "plain-list");
    sections.forEach((s) => ol.append(el("li", "", typeof s === "string" ? s : JSON.stringify(s))));
    box.append(el("p", "label", "Estructura"), ol);
  }
  if (item.origen?.url) {
    const link = el("a", "link", "Abrir el video original");
    link.href = /^https?:\/\//i.test(item.origen.url) ? item.origen.url : "#";
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    box.append(link);
  }
  return box;
}

// A complete, self-contained request: it names only what the kit ships (its launcher and skills),
// so it works in Claude Code or Codex with nothing else installed.
export function handoff(packet) {
  const fields = packet.writable_fields.filter((f) => !f.includes("[N]")).join(", ");
  return [
    `Pedido del Command Center: traducción fiel de la referencia ${packet.id} (marca ${packet.brand}) al idioma «${packet.target_language}».`,
    "",
    "Contrato (obligatorio):",
    packet.contrato,
    "",
    "Pasos:",
    "1. Traducí el texto original de abajo cumpliendo el contrato. No uses otras skills para reescribirlo: es una traducción, no una adaptación.",
    "   (Si un nombre propio o un término no se entiende, podés consultarlo con la skill `web-research`, sin cambiar el texto.)",
    `2. Guardá la traducción en un archivo JSON con solo estas claves: ${fields}` +
      (packet.tipo === "carrusel" ? ", y pieza.slides[0], pieza.slides[1]… para cada lámina" : "") +
      '. Ejemplo: {"pieza.hook": "…", "pieza.full_script": "…"}',
    `3. Escribila en la ficha con: python .kit/launch.py lab apply-translation --brand ${packet.brand} --id ${packet.id} --campos traduccion.json`,
    "4. Borrá traduccion.json y avisame. La reviso y la edito en Ideas antes de grabar.",
    "Después, si quiero hooks nuevos para grabarla, usá la skill `hooks`; para planificar el video, `story-plan`.",
    "",
    "Texto original:",
    "~~~text",
    packet.transcript_original,
    "~~~",
  ].join("\n");
}

function translation(item, brand, reload) {
  const box = card("Traducción fiel", "Sin giro, sin agregar ni quitar ideas");
  const done = item.redaccion?.modo === "traduccion_fiel";
  box.append(el("p", "muted", done ? "Ya está traducida. Podés editarla abajo." : "Tu agente traduce el texto original tal cual; vos después lo editás."));
  const original = input("textarea", { value: item.transcript_original || "" });
  original.rows = 5;
  original.readOnly = true;
  original.setAttribute("aria-label", "Transcripción original");
  box.append(el("p", "label", "Texto original"), original);
  if (!(item.transcript_original || "").trim()) {
    box.append(empty("Sin transcripción todavía. Pedile a tu agente que la saque del link."));
    return box;
  }
  const ask = button("Preparar pedido para tu agente", "btn", async () => {
    try {
      const { packet } = await api(`/api/lab/translation-packet?${q(brand)}&id=${encodeURIComponent(item.id)}`);
      state.packet = packet;
      reload();
    } catch (e) { toast(e.message, "error"); }
  });
  box.append(ask);
  if (state.packet?.id === item.id) {
    box.append(el("p", "hint", state.packet.contrato),
      button("Copiar pedido", "btn btn--primary", () => copyText(handoff(state.packet))));
  }
  return box;
}

function editor(item, brand, reload, ctx) {
  const pieza = item.pieza || {};
  const box = card("Tu versión", "Editá antes de grabar");
  const fields = item.tipo === "carrusel" ? [["headline", "Título del carrusel", 2]] : [["hook", "Hook", 2], ["full_script", "Guion completo", 10]];
  const inputs = {};
  fields.forEach(([key, label, rows]) => {
    const f = input("textarea", { value: pieza[key] || "" });
    f.rows = rows;
    f.setAttribute("aria-label", label);
    inputs[key] = f;
    box.append(el("p", "label", label), f);
  });
  const slides = item.tipo === "carrusel" ? (pieza.slides || []).map((s, i) => {
    const f = input("textarea", { value: typeof s === "string" ? s : JSON.stringify(s) });
    f.rows = 2;
    f.setAttribute("aria-label", `Lámina ${i + 1}`);
    box.append(el("p", "label", `Lámina ${i + 1}`), f);
    return f;
  }) : [];
  const notes = input("textarea", { value: item.notas || "", placeholder: "Notas" });
  notes.rows = 2;
  box.append(el("p", "label", "Notas"), notes);
  const actions = el("div", "actions");
  actions.append(
    button("Guardar", "btn btn--primary", async () => {
      const next = Object.fromEntries(Object.entries(inputs).map(([k, f]) => [k, f.value]));
      if (slides.length) next.slides = slides.map((f) => f.value);
      try { await api("/api/lab/item", { brand: brand.id, id: item.id, pieza: next, notas: notes.value }); toast("Guardado"); reload(); } catch (e) { toast(e.message, "error"); }
    }),
    button("Pasar a guion", "btn", async () => {
      try {
        await api("/api/guion", { titulo: item.tema || item.id, hook: inputs.hook?.value || inputs.headline?.value || "",
          cuerpo: inputs.full_script?.value || slides.map((f) => f.value).join("\n\n"), brand: brand.id,
          tema: item.tema || "", fuente: "content-lab" });
        toast("Guion creado");
        ctx.go("guion");
      } catch (e) { toast(e.message, "error"); }
    }),
    button(item.archivada ? "Sacar del archivo" : "Archivar", "btn btn--quiet", async () => {
      try { await api("/api/lab/archive", { brand: brand.id, id: item.id, archivar: !item.archivada }); reload(); } catch (e) { toast(e.message, "error"); }
    }),
    button("Borrar", "btn btn--danger", async () => {
      if (!window.confirm(`¿Borrar «${item.tema || item.id}»? No se puede deshacer.`)) return;
      try { await api("/api/lab/delete", { brand: brand.id, id: item.id }); state.open = null; reload(); } catch (e) { toast(e.message, "error"); }
    }),
  );
  box.append(actions);
  return box;
}

function referencias(root, data, brand, reload, ctx) {
  const wrap = el("div", "stack");
  if (data.error) return wrap.append(errorLine("Content Lab no disponible", data.error)), wrap;
  const items = data.items || [];
  const current = items.find((i) => i.id === state.open);
  const layout = el("div", "grid grid--sidebar");
  const side = el("div", "stack");
  side.append(newReference(brand, reload));
  const list = card("Tus referencias", `${items.filter((i) => !i.archivada).length} activas`);
  if (!items.length) list.append(empty("Todavía no guardaste ninguna."));
  const gallery = el("div", "item-grid");
  items.forEach((i) => gallery.append(itemCard(i)));
  gallery.addEventListener("reopen", reload);
  list.append(gallery);
  side.append(list);
  const detail = el("div", "stack");
  if (current) detail.append(analysis(current), translation(current, brand, reload), editor(current, brand, reload, ctx));
  else {
    const hint = card(null, "Elegí una referencia");
    hint.append(empty("Abrí una referencia para ver su análisis y editar tu versión."));
    detail.append(hint);
  }
  layout.append(side, detail);
  wrap.append(layout);
  return wrap;
}

function misIdeas(tasks, brand, reload, ctx) {
  const wrap = el("div", "grid grid--2");
  const box = card("Tus ideas", "Anotá sin filtro");
  if (tasks.error) box.append(errorLine("Ideas no disponibles", tasks.error));
  const ideas = (tasks.tasks || []).filter((t) => t.stage === "idea" && t.status !== "done");
  if (!ideas.length && !tasks.error) box.append(empty("Sin ideas todavía. La meta del primer día: 10."));
  ideas.forEach((t) => {
    const row = el("div", "row");
    row.append(el("span", "row-main", t.title), button("Escribir guion", "btn btn--small", async () => {
      try {
        await api("/api/guion", { titulo: t.title, cuerpo: "", brand: brand.id, task_code: t.code });
        await api("/api/tasks/update", { code: t.code, stage: "guion_listo" });
        ctx.go("guion");
      } catch (e) { toast(e.message, "error"); }
    }));
    box.append(row);
  });
  inlineAdd(box, { label: "+ Nueva idea", placeholder: "Una idea por línea y Enter",
    create: (title) => api("/api/tasks", { source_id: crypto.randomUUID(), ecosystem: brand.id, title, stage: "idea", status: "open" }),
    onCreated: reload });

  const ask = card("Pedile ideas a tu agente", "Con un tema o una referencia");
  const topic = input("text", { placeholder: "Tema (por ejemplo: ahorro, rutina, tu oficio)" });
  const ref = input("text", { placeholder: "Referencia o link (opcional)" });
  const out = el("div");
  ask.append(topic, ref, button("Preparar pedido", "btn btn--primary", async () => {
    try {
      const { order } = await api("/api/lab/idea-request", { brand: brand.id, topic: topic.value, reference: ref.value });
      out.replaceChildren(el("p", "hint", `Pedido listo (${order.id}).`),
        button("Copiar mensaje para tu agente", "btn", () => copyText(`Leé el pedido de ideas ${order.id} del Content Lab y proponé 10 ideas.`)));
    } catch (e) { toast(e.message, "error"); }
  }), out);
  wrap.append(box, ask);
  return wrap;
}

export async function render(root, ctx) {
  const brand = ctx.creatorBrand;
  const head = masthead(["Content Lab", brand?.name || "Sin marca"], "Ideas y Content Lab", "Referencias que te gustan y tus propias ideas");
  if (!brand) return root.replaceChildren(head, noBrand());
  const reload = () => render(root, ctx);
  const [items, tasks] = await Promise.all([safe(api(`/api/lab/items?${q(brand)}`)),
    safe(api(`/api/tasks?ecosystem=${encodeURIComponent(brand.id)}`))]);
  const tabs = pills([["referencias", "Referencias"], ["ideas", "Mis ideas"]], state.tab, (k) => { state.tab = k; reload(); });
  head.append(brandPicker(ctx));
  root.replaceChildren(head, tabs, state.tab === "ideas" ? misIdeas(tasks, brand, reload, ctx) : referencias(root, items, brand, reload, ctx));
}
