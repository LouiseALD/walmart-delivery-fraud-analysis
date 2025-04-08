import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Importar funções utilitárias
from utils.loaders import detect_anomalies
from utils.graphics import create_correlation_matrix, create_scatter_plot, create_bar_chart
from utils.filters import cluster_data, filter_suspicious_entries
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def show(data):
    """
    Exibe padrões ocultos e anomalias nos dados de fraude.
    
    Args:
        data: Dicionário com DataFrames para análise
    """
    st.markdown("<h2 style='text-align: center;'>🔍 Padrões Ocultos e Anomalias</h2>", unsafe_allow_html=True)
    
    # Verificar se os dados foram carregados
    if not data:
        st.error("Não foi possível carregar os dados para análise de padrões.")
        return
    
    # Obter dados relevantes
    df_drivers = data.get('drivers')
    df_suspicious_drivers = data.get('suspicious_drivers')
    df_missing_products = data.get('missing_products')
    df_fraud_trend = data.get('fraud_trend')
    df_suspicious_customers = data.get('suspicious_customers')
    
    # Verificar se temos pelo menos um conjunto de dados
    if (df_drivers is None or df_drivers.empty) and \
       (df_suspicious_drivers is None or df_suspicious_drivers.empty) and \
       (df_missing_products is None or df_missing_products.empty) and \
       (df_fraud_trend is None or df_fraud_trend.empty) and \
       (df_suspicious_customers is None or df_suspicious_customers.empty):
        st.warning("Dados insuficientes para análise de padrões ocultos.")
        return
    
    # Configuração de layout
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Criar abas para separar os tipos de análise
    tab1, tab2, tab3 = st.tabs(["🔬 Correlações", "🌟 Clusterização", "📋 Padrões Sequenciais"])
    
    # Aba 1: Correlações
    with tab1:
        st.markdown("<h3>🔬 Análise de Correlações</h3>", unsafe_allow_html=True)
        
        # Explicação
        st.markdown("""
        A análise de correlação identifica relações estatísticas entre diferentes variáveis, 
        revelando padrões que podem não ser óbvios à primeira vista. Valores próximos a 1 indicam 
        forte correlação positiva, valores próximos a -1 indicam forte correlação negativa, e 
        valores próximos a 0 indicam ausência de correlação.
        """)
        
        # Selecionar dataset para análise de correlação
        st.markdown("<h4>Selecione o conjunto de dados para análise:</h4>", unsafe_allow_html=True)
        
        datasets = []
        if df_drivers is not None and not df_drivers.empty:
            datasets.append("Entregadores (Todos)")
        if df_suspicious_drivers is not None and not df_suspicious_drivers.empty:
            datasets.append("Entregadores (Suspeitos)")
        if df_missing_products is not None and not df_missing_products.empty:
            datasets.append("Produtos")
        if df_fraud_trend is not None and not df_fraud_trend.empty:
            datasets.append("Tendências Temporais")
        if df_suspicious_customers is not None and not df_suspicious_customers.empty:
            datasets.append("Clientes Suspeitos")
        
        if not datasets:
            st.warning("Nenhum conjunto de dados disponível para análise de correlação.")
        else:
            selected_dataset = st.selectbox("Conjunto de Dados", datasets)
            
            # Preparar dataframe conforme seleção
            if selected_dataset == "Entregadores (Todos)" and df_drivers is not None:
                df_for_corr = df_drivers.select_dtypes(include=['int64', 'float64'])
            elif selected_dataset == "Entregadores (Suspeitos)" and df_suspicious_drivers is not None:
                df_for_corr = df_suspicious_drivers.select_dtypes(include=['int64', 'float64'])
            elif selected_dataset == "Produtos" and df_missing_products is not None:
                df_for_corr = df_missing_products.select_dtypes(include=['int64', 'float64'])
            elif selected_dataset == "Tendências Temporais" and df_fraud_trend is not None:
                # Excluir a coluna de data para correlação
                if 'date' in df_fraud_trend.columns:
                    df_for_corr = df_fraud_trend.drop('date', axis=1).select_dtypes(include=['int64', 'float64'])
                else:
                    df_for_corr = df_fraud_trend.select_dtypes(include=['int64', 'float64'])
            elif selected_dataset == "Clientes Suspeitos" and df_suspicious_customers is not None:
                df_for_corr = df_suspicious_customers.select_dtypes(include=['int64', 'float64'])
            else:
                df_for_corr = None
            
            if df_for_corr is None or df_for_corr.empty or df_for_corr.shape[1] < 2:
                st.warning(f"O conjunto de dados '{selected_dataset}' não possui variáveis numéricas suficientes para correlação.")
            else:
                # Criar matriz de correlação
                corr_fig = create_correlation_matrix(
                    df_for_corr,
                    title=f"Matriz de Correlação - {selected_dataset}"
                )
                
                st.plotly_chart(corr_fig, use_container_width=True)
                
                # Encontrar e exibir correlações mais fortes
                corr_matrix = df_for_corr.corr()
                
                # Remover auto-correlações (diagonal)
                np.fill_diagonal(corr_matrix.values, 0)
                
                # Encontrar top correlações positivas
                top_pos_corr = corr_matrix.stack().sort_values(ascending=False).head(5)
                top_neg_corr = corr_matrix.stack().sort_values(ascending=True).head(5)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h4>🔝 Top 5 Correlações Positivas</h4>", unsafe_allow_html=True)
                    
                    if not top_pos_corr.empty:
                        for (var1, var2), corr_value in top_pos_corr.items():
                            if var1 != var2:  # Evitar auto-correlações (deve ser redundante aqui)
                                st.markdown(
                                    f"**{var1.replace('_', ' ').title()} & {var2.replace('_', ' ').title()}:** {corr_value:.3f}"
                                )
                    else:
                        st.info("Nenhuma correlação positiva significativa encontrada.")
                
                with col2:
                    st.markdown("<h4>🔽 Top 5 Correlações Negativas</h4>", unsafe_allow_html=True)
                    
                    if not top_neg_corr.empty:
                        for (var1, var2), corr_value in top_neg_corr.items():
                            if var1 != var2:  # Evitar auto-correlações (deve ser redundante aqui)
                                st.markdown(
                                    f"**{var1.replace('_', ' ').title()} & {var2.replace('_', ' ').title()}:** {corr_value:.3f}"
                                )
                    else:
                        st.info("Nenhuma correlação negativa significativa encontrada.")
                
                # Dar contexto e interpretação das principais correlações
                st.markdown("<h4>📊 Interpretação das Correlações</h4>", unsafe_allow_html=True)
                
                # Encontrar a correlação mais forte (seja positiva ou negativa)
                strongest_corr = corr_matrix.stack().abs().sort_values(ascending=False).head(1)
                
                if not strongest_corr.empty:
                    (var1, var2), abs_corr_value = strongest_corr.index[0], strongest_corr.values[0]
                    actual_corr = corr_matrix.loc[var1, var2]
                    
                    if actual_corr > 0:
                        relationship = "positiva"
                        interpretation = "aumenta"
                    else:
                        relationship = "negativa"
                        interpretation = "diminui"
                    
                    insight_text = (
                        f"A correlação mais forte é uma relação {relationship} ({actual_corr:.3f}) entre "
                        f"**{var1.replace('_', ' ').title()}** e **{var2.replace('_', ' ').title()}**. "
                        f"Isso sugere que à medida que {var1.replace('_', ' ')} aumenta, {var2.replace('_', ' ')} {interpretation}. "
                    )
                    
                    if selected_dataset == "Entregadores (Suspeitos)" or selected_dataset == "Entregadores (Todos)":
                        insight_text += (
                            "Esta relação pode indicar um padrão comportamental importante dos entregadores "
                            "que deve ser considerado na estratégia de prevenção de fraudes."
                        )
                    elif selected_dataset == "Produtos":
                        insight_text += (
                            "Esta relação pode ajudar a identificar características dos produtos "
                            "que os tornam mais propensos a serem alvo de fraudes."
                        )
                    elif selected_dataset == "Tendências Temporais":
                        insight_text += (
                            "Esta relação temporal pode indicar fatores sazonais ou tendências "
                            "que influenciam a ocorrência de fraudes."
                        )
                    elif selected_dataset == "Clientes Suspeitos":
                        insight_text += (
                            "Esta relação pode revelar padrões no comportamento de clientes "
                            "que apresentam maior probabilidade de estarem envolvidos em fraudes."
                        )
                    
                    st.markdown(
                        create_insight_box(
                            insight_text,
                            icon_type="info"
                        ),
                        unsafe_allow_html=True
                    )
                    
                    # Criar gráfico de dispersão para a correlação mais forte
                    if var1 in df_for_corr.columns and var2 in df_for_corr.columns:
                        scatter_fig = create_scatter_plot(
                            df_for_corr,
                            var1,
                            var2,
                            f'Relação entre {var1.replace("_", " ").title()} e {var2.replace("_", " ").title()}'
                        )
                        
                        st.plotly_chart(scatter_fig, use_container_width=True)
    
    # Aba 2: Clusterização
    with tab2:
        st.markdown("<h3>🌟 Análise de Clusters</h3>", unsafe_allow_html=True)
        
        # Explicação
        st.markdown("""
        A análise de clusters identifica grupos (clusters) de observações com características 
        semelhantes. Isso pode revelar perfis distintos de fraude ou comportamentos que não 
        seriam facilmente identificáveis por análises tradicionais.
        """)
        
        # Selecionar dataset para clusterização
        st.markdown("<h4>Selecione o conjunto de dados para clusterização:</h4>", unsafe_allow_html=True)
        
        # Mesmo conjunto de datasets da aba anterior
        if not datasets:
            st.warning("Nenhum conjunto de dados disponível para análise de clusters.")
        else:
            # Seleção do dataset
            selected_dataset = st.selectbox("Conjunto de Dados", datasets, key="cluster_dataset")
            
            # Preparar dataframe conforme seleção
            if selected_dataset == "Entregadores (Todos)" and df_drivers is not None:
                df_for_cluster = df_drivers.copy()
                id_col = 'driver_id' if 'driver_id' in df_drivers.columns else None
                name_col = 'driver_name' if 'driver_name' in df_drivers.columns else None
            elif selected_dataset == "Entregadores (Suspeitos)" and df_suspicious_drivers is not None:
                df_for_cluster = df_suspicious_drivers.copy()
                id_col = 'driver_id' if 'driver_id' in df_suspicious_drivers.columns else None
                name_col = 'driver_name' if 'driver_name' in df_suspicious_drivers.columns else None
            elif selected_dataset == "Produtos" and df_missing_products is not None:
                df_for_cluster = df_missing_products.copy()
                id_col = 'product_id' if 'product_id' in df_missing_products.columns else None
                name_col = 'product_name' if 'product_name' in df_missing_products.columns else None
            elif selected_dataset == "Clientes Suspeitos" and df_suspicious_customers is not None:
                df_for_cluster = df_suspicious_customers.copy()
                id_col = 'customer_id' if 'customer_id' in df_suspicious_customers.columns else None
                name_col = 'customer_name' if 'customer_name' in df_suspicious_customers.columns else None
            else:
                df_for_cluster = None
                id_col = None
                name_col = None
            
            if df_for_cluster is None or df_for_cluster.empty:
                st.warning(f"O conjunto de dados '{selected_dataset}' não possui dados suficientes para clusterização.")
            else:
                # Selecionar variáveis numéricas
                numeric_cols = df_for_cluster.select_dtypes(include=['int64', 'float64']).columns.tolist()
                
                if len(numeric_cols) < 2:
                    st.warning(f"O conjunto de dados '{selected_dataset}' não possui variáveis numéricas suficientes para clusterização.")
                else:
                    # Seleção de variáveis para clusterização
                    st.markdown("<h4>Selecione as variáveis para clusterização:</h4>", unsafe_allow_html=True)
                    
                    # Remover colunas de ID da lista de opções
                    id_cols_to_remove = ['driver_id', 'product_id', 'customer_id', 'id']
                    cluster_vars = [col for col in numeric_cols if col not in id_cols_to_remove]
                    
                    if len(cluster_vars) < 2:
                        st.warning("Não há variáveis numéricas suficientes para clusterização após remover colunas de ID.")
                    else:
                        # Limitar a 4 variáveis para simplicidade
                        max_vars = min(4, len(cluster_vars))
                        
                        # Sugerir variáveis relevantes baseadas no dataset
                        default_vars = []
                        
                        if selected_dataset == "Entregadores (Todos)" or selected_dataset == "Entregadores (Suspeitos)":
                            potential_vars = ['percentual_fraude', 'media_itens_faltantes', 'total_entregas', 'age', 
                                            'missing_ratio', 'problem_order_ratio', 'avg_missing_items']
                            for var in potential_vars:
                                if var in cluster_vars and len(default_vars) < max_vars:
                                    default_vars.append(var)
                        elif selected_dataset == "Produtos":
                            potential_vars = ['total_relatos', 'price', 'valor_total_perdido']
                            for var in potential_vars:
                                if var in cluster_vars and len(default_vars) < max_vars:
                                    default_vars.append(var)
                        elif selected_dataset == "Clientes Suspeitos":
                            potential_vars = ['percentual_fraude', 'media_itens_faltantes', 'total_pedidos', 'customer_age']
                            for var in potential_vars:
                                if var in cluster_vars and len(default_vars) < max_vars:
                                    default_vars.append(var)
                        
                        # Se não conseguimos preencher com variáveis sugeridas, pegar as primeiras disponíveis
                        while len(default_vars) < 2:
                            for var in cluster_vars:
                                if var not in default_vars:
                                    default_vars.append(var)
                                    if len(default_vars) == 2:
                                        break
                        
                        # Permitir seleção de variáveis
                        selected_vars = st.multiselect(
                            "Variáveis para Clusterização",
                            options=cluster_vars,
                            default=default_vars[:2]
                        )
                        
                        if len(selected_vars) < 2:
                            st.warning("Selecione pelo menos 2 variáveis para clusterização.")
                        else:
                            # Seleção do número de clusters
                            num_clusters = st.slider("Número de Clusters", min_value=2, max_value=7, value=3)
                            
                            # Aplicar clusterização
                            try:
                                df_clustered = cluster_data(df_for_cluster, selected_vars, n_clusters=num_clusters)
                                
                                if 'cluster' not in df_clustered.columns:
                                    st.error("Falha ao criar clusters. Verifique os dados e tente novamente.")
                                else:
                                    # Visualizar resultados da clusterização
                                    st.markdown("<h4>Resultados da Clusterização:</h4>", unsafe_allow_html=True)
                                    
                                    # Mostrar contagem por cluster
                                    cluster_counts = df_clustered['cluster'].value_counts().reset_index()
                                    cluster_counts.columns = ['Cluster', 'Contagem']
                                    
                                    # Criar gráfico de barras para contagem de clusters
                                    fig = create_bar_chart(
                                        cluster_counts,
                                        'Cluster',
                                        'Contagem',
                                        'Distribuição por Cluster'
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Mostrar médias das variáveis por cluster
                                    cluster_means = df_clustered.groupby('cluster')[selected_vars].mean().reset_index()
                                    
                                    # Formatar tabela para exibição
                                    st.markdown("<h4>Características dos Clusters:</h4>", unsafe_allow_html=True)
                                    
                                    # Adicionar percentual do total para cada cluster
                                    total_items = len(df_clustered)
                                    cluster_means['percentual'] = cluster_counts['Contagem'] / total_items * 100
                                    
                                    # Renomear colunas para exibição
                                    display_cols = ['cluster'] + selected_vars + ['percentual']
                                    display_df = cluster_means[display_cols].copy()
                                    
                                    rename_map = {
                                        'cluster': 'Cluster',
                                        'percentual': 'Percentual (%)'
                                    }
                                    
                                    for var in selected_vars:
                                        rename_map[var] = var.replace('_', ' ').title()
                                    
                                    display_df = display_df.rename(columns=rename_map)
                                    
                                    # Formatar números
                                    for col in display_df.columns:
                                        if col != 'Cluster':
                                            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")
                                    
                                    st.dataframe(display_df, use_container_width=True)
                                    
                                    # Visualização 2D dos clusters
                                    if len(selected_vars) >= 2:
                                        st.markdown("<h4>Visualização dos Clusters:</h4>", unsafe_allow_html=True)
                                        
                                        # Seleção de variáveis para visualização
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            x_var = st.selectbox("Variável X", selected_vars, index=0)
                                        
                                        with col2:
                                            remaining_vars = [var for var in selected_vars if var != x_var]
                                            y_var = st.selectbox("Variável Y", remaining_vars, index=0)
                                        
                                        # Criar scatter plot com clusters
                                        fig = px.scatter(
                                            df_clustered,
                                            x=x_var,
                                            y=y_var,
                                            color='cluster',
                                            hover_name=name_col if name_col in df_clustered.columns else None,
                                            title=f'Visualização de Clusters: {x_var.replace("_", " ").title()} vs {y_var.replace("_", " ").title()}',
                                            color_continuous_scale=px.colors.sequential.Viridis
                                        )
                                        
                                        fig.update_layout(
                                            xaxis_title=x_var.replace("_", " ").title(),
                                            yaxis_title=y_var.replace("_", " ").title(),
                                            legend_title="Cluster",
                                            font=dict(family="sans serif"),
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            plot_bgcolor='rgba(0,0,0,0)',
                                        )
                                        
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Identificar características de cada cluster
                                        st.markdown("<h4>Interpretação dos Clusters:</h4>", unsafe_allow_html=True)
                                        
                                        for i in range(num_clusters):
                                            cluster_data = cluster_means[cluster_means['cluster'] == i]
                                            
                                            if not cluster_data.empty:
                                                # Criar uma descrição do cluster
                                                cluster_size = cluster_counts[cluster_counts['Cluster'] == i]['Contagem'].values[0]
                                                cluster_pct = cluster_size / total_items * 100
                                                
                                                description = f"**Cluster {i}** ({cluster_size} itens, {cluster_pct:.1f}% do total):"
                                                
                                                # Determinar características distintivas
                                                traits = []
                                                
                                                for var in selected_vars:
                                                    var_mean = cluster_data[var].values[0]
                                                    overall_mean = df_clustered[var].mean()
                                                    
                                                    # Verificar se o valor é significativamente diferente da média geral
                                                    if var_mean > overall_mean * 1.2:
                                                        traits.append(f"**{var.replace('_', ' ').title()}** é **alto** ({var_mean:.2f} vs média de {overall_mean:.2f})")
                                                    elif var_mean < overall_mean * 0.8:
                                                        traits.append(f"**{var.replace('_', ' ').title()}** é **baixo** ({var_mean:.2f} vs média de {overall_mean:.2f})")
                                                
                                                # Criar interpretação baseada no dataset
                                                interpretation = ""
                                                
                                                if selected_dataset == "Entregadores (Todos)" or selected_dataset == "Entregadores (Suspeitos)":
                                                    if any("fraude" in trait.lower() for trait in traits) or any("faltantes" in trait.lower() for trait in traits):
                                                        if any("alto" in trait for trait in traits):
                                                            interpretation = "Este grupo de entregadores apresenta **alto risco** e merece atenção prioritária."
                                                        else:
                                                            interpretation = "Este grupo de entregadores apresenta **baixo risco** e parece seguir os procedimentos corretamente."
                                                elif selected_dataset == "Produtos":
                                                    if any("relatos" in trait.lower() for trait in traits):
                                                        if any("alto" in trait for trait in traits):
                                                            interpretation = "Esta categoria de produtos é **frequentemente alvo** de fraudes e requer protocolos especiais de verificação."
                                                        else:
                                                            interpretation = "Esta categoria de produtos é **raramente alvo** de fraudes."
                                                elif selected_dataset == "Clientes Suspeitos":
                                                    if any("fraude" in trait.lower() for trait in traits) or any("faltantes" in trait.lower() for trait in traits):
                                                        if any("alto" in trait for trait in traits):
                                                            interpretation = "Este grupo de clientes apresenta **padrão suspeito** de reclamações de itens não entregues."
                                                        else:
                                                            interpretation = "Este grupo de clientes apresenta **padrão normal** de reclamações."
                                                
                                                # Exibir descrição completa
                                                st.markdown(description)
                                                for trait in traits:
                                                    st.markdown(f"- {trait}")
                                                if interpretation:
                                                    st.markdown(f"- *{interpretation}*")
                                                st.markdown("")  # Linha em branco entre clusters
                            except Exception as e:
                                st.error(f"Erro ao realizar clusterização: {e}")
                                st.info("Tente selecionar outras variáveis ou reduzir o número de clusters.")
    
    # Aba 3: Padrões Sequenciais
    with tab3:
        st.markdown("<h3>📋 Análise de Padrões Sequenciais</h3>", unsafe_allow_html=True)
        
        # Explicação
        st.markdown("""
        A análise de padrões sequenciais identifica sequências de eventos que ocorrem frequentemente 
        e podem indicar comportamentos fraudulentos. Estes padrões temporais ou sequenciais são 
        particularmente úteis para identificar esquemas de fraude organizados.
        """)
        
        # Verificar se temos dados de tendência temporal
        if df_fraud_trend is not None and not df_fraud_trend.empty and 'date' in df_fraud_trend.columns:
            # Preparar dados
            df_trend = df_fraud_trend.copy()
            
            # Garantir que a coluna de data seja datetime
            if not pd.api.types.is_datetime64_any_dtype(df_trend['date']):
                df_trend['date'] = pd.to_datetime(df_trend['date'])
            
            # Ordenar por data
            df_trend = df_trend.sort_values('date')
            
            # Adicionar indicadores temporais
            if 'dia_semana' not in df_trend.columns:
                df_trend['dia_semana'] = df_trend['date'].dt.day_name()
            if 'mes' not in df_trend.columns:
                df_trend['mes'] = df_trend['date'].dt.month_name()
            if 'semana_ano' not in df_trend.columns:
                df_trend['semana_ano'] = df_trend['date'].dt.isocalendar().week
            
            # Detecção de padrões de sazonalidade
            st.markdown("<h4>Padrões Sazonais de Fraude:</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Análise por dia da semana
            with col1:
                weekday_data = df_trend.groupby('dia_semana').agg({
                    'percentual_fraude': 'mean',
                    'itens_faltantes': 'sum',
                    'total_pedidos': 'sum'
                }).reset_index()
                
                # Ordenar dias da semana corretamente
                dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                # Verificar se os dias estão em inglês
                if all(day in dias_ordem for day in weekday_data['dia_semana'].unique()):
                    # Criar mapeamento para ordenação
                    dias_map = {dia: i for i, dia in enumerate(dias_ordem)}
                    weekday_data['ordem'] = weekday_data['dia_semana'].map(dias_map)
                    weekday_data = weekday_data.sort_values('ordem')
                    weekday_data = weekday_data.drop('ordem', axis=1)
                    
                    # Traduzir nomes dos dias
                    dias_pt = {
                        'Monday': 'Segunda',
                        'Tuesday': 'Terça',
                        'Wednesday': 'Quarta',
                        'Thursday': 'Quinta',
                        'Friday': 'Sexta',
                        'Saturday': 'Sábado',
                        'Sunday': 'Domingo'
                    }
                    
                    weekday_data['dia_semana'] = weekday_data['dia_semana'].map(dias_pt)
                
                # Criar gráfico de barras
                fig = create_bar_chart(
                    weekday_data,
                    'dia_semana',
                    'percentual_fraude',
                    'Taxa de Fraude por Dia da Semana'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Identificar padrão semanal
                if not weekday_data.empty:
                    max_day_idx = weekday_data['percentual_fraude'].idxmax()
                    min_day_idx = weekday_data['percentual_fraude'].idxmin()
                    max_day = weekday_data.loc[max_day_idx]
                    min_day = weekday_data.loc[min_day_idx]
                    
                    st.markdown(
                        create_insight_box(
                            f"**{max_day['dia_semana']}** apresenta a maior taxa de fraude semanal ({max_day['percentual_fraude']:.2f}%), "
                            f"enquanto **{min_day['dia_semana']}** apresenta a menor ({min_day['percentual_fraude']:.2f}%). "
                            "Esta variação semanal pode indicar padrões operacionais que facilitam fraudes em dias específicos.",
                            icon_type="info"
                        ),
                        unsafe_allow_html=True
                    )
            
            # Análise por mês
            with col2:
                month_data = df_trend.groupby('mes').agg({
                    'percentual_fraude': 'mean',
                    'itens_faltantes': 'sum',
                    'total_pedidos': 'sum'
                }).reset_index()
                
                # Ordenar meses corretamente
                meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 
                             'July', 'August', 'September', 'October', 'November', 'December']
                
                # Verificar se os meses estão em inglês
                if all(month in meses_ordem for month in month_data['mes'].unique()):
                    # Criar mapeamento para ordenação
                    meses_map = {mes: i for i, mes in enumerate(meses_ordem)}
                    month_data['ordem'] = month_data['mes'].map(meses_map)
                    month_data = month_data.sort_values('ordem')
                    month_data = month_data.drop('ordem', axis=1)
                    
                    # Traduzir nomes dos meses
                    meses_pt = {
                        'January': 'Janeiro',
                        'February': 'Fevereiro',
                        'March': 'Março',
                        'April': 'Abril',
                        'May': 'Maio',
                        'June': 'Junho',
                        'July': 'Julho',
                        'August': 'Agosto',
                        'September': 'Setembro',
                        'October': 'Outubro',
                        'November': 'Novembro',
                        'December': 'Dezembro'
                    }
                    
                    month_data['mes'] = month_data['mes'].map(meses_pt)
                
                # Criar gráfico de barras
                fig = create_bar_chart(
                    month_data,
                    'mes',
                    'percentual_fraude',
                    'Taxa de Fraude por Mês'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Identificar padrão mensal
                if not month_data.empty:
                    max_month_idx = month_data['percentual_fraude'].idxmax()
                    min_month_idx = month_data['percentual_fraude'].idxmin()
                    max_month = month_data.loc[max_month_idx]
                    min_month = month_data.loc[min_month_idx]
                    
                    st.markdown(
                        create_insight_box(
                            f"**{max_month['mes']}** apresenta a maior taxa de fraude anual ({max_month['percentual_fraude']:.2f}%), "
                            f"enquanto **{min_month['mes']}** apresenta a menor ({min_month['percentual_fraude']:.2f}%). "
                            "Esta sazonalidade pode estar relacionada a fatores como volume de vendas, disponibilidade de produtos ou mudanças operacionais.",
                            icon_type="info"
                        ),
                        unsafe_allow_html=True
                    )
            
            # Detecção de anomalias na série temporal
            st.markdown("<h4>Detecção de Anomalias Temporais:</h4>", unsafe_allow_html=True)
            
            # Detectar outliers na série temporal
            df_trend_anomalies = detect_anomalies(df_trend, 'percentual_fraude', threshold=2.0)
            
            # Contar anomalias
            anomaly_count = df_trend_anomalies['anomalia'].sum()
            
            # Criar gráfico de série temporal com destaque para anomalias
            fig = px.line(
                df_trend_anomalies,
                x='date',
                y='percentual_fraude',
                title='Detecção de Anomalias na Taxa de Fraude ao Longo do Tempo'
            )
            
            # Adicionar pontos para anomalias
            fig.add_scatter(
                x=df_trend_anomalies[df_trend_anomalies['anomalia']]['date'],
                y=df_trend_anomalies[df_trend_anomalies['anomalia']]['percentual_fraude'],
                mode='markers',
                marker=dict(color='red', size=10),
                name='Anomalias'
            )
            
            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Taxa de Fraude (%)",
                font=dict(family="sans serif"),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Exibir detalhes das anomalias
            if anomaly_count > 0:
                st.markdown(f"**{anomaly_count} anomalias detectadas na série temporal.**")
                
                # Exibir tabela de anomalias
                anomaly_dates = df_trend_anomalies[df_trend_anomalies['anomalia']]
                
                # Formatar para exibição
                display_cols = ['date', 'percentual_fraude', 'total_pedidos', 'itens_faltantes']
                display_cols = [col for col in display_cols if col in anomaly_dates.columns]
                
                # Renomear colunas para exibição
                rename_map = {
                    'date': 'Data',
                    'percentual_fraude': 'Taxa de Fraude (%)',
                    'total_pedidos': 'Total de Pedidos',
                    'itens_faltantes': 'Itens Faltantes'
                }
                
                display_df = anomaly_dates[display_cols].copy().rename(columns=rename_map)
                
                # Formatar data
                if 'Data' in display_df.columns:
                    display_df['Data'] = display_df['Data'].dt.strftime('%d/%m/%Y')
                
                # Ordenar por taxa de fraude
                display_df = display_df.sort_values('Taxa de Fraude (%)', ascending=False)
                
                st.dataframe(display_df, use_container_width=True)
                
                # Gerar insight sobre as anomalias
                max_anomaly = anomaly_dates.sort_values('percentual_fraude', ascending=False).iloc[0]
                max_anomaly_date = max_anomaly['date'].strftime('%d/%m/%Y')
                max_anomaly_rate = max_anomaly['percentual_fraude']
                
                st.markdown(
                    create_insight_box(
                        f"A anomalia mais significativa ocorreu em **{max_anomaly_date}** com uma taxa de fraude de **{max_anomaly_rate:.2f}%**. "
                        "Recomenda-se investigar eventos específicos ou mudanças operacionais nesta data que possam ter contribuído para este pico.",
                        icon_type="warning"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.success("Não foram detectadas anomalias significativas na série temporal.")
        else:
            st.warning("Dados de tendência temporal insuficientes para análise de padrões sequenciais.")
    
    # Adicionar narrativa na barra lateral
    with st.sidebar:
        st.markdown("<h3>🔍 Padrões Ocultos</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        ### Descobrindo Insights Profundos
        
        A análise avançada de padrões revela:
        
        1. **Correlações não óbvias** entre variáveis que podem indicar fraude
        2. **Agrupamentos naturais** de entregadores, produtos ou clientes com comportamentos similares
        3. **Padrões temporais** que podem indicar esquemas organizados
        4. **Anomalias estatísticas** que merecem investigação prioritária
        
        #### Como aplicar estes insights:
        
        - Utilize correlações para entender relações causais
        - Aplique diferentes estratégias para cada cluster identificado
        - Programe verificações adicionais durante períodos com padrões sazonais de fraude
        - Investigue imediatamente anomalias estatisticamente significativas
        
        > **Dica**: Os padrões detectados podem evoluir com o tempo.
        > Atualize as análises regularmente para capturar
        > novas tendências emergentes.
        """)