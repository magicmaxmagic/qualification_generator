import streamlit as st
import plotly.express as px
import pandas as pd

def display(df_comp):
    st.title("Rapport de Qualification – Vue d'ensemble")

    st.sidebar.markdown("## Filtres")
    entreprises = df_comp["Entreprises"].dropna().unique().tolist()
    selected_entreprises = st.sidebar.multiselect("Entreprises à inclure", entreprises, default=entreprises)

    df_filtered = df_comp[df_comp["Entreprises"].isin(selected_entreprises)]

    if df_filtered.empty:
        st.warning("Aucune donnée à afficher avec les filtres sélectionnés.")
        return

    st.subheader("Top 3 entreprises (Score global)")
    top3 = df_filtered.sort_values("Score Golbal", ascending=False).head(3)
    st.dataframe(top3[["Entreprises", "Score Golbal"]], use_container_width=True)

    st.subheader("Distribution des scores")
    fig = px.histogram(df_filtered, x="Score Golbal", nbins=10, template="simple_white")
    fig.update_layout(title_text="Répartition des scores globaux", title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)