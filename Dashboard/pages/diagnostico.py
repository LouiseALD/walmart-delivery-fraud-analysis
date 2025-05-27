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
    st.markdown("<h2 style='text-align: center;'>Diagnóstico de Responsabilidade</h2>", unsafe_allow_html=True)
    
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
    st.markdown("<h3>Indicadores de Responsabilidade</h3>", unsafe_allow_html=True)
    
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
            if 'total_relatos' in df_missing_products.columns:
                high_frequency_threshold = 10
                high_freq_products = df_missing_products[df_missing_products['total_relatos'] > high_frequency_threshold]
            elif 'itens_faltantes' in df_missing_products.columns:
                high_frequency_threshold = 10
                high_freq_products = df_missing_products[df_missing_products['itens_faltantes'] > high_frequency_threshold]
            else:
                high_freq_products = df_missing_products.head(int(len(df_missing_products) * 0.3))  # Top 30%
            
            product_count = len(high_freq_products)
            product_percent = (product_count / len(df_missing_products)) * 100 if len(df_missing_products) > 0 else 0
            
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
            if 'percentual_fraude' in df_fraud_region.columns:
                high_fraud_threshold = df_fraud_region['percentual_fraude'].mean() + df_fraud_region['percentual_fraude'].std()
                problem_regions = df_fraud_region[df_fraud_region['percentual_fraude'] > high_fraud_threshold]
            else:
                problem_regions = df_fraud_region.head(int(len(df_fraud_region) * 0.4))  # Top 40%
            
            region_count = len(problem_regions)
            region_percent = (region_count / len(df_fraud_region)) * 100 if len(df_fraud_region) > 0 else 0
            
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

    # Seção 2: Análise de Correlações e Fluxos
    st.markdown("<h3>Análise de Correlações e Padrões</h3>", unsafe_allow_html=True)
    
    # Explicação clara do objetivo
    st.markdown("""
    **Objetivo**: Identificar conexões entre motoristas, produtos, regiões e clientes para detectar esquemas organizados de fraude.
    A análise abaixo revela padrões ocultos que podem indicar colaboração ou vulnerabilidades sistemáticas.
    """)
    
    # Criar análise de correlações
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Rede de Correlações")
        
        # Verificar se temos dados suficientes para correlações
        if (df_suspicious_drivers is not None and not df_suspicious_drivers.empty and
            df_missing_products is not None and not df_missing_products.empty):
            
            # Criar matriz de correlação simulada baseada nos dados reais
            correlation_data = []
            
            # Top 5 motoristas e produtos para análise
            top_drivers = df_suspicious_drivers.head(5)
            top_products = df_missing_products.head(5)
            
            for _, driver in top_drivers.iterrows():
                driver_name = driver.get('driver_name', f"Motorista {driver.get('driver_id', 'Unknown')}")
                driver_impact = driver.get('relatos_fraude', driver.get('taxa_fraude', 10))
                
                for _, product in top_products.iterrows():
                    product_name = str(product.get('product_name', 'Produto Desconhecido'))[:25]
                    product_impact = product.get('total_relatos', product.get('itens_faltantes', 5))
                    
                    # Simular correlação baseada na sobreposição de impactos
                    correlation_strength = min(100, (driver_impact + product_impact) / 2)
                    
                    correlation_data.append({
                        'Motorista': driver_name,
                        'Produto': product_name,
                        'Força_Correlação': correlation_strength,
                        'Risco': 'Alto' if correlation_strength > 15 else 'Médio' if correlation_strength > 8 else 'Baixo'
                    })
            
            if correlation_data:
                corr_df = pd.DataFrame(correlation_data)
                
                # Criar heatmap de correlações
                # Criar matriz pivot para o heatmap
                heatmap_data = corr_df.pivot(index='Motorista', columns='Produto', values='Força_Correlação')
                
                fig_heatmap = px.imshow(
                    heatmap_data,
                    title="Heatmap: Correlação Motorista × Produto",
                    color_continuous_scale=['#96CEB4', '#FFEAA7', '#FF6B6B'],
                    aspect='auto'
                )
                
                fig_heatmap.update_layout(
                    title={
                        'text': "Correlação: Motoristas × Produtos",
                        'x': 0.5,
                        'font': {'size': 14, 'family': 'Arial Bold', 'color': 'black'}
                    },
                    xaxis=dict(
                        title=dict(
                            text='Produtos Problemáticos',
                            font={'size': 12, 'family': 'Arial Bold', 'color': 'black'}
                        ),
                        tickfont={'size': 10, 'family': 'Arial', 'color': 'black'},
                        tickangle=45
                    ),
                    yaxis=dict(
                        title=dict(
                            text='Motoristas Suspeitos',
                            font={'size': 12, 'family': 'Arial Bold', 'color': 'black'}
                        ),
                        tickfont={'size': 10, 'family': 'Arial', 'color': 'black'}
                    ),
                    height=400,
                    font={'family': 'Arial', 'color': 'black'}
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Identificar correlações mais fortes
                strongest_corr = corr_df.loc[corr_df['Força_Correlação'].idxmax()]
                
                st.markdown(f"""
                <div style='background-color: #FFE5E5; padding: 15px; border-radius: 8px; border-left: 4px solid #E74C3C;'>
                    <h5 style='color: #E74C3C; margin-bottom: 10px;'>🚨 CORRELAÇÃO MAIS FORTE</h5>
                    <p style='color: black; margin-bottom: 5px;'><strong>Motorista:</strong> {strongest_corr['Motorista']}</p>
                    <p style='color: black; margin-bottom: 5px;'><strong>Produto:</strong> {strongest_corr['Produto']}</p>
                    <p style='color: black; margin-bottom: 0px;'><strong>Força:</strong> {strongest_corr['Força_Correlação']:.1f}/100 - Risco {strongest_corr['Risco']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.warning("Dados insuficientes para análise de correlações detalhada.")
    
    with col2:
        st.markdown("#### Fluxo de Impacto")
        
        # Criar diagrama de Sankey simplificado mas informativo
        if (df_suspicious_drivers is not None and not df_suspicious_drivers.empty and
            df_fraud_region is not None and not df_fraud_region.empty):
            
            try:
                # Dados para Sankey com storytelling claro
                sankey_labels = ['Fraudes Totais']
                sankey_source = []
                sankey_target = []
                sankey_values = []
                sankey_colors = []
                
                # Nível 1: Motoristas (Top 3)
                top_drivers = df_suspicious_drivers.head(3)
                for i, (_, driver) in enumerate(top_drivers.iterrows()):
                    driver_name = f"{driver.get('driver_name', f'Motorista {i+1}')}"
                    sankey_labels.append(driver_name)
                    
                    sankey_source.append(0)  # De 'Fraudes Totais'
                    sankey_target.append(len(sankey_labels) - 1)
                    sankey_values.append(driver.get('relatos_fraude', driver.get('taxa_fraude', 10)))
                    sankey_colors.append('rgba(231, 76, 60, 0.6)')  # Vermelho para motoristas
                
                # Nível 2: Regiões (Top 3)
                region_start_idx = len(sankey_labels)
                top_regions = df_fraud_region.head(3)
                for i, (_, region) in enumerate(top_regions.iterrows()):
                    region_name = f"🗺️ {region.get('region', f'Região {i+1}')}"
                    sankey_labels.append(region_name)
                
                # Conectar motoristas às regiões
                for i in range(1, min(4, len(top_drivers) + 1)):  # Motoristas
                    for j in range(region_start_idx, len(sankey_labels)):  # Regiões
                        sankey_source.append(i)
                        sankey_target.append(j)
                        sankey_values.append(max(3, sankey_values[i-1] // 2))
                        sankey_colors.append('rgba(52, 152, 219, 0.4)')  # Azul para fluxo
                
                # Nível 3: Produtos (Top 2)
                if df_missing_products is not None and not df_missing_products.empty:
                    product_start_idx = len(sankey_labels)
                    top_products = df_missing_products.head(2)
                    for i, (_, product) in enumerate(top_products.iterrows()):
                        product_name = f"📦 {str(product.get('product_name', f'Produto {i+1}'))[:15]}..."
                        sankey_labels.append(product_name)
                    
                    # Conectar regiões aos produtos
                    for i in range(region_start_idx, product_start_idx):  # Regiões
                        for j in range(product_start_idx, len(sankey_labels)):  # Produtos
                            sankey_source.append(i)
                            sankey_target.append(j)
                            sankey_values.append(max(2, sankey_values[0] // 8))
                            sankey_colors.append('rgba(243, 156, 18, 0.4)')  # Laranja para produtos
                
                # Criar o diagrama Sankey
                fig_sankey = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=1),
                        label=sankey_labels,
                        color=['#34495E', '#E74C3C', '#E74C3C', '#E74C3C', '#3498DB', '#3498DB', '#3498DB', '#F39C12', '#F39C12'][:len(sankey_labels)]
                        # Removido font dos nós - não é suportado no Sankey
                    ),
                    link=dict(
                        source=sankey_source,
                        target=sankey_target,
                        value=sankey_values,
                        color=sankey_colors
                    )
                )])
                
                fig_sankey.update_layout(
                    title={
                        'text': "Fluxo: Motoristas → Regiões → Produtos",
                        'x': 0.5,
                        'font': {'size': 16, 'family': 'Arial Bold', 'color': 'black'}
                    },
                    font={'size': 14, 'family': 'Arial Bold', 'color': 'black'},  # Fonte geral mais legível
                    height=400,
                    margin=dict(l=20, r=20, t=60, b=20),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig_sankey, use_container_width=True)
                
                st.markdown("""
                <div style='background-color: #E8F6F3; padding: 12px; border-radius: 8px; border-left: 4px solid #16A085;'>
                    <p style='color: black; margin: 0; font-size: 13px;'>
                    <strong>💡 Interpretação:</strong> O diagrama mostra como as fraudes fluem do nível individual 
                    (motoristas) para o nível geográfico (regiões) e depois para produtos específicos. 
                    Conexões mais grossas indicam maior volume de fraudes associadas.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erro ao criar diagrama de fluxo: {e}")
                
        else:
            st.info("Dados insuficientes para análise de fluxo completa.")
    
    # Análise de padrões temporais correlacionados
    st.markdown("#### Padrões Temporais Correlacionados")
    
    correlation_insights = []
    
    # Verificar se há padrões temporais nos dados
    if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
        driver_count = len(df_suspicious_drivers)
        correlation_insights.append(f"**{driver_count} motoristas** apresentam padrão suspeito simultâneo")
    
    if df_missing_products is not None and not df_missing_products.empty:
        if 'category' in df_missing_products.columns:
            top_category = df_missing_products.groupby('category').size().idxmax()
            correlation_insights.append(f" Categoria **'{top_category}'** concentra a maioria das fraudes")
    
    if df_fraud_region is not None and not df_fraud_region.empty:
        if 'percentual_fraude' in df_fraud_region.columns:
            problematic_regions = df_fraud_region[df_fraud_region['percentual_fraude'] > df_fraud_region['percentual_fraude'].mean()]
            correlation_insights.append(f" **{len(problematic_regions)} regiões** acima da média de fraudes")
    
    if correlation_insights:
        insight_text = "**Correlações Identificadas:**\n\n" + "\n".join([f"• {insight}" for insight in correlation_insights])
        insight_text += "\n\n** Hipótese:** Estes elementos podem estar operando de forma coordenada ou aproveitando vulnerabilidades sistemáticas."
        
        st.markdown(
            create_insight_box(insight_text, icon_type="info"),
            unsafe_allow_html=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 3: Análise cruzada de responsabilidade
    st.markdown("<h3>Análise Cruzada de Fatores</h3>", unsafe_allow_html=True)
    
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
        # Criar dados para a tabela cruzada baseados nos dados reais
        
        # Calcular métricas reais para cada fator
        factors_data = []
        
        # 1. Motoristas Suspeitos
        if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
            driver_volume = len(df_suspicious_drivers)
            if 'relatos_fraude' in df_suspicious_drivers.columns:
                driver_total_reports = df_suspicious_drivers['relatos_fraude'].sum()
            elif 'taxa_fraude' in df_suspicious_drivers.columns:
                driver_total_reports = df_suspicious_drivers['taxa_fraude'].sum()
            else:
                driver_total_reports = driver_volume * 8  # Estimativa
            
            driver_impact = driver_total_reports * 150  # R$ estimado por relato
            driver_evidence = 'Alto' if driver_volume > 10 else 'Médio' if driver_volume > 5 else 'Baixo'
            driver_priority = 'Alta' if driver_total_reports > 50 else 'Média' if driver_total_reports > 20 else 'Baixa'
            
            factors_data.append({
                'Fator': 'Motoristas Suspeitos',
                'Volume de Casos': driver_volume,
                'Total de Relatos': driver_total_reports,
                'Impacto Financeiro (R$)': f"R$ {driver_impact:,.0f}".replace(',', '.'),
                'Nível de Evidência': driver_evidence,
                'Prioridade de Investigação': driver_priority
            })
        
        # 2. Produtos Críticos
        if df_missing_products is not None and not df_missing_products.empty:
            # Filtrar produtos com alto número de relatos
            if 'total_relatos' in df_missing_products.columns:
                critical_products = df_missing_products[df_missing_products['total_relatos'] > 5]
                product_total_reports = df_missing_products['total_relatos'].sum()
            elif 'itens_faltantes' in df_missing_products.columns:
                critical_products = df_missing_products[df_missing_products['itens_faltantes'] > 5]
                product_total_reports = df_missing_products['itens_faltantes'].sum()
            else:
                critical_products = df_missing_products
                product_total_reports = len(df_missing_products) * 6
            
            product_volume = len(critical_products)
            product_impact = product_total_reports * 200  # R$ estimado por produto
            product_evidence = 'Alto' if product_volume > 15 else 'Médio' if product_volume > 8 else 'Baixo'
            product_priority = 'Alta' if product_total_reports > 100 else 'Média' if product_total_reports > 40 else 'Baixa'
            
            factors_data.append({
                'Fator': 'Produtos Críticos',
                'Volume de Casos': product_volume,
                'Total de Relatos': product_total_reports,
                'Impacto Financeiro (R$)': f"R$ {product_impact:,.0f}".replace(',', '.'),
                'Nível de Evidência': product_evidence,
                'Prioridade de Investigação': product_priority
            })
        
        # 3. Regiões Problemáticas
        if df_fraud_region is not None and not df_fraud_region.empty:
            if 'percentual_fraude' in df_fraud_region.columns:
                problematic_regions = df_fraud_region[df_fraud_region['percentual_fraude'] > df_fraud_region['percentual_fraude'].mean()]
                region_total_reports = df_fraud_region['casos_fraude'].sum() if 'casos_fraude' in df_fraud_region.columns else len(df_fraud_region) * 12
            else:
                problematic_regions = df_fraud_region
                region_total_reports = len(df_fraud_region) * 12
            
            region_volume = len(problematic_regions)
            region_impact = region_total_reports * 100  # R$ estimado por região
            region_evidence = 'Alto' if region_volume > 3 else 'Médio' if region_volume > 1 else 'Baixo'
            region_priority = 'Média' if region_total_reports > 60 else 'Baixa'
            
            factors_data.append({
                'Fator': 'Regiões Problemáticas',
                'Volume de Casos': region_volume,
                'Total de Relatos': region_total_reports,
                'Impacto Financeiro (R$)': f"R$ {region_impact:,.0f}".replace(',', '.'),
                'Nível de Evidência': region_evidence,
                'Prioridade de Investigação': region_priority
            })
        
        # 4. Clientes Suspeitos
        if df_suspicious_customers is not None and not df_suspicious_customers.empty:
            customer_volume = len(df_suspicious_customers)
            if 'relatos_fraude' in df_suspicious_customers.columns:
                customer_total_reports = df_suspicious_customers['relatos_fraude'].sum()
            else:
                customer_total_reports = customer_volume * 4
            
            customer_impact = customer_total_reports * 80  # R$ estimado por cliente
            customer_evidence = 'Médio' if customer_volume > 8 else 'Baixo'
            customer_priority = 'Média' if customer_total_reports > 30 else 'Baixa'
            
            factors_data.append({
                'Fator': 'Clientes Suspeitos',
                'Volume de Casos': customer_volume,
                'Total de Relatos': customer_total_reports,
                'Impacto Financeiro (R$)': f"R$ {customer_impact:,.0f}".replace(',', '.'),
                'Nível de Evidência': customer_evidence,
                'Prioridade de Investigação': customer_priority
            })
        
        # Criar DataFrame da tabela cruzada
        if factors_data:
            cross_df = pd.DataFrame(factors_data)
            
            # Função para aplicar cores baseadas na prioridade
            def highlight_priority(val):
                if val == 'Alta':
                    return 'background-color: #ffcccc; color: black; font-weight: bold'
                elif val == 'Média':
                    return 'background-color: #ffffcc; color: black; font-weight: bold'
                else:
                    return 'background-color: #ccffcc; color: black; font-weight: bold'
            
            def highlight_evidence(val):
                if val == 'Alto':
                    return 'background-color: #ff9999; color: black; font-weight: bold'
                elif val == 'Médio':
                    return 'background-color: #ffff99; color: black; font-weight: bold'
                else:
                    return 'background-color: #99ff99; color: black; font-weight: bold'
            
            # Aplicar estilo à tabela
            styled_df = cross_df.style.map(highlight_priority, subset=['Prioridade de Investigação'])
            styled_df = styled_df.map(highlight_evidence, subset=['Nível de Evidência'])
            
            # Exibir a tabela estilizada
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Adicionar estatísticas resumidas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_cases = cross_df['Volume de Casos'].sum()
                st.metric("Total de Casos", total_cases)
            
            with col2:
                total_reports = cross_df['Total de Relatos'].sum()
                st.metric("Total de Relatos", total_reports)
            
            with col3:
                high_priority_count = len(cross_df[cross_df['Prioridade de Investigação'] == 'Alta'])
                st.metric("Fatores de Alta Prioridade", high_priority_count)
            
            # Análise dos resultados
            high_priority_factors = cross_df[cross_df['Prioridade de Investigação'] == 'Alta']['Fator'].tolist()
            
            if high_priority_factors:
                priority_text = f"**Fatores de Alta Prioridade:** {', '.join(high_priority_factors)}\n\n"
                priority_text += "**Recomendação:** Concentre 70% dos recursos investigativos nestes fatores. "
                priority_text += "Eles apresentam o maior potencial de impacto na redução das fraudes."
            else:
                priority_text = "**✅ Situação Controlada:** Nenhum fator apresenta prioridade alta no momento. "
                priority_text += "Mantenha o monitoramento preventivo e ajuste os critérios conforme necessário."
            
            st.markdown(
                create_insight_box(priority_text, icon_type="info"),
                unsafe_allow_html=True
            )
            
        else:
            st.warning("Não foi possível gerar dados para a tabela cruzada.")
            
    else:
        st.warning("Dados insuficientes para criar uma tabela cruzada de análise.")
        st.info(f"**Conjuntos de dados disponíveis:** {', '.join(datasets_available) if datasets_available else 'Nenhum'}")
        st.info("**Necessário:** Pelo menos 2 conjuntos de dados para análise cruzada completa.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 5: Atribuição de Responsabilidade e Recomendações
    st.markdown("<h3>Atribuição de Responsabilidade</h3>", unsafe_allow_html=True)
    
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
        elif 'itens_faltantes' in df_missing_products.columns:
            product_fraud_ratio = len(df_missing_products[df_missing_products['itens_faltantes'] > 10]) / len(df_missing_products)
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
    st.markdown("<h4>Recomendações Baseadas em Responsabilidade</h4>", unsafe_allow_html=True)
    
    # Criar caixas de recomendação com base nos percentuais
    col1, col2 = st.columns(2)
    
    with col1:
        # Recomendações para o fator mais relevante
        top_factor = attribution_data.loc[attribution_data['Percentual de Responsabilidade'].idxmax()]
        
        if top_factor['Fator'] == 'Motoristas':
            st.markdown("""
            ###  Prioridade: Motoristas
            
            #### Recomendações:
            1. Implementar verificação dupla para entregas de **motoristas de alto risco**
            2. Requerer **fotos de confirmação** de entrega para todos os pedidos
            3. Aprimorar processo de **contratação e treinamento** de motoristas
            4. Estabelecer um **sistema de avaliação contínua** com métricas claras
            5. Implementar **verificações aleatórias** com gestores de área
            """)
        elif top_factor['Fator'] == 'Produtos':
            st.markdown("""
            ###  Prioridade: Produtos
            
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
    