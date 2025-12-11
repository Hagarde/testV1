import streamlit as st
import utils 
from datetime import datetime

def app():
    st.header("📝 Formulaire : Sûreté des Personnes")
    
    # CORRECTION 1 : On appelle la fonction sans argument (elle gère le choix interne/ville)
    loc_data = utils.afficher_selecteurs_localisation(referentiel="Ville")
    
    st.markdown("---")

    with st.form("form_personnel"):
        st.subheader("Détails de l'agression")
        
        # CORRECTION 2 : On utilise vraiment les colonnes avec 'with'
        c1, c2 = st.columns(2)
        
        with c1:
            # Sécurité : on met une liste par défaut si "Personnel" n'est pas dans utils
            liste_actes = utils.TYPE_ACTE.get("Personnel", ["Agression Verbale", "Agression Physique", "Menace", "Harcèlement"])
            acte_type = st.selectbox("Type d'acte", liste_actes)
            date_evt = st.date_input("Date de l'incident", datetime.now())

        with c2:
            description = st.text_area("Description des faits", height=100, placeholder="Détails du contexte...")

        st.markdown("#### Aspects Légaux")
        
        cl1, cl2 = st.columns([1, 2])
        with cl1:
            st.write("") # Petit espace pour l'alignement vertical
            plainte_deposee = st.checkbox("Plainte déposée ?", value=False)
        with cl2:
            fichier_plainte = st.file_uploader("Pièce jointe (PV)", type=['pdf', 'jpg', 'png'])
            
        # CORRECTION 3 : Le bouton est DANS le form (indenté)
        submit = st.form_submit_button("Envoyer Rapport 🚨")

    # La logique de traitement est en dehors du form, déclenchée par la variable 'submit'
    if submit:
        if loc_data:
            st.success(f"Signalement '{acte_type}' enregistré pour {loc_data.get('identifiant', 'Inconnu')}")
            # Ajouter ici la logique d'envoi vers OpenCTI
        else:
            st.error("Veuillez sélectionner une localisation.")
