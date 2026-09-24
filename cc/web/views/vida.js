// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Vida Personal: finances (income vs goal, fixed payments, shopping list, goals) and
// tasks + habits (weekly matrix, 30-day consistency, milestones). Everything comes from
// cc.config.json and the local data; with an empty config it simply shows nothing.
import {
  api, areaPath, button, card, el, empty, errorLine, formatDate, inlineAdd, input, masthead, money, pills, safe,
  select, smoothPath, svg, todayIso, toast,
} from "../lib.js";

const AREA_FIXED = "Pagos Fijos";
const AREA_SHOPPING = "Compras";
const AREA_MONTH = "Objetivos del mes";
const TASK_GROUPS = ["Nuevos", "Por hacer"];
const SHOPPING_CATEGORIES = ["Casa", "Comida", "Otros"];
const PRIORITIES = [["high", "Alta"], ["medium", "Media"], ["low", "Baja"]];
const DAY_LABELS = ["L", "M", "M", "J", "V", "S", "D"];
const VIDA = "vida";   // built-in task ecosystem of Vida Personal
let tab = "finanzas";
let disposeChart = () => {};

const period = () => todayIso().slice(0, 7);
const post = (path, body) => api(path, body);

async function act(promise, reload) {
  try { await promise; reload(); } catch (e) { toast(e.message, "error"); }
}

// ------------------------------------------------------------ tasks
function checkRow(task, reload, { amount = false } = {}) {
  const row = el("div", `row${task.status === "done" ? " is-done" : ""}`);
  const check = el("input", "check");
  check.type = "checkbox";
  check.checked = task.status === "done";
  check.setAttribute("aria-label", `Completar ${task.title}`);
  check.addEventListener("change", () => act(task.code
    ? post("/api/tasks/complete", { code: task.code, status: check.checked ? "done" : "open" })
    : post("/api/life/tasks/complete", { id: task.id, done: check.checked }), reload));
  row.append(check, el("span", "row-main", task.title));
  if (task.due_date) row.append(el("span", "chip", formatDate(task.due_date, { day: "numeric", month: "short" })));
  if (amount && task.amount) row.append(el("span", "muted", money(task.amount)));
  return row;
}

function renderTasks(data, reload) {
  const box = card("Tareas", "Tareas y hábitos");
  if (data.error) return box.append(errorLine("Tareas no disponibles", data.error)), box;
  const tasks = (data.tasks || []).filter((t) => t.area !== AREA_MONTH);
  if (!tasks.length) box.append(empty("No hay tareas personales todavía."));
  TASK_GROUPS.forEach((group) => {
    const items = tasks.filter((t) => (TASK_GROUPS.includes(t.area) ? t.area : TASK_GROUPS[0]) === group)
      .sort((a, b) => (a.status === "done") - (b.status === "done"));
    if (!items.length) return;
    box.append(el("p", "label", group));
    items.forEach((t) => box.append(checkRow(t, reload)));
  });
  inlineAdd(box, { label: "+ Agregar tarea", create: (title) => post("/api/tasks",
    { source_id: crypto.randomUUID(), ecosystem: VIDA, title, area: TASK_GROUPS[0], status: "open" }), onCreated: reload });
  return box;
}

function renderMonthGoals(data, reload) {
  const box = card("Objetivos del mes", null, "instrument--side");
  const items = (data.tasks || []).filter((t) => t.area === AREA_MONTH);
  if (!items.length) box.append(empty("Sin objetivos todavía."));
  items.forEach((t) => box.append(checkRow(t, reload)));
  inlineAdd(box, { label: "+ Agregar objetivo", create: (title) => post("/api/tasks",
    { source_id: crypto.randomUUID(), ecosystem: VIDA, title, area: AREA_MONTH, status: "open" }), onCreated: reload });
  return box;
}

// ------------------------------------------------------------ habits
function renderHabits(week, reload) {
  const box = card("Hábitos de la semana", "Se reinicia cada lunes");
  if (week.error) return box.append(errorLine("Hábitos no disponibles", week.error)), box;
  if (!week.habits?.length) {
    return box.append(empty("No configuraste hábitos. Pedile a tu agente: «agregá el hábito leer, de lunes a viernes».")), box;
  }
  const total = week.habits.reduce((n, h) => n + h.days.filter((c) => c.applies).length, 0);
  const done = week.habits.reduce((n, h) => n + h.days.filter((c) => c.done).length, 0);
  box.append(el("p", "muted", `${done} de ${total} esta semana`));
  const table = el("table", "habit-table");
  const head = el("tr");
  head.append(el("th"));
  DAY_LABELS.forEach((d) => head.append(el("th", "", d)));
  head.append(el("th", "", `${week.consistency?.since_days || 30} días`));
  const thead = el("thead");
  thead.append(head);
  const tbody = el("tbody");
  week.habits.forEach((habit) => {
    const tr = el("tr");
    tr.append(el("th", "habit-name", habit.label));
    habit.days.forEach((cell) => {
      const td = el("td");
      if (!cell.applies) td.append(el("span", "muted", "—"));
      else {
        const b = button(cell.done ? "✓" : "", `status${cell.done ? " is-done" : ""}`, () => act(
          post("/api/life/habits", { habit_id: habit.id, date: cell.date, done: !cell.done }), reload));
        b.setAttribute("aria-label", `${habit.label}, ${formatDate(cell.date)}: ${cell.done ? "hecho" : "pendiente"}`);
        td.append(b);
      }
      tr.append(td);
    });
    const pct = week.consistency?.habits?.find((h) => h.id === habit.id)?.pct ?? 0;
    const bar = el("td", "bar-cell");
    const track = el("span", "bar");
    const fill = el("i");
    fill.style.width = `${pct}%`;
    track.append(fill);
    bar.append(track, el("span", "muted", ` ${pct}%`));
    tr.append(bar);
    tbody.append(tr);
  });
  table.append(thead, tbody);
  const scroller = el("div", "table-scroll");
  scroller.append(table);
  box.append(scroller);
  return box;
}

function renderConsistency(stats) {
  const box = card(null, "Constancia de los últimos 30 días", "instrument--side");
  if (!stats) return box.append(empty("No disponible")), box;
  box.append(el("p", "big-number", `${stats.overall_pct}%`));
  const ul = el("ul", "plain-list");
  stats.habits.forEach((h) => { const li = el("li", "row"); li.append(el("span", "row-main", h.label), el("strong", "", `${h.pct}%`)); ul.append(li); });
  box.append(ul);
  return box;
}

function renderMilestones(goals) {
  const box = card("Hitos", "Lo grande que querés lograr", "instrument--side");
  if (goals.error) return box.append(errorLine("Hitos no disponibles", goals.error)), box;
  const list = goals.goals || [];
  if (!list.length) return box.append(empty("Sin hitos. Agregalos en Finanzas › Metas o con el onboarding.")), box;
  const done = list.filter((g) => g.done).length;
  const bar = el("span", "bar bar--wide");
  const fill = el("i");
  fill.style.width = `${Math.round((done / list.length) * 100)}%`;
  bar.append(fill);
  box.append(el("p", "muted", `${done} de ${list.length} logrados`), bar);
  const ul = el("ul", "plain-list");
  list.forEach((g) => { const li = el("li", `row${g.done ? " is-done" : ""}`); li.append(el("span", `status${g.done ? " is-done" : ""}`, g.done ? "✓" : ""), el("span", "row-main", g.title)); ul.append(li); });
  box.append(ul);
  return box;
}

// ------------------------------------------------------------ income
function incomeChart(history, goal, currency) {
  if (history.length < 2) return empty("El histórico aparece cuando tengas al menos dos meses.");
  const region = el("div", "chart-wrap");
  const node = svg("svg", { class: "chart", role: "img", "aria-label": "Histórico mensual de ingresos" });
  region.append(node);
  const draw = () => {
    const width = Math.max(320, Math.round(region.clientWidth || 320)), height = 240;
    const top = 20, bottom = 30, left = 10, right = 18, baseline = height - bottom;
    const maxVal = Math.max(1, (goal || 0) * 1.04, ...history.map((h) => Number(h.total) || 0));
    const stepX = (width - left - right) / (history.length - 1);
    const y = (v) => baseline - (Number(v) / maxVal) * (baseline - top);
    const points = history.map((h, i) => ({ x: left + i * stepX, y: y(h.total) }));
    node.setAttribute("viewBox", `0 0 ${width} ${height}`);
    node.replaceChildren(svg("path", { d: areaPath(points, baseline), class: "chart-area" }),
      svg("path", { d: smoothPath(points), class: "chart-line" }));
    if (goal) {
      const label = svg("text", { x: width - right, y: y(goal) - 6, class: "chart-goal-label", "text-anchor": "end" });
      label.textContent = `Meta ${money(goal, currency)}`;
      node.append(svg("line", { x1: left, y1: y(goal), x2: width - right, y2: y(goal), class: "chart-goal" }), label);
    }
    const every = Math.max(1, Math.ceil(history.length / 6));
    history.forEach((h, i) => {
      if ((history.length - 1 - i) % every) return;
      const t = svg("text", { x: points[i].x, y: height - 8, class: "chart-label", "text-anchor": i === 0 ? "start" : "middle" });
      const [yy, mm] = h.period.split("-").map(Number);
      t.textContent = formatDate(`${yy}-${String(mm).padStart(2, "0")}-01`, { month: "short", year: "2-digit" });
      const title = svg("title");
      title.textContent = `${h.period}: ${money(h.total, currency)}`;
      t.append(title);
      node.append(t);
    });
  };
  const observer = new ResizeObserver(() => (region.isConnected ? draw() : observer.disconnect()));
  observer.observe(region);
  disposeChart = () => observer.disconnect();
  draw();
  return region;
}

function stat(label, value, note) {
  const box = el("article", "stat");
  box.append(el("p", "label", label), el("strong", "stat-value", value));
  if (note) box.append(el("p", "muted", note));
  return box;
}

function renderIncome(view, history, reload) {
  const box = card(null, "Ingresos");
  if (view.error) return box.append(errorLine("Ingresos no disponibles", view.error)), box;
  const cur = view.currency;
  const month = formatDate(`${view.year}-${String(view.month).padStart(2, "0")}-01`, { month: "long", year: "numeric" });
  box.append(el("h3", "card-title", month.charAt(0).toUpperCase() + month.slice(1)));
  const stats = el("div", "stats");
  (view.recurring || []).forEach((r) => stats.append(stat(r.label, money(r.amount, cur), "fijo")));
  stats.append(stat("Extra recibido", money(view.manual.summary.recibido, cur), view.manual.summary.recibido ? "anotado a mano" : "todavía nada"),
    stat("Extra esperado", money(view.manual.summary.proyectado, cur), "todavía no llegó"),
    stat("Total del mes", money(view.total_recibido, cur), view.goal ? `Meta: ${money(view.goal, cur)}` : "Sin meta configurada"));
  if (view.fx_rate) stats.append(stat("Tipo de cambio", String(view.fx_rate), "de tu configuración"));
  box.append(stats);
  if (view.goal) {
    const bar = el("span", "bar bar--wide");
    const fill = el("i");
    fill.style.width = `${Math.min(100, Math.round((view.total_recibido / view.goal) * 100))}%`;
    bar.append(fill);
    box.append(bar);
  }
  const form = el("div", "inline-form");
  const amount = input("number", { placeholder: `Monto (${cur})` });
  amount.min = "0";
  const kind = select([["recibido", "Recibido"], ["proyectado", "Esperado"]], "recibido");
  const source = input("text", { placeholder: "De dónde (opcional)" });
  form.append(amount, kind, source, button("Anotar ingreso", "btn btn--primary", () => {
    const n = Number(amount.value);
    if (!n) return amount.focus();
    act(post("/api/life/income", { kind: kind.value, amount: n, source: source.value.trim() || null }), reload);
  }));
  box.append(form);
  if (!history.error) box.append(el("p", "label", "Histórico mensual"), incomeChart(history.history || [], history.goal, cur));
  return box;
}

function renderFixed(life, reload) {
  const box = card("Pagos fijos del mes", "Finanzas");
  if (life.error) return box.append(errorLine("Pagos no disponibles", life.error)), box;
  const items = (life.tasks || []).filter((t) => t.area === AREA_FIXED && t.period === period());
  const pending = items.filter((t) => t.status !== "done");
  if (!pending.length) box.append(empty(items.length ? "Ya pagaste todos los fijos de este mes." : "Sin pagos fijos este mes."));
  pending.forEach((t) => {
    const row = el("div", "row");
    const pay = button("", "status", () => act(post("/api/life/tasks/complete", { id: t.id, done: true }), reload));
    pay.setAttribute("aria-label", `Marcar ${t.title} como pagado`);
    const del = button("✕", "btn btn--small btn--quiet", () => {
      if (window.confirm(`¿Quitar «${t.title}»?`)) act(post("/api/life/tasks/delete", { id: t.id }), reload);
    });
    del.setAttribute("aria-label", `Quitar ${t.title}`);
    row.append(pay, el("span", "row-main", t.title), el("span", "muted", money(t.amount)),
      t.due_date ? el("span", "chip", formatDate(t.due_date, { day: "numeric", month: "short" })) : el("span"), del);
    box.append(row);
  });
  const form = el("div", "inline-form");
  const title = input("text", { placeholder: "Agregar un pago fijo" });
  const amount = input("number", { placeholder: "Monto" });
  form.append(title, amount, button("Agregar", "btn", () => {
    if (!title.value.trim()) return title.focus();
    act(post("/api/life/tasks", { title: title.value.trim(), area: AREA_FIXED, amount: Number(amount.value) || 0, period: period() }), reload);
  }));
  box.append(form);
  const left = pending.reduce((n, t) => n + (t.amount || 0), 0);
  const total = el("p", "row");
  total.append(el("span", "row-main muted", `${pending.length} de ${items.length} pendientes`), el("strong", "", money(left)));
  box.append(total);
  return box;
}

function renderShopping(life, reload) {
  const box = card("Lista de compras", null, "instrument--side");
  const items = (life.tasks || []).filter((t) => t.area === AREA_SHOPPING).sort((a, b) => (a.status === "done") - (b.status === "done"));
  if (!items.length) box.append(empty("Sin compras todavía."));
  const cats = [...new Set([...SHOPPING_CATEGORIES, ...items.map((t) => t.category).filter(Boolean)])];
  cats.forEach((cat) => {
    const list = items.filter((t) => (t.category || SHOPPING_CATEGORIES[0]) === cat);
    if (!list.length) return;
    box.append(el("p", "label", cat));
    list.forEach((t) => box.append(checkRow(t, reload, { amount: true })));
  });
  const form = el("div", "inline-form");
  const title = input("text", { placeholder: "Agregar una compra" });
  const cat = select(cats.map((c) => [c, c]), cats[0]);
  form.append(title, cat, button("Agregar", "btn", () => {
    if (!title.value.trim()) return title.focus();
    act(post("/api/life/tasks", { title: title.value.trim(), area: AREA_SHOPPING, category: cat.value }), reload);
  }));
  box.append(form);
  return box;
}

function renderGoals(goals, reload, currency) {
  const box = card(`Metas ${todayIso().slice(0, 4)}`, "Todo editable");
  if (goals.error) return box.append(errorLine("Metas no disponibles", goals.error)), box;
  const list = goals.goals || [];
  const table = el("table", "goal-table");
  const head = el("tr");
  ["Meta", "Lista", "Prioridad", "Presupuesto", "Fecha", ""].forEach((h) => head.append(el("th", "", h)));
  const thead = el("thead");
  thead.append(head);
  const tbody = el("tbody");
  if (!list.length) { const tr = el("tr"); const td = el("td", "empty", "No hay metas todavía."); td.colSpan = 6; tr.append(td); tbody.append(tr); }
  list.forEach((g) => {
    const tr = el("tr");
    const done = el("input", "check");
    done.type = "checkbox";
    done.checked = Boolean(g.done);
    done.setAttribute("aria-label", `Meta lograda: ${g.title}`);
    done.addEventListener("change", () => act(post("/api/life/goals/complete", { id: g.id, done: done.checked }), reload));
    const prio = select(PRIORITIES, g.priority || "medium");
    prio.setAttribute("aria-label", "Prioridad");
    prio.addEventListener("change", () => act(post("/api/life/goals", { id: g.id, priority: prio.value }), reload));
    const budget = input("number", { value: g.budget ?? "", placeholder: "—" });
    budget.setAttribute("aria-label", `Presupuesto (${currency})`);
    budget.addEventListener("change", () => act(post("/api/life/goals", { id: g.id, budget: budget.value ? Number(budget.value) : null }), reload));
    const due = input("date", { value: g.due_date || "" });
    due.setAttribute("aria-label", "Fecha");
    due.addEventListener("change", () => act(post("/api/life/goals", { id: g.id, due_date: due.value || null }), reload));
    const del = button("✕", "btn btn--small btn--quiet", () => {
      if (window.confirm(`¿Borrar «${g.title}»?`)) act(post("/api/life/goals/delete", { id: g.id }), reload);
    });
    del.setAttribute("aria-label", `Borrar ${g.title}`);
    [el("span", "", g.title), done, prio, budget, due, del].forEach((node) => { const td = el("td"); td.append(node); tr.append(td); });
    tbody.append(tr);
  });
  table.append(thead, tbody);
  const scroller = el("div", "table-scroll");
  scroller.append(table);
  box.append(scroller);
  inlineAdd(box, { label: "+ Agregar meta", create: (title) => post("/api/life/goals", { title, priority: "medium" }), onCreated: reload });
  const total = list.reduce((n, g) => n + (g.budget || 0), 0);
  if (total) box.append(el("p", "muted", `Presupuesto total: ${money(total, currency)}`));
  return box;
}

export async function render(root, ctx) {
  disposeChart();
  const reload = () => render(root, ctx);
  const currency = ctx.cfg.vida.currency;
  const [tasks, life, week, income, history, goals] = await Promise.all([
    safe(api(`/api/tasks?ecosystem=${VIDA}`)), safe(api("/api/life/tasks")), safe(api(`/api/life/habits?week=${todayIso()}`)),
    safe(api("/api/life/income")), safe(api("/api/life/income-history")), safe(api("/api/life/goals")),
  ]);
  const label = tab === "tareas" ? "Tareas y hábitos" : "Finanzas";
  const head = masthead(["Vida Personal", label], "Vida Personal", "Tu plata, tus tareas y tus hábitos");
  const tabs = pills([["finanzas", "Finanzas"], ["tareas", "Tareas y hábitos"]], tab, (k) => { tab = k; reload(); });
  const grid = el("div", "grid grid--main-side");
  const main = el("div", "stack");
  const side = el("div", "stack");
  if (tab === "tareas") {
    main.append(renderTasks(tasks, reload), renderHabits(week, reload));
    side.append(renderConsistency(week.consistency), renderMilestones(goals), renderMonthGoals(tasks, reload));
  } else {
    main.append(renderIncome(income, history, reload), renderGoals(goals, reload, currency));
    side.append(renderFixed(life, reload), renderShopping(life, reload));
  }
  grid.append(main, side);
  root.replaceChildren(head, tabs, grid);
}
