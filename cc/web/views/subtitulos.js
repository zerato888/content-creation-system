// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Estudio de subtítulos (module `subtitulos`): your clip + the kit's caption engine. The preview is
// the engine's own grouping and styles (POST /api/captions/render with format "preview"), painted
// over the video; exports are .srt, the video with captions burned in, or a transparent layer.
import { api, button, card, el, empty, errorLine, input, masthead, safe, select, toast } from "../lib.js";

const LONG = 60 * 60 * 1000; // transcribing / exporting can take minutes
const state = { file: null, transcript: null, base: null, hook: "", edits: {}, annotated: null,
  marginV: 0.25, preview: null, output: null };

const clone = (x) => JSON.parse(JSON.stringify(x));
const num = (v, d) => (Number.isFinite(Number(v)) ? Number(v) : d);

function range(label, value, min, max, step, onChange) {
  const row = el("label");
  const r = el("input");
  Object.assign(r, { type: "range", min, max, step, value: String(value) });
  const out = el("span", "badge", String(value));
  r.addEventListener("input", () => { out.textContent = r.value; onChange(Number(r.value)); });
  row.append(el("span", "", label), r, out);
  return row;
}

function body(extra = {}) {
  const pick = (id) => state.edits[id] || id;
  return { file: state.file, base_preset: pick(state.base), ...(state.hook ? { hook_preset: pick(state.hook) } : {}),
    ...(state.annotated?.trim() ? { annotated_text: state.annotated } : {}), margin_v_frac: state.marginV, ...extra };
}

// ------------------------------------------------------------ preview painting
function painter(stage, video) {
  const overlay = el("div", "cs-overlay");
  stage.append(overlay);
  let lastKey = null;
  const paint = () => {
    const p = state.preview;
    if (!p) return overlay.replaceChildren();
    const t = video.currentTime;
    const block = p.blocks.find((b) => b.start <= t && t < b.end);
    overlay.style.bottom = `${Math.round(p.margin_v_frac * 100)}%`;
    if (!block) { lastKey = null; return overlay.replaceChildren(); }
    const key = `${block.start}`;
    const h = stage.clientHeight || 1;
    if (key !== lastKey) {
      lastKey = key;
      overlay.style.textAlign = block.alignment;
      overlay.replaceChildren(...block.lines.map((line) => {
        const row = el("span", "cs-line");
        row.style.lineHeight = String(line.spacing || 1);
        line.words.forEach((w, i) => {
          const span = el("span", "cs-word", `${i ? " " : ""}${w.t}`);
          span.dataset.s = String(w.s);
          span.style.fontFamily = `"${w.font}", system-ui, sans-serif`;
          span.style.fontSize = `${Math.max(6, w.size_frac * h)}px`;
          span.style.fontStyle = w.italic ? "italic" : "normal";
          span.style.fontWeight = w.bold ? "700" : "400";
          span.style.textTransform = w.case === "upper" ? "uppercase" : w.case === "lower" ? "lowercase" : "none";
          row.append(span);
        });
        return row;
      }));
    }
    overlay.querySelectorAll(".cs-word").forEach((s) => { s.style.opacity = Number(s.dataset.s) <= t ? "1" : "0"; });
  };
  const loop = () => { paint(); if (!video.paused && video.isConnected) requestAnimationFrame(loop); };
  video.addEventListener("play", loop);
  video.addEventListener("seeked", paint);
  video.addEventListener("timeupdate", paint);
  return () => { lastKey = null; paint(); };
}

// ------------------------------------------------------------ panels
function videosCard(videos, folder, reload) {
  const box = card("Tus clips", `Copiá tus videos en ${folder}`);
  if (!videos.length) box.append(empty("Todavía no hay clips en esa carpeta. Copiá uno y tocá «Actualizar»."));
  videos.forEach((v) => {
    const b = el("button", `item-card${v.file === state.file ? " is-on" : ""}`);
    b.type = "button";
    b.append(el("strong", "", v.file), el("span", "muted", v.has_transcript ? "Transcripto" : "Sin transcribir"));
    b.addEventListener("click", () => { Object.assign(state, { file: v.file, transcript: null, preview: null, output: null, annotated: null }); reload(); });
    box.append(b);
  });
  box.append(button("Actualizar", "btn btn--quiet btn--small", reload));
  return box;
}

function wordsCard(reload) {
  const box = el("details", "instrument");
  box.append(el("summary", "card-title", `Palabras (${state.transcript.words.length}) · corregí lo que Whisper escuchó mal`));
  const grid = el("div", "cs-words");
  const fields = state.transcript.words.map((w) => {
    const f = input("text", { value: w.text });
    f.size = Math.max(3, w.text.length);
    f.setAttribute("aria-label", `Palabra en ${w.start.toFixed(2)} s`);
    grid.append(f);
    return f;
  });
  box.append(grid, button("Guardar palabras", "btn", async () => {
    const words = state.transcript.words.map((w, i) => ({ ...w, text: fields[i].value }));
    try {
      state.transcript = (await api("/api/captions/transcript", { file: state.file, words })).transcript;
      state.annotated = null;
      toast("Palabras guardadas");
      reload();
    } catch (e) { toast(e.message, "error"); }
  }));
  return box;
}

function presetControls(presets, schedule) {
  const box = card("Estilo", "Presets del kit (fuentes libres) o los tuyos");
  const of = (kind) => presets.filter((p) => p.kind === kind).map((p) => [p.id, `${p.id}${p.source === "mine" ? " (mío)" : ""}`]);
  const base = select(of("base"), state.base);
  const hook = select([["", "Sin hook (todo igual)"], ...of("hook")], state.hook);
  base.setAttribute("aria-label", "Preset de base");
  hook.setAttribute("aria-label", "Preset de hook");
  const params = el("div", "stack stack--tight");
  const paintParams = () => {
    params.replaceChildren();
    if (!state.hook) return;
    const data = state.edits[state.hook] ||= clone(presets.find((p) => p.id === state.hook).data);
    const lay = data.layout;
    const count = select([["", "Automático"], ["2", "2 líneas"], ["3", "3 líneas"]], lay.line_count ? String(lay.line_count) : "");
    count.setAttribute("aria-label", "Líneas del hook");
    count.addEventListener("change", () => {
      if (count.value) {
        lay.line_count = Number(count.value);
        lay.line_size_mult = [0, 1, 2].map((i) => num(lay.line_size_mult?.[i], 1));
        lay.line_spacing_mult = [0, 1, 2].map((i) => num(Array.isArray(lay.line_spacing_mult) ? lay.line_spacing_mult[i] : lay.line_spacing_mult, 1.15));
      } else { delete lay.line_count; delete lay.line_size_mult; }
      paintParams();
      schedule();
    });
    params.append(el("p", "label", "Hook: líneas parejas por cantidad de letras"), count);
    if (lay.line_count) {
      for (let i = 0; i < lay.line_count; i += 1) {
        const row = el("div", "cs-row");
        row.append(range(`Línea ${i + 1} tamaño`, num(lay.line_size_mult[i], 1), 0.3, 2.5, 0.01, (v) => { lay.line_size_mult[i] = v; schedule(); }),
          range("espacio", num(lay.line_spacing_mult[i], 1.15), 0.6, 2, 0.01, (v) => { lay.line_spacing_mult[i] = v; schedule(); }));
        params.append(row);
      }
    }
    const align = select([["left", "Izquierda"], ["center", "Centro"], ["right", "Derecha"]], lay.alignment || "left");
    align.setAttribute("aria-label", "Alineación del hook");
    align.addEventListener("change", () => { lay.alignment = align.value; schedule(); });
    params.append(align, range("Aparición (ms)", num(data.reveal.fade_ms, 150), 0, 600, 10, (v) => { data.reveal.fade_ms = v; schedule(); }));
  };
  base.addEventListener("change", () => { state.base = base.value; schedule(); });
  hook.addEventListener("change", () => { state.hook = hook.value; paintParams(); schedule(); });
  paintParams();
  const pos = range("Altura (0 abajo · 1 arriba)", state.marginV, 0.05, 0.95, 0.01, (v) => { state.marginV = v; schedule(); });
  const annotated = input("textarea", { value: state.annotated });
  annotated.rows = 4;
  annotated.setAttribute("aria-label", "Texto anotado");
  annotated.addEventListener("input", () => { state.annotated = annotated.value; schedule(); });
  const n = input("number", { value: "6", className: "field field--num" });
  n.min = "1";
  n.setAttribute("aria-label", "Palabras del hook");
  const mark = button("Usar como hook", "btn btn--small", () => {
    const words = state.transcript.words.map((w) => w.text);
    const k = Math.max(1, Math.min(words.length, Number(n.value) || 1));
    annotated.value = state.annotated = `[hook]${words.slice(0, k).join(" ")}[/hook] ${words.slice(k).join(" ")}`;
    schedule();
  });
  const markRow = el("div", "cs-row");
  markRow.append(el("span", "", "Primeras"), n, el("span", "", "palabras"), mark);
  box.append(el("p", "label", "Base"), base, el("p", "label", "Hook"), hook, params, el("p", "label", "Posición"), pos,
    el("p", "label", "Texto anotado ([hook]…[/hook], *énfasis*)"), markRow, annotated);
  return box;
}

function exportCard(presets) {
  const box = card("Exportar", "Queda en tu carpeta de subtítulos (out/)");
  const result = el("div", "stack stack--tight");
  const show = () => {
    result.replaceChildren();
    if (!state.output) return;
    const a = el("a", "btn", `Descargar ${state.output}`);
    a.href = `/api/captions/output?${new URLSearchParams({ file: state.output })}`;
    a.download = state.output;
    result.append(a);
  };
  const run = (format, label) => {
    const b = button(label, format === "srt" ? "btn" : "btn btn--primary", async () => {
      b.disabled = true;
      const old = b.textContent;
      b.textContent = "Exportando…";
      try {
        state.output = (await api("/api/captions/render", body({ format }), { timeout: LONG })).file;
        toast("Listo");
      } catch (e) { toast(e.message, "error"); }
      b.disabled = false;
      b.textContent = old;
      show();
    });
    return b;
  };
  const adv = el("details");
  adv.append(el("summary", "", "Avanzado"), el("p", "muted", "Capa transparente (ProRes 4444 con alfa) para ponerla encima en tu editor."),
    run("alpha", "Capa transparente"));
  const name = input("text", { placeholder: "nombre-de-tu-preset" });
  name.setAttribute("aria-label", "Nombre del preset");
  const which = select([["hook", "Guardar el hook"], ["base", "Guardar la base"]], "hook");
  const save = button("Guardar preset", "btn btn--quiet", async () => {
    const id = which.value === "hook" ? state.hook : state.base;
    if (!id) return toast("Elegí un preset de hook primero", "error");
    const preset = state.edits[id] || presets.find((p) => p.id === id)?.data;
    try { const r = await api("/api/captions/save-preset", { name: name.value.trim(), preset }); toast(`Preset ${r.id} guardado`); } catch (e) { toast(e.message, "error"); }
  });
  box.append(run("srt", "Subtítulos (.srt)"), run("video", "Video con subtítulos"), adv, result,
    el("p", "label", "Tu preset"), which, name, save);
  show();
  return box;
}

// ------------------------------------------------------------ view
export async function render(root, ctx) {
  const reload = () => render(root, ctx);
  const head = masthead(["Estudio de subtítulos"], "Estudio de subtítulos", "Tu clip, palabra por palabra, con el estilo que elijas");
  const [vids, presetData] = await Promise.all([safe(api("/api/captions/videos")), safe(api("/api/captions/presets"))]);
  if (vids.error) return root.replaceChildren(head, errorLine("Estudio no disponible", vids.error));
  if (presetData.error) return root.replaceChildren(head, errorLine("Presets no disponibles", presetData.error));
  const presets = presetData.presets || [];
  state.base ||= presets.find((p) => p.kind === "base")?.id || null;
  const layout = el("div", "grid grid--sidebar");
  layout.append(videosCard(vids.videos || [], vids.folder, reload));
  if (!state.file) return root.replaceChildren(head, layout), layout.append(empty("Elegí un clip para empezar."));
  if (!state.transcript) {
    const tr = await safe(api(`/api/captions/transcript?${new URLSearchParams({ file: state.file })}`));
    if (tr.error) return root.replaceChildren(head, layout), layout.append(errorLine("No pude abrir el clip", tr.error));
    state.transcript = tr.transcript;
  }
  const work = el("div", "stack");
  const stage = el("div", "cs-stage");
  const video = el("video");
  video.controls = true;
  video.preload = "metadata";
  video.src = `/api/captions/video?${new URLSearchParams({ file: state.file })}`;
  stage.append(video);
  work.append(stage);
  if (!state.transcript) {
    const go = button("Transcribir (Whisper, en tu compu)", "btn btn--primary", async () => {
      go.disabled = true;
      go.textContent = "Transcribiendo… puede tardar unos minutos";
      try {
        state.transcript = (await api("/api/captions/transcript", { file: state.file, lang: ctx.cfg.locale?.language?.slice(0, 2) }, { timeout: LONG })).transcript;
        reload();
      } catch (e) { toast(e.message, "error"); go.disabled = false; go.textContent = "Transcribir"; }
    });
    work.append(card("Primero, la transcripción", "Nada sale de tu computadora"), go);
    layout.append(work);
    return root.replaceChildren(head, layout);
  }
  const repaint = painter(stage, video);
  state.annotated ??= state.transcript.words.map((w) => w.text).join(" ");
  const status = el("p", "hint", "");
  let timer = null;
  const schedule = () => {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      try { state.preview = await api("/api/captions/render", body({ format: "preview" })); status.textContent = "Vista previa aproximada: las fuentes finales las pone el motor al exportar."; }
      catch (e) { state.preview = null; status.textContent = e.message; }
      repaint();
    }, 350);
  };
  work.append(status, wordsCard(reload));
  const side = el("div", "grid grid--2");
  side.append(presetControls(presets, schedule), exportCard(presets));
  work.append(side);
  layout.append(work);
  root.replaceChildren(head, layout);
  schedule();
}
