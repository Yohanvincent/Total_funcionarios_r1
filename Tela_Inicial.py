# Tela_Inicial.py
import streamlit as st

st.set_page_config(
    page_title="Disponibilidade de Equipe",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    "<h1 style='text-align: center; margin-bottom: 50px;'>"
    "Dados Operacionais (Capacidade / Produtividade)"
    "</h1>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("📶 Acumulado x Produção", use_container_width=True):
        st.switch_page("pages/01-Acumulado_x_Producao.py")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📊 Capacidade x Produção", use_container_width=True):
        st.switch_page("pages/02-Capacidade_x_Producao.py")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📶 Produção x Equipe", use_container_width=True):
        st.switch_page("pages/03-Producao_x_Equipe.py")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🧮 Total de Colaboradores", use_container_width=True):
        st.switch_page("pages/04-Total_Funcionarios.py")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("👷👷‍♀️ Auxiliares de Carga/Descarga x Conferentes", use_container_width=True):
        st.switch_page("pages/05-Auxiliar_x_Conferente.py")

st.markdown(
    "<hr style='margin-top: 80px;'>"
    "<p style='text-align: center; color: gray; font-size: 0.9em;'>"
    "Escolha uma opção para visualizar a disponibilidade da equipe."
    "</p>",
    unsafe_allow_html=True
)
