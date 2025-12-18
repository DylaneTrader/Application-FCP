"""
A Propos - Documentation de l'Application
Détaille toutes les notions, formules et concepts utilisés dans l'application
"""

import streamlit as st
from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR

# Configuration de la page
st.set_page_config(
    page_title="Analyse FCP - À Propos",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(f"""
<style>
    .doc-section {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {PRIMARY_COLOR};
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .formula-box {{
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border-left: 3px solid {SECONDARY_COLOR};
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }}
    .concept-card {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, white 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }}
    .warning-box {{
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown(f'<h1 style="color: {PRIMARY_COLOR};">ℹ️ À Propos - Documentation Complète</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Cette page détaille toutes les notions, formules mathématiques et concepts utilisés dans l'application 
    d'analyse des Fonds Communs de Placement (FCP).
    """)
    
    # Sommaire
    st.markdown("---")
    st.markdown("## 📑 Sommaire")
    
    st.markdown("""
    1. [Notions Fondamentales](#notions-fondamentales)
    2. [Indicateurs de Performance](#indicateurs-de-performance)
    3. [Mesures de Risque](#mesures-de-risque)
    4. [Analyse Avancée](#analyse-avancée)
    5. [Interprétation des Résultats](#interprétation-des-résultats)
    6. [Glossaire](#glossaire)
    """)
    
    st.markdown("---")
    
    # Section 1: Notions Fondamentales
    st.markdown('<a id="notions-fondamentales"></a>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color: {PRIMARY_COLOR};">1️⃣ Notions Fondamentales</h2>', unsafe_allow_html=True)
    
    with st.expander("📊 Valeur Liquidative (VL)", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>La Valeur Liquidative représente la valeur d'une part du fonds à un instant donné. 
        Elle est calculée quotidiennement en divisant l'actif net du fonds par le nombre de parts en circulation.</p>
        
        <div class="formula-box">
        VL = Actif Net Total / Nombre de Parts
        </div>
        
        <h4>Utilisation dans l'application</h4>
        <ul>
            <li>Calcul des rendements quotidiens, hebdomadaires, mensuels</li>
            <li>Analyse des performances glissantes (1M, 3M, 6M, 1A, 5A)</li>
            <li>Normalisation pour comparaisons (base 100)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📈 Rendement", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Rendement Simple</h3>
        <div class="formula-box">
        R = (VL_fin - VL_début) / VL_début × 100
        </div>
        
        <h3>Rendement Logarithmique (utilisé pour les calculs)</h3>
        <div class="formula-box">
        r = ln(VL_fin / VL_début)
        </div>
        
        <p><strong>Avantage du rendement logarithmique :</strong> Additivité des rendements sur plusieurs périodes et propriétés statistiques plus robustes.</p>
        
        <h4>Périodes Calendaires</h4>
        <ul>
            <li><strong>WTD (Week to Date)</strong> : Depuis le début de la semaine</li>
            <li><strong>MTD (Month to Date)</strong> : Depuis le début du mois</li>
            <li><strong>QTD (Quarter to Date)</strong> : Depuis le début du trimestre</li>
            <li><strong>YTD (Year to Date)</strong> : Depuis le début de l'année</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("💰 Souscriptions et Rachats", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définitions</h3>
        <ul>
            <li><strong>Souscription</strong> : Achat de parts du fonds (flux entrant)</li>
            <li><strong>Rachat</strong> : Vente de parts du fonds (flux sortant)</li>
        </ul>
        
        <h3>Flux Net</h3>
        <div class="formula-box">
        Flux Net = Souscriptions - Rachats
        </div>
        <p>Un flux net positif indique une collecte nette (plus d'entrées que de sorties).</p>
        
        <h3>Taux de Collecte</h3>
        <div class="formula-box">
        Taux de Collecte = (Souscriptions / Rachats) × 100
        </div>
        <p>Un taux supérieur à 100% indique une attractivité du fonds.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 2: Indicateurs de Performance
    st.markdown("---")
    st.markdown('<a id="indicateurs-de-performance"></a>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color: {PRIMARY_COLOR};">2️⃣ Indicateurs de Performance</h2>', unsafe_allow_html=True)
    
    with st.expander("📊 Ratio de Sharpe", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Formule</h3>
        <div class="formula-box">
        Sharpe = (Rendement Moyen - Taux sans Risque) / Volatilité
        </div>
        
        <p><strong>Dans l'application :</strong> Le taux sans risque est considéré comme nul pour simplifier.</p>
        <div class="formula-box">
        Sharpe = Rendement Moyen / Écart-Type des Rendements
        </div>
        
        <h4>Annualisation</h4>
        <div class="formula-box">
        Sharpe Annualisé = Sharpe Quotidien × √252
        </div>
        <p><small>252 = nombre de jours de trading par an</small></p>
        
        <h4>Interprétation</h4>
        <ul>
            <li><strong>Sharpe > 1</strong> : Bon ratio risque/rendement</li>
            <li><strong>Sharpe > 2</strong> : Excellent ratio</li>
            <li><strong>Sharpe < 0</strong> : Performance inférieure au taux sans risque</li>
        </ul>
        
        <div class="warning-box">
        <strong>⚠️ Limites :</strong> Le ratio de Sharpe suppose une distribution normale des rendements, 
        ce qui n'est pas toujours le cas (voir Skewness et Kurtosis).
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📉 Maximum Drawdown", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>Le Maximum Drawdown représente la plus grande perte depuis un sommet historique.</p>
        
        <h3>Calcul</h3>
        <div class="formula-box">
        Pour chaque point t :
        Peak_t = max(VL_0, VL_1, ..., VL_t)
        Drawdown_t = (VL_t - Peak_t) / Peak_t × 100
        Maximum Drawdown = min(Drawdown_t) pour tout t
        </div>
        
        <h4>Métriques Associées</h4>
        <ul>
            <li><strong>Drawdown Duration</strong> : Temps entre le pic et le creux</li>
            <li><strong>Recovery Time</strong> : Temps entre le creux et le retour au pic</li>
            <li><strong>Drawdown Depth</strong> : Ampleur de la baisse (-X%)</li>
        </ul>
        
        <h4>Interprétation</h4>
        <p>Un Maximum Drawdown de -20% signifie que l'investisseur a pu voir son capital diminuer de 20% 
        depuis un point haut. Plus ce chiffre est faible (proche de 0%), meilleur est le fonds.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🎯 Capture Ratios", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Upside Capture Ratio</h3>
        <div class="formula-box">
        Upside Capture = (Rendement Fonds en Marché Haussier / Rendement Marché en Haussier) × 100
        </div>
        <p>Mesure la participation du fonds aux hausses du marché.</p>
        
        <h3>Downside Capture Ratio</h3>
        <div class="formula-box">
        Downside Capture = (Rendement Fonds en Marché Baissier / Rendement Marché en Baissier) × 100
        </div>
        <p>Mesure la participation du fonds aux baisses du marché.</p>
        
        <h4>Interprétation</h4>
        <ul>
            <li><strong>Upside Capture > 100%</strong> : Le fonds surperforme en marché haussier</li>
            <li><strong>Downside Capture < 100%</strong> : Le fonds protège mieux en marché baissier (bon)</li>
            <li><strong>Idéal</strong> : Upside > 100% et Downside < 100% (asymétrie positive)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 3: Mesures de Risque
    st.markdown("---")
    st.markdown('<a id="mesures-de-risque"></a>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color: {PRIMARY_COLOR};">3️⃣ Mesures de Risque</h2>', unsafe_allow_html=True)
    
    with st.expander("📊 Volatilité", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>La volatilité mesure la dispersion des rendements autour de leur moyenne. 
        C'est l'écart-type des rendements.</p>
        
        <h3>Formule</h3>
        <div class="formula-box">
        σ = √[Σ(r_i - μ)² / (n-1)]
        
        où :
        - r_i = rendement à la période i
        - μ = rendement moyen
        - n = nombre d'observations
        </div>
        
        <h4>Volatilité Annualisée</h4>
        <div class="formula-box">
        σ_annuelle = σ_quotidienne × √252
        </div>
        
        <h4>Interprétation</h4>
        <ul>
            <li><strong>Volatilité < 10%</strong> : Fonds peu risqué</li>
            <li><strong>Volatilité 10-20%</strong> : Risque modéré</li>
            <li><strong>Volatilité > 20%</strong> : Fonds très volatil</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📉 Value at Risk (VaR)", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>La VaR (Value at Risk) estime la perte maximale potentielle sur un horizon donné 
        avec un niveau de confiance spécifié.</p>
        
        <h3>Calcul (Méthode Historique)</h3>
        <div class="formula-box">
        VaR_95% = 5e percentile des rendements
        </div>
        <p>Signifie qu'il y a 5% de chances que la perte soit supérieure à cette valeur.</p>
        
        <h4>Exemple</h4>
        <p>VaR 95% = -2.5% signifie que dans 95% des cas, la perte quotidienne ne dépassera pas 2.5%.</p>
        
        <div class="warning-box">
        <strong>⚠️ Limite :</strong> La VaR ne dit rien sur l'ampleur des pertes au-delà du seuil.
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📉 Conditional VaR (CVaR)", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>La CVaR (ou Expected Shortfall) mesure la perte moyenne <strong>conditionnelle</strong> 
        au dépassement du seuil VaR.</p>
        
        <h3>Formule</h3>
        <div class="formula-box">
        CVaR_95% = Moyenne des rendements ≤ VaR_95%
        </div>
        
        <h4>Avantage sur la VaR</h4>
        <p>La CVaR donne une information sur l'ampleur moyenne des pertes extrêmes, 
        pas seulement leur probabilité. C'est une mesure plus conservatrice et plus informative.</p>
        
        <h4>Exemple</h4>
        <ul>
            <li>VaR 95% = -2.5%</li>
            <li>CVaR 95% = -3.8%</li>
        </ul>
        <p>→ Quand la perte dépasse le seuil de 2.5%, elle est en moyenne de 3.8%.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📊 Skewness (Asymétrie)", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>La Skewness mesure l'asymétrie de la distribution des rendements par rapport à la moyenne.</p>
        
        <h3>Formule</h3>
        <div class="formula-box">
        Skewness = E[(r - μ)³] / σ³
        </div>
        
        <h4>Interprétation</h4>
        <ul>
            <li><strong>Skewness > 0</strong> : Asymétrie positive (queue droite longue) 
                <br>→ Plus de chances de gains extrêmes que de pertes extrêmes (favorable)</li>
            <li><strong>Skewness ≈ 0</strong> : Distribution symétrique (proche loi normale)</li>
            <li><strong>Skewness < 0</strong> : Asymétrie négative (queue gauche longue) 
                <br>→ Plus de chances de pertes extrêmes (défavorable, "tail risk")</li>
        </ul>
        
        <div class="concept-card">
        <strong>💡 En pratique :</strong> Les investisseurs préfèrent une skewness positive, 
        car elle indique un potentiel de gains extrêmes supérieur au risque de pertes extrêmes.
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📊 Kurtosis (Aplatissement)", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>La Kurtosis mesure "l'épaisseur des queues" de la distribution, 
        c'est-à-dire la fréquence des événements extrêmes.</p>
        
        <h3>Formule (Excess Kurtosis)</h3>
        <div class="formula-box">
        Kurtosis = E[(r - μ)⁴] / σ⁴ - 3
        </div>
        <p><small>On soustrait 3 car la loi normale a une kurtosis de 3</small></p>
        
        <h4>Interprétation</h4>
        <ul>
            <li><strong>Kurtosis > 0</strong> : Distribution leptokurtique (queues épaisses)
                <br>→ Plus d'événements extrêmes que prévu par loi normale</li>
            <li><strong>Kurtosis ≈ 0</strong> : Distribution normale</li>
            <li><strong>Kurtosis < 0</strong> : Distribution platykurtique (queues fines)
                <br>→ Moins d'événements extrêmes</li>
        </ul>
        
        <div class="warning-box">
        <strong>⚠️ Attention :</strong> Une kurtosis élevée indique un risque de "black swan" 
        (événements extrêmes rares mais impactants).
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 4: Analyse Avancée
    st.markdown("---")
    st.markdown('<a id="analyse-avancée"></a>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color: {PRIMARY_COLOR};">4️⃣ Analyse Avancée</h2>', unsafe_allow_html=True)
    
    with st.expander("🎯 Ulcer Index", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>L'Ulcer Index mesure la "douleur" ressentie par l'investisseur lors des drawdowns. 
        Il prend en compte à la fois la profondeur et la durée des pertes.</p>
        
        <h3>Formule</h3>
        <div class="formula-box">
        Pour chaque période t :
        Drawdown_t = (VL_t - Peak_t) / Peak_t × 100
        
        Ulcer Index = √[Σ(Drawdown_t)² / n]
        </div>
        
        <h4>Interprétation</h4>
        <p>Plus l'Ulcer Index est faible, moins l'investisseur subit de "douleur" due aux pertes. 
        C'est une mesure plus intuitive que la volatilité pour mesurer le risque ressenti.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🎯 Pain Ratio", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Définition</h3>
        <p>Le Pain Ratio mesure le rendement généré par unité de "douleur" (Ulcer Index).</p>
        
        <h3>Formule</h3>
        <div class="formula-box">
        Pain Ratio = Rendement Total / Ulcer Index
        </div>
        
        <h4>Interprétation</h4>
        <ul>
            <li><strong>Pain Ratio > 2</strong> : Excellent (rendement compense largement la douleur)</li>
            <li><strong>Pain Ratio 1-2</strong> : Bon</li>
            <li><strong>Pain Ratio < 1</strong> : Faible (douleur pas suffisamment compensée)</li>
        </ul>
        
        <div class="concept-card">
        <strong>💡 Avantage :</strong> Le Pain Ratio est plus intuitif que le Sharpe pour les investisseurs, 
        car il se concentre sur les pertes réelles plutôt que sur la volatilité symétrique.
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📊 Profil de Risque (Risk Fingerprint)", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Concept</h3>
        <p>Le Risk Fingerprint est une représentation multidimensionnelle du profil de risque 
        sur 7 dimensions normalisées (0-100).</p>
        
        <h4>Les 7 Dimensions</h4>
        <ol>
            <li><strong>Stabilité</strong> : Inverse de la volatilité (plus haut = plus stable)</li>
            <li><strong>Résilience</strong> : Inverse du max drawdown (plus haut = plus résilient)</li>
            <li><strong>Récupération</strong> : Inverse du temps de récupération moyen</li>
            <li><strong>Protection Extrême</strong> : Inverse de la CVaR (plus haut = mieux protégé)</li>
            <li><strong>Asymétrie</strong> : Skewness normalisée (plus haut = meilleure asymétrie)</li>
            <li><strong>Sharpe Stable</strong> : Stabilité du ratio de Sharpe dans le temps</li>
            <li><strong>Pain Ratio</strong> : Rendement ajusté à la douleur</li>
        </ol>
        
        <h4>Normalisation</h4>
        <div class="formula-box">
        Score_normalisé = (Valeur - Min) / (Max - Min) × 100
        </div>
        <p>Permet de comparer les fonds sur une échelle commune.</p>
        
        <h4>Visualisation</h4>
        <p>Le profil est affiché sous forme de radar chart (spider chart) permettant 
        d'identifier visuellement les forces et faiblesses du fonds.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🔄 Régimes de Volatilité", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Concept</h3>
        <p>Identification des différents régimes de marché basés sur la volatilité glissante.</p>
        
        <h3>Méthodologie</h3>
        <ol>
            <li>Calcul de la volatilité glissante sur 30 jours</li>
            <li>Clustering K-Means pour identifier 3 régimes :
                <ul>
                    <li>Volatilité Basse</li>
                    <li>Volatilité Intermédiaire</li>
                    <li>Volatilité Haute</li>
                </ul>
            </li>
            <li>Attribution de chaque période à un régime</li>
        </ol>
        
        <h4>Analyse par Régime</h4>
        <p>Pour chaque régime, calcul de :</p>
        <ul>
            <li>Durée totale dans le régime</li>
            <li>Performance moyenne</li>
            <li>Volatilité moyenne</li>
            <li>Nombre de transitions</li>
        </ul>
        
        <div class="concept-card">
        <strong>💡 Utilité :</strong> Comprendre comment le fonds se comporte dans différentes 
        conditions de marché permet d'anticiper son comportement futur.
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 5: Interprétation
    st.markdown("---")
    st.markdown('<a id="interprétation-des-résultats"></a>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color: {PRIMARY_COLOR};">5️⃣ Interprétation des Résultats</h2>', unsafe_allow_html=True)
    
    with st.expander("🎯 Profil de Risque Global", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Score Global</h3>
        <p>Le score global est la moyenne des 7 dimensions du Risk Fingerprint.</p>
        
        <h4>Classification</h4>
        <ul>
            <li><strong>Score ≥ 70/100</strong> : Profil EXCELLENT
                <br>→ Fonds bien géré avec risque maîtrisé</li>
            <li><strong>Score 50-70/100</strong> : Profil SATISFAISANT
                <br>→ Équilibre acceptable risque/rendement</li>
            <li><strong>Score < 50/100</strong> : Profil À SURVEILLER
                <br>→ Risques élevés, suivi rapproché recommandé</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📊 Matrices de Corrélation", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Coefficient de Corrélation</h3>
        <div class="formula-box">
        ρ = Cov(X,Y) / (σ_X × σ_Y)
        </div>
        
        <h4>Interprétation</h4>
        <ul>
            <li><strong>ρ = 1</strong> : Corrélation parfaite positive</li>
            <li><strong>ρ = 0</strong> : Aucune corrélation</li>
            <li><strong>ρ = -1</strong> : Corrélation parfaite négative</li>
        </ul>
        
        <h4>Utilité pour la Diversification</h4>
        <p>Des corrélations faibles entre FCP permettent une meilleure diversification du portefeuille. 
        Chercher des FCP avec ρ < 0.7 pour diversifier efficacement.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("💡 Recommandations d'Allocation", expanded=False):
        st.markdown("""
        <div class="doc-section">
        <h3>Basées sur le Score Global</h3>
        
        <h4>Score ≥ 70 (Excellent)</h4>
        <p><strong>Allocation :</strong> Significative (jusqu'à 20-30% du portefeuille)</p>
        <p><strong>Profil investisseur :</strong> Tous types, y compris prudents</p>
        
        <h4>Score 50-70 (Satisfaisant)</h4>
        <p><strong>Allocation :</strong> Modérée (10-20% du portefeuille)</p>
        <p><strong>Profil investisseur :</strong> Équilibré à dynamique</p>
        <p><strong>Complément :</strong> Actifs plus défensifs ou plus dynamiques selon objectifs</p>
        
        <h4>Score < 50 (À Surveiller)</h4>
        <p><strong>Allocation :</strong> Limitée (< 10% du portefeuille)</p>
        <p><strong>Profil investisseur :</strong> Agressif avec forte tolérance au risque</p>
        <p><strong>Approche :</strong> Positionnement tactique uniquement</p>
        
        <div class="warning-box">
        <strong>⚠️ Important :</strong> Ces recommandations sont génériques. 
        L'allocation finale doit tenir compte de la situation personnelle de l'investisseur, 
        de ses objectifs et de son horizon d'investissement.
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 6: Glossaire
    st.markdown("---")
    st.markdown('<a id="glossaire"></a>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color: {PRIMARY_COLOR};">6️⃣ Glossaire</h2>', unsafe_allow_html=True)
    
    glossary_terms = {
        "FCP": "Fonds Commun de Placement - véhicule d'investissement collectif",
        "VL": "Valeur Liquidative - prix d'une part du fonds",
        "Performance": "Rendement réalisé sur une période donnée",
        "Volatilité": "Mesure de dispersion des rendements (risque)",
        "Drawdown": "Perte depuis un sommet historique",
        "Sharpe Ratio": "Rendement ajusté au risque",
        "VaR": "Value at Risk - perte potentielle maximale à un seuil de confiance",
        "CVaR": "Conditional VaR - perte moyenne au-delà du seuil VaR",
        "Skewness": "Asymétrie de la distribution des rendements",
        "Kurtosis": "Aplatissement de la distribution (épaisseur des queues)",
        "Ulcer Index": "Mesure de la douleur due aux drawdowns",
        "Pain Ratio": "Rendement par unité de douleur",
        "Upside Capture": "Participation aux hausses du marché",
        "Downside Capture": "Participation aux baisses du marché",
        "CAGR": "Compound Annual Growth Rate - taux de croissance annuel composé",
        "Corrélation": "Mesure du lien statistique entre deux variables",
        "Régime de marché": "État du marché caractérisé par un niveau de volatilité",
        "Annualisation": "Conversion d'une mesure périodique en taux annuel",
        "Base 100": "Normalisation permettant de comparer des évolutions relatives",
    }
    
    col1, col2 = st.columns(2)
    
    sorted_terms = sorted(glossary_terms.items())
    mid_point = len(sorted_terms) // 2
    
    with col1:
        for term, definition in sorted_terms[:mid_point]:
            st.markdown(f"""
            <div class="concept-card">
                <strong>{term}</strong><br>
                <small>{definition}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for term, definition in sorted_terms[mid_point:]:
            st.markdown(f"""
            <div class="concept-card">
                <strong>{term}</strong><br>
                <small>{definition}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p><strong>Application Analyse FCP - Version 2.0</strong></p>
        <p>Documentation complète des concepts et formules utilisés</p>
        <p>Pour toute question, consultez le README.md ou GUIDE_UTILISATION.md</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
