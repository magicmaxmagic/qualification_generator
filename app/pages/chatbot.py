# === CONSTANTES GLOBALES (labels, titres, messages, boutons, placeholders, etc.) ===
LABEL_PAGE_TITLE = "Assistant IA IVÉO"
LABEL_PAGE_SUBTITLE = "Assistant professionnel pour l'analyse de données"
LABEL_OPENAI_UNAVAILABLE = "**OpenAI temporairement non disponible** - Conflit de versions détecté"
LABEL_OPENAI_WARNING = "Clé API requise"
LABEL_OPENAI_SUCCESS = "API OpenAI configurée"
LABEL_OPENAI_API_KEY = "Clé API OpenAI"
LABEL_OPENAI_API_KEY_HELP = "Entrez votre clé API OpenAI pour activer le chatbot"
LABEL_SIDEBAR_CONFIG = "Configuration IA"
LABEL_SIDEBAR_PARAMS = "Paramètres"
LABEL_SIDEBAR_MODEL = "Modèle IA"
LABEL_SIDEBAR_MODEL_HELP = "Choisissez le modèle OpenAI à utiliser"
LABEL_SIDEBAR_CREATIVITY = "Créativité"
LABEL_SIDEBAR_CREATIVITY_HELP = "Contrôle la créativité des réponses"
LABEL_SIDEBAR_MAX_TOKENS = "Longueur max"
LABEL_SIDEBAR_MAX_TOKENS_HELP = "Nombre maximum de mots dans la réponse"
LABEL_SIDEBAR_QUICK_CHAT = "Chat Rapide"
LABEL_SIDEBAR_QUICK_QUESTION = "Question rapide"
LABEL_SIDEBAR_QUICK_QUESTION_PLACEHOLDER = "Posez une question courte..."
LABEL_SIDEBAR_SEND = "Envoyer"
LABEL_SIDEBAR_ACTIONS = "Actions Rapides"
LABEL_SIDEBAR_ANALYZE = "Analyser les données"
LABEL_SIDEBAR_SUGGESTIONS = "Suggestions d'amélioration"
LABEL_SIDEBAR_CLEAR_HISTORY = "Effacer l'historique"
LABEL_CHAT_PLACEHOLDER = "Tapez votre question ici..."
LABEL_CHAT_SEND = "Envoyer"
LABEL_CHAT_WELCOME = "Bienvenue sur le service d'analyse de données IVÉO. Posez votre question pour démarrer la conversation."
LABEL_CHAT_ASSISTANT = "assistant"
LABEL_CHAT_USER = "user"
LABEL_CHAT_THINKING = "L'IA réfléchit..."
LABEL_CHAT_CONFIGURE_API = "Veuillez configurer votre clé API OpenAI dans la sidebar."
LABEL_TEMP_HEADER = "Assistant Temporaire (sans IA)"
LABEL_TEMP_INFO = "En attendant la correction d'OpenAI, voici ce que je peux vous dire sur vos données :"
LABEL_TEMP_DATA_SUMMARY = "Résumé des données"
LABEL_TEMP_SUGGESTIONS = "Suggestions d'analyse"
LABEL_TEMP_ACTIONS = "Actions recommandées :"
LABEL_TEMP_REFRESH = "Actualiser les données"
LABEL_TEMP_FEEDBACK = "Feedback temporaire"
LABEL_TEMP_FEEDBACK_INPUT = "Décrivez ce que vous cherchez à analyser :"
LABEL_TEMP_FEEDBACK_PLACEHOLDER = "Ex : Je souhaite comparer les entreprises sur les critères de sécurité..."
LABEL_TEMP_FEEDBACK_SUCCESS = "Demande enregistrée ! Elle sera traitée une fois l'IA disponible."
LABEL_TEMP_FEEDBACK_PENDING = "Demandes en attente"
LABEL_TEMP_FEEDBACK_EXPANDER = "Demande {i} - {timestamp}"
LABEL_TEMP_FEEDBACK_BUTTON = "Enregistrer la demande"
LABEL_TEMP_METRIC_ROWS = "Total lignes"
LABEL_TEMP_METRIC_COLS = "Total colonnes"
"""
Page Chatbot IA - Application IVÉO BI
=====================================

Cette page offre un assistant IA conversationnel intégré pour aider les utilisateurs
avec leurs analyses et questions sur les données de l'application.

Fonctionnalités :
- Chat interactif avec OpenAI GPT
- Historique des conversations
- Interface moderne et responsive
- Analyse contextuelle des données
- Suggestions intelligentes

Version : 1.0 - 2025.01.14
"""

import streamlit as st
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    openai_client = None
except ImportError as e:
    OPENAI_AVAILABLE = False
    openai_client = None
from datetime import datetime
import json
from sidebar import apply_sidebar_styles

# Configuration OpenAI
def init_openai():
    """Initialise l'API OpenAI avec la clé fournie par l'utilisateur."""
    global openai_client

    if not OPENAI_AVAILABLE:
        return False

    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""

    if st.session_state.openai_api_key:
        try:
            global openai_client
            # Import OpenAI class inside the function to avoid issues if openai is not installed
            from openai import OpenAI
            openai_client = OpenAI(api_key=st.session_state.openai_api_key)
            return True
        except Exception as e:
            st.error(f"Erreur d'initialisation OpenAI : {str(e)}")
            return False
    return False

def display(all_dfs):
    """
    Fonction principale d'affichage de la page Chatbot.
    
    Args:
        all_dfs (dict): Dictionnaire contenant tous les DataFrames du fichier Excel
    """
    _apply_sidebar_styles()
    _init_chat_history()
    _render_header()
    if not OPENAI_AVAILABLE:
        _render_openai_unavailable(all_dfs)
        return
    _render_custom_css()
    _render_header_styled()
    _setup_sidebar_chat(all_dfs)
    _render_main_chat()

def _apply_sidebar_styles():
    apply_sidebar_styles()

def _init_chat_history():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

def _render_header():
    st.title(LABEL_PAGE_TITLE)
    st.markdown(f"### {LABEL_PAGE_SUBTITLE}")

def _render_openai_unavailable(all_dfs):
    st.warning(LABEL_OPENAI_UNAVAILABLE)
    st.markdown("""
    ### **Solution rapide** :
    
    **Problème** : Conflit entre les versions `openai` et `httpx`
    
    **Commandes de correction** :
    ```bash
    # Étape 1 : Désinstaller les versions conflictuelles
    pip uninstall openai httpx -y
    
    # Étape 2 : Installer les versions compatibles
    pip install httpx==0.24.1
    pip install openai==1.3.0
    
    # Étape 3 : Redémarrer l'application
    ```
    
    **Ou utilisez l'installation alternative** :
    ```bash
    pip install "openai[datalib]"
    ```
    """)
    st.markdown("---")
    st.markdown("### **Aperçu de vos données en attendant** :")
    if all_dfs:
        for sheet_name, df in all_dfs.items():
            if df is not None and not df.empty:
                with st.expander(f"{sheet_name} ({len(df)} lignes, {len(df.columns)} colonnes)"):
                    st.dataframe(df.head())
    _render_temporary_interface(all_dfs)

def _render_custom_css():
    st.markdown("""
    <style>
    body, .main, .block-container {
        background: linear-gradient(120deg, #f5f7fa 0%, #c3cfe2 100%) !important;
    }
    .chat-header {
        background: #2c3e50;
        color: white;
        border-radius: 18px;
        padding: 32px 32px 16px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(44,62,80,0.15);
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 1px;
        position: relative;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 24px;
        border-radius: 20px;
        background: rgba(255,255,255,0.85);
        box-shadow: 0 8px 32px rgba(44,62,80,0.08);
        margin-bottom: 24px;
        backdrop-filter: blur(4px);
    }
    .user-message, .assistant-message {
        padding: 18px 24px;
        border-radius: 24px;
        margin: 16px 0;
        font-size: 1.15rem;
        box-shadow: 0 4px 18px rgba(44,62,80,0.08);
        animation: fadeIn 0.5s;
        word-break: break-word;
        max-width: 80%;
    }
    .user-message {
        background: linear-gradient(135deg, #2980b9 0%, #6dd5fa 100%);
        color: white;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 8px;
        border-top-left-radius: 8px;
    }
    .assistant-message {
        background: linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%);
        color: white;
        margin-right: auto;
        margin-left: 0;
        border-bottom-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-input {
        background: rgba(255,255,255,0.95);
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0 2px 12px rgba(44,62,80,0.08);
        margin-bottom: 16px;
    }
    .sidebar-chat {
        background: #f5f7fa;
        border-radius: 18px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 15px rgba(44,62,80,0.08);
    }
    .stButton > button {
        background: #2c3e50;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(44,62,80,0.10);
        transition: background 0.2s, transform 0.2s;
        cursor: pointer;
    }
    .stButton > button:hover {
        background: #2980b9;
        transform: scale(1.04);
    }
    @media (max-width: 900px) {
        .chat-header { font-size: 1.3rem; padding: 18px 8px; }
        .chat-container { padding: 8px; }
        .user-message, .assistant-message { font-size: 1rem; padding: 12px 10px; }
        .sidebar-chat { padding: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

def _render_header_styled():
    st.markdown('<div class="chat-header">Assistant IA IVÉO</div>', unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:1.1rem; color:#444; margin-bottom:18px;'>Service d'analyse de données professionnelle</div>", unsafe_allow_html=True)


def _setup_sidebar_chat(all_dfs):
    """Configure le chatbot dans la sidebar."""
    with st.sidebar:
        st.markdown('<div class="sidebar-chat">', unsafe_allow_html=True)
        st.markdown("## Configuration IA")
        
        # Configuration de l'API OpenAI
        api_key = st.text_input(
            "Clé API OpenAI",
            type="password",
            value=st.session_state.get("openai_api_key", ""),
            help="Entrez votre clé API OpenAI pour activer le chatbot"
        )
        
        if api_key != st.session_state.get("openai_api_key", ""):
            st.session_state.openai_api_key = api_key
            st.rerun()
        
        # Vérification de la connexion
        if init_openai():
            st.success("API OpenAI configurée")
        else:
            st.warning("Clé API requise")
        
        st.markdown("---")
        
        # Paramètres du modèle
        st.markdown("## Paramètres")
        
        model = st.selectbox(
            "Modèle IA",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0,
            help="Choisissez le modèle OpenAI à utiliser"
        )
        st.session_state.selected_model = model
        
        temperature = st.slider(
            "Créativité",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Contrôle la créativité des réponses"
        )
        st.session_state.temperature = temperature
        
        max_tokens = st.slider(
            "Longueur max",
            min_value=50,
            max_value=2000,
            value=500,
            step=50,
            help="Nombre maximum de mots dans la réponse"
        )
        st.session_state.max_tokens = max_tokens
        
        st.markdown("---")
        
        # Mini chat dans la sidebar
        st.markdown("## Chat Rapide")
        
        quick_question = st.text_input(
            "Question rapide",
            placeholder="Posez une question courte...",
            key="sidebar_question"
        )
        
        if st.button("Envoyer", key="sidebar_send"):
            if quick_question and init_openai():
                with st.spinner("Réflexion..."):
                    response = _get_ai_response(quick_question, all_dfs, is_quick=True)
                    st.success(f": {response}")
            elif not init_openai():
                st.error("Configurez d'abord votre clé API OpenAI")
        
        # Actions rapides
        st.markdown("## Actions Rapides")
        
        if st.button("Analyser les données", key="analyze_data"):
            if init_openai():
                _add_system_message("Analyse des données en cours...", all_dfs)
        
        if st.button("Suggestions d'amélioration", key="suggestions"):
            if init_openai():
                _add_system_message("Génération de suggestions...", all_dfs)
        
        if st.button("Effacer l'historique", key="clear_history"):
            st.session_state.chat_messages = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def _render_main_chat():
    """Affiche l'interface de chat principale."""
    # Zone de chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Afficher l'historique des messages
    if not st.session_state.chat_messages:
        st.markdown(
            f'<div class="assistant-message">{LABEL_CHAT_WELCOME}</div>',
            unsafe_allow_html=True
        )

    for message in st.session_state.chat_messages:
        if message["role"] == LABEL_CHAT_USER or message["role"] == "user":
            st.markdown(
                f'<div class="user-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="assistant-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # Zone de saisie
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "Votre message",
            placeholder=LABEL_CHAT_PLACEHOLDER,
            key="main_chat_input",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button(LABEL_CHAT_SEND, key="main_send", use_container_width=True)

    # Traitement de l'envoi
    if (send_button or user_input) and user_input:
        st.session_state.chat_messages.append({
            "role": LABEL_CHAT_USER,
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        if not init_openai():
            st.session_state.chat_messages.append({
                "role": LABEL_CHAT_ASSISTANT,
                "content": LABEL_CHAT_CONFIGURE_API,
                "timestamp": datetime.now().isoformat()
            })
            return
        with st.spinner(LABEL_CHAT_THINKING):
            ai_response = _get_ai_response(user_input, st.session_state.get("all_dfs", {}))
        st.session_state.chat_messages.append({
            "role": LABEL_CHAT_ASSISTANT,
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        if ai_response is not None and not ai_response.startswith("Erreur") and not ai_response.startswith("Veuillez"):
            st.rerun()

def _get_system_context(all_dfs):
    """
    Génère le contexte système pour l'IA en fonction des DataFrames disponibles.

    Args:
        all_dfs (dict): DataFrames disponibles

    Returns:
        str: Contexte système
    """
    context = """
    Tu es un assistant IA expert en analyse de données pour l'application IVÉO BI.

    CONTEXTE :
    - Tu aides les utilisateurs à analyser et comprendre leurs données business
    - Tu peux répondre aux questions sur les analyses comparatives, les entreprises, et les solutions
    - Tu fournis des insights actionables et des recommandations

    STYLE DE COMMUNICATION :
    - Sois professionnel mais accessible
    - Utilise des emojis appropriés pour rendre la conversation engageante
    - Fournis des réponses structurées et claires
    """

    # Ajouter des informations sur les données disponibles
    if all_dfs:
        context += "\nFeuilles de données disponibles :\n"
        for sheet_name, df in all_dfs.items():
            if df is not None and not df.empty:
                context += f"- {sheet_name}: {len(df)} lignes, {len(df.columns)} colonnes\n"

    context += """
    
    CAPACITÉS :
    - Analyse des données comparatives
    - Recommandations d'amélioration
    - Interprétation des métriques
    - Aide à la prise de décision
    - Explication des tendances

    Réponds toujours en français et reste dans le contexte de l'analyse business et des données IVÉO.
    """

    return context

def _get_ai_response(user_message, all_dfs, is_quick=False):
    """
    Envoie la requête à OpenAI et retourne la réponse du chatbot.

    Args:
        user_message (str): Message de l'utilisateur
        all_dfs (dict): DataFrames disponibles
        is_quick (bool): Si la requête vient du chat rapide

    Returns:
        str: Réponse de l'IA ou message d'erreur
    """
    if not OPENAI_AVAILABLE or openai_client is None:
        return "Erreur : OpenAI n'est pas disponible. Veuillez vérifier la configuration."
    try:
        # Préparer le contexte système
        system_context = _get_system_context(all_dfs)
        messages = [
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_message}
        ]
        model = st.session_state.get("selected_model", "gpt-3.5-turbo")
        temperature = st.session_state.get("temperature", 0.7)
        max_tokens = st.session_state.get("max_tokens", 500)
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content
        return content.strip() if content is not None else ""
    except Exception as e:
        return f"Erreur lors de la génération de la réponse : {str(e)}"

def _add_system_message(action_description, all_dfs):
    """Ajoute un message système basé sur une action rapide."""
    message = "Action non reconnue."
    if action_description == "Analyse des données en cours...":
        message = "Analyse des données effectuée. Voici un résumé :\n\n"
        if all_dfs:
            for sheet_name, df in all_dfs.items():
                if df is not None and not df.empty:
                    message += f"{sheet_name}: {len(df)} entrées avec {len(df.columns)} critères\n"
        message += "\nQue souhaitez-vous analyser en détail ?"
        
    elif action_description == "Génération de suggestions...":
        message = """
        Suggestions d'amélioration pour votre analyse :
        
        1. Visualisations : Ajoutez des graphiques pour mieux comprendre les tendances
        2. Filtres avancés : Utilisez les filtres pour des analyses ciblées
        3. Métriques clés : Identifiez les KPIs les plus importants
        4. Comparaisons : Analysez les écarts entre entreprises
        5. Documentation : Documentez vos insights pour le suivi
        
        Sur quel point souhaitez-vous de l'aide en priorité ?
        """
    
    # Ajouter le message à l'historique
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    
    st.rerun()

def _render_temporary_interface(all_dfs):
    """Affiche une interface temporaire en attendant la correction d'OpenAI."""
    st.markdown("---")
    st.markdown("### Assistant Temporaire (sans IA)")
    
    st.info("""
    En attendant la correction d'OpenAI, voici ce que je peux vous dire sur vos données :
    """)
    
    if all_dfs:
        _render_data_summary(all_dfs)
        _render_suggestions()
    
    _render_feedback_section()

def _render_data_summary(all_dfs):
    """Affiche le résumé des données dans la colonne de gauche."""
    col1, _ = st.columns(2)
    with col1:
        _render_data_summary_title()
        total_rows, total_cols = _compute_data_metrics(all_dfs)
        _render_data_details(all_dfs)
        _render_data_metrics(total_rows, total_cols)

def _render_data_summary_title():
    st.markdown("#### Résumé des données")

def _compute_data_metrics(all_dfs):
    total_rows = 0
    total_cols = 0
    for sheet_name, df in all_dfs.items():
        if df is not None and not df.empty:
            total_rows += len(df)
            total_cols += len(df.columns)
    return total_rows, total_cols

def _render_data_details(all_dfs):
    for sheet_name, df in all_dfs.items():
        if df is not None and not df.empty:
            st.write(f"• {sheet_name} : {len(df)} lignes, {len(df.columns)} colonnes")

def _render_data_metrics(total_rows, total_cols):
    st.metric("Total lignes", total_rows)
    st.metric("Total colonnes", total_cols)

def _render_suggestions():
    """Affiche les suggestions d'analyse dans la colonne de droite."""
    _, col2 = st.columns(2)
    with col2:
        _render_suggestions_title()
        _render_suggestions_list()
        _render_suggestions_refresh()

def _render_suggestions_title():
    st.markdown("#### Suggestions d'analyse")

def _render_suggestions_list():
    st.write("Actions recommandées :")
    st.write("- Utilisez l'Analyse Comparative pour comparer les entreprises")
    st.write("- Filtrez par catégorie pour des analyses ciblées") 
    st.write("- Examinez les critères différenciateurs")
    st.write("- Documentez vos conclusions")

def _render_suggestions_refresh():
    if st.button("Actualiser les données"):
        st.rerun()

def _render_feedback_section():
    """Affiche la zone de feedback temporaire et les demandes enregistrées."""
    st.markdown("---")
    _render_feedback_title()
    user_feedback = _render_feedback_input()
    _handle_feedback_submit(user_feedback)
    _render_pending_feedback()

def _render_feedback_title():
    st.markdown("#### Feedback temporaire")

def _render_feedback_input():
    return st.text_area(
        "Décrivez ce que vous cherchez à analyser :",
        placeholder="Ex : Je souhaite comparer les entreprises sur les critères de sécurité...",
        height=100
    )

def _handle_feedback_submit(user_feedback):
    if st.button("Enregistrer la demande") and user_feedback:
        if "temp_feedback" not in st.session_state:
            st.session_state.temp_feedback = []
        st.session_state.temp_feedback.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "request": user_feedback
        })
        st.success("Demande enregistrée ! Elle sera traitée une fois l'IA disponible.")

def _render_pending_feedback():
    if "temp_feedback" in st.session_state and st.session_state.temp_feedback:
        st.markdown("#### Demandes en attente")
        for i, feedback in enumerate(st.session_state.temp_feedback):
            with st.expander(f"Demande {i+1} - {feedback['timestamp']}"):
                st.write(feedback['request'])
