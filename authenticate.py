# authenticate.py
import streamlit as st
import streamlit_authenticator as stauth

def get_authenticator():
    try:
        secrets = st.secrets.to_dict()
        auth = secrets.get("auth", {})

        credentials = {
            "usernames": {
                auth.get("usernames", ["admin"])[0]: {
                    "name": auth.get("names", ["Admin Logística"])[0],
                    "password": auth.get("passwords", ["logistica123"])[0]
                }
            }
        }

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
