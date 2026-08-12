let currentData = [];

const params = new URLSearchParams(window.location.search);

// Get player ID
const playerId = Number(params.get("player_id"));

// DOM Elements
const playerName = document.getElementById("player-name");
const playerHeadshot = document.getElementById("player-headshot");
const playerHeight = document.getElementById("player-height");
const playerWeight = document.getElementById("player-weight");
const playerExp = document.getElementById("player-exp");
const playerCollege = document.getElementById("player-college");
const playerDraft = document.getElementById("player-draft");
const playerTeam = document.getElementById("player-team");

const tableTypeSelect = document.getElementById("table-type");
const skillGroup = document.getElementById("skill-group");
const skillSelect = document.getElementById("skill-select");
const pillarGroup = document.getElementById("pillar-group");
const pillarSelect = document.getElementById("pillar-select");
const minMinutesSlider = document.getElementById("min-minutes");
const minMinutesVal = document.getElementById("min-minutes-val");
const updateBtn = document.getElementById("update-btn");
const loadingOverlay = document.getElementById("loading");
const emptyState = document.getElementById("empty-state");
const tableHeadRow = document.getElementById("table-head-row");
const tableFilterRow = document.getElementById("table-filter-row");
const tableBody = document.getElementById("table-body");
const playerTable = document.getElementById("player-table");




async function init() {
    if (!Number.isInteger(playerId) || playerId <= 0) {
        playerName.textContent = "Player not found";
        return;
    }
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

    updateBtn.addEventListener("click", fetchAndRender);

    // Initial Setup
    await loadMetadata();
    await updateInfo();
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


async function updateInfo() {
    try {
        const data = await fetchPlayerInfo(playerId);

        playerName.textContent = `${data["FIRST_NAME"]} ${data["LAST_NAME"]}`;
        playerHeadshot.src = playerHeadshotUrl(playerId);
        playerHeadshot.alt = `${playerName.textContent} headshot`;
        playerHeadshot.hidden = false;
        playerHeadshot.addEventListener("error", () => hideMissingImage(playerHeadshot), { once: true });
        playerHeight.textContent = data["HEIGHT"];
        playerWeight.textContent = `${data["WEIGHT"]} lbs`;
        playerExp.textContent = `${data["TO_YEAR"] - data["FROM_YEAR"]} seasons`;
        playerCollege.textContent = data["COLLEGE"] || "—";
        playerDraft.textContent = formatDraft(data["DRAFT_YEAR"], data["DRAFT_NUMBER"]);
        playerTeam.textContent = data["TEAM_NAME"] || data["TEAM_ABBREVIATION"] || "—";

    } catch (err) {
        console.error(err);

        playerName.textContent = "ERROR";
        playerHeight.textContent = "ERROR";
        playerWeight.textContent = "ERROR";
        playerExp.textContent = "ERROR";
        playerTeam.textContent = "ERROR";
    }
}

function formatDraft(year, pick) {
    if (!year || String(year).toLowerCase() === "undrafted") return "Undrafted";
    if (!pick || String(pick).toLowerCase() === "undrafted") return String(year);
    return `${year} · Pick #${pick}`;
}


async function fetchAndRender() {
    loadingOverlay.style.display = "flex";
    emptyState.style.display = "none";
    playerTable.style.display = "table";

    try {
        const data = await fetchPlayerStats({
            playerId: playerId,
            type: tableTypeSelect.value,
            min: minMinutesSlider.value,
            skill: skillSelect.value,
            pillar: pillarSelect.value
        });

        currentData = data;

        if (currentData.length === 0) {
            playerTable.style.display = "none";
            emptyState.style.display = "block";
            return;
        }

        updateTable(currentData, tableHeadRow, tableFilterRow, tableBody);

    } catch (err) {
        console.error(err);

        playerTable.style.display = "none";
        emptyState.style.display = "block";
        emptyState.innerHTML =
            "<p>No data. Try reducing minimum minutes.</p>";
    } finally {
        loadingOverlay.style.display = "none";
    }
}


document.addEventListener("DOMContentLoaded", init);
