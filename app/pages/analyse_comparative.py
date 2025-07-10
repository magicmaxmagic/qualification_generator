"""
Page Analyse Comparative - Application IVÉO BI
==============================================

Cette page affiche une analyse comparative des solutions/entreprises avec un système 
de notation binaire (0 ou 1) pour évaluer les critères.

Fonctionnalités :
- Grille d'évaluation avec badges visuels binaires (0/1)
- Filtrage par type de critère
- Sélection multiple d'entreprises
- Justificatifs détaillés par critère
- Design moderne et responsive

Version : 2.0 - 2025.01.10
"""

import streamlit as st
import pandas as pd
from sidebar import show_sidebar, show_sidebar_alignement, apply_sidebar_styles

# Constantes
NO_INFO_MESSAGE = "Aucune information complémentaire disponible"
COL_FONCTIONNALITES = "Fonctionnalités"
COL_FONCTIONNALITE = "Fonctionnalité"
COL_CATEGORIES = "Catégories"
COL_EXIGENCE = "Exigence différenciateur"
COL_DESCRIPTION = "description"
COL_INFO_COMP = "Information complémentaire"


def display(all_dfs):
    """
    Fonction principale d'affichage de la page Analyse Comparative.
    
    Args:
        all_dfs (dict): Dictionnaire contenant tous les DataFrames du fichier Excel
    """
    # Appliquer les styles de la sidebar
    apply_sidebar_styles()
    
    # --- En-tête de la page ---
    _render_page_header()
    
    # --- Récupération des données ---
    df_comparative = all_dfs.get("Analyse comparative")
    if df_comparative is None:
        st.error("La feuille 'Analyse comparative' est introuvable dans le fichier Excel.")
        return
    
    # --- Validation et préparation des données ---
    success, df_filtered, entreprise_cols, _ = _prepare_data(df_comparative)
    if not success:
        return
    
    # --- Interface utilisateur ---
    selected_entreprises, selected_categories, selected_exigences = _setup_sidebar_controls(entreprise_cols, df_filtered)
    if not selected_entreprises:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return
    
    # Filtrer les données selon les critères sélectionnés
    df_filtered_criteria = _filter_data_by_criteria(df_filtered, selected_categories, selected_exigences)
    if df_filtered_criteria.empty:
        st.warning("Aucune donnée ne correspond aux critères sélectionnés.")
        return
    
    # --- Affichage de la grille d'évaluation ---
    _render_evaluation_grid(df_filtered_criteria, selected_entreprises)


def _render_page_header():
    """Affiche l'en-tête de la page avec le titre et la description."""
    st.title("Analyse Comparative")


def _prepare_data(df_comparative):
    """
    Prépare et valide les données pour l'analyse comparative.
    
    Args:
        df_comparative (pd.DataFrame): DataFrame contenant les données d'analyse comparative
        
    Returns:
        tuple: (success, df_filtered, entreprise_cols, justificatif_cols)
    """
    try:
        # Vérifier la structure des données
        if df_comparative.empty:
            st.error("La feuille 'Analyse comparative' est vide.")
            return False, None, None, None
        
        # Identifier les colonnes d'entreprises et justificatifs à partir de la 5ème colonne
        # Structure alternée : Entreprise, Info complémentaire, Entreprise, Info complémentaire...
        remaining_cols = df_comparative.columns[4:].tolist()
        entreprise_cols = []
        justificatif_cols = []
        
        for i, col in enumerate(remaining_cols):
            if COL_INFO_COMP in col:
                justificatif_cols.append(col)
            else:
                entreprise_cols.append(col)
        
        if not entreprise_cols:
            st.error("Aucune colonne d'entreprise trouvée dans les données.")
            return False, None, None, None
        
        # Utiliser la colonne "Fonctionnalités" comme clé principale
        if COL_FONCTIONNALITES not in df_comparative.columns:
            st.error(f"La colonne '{COL_FONCTIONNALITES}' est introuvable dans les données.")
            return False, None, None, None
        
        # Filtrer les données vides
        df_filtered = df_comparative[df_comparative[COL_FONCTIONNALITES].notna()].copy()
        
        if df_filtered.empty:
            st.error("Aucune fonctionnalité trouvée dans les données.")
            return False, None, None, None
        
        return True, df_filtered, entreprise_cols, justificatif_cols
        
    except Exception as e:
        st.error(f"Erreur lors de la préparation des données : {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False, None, None, None


def _setup_sidebar_controls(entreprise_cols, df_filtered):
    """
    Configure les contrôles de la sidebar pour la sélection d'entreprises et les filtres.
    
    Args:
        entreprise_cols (list): Liste des colonnes d'entreprises
        df_filtered (pd.DataFrame): DataFrame filtré des données
        
    Returns:
        tuple: (selected_entreprises, selected_categories, selected_exigences)
    """
    with st.sidebar:
        st.markdown("### Paramètres de comparaison")
        
        # Sélection des entreprises - toutes par défaut
        selected_entreprises = st.multiselect(
            "Sélectionnez les entreprises à comparer :",
            options=entreprise_cols,
            default=entreprise_cols,  # Toutes les entreprises par défaut
            help="Choisissez les entreprises que vous souhaitez comparer."
        )
        
        st.markdown("---")
        st.markdown("### Filtres")
        
        # Filtre par catégorie
        categories_unique = df_filtered[COL_CATEGORIES].dropna().unique()
        selected_categories = st.multiselect(
            "Filtrer par catégorie :",
            options=categories_unique,
            default=categories_unique,
            help="Sélectionnez les catégories à afficher."
        )
        
        # Filtre par exigence
        exigences_unique = df_filtered[COL_EXIGENCE].dropna().unique()
        selected_exigences = st.multiselect(
            "Filtrer par exigence :",
            options=exigences_unique,
            default=exigences_unique,
            help="Sélectionnez les niveaux d'exigence à afficher."
        )
    
    return selected_entreprises, selected_categories, selected_exigences


def _filter_data_by_criteria(df_filtered, selected_categories, selected_exigences):
    """
    Filtre les données selon les catégories et exigences sélectionnées.
    
    Args:
        df_filtered (pd.DataFrame): DataFrame filtré des données
        selected_categories (list): Liste des catégories sélectionnées
        selected_exigences (list): Liste des exigences sélectionnées
        
    Returns:
        pd.DataFrame: DataFrame filtré selon les critères
    """
    # Appliquer les filtres
    if selected_categories:
        df_filtered = df_filtered[df_filtered[COL_CATEGORIES].isin(selected_categories)]
    
    if selected_exigences:
        df_filtered = df_filtered[df_filtered[COL_EXIGENCE].isin(selected_exigences)]
    
    return df_filtered


def _render_evaluation_grid(df_filtered, selected_entreprises):
    """
    Affiche la grille d'évaluation avec les badges binaires.
    
    Args:
        df_filtered (pd.DataFrame): DataFrame filtré des données
        selected_entreprises (list): Liste des entreprises sélectionnées
    """
    st.markdown("### Grille d'évaluation")    
    # Créer une copie pour l'affichage
    df_display = df_filtered.copy()
    
    # Remplacer les valeurs 0/1 par des icônes pour les colonnes d'entreprises
    def format_score(value):
        """Convertit les scores 0/1 en icônes visuelles."""
        str_value = str(value)
        if str_value in ["1", "1.0"]:
            return "✅"
        elif str_value in ["0", "0.0"]:
            return "❌"
        else:
            return str_value
    
    for col in selected_entreprises:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(format_score)
    
    # Colonnes à afficher : Fonctionnalité, Description + entreprises sélectionnées
    # Exclure Catégorie et Exigence (colonnes 0 et 2)
    info_cols = [df_display.columns[1], df_display.columns[3]]  # Fonctionnalités et description
    columns_to_display = info_cols + selected_entreprises
    
    # Créer le tableau avec les colonnes demandées
    display_df = df_display[columns_to_display].copy()
    
    # Personnaliser les noms des colonnes
    display_df.columns = [
        COL_FONCTIONNALITE if col == COL_FONCTIONNALITES else
        "Description" if col == COL_DESCRIPTION else
        col for col in display_df.columns
    ]
    
    # Afficher le tableau avec gestion des clics
    event = st.dataframe(
        display_df, 
        use_container_width=True,
        column_config={
            **{col: st.column_config.TextColumn(
                col,
                help=f"Cliquez pour voir les détails de {col}",
                width="small"
            ) for col in selected_entreprises},
            COL_FONCTIONNALITE: st.column_config.TextColumn(
                COL_FONCTIONNALITE,
                width="medium"
            ),
            "Description": st.column_config.TextColumn(
                "Description", 
                width="medium"
            )
        },
        hide_index=True,
        height=800,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Gérer les clics sur les lignes pour afficher les détails
    if event.selection and event.selection.get("rows"):
        selected_row = event.selection["rows"][0]
        
        # Récupérer les données de la ligne sélectionnée
        row_data = df_filtered.iloc[selected_row]
        
        # Afficher les détails avec sélecteur d'entreprise
        st.markdown("---")
        st.markdown("### Informations détaillées")
        
        # Ajouter un sélecteur d'entreprise
        col1, col2 = st.columns([1, 3])
        
        with col1:
            selected_entreprise = st.selectbox(
                "Choisir une entreprise :",
                options=selected_entreprises,
                key=f"entreprise_selector_{selected_row}",
                help="Sélectionnez l'entreprise pour voir ses informations complémentaires"
            )
        
        with col2:
            if selected_entreprise:
                _show_detail_card(row_data, selected_entreprise, df_filtered)
    
    # Ajouter du CSS pour styliser le tableau
    st.markdown(
        """
        <style>
        .stDataFrame {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 16px;
        }
        .stDataFrame > div {
            border-radius: 10px;
        }
        .stDataFrame [data-testid="stDataFrameResizeHandle"] {
            display: none;
        }
        .stDataFrame table {
            border-collapse: separate;
            border-spacing: 0;
            width: 80%;
            margin: 0 auto;
        }
        .stDataFrame th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            padding: 18px 8px;
            text-align: center;
            border: none;
            position: sticky;
            top: 0;
            z-index: 10;
            font-size: 16px;
        }
        .stDataFrame td {
            padding: 16px 8px;
            text-align: center;
            border-bottom: 1px solid #f0f0f0;
            border-right: 1px solid #f0f0f0;
            font-size: 16px;
            min-height: 60px;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .stDataFrame tr:hover {
            background-color: #e3f2fd;
            transition: background-color 0.3s ease;
        }
        .stDataFrame td:first-child,
        .stDataFrame td:nth-child(2) {
            text-align: left;
            font-weight: 500;
            background-color: #fafafa;
            padding: 16px 12px;
        }
        .stDataFrame tr:nth-child(even) td:first-child,
        .stDataFrame tr:nth-child(even) td:nth-child(2) {
            background-color: #f0f0f0;
        }
        /* Agrandir les icônes */
        .stDataFrame td {
            line-height: 1.8;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def _show_detail_card(row_data, entreprise_name, df_filtered):
    """
    Affiche une carte détaillée avec les informations complémentaires.
    
    Args:
        row_data (pd.Series): Données de la ligne sélectionnée
        entreprise_name (str): Nom de l'entreprise
        df_filtered (pd.DataFrame): DataFrame complet pour trouver les justificatifs
    """
    # Récupérer les informations de base
    fonctionnalite = row_data.get(COL_FONCTIONNALITES, "N/A")
    
    # Récupérer le score de l'entreprise
    score = row_data.get(entreprise_name, "")
    score_numeric = pd.to_numeric(score, errors="coerce")
    
    # Déterminer le badge et la couleur
    badge_info = _get_badge_info(score_numeric)
    
    # Trouver l'information complémentaire correspondante
    info_complementaire = _get_info_complementaire(row_data, entreprise_name, df_filtered)
    
    # Afficher la carte avec des composants Streamlit natifs
    with st.container():
        # En-tête avec le nom de l'entreprise et le badge
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{entreprise_name}")
        with col2:
            if badge_info["text"] == "✅":
                st.success(badge_info["label"])
            elif badge_info["text"] == "❌":
                st.error(badge_info["label"])
            else:
                st.info(badge_info["label"])
        
        # Informations principales
        st.markdown(f"**Fonctionnalité :** {fonctionnalite}")
        
        # Information complémentaire
        st.markdown("**Information complémentaire :**")
        if info_complementaire and info_complementaire.strip() != NO_INFO_MESSAGE:
            st.info(info_complementaire)
        else:
            st.warning(NO_INFO_MESSAGE)
        
        st.markdown("---")


def _get_badge_info(score_numeric):
    """
    Retourne les informations de badge basées sur le score.
    
    Args:
        score_numeric (float): Score numérique
        
    Returns:
        dict: Informations de badge
    """
    if score_numeric == 1:
        return {
            "color": "#28a745",
            "text": "✅",
            "label": "Critère respecté",
            "card_color": "#d4edda"
        }
    elif score_numeric == 0:
        return {
            "color": "#dc3545",
            "text": "❌",
            "label": "Critère non respecté",
            "card_color": "#f8d7da"
        }
    else:
        return {
            "color": "#6c757d",
            "text": "N/A",
            "label": "Non évalué",
            "card_color": "#e2e3e5"
        }


def _get_info_complementaire(row_data, entreprise_name, df_filtered):
    """
    Récupère l'information complémentaire pour une entreprise donnée.
    
    Args:
        row_data (pd.Series): Données de la ligne
        entreprise_name (str): Nom de l'entreprise
        df_filtered (pd.DataFrame): DataFrame filtré
        
    Returns:
        str: Information complémentaire
    """
    # Identifier les colonnes d'entreprises et justificatifs
    remaining_cols = df_filtered.columns[4:].tolist()
    entreprise_cols = [col for col in remaining_cols if COL_INFO_COMP not in col]
    justificatif_cols = [col for col in remaining_cols if COL_INFO_COMP in col]
    
    # Mapper l'entreprise à sa colonne de justificatif
    if entreprise_name in entreprise_cols:
        entreprise_index = entreprise_cols.index(entreprise_name)
        if entreprise_index < len(justificatif_cols):
            justif_col = justificatif_cols[entreprise_index]
            info_complementaire = row_data.get(justif_col, NO_INFO_MESSAGE)
            
            # Vérifier si la valeur est NaN ou vide
            if pd.isna(info_complementaire) or str(info_complementaire).strip() == "":
                return NO_INFO_MESSAGE
            return str(info_complementaire)
    
    return NO_INFO_MESSAGE
