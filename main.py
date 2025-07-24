
# =================== VARIABLES GLOBALES (labels, titres, messages, navigation) ===================
PAGE_TITLE = "Tableau de bord IVÉO"
PAGE_ICON = "https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg"
NAV_PAGES = ("Accueil", "Entreprise", "Solution", "Analyse comparative")
ERROR_NO_FILE = "Fichier non trouvé. Déposez-le, corrigez le chemin ou utilisez une URL valide."
UPLOAD_LABEL = "Ou déposez un fichier Excel (.xlsx)"
UPLOAD_TYPE = "xlsx"
UPLOAD_KEY = "uploader"
PATH_INPUT_LABEL = "Chemin local ou URL du fichier Excel"
PATH_INPUT_KEY = "excel_path_input"
SIDEBAR_LOGO = "https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg"
SIDEBAR_NAV_LABEL = "Navigation"
SIDEBAR_NAV_KEY = "page_selector"
ERROR_HOME = "Aucune donnée à afficher sur la page d'accueil."
ERROR_ENT = "Aucune donnée entreprise à afficher."
ERROR_SOL = "Aucune donnée solution à afficher."
ERROR_COMP = "Aucune donnée d'analyse comparative à afficher."

import streamlit as st
import os
# -----------------------------------------------------------------------------
# 1) Configuration de la page — Doit être **le tout premier** appel Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
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
from app.pages import analyse_comparative, home, entreprise, solution
import sidebar

# -----------------------------------------------------------------------------
# 3) Masquer “View source on GitHub”
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="collapsedControl"] + div [data-testid="source-link"] {
        display: none !important;
    }
    
    /* Réduction de la taille du texte global */
    .main .block-container {
        font-size: 0.9rem !important;
        line-height: 1.4 !important;
    }
    
    /* Réduction taille des headers */
    h1 {
        font-size: 1.8rem !important;
    }
    h2 {
        font-size: 1.5rem !important;
    }
    h3 {
        font-size: 1.3rem !important;
    }
    h4 {
        font-size: 1.1rem !important;
    }
    
    /* Réduction taille du texte des éléments Streamlit */
    .stMarkdown, .stText {
        font-size: 0.9rem !important;
    }
    
    /* Réduction taille des boutons */
    .stButton > button {
        font-size: 0.85rem !important;
        padding: 0.4rem 0.8rem !important;
    }
    
    /* Réduction taille des selectbox et multiselect */
    .stSelectbox label, .stMultiSelect label {
        font-size: 0.85rem !important;
    }
    
    /* Réduction taille des tableaux */
    .stDataFrame, .stTable {
        font-size: 0.8rem !important;
    }
    
    /* Réduction taille des métriques */
    .metric-container {
        font-size: 0.8rem !important;
    }
    
    /* Réduction taille sidebar */
    .stSidebar {
        font-size: 0.85rem !important;
    }
    
    /* Réduction espacement global */
    .element-container {
        margin-bottom: 0.5rem !important;
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
        SIDEBAR_LOGO,
        use_container_width=True,
    )
    st.markdown("---")

    # 1) lire le dernier chemin ou URL depuis le cookie
    default_path = sidebar.cookies.get("excel_path") or ""
    # 2) uploader drag & drop
    upload = st.file_uploader(
        UPLOAD_LABEL,
        type=UPLOAD_TYPE,
        key=UPLOAD_KEY,
    )
    uploaded_file = None
    # 1) Si un fichier est uploadé, priorité à ce fichier
    if upload:
        os.makedirs("uploads", exist_ok=True)
        saved_path = os.path.abspath(os.path.join("uploads", upload.name))
        with open(saved_path, "wb") as f:
            f.write(upload.getvalue())
        uploaded_file = upload
        uploaded_file.name = upload.name
        sidebar.cookies["excel_path"] = saved_path
    else:
        # 2) Sinon, utiliser le champ texte pour chemin local ou URL
        path_input = st.text_input(
            PATH_INPUT_LABEL,
            value=default_path,
            key=PATH_INPUT_KEY,
        )
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
        st.error(ERROR_NO_FILE)
        st.stop()

    st.markdown("---")
    page = st.radio(
        SIDEBAR_NAV_LABEL,
        NAV_PAGES,
        key=SIDEBAR_NAV_KEY,
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
if page == NAV_PAGES[0]:  # Accueil
    if df_comp is not None and not df_comp.empty:
        all_dfs = {"Comparatif": df_comp, "Entreprise": df_ent, "Solution": df_sol}
        home.display(all_dfs)
    else:
        st.error(ERROR_HOME)
elif page == NAV_PAGES[1]:  # Entreprise
    if df_ent is not None and not df_ent.empty:
        entreprise.display(df_ent)
    else:
        st.error(ERROR_ENT)
elif page == NAV_PAGES[2]:  # Solution
    if df_sol is not None and not df_sol.empty:
        solution.display(df_sol)
    else:
        st.error(ERROR_SOL)
elif page == NAV_PAGES[3]:  # Analyse comparative
    if df_comp is not None and not df_comp.empty:
        all_dfs = {"Analyse comparative": df_comp}
        analyse_comparative.display(all_dfs)
    else:
        st.error(ERROR_COMP)
# elif page == NAV_PAGES[4]:  # Assistant IA
#     all_dfs = {
#         "Analyse comparative": df_comp,
#         "Entreprise": df_ent,
#         "Solutions": df_sol,
#         "Alignement": df_align
#     }
#     chatbot.display(all_dfs)

# -----------------------------------------------------------------------------
# 8) Section d'export PDF à la fin de la sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    sidebar.add_pdf_download_section(df_ent, df_sol, df_comp, df_align)

# -----------------------------------------------------------------------------
# 9) Sauvegarde **une seule fois** des cookies
# -----------------------------------------------------------------------------
if "cookies_saved" not in st.session_state:
    sidebar.cookies.save()
    st.session_state["cookies_saved"] = True