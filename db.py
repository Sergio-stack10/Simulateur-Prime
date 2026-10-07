# -*- coding: utf-8 -*-
"""Connexion MongoDB + helpers payplan (v2)."""
import os
from datetime import datetime, timezone

from pymongo import MongoClient

from payplan_config import PROFILE_POINTS as DEFAULT_PROFILE_POINTS
from payplan_config import PAYPLAN_RULES as DEFAULT_RULES

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
    for r in rules:
        r = dict(r)
        r["montants"] = {str(k): int(v) for k, v in r["montants"].items()}
        out.append(r)
    return out

def _rules_from_db(rules):
    out = []
    for r in rules or []:
        r = dict(r)
        r["montants"] = {int(k): int(v) for k, v in (r.get("montants") or {}).items()}
        out.append(r)
    return out

def get_payplan():
    """Payplan actif depuis la BDD ; seed depuis payplan_config.py au 1er accès."""
    db = get_db()
    doc = db.payplan.find_one({"_id": "active"})
    if not doc:
        doc = {"_id": "active", "profils": dict(DEFAULT_PROFILE_POINTS),
               "regles": _rules_to_db(DEFAULT_RULES),
               "updated_at": datetime.now(timezone.utc)}
        db.payplan.replace_one({"_id": "active"}, doc, upsert=True)
    return dict(doc.get("profils") or {}), _rules_from_db(doc.get("regles"))

def save_payplan(profils, regles):
    db = get_db()
    db.payplan.replace_one(
        {"_id": "active"},
        {"_id": "active", "profils": profils, "regles": _rules_to_db(regles),
         "updated_at": datetime.now(timezone.utc)},
        upsert=True)
