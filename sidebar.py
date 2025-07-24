"""
Sidebar IVÉO BI — Variables globales pour labels, titres, messages, styles
"""
# sidebar.py

import streamlit as st
import random, json
from streamlit_cookies_manager import EncryptedCookieManager

# =================== VARIABLES GLOBALES (labels, titres, messages, styles, états) ===================
SIDEBAR_SECTION_EXPORT = "Export de rapport"
SIDEBAR_SECTION_EXPORT_ICON = "📄"
SIDEBAR_EXPORT_INFO = "Générez un rapport complet incluant toutes les analyses avec les filtres appliqués"
SIDEBAR_EXPORT_HTML_BTN = "📄 HTML"
SIDEBAR_EXPORT_HTML_HELP = "Génère et télécharge le rapport HTML"
SIDEBAR_EXPORT_PDF_BTN = "📄 PDF"
SIDEBAR_EXPORT_PDF_HELP = "Génère et télécharge le rapport PDF (peut échouer sur certaines plateformes)"
SIDEBAR_EXPORT_HTML_SUCCESS = "Rapport HTML généré!"
SIDEBAR_EXPORT_HTML_ERROR = "Erreur lors de la génération HTML"
SIDEBAR_EXPORT_PDF_SUCCESS = "Rapport PDF généré!"
SIDEBAR_EXPORT_PDF_ERROR = "Erreur PDF: {error}"
SIDEBAR_EXPORT_PDF_WARNING = "Erreur PDF: {error}"
SIDEBAR_EXPORT_PDF_INFO = "Utilisez l'export HTML puis convertissez avec votre navigateur (Ctrl+P → Enregistrer en PDF)"
SIDEBAR_EXPORT_PDF_UNAVAILABLE = "Export PDF indisponible. Utilisez HTML puis convertissez avec votre navigateur."
SIDEBAR_EXPORT_MODULE_ERROR = "Module de rapport non disponible: {error}"
SIDEBAR_EXPORT_MODULE_INFO = "Le module de génération de rapport n'est pas accessible"
SIDEBAR_EXPORT_BTN_INFO = "ℹ️ À propos du rapport"
SIDEBAR_EXPORT_BTN_HELP = "Informations sur le rapport PDF"
SIDEBAR_EXPORT_BTN_HELP2 = "Informations détaillées sur le contenu du rapport HTML"
SIDEBAR_EXPORT_MODULE_UNAVAILABLE = (
    "La fonctionnalité d'export PDF est temporairement indisponible.<br>"
    "Veuillez contacter l'administrateur pour résoudre ce problème."
)
SIDEBAR_EXPORT_HTML_CONTENT = (
    "<strong>Le rapport HTML inclut:</strong><br><br>"
    "<strong>1. Résumé exécutif</strong><br>"
    "- Statistiques générales<br>"
    "- Contexte de l'analyse<br><br>"
    "<strong>2. Analyse des entreprises</strong><br>"
    "- Entreprises sélectionnées<br>"
    "- Informations détaillées<br><br>"
    "<strong>3. Analyse des solutions</strong><br>"
    "- Solutions évaluées<br>"
    "- Caractéristiques techniques<br><br>"
    "<strong>4. Analyse comparative</strong><br>"
    "- Critères d'évaluation<br>"
    "- Filtres appliqués<br><br>"
    "<strong>5. Recommandations</strong><br>"
    "- Conseils stratégiques<br>"
    "- Prochaines étapes<br><br>"
    "<strong>6. Annexes</strong><br>"
    "- Méthodologie<br>"
    "- Glossaire<br><br>"
    "<strong>💡 Astuce:</strong> Pour convertir en PDF, ouvrez le fichier HTML dans votre navigateur et utilisez Ctrl+P → 'Enregistrer en PDF'"
)
# Variables globales pour la section comparatif
SIDEBAR_SECTION_FILTER = "Filtrer les entreprises"
SIDEBAR_SECTION_FILTER_ICON = "🏢"
SIDEBAR_FILTER_HELP = "Sélectionnez les entreprises à comparer sur le graphique"
SIDEBAR_FILTER_EXPANDER = "Sélection"
SIDEBAR_FILTER_CHECKBOX = "Tout sélectionner"
SIDEBAR_FILTER_MULTI = "Entreprises à comparer"
SIDEBAR_FILTER_MULTI_HELP = "Choisissez jusqu'à {max} entreprises pour une comparaison optimale"
SIDEBAR_FILTER_WARNING = "Au-delà de {max} entreprises, le radar devient moins lisible."
SIDEBAR_SECTION_COLOR = "Couleurs personnalisées"
SIDEBAR_COLOR_HELP = "Personnalisez la couleur de chaque entreprise"
# Variables globales pour la section alignement
SIDEBAR_SECTION_ALIGN = "Type d'exigence"
SIDEBAR_ALIGN_INFO = "{n} types d'exigences disponibles"
SIDEBAR_ALIGN_RADIO_LABEL = "Choisissez un type d'exigence"
SIDEBAR_ALIGN_RADIO_HELP = "Sélectionnez le type d'exigence pour l'analyse d'alignement"
SIDEBAR_ALIGN_RADIO_CONTAINER_STYLE = (
    "background: rgba(248, 249, 250, 0.9);"
    "border: 1px solid rgba(0, 114, 178, 0.2);"
    "border-radius: 12px;"
    "padding: 16px;"
    "margin: 12px 0;"
)

# —————————————————————————————————————————————
# 1) Initialisation du gestionnaire de cookies
# —————————————————————————————————————————————
COOKIE_PWD = st.secrets["cookie_password"]
cookies = EncryptedCookieManager(prefix="iveo_", password=COOKIE_PWD)
if not cookies.ready():
    st.stop()

# —————————————————————————————————————————————
# 2) Styles pour la sidebar moderne
# —————————————————————————————————————————————
def apply_sidebar_styles():
    """Applique les styles modernes à la sidebar avec le thème IVÉO"""
    st.markdown("""
    <style>
    /* Sidebar principale avec effet moderne */
    .stSidebar > div {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-right: 3px solid rgba(0, 114, 178, 0.2) !important;
        box-shadow: 2px 0 10px rgba(0, 114, 178, 0.1) !important;
    }
    
    /* Conteneur principal de la sidebar */
    .stSidebar {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Titres de section dans la sidebar avec effet premium */
    .stSidebar h3 {
        color: #0072B2 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        margin-bottom: 1rem !important;
        margin-top: 1.5rem !important;
        padding-bottom: 0.8rem !important;
        border-bottom: 3px solid rgba(0, 114, 178, 0.3) !important;
        text-shadow: 0 1px 2px rgba(0, 114, 178, 0.1) !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Selectbox dans la sidebar avec effet premium */
    .stSidebar .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(0, 114, 178, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSidebar .stSelectbox > div > div:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 8px 25px rgba(0, 114, 178, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Multiselect dans la sidebar avec effet premium */
    .stSidebar .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(0, 114, 178, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSidebar .stMultiSelect > div > div:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 8px 25px rgba(0, 114, 178, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Tags du multiselect avec animation */
    .stSidebar .stMultiSelect span[data-baseweb="tag"] {
        background: linear-gradient(135deg, rgba(0, 114, 178, 0.1) 0%, rgba(0, 114, 178, 0.2) 100%) !important;
        color: #0072B2 !important;
        border: 2px solid rgba(0, 114, 178, 0.4) !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        padding: 4px 12px !important;
        margin: 2px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 114, 178, 0.1) !important;
    }
    
    .stSidebar .stMultiSelect span[data-baseweb="tag"]:hover {
        background: linear-gradient(135deg, rgba(0, 114, 178, 0.2) 0%, rgba(0, 114, 178, 0.3) 100%) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 4px 12px rgba(0, 114, 178, 0.2) !important;
    }
    
    /* Color picker dans la sidebar avec effet premium */
    .stSidebar .stColorPicker > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(0, 114, 178, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSidebar .stColorPicker > div > div:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 8px 25px rgba(0, 114, 178, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Checkbox dans la sidebar avec effet premium */
    .stSidebar .stCheckbox > label {
        color: #333 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .stSidebar .stCheckbox > label:hover {
        color: #0072B2 !important;
    }
    
    .stSidebar .stCheckbox > label > span[data-baseweb="checkbox"] {
        border: 3px solid rgba(0, 114, 178, 0.6) !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 114, 178, 0.1) !important;
    }
    
    .stSidebar .stCheckbox > label > span[data-baseweb="checkbox"]:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 4px 12px rgba(0, 114, 178, 0.2) !important;
        transform: scale(1.05) !important;
    }
    
    .stSidebar .stCheckbox > label > span[data-baseweb="checkbox"][data-checked="true"] {
        background: linear-gradient(135deg, #0072B2 0%, #005a8f 100%) !important;
        border-color: #0072B2 !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.3) !important;
    }
    
    /* Radio buttons dans la sidebar avec effet premium */
    .stSidebar .stRadio > label {
        color: #333 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stSidebar .stRadio > div > label {
        color: #555 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        padding: 8px 12px !important;
        margin: 4px 0 !important;
        border-radius: 8px !important;
        background: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid rgba(0, 114, 178, 0.1) !important;
    }
    
    .stSidebar .stRadio > div > label:hover {
        color: #0072B2 !important;
        background: rgba(0, 114, 178, 0.05) !important;
        border-color: rgba(0, 114, 178, 0.3) !important;
        transform: translateX(5px) !important;
    }
    
    .stSidebar .stRadio > div > label > span[data-baseweb="radio"] {
        border: 3px solid rgba(0, 114, 178, 0.6) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 114, 178, 0.1) !important;
    }
    
    .stSidebar .stRadio > div > label > span[data-baseweb="radio"]:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 4px 12px rgba(0, 114, 178, 0.2) !important;
        transform: scale(1.1) !important;
    }
    
    .stSidebar .stRadio > div > label > span[data-baseweb="radio"][data-checked="true"] {
        background: linear-gradient(135deg, #0072B2 0%, #005a8f 100%) !important;
        border-color: #0072B2 !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.3) !important;
    }
    
    /* Expander dans la sidebar avec effet premium */
    .stSidebar .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 249, 250, 0.9) 100%) !important;
        border: 2px solid rgba(0, 114, 178, 0.3) !important;
        border-radius: 12px !important;
        color: #0072B2 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 12px 16px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSidebar .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(0, 114, 178, 0.1) 0%, rgba(0, 114, 178, 0.05) 100%) !important;
        border-color: #0072B2 !important;
        box-shadow: 0 8px 25px rgba(0, 114, 178, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    .stSidebar .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.7) !important;
        border: 2px solid rgba(0, 114, 178, 0.2) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Messages d'alerte dans la sidebar avec effet premium */
    .stSidebar .stAlert {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 193, 7, 0.05) 100%) !important;
        border: 2px solid rgba(255, 193, 7, 0.4) !important;
        border-radius: 12px !important;
        color: #856404 !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        margin: 12px 0 !important;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Labels des composants avec effet premium */
    .stSidebar .stSelectbox > label,
    .stSidebar .stMultiSelect > label,
    .stSidebar .stColorPicker > label,
    .stSidebar .stRadio > label {
        color: #333 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        margin-bottom: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Styles alternatifs pour versions récentes de Streamlit */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-right: 3px solid rgba(0, 114, 178, 0.2) !important;
        box-shadow: 2px 0 10px rgba(0, 114, 178, 0.1) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(0, 114, 178, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 8px 25px rgba(0, 114, 178, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(0, 114, 178, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    [data-testid="stSidebar"] .stMultiSelect > div > div:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 8px 25px rgba(0, 114, 178, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    [data-testid="stSidebar"] .stColorPicker > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(0, 114, 178, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 114, 178, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    [data-testid="stSidebar"] .stColorPicker > div > div:hover {
        border-color: #0072B2 !important;
        box-shadow: 0 8px 25px rgba(0, 114, 178, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Animation au chargement */
    .stSidebar * {
        animation: fadeInUp 0.6s ease-out !important;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """, unsafe_allow_html=True)

def _random_color() -> str:
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(100, 200),
        random.randint(100, 200),
        random.randint(100, 200),
    )

def create_sidebar_section(title: str, icon: str = ""):
    """Crée une section stylée dans la sidebar avec effet premium"""
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(248, 249, 250, 0.9);
        border: 2px solid rgba(0, 114, 178, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #0072B2 0%, #005a8f 100%);
            border-radius: 15px 15px 0 0;
        "></div>
        <h3 style="
            color: #0072B2;
            font-weight: 800;
            font-size: 1.3rem;
            margin: 0 0 0.8rem 0;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            text-shadow: 0 2px 4px rgba(0, 114, 178, 0.1);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        ">
            <div style="
                background: linear-gradient(135deg, #0072B2 0%, #005a8f 100%);
                border-radius: 50%;
                width: 35px;
                height: 35px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                transition: all 0.3s ease;
            ">{icon}</div>
            {title}
        </h3>
        <div style="
            position: absolute;
            bottom: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: radial-gradient(circle, rgba(0, 114, 178, 0.1) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        "></div>
    </div>
    """, unsafe_allow_html=True)

def show_sidebar_comparatif(
    entreprises_disponibles: list[str],
    max_comparaison: int = 6
) -> tuple[list[str], dict[str,str]]:
    # Appliquer les styles modernes
    apply_sidebar_styles()
    
    KEY_SEL = "cmp_selected"
    raw = cookies.get(KEY_SEL)
    previous = json.loads(raw) if raw else entreprises_disponibles[:3]
    previous = [e for e in previous if e in entreprises_disponibles]
    if not previous:
        previous = entreprises_disponibles[:3]

    # Section de filtrage avec style moderne et icône élégante
    #create_sidebar_section(SIDEBAR_SECTION_FILTER, SIDEBAR_SECTION_FILTER_ICON)
    # Ajout d'un petit texte d'aide stylé
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(248, 249, 250, 0.9);
        border: 1px solid rgba(0, 114, 178, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 16px 0;
        color: #0072B2;
        font-size: 0.9rem;
        font-weight: 500;
    ">
        {SIDEBAR_FILTER_HELP}
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='margin:0.7em 0 1.2em 0; border:0; border-top:2px solid #e0e0e0;'>", unsafe_allow_html=True)
    with st.sidebar.expander(SIDEBAR_FILTER_EXPANDER, expanded=True):
        all_sel = st.checkbox(
            SIDEBAR_FILTER_CHECKBOX,
            value=(len(previous) == len(entreprises_disponibles)),
        )
        if all_sel:
            sel = entreprises_disponibles
        else:
            sel = st.multiselect(
                SIDEBAR_FILTER_MULTI,
                entreprises_disponibles,
                default=previous,
                help=SIDEBAR_FILTER_MULTI_HELP.format(max=max_comparaison)
            )
        if len(sel) > max_comparaison:
            st.warning(SIDEBAR_FILTER_WARNING.format(max=max_comparaison))
    # on sérialise la sélection
    cookies[KEY_SEL] = json.dumps(sel)
    # Section couleurs avec style moderne et icône élégante
    st.sidebar.markdown("<hr style='margin:0.7em 0 1.2em 0; border:0; border-top:2px solid #e0e0e0;'>", unsafe_allow_html=True)
    create_sidebar_section(SIDEBAR_SECTION_COLOR, "")
    # Ajout d'un petit texte d'aide stylé
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(248, 249, 250, 0.9);
        border: 1px solid rgba(0, 114, 178, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 16px 0;
        color: #0072B2;
        font-size: 0.9rem;
        font-weight: 500;
    ">
        {SIDEBAR_COLOR_HELP}
    </div>
    """, unsafe_allow_html=True)
    
    couleurs: dict[str, str] = {}
    for i, ent in enumerate(sel):
        ckey = f"cmp_color_{ent}"
        prev = cookies.get(ckey)
        if isinstance(prev, str) and prev.startswith("#") and len(prev) == 7:
            base = prev
        else:
            base = _random_color()
        
        # Conteneur stylé pour chaque color picker
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(248, 249, 250, 0.9);
            border: 1px solid rgba(0, 114, 178, 0.2);
            border-radius: 10px;
            padding: 12px;
            margin: 8px 0;
            transition: all 0.3s ease;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 8px;
            ">
                <div style="
                    width: 12px;
                    height: 12px;
                    background: {base};
                    border-radius: 50%;
                    border: 2px solid #fff;
                "></div>
                <span style="
                    font-weight: 600;
                    color: #333;
                    font-size: 0.9rem;
                ">{ent}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col = st.sidebar.color_picker(
            f"Couleur pour {ent}",
            base,
            key=ckey,
            label_visibility="collapsed"
        )
        couleurs[ent] = col
        cookies[ckey] = col
        
    all_color_keys = [f"cmp_color_{e}" for e in entreprises_disponibles]
    for k in cookies.keys():
        if k.startswith("cmp_color_") and k not in all_color_keys:
            del cookies[k]

    return sel, couleurs

def show_sidebar(
    label: str,
    options: list[str],
    default: list[str]|None = None,
    multiselect: bool = True,
    key: str|None = None
) -> list[str]:
    # Appliquer les styles modernes
    apply_sidebar_styles()
    KEY = key if key is not None else f"{label.replace(' ', '_').lower()}_selected"
    raw = cookies.get(KEY)
    previous = json.loads(raw) if raw else (default or options[:1])
    previous = [v for v in previous if v in options]
    if not previous:
        previous = default or options[:1]
    
    # Barre horizontale avant le filtre entreprises
    st.sidebar.markdown("<hr style='margin:0.7em 0 1.2em 0; border:0; border-top:2px solid #e0e0e0;'>", unsafe_allow_html=True)
    # Section minimaliste : uniquement le multiselect
    if multiselect:
        sel = st.sidebar.multiselect(
            label,
            options,
            default=previous,
            key=KEY,
            help=f"Sélectionnez parmi {len(options)} options disponibles"
        )
    else:
        st.sidebar.markdown("""
        <div style="
            background: rgba(248, 249, 250, 0.9);
            border: 1px solid rgba(0, 114, 178, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            color: #0072B2;
            font-size: 0.9rem;
            font-weight: 500;
        ">
            Sélectionnez une option
        </div>
        """, unsafe_allow_html=True)
        
        idx = options.index(previous[0] if isinstance(previous, list) else previous)
        choice = st.sidebar.selectbox(
            label,
            options,
            index=idx,
            key=KEY,
            help="Choisissez l'option qui vous convient"
        )
        sel = [choice]

    # Barre horizontale après le filtre entreprises
    st.sidebar.markdown("<hr style='margin:0.7em 0 1.2em 0; border:0; border-top:2px solid #e0e0e0;'>", unsafe_allow_html=True)
    cookies[KEY] = json.dumps(sel)
    return sel

def show_sidebar_alignement(df_align) -> str:
    # Appliquer les styles modernes
    apply_sidebar_styles()
    
    KEY = "align_exigence"
    types_ = df_align["Exigence de base"].dropna().unique().tolist()
    raw = cookies.get(KEY)
    
    # Simplification de la logique conditionnelle
    if raw in types_:
        prev = raw
    else:
        prev = types_[0] if types_ else ""

    # Section stylée avec icône spécialisée
    create_sidebar_section(SIDEBAR_SECTION_ALIGN, "")
    # Ajout d'informations contextuelles
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(248, 249, 250, 0.9);
        border: 1px solid rgba(0, 114, 178, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 16px 0;
        color: #0072B2;
        font-size: 0.9rem;
        font-weight: 500;
    ">
        {SIDEBAR_ALIGN_INFO.format(n=len(types_))}
    </div>
    """, unsafe_allow_html=True)
    # Conteneur stylé pour les radio buttons
    st.sidebar.markdown(f"""
    <div style="{SIDEBAR_ALIGN_RADIO_CONTAINER_STYLE}">
    """, unsafe_allow_html=True)
    sel = st.sidebar.radio(
        SIDEBAR_ALIGN_RADIO_LABEL,
        options=types_,
        index=types_.index(prev) if prev in types_ else 0,
        key=KEY,
        help=SIDEBAR_ALIGN_RADIO_HELP
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    cookies[KEY] = sel if sel is not None else ""
    return sel if sel is not None else ""

def add_pdf_download_section(df_ent=None, df_sol=None, df_comp=None, df_align=None):
    """
    Ajoute une section pour télécharger le rapport PDF complet.
    
    Args:
        df_ent: DataFrame des entreprises
        df_sol: DataFrame des solutions
        df_comp: DataFrame d'analyse comparative
        df_align: DataFrame d'alignement
    """
    # Section stylée pour le téléchargement PDF - toujours affichée
    st.sidebar.markdown("---")
    create_sidebar_section(SIDEBAR_SECTION_EXPORT, SIDEBAR_SECTION_EXPORT_ICON)
    try:
        from app.pdf_generator_html import generate_report_with_export_options, create_download_link
        from datetime import datetime
        # Informations sur le rapport - toujours affichées
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(248, 249, 250, 0.9);
            border: 1px solid rgba(0, 114, 178, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            color: #0072B2;
            font-size: 0.9rem;
            font-weight: 500;
        ">
            {SIDEBAR_EXPORT_INFO}
        </div>
        """, unsafe_allow_html=True)
        # Boutons d'export - toujours les deux options disponibles
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button(
                SIDEBAR_EXPORT_HTML_BTN,
                key="generate_html_button",
                help=SIDEBAR_EXPORT_HTML_HELP
            ):
                with st.spinner("Génération du rapport HTML..."):
                    try:
                        reports = generate_report_with_export_options(df_ent, df_sol, df_comp, df_align)
                        if reports["html"]:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"rapport_iveo_{timestamp}.html"
                            download_link = create_download_link(reports["html"], filename)
                            st.success(SIDEBAR_EXPORT_HTML_SUCCESS)
                            st.markdown(download_link, unsafe_allow_html=True)
                        else:
                            st.error(SIDEBAR_EXPORT_HTML_ERROR)
                    except Exception as e:
                        st.error(f"Erreur HTML: {str(e)}")
        with col2:
            if st.button(
                SIDEBAR_EXPORT_PDF_BTN,
                key="generate_pdf_button",
                help=SIDEBAR_EXPORT_PDF_HELP
            ):
                with st.spinner("Génération du rapport PDF..."):
                    try:
                        reports = generate_report_with_export_options(df_ent, df_sol, df_comp, df_align)
                        if reports["pdf"]:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"rapport_iveo_{timestamp}.pdf"
                            download_link = create_download_link(reports["pdf"], filename)
                            st.success(SIDEBAR_EXPORT_PDF_SUCCESS)
                            st.markdown(download_link, unsafe_allow_html=True)
                        else:
                            st.info(SIDEBAR_EXPORT_PDF_UNAVAILABLE)
                    except Exception as e:
                        st.warning(SIDEBAR_EXPORT_PDF_WARNING.format(error=str(e)))
                        st.info(SIDEBAR_EXPORT_PDF_INFO)
    except ImportError as e:
        st.sidebar.error(SIDEBAR_EXPORT_MODULE_ERROR.format(error=str(e)))
        st.sidebar.info(SIDEBAR_EXPORT_MODULE_INFO)
        # Afficher quand même les boutons d'information
        if st.sidebar.button(
            SIDEBAR_EXPORT_BTN_INFO,
            key="pdf_info_button_fallback",
            help=SIDEBAR_EXPORT_BTN_HELP
        ):
            st.sidebar.markdown(f"""
            <div style="
                background: rgba(248, 249, 250, 0.9);
                border: 1px solid rgba(0, 114, 178, 0.2);
                border-radius: 8px;
                padding: 12px 16px;
                margin: 16px 0;
                color: #333;
                font-size: 0.85rem;
                line-height: 1.4;
            ">
                {SIDEBAR_EXPORT_MODULE_UNAVAILABLE}
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.error(f"Erreur: {str(e)}")
    # Bouton d'information - toujours affiché
    if st.sidebar.button(
        SIDEBAR_EXPORT_BTN_INFO,
        key="pdf_info_button",
        help=SIDEBAR_EXPORT_BTN_HELP2
    ):
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(248, 249, 250, 0.9);
            border: 1px solid rgba(0, 114, 178, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            color: #333;
            font-size: 0.85rem;
            line-height: 1.4;
        ">
            {SIDEBAR_EXPORT_HTML_CONTENT}
        </div>
        """, unsafe_allow_html=True)