import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from sidebar import show_sidebar, show_sidebar_comparatif, show_sidebar_alignement

def display(df_comp):
    st.title("Comparatif global des entreprises")

    # 1) Harmonisation du nom de colonne "Score Golbal" → "Score Global"
    if "Score Golbal" in df_comp.columns:
        df_comp = df_comp.rename(columns={"Score Golbal": "Score Global"})

    # 2) Mapping colonne réelle → label court pour radar
    radar_map = {
        "Alignement avec les besoins":           "Alignement\nbesoin",
        "Avantage compétitif":                   "Avantage\ncompétitif",
        "Maturité technologie/business":         "Maturité\ntechno/business",
        "Coût  et avantage économique (achat, fixe, maintenance, etc.)": "Coût/\navantage",
        "Satisfaction client":                   "Satisfaction\nclient",
        "Degré d'accompagnement":                "Accompagnement"
    }
    radar_cols   = list(radar_map.keys())
    radar_labels = list(radar_map.values())

    # 3) On ne garde que les entreprises ayant toutes les valeurs radar
    df_valid = df_comp.dropna(subset=radar_cols, how="any")
    entreprises_disponibles = df_valid["Entreprises"].dropna().unique().tolist()

    # 4) Sidebar → choix des entreprises et des couleurs
    selected_entreprises, couleurs = show_sidebar_comparatif(entreprises_disponibles)
    if not selected_entreprises:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return
    df_filtered = df_valid[df_valid["Entreprises"].isin(selected_entreprises)].copy()

    # 5) Sidebar → choix des colonnes à afficher dans le tableau
    st.sidebar.markdown("### Colonnes du tableau")
    default_cols = ["Entreprises", "Score Global"] + radar_cols[:2]
    default_cols = [c for c in default_cols if c in df_filtered.columns]
    selected_cols = st.sidebar.multiselect(
        "Sélectionnez les colonnes à afficher",
        options=df_filtered.columns.tolist(),
        default=default_cols,
        key="cmp_table_cols"
    )

    # 6) Affichage du tableau de données
    st.markdown("#### Données comparatives")
    st.dataframe(df_filtered[selected_cols], use_container_width=True)

    # 7) Radar combiné superposé
    st.markdown("#### Radar superposé")
    fig = go.Figure()
    for _, row in df_filtered.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row[c] for c in radar_cols],
            theta=radar_labels,
            fill="toself",
            name=row["Entreprises"],
            line=dict(color=couleurs.get(row["Entreprises"]))
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5]),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        showlegend=True,
        margin=dict(t=20, b=20),
        height=550
    )
    st.plotly_chart(fig, use_container_width=True)

    # 8) Subplots individuels (2 colonnes max)
    st.markdown("#### Détails radar par entreprise")
    n = len(df_filtered)
    rows = (n + 1) // 2
    fig2 = make_subplots(
        rows=rows, cols=2,
        specs=[[{"type":"polar"}, {"type":"polar"}] for _ in range(rows)],
        subplot_titles=df_filtered["Entreprises"].tolist(),
        vertical_spacing=0.25
    )
    for idx, (_, row) in enumerate(df_filtered.iterrows()):
        r = idx // 2 + 1
        c = idx % 2 + 1
        fig2.add_trace(go.Scatterpolar(
            r=[row[col] for col in radar_cols],
            theta=radar_labels,
            fill="toself",
            name=row["Entreprises"],
            showlegend=False,
            line=dict(color=couleurs.get(row["Entreprises"]))
        ), row=r, col=c)

    fig2.update_layout(
        height=400 * rows,
        margin=dict(t=60, l=20, r=20),
        font=dict(size=12)
    )
    fig2.update_polars(
        radialaxis=dict(visible=True, range=[0, 5]),
        angularaxis=dict(tickfont=dict(size=11))
    )
    st.plotly_chart(fig2, use_container_width=True)