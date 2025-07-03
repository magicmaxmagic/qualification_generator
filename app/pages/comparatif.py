import streamlit as st
import plotly.express as px
import pandas as pd

def display(df_comp):
    st.title("Comparatif global des entreprises")

    # Colonnes utilisées pour les radars
    radar_cols = [
        "Alignement avec les besoins",
        "Avantage compétitif",
        "Maturité technologie/business",
        "Coût  et avantage économique (achat, fixe, maintenance, etc.)",
        "Satisfaction client",
        "Degré d'accompagnement"
    ]

    # Filtrer les entreprises avec données valides sur toutes les colonnes radar
    df_valid = df_comp.dropna(subset=radar_cols, how='any')
    entreprises_disponibles = df_valid["Entreprises"].dropna().unique().tolist()

    # Sidebar : filtre sur les entreprises
    with st.sidebar:
        st.markdown("### Filtrer les entreprises")
        selected_entreprises = st.multiselect(
            "Entreprises à afficher",
            options=entreprises_disponibles,
            default=entreprises_disponibles
        )

    # Filtrage du DataFrame
    df_filtered = df_valid[df_valid["Entreprises"].isin(selected_entreprises)]

    # Multiselect des colonnes à afficher dans le tableau
    selected_cols = st.multiselect(
        "Colonnes à afficher dans le tableau",
        df_filtered.columns.tolist(),
        default=["Entreprises", "Score Golbal", "Alignement avec les besoins"]
    )

    # Affichage du tableau
    st.markdown("### Données comparatives")
    st.dataframe(df_filtered[selected_cols], use_container_width=True)

    # Affichage des radars
    st.markdown("### Graphiques radar")

    for _, row in df_filtered.iterrows():
        entreprise = row["Entreprises"]
        values = [row[c] for c in radar_cols]

        fig = px.line_polar(
            r=values,
            theta=radar_cols,
            line_close=True,
            title=f"{entreprise} – Évaluation",
            range_r=[0, 5]
        )
        fig.update_traces(fill='toself')
        fig.update_layout(
            margin=dict(t=40, b=40),
            polar=dict(bgcolor="white"),
            paper_bgcolor="white",
            title_x=0.5
        )
        st.plotly_chart(fig, use_container_width=True)