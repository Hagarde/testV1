import streamlit as st
import utils  # On réutilise notre fichier utils
from datetime import datetime

def app():
    st.header("📝 Formulaire : Tertiaire")
    
    # 1. Appel de la localisation (HORS FORMULAIRE)
    loc_data = utils.afficher_selecteurs_localisation(referentiel="GMR") # J'ai retiré referentiel="Ville" car ta nouvelle fonction gère tout
    
    st.markdown("---")

    # 2. Sélecteurs Interactifs (HORS FORMULAIRE pour l'interactivité)
    # On les place ici pour qu'ils se mettent à jour instantanément
    st.subheader("1. Qualification de l'événementInformations Générales")
    col_interactif_1, col_interactif_2 , col_interactif_3= st.columns(3)
    with col_interactif_1:
        acte_type = st.selectbox("Type d'acte", utils.TYPE_ACTE.get("Tertiaire", ["Indéfini"]))
    with col_interactif_2:
        # Ce widget, étant hors du form, rechargera la page à chaque changement
        cat_cible = st.selectbox(
            "Catégorie Cible", 
            sorted(list(utils.CATEGORIES_CIBLES.keys())) + ["Autre"]
        )
    
    with col_interactif_3:
        # Calcul dynamique de la liste en fonction du choix précédent
        if cat_cible == "Autre":
            liste_objets = ["Autre"]
        else:
            # On utilise .get par sécurité + ajout de "Autre"
            liste_objets = sorted(utils.CATEGORIES_CIBLES.get(cat_cible, [])) + ["Autre"]
            
        cible_specifique = st.selectbox("Objet Spécifique", liste_objets)

    # 3. Le reste du Formulaire (DANS LE FORMULAIRE)
    # On remet st.form pour les champs qui ne nécessitent pas d'interactivité immédiate
    with st.form("form_intrusion"):
        st.subheader("2. Détails techniques & juridiques")
    
        c1, c2 = st.columns(2)
        with c1:
            
            perimetre = st.selectbox("Obstacle franchi", sorted(utils.BARRIERES) + ["Autre"])
            
            # On récupère ici les valeurs choisies plus haut pour les inclure au submit si besoin,
            # mais visuellement elles sont déjà affichées au-dessus.
            
        with c2:
            cout_estime = st.number_input("Coût estimé (k€)", min_value=0, step=1)
            reparation_provisioire = st.selectbox("Mesures provisoires ?",['Oui', 'Non'])
        
        description = st.text_area("Description du cheminement")

        st.markdown("#### Aspects Légaux")
        cl1, cl2 = st.columns([1, 2])
        with cl1:
            st.write("") 
            plainte_deposee = st.checkbox("Plainte déposée ?", value=False)
        
        with cl2:
            fichier_plainte = st.file_uploader("Pièce jointe (PV)", type=['pdf', 'jpg', 'png'])
        
        submit = st.form_submit_button("Envoyer Rapport 🚨")
    
    if submit:
        # Lors de l'envoi, on a accès à TOUTES les variables (celles hors du form et celles dedans)
        if loc_data:
             st.success(f"Incident enregistré : {cat_cible} / {cible_specifique} au poste {loc_data.get('identifiant', 'Inconnu')}")
        else:
             st.error("Erreur de localisation")