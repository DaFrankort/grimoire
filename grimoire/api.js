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
    row.style.display = spellName.includes(query) ? "" : "none";
  });
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

window.addEventListener("pywebviewready", getSpells);
