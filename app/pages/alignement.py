import streamlit as st
import pandas as pd
from sidebar import show_sidebar_alignement

def load_data(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    df_comp = pd.read_excel(xls, sheet_name="Comparatif")
    df_ent = pd.read_excel(xls, sheet_name="Entreprise")
    df_align = pd.read_excel(xls, sheet_name="Alignement avec le besoin", header=0)
    return df_comp, df_ent, df_align

def display(df_align):
    st.title("Alignement avec le besoin")
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # --- Nettoyage des colonnes ---
    df_align.columns = [col.strip() for col in df_align.columns]

    # Vérifie que la colonne Exigence de base existe
    if "Exigence de base" not in df_align.columns:
        st.error("La colonne 'Exigence de base' est introuvable dans le fichier Excel.")
        st.stop()

    exigences_types = df_align["Exigence de base"].dropna().unique().tolist()
    exigences_types.sort()

    # --- Sidebar : sélection du type d'exigence ---
    st.sidebar.markdown("### Type d'exigence")
    selected_exigence = st.sidebar.selectbox("Filtrer par exigence :", exigences_types, index=0)

    # --- Filtrage selon sélection ---
    df_filtered = df_align[df_align["Exigence de base"] == selected_exigence].copy()

    # --- Colonnes entreprise et justificatif dynamiques ---
    start_idx = df_filtered.columns.get_loc("Exigences") + 1
    entreprise_cols = df_filtered.columns[start_idx::2]
    justificatif_cols = df_filtered.columns[start_idx + 1::2]

    # Supprime les lignes entièrement vides
    df_filtered = df_filtered[df_filtered[entreprise_cols].notna().any(axis=1)]

    # --- Sidebar : sélection des entreprises visibles ---
    st.sidebar.markdown("### Entreprises à afficher")
    selected_entreprises = st.sidebar.multiselect(
        "Choisir les entreprises :",
        entreprise_cols,
        default=list(entreprise_cols)
    )

    # --- Définition des badges stylisés ---
    badge_map = {
        "0": "<span style='background:#6c757d;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>0</span>",
        "1": "<span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>1</span>",
        "2": "<span style='background:#fd7e14;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>2</span>",
        "3": "<span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>3</span>",
    }
    if selected_exigence == "Exigence de base":
        badge_map = {
            "0": "<span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Non</span>",
            "1": "<span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Oui</span>",
        }

    # Application des badges
    for col in entreprise_cols:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors="coerce").fillna("").astype(str)
        df_filtered[col] = df_filtered[col].map(badge_map).fillna("")

    # --- Légende des scores ---
    st.markdown("### Légende des scores")
    if selected_exigence == "Exigence de base":
        st.markdown("""
        <ul style="list-style:none;padding-left:0;">
            <li><span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Oui</span> : Exigence remplie</li>
            <li><span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>Non</span> : Exigence non remplie</li>
        </ul>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <ul style="list-style:none;padding-left:0;">
            <li><span style='background:#6c757d;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>0</span> : Non répondu / Inapplicable</li>
            <li><span style='background:#dc3545;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>1</span> : Réponse partielle ou insuffisante</li>
            <li><span style='background:#fd7e14;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>2</span> : Réponse moyenne</li>
            <li><span style='background:#28a745;color:white;padding:4px 8px;border-radius:6px;font-size:13px;'>3</span> : Réponse complète et satisfaisante</li>
        </ul>
        """, unsafe_allow_html=True)
        
    # --- Grille d’évaluation ---
    st.markdown("### Grille d’évaluation")
    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
    st.write(
        df_filtered[["Exigences"] + selected_entreprises].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    # --- Justificatifs ---
    st.markdown("<hr style='margin:30px 0;'>", unsafe_allow_html=True)
    st.markdown("### Justificatifs détaillés")

    exigences_unique = df_filtered["Exigences"].dropna().unique()
    if len(exigences_unique) > 0:
        selected_row = st.selectbox("Choisissez une exigence à explorer :", exigences_unique)
        detail = df_filtered[df_filtered["Exigences"] == selected_row].iloc[0]

        for entreprise, justif_col in zip(entreprise_cols, justificatif_cols):
            if entreprise in selected_entreprises:
                justification = detail.get(justif_col, "")
                if justification and isinstance(justification, str) and justification.strip():
                    st.markdown(f"""
                        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                            <strong style="font-size: 15px;">{entreprise}</strong><br>
                            <span style="color: #333; font-size: 14px;">{justification}</span>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Aucune exigence disponible pour ce type.")