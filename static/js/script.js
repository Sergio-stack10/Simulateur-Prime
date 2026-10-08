/* ============================================================
   SimuPrime v7 — script.js COMPLET
   Profils complets · dégradation · bouton nouvelle simulation
   ============================================================ */
const $ = (s) => document.querySelector(s);
const fmt = new Intl.NumberFormat("fr-FR");
const PP = { profils: {}, regles: [] };
const REF = {};
let employee = null;
const MAX_ACT = 7;
let placeholderHTML = "";     // contenu d'attente de la carte résultat

/* ---------------- Utilitaires ---------------- */
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

/* ---------------- Initialisation ---------------- */
document.addEventListener("DOMContentLoaded", async () => {
  placeholderHTML = $("#result-card").innerHTML;   // mémorise l'écran d'attente

  $("#btn-search").onclick = searchEmployee;
  $("#matricule").addEventListener("keydown", (e) => { if (e.key === "Enter") searchEmployee(); });
  $("#btn-calculate").onclick = calculate;
  $("#btn-reset").onclick = resetAll;
  $("#btn-logout").onclick = logout;
  $("#btn-refresh-sims").onclick = loadMySims;
  $("#btn-clear-sims").onclick = clearMySims;
  $("#btn-add-act").onclick = () => addActivity();
  const eomBtn = $("#btn-eom");
  if (eomBtn) eomBtn.onclick = () => { endOfMonth(); toast("Date de référence : fin du mois courant."); };
  endOfMonth();
  await loadPayplan();
  await loadRef();
  addActivity();
  await loadMySims();
});

/* ---------------- Nouvelle simulation (tout effacer) ---------------- */
function resetAll() {
  if (!confirm("Effacer toutes les saisies pour commencer une nouvelle simulation ?")) return;
  employee = null;
  $("#matricule").value = "";
  $("#employee-result").innerHTML = "";
  $("#hire-date").value = "";
  $("#site").value = "ANTA";
  endOfMonth();
  $("#activites").innerHTML = "";
  addActivity();
  const card = $("#result-card");
  card.hidden = false;
  card.innerHTML = placeholderHTML;
  const ph = $("#ph-profils");
  if (ph) ph.innerHTML = Object.entries(PP.profils).map(([c, p]) =>
    `<span class="bchip">${esc(c)} · ${p === null ? "vide" : p + " pt"}</span>`).join("");
  window.scrollTo({ top: 0, behavior: "smooth" });
  toast("Formulaire réinitialisé — nouvelle simulation prête ✨", "success");
}

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
    const ph = $("#ph-profils");
    if (ph) ph.innerHTML = Object.entries(j.profils).map(([c, p]) =>
      `<span class="bchip">${esc(c)} · ${p === null ? "vide" : p + " pt"}</span>`).join("");
  } catch (e) { console.error(e); }
}
async function loadRef() {
  try {
    const j = await api("/api/ref-msa");
    if (!j.ok) return;
    const dl = $("#act-list");
    if (dl) dl.innerHTML = "";
    (j.data || []).forEach((r) => {
      REF[r.id] = { msa: r.msa, libelle: r.libelle || "" };
      if (dl) {
        const o = document.createElement("option");
        o.value = r.id; o.label = r.msa;
        dl.appendChild(o);
      }
    });
  } catch (e) { console.error(e); }
}
function profileOptionsHTML() {
  return `<option value="" disabled selected>Sélectionner…</option>` +
    Object.entries(PP.profils).map(([code, pts]) => {
      const val = (pts === null || pts === undefined) ? "vide" : pts + " pt";
      return `<option value="${esc(code)}">${esc(code)} · ${val}</option>`;
    }).join("");
}

/* ------------------ Activités ------------------ */
function addActivity(activityId = "") {
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
        <div class="field">
          <label>ID de l'activité *</label>
          <input class="a-act" list="act-list" placeholder="ex : W0ZRVV" value="${esc(activityId)}"/>
          <span class="msa-resolved" hidden><span class="dot"></span><span class="txt"></span></span>
        </div>
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

  const actInput = div.querySelector(".a-act");
  const resolve = () => {
    const v = actInput.value.trim().toUpperCase();
    const box = div.querySelector(".msa-resolved");
    if (!v) { box.hidden = true; }
    else if (REF[v]) {
      box.hidden = false; box.classList.remove("unknown");
      box.querySelector(".txt").textContent =
        "CPSA : " + REF[v].msa + (REF[v].libelle ? " · " + REF[v].libelle : "");
    } else {
      box.hidden = false; box.classList.add("unknown");
      box.querySelector(".txt").textContent = "ID inconnu — vérifiez le référentiel (Admin)";
    }
    refreshActs();
  };
  actInput.addEventListener("input", resolve);

  div.querySelector(".act-toggle").onclick = () => {
    div.classList.toggle("collapsed");
    div.querySelector(".act-toggle").textContent =
      div.classList.contains("collapsed") ? "▸" : "▾";
  };
  div.querySelector(".act-del").onclick = () => {
    if ($("#activites").children.length <= 1) { toast("Au moins une activité requise.", "error"); return; }
    div.remove(); refreshActs();
  };
  div.querySelector(".a-heures").addEventListener("input", refreshActs);
  cont.appendChild(div);
  resolve();
}

function refreshActs() {
  let total = 0;
  [...$("#activites").children].forEach((c, i) => {
    c.querySelector(".act-title").textContent = "Activité " + (i + 1);
    const id = c.querySelector(".a-act").value.trim().toUpperCase();
    const badge = c.querySelector(".a-badge");
    badge.textContent = id
      ? (REF[id] ? id + " → " + REF[id].msa : id + " ⚠")
      : "—";
    badge.title = REF[id] && REF[id].libelle ? REF[id].libelle : "";
    const h = parseFloat(c.querySelector(".a-heures").value);
    if (!isNaN(h)) total += h;
  });
  $("#act-count").textContent = $("#activites").children.length + " / " + MAX_ACT;
  $("#act-total-h").textContent = total > 0 ? "Heures totales : " + fmt.format(total) + " h" : "";
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
    if (first && !first.querySelector(".a-act").value && j.data.projet_code) {
      first.querySelector(".a-act").value = j.data.projet_code;
      first.querySelector(".a-act").dispatchEvent(new Event("input"));
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
        ${info("ID activité", e.projet_code)}${info("CPSA (code)", e.msa_code)}
        ${info("Projet", e.projet)}${info("Date d'embauche", e.hire_date)}
      </div>
    </div>`;
}

/* ------------------ Calcul ------------------ */
async function calculate() {
  const hireDate = $("#hire-date").value, site = $("#site").value;
  const referenceDate = $("#reference-date").value;
  const acts = [...$("#activites").children].map((c) => ({
    activity_id: c.querySelector(".a-act").value.trim().toUpperCase(),
    heures: parseFloat(c.querySelector(".a-heures").value),
    profiles: [".a-p1", ".a-p2", ".a-p3"].map((s) => c.querySelector(s).value),
  }));
  if (!hireDate) { toast("Date d'embauche manquante.", "error"); return; }
  for (let i = 0; i < acts.length; i++) {
    const n = i + 1;
    if (!acts[i].activity_id) { toast(`Activité ${n} : ID d'activité manquant.`, "error"); return; }
    if (!REF[acts[i].activity_id]) { toast(`Activité ${n} : ID inconnu dans le référentiel.`, "error"); return; }
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

/* ------------------ Résultat ------------------ */
function renderResult(d) {
  const card = $("#result-card");
  card.hidden = false;
  const acts = d.activites || [];

  const baremeChips = (a) => Object.entries(a.bareme || {}).sort((x, y) => x[0] - y[0])
    .map(([p, m]) => `<span class="bchip ${+p === a.total_points ? "hit" : ""}">
       ${p} pt → ${fmt.format(m)} Ar</span>`).join("");

  const conditions = (a) => {
    const i = a.regle_infos || {}, parts = [];
    if (i.sites && i.sites.length) parts.push("Site : " + i.sites.join(", "));
    if (i.msa && i.msa.length) parts.push("CPSA : " + i.msa.join(", "));
    if (i.embauche_avant) parts.push("Embauche avant le " + i.embauche_avant);
    if (i.embauche_apres) parts.push("Embauche à partir du " + i.embauche_apres);
    parts.push(`Ancienneté : ${i.anciennete_min != null ? i.anciennete_min : "?"}${i.anciennete_max != null ? " à " + i.anciennete_max : "+"} mois`);
    return parts.join(" · ");
  };

  const isDegraded = (a) => (a.detail_points || [])
    .some((p) => p.note && p.note.includes("dégradation"));

  const rows = acts.map((a) => `
    <tr class="${a.eligible ? "" : "off"}">
      <td><b>${esc(a.activity_id || "")}</b> → ${esc(a.msa)}
          ${REF[a.activity_id] && REF[a.activity_id].libelle ? `<br/><span class="muted small">${esc(REF[a.activity_id].libelle)}</span>` : ""}</td>
      <td class="center">${fmt.format(a.heures)} h</td>
      <td class="center">${a.part ?? 0}%</td>
      <td class="center"><b>${a.total_points}</b> pts${isDegraded(a) ? '<span class="deg-badge">⚠ dégradation</span>' : ""}</td>
      <td>${a.eligible ? fmt.format(a.montant) + " Ar" : "—"}</td>
      <td><b>${fmt.format(a.montant_proratise || 0)} Ar</b></td>
    </tr>`).join("");

  const details = acts.map((a, idx) => `
    <details class="rule-detail" ${idx === 0 ? "open" : ""}>
      <summary>${esc(a.activity_id || "")} — ${esc(a.msa)} ·
        <span class="muted">${esc(a.regle || "aucune règle")}</span></summary>
      <div class="rd-body">
        ${a.regle ? `
        <p class="small"><b>Conditions :</b> ${esc(conditions(a))}</p>
        <p class="small"><b>Mois comptés (${a.nb_mois_profil}) :</b>
          ${(a.detail_points || []).filter((p) => p.pris_en_compte)
            .map((p) => `${p.mois} : ${esc(p.profil)} (${p.note ? esc(p.note) : (p.points === null || p.points === undefined ? "vide" : p.points + " pt")})`).join(" · ")}</p>
        <div class="bareme-row">${baremeChips(a)}</div>
        ${a.eligible ? `<p class="small formula">Base ${fmt.format(a.montant)} Ar ×
          (${fmt.format(a.heures)} h ÷ ${fmt.format(d.total_heures)} h) =
          <b>${fmt.format(a.montant_proratise)} Ar</b></p>` : ""}` : ""}
      </div>
    </details>`).join("");

  card.innerHTML = `
    <h2><span class="chip">4</span> Résultat de la simulation
      <button class="btn btn-ghost btn-sm" style="margin-left:auto" onclick="resetAll()">🔄 Nouvelle simulation</button></h2>
    ${d.explication && !d.eligible ? `<div class="alert warn">${esc(d.explication)}</div>` : ""}
    <div class="results">
      <div class="result-box">
        <span class="result-label">Activités calculées</span>
        <span class="result-value">${acts.filter((a) => a.eligible).length}<small>/${acts.length}</small></span>
        <span class="result-sub">Heures totales : ${fmt.format(d.total_heures || 0)} h ·
          Ancienneté : ${d.anciennete_affichee} mois</span>
      </div>
      <div class="result-box highlight">
        <span class="result-label">Prime de régularité estimée</span>
        <span class="result-value gold" id="rv-amount">0</span>
        <span class="result-sub">Prorata selon les heures par activité</span>
      </div>
    </div>
    <div class="table-wrap"><table class="table">
      <thead><tr><th>Activité (ID → CPSA)</th><th>Heures</th><th>Part</th><th>Points</th>
        <th>Montant base</th><th>Montant proratisé</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
    <h3 class="pp-subtitle">Règles du payplan appliquées</h3>
    ${details}`;
  card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  requestAnimationFrame(() => countUp($("#rv-amount"), d.montant_prime || 0, { suffix: " Ar" }));
}

/* ------------------ Mes simulations ------------------ */
async function loadMySims() {
  try {
    const j = await api("/api/simulations?scope=mine&limit=10");
    const rows = (j.data || []).map((r) => {
      const acts = r.activites
        ? r.activites.map((a) => a.activity_id || a.msa).join(", ")
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
async function clearMySims() {
  if (!confirm("Supprimer toutes VOS simulations de cette session ?")) return;
  try {
    const j = await api("/api/simulations/mine", { method: "DELETE" });
    if (j.ok) { toast(j.message, "success"); await loadMySims(); }
  } catch (e) {}
}
