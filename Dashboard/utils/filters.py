import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def apply_global_filters(data, date_filter=None, category_filter=None, region_filter=None):
    """
    Aplica filtros globais a todos os DataFrames relevantes.
    
    Args:
        data: Dicionário com todos os DataFrames
        date_filter: Tupla (data_inicio, data_fim) para filtro
        category_filter: Categoria selecionada para filtro
        region_filter: Região selecionada para filtro
        
    Returns:
        Dicionário com DataFrames filtrados
    """
    if data is None:
        return None
    
    filtered_data = {}
    
    # Aplicar filtro de data ao conjunto de tendências
    if 'fraud_trend' in data and data['fraud_trend'] is not None and date_filter is not None:
        from utils.loaders import apply_date_filter
        filtered_data['fraud_trend'] = apply_date_filter(data['fraud_trend'], date_filter)
    else:
        filtered_data['fraud_trend'] = data.get('fraud_trend')
    
    # Aplicar filtro de categoria aos produtos
    if 'missing_products' in data and data['missing_products'] is not None and category_filter is not None:
        from utils.loaders import apply_category_filter
        filtered_data['missing_products'] = apply_category_filter(
            data['missing_products'], 
            category_filter
        )
    else:
        filtered_data['missing_products'] = data.get('missing_products')
    
    # Aplicar filtro de região
    if 'fraud_region' in data and data['fraud_region'] is not None and region_filter is not None:
        from utils.loaders import apply_region_filter
        filtered_data['fraud_region'] = apply_region_filter(
            data['fraud_region'], 
            region_filter
        )
    else:
        filtered_data['fraud_region'] = data.get('fraud_region')
    
    # Copiar outros dataframes sem alteração
    for key in ['drivers', 'fraud_time', 'suspicious_drivers', 'suspicious_customers']:
        filtered_data[key] = data.get(key)
    
    return filtered_data

def filter_suspicious_entries(df, threshold=0.1, column='percentual_fraude'):
    """
    Filtra entradas suspeitas com base em um limiar.
    
    Args:
        df: DataFrame para filtrar
        threshold: Valor de corte para considerar suspeito
        column: Coluna para aplicar o filtro
        
    Returns:
        DataFrame filtrado com apenas entradas suspeitas
    """
    if df is None or df.empty or column not in df.columns:
        return df
    
    return df[df[column] > threshold]

def cluster_data(df, columns, n_clusters=3):
    """
    Aplica clusterização nos dados para identificar padrões.
    
    Args:
        df: DataFrame a ser clusterizado
        columns: Lista de colunas para usar na clusterização
        n_clusters: Número de clusters a serem criados
        
    Returns:
        DataFrame com informação de cluster adicionada
    """
    if df is None or df.empty or not all(col in df.columns for col in columns):
        return df
    
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # Preparar os dados para clustering
        features = df[columns].copy()
        
        # Lidar com valores ausentes
        features = features.fillna(features.mean())
        
        # Normalizar os dados
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Aplicar K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = kmeans.fit_predict(scaled_features)
        
        return df_with_clusters
    except Exception as e:
        st.warning(f"Erro ao realizar clusterização: {e}")
        return df

def create_date_range_filter(df, date_column='date', key_suffix=''):
    """
    Cria um widget de seleção de intervalo de datas.
    
    Args:
        df: DataFrame com dados de data
        date_column: Nome da coluna de data
        key_suffix: Sufixo para adicionar às chaves dos widgets
        
    Returns:
        Tupla (data_inicio, data_fim) selecionada
    """
    if df is None or df.empty or date_column not in df.columns:
        return None
    
    # Garantir que a coluna de data é datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Determinar min e max datas
    min_date = df[date_column].min().date()
    max_date = df[date_column].max().date()
    
    # Criar slider de data
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(f"Data inicial", 
                                  value=min_date,
                                  min_value=min_date,
                                  max_value=max_date,
                                  key=f"start_date_{key_suffix}")
    with col2:
        end_date = st.date_input(f"Data final", 
                                value=max_date,
                                min_value=min_date,
                                max_value=max_date,
                                key=f"end_date_{key_suffix}")
    
    return (pd.Timestamp(start_date), pd.Timestamp(end_date))

def create_category_filter(df, category_column='category', key_suffix=''):
    """
    Cria um widget de seleção de categoria.
    
    Args:
        df: DataFrame com dados de categoria
        category_column: Nome da coluna de categoria
        key_suffix: Sufixo para adicionar à chave do widget
        
    Returns:
        Categoria selecionada
    """
    if df is None or df.empty or category_column not in df.columns:
        return "Todas"
    
    categories = ["Todas"] + sorted(df[category_column].unique().tolist())
    selected_category = st.selectbox(
        "Selecione a categoria", 
        categories, 
        key=f"category_filter_{key_suffix}"
    )
    
    return selected_category

def create_region_filter(df, region_column='region', key_suffix=''):
    """
    Cria um widget de seleção de região.
    
    Args:
        df: DataFrame com dados de região
        region_column: Nome da coluna de região
        key_suffix: Sufixo para adicionar à chave do widget
        
    Returns:
        Região selecionada
    """
    if df is None or df.empty or region_column not in df.columns:
        return "Todas"
    
    regions = ["Todas"] + sorted(df[region_column].unique().tolist())
    selected_region = st.selectbox(
        "Selecione a região", 
        regions, 
        key=f"region_filter_{key_suffix}"
    )
    
    return selected_region

def create_numeric_filter(df, column, label, min_value=None, max_value=None, key_suffix=''):
    """
    Cria um slider para filtrar valores numéricos.
    
    Args:
        df: DataFrame com dados numéricos
        column: Nome da coluna numérica
        label: Rótulo para o slider
        min_value: Valor mínimo opcional
        max_value: Valor máximo opcional
        key_suffix: Sufixo para adicionar à chave do widget
        
    Returns:
        Tupla (valor_min, valor_max) selecionada
    """
    if df is None or df.empty or column not in df.columns:
        return (None, None)
    
    col_min = df[column].min() if min_value is None else min_value
    col_max = df[column].max() if max_value is None else max_value
    
    values = st.slider(
        label,
        min_value=float(col_min),
        max_value=float(col_max),
        value=(float(col_min), float(col_max)),
        key=f"numeric_filter_{column}_{key_suffix}"
    )
    
    return values