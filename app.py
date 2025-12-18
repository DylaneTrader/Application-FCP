import streamlit as st
import pandas as pd
import os
from config import (
    DATA_FILE, DEFAULT_SHEET_NAME, IS_CSV, 
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
)
from utils import load_data, get_sheet_names

# Configuration de la page
st.set_page_config(
    page_title="Analyse FCP - Accueil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
from config import COMMON_CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)

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
    
    # Sélecteur de feuille (uniquement pour Excel)
    if not IS_CSV:
        selected_sheet = st.selectbox(
            "Sélectionnez une feuille à prévisualiser",
            options=sheet_names,
            index=0,
            help="Choisissez la feuille Excel dont vous souhaitez voir un aperçu"
        )
    else:
        selected_sheet = sheet_names[0]
        st.info(f"📄 Format CSV détecté - Fichier: `{os.path.basename(DATA_FILE)}`")
    
    # Chargement des données pour la feuille sélectionnée
    with st.spinner(f'Chargement des données de la feuille "{selected_sheet}"...'):
        df = load_data(str(selected_sheet))
    
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
        df_info = load_data(str(selected_sheet) if 'selected_sheet' in locals() else 'Valeurs Liquidatives')
        
        if selected_sheet == 'Valeurs Liquidatives' or 'selected_sheet' not in locals():
            fcp_count_info = len([col for col in df_info.columns if col.startswith('FCP')])
        else:
            fcp_count_info = len(df_info['FCP'].unique()) if 'FCP' in df_info.columns else 0
        
        file_type = "CSV" if IS_CSV else "Excel (XLSX)"
        info_text = f"""
        - **Fichier**: `{DATA_FILE}`
        - **Type**: {file_type}
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
