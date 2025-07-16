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
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', Arial, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            background: white;
            font-size: 13px;
            padding: 20px;
        }
        
        .report-container {
            max-width: 210mm;
            margin: 0 auto;
            background: white;
            padding: 0;
        }
        
        .header {
            background: linear-gradient(135deg, #0072B2 0%, #1a8bb8 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 8px;
        }
        
        .header-content {
            position: relative;
            z-index: 2;
        }
        
        .header h1 {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header h2 {
            font-size: 1.5em;
            font-weight: 400;
            margin-bottom: 15px;
            opacity: 0.95;
        }
        
        .header .meta {
            font-size: 1em;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .section {
            margin-bottom: 40px;
            padding: 0;
            page-break-inside: avoid;
        }
        
        .section h2 {
            color: #0072B2;
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e3f0fa;
            page-break-after: avoid;
        }
        
        .section h3 {
            color: #4a5568;
            font-size: 1.3em;
            font-weight: 600;
            margin: 25px 0 15px 0;
            page-break-after: avoid;
        }
        
        .section p {
            margin-bottom: 15px;
            font-size: 1em;
            line-height: 1.6;
            text-align: justify;
        }
        
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
            page-break-inside: avoid;
            max-width: 100%;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border: 1px solid #e2e8f0;
            font-size: 0.9em;
            page-break-inside: avoid;
        }
        
        th {
            background: #0072B2;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85em;
            border-bottom: 2px solid #005a8f;
            page-break-inside: avoid;
        }
        
        td {
            padding: 10px 8px;
            border-bottom: 1px solid #e2e8f0;
            border-right: 1px solid #f1f5f9;
            vertical-align: top;
            font-size: 0.9em;
            word-wrap: break-word;
            max-width: 150px;
        }
        
        tr:nth-child(even) {
            background: #f8fafc;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 25px 0;
            page-break-inside: avoid;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
            page-break-inside: avoid;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: #0072B2;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: 700;
            color: #0072B2;
            margin-bottom: 8px;
            line-height: 1;
        }
        
        .stat-label {
            color: #4a5568;
            font-size: 0.95em;
            font-weight: 500;
            margin: 0;
        }
        
        .company-card {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #0072B2;
            page-break-inside: avoid;
        }
        
        .company-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .company-logo {
            max-width: 80px;
            max-height: 60px;
            border-radius: 4px;
        }
        
        .company-title h3 {
            font-size: 1.4em;
            font-weight: 700;
            color: #0072B2;
            margin: 0 0 5px 0;
        }
        
        .company-title .sector {
            color: #6b7280;
            font-size: 1em;
            font-weight: 500;
        }
        
        .company-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .detail-item {
            padding: 10px;
            background: #f8fafc;
            border-radius: 4px;
            border-left: 2px solid #0072B2;
            font-size: 0.9em;
        }
        
        .detail-item strong {
            color: #374151;
            font-weight: 600;
        }
        
        .toc {
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            margin-bottom: 25px;
            page-break-inside: avoid;
        }
        
        .toc h2 {
            color: #0072B2;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 2px solid #e3f0fa;
            padding-bottom: 10px;
        }
        
        .toc ol {
            padding-left: 20px;
        }
        
        .toc li {
            margin-bottom: 8px;
            padding: 5px 0;
        }
        
        .toc a {
            color: #4a5568;
            text-decoration: none;
            font-weight: 500;
        }
        
        .toc a:hover {
            color: #0072B2;
        }
        
        .executive-summary {
            background: #f8fafc;
            padding: 25px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #e2e8f0;
            page-break-inside: avoid;
        }
        
        .recommendations {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #10b981;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .recommendations h3 {
            color: #10b981;
            margin-bottom: 15px;
        }
        
        .recommendations ul {
            padding-left: 20px;
        }
        
        .recommendations li {
            margin-bottom: 10px;
            padding: 5px 0;
            line-height: 1.5;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .footer {
            background: #f8fafc;
            padding: 25px;
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
            border-top: 1px solid #e2e8f0;
            margin-top: 40px;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        .highlight {
            background: #e3f0fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #0072B2;
            margin: 15px 0;
            page-break-inside: avoid;
        }
        
        .image-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .image-item {
            background: white;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            text-align: center;
        }
        
        .image-item img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        
        /* Optimisations pour l'impression */
        @media print {
            body {
                font-size: 11px;
                line-height: 1.4;
                background: white;
                padding: 10px;
            }
            
            .report-container {
                max-width: none;
                margin: 0;
                padding: 0;
            }
            
            .section {
                margin-bottom: 25px;
            }
            
            .company-card,
            .stat-card,
            .table-container,
            .toc,
            .executive-summary,
            .recommendations,
            .highlight {
                page-break-inside: avoid;
            }
            
            table {
                font-size: 0.8em;
            }
            
            th {
                padding: 8px 6px;
            }
            
            td {
                padding: 6px 6px;
                max-width: 120px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .header h2 {
                font-size: 1.3em;
            }
        }
        
        /* Responsive pour écrans plus petits */
        @media screen and (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .company-details {
                grid-template-columns: 1fr;
            }
            
            .company-header {
                flex-direction: column;
                text-align: center;
            }
            
            table {
                font-size: 0.8em;
            }
            
            th, td {
                padding: 6px 4px;
            }
        }
    </style>
    """
    
    # Récupérer les données des cookies
    selected_companies = []
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
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rapport IVÉO - Analyse Comparative</title>
        <meta name="description" content="Rapport d'analyse comparative IVÉO - Intelligence d'affaires">
        <meta name="author" content="IVÉO">
        <meta name="generator" content="IVÉO BI Platform">
        {css}
    </head>
    <body>
        <div class="report-container">
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
    <div class="header">
        <div class="header-content">
            <h1>IVÉO</h1>
            <h2>Rapport d'Analyse Comparative</h2>
            <div class="meta">
                <p>Intelligence d'Affaires • Analyse Stratégique</p>
                <p>Généré le {date_str}</p>
            </div>
        </div>
    </div>
    """

def _generate_table_of_contents():
    """Génère une table des matières professionnelle."""
    return """
    <div class="section">
        <div class="toc">
            <h2>Table des matières</h2>
            <ol>
                <li><a href="#resume">Résumé exécutif</a></li>
                <li><a href="#entreprises">Analyse des entreprises</a></li>
                <li><a href="#solutions">Analyse des solutions</a></li>
                <li><a href="#comparative">Analyse comparative</a></li>
                <li><a href="#recommandations">Recommandations stratégiques</a></li>
                <li><a href="#methodologie">Méthodologie</a></li>
                <li><a href="#annexes">Annexes</a></li>
            </ol>
        </div>
    </div>
    """

def _generate_executive_summary(df_ent, df_sol, df_comp):
    """Génère un résumé exécutif professionnel avec statistiques et insights."""
    stats = []
    
    # Statistiques principales
    if df_ent is not None and not df_ent.empty:
        stats.append(f'<div class="stat-card"><p class="stat-number">{len(df_ent)}</p><p class="stat-label">Entreprises analysées</p></div>')
    
    if df_sol is not None and not df_sol.empty:
        stats.append(f'<div class="stat-card"><p class="stat-number">{len(df_sol)}</p><p class="stat-label">Solutions évaluées</p></div>')
    
    if df_comp is not None and not df_comp.empty:
        stats.append(f'<div class="stat-card"><p class="stat-number">{len(df_comp)}</p><p class="stat-label">Critères d\'évaluation</p></div>')
    
    # Statistiques additionnelles
    if df_ent is not None and not df_ent.empty:
        secteurs = df_ent.get("Secteur d'activité", pd.Series()).dropna().nunique()
        if secteurs > 0:
            stats.append(f'<div class="stat-card"><p class="stat-number">{secteurs}</p><p class="stat-label">Secteurs représentés</p></div>')
    
    stats_html = ''.join(stats)
    
    # Génération d'insights automatiques
    insights = []
    if df_ent is not None and not df_ent.empty:
        insights.append(f"L'analyse porte sur {len(df_ent)} entreprises représentant une diversité sectorielle significative.")
    
    if df_sol is not None and not df_sol.empty:
        insights.append(f"L'évaluation comprend {len(df_sol)} solutions technologiques répondant à différents besoins organisationnels.")
    
    if df_comp is not None and not df_comp.empty:
        insights.append(f"L'analyse comparative s'appuie sur {len(df_comp)} critères d'évaluation structurés et objectifs.")
    
    insights_html = ' '.join(insights)
    
    return f"""
    <div class="section page-break" id="resume">
        <h2>1. Résumé exécutif</h2>
        
        <div class="executive-summary">
            <div class="stats-grid">
                {stats_html}
            </div>
            
            <div class="highlight">
                <h3>Contexte et objectifs</h3>
                <p>
                    Ce rapport présente une analyse comparative approfondie des solutions et entreprises 
                    évaluées selon une méthodologie rigoureuse. L'objectif est de fournir une base 
                    décisionnelle solide pour orienter les choix stratégiques de l'organisation.
                </p>
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

def _generate_companies_section(df_ent, selected_companies):
    """Génère la section des entreprises avec toutes les informations."""
    if df_ent is None or df_ent.empty:
        return """
        <div class="section page-break" id="entreprises">
            <h2>2. Analyse des entreprises</h2>
            <p>Aucune donnée d'entreprise disponible.</p>
        </div>
        """
    
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
    <div class="section page-break" id="entreprises">
        <h2>2. Analyse des entreprises</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <p class="stat-number">{len(selected_companies)}</p>
                <p class="stat-label">Entreprises analysées</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{len(set(comp['secteur'] for comp in companies_info))}</p>
                <p class="stat-label">Secteurs représentés</p>
            </div>
        </div>
        
        <h3>Profils détaillés des entreprises</h3>
        {companies_html}
        
        <h3>Tableau récapitulatif des entreprises</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 25%;">Entreprise</th>
                        <th style="width: 20%;">Secteur</th>
                        <th style="width: 20%;">Localisation</th>
                        <th style="width: 15%;">Statut</th>
                        <th style="width: 20%;">Site web</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </div>
    </div>
    """

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
        return """
        <div class="section page-break" id="solutions">
            <h2>3. Analyse des solutions</h2>
            <p>Aucune donnée de solution disponible.</p>
        </div>
        """
    
    # Trouver la colonne des solutions
    solution_column = None
    for col in df_sol.columns:
        if 'solution' in col.lower():
            solution_column = col
            break
    
    if solution_column is None:
        return """
        <div class="section page-break" id="solutions">
            <h2>3. Analyse des solutions</h2>
            <p>Aucune colonne de solutions trouvée.</p>
        </div>
        """
    
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
    <table>
        <thead>
            <tr>
                <th>Solution</th>
                <th>Catégorie</th>
                <th>Fournisseur</th>
                <th>Statut</th>
                <th>Site web</th>
            </tr>
        </thead>
        <tbody>
            {''.join(table_rows)}
        </tbody>
    </table>
    """
    
    return f"""
    <div class="section page-break" id="solutions">
        <h2>3. Analyse des solutions</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <p class="stat-number">{len(solutions_to_show)}</p>
                <p class="stat-label">Solutions analysées</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{len(solution_images) if solution_images else 0}</p>
                <p class="stat-label">Images associées</p>
            </div>
        </div>
        
        <h3>Détails des solutions</h3>
        {solutions_html}
        
        <h3>Tableau récapitulatif</h3>
        {table_html}
        
        <p>
            <strong>Solution sélectionnée :</strong> {selected_solution if selected_solution else "Aucune sélection spécifique"}
        </p>
