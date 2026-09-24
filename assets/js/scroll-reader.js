(function () {
  const params = new URLSearchParams(location.search);
  const epId = params.get("ep") || "1";
  const ep = window.EPISODES[epId];
  if (!ep) { location.href = "index.html"; return; }

  const ids = Object.keys(window.EPISODES).sort((a, b) => Number(a) - Number(b));

  document.title = ep.title + " — FALLEN RULE";
  document.getElementById("epTitle").textContent = ep.title;

  const picker = document.getElementById("epPicker");
  if (picker) {
    ids.forEach(function (id) {
      const opt = document.createElement("option");
      opt.value = id;
      opt.textContent = window.EPISODES[id].title;
      if (id === epId) opt.selected = true;
      picker.appendChild(opt);
    });
    picker.addEventListener("change", function () {
      location.href = "reader.html?ep=" + picker.value;
    });
  }

  const curIdx = ids.indexOf(epId);
  const prevEl = document.getElementById("prevEp");
  const nextEl = document.getElementById("nextEp");
  if (prevEl) prevEl.href = curIdx > 0 ? "reader.html?ep=" + ids[curIdx - 1] : "#";
  if (nextEl) nextEl.href = curIdx < ids.length - 1 ? "reader.html?ep=" + ids[curIdx + 1] : "#";

  const canvas = document.getElementById("scrollCanvas");
  canvas.innerHTML = "";

  const ext = ep.ext || ".png";
  const imgs = [];
  for (let i = 1; i <= ep.panelCount; i++) {
    const img = document.createElement("img");
    img.src = ep.base + String(i).padStart(2, "0") + ext;
    img.alt = ep.title + " — panel " + i + "/" + ep.panelCount;
    img.loading = i <= 2 ? "eager" : "lazy";
    img.decoding = "async";
    if (i === 1) img.fetchPriority = "high";
    imgs.push(img);
    canvas.appendChild(img);
  }

  // Zoom panel: klik untuk perbesar, Esc untuk tutup, panah kiri/kanan ganti panel
  let zoomEl = null, zoomImg = null, zoomIdx = 0;

  function openZoom(idx) {
    if (zoomEl) return;
    zoomIdx = (idx + imgs.length) % imgs.length;
    zoomEl = document.createElement("div");
    zoomEl.className = "zoom-overlay";
    zoomEl.setAttribute("role", "dialog");
    zoomEl.setAttribute("aria-label", "Pembesaran panel");
    zoomImg = document.createElement("img");
    zoomImg.src = imgs[zoomIdx].src;
    zoomImg.alt = imgs[zoomIdx].alt;
    const cap = document.createElement("div");
    cap.className = "zoom-cap";
    cap.textContent = (zoomIdx + 1) + " / " + imgs.length;
    cap.appendChild(document.createElement("br"));
    const hint = document.createElement("span");
    hint.className = "zoom-hint";
    hint.textContent = "Esc tutup · panah kiri/kanan ganti panel";
    cap.appendChild(hint);
    zoomEl.appendChild(zoomImg);
    zoomEl.appendChild(cap);
    zoomEl.addEventListener("click", function (e) {
      if (e.target === zoomEl || e.target === cap) closeZoom();
    });
    document.body.appendChild(zoomEl);
    document.body.style.overflow = "hidden";
  }

  function closeZoom() {
    if (!zoomEl) return;
    zoomEl.remove();
    zoomEl = null;
    zoomImg = null;
    document.body.style.overflow = "";
  }

  function cycle(delta) {
    if (!zoomEl) return;
    zoomIdx = (zoomIdx + delta + imgs.length) % imgs.length;
    zoomImg.src = imgs[zoomIdx].src;
    zoomImg.alt = imgs[zoomIdx].alt;
    const cap = zoomEl.querySelector(".zoom-cap");
    if (cap) cap.childNodes[0].nodeValue = (zoomIdx + 1) + " / " + imgs.length + "\n";
  }

  imgs.forEach(function (img, i) {
    img.addEventListener("click", function () { openZoom(i); });
  });
  document.addEventListener("keydown", function (e) {
    if (zoomEl) {
      if (e.key === "Escape") closeZoom();
      else if (e.key === "ArrowRight") cycle(1);
      else if (e.key === "ArrowLeft") cycle(-1);
      return;
    }
    if (e.key === "Escape" && document.querySelector(".zoom-overlay")) closeZoom();
  });
})();