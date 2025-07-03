import streamlit as st
import plotly.express as px

def display(df_comp):
    st.title("Rapport de Qualification – Vue d'ensemble")

    st.subheader("Top 3 entreprises (Score global)")
    top3 = df_comp.sort_values("Score Golbal", ascending=False).head(3)
    st.dataframe(top3[["Entreprises", "Score Golbal"]])

    st.subheader("Distribution des scores")
    fig = px.histogram(
        df_comp,
        x="Score Golbal",
        nbins=10,
        title="Distribution des scores globaux",
        color_discrete_sequence=["#1f8a70"]
    )
    fig.update_layout(
        xaxis_title="Score global",
        yaxis_title="Nombre d'entreprises",
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        title_x=0.5,
        font=dict(size=14),
    )
    st.plotly_chart(fig, use_container_width=True)

