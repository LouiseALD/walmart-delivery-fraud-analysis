import streamlit as st
import pandas as pd

# Utilitários customizados do seu projeto
from utils.graphics import create_pie_chart, create_bar_chart, create_treemap, create_scatter_plot
from utils.filters import create_category_filter
from utils.loaders import prepare_product_data
from config.style_config import create_kpi_card, create_insight_box



def show(data):
    """    Exibe análise de produtos e categorias com maior incidência de fraudes.
    except Exception as e:
        st.error(f"Erro ao processar a visualização: {e}")
    
    Args:
        data: Dicionário com DataFrames para análise
    """
    try:
        st.markdown("<h2 style='text-align: center;'>📦 Produtos & Categorias com Fraudes</h2>", unsafe_allow_html=True)
    
   
        # Verificar se os dados foram carregados
        if not data or 'missing_products' not in data or data['missing_products'] is None or data['missing_products'].empty:
            st.error("Não foi possível carregar os dados de produtos.")
            return
        
        # Preparar dados de produtos
        df_products, category_summary = prepare_product_data(data['missing_products'])
        
        if df_products is None or df_products.empty:
            st.warning("Dados insuficientes para análise de produtos.")
            return
        
        # Configuração de layout
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 1: Filtros específicos para produtos
        st.markdown("<h3>🔍 Filtros de Produto</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # Filtro de categoria
        with col1:
            selected_category = create_category_filter(df_products, 'category', 'products_page')
            
            # Aplicar filtro de categoria
            if selected_category != "Todas":
                df_products_filtered = df_products[df_products['category'] == selected_category]
            else:
                df_products_filtered = df_products
        
        # Filtro de valor
        with col2:
            if 'price' in df_products.columns:
                min_price = float(df_products['price'].min())
                max_price = float(df_products['price'].max())
                
                price_range = st.slider(
                    "Faixa de Preço ($)",
                    min_value=min_price,
                    max_value=max_price,
                    value=(min_price, max_price),
                    step=0.01
                )
                
                # Aplicar filtro de preço
                min_selected, max_selected = price_range
                df_products_filtered = df_products_filtered[
                    (df_products_filtered['price'] >= min_selected) & 
                    (df_products_filtered['price'] <= max_selected)
                ]
        
        # Verificar se ainda temos dados após os filtros
        if df_products_filtered.empty:
            st.warning("Nenhum produto encontrado com os filtros selecionados.")
            return
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 2: KPIs de produtos
        st.markdown("<h3>🔑 Indicadores de Produtos</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Total de produtos com relatos
        with col1:
            total_products = len(df_products_filtered)
            st.markdown(
                create_kpi_card(
                    "Produtos com Relatos", 
                    f"{total_products}", 
                    "Produtos não entregues"
                ), 
                unsafe_allow_html=True
            )
        
        # Total de relatos
        with col2:
            total_reports = df_products_filtered['total_relatos'].sum()
            st.markdown(
                create_kpi_card(
                    "Total de Relatos", 
                    f"{total_reports:,}".replace(',', '.'), 
                    "Número de reclamações",
                    color="danger" if total_reports > 1000 else "warning"
                ), 
                unsafe_allow_html=True
            )
        
        # Valor total perdido
        with col3:
            if 'valor_total_perdido' in df_products_filtered.columns:
                total_value = df_products_filtered['valor_total_perdido'].sum()
                st.markdown(
                    create_kpi_card(
                        "Valor Total Perdido", 
                        f"${total_value:,.2f}".replace(',', '.'), 
                        "Perda financeira estimada",
                        color="danger"
                    ), 
                    unsafe_allow_html=True
                )
            elif 'price' in df_products_filtered.columns and 'total_relatos' in df_products_filtered.columns:
                total_value = (df_products_filtered['price'] * df_products_filtered['total_relatos']).sum()
                st.markdown(
                    create_kpi_card(
                        "Valor Total Perdido", 
                        f"${total_value:,.2f}".replace(',', '.'), 
                        "Perda financeira estimada",
                        color="danger"
                    ), 
                    unsafe_allow_html=True
                )
        
        # Preço médio dos produtos
        with col4:
            if 'price' in df_products_filtered.columns:
                avg_price = df_products_filtered['price'].mean()
                st.markdown(
                    create_kpi_card(
                        "Preço Médio", 
                        f"${avg_price:.2f}", 
                        "Dos produtos não entregues"
                    ), 
                    unsafe_allow_html=True
                )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 3: Análise por Categoria
        st.markdown("<h3>🏷️ Análise por Categoria de Produto</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # Distribuição de fraudes por categoria (gráfico de pizza)
        with col1:
            if category_summary is not None and not category_summary.empty:
                # Ordenar por total de relatos
                category_summary_sorted = category_summary.sort_values('total_relatos', ascending=False)
                
                # Criar gráfico de pizza
                fig = create_pie_chart(
                    category_summary_sorted,
                    'category',
                    'total_relatos',
                    'Distribuição de Fraudes por Categoria',
                    hole=0.4
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Identificar categoria mais problemática
                top_category = category_summary_sorted.iloc[0]['category']
                top_category_pct = (category_summary_sorted.iloc[0]['total_relatos'] / category_summary_sorted['total_relatos'].sum()) * 100
                
                st.markdown(
                    create_insight_box(
                        f"A categoria '{top_category}' representa {top_category_pct:.1f}% de todos os relatos de fraude. "
                        "Recomenda-se uma revisão específica dos procedimentos de entrega para estes itens.",
                        icon_type="warning"
                    ),
                    unsafe_allow_html=True
                )
        
        # Valor perdido por categoria (gráfico de barras)
        with col2:
            if category_summary is not None and not category_summary.empty and 'valor_total_perdido' in category_summary.columns:
                # Ordenar por valor perdido
                category_value_sorted = category_summary.sort_values('valor_total_perdido', ascending=False)
                
                # Criar gráfico de barras
                fig = create_bar_chart(
                    category_value_sorted,
                    'category',
                    'valor_total_perdido',
                    'Valor Perdido por Categoria ($)',
                    orientation='h'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Identificar categoria com maior prejuízo
                top_value_category = category_value_sorted.iloc[0]['category']
                top_value_amount = category_value_sorted.iloc[0]['valor_total_perdido']
                
                st.markdown(
                    create_insight_box(
                        f"A categoria '{top_value_category}' representa o maior prejuízo financeiro (${top_value_amount:,.2f}). "
                        "Priorize a investigação de fraudes nesta categoria para reduzir perdas.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 4: Treemap de categorias e produtos
        st.markdown("<h3>🗂️ Hierarquia de Produtos e Categorias</h3>", unsafe_allow_html=True)
        
        if 'category' in df_products_filtered.columns and 'product_name' in df_products_filtered.columns:
            # Criar treemap
            if 'valor_total_perdido' in df_products_filtered.columns:
                value_column = 'valor_total_perdido'
                color_column = 'price'
                title = 'Mapa Hierárquico de Fraudes por Categoria e Produto (tamanho = valor perdido, cor = preço)'
            else:
                value_column = 'total_relatos'
                color_column = 'price' if 'price' in df_products_filtered.columns else None
                title = 'Mapa Hierárquico de Fraudes por Categoria e Produto (tamanho = relatos, cor = preço)'
            
            fig = create_treemap(
                df_products_filtered,
                ['category', 'product_name'],
                value_column,
                title,
                color_column=color_column
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight sobre o treemap
            st.markdown(
                create_insight_box(
                    "O mapa hierárquico permite visualizar simultaneamente a proporção de fraudes entre categorias "
                    "e produtos específicos. Os blocos maiores representam mais relatos ou maior valor perdido.",
                    icon_type="info"
                ),
                unsafe_allow_html=True
            )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 5: Top produtos com fraudes
        st.markdown("<h3>📈 Top Produtos com Maior Incidência de Fraudes</h3>", unsafe_allow_html=True)
        
        # Ordenar produtos por total de relatos
        top_products = df_products_filtered.sort_values('total_relatos', ascending=False).head(10)
        
        if not top_products.empty:
            col1, col2 = st.columns([2, 1])
            
            # Gráfico de barras com top produtos
            with col1:
                fig = create_bar_chart(
                    top_products,
                    'product_name',
                    'total_relatos',
                    'Top 10 Produtos com Mais Relatos de Fraude',
                    orientation='h',
                    color_column='category' if 'category' in top_products.columns else None
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabela com detalhes dos top produtos
            with col2:
                st.markdown("<h4>Detalhes dos Produtos Críticos</h4>", unsafe_allow_html=True)
                
                # Preparar dados para exibição
                display_cols = ['product_name', 'category', 'total_relatos', 'price']
                
                if 'valor_total_perdido' in top_products.columns:
                    display_cols.append('valor_total_perdido')
                
                # Garantir que temos todas as colunas
                display_cols = [col for col in display_cols if col in top_products.columns]
                
                # Renomear colunas para exibição
                rename_map = {
                    'product_name': 'Produto',
                    'category': 'Categoria',
                    'total_relatos': 'Relatos',
                    'price': 'Preço ($)',
                    'valor_total_perdido': 'Valor Perdido ($)'
                }
                
                display_df = top_products[display_cols].rename(columns=rename_map)
                
                # Formatar valores numéricos
                if 'Preço ($)' in display_df.columns:
                    display_df['Preço ($)'] = display_df['Preço ($)'].map('${:.2f}'.format)
                
                if 'Valor Perdido ($)' in display_df.columns:
                    display_df['Valor Perdido ($)'] = display_df['Valor Perdido ($)'].map('${:.2f}'.format)
                
                # Exibir tabela com estilo
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=350
                )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 6: Análise de correlação preço vs fraude
        st.markdown("<h3>📊 Correlação entre Preço e Fraude</h3>", unsafe_allow_html=True)
        
        if 'price' in df_products_filtered.columns and 'total_relatos' in df_products_filtered.columns:
            # Criar gráfico de dispersão
            fig = create_scatter_plot(
                df_products_filtered,
                'price',
                'total_relatos',
                'Relação entre Preço do Produto e Quantidade de Fraudes',
                color_column='category' if 'category' in df_products_filtered.columns else None,
                text_column='product_name'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calcular correlação
            correlation = df_products_filtered['price'].corr(df_products_filtered['total_relatos'])
            
            # Interpretar correlação
            if abs(correlation) < 0.3:
                corr_message = (
                    f"Há uma correlação fraca ({correlation:.2f}) entre o preço do produto e a incidência de fraudes. "
                    "Outros fatores além do preço parecem estar influenciando os relatos."
                )
            elif correlation >= 0.3:
                corr_message = (
                    f"Há uma correlação positiva significativa ({correlation:.2f}) entre o preço do produto e a incidência de fraudes. "
                    "Produtos mais caros tendem a ter mais relatos de não entrega."
                )
            else:
                corr_message = (
                    f"Há uma correlação negativa significativa ({correlation:.2f}) entre o preço do produto e a incidência de fraudes. "
                    "Curiosamente, produtos mais baratos tendem a ter mais relatos de não entrega."
                )
            
            st.markdown(
                create_insight_box(
                    corr_message,
                    icon_type="info"
                ),
                unsafe_allow_html=True
            )
        
        # Adicionar narrativa na barra lateral
        with st.sidebar:
            st.markdown("<h3>📦 Análise de Produtos</h3>", unsafe_allow_html=True)
            
            st.markdown("""
            ### Identificação de Padrões em Produtos
            
            A análise de produtos e categorias permite:
            
            1. **Identificar itens críticos** que são frequentemente relatados como não entregues
            2. **Calcular o impacto financeiro** das fraudes por categoria
            3. **Descobrir correlações** entre características do produto e fraude
            4. **Priorizar investigações** com base no valor e frequência
            
            #### Como usar esta análise:
            
            - Utilize o treemap para visualizar hierarquicamente os produtos e categorias
            - Examine a correlação entre preço e fraude no gráfico de dispersão
            - Identifique produtos de alto valor com alta incidência de fraudes
            - Implemente verificações adicionais para categorias críticas
            
            > **Dica**: Combine esta análise com os padrões temporais e
            > perfis de motoristas para criar protocolos de verificação
            > específicos por produto.
            """)

    except Exception as e:
        st.error(f"Erro ao processar a visualização: {e}")