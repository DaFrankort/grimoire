function updateSelectedSpells(spells) {
  const tbody = document.getElementById("selected-table-list");
  const table = document.getElementById("selected-table");
  tbody.innerHTML = "";

  spells.forEach((spell) => {
    const row = document.createElement("tr");
    let nameHtml = spell.name;
    const escapedName = spell.name.replace(/'/g, "\\'");
    if (spell.url) nameHtml = `<a href="${spell.url}" target="_blank" rel="noopener noreferrer">${spell.name}</a>`;
    row.innerHTML = `
                          <td>${nameHtml}</td>
                          <td>${spell.source}</td>
                          <td>${spell.level}</td>
                          <td>${spell.school}</td>
                          <td>
                              <button class="btn-pdf" onclick="downloadPdf('${escapedName}', '${spell.source}')">PDF</button>
                              <button class="btn-sub" onClick="deselectSpell('${escapedName}', '${spell.source}')">-</button>
                          </td>
                      `;
    tbody.appendChild(row);
  });
  table.style.display = "table";
  getSpells();
}

function exportAll() {
  window.pywebview.api.export_selected_to_pdf().then((message) => {
    alert(message);
  });
}

function downloadPdf(name, source) {
  window.pywebview.api.export_pdf(name, source).then((message) => {
    alert(message);
  });
}

function selectSpell(name, source) {
  window.pywebview.api.select(name, source).then((selected) => {
    updateSelectedSpells(selected);
  });
}

function deselectSpell(name, source) {
  window.pywebview.api.deselect(name, source).then((selected) => {
    updateSelectedSpells(selected);
  });
}

function getSpells() {
  const tbody = document.getElementById("spells-table-list");
  const table = document.getElementById("spells-table");

  tbody.innerHTML = "";
  window.pywebview.api.fetch().then((spells) => {
    spells.forEach((spell) => {
      const row = document.createElement("tr");
      let nameHtml = spell.name;
      const escapedName = spell.name.replace(/'/g, "\\'");
      if (spell.url) nameHtml = `<a href="${spell.url}" target="_blank" rel="noopener noreferrer">${spell.name}</a>`;
      row.innerHTML = `
                            <td>${nameHtml}</td>
                            <td>${spell.source}</td>
                            <td>${spell.level}</td>
                            <td>${spell.school}</td>
                            <td>
                                <button class="btn-pdf" onclick="downloadPdf('${escapedName}', '${spell.source}')">PDF</button>
                                <button class="btn-add" onClick="selectSpell('${escapedName}', '${spell.source}')">+</button>
                            </td>
                        `;
      tbody.appendChild(row);
    });
    table.style.display = "table";
    filterSpells();
  });
}

function filterSpells() {
  const query = document.getElementById("spell-search").value.toLowerCase();
  const rows = document.querySelectorAll("#spells-table-list tr");

  rows.forEach((row) => {
    const spellName = row.cells[0].textContent.toLowerCase();
    if (spellName.includes(query)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}

window.addEventListener("pywebviewready", () => {
  getSpells();
});
