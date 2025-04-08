import streamlit as st
st.set_page_config(page_title="Dashboard de Fraudes", layout="wide", initial_sidebar_state="expanded")

import os
import sys
import pandas as pd
import sqlite3
from PIL import Image
import base64
import traceback

# Adicionar o diretório atual ao path para importar módulos personalizados
sys.path.append(os.path.dirname(__file__))

# Define o caminho dinâmico para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "Database", "walmart_fraudes.db")



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

# Importar função para carregar dados do banco
from utils.loaders import load_data_from_db

# Função para carregar dados
@st.cache_data
def load_data():
    """Carrega e prepara os dados para uso na aplicação"""
    try:
        # Carregar dados do banco SQLite usando a função do módulo utils.loaders
        data = load_data_from_db()
        
        if data:
            st.session_state['data_loaded'] = True
        
        return data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# Função para criar o cabeçalho
def create_header():
    """Cria o cabeçalho da aplicação com logo e título"""
    header_container = st.container()
    with header_container:
        cols = st.columns([0.1, 0.8, 0.1])
        with cols[0]:
            # Placeholder para logo - substituir pelo caminho real do logo
            try:
                st.image("assets/icons/logos/Walmart_logo.svg", width=80)
            except Exception:
                pass  # Não mostra nada se a imagem falhar
        with cols[1]:
            st.markdown("<h1 class='main-title'>Walmart Fraud Detection Dashboard</h1>", unsafe_allow_html=True)


# Função para criar a barra lateral
def create_sidebar(data):
    """Cria a barra lateral com filtros e informações"""
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
        
        # Informações sobre a aplicação
        with st.expander("Sobre esta Dashboard", expanded=False):
            st.markdown("""
            ### 🛒 Walmart Fraud Detection
            
            Esta dashboard foi desenvolvida para análise e detecção de fraudes
            nas entregas do Walmart, oferecendo insights visuais para
            equipes de logística, auditoria, segurança e operações.
            
            **Navegue pelas abas para explorar diferentes aspectos:**
            - 📊 Panorama: Visão geral dos indicadores
            - 🕒 Tempo: Análise temporal das fraudes
            - 📦 Produtos: Itens mais relatados como não entregues
            - 🧍 Entregadores: Análise de motoristas suspeitos
            - 🔍 Anomalias: Padrões ocultos nos dados
            - ⚖️ Diagnóstico: Avaliação de responsabilidades
            - 📈 Evolução: Tendências ao longo do tempo
            - 💡 Recomendações: Ações sugeridas
            """)
            
        st.markdown("---")
        
        # Exportação
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            st.button("Exportar PDF", key="export_pdf")
        with export_col2:
            st.button("Exportar PNG", key="export_png")

# Menu de navegação principal
def create_navigation_menu():
    """Cria o menu de navegação com abas personalizadas"""
    tabs = st.tabs([
        "📊 Panorama", 
        "🕒 Análise Temporal", 
        "📦 Produtos & Categorias", 
        "🧍 Regiões & Entregadores",
        "🔍 Padrões Ocultos",
        "⚖️ Diagnóstico",
        "📈 Evolução",
        "💡 Recomendações"
    ])
    
    return tabs

def carregar_dados():
    if not os.path.exists(DB_PATH):
        st.error(f"Arquivo de banco de dados não encontrado em {DB_PATH}")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        data = {
            'drivers': pd.read_sql_query("SELECT * FROM drivers", conn),
            'suspicious_drivers': pd.read_sql_query("SELECT * FROM suspicious_drivers", conn),
            'fraud_region': pd.read_sql_query("SELECT * FROM fraud_region", conn),
            'missing_products': pd.read_sql_query("SELECT * FROM missing_products", conn),
            'fraud_time': pd.read_sql_query("SELECT * FROM fraud_time", conn),
            'fraud_trend': pd.read_sql_query("SELECT * FROM fraud_trend", conn),
            'suspicious_customers': pd.read_sql_query("SELECT * FROM suspicious_customers", conn)
        }
        conn.close()
        return data
    except Exception as e:
        st.error(f"Erro ao carregar os dados do banco: {e}")
        return None



def main():
    """Função principal que gerencia o fluxo da aplicação"""
    # Carregar dados
    st.write(f"Tentando carregar o banco em: {DB_PATH}")
    st.write("Existe?", os.path.exists(DB_PATH))

    data = carregar_dados()
    
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
