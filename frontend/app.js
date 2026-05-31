/* ── element refs ───────────────────────────────────── */
const translateBtn   = document.querySelector("#translateBtn");
const audioBtn       = document.querySelector("#audioBtn");
const inputText      = document.querySelector("#inputText");
const audioFile      = document.querySelector("#audioFile");
const sourceLanguage = document.querySelector("#sourceLanguage");
const targetLanguage = document.querySelector("#targetLanguage");
const statusText     = document.querySelector("#status");
const resultDot      = document.querySelector("#resultDot");
const transcriptEl   = document.querySelector("#transcript");
const translationEl  = document.querySelector("#translation");
const charCount      = document.querySelector("#charCount");
const copyBtn        = document.querySelector("#copyBtn");
const resultCard     = document.querySelector("#resultCard");
const swapBtn        = document.querySelector("#swapBtn");
const dropZone       = document.querySelector("#dropZone");
const fileChosen     = document.querySelector("#fileChosen");
const tabs           = document.querySelectorAll(".tab");
const tabContents    = document.querySelectorAll(".tab-content");

/* ── tabs ────────────────────────────────────────────── */
tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    tabs.forEach(t => t.classList.remove("active"));
    tabContents.forEach(c => c.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");
  });
});

/* ── char counter ────────────────────────────────────── */
inputText.addEventListener("input", () => {
  charCount.textContent = inputText.value.length;
});

/* ── swap languages ──────────────────────────────────── */
swapBtn.addEventListener("click", () => {
  const src = sourceLanguage.value;
  const tgt = targetLanguage.value;
  // only swap if src exists in target options
  const srcOptInTarget = [...targetLanguage.options].some(o => o.value === src);
  const tgtOptInSource = [...sourceLanguage.options].some(o => o.value === tgt);
  if (srcOptInTarget && tgtOptInSource) {
    sourceLanguage.value = tgt;
    targetLanguage.value = src;
  }
});

/* ── drag & drop ─────────────────────────────────────── */
dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("audio/")) {
    // assign to the hidden file input via DataTransfer trick
    const dt = new DataTransfer();
    dt.items.add(file);
    audioFile.files = dt.files;
    showFileChosen(file.name);
  }
});

dropZone.addEventListener("click", () => audioFile.click());

audioFile.addEventListener("change", () => {
  if (audioFile.files[0]) showFileChosen(audioFile.files[0].name);
});

function showFileChosen(name) {
  fileChosen.textContent = `✓ ${name}`;
  fileChosen.hidden = false;
}

/* ── status helpers ──────────────────────────────────── */
function setStatus(state, label) {
  resultDot.className = `result-dot ${state}`;
  statusText.textContent = label;
}

function setLoading(isLoading, message = "working on it...") {
  translateBtn.disabled = isLoading;
  audioBtn.disabled     = isLoading;

  // toggle btn inner text
  [translateBtn, audioBtn].forEach(btn => {
    btn.querySelector(".btn-label").hidden  = isLoading;
    btn.querySelector(".btn-loader").hidden = !isLoading;
  });

  if (isLoading) setStatus("busy", message);
}

function showError(err) {
  setStatus("error", "error");
  translationEl.textContent = err.message || "something went wrong 😬";
  copyBtn.hidden = true;
  resultCard.classList.remove("has-result");
}

/* ── load language options ───────────────────────────── */
async function loadLanguages() {
  const response = await fetch("/api/languages");
  const data = await response.json();

  data.languages.forEach(lang => {
    sourceLanguage.add(new Option(lang.name, lang.code));
    if (lang.code !== "auto") {
      targetLanguage.add(new Option(lang.name, lang.code));
    }
  });

  sourceLanguage.value = "auto";
  targetLanguage.value = "ml";
}

/* ── text translate ──────────────────────────────────── */
translateBtn.addEventListener("click", async () => {
  const text = inputText.value.trim();
  if (!text) {
    setStatus("error", "enter some text first");
    return;
  }

  setLoading(true, "translating...");
  transcriptEl.textContent = text;
  translationEl.textContent = "—";
  copyBtn.hidden = true;
  resultCard.classList.remove("has-result");

  try {
    const response = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source_language: sourceLanguage.value,
        target_language: targetLanguage.value,
      }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "translation failed");

    translationEl.textContent = data.translated_text;
    setStatus("ready", `done ✓  ${data.source_language} → ${data.target_language}`);
    copyBtn.hidden = false;
    resultCard.classList.add("has-result");
  } catch (err) {
    showError(err);
  } finally {
    setLoading(false);
  }
});

/* ── audio transcribe + translate ────────────────────── */
audioBtn.addEventListener("click", async () => {
  const file = audioFile.files[0];
  if (!file) {
    setStatus("error", "pick a file first");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("source_language", sourceLanguage.value);
  formData.append("target_language", targetLanguage.value);

  setLoading(true, "transcribing...");
  transcriptEl.textContent = "—";
  translationEl.textContent = "—";
  copyBtn.hidden = true;
  resultCard.classList.remove("has-result");

  try {
    const response = await fetch("/api/transcribe-translate", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "audio translation failed");

    transcriptEl.textContent = data.transcript;
    translationEl.textContent = data.translated_text;
    setStatus("ready", `done ✓  ${data.source_language} → ${data.target_language}`);
    copyBtn.hidden = false;
    resultCard.classList.add("has-result");
  } catch (err) {
    showError(err);
  } finally {
    setLoading(false);
  }
});

/* ── copy button ─────────────────────────────────────── */
copyBtn.addEventListener("click", async () => {
  const text = translationEl.textContent;
  if (!text || text === "—") return;
  try {
    await navigator.clipboard.writeText(text);
    copyBtn.textContent = "copied! ✓";
    setTimeout(() => { copyBtn.textContent = "copy 📋"; }, 1800);
  } catch {
    copyBtn.textContent = "couldn't copy :(";
    setTimeout(() => { copyBtn.textContent = "copy 📋"; }, 1800);
  }
});

/* ── init ────────────────────────────────────────────── */
loadLanguages().catch(showError);