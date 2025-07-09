# app/pages/alignement.py

import streamlit as st
import pandas as pd
from sidebar import show_sidebar, show_sidebar_alignement

def display(all_dfs):
    st.title("Alignement avec le besoin")
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    df_align = all_dfs.get("Analyse comparative")
    if df_align is None:
        st.error("La feuille 'Alignement avec le besoin' est introuvable dans le fichier Excel.")
        return
    
    st.write("Colonnes de la feuille Analyse comparative :", list(df_align.columns))
    st.dataframe(df_align.head())

    st.title("Alignement avec le besoin")
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # --- 1) Nettoyage des colonnes ---
    df_align.columns = [col.strip() for col in df_align.columns]

    # --- 2) Vérification de la colonne clé ---
    if "Exigence de base" not in df_align.columns:
        st.error("La colonne 'Exigence de base' est introuvable dans le fichier Excel.")
        st.stop()

    # --- 3) Sélection persistée du type d'exigence ---
    selected_exigence = show_sidebar_alignement(df_align)
    if not selected_exigence:
        st.info("Veuillez sélectionner un type d'exigence.")
        return

    # --- 4) Filtrage par exigence ---
    df_filtered = df_align[df_align["Exigence de base"] == selected_exigence].copy()

    # --- 5) Détermination dynamique des colonnes Entreprises / Justificatifs ---
    start_idx = df_filtered.columns.get_loc("Exigences") + 1
    entreprise_cols    = list(df_filtered.columns[start_idx::2])
    justificatif_cols  = list(df_filtered.columns[start_idx+1::2])

    # On retire les lignes complètement vides
    df_filtered = df_filtered[df_filtered[entreprise_cols].notna().any(axis=1)]

    # --- 6) Sélection persistée des entreprises à afficher ---
    selected_entreprises = show_sidebar(
        label="Entreprises à afficher",
        options=entreprise_cols,
        default=entreprise_cols,
        multiselect=True
    )
    if not selected_entreprises:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    # --- 7) Construction de la map de badges ---
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

    # --- 8) Application des badges dans le DataFrame ---
    for col in entreprise_cols:
        df_filtered[col] = (
            pd.Series(df_filtered[col])
            .apply(pd.to_numeric, errors="coerce")
            .fillna("")
            .astype(str)
            .replace(badge_map)
            .fillna("")  # pour les cellules vides
        )

    # --- 9) Affichage de la légende ---
    st.markdown("### Légende des scores")
    if selected_exigence == "Exigence de base":
        st.markdown(
            """
            <ul style="list-style:none;padding-left:0;">
              <li><span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Oui</span> : Exigence remplie</li>
              <li><span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Non</span> : Exigence non remplie</li>
            </ul>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <ul style="list-style:none;padding-left:0;">
              <li><span style='background:#6c757d;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>0</span> : Non répondu / Inapplicable</li>
              <li><span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>1</span> : Réponse partielle ou insuffisante</li>
              <li><span style='background:#fd7e14;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>2</span> : Réponse moyenne</li>
              <li><span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>3</span> : Réponse complète et satisfaisante</li>
            </ul>
            """,
            unsafe_allow_html=True
        )

    # --- 10) Grille d’évaluation ---
    st.markdown("### Grille d’évaluation")
    st.write(
        df_filtered[["Exigences"] + selected_entreprises]
            .to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    # --- 11) Justificatifs détaillés ---
    st.markdown("<hr style='margin:30px 0;'>", unsafe_allow_html=True)
    st.markdown("### Justificatifs détaillés")
    exigences_unique = df_filtered["Exigences"].dropna().unique()
    if len(exigences_unique) > 0:
        selected_row = st.selectbox("Choisissez une exigence à explorer :", exigences_unique)
        detail = df_filtered[df_filtered["Exigences"] == selected_row].iloc[0]
        for ent, justif_col in zip(entreprise_cols, justificatif_cols):
            if ent in selected_entreprises:
                justif = detail.get(justif_col, "")
                if isinstance(justif, str) and justif.strip():
                    st.markdown(
                        f"""
                        <div style="border:1px solid #e0e0e0;border-radius:8px;
                                    padding:15px;margin:10px 0;background:#f9f9f9;">
                          <strong style="font-size:15px;">{ent}</strong><br>
                          <span style="color:#333;font-size:14px;">{justif}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    else:
        st.info("Aucune exigence disponible pour ce type.")