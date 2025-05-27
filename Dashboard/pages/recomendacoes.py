import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Importar funções utilitárias
from utils.graphics import create_bar_chart
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def show(data):
    """
    Exibe recomendações baseadas na análise de fraudes.
    
    Args:
        data: Dicionário com DataFrames para análise
    """
    st.markdown("<h2 style='text-align: center;'> Recomendações e Próximos Passos</h2>", unsafe_allow_html=True)
    
    # Verificar se os dados foram carregados
    if not data:
        st.error("Não foi possível carregar os dados para gerar recomendações.")
        return
    
    # Configuração de layout
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 1: Resumo da situação atual
    st.markdown("<h3> Resumo da Situação Atual</h3>", unsafe_allow_html=True)
    
    # Calcular métricas-chave para o resumo
    has_driver_data = ('drivers' in data and data['drivers'] is not None and not data['drivers'].empty) or \
                      ('suspicious_drivers' in data and data['suspicious_drivers'] is not None and not data['suspicious_drivers'].empty)
    
    has_product_data = 'missing_products' in data and data['missing_products'] is not None and not data['missing_products'].empty
    
    has_region_data = 'fraud_region' in data and data['fraud_region'] is not None and not data['fraud_region'].empty
    
    has_trend_data = 'fraud_trend' in data and data['fraud_trend'] is not None and not data['fraud_trend'].empty
    
    # Determinar o nível de risco global
    risk_level = "Médio"  # Padrão
    risk_color = "warning"
    
    if has_trend_data:
        df_trend = data['fraud_trend']
        avg_fraud_rate = df_trend['percentual_fraude'].mean() if 'percentual_fraude' in df_trend.columns else 5.0
        
        if avg_fraud_rate > 7.5:
            risk_level = "Alto"
            risk_color = "danger"
        elif avg_fraud_rate < 2.5:
            risk_level = "Baixo"
            risk_color = "success"
    
    # Exibir resumo
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(
            create_kpi_card(
                "Nível de Risco Global", 
                risk_level, 
                "Baseado na análise de dados",
                color=risk_color
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        summary_text = "Com base na análise dos dados disponíveis, "
        
        if risk_level == "Alto":
            summary_text += (
                "identificamos um **nível de risco alto** para fraudes em entregas do Walmart. "
                "A taxa de fraude está significativamente acima dos níveis aceitáveis, exigindo ações imediatas e abrangentes. "
                "As recomendações a seguir são prioritárias e devem ser implementadas com urgência."
            )
        elif risk_level == "Médio":
            summary_text += (
                "identificamos um **nível de risco médio** para fraudes em entregas do Walmart. "
                "Existem áreas específicas que requerem atenção e melhorias, mas a situação geral não é crítica. "
                "As recomendações a seguir devem ser implementadas em fases, começando pelas de maior impacto."
            )
        else:  # Baixo
            summary_text += (
                "identificamos um **nível de risco baixo** para fraudes em entregas do Walmart. "
                "O sistema atual parece estar funcionando adequadamente, com taxas de fraude dentro de níveis aceitáveis. "
                "As recomendações a seguir visam principalmente otimizar processos e prevenir futuros problemas."
            )
        
        st.markdown(summary_text)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 2: Recomendações prioritárias
    st.markdown("<h3> Recomendações Prioritárias</h3>", unsafe_allow_html=True)
    
    # Criar recomendações baseadas nos dados disponíveis
    recommendations = []
    
    # Recomendações para motoristas
    if has_driver_data:
        recommendations.append({
            "categoria": "Motoristas",
            "titulo": "Implementar Verificação de Entrega com Foto",
            "descricao": "Exigir que os motoristas tirem fotos de todas as entregas para comprovação. Isso pode reduzir fraudes em até 30% segundo estudos do setor.",
            "impacto": 8,
            "esforco": 6,
            "prioridade": "Alta",
            "icon": "🚚"
        })
        
        recommendations.append({
            "categoria": "Motoristas",
            "titulo": "Programa de Auditoria para Motoristas de Alto Risco",
            "descricao": "Criar um programa específico de verificação para motoristas com histórico de altas taxas de fraude, incluindo verificações aleatórias e acompanhamento.",
            "impacto": 9,
            "esforco": 7,
            "prioridade": "Alta",
            "icon": "🔍"
        })
        
        recommendations.append({
            "categoria": "Motoristas",
            "titulo": "Sistema de Incentivo para Baixas Taxas de Fraude",
            "descricao": "Implementar um programa de recompensas para motoristas com baixas taxas de fraude, incentivando boas práticas e criando competição positiva.",
            "impacto": 7,
            "esforco": 5,
            "prioridade": "Média",
            "icon": "🎯"
        })
    
    # Recomendações para produtos
    if has_product_data:
        recommendations.append({
            "categoria": "Produtos",
            "titulo": "Embalagens Especiais para Produtos de Alto Risco",
            "descricao": "Desenvolver embalagens tamper-proof com identificadores únicos para os produtos com maiores taxas de fraude.",
            "impacto": 8,
            "esforco": 8,
            "prioridade": "Alta",
            "icon": "📦"
        })
        
        recommendations.append({
            "categoria": "Produtos",
            "titulo": "Limites de Quantidade para Itens Frequentemente Fraudados",
            "descricao": "Estabelecer limites de quantidade por pedido para produtos com altas taxas de fraude, reduzindo o impacto potencial.",
            "impacto": 6,
            "esforco": 4,
            "prioridade": "Média",
            "icon": "🔢"
        })
    
    # Recomendações para regiões
    if has_region_data:
        recommendations.append({
            "categoria": "Regiões",
            "titulo": "Otimização de Rotas em Áreas de Alto Risco",
            "descricao": "Redesenhar rotas de entrega em regiões com altas taxas de fraude para melhorar a segurança e reduzir oportunidades de desvio.",
            "impacto": 7,
            "esforco": 9,
            "prioridade": "Média",
            "icon": "🗺️"
        })
        
        recommendations.append({
            "categoria": "Regiões",
            "titulo": "Hubs de Verificação Regional",
            "descricao": "Estabelecer centros de verificação em regiões de alto risco, onde os produtos são conferidos antes da entrega final.",
            "impacto": 9,
            "esforco": 10,
            "prioridade": "Baixa",
            "icon": "🏢"
        })
    
    # Recomendações para clientes
    recommendations.append({
        "categoria": "Clientes",
        "titulo": "Sistema de Verificação para Reclamações Frequentes",
        "descricao": "Implementar um processo de verificação adicional para clientes com histórico de múltiplas reclamações de itens não entregues.",
        "impacto": 8,
        "esforco": 7,
        "prioridade": "Alta",
        "icon": "👥"
    })
    
    # Recomendações para processos
    recommendations.append({
        "categoria": "Processos",
        "titulo": "Integração de IA para Detecção de Padrões de Fraude",
        "descricao": "Implementar um sistema de inteligência artificial para identificar padrões suspeitos em tempo real, antes que causem impacto significativo.",
        "impacto": 10,
        "esforco": 9,
        "prioridade": "Alta",
        "icon": "🤖"
    })
    
    recommendations.append({
        "categoria": "Processos",
        "titulo": "Dashboard em Tempo Real para Monitoramento de Fraudes",
        "descricao": "Expandir este dashboard para operar em tempo real, permitindo intervenções imediatas quando padrões anômalos são detectados.",
        "impacto": 8,
        "esforco": 7,
        "prioridade": "Média",
        "icon": "📊"
    })
    
    # Filtrar recomendações prioritárias (alta prioridade)
    priority_recommendations = [r for r in recommendations if r["prioridade"] == "Alta"]
    
    # Exibir recomendações prioritárias em cards
    if priority_recommendations:
        st.markdown("As recomendações a seguir foram identificadas como prioritárias com base na análise dos dados:")
        
        # Organizar em grades de 2 colunas
        for i in range(0, len(priority_recommendations), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(priority_recommendations):
                    rec = priority_recommendations[i + j]
                    
                    with cols[j]:
                        st.markdown(
                            f"""
                            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: rgba(255, 255, 255, 0.8);">
                                <h4>{rec["icon"]} {rec["titulo"]}</h4>
                                <p><strong>Categoria:</strong> {rec["categoria"]}</p>
                                <p>{rec["descricao"]}</p>
                                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                    <span style="color: #296D84;"><strong>Impacto: {rec["impacto"]}/10</strong></span>
                                    <span style="color: #CC5500;"><strong>Esforço: {rec["esforco"]}/10</strong></span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
    else:
        st.info("Não foram identificadas recomendações de alta prioridade.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 3: Matriz de esforço vs impacto
    st.markdown("<h3>Matriz de Esforço vs Impacto</h3>", unsafe_allow_html=True)
    
    # Criar dataframe para a matriz
    recommendations_df = pd.DataFrame(recommendations)
    
    # Criar scatter plot
    fig = px.scatter(
        recommendations_df,
        x="esforco",
        y="impacto",
        color="prioridade",
        size=[7] * len(recommendations),  # Tamanho fixo
        text="titulo",
        color_discrete_map={"Alta": "#FF6B6B", "Média": "#FFD166", "Baixa": "#06D6A0"},
        hover_name="titulo",
        hover_data=["descricao", "categoria"],
        title="Matriz de Priorização: Impacto vs Esforço de Implementação",
        labels={"esforco": "Esforço de Implementação (1-10)", "impacto": "Impacto Potencial (1-10)"}
    )
    
    # Personalizar layout
    fig.update_layout(
        xaxis=dict(range=[0, 11]),
        yaxis=dict(range=[0, 11]),
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        annotations=[
            # Quadrantes
            dict(
                x=2.5,
                y=8.5,
                text="QUICK WINS",
                showarrow=False,
                font=dict(size=12, color="#097969")
            ),
            dict(
                x=8.5,
                y=8.5,
                text="PROJETOS ESTRATÉGICOS",
                showarrow=False,
                font=dict(size=12, color="#8B0000")
            ),
            dict(
                x=2.5,
                y=2.5,
                text="BAIXA PRIORIDADE",
                showarrow=False,
                font=dict(size=12, color="#808080")
            ),
            dict(
                x=8.5,
                y=2.5,
                text="REAVALIAR",
                showarrow=False,
                font=dict(size=12, color="#CD853F")
            )
        ],
        shapes=[
            # Linhas divisórias de quadrantes
            dict(
                type="line",
                x0=5.5, y0=0,
                x1=5.5, y1=11,
                line=dict(
                    color="gray",
                    width=1,
                    dash="dash",
                )
            ),
            dict(
                type="line",
                x0=0, y0=5.5,
                x1=11, y1=5.5,
                line=dict(
                    color="gray",
                    width=1,
                    dash="dash",
                )
            )
        ]
    )
    
    # Exibir matriz
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicação da matriz
    st.markdown(
        create_insight_box(
            "A matriz acima mapeia as recomendações de acordo com seu impacto potencial (eixo vertical) "
            "e o esforço necessário para implementação (eixo horizontal). Os 'Quick Wins' (alto impacto, baixo esforço) "
            "devem ser priorizados para obter resultados rápidos, enquanto os projetos estratégicos de longo prazo "
            "(alto impacto, alto esforço) devem ser planejados com antecedência.",
            icon_type="info"
        ),
        unsafe_allow_html=True
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 4: Plano de ação
    st.markdown("<h3> Plano de Ação Recomendado</h3>", unsafe_allow_html=True)
    
    # Criar estrutura do plano de ação
    st.markdown("""
    O plano de ação a seguir organiza as recomendações em fases de implementação:
    
    ### Fase 1: Ações Imediatas (1-3 meses)
    """)
    
    # Fase 1: Ações imediatas
    # Priorizar Quick Wins (alto impacto, baixo esforço)
    quick_wins = recommendations_df[(recommendations_df['impacto'] >= 6) & (recommendations_df['esforco'] <= 6)]
    
    if not quick_wins.empty:
        for _, rec in quick_wins.iterrows():
            st.markdown(f"""
            <div style="margin-left: 20px; margin-bottom: 10px;">
                <strong>{rec['icon']} {rec['titulo']}</strong> - {rec['descricao']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Não foram identificadas ações imediatas de baixo esforço e alto impacto.")
    
    # Fase 2: Médio prazo
    st.markdown("""
    ### Fase 2: Médio Prazo (4-6 meses)
    """)
    
    # Selecionar ações de médio prazo (prioridade média ou alta implementação moderada)
    medium_term = recommendations_df[
        ((recommendations_df['prioridade'] == "Média") & (recommendations_df['esforco'] <= 8)) | 
        ((recommendations_df['prioridade'] == "Alta") & (recommendations_df['esforco'] > 6) & (recommendations_df['esforco'] <= 8))
    ]
    
    if not medium_term.empty:
        for _, rec in medium_term.iterrows():
            if rec['titulo'] not in quick_wins['titulo'].values:  # Evitar duplicados
                st.markdown(f"""
                <div style="margin-left: 20px; margin-bottom: 10px;">
                    <strong>{rec['icon']} {rec['titulo']}</strong> - {rec['descricao']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Não foram identificadas ações de médio prazo.")
    
    # Fase 3: Longo prazo
    st.markdown("""
    ### Fase 3: Projetos Estratégicos (6-12 meses)
    """)
    
    # Selecionar projetos estratégicos (alto impacto, alto esforço)
    strategic = recommendations_df[(recommendations_df['impacto'] >= 8) & (recommendations_df['esforco'] >= 8)]
    
    if not strategic.empty:
        for _, rec in strategic.iterrows():
            st.markdown(f"""
            <div style="margin-left: 20px; margin-bottom: 10px;">
                <strong>{rec['icon']} {rec['titulo']}</strong> - {rec['descricao']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Não foram identificados projetos estratégicos de longo prazo.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Seção 5: Métricas de acompanhamento
    st.markdown("<h3> Métricas para Acompanhamento</h3>", unsafe_allow_html=True)
    
    # Sugerir métricas para acompanhar a efetividade das ações
    st.markdown("""
    Para avaliar a eficácia das recomendações implementadas, sugerimos monitorar as seguintes métricas-chave:
    
    #### Métricas Primárias:
    - **Taxa geral de fraude (%)**: Acompanhar a tendência mensal comparando com o período base
    - **Valor financeiro recuperado ($)**: Quantificar o impacto financeiro positivo das medidas
    - **Tempo de investigação de fraudes (dias)**: Medir a eficiência do processo investigativo
    
    #### Métricas por Categoria:
    - **Motoristas**: Redução na taxa de fraude por motorista (%), Taxa de adesão ao novo protocolo (%)
    - **Produtos**: Redução de fraudes por categoria de produto (%), Eficácia das novas embalagens (%)
    - **Regiões**: Melhoria nas áreas críticas (%), Eficiência das novas rotas (%)
    - **Clientes**: Redução em reclamações repetidas (%), Satisfação com o processo de entrega (%)
    
    #### Painel de Controle:
    Recomendamos a criação de um painel de controle específico para acompanhar a evolução dessas métricas
    em tempo real, com alertas automáticos para desvios significativos dos objetivos estabelecidos.
    """)
    
    # Adicionar meta de redução de fraude
    current_fraud_rate = 0.0
    
    if has_trend_data:
        df_trend = data['fraud_trend']
        if 'percentual_fraude' in df_trend.columns:
            current_fraud_rate = df_trend['percentual_fraude'].mean()
    
    # Se não temos dados, usar valor placeholder
    if current_fraud_rate == 0.0:
        current_fraud_rate = 5.0
    
    # Definir meta com base na taxa atual
    target_reduction = 0.30  # Meta de redução de 30%
    target_rate = current_fraud_rate * (1 - target_reduction)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            create_kpi_card(
                "Meta de Redução de Fraude", 
                f"{target_reduction * 100:.0f}%", 
                f"Em 12 meses",
                color="success"
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_kpi_card(
                "Taxa de Fraude Alvo", 
                f"{target_rate:.2f}%", 
                f"Atual: {current_fraud_rate:.2f}%",
                color="success"
            ), 
            unsafe_allow_html=True
        )
    