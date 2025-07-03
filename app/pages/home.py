import streamlit as st
import plotly.express as px

def display(df_comp):
    st.title("Rapport de Qualification – Vue d'ensemble")

    st.subheader("Top 3 entreprises (Score global)")
    top3 = df_comp.sort_values("Score Golbal", ascending=False).head(3)
    st.dataframe(top3[["Entreprises", "Score Golbal"]])

    st.subheader("Distribution des scores")
    fig = px.histogram(df_comp, x="Score Golbal", nbins=10)
    st.plotly_chart(fig, use_container_width=True)