// --- LOGIC DIUBAH AGAR SINKRON DENGAN FLASK ---
let articles = [];
let currentArticle = ""; // Track the currently viewed article for export
let activeEventSource = null; // Track the running generation stream

// 1. Generate Articles (Ngobrol sama Flask, bukan OpenRouter langsung)
async function generateArticles() {
  const token = document.getElementById("token").value;
  const model = document.getElementById("model").value;
  const titlesInput = document.getElementById("titles").value;
  const mode = document.getElementById("mode-select").value || "science";
  const lang = document.getElementById("lang-select").value || "English";

  // Update UI Display
  document.getElementById("active-mode-display").innerText = `MODE: ${mode.toUpperCase()} | LANG: ${lang === "English" ? "EN" : "ID"}`;

  const btnExecute = document.getElementById("execute-btn");
  const btnStop = document.getElementById("stop-btn");

  const titleArray = titlesInput.split("\n").filter((t) => t.trim() !== "");
  const titlesParam = titleArray
    .map((t) => encodeURIComponent(t.trim()))
    .join(",");

  if (!token || !model || titleArray.length === 0) {
    appendLog("ERR: Your data is incomplete!", "err");
    return;
  }

  // --- 2. PASANG REM TANGAN (DISABLE) ---
  btnExecute.style.display = "none";
  btnStop.style.display = "block";

  const logContent = document.getElementById("log-content");
  logContent.innerHTML = "";
  ensureLogOpen(); // Pastikan log sidebar kebuka

  const url = `/generate-stream?token=${token}&model=${model}&titles=${titlesParam}&mode=${mode}&lang=${lang}`;
  activeEventSource = new EventSource(url);

  activeEventSource.onmessage = function (event) {
    const data = JSON.parse(event.data);
    appendLog(data.msg, data.type);

    if (data.msg.includes("ALL TASKS FINISHED")) {
      activeEventSource.close();
      activeEventSource = null;

      // --- 3. LEPAS REM (SUCCESS) ---
      unlockUI();

      loadArticles();
      updateStatus("All Articles Ready!", "#00b894");
      // If one article was generated, load it to show stats
      if (titleArray.length === 1) {
        const file = titleArray[0].toLowerCase().replace(/\s+/g, "-") + ".md";
        loadArticle(file);
      }
    }
  };

  activeEventSource.onerror = function () {
    appendLog("CONNECTION LOST: Server stopped streaming.", "err");
    if (activeEventSource) {
      activeEventSource.close();
      activeEventSource = null;
    }

    // --- 4. LEPAS REM (ERROR) ---
    unlockUI();
  };
}

function stopGeneration() {
  if (activeEventSource) {
    activeEventSource.close();
    activeEventSource = null;
    appendLog("🛑 STOPPED: Process terminated by user.", "err");
    updateStatus("STOPPED BY USER", "#ff4d4d");
    unlockUI();
  }
}

// Fungsi Helper biar gak nulis kode berulang
function unlockUI() {
  const btnExecute = document.getElementById("execute-btn");
  const btnStop = document.getElementById("stop-btn");

  btnExecute.style.display = "block";
  btnStop.style.display = "none";
  btnExecute.disabled = false;
  btnExecute.innerText = "⚡ EXECUTE_GENERATION";
  btnExecute.style.opacity = "1";
  btnExecute.style.cursor = "pointer";
}

// Fungsi helper untuk nambah baris log
function appendLog(msg, type) {
  const logContent = document.getElementById("log-content");
  const line = document.createElement("div");
  line.className = `log-line ${type || "info"}`;
  line.innerText = `> ${msg}`;
  logContent.appendChild(line);
  logContent.scrollTop = logContent.scrollHeight;
}

function toggleLog() {
  const panel = document.getElementById("log-panel");
  const btn = document.getElementById("toggle-btn");
  const title = document.getElementById("log-title");

  panel.classList.toggle("minimized");

  if (panel.classList.contains("minimized")) {
    btn.innerText = "»";
    title.style.opacity = "0";
  } else {
    btn.innerText = "_MINIMIZE";
    title.style.opacity = "1";
  }
}

// Fitur tambahan: Klik pada area panel yang menciut untuk membuka
document.getElementById("log-panel").addEventListener("click", function (e) {
  if (this.classList.contains("minimized")) {
    toggleLog();
  }
});

// Otomatis buka log saat generate dimulai
function ensureLogOpen() {
  const panel = document.getElementById("log-panel");
  if (panel.classList.contains("minimized")) {
    toggleLog();
  }
}

function updateStatus(text, color) {
  const el = document.getElementById("status-bar");
  if (el) {
    el.innerText = text;
    el.style.color = color;
  }
}

function toggleGenerator() {
  const panel = document.getElementById("generator-panel");
  panel.classList.toggle("collapsed");
}

async function suggestTopics() {
  const token = document.getElementById("token").value;
  const model = document.getElementById("model").value;
  const keyword = document.getElementById("keyword").value;
  const lang = document.getElementById("lang-select").value;

  if (!token || !model || !keyword) {
    appendLog("ERR: Token, Model, and Keyword are required for brainstorming!", "err");
    return;
  }

  appendLog(`BRAINSTORMING: Suggested titles for "${keyword}"...`, "warn");
  
  try {
    const res = await fetch("/suggest-topics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, model, keyword, lang })
    });
    const data = await res.json();
    
    if (data.status === "success") {
      const titlesTextarea = document.getElementById("titles");
      titlesTextarea.value = data.titles.join("\n");
      appendLog("SUCCESS: 3 titles suggested and added to queue.", "success");
    } else {
      appendLog("ERR: " + data.message, "err");
    }
  } catch (err) {
    appendLog("ERR: Failed to connect to brainstorming engine.", "err");
  }
}

function exportArticle(format) {
  if (!currentArticle) {
    alert("Please select an article first!");
    return;
  }
  const url = `/export/${format}/${currentArticle}`;
  window.open(url, "_blank");
}

async function copyToClipboard() {
  const contentEl = document.getElementById("preview-content");
  if (!contentEl || !currentArticle) return;

  try {
    // We get the raw text by fetching it again or using a cached version
    // For simplicity, let's fetch the .md file and strip metadata
    const res = await fetch("/output/" + currentArticle);
    const text = await res.text();
    const cleanText = text.replace(/^>.*?\n\n/s, "");

    await navigator.clipboard.writeText(cleanText);
    updateStatus("📋 COPIED TO CLIPBOARD", "#00ff00");
    
    // Visual feedback on the button could be added here
  } catch (err) {
    appendLog("ERR: Failed to copy text", "err");
  }
}

function updateArticleStats(text) {
  const statsEl = document.getElementById("article-stats");
  if (!text) {
    statsEl.style.display = "none";
    return;
  }

  // Strip metadata for accurate count
  const cleanText = text.replace(/^>.*?\n\n/s, "");
  const words = cleanText.trim().split(/\s+/).filter(w => w.length > 0).length;
  const readTime = Math.ceil(words / 200);

  document.getElementById("stat-words").innerText = `${words} WORDS`;
  document.getElementById("stat-time").innerText = `${readTime} MIN READ`;
  statsEl.style.display = "flex";
}

// --- LOAD PROMPT MODES FROM FLASK ---
async function loadModes() {
  try {
    const res = await fetch("/prompt-modes");
    const data = await res.json();
    const select = document.getElementById("mode-select");
    select.innerHTML = "";
    data.modes.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.label;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error("Could not load prompt modes:", err);
  }
}

// 2. Load & Render List (Ambil dari endpoint Flask /output/)
async function loadArticles() {
  const listElement = document.getElementById("article-list");
  updateStatus("SYNC: Scanning output folder...", "#f39c12");

  try {
    const syncRes = await fetch("/sync-archive", { method: "POST" });
    const syncData = await syncRes.json();

    if (syncData.status === "success") {
      const res = await fetch(
        "/output/articles.json?t=" + new Date().getTime(),
      );
      const data = await res.json();
      articles = data.articles;
      renderList();
      updateStatus(`READY: ${syncData.count} files synced.`, "#00b894");
    }
  } catch (err) {
    updateStatus("ERR: Sync Failed", "#d63031");
    console.error("Sync error:", err);
  }
}

function renderList() {
  const keyword = document.getElementById("search").value.toLowerCase();
  const listElement = document.getElementById("article-list");
  listElement.innerHTML = "";

  if (articles.length === 0) {
    listElement.innerHTML =
      "<div style='color:#888; padding:20px;'>Archive empty.</div>";
    return;
  }

  articles.forEach((file) => {
    // Format nama file jadi judul cantik di UI
    const title = file.replace(".md", "").replace(/-/g, " ").toUpperCase();
    if (title.toLowerCase().includes(keyword)) {
      const div = document.createElement("div");
      div.className = "article-item";
      div.innerText = "> " + title;
      div.onclick = () => {
        document
          .querySelectorAll(".article-item")
          .forEach((i) => i.classList.remove("active"));
        div.classList.add("active");
        loadArticle(file);
      };
      listElement.appendChild(div);
    }
  });
}

// 3. Load Individual Article (Ambil file .md beneran dari server)
async function loadArticle(file) {
  const previewArea = document.getElementById("preview-content");
  previewArea.innerHTML = "<i>Decrypting file from server...</i>";

  try {
    // Ambil file MD beneran dari endpoint Flask
    const res = await fetch("/output/" + file);
    if (!res.ok) throw new Error("File not found");
    const md = await res.text();

    // Render Markdown
    const previewArea = document.getElementById("preview-content");
    previewArea.innerHTML = marked.parse(md);

    currentArticle = file;
    document.getElementById("viewer-header").style.display = "flex";
    updateArticleStats(md);

    // Syntax Highlighting
    // Syntax Highlighting
    previewArea.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });

    // Math Rendering
    renderMathInElement(previewArea, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
      ],
    });

    document.getElementById("preview").scrollTop = 0; // Scroll ke atas
  } catch (err) {
    document.getElementById("preview-content").innerHTML = `<h2 style='color:#d63031'>FAILED TO LOAD DOCUMENT</h2><p>${err.message}</p>`;
  }
}

// Redundant loadArticles removed
// Utils
// Redundant function removed

document.getElementById("search").addEventListener("input", renderList);
// --- KABEL PENYAMBUNG (EVENT LISTENER) ---

document.addEventListener("DOMContentLoaded", function () {
  const btnExecute = document.getElementById("execute-btn");

  if (btnExecute) {
    btnExecute.addEventListener("click", function () {
      generateArticles();
    });
  }

  // Mode dropdown change
  const modeSelect = document.getElementById("mode-select");
  
  // Load modes & articles on startup
  loadModes();
  loadArticles();
});
