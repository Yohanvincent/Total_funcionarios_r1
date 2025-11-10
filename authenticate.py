# authenticate.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def get_authenticator():
    credentials = yaml.load(st.secrets["auth"], Loader=SafeLoader)
    return stauth.Authenticate(
        credentials["names"],
        credentials["usernames"],
        credentials["passwords"],
        "logistica_dashboard",
        "chave_forte_123",
        cookie_expiry_days=7
    )
