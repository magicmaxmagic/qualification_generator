import streamlit as st
import plotly.express as px
import pandas as pd
from sidebar import show_sidebar  # doit renvoyer liste d’entreprises

def display(df_comp):
    st.title("Rapport de qualification – Vue d'ensemble")

    # 1) Filtrer les entreprises
    entreprises = df_comp["Entreprises"].dropna().unique().tolist()
    selected = show_sidebar(
        "Filtrer les entreprises à afficher",
        entreprises,
        default=entreprises
    )
    if not selected:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    # 2) Couleurs par entreprise
    st.sidebar.markdown("### Couleurs personnalisées")
    color_map = {
        ent: st.sidebar.color_picker(ent, "#0072B2")
        for ent in selected
    }

    # 3) Data cleaning & renommage
    df = df_comp[df_comp["Entreprises"].isin(selected)].copy()
    # gérer les deux orthographes possibles
    if "Score Golbal" in df.columns:
        df.rename(columns={"Score Golbal": "Score Global"}, inplace=True)
    df["Score Global"] = pd.to_numeric(df["Score Global"], errors="coerce")
    df = df[df["Score Global"].notna()]
    if df.empty:
        st.warning("Aucune donnée valide après nettoyage.")
        return

    # 4) Statistiques clés
    st.markdown("---")
    st.markdown("### Statistiques générales")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Entreprises", len(df))
    k2.metric("Score moyen", f"{df['Score Global'].mean():.2f}")
    k3.metric("Score maximal", f"{df['Score Global'].max():.2f}")
    k4.metric("Score minimal", f"{df['Score Global'].min():.2f}")

    # 5) Top 3
    st.markdown("---")
    st.markdown("### Top 3 entreprises (Score Global)")
    top3 = df.sort_values("Score Global", ascending=False).head(3)
    st.dataframe(
        top3[["Entreprises","Score Global"]]
            .rename(columns={"Entreprises":"Entreprise","Score Global":"Score"}),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Entreprise": "Entreprise",
            "Score": st.column_config.NumberColumn("Score", format="%.2f")
        }
    )

    # 6) Bar chart Top 3
    st.markdown("---")
    st.markdown("### Comparaison visuelle du Top 3")
    fig_top3 = px.bar(
        top3,
        x="Entreprises",
        y="Score Global",
        text="Score Global",
        color="Entreprises",
        color_discrete_map=color_map,
        template="simple_white"
    )
    fig_top3.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        showlegend=False
    )
    fig_top3.update_layout(
        margin=dict(t=30, b=60),
        yaxis_title="Score",
        xaxis_tickangle=-15
    )
    st.plotly_chart(fig_top3, use_container_width=True)

    # 7) Distribution par bar chart
    st.markdown("---")
    st.markdown("### Répartition des scores globaux")
    # construire un DataFrame {Score → count}
    dist = df["Score Global"].round(2).value_counts().sort_index().reset_index()
    dist.columns = ["Score","Count"]
    hist_color = st.sidebar.color_picker("Couleur de la répartition", "#0072B2")
    fig_dist = px.bar(
        dist,
        x="Score",
        y="Count",
        text="Count",
        template="simple_white",
        color_discrete_sequence=[hist_color]
    )
    fig_dist.update_traces(textposition="outside")
    fig_dist.update_layout(
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis_title="Score Global",
        yaxis_title="Nombre d’entreprises",
        showlegend=False
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    # 8) Analyse croisée (optionnelle)
    st.markdown("---")
    st.markdown("### Analyse croisée (optionnelle)")
    with st.expander("Voir Score Global vs Nombre d'employés"):
        if "Nombre d'employés" in df.columns:
            fig_sc = px.scatter(
                df,
                x="Nombre d'employés",
                y="Score Global",
                color="Entreprises",
                color_discrete_map=color_map,
                template="simple_white",
                labels={"Score Global":"Score","Nombre d'employés":"Employés"}
            )
            fig_sc.update_layout(margin=dict(t=30,b=30), showlegend=True)
            st.plotly_chart(fig_sc, use_container_width=True)
        else:
            st.info("La colonne 'Nombre d'employés' est manquante dans les données.")