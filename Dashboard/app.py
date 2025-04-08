import streamlit as st

# Importando os módulos de páginas
from pages import resumo, motoristas, regioes, periodos, recomendacoes, analises_avancadas
from utils.styles import aplicar_estilo

def main():
    st.set_page_config(
        page_title="Walmart: Monitoramento de Fraudes",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    aplicar_estilo()

    st.sidebar.title("📊 Dashboard de Entregas Walmart")
    opcao = st.sidebar.radio("Navegar para:", [
        "📌 Resumo Geral",
        "🚚 Motoristas Sob Alerta",
        "📍 Regiões Críticas",
        "⏰ Horários Suspeitos",
        "📊 Análises Avançadas",
        "🛠 Recomendações"
    ])

    if opcao == "📌 Resumo Geral":
        resumo.carregar()
    elif opcao == "🚚 Motoristas Sob Alerta":
        motoristas.carregar()
    elif opcao == "📍 Regiões Críticas":
        regioes.carregar()
    elif opcao == "⏰ Horários Suspeitos":
        periodos.carregar()
    elif opcao == "📊 Análises Avançadas":
        analises_avancadas.carregar()
    elif opcao == "🛠 Recomendações":
        recomendacoes.carregar()

if __name__ == "__main__":
    main()
