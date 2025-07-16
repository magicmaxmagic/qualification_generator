# IVÉO BI - Tableau de Bord Business Intelligence

## Description

IVÉO BI est une application de tableau de bord développée avec Streamlit pour l'analyse et la comparaison de solutions de stationnement intelligent. Cette plateforme permet d'analyser, comparer et évaluer différentes entreprises et solutions technologiques dans le domaine du stationnement intelligent.

## Installation et Démarrage

### Installation locale
```bash
# Cloner le repository
git clone [url-du-repo]
cd BI

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run main.py
```

### Déploiement Cloud
Pour le déploiement sur plateformes cloud (Streamlit Cloud, Render, Heroku, etc.), les dépendances PDF (pdfkit et weasyprint) peuvent causer des erreurs à cause des bibliothèques système manquantes.

**Solution automatique :** L'application détecte automatiquement l'environnement cloud et désactive l'export PDF. Seul l'export HTML reste disponible.

**En cas d'erreur d'installation :**
1. Commentez ces lignes dans requirements.txt :
   ```
   # pdfkit>=1.0.0
   # weasyprint>=60.0
   ```
2. Redéployez l'application

## Architecture de l'Application

### Structure des Fichiers
```
BI/
├── main.py                     # Point d'entrée principal
├── sidebar.py                  # Configuration de la barre latérale
├── requirements.txt            # Dépendances Python
├── Dockerfile                  # Configuration Docker
├── app/
│   ├── __init__.py
│   ├── utils.py               # Fonctions utilitaires
│   ├── pdf_generator.py       # Génération PDF avec ReportLab
│   ├── pdf_generator_html.py  # Génération HTML et PDF
│   └── pages/
│       ├── home.py            # Page d'accueil
│       ├── entreprise.py      # Analyse des entreprises
│       ├── solution.py        # Catalogue des solutions
│       ├── analyse_comparative.py  # Comparaison interactive
│       └── chatbot.py         # Assistant IA
└── uploads/                   # Fichiers de données (ignorés par Git)
```

### Composants Principaux

#### 1. Interface Utilisateur (main.py)
- Configuration de l'application Streamlit
- Navigation principale entre les pages
- Gestion des sessions utilisateur
- Chargement des styles CSS

#### 2. Barre Latérale (sidebar.py)
- Système de filtrage dynamique
- Sélection d'entreprises et critères
- Gestion des cookies pour la persistance
- Export de rapports PDF/HTML

#### 3. Gestion des Données (app/utils.py)
- Chargement et validation des fichiers Excel
- Nettoyage et transformation des données
- Fonctions de cache pour les performances
- Validation des formats de données

#### 4. Génération de Rapports
- **pdf_generator.py** : Rapports PDF avec ReportLab (graphiques, tableaux)
- **pdf_generator_html.py** : Rapports HTML et conversion PDF avec WeasyPrint
- Détection automatique de l'environnement cloud
- Fallback HTML si bibliothèques PDF indisponibles

## Fonctionnalités Détaillées

### 1. Page d'Accueil (home.py)
- Vue d'ensemble du projet IVÉO
- Navigation vers les modules spécialisés
- Présentation de la mission et des objectifs
- Métriques générales du projet

### 2. Analyse des Entreprises (entreprise.py)
- Profils détaillés des entreprises partenaires
- Informations de contact et données organisationnelles
- Visualisations interactives des données
- Géolocalisation des entreprises
- Filtrage par secteur et localisation

### 3. Solutions Technologiques (solution.py)
- Catalogue complet des solutions de stationnement
- Spécifications techniques détaillées
- Comparaisons fonctionnelles
- Gestion des images et documentation
- Filtrage par catégorie et fournisseur

### 4. Analyse Comparative (analyse_comparative.py)
- Grille d'évaluation interactive avec notation binaire (0/1)
- Filtrage dynamique par catégorie et niveau d'exigence
- Sélection personnalisée d'entreprises
- Informations complémentaires avec justifications
- Interface moderne avec navigation fluide
- Graphiques radar pour comparaisons visuelles

### 5. Assistant IA (chatbot.py)
- Interface conversationnelle avec OpenAI
- Analyse contextuelle des données
- Recommandations personnalisées
- Support pour questions techniques

## Technologies et Dépendances

### Frameworks Principal
- **Streamlit** : Framework d'application web pour Python
- **Pandas** : Manipulation et analyse de données
- **Plotly** : Visualisations interactives et graphiques

### Traitement des Données
- **OpenPyXL** : Lecture et écriture de fichiers Excel
- **Geopy** : Géolocalisation et services cartographiques
- **streamlit-aggrid** : Tableaux interactifs avancés

### Génération de Rapports
- **ReportLab** : Génération de PDF programmatique
- **WeasyPrint** : Conversion HTML vers PDF (environnement local)
- **pdfkit** : Alternative pour génération PDF
- **Pillow** : Traitement d'images

### Visualisations
- **Matplotlib** : Graphiques statistiques
- **Seaborn** : Visualisations statistiques avancées
- **cairosvg** : Rendu vectoriel SVG

### Gestion des Sessions
- **streamlit-cookies-manager** : Persistance des préférences utilisateur
- **OpenAI** : Intelligence artificielle conversationnelle

## Format des Données

### Structure du Fichier Excel
Le fichier Excel principal doit contenir plusieurs feuilles :

#### Feuille "Analyse comparative"
| Colonnes de Base | Colonnes d'Entreprises (alternées) |
|------------------|-----------------------------------|
| Type d'exigence | Entreprise 1 |
| Domaine | Information complémentaire 1 |
| Exigence différenciateur | Entreprise 2 |
| Exigence | Information complémentaire 2 |
| Description | ... |
| Catégorie | |

#### Feuille "Entreprises"
- Nom de l'entreprise
- Secteur d'activité
- Localisation
- Statut
- Site web
- Description
- URL du logo

#### Feuille "Solutions"
- Nom de la solution
- Catégorie
- Fournisseur
- Statut
- Description
- Site web
- URL du logo
- URL de vidéo

### Formats de Données Acceptés
- **Scores d'évaluation** : Valeurs binaires (0, 1, "Oui", "Non")
- **Informations complémentaires** : Texte libre avec justifications
- **URLs** : Liens web valides pour sites et médias
- **Catégories** : Classification hiérarchique des fonctionnalités

## Sécurité et Confidentialité

### Protection des Données
- Fichiers sensibles exclus du versioning (.gitignore)
- Données d'entreprises jamais versionnées
- Variables d'environnement pour informations confidentielles
- Contrôle d'accès strict aux informations sensibles

### Fichiers Protégés
```
uploads/           # Données d'entreprises
*.xlsx, *.xls     # Fichiers Excel sensibles
.env              # Variables d'environnement
secrets/          # Clés API et tokens
credentials/      # Informations d'authentification
__pycache__/      # Fichiers compilés Python
*.bak, *.tmp      # Fichiers temporaires
```

## Déploiement et Configuration

### Environnement Local
```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Lancer l'application
streamlit run main.py
```

### Déploiement Docker
```bash
# Construire l'image
docker build -t iveo-bi .

# Lancer le conteneur
docker run -p 8501:8501 iveo-bi
```

### Configuration Streamlit
Le fichier `.streamlit/config.toml` contient :
- Configuration du serveur
- Paramètres d'affichage
- Options de sécurité
- Thème et couleurs

## Utilisation Avancée

### Personnalisation des Filtres
- Filtres par catégorie d'exigence
- Sélection d'entreprises personnalisée
- Niveaux d'exigence configurables
- Persistance des préférences via cookies

### Génération de Rapports
- **HTML** : Rapports interactifs avec navigation
- **PDF** : Documents professionnels pour impression
- **Détection automatique** : Environnement cloud vs local
- **Fallback intelligent** : HTML si PDF indisponible

### Optimisations Performance
- Cache intelligent des données
- Chargement différé des gros fichiers
- Compression des images
- Optimisation des requêtes

## API et Extensions

### Intégration OpenAI
- Configuration via variables d'environnement
- Analyse contextuelle des données
- Génération de recommandations
- Support multilingue

### Extensibilité
- Architecture modulaire pour nouvelles fonctionnalités
- Système de plugins pour analyseurs personnalisés
- API REST pour intégration externe
- Hooks pour traitements personnalisés

## Maintenance et Support

### Surveillance
- Logs d'application détaillés
- Métriques de performance
- Monitoring des erreurs
- Alertes automatiques

### Mises à Jour
- Processus de déploiement automatisé
- Tests de régression
- Sauvegarde des configurations
- Migration des données

## Licence et Conformité

Ce projet est protégé par une licence commerciale propriétaire.

**Copyright © 2025 IVÉO et École de Technologie Supérieure (ETS) de Montréal. Tous droits réservés.**

### Utilisation Autorisée
- Usage interne pour les projets IVÉO
- Recherche académique à l'ETS
- Développement et personnalisation autorisés
- Distribution restreinte aux parties autorisées

### Conformité Réglementaire
- Respect des réglementations sur la protection des données
- Conformité aux standards de sécurité industriels
- Audit de sécurité régulier
- Documentation de conformité maintenue

## Support Technique

Pour toute question technique, bug report ou demande d'amélioration, contactez l'équipe de développement IVÉO via les canaux officiels.
- Utilisation dans le cadre des activités autorisées par IVÉO
- Accès aux fonctionnalités selon les droits accordés
- Consultation de la documentation

### Utilisation Interdite
- Reproduction, distribution ou vente du logiciel
- Modification ou création d'œuvres dérivées
- Ingénierie inverse ou décompilation
- Utilisation commerciale non autorisée
- Partage des données confidentielles

Pour obtenir une licence d'utilisation ou des autorisations supplémentaires, contactez IVÉO.

Voir le fichier [LICENSE](LICENSE) pour les termes complets de la licence.

## Conformité Réglementaire

- Respect des lois sur la protection des données personnelles
- Conformité aux réglementations sectorielles
- Respect des normes de sécurité informatique
- Protection de la propriété intellectuelle

---

Version : 2.0  
Dernière mise à jour : Juillet 2025  
Développé par : Équipe IVÉO - ETS Montréal
