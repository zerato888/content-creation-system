// SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
// Teleprompter for one script: teleprompter.html?guion=<file>. Text goes in via textContent only.
import { api } from "./lib.js";

const params = new URLSearchParams(window.location.search);
const FILE = params.get("guion");
const WORDS_PER_SECOND = 2.6;
const $ = (id) => document.getElementById(id);
const script = $("script");

const stored = (key, fallback) => { try { return Number.parseFloat(localStorage.getItem(key)) || fallback; } catch { return fallback; } };
const store = (key, value) => { try { localStorage.setItem(key, String(value)); } catch { /* private mode */ } };

let speed = stored("tp_speed", 40);   // px per second
let size = stored("tp_size", 42);     // px
let playing = false, last = null, y = 0, maxScroll = 1, guion = null, version = "full";

const measure = () => requestAnimationFrame(() => { maxScroll = Math.max(1, script.scrollHeight - window.innerHeight); });

function draw() {
  const hv = guion.hooks && Number.isInteger(guion.hooks.elegida) ? guion.hooks.opciones[guion.hooks.elegida] : null;
  const hook = hv || guion.hook || "";
  const body = version === "tp" ? (guion.talking_points || "") : ((guion.cuerpo || "").trim() || guion.talking_points || "");
  script.replaceChildren();
  script.style.fontSize = `${size}px`;
  if (!hook && !body) { script.textContent = "Este guion está vacío. Escribilo antes de abrir el teleprompter."; return; }
  if (hook) { const h = document.createElement("div"); h.className = "hook"; h.textContent = hook; script.append(h, document.createElement("br")); }
  script.append(document.createTextNode(body));
  const words = `${hook} ${body}`.trim().split(/\s+/).filter(Boolean).length;
  $("info").textContent = `~${Math.round(words / WORDS_PER_SECOND)} s · espacio: empezar/pausa · ↑↓ velocidad · +/- letra · R reiniciar · F pantalla completa`;
  $("controls").querySelector('[data-act="version"]').textContent = version === "tp" ? "Guion completo" : "Puntos clave";
  measure();
}

function setPlaying(value) { playing = value; $("btn-play").textContent = value ? "⏸ Pausa" : "▶ Empezar"; }
function reset() { y = 0; script.style.transform = "translateY(0px)"; $("progress").style.width = "0%"; }
function tick(t) {
  if (last === null) last = t;
  const dt = (t - last) / 1000;
  last = t;
  if (playing) {
    y -= speed * dt;
    script.style.transform = `translateY(${y}px)`;
    $("progress").style.width = `${Math.min(100, Math.max(0, (-y / maxScroll) * 100))}%`;
    if (-y >= maxScroll) setPlaying(false);
  }
  requestAnimationFrame(tick);
}
function countdownThenPlay() {
  const cd = $("countdown");
  let n = 3;
  cd.hidden = false;
  cd.textContent = String(n);
  const iv = setInterval(() => {
    n -= 1;
    if (n === 0) { cd.hidden = true; clearInterval(iv); setPlaying(true); } else cd.textContent = String(n);
  }, 700);
}
const toggle = () => (playing ? setPlaying(false) : countdownThenPlay());
const bumpSpeed = (d) => { speed = Math.max(5, speed + d); store("tp_speed", speed); };
const bumpSize = (d) => { size = Math.max(18, size + d); store("tp_size", size); script.style.fontSize = `${size}px`; measure(); };
const fullscreen = () => (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen());

const ACTIONS = { reset, slower: () => bumpSpeed(-5), faster: () => bumpSpeed(5), smaller: () => bumpSize(-2),
  bigger: () => bumpSize(2), full: fullscreen, version: () => { version = version === "tp" ? "full" : "tp"; reset(); draw(); } };
$("btn-play").addEventListener("click", toggle);
$("controls").addEventListener("click", (e) => { const act = e.target.closest("[data-act]")?.dataset.act; if (act) ACTIONS[act](); });
$("stage").addEventListener("click", toggle);
document.addEventListener("keydown", (e) => {
  if (e.code === "Space") { e.preventDefault(); toggle(); }
  if (e.key === "ArrowUp") bumpSpeed(5);
  if (e.key === "ArrowDown") bumpSpeed(-5);
  if (e.key === "+" || e.key === "=") bumpSize(2);
  if (e.key === "-") bumpSize(-2);
  if (e.key.toLowerCase() === "r") reset();
  if (e.key.toLowerCase() === "f") fullscreen();
});
let hideTimer = null;
const wake = () => { $("controls").classList.remove("faded"); clearTimeout(hideTimer); hideTimer = setTimeout(() => $("controls").classList.add("faded"), 3000); };
["mousemove", "keydown", "click"].forEach((ev) => document.addEventListener(ev, wake));
wake();

(async () => {
  try {
    guion = (await api("/api/guiones")).guiones.find((g) => g.file === FILE) || null;
  } catch (error) {
    script.textContent = `No se pudo cargar el guion: ${error.message}`;
    return;
  }
  if (!guion) { script.textContent = "Guion no encontrado."; return; }
  document.title = `Teleprompter · ${guion.titulo}`;
  draw();
  requestAnimationFrame(tick);
})();
