import streamlit as st
import plotly.express as px
import pandas as pd

def display(df_comp, df_ent):
    st.title("Fiche entreprise")

    entreprise = st.selectbox("Choisissez une entreprise", df_comp["Entreprises"].unique())
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
            title="Évaluation par critère",
        )
        fig.update_traces(fill='toself', line=dict(color="#1f8a70", width=3))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], showline=False, gridcolor="#e0e0e0"),
                angularaxis=dict(tickfont=dict(size=12))
            ),
            title_x=0.5,
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(size=14)
        )
        st.plotly_chart(fig, use_container_width=True)

