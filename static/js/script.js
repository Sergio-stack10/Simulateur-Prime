/* SimuPrime v3 — page utilisateur (multi-activités) */
const $ = (s) => document.querySelector(s);
const fmt = new Intl.NumberFormat("fr-FR");
const PP = { profils: {}, regles: [] };
let employee = null;
const MAX_ACT = 7;

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
  $("#btn-search").onclick = searchEmployee;
  $("#matricule").addEventListener("keydown", (e) => { if (e.key === "Enter") searchEmployee(); });
  $("#btn-calculate").onclick = calculate;
  $("#btn-logout").onclick = logout;
  $("#btn-refresh-sims").onclick = loadMySims;
  $("#btn-add-act").onclick = () => addActivity();
  $("#btn-eom").onclick = () => { endOfMonth(); toast("Date de référence : fin du mois courant."); };
  endOfMonth();   // défaut = fin du mois de performance
  await loadPayplan();
  await loadMsaList();
  addActivity();  // 1 activité par défaut
  await loadMySims();
});

function endOfMonth() {
  const n = new Date();
  $("#reference-date").value = new Date(n.getFullYear(), n.getMonth() + 1, 0)
    .toISOString().slice(0, 10);
}
async function logout() {
  try { await api("/api/auth/logout", { method: "POST" }); } catch (e) {}
  location.href = "/login";
}
async function loadPayplan() {
  try {
    const j = await api("/api/payplan");
    if (!j.ok) return;
    PP.profils = j.profils; PP.regles = j.regles;
  } catch (e) { console.error(e); }
}
async function loadMsaList() {
  try {
    const j = await api("/api/msas");
    if (j.ok) $("#msa-list").innerHTML =
      (j.data || []).map((c) => `<option value="${esc(c)}"></option>`).join("");
  } catch (e) {}
}
function profileOptionsHTML() {
  return `<option value="" disabled selected>Sélectionner…</option>` +
    Object.entries(PP.profils).map(([l, p]) =>
      `<option value="${esc(l)}">${esc(l)} · ${p} pt</option>`).join("");
}

/* ------------------ Activités ------------------ */
function addActivity(msa = "") {
  const cont = $("#activites");
  if (cont.children.length >= MAX_ACT) { toast(`Maximum ${MAX_ACT} activités.`, "error"); return; }
  const div = document.createElement("div");
  div.className = "act-card";
  div.innerHTML = `
    <div class="act-head">
      <button type="button" class="act-toggle" title="Replier/déplier">▾</button>
      <span class="act-title">Activité</span>
      <span class="badge a-badge">—</span>
      <button type="button" class="btn btn-danger btn-sm act-del" title="Supprimer">✕</button>
    </div>
    <div class="act-body">
      <div class="grid-act">
        <div class="field"><label>Projet (code MSA) *</label>
          <input class="a-msa" list="msa-list" placeholder="ex : WHFR1006" value="${esc(msa)}"/></div>
        <div class="field"><label>Heures sur l'activité *</label>
          <input class="a-heures" type="number" min="0" step="0.5" placeholder="ex : 105"/></div>
      </div>
      <div class="field"><label>Profils M1 → M3 *</label>
        <div class="profile-row">
          <select class="profile a-p1">${profileOptionsHTML()}</select>
          <select class="profile a-p2">${profileOptionsHTML()}</select>
          <select class="profile a-p3">${profileOptionsHTML()}</select>
        </div></div>
    </div>`;
  div.querySelector(".act-toggle").onclick = () => {
    div.classList.toggle("collapsed");
    div.querySelector(".act-toggle").textContent =
      div.classList.contains("collapsed") ? "▸" : "▾";
  };
  div.querySelector(".act-del").onclick = () => {
    if ($("#activites").children.length <= 1) { toast("Au moins une activité requise.", "error"); return; }
    div.remove(); refreshActs();
  };
  div.querySelector(".a-msa").addEventListener("input", refreshActs);
  div.querySelector(".a-heures").addEventListener("input", refreshActs);
  cont.appendChild(div);
  refreshActs();
}
function refreshActs() {
  let total = 0;
  [...$("#activites").children].forEach((c, i) => {
    c.querySelector(".act-title").textContent = "Activité " + (i + 1);
    const msa = c.querySelector(".a-msa").value.trim().toUpperCase();
    c.querySelector(".a-badge").textContent = msa || "—";
    const h = parseFloat(c.querySelector(".a-heures").value);
    if (!isNaN(h)) total += h;
  });
  $("#act-count").textContent = $("#activites").children.length + " / " + MAX_ACT;
  $("#act-total-h").textContent = total > 0 ? "Total : " + fmt.format(total) + " h" : "";
}

/* ------------------ Recherche ------------------ */
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
    const first = $("#activites").querySelector(".act-card");
    if (first && !first.querySelector(".a-msa").value && j.data.msa_code) {
      first.querySelector(".a-msa").value = j.data.msa_code;
      refreshActs();
    }
  } catch (e) { box.innerHTML = `<div class="alert error">Erreur réseau.</div>`; }
}
function renderEmployee(e) {
  const info = (label, value) => `
    <div class="emp-item"><span class="emp-label">${label}</span>
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
        ${info("MSA (code)", e.msa_code)}${info("Projet", e.projet)}
        ${info("MSA (libellé)", e.msa)}${info("Date d'embauche", e.hire_date)}
      </div>
    </div>`;
}

/* ------------------ Calcul ------------------ */
async function calculate() {
  const hireDate = $("#hire-date").value, site = $("#site").value;
  const referenceDate = $("#reference-date").value;
  const acts = [...$("#activites").children].map((c) => ({
    msa: c.querySelector(".a-msa").value.trim(),
    heures: parseFloat(c.querySelector(".a-heures").value),
    profiles: [".a-p1", ".a-p2", ".a-p3"].map((s) => c.querySelector(s).value),
  }));
  if (!hireDate) { toast("Date d'embauche manquante.", "error"); return; }
  for (let i = 0; i < acts.length; i++) {
    const n = i + 1;
    if (!acts[i].msa) { toast(`Activité ${n} : code MSA manquant.`, "error"); return; }
    if (!acts[i].heures || acts[i].heures <= 0) { toast(`Activité ${n} : heures > 0 requises.`, "error"); return; }
    if (acts[i].profiles.some((p) => !p)) { toast(`Activité ${n} : 3 profils requis.`, "error"); return; }
  }
  const btn = $("#btn-calculate");
  btn.classList.add("loading"); btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Calcul…';
  try {
    const j = await api("/api/calculate", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        matricule: employee ? employee.matricule : $("#matricule").value.trim(),
        hire_date: hireDate, site, reference_date: referenceDate || null,
        activites: acts }) });
    if (!j.ok) { toast(j.error, "error"); return; }
    renderResult(j.data);
    await loadMySims();
  } catch (e) { toast("Erreur réseau.", "error"); }
  finally { btn.classList.remove("loading"); btn.disabled = false;
            btn.innerHTML = "✨ Calculer ma prime"; }
}

function renderResult(d) {
  const card = $("#result-card"); card.hidden = false;
  const acts = d.activites || [];
  const maxPts = Math.max(...Object.values(PP.profils), 1);
  const rows = acts.map((a) => `
    <tr class="${a.eligible ? "" : "off"}">
      <td><b>${esc(a.msa)}</b><br/><span class="muted small">${esc(a.regle || a.explication || "—")}</span></td>
      <td class="center">${fmt.format(a.heures)} h</td>
      <td class="center">${a.part ?? 0}%</td>
      <td class="center"><b>${a.total_points}</b>/${(a.nb_mois_profil || 3) * maxPts}</td>
      <td>${a.eligible ? fmt.format(a.montant) + " Ar" : "0 Ar"}</td>
      <td><b>${fmt.format(a.montant_proratise || 0)} Ar</b></td>
    </tr>`).join("");
  card.innerHTML = `
    <h2><span class="chip">4</span> Résultat de la simulation</h2>
    ${d.explication && !d.eligible ? `<div class="alert warn">${esc(d.explication)}</div>` : ""}
    <div class="results">
      <div class="result-box">
        <span class="result-label">Activités calculées</span>
        <span class="result-value">${acts.filter((a) => a.eligible).length}<small>/${acts.length}</small></span>
        <span class="result-sub">Total : ${fmt.format(d.total_heures || 0)} h</span>
      </div>
      <div class="result-box highlight">
        <span class="result-label">Prime de régularité estimée</span>
        <span class="result-value gold" id="rv-amount">0</span>
        <span class="result-sub">Ancienneté : ${d.anciennete_affichee} mois · prorata heures</span>
      </div>
    </div>
    <div class="table-wrap"><table class="table">
      <thead><tr><th>Activité (MSA)</th><th>Heures</th><th>Part</th><th>Points</th>
        <th>Montant activité</th><th>Montant proratisé</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
    <details class="calc-details"><summary>Comment est calculé le prorata ?</summary>
      <p class="muted small">Prime finale = Σ (montant de l'activité × heures de l'activité ÷
      ${fmt.format(d.total_heures || 0)} h). Les activités sans règle applicable comptent pour
      0 Ar mais leurs heures entrent dans le prorata.</p></details>`;
  card.scrollIntoView({ behavior: "smooth", block: "start" });
  requestAnimationFrame(() => countUp($("#rv-amount"), d.montant_prime || 0, { suffix: " Ar" }));
}

async function loadMySims() {
  try {
    const j = await api("/api/simulations?scope=mine&limit=10");
    const rows = (j.data || []).map((r) => {
      const acts = r.activites ? r.activites.map((a) => a.msa).join(", ")
                               : (r.profiles || []).join(" / ");
      return `<tr><td>${new Date(r.created_at).toLocaleString("fr-FR")}</td>
        <td>${esc(r.matricule || "—")}</td><td>${esc(r.site || "")}</td>
        <td>${esc(acts || "—")}</td>
        <td>${r.montant_prime ? fmt.format(r.montant_prime) + " Ar" : "—"}</td></tr>`;
    }).join("");
    $("#my-sims-body").innerHTML = rows ||
      `<tr><td colspan="5" class="muted center">Aucune simulation pour le moment.</td></tr>`;
  } catch (e) {}
}
