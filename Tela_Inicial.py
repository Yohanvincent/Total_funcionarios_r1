# Tela_Inicial.py
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
# AUTENTICAÇÃO COM FALLBACK
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
except:
    st.warning("⚠️ Modo teste: secrets.toml não encontrado. Usando usuário padrão.")
    names = ["Admin Logística"]
    usernames = ["admin"]
    passwords = ["logistica123"]
    hashed_passwords = stauth.Hasher(passwords).generate()
    authenticator = stauth.Authenticate(
        names, usernames, hashed_passwords,
        "logistica_dashboard", "chave_muito_forte_123456789", cookie_expiry_days=7
    )

# =============================================
# TELA DE LOGIN
# =============================================
name, authentication_status, username = authenticator.login("Login Seguro", "main")

# =============================================
# USUÁRIO LOGADO
# =============================================
if authentication_status:
    with st.sidebar:
        st.success(f"Olá, **{name}**!")
        authenticator.logout("Sair", "main")

    st.markdown(
        """
        <h1 style='text-align: center; margin-bottom: 50px;'>
            Dados Operacionais (Capacidade / Produtividade)
        </h1>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📶 Acumulado x Produção", use_container_width=True, key="btn_acum"):
            st.switch_page("pages/01-Acumulado_x_Producao.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📊 Capacidade x Produção", use_container_width=True, key="btn_capac"):
            st.switch_page("pages/02-Capacidade_x_Producao.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📶 Produção x Equipe", use_container_width=True, key="btn_prod"):
            st.switch_page("pages/03-Producao_x_Equipe.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🧮 Total de Colaboradores", use_container_width=True, key="btn_total"):
            st.switch_page("pages/04-Total_Funcionarios.py")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("👷👷‍♀️ Auxiliares de Carga/Descarga x Conferentes", use_container_width=True, key="btn_aux_vs_conf"):
            st.switch_page("pages/05-Auxiliar_x_Conferente.py")

    st.markdown(
        """
        <hr style='margin-top: 80px;'>
        <p style='text-align: center; color: gray; font-size: 0.9em;'>
            Escolha uma opção para visualizar a disponibilidade da equipe.
        </p>
        """,
        unsafe_allow_html=True
    )

elif authentication_status == False:
    st.error("Usuário ou senha incorretos")
elif authentication_status is None:
    st.warning("Por favor, insira suas credenciais")
