const state = {
  summary: null,
  demo: null,
  report: null,
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

function renderGuidedDemo() {
  const metrics = state.summary.headline_metrics;
  const story = state.demo.story;
  const steps = state.demo.steps
    .map((step, index) => `
      <article class="demo-step">
        <span>${index + 1}</span>
        <h3>${step.label}</h3>
        <p class="small">${step.detail}</p>
      </article>`)
    .join("");
  const profiles = Object.entries(state.demo.profiles)
    .map(([profile, result]) => `
      <article class="profile-card">
        <p class="stat-label">${result.profile_label || profile}</p>
        <h3>${result.gate}</h3>
        <p>${result.expected_reading || ""}</p>
        <p class="small">${result.risk_tags.join(", ")}</p>
        <code>${result.decision_envelope.trace_id}</code>
      </article>`)
    .join("");
  document.querySelector("#guided").innerHTML = `
    <h2>3-Minute Demo</h2>
    <div class="story-panel">
      <p class="stat-label">${state.demo.prompt_label}</p>
      <h3>${story.title}</h3>
      <p>${story.problem}</p>
      <p class="small">${story.protocol}</p>
      <code>${state.demo.prompt_hash}</code>
    </div>
    <div class="demo-grid">${steps}</div>
    <h3 class="section-kicker">Profile outcomes</h3>
    <div class="profile-grid">${profiles}</div>
    <h3 class="section-kicker">Privacy boundary</h3>
    <div class="grid-3">
      <div class="callout"><p class="stat-label">Public default</p><p>${state.demo.privacy_boundary.public_default}</p></div>
      <div class="callout"><p class="stat-label">Raw trace rule</p><p>${state.demo.privacy_boundary.raw_trace_rule}</p></div>
      <div class="callout"><p class="stat-label">Public artifact</p><p>${state.demo.privacy_boundary.public_artifact}</p></div>
    </div>
    <div class="completion-strip">
      <div><strong>${pct(metrics.gate_accuracy)}</strong><span>Gate accuracy</span></div>
      <div><strong>${pct(metrics.trace_completeness)}</strong><span>Trace completeness</span></div>
      <div><strong>${pct(metrics.conformance_pass_rate)}</strong><span>Conformance</span></div>
      <div><strong>${metrics.total_decisions}</strong><span>Decisions checked</span></div>
    </div>
    <p class="small boundary-note">Completion signal: ${story.completion_signal}</p>`;
}

function renderEnvelope() {
  const first = state.demo.profiles.guardian.decision_envelope;
  const anatomyRows = state.demo.envelope_anatomy
    .map((item) => `<tr><td>${item.field}</td><td>${item.meaning}</td></tr>`)
    .join("");
  document.querySelector("#envelope").innerHTML = `
    <h2>Decision Envelope</h2>
    <p class="small">Redacted public envelope. Source and candidate content are represented only by hashes.</p>
    <div class="table-wrap anatomy-table">
      <table>
        <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
        <tbody>${anatomyRows}</tbody>
      </table>
    </div>
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

function renderAdversarial() {
  const a = state.report.adversarial;
  const metricCards = `
    <div class="grid-4">
      <div class="callout"><p class="stat-label">Scenarios</p><h3>${a.scenario_count}</h3></div>
      <div class="callout"><p class="stat-label">Gate Accuracy</p><h3>${pct(a.gate_accuracy)}</h3></div>
      <div class="callout"><p class="stat-label">Trace Complete</p><h3>${pct(a.trace_completeness)}</h3></div>
      <div class="callout"><p class="stat-label">Redaction Pass</p><h3>${pct(a.redaction_pass_rate)}</h3></div>
    </div>`;
  const categoryRows = Object.entries(a.category_summary)
    .map(([category, row]) => `
      <tr>
        <td>${category}</td>
        <td>${row.scenario_count}</td>
        <td>${row.decision_count}</td>
        <td>${pct(row.gate_accuracy)}</td>
      </tr>`)
    .join("");
  const scenarioRows = a.details
    .map((row) => `
      <tr>
        <td>${row.scenario_id}</td>
        <td>${row.category}</td>
        <td><code>${row.prompt_hash}</code></td>
        <td>${gateList(row.actual_gates)}</td>
        <td>${passList(row.redaction_pass_by_profile)}</td>
      </tr>`)
    .join("");
  const standards = state.report.reviewer_standard
    .map((item) => `
      <article class="standard-card">
        <p class="stat-label">${item.principle}</p>
        <p>${item.evidence}</p>
      </article>`)
    .join("");
  document.querySelector("#adversarial").innerHTML = `
    <h2>Adversarial Evidence</h2>
    <p class="small">${a.public_export_rule}</p>
    ${metricCards}
    <h3 class="section-kicker">Reviewer standard</h3>
    <div class="standard-grid">${standards}</div>
    <h3 class="section-kicker">Category summary</h3>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Category</th><th>Scenarios</th><th>Decisions</th><th>Gate Accuracy</th></tr></thead>
        <tbody>${categoryRows}</tbody>
      </table>
    </div>
    <h3 class="section-kicker">Scenario evidence</h3>
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Category</th><th>Prompt Hash</th><th>Gates</th><th>Redaction</th></tr></thead>
        <tbody>${scenarioRows}</tbody>
      </table>
    </div>`;
}

function renderExport() {
  document.querySelector("#export").innerHTML = `
    <h2>Evidence Export</h2>
    <p class="small">Combined public evidence payload. Source and candidate content are not included.</p>
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

function gateList(gates) {
  return Object.entries(gates)
    .map(([profile, gate]) => `<span class="gate">${profile}: ${gate}</span>`)
    .join(" ");
}

function passList(values) {
  return Object.entries(values)
    .map(([profile, pass]) => {
      const cls = pass ? "pass-pill" : "fail-pill";
      const label = pass ? "pass" : "fail";
      return `<span class="${cls}">${profile}: ${label}</span>`;
    })
    .join(" ");
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function main() {
  wireTabs();
  [state.summary, state.demo, state.report, state.exportPayload] = await Promise.all([
    fetchJson("/evidence/summary"),
    fetchJson("/evidence/demo"),
    fetchJson("/evidence/report"),
    fetchJson("/evidence/export"),
  ]);
  setHeadlineMetrics(state.summary);
  renderOverview();
  renderGuidedDemo();
  renderEnvelope();
  renderAccuracy();
  renderSeparation();
  renderTrace();
  renderConformance();
  renderBaseline();
  renderViewer();
  renderAdversarial();
  renderExport();
  activateTab(tabFromHash(), false);
}

main().catch((error) => {
  document.querySelector("#overview").innerHTML = `<h2>Load Error</h2><pre>${escapeHtml(String(error))}</pre>`;
});
