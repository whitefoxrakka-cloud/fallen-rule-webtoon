(function () {
  const params = new URLSearchParams(location.search);
  const epId = params.get("ep") || "1";
  const ep = window.EPISODES[epId];
  if (!ep) { location.href = "index.html"; return; }

  document.title = ep.title + " — FALLEN RULE";
  document.getElementById("epTitle").textContent = ep.title;
  const lbl = document.getElementById("epLabel");
  if (lbl) lbl.textContent = "Episode " + epId;

  const canvas = document.getElementById("scrollCanvas");
  canvas.innerHTML = "";

  for (let i = 1; i <= ep.panelCount; i++) {
    const img = document.createElement("img");
    img.src = ep.base + String(i).padStart(2, "0") + ".png";
    img.alt = ep.title + " — panel " + i + "/" + ep.panelCount;
    img.loading = i <= 2 ? "eager" : "lazy";
    img.decoding = "async";
    if (i === 1) img.fetchPriority = "high";
    canvas.appendChild(img);
  }
})();