// ---------- CONFIG: group & metadata for severity ---------- //
const BACKEND_URL = "http://127.0.0.1:8000/analyze_report";

// Lab groups by key
const LAB_GROUPS = {
    "CBC": [
        "hemoglobin", "hematocrit", "rbc", "wbc", "platelets", "mcv", "mch", "mchc", "rdw",
        "neutrophils_pct", "lymphocytes_pct", "monocytes_pct", "eosinophils_pct", "basophils_pct"
    ],
    "Liver": [
        "sgpt", "sgot", "alp", "gamma_gt", "total_bilirubin", "direct_bilirubin",
        "total_protein", "albumin"
    ],
    "Kidney": [
        "urea", "creatinine", "uric_acid"
    ],
    "Lipids": [
        "total_cholesterol", "triglycerides", "hdl", "ldl", "vldl"
    ],
    "Thyroid": [
        "tsh", "t3", "t4"
    ],
};

// Basic ranges (mirrors backend interpretation_config.py for main tests)
// Basic ranges for frontend severity & chart (mirror of backend for main tests)
const LAB_METADATA_FRONT = {
    // CBC
    hemoglobin:   { name: "Hemoglobin", unit: "g/dL",      low: 12.0, high: 17.0 },
    hematocrit:   { name: "Hematocrit", unit: "%",         low: 36.0, high: 50.0 },
    rbc:          { name: "RBC",        unit: "mill/µL",   low: 4.0,  high: 5.8 },
    wbc:          { name: "WBC",        unit: "/µL",       low: 4000, high: 11000 },
    platelets:    { name: "Platelets",  unit: "lakhs/µL",  low: 1.5,  high: 4.5 },
    mcv:          { name: "MCV",        unit: "fL",        low: 80,   high: 100 },
    mch:          { name: "MCH",        unit: "pg",        low: 27,   high: 34 },
    mchc:         { name: "MCHC",       unit: "g/dL",      low: 32,   high: 36 },
    rdw:          { name: "RDW",        unit: "%",         low: 11.5, high: 14.5 },

    neutrophils_pct:  { name: "Neutrophils %",  unit: "%", low: 40, high: 70 },
    lymphocytes_pct:  { name: "Lymphocytes %",  unit: "%", low: 20, high: 40 },
    monocytes_pct:    { name: "Monocytes %",    unit: "%", low: 2,  high: 8 },
    eosinophils_pct:  { name: "Eosinophils %",  unit: "%", low: 1,  high: 6 },
    basophils_pct:    { name: "Basophils %",    unit: "%", low: 0,  high: 1 },

    // Glucose / diabetes
    fasting_glucose:  { name: "Fasting Glucose", unit: "mg/dL", low: 70,  high: 99 },
    pp_glucose:       { name: "Post-meal Glucose", unit: "mg/dL", low: 70, high: 140 },
    hba1c:            { name: "HbA1c", unit: "%",              low: 4.0, high: 5.6 },

    // Lipids
    total_cholesterol:{ name: "Total Cholesterol", unit: "mg/dL", low: 0,   high: 200 },
    triglycerides:    { name: "Triglycerides",     unit: "mg/dL", low: 0,   high: 150 },
    hdl:              { name: "HDL",              unit: "mg/dL", low: 40,  high: 200 },
    ldl:              { name: "LDL",              unit: "mg/dL", low: 0,   high: 130 },
    vldl:             { name: "VLDL",             unit: "mg/dL", low: 5,   high: 40 },

    // Kidney
    urea:             { name: "Urea",            unit: "mg/dL",  low: 15,  high: 40 },
    creatinine:       { name: "Creatinine",      unit: "mg/dL",  low: 0.6, high: 1.3 },
    uric_acid:        { name: "Uric Acid",       unit: "mg/dL",  low: 3.5, high: 7.0 },

    // Liver
    total_bilirubin:  { name: "Total Bilirubin", unit: "mg/dL",  low: 0.2, high: 1.2 },
    direct_bilirubin: { name: "Direct Bilirubin",unit: "mg/dL",  low: 0.0, high: 0.3 },
    sgpt:             { name: "ALT/SGPT",        unit: "U/L",    low: 0,   high: 40 },
    sgot:             { name: "AST/SGOT",        unit: "U/L",    low: 0,   high: 40 },
    alp:              { name: "ALP",             unit: "U/L",    low: 44,  high: 147 },
    gamma_gt:         { name: "GGT",             unit: "U/L",    low: 0,   high: 60 },
    total_protein:    { name: "Total Protein",   unit: "g/dL",   low: 6.0, high: 8.3 },
    albumin:          { name: "Albumin",         unit: "g/dL",   low: 3.5, high: 5.0 },

    // Electrolytes
    sodium:           { name: "Sodium",          unit: "mmol/L", low: 135, high: 145 },
    potassium:        { name: "Potassium",       unit: "mmol/L", low: 3.5, high: 5.0 },
    chloride:         { name: "Chloride",        unit: "mmol/L", low: 98,  high: 107 },

    // Thyroid
    tsh:              { name: "TSH",             unit: "µIU/mL", low: 0.4, high: 4.0 },
    t3:               { name: "T3",              unit: "ng/dL",  low: 80,  high: 200 },
    t4:               { name: "T4",              unit: "µg/dL",  low: 5.0, high: 12.0 },

    // Inflammation
    crp:              { name: "CRP",             unit: "mg/L",   low: 0,   high: 5 },
    esr:              { name: "ESR",             unit: "mm/hr",  low: 0,   high: 20 },

    // Vitamins
    vitamin_d:        { name: "Vitamin D",       unit: "ng/mL",  low: 20,  high: 50 },
    vitamin_b12:      { name: "Vitamin B12",     unit: "pg/mL",  low: 200, high: 900 },
};


// ---------- DOM ELEMENTS ----------
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const fileInfo = document.getElementById("file-info");

const uploadForm = document.getElementById("upload-form");
const analyzeBtn = document.getElementById("analyze-btn");
const analyzeText = document.getElementById("analyze-text");
const loader = document.getElementById("loader");
const statusEl = document.getElementById("status");

const resultsSection = document.getElementById("results");
const riskBox = document.getElementById("risk-section");
const parsedLabsDiv = document.getElementById("parsed-labs");
const summaryDiv = document.getElementById("ai-summary");

const chartCanvas = document.getElementById("labs-chart");
let labsChart = null;

let selectedFile = null;

// ---------- FILE HANDLING ----------
dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
});

dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("drag-over");
});

dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    if (files && files[0]) {
        selectedFile = files[0];
        fileInput.files = files;
        updateFileInfo();
    }
});

fileInput.addEventListener("change", () => {
    selectedFile = fileInput.files[0] || null;
    updateFileInfo();
});

function updateFileInfo() {
    if (!selectedFile) {
        fileInfo.textContent = "";
        return;
    }
    const sizeMB = (selectedFile.size / (1024 * 1024)).toFixed(2);
    fileInfo.textContent = `📄 Selected: ${selectedFile.name} (${sizeMB} MB)`;
}

// ---------- STATUS / LOADING ----------
function setStatus(msg, type = "info") {
    statusEl.textContent = msg;
    const colors = {
        info: "#9ca3af",
        success: "#4ade80",
        error: "#f87171",
    };
    statusEl.style.color = colors[type] || colors.info;
}

function setLoading(isLoading) {
    if (isLoading) {
        analyzeBtn.disabled = true;
        loader.style.display = "inline-block";
        analyzeText.style.display = "none";
    } else {
        analyzeBtn.disabled = false;
        loader.style.display = "none";
        analyzeText.style.display = "inline";
    }
}

// ---------- FORM SUBMIT ----------
uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!selectedFile) {
        setStatus("Please select a report file first.", "error");
        return;
    }

    setLoading(true);
    setStatus("Uploading & analyzing report...", "info");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
        const resp = await fetch(BACKEND_URL, {
            method: "POST",
            body: formData,
        });

        if (!resp.ok) {
            const text = await resp.text();
            throw new Error(`Backend error ${resp.status}: ${text}`);
        }

        const data = await resp.json();
        setStatus("Analysis complete.", "success");
        renderResults(data);
    } catch (err) {
        console.error(err);
        setStatus("Error calling backend: " + err.message, "error");
    } finally {
        setLoading(false);
    }
});

// ---------- SEVERITY / GROUPING HELPERS ----------
function classifyLab(key, value) {
    const meta = LAB_METADATA_FRONT[key];
    if (!meta || meta.low === undefined || meta.high === undefined) {
        return {
            severity: "unknown",
            deviation: 0,
            label: value.toString(),
        };
    }

    const low = meta.low;
    const high = meta.high;
    const mid = (low + high) / 2;

    let severity = "normal";
    let deviation = 0;

    if (value < low) {
        severity = "low";
        deviation = (mid - value) / (high - low || 1);
    } else if (value > high) {
        severity = "high";
        deviation = (value - mid) / (high - low || 1);
    } else {
        severity = "normal";
        deviation = 0;
    }

    return {
        severity,
        deviation: Math.max(0, Number(deviation.toFixed(2))),
        label: `${value} ${meta.unit || ""}`.trim(),
    };
}

function groupLabs(parsed) {
    const groups = {
        "CBC": [],
        "Liver": [],
        "Kidney": [],
        "Lipids": [],
        "Thyroid": [],
        "Others": [],
    };

    for (const [key, value] of Object.entries(parsed)) {
        let foundGroup = null;
        for (const [groupName, keys] of Object.entries(LAB_GROUPS)) {
            if (keys.includes(key)) {
                foundGroup = groupName;
                break;
            }
        }
        if (!foundGroup) foundGroup = "Others";

        const meta = LAB_METADATA_FRONT[key];
        const name = meta?.name || key;
        const classification = classifyLab(key, value);

        groups[foundGroup].push({
            key,
            name,
            value,
            severity: classification.severity,
            label: classification.label,
            deviation: classification.deviation,
        });
    }

    return groups;
}

// ---------- RENDER RESULTS ----------
function renderResults(data) {
    resultsSection.classList.remove("hidden");

    // RISK summary
    const risk = data.ml_result?.risk || {};
    const riskLabel = risk.risk_label || "Unknown";
    const riskScore = typeof risk.risk_score === "number" ? risk.risk_score.toFixed(2) : "0.00";

    let pillClass = "risk-unknown";
    if (riskLabel === "Low") pillClass = "risk-low";
    if (riskLabel === "Moderate") pillClass = "risk-moderate";
    if (riskLabel === "High") pillClass = "risk-high";

    riskBox.innerHTML = `
        <div class="risk-title">Overall risk level (demo only):</div>
        <div>
            <span class="risk-pill ${pillClass}">${riskLabel}</span>
            <span class="muted" style="margin-left:8px;">Score: ${riskScore}</span>
        </div>
        <p class="muted" style="margin-top:4px;">
            This is a rough, automated estimate based only on the numbers the system could read.
            A doctor may interpret your report differently based on your overall health.
        </p>
    `;

    // Labs grouping
    const labs = data.parsed_labs || {};
    const entries = Object.entries(labs);

    if (entries.length === 0) {
        parsedLabsDiv.innerHTML = `<p class="muted">No lab values could be reliably extracted from this report.</p>`;
    } else {
        const grouped = groupLabs(labs);
        parsedLabsDiv.innerHTML = "";

        for (const [groupName, items] of Object.entries(grouped)) {
            if (!items.length) continue;

            const groupCard = document.createElement("div");
            groupCard.className = "labs-group-card";

            const title = document.createElement("div");
            title.className = "labs-group-title";
            title.textContent = groupName;
            groupCard.appendChild(title);

            items.forEach(item => {
                const row = document.createElement("div");
                row.className = "lab-row";

                const left = document.createElement("span");
                left.className = "lab-name";
                left.innerHTML = `<span class="severity-dot severity-${item.severity}"></span>${item.name}`;

                const right = document.createElement("span");
                right.className = "lab-value";
                right.textContent = item.label;

                row.appendChild(left);
                row.appendChild(right);
                groupCard.appendChild(row);
            });

            parsedLabsDiv.appendChild(groupCard);
        }
    }

    // AI SUMMARY (markdown-ish)
    const summary = data.llm_summary || "";
    summaryDiv.innerHTML = formatMarkdown(summary);

    // Bar chart of most abnormal labs
    buildChartFromParsedLabs(labs);
}

// ---------- CHART RENDERING ----------
function buildChartFromParsedLabs(parsed) {
    if (!chartCanvas) return;

    if (labsChart) {
        labsChart.destroy();
        labsChart = null;
    }

    const items = [];
    for (const [key, value] of Object.entries(parsed)) {
        const meta = LAB_METADATA_FRONT[key];
        const { severity, deviation } = classifyLab(key, value);
        if (!meta) continue; // only chart known tests
        items.push({ key, name: meta.name, severity, deviation });
    }

    // Only keep abnormal or interesting results
    const abnormalOnly = items.filter(i => i.severity === "high" || i.severity === "low");
    const list = (abnormalOnly.length ? abnormalOnly : items)
        .sort((a, b) => b.deviation - a.deviation)
        .slice(0, 8);

    if (!list.length) {
        const ctx = chartCanvas.getContext("2d");
        ctx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
        return;
    }

    const labels = list.map(i => i.name);
    const values = list.map(i => i.deviation || 0.01);
    const colors = list.map(i => {
        if (i.severity === "high") return "#f97373";
        if (i.severity === "low") return "#38bdf8";
        if (i.severity === "normal") return "#4ade80";
        return "#6b7280";
    });

    const ctx = chartCanvas.getContext("2d");
    labsChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Relative deviation (demo scale)",
                data: values,
                backgroundColor: colors,
            }],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        display: false
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    ticks: {
                        color: "#e5e7eb",
                        font: { size: 11 }
                    },
                    grid: {
                        color: "rgba(55,65,81,0.5)"
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const idx = context.dataIndex;
                            const item = list[idx];
                            return `${item.name}: more abnormal (${item.severity})`;
                        }
                    }
                }
            }
        }
    });
}

// ---------- MARKDOWN-LIKE RENDER ----------
function formatMarkdown(text) {
    if (!text) return "<p class='muted'>No explanation returned.</p>";

    let html = text;

    html = html.replace(/^### (.*)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.*)$/gm, "<h2>$1</h2>");

    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    html = html.replace(/^- (.*)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>[\s\S]*?<\/li>)/gm, "<ul>$1</ul>");

    html = html.replace(/\n/g, "<br>");

    return html;
}
