import streamlit as st
import plotly.express as px
from utils.loaders import load_data_from_db  # Corrigido para usar a função correta

def carregar():
    st.title(" Análises Avançadas de Entregas")

    # Carregar dados usando a função correta
    df = load_data_from_db()

    # Verificar se temos dados
    if df is None or not isinstance(df, dict) or not df:
        st.error("Não foi possível carregar os dados para análise.")
        return
    
    # Usar o DataFrame de drivers como base
    if 'drivers' in df and df['drivers'] is not None and not df['drivers'].empty:
        df_drivers = df['drivers']
    else:
        st.warning("Dados de motoristas não disponíveis.")
        return

    st.subheader(" Pedidos por Período do Dia")
    # Verificar se a coluna existe antes de tentar usar
    if "periodo_dia" in df_drivers.columns:
        fig1 = px.histogram(df_drivers, x="periodo_dia", color="periodo_dia", title="Distribuição dos Pedidos por Período do Dia")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("A coluna 'periodo_dia' não foi encontrada nos dados carregados.")

    st.subheader(" Proporção de Itens Faltantes por Período")
    if "missing_ratio" in df_drivers.columns and "periodo_dia" in df_drivers.columns:
        fig2 = px.box(df_drivers, x="periodo_dia", y="missing_ratio", color="periodo_dia",
                      title="Boxplot da Proporção de Itens Faltantes por Período")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("As colunas necessárias não foram encontradas nos dados carregados.")

    st.subheader(" Distribuição de Entregas por Hora")
    if "delivery_hour_only" in df_drivers.columns:
        fig3 = px.histogram(df_drivers, x="delivery_hour_only", nbins=24,
                            title="Entregas Realizadas por Hora do Dia")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("A coluna 'delivery_hour_only' não está disponível.")

    st.subheader(" Distribuição da Proporção de Itens Faltantes (Violin Plot)")
    if "missing_ratio" in df_drivers.columns:
        fig4 = px.violin(df_drivers, y="missing_ratio", box=True, points="all",
                         title="Violin Plot da Proporção de Itens Faltantes")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("A coluna 'missing_ratio' não está disponível.")