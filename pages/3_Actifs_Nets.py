"""
Actifs Nets Analysis Page
Analyzes net assets for FCP funds
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from scipy import stats
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# Import centralized configuration and utilities
from config import (
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR,
    COMMON_CSS
)
from utils import load_data

# Configuration de la page
st.set_page_config(
    page_title="Analyse FCP - Actifs Nets",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


@st.cache_data
def load_actifs_nets_data():
    """Load net assets data from CSV or Excel"""
    data_file = os.getenv('FCP_DATA_FILE', 'data_fcp.xlsx')
    file_extension = os.path.splitext(data_file)[1].lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(data_file)
    else:
        df = pd.read_excel(data_file, sheet_name='Actifs Nets')
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date')
    return df


@st.cache_data
def load_souscriptions_rachats_data():
    """Load subscriptions and redemptions data from CSV or Excel"""
    data_file = os.getenv('FCP_DATA_FILE', 'data_fcp.xlsx')
    file_extension = os.path.splitext(data_file)[1].lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(data_file)
    else:
        df = pd.read_excel(data_file, sheet_name='Souscriptions Rachats')
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date')
    return df


@st.cache_data
def load_valeurs_liquidatives_data():
    """Load net asset values (VL) data from CSV or Excel"""
    data_file = os.getenv('FCP_DATA_FILE', 'data_fcp.xlsx')
    file_extension = os.path.splitext(data_file)[1].lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(data_file)
    else:
        df = pd.read_excel(data_file, sheet_name='Valeurs Liquidatives')
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date')
    return df


def calculate_growth_rate(series):
    """Calculate growth rate for a series"""
    if len(series) < 2:
        return 0
    return ((series.iloc[-1] / series.iloc[0]) - 1) * 100


def calculate_cagr(series, periods_per_year=252):
    """Calculate Compound Annual Growth Rate"""
    if len(series) < 2:
        return 0
    years = len(series) / periods_per_year
    if years <= 0 or series.iloc[0] <= 0:
        return 0
    return (((series.iloc[-1] / series.iloc[0]) ** (1 / years)) - 1) * 100


def calculate_correlation_with_flows(df_actifs, df_flows, fcp_name, date_range):
    """Calculate correlation between net assets and subscription/redemption flows"""
    # Filter flows for the FCP
    df_fcp_flows = df_flows[df_flows['FCP'] == fcp_name].copy()
    
    # Calculate net flows (subscriptions - redemptions)
    df_fcp_flows['Montant_Signe'] = df_fcp_flows.apply(
        lambda x: x['Montant'] if x['Opérations'] == 'Souscriptions' else -x['Montant'],
        axis=1
    )
    
    # Aggregate by date
    daily_flows = df_fcp_flows.groupby('Date')['Montant_Signe'].sum()
    
    # Get actifs nets for the FCP
    df_actifs_fcp = df_actifs.set_index('Date')[fcp_name]
    
    # Align dates
    common_dates = df_actifs_fcp.index.intersection(daily_flows.index)
    
    if len(common_dates) < 2:
        return None, None, None
    
    actifs_aligned = df_actifs_fcp.loc[common_dates]
    flows_aligned = daily_flows.loc[common_dates]
    
    # Calculate correlation
    correlation = actifs_aligned.corr(flows_aligned)
    
    return correlation, actifs_aligned, flows_aligned


def calculate_vl_contribution(df_actifs, df_vl, fcp_name, date_range):
    """
    Calculate the contribution of VL performance vs flows to net assets change
    Returns: VL contribution (%), Flow contribution (%), correlation between VL and actifs
    """
    # Get the data for the FCP
    df_actifs_fcp = df_actifs.set_index('Date')[fcp_name]
    df_vl_fcp = df_vl.set_index('Date')[fcp_name]
    
    # Align dates
    common_dates = df_actifs_fcp.index.intersection(df_vl_fcp.index)
    
    if len(common_dates) < 2:
        return None, None, None
    
    actifs_aligned = df_actifs_fcp.loc[common_dates]
    vl_aligned = df_vl_fcp.loc[common_dates]
    
    # Calculate changes
    actifs_change = actifs_aligned.iloc[-1] - actifs_aligned.iloc[0]
    vl_perf = (vl_aligned.iloc[-1] / vl_aligned.iloc[0]) - 1
    
    # Estimate number of shares (assuming stable at start)
    shares_start = actifs_aligned.iloc[0] / vl_aligned.iloc[0]
    
    # VL contribution to actifs change (if shares stayed constant)
    vl_contribution_abs = shares_start * (vl_aligned.iloc[-1] - vl_aligned.iloc[0])
    
    # Calculate percentages
    if actifs_change != 0:
        vl_contribution_pct = (vl_contribution_abs / actifs_change) * 100
        flow_contribution_pct = 100 - vl_contribution_pct
    else:
        vl_contribution_pct = 0
        flow_contribution_pct = 0
    
    # Calculate correlation
    correlation = actifs_aligned.corr(vl_aligned)
    
    return vl_contribution_pct, flow_contribution_pct, correlation


def analyze_client_types(df_flows, selected_fcps, date_range):
    """
    Analyze subscription/redemption patterns by client type
    """
    # Ensure date_range values are pandas Timestamps
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])
    
    # Filter by date and FCPs
    df_filtered = df_flows[
        (df_flows['Date'] >= start_date) & 
        (df_flows['Date'] <= end_date) &
        (df_flows['FCP'].isin(selected_fcps))
    ].copy()
    
    # Calculate signed amounts
    df_filtered['Montant_Signe'] = df_filtered.apply(
        lambda x: x['Montant'] if x['Opérations'] == 'Souscriptions' else -x['Montant'],
        axis=1
    )
    
    # Group by client type
    client_analysis = df_filtered.groupby('Type de clients').agg({
        'Montant': 'sum',
        'Montant_Signe': 'sum'
    }).reset_index()
    
    # Separate subscriptions and redemptions
    subscriptions = df_filtered[df_filtered['Opérations'] == 'Souscriptions'].groupby('Type de clients')['Montant'].sum()
    redemptions = df_filtered[df_filtered['Opérations'] == 'Rachats'].groupby('Type de clients')['Montant'].sum()
    
    return client_analysis, subscriptions, redemptions


@st.cache_data
def analyze_seasonality(df, fcp_columns_tuple):
    """Analyze monthly and quarterly seasonality patterns"""
    df_copy = df.copy()
    fcp_columns = list(fcp_columns_tuple)  # Convert tuple back to list
    
    # Calculate monthly returns for each FCP
    monthly_data = {}
    quarterly_data = {}
    
    # Resample once for all FCPs
    df_monthly_all = df_copy.set_index('Date').resample('ME')[fcp_columns].last()
    df_quarterly_all = df_copy.set_index('Date').resample('QE')[fcp_columns].last()
    
    for fcp in fcp_columns:
        # Monthly analysis - more efficient approach
        df_monthly_returns = df_monthly_all[fcp].pct_change() * 100
        monthly_avg = df_monthly_returns.groupby(df_monthly_returns.index.month).mean()
        monthly_data[fcp] = monthly_avg
        
        # Quarterly analysis - more efficient approach
        df_quarterly_returns = df_quarterly_all[fcp].pct_change() * 100
        quarterly_avg = df_quarterly_returns.groupby(df_quarterly_returns.index.quarter).mean()
        quarterly_data[fcp] = quarterly_avg
    
    return monthly_data, quarterly_data


def main():
    """Main function for the Actifs Nets page"""
    st.header("💼 Analyse des Actifs Nets")
    
    try:
        # Load data
        with st.spinner('Chargement des données...'):
            df = load_actifs_nets_data()
            df_flows = load_souscriptions_rachats_data()
            df_vl = load_valeurs_liquidatives_data()
        
        # Get list of FCP columns (all columns except Date)
        fcp_columns = [col for col in df.columns if col != 'Date']
        
        # ===================
        # Sidebar Filters
        # ===================
        with st.sidebar:
            st.header("🔧 Filtres Intelligents")
            
            st.info("💡 Les filtres FCP sont disponibles dans chaque section d'analyse pour plus de flexibilité.")
        
        # Initialize selected_fcps with all FCPs by default
        selected_fcps = fcp_columns
        
        # Continue with sidebar filters
        with st.sidebar:
            # Date range filter
            with st.expander("📅 Période d'analyse", expanded=True):
                # Quick date filters
                quick_filter = st.radio(
                    "Filtres rapides",
                    options=['Personnalisé', 'WTD', 'MTD', 'QTD', 'YTD', 'Origine'],
                    index=5,
                    help="WTD: Semaine, MTD: Mois, QTD: Trimestre, YTD: Année, Origine: Depuis le début",
                    horizontal=True
                )
                
                # Calculate date range based on quick filter
                max_date = df['Date'].max()
                min_date = df['Date'].min()
                
                if quick_filter == 'WTD':
                    # Week to date - from Monday of current week
                    start_of_week = max_date - timedelta(days=max_date.weekday())
                    date_range = (start_of_week, max_date)
                elif quick_filter == 'MTD':
                    # Month to date - from 1st of current month
                    start_of_month = max_date.replace(day=1)
                    date_range = (start_of_month, max_date)
                elif quick_filter == 'QTD':
                    # Quarter to date - from 1st day of current quarter
                    current_quarter = (max_date.month - 1) // 3
                    start_of_quarter = max_date.replace(month=current_quarter * 3 + 1, day=1)
                    date_range = (start_of_quarter, max_date)
                elif quick_filter == 'YTD':
                    # Year to date - from January 1st of current year
                    start_of_year = max_date.replace(month=1, day=1)
                    date_range = (start_of_year, max_date)
                elif quick_filter == 'Origine':
                    # From the beginning of data
                    date_range = (min_date, max_date)
                else:
                    # Custom date range
                    date_range = st.date_input(
                        "Sélectionnez la période",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="actifs_nets_date_range"
                    )
                
                # Display selected date range
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    try:
                        st.caption(f"📅 Du {date_range[0].strftime('%d/%m/%Y')} au {date_range[1].strftime('%d/%m/%Y')}")
                    except (AttributeError, TypeError):
                        pass  # Skip display if dates are not valid
            
            # Visualization options
            with st.expander("🎨 Options de visualisation", expanded=False):
                # Aggregation period
                aggregation_period = st.selectbox(
                    "Période d'agrégation",
                    options=['Quotidien', 'Hebdomadaire', 'Mensuel', 'Trimestriel', 'Annuel'],
                    index=2,
                    help="Choisissez la fréquence d'affichage des données"
                )
            
            # Advanced filters
            with st.expander("⚙️ Filtres avancés", expanded=False):
                show_trend = st.checkbox("Afficher les lignes de tendance", value=True)
                show_ma = st.checkbox("Afficher moyennes mobiles", value=False)
                if show_ma:
                    ma_window = st.slider("Fenêtre moyenne mobile (jours)", 5, 90, 30)
                else:
                    ma_window = 30
                
                top_n = st.slider("Top N FCP pour les classements", 3, 10, 5)
            
            # Save/Load selections
            with st.expander("💾 Sauvegarder/Charger la Sélection", expanded=False):
                # Save current selection
                selection_name = st.text_input("Nom de la sélection", key="an_save_name")
                if st.button("💾 Sauvegarder la sélection actuelle", use_container_width=True, key="an_save_btn"):
                    if selection_name:
                        if 'an_saved_selections' not in st.session_state:
                            st.session_state.an_saved_selections = {}
                        st.session_state.an_saved_selections[selection_name] = selected_fcps.copy()
                        st.success(f"✅ Sélection '{selection_name}' sauvegardée!")
                    else:
                        st.warning("⚠️ Veuillez entrer un nom pour la sélection")
                
                # Load saved selection
                if 'an_saved_selections' in st.session_state and st.session_state.an_saved_selections:
                    saved_names = list(st.session_state.an_saved_selections.keys())
                    selected_save = st.selectbox("Charger une sélection", options=[""] + saved_names, key="an_load_select")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📂 Charger", use_container_width=True, key="an_load_btn") and selected_save:
                            st.session_state.an_selected_fcps = st.session_state.an_saved_selections[selected_save]
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Supprimer", use_container_width=True, key="an_delete_btn") and selected_save:
                            del st.session_state.an_saved_selections[selected_save]
                            st.rerun()
                else:
                    st.info("Aucune sélection sauvegardée")
        
        # Filter data by date range - handle edge cases
        if isinstance(date_range, tuple) and len(date_range) == 2:
            try:
                mask = (df['Date'] >= pd.Timestamp(date_range[0])) & (df['Date'] <= pd.Timestamp(date_range[1]))
                df_filtered = df[mask].copy()
            except (TypeError, ValueError):
                df_filtered = df.copy()
        else:
            df_filtered = df.copy()
        
        if df_filtered.empty:
            st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
            return
        
        # Map aggregation period to pandas frequency
        period_map = {
            'Quotidien': 'D',
            'Hebdomadaire': 'W',
            'Mensuel': 'M',
            'Trimestriel': 'Q',
            'Annuel': 'Y'
        }
        freq = period_map[aggregation_period]
        
        # ===================
        # Section 1: KPIs (moved to top)
        # ===================
        st.subheader("📊 Indicateurs Clés de Performance")
        
        # Calculate totals for ALL FCPs - with safety checks
        try:
            total_all_fcps_current = df_filtered[fcp_columns].iloc[-1].fillna(0).sum()
            total_all_fcps_start = df_filtered[fcp_columns].iloc[0].fillna(0).sum()
            if total_all_fcps_start > 0 and not pd.isna(total_all_fcps_start):
                growth_rate_all = ((total_all_fcps_current / total_all_fcps_start) - 1) * 100
            else:
                growth_rate_all = 0
            
            # Calculate totals for SELECTED FCPs
            total_actifs_current = df_filtered[selected_fcps].iloc[-1].fillna(0).sum()
            total_actifs_start = df_filtered[selected_fcps].iloc[0].fillna(0).sum()
            if total_actifs_start > 0 and not pd.isna(total_actifs_start):
                growth_rate = ((total_actifs_current / total_actifs_start) - 1) * 100
            else:
                growth_rate = 0
            
            # Calculate share of selected FCPs
            if total_all_fcps_current > 0 and not pd.isna(total_all_fcps_current):
                share_selected = (total_actifs_current / total_all_fcps_current) * 100
            else:
                share_selected = 0
            
            # Handle NaN values
            total_all_fcps_current = 0 if pd.isna(total_all_fcps_current) else total_all_fcps_current
            total_actifs_current = 0 if pd.isna(total_actifs_current) else total_actifs_current
            growth_rate_all = 0 if pd.isna(growth_rate_all) else growth_rate_all
            growth_rate = 0 if pd.isna(growth_rate) else growth_rate
            share_selected = 0 if pd.isna(share_selected) else share_selected
        except IndexError:
            st.error("⚠️ Données insuffisantes pour calculer les indicateurs")
            return
        
        # Calculate volatility for each FCP to find the most volatile
        volatility_data = []
        for fcp in fcp_columns:
            returns = df_filtered[fcp].pct_change().dropna() * 100
            if len(returns) > 1:  # Need at least 2 points for std
                volatility = returns.std()
                if not pd.isna(volatility):  # Only add if not NaN
                    volatility_data.append({
                        'FCP': fcp,
                        'Volatilité': volatility
                    })
        
        # Find most volatile FCP
        most_volatile_fcp = None
        most_volatile_value = 0
        if volatility_data:
            try:
                most_volatile = max(volatility_data, key=lambda x: x['Volatilité'])
                most_volatile_fcp = most_volatile['FCP']
                most_volatile_value = most_volatile['Volatilité']
            except (ValueError, KeyError):
                pass  # Keep default values if error occurs
        
        # Find largest FCP by net assets
        largest_fcp = None
        largest_fcp_amount = 0
        largest_fcp_pct = 0
        current_values = df_filtered[fcp_columns].iloc[-1].fillna(0)
        if len(current_values) > 0 and total_all_fcps_current > 0:
            try:
                # Filter out NaN and zero values
                valid_values = current_values[current_values > 0]
                if len(valid_values) > 0:
                    largest_fcp = valid_values.idxmax()
                    largest_fcp_amount = valid_values.max()
                    largest_fcp_pct = (largest_fcp_amount / total_all_fcps_current) * 100
            except (ValueError, KeyError):
                pass  # Keep default values if error occurs
        
        # Display global indicators in three columns
        col1, col2, col3 = st.columns(3)
        
        # Calculate display values
        total_all_m = total_all_fcps_current/1e6
        emoji_all = '🟢' if growth_rate_all >= 0 else '🔴'
        num_fcps = len(fcp_columns)
        
        with col1:
            st.markdown(f"""
            <div class="ranking-card">
                <h3>💰 Actifs Nets Totaux</h3>
                <div class="ranking-item">
                    <span>Montant Total</span>
                    <span class="ranking-value">{total_all_m:.2f}M FCFA</span>
                </div>
                <div class="ranking-item">
                    <span>Croissance Période</span>
                    <span class="ranking-value">{emoji_all} {growth_rate_all:+.2f}%</span>
                </div>
                <div class="ranking-item">
                    <span>Nombre de FCP</span>
                    <span class="ranking-value">{num_fcps}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Most volatile FCP card
            st.markdown(f"""
            <div class="ranking-card">
                <h3>📊 FCP le Plus Volatil</h3>
                <div class="ranking-item">
                    <span>FCP</span>
                    <span class="ranking-value" style="font-size: 0.85rem;">{most_volatile_fcp if most_volatile_fcp else 'N/A'}</span>
                </div>
                <div class="ranking-item">
                    <span>Volatilité</span>
                    <span class="ranking-value">{most_volatile_value:.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Largest FCP by net assets
            largest_fcp_m = largest_fcp_amount / 1e6
            
            st.markdown(f"""
            <div class="ranking-card">
                <h3>💼 FCP le Plus Important</h3>
                <div class="ranking-item">
                    <span>FCP</span>
                    <span class="ranking-value" style="font-size: 0.85rem;">{largest_fcp if largest_fcp else 'N/A'}</span>
                </div>
                <div class="ranking-item">
                    <span>Actifs Nets</span>
                    <span class="ranking-value">{largest_fcp_m:.2f}M FCFA</span>
                </div>
                <div class="ranking-item">
                    <span>Part du Total</span>
                    <span class="ranking-value">{largest_fcp_pct:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===================
        # Section 2: Temporal Evolution
        # ===================
        st.subheader("📈 Évolution Temporelle des Actifs Nets")
        
        st.markdown("""
        <div class="interpretation-note">
            <strong>💡 Note:</strong> Ce graphique utilise toutes les données disponibles, indépendamment du filtre de période sélectionné dans la barre latérale.
            Vous pouvez choisir la période, le mode de visualisation et les FCP à afficher ci-dessous.
        </div>
        """, unsafe_allow_html=True)
        
        # FCP selection for evolution graph
        st.markdown("##### 🎯 Sélection des FCP à afficher")
        col_fcp1, col_fcp2 = st.columns([4, 1])
        
        with col_fcp1:
            evolution_selected_fcps = st.multiselect(
                "Choisir les FCP pour le graphique d'évolution",
                options=fcp_columns,
                default=fcp_columns,
                key="evolution_fcp_selector",
                help="Sélectionnez un ou plusieurs FCP à visualiser dans le graphique d'évolution"
            )
        
        with col_fcp2:
            if st.button("Tout sélectionner", key="select_all_evolution"):
                st.session_state.evolution_fcp_selector = fcp_columns
                st.rerun()
        
        # Period selection and mode for AN graph - independent of sidebar
        col1, col2 = st.columns([3, 1])
        
        with col1:
            an_period = st.radio(
                "Sélectionnez la période d'affichage",
                options=['1M', '3M', '6M', '1A', 'Tout'],
                index=4,
                horizontal=True,
                key="an_period_selector",
                help="Choisissez la période à visualiser"
            )
        
        with col2:
            an_mode = st.radio(
                "Mode",
                options=['Absolue', 'Base 100', 'Variation %'],
                index=0,
                key="an_mode_selector",
                help="Absolue: valeurs réelles | Base 100: normalisation | Variation %: croissance en pourcentage"
            )
        
        # Use df directly (no need to copy since we're not modifying the original)
        # Filter data based on period selection (from full data, not filtered_df)
        max_date = df['Date'].max()
        
        if an_period == '1M':
            start_date = max_date - timedelta(days=30)
        elif an_period == '3M':
            start_date = max_date - timedelta(days=90)
        elif an_period == '6M':
            start_date = max_date - timedelta(days=180)
        elif an_period == '1A':
            start_date = max_date - timedelta(days=365)
        else:  # 'Tout'
            start_date = df['Date'].min()
        
        # Filter data based on period (from full dataset, independent of sidebar filters)
        an_plot_df = df[df['Date'] >= start_date].copy()
        
        # Check if we have data to display
        if an_plot_df.empty:
            st.warning("⚠️ Aucune donnée disponible pour la période sélectionnée.")
        elif not evolution_selected_fcps:
            st.info("📌 Sélectionnez au moins un FCP pour afficher le graphique.")
        else:
            # Prepare data based on display mode
            if an_mode == 'Base 100':
                # Normalize to base 100
                df_plot = an_plot_df.copy()
                for col in evolution_selected_fcps:
                    if len(df_plot) > 0 and df_plot[col].iloc[0] != 0 and not pd.isna(df_plot[col].iloc[0]):
                        df_plot[col] = (df_plot[col] / df_plot[col].iloc[0]) * 100
                    else:
                        # If first value is 0 or NaN, set entire column to NaN to avoid misleading visualization
                        df_plot[col] = np.nan
                y_label = "Valeur (base 100)"
            elif an_mode == 'Variation %':
                # Calculate percentage change
                df_plot = an_plot_df.copy()
                for col in evolution_selected_fcps:
                    if len(df_plot) > 0 and df_plot[col].iloc[0] != 0 and not pd.isna(df_plot[col].iloc[0]):
                        df_plot[col] = ((df_plot[col] / df_plot[col].iloc[0]) - 1) * 100
                    else:
                        # If first value is 0 or NaN, set entire column to NaN to avoid misleading visualization
                        df_plot[col] = np.nan
                y_label = "Variation (%)"
            else:  # Absolue
                df_plot = an_plot_df.copy()
                y_label = "Actifs Nets (FCFA)"
            
            # Create figure
            fig_evolution = go.Figure()
            
            for fcp in evolution_selected_fcps:
                # Skip columns that are all NaN
                if not df_plot[fcp].isna().all():
                    fig_evolution.add_trace(go.Scatter(
                        x=df_plot['Date'],
                        y=df_plot[fcp],
                        name=fcp,
                        mode='lines',
                        line=dict(width=2),
                        hovertemplate='%{data.name}<br>Date: %{x}<br>Valeur: %{y:,.2f}<extra></extra>'
                    ))
                    
                    # Add moving average if requested
                    if show_ma and an_mode == 'Absolue':
                        ma_values = df_plot[fcp].rolling(window=min(ma_window, len(df_plot))).mean()
                        if not ma_values.isna().all():
                            fig_evolution.add_trace(go.Scatter(
                                x=df_plot['Date'],
                                y=ma_values,
                                name=f'{fcp} (MA{ma_window})',
                                mode='lines',
                                line=dict(width=1, dash='dash'),
                                opacity=0.5,
                                hovertemplate='%{data.name}<br>Date: %{x}<br>MA: %{y:,.2f}<extra></extra>'
                            ))
            
            fig_evolution.update_layout(
                title=f"Évolution des Actifs Nets - {an_mode} - {an_period}",
                xaxis_title="Date",
                yaxis_title=y_label,
                height=500,
                template="plotly_white",
                hovermode='x unified',
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            
            st.plotly_chart(fig_evolution, use_container_width=True)
        
        # ===================
        # Section 3: Distribution par FCP
        # ===================
        st.subheader("📊 Répartition des Actifs Nets par FCP")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart - current distribution
            current_values = df_filtered[selected_fcps].iloc[-1]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=current_values.index,
                values=current_values.values,
                hole=0.4,
                textposition='auto',
                textinfo='label+percent',
                hovertemplate='%{label}<br>Actifs: %{value:,.0f}FCFA<br>Part: %{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title=f"Répartition Actuelle ({df_filtered['Date'].iloc[-1].strftime('%Y-%m-%d')})",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart - comparison current vs start
            start_values = df_filtered[selected_fcps].iloc[0]
            current_values = df_filtered[selected_fcps].iloc[-1]
            
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                name='Début période',
                x=selected_fcps,
                y=start_values.values,
                marker_color='lightblue',
                text=(start_values.values / 1e6).round(1).astype(str) + 'M',
                textposition='outside'
            ))
            
            fig_bar.add_trace(go.Bar(
                name='Fin période',
                x=selected_fcps,
                y=current_values.values,
                marker_color='darkblue',
                text=(current_values.values / 1e6).round(1).astype(str) + 'M',
                textposition='outside'
            ))
            
            fig_bar.update_layout(
                title="Comparaison Début vs Fin de Période",
                xaxis_title="FCP",
                yaxis_title="Actifs Nets (FCFA)",
                height=400,
                template="plotly_white",
                barmode='group'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # ===================
        # Section 4: Advanced Analyses with Tabs
        # ===================
        st.subheader("📈 Analyses Avancées")
        
        # Calculate growth_data once for use in both tabs and rankings section
        growth_data = []
        for fcp in selected_fcps:
            series = df_filtered[fcp].dropna()
            if len(series) >= 2:
                start_val = series.iloc[0]
                end_val = series.iloc[-1]
                growth = ((end_val / start_val) - 1) * 100
                
                # Calculate CAGR if period is long enough
                days = (df_filtered['Date'].iloc[-1] - df_filtered['Date'].iloc[0]).days
                if days > 0:
                    years = days / 365.25
                    cagr = (((end_val / start_val) ** (1 / years)) - 1) * 100
                else:
                    cagr = 0
                
                growth_data.append({
                    'FCP': fcp,
                    'Début': start_val,
                    'Fin': end_val,
                    'Croissance (%)': growth,
                    'CAGR (%)': cagr
                })
        
        # Use tabs to organize multiple analyses
        tab1, tab2, tab3, tab4 = st.tabs([
            "📉 Analyse de Volatilité et Risque",
            "📊 Statistiques Avancées", 
            "💼 Contribution VL vs Flux",
            "👥 Analyse par Type de Clients"
        ])
        
        # ===================
        # TAB 1: Volatility and Risk Analysis
        # ===================
        # ===================
        # TAB 1: Volatility and Risk Analysis
        # ===================
        with tab1:
            st.markdown("""
            <div class="interpretation-note">
                <strong>💡 Note de Synthèse:</strong> Cette analyse se concentre sur la volatilité et le risque des actifs nets. 
                La volatilité indique la stabilité, tandis que le ratio rendement/risque permet d'identifier les FCP offrant le meilleur compromis.
            </div>
            """, unsafe_allow_html=True)
            
            # Add FCP selector for this tab
            st.markdown("##### 🎯 Sélection des FCP pour l'Analyse")
            col_fcp1, col_fcp2 = st.columns([3, 1])
            with col_fcp1:
                tab1_selected_fcps = st.multiselect(
                    "Choisir les FCP à analyser dans cet onglet",
                    options=selected_fcps,
                    default=selected_fcps,
                    key="tab1_fcp_selector",
                    label_visibility="collapsed",
                    help="Sélectionnez les FCP à comparer pour la volatilité et le risque"
                )
            with col_fcp2:
                compare_all = st.checkbox("Comparer au Total", value=False, key="tab1_compare_all",
                                         help="Afficher la moyenne de tous les FCP")
            
            if not tab1_selected_fcps:
                st.info("📌 Sélectionnez au moins un FCP pour afficher l'analyse")
            else:
                
                # Calculate volatility for selected FCPs
                volatility_data = []
                for fcp in tab1_selected_fcps:
                    returns = df_filtered[fcp].pct_change().dropna() * 100
                    if len(returns) > 0:
                        vol = returns.std()
                        mean_ret = returns.mean()
                        volatility_data.append({
                            'FCP': fcp,
                            'Volatilité (%)': vol,
                            'Rendement Moyen (%)': mean_ret,
                            'Ratio Rendement/Risque': mean_ret / vol if vol > 0 else 0
                        })
                
                df_volatility = pd.DataFrame(volatility_data).sort_values('Volatilité (%)', ascending=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Volatility bar chart
                    st.markdown("##### Volatilité par FCP")
                    
                    fig_volatility = go.Figure()
                    fig_volatility.add_trace(go.Bar(
                        x=df_volatility['FCP'],
                        y=df_volatility['Volatilité (%)'],
                        name='Volatilité',
                        marker_color='orange',
                        text=df_volatility['Volatilité (%)'].round(2).astype(str) + '%',
                        textposition='outside'
                    ))
                    
                    fig_volatility.update_layout(
                        title="Volatilité des Actifs Nets",
                        xaxis_title="FCP",
                        yaxis_title="Volatilité (%)",
                        height=350,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_volatility, use_container_width=True, key="tab1_volatility_bar")
                
                with col2:
                    # Ratio Rendement/Risque bar chart
                    st.markdown("##### Ratio Rendement/Risque")
                    
                    df_ratio_sorted = df_volatility.sort_values('Ratio Rendement/Risque', ascending=False)
                    colors_ratio = ['green' if x >= 0 else 'red' for x in df_ratio_sorted['Ratio Rendement/Risque']]
                    
                    fig_ratio = go.Figure()
                    fig_ratio.add_trace(go.Bar(
                        x=df_ratio_sorted['FCP'],
                        y=df_ratio_sorted['Ratio Rendement/Risque'],
                        marker_color=colors_ratio,
                        text=df_ratio_sorted['Ratio Rendement/Risque'].round(3).astype(str),
                        textposition='outside'
                    ))
                    
                    fig_ratio.update_layout(
                        title="Ratio Rendement/Risque par FCP",
                        xaxis_title="FCP",
                        yaxis_title="Ratio",
                        height=350,
                        template="plotly_white",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_ratio, use_container_width=True, key="tab1_ratio_bar")
                
                # === ADDITIONAL RISK ANALYSES ===
                st.markdown("##### 📉 Analyses Complémentaires de Risque")
                
                # Calculate drawdowns and additional risk metrics
                drawdown_data = []
                risk_metrics = []
                
                for fcp in tab1_selected_fcps:
                    series = df_filtered[fcp].dropna()
                    if len(series) > 0:
                        # Calculate running maximum
                        running_max = series.expanding().max()
                        # Calculate drawdown
                        drawdown = (series - running_max) / running_max * 100
                        max_drawdown = drawdown.min()
                        
                        # Calculate daily returns for additional metrics
                        returns = series.pct_change().dropna() * 100
                        
                        # Downside deviation (volatility of negative returns)
                        negative_returns = returns[returns < 0]
                        downside_vol = negative_returns.std() if len(negative_returns) > 0 else 0
                        
                        # Value at Risk (95% confidence)
                        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
                        
                        drawdown_data.append({
                            'FCP': fcp,
                            'Max Drawdown (%)': max_drawdown,
                            'Drawdown Series': drawdown
                        })
                        
                        risk_metrics.append({
                            'FCP': fcp,
                            'Max Drawdown (%)': max_drawdown,
                            'Downside Volatility (%)': downside_vol,
                            'VaR 95% (%)': var_95
                        })
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Max Drawdown bar chart
                    st.markdown("###### Drawdown Maximum par FCP")
                    
                    if risk_metrics:
                        df_drawdown = pd.DataFrame(risk_metrics).sort_values('Max Drawdown (%)')
                        
                        fig_drawdown = go.Figure()
                        fig_drawdown.add_trace(go.Bar(
                            x=df_drawdown['FCP'],
                            y=df_drawdown['Max Drawdown (%)'],
                            marker_color='red',
                            text=df_drawdown['Max Drawdown (%)'].round(2).astype(str) + '%',
                            textposition='outside'
                        ))
                        
                        fig_drawdown.update_layout(
                            title="Plus Grande Baisse (Drawdown)",
                            xaxis_title="FCP",
                            yaxis_title="Max Drawdown (%)",
                            height=350,
                            template="plotly_white",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_drawdown, use_container_width=True, key="tab1_drawdown_bar")
                        
                        st.markdown("""
                        **💡 Interprétation:** Le Max Drawdown mesure la plus grande perte depuis un sommet. 
                        Un drawdown important indique un risque de perte élevé pendant les périodes difficiles.
                        """)
                
                with col2:
                    # Risk metrics table
                    st.markdown("###### Métriques de Risque Avancées")
                    
                    if risk_metrics:
                        df_risk_metrics = pd.DataFrame(risk_metrics)
                        df_risk_display = df_risk_metrics.copy()
                        df_risk_display['Max Drawdown (%)'] = df_risk_display['Max Drawdown (%)'].round(2)
                        df_risk_display['Downside Volatility (%)'] = df_risk_display['Downside Volatility (%)'].round(2)
                        df_risk_display['VaR 95% (%)'] = df_risk_display['VaR 95% (%)'].round(2)
                        
                        st.dataframe(
                            df_risk_display.style.background_gradient(
                                subset=['Max Drawdown (%)', 'VaR 95% (%)'], 
                                cmap='RdYlGn_r'
                            ).background_gradient(
                                subset=['Downside Volatility (%)'], 
                                cmap='RdYlGn_r'
                            ),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        st.markdown("""
                        **💡 Légende:**
                        - **Downside Vol.:** Volatilité des rendements négatifs uniquement
                        - **VaR 95%:** Perte maximale probable dans 95% des cas (sur une journée)
                        """)
                
                # Drawdown evolution over time for best/worst FCP
                if drawdown_data and len(drawdown_data) >= 2:
                    st.markdown("###### 📉 Évolution des Drawdowns dans le Temps")
                    
                    # Select FCP with best and worst max drawdown
                    df_dd = pd.DataFrame(risk_metrics).sort_values('Max Drawdown (%)')
                    worst_dd_fcp = df_dd.iloc[0]['FCP']
                    best_dd_fcp = df_dd.iloc[-1]['FCP']
                    
                    fig_dd_evolution = go.Figure()
                    
                    for dd_item in drawdown_data:
                        if dd_item['FCP'] in [worst_dd_fcp, best_dd_fcp]:
                            fig_dd_evolution.add_trace(go.Scatter(
                                x=df_filtered['Date'],
                                y=dd_item['Drawdown Series'],
                                name=dd_item['FCP'],
                                mode='lines',
                                line=dict(width=2),
                                hovertemplate='%{data.name}<br>Date: %{x}<br>Drawdown: %{y:.2f}%<extra></extra>'
                            ))
                    
                    fig_dd_evolution.update_layout(
                        title=f"Évolution des Drawdowns - Meilleur vs Pire",
                        xaxis_title="Date",
                        yaxis_title="Drawdown (%)",
                        height=400,
                        template="plotly_white",
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_dd_evolution, use_container_width=True, key="tab1_dd_evolution")
                    
                    st.markdown("""
                    **📊 Analyse:** Ce graphique montre comment les pertes depuis les sommets évoluent dans le temps. 
                    Des périodes prolongées de drawdown élevé suggèrent des difficultés à récupérer les pertes.
                    """)
        
        # ===================
        # TAB 2: Advanced Statistics
        # ===================
        with tab2:
            st.markdown("""
            <div class="interpretation-note">
                <strong>💡 Note:</strong> Cette section présente des statistiques approfondies sur les actifs nets,
                incluant résumés statistiques, distribution des valeurs, et corrélations avec les flux.
            </div>
            """, unsafe_allow_html=True)
            
            # === STATISTICAL SUMMARY ===
            st.markdown("#### 📊 Résumé Statistique")
            
            stats_data = []
            for fcp in selected_fcps:
                series = df_filtered[fcp].dropna()
                if len(series) > 0:
                    stats_data.append({
                        'FCP': fcp,
                        'Moyenne': series.mean(),
                        'Médiane': series.median(),
                        'Écart-type': series.std(),
                        'Min': series.min(),
                        'Max': series.max()
                    })
            
            df_stats = pd.DataFrame(stats_data)
            df_stats_display = df_stats.copy()
            for col in ['Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max']:
                df_stats_display[col] = (df_stats_display[col] / 1e6).round(2).astype(str) + 'M FCFA'
            
            st.dataframe(df_stats_display, use_container_width=True, hide_index=True)
            
            # === DISTRIBUTION ANALYSIS ===
            st.markdown("#### 📈 Graphique de Distribution des Actifs Nets")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Box plot distribution
                st.markdown("##### Distribution par FCP (Box Plot)")
                
                fig_box = go.Figure()
                
                for fcp in selected_fcps:
                    fig_box.add_trace(go.Box(
                        y=df_filtered[fcp],
                        name=fcp,
                        boxmean='sd'
                    ))
                
                fig_box.update_layout(
                    title="Distribution des Valeurs par FCP",
                    yaxis_title="Actifs Nets (FCFA)",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_box, use_container_width=True, key="tab2_box_plot")
            
            with col2:
                # Histogram for a selected FCP
                st.markdown("##### Distribution pour un FCP sélectionné")
                
                tab2_fcp_for_hist = st.selectbox(
                    "Choisir un FCP",
                    options=selected_fcps,
                    key="tab2_hist_fcp",
                    help="Sélectionnez un FCP pour voir sa distribution en histogramme"
                )
                
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Histogram(
                    x=df_filtered[tab2_fcp_for_hist],
                    nbinsx=30,
                    name=tab2_fcp_for_hist,
                    marker_color=PRIMARY_COLOR
                ))
                
                fig_hist.update_layout(
                    title=f"Distribution - {tab2_fcp_for_hist}",
                    xaxis_title="Actifs Nets (FCFA)",
                    yaxis_title="Fréquence",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_hist, use_container_width=True, key="tab2_histogram")
            
            # === CORRELATION WITH FLOWS ===
            st.markdown("#### 🔗 Corrélation avec Souscriptions et Achats")
            
            st.markdown("""
            <div class="interpretation-note">
                <strong>💡</strong> Analyse de la relation entre actifs nets et flux de souscriptions/rachats.
                Une forte corrélation positive suggère que les variations sont principalement dues aux flux d'investisseurs.
            </div>
            """, unsafe_allow_html=True)
            
            # Select FCP for detailed analysis
            tab2_fcp_for_flow = st.selectbox(
                "Sélectionnez un FCP pour l'analyse de corrélation",
                options=selected_fcps,
                key="tab2_flow_fcp",
                help="Choisissez un FCP pour voir sa corrélation avec les flux"
            )
            
            # Calculate correlation
            correlation, actifs_aligned, flows_aligned = calculate_correlation_with_flows(
                df_filtered, 
                df_flows[df_flows['Date'].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))],
                tab2_fcp_for_flow,
                date_range
            )
            
            if correlation is not None:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric(
                        "Coefficient de Corrélation",
                        f"{correlation:.3f}",
                        help="Corrélation entre actifs nets et flux nets quotidiens"
                    )
                    
                    # Interpretation
                    if abs(correlation) > 0.7:
                        st.success("✅ Corrélation forte")
                    elif abs(correlation) > 0.4:
                        st.info("ℹ️ Corrélation modérée")
                    else:
                        st.warning("⚠️ Corrélation faible")
                
                with col2:
                    # Scatter plot
                    fig_scatter = go.Figure()
                    
                    fig_scatter.add_trace(go.Scatter(
                        x=flows_aligned,
                        y=actifs_aligned,
                        mode='markers',
                        marker=dict(size=8, opacity=0.6, color=PRIMARY_COLOR),
                        name='Observations',
                        hovertemplate='Flux: %{x:,.0f}FCFA<br>Actifs: %{y:,.0f}FCFA<extra></extra>'
                    ))
                    
                    fig_scatter.update_layout(
                        title=f"Relation Actifs Nets vs Flux Nets - {tab2_fcp_for_flow}",
                        xaxis_title="Flux Net Quotidien (FCFA)",
                        yaxis_title="Actifs Nets (FCFA)",
                        height=350,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_scatter, use_container_width=True, key="tab2_scatter")
            else:
                st.info("Pas assez de données pour calculer la corrélation pour ce FCP.")
        
        # ===================
        # TAB 3: VL Performance Contribution
        # ===================
        with tab3:
            st.markdown("""
            <div class="interpretation-note">
                <strong>💡 Note de Synthèse:</strong> Cette analyse décompose l'évolution des actifs nets en deux composantes :
                <ul>
                    <li><strong>Performance VL:</strong> La contribution de la variation de la valeur liquidative</li>
                    <li><strong>Flux nets:</strong> La contribution des souscriptions et rachats</li>
                </ul>
                Comprendre ces deux sources de variation permet d'identifier si la croissance du fonds provient 
                principalement de bonnes performances ou de l'attractivité commerciale.
            </div>
            """, unsafe_allow_html=True)
            
            # Select FCP for VL contribution analysis
            fcp_for_vl_analysis = st.selectbox(
                "Sélectionnez un FCP pour l'analyse de contribution VL",
                options=selected_fcps,
                key="vl_contrib_fcp",
                help="Choisissez un FCP pour voir la décomposition de ses variations d'actifs"
            )
            
            # Calculate VL contribution
            vl_df_filtered = df_vl[
                (df_vl['Date'] >= pd.Timestamp(date_range[0])) & 
                (df_vl['Date'] <= pd.Timestamp(date_range[1]))
            ]
            
            vl_contrib_pct, flow_contrib_pct, vl_correlation = calculate_vl_contribution(
                df_filtered,
                vl_df_filtered,
                fcp_for_vl_analysis,
                date_range
            )
            
            if vl_contrib_pct is not None:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Contribution Performance VL",
                        f"{vl_contrib_pct:.1f}%",
                        help="Part de la variation d'actifs due à la performance de la VL"
                    )
                
                with col2:
                    st.metric(
                        "Contribution Flux Nets",
                        f"{flow_contrib_pct:.1f}%",
                        help="Part de la variation d'actifs due aux flux de souscriptions/rachats"
                    )
                
                with col3:
                    st.metric(
                        "Corrélation VL-Actifs",
                        f"{vl_correlation:.3f}",
                        help="Corrélation entre la VL et les actifs nets"
                    )
                
                # Visualization: Pie chart of contributions
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig_contrib = go.Figure(data=[go.Pie(
                        labels=['Performance VL', 'Flux Nets'],
                        values=[max(0, vl_contrib_pct), max(0, flow_contrib_pct)],
                        hole=0.4,
                        marker=dict(colors=['#114B80', '#567389']),
                        textposition='auto',
                        textinfo='label+percent',
                        hovertemplate='%{label}<br>Contribution: %{value:.1f}%<extra></extra>'
                    )])
                    
                    fig_contrib.update_layout(
                        title=f"Décomposition de la Variation d'Actifs - {fcp_for_vl_analysis}",
                        height=400,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_contrib, use_container_width=True, key="tab3_pie")
                
                with col2:
                    # Interpretation based on contributions
                    if abs(vl_contrib_pct) > 70:
                        st.markdown("""
                        <div class="insight-box">
                            <h4>📈 Performance Dominante</h4>
                            <p>La variation des actifs nets est principalement due à la performance de la VL. 
                            Le fonds génère de la valeur par ses investissements.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif abs(flow_contrib_pct) > 70:
                        st.markdown("""
                        <div class="insight-box">
                            <h4>💰 Flux Dominants</h4>
                            <p>La variation des actifs nets est principalement due aux flux de souscriptions/rachats. 
                            L'attractivité commerciale du fonds est le facteur clé.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="insight-box">
                            <h4>⚖️ Contributions Équilibrées</h4>
                            <p>Les variations d'actifs résultent d'un mélange équilibré entre performance VL et flux nets.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Comparative analysis for all selected FCPs
                st.markdown("##### Comparaison Multi-FCP")
                
                vl_contrib_data = []
                for fcp in selected_fcps:
                    vl_c, flow_c, corr = calculate_vl_contribution(df_filtered, vl_df_filtered, fcp, date_range)
                    if vl_c is not None:
                        vl_contrib_data.append({
                            'FCP': fcp,
                            'Contrib. VL (%)': vl_c,
                            'Contrib. Flux (%)': flow_c,
                            'Corrélation': corr
                        })
                
                if vl_contrib_data:
                    df_vl_contrib = pd.DataFrame(vl_contrib_data)
                    
                    # Stacked bar chart
                    fig_contrib_compare = go.Figure()
                    
                    fig_contrib_compare.add_trace(go.Bar(
                        name='Performance VL',
                        x=df_vl_contrib['FCP'],
                        y=df_vl_contrib['Contrib. VL (%)'],
                        marker_color='#114B80',
                        text=df_vl_contrib['Contrib. VL (%)'].round(1).astype(str) + '%',
                        textposition='inside'
                    ))
                    
                    fig_contrib_compare.add_trace(go.Bar(
                        name='Flux Nets',
                        x=df_vl_contrib['FCP'],
                        y=df_vl_contrib['Contrib. Flux (%)'],
                        marker_color='#567389',
                        text=df_vl_contrib['Contrib. Flux (%)'].round(1).astype(str) + '%',
                        textposition='inside'
                    ))
                    
                    fig_contrib_compare.update_layout(
                        title="Contributions VL vs Flux par FCP",
                        xaxis_title="FCP",
                        yaxis_title="Contribution (%)",
                        barmode='stack',
                        height=400,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_contrib_compare, use_container_width=True, key="tab3_bar")
                    
                    # Display table
                    df_vl_contrib_display = df_vl_contrib.copy()
                    df_vl_contrib_display['Contrib. VL (%)'] = df_vl_contrib_display['Contrib. VL (%)'].round(2)
                    df_vl_contrib_display['Contrib. Flux (%)'] = df_vl_contrib_display['Contrib. Flux (%)'].round(2)
                    df_vl_contrib_display['Corrélation'] = df_vl_contrib_display['Corrélation'].round(3)
                    
                    st.dataframe(df_vl_contrib_display, use_container_width=True, hide_index=True)
            else:
                st.info("Pas assez de données pour calculer les contributions VL pour ce FCP sur la période sélectionnée.")
        
        # ===================
        # TAB 4: Client Type Analysis
        # ===================
        with tab4:
            st.markdown("""
            <div class="interpretation-note">
                <strong>💡 Note de Synthèse:</strong> Cette analyse combine les données de flux (Souscriptions/Rachats) 
                avec les actifs nets pour comprendre quels types de clients contribuent le plus aux variations. 
                Identifier les segments clés permet d'adapter les stratégies commerciales et de gestion.
            </div>
            """, unsafe_allow_html=True)
            
            # Analyze client types
            client_analysis, subscriptions, redemptions = analyze_client_types(
                df_flows,
                selected_fcps,
                date_range
            )
            
            if not client_analysis.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart of net flows by client type
                    fig_client_pie = go.Figure(data=[go.Pie(
                        labels=client_analysis['Type de clients'],
                        values=client_analysis['Montant_Signe'].abs(),
                        hole=0.4,
                        textposition='auto',
                        textinfo='label+percent',
                        hovertemplate='%{label}<br>Flux Net: %{value:,.0f}FCFA<extra></extra>'
                    )])
                    
                    fig_client_pie.update_layout(
                        title="Répartition des Flux Nets par Type de Client",
                        height=400,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_client_pie, use_container_width=True, key="tab4_pie")
                
                with col2:
                    # Bar chart comparing subscriptions vs redemptions
                    fig_client_bar = go.Figure()
                    
                    client_types = subscriptions.index.union(redemptions.index)
                    
                    fig_client_bar.add_trace(go.Bar(
                        name='Souscriptions',
                        x=client_types,
                        y=[subscriptions.get(ct, 0) for ct in client_types],
                        marker_color='green',
                        text=[(subscriptions.get(ct, 0) / 1e6).round(1) if subscriptions.get(ct, 0) > 0 else 0 for ct in client_types],
                        texttemplate='%{text}M',
                        textposition='outside'
                    ))
                    
                    fig_client_bar.add_trace(go.Bar(
                        name='Rachats',
                        x=client_types,
                        y=[redemptions.get(ct, 0) for ct in client_types],
                        marker_color='red',
                        text=[(redemptions.get(ct, 0) / 1e6).round(1) if redemptions.get(ct, 0) > 0 else 0 for ct in client_types],
                        texttemplate='%{text}M',
                        textposition='outside'
                    ))
                    
                    fig_client_bar.update_layout(
                        title="Souscriptions vs Rachats par Type de Client",
                        xaxis_title="Type de Client",
                        yaxis_title="Montant (FCFA)",
                        height=400,
                        template="plotly_white",
                        barmode='group'
                    )
                    
                    st.plotly_chart(fig_client_bar, use_container_width=True, key="tab4_bar")
                
                # Detailed table
                st.markdown("##### Détails par Type de Client")
                
                df_client_display = client_analysis.copy()
                df_client_display['Souscriptions'] = df_client_display['Type de clients'].map(
                    lambda x: subscriptions.get(x, 0)
                )
                df_client_display['Rachats'] = df_client_display['Type de clients'].map(
                    lambda x: redemptions.get(x, 0)
                )
                df_client_display = df_client_display[['Type de clients', 'Souscriptions', 'Rachats', 'Montant_Signe']]
                df_client_display.columns = ['Type de Client', 'Souscriptions', 'Rachats', 'Flux Net']
                
                # Format values
                for col in ['Souscriptions', 'Rachats', 'Flux Net']:
                    df_client_display[col] = (df_client_display[col] / 1e6).round(2).astype(str) + 'M FCFA'
                
                st.dataframe(df_client_display, use_container_width=True, hide_index=True)
                
                # Key insights
                if len(client_analysis) > 0:
                    dominant_client = client_analysis.loc[client_analysis['Montant_Signe'].abs().idxmax(), 'Type de clients']
                    dominant_amount = client_analysis.loc[client_analysis['Montant_Signe'].abs().idxmax(), 'Montant_Signe']
                    dominant_amount_m = abs(dominant_amount)/1e6
                    flux_type = 'positif' if dominant_amount > 0 else 'négatif'
                    recommandation = 'Renforcer les actions commerciales vers ce segment porteur.' if dominant_amount > 0 else 'Analyser les causes de rachats et mettre en place des actions de rétention.'
                    
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>🎯 Segment Client Dominant</h4>
                        <p>Le type de client "<strong>{dominant_client}</strong>" a généré le flux net le plus important 
                        avec <strong>{dominant_amount_m:.2f}M FCFA</strong> ({flux_type}).</p>
                        <p><strong>Recommandation:</strong> {recommandation}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Pas de données de flux disponibles pour les FCP sélectionnés sur cette période.")
        
        st.markdown("---")
        
        # ===================
        # Section 5: Data Export
        # ===================
        st.subheader("📥 Export des Données et Analyses")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export actifs nets data for selected FCPs
            export_df = df_filtered[['Date'] + selected_fcps].copy()
            csv_actifs = export_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📊 Télécharger Actifs Nets (CSV)",
                data=csv_actifs,
                file_name=f"actifs_nets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Télécharger les actifs nets des FCP sélectionnés"
            )
        
        with col2:
            # Export summary statistics
            summary_data = []
            for fcp in selected_fcps:
                initial = df_filtered[fcp].iloc[0]
                final = df_filtered[fcp].iloc[-1]
                growth = ((final / initial) - 1) * 100 if initial > 0 else 0
                
                summary_data.append({
                    'FCP': fcp,
                    'Actifs Initiaux (FCFA)': initial,
                    'Actifs Finaux (FCFA)': final,
                    'Croissance (%)': growth,
                    'Moyenne (FCFA)': df_filtered[fcp].mean(),
                    'Maximum (FCFA)': df_filtered[fcp].max(),
                    'Minimum (FCFA)': df_filtered[fcp].min(),
                    'Écart-type (FCFA)': df_filtered[fcp].std()
                })
            
            summary_df = pd.DataFrame(summary_data)
            csv_summary = summary_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📈 Télécharger Statistiques (CSV)",
                data=csv_summary,
                file_name=f"statistiques_actifs_nets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Télécharger les statistiques des actifs nets"
            )
        
        st.markdown("""
        <div class="interpretation-note">
            <h4>💡 Note sur les Exports</h4>
            <p>Les fichiers exportés contiennent uniquement les données des FCP sélectionnés pour la période analysée. 
            Les statistiques sont calculées sur cette même période.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Success message
        st.success("✅ Analyse des Actifs Nets complétée avec succès!")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
        # Log the full error for debugging (in production, this should go to a logging service)
        import traceback
        import logging
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    main()
