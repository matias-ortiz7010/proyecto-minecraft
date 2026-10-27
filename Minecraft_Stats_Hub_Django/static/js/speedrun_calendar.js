(() => {
  "use strict";
  const container = document.querySelector("[data-sr-datepicker]");
  if (!container) return;

  const input = container.querySelector('input[name="fecha"]');
  const toggle = container.querySelector("[data-sr-toggle]");
  const panel = container.querySelector("[data-sr-calendar]");
  const monthSelect = container.querySelector("[data-sr-month]");
  const yearSelect = container.querySelector("[data-sr-year]");
  const days = container.querySelector("[data-sr-days]");
  const months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
                  "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

  const today = new Date();
  const pad = value => String(value).padStart(2, "0");
  const formatDate = date => `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()}`;

  function parseDate(value) {
    const raw = value.trim();
    let match = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(raw);
    let day, month, year;
    if (match) {
      day = Number(match[1]); month = Number(match[2]) - 1; year = Number(match[3]);
    } else {
      match = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(raw);
      if (!match) return null;
      year = Number(match[1]); month = Number(match[2]) - 1; day = Number(match[3]);
    }
    if (year < 1 || year > 9999 || month < 0 || month > 11 || day < 1 || day > 31) return null;
    const d = new Date(0);
    d.setFullYear(year, month, day);
    d.setHours(12, 0, 0, 0);
    return d.getFullYear() === year && d.getMonth() === month && d.getDate() === day ? d : null;
  }

  let viewed = parseDate(input.value) || new Date(today.getFullYear(), today.getMonth(), 1);
  viewed = new Date(viewed.getFullYear(), viewed.getMonth(), 1);

  months.forEach((month, index) => {
    monthSelect.add(new Option(month, String(index)));
  });

  function render() {
    const year = viewed.getFullYear();
    const month = viewed.getMonth();
    monthSelect.value = String(month);
    // Opciones de año correctas (2009, 2010, ..., 2026), nunca días 1-31.
    const startYear = Math.min(2009, year);
    const endYear = Math.max(today.getFullYear() + 5, year);
    yearSelect.replaceChildren();
    for (let y = startYear; y <= endYear; y++) {
      yearSelect.add(new Option(String(y), String(y)));
    }
    yearSelect.value = String(year);

    days.replaceChildren();
    const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7;
    const count = new Date(year, month + 1, 0).getDate();
    const selected = parseDate(input.value);
    for (let i = 0; i < firstWeekday; i++) {
      const blank = document.createElement("span");
      blank.setAttribute("aria-hidden", "true");
      days.appendChild(blank);
    }
    for (let day = 1; day <= count; day++) {
      const cell = document.createElement("button");
      cell.type = "button";
      cell.className = "sr-calendar-day";
      cell.textContent = String(day);
      cell.setAttribute("aria-label", `${day} de ${months[month].toLowerCase()} de ${year}`);
      const isSelected = selected && selected.getFullYear() === year &&
        selected.getMonth() === month && selected.getDate() === day;
      cell.setAttribute("aria-pressed", isSelected ? "true" : "false");
      if (isSelected) cell.classList.add("selected");
      if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {
        cell.classList.add("today");
      }
      cell.addEventListener("click", () => {
        input.value = formatDate(new Date(year, month, day));
        input.dispatchEvent(new Event("change", { bubbles: true }));
        closePanel();
        toggle.focus();
      });
      days.appendChild(cell);
    }
  }

  function closePanel() {
    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    panel.classList.remove("sr-calendar-up");
  }

  function openPanel() {
    const current = parseDate(input.value);
    if (current) viewed = new Date(current.getFullYear(), current.getMonth(), 1);
    render();
    panel.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    panel.classList.remove("sr-calendar-up");
    const bounds = panel.getBoundingClientRect();
    const rootBounds = container.getBoundingClientRect();
    if (bounds.bottom > window.innerHeight - 12 && rootBounds.top > bounds.height + 12) {
      panel.classList.add("sr-calendar-up");
    }
    const initialFocus = panel.querySelector(".sr-calendar-day.selected") || panel.querySelector(".sr-calendar-day");
    if (initialFocus) initialFocus.focus();
  }

  toggle.addEventListener("click", () => panel.hidden ? openPanel() : closePanel());
  container.querySelector("[data-sr-prev]").addEventListener("click", () => {
    viewed = new Date(viewed.getFullYear(), viewed.getMonth() - 1, 1);
    render();
  });
  container.querySelector("[data-sr-next]").addEventListener("click", () => {
    viewed = new Date(viewed.getFullYear(), viewed.getMonth() + 1, 1);
    render();
  });
  monthSelect.addEventListener("change", () => {
    viewed = new Date(viewed.getFullYear(), Number(monthSelect.value), 1);
    render();
  });
  yearSelect.addEventListener("change", () => {
    viewed = new Date(Number(yearSelect.value), viewed.getMonth(), 1);
    render();
  });
  container.querySelector("[data-sr-today]").addEventListener("click", () => {
    input.value = formatDate(today);
    input.dispatchEvent(new Event("change", { bubbles: true }));
    closePanel(); toggle.focus();
  });
  container.querySelector("[data-sr-clear]").addEventListener("click", () => {
    input.value = "";
    input.dispatchEvent(new Event("change", { bubbles: true }));
    closePanel(); toggle.focus();
  });
  container.querySelector("[data-sr-close]").addEventListener("click", () => {
    closePanel(); toggle.focus();
  });
  input.addEventListener("change", () => {
    const parsed = parseDate(input.value);
    if (parsed) viewed = new Date(parsed.getFullYear(), parsed.getMonth(), 1);
    if (!panel.hidden) render();
  });
  document.addEventListener("pointerdown", event => {
    if (!panel.hidden && !container.contains(event.target)) closePanel();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !panel.hidden) {
      closePanel(); toggle.focus();
    }
  });
})();
