# Tela_Inicial.py
# =============================================
# OBJETIVO: Login seguro + navegação com botões
# =============================================
import streamlit as st
import streamlit_authenticator as stauth

# =============================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(
    page_title="Disponibilidade de Equipe",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================
# AUTENTICAÇÃO (usa secrets.toml do Streamlit Cloud)
# =============================================
try:
    authenticator = stauth.Authenticate(
        st.secrets["auth"]["names"],
        st.secrets["auth"]["usernames"],
        st.secrets["auth"]["passwords"],
        "logistica_dashboard",
        "chave_muito_forte_123456789",
        cookie_expiry_days=7
    )
except Exception as e:
    st.error("Erro ao carregar autenticação. Verifique o secrets.toml.")
    st.stop()

# =============================================
# TELA DE LOGIN
# =============================================
name, authentication_status, username = authenticator.login("Login Seguro", "main")

# =============================================
# USUÁRIO LOGADO → MOSTRA DASHBOARD
# =============================================
if authentication_status:
    # Sidebar com logout
    with st.sidebar:
        st.success(f"Olá, **{name}**!")
        authenticator.logout("Sair", "main")

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
        if st.button("👷👷‍♀️ Auxiliares de Carga/Descarga x Conferentes", use_container_width=True, key="btn_aux_vs_conf"):
            st.switch_page("pages/05-Auxiliar_x_Conferente.py")

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

# =============================================
# ERROS DE LOGIN
# =============================================
elif authentication_status == False:
    st.error("Usuário ou senha incorretos")
elif authentication_status is None:
    st.warning("Por favor, insira suas credenciais")
