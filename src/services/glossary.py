"""Glossary data derived from the scoring configuration used by the app."""

from src.config.load_config import column_metadata, configs


FORMULAS = {
    "PTS": "100 × points / possessions",
    "Shots": "FGA + 0.44 × FTA",
    "TSP": "PTS / (2 × (FGA + 0.44 × FTA))",
    "TOVP": "TOV / (Shots + TOV)",
    "negTOVP": "−TOVP",
    "Score": "PTS × TSP",
    "Pass": "AST² / (AST + TOV)",
    "Double": "Score × Pass",
    "Add": "(PTS + AST)² / (Shots + AST + TOV)",
    "TouchEfficiency": "AST rate × points per assist + points per touch",
    "RimPressure": "Rim rate × (rim score rate × (1 − rim turnover rate))",
    "Iso": "Isolation points × isolation points per possession",
    "PnR": "P&R ball-handler and handoff points × points per possession",
    "TPP": "3P% × volume multiplier",
    "TPS": "3P%² × 3PA",
    "FTP": "(FTM + league-average FT% × baseline FTA) / (FTA + baseline FTA)",
    "OffScreen": "Off-screen points × off-screen points per possession",
    "SpotUp": "Spot-up points × spot-up points per possession",
    "CatchShoot": "Catch-and-shoot points × catch-and-shoot points per attempt",
    "Cut": "Cut points × cut points per possession",
    "Rollman": "Roll-man points × roll-man points per possession",
    "Stock": "STL + BLK",
    "Double_def": "STL × BLK",
    "AdjPMRim": "−rim FG% plus-minus × √(rim defended FGA)",
    "AdjPMOut": "−perimeter FG% plus-minus × √(perimeter defended FGA)",
    "D_FGA_out": "All defended FGA − rim defended FGA",
    "ClipMatchupVers": "Matchup versatility, clipped to the 0.9–1.0 range",
    "AdjBLK": "Block rate − height-based expected block rate",
    "AdjOREB": "Contested offensive rebound rate − height-based expected rate",
    "AdjDREB": "Contested defensive rebound rate − height-based expected rate",
    "Hustle": "Loose balls recovered + charges drawn + box outs / 4",
}


def get_glossary():
    skills = []
    pillars = []
    for skill_name in ("Creation", "OffBall", "Defense", "Physicality"):
        config = configs[skill_name.lower()]
        skill_pillars = []
        for pillar_name, pillar in config["pillars"].items():
            stats = [
                {
                    "name": stat_name,
                    "weight": stat["weight"],
                    "description": stat["description"],
                    "formula": FORMULAS.get(stat_name),
                }
                for stat_name, stat in pillar["stats"].items()
            ]
            pillar_data = {
                "name": pillar_name,
                "skill": skill_name,
                "weight": pillar["weight"],
                "description": pillar["description"],
                "stats": stats,
            }
            skill_pillars.append(pillar_data)
            pillars.append(pillar_data)
        skills.append({
            "name": skill_name,
            "description": column_metadata[skill_name]["description"],
            "pillars": skill_pillars,
        })

    raw_stat_details = {
        name: {
            "name": name,
            "display_name": value.get("display_name", name),
            "description": value.get("description", ""),
            "formula": FORMULAS.get(name),
        }
        for name, value in column_metadata.items()
        if value.get("type") == "raw"
    }
    # Include every component metric used in a pillar, including derived
    # measures which do not have a standalone column-metadata entry.
    for pillar in pillars:
        for stat in pillar["stats"]:
            raw_stat_details[stat["name"]] = {
                "name": stat["name"],
                "display_name": column_metadata.get(stat["name"], {}).get("display_name", stat["name"]),
                "description": stat["description"],
                "formula": stat["formula"],
            }

    return {
        "methodology": {
            "minimum_minutes": "Players below the selected minimum-minute threshold are excluded before scores are calculated.",
            "raw_scores": "The source tracking, play-type, and box-score data are converted into the raw measures below. Counting statistics are generally expressed per 100 possessions.",
            "z_scores": "Every raw measure is standardized within the eligible player pool: z = (value − pool mean) / pool standard deviation.",
            "pillars": "A pillar is the weighted sum of its component raw-stat z-scores, then standardized again.",
            "skills": "A skill is the weighted sum of its pillar scores, then standardized again.",
            "overall": "Overall Rating and Role are weighted sums of skill scores, then standardized again. Their weights are listed below.",
        },
        "overall": [
            {
                "name": score_name,
                "description": column_metadata[score_name]["description"],
                "weights": [
                    {"name": skill_name, "weight": info["weight"]}
                    for skill_name, info in config.items()
                ],
            }
            for score_name, config in configs["combined"].items()
        ],
        "skills": skills,
        "pillars": pillars,
        "raw_stats": sorted(raw_stat_details.values(), key=lambda stat: stat["display_name"]),
    }
