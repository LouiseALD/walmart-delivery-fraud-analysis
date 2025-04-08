import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Importar funções utilitárias
from utils.loaders import prepare_fraud_trend_data, prepare_region_data
from utils.graphics import create_time_series, create_pie_chart, create_gauge_chart, create_bar_chart
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def show(data):
    """
    Exibe o panorama geral de fraudes em entregas.
    
    Args:
        data: Dicionário com DataFrames para análise
    """
    st.markdown("<h2 style='text-align: center;'>📊 Panorama Geral de Fraudes em Entregas</h2>", unsafe_allow_html=True)
    
    # Verificar se os dados foram carregados
    if not data or 'fraud_trend' not in data or data['fraud_trend'] is None or data['fraud_trend'].empty:
        st.error("Não foi possível carregar os dados para o panorama geral.")
        return
    
    # Preparar dados
    df_fraud_trend = prepare_fraud_trend_data(data['fraud_trend'])
    df_fraud_region = prepare_region_data(data['fraud_region']) if 'fraud_region' in data else None
    df_missing_products = data.get('missing_products')
    df_suspicious_drivers = data.get('suspicious_drivers')
    
    # Configuração de layout
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 1: KPIs principais
    st.markdown("<h3>🔑 Indicadores de Desempenho (KPIs)</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total de pedidos
    with col1:
        if df_fraud_trend is not None and not df_fraud_trend.empty:
            total_orders = df_fraud_trend['total_pedidos'].sum()
            st.markdown(
                create_kpi_card(
                    "Total de Pedidos", 
                    f"{total_orders:,}".replace(',', '.'), 
                    "Pedidos analisados no período"
                ), 
                unsafe_allow_html=True
            )
    
    # Total de itens faltantes
    with col2:
        if df_fraud_trend is not None and not df_fraud_trend.empty:
            total_missing_items = df_fraud_trend['itens_faltantes'].sum()
            st.markdown(
                create_kpi_card(
                    "Itens Faltantes", 
                    f"{total_missing_items:,}".replace(',', '.'), 
                    "Total de itens não entregues",
                    color="danger"
                ), 
                unsafe_allow_html=True
            )
    
    # Percentual médio de fraudes
    with col3:
        if df_fraud_trend is not None and not df_fraud_trend.empty:
            avg_fraud_rate = df_fraud_trend['percentual_fraude'].mean()
            st.markdown(
                create_kpi_card(
                    "Taxa Média de Fraude", 
                    f"{avg_fraud_rate:.2f}%", 
                    "Média de fraudes no período",
                    color="warning" if avg_fraud_rate > 5 else "success"
                ), 
                unsafe_allow_html=True
            )
    
    # Motoristas suspeitos
    with col4:
        if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
            suspicious_count = len(df_suspicious_drivers)
            st.markdown(
                create_kpi_card(
                    "Motoristas Suspeitos", 
                    f"{suspicious_count}", 
                    "Motoristas com alta taxa de fraude",
                    color="danger" if suspicious_count > 10 else "warning"
                ), 
                unsafe_allow_html=True
            )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 2: Gráficos principais
    col1, col2 = st.columns([2, 1])
    
    # Gráfico de tendência de fraudes
    with col1:
        st.markdown("<h3>📈 Tendência de Fraudes</h3>", unsafe_allow_html=True)
        
        if df_fraud_trend is not None and not df_fraud_trend.empty:
            # Criar gráfico de tendência
            fig = create_time_series(
                df_fraud_trend,
                'date',
                'percentual_fraude',
                'Evolução do Percentual de Fraudes',
                add_trendline=True,
                secondary_y_column='itens_faltantes'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Adicionar insights
            last_30_days = df_fraud_trend[df_fraud_trend['date'] >= df_fraud_trend['date'].max() - pd.Timedelta(days=30)]
            current_trend = last_30_days['percentual_fraude'].iloc[-1] - last_30_days['percentual_fraude'].iloc[0]
            
            if current_trend > 0:
                st.markdown(
                    create_insight_box(
                        f"⚠️ Alerta: A taxa de fraude aumentou {abs(current_trend):.2f}% nos últimos 30 dias. "
                        "É recomendável investigar as causas deste aumento.",
                        icon_type="warning"
                    ),
                    unsafe_allow_html=True
                )
            elif current_trend < 0:
                st.markdown(
                    create_insight_box(
                        f"✅ A taxa de fraude diminuiu {abs(current_trend):.2f}% nos últimos 30 dias. "
                        "As medidas de prevenção parecem estar funcionando.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
    
    # Distribuição por categoria
    with col2:
        st.markdown("<h3>🔄 Distribuição de Fraudes</h3>", unsafe_allow_html=True)
        
        # Verificar se temos dados de produtos ou regiões
        if df_missing_products is not None and not df_missing_products.empty and 'category' in df_missing_products.columns:
            # Agregar por categoria
            category_data = df_missing_products.groupby('category').agg({
                'total_relatos': 'sum'
            }).reset_index().sort_values('total_relatos', ascending=False)
            
            # Criar gráfico de pizza
            fig = create_pie_chart(
                category_data,
                'category',
                'total_relatos',
                'Fraudes por Categoria de Produto',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Encontrar categoria mais problemática
            top_category = category_data.iloc[0]['category']
            top_count = category_data.iloc[0]['total_relatos']
            total_count = category_data['total_relatos'].sum()
            
            st.markdown(
                create_insight_box(
                    f"A categoria '{top_category}' representa {(top_count/total_count*100):.1f}% de todas as fraudes. "
                    "Investigue os produtos desta categoria com prioridade.",
                    icon_type="info"
                ),
                unsafe_allow_html=True
            )
        elif df_fraud_region is not None and not df_fraud_region.empty:
            # Usar dados de região em vez de categoria
            fig = create_pie_chart(
                df_fraud_region,
                'region',
                'percentual_fraude',
                'Fraudes por Região',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Encontrar região mais problemática
            top_region = df_fraud_region.sort_values('percentual_fraude', ascending=False).iloc[0]['region']
            
            st.markdown(
                create_insight_box(
                    f"A região '{top_region}' apresenta a maior taxa de fraude. "
                    "Recomenda-se revisar os procedimentos de entrega nesta área.",
                    icon_type="info"
                ),
                unsafe_allow_html=True
            )
        else:
            st.info("Dados de distribuição insuficientes. Verifique a conexão com a base de dados.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 3: Destaques e Tendências
    st.markdown("<h3>🚨 Principais Alertas e Tendências</h3>", unsafe_allow_html=True)
    
    # Top motoristas suspeitos
    col1, col2 = st.columns(2)

    with col1:
            if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
                st.markdown("<h4>👤 Top 5 Motoristas com Maior Média de Itens Não Entregues por Entrega</h4>", unsafe_allow_html=True)

                # Renomear colunas para exibição mais amigável (sem alterar o df original)
                df_plot = df_suspicious_drivers.rename(columns={
                    "driver_name": "nome_motorista",
                    "percentual_fraude": "media_itens_fraudados"
                })

                # Verificar se colunas para cálculo corrigido existem
                if {'entregas_fraudadas', 'entregas_totais'}.issubset(df_plot.columns):
                    df_plot["media_itens_fraudados"] = (
                        df_plot["entregas_fraudadas"] / df_plot["entregas_totais"]
                    ) * 100
                    coluna_para_plotar = "media_itens_fraudados"
                    titulo = "Top 5 Motoristas por % de Entregas com Itens Não Entregues"
                elif "media_itens_fraudados" in df_plot.columns:
                    st.info("Usando coluna já existente 'media_itens_fraudados'.")
                    coluna_para_plotar = "media_itens_fraudados"
                    titulo = "Top 5 Motoristas por Média de Itens Não Entregues por Entrega (%)"
                else:
                    st.error("Nenhuma coluna apropriada encontrada para calcular a taxa de fraude.")
                    coluna_para_plotar = None

                # Plotar gráfico, se possível
                if coluna_para_plotar:
                    top_motoristas = df_plot.sort_values(coluna_para_plotar, ascending=False).head(5)

                    fig = create_bar_chart(
                        top_motoristas,
                        'Nome Motorista',         # eixo X
                        coluna_para_plotar,       # eixo Y
                        titulo,
                        orientation='h',
                        height=300
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Adicionar legenda explicativa
                    st.caption("📌 Este indicador representa a média de itens não entregues por entrega realizada. "
                            "Valores acima de 100% indicam que, em média, mais de 1 item foi reportado como não entregue por entrega.")



    
    # Top produtos não entregues
    with col2:
        if df_missing_products is not None and not df_missing_products.empty:
            st.markdown("<h4>📦 Produtos mais Reportados como Não Entregues</h4>", unsafe_allow_html=True)
            
            # Selecionar top 5 produtos por número de relatos
            top_products = df_missing_products.sort_values('total_relatos', ascending=False).head(5)
            
            # Criar gráfico de barras
            fig = create_bar_chart(
                top_products,
                'product_name',
                'total_relatos',
                'Top 5 Produtos por Relatos de Não Entrega',
                orientation='h',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Seção 4: Medidor de Saúde Geral
    st.markdown("<h3>📉 Medidor de Saúde do Sistema de Entregas</h3>", unsafe_allow_html=True)
    
    # Calcular índice de saúde baseado em vários fatores
    health_score = 100
    
    if df_fraud_trend is not None and not df_fraud_trend.empty:
        # Reduzir pontuação com base na taxa média de fraude
        avg_fraud_rate = df_fraud_trend['percentual_fraude'].mean()
        health_score -= min(avg_fraud_rate * 5, 50)  # Reduzir até 50 pontos
        
        # Reduzir pontuação com base na tendência recente
        last_30_days = df_fraud_trend[df_fraud_trend['date'] >= df_fraud_trend['date'].max() - pd.Timedelta(days=30)]
        if not last_30_days.empty and len(last_30_days) > 1:
            current_trend = last_30_days['percentual_fraude'].iloc[-1] - last_30_days['percentual_fraude'].iloc[0]
            health_score -= min(current_trend * 3, 20)  # Reduzir até 20 pontos se tendência positiva
    
    # Garantir que o score esteja entre 0 e 100
    health_score = max(0, min(100, health_score))
    
    # Determinar cor baseada na pontuação
    if health_score >= 70:
        score_color = "green"
        health_status = "Bom"
    elif health_score >= 40:
        score_color = "yellow"
        health_status = "Atenção"
    else:
        score_color = "red"
        health_status = "Crítico"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        fig = create_gauge_chart(
            health_score,
            f"Status do Sistema de Entregas: {health_status}",
            min_value=0,
            max_value=100,
            threshold_values=[40, 70],
            threshold_colors=['red', 'yellow', 'green'],
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Exibir recomendações baseadas no status de saúde
    if health_score < 40:
        st.markdown(
            create_insight_box(
                "🚨 Situação crítica detectada! Recomenda-se uma revisão imediata dos procedimentos de entrega "
                "e uma investigação aprofundada dos motoristas e regiões com maior índice de fraude.",
                icon_type="alert"
            ),
            unsafe_allow_html=True
        )
    elif health_score < 70:
        st.markdown(
            create_insight_box(
                "⚠️ Há margem significativa para melhorias. Verifique os motoristas com maior taxa de fraude "
                "e implemente verificações adicionais para produtos frequentemente relatados como não entregues.",
                icon_type="warning"
            ),
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            create_insight_box(
                "✅ O sistema de entregas está funcionando adequadamente, mas mantenha monitoramento constante "
                "para detectar precocemente qualquer alteração de padrão.",
                icon_type="info"
            ),
            unsafe_allow_html=True
        )
    
    # Narrativa contextual na barra lateral
    with st.sidebar:
        st.markdown("<h3>📖 Narrativa Contextual</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        ### Detecção de Fraudes em Entregas
        
        O sistema de detecção de fraudes do Walmart analisa continuamente os padrões
        de entregas e relatos de clientes para identificar possíveis problemas.
        
        #### Principais Indicadores:
        
        - **Taxa de Fraude**: Percentual de pedidos com relatos de itens faltantes.
        - **Itens Faltantes**: Produtos pagos mas não recebidos pelos clientes.
        - **Motoristas Suspeitos**: Entregadores com alto índice de reclamações.
        - **Regiões Problemáticas**: Áreas com concentração anormal de fraudes.
        
        #### Como Usar Este Dashboard:
        
        1. Analise as tendências recentes no gráfico principal
        2. Verifique os produtos e categorias mais afetados
        3. Investigue os motoristas com maior índice de fraude
        4. Implemente ações corretivas baseadas nas recomendações
        
        > **Dica**: Use os filtros globais no topo da barra lateral para
        > refinar sua análise por período, categoria ou região.
        """)