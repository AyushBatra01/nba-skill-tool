const API_BASE = "http://127.0.0.1:8000";

const pillarMappings = {
    "Creation": ["Scoring", "Playmaking", "DualThreat", "Pressure"],
    "OffBall": ["Shooting", "Spacing", "Interior"],
    "Defense": ["Disruption", "RimProtection", "Assignment", "Versatility"],
    "Physicality": ["RimForce", "Explosiveness", "Rebounding", "Motor"]
};

const ignoredColumns = ["PLAYER_ID", "TEAM_ID", "SEASON"];
const nonPctColumns = ["PLAYER_NAME", "TEAM", "MIN"];

let currentData = [];
let sortState = { column: null, asc: false };

// DOM Elements
const tableTypeSelect = document.getElementById("table-type");
const skillGroup = document.getElementById("skill-group");
const skillSelect = document.getElementById("skill-select");
const pillarGroup = document.getElementById("pillar-group");
const pillarSelect = document.getElementById("pillar-select");
const seasonSelect = document.getElementById("season-select");
const minMinutesSlider = document.getElementById("min-minutes");
const minMinutesVal = document.getElementById("min-minutes-val");
const updateBtn = document.getElementById("update-btn");
const loadingOverlay = document.getElementById("loading");
const emptyState = document.getElementById("empty-state");
const tableHeadRow = document.getElementById("table-head-row");
const tableBody = document.getElementById("table-body");
const leaderboardTable = document.getElementById("leaderboard-table");

// Initialization
function init() {
    // Event Listeners
    tableTypeSelect.addEventListener("change", updateDropdownVisibilities);
    skillSelect.addEventListener("change", populatePillars);
    minMinutesSlider.addEventListener("input", (e) => {
        minMinutesVal.textContent = e.target.value;
    });
    updateBtn.addEventListener("click", fetchAndRenderData);

    // Initial setup
    updateDropdownVisibilities();
    populatePillars();
    fetchAndRenderData();
}

function updateDropdownVisibilities() {
    const type = tableTypeSelect.value;
    if (type === "overall") {
        skillGroup.style.display = "none";
        pillarGroup.style.display = "none";
    } else if (type === "skill") {
        skillGroup.style.display = "flex";
        pillarGroup.style.display = "none";
    } else if (type === "pillar") {
        skillGroup.style.display = "flex";
        pillarGroup.style.display = "flex";
    }
}

function populatePillars() {
    const skill = skillSelect.value;
    const pillars = pillarMappings[skill] || [];
    pillarSelect.innerHTML = "";
    pillars.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p;
        opt.textContent = p;
        pillarSelect.appendChild(opt);
    });
}

async function fetchAndRenderData() {
    loadingOverlay.style.display = "flex";
    emptyState.style.display = "none";
    leaderboardTable.style.display = "table";
    
    const type = tableTypeSelect.value;
    const season = seasonSelect.value;
    const min = minMinutesSlider.value;
    const skill = skillSelect.value;
    const pillar = pillarSelect.value;

    let url = "";
    if (type === "overall") {
        url = `${API_BASE}/leaderboard/overall?season=${season}&minimum=${min}`;
    } else if (type === "skill") {
        url = `${API_BASE}/leaderboard/skill/${skill}?season=${season}&minimum=${min}`;
    } else if (type === "pillar") {
        url = `${API_BASE}/leaderboard/pillar/${skill}/${pillar}?season=${season}&minimum=${min}`;
    }

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        
        currentData = data;
        
        if (currentData.length === 0) {
            leaderboardTable.style.display = "none";
            emptyState.style.display = "block";
        } else {
            // Default sort by the most relevant column if not set
            if (!sortState.column) {
                const cols = Object.keys(currentData[0]).filter(c => !ignoredColumns.includes(c) && !nonPctColumns.includes(c));
                sortState.column = cols[cols.length - 1] || "MIN"; // Usually the last column is the rating/target
                sortState.asc = false;
            }
            
            computePercentiles();
            sortData();
            renderTable();
        }
    } catch (error) {
        console.error("Error fetching data:", error);
        leaderboardTable.style.display = "none";
        emptyState.style.display = "block";
        emptyState.innerHTML = `<p>Error loading data. Make sure the backend is running.</p>`;
    } finally {
        loadingOverlay.style.display = "none";
    }
}

function computePercentiles() {
    if (currentData.length === 0) return;
    
    const columns = Object.keys(currentData[0]);
    const numRows = currentData.length;

    columns.forEach(col => {
        if (ignoredColumns.includes(col) || nonPctColumns.includes(col)) return;
        
        // Extract values and sort
        const values = currentData.map(row => row[col]).filter(v => v !== null && v !== undefined);
        values.sort((a, b) => a - b);
        
        currentData.forEach(row => {
            const val = row[col];
            if (val === null || val === undefined) {
                row[`${col}_pct`] = null;
                return;
            }
            // Find index to calculate percentile
            const idx = values.findIndex(v => v >= val);
            const pct = (idx / Math.max(1, values.length - 1)) * 100;
            row[`${col}_pct`] = pct;
        });
    });
}

function sortData() {
    if (!sortState.column) return;
    const col = sortState.column;
    const asc = sortState.asc ? 1 : -1;

    currentData.sort((a, b) => {
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
    if (sortState.column === col) {
        sortState.asc = !sortState.asc;
    } else {
        sortState.column = col;
        sortState.asc = false;
    }
    sortData();
    renderTable();
}

function getBgColorForPercentile(pct) {
    if (pct === null || pct === undefined) return "transparent";
    // Color scale: Red (0) -> Yellow (50) -> Green (100)
    // HSL Hue: 0 is Red, 60 is Yellow, 120 is Green
    const hue = (pct / 100) * 120;
    return `hsla(${hue}, 70%, 40%, 0.6)`;
}

function renderTable() {
    if (currentData.length === 0) return;

    const columns = Object.keys(currentData[0]).filter(c => !ignoredColumns.includes(c) && !c.endsWith("_pct"));
    
    // Render Head
    tableHeadRow.innerHTML = "";
    columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col.replace(/_/g, " ");
        
        if (sortState.column === col) {
            th.classList.add(sortState.asc ? "sorted-asc" : "sorted-desc");
            th.innerHTML += `<span class="sort-icon">${sortState.asc ? "▲" : "▼"}</span>`;
        }
        
        th.addEventListener("click", () => handleSort(col));
        tableHeadRow.appendChild(th);
    });

    // Render Body
    tableBody.innerHTML = "";
    currentData.forEach(row => {
        const tr = document.createElement("tr");
        
        columns.forEach(col => {
            const td = document.createElement("td");
            let val = row[col];
            
            if (val === null || val === undefined) {
                td.textContent = "-";
                tr.appendChild(td);
                return;
            }

            if (nonPctColumns.includes(col)) {
                td.textContent = typeof val === 'number' ? val.toLocaleString(undefined, {maximumFractionDigits: 1}) : val;
            } else {
                // Is a percentage/value column
                const pct = row[`${col}_pct`];
                const formattedVal = typeof val === 'number' ? val.toFixed(2) : val;
                
                td.innerHTML = `
                    <div class="val-cell" style="background-color: ${getBgColorForPercentile(pct)}; padding: 0.25rem 0.5rem;">
                        <span class="val-raw">${formattedVal}</span>
                        <span class="val-pct">${pct !== null ? pct.toFixed(1) + '%' : ''}</span>
                    </div>
                `;
            }
            tr.appendChild(td);
        });
        
        tableBody.appendChild(tr);
    });
}

// Start app
document.addEventListener("DOMContentLoaded", init);
