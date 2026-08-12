let columnMetadata = {};

const pillarMappings = {
    "Creation": ["Scoring", "Playmaking", "DualThreat", "Pressure"],
    "OffBall": ["Shooting", "Spacing", "Interior"],
    "Defense": ["Disruption", "RimProtection", "Assignment", "Versatility"],
    "Physicality": ["RimForce", "Explosiveness", "Rebounding", "Motor"]
};

const ignoredColumns = ["PLAYER_ID", "TEAM_ID"];
const nonPctColumns = ["PLAYER_NAME", "TEAM", "SEASON", "AGE", "MIN", "HEIGHT", "WEIGHT", "COLLEGE", "COUNTRY", "DRAFT_YEAR", "DRAFT_NUMBER"];
const filterableColumns = ["PLAYER_NAME", "TEAM", "SEASON"];

function renderSiteHeader() {
    const mount = document.getElementById("site-header");
    if (!mount) return;

    const page = document.body.dataset.page || "leaderboard";
    const links = [
        ["leaderboard", "index.html", "Leaderboard"],
        ["players", "players.html", "Players"],
        ["teams", "teams.html", "Teams"],
        ["glossary", "glossary.html", "Glossary"],
    ];

    mount.innerHTML = `
        <nav class="site-nav" aria-label="Primary navigation">
            <a class="brand" href="index.html" aria-label="NBA Skills home">
                <span>NBA Skills</span>
            </a>
            <div class="nav-links">
                ${links.map(([key, href, label]) => `
                    <a href="${href}" class="nav-link ${page === key ? "is-active" : ""}">
                        ${label}
                    </a>
                `).join("")}
            </div>
        </nav>
    `;
}

function playerHeadshotUrl(playerId) {
    return `https://cdn.nba.com/headshots/nba/latest/1040x760/${playerId}.png`;
}

function teamLogoUrl(teamId) {
    return `https://cdn.nba.com/logos/nba/${teamId}/primary/L/logo.svg`;
}

function hideMissingImage(image) {
    image.classList.add("is-missing");
    image.remove();
}

renderSiteHeader();

async function loadMetadata() {
    const res = await fetch("./assets/column_metadata.json");
    if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
    }
    columnMetadata = await res.json();
}

function getMeta(col) {
    return columnMetadata[col] || {};
}

function formatValue(col, val) {
    const meta = getMeta(col);
    if (val === null || val === undefined) return "-";
    if (typeof val !== "number") return String(val);

    const decimals = meta.decimals ?? 0;
    if (meta.percent) {
        return `${(val * 100).toFixed(decimals-2)}%`;
    }

    if (col == "HEIGHT") {
        const feet = Math.floor(val / 12);
        const inches = val % 12;
        return `${feet}'${inches}"`
    }

    return val.toFixed(decimals);
}


function seasonOptions({
    seasonSelect,
    startYear = 2018,
    endYear = 2026
}) {
    for (let year = endYear; year >= startYear; year--) {
        const option = document.createElement("option");

        option.value = year;
        option.textContent = `${year-1}-${String(year).slice(-2)}`;

        if (year === endYear) {
            option.selected = true;
        }

        seasonSelect.appendChild(option);
    }
}


function updateDropdownVisibilities({
    tableTypeSelect,
    skillGroup,
    pillarGroup
}) {
    switch (tableTypeSelect.value) {
        case "overall":
            skillGroup.style.display = "none";
            pillarGroup.style.display = "none";
            break;

        case "skill":
            skillGroup.style.display = "flex";
            pillarGroup.style.display = "none";
            break;

        case "pillar":
            skillGroup.style.display = "flex";
            pillarGroup.style.display = "flex";
            break;
    }
}


function populatePillars({
    skillSelect,
    pillarSelect
}) {
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
