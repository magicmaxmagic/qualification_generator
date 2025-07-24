import streamlit as st
import plotly.express as px
import pandas as pd
from sidebar import show_sidebar, cookies
import json
import pandas as pd
import pydeck as pdk
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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
LABEL_COUT_INIT = "Coûts initiaux"
LABEL_COUT_REC = "Coûts récurrents (année)"
LABEL_COUT_TOTAL = "Coût total prévisionnel"
LABEL_RESPECTE = "Respecté"
LABEL_NON_RESPECTE = "Non respecté"
LABEL_STATUT = "Statut"
LABEL_NB_CRITERES = "Nombre de critères"
LABEL_TYPE_COUT = "Type de coût"
LABEL_MONTANT = "Montant ($)"
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

TITRE_HEADER = "Qualification"
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
    # Barre horizontale entre le header et la section logos
    st.markdown("---")
    # On déplace la sélection d'entreprises AVANT l'affichage des logos
    # Liste cohérente des entreprises présentes dans toutes les feuilles
    available_entreprises = get_available_entreprises(df_ent, df_sol, df_comp)
    # Uniformisation pour la sélection
    def norm(x):
        return x.strip().lower() if isinstance(x, str) else x
    norm_map = {norm(e): e for e in available_entreprises}
    norm_options = list(norm_map.keys())
    # Sélectionne tout par défaut
    selected_norm = show_sidebar(
        label=LABEL_ENTREPRISES,
        options=norm_options,
        default=norm_options,
        multiselect=True
    ) if norm_options else []
    # Remonte les valeurs originales pour le reste du dashboard
    selected_entreprises = [norm_map[n] for n in selected_norm]
    # Suppression complète : aucune fonction de résumé n'est appelée
    show_logos(df_ent, selected_entreprises)
    show_costs(df_sol)
    show_global_map(df_ent)

def show_global_map(df_ent):
    
    st.markdown("---")
    st.markdown(f"<div style='text-align:center; font-size:1.08em; color:{COLOR_COST_TOTAL}; font-weight:600; margin-bottom:0.2em;'>Carte des entreprises</div>", unsafe_allow_html=True)
    if df_ent is None or df_ent.empty:
        st.info("Aucune donnée d'entreprise disponible pour la carte.")
        return
    # Recherche des colonnes latitude/longitude
    lat_col = None
    lon_col = None
    for col in df_ent.columns:
        if col.lower() in ["latitude", "lat"]:
            lat_col = col
        if col.lower() in ["longitude", "lon", "lng"]:
            lon_col = col
    if lat_col and lon_col:
        df_map = df_ent[[LABEL_ENTREPRISES, lat_col, lon_col]].dropna(subset=[lat_col, lon_col])
        df_map = df_map.rename(columns={lat_col: "lat", lon_col: "lon"})
        colors = [
            [0, 114, 178, 200], [220, 53, 69, 200], [40, 167, 69, 200], [255, 193, 7, 200],
            [108, 117, 125, 200], [111, 66, 193, 200], [255, 87, 51, 200], [23, 162, 184, 200],
        ]
        df_map['color'] = [colors[i % len(colors)] for i in range(len(df_map))]
        layer = pdk.Layer(
            'ScatterplotLayer',
            df_map,
            get_position='[lon,lat]',
            get_radius=8000,
            get_fill_color='color',
            pickable=True
        )
        center_lat = df_map['lat'].iloc[0]
        center_lon = df_map['lon'].iloc[0]
        view = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=7)
        deck = pdk.Deck(
            initial_view_state=view,
            layers=[layer],
            tooltip={
                "html": "<b>📍 {name}</b><br/><b>Coordonnées:</b> {lat:.4f}, {lon:.4f}",
                "style": {"backgroundColor": "rgba(255, 255, 255, 0.95)", "color": "black", "padding": "10px", "borderRadius": "8px", "boxShadow": "0 4px 16px rgba(0,0,0,0.2)"}
            },
        )
        st.pydeck_chart(deck, use_container_width=True)
    else:        
        # Utilisation des colonnes de localisation personnalisées
        loc_cols = [col for col in df_ent.columns if col.strip().lower() in ["localisation (siège social)", "localisation (québec)"]]
        if loc_cols:
            geolocator = Nominatim(user_agent="iveo_map")
            geocode = RateLimiter(lambda x: geolocator.geocode(x, timeout=10), min_delay_seconds=1, max_retries=2, error_wait_seconds=2.0, swallow_exceptions=False)
            # Fusionner les deux colonnes en une seule série de localisation, en ignorant les valeurs vides
            df_map = df_ent[[LABEL_ENTREPRISES] + loc_cols].copy()
            df_map['localisation'] = df_map[loc_cols].bfill(axis=1).iloc[:, 0]
            df_map = df_map.dropna(subset=['localisation'])
            import geopy.exc
            def safe_geocode(x):
                try:
                    return geocode(str(x))
                except (geopy.exc.GeocoderUnavailable, geopy.exc.GeocoderTimedOut, geopy.exc.GeocoderServiceError, Exception):
                    return None
            df_map['location'] = df_map['localisation'].apply(safe_geocode)
            df_map = df_map[df_map['location'].notnull()]
            df_map['lat'] = df_map['location'].apply(lambda loc: loc.latitude if loc else None)
            df_map['lon'] = df_map['location'].apply(lambda loc: loc.longitude if loc else None)
            df_map = df_map.dropna(subset=['lat', 'lon'])
            # Supprimer la colonne 'location' avant d'afficher la carte (pydeck ne supporte pas les objets)
            if 'location' in df_map.columns:
                df_map = df_map.drop(columns=['location'])
            if not df_map.empty:
                # Regrouper les entreprises par coordonnées
                df_grouped = df_map.groupby(['lat', 'lon']).agg({
                    LABEL_ENTREPRISES: lambda x: list(x),
                }).reset_index()
                df_grouped['count'] = df_grouped[LABEL_ENTREPRISES].apply(len)
                df_grouped['name'] = df_grouped[LABEL_ENTREPRISES].apply(lambda x: ', '.join(x))
                colors = [
                    [0, 114, 178, 200], [220, 53, 69, 200], [40, 167, 69, 200], [255, 193, 7, 200],
                    [108, 117, 125, 200], [111, 66, 193, 200], [255, 87, 51, 200], [23, 162, 184, 200],
                ]
                df_grouped['color'] = [colors[i % len(colors)] for i in range(len(df_grouped))]
                # Rayon plus grand pour visibilité mondiale
                base_radius = 40000
                df_grouped['radius'] = base_radius + (df_grouped['count'] - 1) * 20000
                # Affichage du nombre si plusieurs entreprises
                df_grouped['label'] = df_grouped.apply(lambda row: f"+{row['count']}" if row['count'] > 1 else '', axis=1)
                scatter_layer = pdk.Layer(
                    'ScatterplotLayer',
                    df_grouped,
                    get_position='[lon,lat]',
                    get_radius='radius',
                    get_fill_color='color',
                    pickable=True,
                    auto_highlight=True
                )
                text_layer = pdk.Layer(
                    'TextLayer',
                    df_grouped[df_grouped['label'] != ''],
                    get_position='[lon,lat]',
                    get_text='label',
                    get_color=[0,0,0,255],
                    get_size=32,
                    get_alignment_baseline="bottom"
                )
                center_lat = df_grouped['lat'].iloc[0]
                center_lon = df_grouped['lon'].iloc[0]
                view = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=2)
                deck = pdk.Deck(
                    initial_view_state=view,
                    layers=[scatter_layer, text_layer],
                    tooltip={
                        "html": "<b>📍 {name}</b><br/><b>Coordonnées:</b> {lat:.4f}, {lon:.4f}",
                        "style": {"backgroundColor": "rgba(255, 255, 255, 0.95)", "color": "black", "padding": "10px", "borderRadius": "8px", "boxShadow": "0 4px 16px rgba(0,0,0,0.2)"}
                    },
                )
                st.pydeck_chart(deck, use_container_width=True)
            else:
                st.info("Impossible de géocoder les localisations (service indisponible ou timeout). Les points non géocodés sont ignorés.")
        else:
            st.info("Aucune colonne de localisation trouvée dans les données entreprises. La carte ne peut pas être affichée.")
    # Toutes les analyses doivent utiliser la même sélection globale !
    #show_frise(df_ent, selected_entreprises)
    # show_analyses(df_comp, df_sol, selected_entreprises)

def show_bandeau_summary(df_ent, df_sol, df_comp, selected_entreprises=None):
    # Bandeau totalement supprimé, ne rien afficher ni exécuter
    return

def get_available_entreprises(df_ent=None, df_sol=None, df_comp=None):
    # Retourne toutes les entreprises de la feuille Entreprise
    if df_ent is not None and LABEL_ENTREPRISES in df_ent.columns:
        # Debug: afficher toutes les valeurs pour analyse
        pass
        entreprises = df_ent[LABEL_ENTREPRISES].astype(str)
        entreprises = entreprises[entreprises.str.lower() != 'nan']
        entreprises = entreprises[entreprises.str.strip() != '']
        entreprises = entreprises.str.strip()
        entreprises = entreprises.drop_duplicates()
        return sorted(list(entreprises))
    return []

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
    # Bandeau totalement supprimé, ne rien afficher ni exécuter
    return

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
    # Bandeau totalement supprimé, ne rien afficher ni exécuter
    return


def _get_logo_url(row, url_logo_col):
    """Helper to get logo URL from a row, fallback to default if missing."""
    if url_logo_col and url_logo_col in row and pd.notna(row[url_logo_col]) and str(row[url_logo_col]).strip():
        return row[url_logo_col]
    return IMG_ENTREPRISE

def show_logos(df_ent, selected_entreprises=None):
    def _find_url_logo_col(cols):
        import unicodedata
        def normalize(s):
            return ''.join([c for c in unicodedata.normalize('NFKD', str(s)) if not unicodedata.combining(c)]).replace(' ', '').lower()
        for col in cols:
            if normalize(col) in [normalize('URL (logo)'), 'urllogo', 'logo', 'url_logo', 'url', 'logourl']:
                return col
        return None

    def _render_single_logo(row, url_logo_col):
        st.markdown('<div style="display:flex;justify-content:center;">', unsafe_allow_html=True)
        logo_url = _get_logo_url(row, url_logo_col)
        st.markdown(f"""
<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.3em;min-width:120px;'>
    <img src='{logo_url}' width='70' style='display:block;margin:0 auto 0.2em auto;' />
    <div style='text-align:center; font-size:0.95em; color:#555; font-weight:500;'>{row[LABEL_ENTREPRISES]}</div>
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def _render_two_logos(logos, url_logo_col):
        cols = st.columns(2)
        for i, (_, row) in enumerate(logos.iterrows()):
            with cols[i]:
                logo_url = _get_logo_url(row, url_logo_col)
                st.markdown(f"""
<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.3em;min-width:120px;'>
    <img src='{logo_url}' width='70' style='display:block;margin:0 auto 0.2em auto;' />
    <div style='text-align:center; font-size:0.95em; color:#555; font-weight:500;'>{row[LABEL_ENTREPRISES]}</div>
</div>
""", unsafe_allow_html=True)
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

    n_logos = len(logos)
    if n_logos == 1:
        _render_single_logo(logos.iloc[0], url_logo_col)
    elif n_logos == 2:
        _render_two_logos(logos, url_logo_col)
    elif n_logos > 2:
        _render_multiple_logos(logos, url_logo_col)

def _render_multiple_logos(logos, url_logo_col):

    n_logos = len(logos)
    n_cols = 5
    start = 0
    while start < n_logos:
        row_logos = logos.iloc[start:start+3]
        num_in_row = len(row_logos)
        cols = st.columns(n_cols)
        # Placement des colonnes selon le nombre de logos dans la ligne
        if num_in_row == 1:
            positions = [2]
        elif num_in_row == 2:
            positions = [1,3]
        else:
            positions = [0,2,4]
        for i in range(n_cols):
            if i not in positions:
                with cols[i]:
                    st.markdown("<div></div>", unsafe_allow_html=True)
        for idx, (_, row) in enumerate(row_logos.iterrows()):
            col_pos = positions[idx]
            with cols[col_pos]:
                logo_url = _get_logo_url(row, url_logo_col)
                st.markdown(f"""
<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.3em;width:100%;'>
    <img src='{logo_url}' width='70' style='display:block;margin:0 auto 0.2em auto;' />
    <div style='text-align:center; font-size:0.95em; color:#555; font-weight:500;'>{row[LABEL_ENTREPRISES]}</div>
</div>
""", unsafe_allow_html=True)
        start += 3

    n_logos = len(logos)
    n_cols = 5
    if n_logos == 4:
        # Ligne 1 : colonnes 0,2,4 (logos 1,2,3)
        cols = st.columns(n_cols)
        for i in range(n_cols):
            if i not in [0,2,4]:
                with cols[i]:
                    st.markdown("<div></div>", unsafe_allow_html=True)
        for idx in range(3):
            with cols[[0,2,4][idx]]:
                logo_url = _get_logo_url(logos.iloc[idx], url_logo_col)
                
    # Suppression du rendu du graphique ici, cette fonction ne doit afficher que les logos



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
    montant = _extract_amount(val)
    if montant is None:
        return None
    # Les coûts récurrents sont déjà annuels, aucune conversion
    return montant


def _prepare_cost_dataframe(df_sol, col_ent, col_init, col_rec, mois):
    import pandas as pd
    if any(col is None for col in [col_ent, col_init, col_rec]):
        return None
    df_plot = pd.DataFrame({
        "Solution": df_sol[col_ent],
        LABEL_COUT_INIT: df_sol[col_init].apply(_extract_amount),
        LABEL_COUT_REC: df_sol.apply(lambda row: _extract_recurring(row, col_rec), axis=1)
    })
    # Les coûts récurrents sont annuels, donc on les ramène au mois puis on multiplie par le nombre de mois
    df_plot[LABEL_COUT_REC] = df_plot[LABEL_COUT_REC].fillna(0) / 12 * mois
    # Coût total = coût initial + coût récurrent (sur la période)
    df_plot[LABEL_COUT_TOTAL] = df_plot[LABEL_COUT_INIT].fillna(0) + df_plot[LABEL_COUT_REC]
    df_plot = df_plot.dropna(subset=["Solution"], how="any")
    df_agg = df_plot.groupby("Solution").agg({
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
        x="Solution",
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
        xaxis_title="Solution",
        yaxis_title="Montant prévisionnel (€ ou $)",
        margin=PLOTLY_MARGIN
    )
    return fig

def show_costs(df_sol):
    # Affiche le comparatif prévisionnel des coûts par entreprise.
    st.markdown("---")
    st.markdown(f"<div style='text-align:center; font-size:1.08em; color:{COLOR_COST_TOTAL}; font-weight:600; margin-bottom:0.2em;'>{TITRE_COST}</div>", unsafe_allow_html=True)
    if _show_costs_info_if_missing(df_sol):
        return
    col_init, col_rec, col_sol = _find_cost_columns(df_sol)
    if _show_costs_info_if_invalid_columns(col_init, col_rec, col_sol):
        return
    mois = _show_costs_sidebar_slider()
    df_plot = _prepare_cost_dataframe(df_sol, col_sol, col_init, col_rec, mois)
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
        st.info("Colonnes 'Nom de la solution', 'Coûts initiaux' et/ou 'Coûts récurrents' non trouvées dans la feuille Solution.")
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
        return ''.join([c for c in nfkd if not unicodedata.combining(c)]).replace(' ', '').replace("(","").replace(")","").replace("-","").replace("'","").lower()

    col_sol = None
    # Priorité absolue : colonne strictement 'Nom de la solution'
    for col in df_sol.columns:
        if normalize_colname(col) == "nomdelasolution":
            col_sol = col
            break
    # Priorité 1 : colonne contenant à la fois 'nom' et 'solution'
    if not col_sol:
        for col in df_sol.columns:
            norm = normalize_colname(col)
            if "nom" in norm and "solution" in norm:
                col_sol = col
                break
    # Priorité 2 : colonne contenant 'solution' seule si rien trouvé
    if not col_sol:
        for col in df_sol.columns:
            norm = normalize_colname(col)
            if "solution" in norm:
                col_sol = col
                break

    col_init = col_rec = col_ent = None
    init_variants = ["initial", "initiaux", "initiale", "initiales"]
    rec_variants = ["recurrent", "recurrents", "recurent", "recurents", "récurrent", "récurrents", "récurrente", "récurrentes", "annee", "année", "an"]
    for col in df_sol.columns:
        norm = normalize_colname(col)
        # Recherche plus souple pour les coûts initiaux
        if col_init is None and "cout" in norm and any(v in norm for v in init_variants):
            col_init = col
        # Recherche plus souple pour les coûts récurrents, accepte fautes et variantes
        if col_rec is None and "cout" in norm and any(v in norm for v in rec_variants):
            col_rec = col
        # Recherche universelle pour entreprise
        if col_ent is None and "entreprise" in norm:
            col_ent = col
    return col_init, col_rec, col_sol