"""
Valeurs Liquidatives Analysis Page
Analyzes net asset values for FCP funds
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from scipy import stats
import os

# Constants
TRADING_DAYS_PER_YEAR = 252
DATA_FILE = os.getenv('FCP_DATA_FILE', 'data_fcp.xlsx')

# Risk Fingerprint Normalization Constants
# For skewness normalization: transforms skewness values to [0, 100] scale
# Positive skewness (right tail) maps to [50, 100], negative to [0, 50]
SKEWNESS_SCALE_FACTOR = 25  # Scaling factor for skewness transformation
SKEWNESS_NEUTRAL_SCORE = 50  # Score for zero skewness (neutral distribution)

# Color Scheme
PRIMARY_COLOR = "#114B80"    # Bleu profond — titres, boutons principaux
SECONDARY_COLOR = "#567389"  # Bleu-gris — widgets, lignes, icônes
ACCENT_COLOR = "#ACC7DF"     # Bleu clair — fonds de cartes, hover

def hex_to_rgba(hex_color, alpha=1.0):
    """
    Convert hex color to rgba string format.
    
    Args:
        hex_color (str): Hex color string (e.g., '#114B80' or '114B80')
        alpha (float): Alpha transparency value between 0.0 and 1.0
        
    Returns:
        str: RGBA color string (e.g., 'rgba(17, 75, 128, 0.3)')
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"Alpha value must be between 0.0 and 1.0, got {alpha}")
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color format: {hex_color}. Expected 6-character hex string.")
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        raise ValueError(f"Invalid hex color format: {hex_color}. Could not parse hex values.")
    return f'rgba({r}, {g}, {b}, {alpha})'

def generate_llm_style_narrative(fcp_name, risk_profile, metrics, strengths, weaknesses):
    """
    Generate an advanced, context-aware narrative analysis using LLM-style logic.
    This function analyzes multiple dimensions and creates a cohesive, professional narrative.
    
    Args:
        fcp_name (str): Name of the FCP
        risk_profile (dict): Normalized risk profile scores
        metrics (dict): Raw metrics (volatility, drawdown, sharpe, etc.)
        strengths (list): Top 3 strengths as (dimension, score) tuples
        weaknesses (list): Bottom 3 weaknesses as (dimension, score) tuples
    
    Returns:
        str: Professional narrative ready for investment committee
    """
    
    # Extract key metrics
    score_global = np.mean(list(risk_profile.values()))
    volatility = metrics.get('volatility', 0)
    max_dd = metrics.get('max_drawdown', 0)
    pain_ratio = metrics.get('pain_ratio', 0)
    skewness = metrics.get('skewness', 0)
    sharpe = metrics.get('sharpe_ratio', 0)
    ulcer = metrics.get('ulcer_index', 0)
    
    # Determine overall quality
    if score_global >= 70:
        quality = "excellent"
        quality_color = "#28a745"
    elif score_global >= 50:
        quality = "satisfaisant"
        quality_color = "#ffc107"
    else:
        quality = "préoccupant"
        quality_color = "#dc3545"
    
    # Opening paragraph - contextual introduction
    if score_global >= 70:
        opening = f"Le fonds **{fcp_name}** se distingue par un profil de risque **{quality}** (score global: {score_global:.1f}/100), reflétant une gestion rigoureuse et une maîtrise avancée des risques. "
    elif score_global >= 50:
        opening = f"Le fonds **{fcp_name}** présente un profil de risque **{quality}** (score global: {score_global:.1f}/100), caractérisé par un équilibre raisonnable entre potentiel de performance et exposition aux risques. "
    else:
        opening = f"Le fonds **{fcp_name}** affiche un profil de risque **{quality}** (score global: {score_global:.1f}/100), nécessitant une vigilance accrue et un suivi rapproché des expositions. "
    
    # Volatility analysis with context
    vol_pct = risk_profile.get('volatility', 50)
    if vol_pct >= 70:
        vol_narrative = f"La **volatilité remarquablement contenue** ({volatility:.2f}%, score: {vol_pct:.0f}/100) témoigne d'une gestion prudente et d'une construction de portefeuille bien diversifiée, offrant un confort de détention appréciable pour les investisseurs."
    elif vol_pct >= 40:
        vol_narrative = f"La **volatilité modérée** ({volatility:.2f}%, score: {vol_pct:.0f}/100) se situe dans une fourchette équilibrée, permettant de capter des opportunités de marché tout en limitant les fluctuations excessives."
    else:
        vol_narrative = f"La **volatilité élevée** ({volatility:.2f}%, score: {vol_pct:.0f}/100) reflète une exposition significative aux fluctuations de marché, requérant une tolérance au risque importante et un horizon d'investissement approprié."
    
    # Drawdown and resilience analysis
    dd_pct = risk_profile.get('max_drawdown', 50)
    if dd_pct >= 70:
        dd_narrative = f"La **résilience exceptionnelle** face aux phases adverses (drawdown max: {abs(max_dd):.2f}%, score: {dd_pct:.0f}/100) démontre une capacité remarquable à préserver le capital en période de stress, caractéristique essentielle pour la confiance des porteurs."
    elif dd_pct >= 40:
        dd_narrative = f"La **résilience modérée** (drawdown max: {abs(max_dd):.2f}%, score: {dd_pct:.0f}/100) indique que le fonds a connu des périodes de baisse significatives mais gérables, typiques d'une exposition aux actifs risqués."
    else:
        dd_narrative = f"Les **drawdowns historiques importants** (max: {abs(max_dd):.2f}%, score: {dd_pct:.0f}/100) signalent un risque de perte en capital substantiel en période adverse, nécessitant une allocation prudente et une diversification appropriée."
    
    # Pain Ratio and investor experience
    if pain_ratio > 2:
        pain_narrative = f"Le **Pain Ratio exceptionnel** ({pain_ratio:.2f}) révèle que le fonds compense largement la 'douleur' ressentie par l'investisseur lors des phases de drawdown par ses performances, un attribut hautement valorisé en gestion d'actifs."
    elif pain_ratio > 1:
        pain_narrative = f"Le **Pain Ratio positif** ({pain_ratio:.2f}) suggère un équilibre acceptable entre les rendements générés et l'inconfort psychologique des périodes de perte, caractéristique d'une gestion équilibrée."
    else:
        pain_narrative = f"Le **Pain Ratio limité** ({pain_ratio:.2f}) indique que la douleur ressentie lors des drawdowns n'est pas suffisamment compensée par la performance, un point d'attention pour la satisfaction des investisseurs."
    
    # Skewness and tail risk
    if skewness > 0.3:
        skew_narrative = f"L'**asymétrie positive marquée** (skewness: {skewness:.3f}) constitue un avantage significatif, avec un potentiel de gains extrêmes supérieur au risque de pertes catastrophiques - un profil recherché par les investisseurs avertis."
    elif abs(skewness) <= 0.3:
        skew_narrative = f"La **distribution relativement symétrique** des rendements (skewness: {skewness:.3f}) s'apparente à une loi normale, sans biais particulier vers les queues de distribution."
    else:
        skew_narrative = f"L'**asymétrie négative** (skewness: {skewness:.3f}) constitue un signal d'alerte important, révélant un risque accru de pertes extrêmes ('tail risk') qui mérite une attention particulière dans l'évaluation du risque global."
    
    # Sharpe ratio interpretation
    if sharpe > 2:
        sharpe_text = f"un ratio de Sharpe exceptionnel ({sharpe:.2f})"
    elif sharpe > 1:
        sharpe_text = f"un ratio de Sharpe satisfaisant ({sharpe:.2f})"
    elif sharpe > 0:
        sharpe_text = f"un ratio de Sharpe modeste ({sharpe:.2f})"
    else:
        sharpe_text = f"un ratio de Sharpe négatif ({sharpe:.2f}), suggérant une sous-performance par rapport au taux sans risque"
    
    # Build comprehensive analysis
    analysis_parts = [
        opening,
        "",
        "**Analyse Multidimensionnelle du Risque :**",
        "",
        f"1. **Stabilité et Volatilité** : {vol_narrative}",
        "",
        f"2. **Résilience et Drawdowns** : {dd_narrative}",
        "",
        f"3. **Expérience Investisseur** : {pain_narrative} L'Ulcer Index de {ulcer:.2f} quantifie précisément cette dimension.",
        "",
        f"4. **Profil Distributionnel** : {skew_narrative}",
        "",
        f"5. **Rendement Ajusté** : Le fonds affiche {sharpe_text}, témoignant de {'son excellente' if sharpe > 2 else 'son' if sharpe > 1 else 'une'} capacité à générer de la performance par unité de risque pris.",
        "",
    ]
    
    # Add strengths section
    if strengths:
        analysis_parts.extend([
            "**Points Forts Identifiés :**",
            ""
        ])
        for dim, score in strengths:
            if score >= 70:
                strength_desc = "excellent"
            elif score >= 60:
                strength_desc = "très bon"
            else:
                strength_desc = "bon"
            analysis_parts.append(f"- **{dim}** : Performance {strength_desc} (score: {score:.0f}/100)")
        analysis_parts.append("")
    
    # Add weaknesses section
    if weaknesses:
        analysis_parts.extend([
            "**Points d'Attention :**",
            ""
        ])
        for dim, score in weaknesses:
            if score < 30:
                weakness_desc = "nécessite une attention immédiate"
            elif score < 50:
                weakness_desc = "mériterait d'être amélioré"
            else:
                weakness_desc = "à surveiller"
            analysis_parts.append(f"- **{dim}** : {weakness_desc} (score: {score:.0f}/100)")
        analysis_parts.append("")
    
    # Allocation recommendation
    analysis_parts.append("**Recommandation d'Allocation :**")
    analysis_parts.append("")
    if score_global >= 70:
        recommendation = f"Le profil de risque favorable de **{fcp_name}** permet d'envisager une **allocation significative** (15-25% d'un portefeuille diversifié), adaptée à un large spectre d'investisseurs, y compris ceux recherchant un équilibre entre croissance et préservation du capital."
    elif score_global >= 50:
        recommendation = f"Le profil équilibré suggère une **allocation modérée** (10-15% d'un portefeuille), en complément d'actifs plus défensifs ou plus dynamiques selon les objectifs spécifiques. Convient aux investisseurs avec une tolérance au risque moyenne à élevée et un horizon moyen-long terme."
    else:
        recommendation = f"Le profil de risque élevé recommande une **allocation limitée et tactique** (< 10% d'un portefeuille), strictement réservée aux investisseurs aguerris avec une forte tolérance au risque, une capacité financière appropriée, et un horizon d'investissement long terme."
    
    analysis_parts.append(recommendation)
    
    # Final synthesis
    analysis_parts.extend([
        "",
        "**Synthèse Décisionnelle :**",
        ""
    ])
    
    if score_global >= 70:
        final_synthesis = f"**{fcp_name}** se positionne comme un véhicule d'investissement de qualité supérieure, combinant maîtrise des risques et potentiel de performance. La cohérence du profil de risque à travers les différentes dimensions analysées renforce la confiance dans la stabilité future du fonds."
    elif score_global >= 50:
        final_synthesis = f"**{fcp_name}** présente un profil de risque acceptable dans sa catégorie, avec un équilibre risque-rendement qui nécessite toutefois une surveillance active et une allocation réfléchie dans le cadre d'une stratégie de diversification appropriée."
    else:
        final_synthesis = f"**{fcp_name}** requiert une évaluation approfondie des objectifs d'investissement et de la tolérance au risque avant toute allocation. Un suivi rapproché et des revues fréquentes sont indispensables, avec une préparation aux scénarios de stress potentiels."
    
    analysis_parts.append(final_synthesis)
    
    return "\n".join(analysis_parts)

# Configuration de la page
st.set_page_config(
    page_title="Analyse FCP - Valeurs Liquidatives",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for simplified styling
st.markdown(f"""
<style>
    .ranking-card {{
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 3px;
        border: 1px solid #dee2e6;
        margin-bottom: 0.3rem;
    }}
    .ranking-card h3 {{
        color: {PRIMARY_COLOR};
        margin: 0 0 0.3rem 0;
        font-size: 1rem;
        font-weight: 600;
    }}
    .ranking-item {{
        background-color: #ffffff;
        padding: 0.3rem;
        border-radius: 2px;
        margin-bottom: 0.2rem;
        border: 1px solid #e9ecef;
    }}
    .ranking-number {{
        display: inline-block;
        background-color: {SECONDARY_COLOR};
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 3px;
        text-align: center;
        line-height: 24px;
        margin-right: 5px;
        font-weight: bold;
        font-size: 0.85rem;
    }}
    .ranking-value {{
        float: right;
        font-weight: bold;
        font-size: 0.95rem;
    }}
    .insight-box {{
        background-color: #f8f9fa;
        border-left: 2px solid {PRIMARY_COLOR};
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.3rem 0;
    }}
    .insight-box h4 {{
        color: {PRIMARY_COLOR};
        margin: 0 0 0.3rem 0;
        font-size: 0.95rem;
    }}
    .interpretation-note {{
        background-color: #ffffff;
        border-left: 2px solid {SECONDARY_COLOR};
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.3rem 0;
        border: 1px solid #e9ecef;
    }}
    .alert-box {{
        background-color: #ffebee;
        border-left: 2px solid #dc3545;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.3rem 0;
    }}
    .alert-box h4 {{
        color: #dc3545;
        margin: 0 0 0.3rem 0;
        font-size: 0.95rem;
    }}
    .alert-box p {{
        margin: 0.2rem 0;
    }}
    .alert-box ul {{
        margin: 0.2rem 0;
        padding-left: 1.2rem;
    }}
</style>
""", unsafe_allow_html=True)


def calculate_calendar_performance(df, fcp_name):
    """Calcule les performances calendaires (WTD, MTD, QTD, STD, YTD)"""
    latest_date = df['Date'].max()
    latest_value = df[df['Date'] == latest_date][fcp_name].values[0]
    
    # Week to Date
    week_start = latest_date - timedelta(days=latest_date.weekday())
    wtd_value = df[df['Date'] >= week_start][fcp_name].iloc[0] if len(df[df['Date'] >= week_start]) > 0 else latest_value
    wtd = ((latest_value / wtd_value) - 1) * 100
    
    # Month to Date
    month_start = latest_date.replace(day=1)
    mtd_value = df[df['Date'] >= month_start][fcp_name].iloc[0] if len(df[df['Date'] >= month_start]) > 0 else latest_value
    mtd = ((latest_value / mtd_value) - 1) * 100
    
    # Quarter to Date
    quarter_start = pd.Timestamp(latest_date.year, ((latest_date.month - 1) // 3) * 3 + 1, 1)
    qtd_value = df[df['Date'] >= quarter_start][fcp_name].iloc[0] if len(df[df['Date'] >= quarter_start]) > 0 else latest_value
    qtd = ((latest_value / qtd_value) - 1) * 100
    
    # Semester to Date
    semester_start = pd.Timestamp(latest_date.year, 1 if latest_date.month <= 6 else 7, 1)
    std_value = df[df['Date'] >= semester_start][fcp_name].iloc[0] if len(df[df['Date'] >= semester_start]) > 0 else latest_value
    std = ((latest_value / std_value) - 1) * 100
    
    # Year to Date
    year_start = pd.Timestamp(latest_date.year, 1, 1)
    ytd_value = df[df['Date'] >= year_start][fcp_name].iloc[0] if len(df[df['Date'] >= year_start]) > 0 else latest_value
    ytd = ((latest_value / ytd_value) - 1) * 100
    
    return {'WTD': wtd, 'MTD': mtd, 'QTD': qtd, 'STD': std, 'YTD': ytd}


def calculate_rolling_performance(df, fcp_name):
    """Calcule les performances glissantes"""
    latest_date = df['Date'].max()
    latest_value = df[df['Date'] == latest_date][fcp_name].values[0]
    
    performances = {}
    periods = {
        '1M': 30,
        '3M': 90,
        '6M': 180,
        '1Y': 365,
        '5Y': 1825
    }
    
    for label, days in periods.items():
        start_date = latest_date - timedelta(days=days)
        period_data = df[df['Date'] >= start_date]
        if len(period_data) > 0:
            start_value = period_data[fcp_name].iloc[0]
            performances[label] = ((latest_value / start_value) - 1) * 100
        else:
            performances[label] = None
    
    # Origine
    origin_value = df[fcp_name].iloc[0]
    performances['Origine'] = ((latest_value / origin_value) - 1) * 100
    
    return performances


def calculate_risk_metrics(df, fcp_name):
    """Calcule les indicateurs de risque avancés"""
    returns = df[fcp_name].pct_change().dropna() * 100
    
    # Métriques de base
    mean_return = returns.mean()
    volatility = returns.std()
    sharpe_ratio = (mean_return * TRADING_DAYS_PER_YEAR) / (volatility * np.sqrt(TRADING_DAYS_PER_YEAR)) if volatility > 0 else 0
    
    # VaR et CVaR (95%)
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    
    # Skewness et Kurtosis
    skewness = stats.skew(returns)
    kurtosis = stats.kurtosis(returns)
    
    # Maximum Drawdown
    cumulative = (1 + df[fcp_name].pct_change().fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min() * 100
    
    return {
        'Rendement Moyen (%)': mean_return,
        'Volatilité (%)': volatility,
        'Ratio de Sharpe': sharpe_ratio,
        'VaR 95% (%)': var_95,
        'CVaR 95% (%)': cvar_95,
        'Skewness': skewness,
        'Kurtosis': kurtosis,
        'Max Drawdown (%)': max_drawdown
    }


def volatility_clustering(df, fcp_name, n_clusters=3, window=30):
    """Analyse les clusters de volatilité avec rolling window"""
    # Reset index to ensure proper alignment
    df_indexed = df.reset_index(drop=True)
    returns = df_indexed[fcp_name].pct_change() * 100
    
    # Volatilité glissante
    rolling_vol = returns.rolling(window=window).std()
    
    # Préparation des données pour le clustering
    rolling_vol_clean = rolling_vol.dropna()
    X = rolling_vol_clean.values.reshape(-1, 1)
    
    # KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    
    # Dates correspondantes: align with the rolling volatility indices
    dates = df_indexed['Date'].iloc[rolling_vol_clean.index].values
    
    return dates, rolling_vol_clean.values, clusters


def analyze_volatility_regimes(df, fcp_name, window=30):
    """
    Analyse avancée des régimes de volatilité avec interprétation économique
    
    Returns:
        dict: Dictionnaire contenant toutes les analyses de régimes de volatilité
    """
    # Reset index pour alignement correct
    df_indexed = df.reset_index(drop=True)
    returns = df_indexed[fcp_name].pct_change() * 100
    
    # Calcul de la volatilité glissante
    rolling_vol = returns.rolling(window=window).std()
    rolling_vol_clean = rolling_vol.dropna()
    
    # Préparation pour clustering
    X = rolling_vol_clean.values.reshape(-1, 1)
    
    # KMeans clustering (3 régimes: faible, intermédiaire, élevé)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    
    # Récupération des centres et labélisation économique
    centers = kmeans.cluster_centers_.flatten()
    cluster_order = np.argsort(centers)
    
    # Mapping économique: 0=Faible, 1=Intermédiaire, 2=Élevé
    regime_mapping = {cluster_order[0]: 0, cluster_order[1]: 1, cluster_order[2]: 2}
    labeled_clusters = np.array([regime_mapping[c] for c in clusters])
    
    regime_names = {0: "Faible Volatilité", 1: "Volatilité Intermédiaire", 2: "Forte Volatilité"}
    
    # Dates correspondantes
    dates = df_indexed['Date'].iloc[rolling_vol_clean.index].values
    
    # Création d'un DataFrame avec tous les indices alignés
    regime_df = pd.DataFrame({
        'Date': dates,
        'Volatility': rolling_vol_clean.values,
        'Regime': labeled_clusters
    })
    
    # Ajout des rendements alignés
    aligned_returns = returns.iloc[rolling_vol_clean.index].values
    regime_df['Return'] = aligned_returns
    
    # Calcul du drawdown pour chaque point
    cumulative = (1 + df_indexed[fcp_name].pct_change().fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    aligned_drawdown = drawdown.iloc[rolling_vol_clean.index].values
    regime_df['Drawdown'] = aligned_drawdown
    
    # Statistiques par régime
    regime_stats = {}
    for regime_id in range(3):
        regime_data = regime_df[regime_df['Regime'] == regime_id]
        
        regime_stats[regime_id] = {
            'name': regime_names[regime_id],
            'count': len(regime_data),
            'proportion': len(regime_data) / len(regime_df) * 100,
            'avg_volatility': regime_data['Volatility'].mean(),
            'avg_return': regime_data['Return'].mean(),
            'max_drawdown': regime_data['Drawdown'].min(),
            'min_volatility': regime_data['Volatility'].min(),
            'max_volatility': regime_data['Volatility'].max(),
        }
    
    # Analyse des transitions entre régimes
    transitions = np.zeros((3, 3))
    for i in range(len(labeled_clusters) - 1):
        from_regime = labeled_clusters[i]
        to_regime = labeled_clusters[i + 1]
        transitions[from_regime, to_regime] += 1
    
    # Normalisation pour obtenir des probabilités
    transition_probs = transitions / transitions.sum(axis=1, keepdims=True)
    transition_probs = np.nan_to_num(transition_probs)  # Remplacer NaN par 0
    
    # Régime actuel
    current_regime = labeled_clusters[-1]
    current_regime_name = regime_names[current_regime]
    
    # Analyse de persistance (temps moyen dans chaque régime)
    regime_sequences = []
    current_seq = {'regime': labeled_clusters[0], 'length': 1}
    
    for i in range(1, len(labeled_clusters)):
        if labeled_clusters[i] == current_seq['regime']:
            current_seq['length'] += 1
        else:
            regime_sequences.append(current_seq)
            current_seq = {'regime': labeled_clusters[i], 'length': 1}
    regime_sequences.append(current_seq)
    
    # Calcul de la persistance moyenne par régime
    persistence = {}
    for regime_id in range(3):
        regime_lengths = [seq['length'] for seq in regime_sequences if seq['regime'] == regime_id]
        persistence[regime_id] = {
            'avg_duration': np.mean(regime_lengths) if regime_lengths else 0,
            'max_duration': np.max(regime_lengths) if regime_lengths else 0,
            'episodes': len(regime_lengths)
        }
    
    # Analyse risque-rendement par régime
    risk_return_analysis = {}
    for regime_id in range(3):
        regime_data = regime_df[regime_df['Regime'] == regime_id]
        if len(regime_data) > 0:
            # Returns are in percentage, convert to decimal for Sharpe ratio calculation
            mean_return_decimal = regime_data['Return'].mean() / 100
            std_return_decimal = regime_data['Return'].std() / 100
            sharpe = (mean_return_decimal * TRADING_DAYS_PER_YEAR) / \
                     (std_return_decimal * np.sqrt(TRADING_DAYS_PER_YEAR)) \
                     if std_return_decimal > 0 else 0
            
            risk_return_analysis[regime_id] = {
                'sharpe_ratio': sharpe,
                'return_volatility_ratio': regime_data['Return'].mean() / regime_data['Volatility'].mean() \
                                          if regime_data['Volatility'].mean() > 0 else 0
            }
    
    return {
        'regime_df': regime_df,
        'regime_stats': regime_stats,
        'regime_names': regime_names,
        'transitions': transitions,
        'transition_probs': transition_probs,
        'current_regime': current_regime,
        'current_regime_name': current_regime_name,
        'persistence': persistence,
        'risk_return_analysis': risk_return_analysis,
        'sorted_centers': sorted(centers)
    }


def analyze_drawdowns(df, fcp_name):
    """
    Analyse dynamique des drawdowns: profondeur, fréquence, durée et temps de récupération
    
    Returns:
        dict: Métriques de drawdown incluant profils des épisodes de stress
    """
    df_indexed = df.reset_index(drop=True)
    prices = df_indexed[fcp_name]
    
    # Calcul du drawdown série complète
    cumulative = (1 + prices.pct_change().fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    
    # Identification des épisodes de drawdown
    in_drawdown = drawdown < 0
    drawdown_episodes = []
    
    if in_drawdown.any():
        # Trouver les débuts et fins d'épisodes
        starts = in_drawdown.ne(in_drawdown.shift()).cumsum()
        for episode_id in starts[in_drawdown].unique():
            episode_mask = (starts == episode_id) & in_drawdown
            episode_data = drawdown[episode_mask]
            
            if len(episode_data) > 0:
                start_idx = episode_data.index[0]
                end_idx = episode_data.index[-1]
                
                # Trouver le temps de récupération
                recovery_idx = None
                if end_idx < len(drawdown) - 1:
                    future_dd = drawdown.iloc[end_idx+1:]
                    recovery_points = future_dd[future_dd >= -0.01]  # Récupération à <0.01% du max
                    if len(recovery_points) > 0:
                        recovery_idx = recovery_points.index[0]
                
                drawdown_episodes.append({
                    'start_date': df_indexed['Date'].iloc[start_idx],
                    'end_date': df_indexed['Date'].iloc[end_idx],
                    'start_idx': start_idx,
                    'end_idx': end_idx,
                    'recovery_idx': recovery_idx,
                    'depth': episode_data.min(),
                    'duration': len(episode_data),
                    'recovery_time': (recovery_idx - end_idx) if recovery_idx is not None else None
                })
    
    # Calcul des métriques globales
    max_dd = drawdown.min()
    avg_dd = drawdown[drawdown < 0].mean() if (drawdown < 0).any() else 0
    
    # Ulcer Index: racine carrée de la moyenne des drawdowns au carré
    ulcer_index = np.sqrt((drawdown ** 2).mean())
    
    # Pain Ratio: rendement total / Ulcer Index
    total_return = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100
    pain_ratio = total_return / ulcer_index if ulcer_index > 0 else 0
    
    return {
        'max_drawdown': max_dd,
        'avg_drawdown': avg_dd,
        'ulcer_index': ulcer_index,
        'pain_ratio': pain_ratio,
        'drawdown_series': drawdown,
        'drawdown_episodes': drawdown_episodes,
        'num_episodes': len(drawdown_episodes),
        'dates': df_indexed['Date']
    }


def calculate_rolling_risk_indicators(df, fcp_name, window=60):
    """
    Calcule les indicateurs de risque rolling pour détecter les évolutions du profil de risque
    
    Args:
        df: DataFrame avec les VL
        fcp_name: Nom du FCP
        window: Fenêtre pour le rolling (défaut 60 jours ≈ 3 mois)
    
    Returns:
        DataFrame avec les indicateurs rolling
    """
    df_indexed = df.reset_index(drop=True)
    returns = df_indexed[fcp_name].pct_change() * 100
    
    # Rolling metrics
    rolling_mean = returns.rolling(window=window).mean()
    rolling_std = returns.rolling(window=window).std()
    
    # Rolling Sharpe Ratio
    rolling_sharpe = (rolling_mean * TRADING_DAYS_PER_YEAR) / \
                     (rolling_std * np.sqrt(TRADING_DAYS_PER_YEAR))
    
    # Rolling VaR et CVaR
    rolling_var = returns.rolling(window=window).quantile(0.05)
    
    # Rolling CVaR (mean of returns below VaR)
    def calc_cvar(x):
        if len(x) < 2:
            return np.nan
        var = np.percentile(x.dropna(), 5)
        return x[x <= var].mean()
    
    rolling_cvar = returns.rolling(window=window).apply(calc_cvar, raw=False)
    
    # Construire le DataFrame de résultats
    rolling_df = pd.DataFrame({
        'Date': df_indexed['Date'],
        'Rolling_Sharpe': rolling_sharpe,
        'Rolling_VaR': rolling_var,
        'Rolling_CVaR': rolling_cvar,
        'Rolling_Volatility': rolling_std
    })
    
    return rolling_df


def calculate_loss_probabilities(df, fcp_name):
    """
    Calcule les probabilités empiriques de perte à 1, 3 et 6 mois
    
    Returns:
        dict: Probabilités de perte à différents horizons
    """
    df_indexed = df.reset_index(drop=True)
    prices = df_indexed[fcp_name]
    
    horizons = {
        '1M': 21,   # ~1 mois
        '3M': 63,   # ~3 mois
        '6M': 126   # ~6 mois
    }
    
    loss_probs = {}
    
    for label, days in horizons.items():
        returns_horizon = []
        
        # Calculer les rendements à l'horizon donné
        for i in range(len(prices) - days):
            ret = ((prices.iloc[i + days] / prices.iloc[i]) - 1) * 100
            returns_horizon.append(ret)
        
        if len(returns_horizon) > 0:
            returns_arr = np.array(returns_horizon)
            loss_prob = (returns_arr < 0).sum() / len(returns_arr) * 100
            avg_loss = returns_arr[returns_arr < 0].mean() if (returns_arr < 0).any() else 0
            avg_gain = returns_arr[returns_arr > 0].mean() if (returns_arr > 0).any() else 0
            
            loss_probs[label] = {
                'probability': loss_prob,
                'avg_loss': avg_loss,
                'avg_gain': avg_gain,
                'gain_loss_ratio': abs(avg_gain / avg_loss) if avg_loss < 0 else 0
            }
        else:
            loss_probs[label] = {
                'probability': 0,
                'avg_loss': 0,
                'avg_gain': 0,
                'gain_loss_ratio': 0
            }
    
    return loss_probs


def calculate_capture_ratios(df, fcp_name, benchmark_name=None):
    """
    Calcule les ratios de capture haussière et baissière
    Si pas de benchmark, utilise la moyenne de tous les FCP
    
    Returns:
        dict: Ratios de capture up/down
    """
    df_indexed = df.reset_index(drop=True)
    fcp_returns = df_indexed[fcp_name].pct_change().dropna() * 100
    
    # Si pas de benchmark, utiliser la moyenne des autres FCP
    if benchmark_name is None or benchmark_name not in df_indexed.columns:
        fcp_cols = [col for col in df_indexed.columns if col.startswith('FCP') and col != fcp_name]
        if len(fcp_cols) > 0:
            benchmark_returns = df_indexed[fcp_cols].pct_change().mean(axis=1).dropna() * 100
        else:
            return {'upside_capture': 0, 'downside_capture': 0}
    else:
        benchmark_returns = df_indexed[benchmark_name].pct_change().dropna() * 100
    
    # Aligner les séries
    min_len = min(len(fcp_returns), len(benchmark_returns))
    fcp_returns = fcp_returns.iloc[:min_len]
    benchmark_returns = benchmark_returns.iloc[:min_len]
    
    # Périodes haussières et baissières du benchmark
    up_periods = benchmark_returns > 0
    down_periods = benchmark_returns < 0
    
    # Capture ratios
    if up_periods.any():
        upside_capture = (fcp_returns[up_periods].mean() / benchmark_returns[up_periods].mean()) * 100
    else:
        upside_capture = 0
    
    if down_periods.any():
        downside_capture = (fcp_returns[down_periods].mean() / benchmark_returns[down_periods].mean()) * 100
    else:
        downside_capture = 0
    
    return {
        'upside_capture': upside_capture,
        'downside_capture': downside_capture
    }


def calculate_risk_fingerprint(df, fcp_name):
    """
    Construit une signature synthétique du risque normalisée et comparable
    
    Returns:
        dict: Métriques normalisées pour le profil de risque
    """
    # Calcul des métriques de base
    returns = df[fcp_name].pct_change().dropna() * 100
    volatility = returns.std()
    
    # Drawdown analysis
    dd_analysis = analyze_drawdowns(df, fcp_name)
    
    # Rolling indicators pour la stabilité du Sharpe
    rolling_risk = calculate_rolling_risk_indicators(df, fcp_name, window=60)
    sharpe_stability = rolling_risk['Rolling_Sharpe'].std()
    
    # CVaR pour le risque extrême
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    
    # Asymétrie
    skewness = stats.skew(returns)
    
    # Temps de récupération moyen
    episodes_with_recovery = [ep for ep in dd_analysis['drawdown_episodes'] 
                             if ep['recovery_time'] is not None]
    avg_recovery_time = np.mean([ep['recovery_time'] for ep in episodes_with_recovery]) \
                       if episodes_with_recovery else 0
    
    return {
        'volatility': volatility,
        'max_drawdown': abs(dd_analysis['max_drawdown']),
        'avg_drawdown': abs(dd_analysis['avg_drawdown']),
        'avg_recovery_time': avg_recovery_time,
        'cvar_95': abs(cvar_95),
        'skewness': skewness,
        'sharpe_stability': sharpe_stability,
        'ulcer_index': dd_analysis['ulcer_index'],
        'pain_ratio': dd_analysis['pain_ratio']
    }


def normalize_risk_fingerprint(fingerprints_dict):
    """
    Normalise les fingerprints pour comparaison entre FCP
    
    Args:
        fingerprints_dict: Dict avec {fcp_name: fingerprint}
    
    Returns:
        dict: Fingerprints normalisés [0-100]
    """
    if not fingerprints_dict:
        return {}
    
    # Extraire toutes les valeurs par métrique
    metrics = list(next(iter(fingerprints_dict.values())).keys())
    
    normalized = {}
    
    for fcp_name, fingerprint in fingerprints_dict.items():
        normalized[fcp_name] = {}
        
        for metric in metrics:
            values = [fp[metric] for fp in fingerprints_dict.values()]
            min_val = min(values)
            max_val = max(values)
            
            # Normalisation [0-100]
            if max_val > min_val:
                norm_value = ((fingerprint[metric] - min_val) / (max_val - min_val)) * 100
            else:
                norm_value = 50  # Valeur médiane si tous égaux
            
            # Inverser pour les métriques "moins c'est mieux"
            if metric in ['volatility', 'max_drawdown', 'avg_drawdown', 'avg_recovery_time', 
                         'cvar_95', 'sharpe_stability', 'ulcer_index']:
                norm_value = 100 - norm_value
            
            # Ajuster skewness (positif = bien, négatif = mauvais)
            if metric == 'skewness':
                # Convertir de [-inf, +inf] vers [0, 100]
                # Skewness positif (queues à droite) = mieux
                if fingerprint[metric] >= 0:
                    norm_value = 50 + min(fingerprint[metric] * 10, 50)
                else:
                    norm_value = 50 + max(fingerprint[metric] * 10, -50)
            
            normalized[fcp_name][metric] = norm_value
    
    return normalized


def calculate_7d_risk_profile(df, fcp_name):
    """
    Calcule le profil de risque sur 7 dimensions pour le Risk Fingerprint.
    
    Les 7 dimensions sont:
    a. Stabilité: Inverse de la volatilité (plus haut = plus stable)
    b. Résilience: Inverse du max drawdown (plus haut = plus résilient)
    c. Récupération: Inverse du temps de récupération moyen
    d. Protection Extrême: Inverse de la CVaR (plus haut = mieux protégé)
    e. Asymétrie: Skewness normalisée (plus haut = meilleure asymétrie)
    f. Sharpe Stable: Stabilité du ratio de Sharpe dans le temps
    g. Pain Ratio: Rendement ajusté à la douleur
    
    Args:
        df: DataFrame avec les valeurs liquidatives
        fcp_name: Nom du FCP
    
    Returns:
        dict: Les 7 dimensions avec leurs valeurs brutes
    """
    # Calcul des métriques de base
    returns = df[fcp_name].pct_change().dropna() * 100
    
    # 1. Stabilité (inverse de la volatilité)
    volatility = returns.std()
    stabilite = volatility  # Sera inversé lors de la normalisation
    
    # 2. Résilience (inverse du max drawdown)
    dd_analysis = analyze_drawdowns(df, fcp_name)
    resilience = abs(dd_analysis['max_drawdown'])  # Sera inversé lors de la normalisation
    
    # 3. Récupération (inverse du temps de récupération moyen)
    episodes_with_recovery = [ep for ep in dd_analysis['drawdown_episodes'] 
                             if ep['recovery_time'] is not None]
    # Use minimum meaningful recovery time (1 day) if no recovery episodes exist
    # This prevents division by zero and represents "instant recovery" scenario
    avg_recovery_time = np.mean([ep['recovery_time'] for ep in episodes_with_recovery]) \
                       if episodes_with_recovery else 1
    recuperation = avg_recovery_time  # Sera inversé lors de la normalisation
    
    # 4. Protection Extrême (inverse de la CVaR)
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    protection_extreme = abs(cvar_95)  # Sera inversé lors de la normalisation
    
    # 5. Asymétrie (skewness normalisée)
    skewness = stats.skew(returns)
    asymetrie = skewness  # Sera traité spécialement lors de la normalisation
    
    # 6. Sharpe Stable (stabilité du ratio de Sharpe)
    rolling_risk = calculate_rolling_risk_indicators(df, fcp_name, window=60)
    sharpe_stability = rolling_risk['Rolling_Sharpe'].std()
    sharpe_stable = sharpe_stability  # Sera inversé lors de la normalisation
    
    # 7. Pain Ratio (rendement ajusté à la douleur)
    pain_ratio = dd_analysis['pain_ratio']
    
    return {
        'Stabilité': stabilite,
        'Résilience': resilience,
        'Récupération': recuperation,
        'Protection Extrême': protection_extreme,
        'Asymétrie': asymetrie,
        'Sharpe Stable': sharpe_stable,
        'Pain Ratio': pain_ratio
    }


def normalize_7d_risk_profile(profiles_dict):
    """
    Normalise les profils de risque 7D pour comparaison entre FCP.
    Score normalisé = (Valeur - Min) / (Max - Min) × 100
    
    Args:
        profiles_dict: Dict avec {fcp_name: profile_7d}
    
    Returns:
        dict: Profils normalisés [0-100]
    """
    if not profiles_dict:
        return {}
    
    # Dimensions à inverser (moins c'est mieux)
    inverse_dimensions = ['Stabilité', 'Résilience', 'Récupération', 'Protection Extrême', 'Sharpe Stable']
    
    normalized = {}
    
    for fcp_name, profile in profiles_dict.items():
        normalized[fcp_name] = {}
        
        for dimension, value in profile.items():
            # Collecter toutes les valeurs pour cette dimension
            all_values = [p[dimension] for p in profiles_dict.values()]
            min_val = min(all_values)
            max_val = max(all_values)
            
            # Normalisation [0-100]
            if max_val > min_val:
                norm_value = ((value - min_val) / (max_val - min_val)) * 100
            else:
                norm_value = 50  # Valeur médiane si tous égaux
            
            # Inverser pour les dimensions "moins c'est mieux"
            if dimension in inverse_dimensions:
                norm_value = 100 - norm_value
            
            # Traitement spécial pour l'asymétrie (skewness)
            if dimension == 'Asymétrie':
                # Convertir de [-inf, +inf] vers [0, 100]
                # Skewness positif (queues à droite) = mieux, maps to [50, 100]
                # Skewness négatif (queues à gauche) = moins bien, maps to [0, 50]
                # Utilise SKEWNESS_SCALE_FACTOR pour la transformation linéaire
                if value >= 0:
                    norm_value = SKEWNESS_NEUTRAL_SCORE + min(value * SKEWNESS_SCALE_FACTOR, SKEWNESS_NEUTRAL_SCORE)
                else:
                    norm_value = SKEWNESS_NEUTRAL_SCORE + max(value * SKEWNESS_SCALE_FACTOR, -SKEWNESS_NEUTRAL_SCORE)
            
            normalized[fcp_name][dimension] = norm_value
    
    return normalized


def create_risk_fingerprint_chart(normalized_profile, fcp_name):
    """
    Crée un radar chart (spider chart) pour le Risk Fingerprint.
    
    Args:
        normalized_profile: Dict avec les 7 dimensions normalisées [0-100]
        fcp_name: Nom du FCP
    
    Returns:
        plotly.graph_objects.Figure: Le radar chart
    """
    dimensions = list(normalized_profile.keys())
    values = list(normalized_profile.values())
    
    # Fermer le radar chart en ajoutant la première valeur à la fin
    dimensions_closed = dimensions + [dimensions[0]]
    values_closed = values + [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=dimensions_closed,
        fill='toself',
        fillcolor=hex_to_rgba(PRIMARY_COLOR, 0.3),
        line=dict(color=PRIMARY_COLOR, width=2),
        name=fcp_name,
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                showticklabels=True,
                ticks='outside'
            ),
            angularaxis=dict(
                direction='clockwise'
            )
        ),
        showlegend=True,
        title=f"Risk Fingerprint - {fcp_name}",
        height=500,
        template="plotly_white"
    )
    
    return fig


@st.cache_data
def load_data():
    """Charge les données du fichier Excel"""
    df = pd.read_excel(DATA_FILE, sheet_name='Valeurs Liquidatives')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    return df


def main():
    """Main function for the Valeurs Liquidatives page"""
    st.header("📈 Analyse des Valeurs Liquidatives")
    
    # Load data
    with st.spinner('Chargement des données...'):
        df = load_data()
    
    # Obtenir la liste des FCP
    fcp_cols = [col for col in df.columns if col != 'Date']
    
    # Sidebar pour les filtres
    with st.sidebar:
        st.header("🔧 Filtres et Paramètres")
        
        # Sélection du/des FCP
        st.markdown("### 📊 Sélection des FCP")
        
        # Initialize session state for selected FCPs if not exists
        # Default to empty list (which will select all FCPs)
        if 'vl_selected_fcps' not in st.session_state:
            st.session_state.vl_selected_fcps = []

        selected_fcps = st.multiselect(
            "FCP à analyser",
            options=fcp_cols,
            default=st.session_state.vl_selected_fcps,
            key="vl_multiselect",
            help="Sélectionnez un ou plusieurs FCP. Si aucun FCP n'est sélectionné, tous les FCP seront analysés."
        )

        
        # Update session state
        st.session_state.vl_selected_fcps = selected_fcps
        
        # If no FCP is selected, use all FCPs
        if not selected_fcps:
            selected_fcps = fcp_cols
            st.info(f"📌 **Tous les FCP sélectionnés ({len(fcp_cols)} FCP)**")
        else:
            st.info(f"📌 **{len(selected_fcps)}/{len(fcp_cols)}** FCP sélectionnés")
        
        # Filtre de date avec options rapides
        with st.expander("📅 Période d'analyse", expanded=True):
            quick_filter = st.radio(
                "Filtres rapides",
                options=['Personnalisé', 'WTD', 'MTD', 'QTD', 'YTD', 'Origine'],
                index=5,
                help="WTD: Semaine, MTD: Mois, QTD: Trimestre, YTD: Année, Origine: Depuis le début",
                horizontal=True
            )
            
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            
            if quick_filter == 'WTD':
                date_range = (max_date - timedelta(days=max_date.weekday()), max_date)
            elif quick_filter == 'MTD':
                date_range = (max_date.replace(day=1), max_date)
            elif quick_filter == 'QTD':
                quarter_start_month = ((max_date.month - 1) // 3) * 3 + 1
                date_range = (max_date.replace(month=quarter_start_month, day=1), max_date)
            elif quick_filter == 'YTD':
                date_range = (max_date.replace(month=1, day=1), max_date)
            elif quick_filter == 'Origine':
                date_range = (min_date, max_date)
            else:
                date_range = st.date_input(
                    "Sélectionnez la période",
                    value=(df['Date'].min(), df['Date'].max()),
                    min_value=df['Date'].min(),
                    max_value=df['Date'].max(),
                    key="valeurs_liquidatives_date_range"
                )
            
            # Display selected date range
            if isinstance(date_range, tuple) and len(date_range) == 2:
                try:
                    st.caption(f"📅 Du {date_range[0].strftime('%d/%m/%Y')} au {date_range[1].strftime('%d/%m/%Y')}")
                except (AttributeError, TypeError):
                    pass
        

        
        # Save/Load selections
        with st.expander("💾 Sauvegarder/Charger la Sélection", expanded=False):
            # Save current selection
            selection_name = st.text_input("Nom de la sélection", key="vl_save_name")
            if st.button("💾 Sauvegarder la sélection actuelle", use_container_width=True):
                if selection_name:
                    if 'vl_saved_selections' not in st.session_state:
                        st.session_state.vl_saved_selections = {}
                    # Save the actual selected FCPs from session state (before conversion to all FCPs)
                    st.session_state.vl_saved_selections[selection_name] = st.session_state.vl_selected_fcps.copy()
                    st.success(f"✅ Sélection '{selection_name}' sauvegardée!")
                else:
                    st.warning("⚠️ Veuillez entrer un nom pour la sélection")
            
            # Load saved selection
            if 'vl_saved_selections' in st.session_state and st.session_state.vl_saved_selections:
                saved_names = list(st.session_state.vl_saved_selections.keys())
                selected_save = st.selectbox("Charger une sélection", options=[""] + saved_names)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📂 Charger", use_container_width=True) and selected_save:
                        st.session_state.vl_selected_fcps = st.session_state.vl_saved_selections[selected_save]
                        st.rerun()
                with col2:
                    if st.button("🗑️ Supprimer", use_container_width=True) and selected_save:
                        del st.session_state.vl_saved_selections[selected_save]
                        st.rerun()
            else:
                st.info("Aucune sélection sauvegardée")
        
        # Bouton de réinitialisation
        if st.button("🔄 Réinitialiser tous les filtres", use_container_width=True):
            st.session_state.vl_selected_fcps = []
            st.rerun()
    
    # Note: removed the check "if not selected_fcps" since empty selection now means "all FCPs"
    
    # Filtrage des données par date (used for some analyses but not for performances)
    if len(date_range) == 2:
        mask = (df['Date'] >= pd.Timestamp(date_range[0])) & (df['Date'] <= pd.Timestamp(date_range[1]))
        filtered_df = df[mask].copy()
    else:
        filtered_df = df.copy()
    
    # Use full data for performance calculations
    full_df = df.copy()
    
    # ===================
    # Section 0: Comparative Summary - Selected vs All FCPs
    # ===================
    st.markdown("### 📊 Vue d'Ensemble Comparative")
    
    # Calculate stats for all FCPs
    all_fcp_stats = {}
    for fcp in fcp_cols:
        all_fcp_stats[fcp] = {
            'current': filtered_df[fcp].iloc[-1],
            'initial': filtered_df[fcp].iloc[0],
            'performance': ((filtered_df[fcp].iloc[-1] / filtered_df[fcp].iloc[0]) - 1) * 100,
            'volatility': (filtered_df[fcp].pct_change().dropna() * 100).std()
        }
    

    # Positioning chart - where selected FCPs rank among all
    st.markdown("#### 📍 Positionnement des FCP Sélectionnés")
    
    # Create ranking dataframe
    ranking_df = pd.DataFrame([
        {
            'FCP': fcp,
            'Performance (%)': all_fcp_stats[fcp]['performance'],
            'Volatilité (%)': all_fcp_stats[fcp]['volatility'],
            'Sélectionné': 'Oui' if fcp in selected_fcps else 'Non'
        }
        for fcp in fcp_cols
    ]).sort_values('Performance (%)', ascending=False)
    
    # Add rank
    ranking_df['Rang'] = range(1, len(ranking_df) + 1)
    
    # Create scatter plot showing performance vs volatility
    fig_positioning = go.Figure()
    
    # Plot all FCPs
    for _, row in ranking_df.iterrows():
        is_selected = row['Sélectionné'] == 'Oui'
        fig_positioning.add_trace(go.Scatter(
            x=[row['Volatilité (%)']],
            y=[row['Performance (%)']],
            mode='markers+text',
            name=row['FCP'],
            text=row['FCP'],
            textposition='top center',
            marker=dict(
                size=15 if is_selected else 8,
                color=PRIMARY_COLOR if is_selected else SECONDARY_COLOR,
                opacity=1.0 if is_selected else 0.4,
                line=dict(width=2 if is_selected else 0, color='white')
            ),
            textfont=dict(
                size=10 if is_selected else 8,
                color=PRIMARY_COLOR if is_selected else SECONDARY_COLOR
            ),
            showlegend=False,
            hovertemplate='<b>%{text}</b><br>' +
                         'Performance: %{y:.2f}%<br>' +
                         'Volatilité: %{x:.2f}%<br>' +
                         '<extra></extra>'
        ))
    
    # Add quadrant lines (median)
    median_perf = ranking_df['Performance (%)'].median()
    median_vol = ranking_df['Volatilité (%)'].median()
    
    fig_positioning.add_hline(y=median_perf, line_dash="dash", line_color="gray", opacity=0.3)
    fig_positioning.add_vline(x=median_vol, line_dash="dash", line_color="gray", opacity=0.3)
    
    fig_positioning.update_layout(
        title="Performance vs Volatilité - FCP Sélectionnés en surbrillance",
        xaxis_title="Volatilité (%)",
        yaxis_title="Performance (%)",
        height=500,
        template="plotly_white",
        hovermode='closest'
    )
    
    st.plotly_chart(fig_positioning, use_container_width=True)
    
    # Show ranking table for selected FCPs (without Rang column)
    selected_ranking = ranking_df[ranking_df['Sélectionné'] == 'Oui'][['FCP', 'Performance (%)', 'Volatilité (%)']].reset_index(drop=True)
    
    st.markdown("#### 📋 Classement des FCP Sélectionnés")
    
    st.dataframe(
        selected_ranking.style.background_gradient(subset=['Performance (%)'], cmap='RdYlGn')
                          .background_gradient(subset=['Volatilité (%)'], cmap='RdYlGn_r')
                          .format({'Performance (%)': '{:+.2f}%', 'Volatilité (%)': '{:.2f}%'}),
        use_container_width=True,
        hide_index=True
    )
    
    # Add brief comment based on results
    best_fcp = selected_ranking.loc[selected_ranking['Performance (%)'].idxmax()]
    worst_fcp = selected_ranking.loc[selected_ranking['Performance (%)'].idxmin()]
    avg_perf = selected_ranking['Performance (%)'].mean()
    
    st.markdown(f"""
**💬 Commentaire:** Parmi les {len(selected_ranking)} FCP sélectionnés, **{best_fcp['FCP']}** affiche la meilleure 
performance avec **{best_fcp['Performance (%)']:+.2f}%**, tandis que **{worst_fcp['FCP']}** présente la performance 
la plus faible à **{worst_fcp['Performance (%)']:+.2f}%**. La performance moyenne du groupe s'établit à **{avg_perf:+.2f}%**.
""")
    
    st.markdown("---")
    
    # ===================
    # Section 2: Performance Analyses with Tabs
    # ===================
    st.subheader("📈 Analyses de Performance")
    
    tab1, tab2 = st.tabs(["📅 Performances Calendaires", "📊 Performances Glissantes"])
    
    with tab1:
        st.markdown("""
        <div class="interpretation-note">
            <strong>💡 Interprétation:</strong> Les performances calendaires mesurent les rendements sur différentes périodes fixes 
            (semaine, mois, trimestre, année en cours). Ces métriques permettent de comparer la performance récente des FCP.
        </div>
        """, unsafe_allow_html=True)
        
        calendar_data = []
        for fcp in selected_fcps:
            perf = calculate_calendar_performance(full_df, fcp)
            perf['FCP'] = fcp
            calendar_data.append(perf)
        
        calendar_df = pd.DataFrame(calendar_data)
        calendar_df = calendar_df.set_index('FCP')
        
        # Display as table with formatting
        st.markdown("##### 📊 Tableau des Performances Calendaires")
        st.dataframe(
            calendar_df.style.background_gradient(cmap='RdYlGn', axis=None)
                            .format("{:+.2f}%"),
            use_container_width=True
        )
    
    with tab2:
        st.markdown("""
        <div class="interpretation-note">
            <strong>💡 Interprétation:</strong> Les performances glissantes mesurent les rendements sur des périodes mobiles 
            (1 mois, 3 mois, 6 mois, 1 an, 5 ans). Elles permettent d'évaluer la constance des performances dans le temps.
        </div>
        """, unsafe_allow_html=True)
        
        rolling_data = []
        for fcp in selected_fcps:
            perf = calculate_rolling_performance(full_df, fcp)
            perf['FCP'] = fcp
            rolling_data.append(perf)
        
        rolling_df = pd.DataFrame(rolling_data)
        rolling_df = rolling_df.set_index('FCP')
        
        # Display as table with formatting
        st.markdown("##### 📊 Tableau des Performances Glissantes")
        st.dataframe(
            rolling_df.style.background_gradient(cmap='RdYlGn', axis=None)
                           .format(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A"),
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Section 3: Évolution des valeurs liquidatives
    st.subheader("📈 Évolution des Valeurs Liquidatives dans le Temps")
    
    st.markdown("""
    <div class="interpretation-note">
        <strong>💡 Note:</strong> Ce graphique utilise toutes les données disponibles, indépendamment du filtre de période sélectionné dans la barre latérale.
        Vous pouvez choisir la période et le mode de visualisation ci-dessous.
    </div>
    """, unsafe_allow_html=True)
    
    # Period selection for VL graph
    col1, col2 = st.columns([3, 1])
    
    with col1:
        vl_period = st.radio(
            "Sélectionnez la période d'affichage",
            options=['1M', '3M', '6M', '1A', 'Tout'],
            index=4,
            horizontal=True,
            help="Choisissez la période à visualiser"
        )
    
    with col2:
        vl_mode = st.radio(
            "Mode",
            options=['Absolue', 'Cumulé (%)'],
            index=0,
            help="Absolue: valeurs liquidatives réelles | Cumulé: performance en % depuis le début de la période"
        )
    
    # Filter data based on period selection
    max_date = full_df['Date'].max()
    
    if vl_period == '1M':
        start_date = max_date - timedelta(days=30)
    elif vl_period == '3M':
        start_date = max_date - timedelta(days=90)
    elif vl_period == '6M':
        start_date = max_date - timedelta(days=180)
    elif vl_period == '1A':
        start_date = max_date - timedelta(days=365)
    else:  # 'Tout'
        start_date = full_df['Date'].min()
    
    vl_plot_df = full_df[full_df['Date'] >= start_date].copy()
    
    # Prepare data based on mode
    if vl_mode == 'Cumulé (%)':
        for fcp in selected_fcps:
            vl_plot_df[fcp] = ((vl_plot_df[fcp] / vl_plot_df[fcp].iloc[0]) - 1) * 100
    
    # Create the evolution chart
    fig_evolution = go.Figure()
    
    for fcp in selected_fcps:
        fig_evolution.add_trace(go.Scatter(
            x=vl_plot_df['Date'],
            y=vl_plot_df[fcp],
            mode='lines',
            name=fcp,
            line=dict(width=2),
            hovertemplate='<b>%{data.name}</b><br>Date: %{x}<br>Valeur: %{y:.2f}<extra></extra>'
        ))
    
    y_title = "Performance Cumulée (%)" if vl_mode == 'Cumulé (%)' else "Valeur Liquidative"
    title_text = f"Évolution des Valeurs Liquidatives - {vl_period} - {vl_mode}"
    
    fig_evolution.update_layout(
        title=title_text,
        xaxis_title="Date",
        yaxis_title=y_title,
        height=600,
        template="plotly_white",
        hovermode='x unified',
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    st.markdown("---")
    
    # ===================
    # Section 4: Advanced Analyses with Tabs
    # ===================
    st.subheader("📊 Analyses Avancées")
    
    tab1, tab2, tab3 = st.tabs(["📈 Distributions, Stats & Corrélations", "⚠️ Risque", "🎯 Volatilité"])
    
    with tab1:
        st.markdown("""
        <div class="interpretation-note">
            <strong>💡 Note de Synthèse:</strong> L'analyse des distributions permet de comprendre le comportement statistique 
            des rendements. Une distribution normale (Skewness proche de 0, Kurtosis proche de 0) indique des variations régulières,
            tandis que des valeurs extrêmes suggèrent des comportements atypiques.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogramme des rendements
            fig_hist = go.Figure()
            
            for fcp in selected_fcps:
                returns = filtered_df[fcp].pct_change().dropna() * 100
                fig_hist.add_trace(go.Histogram(
                    x=returns,
                    name=fcp,
                    opacity=0.7,
                    nbinsx=50
                ))
            
            fig_hist.update_layout(
                title="Distribution des Rendements Quotidiens",
                xaxis_title="Rendement (%)",
                yaxis_title="Fréquence",
                barmode='overlay',
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot des rendements
            fig_box = go.Figure()
            
            for fcp in selected_fcps:
                returns = filtered_df[fcp].pct_change().dropna() * 100
                fig_box.add_trace(go.Box(
                    y=returns,
                    name=fcp,
                    boxmean='sd'
                ))
            
            fig_box.update_layout(
                title="Box Plot des Rendements Quotidiens",
                yaxis_title="Rendement (%)",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Statistiques descriptives
        st.markdown("##### Statistiques Descriptives Détaillées")
        
        stats_data = []
        for fcp in selected_fcps:
            returns = filtered_df[fcp].pct_change().dropna() * 100
            stats_dict = {
                'FCP': fcp,
                'Rendement Moyen (%)': returns.mean(),
                'Médiane (%)': returns.median(),
                'Écart-type (%)': returns.std(),
                'Min (%)': returns.min(),
                'Max (%)': returns.max(),
                'Skewness': stats.skew(returns),
                'Kurtosis': stats.kurtosis(returns)
            }
            stats_data.append(stats_dict)
        
        stats_df = pd.DataFrame(stats_data)
        stats_df = stats_df.set_index('FCP')
        
        # Formatage des nombres
        styled_stats = stats_df.style.format("{:.3f}")
        st.dataframe(styled_stats, use_container_width=True)
        
        # Quartile analysis
        st.markdown("##### Analyse par Quartiles")
        
        quartile_data = []
        for fcp in selected_fcps:
            returns = filtered_df[fcp].pct_change().dropna() * 100
            q1 = returns.quantile(0.25)
            q2 = returns.quantile(0.50)  # Median
            q3 = returns.quantile(0.75)
            quartile_data.append({
                'FCP': fcp,
                'Q1 (25%)': f"{q1:.3f}%",
                'Médiane (Q2)': f"{q2:.3f}%",
                'Q3 (75%)': f"{q3:.3f}%",
                'IQR': f"{(q3-q1):.3f}%"
            })
        
        df_quartiles = pd.DataFrame(quartile_data)
        st.dataframe(df_quartiles, use_container_width=True, hide_index=True)
        
        st.markdown("""
        <div class="interpretation-note">
        <strong>💡 Interprétation:</strong> L'écart interquartile (IQR) mesure la dispersion centrale des rendements.
        Un IQR faible indique des rendements plus concentrés et donc plus prévisibles.
        </div>
        """, unsafe_allow_html=True)
        
        # ========================================
        # ANALYSE DES CORRÉLATIONS
        # ========================================
        st.markdown("---")
        st.markdown("### 🔗 Analyse des Corrélations")
        
        st.markdown("""
        <div class="interpretation-note">
            <strong>💡 Note:</strong> L'analyse des corrélations entre les valeurs liquidatives des différents FCP 
            permet d'identifier les interdépendances et opportunités de diversification. Une faible corrélation entre deux FCP 
            indique qu'ils évoluent de manière relativement indépendante.
        </div>
        """, unsafe_allow_html=True)
        
        if len(selected_fcps) > 1:
            # Calculate correlation matrix
            correlation_matrix = filtered_df[selected_fcps].corr()
            
            # Heatmap
            fig_corr = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlation_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Corrélation")
            ))
            
            fig_corr.update_layout(
                title="Matrice de Corrélation des Valeurs Liquidatives",
                height=max(400, len(correlation_matrix) * 30),
                template="plotly_white"
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Find most and least correlated pairs
            corr_pairs = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_pairs.append({
                        'FCP 1': correlation_matrix.columns[i],
                        'FCP 2': correlation_matrix.columns[j],
                        'Corrélation': correlation_matrix.iloc[i, j]
                    })
            
            df_corr_pairs = pd.DataFrame(corr_pairs).sort_values('Corrélation', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🔗 Paires Les Plus Corrélées")
                top_corr = df_corr_pairs.head(5)
                top_corr['Corrélation'] = top_corr['Corrélation'].round(3)
                st.dataframe(top_corr, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("##### 🔀 Paires Les Moins Corrélées")
                bottom_corr = df_corr_pairs.tail(5).sort_values('Corrélation')
                bottom_corr['Corrélation'] = bottom_corr['Corrélation'].round(3)
                st.dataframe(bottom_corr, use_container_width=True, hide_index=True)
            
            # Interpretation
            st.markdown("""
            <div class="interpretation-note">
            <strong>💡 Interprétation:</strong><br>
            • <strong>Corrélation proche de 1:</strong> Les VL évoluent de manière très similaire - faible diversification<br>
            • <strong>Corrélation proche de 0:</strong> Pas de relation linéaire - bonne opportunité de diversification<br>
            • <strong>Corrélation négative:</strong> Les VL évoluent de manière opposée - excellente diversification
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sélectionnez au moins 2 FCP pour voir l'analyse de corrélation.")
    
    with tab2:
        st.markdown("""
        <div class="interpretation-note">
            <strong>💡 Note de Synthèse:</strong> Les indicateurs de risque mesurent différents aspects de la volatilité 
            et des pertes potentielles. Le Ratio de Sharpe évalue le rendement ajusté au risque, tandis que VaR et CVaR 
            quantifient les pertes extrêmes possibles.
        </div>
        """, unsafe_allow_html=True)
        
        risk_data = []
        for fcp in selected_fcps:
            risk_metrics = calculate_risk_metrics(filtered_df, fcp)
            risk_metrics['FCP'] = fcp
            risk_data.append(risk_metrics)
        
        risk_df = pd.DataFrame(risk_data)
        risk_df = risk_df.set_index('FCP')
        
        # Formatage et affichage
        styled_risk = risk_df.style.format("{:.3f}")
        st.dataframe(styled_risk, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Sharpe Ratio comparison
            fig_sharpe = go.Figure()
            fig_sharpe.add_trace(go.Bar(
                x=risk_df.index,
                y=risk_df['Ratio de Sharpe'],
                marker_color='#114B80',
                text=risk_df['Ratio de Sharpe'].round(3).astype(str),
                textposition='outside'
            ))
            
            fig_sharpe.update_layout(
                title="Ratio de Sharpe par FCP",
                xaxis_title="FCP",
                yaxis_title="Ratio de Sharpe",
                height=350,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_sharpe, use_container_width=True)
        
        with col2:
            # Max Drawdown comparison
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Bar(
                x=risk_df.index,
                y=risk_df['Max Drawdown (%)'],
                marker_color='#567389',
                text=risk_df['Max Drawdown (%)'].round(2).astype(str) + '%',
                textposition='outside'
            ))
            
            fig_dd.update_layout(
                title="Drawdown Maximum par FCP",
                xaxis_title="FCP",
                yaxis_title="Max Drawdown (%)",
                height=350,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_dd, use_container_width=True)
        
        # Key insights
        best_sharpe_fcp = risk_df['Ratio de Sharpe'].idxmax()
        worst_dd_fcp = risk_df['Max Drawdown (%)'].idxmin()
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>🎯 Points Clés</h4>
            <p>• <strong>Meilleur Ratio de Sharpe:</strong> {best_sharpe_fcp} ({risk_df.loc[best_sharpe_fcp, 'Ratio de Sharpe']:.3f})</p>
            <p>• <strong>Drawdown le plus faible:</strong> {worst_dd_fcp} ({risk_df.loc[worst_dd_fcp, 'Max Drawdown (%)']:.2f}%)</p>
            <p>• <strong>VaR moyen 95%:</strong> {risk_df['VaR 95% (%)'].mean():.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Explications des métriques
        with st.expander("ℹ️ Explications des indicateurs de risque"):
            st.markdown("""
            - **Rendement Moyen**: Rendement quotidien moyen en pourcentage
            - **Volatilité**: Écart-type des rendements (mesure de la dispersion)
            - **Ratio de Sharpe**: Rendement ajusté au risque (plus élevé = meilleur)
            - **VaR 95%**: Value at Risk - perte maximale attendue dans 95% des cas
            - **CVaR 95%**: Conditional VaR - perte moyenne au-delà du VaR
            - **Skewness**: Asymétrie de la distribution (< 0 = queue à gauche)
            - **Kurtosis**: "Épaisseur" des queues de distribution (> 0 = queues épaisses)
            - **Max Drawdown**: Perte maximale depuis un sommet historique
            """)
        
        # ========================================
        # ANALYSE AVANCÉE DU RISQUE
        # ========================================
        st.markdown("---")
        st.markdown(f"""
        <div class="insight-box">
            <h4>🎯 Analyse Avancée du Risque</h4>
            <p>Cette section propose une analyse approfondie et dynamique du risque, allant au-delà des statistiques agrégées.
            Elle combine une vue temporelle, distributionnelle et comparative pour une compréhension complète du profil de risque.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if len(selected_fcps) > 0:
            # Sélection du FCP principal pour l'analyse détaillée
            main_fcp = st.selectbox(
                "Sélectionnez le FCP principal pour l'analyse détaillée",
                selected_fcps,
                key="advanced_risk_main_fcp"
            )
            
            # ========================================
            # RISK FINGERPRINT - PROFIL DE RISQUE 7D
            # ========================================
            st.markdown("---")
            st.markdown("### 🎯 Risk Fingerprint - Profil de Risque Multidimensionnel")
            
            st.markdown("""
            <div class="insight-box">
                <h4>📊 Représentation du Profil de Risque sur 7 Dimensions</h4>
                <p>Le <strong>Risk Fingerprint</strong> offre une représentation multidimensionnelle du profil de risque 
                sur 7 dimensions normalisées (0-100). Cette visualisation permet d'identifier rapidement les forces et 
                faiblesses du fonds en matière de gestion du risque.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculer le profil 7D pour tous les FCPs sélectionnés
            profiles_7d = {}
            for fcp in selected_fcps:
                try:
                    profiles_7d[fcp] = calculate_7d_risk_profile(full_df, fcp)
                except Exception as e:
                    st.warning(f"⚠️ Impossible de calculer le profil pour {fcp}: {str(e)}")
            
            if profiles_7d:
                # Normaliser les profils
                normalized_profiles = normalize_7d_risk_profile(profiles_7d)
                
                # Afficher le radar chart pour le FCP principal
                if main_fcp in normalized_profiles:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Créer et afficher le radar chart
                        fig_radar = create_risk_fingerprint_chart(normalized_profiles[main_fcp], main_fcp)
                        st.plotly_chart(fig_radar, use_container_width=True)
                    
                    with col2:
                        st.markdown("##### 📋 Scores par Dimension")
                        
                        # Tableau des scores
                        scores_data = []
                        for dimension, score in normalized_profiles[main_fcp].items():
                            scores_data.append({
                                'Dimension': dimension,
                                'Score': f"{score:.1f}/100"
                            })
                        
                        scores_df = pd.DataFrame(scores_data)
                        st.dataframe(scores_df, use_container_width=True, hide_index=True)
                        
                        # Score global
                        global_score = np.mean(list(normalized_profiles[main_fcp].values()))
                        
                        # Déterminer le niveau de risque
                        if global_score >= 70:
                            risk_level = "Excellent"
                            risk_color = "#28a745"
                        elif global_score >= 50:
                            risk_level = "Bon"
                            risk_color = "#ffc107"
                        else:
                            risk_level = "À Surveiller"
                            risk_color = "#dc3545"
                        
                        st.markdown(f"""
                        <div style="background-color: {risk_color}15; border-left: 4px solid {risk_color}; 
                                    padding: 1rem; border-radius: 5px; margin-top: 1rem;">
                            <div style="font-size: 0.9rem; font-weight: bold; margin-bottom: 0.5rem;">Score Global</div>
                            <div style="font-size: 2rem; font-weight: bold; color: {risk_color};">{global_score:.1f}/100</div>
                            <div style="font-size: 1rem; margin-top: 0.3rem;">{risk_level}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Explication des 7 dimensions
                with st.expander("ℹ️ Explication des 7 Dimensions du Risk Fingerprint"):
                    st.markdown("""
                    Le Risk Fingerprint analyse le profil de risque du fonds sur 7 dimensions clés :
                    
                    1. **Stabilité** : Inverse de la volatilité. Un score élevé indique des rendements stables et prévisibles.
                    
                    2. **Résilience** : Inverse du drawdown maximum. Un score élevé montre une forte capacité à limiter les pertes en période adverse.
                    
                    3. **Récupération** : Inverse du temps de récupération moyen après un drawdown. Un score élevé indique une capacité rapide à retrouver les niveaux précédents.
                    
                    4. **Protection Extrême** : Inverse de la CVaR (Conditional Value at Risk). Un score élevé signifie une meilleure protection contre les pertes extrêmes.
                    
                    5. **Asymétrie** : Skewness normalisée. Un score élevé indique une distribution favorable avec plus de gains extrêmes que de pertes extrêmes.
                    
                    6. **Sharpe Stable** : Stabilité du ratio de Sharpe dans le temps. Un score élevé montre un rendement ajusté au risque constant et fiable.
                    
                    7. **Pain Ratio** : Rendement ajusté à la "douleur" (Ulcer Index). Un score élevé indique que les rendements compensent bien l'inconfort des drawdowns.
                    
                    **Normalisation** : Toutes les dimensions sont normalisées sur une échelle de 0 à 100 selon la formule :
                    `Score = (Valeur - Min) / (Max - Min) × 100`
                    
                    Cette normalisation permet de comparer les fonds sur une échelle commune, indépendamment des unités de mesure d'origine.
                    """)
                
                # Comparaison multi-FCP si plusieurs FCP sélectionnés
                if len(selected_fcps) > 1:
                    st.markdown("---")
                    st.markdown("##### 📊 Comparaison des Profils de Risque")
                    
                    # Créer un tableau comparatif
                    comparison_data = []
                    for fcp_name, profile in normalized_profiles.items():
                        row = {'FCP': fcp_name}
                        row.update({dim: f"{score:.1f}" for dim, score in profile.items()})
                        row['Score Global'] = f"{np.mean(list(profile.values())):.1f}"
                        comparison_data.append(row)
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                    
                    # Identifier les meilleurs et moins bons sur chaque dimension
                    st.markdown("##### 🏆 Forces et Faiblesses par Dimension")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Top Performers par Dimension**")
                        best_performers = []
                        for dimension in normalized_profiles[main_fcp].keys():
                            best_fcp = max(normalized_profiles.items(), key=lambda x: x[1][dimension])
                            best_performers.append({
                                'Dimension': dimension,
                                'FCP': best_fcp[0],
                                'Score': f"{best_fcp[1][dimension]:.1f}"
                            })
                        
                        best_df = pd.DataFrame(best_performers)
                        st.dataframe(best_df, use_container_width=True, hide_index=True)
                    
                    with col2:
                        st.markdown("**Points d'Attention par Dimension**")
                        worst_performers = []
                        for dimension in normalized_profiles[main_fcp].keys():
                            worst_fcp = min(normalized_profiles.items(), key=lambda x: x[1][dimension])
                            worst_performers.append({
                                'Dimension': dimension,
                                'FCP': worst_fcp[0],
                                'Score': f"{worst_fcp[1][dimension]:.1f}"
                            })
                        
                        worst_df = pd.DataFrame(worst_performers)
                        st.dataframe(worst_df, use_container_width=True, hide_index=True)
            
            # ========================================
            # 1. RISQUE DANS LE TEMPS - DRAWDOWNS
            # ========================================
            st.markdown("---")
            st.markdown("### 📉 1. Risque dans le Temps : Analyse des Drawdowns")
            
            dd_analysis = analyze_drawdowns(filtered_df, main_fcp)
            
            # Métriques clés des drawdowns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Drawdown Maximum",
                    f"{dd_analysis['max_drawdown']:.2f}%",
                    help="Perte maximale depuis un sommet historique"
                )
            
            with col2:
                st.metric(
                    "Drawdown Moyen",
                    f"{dd_analysis['avg_drawdown']:.2f}%",
                    help="Drawdown moyen sur les périodes de baisse"
                )
            
            with col3:
                st.metric(
                    "Ulcer Index",
                    f"{dd_analysis['ulcer_index']:.2f}",
                    help="Mesure de la douleur du risque (racine carrée des DD²)"
                )
            
            with col4:
                st.metric(
                    "Pain Ratio",
                    f"{dd_analysis['pain_ratio']:.2f}",
                    help="Rendement total / Ulcer Index (plus élevé = meilleur)"
                )
            
            # Graphique des drawdowns cumulés
            fig_dd = go.Figure()
            
            fig_dd.add_trace(go.Scatter(
                x=dd_analysis['dates'],
                y=dd_analysis['drawdown_series'],
                fill='tozeroy',
                fillcolor='rgba(220, 53, 69, 0.3)',
                line=dict(color='#dc3545', width=2),
                name='Drawdown'
            ))
            
            # Marquer les épisodes de stress majeurs (DD > 5%)
            major_stress = [ep for ep in dd_analysis['drawdown_episodes'] if ep['depth'] < -5]
            if major_stress:
                for ep in major_stress:
                    fig_dd.add_vrect(
                        x0=ep['start_date'],
                        x1=ep['end_date'],
                        fillcolor="rgba(220, 53, 69, 0.1)",
                        layer="below",
                        line_width=0,
                    )
            
            fig_dd.update_layout(
                title=f"Évolution des Drawdowns - {main_fcp}",
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
                height=400,
                template="plotly_white",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_dd, use_container_width=True)
            
            # Tableau des épisodes de stress majeurs
            if major_stress:
                st.markdown("##### 🔴 Épisodes de Stress Majeurs (Drawdown > 5%)")
                
                stress_data = []
                for ep in sorted(major_stress, key=lambda x: x['depth']):
                    recovery_text = f"{ep['recovery_time']} jours" if ep['recovery_time'] else "Non récupéré"
                    stress_data.append({
                        'Début': ep['start_date'].strftime('%Y-%m-%d'),
                        'Fin': ep['end_date'].strftime('%Y-%m-%d'),
                        'Profondeur': f"{ep['depth']:.2f}%",
                        'Durée': f"{ep['duration']} jours",
                        'Récupération': recovery_text
                    })
                
                df_stress = pd.DataFrame(stress_data)
                st.dataframe(df_stress, use_container_width=True, hide_index=True)
                
                st.markdown(f"""
                <div class="interpretation-note">
                <strong>💡 Interprétation:</strong> Le fonds a connu <strong>{len(major_stress)} épisodes de stress significatifs</strong> 
                (drawdown > 5%). Le drawdown maximum de <strong>{dd_analysis['max_drawdown']:.2f}%</strong> et l'Ulcer Index de 
                <strong>{dd_analysis['ulcer_index']:.2f}</strong> reflètent l'intensité du risque vécu par les investisseurs.
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        <div class="insight-box">
            <h4>🎯 Analyse Avancée des Régimes de Volatilité</h4>
            <p>Cette analyse identifie <strong>3 régimes de volatilité distincts</strong> (faible, intermédiaire, élevé) 
            et évalue la capacité du fonds à créer de la valeur selon les conditions de marché. Elle permet d'évaluer 
            la résilience en période de stress et la stabilité du profil de risque.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="interpretation-note">
            <strong>💡 Note Importante:</strong> Cette analyse de volatilité utilise <strong>toute l'historique disponible</strong>, 
            indépendamment du filtre de période sélectionné dans la barre latérale. Cela permet d'avoir une vue complète 
            des régimes de volatilité sur toute la durée de vie du fonds.
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection d'un FCP pour l'analyse
        if len(selected_fcps) > 0:
            fcp_for_analysis = st.selectbox(
                "Sélectionnez un FCP pour l'analyse des régimes de volatilité",
                selected_fcps,
                key="regime_analysis_fcp"
            )
            
            # Analyse des régimes de volatilité - UTILISE TOUTE L'HISTORIQUE
            regime_analysis = analyze_volatility_regimes(full_df, fcp_for_analysis, window=30)
            
            st.markdown("---")
            st.markdown("### 📋 Synthèse Exécutive")
            
            current_regime = regime_analysis['current_regime']
            current_regime_name = regime_analysis['current_regime_name']
            regime_stats = regime_analysis['regime_stats']
            
            # Indicateurs de situation actuelle - Enhanced presentation
            regime_icon = {0: "✅", 1: "⚠️", 2: "🔴"}[current_regime]
            regime_color = {0: "#28a745", 1: "#ffc107", 2: "#dc3545"}[current_regime]
            time_in_regime = regime_stats[current_regime]['proportion']
            avg_return_current = regime_stats[current_regime]['avg_return']
            persistence_current = regime_analysis['persistence'][current_regime]
            avg_duration = persistence_current['avg_duration']
            episodes = persistence_current['episodes']
            
            # Beautiful card presentation for executive summary
            st.markdown(f"""
            <div style="background-color: {regime_color}15; border-left: 4px solid {regime_color}; 
                        padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{regime_icon}</span>
                    <span style="font-size: 1.2rem; font-weight: bold; color: {regime_color};">
                        Régime Actuel: {current_regime_name}
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; margin-top: 0.8rem;">
                    <div>
                        <strong>Volatilité:</strong> {regime_stats[current_regime]['avg_volatility']:.2f}%
                    </div>
                    <div>
                        <strong>Proportion:</strong> {time_in_regime:.1f}%
                    </div>
                    <div>
                        <strong>Rendement Moyen:</strong> {avg_return_current:+.3f}%
                    </div>
                    <div>
                        <strong>Durée Moyenne:</strong> {avg_duration:.0f} jours
                    </div>
                    <div>
                        <strong>Épisodes:</strong> {episodes}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Phrases prêtes à l'emploi pour le reporting
            signal_vigilance = ""
            signal_text = ""
            
            if current_regime == 0:  # Faible volatilité
                signal_text = "CONFORT"
                signal_vigilance = f"""
                <div class="insight-box">
                    <h4>✅ Signal de Confort</h4>
                    <p><strong>Contexte favorable:</strong> Le fonds évolue actuellement dans un régime de <strong>faible volatilité</strong> 
                    ({regime_stats[0]['avg_volatility']:.2f}%), représentant {regime_stats[0]['proportion']:.1f}% du temps historique.</p>
                    <ul>
                        <li>Le fonds bénéficie actuellement d'un environnement de marché stable, avec une <strong>volatilité contenue à {regime_stats[0]['avg_volatility']:.2f}%.</strong></li>
                        <li>Dans ces conditions de faible volatilité, le fonds génère un <strong>rendement quotidien moyen de {avg_return_current:+.3f}%</strong>, 
                        démontrant sa capacité à créer de la valeur en environnement calme.</li>
                        <li>L'analyse historique montre que ce régime de stabilité se maintient en moyenne pendant <strong>{avg_duration:.0f} jours ouvrés.</strong></li>
                    </ul>
                </div>
                """
            elif current_regime == 1:  # Volatilité intermédiaire
                signal_text = "VIGILANCE MODÉRÉE"
                signal_vigilance = f"""
                <div class="interpretation-note">
                    <h4>⚠️ Signal de Vigilance Modérée</h4>
                    <p><strong>Contexte en transition:</strong> Le fonds se trouve dans un régime de <strong>volatilité intermédiaire</strong> 
                    ({regime_stats[1]['avg_volatility']:.2f}%), phase qui représente {regime_stats[1]['proportion']:.1f}% du temps historique.</p>
                    <ul>
                        <li>Le fonds traverse actuellement une phase de <strong>volatilité modérée ({regime_stats[1]['avg_volatility']:.2f}%)</strong>, 
                        caractéristique des périodes de transition de marché.</li>
                        <li>Dans ce régime intermédiaire, le <strong>rendement quotidien moyen s'établit à {avg_return_current:+.3f}%</strong>, 
                        reflétant un équilibre risque-rendement ajusté.</li>
                        <li>La durée moyenne de ce type de période est de <strong>{avg_duration:.0f} jours</strong>, suggérant une situation temporaire.</li>
                    </ul>
                </div>
                """
            else:  # Forte volatilité
                signal_text = "VIGILANCE ÉLEVÉE"
                high_vol_freq = regime_stats[2]['proportion']
                signal_vigilance = f"""
                <div class="alert-box">
                    <h4>🔴 Signal de Vigilance Élevée</h4>
                    <p><strong>Contexte de stress:</strong> Le fonds évolue actuellement dans un régime de <strong>forte volatilité</strong> 
                    ({regime_stats[2]['avg_volatility']:.2f}%), situation historiquement observée {regime_stats[2]['proportion']:.1f}% du temps.</p>
                    <ul>
                        <li>Le fonds traverse une période de <strong>volatilité élevée ({regime_stats[2]['avg_volatility']:.2f}%)</strong>, 
                        nécessitant un suivi rapproché des positions.</li>
                        <li>En phase de stress, le fonds affiche un <strong>rendement quotidien moyen de {avg_return_current:+.3f}%</strong>, 
                        avec un drawdown maximal observé de {regime_stats[2]['max_drawdown']:.2f}%.</li>
                        <li>Historiquement, les épisodes de forte <strong>volatilité durent en moyenne {avg_duration:.0f} jours ouvrés</strong>, 
                        avec {episodes} occurrences sur la période analysée.</li>
                        <li>La résilience du fonds en période de stress est un facteur clé à surveiller pour évaluer la qualité de gestion du risque.</li>
                    </ul>
                </div>
                """
            
            st.markdown(signal_vigilance, unsafe_allow_html=True)
            
            # ===============================
            # VISUALISATION DES RÉGIMES
            # ===============================
            st.markdown("---")
            st.markdown("### 📈 Cycle de Volatilité et Transitions de Régimes")
            
            regime_df = regime_analysis['regime_df']
            
            # Graphique temporel des régimes
            fig_regime_timeline = go.Figure()
            
            regime_colors_map = {0: '#28a745', 1: '#ffc107', 2: '#dc3545'}
            regime_names = regime_analysis['regime_names']
            
            for regime_id in range(3):
                regime_data = regime_df[regime_df['Regime'] == regime_id]
                fig_regime_timeline.add_trace(go.Scatter(
                    x=regime_data['Date'],
                    y=regime_data['Volatility'],
                    mode='markers',
                    name=regime_names[regime_id],
                    marker=dict(size=6, color=regime_colors_map[regime_id]),
                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Volatilité: %{y:.2f}%<extra></extra>'
                ))
            
            fig_regime_timeline.update_layout(
                title=f"Cycle de Volatilité et Régimes - {fcp_for_analysis}",
                xaxis_title="Date",
                yaxis_title="Volatilité Glissante 30J (%)",
                height=500,
                template="plotly_white",
                hovermode='closest',
                showlegend=True
            )
            
            st.plotly_chart(fig_regime_timeline, use_container_width=True)
            
            st.markdown("""
            <div class="interpretation-note">
                <strong>💡 Lecture du Graphique:</strong> Ce graphique illustre la dynamique de la volatilité dans le temps, 
                avec chaque couleur représentant un régime distinct. Les transitions entre régimes révèlent les changements 
                de conditions de marché et permettent d'anticiper les phases de stress ou de stabilité.
            </div>
            """, unsafe_allow_html=True)
            
            # ===============================
            # ANALYSE DESCRIPTIVE PAR RÉGIME
            # ===============================
            st.markdown("---")
            st.markdown("### 📊 Analyse Descriptive par Régime de Volatilité")
            
            # Tableau récapitulatif par régime
            regime_summary = []
            for regime_id in range(3):
                regime_stat = regime_stats[regime_id]
                rr_analysis = regime_analysis['risk_return_analysis'][regime_id]
                persistence = regime_analysis['persistence'][regime_id]
                
                regime_summary.append({
                    'Régime': regime_names[regime_id],
                    'Proportion (%)': f"{regime_stat['proportion']:.1f}%",
                    'Volatilité Moy. (%)': f"{regime_stat['avg_volatility']:.2f}",
                    'Rendement Moy. (%)': f"{regime_stat['avg_return']:+.3f}",
                    'Max Drawdown (%)': f"{regime_stat['max_drawdown']:.2f}",
                    'Ratio Sharpe': f"{rr_analysis['sharpe_ratio']:.2f}",
                    'Durée Moy. (jours)': f"{persistence['avg_duration']:.0f}",
                    'Nb Épisodes': persistence['episodes']
                })
            
            regime_summary_df = pd.DataFrame(regime_summary)
            st.dataframe(regime_summary_df, use_container_width=True, hide_index=True)
            
            # Visualisations comparatives
            col1, col2 = st.columns(2)
            
            with col1:
                # Performance moyenne par régime
                fig_perf_regime = go.Figure()
                avg_returns = [regime_stats[i]['avg_return'] for i in range(3)]
                colors_bars = ['#28a745', '#ffc107', '#dc3545']
                
                fig_perf_regime.add_trace(go.Bar(
                    x=[regime_names[i] for i in range(3)],
                    y=avg_returns,
                    marker_color=colors_bars,
                    text=[f"{val:+.3f}%" for val in avg_returns],
                    textposition='outside'
                ))
                
                fig_perf_regime.update_layout(
                    title="Rendement Moyen Quotidien par Régime",
                    xaxis_title="Régime",
                    yaxis_title="Rendement (%)",
                    height=350,
                    template="plotly_white",
                    showlegend=False
                )
                
                st.plotly_chart(fig_perf_regime, use_container_width=True)
            
            with col2:
                # Proportion du temps par régime
                fig_time_regime = go.Figure()
                proportions = [regime_stats[i]['proportion'] for i in range(3)]
                
                fig_time_regime.add_trace(go.Pie(
                    labels=[regime_names[i] for i in range(3)],
                    values=proportions,
                    marker=dict(colors=colors_bars),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Proportion: %{value:.1f}%<extra></extra>'
                ))
                
                fig_time_regime.update_layout(
                    title="Répartition du Temps par Régime",
                    height=350,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_time_regime, use_container_width=True)
            
            # ===============================
            # MATRICE DE TRANSITION
            # ===============================
            st.markdown("---")
            st.markdown("### 🔄 Matrice de Transition entre Régimes")
            
            transition_probs = regime_analysis['transition_probs']
            
            fig_transition = go.Figure(data=go.Heatmap(
                z=transition_probs * 100,
                x=[regime_names[i] for i in range(3)],
                y=[regime_names[i] for i in range(3)],
                colorscale='Blues',
                text=np.round(transition_probs * 100, 1),
                texttemplate='%{text}%',
                textfont={"size": 12},
                colorbar=dict(title="Probabilité (%)")
            ))
            
            fig_transition.update_layout(
                title="Probabilités de Transition entre Régimes de Volatilité",
                xaxis_title="Vers →",
                yaxis_title="Depuis ↓",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_transition, use_container_width=True)
            
            # Interprétation des transitions
            max_persistence_regime = max(range(3), key=lambda i: transition_probs[i, i])
            max_persistence_prob = transition_probs[max_persistence_regime, max_persistence_regime] * 100
            
            st.markdown(f"""
            <div class="interpretation-note">
                <strong>💡 Interprétation de la Matrice:</strong><br>
                • La diagonale représente la <strong>persistance</strong> de chaque régime (probabilité de rester dans le même état).<br>
                • Le régime <strong>{regime_names[max_persistence_regime]}</strong> présente la plus forte persistance ({max_persistence_prob:.1f}%), 
                indiquant une tendance à se maintenir dans cet état.<br>
                • Les valeurs hors diagonale indiquent les probabilités de <strong>transition</strong> d'un régime à un autre, 
                révélant la dynamique des cycles de volatilité.
            </div>
            """, unsafe_allow_html=True)
            
            # ===============================
            # ANALYSE RISQUE-RENDEMENT
            # ===============================
            st.markdown("---")
            st.markdown("### 💼 Analyse Risque-Rendement par Régime")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Ratio de Sharpe par régime
                fig_sharpe_regime = go.Figure()
                sharpe_ratios = [regime_analysis['risk_return_analysis'][i]['sharpe_ratio'] for i in range(3)]
                
                fig_sharpe_regime.add_trace(go.Bar(
                    x=[regime_names[i] for i in range(3)],
                    y=sharpe_ratios,
                    marker_color=colors_bars,
                    text=[f"{val:.2f}" for val in sharpe_ratios],
                    textposition='outside'
                ))
                
                fig_sharpe_regime.update_layout(
                    title="Ratio de Sharpe par Régime",
                    xaxis_title="Régime",
                    yaxis_title="Ratio de Sharpe",
                    height=350,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_sharpe_regime, use_container_width=True)
            
            with col2:
                # Drawdown maximal par régime
                fig_dd_regime = go.Figure()
                drawdowns = [regime_stats[i]['max_drawdown'] for i in range(3)]
                
                fig_dd_regime.add_trace(go.Bar(
                    x=[regime_names[i] for i in range(3)],
                    y=drawdowns,
                    marker_color=colors_bars,
                    text=[f"{val:.2f}%" for val in drawdowns],
                    textposition='outside'
                ))
                
                fig_dd_regime.update_layout(
                    title="Drawdown Maximal par Régime",
                    xaxis_title="Régime",
                    yaxis_title="Max Drawdown (%)",
                    height=350,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_dd_regime, use_container_width=True)
            
            # Interprétation risque-rendement - Simplified presentation
            best_sharpe_regime = max(range(3), key=lambda i: regime_analysis['risk_return_analysis'][i]['sharpe_ratio'])
            worst_dd_regime = min(range(3), key=lambda i: regime_stats[i]['max_drawdown'])
            
            low_vol_return = regime_stats[0]['avg_return']
            high_vol_return = regime_stats[2]['avg_return']
            
            value_creation_text = "positive, démontrant une bonne capacité à créer de la valeur" if low_vol_return > 0 else "négative, suggérant des difficultés à capitaliser sur la stabilité"
            resilience_text = "résilient" if high_vol_return > -0.1 else "sous pression"
            
            st.markdown(f"""
**🎯 Interprétation Risque-Rendement**

**Création de valeur en période calme:**  
En régime de faible volatilité, le fonds génère un rendement quotidien moyen de **{low_vol_return:+.3f}%**, 
performance {value_creation_text} en environnement stable.

**Résilience en période de stress:**  
En régime de forte volatilité, le rendement moyen est de **{high_vol_return:+.3f}%**, 
indiquant un fonds {resilience_text} face aux turbulences de marché. Le drawdown maximal de 
**{regime_stats[2]['max_drawdown']:.2f}%** reflète l'exposition au risque extrême.

**Profil risque-rendement optimal:**  
Le régime **{regime_names[best_sharpe_regime]}** offre le meilleur ratio de Sharpe 
({regime_analysis['risk_return_analysis'][best_sharpe_regime]['sharpe_ratio']:.2f}), 
indiquant la période où le rendement ajusté au risque est le plus favorable.
""")
            
            # ===============================
            # STABILITÉ DU PROFIL DE RISQUE
            # ===============================
            st.markdown("---")
            st.markdown("### 🎲 Analyse de Stabilité du Profil de Risque")
            
            high_vol_freq = regime_stats[2]['proportion']
            high_vol_episodes = regime_analysis['persistence'][2]['episodes']
            high_vol_avg_duration = regime_analysis['persistence'][2]['avg_duration']
            high_vol_persistence = transition_probs[2, 2] * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Fréquence Forte Volatilité",
                    f"{high_vol_freq:.1f}%",
                    help="Pourcentage du temps passé en régime de forte volatilité"
                )
            
            with col2:
                st.metric(
                    "Nombre d'Épisodes",
                    f"{high_vol_episodes}",
                    help="Nombre d'occurrences de forte volatilité sur la période"
                )
            
            with col3:
                st.metric(
                    "Persistance Moyenne",
                    f"{high_vol_avg_duration:.0f} jours",
                    help="Durée moyenne d'un épisode de forte volatilité"
                )
            
            # Score de stabilité
            stability_score = 100 - (high_vol_freq + (high_vol_episodes / len(regime_df) * 100 * 10))
            stability_score = max(0, min(100, stability_score))
            
            stability_interpretation = ""
            if stability_score >= 75:
                stability_color = "#28a745"
                stability_level = "Excellent"
                stability_interpretation = "Le fonds présente un profil de risque très stable, avec des épisodes de forte volatilité rares et de courte durée."
            elif stability_score >= 50:
                stability_color = "#ffc107"
                stability_level = "Bon"
                stability_interpretation = "Le fonds affiche une stabilité correcte, avec une exposition modérée aux périodes de forte volatilité."
            else:
                stability_color = "#dc3545"
                stability_level = "À Surveiller"
                stability_interpretation = "Le fonds présente une exposition significative aux régimes de forte volatilité, nécessitant une surveillance accrue."
            
            st.markdown(f"""
            <div class="ranking-card">
                <h3>📊 Score de Stabilité du Profil de Risque</h3>
                <div style="text-align: center; padding: 0.3rem;">
                    <div style="font-size: 2rem; font-weight: bold;">{stability_score:.0f}/100</div>
                    <div style="font-size: 1rem; margin-top: 0.2rem;">{stability_level}</div>
                </div>
                <div class="ranking-item">
                    <p style="margin: 0;">{stability_interpretation}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="interpretation-note">
                <strong>💡 Éléments d'Analyse:</strong><br>
                • <strong>Fréquence:</strong> Le fonds passe {high_vol_freq:.1f}% de son temps en régime de forte volatilité, 
                réparti sur {high_vol_episodes} épisodes distincts.<br>
                • <strong>Persistance:</strong> Chaque épisode de forte volatilité dure en moyenne {high_vol_avg_duration:.0f} jours ouvrés, 
                avec une probabilité de {high_vol_persistence:.1f}% de se maintenir d'un jour à l'autre.<br>
                • <strong>Implications pour la gestion:</strong> {"Une fréquence élevée et/ou une forte persistance des régimes volatils peuvent indiquer un profil de risque structurellement plus élevé, nécessitant une allocation et une gestion active adaptées." if high_vol_freq > 25 or high_vol_persistence > 50 else "La faible fréquence et persistance des régimes volatils suggèrent un profil de risque maîtrisé et cohérent avec une stratégie de gestion prudente."}
            </div>
            """, unsafe_allow_html=True)
            
            # ===============================
            # AIDE À LA DÉCISION
            # ===============================
            st.markdown("---")
            st.markdown("### 🎯 Éléments d'Aide à la Décision")
            
            # Signaux de gestion
            signals = []
            
            # Signal 1: Régime actuel
            if current_regime == 0:
                signals.append({
                    'Signal': '✅ Environnement Favorable',
                    'Description': 'Régime de faible volatilité actuel',
                    'Action Suggérée': 'Période propice au renforcement des positions et à l\'optimisation de l\'allocation'
                })
            elif current_regime == 2:
                signals.append({
                    'Signal': '🔴 Vigilance Requise',
                    'Description': 'Régime de forte volatilité actuel',
                    'Action Suggérée': 'Surveiller étroitement les positions, envisager des couvertures ou réductions d\'exposition'
                })
            else:
                signals.append({
                    'Signal': '⚠️ Phase de Transition',
                    'Description': 'Régime de volatilité intermédiaire',
                    'Action Suggérée': 'Maintenir une vigilance accrue, anticiper une évolution vers un régime plus stable ou plus volatile'
                })
            
            # Signal 2: Performance dans le régime actuel
            if current_regime == 0 and low_vol_return > 0.05:
                signals.append({
                    'Signal': '✅ Création de Valeur Active',
                    'Description': f'Rendement positif de {low_vol_return:+.3f}% en période stable',
                    'Action Suggérée': 'Profil adapté aux investisseurs recherchant une croissance régulière'
                })
            elif current_regime == 2 and high_vol_return < -0.2:
                signals.append({
                    'Signal': '⚠️ Sensibilité au Stress',
                    'Description': f'Rendement négatif de {high_vol_return:+.3f}% en période volatile',
                    'Action Suggérée': 'Évaluer les mécanismes de protection et la stratégie de gestion du risque'
                })
            
            # Signal 3: Stabilité
            if stability_score >= 75:
                signals.append({
                    'Signal': '✅ Profil Stable',
                    'Description': f'Score de stabilité élevé ({stability_score:.0f}/100)',
                    'Action Suggérée': 'Profil adapté aux investisseurs recherchant régularité et prévisibilité'
                })
            elif stability_score < 50:
                signals.append({
                    'Signal': '🔴 Volatilité Structurelle',
                    'Description': f'Score de stabilité faible ({stability_score:.0f}/100)',
                    'Action Suggérée': 'Convient aux investisseurs tolérants au risque, surveiller la cohérence avec le mandat'
                })
            
            signals_df = pd.DataFrame(signals)
            st.dataframe(signals_df, use_container_width=True, hide_index=True)
    
    # Section: Export des Données
    # ===================
    st.markdown("---")
    st.subheader("📥 Export des Données et Analyses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export VL data for selected FCPs
        export_df = filtered_df[['Date'] + selected_fcps].copy()
        csv_vl = export_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📊 Télécharger Valeurs Liquidatives (CSV)",
            data=csv_vl,
            file_name=f"valeurs_liquidatives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Télécharger les valeurs liquidatives des FCP sélectionnés"
        )
    
    with col2:
        # Export summary statistics
        summary_data = []
        for fcp in selected_fcps:
            returns = filtered_df[fcp].pct_change().dropna() * 100
            summary_data.append({
                'FCP': fcp,
                'VL Initiale': filtered_df[fcp].iloc[0],
                'VL Finale': filtered_df[fcp].iloc[-1],
                'Performance (%)': ((filtered_df[fcp].iloc[-1] / filtered_df[fcp].iloc[0]) - 1) * 100,
                'Volatilité (%)': returns.std(),
                'Rendement Moyen (%)': returns.mean(),
                'Max': returns.max(),
                'Min': returns.min()
            })
        
        summary_df = pd.DataFrame(summary_data)
        csv_summary = summary_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📈 Télécharger Statistiques (CSV)",
            data=csv_summary,
            file_name=f"statistiques_fcps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Télécharger les statistiques récapitulatives des FCP sélectionnés"
        )
    
    st.markdown("""
    <div class="interpretation-note">
        <h4>💡 Note sur les Exports</h4>
        <p>Les fichiers exportés contiennent uniquement les données des FCP sélectionnés pour la période analysée. 
        Les statistiques sont calculées sur cette même période.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()