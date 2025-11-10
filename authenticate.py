# authenticate.py
import streamlit as st
import streamlit_authenticator as stauth

def get_authenticator():
    try:
        # CORREÇÃO: st.secrets.get retorna dict → extrai listas
        auth_config = st.secrets.get("auth", {})
        if not auth_config:
            raise KeyError("Configuração 'auth' não encontrada")
        
        names = auth_config.get("names", [])
        usernames = auth_config.get("usernames", [])
        passwords = auth_config.get("passwords", [])
        
        if not (names and usernames and passwords):
            raise ValueError("Listas de auth vazias")
            
    except Exception as e:
        st.warning(f"Modo teste ativo: {str(e)}")
        names = ["Admin Logística"]
        usernames = ["admin"]
        passwords = ["logistica123"]  # TEXTO CLARO PARA TESTE

    return stauth.Authenticate(
        names,
        usernames,
        passwords,
        "logistica_dashboard",
        "chave_forte_123",
        cookie_expiry_days=7
    )
