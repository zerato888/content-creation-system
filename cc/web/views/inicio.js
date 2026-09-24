// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Inicio de creador: weekly streak, the next step, videos recorded (views at 48h) and the hook winner.
import { api, button, card, el, empty, errorLine, formatDate, input, masthead, safe, toast } from "../lib.js";

function streakCard(s) {
  const box = card(null, "Racha semanal", "instrument--focus streak");
  if (s.error) return box.append(errorLine("Racha no disponible", s.error)), box;
  const big = el("p", "streak-number");
  big.append(el("strong", "", String(s.streak_weeks)), el("span", "", s.streak_weeks === 1 ? " semana" : " semanas"));
  const dots = el("div", "streak-dots");
  for (let i = 0; i < s.goal; i += 1) dots.append(el("span", `dot${i < s.this_week ? " is-on" : ""}`));
  box.append(big, dots, el("p", "muted", s.remaining
    ? `Esta semana: ${s.this_week} de ${s.goal} videos. Te faltan ${s.remaining}.`
    : `Semana cumplida: ${s.this_week} de ${s.goal} videos.`));
  if (s.grace_days) box.append(el("p", "hint", `Si un video se te pasa al lunes, cuenta para la semana anterior (${s.grace_days} día de gracia).`));
  return box;
}

function nextStep(guiones, items, tasks, ctx) {
  const box = card("Tu próximo paso", "Qué hacer ahora");
  const ready = (guiones.guiones || []).find((g) => ["en_proceso", "aprobado", "grabando"].includes(g.estado));
  let text, cta, hash;
  if (ready) [text, cta, hash] = [`Grabá «${ready.titulo}».`, "Ir al guion", "guion"];
  else if ((tasks.tasks || []).some((t) => t.stage === "idea" && t.status !== "done")
    || (items.items || []).some((i) => !i.archivada)) [text, cta, hash] = ["Elegí una de tus ideas y escribí el guion.", "Ver ideas", "ideas"];
  else [text, cta, hash] = ["Anotá 10 ideas o pegá un video que te guste.", "Empezar con ideas", "ideas"];
  box.append(el("p", "lead", text), button(cta, "btn btn--primary", () => ctx.go(hash)));
  if (hash !== "guion") box.append(button("Escribir un guion", "btn", () => ctx.go("guion")));
  return box;
}

function recommendations(recs) {
  const box = card("Avisos", "El sistema te sugiere");
  if (recs.error) return box.append(errorLine("Avisos no disponibles", recs.error)), box;
  if (!recs.items?.length) return box.append(empty("Nada pendiente. Todo en orden.")), box;
  const ul = el("ul", "plain-list");
  recs.items.forEach((r) => ul.append(el("li", "", r.text)));
  box.append(ul);
  return box;
}

function recordings(data, reload) {
  const box = card("Tus videos", "Vistas a las 48 horas");
  if (data.error) return box.append(errorLine("Videos no disponibles", data.error)), box;
  const rows = (data.recordings || []).slice(0, 12);
  if (!rows.length) return box.append(empty("Todavía no grabaste nada. Cuando toques «Ya grabé», aparece acá.")), box;
  box.append(el("p", "hint", "Dos días después de publicar, anotá cuántas vistas tuvo."));
  rows.forEach((r) => {
    const row = el("div", "row");
    const views = input("number", { value: r.views_48h ?? "", placeholder: "Vistas", className: "field field--num" });
    views.min = "0";
    views.setAttribute("aria-label", `Vistas a las 48 horas de ${r.title}`);
    views.addEventListener("change", async () => {
      const value = Number.parseInt(views.value, 10);
      if (!Number.isFinite(value) || value < 0) return;
      try { await api("/api/creator/views", { id: r.id, views_48h: value }); toast("Vistas guardadas"); reload(); } catch (e) { toast(e.message, "error"); }
    });
    const copy = el("div", "row-main");
    copy.append(el("strong", "", r.title), el("span", "muted", `${formatDate(r.date)}${r.hook ? ` · ${r.hook}` : ""}`));
    row.append(copy, views);
    box.append(row);
  });
  return box;
}

function hookWinner(data) {
  const box = card("Hook ganador de la semana", "Se decide el domingo");
  if (data.error) return box.append(errorLine("No disponible", data.error)), box;
  if (!data.winner) return box.append(empty("Anotá las vistas de tus videos para saber qué hook ganó.")), box;
  box.append(el("p", "lead", data.winner.hook || data.winner.title),
    el("p", "muted", `${data.winner.views_48h} vistas a las 48 h · ${data.measured} video(s) medidos desde el ${formatDate(data.week_start)}`));
  return box;
}

export async function render(root, ctx) {
  const brand = ctx.creatorBrand;
  const [summary, guiones, items, tasks, recs, recs48, winner] = await Promise.all([
    safe(api("/api/creator/summary")), safe(api("/api/guiones")),
    brand ? safe(api(`/api/lab/items?brand=${encodeURIComponent(brand.id)}`)) : Promise.resolve({ items: [] }),
    brand ? safe(api(`/api/tasks?ecosystem=${encodeURIComponent(brand.id)}`)) : Promise.resolve({ tasks: [] }),
    safe(api("/api/recommendations")), safe(api("/api/creator/recordings")), safe(api("/api/creator/hook-winner")),
  ]);
  const reload = () => render(root, ctx);
  const grid = el("div", "grid grid--2");
  grid.append(streakCard(summary), nextStep(guiones, items, tasks, ctx), recordings(recs48, reload), hookWinner(winner),
    recommendations(recs));
  const head = masthead(["Inicio"], brand ? brand.name : "Tu espacio de creador", "Tu semana de un vistazo");
  if (!brand) grid.prepend(el("p", "empty", "Todavía no configuraste ninguna marca. Pedile a tu agente: «agregá mi marca personal»."));
  root.replaceChildren(head, grid);
}
