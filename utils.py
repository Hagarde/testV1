# utils.py
import streamlit as st
import pandas as pd
import os

# --- Données de référence ---

CATEGORIES_CIBLES = {
    "Infrastructures Réseau": ["Pylône", "Câble aérien", "Câble souterrain", "Transformateur", "Télécom"],
    "Bâtiments & Sites": ["Bâtiment Industriel", "Bâtiment de relayage", "Mur", "Portail"],
    "Bien matériel": ["Véhicule", "Outillage", "Touret", "Carburant", "PC/Téléphone"],
    "Aucun(e)": ["Aucun(e)"],
}

BARRIERES = ["Aucune", "Portail", "Grillage simple", "Clôture électrifiée", "Mur", "Contrôle d'accès"]
TYPE_ACTE = { 
    "Personnel" : ["Aggression"],
    "Tertiaire" : ["Vol", "Dégradation / Vandalisme", "Intrusion", "Incendie volontaire", "Sabotage", "Agression", "Inscription/Ajout illicite"],
    "Chantier" : ["Vol", "Dégradation / Vandalisme", "Intrusion", "Incendie volontaire", "Sabotage", "Agression", "Inscription/Ajout illicite"], 
    "Primaire" : [ "Vol", "Dégradation / Vandalisme", "Intrusion", "Incendie volontaire", "Sabotage", "Agression", "Inscription/Ajout illicite", "Sciage", "Déboulonage"]
}

# --- Fonctions ---

def charger_locations_interne():
    """Charge la structure GMR/GDP/Poste"""
    chemin_csv = "locations_db.csv"
    if not os.path.exists(chemin_csv):
        # Données fictives Interne
        data = {
            "Région": ["Ile-de-France", "Ile-de-France", "PACA", "Auvergne-Rhône-Alpes"],
            "Département": ["Paris", "Yvelines", "Bouches-du-Rhône", "Rhône"],
            "GMR": ["GMR-Paris", "GMR-Ouest", "GMR-Marseille", "GMR-Lyon"],
            "GDP": ["GDP-Batignolles", "GDP-Versailles", "GDP-Prado", "GDP-Part-Dieu"], 
            "ID_Poste" : ["POSTE-A", "POSTE-B", "POSTE-C", "POSTE-D"], 
            "Label_Recherche" : ["GDP-Batignolles (POSTE-D)", "GDP-Versailles (POSTE-D)", "GDP-Prado (POSTE-D)", "GMR-Lyon (POSTE-D)"]
        }
        pd.DataFrame(data).to_csv(chemin_csv, index=False)
    return pd.read_csv(chemin_csv)

def charger_villes_france():
    """
    Charge une base de villes (Région/Dépt/Ville/CodePostal).
    Pour l'exemple, on crée un petit fichier fictif si inexistant.
    """
    chemin_villes = "villes_db.csv"
    if not os.path.exists(chemin_villes):
        data = {
            "Région": ["Ile-de-France", "Ile-de-France", "PACA", "Auvergne-Rhône-Alpes"],
            "Département": ["Paris", "Hauts-de-Seine", "Bouches-du-Rhône", "Rhône"],
            "Ville": ["Paris 01", "La Défense", "Marseille", "Lyon"],
            "CodePostal": ["75001", "92800", "13000", "69000"],
            "Label_Recherche" : ["Paris 01 (75001)", "La Défense (92800)", "Marseille (13000)", "Lyon (69000)"]
        }
        pd.DataFrame(data).to_csv(chemin_villes, index=False)
    return pd.read_csv(chemin_villes)
# -----------------------------------------------------------------------------
# 3. LE COMPOSANT DE RECHERCHE MUTUALISÉ
# -----------------------------------------------------------------------------
def afficher_selecteurs_localisation(referentiel):
    """
    Affiche une barre de recherche unique.
    En fonction du mode, charge df_interne ou df_ville.
    Une fois sélectionné, déduit et affiche le contexte (Région, Dépt, etc.)
    """
    st.subheader(" Information générales")
    date_evt = st.date_input("Date de l'événement")
    
    mode_loc = st.radio(
        "Référentiel :",
        ["🏢 Site Interne (Poste)", "🌍 Adresse Civile (Ville)"],
        horizontal=(referentiel == "Ville")
    )
    
    # 2. Chargement du bon DataFrame en fonction du choix
    if mode_loc == "🏢 Site Interne (Poste)":
        df_source = charger_locations_interne()
        placeholder_text = "Tapez le nom du poste (ex: MER...)"
        label_resultat = "Poste électrique"
    else:
        df_source = charger_villes_france()
        placeholder_text = "Tapez le nom de la ville (ex: Par...)"
        label_resultat = "Ville"

    resultat = {}

    # 3. Barre de Recherche Mutualisée
    col_search, col_status = st.columns([3, 1])
    with col_search:
        # On utilise une clé dynamique pour vider le champ si on change de mode
        recherche = st.text_input(f"🔍 Rechercher : {label_resultat}", 
                                  placeholder=placeholder_text, 
                                  key=f"search_{mode_loc}")

    selection_row = None

    # 4. Logique de filtrage (dès 3 caractères)
    if recherche and len(recherche) >= 3:
        masque = df_source["Label_Recherche"].str.contains(recherche, case=False, na=False)
        df_filtre = df_source[masque]
        nb_res = len(df_filtre)

        if nb_res == 0:
            st.warning("Aucun résultat trouvé.")
        else:
            # Sélecteur de résultats
            options = df_filtre["Label_Recherche"].head(50).tolist()
            choix = st.selectbox(f"✅ Sélectionnez le {label_resultat} :", options)
            
            # Récupération de la ligne complète (Pandas Series)
            selection_row = df_source[df_source["Label_Recherche"] == choix].iloc[0]

    # 5. Affichage "Contextuel" (La déduction automatique)
    if selection_row is not None:
        st.markdown("---")
        if mode_loc == "🏢 Site Interne (Poste)" : 
            resultat = {
                "mode": "interne",
                "region": selection_row["Région"],
                "departement": selection_row["Département"],
                "gmr": selection_row["GMR"],
                "gdp": selection_row["GDP"],
                "identifiant": selection_row["ID_Poste"], # Juste le code (ex: MEREN)
            }
        else: # Mode Ville
            resultat = {
                "mode": "ville",
                "region": selection_row["Région"],
                "departement": selection_row["Département"],
                "gmr": "Hors GMR",
                "identifiant": f"{selection_row['Ville']} ({selection_row['CodePostal']})",
            }
            
    return resultat