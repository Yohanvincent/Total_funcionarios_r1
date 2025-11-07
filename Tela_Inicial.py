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
# AUTENTICAÇÃO
# =============================================
try:
    names = st.secrets["auth"]["names"]
    usernames = st.secrets["auth"]["usernames"]
    passwords = st.secrets["auth"]["passwords"]

    credentials = {"usernames": {}}
    for u, n, p in zip(usernames, names, passwords):
        credentials["usernames"][u.lower()] = {"name": n, "password": p}
except:
    st.warning("⚠️ Modo teste")
    credentials = {
        "usernames": {
            "admin": {
                "name": "Admin Logística",
                "password": "$2b$12$5uQ2z7W3k8Y9p0r1t2v3w4x6y7z8A9B0C1D2E3F4G5H6I7J8K9L0M"
            }
        }
    }

authenticator = stauth.Authenticate(
    credentials,
    "logistica_dashboard",
    "chave_forte_123",
    cookie_expiry_days=7
)

# =============================================
# GERENCIAMENTO DE ESTADO DO LOGIN (SEM RERUN)
# =============================================
if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = None
    st.session_state.name = None
    st.session_state.username = None

# Se logout foi clicado, limpa o estado
if st.session_state.authentication_status:
    name, authentication_status, username = authenticator.login("Login", "main")
    if authentication_status == False:
        st.session_state.authentication_status = False
    elif authentication_status is None:
        st.session_state.authentication_status = None
else:
    # Tenta login se não logado
    name, authentication_status, username = authenticator.login("Login", "main")
    if authentication_status:
        st.session_state.authentication_status = True
        st.session_state.name = name
        st.session_state.username = username
    elif authentication_status == False:
        st.session_state.authentication_status = False
    else:
        st.session_state.authentication_status = None

# =============================================
# CONTEÚDO LOGADO (USANDO SESSION STATE)
# =============================================
if st.session_state.authentication_status:
    # Sidebar com logout
    with st.sidebar:
        st.success(f"Olá, **{st.session_state.name}**!")
        if st.button("Sair"):
            authenticator.logout("Sair", "main")
            # Limpa session state e rerun
            for key in st.session_state.keys():
                del st.session_state[key]
            st.experimental_rerun()

    # TÍTULO
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 50px;'>"
        "Dados Operacionais (Capacidade / Produtividade)"
        "</h1>",
        unsafe_allow_html=True
    )

    # BOTÕES (AGORA SEM CHAVES DUPLICADAS PARA EVITAR ERROS)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📶 Acumulado x Produção", use_container_width=True, key="btn1"):
            st.switch_page("pages/01-Acumulado_x_Producao.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📊 Capacidade x Produção", use_container_width=True, key="btn2"):
            st.switch_page("pages/02-Capacidade_x_Producao.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📶 Produção x Equipe", use_container_width=True, key="btn3"):
            st.switch_page("pages/03-Producao_x_Equipe.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🧮 Total de Colaboradores", use_container_width=True, key="btn4"):
            st.switch_page("pages/04-Total_Funcionarios.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("👷👷‍♀️ Auxiliares de Carga/Descarga x Conferentes", use_container_width=True, key="btn5"):
            st.switch_page("pages/05-Auxiliar_x_Conferente.py")

    # RODAPÉ
    st.markdown(
        "<hr style='margin-top: 80px;'>"
        "<p style='text-align: center; color: gray; font-size: 0.9em;'>"
        "Escolha uma opção para visualizar a disponibilidade da equipe."
        "</p>",
        unsafe_allow_html=True
    )

# =============================================
# ERROS
# =============================================
elif st.session_state.authentication_status == False:
    st.error("❌ Usuário ou senha incorretos")
elif st.session_state.authentication_status is None:
    st.warning("🔐 Por favor, insira suas credenciais")
