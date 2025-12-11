import streamlit as st
import utils  # On réutilise notre fichier utils
from datetime import datetime

def app():
    st.header("📝 Formulaire : Personnel")
    # 1. Appel de la localisation partagée
    loc_data = utils.afficher_selecteurs_localisation(referentiel="Ville")
    # 2. Champs spécifiques à l'Intrusion
    with st.form("form_intrusion"):
        st.subheader("Détails de l'intrusion")
    
        c1, c2 = st.columns(2)
        with c1:
            date_evt = st.date_input("Date de l'intrusion")
        with c2:
            acte_type = st.selectbox("Type d'acte", utils.TYPE_ACTE["Personnel"]) 
        description = st.text_area("Description du cheminement")
        
        submit = st.form_submit_button("Envoyer Rapport 🚨")
    
    if submit:
        # Ici, ta logique d'envoi vers OpenCTI
        st.success(f"Intrusion au poste {loc_data['id_poste']} signalée !")