// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Biblioteca (module `biblioteca`): what the installed kit ships, with «Copiar ID». Starts empty.
import { api, button, card, copyText, el, empty, errorLine, masthead, safe } from "../lib.js";

const SECTIONS = [["captions", "Subtítulos"], ["broll_modes", "Material de apoyo (b-roll)"], ["carousel", "Carruseles"],
  ["components", "Componentes"], ["voices", "Voces"]];

export async function render(root) {
  const data = await safe(api("/api/library"));
  const head = masthead(["Biblioteca"], "Biblioteca", "Todo lo que tu kit tiene instalado. Copiá el ID y pasáselo a tu agente.");
  if (data.error) return root.replaceChildren(head, errorLine("Biblioteca no disponible", data.error));
  const grid = el("div", "grid grid--2");
  SECTIONS.forEach(([key, title]) => {
    const box = card(title, `${(data[key] || []).length} disponibles`);
    if (!(data[key] || []).length) box.append(empty("Vacío por ahora."));
    (data[key] || []).forEach((item) => {
      const row = el("div", "row");
      const main = el("div", "row-main");
      main.append(el("strong", "", item.label || item.id), el("span", "muted", item.id));
      row.append(main);
      if (item.status) row.append(el("span", "chip", item.status));
      const copy = button("Copiar ID", "btn btn--small", () => copyText(item.id));
      copy.setAttribute("aria-label", `Copiar ID ${item.id}`);
      row.append(copy);
      box.append(row);
    });
    grid.append(box);
  });
  const hooks = card("Banco de hooks", data.hooks_bank ? "Instalado" : "No instalado");
  hooks.append(el("p", "muted", data.hooks_bank ? "Lo usás desde Guion y grabación." : "Se instala con el kit de guion."));
  grid.append(hooks);
  root.replaceChildren(head, grid);
}
