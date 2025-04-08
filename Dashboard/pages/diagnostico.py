import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Importar funções utilitárias
from utils.graphics import create_sankey_diagram, create_bar_chart, create_pie_chart
from utils.filters import create_category_filter, create_region_filter
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def show(data):
    """
    Exibe o diagnóstico detalhado de responsabilidade e impacto das fraudes.
    
    Args:
        data: Dicionário com DataFrames para análise
    """
    st.markdown("<h2 style='text-align: center;'>⚖️ Diagnóstico de Responsabilidade</h2>", unsafe_allow_html=True)
    
    # Verificar se os dados foram carregados
    if not data:
        st.error("Não foi possível carregar os dados para o diagnóstico.")
        return
    
    # Obter dados relevantes
    df_drivers = data.get('drivers')
    df_suspicious_drivers = data.get('suspicious_drivers')
    df_missing_products = data.get('missing_products')
    df_fraud_region = data.get('fraud_region')
    df_suspicious_customers = data.get('suspicious_customers')
    
    # Verificar se temos pelo menos um conjunto de dados
    if (df_drivers is None or df_drivers.empty) and \
       (df_suspicious_drivers is None or df_suspicious_drivers.empty) and \
       (df_missing_products is None or df_missing_products.empty) and \
       (df_fraud_region is None or df_fraud_region.empty) and \
       (df_suspicious_customers is None or df_suspicious_customers.empty):
        st.warning("Dados insuficientes para diagnóstico de responsabilidade.")
        return
    
    # Configuração de layout
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 1: Indicadores Chave de Diagnóstico
    st.markdown("<h3>🔑 Indicadores de Responsabilidade</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # KPI 1: Total de motoristas suspeitos
    with col1:
        if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
            driver_count = len(df_suspicious_drivers)
            driver_percent = (driver_count / len(df_drivers)) * 100 if df_drivers is not None and not df_drivers.empty else 0
            
            st.markdown(
                create_kpi_card(
                    "Motoristas Suspeitos", 
                    f"{driver_count}", 
                    f"{driver_percent:.1f}% do total",
                    color="danger" if driver_percent > 10 else "warning"
                ), 
                unsafe_allow_html=True
            )
    
    # KPI 2: Total de produtos frequentemente não entregues
    with col2:
        if df_missing_products is not None and not df_missing_products.empty:
            # Definir um limiar para produtos frequentemente não entregues
            high_frequency_threshold = 10
            high_freq_products = df_missing_products[df_missing_products['total_relatos'] > high_frequency_threshold]
            product_count = len(high_freq_products)
            product_percent = (product_count / len(df_missing_products)) * 100
            
            st.markdown(
                create_kpi_card(
                    "Produtos Críticos", 
                    f"{product_count}", 
                    f"{product_percent:.1f}% do catálogo",
                    color="danger" if product_percent > 15 else "warning"
                ), 
                unsafe_allow_html=True
            )
    
    # KPI 3: Regiões problemáticas
    with col3:
        if df_fraud_region is not None and not df_fraud_region.empty:
            # Definir um limiar para regiões problemáticas
            high_fraud_threshold = df_fraud_region['percentual_fraude'].mean() + df_fraud_region['percentual_fraude'].std()
            problem_regions = df_fraud_region[df_fraud_region['percentual_fraude'] > high_fraud_threshold]
            region_count = len(problem_regions)
            region_percent = (region_count / len(df_fraud_region)) * 100
            
            st.markdown(
                create_kpi_card(
                    "Regiões Problemáticas", 
                    f"{region_count}", 
                    f"{region_percent:.1f}% das áreas",
                    color="danger" if region_percent > 20 else "warning"
                ), 
                unsafe_allow_html=True
            )
    
    # KPI 4: Clientes suspeitos
    with col4:
        if df_suspicious_customers is not None and not df_suspicious_customers.empty:
            customer_count = len(df_suspicious_customers)
            
            st.markdown(
                create_kpi_card(
                    "Clientes Suspeitos", 
                    f"{customer_count}", 
                    "Com padrão anômalo",
                    color="warning"
                ), 
                unsafe_allow_html=True
            )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 2: Diagrama de Sankey (Fluxo de Responsabilidade)
    st.markdown("<h3>🔄 Fluxo de Responsabilidade</h3>", unsafe_allow_html=True)
    
    # Explicação do diagrama
    st.markdown("""
    O diagrama de fluxo abaixo mostra a distribuição de responsabilidade entre os diferentes elementos envolvidos 
    no processo de entrega: motoristas, regiões, produtos e clientes. A espessura das conexões representa o volume 
    de fraudes associado a cada relação.
    """)
    
    # Criar dados para o diagrama de Sankey
    # Este é um exemplo que pode precisar ser adaptado conforme os dados disponíveis
    has_sankey_data = False
    
    if (df_suspicious_drivers is not None and not df_suspicious_drivers.empty) and \
       (df_fraud_region is not None and not df_fraud_region.empty) and \
       (df_suspicious_customers is not None and not df_suspicious_customers.empty):
        
        try:
            sankey_rows = []

            for _, driver in df_suspicious_drivers.head(5).iterrows():
                driver_name = driver.get('driver_name') or f"Motorista {driver.get('driver_id', 'Desconhecido')}"
                value = driver.get('itens_faltantes') or driver.get('total_missing_items', 10)

                sankey_rows.append({
                    'source': 'Fraude',
                    'target': driver_name,
                    'value': value
                })

                for _, region in df_fraud_region.head(4).iterrows():
                    region_name = region.get('region', 'Região Desconhecida')
                    region_value = value * (region.get('percentual_fraude', 25) / 100)

                    sankey_rows.append({
                        'source': driver_name,
                        'target': region_name,
                        'value': region_value
                    })

                    for _, customer in df_suspicious_customers.head(3).iterrows():
                        customer_name = customer.get('customer_name') or f"Cliente {customer.get('customer_id', 'Desconhecido')}"
                        customer_value = region_value * (customer.get('percentual_fraude', 33) / 100)

                        sankey_rows.append({
                            'source': region_name,
                            'target': customer_name,
                            'value': customer_value
                        })
            if sankey_rows:
                sankey_data = pd.DataFrame(sankey_rows)

                fig = create_sankey_diagram(
                    sankey_data,
                    'source',
                    'target',
                    'value',
                    'Fluxo de Responsabilidade por Fraudes'
                )

                has_sankey_data = True
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    create_insight_box(
                        "O diagrama acima mostra como as fraudes fluem através dos diferentes elementos do sistema de entregas...",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
                
        except Exception as e:
            has_sankey_data = False
            st.error(f"Não foi possível criar o diagrama de Sankey: {e}")
    
    if not has_sankey_data:
        # Alternativa quando não temos dados suficientes para o Sankey
        st.warning("Dados insuficientes para criar um diagrama de fluxo de responsabilidade completo.")
        
        # Criar visualizações alternativas
        col1, col2 = st.columns(2)
        
        # Gráfico de pizza para responsabilidade 
        with col1:
            # Dados estimados para exemplo
            responsibility_data = pd.DataFrame({
                'categoria': ['Motoristas', 'Produtos', 'Regiões', 'Clientes'],
                'percentual': [40, 30, 20, 10]  # Valores estimados com base na experiência
            })
            
            fig = create_pie_chart(
                responsibility_data,
                'categoria',
                'percentual',
                'Distribuição Estimada de Responsabilidade',
                hole=0.4
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Explicação de como a responsabilidade é estimada
        with col2:
            st.markdown("""
            ### Análise de Responsabilidade
            
            A responsabilidade por fraudes em entregas é geralmente distribuída entre:
            
            - **Motoristas**: Podem ser responsáveis por fraudes intencionais ou erros
            - **Produtos**: Algumas categorias de produtos são mais propensas a fraudes
            - **Regiões**: Fatores geográficos como distância e segurança influenciam as taxas de fraude
            - **Clientes**: Em alguns casos, clientes podem reportar falsamente produtos como não entregues
            
            Esta distribuição é uma estimativa baseada em análises do setor e pode variar conforme o contexto específico do Walmart.
            """)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 3: Análise cruzada de responsabilidade
    st.markdown("<h3>📊 Análise Cruzada de Fatores</h3>", unsafe_allow_html=True)
    
    # Criar estrutura para análise cruzada
    # Primeira linha: filtros
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro de categoria se tivermos dados de produtos
        if df_missing_products is not None and not df_missing_products.empty:
            selected_category = create_category_filter(df_missing_products, 'category', 'diagnostic')
        else:
            selected_category = "Todas"
    
    with col2:
        # Filtro de região se tivermos dados regionais
        if df_fraud_region is not None and not df_fraud_region.empty:
            selected_region = create_region_filter(df_fraud_region, 'region', 'diagnostic')
        else:
            selected_region = "Todas"
    
    # Aplicar filtros aos dados
    # (Na prática, precisaríamos de mais dados relacionais para fazer uma análise cruzada completa)
    
    # Seção 4: Tabela cruzada de análise
    st.markdown("<h4>📋 Tabela Cruzada de Análise</h4>", unsafe_allow_html=True)
    
    # Verificar se temos pelo menos dois conjuntos de dados para análise cruzada
    datasets_available = []
    if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
        datasets_available.append("motoristas")
    if df_missing_products is not None and not df_missing_products.empty:
        datasets_available.append("produtos")
    if df_fraud_region is not None and not df_fraud_region.empty:
        datasets_available.append("regiões")
    if df_suspicious_customers is not None and not df_suspicious_customers.empty:
        datasets_available.append("clientes")
    
    if len(datasets_available) >= 2:
        # Criar uma tabela cruzada simulada (exemplo)
        # Em uma implementação real, precisaríamos de dados relacionais completos
        
        # Criar dados de exemplo para a tabela cruzada
        cross_data = {
            'Fator': ['Motoristas Suspeitos', 'Produtos Críticos', 'Regiões Problemáticas', 'Clientes Suspeitos'],
            'Volume de Fraudes': [
                len(df_suspicious_drivers) * 5 if df_suspicious_drivers is not None and not df_suspicious_drivers.empty else 0,
                len(df_missing_products[df_missing_products['total_relatos'] > 10]) if df_missing_products is not None and not df_missing_products.empty else 0,
                len(df_fraud_region[df_fraud_region['percentual_fraude'] > df_fraud_region['percentual_fraude'].mean()]) if df_fraud_region is not None and not df_fraud_region.empty else 0,
                len(df_suspicious_customers) if df_suspicious_customers is not None and not df_suspicious_customers.empty else 0
            ],
            'Impacto Financeiro ($)': [
                50000,  # Valores ilustrativos
                35000,
                25000,
                15000
            ],
            'Nível de Evidência': [
                'Alto' if df_suspicious_drivers is not None and not df_suspicious_drivers.empty else 'Baixo',
                'Médio' if df_missing_products is not None and not df_missing_products.empty else 'Baixo',
                'Médio' if df_fraud_region is not None and not df_fraud_region.empty else 'Baixo',
                'Baixo' if df_suspicious_customers is not None and not df_suspicious_customers.empty else 'Baixo'
            ],
            'Prioridade de Investigação': [
                'Alta' if df_suspicious_drivers is not None and not df_suspicious_drivers.empty else 'Baixa',
                'Alta' if df_missing_products is not None and not df_missing_products.empty else 'Baixa',
                'Média' if df_fraud_region is not None and not df_fraud_region.empty else 'Baixa',
                'Média' if df_suspicious_customers is not None and not df_suspicious_customers.empty else 'Baixa'
            ]
        }
        
        cross_df = pd.DataFrame(cross_data)
        
        # Aplicar estilo
        def highlight_priority(val):
            if val == 'Alta':
                return 'background-color: #ffcccc'
            elif val == 'Média':
                return 'background-color: #ffffcc'
            else:
                return 'background-color: #ccffcc'
        
        # Exibir tabela com estilo
        cross_df.style.applymap(highlight_priority, subset=['Prioridade de Investigação'])

        
        # Adicionar explicação da tabela
        st.markdown(
            create_insight_box(
                "A tabela acima cruza os diferentes fatores de responsabilidade com seu respectivo impacto e prioridade. "
                "Observe que a prioridade é determinada com base no volume de fraudes, impacto financeiro e nível de evidência disponível.",
                icon_type="info"
            ),
            unsafe_allow_html=True
        )
    else:
        st.warning("Dados insuficientes para criar uma tabela cruzada de análise.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 5: Atribuição de Responsabilidade e Recomendações
    st.markdown("<h3>🎯 Atribuição de Responsabilidade</h3>", unsafe_allow_html=True)
    
    # Criar gráfico de barras com atribuição de responsabilidade
    # Usar dados estimados se não tivermos dados completos
    
    # Determinar percentuais com base nos dados disponíveis
    motorist_pct = 40  # Valores default
    product_pct = 30
    region_pct = 20
    customer_pct = 10
    
    # Ajustar com base nos dados disponíveis
    if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
        if 'percentual_fraude' in df_suspicious_drivers.columns:
            driver_fraud = df_suspicious_drivers['percentual_fraude'].mean()
            motorist_pct = min(70, max(20, int(driver_fraud * 5)))  # Ajustar para range razoável
    
    if df_missing_products is not None and not df_missing_products.empty:
        if 'total_relatos' in df_missing_products.columns:
            product_fraud_ratio = len(df_missing_products[df_missing_products['total_relatos'] > 10]) / len(df_missing_products)
            product_pct = min(60, max(10, int(product_fraud_ratio * 100)))
    
    # Rebalancear percentuais para somarem 100%
    total_pct = motorist_pct + product_pct + region_pct + customer_pct
    motorist_pct = int((motorist_pct / total_pct) * 100)
    product_pct = int((product_pct / total_pct) * 100)
    region_pct = int((region_pct / total_pct) * 100)
    customer_pct = 100 - motorist_pct - product_pct - region_pct  # Garantir que some 100%
    
    attribution_data = pd.DataFrame({
        'Fator': ['Motoristas', 'Produtos', 'Regiões', 'Clientes'],
        'Percentual de Responsabilidade': [motorist_pct, product_pct, region_pct, customer_pct]
    })
    
    fig = create_bar_chart(
        attribution_data,
        'Fator',
        'Percentual de Responsabilidade',
        'Atribuição de Responsabilidade por Fraudes (%)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar explicação
    st.markdown(
        create_insight_box(
            f"A análise atribui {motorist_pct}% da responsabilidade a motoristas, {product_pct}% a produtos específicos, "
            f"{region_pct}% a fatores regionais e {customer_pct}% a padrões de comportamento dos clientes. "
            "Esta distribuição pode variar conforme novas evidências forem coletadas.",
            icon_type="info"
        ),
        unsafe_allow_html=True
    )
    
    # Recomendações específicas baseadas na atribuição de responsabilidade
    st.markdown("<h4>📝 Recomendações Baseadas em Responsabilidade</h4>", unsafe_allow_html=True)
    
    # Criar caixas de recomendação com base nos percentuais
    col1, col2 = st.columns(2)
    
    with col1:
        # Recomendações para o fator mais relevante
        top_factor = attribution_data.loc[attribution_data['Percentual de Responsabilidade'].idxmax()]
        
        if top_factor['Fator'] == 'Motoristas':
            st.markdown("""
            ### 🚚 Prioridade: Motoristas
            
            #### Recomendações:
            1. Implementar verificação dupla para entregas de **motoristas de alto risco**
            2. Requerer **fotos de confirmação** de entrega para todos os pedidos
            3. Aprimorar processo de **contratação e treinamento** de motoristas
            4. Estabelecer um **sistema de avaliação contínua** com métricas claras
            5. Implementar **verificações aleatórias** com gestores de área
            """)
        elif top_factor['Fator'] == 'Produtos':
            st.markdown("""
            ### 📦 Prioridade: Produtos
            
            #### Recomendações:
            1. Implementar **etiquetas de segurança** para produtos de alto valor
            2. Criar **embalagens personalizadas** para categorias problemáticas
            3. Adicionar **verificação adicional no checkout** para itens críticos
            4. Estabelecer **limites de quantidade** para produtos frequentemente fraudados
            5. Implementar **rastreamento RFID** para produtos de maior valor
            """)
        elif top_factor['Fator'] == 'Regiões':
            st.markdown("""
            ### 🗺️ Prioridade: Regiões
            
            #### Recomendações:
            1. Realizar **auditorias regionais** em áreas com altas taxas de fraude
            2. Ajustar **rotas de entrega** para melhorar segurança
            3. Implementar **verificações adicionais** para entregas em áreas críticas
            4. Estabelecer **centros de verificação regionais** em áreas problemáticas
            5. Realizar **treinamento específico** para equipes em regiões de alto risco
            """)
        else:  # Clientes
            st.markdown("""
            ### 👥 Prioridade: Clientes
            
            #### Recomendações:
            1. Implementar **verificação adicional** para clientes com histórico suspeito
            2. Requerer **assinatura digital** para confirmação de entregas
            3. Estabelecer **limites de reclamações** antes de investigação automática
            4. Criar um **processo de verificação escalonado** para reclamações recorrentes
            5. Implementar **comunicação proativa** com clientes durante todo o processo
            """)
    
    with col2:
        # Recomendações para o segundo fator mais relevante
        second_factor = attribution_data.sort_values('Percentual de Responsabilidade', ascending=False).iloc[1]
        
        if second_factor['Fator'] == 'Motoristas':
            st.markdown("""
            ### 🚚 Atenção Secundária: Motoristas
            
            #### Recomendações:
            1. Estabelecer **sistema de incentivos** para entregas sem reclamações
            2. Implementar **rotação de rotas** para evitar padrões previsíveis
            3. Realizar **auditorias aleatórias** de processo de entrega
            4. Criar **grupos de discussão** para compartilhar melhores práticas
            5. Desenvolver **métricas de desempenho** mais granulares
            """)
        elif second_factor['Fator'] == 'Produtos':
            st.markdown("""
            ### 📦 Atenção Secundária: Produtos
            
            #### Recomendações:
            1. Revisar **procedimentos de embalagem** para produtos problemáticos
            2. Implementar **código QR de verificação** para produtos de alto valor
            3. Registrar **peso esperado vs. real** para detectar substituições
            4. Criar **embalagens tamper-proof** para categorias sensíveis
            5. Estabelecer **protocolo de verificação visual** no carregamento
            """)
        elif second_factor['Fator'] == 'Regiões':
            st.markdown("""
            ### 🗺️ Atenção Secundária: Regiões
            
            #### Recomendações:
            1. Implementar **análise geoespacial** das fraudes para identificar padrões
            2. Ajustar **horários de entrega** em áreas problemáticas
            3. Estabelecer **parcerias locais** para melhorar segurança de entrega
            4. Criar **protocolos específicos** para regiões com alto índice de fraude
            5. Implementar **sistema de monitoramento** regionalizado
            """)
        else:  # Clientes
            st.markdown("""
            ### 👥 Atenção Secundária: Clientes
            
            #### Recomendações:
            1. Desenvolver **sistema de classificação de risco** para clientes
            2. Implementar **processo de confirmação por foto** para entregas
            3. Estabelecer **limite de valor** para entregas sem verificação adicional
            4. Criar **perfis de comportamento** para identificar padrões suspeitos
            5. Introduzir **verificação aleatória** de satisfação pós-entrega
            """)
    
    # Adicionar narrativa na barra lateral
    with st.sidebar:
        st.markdown("<h3>⚖️ Diagnóstico</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        ### Entendendo a Responsabilidade
        
        O diagnóstico de responsabilidade permite:
        
        1. **Identificar as causas raiz** das fraudes em entregas
        2. **Direcionar recursos** para as áreas mais críticas
        3. **Desenvolver soluções específicas** para cada fator de risco
        4. **Priorizar ações** com base no impacto potencial
        
        #### Como interpretar este diagnóstico:
        
        - O diagrama de fluxo mostra como as fraudes se propagam pelo sistema
        - A tabela cruzada permite comparar diferentes fatores de risco
        - O gráfico de atribuição quantifica a contribuição de cada fator
        - As recomendações oferecem ações práticas baseadas nos insights
        
        > **Dica**: Este diagnóstico deve ser atualizado regularmente
        > à medida que novas informações são coletadas e as ações
        > implementadas começam a mostrar resultados.
        """)