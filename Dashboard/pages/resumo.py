import streamlit as st
import pandas as pd
from utils.load_data import carregar_dados
from utils.plotting import grafico_fraudes_por_periodo

def carregar():
    st.title("📌 Panorama Geral de Entregas e Indicadores Críticos")

    df = carregar_dados()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Pedidos", f"{df.shape[0]:,}")
    with col2:
        st.metric("Itens Faltantes", f"{df['itens_faltantes'].sum():,}")
    with col3:
        taxa = (df['itens_faltantes'].sum() / (df['itens_faltantes'].sum() + df['itens_entregues'].sum())) * 100
        st.metric("Taxa Geral de Itens Faltantes", f"{taxa:.2f}%")

    st.markdown("---")
    st.subheader("📈 Evolução das Ocorrências por Período do Dia")
    fig = grafico_fraudes_por_periodo(df)
    st.plotly_chart(fig, use_container_width=True)
