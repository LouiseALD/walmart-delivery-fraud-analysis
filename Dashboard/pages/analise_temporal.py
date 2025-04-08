import streamlit as st
import pandas as pd
import numpy as np
import traceback
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import calendar

# Importar funções utilitárias
from utils.loaders import prepare_data_for_time_analysis, prepare_fraud_trend_data
from utils.graphics import create_time_heatmap, create_time_series, create_bar_chart
from utils.filters import create_date_range_filter
from config.style_config import create_kpi_card, create_insight_box, create_tooltip

def show(data):
    """
    Exibe a análise temporal de fraudes em entregas.

    Args:
        data: Dicionário com DataFrames para análise
    """
    try:
        st.markdown("<h2 style='text-align: center;'>🕒 Análise Temporal de Fraudes</h2>", unsafe_allow_html=True)

        if not data:
            st.error("Não foi possível carregar os dados para a análise temporal.")
            return

        df_fraud_time = prepare_data_for_time_analysis(data.get('fraud_time')) if 'fraud_time' in data else None
        df_fraud_trend = prepare_fraud_trend_data(data.get('fraud_trend')) if 'fraud_trend' in data else None

        if (df_fraud_time is None or df_fraud_time.empty) and (df_fraud_trend is None or df_fraud_trend.empty):
            st.warning("Dados insuficientes para análise temporal. Verifique a conexão com o banco de dados.")
            return

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3>⏰ Filtros de Tempo</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if df_fraud_trend is not None and not df_fraud_trend.empty and 'date' in df_fraud_trend.columns:
                date_range = create_date_range_filter(df_fraud_trend, 'date', 'time_analysis')
                if date_range:
                    start_date, end_date = date_range
                    df_fraud_trend_filtered = df_fraud_trend[
                        (df_fraud_trend['date'] >= start_date) &
                        (df_fraud_trend['date'] <= end_date)
                    ]
                else:
                    df_fraud_trend_filtered = df_fraud_trend
            else:
                df_fraud_trend_filtered = df_fraud_trend

        with col2:
            if df_fraud_time is not None and not df_fraud_time.empty and 'hora' in df_fraud_time.columns:
                hour_range = st.slider(
                    "Faixa de Hora do Dia",
                    min_value=0,
                    max_value=23,
                    value=(0, 23),
                    step=1
                )
                start_hour, end_hour = hour_range
                df_fraud_time_filtered = df_fraud_time[
                    (df_fraud_time['hora'] >= start_hour) &
                    (df_fraud_time['hora'] <= end_hour)
                ]
            else:
                df_fraud_time_filtered = df_fraud_time

    
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 2: KPIs temporais
        st.markdown("<h3>🔑 Indicadores Temporais</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Hora de pico de fraudes
        with col1:
            if df_fraud_time_filtered is not None and not df_fraud_time_filtered.empty and 'hora' in df_fraud_time_filtered.columns:
                # Encontrar hora com maior percentual de fraude
                peak_hour_data = df_fraud_time_filtered.loc[df_fraud_time_filtered['percentual_fraude'].idxmax()]
                peak_hour = peak_hour_data['hora']
                peak_fraud_rate = peak_hour_data['percentual_fraude']
                
                # Formatar hora para exibição
                peak_hour_formatted = f"{int(peak_hour)}:00"
                
                st.markdown(
                    create_kpi_card(
                        "Hora de Pico de Fraudes", 
                        peak_hour_formatted, 
                        f"Taxa de fraude: {peak_fraud_rate:.2f}%",
                        color="warning"
                    ), 
                    unsafe_allow_html=True
                )
        
        # Período do dia mais crítico
        with col2:
            if df_fraud_time_filtered is not None and not df_fraud_time_filtered.empty and 'periodo_dia' in df_fraud_time_filtered.columns:
                # Agrupar por período do dia
                period_data = df_fraud_time_filtered.groupby('periodo_dia').agg({
                    'percentual_fraude': 'mean'
                }).reset_index()
                
                # Encontrar período com maior percentual de fraude
                peak_period_data = period_data.loc[period_data['percentual_fraude'].idxmax()]
                peak_period = peak_period_data['periodo_dia']
                peak_period_rate = peak_period_data['percentual_fraude']
                
                st.markdown(
                    create_kpi_card(
                        "Período Mais Crítico", 
                        peak_period, 
                        f"Taxa de fraude: {peak_period_rate:.2f}%",
                        color="warning"
                    ), 
                    unsafe_allow_html=True
                )
        
        # Dia da semana com maior fraude
        with col3:
            if df_fraud_trend_filtered is not None and not df_fraud_trend_filtered.empty and 'date' in df_fraud_trend_filtered.columns:
                # Adicionar dia da semana se não existir
                if 'dia_semana' not in df_fraud_trend_filtered.columns:
                    df_fraud_trend_filtered['dia_semana'] = df_fraud_trend_filtered['date'].dt.day_name()
                
                # Agrupar por dia da semana
                weekday_data = df_fraud_trend_filtered.groupby('dia_semana').agg({
                    'percentual_fraude': 'mean'
                }).reset_index()
                
                # Verificar se temos dados
                if not weekday_data.empty:
                    # Encontrar dia com maior percentual de fraude
                    peak_weekday_data = weekday_data.loc[weekday_data['percentual_fraude'].idxmax()]
                    peak_weekday = peak_weekday_data['dia_semana']
                    peak_weekday_rate = peak_weekday_data['percentual_fraude']
                    
                    # Traduzir dia para português se necessário
                    dias_pt = {
                        'Monday': 'Segunda',
                        'Tuesday': 'Terça',
                        'Wednesday': 'Quarta',
                        'Thursday': 'Quinta',
                        'Friday': 'Sexta',
                        'Saturday': 'Sábado',
                        'Sunday': 'Domingo'
                    }
                    
                    if peak_weekday in dias_pt:
                        peak_weekday = dias_pt[peak_weekday]
                    
                    st.markdown(
                        create_kpi_card(
                            "Dia da Semana Crítico", 
                            peak_weekday, 
                            f"Taxa de fraude: {peak_weekday_rate:.2f}%",
                            color="warning"
                        ), 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        create_kpi_card(
                            "Dia da Semana Crítico", 
                            "N/D", 
                            "Dados insuficientes",
                            color=""
                        ), 
                        unsafe_allow_html=True
                    )
        
        # Mês com maior fraude
        with col4:
            if df_fraud_trend_filtered is not None and not df_fraud_trend_filtered.empty and 'date' in df_fraud_trend_filtered.columns:
                # Adicionar mês se não existir
                # Garantir colunas 'mes' e 'nome_mes'
                if 'mes' not in df_fraud_trend_filtered.columns:
                    df_fraud_trend_filtered['mes'] = df_fraud_trend_filtered['date'].dt.month

                if 'nome_mes' not in df_fraud_trend_filtered.columns:
                    df_fraud_trend_filtered['nome_mes'] = df_fraud_trend_filtered['date'].dt.month.apply(
                        lambda x: calendar.month_name[x]
                    )


                
                # Agrupar por mês
                month_data = df_fraud_trend_filtered.groupby(['mes', 'nome_mes']).agg({
                    'percentual_fraude': 'mean'
                }).reset_index()
                
                # Verificar se temos dados
                if not month_data.empty:
                    # Encontrar mês com maior percentual de fraude
                    peak_month_data = month_data.loc[month_data['percentual_fraude'].idxmax()]
                    peak_month = peak_month_data['nome_mes']
                    peak_month_rate = peak_month_data['percentual_fraude']
                    
                    # Traduzir mês para português se necessário
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
                    
                    if peak_month in meses_pt:
                        peak_month = meses_pt[peak_month]
                    
                    st.markdown(
                        create_kpi_card(
                            "Mês Mais Crítico", 
                            peak_month, 
                            f"Taxa de fraude: {peak_month_rate:.2f}%",
                            color="warning"
                        ), 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        create_kpi_card(
                            "Mês Mais Crítico", 
                            "N/D", 
                            "Dados insuficientes",
                            color=""
                        ), 
                        unsafe_allow_html=True
                    )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 3: Heatmap de fraudes por hora/dia
        st.markdown("<h3>🔥 Heatmap de Fraudes por Hora e Dia</h3>", unsafe_allow_html=True)
        
        if df_fraud_time_filtered is not None and not df_fraud_time_filtered.empty and 'hora' in df_fraud_time_filtered.columns:
            # Preparar dados para heatmap
            if df_fraud_trend_filtered is not None and not df_fraud_trend_filtered.empty and 'date' in df_fraud_trend_filtered.columns:
                # Se temos dados detalhados, tentar criar heatmap por hora e dia da semana
                try:
                    # Adicionar dia da semana e hora se não existirem
                    if 'dia_semana' not in df_fraud_trend_filtered.columns:
                        df_fraud_trend_filtered['dia_semana'] = df_fraud_trend_filtered['date'].dt.day_name()
                    
                    if 'hora' not in df_fraud_trend_filtered.columns:
                        # Tentar criar dados sintéticos combinando as duas fontes
                        combined_data = []
                        
                        for day in df_fraud_trend_filtered['dia_semana'].unique():
                            day_fraud_rate = df_fraud_trend_filtered[df_fraud_trend_filtered['dia_semana'] == day]['percentual_fraude'].mean()
                            
                            for hour_data in df_fraud_time_filtered.itertuples():
                                # Ajustar taxa de fraude baseada no dia e hora
                                adjusted_rate = hour_data.percentual_fraude * (day_fraud_rate / df_fraud_trend_filtered['percentual_fraude'].mean())
                                
                                combined_data.append({
                                    'hora': hour_data.hora,
                                    'dia_semana': day,
                                    'percentual_fraude': adjusted_rate
                                })
                        
                        heatmap_data = pd.DataFrame(combined_data)
                    else:
                        # Usar dados existentes se hora já estiver presente
                        heatmap_data = df_fraud_trend_filtered
                    
                    # Criar heatmap
                    heatmap_fig = create_time_heatmap(
                        heatmap_data,
                        'hora',
                        'dia_semana',
                        'percentual_fraude',
                        'Taxa de Fraude por Hora e Dia da Semana'
                    )
                    
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                except Exception as e:
                    # Se não conseguir criar heatmap completo, usar só dados por hora
                    st.warning(f"Não foi possível criar o heatmap completo. Mostrando apenas dados por hora. Erro: {e}")
                    
                    heatmap_fig = create_time_heatmap(
                        df_fraud_time_filtered,
                        'hora',
                        None,
                        'percentual_fraude',
                        'Taxa de Fraude por Hora do Dia'
                    )
                    
                    st.plotly_chart(heatmap_fig, use_container_width=True)
            else:
                # Usar apenas dados por hora
                heatmap_fig = create_time_heatmap(
                    df_fraud_time_filtered,
                    'hora',
                    None,
                    'percentual_fraude',
                    'Taxa de Fraude por Hora do Dia'
                )
                
                st.plotly_chart(heatmap_fig, use_container_width=True)
            
            # Extrair insights do heatmap
            if 'periodo_dia' in df_fraud_time_filtered.columns:
                period_data = df_fraud_time_filtered.groupby('periodo_dia').agg({
                    'percentual_fraude': ['mean', 'max']
                }).reset_index()
                
                period_data.columns = ['periodo_dia', 'media_fraude', 'max_fraude']
                
                # Classificar períodos por taxa média de fraude
                period_data = period_data.sort_values('media_fraude', ascending=False)
                
                top_period = period_data.iloc[0]['periodo_dia']
                top_period_rate = period_data.iloc[0]['media_fraude']
                
                st.markdown(
                    create_insight_box(
                        f"O período de '{top_period}' apresenta a maior taxa média de fraude ({top_period_rate:.2f}%). "
                        "Recomenda-se reforçar os procedimentos de verificação das entregas neste período.",
                        icon_type="warning"
                    ),
                    unsafe_allow_html=True
                )
        else:
            st.warning("Dados insuficientes para gerar o heatmap de fraudes por hora.")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 4: Análise de sazonalidade
        st.markdown("<h3>📅 Análise de Sazonalidade</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # Análise por dia da semana
        with col1:
            if df_fraud_trend_filtered is not None and not df_fraud_trend_filtered.empty and 'date' in df_fraud_trend_filtered.columns:
                # Adicionar dia da semana se não existir
                if 'dia_semana' not in df_fraud_trend_filtered.columns:
                    df_fraud_trend_filtered['dia_semana'] = df_fraud_trend_filtered['date'].dt.day_name()
                
                # Agrupar por dia da semana
                weekday_data = df_fraud_trend_filtered.groupby('dia_semana').agg({
                    'percentual_fraude': 'mean',
                    'total_pedidos': 'sum',
                    'itens_faltantes': 'sum'
                }).reset_index()
                
                # Ordenar os dias da semana corretamente
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
                weekday_fig = create_bar_chart(
                    weekday_data,
                    'dia_semana',
                    'percentual_fraude',
                    'Taxa de Fraude por Dia da Semana',
                    height=350
                )
                
                st.plotly_chart(weekday_fig, use_container_width=True)
                
                # Identificar dias mais críticos
                top_weekday = weekday_data.sort_values('percentual_fraude', ascending=False).iloc[0]['dia_semana']
                top_weekday_rate = weekday_data.sort_values('percentual_fraude', ascending=False).iloc[0]['percentual_fraude']
                
                st.markdown(
                    create_insight_box(
                        f"O dia '{top_weekday}' apresenta a maior taxa de fraude ({top_weekday_rate:.2f}%). "
                        "Considere implementar verificações adicionais neste dia da semana.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.warning("Dados insuficientes para análise por dia da semana.")
        
        # Análise por mês
        with col2:
            if df_fraud_trend_filtered is not None and not df_fraud_trend_filtered.empty and 'date' in df_fraud_trend_filtered.columns:
                # Adicionar mês se não existir
                if 'mes' not in df_fraud_trend_filtered.columns:
                    df_fraud_trend_filtered['mes'] = df_fraud_trend_filtered['date'].dt.month
                    df_fraud_trend_filtered['nome_mes'] = df_fraud_trend_filtered['date'].dt.month.apply(
                        lambda x: calendar.month_name[x]
                    )
                
                # Agrupar por mês
                month_data = df_fraud_trend_filtered.groupby(['mes', 'nome_mes']).agg({
                    'percentual_fraude': 'mean',
                    'total_pedidos': 'sum',
                    'itens_faltantes': 'sum'
                }).reset_index().sort_values('mes')
                
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
                month_fig = create_bar_chart(
                    month_data,
                    'nome_mes',
                    'percentual_fraude',
                    'Taxa de Fraude por Mês',
                    height=350
                )
                
                st.plotly_chart(month_fig, use_container_width=True)
                
                # Identificar meses mais críticos
                top_month = month_data.sort_values('percentual_fraude', ascending=False).iloc[0]['nome_mes']
                top_month_rate = month_data.sort_values('percentual_fraude', ascending=False).iloc[0]['percentual_fraude']
                
                st.markdown(
                    create_insight_box(
                        f"O mês de '{top_month}' apresenta a maior taxa de fraude ({top_month_rate:.2f}%). "
                        "Planeje reforços operacionais neste período do ano para o próximo ciclo.",
                        icon_type="info"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.warning("Dados insuficientes para análise por mês.")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Seção 5: Tendência e Evolução Temporal
        st.markdown("<h3>📈 Evolução Temporal das Fraudes</h3>", unsafe_allow_html=True)
        
        if df_fraud_trend_filtered is not None and not df_fraud_trend_filtered.empty and 'date' in df_fraud_trend_filtered.columns:
            # Criar média móvel se não existir
            if 'media_movel_7d' not in df_fraud_trend_filtered.columns:
                df_fraud_trend_filtered['media_movel_7d'] = df_fraud_trend_filtered['percentual_fraude'].rolling(window=7, min_periods=1).mean()
            
            # Criar gráfico de série temporal
            ts_fig = create_time_series(
                df_fraud_trend_filtered,
                'date',
                'percentual_fraude',
                'Evolução da Taxa de Fraude ao Longo do Tempo',
                add_trendline=True,
                secondary_y_column='total_pedidos'
            )
            
            st.plotly_chart(ts_fig, use_container_width=True)
            
            # Calcular tendência recente
            recent_data = df_fraud_trend_filtered.sort_values('date').tail(30)
            
            if len(recent_data) > 5:
                start_rate = recent_data.iloc[0]['percentual_fraude']
                end_rate = recent_data.iloc[-1]['percentual_fraude']
                trend_pct = ((end_rate - start_rate) / start_rate) * 100 if start_rate > 0 else 0
                
                if trend_pct > 5:
                    trend_message = f"Alerta: A taxa de fraude aumentou {trend_pct:.1f}% nos últimos {len(recent_data)} dias. "
                    trend_icon = "warning"
                elif trend_pct < -5:
                    trend_message = f"A taxa de fraude diminuiu {abs(trend_pct):.1f}% nos últimos {len(recent_data)} dias. "
                    trend_icon = "info"
                else:
                    trend_message = f"A taxa de fraude manteve-se estável (variação de {trend_pct:.1f}%) nos últimos {len(recent_data)} dias. "
                    trend_icon = "info"
                
                st.markdown(
                    create_insight_box(
                        trend_message + "Este indicador de tendência é crucial para avaliar a eficácia das medidas anti-fraude implementadas.",
                        icon_type=trend_icon
                    ),
                    unsafe_allow_html=True
                )
        else:
            st.warning("Dados insuficientes para análise de tendência temporal.")
        
        # Adicionar narrativa na barra lateral
        with st.sidebar:
            st.markdown("<h3>📊 Interpretação Temporal</h3>", unsafe_allow_html=True)
            
            st.markdown("""
            ### Análise de Padrões Temporais
            
            A análise temporal de fraudes é fundamental para:
            
            1. **Identificar padrões recorrentes** em horários e dias específicos
            2. **Detectar sazonalidades** que podem estar relacionadas a fatores externos
            3. **Avaliar a eficácia** das medidas de segurança implementadas
            4. **Otimizar recursos** de verificação e auditoria
            
            #### Como interpretar:
            
            - **Heatmap**: As áreas mais escuras indicam concentração de fraudes
            - **Gráficos de barras**: Mostram variações por período
            - **Linhas de tendência**: Revelam o comportamento ao longo do tempo
            
            > **Dica**: Combine a análise temporal com o perfil de motoristas
            > e produtos para identificar correlações significativas.
            """)

    except Exception as e:
        st.error(f"Erro ao processar a visualização: {e}")
        st.text("Detalhes do erro:")
        st.text(traceback.format_exc())
