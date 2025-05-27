import streamlit as st
st.set_page_config(page_title="Dashboard de Fraudes", layout="wide", initial_sidebar_state="expanded")

import os
import sys
import pandas as pd
import sqlite3
from PIL import Image
import base64
import traceback
import gc
import warnings

# Suprimir warnings para melhor performance
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Adicionar o diretório atual ao path para importar módulos personalizados
sys.path.append(os.path.dirname(__file__))

# Define o caminho dinâmico para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Subir um nível para acessar a pasta Database na raiz do projeto
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "Database", "walmart_fraudes.db")

# Importar configurações de estilo
from config.style_config import apply_style, get_custom_css
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] ul {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Aplicar estilos customizados
apply_style()
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Inicializar variáveis de sessão
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False
if 'date_filter' not in st.session_state:
    st.session_state['date_filter'] = None
if 'category_filter' not in st.session_state:
    st.session_state['category_filter'] = "Todas"
if 'region_filter' not in st.session_state:
    st.session_state['region_filter'] = "Todas"

# Função para carregar dados - SUPER OTIMIZADA
@st.cache_data(ttl=600, show_spinner=False)  # Cache por 10 minutos, sem spinner
def load_data():
    """Carrega e prepara os dados para uso na aplicação"""
    try:
        data = carregar_dados()
        if data:
            st.session_state['data_loaded'] = True
        return data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def carregar_dados():
    """Função otimizada de carregamento de dados"""
    
    if not os.path.exists(DB_PATH):
        st.error(f"Arquivo de banco de dados não encontrado em {DB_PATH}")
        return None

    try:
        # Conexão otimizada
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        
        # Queries super otimizadas - apenas dados essenciais
        orders_df = pd.read_sql_query("""
            SELECT date, order_id, region, items_missing, 
                   delivery_hour_only, driver_id, customer_id 
            FROM orders 
            LIMIT 10000
        """, conn)
        
        drivers_df = pd.read_sql_query("SELECT driver_id, driver_name, age, Trips FROM drivers LIMIT 500", conn)
        customers_df = pd.read_sql_query("SELECT customer_id, customer_name FROM customers LIMIT 1000", conn)
        products_df = pd.read_sql_query("SELECT product_id, product_name, category FROM products LIMIT 200", conn)
        missing_items_df = pd.read_sql_query("SELECT product_id_1, product_id_2, product_id_3 FROM missing_items LIMIT 5000", conn)
        
        conn.close()
        
        # Converter data apenas uma vez
        orders_df['date'] = pd.to_datetime(orders_df['date'])
        
        # 1. fraud_trend: tendência temporal das fraudes
        fraud_trend = orders_df.groupby(orders_df['date'].dt.date).agg({
            'items_missing': 'sum',
            'order_id': 'count'
        }).reset_index()
        fraud_trend.columns = ['date', 'itens_faltantes', 'total_pedidos']
        fraud_trend['date'] = pd.to_datetime(fraud_trend['date'])
        fraud_trend['casos_fraude'] = fraud_trend['itens_faltantes']
        fraud_trend['percentual_fraude'] = (fraud_trend['itens_faltantes'] / fraud_trend['total_pedidos'] * 100).round(2)
        
        # 2. fraud_region: fraudes por região
        fraud_region = orders_df.groupby('region').agg({
            'items_missing': 'sum',
            'order_id': 'count'
        }).reset_index()
        fraud_region.columns = ['region', 'casos_fraude', 'total_pedidos']
        fraud_region['taxa_fraude'] = (fraud_region['casos_fraude'] / fraud_region['total_pedidos'] * 100).round(2)
        fraud_region['percentual_fraude'] = fraud_region['taxa_fraude']
        fraud_region['total_itens_faltantes'] = fraud_region['casos_fraude']
        
        # 3. missing_products: produtos mais reportados como faltantes
        missing_list = []
        for col in ['product_id_1', 'product_id_2', 'product_id_3']:
            missing_list.extend(missing_items_df[col].dropna().tolist())
        
        # Processamento super otimizado - amostras menores
        missing_products_count = pd.Series(missing_list).value_counts().head(50).reset_index()  # Apenas top 50
        missing_products_count.columns = ['product_id', 'missing_count']
        
        missing_products = missing_products_count.merge(
            products_df[['product_id', 'product_name', 'category']], 
            on='product_id', 
            how='left'
        )
        missing_products.rename(columns={'missing_count': 'itens_faltantes'}, inplace=True)
        missing_products['total_relatos'] = missing_products['itens_faltantes']
        
        # 4. drivers: todos os motoristas
        drivers = drivers_df.copy()
        drivers.rename(columns={'Trips': 'total_entregas'}, inplace=True)
        
        # Criar coluna faixa_etaria que está sendo usada nas páginas
        if 'age' in drivers.columns:
            drivers['faixa_etaria'] = pd.cut(
                drivers['age'], 
                bins=[0, 25, 35, 45, 55, 100], 
                labels=['18-25', '26-35', '36-45', '46-55', '55+'],
                right=False
            )
        else:
            # Se não tiver age, criar faixa_etaria fictícia
            drivers['faixa_etaria'] = '26-35'
        
        # 5. suspicious_drivers: motoristas com alta taxa de itens faltantes
        driver_stats = orders_df.groupby('driver_id').agg({
            'items_missing': 'sum',
            'order_id': 'count'
        }).reset_index()
        driver_stats.columns = ['driver_id', 'relatos_fraude', 'total_entregas']
        driver_stats['taxa_fraude'] = (driver_stats['relatos_fraude'] / driver_stats['total_entregas'] * 100).round(2)
        driver_stats['percentual_fraude'] = driver_stats['taxa_fraude']
        
        # Limitar resultados para performance máxima
        suspicious_drivers = driver_stats[
            (driver_stats['taxa_fraude'] > 15) & 
            (driver_stats['total_entregas'] > 5)
        ].head(20).merge(drivers_df[['driver_id', 'driver_name']], on='driver_id', how='left')  # Apenas top 20
        
        # 6. fraud_time: fraudes por horário
        fraud_time = orders_df.groupby('delivery_hour_only').agg({
            'items_missing': 'sum',
            'order_id': 'count'
        }).reset_index()
        fraud_time.columns = ['hour', 'casos_fraude', 'total_entregas']
        
        # 7. suspicious_customers: clientes com muitos relatos
        customer_stats = orders_df.groupby('customer_id').agg({
            'items_missing': 'sum',
            'order_id': 'count',
            'region': 'first'
        }).reset_index()
        customer_stats.columns = ['customer_id', 'relatos_fraude', 'total_pedidos', 'region']
        customer_stats['taxa_fraude'] = (customer_stats['relatos_fraude'] / customer_stats['total_pedidos'] * 100).round(2)
        customer_stats['percentual_fraude'] = customer_stats['taxa_fraude']
        
        # Limitar resultados para performance máxima
        suspicious_customers = customer_stats[
            (customer_stats['taxa_fraude'] > 20) & 
            (customer_stats['total_pedidos'] > 3)
        ].head(20).merge(customers_df[['customer_id', 'customer_name']], on='customer_id', how='left')  # Apenas top 20
        
        # Limpeza de memória
        del orders_df, drivers_df, customers_df, products_df, missing_items_df
        gc.collect()
        
        # Retornar dados no formato esperado
        data = {
            'fraud_trend': fraud_trend,
            'fraud_region': fraud_region,
            'missing_products': missing_products,
            'drivers': drivers,
            'suspicious_drivers': suspicious_drivers,
            'fraud_time': fraud_time,
            'suspicious_customers': suspicious_customers
        }
        
        return data
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados do banco: {e}")
        return None

# Função para criar o cabeçalho
def create_header():
    """Cria o cabeçalho da aplicação com logo e título"""
    header_container = st.container()
    with header_container:
        cols = st.columns([0.1, 0.8, 0.1])
        with cols[0]:
            try:
                st.image("assets/icons/logos/Walmart_logo.svg", width=80)
            except Exception:
                pass
        with cols[1]:
            st.markdown("<h1 class='main-title'>Walmart Fraud Detection Dashboard</h1>", unsafe_allow_html=True)

# Função para criar a barra lateral (mantendo apenas filtros essenciais)
def create_sidebar(data):
    """Cria a barra lateral apenas com filtros"""
    with st.sidebar:
        st.markdown("<h2 class='sidebar-title'>Filtros Globais</h2>", unsafe_allow_html=True)
        
        # Filtro de data
        if data and 'fraud_trend' in data and not data['fraud_trend'].empty:
            min_date = data['fraud_trend']['date'].min()
            max_date = data['fraud_trend']['date'].max()
            date_range = st.date_input(
                "Período de Análise",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            st.session_state['date_filter'] = date_range
        
        # Filtro de categoria
        if data and 'missing_products' in data and not data['missing_products'].empty:
            categories = ["Todas"] + sorted(data['missing_products']['category'].unique().tolist())
            selected_category = st.selectbox("Categoria de Produto", categories)
            st.session_state['category_filter'] = selected_category
        
        # Filtro de região
        if data and 'fraud_region' in data and not data['fraud_region'].empty:
            regions = ["Todas"] + sorted(data['fraud_region']['region'].unique().tolist())
            selected_region = st.selectbox("Região", regions)
            st.session_state['region_filter'] = selected_region
        
        st.markdown("---")
        

# Menu de navegação principal
def create_navigation_menu():
    """Cria o menu de navegação com abas personalizadas"""
    tabs = st.tabs([
        "Panorama Geral", 
        "Análise Temporal", 
        "Produtos & Categorias", 
        "Regiões & Entregadores",
        "Padrões Ocultos",
        "Diagnóstico",
        "Evolução",
        "Recomendações"
    ])
    
    return tabs

def main():
    """Função principal que gerencia o fluxo da aplicação"""
    
    # Carregar dados
    data = load_data()
    
    # Criar cabeçalho
    create_header()
    
    # Criar barra lateral
    create_sidebar(data)
    
    # Criar menu de navegação
    tabs = create_navigation_menu()
    
    # Carregar módulos de páginas conforme a seleção da aba
    from pages import panorama, analise_temporal, categorias_itens, regioes_entregadores
    from pages import padroes_ocultos, diagnostico, evolucao, recomendacoes
    
    with tabs[0]:
        panorama.show(data)
    
    with tabs[1]:
        analise_temporal.show(data)
        
    with tabs[2]:
        categorias_itens.show(data)
        
    with tabs[3]:
        regioes_entregadores.show(data)
    
    with tabs[4]:
        padroes_ocultos.show(data)
        
    with tabs[5]:
        diagnostico.show(data)
        
    with tabs[6]:
        evolucao.show(data)
        
    with tabs[7]:
        recomendacoes.show(data)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Ocorreu um erro na aplicação: {e}")
        st.text("Detalhes do erro:")
        st.text(traceback.format_exc())