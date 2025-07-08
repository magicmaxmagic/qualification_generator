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
    st.image(
        "https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg",
        use_container_width=True,
    )
    st.markdown("---")

    # 1) lire le dernier chemin ou URL depuis le cookie
    last_ref = sidebar.cookies.get("excel_path") or ""

    # 2) champ texte pour chemin local ou URL, pré-rempli
    path_input = st.text_input(
        "Chemin local ou URL du fichier Excel",
        value=last_ref,
        key="excel_path_input",
    )

    # 3) uploader drag & drop
    upload = st.file_uploader(
        "Ou déposez un fichier Excel (.xlsx)",
        type="xlsx",
        key="uploader",
    )
    if upload:
        os.makedirs("uploads", exist_ok=True)
        saved_path = os.path.abspath(os.path.join("uploads", upload.name))
        with open(saved_path, "wb") as f:
            f.write(upload.getvalue())
        path_input = saved_path
        sidebar.cookies["excel_path"] = saved_path
        st.session_state["excel_path_input"] = saved_path

    # 4) déterminer la source effective
    if path_input.startswith(("http://", "https://")):
        import requests
        from io import BytesIO

        url = path_input
        # pour forcer le téléchargement sur SharePoint (“?download=1”)
        if "sharepoint.com" in url and "download=" not in url:
            base = url.split("?")[0]
            url = f"{base}?download=1"

        resp = requests.get(url)
        try:
            resp.raise_for_status()
        except Exception as e:
            st.error(f"Échec du téléchargement ({resp.status_code}) : {e}")
            st.stop()

        uploaded_file = BytesIO(resp.content)
        # reconstitue un nom de fichier valide
        uploaded_file.name = os.path.basename(path_input.split("?")[0])
        # on met à jour le cookie
        sidebar.cookies["excel_path"] = path_input

    # sinon, chemin local existant
    elif os.path.isfile(path_input):
        with open(path_input, "rb") as f:
            data = f.read()
        from io import BytesIO
        uploaded_file = BytesIO(data)
        uploaded_file.name = os.path.basename(path_input)
        sidebar.cookies["excel_path"] = path_input

    else:
        st.error("Fichier non trouvé. Déposez-le, corrigez le chemin ou utilisez une URL valide.")
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