import streamlit as st
import base64
import os
import hashlib
import time
import json
from datetime import datetime, timedelta
import secrets

# --- Page Configuration ---
st.set_page_config(page_title="Home - Gyaan Apps", layout="wide")

# --- Constants ---
USERS_FILE = "users.json"
RESET_TOKENS_FILE = "reset_tokens.json"
FAQ_FILE = "faq_data.json"

# --- Query Param Persistence ---
query_params = st.query_params
if "user" in query_params and "user" not in st.session_state:
    st.session_state["user"] = query_params["user"]
if "token" in query_params and "token" not in st.session_state:
    st.session_state["token"] = query_params["token"]
if "ts" in query_params and "ts" not in st.session_state:
    st.session_state["ts"] = query_params["ts"]

# Initialize session state variables
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False
if "show_forgot_password" not in st.session_state:
    st.session_state["show_forgot_password"] = False

# Hide sidebar, sidebar nav, sidebar arrow SVG, and sidebar collapse button
st.markdown("""
    <style>
    /* [data-testid="stSidebar"] {display: none !important;} */ /* Ensure sidebar is visible */
    /* div[data-testid="stSidebarNav"] {display: none !important;} */ /* Ensure sidebar nav is visible */
    /* Hide sidebar arrow SVG by class and tag */
    /* svg.eyeqlp53.st-emotion-cache-1f3w014 {display: none !important;} */ /* Ensure sidebar arrow is visible */
    /* Fallback: hide any SVG inside sidebar nav */
    /* [data-testid="stSidebarNav"] svg {display: none !important;} */ /* Ensure sidebar nav SVGs are visible */
    /* Hide sidebar collapse/expand button */
    /* button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;} */ /* Ensure collapse button is visible */
    </style>
""", unsafe_allow_html=True)

# --- Inject Custom CSS ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        height: 100vh;
        min-height: 100vh;
        display: block;
        margin: 0;
        padding: 0;
        padding-bottom: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        min-height: 0 !important;
        height: auto !important;
        flex: unset !important;
        display: block !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    .block-container {
        padding-top: 0 !important;
    }

    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    .user-info {
        font-weight: 600;
        color: #374151;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .login-button {
        background: #3B82F6;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }

    .login-button:hover {
        background: #2563EB;
    }

    .logout-button {
        background: #EF4444;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }

    .logout-button:hover {
        background: #DC2626;
    }

    .announcement {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        color: #166534;
        padding: 15px 20px;
        border-radius: 12px;
        border: 2px solid #16A34A;
        box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15);
        animation: slideDown 0.5s ease-out, pulse 2s ease-in-out infinite;
        position: relative;
        overflow: hidden;
        font-weight: 500;
        font-size: 1.1em;
        margin-bottom: 25px;
    }

    .stCard {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(17, 24, 39, 0.08);
        text-align: center;
        overflow: hidden;
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
        height: auto;
        display: block;
        text-decoration: none;
        color: inherit;
        margin-bottom: 8px;
        cursor: default; /* Add this line to change cursor to arrow */
    }

    /* Remove hover effect from .stCard */
    .stCard:hover {
        /* No transform or shadow on hover */
        transform: none;
        box-shadow: 0 4px 8px rgba(17, 24, 39, 0.08);
        border-color: #E5E7EB;
    }
    
    /* Hide button text and style as invisible overlay */
    .card-button {
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        width: 100% !important;
        height: 50px !important;
        margin: 0 !important;
        padding: 0 !important;
        cursor: pointer !important;
    }

    .card-button:hover {
        background: transparent !important;
        border: none !important;
    }

    .card-button:focus {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .card-title {
        font-size: 1.1em; /* Reduced from 1.25em */
        font-weight: 600;
        background: #4B5563;
        color: white;
        padding: 10px; /* Reduced from 15px */
        margin: 0;
        text-align: center;
    }

    /* Add style for the card description span */
    .card-title span {
        text-align: center;
        display: block;
        font-weight: normal;
    }

    .card-image {
        width: 100%;
        padding: 10px; /* Reduced from 15px */
        background: #F9FAFB;
        height: 150px; /* Reduced from 200px */
        object-fit: contain;
        max-width: 100%;
        max-height: 100%;
        display: block;
        margin: 0 auto;
    }

    .footer {
        text-align: center;
        font-size: 14px;
        padding: 10px;
        margin-top: 0;
        border-top: 1px solid #E5E7EB;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        position: fixed !important;
        left: 0 !important;
        bottom: 0 !important;
        /* width: 100% !important; */
        background: #fff !important;
        z-index: 9999 !important;
        margin-bottom: 0 !important;
        /* Center footer with respect to main content area */
        width: calc(100vw - var(--sidebar-width, 350px));
        left: var(--sidebar-width, 350px) !important;
        right: 0;
        margin-left: auto;
        margin-right: auto;
        max-width: 100vw;
    }

    /* Responsive: fallback for small screens */
    @media (max-width: 900px) {
        .footer {
            left: 0 !important;
            width: 100vw !important;
        }
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }

    .footer-text {
        font-weight: bold;
        color: #222 !important;
        font-size: 1.1em;
        flex: 1;
        text-align: center;
        background: none !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 1 !important;
    }

    /* Add style for Open [card] button before login */
    .open-card-btn {
        display: block;
        text-align: center;
        background: #3B82F6 !important;
        color: white !important;
        padding: 10px 0;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        margin-top: 8px;
        border: none;
        width: 100%;
        font-size: 1em;
        transition: background 0.2s;
    }

    .open-card-btn:hover {
        background: #2563EB !important;
        color: white !important;
    }

    /* Add style for Open [card] button after login */
    .open-card-btn-loggedin {
        display: block;
        text-align: center;
        background: #16A34A !important; /* Green shade */
        color: white !important;
        padding: 10px 0;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        margin-top: 8px;
        border: none;
        width: 100%;
        font-size: 1em;
        transition: background 0.2s;
    }

    .open-card-btn-loggedin:hover {
        background: #15803D !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- User Management Functions ---
def load_users():
    """Load users from JSON file."""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving users: {e}")
        return False

def hash_password(password):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash."""
    return hash_password(password) == hashed_password

def create_user(username, password, email):
    """Create a new user."""
    users = load_users()
    username = username.lower()
    
    # Check if user already exists (case insensitive)
    username_lower = username.lower()
    email_lower = email.lower()
    
    for existing_user in users.keys():
        if existing_user.lower() == username_lower:
            return False, "Username already exists"
    
    # Check if email already exists (case insensitive)
    for user_data in users.values():
        if user_data.get('email', '').lower() == email_lower:
            return False, "Email already exists"
    
    # Create new user (store original case but check case insensitive)
    users[username] = {
        'password': hash_password(password),
        'email': email,
        'created_at': datetime.now().isoformat(),
        'role': 'USER'
    }
    
    if save_users(users):
        return True, "User created successfully"
    else:
        return False, "Error creating user"

def authenticate_user(username, password):
    """Authenticate user with username and password (case insensitive)."""
    users = load_users()
    username_lower = username.lower()
    
    # Find user with case insensitive comparison
    actual_username = None
    for user in users.keys():
        if user.lower() == username_lower:
            actual_username = user
            break
    
    if not actual_username:
        return False
    
    return verify_password(password, users[actual_username]['password'])

def get_user_info(username):
    """Get user information (case insensitive)."""
    users = load_users()
    username_lower = username.lower()
    
    # Find user with case insensitive comparison
    for user, data in users.items():
        if user.lower() == username_lower:
            return data
    return {}

# --- FAQ and About Functions ---
def load_faq_data():
    """Load FAQ and About data from JSON file."""
    try:
        if os.path.exists(FAQ_FILE):
            with open(FAQ_FILE, 'r') as f:
                return json.load(f)
        else:
            # Create default FAQ file if it doesn't exist
            default_data = {
                "faqs": [
                    {
                        "question": "What is Gyaan Apps?",
                        "answer": "Gyaan Apps is a comprehensive suite of AI-powered applications designed to enhance productivity and streamline various tasks."
                    }
                ],
                "about": {
                    "title": "About Gyaan",
                    "content": "Gyaan is an innovative AI-powered platform developed by Team GYAAN."
                }
            }
            with open(FAQ_FILE, 'w') as f:
                json.dump(default_data, f, indent=2)
            return default_data
    except Exception as e:
        st.error(f"Error loading FAQ data: {e}")
        return {"faqs": [], "about": {"title": "About Gyaan", "content": "Content not available."}}

# --- Reset Token Functions ---
def load_reset_tokens():
    """Load reset tokens from JSON file."""
    try:
        if os.path.exists(RESET_TOKENS_FILE):
            with open(RESET_TOKENS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading reset tokens: {e}")
        return {}

def save_reset_tokens(tokens):
    """Save reset tokens to JSON file."""
    try:
        with open(RESET_TOKENS_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving reset tokens: {e}")
        return False

def generate_reset_token(username):
    """Generate a password reset token."""
    token = secrets.token_urlsafe(32)
    expiry = (datetime.now() + timedelta(hours=1)).isoformat()
    
    tokens = load_reset_tokens()
    tokens[token] = {
        'username': username,
        'expiry': expiry
    }
    
    if save_reset_tokens(tokens):
        return token
    return None

def verify_reset_token(token):
    """Verify and return username for reset token."""
    tokens = load_reset_tokens()
    
    if token not in tokens:
        return None
    
    token_data = tokens[token]
    expiry = datetime.fromisoformat(token_data['expiry'])
    
    if datetime.now() > expiry:
        # Token expired, remove it
        del tokens[token]
        save_reset_tokens(tokens)
        return None
    
    return token_data['username']

def reset_password(token, new_password):
    """Reset user password using token."""
    username = verify_reset_token(token)
    if not username:
        return False, "Invalid or expired token"
    
    users = load_users()
    if username not in users:
        return False, "User not found"
    
    # Update password
    users[username]['password'] = hash_password(new_password)
    
    # Remove used token
    tokens = load_reset_tokens()
    if token in tokens:
        del tokens[token]
        save_reset_tokens(tokens)
    
    if save_users(users):
        return True, "Password reset successfully"
    else:
        return False, "Error resetting password"

# --- Token Generation Function ---
def generate_user_token(username):
    """Generate a secure token for user authentication."""
    # print(username)
    username = username.lower()
    secret_key = "GYAAN_SECRET_KEY_2025"
    token_string = f"{username}:{secret_key}"
    # print(token_string)
    token = hashlib.sha256(token_string.encode()).hexdigest()
    timestamp = "STATIC"
    # print("User data : ", username)
    # print("Secreate key: ", secret_key)
    # print("Generated Token = ", token)
    return token, timestamp

# --- Get Base64 Image Function ---
def get_base64_image(image_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(script_dir, image_path)
    
    if not os.path.isfile(absolute_path):
        parent_dir = os.path.dirname(script_dir)
        absolute_path = os.path.join(parent_dir, image_path)
    
    try:
        with open(absolute_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        placeholder = ""
        return placeholder

# --- Handle Login/Logout Logic ---
def handle_logout():
    # Clear session state
    for key in ['user', 'token', 'ts', 'role']:
        if key in st.session_state:
            del st.session_state[key]
    # Clear query params
    st.query_params.clear()
    st.session_state["show_login"] = False
    st.session_state["show_signup"] = False
    st.session_state["show_forgot_password"] = False
    st.rerun()

def handle_login_click():
    st.session_state["show_login"] = True
    st.session_state["show_signup"] = False
    st.session_state["show_forgot_password"] = False
    st.rerun()

def handle_signup_click():
    st.session_state["show_signup"] = True
    st.session_state["show_login"] = False
    st.session_state["show_forgot_password"] = False
    st.rerun()

def handle_forgot_password_click():
    st.session_state["show_forgot_password"] = True
    st.session_state["show_login"] = False
    st.session_state["show_signup"] = False
    st.rerun()

def handle_login_submit(username, password):
    if authenticate_user(username, password):
        token, ts = generate_user_token(username)
        
        # Get the actual username with correct case
        users = load_users()
        actual_username = None
        for user in users.keys():
            if user.lower() == username.lower():
                actual_username = user
                break
        
        user_info = get_user_info(actual_username)
        st.session_state['user'] = actual_username
        st.session_state['token'] = token
        st.session_state['ts'] = ts
        st.session_state['role'] = user_info.get('role', 'USER')
        st.session_state["show_login"] = False
        # Update query params
        st.query_params.update(user=actual_username, token=token, ts=ts)
        st.success("Login successful!")
        st.rerun()
    else:
        st.error("Invalid Creditinals or User Does not exist. Please click on singup if new user or click on Forgot password to rest your password.")

def handle_signup_submit(username, password, confirm_password, email):
    if password != confirm_password:
        st.error("Passwords do not match.")
        return
    
    if len(password) < 6:
        st.error("Password must be at least 6 characters long.")
        return
    
    success, message = create_user(username, password, email)
    if success:
        st.success(message)
        st.info("You can now login with your credentials.")
        st.session_state["show_signup"] = False
        st.session_state["show_login"] = True
        st.rerun()
    else:
        st.error(message)

def handle_forgot_password_submit(username_or_email, new_password, confirm_password):
    """Handle forgot password with direct password reset."""
    if new_password != confirm_password:
        st.error("Passwords do not match.")
        return False
    
    if len(new_password) < 6:
        st.error("Password must be at least 6 characters long.")
        return False
    
    users = load_users()
    username = None
    username_or_email_lower = username_or_email.lower()
    
    # Check if input is username or email (case insensitive)
    for user, data in users.items():
        if user.lower() == username_or_email_lower or data.get('email', '').lower() == username_or_email_lower:
            username = user
            break
    
    if not username:
        st.error("Username or email not found.")
        return False
    
    # Update password directly
    users[username]['password'] = hash_password(new_password)
    
    if save_users(users):
        st.success("Password reset successfully! You can now login with your new password.")
        return True
    else:
        st.error("Error resetting password.")
        return False

# --- Handle App Card Click ---
def handle_app_click(link):
    username = st.session_state.get('user', '')
    if not username:
        # User not logged in, show login form
        st.session_state["show_login"] = True
        st.rerun()
    else:
        # User logged in, redirect to app
        token = st.session_state.get("token", "")
        ts = st.session_state.get("ts", "")
        separator = "&" if "?" in link else "?"
        full_link = f"{link}{separator}user={username}&token={token}&ts={ts}"
        st.markdown(f'<meta http-equiv="refresh" content="0; url={full_link}">', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    # try:
    #     logo_base64 = get_base64_image("artifacts/Gyaan_logo.jpeg")
    #     if logo_base64:
    #         st.image(f"data:image/jpeg;base64,{logo_base64}", width=100)
    # except Exception:
    #     st.warning("Logo image not found.") # Or pass silently
        
    st.markdown("<h2 style='text-align: center;'>Gyaan Apps</h2>", unsafe_allow_html=True)
    st.markdown("---")

    username = st.session_state.get('user')
    if username:
        st.success(f"Logged in as: **{username}**")
        
        # st.markdown("#### Quick Links")
        # # Use HTML buttons for smooth scroll
        # st.markdown("""
        # <button onclick="window.scrollTo({top: document.getElementById('app-cards-section').getBoundingClientRect().top + window.scrollY - 20, behavior: 'smooth'});" style="background:none;border:none;color:#3B82F6;cursor:pointer;font-size:1em;text-align:left;width:100%;">📱 Apps</button>
        # <button onclick="window.scrollTo({top: document.getElementById('about-gyaan-section').getBoundingClientRect().top + window.scrollY - 20, behavior: 'smooth'});" style="background:none;border:none;color:#3B82F6;cursor:pointer;font-size:1em;text-align:left;width:100%;">📄 About Gyaan</button>
        # <button onclick="window.scrollTo({top: document.getElementById('faq-section').getBoundingClientRect().top + window.scrollY - 20, behavior: 'smooth'});" style="background:none;border:none;color:#3B82F6;cursor:pointer;font-size:1em;text-align:left;width:100%;">❓ FAQ</button>
        # """, unsafe_allow_html=True)

        # st.markdown("---")
        if st.button("Logout", use_container_width=True, key="sidebar_logout_btn"):
            handle_logout()
    else:
        st.info("You are not logged in.")
        if st.button("🔑 Login", use_container_width=True, key="sidebar_login_action_btn"):
            handle_login_click()
        if st.button("✍️ Sign Up", use_container_width=True, key="sidebar_signup_action_btn"):
            handle_signup_click()
        
    st.markdown("---")
    
    # Add instruction buttons
    st.markdown("### Instructions")
    if st.button("Gyaan Coder Instructions", use_container_width=True):
        st.switch_page("pages/coder_instruction.py")
    
    if st.button("Gyaan Doc Instructions", use_container_width=True):
        st.switch_page("pages/doc_instruction.py")
    
    if st.button("Gyaan Meeting Instructions", use_container_width=True):
        st.switch_page("pages/meeting_instruction.py")
    
    if st.button("Gyaan Admin Instructions", use_container_width=True):
        st.switch_page("pages/admin_instruction.py")
    
    if st.button("Login or Signup Instructions", use_container_width=True):
        st.switch_page("pages/login_signup.py")

    # Inject JS to allow scrolling to anchors
    st.markdown("""
    <script>
    // Ensure the scroll works after Streamlit reruns
    window.scrollToSection = function(id) {
        var el = document.getElementById(id);
        if (el) {
            window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY - 20, behavior: 'smooth'});
        }
    }
    </script>
    """, unsafe_allow_html=True)

# --- Main App Layout ---

# Top Bar with Login/User Info
username = st.session_state.get('user', '')
if username:
    # User is logged in
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="user-info">👤 Welcome, {username}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("Logout", key="logout_btn"):
            handle_logout()
else:
    # User not logged in
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown('<div class="user-info">Welcome to Gyaan Apps</div>', unsafe_allow_html=True)
    with col2:
        if st.button("Login", key="login_btn"):
            handle_login_click()
    with col3:
        if st.button("Sign Up", key="signup_btn"):
            handle_signup_click()

# Show login form
if st.session_state.get("show_login", False) and not username:
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Login</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_login = st.form_submit_button("Login", use_container_width=True)
        
        if submit_login:
            if login_username and login_password:
                handle_login_submit(login_username, login_password)
            else:
                st.error("Please enter both username and password.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Cancel", key="cancel_login"):
            st.session_state["show_login"] = False
            st.rerun()
    with col2:
        if st.button("Sign Up", key="goto_signup"):
            handle_signup_click()
    with col3:
        if st.button("Forgot Password?", key="goto_forgot"):
            handle_forgot_password_click()

# Show signup form
elif st.session_state.get("show_signup", False) and not username:
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Sign Up</h2>", unsafe_allow_html=True)
    
    with st.form("signup_form"):
        signup_username = st.text_input("Username")
        signup_email = st.text_input("Email")
        signup_password = st.text_input("Password", type="password")
        signup_confirm_password = st.text_input("Confirm Password", type="password")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit_signup:
            if signup_username and signup_email and signup_password and signup_confirm_password:
                handle_signup_submit(signup_username, signup_password, signup_confirm_password, signup_email)
            else:
                st.error("Please fill in all fields.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Cancel", key="cancel_signup"):
            st.session_state["show_signup"] = False
            st.rerun()
    with col2:
        if st.button("Login", key="goto_login"):
            handle_login_click()

# Show forgot password form
elif st.session_state.get("show_forgot_password", False) and not username:
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Reset Password</h2>", unsafe_allow_html=True)
    
    with st.form("forgot_password_form"):
        username_or_email = st.text_input("Username or Email")
        st.markdown("<br>", unsafe_allow_html=True)
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_reset = st.form_submit_button("Reset Password", use_container_width=True)
        
        if submit_reset:
            if username_or_email and new_password and confirm_new_password:
                if handle_forgot_password_submit(username_or_email, new_password, confirm_new_password):
                    st.session_state["show_forgot_password"] = False
                    st.session_state["show_login"] = True
                    time.sleep(2)  # Small delay to show success message
                    st.rerun()
            else:
                st.error("Please fill in all fields.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Cancel", key="cancel_forgot"):
            st.session_state["show_forgot_password"] = False
            st.rerun()
    with col2:
        if st.button("Login", key="goto_login_from_forgot"):
            handle_login_click()

else:
    # Show main app content
    # st.markdown('<div class="announcement">🔔 Latest updates and announcements will appear here</div>', unsafe_allow_html=True)
    st.markdown("<h1 id='app-cards-section' style='text-align: center;'>Gyaan Apps</h1>", unsafe_allow_html=True)

    # App Cards
    cards = [
        {"name": "GYAAN CODER<br><span style='font-size:0.85em'>Gyaan Coder provides real-time answers and code solutions for user queries across any programming language.</span>", "img": "artifacts/coder.jpg", "link": "http://10.21.4.25:8502"},
        {"name": "GYAAN DOC<br><span style='font-size:0.85em'>Gyaan Doc is an AI-powered app that lets you upload documents, get instant summaries, and ask questions based on their content.</span>", "img": "artifacts/doc.jpg", "link": "http://10.21.4.25:8503"},
        {"name": "GYAAN MEETING<br><span style='font-size:0.85em'>Gyaan Meeting converts meeting audio into text, provides transcripts, and lets you query information directly from the conversation.</span>", "img": "artifacts/meeting.jpg", "link": "http://10.21.4.25:8504"},
        {"name": "GYAAN ADMIN<br><span style='font-size:0.85em'>Gyaan Admin is a chatbot to streamline admin tasks and answer queries on operations, policies, and processes.</span>", "img": "artifacts/admin.png", "link": "http://10.21.4.25:8505"},
        # {"name": "GYAAN JITSI<br><span style='font-size:0.85em'>Gyaan Jitsi is an ai enabled meeting platform with meeting recording functionalities.Please upload recorded jitsi meetings to Gyaan Meeting</span>", "img": "artifacts/jitsi.png", "link": "https://gyaanjitsi.ursc.dos.gov.in/"},
        {"name": "ELSIS<br><span style='font-size:0.85em'>ELSIS is a patented AI software designed to detect minute cracks in solar cells with unprecedented precision.</span>", "img": "artifacts/Gyaan_logo.jpeg", "link": "#"},
        {"name": "Medical AI Doctor in Space<br><span style='font-size:0.85em'>MAIDS is a comprehensive medical assistant for astronauts, capable of diagnosing conditions and providing medicine recommendations with precise dosages using pharmacopoeia data</span>", "img": "artifacts/Gyaan_logo.jpeg", "link": "#"},
        {"name": "Integrated Spacecraft Health Monitoring<br><span style='font-size:0.85em'> </span>", "img": "artifacts/Gyaan_logo.jpeg", "link": "#"},
    ]

    cols = st.columns(3)
    
    for i, card in enumerate(cards):
        with cols[i % 3]:
            img_base64 = get_base64_image(card['img'])
            
            # Display card content
            card_html = f'''
            <div class="stCard">
                <img src="data:image/jpeg;base64,{img_base64}" class="card-image">
                <p class="card-title">{card["name"]}</p>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Add button or link below card for clicking
            if card['name'].startswith('ELSIS') or card['name'].startswith('Medical AI Doctor in Space'):
                if st.button("Coming Soon", key=f"card_btn_{i}", 
                            help=f"{card['name'].split('<')[0]} - Coming Soon",
                            use_container_width=True,
                            disabled=False):
                    st.info("This app is coming soon!")
                    pass  # Do nothing for coming soon apps
            else:
                # Build the full link with query params if logged in
                username = st.session_state.get('user', '')
                token = st.session_state.get('token', '')
                ts = st.session_state.get('ts', '')
                link = card['link']
                if link.startswith("http"):
                    if username:
                        separator = "&" if "?" in link else "?"
                        full_link = f"{link}{separator}user={username}&token={token}&ts={ts}"
                        # Use HTML anchor styled as a button to open in new tab
                        button_html = f'''<a href="{full_link}" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;background:#3B82F6;color:white;padding:10px 0;border-radius:6px;text-decoration:none;font-weight:500;margin-top:8px;">Open {card['name'].split('<')[0]}</a>'''
                        st.markdown(button_html, unsafe_allow_html=True)
                    else:
                        # If not logged in, show a button that takes user to login page
                        if st.button(f"Open {card['name'].split('<')[0]}", key=f"card_btn_{i}_login_redirect", help="Login required to access this app", use_container_width=True):
                            st.session_state["show_login"] = True
                            st.session_state["show_signup"] = False
                            st.session_state["show_forgot_password"] = False
                            st.rerun()
                else:
                    if st.button(f"Open {card['name'].split('<')[0]}", key=f"card_btn_{i}", 
                                help=f"Click to open {card['name'].split('<')[0]}",
                                use_container_width=True):
                        st.info("This app is coming soon!")

    # About Gyaan Section
    st.markdown("---")
    faq_data = load_faq_data()
    about_data = faq_data.get('about', {})
    
    st.markdown(f"<h2 id='about-gyaan-section' style='text-align: center; margin-top: 40px; color: #374151;'>{about_data.get('title', 'About Gyaan')}</h2>", unsafe_allow_html=True)
    
    # Format the about content with proper line breaks
    about_content = about_data.get('content', 'Content not available.')
    about_content = about_content.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    st.markdown(f"""
    <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: 20px 0; border: 1px solid #E5E7EB;'>
        <div style='font-size: 1.1em; line-height: 1.6; color: #374151;'>
            {about_content}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FAQ Section
    st.markdown("---")
    st.markdown("<h2 id='faq-section' style='text-align: center; margin-top: 40px; color: #374151;'>Frequently Asked Questions</h2>", unsafe_allow_html=True)
    
    faqs = faq_data.get('faqs', [])
    
    if faqs:
        for i, faq in enumerate(faqs):
            with st.expander(faq['question'], expanded=False):
                st.write(faq['answer'])
    else:
        st.info("No FAQs available at the moment.")

# Footer
isro_logo_base64 = get_base64_image("artifacts/isro.jpg")
ursc_logo_base64 = get_base64_image("artifacts/ursc.jpg")

footer_html = f"""
<div class="footer">
    <img src="data:image/jpeg;base64,{isro_logo_base64}" alt="ISRO Logo" style="height: 35px; margin-right: 10px;">
    <div class="footer-text">🚀 Built by Team GYAAN</div>
    <img src="data:image/jpeg;base64,{ursc_logo_base64}" alt="UESC Logo" style="height: 35px; margin-left: 10px;">
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)


# import streamlit as st
# import base64
# import os
# import hashlib
# import time
# import json
# from datetime import datetime, timedelta
# import secrets

# # --- Page Configuration ---
# st.set_page_config(page_title="Home - Gyaan Apps", layout="wide")

# # --- Constants ---
# USERS_FILE = "users.json"
# RESET_TOKENS_FILE = "reset_tokens.json"
# FAQ_FILE = "faq_data.json"

# # --- Query Param Persistence ---
# query_params = st.query_params
# if "user" in query_params and "user" not in st.session_state:
#     st.session_state["user"] = query_params["user"]
# if "token" in query_params and "token" not in st.session_state:
#     st.session_state["token"] = query_params["token"]
# if "ts" in query_params and "ts" not in st.session_state:
#     st.session_state["ts"] = query_params["ts"]

# # Initialize session state variables
# if "show_login" not in st.session_state:
#     st.session_state["show_login"] = False
# if "show_signup" not in st.session_state:
#     st.session_state["show_signup"] = False
# if "show_forgot_password" not in st.session_state:
#     st.session_state["show_forgot_password"] = False

# # Hide sidebar, sidebar nav, sidebar arrow SVG, and sidebar collapse button
# st.markdown("""
#     <style>
#     [data-testid="stSidebar"] {display: none !important;}
#     div[data-testid="stSidebarNav"] {display: none !important;}
#     /* Hide sidebar arrow SVG by class and tag */
#     svg.eyeqlp53.st-emotion-cache-1f3w014 {display: none !important;}
#     /* Fallback: hide any SVG inside sidebar nav */
#     [data-testid="stSidebarNav"] svg {display: none !important;}
#     /* Hide sidebar collapse/expand button */
#     button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;}
#     </style>
# """, unsafe_allow_html=True)

# # --- Inject Custom CSS ---
# st.markdown("""
#     <style>
#     body {
#         background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
#         height: 100vh;
#         min-height: 100vh;
#         display: block;
#         margin: 0;
#         padding: 0;
#         padding-bottom: 0 !important;
#     }

#     [data-testid="stAppViewContainer"] > .main {
#         min-height: 0 !important;
#         height: auto !important;
#         flex: unset !important;
#         display: block !important;
#         padding-bottom: 0 !important;
#         margin-bottom: 0 !important;
#     }

#     .block-container {
#         padding-top: 0 !important;
#     }

#     .top-bar {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         padding: 15px 20px;
#         background: white;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#         margin-bottom: 20px;
#     }

#     .user-info {
#         font-weight: 600;
#         color: #374151;
#         display: flex;
#         align-items: center;
#         gap: 10px;
#     }

#     .login-button {
#         background: #3B82F6;
#         color: white;
#         border: none;
#         padding: 8px 16px;
#         border-radius: 6px;
#         cursor: pointer;
#         font-weight: 500;
#         transition: background-color 0.2s;
#     }

#     .login-button:hover {
#         background: #2563EB;
#     }

#     .logout-button {
#         background: #EF4444;
#         color: white;
#         border: none;
#         padding: 8px 16px;
#         border-radius: 6px;
#         cursor: pointer;
#         font-weight: 500;
#         transition: background-color 0.2s;
#     }

#     .logout-button:hover {
#         background: #DC2626;
#     }

#     .announcement {
#         background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
#         color: #166534;
#         padding: 15px 20px;
#         border-radius: 12px;
#         border: 2px solid #16A34A;
#         box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15);
#         animation: slideDown 0.5s ease-out, pulse 2s ease-in-out infinite;
#         position: relative;
#         overflow: hidden;
#         font-weight: 500;
#         font-size: 1.1em;
#         margin-bottom: 25px;
#     }

#     .stCard {
#         background: white;
#         border-radius: 12px;
#         box-shadow: 0 4px 8px rgba(17, 24, 39, 0.08);
#         text-align: center;
#         overflow: hidden;
#         border: 1px solid #E5E7EB;
#         transition: all 0.3s ease;
#         height: auto;
#         display: block;
#         text-decoration: none;
#         color: inherit;
#         margin-bottom: 8px;
#         cursor: default; /* Add this line to change cursor to arrow */
#     }

#     /* Remove hover effect from .stCard */
#     .stCard:hover {
#         /* No transform or shadow on hover */
#         transform: none;
#         box-shadow: 0 4px 8px rgba(17, 24, 39, 0.08);
#         border-color: #E5E7EB;
#     }
    
#     /* Hide button text and style as invisible overlay */
#     .card-button {
#         background: transparent !important;
#         border: none !important;
#         color: transparent !important;
#         width: 100% !important;
#         height: 50px !important;
#         margin: 0 !important;
#         padding: 0 !important;
#         cursor: pointer !important;
#     }

#     .card-button:hover {
#         background: transparent !important;
#         border: none !important;
#     }

#     .card-button:focus {
#         background: transparent !important;
#         border: none !important;
#         box-shadow: none !important;
#     }

#     .card-title {
#         font-size: 1.1em; /* Reduced from 1.25em */
#         font-weight: 600;
#         background: #4B5563;
#         color: white;
#         padding: 10px; /* Reduced from 15px */
#         margin: 0;
#         text-align: center;
#     }

#     /* Add style for the card description span */
#     .card-title span {
#         text-align: center;
#         display: block;
#         font-weight: normal;
#     }

#     .card-image {
#         width: 100%;
#         padding: 10px; /* Reduced from 15px */
#         background: #F9FAFB;
#         height: 150px; /* Reduced from 200px */
#         object-fit: contain;
#         max-width: 100%;
#         max-height: 100%;
#         display: block;
#         margin: 0 auto;
#     }

#     .footer {
#         text-align: center;
#         font-size: 14px;
#         padding: 10px;
#         margin-top: 0;
#         border-top: 1px solid #E5E7EB;
#         box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
#         display: flex;
#         justify-content: center;
#         align-items: center;
#         gap: 10px;
#         position: fixed !important;
#         left: 0 !important;
#         bottom: 0 !important;
#         width: 100% !important;
#         background: #fff !important;
#         z-index: 9999 !important;
#         margin-bottom: 0 !important;
#     }

#     .footer img {
#         height: 35px;
#         object-fit: contain;
#     }

#     .footer-text {
#         font-weight: bold;
#         color: #222;
#         font-size: 1.1em;
#     }

#     .login-form {
#         max-width: 400px;
#         margin: 50px auto;
#         padding: 30px;
#         background: white;
#         border-radius: 15px;
#         box-shadow: 0 6px 20px rgba(0,0,0,0.1);
#     }

#     .auth-link {
#         color: #3B82F6;
#         text-decoration: none;
#         cursor: pointer;
#         font-weight: 500;
#     }

#     .auth-link:hover {
#         color: #2563EB;
#         text-decoration: underline;
#     }

#     @keyframes slideDown {
#         from {
#             transform: translateY(-20px);
#             opacity: 0;
#         }
#         to {
#             transform: translateY(0);
#             opacity: 1;
#         }
#     }

#     @keyframes pulse {
#         0% { box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15); }
#         50% { box-shadow: 0 4px 20px rgba(22, 163, 74, 0.25); }
#         100% { box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15); }
#     }

#     header[data-testid="stHeader"] {
#         display: none !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- User Management Functions ---
# def load_users():
#     """Load users from JSON file."""
#     try:
#         if os.path.exists(USERS_FILE):
#             with open(USERS_FILE, 'r') as f:
#                 return json.load(f)
#         return {}
#     except Exception as e:
#         st.error(f"Error loading users: {e}")
#         return {}

# def save_users(users):
#     """Save users to JSON file."""
#     try:
#         with open(USERS_FILE, 'w') as f:
#             json.dump(users, f, indent=2)
#         return True
#     except Exception as e:
#         st.error(f"Error saving users: {e}")
#         return False

# def hash_password(password):
#     """Hash password using SHA256."""
#     return hashlib.sha256(password.encode()).hexdigest()

# def verify_password(password, hashed_password):
#     """Verify password against hash."""
#     return hash_password(password) == hashed_password

# def create_user(username, password, email):
#     """Create a new user."""
#     users = load_users()
#     username = username.lower()
    
#     # Check if user already exists (case insensitive)
#     username_lower = username.lower()
#     email_lower = email.lower()
    
#     for existing_user in users.keys():
#         if existing_user.lower() == username_lower:
#             return False, "Username already exists"
    
#     # Check if email already exists (case insensitive)
#     for user_data in users.values():
#         if user_data.get('email', '').lower() == email_lower:
#             return False, "Email already exists"
    
#     # Create new user (store original case but check case insensitive)
#     users[username] = {
#         'password': hash_password(password),
#         'email': email,
#         'created_at': datetime.now().isoformat(),
#         'role': 'USER'
#     }
    
#     if save_users(users):
#         return True, "User created successfully"
#     else:
#         return False, "Error creating user"

# def authenticate_user(username, password):
#     """Authenticate user with username and password (case insensitive)."""
#     users = load_users()
#     username_lower = username.lower()
    
#     # Find user with case insensitive comparison
#     actual_username = None
#     for user in users.keys():
#         if user.lower() == username_lower:
#             actual_username = user
#             break
    
#     if not actual_username:
#         return False
    
#     return verify_password(password, users[actual_username]['password'])

# def get_user_info(username):
#     """Get user information (case insensitive)."""
#     users = load_users()
#     username_lower = username.lower()
    
#     # Find user with case insensitive comparison
#     for user, data in users.items():
#         if user.lower() == username_lower:
#             return data
#     return {}

# # --- FAQ and About Functions ---
# def load_faq_data():
#     """Load FAQ and About data from JSON file."""
#     try:
#         if os.path.exists(FAQ_FILE):
#             with open(FAQ_FILE, 'r') as f:
#                 return json.load(f)
#         else:
#             # Create default FAQ file if it doesn't exist
#             default_data = {
#                 "faqs": [
#                     {
#                         "question": "What is Gyaan Apps?",
#                         "answer": "Gyaan Apps is a comprehensive suite of AI-powered applications designed to enhance productivity and streamline various tasks."
#                     }
#                 ],
#                 "about": {
#                     "title": "About Gyaan",
#                     "content": "Gyaan is an innovative AI-powered platform developed by Team GYAAN."
#                 }
#             }
#             with open(FAQ_FILE, 'w') as f:
#                 json.dump(default_data, f, indent=2)
#             return default_data
#     except Exception as e:
#         st.error(f"Error loading FAQ data: {e}")
#         return {"faqs": [], "about": {"title": "About Gyaan", "content": "Content not available."}}

# # --- Reset Token Functions ---
# def load_reset_tokens():
#     """Load reset tokens from JSON file."""
#     try:
#         if os.path.exists(RESET_TOKENS_FILE):
#             with open(RESET_TOKENS_FILE, 'r') as f:
#                 return json.load(f)
#         return {}
#     except Exception as e:
#         st.error(f"Error loading reset tokens: {e}")
#         return {}

# def save_reset_tokens(tokens):
#     """Save reset tokens to JSON file."""
#     try:
#         with open(RESET_TOKENS_FILE, 'w') as f:
#             json.dump(tokens, f, indent=2)
#         return True
#     except Exception as e:
#         st.error(f"Error saving reset tokens: {e}")
#         return False

# def generate_reset_token(username):
#     """Generate a password reset token."""
#     token = secrets.token_urlsafe(32)
#     expiry = (datetime.now() + timedelta(hours=1)).isoformat()
    
#     tokens = load_reset_tokens()
#     tokens[token] = {
#         'username': username,
#         'expiry': expiry
#     }
    
#     if save_reset_tokens(tokens):
#         return token
#     return None

# def verify_reset_token(token):
#     """Verify and return username for reset token."""
#     tokens = load_reset_tokens()
    
#     if token not in tokens:
#         return None
    
#     token_data = tokens[token]
#     expiry = datetime.fromisoformat(token_data['expiry'])
    
#     if datetime.now() > expiry:
#         # Token expired, remove it
#         del tokens[token]
#         save_reset_tokens(tokens)
#         return None
    
#     return token_data['username']

# def reset_password(token, new_password):
#     """Reset user password using token."""
#     username = verify_reset_token(token)
#     if not username:
#         return False, "Invalid or expired token"
    
#     users = load_users()
#     if username not in users:
#         return False, "User not found"
    
#     # Update password
#     users[username]['password'] = hash_password(new_password)
    
#     # Remove used token
#     tokens = load_reset_tokens()
#     if token in tokens:
#         del tokens[token]
#         save_reset_tokens(tokens)
    
#     if save_users(users):
#         return True, "Password reset successfully"
#     else:
#         return False, "Error resetting password"

# # --- Token Generation Function ---
# def generate_user_token(username):
#     """Generate a secure token for user authentication."""
#     # print(username)
#     username = username.lower()
#     secret_key = "GYAAN_SECRET_KEY_2025"
#     token_string = f"{username}:{secret_key}"
#     # print(token_string)
#     token = hashlib.sha256(token_string.encode()).hexdigest()
#     timestamp = "STATIC"
#     # print("User data : ", username)
#     # print("Secreate key: ", secret_key)
#     # print("Generated Token = ", token)
#     return token, timestamp

# # --- Get Base64 Image Function ---
# def get_base64_image(image_path):
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     absolute_path = os.path.join(script_dir, image_path)
    
#     if not os.path.isfile(absolute_path):
#         parent_dir = os.path.dirname(script_dir)
#         absolute_path = os.path.join(parent_dir, image_path)
    
#     try:
#         with open(absolute_path, "rb") as img_file:
#             return base64.b64encode(img_file.read()).decode()
#     except FileNotFoundError:
#         placeholder = ""
#         return placeholder

# # --- Handle Login/Logout Logic ---
# def handle_logout():
#     # Clear session state
#     for key in ['user', 'token', 'ts', 'role']:
#         if key in st.session_state:
#             del st.session_state[key]
#     # Clear query params
#     st.query_params.clear()
#     st.session_state["show_login"] = False
#     st.session_state["show_signup"] = False
#     st.session_state["show_forgot_password"] = False
#     st.rerun()

# def handle_login_click():
#     st.session_state["show_login"] = True
#     st.session_state["show_signup"] = False
#     st.session_state["show_forgot_password"] = False
#     st.rerun()

# def handle_signup_click():
#     st.session_state["show_signup"] = True
#     st.session_state["show_login"] = False
#     st.session_state["show_forgot_password"] = False
#     st.rerun()

# def handle_forgot_password_click():
#     st.session_state["show_forgot_password"] = True
#     st.session_state["show_login"] = False
#     st.session_state["show_signup"] = False
#     st.rerun()

# def handle_login_submit(username, password):
#     if authenticate_user(username, password):
#         token, ts = generate_user_token(username)
        
#         # Get the actual username with correct case
#         users = load_users()
#         actual_username = None
#         for user in users.keys():
#             if user.lower() == username.lower():
#                 actual_username = user
#                 break
        
#         user_info = get_user_info(actual_username)
#         st.session_state['user'] = actual_username
#         st.session_state['token'] = token
#         st.session_state['ts'] = ts
#         st.session_state['role'] = user_info.get('role', 'USER')
#         st.session_state["show_login"] = False
#         # Update query params
#         st.query_params.update(user=actual_username, token=token, ts=ts)
#         st.success("Login successful!")
#         st.rerun()
#     else:
#         st.error("Invalid Creditinals or User Does not exist. Please click on singup if new user or click on Forgot password to rest your password.")

# def handle_signup_submit(username, password, confirm_password, email):
#     if password != confirm_password:
#         st.error("Passwords do not match.")
#         return
    
#     if len(password) < 6:
#         st.error("Password must be at least 6 characters long.")
#         return
    
#     success, message = create_user(username, password, email)
#     if success:
#         st.success(message)
#         st.info("You can now login with your credentials.")
#         st.session_state["show_signup"] = False
#         st.session_state["show_login"] = True
#         st.rerun()
#     else:
#         st.error(message)

# def handle_forgot_password_submit(username_or_email, new_password, confirm_password):
#     """Handle forgot password with direct password reset."""
#     if new_password != confirm_password:
#         st.error("Passwords do not match.")
#         return False
    
#     if len(new_password) < 6:
#         st.error("Password must be at least 6 characters long.")
#         return False
    
#     users = load_users()
#     username = None
#     username_or_email_lower = username_or_email.lower()
    
#     # Check if input is username or email (case insensitive)
#     for user, data in users.items():
#         if user.lower() == username_or_email_lower or data.get('email', '').lower() == username_or_email_lower:
#             username = user
#             break
    
#     if not username:
#         st.error("Username or email not found.")
#         return False
    
#     # Update password directly
#     users[username]['password'] = hash_password(new_password)
    
#     if save_users(users):
#         st.success("Password reset successfully! You can now login with your new password.")
#         return True
#     else:
#         st.error("Error resetting password.")
#         return False

# # --- Handle App Card Click ---
# def handle_app_click(link):
#     username = st.session_state.get('user', '')
#     if not username:
#         # User not logged in, show login form
#         st.session_state["show_login"] = True
#         st.rerun()
#     else:
#         # User logged in, redirect to app
#         token = st.session_state.get("token", "")
#         ts = st.session_state.get("ts", "")
#         separator = "&" if "?" in link else "?"
#         full_link = f"{link}{separator}user={username}&token={token}&ts={ts}"
#         st.markdown(f'<meta http-equiv="refresh" content="0; url={full_link}">', unsafe_allow_html=True)

# # --- Main App Layout ---

# # Top Bar with Login/User Info
# username = st.session_state.get('user', '')
# if username:
#     # User is logged in
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         st.markdown(f'<div class="user-info">👤 Welcome, {username}</div>', unsafe_allow_html=True)
#     with col2:
#         if st.button("Logout", key="logout_btn"):
#             handle_logout()
# else:
#     # User not logged in
#     col1, col2, col3 = st.columns([2, 1, 1])
#     with col1:
#         st.markdown('<div class="user-info">Welcome to Gyaan Apps</div>', unsafe_allow_html=True)
#     with col2:
#         if st.button("Login", key="login_btn"):
#             handle_login_click()
#     with col3:
#         if st.button("Sign Up", key="signup_btn"):
#             handle_signup_click()

# # Show login form
# if st.session_state.get("show_login", False) and not username:
#     st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Login</h2>", unsafe_allow_html=True)
    
#     with st.form("login_form"):
#         login_username = st.text_input("Username")
#         login_password = st.text_input("Password", type="password")
#         col1, col2, col3 = st.columns([1, 1, 1])
#         with col2:
#             submit_login = st.form_submit_button("Login", use_container_width=True)
        
#         if submit_login:
#             if login_username and login_password:
#                 handle_login_submit(login_username, login_password)
#             else:
#                 st.error("Please enter both username and password.")
    
#     col1, col2, col3 = st.columns([1, 1, 1])
#     with col1:
#         if st.button("Cancel", key="cancel_login"):
#             st.session_state["show_login"] = False
#             st.rerun()
#     with col2:
#         if st.button("Sign Up", key="goto_signup"):
#             handle_signup_click()
#     with col3:
#         if st.button("Forgot Password?", key="goto_forgot"):
#             handle_forgot_password_click()

# # Show signup form
# elif st.session_state.get("show_signup", False) and not username:
#     st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Sign Up</h2>", unsafe_allow_html=True)
    
#     with st.form("signup_form"):
#         signup_username = st.text_input("Username")
#         signup_email = st.text_input("Email")
#         signup_password = st.text_input("Password", type="password")
#         signup_confirm_password = st.text_input("Confirm Password", type="password")
#         col1, col2, col3 = st.columns([1, 1, 1])
#         with col2:
#             submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
        
#         if submit_signup:
#             if signup_username and signup_email and signup_password and signup_confirm_password:
#                 handle_signup_submit(signup_username, signup_password, signup_confirm_password, signup_email)
#             else:
#                 st.error("Please fill in all fields.")
    
#     col1, col2, col3 = st.columns([1, 1, 1])
#     with col1:
#         if st.button("Cancel", key="cancel_signup"):
#             st.session_state["show_signup"] = False
#             st.rerun()
#     with col2:
#         if st.button("Login", key="goto_login"):
#             handle_login_click()

# # Show forgot password form
# elif st.session_state.get("show_forgot_password", False) and not username:
#     st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Reset Password</h2>", unsafe_allow_html=True)
    
#     with st.form("forgot_password_form"):
#         username_or_email = st.text_input("Username or Email")
#         st.markdown("<br>", unsafe_allow_html=True)
#         new_password = st.text_input("New Password", type="password")
#         confirm_new_password = st.text_input("Confirm New Password", type="password")
#         col1, col2, col3 = st.columns([1, 1, 1])
#         with col2:
#             submit_reset = st.form_submit_button("Reset Password", use_container_width=True)
        
#         if submit_reset:
#             if username_or_email and new_password and confirm_new_password:
#                 if handle_forgot_password_submit(username_or_email, new_password, confirm_new_password):
#                     st.session_state["show_forgot_password"] = False
#                     st.session_state["show_login"] = True
#                     time.sleep(2)  # Small delay to show success message
#                     st.rerun()
#             else:
#                 st.error("Please fill in all fields.")
    
#     col1, col2, col3 = st.columns([1, 1, 1])
#     with col1:
#         if st.button("Cancel", key="cancel_forgot"):
#             st.session_state["show_forgot_password"] = False
#             st.rerun()
#     with col2:
#         if st.button("Login", key="goto_login_from_forgot"):
#             handle_login_click()

# else:
#     # Show main app content
#     # st.markdown('<div class="announcement">🔔 Latest updates and announcements will appear here</div>', unsafe_allow_html=True)
#     st.markdown("<h1 style='text-align: center;'>Gyaan Apps</h1>", unsafe_allow_html=True)

#     # App Cards
#     cards = [
#         {"name": "GYAAN CODER<br><span style='font-size:0.85em'>Gyaan Coder provides real-time answers and code solutions for user queries across any programming language.</span>", "img": "artifacts/coder.jpg", "link": "http://10.21.4.25:8502"},
#         {"name": "GYAAN DOC<br><span style='font-size:0.85em'>Gyaan Doc is an AI-powered app that lets you upload documents, get instant summaries, and ask questions based on their content.</span>", "img": "artifacts/doc.jpg", "link": "http://10.21.4.25:8503"},
#         {"name": "GYAAN MEETING<br><span style='font-size:0.85em'>Gyaan Meeting converts meeting audio into text, provides transcripts, and lets you query information directly from the conversation.</span>", "img": "artifacts/meeting.jpg", "link": "http://10.21.4.25:8504"},
#         {"name": "GYAAN ADMIN<br><span style='font-size:0.85em'>Gyaan Admin is a chatbot to streamline admin tasks and answer queries on operations, policies, and processes.</span>", "img": "artifacts/admin.png", "link": "http://10.21.4.25:8505"},
#         {"name": "GYAAN JITSI<br><span style='font-size:0.85em'>Gyaan Jitsi is an ai enabled meeting platform with meeting recording functionalities.Please upload recorded jitsi meetings to Gyaan Meeting</span>", "img": "artifacts/jitsi.png", "link": "https://gyaanjitsi.ursc.dos.gov.in/"},
#         {"name": "ELSIS<br><span style='font-size:0.85em'>ELSIS is a patented AI software designed to detect minute cracks in solar cells with unprecedented precision.</span>", "img": "artifacts/Gyaan_logo.jpeg", "link": "#"},
#         {"name": "Medical AI Doctor in Space<br><span style='font-size:0.85em'>MAIDS is a comprehensive medical assistant for astronauts, capable of diagnosing conditions and providing medicine recommendations with precise dosages using pharmacopoeia data</span>", "img": "artifacts/Gyaan_logo.jpeg", "link": "#"},
#         {"name": "Integrated Spacecraft Health Monitoring<br><span style='font-size:0.85em'> </span>", "img": "artifacts/Gyaan_logo.jpeg", "link": "#"},
#     ]

#     cols = st.columns(3)
    
#     for i, card in enumerate(cards):
#         with cols[i % 3]:
#             img_base64 = get_base64_image(card['img'])
            
#             # Display card content
#             card_html = f'''
#             <div class="stCard">
#                 <img src="data:image/jpeg;base64,{img_base64}" class="card-image">
#                 <p class="card-title">{card["name"]}</p>
#             </div>
#             '''
#             st.markdown(card_html, unsafe_allow_html=True)
            
#             # Add button below card for clicking
#             if card['name'].startswith('ELSIS') or card['name'].startswith('Medical AI Doctor in Space'):
#                 if st.button("Coming Soon", key=f"card_btn_{i}", 
#                             help=f"{card['name'].split('<')[0]} - Coming Soon",
#                             use_container_width=True,
#                             disabled=False):
#                     st.info("This app is coming soon!")
#                     pass  # Do nothing for coming soon apps
#             else:
#                 if st.button(f"Open {card['name'].split('<')[0]}", key=f"card_btn_{i}", 
#                             help=f"Click to open {card['name'].split('<')[0]}",
#                             use_container_width=True):
#                     if card['link'].startswith("http"):
#                         handle_app_click(card['link'])
#                     else:
#                         st.info("This app is coming soon!")

#     # About Gyaan Section
#     st.markdown("---")
#     faq_data = load_faq_data()
#     about_data = faq_data.get('about', {})
    
#     st.markdown(f"<h2 style='text-align: center; margin-top: 40px; color: #374151;'>{about_data.get('title', 'About Gyaan')}</h2>", unsafe_allow_html=True)
    
#     # Format the about content with proper line breaks
#     about_content = about_data.get('content', 'Content not available.')
#     about_content = about_content.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
#     st.markdown(f"""
#     <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: 20px 0; border: 1px solid #E5E7EB;'>
#         <div style='font-size: 1.1em; line-height: 1.6; color: #374151;'>
#             {about_content}
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # FAQ Section
#     st.markdown("---")
#     st.markdown("<h2 style='text-align: center; margin-top: 40px; color: #374151;'>Frequently Asked Questions</h2>", unsafe_allow_html=True)
    
#     faqs = faq_data.get('faqs', [])
    
#     if faqs:
#         for i, faq in enumerate(faqs):
#             with st.expander(faq['question'], expanded=False):
#                 st.write(faq['answer'])
#     else:
#         st.info("No FAQs available at the moment.")

# # Footer
# st.markdown("""
# <div class="footer">
#     <div class="footer-text">🚀 Built by Team GYAAN</div>
# </div>
# """, unsafe_allow_html=True)