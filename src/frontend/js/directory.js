const searchInput = document.getElementById("directory-search");
const directoryGrid = document.getElementById("directory-grid");
const directoryCount = document.getElementById("directory-count");
const directoryEmpty = document.getElementById("directory-empty");
const seasonSelect = document.getElementById("directory-season");
const isTeamDirectory = document.body.dataset.page === "teams";
let entries = [];
let directoryRequest = 0;

function searchableText(entry) {
    if (isTeamDirectory) {
        return [entry.FULL_NAME, entry.CITY, entry.ABBREVIATION, entry.NICKNAME].join(" ").toLowerCase();
    }
    return [entry.FIRST_NAME, entry.LAST_NAME, entry.TEAM_NAME, entry.TEAM_ABBREVIATION].join(" ").toLowerCase();
}

function renderDirectory() {
    const query = searchInput.value.trim().toLowerCase();
    const visibleEntries = entries.filter(entry => searchableText(entry).includes(query));
    directoryGrid.innerHTML = "";
    directoryCount.textContent = `${visibleEntries.length} ${isTeamDirectory ? "teams" : "players"}`;
    directoryEmpty.hidden = visibleEntries.length > 0;

    visibleEntries.forEach(entry => {
        const link = document.createElement("a");
        link.className = "directory-card glass-panel";
        link.href = isTeamDirectory
            ? `team.html?team_id=${entry.TEAM_ID}`
            : `player.html?player_id=${entry.PLAYER_ID}`;

        const image = document.createElement("img");
        image.className = isTeamDirectory ? "directory-team-logo" : "directory-headshot";
        image.src = isTeamDirectory ? teamLogoUrl(entry.TEAM_ID) : playerHeadshotUrl(entry.PLAYER_ID);
        image.alt = "";
        image.addEventListener("error", () => hideMissingImage(image), { once: true });

        const copy = document.createElement("div");
        const title = document.createElement("h2");
        const detail = document.createElement("p");
        if (isTeamDirectory) {
            title.textContent = entry.FULL_NAME;
            detail.textContent = `${entry.ABBREVIATION} · Founded ${entry.YEAR_FOUNDED}`;
        } else {
            title.textContent = `${entry.FIRST_NAME} ${entry.LAST_NAME}`;
            detail.textContent = entry.TEAM_NAME || entry.TEAM_ABBREVIATION || "NBA player";
        }
        copy.append(title, detail);
        link.append(image, copy);
        directoryGrid.appendChild(link);
    });
}

async function initDirectory() {
    try {
        if (isTeamDirectory) {
            entries = await fetchTeamDirectory();
            renderDirectory();
            return;
        }

        seasonOptions({ seasonSelect });
        seasonSelect.addEventListener("change", loadPlayersForSeason);
        await loadPlayersForSeason();
    } catch (error) {
        console.error(error);
        directoryEmpty.hidden = false;
        directoryEmpty.textContent = "Unable to load the directory. Make sure the backend is running.";
    }
}

async function loadPlayersForSeason() {
    const request = ++directoryRequest;
    directoryGrid.innerHTML = "";
    directoryEmpty.hidden = true;
    directoryCount.textContent = "Loading players…";

    try {
        const seasonEntries = await fetchPlayerDirectory(seasonSelect.value);
        if (request !== directoryRequest) return;
        entries = seasonEntries;
        renderDirectory();
    } catch (error) {
        if (request !== directoryRequest) return;
        console.error(error);
        directoryEmpty.hidden = false;
        directoryEmpty.textContent = "Unable to load the player directory. Make sure the backend is running.";
    }
}

searchInput.addEventListener("input", renderDirectory);
document.addEventListener("DOMContentLoaded", initDirectory);
