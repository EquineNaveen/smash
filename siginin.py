import streamlit as st
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, ALL_ATTRIBUTES, SUBTREE, core

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    /* Hide default Streamlit sidebar navigation */
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    /* Hide sidebar collapse/expand button and its parent container */
    button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;}
    div.st-emotion-cache-1y9tyez.eczjsme4 {display: none !important;}
    </style>
""", unsafe_allow_html=True)

def ldap_authenticate(username: str, password: str):
    # server_uri = "ldap://10.21.6.164:389"
    # base_dn = "dc=dos"
    # user_dn = f"mailacceptinggeneralid={username},{base_dn}"
    # try:
    #     server = Server(server_uri, get_info=ALL)
    #     conn = Connection(server, user=user_dn, password=password, authentication=SIMPLE, auto_bind=True)
    #     conn.unbind()
    return True
    # except core.exceptions.LDAPBindError:
    #     return False
    # except Exception as error:
    #     st.error(f"LDAP error: {error}")
    #     return False

def login():
    st.markdown("<h1 style='text-align: center;'>Login Page</h1>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if ldap_authenticate(username, password):
            st.session_state['user'] = username
            st.session_state['role'] = "USER"
            st.success("Login successful!")
            # Redirect to apps.py after successful login
            st.switch_page("pages/apps.py")
        else:
            st.error("Invalid credentials.")

if 'user' in st.session_state:
    # Redirect to apps.py if already logged in
    st.switch_page("pages/apps.py")
    st.stop()
else:
    login()