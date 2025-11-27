import streamlit as st
from drill_library import drills_page
import json
import os

st.set_page_config(layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state._login_msg = ''


with st.sidebar:

    st.image("img/logoOM2.png", width=80, output_format="PNG")

    # Carica credenziali da data/credentials.json se presente (formato: {"user":"pass", ...})
    creds = {}
    creds_path = 'credentials.json'
    if os.path.exists(creds_path):
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
        except Exception:
            creds = {}

    if not st.session_state.authenticated:
        st.header("Login")
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        if st.button("Login"):
            if username and password:
                valid = (username in creds and creds[username] == password) or (not creds and username == "admin" and password == "admin")
                if valid:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.session_state._login_msg = "Credential not correct"
            else:
                st.session_state._login_msg = "Insert username and password"
        if st.session_state._login_msg:
            st.error(st.session_state._login_msg)

    else:
        st.write(f"Access as **{st.session_state.user}**")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

# --- CSS per centrare le tabs ---
st.markdown("""
    <style>
    /* Centra il container delle tab */
    div[data-baseweb="tab-list"] {
        justify-content: center !important;
    }

    /* (opzionale) Migliora estetica */
    div[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #333 !important;
        padding: 6px 20px !important;
        border-radius: 6px 6px 0 0 !important;
    }

    div[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #4A90E2 !important;
        color: #000 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black;'>Drill Calculator App</h1>", unsafe_allow_html=True)

if st.session_state.authenticated == True:

    with open('data/drill_pro2.json', 'r') as f:
        drill_data = json.load(f)

    with open('data/drill_pro2_players.json', 'r') as f:
        drill_data_players = json.load(f)
    
    drills_page(drill_data=drill_data,
                drill_data_players=drill_data_players)

else:

    st.warning("Per favore, effettua il login dalla barra laterale.")

