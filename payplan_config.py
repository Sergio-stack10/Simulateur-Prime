# -*- coding: utf-8 -*-
"""
=====================================================================
 PAYPLAN — PRIME DE RÉGULARITÉ (v8 · format PALIERS)
=====================================================================
 Format des montants : liste de paliers {min, max, montant}
   ex : [{"min": 0, "max": 2, "montant": 0}, {"min": 3, "max": 5, "montant": 90000}]
 Le montant applicable = le palier qui CONTIENT le total de points.

 ⚠️ MONTANTS D'EXEMPLE — à saisir via Admin → Payplan (ou option B).
 Seule ligne réelle lue sur votre image : TMM · Après · 4-6 mois · 0-2 pts → 0
=====================================================================
"""

PROFILE_POINTS = {
    "Leader": 3,
    "Fragile": 1,
    "Soutien Intense": 0,
    "Non évalué": None,
}

MIN_ANCIENNETE_MOIS = 4

# Dégradation : dernier mois en baisse → ses points non comptés (L-L-F → 6)
REGLE_DEGRADATION = True

PAYPLAN_RULES = [
    # ---- Liste MSA 1 : WHFR1135 et WHFR919 ----
    {"index": 1, "nom": "ANTA · Avant 01/06/2023 · WHFR1135 & WHFR919",
     "sites": ["ANTA"], "msa": ["WHFR1135", "WHFR919"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 3, "montant": 160000},
         {"min": 4, "max": 4, "montant": 170000},
         {"min": 5, "max": 5, "montant": 180000},
         {"min": 6, "max": 9, "montant": 185000},
     ],
     "explication": "Ligne 8 — embauchés avant le 01/06/2023 sur WHFR1135 / WHFR919."},

    # ---- Liste MSA 2 : 11 projets ----
    {"index": 2, "nom": "ANTA · Avant 01/06/2023 · Projets spécifiques (liste 2)",
     "sites": ["ANTA"],
     "msa": ["WHFR919", "WHFR1006", "WHFR1039", "WHFR1154", "WHFR1171", "WHFR218",
             "WHFR2749", "WHFR594", "WHFR907", "WHFR977", "WHFR1265"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 3, "montant": 150000},
         {"min": 4, "max": 4, "montant": 160000},
         {"min": 5, "max": 5, "montant": 170000},
         {"min": 6, "max": 9, "montant": 180000},
     ],
     "explication": "Ligne 9 — embauchés avant le 01/06/2023, projets de la liste 2."},

    # ---- TMM · Avant ----
    {"index": 10, "nom": "TMM · Avant 01/06/2023 · 4 à 6 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 3, "montant": 70000},
         {"min": 4, "max": 6, "montant": 100000},
     ],
     "explication": "Ligne 1 — 2 derniers mois."},
    {"index": 11, "nom": "TMM · Avant 01/06/2023 · 7 à 18 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 4, "montant": 125000},
         {"min": 5, "max": 6, "montant": 150000},
         {"min": 7, "max": 9, "montant": 170000},
     ],
     "explication": "Ligne 2 — 3 derniers mois."},
    {"index": 12, "nom": "TMM · Avant 01/06/2023 · 19 mois et +",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 4, "montant": 155000},
         {"min": 5, "max": 6, "montant": 172000},
         {"min": 7, "max": 9, "montant": 178000},
     ],
     "explication": "Ligne 3 — 3 derniers mois. ← votre « ligne 19 » ? (à confirmer)"},

    # ---- ANTA général · Avant ----
    {"index": 20, "nom": "ANTA · Avant 01/06/2023 · 4 à 6 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 3, "montant": 75000},
         {"min": 4, "max": 6, "montant": 105000},
     ],
     "explication": "Ligne 4 — 2 derniers mois."},
    {"index": 21, "nom": "ANTA · Avant 01/06/2023 · 7 à 18 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 4, "montant": 135000},
         {"min": 5, "max": 6, "montant": 160000},
         {"min": 7, "max": 9, "montant": 180000},
     ],
     "explication": "Ligne 5 — 3 derniers mois."},
    {"index": 22, "nom": "ANTA · Avant 01/06/2023 · 19 mois et +",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},
         {"min": 3, "max": 4, "montant": 165000},
         {"min": 5, "max": 6, "montant": 185000},
         {"min": 7, "max": 9, "montant": 195000},
     ],
     "explication": "Ligne 6 — 3 derniers mois."},

    # ---- TMM · Après (seule ligne réelle de votre image) ----
    {"index": 30, "nom": "TMM · Après 01/06/2023",
     "sites": ["TMM"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": [
         {"min": 0, "max": 2, "montant": 0},   # ← lu sur votre image ✓
         {"min": 3, "max": 3, "montant": 60000},
         {"min": 4, "max": 4, "montant": 70000},
         {"min": 5, "max": 6, "montant": 80000},
         {"min": 7, "max": 9, "montant": 90000},
     ],
     "explication": "Ligne 7 — embauchés à partir du 01/06/2023."},
]

REF_MSA_SEED = [
    ("W0ZVC5", "SITECSO", "Site CSO"),
    ("W0ZVBY", "CORPHQ", "Corp HQ"),
    ("W0ZQPJ", "WHFR1006", "Orange At Hd"),
    ("W0ZRVV", "WHFR2729", "DRM - FRAIS DE ROUTE"),
]

# =========================================================================
# LOGIQUE (ne pas modifier)
# =========================================================================
import calendar
from datetime import date

def months_between(start: date, end: date) -> int:
    if end < start:
        return 0
    m = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        m -= 1
    return max(0, m)

def anciennete_decimale(start: date, end: date) -> float:
    if end < start:
        return 0.0
    base = (end.year - start.year) * 12 + (end.month - start.month)
    dim = calendar.monthrange(end.year, end.month)[1]
    return round(max(0.0, base + (end.day - start.day) / dim), 1)

def _iso(d):
    if not d:
        return None
    try:
        return date.fromisoformat(str(d)[:10])
    except ValueError:
        return None

def somme_points_profils(profiles, nb_mois, profile_points):
    labels = ["M1", "M2", "M3"]
    retenus = profiles if nb_mois >= len(profiles) else profiles[-nb_mois:]
    offset = len(profiles) - len(retenus)
    detail = []

    def pts_of(p):
        v = profile_points.get(p) if p in profile_points else 0
        return 0 if v is None else v

    for j in range(offset):
        p = profiles[j]
        detail.append({"mois": labels[j], "profil": p,
                       "points": profile_points.get(p) if p in profile_points else 0,
                       "pris_en_compte": False, "note": "hors période"})

    counted = [pts_of(p) for p in retenus]
    degraded = (REGLE_DEGRADATION and len(counted) >= 2
                and counted[-1] < counted[-2])
    if degraded:
        counted[-1] = 0

    total = 0
    for i, p in enumerate(retenus):
        note = None
        if degraded and i == len(counted) - 1:
            note = "0 pt — dégradation"
        detail.append({"mois": labels[offset + i], "profil": p,
                       "points": profile_points.get(p) if p in profile_points else 0,
                       "pris_en_compte": True, "note": note})
        total += counted[i]
    return total, detail

def trouver_regle(regles, site, msa, anciennete_mois, hire_date):
    """Priorité : 1) règles avec CPSA spécifiques, 2) index croissant."""
    def cle(r):
        return (0 if (r.get("msa") or []) else 1, r.get("index", 999))
    for regle in sorted(regles, key=cle):
        if regle.get("sites") and site.upper() not in [s.upper() for s in regle["sites"]]:
            continue
        avant, apres = _iso(regle.get("embauche_avant")), _iso(regle.get("embauche_apres"))
        if avant and not hire_date < avant:
            continue
        if apres and not hire_date >= apres:
            continue
        liste = [str(m).strip().upper() for m in (regle.get("msa") or []) if str(m).strip()]
        if liste and str(msa or "").strip().upper() not in liste:
            continue
        if anciennete_mois < regle.get("anciennete_min", 0):
            continue
        amax = regle.get("anciennete_max")
        if amax is not None and anciennete_mois > amax:
            continue
        return regle
    return None

def _montant_for_points(paliers, points):
    """Retourne le montant du PALIER contenant les points (ex : 5 pts dans 4-6)."""
    for p in (paliers or []):
        try:
            if int(p["min"]) <= points <= int(p["max"]):
                return int(p["montant"])
        except (KeyError, TypeError, ValueError):
            continue
    return None

def calculate_activity(hire_date, site, msa, profiles, anciennete, profile_points, rules):
    res = {"msa": msa, "regle": None, "total_points": 0, "montant": None,
           "eligible": False, "explication": "", "detail_points": [], "nb_mois_profil": None}
    regle = trouver_regle(rules, site, msa, anciennete, hire_date)
    if regle is None:
        res["explication"] = f"Aucune règle (site {site}, CPSA {msa or '—'})."
        return res
    total, detail = somme_points_profils(profiles, regle["nb_mois_profil"], profile_points)
    paliers = regle["montants"]
    montant = _montant_for_points(paliers, total)
    res.update({"regle": regle["nom"], "nb_mois_profil": regle["nb_mois_profil"],
                "detail_points": detail, "total_points": total,
                "explication": regle.get("explication", ""),
                "bareme": paliers,
                "regle_infos": {
                    "sites": regle.get("sites") or [],
                    "msa": regle.get("msa") or [],
                    "embauche_avant": regle.get("embauche_avant"),
                    "embauche_apres": regle.get("embauche_apres"),
                    "anciennete_min": regle.get("anciennete_min", 0),
                    "anciennete_max": regle.get("anciennete_max"),
                }})
    if montant is None:
        res["explication"] += (f" | Aucun palier ne contient {total} pt "
                               f"dans « {regle['nom']} ».")
        return res
    res["eligible"] = True
    res["montant"] = montant
    return res

def calculate_prime(hire_date, site, activites, reference_date=None,
                    profile_points=None, rules=None):
    profile_points = profile_points if profile_points is not None else PROFILE_POINTS
    rules = rules if rules is not None else PAYPLAN_RULES
    reference_date = reference_date or date.today()
    anciennete = months_between(hire_date, reference_date)

    resultat = {"date_embauche": hire_date.isoformat(),
                "date_reference": reference_date.isoformat(),
                "anciennete_mois": anciennete,
                "anciennete_affichee": anciennete_decimale(hire_date, reference_date),
                "eligible": False, "montant_prime": 0, "explication": "",
                "activites": [], "total_heures": 0}
    if anciennete < MIN_ANCIENNETE_MOIS:
        resultat["explication"] = (f"Non éligible : ancienneté {anciennete} mois "
                                   f"(minimum {MIN_ANCIENNETE_MOIS} mois).")
        return resultat

    total_heures = sum(float(a.get("heures") or 0) for a in activites)
    if total_heures <= 0:
        resultat["explication"] = "Renseignez les heures travaillées par activité."
        return resultat
    resultat["total_heures"] = total_heures

    montant_final = 0
    for a in activites:
        h = float(a.get("heures") or 0)
        act = calculate_activity(hire_date, site, a.get("msa"), a.get("profiles") or [],
                                 anciennete, profile_points, rules)
        act["activity_id"] = a.get("activity_id")
        part = h / total_heures
        act["heures"] = h
        act["part"] = round(part * 100, 1)
        act["montant_proratise"] = round((act["montant"] or 0) * part) if act["eligible"] else 0
        montant_final += act["montant_proratise"]
        resultat["activites"].append(act)

    resultat["montant_prime"] = montant_final
    resultat["eligible"] = montant_final > 0
    return resultat
