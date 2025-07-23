"""
Module de génération de rapport PDF simplifié pour l'application IVÉO BI
======================================================================

Ce module génère un rapport PDF simple sans dépendances complexes.
Il utilise une approche HTML vers PDF plus robuste.

Version : 1.1 - 2025.01.16
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from datetime import datetime
import json
from sidebar import cookies
from weasyprint import HTML


# Imports pour l'export PDF avec gestion d'erreurs
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

try:
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
except Exception:
    # Gestion d'erreur étendue pour les problèmes de bibliothèques système
    WEASYPRINT_AVAILABLE = False

# Détection de l'environnement cloud au niveau module
import os
IS_CLOUD_ENV = (
    os.getenv('STREAMLIT_CLOUD') == 'true' or 
    os.getenv('RENDER') is not None or 
    os.getenv('HEROKU') is not None or 
    os.getenv('RAILWAY_ENVIRONMENT') is not None or
    os.getenv('VERCEL') is not None
)


# =================== VARIABLES D'ÉTAT ET MESSAGES ===================
MSG_MISSING_LIBS = "Bibliothèques système manquantes pour WeasyPrint (libpango, libcairo). Tentative avec pdfkit..."
MSG_MISSING_FONTCONFIG = "Configuration des polices manquante. Tentative avec pdfkit..."
MSG_WEASYPRINT_ERROR = "Erreur WeasyPrint: {}"
MSG_PDFKIT_MISSING = "wkhtmltopdf non installé sur cette plateforme."
MSG_PDFKIT_NOT_FOUND = "Exécutable wkhtmltopdf introuvable."
MSG_PDFKIT_ERROR = "Erreur pdfkit: {}"
MSG_PDF_EXPORT_UNAVAILABLE = "L'export PDF n'est pas disponible sur cette plateforme."
MSG_PDF_EXPORT_FATAL = "Erreur fatale lors de l'export PDF (bibliothèques système manquantes)."
MSG_PDF_EXPORT_ERROR = "Erreur lors de la génération PDF: {}"
MSG_REPORT_GEN_ERROR = "Erreur lors de la génération du rapport : {}"

# Titres et labels globaux
TITLE_REPORT = "Rapport IVÉO - Analyse Comparative"
META_DESCRIPTION = "Rapport d'analyse comparative IVÉO - Intelligence d'affaires"
META_AUTHOR = "IVÉO"
META_GENERATOR = "IVÉO BI Platform"
TITLE_HEADER = "Rapport d'Analyse Comparative"
LABEL_META = "Intelligence d'Affaires • Analyse Stratégique"
LABEL_GENERATED_ON = "Généré le {}"
TITLE_TOC = "Table des matières"
TOC_ITEMS = [
    ("resume", "Résumé exécutif"),
    ("entreprises", "Analyse des entreprises"),
    ("solutions", "Analyse des solutions"),
    ("comparative", "Analyse comparative"),
    ("recommandations", "Recommandations stratégiques"),
    ("methodologie", "Méthodologie"),
    ("annexes", "Annexes")
]
TITLE_EXEC_SUMMARY = "1. Résumé exécutif"
TITLE_COMPANIES = "2. Analyse des entreprises"
TITLE_SOLUTIONS = "3. Analyse des solutions"
TITLE_COMPARATIVE = "4. Analyse comparative"
TITLE_RECOMMENDATIONS = "5. Recommandations stratégiques"
TITLE_METHODOLOGY = "6. Méthodologie"
TITLE_ANNEXES = "7. Annexes"
LABEL_NO_COMPANY_DATA = "Aucune donnée d'entreprise disponible."
LABEL_NO_SOLUTION_DATA = "Aucune donnée de solution disponible."
LABEL_NO_COMPARATIVE_DATA = "Aucune donnée d'analyse comparative disponible avec les filtres actuels."
LABEL_COMPANIES_ANALYSED = "Entreprises analysées"
LABEL_SECTORS = "Secteurs représentés"
LABEL_SOLUTIONS_ANALYSED = "Solutions analysées"
LABEL_IMAGES_ASSOCIATED = "Images associées"
LABEL_CRITERIA = "Critères évalués"
LABEL_DOMAINS = "Domaines"
LABEL_COMPANIES = "Entreprises"
LABEL_FILTERS = "Filtres appliqués"
LABEL_NO_COMPANY = "Aucune entreprise à afficher."
LABEL_NO_SOLUTION_COLUMN = "Aucune colonne de solutions trouvée."
LABEL_SELECTED_SOLUTION = "Solution sélectionnée :"
LABEL_NO_SELECTION = "Aucune sélection spécifique"
LABEL_TABLE_COMPANY = ["Entreprise", "Secteur", "Localisation", "Statut", "Site web"]
LABEL_TABLE_SOLUTION = ["Solution", "Catégorie", "Fournisseur", "Statut", "Site web"]
LABEL_YES = "✓ Oui"
LABEL_NO = "✗ Non"
LABEL_NA = "-"


def _clean_na_value(value):
    """
    Nettoie les valeurs N/A et les remplace par des chaînes vides ou des valeurs par défaut.
    
    Args:
        value: Valeur à nettoyer
        
    Returns:
        str: Valeur nettoyée
    """
    if pd.isna(value) or str(value).strip().lower() in ['n/a', 'nan', '-', '']:
        return ""
    return str(value).strip()

def _get_clean_value(info, key, default=""):
    """
    Récupère une valeur nettoyée depuis un objet pandas Series.
    
    Args:
        info: Objet pandas Series
        key: Clé à récupérer
        default: Valeur par défaut si vide
        
    Returns:
        str: Valeur nettoyée
    """
    value = info.get(key, default)
    cleaned = _clean_na_value(value)
    return cleaned if cleaned else default

def generate_html_report(df_ent, df_sol, df_comp, df_align=None):
    """
    Génère un rapport HTML complet qui peut être converti en PDF.
    
    Args:
        df_ent (pd.DataFrame): Données des entreprises
        df_sol (pd.DataFrame): Données des solutions
        df_comp (pd.DataFrame): Données d'analyse comparative
        df_align (pd.DataFrame): Données d'alignement (optionnel)
        
    Returns:
        str: HTML du rapport complet
    """
    
    # CSS pour le rapport professionnel - Version optimisée pour la lisibilité
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * {margin: 0; padding: 0; box-sizing: border-box;}
    </style>
    """
    # Récupérer les données des cookies
    selected_companies = []
    selected_solution = ""
    selected_categories = []
    selected_solution = ""
    selected_categories = []
    
    try:
        selected_companies = json.loads(cookies.get("selected_companies", "[]"))
        selected_solution_json = cookies.get("solution_selected", "[]")
        selected_solutions = json.loads(selected_solution_json)
        if selected_solutions:
            selected_solution = selected_solutions[0]
        selected_categories = json.loads(cookies.get("selected_categories", "[]"))
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Générer le HTML avec une structure améliorée
    html = f"""
    <!DOCTYPE html>
    <html lang=\"fr\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>{TITLE_REPORT}</title>
        <meta name=\"description\" content=\"{META_DESCRIPTION}\">
        <meta name=\"author\" content=\"{META_AUTHOR}\">
        <meta name=\"generator\" content=\"{META_GENERATOR}\">
        {css}
    </head>
    <body>
        <div class=\"report-container\">
            {_generate_header()}
            {_generate_table_of_contents()}
            {_generate_executive_summary(df_ent, df_sol, df_comp)}
            {_generate_companies_section(df_ent, selected_companies)}
            {_generate_solutions_section(df_sol, selected_solution)}
            {_generate_comparative_section(df_comp, selected_categories, selected_companies)}
            {_generate_recommendations()}
            {_generate_methodology_section()}
            {_generate_annexes()}
            {_generate_footer()}
        </div>
    </body>
    </html>
    """
    
    return html

def _generate_header():
    """Génère l'en-tête du rapport avec un design professionnel."""
    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    return f"""
    <div class=\"header\">
        <div class=\"header-content\">
            <h1>{META_AUTHOR}</h1>
            <h2>{TITLE_HEADER}</h2>
            <div class=\"meta\">
                <p>{LABEL_META}</p>
                <p>{LABEL_GENERATED_ON.format(date_str)}</p>
            </div>
        </div>
    </div>
    """

def _generate_table_of_contents():
    """Génère une table des matières professionnelle."""
    toc_items_html = ''.join([f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in TOC_ITEMS])
    return f"""
    <div class=\"section\">
        <div class=\"toc\">
            <h2>{TITLE_TOC}</h2>
            <ol>
                {toc_items_html}
            </ol>
        </div>
    </div>
    """

def _generate_executive_summary(df_ent, df_sol, df_comp):
    """Génère un résumé exécutif professionnel avec statistiques et insights."""
    stats_html = _generate_executive_stats_html(df_ent, df_sol, df_comp)
    insights_html = _generate_executive_insights_html(df_ent, df_sol, df_comp)
    return _build_executive_summary_html(stats_html, insights_html)

def _build_executive_summary_html(stats_html, insights_html):
    """Construit le HTML du résumé exécutif à partir des sous-parties."""
    return f"""
    <div class=\"section page-break\" id=\"resume\">
        <h2>{TITLE_EXEC_SUMMARY}</h2>
        <div class=\"executive-summary\">
            <div class=\"stats-grid\">{stats_html}</div>
            <div class=\"highlight\">
                <h3>Contexte et objectifs</h3>
                <p>Ce rapport présente une analyse comparative approfondie des solutions et entreprises évaluées selon une méthodologie rigoureuse. L'objectif est de fournir une base décisionnelle solide pour orienter les choix stratégiques de l'organisation.</p>
                <p>{insights_html}</p>
            </div>
            <h3>Points clés de l'analyse</h3>
            <ul>
                <li>Évaluation multi-critères basée sur des indicateurs quantitatifs et qualitatifs</li>
                <li>Analyse comparative structurée permettant l'identification des solutions optimales</li>
                <li>Recommandations stratégiques alignées sur les objectifs organisationnels</li>
                <li>Méthodologie transparente et reproductible</li>
            </ul>
        </div>
    </div>
    """

def _generate_executive_stats_html(df_ent, df_sol, df_comp):
    """Génère le HTML des statistiques pour le résumé exécutif."""
    stats = []
    if df_ent is not None and not df_ent.empty:
        stats.append(f'<div class="stat-card"><p class="stat-number">{len(df_ent)}</p><p class="stat-label">Entreprises analysées</p></div>')
    if df_sol is not None and not df_sol.empty:
        stats.append(f'<div class="stat-card"><p class="stat-number">{len(df_sol)}</p><p class="stat-label">Solutions évaluées</p></div>')
    if df_comp is not None and not df_comp.empty:
        stats.append(f'<div class="stat-card"><p class="stat-number">{len(df_comp)}</p><p class="stat-label">Critères d\'évaluation</p></div>')
    if df_ent is not None and not df_ent.empty:
        secteurs = df_ent.get("Secteur d'activité", pd.Series()).dropna().nunique()
        if secteurs > 0:
            stats.append(f'<div class="stat-card"><p class="stat-number">{secteurs}</p><p class="stat-label">Secteurs représentés</p></div>')
    return ''.join(stats)

def _generate_executive_insights_html(df_ent, df_sol, df_comp):
    """Génère le HTML des insights automatiques pour le résumé exécutif."""
    insights = []
    if df_ent is not None and not df_ent.empty:
        insights.append(f"L'analyse porte sur {len(df_ent)} entreprises représentant une diversité sectorielle significative.")
    if df_sol is not None and not df_sol.empty:
        insights.append(f"L'évaluation comprend {len(df_sol)} solutions technologiques répondant à différents besoins organisationnels.")
    if df_comp is not None and not df_comp.empty:
        insights.append(f"L'analyse comparative s'appuie sur {len(df_comp)} critères d'évaluation structurés et objectifs.")
    return ' '.join(insights)

def _generate_companies_section(df_ent, selected_companies):
    """Génère la section des entreprises avec toutes les informations."""
    if df_ent is None or df_ent.empty:
        return f"""
        <div class=\"section page-break\" id=\"entreprises\">\n            <h2>{TITLE_COMPANIES}</h2>\n            <p>{LABEL_NO_COMPANY_DATA}</p>\n        </div>\n        """
    
    if not selected_companies:
        company_column = df_ent.columns[0]
        selected_companies = df_ent[company_column].dropna().unique().tolist()

    companies_info = [_extract_company_details(df_ent, company) for company in selected_companies]
    companies_info = [c for c in companies_info if c is not None]

    companies_html = ''.join([_generate_company_html(company) for company in companies_info])
    
    # Générer les lignes du tableau récapitulatif
    table_rows = []
    for comp in companies_info:
        # Gestion du site web avec logique simplifiée
        site_web_cell = "Non spécifié"
        if comp["site_web"]:
            if comp["site_web"].startswith('http'):
                site_web_cell = f'<a href="{comp["site_web"]}" target="_blank">Lien</a>'
            else:
                site_web_cell = comp["site_web"]
        
        table_rows.append(f"""
        <tr>
            <td><strong>{comp["nom"]}</strong></td>
            <td>{comp["secteur"]}</td>
            <td>{comp["localisation"]}</td>
            <td>{comp["statut"]}</td>
            <td>{site_web_cell}</td>
        </tr>
        """)

    return f"""
    <div class=\"section page-break\" id=\"entreprises\">\n        <h2>{TITLE_COMPANIES}</h2>\n        <div class=\"stats-grid\">\n            <div class=\"stat-card\">\n                <p class=\"stat-number\">{len(selected_companies)}</p>\n                <p class=\"stat-label\">{LABEL_COMPANIES_ANALYSED}</p>\n            </div>\n            <div class=\"stat-card\">\n                <p class=\"stat-number\">{len(set(comp['secteur'] for comp in companies_info))}</p>\n                <p class=\"stat-label\">{LABEL_SECTORS}</p>\n            </div>\n        </div>\n        <h3>Profils détaillés des entreprises</h3>\n        {companies_html}\n        <h3>Tableau récapitulatif des entreprises</h3>\n        <div class=\"table-container\">\n            <table>\n                <thead>\n                    <tr>\n                        <th style=\"width: 25%;\">{LABEL_TABLE_COMPANY[0]}</th>\n                        <th style=\"width: 20%;\">{LABEL_TABLE_COMPANY[1]}</th>\n                        <th style=\"width: 20%;\">{LABEL_TABLE_COMPANY[2]}</th>\n                        <th style=\"width: 15%;\">{LABEL_TABLE_COMPANY[3]}</th>\n                        <th style=\"width: 20%;\">{LABEL_TABLE_COMPANY[4]}</th>\n                    </tr>\n                </thead>\n                <tbody>\n                    {''.join(table_rows)}\n                </tbody>\n            </table>\n        </div>\n    </div>\n    """

def _extract_company_details(df_ent, company):
    company_info = df_ent[df_ent.iloc[:, 0] == company]
    if company_info.empty:
        return None
    info = company_info.iloc[0]
    company_details = {
        'nom': str(company),
        'secteur': _get_clean_value(info, "Secteur d'activité", "Non spécifié"),
        'localisation': _get_clean_value(info, "Localisation", "Non spécifiée"),
        'statut': _get_clean_value(info, "Statut", "Non spécifié"),
        'description': _get_clean_value(info, "Description", "Description non disponible"),
        'site_web': _get_clean_value(info, "Site web", ""),
        'logo': _get_clean_value(info, "URL (logo)", ""),
        'autres_infos': {}
    }
    for col in df_ent.columns:
        if col not in ['Secteur d\'activité', 'Localisation', 'Statut', 'Description', 'Site web', 'URL (logo)']:
            value = _get_clean_value(info, col, "")
            if value:  # Seulement ajouter si la valeur n'est pas vide
                company_details['autres_infos'][col] = value
    return company_details

def _generate_company_html(company):
    """Génère le HTML pour une entreprise avec un design professionnel."""
    logo_html = ""
    if company['logo'] and company['logo'].startswith('http'):
        logo_html = f'<img src="{company["logo"]}" alt="Logo {company["nom"]}" class="company-logo" onerror="this.style.display=\'none\'">'
    
    site_web_html = ""
    if company['site_web'] and company['site_web'].startswith('http'):
        site_web_html = f'<div class="detail-item"><strong>Site web:</strong> <a href="{company["site_web"]}" target="_blank">{company["site_web"]}</a></div>'
    
    autres_infos_html = ""
    if company['autres_infos']:
        autres_infos_html = "<h3>Informations complémentaires</h3><div class=\"company-details\">"
        for key, value in company['autres_infos'].items():
            autres_infos_html += f'<div class="detail-item"><strong>{key}:</strong> {value}</div>'
        autres_infos_html += "</div>"
    
    description_html = ""
    if company['description']:
        description_html = f'<div class="highlight"><strong>Description:</strong> {company["description"]}</div>'
    
    return f"""
    <div class="company-card">
        <div class="company-header">
            {logo_html}
            <div class="company-title">
                <h3>{company['nom']}</h3>
                <div class="sector">{company['secteur']}</div>
            </div>
        </div>
        
        <div class="company-details">
            <div class="detail-item"><strong>Localisation:</strong> {company['localisation']}</div>
            <div class="detail-item"><strong>Statut:</strong> {company['statut']}</div>
            {site_web_html}
        </div>
        
        {description_html}
        {autres_infos_html}
    </div>
    """

def _generate_companies_summary_table(companies_info):
    """Génère un tableau récapitulatif des entreprises avec design professionnel."""
    if not companies_info:
        return "<p>Aucune entreprise à afficher.</p>"
    
    rows = []
    for comp in companies_info:
        # Gestion du site web avec logique simplifiée
        site_web_cell = "Non spécifié"
        if comp["site_web"]:
            if comp["site_web"].startswith('http'):
                site_web_cell = f'<a href="{comp["site_web"]}" target="_blank">Lien</a>'
            else:
                site_web_cell = comp["site_web"]
        
        rows.append(f"""
        <tr>
            <td><strong>{comp["nom"]}</strong></td>
            <td>{comp["secteur"]}</td>
            <td>{comp["localisation"]}</td>
            <td>{comp["statut"]}</td>
            <td>{site_web_cell}</td>
        </tr>
        """)
    
    return f"""
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Entreprise</th>
                    <th>Secteur d'activité</th>
                    <th>Localisation</th>
                    <th>Statut</th>
                    <th>Site web</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """

def _generate_solutions_section(df_sol, selected_solution):
    """Génère la section des solutions avec toutes les informations et images."""
    if df_sol is None or df_sol.empty:
        return f"""
        <div class=\"section page-break\" id=\"solutions\">\n            <h2>{TITLE_SOLUTIONS}</h2>\n            <p>{LABEL_NO_SOLUTION_DATA}</p>\n        </div>\n        """
    
    # Trouver la colonne des solutions
    solution_column = None
    for col in df_sol.columns:
        if 'solution' in col.lower():
            solution_column = col
            break
    
    if solution_column is None:
        return f"""
        <div class=\"section page-break\" id=\"solutions\">\n            <h2>{TITLE_SOLUTIONS}</h2>\n            <p>{LABEL_NO_SOLUTION_COLUMN}</p>\n        </div>\n        """
    
    # Récupérer les solutions à afficher - TOUTES les solutions disponibles
    solutions_to_show = []
    if df_sol[solution_column].notna().any():
        solutions_to_show = df_sol[solution_column].dropna().unique().tolist()
    
    # Si une solution spécifique est sélectionnée, la mettre en premier
    if selected_solution and selected_solution in solutions_to_show:
        solutions_to_show.remove(selected_solution)
        solutions_to_show.insert(0, selected_solution)
    
    # Récupérer les images persistantes pour la solution sélectionnée
    solution_images = []
    if selected_solution:
        try:
            import json
            from sidebar import cookies
            
            # Images URL
            cookie_key_urls = f"solution_images_urls_{selected_solution}"
            saved_urls_raw = cookies.get(cookie_key_urls)
            if saved_urls_raw:
                saved_urls = json.loads(saved_urls_raw)
                solution_images.extend(saved_urls)
            
            # Images fichiers (on ne peut pas les afficher dans le rapport HTML)
            cookie_key_files = f"solution_images_files_{selected_solution}"
            saved_files_raw = cookies.get(cookie_key_files)
            if saved_files_raw:
                saved_files = json.loads(saved_files_raw)
                if saved_files:
                    solution_images.append(f"Images sauvegardées: {len(saved_files)} fichier(s)")
        except:
            pass
    
    # Générer les détails des solutions
    solutions_html = ""
    for solution in solutions_to_show:
        solution_info = df_sol[df_sol[solution_column] == solution]
        if not solution_info.empty:
            info = solution_info.iloc[0]
            
            # Récupérer toutes les informations avec nettoyage
            solution_details = {
                'nom': str(solution),
                'categorie': _get_clean_value(info, "Catégorie", "Non spécifiée"),
                'fournisseur': _get_clean_value(info, "Fournisseur", "Non spécifié"),
                'statut': _get_clean_value(info, "Statut", "Non spécifié"),
                'description': _get_clean_value(info, "Description", "Description non disponible"),
                'site_web': _get_clean_value(info, "Site web", ""),
                'logo': _get_clean_value(info, "URL (logo)", ""),
                'video': _get_clean_value(info, "URL (vidéo)", ""),
                'autres_infos': {}
            }
            
            # Récupérer les images depuis les colonnes
            images_colonnes = []
            for col in df_sol.columns:
                if 'image' in col.lower() or 'photo' in col.lower() or 'screenshot' in col.lower():
                    img_url = info.get(col, '')
                    if isinstance(img_url, str) and img_url.strip() and img_url.startswith('http'):
                        images_colonnes.append(img_url.strip())
            
            # Récupérer toutes les autres colonnes avec nettoyage
            for col in df_sol.columns:
                if col not in ['Catégorie', 'Fournisseur', 'Statut', 'Description', 'Site web', 'URL (logo)', 'URL (vidéo)'] and solution_column != col:
                    value = _get_clean_value(info, col, "")
                    if value:  # Seulement ajouter si la valeur n'est pas vide
                        solution_details['autres_infos'][col] = value
            
            # Logo si disponible
            logo_html = ""
            if solution_details['logo'] and solution_details['logo'].startswith('http'):
                logo_html = f'<img src="{solution_details["logo"]}" alt="Logo {solution_details["nom"]}" style="max-width: 100px; max-height: 60px; margin: 10px 0;" onerror="this.style.display=\'none\'">'
            
            # Site web si disponible
            site_web_html = ""
            if solution_details['site_web'] and solution_details['site_web'].startswith('http'):
                site_web_html = f'<p><strong>Site web:</strong> <a href="{solution_details["site_web"]}" target="_blank">{solution_details["site_web"]}</a></p>'
            
            # Vidéo si disponible
            video_html = ""
            if solution_details['video'] and solution_details['video'].startswith('http'):
                video_html = f'<p><strong>Vidéo:</strong> <a href="{solution_details["video"]}" target="_blank">Voir la vidéo</a></p>'
            
            # Images des colonnes
            images_html = ""
            all_images = images_colonnes + (solution_images if solution == selected_solution else [])
            if all_images:
                images_html = "<h4>Images</h4><div style='display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0;'>"
                for img_url in all_images:
                    if isinstance(img_url, str) and img_url.startswith('http'):
                        images_html += f'<img src="{img_url}" alt="Image solution" style="max-width: 200px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px;" onerror="this.style.display=\'none\'">'
                    else:
                        images_html += f'<p style="font-size: 0.9em; color: #666;">{img_url}</p>'
                images_html += "</div>"
            
            # Informations supplémentaires
            autres_infos_html = ""
            if solution_details['autres_infos']:
                autres_infos_html = "<h4>Informations détaillées</h4><ul>"
                for key, value in solution_details['autres_infos'].items():
                    autres_infos_html += f"<li><strong>{key}:</strong> {value}</li>"
                autres_infos_html += "</ul>"
            
            solutions_html += f"""
            <div style="background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid #0072B2;">
                <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 15px;">
                    {logo_html}
                    <div>
                        <h3 style="margin: 0; color: #0072B2;">{solution_details['nom']}</h3>
                        <p style="margin: 5px 0; color: #666;">{solution_details['categorie']}</p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 15px 0;">
                    <div><strong>Fournisseur:</strong> {solution_details['fournisseur']}</div>
                    <div><strong>Statut:</strong> {solution_details['statut']}</div>
                </div>
                
                {f'<p><strong>Description:</strong> {solution_details["description"]}</p>' if solution_details['description'] else ''}
                {site_web_html}
                {video_html}
                {images_html}
                {autres_infos_html}
            </div>
            """
    
    # Tableau récapitulatif
    table_rows = []
    for solution in solutions_to_show:
        solution_info = df_sol[df_sol[solution_column] == solution]
        if not solution_info.empty:
            info = solution_info.iloc[0]
            category = _get_clean_value(info, "Catégorie", "Non spécifiée")
            provider = _get_clean_value(info, "Fournisseur", "Non spécifié")
            status = _get_clean_value(info, "Statut", "Non spécifié")
            site_web = _get_clean_value(info, "Site web", "")
            
            table_rows.append(f"""
            <tr>
                <td>{str(solution)[:40]}</td>
                <td>{category[:30]}</td>
                <td>{provider[:30]}</td>
                <td>{status[:20]}</td>
                <td>{'<a href="' + site_web + '" target="_blank">Lien</a>' if site_web and site_web.startswith('http') else (site_web if site_web else 'Non spécifié')}</td>
            </tr>
            """)
    
    table_html = f"""
    <table>\n        <thead>\n            <tr>\n                <th>{LABEL_TABLE_SOLUTION[0]}</th>\n                <th>{LABEL_TABLE_SOLUTION[1]}</th>\n                <th>{LABEL_TABLE_SOLUTION[2]}</th>\n                <th>{LABEL_TABLE_SOLUTION[3]}</th>\n                <th>{LABEL_TABLE_SOLUTION[4]}</th>\n            </tr>\n        </thead>\n        <tbody>\n            {''.join(table_rows)}\n        </tbody>\n    </table>\n    """
    
    return f"""
    <div class=\"section page-break\" id=\"solutions\">\n        <h2>{TITLE_SOLUTIONS}</h2>\n        <div class=\"stats-grid\">\n            <div class=\"stat-card\">\n                <p class=\"stat-number\">{len(solutions_to_show)}</p>\n                <p class=\"stat-label\">{LABEL_SOLUTIONS_ANALYSED}</p>\n            </div>\n            <div class=\"stat-card\">\n                <p class=\"stat-number\">{len(solution_images) if solution_images else 0}</p>\n                <p class=\"stat-label\">{LABEL_IMAGES_ASSOCIATED}</p>\n            </div>\n        </div>\n        <h3>Détails des solutions</h3>\n        {solutions_html}\n        <h3>Tableau récapitulatif</h3>\n        {table_html}\n        <p>\n            <strong>{LABEL_SELECTED_SOLUTION}</strong> {selected_solution if selected_solution else LABEL_NO_SELECTION}\n        </p>\n    </div>\n    """

def _generate_comparative_section(df_comp=None, selected_categories=None, selected_companies=None):
    """Génère la section d'analyse comparative avec filtres appliqués."""
    # Analyser les filtres appliqués
    filters_applied = {}
    
    # Examiner les sessions state pour récupérer les filtres
    try:
        import streamlit as st
        if hasattr(st, 'session_state'):
            for key, value in st.session_state.items():
                if isinstance(key, str) and key.startswith('selected_criteria_') and value:
                    try:
                        criteria_name = key.replace('selected_criteria_', '').replace('_', ' ').title()
                        filters_applied[f"Critère {criteria_name}"] = value
                    except Exception:
                        pass
    except Exception:
        pass
    
    # Ajouter les filtres passés en paramètres
    if selected_categories:
        filters_applied['Catégories sélectionnées'] = selected_categories
    if selected_companies:
        filters_applied['Entreprises sélectionnées'] = selected_companies
    
    # Générer le HTML des filtres appliqués
    filters_html = ""
    if filters_applied:
        filters_html = "<h3>Filtres et critères appliqués</h3><div style='background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;'>"
        for filter_name, filter_value in filters_applied.items():
            if isinstance(filter_value, list):
                value_str = ", ".join(str(v) for v in filter_value)
            else:
                value_str = str(filter_value)
            filters_html += f"<p><strong>{filter_name}:</strong> {value_str}</p>"
        filters_html += "</div>"
    
    # Section par défaut si pas de données
    if df_comp is None or df_comp.empty:
        return f"""
        <div class=\"section page-break\" id=\"comparative\">\n            <h2>{TITLE_COMPARATIVE}</h2>\n            <div class=\"stats-grid\">\n                <div class=\"stat-card\">\n                    <p class=\"stat-number\">{len(filters_applied)}</p>\n                    <p class=\"stat-label\">{LABEL_FILTERS}</p>\n                </div>\n                <div class=\"stat-card\">\n                    <p class=\"stat-number\">0</p>\n                    <p class=\"stat-label\">{LABEL_CRITERIA}</p>\n                </div>\n            </div>\n            {filters_html}\n            <p>{LABEL_NO_COMPARATIVE_DATA}</p>\n        </div>\n        """
    
    # Analyser les données disponibles
    total_criteria = len(df_comp)
    unique_categories = df_comp.get('Domaine', pd.Series()).dropna().unique() if 'Domaine' in df_comp.columns else []
    
    # Identifier les colonnes d'entreprises (toutes sauf les colonnes de base)
    base_columns = ["Type d'exigence", "Domaine", "Exigence différenciateur", "Exigence", "Description", "Catégorie"]
    company_columns = [col for col in df_comp.columns if col not in base_columns and "Information complémentaire" not in col]
    
    # Détecter si le tableau nécessite le mode paysage
    total_columns = len(base_columns) + len(company_columns)
    landscape_mode = total_columns > 6  # Mode paysage si plus de 6 colonnes
    
    # Styles CSS pour le mode paysage
    landscape_css = ""
    if landscape_mode:
        landscape_css = """
        <style>
        @media print {
            .comparative-table-container {
                transform: rotate(90deg);
                transform-origin: center;
                position: relative;
                width: 297mm;
                height: 210mm;
                margin: 0 auto;
                page-break-inside: avoid;
            }
            .comparative-table-container table {
                font-size: 0.7em;
            }
            .comparative-table-container th, 
            .comparative-table-container td {
                padding: 4px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 80px;
            }
        }
        </style>
        """
    
    # Statistiques
    stats_html = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <p class="stat-number">{total_criteria}</p>
            <p class="stat-label">Critères évalués</p>
        </div>
        <div class="stat-card">
            <p class="stat-number">{len(unique_categories)}</p>
            <p class="stat-label">Domaines</p>
        </div>
        <div class="stat-card">
            <p class="stat-number">{len(company_columns)}</p>
            <p class="stat-label">Entreprises</p>
        </div>
        <div class="stat-card">
            <p class="stat-number">{len(filters_applied)}</p>
            <p class="stat-label">Filtres appliqués</p>
        </div>
    </div>
    """
    
    # Générer le tableau avec les colonnes d'entreprises
    table_html = f"""
    {landscape_css}
    <div class="{'landscape-table' if landscape_mode else 'responsive-table'}">
        <h3>Tableau d'analyse comparative avec réponses par entreprise</h3>
        {"<p><strong>Mode paysage activé</strong> - Tableau optimisé pour l'impression landscape</p>" if landscape_mode else ""}
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 35%;">Critère</th>
                        <th style="width: 15%;">Domaine</th>
                        <th style="width: 15%;">Différenciateur</th>
    """
    
    # Ajouter les colonnes d'entreprises avec largeur dynamique
    company_width = f"{35 / len(company_columns)}%" if company_columns else "10%"
    for company in company_columns:
        table_html += f'<th style="width: {company_width}; text-align: center;">{company}</th>'
    
    table_html += """
                    </tr>
                </thead>
                <tbody>
    """
    
    # Générer les lignes du tableau avec pagination
    max_rows_per_page = 15 if landscape_mode else 20
    current_row = 0
    
    for idx, row in df_comp.iterrows():
        if current_row >= max_rows_per_page:
            # Nouvelle page/section
            table_html += """
                </tbody>
            </table>
        </div>
        <div class="page-break"></div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 35%;">Critère</th>
                        <th style="width: 15%;">Domaine</th>
                        <th style="width: 15%;">Différenciateur</th>
            """
            
            # Ajouter les colonnes d'entreprises avec largeur dynamique
            for company in company_columns:
                table_html += f'<th style="width: {company_width}; text-align: center;">{company}</th>'
            
            table_html += """
                    </tr>
                </thead>
                <tbody>
            """
            current_row = 0
        
        # Nettoyer les valeurs des colonnes de base
        critere = _get_clean_value(row, "Exigence", "Non spécifié")
        if len(critere) > 150:
            critere = critere[:147] + "..."
        
        domaine = _get_clean_value(row, "Domaine", "Non spécifié")
        if len(domaine) > 30:
            domaine = domaine[:27] + "..."
        
        differenciatrice = _get_clean_value(row, "Exigence différenciateur", "Non spécifié")
        if len(differenciatrice) > 30:
            differenciatrice = differenciatrice[:27] + "..."
        
        table_html += f"""
        <tr>
            <td style="padding: 8px; border-right: 1px solid #ddd;"><strong>{critere}</strong></td>
            <td style="padding: 8px; border-right: 1px solid #ddd;">{domaine}</td>
            <td style="padding: 8px; border-right: 1px solid #ddd;">{differenciatrice}</td>
        """
        
        # Ajouter les réponses des entreprises
        for company in company_columns:
            company_value = _get_clean_value(row, company, "")
            
            # Interpréter la valeur comme oui/non avec classes CSS
            if str(company_value).strip() in ['1', '1.0', 'Oui', 'oui', 'OUI', 'Yes', 'yes', 'TRUE', 'True', 'true']:
                cell_content = '<span>✓ Oui</span>'
                cell_class = "cell-yes"
            elif str(company_value).strip() in ['0', '0.0', 'Non', 'non', 'NON', 'No', 'no', 'FALSE', 'False', 'false']:
                cell_content = '<span>✗ Non</span>'
                cell_class = "cell-no"
            else:
                cell_content = '<span>-</span>'
                cell_class = "cell-na"
            
            table_html += f'<td class="{cell_class}" style="padding: 8px; border-right: 1px solid #ddd;">{cell_content}</td>'
        
        table_html += "</tr>"
        current_row += 1
    
    table_html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    # Sections supprimées : Analyse par domaine et Tableau de synthèse des scores par entreprise
    category_analysis = ""
    
    return f"""
    <div class="section page-break" id="comparative">
        <h2>4. Analyse comparative</h2>
        
        {stats_html}
        
        {filters_html}
        
        {table_html}
        
        {category_analysis}
        
        <div style="margin-top: 30px;">
            <h3>Méthodologie d'évaluation</h3>
            <p>Cette analyse comparative est basée sur les critères sélectionnés et les filtres appliqués. 
            Les données sont extraites de la base de données IVÉO et reflètent l'état actuel des informations disponibles.</p>
            <p>Les priorités sont classées selon l'importance stratégique de chaque critère pour l'organisation.</p>
        </div>
    </div>
    """

def _generate_recommendations():
    """Génère la section des recommandations stratégiques."""
    return """
    <div class="section page-break" id="recommandations">
        <h2>5. Recommandations stratégiques</h2>
        
        <div class="recommendations">
            <h3>Recommandations prioritaires</h3>
            <ul>
                <li><strong>Évaluation approfondie des solutions leaders</strong> : Procéder à une analyse détaillée des solutions ayant obtenu les meilleures notes dans l'évaluation comparative</li>
                <li><strong>Validation des critères critiques</strong> : Confirmer que les critères les plus importants pour l'organisation sont correctement pondérés dans l'analyse</li>
                <li><strong>Pilote d'implémentation</strong> : Planifier une phase pilote avec les solutions sélectionnées pour valider leur adéquation opérationnelle</li>
                <li><strong>Analyse coût-bénéfice approfondie</strong> : Compléter l'évaluation technique par une analyse financière détaillée</li>
            </ul>
        </div>
        
        <div class="recommendations">
            <h3>Considérations stratégiques</h3>
            <ul>
                <li><strong>Alignement organisationnel</strong> : S'assurer que la solution choisie s'intègre dans l'écosystème technologique existant</li>
                <li><strong>Capacité d'évolution</strong> : Privilégier les solutions offrant une roadmap claire et des possibilités d'évolution</li>
                <li><strong>Support et maintenance</strong> : Évaluer la qualité du support technique et la stabilité financière des fournisseurs</li>
                <li><strong>Formation et adoption</strong> : Prévoir un plan de formation pour maximiser l'adoption utilisateur</li>
            </ul>
        </div>
        
        <div class="highlight">
            <h3>Prochaines étapes recommandées</h3>
            <p>
                1. <strong>Validation des résultats</strong> avec les parties prenantes clés<br>
                2. <strong>Démonstrations techniques</strong> avec les fournisseurs finalistes<br>
                3. <strong>Évaluation des références clients</strong> et retours d'expérience<br>
                4. <strong>Négociation commerciale</strong> et finalisation des conditions contractuelles<br>
                5. <strong>Planification de l'implémentation</strong> et définition des jalons
            </p>
        </div>
    </div>
    """

def _generate_methodology_section():
    """Génère la section méthodologie."""
    return f"""
    <div class=\"section page-break\" id=\"methodologie\">\n        <h2>{TITLE_METHODOLOGY}</h2>\n        <div class=\"highlight\">\n            <h3>Approche méthodologique</h3>\n            <p>L'analyse comparative a été menée selon une méthodologie structurée et objective, garantissant la fiabilité et la reproductibilité des résultats.</p>\n        </div>\n        <h3>Étapes de l'analyse</h3>\n        <div class=\"company-details\">\n            <div class=\"detail-item\"><strong>1. Collecte des données</strong><br>Recueil systématique des informations sur les entreprises et solutions évaluées</div>\n            <div class=\"detail-item\"><strong>2. Définition des critères</strong><br>Établissement d'une grille d'évaluation basée sur les besoins organisationnels</div>\n            <div class=\"detail-item\"><strong>3. Évaluation comparative</strong><br>Notation objective selon les critères définis avec vérification croisée</div>\n            <div class=\"detail-item\"><strong>4. Analyse des résultats</strong><br>Synthèse des évaluations et identification des patterns significatifs</div>\n        </div>\n        <h3>Critères d'évaluation</h3>\n        <div class=\"table-container\">\n            <table>\n                <thead>\n                    <tr>\n                        <th>{LABEL_TABLE_SOLUTION[1]}</th>\n                        <th>Description</th>\n                        <th>Pondération</th>\n                    </tr>\n                </thead>\n                <tbody>\n                    <tr>\n                        <td><strong>Fonctionnalités techniques</strong></td>\n                        <td>Évaluation des capacités techniques et fonctionnelles</td>\n                        <td>Élevée</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Facilité d'utilisation</strong></td>\n                        <td>Ergonomie et facilité d'adoption par les utilisateurs</td>\n                        <td>Moyenne</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Support et maintenance</strong></td>\n                        <td>Qualité du support technique et de la maintenance</td>\n                        <td>Élevée</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Coût total de possession</strong></td>\n                        <td>Analyse des coûts d'acquisition et d'exploitation</td>\n                        <td>Très élevée</td>\n                    </tr>\n                </tbody>\n            </table>\n        </div>\n        <h3>Limites et considérations</h3>\n        <p>Cette analyse se base sur les informations disponibles au moment de l'évaluation. Les évolutions technologiques et les changements organisationnels peuvent influencer la pertinence des recommandations. Il est recommandé de procéder à des réévaluations périodiques pour maintenir la pertinence de l'analyse.</p>\n    </div>\n    """

def _generate_annexes():
    """Génère les annexes avec informations détaillées."""
    return f"""
    <div class=\"section page-break\" id=\"annexes\">\n        <h2>{TITLE_ANNEXES}</h2>\n        <h3>Méthodologie d'évaluation détaillée</h3>\n        <div class=\"table-container\">\n            <table>\n                <thead>\n                    <tr>\n                        <th>Aspect</th>\n                        <th>Description</th>\n                        <th>Méthode</th>\n                    </tr>\n                </thead>\n                <tbody>\n                    <tr>\n                        <td><strong>Critères d'évaluation</strong></td>\n                        <td>Évaluation binaire ({LABEL_YES}/{LABEL_NO}) ou numérique selon le critère</td>\n                        <td>Notation standardisée</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Pondération</strong></td>\n                        <td>Importance relative selon les besoins organisationnels</td>\n                        <td>Consultation des parties prenantes</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Validation</strong></td>\n                        <td>Vérification croisée des évaluations</td>\n                        <td>Revue par les experts métier</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Mise à jour</strong></td>\n                        <td>Actualisation périodique des données</td>\n                        <td>Cycle de révision trimestriel</td>\n                    </tr>\n                </tbody>\n            </table>\n        </div>\n        <h3>Sources des données</h3>\n        <div class=\"company-details\">\n            <div class=\"detail-item\"><strong>Documentation officielle</strong><br>Fiches techniques et spécifications fournisseurs</div>\n            <div class=\"detail-item\"><strong>Démonstrations techniques</strong><br>Évaluations en conditions réelles d'utilisation</div>\n            <div class=\"detail-item\"><strong>Retours d'expérience</strong><br>Témoignages clients et études de cas</div>\n            <div class=\"detail-item\"><strong>Analyses tierces</strong><br>Rapports d'analystes et comparatifs sectoriels</div>\n        </div>\n        <h3>Glossaire</h3>\n        <div class=\"table-container\">\n            <table>\n                <thead>\n                    <tr>\n                        <th>Terme</th>\n                        <th>Définition</th>\n                    </tr>\n                </thead>\n                <tbody>\n                    <tr>\n                        <td><strong>Analyse comparative</strong></td>\n                        <td>Évaluation systématique de solutions selon des critères prédéfinis</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Critère différenciateur</strong></td>\n                        <td>Élément d'évaluation permettant de distinguer les solutions</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Pondération</strong></td>\n                        <td>Coefficient d'importance attribué à chaque critère d'évaluation</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Score normalisé</strong></td>\n                        <td>Notation standardisée permettant la comparaison entre solutions</td>\n                    </tr>\n                </tbody>\n            </table>\n        </div>\n        <h3>Informations techniques</h3>\n        <div class=\"highlight\">\n            <p><strong>Plateforme d'analyse :</strong> {META_GENERATOR}</p>\n            <p><strong>Version du rapport :</strong> 1.0</p>\n            <p><strong>Format de données :</strong> Excel (.xlsx)</p>\n            <p><strong>Méthode d'export :</strong> HTML vers PDF</p>\n        </div>\n    </div>\n    """

def _generate_footer():
    """Génère le pied de page professionnel."""
    return """
    <div class="footer">
        <p><strong>IVÉO - Intelligence d'Affaires</strong></p>
        <p>Rapport généré automatiquement • Toute reproduction interdite sans autorisation</p>
        <p>Pour toute question, contactez l'équipe IVÉO</p>
    </div>
    """

def create_html_download_link(html_content, filename):
    """
    Crée un lien de téléchargement pour le rapport HTML.
    
    Args:
        html_content (str): Contenu HTML du rapport
        filename (str): Nom du fichier
        
    Returns:
        str: HTML du lien de téléchargement
    """
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}" style="display: inline-block; color: #fff; background-color: #0072B2; text-decoration: none; font-weight: bold; padding: 12px 24px; border-radius: 8px; margin: 10px 0;">📄 Télécharger le rapport HTML</a>'
    return href

def create_pdf_download_link(pdf_content, filename):
    """
    Crée un lien de téléchargement pour le rapport PDF.
    
    Args:
        pdf_content (bytes): Contenu PDF du rapport
        filename (str): Nom du fichier
        
    Returns:
        str: HTML du lien de téléchargement
    """
    b64 = base64.b64encode(pdf_content).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="display: inline-block; color: #fff; background-color: #dc3545; text-decoration: none; font-weight: bold; padding: 12px 24px; border-radius: 8px; margin: 10px 0;">📄 Télécharger le rapport PDF</a>'
    return href

def generate_pdf_from_html(html_content):
    """
    Génère un PDF à partir du contenu HTML.
    
    Args:
        html_content (str): Contenu HTML du rapport
        
    Returns:
        bytes: Contenu PDF ou None si erreur
    """
    try:
        # Essayer avec WeasyPrint d'abord
        if WEASYPRINT_AVAILABLE:
            try:
                from weasyprint import HTML as WeasyHTML
                pdf_bytes = WeasyHTML(string=html_content).write_pdf()
                return pdf_bytes
            except Exception as e:
                error_msg = str(e).lower()
                if any(lib in error_msg for lib in ["libpango", "libcairo", "libffi", "shared object", "ctypes"]):
                    st.warning(MSG_MISSING_LIBS)
                elif "fontconfig" in error_msg:
                    st.warning(MSG_MISSING_FONTCONFIG)
                else:
                    st.warning(MSG_WEASYPRINT_ERROR.format(error_msg))
        # Fallback avec pdfkit
        if PDFKIT_AVAILABLE:
            try:
                MARGIN = '0.75in'
                options = {
                    'page-size': 'A4',
                    'margin-top': MARGIN,
                    'margin-right': MARGIN,
                    'margin-bottom': MARGIN,
                    'margin-left': MARGIN,
                    'encoding': "UTF-8",
                    'no-outline': None,
                    'enable-local-file-access': None,
                    'quiet': ''
                }
                pdf_bytes = pdfkit.from_string(html_content, False, options=options)
                return pdf_bytes
            except Exception as e:
                error_msg = str(e)
                if "wkhtmltopdf" in error_msg:
                    st.warning(MSG_PDFKIT_MISSING)
                elif "No such file or directory" in error_msg:
                    st.warning(MSG_PDFKIT_NOT_FOUND)
                else:
                    st.warning(MSG_PDFKIT_ERROR.format(error_msg))
        # Si aucune bibliothèque n'est disponible ou si toutes ont échoué
        st.info(MSG_PDF_EXPORT_UNAVAILABLE)
        return None
    except Exception as e:
        error_msg = str(e).lower()
        if any(lib in error_msg for lib in ["libpango", "libcairo", "libffi", "shared object", "ctypes"]):
            st.error(MSG_PDF_EXPORT_FATAL)
        else:
            st.error(MSG_PDF_EXPORT_ERROR.format(error_msg))
        return None

def generate_report_pdf(df_ent, df_sol, df_comp, df_align=None):
    """
    Fonction principale pour générer le rapport (version HTML).
    Compatible avec l'ancienne interface.
    
    Args:
        df_ent (pd.DataFrame): Données des entreprises
        df_sol (pd.DataFrame): Données des solutions
        df_comp (pd.DataFrame): Données d'analyse comparative
        df_align (pd.DataFrame): Données d'alignement (optionnel)
        
    Returns:
        str: Contenu HTML du rapport
    """
    try:
        html_content = generate_html_report(df_ent, df_sol, df_comp, df_align)
        return html_content
    except Exception as e:
        st.error(MSG_REPORT_GEN_ERROR.format(str(e)))
        return None

def create_download_link(content, filename):
    """
    Crée un lien de téléchargement pour le rapport.
    
    Args:
        content: Contenu du rapport (HTML string ou PDF bytes)
        filename (str): Nom du fichier
        
    Returns:
        str: HTML du lien de téléchargement
    """
    if isinstance(content, str):
        # C'est du HTML
        return create_html_download_link(content, filename.replace('.pdf', '.html'))
    elif isinstance(content, bytes):
        # C'est du PDF
        return create_pdf_download_link(content, filename.replace('.html', '.pdf'))
    return None

def generate_report_with_export_options(df_ent, df_sol, df_comp, df_align=None):
    """
    Génère un rapport avec options d'export HTML et PDF.
    
    Args:
        df_ent (pd.DataFrame): Données des entreprises
        df_sol (pd.DataFrame): Données des solutions
        df_comp (pd.DataFrame): Données d'analyse comparative
        df_align (pd.DataFrame): Données d'alignement (optionnel)
        
    Returns:
        dict: {"html": html_content, "pdf": pdf_content}
    """
    try:
        # Générer le contenu HTML
        html_content = generate_html_report(df_ent, df_sol, df_comp, df_align)
        if not html_content:
            return {"html": None, "pdf": None}
        # Générer le PDF à partir du HTML
        pdf_content = generate_pdf_from_html(html_content)
        return {
            "html": html_content,
            "pdf": pdf_content
        }
    except Exception as e:
        st.error(MSG_REPORT_GEN_ERROR.format(str(e)))
        return {"html": None, "pdf": None}
