const API_BASE = "http://127.0.0.1:8000";

const pillarMappings = {
    "Creation": ["Scoring", "Playmaking", "DualThreat", "Pressure"],
    "OffBall": ["Shooting", "Spacing", "Interior"],
    "Defense": ["Disruption", "RimProtection", "Assignment", "Versatility"],
    "Physicality": ["RimForce", "Explosiveness", "Rebounding", "Motor"]
};

const ignoredColumns = ["PLAYER_ID", "TEAM_ID", "SEASON"];
const nonPctColumns = ["PLAYER_NAME", "TEAM", "AGE", "MIN", "HEIGHT", "WEIGHT", "COLLEGE", "COUNTRY", "DRAFT_YEAR", "DRAFT_NUMBER"];
const filterableColumns = ["PLAYER_NAME", "TEAM"];
