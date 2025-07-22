# Utilitaire pour obtenir la liste cohérente des entreprises présentes dans toutes les feuilles nécessaires
def get_available_entreprises(df_ent=None, df_sol=None, df_comp=None):
    sets = []
    if df_ent is not None and LABEL_ENTREPRISES in df_ent.columns:
        sets.append(set(df_ent[LABEL_ENTREPRISES].dropna().unique()))
    if df_sol is not None and LABEL_ENTREPRISES in df_sol.columns:
        sets.append(set(df_sol[LABEL_ENTREPRISES].dropna().unique()))
    if df_comp is not None:
        # Colonnes d'entreprises dans Comparatif (hors description)
        entreprises_comp = [col for col in df_comp.columns if col not in COLS_DESCRIPTION and LABEL_INFORMATION_COMPLEMENTAIRE not in col]
        sets.append(set(entreprises_comp))
    if not sets:
        return []
    # Intersection de toutes les sources
    return sorted(list(set.intersection(*sets)))
# app/pages/home.py



import streamlit as st
import plotly.express as px
import pandas as pd
from sidebar import show_sidebar, cookies
import json

# === CONSTANTES GLOBALES ===
SCORE_GLOBAL = "Score global"

# === CONSTANTES GLOBALES (labels, colonnes, couleurs, marges, etc.) ===
COLS_DESCRIPTION = ["Type d'exigence", "Domaine", "Exigence différenciateur", "Exigence"]
LABEL_ENTREPRISES = "Entreprises"
LABEL_SOLUTIONS = "Solutions"
LABEL_EXIGENCES = "Exigences"
LABEL_HIST_COLOR = "Histogramme"
LABEL_ANNEE_FONDATION = "Année de fondation"
LABEL_ANNEE_CREATION = "Année de création"
LABEL_LOGO = "Logo"
LABEL_COUT_INIT = "Coût initial"
LABEL_COUT_REC = "Coût récurrent"
LABEL_COUT_TOTAL = "Coût total prévisionnel"
LABEL_RESPECTE = "Respecté"
LABEL_NON_RESPECTE = "Non respecté"
LABEL_STATUT = "Statut"
LABEL_NB_CRITERES = "Nombre de critères"
LABEL_TYPE_COUT = "Type de coût"
LABEL_MONTANT = "Montant (€/$)"
LABEL_EFFECTIF = "Effectif"
LABEL_EMPLOYES = "employé"
LABEL_INFORMATION_COMPLEMENTAIRE = "Information complémentaire"

KEY_HIST_COLOR = "home_hist_color"
KEY_HIST_COLOR_EXPANDER = "home_hist_color_expander"
KEY_SLIDER_MOIS = "slider_mois_prevision_expander"
KEY_PLOTLY_CLASS = "plotly_class"
KEY_PLOTLY_REP = "plotly_rep"
KEY_PLOTLY_COST = "plotly_cost_expander"

COLOR_DEFAULT = "#0072B2"
COLOR_COST_INIT = "#16a085"
COLOR_COST_REC = "#e67e22"
COLOR_COST_TOTAL = "#2980b9"
COLOR_REP_OK = "#2980b9"
COLOR_REP_NOK = "#dc3545"

PLOTLY_MARGIN = dict(l=20, r=20, t=20, b=40)
PLOTLY_BG = "#ffffff"
PLOTLY_HEIGHT = 320
PLOTLY_TEMPLATE = "simple_white"

HTML_HR = "<hr style='margin:0.5em 0 1.2em 0; border:0; border-top:1.5px solid #eee;'>"

TITRE_HEADER = "Qualification BI – Vue d'ensemble"
TITRE_LOGOS = "Nos entreprises participantes"
TITRE_FRISE = "Année de création des entreprises"
TITRE_CLASSEMENT = "Classement des entreprises par score global"
TITRE_REPARTITION = "Répartition des scores par entreprise (respecté/non respecté)"
TITRE_COST = "Comparatif prévisionnel des coûts par entreprise"
TITRE_ANNEE_CREATION = "Année de création des entreprises"

IMG_HEADER = "https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg"
IMG_ENTREPRISE = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
IMG_SOL = "https://cdn-icons-png.flaticon.com/512/1828/1828817.png"
IMG_EXIG = "https://cdn-icons-png.flaticon.com/512/1828/1828919.png"

def display(all_dfs: dict):
    """
    Fonction principale qui orchestre l'affichage de la page d'accueil BI.
    Elle appelle les sous-fonctions pour chaque section : header, bandeau, logos, frise, sidebar, analyses.
    """
    inject_responsive_css()
    df_ent = all_dfs.get("Entreprise")
    df_sol = all_dfs.get("Solution")
    df_comp = all_dfs.get("Comparatif")

    show_header()
    # On déplace la sélection d'entreprises AVANT l'affichage des logos
    # Liste cohérente des entreprises présentes dans toutes les feuilles
    available_entreprises = get_available_entreprises(df_ent, df_sol, df_comp)
    selected_entreprises = show_sidebar(
        label=LABEL_ENTREPRISES,
        options=available_entreprises,
        default=available_entreprises,
        multiselect=True
    ) if available_entreprises else []
    show_bandeau_summary(df_ent, df_sol, df_comp, selected_entreprises)
    show_logos(df_ent, selected_entreprises)
    # Toutes les analyses doivent utiliser la même sélection globale !
    show_frise(df_ent, selected_entreprises)
    show_analyses(df_comp, df_sol, selected_entreprises)

def show_bandeau_summary(df_ent, df_sol, df_comp, selected_entreprises=None):
    """Affiche le bandeau récapitulatif avec le nombre d'entreprises, solutions, exigences, filtré si besoin."""
    nb_entreprises = _filtered_count(df_ent, LABEL_ENTREPRISES, selected_entreprises)
    nb_solutions = _filtered_solution_count(df_sol, selected_entreprises)
    nb_exigences = _filtered_exigence_count(df_comp)
    _display_bandeau_items(nb_entreprises, nb_solutions, nb_exigences)
    st.markdown("---")

def inject_responsive_css():
    st.markdown(
        """
<style>
img { max-width: 100%; height: auto; }
.block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
@media (max-width: 900px) {
    .stColumns { flex-direction: column !important; }
    .stColumn { width: 100% !important; min-width: 0 !important; }
}
@media (max-width: 600px) {
    h1, h2, h3, h4, h5, h6 { font-size: 1.1em !important; }
    .stButton>button, .stSlider, .stSelectbox, .stMultiSelect { font-size: 1em !important; }
}
</style>
        """,
        unsafe_allow_html=True
    )
    
def show_header():
    """Affiche le header principal de la page."""
    st.markdown(f"""
        <div style='text-align:center; margin-bottom: 0.5em;'>
            <img src='{IMG_HEADER}' width='80' style='margin-bottom:0.5em;' />
            <h1 style='color:{COLOR_COST_TOTAL}; margin-bottom:0;'>{TITRE_HEADER}</h1>
        </div>
    """, unsafe_allow_html=True)


def show_bandeau(df_ent, df_sol, df_comp, selected_entreprises=None):
    """Affiche le bandeau récapitulatif avec le nombre d'entreprises, solutions, exigences, filtré si besoin."""
    nb_entreprises = _filtered_count(df_ent, LABEL_ENTREPRISES, selected_entreprises)
    nb_solutions = _filtered_solution_count(df_sol, selected_entreprises)
    nb_exigences = _filtered_exigence_count(df_comp)
    _display_bandeau_items(nb_entreprises, nb_solutions, nb_exigences)
    st.markdown("---")

def _filtered_count(df, col_name, selected=None):
    if df is None:
        return 0
    if selected is not None and col_name in df.columns:
        return df[df[col_name].isin(selected)][col_name].nunique()
    return df[col_name].nunique() if col_name in df.columns else len(df)

def _filtered_solution_count(df_sol, selected=None):
    if df_sol is None:
        return 0
    if selected is not None and LABEL_ENTREPRISES in df_sol.columns:
        if LABEL_SOLUTIONS in df_sol.columns:
            return df_sol[df_sol[LABEL_ENTREPRISES].isin(selected)][LABEL_SOLUTIONS].nunique()
        else:
            return df_sol[df_sol[LABEL_ENTREPRISES].isin(selected)].shape[0]
    return df_sol[LABEL_SOLUTIONS].nunique() if LABEL_SOLUTIONS in df_sol.columns else len(df_sol)

def _filtered_exigence_count(df_comp):
    return len(df_comp) if df_comp is not None else 0

def _display_bandeau_items(nb_entreprises, nb_solutions, nb_exigences):
    cols = st.columns(3)
    items = [
        (IMG_ENTREPRISE, COLOR_COST_TOTAL, nb_entreprises, LABEL_ENTREPRISES),
        (IMG_SOL, COLOR_COST_INIT, nb_solutions, LABEL_SOLUTIONS),
        (IMG_EXIG, COLOR_COST_REC, nb_exigences, LABEL_EXIGENCES)
    ]
    for i, (img, color, nb, label) in enumerate(items):
        with cols[i % 3]:
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<img src='{img}' width='38'/><br>"
                f"<span style='font-size:1.6em; color:{color}; font-weight:bold'>{nb}</span><br>"
                f"<span style='color:#888;'>{label}</span></div>",
                unsafe_allow_html=True
            )


def show_logos(df_ent, selected_entreprises=None):
    """Affiche les logos des entreprises participantes."""
    if df_ent is None or LABEL_ENTREPRISES not in df_ent.columns:
        return

    # Filtrer selon la sélection si fournie
    if selected_entreprises is not None:
        df_ent = df_ent[df_ent[LABEL_ENTREPRISES].isin(selected_entreprises)]

    st.markdown(
        f"<div style='text-align:center; font-size:1.1em; margin-bottom:0.5em; color:{COLOR_COST_TOTAL}; font-weight:bold;'>{TITRE_LOGOS}</div>",
        unsafe_allow_html=True
    )

    url_logo_col = _find_url_logo_col(df_ent.columns)
    logos = df_ent[[c for c in [url_logo_col, LABEL_ENTREPRISES] if c in df_ent.columns]].copy() if url_logo_col else df_ent[[LABEL_ENTREPRISES]].copy()
    n_logos = len(logos)

    if n_logos == 1:
        _render_single_logo(logos.iloc[0], url_logo_col)
    elif n_logos == 2:
        _render_two_logos(logos, url_logo_col)
    elif n_logos > 2:
        _render_multiple_logos(logos, url_logo_col)
    # Suppression de la ligne horizontale ici pour éviter la multiplication des lignes

def _find_url_logo_col(cols):
    import unicodedata
    def normalize(s):
        return ''.join([c for c in unicodedata.normalize('NFKD', str(s)) if not unicodedata.combining(c)]).replace(' ', '').lower()
    for col in cols:
        if normalize(col) in [normalize('URL (logo)'), 'urllogo', 'logo', 'url_logo', 'url', 'logourl']:
            return col
    return None

def _get_logo_url(row, url_logo_col):
    if url_logo_col and url_logo_col in row and pd.notna(row[url_logo_col]):
        return row[url_logo_col]
    return IMG_ENTREPRISE

def _render_single_logo(row, url_logo_col):
    st.markdown('<div style="display:flex;justify-content:center;">', unsafe_allow_html=True)
    logo_url = _get_logo_url(row, url_logo_col)
    st.markdown(f'''
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.3em;min-width:120px;">
    <img src="{logo_url}" width="70" style="display:block;margin:0 auto 0.2em auto;" />
    <div style="text-align:center; font-size:0.95em; color:#555; font-weight:500;">{row[LABEL_ENTREPRISES]}</div>
</div>
''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def _render_two_logos(logos, url_logo_col):
    cols = st.columns(2)
    for i, (_, row) in enumerate(logos.iterrows()):
        with cols[i]:
            logo_url = _get_logo_url(row, url_logo_col)
            st.markdown(f'''
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.3em;min-width:120px;">
    <img src="{logo_url}" width="70" style="display:block;margin:0 auto 0.2em auto;" />
    <div style="text-align:center; font-size:0.95em; color:#555; font-weight:500;">{row[LABEL_ENTREPRISES]}</div>
</div>
''', unsafe_allow_html=True)

def _render_multiple_logos(logos, url_logo_col):
    n_logos = len(logos)
    n_cols = min(6, n_logos)
    cols = st.columns(n_cols)
    for i, (_, row) in enumerate(logos.iterrows()):
        with cols[i % n_cols]:
            logo_url = _get_logo_url(row, url_logo_col)
            st.markdown(f'''
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.3em;width:100%;">
    <img src="{logo_url}" width="70" style="display:block;margin:0 auto 0.2em auto;" />
    <div style="text-align:center; font-size:0.95em; color:#555; font-weight:500;">{row[LABEL_ENTREPRISES]}</div>
</div>
''', unsafe_allow_html=True)


def show_frise(df_ent, selected_entreprises=None):
    """Affiche la frise chronologique des années de création des entreprises, filtrée si besoin."""
    def _show_frise(df_ent, selected_entreprises=None):
        st.markdown(f"<div style='text-align:center; font-size:1.15em; color:{COLOR_COST_TOTAL}; font-weight:600; margin-bottom:0.2em;'>{TITRE_FRISE}</div>", unsafe_allow_html=True)
        if df_ent is not None and LABEL_ANNEE_FONDATION in df_ent.columns and LABEL_ENTREPRISES in df_ent.columns:
            df_annee = df_ent[[LABEL_ENTREPRISES, LABEL_ANNEE_FONDATION]].dropna()
            if selected_entreprises is not None:
                df_annee = df_annee[df_annee[LABEL_ENTREPRISES].isin(selected_entreprises)]
            df_annee = df_annee[pd.to_numeric(df_annee[LABEL_ANNEE_FONDATION], errors="coerce").notna()]
            df_annee[LABEL_ANNEE_FONDATION] = pd.to_numeric(df_annee[LABEL_ANNEE_FONDATION], errors="coerce")
            if not df_annee.empty:
                import plotly.graph_objects as go
                couleurs = px.colors.qualitative.Plotly
                fig = go.Figure()
                for i, row in df_annee.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row[LABEL_ANNEE_FONDATION]],
                        y=[0],
                        mode="markers+text",
                        marker=dict(size=28, color=couleurs[i%len(couleurs)], opacity=0.9, line=dict(width=2, color="#fff")),
                        text=[row[LABEL_ENTREPRISES]],
                        textposition="top center",
                        name=str(row[LABEL_ENTREPRISES])
                    ))
                fig.add_shape(type="line", x0=df_annee[LABEL_ANNEE_FONDATION].min()-1, x1=df_annee[LABEL_ANNEE_FONDATION].max()+1, y0=0, y1=0,
                              line=dict(color="#bbb", width=3), layer="below")
                fig.update_layout(
                    xaxis_title=LABEL_ANNEE_CREATION,
                    yaxis_title="",
                    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, fixedrange=True),
                    xaxis=dict(showgrid=False),
                    margin=PLOTLY_MARGIN,
                    plot_bgcolor=PLOTLY_BG,
                    showlegend=False,
                    height=PLOTLY_HEIGHT
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée d'année de création exploitable.")
        else:
            st.info(f"Colonne '{LABEL_ANNEE_FONDATION}' ou '{LABEL_ENTREPRISES}' non trouvée dans la feuille Entreprise.")
    # Appel avec sélection
    _show_frise(df_ent, selected_entreprises)


def show_analyses(df_comp, df_sol, selected_entreprises=None):
    """
    Affiche la partie analytique principale : sidebar, sélection, couleurs, classement, répartition, coûts.
    """
    if df_comp is None:
        st.error("La feuille 'Comparatif' est introuvable dans le fichier Excel.")
        return

    # Utiliser strictement la sélection globale passée en paramètre
    if selected_entreprises is None or not selected_entreprises:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    entreprises = selected_entreprises
    color_map = get_color_map(entreprises, entreprises)
    df = clean_and_convert_df(df_comp, entreprises)

    st.markdown("---")
    show_classement_repartition(df, entreprises, color_map)

    if df_sol is not None and LABEL_ENTREPRISES in df_sol.columns:
        df_sol_filtered = df_sol[df_sol[LABEL_ENTREPRISES].isin(entreprises)]
    else:
        df_sol_filtered = df_sol
    show_costs(df_sol_filtered)

def get_color_map(selected, entreprises):
    st.sidebar.markdown("### Couleurs par entreprise")
    color_map = {}
    for ent in selected:
        KEY_COLOR = f"color_{ent}"
        raw_col = cookies.get(KEY_COLOR)
        default_col = raw_col if raw_col else COLOR_DEFAULT
        col = st.sidebar.color_picker(ent, default_col, key=KEY_COLOR)
        color_map[ent] = col
        cookies[KEY_COLOR] = col
    valid_keys = {f"color_{e}" for e in entreprises}
    for k in list(cookies.keys()):
        if k.startswith("color_") and k not in valid_keys:
            del cookies[k]
    raw_hist = cookies.get(KEY_HIST_COLOR)
    default_hist = raw_hist if raw_hist else COLOR_DEFAULT
    hist_color = st.sidebar.color_picker(LABEL_HIST_COLOR, default_hist, key=KEY_HIST_COLOR)
    cookies[KEY_HIST_COLOR] = hist_color
    return color_map

def clean_and_convert_df(df_comp, selected):
    df = df_comp.copy()
    df = df[[*COLS_DESCRIPTION, *selected] if COLS_DESCRIPTION else selected]
    for col in selected:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def show_classement_repartition(df, selected, color_map):
    """Affiche le classement et la répartition des scores côte à côte."""
    # La ligne horizontale est désormais gérée par la fonction appelante (show_analyses)
    col_left, col_right = st.columns(2, gap="medium")
    # Classement à gauche
    classement = []
    for col in selected:
        col_data = pd.to_numeric(df[col], errors="coerce")
        score = col_data.sum()
        classement.append({LABEL_ENTREPRISES: col, SCORE_GLOBAL: score})
    df_classement = pd.DataFrame(classement).sort_values(SCORE_GLOBAL, ascending=False)
    fig_class = px.bar(
        df_classement,
        x=LABEL_ENTREPRISES,
        y=SCORE_GLOBAL,
        color=LABEL_ENTREPRISES,
        color_discrete_map=color_map,
        template=PLOTLY_TEMPLATE,
        labels={SCORE_GLOBAL: SCORE_GLOBAL, LABEL_ENTREPRISES: LABEL_ENTREPRISES}
    )
    fig_class.update_layout(margin=PLOTLY_MARGIN, xaxis_title=LABEL_ENTREPRISES, yaxis_title=SCORE_GLOBAL)
    # Répartition à droite
    repartition = []
    for col in selected:
        col_data = pd.to_numeric(df[col], errors="coerce")
        count_1 = (col_data == 1).sum()
        count_0 = (col_data == 0).sum()
        repartition.append({LABEL_ENTREPRISES: col, LABEL_RESPECTE: count_1, LABEL_NON_RESPECTE: count_0})
    rep_df = pd.DataFrame(repartition)
    rep_df = rep_df.set_index(LABEL_ENTREPRISES)
    fig_rep = px.bar(
        rep_df,
        x=rep_df.index,
        y=[LABEL_RESPECTE, LABEL_NON_RESPECTE],
        barmode="group",
        color_discrete_map={LABEL_RESPECTE: COLOR_REP_OK, LABEL_NON_RESPECTE: COLOR_REP_NOK},
        template=PLOTLY_TEMPLATE,
        labels={"value": LABEL_NB_CRITERES, "variable": LABEL_STATUT, LABEL_ENTREPRISES: LABEL_ENTREPRISES}
    )
    fig_rep.update_layout(margin=PLOTLY_MARGIN, xaxis_title=LABEL_ENTREPRISES, yaxis_title=LABEL_NB_CRITERES)
    with col_left:
        st.markdown(f"<div style='text-align:center; font-size:1.08em; color:{COLOR_COST_TOTAL}; font-weight:600; margin-bottom:0.2em;'>{TITRE_CLASSEMENT}</div>", unsafe_allow_html=True)
        st.plotly_chart(fig_class, use_container_width=True, key=KEY_PLOTLY_CLASS)
    with col_right:
        st.markdown(f"<div style='text-align:center; font-size:1.08em; color:{COLOR_COST_TOTAL}; font-weight:600; margin-bottom:0.2em;'>{TITRE_REPARTITION}</div>", unsafe_allow_html=True)
        st.plotly_chart(fig_rep, use_container_width=True, key=KEY_PLOTLY_REP)


def show_costs(df_sol):
    """Affiche le comparatif prévisionnel des coûts par entreprise."""
    st.markdown("---")
    st.markdown(f"<div style='text-align:center; font-size:1.08em; color:{COLOR_COST_TOTAL}; font-weight:600; margin-bottom:0.2em;'>{TITRE_COST}</div>", unsafe_allow_html=True)
    if _show_costs_info_if_missing(df_sol):
        return

    col_init, col_rec, col_ent = _find_cost_columns(df_sol)
    if _show_costs_info_if_invalid_columns(col_init, col_rec, col_ent):
        return

    mois = _show_costs_sidebar_slider()
    df_plot = _prepare_cost_dataframe(df_sol, col_ent, col_init, col_rec, mois)
    if _show_costs_info_if_no_data(df_plot):
        return

    fig = _build_cost_bar_chart(df_plot)
    st.plotly_chart(fig, use_container_width=True, key=KEY_PLOTLY_COST)

def _show_costs_info_if_missing(df_sol):
    if df_sol is None:
        st.info("La feuille Solution n'est pas disponible dans le fichier Excel.")
        return True
    return False

def _show_costs_info_if_invalid_columns(col_init, col_rec, col_ent):
    if not (col_init and col_rec and col_ent):
        st.info("Colonnes 'Entreprises', 'Coûts initiaux' et/ou 'Coûts récurrents' non trouvées dans la feuille Solution.")
        return True
    return False

def _show_costs_sidebar_slider():
    with st.sidebar:
        mois = st.slider("Nombre de mois pour la prévision", min_value=1, max_value=120, value=12, key=KEY_SLIDER_MOIS)
    return mois

def _show_costs_info_if_no_data(df_plot):
    if df_plot is None or df_plot.empty:
        st.info("Aucune donnée de coût exploitable pour le comparatif.")
        return True
    return False


def _find_cost_columns(df_sol):
    import unicodedata
    def normalize_colname(name):
        nfkd = unicodedata.normalize('NFKD', str(name))
        return ''.join([c for c in nfkd if not unicodedata.combining(c)]).replace(' ', '').lower()
    col_init = col_rec = col_ent = None
    for col in df_sol.columns:
        norm = normalize_colname(col)
        if norm == "coutsinitiaux":
            col_init = col
        if norm == "coutsrecurrents":
            col_rec = col
        if "entreprise" in norm:
            col_ent = col
    return col_init, col_rec, col_ent


def _extract_amount(val):
    import re
    import pandas as pd
    if pd.isna(val):
        return None
    match = re.search(r"([\d\s]+[\d])", str(val).replace(" ", " "))
    if match:
        montant = match.group(1)
        montant = montant.replace(" ", "")
        try:
            return float(montant)
        except Exception:
            return None
    return None


def _extract_recurring(row, col_rec):
    import pandas as pd
    val = row[col_rec]
    raw = str(val).lower() if not pd.isna(val) else ""
    montant = _extract_amount(val)
    if montant is None:
        return None
    if "an" in raw or "année" in raw:
        return montant / 12
    return montant


def _prepare_cost_dataframe(df_sol, col_ent, col_init, col_rec, mois):
    import pandas as pd
    if any(col is None for col in [col_ent, col_init, col_rec]):
        return None
    df_plot = pd.DataFrame({
        LABEL_ENTREPRISES: df_sol[col_ent],
        LABEL_COUT_INIT: df_sol[col_init].apply(_extract_amount),
        LABEL_COUT_REC: df_sol.apply(lambda row: _extract_recurring(row, col_rec), axis=1)
    })
    df_plot[LABEL_COUT_TOTAL] = df_plot[LABEL_COUT_INIT].fillna(0) + df_plot[LABEL_COUT_REC].fillna(0) * mois
    df_plot = df_plot.dropna(subset=[LABEL_ENTREPRISES], how="any")
    df_agg = df_plot.groupby(LABEL_ENTREPRISES).agg({
        LABEL_COUT_INIT: "sum",
        LABEL_COUT_REC: "sum",
        LABEL_COUT_TOTAL: "sum"
    }).reset_index()
    for col in [LABEL_COUT_INIT, LABEL_COUT_REC, LABEL_COUT_TOTAL]:
        df_agg[col] = pd.to_numeric(df_agg[col], errors="coerce")
    return df_agg if not df_agg.empty else None


def _build_cost_bar_chart(df_agg):
    import plotly.express as px
    fig = px.bar(
        df_agg,
        x=LABEL_ENTREPRISES,
        y=[LABEL_COUT_INIT, LABEL_COUT_REC, LABEL_COUT_TOTAL],
        barmode="group",
        color_discrete_map={
            LABEL_COUT_INIT: COLOR_COST_INIT,
            LABEL_COUT_REC: COLOR_COST_REC,
            LABEL_COUT_TOTAL: COLOR_COST_TOTAL
        },
        template=PLOTLY_TEMPLATE,
        labels={"value": LABEL_MONTANT, "variable": LABEL_TYPE_COUT, LABEL_ENTREPRISES: LABEL_ENTREPRISES}
    )
    fig.update_layout(
        xaxis_title=LABEL_ENTREPRISES,
        yaxis_title="Montant prévisionnel (€ ou $)",
        margin=PLOTLY_MARGIN
    )
    return fig