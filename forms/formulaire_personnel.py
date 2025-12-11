import streamlit as st
import utils  # On réutilise notre fichier utils
from datetime import datetime

def app():
    st.header("📝 Formulaire : Personnel")
    loc_data = utils.afficher_selecteurs_localisation(referentiel="Ville")
    with st.form("form_intrusion"):
        st.subheader("Détails de l'aggression")
        c1, c2 = st.columns(2)
        acte_type = st.selectbox("Type d'acte", utils.TYPE_ACTE["Personnel"]) 
        description = st.text_area("Description du cheminement")
    st.markdown("#### Aspects Légaux")
    cl1, cl2 = st.columns([1, 2])
    with cl1:
        st.write("") 
        plainte_deposee = st.checkbox("Plainte déposée ?", value=False)
        
    with cl2:
        fichier_plainte = st.file_uploader("Pièce jointe (PV)", type=['pdf', 'jpg', 'png'])
    
    if submit:
        # Ici, ta logique d'envoi vers OpenCTI
        st.success(f"Intrusion au poste {loc_data['id_poste']} signalée !")