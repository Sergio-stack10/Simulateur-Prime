# -*- coding: utf-8 -*-
"""
=====================================================================
 PAYPLAN — PRIME DE RÉGULARITÉ
=====================================================================
 ⚠️  Les valeurs ci-dessous sont des EXEMPLES calibrés pour reproduire
 la maquette (Leader+Fragile+Leader = 7 pts -> 185 000 Ar, ANTA 37m+).
 REPORTEZ ICI LES CHIFFRES EXACTS DE VOTRE PAYPLAN OFFICIEL :

   1. PROFILE_POINTS  -> points par profil mensuel
   2. PAYPLAN_RULES   -> une entrée par ligne du tableau du payplan
=====================================================================
"""
import calendar
from datetime import date

# -------------------------------------------------------------------------
# 1) POINTS PAR PROFIL MENSUEL (M1 = plus ancien, M3 = plus récent)
# -------------------------------------------------------------------------
PROFILE_POINTS = {
    "Leader":     3,
    "Confirmé":   2,
    "Fragile":    1,
    "Non évalué": 0,   # à retirer si ce profil n'existe pas chez vous
}

# -------------------------------------------------------------------------
# 2) ÉLIGIBILITÉ
# -------------------------------------------------------------------------
MIN_ANCIENNETE_MOIS = 4   # en dessous : non éligible (cf. payplan)

# -------------------------------------------------------------------------
# 3) RÈGLES DU PAYPLAN
#    - "sites"          : codes concernés (ANTA / TMM / ...)
#    - "anciennete_min/max" : tranche d'ancienneté en mois (max=None : illimité)
#    - "nb_mois_profil" : nb de derniers mois de profil comptés (2 ou 3)
#    - "embauche_avant/apres" : contrainte optionnelle sur la date d'embauche
#      (ex. règle spéciale « embauchés avant le 01/06/2023 »).
#      ⚠️ Placer les règles conditionnelles AVANT les règles générales :
#      la première règle qui correspond est appliquée.
#    - "montants"       : barème {total_points: montant en Ariary}
# -------------------------------------------------------------------------
PAYPLAN_RULES = [
    # ---------------- ANTANANARIVO (ANTA) ----------------
    {
        "nom": "ANTA · 4 à 6 mois · 2 derniers mois",
        "sites": ["ANTA"],
        "anciennete_min": 4, "anciennete_max": 6,
        "nb_mois_profil": 2,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {2: 60000, 3: 75000, 4: 90000, 5: 105000, 6: 120000},
        "explication": "Ancienneté 4 à 6 mois : seuls les 2 derniers mois (M2, M3) sont pris en compte.",
    },
    {
        "nom": "ANTA · 7 à 18 mois · 3 derniers mois",
        "sites": ["ANTA"],
        "anciennete_min": 7, "anciennete_max": 18,
        "nb_mois_profil": 3,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {3: 120000, 4: 135000, 5: 150000, 6: 160000,
                     7: 170000, 8: 180000, 9: 195000},
        "explication": "Ancienneté 7 à 18 mois : profils des 3 derniers mois (M1, M2, M3).",
    },
    {
        "nom": "ANTA · 19 à 36 mois · 3 derniers mois",
        "sites": ["ANTA"],
        "anciennete_min": 19, "anciennete_max": 36,
        "nb_mois_profil": 3,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {3: 140000, 4: 155000, 5: 168000, 6: 175000,
                     7: 182000, 8: 192000, 9: 205000},
        "explication": "Ancienneté 19 à 36 mois : profils des 3 derniers mois.",
    },
    {
        "nom": "ANTA · 37 mois et + · 3 derniers mois",
        "sites": ["ANTA"],
        "anciennete_min": 37, "anciennete_max": None,
        "nb_mois_profil": 3,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {3: 155000, 4: 165000, 5: 175000, 6: 180000,
                     7: 185000, 8: 195000, 9: 210000},
        "explication": "Ancienneté 37 mois et + : profils des 3 derniers mois.",
    },

    # ---------------- TAMATAVE (TMM) ----------------
    {
        "nom": "TMM · 4 à 6 mois · 2 derniers mois",
        "sites": ["TMM"],
        "anciennete_min": 4, "anciennete_max": 6,
        "nb_mois_profil": 2,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {2: 55000, 3: 70000, 4: 85000, 5: 100000, 6: 115000},
        "explication": "Ancienneté 4 à 6 mois : seuls les 2 derniers mois (M2, M3) sont pris en compte.",
    },
    {
        "nom": "TMM · 7 à 18 mois · 3 derniers mois",
        "sites": ["TMM"],
        "anciennete_min": 7, "anciennete_max": 18,
        "nb_mois_profil": 3,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {3: 110000, 4: 125000, 5: 140000, 6: 150000,
                     7: 160000, 8: 170000, 9: 185000},
        "explication": "Ancienneté 7 à 18 mois : profils des 3 derniers mois.",
    },
    {
        "nom": "TMM · 19 à 36 mois · 3 derniers mois",
        "sites": ["TMM"],
        "anciennete_min": 19, "anciennete_max": 36,
        "nb_mois_profil": 3,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {3: 130000, 4: 145000, 5: 158000, 6: 165000,
                     7: 172000, 8: 182000, 9: 195000},
        "explication": "Ancienneté 19 à 36 mois : profils des 3 derniers mois.",
    },
    {
        "nom": "TMM · 37 mois et + · 3 derniers mois",
        "sites": ["TMM"],
        "anciennete_min": 37, "anciennete_max": None,
        "nb_mois_profil": 3,
        "embauche_avant": None, "embauche_apres": None,
        "montants": {3: 145000, 4: 155000, 5: 165000, 6: 172000,
                     7: 178000, 8: 188000, 9: 200000},
        "explication": "Ancienneté 37 mois et + : profils des 3 derniers mois.",
    },

    # ------------------------------------------------------------------
    # EXEMPLE de règle conditionnelle « Avant le 01/06/2023 »
    # (à activer/adaptater si votre payplan distingue ces embauches —
    #  placer cette règle AVANT la règle générale ANTA 37 mois et +) :
    #
    # {
    #     "nom": "ANTA · embauchés avant le 01/06/2023 · 37 mois et +",
    #     "sites": ["ANTA"],
    #     "anciennete_min": 37, "anciennete_max": None,
    #     "nb_mois_profil": 3,
    #     "embauche_avant": "2023-06-01",   # ne s'applique QU'À ces embauches
    #     "embauche_apres": None,
    #     "montants": {3: 160000, 4: 170000, 5: 180000, 6: 185000,
    #                  7: 190000, 8: 200000, 9: 215000},
    #     "explication": "Régime transitoire : embauches antérieures au 01/06/2023.",
    # },
    # ------------------------------------------------------------------
]


# =========================================================================
# LOGIQUE DE CALCUL (paramétrable — appelée avec le payplan de la BDD)
# =========================================================================
import calendar
from datetime import date

def months_between(start: date, end: date) -> int:
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(0, months)

def anciennete_decimale(start: date, end: date) -> float:
    if end < start:
        return 0.0
    base = (end.year - start.year) * 12 + (end.month - start.month)
    dim = calendar.monthrange(end.year, end.month)[1]
    return round(max(0.0, base + (end.day - start.day) / dim), 1)

def somme_points_profils(profiles, nb_mois, profile_points):
    labels = ["M1", "M2", "M3"]
    retenus = profiles if nb_mois >= len(profiles) else profiles[-nb_mois:]
    offset = len(profiles) - len(retenus)
    total, detail = 0, []
    for j in range(offset):
        detail.append({"mois": labels[j], "profil": profiles[j],
                       "points": profile_points.get(profiles[j], 0),
                       "pris_en_compte": False})
    for i, p in enumerate(retenus):
        pts = profile_points.get(p, 0)
        total += pts
        detail.append({"mois": labels[offset + i], "profil": p,
                       "points": pts, "pris_en_compte": True})
    return total, detail

def trouver_regle(regles, site, anciennete_mois, hire_date):
    for regle in regles:
        if site.upper() not in [s.upper() for s in regle.get("sites", [])]:
            continue
        if anciennete_mois < regle.get("anciennete_min", 0):
            continue
        amax = regle.get("anciennete_max")
        if amax is not None and anciennete_mois > amax:
            continue
        avant, apres = regle.get("embauche_avant"), regle.get("embauche_apres")
        if avant and hire_date >= date.fromisoformat(str(avant)[:10]):
            continue
        if apres and hire_date <= date.fromisoformat(str(apres)[:10]):
            continue
        return regle
    return None

def calculate_prime(hire_date, site, profiles, reference_date=None,
                    profile_points=None, rules=None):
    profile_points = profile_points if profile_points is not None else PROFILE_POINTS
    rules = rules if rules is not None else PAYPLAN_RULES
    reference_date = reference_date or date.today()
    anciennete = months_between(hire_date, reference_date)

    resultat = {
        "date_embauche": hire_date.isoformat(),
        "date_reference": reference_date.isoformat(),
        "anciennete_mois": anciennete,
        "anciennete_affichee": anciennete_decimale(hire_date, reference_date),
        "eligible": False, "total_points": 0, "montant_prime": None,
        "regle": None, "nb_mois_profil": None,
        "explication": "", "detail_points": [],
    }
    if anciennete < MIN_ANCIENNETE_MOIS:
        resultat["explication"] = (f"Non éligible : ancienneté de {anciennete} mois — "
                                   f"minimum requis : {MIN_ANCIENNETE_MOIS} mois.")
        return resultat

    regle = trouver_regle(rules, site, anciennete, hire_date)
    if regle is None:
        resultat["explication"] = (f"Aucune règle du payplan ne correspond "
                                   f"(site {site}, ancienneté {anciennete} mois).")
        return resultat

    total_points, detail = somme_points_profils(profiles, regle["nb_mois_profil"], profile_points)
    montants = {int(k): v for k, v in regle["montants"].items()}
    montant = montants.get(total_points)

    resultat.update({"regle": regle["nom"], "nb_mois_profil": regle["nb_mois_profil"],
                     "detail_points": detail, "total_points": total_points,
                     "explication": regle.get("explication", "")})
    if montant is None:
        resultat["explication"] += (f" | Aucun montant défini pour {total_points} "
                                    f"point(s) dans la règle « {regle['nom']} ».")
        return resultat
    resultat["eligible"] = True
    resultat["montant_prime"] = montant
    return resultat
