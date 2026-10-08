# -*- coding: utf-8 -*-
"""Connexion MongoDB + helpers payplan/référentiel (v6)."""
import os
from datetime import datetime, timezone

from pymongo import MongoClient

from payplan_config import PROFILE_POINTS as DEFAULT_PROFILE_POINTS
from payplan_config import PAYPLAN_RULES as DEFAULT_RULES
from payplan_config import REF_MSA_SEED

# ⚙️ Augmentez ces numéros pour FORCER la réinitialisation depuis payplan_config.py
PAYPLAN_VERSION = 6
REF_VERSION = 6

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        uri = os.environ.get("MONGODB_URI")
        if not uri:
            raise RuntimeError("Variable d'environnement MONGODB_URI manquante.")
        _client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        _db = _client.get_default_database("SIMULATEUR")
        _db.employees.create_index("mat_wkd")
        _db.employees.create_index("mat_paie")
        _db.simulations.create_index([("sid", 1), ("created_at", -1)])
        _db.simulations.create_index([("created_at", -1)])
    return _db

def _rules_to_db(rules):
    out = []
    for i, r in enumerate(rules):
        r = dict(r)
        r.setdefault("msa", [])
        r.setdefault("embauche_avant", None)
        r.setdefault("embauche_apres", None)
        r.setdefault("index", (i + 1) * 10)
        r.setdefault("explication", "")
        r["montants"] = {str(k): int(v) for k, v in r["montants"].items()}
        out.append(r)
    return out

def _rules_from_db(rules):
    out = []
    for i, r in enumerate(rules or []):
        r = dict(r)
        r.setdefault("msa", [])
        r.setdefault("embauche_avant", None)
        r.setdefault("embauche_apres", None)
        r.setdefault("index", (i + 1) * 10)
        r.setdefault("explication", "")
        r["montants"] = {int(k): int(v) for k, v in (r.get("montants") or {}).items()}
        out.append(r)
    return out

def get_payplan():
    """Payplan depuis la BDD. Si absent OU ancien format (version différente),
    réinitialisation AUTOMATIQUE depuis payplan_config.py → les règles par
    défaut (L1-L9) apparaissent sans rien cliquer."""
    db = get_db()
    doc = db.payplan.find_one({"_id": "active"})
    if not doc or doc.get("version") != PAYPLAN_VERSION:
        doc = {"_id": "active", "version": PAYPLAN_VERSION,
               "profils": dict(DEFAULT_PROFILE_POINTS),
               "regles": _rules_to_db(DEFAULT_RULES),
               "updated_at": datetime.now(timezone.utc)}
        db.payplan.replace_one({"_id": "active"}, doc, upsert=True)
    return dict(doc.get("profils") or {}), _rules_from_db(doc.get("regles"))

def save_payplan(profils, regles):
    db = get_db()
    db.payplan.replace_one(
        {"_id": "active"},
        {"_id": "active", "version": PAYPLAN_VERSION,
         "profils": profils, "regles": _rules_to_db(regles),
         "updated_at": datetime.now(timezone.utc)},
        upsert=True)

def reset_payplan():
    get_db().payplan.delete_one({"_id": "active"})

def get_ref_msa():
    db = get_db()
    doc = db.ref_msa.find_one({"_id": "active"})
    if not doc or doc.get("version") != REF_VERSION:
        doc = {"_id": "active", "version": REF_VERSION,
               "rows": [{"id": a, "msa": m, "libelle": l} for a, m, l in REF_MSA_SEED],
               "updated_at": datetime.now(timezone.utc)}
        db.ref_msa.replace_one({"_id": "active"}, doc, upsert=True)
    return doc.get("rows") or []

def save_ref_msa(rows):
    db = get_db()
    db.ref_msa.replace_one({"_id": "active"},
                           {"_id": "active", "version": REF_VERSION, "rows": rows,
                            "updated_at": datetime.now(timezone.utc)}, upsert=True)

def reset_ref_msa():
    get_db().ref_msa.delete_one({"_id": "active"})
