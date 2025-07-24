# Valeur par défaut pour les champs vides
LABEL_INFO_VALEUR_PAR_DEFAUT = "N/A"
import streamlit as st
from sidebar import show_sidebar
import pandas as pd
import pydeck as pdk
import json
import requests
import io
from geopy.geocoders import Nominatim

"""
=== CONSTANTES GLOBALES (labels, colonnes, messages, titres, etc.) ===
"""
LABEL_ENTREPRISES = "Entreprises"
LABEL_DESCRIPTION = "Description"
LABEL_URL_LOGO = "URL (logo)"
LABEL_URL_VIDEO = "URL (vidéo)"
LABEL_LOGO = "Logo"
LABEL_SITE_WEB = "Site web"
LABEL_LOCALISATION = "Localisation (Siège social)"
LABEL_FICHE_ENTREPRISE = "Fiche entreprise"
LABEL_CHAMPS_VISIBLES = "Champs visibles"
LABEL_COULEUR_PRINCIPALE = "Couleur principale"
LABEL_CHOISISSEZ_ENTREPRISE = "Choisissez une entreprise"
LABEL_AUCUNE_DESCRIPTION = "Aucune description disponible."
LABEL_AUCUNE_LOCALISATION = "Aucune colonne de localisation trouvée dans les données."
LABEL_ADRESSE_NON_GEOCODEE = "Adresse non géocodée ou introuvable. Merci de vérifier l'adresse saisie."
LABEL_INFOS_GENERALES = "Informations générales"
LABEL_LOCALISATION_SECTION = "Localisation"
LABEL_SIEGE_SOCIAL = "Siège social"
LABEL_NA = "N/A"
LABEL_LOGO_FALLBACK = "Logo"
LABEL_BOUTON_VIDEO = "Vidéo"
LABEL_BOUTON_VOIR_LOGO = "Voir le logo sur SharePoint"
LABEL_LOGO_NON_AFFICHE = "Le logo n'a pu être affiché directement."
LOGO_CAPTION = "Logo de l'entreprise"
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
SEPARATOR = '<div style="margin:0.8rem 0;border-bottom:1px solid rgba(0,0,0,0.1);"></div>'

# --- Caching Geocoder ---
from geopy.extra.rate_limiter import RateLimiter

@st.cache_data(show_spinner=False)
def geocode(address: str):
    import time
    try:
        geolocator = Nominatim(user_agent="entreprise_app")
        # Timeout fixé à 5 secondes
        start = time.time()
        geocode_sync = RateLimiter(lambda addr: geolocator.geocode(addr), min_delay_seconds=1)
        loc = geocode_sync(address)
        elapsed = time.time() - start
        if elapsed > 5 or loc is None:
            return (None, None)
        return (loc.latitude, loc.longitude)
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
    card = f'''
    <div style="background:{THEME['glass_bg']};border:1px solid {THEME['glass_border']};border-radius:14px;padding:18px 20px;margin-bottom:1rem;box-shadow:{THEME['glass_shadow']};display:flex;flex-direction:column;align-items:center;gap:10px;">
        <div style="display:flex;align-items:center;justify-content:center;gap:10px;">
            {logo}
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:0;">
                <h2 style="font-size:1.7rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;word-break:break-word;text-align:center;">{name}</h2>
            </div>
        </div>
        {btns_html}
    </div>
    '''
    st.markdown(_wrap_html(card, 600), unsafe_allow_html=True)

from typing import Optional

def render_section(title: str, bg: Optional[str] = None):
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
    
    # Espacement réduit entre les sections
    if st.session_state['section_count'] > 1:
        st.markdown('<div style="margin:1rem 0 0.5rem 0;"></div>', unsafe_allow_html=True)
    
    # Titre de section professionnel avec transparence simple
    section_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:12px;'
        'padding:12px 20px;margin-bottom:0.8rem;text-align:center;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;'
        'position:relative;'
    )
    
    section_html = f'''
    <div style="{section_style}">
        <h3 style="margin:0;font-size:1.6rem;font-weight:700;color:#000;letter-spacing:-0.01em;">{title}</h3>
    </div>
    '''
    st.markdown(_wrap_html(section_html, 1000), unsafe_allow_html=True)

def reset_section_counter():
    """Réinitialise le compteur de section pour l'affichage harmonisé des titres de section."""
    st.session_state['section_count'] = 0

# --- Fonctions d'aide pour la section Logo (sorties de render_logo_section) ---

def is_valid_logo(logo_img):
    # Exclure les valeurs nulles, nan
    if logo_img is None or pd.isna(logo_img):
        return False
    
    # Accepter les images binaires (bytes) extraites d'Excel
    if isinstance(logo_img, bytes):
        return True
    
    # Convertir en string pour vérification
    str_val = str(logo_img).strip()
    
    # Exclure les chaînes d'erreur Excel ou vides
    if str_val.lower() in ['#value!', '#name?', '#ref!', '#div/0!', '#num!', '#null!', 'nan', '']:
        return False
    
    # Accepter les liens SharePoint ou chemins Windows
    if str_val.startswith(('https://', 'http://', 'C:\\')):
        return True
    
    # Exclure les valeurs numériques simples (0, 1, etc.)
    if str_val.isdigit():
        return False
    
    # Accepter toute autre valeur string non vide
    return True

def download_and_display_image(url):
    """
    Tente de télécharger une image depuis une URL et de l'afficher.
    Retourne True si l'affichage réussit, False sinon.
    """
    try:
        download_url = url
        # Si c'est un lien de partage SharePoint, on le transforme en lien de téléchargement direct
        if 'sharepoint.com' in url and '?e=' in url:
            download_url = url + '&download=1'
        
        # Certains liens SharePoint nécessitent un user-agent pour fonctionner
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(download_url, headers=headers, stream=True, timeout=10)
        
        content_type = response.headers.get('Content-Type', '')
        if response.status_code == 200 and 'image' in content_type:
            image_bytes = io.BytesIO(response.content)
            st.image(image_bytes, width=150, caption=LOGO_CAPTION)
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False

def try_display_image(img_src):
    
    if 'sharepoint.com' in str(img_src):
        
        # Tenter de télécharger et d'afficher l'image
        if download_and_display_image(img_src):
            return True
        
        # Si le téléchargement échoue, afficher le lien cliquable comme solution de secours
        try:
            st.markdown(f'''
                <div style="border:1px solid #ddd; border-radius:8px; padding:15px; text-align:center; background-color:#f9f9f9; margin-top: 10px;">
                    <p style="margin-bottom:12px; font-size:0.9rem; color:#333;">Le logo n'a pu être affiché directement.</p>
                    <a href="{img_src}" target="_blank" style="display: inline-block; color: #fff; background-color: #0072B2; text-decoration: none; font-weight: bold; padding: 8px 16px; border-radius: 5px;">
                        🔗 Voir le logo sur SharePoint
                    </a>
                </div>
            ''', unsafe_allow_html=True)
            return True
        except Exception as e:
            return False
    try:
        st.image(img_src, width=120, caption=LOGO_CAPTION, use_container_width=False)
        return True
    except Exception as e:
        return False

def extract_url_from_text(text):
    import re
    patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        r'C:\\[^\s<>"{}|^`\[\]]+'
    ]
    for pattern in patterns:
        url_match = re.search(pattern, text)
        if url_match:
            url = url_match.group()
            return url
    return None

def display_logo_from_str(logo_str):
    if logo_str.startswith(('https://', 'http://', 'C:\\')):
        return try_display_image(logo_str)
    if 'http' in logo_str.lower():
        extracted_url = extract_url_from_text(logo_str)
        if extracted_url:
            return try_display_image(extracted_url)
    return False

def display_logo_from_object(logo_img):
    if isinstance(logo_img, bytes):
        try:
            st.image(logo_img, width=150, caption=LOGO_CAPTION)
            return True
        except Exception as e:
            return False
    
    # Cas 2: Objet avec méthode read() (file-like object)
    if hasattr(logo_img, 'read'):
        return try_display_image(logo_img)
    
    # Cas 3: Bytearray
    if isinstance(logo_img, bytearray):
        return try_display_image(logo_img)
    
    # Cas 4: PIL Image (si disponible)
    try:
        from PIL import Image
        if isinstance(logo_img, Image.Image):
            return try_display_image(logo_img)
    except ImportError:
        pass
    
    return False

def display_logo(logo_img):
    # D'abord, vérifier si c'est une image binaire (bytes) extraite d'Excel
    if isinstance(logo_img, bytes):
        return display_logo_from_object(logo_img)
    
    # Ensuite, traiter comme une chaîne de caractères (URL, chemin, etc.)
    logo_str = str(logo_img).strip()
    
    # Ignorer complètement les erreurs Excel
    if logo_str in ['#VALUE!', '#NAME?', '#REF!', '#DIV/0!', '#NUM!', '#NULL!']:
        return False
    
    if logo_str.isdigit() and logo_str in ['0', '1']:
        return False
    
    if not is_valid_logo(logo_img):
        return False
    
    if display_logo_from_str(logo_str):
        return True
    
    return display_logo_from_object(logo_img)

# --- Main Display ---
def sidebar_setup(df_ent):
    companies = df_ent[LABEL_ENTREPRISES].dropna().unique()
    selected = st.sidebar.selectbox(LABEL_CHOISISSEZ_ENTREPRISE, companies, key='select_entreprise')
    cookies['entreprise_selected'] = json.dumps([selected])
    info = df_ent[df_ent[LABEL_ENTREPRISES] == selected].iloc[0]
    color = st.sidebar.color_picker(LABEL_COULEUR_PRINCIPALE, THEME['accent'])
    fields = [c for c in df_ent.columns if c not in [LABEL_ENTREPRISES, LABEL_DESCRIPTION, LABEL_URL_LOGO, LABEL_URL_VIDEO, LABEL_LOGO]]
    selected_fields = st.sidebar.multiselect(LABEL_CHAMPS_VISIBLES, fields, default=fields[:4], key='fields_entreprise')
    return selected, info, color, selected_fields

def render_left_column(info, selected_fields):
    render_section(LABEL_INFOS_GENERALES)
    cards_container_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
        'padding:16px 20px;margin-bottom:1rem;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;'
        'position:relative;'
        'overflow:hidden;'
    )
    cards = ''
    for i, f in enumerate(selected_fields):
        val = info.get(f, LABEL_NA)
        card_bg = THEME['glass_bg'] if i % 2 == 0 else THEME['glass_bg_blue']
        card_style = (
            f'background:{card_bg};border:1px solid {THEME["glass_border"]};border-radius:12px;'
            'padding:14px 18px;margin:0 0 12px 0;width:100%;'
            f'box-shadow:0 4px 16px rgba(0,114,178,0.12);transition:all 0.3s ease;'
            'position:relative;overflow:hidden;'
        )
        cards += f'''<div style="{card_style}">
            <strong style="font-size:1.0rem;font-weight:700;color:{THEME["primary"]};display:block;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">{f}</strong>
            <div style="font-size:1.3rem;color:#000;font-weight:600;line-height:1.3;">{val}</div>
        </div>'''
    grid_section_html = f'''<div style="{cards_container_style}">
        <div style="display:flex;flex-direction:column;gap:0;width:100%;">{cards}</div>
    </div>'''
    st.markdown(grid_section_html, unsafe_allow_html=True)

def get_url_site(info):
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
    return url_site

def render_logo_section(selected, info, color, url_site, video):
    # Affichage horizontal : logo à gauche, nom à droite, boutons en dessous
    logo_url = info.get(LABEL_URL_LOGO, None)
    logo_html = ''
    if isinstance(logo_url, str) and logo_url.startswith(('http://', 'https://')):
        logo_html = f"<img src='{logo_url}' width='80' style='border-radius:8px;box-shadow:0 2px 8px rgba(0,114,178,0.08);' alt='{LOGO_CAPTION}'/>"
    else:
        logo_html = f"<div style='width:80px;height:80px;border-radius:8px;background:{THEME['glass_bg']};border:1px solid {THEME['glass_border']};display:flex;align-items:center;justify-content:center;color:#000;font-size:14px;font-weight:600;box-shadow:{THEME['glass_shadow']};'>{LABEL_LOGO_FALLBACK}</div>"

    name_html = f"<div style='display:flex;flex-direction:column;justify-content:center;'><h2 style='font-size:1.4rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;text-align:center;'>{selected}</h2></div>"

    # Boutons centrés (site web et/ou vidéo)
    btns = []
    if isinstance(url_site, str) and url_site.strip() and url_site.strip().lower() not in ['-', 'nan', 'aucun', 'none']:
        btns.append(f'''<a href="{url_site}" target="_blank" style="text-decoration:none;display:inline-block;margin-right:8px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:{THEME['glass_bg']};border:2px solid {THEME['primary']};color:#000;font-weight:600;font-size:0.8rem;padding:6px 12px;border-radius:6px;cursor:pointer;transition:all 0.3s ease;letter-spacing:0.3px;box-shadow:{THEME['glass_shadow']};">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="margin-right:1px;vertical-align:middle;"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 0 20M12 2a15.3 15.3 0 0 0 0 20" stroke="currentColor" stroke-width="2" fill="none"/></svg>
            {LABEL_SITE_WEB}
        </div></a>''')
    # Affichage du bouton vidéo YouTube même si le site web n'est pas présent
    if isinstance(video, str) and video.strip() and video.strip().lower() not in ['-', 'nan', 'aucun', 'none']:
        # On vérifie que c'est bien une URL YouTube
        video_url = video.strip()
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            btns.append(f'''<a href="{video_url}" target="_blank" style="text-decoration:none;display:inline-block;">
            <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(220,53,69,0.7);border:2px solid #dc3545;color:#fff;font-weight:600;font-size:0.8rem;padding:6px 12px;border-radius:6px;cursor:pointer;transition:all 0.3s ease;letter-spacing:0.3px;box-shadow:0 4px 16px rgba(220,53,69,0.2);">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="margin-right:1px;vertical-align:middle;"><rect x="2" y="6" width="20" height="12" rx="3" fill="#dc3545"/><polygon points="10,9 16,12 10,15" fill="#fff"/></svg>
                Vidéo
            </div></a>''')

    btns_html = '<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;justify-content:center;width:100%;">' + ''.join(btns) + '</div>' if btns else ''

    st.markdown(f"""
    <div style='display:flex;flex-direction:column;align-items:center;width:100%;'>
        <div style='display:flex;align-items:center;justify-content:center;gap:18px;margin-bottom:8px;width:100%;'>
            {logo_html}
            {name_html}
        </div>
        {btns_html}
    </div>
    """, unsafe_allow_html=True)

def render_description_section(info):
    render_section(LABEL_DESCRIPTION)
    desc = info.get(LABEL_DESCRIPTION, '')
    if not isinstance(desc, str) or not desc.strip():
        desc = LABEL_AUCUNE_DESCRIPTION
    desc_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
        'padding:16px 20px;margin-bottom:1rem;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;'
        'position:relative;'
        'overflow:hidden;'
    )
    desc_html = f'''
    <div style="{desc_style}">
        <div style="font-size:1.1rem;line-height:1.5;color:#000;text-align:justify;border-left:4px solid {THEME["primary"]};padding-left:16px;font-weight:500;">{desc}</div>
    </div>
    '''
    st.markdown(desc_html, unsafe_allow_html=True)

def render_map_section(info):
    render_section('Localisation')
    
    # Trouver toutes les colonnes qui commencent par "localisation" ou "Localisation"
    location_columns = [col for col in info.index if col.lower().startswith('localisation')]
    
    # Si aucune colonne trouvée, essayer quelques variantes communes
    if not location_columns:
        # Chercher des colonnes avec "localisation" n'importe où dans le nom
        location_columns = [col for col in info.index if 'localisation' in col.lower()]
    
    # Si toujours aucune colonne, utiliser l'ancienne méthode avec une colonne spécifique
    if not location_columns:
        # Fallback vers la méthode originale
        addr = info.get(LABEL_LOCALISATION, '')
        if addr and str(addr).strip() and str(addr).strip().lower() != 'nan':
            with st.spinner('Géocodage de l\'adresse en cours...'):
                lat, lon = geocode(str(addr))
                if lat and lon:
                    df_map = pd.DataFrame([{'lat': lat, 'lon': lon, 'name': 'Siège social', 'address': str(addr)}])
                    layer = pdk.Layer(
                        'ScatterplotLayer',
                        df_map,
                        get_position='[lon,lat]',
                        get_radius=8000,  # Rayon fixe plus grand
                        get_color=[0,114,178],
                        pickable=True
                    )
                    view = pdk.ViewState(latitude=lat, longitude=lon, zoom=10)  # Augmenté de 7 à 10
                    deck = pdk.Deck(
                        initial_view_state=view,
                        layers=[layer],
                        tooltip={"text": "{name} : {address}"},  # type: ignore[arg-type]
                    )
                    st.pydeck_chart(deck, use_container_width=True)
                    return
        
        # Si aucune adresse trouvée, afficher un message d'erreur
        error_style = (
            'background:rgba(248, 215, 218, 0.8);border:1px solid rgba(220, 53, 69, 0.4);border-radius:12px;'
            'padding:12px 20px;margin-bottom:1rem;text-align:center;'
            'box-shadow:0 4px 16px rgba(220, 53, 69, 0.15);'
            'transition:all 0.3s ease;'
            'position:relative;'
            'overflow:hidden;'
        )
        error_html = f'''
        <div style="{error_style}">
            <p style="margin:0;font-size:1.1rem;color:#000;font-weight:600;">{LABEL_AUCUNE_LOCALISATION}</p>
        </div>
        '''
        st.markdown(error_html, unsafe_allow_html=True)
        return
    
    # Traitement des colonnes de localisation trouvées
    map_data = []
    
    # Géocoder toutes les adresses de localisation
    for col in location_columns:
        addr = info.get(col, '')
        if addr and str(addr).strip() and str(addr).strip().lower() not in ['nan', 'n/a', '-', '']:
            with st.spinner(f'Géocodage de {col} en cours...'):
                lat, lon = geocode(str(addr))
                if lat and lon:
                    # Créer un nom court pour la colonne
                    name = col.replace('Localisation', '').replace('(', '').replace(')', '').strip()
                    if not name:
                        name = "Localisation"
                    map_data.append({'lat': lat, 'lon': lon, 'name': name, 'address': str(addr)})
    
    if map_data:
        df_map = pd.DataFrame(map_data)
        
        # Ajouter des couleurs différentes pour chaque point
        colors = [
            [0, 114, 178, 200],      # Bleu IVEO
            [220, 53, 69, 200],      # Rouge
            [40, 167, 69, 200],      # Vert
            [255, 193, 7, 200],      # Jaune
            [108, 117, 125, 200],    # Gris
            [111, 66, 193, 200],     # Violet
            [255, 87, 51, 200],      # Orange
            [23, 162, 184, 200],     # Cyan
        ]
        
        # Assigner une couleur à chaque point
        df_map['color'] = [colors[i % len(colors)] for i in range(len(df_map))]
        
        layer = pdk.Layer(
            'ScatterplotLayer',
            df_map,
            get_position='[lon,lat]',
            get_radius=8000,  # Rayon fixe plus grand
            get_fill_color='color',
            pickable=True
        )
        
        # Centrer la carte sur la première localisation au lieu de la moyenne
        center_lat = df_map['lat'].iloc[0]
        center_lon = df_map['lon'].iloc[0]
        
        view = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=7)  # Réduit de 10 à 7 pour éviter le zoom trop proche
        deck = pdk.Deck(
            initial_view_state=view,
            layers=[layer],
            # ignore incorrect type stub for tooltip dict
            tooltip={
                "html": "<b>📍 {name}</b><br/><b>Adresse:</b> {address}<br/><b>Coordonnées:</b> {lat:.4f}, {lon:.4f}",
                "style": {"backgroundColor": "rgba(255, 255, 255, 0.95)", "color": "black", "padding": "10px", "borderRadius": "8px", "boxShadow": "0 4px 16px rgba(0,0,0,0.2)"}
            },  # type: ignore[arg-type]
        )
        st.pydeck_chart(
            deck,
            use_container_width=True
        )
    else:
        error_style = (
            'background:rgba(248, 215, 218, 0.8);border:1px solid rgba(220, 53, 69, 0.4);border-radius:12px;'
            'padding:12px 20px;margin-bottom:1rem;text-align:center;'
            'box-shadow:0 4px 16px rgba(220, 53, 69, 0.15);'
            'transition:all 0.3s ease;'
            'position:relative;'
            'overflow:hidden;'
        )
        error_html = f'''
        <div style="{error_style}">
            <p style="margin:0;font-size:1.1rem;color:#000;font-weight:600;">{LABEL_ADRESSE_NON_GEOCODEE}</p>
        </div>
        '''
        st.markdown(error_html, unsafe_allow_html=True)

def display(df_ent: pd.DataFrame):
    apply_sidebar_styles()
    reset_section_counter()
    # Sélection globale d'entreprise(s)
    if df_ent is None or df_ent.empty or LABEL_ENTREPRISES not in df_ent.columns:
        st.error("Aucune donnée d'entreprise disponible.")
        return
    entreprises = df_ent[LABEL_ENTREPRISES].dropna().unique().tolist()
    selected = show_sidebar(
        label=LABEL_CHOISISSEZ_ENTREPRISE,
        options=entreprises,
        default=entreprises[:1],
        multiselect=False
    )
    # Nettoyage du nom sélectionné pour enlever crochets et quotes
    def clean_name(val):
        import re
        if isinstance(val, list) and val:
            val = val[0]
        val = str(val)
        val = re.sub(r"^\[|'|\"|\[|\]$", "", val)
        val = val.strip("[]'")
        return val
    clean_selected = clean_name(selected)
    # Filtrer le DataFrame selon la sélection
    info = df_ent[df_ent[LABEL_ENTREPRISES].isin([clean_selected])].iloc[0] if clean_selected else df_ent.iloc[0]
    color = THEME['accent']
    # Champs visibles : tous les champs non vides pour l'entreprise sélectionnée
    general_fields = [c for c in df_ent.columns if c != LABEL_ENTREPRISES and c.lower() not in ['description','url (logo)','url (vidéo)','website','site web'] and not c.lower().startswith('description') and not c.lower().startswith('url')]
    # On sélectionne par défaut tous les champs non vides pour l'entreprise sélectionnée
    default_fields = [f for f in general_fields if pd.notna(info.get(f, None)) and str(info.get(f, '')).strip() and str(info.get(f, '')).lower() not in ['nan', 'n/a', '-', '']]
    # Multiselect juste après le choix d'entreprise
    selected_fields = st.sidebar.multiselect(LABEL_CHAMPS_VISIBLES, general_fields, default=default_fields, key='fields_entreprise')
    st.sidebar.color_picker(LABEL_COULEUR_PRINCIPALE, THEME['accent'])
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
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.85) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    render_header(LABEL_FICHE_ENTREPRISE)
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    # Affichage description à gauche, logo/nom à droite
    col_desc, col_logo = st.columns([1, 1])
    with col_desc:
        render_description_section(info)
    with col_logo:
        url_site = get_url_site(info)
        video = info.get('URL (vidéo)', '')
        render_logo_section(clean_selected, info, color, url_site, video)
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    # Affichage des autres informations en bas, centrées
    render_section(LABEL_INFOS_GENERALES)
    info_items = []
    for f in selected_fields:
        val = info.get(f, LABEL_INFO_VALEUR_PAR_DEFAUT)
        if pd.notna(val) and str(val).strip() and str(val).lower() not in ['nan', 'n/a', '-', '']:
            info_items.append((f, val))
    card_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:12px;'
        'padding:14px 18px;margin:0 0 12px 0;width:100%;'
        f'box-shadow:0 4px 16px rgba(0,114,178,0.12);transition:all 0.3s ease;'
        'position:relative;overflow:hidden;'
    )
    def render_card(f, val):
        return f'''<div style="{card_style}">
            <strong style="font-size:1.0rem;font-weight:700;color:{THEME['primary']};display:block;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">{f}</strong>
            <div style="font-size:1.3rem;color:#000;font-weight:600;line-height:1.3;">{val}</div>
        </div>'''
    if info_items:
        if len(info_items) == 1:
            f, val = info_items[0]
            html = f"<div style='display:flex;justify-content:center;width:100%;'>{render_card(f, val)}</div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, (f, val) in enumerate(info_items):
                with cols[i % 2]:
                    st.markdown(render_card(f, val), unsafe_allow_html=True)
        # Section localisation supprimée
