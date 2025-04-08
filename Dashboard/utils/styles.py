import streamlit as st

def aplicar_estilo():
    st.markdown("""
        <style>
            /* Ajuste no padding da página */
            .main {
                padding-top: 2rem;
                padding-right: 2rem;
                padding-left: 2rem;
                background-color: #FFFCEE;
            }

            /* Estilo para títulos */
            h1, h2, h3 {
                color: #296D84;
                font-family: 'Segoe UI', sans-serif;
            }

            /* Estilo para texto */
            body, p, div {
                font-size: 16px;
                color: #000000;
            }

            /* Estilo para a barra lateral */
            .css-1d391kg, .css-1cpxqw2 {
                background-color: #F2BB6E;
                color: #000000;
            }

            /* Remoção do rodapé padrão do Streamlit */
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
