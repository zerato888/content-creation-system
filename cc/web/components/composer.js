// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// "Agregar tarea" dialog: title, where it goes (one of your brands or Vida Personal), priority, due date.
import { api, button, el, input, select, toast } from "../lib.js";

const PRIORITIES = [["high", "Alta"], ["medium", "Media"], ["low", "Baja"]];

// places: [[ecosystemId, label], ...]. Resolves after the task is created (or the dialog is cancelled).
export function openComposer({ places, onCreated = () => {}, trigger = document.activeElement }) {
  const dialog = el("dialog", "dialog");
  dialog.setAttribute("aria-labelledby", "composer-title");
  const form = el("form", "dialog-form");
  form.method = "dialog";
  const heading = el("h2", "card-title", "Agregar tarea");
  heading.id = "composer-title";
  const title = input("text", { placeholder: "¿Qué hay que hacer?" });
  title.required = true;
  title.setAttribute("aria-label", "Título");
  const where = select(places, places[0]?.[0]);
  where.setAttribute("aria-label", "Dónde va");
  const priority = select(PRIORITIES, "medium");
  priority.setAttribute("aria-label", "Prioridad");
  const due = input("date");
  due.setAttribute("aria-label", "Fecha límite (opcional)");
  const error = el("p", "empty is-error");
  error.hidden = true;
  error.setAttribute("role", "alert");
  const cancel = button("Cancelar", "btn btn--quiet", () => dialog.close());
  const submit = el("button", "btn btn--primary", "Crear tarea");
  submit.type = "submit";
  form.append(heading, title, ...(places.length > 1 ? [where] : []), priority, due, error, cancel, submit);
  dialog.append(form);
  dialog.addEventListener("close", () => { dialog.remove(); trigger?.focus?.(); }, { once: true });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    error.hidden = true;
    submit.disabled = true;
    try {
      const body = { source_id: crypto.randomUUID(), ecosystem: where.value, title: title.value.trim(),
        priority: priority.value, status: "open" };
      if (due.value) body.due_date = due.value;
      const { task } = await api("/api/tasks", body);
      dialog.close();
      toast(`Tarea creada: ${task.code}`);
      onCreated(task);
    } catch (e) {
      error.textContent = e.message;
      error.hidden = false;
      submit.disabled = false;
    }
  });
  document.body.append(dialog);
  dialog.showModal();
  title.focus();
  return dialog;
}
