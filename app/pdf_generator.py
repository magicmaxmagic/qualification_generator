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
from io import BytesIO
import base64
from datetime import datetime
import json
from sidebar import cookies
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors

# =================== VARIABLES GLOBALES (labels, titres, messages, colonnes, limites) ===================
TITLE_HEADER = "IVÉO - Intelligence d'Affaires"
TITLE_REPORT = "Rapport d'Analyse Comparative"
LABEL_GENERATED_ON = "Généré le {date}"
TITLE_TOC = "Table des matières"
TOC_ITEMS = [
    "1. Résumé exécutif",
    "2. Analyse des entreprises",
    "3. Analyse des solutions",
    "4. Analyse comparative",
    "5. Recommandations",
    "6. Annexes"
]
TITLE_EXEC_SUMMARY = "1. Résumé exécutif"
LABEL_NB_COMPANIES = "Nombre d'entreprises analysées"
LABEL_NB_SOLUTIONS = "Nombre de solutions évaluées"
LABEL_NB_CRITERIA = "Critères d'évaluation"
CONTEXT_TEXT = (
    "Ce rapport présente une analyse comparative complète des solutions et entreprises "
    "évaluées selon les critères définis. L'analyse inclut des évaluations détaillées, "
    "des comparaisons objectives et des recommandations stratégiques pour faciliter "
    "la prise de décision."
)
TITLE_COMPANIES = "2. Analyse des entreprises"
LABEL_NO_COMPANY_DATA = "Aucune donnée d'entreprise disponible."
TABLE_COMPANY_HEADER = ["Entreprise", "Secteur", "Localisation", "Statut"]
COMPANY_COL_SECTOR = "Secteur d'activité"
COMPANY_COL_LOCATION = "Localisation"
COMPANY_COL_STATUS = "Statut"
COMPANY_MAX = 10
TITLE_SOLUTIONS = "3. Analyse des solutions"
LABEL_NO_SOLUTION_DATA = "Aucune donnée de solution disponible."
TABLE_SOLUTION_HEADER = ["Solution", "Catégorie", "Fournisseur", "Statut"]
SOLUTION_COL_CATEGORY = "Catégorie"
SOLUTION_COL_PROVIDER = "Fournisseur"
SOLUTION_COL_STATUS = "Statut"
SOLUTION_MAX = 5
TITLE_COMPARATIVE = "4. Analyse comparative"
LABEL_NO_COMP_DATA = "Aucune donnée d'analyse comparative disponible."
LABEL_FILTERS_APPLIED = "Filtres appliqués:"
LABEL_CATEGORIES = "Catégories: {categories}"
LABEL_COMPANIES = "Entreprises: {companies}"
TABLE_COMPARISON_HEADER = ["Type d'exigence", "Domaine", "Exigence différenciateur", "Exigence"]
COMPARISON_COL_TYPE = "Type d'exigence"
COMPARISON_COL_DOMAIN = "Domaine"
COMPARISON_COL_DIFF = "Exigence différenciateur"
COMPARISON_COL_REQ = "Exigence"
COMPARISON_MAX = 15
TITLE_RECOMMENDATIONS = "5. Recommandations"
RECOMMENDATIONS_TEXT = (
    "Basé sur l'analyse comparative réalisée, voici les principales recommandations :\n\n"
    "• Prioriser les solutions qui répondent aux exigences critiques identifiées\n"
    "• Considérer les aspects de compatibilité et d'intégration avec l'infrastructure existante\n"
    "• Évaluer le rapport coût-bénéfice pour chaque solution candidate\n"
    "• Planifier une phase pilote pour valider les solutions présélectionnées\n"
    "• Prévoir une stratégie de formation et d'accompagnement au changement\n\n"
    "Ces recommandations doivent être adaptées selon le contexte spécifique de l'organisation\n"
    "et les contraintes opérationnelles identifiées."
)
TITLE_ANNEXES = "6. Annexes"
ANNEXES_TEXT = (
    "Méthodologie d'évaluation:\n"
    "- Critères d'évaluation binaires (0/1)\n"
    "- Pondération selon les exigences métier\n"
    "- Validation par les parties prenantes\n\n"
    "Sources des données:\n"
    "- Fichier Excel d'analyse comparative\n"
    "- Données fournisseurs\n"
    "- Évaluations internes\n\n"
    "Glossaire des termes techniques disponible sur demande."
)
DOWNLOAD_LABEL = "📄 Télécharger le rapport PDF"
DOWNLOAD_STYLE = (
    "display: inline-block; color: #fff; background-color: #0072B2; text-decoration: none; "
    "font-weight: bold; padding: 12px 24px; border-radius: 8px; margin: 10px 0;"
)
ERROR_PDF_GEN = "Erreur lors de la génération du PDF : {error}"


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
        self.story.append(Paragraph(TITLE_HEADER, self.styles['IVEOTitle']))
        self.story.append(Spacer(1, 10))
        self.story.append(Paragraph(TITLE_REPORT, self.styles['IVEOTitle']))
        date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        self.story.append(Paragraph(LABEL_GENERATED_ON.format(date=date_str), self.styles['IVEOCaption']))
        self.story.append(Spacer(1, 20))
    
    def _add_table_of_contents(self):
        """Ajoute une table des matières."""
        self.story.append(Paragraph(TITLE_TOC, self.styles['IVEOSubtitle']))
        for item in TOC_ITEMS:
            self.story.append(Paragraph(item, self.styles['IVEONormal']))
        self.story.append(PageBreak())
    
    def _add_executive_summary(self, df_ent, df_sol, df_comp):
        """Ajoute le résumé exécutif."""
        self.story.append(Paragraph(TITLE_EXEC_SUMMARY, self.styles['IVEOSubtitle']))
        # Statistiques générales
        stats_data = []
        if df_ent is not None and not df_ent.empty:
            stats_data.append([LABEL_NB_COMPANIES, str(len(df_ent))])
        if df_sol is not None and not df_sol.empty:
            stats_data.append([LABEL_NB_SOLUTIONS, str(len(df_sol))])
        if df_comp is not None and not df_comp.empty:
            stats_data.append([LABEL_NB_CRITERIA, str(len(df_comp))])
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
        self.story.append(Paragraph(CONTEXT_TEXT, self.styles['IVEONormal']))
        self.story.append(PageBreak())
    
    def _add_companies_analysis(self, df_ent):
        """Ajoute l'analyse des entreprises."""
        self.story.append(Paragraph(TITLE_COMPANIES, self.styles['IVEOSubtitle']))
        if df_ent is None or df_ent.empty:
            self.story.append(Paragraph(LABEL_NO_COMPANY_DATA, self.styles['IVEONormal']))
            return
        selected_companies = self._get_selected_companies(df_ent)
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
        company_data = [TABLE_COMPANY_HEADER]
        for company in selected_companies[:COMPANY_MAX]:
            company_info = df_ent[df_ent.iloc[:, 0] == company]
            if not company_info.empty:
                info = company_info.iloc[0]
                sector = info.get(COMPANY_COL_SECTOR, "N/A")
                location = info.get(COMPANY_COL_LOCATION, "N/A")
                status = info.get(COMPANY_COL_STATUS, "N/A")
                company_data.append([
                    str(company)[:30],
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
        self.story.append(Paragraph(TITLE_SOLUTIONS, self.styles['IVEOSubtitle']))
        if df_sol is None or df_sol.empty:
            self.story.append(Paragraph(LABEL_NO_SOLUTION_DATA, self.styles['IVEONormal']))
            return
        selected_solution = ""
        try:
            selected_solution_json = cookies.get("solution_selected", "[]")
            selected_solutions = json.loads(selected_solution_json)
            if selected_solutions:
                selected_solution = selected_solutions[0]
        except (json.JSONDecodeError, TypeError):
            pass
        solution_column = next((col for col in df_sol.columns if 'solution' in col.lower()), None)
        if solution_column:
            solutions_to_show = [selected_solution] if selected_solution else df_sol[solution_column].dropna().unique().tolist()[:SOLUTION_MAX]
            solution_data = [TABLE_SOLUTION_HEADER]
            for solution in solutions_to_show:
                solution_info = df_sol[df_sol[solution_column] == solution]
                if not solution_info.empty:
                    info = solution_info.iloc[0]
                    category = info.get(SOLUTION_COL_CATEGORY, "N/A")
                    provider = info.get(SOLUTION_COL_PROVIDER, "N/A") 
                    status = info.get(SOLUTION_COL_STATUS, "N/A")
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
        self.story.append(Paragraph(TITLE_COMPARATIVE, self.styles['IVEOSubtitle']))
        if df_comp is None or df_comp.empty:
            self.story.append(Paragraph(LABEL_NO_COMP_DATA, self.styles['IVEONormal']))
            return
        try:
            selected_categories = json.loads(cookies.get("selected_categories", "[]"))
            selected_companies = json.loads(cookies.get("selected_companies", "[]"))
        except (json.JSONDecodeError, TypeError):
            selected_categories = []
            selected_companies = []
        if selected_categories or selected_companies:
            self.story.append(Paragraph(LABEL_FILTERS_APPLIED, self.styles['IVEOSection']))
            if selected_categories:
                cat_text = LABEL_CATEGORIES.format(categories=", ".join(selected_categories))
                self.story.append(Paragraph(cat_text, self.styles['IVEONormal']))
            if selected_companies:
                comp_text = LABEL_COMPANIES.format(companies=", ".join(selected_companies))
                self.story.append(Paragraph(comp_text, self.styles['IVEONormal']))
        if len(df_comp) > 0:
            comparison_data = [TABLE_COMPARISON_HEADER]
            for _, row in df_comp.head(COMPARISON_MAX).iterrows():
                type_exigence = str(row.get(COMPARISON_COL_TYPE, "N/A"))[:30]
                domaine = str(row.get(COMPARISON_COL_DOMAIN, "N/A"))[:30]
                exigence_diff = str(row.get(COMPARISON_COL_DIFF, "N/A"))[:20]
                exigence = str(row.get(COMPARISON_COL_REQ, "N/A"))[:40]
                comparison_data.append([type_exigence, domaine, exigence_diff, exigence])
            comparison_table = Table(comparison_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
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
        self.story.append(Paragraph(TITLE_RECOMMENDATIONS, self.styles['IVEOSubtitle']))
        self.story.append(Paragraph(RECOMMENDATIONS_TEXT, self.styles['IVEONormal']))
        self.story.append(PageBreak())
    
    def _add_annexes(self):
        """Ajoute les annexes."""
        self.story.append(Paragraph(TITLE_ANNEXES, self.styles['IVEOSubtitle']))
        self.story.append(Paragraph(ANNEXES_TEXT, self.styles['IVEONormal']))
    
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
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="{DOWNLOAD_STYLE}">{DOWNLOAD_LABEL}</a>'
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
        st.error(ERROR_PDF_GEN.format(error=str(e)))
        return None
