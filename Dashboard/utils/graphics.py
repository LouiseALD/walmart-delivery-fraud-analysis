import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from config.style_config import THEME, create_tooltip

def create_time_heatmap(df, time_column='hora', day_column='dia_semana', value_column='percentual_fraude', 
                       title='Heatmap de Fraudes por Hora/Dia'):
    """
    Cria um heatmap de valores ao longo do tempo.
    
    Args:
        df: DataFrame com dados
        time_column: Coluna com horários
        day_column: Coluna com dias da semana
        value_column: Coluna com valores para o heatmap
        title: Título do gráfico
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in [time_column, value_column]):
        # Criar um heatmap vazio se não tivermos dados
        blank_df = pd.DataFrame({
            time_column: range(24),
            value_column: [0] * 24
        })
        fig = px.density_heatmap(
            blank_df, 
            x=time_column, 
            y=None, 
            z=value_column,
            title="Não há dados disponíveis para o heatmap"
        )
        return fig
    
    # Se não temos coluna de dia, usamos só a coluna de hora
    if day_column not in df.columns:
        pivot_data = df.copy()
    else:
        # Criar pivot table para heatmap
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Tradução para dias em português
        dias_pt = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        
        # Verificar se os dias estão em inglês ou português
        sample_day = df[day_column].iloc[0] if not df.empty else ''
        
        if sample_day in dias_pt.keys():
            # Traduzir dias para português para exibição
            df[day_column] = df[day_column].map(dias_pt)
            days_order = [dias_pt[day] for day in days_order]
        
        # Pivot dos dados
        pivot_data = df.pivot_table(
            values=value_column, 
            index=day_column, 
            columns=time_column, 
            aggfunc='mean'
        ).reindex(days_order)
    
    # Plotar heatmap com Plotly
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    if day_column not in df.columns:
        fig = px.density_heatmap(
            df, 
            x=time_column, 
            y=None, 
            z=value_column,
            title=title,
            color_continuous_scale='Viridis'
        )
    else:
        # Preparar dados para plotly
        heatmap_df = pivot_data.reset_index().melt(
            id_vars=day_column, 
            var_name=time_column, 
            value_name=value_column
        )
        
        fig = px.density_heatmap(
            heatmap_df, 
            x=time_column, 
            y=day_column, 
            z=value_column,
            title=title,
            color_continuous_scale='Viridis'
        )
    
    # Customizar layout
    fig.update_layout(
        font=dict(family="sans serif"),
        margin=dict(l=40, r=40, t=40, b=40),
        title_font_size=16,
        title_x=0.5,
        coloraxis_colorbar=dict(
            title=value_column.replace('_', ' ').title(),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_bar_chart(df, x_column, y_column, title, color_column=None, 
                   orientation='v', height=400, text_auto=True):
    """
    Cria um gráfico de barras.
    
    Args:
        df: DataFrame com dados
        x_column: Coluna para eixo X
        y_column: Coluna para eixo Y
        title: Título do gráfico
        color_column: Coluna para coloração (opcional)
        orientation: Orientação das barras ('v' para vertical, 'h' para horizontal)
        height: Altura do gráfico
        text_auto: Mostrar valores nas barras
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in [x_column, y_column]):
        # Retornar gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=height
        )
        return fig
    
    # Determinar orientação
    if orientation == 'h':
        fig = px.bar(
            df, 
            y=x_column, 
            x=y_column, 
            title=title,
            color=color_column,
            orientation='h',
            text_auto=text_auto,
            height=height
        )
    else:
        fig = px.bar(
            df, 
            x=x_column, 
            y=y_column, 
            title=title,
            color=color_column,
            text_auto=text_auto,
            height=height
        )
    
    # Customizar layout
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    fig.update_layout(
        font=dict(family="sans serif"),
        margin=dict(l=40, r=40, t=40, b=40),
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_traces(
        marker_line_width=0,
        hovertemplate='%{y}<br>%{x}<extra></extra>' if orientation == 'v' else '%{x}<br>%{y}<extra></extra>'
    )
    
    # Ajuste para gráficos horizontais
    if orientation == 'h':
        fig.update_yaxes(categoryorder='total ascending')
    
    return fig

def create_time_series(df, x_column, y_column, title, add_trendline=True, height=400, 
                     secondary_y_column=None, colors=None):
    """
    Cria um gráfico de série temporal.
    
    Args:
        df: DataFrame com dados
        x_column: Coluna para eixo X (temporal)
        y_column: Coluna para eixo Y
        title: Título do gráfico
        add_trendline: Adicionar linha de tendência
        height: Altura do gráfico
        secondary_y_column: Coluna para eixo Y secundário (opcional)
        colors: Lista de cores para as linhas (opcional)
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in [x_column, y_column]):
        # Retornar gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=height
        )
        return fig
    
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    if colors is None:
        colors = THEME[theme_mode]['chart_colors']
    
    # Criar figura base
    if secondary_y_column is not None and secondary_y_column in df.columns:
        # Criar figura com eixo Y duplo
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Adicionar primeira série no eixo Y primário
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[y_column],
                name=y_column.replace('_', ' ').title(),
                line=dict(color=colors[0], width=2),
                mode='lines+markers',
                marker=dict(size=6)
            ),
            secondary_y=False
        )
        
        # Adicionar segunda série no eixo Y secundário
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[secondary_y_column],
                name=secondary_y_column.replace('_', ' ').title(),
                line=dict(color=colors[1], width=2),
                mode='lines+markers',
                marker=dict(size=6)
            ),
            secondary_y=True
        )
        
        # Adicionar títulos dos eixos
        fig.update_yaxes(title_text=y_column.replace('_', ' ').title(), secondary_y=False)
        fig.update_yaxes(title_text=secondary_y_column.replace('_', ' ').title(), secondary_y=True)
    else:
        # Criar figura com eixo Y único
        fig = go.Figure()
        
        # Adicionar série principal
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[y_column],
                name=y_column.replace('_', ' ').title(),
                line=dict(color=colors[0], width=2),
                mode='lines+markers',
                marker=dict(size=6)
            )
        )
    
    # Adicionar linha de tendência se solicitado
    if add_trendline:
        # Converter para valores numéricos para a linha de tendência
        x_numeric = pd.to_numeric(pd.Series(range(len(df))))
        y_numeric = pd.to_numeric(df[y_column])
        
        # Calcular linha de tendência (regressão linear)
        try:
            import numpy as np
            z = np.polyfit(x_numeric, y_numeric, 1)
            p = np.poly1d(z)
            trend_y = p(x_numeric)
            
            fig.add_trace(
                go.Scatter(
                    x=df[x_column],
                    y=trend_y,
                    name='Tendência',
                    line=dict(color='rgba(255, 165, 0, 0.7)', width=2, dash='dot'),
                    mode='lines'
                )
            )
        except Exception as e:
            st.warning(f"Não foi possível criar a linha de tendência: {e}")
    
    # Atualizar layout
    fig.update_layout(
        title=title,
        xaxis_title=x_column.replace('_', ' ').title(),
        yaxis_title=y_column.replace('_', ' ').title(),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(family="sans serif"),
        height=height,
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    # Adicionar grid e linhas de eixo
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
    
    return fig

def create_pie_chart(df, label_column, value_column, title, hole=0, height=400):
    """
    Cria um gráfico de pizza ou donut.
    
    Args:
        df: DataFrame com dados
        label_column: Coluna para rótulos
        value_column: Coluna para valores
        title: Título do gráfico
        hole: Tamanho do buraco (0 para pizza, >0 para donut)
        height: Altura do gráfico
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in [label_column, value_column]):
        # Retornar gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=height
        )
        return fig
    
    # Criar gráfico de pizza
    fig = px.pie(
        df,
        names=label_column,
        values=value_column,
        title=title,
        hole=hole
    )
    
    # Customizar layout
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    fig.update_layout(
        font=dict(family="sans serif"),
        height=height,
        margin=dict(l=40, r=40, t=40, b=40),
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Atualizar traços
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        marker=dict(line=dict(color='#FFFFFF', width=1))
    )
    
    return fig

def create_gauge_chart(value, title, min_value=0, max_value=100, threshold_values=None, threshold_colors=None, height=300):
    """
    Cria um gráfico de medidor.
    
    Args:
        value: Valor a ser exibido no medidor
        title: Título do gráfico
        min_value: Valor mínimo da escala
        max_value: Valor máximo da escala
        threshold_values: Lista de valores limite para cores diferentes
        threshold_colors: Lista de cores para cada faixa
        height: Altura do gráfico
        
    Returns:
        Objeto de figura do Plotly
    """
    if threshold_values is None:
        threshold_values = [33, 66]
    
    if threshold_colors is None:
        threshold_colors = ['red', 'yellow', 'green']
    
    # Garantir que o valor esteja dentro dos limites
    value = max(min_value, min(value, max_value))
    
    # Definir faixas para cores
    steps = []
    for i in range(len(threshold_values) + 1):
        if i == 0:
            range_min = min_value
            range_max = threshold_values[0]
        elif i == len(threshold_values):
            range_min = threshold_values[-1]
            range_max = max_value
        else:
            range_min = threshold_values[i-1]
            range_max = threshold_values[i]
        
        steps.append(
            dict(
                range=[range_min, range_max],
                color=threshold_colors[i],
                thickness=0.75
            )
        )
    
    # Criar gráfico de medidor
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [min_value, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': steps,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    # Customizar layout
    fig.update_layout(
        font=dict(family="sans serif"),
        height=height,
        margin=dict(l=40, r=40, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_scatter_plot(df, x_column, y_column, title, color_column=None, size_column=None, text_column=None, height=400):
    """
    Cria um gráfico de dispersão.
    
    Args:
        df: DataFrame com dados
        x_column: Coluna para eixo X
        y_column: Coluna para eixo Y
        title: Título do gráfico
        color_column: Coluna para coloração (opcional)
        size_column: Coluna para tamanho dos pontos (opcional)
        text_column: Coluna para texto ao passar o mouse (opcional)
        height: Altura do gráfico
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in [x_column, y_column]):
        # Retornar gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=height
        )
        return fig
    
    # Configurar parâmetros do gráfico
    scatter_params = {
        'x': x_column,
        'y': y_column,
        'title': title,
        'height': height
    }
    
    if color_column is not None and color_column in df.columns:
        scatter_params['color'] = color_column
    
    if size_column is not None and size_column in df.columns:
        scatter_params['size'] = size_column
    
    if text_column is not None and text_column in df.columns:
        scatter_params['hover_name'] = text_column
    
    # Criar gráfico de dispersão
    fig = px.scatter(df, **scatter_params)
    
    # Customizar layout
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    fig.update_layout(
        font=dict(family="sans serif"),
        margin=dict(l=40, r=40, t=40, b=40),
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    # Adicionar linha de tendência
    fig.update_traces(
        marker=dict(
            size=10 if size_column is None else None,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        selector=dict(mode='markers')
    )
    
    # Adicionar grid e linhas de eixo
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor='lightgray',
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        title=x_column.replace('_', ' ').title()
    )
    
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor='lightgray',
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        title=y_column.replace('_', ' ').title()
    )
    
    return fig

def create_treemap(df, path, values, title, color_column=None, height=500):
    """
    Cria um gráfico de treemap.
    
    Args:
        df: DataFrame com dados
        path: Lista de colunas para hierarquia
        values: Coluna para valores
        title: Título do gráfico
        color_column: Coluna para coloração (opcional)
        height: Altura do gráfico
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in path) or values not in df.columns:
        # Retornar gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=height
        )
        return fig
    
    # Configurar parâmetros do gráfico
    treemap_params = {
        'path': path,
        'values': values,
        'title': title,
        'height': height
    }
    
    if color_column is not None and color_column in df.columns:
        treemap_params['color'] = color_column
    
    # Criar gráfico de treemap
    fig = px.treemap(df, **treemap_params)
    
    # Customizar layout
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    fig.update_layout(
        font=dict(family="sans serif"),
        margin=dict(l=40, r=40, t=40, b=40),
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Atualizar traços
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>%{value}<extra></extra>',
        textinfo='label+value'
    )
    
    return fig

def create_correlation_matrix(df, title='Matriz de Correlação', height=600):
    """
    Cria uma matriz de correlação.
    
    Args:
        df: DataFrame com dados numéricos
        title: Título do gráfico
        height: Altura do gráfico
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or df.shape[1] < 2:
        # Retornar gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=height
        )
        return fig
    
    # Calcular matriz de correlação
    corr_matrix = df.corr()
    
    # Criar heatmap de correlação
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        title=title
    )
    
    # Customizar layout
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    fig.update_layout(
        font=dict(family="sans serif"),
        height=height,
        margin=dict(l=40, r=40, t=40, b=40),
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    # Atualizar traços
    fig.update_traces(
        text=corr_matrix.round(2),
        texttemplate='%{text:.2f}'
    )
    
    # Ajustar tamanho da colorbar
    fig.update_layout(
        coloraxis_colorbar=dict(
            title='Correlação',
            thicknessmode="pixels", thickness=20,
            lenmode="pixels", len=height * 0.6,
            yanchor="top", y=1,
            ticks="outside"
        )
    )
    
    return fig

def create_map(df, lat_column, lon_column, color_col=None, size_col=None, hover_name=None, hover_data=None, title='Mapa'):
    """
    Cria um mapa com pontos georreferenciados.
    
    Args:
        df: DataFrame com dados
        lat_column: Coluna com latitude
        lon_column: Coluna com longitude
        color_col: Coluna para coloração (opcional)
        size_col: Coluna para tamanho dos pontos (opcional)
        hover_name: Coluna para nome no hover (opcional)
        hover_data: Lista de colunas para dados adicionais no hover (opcional)
        title: Título do mapa
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in [lat_column, lon_column]):
        # Retornar mapa vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=600
        )
        return fig
    
    # Configurar parâmetros do mapa
    map_params = {
        'lat': lat_column,
        'lon': lon_column,
        'title': title,
        'zoom': 3,
        'height': 600
    }
    
    if color_col is not None and color_col in df.columns:
        map_params['color'] = color_col
    
    if size_col is not None and size_col in df.columns:
        map_params['size'] = size_col
    
    if hover_name is not None and hover_name in df.columns:
        map_params['hover_name'] = hover_name
    
    if hover_data is not None:
        # Filtrar apenas colunas existentes
        hover_data = [col for col in hover_data if col in df.columns]
        if hover_data:
            map_params['hover_data'] = hover_data
    
    # Criar mapa
    fig = px.scatter_mapbox(df, **map_params)
    
    # Definir estilo do mapa
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": df[lat_column].mean(), "lon": df[lon_column].mean()},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_sankey_diagram(df, source_col, target_col, value_col, title='Diagrama de Sankey'):
    """
    Cria um diagrama de Sankey.
    
    Args:
        df: DataFrame com dados
        source_col: Coluna de origem
        target_col: Coluna de destino
        value_col: Coluna com valores
        title: Título do diagrama
        
    Returns:
        Objeto de figura do Plotly
    """
    if df is None or df.empty or not all(col in df.columns for col in [source_col, target_col, value_col]):
        # Retornar diagrama vazio
        fig = go.Figure()
        fig.update_layout(
            title=title + " (Sem dados disponíveis)",
            height=600
        )
        return fig
    
    # Preparar dados para o diagrama de Sankey
    sources = df[source_col].tolist()
    targets = df[target_col].tolist()
    values = df[value_col].tolist()
    
    # Criar lista única de nós
    all_nodes = sorted(list(set(sources + targets)))
    
    # Mapear nós para índices
    node_dict = {node: i for i, node in enumerate(all_nodes)}
    
    # Converter nomes para índices
    source_indices = [node_dict[source] for source in sources]
    target_indices = [node_dict[target] for target in targets]
    
    # Criar diagrama de Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="gray", width=0.5),
            label=all_nodes,
            color="blue"
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            hovertemplate='%{source.label} → %{target.label}: %{value}<extra></extra>'
        )
    )])
    
    # Customizar layout
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    fig.update_layout(
        title=title,
        font=dict(family="sans serif", size=12),
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig