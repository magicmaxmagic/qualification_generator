import streamlit as st
import os

# -----------------------------------------------------------------------------
# 1) Configuration de la page — Doit être **le tout premier** appel Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tableau de bord IVÉO",
    page_icon="https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg",
    layout="wide",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    },
)

# -----------------------------------------------------------------------------
# 2) On importe le reste
# -----------------------------------------------------------------------------
import io
from app import utils
from app.pages import home, comparatif, entreprise, alignement
import sidebar  # votre sidebar.py à la racine

# -----------------------------------------------------------------------------
# 3) Masquer “View source on GitHub”
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="collapsedControl"] + div [data-testid="source-link"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 4) Charger le CSS perso
# -----------------------------------------------------------------------------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5) Sidebar : logo, uploader, navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg", use_container_width=True)
    st.markdown("---")

    # 5.a) chemin local persistent via cookies
    last_path = sidebar.cookies.get("excel_path") or ""
    path_input = st.text_input(
        "Ou entrez le chemin local du fichier Excel",
        value=last_path,
        key="excel_path_input"
    )

    uploaded_file = None
    # si le fichier existe localement, on le charge
    if path_input and os.path.isfile(path_input):
        sidebar.cookies["excel_path"] = path_input
        with open(path_input, "rb") as f:
            data = f.read()
        from io import BytesIO
        uploaded_file = BytesIO(data)
        uploaded_file.name = os.path.basename(path_input)
    else:
        # fallback sur l’upload classique
        uploaded_file = st.file_uploader(
            "Déposez votre fichier Excel (.xlsx)",
            type="xlsx",
            key="uploader",
        )

    if not uploaded_file:
        st.info("Merci de déposer un fichier pour générer le rapport.")
        st.stop()

    st.markdown("---")
    page = st.radio(
        "Navigation",
        ("Home", "Comparatif", "Entreprise", "Alignement avec le besoin"),
        key="page_selector",
    )

# -----------------------------------------------------------------------------
# 6) Chargement + cache des données
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_from_bytes(name: str, raw: bytes):
    return utils.load_data(io.BytesIO(raw))

df_comp, df_ent, df_align = load_from_bytes(
    uploaded_file.name, uploaded_file.getvalue()
)

# -----------------------------------------------------------------------------
# 7) Dispatch selon la page
# -----------------------------------------------------------------------------
if page == "Home":
    home.display(df_comp)
elif page == "Comparatif":
    comparatif.display(df_comp)
elif page == "Entreprise":
    entreprise.display(df_comp, df_ent)
else:
    alignement.display(df_align)

# -----------------------------------------------------------------------------
# 8) Sauvegarde **une seule fois** des cookies
# -----------------------------------------------------------------------------
if "cookies_saved" not in st.session_state:
    sidebar.cookies.save()
    st.session_state["cookies_saved"] = True