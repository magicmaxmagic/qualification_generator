# IVÉO BI - Tableau de Bord Business Intelligence

## Description

IVÉO BI est une application de tableau de bord développée avec Streamlit pour l'analyse et la comparaison de solutions de stationnement intelligent. Cette plateforme permet d'analyser, comparer et évaluer différentes entreprises et solutions technologiques dans le domaine du stationnement intelligent.

## Fonctionnalités Principales

### Accueil
- Vue d'ensemble du projet IVÉO
- Navigation vers les différents modules
- Présentation des objectifs et de la mission

### Analyse des Entreprises
- Profils détaillés des entreprises partenaires
- Informations de contact et données organisationnelles
- Visualisations interactives des données d'entreprise

### Solutions Technologiques
- Catalogue des solutions de stationnement intelligent
- Spécifications techniques détaillées
- Comparaisons fonctionnelles

### Analyse Comparative
- Grille d'évaluation interactive avec système de notation binaire (0/1)
- Filtrage par catégorie et niveau d'exigence
- Sélection d'entreprises pour comparaisons personnalisées
- Informations complémentaires détaillées avec justifications
- Interface moderne et navigation fluide
- Tableau interactif : cliquez sur une ligne pour voir les détails d'une entreprise spécifique

## Installation et Configuration

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. Cloner le dépôt
   ```bash
   git clone [URL_DU_DEPOT]
   cd BI
   ```

2. Créer un environnement virtuel
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installer les dépendances
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les données
   - Placez votre fichier Excel de données dans le dossier `uploads/`
   - Assurez-vous que le fichier contient les feuilles nécessaires (notamment "Analyse comparative")

## Utilisation

### Démarrage de l'application

```bash
streamlit run main.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

### Navigation

1. Page d'Accueil : Vue d'ensemble et navigation
2. Entreprises : Analyse des profils d'entreprises
3. Solutions : Catalogue des solutions technologiques
4. Analyse Comparative : Comparaison interactive des solutions

### Utilisation de l'Analyse Comparative

1. Téléchargement des données : Utilisez la sidebar pour charger votre fichier Excel
2. Filtrage : Sélectionnez les catégories et niveaux d'exigence souhaités
3. Sélection d'entreprises : Choisissez les entreprises à comparer
4. Interaction : Cliquez sur une ligne du tableau pour voir les détails
5. Analyse : Consultez les informations complémentaires pour chaque entreprise

## Structure du Projet

```
BI/
├── main.py                     # Point d'entrée de l'application
├── sidebar.py                  # Configuration de la barre latérale
├── styles.css                  # Styles CSS personnalisés
├── requirements.txt            # Dépendances Python
├── Dockerfile                  # Configuration Docker
├── LICENSE                     # Licence commerciale propriétaire
├── .gitignore                  # Fichiers à ignorer par Git
├── app/
│   ├── __init__.py
│   ├── utils.py               # Utilitaires et fonctions communes
│   └── pages/
│       ├── home.py            # Page d'accueil
│       ├── entreprise.py      # Page des entreprises
│       ├── solution.py        # Page des solutions
│       └── analyse_comparative.py  # Page d'analyse comparative
├── uploads/                   # Dossier pour les fichiers de données (gitignored)
├── .streamlit/               # Configuration Streamlit
└── .devcontainer/           # Configuration pour développement en conteneur
```

## Technologies Utilisées

- Streamlit - Framework de développement d'applications web
- Pandas - Manipulation et analyse de données
- Plotly - Visualisations interactives
- OpenPyXL - Lecture de fichiers Excel
- Geopy - Géolocalisation et cartographie

## Format des Données

### Structure du fichier Excel

Le fichier Excel doit contenir une feuille "Analyse comparative" avec la structure suivante :

| Colonnes 0-3 | Colonnes 4+ (alternées) |
|--------------|-------------------------|
| - Catégories | - Entreprise 1 |
| - Fonctionnalités | - Information complémentaire 1 |
| - Exigence différenciateur | - Entreprise 2 |
| - Description | - Information complémentaire 2 |
| | - ... |

### Format des données
- Scores d'entreprises : Valeurs binaires (0 ou 1)
- Informations complémentaires : Texte libre avec justifications
- Catégories : Classification des fonctionnalités
- Exigences : Niveaux d'importance des critères

## Sécurité et Confidentialité

### Protection des Données
- Les fichiers sensibles sont exclus du dépôt grâce au fichier `.gitignore`.
- Les données d'entreprises ne doivent jamais être versionnées.
- Utilisez des variables d'environnement pour toute information confidentielle.
- Contrôlez strictement l'accès aux informations sensibles.

### Bonnes Pratiques de Sécurité
- Ne jamais committer de vraies données d'entreprises ou de clients.
- Utiliser uniquement des données de test pour les démonstrations et le développement.
- Vérifier régulièrement l'absence de fichiers sensibles dans Git.
- Respecter les réglementations sur la protection des données.

### Fichiers à cacher impérativement
```
uploads/           # Données d'entreprises
*.xlsx, *.xls     # Fichiers Excel sensibles
.env              # Variables d'environnement
secrets/          # Clés API et tokens
credentials/      # Informations d'authentification
+test_app_quick.py # Script de test pouvant contenir des données sensibles
*.bak             # Fichiers de sauvegarde
*.tmp             # Fichiers temporaires
```

## Déploiement avec Docker

```bash
# Construire l'image
docker build -t iveo-bi .

# Lancer le conteneur
docker run -p 8501:8501 iveo-bi
```

## Tests

```bash
# Exécuter les tests de validation
python test_app_quick.py
```

## Développement

### Ajout de nouvelles fonctionnalités

1. Nouvelles pages : Créez un fichier dans `app/pages/`
2. Fonctions utilitaires : Ajoutez-les dans `app/utils.py`
3. Styles : Modifiez `styles.css` pour les personnalisations CSS
4. Navigation : Mettez à jour `main.py` et `sidebar.py`

### Guidelines de développement

- Suivre les conventions de nommage Python (PEP 8)
- Documenter les fonctions avec des docstrings
- Tester les modifications avant de les pousser
- Maintenir la structure modulaire du projet
- Respecter la licence propriétaire

## Fonctionnalités Avancées

### Analyse Comparative v2.0

- Interface moderne et responsive
- Système de badges visuels pour les scores binaires
- Filtrage dynamique par catégories et exigences
- Sélection interactive d'entreprises
- Cartes d'informations détaillées avec justifications
- Navigation fluide avec état de session préservé

### Performances

- Mise en cache intelligente des données
- Chargement optimisé des fichiers Excel
- Interface responsive adaptée aux différentes tailles d'écran

## Support et Contact

Pour toute question ou support technique, contactez l'équipe de développement IVÉO.

## Licence

Ce projet est protégé par une licence commerciale propriétaire.

Copyright © 2025 IVÉO et École de Technologie Supérieure (ETS) de Montréal. Tous droits réservés.

### Utilisation Autorisée
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
