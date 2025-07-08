# sidebar.py
import streamlit as st
import random, json
from streamlit_cookies_manager import EncryptedCookieManager

# —————————————————————————————————————————————
# 1) Initialisation du gestionnaire de cookies
# —————————————————————————————————————————————
COOKIE_PWD = st.secrets["cookie_password"]
cookies = EncryptedCookieManager(prefix="iveo_", password=COOKIE_PWD)
if not cookies.ready():
    st.stop()

def _random_color() -> str:
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(100, 200),
        random.randint(100, 200),
        random.randint(100, 200),
    )

def show_sidebar_comparatif(
    entreprises_disponibles: list[str],
    max_comparaison: int = 6
) -> tuple[list[str], dict[str,str]]:
    KEY_SEL = "cmp_selected"
    raw = cookies.get(KEY_SEL)
    previous = json.loads(raw) if raw else entreprises_disponibles[:3]
    previous = [e for e in previous if e in entreprises_disponibles]
    if not previous:
        previous = entreprises_disponibles[:3]

    st.sidebar.markdown("### Filtrer les entreprises")
    with st.sidebar.expander("Sélection", expanded=True):
        all_sel = st.checkbox(
            "Tout sélectionner",
            value=(len(previous) == len(entreprises_disponibles)),
        )
        if all_sel:
            sel = entreprises_disponibles
        else:
            sel = st.multiselect(
                "Entreprises à comparer",
                entreprises_disponibles,
                default=previous
            )
        if len(sel) > max_comparaison:
            st.warning(f"Au-delà de {max_comparaison}, le radar devient illisible.")

    # on sérialise la sélection
    cookies[KEY_SEL] = json.dumps(sel)

    st.sidebar.markdown("---\n### Couleurs personnalisées")
    couleurs: dict[str, str] = {}
    for ent in sel:
        ckey = f"cmp_color_{ent}"
        prev = cookies.get(ckey)
        if isinstance(prev, str) and prev.startswith("#") and len(prev) == 7:
            base = prev
        else:
            base = _random_color()
        col = st.sidebar.color_picker(ent, base, key=ckey)
        couleurs[ent] = col
        cookies[ckey] = col
        
    all_color_keys = [f"cmp_color_{e}" for e in entreprises_disponibles]
    for k in list(cookies.keys()):
        if k.startswith("cmp_color_") and k not in all_color_keys:
            del cookies[k]

    return sel, couleurs

def show_sidebar(
    label: str,
    options: list[str],
    default: list[str]|None = None,
    multiselect: bool = True
) -> list[str]:
    KEY = f"{label.replace(' ', '_').lower()}_selected"
    raw = cookies.get(KEY)
    previous = json.loads(raw) if raw else (default or options[:1])
    previous = [v for v in previous if v in options]
    if not previous:
        previous = default or options[:1]
    st.sidebar.markdown(f"### {label}")
    if multiselect:
        sel = st.sidebar.multiselect(
            label,
            options,
            default=previous,
            key=KEY
        )
    else:
        idx = options.index(previous[0] if isinstance(previous, list) else previous)
        choice = st.sidebar.selectbox(
            label,
            options,
            index=idx,
            key=KEY
        )
        sel = [choice]

    cookies[KEY] = json.dumps(sel)
    return sel

def show_sidebar_alignement(df_align) -> str:
    KEY = "align_exigence"
    types_ = df_align["Exigence de base"].dropna().unique().tolist()
    raw = cookies.get(KEY)
    prev = raw if raw in types_ else (types_[0] if types_ else "")

    st.sidebar.markdown("### Type d'exigence")
    sel = st.sidebar.radio(
        "Choisissez un type",
        options=types_,
        index=types_.index(prev) if prev in types_ else 0,
        key=KEY
    )

    cookies[KEY] = sel
    return sel