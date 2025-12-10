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
**Formulaire de signalement.** Veuillez renseigner les champs ci-dessous pour structurer la remontée d'information vers **OpenCTI**.
""")

# -----------------------------------------------------------------------------
# 2. DONNÉES DE RÉFÉRENCE
# -----------------------------------------------------------------------------

# Vos catégories (CONSERVÉES TELLES QUELLES)
CATEGORIES_CIBLES = {
    "Infrastructures Réseau": ["Pylône", "Câble aérien", "Câble souterrain", "Transformateur", "Télécom", "Drapeau/Banderole", "Tag"],
    "Bâtiments & Sites": ["Bâtiment Industriel (BI)", "Bâtiment de relayage (BR)", "Mur/Palplanche", "Portail", "Drapeau/Banderole", "Tag"],
    "Bien matériel": ["Véhicule de service", "Outillage", "Touret", "Carburant", "Téléphone", "Ordinateur"],
    "Collaborateur": ["Collaborateur"], 
    "Autre": ["Autre"]
}

TYPES_ACTES = [
    "Vol", "Dégradation / Vandalisme", 
    "Intrusion", "Incendie volontaire", "Sabotage", "Agressions", "Inscription/Ajout illicite", "Sciage", "Déboulonage"
]

BARRIERES = ["Aucune", "Portail", "Palplanche", "Grillage simple", "Clôture électrifiée", "Mur", "Contrôle d'accès"]

# Génération des données fictives
def verifier_et_creer_donnees_demo():
    chemin_csv = "locations_db.csv"
    if not os.path.exists(chemin_csv):
        data = {
            "Région": ["Ile-de-France", "Ile-de-France", "Ile-de-France", "PACA", "PACA", "Auvergne-Rhône-Alpes"],
            "Département": ["Paris", "Yvelines", "Seine-et-Marne", "Bouches-du-Rhône", "Var", "Rhône"],
            "GMR": ["GMR-Paris-Nord", "GMR-Ouest", "GMR-Est", "GMR-Marseille", "GMR-Toulon", "GMR-Lyon"],
            "GDP": ["GDP-Batignolles", "GDP-Versailles", "GDP-Melun", "GDP-Prado", "GDP-Hyères", "GDP-Part-Dieu"], 
            "ID_Poste" : ["MEREN", "NANCY", "RECYS", "CAREN", "LYPOD", "BURES"]
        }
        df = pd.DataFrame(data)
        df.to_csv(chemin_csv, index=False)

verifier_et_creer_donnees_demo()

@st.cache_data
def charger_locations():
    if os.path.exists("locations_db.parquet"):
        return pd.read_parquet("locations_db.parquet")
    elif os.path.exists("locations_db.csv"):
        return pd.read_csv("locations_db.csv")
    else:
        return pd.DataFrame()

df_locations = charger_locations()

# -----------------------------------------------------------------------------
# 3. SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Connexion API")
    # Gestion sécurisée des secrets
    api_url = st.secrets["opencti"]["url"] if "opencti" in st.secrets else ""
    api_token = st.secrets["opencti"]["token"] if "opencti" in st.secrets else ""
    
    if api_url and api_token:
        st.success("✅ Identifiants chargés")
    else:
        st.warning("⚠️ Identifiants manquants dans secrets.toml")

# -----------------------------------------------------------------------------
# 4. SÉLECTEURS EN CASCADE (HORS DU FORMULAIRE)
# -----------------------------------------------------------------------------
# Permet l'interactivité instantanée

st.subheader("1. Contexte et Localisation")

# Ligne 1 : Date et Localisation Macro
col_top1, col_top2 = st.columns([1, 4])
with col_top1:
    date_detection = st.date_input("Date de détection", datetime.now())

with col_top2:
    if not df_locations.empty:
        # On divise la partie localisation en 5 colonnes étroites
        c_reg, c_dep, c_gmr, c_gdp, c_id = st.columns(5)
        
        with c_reg:
            region_sel = st.selectbox("Région", sorted(df_locations["Région"].unique()))
        with c_dep:
            deps = sorted(df_locations[df_locations["Région"] == region_sel]["Département"].unique())
            dept_sel = st.selectbox("Département", deps)
        with c_gmr:
            gmrs = sorted(df_locations[df_locations["Département"] == dept_sel]["GMR"].unique())
            gmr_sel = st.selectbox("GMR", gmrs)
        with c_gdp:
            gdps = sorted(df_locations[df_locations["GMR"] == gmr_sel]["GDP"].unique())
            gdp_sel = st.selectbox("GDP", gdps)
        with c_id:
            # CORRECTION : Ajout du selectbox pour l'ID Poste
            ids_dispos = sorted(df_locations[df_locations["GDP"] == gdp_sel]["ID_Poste"].unique())
            id_poste_sel = st.selectbox("ID Poste", ids_dispos)
    else:
        st.error("Base de données introuvable.")

# Ligne 2 : Typologie
st.write("") # Espacement
col_type1, col_type2, col_type3, col_type4 = st.columns(4)

with col_type1:
    acte_type = st.selectbox("Type d'acte", TYPES_ACTES)
with col_type2:
    cat_cible = st.selectbox("Catégorie Cible", list(CATEGORIES_CIBLES.keys()))
with col_type3:
    cible_specifique = st.selectbox("Objet Spécifique", CATEGORIES_CIBLES[cat_cible])
with col_type4:
    cible_orga = st.selectbox("Entité visée", ["RTE", "Enedis", "Prestataire"])

# -----------------------------------------------------------------------------
# 5. FORMULAIRE DE DÉTAILS (st.form)
# -----------------------------------------------------------------------------
st.markdown("---")

with st.form("incident_form"):
    st.subheader("2. Détails techniques & juridiques")
    
    # Bloc A : Détails physiques
    c1, c2 = st.columns(2)
    
    with c1:
        perimetre = st.selectbox("Barrière franchie", BARRIERES)
        reparation_provisioire = st.checkbox('Mesure provisoire mise en place ?', True)
    with c2:
        cout_estime = st.number_input("Coût estimé (€)", min_value=0.0, step=100.0)

    # Bloc B : Description et Impact
    c_desc, c_chk = st.columns([3, 1])
    with c_desc:
        description = st.text_area("Description des faits", height=100, placeholder="Détails du mode opératoire...")
    with c_chk:
        impact_client = st.checkbox("Impact Client (Coupure)")

    st.markdown("#### Aspects Légaux")
    cl1, cl2 = st.columns([1, 2])
    
    with cl1:
        st.write("") 
        plainte_deposee = st.checkbox("Plainte déposée ?", value=False)
    
    with cl2:
        fichier_plainte = st.file_uploader(
            "Pièce jointe (PV de plainte)", 
            type=['pdf', 'jpg', 'png'],
            help="Requis si plainte déposée."
        )

    st.markdown("---")
    submitted = st.form_submit_button("Envoyer le rapport 🚀", type="primary")

# -----------------------------------------------------------------------------
# 6. LOGIQUE DE VALIDATION ET ENVOI
# -----------------------------------------------------------------------------
if submitted:
    erreurs = []
    
    # Validation
    if not zone_id:
        erreurs.append("Veuillez indiquer la zone précise franchie.")
    
    if plainte_deposee and fichier_plainte is None:
        erreurs.append("Merci de joindre le fichier de plainte.")
        
    if not api_url or not api_token:
        erreurs.append("Configuration OpenCTI manquante.")

    if erreurs:
        for err in erreurs:
            st.error(f"⚠️ {err}")
    else:
        try:
            with st.spinner('Envoi en cours...'):
                # Construction du Payload
                payload = {
                    "titre": f"{acte_type} sur {cible_specifique} ({id_poste_sel})",
                    "date": date_detection.isoformat(),
                    "entite": cible_orga,
                    "localisation": {
                        "region": region_sel,
                        "gdp": gdp_sel,
                        "id_poste": id_poste_sel, # On utilise l'ID sélectionné
                        "zone_detail": zone_id
                    },
                    "classification": {
                        "acte": acte_type,
                        "cible_cat": cat_cible,
                        "cible_obj": cible_specifique
                    },
                    "impact": {
                        "cout": cout_estime,
                        "client": impact_client,
                        "perimetre": perimetre
                    },
                    "legal": {
                        "plainte": plainte_deposee,
                        "fichier": fichier_plainte.name if fichier_plainte else None
                    },
                    "description": description
                }
                
                # Simulation succès
                st.success("✅ Incident enregistré avec succès !")
                with st.expander("Voir le JSON généré"):
                    st.json(payload)
                    
        except Exception as e:
            st.error(f"Erreur technique : {e}")