"""
Fonctions utilitaires partagées pour l'application FCP
Contient les fonctions de chargement de données et de conversion
"""
import pandas as pd
import numpy as np
import streamlit as st
from config import DATA_FILE, IS_CSV, DEFAULT_SHEET_NAME


@st.cache_data
def load_data(sheet_name=DEFAULT_SHEET_NAME):
    """
    Charge les données du fichier CSV ou Excel
    
    Args:
        sheet_name (str): Nom de la feuille Excel à charger (ignoré pour CSV)
    
    Returns:
        pd.DataFrame: DataFrame avec les données chargées et dates triées
    """
    if IS_CSV:
        # Pour CSV, charger directement (pas de notion de feuilles)
        df = pd.read_csv(DATA_FILE)
    else:
        # Pour Excel, charger la feuille spécifiée
        df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)
    
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.sort_values('Date')
    return df


@st.cache_data
def get_sheet_names():
    """
    Récupère la liste des feuilles disponibles dans le fichier Excel
    (ou nom par défaut pour CSV)
    
    Returns:
        list: Liste des noms de feuilles
    """
    if IS_CSV:
        # Pour CSV, retourner un nom de feuille par défaut
        return ['Data']
    else:
        # Pour Excel, retourner les noms réels des feuilles
        with pd.ExcelFile(DATA_FILE) as xls:
            return xls.sheet_names


def hex_to_rgba(hex_color, alpha=1.0):
    """
    Convertit une couleur hexadécimale en format rgba string.
    Valide les entrées et lève des exceptions en cas d'erreur.
    
    Args:
        hex_color (str): Couleur hexadécimale (e.g., '#114B80' ou '114B80')
        alpha (float): Valeur de transparence alpha entre 0.0 et 1.0
        
    Returns:
        str: Couleur au format RGBA (e.g., 'rgba(17, 75, 128, 0.3)')
        
    Raises:
        ValueError: Si alpha n'est pas entre 0.0 et 1.0 ou si le format hex est invalide
    """
    # Validation de l'alpha
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"Alpha value must be between 0.0 and 1.0, got {alpha}")
    
    # Nettoyage et validation du format hex
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color format: {hex_color}. Expected 6-character hex string.")
    
    # Conversion hex vers RGB
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        raise ValueError(f"Invalid hex color format: {hex_color}. Could not parse hex values.")
    
    return f'rgba({r}, {g}, {b}, {alpha})'


def format_number(value, decimals=2, suffix=''):
    """
    Formate un nombre pour l'affichage
    
    Args:
        value (float): Valeur à formater
        decimals (int): Nombre de décimales
        suffix (str): Suffixe à ajouter (%, M, etc.)
    
    Returns:
        str: Nombre formaté
    """
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"


def safe_division(numerator, denominator, default=0):
    """
    Effectue une division sécurisée en évitant la division par zéro
    
    Args:
        numerator (float): Numérateur
        denominator (float): Dénominateur
        default (float): Valeur par défaut si division impossible
    
    Returns:
        float: Résultat de la division ou valeur par défaut
    """
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def calculate_returns(prices):
    """
    Calcule les rendements à partir d'une série de prix
    
    Args:
        prices (pd.Series): Série de prix
        
    Returns:
        pd.Series: Série de rendements (en pourcentage)
    """
    if len(prices) < 2:
        return pd.Series()
    return prices.pct_change().dropna() * 100


def calculate_annualized_return(returns, periods_per_year=252):
    """
    Calcule le rendement annualisé
    
    Args:
        returns (pd.Series): Série de rendements
        periods_per_year (int): Nombre de périodes par an (252 pour jours de trading)
            Note: Ce paramètre doit correspondre à la fréquence des données.
            Utiliser 252 pour données quotidiennes, 12 pour mensuelles, etc.
        
    Returns:
        float: Rendement annualisé en pourcentage
    """
    if len(returns) == 0:
        return 0
    mean_return = returns.mean()
    return ((1 + mean_return / 100) ** periods_per_year - 1) * 100


def calculate_volatility(returns, periods_per_year=252):
    """
    Calcule la volatilité annualisée
    
    Args:
        returns (pd.Series): Série de rendements
        periods_per_year (int): Nombre de périodes par an
            Note: Ce paramètre doit correspondre à la fréquence des données.
            Utiliser 252 pour données quotidiennes, 12 pour mensuelles, etc.
        
    Returns:
        float: Volatilité annualisée en pourcentage
    """
    if len(returns) == 0:
        return 0
    return returns.std() * np.sqrt(periods_per_year)


def calculate_sharpe_ratio(returns, risk_free_rate=0, periods_per_year=252):
    """
    Calcule le ratio de Sharpe
    
    Args:
        returns (pd.Series): Série de rendements
        risk_free_rate (float): Taux sans risque annuel (en %)
        periods_per_year (int): Nombre de périodes par an
        
    Returns:
        float: Ratio de Sharpe
    """
    if len(returns) == 0:
        return 0
    
    excess_returns = returns - (risk_free_rate / periods_per_year)
    if excess_returns.std() == 0:
        return 0
    
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)


def calculate_max_drawdown(prices):
    """
    Calcule le drawdown maximum
    
    Args:
        prices (pd.Series): Série de prix
        
    Returns:
        float: Drawdown maximum en pourcentage (valeur négative)
    """
    if len(prices) == 0:
        return 0
    
    # Calculer les rendements cumulés en gérant les NaN
    cumulative_returns = (1 + prices.pct_change().fillna(0)).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max * 100
    
    return drawdown.min()


def get_fcp_columns(df):
    """
    Extrait les colonnes FCP d'un DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame contenant les données
        
    Returns:
        list: Liste des noms de colonnes FCP (toutes sauf 'Date')
    """
    return [col for col in df.columns if col != 'Date']


def filter_dataframe_by_date(df, start_date, end_date):
    """
    Filtre un DataFrame par plage de dates
    
    Args:
        df (pd.DataFrame): DataFrame avec une colonne 'Date'
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    if 'Date' not in df.columns:
        return df
    
    mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
    return df[mask]

