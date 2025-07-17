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
            bars = ax.bar(range(len(sector_counts)), sector_counts.values, 
                         color=self.theme_color, alpha=0.8)
            
            # Personnalisation
            ax.set_title('Répartition des entreprises par secteur', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Secteurs d\'activité', fontsize=12)
            ax.set_ylabel('Nombre d\'entreprises', fontsize=12)
            ax.set_xticks(range(len(sector_counts)))
            ax.set_xticklabels(sector_counts.index, rotation=45, ha='right')
            
            # Ajouter les valeurs sur les barres
            for bar, value in zip(bars, sector_counts.values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(value), ha='center', va='bottom', fontweight='bold')
            
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
            print(f"Erreur lors de la création du graphique entreprises: {e}")
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
            ax.set_title('Répartition des solutions par catégorie', 
                        fontsize=16, fontweight='bold', pad=20)
            
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
            print(f"Erreur lors de la création du graphique solutions: {e}")
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
            ax.set_title('Nombre de critères par catégorie', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Nombre de critères', fontsize=12)
            ax.set_ylabel('Catégories', fontsize=12)
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
            print(f"Erreur lors de la création du graphique comparatif: {e}")
            return None

def add_charts_to_pdf_generator(generator_class):
    """
    Ajoute les fonctionnalités graphiques au générateur PDF.
    """
    def _add_charts_to_companies_analysis(self, df_ent):
        """Version améliorée avec graphiques."""
        self.story.append(Paragraph("2. Analyse des entreprises", self.styles['IVEOSubtitle']))
        
        if df_ent is None or df_ent.empty:
            self.story.append(Paragraph("Aucune donnée d'entreprise disponible.", self.styles['IVEONormal']))
            return
        
        # Récupérer les entreprises sélectionnées
        selected_companies = self._get_selected_companies(df_ent)
        
        # Ajouter le graphique
        chart_generator = PDFChartGenerator()
        chart = chart_generator.create_companies_chart(df_ent, selected_companies)
        
        if chart:
            self.story.append(chart)
            self.story.append(Spacer(1, 12))
            self.story.append(Paragraph("Graphique 1: Répartition des entreprises par secteur", self.styles['IVEOCaption']))
            self.story.append(Spacer(1, 20))
        
        # Tableau des entreprises
        if selected_companies:
            company_table = self._create_companies_table(df_ent, selected_companies)
            self.story.append(company_table)
        
        self.story.append(PageBreak())
    
    def _add_charts_to_solutions_analysis(self, df_sol):
        """Version améliorée avec graphiques."""
        self.story.append(Paragraph("3. Analyse des solutions", self.styles['IVEOSubtitle']))
        
        if df_sol is None or df_sol.empty:
            self.story.append(Paragraph("Aucune donnée de solution disponible.", self.styles['IVEONormal']))
            return
        
        # Ajouter le graphique
        chart_generator = PDFChartGenerator()
        chart = chart_generator.create_solutions_chart(df_sol)
        
        if chart:
            self.story.append(chart)
            self.story.append(Spacer(1, 12))
            self.story.append(Paragraph("Graphique 2: Répartition des solutions par catégorie", self.styles['IVEOCaption']))
            self.story.append(Spacer(1, 20))
        
        # Tableau des solutions (code existant)
        # ... (garder le code existant)
        
        self.story.append(PageBreak())
    
    def _add_charts_to_comparative_analysis(self, df_comp):
        """Version améliorée avec graphiques."""
        self.story.append(Paragraph("4. Analyse comparative", self.styles['IVEOSubtitle']))
        
        if df_comp is None or df_comp.empty:
            self.story.append(Paragraph("Aucune donnée d'analyse comparative disponible.", self.styles['IVEONormal']))
            return
        
        # Ajouter le graphique
        chart_generator = PDFChartGenerator()
        chart = chart_generator.create_comparative_chart(df_comp)
        
        if chart:
            self.story.append(chart)
            self.story.append(Spacer(1, 12))
            self.story.append(Paragraph("Graphique 3: Critères d'évaluation par catégorie", self.styles['IVEOCaption']))
            self.story.append(Spacer(1, 20))
        
        # Tableau comparatif (code existant)
        # ... (garder le code existant)
        
        self.story.append(PageBreak())
    
    # Remplacer les méthodes existantes
    generator_class._add_companies_analysis = _add_charts_to_companies_analysis
    generator_class._add_solutions_analysis = _add_charts_to_solutions_analysis
    generator_class._add_comparative_analysis = _add_charts_to_comparative_analysis
    
    return generator_class
