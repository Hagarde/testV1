# streamlit_app.py
import streamlit as st
# Import des formulaires spécifiques (nous allons les créer juste après)
from forms import formulaire_personnel, formulaire_chantier, formulaire_primaire, formulaire_tertiaire


st.set_page_config(page_title="Portail Incidents", page_icon="🛡️", layout="wide")

st.title("🛡️ Portail de Remontée d'Incidents")

nature_incident = st.selectbox(
    "Qui êtes-vous ?",
    [
        "Primaire",
        "Tertiaire",
        "Chantier",
        "Personnel RTE sur terrain"
    ], index=None
)

st.markdown("---")

# --- LOGIQUE DE ROUTAGE ---
if nature_incident == "Primaire":
    formulaire_primaire.app()
elif nature_incident == "Tertiaire":
    formulaire_tertiaire.app()
elif nature_incident == "Chantier":
    formulaire_chantier.app()
elif nature_incident == "Personnel RTE sur terrain":
    formulaire_personnel.app()