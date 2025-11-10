# Tela_Inicial.py
import streamlit as st
import streamlit_authenticator as stauth

# =============================================
# CONFIGURAÇÃO
# =============================================
st.set_page_config(
    page_title="Disponibilidade de Equipe",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# =============================================
# AUTENTICAÇÃO DIRETA (SIMPLIFICADA)
# =============================================
try:
    # Carrega do secrets.toml
    names = st.secrets["auth"]["names"]
    usernames = st.secrets["auth"]["usernames"]
    passwords = st.secrets["auth"]["passwords"]
except:
    # Modo teste
    names = ["Admin Logística"]
    usernames = ["admin"]
    passwords = ["logistica123"]

# Cria credentials dict (OBRIGATÓRIO)
credentials = {"usernames": {}}
for u, n, p in zip(usernames, names, passwords):
    credentials["usernames"][u.lower()] = {"name": n, "password": p}

authenticator = stauth.Authenticate(
    credentials,
    "logistica_dashboard",
    "chave_forte_123",
    cookie_expiry_days=7
)

# =============================================
# LOGIN VISÍVEL
# =============================================
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Salva no session state
    st.session_state.authentication_status = True
    st.session_state.name = name
    st.session_state.username = username

    # Logout na sidebar
    with st.sidebar:
        st.success(f"Olá, **{name}**!")
        authenticator.logout("Sair", "sidebar")

    # TÍTULO
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 50px;'>"
        "Dados Operacionais (Capacidade / Produtividade)"
        "</h1>",
        unsafe_allow_html=True
    )

    # 5 BOTÕES CENTRALIZADOS
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

    # RODAPÉ
    st.markdown(
        "<hr style='margin-top: 80px;'>"
        "<p style='text-align: center; color: gray; font-size: 0.9em;'>"
        "Escolha uma opção para visualizar a disponibilidade da equipe."
        "</p>",
        unsafe_allow_html=True
    )

elif authentication_status == False:
    st.error("Usuário ou senha incorretos")
elif authentication_status is None:
    st.warning("Por favor, insira suas credenciais")
