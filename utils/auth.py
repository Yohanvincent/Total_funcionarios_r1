# utils/auth.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml

def get_authenticator():
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

    return stauth.Authenticate(
        credentials,
        "logistica_dashboard",
        "chave_forte_123",
        cookie_expiry_days=7
    )
