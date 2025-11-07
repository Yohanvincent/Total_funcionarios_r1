# Tela_inicial.py
# =============================================
# OBJETIVO: Página inicial com navegação direta para as abas
# FUNCIONALIDADES:
# • Três botões grandes e intuitivos
# • Redirecionamento imediato via st.switch_page()
# • Layout centralizado e responsivo
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
        Dados Operacionais (Capacidade / Produtividade)
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
   # Botões na ordem solicitada:

# 1. Acumulado x Produção
if st.button(
    "Acumulado x Produção",
    use_container_width=True,
    key="btn_acum"
):
    st.switch_page("pages/01-Acumulado_x_Producao.py")
st.markdown("<br>", unsafe_allow_html=True)

# 2. Capacidade x Produção
if st.button(
    "Capacidade x Produção",
    use_container_width=True,
    key="btn_capac"
):
    st.switch_page("pages/02-Capacidade_x_Producao.py")
st.markdown("<br>", unsafe_allow_html=True)

# 3. Produção x Equipe
if st.button(
    "Produção x Equipe",
    use_container_width=True,
    key="btn_prod"
):
    st.switch_page("pages/03-Producao_x_Equipe.py")
st.markdown("<br>", unsafe_allow_html=True)

# 4. Total Funcionários
if st.button(
    "Total de Colaboradores",
    use_container_width=True,
    key="btn_total"
):
    st.switch_page("pages/04-Total_Funcionarios.py")
st.markdown("<br>", unsafe_allow_html=True)

# 5. Auxiliar x Conferentes
if st.button(
    "Auxiliares de Carga/Descarga x Conferentes",
    use_container_width=True,
    key="btn_aux_vs_conf"
):
    st.switch_page("pages/05-Auxiliar_x_Conferente.py")

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
