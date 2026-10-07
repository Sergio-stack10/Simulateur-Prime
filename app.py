# -*- coding: utf-8 -*-
"""
SIMULATEUR DE PRIME DE RÉGULARITÉ — Backend (production, MongoDB Atlas)
"""
import os
import re
from datetime import date, datetime, timezone

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from db import get_db
from payplan_config import PAYPLAN_RULES, PROFILE_POINTS, calculate_prime

load_dotenv()  # charge .env en local uniquement (sur Render : dashboard)
app = Flask(__name__)

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")  # requis pour l'upload/historique

# ------------------------------------------------------------- Helpers
SITE_KEYWORDS = {"ANTA": ("antananarivo", "tana"), "TMM": ("tamatave", "toamasina")}
TECH_PATTERN = re.compile(
    r"d[ée]veloppeur|ing[ée]nieur|\bdev\b|technicien|informatique|"
    r"administrateur base|database|\bdata\b|\bbi\b|network|\bnoc\b|software", re.I)

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

def admin_ok(request) -> bool:
    """Protège les routes sensibles si ADMIN_TOKEN est configuré."""
    if not ADMIN_TOKEN:
        return True  # mode dev local
    token = (request.headers.get("X-Admin-Token", "")
             or request.args.get("token", "")
             or request.form.get("admin_token", ""))
    return token == ADMIN_TOKEN

# ------------------------------------------------------------- Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    """Endpoint léger pour UptimeRobot + diagnostic DB."""
    try:
        get_db().command("ping")
        db_status = "connected"
    except Exception:
        db_status = "error"
    return jsonify({"ok": True, "db": db_status})

@app.route("/api/payplan")
def api_payplan():
    return jsonify({"ok": True, "profils": PROFILE_POINTS, "regles": PAYPLAN_RULES})

@app.route("/api/employee/<matricule>")
def api_employee(matricule: str):
    mat = _norm_mat(matricule).upper()
    e = get_db().employees.find_one({"$or": [{"mat_wkd": mat}, {"mat_paie": mat}]})
    if not e:
        return jsonify({"ok": False, "error":
            f"Matricule « {matricule} » introuvable. L'extraction ACTIF est peut-être "
            f"vide — un administrateur doit la recharger."}), 404
    e.pop("_id", None)
    return jsonify({"ok": True, "data": e})

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    p = request.get_json(silent=True) or {}
    hire_raw = str(p.get("hire_date") or "").strip()
    site = str(p.get("site") or "").strip().upper()
    profiles = p.get("profiles") or []
    ref_raw = str(p.get("reference_date") or "").strip()

    if not hire_raw:
        return jsonify({"ok": False, "error": "La date d'embauche est obligatoire."}), 400
    try:
        hire_date = date.fromisoformat(hire_raw)
    except ValueError:
        return jsonify({"ok": False, "error": "Date d'embauche invalide."}), 400
    if not site:
        return jsonify({"ok": False, "error": "Le site est obligatoire."}), 400
    if (not isinstance(profiles, list) or len(profiles) != 3
            or any(x not in PROFILE_POINTS for x in profiles)):
        return jsonify({"ok": False, "error": "3 profils attendus parmi : "
                        + ", ".join(PROFILE_POINTS) + "."}), 400
    try:
        reference_date = date.fromisoformat(ref_raw) if ref_raw else date.today()
    except ValueError:
        return jsonify({"ok": False, "error": "Date de référence invalide."}), 400

    result = calculate_prime(hire_date, site, profiles, reference_date)

    # ---- Historisation de la simulation (bonus : traçabilité)
    matricule = str(p.get("matricule") or "").strip()
    emp = (get_db().employees.find_one({"mat_wkd": _norm_mat(matricule).upper()},
                                       {"nom": 1}) if matricule else None)
    record = dict(result, matricule=matricule, site=site, profiles=profiles,
                  nom=emp.get("nom") if emp else None,
                  created_at=datetime.now(timezone.utc))
    try:
        get_db().simulations.insert_one(record)
    except Exception:
        pass  # le calcul doit aboutir même si l'historique échoue

    return jsonify({"ok": True, "data": result})

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if not admin_ok(request):
        return jsonify({"ok": False, "error": "Token administrateur requis."}), 401
    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"ok": False, "error": "Aucun fichier reçu."}), 400
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        return jsonify({"ok": False, "error": "Format attendu : Excel."}), 400
    try:
        df = pd.read_excel(file, sheet_name=0)
    except Exception as exc:
        return jsonify({"ok": False, "error": f"Fichier illisible : {exc}"}), 400

    df.columns = [str(c).strip() for c in df.columns]
    required = {"Employee ID", "Hire Date", "Location", "Activity ID", "Business Title"}
    if not required.issubset(set(df.columns)):
        return jsonify({"ok": False, "error": "Colonnes manquantes : "
                        + ", ".join(sorted(required - set(df.columns)))}), 400

    # ⚠️ On ne stocke QUE les champs nécessaires — pas d'adresse/téléphone (RGPD-like)
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
            "poste": poste,
            "typo": derive_typo(poste),
            "location": location,
            "site": derive_site(location),
            "projet": _clean(r.get("Activity ID")),
            "msa": _clean(r.get("MSA")) if "MSA" in df.columns else "",
            "statut_wkd": "ACTIVE",
            "hire_date": hire.isoformat() if hire else None,
        })

    db = get_db()
    db.employees.delete_many({})
    db.employees.insert_many(docs)
    return jsonify({"ok": True,
                    "message": f"Extraction ACTIF enregistrée : {len(docs)} collaborateurs."})

@app.route("/api/simulations")
def api_simulations():
    """Historique des simulations (protégé par token admin)."""
    if not admin_ok(request):
        return jsonify({"ok": False, "error": "Token administrateur requis."}), 401
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
    except ValueError:
        limit = 20
    cur = get_db().simulations.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return jsonify({"ok": True, "data": list(cur)})

if __name__ == "__main__":
    app.run(debug=True)
