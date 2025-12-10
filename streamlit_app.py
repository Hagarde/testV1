import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pycti import OpenCTIApiClient

# -----------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Déclaration d'Incident Sécurité",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Portail de Remontée d'Incidents")
st.markdown("""
Ce formulaire permet de structurer la remontée d'information avant envoi vers **OpenCTI**.
Les champs de localisation se mettent à jour dynamiquement.
""")

# -----------------------------------------------------------------------------
# 2. GESTION DES DONNÉES DE RÉFÉRENCE (MOCKUP & CHARGEMENT)
# -----------------------------------------------------------------------------

# Dictionnaires pour la catégorisation (Facilement éditable)
CATEGORIES_CIBLES = {
    "Infrastructures Réseau": ["Pylône", "Câble aérien", "Câble souterrain", "Transformateur", "Armoire"],
    "Bâtiments & Sites": ["Mur extérieur", "Ajout d'un objet (Drapeau, Déchets, ...)", "Entrepôt logistique"],
    "Matériel & Véhicules": ["Véhicule de service", "Outillage", "Stock de cuivre", "Groupe électrogène"],
    "Systèmes d'Information": ["Poste de travail", "Serveur", "Données clients", "Application métier"],
    "Autre": ["Autre"]
}

TYPES_ACTES = [
    "Vol (Simple)", "Vol (Effraction)", "Dégradation / Vandalisme", 
    "Intrusion", "Incendie", "Sabotage", "Agressions"
]

BARRIERES = ["Aucune", "Portail", "Palplanche", "Grillage simple", "Clôture électrifiée", "Mur", "Contrôle d'accès"]

# Fonction pour créer un fichier de données fictif si aucun n'existe (pour que le code tourne direct)
def verifier_et_creer_donnees_demo():
    chemin_csv = "locations_db.csv"
    if not os.path.exists(chemin_csv):
        data = {
            "Région": ["Ile-de-France", "Ile-de-France", "Ile-de-France", "PACA", "PACA", "Auvergne-Rhône-Alpes"],
            "Département": ["Paris", "Yvelines", "Seine-et-Marne", "Bouches-du-Rhône", "Var", "Rhône"],
            "GMR": ["GMR-Paris-Nord", "GMR-Ouest", "GMR-Est", "GMR-Marseille", "GMR-Toulon", "GMR-Lyon"],
            "GDP": ["GDP-Batignolles", "GDP-Versailles", "GDP-Melun", "GDP-Prado", "GDP-Hyères", "GDP-Part-Dieu"]
        }
        df = pd.DataFrame(data)
        df.to_csv(chemin_csv, index=False)

verifier_et_creer_donnees_demo()

# Chargement optimisé avec Cache
@st.cache_data
def charger_locations():
    # Priorité au format Parquet (plus rapide), sinon CSV
    if os.path.exists("locations_db.parquet"):
        return pd.read_parquet("locations_db.parquet")
    elif os.path.exists("locations_db.csv"):
        return pd.read_csv("locations_db.csv")
    else:
        return pd.DataFrame() # Retourne vide si rien trouvé

df_locations = charger_locations()

# -----------------------------------------------------------------------------
# 3. SIDEBAR : CONNEXION OPENCTI
# -----------------------------------------------------------------------------
# Récupération depuis secrets.toml ou champs vides
api_url = st.secrets["opencti"]["url"] if "opencti" in st.secrets else ""
api_token = st.secrets["opencti"]["token"] if "opencti" in st.secrets else ""

# -----------------------------------------------------------------------------
# 4. SÉLECTEURS EN CASCADE (HORS FORMULAIRE)
# -----------------------------------------------------------------------------
# Ils sont hors du st.form pour permettre le rafraîchissement immédiat de la page

st.subheader("1. Localisation de l'incident")

if not df_locations.empty:
    col_loc1, col_loc2, col_loc3, col_loc4 = st.columns(4)
    
    with col_loc1:
        region_sel = st.selectbox("Région", sorted(df_locations["Région"].unique()))
    
    with col_loc2:
        # Filtre les départements selon la région choisie
        deps = sorted(df_locations[df_locations["Région"] == region_sel]["Département"].unique())
        dept_sel = st.selectbox("Département", deps)
        
    with col_loc3:
        # Filtre les GMR selon le département choisi
        gmrs = sorted(df_locations[df_locations["Département"] == dept_sel]["GMR"].unique())
        gmr_sel = st.selectbox("GMR", gmrs)
        
    with col_loc4:
        # Filtre les GDP selon le GMR choisi
        gdps = sorted(df_locations[df_locations["GMR"] == gmr_sel]["GDP"].unique())
        gdp_sel = st.selectbox("GDP", gdps)
else:
    st.error("Erreur : Base de données de localisation introuvable.")


st.subheader("2. Typologie")
col_type1, col_type2, col_type3, col_type4 = st.columns(4)

with col_type1:
    acte_type = st.selectbox("Type d'acte malveillant", TYPES_ACTES)
with col_type2:
    cat_cible = st.selectbox("Catégorie de la cible", list(CATEGORIES_CIBLES.keys()))
with col_type3:
    # Affiche les sous-catégories basées sur la catégorie
    cible_specifique = st.selectbox("Objet/Cible spécifique", CATEGORIES_CIBLES[cat_cible])
with col_type4 : 
    cible = st.selectbox("Organisation ciblée", ["RTE", "Enedis", "Prestataire"])
# -----------------------------------------------------------------------------
# 5. FORMULAIRE DE DÉTAILS (st.form)
# -----------------------------------------------------------------------------
st.markdown("---")

with st.form("incident_form"):
    st.subheader("3. Détails et Preuves")
    
    c1, c2 = st.columns(2)
    
    with c1:
        date_detection = st.date_input("Date de détection", datetime.now())
        perimetre = st.selectbox("Périmètre/Barrière enfreinte", BARRIERES)
        
    with c2:
        cout_estime = st.number_input("Estimation du coût (€)", min_value=0.0, step=100.0, format="%.2f")
        impact_client = st.checkbox("Impact Client avéré (Coupure, Retard service)")
    
    description = st.text_area("Description détaillée des faits", height=120, placeholder="Chronologie, mode opératoire...")

    st.markdown("#### Aspects Légaux")
    cl1, cl2 = st.columns([1, 2])
    
    with cl1:
        st.write("") # Spacer
        st.write("") 
        plainte_deposee = st.checkbox("Une plainte a été déposée", value=False)
    
    with cl2:
        # L'upload est toujours visible, mais le label guide l'utilisateur
        fichier_plainte = st.file_uploader(
            "Téléverser le Récépissé de Plainte (ou PV)", 
            type=['pdf'],
            help="Obligatoire si la case 'Plainte' est cochée."
        )

    st.markdown("---")
    submitted = st.form_submit_button("Valider et Transmettre 🚀", type="primary")

# -----------------------------------------------------------------------------
# 6. LOGIQUE DE SOUMISSION
# -----------------------------------------------------------------------------
if submitted:
    # --- A. Validation des champs ---
    erreurs = []
    
    if not zone_id:
        erreurs.append("L'identifiant de la zone franchie est requis.")
    
    if plainte_deposee and fichier_plainte is None:
        erreurs.append("Une plainte est déclarée mais aucun fichier n'a été joint.")
        
    if not api_url or not api_token:
        erreurs.append("Les identifiants OpenCTI sont manquants.")

    # --- B. Traitement ---
    if erreurs:
        for err in erreurs:
            st.error(f"⚠️ {err}")
    else:
        try:
            with st.spinner('Connexion et envoi vers OpenCTI...'):
                # 1. Connexion (Instance réelle)
                # opencti_api_client = OpenCTIApiClient(api_url, api_token)
                
                # 2. Préparation du Payload (JSON)
                # C'est ici que vous mappez vos champs Streamlit vers le format STIX/OpenCTI
                incident_payload = {
                    "name": f"{acte_type} - {gdp_sel}",
                    "incident_type": acte_type,
                    "description": description,
                    "date": date_detection.isoformat(),
                    "location_hierarchy": {
                        "region": region_sel,
                        "department": dept_sel,
                        "gmr": gmr_sel,
                        "gdp": gdp_sel,
                    },
                    "impact": {
                        "cost": cout_estime,
                        "client_impact": impact_client
                    },
                    "target": {
                        "category": cat_cible,
                        "object": cible_specifique
                    },
                    "legal": {
                        "complaint_filed": plainte_deposee,
                        "file_name": fichier_plainte.name if fichier_plainte else None
                    }
                }
                
                # 3. Simulation de l'envoi (À remplacer par opencti_api_client.incident.create(...))
                # time.sleep(1) # Simulation latence
                
                st.success("✅ Incident créé avec succès dans OpenCTI !")
                
                # Affichage des données transmises pour vérification
                with st.expander("Voir les données JSON transmises"):
                    st.json(incident_payload)
                    
        except Exception as e:
            st.error(f"Erreur technique lors de l'envoi : {str(e)}")