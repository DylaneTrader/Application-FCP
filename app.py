import streamlit as st
import pandas as pd
import os

# Constants
DATA_FILE = os.getenv('FCP_DATA_FILE', 'data_fcp.xlsx')
DEFAULT_SHEET_NAME = 'Valeurs Liquidatives'  # Default sheet for data loading

# Color Scheme
PRIMARY_COLOR = "#114B80"    # Bleu profond — titres, boutons principaux
SECONDARY_COLOR = "#567389"  # Bleu-gris — widgets, lignes, icônes
ACCENT_COLOR = "#ACC7DF"     # Bleu clair — fonds de cartes, hover

# Configuration de la page
st.set_page_config(
    page_title="Analyse FCP - Accueil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour améliorer l'esthétique
st.markdown(f"""
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
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {{
        background-color: #f8f9fa;
    }}
    /* Better spacing for metrics */
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
</style>
""", unsafe_allow_html=True)

# Chargement des données
@st.cache_data
def load_data(sheet_name=DEFAULT_SHEET_NAME):
    """Charge les données du fichier Excel"""
    try:
        df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
        return df
    except PermissionError:
        st.error("""
        ❌ **Erreur d'accès au fichier**
        
        Le fichier de données est actuellement verrouillé. Cela se produit généralement quand :
        - Le fichier Excel est ouvert dans une autre application
        - Le fichier est en cours d'utilisation par un autre programme
        
        **Solutions :**
        1. Fermez le fichier Excel s'il est ouvert
        2. Vérifiez qu'aucun autre programme n'utilise le fichier
        3. Assurez-vous d'avoir les permissions nécessaires pour lire le fichier
        
        Puis rafraîchissez cette page.
        """)
        st.stop()
    except FileNotFoundError:
        st.error(f"""
        ❌ **Fichier de données introuvable**
        
        Le fichier `{DATA_FILE}` n'a pas été trouvé dans le répertoire attendu.
        
        **Solutions :**
        1. Vérifiez que le fichier existe dans le dossier de l'application
        2. Vérifiez le nom du fichier (doit être exactement `{DATA_FILE}`)
        3. Assurez-vous que le fichier n'a pas été déplacé ou supprimé
        """)
        st.stop()

@st.cache_data
def get_sheet_names():
    """Récupère la liste des feuilles disponibles dans le fichier Excel"""
    try:
        xls = pd.ExcelFile(DATA_FILE)
        return xls.sheet_names
    except PermissionError:
        st.error("""
        ❌ **Erreur d'accès au fichier**
        
        Le fichier de données est actuellement verrouillé. Cela se produit généralement quand :
        - Le fichier Excel est ouvert dans une autre application
        - Le fichier est en cours d'utilisation par un autre programme
        
        **Solutions :**
        1. **Fermez le fichier Excel** s'il est ouvert
        2. Vérifiez qu'aucun autre programme n'utilise le fichier
        3. Assurez-vous d'avoir les permissions nécessaires pour lire le fichier
        
        Puis rafraîchissez cette page (F5 ou Ctrl+R).
        """)
        st.stop()
    except FileNotFoundError:
        st.error(f"""
        ❌ **Fichier de données introuvable**
        
        Le fichier `{DATA_FILE}` n'a pas été trouvé dans le répertoire attendu.
        
        **Solutions :**
        1. Vérifiez que le fichier existe dans le dossier de l'application
        2. Vérifiez le nom du fichier (doit être exactement `{DATA_FILE}`)
        3. Assurez-vous que le fichier n'a pas été déplacé ou supprimé
        """)
        st.stop()

# Application principale
def main():
    st.markdown('<h1 class="main-header">📊 Analyse FCP - Tableau de Bord</h1>', unsafe_allow_html=True)
    
    # Information en haut de page
    st.markdown("### 👋 Bienvenue dans l'outil d'analyse FCP")
    st.markdown("Cette application vous permet d'analyser en profondeur vos fonds communs de placement.")
    
    st.markdown("---")
    
    # Section: Aperçu des Données avec filtre de feuille
    st.subheader("📊 Aperçu des Données")
    
    # Récupérer les noms des feuilles
    sheet_names = get_sheet_names()
    
    # Sélecteur de feuille
    selected_sheet = st.selectbox(
        "Sélectionnez une feuille à prévisualiser",
        options=sheet_names,
        index=0,
        help="Choisissez la feuille Excel dont vous souhaitez voir un aperçu"
    )
    
    # Chargement des données pour la feuille sélectionnée
    with st.spinner(f'Chargement des données de la feuille "{selected_sheet}"...'):
        df = load_data(selected_sheet)
    
    # Statistiques générales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if selected_sheet == 'Valeurs Liquidatives':
            fcp_count = len([col for col in df.columns if col.startswith('FCP')])
            st.metric("Nombre de FCP", fcp_count)
        else:
            fcp_count = len(df['FCP'].unique()) if 'FCP' in df.columns else 0
            st.metric("Nombre de FCP", fcp_count)
    
    with col2:
        if 'Date' in df.columns:
            date_range = (df['Date'].max() - df['Date'].min()).days
            st.metric("Période (jours)", f"{date_range}")
        else:
            st.metric("Lignes", len(df))
    
    with col3:
        if 'Date' in df.columns:
            st.metric("Date début", df['Date'].min().strftime('%Y-%m-%d'))
        else:
            st.metric("Colonnes", len(df.columns))
    
    with col4:
        if 'Date' in df.columns:
            st.metric("Date fin", df['Date'].max().strftime('%Y-%m-%d'))
        else:
            st.metric("Feuille", selected_sheet)
    
    # Aperçu des données
    st.markdown(f"**Aperçu des données - {selected_sheet}**")
    
    # Afficher les premières lignes
    num_rows = st.slider("Nombre de lignes à afficher", min_value=5, max_value=100, value=10, step=5)
    st.dataframe(df.head(num_rows), use_container_width=True)
    
    # Informations sur les colonnes
    with st.expander("📋 Informations sur les colonnes"):
        col_info = pd.DataFrame({
            'Colonne': df.columns,
            'Type': df.dtypes.astype(str),
            'Valeurs non-nulles': df.count(),
            'Valeurs uniques': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Pages disponibles
    st.subheader("📑 Pages d'Analyse Disponibles")
    st.markdown("Utilisez la barre latérale pour naviguer entre les différentes pages d'analyse.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="page-card">
            <h3>📈 Valeurs Liquidatives</h3>
            <p>Analyse complète des valeurs liquidatives avec :</p>
            <ul>
                <li>Performances calendaires et glissantes</li>
                <li>Évolution temporelle interactive</li>
                <li>Distributions et statistiques</li>
                <li>Indicateurs de risque avancés</li>
                <li>Clusters de volatilité</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="page-card">
            <h3>💰 Souscriptions & Rachats</h3>
            <p>Analyse des flux de souscriptions et rachats :</p>
            <ul>
                <li>Indicateurs clés et évolution temporelle</li>
                <li>Comparaison par FCP</li>
                <li>Analyse par type de client</li>
                <li>Heatmaps et corrélations</li>
                <li>Top performers et export de données</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="page-card">
            <h3>💼 Actifs Nets</h3>
            <p>Analyse des actifs nets sous gestion :</p>
            <ul>
                <li>Évolution et répartition des actifs</li>
                <li>Analyse de croissance et tendances</li>
                <li>Comparaisons et classements</li>
                <li>Statistiques avancées</li>
                <li>Corrélation avec les flux</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Instructions
    st.subheader("ℹ️ Comment utiliser l'application")
    
    st.markdown("""
    1. **Naviguez** vers une page d'analyse en utilisant la barre latérale
    2. **Sélectionnez** les FCP que vous souhaitez analyser
    3. **Ajustez** la période d'analyse et les autres paramètres
    4. **Explorez** les différentes visualisations et statistiques
    5. **Exportez** vos données si nécessaire
    """)
    
    # Informations sur le fichier de données
    with st.expander("📁 Informations sur le fichier de données"):
        # Charger les données de la feuille sélectionnée ou par défaut
        df_info = load_data(selected_sheet if 'selected_sheet' in locals() else 'Valeurs Liquidatives')
        
        if selected_sheet == 'Valeurs Liquidatives' or 'selected_sheet' not in locals():
            fcp_count_info = len([col for col in df_info.columns if col.startswith('FCP')])
        else:
            fcp_count_info = len(df_info['FCP'].unique()) if 'FCP' in df_info.columns else 0
            
        info_text = f"""
        - **Fichier**: `{DATA_FILE}`
        - **Nombre de FCP**: {fcp_count_info}
        """
        
        if 'Date' in df_info.columns:
            info_text += f"""
        - **Période couverte**: {df_info['Date'].min().strftime('%Y-%m-%d')} à {df_info['Date'].max().strftime('%Y-%m-%d')}
        - **Nombre d'observations**: {len(df_info)}
        """
        else:
            info_text += f"""
        - **Nombre de lignes**: {len(df_info)}
        - **Nombre de colonnes**: {len(df_info.columns)}
        """
        
        st.markdown(info_text)

if __name__ == "__main__":
    main()