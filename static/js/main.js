// --- LOGIC DIUBAH AGAR SINKRON DENGAN FLASK ---
let articles = [];

// 1. Generate Articles (Ngobrol sama Flask, bukan OpenRouter langsung)
async function generateArticles() {
  const token = document.getElementById("token").value;
  const model = document.getElementById("model").value;
  const titlesInput = document.getElementById("titles").value;

  // 1. Ambil referensi tombolnya
  const btnExecute = document.querySelector(".btn-primary");

  const titleArray = titlesInput.split("\n").filter((t) => t.trim() !== "");
  const titlesParam = titleArray
    .map((t) => encodeURIComponent(t.trim()))
    .join(",");

  if (!token || !model || titleArray.length === 0) {
    appendLog("ERR: Data tidak lengkap!", "err");
    return;
  }

  // --- 2. PASANG REM TANGAN (DISABLE) ---
  btnExecute.disabled = true;
  btnExecute.innerText = "⚡ GENERATING..."; // Ubah teks biar keren
  btnExecute.style.opacity = "0.5";
  btnExecute.style.cursor = "not-allowed";

  const logContent = document.getElementById("log-content");
  logContent.innerHTML = "";
  ensureLogOpen(); // Pastikan log sidebar kebuka

  const url = `/generate-stream?token=${token}&model=${model}&titles=${titlesParam}`;
  const eventSource = new EventSource(url);

  eventSource.onmessage = function (event) {
    const data = JSON.parse(event.data);
    appendLog(data.msg, data.type);

    if (data.msg.includes("ALL TASKS FINISHED")) {
      eventSource.close();

      // --- 3. LEPAS REM (SUCCESS) ---
      unlockButton(btnExecute);

      loadArticles();
      updateStatus("All Articles Ready!", "#00b894");
    }
  };

  eventSource.onerror = function () {
    appendLog("CONNECTION LOST: Server stopped streaming.", "err");
    eventSource.close();

    // --- 4. LEPAS REM (ERROR) ---
    // Jangan lupa dibuka lagi biar user bisa coba lagi kalau error
    unlockButton(btnExecute);
  };
}

// Fungsi Helper biar gak nulis kode berulang
function unlockButton(btn) {
  btn.disabled = false;
  btn.innerText = "EXECUTE GENERATION";
  btn.style.opacity = "1";
  btn.style.cursor = "pointer";
}

// Fungsi helper untuk nambah baris log
function appendLog(msg, type) {
  const logContent = document.getElementById("log-content");
  const line = document.createElement("div");
  line.className = `log-line ${type || "info"}`;
  line.innerText = `> ${msg}`;
  logContent.appendChild(line);

  // Auto scroll ke bawah
  logContent.scrollTop = logContent.scrollHeight;
}

function toggleLog() {
  const panel = document.getElementById("log-panel");
  const btn = document.getElementById("toggle-btn");
  const title = document.getElementById("log-title");

  panel.classList.toggle("minimized");

  if (panel.classList.contains("minimized")) {
    btn.innerText = "»"; // Icon arah buka
    title.style.opacity = "0"; // Sembunyikan judul halus
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

// Tambahkan ini di fungsi generateArticles agar otomatis terbuka saat running
function openLogAutomatically() {
  const panel = document.getElementById("log-panel");
  if (panel.classList.contains("minimized")) {
    toggleLog();
  }
}

function appendLog(msg, type) {
  const logContent = document.getElementById("log-content");
  const line = document.createElement("div");
  line.className = `log-line ${type}`;
  line.innerText = `> ${msg}`;
  logContent.appendChild(line);
  logContent.scrollTop = logContent.scrollHeight;
}

/**
 * Helper untuk memperbarui teks dan warna pada status bar
 */
function updateStatus(text, color) {
  const el = document.getElementById("status-bar");
  if (el) {
    el.innerText = text;
    el.style.color = color;
  }
}

// 2. Load & Render List (Ambil dari endpoint Flask /output/)
async function loadArticles() {
  const listElement = document.getElementById("article-list");
  listElement.innerHTML = "<i>Loading archive...</i>";

  try {
    // Ambil JSON index dari server Flask
    const res = await fetch(
      "/output/articles.json?t=" + str(new Date().getTime()),
    ); // tambahkan cachebuster
    const data = await res.json();
    articles = data.articles;
    renderList();
  } catch (err) {
    listElement.innerHTML =
      "<div style='color:red; padding:20px;'>ERR: Could not load index.</div>";
    console.error("Critical: Could not load index.", err);
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
  const preview = document.getElementById("preview");
  preview.innerHTML = "<i>Decrypting file from server...</i>";

  try {
    // Ambil file MD beneran dari endpoint Flask
    const res = await fetch("/output/" + file);
    if (!res.ok) throw new Error("File not found");
    const md = await res.text();

    // Render Markdown
    preview.innerHTML = marked.parse(md);

    // Syntax Highlighting
    preview.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });

    // Math Rendering
    renderMathInElement(preview, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
      ],
    });

    preview.scrollTop = 0; // Scroll ke atas
  } catch (err) {
    preview.innerHTML = `<h2 style='color:#d63031'>FAILED TO LOAD DOCUMENT</h2><p>${err.message}</p>`;
  }
}

async function loadArticles() {
  const listElement = document.getElementById("article-list");
  updateStatus("SYNC: Scanning output folder...", "#f39c12");

  try {
    // 1. Jalankan script Python kamu lewat Flask
    const syncRes = await fetch("/sync-archive", { method: "POST" });
    const syncData = await syncRes.json();

    if (syncData.status === "success") {
      // 2. Setelah JSON terupdate, ambil isinya untuk ditampilkan di UI
      // Gunakan timestamp (?t=...) supaya browser gak pakai cache lama
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
// Utils
function updateStatus(text, color) {
  const el = document.getElementById("status-bar");
  el.innerText = text;
  el.style.color = color;
}

document.getElementById("search").addEventListener("input", renderList);
// --- KABEL PENYAMBUNG (EVENT LISTENER) ---

document.addEventListener("DOMContentLoaded", function () {
  const btnExecute = document.querySelector(".btn-primary");

  if (btnExecute) {
    btnExecute.addEventListener("click", function () {
      // Jalankan fungsi utama
      generateArticles();
    });
  }

  // Inisialisasi awal list artikel
  loadArticles();
});
// Load daftar artikel saat pertama kali buka halaman
window.onload = loadArticles;
