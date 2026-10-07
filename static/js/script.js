/* SimuPrime — page utilisateur */
const $ = (s) => document.querySelector(s);
const fmt = new Intl.NumberFormat("fr-FR");
const PP = { profils: {}, regles: [] };
let employee = null;

function esc(s) {
  return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

async function api(url, opts = {}) {
  const res = await fetch(url, opts);
  if (res.status === 401) { location.href = "/login"; throw new Error("401"); }
  const ct = res.headers.get("content-type") || "";
  const j = ct.includes("json") ? await res.json() : { ok: false, error: "Réponse invalide" };
  if (res.status === 403) { toast(j.error || "Accès refusé", "error"); throw new Error("403"); }
  return j;
}

function toast(msg, type = "info") {
  const t = document.createElement("div");
  t.className = "toast " + type; t.textContent = msg;
  $("#toasts").appendChild(t);
  setTimeout(() => { t.style.opacity = "0"; setTimeout(() => t.remove(), 300); }, 3800);
}

function countUp(el, target, { dur = 900, suffix = "" } = {}) {
  const t0 = performance.now();
  (function f(t) {
    const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
    el.textContent = fmt.format(Math.round(target * e)) + suffix;
    if (p < 1) requestAnimationFrame(f);
  })(t0);
}

document.addEventListener("DOMContentLoaded", async () => {
  $("#reference-date").value = new Date().toISOString().slice(0, 10);
  $("#btn-search").onclick = searchEmployee;
  $("#matricule").addEventListener("keydown", (e) => { if (e.key === "Enter") searchEmployee(); });
  $("#btn-calculate").onclick = calculate;
  $("#btn-logout").onclick = logout;
  $("#btn-refresh-sims").onclick = loadMySims;
  await loadPayplan();
  await loadMySims();
});

async function logout() {
  try { await api("/api/auth/logout", { method: "POST" }); } catch (e) {}
  location.href = "/login";
}

async function loadPayplan() {
  try {
    const j = await api("/api/payplan");
    if (!j.ok) return;
    PP.profils = j.profils; PP.regles = j.regles;
    const opts = Object.entries(j.profils)
      .map(([l, p]) => `<option value="${esc(l)}">${esc(l)} · ${p} pt</option>`).join("");
    document.querySelectorAll("select.profile").forEach((s) =>
      s.innerHTML = `<option value="" disabled selected>Sélectionner…</option>${opts}`);
  } catch (e) { console.error(e); }
}

async function searchEmployee() {
  const mat = $("#matricule").value.trim(), box = $("#employee-result");
  if (!mat) { box.innerHTML = `<div class="alert warn">Veuillez saisir un matricule.</div>`; return; }
  box.innerHTML = `<p class="muted">⏳ Recherche…</p>`;
  try {
    const j = await api("/api/employee/" + encodeURIComponent(mat));
    if (!j.ok) { employee = null;
      box.innerHTML = `<div class="alert warn">${esc(j.error)}</div>`; return; }
    employee = j.data;
    box.innerHTML = renderEmployee(j.data);
    if (j.data.hire_date) $("#hire-date").value = j.data.hire_date;
    if (j.data.site) $("#site").value = j.data.site;
  } catch (e) { box.innerHTML = `<div class="alert error">Erreur réseau.</div>`; }
}

function renderEmployee(e) {
  const info = (label, value) => `
    <div class="emp-item">
      <span class="emp-label">${label}</span>
      <span class="emp-value">${esc(value || "—")}</span></div>`;
  return `
    <div class="employee-card">
      <div class="emp-head">
        <div><span class="emp-name">${esc(e.nom)}</span>
             <span class="muted"> · ${esc(e.poste)}</span></div>
        <span class="badge ok">${esc(e.statut_wkd)}</span>
      </div>
      <div class="emp-grid">
        ${info("Matricule WKD", e.matricule)}${info("N° paie", e.matricule_paie)}
        ${info("Typo", e.typo)}${info("Site (payplan)", e.site)}
        ${info("Location", e.location)}${info("Projet", e.projet)}
        ${info("MSA", e.msa)}${info("Date d'embauche", e.hire_date)}
      </div>
    </div>`;
}

async function calculate() {
  const profiles = [...document.querySelectorAll("select.profile")].map((s) => s.value);
  const hireDate = $("#hire-date").value, site = $("#site").value;
  const referenceDate = $("#reference-date").value;
  const missing = [];
  if (!hireDate) missing.push("date d'embauche");
  if (profiles.some((p) => !p)) missing.push("les 3 profils");
  if (missing.length) { toast("Champs manquants : " + missing.join(", "), "error"); return; }

  const btn = $("#btn-calculate");
  btn.classList.add("loading"); btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Calcul…';
  try {
    const j = await api("/api/calculate", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        matricule: employee ? employee.matricule : $("#matricule").value.trim(),
        hire_date: hireDate, site, profiles,
        reference_date: referenceDate || null }) });
    if (!j.ok) { toast(j.error, "error"); return; }
    renderResult(j.data);
    await loadMySims();
  } catch (e) { toast("Erreur réseau.", "error"); }
  finally { btn.classList.remove("loading"); btn.disabled = false;
            btn.innerHTML = "✨ Calculer ma prime"; }
}

function renderResult(d) {
  const card = $("#result-card"); card.hidden = false;
  const maxPts = Math.max(...Object.values(PP.profils), 1) * (d.nb_mois_profil || 3);
  const pct = Math.min(100, Math.round(d.total_points / maxPts * 100));
  const rows = (d.detail_points || []).map((p) => `
    <tr class="${p.pris_en_compte ? "" : "off"}">
      <td>${p.mois}</td><td>${esc(p.profil)}</td>
      <td class="center">${p.pris_en_compte ? p.points + " pt" : "non compté"}</td></tr>`).join("");
  const detail = `
    <div class="table-wrap"><table class="table">
      <thead><tr><th>Mois</th><th>Profil</th><th>Points retenus</th></tr></thead>
      <tbody>${rows}<tr class="total"><td colspan="2">Total</td>
        <td class="center">${d.total_points} pts</td></tr></tbody></table></div>
    <p class="muted small">Règle : <b>${esc(d.regle || "—")}</b> ·
      Ancienneté retenue : <b>${d.anciennete_mois} mois</b> (au ${d.date_reference})<br/>
      ${esc(d.explication || "")}</p>`;

  if (!d.eligible) {
    card.innerHTML = `<h2><span class="chip">3</span> Résultat</h2>
      <div class="alert warn">${esc(d.explication || "Non éligible.")}</div>${detail}`;
    card.scrollIntoView({ behavior: "smooth" }); return;
  }
  card.innerHTML = `
    <h2><span class="chip">3</span> Résultat de la simulation</h2>
    <div class="results">
      <div class="result-box">
        <span class="result-label">Cumul de points</span>
        <span class="result-value" id="rv-points">0</span>
        <div class="gauge"><div class="gauge-fill" id="gauge"></div></div>
        <span class="result-sub">sur ${d.nb_mois_profil} mois · max ${maxPts} pts</span>
      </div>
      <div class="result-box highlight">
        <span class="result-label">Prime estimée</span>
        <span class="result-value gold" id="rv-amount">0</span>
        <span class="result-sub">Ancienneté : ${d.anciennete_affichee} mois</span>
      </div>
    </div>${detail}`;
  card.scrollIntoView({ behavior: "smooth", block: "start" });
  requestAnimationFrame(() => {
    countUp($("#rv-points"), d.total_points, { suffix: " pts" });
    countUp($("#rv-amount"), d.montant_prime, { suffix: " Ar" });
    $("#gauge").style.width = pct + "%";
  });
}

async function loadMySims() {
  try {
    const j = await api("/api/simulations?scope=mine&limit=10");
    const rows = (j.data || []).map((r) => `
      <tr><td>${new Date(r.created_at).toLocaleString("fr-FR")}</td>
      <td>${esc(r.matricule || "—")}</td><td>${esc(r.site || "")}</td>
      <td>${(r.profiles || []).map(esc).join(" / ")}</td>
      <td class="center"><b>${r.total_points}</b></td>
      <td>${r.montant_prime != null ? fmt.format(r.montant_prime) + " Ar" : "—"}</td></tr>`).join("");
    $("#my-sims-body").innerHTML = rows ||
      `<tr><td colspan="6" class="muted center">Aucune simulation pour le moment.</td></tr>`;
  } catch (e) {}
}
