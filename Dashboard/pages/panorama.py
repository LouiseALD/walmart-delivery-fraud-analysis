import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Importar funções utilitárias
from utils.loaders import prepare_fraud_trend_data, prepare_region_data
from utils.graphics import create_time_series, create_pie_chart, create_gauge_chart, create_bar_chart
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def create_case_introduction():
    """
    Cria uma introdução completa sobre o case de detecção de fraudes do Walmart
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="color: white; text-align: center; margin-bottom: 1rem;">
            🛒 Walmart Fraud Detection Dashboard
        </h1>
        <h3 style="color: #E8F4FD; text-align: center; margin-bottom: 2rem;">
            Dashboard de Detecção e Análise de Fraudes em Entregas
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Seção: Sobre o Case
    st.markdown("---")
    st.markdown("## Sobre o Case")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### O Problema
        
        O **Walmart**, uma das maiores redes varejistas do mundo, enfrenta um desafio crescente com **fraudes em entregas**. 
        Clientes relatam não receber produtos pelos quais pagaram, gerando:
        
        -  **Perdas financeiras** significativas
        -  **Insatisfação do cliente** e perda de confiança
        -  **Dificuldade em identificar** se é fraude real ou erro operacional
        -  **Desafios legais** e de conformidade
        -  **Falta de visibilidade** sobre padrões de fraude
        
        ### A Solução
        
        Esta **dashboard interativa** foi desenvolvida para:
        
         **Detectar padrões** suspeitos em entregas  
         **Identificar motoristas** com alta taxa de fraude  
         **Mapear produtos** mais vulneráveis  
         **Analisar tendências** temporais e geográficas  
         **Fornecer insights** acionáveis para tomada de decisão  
         **Automatizar a detecção** de anomalias  
        """)
    
    with col2:
        st.markdown("""
        ### Dados Analisados
        
        **Volume de Entregas:**
        - Milhares de pedidos diários
        - Centenas de motoristas
        - Múltiplas regiões geográficas
        
        **Indicadores Chave:**
        - Taxa de fraude por motorista
        - Produtos mais relatados
        - Padrões temporais
        - Concentração geográfica
        
        **Tempo Real:**
        - Atualização contínua
        - Alertas automáticos
        - Dashboards interativos
        """)
    
    # Seção: Objetivos
    st.markdown("---")
    st.markdown("## Objetivos da Dashboard")
    
    objectives = [
        {
            "icon": "🕵️",
            "title": "Detecção Proativa",
            "description": "Identificar padrões de fraude antes que causem perdas significativas"
        },
        {
            "icon": "📍",
            "title": "Localização Precisa",
            "description": "Mapear exatamente onde, quando e quem está envolvido em atividades suspeitas"
        },
        {
            "icon": "📈",
            "title": "Análise de Tendências",
            "description": "Compreender a evolução das fraudes ao longo do tempo para ação preventiva"
        },
        {
            "icon": "⚖️",
            "title": "Tomada de Decisão",
            "description": "Fornecer dados concretos para decisões de contratação, treinamento e processos"
        },
        {
            "icon": "💡",
            "title": "Insights Acionáveis",
            "description": "Converter dados em recomendações práticas para redução de fraudes"
        },
        {
            "icon": "🔄",
            "title": "Melhoria Contínua",
            "description": "Monitorar eficácia das medidas implementadas e ajustar estratégias"
        }
    ]
    
    cols = st.columns(3)
    for i, obj in enumerate(objectives):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
                        border-left: 4px solid #296D84; margin-bottom: 15px;">
                <h4>{obj['icon']} {obj['title']}</h4>
                <p style="margin-bottom: 0;">{obj['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Seção: Problemas que Resolve
    st.markdown("---")
    st.markdown("##  Problemas que a Dashboard propôe resolver")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ❌ Antes (Problemas)
        
        - **Detecção Manual:** Fraudes descobertas apenas após múltiplas reclamações
        - **Sem Padrões:** Incapacidade de identificar comportamentos sistemáticos
        - **Decisões Cegas:** Ações baseadas em intuição, não em dados
        - **Reação Tardia:** Problemas descobertos só após grandes perdas
        - **Falta de Visibilidade:** Sem visão holística do problema
        - **Processos Ineficientes:** Investigações demoradas e pouco direcionadas
        """)
    
    with col2:
        st.markdown("""
        ### ✅ Depois (Soluções)
        
        - **Detecção Automática:** Algoritmos identificam padrões suspeitos instantaneamente
        - **Reconhecimento de Padrões:** IA detecta comportamentos anômalos automaticamente
        - **Decisões Data-Driven:** Todas as ações baseadas em evidências concretas
        - **Prevenção Proativa:** Problemas identificados antes de causar grandes impactos
        - **Visão 360°:** Dashboard completa com todos os ângulos do problema
        - **Investigação Direcionada:** Recursos focados nos casos de maior probabilidade
        """)
    
    # Seção: Insights Principais
    st.markdown("---")
    st.markdown("##  Principais Insights Fornecidos")
    
    insights_categories = [
        {
            "category": "Análise de Motoristas",
            "insights": [
                "Quais motoristas têm taxa de fraude acima da média",
                "Padrões de comportamento suspeito por entregador",
                "Correlação entre experiência e índice de fraudes",
                "Identificação de motoristas que merecem investigação prioritária"
            ]
        },
        {
            "category": "Análise de Produtos",
            "insights": [
                "Quais produtos são mais frequentemente 'não entregues'",
                "Categorias de produtos mais vulneráveis",
                "Relação entre valor do produto e taxa de fraude",
                "Padrões de produtos fraudados por motorista específico"
            ]
        },
        {
            "category": "Análise Geográfica",
            "insights": [
                "Regiões com maior concentração de fraudes",
                "Rotas de entrega mais problemáticas",
                "Correlação entre localização e tipo de fraude",
                "Oportunidades de otimização logística"
            ]
        },
        {
            "category": "Análise Temporal",
            "insights": [
                "Horários de pico de atividade fraudulenta",
                "Sazonalidade das fraudes",
                "Tendências de crescimento ou redução",
                "Padrões de fim de semana vs dias úteis"
            ]
        }
    ]
    
    for insight_cat in insights_categories:
        with st.expander(f"**{insight_cat['category']}**", expanded=False):
            for insight in insight_cat['insights']:
                st.markdown(f"• {insight}")
    
    # Seção: Como Utilizar
    st.markdown("---")
    st.markdown("##  Como Utilizar Esta Dashboard")
    
    st.markdown("""
    ###  Navegação pela Dashboard
    
    A dashboard está organizada em **8 seções principais**, cada uma focada em um aspecto específico da análise:
    """)
    
    navigation_guide = [
        {
            "tab": "1️⃣ Panorama",
            "description": "Visão geral com KPIs principais e análise motorista vs produto",
            "use_case": "Comece aqui para ter uma visão completa da situação atual"
        },
        {
            "tab": "2️⃣ Análise Temporal",
            "description": "Padrões de fraude ao longo do tempo, sazonalidade e tendências",
            "use_case": "Identifique quando as fraudes mais acontecem"
        },
        {
            "tab": "3️⃣ Produtos & Categorias",
            "description": "Análise detalhada dos produtos mais afetados por fraudes",
            "use_case": "Descubra quais produtos precisam de proteção extra"
        },
        {
            "tab": "4️⃣ Regiões & Entregadores",
            "description": "Análise geográfica e perfil detalhado dos entregadores",
            "use_case": "Identifique áreas problemáticas e motoristas suspeitos"
        },
        {
            "tab": "5️⃣ Padrões Ocultos",
            "description": "Análise avançada com IA para detectar padrões não óbvios",
            "use_case": "Encontre conexões e anomalias que passariam despercebidas"
        },
        {
            "tab": "6️⃣ Diagnóstico",
            "description": "Análise de responsabilidade e atribuição de causas",
            "use_case": "Entenda as causas raiz dos problemas"
        },
        {
            "tab": "7️⃣ Evolução",
            "description": "Tendências e projeções futuras baseadas em dados históricos",
            "use_case": "Planeje ações preventivas baseadas em tendências"
        },
        {
            "tab": "8️ Recomendações",
            "description": "Sugestões práticas de ações baseadas na análise completa",
            "use_case": "Implemente soluções concretas para reduzir fraudes"
        }
    ]
    
    for guide in navigation_guide:
        st.markdown(f"""
        **{guide['tab']}**  
         *{guide['description']}*  
         **Quando usar:** {guide['use_case']}
        """)
    
    # Seção: Workflow Recomendado
    st.markdown("---")
    st.markdown("## 🔄 Workflow Recomendado")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        ### Para Gestores
        
        1. **Panorama** → Visão executiva
        2. **Evolução** → Tendências estratégicas
        3. **Diagnóstico** → Causas raiz
        4. **Recomendações** → Plano de ação
        
        ### Para Analistas
        
        1. **Padrões Ocultos** → Análise profunda
        2. **Produtos & Categorias** → Análise detalhada
        3. **Regiões & Entregadores** → Investigação específica
        4. **Análise Temporal** → Validação de hipóteses
        
        ### Para Ação Imediata
        
        1. **Panorama** → Casos críticos
        2. **Regiões & Entregadores** → Ação específica
        3. **Recomendações** → Implementação
        """)
    
    with col2:
        st.markdown("""
        ### Processo de Investigação Recomendado
        
        ** Passo 1: Identificação (Panorama)**
        - Verifique os KPIs principais
        - Identifique motoristas e produtos críticos
        - Observe tendências gerais
        
        ** Passo 2: Análise Detalhada**
        - Use "Padrões Ocultos" para correlações
        - Analise "Produtos & Categorias" para especificidades
        - Examine "Regiões & Entregadores" para contexto geográfico
        
        ** Passo 3: Contextualização**
        - Consulte "Análise Temporal" para sazonalidade
        - Revise "Evolução" para tendências históricas
        - Utilize "Diagnóstico" para causas raiz
    
        ** Passo 4: Ação**
        - Implemente sugestões de "Recomendações"
        - Configure alertas baseados nos insights
        - Monitore resultados continuamente
        
        ** Passo 5: Monitoramento**
        - Retorne ao "Panorama" para acompanhar evolução
        - Ajuste estratégias baseado em novos dados
        - Documente lições aprendidas
        """)
    
    # Seção: Alertas e Indicadores
    st.markdown("---")
    st.markdown("## Sistema de Alertas e Indicadores")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🔴 Alertas Críticos
        
        **Motoristas:**
        - Taxa de fraude ≥ 10%
        - Mais de 20 fraudes confirmadas
        - Padrão anômalo detectado
        
        **Produtos:**
        - >50 relatos de não entrega
        - Concentração >80% em um motorista
        - Pico súbito de reclamações
        """)
    
    with col2:
        st.markdown("""
        ### 🟠 Alertas de Atenção
        
        **Tendências:**
        - Crescimento >5% em 30 dias
        - Novos padrões emergentes
        - Desvios sazonais
        
        **Regiões:**
        - Taxa acima da média nacional
        - Concentração geográfica anômala
        """)
    
    with col3:
        st.markdown("""
        ### 🟢 Indicadores Positivos
        
        **Melhorias:**
        - Redução consistente de fraudes
        - Eficácia de medidas implementadas
        - Identificação proativa de riscos
        
        **Controle:**
        - Taxas dentro de parâmetros esperados
        - Distribuição equilibrada de casos
        """)
    
    # Call to Action
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #E8F6F3; padding: 20px; border-radius: 10px; border-left: 4px solid #16A085;">
        <h3> Pronto para Começar?</h3>
        <p><strong>Role para baixo</strong> para ver os dados em tempo real e começar sua análise!</p>
        <p> <strong>Dica:</strong> Use a barra lateral para filtrar dados por período, categoria ou região específica.</p>
    </div>
    """, unsafe_allow_html=True)

def create_driver_product_analysis(df_drivers, df_products=None, df_fraud_details=None):
    """
    Cria análise detalhada de quais produtos cada motorista está fraudando
    """
    results = {}
    
    # Tentar múltiplas fontes de dados para relacionar motorista-produto
    data_source = None
    
    if df_fraud_details is not None and not df_fraud_details.empty:
        data_source = df_fraud_details
    elif df_products is not None and not df_products.empty:
        data_source = df_products
    
    if data_source is None:
        return None, None, None
    
    # Detectar colunas automaticamente
    driver_col = None
    product_col = None
    fraud_col = None
    
    # Possíveis nomes de colunas
    driver_columns = ['driver_name', 'motorista', 'nome_motorista', 'driver_id', 'entregador']
    product_columns = ['product_name', 'produto', 'item', 'product_id', 'nome_produto']
    fraud_columns = ['fraud_count', 'relatos_fraude', 'itens_faltantes', 'quantidade_fraude', 'quantidade', 'qtd_fraude']
    
    for col in driver_columns:
        if col in data_source.columns:
            driver_col = col
            break
    
    for col in product_columns:
        if col in data_source.columns:
            product_col = col
            break
    
    for col in fraud_columns:
        if col in data_source.columns:
            fraud_col = col
            break
    
    if not (driver_col and product_col and fraud_col):
        return None, None, None
    
    # Preparar dados agregados
    fraud_summary = data_source.groupby([driver_col, product_col])[fraud_col].sum().reset_index()
    fraud_summary = fraud_summary[fraud_summary[fraud_col] > 0]  # Apenas fraudes confirmadas
    
    # 1. Criar heatmap
    fraud_matrix = fraud_summary.pivot_table(
        index=driver_col,
        columns=product_col,
        values=fraud_col,
        fill_value=0
    )
    
    # Filtrar para mostrar apenas os mais relevantes
    top_drivers = fraud_matrix.sum(axis=1).nlargest(20).index
    top_products = fraud_matrix.sum(axis=0).nlargest(15).index
    
    fraud_matrix_filtered = fraud_matrix.loc[top_drivers, top_products]
    
    # Criar heatmap com anotações
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=fraud_matrix_filtered.values,
        x=fraud_matrix_filtered.columns,
        y=fraud_matrix_filtered.index,
        colorscale='Reds',
        showscale=True,
        colorbar=dict(title="Qtd de Fraudes"),
        text=fraud_matrix_filtered.values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoveremplate='<b>Motorista:</b> %{y}<br><b>Produto:</b> %{x}<br><b>Fraudes:</b> %{z}<extra></extra>'
    ))
    
    fig_heatmap.update_layout(
        title='Mapa de Fraudes: Quais Produtos Cada Motorista Está Fraudando',
        xaxis_title="Produtos",
        yaxis_title="Motoristas",
        height=600,
        font=dict(size=11)
    )
    fig_heatmap.update_xaxes(tickangle=45)
    
    # 2. Criar tabela detalhada por motorista
    driver_details = []
    for driver in fraud_summary[driver_col].unique():
        driver_data = fraud_summary[fraud_summary[driver_col] == driver]
        driver_data_sorted = driver_data.sort_values(fraud_col, ascending=False)
        
        total_frauds = driver_data[fraud_col].sum()
        top_product = driver_data_sorted.iloc[0][product_col]
        top_fraud_count = driver_data_sorted.iloc[0][fraud_col]
        products_frauded = len(driver_data)
        
        driver_details.append({
            'Motorista': driver,
            'Total de Fraudes': total_frauds,
            'Produto Mais Fraudado': top_product,
            'Qtd do Produto Principal': top_fraud_count,
            'Variedade de Produtos': products_frauded,
            'Produtos Fraudados': ', '.join([f"{row[product_col]} ({row[fraud_col]})" 
                                           for _, row in driver_data_sorted.head(5).iterrows()])
        })
    
    df_driver_details = pd.DataFrame(driver_details).sort_values('Total de Fraudes', ascending=False)
    
    # 3. Criar gráfico de barras empilhadas
    # Pegar top 10 motoristas
    top_drivers_list = df_driver_details.head(10)['Motorista'].tolist()
    fraud_data_top = fraud_summary[fraud_summary[driver_col].isin(top_drivers_list)]
    
    fig_stacked = px.bar(
        fraud_data_top,
        x=driver_col,
        y=fraud_col,
        color=product_col,
        title='Top 10 Motoristas: Distribuição de Fraudes por Produto',
        labels={
            driver_col: 'Motoristas',
            fraud_col: 'Quantidade de Fraudes',
            product_col: 'Produto'
        }
    )
    fig_stacked.update_layout(
        height=500,
        xaxis_tickangle=45,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
    )
    
    return fig_heatmap, df_driver_details, fig_stacked

def create_individual_driver_report(df_fraud_details, selected_driver):
    """
    Cria relatório individual para um motorista específico
    """
    if df_fraud_details is None or selected_driver is None:
        return None
    
    # Detectar colunas
    driver_col = None
    product_col = None
    fraud_col = None
    
    driver_columns = ['driver_name', 'motorista', 'nome_motorista', 'driver_id', 'entregador']
    product_columns = ['product_name', 'produto', 'item', 'product_id', 'nome_produto']
    fraud_columns = ['fraud_count', 'relatos_fraude', 'itens_faltantes', 'quantidade_fraude', 'quantidade', 'qtd_fraude']
    
    for col in driver_columns:
        if col in df_fraud_details.columns:
            driver_col = col
            break
    
    for col in product_columns:
        if col in df_fraud_details.columns:
            product_col = col
            break
    
    for col in fraud_columns:
        if col in df_fraud_details.columns:
            fraud_col = col
            break
    
    if not all([driver_col, product_col, fraud_col]):
        return None
    
    # Filtrar dados do motorista
    driver_data = df_fraud_details[df_fraud_details[driver_col] == selected_driver]
    
    if driver_data.empty:
        return None
    
    # Agregar por produto
    product_summary = driver_data.groupby(product_col)[fraud_col].sum().reset_index()
    product_summary = product_summary.sort_values(fraud_col, ascending=False)
    
    # Criar gráfico de pizza
    fig = px.pie(
        product_summary,
        values=fraud_col,
        names=product_col,
        title=f'Distribuição de Fraudes - {selected_driver}',
        hover_data=[fraud_col]
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Fraudes: %{value}<br>Percentual: %{percent}<extra></extra>'
    )
    
    return fig, product_summary

def show(data):
    """
    Exibe o panorama geral de fraudes em entregas com introdução completa do case.
    
    Args:
        data: Dicionário com DataFrames para análise
    """
    # Criar introdução completa do case
    create_case_introduction()
    
    # Verificar se os dados foram carregados
    if not data or 'fraud_trend' not in data or data['fraud_trend'] is None or data['fraud_trend'].empty:
        st.error("❌ Não foi possível carregar os dados para o panorama geral.")
        return
    
    # Preparar dados
    df_fraud_trend = prepare_fraud_trend_data(data['fraud_trend'])
    df_fraud_region = prepare_region_data(data['fraud_region']) if 'fraud_region' in data else None
    df_missing_products = data.get('missing_products')
    df_suspicious_drivers = data.get('suspicious_drivers')
    df_driver_products = data.get('driver_products')  # Nova fonte de dados para relacionar motoristas e produtos
    
    # Divisor para indicar início dos dados
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #F0F8FF; padding: 15px; border-radius: 10px; border-left: 4px solid #4169E1;">
        <h2>Dados em Tempo Real - Dashboard Interativa</h2>
        <p>A partir daqui você encontrará os dados reais de fraudes processados em tempo real. 
        Use os filtros na barra lateral para personalizar sua análise.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuração de layout
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 1: KPIs principais
    st.markdown("<h3> Indicadores de Desempenho (KPIs)</h3>", unsafe_allow_html=True)
    
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
        st.markdown("<h3> Tendência de Fraudes</h3>", unsafe_allow_html=True)
        
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
                        "f **Alerta**: A taxa de fraude aumentou {abs(current_trend):.2f}% nos últimos 30 dias. "
                        "É recomendável investigar as causas deste aumento.",
                        icon_type="warning"
                    ),
                    unsafe_allow_html=True
                )
            elif current_trend < 0:
                st.markdown(
                    create_insight_box(
                        f" **Melhoria**: A taxa de fraude diminuiu {abs(current_trend):.2f}% nos últimos 30 dias. "
                        "As medidas de prevenção parecem estar funcionando.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
    
    # Distribuição por categoria
    with col2:
        st.markdown("<h3> Distribuição de Fraudes</h3>", unsafe_allow_html=True)
        
        # Verificar se temos dados de produtos
        if df_missing_products is not None and not df_missing_products.empty:
            
            # Verificar qual coluna usar para agregação
            value_column = None
            if 'total_relatos' in df_missing_products.columns:
                value_column = 'total_relatos'
            elif 'itens_faltantes' in df_missing_products.columns:
                value_column = 'itens_faltantes'
            
            if 'category' in df_missing_products.columns and value_column:
                # Agregar por categoria
                category_data = df_missing_products.groupby('category').agg({
                    value_column: 'sum'
                }).reset_index().sort_values(value_column, ascending=False)
                
                # Renomear coluna para consistência
                category_data.rename(columns={value_column: 'total_fraudes'}, inplace=True)
                
                # Criar gráfico de pizza
                fig = create_pie_chart(
                    category_data,
                    'category',
                    'total_fraudes',
                    'Fraudes por Categoria de Produto',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Encontrar categoria mais problemática
                if not category_data.empty:
                    top_category = category_data.iloc[0]['category']
                    top_count = category_data.iloc[0]['total_fraudes']
                    total_count = category_data['total_fraudes'].sum()
                    
                    st.markdown(
                        create_insight_box(
                            f" A categoria '{top_category}' representa {(top_count/total_count*100):.1f}% de todas as fraudes. "
                            "Investigue os produtos desta categoria com prioridade.",
                            icon_type="info"
                        ),
                        unsafe_allow_html=True
                    )
            else:
                st.warning("Dados de produtos não possuem colunas 'category' ou valor para agregação.")
                
        # Se não tiver dados de produtos, usar dados de região
        elif df_fraud_region is not None and not df_fraud_region.empty:
            
            # Verificar qual coluna usar
            value_column = None
            if 'percentual_fraude' in df_fraud_region.columns:
                value_column = 'percentual_fraude'
            elif 'taxa_fraude' in df_fraud_region.columns:
                value_column = 'taxa_fraude'
            elif 'casos_fraude' in df_fraud_region.columns:
                value_column = 'casos_fraude'
            elif 'total_itens_faltantes' in df_fraud_region.columns:
                value_column = 'total_itens_faltantes'
            
            if 'region' in df_fraud_region.columns and value_column:
                # Usar dados de região
                fig = create_pie_chart(
                    df_fraud_region,
                    'region',
                    value_column,
                    f'Fraudes por Região ({value_column})',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Encontrar região mais problemática
                top_region = df_fraud_region.sort_values(value_column, ascending=False).iloc[0]['region']
                top_value = df_fraud_region.sort_values(value_column, ascending=False).iloc[0][value_column]
                
                st.markdown(
                    create_insight_box(
                        f" A região '{top_region}' apresenta o maior valor de {value_column}: {top_value:.2f}. "
                        "Recomenda-se revisar os procedimentos de entrega nesta área.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.warning("Dados de região não possuem colunas necessárias.")
                
        else:
            st.info("Dados de distribuição insuficientes. Verifique a conexão com a base de dados.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 3: Análise Detalhada de Fraudes por Motorista e Produto
    st.markdown("<h3> Análise Detalhada: Quais Produtos Cada Motorista Está Fraudando</h3>", unsafe_allow_html=True)
    
    # Tentar usar dados específicos de fraude ou produtos
    df_fraud_details = data.get('fraud_details') or data.get('driver_products') or df_missing_products
    
    # Criar análise detalhada
    heatmap_fig, driver_details_df, stacked_fig = create_driver_product_analysis(
        df_suspicious_drivers, 
        df_missing_products, 
        df_fraud_details
    )
    
    if heatmap_fig and driver_details_df is not None:
        
        # Criar abas para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs([
            " Mapa de Fraudes", 
            " Detalhes por Motorista", 
            " Gráfico Empilhado",
            " Análise Individual"
        ])
        
        with tab1:
            st.markdown("####  Mapa de Calor: Motorista vs Produto")
            st.plotly_chart(heatmap_fig, use_container_width=True)
            
            st.markdown("""
            ** Como interpretar este mapa:**
            - Cada célula mostra quantos itens de um produto específico um motorista fraudou
            - Cores mais vermelhas = mais fraudes
            - Números nas células = quantidade exata de fraudes
            - Passe o mouse sobre as células para ver detalhes
            """)
        
        with tab2:
            st.markdown("#### Tabela Detalhada por Motorista")
            
            # Filtros
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                min_frauds = st.number_input(
                    "Mínimo de fraudes totais",
                    min_value=0,
                    max_value=int(driver_details_df['Total de Fraudes'].max()),
                    value=0
                )
            
            with col_filter2:
                min_variety = st.number_input(
                    "Mínimo de produtos diferentes",
                    min_value=1,
                    max_value=int(driver_details_df['Variedade de Produtos'].max()),
                    value=1
                )
            
            # Filtrar dados
            filtered_details = driver_details_df[
                (driver_details_df['Total de Fraudes'] >= min_frauds) &
                (driver_details_df['Variedade de Produtos'] >= min_variety)
            ]
            
            if not filtered_details.empty:
                st.dataframe(filtered_details, use_container_width=True, height=400)
                
                # Download
                csv_details = filtered_details.to_csv(index=False)
                st.download_button(
                    label=" Baixar Detalhes (CSV)",
                    data=csv_details,
                    file_name=f"detalhes_fraudes_motoristas_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Insights automáticos
                st.markdown("---")
                st.markdown("#### Insights Automáticos")
                
                # Motorista com mais fraudes
                top_fraudster = filtered_details.iloc[0]
                st.markdown(f"""
                <div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0;'>
                    <strong>Motorista com maior índice de fraudes:</strong> {top_fraudster['Motorista']}<br>
                    <strong>Total de Fraudes:</strong> {top_fraudster['Total de Fraudes']}<br>
                    <strong>Produto Favorito:</strong> {top_fraudster['Produto Mais Fraudado']} ({top_fraudster['Qtd do Produto Principal']} unidades)<br>
                    <strong>Variedade:</strong> Frauda {top_fraudster['Variedade de Produtos']} tipos diferentes de produtos
                </div>
                """, unsafe_allow_html=True)
                
                # Motorista mais diversificado
                most_diverse = filtered_details.loc[filtered_details['Variedade de Produtos'].idxmax()]
                st.markdown(f"""
                <div style='background-color: #d1ecf1; padding: 10px; border-radius: 5px; margin: 10px 0;'>
                    <strong> Mais Diversificado:</strong> {most_diverse['Motorista']}<br>
                    <strong>Variedade:</strong> {most_diverse['Variedade de Produtos']} tipos de produtos diferentes<br>
                    <strong>Total de Fraudes:</strong> {most_diverse['Total de Fraudes']}<br>
                    <strong>Estratégia:</strong> Este motorista espalha as fraudes por muitos produtos diferentes
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.info("Nenhum motorista encontrado com os filtros aplicados.")
        
        with tab3:
            st.markdown("####  Distribuição de Fraudes por Motorista e Produto")
            
            if stacked_fig:
                st.plotly_chart(stacked_fig, use_container_width=True)
                
                st.markdown("""
                ** Como interpretar este gráfico:**
                - Cada barra representa um motorista
                - As cores mostram diferentes produtos
                - A altura total da barra = total de fraudes do motorista
                - Cada segmento colorido = quantidade fraudada daquele produto específico
                """)
            else:
                st.info("Dados insuficientes para criar o gráfico empilhado.")
        
        with tab4:
            st.markdown("#### Análise Individual de Motorista")
            
            # Seletor de motorista
            available_drivers = driver_details_df['Motorista'].tolist()
            selected_driver = st.selectbox(
                "Selecione um motorista para análise detalhada:",
                options=available_drivers,
                key="individual_driver_analysis"
            )
            
            if selected_driver:
                # Criar análise individual
                individual_fig, individual_data = create_individual_driver_report(df_fraud_details, selected_driver)
                
                if individual_fig and individual_data is not None:
                    
                    # Métricas do motorista
                    driver_info = driver_details_df[driver_details_df['Motorista'] == selected_driver].iloc[0]
                    
                    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
                    
                    with col_metric1:
                        st.metric("Total de Fraudes", driver_info['Total de Fraudes'])
                    with col_metric2:
                        st.metric("Produto Principal", driver_info['Produto Mais Fraudado'])
                    with col_metric3:
                        st.metric("Qtd do Principal", driver_info['Qtd do Produto Principal'])
                    with col_metric4:
                        st.metric("Variedade", f"{driver_info['Variedade de Produtos']} produtos")
                    
                    # Gráfico de pizza
                    col_chart, col_table = st.columns([2, 1])
                    
                    with col_chart:
                        st.plotly_chart(individual_fig, use_container_width=True)
                    
                    with col_table:
                        st.markdown("##### Produtos Fraudados")
                        st.dataframe(
                            individual_data.rename(columns={
                                individual_data.columns[0]: 'Produto',
                                individual_data.columns[1]: 'Quantidade'
                            }),
                            hide_index=True
                        )
                    
                    # Recomendações específicas
                    st.markdown("---")
                    st.markdown("#### Recomendações Específicas")
                    
                    total_frauds = driver_info['Total de Fraudes']
                    variety = driver_info['Variedade de Produtos']
                    main_product = driver_info['Produto Mais Fraudado']
                    main_qty = driver_info['Qtd do Produto Principal']
                    
                    if total_frauds >= 20:
                        st.error(f"🔴 **AÇÃO IMEDIATA**: {selected_driver} possui {total_frauds} fraudes confirmadas. Suspender e investigar imediatamente.")
                    elif total_frauds >= 10:
                        st.warning(f"🟠 **MONITORAMENTO**: {selected_driver} precisa de supervisão próxima em todas as entregas.")
                    
                    if variety >= 5:
                        st.warning(f" **PADRÃO DIVERSIFICADO**: Este motorista frauda {variety} tipos de produtos diferentes. Possível estratégia para evitar detecção.")
                    
                    concentration_rate = (main_qty / total_frauds) * 100
                    if concentration_rate >= 50:
                        st.info(f" **FOCO EM {main_product}**: {concentration_rate:.1f}% das fraudes são deste produto. Revisar procedimentos específicos para este item.")
                
                else:
                    st.error("Não foi possível gerar análise individual para este motorista.")
    
    else:
        st.warning("""
        **⚠️ Dados insuficientes para análise detalhada motorista vs produto.**
        
        Para esta funcionalidade funcionar, é necessário ter dados que relacionem:
        - Nome do motorista
        - Nome/ID do produto  
        - Quantidade fraudada
        
        **Colunas esperadas em uma das tabelas de dados:**
        - Motorista: `driver_name`, `motorista`, `nome_motorista`
        - Produto: `product_name`, `produto`, `item`, `nome_produto`
        - Quantidade: `fraud_count`, `relatos_fraude`, `itens_faltantes`, `quantidade_fraude`
        """)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 4: Lista Completa de Motoristas
    st.markdown("<h3> Lista Completa de Motoristas e Taxa de Fraude</h3>", unsafe_allow_html=True)
    
    if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
        
        # Verificar colunas disponíveis para determinar estrutura dos dados
        available_columns = df_suspicious_drivers.columns.tolist()
        
        # Identificar colunas de taxa de fraude
        fraud_rate_column = None
        driver_name_column = None
        
        # Mapear colunas possíveis para taxa de fraude
        fraud_columns = ['percentual_fraude', 'taxa_fraude', 'fraud_rate', 'fraude_percent']
        for col in fraud_columns:
            if col in available_columns:
                fraud_rate_column = col
                break
        
        # Mapear colunas possíveis para nome do motorista
        name_columns = ['driver_name', 'motorista', 'nome_motorista', 'driver', 'name']
        for col in name_columns:
            if col in available_columns:
                driver_name_column = col
                break
        
        if fraud_rate_column and driver_name_column:
            # Criar abas para diferentes visualizações
            tab1, tab2, tab3 = st.tabs([" Lista Ranqueada", " Gráfico de Barras", " Tabela Detalhada"])
            
            # Preparar dados ordenados
            drivers_sorted = df_suspicious_drivers.sort_values(fraud_rate_column, ascending=False).copy()
            
            with tab1:
                st.markdown("####  Ranking de Motoristas por Taxa de Fraude")
                
                # Filtros para a lista
                col_filter1, col_filter2 = st.columns(2)
                
                with col_filter1:
                    min_fraud_rate = st.slider(
                        "Taxa mínima de fraude (%)", 
                        min_value=0.0, 
                        max_value=float(drivers_sorted[fraud_rate_column].max()), 
                        value=0.0,
                        step=0.1
                    )
                
                with col_filter2:
                    show_top_n = st.selectbox(
                        "Mostrar top N motoristas",
                        options=[10, 20, 50, 100, "Todos"],
                        index=4
                    )
                
                # Filtrar dados
                filtered_drivers = drivers_sorted[drivers_sorted[fraud_rate_column] >= min_fraud_rate]
                
                if show_top_n != "Todos":
                    filtered_drivers = filtered_drivers.head(show_top_n)
                
                # Exibir lista ranqueada
                if not filtered_drivers.empty:
                    st.markdown(f"**Total de motoristas exibidos: {len(filtered_drivers)}**")
                    
                    for idx, (_, row) in enumerate(filtered_drivers.iterrows(), 1):
                        driver_name = row[driver_name_column]
                        fraud_rate = row[fraud_rate_column]
                        
                        # Definir cor baseada na taxa de fraude
                        if fraud_rate >= 10:
                            color = "🔴"
                            alert_level = "CRÍTICO"
                            border_color = "#dc3545"
                        elif fraud_rate >= 5:
                            color = "🟠"
                            alert_level = "ALTO"
                            border_color = "#fd7e14"
                        elif fraud_rate >= 2:
                            color = "🟡"
                            alert_level = "MÉDIO"
                            border_color = "#ffc107"
                        else:
                            color = "🟢"
                            alert_level = "BAIXO"
                            border_color = "#28a745"
                        
                        # Criar card para cada motorista
                        st.markdown(f"""
                        <div style='
                            background-color: #f8f9fa; 
                            padding: 10px; 
                            margin: 5px 0; 
                            border-left: 4px solid {border_color}; 
                            border-radius: 5px;
                        '>
                            <strong>#{idx} - {driver_name}</strong><br>
                            {color} Taxa de Fraude: <strong>{fraud_rate:.2f}%</strong> - Nível: <strong>{alert_level}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhum motorista encontrado com os filtros aplicados.")
            
            with tab2:
                st.markdown("####  Gráfico de Barras - Taxa de Fraude por Motorista")
                
                # Opção para escolher quantos motoristas mostrar no gráfico
                top_n_chart = st.selectbox(
                    "Número de motoristas no gráfico",
                    options=[10, 20, 30, 50],
                    index=1,
                    key="chart_top_n"
                )
                
                chart_data = drivers_sorted.head(top_n_chart)
                
                if not chart_data.empty:
                    # Criar gráfico de barras horizontal
                    fig = create_bar_chart(
                        chart_data,
                        driver_name_column,
                        fraud_rate_column,
                        f'Top {top_n_chart} Motoristas por Taxa de Fraude (%)',
                        orientation='h',
                        height=max(400, top_n_chart * 25)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Estatísticas do gráfico
                    avg_fraud = chart_data[fraud_rate_column].mean()
                    max_fraud = chart_data[fraud_rate_column].max()
                    min_fraud = chart_data[fraud_rate_column].min()
                    
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    
                    with col_stat1:
                        st.metric("Taxa Média", f"{avg_fraud:.2f}%")
                    with col_stat2:
                        st.metric("Taxa Máxima", f"{max_fraud:.2f}%")
                    with col_stat3:
                        st.metric("Taxa Mínima", f"{min_fraud:.2f}%")
            
            with tab3:
                st.markdown("#### Tabela Completa de Motoristas")
                
                # Preparar dados para tabela
                table_data = drivers_sorted.copy()
                
                # Adicionar coluna de ranking
                table_data['Ranking'] = range(1, len(table_data) + 1)
                
                # Adicionar coluna de classificação de risco
                def classify_risk(fraud_rate):
                    if fraud_rate >= 10:
                        return "🔴 CRÍTICO"
                    elif fraud_rate >= 5:
                        return "🟠 ALTO"
                    elif fraud_rate >= 2:
                        return "🟡 MÉDIO"
                    else:
                        return "🟢 BAIXO"
                
                table_data['Nível de Risco'] = table_data[fraud_rate_column].apply(classify_risk)
                
                # Reorganizar colunas para melhor visualização
                display_columns = ['Ranking', driver_name_column, fraud_rate_column, 'Nível de Risco']
                
                # Adicionar outras colunas relevantes se existirem
                other_relevant_columns = ['total_entregas', 'entregas_totais', 'pedidos_entregues', 'relatos_fraude', 'itens_faltantes']
                for col in other_relevant_columns:
                    if col in available_columns:
                        display_columns.append(col)
                
                # Filtrar apenas colunas que existem
                display_columns = [col for col in display_columns if col in table_data.columns]
                
                # Renomear colunas para melhor apresentação
                column_names = {
                    'Ranking': 'Posição',
                    driver_name_column: 'Nome do Motorista',
                    fraud_rate_column: 'Taxa de Fraude (%)',
                    'total_entregas': 'Total de Entregas',
                    'entregas_totais': 'Total de Entregas',
                    'pedidos_entregues': 'Pedidos Entregues',
                    'relatos_fraude': 'Relatos de Fraude',
                    'itens_faltantes': 'Itens Faltantes'
                }
                
                table_display = table_data[display_columns].rename(columns=column_names)
                
                # Configurar exibição da tabela
                st.dataframe(
                    table_display,
                    use_container_width=True,
                    height=400
                )
                
                # Opção para download
                csv = table_display.to_csv(index=False)
                st.download_button(
                    label=" Baixar Lista Completa (CSV)",
                    data=csv,
                    file_name=f"motoristas_fraude_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Resumo estatístico
                st.markdown("---")
                st.markdown("#### Resumo Estatístico")
                
                total_drivers = len(table_data)
                critical_drivers = len(table_data[table_data[fraud_rate_column] >= 10])
                high_risk_drivers = len(table_data[(table_data[fraud_rate_column] >= 5) & (table_data[fraud_rate_column] < 10)])
                medium_risk_drivers = len(table_data[(table_data[fraud_rate_column] >= 2) & (table_data[fraud_rate_column] < 5)])
                low_risk_drivers = len(table_data[table_data[fraud_rate_column] < 2])
                
                col_summary1, col_summary2, col_summary3, col_summary4, col_summary5 = st.columns(5)
                
                with col_summary1:
                    st.metric("Total de Motoristas", total_drivers)
                with col_summary2:
                    st.metric("🔴 Crítico (≥10%)", critical_drivers)
                with col_summary3:
                    st.metric("🟠 Alto (5-10%)", high_risk_drivers)
                with col_summary4:
                    st.metric("🟡 Médio (2-5%)", medium_risk_drivers)
                with col_summary5:
                    st.metric("🟢 Baixo (<2%)", low_risk_drivers)
        
        else:
            st.error("Dados de motoristas não possuem as colunas necessárias para análise.")
            st.write("**Colunas disponíveis:**", available_columns)
            st.write("**Colunas esperadas:** driver_name/motorista (nome) e percentual_fraude/taxa_fraude (taxa)")
    
    else:
        st.info("Nenhum dado de motorista disponível para análise.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 5: Top produtos não entregues
    st.markdown("<h3>📦 Produtos Mais Reportados como Não Entregues</h3>", unsafe_allow_html=True)
    
    if df_missing_products is not None and not df_missing_products.empty:
        
        # Verificar se as colunas necessárias existem
        if 'total_relatos' in df_missing_products.columns and 'product_name' in df_missing_products.columns:
            # Selecionar top 10 produtos por número de relatos
            top_products = df_missing_products.sort_values('total_relatos', ascending=False).head(10)
            
            # Criar gráfico de barras
            fig = create_bar_chart(
                top_products,
                'product_name',
                'total_relatos',
                'Top 10 Produtos por Relatos de Não Entrega',
                orientation='h',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif 'itens_faltantes' in df_missing_products.columns and 'product_name' in df_missing_products.columns:
            # Usar itens_faltantes como alternativa
            top_products = df_missing_products.sort_values('itens_faltantes', ascending=False).head(10)
            
            fig = create_bar_chart(
                top_products,
                'product_name',
                'itens_faltantes',
                'Top 10 Produtos por Itens Faltantes',
                orientation='h',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Dados de produtos não possuem as colunas necessárias.")
            st.write("**Colunas disponíveis:**", list(df_missing_products.columns))
    else:
        st.info("Nenhum produto com relatos de não entrega no período selecionado.")
    
    # Seção de insights e próximos passos
    st.markdown("---")
    st.markdown("### Próximos Passos Recomendados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ####  Ações Imediatas
        
        1. **Foque nos motoristas críticos** (taxa ≥10%)
        2. **Implemente verificações** nos produtos mais fraudados
        3. **Revise procedimentos** nas regiões problemáticas
        4. **Configure alertas** para casos anômalos
        """)
    
    with col2:
        st.markdown("""
        ####  Monitoramento Contínuo
        
        1. **Acompanhe tendências** diariamente
        2. **Atualize filtros** conforme novos padrões
        3. **Documente ações** tomadas
        4. **Meça eficácia** das medidas implementadas
        """)
    
    st.markdown("###  Insights da Análise Motorista vs Produto")
    
    if heatmap_fig and driver_details_df is not None:
        st.markdown("""
        ** Análise Avançada Disponível:**
        
        O novo sistema de relacionamento motorista vs produto permite identificar:
        - **Padrões de comportamento suspeito** específicos por motorista
        - **Produtos mais vulneráveis** em mãos de determinados entregadores
        - **Estratégias de fraude** (concentrada vs diversificada)
        - **Pontos críticos** para intervenção prioritária
        
        **Como aproveitar estes insights:**
        1. Use o **mapa de calor** para visualizar concentrações de fraude
        2. Analise a **tabela detalhada** para entender padrões individuais
        3. Monitore **motoristas diversificados** que podem estar evitando detecção
        4. Implemente **verificações específicas** por produto/motorista
        """)
    else:
        st.markdown("""
        **⚠️ Para Habilitar Análise Avançada:**
        
        Para ativar o sistema completo de análise motorista vs produto, certifique-se de que os dados contenham:
        
        1. **Tabela de relacionamento** com colunas:
           - `driver_name` ou `motorista` (nome do entregador)
           - `product_name` ou `produto` (nome/ID do produto)
           - `fraud_count` ou `relatos_fraude` (quantidade de fraudes)
        
        2. **Dados integrados** que permitam cruzar informações entre:
           - Motoristas e suas entregas
           - Produtos e suas ocorrências de fraude
           - Relatos de clientes por entregador e produto
        
        Com estes dados, o dashboard oferecerá insights muito mais precisos e acionáveis.
        """)
    

    
    # Footer com resumo
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #F8F9FA; padding: 20px; border-radius: 10px; border: 1px solid #E9ECEF;">
        <h4> Resumo do Panorama</h4>
        <p>Este panorama fornece uma <strong>visão executiva completa</strong> do status atual de fraudes em entregas do Walmart. 
        Os dados são atualizados em tempo real e incluem análises de motoristas, produtos, regiões e tendências temporais.</p>
        
        <p><strong> Objetivo:</strong> Detectar, analisar e prevenir fraudes através de insights baseados em dados.</p>
        <p><strong> Cobertura:</strong> Análise completa de padrões, correlações e anomalias em entregas.</p>
        <p><strong> Ação:</strong> Use os insights para tomar decisões informadas e implementar medidas preventivas.</p>
        
        <p style="margin-top: 15px;"><em>💡 Para análises mais específicas, navegue pelas outras seções da dashboard usando as abas superiores.</em></p>
    </div>
    """, unsafe_allow_html=True)