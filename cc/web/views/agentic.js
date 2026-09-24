// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Agentic OS (module `agentic`): map of agents, skills, knowledge and wiki from /api/v2/system,
// the task pulse and the pending work. Dates follow the configured timezone.
import { api, button, card, el, empty, errorLine, formatDateTime, input, masthead, pills, safe, toast } from "../lib.js";

const KINDS = [["agents", "Agentes"], ["skills", "Skills"], ["knowledge", "Conocimiento"], ["wiki", "Wiki"]];
const STATUS = { backlog: "Pendiente", open: "Abierta", in_progress: "En curso", done: "Hecha" };
const STALE_DAYS = 14;
const state = { tab: "mapa", kind: "agents", query: "", open: null, source: null };

function nodeDetail(system, node, reload) {
  const box = card(node.label, node.kind);
  if (node.description) box.append(el("p", "muted", node.description));
  box.append(el("p", "hint", node.path), el("p", "hint", `Actualizado: ${formatDateTime(node.updated_at)}`));
  const byId = Object.fromEntries(["agents", "skills", "knowledge", "wiki"].flatMap((k) => system[k].map((n) => [n.id, n])));
  const links = system.relationships.filter((r) => r.source === node.id || r.target === node.id);
  box.append(el("p", "label", `Conexiones (${links.length})`));
  if (!links.length) box.append(empty("Sin conexiones."));
  links.forEach((r) => {
    const other = byId[r.source === node.id ? r.target : r.source];
    if (!other) return;
    box.append(button(`${other.kind}: ${other.label}`, "btn btn--small btn--quiet", () => { state.open = other.id; state.source = null; reload(); }));
  });
  box.append(button("Ver el archivo", "btn", async () => {
    try { state.source = (await api(`/api/v2/source?id=${encodeURIComponent(node.id)}`)).content; reload(); } catch (e) { toast(e.message, "error"); }
  }));
  if (state.source !== null) box.append(el("pre", "source", state.source));
  return box;
}

function map(system, reload) {
  const wrap = el("div", "stack");
  const stats = el("div", "stats");
  KINDS.forEach(([k, l]) => {
    const s = button("", `stat stat--button${state.kind === k ? " is-on" : ""}`, () => { state.kind = k; reload(); });
    s.append(el("span", "label", l), el("strong", "stat-value", String(system[k].length)));
    stats.append(s);
  });
  wrap.append(stats);
  const grid = el("div", "grid grid--sidebar");
  const list = card(KINDS.find(([k]) => k === state.kind)[1]);
  const search = input("search", { value: state.query, placeholder: "Buscar" });
  search.addEventListener("input", () => {
    state.query = search.value;
    list.querySelectorAll(".item-card").forEach((b) => { b.hidden = !b.textContent.toLowerCase().includes(state.query.toLowerCase()); });
  });
  list.append(search);
  const nodes = system[state.kind];
  if (!nodes.length) list.append(empty("Nada instalado de este tipo."));
  nodes.forEach((n) => {
    const b = el("button", `item-card${n.id === state.open ? " is-on" : ""}`);
    b.type = "button";
    b.append(el("strong", "", n.label), el("span", "muted", n.description || n.path));
    b.hidden = Boolean(state.query) && !b.textContent.toLowerCase().includes(state.query.toLowerCase());
    b.addEventListener("click", () => { state.open = n.id; state.source = null; reload(); });
    list.append(b);
  });
  const all = KINDS.flatMap(([k]) => system[k]);
  const current = all.find((n) => n.id === state.open);
  grid.append(list, current ? nodeDetail(system, current, reload) : card(null, "Elegí algo para ver sus conexiones"));
  wrap.append(grid);
  const d = system.diagnostics || {};
  const problems = [...(d.dangling_declared_skills || []).map((x) => `${x.agent} declara la skill «${x.skill}», que no está instalada`),
    ...(d.dangling_knowledge_paths || []).map((x) => `${x.agent} apunta a «${x.path}», que no existe`),
    ...(d.task_links?.danglers || []).map((x) => `La tarea ${x.task_code} apunta a ${x.node_id}, que no existe`)];
  const diag = card("Revisión", problems.length ? `${problems.length} aviso(s)` : "Todo conectado");
  if (!problems.length) diag.append(empty("No hay conexiones rotas."));
  const ul = el("ul", "plain-list");
  problems.forEach((p) => ul.append(el("li", "", p)));
  diag.append(ul);
  wrap.append(diag);
  return wrap;
}

function pulse(tasks, ctx) {
  const grid = el("div", "grid grid--2");
  const names = Object.fromEntries([...ctx.brands.map((b) => [b.id, b.name]), ["vida", "Vida Personal"]]);
  const byEco = {};
  tasks.forEach((t) => { (byEco[t.ecosystem] ||= { backlog: 0, open: 0, in_progress: 0, done: 0 })[t.status] += 1; });
  const box = card("Pulso de tareas", "Por marca");
  if (!Object.keys(byEco).length) box.append(empty("Sin tareas todavía."));
  Object.entries(byEco).forEach(([eco, counts]) => {
    const row = el("div", "row");
    row.append(el("strong", "row-main", names[eco] || eco));
    Object.entries(counts).forEach(([s, n]) => row.append(el("span", "chip", `${STATUS[s]}: ${n}`)));
    box.append(row);
  });
  const recent = card("Movimiento reciente", "Últimos cambios");
  const last = [...tasks].sort((a, b) => (b.updated_at || "").localeCompare(a.updated_at || "")).slice(0, 12);
  if (!last.length) recent.append(empty("Nada todavía."));
  last.forEach((t) => {
    const row = el("div", "row");
    const main = el("div", "row-main");
    main.append(el("strong", "", `${t.code} · ${t.title}`), el("span", "muted", `${STATUS[t.status]} · ${formatDateTime(t.updated_at)}`));
    row.append(main);
    recent.append(row);
  });
  grid.append(box, recent);
  return grid;
}

function backlog(tasks) {
  const cutoff = Date.now() - STALE_DAYS * 86400000;
  const stale = tasks.filter((t) => t.status !== "done" && Date.parse(t.updated_at) < cutoff);
  const open = tasks.filter((t) => t.status === "backlog");
  const grid = el("div", "grid grid--2");
  const a = card("Estancadas", `Sin cambios hace más de ${STALE_DAYS} días`);
  if (!stale.length) a.append(empty("Nada estancado."));
  stale.forEach((t) => a.append(el("p", "row", `${t.code} · ${t.title}`)));
  const b = card("Pendientes", `${open.length} sin empezar`);
  if (!open.length) b.append(empty("No hay pendientes."));
  open.slice(0, 30).forEach((t) => b.append(el("p", "row", `${t.code} · ${t.title}`)));
  grid.append(a, b);
  return grid;
}

export async function render(root, ctx) {
  const reload = () => render(root, ctx);
  const [system, tasks] = await Promise.all([safe(api("/api/v2/system")), safe(api("/api/tasks"))]);
  const head = masthead(["Agentic OS"], "Agentic OS", "Tus agentes, skills y conocimiento, y cómo va el trabajo");
  const tabs = pills([["mapa", "Mapa"], ["pulso", "Pulso"], ["pendientes", "Pendientes"]], state.tab, (k) => { state.tab = k; reload(); });
  let body;
  if (state.tab === "mapa") body = system.error ? errorLine("Mapa no disponible", system.error) : map(system, reload);
  else if (tasks.error) body = errorLine("Tareas no disponibles", tasks.error);
  else body = state.tab === "pulso" ? pulse(tasks.tasks || [], ctx) : backlog(tasks.tasks || []);
  root.replaceChildren(head, tabs, body);
}
