// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Command palette (Ctrl/Cmd+K): jump to any screen, open a task's board, or add a task.
// Entries are plain data; nothing is written as HTML.
import { api, el, safe } from "../lib.js";

const fold = (v) => String(v || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function filterEntries(entries, query) {
  const needle = fold(query).trim();
  return needle ? entries.filter((e) => fold(`${e.label} ${e.type} ${e.meta}`).includes(needle)) : entries;
}

// getEntries() -> [{type, label, meta, run}]; called each time the palette opens so it is never stale.
export function mountPalette(getEntries) {
  const dialog = el("dialog", "palette");
  const heading = el("h2", "palette__title", "Ir a cualquier parte");
  heading.id = "palette-title";
  dialog.setAttribute("aria-labelledby", heading.id);
  const field = el("input", "field");
  field.type = "search";
  field.placeholder = "Escribí para buscar";
  field.setAttribute("aria-label", "Buscar pantallas, tareas o acciones");
  const status = el("p", "hint");
  status.setAttribute("aria-live", "polite");
  const list = el("div", "palette__list");
  list.setAttribute("role", "listbox");
  dialog.append(heading, field, status, list);
  document.body.append(dialog);

  let entries = [];
  let shown = [];
  let index = 0;
  let back = null;

  const draw = () => {
    shown = filterEntries(entries, field.value).slice(0, 40);
    index = Math.min(index, Math.max(0, shown.length - 1));
    list.replaceChildren(...shown.map((e, i) => {
      const b = el("button", "palette__item");
      b.type = "button";
      b.setAttribute("role", "option");
      b.setAttribute("aria-selected", String(i === index));
      b.append(el("span", "chip", e.type), el("strong", "", e.label), el("small", "muted", e.meta || ""));
      b.addEventListener("click", () => { index = i; choose(); });
      return b;
    }));
    status.textContent = shown.length ? `${shown.length} resultados · ↑↓ · Enter · Esc` : "Sin resultados";
    list.querySelector('[aria-selected="true"]')?.scrollIntoView({ block: "nearest" });
  };
  const choose = () => { const e = shown[index]; if (e) { dialog.close(); e.run(); } };

  const open = async () => {
    if (dialog.open) return;
    back = document.activeElement;
    field.value = "";
    index = 0;
    entries = [];
    draw();
    dialog.showModal();
    field.focus();
    entries = await getEntries();
    draw();
  };

  field.addEventListener("input", () => { index = 0; draw(); });
  dialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") { event.preventDefault(); dialog.close(); return; }
    if (!shown.length) return;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      index = (index + (event.key === "ArrowDown" ? 1 : -1) + shown.length) % shown.length;
      draw();
    } else if (event.key === "Enter") { event.preventDefault(); choose(); }
  });
  dialog.addEventListener("close", () => back?.focus?.());
  window.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); open(); }
  });
  return { open };
}

export async function taskEntries(go) {
  const data = await safe(api("/api/tasks"));
  return (data.tasks || []).filter((t) => t.status !== "done").map((t) => ({
    type: "Tarea", label: t.title, meta: t.code, run: () => go(t.ecosystem),
  }));
}
