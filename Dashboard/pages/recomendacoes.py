import streamlit as st

def carregar():
    st.title("🛠 Recomendações Estratégicas")
    st.markdown("""
    ### 📍 Baseado na análise dos dados, recomenda-se:

    - **Auditoria de Motoristas** com taxas anormais de itens faltantes;
    - **Verificação fotográfica** no momento da entrega;
    - **Checklist Digital** e **Assinatura Digital do Cliente**;
    - Reforço de **segurança nas regiões críticas**;
    - Monitoramento em **períodos de maior risco**, especialmente no turno da manhã;
    - **Pontuação e incentivo** para motoristas com bons indicadores;
    - **Coleta de GPS e tempo de entrega** para refinar a detecção de fraudes;
    - **Testes A/B** com diferentes métodos de embalagem e verificação.
    """)
