# authenticate.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def get_authenticator():
    try:
        # CORREÇÃO: st.secrets não é dicionário direto
        auth_config = st.secrets.get("auth", {})
        if not auth_config:
            raise KeyError
        names = auth_config["names"]
        usernames = auth_config["usernames"]
        passwords = auth_config["passwords"]
    except:
        st.warning("Modo teste ativo")
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
