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
    st.title("Assistant IA IVÉO")
    st.markdown("### Assistant professionnel pour l'analyse de données")

def _render_openai_unavailable(all_dfs):
    st.warning("**OpenAI temporairement non disponible** - Conflit de versions détecté")
    st.markdown("""
    ### �️ **Solution rapide** :
    
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
            '<div class="assistant-message">Bienvenue sur le service d\'analyse de données IVÉO. Posez votre question pour démarrer la conversation.</div>',
            unsafe_allow_html=True
        )
    
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
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
            placeholder="Tapez votre question ici...",
            key="main_chat_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Envoyer", key="main_send", use_container_width=True)
    
    # Traitement de l'envoi
    if (send_button or user_input) and user_input:
        # Ajouter le message de l'utilisateur
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        # Tenter la connexion et l'appel à l'API
        if not init_openai():
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "Veuillez configurer votre clé API OpenAI dans la sidebar.",
                "timestamp": datetime.now().isoformat()
            })
            return
        with st.spinner("🤔 L'IA réfléchit..."):
            ai_response = _get_ai_response(user_input, st.session_state.get("all_dfs", {}))
        # Si erreur API, on affiche le message d'erreur mais on n'appelle pas st.rerun()
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        # On ne fait st.rerun() que si la réponse n'est pas une erreur
        if ai_response is not None and not ai_response.startswith("Erreur") and not ai_response.startswith("Veuillez"):
            st.rerun()

def _get_ai_response(user_message, all_dfs, is_quick=False):
    """
    Obtient une réponse de l'API OpenAI.
    
    Args:
        user_message (str): Message de l'utilisateur
        all_dfs (dict): DataFrames disponibles
        is_quick (bool): Si c'est une question rapide
        
    Returns:
        str: Réponse de l'IA
    """
    if not OPENAI_AVAILABLE:
        return "OpenAI n'est pas disponible. Veuillez installer la librairie."
        
    try:
        # Contexte système
        system_context = _build_system_context(all_dfs)
        
        # Préparer les messages
        messages = [
            {"role": "system", "content": system_context}
        ]
        
        # Ajouter l'historique récent si ce n'est pas une question rapide
        if not is_quick and st.session_state.chat_messages:
            recent_messages = st.session_state.chat_messages[-6:]  # 6 derniers messages
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Ajouter le message actuel
        messages.append({"role": "user", "content": user_message})
        
        # Appel à l'API OpenAI
        if openai_client is None:
            return "Client OpenAI non initialisé. Vérifiez votre clé API."
            
        # Convertir les messages au format requis par OpenAI
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "system":
                formatted_messages.append({"role": "system", "content": msg["content"]})
            elif msg["role"] == "user":
                formatted_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                formatted_messages.append({"role": "assistant", "content": msg["content"]})
            else:
                formatted_messages.append({"role": "user", "content": msg["content"]})

        response = openai_client.chat.completions.create(
            model=st.session_state.get("selected_model", "gpt-3.5-turbo"),
            messages=formatted_messages,
            temperature=st.session_state.get("temperature", 0.7),
            max_tokens=st.session_state.get("max_tokens", 500)
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Erreur lors de la communication avec l'IA : {str(e)}"

def _build_system_context(all_dfs):
    """
    Construit le contexte système pour l'IA.
    
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
    - Suggère des actions concrètes quand c'est pertinent
    
    DONNÉES DISPONIBLES :
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
