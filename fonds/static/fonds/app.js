// Trace chaque <div class="graphique" data-figure="id"> à partir du JSON du <script id="id">.
(function () {
  function rgb(hexa) {
    var h = hexa.replace("#", "");
    return [0, 2, 4].map(function (i) { return parseInt(h.substr(i, 2), 16); }).join(", ");
  }
  function sombre() {
    var t = document.documentElement.dataset.theme;
    return t ? t === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function tracer(racine) {
    if (!window.Plotly) return;
    var style = getComputedStyle(document.documentElement);
    var texte = style.getPropertyValue("--texte").trim() || "#1c2733";
    var primaire = style.getPropertyValue("--primaire").trim(), accent = style.getPropertyValue("--accent").trim();
    (racine || document).querySelectorAll(".graphique[data-figure]").forEach(function (el) {
      var source = document.getElementById(el.dataset.figure);
      if (!source) return;
      var json = source.textContent;
      // En thème sombre, la couleur principale (souvent foncée) cède la place à la couleur d'accent de la SGO.
      if (sombre() && primaire && accent) {
        json = json.split(primaire).join(accent).split(primaire.toLowerCase()).join(accent)
                   .split("rgba(" + rgb(primaire)).join("rgba(" + rgb(accent));
      }
      var fig = JSON.parse(json);
      fig.layout = fig.layout || {};
      fig.layout.font = Object.assign({}, fig.layout.font, { color: texte, family: getComputedStyle(document.body).fontFamily });
      Plotly.react(el, fig.data, fig.layout, { responsive: true, displaylogo: false,
        modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"] });
    });
  }
  document.addEventListener("DOMContentLoaded", function () { tracer(); });
  document.addEventListener("htmx:afterSwap", function (e) { tracer(e.target); });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () { tracer(); });
})();
