"""
Module d'amélioration du générateur PDF avec graphiques et statistiques
====================================================================

Ce module étend le générateur PDF de base avec des fonctionnalités avancées :
- Graphiques en barres et camemberts
- Analyses statistiques des données
- Visualisations des filtres appliqués
- Métriques de performance

Version : 1.1 - 2025.01.16
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import tempfile
import os

from reportlab.platypus import Image, Spacer, Paragraph, PageBreak
from reportlab.lib.units import inch

# =================== VARIABLES D'ÉTAT ET MESSAGES ===================
MSG_NO_COMPANY_DATA = "Aucune donnée d'entreprise disponible."
MSG_NO_SOLUTION_DATA = "Aucune donnée de solution disponible."
MSG_NO_COMPARATIVE_DATA = "Aucune donnée d'analyse comparative disponible."
TITLE_COMPANIES_ANALYSIS = "2. Analyse des entreprises"
TITLE_SOLUTIONS_ANALYSIS = "3. Analyse des solutions"
TITLE_COMPARATIVE_ANALYSIS = "4. Analyse comparative"
CAPTION_COMPANIES_CHART = "Graphique 1: Répartition des entreprises par secteur"
CAPTION_SOLUTIONS_CHART = "Graphique 2: Répartition des solutions par catégorie"
CAPTION_COMPARATIVE_CHART = "Graphique 3: Critères d'évaluation par catégorie"
ERR_COMPANIES_CHART = "Erreur lors de la création du graphique entreprises: {}"
ERR_SOLUTIONS_CHART = "Erreur lors de la création du graphique solutions: {}"
ERR_COMPARATIVE_CHART = "Erreur lors de la création du graphique comparatif: {}"

# Configuration matplotlib pour de meilleurs graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class PDFChartGenerator:
    """
    Générateur de graphiques pour les rapports PDF.
    """
    
    def __init__(self, theme_color="#0072B2"):
        self.theme_color = theme_color
        self.fig_size = (10, 6)
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        
    def create_companies_chart(self, df_ent, selected_companies=None):
        """
        Crée un graphique des entreprises par secteur.
        
        Returns:
            Image: Objet Image ReportLab
        """
        if df_ent is None or df_ent.empty:
            return None
            
        try:
            # Identifier la colonne secteur
            sector_column = None
            for col in df_ent.columns:
                if 'secteur' in col.lower():
                    sector_column = col
                    break
            if sector_column is None:
                return None
            # Filtrer les données si nécessaire
            if selected_companies:
                company_col = df_ent.columns[0]  # Première colonne = entreprises
                df_filtered = df_ent[df_ent[company_col].isin(selected_companies)]
            else:
                df_filtered = df_ent
            # Compter les entreprises par secteur
            sector_counts = df_filtered[sector_column].value_counts()
            # Créer le graphique
            fig, ax = plt.subplots(figsize=self.fig_size)
            # Graphique en barres
            bars = ax.bar(range(len(sector_counts)), sector_counts.values, color=self.theme_color, alpha=0.8)
            # Personnalisation
            ax.set_title(CAPTION_COMPANIES_CHART, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel("Secteurs d'activité", fontsize=12)
            ax.set_ylabel("Nombre d'entreprises", fontsize=12)
            ax.set_xticks(range(len(sector_counts)))
            ax.set_xticklabels(sector_counts.index, rotation=45, ha='right')
            # Ajouter les valeurs sur les barres
            for bar, value in zip(bars, sector_counts.values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(value), ha='center', va='bottom', fontweight='bold')
            plt.tight_layout()
            # Sauvegarder en tant qu'image temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                plt.savefig(tmp.name, format='png', dpi=300, bbox_inches='tight')
                tmp_path = tmp.name
            plt.close()
            # Créer l'objet Image ReportLab
            img = Image(tmp_path, width=6*inch, height=3.6*inch)
            # Nettoyer le fichier temporaire
            os.unlink(tmp_path)
            return img
        except Exception as e:
            print(ERR_COMPANIES_CHART.format(e))
            return None
    
    def create_solutions_chart(self, df_sol):
        """
        Crée un graphique des solutions par catégorie.
        
        Returns:
            Image: Objet Image ReportLab
        """
        if df_sol is None or df_sol.empty:
            return None
            
        try:
            # Identifier la colonne catégorie
            category_column = None
            for col in df_sol.columns:
                if 'catégorie' in col.lower() or 'category' in col.lower():
                    category_column = col
                    break
            if category_column is None:
                return None
            # Compter les solutions par catégorie
            category_counts = df_sol[category_column].value_counts()
            # Créer le graphique en camembert
            fig, ax = plt.subplots(figsize=self.fig_size)
            # Palette de couleurs
            cmap = cm.get_cmap('Set3')
            colors = [cmap(i) for i in range(len(category_counts))]
            wedges, texts, autotexts = ax.pie(
                category_counts.values,
                labels=category_counts.index,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10}
            )
            # Personnalisation
            ax.set_title(CAPTION_SOLUTIONS_CHART, fontsize=16, fontweight='bold', pad=20)
            # Améliorer la lisibilité
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            plt.tight_layout()
            # Sauvegarder en tant qu'image temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                plt.savefig(tmp.name, format='png', dpi=300, bbox_inches='tight')
                tmp_path = tmp.name
            plt.close()
            # Créer l'objet Image ReportLab
            img = Image(tmp_path, width=6*inch, height=3.6*inch)
            # Nettoyer le fichier temporaire
            os.unlink(tmp_path)
            return img
        except Exception as e:
            print(ERR_SOLUTIONS_CHART.format(e))
            return None
    
    def create_comparative_chart(self, df_comp):
        """
        Crée un graphique d'analyse comparative.
        
        Returns:
            Image: Objet Image ReportLab
        """
        if df_comp is None or df_comp.empty:
            return None
            
        try:
            # Analyser les critères par catégorie
            category_column = None
            for col in df_comp.columns:
                if 'catégorie' in col.lower():
                    category_column = col
                    break
            if category_column is None:
                return None
            # Compter les critères par catégorie
            category_counts = df_comp[category_column].value_counts()
            # Créer le graphique
            fig, ax = plt.subplots(figsize=self.fig_size)
            # Graphique en barres horizontales
            bars = ax.barh(range(len(category_counts)), category_counts.values, color=self.theme_color, alpha=0.8)
            # Personnalisation
            ax.set_title(CAPTION_COMPARATIVE_CHART, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel("Nombre de critères", fontsize=12)
            ax.set_ylabel("Catégories", fontsize=12)
            ax.set_yticks(range(len(category_counts)))
            ax.set_yticklabels(category_counts.index)
            # Ajouter les valeurs
            for i, (bar, value) in enumerate(zip(bars, category_counts.values)):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, str(value), ha='left', va='center', fontweight='bold')
            plt.tight_layout()
            # Sauvegarder en tant qu'image temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                plt.savefig(tmp.name, format='png', dpi=300, bbox_inches='tight')
                tmp_path = tmp.name
            plt.close()
            # Créer l'objet Image ReportLab
            img = Image(tmp_path, width=6*inch, height=3.6*inch)
            # Nettoyer le fichier temporaire
            os.unlink(tmp_path)
            return img
        except Exception as e:
            print(ERR_COMPARATIVE_CHART.format(e))
            return None

def add_charts_to_pdf_generator(generator_class):
    """
    Ajoute les fonctionnalités graphiques au générateur PDF.
    """

    def _handle_empty_df(self, title):
        if "entreprise" in title.lower():
            self.story.append(Paragraph(MSG_NO_COMPANY_DATA, self.styles['IVEONormal']))
        elif "solution" in title.lower():
            self.story.append(Paragraph(MSG_NO_SOLUTION_DATA, self.styles['IVEONormal']))
        else:
            self.story.append(Paragraph(MSG_NO_COMPARATIVE_DATA, self.styles['IVEONormal']))

    def _add_chart_and_table(self, chart, caption, table_func, df, selected):
        if chart:
            self.story.append(chart)
            self.story.append(Spacer(1, 12))
            self.story.append(Paragraph(caption, self.styles['IVEOCaption']))
            self.story.append(Spacer(1, 20))
        if table_func and selected:
            table = table_func(df, selected)
            self.story.append(table)

    def _add_chart_section(self, title, df, chart_func, caption, table_func=None, get_selected_func=None):
        self.story.append(Paragraph(title, self.styles['IVEOSubtitle']))
        if df is None or df.empty:
            self._handle_empty_df(title)
            return
        chart_generator = PDFChartGenerator()
        selected = get_selected_func(df) if get_selected_func else None
        chart = chart_func(chart_generator, df, selected) if selected is not None else chart_func(chart_generator, df)
        self._add_chart_and_table(chart, caption, table_func, df, selected)
        self.story.append(PageBreak())

    def _add_charts_to_companies_analysis(self, df_ent):
        """Version améliorée avec graphiques."""
        self._add_chart_section(
            TITLE_COMPANIES_ANALYSIS,
            df_ent,
            lambda gen, df, sel: gen.create_companies_chart(df, sel),
            CAPTION_COMPANIES_CHART,
            table_func=self._create_companies_table,
            get_selected_func=self._get_selected_companies
        )

    def _add_charts_to_solutions_analysis(self, df_sol):
        """Version améliorée avec graphiques."""
        self._add_chart_section(
            TITLE_SOLUTIONS_ANALYSIS,
            df_sol,
            lambda gen, df: gen.create_solutions_chart(df),
            CAPTION_SOLUTIONS_CHART
        )
        # Tableau des solutions (code existant)
        # ... (garder le code existant)
        self.story.append(PageBreak())

    def _add_charts_to_comparative_analysis(self, df_comp):
        """Version améliorée avec graphiques."""
        self._add_chart_section(
            TITLE_COMPARATIVE_ANALYSIS,
            df_comp,
            lambda gen, df: gen.create_comparative_chart(df),
            CAPTION_COMPARATIVE_CHART
        )
        self.story.append(PageBreak())

    # Remplacer les méthodes existantes
    generator_class._add_companies_analysis = _add_charts_to_companies_analysis
    generator_class._add_solutions_analysis = _add_charts_to_solutions_analysis
    generator_class._add_comparative_analysis = _add_charts_to_comparative_analysis

    return generator_class
