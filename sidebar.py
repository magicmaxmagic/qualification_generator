# sidebar.py
import streamlit as st
import random, json
from streamlit_cookies_manager import EncryptedCookieManager

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
    create_sidebar_section("Filtrer les entreprises", "🏢")
    
    # Ajout d'un petit texte d'aide stylé
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
        Sélectionnez les entreprises à comparer sur le graphique
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar.expander("Sélection", expanded=True):
        all_sel = st.checkbox(
            "Tout sélectionner",
            value=(len(previous) == len(entreprises_disponibles)),
        )
        if all_sel:
            sel = entreprises_disponibles
        else:
            sel = st.multiselect(
                "Entreprises à comparer",
                entreprises_disponibles,
                default=previous,
                help="Choisissez jusqu'à 6 entreprises pour une comparaison optimale"
            )
        if len(sel) > max_comparaison:
            st.warning(f"Au-delà de {max_comparaison} entreprises, le radar devient moins lisible.")

    # on sérialise la sélection
    cookies[KEY_SEL] = json.dumps(sel)

    # Section couleurs avec style moderne et icône élégante
    create_sidebar_section("Couleurs personnalisées", "")
    
    # Ajout d'un petit texte d'aide stylé
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
        Personnalisez la couleur de chaque entreprise
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
    multiselect: bool = True
) -> list[str]:
    # Appliquer les styles modernes
    apply_sidebar_styles()
    
    KEY = f"{label.replace(' ', '_').lower()}_selected"
    raw = cookies.get(KEY)
    previous = json.loads(raw) if raw else (default or options[:1])
    previous = [v for v in previous if v in options]
    if not previous:
        previous = default or options[:1]
    
    # Section stylée avec icône contextuelle
    if "données" in label.lower():
        icon = "�"
    elif "filtre" in label.lower():
        icon = ""
    else:
        icon = ""
    create_sidebar_section(label, icon)
    
    # Ajout d'un indicateur de sélection
    if multiselect:
        selected_count = len(previous)
        total_count = len(options)
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
            {selected_count}/{total_count} éléments sélectionnés
        </div>
        """, unsafe_allow_html=True)
        
        sel = st.sidebar.multiselect(
            label,
            options,
            default=previous,
            key=KEY,
            help=f"Sélectionnez parmi {total_count} options disponibles"
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
    create_sidebar_section("Type d'exigence", "")
    
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
        {len(types_)} types d'exigences disponibles
    </div>
    """, unsafe_allow_html=True)
    
    # Conteneur stylé pour les radio buttons
    st.sidebar.markdown("""
    <div style="
        background: rgba(248, 249, 250, 0.9);
        border: 1px solid rgba(0, 114, 178, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    ">
    """, unsafe_allow_html=True)
    
    sel = st.sidebar.radio(
        "Choisissez un type d'exigence",
        options=types_,
        index=types_.index(prev) if prev in types_ else 0,
        key=KEY,
        help="Sélectionnez le type d'exigence pour l'analyse d'alignement"
    )
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    cookies[KEY] = sel
    return sel