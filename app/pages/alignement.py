import streamlit as st

def display(df_align):
    st.title("Alignement avec le besoin")

    exigence_types = df_align["Exigence de base"].dropna().unique()
    selected_exigence = st.selectbox("Type d'exigence à afficher", exigence_types)

    df_filtered = df_align[df_align["Exigence de base"] == selected_exigence].copy()
    df_filtered = df_filtered.astype(str)

    icon_map_base = {"1": "🟢", "0": "🔴"}
    icon_map_other = {"0": "⚪", "1": "🔴", "2": "🟠", "3": "🟢"}

    for col in df_filtered.columns:
        if "Entreprise" in col:
            if selected_exigence == "Exigence de base":
                df_filtered[col] = df_filtered[col].map(icon_map_base).fillna(df_filtered[col])
            else:
                df_filtered[col] = df_filtered[col].map(icon_map_other).fillna(df_filtered[col])

    st.markdown("### Grille d'exigences")
    st.dataframe(df_filtered, use_container_width=True)