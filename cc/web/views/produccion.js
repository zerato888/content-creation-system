// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Content Lab avanzado (module `produccion_avanzada`): productions, orders, delivery review, templates.
import { api, button, card, el, empty, errorLine, formatDateTime, input, masthead, pills, safe, select, toast } from "../lib.js";

const STATE_LABEL = {
  draft: "Borrador", content_review: "Revisión de contenido", ready_to_produce: "Lista para producir",
  not_started: "Sin empezar", in_production: "En producción", delivery_review: "Revisión de entrega", finished: "Terminada",
  not_required: "Sin publicar", ready_to_publish: "Lista para publicar", scheduled: "Programada", published: "Publicada", closed: "Cerrada",
};
const state = { tab: "producciones", open: null };
const label = (s) => STATE_LABEL[s] || s || "—";

const lines = (text) => text.split("\n").map((l) => l.trim()).filter(Boolean);
const save = (p, patch, ok, reload) => api("/api/lab/production", { id: p.id, expected_revision: p.revision, ...patch })
  .then(() => { toast(ok); reload(); }, (e) => toast(e.message, "error"));

// An action whose prerequisite is not met is shown disabled, with the reason next to it.
function gated(labelText, cls, reason, onClick) {
  const wrap = el("div", "stack stack--tight");
  const b = button(labelText, cls, onClick);
  b.disabled = Boolean(reason);
  wrap.append(b);
  if (reason) wrap.append(el("p", "hint", reason));
  return wrap;
}

function contentEditor(p, reload) {
  const box = card("Contenido", "1 · Qué se produce");
  const format = select([["video", "Video"], ["carousel", "Carrusel"]], p.format);
  const mode = select([["script", "Guion aprobado"], ["freestyle", "Libre (desde archivos)"],
    ["selection", "Selección de archivos"], ["single", "Un archivo"]], p.input_mode);
  const text = input("textarea", { value: (p.approved_content || []).map((c) => (typeof c === "string" ? c : c.text)).join("\n"),
    placeholder: "Una línea por bloque (guion) o por lámina (carrusel)" });
  text.rows = 6;
  const sources = input("textarea", { value: (p.source_paths || []).join("\n"),
    placeholder: "Archivos de entrada, uno por línea, relativos a .kit-personal/data/" });
  sources.rows = 3;
  [[format, "Formato"], [mode, "Entrada"], [text, "Contenido aprobado"], [sources, "Archivos de entrada"]]
    .forEach(([f, l]) => { f.setAttribute("aria-label", l); box.append(el("p", "label", l), f); });
  box.append(el("p", "hint", "Cambiar el contenido lo vuelve a «Borrador»: después se revisa y aprueba de nuevo."),
    button("Guardar contenido", "btn", () => save(p, { format: format.value, input_mode: mode.value,
      approved_content: lines(text.value), source_paths: lines(sources.value) }, "Contenido guardado", reload)));
  const next = { draft: ["content_review", "Enviar a revisión"], content_review: ["ready_to_produce", "Aprobar el contenido"] }[p.content_state];
  const actions = el("div", "actions");
  if (next) actions.append(button(next[1], "btn btn--primary", () => save(p, { content_state: next[0] }, label(next[0]), reload)));
  if (p.content_state !== "draft") actions.append(button("Volver a borrador", "btn btn--quiet", () => save(p, { content_state: "draft" }, "Borrador", reload)));
  box.append(actions);
  return box;
}

function deliveryReview(p, reload) {
  const box = card("Entrega", "3 · Revisar lo producido");
  const paths = (p.delivery || {}).result_paths || [];
  const files = input("textarea", { value: paths.join("\n"), placeholder: "Archivos finales, uno por línea, relativos a .kit-personal/data/" });
  files.rows = 3;
  files.setAttribute("aria-label", "Archivos finales");
  box.append(el("p", "label", "Archivos finales"), files,
    button("Guardar archivos finales", "btn", () => save(p, { delivery: { ...(p.delivery || {}), result_paths: lines(files.value) },
      production_state: "delivery_review" }, "Archivos guardados", reload)));
  const approval = p.delivery_approval?.files || [];
  approval.forEach((f) => { const row = el("div", "row"); row.append(el("span", "row-main", f.path),
    el("span", "muted", f.duration_s ? `${Math.round(f.duration_s)} s` : `${f.width}×${f.height}`)); box.append(row); });
  const actions = el("div", "actions");
  actions.append(
    gated("Aprobar la entrega", "btn btn--primary", paths.length ? null : "Primero guardá los archivos finales.", async () => {
      if (!window.confirm("¿Revisaste los archivos finales y los aprobás?")) return;
      save(p, { approve_delivery: true }, "Entrega aprobada", reload);
    }),
    gated("Marcar como terminada", "btn", p.delivery_approved_at ? null : "Se puede terminar después de aprobar la entrega.",
      () => save(p, { production_state: "finished" }, "Terminada", reload)),
  );
  box.append(actions);
  return box;
}

function productionDetail(p, orders, reload) {
  const wrap = el("div", "stack");
  const box = card(p.title || p.id, `Revisión ${p.revision}`);
  [["Contenido", p.content_state], ["Producción", p.production_state], ["Publicación", p.publication_state]]
    .forEach(([k, v]) => { const row = el("p", "kv"); row.append(el("span", "label", k), el("span", "", label(v))); box.append(row); });
  if (p.delivery_approved_at) box.append(el("p", "muted", `Entrega aprobada: ${formatDateTime(p.delivery_approved_at)}`));
  const order = card("Pedido de producción", "2 · Mandar a producir");
  order.append(gated("Crear pedido de producción", "btn btn--primary",
    p.content_state === "ready_to_produce" ? null : "Se habilita cuando el contenido está aprobado (paso 1).", async () => {
      try { await api("/api/lab/order", { production_id: p.id, expected_revision: p.revision }); toast("Pedido creado"); reload(); } catch (e) { toast(e.message, "error"); }
    }));
  const mine = orders.filter((o) => o.production_id === p.id);
  order.append(el("p", "label", "Pedidos"));
  if (!mine.length) order.append(empty("Sin pedidos."));
  mine.forEach((o) => { const row = el("div", "row"); row.append(el("span", "row-main", o.id), el("span", "chip", o.execution_state || "—")); order.append(row); });
  if (mine.length && p.production_state === "not_started") {
    order.append(button("Marcar en producción", "btn", () => save(p, { production_state: "in_production" }, "En producción", reload)));
  }
  wrap.append(box, contentEditor(p, reload), order, deliveryReview(p, reload));
  return wrap;
}

function productions(ctx, data, orders, reload) {
  const grid = el("div", "grid grid--sidebar");
  const side = card("Producciones", data.error ? null : `${(data.productions || []).length} en total`);
  const title = input("text", { placeholder: "Nombre de la producción" });
  const brand = select(ctx.brands.map((b) => [b.id, b.name]), ctx.creatorBrand?.id);
  side.append(title, brand, button("Crear", "btn btn--primary", async () => {
    if (!title.value.trim()) return title.focus();
    try { const r = await api("/api/lab/production", { title: title.value.trim(), ecosystem: brand.value }); state.open = r.production.id; reload(); } catch (e) { toast(e.message, "error"); }
  }));
  if (data.error) side.append(errorLine("No disponible", data.error));
  const list = data.productions || [];
  if (!list.length && !data.error) side.append(empty("Todavía no hay producciones."));
  list.forEach((p) => {
    const b = el("button", `item-card${p.id === state.open ? " is-on" : ""}`);
    b.type = "button";
    b.append(el("span", "label", label(p.production_state)), el("strong", "", p.title || p.id));
    b.addEventListener("click", () => { state.open = p.id; reload(); });
    side.append(b);
  });
  const current = list.find((p) => p.id === state.open);
  const detail = current ? productionDetail(current, orders.orders || [], reload) : card(null, "Elegí una producción");
  grid.append(side, detail);
  return grid;
}

function templates(data) {
  const box = card("Plantillas", "Configuraciones reusables");
  if (data.error) return box.append(errorLine("No disponible", data.error)), box;
  if (!data.templates?.length) return box.append(empty("Sin plantillas. Tu agente las crea cuando repetís un formato.")), box;
  data.templates.forEach((t) => { const row = el("div", "row"); row.append(el("span", "row-main", t.name || t.title || t.id), el("span", "muted", `rev. ${t.revision}`)); box.append(row); });
  return box;
}

export async function render(root, ctx) {
  const reload = () => render(root, ctx);
  const [prods, orders, tpls] = await Promise.all([safe(api("/api/lab/productions")), safe(api("/api/lab/orders")),
    safe(api("/api/lab/templates"))]);
  const head = masthead(["Content Lab", "Producción"], "Producción avanzada", "Producciones, pedidos, revisión de entrega y plantillas");
  const tabs = pills([["producciones", "Producciones"], ["plantillas", "Plantillas"]], state.tab, (k) => { state.tab = k; reload(); });
  root.replaceChildren(head, tabs, state.tab === "plantillas" ? templates(tpls) : productions(ctx, prods, orders, reload));
}
