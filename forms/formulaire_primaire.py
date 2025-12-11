import streamlit as st
import utils  # On réutilise notre fichier utils
from datetime import datetime

def app():
    st.header("📝 Formulaire : Primaire")
    # 1. Appel de la localisation partagée
    loc_data = utils.afficher_selecteurs_localisation(referentiel="Ville")
    # 2. Champs spécifiques à l'Intrusion
    with st.form("form_intrusion"):
        st.subheader("Détails de l'intrusion")
    
        c1, c2 = st.columns(2)
        with c1:
            date_evt = st.date_input("Date de l'intrusion")
            cat_cible = st.selectbox("Catégorie Cible", sorted(list(utils.CATEGORIES_CIBLES.keys())) + ["Autre"])
            perimetre = st.selectbox("Obstacle/Protection périmétrique franchie", sorted(utils.BARRIERES) + ["Autre"], help="")
            reparation_provisioire = st.selectbox("Est-ce que des mesures provisoires ont été mises en place ?",['Oui', 'Non'])
        with c2:
            acte_type = st.selectbox("Type d'acte", utils.TYPE_ACTE["Primaire"])
            cible_specifique = st.selectbox("Objet Spécifique", sorted(utils.CATEGORIES_CIBLES[cat_cible]) + ["Autre"])
            cout_estime = st.number_input("Coût estimé (k€)", min_value=0, step=1)
            impact_client = st.selectbox("Est-ce qu'un client a été impacté ?", ['Oui', 'Non'])       
        description = st.text_area("Description du cheminement")

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
        
        submit = st.form_submit_button("Envoyer Rapport 🚨")
    
    if submit:
        # Ici, ta logique d'envoi vers OpenCTI
        st.success(f"Intrusion au poste {loc_data['id_poste']} signalée !")