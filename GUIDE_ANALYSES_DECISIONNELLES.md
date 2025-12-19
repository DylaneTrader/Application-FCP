# Guide Complet des Analyses Décisionnelles FCP
## Comment chaque analyse aide à affiner les décisions, apprécier le risque et comprendre les produits

---

**Date de création** : 18 décembre 2025  
**Version** : 2.0  
**Destinataires** : Gestionnaires de portefeuilles, Gestionnaires de risque, Équipe commerciale  
**Auteur** : DYLANE - CGF GESTION

---

## Table des Matières

1. [Introduction et Contexte](#1-introduction-et-contexte)
2. [Analyses des Valeurs Liquidatives](#2-analyses-des-valeurs-liquidatives)
3. [Analyses des Souscriptions et Rachats](#3-analyses-des-souscriptions-et-rachats)
4. [Analyses des Actifs Nets](#4-analyses-des-actifs-nets)
5. [Synthèse et Recommandations d'Usage](#5-synthèse-et-recommandations-dusage)

---

# 1. Introduction et Contexte

## 1.1 Objectif de ce Document

Ce document détaille **comment chaque analyse disponible dans l'application FCP** aide les trois acteurs clés de l'entreprise :

- **👨‍💼 Gestionnaires de Portefeuilles** : Affiner leurs décisions d'allocation et de gestion
- **🛡️ Gestionnaires de Risque** : Mieux apprécier et quantifier le risque
- **💼 Équipe Commerciale** : Mieux comprendre et expliquer les produits qu'elle vend

## 1.2 Structure de l'Analyse

Pour chaque analyse, nous détaillons :
- **📊 Logique** : Pourquoi cette analyse existe et ce qu'elle mesure
- **🧮 Formules** : Les calculs mathématiques sous-jacents
- **💡 Interprétation** : Comment lire et comprendre les résultats
- **⚠️ Subtilités** : Les pièges à éviter et les nuances importantes
- **🎯 Utilité par Profil** : Comment chaque acteur utilise cette analyse

---

# 2. Analyses des Valeurs Liquidatives

Les valeurs liquidatives (VL) sont le cœur de l'analyse de performance des FCP. Cette section couvre toutes les analyses disponibles dans le module "Valeurs Liquidatives".

---

## 2.1 Performances Calendaires

### 📊 Logique
Les performances calendaires mesurent les rendements sur des périodes temporelles fixes et standardisées (WTD, MTD, QTD, STD, YTD). Elles permettent de comparer la performance actuelle du fonds avec des repères temporels universels.

### 🧮 Formules

**Week to Date (WTD)**
```
Rendement_WTD = (VL_actuelle / VL_début_semaine - 1) × 100
```

**Month to Date (MTD)**
```
Rendement_MTD = (VL_actuelle / VL_début_mois - 1) × 100
```

**Quarter to Date (QTD)**
```
Rendement_QTD = (VL_actuelle / VL_début_trimestre - 1) × 100
```

**Semester to Date (STD)**
```
Rendement_STD = (VL_actuelle / VL_début_semestre - 1) × 100
```

**Year to Date (YTD)**
```
Rendement_YTD = (VL_actuelle / VL_début_année - 1) × 100
```

### 💡 Interprétation

- **WTD** : Performance de la semaine en cours (plus volatile, réagit aux événements récents)
- **MTD** : Performance mensuelle (balance entre réactivité et stabilité)
- **QTD** : Performance trimestrielle (utilisé pour les rapports trimestriels)
- **YTD** : Performance depuis début d'année (référence standard pour les comparaisons annuelles)

**Échelle de lecture** :
- `> 5%` : Très bonne performance
- `2% à 5%` : Bonne performance
- `0% à 2%` : Performance positive modérée
- `< 0%` : Performance négative (nécessite analyse)

### ⚠️ Subtilités

1. **Effet de date** : WTD et MTD sont très sensibles à la date de consultation
2. **Saisonnalité** : Certains FCP peuvent avoir des patterns saisonniers (ex: meilleure performance en fin d'année)
3. **Biais de survie** : Ne compare que les fonds encore actifs
4. **Point de départ** : YTD repart à zéro chaque 1er janvier, peut masquer des tendances long terme

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Suivre la performance récente pour ajuster les allocations
- Identifier rapidement les fonds sous-performants ou sur-performants
- Décider des rééquilibrages intra-mois/intra-trimestre
- **Action concrète** : Si MTD < -2% et QTD < -5%, envisager une réduction de l'exposition

**🛡️ Gestionnaires de Risque**
- Détecter les déviations rapides par rapport aux objectifs
- Identifier les fonds nécessitant une surveillance accrue
- Valider que les performances restent dans les limites du prospectus
- **Action concrète** : Si WTD montre une volatilité inhabituelle, déclencher une analyse approfondie

**💼 Équipe Commerciale**
- Communiquer les performances récentes aux clients (MTD/YTD)
- Comparer avec la concurrence sur des périodes standardisées
- Argumenter sur la réactivité du fonds (WTD, MTD)
- **Pitch client** : "Notre fonds affiche un YTD de +8.5%, surperformant la moyenne du marché de +2.1%"

---

## 2.2 Performances Glissantes

### 📊 Logique
Les performances glissantes mesurent les rendements sur des fenêtres temporelles mobiles (1M, 3M, 6M, 1Y, 3Y, 5Y, Origine). Contrairement aux calendaires, elles ne dépendent pas de dates fixes et donnent une vision plus stable de la performance.

### 🧮 Formules

**Performance 1 Mois (1M)**
```
Rendement_1M = (VL_actuelle / VL_il_y_a_1_mois - 1) × 100
```

**Performance Annualisée (pour périodes > 1 an)**
```
Rendement_Annualisé = ((VL_finale / VL_initiale)^(252/jours) - 1) × 100
```
Où 252 = nombre de jours de trading par an

**Performance Origine**
```
Rendement_Origine = (VL_actuelle / VL_création - 1) × 100
```

### 💡 Interprétation

- **1M, 3M** : Court terme, volatiles, suivent les tendances récentes
- **6M, 1Y** : Moyen terme, filtrent le bruit de court terme
- **3Y, 5Y** : Long terme, montrent la capacité de création de valeur durable
- **Origine** : Performance historique totale depuis la création

**Échelle comparative** :
- Comparer 1Y avec l'indice de référence
- 3Y et 5Y doivent montrer une sur-performance consistante
- Origine doit refléter la promesse initiale du fonds

### ⚠️ Subtilités

1. **Annualisation** : Les performances < 1 an ne sont pas annualisées (simple rendement)
2. **Effet de base** : Une forte performance passée rend difficile une sur-performance continue
3. **Survivor bias** : Les fonds fermés ou fusionnés n'apparaissent pas
4. **Fenêtre glissante** : Change chaque jour, contrairement aux calendaires

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Évaluer la consistance de la performance (3Y, 5Y)
- Comparer avec les benchmarks sur différentes périodes
- Identifier les cycles de sur/sous-performance
- **Action concrète** : Si 1Y > benchmark mais 3Y < benchmark, questionner la stratégie récente

**🛡️ Gestionnaires de Risque**
- Valider que le track record justifie le profil de risque
- Détecter les changements de régime (1Y vs 3Y)
- Vérifier la cohérence avec les objectifs long terme
- **Action concrète** : Performance 5Y < objectif prospectus → revue de la gestion

**💼 Équipe Commerciale**
- Mettre en avant les performances long terme (3Y, 5Y)
- Expliquer les variations court terme dans le contexte long terme
- Utiliser "Origine" pour montrer le succès historique
- **Pitch client** : "Sur 5 ans, notre fonds a généré +45%, soit +7.7% annualisé"

---

## 2.3 Métriques de Risque

### 📊 Logique
Les métriques de risque quantifient la volatilité, les pertes potentielles et le profil risque-rendement. Elles sont essentielles pour comprendre "à quel prix" la performance a été obtenue.

### 🧮 Formules

**Volatilité (Écart-type annualisé)**
```
σ_annuelle = σ_quotidienne × √252

Où σ_quotidienne = √(Σ(Ri - R̄)² / (n-1))
Ri = rendement quotidien
R̄ = rendement moyen
```

**Value at Risk (VaR 95%)**
```
VaR₉₅ = -Percentile₅(Rendements quotidiens) × √T

T = horizon temporel (ex: 21 jours pour 1 mois)
```
La VaR répond à : "Avec 95% de confiance, on ne perdra pas plus de X%"

**Conditional Value at Risk (CVaR 95%)**
```
CVaR₉₅ = Moyenne(Rendements | Rendements < VaR₉₅)
```
La CVaR mesure la perte moyenne dans les 5% pires scénarios.

**Ratio de Sharpe**
```
Sharpe = (Rendement_annualisé - Taux_sans_risque) / Volatilité_annualisée

Généralement, Taux_sans_risque = 0 pour simplification
```

**Maximum Drawdown (MDD)**
```
MDD = min((VL_t - max(VL₀...VL_t)) / max(VL₀...VL_t)) × 100

C'est la plus grande perte pic-à-creux observée
```

**Skewness (Asymétrie)**
```
Skewness = E[(R - μ)³] / σ³

Mesure l'asymétrie de la distribution des rendements
```

**Kurtosis (Aplatissement)**
```
Kurtosis_excess = E[(R - μ)⁴] / σ⁴ - 3

Mesure l'épaisseur des queues de distribution
```

### 💡 Interprétation

**Volatilité**
- `< 5%` : Très faible (monétaire, obligations courtes)
- `5-10%` : Faible (obligations mixtes)
- `10-15%` : Modérée (fonds équilibrés)
- `15-25%` : Élevée (actions, marchés émergents)
- `> 25%` : Très élevée (sectoriels, levier)

**VaR 95% (mensuelle)**
- `-2%` : Avec 95% de confiance, perte max sur 1 mois = 2%
- Plus la VaR est négative, plus le risque est élevé

**CVaR 95%**
- Toujours plus négative que la VaR
- Mesure la "catastrophe moyenne" dans les 5% pires cas
- CVaR de -8% : dans les pires 5% des scénarios, perte moyenne = 8%

**Ratio de Sharpe**
- `< 0` : Performance inférieure au sans-risque (mauvais)
- `0 - 0.5` : Faible qualité risque-rendement
- `0.5 - 1` : Acceptable
- `1 - 2` : Bon
- `> 2` : Excellent

**Maximum Drawdown**
- `-10%` : Perte maximale observée = 10% (acceptable)
- `-20%` : Modéré (typique pour fonds actions)
- `-30%` : Élevé (nécessite profil agressif)
- `-50%+` : Extrême (hedge funds, sectoriels)

**Skewness**
- `> 0` : Asymétrie positive (bonne) → plus de gains extrêmes que de pertes extrêmes
- `= 0` : Symétrique (distribution normale)
- `< 0` : Asymétrie négative (mauvaise) → plus de pertes extrêmes que de gains extrêmes

**Kurtosis**
- `= 0` : Distribution normale
- `> 0` : Queues épaisses → plus d'événements extrêmes que prévu
- `< 0` : Queues fines → moins d'événements extrêmes

### ⚠️ Subtilités

1. **Hypothèse de normalité** : VaR et CVaR supposent souvent une distribution normale, ce qui sous-estime les risques extrêmes
2. **Période de calcul** : Volatilité calculée sur 1 an vs 3 ans peut être très différente
3. **Ratio de Sharpe** : Peut être trompeur si rendements non-normaux (skewness négatif)
4. **Drawdown** : MDD historique ≠ MDD futur (peut être pire)
5. **Autocorrélation** : Si rendements autocorrélés, formules standard sous-estiment le risque

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Comparer l'efficience de plusieurs fonds (Sharpe ratio)
- Identifier les fonds avec meilleur ratio risque-rendement
- Construire des portefeuilles optimisés (Markowitz)
- **Action concrète** : Choisir le fonds avec Sharpe > 1 et MDD < -15% pour allocation défensive

**🛡️ Gestionnaires de Risque**
- Définir les limites de risque (VaR, CVaR, MDD)
- Surveiller les dépassements de seuils
- Stress testing et scénarios extrêmes (CVaR)
- Reporting réglementaire (VaR)
- **Action concrète** : Si CVaR > seuil prospectus, exiger une réduction de l'exposition

**💼 Équipe Commerciale**
- Expliquer le profil de risque en termes simples
- Qualifier le fonds (prudent/équilibré/dynamique) via volatilité
- Rassurer sur la "pire chute" historique (MDD)
- **Pitch client** : "Ce fonds a une volatilité de 12% et n'a jamais perdu plus de 18% depuis sa création"

---

## 2.4 Analyse des Distributions et Statistiques

### 📊 Logique
L'analyse de la distribution des rendements permet de vérifier si le fonds se comporte de manière "normale" ou présente des caractéristiques atypiques (asymétrie, queues épaisses).

### 🧮 Formules

**Quartiles**
```
Q1 = Percentile₂₅(Rendements)  → 25% des rendements sont inférieurs
Q2 = Percentile₅₀(Rendements)  → Médiane
Q3 = Percentile₇₅(Rendements)  → 75% des rendements sont inférieurs
```

**Écart Interquartile (IQR)**
```
IQR = Q3 - Q1

Mesure la dispersion centrale (50% des données)
```

**Test de Normalité (Shapiro-Wilk)**
```
W = (Σ aᵢ × x₍ᵢ₎)² / Σ(xᵢ - x̄)²

p-value < 0.05 → Rejet de l'hypothèse de normalité
```

### 💡 Interprétation

**Histogramme**
- **Forme en cloche** : Distribution normale (bonne)
- **Asymétrique à gauche** : Plus de rendements négatifs extrêmes (risqué)
- **Asymétrique à droite** : Plus de rendements positifs extrêmes (favorable)
- **Bimodale** : Deux régimes distincts (marché haussier vs baissier)

**Box Plot**
- **Boîte compacte** : Faible dispersion des rendements
- **Moustaches longues** : Rendements extrêmes fréquents
- **Points outliers** : Événements exceptionnels

**Test de normalité**
- `p > 0.05` : Distribution normale (les modèles standards fonctionnent)
- `p < 0.05` : Distribution non-normale (attention aux VaR/Sharpe standards)

### ⚠️ Subtilités

1. **Taille d'échantillon** : Besoin de >30 observations pour test de normalité fiable
2. **Autocorrélation** : Peut fausser les tests statistiques
3. **Fat tails** : Même si test dit "normal", peut y avoir des queues épaisses
4. **Régimes changeants** : Distribution peut changer dans le temps

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Valider les hypothèses des modèles d'optimisation
- Identifier les fonds avec distributions favorables (skew positif)
- Détecter les régimes multiples (bimodal)
- **Action concrète** : Éviter les fonds avec skewness < -0.5 (risque de pertes extrêmes)

**🛡️ Gestionnaires de Risque**
- Vérifier la validité des modèles VaR/CVaR
- Identifier les distributions à queues épaisses
- Ajuster les modèles de risque si non-normalité
- **Action concrète** : Si kurtosis > 3, utiliser des modèles de risque non-paramétriques

**💼 Équipe Commerciale**
- Expliquer la "normalité" ou "atypicité" du fonds
- Rassurer sur la prévisibilité des rendements
- Vulgariser les statistiques
- **Pitch client** : "Les rendements de ce fonds suivent une distribution équilibrée, sans surprises extrêmes"

---

## 2.5 Corrélations entre Fonds

### 📊 Logique
Les corrélations mesurent le degré de co-mouvement entre les fonds. Elles sont essentielles pour la diversification : des fonds peu corrélés réduisent le risque du portefeuille global.

### 🧮 Formules

**Coefficient de Corrélation de Pearson**
```
ρ(A,B) = Cov(A,B) / (σ_A × σ_B)

Où:
Cov(A,B) = E[(A - μ_A)(B - μ_B)]  → Covariance
σ_A, σ_B = Écarts-types de A et B
```

Valeur : `-1 ≤ ρ ≤ +1`

**Coefficient de Détermination**
```
R² = ρ²

Proportion de variance de A expliquée par B
```

### 💡 Interprétation

**Coefficient de corrélation**
- `ρ = +1` : Corrélation parfaite positive (mouvements identiques)
- `ρ = +0.7 à +1` : Forte corrélation positive
- `ρ = +0.3 à +0.7` : Corrélation modérée
- `ρ = -0.3 à +0.3` : Faible corrélation (bonne diversification)
- `ρ = -0.7 à -0.3` : Corrélation négative modérée
- `ρ = -1 à -0.7` : Forte corrélation négative
- `ρ = -1` : Corrélation parfaite négative (mouvements opposés)

**Heatmap de corrélation**
- **Zone rouge** : Corrélations élevées (>0.7) → peu de diversification
- **Zone verte** : Corrélations faibles (<0.3) → bonne diversification
- **Zone bleue** : Corrélations négatives → diversification excellente

### ⚠️ Subtilités

1. **Corrélation ≠ Causalité** : Deux fonds peuvent être corrélés sans lien de cause à effet
2. **Instabilité temporelle** : Corrélations changent dans le temps, surtout en crise
3. **Corrélations extrêmes** : Tendent à augmenter lors des chocs de marché (perte de diversification)
4. **Non-linéarité** : Pearson mesure seulement les relations linéaires

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Construire des portefeuilles diversifiés (corrélations faibles)
- Identifier les fonds redondants (corrélations > 0.8)
- Optimiser l'allocation pour réduire le risque global
- **Action concrète** : Si ρ(A,B) > 0.9, éliminer l'un des deux fonds pour éviter la redondance

**🛡️ Gestionnaires de Risque**
- Mesurer le risque de concentration
- Détecter les facteurs de risque communs
- Stress-tester les corrélations en crise
- **Action concrète** : Si portefeuille avec corrélations moyennes > 0.7, exiger une diversification

**💼 Équipe Commerciale**
- Expliquer la complémentarité des fonds dans un portefeuille
- Proposer des combinaisons de fonds décorrélés
- Argumenter sur les bénéfices de diversification
- **Pitch client** : "En combinant ces 3 fonds (corrélations < 0.4), vous réduisez votre risque de 30%"

---

## 2.6 Risk Fingerprint (Profil de Risque Multidimensionnel)

### 📊 Logique
Le Risk Fingerprint est une représentation visuelle du profil de risque sur 7 dimensions normalisées (0-100). Il permet d'identifier rapidement les forces et faiblesses d'un fonds en termes de risque.

### 🧮 Formules

Les 7 dimensions sont :

**1. Stabilité** (inverse de la volatilité)
```
Score_Stabilité = 100 × (1 - (σ_fonds - σ_min) / (σ_max - σ_min))

Mesure la régularité des rendements
```

**2. Résilience** (inverse du maximum drawdown)
```
Score_Résilience = 100 × (1 - |MDD_fonds - MDD_min| / |MDD_max - MDD_min|)

Mesure la capacité à limiter les pertes
```

**3. Récupération** (inverse du temps de récupération moyen)
```
Score_Récupération = 100 × (1 - (T_recup_fonds - T_recup_min) / (T_recup_max - T_recup_min))

Mesure la vitesse de rebond après une perte
```

**4. Protection Extrême** (inverse de CVaR)
```
Score_Protection = 100 × (1 - |CVaR_fonds - CVaR_min| / |CVaR_max - CVaR_min|)

Mesure la protection contre les scénarios catastrophes
```

**5. Asymétrie** (skewness normalisée)
```
Score_Asymétrie = 50 + (Skewness_fonds × 25)

Normalisée pour que 0 → 50 (neutre), positif → >50 (favorable)
```

**6. Sharpe Stable** (stabilité du ratio de Sharpe)
```
Score_Sharpe = 100 × (1 - (σ_Sharpe_fonds - σ_Sharpe_min) / (σ_Sharpe_max - σ_Sharpe_min))

Mesure la consistance de la qualité risque-rendement
```

**7. Pain Ratio** (rendement ajusté par l'Ulcer Index)
```
Pain_Ratio = Rendement_Total / Ulcer_Index

Score_Pain = 100 × (Pain_fonds - Pain_min) / (Pain_max - Pain_min)

Mesure le rendement par unité de "douleur" subie
```

**Score Global**
```
Score_Global = Moyenne(7 dimensions)
```

### 💡 Interprétation

**Score Global**
- `70-100` : Excellent profil de risque (vert)
- `50-70` : Profil de risque satisfaisant (orange)
- `0-50` : Profil de risque préoccupant (rouge)

**Radar Chart**
- **Polygone large et régulier** : Profil de risque équilibré
- **Polygone déformé** : Forces et faiblesses marquées
- **Pointes vers l'extérieur** : Points forts (scores élevés)
- **Creux vers le centre** : Points faibles (scores faibles)

**Interprétation par dimension** :
- **Stabilité élevée** : Fonds peu volatil, prévisible
- **Résilience élevée** : Fonds qui limite bien les pertes maximales
- **Récupération élevée** : Fonds qui rebondit rapidement après une baisse
- **Protection élevée** : Fonds protégé contre les scénarios extrêmes
- **Asymétrie élevée** : Fonds avec plus de gains extrêmes que de pertes
- **Sharpe Stable élevé** : Qualité risque-rendement constante
- **Pain Ratio élevé** : Bon rendement pour la "douleur" subie

### ⚠️ Subtilités

1. **Normalisation relative** : Scores calculés relativement aux autres fonds de l'univers
2. **Changement d'univers** : Ajouter/retirer un fonds change tous les scores
3. **Période de calcul** : Scores sensibles à la période d'historique
4. **Trade-offs** : Un score parfait (100 partout) est impossible (compromis risque-rendement)
5. **Skewness** : Transformation sigmoïdale peut amplifier de petites différences

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Visualiser rapidement le profil de risque complet
- Comparer plusieurs fonds en un coup d'œil
- Identifier les fonds "équilibrés" vs "spécialisés"
- Construire des portefeuilles en mixant des profils complémentaires
- **Action concrète** : Sélectionner un fonds avec Score_Global > 60 et Résilience > 70 pour allocation défensive

**🛡️ Gestionnaires de Risque**
- Détecter les fonds avec faiblesses critiques (scores < 30 sur une dimension)
- Prioriser les revues de gestion (fonds avec Score_Global < 50)
- Valider que le profil correspond aux promesses du prospectus
- **Action concrète** : Si Protection Extrême < 40, exiger des stress tests supplémentaires

**💼 Équipe Commerciale**
- Présenter visuellement le profil de risque au client (radar chart)
- Expliquer les forces du fonds en termes simples
- Être transparent sur les faiblesses
- Différencier les fonds concurrents
- **Pitch client** : "Notre fonds excelle en Résilience (85/100) et Récupération (78/100), idéal pour les profils prudents"

---

## 2.7 Analyse des Régimes de Volatilité

### 📊 Logique
L'analyse par régimes identifie 3 états de marché distincts (Faible, Intermédiaire, Élevé volatilité) et évalue comment le fonds performe dans chaque régime. Cela permet de comprendre si le fonds crée de la valeur dans tous les environnements ou seulement certains.

### 🧮 Formules

**Calcul de la volatilité glissante**
```
σ_rolling(t) = √(Σ(R_{t-window:t} - R̄)² / window) × √252

window = 30 jours (typique)
```

**Clustering K-Means (3 régimes)**
```
Algorithme:
1. Initialiser 3 centres aléatoires
2. Assigner chaque point au centre le plus proche
3. Recalculer les centres comme moyenne des points assignés
4. Répéter jusqu'à convergence

Résultat: Label 0, 1, 2 pour chaque point
```

**Labélisation économique**
```
Régime 0 = Faible si centre₀ = min(centres)
Régime 1 = Intermédiaire si centre₁ = médian(centres)
Régime 2 = Élevé si centre₂ = max(centres)
```

**Matrice de Transition**
```
P(i→j) = Nombre de transitions de i vers j / Nombre total de sorties de i

Exemple: P(Faible→Élevé) = 5% → 5% de chances de passer directement de Faible à Élevé
```

**Persistance (temps moyen dans un régime)**
```
Persistance_i = 1 / (1 - P(i→i))

Exemple: Si P(Faible→Faible) = 0.9, Persistance = 1/(1-0.9) = 10 jours
```

**Sharpe par régime**
```
Sharpe_régime_i = (R̄_régime_i × 252) / (σ_régime_i × √252)

Mesure l'efficience risque-rendement dans chaque régime
```

### 💡 Interprétation

**Régime actuel**
- ✅ **Faible** : Environnement calme, favorable (volatilité < 10%)
- ⚠️ **Intermédiaire** : Phase de transition (volatilité 10-20%)
- 🔴 **Élevé** : Environnement turbulent, risqué (volatilité > 20%)

**Matrice de Transition**
- **Diagonale élevée** : Régimes persistants (ex: P(Faible→Faible) = 85%)
- **Hors diagonale faible** : Transitions rares
- **Asymétrie** : Ex: facile de passer de Faible à Élevé (crise), difficile l'inverse

**Sharpe par régime**
- **Sharpe_Faible > Sharpe_Élevé** : Fonds performe mieux en environnement calme (typique)
- **Sharpe_Élevé > Sharpe_Faible** : Fonds profite de la volatilité (opportuniste)
- **Sharpe négatifs** : Destruction de valeur dans ce régime

**Rendement par régime**
- **R_Faible > 0** : Crée de la valeur en environnement calme
- **R_Élevé < 0** : Subit des pertes en crise (normal)
- **R_Élevé > 0** : Fonds résilient même en crise (rare et précieux)

### ⚠️ Subtilités

1. **Choix du nombre de régimes** : 3 est un compromis (2 = trop simple, 4+ = sur-ajustement)
2. **Fenêtre de volatilité** : 30 jours est standard, mais 60 ou 90 donnent des régimes plus lisses
3. **Stabilité des clusters** : Régimes peuvent changer si on change la période
4. **Causalité** : Corrélation entre régime et performance ≠ causalité
5. **Forward-looking** : Matrice de transition historique ≠ future (régimes non-stationnaires)

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Savoir si le fonds performe mieux en marché calme ou agité
- Construire des portefeuilles "tous temps" en mixant des fonds complémentaires
- Ajuster l'allocation selon le régime actuel
- **Action concrète** : Si régime actuel = Élevé et Sharpe_Élevé < 0 pour un fonds, réduire temporairement l'exposition

**🛡️ Gestionnaires de Risque**
- Identifier les fonds vulnérables en période de crise (Sharpe_Élevé très négatif)
- Surveiller les transitions de régimes (alertes)
- Valider que le fonds est résilient dans tous les régimes
- **Action concrète** : Si P(Faible→Élevé) > 20%, prévoir des plans de contingence

**💼 Équipe Commerciale**
- Expliquer que le fonds est "tout temps" ou "spécialisé"
- Rassurer sur la performance en crise
- Qualifier le fonds selon le profil de risque du client
- **Pitch client** : "Ce fonds a un Sharpe positif dans les 3 régimes de volatilité, c'est un vrai fonds 'tout temps'"

---

## 2.8 Analyse des Drawdowns

### 📊 Logique
Un drawdown est une baisse de valeur depuis un pic précédent. L'analyse des drawdowns identifie les épisodes de perte, leur profondeur, leur durée et le temps de récupération. C'est une mesure intuitive du "pire qui peut arriver".

### 🧮 Formules

**Drawdown à l'instant t**
```
DD(t) = (VL(t) - max(VL[0:t])) / max(VL[0:t]) × 100

Si VL(t) = nouveau max, alors DD(t) = 0%
```

**Maximum Drawdown (MDD)**
```
MDD = min(DD(t)) pour tout t

C'est le plus grand drawdown observé
```

**Épisode de Drawdown**
- **Début** : Lorsque DD passe de 0% à négatif
- **Creux** : Point de DD minimum de l'épisode
- **Fin** : Lorsque DD revient à 0% (nouveau pic atteint)

**Durée de l'épisode**
```
Durée = Date_fin - Date_début (en jours)
```

**Temps de Récupération**
```
T_recup = Date_fin - Date_creux (en jours)

Temps pour revenir au pic depuis le creux
```

**Ulcer Index**
```
Ulcer = √(Σ DD(t)² / n)

Moyenne quadratique des drawdowns (mesure la "douleur")
```

**Pain Ratio**
```
Pain_Ratio = Rendement_Total / Ulcer_Index

Rendement obtenu par unité de "douleur"
```

### �� Interprétation

**Maximum Drawdown**
- `-10%` : Acceptable pour fonds prudent
- `-20%` : Typique pour fonds équilibré
- `-30%` : Acceptable pour fonds dynamique
- `-50%+` : Extrême (hedge funds, sectoriels)

**Durée des épisodes**
- `< 3 mois` : Court terme, récupération rapide
- `3-12 mois` : Moyen terme, normal
- `> 12 mois` : Long terme, préoccupant

**Temps de récupération**
- `< 6 mois` : Récupération rapide (bon)
- `6-12 mois` : Normal
- `> 12 mois` : Lent (problème de performance)

**Ulcer Index**
- `< 5` : Faible douleur
- `5-10` : Modéré
- `> 10` : Douleur élevée

**Pain Ratio**
- `> 1` : Bon (rendement > douleur)
- `0.5-1` : Acceptable
- `< 0.5` : Mauvais (trop de douleur pour le rendement)

### ⚠️ Subtilités

1. **Seuil de récupération** : Définir "récupération" à -0.01% (quasi-complet) vs 0% exact
2. **Drawdowns multiples** : Peut y avoir plusieurs épisodes simultanés (définition de "fin")
3. **Drawdown en cours** : DD actuel peut ne pas être terminé (pas de temps de récupération connu)
4. **Ulcer vs Volatilité** : Ulcer pénalise plus les pertes que la volatilité simple
5. **Biais de période** : MDD dépend fortement de la période observée

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Connaître le "pire cas" historique pour dimensionner l'allocation
- Comparer la résilience de plusieurs fonds
- Estimer le capital à risque
- **Action concrète** : Si MDD > -30%, limiter l'allocation à 20% du portefeuille max

**🛡️ Gestionnaires de Risque**
- Définir des limites de drawdown acceptables
- Déclencher des alertes si DD actuel approche du MDD historique
- Stress-testing : simuler des DD futurs
- **Action concrète** : Si DD actuel > 80% du MDD historique, augmenter la surveillance

**💼 Équipe Commerciale**
- Communiquer le "pire qui peut arriver" aux clients
- Qualifier la tolérance à la perte requise
- Rassurer avec le temps de récupération moyen
- **Pitch client** : "Le pire drawdown a été de -22% en mars 2020, récupéré en 4 mois. Depuis, le fonds est à +15%"

---

## 2.9 Indicateurs de Risque Glissants

### 📊 Logique
Les indicateurs glissants (rolling) montrent l'évolution temporelle du risque. Contrairement aux métriques statiques, ils révèlent les changements de régime, la stabilité des caractéristiques et les périodes de risque élevé.

### 🧮 Formules

**Volatilité Glissante**
```
σ_rolling(t, window) = √(Σ(R_{t-window:t} - R̄)² / window) × √252

Typiquement window = 60 jours (3 mois)
```

**Sharpe Glissant**
```
Sharpe_rolling(t, window) = (R̄_{t-window:t} × 252) / (σ_rolling(t) × √252)

Mesure l'efficience risque-rendement sur la fenêtre
```

**VaR Glissante (95%)**
```
VaR_rolling(t, window) = -Percentile₅(R_{t-window:t}) × √21

Estimation de la perte maximale à 95% sur 1 mois, réévaluée chaque jour
```

**CVaR Glissante (95%)**
```
CVaR_rolling(t, window) = Moyenne(R_{t-window:t} | R < VaR_rolling(t))

Perte moyenne dans les 5% pires scénarios, réévaluée chaque jour
```

### 💡 Interprétation

**Volatilité Glissante**
- **Tendance haussière** : Risque en augmentation (surveillance)
- **Tendance baissière** : Risque en diminution (positif)
- **Pics** : Périodes de stress (crises)
- **Stabilité** : Risque prévisible (bon)

**Sharpe Glissant**
- **Au-dessus de 1** : Période de bonne efficience
- **Croise zéro** : Passage performance positive/négative
- **Volatilité élevée** : Qualité risque-rendement instable

**VaR/CVaR Glissantes**
- **Augmentation (plus négatif)** : Risque extrême en hausse
- **Corrélation avec volatilité** : Normal, mais CVaR peut diverger
- **Divergence VaR/CVaR** : Queues de distribution changeantes

**Graphique temporel**
- **Zone verte** : Périodes de faible risque
- **Zone rouge** : Périodes de risque élevé
- **Transitions** : Changements de régime

### ⚠️ Subtilités

1. **Choix de la fenêtre** : 60 jours = compromis réactivité/stabilité (30 = plus réactif, 120 = plus stable)
2. **Lag** : Indicateurs glissants réagissent avec retard aux changements
3. **Lookback bias** : Basés sur le passé, ne prédisent pas le futur
4. **Autocorrélation** : Valeurs successives sont corrélées (pas indépendantes)

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Détecter les changements de régime en temps réel
- Ajuster dynamiquement l'allocation selon le risque actuel
- Identifier les périodes opportunes pour renforcer/alléger
- **Action concrète** : Si Sharpe glissant < 0.5 pendant 3 mois consécutifs, réduire l'allocation

**🛡️ Gestionnaires de Risque**
- Surveiller l'évolution du risque en continu
- Détecter les dégradations avant qu'elles ne deviennent critiques
- Valider la stabilité du profil de risque
- **Action concrète** : Si VaR glissante dépasse le seuil pendant 2 semaines, déclencher une revue

**💼 Équipe Commerciale**
- Montrer la réactivité de la gestion au risque
- Expliquer les périodes difficiles (pics de volatilité)
- Valoriser la stabilité du risque
- **Pitch client** : "La volatilité du fonds est restée stable autour de 12% ces 2 dernières années, signe d'une gestion maîtrisée"

---

## 2.10 Probabilités de Perte

### 📊 Logique
Les probabilités de perte estiment la chance de subir une perte sur différents horizons temporels (1M, 3M, 6M, 1Y, 2Y). Elles donnent une perspective concrète et accessible du risque.

### 🧮 Formules

**Méthode Bootstrap Historique**
```
1. Échantillonner aléatoirement (avec remise) des rendements historiques
2. Calculer le rendement cumulé sur l'horizon T
3. Répéter N fois (ex: 10,000 simulations)
4. Compter le % de simulations avec rendement < 0%
```

**Probabilité de perte sur horizon T**
```
P(Perte sur T) = Nombre de simulations avec R_cumulé < 0 / Nombre total de simulations

Exemple: 2500/10000 = 25% de chances de perte sur 1 an
```

**Perte moyenne conditionnelle**
```
Perte_moyenne_si_perte = Moyenne(R_cumulé | R_cumulé < 0)

Exemple: Si perte, elle est en moyenne de -8%
```

### 💡 Interprétation

**Probabilité de perte 1M**
- `< 20%` : Fonds très stable
- `20-40%` : Modéré
- `> 40%` : Volatil

**Probabilité de perte 1Y**
- `< 10%` : Très faible risque annuel
- `10-25%` : Risque modéré
- `> 25%` : Risque élevé

**Règle empirique**
- Plus l'horizon est long, plus la probabilité de perte diminue (si rendement moyen > 0)
- Si P(Perte_1Y) > 30%, profil agressif requis

**Perte moyenne**
- `-5%` : Perte modérée si ça arrive
- `-10%` : Perte conséquente
- `-20%+` : Perte sévère

### ⚠️ Subtilités

1. **Hypothèse i.i.d.** : Suppose que rendements futurs = passés (faux en réalité)
2. **Autocorrélation** : Rendements corrélés violent l'hypothèse bootstrap
3. **Régimes changeants** : Passé peut ne pas refléter le futur
4. **Nombre de simulations** : 10,000 = standard (moins = imprécis, plus = coûteux)
5. **Horizon vs fréquence** : Probabilité 1M basée sur rendements quotidiens peut sous-estimer le risque

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Comprendre le risque de perte réel sur l'horizon d'investissement
- Comparer intuitivement le risque de plusieurs fonds
- **Action concrète** : Si P(Perte_1Y) > 20% pour fonds "prudent", réviser la classification

**🛡️ Gestionnaires de Risque**
- Quantifier le risque en termes accessibles
- Communiquer le risque aux comités
- **Action concrète** : Si P(Perte_3M) > 35%, exiger justification de la stratégie

**💼 Équipe Commerciale**
- Expliquer le risque en langage simple aux clients
- Qualifier la tolérance au risque requise
- **Pitch client** : "Historiquement, ce fonds a 15% de chances de perdre de l'argent sur 1 an, et si cela arrive, la perte moyenne est de 6%"

---

## 2.11 Capture Ratios (Upside/Downside)

### 📊 Logique
Les capture ratios mesurent la capacité du fonds à capturer les hausses du marché (upside) et à limiter les baisses (downside), relativement à un benchmark. Ils indiquent si le fonds "surperforme quand ça monte" et "résiste quand ça baisse".

### 🧮 Formules

**Upside Capture Ratio**
```
UCR = (Rendement_fonds quand Benchmark > 0) / (Rendement_benchmark quand Benchmark > 0) × 100

Exemple: UCR = 110% → Le fonds capture 110% des hausses du marché
```

**Downside Capture Ratio**
```
DCR = (Rendement_fonds quand Benchmark < 0) / (Rendement_benchmark quand Benchmark < 0) × 100

Exemple: DCR = 80% → Le fonds capture seulement 80% des baisses du marché (bien!)
```

**Capture Ratio (global)**
```
CR = UCR / DCR

Exemple: CR = 110 / 80 = 1.375 → Le fonds capture 1.375x plus de hausse que de baisse
```

### 💡 Interprétation

**Upside Capture Ratio**
- `> 100%` : Surperforme dans les hausses (offensif)
- `= 100%` : Suit exactement le benchmark
- `< 100%` : Sous-performe dans les hausses (défensif)

**Downside Capture Ratio**
- `< 100%` : Limite mieux les baisses que le benchmark (bon!)
- `= 100%` : Suit exactement le benchmark
- `> 100%` : Subit plus les baisses (mauvais)

**Profils typiques**
- **UCR > 100%, DCR < 100%** : Profil idéal (gagne plus, perd moins)
- **UCR > 100%, DCR > 100%** : Fonds à beta élevé (amplifie tout)
- **UCR < 100%, DCR < 100%** : Fonds défensif (atténue tout)
- **UCR < 100%, DCR > 100%** : Problème (perd la hausse ET la baisse)

**Capture Ratio Global**
- `> 1.2` : Excellent
- `1.0-1.2` : Bon
- `0.8-1.0` : Acceptable
- `< 0.8` : Problématique

### ⚠️ Subtilités

1. **Choix du benchmark** : Doit être pertinent (même classe d'actifs, même géographie)
2. **Périodes asymétriques** : Peut y avoir plus de jours de hausse que de baisse (ou inverse)
3. **Magnitude vs fréquence** : Ne distingue pas "petites hausses fréquentes" vs "grandes hausses rares"
4. **Non-linéarité** : Peut varier selon les périodes

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Identifier les fonds "gagnants" (UCR > 100%, DCR < 100%)
- Construire des portefeuilles core-satellite
- **Action concrète** : Si UCR < 95% et DCR > 105%, éliminer le fonds (détruit de la valeur)

**🛡️ Gestionnaires de Risque**
- Valider que le fonds respecte son positionnement (offensif/défensif)
- Détecter les dérives de style
- **Action concrète** : Si fonds "prudent" a DCR > 120%, exiger explication

**💼 Équipe Commerciale**
- Valoriser la capacité du fonds à "gagner plus, perdre moins"
- Différencier vs benchmark et concurrence
- **Pitch client** : "Notre fonds capture 105% des hausses du marché et seulement 85% des baisses, offrant un profil asymétrique attractif"

---

## 2.12 Récapitulatif des Analyses de Valeurs Liquidatives

**Résumé des 12 analyses clés** :

| Analyse | Gestionnaire de Portefeuille | Gestionnaire de Risque | Équipe Commerciale |
|---------|------------------------------|------------------------|-------------------|
| Performances Calendaires | Suivi court terme, ajustements tactiques | Détection rapide des déviations | Communication performance récente |
| Performances Glissantes | Évaluation consistance LT | Validation track record | Argumentation performance durable |
| Métriques de Risque | Comparaison efficience (Sharpe) | Définition limites de risque | Qualification profil risque |
| Distributions & Stats | Validation modèles | Ajustement modèles si non-normalité | Explication comportement fonds |
| Corrélations | Construction portefeuilles diversifiés | Mesure risque concentration | Proposition combinaisons fonds |
| Risk Fingerprint | Visualisation profil complet | Détection faiblesses critiques | Présentation visuelle profil |
| Régimes de Volatilité | Allocation selon régime | Surveillance transitions | Qualification "tout temps" |
| Drawdowns | Dimensionnement allocation | Alertes drawdown actuel | Communication "pire cas" |
| Indicateurs Glissants | Ajustements dynamiques | Surveillance continue risque | Démonstration stabilité |
| Probabilités de Perte | Compréhension risque réel | Quantification accessible | Explication risque simple |
| Capture Ratios | Identification fonds "gagnants" | Validation positionnement | Valorisation asymétrie |

---

# 3. Analyses des Souscriptions et Rachats

Les souscriptions et rachats représentent les flux entrants et sortants du fonds. Cette section détaille comment ces analyses permettent de comprendre le comportement des investisseurs et la dynamique commerciale.

---

## 3.1 Flux Nets (Souscriptions - Rachats)

### 📊 Logique
Les flux nets mesurent la différence entre souscriptions et rachats. Un flux net positif indique une collecte nette (attractivité), un flux net négatif indique des sorties nettes (décollecte).

### 🧮 Formules

**Flux Net**
```
Flux_Net(t) = Souscriptions(t) - Rachats(t)

Peut être positif (collecte) ou négatif (décollecte)
```

**Taux de Collecte**
```
Taux_Collecte(t) = (Flux_Net(t) / Actifs_Nets(t-1)) × 100

Exprime le flux net en % des actifs
```

**Collecte Cumulée**
```
Collecte_Cumulée(t) = Σ Flux_Net(0→t)

Somme de tous les flux nets depuis l'origine
```

**Taux de Rotation**
```
Taux_Rotation = (Souscriptions + Rachats) / (2 × Actifs_Moyens) × 100

Mesure l'activité (indépendamment du sens)
```

### 💡 Interprétation

**Flux Net**
- `> 0` : Collecte nette (bon signe commercial)
- `= 0` : Équilibre
- `< 0` : Décollecte (attention)

**Magnitude**
- `|Flux| < 5% Actifs` : Flux modérés
- `|Flux| 5-15% Actifs` : Flux significatifs
- `|Flux| > 15% Actifs` : Flux exceptionnels

**Tendances temporelles**
- **Tendance haussière continue** : Fonds en croissance
- **Tendance baissière** : Perte de confiance
- **Volatilité élevée** : Comportement erratique des investisseurs
- **Saisonnalité** : Pics de fin d'année fiscale

**Taux de Rotation**
- `< 20%` : Investisseurs stables (long terme)
- `20-50%` : Activité modérée
- `> 50%` : Forte rotation (court terme, volatil)

### ⚠️ Subtilités

1. **Causalité inversée** : Bonne performance → souscriptions OU souscriptions → bonne performance (flux push prices)
2. **Effet de taille** : 10M€ de collecte = beaucoup pour petit fonds, peu pour grand fonds
3. **Lag temporel** : Souscriptions suivent la performance avec décalage (investors chase returns)
4. **Saisonnalité** : Fin d'année fiscale, début d'année (new money)
5. **Type de client** : Institutionnels = gros flux ponctuels, Retail = petits flux continus

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Anticiper les besoins de liquidité (gros rachats)
- Gérer les entrées massives sans diluer la performance
- Ajuster la stratégie si flux créent des contraintes
- **Action concrète** : Si flux entrant > 20% actifs, préparer un plan de déploiement progressif

**🛡️ Gestionnaires de Risque**
- Surveiller les décollectes massives (risque de liquidité)
- Valider que le fonds peut honorer les rachats
- Détecter les comportements de "run" (panique)
- **Action concrète** : Si décollecte > 10% en 1 mois, stress-tester la liquidité du portefeuille

**💼 Équipe Commerciale**
- Utiliser la collecte comme preuve de confiance
- Identifier les périodes de forte activité commerciale
- Comprendre la saisonnalité pour planifier les campagnes
- **Pitch client** : "Notre fonds a collecté 50M€ nets en 2024, reflétant la confiance de 500+ investisseurs"

---

## 3.2 Analyse par Type de Client

### 📊 Logique
Distinguer les flux par type de client (Institutionnels, Retail, Corporates, etc.) permet de comprendre la structure de la base d'investisseurs et les dynamiques différentes de chaque segment.

### 🧮 Formules

**Part de chaque segment**
```
Part_Segment_X = Souscriptions_X / Total_Souscriptions × 100

Exemple: Part_Institutionnels = 70% → 70% des souscriptions viennent d'institutionnels
```

**Flux Net par segment**
```
Flux_Net_Segment_X = Souscriptions_X - Rachats_X
```

**Taux de Rétention par segment**
```
Taux_Rétention_X = (Actifs_X(t) - Flux_Net_X(t)) / Actifs_X(t-1)

Mesure la stabilité du segment (hors flux)
```

### 💡 Interprétation

**Institutionnels**
- **Caractéristiques** : Gros tickets, long terme, sensibles à la performance
- **Flux positifs** : Validation professionnelle
- **Flux négatifs** : Signal d'alarme (ils ont accès à plus d'info)

**Retail (Particuliers)**
- **Caractéristiques** : Petits tickets, émotionnels, chasse la performance
- **Flux positifs** : Base large, stable
- **Flux négatifs** : Panique potentielle en crise

**Corporates**
- **Caractéristiques** : Moyens tickets, moyen terme, fiscalement motivés
- **Saisonnalité** : Forte en fin d'année fiscale

**Diversification de la base**
- **> 80% d'un segment** : Concentration risquée
- **Bien réparti** : Résilience accrue

### ⚠️ Subtilités

1. **Comportement contracyclique** : Institutionnels peuvent acheter quand Retail vend (opportunité)
2. **Effet de contagion** : Si un segment panique, peut contaminer les autres
3. **Sticky money vs hot money** : Institutionnels LT = sticky, Retail CT = hot
4. **Réglementation** : Certains segments soumis à contraintes réglementaires

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Comprendre qui sont les "vrais" investisseurs long terme
- Anticiper les flux selon le comportement typique de chaque segment
- **Action concrète** : Si base > 70% Retail et performance négative, prévoir des rachats massifs

**🛡️ Gestionnaires de Risque**
- Évaluer le risque de run selon la composition de la base
- Identifier les concentrations dangereuses
- **Action concrète** : Si > 50% d'un seul investisseur institutionnel, exiger un buffer de liquidité

**💼 Équipe Commerciale**
- Cibler les efforts de distribution (quel segment croît/décroît)
- Adapter le discours à chaque segment
- Construire une base diversifiée
- **Stratégie** : "Nous visons 60% Institutionnels, 30% Retail, 10% Corporates pour une base stable"

---

## 3.3 Analyse Temporelle et Saisonnalité

### 📊 Logique
Les flux présentent souvent des patterns temporels : tendances, cycles, saisonnalité. Les identifier permet d'anticiper et de planifier.

### 🧮 Formules

**Décomposition Temporelle (Seasonal Decompose)**
```
Série = Tendance + Saisonnalité + Résidus

Tendance = Moyenne mobile longue (ex: 12 mois)
Saisonnalité = Pattern répétitif annuel
Résidus = Variations inexpliquées
```

**Taux de Croissance Mensuel**
```
Taux_Croissance(t) = (Flux(t) - Flux(t-1)) / |Flux(t-1)| × 100

Mesure l'accélération/décélération
```

**Autocorrélation**
```
ACF(lag) = Corr(Flux(t), Flux(t-lag))

Mesure si les flux d'un mois prédisent le mois suivant
```

### 💡 Interprétation

**Tendance**
- **Haussière** : Fonds en phase de croissance
- **Stable** : Maturité
- **Baissière** : Déclin

**Saisonnalité**
- **Q1** : Nouveaux budgets d'investissement (hausse)
- **Q4** : Optimisation fiscale (hausse ou baisse selon produit)
- **Été** : Faible activité
- **Patterns spécifiques** : Ex: hausse chaque janvier

**Volatilité des flux**
- **Faible** : Base stable, prévisible
- **Élevée** : Base volatile, difficile à gérer

**Autocorrélation positive**
- Flux d'un mois prédisent le suivant
- Permet le forecasting

### ⚠️ Subtilités

1. **Changement de régime** : Saisonnalité historique peut disparaître
2. **Événements exceptionnels** : Faussent les patterns (COVID, crises)
3. **Taille de l'échantillon** : Besoin de >24 mois pour saisonnalité fiable
4. **Décomposition additive vs multiplicative** : Choisir selon la nature des données

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Anticiper les besoins de liquidité saisonniers
- Planifier les investissements selon les flux attendus
- **Action concrète** : Si saisonnalité montre rachats en décembre, augmenter cash en novembre

**🛡️ Gestionnaires de Risque**
- Prévoir les stress de liquidité saisonniers
- Ajuster les limites selon les périodes
- **Action concrète** : Exiger 15% de cash en périodes de rachats historiquement élevés

**💼 Équipe Commerciale**
- Planifier les campagnes selon les périodes favorables
- Expliquer les variations saisonnières aux clients
- **Stratégie** : "Nos campagnes de communication se concentrent en janvier et septembre, pics historiques de souscriptions"

---

## 3.4 Récapitulatif des Analyses de Souscriptions & Rachats

**Résumé des analyses clés** :

| Analyse | Gestionnaire de Portefeuille | Gestionnaire de Risque | Équipe Commerciale |
|---------|------------------------------|------------------------|-------------------|
| Flux Nets | Anticiper besoins liquidité | Surveiller décollectes massives | Preuve de confiance |
| Type de Client | Comprendre investisseurs LT | Évaluer risque de run | Cibler distribution |
| Temporalité & Saisonnalité | Planifier investissements | Prévoir stress liquidité | Planifier campagnes |
| Corrélation Flux-Perf | Anticiper flux futurs | Identifier base volatile | Timing commercial |

---

# 4. Analyses des Actifs Nets

Les actifs nets représentent la valeur totale du fonds. Cette section détaille comment l'analyse de leur évolution et composition informe sur la santé et la dynamique du fonds.

---

## 4.1 Évolution et Croissance des Actifs

### 📊 Logique
L'évolution des actifs nets combine les effets de la performance (valorisation) et des flux (souscriptions/rachats). Décomposer ces deux contributions permet de comprendre les sources de croissance.

### 🧮 Formules

**Variation des Actifs**
```
ΔActifs(t) = Actifs(t) - Actifs(t-1)
```

**Décomposition de la variation**
```
ΔActifs(t) = Effet_Performance + Effet_Flux

Effet_Performance = Actifs(t-1) × Rendement(t)
Effet_Flux = Souscriptions(t) - Rachats(t)
```

**Taux de Croissance**
```
Taux_Croissance = (Actifs(t) / Actifs(t-1) - 1) × 100
```

**CAGR (Compound Annual Growth Rate)**
```
CAGR = ((Actifs_final / Actifs_initial)^(1/années) - 1) × 100

Mesure la croissance annualisée moyenne
```

### 💡 Interprétation

**Croissance forte avec flux positifs et performance positive**
- **Meilleur scénario** : Cercle vertueux (performance attire flux)

**Croissance malgré flux négatifs**
- Performance compense les rachats
- Base se réduit mais fonds performant

**Décroissance malgré flux positifs**
- Performance négative plus forte que les souscriptions
- Signal d'alarme

**CAGR**
- `> 15%` : Forte croissance
- `5-15%` : Croissance modérée
- `0-5%` : Faible croissance
- `< 0%` : Déclin

### ⚠️ Subtilités

1. **Timing des flux** : Flux arrivés en début vs fin de période ont impact différent
2. **Effet de base** : Croissance % facile sur petite base, difficile sur grosse base
3. **Dividendes** : Si distribués, réduisent les actifs (ne pas confondre avec performance)
4. **Changement de stratégie** : Fusion/scission fausse les comparaisons historiques

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Comprendre si croissance = performance ou collecte commerciale
- Gérer les contraintes de taille (marchés illiquides)
- **Action concrète** : Si actifs doublent par flux, adapter stratégie pour éviter dilution performance

**🛡️ Gestionnaires de Risque**
- Surveiller les fonds en déclin rapide (risque de fermeture)
- Valider que croissance reste gérable
- **Action concrète** : Si actifs > seuil de liquidité du marché, exiger diversification

**💼 Équipe Commerciale**
- Mettre en avant la croissance des actifs
- Distinguer croissance organique (performance) vs inorganique (flux)
- **Pitch client** : "Notre fonds a crû de 120M€ à 180M€ en 2 ans, dont 70% grâce à la performance"

---

## 4.2 Analyse de Saisonnalité des Actifs

### 📊 Logique
Les actifs peuvent présenter des patterns saisonniers liés aux flux, à la performance ou aux deux. Identifier ces patterns permet d'anticiper et de planifier.

### 🧮 Formules

**Décomposition Saisonnière**
```
Actifs(t) = Tendance(t) + Saisonnalité(t) + Résidus(t)

Via méthode STL (Seasonal and Trend decomposition using Loess)
```

**Indice Saisonnier**
```
Indice_Mois_X = Moyenne_Mois_X / Moyenne_Annuelle × 100

> 100 = mois fort
< 100 = mois faible
```

### 💡 Interprétation

**Saisonnalité forte**
- Indice varie de >20 points entre mois fort et faible
- Patterns prévisibles

**Patterns typiques**
- **Janvier** : Souvent fort (nouveaux budgets)
- **Décembre** : Variable (optimisation fiscale)
- **Été** : Souvent faible (vacances)

### ⚠️ Subtilités

1. **Besoin de données** : >2 ans nécessaires pour détecter saisonnalité
2. **Changements** : Patterns peuvent évoluer
3. **Causalité** : Saisonnalité actifs = combinaison saisonnalité flux + performance

### 🎯 Utilité par Profil

**👨‍💼 Gestionnaires de Portefeuilles**
- Anticiper les variations saisonnières de taille
- Planifier liquidité selon les patterns
- **Action concrète** : Si actifs +15% chaque janvier, préparer déploiement en décembre

**🛡️ Gestionnaires de Risque**
- Ajuster les seuils et limites selon la saison
- Prévoir les stress saisonniers
- **Action concrète** : Exiger 20% cash en décembre si rachats saisonniers élevés

**💼 Équipe Commerciale**
- Concentrer efforts sur périodes favorables
- Expliquer variations saisonnières aux clients
- **Stratégie** : "Historiquement, janvier et septembre sont nos mois de collecte forte"

---

## 4.3 Récapitulatif des Analyses d'Actifs Nets

**Résumé des analyses clés** :

| Analyse | Gestionnaire de Portefeuille | Gestionnaire de Risque | Équipe Commerciale |
|---------|------------------------------|------------------------|-------------------|
| Évolution & Croissance | Comprendre sources croissance | Surveiller déclin rapide | Valoriser croissance |
| Saisonnalité | Planifier liquidité | Ajuster limites saisonnières | Timing commercial |
| Répartition par FCP | Gérer contraintes taille | Mesurer concentration | Identifier fonds stars |

---

# 5. Synthèse et Recommandations d'Usage

## 5.1 Vue d'Ensemble : Un Système Décisionnel Intégré

Les trois modules d'analyse (Valeurs Liquidatives, Souscriptions & Rachats, Actifs Nets) forment un **système décisionnel intégré** où chaque pièce informe les autres :

**Boucle Vertueuse**
```
Performance → Flux Positifs → Croissance Actifs → Économies d'Échelle → Meilleure Performance
```

**Boucle Vicieuse**
```
Sous-Performance → Rachats → Décroissance Actifs → Coûts Fixes Élevés → Pire Performance
```

**Interactions Clés**
- **VL ↔ Flux** : Performance attire/repousse les investisseurs
- **Flux ↔ Actifs** : Collecte fait croître les actifs
- **Actifs ↔ VL** : Taille impacte la capacité de performance

## 5.2 Guide d'Usage par Profil

### 👨‍💼 Pour les Gestionnaires de Portefeuilles

**Routine Quotidienne**
1. Consulter VL et rendements quotidiens
2. Vérifier indicateurs de risque glissants
3. Surveiller régimes de volatilité actuels

**Routine Hebdomadaire**
1. Analyser performances WTD et MTD
2. Examiner flux nets de la semaine
3. Ajuster allocations si nécessaire

**Routine Mensuelle**
1. Revoir performances calendaires et glissantes
2. Analyser métriques de risque complètes
3. Étudier distributions et corrélations
4. Examiner flux par type de client
5. Projeter actifs du mois suivant

**Routine Trimestrielle**
1. Revue complète Risk Fingerprint
2. Analyse régimes de volatilité sur le trimestre
3. Décomposition croissance actifs (perf vs flux)
4. Réévaluation stratégique si nécessaire

**Décisions Clés Supportées**
- ✅ Allocation d'actifs (quel fonds, quelle proportion)
- ✅ Timing d'entrée/sortie (régimes de volatilité)
- ✅ Gestion de la liquidité (anticipation flux)
- ✅ Dimensionnement des positions (contraintes taille)

### 🛡️ Pour les Gestionnaires de Risque

**Routine Quotidienne**
1. Surveiller drawdowns actuels vs historiques
2. Vérifier VaR/CVaR glissantes
3. Alertes sur dépassements de seuils

**Routine Hebdomadaire**
1. Examiner volatilité glissante
2. Vérifier flux nets (risque de décollecte)
3. Contrôler exposition par régime de volatilité

**Routine Mensuelle**
1. Revue complète des métriques de risque
2. Test de conformité aux limites prospectus
3. Analyse flux par type client (risque concentration)
4. Stress tests sur actifs (scénarios de crise)

**Routine Trimestrielle**
1. Audit complet Risk Fingerprint
2. Validation profils vs promesses commerciales
3. Décomposition sources de risque
4. Rapport risque au comité

**Décisions Clés Supportées**
- ✅ Définition/ajustement des limites de risque
- ✅ Déclenchement d'alertes et escalations
- ✅ Validation de conformité réglementaire
- ✅ Recommandations de réduction d'exposition

### 💼 Pour l'Équipe Commerciale

**Routine Quotidienne**
1. Consulter performances du jour
2. Préparer arguments pour prospects

**Routine Hebdomadaire**
1. Analyser WTD, MTD pour pitchs
2. Identifier fonds en forme pour pushs commerciaux

**Routine Mensuelle**
1. Préparer factsheets avec performances
2. Analyser flux de collecte du mois
3. Identifier segments client actifs
4. Planifier campagnes selon saisonnalité

**Routine Trimestrielle**
1. Préparation présentations clients (QTD, YTD)
2. Benchmarking vs concurrence
3. Revue stratégie commerciale par fonds
4. Célébration des succès (fonds en collecte)

**Arguments Clés par Analyse**
- **Performances** : "YTD +12%, top quartile de la catégorie"
- **Risque** : "Volatilité 10%, Sharpe 1.3, profil équilibré"
- **Risk Fingerprint** : "Score global 75/100, excellente résilience"
- **Flux** : "50M€ collectés en 2024, confiance de 1000+ clients"
- **Actifs** : "180M€ d'actifs, taille optimale pour liquidité et performance"

## 5.3 Pièges à Éviter

**Erreurs Communes**

1. **Surinvestir les performances passées**
   - ⚠️ "Ce fonds a fait +30% l'an dernier donc je mets tout dedans"
   - ✅ Regarder la consistance (3Y, 5Y) et le profil de risque

2. **Ignorer les corrélations**
   - ⚠️ "J'ai 5 fonds, je suis bien diversifié"
   - ✅ Si corrélations > 0.8, c'est comme avoir 1 seul fonds

3. **Confondre volatilité et risque**
   - ⚠️ "Volatilité faible = pas de risque"
   - ✅ Regarder aussi skewness, kurtosis, drawdowns

4. **Chasser la performance**
   - ⚠️ "Le fonds a fait +20% récemment, j'achète"
   - ✅ Vérifier si c'est soutenable ou un pic isolé

5. **Ignorer les flux**
   - ⚠️ "Peu importe les rachats, seule la performance compte"
   - ✅ Décollecte massive = signal d'alarme (autres investisseurs savent quelque chose)

6. **Sur-optimiser**
   - ⚠️ "Mon modèle dit d'allouer exactement 23.47% à ce fonds"
   - ✅ Les décimales sont illusoires, rester pragmatique

7. **Négliger la taille**
   - ⚠️ "Excellent fonds, je recommande pour tous mes clients"
   - ✅ Fonds trop petit = risque de fermeture, trop gros = contraintes

8. **Croire à la normalité**
   - ⚠️ "Les rendements suivent une loi normale"
   - ✅ Fat tails existent, utiliser CVaR et scénarios extrêmes

## 5.4 Conclusion

Les analyses présentées dans ce guide forment un **écosystème décisionnel complet** permettant de :

**Pour les Gestionnaires de Portefeuilles** :
- Construire des portefeuilles optimisés
- Anticiper les besoins de liquidité
- Ajuster dynamiquement les allocations

**Pour les Gestionnaires de Risque** :
- Quantifier et surveiller le risque multi-dimensionnellement
- Détecter rapidement les dégradations
- Assurer la conformité réglementaire

**Pour l'Équipe Commerciale** :
- Communiquer efficacement avec les clients
- Différencier les produits
- Planifier les actions commerciales

**Principe Directeur** : Aucune analyse n'est suffisante seule. C'est la **combinaison intelligente** de plusieurs perspectives (performance, risque, flux, actifs) qui permet des décisions robustes et éclairées.

---

**© 2025 CGF BOURSE - Tous droits réservés**

*Ce document est destiné à un usage interne pour les équipes de gestion, de risque et commerciales. Il ne constitue pas un conseil en investissement et ne doit pas être diffusé à des tiers sans autorisation.*

