import streamlit as st
import pandas as pd
import pydeck as pdk
import json
from geopy.geocoders import Nominatim
from sidebar import cookies

# --- Visual Theme ---
THEME = {
    # Bleu clair de la sidebar (ex : #e6f4f1), blanc, et bleu vif
    "primary": "#0072B2",           # Bleu vif (accent)
    "secondary": "#e3f0fa",         # Bleu clair pur (sans vert)
    "background": "#fff",           # Blanc pur
    "gradient_start": "#e3f0fa",    # Bleu clair pur (sans vert)
    "gradient_end": "#fff",         # Blanc
    "accent": "#0072B2",            # Bleu vif
    "shadow_light": "0 2px 16px rgba(0,0,0,0.08)",
    "radius": "18px",
}
HR = '<hr style="margin:2.2rem 0 1.5rem 0; border:none; border-top:2px solid #e3f0fa;" />'

# --- Caching Geocoder ---
@st.cache_data(show_spinner=False)
def geocode(address: str):
    try:
        loc = Nominatim(user_agent="entreprise_app").geocode(address)
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except Exception:
        return (None, None)

# --- HTML Generators ---
def _wrap_html(html: str, max_width: int = 900):
    """
    Enveloppe un bloc HTML dans un conteneur centré avec largeur maximale.
    Permet de centrer et limiter la largeur des sections pour un rendu responsive.
    Args:
        html (str): Le code HTML à envelopper.
        max_width (int): Largeur maximale du conteneur (en px).
    Returns:
        str: HTML prêt à être injecté dans st.markdown.
    """
    return f'<div style="max-width:{max_width}px;margin:0 auto;">{html}</div>'

def render_header(title: str):
    """
    Affiche le header principal de la page avec un fond dégradé, un emoji et le titre centré.
    Args:
        title (str): Titre à afficher dans le header.
    """
    style = (
        f'display:flex;align-items:center;justify-content:center;'
        f'background:#fff;'
        f'box-shadow:{THEME["shadow_light"]};border-radius:{THEME["radius"]};'
        f'padding:18px 32px;margin-bottom:1rem;'
        f'gap:16px;'
    )
    html = f'<div style="{style}"><h1 style="margin:0;font-size:2.7rem;font-weight:900;color:#181818;">{title}</h1></div>'
    st.markdown(_wrap_html(html), unsafe_allow_html=True)

def render_logo_and_name(name: str, logo_url: str, color: str):
    """
    Affiche une carte contenant le nom de l'entreprise et son logo (ou un fallback si absent).
    Args:
        name (str): Nom de l'entreprise.
        logo_url (str): URL du logo (ou vide).
        color (str): Couleur principale personnalisée pour le nom.
    """
    if isinstance(logo_url, str) and logo_url.startswith('http'):
        logo = f"<img src='{logo_url}' width='110' style='border-radius:14px;box-shadow:{THEME['shadow_light']};margin-left:32px;' alt='Logo entreprise'/>"
    else:
        logo = "<div style='width:110px;height:110px;display:flex;align-items:center;justify-content:center;background:#eee;border:1px solid #ddd;border-radius:14px;margin-left:32px;color:#aaa;font-size:13px;'>Logo</div>"
    html = (
        f'display:flex;align-items:center;justify-content:center;gap:36px;'
        f'box-shadow:{THEME["shadow_light"]};background:#fff;'
        f'border-radius:{THEME["radius"]};padding:28px 36px 18px 36px;max-width:700px;margin:24px auto 0 auto;'
    )
    # Couleur du nom de l'entreprise forcée à noir
    card = f'<div style="{html}"><div style="flex:1;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;min-width:0;"><span style="font-size:2.4rem;font-weight:800;color:#181818;letter-spacing:0.5px;line-height:1.1;word-break:break-word;">{name}</span></div><div style="flex-shrink:0;">{logo}</div></div>'
    st.markdown(_wrap_html(card, 700), unsafe_allow_html=True)

def render_button(label: str, url: str):
    """
    Affiche un bouton stylisé (site web ou vidéo) avec accessibilité et effet hover moderne.
    Args:
        label (str): Texte du bouton.
        url (str): Lien cible (YouTube ou site web).
    """
    if 'youtube' in url:
        btn = (
            f'''<a href="{url}" target="_blank" aria-label="Voir la vidéo de présentation" title="Voir la vidéo de présentation" style="text-decoration:none;">
              <span style="display:inline-flex;align-items:center;gap:10px;background:linear-gradient(90deg,#ff0000 0%,#c4302b 100%);color:#fff;font-weight:700;font-size:1.13rem;padding:10px 26px 10px 18px;border:none;border-radius:28px;box-shadow:0 4px 18px #c4302b22,0 1.5px 6px #ff000022;cursor:pointer;transition:box-shadow 0.2s,transform 0.2s,scale 0.2s;letter-spacing:0.5px;line-height:1.2;overflow:hidden;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="margin-right:6px;"><rect width="24" height="24" rx="12" fill="#ff0000"/><polygon points="10,8 16,12 10,16" fill="#fff"/></svg>
                <span>Voir la vidéo</span>
              </span>
            </a>'''
        )
    else:
        btn = (
            f'<a href="{url}" target="_blank" aria-label="Site web officiel" title="Site web officiel" style="text-decoration:none;">'
            f'<button style="background:#fff;border:2.5px solid #0072B2;color:#181818;padding:10px 22px;border-radius:28px;font-weight:700;cursor:pointer;box-shadow:0 4px 18px #0072B222;transition:transform .2s;font-size:1.08rem;">{label}</button></a>'
        )
    st.markdown(_wrap_html(btn, 400), unsafe_allow_html=True)

def render_section(title: str, bg: str = None):
    """
    Affiche un titre de section centré, avec fond blanc ou bleu clair et séparation visuelle harmonisée.
    Args:
        title (str): Titre de la section.
        bg (str, optionnel): Couleur de fond (blanc ou bleu clair). Défaut : blanc.
    """
    # Utilisation de st.session_state pour garantir la robustesse du compteur même en cas de reload
    if 'section_count' not in st.session_state:
        st.session_state['section_count'] = 0
    st.session_state['section_count'] += 1
    # Afficher le HR uniquement à partir de la 2e section, avec marge haute
    if st.session_state['section_count'] > 1:
        st.markdown(HR, unsafe_allow_html=True)
    # Titre de section simple, centré, sans fond ni carte
    st.markdown(_wrap_html(f'<h3 style="color:#181818;text-align:center;margin:0 0 1.1rem 0;font-size:1.45rem;font-weight:800;letter-spacing:0.01em;">{title}</h3>'), unsafe_allow_html=True)

def reset_section_counter():
    """Réinitialise le compteur de section pour l'affichage harmonisé des titres de section."""
    st.session_state['section_count'] = 0

# --- Main Display ---
def display(df_ent: pd.DataFrame):
    # Réinitialiser le compteur de section à chaque affichage (avant tout appel à render_section)
    reset_section_counter()
    # Sidebar: select company
    companies = df_ent['Entreprises'].dropna().unique()
    selected = st.sidebar.selectbox('Choisissez une entreprise', companies, key='select_entreprise')
    cookies['entreprise_selected'] = json.dumps([selected])
    info = df_ent[df_ent['Entreprises'] == selected].iloc[0]

    # Colors
    color = st.sidebar.color_picker('Couleur principale', THEME['accent'])


    # Header
    render_header('Fiche entreprise')
    # Ligne séparatrice entre le header et le bloc logo/boutons
    st.markdown(HR, unsafe_allow_html=True)



    # Logo, nom
    render_logo_and_name(selected, info.get('URL (logo)', ''), color)
    # Récupération des URLs (compatibilité)
    # Recherche robuste de l'URL du site web (insensible à la casse, espaces, etc.)
    url_site = ''
    for key in info.keys():
        if 'site' in key.lower() and 'web' in key.lower():
            val = info.get(key, '')
            if isinstance(val, str) and val.strip() and val.strip().lower() not in ['-', 'nan', 'aucun', 'none']:
                url_site = val.strip()
                break
        if key.strip().lower() == 'website':
            val = info.get(key, '')
            if isinstance(val, str) and val.strip() and val.strip().lower() not in ['-', 'nan', 'aucun', 'none']:
                url_site = val.strip()
                break
    video = info.get('URL (vidéo)', '')
    # Affichage côte à côte, site web à gauche, vidéo à droite
    btns_html = ''
    show_site = isinstance(url_site, str) and url_site.strip() and url_site.strip().lower() not in ['-', 'nan', 'aucun', 'none']
    show_video = isinstance(video, str) and 'youtube' in video and video.strip().lower() not in ['-', 'nan', 'aucun', 'none']
    if show_site or show_video:
        st.markdown('''<style>
        a[aria-label="Site web officiel"] span:hover, a[aria-label="Site web officiel"] span:focus {
            background:linear-gradient(90deg,#e6f4f1 0%,#fff 100%);
            border:2.5px solid #0072B2;
            transform:scale(1.045);
            box-shadow:0 8px 32px #0072B244, 0 2px 8px #0072B244;
        }
        a[aria-label="Voir la vidéo de présentation"] span:hover, a[aria-label="Voir la vidéo de présentation"] span:focus {
            background:linear-gradient(90deg,#fff 0%,#ffeaea 100%) !important;
            border:2.5px solid #c4302b !important;
            transform:scale(1.045) !important;
            box-shadow:0 8px 32px #c4302b44, 0 2px 8px #c4302b44 !important;
        }
        </style>''', unsafe_allow_html=True)
        btns_html += '<div style="margin:18px 0 0 0;text-align:center;display:flex;justify-content:center;gap:18px;flex-wrap:wrap;">'
        if show_site:
            btns_html += f'''
            <a href="{url_site}" target="_blank" aria-label="Site web officiel" title="Site web officiel" style="text-decoration:none;">
              <span style="display:inline-flex;align-items:center;gap:10px;background:#fff;border:2.5px solid #fff;color:#0072B2;font-weight:700;font-size:1.13rem;padding:10px 26px 10px 18px;border-radius:28px;box-shadow:0 4px 18px #0072B222,0 1.5px 6px #0072B222;cursor:pointer;transition:box-shadow 0.22s,transform 0.18s,scale 0.18s;letter-spacing:0.5px;line-height:1.2;overflow:hidden;position:relative;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="margin-right:6px;"><circle cx="12" cy="12" r="12" fill="#0072B2"/><path d="M16.5 12a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Zm-7.5 0a3 3 0 1 0 6 0 3 3 0 0 0-6 0Z" fill="#fff"/></svg>
                <span>Site web officiel</span>
                <span style="position:absolute;inset:0;border-radius:28px;pointer-events:none;transition:box-shadow 0.22s,transform 0.18s,scale 0.18s;"></span>
              </span>
            </a>'''
        if show_video:
            btns_html += f'''
            <a href="{video}" target="_blank" aria-label="Voir la vidéo de présentation" title="Voir la vidéo de présentation" style="text-decoration:none;">
              <span style="display:inline-flex;align-items:center;gap:10px;background:#fff;border:2.5px solid #fff;color:#c4302b;font-weight:700;font-size:1.13rem;padding:10px 26px 10px 18px;border-radius:28px;box-shadow:0 4px 18px #c4302b22,0 1.5px 6px #c4302b22;cursor:pointer;transition:box-shadow 0.22s,transform 0.18s,scale 0.18s;letter-spacing:0.5px;line-height:1.2;overflow:hidden;position:relative;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="margin-right:6px;"><rect width="24" height="24" rx="12" fill="#c4302b"/><polygon points="10,8 16,12 10,16" fill="#fff"/></svg>
                <span>Voir la vidéo</span>
                <span style="position:absolute;inset:0;border-radius:28px;pointer-events:none;transition:box-shadow 0.22s,transform 0.18s,scale 0.18s;"></span>
              </span>
            </a>'''
        btns_html += '</div>'
        st.markdown(_wrap_html(btns_html, 700), unsafe_allow_html=True)

    # Ligne séparatrice entre le header/logo/boutons et la première section
    st.markdown(HR, unsafe_allow_html=True)

    render_section('Description', bg=THEME["background"])
    desc = info.get('Description', '')
    if not isinstance(desc, str) or not desc.strip():
        desc = "Aucune description disponible."
    # Sécurité couleur : forcer le fond à blanc pur, jamais vert ni autre couleur
    desc_bg = THEME["background"] if THEME["background"] in ["#fff", "#ffffff", THEME["secondary"]] else "#fff"
    desc_html = (
        f'<div style="background:{desc_bg};padding:1.5rem 2.2rem 1.7rem 2.2rem;border-radius:{THEME["radius"]};'
        f'box-shadow:{THEME["shadow_light"]};margin-top:-1.1rem;margin-bottom:1.5rem;min-width:0;width:100%;">'
        f'<div style="border-left:6px solid {THEME["primary"]};font-size:1.13rem;padding-left:1.1rem;">{desc}</div>'
        f'</div>'
    )
    st.markdown(_wrap_html(desc_html, 1200), unsafe_allow_html=True)

    # Info Cards (forcer fond blanc sur toute la section, jamais vert)
    # Un seul bloc/titre pour Informations générales
    render_section('Informations générales', bg=THEME["background"])
    fields = [c for c in df_ent.columns if c not in ['Entreprises','Description','URL (logo)','URL (vidéo)']]
    selected_fields = st.sidebar.multiselect('Champs visibles', fields, default=fields[:4], key='fields_entreprise')
    cards = ''
    for i, f in enumerate(selected_fields):
        val = info.get(f, 'N/A')
        bg = THEME['background'] if i % 2 == 0 else THEME['secondary']
        if bg not in [THEME['background'], THEME['secondary']]:
            bg = THEME['background']
        cards += (
            f'<div style="background:{bg};padding:1rem 1.2rem;border-radius:{THEME["radius"]};'
            f'box-shadow:{THEME["shadow_light"]};margin:8px;min-width:200px;transition:box-shadow .2s;">'
            f'<strong style="color:{THEME["primary"]};font-size:1.08rem;">{f}</strong><div style="font-size:1.18rem;">{val}</div></div>'
        )
    grid_bg = THEME["background"] if THEME["background"] in ["#ffffff", "#ffffff", THEME["secondary"]] else "#ffffff"
    grid_section_html = (
        f'<div style="background:{grid_bg};padding:1.5rem 2.2rem 1.7rem 2.2rem;border-radius:{THEME["radius"]};box-shadow:{THEME["shadow_light"]};margin-top:-1.1rem;margin-bottom:1.5rem;">'
        f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:24px;width:100%;">{cards}</div>'
        f'</div>'
    )
    st.markdown(_wrap_html(grid_section_html, 1200), unsafe_allow_html=True)

    # Carte de localisation améliorée
    render_section('Localisation')
    addr = info.get('Localisation (Siège social)', '')
    with st.spinner('Géocodage de l’adresse en cours...'):
        lat, lon = geocode(addr)
    if lat and lon:
        df_map = pd.DataFrame([{'lat': lat, 'lon': lon, 'name': 'Siège'}])
        layer = pdk.Layer(
            'ScatterplotLayer',
            df_map,
            get_position='[lon,lat]',
            get_radius=1000,
            get_color=[0,128,255],
            pickable=True,
            tooltip=True
        )
        view = pdk.ViewState(latitude=lat, longitude=lon, zoom=7)
        st.pydeck_chart(
            pdk.Deck(
                initial_view_state=view,
                layers=[layer],
                tooltip={"text": "{name} : [{lat}, {lon}]"}
            ),
            use_container_width=True
        )
    else:
        st.warning('Adresse non géocodée ou introuvable. Merci de vérifier l’adresse saisie.', icon="")
