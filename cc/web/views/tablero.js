// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Tablero: 3 columns (Idea / Guion listo / Publicado); advanced mode shows 4 (adds Grabado).
import { api, brandPicker, button, el, empty, errorLine, inlineAdd, masthead, noBrand, safe, toast } from "../lib.js";

const SIMPLE = [["idea", "Idea", ["idea"]], ["guion_listo", "Guion listo", ["guion_listo", "grabado", "editado"]],
  ["publicado", "Publicado", ["publicado"]]];
const ADVANCED = [["idea", "Idea", ["idea"]], ["guion_listo", "Guion listo", ["guion_listo"]],
  ["grabado", "Grabado", ["grabado", "editado"]], ["publicado", "Publicado", ["publicado"]]];
const LABEL = { idea: "Idea", guion_listo: "Guion listo", grabado: "Grabado", editado: "Editado", publicado: "Publicado" };
const MODE_KEY = "cc-board-advanced";

function advanced() { try { return localStorage.getItem(MODE_KEY) === "1"; } catch { return false; } }

async function move(task, stage, reload) {
  try { await api("/api/tasks/update", { code: task.code, stage }); reload(); } catch (e) { toast(e.message, "error"); }
}

function taskCard(task, columns, index, reload) {
  const box = el("article", "board-card");
  box.append(el("span", "label", task.code), el("strong", "", task.title));
  if (task.stage !== columns[index][0]) box.append(el("span", "badge", LABEL[task.stage] || task.stage));
  const nav = el("div", "actions actions--tight");
  [[-1, "←"], [1, "→"]].forEach(([step, arrow]) => {
    const target = columns[index + step];
    if (!target) return;
    const b = button(arrow, "btn btn--small", () => move(task, target[0], reload));
    b.setAttribute("aria-label", `Mover «${task.title}» a ${target[1]}`);
    nav.append(b);
  });
  box.append(nav);
  return box;
}

export async function render(root, ctx) {
  const brand = ctx.creatorBrand;
  const head = masthead(["Tablero", brand?.name || "Sin marca"], "Tablero", "De la idea al video publicado");
  if (!brand) return root.replaceChildren(head, noBrand());
  const reload = () => render(root, ctx);
  const data = await safe(api(`/api/tasks?ecosystem=${encodeURIComponent(brand.id)}`));
  const isAdvanced = advanced();
  const toggle = button(isAdvanced ? "Modo simple (3 columnas)" : "Modo avanzado (4 columnas)", "btn btn--quiet", () => {
    try { localStorage.setItem(MODE_KEY, isAdvanced ? "0" : "1"); } catch { /* private mode */ }
    reload();
  });
  head.append(brandPicker(ctx), toggle);
  if (data.error) return root.replaceChildren(head, errorLine("Tablero no disponible", data.error));
  const columns = isAdvanced ? ADVANCED : SIMPLE;
  const tasks = (data.tasks || []).filter((t) => t.stage && t.status !== "done");
  const board = el("div", `board board--${columns.length}`);
  columns.forEach(([key, label, stages], index) => {
    const col = el("section", "board-col instrument");
    const items = tasks.filter((t) => stages.includes(t.stage));
    const title = el("h3", "card-title", label);
    title.append(el("span", "count", ` ${items.length}`));
    col.append(title);
    if (!items.length) col.append(empty(index === 0 ? "Anotá tu primera idea." : "Nada acá todavía."));
    items.forEach((t) => col.append(taskCard(t, columns, index, reload)));
    if (key === "idea") {
      inlineAdd(col, { label: "+ Idea", placeholder: "Idea y Enter",
        create: (t) => api("/api/tasks", { source_id: crypto.randomUUID(), ecosystem: brand.id, title: t, stage: "idea", status: "open" }),
        onCreated: reload });
    }
    board.append(col);
  });
  root.replaceChildren(head, board, el("p", "hint", "«Ya grabé» en Guion mueve la tarjeta sola. Cuando publiques, pasala a «Publicado»."));
}
