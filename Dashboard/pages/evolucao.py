import streamlit as st
import pandas as pd
import numpy as np
import traceback

from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Importar funções utilitárias
from utils.loaders import prepare_fraud_trend_data
from utils.graphics import create_time_series, create_bar_chart
from utils.filters import create_date_range_filter
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def show(data):
    """
    Exibe a evolução e tendências das fraudes ao longo do tempo.
    except Exception as e:
        st.error(f"Erro ao processar a visualização: {e}")
    
    Args:
        data: Dicionário com DataFrames para análise
    """

    try:

        st.markdown("<h2 style='text-align: center;'>📈 Evolução e Tendências de Fraudes</h2>", unsafe_allow_html=True)
        
        # Verificar se os dados foram carregados
        if not data or 'fraud_trend' not in data or data['fraud_trend'] is None or data['fraud_trend'].empty:
            st.error("Não foi possível carregar os dados de tendência para análise de evolução.")
            return
        
        # Preparar dados
        df_trend = prepare_fraud_trend_data(data['fraud_trend'])
        
        # Verificar se temos a coluna de data
        if 'date' not in df_trend.columns:
            st.warning("Dados de tendência não possuem informação de data. Impossível analisar evolução temporal.")
            return
        
        # Configuração de layout
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 1: Filtros temporais
        st.markdown("<h3>⏱️ Período de Análise</h3>", unsafe_allow_html=True)
        
        date_range = create_date_range_filter(df_trend, 'date', 'evolution')
        
        if date_range:
            start_date, end_date = date_range

            # Filtrar dados por período selecionado
            df_trend_filtered = df_trend[
                (df_trend['date'] >= start_date) & 
                (df_trend['date'] <= end_date)
            ]
        else:
            df_trend_filtered = df_trend

        # Garantir colunas de mês e nome do mês
        if not df_trend_filtered.empty and 'date' in df_trend_filtered.columns:
            df_trend_filtered['date'] = pd.to_datetime(df_trend_filtered['date'], errors='coerce')

            if 'mes' not in df_trend_filtered.columns:
                df_trend_filtered['mes'] = df_trend_filtered['date'].dt.month

            if 'nome_mes' not in df_trend_filtered.columns:
                df_trend_filtered['nome_mes'] = df_trend_filtered['date'].dt.month_name()

        
        # Verificar se ainda temos dados após o filtro
        if df_trend_filtered.empty:
            st.warning("Nenhum dado disponível para o período selecionado.")
            return
        
        # Calcular o período em dias
        days_count = (df_trend_filtered['date'].max() - df_trend_filtered['date'].min()).days
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 2: KPIs de Evolução
        st.markdown("<h3>🔑 Indicadores de Evolução</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # KPI 1: Período analisado
        with col1:
            st.markdown(
                create_kpi_card(
                    "Período Analisado", 
                    f"{days_count} dias", 
                    f"{df_trend_filtered['date'].min().strftime('%d/%m/%y')} - {df_trend_filtered['date'].max().strftime('%d/%m/%y')}"
                ), 
                unsafe_allow_html=True
            )
        
        # KPI 2: Tendência de fraude
        with col2:
            # Calcular tendência (comparar início e fim do período)
            if len(df_trend_filtered) >= 2:
                start_fraud_rate = df_trend_filtered.sort_values('date').iloc[0]['percentual_fraude']
                end_fraud_rate = df_trend_filtered.sort_values('date').iloc[-1]['percentual_fraude']
                trend_pct = ((end_fraud_rate - start_fraud_rate) / start_fraud_rate) * 100 if start_fraud_rate > 0 else 0
                
                trend_text = f"{trend_pct:.1f}% {'▲' if trend_pct > 0 else '▼' if trend_pct < 0 else '■'}"
                trend_color = "danger" if trend_pct > 5 else "success" if trend_pct < 0 else "warning"
                
                st.markdown(
                    create_kpi_card(
                        "Tendência de Fraude", 
                        trend_text, 
                        "Variação no período",
                        color=trend_color
                    ), 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    create_kpi_card(
                        "Tendência de Fraude", 
                        "N/D", 
                        "Dados insuficientes"
                    ), 
                    unsafe_allow_html=True
                )
        
        # KPI 3: Pico de fraude
        with col3:
            max_fraud_row = df_trend_filtered.loc[df_trend_filtered['percentual_fraude'].idxmax()]
            max_fraud_rate = max_fraud_row['percentual_fraude']
            max_fraud_date = max_fraud_row['date'].strftime('%d/%m/%y')
            
            st.markdown(
                create_kpi_card(
                    "Pico de Fraude", 
                    f"{max_fraud_rate:.2f}%", 
                    f"Em {max_fraud_date}",
                    color="danger"
                ), 
                unsafe_allow_html=True
            )
        
        # KPI 4: Menor taxa de fraude
        with col4:
            min_fraud_row = df_trend_filtered.loc[df_trend_filtered['percentual_fraude'].idxmin()]
            min_fraud_rate = min_fraud_row['percentual_fraude']
            min_fraud_date = min_fraud_row['date'].strftime('%d/%m/%y')
            
            st.markdown(
                create_kpi_card(
                    "Menor Taxa de Fraude", 
                    f"{min_fraud_rate:.2f}%", 
                    f"Em {min_fraud_date}",
                    color="success"
                ), 
                unsafe_allow_html=True
            )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 3: Gráfico de evolução temporal
        st.markdown("<h3>📊 Evolução Temporal das Fraudes</h3>", unsafe_allow_html=True)
        
        # Criar gráfico de série temporal
        fig_time_series = create_time_series(
            df_trend_filtered,
            'date',
            'percentual_fraude',
            'Evolução da Taxa de Fraude ao Longo do Tempo',
            add_trendline=True,
            secondary_y_column='total_pedidos'
        )
        
        st.plotly_chart(fig_time_series, use_container_width=True)
        
        # Adicionar análise de tendência
        if len(df_trend_filtered) >= 10:
            # Criar uma média móvel para suavizar a tendência
            if 'media_movel_7d' not in df_trend_filtered.columns:
                df_trend_filtered['media_movel_7d'] = df_trend_filtered['percentual_fraude'].rolling(window=7, min_periods=1).mean()
            
            # Dividir o período em início, meio e fim para análise
            period_length = len(df_trend_filtered)
            start_period = df_trend_filtered.iloc[:int(period_length/3)]
            middle_period = df_trend_filtered.iloc[int(period_length/3):int(2*period_length/3)]
            end_period = df_trend_filtered.iloc[int(2*period_length/3):]
            
            # Calcular tendências por período
            start_avg = start_period['percentual_fraude'].mean()
            middle_avg = middle_period['percentual_fraude'].mean()
            end_avg = end_period['percentual_fraude'].mean()
            
            # Interpretar tendências
            trend_message = ""
            
            if end_avg > middle_avg > start_avg:
                trend_message = "🚨 **Tendência de alta contínua**: A taxa de fraude aumentou consistentemente durante todo o período analisado."
                trend_icon = "warning"
            elif end_avg < middle_avg < start_avg:
                trend_message = "✅ **Tendência de queda contínua**: A taxa de fraude diminuiu consistentemente durante todo o período analisado."
                trend_icon = "info"
            elif middle_avg > start_avg and middle_avg > end_avg:
                trend_message = "📊 **Tendência de pico central**: A taxa de fraude aumentou na parte central do período e depois diminuiu."
                trend_icon = "info"
            elif middle_avg < start_avg and middle_avg < end_avg:
                trend_message = "📊 **Tendência de vale central**: A taxa de fraude diminuiu na parte central do período e depois aumentou."
                trend_icon = "warning"
            elif end_avg > start_avg:
                trend_message = "⚠️ **Tendência geral de alta**: Apesar de algumas variações, a taxa de fraude aumentou quando comparamos o início e fim do período."
                trend_icon = "warning"
            elif end_avg < start_avg:
                trend_message = "📉 **Tendência geral de queda**: Apesar de algumas variações, a taxa de fraude diminuiu quando comparamos o início e fim do período."
                trend_icon = "info"
            else:
                trend_message = "➡️ **Tendência estável**: A taxa de fraude permaneceu relativamente estável durante o período analisado."
                trend_icon = "info"
            
            st.markdown(
                create_insight_box(
                    trend_message + f" A taxa média de fraude passou de {start_avg:.2f}% no início para {end_avg:.2f}% no final do período.",
                    icon_type=trend_icon
                ),
                unsafe_allow_html=True
            )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 4: Análise de sazonalidade
        st.markdown("<h3>🔄 Análise de Padrões Sazonais</h3>", unsafe_allow_html=True)
        
        # Preparar dados de sazonalidade
        # Adicionar dia da semana se não existir
        if 'dia_semana' not in df_trend_filtered.columns:
            df_trend_filtered['dia_semana'] = df_trend_filtered['date'].dt.day_name()
        
        # Adicionar mês se não existir
        if 'mes' not in df_trend_filtered.columns:
            df_trend_filtered['mes'] = df_trend_filtered['date'].dt.month
            df_trend_filtered['nome_mes'] = df_trend_filtered['date'].dt.month_name()
        
        col1, col2 = st.columns(2)
        
        # Análise por dia da semana
        with col1:
            weekday_data = df_trend_filtered.groupby('dia_semana').agg({
                'percentual_fraude': 'mean',
                'total_pedidos': 'mean'
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
            fig_weekday = create_bar_chart(
                weekday_data,
                'dia_semana',
                'percentual_fraude',
                'Taxa Média de Fraude por Dia da Semana'
            )
            
            st.plotly_chart(fig_weekday, use_container_width=True)
        
        # Análise por mês
        with col2:
            if 'nome_mes' in df_trend_filtered.columns:
                month_data = df_trend_filtered.groupby(['mes', 'nome_mes']).agg({
                    'percentual_fraude': 'mean',
                    'total_pedidos': 'mean'
                }).reset_index()
                
                # Ordenar meses corretamente
                month_data = month_data.sort_values('mes')
                
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
                
                if all(month in meses_pt for month in month_data['nome_mes'].unique()):
                    month_data['nome_mes'] = month_data['nome_mes'].map(meses_pt)
                
                # Criar gráfico de barras
                fig_month = create_bar_chart(
                    month_data,
                    'nome_mes',
                    'percentual_fraude',
                    'Taxa Média de Fraude por Mês'
                )
                
                st.plotly_chart(fig_month, use_container_width=True)
        
        # Análise adicional de sazonalidade
        if weekday_data is not None and not weekday_data.empty:
            max_weekday = weekday_data.loc[weekday_data['percentual_fraude'].idxmax()]
            min_weekday = weekday_data.loc[weekday_data['percentual_fraude'].idxmin()]
            
            weekday_insight = (
                f"**Padrão semanal**: {max_weekday['dia_semana']} apresenta a maior taxa média de fraude ({max_weekday['percentual_fraude']:.2f}%), "
                f"enquanto {min_weekday['dia_semana']} apresenta a menor ({min_weekday['percentual_fraude']:.2f}%). "
            )
            
            if 'month_data' in locals() and month_data is not None and not month_data.empty:
                max_month = month_data.loc[month_data['percentual_fraude'].idxmax()]
                min_month = month_data.loc[month_data['percentual_fraude'].idxmin()]
                
                month_insight = (
                    f"**Padrão mensal**: {max_month['nome_mes']} apresenta a maior taxa média de fraude ({max_month['percentual_fraude']:.2f}%), "
                    f"enquanto {min_month['nome_mes']} apresenta a menor ({min_month['percentual_fraude']:.2f}%). "
                )
                
                st.markdown(
                    create_insight_box(
                        weekday_insight + month_insight + "Estes padrões sazonais podem orientar estratégias específicas de verificação e prevenção.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    create_insight_box(
                        weekday_insight + "Este padrão semanal pode orientar estratégias específicas de verificação e prevenção.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 5: Comparação de períodos
        st.markdown("<h3>🔍 Comparação Entre Períodos</h3>", unsafe_allow_html=True)
        
        # Determinar ponto médio para dividir os dados em dois períodos
        middle_date = df_trend_filtered['date'].min() + (df_trend_filtered['date'].max() - df_trend_filtered['date'].min()) / 2
        
        # Dividir em dois períodos para comparação
        first_period = df_trend_filtered[df_trend_filtered['date'] <= middle_date]
        second_period = df_trend_filtered[df_trend_filtered['date'] > middle_date]
        
        # Verificar se temos dados suficientes em ambos os períodos
        if len(first_period) > 0 and len(second_period) > 0:
            # Calcular estatísticas para cada período
            first_avg = first_period['percentual_fraude'].mean()
            second_avg = second_period['percentual_fraude'].mean()
            
            first_max = first_period['percentual_fraude'].max()
            second_max = second_period['percentual_fraude'].max()
            
            first_min = first_period['percentual_fraude'].min()
            second_min = second_period['percentual_fraude'].min()
            
            first_orders = first_period['total_pedidos'].sum()
            second_orders = second_period['total_pedidos'].sum()
            
            # Criar tabela comparativa
            comparison_data = {
                'Métrica': ['Taxa Média de Fraude (%)', 'Taxa Máxima de Fraude (%)', 'Taxa Mínima de Fraude (%)', 'Total de Pedidos'],
                'Primeiro Período': [f"{first_avg:.2f}%", f"{first_max:.2f}%", f"{first_min:.2f}%", f"{first_orders:,}".replace(',', '.')],
                'Segundo Período': [f"{second_avg:.2f}%", f"{second_max:.2f}%", f"{second_min:.2f}%", f"{second_orders:,}".replace(',', '.')],
                'Variação': [
                    f"{(second_avg - first_avg):.2f}% ({'▲' if second_avg > first_avg else '▼' if second_avg < first_avg else '■'})",
                    f"{(second_max - first_max):.2f}% ({'▲' if second_max > first_max else '▼' if second_max < first_max else '■'})",
                    f"{(second_min - first_min):.2f}% ({'▲' if second_min > first_min else '▼' if second_min < first_min else '■'})",
                    f"{second_orders - first_orders:,} ({'▲' if second_orders > first_orders else '▼' if second_orders < first_orders else '■'})".replace(',', '.')
                ]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Aplicar estilo para destacar variações
            def highlight_variation(val):
                if isinstance(val, str) and '▲' in val:
                    return 'color: red'
                elif isinstance(val, str) and '▼' in val:
                    return 'color: green'
                return ''
            
            # Exibir tabela comparativa
            st.dataframe(
                comparison_df.style.applymap(highlight_variation, subset=['Variação']),
                use_container_width=True
            )


            
            # Adicionar análise comparativa
            variation_pct = ((second_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
            
            if abs(variation_pct) < 5:
                variation_message = (
                    f"A comparação entre os dois períodos mostra uma **variação estável** ({variation_pct:.1f}%) na taxa média de fraude. "
                    "Isso sugere que as condições permaneceram relativamente constantes ou que as medidas implementadas mantiveram a situação sob controle."
                )
                variation_icon = "info"
            elif variation_pct > 0:
                variation_message = (
                    f"A comparação entre os dois períodos mostra um **aumento significativo** ({variation_pct:.1f}%) na taxa média de fraude. "
                    "Este crescimento pode indicar a necessidade de revisar as políticas de prevenção de fraudes ou investigar mudanças operacionais recentes."
                )
                variation_icon = "warning"
            else:  # variation_pct < 0
                variation_message = (
                    f"A comparação entre os dois períodos mostra uma **redução significativa** ({abs(variation_pct):.1f}%) na taxa média de fraude. "
                    "Esta melhoria pode ser resultado de medidas preventivas implementadas recentemente ou mudanças no contexto operacional."
                )
                variation_icon = "info"
            
            st.markdown(
                create_insight_box(
                    variation_message,
                    icon_type=variation_icon
                ),
                unsafe_allow_html=True
            )
            
            # Gráfico comparativo dos dois períodos (sobrepostos)
            st.markdown("<h4>📊 Visualização Comparativa de Períodos</h4>", unsafe_allow_html=True)
            
            # Criar figura com subplots
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Transformar as datas para número de dias desde o início do período
            first_period = first_period.copy()
            second_period = second_period.copy()
            
            first_period['dias'] = (first_period['date'] - first_period['date'].min()).dt.days
            second_period['dias'] = (second_period['date'] - second_period['date'].min()).dt.days
            
            # Adicionar primeira série (primeiro período)
            fig.add_trace(
                go.Scatter(
                    x=first_period['dias'],
                    y=first_period['percentual_fraude'],
                    name="Primeiro Período",
                    line=dict(color="#1f77b4", width=2),
                    mode='lines'
                ),
                secondary_y=False
            )
            
            # Adicionar segunda série (segundo período)
            fig.add_trace(
                go.Scatter(
                    x=second_period['dias'],
                    y=second_period['percentual_fraude'],
                    name="Segundo Período",
                    line=dict(color="#ff7f0e", width=2),
                    mode='lines'
                ),
                secondary_y=False
            )
            
            # Atualizar layout
            fig.update_layout(
                title="Comparação da Taxa de Fraude por Dias desde o Início do Período",
                xaxis=dict(title="Dias desde o início do período"),
                yaxis=dict(title="Taxa de Fraude (%)"),
                legend=dict(x=0.01, y=0.99),
                font=dict(family="sans serif"),
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            
            fig.update_xaxes(
                showline=True,
                linewidth=1,
                linecolor='lightgray',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            
            fig.update_yaxes(
                showline=True,
                linewidth=1,
                linecolor='lightgray',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados insuficientes para realizar uma comparação entre períodos.")
        
        # Adicionar narrativa na barra lateral
        with st.sidebar:
            st.markdown("<h3>📈 Evolução</h3>", unsafe_allow_html=True)
            
            st.markdown("""
            ### Análise de Tendências Temporais
            
            A análise de evolução temporal permite:
            
            1. **Identificar tendências** de aumento ou diminuição de fraudes
            2. **Detectar padrões sazonais** que podem influenciar as ocorrências
            3. **Avaliar a eficácia** de medidas implementadas anteriormente
            4. **Projetar cenários futuros** baseados em dados históricos
            
            #### Como utilizar esta análise:
            
            - Observe a tendência geral para determinar se a situação está melhorando ou piorando
            - Identifique períodos sazonais críticos que requerem atenção especial
            - Compare diferentes intervalos de tempo para avaliar o impacto de mudanças operacionais
            - Utilize os padrões detectados para prever e mitigar problemas futuros
            
            > **Dica**: Ao implementar novas medidas de prevenção,
            > monitore cuidadosamente a evolução temporal para
            > avaliar sua eficácia real ao longo do tempo.
            """)
    except Exception as e:
        st.error(f"Erro ao processar a visualização: {e}")
        st.text("Detalhes do erro:")
        st.text(traceback.format_exc())