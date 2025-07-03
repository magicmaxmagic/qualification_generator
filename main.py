import streamlit as st
from app import utils
from app.pages import home, comparatif, entreprise, alignement
from app.pages.alignement import display
from app.utils import load_data 
# --- DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT ---
st.set_page_config(
    page_title="Tableau de bord IVÉO",
    layout="wide",
    page_icon="🟢"
)


# --- CHARGER LES STYLES ---
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg", use_container_width=True)
    st.markdown("---")  # Ligne de séparation
    
#st.markdown("<hr style='border:1px solid #72bf44; margin-top:-10px;'>", unsafe_allow_html=True)

# --- UPLOADER ---
uploaded_file = st.file_uploader("Dépose ton fichier Excel ici (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Lecture dynamique depuis le fichier uploadé
    df_comp, df_ent, df_align = utils.load_data(uploaded_file)
    # --- Navigation dans la sidebar ---
    page = st.sidebar.radio("Navigation", ["Home", "Comparatif", "Entreprise", "Alignement avec le besoin"])

    # --- Affichage dynamique en fonction de la page choisie ---
    if page == "Home":
        home.display(df_comp)
    elif page == "Comparatif":
        comparatif.display(df_comp)
    elif page == "Entreprise":
        entreprise.display(df_comp, df_ent)
    elif page == "Alignement avec le besoin":
        alignement.display(df_align)
else:
    st.info("Merci de déposer un fichier Excel pour générer le rapport.")