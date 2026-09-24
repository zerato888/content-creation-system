// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// One template for every brand in cc.config.json: tasks, milestones ("hitos" = tasks with
// area "hito") and, with the `metricas` module on, the connected metrics of that brand.
import {
  api, brandMark, button, card, compact, el, empty, errorLine, fileToBase64, formatDateTime, inlineAdd, input, masthead, safe,
  select, toast,
} from "../lib.js";

const STATUS = [["backlog", "Pendiente"], ["open", "Abierta"], ["in_progress", "En curso"], ["done", "Hecha"]];
const PRIORITY = [["high", "Alta"], ["medium", "Media"], ["low", "Baja"]];
const HITO = "hito";

function field(task, key, node, reload) {
  node.addEventListener("change", async () => {
    const value = node.value.trim() || null;
    if (value === (task[key] || null)) return;
    node.disabled = true;
    try { await api("/api/tasks/update", { code: task.code, [key]: value }); reload(); } catch (e) { node.disabled = false; toast(e.message, "error"); }
  });
  node.setAttribute("aria-label", `${key} de ${task.code}`);
  return node;
}

function tasksPanel(brand, tasks, reload) {
  const box = card("Tareas", brand.name);
  const active = tasks.filter((t) => t.status !== "done" && t.area !== HITO);
  if (!active.length) box.append(empty(`No hay tareas activas de ${brand.name}.`));
  else {
    const table = el("div", "task-table");
    const head = el("div", "task-row task-row--head");
    ["Código", "Tarea", "Prioridad", "Fecha", "Estado"].forEach((h) => head.append(el("span", "", h)));
    table.append(head);
    active.slice(0, 50).forEach((t) => {
      const row = el("div", "task-row");
      row.append(el("span", "label", t.code),
        field(t, "title", input("text", { value: t.title }), reload),
        field(t, "priority", select(PRIORITY, t.priority || "medium"), reload),
        field(t, "due_date", input("date", { value: t.due_date || "" }), reload),
        field(t, "status", select(STATUS, t.status), reload));
      table.append(row);
    });
    box.append(table);
  }
  inlineAdd(box, { label: "+ Agregar tarea", create: (title) => api("/api/tasks",
    { source_id: crypto.randomUUID(), ecosystem: brand.id, title, status: "backlog" }), onCreated: reload });
  return box;
}

function hitosPanel(brand, tasks, reload) {
  const hitos = tasks.filter((t) => t.area === HITO);
  const done = hitos.filter((t) => t.status === "done").length;
  const box = card("Hitos", "Lo grande de esta marca", "instrument--focus");
  if (hitos.length) {
    const bar = el("span", "bar bar--wide");
    const fill = el("i");
    fill.style.width = `${Math.round((done / hitos.length) * 100)}%`;
    bar.append(fill);
    box.append(el("p", "muted", `${done} de ${hitos.length} logrados`), bar);
  } else box.append(empty("Sin hitos todavía."));
  hitos.forEach((t) => {
    const row = el("div", `row${t.status === "done" ? " is-done" : ""}`);
    const check = el("input", "check");
    check.type = "checkbox";
    check.checked = t.status === "done";
    check.setAttribute("aria-label", `Hito logrado: ${t.title}`);
    check.addEventListener("change", async () => {
      try { await api("/api/tasks/complete", { code: t.code, status: check.checked ? "done" : "open" }); reload(); } catch (e) { toast(e.message, "error"); }
    });
    row.append(check, el("span", "row-main", t.title));
    box.append(row);
  });
  inlineAdd(box, { label: "+ Agregar hito", create: (title) => api("/api/tasks",
    { source_id: crypto.randomUUID(), ecosystem: brand.id, title, area: HITO, status: "open" }), onCreated: reload });
  return box;
}

function metricsPanel(brand, data, reload) {
  const box = card("Métricas conectadas", brand.metrics?.provider && brand.metrics.provider !== "none" ? brand.metrics.provider : "Sin conector");
  const provider = brand.metrics?.provider || "none";
  if (provider === "none") return box.append(empty("Esta marca no tiene conector. Anotá las vistas a mano en Inicio.")), box;
  if (data.error) box.append(errorLine("Métricas no disponibles", data.error));
  const m = data.metrics;
  if (!m) box.append(empty("Todavía no se trajeron métricas."));
  else {
    const stats = el("div", "stats");
    Object.entries(m.totals || {}).forEach(([k, v]) => {
      const s = el("article", "stat");
      s.append(el("p", "label", k.replace(/_/g, " ")), el("strong", "stat-value", k.endsWith("_pct") ? `${v}%` : compact(v)));
      stats.append(s);
    });
    box.append(stats, el("p", "hint", `Actualizado: ${formatDateTime(m.fetched_at)}`));
  }
  const refresh = button("Actualizar ahora", "btn", async () => {
    refresh.disabled = true;
    try { await api("/api/metrics/refresh", { brand: brand.id }); toast("Métricas actualizadas"); reload(); } catch (e) { refresh.disabled = false; toast(e.message, "error"); }
  });
  box.append(refresh);
  return box;
}

function logoUpload(brand, ctx) {
  const pick = el("input");
  pick.type = "file";
  pick.accept = "image/png,image/jpeg,image/webp";
  pick.hidden = true;
  pick.addEventListener("change", async () => {
    const file = pick.files?.[0];
    pick.value = "";
    if (!file) return;
    if (file.size > 1024 * 1024) return toast("El logo pesa más de 1 MB", "error");
    try {
      await api("/api/brand/logo", { brand: brand.id, data: await fileToBase64(file) });
      ctx.logoVersion += 1;
      await ctx.reloadConfig();
      toast("Logo guardado");
    } catch (e) { toast(e.message, "error"); }
  });
  const b = button(ctx.logos.includes(brand.id) ? "Cambiar logo" : "Subir logo", "btn btn--quiet btn--small", () => pick.click());
  const wrap = el("span");
  wrap.append(b, pick);
  return wrap;
}

export async function render(root, ctx, brandId) {
  const brand = ctx.brands.find((b) => b.id === brandId);
  const reload = () => render(root, ctx, brandId);
  const withMetrics = ctx.enabled("metricas");
  const [tasks, metrics] = await Promise.all([safe(api(`/api/tasks?ecosystem=${encodeURIComponent(brand.id)}`)),
    withMetrics ? safe(api(`/api/metrics?brand=${encodeURIComponent(brand.id)}`)) : Promise.resolve(null)]);
  const head = masthead([brand.name, "Operación"], brand.name, brand.kind === "personal-brand" ? "Tu marca personal" : "Marca");
  head.prepend(brandMark(brand, ctx));
  head.append(logoUpload(brand, ctx));
  const grid = el("div", "grid grid--main-side");
  const main = el("div", "stack");
  const side = el("div", "stack");
  if (tasks.error) main.append(errorLine("Tareas no disponibles", tasks.error));
  else {
    main.append(tasksPanel(brand, tasks.tasks || [], reload));
    side.append(hitosPanel(brand, tasks.tasks || [], reload));
  }
  if (metrics) main.append(metricsPanel(brand, metrics, reload));
  grid.append(main, side);
  root.replaceChildren(head, grid);
}
