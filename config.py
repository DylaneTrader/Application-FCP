"""
Configuration centrale pour l'application FCP
Contient les constantes, couleurs et configurations partagées entre toutes les pages
"""
import os

# Configuration des fichiers de données
DATA_FILE = os.getenv('FCP_DATA_FILE', 'data_fcp.xlsx')
DEFAULT_SHEET_NAME = 'Valeurs Liquidatives'

# Détection automatique du type de fichier
FILE_EXTENSION = os.path.splitext(DATA_FILE)[1].lower()
IS_CSV = FILE_EXTENSION == '.csv'

# Palette de couleurs de l'application
PRIMARY_COLOR = "#114B80"    # Bleu profond — titres, boutons principaux
SECONDARY_COLOR = "#567389"  # Bleu-gris — widgets, lignes, icônes
ACCENT_COLOR = "#ACC7DF"     # Bleu clair — fonds de cartes, hover

# Constantes pour les calculs financiers
TRADING_DAYS_PER_YEAR = 252

# Constantes pour les analyses
MIN_SEASONALITY_PERIODS = 24  # Minimum observations pour analyse de saisonnalité
DEFAULT_RADAR_RANGE = 150  # Portée maximale par défaut pour graphiques radar
ALL_FCP_LABEL = "Tous les FCP"  # Label pour les données FCP agrégées
MILLIONS_DIVISOR = 1e6  # Diviseur pour convertir en millions
HIGH_VOLATILITY_THRESHOLD = 50  # Seuil de pourcentage pour haute volatilité

# CSS commun pour toutes les pages
COMMON_CSS = f"""
<style>
    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {PRIMARY_COLOR};
        text-align: center;
        margin-bottom: 1rem;
    }}
    .metric-card {{
        background-color: #f8f9fa;
        padding: 0.3rem;
        border-radius: 3px;
        border-left: 2px solid {PRIMARY_COLOR};
    }}
    /* Note: .css-1d391kg is a Streamlit internal class that may change between versions.
       Using [data-testid] selectors is more stable. Keep both for compatibility. */
    .css-1d391kg, [data-testid="stSidebar"] {{
        background-color: #f8f9fa;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.5rem;
        font-weight: bold;
    }}
    .page-card {{
        background-color: #ffffff;
        padding: 0.5rem;
        border-radius: 3px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 0.3rem;
        border-left: 2px solid {PRIMARY_COLOR};
    }}
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
    .seasonality-card {{
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.3rem 0;
        border: 1px solid #dee2e6;
    }}
</style>
"""
