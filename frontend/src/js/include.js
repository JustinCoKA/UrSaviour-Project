// js/include.js
function includeHTML() {
  const elements = document.querySelectorAll('[data-include]');
  elements.forEach(el => {
    const file = el.getAttribute('data-include');
    fetch(file)
      .then(res => res.text())
      .then(data => {
        el.innerHTML = data;
      })
      .catch(() => {
        el.innerHTML = `<p style="color:red;">Failed to load ${file}</p>`;
      });
  });
}

document.addEventListener("DOMContentLoaded", includeHTML);

