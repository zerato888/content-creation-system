// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Vida Personal notebooks: diario (with a month calendar), recordatorios and ideas.
// Everything is empty until the person writes something; data lives in the local life.db.
import { api, button, card, el, empty, errorLine, formatDate, inlineAdd, input, locale, safe, select, todayIso, toast } from "../lib.js";

const MOODS = [["", "Sin ánimo"], ["1", "1 · mal"], ["2", "2"], ["3", "3 · normal"], ["4", "4"], ["5", "5 · muy bien"]];
let month = null;      // "YYYY-MM" shown in the diary
let picked = null;     // "YYYY-MM-DD" selected in the diary

async function act(promise, reload) {
  try { await promise; reload(); } catch (e) { toast(e.message, "error"); }
}

function shiftMonth(ym, step) {
  const [y, m] = ym.split("-").map(Number);
  const d = new Date(y, m - 1 + step, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function calendar(ym, days, reload) {
  const [y, m] = ym.split("-").map(Number);
  const first = (new Date(y, m - 1, 1).getDay() + 6) % 7;   // Monday first
  const total = new Date(y, m, 0).getDate();
  const grid = el("div", "calendar");
  for (let i = 0; i < first; i += 1) grid.append(el("span", "calendar-blank"));
  for (let d = 1; d <= total; d += 1) {
    const iso = `${ym}-${String(d).padStart(2, "0")}`;
    const b = button(String(d), `calendar-day${days.has(iso) ? " has-entry" : ""}${iso === picked ? " is-picked" : ""}`,
      () => { picked = iso; reload(); });
    b.setAttribute("aria-label", `${formatDate(iso)}${days.has(iso) ? ", con entradas" : ""}`);
    grid.append(b);
  }
  return grid;
}

export async function journal(reload) {
  const today = todayIso();
  month = month || today.slice(0, 7);
  picked = picked && picked.startsWith(month) ? picked : (today.startsWith(month) ? today : `${month}-01`);
  const data = await safe(api(`/api/life/journal?month=${month}`));
  const box = card("Diario", "Un día a la vez");
  if (data.error) return box.append(errorLine("Diario no disponible", data.error)), box;
  const entries = data.items || [];
  const nav = el("div", "calendar-nav");
  const title = new Intl.DateTimeFormat(locale().language, { month: "long", year: "numeric" })
    .format(new Date(Number(month.slice(0, 4)), Number(month.slice(5)) - 1, 1));
  const prev = button("←", "btn btn--small", () => { month = shiftMonth(month, -1); reload(); });
  const next = button("→", "btn btn--small", () => { month = shiftMonth(month, 1); reload(); });
  prev.setAttribute("aria-label", "Mes anterior");
  next.setAttribute("aria-label", "Mes siguiente");
  nav.append(prev, el("strong", "calendar-title", title), next);
  box.append(nav, calendar(month, new Set(entries.map((e) => e.date)), reload));

  box.append(el("p", "label", formatDate(picked)));
  const dayEntries = entries.filter((e) => e.date === picked);
  if (!dayEntries.length) box.append(empty("Nada escrito este día."));
  dayEntries.forEach((e) => {
    const row = el("div", "row");
    const copy = el("div", "row-main");
    copy.append(el("span", "journal-text", e.text));
    if (e.mood) copy.append(el("span", "muted", `Ánimo ${e.mood} de 5`));
    const del = button("✕", "btn btn--small btn--quiet", () => {
      if (window.confirm("¿Borrar esta entrada?")) act(api("/api/life/journal/delete", { id: e.id }), reload);
    });
    del.setAttribute("aria-label", "Borrar entrada");
    row.append(copy, del);
    box.append(row);
  });
  const text = input("textarea", { placeholder: "¿Cómo estuvo el día?" });
  text.rows = 4;
  text.setAttribute("aria-label", "Nueva entrada");
  const mood = select(MOODS, "");
  mood.setAttribute("aria-label", "Ánimo");
  const save = button("Guardar entrada", "btn btn--primary", () => {
    if (!text.value.trim()) return toast("Escribí algo primero", "error");
    act(api("/api/life/journal", { text: text.value.trim(), date: picked, mood: mood.value ? Number(mood.value) : null }), reload);
  });
  box.append(text, mood, save);
  return box;
}

export async function reminders(reload) {
  const data = await safe(api("/api/life/reminders"));
  const box = card("Recordatorios", "Lo que no querés olvidar");
  if (data.error) return box.append(errorLine("Recordatorios no disponibles", data.error)), box;
  const items = data.items || [];
  const today = todayIso();
  if (!items.length) box.append(empty("No hay recordatorios todavía."));
  items.forEach((r) => {
    const row = el("div", `row${r.done ? " is-done" : ""}`);
    const check = el("input", "check");
    check.type = "checkbox";
    check.checked = Boolean(r.done);
    check.setAttribute("aria-label", `Listo: ${r.title}`);
    check.addEventListener("change", () => act(api("/api/life/reminders/complete", { id: r.id, done: check.checked }), reload));
    const when = [r.due_date && formatDate(r.due_date, { day: "numeric", month: "short" }), r.due_time].filter(Boolean).join(" ");
    const late = !r.done && r.due_date && r.due_date < today;
    row.append(check, el("span", "row-main", r.title));
    if (when) row.append(el("span", late ? "badge" : "chip", late ? `Vencido · ${when}` : when));
    const del = button("✕", "btn btn--small btn--quiet", () => act(api("/api/life/reminders/delete", { id: r.id }), reload));
    del.setAttribute("aria-label", `Borrar ${r.title}`);
    row.append(del);
    box.append(row);
  });
  const date = input("date");
  date.setAttribute("aria-label", "Fecha del próximo recordatorio");
  const time = input("time");
  time.setAttribute("aria-label", "Hora (opcional)");
  const form = el("div", "inline-form");
  form.append(date, time);
  box.append(form);
  inlineAdd(box, { label: "+ Agregar recordatorio", create: (title) => api("/api/life/reminders",
    { title, due_date: date.value || null, due_time: time.value || null }), onCreated: reload });
  return box;
}

export async function ideas(reload) {
  const data = await safe(api("/api/life/ideas"));
  const box = card("Ideas", "Anotalas antes de que se vayan");
  if (data.error) return box.append(errorLine("Ideas no disponibles", data.error)), box;
  const items = data.items || [];
  if (!items.length) box.append(empty("Todavía no anotaste ninguna idea."));
  items.forEach((i) => {
    const row = el("div", `row${i.done ? " is-done" : ""}`);
    const check = el("input", "check");
    check.type = "checkbox";
    check.checked = Boolean(i.done);
    check.setAttribute("aria-label", `Hecha: ${i.text}`);
    check.addEventListener("change", () => act(api("/api/life/ideas/complete", { id: i.id, done: check.checked }), reload));
    const del = button("✕", "btn btn--small btn--quiet", () => act(api("/api/life/ideas/delete", { id: i.id }), reload));
    del.setAttribute("aria-label", `Borrar ${i.text}`);
    row.append(check, el("span", "row-main", i.text), del);
    box.append(row);
  });
  inlineAdd(box, { label: "+ Anotar idea", create: (text) => api("/api/life/ideas", { text }), onCreated: reload });
  return box;
}
