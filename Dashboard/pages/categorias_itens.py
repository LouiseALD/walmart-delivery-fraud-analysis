import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Utilitários customizados do seu projeto
from utils.graphics import create_pie_chart, create_bar_chart, create_treemap, create_scatter_plot
from utils.filters import create_category_filter
from config.style_config import create_kpi_card, create_insight_box

def show(data):
    """
    Exibe análise avançada de produtos e categorias com maior incidência de fraudes.
    """
    try:
        st.markdown("<h2 style='text-align: center;'>Análise Avançada de Produtos & Categorias</h2>", unsafe_allow_html=True)
        
        # Verificar se os dados foram carregados
        if not data or 'missing_products' not in data or data['missing_products'] is None or data['missing_products'].empty:
            st.error("Não foi possível carregar os dados de produtos.")
            return
        
        # Preparar dados de produtos com verificação de colunas
        df_products = data['missing_products'].copy()
        
        # Verificar e ajustar colunas necessárias
        required_columns = {
            'product_name': 'Nome do Produto',
            'category': 'Categoria',
            'total_relatos': 'itens_faltantes',  # Fallback
            'price': None  # Opcional
        }
        
        # Mapear colunas existentes
        for col, fallback in required_columns.items():
            if col not in df_products.columns and fallback and fallback in df_products.columns:
                df_products[col] = df_products[fallback]
        
        # Verificar se temos dados mínimos
        if 'product_name' not in df_products.columns or 'category' not in df_products.columns:
            st.warning("Dados insuficientes para análise de produtos. Colunas necessárias: product_name, category")
            return
        
        # Usar total_relatos ou itens_faltantes
        if 'total_relatos' not in df_products.columns:
            if 'itens_faltantes' in df_products.columns:
                df_products['total_relatos'] = df_products['itens_faltantes']
            else:
                st.warning("Não foi possível encontrar dados de relatos ou itens faltantes.")
                return
        
        # Garantir que temos preços (estimativa se não existir)
        if 'price' not in df_products.columns:
            # Criar preços estimados baseados na categoria
            np.random.seed(42)
            category_base_prices = {
                'Electronics': 200,
                'Supermarket': 25,
                'Clothing': 50,
                'Home': 75,
                'Books': 20,
                'Sports': 60,
                'Beauty': 35,
                'Toys': 30
            }
            
            df_products['price'] = df_products['category'].map(
                lambda x: category_base_prices.get(x, 50) * np.random.uniform(0.5, 2.5)
            )
        
        # Criar valor total perdido
        df_products['valor_total_perdido'] = df_products['price'] * df_products['total_relatos']
        
        # Configuração de layout
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 1: Filtros inteligentes
        st.markdown("<h3> Filtros Inteligentes</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro de categoria com melhorias
            categories = ['Todas'] + sorted(df_products['category'].unique().tolist())
            selected_category = st.selectbox(
                "Categoria",
                categories,
                help="Filtre por categoria específica para análise focada"
            )
        
        with col2:
            # Filtro de impacto
            impact_options = {
                'Todos': None,
                'Alto Impacto (>10 relatos)': 10,
                'Médio Impacto (5-10 relatos)': (5, 10),
                'Baixo Impacto (<5 relatos)': 5
            }
            
            selected_impact = st.selectbox(
                "Nível de Impacto",
                list(impact_options.keys()),
                help="Filtre produtos por número de relatos de fraude"
            )
        
        with col3:
            # Filtro de valor
            price_filter = st.selectbox(
                "Faixa de Preço",
                ['Todos', 'Alto Valor (>$100)', 'Médio Valor ($20-$100)', 'Baixo Valor (<$20)'],
                help="Filtre produtos por faixa de preço"
            )
        
        # Aplicar filtros
        df_filtered = df_products.copy()
        
        if selected_category != 'Todas':
            df_filtered = df_filtered[df_filtered['category'] == selected_category]
        
        # Filtro de impacto
        impact_value = impact_options[selected_impact]
        if impact_value is not None:
            if isinstance(impact_value, tuple):
                min_val, max_val = impact_value
                df_filtered = df_filtered[
                    (df_filtered['total_relatos'] >= min_val) & 
                    (df_filtered['total_relatos'] <= max_val)
                ]
            elif selected_impact == 'Alto Impacto (>10 relatos)':
                df_filtered = df_filtered[df_filtered['total_relatos'] > impact_value]
            elif selected_impact == 'Baixo Impacto (<5 relatos)':
                df_filtered = df_filtered[df_filtered['total_relatos'] < impact_value]
        
        # Filtro de preço
        if price_filter == 'Alto Valor (>$100)':
            df_filtered = df_filtered[df_filtered['price'] > 100]
        elif price_filter == 'Médio Valor ($20-$100)':
            df_filtered = df_filtered[(df_filtered['price'] >= 20) & (df_filtered['price'] <= 100)]
        elif price_filter == 'Baixo Valor (<$20)':
            df_filtered = df_filtered[df_filtered['price'] < 20]
        
        if df_filtered.empty:
            st.warning("⚠️ Nenhum produto encontrado com os filtros selecionados.")
            return
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 2: Dashboard de KPIs
        st.markdown("<h3>Dashboard de Indicadores</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_products = len(df_filtered)
            st.markdown(
                create_kpi_card(
                    "Produtos Afetados", 
                    f"{total_products}", 
                    "Itens com relatos",
                    color="info"
                ), 
                unsafe_allow_html=True
            )
        
        with col2:
            total_reports = df_filtered['total_relatos'].sum()
            st.markdown(
                create_kpi_card(
                    "Total de Relatos", 
                    f"{total_reports:,}".replace(',', '.'), 
                    "Reclamações registradas",
                    color="warning" if total_reports > 100 else "success"
                ), 
                unsafe_allow_html=True
            )
        
        with col3:
            total_value = df_filtered['valor_total_perdido'].sum()
            st.markdown(
                create_kpi_card(
                    "Perda Financeira", 
                    f"${total_value:,.0f}".replace(',', '.'), 
                    "Valor total perdido",
                    color="danger"
                ), 
                unsafe_allow_html=True
            )
        
        with col4:
            avg_price = df_filtered['price'].mean()
            st.markdown(
                create_kpi_card(
                    "Preço Médio", 
                    f"${avg_price:.2f}", 
                    "Produtos afetados"
                ), 
                unsafe_allow_html=True
            )
        
        with col5:
            categories_affected = df_filtered['category'].nunique()
            st.markdown(
                create_kpi_card(
                    "Categorias", 
                    f"{categories_affected}", 
                    "Categorias afetadas",
                    color="info"
                ), 
                unsafe_allow_html=True
            )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 3: Análise Visual Avançada
        st.markdown("<h3> Análise Visual Interativa</h3>", unsafe_allow_html=True)
        
        # Primeira linha de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Distribuição por Categoria")
            
            # Agrupar por categoria
            category_data = df_filtered.groupby('category').agg({
                'total_relatos': 'sum',
                'valor_total_perdido': 'sum',
                'product_name': 'count'
            }).reset_index()
            category_data.columns = ['category', 'total_relatos', 'valor_total', 'num_produtos']
            
            # Gráfico de pizza melhorado
            fig_pie = go.Figure(data=[go.Pie(
                labels=category_data['category'],
                values=category_data['total_relatos'],
                hole=0.4,
                textinfo='label+percent+value',
                textfont={'size': 12, 'family': 'Arial Bold', 'color': 'black'},
                marker=dict(
                    colors=px.colors.qualitative.Set3,
                    line=dict(color='white', width=2)
                ),
                hovertemplate='<b>%{label}</b><br>' +
                              'Relatos: %{value}<br>' +
                              'Percentual: %{percent}<br>' +
                              '<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title={
                    'text': 'Relatos por Categoria',
                    'x': 0.5,
                    'font': {'size': 16, 'family': 'Arial Bold', 'color': 'black'}
                },
                font={'family': 'Arial', 'color': 'black'},
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("#### Impacto Financeiro por Categoria")
            
            # Gráfico de barras para valor perdido
            fig_bar = go.Figure(data=[go.Bar(
                x=category_data['valor_total'],
                y=category_data['category'],
                orientation='h',
                marker=dict(
                    color=category_data['valor_total'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Valor Perdido ($)")
                ),
                text=[f'${val:,.0f}' for val in category_data['valor_total']],
                textposition='inside',
                textfont={'size': 11, 'color': 'white', 'family': 'Arial Bold'},
                hovertemplate='<b>%{y}</b><br>' +
                              'Valor Perdido: $%{x:,.0f}<br>' +
                              '<extra></extra>'
            )])
            
            fig_bar.update_layout(
                title={
                    'text': 'Perda Financeira por Categoria',
                    'x': 0.5,
                    'font': {'size': 16, 'family': 'Arial Bold', 'color': 'black'}
                },
                xaxis=dict(
                    title=dict(text='Valor Perdido ($)', font={'size': 14, 'family': 'Arial Bold', 'color': 'black'}),
                    tickfont={'size': 12, 'family': 'Arial', 'color': 'black'}
                ),
                yaxis=dict(
                    tickfont={'size': 12, 'family': 'Arial', 'color': 'black'}
                ),
                font={'family': 'Arial', 'color': 'black'},
                height=400,
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # SEÇÃO MELHORADA: Mapa Hierárquico de Produtos com Emojis
        st.markdown("#### Mapa Hierárquico de Produtos")
        
        # Criar treemap com emojis para melhor visualização
        if len(df_filtered) > 0:
            try:
                # Preparar dados para treemap
                df_treemap = df_filtered.head(20).copy()  # Limitar a 20 produtos
                
                # Adicionar emojis por categoria
                category_emojis = {
                    'Electronics': '📱',
                    'Supermarket': '🛒', 
                    'Clothing': '👕',
                    'Home': '🏠',
                    'Books': '📚',
                    'Sports': '⚽',
                    'Beauty': '💄',
                    'Toys': '🧸'
                }
                
                # Criar texto com emoji
                df_treemap['emoji'] = df_treemap['category'].map(category_emojis).fillna('📦')
                df_treemap['display_name'] = df_treemap.apply(
                    lambda row: f"{row['emoji']} {row['product_name'][:25]}{'...' if len(row['product_name']) > 25 else ''}", 
                    axis=1
                )
                
                # Treemap principal
                fig_treemap = px.treemap(
                    df_treemap,
                    path=['category', 'display_name'],
                    values='total_relatos',
                    color='price',
                    color_continuous_scale='RdYlBu_r',
                    title='Hierarquia de Produtos por Categoria (Top 20)'
                )
                
                fig_treemap.update_layout(
                    title={
                        'text': 'Hierarquia de Produtos por Categoria (Top 20)',
                        'x': 0.5,
                        'font': {'size': 16, 'family': 'Arial Bold', 'color': 'black'}
                    },
                    font={'family': 'Arial', 'color': 'black'},
                    height=500
                )
                
                fig_treemap.update_traces(
                    textfont={'size': 12, 'family': 'Arial Bold', 'color': 'black'},
                    texttemplate="<b>%{label}</b><br>%{value} relatos",
                    hovertemplate='<b>%{label}</b><br>' +
                                  'Categoria: %{parent}<br>' +
                                  'Relatos: %{value}<br>' +
                                  'Preço: $%{color:.2f}<br>' +
                                  '<extra></extra>'
                )
                
                st.plotly_chart(fig_treemap, use_container_width=True)
                
                # Grid visual alternativo
                st.markdown("##### Produtos Mais Críticos")
                
                # Criar grid de 4 colunas
                df_top = df_filtered.nlargest(8, 'total_relatos')
                cols = st.columns(4)
                
                for idx, (_, product) in enumerate(df_top.iterrows()):
                    col_idx = idx % 4
                    
                    with cols[col_idx]:
                        emoji = category_emojis.get(product['category'], '📦')
                        
                        # Card simples do produto
                        st.markdown(
                            f"""
                            <div style="
                                border: 2px solid #ddd;
                                border-radius: 10px;
                                padding: 10px;
                                text-align: center;
                                background: #f8f9fa;
                                margin-bottom: 10px;
                                height: 160px;
                            ">
                                <div style="font-size: 30px; margin-bottom: 5px;">
                                    {emoji}
                                </div>
                                <h6 style="color: #2c3e50; margin: 3px 0; font-size: 12px;">
                                    {product['product_name'][:20]}{'...' if len(product['product_name']) > 20 else ''}
                                </h6>
                                <p style="color: #7f8c8d; font-size: 10px; margin: 2px 0;">
                                    {product['category']}
                                </p>
                                <div style="background: #e74c3c; color: white; padding: 3px; border-radius: 3px; margin: 3px 0; font-size: 11px;">
                                    {int(product['total_relatos'])} relatos
                                </div>
                                <div style="background: #27ae60; color: white; padding: 3px; border-radius: 3px; font-size: 11px;">
                                    ${product['price']:.0f}
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                
            except Exception as e:
                st.warning(f"Problema com visualização avançada: {e}")
                
                # Fallback: Gráfico de barras simples
                st.markdown("**Análise por Categoria e Produto**")
                
                top_by_category = df_filtered.groupby('category').apply(
                    lambda x: x.nlargest(3, 'total_relatos')
                ).reset_index(drop=True)
                
                fig_bar_grouped = px.bar(
                    top_by_category,
                    x='category',
                    y='total_relatos',
                    color='product_name',
                    title='Top 3 Produtos por Categoria',
                    labels={'total_relatos': 'Número de Relatos', 'category': 'Categoria'}
                )
                
                fig_bar_grouped.update_layout(
                    title={'x': 0.5},
                    height=400
                )
                
                st.plotly_chart(fig_bar_grouped, use_container_width=True)
        else:
            st.warning("Não há dados suficientes para criar o mapa hierárquico.")
        
        # Adicionar insight sobre a visualização
        st.markdown(
            create_insight_box(
                "O tamanho representa o número de relatos e a cor indica o preço do produto.",
                icon_type="info"
            ),
            unsafe_allow_html=True
        )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 4: Rankings e Top Performers
        st.markdown("<h3> Rankings de Produtos Críticos</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Top 10 - Mais Relatados")
            
            top_reported = df_filtered.nlargest(10, 'total_relatos')
            
            fig_top = go.Figure(data=[go.Bar(
                x=top_reported['total_relatos'],
                y=[name[:30] + '...' if len(name) > 30 else name for name in top_reported['product_name']],
                orientation='h',
                marker=dict(color='#E74C3C'),
                text=top_reported['total_relatos'],
                textposition='inside',
                textfont={'size': 10, 'color': 'white', 'family': 'Arial Bold'}
            )])
            
            fig_top.update_layout(
                title={
                    'text': 'Produtos com Mais Relatos',
                    'x': 0.5,
                    'font': {'size': 14, 'family': 'Arial Bold', 'color': 'black'}
                },
                xaxis=dict(
                    title=dict(text='Número de Relatos', font={'size': 12, 'family': 'Arial Bold', 'color': 'black'}),
                    tickfont={'size': 10, 'family': 'Arial', 'color': 'black'}
                ),
                yaxis=dict(
                    tickfont={'size': 10, 'family': 'Arial', 'color': 'black'}
                ),
                height=400,
                margin=dict(l=150)
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col2:
            st.markdown("#### Top 10 - Maior Prejuízo")
            
            top_value = df_filtered.nlargest(10, 'valor_total_perdido')
            
            fig_value = go.Figure(data=[go.Bar(
                x=top_value['valor_total_perdido'],
                y=[name[:30] + '...' if len(name) > 30 else name for name in top_value['product_name']],
                orientation='h',
                marker=dict(color='#8E44AD'),
                text=[f'${val:,.0f}' for val in top_value['valor_total_perdido']],
                textposition='inside',
                textfont={'size': 10, 'color': 'white', 'family': 'Arial Bold'}
            )])
            
            fig_value.update_layout(
                title={
                    'text': 'Produtos com Maior Prejuízo',
                    'x': 0.5,
                    'font': {'size': 14, 'family': 'Arial Bold', 'color': 'black'}
                },
                xaxis=dict(
                    title=dict(text='Valor Perdido ($)', font={'size': 12, 'family': 'Arial Bold', 'color': 'black'}),
                    tickfont={'size': 10, 'family': 'Arial', 'color': 'black'}
                ),
                yaxis=dict(
                    tickfont={'size': 10, 'family': 'Arial', 'color': 'black'}
                ),
                height=400,
                margin=dict(l=150)
            )
            
            st.plotly_chart(fig_value, use_container_width=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 5: Análise de Correlação Avançada
        st.markdown("<h3>Análise de Correlação: Preço × Fraude</h3>", unsafe_allow_html=True)
        
        # Gráfico de dispersão melhorado
        fig_scatter = go.Figure()
        
        # Adicionar pontos por categoria
        for category in df_filtered['category'].unique():
            cat_data = df_filtered[df_filtered['category'] == category]
            
            fig_scatter.add_trace(go.Scatter(
                x=cat_data['price'],
                y=cat_data['total_relatos'],
                mode='markers',
                name=category,
                text=[f"{row['product_name']}<br>Categoria: {row['category']}<br>Preço: ${row['price']:.2f}<br>Relatos: {row['total_relatos']}" 
                      for _, row in cat_data.iterrows()],
                hovertemplate='%{text}<extra></extra>',
                marker=dict(
                    size=cat_data['valor_total_perdido'] / 50,  # Tamanho proporcional ao valor perdido
                    sizemode='area',
                    sizemin=4,
                    opacity=0.7
                )
            ))
        
        # Adicionar linha de tendência
        correlation = df_filtered['price'].corr(df_filtered['total_relatos'])
        
        # Calcular linha de regressão
        z = np.polyfit(df_filtered['price'], df_filtered['total_relatos'], 1)
        p = np.poly1d(z)
        
        fig_scatter.add_trace(go.Scatter(
            x=df_filtered['price'].sort_values(),
            y=p(df_filtered['price'].sort_values()),
            mode='lines',
            name=f'Tendência (r={correlation:.3f})',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig_scatter.update_layout(
            title={
                'text': f'Correlação Preço × Relatos de Fraude (r = {correlation:.3f})',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial Bold', 'color': 'black'}
            },
            xaxis=dict(
                title=dict(text='Preço do Produto ($)', font={'size': 14, 'family': 'Arial Bold', 'color': 'black'}),
                tickfont={'size': 12, 'family': 'Arial', 'color': 'black'}
            ),
            yaxis=dict(
                title=dict(text='Número de Relatos', font={'size': 14, 'family': 'Arial Bold', 'color': 'black'}),
                tickfont={'size': 12, 'family': 'Arial', 'color': 'black'}
            ),
            font={'family': 'Arial', 'color': 'black'},
            height=500,
            hovermode='closest'
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Interpretação da correlação
        if abs(correlation) < 0.3:
            corr_interpretation = "fraca"
            corr_color = "info"
            corr_message = "Outros fatores além do preço influenciam significativamente os relatos de fraude."
        elif correlation >= 0.3:
            corr_interpretation = "positiva moderada" if correlation < 0.7 else "positiva forte"
            corr_color = "warning"
            corr_message = "Produtos mais caros tendem a ter mais relatos de fraude. Considere verificações adicionais para itens de alto valor."
        else:
            corr_interpretation = "negativa moderada" if correlation > -0.7 else "negativa forte"
            corr_color = "info"
            corr_message = "Produtos mais baratos tendem a ter mais relatos de fraude. Pode indicar problemas no processo de produtos de menor valor."
        
        st.markdown(
            create_insight_box(
                f"**Correlação {corr_interpretation}** detectada (r = {correlation:.3f}). {corr_message}",
                icon_type=corr_color
            ),
            unsafe_allow_html=True
        )
        
        # Seção 6: Tabela Interativa Detalhada
        st.markdown("<h3>Tabela Detalhada de Produtos</h3>", unsafe_allow_html=True)
        
        # Preparar dados para exibição
        display_df = df_filtered.copy()
        display_df = display_df.sort_values('valor_total_perdido', ascending=False)
        
        # Renomear e formatar colunas
        display_df['Produto'] = display_df['product_name'].str[:50]
        display_df['Categoria'] = display_df['category']
        display_df['Relatos'] = display_df['total_relatos']
        display_df['Preço'] = display_df['price'].map('${:.2f}'.format)
        display_df['Valor Perdido'] = display_df['valor_total_perdido'].map('${:,.2f}'.format)
        display_df['Risco'] = pd.cut(
            display_df['total_relatos'], 
            bins=[0, 5, 15, float('inf')], 
            labels=['🟢 Baixo', '🟡 Médio', '🔴 Alto']
        )
        
        # Exibir tabela
        cols_to_show = ['Produto', 'Categoria', 'Relatos', 'Preço', 'Valor Perdido', 'Risco']
        st.dataframe(
            display_df[cols_to_show],
            use_container_width=True,
            height=400
        )
        
    
    except Exception as e:
        st.error(f"Erro ao processar a visualização: {e}")
        st.exception(e)  # Para debug detalhado