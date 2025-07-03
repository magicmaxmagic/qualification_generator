import streamlit as st
import plotly.express as px
import pandas as pd

def display(df_comp, df_ent):
    st.title("Fiche entreprise")

    entreprises = df_comp["Entreprises"].dropna().unique().tolist()
    entreprise = st.sidebar.selectbox("Choisissez une entreprise", entreprises)

    row = df_comp[df_comp["Entreprises"] == entreprise].iloc[0]
    info = df_ent[df_ent["Entreprises"] == entreprise].iloc[0]

    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        st.markdown(f"## {entreprise}")
        st.markdown(f"**Localisation** : {info.get('Localisation (Siège social)', 'N/A')}")
        st.markdown(f"**Année de fondation** : {int(info['Année de fondation']) if not pd.isna(info['Année de fondation']) else 'N/A'}")
        st.markdown(f"**Score global** : {row.get('Score Golbal', 'N/A')}/5")

        image_url = info.get("URL", "")
        if isinstance(image_url, str) and image_url.startswith("http"):
            st.image(image_url, use_container_width=True, caption="Logo / image")

        st.markdown("**Description** :")
        st.markdown(info.get("Description", "N/A"))

    with col2:
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
            template="simple_white",
        )
        fig.update_layout(title_text="Évaluation par critère", title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

