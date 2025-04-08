import streamlit as st
import pandas as pd
from utils.load_data import carregar_dados

def carregar():
    st.title("📍 Regiões Críticas")
    st.write("Zonas com maior índice de ocorrências suspeitas.")

    df = carregar_dados()
    regioes = df.groupby("regiao").agg({
        'pedido_id': 'count',
        'itens_faltantes': 'sum'
    }).reset_index()
    regioes["taxa"] = regioes["itens_faltantes"] / regioes["pedido_id"]
    regioes = regioes.sort_values("taxa", ascending=False)

    st.dataframe(regioes.rename(columns={
        'regiao': 'Região',
        'pedido_id': 'Total de Pedidos',
        'itens_faltantes': 'Itens Faltantes',
        'taxa': 'Taxa de Itens Faltantes'
    }), use_container_width=True)
