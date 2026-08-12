let tableState = {
    data: [],
    filters: {},
    sort: { column: null, asc: false },
    metadata: {},
    elements: null
};

function setTableState(newState) {
    tableState = { ...tableState, ...newState };
}

function getFilteredData() {
    return tableState.data.filter(row => {
        for (const key in tableState.filters) {
            const val = tableState.filters[key];
            if (!val) continue;

            if (!row[key]?.toLowerCase?.().includes(val)) {
                return false;
            }
        }
        return true;
    });
}

function sortData() {
    if (!tableState.sort.column) return;
    const col = tableState.sort.column;
    const asc = tableState.sort.asc ? 1 : -1;

    tableState.data.sort((a, b) => {
        let valA = a[col];
        let valB = b[col];

        if (valA === null || valA === undefined) valA = -Infinity;
        if (valB === null || valB === undefined) valB = -Infinity;

        if (valA < valB) return -1 * asc;
        if (valA > valB) return 1 * asc;
        return 0;
    });
}

function handleSort(col) {
    if (tableState.sort.column === col) {
        tableState.sort.asc = !tableState.sort.asc;
    } else {
        tableState.sort.column = col;
        if (nonPctColumns.includes(tableState.sort.column)) {
            tableState.sort.asc = true;
        } else {
            tableState.sort.asc = false;
        }
    }
    sortData();
    renderBody(tableState.elements);
}

function getColorFromPercentile(col, pct) {
    const meta = getMeta(col);

    if (pct === null || pct === undefined) return "transparent";

    let adjustedPct = pct;

    const hue = (adjustedPct / 100) * 120;
    return `hsla(${hue}, 70%, 40%, 0.6)`;
}


function renderTable(elements) {
    sortData();
    renderHeaders(elements);
    renderBody(elements);
}


function renderHeaders({ tableHeadRow, tableFilterRow, tableBody }) {

    const columns = Object.keys(tableState.data[0] || {})
        .filter(c => !ignoredColumns.includes(c) && !c.endsWith("_pct"));

    tableHeadRow.innerHTML = "";
    tableFilterRow.innerHTML = "";

    columns.forEach(col => {

        const meta = getMeta(col);

        const th = document.createElement("th");
        th.textContent = meta.display_name || col;

        if (meta.description) {
            th.dataset.tooltip = meta.description;
        }

        th.addEventListener("click", () => handleSort(col));

        tableHeadRow.appendChild(th);

        // filter row
        const filterTh = document.createElement("th");

        if (filterableColumns.includes(col)) {
            const input = document.createElement("input");
            input.value = tableState.filters[col] || "";

            input.addEventListener("input", (e) => {
                tableState.filters[col] = e.target.value.toLowerCase();
                renderBody({ tableBody });
            });

            filterTh.appendChild(input);
        }

        tableFilterRow.appendChild(filterTh);
    });
}


function renderBody({ tableBody }) {

    const rows = getFilteredData();
    const columns = Object.keys(tableState.data[0] || {})
        .filter(c => !ignoredColumns.includes(c) && !c.endsWith("_pct"));

    tableBody.innerHTML = "";

    rows.forEach(row => {
        const tr = document.createElement("tr");

        columns.forEach(col => {
            const td = document.createElement("td");

            if (col === "PLAYER_NAME") {
                const link = document.createElement("a");
                link.className = "player-link identity-link";
                link.href = `player.html?player_id=${row.PLAYER_ID}`;
                const image = document.createElement("img");
                image.className = "table-headshot";
                image.src = playerHeadshotUrl(row.PLAYER_ID);
                image.alt = "";
                image.addEventListener("error", () => hideMissingImage(image), { once: true });
                const name = document.createElement("span");
                name.textContent = row.PLAYER_NAME;
                link.append(image, name);
                td.appendChild(link);
                tr.appendChild(td);
                return;
            }

            if (col == "TEAM") {
                const link = document.createElement("a");
                link.className = "player-link identity-link team-link";
                link.href = `team.html?team_id=${row.TEAM_ID}`;
                const image = document.createElement("img");
                image.className = "table-team-logo";
                image.src = teamLogoUrl(row.TEAM_ID);
                image.alt = "";
                image.addEventListener("error", () => hideMissingImage(image), { once: true });
                const abbreviation = document.createElement("span");
                abbreviation.textContent = row.TEAM;
                link.append(image, abbreviation);
                td.appendChild(link);
                tr.appendChild(td);
                return;
            }

            const val = row[col];
            if (val == null) {
                td.textContent = "-";
                tr.appendChild(td);
                return;
            }

            const pct = row[`${col}_pct`];
            const formattedVal = formatValue(col, val);

            td.innerHTML = `
                <div class="val-cell" style="background-color: ${getColorFromPercentile(col, pct)}; padding: 0.25rem 0.5rem;">
                    <span class="val-raw">${formattedVal}</span>
                    <span class="val-pct">${pct != null ? pct.toFixed(1) + '%' : ''}</span>
                </div>
            `;

            tr.appendChild(td);
        });

        tableBody.appendChild(tr);
    });
}


function updateTable(currentData, tableHeadRow, tableFilterRow, tableBody) {
    setTableState({
        data: currentData,
        elements: {
            tableHeadRow,
            tableFilterRow,
            tableBody
        }
    });

    renderTable({
        tableHeadRow,
        tableFilterRow,
        tableBody
    });
}
