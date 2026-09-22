(function () {
  const params = new URLSearchParams(location.search);
  const epId = params.get("ep") || "1";
  const ep = window.EPISODES[epId];
  if (!ep) {
    location.href = "index.html";
    return;
  }

  const img = document.getElementById("panelImg");
  const counter = document.getElementById("panelCounter");
  const title = document.getElementById("epTitle");
  title.textContent = ep.title;

  let idx = 1;

  function render() {
    img.src = ep.base + String(idx).padStart(2, "0") + ".png";
    img.alt = ep.title + " — panel " + idx;
    counter.textContent = idx + " / " + ep.panelCount;
    document.body.dataset.first = idx === 1 ? "1" : "0";
    document.title = ep.title + " (" + idx + "/" + ep.panelCount + ") — FALLEN RULE";
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function go(step) {
    const next = idx + step;
    if (next < 1 || next > ep.panelCount) return;
    idx = next;
    render();
  }

  const halves = [
    ["prevPanel", -1],
    ["nextPanel", 1],
    ["prevPanelB", -1],
    ["nextPanelB", 1]
  ];
  halves.forEach(function (h) {
    document.getElementById(h[0]).addEventListener("click", function () { go(h[1]); });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft" || e.key === "PageUp") go(-1);
    else if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") go(1);
  });

  document.getElementById("panelStage").addEventListener("click", function (e) {
    const r = this.getBoundingClientRect();
    go((e.clientX - r.left) < r.width / 2 ? -1 : 1);
  });

  render();
})();