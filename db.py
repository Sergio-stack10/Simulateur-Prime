# -*- coding: utf-8 -*-
"""Connexion MongoDB + helpers (v10 — rechargement forcé du payplan)."""
import os
from datetime import datetime, timezone

from pymongo import MongoClient

from payplan_config import PROFILE_POINTS as DEFAULT_PROFILE_POINTS
from payplan_config import PAYPLAN_RULES as DEFAULT_RULES
from payplan_config import REF_MSA_SEED

PAYPLAN_VERSION = 10   # ⚠️ changez ce numéro pour forcer un rechargement du fichier
REF_VERSION = 6        # ne pas toucher (conserve votre référentiel importé)

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

def _norm_montants(m):
    if isinstance(m, dict):
        return sorted(({"min": int(k), "max": int(k), "montant": int(v)}
                       for k, v in m.items()), key=lambda x: x["min"])
    if isinstance(m, list):
        out = []
        for p in m:
            try:
                out.append({"min": int(p.get("min", 0)),
                            "max": int(p.get("max", p.get("min", 0))),
                            "montant": int(p.get("montant", 0))})
            except (TypeError, ValueError, AttributeError):
                continue
        return sorted(out, key=lambda x: x["min"])
    return []

def _rules_to_db(rules):
    out = []
    for i, r in enumerate(rules):
        r = dict(r)
        r.setdefault("msa", [])
        r.setdefault("embauche_avant", None)
        r.setdefault("embauche_apres", None)
        r.setdefault("index", (i + 1) * 10)
        r.setdefault("explication", "")
        r["montants"] = _norm_montants(r.get("montants"))
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
        r["montants"] = _norm_montants(r.get("montants"))
        out.append(r)
    return out

def get_payplan():
    db = get_db()
    doc = db.payplan.find_one({"_id": "active"})
    if doc and doc.get("version") == PAYPLAN_VERSION:
        return dict(doc.get("profils") or {}), _rules_from_db(doc.get("regles"))
    # Version différente ou absente → RECHARGEMENT COMPLET depuis le fichier.
    # (Les montants saisis via Admin → 💾 restent ensuite enregistrés.)
    db.payplan.replace_one(
        {"_id": "active"},
        {"_id": "active", "version": PAYPLAN_VERSION,
         "profils": dict(DEFAULT_PROFILE_POINTS),
         "regles": _rules_to_db(DEFAULT_RULES),
         "updated_at": datetime.now(timezone.utc)},
        upsert=True)
    return dict(DEFAULT_PROFILE_POINTS), _rules_from_db(DEFAULT_RULES)

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
