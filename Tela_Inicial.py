# Tela_inicial.py
# =============================================
# OBJETIVO: Página inicial com navegação para as abas
# FUNCIONALIDADES:
#   • Dois botões grandes e claros
#   • Redirecionamento para as páginas específicas
#   • Layout limpo e centralizado
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
        Disponibilidade de Equipe
    </h1>
    """,
    unsafe_allow_html=True
)

# =============================================
# BOTÕES DE NAVEGAÇÃO (CENTRALIZADOS)
# =============================================
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("<br>", unsafe_allow_html=True)  # Espaço vertical

with col2:
    # Botão para Conferentes vs Auxiliares
    if st.button(
        "📊 Conferentes vs Auxiliares",
        use_container_width=True,
        key="btn_conf_vs_aux"
    ):
        st.switch_page("pages/1_Conferentes_vs_Auxiliares.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão para Total de Funcionários
    if st.button(
        "👥 Total de Funcionários",
        use_container_width=True,
        key="btn_total"
    ):
        st.switch_page("pages/2_Total_Funcionarios.py")

with col3:
    st.markdown("<br>", unsafe_allow_html=True)  # Espaço vertical

# =============================================
# RODAPÉ (OPCIONAL)
# =============================================
st.markdown(
    """
    <hr style='margin-top: 80px;'>
    <p style='text-align: center; color: gray; font-size: 0.9em;'>
        Selecione uma opção acima para visualizar os gráficos de disponibilidade.
    </p>
    """,
    unsafe_allow_html=True
)
