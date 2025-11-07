# Tela_inicial.py
# =============================================
# OBJETIVO: Página inicial com navegação + campos de colagem
# FUNCIONALIDADES:
# • Campos para colar jornadas (Conferentes + Auxiliares)
# • Dados persistem via session_state
# • Botões na ordem solicitada
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
# PERSISTÊNCIA DE DADOS COLADOS
# =============================================
if "jornada_conf" not in st.session_state:
    st.session_state.jornada_conf = ""
if "jornada_aux" not in st.session_state:
    st.session_state.jornada_aux = ""

# =============================================
# TÍTULO CENTRALIZADO
# =============================================
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 40px;'>
        Dados Operacionais (Capacidade / Produtividade)
    </h1>
    """,
    unsafe_allow_html=True
)

# =============================================
# CAMPOS PARA COLAR JORNADAS
# =============================================
st.markdown("### Cole as jornadas (uma por linha, separadas por espaço)")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Conferentes**")
    jornada_conf = st.text_area(
        "Cole aqui os dados de Conferentes",
        value=st.session_state.jornada_conf,
        height=300,
        placeholder="01:00 04:00 05:05 10:23 1\n16:00 20:00 21:05 01:24 2\n...",
        key="input_conf"
    )
    if jornada_conf != st.session_state.jornada_conf:
        st.session_state.jornada_conf = jornada_conf
        st.success("Conferentes atualizados!")

with col_b:
    st.markdown("**Auxiliares**")
    jornada_aux = st.text_area(
        "Cole aqui os dados de Auxiliares",
        value=st.session_state.jornada_aux,
        height=300,
        placeholder="16:00 20:00 21:05 01:24 5\n18:00 22:00 23:00 03:12 1\n...",
        key="input_aux"
    )
    if jornada_aux != st.session_state.jornada_aux:
        st.session_state.jornada_aux = jornada_aux
        st.success("Auxiliares atualizados!")

st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# BOTÕES DE NAVEGAÇÃO (CENTRALIZADOS, ORDEM CORRETA)
# =============================================
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # 1. Acumulado x Produção
    if st.button("📶 Acumulado x Produção", use_container_width=True, key="btn_acum"):
        st.switch_page("pages/01-Acumulado_x_Producao.py")
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Capacidade x Produção
    if st.button("📊 Capacidade x Produção", use_container_width=True, key="btn_capac"):
        st.switch_page("pages/02-Capacidade_x_Producao.py")
    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Produção x Equipe
    if st.button("📶 Produção x Equipe", use_container_width=True, key="btn_prod"):
        st.switch_page("pages/03-Producao_x_Equipe.py")
    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Total de Colaboradores
    if st.button("🧮 Total de Colaboradores", use_container_width=True, key="btn_total"):
        st.switch_page("pages/04-Total_Funcionarios.py")
    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Auxiliares x Conferentes
    if st.button("👷👷‍♀️ Auxiliares x Conferentes", use_container_width=True, key="btn_aux_vs_conf"):
        st.switch_page("pages/05-Auxiliar_x_Conferente.py")

# =============================================
# RODAPÉ
# =============================================
st.markdown(
    """
    <hr style='margin-top: 60px;'>
    <p style='text-align: center; color: gray; font-size: 0.9em;'>
        Cole os dados → Clique em um botão → Veja os gráficos em tempo real.
    </p>
    """,
    unsafe_allow_html=True
)
