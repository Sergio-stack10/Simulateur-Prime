# -*- coding: utf-8 -*-
"""
=====================================================================
 PAYPLAN — PRIME DE RÉGULARITÉ (v3 · multi-activités)
=====================================================================
 ⚠️ MONTANTS D'EXEMPLE : reportez vos valeurs Excel via le PANNEAU
 ADMIN (sans redéploiement) ou ici + bouton « ⟲ Réinitialiser ».

 Une règle = une ligne de votre matrice :
   index            : ordre (plus petit = prioritaire)
   sites            : ANTA / TMM (vide = tous)
   msa              : codes projets (vide = tous)
   embauche_avant   : embauches AVANT cette date
   embauche_apres   : embauches À PARTIR de cette date
   anciennete_min/max : tranche d'ancienneté en mois (max None = ∞)
   nb_mois_profil   : derniers mois comptés (2 ou 3)
   montants         : {points: montant Ar}

 Priorité automatique : 1) règles AVEC msa d'abord, 2) puis index croissant.
=====================================================================
"""

PROFILE_POINTS = {"Leader": 3, "Fragile": 1, "Soutien Intense": 0, "Non évalué": None}
MIN_ANCIENNETE_MOIS = 4

PAYPLAN_RULES = [
    # ---- Ligne 8 : ANTA · avant 01/06/2023 · WHFR1135 & WHFR919 ----
    {"index": 1, "nom": "L8 · ANTA · Avant 01/06/2023 · WHFR1135 & WHFR919",
     "sites": ["ANTA"], "msa": ["WHFR1135", "WHFR919"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 160000, 4: 170000, 5: 180000, 6: 185000, 7: 190000, 8: 200000, 9: 215000},
     "explication": "Ligne 8 — embauchés avant le 01/06/2023 sur WHFR1135 / WHFR919."},

    # ---- Ligne 9 : ANTA · avant 01/06/2023 · projets spécifiques ----
    {"index": 2, "nom": "L9 · ANTA · Avant 01/06/2023 · Projets spécifiques",
     "sites": ["ANTA"],
     "msa": ["WHFR919", "WHFR1006", "WHFR1039", "WHFR1154", "WHFR1171", "WHFR218",
             "WHFR2749", "WHFR594", "WHFR907", "WHFR977", "WHFR1265"],
     "embauche_avant": "2023-06-01", "embauche_apres": None,
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 150000, 4: 160000, 5: 170000, 6: 175000, 7: 180000, 8: 190000, 9: 205000},
     "explication": "Ligne 9 — embauchés avant le 01/06/2023 sur les projets listés."},

    # ---- Lignes 1 à 3 : TMM · avant 01/06/2023 ----
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

    # ---- Lignes 4 à 6 : ANTA · avant 01/06/2023 · tous projets ----
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

    # ---- Ligne 7 : TMM · après 01/06/2023 ----
    {"index": 30, "nom": "L7 · TMM · Après 01/06/2023",
     "sites": ["TMM"], "msa": [], "embauche_avant": None, "embauche_apres": "2023-06-01",
     "anciennete_min": 4, "anciennete_max": None, "nb_mois_profil": 3,
     "montants": {3: 110000, 4: 125000, 5: 140000, 6: 150000, 7: 160000, 8: 170000, 9: 185000},
     "explication": "Ligne 7 — embauchés à partir du 01/06/2023 — 3 derniers mois."},

    # ⚠️ Pas de ligne « ANTA · après 01/06/2023 » décrite : si elle existe
    # dans votre payplan, ajoutez-la ici ou via le panneau Admin.
]

# -------------------------------------------------------------------------
# TABLE RÉFÉRENTIELLE : ID activité → MSA (modifiable dans le panneau Admin)
# -------------------------------------------------------------------------
REF_MSA_SEED = [
    ("W0ZVC5", "SITECSO"), ("W0ZVBY", "CORPHQ"), ("W0ZV80", "SITECSOTH"),
    ("W0ZVAN", "SITEHQ"), ("W0ZVBL", "FRANCERGNCSO"), ("W0ZX3M", "980006157"),
    ("W0ZT0B", "WHFR2822"), ("W0ZM8M", "WHFR9"), ("W0ZNVJ", "WHFR1818"),
    ("W0ZO6O", "WHFR1834"), ("W0ZQPJ", "WHFR1006"), ("W0ZVPL", "WHFR1039"),
    ("W0ZR30", "WHFR1039"), ("W0ZRW0", "WHFR2731"), ("W0ZZ7K", "WHFR2373"),
    ("W0ZM8I", "WHFR965"), ("W0ZOX8", "WHFR1831"), ("W0ZO68", "WHFR1135"),
    ("W0ZOVY", "WHFR1661"), ("W0ZTD2", "WHFR2857"), ("W0ZPHH", "WHFR56"),
    ("W0ZQ4M", "WHFR1187"), ("W0ZMZZ", "WHFR1188"), ("W0ZR1Z", "WHFR907"),
    ("W0ZNW8", "WHFR218"), ("W0ZQ21", "WHFR1830"), ("W0ZMY0", "WHFR1451"),
    ("W0ZRDE", "WHFR1944"), ("W0ZRFP", "WHFR1154"), ("W0ZPKW", "WHFR1909"),
    ("W0ZRVV", "WHFR2729"), ("W0ZLN2", "WHFR1732"), ("W0ZTM3", "WHFR2905"),
    ("W0ZTOJ", "WHFR2914"), ("W0ZVKT", "WHFR216"), ("W0ZHE1", "980000875"),
    ("W0ZMYX", "WHFR1171"), ("W0ZSI2", "WHFR2749"), ("W0ZOWG", "WHFR711"),
    ("W0ZASC", "DELRECRUITING"),
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
    """None = profil « Non évalué » : vide (aucun point ajouté, affiché « vide »)."""
    labels = ["M1", "M2", "M3"]
    retenus = profiles if nb_mois >= len(profiles) else profiles[-nb_mois:]
    offset = len(profiles) - len(retenus)
    total, detail = 0, []

    def pts_of(p):
        return profile_points.get(p) if p in profile_points else 0

    for j in range(offset):
        detail.append({"mois": labels[j], "profil": profiles[j],
                       "points": pts_of(profiles[j]), "pris_en_compte": False})
    for i, p in enumerate(retenus):
        v = pts_of(p)
        if v is not None:
            total += v
        detail.append({"mois": labels[offset + i], "profil": p,
                       "points": v, "pris_en_compte": True})
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
        res["explication"] = f"Aucune règle (site {site}, MSA {msa or '—'})."
        return res
    total, detail = somme_points_profils(profiles, regle["nb_mois_profil"], profile_points)
    montants = {int(k): int(v) for k, v in regle["montants"].items()}
    montant = montants.get(total)
    res.update({"regle": regle["nom"], "nb_mois_profil": regle["nb_mois_profil"],
                "detail_points": detail, "total_points": total,
                "explication": regle.get("explication", "")})
    if montant is None:
        res["explication"] += f" | Aucun montant pour {total} pt dans « {regle['nom']} »."
        return res
    res["eligible"] = True
    res["montant"] = montant
    return res

def calculate_prime(hire_date, site, activites, reference_date=None,
                    profile_points=None, rules=None):
    """activites : [{msa, heures, profiles:[p1,p2,p3]}, ...]"""
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
        act["activity_id"] = a.get("activity_id")   # ← AJOUTEZ CETTE LIGNE
        part = h / total_heures
        act["heures"] = h
        act["part"] = round(part * 100, 1)
        act["montant_proratise"] = round((act["montant"] or 0) * part) if act["eligible"] else 0
        montant_final += act["montant_proratise"]
        resultat["activites"].append(act)

    resultat["montant_prime"] = montant_final
    resultat["eligible"] = montant_final > 0
    return resultat
