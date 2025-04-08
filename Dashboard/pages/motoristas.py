import streamlit as st
import pandas as pd
from utils.load_data import carregar_dados

def carregar():
    st.title("🚚 Motoristas Sob Alerta")
    st.write("Análise dos motoristas com maiores taxas de itens não entregues.")

    df = carregar_dados()

    motoristas = df.groupby(['driver_id']).agg({
        'pedido_id': 'count',
        'itens_faltantes': 'sum'
    }).reset_index()

    motoristas["taxa_fraude"] = motoristas["itens_faltantes"] / motoristas["pedido_id"]
    motoristas = motoristas.sort_values("taxa_fraude", ascending=False).head(10)

    st.dataframe(motoristas.rename(columns={
        'driver_id': 'ID do Motorista',
        'pedido_id': 'Pedidos Entregues',
        'itens_faltantes': 'Total de Itens Faltantes',
        'taxa_fraude': 'Taxa de Itens Faltantes'
    }), use_container_width=True)
