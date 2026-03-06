import streamlit as st
import os
from datetime import datetime

# Import des modules personnalisés
import utils        
import generate_pdf 

# =============================================================================
# CONFIGURATION GÉNÉRALE
# =============================================================================
st.set_page_config(page_title="Portail acte de malveillances", page_icon="🛡️", layout="wide")
MEDIA_ROOT = "./data/media"
os.makedirs(MEDIA_ROOT, exist_ok=True)

def sauvegarder_fichier_local(uploaded_file):
    if uploaded_file is None: return None
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{uploaded_file.name}".replace(" ", "_")
        file_path = os.path.join(MEDIA_ROOT, safe_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"❌ Erreur sauvegarde fichier : {e}")
        return None

# =============================================================================
# UI PRINCIPALE
# =============================================================================
st.title("🛡️ Detectout")
st.markdown("---")

# 1. DATE ET LOCALISATION
loc_data = utils.afficher_selecteurs_localisation()
is_urgent = st.checkbox("⚠️ Evénement URGENT", help="Cochez si une intervention immédiate est requise.")

st.markdown("---")

# 2. QUALIFICATION DES FAITS
st.subheader("2. Qualification des faits")
st.info("💡 Vous pouvez ajouter plusieurs actes pour un même acte de malveillance.")
liste_faits_saisis = utils.gerer_saisie_actes()

# 3. DÉTAILS TECHNIQUES & OBSTACLES
st.subheader("3. Détails techniques")
c1, c2 = st.columns(2)

with c1:
    cout_estime = utils.INPUT_COUT_ESTIME()
    reparation_provisioire = utils.SELECT_BOX_MESURE_PROVISOIRE()


with c2:
    # --- CHANGEMENT MULTISELECT ---
    options_obstacles = getattr(utils, 'BARRIERES', [])
    
    obstacles_selectionnes = st.multiselect(
        "Dégradation périmétrique",
        options=options_obstacles,
        default=[],
        help="Renseignez le type de protection périmétrique franchis ou endommagé"
    )
    
    siv_present = utils.SELECT_BOX_SIV_DECLENCHE()

description = utils.INPUT_DESCRIPTION()
st.markdown("""**Avertissement relatif à la protection des données personnelles**
            
Pour rappel, dans les zones de commentaire libre, vous devez impérativement rédiger de façon objective et jamais excessive ou insultante. Toute donnée considérée comme sensible (origine raciale ou ethnique, opinions politiques, philosophiques ou religieuses, appartenance syndicale, données relatives à la santé ou à la vie sexuelle) doit être exclue. Toute donnée permettant d’identifier des tiers doit être également exclue.""")
st.markdown("---")

# 4. JURIDIQUE & PREUVES
st.subheader("4. Aspects juridiques & Pièces jointes")
col_jur_1, col_jur_2 = st.columns(2)
with col_jur_1:
    statut_plainte = utils.INPUT_PLAINTE()
with col_jur_2:
    st.markdown("**Ajouter une pièce jointe (plainte, photos, ...)**")
    uploaded_file = st.file_uploader("Format : PDF, JPG, PNG", type=['pdf', 'png', 'jpg', 'jpeg'])
st.markdown("---")

# =============================================================================
# PRÉPARATION DES DONNÉES
# =============================================================================
donnees_valides = (loc_data is not None)
final_data = {}

if donnees_valides:
    final_data = loc_data.copy()
    
    # LOGIQUE INTELLIGENTE OBSTACLES : Si vide, on envoie ["Aucun"]
    obs_final = obstacles_selectionnes if obstacles_selectionnes else ["Aucun"]

    final_data.update({
        "liste_faits": liste_faits_saisis,
        "obstacles_list": obs_final, 
        "cout": cout_estime,
        "mesure_provisoire": reparation_provisioire,
        "siv": siv_present,
        "plainte": statut_plainte,
        "desc": description,
        "urgent": is_urgent, # Envoi du booléen
        "chemin_fichier": None 
    })
    
    # Rétro-compatibilité
    if liste_faits_saisis:
        final_data["acte"] = liste_faits_saisis[0].get('acte')
        final_data["cat_cible"] = liste_faits_saisis[0].get('categorie')
        final_data["cible_spec"] = liste_faits_saisis[0].get('objet')
        final_data["obstacle"] = ", ".join(obs_final)
    else:
        final_data["acte"] = "Incident"
        final_data["obstacle"] = "Aucun"

# =============================================================================
# ACTIONS
# =============================================================================
st.subheader("🚀 Actions")
col_pdf, col_db = st.columns(2)

with col_pdf:
    if st.button("📄 Générer PDF", disabled=not donnees_valides):
        try:
            pdf_bytes = generate_pdf.generer_pdf(final_data)
            nom_pdf = f"Rapport_{final_data['date'].strftime('%Y-%m-%d')}_Securite.pdf"
            st.download_button("📥 Télécharger PDF", data=pdf_bytes, file_name=nom_pdf, mime="application/pdf", use_container_width=True)
            st.success("PDF prêt !")
        except Exception as e:
            st.error(f"Erreur PDF : {e}")

with col_db:
    if st.button("💾 Enregistrer en Base", type="primary", use_container_width=True, disabled=True):# disabled=not donnees_valides
        with st.spinner("Enregistrement..."):
            if uploaded_file:
                path = sauvegarder_fichier_local(uploaded_file)
                if path: final_data["chemin_fichier"] = path
            
            result = db_manager.sauvegarder_incident_postgres(final_data)
            
            if result and result.get("success"):
                st.success(f"✅ Enregistré avec succès ! (ID: {result['id']})")
                st.balloons()
            else:
                st.error("❌ Erreur SQL")
                st.error(result.get("error") if result else "Pas de réponse")
                if result and result.get("trace"):
                    with st.expander("Détails"): st.code(result["trace"])