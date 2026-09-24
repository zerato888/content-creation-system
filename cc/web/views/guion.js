// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Guion y grabación: simple composer (3 structures + hooks bank), scripts with 3 hook
// versions, teleprompter and «Ya grabé» (moves the script and adds to the streak).
import {
  api, brandPicker, button, card, el, empty, errorLine, formatDate, input, masthead, noBrand, safe, select, toast,
} from "../lib.js";

const STRUCTURES = [
  { key: "problema-solucion", name: "Problema → solución",
    beats: ["Hook: nombrá el problema tal como lo vive quien te mira", "Por qué pasa (una sola causa clara)",
      "Qué hacer, en pasos concretos", "Cierre: una frase para recordar y qué hacer ahora"] },
  { key: "historia", name: "Historia personal",
    beats: ["Hook: el momento exacto en que todo cambió", "Cómo era antes", "Qué pasó y qué aprendiste",
      "Qué cambió después", "Cierre: la lección para quien te mira"] },
  { key: "lista", name: "Lista de consejos",
    beats: ["Hook: el número y el resultado («3 cosas que…»)", "Consejo 1 con un ejemplo", "Consejo 2 con un ejemplo",
      "Consejo 3 con un ejemplo", "Cierre: cuál probar primero"] },
];
const ESTADOS = { en_proceso: "En proceso", aprobado: "Aprobado", grabando: "Grabando", grabado: "Grabado", editado: "Editado" };
const state = { file: null, structure: STRUCTURES[0].key, bankCategory: null };
// Unsaved edits per script, kept across re-renders (favorite, hook versions...) until saved.
const drafts = {};
// One request key per script's «Ya grabé»: a retry after a lost answer is the same request.
const recordKeys = {};
const newKey = () => (globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`);

// The kit's hooks bank (.kit/presets/hooks/hooks-bank.json), served by the backend. Loaded once per page.
let bankPromise = null;
function hooksBank() {
  bankPromise ||= api("/api/hooks-bank").then((r) => r.bank, () => null);
  return bankPromise;
}

function bankPanel(bank, hookField) {
  const box = card("Banco de hooks", "Elegí un tipo y adaptalo");
  if (!bank?.categories?.length) return box.append(empty("El banco de hooks no está instalado en este kit.")), box;
  const cats = bank.categories;
  const current = cats.find((c) => c.id === state.bankCategory) || cats[0];
  const pick = select(cats.map((c) => [c.id, c.name]), current.id);
  pick.setAttribute("aria-label", "Tipo de hook");
  const list = el("div", "stack stack--tight");
  const fill = (cat) => {
    list.replaceChildren();
    [...(cat.templates || []), ...(cat.examples || [])].forEach((text) => {
      const row = el("div", "row");
      row.append(el("span", "row-main", text), button("Usar", "btn btn--small", () => { hookField.value = text; hookField.focus(); }));
      list.append(row);
    });
  };
  pick.addEventListener("change", () => { state.bankCategory = pick.value; fill(cats.find((c) => c.id === pick.value)); });
  fill(current);
  if (bank.principles?.say_the_topic) box.append(el("p", "hint", bank.principles.say_the_topic));
  box.append(pick, list);
  return box;
}

function composer(brand, bank, reload) {
  const wrap = el("div", "grid grid--2");
  const box = card("Nuevo guion", "Compositor");
  const title = input("text", { placeholder: "Título (para vos)" });
  const hook = input("textarea", { placeholder: "Hook: la primera frase. Decí de qué trata." });
  hook.rows = 2;
  const body = input("textarea");
  body.rows = 12;
  const structure = () => STRUCTURES.find((s) => s.key === state.structure);
  const applyStructure = () => { body.placeholder = structure().beats.map((b, i) => `${i + 1}. ${b}`).join("\n\n"); };
  const bar = el("div", "pills");
  STRUCTURES.forEach((s) => {
    const b = button(s.name, `pill${s.key === state.structure ? " on" : ""}`, () => {
      state.structure = s.key;
      bar.querySelectorAll(".pill").forEach((p) => p.classList.toggle("on", p === b));
      applyStructure();
    });
    bar.append(b);
  });
  applyStructure();
  const save = button("Guardar guion", "btn btn--primary", async () => {
    if (!title.value.trim()) return toast("Poné un título", "error");
    save.disabled = true;
    try {
      const { file } = await api("/api/guion", { titulo: title.value, hook: hook.value, cuerpo: body.value,
        estructura: structure().name, brand: brand.id });
      state.file = file;
      toast("Guion guardado");
      reload();
    } catch (e) { save.disabled = false; toast(e.message, "error"); }
  });
  box.append(title, el("p", "label", "Estructura"), bar, el("p", "label", "Hook"), hook, el("p", "label", "Guion"), body, save);
  wrap.append(box, bankPanel(bank, hook));
  return wrap;
}

function hookVersions(g, reload) {
  const box = card("3 versiones del hook", "Grabá las tres y quedate con la mejor");
  const opts = g.hooks?.opciones || [];
  const kept = drafts[`hooks:${g.file}`] || {};
  const fields = [0, 1, 2].map((i) => {
    const f = input("text", { value: i in kept ? kept[i] : (opts[i] ?? (i === 0 ? g.hook : "")), placeholder: `Versión ${i + 1}` });
    f.setAttribute("aria-label", `Versión ${i + 1} del hook`);
    f.addEventListener("input", () => { (drafts[`hooks:${g.file}`] ||= {})[i] = f.value; });
    return f;
  });
  const chosen = Number.isInteger(g.hooks?.elegida) ? g.hooks.elegida : null;
  const group = `hook-${g.file}`;
  fields.forEach((f, i) => {
    const row = el("label", "row");
    const radio = el("input");
    radio.type = "radio";
    radio.name = group;
    radio.value = String(i);
    radio.checked = chosen === i;
    row.append(radio, f);
    box.append(row);
  });
  box.append(button("Guardar versiones", "btn", async () => {
    const opciones = fields.map((f) => f.value.trim()).filter(Boolean);
    const pickedRadio = box.querySelector(`input[name="${CSS.escape(group)}"]:checked`);
    const picked = pickedRadio ? Number(pickedRadio.value) : null;
    const elegida = picked !== null && fields[picked].value.trim() ? opciones.indexOf(fields[picked].value.trim()) : null;
    try { await api("/api/guion/hooks", { file: g.file, opciones, elegida }); delete drafts[`hooks:${g.file}`]; toast("Versiones guardadas"); reload(); } catch (e) { toast(e.message, "error"); }
  }));
  return box;
}

function editor(g, brand, reload) {
  const wrap = el("div", "stack");
  const box = card(g.titulo, `${ESTADOS[g.estado] || g.estado}${g.estructura ? ` · ${g.estructura}` : ""}${g.task_code ? ` · tarjeta ${g.task_code}` : ""}`);
  const fields = {};
  const draft = drafts[g.file] || {};
  [["hook", "Hook", 2], ["cuerpo", "Guion", 12], ["talking_points", "Puntos clave (opcional)", 4], ["caption", "Texto del post", 3], ["notas", "Notas", 2]]
    .forEach(([key, label, rows]) => {
      const f = input("textarea", { value: key in draft ? draft[key] : (g[key] || "") });
      f.rows = rows;
      f.setAttribute("aria-label", label);
      f.addEventListener("input", () => { (drafts[g.file] ||= {})[key] = f.value; });
      fields[key] = f;
      box.append(el("p", "label", label), f);
    });
  // Saves what is on screen (only if something changed). Every action that uses the script calls it first.
  const saveDraft = async () => {
    if (!drafts[g.file] || !Object.keys(drafts[g.file]).length) return;
    await api("/api/guion", { file: g.file, ...Object.fromEntries(Object.entries(fields).map(([k, f]) => [k, f.value])) });
    delete drafts[g.file];
  };
  const tele = button("Abrir teleprompter", "btn", async () => {
    const win = window.open("about:blank", "_blank"); // opened now, while the click still counts
    try {
      await saveDraft();
      const url = `teleprompter.html?${new URLSearchParams({ guion: g.file })}`;
      if (win) { win.opener = null; win.location.href = url; } else window.open(url, "_blank", "noopener");
    } catch (e) { win?.close(); toast(`No pude guardar antes de abrir: ${e.message}`, "error"); }
  });
  const actions = el("div", "actions");
  actions.append(
    button("Guardar", "btn btn--primary", async () => {
      drafts[g.file] ||= { _: true };
      try { await saveDraft(); toast("Guardado"); reload(); } catch (e) { toast(e.message, "error"); }
    }),
    tele,
    button(g.favorito ? "★ Favorito" : "☆ Favorito", "btn btn--quiet", async () => {
      try { await api("/api/guion/favorite", { file: g.file }); reload(); } catch (e) { toast(e.message, "error"); }
    }),
    button("Borrar", "btn btn--danger", async () => {
      if (!window.confirm(`¿Borrar «${g.titulo}»?`)) return;
      try { await api("/api/guion/delete", { file: g.file }); delete drafts[g.file]; state.file = null; reload(); } catch (e) { toast(e.message, "error"); }
    }),
  );
  box.append(actions);

  const rec = card("Ya grabé", "Paso final");
  if (["grabado", "editado"].includes(g.estado)) rec.append(el("p", "muted", "Este guion ya está grabado. Anotá sus vistas en Inicio a las 48 horas."));
  else {
    rec.append(el("p", "muted", "Cuando termines de grabar, tocá el botón: suma a tu racha y mueve el guion a «Grabado»."));
    const done = button("Ya grabé", "btn btn--primary btn--big", async () => {
      const chosen = Number.isInteger(g.hooks?.elegida) ? g.hooks.opciones[g.hooks.elegida] : null;
      done.disabled = true; // a double click is one recording (and the server dedupes by script and key)
      try {
        await saveDraft(); // what you recorded is what is on screen, not the last saved version
        recordKeys[g.file] ||= newKey();
        // the board card is linked by id when the script was created from it (task_code); the server uses it
        const r = await api("/api/creator/recorded", { file: g.file, brand: brand.id, hook: chosen || fields.hook.value || null,
          request_key: recordKeys[g.file] });
        delete recordKeys[g.file];
        toast(r.recording?.duplicate ? "Ya estaba anotado: no lo sumé dos veces." :
          r.remaining ? `¡Bien! Te faltan ${r.remaining} esta semana.` : "¡Semana cumplida!");
        reload();
      } catch (e) { done.disabled = false; toast(e.message, "error"); }
    });
    rec.append(done);
  }
  wrap.append(box, hookVersions(g, reload), rec);
  return wrap;
}

function scriptList(guiones, brand) {
  const box = card("Tus guiones", `${guiones.length} en total`);
  const nuevo = button("+ Nuevo guion", "btn btn--primary", () => { state.file = null; box.dispatchEvent(new CustomEvent("reopen", { bubbles: true })); });
  box.append(nuevo);
  if (!guiones.length) box.append(empty("Todavía no hay guiones."));
  guiones.forEach((g) => {
    const b = el("button", `item-card${g.file === state.file ? " is-on" : ""}`);
    b.type = "button";
    b.append(el("span", "label", `${ESTADOS[g.estado] || g.estado}${g.favorito ? " · ★" : ""}`), el("strong", "", g.titulo),
      el("span", "muted", formatDate(new Date(g.mtime * 1000).toISOString().slice(0, 10))));
    b.addEventListener("click", () => { state.file = g.file; b.dispatchEvent(new CustomEvent("reopen", { bubbles: true })); });
    box.append(b);
  });
  return box;
}

export async function render(root, ctx) {
  const brand = ctx.creatorBrand;
  const head = masthead(["Guion y grabación", brand?.name || "Sin marca"], "Guion y grabación", "Escribí, ensayá con el teleprompter y grabá");
  if (!brand) return root.replaceChildren(head, noBrand());
  head.append(brandPicker(ctx));
  const reload = () => render(root, ctx);
  const [data, bank] = await Promise.all([safe(api("/api/guiones")), hooksBank()]);
  if (data.error) return root.replaceChildren(head, errorLine("Guiones no disponibles", data.error));
  // scripts of this brand, plus old scripts with no brand (so nothing is ever hidden)
  const guiones = (data.guiones || []).filter((g) => !g.brand || g.brand === brand.id);
  const current = guiones.find((g) => g.file === state.file);
  const layout = el("div", "grid grid--sidebar");
  const side = scriptList(guiones, brand);
  side.addEventListener("reopen", reload);
  layout.append(side, current ? editor(current, brand, reload) : composer(brand, bank, reload));
  root.replaceChildren(head, layout);
}
