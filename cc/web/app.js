// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Shell: the menu and the views come from GET /api/config (active brands + toggles).
// Nothing about any brand is written here. Router by hash: #vista or #marca/<id>.
import { api, button, el, setLocale, toast } from "./lib.js";

const VIEWS = {
  inicio: { label: "Inicio", load: () => import("./views/inicio.js") },
  ideas: { label: "Ideas y Content Lab", load: () => import("./views/ideas.js") },
  guion: { label: "Guion y grabación", load: () => import("./views/guion.js") },
  tablero: { label: "Tablero", load: () => import("./views/tablero.js") },
  marca: { label: "Marca", load: () => import("./views/marca.js") },
  vida: { label: "Vida Personal", load: () => import("./views/vida.js"), toggle: "vida" },
  produccion: { label: "Producción", load: () => import("./views/produccion.js"), toggle: "produccion_avanzada" },
  biblioteca: { label: "Biblioteca", load: () => import("./views/biblioteca.js"), toggle: "biblioteca" },
  agentic: { label: "Agentic OS", load: () => import("./views/agentic.js"), toggle: "agentic" },
  subtitulos: { label: "Estudio de subtítulos", load: () => import("./views/subtitulos.js"), toggle: "subtitulos" },
};
// Module switches shown in the rail. Flipping one writes cc.config.json and redraws the menu (no reload).
const MODULES = [["vida", "Vida Personal"], ["marcas_extra", "Mis otras marcas"], ["produccion_avanzada", "Producción avanzada"],
  ["biblioteca", "Biblioteca"], ["subtitulos", "Estudio de subtítulos"], ["metricas", "Métricas conectadas"],
  ["agentic", "Agentic OS"]];
const DEFAULT_ACCENT = "#7C5CFF";
const HEX = /^#[0-9a-f]{3,8}$/i;
const BRAND_KEY = "cc-creator-brand";

const nav = document.getElementById("nav");
const view = document.getElementById("view");
const warnings = document.getElementById("warnings");
const modules = document.getElementById("modules");

const ctx = {
  cfg: null,
  brands: [],               // active brands (toggles applied by the server)
  logos: [],                // brand ids with an uploaded logo
  logoVersion: 0,
  get creatorBrand() {
    let saved = null;
    try { saved = localStorage.getItem(BRAND_KEY); } catch { /* private mode */ }
    return this.brands.find((b) => b.id === saved)
      || this.brands.find((b) => b.kind === "personal-brand") || this.brands[0] || null;
  },
  setCreatorBrand(id) {
    try { localStorage.setItem(BRAND_KEY, id); } catch { /* private mode */ }
    route();
  },
  enabled: (module) => Boolean(ctx.cfg?.toggles?.[module]),
  go: (hash) => { window.location.hash = hash; },
  refresh: () => route(),
  reloadConfig: async () => { applyConfig(await api("/api/config")); renderModules(); route(); },
};

export function setAccent(color) {
  document.documentElement.style.setProperty("--accent", HEX.test(color || "") ? color : DEFAULT_ACCENT);
}

function menu() {
  const items = [["inicio", VIEWS.inicio.label], ["ideas", VIEWS.ideas.label], ["guion", VIEWS.guion.label],
    ["tablero", VIEWS.tablero.label]];
  ctx.brands.forEach((b) => items.push([`marca/${b.id}`, b.name]));
  ["vida", "produccion", "biblioteca", "subtitulos", "agentic"].forEach((key) => {
    if (ctx.enabled(VIEWS[key].toggle)) items.push([key, VIEWS[key].label]);
  });
  return items;
}

function renderNav(current) {
  nav.replaceChildren(...menu().map(([hash, label]) => {
    const b = button(label, "nav-item", () => ctx.go(hash));
    if (hash === current) b.setAttribute("aria-current", "page");
    return b;
  }));
}

function renderWarnings() {
  const list = ctx.cfg._warnings || [];
  if (!list.length) return warnings.replaceChildren();
  const box = el("details", "warning-box");
  box.append(el("summary", "", `Tu configuración tiene ${list.length} dato(s) que se ignoraron. Todo lo demás funciona.`));
  const ul = el("ul");
  list.slice(0, 50).forEach((w) => ul.append(el("li", "", w)));
  box.append(ul);
  warnings.replaceChildren(box);
}

function renderModules() {
  const box = el("details", "modules");
  box.append(el("summary", "", "Módulos"));
  const panel = el("div", "modules-panel");
  MODULES.forEach(([key, label]) => {
    if (!(key in (ctx.cfg.toggles || {}))) return;
    const row = el("label");
    const check = el("input");
    check.type = "checkbox";
    check.checked = ctx.enabled(key);
    check.addEventListener("change", async () => {
      check.disabled = true;
      try {
        applyConfig(await api("/api/config/toggle", { module: key, on: check.checked }));
        renderWarnings();
        route();
        toast(check.checked ? `${label}: prendido` : `${label}: apagado`);
      } catch (error) {
        check.checked = !check.checked;
        toast(error.message, "error");
      } finally { check.disabled = false; }
    });
    row.append(check, el("span", "", label));
    panel.append(row);
  });
  box.append(panel);
  modules.replaceChildren(box);
}

function applyConfig({ config, active_brands: active, logos }) {
  ctx.cfg = config;
  ctx.brands = config.brands.filter((b) => active.includes(b.id));
  ctx.logos = logos || [];
}

let token = 0;
async function route() {
  const mine = ++token;
  const hash = window.location.hash.slice(1) || "inicio";
  const [name, param] = hash.split("/");
  const spec = VIEWS[name];
  const allowed = spec && (!spec.toggle || ctx.enabled(spec.toggle))
    && (name !== "marca" || ctx.brands.some((b) => b.id === param));
  if (!allowed) { if (hash !== "inicio") ctx.go("inicio"); else view.replaceChildren(el("p", "empty", "Vista no disponible.")); return; }
  renderNav(hash);
  const brand = name === "marca" ? ctx.brands.find((b) => b.id === param) : ctx.creatorBrand;
  setAccent(name === "vida" || name === "agentic" ? null : brand?.accent);
  view.replaceChildren(el("p", "loading", "Cargando…"));
  try {
    const module = await spec.load();
    if (mine !== token) return;
    const root = el("div", `view view--${name}`);
    view.replaceChildren(root);
    await module.render(root, ctx, param);
  } catch (error) {
    if (mine === token) view.replaceChildren(el("p", "empty is-error", `No se pudo abrir esta vista: ${error.message}`));
  }
}

async function boot() {
  try {
    applyConfig(await api("/api/config"));
  } catch (error) {
    view.replaceChildren(el("p", "empty is-error", error.status === 401
      ? "La sesión venció. Abrí el Command Center de nuevo desde su enlace."
      : `No se pudo leer la configuración: ${error.message}`));
    return;
  }
  setLocale(ctx.cfg);
  document.documentElement.lang = ctx.cfg.locale?.language || "es";
  renderWarnings();
  renderModules();
  window.addEventListener("hashchange", route);
  route();
}

boot();
