const API_BASE = "http://127.0.0.1:8000";

async function fetchLeaderboard(params) {
    const { type, season, min, skill, pillar, detailed } = params;

    let url = "";

    if (type === "overall") {
        url = `${API_BASE}/leaderboard/overall?season=${season}&minimum=${min}&detailed=${detailed}`;
    } else if (type === "skill") {
        url = `${API_BASE}/leaderboard/skill/${skill}?season=${season}&minimum=${min}&detailed=${detailed}`;
    } else {
        url = `${API_BASE}/leaderboard/pillar/${skill}/${pillar}?season=${season}&minimum=${min}&detailed=${detailed}`;
    }

    const res = await fetch(url);
    if (!res.ok) throw new Error("API error");

    return await res.json();
}


async function fetchPlayerInfo(playerId) {
    let url = `${API_BASE}/player/${playerId}/info`;

    const res = await fetch(url)
    if (!res.ok) throw new Error("API error");

    return await res.json();
}

async function fetchPlayerDirectory(season) {
    const res = await fetch(`${API_BASE}/player/directory?season=${season}`);
    if (!res.ok) throw new Error("API error");
    return await res.json();
}


async function fetchPlayerStats(params) {
    const { playerId, type, min, skill, pillar } = params;

    let url = "";

    if (type === "overall") {
        url = `${API_BASE}/player/${playerId}/overall?minimum=${min}`;
    } else if (type === "skill") {
        url = `${API_BASE}/player/${playerId}/skill/${skill}?minimum=${min}`;
    } else {
        url = `${API_BASE}/player/${playerId}/pillar/${skill}/${pillar}?minimum=${min}`;
    }

    const res = await fetch(url);
    if (!res.ok) throw new Error("API error");

    return await res.json();
}


async function fetchTeamStats(params) {
    const { teamId, type, season, min, skill, pillar, detailed } = params;

    let url = "";

    if (type === "overall") {
        url = `${API_BASE}/team/${teamId}/overall?season=${season}&minimum=${min}&detailed=${detailed}`;
    } else if (type === "skill") {
        url = `${API_BASE}/team/${teamId}/skill/${skill}?season=${season}&minimum=${min}&detailed=${detailed}`;
    } else {
        url = `${API_BASE}/team/${teamId}/pillar/${skill}/${pillar}?season=${season}&minimum=${min}&detailed=${detailed}`;
    }

    const res = await fetch(url);
    if (!res.ok) throw new Error("API error");

    return await res.json();
}

async function fetchTeamInfo(teamId) {
    const res = await fetch(`${API_BASE}/team/${teamId}/info`);
    if (!res.ok) throw new Error("API error");
    return await res.json();
}

async function fetchTeamDirectory() {
    const res = await fetch(`${API_BASE}/team/directory`);
    if (!res.ok) throw new Error("API error");
    return await res.json();
}

async function fetchGlossary() {
    const res = await fetch(`${API_BASE}/glossary`);
    if (!res.ok) throw new Error("API error");
    return await res.json();
}
