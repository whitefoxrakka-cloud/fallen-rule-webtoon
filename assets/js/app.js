// Tema (dark/light) + toggle
(function () {
  const key = "fallen-rule-theme";
  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
  }
  const saved = localStorage.getItem(key);
  if (saved) apply(saved);

  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", function () {
      const cur = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
      const next = cur === "light" ? "dark" : "light";
      apply(next);
      localStorage.setItem(key, next);
    });
  }
})();

// Simpan posisi baca novel (lanjut dari posisi terakhir)
(function () {
  const KEY = "fallen-rule-progress";
  const page = document.body && (document.body.dataset.page || "");
  const file = location.pathname.split("/").pop() || "index.html";

  function readProgress() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || null;
    } catch (e) {
      return null;
    }
  }
  function writeProgress(entry) {
    try {
      localStorage.setItem(KEY, JSON.stringify(entry));
    } catch (e) {
      /* storage penuh / tak tersedia */
    }
  }

  // Halaman novel: catat scroll, pulihkan posisi saat kembali
  const isNovel = !!document.querySelector("main.novel");
  if (isNovel && `${file}`.startsWith("arc1-")) {
    const titleNode = document.querySelector("h1.novel-title");
    const subNode = document.querySelector("h2.novel-sub");
    const title = (titleNode ? titleNode.textContent.trim() : "")
      + (subNode && subNode.textContent.trim() ? " — " + subNode.textContent.trim() : "");
    // Pulihkan posisi SEBELUM mencatat, agar tidak tertimpa nilai awal 0
    const saved = readProgress();
    let restoring = false;
    if (saved && saved.file === file && typeof saved.y === "number") {
      restoring = true;
      requestAnimationFrame(function () {
        window.scrollTo(0, saved.y);
        setTimeout(function () { restoring = false; }, 300);
      });
    }
    let timer = null;
    function record() {
      const doc = document.documentElement;
      const max = doc.scrollHeight - window.innerHeight;
      const pct = max > 0 ? Math.round((window.scrollY / max) * 100) : 0;
      writeProgress({ file, title, pct, y: window.scrollY });
    }
    window.addEventListener(
      "scroll",
      function () {
        if (restoring) return;
        clearTimeout(timer);
        timer = setTimeout(record, 300);
      },
      { passive: true }
    );
  }

  // Halaman index: kartu "lanjutkan baca"
  const resume = document.getElementById("resumeNovel");
  if (resume) {
    const saved = readProgress();
    if (saved && saved.file && saved.file !== "index.html") {
      resume.href = "novel/" + saved.file;
      resume.querySelector(".resume-title").textContent = saved.title || saved.file;
      if (saved.pct) {
        const p = resume.querySelector(".resume-pct");
        if (p) p.textContent = "Lanjut dari " + saved.pct + "%";
      }
      resume.hidden = false;
    }
  }
})();

// Kontrol baca: ukuran huruf, lebar kolom, daftar isi bab
(function () {
  const RKEY = "fallen-rule-reader";
  const main = document.querySelector("main.novel");

  function loadSettings() {
    try {
      return JSON.parse(localStorage.getItem(RKEY)) || {};
    } catch (e) {
      return {};
    }
  }
  function saveSettings(s) {
    try {
      localStorage.setItem(RKEY, JSON.stringify(s));
    } catch (e) {}
  }
  function apply() {
    if (!main) return;
    const s = loadSettings();
    main.style.fontSize = (s.font || 17) + "px";
    main.classList.toggle("novel-wide", !!s.wide);
  }

  if (main) {
    apply();
    const minus = document.getElementById("fontMinus");
    const plus = document.getElementById("fontPlus");
    const width = document.getElementById("widthToggle");
    const note = document.getElementById("readerNote");

    function setFont(delta) {
      const s = loadSettings();
      const font = Math.min(21, Math.max(14, (s.font || 17) + delta));
      s.font = font;
      saveSettings(s);
      apply();
      if (note) note.textContent = "Huruf " + font + "px";
    }
    if (minus) minus.addEventListener("click", function () { setFont(-1); });
    if (plus) plus.addEventListener("click", function () { setFont(1); });
    if (width) {
      width.addEventListener("click", function () {
        const s = loadSettings();
        s.wide = !s.wide;
        saveSettings(s);
        apply();
        if (note) note.textContent = s.wide ? "Lebar kolom: luas" : "Lebar kolom: standar";
      });
    }
  }

  // Daftar isi bab (dropdown)
  const picker = document.getElementById("chapPicker");
  if (picker) {
    if (picker.options.length > 1) {
      picker.addEventListener("change", function () {
        if (picker.value) location.href = picker.value;
      });
    } else {
      picker.disabled = true;
    }
  }
})();