import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Importar funções utilitárias
from utils.loaders import prepare_region_data, prepare_driver_data, detect_anomalies
from utils.graphics import create_bar_chart, create_scatter_plot, create_map
from utils.filters import create_region_filter, filter_suspicious_entries
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def show(data):
    """
    Exibe análise de regiões e entregadores com maior incidência de fraudes.
    
    Args:
        data: Dicionário com DataFrames para análise
    """
    st.markdown("<h2 style='text-align: center;'>🧍 Regiões & Entregadores</h2>", unsafe_allow_html=True)
    
    # Verificar se os dados foram carregados
    if not data:
        st.error("Não foi possível carregar os dados para análise de regiões e entregadores.")
        return

    # Preparar dados
    df_region = prepare_region_data(data.get('fraud_region')) if 'fraud_region' in data else None
    df_drivers = prepare_driver_data(
        data.get('drivers'),
        data.get('suspicious_drivers')
    ) if 'drivers' in data or 'suspicious_drivers' in data else None
    
    # Verificar se temos pelo menos um conjunto de dados
    if (df_region is None or df_region.empty) and (df_drivers is None or df_drivers.empty):
        st.warning("Dados insuficientes para análise de regiões e entregadores.")
        return
    
    # Configuração de layout
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Criar abas para separar as análises
    tab1, tab2 = st.tabs(["🌎 Análise Regional", "👤 Perfil de Entregadores"])
    
    # Aba 1: Análise Regional
    with tab1:
        if df_region is not None and not df_region.empty:
            # Título da seção
            st.markdown("<h3>🌎 Análise por Região</h3>", unsafe_allow_html=True)
            
            # Filtro de região
            selected_region = create_region_filter(df_region, 'region', 'region_tab')
            
            # Aplicar filtro de região
            if selected_region != "Todas":
                df_region_filtered = df_region[df_region['region'] == selected_region]
            else:
                df_region_filtered = df_region
            
            # Seção 1: KPIs de região
            st.markdown("<h4>🔑 Indicadores Regionais</h4>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Total de regiões
            with col1:
                total_regions = len(df_region_filtered)
                st.markdown(
                    create_kpi_card(
                        "Total de Regiões", 
                        f"{total_regions}", 
                        "Regiões analisadas"
                    ), 
                    unsafe_allow_html=True
                )
            
            # Total de pedidos
            with col2:
                if 'total_pedidos' in df_region_filtered.columns:
                    total_orders = df_region_filtered['total_pedidos'].sum()
                    st.markdown(
                        create_kpi_card(
                            "Total de Pedidos", 
                            f"{total_orders:,}".replace(',', '.'), 
                            "Pedidos nas regiões"
                        ), 
                        unsafe_allow_html=True
                    )
            
            # Total de itens faltantes
            with col3:
                if 'total_itens_faltantes' in df_region_filtered.columns:
                    total_missing = df_region_filtered['total_itens_faltantes'].sum()
                    st.markdown(
                        create_kpi_card(
                            "Itens Faltantes", 
                            f"{total_missing:,}".replace(',', '.'), 
                            "Itens não entregues",
                            color="danger"
                        ), 
                        unsafe_allow_html=True
                    )
            
            # Taxa média de fraude
            with col4:
                if 'percentual_fraude' in df_region_filtered.columns:
                    avg_fraud = df_region_filtered['percentual_fraude'].mean()
                    st.markdown(
                        create_kpi_card(
                            "Taxa Média de Fraude", 
                            f"{avg_fraud:.2f}%", 
                            "Média entre regiões",
                            color="warning" if avg_fraud > 5 else "success"
                        ), 
                        unsafe_allow_html=True
                    )
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Seção 2: Visualização de regiões
            st.markdown("<h4>🗺️ Distribuição Geográfica de Fraudes</h4>", unsafe_allow_html=True)
            
            # Verificar se temos dados de coordenadas
            has_coords = all(col in df_region_filtered.columns for col in ['latitude', 'longitude'])
            
            if has_coords:
                # Criar mapa
                fig = create_map(
                    df_region_filtered,
                    'latitude',
                    'longitude',
                    color_col='percentual_fraude',
                    size_col='total_pedidos',
                    hover_name='region',
                    hover_data=['total_itens_faltantes', 'media_itens_faltantes'],
                    title="Mapa de Fraudes por Região"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Se não temos coordenadas, mostrar gráfico de barras
                st.warning("Dados de geolocalização não disponíveis. Mostrando distribuição por região.")
                
                # Ordenar regiões por percentual de fraude
                region_sorted = df_region_filtered.sort_values('percentual_fraude', ascending=False)
                
                # Criar gráfico de barras
                fig = create_bar_chart(
                    region_sorted,
                    'region',
                    'percentual_fraude',
                    'Taxa de Fraude por Região (%)',
                    orientation='h'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Identificar região mais problemática
            top_region = df_region_filtered.sort_values('percentual_fraude', ascending=False).iloc[0]
            
            st.markdown(
                create_insight_box(
                    f"A região '{top_region['region']}' apresenta a maior taxa de fraude ({top_region['percentual_fraude']:.2f}%). "
                    f"Foram registrados {top_region['total_itens_faltantes']:,} itens faltantes em {top_region['total_pedidos']:,} pedidos. ".replace(',', '.') +
                    "Recomenda-se uma investigação aprofundada desta região.",
                    icon_type="warning"
                ),
                unsafe_allow_html=True
            )
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Seção 3: Comparação entre regiões
            st.markdown("<h4>📊 Comparação Entre Regiões</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Gráfico de barras com taxa de fraude por região
            with col1:
                region_sorted = df_region_filtered.sort_values('percentual_fraude', ascending=False)
                
                fig = create_bar_chart(
                    region_sorted,
                    'region',
                    'percentual_fraude',
                    'Taxa de Fraude por Região (%)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de barras com média de itens faltantes por região
            with col2:
                if 'media_itens_faltantes' in df_region_filtered.columns:
                    region_sorted_by_avg = df_region_filtered.sort_values('media_itens_faltantes', ascending=False)
                    
                    fig = create_bar_chart(
                        region_sorted_by_avg,
                        'region',
                        'media_itens_faltantes',
                        'Média de Itens Faltantes por Região'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Criar scatter plot para correlação
            if 'total_pedidos' in df_region_filtered.columns and 'percentual_fraude' in df_region_filtered.columns:
                fig = create_scatter_plot(
                    df_region_filtered,
                    'total_pedidos',
                    'percentual_fraude',
                    'Relação entre Volume de Pedidos e Taxa de Fraude',
                    text_column='region'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calcular correlação
                correlation = df_region_filtered['total_pedidos'].corr(df_region_filtered['percentual_fraude'])
                
                # Interpretar correlação
                if abs(correlation) < 0.3:
                    corr_message = (
                        f"Há uma correlação fraca ({correlation:.2f}) entre o volume de pedidos e a taxa de fraude. "
                        "O volume de entregas parece não afetar significativamente a ocorrência de fraudes."
                    )
                elif correlation >= 0.3:
                    corr_message = (
                        f"Há uma correlação positiva significativa ({correlation:.2f}) entre o volume de pedidos e a taxa de fraude. "
                        "Regiões com mais entregas tendem a ter maiores taxas de fraude, possivelmente devido à pressão operacional."
                    )
                else:
                    corr_message = (
                        f"Há uma correlação negativa significativa ({correlation:.2f}) entre o volume de pedidos e a taxa de fraude. "
                        "Regiões com menos entregas tendem a ter maiores taxas de fraude, sugerindo possíveis problemas operacionais nestas áreas."
                    )
                
                st.markdown(
                    create_insight_box(
                        corr_message,
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
        else:
            st.warning("Dados de região não disponíveis.")
    
    # Aba 2: Perfil de Entregadores
    with tab2:
        if df_drivers is not None and not df_drivers.empty:
            # Título da seção
            st.markdown("<h3>👤 Análise de Entregadores</h3>", unsafe_allow_html=True)
            
            # Controles de filtro
            col1, col2 = st.columns(2)
            
            with col1:
                # Filtro de idade
                if 'age' in df_drivers.columns:
                    min_age = int(df_drivers['age'].min())
                    max_age = int(df_drivers['age'].max())
                    
                    age_range = st.slider(
                        "Faixa Etária",
                        min_value=min_age,
                        max_value=max_age,
                        value=(min_age, max_age),
                        step=1
                    )
                    
                    # Aplicar filtro de idade
                    min_selected_age, max_selected_age = age_range
                    df_drivers_filtered = df_drivers[
                        (df_drivers['age'] >= min_selected_age) & 
                        (df_drivers['age'] <= max_selected_age)
                    ]
                else:
                    df_drivers_filtered = df_drivers
            
            with col2:
                # Filtro de suspeitos
                if 'suspeito' in df_drivers.columns:
                    show_suspicious_only = st.checkbox("Mostrar apenas motoristas suspeitos", value=False)
                    
                    if show_suspicious_only:
                        df_drivers_filtered = df_drivers_filtered[df_drivers_filtered['suspeito'] == True]
                
                # Filtro de número mínimo de entregas
                if 'orders_delivered' in df_drivers_filtered.columns or 'total_entregas' in df_drivers_filtered.columns:
                    col_name = 'orders_delivered' if 'orders_delivered' in df_drivers_filtered.columns else 'total_entregas'
                    
                    min_deliveries = int(df_drivers_filtered[col_name].min())
                    max_deliveries = int(df_drivers_filtered[col_name].max())
                    
                    min_deliver_threshold = st.slider(
                        "Mínimo de Entregas",
                        min_value=min_deliveries,
                        max_value=max_deliveries,
                        value=min_deliveries,
                        step=10
                    )
                    
                    # Aplicar filtro de entregas mínimas
                    df_drivers_filtered = df_drivers_filtered[df_drivers_filtered[col_name] >= min_deliver_threshold]
            
            # Verificar se ainda temos dados após os filtros
            if df_drivers_filtered.empty:
                st.warning("Nenhum entregador encontrado com os filtros selecionados.")
                return
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Seção 1: KPIs de entregadores
            st.markdown("<h4>🔑 Indicadores de Entregadores</h4>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Total de entregadores
            with col1:
                total_drivers = len(df_drivers_filtered)
                st.markdown(
                    create_kpi_card(
                        "Total de Entregadores", 
                        f"{total_drivers}", 
                        "Entregadores analisados"
                    ), 
                    unsafe_allow_html=True
                )
            
            # Total de entregadores suspeitos
            with col2:
                if 'suspeito' in df_drivers_filtered.columns:
                    suspicious_count = df_drivers_filtered['suspeito'].sum()
                    suspicious_pct = (suspicious_count / total_drivers) * 100
                    
                    st.markdown(
                        create_kpi_card(
                            "Entregadores Suspeitos", 
                            f"{suspicious_count} ({suspicious_pct:.1f}%)", 
                            "Com alta taxa de fraude",
                            color="danger" if suspicious_count > 10 else "warning"
                        ), 
                        unsafe_allow_html=True
                    )
            
            # Taxa média de fraude
            with col3:
                if 'percentual_fraude' in df_drivers_filtered.columns:
                    avg_fraud = df_drivers_filtered['percentual_fraude'].mean()
                    
                    st.markdown(
                        create_kpi_card(
                            "Taxa Média de Fraude", 
                            f"{avg_fraud:.2f}%", 
                            "Entre entregadores",
                            color="danger" if avg_fraud > 10 else "warning"
                        ), 
                        unsafe_allow_html=True
                    )
            
            # Idade média
            with col4:
                if 'age' in df_drivers_filtered.columns:
                    avg_age = df_drivers_filtered['age'].mean()
                    
                    st.markdown(
                        create_kpi_card(
                            "Idade Média", 
                            f"{avg_age:.1f} anos", 
                            "Dos entregadores"
                        ), 
                        unsafe_allow_html=True
                    )
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Seção 2: Top entregadores suspeitos
            st.markdown("<h4>⚠️ Entregadores com Maior Taxa de Fraude</h4>", unsafe_allow_html=True)
            
            # Verificar quais colunas estão disponíveis para ranking
            rank_column = None
            if 'percentual_fraude' in df_drivers_filtered.columns:
                rank_column = 'percentual_fraude'
            elif 'missing_ratio' in df_drivers_filtered.columns:
                rank_column = 'missing_ratio'
            elif 'problem_order_ratio' in df_drivers_filtered.columns:
                rank_column = 'problem_order_ratio'
            elif 'media_itens_faltantes' in df_drivers_filtered.columns:
                rank_column = 'media_itens_faltantes'
            
            if rank_column is not None:
                # Ordenar por coluna de ranking
                top_drivers = df_drivers_filtered.sort_values(rank_column, ascending=False).head(10)
                
                # Definir nome da coluna para display
                driver_name_col = 'driver_name' if 'driver_name' in top_drivers.columns else 'nome' if 'nome' in top_drivers.columns else None
                
                if driver_name_col:
                    # Criar gráfico de barras
                    fig = create_bar_chart(
                        top_drivers,
                        driver_name_col,
                        rank_column,
                        f'Top 10 Entregadores por {rank_column.replace("_", " ").title()}',
                        orientation='h'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Exibir tabela com detalhes
                    st.markdown("<h4>Detalhes dos Entregadores Mais Críticos</h4>", unsafe_allow_html=True)
                    
                    # Preparar colunas para exibição
                    display_cols = [driver_name_col, 'age', rank_column]
                    
                    # Adicionar colunas de entregas e itens faltantes se disponíveis
                    if 'orders_delivered' in top_drivers.columns:
                        display_cols.append('orders_delivered')
                    elif 'total_entregas' in top_drivers.columns:
                        display_cols.append('total_entregas')
                    
                    if 'total_missing_items' in top_drivers.columns:
                        display_cols.append('total_missing_items')
                    elif 'itens_faltantes' in top_drivers.columns:
                        display_cols.append('itens_faltantes')
                    
                    # Garantir que temos todas as colunas
                    display_cols = [col for col in display_cols if col in top_drivers.columns]
                    
                    # Renomear colunas para exibição
                    rename_map = {
                        driver_name_col: 'Entregador',
                        'age': 'Idade',
                        'percentual_fraude': 'Taxa de Fraude (%)',
                        'missing_ratio': 'Taxa de Itens Faltantes',
                        'problem_order_ratio': 'Taxa de Problemas',
                        'media_itens_faltantes': 'Média de Itens Faltantes',
                        'orders_delivered': 'Entregas Realizadas',
                        'total_entregas': 'Entregas Realizadas',
                        'total_missing_items': 'Itens Faltantes',
                        'itens_faltantes': 'Itens Faltantes'
                    }
                    
                    display_df = top_drivers[display_cols].rename(columns={col: rename_map[col] for col in display_cols if col in rename_map})
                    
                    # Destacar os entregadores mais críticos
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=350
                    )
            else:
                st.warning("Dados insuficientes para ranquear entregadores.")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Seção 3: Análise exploratória
            st.markdown("<h4>📊 Análise Exploratória de Entregadores</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Distribuição por idade
            with col1:
                if 'age' in df_drivers_filtered.columns:
                    # Agrupar por faixa etária
                    df_drivers_filtered['faixa_etaria'] = pd.cut(
                        df_drivers_filtered['age'],
                        bins=[18, 25, 35, 45, 55, 65, 100],
                        labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
                    )
                    
                    age_group = df_drivers_filtered.groupby('faixa_etaria').size().reset_index(name='contagem')
                    
                    # Criar gráfico de barras
                    fig = create_bar_chart(
                        age_group,
                        'faixa_etaria',
                        'contagem',
                        'Distribuição de Entregadores por Faixa Etária'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Verificar correlação entre idade e fraude
                    if rank_column is not None:
                        correlation = df_drivers_filtered['age'].corr(df_drivers_filtered[rank_column])
                        
                        if abs(correlation) < 0.2:
                            age_insight = (
                                f"Não há correlação significativa ({correlation:.2f}) entre a idade do entregador e a taxa de fraude."
                            )
                        elif correlation > 0:
                            age_insight = (
                                f"Há uma correlação positiva ({correlation:.2f}) entre a idade e a taxa de fraude. "
                                "Entregadores mais velhos tendem a apresentar mais problemas nas entregas."
                            )
                        else:
                            age_insight = (
                                f"Há uma correlação negativa ({correlation:.2f}) entre a idade e a taxa de fraude. "
                                "Entregadores mais jovens tendem a apresentar mais problemas nas entregas."
                            )
                        
                        st.markdown(
                            create_insight_box(
                                age_insight,
                                icon_type="info"
                            ),
                            unsafe_allow_html=True
                        )
            
            # Relação entre entregas e fraudes
            with col2:
                delivery_col = None
                if 'orders_delivered' in df_drivers_filtered.columns:
                    delivery_col = 'orders_delivered'
                elif 'total_entregas' in df_drivers_filtered.columns:
                    delivery_col = 'total_entregas'
                elif 'Trips' in df_drivers_filtered.columns:
                    delivery_col = 'Trips'
                
                if delivery_col and rank_column:
                    # Criar scatter plot
                    fig = create_scatter_plot(
                        df_drivers_filtered,
                        delivery_col,
                        rank_column,
                        f'Relação entre Número de Entregas e {rank_column.replace("_", " ").title()}'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calcular correlação
                    correlation = df_drivers_filtered[delivery_col].corr(df_drivers_filtered[rank_column])
                    
                    if abs(correlation) < 0.2:
                        delivery_insight = (
                            f"Não há correlação significativa ({correlation:.2f}) entre o volume de entregas e a taxa de fraude. "
                            "Outros fatores parecem influenciar mais as ocorrências."
                        )
                    elif correlation > 0:
                        delivery_insight = (
                            f"Há uma correlação positiva ({correlation:.2f}) entre o volume de entregas e a taxa de fraude. "
                            "Entregadores com mais entregas tendem a apresentar mais problemas, possivelmente devido à pressão por produtividade."
                        )
                    else:
                        delivery_insight = (
                            f"Há uma correlação negativa ({correlation:.2f}) entre o volume de entregas e a taxa de fraude. "
                            "Entregadores com menos entregas tendem a apresentar mais problemas, sugerindo possível falta de experiência ou treinamento."
                        )
                    
                    st.markdown(
                        create_insight_box(
                            delivery_insight,
                            icon_type="info"
                        ),
                        unsafe_allow_html=True
                    )
            
            # Detecção de anomalias
            if rank_column:
                st.markdown("<h4>🔍 Detecção de Entregadores Anômalos</h4>", unsafe_allow_html=True)
                
                # Detectar anomalias no ranking
                df_anomalies = detect_anomalies(df_drivers_filtered, rank_column)
                
                # Contar anomalias
                anomaly_count = df_anomalies['anomalia'].sum()
                
                if anomaly_count > 0:
                    # Filtrar apenas anomalias
                    df_anomalies_only = df_anomalies[df_anomalies['anomalia']].sort_values(rank_column, ascending=False)
                    
                    # Exibir contador de anomalias
                    st.warning(f"Foram detectados {anomaly_count} entregadores com comportamento anômalo.")
                    
                    # Exibir gráfico com todas as observações, destacando anomalias
                    driver_name_col = 'driver_name' if 'driver_name' in df_anomalies else 'nome' if 'nome' in df_anomalies else None
                    
                    if driver_name_col and delivery_col:
                        fig = px.scatter(
                            df_anomalies,
                            x=delivery_col,
                            y=rank_column,
                            color='anomalia',
                            hover_name=driver_name_col,
                            title=f'Detecção de Anomalias: Entregadores com {rank_column.replace("_", " ").title()} Atípica',
                            color_discrete_map={True: 'red', False: 'blue'}
                        )
                        
                        fig.update_layout(
                            xaxis_title="Número de Entregas",
                            yaxis_title=rank_column.replace("_", " ").title(),
                            legend_title="Anomalia",
                            font=dict(family="sans serif"),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Lista dos entregadores anômalos
                        st.markdown("<h5>Entregadores com Comportamento Anômalo:</h5>", unsafe_allow_html=True)
                        
                        # Preparar colunas para exibição
                        anomaly_cols = [driver_name_col, 'age', rank_column, delivery_col]
                        anomaly_cols = [col for col in anomaly_cols if col in df_anomalies_only.columns]
                        
                        # Renomear colunas
                        rename_map = {
                            driver_name_col: 'Entregador',
                            'age': 'Idade',
                            'percentual_fraude': 'Taxa de Fraude (%)',
                            'missing_ratio': 'Taxa de Itens Faltantes',
                            'problem_order_ratio': 'Taxa de Problemas',
                            'media_itens_faltantes': 'Média de Itens Faltantes',
                            'orders_delivered': 'Entregas Realizadas',
                            'total_entregas': 'Entregas Realizadas',
                            'Trips': 'Entregas Realizadas'
                        }
                        
                        anomaly_df = df_anomalies_only[anomaly_cols].rename(columns={col: rename_map[col] for col in anomaly_cols if col in rename_map})
                        
                        st.dataframe(
                            anomaly_df,
                            use_container_width=True
                        )
                        
                        st.markdown(
                            create_insight_box(
                                "Os entregadores destacados apresentam padrões significativamente diferentes dos demais, "
                                "com taxas de fraude estatisticamente anômalas. Recomenda-se uma investigação prioritária destes casos.",
                                icon_type="warning"
                            ),
                            unsafe_allow_html=True
                        )
                else:
                    st.success("Não foram detectados entregadores com comportamento estatisticamente anômalo.")
        else:
            st.warning("Dados de entregadores não disponíveis.")
    
    # Adicionar narrativa na barra lateral
    with st.sidebar:
        st.markdown("<h3>🧍 Análise de Entregadores</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        ### Compreendendo o Fator Humano
        
        A análise de entregadores e regiões permite:
        
        1. **Identificar padrões geográficos** de concentração de fraudes
        2. **Detectar entregadores anômalos** com taxas de fraude atípicas
        3. **Correlacionar fatores demográficos** com ocorrências de fraude
        4. **Priorizar investigações** com base em evidências estatísticas
        
        #### Como aplicar estes insights:
        
        - Verifique se há concentração regional de fraudes
        - Identifique entregadores com comportamento estatisticamente anômalo
        - Analise possíveis fatores externos (distância, tráfego) que afetam regiões específicas
        - Considere programas de treinamento focados em grupos específicos de entregadores
        
        > **Dica**: Combine esta análise com as características dos produtos 
        > frequentemente relatados como não entregues para criar um perfil 
        > completo de risco.
        """)