# authenticate.py
import streamlit as st
import streamlit_authenticator as stauth

def get_authenticator():
    try:
        # CORREÇÃO FINAL: st.secrets.to_dict() → dict completo
        secrets_dict = st.secrets.to_dict()
        auth_config = secrets_dict.get("auth", {})
        
        if not auth_config:
            raise KeyError("Seção 'auth' não encontrada")
        
        names = auth_config.get("names", [])
        usernames = auth_config.get("usernames", [])
        passwords = auth_config.get("passwords", [])
        
        if len(names) == 0 or len(usernames) == 0 or len(passwords) == 0:
            raise ValueError("Listas de auth vazias")
            
    except Exception as e:
        st.warning(f"Modo teste ativo: {str(e)}")
        names = ["Admin Logística"]
        usernames = ["admin"]
        passwords = ["logistica123"]  # TEXTO CLARO

    return stauth.Authenticate(
        names,
        usernames,
        passwords,
        "logistica_dashboard",
        "chave_forte_123",
        cookie_expiry_days=7
    )
