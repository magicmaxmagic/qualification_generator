# main.py
import os
import uuid
import io
import streamlit as st
from app import utils
from app.pages import home, comparatif, entreprise, alignement

# -----------------------------------------------------------------------------
# 1) Configuration de la page — DOIT ÊTRE LA TOUTE 1re COMMANDE STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tableau de bord IVÉO",
    page_icon="https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg",
    layout="wide",
)

# -----------------------------------------------------------------------------
# 2) Charger votre CSS
# -----------------------------------------------------------------------------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3) Initialiser la session
# -----------------------------------------------------------------------------
if "file_path" not in st.session_state:
    st.session_state.file_path = None
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -----------------------------------------------------------------------------
# 4) Barre latérale : logo, uploader OU changement de fichier, puis nav
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg",
        use_container_width=True
    )
    st.markdown("---")

    # Si on n’a pas encore de fichier → uploader
    if st.session_state.file_path is None:
        uploaded = st.file_uploader(
            "Déposez votre fichier Excel (.xlsx)",
            type="xlsx",
            key="uploader"
        )
        if uploaded is not None:
            # Écrire le fichier sur disque
            tmp_name = f"/tmp/{uuid.uuid4()}.xlsx"
            with open(tmp_name, "wb") as f:
                f.write(uploaded.getvalue())
            st.session_state.file_path = tmp_name
    else:
        # Sinon on l’affiche et on propose de le remplacer
        fname = os.path.basename(st.session_state.file_path)
        st.markdown(f"**Fichier chargé :** {fname}")
        if st.button("🔄 Changer de fichier"):
            try:
                os.remove(st.session_state.file_path)
            except OSError:
                pass
            st.session_state.file_path = None

    st.markdown("---")

    # Navigation persistante
    st.session_state.page = st.radio(
        "Navigation",
        ["Home", "Comparatif", "Entreprise", "Alignement avec le besoin"],
        index=["Home","Comparatif","Entreprise","Alignement avec le besoin"]
              .index(st.session_state.page),
        key="page_selector"
    )

# -----------------------------------------------------------------------------
# 5) Tant que pas de fichier, on stoppe
# -----------------------------------------------------------------------------
if st.session_state.file_path is None:
    st.info("Merci de déposer un fichier pour générer le rapport.")
    st.stop()

# -----------------------------------------------------------------------------
# 6) Chargement (et caching) du DataFrame
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _load(path):
    # utils.load_data doit accepter un chemin
    return utils.load_data(path)

# Relire si le fichier a changé
if (
    "df_comp" not in st.session_state
    or st.session_state.file_path != st.session_state.get("last_path")
):
    df_comp, df_ent, df_align = _load(st.session_state.file_path)
    st.session_state.df_comp     = df_comp
    st.session_state.df_ent      = df_ent
    st.session_state.df_align    = df_align
    st.session_state.last_path   = st.session_state.file_path
else:
    df_comp  = st.session_state.df_comp
    df_ent   = st.session_state.df_ent
    df_align = st.session_state.df_align

# -----------------------------------------------------------------------------
# 7) Dispatcher vers la page choisie
# -----------------------------------------------------------------------------
page = st.session_state.page
if page == "Home":
    home.display(df_comp)
elif page == "Comparatif":
    comparatif.display(df_comp)
elif page == "Entreprise":
    entreprise.display(df_comp, df_ent)
else:
    alignement.display(df_align)