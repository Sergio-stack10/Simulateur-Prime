# -*- coding: utf-8 -*-
"""
SimuPrime v2 — auth par rôles, payplan éditable en BDD,
historique des simulations isolé par session.
"""
import os
import re
import uuid
import secrets
from datetime import date, datetime, timezone
from functools import wraps

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session

from db import get_db, get_payplan, save_payplan, reset_payplan
from payplan_config import calculate_prime
from db import (get_db, get_payplan, save_payplan, reset_payplan,
                get_ref_msa, save_ref_msa, reset_ref_msa)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or os.environ.get("ADMIN_TOKEN") or ""

# ------------------------------------------------------------------ Helpers
SITE_KEYWORDS = {"ANTA": ("antananarivo", "tana"), "TMM": ("tamatave", "toamasina")}
TECH_PATTERN = re.compile(
    r"d[ée]veloppeur|ing[ée]nieur|\bdev\b|technicien|informatique|"
    r"administrateur base|database|\bdata\b|\bbi\b|network|\bnoc\b|software", re.I)

def now_utc():
    return datetime.now(timezone.utc)

def _norm_mat(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") else s

def _clean(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()
    return "" if s.lower() in {"nan", "none"} else s

def derive_site(location: str) -> str:
    loc = (location or "").lower()
    for code, kw in SITE_KEYWORDS.items():
        if any(k in loc for k in kw):
            return code
    return "AUTRE"

def derive_typo(title: str) -> str:
    return "TECH" if TECH_PATTERN.search(title or "") else "OPS"

def extract_activity_code(activity_full: str) -> str:
    """'W0ZQPJ Orange At Hd - Antananarivo' -> 'W0ZQPJ'."""
    s = str(activity_full or "").strip()
    return s.split()[0].upper() if s else ""

def extract_msa_code(msa_full: str) -> str:
    """'16152 - Orange - WHFR1006' -> 'WHFR1006'."""
    s = str(msa_full or "").strip()
    if not s:
        return ""
    parts = [p.strip() for p in s.split(" - ")]
    return parts[-1] if parts and parts[-1] else s

def parse_hire_date(value):
    if value is None:
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, float) and pd.isna(value):
        return None
    try:
        return pd.to_datetime(str(value).strip()).date()
    except Exception:
        return None

# -------------------------------------------------------------------- Auth
def current_user():
    if session.get("role") in ("user", "admin"):
        return {"role": session["role"], "sid": session.get("sid", "")}
    return None

def _unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Session expirée — reconnectez-vous."}), 401
    return redirect("/login")

def _forbidden():
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Accès réservé à l'administrateur."}), 403
    return redirect("/")

def login_required(f):
    @wraps(f)
    def wrapper(*a, **k):
        if not current_user():
            return _unauthorized()
        return f(*a, **k)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*a, **k):
        u = current_user()
        if not u:
            return _unauthorized()
        if u["role"] != "admin":
            return _forbidden()
        return f(*a, **k)
    return wrapper

# ------------------------------------------------------------------- Pages
@app.route("/login")
def login_page():
    u = current_user()
    if u:
        return redirect("/admin" if u["role"] == "admin" else "/")
    return render_template("login.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html", role=session["role"])

@app.route("/admin")
@admin_required
def admin_page():
    return render_template("admin.html", role="admin")

# ----------------------------------------------------------------- Auth API
@app.post("/api/auth/login")
def auth_login():
    d = request.get_json(silent=True) or {}
    role = d.get("role")
    if role == "user":
        session.clear()
        session.update(role="user", sid=uuid.uuid4().hex, logged_at=now_utc().isoformat())
        return jsonify({"ok": True, "redirect": "/"})
    if role == "admin":
        if not ADMIN_PASSWORD:
            return jsonify({"ok": False, "error": "Mot de passe admin non configuré "
                            "(variable ADMIN_PASSWORD)."}), 503
        if str(d.get("password") or "") != ADMIN_PASSWORD:
            return jsonify({"ok": False, "error": "Mot de passe incorrect."}), 401
        session.clear()
        session.update(role="admin", sid=uuid.uuid4().hex, logged_at=now_utc().isoformat())
        return jsonify({"ok": True, "redirect": "/admin"})
    return jsonify({"ok": False, "error": "Rôle invalide."}), 400

@app.post("/api/auth/logout")
def auth_logout():
    session.clear()
    return jsonify({"ok": True})

@app.get("/api/auth/me")
def auth_me():
    u = current_user()
    return jsonify({"ok": bool(u), "user": u})

# ------------------------------------------------------------------- Public
@app.route("/api/health")
def health():
    try:
        get_db().command("ping")
        db_status = "connected"
    except Exception:
        db_status = "error"
    return jsonify({"ok": True, "db": db_status})

# ------------------------------------------------------------------ Payplan
@app.get("/api/payplan")
@login_required
def api_payplan_get():
    profils, regles = get_payplan()
    return jsonify({"ok": True, "profils": profils, "regles": regles})

@app.put("/api/payplan")
@admin_required
def api_payplan_put():
    d = request.get_json(silent=True) or {}
    try:
        profils = _validate_profils(d.get("profils"))
        regles = _validate_regles(d.get("regles"))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    save_payplan(profils, regles)
    profils, regles = get_payplan()
    return jsonify({"ok": True, "message": "Payplan enregistré.",
                    "profils": profils, "regles": regles})

@app.post("/api/payplan/reset")
@admin_required
def api_payplan_reset():
    reset_payplan()
    profils, regles = get_payplan()
    return jsonify({"ok": True, "message": "Payplan réinitialisé depuis payplan_config.py.",
                    "profils": profils, "regles": regles})

def _validate_profils(p):
    if not isinstance(p, dict) or not p:
        raise ValueError("Profils invalides.")
    out = {}
    for k, v in p.items():
        k = str(k).strip()
        if not k:
            raise ValueError("Nom de profil vide.")
        if v in (None, "", "null", "None"):
            out[k] = None          # « vide » (ex : Non évalué)
        else:
            try:
                v = int(v)
            except (TypeError, ValueError):
                raise ValueError(f"Points invalides pour « {k} ».")
            if not 0 <= v <= 20:
                raise ValueError(f"Points invalides pour « {k} » (0 à 20).")
            out[k] = v
    return out

def _val_date(v):
    v = str(v or "").strip()
    if not v or v.lower() in ("none", "null"):
        return None
    for f in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(v, f).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Date invalide : « {v} » (AAAA-MM-JJ)")

def _validate_regles(rs):
    if not isinstance(rs, list) or not rs:
        raise ValueError("Au moins une règle est requise.")
    out = []
    for i, r in enumerate(rs, 1):
        nom = str(r.get("nom") or f"Règle {i}").strip()
        try:
            sites = [s.strip().upper() for s in str(r.get("sites") or "").split(",") if s.strip()]
            msa = [m.strip().upper() for m in str(r.get("msa") or "").split(",") if m.strip()]
            avant, apres = _val_date(r.get("embauche_avant")), _val_date(r.get("embauche_apres"))
            try:
                index = int(r.get("index") or i * 10)
            except (TypeError, ValueError):
                index = i * 10
            amin = int(r.get("anciennete_min") or 0)
            raw_max = r.get("anciennete_max")
            amax = int(raw_max) if raw_max not in (None, "", "null") else None
            nb = int(r.get("nb_mois_profil") or 3)
            if not 1 <= nb <= 3:
                raise ValueError("nb_mois_profil doit être 1, 2 ou 3")
            montants = {int(k): int(v) for k, v in dict(r.get("montants") or {}).items()}
            if not montants:
                raise ValueError("aucun montant défini")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Règle « {nom} » invalide : {e}")
        if amax is not None and amin > amax:
            raise ValueError(f"Règle « {nom} » : ancienneté min > max")
        out.append({"nom": nom, "sites": sites, "msa": msa,
                    "embauche_avant": avant, "embauche_apres": apres, "index": index,
                    "anciennete_min": amin, "anciennete_max": amax,
                    "nb_mois_profil": nb, "montants": montants,
                    "explication": str(r.get("explication") or "")})
    return out

# ----------------------------------------------------------------- Employee
@app.route("/api/employee/<matricule>")
@login_required
def api_employee(matricule: str):
    mat = _norm_mat(matricule).upper()
    e = get_db().employees.find_one({"$or": [{"mat_wkd": mat}, {"mat_paie": mat}]})
    if not e:
        return jsonify({"ok": False, "error": f"Matricule « {matricule} » introuvable "
                        "dans l'extraction ACTIF."}), 404
    e.pop("_id", None)
    e.setdefault("msa_code", extract_msa_code(e.get("msa")))
    e.setdefault("projet_code", extract_activity_code(e.get("projet")))
    return jsonify({"ok": True, "data": e})

@app.get("/api/ref-msa")
@login_required
def api_ref_msa_get():
    return jsonify({"ok": True, "data": get_ref_msa()})

@app.put("/api/ref-msa")
@admin_required
def api_ref_msa_put():
    d = request.get_json(silent=True) or {}
    rows = d.get("rows")
    if not isinstance(rows, list) or not rows:
        return jsonify({"ok": False, "error": "Au moins une ligne requise."}), 400
    clean, seen = [], set()
    for i, r in enumerate(rows, 1):
        aid = str(r.get("id") or "").strip().upper()
        msa = str(r.get("msa") or "").strip().upper()
        lib = str(r.get("libelle") or "").strip()
        if not aid or not msa:
            return jsonify({"ok": False, "error": f"Ligne {i} : ID activité et MSA requis."}), 400
        if aid in seen:
            return jsonify({"ok": False, "error": f"Ligne {i} : ID « {aid} » en double."}), 400
        seen.add(aid)
        clean.append({"id": aid, "msa": msa, "libelle": lib})
    save_ref_msa(clean)
    return jsonify({"ok": True, "message": f"Référentiel enregistré : {len(clean)} lignes.",
                    "data": clean})

@app.post("/api/ref-msa/reset")
@admin_required
def api_ref_msa_reset():
    reset_ref_msa()
    return jsonify({"ok": True, "message": "Référentiel réinitialisé.",
                    "data": get_ref_msa()})

@app.post("/api/ref-msa/upload")
@admin_required
def api_ref_msa_upload():
    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"ok": False, "error": "Aucun fichier reçu."}), 400
    try:
        df = pd.read_excel(file, sheet_name=0)
    except Exception as exc:
        return jsonify({"ok": False, "error": f"Fichier illisible : {exc}"}), 400

    def norm(c):
        return (str(c).strip().lower()
                .replace("é", "e").replace("è", "e").replace("ê", "e")
                .replace(" ", "").replace("-", "").replace("_", ""))
    cols = {norm(c): c for c in df.columns}
    def find(*cands):
        for cand in cands:
            if cand in cols:
                return cols[cand]
        return None

    c_cpsa = find("cpsa", "msa")
    c_act  = find("activites", "activite", "libelle", "libelleactivite")
    c_id   = find("idactivite", "idactivites", "id", "activiteid")
    if not (c_cpsa and c_act and c_id):
        return jsonify({"ok": False, "error": "Colonnes attendues : CPSA · Activités · ID activité"}), 400

    rows, seen = [], set()
    for _, r in df.iterrows():
        aid = _clean(r.get(c_id)).upper()
        msa = _clean(r.get(c_cpsa)).upper()
        lib = _clean(r.get(c_act))
        if not aid or not msa or aid in seen:
            continue
        seen.add(aid)
        rows.append({"id": aid, "msa": msa, "libelle": lib})
    if not rows:
        return jsonify({"ok": False, "error": "Aucune ligne valide (ID et CPSA requis)."}), 400
    save_ref_msa(rows)
    return jsonify({"ok": True, "message": f"Référentiel importé : {len(rows)} lignes.",
                    "data": rows})

# ---------------------------------------------------------------- Calculate
@app.post("/api/calculate")
@login_required
def api_calculate():
    p = request.get_json(silent=True) or {}
    profils, regles = get_payplan()
    hire_raw = str(p.get("hire_date") or "").strip()
    site = str(p.get("site") or "").strip().upper()
    ref_raw = str(p.get("reference_date") or "").strip()
    activites = p.get("activites") or []

    if not hire_raw:
        return jsonify({"ok": False, "error": "La date d'embauche est obligatoire."}), 400
    try:
        hire_date = date.fromisoformat(hire_raw)
    except ValueError:
        return jsonify({"ok": False, "error": "Date d'embauche invalide."}), 400
    if not site:
        return jsonify({"ok": False, "error": "Le site est obligatoire."}), 400
    if not isinstance(activites, list) or not 1 <= len(activites) <= 7:
        return jsonify({"ok": False, "error": "Renseignez entre 1 et 7 activités."}), 400
    try:
        reference_date = date.fromisoformat(ref_raw) if ref_raw else date.today()
    except ValueError:
        return jsonify({"ok": False, "error": "Date de référence invalide."}), 400

    ref_msa = {r["id"]: r["msa"] for r in get_ref_msa()}
    clean = []
    for i, a in enumerate(activites, 1):
        activity_id = str(a.get("activity_id") or "").strip().upper()
        profiles = a.get("profiles") or []
        try:
            heures = float(a.get("heures") or 0)
        except (TypeError, ValueError):
            heures = 0.0
        if not activity_id:
            return jsonify({"ok": False, "error": f"Activité {i} : ID d'activité manquant."}), 400
        if heures <= 0:
            return jsonify({"ok": False, "error": f"Activité {i} : heures > 0 requises."}), 400
        if len(profiles) != 3 or any(x not in profils for x in profiles):
            return jsonify({"ok": False, "error": f"Activité {i} : 3 profils attendus parmi : "
                            + ", ".join(profils) + "."}), 400
        msa = ref_msa.get(activity_id)
        if not msa:
            return jsonify({"ok": False, "error": f"Activité {i} : ID « {activity_id} » absent "
                            "du référentiel (voir panneau Admin)."}), 400
        clean.append({"activity_id": activity_id, "msa": msa,
                      "heures": heures, "profiles": profiles})

    result = calculate_prime(hire_date, site, clean, reference_date, profils, regles)

    u = current_user()
    matricule = str(p.get("matricule") or "").strip()
    emp = (get_db().employees.find_one({"mat_wkd": _norm_mat(matricule).upper()}, {"nom": 1})
           if matricule else None)
    record = dict(result, matricule=matricule, site=site, nom=(emp or {}).get("nom"),
                  sid=u["sid"], role=u["role"], created_at=now_utc())
    try:
        get_db().simulations.insert_one(record)
    except Exception:
        pass
    return jsonify({"ok": True, "data": result})

# ------------------------------------------------------------- Simulations
@app.get("/api/simulations")
@login_required
def api_simulations():
    u = current_user()
    scope = request.args.get("scope", "mine")
    try:
        limit = min(int(request.args.get("limit", 20)), 200)
    except ValueError:
        limit = 20
    q = {} if (u["role"] == "admin" and scope == "all") else {"sid": u["sid"]}
    cur = get_db().simulations.find(q, {"_id": 0}).sort("created_at", -1).limit(limit)
    return jsonify({"ok": True, "data": list(cur)})

# ------------------------------------------------------------------- Upload
@app.route("/api/upload", methods=["POST"])
@admin_required
def api_upload():
    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"ok": False, "error": "Aucun fichier reçu."}), 400
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        return jsonify({"ok": False, "error": "Format attendu : Excel (.xlsx/.xls)."}), 400
    try:
        df = pd.read_excel(file, sheet_name=0)
    except Exception as exc:
        return jsonify({"ok": False, "error": f"Fichier illisible : {exc}"}), 400

    df.columns = [str(c).strip() for c in df.columns]
    required = {"Employee ID", "Hire Date", "Location", "Activity ID", "Business Title"}
    if not required.issubset(set(df.columns)):
        return jsonify({"ok": False, "error": "Colonnes manquantes : "
                        + ", ".join(sorted(required - set(df.columns)))}), 400

    docs = []
    for _, r in df.iterrows():
        mat = _norm_mat(r.get("Employee ID"))
        if not mat:
            continue
        poste = _clean(r.get("Business Title"))
        location = _clean(r.get("Location"))
        hire = parse_hire_date(r.get("Hire Date"))
        docs.append({
            "mat_wkd": mat,
            "mat_paie": (_norm_mat(r.get("Previous Payroll ID")).upper()
                         if "Previous Payroll ID" in df.columns else ""),
            "nom": f"{_clean(r.get('First Name'))} {_clean(r.get('Last Name'))}".strip(),
            "poste": poste, "typo": derive_typo(poste), "location": location,
            "site": derive_site(location), "projet": _clean(r.get("Activity ID")),
            "msa": _clean(r.get("MSA")) if "MSA" in df.columns else "",
            "statut_wkd": "ACTIVE",
            "hire_date": hire.isoformat() if hire else None,
            "msa_code": extract_msa_code(_clean(r.get("MSA")) if "MSA" in df.columns else ""),
            "projet_code": extract_activity_code(_clean(r.get("Activity ID"))),
        })

    db = get_db()
    db.employees.delete_many({})
    if docs:
        db.employees.insert_many(docs)
    db.meta.replace_one({"_id": "actif"},
                        {"_id": "actif", "count": len(docs), "updated_at": now_utc()},
                        upsert=True)
    return jsonify({"ok": True,
                    "message": f"Extraction ACTIF enregistrée : {len(docs)} collaborateurs."})

# -------------------------------------------------------------------- Stats
@app.get("/api/stats")
@admin_required
def api_stats():
    db = get_db()
    try:
        db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "error"
    meta = db.meta.find_one({"_id": "actif"}) or {}
    pp = db.payplan.find_one({"_id": "active"}) or {}
    return jsonify({"ok": True, "data": {
        "employees": db.employees.count_documents({}),
        "simulations": db.simulations.count_documents({}),
        "db": db_status,
        "actif_updated_at": meta.get("updated_at"),
        "payplan_updated_at": pp.get("updated_at"),
    }})

if __name__ == "__main__":
    app.run(debug=True)
