# Tela_inicial.py
# =============================================
# OBJETIVO: Página inicial com navegação direta para as abas
# FUNCIONALIDADES:
#   • Dois botões grandes e intuitivos
#   • Redirecionamento imediato via st.switch_page()
#   • Layout centralizado e responsivo
# =============================================

import streamlit as st

# =============================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(
    page_title="Disponibilidade de Equipe",
    layout="wide"
)

# =============================================
# TÍTULO CENTRALIZADO
# =============================================
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 50px;'>
        Excelência Operacional - Dados (Capacidade / Produtividade)
    </h1>
    """,
    unsafe_allow_html=True
)

# =============================================
# BOTÕES DE NAVEGAÇÃO (CENTRALIZADOS)
# =============================================
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("<br>", unsafe_allow_html=True)

with col2:
    # Botão para Auxiliar x Conferente
    if st.button(
        "👷Conferentes vs 👷‍♀️Auxiliares",
        use_container_width=True,
        key="btn_aux_vs_conf"
    ):
        st.switch_page("pages/Auxiliar_x_Conferente.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão para Total de Funcionários
    if st.button(
        "🧮Total de Funcionários",
        use_container_width=True,
        key="btn_total"
    ):
        st.switch_page("pages/Total_Funcionarios.py")

with col3:
    st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# RODAPÉ
# =============================================
st.markdown(
    """
    <hr style='margin-top: 80px;'>
    <p style='text-align: center; color: gray; font-size: 0.9em;'>
        Escolha uma opção para visualizar a disponibilidade da equipe.
    </p>
    """,
    unsafe_allow_html=True
)
