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