const state = {
  summary: null,
  demo: null,
  exportPayload: null,
};

const pct = (value) => `${(value * 100).toFixed(2)}%`;

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json();
}

function setHeadlineMetrics(summary) {
  const metrics = summary.headline_metrics;
  const cards = document.querySelectorAll("#headline-metrics article strong");
  cards[0].textContent = pct(metrics.gate_accuracy);
  cards[1].textContent = pct(metrics.trace_completeness);
  cards[2].textContent = pct(metrics.conformance_pass_rate);
  cards[3].textContent = String(metrics.total_decisions);
}

function renderOverview() {
  const s = state.summary;
  document.querySelector("#overview").innerHTML = `
    <h2>Overview</h2>
    <div class="grid-2">
      <div class="callout">
        <p class="stat-label">Reference architecture</p>
        <h3>${s.positioning.primary}</h3>
        <p class="small">${s.positioning.system_name}. ${s.positioning.protocol_name}.</p>
      </div>
      <div class="callout">
        <p class="stat-label">Claim boundary</p>
        <ul>${s.positioning.not_claims.map((claim) => `<li>${claim}</li>`).join("")}</ul>
      </div>
    </div>`;
}

function renderEnvelope() {
  const first = state.demo.profiles.guardian.decision_envelope;
  document.querySelector("#envelope").innerHTML = `
    <h2>DecisionEnvelope</h2>
    <p class="small">Redacted public envelope for the canonical investor prompt. Raw prompt and candidate text are represented by hashes.</p>
    <pre>${escapeHtml(JSON.stringify(first, null, 2))}</pre>`;
}

function renderAccuracy() {
  const b = state.summary.benchmark;
  document.querySelector("#accuracy").innerHTML = `
    <h2>Gate Accuracy</h2>
    <div class="callout">
      <p class="stat-label">CognitiveOS-v0 seed benchmark</p>
      <h3>${pct(state.summary.headline_metrics.gate_accuracy)}</h3>
      <p class="small">${b.scenario_count} scenarios across ${b.profile_count} profiles.</p>
    </div>`;
}

function renderSeparation() {
  const b = state.summary.benchmark;
  document.querySelector("#separation").innerHTML = `
    <h2>Profile Separation</h2>
    <div class="grid-2">
      <div class="callout"><p class="stat-label">Gate Difference Rate</p><h3>${pct(b.gate_difference_rate)}</h3></div>
      <div class="callout"><p class="stat-label">Profile Separation Score</p><h3>${pct(b.profile_separation_score)}</h3></div>
    </div>`;
}

function renderTrace() {
  document.querySelector("#trace").innerHTML = `
    <h2>Trace Completeness</h2>
    <div class="callout">
      <p class="stat-label">Auditable trace coverage</p>
      <h3>${pct(state.summary.headline_metrics.trace_completeness)}</h3>
      <p class="small">Trace completeness is counted only when the decision includes trace id, profile, gate, axis, reason, counterfactual, and risk tag structure.</p>
    </div>`;
}

function renderConformance() {
  const c = state.summary.conformance;
  document.querySelector("#conformance").innerHTML = `
    <h2>Conformance</h2>
    <div class="grid-2">
      <div class="callout"><p class="stat-label">Pass Rate</p><h3>${pct(c.conformance_pass_rate)}</h3></div>
      <div class="callout"><p class="stat-label">Total Decisions</p><h3>${c.total}</h3></div>
    </div>
    <pre>${escapeHtml(JSON.stringify(c, null, 2))}</pre>`;
}

function renderBaseline() {
  const rows = Object.entries(state.summary.baselines)
    .map(([name, metrics]) => `
      <tr>
        <td>${name}</td>
        <td>${pct(metrics.gate_accuracy)}</td>
        <td>${pct(metrics.trace_completeness)}</td>
        <td>${pct(metrics.profile_separation_score)}</td>
      </tr>`)
    .join("");
  document.querySelector("#baseline").innerHTML = `
    <h2>Baseline Comparison</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Runner</th><th>Gate Accuracy</th><th>Trace</th><th>Profile Separation</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function renderViewer() {
  const rows = Object.entries(state.demo.profiles)
    .map(([profile, result]) => `
      <tr>
        <td>${profile}</td>
        <td><span class="gate">${result.gate}</span></td>
        <td>${result.risk_tags.join(", ")}</td>
        <td>${result.decision_envelope.trace_id}</td>
      </tr>`)
    .join("");
  document.querySelector("#viewer").innerHTML = `
    <h2>Redacted Trace Viewer</h2>
    <p class="small">Canonical investor prompt is represented by prompt hash: ${state.demo.prompt_hash}</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Profile</th><th>Gate</th><th>Risk Tags</th><th>Trace ID</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function renderExport() {
  document.querySelector("#export").innerHTML = `
    <h2>Evidence Export</h2>
    <p class="small">Combined public evidence payload. Raw prompt and candidate text are not included.</p>
    <pre>${escapeHtml(JSON.stringify(state.exportPayload, null, 2))}</pre>`;
}

function wireTabs() {
  document.querySelectorAll(".tabs button").forEach((button) => {
    button.addEventListener("click", () => {
      activateTab(button.dataset.tab, true);
    });
  });
  window.addEventListener("hashchange", () => activateTab(tabFromHash(), false));
}

function activateTab(tabId, updateHash) {
  const panel = document.getElementById(tabId);
  const button = document.querySelector(`.tabs button[data-tab="${tabId}"]`);
  if (!panel || !button) return;
  document.querySelectorAll(".tabs button").forEach((item) => item.classList.remove("active"));
  document.querySelectorAll(".panel").forEach((item) => item.classList.remove("active"));
  button.classList.add("active");
  panel.classList.add("active");
  if (updateHash) {
    history.replaceState(null, "", `#${tabId}`);
  }
}

function tabFromHash() {
  return window.location.hash.replace("#", "") || "overview";
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function main() {
  wireTabs();
  [state.summary, state.demo, state.exportPayload] = await Promise.all([
    fetchJson("/evidence/summary"),
    fetchJson("/evidence/demo"),
    fetchJson("/evidence/export"),
  ]);
  setHeadlineMetrics(state.summary);
  renderOverview();
  renderEnvelope();
  renderAccuracy();
  renderSeparation();
  renderTrace();
  renderConformance();
  renderBaseline();
  renderViewer();
  renderExport();
  activateTab(tabFromHash(), false);
}

main().catch((error) => {
  document.querySelector("#overview").innerHTML = `<h2>Load Error</h2><pre>${escapeHtml(String(error))}</pre>`;
});
