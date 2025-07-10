import streamlit as st
import pandas as pd
import pydeck as pdk
import json
from geopy.geocoders import Nominatim
from sidebar import cookies, apply_sidebar_styles

# Version: 2025.01.10 - Page Solution compacte avec gestion d'images - Design identique à Entreprise
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
        loc = Nominatim(user_agent="solution_app").geocode(address)
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
        name (str): Nom de la solution.
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
            <img src='{logo_url}' width='48' style='border-radius:4px;max-width:100%;max-height:100%;object-fit:contain;' alt='Logo solution'/>
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

def render_image_section(images_urls: list, uploaded_image=None):
    """
    Section d'affichage des images avec transparence simple.
    Args:
        images_urls (list): Liste des URLs d'images.
        uploaded_image: Fichier image uploadé via Streamlit.
    """
    # Vérifier s'il y a des images à afficher
    has_url_images = images_urls and any(img.strip() for img in images_urls if isinstance(img, str) and img.strip().lower() not in ['-', 'nan', 'aucun', 'none', 'uploaded_file'])
    has_uploaded_image = uploaded_image is not None
    
    # Si aucune image, ne pas afficher la section
    if not has_url_images and not has_uploaded_image:
        return
    
    # Conteneur pour les images
    images_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
        'padding:20px 24px;margin-bottom:1.5rem;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;'
        'position:relative;'
        'overflow:hidden;'
    )
    
    # Générer les images URL
    images_html = ''
    for img_url in images_urls:
        if isinstance(img_url, str) and img_url.strip() and img_url.strip().lower() not in ['-', 'nan', 'aucun', 'none', 'uploaded_file']:
            if img_url.startswith('http'):
                images_html += f'''
                <div style="margin-bottom:20px;text-align:center;">
                    <div style="font-size:0.9rem;color:{THEME["primary"]};font-weight:600;margin-bottom:8px;">Image depuis URL</div>
                    <img src="{img_url}" style="max-width:100%;max-height:400px;object-fit:contain;border-radius:12px;box-shadow:0 6px 20px rgba(0,114,178,0.2);border:2px solid rgba(0,114,178,0.1);" alt="Image solution"/>
                </div>
                '''
    
    # Afficher le conteneur HTML s'il y a des images URL
    if images_html:
        section_html = f'''
        <div style="{images_style}">
            {images_html}
        </div>
        '''
        st.markdown(section_html, unsafe_allow_html=True)
    
    # Afficher l'image uploadée avec Streamlit dans un conteneur stylé
    if uploaded_image is not None:
        
        
        # Afficher l'image dans un conteneur avec bordure arrondie
        st.markdown(f'''
        <div style="{images_style}">
        ''', unsafe_allow_html=True)
        
        # Utiliser des colonnes pour centrer l'image
        _, col2, _ = st.columns([1, 3, 1])
        with col2:
            st.image(
                uploaded_image, 
                use_container_width=True, 
                caption=uploaded_image.name,
                output_format="auto"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

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
def display(df_sol: pd.DataFrame):
    # Appliquer les styles modernes à la sidebar
    apply_sidebar_styles()
    
    # Réinitialiser le compteur de section à chaque affichage (avant tout appel à render_section)
    reset_section_counter()
    
    # Vérifier si le DataFrame contient des données
    if df_sol.empty:
        st.error("Aucune donnée de solution disponible.")
        return
    
    # Sidebar - Sélection de la solution
    solution_column = None
    for col in df_sol.columns:
        if 'solution' in col.lower():
            solution_column = col
            break
    
    if not solution_column:
        st.error("Aucune colonne 'Solutions' trouvée dans les données.")
        return
    
    solutions = df_sol[solution_column].dropna().unique()
    if len(solutions) == 0:
        st.error("Aucune solution disponible dans les données.")
        return
    
    selected = st.sidebar.selectbox('Choisissez une solution', solutions, key='select_solution')
    cookies['solution_selected'] = json.dumps([selected])
    info = df_sol[df_sol[solution_column] == selected].iloc[0]

    # Colors
    color = st.sidebar.color_picker('Couleur principale', THEME['accent'])
    
    # Champ pour ajouter une image
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Ajouter une image**")
    
    # Option 1: URL d'image
    image_url = st.sidebar.text_input(
        "URL de l'image",
        placeholder="https://exemple.com/image.jpg",
        key='custom_image_url'
    )
    
    # Option 2: Upload d'image
    uploaded_image = st.sidebar.file_uploader(
        "Télécharger une image",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
        key='uploaded_image'
    )

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
    
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 12px rgba(0,114,178,0.08) !important;
    }
    
    .stFileUploader > div > div {
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
    render_header('Fiche solution')
    
    # Ligne séparatrice fine après le header
    st.markdown(SEPARATOR, unsafe_allow_html=True)

    # Vérifier s'il y a des images à afficher pour adapter la disposition
    image_fields = [key for key in info.keys() if 'image' in key.lower() or 'photo' in key.lower() or 'screenshot' in key.lower()]
    images_urls = []
    
    # Ajouter les images des champs Excel
    for field in image_fields:
        img_url = info.get(field, '')
        if isinstance(img_url, str) and img_url.strip():
            images_urls.append(img_url.strip())
    
    # Ajouter l'image personnalisée si fournie (URL)
    if image_url and image_url.strip():
        images_urls.append(image_url.strip())
    
    # Ajouter l'image uploadée si fournie
    if uploaded_image is not None:
        images_urls.append('uploaded_file')
    
    has_images = bool(images_urls) or uploaded_image is not None

    # Mise en page en deux colonnes : Description + Informations générales à gauche, Nom + Images à droite
    col_left, col_right = st.columns([1, 1])
    
    # Colonne gauche : Description puis Informations générales
    with col_left:
        # Section Description avec transparence simple
        render_section('Description')
        
        # Recherche de la colonne Description (commence par "Description")
        desc_column = None
        for col in df_sol.columns:
            if col.lower().startswith('description'):
                desc_column = col
                break
        
        desc = ''
        if desc_column:
            desc = info.get(desc_column, '')
        
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

        # Ligne séparatrice fine entre la description et les informations générales
        st.markdown(SEPARATOR, unsafe_allow_html=True)

        # Info Cards professionnelles avec transparence simple
        render_section('Informations générales')
        fields = [c for c in df_sol.columns if c != solution_column and c.lower() not in ['description','url (logo)','url (vidéo)','website','site web']]
        selected_fields = st.sidebar.multiselect('Champs visibles', fields, default=fields[:4], key='fields_solution')
        
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
            if pd.notna(val) and str(val).strip():
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
        
        if cards:
            grid_section_html = f'''<div style="{cards_container_style}">
                <div style="display:flex;flex-direction:column;gap:0;width:100%;">{cards}</div>
            </div>'''
            st.markdown(grid_section_html, unsafe_allow_html=True)
    
    # Colonne droite : Nom/Logo puis Images (si présentes)
    with col_right:
        # Nom et boutons dans la carte premium avec transparence simple
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
        # Nom de la solution uniquement (sans logo)
        name_style = (
            'display:flex;flex-direction:column;gap:12px;'
            f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:12px;'
            'padding:16px 20px;max-width:600px;margin:0 auto 1rem auto;'
            f'box-shadow:{THEME["glass_shadow"]};position:relative;'
            'transition: all 0.3s ease;'
        )
        
        # Nom de la solution centré
        name_html = f'''
        <div style="{name_style}">
            <h2 style="font-size:1.4rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;text-align:center;">{selected}</h2>
        </div>
        '''
        
        st.markdown(_wrap_html(name_html, 600), unsafe_allow_html=True)

        # Section Images (si présentes) - Priorité visuelle
        if has_images:
            # Ligne séparatrice fine entre le nom/logo et les images
            st.markdown(SEPARATOR, unsafe_allow_html=True)
            
            render_section('Images')
            render_image_section(images_urls, uploaded_image)

    # Sections techniques et localisation en pleine largeur sous les deux colonnes
    # Section Caractéristiques techniques
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    render_section('Caractéristiques techniques')
    
    # Vérifier s'il y a des informations techniques spécifiques à afficher
    tech_fields = [key for key in info.keys() if any(word in key.lower() for word in ['technologie', 'version', 'compatibilité', 'système', 'plateforme', 'api', 'technique', 'tech'])]
    
    if tech_fields:
        tech_style = (
            f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
            'padding:20px 24px;margin-bottom:1.5rem;'
            f'box-shadow:{THEME["glass_shadow"]};'
            'transition:all 0.3s ease;'
            'position:relative;'
            'overflow:hidden;'
        )
        
        tech_content = ''
        for field in tech_fields[:3]:  # Limiter à 3 champs techniques
            val = info.get(field, 'N/A')
            if pd.notna(val) and str(val).strip():
                tech_content += f'<div style="margin-bottom:12px;"><strong style="color:{THEME["primary"]};font-size:0.9rem;">{field}:</strong> <span style="color:#000;font-size:0.9rem;">{val}</span></div>'
        
        if tech_content:
            tech_html = f'''
            <div style="{tech_style}">
                {tech_content}
            </div>
            '''
            st.markdown(tech_html, unsafe_allow_html=True)
        else:
            # Message si pas d'informations techniques valides
            info_style = (
                'background:rgba(227, 240, 250, 0.8);border:1px solid rgba(0, 114, 178, 0.3);border-radius:12px;'
                'padding:16px 24px;margin-bottom:1.5rem;text-align:center;'
                'box-shadow:0 4px 16px rgba(0, 114, 178, 0.1);'
                'transition:all 0.3s ease;'
                'position:relative;'
                'overflow:hidden;'
            )
            info_html = f'''
            <div style="{info_style}">
                <p style="margin:0;font-size:1rem;color:#000;font-weight:600;">Aucune caractéristique technique spécifique disponible.</p>
            </div>
            '''
            st.markdown(info_html, unsafe_allow_html=True)
    else:
        # Message si pas d'informations techniques
        info_style = (
            'background:rgba(227, 240, 250, 0.8);border:1px solid rgba(0, 114, 178, 0.3);border-radius:12px;'
            'padding:16px 24px;margin-bottom:1.5rem;text-align:center;'
            'box-shadow:0 4px 16px rgba(0, 114, 178, 0.1);'
            'transition:all 0.3s ease;'
            'position:relative;'
            'overflow:hidden;'
        )
        info_html = f'''
        <div style="{info_style}">
            <p style="margin:0;font-size:1rem;color:#000;font-weight:600;">Aucune caractéristique technique spécifique disponible.</p>
        </div>
        '''
        st.markdown(info_html, unsafe_allow_html=True)

    # Section Localisation (si des données de localisation existent)
    location_fields = [key for key in info.keys() if any(word in key.lower() for word in ['localisation', 'adresse', 'siège', 'address', 'location'])]
    
    if location_fields:
        # Ligne séparatrice fine entre les caractéristiques techniques et la localisation
        st.markdown(SEPARATOR, unsafe_allow_html=True)
        
        # Carte de localisation améliorée avec transparence simple
        render_section('Localisation')
        
        # Prendre le premier champ de localisation trouvé
        addr = info.get(location_fields[0], '')
        
        if isinstance(addr, str) and addr.strip() and addr.strip().lower() not in ['-', 'nan', 'aucun', 'none']:
            with st.spinner('Géocodage de l\'adresse en cours...'):
                lat, lon = geocode(addr)
            
            if lat and lon:
                df_map = pd.DataFrame([{'lat': lat, 'lon': lon, 'name': 'Localisation'}])
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
