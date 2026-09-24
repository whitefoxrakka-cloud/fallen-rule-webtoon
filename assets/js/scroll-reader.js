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
  for (let i = 1; i <= ep.panelCount; i++) {
    const img = document.createElement("img");
    img.src = ep.base + String(i).padStart(2, "0") + ext;
    img.alt = ep.title + " — panel " + i + "/" + ep.panelCount;
    img.loading = i <= 2 ? "eager" : "lazy";
    img.decoding = "async";
    if (i === 1) img.fetchPriority = "high";
    canvas.appendChild(img);
  }
})();