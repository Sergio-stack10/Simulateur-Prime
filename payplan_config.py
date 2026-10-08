# -*- coding: utf-8 -*-
"""
=====================================================================
 PAYPLAN — PRIME DE RÉGULARITÉ (v7)
=====================================================================
 ⚠️ Montants d'EXEMPLE ci-dessous. Vos vrais montants : panneau Admin
 (recommandé) ou ici + bouton « ⟲ Réinitialiser (fichier) ».
=====================================================================
"""

# -------------------------------------------------------------------------
# 1) PROFILS (noms complets)
# -------------------------------------------------------------------------
PROFILE_POINTS = {
    "Leader": 3,
    "Fragile": 1,
    "Soutien Intense": 0,
    "Non évalué": None,     # None = vide : aucun point attribué
}

MIN_ANCIENNETE_MOIS = 4

# -------------------------------------------------------------------------
# 2) RÈGLE DE DÉGRADATION
#    Si le profil du DERNIER mois compté est INFÉRIEUR au mois précédent,
#    les points du dernier mois NE SONT PAS comptés.
#    Ex : Leader - Leader - Fragile → 3 + 3 + 0 = 6 points
# -------------------------------------------------------------------------
REGLE_DEGRADATION = True

# -------------------------------------------------------------------------
# 3) RÈGLES DU PAYPLAN (matrice — priorité : règles CPSA d'abord, puis index)
# -------------------------------------------------------------------------
PAYPLAN_RULES = [
    {"index": 1, "nom": "L8 · ANTA · Avant 01/06/2023 · WHFR1135 & WHFR919",
     "sites": ["ANTA"], "msa": ["WHFR1135", "WHFR919"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 160000, 4: 170000, 5: 180000, 6: 185000, 7: 190000, 8: 200000, 9: 215000},
     "explication": "Ligne 8 — embauchés avant le 01/06/2023 sur WHFR1135 / WHFR919."},

    {"index": 2, "nom": "L9 · ANTA · Avant 01/06/2023 · Projets spécifiques",
     "sites": ["ANTA"],
     "msa": ["WHFR919", "WHFR1006", "WHFR1039", "WHFR1154", "WHFR1171", "WHFR218",
             "WHFR2749", "WHFR594", "WHFR907", "WHFR977", "WHFR1265"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 150000, 4: 160000, 5: 170000, 6: 175000, 7: 180000, 8: 190000, 9: 205000},
     "explication": "Ligne 9 — embauchés avant le 01/06/2023 sur les projets listés."},

    {"index": 10, "nom": "L1 · TMM · Avant 01/06/2023 · 4 à 6 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": {2: 55000, 3: 70000, 4: 85000, 5: 100000, 6: 115000},
     "explication": "Ligne 1 — 2 derniers mois."},
    {"index": 11, "nom": "L2 · TMM · Avant 01/06/2023 · 7 à 18 mois",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": {3: 110000, 4: 125000, 5: 140000, 6: 150000, 7: 160000, 8: 170000, 9: 185000},
     "explication": "Ligne 2 — 3 derniers mois."},
    {"index": 12, "nom": "L3 · TMM · Avant 01/06/2023 · 19 mois et +",
     "sites": ["TMM"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 145000, 4: 155000, 5: 165000, 6: 172000, 7: 178000, 8: 188000, 9: 200000},
     "explication": "Ligne 3 — 3 derniers mois."},

    {"index": 20, "nom": "L4 · ANTA · Avant 01/06/2023 · 4 à 6 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": 6, "nb_mois_profil": 2,
     "montants": {2: 60000, 3: 75000, 4: 90000, 5: 105000, 6: 120000},
     "explication": "Ligne 4 — 2 derniers mois."},
    {"index": 21, "nom": "L5 · ANTA · Avant 01/06/2023 · 7 à 18 mois",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 7, "anciennete_max": 18, "nb_mois_profil": 3,
     "montants": {3: 120000, 4: 135000, 5: 150000, 6: 160000, 7: 170000, 8: 180000, 9: 195000},
     "explication": "Ligne 5 — 3 derniers mois."},
    {"index": 22, "nom": "L6 · ANTA · Avant 01/06/2023 · 19 mois et +",
     "sites": ["ANTA"], "msa": [], "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 19, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 155000, 4: 165000, 5: 175000, 6: 180000, 7: 185000, 8: 195000, 9: 210000},
     "explication": "Ligne 6 — 3 derniers mois."},

    {"index": 30, "nom": "L7 · TMM · Après 01/06/2023",
     "sites": ["TMM"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 110000, 4: 125000, 5: 140000, 6: 150000, 7: 160000, 8: 170000, 9: 185000},
     "explication": "Ligne 7 — embauchés à partir du 01/06/2023 — 3 derniers mois."},
]

# -------------------------------------------------------------------------
# 4) RÉFÉRENTIEL : (ID activité, CPSA, Libellé) — éditable/importable via Admin
# -------------------------------------------------------------------------
REF_MSA_SEED = [
    ("W0ZVC5", "SITECSO", "Site CSO"),
    ("W0ZVBY", "CORPHQ", "Corp HQ"),
    ("W0ZQPJ", "WHFR1006", "Orange At Hd"),
    ("W0ZRVV", "WHFR2729", "DRM - FRAIS DE ROUTE"),
    # ⚠️ Liste d'exemple — importez votre Excel complet via le panneau Admin
]

# =========================================================================
# LOGIQUE DE CALCUL (ne pas modifier)
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
    """
    Points des N derniers mois (M3 = plus récent).
    · « Non évalué » (None) = vide → 0 point.
    · DÉGRADATION : si le dernier mois compté est INFÉRIEUR au précédent,
      ses points NE SONT PAS comptés. Ex : Leader-Leader-Fragile → 6 pts.
    """
    labels = ["M1", "M2", "M3"]
    retenus = profiles if nb_mois >= len(profiles) else profiles[-nb_mois:]
    offset = len(profiles) - len(retenus)
    detail = []

    def pts_of(p):
        v = profile_points.get(p) if p in profile_points else 0
        return 0 if v is None else v

    # Mois hors période
    for j in range(offset):
        p = profiles[j]
        detail.append({"mois": labels[j], "profil": p,
                       "points": profile_points.get(p) if p in profile_points else 0,
                       "pris_en_compte": False, "note": "hors période"})

    # Mois comptés + règle de dégradation
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

def calculate_activity(hire_date, site, msa, profiles, anciennete, profile_points, rules):
    res = {"msa": msa, "regle": None, "total_points": 0, "montant": None,
           "eligible": False, "explication": "", "detail_points": [], "nb_mois_profil": None}
    regle = trouver_regle(rules, site, msa, anciennete, hire_date)
    if regle is None:
        res["explication"] = f"Aucune règle (site {site}, CPSA {msa or '—'})."
        return res
    total, detail = somme_points_profils(profiles, regle["nb_mois_profil"], profile_points)
    montants = {int(k): int(v) for k, v in regle["montants"].items()}
    montant = montants.get(total)
    res.update({"regle": regle["nom"], "nb_mois_profil": regle["nb_mois_profil"],
                "detail_points": detail, "total_points": total,
                "explication": regle.get("explication", ""),
                "bareme": montants,
                "regle_infos": {
                    "sites": regle.get("sites") or [],
                    "msa": regle.get("msa") or [],
                    "embauche_avant": regle.get("embauche_avant"),
                    "embauche_apres": regle.get("embauche_apres"),
                    "anciennete_min": regle.get("anciennete_min", 0),
                    "anciennete_max": regle.get("anciennete_max"),
                }})
    if montant is None:
        res["explication"] += f" | Aucun montant pour {total} pt dans « {regle['nom']} »."
        return res
    res["eligible"] = True
    res["montant"] = montant
    return res

def calculate_prime(hire_date, site, activites, reference_date=None,
                    profile_points=None, rules=None):
    """activites : [{activity_id, msa, heures, profiles:[p1,p2,p3]}, ...]"""
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
