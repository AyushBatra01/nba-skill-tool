let currentData = [];

const params = new URLSearchParams(window.location.search);

// Get team ID
const teamId = Number(params.get("team_id"));

// DOM Elements
const teamName = document.getElementById("team-name");
const teamLogo = document.getElementById("team-logo");
const teamCity = document.getElementById("team-city");
const teamFounded = document.getElementById("team-founded");
const teamAge = document.getElementById("team-age");
const teamAbbreviation = document.getElementById("team-abbreviation");
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
const teamTable = document.getElementById("team-table");


async function init() {
    if (!Number.isInteger(teamId) || teamId <= 0) {
        teamName.textContent = "Team not found";
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

    extraInfoToggle.addEventListener("change", () => {
        extraInfoLabel.textContent =
            extraInfoToggle.checked ? "On" : "Off";
    });

    updateBtn.addEventListener("click", fetchAndRender);

    // Initial setup
    await loadMetadata();
    await updateInfo();
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


async function updateInfo() {
    try {
        const data = await fetchTeamInfo(teamId);
        teamName.textContent = data.FULL_NAME;
        teamCity.textContent = data.CITY || "—";
        teamFounded.textContent = data.YEAR_FOUNDED || "—";
        teamAge.textContent = data.YEAR_FOUNDED
            ? `${new Date().getFullYear() - data.YEAR_FOUNDED} years`
            : "—";
        teamAbbreviation.textContent = data.ABBREVIATION || "—";
        teamLogo.src = teamLogoUrl(teamId);
        teamLogo.alt = `${data.FULL_NAME} logo`;
        teamLogo.hidden = false;
        teamLogo.addEventListener("error", () => hideMissingImage(teamLogo), { once: true });
    } catch (err) {
        console.error(err);
        teamName.textContent = "Team not found";
    }
}


async function fetchAndRender() {
    loadingOverlay.style.display = "flex";
    emptyState.style.display = "none";
    teamTable.style.display = "table";

    try {
        const data = await fetchTeamStats({
            teamId: teamId,
            type: tableTypeSelect.value,
            season: seasonSelect.value,
            min: minMinutesSlider.value,
            skill: skillSelect.value,
            pillar: pillarSelect.value,
            detailed: extraInfoToggle.checked
        });

        currentData = data;

        if (currentData.length === 0) {
            teamTable.style.display = "none";
            emptyState.style.display = "block";
            return;
        }

        updateTable(currentData, tableHeadRow, tableFilterRow, tableBody);

    } catch (err) {
        console.error(err);

        teamTable.style.display = "none";
        emptyState.style.display = "block";
        emptyState.innerHTML =
            "<p>Error loading data. Make sure the backend is running.</p>";
    } finally {
        loadingOverlay.style.display = "none";
    }
}


document.addEventListener("DOMContentLoaded", init);
