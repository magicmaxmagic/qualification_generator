import streamlit as st
import plotly.express as px
import pandas as pd
import pydeck as pdk
from sidebar import show_sidebar
from geopy.geocoders import Nominatim

@st.cache_data(show_spinner=False)
def geocode(location):
    try:
        geolocator = Nominatim(user_agent="entreprise_app")
        loc = geolocator.geocode(location)
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except:
        return None, None

def display(df_comp, df_ent):
    st.title("Fiche entreprise")

    entreprises = df_comp["Entreprises"].dropna().unique().tolist()
    selected = show_sidebar("Choisissez une entreprise", entreprises, default=entreprises[:1], multiselect=False)

    if not selected:
        st.info("Veuillez sélectionner une entreprise.")
        return

    entreprise = selected[0]
    row = df_comp[df_comp["Entreprises"] == entreprise].iloc[0]
    info = df_ent[df_ent["Entreprises"] == entreprise].iloc[0]

    # --- En-tête centré : nom + logo ---
    image_url = info.get("URL", "")
    logo_html = f"<img src='{image_url}' width='150' style='margin: 0 auto; display: block;'/>" if isinstance(image_url, str) and image_url.startswith("http") else "<div style='padding:30px;text-align:center;border-radius:10px;background:#f0f0f0;'>Logo non disponible</div>"

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:40px;">
            <h2 style="margin-bottom:20px;">{entreprise}</h2>
            {logo_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Description ---
    st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
    st.markdown("### Description")
    description = info.get("Description", "").strip() or "Aucune description disponible."
    st.markdown(
        f"<div style='background-color:#f9f9f9;padding:15px;border-left:5px solid #3e8e7e;border-radius:5px;color:#333;'>"
        f"{description}</div>",
        unsafe_allow_html=True
    )

    # --- Attributs à afficher ---
    st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
    st.markdown("### Informations générales")
    attributs_disponibles = [
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

    st.sidebar.markdown("### Informations à afficher")
    selected_infos = st.sidebar.multiselect(
        "Champs visibles dans le tableau :",
        options=attributs_disponibles,
        default=[
            "Localisation (Siège social)",
            "Année de fondation",
            "Nombre d'employés",
            "Score Global"
        ]
    )

    infos = []
    for label in selected_infos:
        val = info.get(label, row.get(label, "N/A"))
        if pd.isna(val):
            val = "N/A"
        elif label == "Année de fondation" and isinstance(val, float):
            val = str(int(val))
        else:
            val = str(val)
        infos.append((label, val))

    df_infos = pd.DataFrame(infos, columns=["Attribut", "Valeur"])
    st.dataframe(df_infos, hide_index=True, use_container_width=True)

    # --- Radar ---
    st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
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
        line_close=True,
        range_r=[0, 5],
        template="simple_white"
    )
    fig.update_traces(fill='toself')
    fig.update_layout(
        height=500,
        margin=dict(t=30, b=30),
        polar=dict(radialaxis=dict(visible=True, range=[0, 5]))
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Carte de localisation ---
    st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
    st.markdown("### Localisation sur la carte")
    loc_text = info.get("Localisation (Siège social)", "")
    lat, lon = geocode(loc_text)

    if lat and lon:
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=10,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=pd.DataFrame({'lat': [lat], 'lon': [lon]}),
                    get_position='[lon, lat]',
                    get_radius=200,
                    get_color=[60, 179, 113],
                    pickable=True,
                ),
            ],
        ))
    else:
        st.info("Localisation non trouvée ou adresse invalide.")