"""
Module de génération de rapport PDF pour l'application IVÉO BI
============================================================

Ce module permet de générer un rapport PDF complet incluant toutes les pages 
de l'application avec les filtres appliqués.

Fonctionnalités :
- Génération d'un rapport PDF multi-pages
- Inclusion de données filtrées des entreprises, solutions, et analyses
- Mise en page professionnelle avec logos et branding IVÉO
- Graphiques et tableaux formatés pour présentation client
- Sauvegarde et téléchargement du rapport

Auteur : Équipe IVÉO
Version : 1.0 - 2025.01.16
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64
from datetime import datetime
import json
from sidebar import cookies
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
import requests
from PIL import Image as PILImage
import tempfile
import os
from cairosvg import svg2png


# Couleurs IVÉO
IVEO_BLUE = HexColor("#0072B2")
IVEO_LIGHT_BLUE = HexColor("#e3f0fa")
IVEO_GRAY = HexColor("#666666")

class IVEOPDFGenerator:
    """
    Générateur de rapport PDF pour l'application IVÉO BI.
    """
    
    def __init__(self):
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.story = []
        
    def _setup_custom_styles(self):
        """Configuration des styles personnalisés IVÉO."""
        # Style pour les titres principaux
        self.styles.add(ParagraphStyle(
            name='IVEOTitle',
            parent=self.styles['Title'],
            fontSize=20,
            textColor=IVEO_BLUE,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='IVEOSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=IVEO_BLUE,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les sections
        self.styles.add(ParagraphStyle(
            name='IVEOSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=IVEO_GRAY,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='IVEONormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Style pour les légendes
        self.styles.add(ParagraphStyle(
            name='IVEOCaption',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=IVEO_GRAY,
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
    
    def _add_header(self):
        """Ajoute l'en-tête du rapport avec le logo IVÉO."""
        try:
            # Télécharger le logo IVÉO
            logo_url = "https://iveo.ca/themes/core/assets/images/content/logos/logo-iveo.svg"
            response = requests.get(logo_url)
            
            if response.status_code == 200:
                # Créer un fichier temporaire pour le logo
                with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file_path = tmp_file.name
                
                # Convertir SVG en PNG pour ReportLab
                try:
                    png_data = svg2png(url=tmp_file_path)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as png_file:
                        png_file.write(png_data)
                        png_file_path = png_file.name
                    
                    # Ajouter le logo au rapport
                    logo = Image(png_file_path, width=2*inch, height=1*inch)
                    logo.hAlign = 'CENTER'
                    self.story.append(logo)
                    
                    # Nettoyer les fichiers temporaires
                    os.unlink(tmp_file_path)
                    os.unlink(png_file_path)
                    
                except ImportError:
                    # Si cairosvg n'est pas disponible, utiliser un placeholder
                    self.story.append(Paragraph("LOGO IVÉO", self.styles['IVEOTitle']))
                    
        except Exception:
            # En cas d'erreur, utiliser un placeholder
            self.story.append(Paragraph("IVÉO - Intelligence d'Affaires", self.styles['IVEOTitle']))
        
        # Titre du rapport
        self.story.append(Paragraph("Rapport d'Analyse Comparative", self.styles['IVEOTitle']))
        
        # Date de génération
        date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        self.story.append(Paragraph(f"Généré le {date_str}", self.styles['IVEOCaption']))
        
        self.story.append(Spacer(1, 20))
    
    def _add_table_of_contents(self):
        """Ajoute une table des matières."""
        self.story.append(Paragraph("Table des matières", self.styles['IVEOSubtitle']))
        
        toc_items = [
            "1. Résumé exécutif",
            "2. Analyse des entreprises",
            "3. Analyse des solutions",
            "4. Analyse comparative",
            "5. Recommandations",
            "6. Annexes"
        ]
        
        for item in toc_items:
            self.story.append(Paragraph(item, self.styles['IVEONormal']))
        
        self.story.append(PageBreak())
    
    def _add_executive_summary(self, df_ent, df_sol, df_comp):
        """Ajoute le résumé exécutif."""
        self.story.append(Paragraph("1. Résumé exécutif", self.styles['IVEOSubtitle']))
        
        # Statistiques générales
        stats_data = []
        if df_ent is not None and not df_ent.empty:
            stats_data.append(["Nombre d'entreprises analysées", str(len(df_ent))])
        if df_sol is not None and not df_sol.empty:
            stats_data.append(["Nombre de solutions évaluées", str(len(df_sol))])
        if df_comp is not None and not df_comp.empty:
            stats_data.append(["Critères d'évaluation", str(len(df_comp))])
        
        if stats_data:
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), IVEO_LIGHT_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), IVEO_BLUE),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            self.story.append(stats_table)
        
        self.story.append(Spacer(1, 20))
        
        # Contexte du rapport
        context_text = """
        Ce rapport présente une analyse comparative complète des solutions et entreprises 
        évaluées selon les critères définis. L'analyse inclut des évaluations détaillées, 
        des comparaisons objectives et des recommandations stratégiques pour faciliter 
        la prise de décision.
        """
        self.story.append(Paragraph(context_text, self.styles['IVEONormal']))
        
        self.story.append(PageBreak())
    
    def _add_companies_analysis(self, df_ent):
        """Ajoute l'analyse des entreprises."""
        self.story.append(Paragraph("2. Analyse des entreprises", self.styles['IVEOSubtitle']))
        
        if df_ent is None or df_ent.empty:
            self.story.append(Paragraph("Aucune donnée d'entreprise disponible.", self.styles['IVEONormal']))
            return
        
        # Récupérer les entreprises sélectionnées depuis les cookies
        selected_companies = self._get_selected_companies(df_ent)
        
        # Tableau des entreprises
        if selected_companies:
            company_table = self._create_companies_table(df_ent, selected_companies)
            self.story.append(company_table)
        
        self.story.append(PageBreak())
    
    def _get_selected_companies(self, df_ent):
        """Récupère les entreprises sélectionnées depuis les cookies."""
        selected_companies = []
        try:
            selected_companies_json = cookies.get("selected_companies", "[]")
            selected_companies = json.loads(selected_companies_json)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Si aucune sélection, prendre toutes les entreprises
        if not selected_companies:
            company_column = self._find_company_column(df_ent)
            if company_column:
                selected_companies = df_ent[company_column].dropna().unique().tolist()
        
        return selected_companies
    
    def _find_company_column(self, df_ent):
        """Trouve la colonne des entreprises dans le DataFrame."""
        for col in df_ent.columns:
            if 'entreprise' in col.lower() or 'compan' in col.lower():
                return col
        return None
    
    def _create_companies_table(self, df_ent, selected_companies):
        """Crée le tableau des entreprises pour le PDF."""
        company_data = [["Entreprise", "Secteur", "Localisation", "Statut"]]
        
        for company in selected_companies[:10]:  # Limiter à 10 entreprises
            company_info = df_ent[df_ent.iloc[:, 0] == company]
            if not company_info.empty:
                info = company_info.iloc[0]
                sector = info.get("Secteur d'activité", "N/A")
                location = info.get("Localisation", "N/A")
                status = info.get("Statut", "N/A")
                company_data.append([
                    str(company)[:30],  # Limiter la longueur
                    str(sector)[:20],
                    str(location)[:20],
                    str(status)[:15]
                ])
        
        company_table = Table(company_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), IVEO_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        return company_table
    
    def _add_solutions_analysis(self, df_sol):
        """Ajoute l'analyse des solutions."""
        self.story.append(Paragraph("3. Analyse des solutions", self.styles['IVEOSubtitle']))
        
        if df_sol is None or df_sol.empty:
            self.story.append(Paragraph("Aucune donnée de solution disponible.", self.styles['IVEONormal']))
            return
        
        # Récupérer la solution sélectionnée depuis les cookies
        selected_solution = ""
        try:
            selected_solution_json = cookies.get("solution_selected", "[]")
            selected_solutions = json.loads(selected_solution_json)
            if selected_solutions:
                selected_solution = selected_solutions[0]
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Tableau des solutions
        solution_column = None
        for col in df_sol.columns:
            if 'solution' in col.lower():
                solution_column = col
                break
        
        if solution_column:
            solutions_to_show = [selected_solution] if selected_solution else df_sol[solution_column].dropna().unique().tolist()[:5]
            
            solution_data = [["Solution", "Catégorie", "Fournisseur", "Statut"]]
            
            for solution in solutions_to_show:
                solution_info = df_sol[df_sol[solution_column] == solution]
                if not solution_info.empty:
                    info = solution_info.iloc[0]
                    category = info.get("Catégorie", "N/A")
                    provider = info.get("Fournisseur", "N/A") 
                    status = info.get("Statut", "N/A")
                    solution_data.append([
                        str(solution)[:30],
                        str(category)[:20],
                        str(provider)[:20],
                        str(status)[:15]
                    ])
            
            solution_table = Table(solution_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
            solution_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), IVEO_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            self.story.append(solution_table)
        
        self.story.append(PageBreak())
    
    def _add_comparative_analysis(self, df_comp):
        """Ajoute l'analyse comparative."""
        self.story.append(Paragraph("4. Analyse comparative", self.styles['IVEOSubtitle']))
        
        if df_comp is None or df_comp.empty:
            self.story.append(Paragraph("Aucune donnée d'analyse comparative disponible.", self.styles['IVEONormal']))
            return
        
        # Récupérer les filtres appliqués
        try:
            selected_categories = json.loads(cookies.get("selected_categories", "[]"))
            selected_companies = json.loads(cookies.get("selected_companies", "[]"))
        except (json.JSONDecodeError, TypeError):
            selected_categories = []
            selected_companies = []
        
        # Résumé des filtres appliqués
        if selected_categories or selected_companies:
            self.story.append(Paragraph("Filtres appliqués:", self.styles['IVEOSection']))
            
            if selected_categories:
                cat_text = f"Catégories: {', '.join(selected_categories)}"
                self.story.append(Paragraph(cat_text, self.styles['IVEONormal']))
            
            if selected_companies:
                comp_text = f"Entreprises: {', '.join(selected_companies)}"
                self.story.append(Paragraph(comp_text, self.styles['IVEONormal']))
        
        # Tableau d'analyse comparative (premiers critères)
        if len(df_comp) > 0:
            # Prendre les premières colonnes importantes
            comparison_data = [["Critère", "Description", "Priorité"]]
            
            for idx, row in df_comp.head(15).iterrows():  # Limiter à 15 critères
                criterion = str(row.get("Fonctionnalité", "N/A"))[:40]
                description = str(row.get("description", "N/A"))[:60]
                priority = str(row.get("Exigence différenciateur", "N/A"))[:20]
                
                comparison_data.append([criterion, description, priority])
            
            comparison_table = Table(comparison_data, colWidths=[2*inch, 3*inch, 1*inch])
            comparison_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), IVEO_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            self.story.append(comparison_table)
        
        self.story.append(PageBreak())
    
    def _add_recommendations(self):
        """Ajoute les recommandations."""
        self.story.append(Paragraph("5. Recommandations", self.styles['IVEOSubtitle']))
        
        recommendations_text = """
        Basé sur l'analyse comparative réalisée, voici les principales recommandations :
        
        • Prioriser les solutions qui répondent aux exigences critiques identifiées
        • Considérer les aspects de compatibilité et d'intégration avec l'infrastructure existante
        • Évaluer le rapport coût-bénéfice pour chaque solution candidate
        • Planifier une phase pilote pour valider les solutions présélectionnées
        • Prévoir une stratégie de formation et d'accompagnement au changement
        
        Ces recommandations doivent être adaptées selon le contexte spécifique de l'organisation
        et les contraintes opérationnelles identifiées.
        """
        
        self.story.append(Paragraph(recommendations_text, self.styles['IVEONormal']))
        
        self.story.append(PageBreak())
    
    def _add_annexes(self):
        """Ajoute les annexes."""
        self.story.append(Paragraph("6. Annexes", self.styles['IVEOSubtitle']))
        
        annexes_text = """
        Méthodologie d'évaluation:
        - Critères d'évaluation binaires (0/1)
        - Pondération selon les exigences métier
        - Validation par les parties prenantes
        
        Sources des données:
        - Fichier Excel d'analyse comparative
        - Données fournisseurs
        - Évaluations internes
        
        Glossaire des termes techniques disponible sur demande.
        """
        
        self.story.append(Paragraph(annexes_text, self.styles['IVEONormal']))
    
    def generate_pdf(self, df_ent, df_sol, df_comp, df_align=None):
        """
        Génère le rapport PDF complet.
        
        Args:
            df_ent (pd.DataFrame): Données des entreprises
            df_sol (pd.DataFrame): Données des solutions
            df_comp (pd.DataFrame): Données d'analyse comparative
            df_align (pd.DataFrame): Données d'alignement (optionnel)
            
        Returns:
            BytesIO: Buffer contenant le PDF généré
        """
        # Construire le rapport section par section
        self._add_header()
        self._add_table_of_contents()
        self._add_executive_summary(df_ent, df_sol, df_comp)
        self._add_companies_analysis(df_ent)
        self._add_solutions_analysis(df_sol)
        self._add_comparative_analysis(df_comp)
        self._add_recommendations()
        self._add_annexes()
        
        # Générer le PDF
        self.doc.build(self.story)
        
        # Retourner le buffer
        self.buffer.seek(0)
        return self.buffer

def create_download_link(buffer, filename):
    """
    Crée un lien de téléchargement pour le PDF.
    
    Args:
        buffer (BytesIO): Buffer contenant le PDF
        filename (str): Nom du fichier
        
    Returns:
        str: HTML du lien de téléchargement
    """
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="display: inline-block; color: #fff; background-color: #0072B2; text-decoration: none; font-weight: bold; padding: 12px 24px; border-radius: 8px; margin: 10px 0;">📄 Télécharger le rapport PDF</a>'
    return href

def generate_report_pdf(df_ent, df_sol, df_comp, df_align=None):
    """
    Fonction principale pour générer le rapport PDF.
    
    Args:
        df_ent (pd.DataFrame): Données des entreprises
        df_sol (pd.DataFrame): Données des solutions
        df_comp (pd.DataFrame): Données d'analyse comparative
        df_align (pd.DataFrame): Données d'alignement (optionnel)
        
    Returns:
        BytesIO: Buffer contenant le PDF généré
    """
    try:
        generator = IVEOPDFGenerator()
        buffer = generator.generate_pdf(df_ent, df_sol, df_comp, df_align)
        return buffer
    except Exception as e:
        st.error(f"Erreur lors de la génération du PDF : {str(e)}")
        return None
