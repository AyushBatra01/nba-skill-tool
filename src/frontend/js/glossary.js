const methodologySteps = document.getElementById("methodology-steps");
const overallList = document.getElementById("overall-list");
const skillList = document.getElementById("skill-list");
const rawStatList = document.getElementById("raw-stat-list");
const glossarySearch = document.getElementById("glossary-search");
const glossaryEmpty = document.getElementById("glossary-empty");
let rawStats = [];

function addTextElement(parent, tag, text, className) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = text;
    parent.appendChild(element);
    return element;
}

function renderMethodology(methodology) {
    methodologySteps.innerHTML = "";
    Object.entries(methodology).forEach(([title, explanation], index) => {
        const step = document.createElement("article");
        step.className = "methodology-step";
        addTextElement(step, "span", String(index + 1).padStart(2, "0"), "step-number");
        const copy = document.createElement("div");
        addTextElement(copy, "h3", title.replace(/_/g, " "));
        addTextElement(copy, "p", explanation);
        step.appendChild(copy);
        methodologySteps.appendChild(step);
    });
}

function renderWeightedCard(item, description, weights) {
    const card = document.createElement("article");
    card.className = "glossary-card glass-panel";
    addTextElement(card, "h3", item);
    addTextElement(card, "p", description);
    const weightList = document.createElement("ul");
    weightList.className = "weight-list";
    weights.forEach(weight => {
        const row = document.createElement("li");
        addTextElement(row, "span", weight.name);
        addTextElement(row, "strong", `${Math.round(weight.weight * 100)}%`);
        weightList.appendChild(row);
    });
    card.appendChild(weightList);
    return card;
}

function renderSkills(skills) {
    skillList.innerHTML = "";
    skills.forEach(skill => {
        const skillSection = document.createElement("article");
        skillSection.className = "skill-glossary glass-panel";
        addTextElement(skillSection, "h3", skill.name);
        addTextElement(skillSection, "p", skill.description);
        const pillars = document.createElement("div");
        pillars.className = "pillar-list";
        skill.pillars.forEach(pillar => {
            const pillarElement = document.createElement("details");
            pillarElement.className = "pillar-detail";
            const summary = document.createElement("summary");
            addTextElement(summary, "span", pillar.name);
            addTextElement(summary, "small", `${Math.round(pillar.weight * 100)}% of ${skill.name}`);
            pillarElement.appendChild(summary);
            addTextElement(pillarElement, "p", pillar.description);
            const metricList = document.createElement("ul");
            metricList.className = "weight-list metric-list";
            pillar.stats.forEach(stat => {
                const row = document.createElement("li");
                const label = document.createElement("span");
                label.textContent = stat.name;
                label.title = stat.description;
                row.appendChild(label);
                addTextElement(row, "strong", `${Math.round(stat.weight * 100)}%`);
                metricList.appendChild(row);
            });
            pillarElement.appendChild(metricList);
            pillars.appendChild(pillarElement);
        });
        skillSection.appendChild(pillars);
        skillList.appendChild(skillSection);
    });
}

function renderRawStats() {
    const query = glossarySearch.value.trim().toLowerCase();
    const shown = rawStats.filter(stat =>
        [stat.name, stat.display_name, stat.description, stat.formula]
            .filter(Boolean)
            .join(" ")
            .toLowerCase()
            .includes(query)
    );
    rawStatList.innerHTML = "";
    glossaryEmpty.hidden = shown.length > 0;
    shown.forEach(stat => {
        const card = document.createElement("article");
        card.className = "glossary-card raw-stat-card glass-panel";
        addTextElement(card, "h3", stat.display_name);
        if (stat.display_name !== stat.name) addTextElement(card, "span", stat.name, "stat-key");
        addTextElement(card, "p", stat.description);
        if (stat.formula) addTextElement(card, "code", stat.formula, "formula");
        rawStatList.appendChild(card);
    });
}

async function initGlossary() {
    try {
        const data = await fetchGlossary();
        renderMethodology(data.methodology);
        data.overall.forEach(score => overallList.appendChild(renderWeightedCard(score.name, score.description, score.weights)));
        renderSkills(data.skills);
        rawStats = data.raw_stats;
        renderRawStats();
    } catch (error) {
        console.error(error);
        rawStatList.innerHTML = "<p class=\"directory-empty\">Unable to load the glossary. Make sure the backend is running.</p>";
    }
}

glossarySearch.addEventListener("input", renderRawStats);
document.addEventListener("DOMContentLoaded", initGlossary);
