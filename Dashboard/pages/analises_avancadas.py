import streamlit as st
import plotly.express as px
from utils.load_data import carregar_dados

def carregar():
    st.title("📊 Análises Avançadas de Entregas")

    df = carregar_dados()

    st.subheader("📌 Pedidos por Período do Dia")
    fig1 = px.histogram(df, x="periodo", color="periodo", title="Distribuição dos Pedidos por Período do Dia")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📈 Proporção de Itens Faltantes por Período")
    if "missing_ratio" in df.columns:
        fig2 = px.box(df, x="periodo", y="missing_ratio", color="periodo",
                      title="Boxplot da Proporção de Itens Faltantes por Período")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("A coluna 'missing_ratio' não foi encontrada nos dados carregados.")

    st.subheader("⏰ Distribuição de Entregas por Hora")
    if "delivery_hour_only" in df.columns:
        fig3 = px.histogram(df, x="delivery_hour_only", nbins=24,
                            title="Entregas Realizadas por Hora do Dia")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("A coluna 'delivery_hour_only' não está disponível.")

    st.subheader("🎻 Distribuição da Proporção de Itens Faltantes (Violin Plot)")
    if "missing_ratio" in df.columns:
        fig4 = px.violin(df, y="missing_ratio", box=True, points="all",
                         title="Violin Plot da Proporção de Itens Faltantes")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("A coluna 'missing_ratio' não está disponível.")
