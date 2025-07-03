import streamlit as st
from app import utils
from app.pages import home, comparatif, entreprise, alignement

st.set_page_config(page_title="Rapport de qualification", layout="wide")
st.title("Rapport de qualification")

# --- UPLOADER ---
uploaded_file = st.file_uploader("Dépose ton fichier Excel ici (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Lecture dynamique depuis le fichier uploadé
    df_comp, df_ent, df_align = utils.load_data(uploaded_file)

    # Navigation sur le côté
    page = st.sidebar.radio("Navigation", ["Home", "Comparatif", "Entreprise", "Alignement avec le besoin"])

    # Affichage dynamique de la page
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