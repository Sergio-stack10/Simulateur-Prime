# -*- coding: utf-8 -*-
"""Connexion MongoDB Atlas (singleton) — variables d'environnement uniquement."""
import os
from pymongo import MongoClient

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        uri = os.environ.get("MONGODB_URI")
        if not uri:
            raise RuntimeError("Variable d'environnement MONGODB_URI manquante.")
        _client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        # La base est définie dans l'URI (…/SIMULATEUR?…) ; sinon fallback :
        _db = _client.get_default_database("SIMULATEUR")
        # Index (créés une seule fois, accélèrent la recherche par matricule)
        _db.employees.create_index("mat_wkd")
        _db.employees.create_index("mat_paie")
        _db.simulations.create_index([("created_at", -1)])
    return _db
