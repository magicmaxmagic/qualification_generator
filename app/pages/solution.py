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
from sidebar import cookies, apply_sidebar_styles, show_sidebar
from app.pages.entreprise import render_left_column, get_url_site, render_logo_section, render_description_section, render_map_section, render_header
from typing import Any

# Version: 2025.01.10 - Page Solution compacte avec gestion d'images - Design identique à Entreprise
"""
=== CONSTANTES GLOBALES (labels, colonnes, messages, titres, etc.) ===
"""

# --- Labels additionnels pour captions, erreurs, info-bulle, etc. ---
LABEL_CHOIX_SOLUTION = "Choisissez une solution"
LABEL_AJOUTER_IMAGES = "Ajouter des images"
LABEL_URLS_IMAGES = "URLs d'images"
LABEL_NB_URLS_IMAGES = "Nombre d'URLs d'images"
LABEL_PLACEHOLDER_URL = "https://exemple.com/image.jpg"
LABEL_TELECHARGER_IMAGES = "Télécharger des images"
LABEL_SELECTIONNER_IMAGES = "Sélectionner des images"
LABEL_IMAGE_DE_LA_SOLUTION = "Image de la solution"
LABEL_IMAGE_SAUVEGARDEE_CAPTION = "Image sauvegardée: {name}"
LABEL_IMAGE_UPLOADED_CAPTION = "Image: {name}"
LABEL_IMPOSSIBLE_CHARGER_IMAGE = "Impossible de charger l'image depuis l'URL: {url}"
LABEL_ERREUR_URL = "Erreur lors du traitement de l'URL: {url}"
LABEL_ASTUCE_URL = "Astuce : Assurez-vous que l'URL pointe directement vers un fichier image (.jpg, .png, .gif, etc.)"
# --- Configuration pour la persistance des images ---
UPLOAD_DIR = Path("uploads/user_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

LABEL_FICHE_SOLUTION = "Fiche solution"
LABEL_ENTREPRISES = "Entreprises"
LABEL_SOLUTIONS = "Solutions"
LABEL_EXIGENCES = "Exigences"
LABEL_CHOISISSEZ_ENTREPRISE = "Choisissez une entreprise"
SEPARATOR = '<div style="margin:0.8rem 0;border-bottom:1px solid rgba(0,0,0,0.1);"></div>'
LABEL_INFOS_GENERALES = "Informations générales"
LABEL_IMAGES = "Images"
LABEL_DESCRIPTION = "Description"
LABEL_CARACTERISTIQUES_TECH = "Caractéristiques techniques"
LABEL_CHAMPS_VISIBLES = "Champs visibles"
LABEL_SITE_WEB = "Site web"
LABEL_BOUTON_VIDEO = "Vidéo"
LABEL_AUCUNE_DESCRIPTION = "Aucune description disponible."
LABEL_AUCUNE_CARAC_TECH = "Aucune caractéristique technique spécifique disponible."
LABEL_IMAGE_URL = "Image depuis URL"
LABEL_IMAGE_SAUVEGARDEE = "Image sauvegardée"
LABEL_IMAGE = "Image"
LABEL_IMAGE_NON_AFFICHEE = "L'image n'a pu être affichée directement."
LABEL_VOIR_IMAGE = "🔗 Voir l'image dans un nouvel onglet"
LABEL_OUVRIR_URL = "🔗 Ouvrir l'URL dans un nouvel onglet"
LABEL_SUPPRIMER_URL = "🗑️"
LABEL_SUPPRIMER_TOUT = "🗑️ Supprimer TOUTES les images sauvegardées"
LABEL_IMAGES_SAUVEGARDEES = "Images sauvegardées"
LABEL_URLS_SAUVEGARDEES = "URLs sauvegardées:"
LABEL_FICHIERS_SAUVEGARDES = "Fichiers sauvegardés:"
LABEL_TOTAL_IMAGES = "Total: {n} image(s)"
LABEL_URL = "URL"
LABEL_FICHIER = "Fichier"
LABEL_SUPPRIMER_URL_TOOLTIP = "Supprimer cette URL"
LABEL_SUPPRIMER_FICHIER_TOOLTIP = "Supprimer ce fichier"
LABEL_SUPPRIMER_TOUT_SUCCESS = "Toutes les images supprimées !"
LABEL_SUPPRIMER_URL_SUCCESS = "URL supprimée !"
LABEL_SUPPRIMER_FICHIER_SUCCESS = "Fichier supprimé !"

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
        top_container += f'<h2 style="font-size:1.7rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;word-break:break-word;text-align:center;">{name}</h2>'
        top_container += '</div></div>'
    else:
        # Nom seul, centré
        top_container = f'<div style="display:flex;align-items:center;justify-content:center;"><h2 style="font-size:1.7rem;font-weight:700;color:#000;margin:0;letter-spacing:-0.01em;line-height:1.1;word-break:break-word;text-align:center;">{name}</h2></div>'
    
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
        render_uploaded_images(uploaded_images if uploaded_images is not None else [], images_style)
    if has_saved_images:
        render_saved_images(saved_files_paths or [], images_style)

def render_url_images(images_urls: list, images_style: str):
    """
    Affiche les images depuis les URLs avec gestion robuste.
    Args:
        images_urls (list): Liste des URLs d'images
        images_style (str): Style CSS pour les images
    """
    def _render_single_url_image(img_url: str, images_style: str):
        try:
            st.markdown(f'''
            <div style="{images_style}">
                <div style="margin-bottom:12px;text-align:center;">
                    <div style="font-size:0.8rem;color:{THEME["primary"]};font-weight:600;margin-bottom:6px;">{LABEL_IMAGE_URL}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            _, col2, _ = st.columns([0.5, 4, 0.5])
            with col2:
                try:
                    st.image(img_url, use_container_width=True, caption=LABEL_IMAGE_DE_LA_SOLUTION)
                except Exception:
                    st.error(LABEL_IMPOSSIBLE_CHARGER_IMAGE.format(url=img_url))
                    st.markdown(f'''
                    <div style="border:1px solid #ddd; border-radius:8px; padding:15px; text-align:center; background-color:#f9f9f9; margin-top: 10px;">
                        <p style="margin-bottom:12px; font-size:0.9rem; color:#333;">{LABEL_IMAGE_NON_AFFICHEE}</p>
                        <a href="{img_url}" target="_blank" style="display: inline-block; color: #fff; background-color: #0072B2; text-decoration: none; font-weight: bold; padding: 8px 16px; border-radius: 5px;">
                            {LABEL_VOIR_IMAGE}
                        </a>
                    </div>
                    ''', unsafe_allow_html=True)
        except Exception:
            st.error(LABEL_ERREUR_URL.format(url=img_url))
            st.info(LABEL_ASTUCE_URL)
            st.markdown(f'''
            <a href="{img_url}" target="_blank" style="display: inline-block; color: #fff; background-color: #0072B2; text-decoration: none; font-weight: bold; padding: 8px 16px; border-radius: 5px;">
                {LABEL_OUVRIR_URL}
            </a>
            ''', unsafe_allow_html=True)

    if not images_urls:
        return

    for img_url in images_urls:
        if (
            isinstance(img_url, str)
            and img_url.strip()
            and img_url.strip().lower() not in ['-', 'nan', 'aucun', 'none', 'uploaded_file']
            and img_url.startswith('http')
        ):
            _render_single_url_image(img_url, images_style)

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
                caption=LABEL_IMAGE_UPLOADED_CAPTION.format(name=uploaded_image.name),
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
                    caption=LABEL_IMAGE_SAUVEGARDEE_CAPTION.format(name=Path(filepath).name),
                    output_format="auto"
                )
            st.markdown('</div>', unsafe_allow_html=True)

def render_section(title: str, bg: str = ""):
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

# --- Helper Functions for Display ---

def _validate_dataframe(df_sol: pd.DataFrame) -> tuple[bool, str]:
    """
    Valide le DataFrame et trouve la colonne solution.
    
    Returns:
        tuple: (is_valid, solution_column or error_message)
    """
    if df_sol.empty:
        return False, LABEL_ERREUR_AUCUNE_DONNEE_SOLUTION
    # Trouver la colonne solution
    solution_column = None
    for col in df_sol.columns:
        if 'solution' in col.lower():
            solution_column = col
            break
    if not solution_column:
        return False, LABEL_ERREUR_AUCUNE_COLONNE_SOLUTION
    solutions = df_sol[solution_column].dropna().unique()
    if len(solutions) == 0:
        return False, LABEL_ERREUR_AUCUNE_SOLUTION
    return True, solution_column

def _setup_sidebar_inputs(solutions: list) -> tuple[str, list, Any]:
    """
    Configure les éléments d'entrée de la sidebar.
    
    Args:
        solutions (list): Liste des solutions disponibles
        
    Returns:
        tuple: (selected_solution, image_urls, uploaded_images)
    """
    # Sélection de la solution
    if solutions and len(solutions) > 0:
        selected = st.sidebar.selectbox(LABEL_CHOIX_SOLUTION, solutions, key='select_solution')
    else:
        selected = ""
    cookies['solution_selected'] = json.dumps([selected])

    # Champs visibles : tous les champs valides pour la solution sélectionnée
    import pandas as pd
    df_sol = st.session_state.get('df_sol', None)
    info = None
    general_fields = []
    default_fields = []
    selected_fields = []
    if df_sol is not None and selected:
        # Trouver la colonne solution
        solution_column = None
        for col in df_sol.columns:
            if col.lower() in ['solution', 'solutions']:
                solution_column = col
                break
        if solution_column:
            info = df_sol[df_sol[solution_column] == selected].iloc[0]
            general_fields = [c for c in df_sol.columns if c.lower() not in ['solution','solutions','description','images','site web','url (logo)','url (vidéo)','website'] and not c.lower().startswith('description') and not c.lower().startswith('url')]
            default_fields = general_fields.copy()
            sidebar_fields_key = f"fields_solution_sidebar_{selected}_{hash(tuple(general_fields))}" if selected else "fields_solution_sidebar"
            st.sidebar.markdown(f"**{LABEL_CHAMPS_VISIBLES}**")
            # Supprime toute sélection précédente pour forcer la sélection de tous les champs à chaque affichage
            for key in list(st.session_state.keys()):
                if key.startswith("fields_solution_sidebar_"):
                    del st.session_state[key]
            selected_fields = st.sidebar.multiselect(LABEL_CHAMPS_VISIBLES, general_fields, default=general_fields, key=sidebar_fields_key)
            st.session_state['selected_fields_sidebar'] = selected_fields
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{LABEL_AJOUTER_IMAGES}**")
    # URLs d'images
    st.sidebar.markdown(f"**{LABEL_URLS_IMAGES}**")
    num_urls = st.sidebar.number_input(LABEL_NB_URLS_IMAGES, min_value=0, max_value=5, value=1, key='num_image_urls')
    image_urls = []
    for i in range(num_urls):
        url = st.sidebar.text_input(
            f"URL de l'image {i+1}",
            placeholder=LABEL_PLACEHOLDER_URL,
            key=f'custom_image_url_{i}'
        )
        if url and url.strip():
            image_urls.append(url.strip())
    # Upload d'images
    st.sidebar.markdown(f"**{LABEL_TELECHARGER_IMAGES}**")
    # Clé dynamique pour le file_uploader
    if 'file_uploader_key' not in st.session_state:
        st.session_state['file_uploader_key'] = 0
    uploaded_images = st.sidebar.file_uploader(
        LABEL_SELECTIONNER_IMAGES,
        type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
        accept_multiple_files=True,
        key=f'uploaded_images_{st.session_state["file_uploader_key"]}'
    )

    # S'assurer que selected est toujours une chaîne de caractères
    if selected is None:
        selected = ""
    return selected, image_urls, uploaded_images, selected_fields

def _handle_image_persistence(selected: str, image_urls: list, uploaded_images: Any) -> tuple[list, list]:
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
            if 'file_uploader_key' not in st.session_state:
                st.session_state['file_uploader_key'] = 0
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
        
    st.sidebar.markdown(f"**{LABEL_URLS_SAUVEGARDEES}**")
    for i, url in enumerate(persistent_urls):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.write(f"🔗 {LABEL_URL} {i+1}")
        with col2:
            if st.button(LABEL_SUPPRIMER_URL, key=f"delete_url_{i}", help=LABEL_SUPPRIMER_URL_TOOLTIP):
                updated_urls = [u for j, u in enumerate(persistent_urls) if j != i]
                cookie_key_urls = f"solution_images_urls_{selected}"
                cookies[cookie_key_urls] = json.dumps(updated_urls)
                st.sidebar.success(LABEL_SUPPRIMER_URL_SUCCESS)
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
        
    st.sidebar.markdown(f"**{LABEL_FICHIERS_SAUVEGARDES}**")
    for i, filepath in enumerate(persistent_files):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            filename = Path(filepath).name
            st.write(f"📁 {LABEL_FICHIER} : {filename[:20]}...")
        with col2:
            if st.button(LABEL_SUPPRIMER_URL, key=f"delete_file_{i}", help=LABEL_SUPPRIMER_FICHIER_TOOLTIP):
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
                
                # Assurer que la clé existe avant de l'incrémenter
                if 'file_uploader_key' not in st.session_state:
                    st.session_state['file_uploader_key'] = 0
                st.session_state['file_uploader_key'] += 1
                
                st.sidebar.success(LABEL_SUPPRIMER_FICHIER_SUCCESS)
                st.rerun()

def _render_global_deletion_button(persistent_urls: list, persistent_files: list, selected: str):
    """
    Affiche le bouton de suppression globale.
    
    Args:
        persistent_urls (list): Liste des URLs persistantes
        persistent_files (list): Liste des fichiers persistants
        selected (str): Solution sélectionnée
    """
    if st.sidebar.button(LABEL_SUPPRIMER_TOUT):
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
        
        # Assurer que la clé existe avant de l'incrémenter
        if 'file_uploader_key' not in st.session_state:
            st.session_state['file_uploader_key'] = 0
        st.session_state['file_uploader_key'] += 1
        
        st.sidebar.success(LABEL_SUPPRIMER_TOUT_SUCCESS)
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
    st.sidebar.markdown(f"**{LABEL_IMAGES_SAUVEGARDEES}**")
    
    # URLs avec suppression individuelle
    _render_url_deletion_buttons(persistent_urls, selected)
    
    # Fichiers avec suppression individuelle
    _render_file_deletion_buttons(persistent_files, selected)
    
    st.sidebar.write(LABEL_TOTAL_IMAGES.format(n=len(persistent_urls) + len(persistent_files)))
    
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
        desc = LABEL_AUCUNE_DESCRIPTION
    
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
        render_section(LABEL_INFOS_GENERALES)
        fields = [c for c in df_sol.columns if c != solution_column and 
                 c.lower() not in ['description','url (logo)','url (vidéo)','website','site web'] and
                 not c.lower().startswith('description') and
                 not c.lower().startswith('url')]
        sidebar_fields_key = f"fields_solution_withimg_{info.get(solution_column, '')}" if info.get(solution_column, '') else "fields_solution_withimg"
        selected_fields = st.sidebar.multiselect(LABEL_CHAMPS_VISIBLES, fields, default=fields[:4], key=sidebar_fields_key)
        _render_info_cards(selected_fields, info)
    with col_right2:
        render_section(LABEL_IMAGES)
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
    render_section(LABEL_INFOS_GENERALES)
    # Utilise le multiselect défini dans _setup_sidebar_inputs
    selected_fields = st.session_state.get('selected_fields_sidebar', [])
    display_fields = selected_fields
    mid_point = (len(display_fields) + 1) // 2
    fields_left = display_fields[:mid_point]
    fields_right = display_fields[mid_point:]

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
        'padding:16px 20px;margin-bottom:1rem;'
        f'box-shadow:{THEME["glass_shadow"]};'
        'transition:all 0.3s ease;position:relative;overflow:hidden;'
    )
    cards = ''
    for i, f in enumerate(fields):
        # Si le champ est exactement 'URL', utiliser le label global
        if f.strip().upper() == 'URL':
            continue  # Ne jamais afficher la carte URL
        elif f.strip().upper() == 'FICHIER':
            display_field = LABEL_FICHIER
        else:
            display_field = f
        val = info.get(f, LABEL_INFO_VALEUR_PAR_DEFAUT)
        # Affiche la carte seulement si la valeur est non vide et non N/A
        if not (pd.notna(val) and str(val).strip()) or str(val).lower() in ['nan', 'n/a', '-', '']:
            continue
        card_bg = THEME['glass_bg'] if (i + start_index) % 2 == 0 else THEME['glass_bg_blue']
        card_style = (
            f'background:{card_bg};border:1px solid {THEME["glass_border"]};border-radius:12px;'
            'padding:14px 18px;margin:0 0 12px 0;width:100%;'
            f'box-shadow:0 4px 16px rgba(0,114,178,0.12);transition:all 0.3s ease;'
            'position:relative;overflow:hidden;'
        )
        cards += f'''<div style="{card_style}">
            <strong style="font-size:1.0rem;font-weight:700;color:{THEME["primary"]};display:block;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">{display_field}</strong>
            <div style="font-size:1.3rem;color:#000;font-weight:600;line-height:1.3;">{val}</div>
        </div>'''
    if cards:
        grid_section_html = f'''<div style="{cards_container_style}">
            <div style="display:flex;flex-direction:column;gap:0;width:100%;">{cards}</div>
        </div>'''
        st.markdown(grid_section_html, unsafe_allow_html=True)

def _render_description_section(desc: str):
    """
    Affiche la section description de la solution.
    
    Args:
        desc (str): Description de la solution
    """
    render_section(LABEL_DESCRIPTION)
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

def _render_technical_section(info: pd.Series):
    """
    Affiche la section des caractéristiques techniques.
    """
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    render_section(LABEL_CARACTERISTIQUES_TECH)
    
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
            val = info.get(field, LABEL_INFO_VALEUR_PAR_DEFAUT)
            if pd.notna(val) and str(val).strip():
                tech_content += f'<div style="margin-bottom:12px;"><strong style="color:{THEME["primary"]};font-size:1.0rem;">{field}:</strong> <span style="color:#000;font-size:1.0rem;">{val}</span></div>'
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
        <p style="margin:0;font-size:1.1rem;color:#000;font-weight:600;">{LABEL_AUCUNE_CARAC_TECH}</p>
    </div>
    '''
    st.markdown(info_html, unsafe_allow_html=True)
"""
Labels additionnels pour les messages d'erreur et valeurs par défaut (ajoutés pour la factorisation complète)
"""
LABEL_ERREUR_AUCUNE_DONNEE_SOLUTION = "Aucune donnée de solution disponible."
LABEL_ERREUR_AUCUNE_COLONNE_SOLUTION = "Aucune colonne 'Solutions' trouvée dans les données."
LABEL_ERREUR_AUCUNE_SOLUTION = "Aucune solution disponible dans les données."
LABEL_INFO_VALEUR_PAR_DEFAUT = "N/A"

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
    """
    apply_sidebar_styles()
    _apply_page_styles()
    _apply_page_styles()
    # Validation du DataFrame
    is_valid, result = _validate_dataframe(df_sol)
    if not is_valid:
        st.error(result)
        return
    solution_column = result
    solutions = df_sol[solution_column].dropna().unique()
    selected, image_urls, uploaded_images, selected_fields = _setup_sidebar_inputs(list(solutions))
    info = df_sol[df_sol[solution_column] == selected].iloc[0] if selected else df_sol.iloc[0]
    cookies['solution_selected'] = json.dumps([selected])
    st.session_state['selected_fields_sidebar'] = selected_fields
    persistent_urls, persistent_files = _handle_image_persistence(selected, image_urls, uploaded_images)
    _render_persistent_images_sidebar(selected, persistent_urls, persistent_files)
    url_site, video = _get_solution_urls(info)
    desc = _get_description(info, df_sol)
    images_urls = _collect_all_images(info, persistent_urls, image_urls)
    render_header(LABEL_FICHE_SOLUTION)
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    col_desc, col_name = st.columns([1, 1])
    with col_desc:
        _render_description_section(desc)
    with col_name:
        render_logo_and_name(selected, info.get('URL (logo)', ''), THEME['accent'], url_site, video)
    st.markdown(SEPARATOR, unsafe_allow_html=True)
    if images_urls or persistent_files:
        _render_info_with_images(df_sol, solution_column, info, images_urls, persistent_files)
    else:
        _render_info_without_images(df_sol, solution_column, info)
