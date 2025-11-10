# Tela_Inicial.py
import streamlit as st
import streamlit_authenticator as stauth
import bcrypt

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
# INICIALIZA SESSION STATE
# =============================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = None

# =============================================
# FORMULÁRIO DE LOGIN (MANUAL)
# =============================================
if not st.session_state.logged_in:
    with st.form("login_form"):
        st.subheader("Login Seguro")
        username = st.text_input("Usuário", value="admin")
        password = st.text_input("Senha", type="password", value="logistica123")
        submit = st.form_submit_button("Entrar")

        if submit:
            # VALIDAÇÃO MANUAL (POIS login() NÃO ACEITA PARÂMETROS)
            user_key = username.lower()
            if user_key in credentials["usernames"]:
                stored_hash = credentials["usernames"][user_key]["password"]
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    st.session_state.logged_in = True
                    st.session_state.user_name = credentials["usernames"][user_key]["name"]
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Senha incorreta")
            else:
                st.error("Usuário não encontrado")

# =============================================
# CONTEÚDO LOGADO
# =============================================
else:
    # Sidebar com logout
    with st.sidebar:
        st.success(f"Olá, **{st.session_state.user_name}**!")
        if st.button("Sair"):
            st.session_state.logged_in = False
            st.session_state.user_name = None
            st.rerun()

    # Título
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 50px;'>"
        "Dados Operacionais (Capacidade / Produtividade)"
        "</h1>",
        unsafe_allow_html=True
    )

    # Botões centralizados
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

    # Rodapé
    st.markdown(
        "<hr style='margin-top: 80px;'>"
        "<p style='text-align: center; color: gray; font-size: 0.9em;'>"
        "Escolha uma opção para visualizar a disponibilidade da equipe."
        "</p>",
        unsafe_allow_html=True
    )
