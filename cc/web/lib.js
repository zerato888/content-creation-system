// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Shared helpers. Security rule for the whole UI: every string that comes from the
// user or the server goes into the page through textContent / value / setAttribute,
// never through HTML parsing (no HTML-string sinks anywhere in this tree; a test enforces it).

export const el = (tag, className = "", text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
};

export function button(label, className = "btn", onClick) {
  const b = el("button", className, label);
  b.type = "button";
  if (onClick) b.addEventListener("click", onClick);
  return b;
}

export function input(type, { value = "", placeholder = "", className = "field" } = {}) {
  const i = el(type === "textarea" ? "textarea" : "input", className);
  if (type !== "textarea") i.type = type;
  i.value = value ?? "";
  if (placeholder) i.placeholder = placeholder;
  return i;
}

export function select(options, value, className = "field") {
  const s = el("select", className);
  options.forEach(([stored, label]) => s.append(new Option(label, stored, false, stored === value)));
  return s;
}

const TIMEOUT_MS = 10_000;

// `timeout` in ms: long jobs (transcribing, exporting video) pass their own.
export async function api(path, body, { timeout = TIMEOUT_MS } = {}) {
  const opts = { headers: { Accept: "application/json" }, signal: AbortSignal.timeout(timeout) };
  if (body !== undefined) {
    opts.method = "POST";
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  let response;
  try {
    response = await fetch(path, opts);
  } catch (error) {
    throw new Error(error?.name === "TimeoutError" ? "El servidor no respondió" : "No se pudo conectar");
  }
  const payload = await response.json().catch(() => ({ ok: false, error: `HTTP ${response.status}` }));
  if (!response.ok || payload.ok === false) {
    const err = new Error(payload.error || `HTTP ${response.status}`);
    err.status = response.status;
    throw err;
  }
  return payload;
}

// Never throws: returns {error} so one dead section never blanks the whole view.
export const safe = (promise) => promise.catch((error) => ({ error }));

// ------------------------------------------------------------ locale (from cc.config.json)
let LOCALE = { language: "es", timezone: "UTC", currency: "USD" };
export function setLocale(cfg) {
  LOCALE = { language: cfg.locale?.language || "es", timezone: cfg.locale?.timezone || "UTC",
    currency: cfg.vida?.currency || "USD" };
}
export const locale = () => LOCALE;

export function money(n, currency = LOCALE.currency) {
  try {
    return new Intl.NumberFormat(LOCALE.language, { style: "currency", currency, maximumFractionDigits: 0 }).format(n || 0);
  } catch {
    return `${Math.round(n || 0)} ${currency}`;
  }
}

export const compact = (n) => (Number.isFinite(Number(n))
  ? new Intl.NumberFormat(LOCALE.language, { notation: "compact", maximumFractionDigits: 1 }).format(Number(n))
  : "Sin dato");

export function formatDate(iso, opts = { day: "numeric", month: "short", year: "numeric" }) {
  if (!iso) return "Sin fecha";
  const [y, m, d] = String(iso).slice(0, 10).split("-").map(Number);
  if (!y || !m || !d) return String(iso);
  return new Intl.DateTimeFormat(LOCALE.language, opts).format(new Date(y, m - 1, d, 12));
}

export function formatDateTime(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.valueOf())) return "Sin fecha";
  try {
    return new Intl.DateTimeFormat(LOCALE.language, { dateStyle: "medium", timeStyle: "short",
      timeZone: LOCALE.timezone }).format(date);
  } catch {
    return date.toISOString();
  }
}

// "Today" in the configured timezone, as YYYY-MM-DD.
export function todayIso() {
  try {
    return new Intl.DateTimeFormat("en-CA", { timeZone: LOCALE.timezone }).format(new Date());
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

// ------------------------------------------------------------ page chrome
export function masthead(crumbs, title, subtitle) {
  const head = el("header", "page-head");
  const copy = el("div", "page-copy");
  const trail = el("p", "crumbs");
  crumbs.forEach((crumb, i) => {
    if (i) trail.append(el("span", "crumbs-sep", "›"));
    trail.append(el("span", i === crumbs.length - 1 ? "crumbs-current" : "crumbs-link", crumb));
  });
  copy.append(trail, el("h2", "page-title", title));
  if (subtitle) copy.append(el("p", "page-subtitle", subtitle));
  head.append(copy);
  return head;
}

export function card(title, label, extra = "") {
  const box = el("section", `instrument ${extra}`.trim());
  if (label) box.append(el("p", "label", label));
  if (title) box.append(el("h3", "card-title", title));
  return box;
}

export function pills(items, current, onPick) {
  const bar = el("div", "pills");
  bar.setAttribute("role", "tablist");
  items.forEach(([key, label]) => {
    const b = button(label, `pill${key === current ? " on" : ""}`, () => onPick(key));
    b.setAttribute("role", "tab");
    b.setAttribute("aria-selected", String(key === current));
    bar.append(b);
  });
  return bar;
}

export const empty = (text) => el("p", "empty", text);
export const errorLine = (what, error) => el("p", "empty is-error", `${what}: ${error?.message || error}`);

export function toast(text, kind = "ok") {
  const box = el("div", `toast toast--${kind}`, text);
  box.setAttribute("role", "status");
  document.body.append(box);
  setTimeout(() => box.remove(), 3200);
}

export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    toast("Copiado");
  } catch {
    toast("No se pudo copiar", "error");
  }
}

// The brand's uploaded logo when there is one (ctx.logos, from /api/config), else its initials.
export function brandMark(brand, ctx) {
  if (!ctx?.logos?.includes(brand.id)) return monogram(brand.name);
  const img = el("img", "monogram monogram--logo");
  img.alt = "";
  img.src = `/api/brand/logo?${new URLSearchParams({ brand: brand.id, v: String(ctx.logoVersion || 0) })}`;
  img.addEventListener("error", () => img.replaceWith(monogram(brand.name)));
  return img;
}

// Bytes -> base64 without building HTML or data URLs.
export async function fileToBase64(file) {
  const bytes = new Uint8Array(await file.arrayBuffer());
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

export function monogram(name) {
  const letters = String(name || "?").trim().split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  const m = el("span", "monogram", letters || "?");
  m.setAttribute("aria-hidden", "true");
  return m;
}

// ------------------------------------------------------------ svg (built with DOM, never parsed)
const SVG_NS = "http://www.w3.org/2000/svg";
export function svg(tag, attrs = {}) {
  const node = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, String(v)));
  return node;
}

export function smoothPath(points, tension = 0.18) {
  if (!points.length) return "";
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;
  const path = [`M ${points[0].x} ${points[0].y}`];
  const amount = Math.min(1, Math.max(0, tension)) / 6;
  for (let i = 0; i < points.length - 1; i += 1) {
    const before = points[Math.max(0, i - 1)], start = points[i], end = points[i + 1];
    const after = points[Math.min(points.length - 1, i + 2)];
    path.push(`C ${start.x + (end.x - before.x) * amount} ${start.y + (end.y - before.y) * amount}, `
      + `${end.x - (after.x - start.x) * amount} ${end.y - (after.y - start.y) * amount}, ${end.x} ${end.y}`);
  }
  return path.join(" ");
}

export const areaPath = (points, baseline) => (points.length
  ? `${smoothPath(points)} L ${points.at(-1).x} ${baseline} L ${points[0].x} ${baseline} Z` : "");

// Real series only: fewer than 2 real points renders nothing (no fake curves).
export function sparkline(values, className = "spark") {
  const nums = values.map(Number);
  if (nums.length < 2 || !nums.every(Number.isFinite)) return null;
  const min = Math.min(...nums), span = Math.max(...nums) - min || 1;
  const node = svg("svg", { class: className, viewBox: "0 0 100 36", preserveAspectRatio: "none", "aria-hidden": "true" });
  const points = nums.map((v, i) => ({ x: (i / (nums.length - 1)) * 100, y: 30 - ((v - min) / span) * 23 }));
  node.append(svg("path", { d: areaPath(points, 36), class: `${className}__area` }),
    svg("path", { d: smoothPath(points), class: `${className}__line` }));
  return node;
}

// Inline "+ Agregar" row that turns into an input; Enter creates, Escape cancels.
export function inlineAdd(container, { label = "+ Agregar", placeholder = "Escribí y Enter", create, onCreated }) {
  const row = button(label, "inline-add");
  const field = input("text", { placeholder, className: "field inline-add__input" });
  const err = el("p", "empty is-error");
  let busy = false;
  const reset = () => { busy = false; field.value = ""; field.disabled = false; err.remove(); if (field.isConnected) field.replaceWith(row); };
  row.addEventListener("click", () => { row.replaceWith(field); field.focus(); });
  field.addEventListener("keydown", async (event) => {
    if (event.key === "Escape") return reset();
    if (event.key !== "Enter" || busy) return;
    const title = field.value.trim();
    if (!title) return reset();
    busy = true;
    field.disabled = true;
    try {
      await create(title);
      reset();
      await onCreated?.();
    } catch (error) {
      busy = false;
      field.disabled = false;
      err.textContent = error.message;
      field.after(err);
      field.focus();
    }
  });
  field.addEventListener("blur", () => { if (!busy && !field.value.trim()) reset(); });
  container.append(row);
}

// Brand switcher for the creator views; hidden when there is only one active brand.
export function brandPicker(ctx) {
  if (ctx.brands.length < 2) return el("span");
  const pick = select(ctx.brands.map((b) => [b.id, b.name]), ctx.creatorBrand?.id, "field field--inline");
  pick.setAttribute("aria-label", "Marca");
  pick.addEventListener("change", () => ctx.setCreatorBrand(pick.value));
  return pick;
}

export const noBrand = () => el("p", "empty",
  "Todavía no configuraste ninguna marca. Pedile a tu agente: «agregá mi marca personal».");
