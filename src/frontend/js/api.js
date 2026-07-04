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