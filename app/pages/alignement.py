import streamlit as st
import pandas as pd

# --- Chargement des données ---
def load_data(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)

    df_comp = pd.read_excel(xls, sheet_name="Comparatif")
    df_ent = pd.read_excel(xls, sheet_name="Entreprise")

    # Utilisation directe du header (ligne 1 visible)
    df_align = pd.read_excel(xls, sheet_name="Alignement avec le besoin", header=0)

    return df_comp, df_ent, df_align

# --- Affichage de la page "Alignement avec le besoin" ---
def display(df_align):
    st.title("Alignement avec le besoin")

    # Nettoyage des colonnes
    df_align.columns = [col.strip() for col in df_align.columns]

    # Sélection du type d'exigence
    exigence_types = df_align["Exigence de base"].dropna().unique()
    selected_exigence = st.selectbox("Type d'exigence à afficher", exigence_types)

    # Filtrage du type sélectionné
    df_filtered = df_align[df_align["Exigence de base"] == selected_exigence].copy()

    # Déduire dynamiquement les noms des colonnes d'entreprises et justificatifs
    start_idx = df_filtered.columns.get_loc("Exigences") + 1
    entreprise_cols = df_filtered.columns[start_idx::2]
    justificatif_cols = df_filtered.columns[start_idx+1::2]

    # Filtrage des lignes ayant au moins une valeur entreprise
    df_filtered = df_filtered[df_filtered[entreprise_cols].notna().any(axis=1)]

    # Badge visuel (couleurs)
    if selected_exigence == "Exigence de base":
        badge_map = {
            "0": "<span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Non</span>",
            "1": "<span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Oui</span>",
        }
    else:
        badge_map = {
            "0": "<span style='background:#6c757d;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>0</span>",
            "1": "<span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>1</span>",
            "2": "<span style='background:#fd7e14;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>2</span>",
            "3": "<span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>3</span>",
        }

    # Conversion et mapping badge
    for col in entreprise_cols:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors="coerce").fillna("").astype(str)
        df_filtered[col] = df_filtered[col].map(badge_map).fillna("")

    # Filtres dynamiques par entreprise
    selected_entreprises = st.multiselect("Filtrer les entreprises :", entreprise_cols, default=entreprise_cols)

    display_cols = ["Exigences"] + selected_entreprises

    # Affichage du tableau stylisé
    st.markdown("### Grille d’évaluation")
    st.write(df_filtered[display_cols].to_html(escape=False, index=False), unsafe_allow_html=True)

    # Affichage des justificatifs dynamiques
    st.markdown("---")
    st.markdown("### Justificatifs détaillés")

    exigences_unique = df_filtered["Exigences"].dropna().unique()
    if len(exigences_unique) > 0:
        selected_row = st.selectbox("Choisissez une exigence :", exigences_unique)
        detail = df_filtered[df_filtered["Exigences"] == selected_row].iloc[0]

        for entreprise, justif_col in zip(entreprise_cols, justificatif_cols):
            if entreprise in selected_entreprises:
                justification = detail.get(justif_col, "")
                if justification and isinstance(justification, str):
                    st.markdown(f"""
                        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 8px 0; background-color: #f9f9f9;">
                            <strong style="font-size: 15px;">{entreprise}</strong><br>
                            <span style="color: #333; font-size: 14px;">{justification}</span>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Aucune exigence à afficher pour ce type.")