# -*- coding: utf-8 -*-
"""
=====================================================================
 PAYPLAN — PRIME DE RÉGULARITÉ (v17 · points par MOIS + dégradation
 sur points courants)
=====================================================================
 · PROFILE_POINT_EFFECTS : historique des points avec date d'effet au
   mois de PERFORMANCE. Chaque mois (M1/M2/M3) est résolu séparément :
   un profil peut valoir 3 pts en M1/M2 et 2 pts en M3.
 · Dégradation : comparée aux points COURANTS — un changement de barème
   (ex : Challenger 3→2 au 01/09/2026) n'est PAS une dégradation.
 · PAYPLAN_RULES : seed uniquement (BDD vide / reset Admin).
 ⚠️ Montants seed = placeholders 0 : vos vrais montants vivent en BDD.
=====================================================================
"""

# -------------------------------------------------------------------------
# 1) PROFILS (valeurs COURANTES — modifiables via Admin → Payplan)
# -------------------------------------------------------------------------
PROFILE_POINTS = {
    "Leader": 3,
    "Challenger": 2,
    "Fragile": 1,
    "Care": 0,
    "Non évalué": None,     # None = vide : aucun point
}

# ── Historique des points (date d'effet au mois de PERFORMANCE) ──
# Un profil vaut « ancien » pour tout mois de performance antérieur à
# date_effet ; à partir de ce mois, valeur courante du payplan.
PROFILE_POINT_EFFECTS = [
    {"profil": "Challenger", "ancien": 3, "date_effet": "2026-09-01"},
]

MIN_ANCIENNETE_MOIS = 4
REGLE_DEGRADATION = True       # dernier mois en baisse → points non comptés
REGLE_NOUVEAUX_4_6 = True      # ancienneté 4-6 mois : 1er mois non compté

def _paliers(*triplets):
    return [{"min": a, "max": b, "montant": m} for a, b, m in triplets]

# -------------------------------------------------------------------------
# 2) RÈGLES SEED (⚠️ placeholders 0 — vraies valeurs en BDD via Admin)
# -------------------------------------------------------------------------
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

# ── Historique : valeur « ancienne » d'un profil pour un mois ISO ──
def _legacy_value(profil, mois_iso):
    """Retourne l'ancienne valeur si le mois (ISO YYYY-MM-DD) est
    antérieur à la date d'effet d'un historique ; sinon None."""
    for e in PROFILE_POINT_EFFECTS:
        if e.get("profil") == profil and str(mois_iso) < str(e.get("date_effet"))[:10]:
            return e.get("ancien")
    return None

# ── Points des profils d'une activité (résolution MOIS PAR MOIS) ──
def somme_points_profils(profiles, nb_mois, profile_points, month_dates=None):
    """
    · « Non évalué » (None) = vide → 0 point.
    · month_dates = {M1: ISO, M2: ISO, M3: ISO} : chaque mois est résolu
      SÉPARÉMENT (Challenger peut valoir 3 pts en M1/M2 et 2 pts en M3).
    · DÉGRADATION : comparée aux points COURANTS — un changement de
      barème n'est PAS une dégradation (Challenger 3→3→2 : total 8).
    """
    labels = ["M1", "M2", "M3"]
    retenus = profiles if nb_mois >= len(profiles) else profiles[-nb_mois:]
    offset = len(profiles) - len(retenus)
    detail = []

    def base_pts(p):
        v = profile_points.get(p) if p in profile_points else None
        return 0 if v is None else v

    def pts_for_month(profil, label):
        """Points de CE profil pour SON mois (historique inclus)."""
        mois_iso = (month_dates or {}).get(label)
        if mois_iso is None:
            return base_pts(profil)
        legacy = _legacy_value(profil, mois_iso)
        if legacy is not None:
            return 0 if legacy is None else legacy
        return base_pts(profil)

    # Mois hors période (ex : M1 quand la règle n'en compte que 2)
    for j in range(offset):
        p = profiles[j]
        detail.append({"mois": labels[j], "profil": p,
                       "points": profile_points.get(p) if p in profile_points else 0,
                       "pris_en_compte": False, "note": "hors période"})

    # Valeurs effectives MOIS PAR MOIS (pour le total)
    counted = [pts_for_month(p, labels[offset + i]) for i, p in enumerate(retenus)]

    # Dégradation : comparaison sur points COURANTS (sans historique) —
    # la baisse due à un changement de barème n'est pas une dégradation
    counted_courants = [base_pts(p) for p in retenus]
    degraded = (REGLE_DEGRADATION and len(counted_courants) >= 2
                and counted_courants[-1] < counted_courants[-2])
    if degraded:
        counted[-1] = 0

    total = 0
    for i, p in enumerate(retenus):
        note = "0 pt — dégradation" if (degraded and i == len(counted) - 1) else None
        detail.append({"mois": labels[offset + i], "profil": p,
                       "points": profile_points.get(p) if p in profile_points else 0,
                       "pris_en_compte": True, "note": note,
                       "points_mois": counted[i]})
        total += counted[i]
    return total, detail

# ── Sélection de la règle (priorité : MSA spécifiques puis index) ──
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

# ── Calcul d'une activité ──
def calculate_activity(hire_date, site, msa, profiles, anciennete, profile_points, rules,
                       month_dates=None):
    res = {"msa": msa, "regle": None, "total_points": 0, "montant": None,
           "eligible": False, "explication": "", "detail_points": [], "nb_mois_profil": None}
    regle = trouver_regle(rules, site, msa, anciennete, hire_date)
    if regle is None:
        res["explication"] = (f"Aucune règle : Site={site} · MSA={msa or '—'} · "
                              f"embauche={hire_date.strftime('%d/%m/%Y')} · "
                              f"ancienneté={anciennete} mois. Complétez le payplan (Admin).")
        return res

    nb_mois = regle["nb_mois_profil"]
    if REGLE_NOUVEAUX_4_6 and 4 <= anciennete <= 6:
        nb_mois = min(nb_mois, 2)

    total, detail = somme_points_profils(profiles, nb_mois, profile_points, month_dates)
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

# ── Calcul global (prorata base d'heures) ──
def calculate_prime(hire_date, site, activites, reference_date=None,
                    profile_points=None, rules=None, base_heures=None, month_dates=None):
    """activites : [{activity_id, msa, heures, profiles}, ...]
    Prorata : montant_proratise = (montant_base × heures_activité) ÷ base_heures"""
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
                                 anciennete, profile_points, rules,
                                 month_dates=month_dates)
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
