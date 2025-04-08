import streamlit as st
import pandas as pd
from utils.load_data import carregar_dados

def carregar():
    st.title("⏰ Horários Suspeitos")
    st.write("Análise por períodos do dia com mais casos registrados.")

    df = carregar_dados()
    periodos = df.groupby("periodo").agg({
        'pedido_id': 'count',
        'itens_faltantes': 'sum'
    }).reset_index()
    periodos["taxa"] = periodos["itens_faltantes"] / periodos["pedido_id"]

    st.dataframe(periodos.rename(columns={
        'periodo': 'Período do Dia',
        'pedido_id': 'Total de Pedidos',
        'itens_faltantes': 'Itens Faltantes',
        'taxa': 'Taxa de Itens Faltantes'
    }), use_container_width=True)
