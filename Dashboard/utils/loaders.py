import pandas as pd
import streamlit as st
import numpy as np
import sqlite3
from datetime import datetime, timedelta

@st.cache_data
def prepare_data_for_time_analysis(df_fraud_time):
    """
    Prepara os dados de fraude por horário para análise.
    
    Args:
        df_fraud_time: DataFrame com dados de fraude por horário
        
    Returns:
        DataFrame processado para análise temporal
    """
    # Garantir que temos as colunas necessárias
    if 'hora' not in df_fraud_time.columns:
        return df_fraud_time
    
    # Adicionar período do dia se não existir
    if 'periodo_dia' not in df_fraud_time.columns:
        df_fraud_time['periodo_dia'] = df_fraud_time['hora'].apply(lambda x: 
            'Madrugada' if 0 <= x < 6 else 
            'Manhã' if 6 <= x < 12 else 
            'Tarde' if 12 <= x < 18 else 'Noite')
    
    # Calcular porcentagem de fraude
    if 'percentual_fraude' not in df_fraud_time.columns:
        if all(col in df_fraud_time.columns for col in ['pedidos_com_fraude', 'total_pedidos']):
            df_fraud_time['percentual_fraude'] = (df_fraud_time['pedidos_com_fraude'] / 
                                                df_fraud_time['total_pedidos'] * 100).round(2)
    
    return df_fraud_time

def get_id_column(df):
    """
    Busca por uma coluna de ID válida no DataFrame.
    
    Args:
        df: DataFrame para buscar a coluna de ID
        
    Returns:
        Nome da coluna de ID encontrada ou None
    """
    possible_id_columns = ['id', 'order_id', 'driver_id', 'customer_id', 'product_id', 'ID']
    
    for col in possible_id_columns:
        if col in df.columns:
            return col
    
    # Se não encontrar nenhuma coluna de ID específica, usar a primeira coluna
    if len(df.columns) > 0:
        return df.columns[0]
    
    return None

@st.cache_data
def prepare_fraud_trend_data(df_fraud_trend):
    """
    Prepara os dados de tendência de fraude para análise.
    
    Args:
        df_fraud_trend: DataFrame com dados de tendência de fraude
        
    Returns:
        DataFrame processado para análise de tendência
    """
    if df_fraud_trend is None or df_fraud_trend.empty:
        return pd.DataFrame()
    
    # Converter coluna de data para datetime se necessário
    if 'date' in df_fraud_trend.columns and not pd.api.types.is_datetime64_any_dtype(df_fraud_trend['date']):
        df_fraud_trend['date'] = pd.to_datetime(df_fraud_trend['date'])
    
    # Criar colunas adicionais para análise
    if 'date' in df_fraud_trend.columns:
        df_fraud_trend['mes'] = df_fraud_trend['date'].dt.month
        df_fraud_trend['dia_semana'] = df_fraud_trend['date'].dt.day_name()
        df_fraud_trend['semana_ano'] = df_fraud_trend['date'].dt.isocalendar().week
    
    # Calcular média móvel para suavizar tendência
    if 'percentual_fraude' in df_fraud_trend.columns:
        df_fraud_trend['media_movel_7d'] = df_fraud_trend['percentual_fraude'].rolling(window=7, min_periods=1).mean()
    
    return df_fraud_trend

@st.cache_data
def prepare_region_data(df_fraud_region):
    """
    Prepara os dados de fraude por região para análise.
    
    Args:
        df_fraud_region: DataFrame com dados de fraude por região
        
    Returns:
        DataFrame processado para análise regional
    """
    if df_fraud_region is None or df_fraud_region.empty:
        return pd.DataFrame()

    # Calcular métricas adicionais se necessário
    if 'itens_por_pedido' not in df_fraud_region.columns and 'total_pedidos' in df_fraud_region.columns and 'total_itens_faltantes' in df_fraud_region.columns:
        df_fraud_region['itens_por_pedido'] = (df_fraud_region['total_itens_faltantes'] / 
                                               df_fraud_region['total_pedidos']).round(2)
    
    # Calcular score de risco
    if 'risk_score' not in df_fraud_region.columns and 'percentual_fraude' in df_fraud_region.columns and 'media_itens_faltantes' in df_fraud_region.columns:
        # Normalizar métricas para score
        max_percent = df_fraud_region['percentual_fraude'].max()
        max_items = df_fraud_region['media_itens_faltantes'].max()
        
        df_fraud_region['risk_score'] = (
            0.7 * (df_fraud_region['percentual_fraude'] / max_percent if max_percent > 0 else 0) + 
            0.3 * (df_fraud_region['media_itens_faltantes'] / max_items if max_items > 0 else 0)
        ).round(2)
    
    return df_fraud_region

@st.cache_data
def prepare_driver_data(df_drivers, df_suspicious_drivers):
    """
    Prepara os dados de motoristas para análise.
    
    Args:
        df_drivers: DataFrame com dados de todos os motoristas
        df_suspicious_drivers: DataFrame com dados de motoristas suspeitos
        
    Returns:
        DataFrame processado para análise de motoristas
    """
    if df_drivers is None or df_drivers.empty:
        return df_suspicious_drivers
    
    if df_suspicious_drivers is None or df_suspicious_drivers.empty:
        return df_drivers
    
    # Mesclar dados de todos os motoristas com os suspeitos
    # Primeiro, garantir que os IDs são do mesmo tipo
    df_drivers['driver_id'] = df_drivers['driver_id'].astype(str)
    df_suspicious_drivers['driver_id'] = df_suspicious_drivers['driver_id'].astype(str)
    
    # Marcar motoristas suspeitos
    df_drivers['suspeito'] = df_drivers['driver_id'].isin(df_suspicious_drivers['driver_id'])
    
    # Adicionar informações adicionais dos motoristas suspeitos se disponíveis
    if 'percentual_fraude' in df_suspicious_drivers.columns:
        # Mesclar com base no driver_id
        df_merged = pd.merge(
            df_drivers, 
            df_suspicious_drivers[['driver_id', 'percentual_fraude']], 
            on='driver_id', 
            how='left'
        )
        df_merged['percentual_fraude'] = df_merged['percentual_fraude'].fillna(0)
        return df_merged
    
    return df_drivers

@st.cache_data
def prepare_product_data(df_missing_products):
    """
    Prepara os dados de produtos não entregues para análise.
    
    Args:
        df_missing_products: DataFrame com dados de produtos não entregues
        
    Returns:
        DataFrame processado para análise de produtos
    """
    if df_missing_products is None or df_missing_products.empty:
        return pd.DataFrame(), None
    
    # Calcular valor total perdido por produto
    if 'price' in df_missing_products.columns and 'total_relatos' in df_missing_products.columns:
        df_missing_products['valor_total_perdido'] = (df_missing_products['price'] * 
                                                     df_missing_products['total_relatos']).round(2)
    
    # Agrupar por categoria
    category_summary = None
    if 'category' in df_missing_products.columns:
        category_summary = df_missing_products.groupby('category').agg({
            'total_relatos': 'sum',
            'product_id': 'count'
        }).reset_index()
        
        if 'price' in df_missing_products.columns:
            category_price = df_missing_products.groupby('category')['price'].mean().reset_index()
            category_summary = pd.merge(category_summary, category_price, on='category')
        
        if 'valor_total_perdido' in df_missing_products.columns:
            category_total = df_missing_products.groupby('category')['valor_total_perdido'].sum().reset_index()
            category_summary = pd.merge(category_summary, category_total, on='category')
        
        # Renomear colunas
        rename_cols = {
            'product_id': 'qtd_produtos',
            'price': 'preco_medio'
        }
        category_summary = category_summary.rename(columns={col: rename_cols[col] for col in rename_cols.keys() if col in category_summary.columns})
        
        # Adicionar aos dados originais
        df_missing_products = df_missing_products.copy()
        df_missing_products['categoria_total_relatos'] = df_missing_products['category'].map(
            category_summary.set_index('category')['total_relatos']
        )
    
    return df_missing_products, category_summary

def load_data_from_db():
    """
    Carrega os dados do banco de dados SQLite
    
    Returns:
        Dicionário contendo todos os DataFrames necessários para a aplicação
    """
    try:
        # Conectar ao banco de dados no caminho específico
        db_path = r'C:\Users\louis\datatech\Database\walmart_fraudes.db'
        conn = sqlite3.connect(db_path)
        
        # Definir mapeamento baseado nas tabelas reais do banco
        # Tabelas encontradas: orders, drivers, customers, missing_items, products
        
        # Carregar tabela drivers
        try:
            df_drivers = pd.read_sql("SELECT * FROM drivers", conn)
        except Exception as e:
            df_drivers = generate_mock_data('drivers')
            st.warning("Tabela 'drivers' não encontrada. Usando dados fictícios.")
        
        # Criar dados de fraud_time a partir da tabela orders se possível
        try:
            df_orders = pd.read_sql("SELECT * FROM orders", conn)
            
            # Buscar coluna de hora/data usando a função auxiliar
            hour_col = None
            for col in ['delivery_hour', 'hour', 'created_at', 'timestamp', 'date']:
                if col in df_orders.columns:
                    hour_col = col
                    break
            
            if hour_col:
                # Processar para extrair hora
                if pd.api.types.is_datetime64_any_dtype(df_orders[hour_col]):
                    df_orders['hora'] = df_orders[hour_col].dt.hour
                else:
                    # Tenta converter para datetime
                    try:
                        # Tentar inferir o formato de data comum
                        sample_date = df_orders[hour_col].iloc[0] if len(df_orders) > 0 else None
                        
                        if sample_date:
                            if isinstance(sample_date, str):
                                # Tentar alguns formatos comuns de data
                                formats_to_try = [
                                    '%Y-%m-%d %H:%M:%S',  # 2023-01-15 14:30:00
                                    '%d/%m/%Y %H:%M',     # 15/01/2023 14:30
                                    '%m/%d/%Y %H:%M',     # 01/15/2023 14:30
                                    '%Y-%m-%dT%H:%M:%S',  # 2023-01-15T14:30:00
                                    '%Y%m%d%H%M%S'        # 20230115143000
                                ]
                                
                                for date_format in formats_to_try:
                                    try:
                                        df_orders['hora'] = pd.to_datetime(df_orders[hour_col], format=date_format).dt.hour
                                        break
                                    except:
                                        continue
                                else:
                                    # Se nenhum formato funcionar, usar o método padrão que gera o aviso
                                    df_orders['hora'] = pd.to_datetime(df_orders[hour_col], errors='coerce').dt.hour
                            else:
                                # Se não for string, tentar converter normalmente
                                df_orders['hora'] = pd.to_datetime(df_orders[hour_col]).dt.hour
                        else:
                            # Gerar horas aleatórias se não houver dados
                            df_orders['hora'] = np.random.randint(0, 24, len(df_orders))
                    except Exception as e:
                        # Em caso de erro, gerar horas aleatórias
                        st.warning(f"Erro ao extrair hora: {e}. Usando valores aleatórios.")
                        df_orders['hora'] = np.random.randint(0, 24, len(df_orders))
                
                # Usar a função auxiliar para buscar coluna de ID
                id_col = get_id_column(df_orders)
                
                if id_col:
                    # Agrupar por hora para criar dados de fraude por horário
                    df_fraud_time = df_orders.groupby('hora').agg({
                        id_col: 'count',  # Usar a coluna de ID encontrada
                    }).reset_index()
                    
                    df_fraud_time.columns = ['hora', 'total_pedidos']
                    df_fraud_time['periodo_dia'] = df_fraud_time['hora'].apply(lambda x: 
                        'Madrugada' if 0 <= x < 6 else 
                        'Manhã' if 6 <= x < 12 else 
                        'Tarde' if 12 <= x < 18 else 'Noite')
                    
                    # Gerar pedidos com fraude (simulados)
                    df_fraud_time['pedidos_com_fraude'] = np.random.randint(1, 20, len(df_fraud_time))
                    df_fraud_time['percentual_fraude'] = (df_fraud_time['pedidos_com_fraude'] / df_fraud_time['total_pedidos'] * 100).round(2)
                else:
                    st.warning("Nenhuma coluna de ID encontrada na tabela orders.")
                    df_fraud_time = generate_mock_data('fraud_time')
            else:
                df_fraud_time = generate_mock_data('fraud_time')
        except Exception as e:
            st.warning(f"Erro ao processar dados de horário: {e}")
            df_fraud_time = generate_mock_data('fraud_time')
        
        # Gerar dados de região baseados na localização dos clientes, se disponível
        try:
            df_customers = pd.read_sql("SELECT * FROM customers", conn)
            region_col = None
            
            for col in ['region', 'state', 'location', 'city', 'address']:
                if col in df_customers.columns:
                    region_col = col
                    break
                    
            if region_col:
                # Usar a função auxiliar para buscar coluna de ID
                id_col = get_id_column(df_customers)
                
                if id_col:
                    df_fraud_region = df_customers.groupby(region_col).agg({
                        id_col: 'count'  # Usar a coluna de ID encontrada
                    }).reset_index()
                    
                    df_fraud_region.columns = ['region', 'total_pedidos']
                    df_fraud_region['total_itens_faltantes'] = np.random.randint(5, 50, len(df_fraud_region))
                    df_fraud_region['media_itens_faltantes'] = (df_fraud_region['total_itens_faltantes'] / df_fraud_region['total_pedidos']).round(2)
                    df_fraud_region['percentual_fraude'] = (df_fraud_region['total_itens_faltantes'] / (df_fraud_region['total_pedidos'] * 5) * 100).round(2)
                else:
                    st.warning("Nenhuma coluna de ID encontrada na tabela customers.")
                    df_fraud_region = generate_mock_data('fraud_region')
            else:
                df_fraud_region = generate_mock_data('fraud_region')
        except Exception as e:
            st.warning(f"Erro ao processar dados de região: {e}")
            df_fraud_region = generate_mock_data('fraud_region')
        
        # Motoristas suspeitos (usando os 20% piores motoristas)
        try:
            if len(df_drivers) > 0:
                suspicious_count = max(1, int(len(df_drivers) * 0.2))  # 20% ou pelo menos 1
                
                # Verificar se há alguma medida de desempenho
                performance_cols = [col for col in df_drivers.columns if any(term in col.lower() for term in 
                                   ['rating', 'score', 'performance', 'avaliacao', 'fraude', 'fraud', 'missing'])]
                
                if performance_cols:
                    # Ordenar pelos piores (considerando que valores mais altos são piores para 'missing' e 'fraude')
                    sort_ascending = any(term in performance_cols[0].lower() for term in ['missing', 'fraude', 'fraud'])
                    df_suspicious_drivers = df_drivers.sort_values(performance_cols[0], ascending=not sort_ascending).head(suspicious_count).copy()
                else:
                    # Se não houver medida de desempenho, gere valores aleatórios
                    df_drivers['desempenho_aleatorio'] = np.random.uniform(1, 10, len(df_drivers))
                    df_suspicious_drivers = df_drivers.sort_values('desempenho_aleatorio', ascending=False).head(suspicious_count).copy()
                    df_suspicious_drivers.drop('desempenho_aleatorio', axis=1, inplace=True)
                
                # Adicionar colunas de fraude simuladas
                df_suspicious_drivers['total_entregas'] = np.random.randint(10, 500, len(df_suspicious_drivers))
                df_suspicious_drivers['itens_faltantes'] = np.random.randint(10, 100, len(df_suspicious_drivers))
                df_suspicious_drivers['media_itens_faltantes'] = (df_suspicious_drivers['itens_faltantes'] / df_suspicious_drivers['total_entregas']).round(2)
                df_suspicious_drivers['percentual_fraude'] = (df_suspicious_drivers['itens_faltantes'] / (df_suspicious_drivers['total_entregas'] * 5) * 100).round(2)
            else:
                df_suspicious_drivers = generate_mock_data('suspicious_drivers')
        except Exception as e:
            st.warning(f"Erro ao processar dados de motoristas suspeitos: {e}")
            df_suspicious_drivers = generate_mock_data('suspicious_drivers')
        
        # Produtos não entregues
        try:
            df_products = pd.read_sql("SELECT * FROM products", conn)
            df_missing = pd.read_sql("SELECT * FROM missing_items", conn)
            
            # Verificar se há informações sobre o produto e sua categoria
            product_id_col = None
            for col in df_missing.columns:
                if 'product' in col.lower() and 'id' in col.lower():
                    product_id_col = col
                    break
            
            if product_id_col and product_id_col in df_missing.columns:
                # Contar ocorrências de cada produto
                product_counts = df_missing[product_id_col].value_counts().reset_index()
                product_counts.columns = ['product_id', 'total_relatos']
                
                # Buscar coluna de ID nos produtos
                product_main_id = get_id_column(df_products)
                
                if product_main_id:
                    # Mesclar com informações de produtos
                    merged_df = pd.merge(product_counts, df_products, left_on='product_id', right_on=product_main_id, how='left')
                    
                    # Verificar colunas para categoria e preço
                    category_col = None
                    name_col = None
                    price_col = None
                    
                    for col in merged_df.columns:
                        if any(term in col.lower() for term in ['category', 'categoria', 'type', 'tipo']):
                            category_col = col
                        elif any(term in col.lower() for term in ['name', 'nome', 'title', 'titulo']):
                            name_col = col
                        elif any(term in col.lower() for term in ['price', 'preco', 'valor', 'value']):
                            price_col = col
                    
                    # Criar DataFrame final
                    df_missing_products = pd.DataFrame()

                    # Garantir que haja uma coluna 'id' (mesmo que seja cópia de product_id)
                    merged_df['id'] = merged_df['product_id']  # garante compatibilidade com código que espera 'id'

                    df_missing_products['id'] = merged_df['id']
                    df_missing_products['product_id'] = merged_df['product_id']
                    
                    if name_col:
                        df_missing_products['product_name'] = merged_df[name_col]
                    else:
                        df_missing_products['product_name'] = [f"Produto {i}" for i in range(len(merged_df))]
                    
                    if category_col:
                        df_missing_products['category'] = merged_df[category_col]
                    else:
                        df_missing_products['category'] = np.random.choice(['Eletrônicos', 'Alimentos', 'Vestuário', 'Casa'], len(merged_df))
                    
                    if price_col:
                        df_missing_products['price'] = merged_df[price_col]
                    else:
                        df_missing_products['price'] = np.random.uniform(10, 500, len(merged_df))
                    
                    df_missing_products['total_relatos'] = merged_df['total_relatos']
                else:
                    st.warning("Nenhuma coluna de ID encontrada na tabela products.")
                    df_missing_products = generate_mock_data('missing_products')
            else:
                df_missing_products = generate_mock_data('missing_products')
        except Exception as e:
            st.warning(f"Erro ao processar dados de produtos: {e}")
            df_missing_products = generate_mock_data('missing_products')
        
        # Tendência de fraudes (baseado em orders se disponível)
        try:
            if 'df_orders' in locals():
                # Verificar se há data
                date_col = None
                for col in df_orders.columns:
                    if any(term in col.lower() for term in ['date', 'data', 'created_at', 'created', 'datetime']):
                        date_col = col
                        break
                
                if date_col and date_col in df_orders.columns:
                    # Converter para datetime
                    df_orders[date_col] = pd.to_datetime(df_orders[date_col], errors='coerce')
                    
                    # Agrupar por data
                    df_orders['date'] = df_orders[date_col].dt.date
                    
                    # Usar a função auxiliar para buscar coluna de ID
                    id_col = get_id_column(df_orders)
                    
                    if id_col:
                        df_fraud_trend = df_orders.groupby('date').agg({
                            id_col: 'count'  # Usar a coluna de ID encontrada
                        }).reset_index()
                        
                        df_fraud_trend.columns = ['date', 'total_pedidos']
                        
                        # Gerar itens faltantes (simulados)
                        df_fraud_trend['date'] = pd.to_datetime(df_fraud_trend['date'])
                        df_fraud_trend['itens_faltantes'] = np.random.randint(1, 50, len(df_fraud_trend))
                        df_fraud_trend['percentual_fraude'] = (df_fraud_trend['itens_faltantes'] / (df_fraud_trend['total_pedidos'] * 5) * 100).round(2)
                    else:
                        st.warning("Nenhuma coluna de ID encontrada para análise de tendência.")
                        df_fraud_trend = generate_mock_data('fraud_trend')
                else:
                    df_fraud_trend = generate_mock_data('fraud_trend')
            else:
                df_fraud_trend = generate_mock_data('fraud_trend')
        except Exception as e:
            st.warning(f"Erro ao processar dados de tendência: {e}")
            df_fraud_trend = generate_mock_data('fraud_trend')
        
        # Clientes suspeitos
        try:
            if 'df_customers' in locals() and len(df_customers) > 0:
                # Selecionar 50 clientes aleatórios para simular suspeitos
                suspicious_count = min(50, len(df_customers))
                df_suspicious_customers = df_customers.sample(suspicious_count).copy()
                
                # Buscar coluna de ID
                id_col = get_id_column(df_suspicious_customers)
                
                # Adicionar colunas simuladas de fraude
                if id_col:
                    df_suspicious_customers['customer_id'] = df_suspicious_customers[id_col]
                else:
                    df_suspicious_customers['customer_id'] = [f"C{i:03d}" for i in range(1, suspicious_count+1)]
                
                # Buscar coluna de nome
                name_col = None
                for col in df_suspicious_customers.columns:
                    if any(term in col.lower() for term in ['name', 'nome']):
                        name_col = col
                        break
                
                if name_col:
                    df_suspicious_customers['customer_name'] = df_suspicious_customers[name_col]
                else:
                    df_suspicious_customers['customer_name'] = [f"Cliente {i}" for i in range(1, suspicious_count+1)]
                
                # Buscar coluna de idade
                age_col = None
                for col in df_suspicious_customers.columns:
                    if any(term in col.lower() for term in ['age', 'idade']):
                        age_col = col
                        break
                
                if age_col:
                    df_suspicious_customers['customer_age'] = df_suspicious_customers[age_col]
                else:
                    df_suspicious_customers['customer_age'] = np.random.randint(18, 70, suspicious_count)
                
                df_suspicious_customers['total_pedidos'] = np.random.randint(5, 50, suspicious_count)
                df_suspicious_customers['itens_faltantes'] = np.random.randint(2, 30, suspicious_count)
                df_suspicious_customers['media_itens_faltantes'] = (df_suspicious_customers['itens_faltantes'] / df_suspicious_customers['total_pedidos']).round(2)
                df_suspicious_customers['percentual_fraude'] = (df_suspicious_customers['itens_faltantes'] / (df_suspicious_customers['total_pedidos'] * 5) * 100).round(2)
            else:
                df_suspicious_customers = generate_mock_data('suspicious_customers')
        except Exception as e:
            st.warning(f"Erro ao processar dados de clientes suspeitos: {e}")
            df_suspicious_customers = generate_mock_data('suspicious_customers')
        
        # Fechar conexão
        conn.close()
        
        return {
            'drivers': df_drivers,
            'fraud_time': df_fraud_time, 
            'fraud_region': df_fraud_region,
            'suspicious_drivers': df_suspicious_drivers,
            'missing_products': df_missing_products,
            'fraud_trend': df_fraud_trend,
            'suspicious_customers': df_suspicious_customers
        }
        
    except Exception as e:
        st.warning(f"Erro ao acessar o banco de dados: {e}. Carregando dados fictícios...")
        
        # Se houver qualquer erro, gerar todos os dados fictícios
        return generate_mock_data_all()

def generate_mock_data(data_type):
    """
    Gera dados fictícios para demonstração quando os dados reais não estão disponíveis
    """
    np.random.seed(42)  # Para reprodutibilidade
    
    if data_type == 'drivers':
        # Gerar dados de motoristas
        n_drivers = 100
        data = {
            'driver_id': [f'D{i:03d}' for i in range(1, n_drivers+1)],
            'driver_name': [f'Motorista {i}' for i in range(1, n_drivers+1)],
            'age': np.random.randint(20, 60, n_drivers),
            'Trips': np.random.randint(10, 500, n_drivers),
            'orders_delivered': np.random.randint(10, 500, n_drivers),
            'avg_missing_items': np.random.uniform(0, 5, n_drivers),
            'total_missing_items': np.random.randint(0, 50, n_drivers),
            'total_delivered_items': np.random.randint(50, 1000, n_drivers),
            'missing_ratio': np.random.uniform(0, 0.2, n_drivers),
            'avg_order_amount': np.random.uniform(20, 200, n_drivers),
            'orders_with_missing': np.random.randint(0, 30, n_drivers),
            'problem_order_ratio': np.random.uniform(0, 0.3, n_drivers)
        }
        return pd.DataFrame(data)
    
    elif data_type == 'fraud_time':
        # Gerar dados de fraude por horário
        data = {
            'hora': list(range(24)),
            'periodo_dia': ['Madrugada']*6 + ['Manhã']*6 + ['Tarde']*6 + ['Noite']*6,
            'total_pedidos': [np.random.randint(100, 1000) for _ in range(24)],
            'pedidos_com_fraude': [np.random.randint(5, 50) for _ in range(24)]
        }
        df = pd.DataFrame(data)
        df['percentual_fraude'] = (df['pedidos_com_fraude'] / df['total_pedidos'] * 100).round(2)
        return df
    
    elif data_type == 'fraud_region':
        # Gerar dados de fraude por região
        regions = ['Norte', 'Sul', 'Leste', 'Oeste', 'Centro', 'Nordeste', 'Sudeste']
        data = {
            'region': regions,
            'total_pedidos': [np.random.randint(500, 5000) for _ in range(len(regions))],
            'total_itens_faltantes': [np.random.randint(50, 500) for _ in range(len(regions))]
        }
        df = pd.DataFrame(data)
        df['media_itens_faltantes'] = (df['total_itens_faltantes'] / df['total_pedidos']).round(2)
        df['percentual_fraude'] = (df['total_itens_faltantes'] / (df['total_pedidos'] * 5) * 100).round(2)
        return df
    
    elif data_type == 'suspicious_drivers':
        # Gerar dados de motoristas suspeitos
        n_drivers = 50
        data = {
            'driver_id': [f'D{i:03d}' for i in range(1, n_drivers+1)],
            'driver_name': [f'Motorista {i}' for i in range(1, n_drivers+1)],
            'age': np.random.randint(20, 60, n_drivers),
            'total_entregas': np.random.randint(10, 500, n_drivers),
            'itens_faltantes': np.random.randint(10, 100, n_drivers)
        }
        df = pd.DataFrame(data)
        df['media_itens_faltantes'] = (df['itens_faltantes'] / df['total_entregas']).round(2)
        df['percentual_fraude'] = (df['itens_faltantes'] / (df['total_entregas'] * 5) * 100).round(2)
        return df
    
    elif data_type == 'missing_products':
        # Gerar dados de produtos não entregues
        n_products = 50
        categories = ['Eletrônicos', 'Alimentos', 'Vestuário', 'Casa', 'Beleza', 'Brinquedos', 'Esportes']
        data = {
            'product_id': [f'P{i:03d}' for i in range(1, n_products+1)],
            'product_name': [f'Produto {i}' for i in range(1, n_products+1)],
            'category': np.random.choice(categories, n_products),
            'price': np.random.uniform(10, 500, n_products),
            'total_relatos': np.random.randint(1, 100, n_products)
        }
        df = pd.DataFrame(data)
        df['id'] = df['product_id']  # Garantir que existe coluna 'id'
        return df
    
    elif data_type == 'fraud_trend':
        # Gerar dados de tendência de fraudes
        n_days = 365
        today = datetime.now()
        dates = [(today - timedelta(days=i)).date() for i in range(n_days)]
        dates.reverse()  # Para ordenar cronologicamente
        
        data = {
            'date': dates,
            'total_pedidos': [np.random.randint(500, 2000) for _ in range(n_days)],
            'itens_faltantes': [np.random.randint(20, 200) for _ in range(n_days)]
        }
        df = pd.DataFrame(data)
        df['percentual_fraude'] = (df['itens_faltantes'] / (df['total_pedidos'] * 5) * 100).round(2)
        return df
    
    elif data_type == 'suspicious_customers':
        # Gerar dados de clientes suspeitos
        n_customers = 50
        data = {
            'customer_id': [f'C{i:03d}' for i in range(1, n_customers+1)],
            'customer_name': [f'Cliente {i}' for i in range(1, n_customers+1)],
            'customer_age': np.random.randint(18, 70, n_customers),
            'total_pedidos': np.random.randint(5, 50, n_customers),
            'itens_faltantes': np.random.randint(2, 30, n_customers)
        }
        df = pd.DataFrame(data)
        df['media_itens_faltantes'] = (df['itens_faltantes'] / df['total_pedidos']).round(2)
        df['percentual_fraude'] = (df['itens_faltantes'] / (df['total_pedidos'] * 5) * 100).round(2)
        return df
    
    # Caso padrão para tipos desconhecidos
    return pd.DataFrame()

def generate_mock_data_all():
    """
    Gera dados fictícios para demonstração para todos os tipos de dados
    
    Returns:
        Dicionário com todos os DataFrames necessários
    """
    return {
        'drivers': generate_mock_data('drivers'),
        'fraud_time': generate_mock_data('fraud_time'),
        'fraud_region': generate_mock_data('fraud_region'),
        'suspicious_drivers': generate_mock_data('suspicious_drivers'),
        'missing_products': generate_mock_data('missing_products'),
        'fraud_trend': generate_mock_data('fraud_trend'),
        'suspicious_customers': generate_mock_data('suspicious_customers')
    }

@st.cache_data
def apply_date_filter(df, date_range=None, date_column='date'):
    """
    Filtra DataFrame por intervalo de datas.
    
    Args:
        df: DataFrame a ser filtrado
        date_range: Tupla (data_inicio, data_fim) para filtro
        date_column: Nome da coluna de data no DataFrame
        
    Returns:
        DataFrame filtrado
    """
    if df is None or df.empty or date_range is None or date_column not in df.columns:
        return df
    
    # Garantir que a coluna de data é datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Aplicar filtro de data
    start_date, end_date = date_range
    filtered_df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    
    return filtered_df

@st.cache_data
def apply_category_filter(df, category=None, category_column='category'):
    """
    Filtra DataFrame por categoria.
    
    Args:
        df: DataFrame a ser filtrado
        category: Categoria para filtro
        category_column: Nome da coluna de categoria no DataFrame
        
    Returns:
        DataFrame filtrado
    """
    if df is None or df.empty or category is None or category == "Todas" or category_column not in df.columns:
        return df
    
    # Aplicar filtro de categoria
    return df[df[category_column] == category]

@st.cache_data
def apply_region_filter(df, region=None, region_column='region'):
    """
    Filtra DataFrame por região.
    
    Args:
        df: DataFrame a ser filtrado
        region: Região para filtro
        region_column: Nome da coluna de região no DataFrame
        
    Returns:
        DataFrame filtrado
    """
    if df is None or df.empty or region is None or region == "Todas" or region_column not in df.columns:
        return df
    
    # Aplicar filtro de região
    return df[df[region_column] == region]

@st.cache_data
def detect_anomalies(df, column, threshold=1.5):
    """
    Detecta anomalias em uma coluna usando o método do IQR (Intervalo Interquartil).
    
    Args:
        df: DataFrame com os dados
        column: Nome da coluna para detectar anomalias
        threshold: Multiplicador do IQR para determinar limites (padrão: 1.5)
        
    Returns:
        DataFrame com coluna adicional indicando anomalias
    """
    if df is None or df.empty or column not in df.columns:
        return df
    
    # Calcular quartis e IQR
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    
    # Definir limites
    lower_bound = q1 - (threshold * iqr)
    upper_bound = q3 + (threshold * iqr)
    
    # Marcar anomalias
    df = df.copy()
    df['anomalia'] = ((df[column] < lower_bound) | (df[column] > upper_bound))
    
    return df