# app/pages/entreprise.py

import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import json
from geopy.geocoders import Nominatim
from sidebar import cookies, show_sidebar, show_sidebar_alignement

# --- Memoize la géocodification pour ne pas re-appeler Nominatim
@st.cache_data(show_spinner=False)
def geocode(location: str):
    try:
        geolocator = Nominatim(user_agent="entreprise_app")
        loc = geolocator.geocode(location)
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except:
        return None, None


def display(df_comp: pd.DataFrame, df_ent: pd.DataFrame):
    st.title("Fiche entreprise")

    # 1) Sélection persistée de l'entreprise
    entreprises = df_comp["Entreprises"].dropna().unique().tolist()
    raw_sel = cookies.get("choisissez_une_entreprise_selected")
    prev_sel = json.loads(raw_sel) if raw_sel else [entreprises[0]]
    selected = st.sidebar.selectbox(
        "Choisissez une entreprise",
        options=entreprises,
        index=entreprises.index(prev_sel[0]) if prev_sel[0] in entreprises else 0
    )
    cookies["choisissez_une_entreprise_selected"] = json.dumps([selected])

    # 2) Valider la sélection
    if not selected:
        st.info("Veuillez sélectionner une entreprise.")
        return
    entreprise = selected

    # 3) Récupérer données
    row = df_comp[df_comp["Entreprises"] == entreprise].iloc[0]
    info = df_ent[df_ent["Entreprises"] == entreprise].iloc[0]

    # 4) En-tête centré avec logo
    image_url = info.get("URL", "")
    if isinstance(image_url, str) and image_url.startswith("http"):
        logo_html = f"<img src='{image_url}' width='150' style='margin:0 auto; display:block'/>"
    else:
        logo_html = "<div style='padding:30px;text-align:center;border:1px solid #ddd;border-radius:8px;'>Logo non disponible</div>"
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:2rem;">
          <h2 style="margin-bottom:1rem;">{entreprise}</h2>
          {logo_html}
        </div>
        """, unsafe_allow_html=True
    )

    # 5) Description
    description = info.get("Description", "").strip() or "Aucune description disponible."
    st.markdown("### Description")
    st.markdown(
        f"<div style='background:#f9f9f9;padding:1rem;border-left:4px solid #3e8e7e;border-radius:4px'>{description}</div>",
        unsafe_allow_html=True
    )

    # 6) Choix persistant des champs à afficher
    st.sidebar.markdown("### Informations à afficher")
    attributs = [
      "Localisation (Siège social)",
      "Année de fondation",
      "Nombre d'employés",
      "Score Global",
      "Alignement avec le besoin",
      "Avantage compétitif",
      "Maturité technologie/business",
      "Coût  et avantage économique (achat, fixe, maintenance, etc.)",
      "Expertise de l'équipe",
      "Satisfaction client",
      "Degré d'accompagnement"
    ]
    default_fields = attributs[:4]
    raw_fields = cookies.get("entreprise_fields")
    prev_fields = json.loads(raw_fields) if raw_fields else default_fields
    selected_infos = st.sidebar.multiselect(
      "Champs visibles",
      attributs,
      default=prev_fields
    )
    cookies["entreprise_fields"] = json.dumps(selected_infos)

    # 7) Construire et afficher le tableau
    infos = []
    for label in selected_infos:
        val = info.get(label, row.get(label, "N/A"))
        if pd.isna(val):
            val = "N/A"
        if label == "Année de fondation" and isinstance(val, float):
            val = str(int(val))
        infos.append((label, val))
    df_infos = pd.DataFrame(infos, columns=["Attribut","Valeur"]).astype(str)
    st.markdown("### Informations générales")
    st.dataframe(df_infos, hide_index=True, use_container_width=True)

    # 8) Couleurs par entreprise
    st.sidebar.markdown("### Couleurs par entreprise")
    color_map = {}
    raw_col = cookies.get(f"color_{entreprise}")
    default_col = raw_col if raw_col else "#0072B2"
    col = st.sidebar.color_picker(entreprise, default_col)
    color_map[entreprise] = col
    cookies[f"color_{entreprise}"] = col

    # 9) Couleur de la répartition
    st.sidebar.markdown("### Couleur de la répartition")
    raw_hist = cookies.get("entreprise_hist_color")
    default_hist = raw_hist if raw_hist else "#0072B2"
    hist_color = st.sidebar.color_picker("Histogramme", default_hist)
    cookies["entreprise_hist_color"] = hist_color

    # 10) Sauvegarde des cookies
    cookies.save()

    # --- 11) Radar individuel ---
    st.markdown("### Évaluation par critère")
    radar_data = {
      "Alignement": row.get("Alignement avec les besoins", 0),
      "Compétitif": row.get("Avantage compétitif", 0),
      "Maturité": row.get("Maturité technologie/business", 0),
      "Coût/avantage": row.get("Coût  et avantage économique (achat, fixe, maintenance, etc.)", 0),
      "Satisfaction": row.get("Satisfaction client", 0),
      "Accompagnement": row.get("Degré d'accompagnement", 0)
    }
    fig = px.line_polar(
        r=list(radar_data.values()),
        theta=list(radar_data.keys()),
        line_close=True, range_r=[0,5], template="simple_white"
    )
    fig.update_traces(fill="toself")
    fig.update_layout(height=450, margin=dict(t=30,b=30), polar=dict(radialaxis=dict(visible=True,range=[0,5])))
    st.plotly_chart(fig, use_container_width=True)

    # --- 12) Carte de localisation ---
    st.markdown("### Localisation sur la carte")
    loc = info.get("Localisation (Siège social)", "")
    lat, lon = geocode(loc)
    if lat and lon:
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10, pitch=0),
            layers=[pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame({"lat":[lat],"lon":[lon]}),
                get_position='[lon, lat]', get_radius=200, get_color=[60,179,113]
            )]
        ))
    else:
        st.info("Localisation non trouvée ou adresse invalide.")
