# authenticate.py
import streamlit as st
import streamlit_authenticator as stauth

def get_authenticator():
    try:
        # Usa st.secrets.to_dict() → dict completo
        secrets = st.secrets.to_dict()
        auth = secrets.get("auth", {})

        if not auth:
            raise KeyError("Seção [auth] não encontrada")

        # Monta o dicionário de credentials (OBRIGATÓRIO)
        credentials = {"usernames": {}}
        names = auth.get("names", [])
        usernames = auth.get("usernames", [])
        passwords = auth.get("passwords", [])

        for username, name, password in zip(usernames, names, passwords):
            credentials["usernames"][username.lower()] = {
                "name": name,
                "password": password
            }

        if not credentials["usernames"]:
            raise ValueError("Nenhum usuário encontrado")

    except Exception as e:
        st.warning(f"Modo teste: {str(e)}")
        credentials = {
            "usernames": {
                "admin": {
                    "name": "Admin Logística",
                    "password": "logistica123"
                }
            }
        }

    return stauth.Authenticate(
        credentials,
        "logistica_dashboard",
        "chave_forte_123",
        cookie_expiry_days=7
    )
