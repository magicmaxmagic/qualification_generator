import streamlit as st
import random

def show_sidebar_comparatif(entreprises_disponibles, max_comparaison=6):
    st.sidebar.markdown("### Comparateur intelligent")

    with st.sidebar.expander("Sélection des entreprises", expanded=True):
        all_selected = st.checkbox("Tout sélectionner", value=True)
        
        if all_selected:
            selected = entreprises_disponibles
        else:
            selected = st.multiselect(
                "Choisissez les entreprises à comparer :",
                options=entreprises_disponibles,
                default=entreprises_disponibles[:3],
                help=f"Vous pouvez en comparer jusqu'à {max_comparaison} pour une meilleure lisibilité du radar."
            )

        st.markdown(f"**{len(selected)} entreprise(s)** sélectionnée(s)")

        if len(selected) > max_comparaison:
            st.warning(f"Le radar peut devenir illisible au-delà de {max_comparaison} entreprises.")

        if not selected:
            st.info("Aucune entreprise sélectionnée. Le radar ne sera pas affiché.", icon="⚠️")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Personnalisation visuelle (optionnelle)**")

    couleurs = {}
    if len(selected) > 0:
        for entreprise in selected:
            couleurs[entreprise] = st.sidebar.color_picker(f"Couleur pour {entreprise}", _get_random_color())

    return selected, couleurs

def _get_random_color():
    r = lambda: random.randint(100, 200)
    return f'#{r():02x}{r():02x}{r():02x}'

# --- Sidebar générique pour les autres pages (home, entreprise, etc.)
def show_sidebar(label, options, default=None, multiselect=True, single=False):
    st.sidebar.markdown(f"### {label}")
    if single or not multiselect:
        return [st.sidebar.selectbox("Sélection :", options, index=0 if not default else options.index(default[0]))]
    else:
        return st.sidebar.multiselect("Sélection :", options, default=default or options[:1])
    
def show_sidebar_alignement(df_align):
    st.sidebar.markdown("### Type d'exigence")
    types_exigence = df_align["Exigence de base"].dropna().unique().tolist()

    if not types_exigence:
        st.sidebar.warning("Aucun type d'exigence détecté.")
        return None

    return st.sidebar.radio(
        "Sélectionnez un type d'exigence :",
        options=types_exigence,
        index=0
    )