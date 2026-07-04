let currentData = [];

// DOM Elements
const tableTypeSelect = document.getElementById("table-type");
const skillGroup = document.getElementById("skill-group");
const skillSelect = document.getElementById("skill-select");
const pillarGroup = document.getElementById("pillar-group");
const pillarSelect = document.getElementById("pillar-select");
const seasonSelect = document.getElementById("season-select");
const minMinutesSlider = document.getElementById("min-minutes");
const minMinutesVal = document.getElementById("min-minutes-val");
const extraInfoToggle = document.getElementById("extra-info-toggle");
const extraInfoLabel = document.getElementById("extra-info-label");
const updateBtn = document.getElementById("update-btn");
const loadingOverlay = document.getElementById("loading");
const emptyState = document.getElementById("empty-state");
const tableHeadRow = document.getElementById("table-head-row");
const tableFilterRow = document.getElementById("table-filter-row");
const tableBody = document.getElementById("table-body");
const leaderboardTable = document.getElementById("leaderboard-table");


async function init() {
    // Event Listeners
    tableTypeSelect.addEventListener("change", () =>
        updateDropdownVisibilities({
            tableTypeSelect,
            skillGroup,
            pillarGroup
        })
    );

    skillSelect.addEventListener("change", () =>
        populatePillars({
            skillSelect,
            pillarSelect
        })
    );

    minMinutesSlider.addEventListener("input", (e) => {
        minMinutesVal.textContent = e.target.value;
    });

    extraInfoToggle.addEventListener("change", () => {
        extraInfoLabel.textContent =
            extraInfoToggle.checked ? "On" : "Off";
    });

    updateBtn.addEventListener("click", fetchAndRender);

    // Initial setup
    await loadMetadata();
    seasonOptions({seasonSelect});
    updateDropdownVisibilities({
        tableTypeSelect,
        skillGroup,
        pillarGroup
    });
    populatePillars({
        skillSelect,
        pillarSelect
    })
    await fetchAndRender();
}


async function fetchAndRender() {
    loadingOverlay.style.display = "flex";
    emptyState.style.display = "none";
    leaderboardTable.style.display = "table";

    try {
        const data = await fetchLeaderboard({
            type: tableTypeSelect.value,
            season: seasonSelect.value,
            min: minMinutesSlider.value,
            skill: skillSelect.value,
            pillar: pillarSelect.value,
            detailed: extraInfoToggle.checked
        });

        currentData = data;

        if (currentData.length === 0) {
            leaderboardTable.style.display = "none";
            emptyState.style.display = "block";
            return;
        }

        updateTable(currentData, tableHeadRow, tableFilterRow, tableBody);

    } catch (err) {
        console.error(err);

        leaderboardTable.style.display = "none";
        emptyState.style.display = "block";
        emptyState.innerHTML =
            "<p>Error loading data. Make sure the backend is running.</p>";
    } finally {
        loadingOverlay.style.display = "none";
    }
}


document.addEventListener("DOMContentLoaded", init);





//let currentData = [];
//let sortState = { column: null, asc: false };
//let filters = {
//    PLAYER_NAME: "",
//    TEAM: ""
//};

//// DOM Elements
//const tableTypeSelect = document.getElementById("table-type");
//const skillGroup = document.getElementById("skill-group");
//const skillSelect = document.getElementById("skill-select");
//const pillarGroup = document.getElementById("pillar-group");
//const pillarSelect = document.getElementById("pillar-select");
//const seasonSelect = document.getElementById("season-select");
//const minMinutesSlider = document.getElementById("min-minutes");
//const minMinutesVal = document.getElementById("min-minutes-val");
//const extraInfoToggle = document.getElementById("extra-info-toggle");
//const extraInfoLabel = document.getElementById("extra-info-label");
//const updateBtn = document.getElementById("update-btn");
//const loadingOverlay = document.getElementById("loading");
//const emptyState = document.getElementById("empty-state");
//const tableHeadRow = document.getElementById("table-head-row");
//const tableFilterRow = document.getElementById("table-filter-row");
//const tableBody = document.getElementById("table-body");
//const leaderboardTable = document.getElementById("leaderboard-table");

//// Initialization
//async function init() {
//    // Event Listeners
//    tableTypeSelect.addEventListener("change", updateDropdownVisibilities);
//    skillSelect.addEventListener("change", populatePillars);
//    minMinutesSlider.addEventListener("input", (e) => {
//        minMinutesVal.textContent = e.target.value;
//    });
//    extraInfoToggle.addEventListener("change", () => {
//        extraInfoLabel.textContent =
//            extraInfoToggle.checked ? "On" : "Off";
//    });
//    updateBtn.addEventListener("click", fetchAndRenderData);
//
//    // Initial setup
//    await loadMetadata();
//    seasonOptions();
//    updateDropdownVisibilities();
//    populatePillars();
//    await fetchAndRenderData();
//}

//function seasonOptions() {
//    const startYear = 2018;
//    const endYear = 2026;
//
//    for (let year = endYear; year >= startYear; year--) {
//        const option = document.createElement("option");
//
//        option.value = year;
//        option.textContent = `${year-1}-${String(year).slice(-2)}`;
//
//        if (year === endYear) {
//            option.selected = true;
//        }
//
//        seasonSelect.appendChild(option);
//    }
//}
//
//function updateDropdownVisibilities() {
//    const type = tableTypeSelect.value;
//    if (type === "overall") {
//        skillGroup.style.display = "none";
//        pillarGroup.style.display = "none";
//    } else if (type === "skill") {
//        skillGroup.style.display = "flex";
//        pillarGroup.style.display = "none";
//    } else if (type === "pillar") {
//        skillGroup.style.display = "flex";
//        pillarGroup.style.display = "flex";
//    }
//}
//
//function populatePillars() {
//    const skill = skillSelect.value;
//    const pillars = pillarMappings[skill] || [];
//    pillarSelect.innerHTML = "";
//    pillars.forEach(p => {
//        const opt = document.createElement("option");
//        opt.value = p;
//        opt.textContent = p;
//        pillarSelect.appendChild(opt);
//    });
//}

//async function fetchAndRenderData() {
//    loadingOverlay.style.display = "flex";
//    emptyState.style.display = "none";
//    leaderboardTable.style.display = "table";
//
//    const type = tableTypeSelect.value;
//    const season = seasonSelect.value;
//    const min = minMinutesSlider.value;
//    const skill = skillSelect.value;
//    const pillar = pillarSelect.value;
//    const extraInfo = extraInfoToggle.checked;
//
//    let url = "";
//    if (type === "overall") {
//        url = `${API_BASE}/leaderboard/overall?season=${season}&minimum=${min}&detailed=${extraInfo}`;
//    } else if (type === "skill") {
//        url = `${API_BASE}/leaderboard/skill/${skill}?season=${season}&minimum=${min}&detailed=${extraInfo}`;
//    } else if (type === "pillar") {
//        url = `${API_BASE}/leaderboard/pillar/${skill}/${pillar}?season=${season}&minimum=${min}&detailed=${extraInfo}`;
//    }
//
//    try {
//        const response = await fetch(url);
//        if (!response.ok) throw new Error("Network response was not ok");
//        const data = await response.json();
//
//        currentData = data;
//
//        if (currentData.length === 0) {
//            leaderboardTable.style.display = "none";
//            emptyState.style.display = "block";
//        } else {
//            // Default sort by the most relevant column if not set
//            if (!sortState.column) {
//                const cols = Object.keys(currentData[0]).filter(c => !ignoredColumns.includes(c) && !nonPctColumns.includes(c));
//                sortState.column = cols[cols.length - 1] || "MIN"; // Usually the last column is the rating/target
//                sortState.asc = false;
//            }
//
//            computePercentiles();
//            // getFilteredData();
//            sortData();
//            renderTable();
//        }
//    } catch (error) {
//        console.error("Error fetching data:", error);
//        leaderboardTable.style.display = "none";
//        emptyState.style.display = "block";
//        emptyState.innerHTML = `<p>Error loading data. Make sure the backend is running.</p>`;
//    } finally {
//        loadingOverlay.style.display = "none";
//    }
//}


//function computePercentiles() {
//    if (currentData.length === 0) return;
//
//    const columns = Object.keys(currentData[0]);
//    const numRows = currentData.length;
//
//    columns.forEach(col => {
//        if (ignoredColumns.includes(col) || nonPctColumns.includes(col)) return;
//
//        // Extract values and sort
//        const meta = getMeta(col)
//        const values = currentData.map(row => row[col]).filter(v => v !== null && v !== undefined);
//        values.sort((a, b) => a - b);
//
//        currentData.forEach(row => {
//            const val = row[col];
//            if (val === null || val === undefined) {
//                row[`${col}_pct`] = null;
//                return;
//            }
//            // Find index to calculate percentile
//            const idx = values.findIndex(v => v >= val);
//            const pct = (idx / Math.max(1, values.length - 1)) * 100;
//            if (meta.higher_is_better) {
//                row[`${col}_pct`] = pct;
//            } else {
//                row[`${col}_pct`] = 100 - pct;
//            }
//        });
//    });
//}

//function sortData() {
//    if (!sortState.column) return;
//    const col = sortState.column;
//    const asc = sortState.asc ? 1 : -1;
//
//    currentData.sort((a, b) => {
//        let valA = a[col];
//        let valB = b[col];
//
//        if (valA === null || valA === undefined) valA = -Infinity;
//        if (valB === null || valB === undefined) valB = -Infinity;
//
//        if (valA < valB) return -1 * asc;
//        if (valA > valB) return 1 * asc;
//        return 0;
//    });
//}
//
//function handleSort(col) {
//    if (sortState.column === col) {
//        sortState.asc = !sortState.asc;
//    } else {
//        sortState.column = col;
//        if (nonPctColumns.includes(sortState.column)) {
//            sortState.asc = true;
//        } else {
//            sortState.asc = false;
//        }
//    }
//    sortData();
//    renderTable();
//}
//
//function getColorFromPercentile(col, pct) {
//    const meta = getMeta(col);
//
//    if (pct === null || pct === undefined) return "transparent";
//
//    let adjustedPct = pct;
//
//    const hue = (adjustedPct / 100) * 120;
//    return `hsla(${hue}, 70%, 40%, 0.6)`;
//}
//
//function getFilteredData() {
//    return currentData.filter(row => {
//        if (
//            filters.PLAYER_NAME &&
//            !row.PLAYER_NAME.toLowerCase().includes(filters.PLAYER_NAME)
//        ) {
//            return false;
//        }
//
//        if (
//            filters.TEAM &&
//            !row.TEAM.toLowerCase().includes(filters.TEAM)
//        ) {
//            return false;
//        }
//
//        return true;
//    });
//}
//
//
//function renderTable() {
//    renderHeaders();
//    renderBody();
//}
//
//
//function renderHeaders() {
//    if (currentData.length === 0) return;
//
//    const columns = Object.keys(currentData[0]).filter(c => !ignoredColumns.includes(c) && !c.endsWith("_pct"));
//
//    // Render Head
//    tableHeadRow.innerHTML = "";
//    columns.forEach(col => {
//        const meta = getMeta(col);
//        const th = document.createElement("th");
//        th.textContent = meta.display_name || col.replace(/_/g, " ");
//        if (meta.description) {
//            th.dataset.tooltip = meta.description;
//        }
//        // th.title = meta.description || "";
//
//        if (sortState.column === col) {
//            th.classList.add(sortState.asc ? "sorted-asc" : "sorted-desc");
//            th.innerHTML += `<span class="sort-icon">${sortState.asc ? "▲" : "▼"}</span>`;
//        }
//
//        th.addEventListener("click", () => handleSort(col));
//        tableHeadRow.appendChild(th);
//    });
//
//    // Render Filters
//    tableFilterRow.innerHTML = "";
//    columns.forEach(col => {
//        const th = document.createElement("th");
//        if (filterableColumns.includes(col)) {
//            const input = document.createElement("input");
//            input.type = "text";
//            input.placeholder = "Search...";
//            input.value = filters[col];
//            input.addEventListener("input", (e) => {
//                filters[col] = e.target.value.toLowerCase();
//                renderBody();
//            });
//            th.appendChild(input);
//        }
//        tableFilterRow.appendChild(th);
//    });
//}
//
//function renderBody() {
//    if (currentData.length === 0) return;
//    // Render Body
//    const columns = Object.keys(currentData[0]).filter(c => !ignoredColumns.includes(c) && !c.endsWith("_pct"));
//    const rows = getFilteredData();
//    tableBody.innerHTML = "";
//    rows.forEach(row => {
//        const tr = document.createElement("tr");
//
//        columns.forEach(col => {
//            const meta = getMeta(col);
//            const td = document.createElement("td");
//
//            if (col == "PLAYER_NAME") {
//                td.innerHTML = `
//                    <a class="player-link" href="player.html?player_id=${row.PLAYER_ID}">
//                        ${row.PLAYER_NAME}
//                    </a>
//                `;
//                tr.appendChild(td);
//                return;
//            }
//
//            let val = row[col];
//
//            if (val === null || val === undefined) {
//                td.textContent = "-";
//                tr.appendChild(td);
//                return;
//            }
//
//            const pct = row[`${col}_pct`];
//            const formattedVal = formatValue(col, val);
//
//            td.innerHTML = `
//                <div class="val-cell" style="background-color: ${getColorFromPercentile(col, pct)}; padding: 0.25rem 0.5rem;">
//                    <span class="val-raw">${formattedVal}</span>
//                    <span class="val-pct">${pct != null ? pct.toFixed(1) + '%' : ''}</span>
//                </div>
//            `;
//
//            tr.appendChild(td)
//        });
//
//        tableBody.appendChild(tr);
//    });
//}

//// Start app
//document.addEventListener("DOMContentLoaded", init);
