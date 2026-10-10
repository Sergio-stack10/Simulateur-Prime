# -*- coding: utf-8 -*-
"""
=====================================================================
 PAYPLAN — PRIME DE RÉGULARITÉ (v12)
=====================================================================
 ⚠️ Les règles ci-dessous ne servent qu'au PREMIER démarrage (BDD vide).
 Votre payplan réel vit dans MongoDB (matrice importée via Admin).
=====================================================================
"""

PROFILE_POINTS = {
    "Leader": 3,
    "Challenger": 2,
    "Fragile": 1,
    "Care": 0,
    "Non évalué": None,     # None = vide : aucun point
}

MIN_ANCIENNETE_MOIS = 4

# Dernier mois compté en baisse → ses points ne sont pas comptés (L-L-F → 6)
REGLE_DEGRADATION = True

# Nouveaux intégrants (ancienneté 4 à 6 mois à la fin du mois de référence) :
# le profil du PREMIER mois (M1) n'est pas pris en compte — seuls les
# 2 derniers mois comptent, quelle que soit la règle du payplan.
REGLE_NOUVEAUX_4_6 = True

def _paliers(*triplets):
    return [{"min": a, "max": b, "montant": m} for a, b, m in triplets]

# ⚠️ PLACEHOLDERS (0 Ar) — seed uniquement. Vos montants réels sont en BDD.
PAYPLAN_RULES = [
    {"index": 1, "nom": "ANTA · Avant 01/06/2023 · WHFR1135 & WHFR919",
     "sites": ["ANTA"], "msa": ["WHFR1135", "WHFR919"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 5, 0), (6, 9, 0)), "explication": "Seed."},
    {"index": 2, "nom": "ANTA · Avant 01/06/2023 · Projets spécifiques (liste 2)",
     "sites": ["ANTA"],
     "msa": ["WHFR919", "WHFR1006", "WHFR1039", "WHFR1154", "WHFR1171", "WHFR218",
             "WHFR2749", "WHFR594", "WHFR907", "WHFR977", "WHFR1265"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 5, 0), (6, 9, 0)), "explication": "Seed."},
    {"index": 10, "nom": "TMM · Avant 01/06/2023 · 4 à 6 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0)), "explication": "Seed."},
    {"index": 11, "nom": "TMM · Avant 01/06/2023 · 7 à 18 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
    {"index": 12, "nom": "TMM · Avant 01/06/2023 · 19 mois et +",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
    {"index": 20, "nom": "ANTA · Avant 01/06/2023 · 4 à 6 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0)), "explication": "Seed."},
    {"index": 21, "nom": "ANTA · Avant 01/06/2023 · 7 à 18 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
    {"index": 22, "nom": "ANTA · Avant 01/06/2023 · 19 mois et +",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
    {"index": 40, "nom": "TMM · Après 01/06/2023 · 4 à 6 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0)), "explication": "Seed."},
    {"index": 41, "nom": "TMM · Après 01/06/2023 · 7 à 18 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
    {"index": 42, "nom": "TMM · Après 01/06/2023 · 19 mois et +",
     "sites": ["TMM"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
    {"index": 50, "nom": "ANTA · Après 01/06/2023 · 4 à 6 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0)), "explication": "Seed."},
    {"index": 51, "nom": "ANTA · Après 01/06/2023 · 7 à 18 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
    {"index": 52, "nom": "ANTA · Après 01/06/2023 · 19 mois et +",
     "sites": ["ANTA"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": _paliers((0, 2, 0), (3, 4, 0), (5, 6, 0), (7, 9, 0)), "explication": "Seed."},
]

REF_MSA_SEED = [
    ("W0ZVC5", "SITECSO", "Site CSO"),
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
    degraded = (REGLE_DEGRADATION and len(counted) >= 2 and counted[-1] < counted[-2])
    if degraded:
        counted[-1] = 0

    total = 0
    for i, p in enumerate(retenus):
        note = "0 pt — dégradation" if (degraded and i == len(counted) - 1) else None
        detail.append({"mois": labels[offset + i], "profil": p,
                       "points": profile_points.get(p) if p in profile_points else 0,
                       "pris_en_compte": True, "note": note})
        total += counted[i]
    return total, detail

def trouver_regle(regles, site, msa, anciennete_mois, hire_date):
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
        res["explication"] = (f"Aucune règle : Site={site} · MSA={msa or '—'} · "
                              f"embauche={hire_date.strftime('%d/%m/%Y')} · "
                              f"ancienneté={anciennete} mois. Complétez le payplan (Admin).")
        return res

    nb_mois = regle["nb_mois_profil"]
    # Nouveaux intégrants (4 à 6 mois) : le 1er mois n'est pas compté
    if REGLE_NOUVEAUX_4_6 and 4 <= anciennete <= 6:
        nb_mois = min(nb_mois, 2)

    total, detail = somme_points_profils(profiles, nb_mois, profile_points)
    montant = _montant_for_points(regle["montants"], total)
    res.update({"regle": regle["nom"], "nb_mois_profil": nb_mois,
                "detail_points": detail, "total_points": total,
                "explication": regle.get("explication", ""),
                "bareme": regle["montants"],
                "regle_infos": {"sites": regle.get("sites") or [], "msa": regle.get("msa") or [],
                                "embauche_avant": regle.get("embauche_avant"),
                                "embauche_apres": regle.get("embauche_apres"),
                                "anciennete_min": regle.get("anciennete_min", 0),
                                "anciennete_max": regle.get("anciennete_max")}})
    if montant is None:
        res["explication"] += f" | Aucun palier ne contient {total} pt."
        return res
    res["eligible"] = True
    res["montant"] = montant
    return res

def calculate_prime(hire_date, site, activites, reference_date=None,
                    profile_points=None, rules=None, base_heures=None):
    """Prorata : (montant_base × heures_activité) ÷ base_heures"""
    profile_points = profile_points if profile_points is not None else PROFILE_POINTS
    rules = rules if rules is not None else PAYPLAN_RULES
    reference_date = reference_date or date.today()
    anciennete = months_between(hire_date, reference_date)

    resultat = {"date_embauche": hire_date.isoformat(),
                "date_reference": reference_date.isoformat(),
                "anciennete_mois": anciennete,
                "anciennete_affichee": anciennete_decimale(hire_date, reference_date),
                "eligible": False, "montant_prime": 0, "explication": "",
                "activites": [], "total_heures": 0, "base_heures": None}
    if anciennete < MIN_ANCIENNETE_MOIS:
        resultat["explication"] = (f"Non éligible : ancienneté {anciennete} mois "
                                   f"(minimum {MIN_ANCIENNETE_MOIS} mois).")
        return resultat
    if not base_heures or base_heures <= 0:
        resultat["explication"] = "Renseignez la base d'heures (ex : 176)."
        return resultat
    resultat["base_heures"] = base_heures
    resultat["total_heures"] = sum(float(a.get("heures") or 0) for a in activites)

    montant_final = 0
    for a in activites:
        h = float(a.get("heures") or 0)
        act = calculate_activity(hire_date, site, a.get("msa"), a.get("profiles") or [],
                                 anciennete, profile_points, rules)
        act["activity_id"] = a.get("activity_id")
        act["heures"] = h
        act["part"] = round(h / base_heures * 100, 1)
        act["montant_proratise"] = (round((act["montant"] or 0) * h / base_heures)
                                    if act["eligible"] else 0)
        montant_final += act["montant_proratise"]
        resultat["activites"].append(act)

    resultat["montant_prime"] = montant_final
    resultat["eligible"] = montant_final > 0
    return resultat
