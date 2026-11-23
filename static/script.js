const $ = s => document.querySelector(s);
const EXAMPLE_TEXT = "Meet me at the park at 5 pm.";
const META = {
  monoalphabetic: {label: "Keyword (letters)", ph: "e.g. ZEBRA", sample: "ZEBRA",
    hint: "Every letter is swapped for a fixed substitute from one scrambled alphabet. Case, spaces and punctuation are kept.",
    title: "Substitution alphabet"},
  vigenere: {label: "Keyword (letters)", ph: "e.g. LEMON", sample: "LEMON",
    hint: "Each letter is shifted by the matching letter of the repeating keyword, so the same letter can encrypt differently. Non-letters are kept.",
    title: null},
  playfair: {label: "Keyword (letters)", ph: "e.g. MONARCHY", sample: "MONARCHY",
    hint: "Letters are encrypted in pairs using a 5×5 grid. The output is uppercase letters only, J becomes I, and X is used as padding.",
    title: "Playfair 5×5 grid"},
  polybius: {label: "Keyword (optional)", ph: "leave empty for the normal grid", sample: "",
    hint: "Each character becomes two digits: its row and column in an 8×8 grid. Characters outside the grid are written as ~hex~.",
    title: "Polybius 8×8 grid (row 1-8, column 1-8)"},
};
const keys = {};
let mode = "monoalphabetic", action = "encrypt", seq = 0, timer;

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}
const show = c => c === " " ? "␣" : c;

function drawTable(t) {
  const box = $("#table"), m = META[mode];
  box.replaceChildren();
  $("#tableCard").hidden = !t || !m.title;
  if (!t || !m.title) return;
  $("#tableTitle").textContent = m.title;
  if (t.kind === "mono") {
    const strip = el("div", "strip");
    [...t.plain].forEach(c => strip.append(el("span", "", c)));
    [...t.cipher].forEach(c => strip.append(el("span", "c", c)));
    box.append(strip, el("div", "note", "Top row: plain letter. Bottom row: what it becomes."));
  } else {
    const g = el("div", "grid");
    g.style.gridTemplateColumns = `repeat(${t.cols}, minmax(0, 1fr))`;
    t.cells.forEach(c => g.append(el("span", "", show(c))));
    box.append(g);
    if (t.cols === 5) box.append(el("div", "note", "I and J share the same cell."));
  }
}

async function run() {
  const my = ++seq;
  $("#status").textContent = "";
  try {
    const res = await fetch("/api/convert", {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({mode, action, text: $("#input").value, key: $("#key").value})});
    const d = await res.json();
    if (my !== seq) return;                      // a newer request has already replaced this one
    if (!res.ok) { $("#output").textContent = ""; $("#status").textContent = "⚠ " + d.error; drawTable(null); return; }
    $("#output").textContent = d.output;
    drawTable(d.table);
  } catch (e) {
    if (my === seq) $("#status").textContent = "⚠ Cannot reach the server. Is python app.py running?";
  }
}
const schedule = () => { clearTimeout(timer); timer = setTimeout(run, 150); };

function updateCount() {
  const n = $("#input").value.length;
  $("#count").textContent = `${n} character${n === 1 ? "" : "s"}`;
}

function setAction(a) {
  action = a;
  document.querySelectorAll("#action button").forEach(b => b.classList.toggle("on", b.dataset.a === a));
  $("#inLabel").textContent = a === "encrypt" ? "Plain text" : "Cipher text";
  $("#outLabel").textContent = a === "encrypt" ? "Cipher text" : "Plain text";
  $("#input").placeholder = a === "encrypt" ? "Type or paste text here…" : "Paste the cipher text here…";
}

function setMode(m) {
  keys[mode] = $("#key").value;
  mode = m;
  $("#method").value = m;
  $("#keyLabel").textContent = META[m].label;
  $("#key").placeholder = META[m].ph;
  $("#key").value = keys[m] || "";
  $("#hint").textContent = META[m].hint;
}

$("#method").onchange = e => { setMode(e.target.value); run(); };
$("#action").onclick = e => { if (e.target.dataset.a) { setAction(e.target.dataset.a); run(); } };
$("#input").oninput = () => { updateCount(); schedule(); };
$("#key").oninput = schedule;
$("#clear").onclick = () => { $("#input").value = ""; updateCount(); $("#input").focus(); run(); };
$("#example").onclick = () => {
  setAction("encrypt");
  $("#input").value = EXAMPLE_TEXT;
  if (!$("#key").value.trim()) $("#key").value = META[mode].sample;
  updateCount(); run();
};
$("#swap").onclick = () => {
  $("#input").value = $("#output").textContent;
  setAction(action === "encrypt" ? "decrypt" : "encrypt");
  updateCount(); run();
};
$("#copy").onclick = async () => {
  const b = $("#copy");
  try { await navigator.clipboard.writeText($("#output").textContent); b.textContent = "Copied ✓"; }
  catch (e) { b.textContent = "Press Ctrl+C"; }
  setTimeout(() => b.textContent = "Copy", 1400);
};

setMode("monoalphabetic");
run();