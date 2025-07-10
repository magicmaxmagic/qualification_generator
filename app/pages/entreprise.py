import streamlit as st
import pandas as pd
import pydeck as pdk
import json
from geopy.geocoders import Nominatim
from sidebar import cookies, apply_sidebar_styles

# --- Visual Theme avec Transparence Simple ---
THEME = {
    # Couleurs principales IVÉO
    "primary": "#0072B2",           # Bleu vif (accent)
    "secondary": "#fff",         # Bleu clair pur (sans vert)
    "background": "#fff",           # Blanc pur
    "gradient_start": "#fff",    # Bleu clair pur (sans vert)
    "gradient_end": "#fff",         # Blanc
    "accent": "#0072B2",            # Bleu vif
    "shadow_light": "0 2px 16px rgba(0,0,0,0.08)",
    "radius": "18px",
    
    # Transparence simple et professionnelle
    "glass_bg": "rgba(255, 255, 255, 0.7)",            # Blanc semi-transparent simple
    "glass_bg_light": "rgba(255, 255, 255, 0.8)",      # Blanc plus opaque
    "glass_bg_blue": "rgba(255, 255, 255, 0.6)",       # Bleu clair semi-transparent
    "glass_border": "rgba(255, 255, 255, 0.2)",        # Bordure transparente simple
    "glass_shadow": "0 4px 20px rgba(255, 255, 255, 0.1), 0 2px 8px rgba(255, 255, 255, 0.05)",
    "glass_backdrop": "",                               # Pas de flou
}

HR = '<hr style="margin:1.5rem 0 1rem 0; border:none; border-top:2px solid #e3f0fa;" />'
SEPARATOR = '<div style="margin:1.2rem 0;border-bottom:1px solid rgba(0,0,0,0.1);"></div>'

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
    Header professionnel compact avec effet de transparence simple pour présentation client.
    Args:
        title (str): Titre à afficher dans le header.
    """
    style = (
        'display:flex;align-items:center;justify-content:center;flex-direction:column;'
        f'background:{THEME["glass_bg_light"]};'
        f'box-shadow:{THEME["glass_shadow"]};'
        'border-radius:12px;'
        'padding:16px 18px;margin-bottom:1rem;'
        f'border:1px solid {THEME["glass_border"]};max-width:900px;'
        'position:relative;'
        'transition: all 0.3s ease;'
    )
    html = f'''<div style="{style}">
        <h1 style="margin:0;font-size:1.6rem;font-weight:700;color:#000;letter-spacing:-0.01em;line-height:1.1;text-align:center;">{title}</h1>
    </div>'''
    st.markdown(_wrap_html(html, 900), unsafe_allow_html=True)

def render_logo_and_name(name: str, logo_url: str, color: str, url_site: str = '', video: str = ''):
    """
    Carte professionnelle compacte avec transparence simple pour présentation client.
    Args:
        name (str): Nom de l'entreprise.
        logo_url (str): URL du logo.
        color (str): Couleur principale.
        url_site (str): URL du site web.
        video (str): URL de la vidéo.
    """
    show_site = isinstance(url_site, str) and url_site.strip() and url_site.strip().lower() not in ['-', 'nan', 'aucun', 'none']
    show_video = isinstance(video, str) and 'youtube' in video and video.strip().lower() not in ['-', 'nan', 'aucun', 'none']

    # Logo professionnel compact avec transparence simple
    if isinstance(logo_url, str) and logo_url.startswith('http'):
        logo = f"""<div style="width:60px;height:60px;border-radius:8px;background:{THEME['glass_bg']};padding:6px;border:1px solid {THEME['glass_border']};display:flex;align-items:center;justify-content:center;box-shadow:{THEME['glass_shadow']};transition:all 0.3s ease;">
            <img src='{logo_url}' width='48' style='border-radius:4px;max-width:100%;max-height:100%;object-fit:contain;' alt='Logo entreprise'/>
        </div>"""
    else:
        logo = f"""<div style="width:60px;height:60px;border-radius:8px;background:{THEME['glass_bg']};border:1px solid {THEME['glass_border']};display:flex;align-items:center;justify-content:center;color:#000;font-size:10px;font-weight:600;box-shadow:{THEME['glass_shadow']};transition:all 0.3s ease;">Logo</div>"""

    # Boutons professionnels compacts avec transparence simple
    btns = ''
    if show_site:
        btns += f'''<a href="{url_site}" target="_blank" style="text-decoration:none;display:inline-block;margin-right:8px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:{THEME['glass_bg']};border:2px solid {THEME['primary']};color:#000;font-weight:600;font-size:0.8rem;padding:6px 12px;border-radius:6px;cursor:pointer;transition:all 0.3s ease;letter-spacing:0.3px;box-shadow:{THEME['glass_shadow']};">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" style="margin-right:1px;"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            Site web
        </div></a>'''
    if show_video:
        btns += f'''<a href="{video}" target="_blank" style="text-decoration:none;display:inline-block;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(220,53,69,0.7);border:2px solid #dc3545;color:#fff;font-weight:600;font-size:0.8rem;padding:6px 12px;border-radius:6px;cursor:pointer;transition:all 0.3s ease;letter-spacing:0.3px;box-shadow:0 4px 16px rgba(220,53,69,0.2);">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" style="margin-right:1px;"><polygon points="5,3 19,12 5,21" fill="currentColor"/></svg>
            Vidéo
        </div></a>'''
    
    btns_html = f'<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">{btns}</div>' if btns else ''

    # Carte professionnelle compacte avec transparence simple - Structure verticale
    html = (
        'display:flex;flex-direction:column;gap:12px;'
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:12px;'
        'padding:16px 20px;max-width:600px;margin:0 auto 1rem auto;'
        f'box-shadow:{THEME["glass_shadow"]};position:relative;'
        'transition: all 0.3s ease;'
    )
    
    # Conteneur du haut : Logo + Nom (alignement centré avec gap réduit)
    top_container = f'<div style="display:flex;align-items:center;justify-content:center;gap:10px;"><div style="flex-shrink:0;">{logo}</div><div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:0;">'
    top_container += f'<h2 style="font-size:1.4rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;word-break:break-word;text-align:center;">{name}</h2>'
    top_container += '</div></div>'
    
    # Conteneur du bas : Boutons
    bottom_container = f'<div style="display:flex;justify-content:center;width:100%;">{btns_html}</div>' if btns else ''
    
    card = f'<div style="{html}">{top_container}{bottom_container}</div>'
    
    st.markdown(_wrap_html(card, 600), unsafe_allow_html=True)

def render_section(title: str, bg: str = None):
    """
    Titre de section professionnel avec transparence simple pour présentation client.
    Args:
        title (str): Titre de la section.
        bg (str, optionnel): Couleur de fond (non utilisé).
    """
    # Utilisation de st.session_state pour garantir la robustesse du compteur même en cas de reload
    if 'section_count' not in st.session_state:
        st.session_state['section_count'] = 0
    st.session_state['section_count'] += 1
    
    # Espacement entre les sections
    if st.session_state['section_count'] > 1:
        st.markdown('<div style="margin:2rem 0 1.5rem 0;"></div>', unsafe_allow_html=True)
    
    # Titre de section professionnel avec transparence simple
    section_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:12px;'
        'padding:16px 24px;margin-bottom:1rem;text-align:center;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;'
        'position:relative;'
    )
    
    section_html = f'''
    <div style="{section_style}">
        <h3 style="margin:0;font-size:1.3rem;font-weight:700;color:#000;letter-spacing:-0.01em;">{title}</h3>
    </div>
    '''
    st.markdown(_wrap_html(section_html, 1000), unsafe_allow_html=True)

def reset_section_counter():
    """Réinitialise le compteur de section pour l'affichage harmonisé des titres de section."""
    st.session_state['section_count'] = 0

# --- Main Display ---
def display(df_ent: pd.DataFrame):
    # Appliquer les styles modernes à la sidebar
    apply_sidebar_styles()
    
    # Réinitialiser le compteur de section à chaque affichage (avant tout appel à render_section)
    reset_section_counter()
    
    # Sidebar: select company
    companies = df_ent['Entreprises'].dropna().unique()
    selected = st.sidebar.selectbox('Choisissez une entreprise', companies, key='select_entreprise')
    cookies['entreprise_selected'] = json.dumps([selected])
    info = df_ent[df_ent['Entreprises'] == selected].iloc[0]

    # Colors
    color = st.sidebar.color_picker('Couleur principale', THEME['accent'])

    # Style CSS pour un rendu professionnel avec transparence simple
    st.markdown("""
    <style>
    .main .block-container {
        background: linear-gradient(135deg, #e3f0fa 0%, #f8f9fa 50%, #e9ecef 100%);
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        position: relative;
        min-height: 100vh;
    }
    
    .main .block-container::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 25% 25%, rgba(0,114,178,0.05) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(227,240,250,0.08) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Transparence pour les éléments flottants */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 12px rgba(255,255,255,0.08) !important;
    }
    
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 12px rgba(0,114,178,0.08) !important;
    }
    
    .stColorPicker > div > div {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 12px rgba(0,114,178,0.08) !important;
    }
    
    /* Sidebar avec transparence */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.85) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header en haut de la page
    render_header('Fiche entreprise')
    
    # Ligne séparatrice fine après le header
    st.markdown(SEPARATOR, unsafe_allow_html=True)

    # Mise en page en deux colonnes : Informations générales à gauche, Contenu principal à droite
    col_left, col_right = st.columns([1, 1])
    
    # Colonne gauche : Informations générales
    with col_left:
        # Info Cards professionnelles avec transparence simple
        render_section('Informations générales')
        fields = [c for c in df_ent.columns if c not in ['Entreprises','Description','URL (logo)','URL (vidéo)']]
        selected_fields = st.sidebar.multiselect('Champs visibles', fields, default=fields[:4], key='fields_entreprise')
        
        # Conteneur professionnel pour les cartes avec transparence simple
        cards_container_style = (
            f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
            'padding:20px 24px;margin-bottom:1.5rem;'
            f'box-shadow:{THEME["glass_shadow"]};'
            'transition:all 0.3s ease;'
            'position:relative;'
            'overflow:hidden;'
        )
        
        cards = ''
        for i, f in enumerate(selected_fields):
            val = info.get(f, 'N/A')
            card_bg = THEME['glass_bg'] if i % 2 == 0 else THEME['glass_bg_blue']
            card_style = (
                f'background:{card_bg};border:1px solid {THEME["glass_border"]};border-radius:12px;'
                'padding:14px 18px;margin:0 0 12px 0;width:100%;'
                f'box-shadow:0 4px 16px rgba(0,114,178,0.12);transition:all 0.3s ease;'
                'position:relative;overflow:hidden;'
            )
            cards += f'''<div style="{card_style}">
                <strong style="font-size:0.9rem;font-weight:800;color:{THEME["primary"]};display:block;margin-bottom:6px;">{f}</strong>
                <div style="font-size:0.9rem;color:#000;font-weight:600;">{val}</div>
            </div>'''
        
        grid_section_html = f'''<div style="{cards_container_style}">
            <div style="display:flex;flex-direction:column;gap:0;width:100%;">{cards}</div>
        </div>'''
        st.markdown(grid_section_html, unsafe_allow_html=True)
    
    # Colonne droite : Logo/Nom, Description, Localisation
    with col_right:
        # Logo, nom, boutons dans la carte premium avec transparence simple
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
        render_logo_and_name(selected, info.get('URL (logo)', ''), color, url_site, video)

        # Ligne séparatrice fine entre le conteneur logo/nom/boutons et la section Description
        st.markdown(SEPARATOR, unsafe_allow_html=True)

        # Section Description avec transparence simple
        render_section('Description')
        desc = info.get('Description', '')
        if not isinstance(desc, str) or not desc.strip():
            desc = "Aucune description disponible."
        
        # Section Description professionnelle avec transparence simple
        desc_style = (
            f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
            'padding:20px 24px;margin-bottom:1.5rem;'
            f'box-shadow:{THEME["glass_shadow"]};'
            'transition:all 0.3s ease;'
            'position:relative;'
            'overflow:hidden;'
        )
        desc_html = f'''
        <div style="{desc_style}">
            <div style="font-size:0.95rem;line-height:1.5;color:#000;text-align:justify;border-left:4px solid {THEME["primary"]};padding-left:16px;font-weight:500;">{desc}</div>
        </div>
        '''
        st.markdown(desc_html, unsafe_allow_html=True)

        # Ligne séparatrice fine entre la description et la localisation
        st.markdown(SEPARATOR, unsafe_allow_html=True)
        
        # Carte de localisation améliorée avec transparence simple
        render_section('Localisation')
        addr = info.get('Localisation (Siège social)', '')
        
        with st.spinner('Géocodage de l\'adresse en cours...'):
            lat, lon = geocode(addr)
        
        if lat and lon:
            df_map = pd.DataFrame([{'lat': lat, 'lon': lon, 'name': 'Siège'}])
            layer = pdk.Layer(
                'ScatterplotLayer',
                df_map,
                get_position='[lon,lat]',
                get_radius=1000,
                get_color=[0,114,178],
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
            # Message d'erreur dans un conteneur avec transparence simple
            error_style = (
                'background:rgba(248, 215, 218, 0.8);border:1px solid rgba(220, 53, 69, 0.4);border-radius:12px;'
                'padding:16px 24px;margin-bottom:1.5rem;text-align:center;'
                'box-shadow:0 4px 16px rgba(220, 53, 69, 0.15);'
                'transition:all 0.3s ease;'
                'position:relative;'
                'overflow:hidden;'
            )
            error_html = f'''
            <div style="{error_style}">
                <p style="margin:0;font-size:1rem;color:#000;font-weight:600;">Adresse non géocodée ou introuvable. Merci de vérifier l'adresse saisie.</p>
            </div>
            '''
            st.markdown(error_html, unsafe_allow_html=True)
