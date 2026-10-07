/* =========================================================================
   Simulateur Prime de Régularité — logique front
   ========================================================================= */
const $ = (sel) => document.querySelector(sel);
const fmtAr = new Intl.NumberFormat("fr-FR");
const state = { employee: null, profils: {}, regles: [] };

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
function alertBox(msg, type = "warn") {
  return `<div class="alert ${type}">${escapeHtml(msg)}</div>`;
}

document.addEventListener("DOMContentLoaded", async () => {
  $("#reference-date").value = new Date().toISOString().slice(0, 10);
  bindEvents();
  await loadPayplan();
});

function bindEvents() {
  $("#btn-search").addEventListener("click", searchEmployee);
  $("#matricule").addEventListener("keydown", (e) => { if (e.key === "Enter") searchEmployee(); });
  $("#btn-calculate").addEventListener("click", calculate);
  $("#btn-upload").addEventListener("click", uploadActif);
}

/* ------------------------------ Payplan ------------------------------ */
async function loadPayplan() {
  try {
    const res = await fetch("/api/payplan");
    const json = await res.json();
    if (!json.ok) return;
    state.profils = json.profils;
    state.regles = json.regles;
    fillProfileSelects();
    renderPayplanTable();
  } catch (e) { console.error("Chargement du payplan impossible", e); }
}

function fillProfileSelects() {
  const options = Object.entries(state.profils)
    .map(([label, pts]) =>
      `<option value="${escapeHtml(label)}">${escapeHtml(label)} — ${pts} pt</option>`)
    .join("");
  document.querySelectorAll("select.profile").forEach((sel) => {
    sel.innerHTML = `<option value="" disabled selected>Sélectionner…</option>${options}`;
  });
}

function renderPayplanTable() {
  const rows = state.regles.map((r) => {
    const bareme = Object.entries(r.montants)
      .sort((a, b) => Number(a[0]) - Number(b[0]))
      .map(([p, m]) => `<span class="bareme-item"><b>${p} pts</b> → ${fmtAr.format(m)} Ar</span>`)
      .join("");
    return `<tr>
      <td>${escapeHtml(r.nom)}</td>
      <td class="center">${r.nb_mois_profil}</td>
      <td><div class="bareme">${bareme}</div></td>
      <td class="muted">${escapeHtml(r.explication || "")}</td>
    </tr>`;
  }).join("");
  $("#payplan-table").innerHTML = `
    <table class="table">
      <thead><tr><th>Règle</th><th>Mois comptés</th><th>Barème points → montant</th><th>Explication</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

/* -------------------- Recherche collaborateur (ACTIF) ----------------- */
async function searchEmployee() {
  const mat = $("#matricule").value.trim();
  const box = $("#employee-result");
  if (!mat) { box.innerHTML = alertBox("Veuillez saisir un matricule WKD."); return; }
  box.innerHTML = `<div class="loading">⏳ Recherche dans l'extraction ACTIF…</div>`;
  try {
    const res = await fetch(`/api/employee/${encodeURIComponent(mat)}`);
    const json = await res.json();
    if (!json.ok) {
      state.employee = null;
      box.innerHTML = alertBox(json.error + " Vous pouvez saisir la date d'embauche et le site manuellement.");
      return;
    }
    state.employee = json.data;
    box.innerHTML = renderEmployee(json.data);
    if (json.data.hire_date) $("#hire-date").value = json.data.hire_date;
    if (json.data.site) $("#site").value = json.data.site;
  } catch (e) {
    box.innerHTML = alertBox("Erreur réseau — le serveur est-il démarré ?", "error");
  }
}

function renderEmployee(e) {
  const info = (label, value) => `
    <div class="emp-item">
      <span class="emp-label">${label}</span>
      <span class="emp-value">${escapeHtml(value || "—")}</span>
    </div>`;
  return `
    <div class="employee-card">
      <div class="emp-head">
        <div><span class="emp-name">${escapeHtml(e.nom)}</span>
             <span class="muted"> · ${escapeHtml(e.poste)}</span></div>
        <span class="badge ok">${escapeHtml(e.statut_wkd)}</span>
      </div>
      <div class="emp-grid">
        ${info("Matricule WKD", e.matricule)}
        ${info("N° paie", e.matricule_paie)}
        ${info("Typo", e.typo)}
        ${info("Site (payplan)", e.site)}
        ${info("Location", e.location)}
        ${info("Projet", e.projet)}
        ${info("MSA", e.msa)}
        ${info("Date d'embauche", e.hire_date)}
      </div>
    </div>`;
}

/* ------------------------------ Calcul ------------------------------- */
async function calculate() {
  const profiles = [...document.querySelectorAll("select.profile")].map((s) => s.value);
  const hireDate = $("#hire-date").value;
  const site = $("#site").value;
  const referenceDate = $("#reference-date").value;

  const missing = [];
  if (!hireDate) missing.push("la date d'embauche");
  if (profiles.some((p) => !p)) missing.push("les 3 profils (M1, M2, M3)");
  if (missing.length) { showResult(alertBox(`Champs manquants : ${missing.join(", ")}.`)); return; }

  const payload = {
    matricule: state.employee ? state.employee.matricule : $("#matricule").value.trim(),
    hire_date: hireDate,
    site: site,
    profiles: profiles,
    reference_date: referenceDate || null,
  };

  try {
    const res = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (!json.ok) { showResult(alertBox(json.error, "error")); return; }
    renderResult(json.data);
  } catch (e) {
    showResult(alertBox("Erreur réseau lors du calcul.", "error"));
  }
}

function showResult(html) {
  const card = $("#result-card");
  card.hidden = false;
  card.innerHTML = `<h2>3 · Résultat de la simulation</h2>${html}`;
  card.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderResult(d) {
  const hasDetail = Array.isArray(d.detail_points) && d.detail_points.length > 0;

  const rows = d.detail_points.map((p) => `
    <tr class="${p.pris_en_compte ? "" : "off"}">
      <td>${p.mois}</td>
      <td>${escapeHtml(p.profil)}</td>
      <td class="center">${p.pris_en_compte ? p.points + " pt" : "non compté"}</td>
    </tr>`).join("");

  const detail = hasDetail ? `
    <div class="detail-block">
      <h3>Détail du calcul</h3>
      <table class="table small">
        <thead><tr><th>Mois</th><th>Profil</th><th>Points retenus</th></tr></thead>
        <tbody>${rows}
          <tr class="total"><td colspan="2">Total</td>
              <td class="center">${d.total_points} pts</td></tr>
        </tbody>
      </table>
      <p class="muted small-text">
        Règle appliquée : <b>${escapeHtml(d.regle)}</b><br>
        Ancienneté retenue : <b>${d.anciennete_mois} mois</b> (au ${d.date_reference})<br>
        ${escapeHtml(d.explication || "")}
      </p>
    </div>` : "";

  if (!d.eligible) {
    showResult(alertBox(d.explication || "Non éligible.") + detail);
    return;
  }

  showResult(`
    <div class="results">
      <div class="result-box">
        <span class="result-label">Cumul de points</span>
        <span class="result-value">${d.total_points}<small> pts</small></span>
        <span class="result-sub">sur les ${d.nb_mois_profil} derniers mois</span>
      </div>
      <div class="result-box highlight">
        <span class="result-label">Prime estimée</span>
        <span class="result-value">${fmtAr.format(d.montant_prime)}<small> Ar</small></span>
        <span class="result-sub">Ancienneté : ${d.anciennete_affichee} mois</span>
      </div>
    </div>
    ${detail}`);
}

/* --------------------------- Upload ACTIF ---------------------------- */
async function uploadActif() {
  const input = $("#file-actif");
  const status = $("#upload-status");
  if (!input.files.length) { status.textContent = "Choisissez d'abord un fichier .xlsx"; return; }
  // Token admin (requis une fois l'outil déployé publiquement)
  const token = prompt("Token administrateur :") || "";
  const fd = new FormData();
  fd.append("file", input.files[0]);
  fd.append("admin_token", token);
  status.textContent = "⏳ Chargement…";
  try {
    const res = await fetch("/api/upload", { method: "POST", body: fd });
    const json = await res.json();
    status.textContent = json.ok ? "✅ " + json.message : "❌ " + json.error;
  } catch (e) { status.textContent = "❌ Erreur réseau"; }
}
