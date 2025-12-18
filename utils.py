"""
Fonctions utilitaires partagées pour l'application FCP
Contient les fonctions de chargement de données et de conversion
"""
import pandas as pd
import streamlit as st
from config import DATA_FILE, IS_CSV, DEFAULT_SHEET_NAME, PRIMARY_COLOR


@st.cache_data
def load_data(sheet_name=DEFAULT_SHEET_NAME):
    """
    Charge les données du fichier CSV ou Excel
    
    Args:
        sheet_name (str): Nom de la feuille Excel à charger (ignoré pour CSV)
    
    Returns:
        pd.DataFrame: DataFrame avec les données chargées
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
        xls = pd.ExcelFile(DATA_FILE)
        return xls.sheet_names


def hex_to_rgba(hex_color, alpha=1.0):
    """
    Convertit une couleur hexadécimale en format rgba string
    
    Args:
        hex_color (str): Couleur hexadécimale (e.g., '#114B80' ou '114B80')
        alpha (float): Valeur de transparence alpha entre 0.0 et 1.0
        
    Returns:
        str: Couleur au format RGBA (e.g., 'rgba(17, 75, 128, 0.3)')
        
    Raises:
        ValueError: Si alpha n'est pas entre 0.0 et 1.0 ou si le format hex est invalide
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
