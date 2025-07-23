import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.pages.home import get_available_entreprises, COLS_DESCRIPTION, LABEL_INFORMATION_COMPLEMENTAIRE, LABEL_ENTREPRISES
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
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from sidebar import show_sidebar, show_sidebar_alignement, apply_sidebar_styles



# === CONSTANTES GLOBALES (labels, messages, couleurs, etc.) ===
NO_INFO_MESSAGE = "Aucune information complémentaire disponible"
COL_FONCTIONNALITES = "Type d'exigence"
COL_CATEGORIES = "Domaine"
COL_EXIGENCE = "Exigence différenciateur"
COL_DESCRIPTION = "Exigence"
COL_INFO_COMP = "Information complémentaire"
SELECTION_COL = "Sélection"

# Labels et couleurs pour les badges
BADGE_RESPECTE_COLOR = "#28a745"
BADGE_RESPECTE_TEXT = "1"
BADGE_RESPECTE_LABEL = "Critère respecté"
BADGE_RESPECTE_CARD_COLOR = "#d4edda"

BADGE_NON_RESPECTE_COLOR = "#dc3545"
BADGE_NON_RESPECTE_TEXT = "0"
BADGE_NON_RESPECTE_LABEL = "Critère non respecté"
BADGE_NON_RESPECTE_CARD_COLOR = "#f8d7da"

BADGE_NON_EVALUE_COLOR = "#6c757d"
BADGE_NON_EVALUE_TEXT = "N/A"
BADGE_NON_EVALUE_LABEL = "Non évalué"
BADGE_NON_EVALUE_CARD_COLOR = "#e2e3e5"

# Labels pour la sidebar et les messages utilisateur
LABEL_PARAM_COMPARAISON = "Paramètres de comparaison"
LABEL_SELECT_ENTREPRISES = "Sélectionnez les entreprises à comparer :"
LABEL_SELECT_ENTREPRISES_HELP = "Choisissez les entreprises que vous souhaitez comparer."
LABEL_FILTRES = "Filtres"
LABEL_FILTRE_TYPE_EXIGENCE = "Filtrer par type d'exigence :"
LABEL_FILTRE_TYPE_EXIGENCE_HELP = "Sélectionnez les types d'exigence à afficher."
LABEL_FILTRE_CATEGORIE = "Filtrer par catégorie :"
LABEL_FILTRE_CATEGORIE_HELP = "Sélectionnez les catégories à afficher."
LABEL_FILTRE_EXIGENCE = "Filtrer par exigence différenciatrice :"
LABEL_FILTRE_EXIGENCE_HELP = "Sélectionnez les niveaux d'exigence à afficher."
LABEL_WARNING_SELECT_ENTREPRISE = "Veuillez sélectionner au moins une entreprise."
LABEL_WARNING_NO_DATA = "Aucune donnée ne correspond aux critères sélectionnés."
LABEL_PAGE_TITLE = "Analyse Comparative"
LABEL_GRILLE_EVAL = "Grille d'évaluation"
LABEL_INFOS_COMP = "Informations complémentaires pour : {exigence}"
LABEL_IMPOSSIBLE_EXIGENCE = "Impossible de récupérer l'exigence depuis la grille"
LABEL_AUCUNE_LIGNE = "Aucune ligne trouvée pour l'exigence: {exigence}"
LABEL_AUCUNE_INFO_COMP = "Aucune information complémentaire disponible pour : {exigence}"


def display(all_dfs):
    """
    Fonction principale d'affichage de la page Analyse Comparative.
    
    Args:
        all_dfs (dict): Dictionnaire contenant tous les DataFrames du fichier Excel
    """
    # Appliquer les styles de la sidebar
    apply_sidebar_styles()
    _render_page_header()
    df_comparative = all_dfs.get("Analyse comparative")
    df_ent = all_dfs.get("Entreprise")
    df_sol = all_dfs.get("Solution")
    if df_comparative is None:
        st.error("La feuille 'Analyse comparative' est introuvable dans le fichier Excel.")
        return
    success, df_filtered, entreprise_cols, _ = _prepare_data(df_comparative)
    if not success:
        return
    # --- Synchronisation stricte avec la sélection globale de home.py ---
    # Diagnostic : liste des entreprises dans chaque feuille
    # ...existing code...
    # Utiliser directement les colonnes d'entreprises extraites de la feuille Analyse comparative
    available_entreprises = entreprise_cols
    if not available_entreprises:
        st.error("Aucune colonne d'entreprise trouvée dans la feuille 'Analyse comparative'.")
        return
    # On lit la sélection globale depuis les cookies de session (clé utilisée dans show_sidebar)
    import json
    from sidebar import cookies
    raw = cookies.get('entreprises_selected')
    selected_entreprises = json.loads(raw) if raw else available_entreprises
    selected_entreprises = [e for e in selected_entreprises if e in available_entreprises]
    if not selected_entreprises:
        st.warning("Veuillez sélectionner au moins une entreprise dans la page d'accueil.")
        return
    # --- Interface utilisateur (filtres supplémentaires, sans multiselect entreprises) ---
    selected_types_exigence, selected_categories, selected_exigences = _setup_sidebar_filters(df_filtered)
    df_filtered_criteria = _filter_data_by_criteria(df_filtered, selected_types_exigence, selected_categories, selected_exigences)
    if df_filtered_criteria is None or df_filtered_criteria.empty:
        st.warning(LABEL_WARNING_NO_DATA)
        return
    # --- Affichage de la grille d'évaluation ---
    _render_evaluation_grid(df_filtered_criteria, selected_entreprises)


def _render_page_header():
    """Affiche l'en-tête de la page avec le titre et la description."""
    st.title(LABEL_PAGE_TITLE)


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
        tuple: (selected_entreprises, selected_types_exigence, selected_categories, selected_exigences)
    """
def _setup_sidebar_filters(df_filtered):
    with st.sidebar:
        st.markdown(f"### {LABEL_FILTRES}")
        # Filtre par type d'exigence
        types_exigence_unique = df_filtered[COL_FONCTIONNALITES].dropna().unique()
        selected_types_exigence = st.multiselect(
            LABEL_FILTRE_TYPE_EXIGENCE,
            options=types_exigence_unique,
            default=types_exigence_unique,
            help=LABEL_FILTRE_TYPE_EXIGENCE_HELP
        )
        # Filtre par catégorie
        categories_unique = df_filtered[COL_CATEGORIES].dropna().unique()
        selected_categories = st.multiselect(
            LABEL_FILTRE_CATEGORIE,
            options=categories_unique,
            default=categories_unique,
            help=LABEL_FILTRE_CATEGORIE_HELP
        )
        # Filtre par exigence
        exigences_unique = df_filtered[COL_EXIGENCE].dropna().unique()
        def transform_exigence_value(value):
            if str(value) == "0" or str(value) == "0.0":
                return "Non"
            elif str(value) == "1" or str(value) == "1.0":
                return "Oui"
            else:
                return str(value)
        exigences_display = [transform_exigence_value(val) for val in exigences_unique]
        exigences_mapping = dict(zip(exigences_display, exigences_unique))
        selected_exigences_display = st.multiselect(
            LABEL_FILTRE_EXIGENCE,
            options=exigences_display,
            default=exigences_display,
            help=LABEL_FILTRE_EXIGENCE_HELP
        )
        selected_exigences = [exigences_mapping[val] for val in selected_exigences_display]
    return selected_types_exigence, selected_categories, selected_exigences


def _filter_data_by_criteria(df_filtered, selected_types_exigence, selected_categories, selected_exigences):
    """
    Filtre les données selon les types d'exigence, catégories et exigences sélectionnées.
    
    Args:
        df_filtered (pd.DataFrame): DataFrame filtré des données
        selected_types_exigence (list): Liste des types d'exigence sélectionnés
        selected_categories (list): Liste des catégories sélectionnées
        selected_exigences (list): Liste des exigences sélectionnées
        
    Returns:
        pd.DataFrame: DataFrame filtré selon les critères
    """
    # Appliquer les filtres
    if selected_types_exigence:
        df_filtered = df_filtered[df_filtered[COL_FONCTIONNALITES].isin(selected_types_exigence)]
    
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
    st.markdown(f"### {LABEL_GRILLE_EVAL}")
    df_display = _format_scores_for_display(df_filtered, selected_entreprises)
    display_df = _prepare_display_dataframe(df_display, selected_entreprises)
    grid_options, custom_css = _build_aggrid_options(display_df, selected_entreprises)
    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=900,
        width='100%',
        allow_unsafe_jscode=True,
        theme="balham",
        custom_css=custom_css,
        enable_enterprise_modules=True
    )
    _display_selected_infos(grid_response, df_filtered, selected_entreprises)

def _format_scores_for_display(df_filtered, selected_entreprises):
    """Formatte les scores des entreprises en icônes pour l'affichage."""
    df_display = df_filtered.copy()
    def format_score_icons(value):
        str_value = str(value)
        if str_value in ["1", "1.0"]:
            return "✅"
        elif str_value in ["0", "0.0"]:
            return "❌"
        elif str_value in ["0.5", "½"]:
            return "⚠️"
        else:
            return "❓"
    for col in selected_entreprises:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(format_score_icons)
    return df_display

def _prepare_display_dataframe(df_display, selected_entreprises):
    """Prépare le DataFrame à afficher dans AgGrid."""
    # Utiliser la colonne COL_DESCRIPTION comme colonne principale
    info_cols = [COL_DESCRIPTION]  # Utiliser la colonne "Exigence"
    columns_to_display = info_cols + selected_entreprises
    display_df = df_display[columns_to_display].copy()
    # Les colonnes restent telles quelles
    st.markdown("""
    <style>
    .ag-cell span {
        box-shadow: 0 2px 6px rgba(44,62,80,0.10);
    }
    </style>
    """, unsafe_allow_html=True)
    display_df.insert(0, SELECTION_COL, False)
    return display_df

def _build_aggrid_options(display_df, selected_entreprises):
    """Construit les options et le CSS personnalisés pour AgGrid."""
    from st_aggrid import JsCode
    cell_renderer_js = JsCode("""
        function(params) {
            return params.value;
        }
    """)
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_column(SELECTION_COL, header_name="", width=32, pinned=True, cellStyle={"textAlign": "center"})
    for col in display_df.columns:
        if col != SELECTION_COL:
            if col in selected_entreprises:
                gb.configure_column(
                    col,
                    width=120,
                    cellStyle={"textAlign": "center", "fontSize": "20px", "paddingTop": "8px"},
                    cellRenderer=cell_renderer_js,
                    cellRendererParams={"innerRenderer": True},
                    autoHeight=True,
                    wrapText=True
                )
            else:
                gb.configure_column(
                    col,
                    width=120,
                    cellStyle={"textAlign": "center", "fontSize": "20px", "paddingTop": "8px"}
                )
    gb.configure_grid_options(rowHeight=50)
    gb.configure_grid_options(headerHeight=45)
    gb.configure_grid_options(
        defaultColDef={
            "headerClass": "custom-header"
        }
    )
    grid_options = gb.build()
    custom_css = {
        ".ag-header-cell-label": {
            "background": "#2c3e50",
            "font-weight": "600",
            "color": "#f5f7fa",
            "font-size": "1.15rem",
            "border-bottom": "2px solid #2980b9",
            "justify-content": "center",
            "align-items": "center",
            "border-radius": "8px 8px 0 0",
            "font-family": "'Segoe UI', 'Roboto', Arial, sans-serif"
        },
        ".ag-header": {
            "background": "#2c3e50",
            "box-shadow": "0 2px 8px rgba(44,62,80,0.08)",
            "border-radius": "8px 8px 0 0"
        },
        ".ag-cell": {
            "border-right": "2px solid #e0e0e0",
            "font-size": "22px",
            "padding": "12px",
            "background": "linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)",
            "box-shadow": "inset 0 1px 3px rgba(0,0,0,0.1)"
        },
        ".ag-row-even": {
            "background": "linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%)"
        },
        ".ag-row-odd": {
            "background": "linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%)"
        },
        ".ag-row:hover": {
            "background": "linear-gradient(145deg, #e3f2fd 0%, #bbdefb 100%) !important",
            "transition": "all 0.3s ease",
            "transform": "scale(1.02)",
            "box-shadow": "0 4px 8px rgba(0,0,0,0.15)"
        }
    }
    return grid_options, custom_css

def _display_selected_infos(grid_response, df_filtered, selected_entreprises):
    """Affiche les informations complémentaires pour les lignes sélectionnées."""
    selected_rows = grid_response["selected_rows"]
    if isinstance(selected_rows, pd.DataFrame):
        selected_rows = selected_rows.to_dict(orient="records")
    
    if not selected_rows:
        return
    st.markdown("---")
    for row in selected_rows:
        # Récupérer l'exigence depuis la grille
        selected_exigence = row.get(COL_DESCRIPTION)
        if selected_exigence is None:
            st.warning(LABEL_IMPOSSIBLE_EXIGENCE)
            continue
        # Trouver la ligne correspondante dans le DataFrame original
        matching_rows = df_filtered[df_filtered[COL_DESCRIPTION] == selected_exigence]
        if matching_rows.empty:
            st.warning(LABEL_AUCUNE_LIGNE.format(exigence=selected_exigence))
            continue
        idx = matching_rows.index[0]
        row_data = df_filtered.iloc[idx]
        infos_to_display = _get_infos_to_display(row_data, selected_entreprises, df_filtered)
        if infos_to_display:
            st.markdown(LABEL_INFOS_COMP.format(exigence=selected_exigence))
            for entreprise, info_complementaire in infos_to_display:
                st.markdown(f"**{entreprise}** :")
                st.info(info_complementaire)
        else:
            st.info(LABEL_AUCUNE_INFO_COMP.format(exigence=selected_exigence))

def _get_infos_to_display(row_data, selected_entreprises, df_filtered):
    """Retourne la liste des tuples (entreprise, info_complementaire) à afficher."""
    infos_to_display = []
    for entreprise in selected_entreprises:
        info_complementaire = _get_info_complementaire(row_data, entreprise, df_filtered)
        if info_complementaire and info_complementaire.strip() != NO_INFO_MESSAGE:
            infos_to_display.append((entreprise, info_complementaire))
    return infos_to_display


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
            if badge_info["text"] == "1":
                st.success(badge_info["label"])
            elif badge_info["text"] == "0":
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
            "color": BADGE_RESPECTE_COLOR,
            "text": BADGE_RESPECTE_TEXT,
            "label": BADGE_RESPECTE_LABEL,
            "card_color": BADGE_RESPECTE_CARD_COLOR
        }
    elif score_numeric == 0:
        return {
            "color": BADGE_NON_RESPECTE_COLOR,
            "text": BADGE_NON_RESPECTE_TEXT,
            "label": BADGE_NON_RESPECTE_LABEL,
            "card_color": BADGE_NON_RESPECTE_CARD_COLOR
        }
    else:
        return {
            "color": BADGE_NON_EVALUE_COLOR,
            "text": BADGE_NON_EVALUE_TEXT,
            "label": BADGE_NON_EVALUE_LABEL,
            "card_color": BADGE_NON_EVALUE_CARD_COLOR
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
