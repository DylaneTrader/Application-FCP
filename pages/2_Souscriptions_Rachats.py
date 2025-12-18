"""
Souscriptions et Rachats Analysis Page
Analyzes subscriptions and redemptions for FCP funds
"""
import os
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
    MIN_SEASONALITY_PERIODS, DEFAULT_RADAR_RANGE, ALL_FCP_LABEL,
    MILLIONS_DIVISOR, HIGH_VOLATILITY_THRESHOLD,
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR,
    COMMON_CSS
)
from utils import load_data

# Configuration de la page
st.set_page_config(
    page_title="Analyse FCP - Souscriptions & Rachats",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


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


def calculate_net_flows(df):
    """Calculate net flows (subscriptions - redemptions)"""
    df_copy = df.copy()
    # Create a signed amount column: positive for subscriptions, negative for redemptions
    df_copy['Montant_Signe'] = df_copy.apply(
        lambda x: x['Montant'] if x['Opérations'] == 'Souscriptions' else -x['Montant'],
        axis=1
    )
    return df_copy


def calculate_growth_rates(series, period='M'):
    """Calculate growth rates for a time series"""
    if len(series) < 2:
        return pd.Series()
    return series.pct_change() * 100


def main():
    """Main function for the Souscriptions et Rachats page"""
    st.header("💰 Analyse des Souscriptions et Rachats")
    
    # Load data
    with st.spinner('Chargement des données de souscriptions et rachats...'):
        df = load_souscriptions_rachats_data()
        df = calculate_net_flows(df)
    
    # Get unique values for filters
    all_fcps = sorted(df['FCP'].unique())
    all_operations = sorted(df['Opérations'].unique())
    all_client_types = sorted(df['Type de clients'].unique())
    
    # Use all FCPs for analysis
    selected_fcps = all_fcps
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔧 Filtres")
        
        st.info(f"📊 Analyse de tous les FCP ({len(all_fcps)} FCP)")
        
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
            
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            
            if quick_filter == 'WTD':
                # Week to date
                date_range = (max_date - timedelta(days=max_date.weekday()), max_date)
            elif quick_filter == 'MTD':
                # Month to date
                date_range = (max_date.replace(day=1), max_date)
            elif quick_filter == 'QTD':
                # Quarter to date
                quarter_start_month = ((max_date.month - 1) // 3) * 3 + 1
                date_range = (max_date.replace(month=quarter_start_month, day=1), max_date)
            elif quick_filter == 'YTD':
                # Year to date
                date_range = (max_date.replace(month=1, day=1), max_date)
            elif quick_filter == 'Origine':
                # From the beginning
                date_range = (min_date, max_date)
            else:
                # Custom date range
                date_range = st.date_input(
                    "Sélectionnez la période",
                    value=(df['Date'].min(), df['Date'].max()),
                    min_value=df['Date'].min(),
                    max_value=df['Date'].max(),
                    key="souscriptions_rachats_date_range"
                )
            
            # Display selected date range
            if isinstance(date_range, tuple) and len(date_range) == 2:
                try:
                    st.caption(f"📅 Du {date_range[0].strftime('%d/%m/%Y')} au {date_range[1].strftime('%d/%m/%Y')}")
                except (AttributeError, TypeError):
                    pass
        
        # Filters grouped
        with st.expander("🔍 Filtres détaillés", expanded=False):
            # Operation type filter
            selected_operations = st.multiselect(
                "Type d'opération",
                options=all_operations,
                default=all_operations
            )
            
            # Client type filter
            selected_client_types = st.multiselect(
                "Type de clients",
                options=all_client_types,
                default=all_client_types
            )
            
            st.caption(f"📊 {len(selected_operations)} opérations, {len(selected_client_types)} types clients")
        
        # Visualization options
        with st.expander("🎨 Options de visualisation", expanded=False):
            # Aggregation period
            aggregation_period = st.selectbox(
                "Période d'agrégation",
                options=['Quotidien', 'Hebdomadaire', 'Mensuel', 'Trimestriel'],
                index=2
            )
    
    # Filter data (Note: FCP filtering removed - all FCPs are always included)
    if len(date_range) == 2:
        mask = (df['Date'] >= pd.Timestamp(date_range[0])) & (df['Date'] <= pd.Timestamp(date_range[1]))
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Apply operation and client type filters only (all FCPs are included)
    df_filtered = df_filtered[
        (df_filtered['Opérations'].isin(selected_operations)) &
        (df_filtered['Type de clients'].isin(selected_client_types))
    ]
    
    if df_filtered.empty:
        st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
        return
    
    # Map aggregation period to pandas frequency
    period_map = {
        'Quotidien': 'D',
        'Hebdomadaire': 'W',
        'Mensuel': 'M',
        'Trimestriel': 'Q'
    }
    freq = period_map[aggregation_period]
    
    # Keep full dataset for various analyses
    full_df = df.copy()
    
    # Calculate metrics for ALL FCPs in the period (used by later sections)
    df_all = df.copy()
    if len(date_range) == 2:
        mask_all = (df_all['Date'] >= pd.Timestamp(date_range[0])) & (df_all['Date'] <= pd.Timestamp(date_range[1]))
        df_all = df_all[mask_all]
    
    # ===================
    # Section 1: KPIs with Card Format (moved to top)
    # ===================
    st.subheader("📊 Indicateurs Clés de Performance - Tous les FCP")
    
    # Calculate metrics for all FCPs with applied filters
    total_souscriptions = df_filtered[df_filtered['Opérations'] == 'Souscriptions']['Montant'].sum()
    total_rachats = df_filtered[df_filtered['Opérations'] == 'Rachats']['Montant'].sum()
    flux_net = total_souscriptions - total_rachats
    nb_operations = len(df_filtered)
    taux_collecte = (total_souscriptions / total_rachats * 100) if total_rachats > 0 else 0
    
    # Display in card format
    total_sous_m = total_souscriptions/1e6
    total_rach_m = total_rachats/1e6
    flux_net_m = flux_net/1e6
    emoji_flux = '🟢' if flux_net >= 0 else '🔴'
    num_fcps = len(all_fcps)
    
    st.markdown(f"""
    <div class="ranking-card">
        <h3>💰 Performance Globale ({num_fcps} FCP)</h3>
        <div class="ranking-item">
            <span>Total Souscriptions</span>
            <span class="ranking-value">{total_sous_m:.2f}M FCFA</span>
        </div>
        <div class="ranking-item">
            <span>Total Rachats</span>
            <span class="ranking-value">{total_rach_m:.2f}M FCFA</span>
        </div>
        <div class="ranking-item">
            <span>Flux Net</span>
            <span class="ranking-value">{emoji_flux} {flux_net_m:+.2f}M FCFA</span>
        </div>
        <div class="ranking-item">
            <span>Taux de Collecte</span>
            <span class="ranking-value">{taux_collecte:.1f}%</span>
        </div>
        <div class="ranking-item">
            <span>Nombre d'opérations</span>
            <span class="ranking-value">{nb_operations:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Synthesis note
    collecte_status = "(collecte nette positive ✅)" if flux_net >= 0 else "(décollecte nette ⚠️)"
    taux_per_euro = taux_collecte/100
    
    st.markdown(f"""
    <div class="insight-box">
        <h4>💡 Note de Synthèse</h4>
        <p><strong>Performance Globale:</strong> Sur la période sélectionnée, l'ensemble des {num_fcps} FCP présente des flux nets de <strong>{flux_net_m:+.2f}M FCFA</strong> 
        {collecte_status}. 
        Le taux de collecte global est de <strong>{taux_collecte:.1f}%</strong>, indiquant que pour chaque FCFA racheté, 
        <strong>{taux_per_euro:.2f}FCFA</strong> sont souscrits.</p>
        <p>Cette analyse porte sur <strong>{nb_operations:,} opérations</strong> au total, permettant une vue d'ensemble complète 
        de l'activité de souscriptions et rachats.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===================
    # Section 2: Temporal Evolution
    # ===================
    st.subheader("📈 Évolution Temporelle - Tous les FCP")
    
    # Use tabs to organize content better
    tab1, tab2 = st.tabs(["📊 Évolution Temporelle", "🏆 Comparaison FCP"])
    
    with tab1:
        # Aggregate by date and operation type
        df_temporal = df_filtered.set_index('Date').groupby([pd.Grouper(freq=freq), 'Opérations'])['Montant'].sum().reset_index()
        
        # Create pivot for better visualization
        df_pivot = df_temporal.pivot(index='Date', columns='Opérations', values='Montant').fillna(0)
        
        # Calculate net flows
        if 'Souscriptions' in df_pivot.columns and 'Rachats' in df_pivot.columns:
            df_pivot['Flux Net'] = df_pivot['Souscriptions'] - df_pivot['Rachats']
        elif 'Souscriptions' in df_pivot.columns:
            df_pivot['Flux Net'] = df_pivot['Souscriptions']
        elif 'Rachats' in df_pivot.columns:
            df_pivot['Flux Net'] = -df_pivot['Rachats']
        else:
            df_pivot['Flux Net'] = 0
        
        # Create figure with subplots
        fig_temporal = go.Figure()
        
        if 'Souscriptions' in df_pivot.columns:
            fig_temporal.add_trace(go.Bar(
                x=df_pivot.index,
                y=df_pivot['Souscriptions'],
                name='Souscriptions',
                marker_color='#114B80',
                opacity=0.7
            ))
        
        if 'Rachats' in df_pivot.columns:
            fig_temporal.add_trace(go.Bar(
                x=df_pivot.index,
                y=df_pivot['Rachats'],
                name='Rachats',
                marker_color='#567389',
                opacity=0.7
            ))
        
        fig_temporal.add_trace(go.Scatter(
            x=df_pivot.index,
            y=df_pivot['Flux Net'],
            name='Flux Net',
            mode='lines+markers',
            line=dict(color='#ACC7DF', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig_temporal.update_layout(
            title=f"Évolution des Souscriptions, Rachats et Flux Nets ({aggregation_period})",
            xaxis_title="Date",
            yaxis_title="Montant (FCFA)",
            yaxis2=dict(
                title="Flux Net (FCFA)",
                overlaying='y',
                side='right'
            ),
            height=500,
            template="plotly_white",
            hovermode='x unified',
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Add interpretation
        positive_periods = (df_pivot['Flux Net'] > 0).sum()
        negative_periods = (df_pivot['Flux Net'] < 0).sum()
        total_periods = len(df_pivot)
        
        st.markdown(f"""
        <div class="interpretation-note">
        <strong>📊 Analyse de Tendance:</strong> Sur les {total_periods} périodes analysées, 
        <strong>{positive_periods} périodes ({positive_periods/total_periods*100:.1f}%)</strong> présentent des flux nets positifs (collecte nette),
        tandis que <strong>{negative_periods} périodes ({negative_periods/total_periods*100:.1f}%)</strong> montrent une décollecte nette.
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Total by FCP and operation
            df_by_fcp = df_filtered.groupby(['FCP', 'Opérations'])['Montant'].sum().reset_index()
            df_by_fcp_pivot = df_by_fcp.pivot(index='FCP', columns='Opérations', values='Montant').fillna(0)
            
            fig_fcp = go.Figure()
            
            if 'Souscriptions' in df_by_fcp_pivot.columns:
                text_values = (df_by_fcp_pivot['Souscriptions'] / MILLIONS_DIVISOR).round(1).astype(str) + 'M'
                fig_fcp.add_trace(go.Bar(
                    name='Souscriptions',
                    x=df_by_fcp_pivot.index,
                    y=df_by_fcp_pivot['Souscriptions'],
                    marker_color='#114B80',
                    text=text_values,
                    textposition='outside'
                ))
            
            if 'Rachats' in df_by_fcp_pivot.columns:
                text_values = (df_by_fcp_pivot['Rachats'] / MILLIONS_DIVISOR).round(1).astype(str) + 'M'
                fig_fcp.add_trace(go.Bar(
                    name='Rachats',
                    x=df_by_fcp_pivot.index,
                    y=df_by_fcp_pivot['Rachats'],
                    marker_color='#567389',
                    text=text_values,
                    textposition='outside'
                ))
            
            fig_fcp.update_layout(
                title="Montants par FCP",
                xaxis_title="FCP",
                yaxis_title="Montant (FCFA)",
                height=400,
                template="plotly_white",
                barmode='group'
            )
            
            st.plotly_chart(fig_fcp, use_container_width=True)
        
        with col2:
            # Net flows by FCP
            df_net_fcp = df_filtered.groupby('FCP')['Montant_Signe'].sum().reset_index()
            df_net_fcp.columns = ['FCP', 'Flux Net']
            df_net_fcp = df_net_fcp.sort_values('Flux Net', ascending=False)
            
            fig_net_fcp = go.Figure()
            
            colors = ['#114B80' if x >= 0 else '#567389' for x in df_net_fcp['Flux Net']]
            text_values = (df_net_fcp['Flux Net'] / MILLIONS_DIVISOR).round(1).astype(str) + 'M'
            
            fig_net_fcp.add_trace(go.Bar(
                x=df_net_fcp['FCP'],
                y=df_net_fcp['Flux Net'],
                marker_color=colors,
                text=text_values,
                textposition='outside'
            ))
            
            fig_net_fcp.update_layout(
                title="Flux Net par FCP",
                xaxis_title="FCP",
                yaxis_title="Flux Net (FCFA)",
                height=400,
                template="plotly_white",
                showlegend=False
            )
            
            st.plotly_chart(fig_net_fcp, use_container_width=True)
    
    # ===================
    # Section 4: Client Analysis & Heatmap
    # ===================
    st.subheader("👥 Analyse par Type de Client et Heatmap - Tous les FCP")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Répartition", "🔥 Heatmap", "📋 Tableau Détaillé", "👥 Dynamique Client"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for subscriptions by client type
            df_client_sous = df_filtered[df_filtered['Opérations'] == 'Souscriptions'].groupby('Type de clients')['Montant'].sum()
            
            if not df_client_sous.empty:
                fig_pie_sous = go.Figure(data=[go.Pie(
                    labels=df_client_sous.index,
                    values=df_client_sous.values,
                    hole=0.3,
                    marker=dict(colors=px.colors.qualitative.Set2)
                )])
                
                fig_pie_sous.update_layout(
                    title="Répartition des Souscriptions par Type de Client",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_pie_sous, use_container_width=True)
        
        with col2:
            # Pie chart for redemptions by client type
            df_client_rachats = df_filtered[df_filtered['Opérations'] == 'Rachats'].groupby('Type de clients')['Montant'].sum()
            
            if not df_client_rachats.empty:
                fig_pie_rachats = go.Figure(data=[go.Pie(
                    labels=df_client_rachats.index,
                    values=df_client_rachats.values,
                    hole=0.3,
                    marker=dict(colors=px.colors.qualitative.Set3)
                )])
                
                fig_pie_rachats.update_layout(
                    title="Répartition des Rachats par Type de Client",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_pie_rachats, use_container_width=True)
    
    with tab2:
        # Heatmap Analysis
        # Select operation type for heatmap
        heatmap_operation = st.radio(
            "Type d'opération pour la heatmap",
            options=['Souscriptions', 'Rachats', 'Flux Net'],
            horizontal=True
        )
        
        if heatmap_operation == 'Flux Net':
            df_heatmap = df_filtered.groupby(['FCP', 'Type de clients'])['Montant_Signe'].sum().reset_index()
            df_heatmap_pivot = df_heatmap.pivot(index='FCP', columns='Type de clients', values='Montant_Signe').fillna(0)
        else:
            df_heatmap = df_filtered[df_filtered['Opérations'] == heatmap_operation].groupby(['FCP', 'Type de clients'])['Montant'].sum().reset_index()
            df_heatmap_pivot = df_heatmap.pivot(index='FCP', columns='Type de clients', values='Montant').fillna(0)
        
        if not df_heatmap_pivot.empty:
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=df_heatmap_pivot.values,
                x=df_heatmap_pivot.columns,
                y=df_heatmap_pivot.index,
                colorscale='RdYlGn' if heatmap_operation == 'Flux Net' else 'Blues',
                text=np.round(df_heatmap_pivot.values / 1000, 1),
                texttemplate='%{text}K',
                textfont={"size": 10},
                colorbar=dict(title="Montant (FCFA)")
            ))
            
            fig_heatmap.update_layout(
                title=f"Heatmap des {heatmap_operation} par FCP et Type de Client",
                xaxis_title="Type de Client",
                yaxis_title="FCP",
                height=max(400, len(df_heatmap_pivot) * 30),
                template="plotly_white"
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab3:
        # Detailed table by client type
        df_client_detail = df_filtered.groupby(['Type de clients', 'Opérations'])['Montant'].agg(['sum', 'count', 'mean']).reset_index()
        df_client_detail.columns = ['Type de clients', 'Opération', 'Montant Total', 'Nombre', 'Montant Moyen']
        df_client_detail['Montant Total'] = df_client_detail['Montant Total'].apply(lambda x: f'{x:,.0f} FCFA')
        df_client_detail['Montant Moyen'] = df_client_detail['Montant Moyen'].apply(lambda x: f'{x:,.0f} FCFA')
        
        st.dataframe(df_client_detail, use_container_width=True, hide_index=True)
    
    with tab4:
        st.markdown("##### 👥 Dynamique et Comportement des Clients")
        
        # Client type selector
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_client_types_analysis = st.multiselect(
                "Sélectionner des types de clients à analyser",
                options=all_client_types,
                default=all_client_types,
                key="client_types_analysis"
            )
        with col2:
            compare_clients = st.checkbox("Comparer au Total", value=True, key="compare_clients_total")
        
        if not selected_client_types_analysis:
            st.warning("⚠️ Veuillez sélectionner au moins un type de client")
        else:
            df_clients = df_filtered[df_filtered['Type de clients'].isin(selected_client_types_analysis)]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Client evolution over time
                st.markdown("**📈 Évolution des Flux par Type de Client**")
                
                df_client_time = df_clients.set_index('Date').groupby([pd.Grouper(freq='M'), 'Type de clients'])['Montant_Signe'].sum().reset_index()
                
                fig_client_time = go.Figure()
                
                for client_type in selected_client_types_analysis:
                    df_ct = df_client_time[df_client_time['Type de clients'] == client_type]
                    fig_client_time.add_trace(go.Scatter(
                        x=df_ct['Date'],
                        y=df_ct['Montant_Signe'],
                        name=client_type,
                        mode='lines+markers',
                        line=dict(width=2)
                    ))
                
                fig_client_time.update_layout(
                    title="Flux Nets Mensuels par Type de Client",
                    xaxis_title="Date",
                    yaxis_title="Flux Net (FCFA)",
                    height=400,
                    template="plotly_white",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_client_time, use_container_width=True)
            
            with col2:
                # Client contribution to total
                st.markdown("**📊 Contribution par Type de Client**")
                
                client_contrib = []
                total_flux = df_clients['Montant_Signe'].sum()
                
                for client_type in selected_client_types_analysis:
                    df_ct = df_clients[df_clients['Type de clients'] == client_type]
                    flux_ct = df_ct['Montant_Signe'].sum()
                    contrib_pct = (flux_ct / total_flux * 100) if total_flux != 0 else 0
                    
                    client_contrib.append({
                        'Type de Client': client_type,
                        'Flux Net': flux_ct,
                        'Contribution (%)': contrib_pct
                    })
                
                df_client_contrib = pd.DataFrame(client_contrib).sort_values('Flux Net', ascending=False)
                
                fig_client_contrib = go.Figure(data=[go.Pie(
                    labels=df_client_contrib['Type de Client'],
                    values=df_client_contrib['Flux Net'],
                    hole=0.4,
                    marker=dict(colors=px.colors.qualitative.Set2),
                    textposition='inside',
                    textinfo='label+percent'
                )])
                
                fig_client_contrib.update_layout(
                    title="Répartition des Flux Nets",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_client_contrib, use_container_width=True)
            
            # Client statistics table
            st.markdown("**📋 Tableau Récapitulatif par Type de Client:**")
            
            client_stats = []
            for client_type in selected_client_types_analysis:
                df_ct = df_clients[df_clients['Type de clients'] == client_type]
                
                sous = df_ct[df_ct['Opérations'] == 'Souscriptions']['Montant'].sum()
                rach = df_ct[df_ct['Opérations'] == 'Rachats']['Montant'].sum()
                flux_net = sous - rach
                taux_collecte = (sous / rach * 100) if rach > 0 else 0
                nb_ops = len(df_ct)
                montant_moyen = df_ct['Montant'].mean()
                
                client_stats.append({
                    'Type de Client': client_type,
                    'Souscriptions (MFCFA)': sous / MILLIONS_DIVISOR,
                    'Rachats (MFCFA)': rach / MILLIONS_DIVISOR,
                    'Flux Net (MFCFA)': flux_net / MILLIONS_DIVISOR,
                    'Taux Collecte (%)': taux_collecte,
                    'Nb Opérations': nb_ops,
                    'Montant Moyen (FCFA)': montant_moyen
                })
            
            df_client_stats = pd.DataFrame(client_stats).sort_values('Flux Net (MFCFA)', ascending=False)
            
            st.dataframe(
                df_client_stats.style.format({
                    'Souscriptions (MFCFA)': '{:.2f}',
                    'Rachats (MFCFA)': '{:.2f}',
                    'Flux Net (MFCFA)': '{:+.2f}',
                    'Taux Collecte (%)': '{:.1f}',
                    'Nb Opérations': '{:,}',
                    'Montant Moyen (FCFA)': '{:,.0f}'
                }).background_gradient(subset=['Flux Net (MFCFA)'], cmap='RdYlGn')
                  .background_gradient(subset=['Taux Collecte (%)'], cmap='RdYlGn'),
                use_container_width=True,
                hide_index=True
            )
            
            # Behavioral insights
            best_client = df_client_stats.iloc[0] if len(df_client_stats) > 0 else None
            
            if best_client is not None:
                st.markdown(f"""
                <div class="interpretation-note">
                <strong>💡 Insights Comportementaux:</strong><br>
                • <strong>Segment le plus performant:</strong> {best_client['Type de Client']} avec {best_client['Flux Net (MFCFA)']:.2f}M FCFA de flux net<br>
                • <strong>Taux de collecte:</strong> {best_client['Taux Collecte (%)']:.1f}% - {"✅ Attractif" if best_client['Taux Collecte (%)'] > 100 else "⚠️ Attention"}<br>
                • <strong>Volume d'activité:</strong> {best_client['Nb Opérations']:,} opérations ({best_client['Montant Moyen (FCFA)']:,.0f} FCFA moyen)<br>
                • Analysez les segments avec décollecte pour identifier des actions correctives
                </div>
                """, unsafe_allow_html=True)
    
    # ===================
    # Section 5: Advanced Statistics
    # ===================
    st.subheader("📊 Statistiques Avancées - Tous les FCP")
    
    tab1, tab2 = st.tabs(["📈 Croissance & Distribution", "📉 Tendances"])
    
    with tab1:
        # Add FCP selector for comparative analysis
        st.markdown("##### Analyse Comparative par FCP")
        
        # FCP selector for detailed comparison
        analysis_fcps = st.multiselect(
            "Sélectionner des FCP pour analyse détaillée (laisser vide pour agrégat de tous les FCP)",
            options=all_fcps,
            default=[],
            key="growth_dist_fcps",
            help="Choisissez jusqu'à 5 FCP pour comparer leurs performances individuelles"
        )
        
        # Limit to 5 FCPs for clarity
        if len(analysis_fcps) > 5:
            st.warning("⚠️ Veuillez sélectionner au maximum 5 FCP pour une meilleure lisibilité")
            analysis_fcps = analysis_fcps[:5]
        
        show_total = st.checkbox("Afficher la comparaison avec le Total (tous FCP)", value=False, key="show_total_growth")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly growth rates - by FCP or aggregated
            st.markdown("##### Taux de Croissance Mensuel des Flux Nets")
            
            fig_growth = go.Figure()
            
            if analysis_fcps:
                # Show individual FCP growth rates
                colors = px.colors.qualitative.Plotly
                for idx, fcp in enumerate(analysis_fcps):
                    df_fcp_monthly = df_filtered[df_filtered['FCP'] == fcp].set_index('Date').resample('M')['Montant_Signe'].sum()
                    if len(df_fcp_monthly) > 1:
                        growth_fcp = calculate_growth_rates(df_fcp_monthly)
                        if not growth_fcp.empty:
                            fig_growth.add_trace(go.Scatter(
                                x=df_fcp_monthly.index[1:],
                                y=growth_fcp.dropna(),
                                name=fcp,
                                mode='lines+markers',
                                line=dict(color=colors[idx % len(colors)], width=2),
                                marker=dict(size=6)
                            ))
            else:
                # Show aggregated growth for all FCPs
                df_monthly = df_filtered.set_index('Date').resample('M')['Montant_Signe'].sum()
                if len(df_monthly) > 1:
                    growth_selected = calculate_growth_rates(df_monthly)
                    if not growth_selected.empty:
                        fig_growth.add_trace(go.Scatter(
                            x=df_monthly.index[1:],
                            y=growth_selected.dropna(),
                            name='Tous les FCP',
                            mode='lines+markers',
                            line=dict(color='#114B80', width=3),
                            marker=dict(size=8)
                        ))
            
            # Add total comparison if requested
            if show_total:
                df_all_monthly = df_all.set_index('Date').resample('M')['Montant_Signe'].sum()
                if len(df_all_monthly) > 1:
                    growth_all = calculate_growth_rates(df_all_monthly)
                    if not growth_all.empty:
                        fig_growth.add_trace(go.Scatter(
                            x=df_all_monthly.index[1:],
                            y=growth_all.dropna(),
                            name='Total (tous FCP)',
                            mode='lines',
                            line=dict(color='gray', width=2, dash='dash'),
                            opacity=0.6
                        ))
            
            fig_growth.update_layout(
                title="Taux de Croissance Mensuel des Flux Nets (%)",
                xaxis_title="Date",
                yaxis_title="Croissance (%)",
                height=400,
                template="plotly_white",
                hovermode='x unified',
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            
            st.plotly_chart(fig_growth, use_container_width=True)
            
            # Stats summary
            if analysis_fcps:
                st.markdown("**📊 Statistiques de croissance:**")
                stats_data = []
                for fcp in analysis_fcps:
                    df_fcp_monthly = df_filtered[df_filtered['FCP'] == fcp].set_index('Date').resample('M')['Montant_Signe'].sum()
                    if len(df_fcp_monthly) > 1:
                        growth_fcp = calculate_growth_rates(df_fcp_monthly)
                        if not growth_fcp.empty:
                            stats_data.append({
                                'FCP': fcp,
                                'Croissance Moyenne (%)': growth_fcp.mean(),
                                'Écart-type (%)': growth_fcp.std(),
                                'Min (%)': growth_fcp.min(),
                                'Max (%)': growth_fcp.max()
                            })
                
                if stats_data:
                    df_stats = pd.DataFrame(stats_data)
                    st.dataframe(
                        df_stats.style.format({
                            'Croissance Moyenne (%)': '{:.2f}',
                            'Écart-type (%)': '{:.2f}',
                            'Min (%)': '{:.2f}',
                            'Max (%)': '{:.2f}'
                        }).background_gradient(subset=['Croissance Moyenne (%)'], cmap='RdYlGn', vmin=-50, vmax=50),
                        use_container_width=True,
                        hide_index=True
                    )
        
        with col2:
            # Distribution comparative by FCP
            st.markdown("##### Distribution Comparative des Flux Nets")
            
            fig_dist = go.Figure()
            
            if analysis_fcps:
                # Show distribution for each selected FCP
                for fcp in analysis_fcps:
                    df_fcp = df_filtered[df_filtered['FCP'] == fcp]
                    df_fcp_daily = df_fcp.set_index('Date').resample('D')['Montant_Signe'].sum()
                    fig_dist.add_trace(go.Box(
                        y=df_fcp_daily,
                        name=fcp,
                        boxmean='sd'
                    ))
            else:
                # Show distribution by operation type for all FCPs
                for operation in df_filtered['Opérations'].unique():
                    df_op = df_filtered[df_filtered['Opérations'] == operation]['Montant']
                    fig_dist.add_trace(go.Box(
                        y=df_op,
                        name=operation,
                        boxmean='sd'
                    ))
            
            # Add total comparison if requested
            if show_total and not analysis_fcps:
                for operation in df_all['Opérations'].unique():
                    df_op_all = df_all[df_all['Opérations'] == operation]['Montant']
                    fig_dist.add_trace(go.Box(
                        y=df_op_all,
                        name=f"{operation} (Total)",
                        boxmean='sd',
                        marker=dict(opacity=0.4)
                    ))
            
            fig_dist.update_layout(
                title="Distribution des Montants",
                yaxis_title="Montant (FCFA)",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Distribution statistics
            if analysis_fcps:
                st.markdown("**📊 Statistiques de distribution:**")
                dist_stats = []
                for fcp in analysis_fcps:
                    df_fcp_daily = df_filtered[df_filtered['FCP'] == fcp].set_index('Date').resample('D')['Montant_Signe'].sum()
                    dist_stats.append({
                        'FCP': fcp,
                        'Médiane': df_fcp_daily.median(),
                        'Moyenne': df_fcp_daily.mean(),
                        'Écart-type': df_fcp_daily.std(),
                        'Q1': df_fcp_daily.quantile(0.25),
                        'Q3': df_fcp_daily.quantile(0.75)
                    })
                
                if dist_stats:
                    df_dist_stats = pd.DataFrame(dist_stats)
                    st.dataframe(
                        df_dist_stats.style.format({
                            'Médiane': '{:,.0f} FCFA',
                            'Moyenne': '{:,.0f} FCFA',
                            'Écart-type': '{:,.0f} FCFA',
                            'Q1': '{:,.0f} FCFA',
                            'Q3': '{:,.0f} FCFA'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
    
    with tab2:
        # Add trend analysis with FCP comparison
        st.markdown("##### Analyse de Tendances et Moyennes Mobiles")
        
        # FCP selector for trend analysis
        col1, col2 = st.columns([3, 1])
        with col1:
            trend_fcps = st.multiselect(
                "Sélectionner des FCP pour analyse de tendances (laisser vide pour agrégat de tous les FCP)",
                options=all_fcps,
                default=[],
                key="trend_fcps",
                help="Choisissez jusqu'à 4 FCP pour comparer leurs tendances"
            )
        with col2:
            show_total_trend = st.checkbox("Afficher Total", value=True, key="show_total_trend")
        
        # Limit to 4 FCPs for clarity
        if len(trend_fcps) > 4:
            st.warning("⚠️ Veuillez sélectionner au maximum 4 FCP pour une meilleure lisibilité")
            trend_fcps = trend_fcps[:4]
        
        # Trend analysis chart
        fig_trend = go.Figure()
        
        if trend_fcps:
            # Show individual FCP trends
            colors = px.colors.qualitative.Set2
            for idx, fcp in enumerate(trend_fcps):
                df_fcp_trend = df_filtered[df_filtered['FCP'] == fcp].set_index('Date').resample('W')['Montant_Signe'].sum().reset_index()
                if len(df_fcp_trend) > 0:
                    df_fcp_trend['MA_4W'] = df_fcp_trend['Montant_Signe'].rolling(window=4, min_periods=1).mean()
                    df_fcp_trend['MA_12W'] = df_fcp_trend['Montant_Signe'].rolling(window=12, min_periods=1).mean()
                    
                    # Raw data (light)
                    fig_trend.add_trace(go.Scatter(
                        x=df_fcp_trend['Date'],
                        y=df_fcp_trend['Montant_Signe'],
                        mode='lines',
                        name=f'{fcp} (brut)',
                        line=dict(color=colors[idx % len(colors)], width=1),
                        opacity=0.3,
                        showlegend=True
                    ))
                    
                    # MA 4W
                    fig_trend.add_trace(go.Scatter(
                        x=df_fcp_trend['Date'],
                        y=df_fcp_trend['MA_4W'],
                        mode='lines',
                        name=f'{fcp} (MA 4S)',
                        line=dict(color=colors[idx % len(colors)], width=2),
                        showlegend=True
                    ))
        else:
            # Show aggregated trend for all FCPs
            df_trend = df_filtered.set_index('Date').resample('W')['Montant_Signe'].sum().reset_index()
            df_trend['MA_4W'] = df_trend['Montant_Signe'].rolling(window=4, min_periods=1).mean()
            df_trend['MA_12W'] = df_trend['Montant_Signe'].rolling(window=12, min_periods=1).mean()
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['Date'],
                y=df_trend['Montant_Signe'],
                mode='lines',
                name='Flux Net Hebdomadaire (Tous les FCP)',
                line=dict(color='lightgray', width=1),
                opacity=0.5
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['Date'],
                y=df_trend['MA_4W'],
                mode='lines',
                name='Moyenne Mobile 4 Semaines',
                line=dict(color='#114B80', width=2)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['Date'],
                y=df_trend['MA_12W'],
                mode='lines',
                name='Moyenne Mobile 12 Semaines',
                line=dict(color='#567389', width=2)
            ))
        
        # Add total comparison if requested
        if show_total_trend:
            df_all_trend = df_all.set_index('Date').resample('W')['Montant_Signe'].sum().reset_index()
            df_all_trend['MA_4W'] = df_all_trend['Montant_Signe'].rolling(window=4, min_periods=1).mean()
            
            fig_trend.add_trace(go.Scatter(
                x=df_all_trend['Date'],
                y=df_all_trend['MA_4W'],
                mode='lines',
                name='Total (MA 4S)',
                line=dict(color='gray', width=2, dash='dash'),
                opacity=0.6
            ))
        
        fig_trend.update_layout(
            title="Flux Nets et Moyennes Mobiles",
            xaxis_title="Date",
            yaxis_title="Flux Net (FCFA)",
            height=500,
            template="plotly_white",
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Trend statistics
        if trend_fcps:
            st.markdown("**📊 Analyse de tendance par FCP:**")
            
            trend_stats = []
            for fcp in trend_fcps:
                df_fcp_trend = df_filtered[df_filtered['FCP'] == fcp].set_index('Date').resample('W')['Montant_Signe'].sum()
                if len(df_fcp_trend) > 1:
                    # Calculate trend using linear regression
                    x = np.arange(len(df_fcp_trend))
                    y = df_fcp_trend.values
                    if len(x) > 0 and not np.all(np.isnan(y)):
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                        trend_direction = "📈 Hausse" if slope > 0 else "📉 Baisse"
                        trend_stats.append({
                            'FCP': fcp,
                            'Tendance': trend_direction,
                            'Pente (FCFA/sem)': slope,
                            'R² (%)': r_value**2 * 100,
                            'Flux Moyen (FCFA)': df_fcp_trend.mean()
                        })
            
            if trend_stats:
                df_trend_stats = pd.DataFrame(trend_stats)
                st.dataframe(
                    df_trend_stats.style.format({
                        'Pente (FCFA/sem)': '{:,.0f}',
                        'R² (%)': '{:.1f}',
                        'Flux Moyen (FCFA)': '{:,.0f}'
                    }).background_gradient(subset=['Pente (FCFA/sem)'], cmap='RdYlGn'),
                    use_container_width=True,
                    hide_index=True
                )
        
        st.markdown("""
        <div class="interpretation-note">
        <strong>💡 Analyse de Tendance:</strong> Les moyennes mobiles lissent les fluctuations court terme et révèlent la tendance sous-jacente.
        Une moyenne mobile ascendante indique une tendance positive à la collecte, tandis qu'une moyenne descendante suggère une décollecte.
        La pente de régression indique la vitesse de changement des flux, et le R² mesure la force de la tendance.
        </div>
        """, unsafe_allow_html=True)
    
    # ===================
    # Section 7.5: Advanced Analyses
    # ===================
    st.subheader("🔬 Analyses Avancées - Tous les FCP")
    
    # Tabs for different advanced analyses (removed Dynamique Client - moved to Client Analysis section)
    tab1, tab2, tab3 = st.tabs(["💎 Concentration & Intensité", "📈 Volatilité & Stabilité", "🔄 Saisonnalité Approfondie"])
    
    with tab1:
        st.markdown("##### Analyse de la Concentration et de l'Intensité des Flux")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Concentration analysis - Top N FCPs contribution
            st.markdown("**Concentration des Flux Nets (Top FCP)**")
            
            # Calculate net flows by FCP
            fcp_net_flows = df_filtered.groupby('FCP')['Montant_Signe'].sum().sort_values(ascending=False)
            total_net_flow = fcp_net_flows.sum()
            
            # Get the last date in the filtered data
            last_date = df_filtered['Date'].max()
            
            # Calculate net flows at the last date
            df_last_date = df_filtered[df_filtered['Date'] == last_date]
            fcp_net_flows_last_date = df_last_date.groupby('FCP')['Montant_Signe'].sum()
            total_net_flow_last_date = fcp_net_flows_last_date.sum()
            
            # Calculate cumulative percentage
            fcp_net_flows_df = pd.DataFrame({
                'FCP': fcp_net_flows.index,
                'Flux Net': fcp_net_flows.values,
                'Part (%)': (fcp_net_flows.values / total_net_flow * 100) if total_net_flow != 0 else 0
            })
            fcp_net_flows_df['Part Cumulée (%)'] = fcp_net_flows_df['Part (%)'].cumsum()
            
            # Add "Part au [dernière date]" column - calculate shares directly
            if total_net_flow_last_date != 0:
                fcp_net_flows_df[f'Part au {last_date.strftime("%Y-%m-%d")}'] = fcp_net_flows_df['FCP'].apply(
                    lambda fcp: (fcp_net_flows_last_date.get(fcp, 0) / total_net_flow_last_date * 100)
                )
            else:
                fcp_net_flows_df[f'Part au {last_date.strftime("%Y-%m-%d")}'] = 0
            
            # Display table
            st.dataframe(
                fcp_net_flows_df.style.format({
                    'Flux Net': '{:,.0f} FCFA',
                    'Part (%)': '{:.2f}',
                    'Part Cumulée (%)': '{:.2f}',
                    f'Part au {last_date.strftime("%Y-%m-%d")}': '{:.2f}'
                }).background_gradient(subset=['Part (%)'], cmap='Blues'),
                use_container_width=True,
                hide_index=True
            )
            
            # Concentration metrics
            top3_contribution = fcp_net_flows_df.head(3)['Part (%)'].sum()
            top5_contribution = fcp_net_flows_df.head(5)['Part (%)'].sum() if len(fcp_net_flows_df) >= 5 else fcp_net_flows_df['Part (%)'].sum()
            
            st.markdown(f"""
            <div class="interpretation-note">
            <strong>💡 Concentration:</strong><br>
            • Top 3 FCP représentent <strong>{top3_contribution:.1f}%</strong> des flux nets<br>
            • Top 5 FCP représentent <strong>{top5_contribution:.1f}%</strong> des flux nets<br>
            • {"⚠️ Concentration élevée" if top3_contribution > 70 else "✅ Diversification correcte"}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Intensity analysis - Taux de collecte by segment
            st.markdown("**Intensité de Collecte par FCP**")
            
            # Calculate collection rate by FCP
            intensity_data = []
            for fcp in all_fcps:
                df_fcp = df_filtered[df_filtered['FCP'] == fcp]
                sous = df_fcp[df_fcp['Opérations'] == 'Souscriptions']['Montant'].sum()
                rach = df_fcp[df_fcp['Opérations'] == 'Rachats']['Montant'].sum()
                flux_net = sous - rach
                taux_collecte = (sous / rach * 100) if rach > 0 else 0
                
                intensity_data.append({
                    'FCP': fcp,
                    'Souscriptions': sous,
                    'Rachats': rach,
                    'Taux Collecte (%)': taux_collecte,
                    'Flux Net': flux_net
                })
            
            df_intensity = pd.DataFrame(intensity_data).sort_values('Taux Collecte (%)', ascending=False)
            
            # Visualization
            fig_intensity = go.Figure()
            
            colors_intensity = ['green' if x > 100 else 'orange' if x > 90 else 'red' for x in df_intensity['Taux Collecte (%)']]
            
            fig_intensity.add_trace(go.Bar(
                x=df_intensity['FCP'],
                y=df_intensity['Taux Collecte (%)'],
                marker_color=colors_intensity,
                text=[f"{v:.1f}%" for v in df_intensity['Taux Collecte (%)']],
                textposition='outside'
            ))
            
            # Add reference line at 100%
            fig_intensity.add_hline(y=100, line_dash="dash", line_color="gray", 
                                   annotation_text="Équilibre (100%)")
            
            fig_intensity.update_layout(
                title="Taux de Collecte par FCP",
                xaxis_title="FCP",
                yaxis_title="Taux de Collecte (%)",
                height=350,
                template="plotly_white",
                showlegend=False
            )
            
            st.plotly_chart(fig_intensity, use_container_width=True)
            
            # Intensity metrics
            high_performers = (df_intensity['Taux Collecte (%)'] > 100).sum()
            avg_taux = df_intensity['Taux Collecte (%)'].mean()
            
            st.markdown(f"""
            <div class="interpretation-note">
            <strong>💡 Intensité:</strong><br>
            • <strong>{high_performers}/{len(df_intensity)}</strong> FCP avec collecte nette positive<br>
            • Taux moyen: <strong>{avg_taux:.1f}%</strong><br>
            • {"✅ Performance saine" if avg_taux > 100 else "⚠️ Décollecte globale"}
            </div>
            """, unsafe_allow_html=True)
        
        # Additional: Pareto chart
        st.markdown("##### 📊 Diagramme de Pareto - Concentration des Flux")
        
        fig_pareto = go.Figure()
        
        fig_pareto.add_trace(go.Bar(
            x=fcp_net_flows_df['FCP'],
            y=fcp_net_flows_df['Flux Net'],
            name='Flux Net',
            marker_color='#114B80',
            yaxis='y'
        ))
        
        fig_pareto.add_trace(go.Scatter(
            x=fcp_net_flows_df['FCP'],
            y=fcp_net_flows_df['Part Cumulée (%)'],
            name='Part Cumulée',
            mode='lines+markers',
            line=dict(color='#567389', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig_pareto.update_layout(
            title="Diagramme de Pareto des Flux Nets",
            xaxis_title="FCP",
            yaxis=dict(title="Flux Net (FCFA)"),
            yaxis2=dict(title="Part Cumulée (%)", overlaying='y', side='right', range=[0, 105]),
            height=400,
            template="plotly_white",
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_pareto, use_container_width=True)
        
        # Interpretation note for Pareto diagram
        # Calculate 80/20 rule metrics
        cumulative_80_pct = fcp_net_flows_df[fcp_net_flows_df['Part Cumulée (%)'] <= 80]
        num_fcps_for_80_pct = len(cumulative_80_pct) if len(cumulative_80_pct) > 0 else 0
        pct_fcps_for_80_pct = (num_fcps_for_80_pct / len(fcp_net_flows_df) * 100) if len(fcp_net_flows_df) > 0 else 0
        
        st.markdown(f"""
        <div class="interpretation-note">
        <strong>📊 Interprétation du Diagramme de Pareto:</strong><br>
        <p>Le diagramme de Pareto permet de visualiser la concentration des flux nets entre les différents FCP. 
        Il combine un graphique en barres (flux nets par FCP) avec une courbe de cumul (part cumulée en %).</p>
        <p><strong>Analyse de la concentration:</strong></p>
        <ul>
        <li><strong>{num_fcps_for_80_pct}/{len(fcp_net_flows_df)}</strong> FCP ({pct_fcps_for_80_pct:.1f}%) représentent environ <strong>80%</strong> des flux nets totaux</li>
        <li>{"⚠️ <strong>Concentration élevée:</strong> Les flux sont dominés par un petit nombre de FCP, ce qui peut présenter un risque de concentration." if pct_fcps_for_80_pct < 30 else "✅ <strong>Diversification correcte:</strong> Les flux sont répartis de manière relativement équilibrée entre les FCP."}</li>
        <li>La courbe ascendante montre la contribution cumulative de chaque FCP aux flux nets totaux</li>
        </ul>
        <p><strong>💡 Recommandation:</strong> {"Surveiller les FCP dominants pour assurer la stabilité des flux." if pct_fcps_for_80_pct < 30 else "Maintenir cet équilibre pour limiter les risques de concentration."}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("##### Analyse de la Volatilité et de la Stabilité des Flux")
        
        # FCP selector for volatility comparison
        col1, col2 = st.columns([3, 1])
        with col1:
            volatility_fcps = st.multiselect(
                "Sélectionner des FCP pour analyser la volatilité (laisser vide pour tous les FCP)",
                options=all_fcps,
                default=all_fcps[:5] if len(all_fcps) >= 5 else all_fcps,
                key="volatility_fcps"
            )
        with col2:
            compare_to_total_vol = st.checkbox("Comparer au Total", value=True, key="compare_vol_total")
        
        if not volatility_fcps:
            volatility_fcps = all_fcps
        
        # Calculate volatility metrics
        volatility_data = []
        for fcp in volatility_fcps:
            fcp_flows = df_filtered[df_filtered['FCP'] == fcp].set_index('Date').resample('W')['Montant_Signe'].sum()
            if len(fcp_flows) > 1:
                mean_flow = fcp_flows.mean()
                std_flow = fcp_flows.std()
                cv = (std_flow / abs(mean_flow) * 100) if mean_flow != 0 else 0
                max_drawdown = ((fcp_flows.cummax() - fcp_flows) / fcp_flows.cummax().abs()).max() * 100
                
                volatility_data.append({
                    'FCP': fcp,
                    'Flux Moyen (FCFA)': mean_flow,
                    'Écart-type (FCFA)': std_flow,
                    'CV (%)': cv,
                    'Max Drawdown (%)': max_drawdown
                })
        
        # Add total comparison if requested
        if compare_to_total_vol:
            all_flows = df_all.set_index('Date').resample('W')['Montant_Signe'].sum()
            if len(all_flows) > 1:
                mean_all = all_flows.mean()
                std_all = all_flows.std()
                cv_all = (std_all / abs(mean_all) * 100) if mean_all != 0 else 0
                max_dd_all = ((all_flows.cummax() - all_flows) / all_flows.cummax().abs()).max() * 100
                
                volatility_data.append({
                    'FCP': 'TOTAL (référence)',
                    'Flux Moyen (FCFA)': mean_all,
                    'Écart-type (FCFA)': std_all,
                    'CV (%)': cv_all,
                    'Max Drawdown (%)': max_dd_all
                })
        
        if volatility_data:
            df_volatility = pd.DataFrame(volatility_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Coefficient of Variation chart
                df_vol_sorted = df_volatility[df_volatility['FCP'] != 'TOTAL (référence)'].sort_values('CV (%)', ascending=False)
                
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Bar(
                    x=df_vol_sorted['FCP'],
                    y=df_vol_sorted['CV (%)'],
                    marker_color='#114B80',
                    text=[f"{v:.1f}%" for v in df_vol_sorted['CV (%)']],
                    textposition='outside',
                    name='CV FCP'
                ))
                
                # Add total reference line if available
                if compare_to_total_vol:
                    total_cv = df_volatility[df_volatility['FCP'] == 'TOTAL (référence)']['CV (%)'].values[0]
                    fig_vol.add_hline(y=total_cv, line_dash="dash", line_color="red", 
                                     annotation_text=f"Total: {total_cv:.1f}%")
                
                fig_vol.update_layout(
                    title="Coefficient de Variation par FCP",
                    xaxis_title="FCP",
                    yaxis_title="Coefficient de Variation (%)",
                    height=350,
                    template="plotly_white",
                    showlegend=False
                )
                
                st.plotly_chart(fig_vol, use_container_width=True)
            
            with col2:
                # Volatility distribution and comparison chart
                st.markdown("**Distribution de la Volatilité des Flux**")
                
                fig_vol_dist = go.Figure()
                
                # If specific FCPs are selected, show their distribution
                # Otherwise show all FCPs
                display_fcps = volatility_fcps if volatility_fcps else all_fcps
                
                for fcp in display_fcps:
                    fcp_flows = df_filtered[df_filtered['FCP'] == fcp].set_index('Date').resample('W')['Montant_Signe'].sum()
                    if len(fcp_flows) > 4:  # Need at least a few data points
                        # Create a box plot showing the distribution of weekly flows
                        fig_vol_dist.add_trace(go.Box(
                            y=fcp_flows.values,
                            name=fcp,
                            boxmean='sd',  # Show mean and standard deviation
                            marker_color='#114B80'
                        ))
                
                fig_vol_dist.update_layout(
                    title="Distribution des Flux Hebdomadaires par FCP",
                    xaxis_title="FCP",
                    yaxis_title="Flux Hebdomadaire (FCFA)",
                    height=350,
                    template="plotly_white",
                    showlegend=False
                )
                
                st.plotly_chart(fig_vol_dist, use_container_width=True)
                
                # Add interpretation
                st.caption("""
                📊 **Interprétation:** Ce graphique montre la distribution des flux hebdomadaires pour chaque FCP. 
                Les boîtes représentent l'intervalle interquartile (IQR), les lignes montrent les valeurs min/max, 
                et les marqueurs indiquent la moyenne (losange) et l'écart-type. Plus la boîte est grande, 
                plus la volatilité des flux est élevée.
                """)
            
            # Volatility statistics table
            st.markdown("**📊 Tableau Récapitulatif de Volatilité:**")
            st.dataframe(
                df_volatility.style.format({
                    'Flux Moyen (FCFA)': '{:,.0f}',
                    'Écart-type (FCFA)': '{:,.0f}',
                    'CV (%)': '{:.2f}',
                    'Max Drawdown (%)': '{:.2f}'
                }).background_gradient(subset=['CV (%)'], cmap='RdYlGn_r'),
                use_container_width=True,
                hide_index=True
            )
            
            # Interpretation
            most_volatile_fcp = df_vol_sorted.iloc[0] if len(df_vol_sorted) > 0 else None
            least_volatile_fcp = df_vol_sorted.iloc[-1] if len(df_vol_sorted) > 0 else None
            
            if most_volatile_fcp is not None and least_volatile_fcp is not None:
                st.markdown(f"""
                <div class="interpretation-note">
                <strong>💡 Interprétation de la Volatilité:</strong><br>
                • <strong>Plus volatil:</strong> {most_volatile_fcp['FCP']} (CV: {most_volatile_fcp['CV (%)']:.1f}%) - flux irréguliers<br>
                • <strong>Plus stable:</strong> {least_volatile_fcp['FCP']} (CV: {least_volatile_fcp['CV (%)']:.1f}%) - flux réguliers<br>
                • Le coefficient de variation (CV) mesure la volatilité relative: plus il est élevé, plus les flux sont irréguliers<br>
                • Le Max Drawdown mesure la plus forte baisse relative depuis un sommet
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("##### 🔄 Analyse Approfondie de la Saisonnalité")
        
        # Info message that seasonality uses all available data
        st.info("ℹ️ L'analyse de saisonnalité utilise **toutes les données disponibles** (indépendamment des filtres temporels) pour détecter les patterns saisonniers de manière précise.")
        
        # FCP selector for seasonality analysis - SINGLE SELECTION
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            seasonality_fcp = st.selectbox(
                "Sélectionner un FCP pour analyse saisonnière",
                options=[ALL_FCP_LABEL] + all_fcps,
                index=0,
                key="seasonality_fcp",
                help="Choisissez un FCP pour analyser sa saisonnalité en comparaison avec le Total"
            )
        with col2:
            seasonality_metric = st.selectbox(
                "Métrique à analyser",
                options=['Flux Net', 'Souscriptions', 'Rachats'],
                key="seasonality_metric"
            )
        with col3:
            show_total_season = st.checkbox("Comparer au Total", value=True, key="show_total_season")
        
        # Convert to list format for compatibility with existing code
        if seasonality_fcp == ALL_FCP_LABEL:
            seasonality_fcps = []
        else:
            seasonality_fcps = [seasonality_fcp]
        
        # Prepare data based on metric - use full_df for seasonality (independent of temporal filters)
        if seasonality_metric == 'Flux Net':
            metric_col = 'Montant_Signe'
        elif seasonality_metric == 'Souscriptions':
            df_full_metric = full_df[full_df['Opérations'] == 'Souscriptions']
            metric_col = 'Montant'
        else:  # Rachats
            df_full_metric = full_df[full_df['Opérations'] == 'Rachats']
            metric_col = 'Montant'
        
        if seasonality_metric != 'Flux Net':
            df_work = df_full_metric
        else:
            df_work = full_df
        
        # 1. Monthly patterns visualization
        st.markdown(f"**📅 Patterns Mensuels - {seasonality_metric}**")
        
        # Calculate monthly averages
        if seasonality_fcps:
            # By FCP
            monthly_data = []
            for fcp in seasonality_fcps:
                df_fcp = df_work[df_work['FCP'] == fcp].copy()
                df_fcp['Month'] = df_fcp['Date'].dt.month
                monthly_avg = df_fcp.groupby('Month')[metric_col].mean()
                monthly_data.append({
                    'FCP': fcp,
                    'data': monthly_avg
                })
        else:
            # Aggregated
            df_work_copy = df_work.copy()
            df_work_copy['Month'] = df_work_copy['Date'].dt.month
            monthly_avg = df_work_copy.groupby('Month')[metric_col].mean()
            monthly_data = [{'FCP': ALL_FCP_LABEL, 'data': monthly_avg}]
        
        # Add total if requested - use full_df for seasonality (independent of temporal filters)
        if show_total_season:
            if seasonality_metric == 'Flux Net':
                df_all_work = full_df
            elif seasonality_metric == 'Souscriptions':
                df_all_work = full_df[full_df['Opérations'] == 'Souscriptions']
            else:
                df_all_work = full_df[full_df['Opérations'] == 'Rachats']
            
            df_all_work_copy = df_all_work.copy()
            df_all_work_copy['Month'] = df_all_work_copy['Date'].dt.month
            if seasonality_metric == 'Flux Net':
                monthly_avg_all = df_all_work_copy.groupby('Month')['Montant_Signe'].mean()
            else:
                monthly_avg_all = df_all_work_copy.groupby('Month')['Montant'].mean()
            monthly_data.append({'FCP': 'TOTAL', 'data': monthly_avg_all})
        
        # Month names for charts
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart by month
            fig_monthly = go.Figure()
            
            for item in monthly_data:
                fcp_name = item['FCP']
                data_series = item['data']
                
                # Ensure all months are present
                all_months = pd.Series(index=range(1, 13), dtype=float)
                all_months.update(data_series)
                
                is_total = (fcp_name == 'TOTAL')
                
                fig_monthly.add_trace(go.Bar(
                    x=[month_names[i] for i in range(12)],
                    y=all_months.values,
                    name=fcp_name,
                    opacity=0.6 if is_total else 1.0,
                    marker=dict(
                        line=dict(width=2, color='gray') if is_total else dict(width=0),
                        pattern=dict(shape="/" if is_total else "")
                    )
                ))
            
            fig_monthly.update_layout(
                title=f"Moyenne Mensuelle - {seasonality_metric}",
                xaxis_title="Mois",
                yaxis_title=f"{seasonality_metric} (FCFA)",
                height=400,
                template="plotly_white",
                barmode='group'
            )
            
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            # Heatmap by month and year
            st.markdown("**Heatmap Année x Mois**")
            
            # Prepare heatmap data (use aggregated or first FCP)
            if seasonality_fcps:
                df_heatmap = df_work[df_work['FCP'] == seasonality_fcps[0]].copy()
            else:
                df_heatmap = df_work.copy()
            
            df_heatmap['Year'] = df_heatmap['Date'].dt.year
            df_heatmap['Month'] = df_heatmap['Date'].dt.month
            
            heatmap_pivot = df_heatmap.groupby(['Year', 'Month'])[metric_col].sum().reset_index()
            heatmap_pivot = heatmap_pivot.pivot(index='Year', columns='Month', values=metric_col).fillna(0)
            
            if not heatmap_pivot.empty:
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=heatmap_pivot.values,
                    x=[month_names[i-1] for i in heatmap_pivot.columns],
                    y=heatmap_pivot.index,
                    colorscale='RdYlGn' if seasonality_metric == 'Flux Net' else 'Blues',
                    text=np.round(heatmap_pivot.values / 1000, 0),
                    texttemplate='%{text}K',
                    textfont={"size": 9},
                    colorbar=dict(title=f"{seasonality_metric} (FCFA)")
                ))
                
                fig_heatmap.update_layout(
                    title=f"Heatmap {seasonality_metric}",
                    xaxis_title="Mois",
                    yaxis_title="Année",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # 2. Seasonal decomposition (if statsmodels available and enough data)
        if STATSMODELS_AVAILABLE:
            st.markdown("**📊 Décomposition Saisonnière (Trend + Seasonal + Residual)**")
            
            # Use aggregated data or first selected FCP
            if seasonality_fcps:
                df_decomp = df_work[df_work['FCP'] == seasonality_fcps[0]].set_index('Date').resample('M')[metric_col].sum()
                decomp_title = f"{seasonality_fcps[0]}"
            else:
                df_decomp = df_work.set_index('Date').resample('M')[metric_col].sum()
                decomp_title = "Tous les FCP"
            
            if len(df_decomp) >= MIN_SEASONALITY_PERIODS:
                try:
                    # Perform seasonal decomposition
                    decomposition = seasonal_decompose(df_decomp, model='additive', period=12)
                    
                    # Create subplots
                    from plotly.subplots import make_subplots
                    
                    fig_decomp = make_subplots(
                        rows=4, cols=1,
                        subplot_titles=("Données Observées", "Tendance", "Saisonnalité", "Résidus"),
                        vertical_spacing=0.08,
                        row_heights=[0.25, 0.25, 0.25, 0.25]
                    )
                    
                    # Observed
                    fig_decomp.add_trace(
                        go.Scatter(x=df_decomp.index, y=df_decomp.values, mode='lines', 
                                  name='Observé', line=dict(color='#114B80')),
                        row=1, col=1
                    )
                    
                    # Trend
                    fig_decomp.add_trace(
                        go.Scatter(x=decomposition.trend.index, y=decomposition.trend.values, 
                                  mode='lines', name='Tendance', line=dict(color='#567389', width=2)),
                        row=2, col=1
                    )
                    
                    # Seasonal
                    fig_decomp.add_trace(
                        go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal.values,
                                  mode='lines', name='Saisonnalité', line=dict(color='#ACC7DF', width=2)),
                        row=3, col=1
                    )
                    
                    # Residual
                    fig_decomp.add_trace(
                        go.Scatter(x=decomposition.resid.index, y=decomposition.resid.values,
                                  mode='lines', name='Résidus', line=dict(color='lightgray')),
                        row=4, col=1
                    )
                    
                    fig_decomp.update_layout(
                        height=800,
                        title_text=f"Décomposition Saisonnière - {decomp_title}",
                        showlegend=False,
                        template="plotly_white"
                    )
                    
                    fig_decomp.update_xaxes(title_text="Date", row=4, col=1)
                    
                    st.plotly_chart(fig_decomp, use_container_width=True)
                    
                    # Seasonal strength metrics
                    var_residual = np.var(decomposition.resid.dropna())
                    var_seasonal_resid = np.var(decomposition.seasonal.dropna() + decomposition.resid.dropna())
                    seasonal_strength = max(0, 1 - (var_residual / var_seasonal_resid)) if var_seasonal_resid != 0 else 0
                    
                    # Identify best and worst months
                    seasonal_by_month = decomposition.seasonal.groupby(decomposition.seasonal.index.month).mean()
                    best_month = seasonal_by_month.idxmax()
                    worst_month = seasonal_by_month.idxmin()
                    best_month_value = seasonal_by_month.max()
                    worst_month_value = seasonal_by_month.min()
                    
                    st.markdown(f"""
                    <div class="interpretation-note">
                    <strong>💡 Interprétation de la Décomposition Saisonnière:</strong><br>
                    • <strong>Force saisonnière:</strong> {seasonal_strength*100:.1f}% (plus proche de 100% = saisonnalité forte)<br>
                    • <strong>Meilleur mois:</strong> {month_names[best_month-1]} (+{best_month_value:,.0f} FCFA en moyenne)<br>
                    • <strong>Mois le plus faible:</strong> {month_names[worst_month-1]} ({worst_month_value:,.0f} FCFA en moyenne)<br>
                    • <strong>Tendance:</strong> {"📈 Hausse" if decomposition.trend.dropna().iloc[-1] > decomposition.trend.dropna().iloc[0] else "📉 Baisse"} sur la période<br>
                    • Les résidus représentent les variations non expliquées par la tendance et la saisonnalité
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.info(f"Impossible de calculer la décomposition saisonnière: {str(e)[:150]}")
            else:
                st.info(f"Au moins {MIN_SEASONALITY_PERIODS} mois de données nécessaires pour la décomposition saisonnière.")
        else:
            st.info("Module statsmodels non disponible pour l'analyse de saisonnalité avancée.")
        
        # 3. Radar chart for seasonal patterns
        st.markdown("**🕸️ Radar Chart - Patterns Mensuels**")
        
        # Separate FCP selector for radar chart (multi-select)
        radar_fcps = st.multiselect(
            "Sélectionner des FCP pour comparer les profils saisonniers",
            options=all_fcps,
            default=[],
            key="radar_fcps",
            help="Par défaut (aucune sélection), seul le profil saisonnier du Total est affiché. Sélectionnez des FCP pour comparer leurs profils saisonniers au Total."
        )
        
        # Build radar chart data
        radar_monthly_data = []
        
        # Always include Total in radar chart
        if seasonality_metric == 'Flux Net':
            df_all_work = full_df
            metric_col_radar = 'Montant_Signe'
        elif seasonality_metric == 'Souscriptions':
            df_all_work = full_df[full_df['Opérations'] == 'Souscriptions']
            metric_col_radar = 'Montant'
        else:
            df_all_work = full_df[full_df['Opérations'] == 'Rachats']
            metric_col_radar = 'Montant'
        
        df_all_work_copy = df_all_work.copy()
        df_all_work_copy['Month'] = df_all_work_copy['Date'].dt.month
        monthly_avg_all = df_all_work_copy.groupby('Month')[metric_col_radar].mean()
        radar_monthly_data.append({'FCP': 'TOTAL', 'data': monthly_avg_all})
        
        # Add selected FCPs for radar chart
        if radar_fcps:
            for fcp in radar_fcps:
                # Use df_all_work for consistency with Total data source
                df_fcp = df_all_work[df_all_work['FCP'] == fcp].copy()
                df_fcp['Month'] = df_fcp['Date'].dt.month
                monthly_avg = df_fcp.groupby('Month')[metric_col_radar].mean()
                radar_monthly_data.append({
                    'FCP': fcp,
                    'data': monthly_avg
                })
        
        fig_radar = go.Figure()
        
        # Track max normalized value for chart range
        max_normalized_value = 0
        
        for item in radar_monthly_data:
            fcp_name = item['FCP']
            data_series = item['data']
            
            # Ensure all months are present
            all_months = pd.Series(index=range(1, 13), dtype=float)
            all_months.update(data_series)
            
            # Normalize to percentage of annual average for better comparison
            annual_avg = all_months.mean()
            normalized_values = (all_months / annual_avg * 100) if annual_avg != 0 else all_months
            
            # Track maximum for range calculation
            if not normalized_values.empty:
                max_normalized_value = max(max_normalized_value, normalized_values.max())
            
            is_total = (fcp_name == 'TOTAL')
            
            fig_radar.add_trace(go.Scatterpolar(
                r=normalized_values.values.tolist() + [normalized_values.values[0]],  # Close the loop
                theta=month_names + [month_names[0]],
                name=fcp_name,
                fill='toself' if not is_total else None,
                opacity=0.4 if is_total else 0.6,
                line=dict(dash='dash' if is_total else 'solid', width=2 if is_total else 1.5)
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(DEFAULT_RADAR_RANGE, max_normalized_value * 1.1 if max_normalized_value > 0 else DEFAULT_RADAR_RANGE)]
                )
            ),
            title=f"Patterns Saisonniers Normalisés (100 = moyenne annuelle)",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Add interpretation card based on FCP selection and metric
        st.markdown("**💡 Carte d'Interprétation des Résultats**")
        
        # Determine which FCP(s) are being analyzed
        if seasonality_fcp == ALL_FCP_LABEL or not seasonality_fcps:
            analysis_scope = "Tous les FCP"
            fcp_desc = "l'ensemble des FCP"
        else:
            analysis_scope = seasonality_fcp
            fcp_desc = f"le FCP {seasonality_fcp}"
        
        # Generate interpretation based on the metric
        if seasonality_metric == "Flux Net":
            metric_desc = "flux nets (souscriptions - rachats)"
            metric_interpretation = """
            Les flux nets représentent la différence entre les souscriptions et les rachats. 
            Un flux net positif indique une collecte nette (plus de souscriptions que de rachats), 
            tandis qu'un flux net négatif indique une décollecte nette.
            """
        elif seasonality_metric == "Souscriptions":
            metric_desc = "souscriptions"
            metric_interpretation = """
            Les souscriptions représentent les nouveaux investissements dans les FCP. 
            Des pics de souscriptions peuvent indiquer des périodes de confiance des investisseurs 
            ou des campagnes de commercialisation réussies.
            """
        else:  # Rachats
            metric_desc = "rachats"
            metric_interpretation = """
            Les rachats représentent les retraits d'investissements des FCP. 
            Des pics de rachats peuvent indiquer des besoins de liquidités des investisseurs 
            ou une perte de confiance dans les FCP.
            """
        
        # Calculate key seasonal insights from the current selection
        if seasonality_fcps:
            df_insight = df_work[df_work['FCP'] == seasonality_fcps[0]].copy()
        else:
            df_insight = df_work.copy()
        
        df_insight['Month'] = df_insight['Date'].dt.month
        monthly_avg_insight = df_insight.groupby('Month')[metric_col].mean()
        
        if len(monthly_avg_insight) > 0:
            best_month_idx = monthly_avg_insight.idxmax()
            worst_month_idx = monthly_avg_insight.idxmin()
            best_month_name = month_names[best_month_idx-1]
            worst_month_name = month_names[worst_month_idx-1]
            best_month_val = monthly_avg_insight.max()
            worst_month_val = monthly_avg_insight.min()
            avg_val = monthly_avg_insight.mean()
            volatility_pct = (monthly_avg_insight.std() / abs(avg_val) * 100) if avg_val != 0 else 0
            
            seasonality_interpretation = f"""
            <div class="interpretation-note">
            <strong>📊 Analyse de la Saisonnalité pour {analysis_scope} - Métrique: {seasonality_metric}</strong><br><br>
            
            <strong>Métrique analysée:</strong><br>
            {metric_interpretation}
            
            <strong>Observations pour {fcp_desc}:</strong><br>
            <ul>
            <li><strong>Meilleur mois:</strong> {best_month_name} avec une moyenne de {best_month_val:,.0f} FCFA</li>
            <li><strong>Mois le plus faible:</strong> {worst_month_name} avec une moyenne de {worst_month_val:,.0f} FCFA</li>
            <li><strong>Moyenne annuelle:</strong> {avg_val:,.0f} FCFA</li>
            <li><strong>Volatilité saisonnière:</strong> {volatility_pct:.1f}% (coefficient de variation mensuel)</li>
            </ul>
            
            <strong>Recommandations:</strong><br>
            """
            
            if volatility_pct > HIGH_VOLATILITY_THRESHOLD:
                seasonality_interpretation += """
                <ul>
                <li>⚠️ Forte volatilité saisonnière détectée - planifier les besoins de liquidité en conséquence</li>
                <li>📅 Anticiper les variations saisonnières dans les prévisions de flux</li>
                </ul>
                """
            else:
                seasonality_interpretation += """
                <ul>
                <li>✅ Volatilité saisonnière modérée - flux relativement stables tout au long de l'année</li>
                <li>📈 Profiter des mois forts pour optimiser la commercialisation</li>
                </ul>
                """
            
            if best_month_val > avg_val * 1.5:
                seasonality_interpretation += f"""
                <li>💡 Le mois de {best_month_name} présente une activité exceptionnelle (+{((best_month_val/avg_val - 1)*100):.0f}% vs moyenne) - identifier les facteurs de succès</li>
                """
            
            seasonality_interpretation += """
            </div>
            """
            
            st.markdown(seasonality_interpretation, unsafe_allow_html=True)
        else:
            st.info("Données insuffisantes pour générer une interprétation détaillée.")
    
    # ===================
    # Section 8: Top Performers
    # ===================
    st.subheader("🏅 Classements et Performances - Tous les FCP")
    
    col1, col2, col3 = st.columns(3)
    
    # Présentation sous forme de cartes individuelles pour chaque classement
    with col1:
        top_sous = df_filtered[df_filtered['Opérations'] == 'Souscriptions'].groupby('FCP')['Montant'].sum().sort_values(ascending=False).head(5)
        st.markdown("""
        <div class="ranking-card">
            <h3>🥇 Top 5 Souscriptions</h3>
            <ul style="list-style:none; padding-left:0;">
        """, unsafe_allow_html=True)
        for i, (fcp, montant) in enumerate(top_sous.items(), 1):
            montant_m = montant / MILLIONS_DIVISOR
            st.markdown(f"""
                <li class="ranking-item">
                    <span class="ranking-number">{i}</span>
                    <span>{fcp}</span>
                    <span class="ranking-value">{montant_m:.2f}M FCFA</span>
                </li>
            """, unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)

    with col2:
        top_rachats = df_filtered[df_filtered['Opérations'] == 'Rachats'].groupby('FCP')['Montant'].sum().sort_values(ascending=False).head(5)
        st.markdown("""
        <div class="ranking-card">
            <h3>🔻 Top 5 Rachats</h3>
            <ul style="list-style:none; padding-left:0;">
        """, unsafe_allow_html=True)
        for i, (fcp, montant) in enumerate(top_rachats.items(), 1):
            montant_m = montant / MILLIONS_DIVISOR
            st.markdown(f"""
                <li class="ranking-item">
                    <span class="ranking-number">{i}</span>
                    <span>{fcp}</span>
                    <span class="ranking-value">{montant_m:.2f}M FCFA</span>
                </li>
            """, unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)

    with col3:
        top_net = df_filtered.groupby('FCP')['Montant_Signe'].sum().sort_values(ascending=False).head(5)
        st.markdown("""
        <div class="ranking-card">
            <h3>💎 Top 5 Flux Nets</h3>
            <ul style="list-style:none; padding-left:0;">
        """, unsafe_allow_html=True)
        for i, (fcp, montant) in enumerate(top_net.items(), 1):
            emoji = '🟢' if montant >= 0 else '🔴'
            montant_m = montant / MILLIONS_DIVISOR
            st.markdown(f"""
                <li class="ranking-item">
                    <span class="ranking-number">{i}</span>
                    <span>{fcp}</span>
                    <span class="ranking-value">{emoji} {montant_m:.2f}M FCFA</span>
                </li>
            """, unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # ===================
    # Section 9: Export Data
    # ===================
    with st.expander("📥 Exporter les données filtrées"):
        st.markdown("Téléchargez les données filtrées au format CSV")
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name=f'souscriptions_rachats_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )


if __name__ == "__main__":
    main()
