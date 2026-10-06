from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

# Chargement du fichier Excel (à adapter selon le nom exact de votre fichier)
# Assurez-vous que le fichier s'appelle bien ACTIF.xlsx et est dans le même dossier
try:
    df_actifs = pd.read_excel('ACTIF.xlsx', sheet_name='ACTIF')
    # Nettoyage des noms de colonnes (au cas où il y a des espaces)
    df_actifs.columns = df_actifs.columns.str.strip()
except Exception as e:
    print(f"Erreur lors du chargement du fichier Excel: {e}")
    df_actifs = pd.DataFrame()

def get_site_code(location):
    """Détermine le code site (ANTA ou TMM) en fonction de la localisation."""
    if pd.isna(location):
        return "ANTA" # Par défaut
    loc_str = str(location).upper()
    if "TAMATAVE" in loc_str or "TOAMASINA" in loc_str:
        return "TMM"
    return "ANTA" # Par défaut Antananarivo

def calculer_prime(site, anciennete_mois, profil_m1, profil_m2, profil_m3):
    """
    Applique le payplan de l'image 2.
    Retourne le cumul de points et le montant de la prime.
    """
    points = 0
    
    # Définition des grilles de points selon le site (Basé sur l'image 2)
    # Format: { 'Profil': points }
    grille_points = {
        'ANTA': {
            '4-6 mois': {'0-2': 0, '3': 20, '4': 50, '5': 75, '6': 100},
            '7-18 mois': {'0-3': 0, '4': 25, '5': 65, '6-7': 95, '8-9': 130},
            '>=19 mois': {'0-3': 0, '4': 35, '5': 90, '6-7': 135, '8-9': 180}
        },
        'TMM': {
            '4-6 mois': {'0-2': 0, '3': 10, '4': 20, '5': 35, '6': 50},
            '7-18 mois': {'0-3': 0, '4': 15, '5': 37, '6-7': 56, '8-9': 75},
            '>=19 mois': {'0-3': 0, '4': 20, '5': 55, '6-7': 82, '8-9': 110}
        }
    }

    # Définition des montants (en Ariary) selon le site et les points
    # Format: { 'Points': Montant }
    grille_montants = {
        'ANTA': {
            0: 0, 3: 20000, 4: 50000, 5: 75000, 6: 100000,
            7: 95000, 8: 130000, 9: 180000 # Note: Les montants varient selon l'ancienneté, simplification ici
        },
        'TMM': {
            0: 0, 3: 10000, 4: 20000, 5: 35000, 6: 50000,
            7: 56000, 8: 75000, 9: 110000
        }
    }

    # Fonction pour mapper un profil à un nombre de points
    def map_profil_to_points(profil, tranche_anciennete, site_code):
        profil = str(profil).strip().capitalize()
        if profil in ['0-2', '0-3']: return 0
        
        # On cherche dans la grille du site
        site_grid = grille_points.get(site_code, {})
        tranche_grid = site_grid.get(tranche_anciennete, {})
        
        for key, val in tranche_grid.items():
            if '-' in key:
                min_p, max_p = map(int, key.split('-'))
                if min_p <= int(profil) <= max_p:
                    return val
            elif str(profil) == key:
                return val
        return 0

    # Déterminer la tranche d'ancienneté
    if 4 <= anciennete_mois <= 6:
        tranche = '4-6 mois'
    elif 7 <= anciennete_mois <= 18:
        tranche = '7-18 mois'
    else:
        tranche = '>=19 mois'

    # Calcul des points pour chaque mois
    p1 = map_profil_to_points(profil_m1, tranche, site)
    p2 = map_profil_to_points(profil_m2, tranche, site)
    p3 = map_profil_to_points(profil_m3, tranche, site)
    
    cumul_points = p1 + p2 + p3

    # Calcul du montant de la prime
    # Note: Le montant exact dépend du cumul de points ET de l'ancienneté exacte.
    # Ici on prend le montant correspondant au palier de points atteint.
    montant_prime = 0
    montants_site = grille_montants.get(site, {})
    
    # On cherche le montant correspondant au cumul de points
    # (Simplification: on prend le montant le plus élevé atteint)
    for pts, montant in sorted(montants_site.items()):
        if cumul_points >= pts:
            montant_prime = montant

    return cumul_points, montant_prime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json
    matricule = str(data.get('matricule', '')).strip()
    date_embauche_str = data.get('date_embauche')
    profil_m1 = data.get('profil_m1')
    profil_m2 = data.get('profil_m2')
    profil_m3 = data.get('profil_m3')

    # 1. Recherche du collaborateur dans le fichier Excel
    # On s'assure que la colonne 'Employee ID' est bien lue comme string
    df_actifs['Employee ID'] = df_actifs['Employee ID'].astype(str).str.strip()
    
    collaborateur = df_actifs[df_actifs['Employee ID'] == matricule]
    
    if collaborateur.empty:
        return jsonify({'error': 'Matricule non trouvé dans la base ACTIF.'}), 404

    # Extraction des données
    row = collaborateur.iloc[0]
    nom_complet = f"{row.get('First Name', '')} {row.get('Last Name', '')}"
    statut = "ACTIVE" # On suppose que s'il est dans ACTIF, il est actif
    site_location = row.get('Location', '')
    
    # Détermination du site (ANTA ou TMM)
    site_code = get_site_code(site_location)
    
    # Calcul de l'ancienneté
    try:
        date_embauche = datetime.strptime(date_embauche_str, '%Y-%m-%d')
        aujourd_hui = datetime.now()
        diff = relativedelta(aujourd_hui, date_embauche)
        anciennete_mois = diff.years * 12 + diff.months
    except:
        anciennete_mois = 0

    # 2. Calcul de la prime
    cumul_points, prime_estimee = calculer_prime(site_code, anciennete_mois, profil_m1, profil_m2, profil_m3)

    # 3. Retour des résultats
    return jsonify({
        'nom': nom_complet,
        'statut': statut,
        'site': site_code,
        'anciennete_mois': anciennete_mois,
        'profil_m1': profil_m1,
        'profil_m2': profil_m2,
        'profil_m3': profil_m3,
        'cumul_points': cumul_points,
        'prime_estimee': f"{prime_estimee:,} Ar".replace(',', ' ')
    })

if __name__ == '__main__':
    app.run(debug=True)
