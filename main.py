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
from app.pages import analyse_comparative, home, entreprise, solution, chatbot
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
# Fichier styles.css supprimé - styles intégrés dans le code ci-dessus

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
    default_path = sidebar.cookies.get("excel_path") or ""

    # 2) uploader drag & drop
    upload = st.file_uploader(
        "Ou déposez un fichier Excel (.xlsx)",
        type="xlsx",
        key="uploader",
    )
    path_input = default_path
    if upload:
        os.makedirs("uploads", exist_ok=True)
        saved_path = os.path.abspath(os.path.join("uploads", upload.name))
        with open(saved_path, "wb") as f:
            f.write(upload.getvalue())
        path_input = saved_path
        sidebar.cookies["excel_path"] = saved_path

    # 3) champ texte pour chemin local ou URL, pré-rempli
    path_input = st.text_input(
        "Chemin local ou URL du fichier Excel",
        value=path_input,
        key="excel_path_input",
    )

    # 4) déterminer la source effective
    uploaded_file = None
    if path_input.startswith(("http://", "https://")):
        import requests
        from io import BytesIO

        url = path_input
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
        uploaded_file.name = os.path.basename(path_input.split("?")[0])
        sidebar.cookies["excel_path"] = path_input

    elif os.path.isfile(path_input):
        with open(path_input, "rb") as f:
            data = f.read()
        from io import BytesIO
        uploaded_file = BytesIO(data)
        uploaded_file.name = os.path.basename(path_input)
        sidebar.cookies["excel_path"] = path_input

    if not uploaded_file:
        st.error("Fichier non trouvé. Déposez-le, corrigez le chemin ou utilisez une URL valide.")
        st.stop()

    st.markdown("---")
    page = st.radio(
        "Navigation",
        ("Entreprise", "Solution", "Analyse comparative", "Assistant IA"),
        key="page_selector",
    )
# -----------------------------------------------------------------------------
# 6) Chargement + cache des données
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_from_bytes(name: str, raw: bytes):
    return utils.load_data(io.BytesIO(raw))

df_comp, df_ent, df_align, df_sol = load_from_bytes(
    uploaded_file.name, uploaded_file.getvalue()
)


# -----------------------------------------------------------------------------
# 7) Dispatch selon la page
# -----------------------------------------------------------------------------
if page == "Entreprise":
    # On vérifie que le DataFrame est bien chargé et non vide
    if df_ent is not None and not df_ent.empty:
        entreprise.display(df_ent)
    else:
        st.error("Aucune donnée entreprise à afficher.")
elif page == "Solution":
    # On vérifie que le DataFrame est bien chargé et non vide
    if df_sol is not None and not df_sol.empty:
        solution.display(df_sol)
    else:
        st.error("Aucune donnée solution à afficher.")
elif page == "Analyse comparative":
    if df_comp is not None and not df_comp.empty:
        # Créer un dictionnaire avec les DataFrames comme attendu par la nouvelle page
        all_dfs = {"Analyse comparative": df_comp}
        analyse_comparative.display(all_dfs)
    else:
        st.error("Aucune donnée d'analyse comparative à afficher.")
elif page == "Assistant IA":
    # Créer un dictionnaire avec tous les DataFrames pour le chatbot
    all_dfs = {
        "Analyse comparative": df_comp,
        "Entreprises": df_ent,
        "Solutions": df_sol,
        "Alignement": df_align
    }
    chatbot.display(all_dfs)

# -----------------------------------------------------------------------------
# 8) Section d'export PDF à la fin de la sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    sidebar.add_pdf_download_section(df_ent, df_sol, df_comp, df_align)

# -----------------------------------------------------------------------------
# 9) Sauvegarde **une seule fois** des cookies
# -----------------------------------------------------------------------------
if "cookies_saved" not in st.session_state:
    sidebar.cookies.save()
    st.session_state["cookies_saved"] = True