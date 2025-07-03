import streamlit as st
import plotly.express as px

def display(df_comp):
    st.title("Comparatif global des entreprises")

    selected_cols = st.multiselect("Colonnes à afficher", df_comp.columns.tolist(), default=[
        "Entreprises", "Score Golbal", "Alignement avec les besoins"])
    st.dataframe(df_comp[selected_cols])

    st.subheader("Graphiques radar")
    radar_cols = [
        "Alignement avec les besoins",
        "Avantage compétitif",
        "Maturité technologie/business",
        "Coût  et avantage économique (achat, fixe, maintenance, etc.)",
        "Satisfaction client",
        "Degré d'accompagnement"
    ]

    for _, row in df_comp.iterrows():
        fig = px.line_polar(
            r=[row[c] for c in radar_cols],
            theta=radar_cols,
            line_close=True,
            title=row["Entreprises"]
        )
        st.plotly_chart(fig, use_container_width=True)