"""
Page Solution - Application IVÉO BI
===================================

Cette page affiche les détails d'une solution sélectionnée avec une interface moderne, 
compacte et harmonisée avec la charte graphique IVÉO.

Fonctionnalités principales :
- Affichage des informations de solution en colonnes adaptatives
- Support multi-images avec persistance (URLs et uploads)
- Gestion des images sauvegardées avec suppression individuelle
- Design responsive et moderne
- Sections techniques et de localisation

Architecture du code :
- Fonction display() principale refactorisée pour la maintenabilité
- Fonctions helper spécialisées pour chaque fonctionnalité
- Gestion d'erreurs et validation des données
- Styles CSS intégrés et cohérents

Auteurs : Équipe IVÉO
Version : 3.0 (Refactorisée - 2025.01.10)
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import os
import hashlib
import time
from pathlib import Path
from geopy.geocoders import Nominatim
from sidebar import cookies, apply_sidebar_styles

# Version: 2025.01.10 - Page Solution compacte avec gestion d'images - Design identique à Entreprise

# --- Configuration pour la persistance des images ---
UPLOAD_DIR = Path("uploads/user_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_image(uploaded_file, solution_name):
    """
    Sauvegarde une image uploadée et retourne le chemin relatif.
    Args:
        uploaded_file: Fichier uploadé via Streamlit
        solution_name: Nom de la solution pour organiser les fichiers
    Returns:
        str: Chemin relatif vers le fichier sauvegardé
    """
    if uploaded_file is None:
        return None
    
    # Créer un hash unique basé sur le contenu et le nom du fichier
    file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
    timestamp = int(time.time())
    
    # Nettoyer le nom de la solution pour le nom de fichier (enlever les caractères problématiques)
    clean_solution_name = "".join(c for c in solution_name if c.isalnum() or c in ('-', '_')).rstrip()
    clean_solution_name = clean_solution_name.replace(' ', '_')
    # Éviter les noms vides
    if not clean_solution_name:
        clean_solution_name = "solution"
    
    # Extension du fichier (nettoyée)
    file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'jpg'
    file_extension = "".join(c for c in file_extension if c.isalnum()).lower()
    
    # Nom du fichier final avec protection contre les doublons
    base_filename = f"{clean_solution_name}_{file_hash}_{timestamp}"
    filename = f"{base_filename}.{file_extension}"
    filepath = UPLOAD_DIR / filename
    
    # Éviter les doublons en ajoutant un compteur si nécessaire
    counter = 1
    while filepath.exists():
        filename = f"{base_filename}_{counter}.{file_extension}"
        filepath = UPLOAD_DIR / filename
        counter += 1
    
    # Sauvegarder le fichier
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Retourner le chemin relatif de manière robuste
    try:
        # Utiliser os.path.relpath qui est plus robuste
        return os.path.relpath(str(filepath), str(Path.cwd()))
    except ValueError:
        # Fallback : méthode string simple
        return str(filepath).replace(str(Path.cwd()), "").lstrip("/\\")

def load_saved_image(filepath):
    """
    Charge une image sauvegardée à partir de son chemin.
    Args:
        filepath: Chemin vers le fichier image
    Returns:
        bytes: Contenu de l'image ou None si erreur
    """
    try:
        full_path = Path(filepath)
        if full_path.exists():
            with open(full_path, "rb") as f:
                return f.read()
    except Exception:
        pass
    return None

def get_persistent_images(solution_name):
    """
    Récupère les images persistantes pour une solution depuis les cookies.
    Args:
        solution_name: Nom de la solution
    Returns:
        tuple: (urls_list, saved_files_paths_list)
    """
    cookie_key_urls = f"solution_images_urls_{solution_name}"
    cookie_key_files = f"solution_images_files_{solution_name}"
    
    # Récupérer les URLs depuis les cookies
    saved_urls_raw = cookies.get(cookie_key_urls)
    saved_urls = json.loads(saved_urls_raw) if saved_urls_raw else []
    
    # Récupérer les chemins de fichiers depuis les cookies
    saved_files_raw = cookies.get(cookie_key_files)
    saved_files = json.loads(saved_files_raw) if saved_files_raw else []
    
    # Vérifier que les fichiers existent encore
    valid_files = []
    for filepath in saved_files:
        if load_saved_image(filepath) is not None:
            valid_files.append(filepath)
    
    return saved_urls, valid_files

def save_persistent_images(solution_name, urls_list, uploaded_files):
    """
    Sauvegarde les images et leurs références dans les cookies.
    Args:
        solution_name: Nom de la solution
        urls_list: Liste des URLs d'images
        uploaded_files: Liste des fichiers uploadés
    """
    cookie_key_urls = f"solution_images_urls_{solution_name}"
    cookie_key_files = f"solution_images_files_{solution_name}"
    
    # Sauvegarder les URLs
    clean_urls = [url.strip() for url in urls_list if url and url.strip()]
    cookies[cookie_key_urls] = json.dumps(clean_urls)
    
    # Sauvegarder les fichiers uploadés et stocker leurs chemins
    saved_files = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            saved_path = save_uploaded_image(uploaded_file, solution_name)
            if saved_path:
                saved_files.append(saved_path)
    
    # Récupérer les anciens fichiers et les ajouter
    _, old_files = get_persistent_images(solution_name)
    all_files = list(set(old_files + saved_files))  # Éviter les doublons
    
    cookies[cookie_key_files] = json.dumps(all_files)

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
        logo_url (str): URL du logo (si vide, pas de logo affiché).
        color (str): Couleur principale.
        url_site (str): URL du site web.
        video (str): URL de la vidéo.
    """
    show_site = isinstance(url_site, str) and url_site.strip() and url_site.strip().lower() not in ['-', 'nan', 'aucun', 'none']
    # Rendre la condition vidéo plus flexible - pas seulement YouTube
    show_video = isinstance(video, str) and video.strip() and video.strip().lower() not in ['-', 'nan', 'aucun', 'none'] and ('youtube' in video.lower() or 'youtu.be' in video.lower() or 'vimeo' in video.lower() or 'http' in video.lower())
    show_logo = isinstance(logo_url, str) and logo_url.strip() and logo_url.startswith('http')

    # Logo professionnel compact avec transparence simple (seulement si logo_url fourni)
    logo = ''
    if show_logo:
        logo = f"""<div style="width:60px;height:60px;border-radius:8px;background:{THEME['glass_bg']};padding:6px;border:1px solid {THEME['glass_border']};display:flex;align-items:center;justify-content:center;box-shadow:{THEME['glass_shadow']};transition:all 0.3s ease;">
            <img src='{logo_url}' width='48' style='border-radius:4px;max-width:100%;max-height:100%;object-fit:contain;' alt='Logo solution'/>
        </div>"""

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

    # Carte professionnelle compacte avec transparence simple
    html = (
        'display:flex;flex-direction:column;gap:12px;'
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:12px;'
        'padding:16px 20px;max-width:600px;margin:0 auto 0.5rem auto;'
        f'box-shadow:{THEME["glass_shadow"]};position:relative;'
        'transition: all 0.3s ease;'
    )
    
    # Conteneur du haut : Logo + Nom (seulement si logo présent) ou Nom seul
    if show_logo:
        top_container = f'<div style="display:flex;align-items:center;justify-content:center;gap:10px;"><div style="flex-shrink:0;">{logo}</div><div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:0;">'
        top_container += f'<h2 style="font-size:1.4rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;word-break:break-word;text-align:center;">{name}</h2>'
        top_container += '</div></div>'
    else:
        # Nom seul, centré
        top_container = f'<div style="display:flex;align-items:center;justify-content:center;"><h2 style="font-size:1.4rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;word-break:break-word;text-align:center;">{name}</h2></div>'
    
    # Conteneur du bas : Boutons
    bottom_container = f'<div style="display:flex;justify-content:center;width:100%;">{btns_html}</div>' if btns else ''
    
    card = f'<div style="{html}">{top_container}{bottom_container}</div>'
    
    st.markdown(_wrap_html(card, 600), unsafe_allow_html=True)
    
def render_image_section(images_urls: list, uploaded_images=None, saved_files_paths=None):
    """
    Section d'affichage des images avec transparence simple et support des images persistantes.
    Args:
        images_urls (list): Liste des URLs d'images.
        uploaded_images: Liste des fichiers images uploadés via Streamlit.
        saved_files_paths (list): Liste des chemins vers les images sauvegardées.
    """
    has_url_images = images_urls and any(
        img.strip() for img in images_urls
        if isinstance(img, str) and img.strip().lower() not in ['-', 'nan', 'aucun', 'none', 'uploaded_file']
    )
    has_uploaded_images = uploaded_images is not None and len(uploaded_images) > 0
    has_saved_images = saved_files_paths is not None and len(saved_files_paths) > 0

    if not has_url_images and not has_uploaded_images and not has_saved_images:
        return

    images_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:12px;'
        'padding:12px 16px;margin-bottom:1rem;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;'
        'position:relative;'
        'overflow:hidden;'
    )

    if has_url_images:
        render_url_images(images_urls, images_style)
    if has_uploaded_images:
        render_uploaded_images(uploaded_images, images_style)
    if has_saved_images:
        render_saved_images(saved_files_paths, images_style)

def render_url_images(images_urls: list, images_style: str):
    """
    Affiche les images depuis les URLs.
    Args:
        images_urls (list): Liste des URLs d'images
        images_style (str): Style CSS pour les images
    """
    images_html = ''
    for img_url in images_urls:
        if isinstance(img_url, str) and img_url.strip() and img_url.strip().lower() not in ['-', 'nan', 'aucun', 'none', 'uploaded_file']:
            if img_url.startswith('http'):
                images_html += f'''
                <div style="margin-bottom:12px;text-align:center;">
                    <div style="font-size:0.8rem;color:{THEME["primary"]};font-weight:600;margin-bottom:6px;">Image depuis URL</div>
                    <img src="{img_url}" style="max-width:100%;max-height:300px;object-fit:contain;border-radius:8px;box-shadow:0 4px 15px rgba(0,114,178,0.15);border:1px solid rgba(0,114,178,0.1);" alt="Image solution"/>
                </div>
                '''
    if images_html:
        section_html = f'''
        <div style="{images_style}">
            {images_html}
        </div>
        '''
        st.markdown(section_html, unsafe_allow_html=True)

def render_uploaded_images(uploaded_images: list, images_style: str):
    """
    Affiche les images uploadées.
    Args:
        uploaded_images (list): Liste des images uploadées
        images_style (str): Style CSS pour les images
    """
    if not uploaded_images:
        return
    for uploaded_image in uploaded_images:
        st.markdown(f'''
        <div style="{images_style}">
        ''', unsafe_allow_html=True)
        _, col2, _ = st.columns([0.5, 4, 0.5])
        with col2:
            st.image(
                uploaded_image,
                use_container_width=True,
                caption=f"Image: {uploaded_image.name}",
                output_format="auto"
            )
        st.markdown('</div>', unsafe_allow_html=True)

def render_saved_images(saved_files_paths: list, images_style: str):
    """
    Affiche les images sauvegardées.
    Args:
        saved_files_paths (list): Liste des chemins des fichiers sauvegardés
        images_style (str): Style CSS pour les images
    """
    if not saved_files_paths:
        return
    for filepath in saved_files_paths:
        image_data = load_saved_image(filepath)
        if image_data:
            st.markdown(f'''
            <div style="{images_style}">
            ''', unsafe_allow_html=True)
            _, col2, _ = st.columns([0.5, 4, 0.5])
            with col2:
                st.image(
                    image_data,
                    use_container_width=True,
                    caption=f"Image sauvegardée: {Path(filepath).name}",
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

# --- Helper Functions for Display ---

def _validate_dataframe(df_sol: pd.DataFrame) -> tuple[bool, str]:
    """
    Valide le DataFrame et trouve la colonne solution.
    
    Returns:
        tuple: (is_valid, solution_column or error_message)
    """
    if df_sol.empty:
        return False, "Aucune donnée de solution disponible."
    
    # Trouver la colonne solution
    solution_column = None
    for col in df_sol.columns:
        if 'solution' in col.lower():
            solution_column = col
            break
    
    if not solution_column:
        return False, "Aucune colonne 'Solutions' trouvée dans les données."
    
    solutions = df_sol[solution_column].dropna().unique()
    if len(solutions) == 0:
        return False, "Aucune solution disponible dans les données."
    
    return True, solution_column

def _setup_sidebar_inputs(solutions: list) -> tuple[str, list, any]:
    """
    Configure les éléments d'entrée de la sidebar.
    
    Args:
        solutions (list): Liste des solutions disponibles
        
    Returns:
        tuple: (selected_solution, image_urls, uploaded_images)
    """
    # Sélection de la solution
    selected = st.sidebar.selectbox('Choisissez une solution', solutions, key='select_solution')
    cookies['solution_selected'] = json.dumps([selected])
    
    # Section d'ajout d'images
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Ajouter des images**")
    
    # URLs d'images
    st.sidebar.markdown("**URLs d'images**")
    num_urls = st.sidebar.number_input("Nombre d'URLs d'images", min_value=0, max_value=5, value=1, key='num_image_urls')
    
    image_urls = []
    for i in range(num_urls):
        url = st.sidebar.text_input(
            f"URL de l'image {i+1}",
            placeholder="https://exemple.com/image.jpg",
            key=f'custom_image_url_{i}'
        )
        if url and url.strip():
            image_urls.append(url.strip())
    
    # Upload d'images
    st.sidebar.markdown("**Télécharger des images**")
    
    # Clé dynamique pour le file_uploader
    if 'file_uploader_key' not in st.session_state:
        st.session_state['file_uploader_key'] = 0
    
    uploaded_images = st.sidebar.file_uploader(
        "Sélectionner des images",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
        accept_multiple_files=True,
        key=f'uploaded_images_{st.session_state["file_uploader_key"]}'
    )
    
    return selected, image_urls, uploaded_images

def _handle_image_persistence(selected: str, image_urls: list, uploaded_images: any) -> tuple[list, list]:
    """
    Gère la persistance des images (sauvegarde et récupération).
    
    Returns:
        tuple: (persistent_urls, persistent_files)
    """
    # Sauvegarder les URLs
    if image_urls:
        save_persistent_images(selected, image_urls, None)
    
    # Récupérer les images persistantes
    persistent_urls, persistent_files = get_persistent_images(selected)
    
    # Sauvegarder les nouvelles images uploadées
    if uploaded_images:
        new_uploaded_images = []
        for uploaded_img in uploaded_images:
            img_hash = hashlib.md5(uploaded_img.getvalue()).hexdigest()[:8]
            # Vérifier si l'image existe déjà
            exists = any(img_hash in persistent_file for persistent_file in persistent_files)
            if not exists:
                new_uploaded_images.append(uploaded_img)
        
        if new_uploaded_images:
            save_persistent_images(selected, [], new_uploaded_images)
            persistent_urls, persistent_files = get_persistent_images(selected)
            # Réinitialiser le file_uploader
            st.session_state['file_uploader_key'] += 1
            st.rerun()
    
    return persistent_urls, persistent_files

def _render_url_deletion_buttons(persistent_urls: list, selected: str):
    """
    Affiche les boutons de suppression pour les URLs persistantes.
    
    Args:
        persistent_urls (list): Liste des URLs persistantes
        selected (str): Solution sélectionnée
    """
    if not persistent_urls:
        return
        
    st.sidebar.markdown("**URLs sauvegardées:**")
    for i, url in enumerate(persistent_urls):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.write(f"🔗 URL {i+1}")
        with col2:
            if st.button("🗑️", key=f"delete_url_{i}", help="Supprimer cette URL"):
                updated_urls = [u for j, u in enumerate(persistent_urls) if j != i]
                cookie_key_urls = f"solution_images_urls_{selected}"
                cookies[cookie_key_urls] = json.dumps(updated_urls)
                st.sidebar.success("URL supprimée !")
                st.rerun()

def _render_file_deletion_buttons(persistent_files: list, selected: str):
    """
    Affiche les boutons de suppression pour les fichiers persistants.
    
    Args:
        persistent_files (list): Liste des fichiers persistants
        selected (str): Solution sélectionnée
    """
    if not persistent_files:
        return
        
    st.sidebar.markdown("**Fichiers sauvegardés:**")
    for i, filepath in enumerate(persistent_files):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            filename = Path(filepath).name
            st.write(f"📁 {filename[:20]}...")
        with col2:
            if st.button("🗑️", key=f"delete_file_{i}", help="Supprimer ce fichier"):
                # Supprimer le fichier physique
                try:
                    full_path = Path(filepath)
                    if full_path.exists():
                        full_path.unlink()
                except Exception:
                    pass
                
                # Supprimer de la liste persistante
                updated_files = [f for j, f in enumerate(persistent_files) if j != i]
                cookie_key_files = f"solution_images_files_{selected}"
                cookies[cookie_key_files] = json.dumps(updated_files)
                st.session_state['file_uploader_key'] += 1
                st.sidebar.success("Fichier supprimé !")
                st.rerun()

def _render_global_deletion_button(persistent_urls: list, persistent_files: list, selected: str):
    """
    Affiche le bouton de suppression globale.
    
    Args:
        persistent_urls (list): Liste des URLs persistantes
        persistent_files (list): Liste des fichiers persistants
        selected (str): Solution sélectionnée
    """
    if st.sidebar.button("🗑️ Supprimer TOUTES les images sauvegardées"):
        # Supprimer tous les fichiers physiques
        for filepath in persistent_files:
            try:
                full_path = Path(filepath)
                if full_path.exists():
                    full_path.unlink()
            except Exception:
                pass
        
        # Nettoyer les cookies
        cookie_key_urls = f"solution_images_urls_{selected}"
        cookie_key_files = f"solution_images_files_{selected}"
        cookies[cookie_key_urls] = json.dumps([])
        cookies[cookie_key_files] = json.dumps([])
        st.session_state['file_uploader_key'] += 1
        st.sidebar.success("Toutes les images supprimées !")
        st.rerun()

def _render_persistent_images_sidebar(selected: str, persistent_urls: list, persistent_files: list):
    """
    Affiche la section des images persistantes dans la sidebar avec boutons de suppression.
    
    Args:
        selected (str): Solution sélectionnée
        persistent_urls (list): Liste des URLs persistantes
        persistent_files (list): Liste des fichiers persistants
    """
    if not persistent_urls and not persistent_files:
        return
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Images sauvegardées**")
    
    # URLs avec suppression individuelle
    _render_url_deletion_buttons(persistent_urls, selected)
    
    # Fichiers avec suppression individuelle
    _render_file_deletion_buttons(persistent_files, selected)
    
    st.sidebar.write(f"Total: {len(persistent_urls) + len(persistent_files)} image(s)")
    
    # Bouton de suppression globale
    _render_global_deletion_button(persistent_urls, persistent_files, selected)

def _get_solution_urls(info: pd.Series) -> tuple[str, str]:
    """
    Extrait les URLs de site web et vidéo de la solution.
    
    Returns:
        tuple: (url_site, video_url)
    """
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
    return url_site, video

def _get_description(info: pd.Series, df_sol: pd.DataFrame) -> str:
    """
    Récupère la description de la solution.
    
    Returns:
        str: Description ou message par défaut
    """
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
    
    return desc

def _collect_all_images(info: pd.Series, persistent_urls: list, image_urls: list) -> list:
    """
    Collecte toutes les URLs d'images de différentes sources.
    
    Returns:
        list: Liste de toutes les URLs d'images
    """
    images_urls = []
    
    # Images des champs Excel
    image_fields = [key for key in info.keys() if 'image' in key.lower() or 'photo' in key.lower() or 'screenshot' in key.lower()]
    for field in image_fields:
        img_url = info.get(field, '')
        if isinstance(img_url, str) and img_url.strip():
            images_urls.append(img_url.strip())
    
    # Images persistantes (URLs)
    for url in persistent_urls:
        if url and url.strip():
            images_urls.append(url.strip())
    
    # Images personnalisées actuelles
    for url in image_urls:
        if url and url.strip():
            images_urls.append(url.strip())
    
    return images_urls

def _render_main_content(selected: str, info: pd.Series, desc: str, url_site: str, video: str, 
                        images_urls: list, persistent_files: list, uploaded_images: any,
                        df_sol: pd.DataFrame, solution_column: str):
    """
    Affiche le contenu principal de la page.
    
    Args:
        selected (str): Solution sélectionnée
        info (pd.Series): Données de la solution
        desc (str): Description de la solution
        url_site (str): URL du site web
        video (str): URL de la vidéo
        images_urls (list): Liste des URLs d'images
        persistent_files (list): Liste des fichiers persistants
        uploaded_images (any): Images uploadées
        df_sol (pd.DataFrame): DataFrame des solutions
        solution_column (str): Nom de la colonne solution
    """
    # Header
    render_header('Fiche solution')
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    
    # Vérifier s'il y a des images
    has_images = bool(images_urls) or bool(uploaded_images) or bool(persistent_files)
    
    # Section Description + Nom/Logo (2 colonnes)
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        render_section('Description')
        desc_style = (
            f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
            'padding:20px 24px;margin-bottom:1.5rem;'
            f'box-shadow:{THEME["glass_shadow"]};'
            'transition:all 0.3s ease;position:relative;overflow:hidden;'
        )
        desc_html = f'''
        <div style="{desc_style}">
            <div style="font-size:0.95rem;line-height:1.5;color:#000;text-align:justify;border-left:4px solid {THEME["primary"]};padding-left:16px;font-weight:500;">{desc}</div>
        </div>
        '''
        st.markdown(desc_html, unsafe_allow_html=True)
    
    with col_right:
        render_logo_and_name(selected, '', '#0072B2', url_site, video)
    
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    
    # Section Informations + Images (adaptative)
    if has_images:
        _render_info_with_images(df_sol, solution_column, info, images_urls, persistent_files)
    else:
        _render_info_without_images(df_sol, solution_column, info)

def _render_info_with_images(df_sol: pd.DataFrame, solution_column: str, info: pd.Series, 
                           images_urls: list, persistent_files: list):
    """
    Affiche les informations avec images en deux colonnes.
    
    Args:
        df_sol (pd.DataFrame): DataFrame des solutions
        solution_column (str): Nom de la colonne solution
        info (pd.Series): Données de la solution
        images_urls (list): Liste des URLs d'images
        persistent_files (list): Liste des fichiers persistants
    """
    col_left2, col_right2 = st.columns([1, 1])
    
    with col_left2:
        render_section('Informations générales')
        fields = [c for c in df_sol.columns if c != solution_column and 
                 c.lower() not in ['description','url (logo)','url (vidéo)','website','site web']]
        selected_fields = st.sidebar.multiselect('Champs visibles', fields, default=fields[:4], key='fields_solution')
        
        _render_info_cards(selected_fields, info)
    
    with col_right2:
        render_section('Images')
        # Ne pas passer uploaded_images car elles sont déjà dans persistent_files
        render_image_section(images_urls, None, persistent_files)

def _render_info_without_images(df_sol: pd.DataFrame, solution_column: str, info: pd.Series):
    """
    Affiche les informations sans images sur 2 colonnes.
    
    Args:
        df_sol (pd.DataFrame): DataFrame des solutions
        solution_column (str): Nom de la colonne solution
        info (pd.Series): Données de la solution
    """
    render_section('Informations générales')
    fields = [c for c in df_sol.columns if c != solution_column and 
             c.lower() not in ['description','url (logo)','url (vidéo)','website','site web']]
    selected_fields = st.sidebar.multiselect('Champs visibles', fields, default=fields[:6], key='fields_solution')
    
    # Diviser en deux groupes
    mid_point = (len(selected_fields) + 1) // 2
    fields_left = selected_fields[:mid_point]
    fields_right = selected_fields[mid_point:]
    
    col_info_left, col_info_right = st.columns([1, 1])
    
    with col_info_left:
        _render_info_cards(fields_left, info)
    
    with col_info_right:
        _render_info_cards(fields_right, info, start_index=mid_point)

def _render_info_cards(fields: list, info: pd.Series, start_index: int = 0):
    """
    Affiche les cartes d'informations.
    
    Args:
        fields (list): Liste des champs à afficher
        info (pd.Series): Données de la solution
        start_index (int): Index de départ pour l'alternance des couleurs
    """
    if not fields:
        return
        
    cards_container_style = (
        f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
        'padding:20px 24px;margin-bottom:1.5rem;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;position:relative;overflow:hidden;'
    )
    
    cards = ''
    for i, f in enumerate(fields):
        val = info.get(f, 'N/A')
        if pd.notna(val) and str(val).strip():
            card_bg = THEME['glass_bg'] if (i + start_index) % 2 == 0 else THEME['glass_bg_blue']
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

def _render_technical_section(info: pd.Series):
    """
    Affiche la section des caractéristiques techniques.
    """
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    render_section('Caractéristiques techniques')
    
    tech_fields = [key for key in info.keys() if any(word in key.lower() 
                  for word in ['technologie', 'version', 'compatibilité', 'système', 'plateforme', 'api', 'technique', 'tech'])]
    
    if tech_fields:
        tech_style = (
            f'background:{THEME["glass_bg"]};border:1px solid {THEME["glass_border"]};border-radius:14px;'
            'padding:20px 24px;margin-bottom:1.5rem;'
            f'box-shadow:{THEME["glass_shadow"]};'
            'transition:all 0.3s ease;position:relative;overflow:hidden;'
        )
        
        tech_content = ''
        for field in tech_fields[:3]:
            val = info.get(field, 'N/A')
            if pd.notna(val) and str(val).strip():
                tech_content += f'<div style="margin-bottom:12px;"><strong style="color:{THEME["primary"]};font-size:0.9rem;">{field}:</strong> <span style="color:#000;font-size:0.9rem;">{val}</span></div>'
        
        if tech_content:
            tech_html = f'<div style="{tech_style}">{tech_content}</div>'
            st.markdown(tech_html, unsafe_allow_html=True)
            return
    
    # Message par défaut si pas d'infos techniques
    info_style = (
        'background:rgba(227, 240, 250, 0.8);border:1px solid rgba(0, 114, 178, 0.3);border-radius:12px;'
        'padding:16px 24px;margin-bottom:1.5rem;text-align:center;'
        'box-shadow:0 4px 16px rgba(0, 114, 178, 0.1);'
        'transition:all 0.3s ease;position:relative;overflow:hidden;'
    )
    info_html = f'''
    <div style="{info_style}">
        <p style="margin:0;font-size:1rem;color:#000;font-weight:600;">Aucune caractéristique technique spécifique disponible.</p>
    </div>
    '''
    st.markdown(info_html, unsafe_allow_html=True)

def _render_location_section(info: pd.Series):
    """
    Affiche la section de localisation si applicable.
    """
    location_fields = [key for key in info.keys() if any(word in key.lower() 
                      for word in ['localisation', 'adresse', 'siège', 'address', 'location'])]
    
    if not location_fields:
        return
    
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    render_section('Localisation')
    
    addr = info.get(location_fields[0], '')
    if not isinstance(addr, str) or not addr.strip() or addr.strip().lower() in ['-', 'nan', 'aucun', 'none']:
        return
    
    with st.spinner('Géocodage de l\'adresse en cours...'):
        lat, lon = geocode(addr)
    
    if lat and lon:
        df_map = pd.DataFrame([{'lat': lat, 'lon': lon, 'name': 'Localisation'}])
        layer = pdk.Layer(
            'ScatterplotLayer', df_map, get_position='[lon,lat]', get_radius=1000,
            get_color=[0,114,178], pickable=True, tooltip=True
        )
        view = pdk.ViewState(latitude=lat, longitude=lon, zoom=7)
        st.pydeck_chart(pdk.Deck(initial_view_state=view, layers=[layer], 
                                tooltip={"text": "{name} : [{lat}, {lon}]"}), use_container_width=True)
    else:
        error_style = (
            'background:rgba(248, 215, 218, 0.8);border:1px solid rgba(220, 53, 69, 0.4);border-radius:12px;'
            'padding:16px 24px;margin-bottom:1.5rem;text-align:center;'
            'box-shadow:0 4px 16px rgba(220, 53, 69, 0.15);'
            'transition:all 0.3s ease;position:relative;overflow:hidden;'
        )
        error_html = f'''
        <div style="{error_style}">
            <p style="margin:0;font-size:1rem;color:#000;font-weight:600;">Adresse non géocodée ou introuvable. Merci de vérifier l'adresse saisie.</p>
        </div>
        '''
        st.markdown(error_html, unsafe_allow_html=True)

def _apply_page_styles():
    """
    Applique les styles CSS de la page.
    """
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
    .stSelectbox > div > div, .stMultiSelect > div > div, .stColorPicker > div > div,
    .stTextInput > div > div, .stFileUploader > div > div {
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

# --- Main Display ---
def display(df_sol: pd.DataFrame):
    """
    Fonction principale d'affichage de la page Solution, refactorisée pour une meilleure maintenabilité.
    
    Args:
        df_sol (pd.DataFrame): DataFrame contenant les données des solutions
    """
    # Appliquer les styles modernes à la sidebar
    apply_sidebar_styles()
    
    # Réinitialiser le compteur de section à chaque affichage
    if 'section_count' not in st.session_state:
        st.session_state['section_count'] = 0
    st.session_state['section_count'] = 0
    
    # Appliquer les styles CSS de la page
    _apply_page_styles()
    
    # Validation du DataFrame
    is_valid, result = _validate_dataframe(df_sol)
    if not is_valid:
        st.error(result)
        return
    
    solution_column = result
    solutions = df_sol[solution_column].dropna().unique()
    
    # Configuration des éléments d'entrée de la sidebar
    selected, image_urls, uploaded_images = _setup_sidebar_inputs(solutions)
    
    # Récupération des informations de la solution sélectionnée
    info = df_sol[df_sol[solution_column] == selected].iloc[0]
    cookies['solution_selected'] = json.dumps([selected])
    
    # Gestion de la persistance des images
    persistent_urls, persistent_files = _handle_image_persistence(selected, image_urls, uploaded_images)
    
    # Affichage des images persistantes dans la sidebar
    _render_persistent_images_sidebar(selected, persistent_urls, persistent_files)
    
    # Récupération des URLs et de la description
    url_site, video = _get_solution_urls(info)
    desc = _get_description(info, df_sol)
    
    # Collecte de toutes les images
    images_urls = _collect_all_images(info, persistent_urls, image_urls)
    
    # Affichage du contenu principal
    _render_main_content(selected, info, desc, url_site, video, 
                        images_urls, persistent_files, uploaded_images,
                        df_sol, solution_column)
    
    # Affichage des sections techniques et de localisation
    _render_technical_section(info)
    _render_location_section(info)
