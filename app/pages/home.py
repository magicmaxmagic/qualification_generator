# app/pages/home.py

import streamlit as st
import plotly.express as px
import pandas as pd
from sidebar import show_sidebar

def display(df_comp: pd.DataFrame):
    st.title("Rapport de qualification – Vue d'ensemble")

    # --- 1) Récupérer la liste des entreprises ---
    entreprises = df_comp["Entreprises"].dropna().unique().tolist()

    # --- 2) Sidebar : filtrer les entreprises (persisté via cookies/session) ---
    selected = show_sidebar(
        label="Entreprises à afficher",
        options=entreprises,
        default=entreprises,
        multiselect=True
    )
    if not selected:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    # --- 3) Sidebar : couleurs par entreprise (persistées) ---
    st.sidebar.markdown("### Couleurs par entreprise")
    color_map = {}
    for ent in selected:
        key = f"color_{ent}"
        col = st.sidebar.color_picker(
            ent,
            st.session_state.get(key, "#0072B2"),
            key=key
        )
        color_map[ent] = col

    # --- 4) Sidebar : couleur de l'histogramme (persistée) ---
    hist_color = st.sidebar.color_picker(
        "Histogramme",
        st.session_state.get("home_hist_color", "#0072B2"),
        key="home_hist_color"
    )

    # --- 5) Filtrer et nettoyer le DataFrame ---
    df = df_comp[df_comp["Entreprises"].isin(selected)].copy()
    if "Score Golbal" in df.columns:
        df.rename(columns={"Score Golbal": "Score Global"}, inplace=True)
    df["Score Global"] = pd.to_numeric(df["Score Global"], errors="coerce")
    df = df[df["Score Global"].notna()]
    if df.empty:
        st.warning("Aucune donnée valide après nettoyage.")
        return

    # --- 6) Statistiques clés ---
    st.markdown("---")
    st.markdown("### Statistiques générales")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entreprises", len(df))
    c2.metric("Score moyen", f"{df['Score Global'].mean():.2f}")
    c3.metric("Score maximal", f"{df['Score Global'].max():.2f}")
    c4.metric("Score minimal", f"{df['Score Global'].min():.2f}")

    # --- 7) Top 3 entreprises ---
    st.markdown("---")
    st.markdown("### Top 3 entreprises (Score Global)")
    top3 = df.sort_values("Score Global", ascending=False).head(3)
    st.dataframe(
        top3[["Entreprises", "Score Global"]]
            .rename(columns={"Entreprises": "Entreprise", "Score Global": "Score"}),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Entreprise": "Entreprise",
            "Score": st.column_config.NumberColumn("Score", format="%.2f")
        }
    )

    # --- 8) Bar chart Top 3 ---
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
    fig_top3.update_traces(texttemplate="%{text:.2f}", textposition="outside", showlegend=False)
    fig_top3.update_layout(margin=dict(t=30, b=60), yaxis_title="Score", xaxis_tickangle=-15)
    st.plotly_chart(fig_top3, use_container_width=True)

    # --- 9) Répartition des scores ---
    st.markdown("---")
    st.markdown("### Répartition des scores globaux")
    dist = df["Score Global"].round(2).value_counts().sort_index().reset_index()
    dist.columns = ["Score", "Count"]
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

    # --- 10) Analyse croisée (optionnelle) ---
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
                labels={"Score Global": "Score", "Nombre d'employés": "Employés"}
            )
            fig_sc.update_layout(margin=dict(t=30, b=30), showlegend=True)
            st.plotly_chart(fig_sc, use_container_width=True)
        else:
            st.info("La colonne 'Nombre d'employés' est manquante.")