let filterOptions = {};
let selectedClassFilter = "all";
let selectedSchoolFilter = "all";
let selectedLevelFilter = "all";

function _createSpellRowHtml(spell, isSelected) {
  const nameHtml = spell.url
    ? `<a href="${spell.url}" target="_blank" rel="noopener noreferrer">${spell.name}</a>`
    : spell.name;

  const escapedName = spell.name.replace(/'/g, "\\'");
  const escapedSource = spell.source.replace(/'/g, "\\'");

  const actionButton = isSelected
    ? `<button class="btn-sub" onClick="deselectSpell('${escapedName}', '${escapedSource}')">-</button>`
    : `<button class="btn-add" onClick="selectSpell('${escapedName}', '${escapedSource}')">+</button>`;

  return `
    <td>${nameHtml}</td>
    <td>${spell.source}</td>
    <td>${spell.level}</td>
    <td>${spell.school}</td>
    <td>
      <button class="btn-pdf" onclick="downloadPdf('${escapedName}', '${escapedSource}')">PDF</button>
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
      selectedClassFilter === "all" ||
      spellClasses.some((c) => {
        const uniqueClassKey = `${c.name} (${c.source})`;
        return uniqueClassKey === selectedClassFilter;
      });

    const spellLevel = row.cells[2].textContent;
    const matchesLevel = selectedLevelFilter === "all" || spellLevel === selectedLevelFilter;

    const spellSchool = row.cells[3].textContent.toLowerCase();
    const matchesSchool = selectedSchoolFilter === "all" || spellSchool === selectedSchoolFilter;
    
    row.style.display = matchesSearch && matchesClass && matchesLevel && matchesSchool ? "" : "none";
  });
}

function _createDropdown({ containerId, defaultText, items, getValue, getLabel, onChange }) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const select = document.createElement("select");
  select.innerHTML = `<option value="all">${defaultText}</option>`;

  items.forEach((item) => {
    const option = document.createElement("option");
    option.value = getValue(item);
    option.textContent = getLabel(item);
    select.appendChild(option);
  });

  select.addEventListener("change", (e) => {
    onChange(e.target.value);
    filterSpells();
  });

  container.innerHTML = "";
  container.appendChild(select);
}

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
      _createDropdown({
        containerId: "class-filter-container",
        defaultText: "All Classes",
        items: sortedClasses,
        getValue: (c) => `${c.name} (${c.source})`,
        getLabel: (c) => `${c.name} (${c.source})`,
        onChange: (val) => {
          selectedClassFilter = val;
        },
      });
    }

    if (filterOptions.schools) {
      _createDropdown({
        containerId: "school-filter-container",
        defaultText: "All Schools",
        items: filterOptions.schools,
        getValue: (s) => s,
        getLabel: (s) => s.charAt(0).toUpperCase() + s.slice(1),
        onChange: (val) => {
          selectedSchoolFilter = val;
        },
      });
    }

    if (filterOptions.levels) {
      _createDropdown({
        containerId: "level-filter-container",
        defaultText: "All Levels",
        items: filterOptions.levels,
        getValue: (l) => l,
        getLabel: (l) => l,
        onChange: (val) => {
          selectedLevelFilter = val;
        },
      });
    }
  });
  getSpells();
});
