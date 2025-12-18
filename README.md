# 📊 Application de Gestion FCP

Application web interactive pour l'analyse et la gestion de Fonds Communs de Placement (FCP), développée avec Streamlit.

## 🎯 Objectif

Cette application offre une plateforme complète pour analyser les performances des FCP, gérer les souscriptions/rachats, suivre les actifs nets et générer des rapports détaillés avec visualisations avancées.

## ✨ Fonctionnalités Principales

### 1. 📈 Valeurs Liquidatives
- **Analyse de performance** : Visualisation des valeurs liquidatives avec graphiques interactifs
- **Calculs de rendement** : Rendements annualisés, volatilité, ratios de Sharpe
- **Comparaisons multi-fonds** : Analyse comparative entre plusieurs FCP
- **Clustering et segmentation** : Regroupement automatique des fonds par profil de risque
- **Rapports narratifs** : Génération automatique de résumés analytiques

### 2. 💰 Souscriptions & Rachats
- Gestion des transactions de souscription et rachat
- Suivi des flux entrants et sortants
- Historique détaillé des opérations

### 3. 💼 Actifs Nets
- Suivi de l'évolution des actifs nets
- Analyse de la composition du portefeuille
- Indicateurs de performance globale

### 4. ℹ️ À Propos
- Documentation de l'application
- Informations sur les méthodologies de calcul
- Guide d'utilisation

## 🛠️ Technologies Utilisées

- **Framework** : Streamlit
- **Data Analysis** : Pandas, NumPy
- **Visualisations** : Plotly, Plotly Express
- **Machine Learning** : Scikit-learn (clustering K-Means)
- **Statistiques** : SciPy

## 📋 Prérequis

- Python 3.8 ou supérieur
- Fichier de données FCP au format **CSV** ou **Excel (XLSX)**
  - Format CSV : `data_fcp.csv`
  - Format Excel : `data_fcp.xlsx`

## 🚀 Installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd Application-FCP
```

2. **Installer les dépendances**
```bash
pip install streamlit pandas numpy plotly scikit-learn scipy openpyxl
```

## 💻 Utilisation

### Démarrage de l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse `http://localhost:8501`

### Configuration

L'application **détecte automatiquement** le format du fichier (CSV ou XLSX) en fonction de l'extension.

Pour spécifier un fichier de données personnalisé, utilisez la variable d'environnement :

```bash
set FCP_DATA_FILE=chemin/vers/votre/fichier.xlsx  # Windows - Excel
set FCP_DATA_FILE=chemin/vers/votre/fichier.csv   # Windows - CSV
export FCP_DATA_FILE=chemin/vers/votre/fichier.xlsx  # Linux/Mac - Excel
export FCP_DATA_FILE=chemin/vers/votre/fichier.csv   # Linux/Mac - CSV
```

Par défaut, l'application cherche le fichier `data_fcp.xlsx` dans le répertoire courant.

**Note** : Pour les fichiers CSV, toutes les données doivent être dans un seul fichier. Pour les fichiers Excel, les données peuvent être organisées en plusieurs feuilles (Valeurs Liquidatives, Souscriptions Rachats, Actifs Nets).

## 📁 Structure du Projet

```
Application-FCP/
├── app.py                          # Page d'accueil et configuration principale
├── config.py                       # Configuration centralisée (couleurs, constantes)
├── utils.py                        # Fonctions utilitaires partagées
├── data_loader.py                  # Utilitaire legacy (référence historique)
├── requirements.txt                # Dépendances Python
├── .gitignore                      # Fichiers à ignorer par Git
├── pages/
│   ├── 1_Valeurs_Liquidatives.py  # Module d'analyse des valeurs liquidatives
│   ├── 2_Souscriptions_Rachats.py # Module de gestion des transactions
│   ├── 3_Actifs_Nets.py           # Module de suivi des actifs nets
│   └── 4_A_Propos.py              # Page d'information et documentation
├── data_fcp.xlsx                   # Fichier de données (non inclus dans le repo)
└── README.md                       # Documentation
```

### Améliorations du Code (Décembre 2024)

L'application a été optimisée pour améliorer la maintenabilité et les performances :

- **Configuration centralisée** : Toutes les constantes et couleurs sont maintenant dans `config.py`
- **Fonctions utilitaires** : Code partagé consolidé dans `utils.py` pour éviter la duplication
- **Caching amélioré** : Utilisation optimale de `@st.cache_data` pour les performances
- **CSS commun** : Styles partagés entre pages pour cohérence visuelle
- **Documentation** : Ajout de docstrings complètes et de `requirements.txt`
- **Gestion Git** : Ajout de `.gitignore` approprié pour projets Python/Streamlit

## 📊 Format des Données

L'application supporte deux formats de fichiers :

### Format Excel (XLSX) - Recommandé
Le fichier Excel peut contenir plusieurs feuilles pour organiser les données :
- **Valeurs Liquidatives** : Données quotidiennes des VL
  - Colonne `Date` : Format date (DD/MM/YYYY)
  - Colonnes suivantes : Une colonne par FCP avec les valeurs liquidatives
- **Souscriptions Rachats** : Transactions de souscription et rachat
  - Colonnes : Date, FCP, Opérations, Montant, Type de Client
- **Actifs Nets** : Évolution des actifs nets par FCP
  - Colonnes : Date, FCP, Montant

### Format CSV
Pour les fichiers CSV, toutes les données doivent être dans un seul fichier :
- Colonne `Date` : Format date (YYYY-MM-DD ou DD/MM/YYYY)
- Colonnes suivantes : Selon le type de données (VL, transactions, actifs)
- Encodage : UTF-8 recommandé
- Séparateur : Virgule (,)

## 🎨 Thème et Design

L'application utilise une palette de couleurs professionnelle :
- **Bleu profond** (#114B80) : Titres et boutons principaux
- **Bleu-gris** (#567389) : Widgets et éléments secondaires
- **Bleu clair** (#ACC7DF) : Arrière-plans et effets de survol

## 📈 Métriques Calculées

L'application calcule automatiquement :
- Rendements annualisés
- Volatilité (écart-type)
- Ratio de Sharpe
- Drawdown maximum
- Corrélations entre fonds
- Profils de risque par clustering

## 🤝 Contribution

Pour contribuer au projet :
1. Fork le repository
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est développé pour **CGF BOURSE** - Tous droits réservés.

## 👤 Auteur

**DYLANE** - CGF BOURSE

## 📞 Support

Pour toute question ou problème, veuillez contacter l'équipe de développement CGF BOURSE.

---

**Note** : Cette application est destinée à un usage interne pour l'analyse professionnelle des fonds communs de placement.