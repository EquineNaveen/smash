import streamlit as st
from PIL import Image

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
/* Center align the main title */
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("Gyaan Apps: Login, Signup & Password Reset Instructions")

st.markdown("""
Welcome to Gyaan Apps! Please follow the instructions below for Signup, Login, and Password Reset.

---
**Note:** If you are a new user, you must complete the Signup process before you can Login or Reset your password.
---
""")

# --- Steps to Sign Up ---
try:
    st.image(r"artifacts/login and signup/signup.PNG", caption="Sign Up Screen", use_column_width=True)
except Exception:
    st.warning("Sign Up screenshot (signup.PNG) not found.")

st.markdown("""
### Steps to Sign Up

1. Click the **Sign Up** button on the left sidebar or at the top.
2. Fill in your **Username**, **Email**, **Password**, and **Confirm Password**.
3. Click the **Sign Up** button to create your account.
4. If you already have an account, click **Login** to go back.
---
""")

# --- Steps to Login ---
try:
    st.image(r"artifacts/login and signup/login.PNG", caption="Login Screen", use_column_width=True)
except Exception:
    st.info("Please save your login screenshot as 'login.PNG' in the folder: D:/smash/artifacts/login and signup/")



st.markdown("""
### Steps to Login

1. Make sure you have already signed up for an account.
2. Click the **Login** button on the left sidebar or at the top.
3. Enter your **Username** and **Password** in the respective fields.
4. Click the **Login** button to access your account.
5. If you forgot your password, click **Forgot Password?** to reset it.

---
""")

# --- Steps to Reset Password ---
try:
    st.image(r"artifacts/login and signup/forgot_password.PNG", caption="Reset Password Screen", use_column_width=True)
except Exception:
    st.warning("Reset Password screenshot (forgot password.PNG) not found.")

st.markdown("""
### Steps to Reset Password

1. Click **Forgot Password?** on the Login screen.
2. Enter your **Username or Email**.
3. Enter your **New Password** and **Confirm New Password**.
4. Click **Reset Password** to update your password.
5. Click **Login** to return to the login page.
""")


