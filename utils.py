import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =============================================================================
# 0. FONCTIONS UTILITAIRES
# =============================================================================
def trier_avec_autre_fin(liste):
    """ Trie une liste alphabétiquement mais force 'Autre' à la fin. """
    elements = [x for x in list(set(liste)) if x != "Autre"]
    elements.sort()
    if "Autre" in liste:
        elements.append("Autre")
    return elements

# =============================================================================
# 1. DONNÉES DE RÉFÉRENCE
# =============================================================================

# --- A. LISTE DES CIBLES (Objets spécifiques) ---
# Sert de base pour la complétion de la 3ème étape de la cascade
CATEGORIES_CIBLES = {
    "Infrastructures Réseau": ["Pylône", "Pylône aérosouterain", "Câble aérien", "Câble souterrain", "Transformateur", "Télécom", "Caniveau", "RGT"],
    "Bâtiments & Sites": ["Bâtiment Industriel", "Bâtiment de relayage", "Mur", "Portail", "Palplanche", "Clôture", "Autre Bâtiment"],
    "Bien matériel": ["Véhicule", "Outillage", "Touret", "Carburant", "PC/Téléphone", "Groupe Electrogène (GE)"],
    "Employé": ["Salariés", "Prestataire"],
    "Aucun": ["Aucun"],
}
# Génération automatique d'une liste globale pour les modes opératoires larges (ex: Effraction)
TOUTES_CIBLES = [item for sublist in CATEGORIES_CIBLES.values() for item in sublist]

# --- B. TYPOLOGIES (Niveau 1) ---
TYPOLOGIE_LISTE_BRUTE = [
    "Intrusion", "Vol", "Vandalisme", "Sabotage", 
    "Malveillance interne", "Agression / Intimidation", "Terrorisme", "Autre"
]
TYPOLOGIE_GLOBAL = trier_avec_autre_fin(TYPOLOGIE_LISTE_BRUTE)

# --- C. RÈGLES DE CASCADE : Typologie -> Mode Opératoire -> Cibles possibles ---
REGLES_CASCADE = {
    "Intrusion": {
        "Tentative d’intrusion": "ALL",
        "Effraction": "ALL",
        "Escalade ou destruction des protections périmétriques": ["Mur", "Portail", "Palplanche", "Clôture", "Autre Bâtiment"],
        "Usage de faux": "ALL"
    },
    "Vol": {
        "Vol d’un bien matériel ou industriel": ["Outillage", "PC/Téléphone", "Véhicule", "Touret", "RGT", "Câble aérien", "Câble souterrain", "Carburant", "Groupe Electrogène (GE)"],
        "Tentative de vol": "ALL"
    },
    "Vandalisme": {
        "Inscription illicite (Tag)": ["Mur", "Portail", "Clôture", "Bâtiment Industriel", "Bâtiment de relayage", "Véhicule"],
        "Dégradation volontaire (Bris, destruction)": "ALL",
        "Dépôt sauvage": ["Mur", "Portail", "Clôture", "Autre Bâtiment"],
        "Incendie volontaire d’éléments secondaires": ["Mur", "Portail", "Véhicule", "Autre"]
    },
    "Sabotage": {
        "Incendie volontaire d’infrastructures": ["Pylône", "Pylône aérosouterain", "Caniveau", "Transformateur", "Câble souterrain", "Câble aérien", "Bâtiment Industriel", "Bâtiment de relayage"],
        "Sciage": ["Pylône", "Pylône aérosouterain"],
        "Déboulonnage": ["Pylône", "Pylône aérosouterain"],
        "Sabotage des liaisons télécoms": ["Télécom", "RGT", "Caniveau"]
    },
    "Malveillance interne": {
        "Vol interne": ["Outillage", "PC/Téléphone", "Véhicule", "Touret", "RGT", "Carburant", "Autre"],
        "Occupation illégale des locaux": ["Bâtiment Industriel", "Bâtiment de relayage", "Autre Bâtiment"],
        "Utilisation inappropriée des infrastructures": "ALL",
        "Détérioration ou sabotage": "ALL"
    },
    "Agression / Intimidation": {
        "Violence physique": ["Salariés", "Prestataire"],
        "Menaces verbales, intimidation, chantage": ["Salariés", "Prestataire"],
        "Vol à main armée ou extorsion": ["Salariés", "Prestataire"],
        "Contrainte ou obtention d'information": ["Salariés", "Prestataire"]
    },
    "Terrorisme": {
        "Attaque armée": ["Salariés", "Prestataire", "Bâtiment Industriel", "Autre Bâtiment"],
        "Prise d’otages, séquestration": ["Salariés", "Prestataire"],
        "Action coordonnée de masse": "ALL",
        "Menace ou chantage stratégique": ["Salariés", "Prestataire", "Autre"],
        "Sabotage massif d’installations critiques": ["Transformateur", "Bâtiment Industriel", "Bâtiment de relayage", "Télécom", "Pylône", "Pylône aérosouterain", "Câble aérien", "Câble souterrain"],
        "Utilisation de substances chimiques, biologiques, radioactives": "ALL"
    },
    "Autre": {"Autre": ["Autre"]}
}

# --- D. AUTRES LISTES ---
BARRIERES = ["Portail", "Portillion", "Grillage simple sans bavolet", "Grillage simple avec bavolet", 
             "Mur", "Contrôle d'accès", "Palplanche"]

# =============================================================================
# 2. FONCTIONS UI SIMPLES
# =============================================================================

def INPUT_DATETIME(): return st.date_input("Date de l'événement", datetime.now())
def INPUT_COUT_ESTIME(): return st.number_input("Coût estimé (k€)", min_value=0, step=1)  
def INPUT_DESCRIPTION(): return st.text_area("Description détaillée de l'acte de malveillance", placeholder="Client ciblé, prestataire visé, revendication locale, mesures conservatoires, interpellation, fuite des intrus, ...", help="Si les informations suivantes sont disponibles, veuillez préciser : Client ciblé, prestataire visé, revendication locale, mesures conservatoires, interpellation, fuite des intrus, ...")
def SELECT_BOX_MESURE_PROVISOIRE(): return st.selectbox("Mesures conservatoires mises en place ?", ['Oui', 'Non'], placeholder=None, help="Veuillez préciser le type de mesure conservatoire mise en place dans la description")
def SELECT_BOX_SIV_DECLENCHE(): return st.selectbox("Si un SIV est installé, a-t-il été déclenché ?", ['Oui', 'Non', "SIV absent du site"], placeholder=None)
def INPUT_PLAINTE(): return st.selectbox("Statut de la plainte", ["Déposée", "Dépôt prévu", "Pas de plainte prévue"])

# =============================================================================
# 3. GESTIONNAIRE DE LISTE DYNAMIQUE (FAITS)
# =============================================================================
def gerer_saisie_actes():
    st.markdown("##### 📝 Qualification détaillée de l'acte malveillant")
    if "liste_faits" not in st.session_state:
        st.session_state.liste_faits = [{"id": 0}]
    
    c_add, c_del, _ = st.columns([1, 1, 3])
    if c_add.button("➕ Ajouter un acte", help="Pour ajouter un acte malveillant supplémentaire"):
        new_id = st.session_state.liste_faits[-1]["id"] + 1 if st.session_state.liste_faits else 0
        st.session_state.liste_faits.append({"id": new_id})
    if c_del.button("🗑️ Retirer le dernier") and len(st.session_state.liste_faits) > 1:
        st.session_state.liste_faits.pop()

    resultats_faits = []
    for i, fait in enumerate(st.session_state.liste_faits):
        uid = fait["id"]
        st.markdown(f"**Acte n°{i+1}**")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            typologie = st.selectbox("1. Typologie", TYPOLOGIE_GLOBAL, key=f"typo_{uid}")
            
        with c2:
            raw_modes = list(REGLES_CASCADE.get(typologie, {}).keys()) if typologie in REGLES_CASCADE else ["Autre"]
            mode_op = st.selectbox("2. Mode Opératoire", trier_avec_autre_fin(raw_modes), key=f"mode_{uid}")
            
        with c3:
            liste_cibles_brutes = ["Autre"]
            if typologie in REGLES_CASCADE and mode_op in REGLES_CASCADE[typologie]:
                regle = REGLES_CASCADE[typologie][mode_op]
                # Si le mode opératoire peut toucher n'importe quoi (ex: Effraction), on charge toute la liste
                liste_cibles_brutes = TOUTES_CIBLES if regle == "ALL" else regle
                
            cible = st.selectbox("3. Cible Spécifique", trier_avec_autre_fin(liste_cibles_brutes + ["Autre"]), key=f"cible_{uid}")
        
        resultats_faits.append({"acte": typologie, "categorie": mode_op, "objet": cible})
        st.markdown("---")
        
    return resultats_faits

# =============================================================================
# 4. LOCALISATION
# =============================================================================
@st.cache_data
def load_parquet_data(file_path):
    if not os.path.exists(file_path): return pd.DataFrame()
    df = pd.read_parquet(file_path)
    if 'Commune' in df.columns:
        prefix = ""
        if 'Identifiant de référence' in df.columns: prefix = df['Identifiant de référence'].astype(str) + " - "
        elif 'GMR_Nom_Complet' in df.columns: prefix = "SITE - "
        df['Label_Recherche'] = prefix + df['Commune'].astype(str).str.upper() + " (" + df['code_postal'].astype(str) + ")"
    return df

def afficher_selecteurs_localisation():
    st.subheader("📍 Localisation de l'acte de malveillance")
    date_incident = INPUT_DATETIME()
    mode = st.radio("Type de lieu :", ["🏢 Site", "🌍 Commune"], horizontal=True)
    is_site = "Site" in mode
    path = "./data/donnees_site_RTE.parquet" if is_site else "./data/donnees_villes.parquet"
    df = load_parquet_data(path)
    
    if df.empty: 
        st.error(f"Fichier de données introuvable : {path}")
        return None
    
    rech = st.text_input("🔍 Rechercher", placeholder="Nom Site, Code, Ville...")
    sel = None
    if rech and len(rech) >= 2:
        mask = df["Label_Recherche"].str.contains(rech.upper(), na=False)
        if is_site and 'GMR_Nom_Complet' in df.columns: mask |= df["GMR_Nom_Complet"].str.contains(rech.upper(), na=False)
        filtered = df[mask]
        if not filtered.empty:
            choix = st.selectbox("Sélectionnez :", filtered["Label_Recherche"].head(30).tolist())
            sel = df[df["Label_Recherche"] == choix].iloc[0]
        else: st.warning("Aucun résultat.")

    if sel is not None:
        st.success(f"✅ {sel['Label_Recherche']}")
        data_loc = {
            "date": date_incident, 
            "type": "site" if is_site else "ville",
            "label_complet": sel["Label_Recherche"], 
            "commune": sel.get("Commune", "Inconnue"),
            "cp": str(sel.get("code_postal", "")), 
            "departement": sel.get("dep_nom", "N/A"), 
            "region": sel.get("reg_nom", "N/A"),
        }
        if is_site: data_loc.update({"id_ref": sel.get("Identifiant de référence", "N/A"), "gmr": sel.get("GMR_Nom_Complet", "N/A"), "gdp": sel.get("GDP_Nom_Complet", "N/A")})
        else: data_loc["id_ref"] = "N/A"
        return data_loc
    return None