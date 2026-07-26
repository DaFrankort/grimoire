let filterOptions = {};
let selectedClassFilters = new Set();
let selectedSchoolFilters = new Set();
let selectedLevelFilters = new Set();

function _createSpellRowHtml(spell, isSelected) {
  const nameHtml = spell.url
    ? `<a href="${spell.url}" target="_blank" rel="noopener noreferrer">${spell.name}</a>`
    : spell.name;

  const escapedName = spell.name.replace(/'/g, "\\'");
  const escapedSource = spell.source.replace(/'/g, "\\'");

  const actionButton = isSelected
    ? `<button class="btn btn-primary" onClick="deselectSpell('${escapedName}', '${escapedSource}')">-</button>`
    : `<button class="btn btn-primary" onClick="selectSpell('${escapedName}', '${escapedSource}')">+</button>`;

  return `
    <td>${nameHtml}</td>
    <td>${spell.source}</td>
    <td>${spell.level}</td>
    <td>${spell.school}</td>
    <td>
      <button class="btn btn-primary btn-export" onclick="downloadPdf('${escapedName}', '${escapedSource}')">PDF</button>
      ${actionButton}
    </td>
  `;
}

function _renderSpellTable(tbodyId, tableId, spells, isSelected) {
  const tbody = document.getElementById(tbodyId);
  const table = document.getElementById(tableId);

  if (!tbody || !table) return;

  tbody.innerHTML = "";

  spells.forEach((spell) => {
    const row = document.createElement("tr");
    row.innerHTML = _createSpellRowHtml(spell, isSelected);
    row.dataset.classes = JSON.stringify(spell.classes || []);
    tbody.appendChild(row);
  });

  table.style.display = "table";
}

function updateSelectedSpells(spells) {
  _renderSpellTable("selected-table-list", "selected-table", spells, true);
  getSpells();
}

function getSpells() {
  window.pywebview.api.fetch().then((spells) => {
    _renderSpellTable("spells-table-list", "spells-table", spells, false);
    filterSpells();
  });
}

function filterSpells() {
  const query = document.getElementById("spell-search")?.value.toLowerCase() || "";
  const rows = document.querySelectorAll("#spells-table-list tr");

  rows.forEach((row) => {
    const spellName = row.cells[0].textContent.toLowerCase();
    const matchesSearch = spellName.includes(query);

    const spellClasses = JSON.parse(row.dataset.classes || "[]");
    const matchesClass =
      selectedClassFilters.size === 0 || spellClasses.some((c) => selectedClassFilters.has(`${c.name} (${c.source})`));

    const spellLevel = row.cells[2].textContent;
    const matchesLevel = selectedLevelFilters.size === 0 || selectedLevelFilters.has(spellLevel);

    const spellSchool = row.cells[3].textContent.toLowerCase();
    const matchesSchool = selectedSchoolFilters.size === 0 || selectedSchoolFilters.has(spellSchool);

    row.style.display = matchesSearch && matchesClass && matchesLevel && matchesSchool ? "" : "none";
  });
}

function _createMultiSelectDropdown({ containerId, defaultText, items, getValue, getLabel, trackingSet }) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = "";

  const headerBtn = document.createElement("button");
  headerBtn.className = "dropdown-header";
  headerBtn.textContent = defaultText;

  const contentDiv = document.createElement("div");
  contentDiv.className = "dropdown-content";

  contentDiv.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // Toggle visibility when clicking the header
  headerBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    document.querySelectorAll(".dropdown-container").forEach((c) => {
      if (c !== container) c.classList.remove("active");
    });
    container.classList.toggle("active");
  });

  items.forEach((item) => {
    const val = getValue(item);
    const labelText = getLabel(item);

    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = val;

    checkbox.addEventListener("change", (e) => {
      if (e.target.checked) {
        trackingSet.add(val);
      } else {
        trackingSet.delete(val);
      }

      if (trackingSet.size === 0) {
        headerBtn.textContent = defaultText;
      } else if (trackingSet.size <= 2) {
        headerBtn.textContent = Array.from(trackingSet).join(", ");
      } else {
        headerBtn.textContent = `${trackingSet.size} Selected`;
      }

      filterSpells();
    });

    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(" " + labelText));
    contentDiv.appendChild(label);
  });

  container.appendChild(headerBtn);
  container.appendChild(contentDiv);
}

// Close the dropdown menus if clicking outside of them entirely
document.addEventListener("click", () => {
  document.querySelectorAll(".dropdown-container").forEach((c) => c.classList.remove("active"));
});

function exportAll() {
  window.pywebview.api.export_selected_to_pdf().then(alert);
}

function downloadPdf(name, source) {
  window.pywebview.api.export_pdf(name, source).then(alert);
}

function selectSpell(name, source) {
  window.pywebview.api.select(name, source).then(updateSelectedSpells);
}

function deselectSpell(name, source) {
  window.pywebview.api.deselect(name, source).then(updateSelectedSpells);
}

window.addEventListener("pywebviewready", () => {
  window.pywebview.api.get_filter_options().then((options) => {
    filterOptions = options;
    if (!filterOptions) return;

    if (filterOptions.classes) {
      const sortedClasses = [...filterOptions.classes].sort((a, b) => a.name.localeCompare(b.name));
      _createMultiSelectDropdown({
        containerId: "class-filter-container",
        defaultText: "All Classes",
        items: sortedClasses,
        getValue: (c) => `${c.name} (${c.source})`,
        getLabel: (c) => `${c.name} (${c.source})`,
        trackingSet: selectedClassFilters,
      });
    }

    if (filterOptions.schools) {
      _createMultiSelectDropdown({
        containerId: "school-filter-container",
        defaultText: "All Schools",
        items: filterOptions.schools,
        getValue: (s) => s.toLowerCase(),
        getLabel: (s) => s.charAt(0).toUpperCase() + s.slice(1),
        trackingSet: selectedSchoolFilters,
      });
    }

    if (filterOptions.levels) {
      _createMultiSelectDropdown({
        containerId: "level-filter-container",
        defaultText: "All Levels",
        items: filterOptions.levels,
        getValue: (l) => l,
        getLabel: (l) => l,
        trackingSet: selectedLevelFilters,
      });
    }
  });
  getSpells();
});
