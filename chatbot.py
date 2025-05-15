import streamlit as st

# Set page config at the very beginning of the script
st.set_page_config(page_title="Coding Chatbot", page_icon="🤖", layout="centered")

import sys
import os
from pathlib import Path
from urllib.parse import parse_qs
import hashlib
import time

# Fix the import by adding the parent directory to the path
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Now import the function from gyancoder
# from gyancoder import get_coding_response

import json
from datetime import datetime

# Token validation function
def validate_user_token(username, token, timestamp):
    """Validate the token received from apps.py."""
    if not all([username, token, timestamp]):
        return False
    
    try:
        # Secret key should match the one in apps.py
        secret_key = "GYAAN_SECRET_KEY_2023"
        # Check if token is expired (more than 2 hours old)
        current_hour = int(time.time() // 3600)
        token_hour = int(timestamp)
        if current_hour - token_hour > 2:  # 2-hour expiration
            return False
            
        # Recreate the token for verification
        token_string = f"{username}:{timestamp}:{secret_key}"
        expected_token = hashlib.sha256(token_string.encode()).hexdigest()
        
        # Compare the received token with the expected token
        return token == expected_token
    except Exception:
        return False

# Get username and token from URL parameter
def get_user_credentials_from_url():
    query_params = st.query_params
    username = query_params.get("user", "")
    token = query_params.get("token", "")
    timestamp = query_params.get("ts", "")
    
    # Validate the token
    is_valid = validate_user_token(username, token, timestamp)
    
    if not is_valid:
        return "guest"  # Return default username if validation fails
    return username

# Initialize session state variables at the very beginning
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'current_chat_id' not in st.session_state:
    st.session_state['current_chat_id'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = get_user_credentials_from_url()
if 'authenticated' not in st.session_state:
    # Check if the user is authenticated
    query_params = st.query_params
    username = query_params.get("user", "")
    token = query_params.get("token", "")
    timestamp = query_params.get("ts", "")
    st.session_state['authenticated'] = validate_user_token(username, token, timestamp)

# Function definitions
def get_user_chat_dir():
    """Create and return the user's chat directory path based on username."""
    username = st.session_state['username']
    chat_dir = Path(f"./user_chats/{username}")
    chat_dir.mkdir(parents=True, exist_ok=True)
    return chat_dir

def save_chat_history():
    """Save current chat history to a JSON file."""
    if not st.session_state['chat_history']:
        return
    
    user_dir = get_user_chat_dir()
    
    # Generate a unique filename if none exists
    if not st.session_state['current_chat_id']:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state['current_chat_id'] = f"chat_{timestamp}.json"
    
    chat_file = user_dir / st.session_state['current_chat_id']
    
    # Format messages for saving
    messages = st.session_state['chat_history']
    
    # Get the first user query as chat title
    first_query = ""
    for message in messages:
        if message[0] == "user":
            first_query = message[1]
            break
    
    # Save chat data
    chat_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "first_query": first_query,
        "messages": messages,
        "username": st.session_state['username']
    }
    
    with open(chat_file, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

def load_chat_histories():
    """Load all available chat histories for the user."""
    user_dir = get_user_chat_dir()
    chat_files = []
    
    if user_dir.exists():
        for filepath in user_dir.glob('*.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
                chat_files.append((filepath.name, chat_data))
    
    return sorted(chat_files, key=lambda x: x[0], reverse=True)

def delete_chat_history(chat_file):
    """Delete a specific chat history file."""
    user_dir = get_user_chat_dir()
    filepath = user_dir / chat_file
    
    if filepath.exists():
        filepath.unlink() 
        return True
    return False

def get_response(user_query):
    """Send user query to gyancoder.py and get model response."""
    return get_coding_response(user_query)

# Check authentication before displaying content
if not st.session_state['authenticated']:
    st.error("⛔ Invalid or expired authentication token. Please return to the main page and try again.")
    st.stop()  # Stop execution if not authenticated

col1, col2 = st.columns([5, 1])
with col1:
    st.title("🤖 Code Helper Bot")
with col2:
    if st.button("New Chat", key="clear_chat_btn"):
        if st.session_state['chat_history']:  
            save_chat_history()
        st.session_state['chat_history'] = []  
        st.session_state['current_chat_id'] = None

st.markdown("""
    <style>
    /* Hide default Streamlit sidebar navigation */
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Remove space above first element in sidebar (ISRO image) */
    section[data-testid="stSidebar"] > div:first-child > div:first-child {
        margin-top: -25px !important;
        padding-top: 0 !important;
    }
    
    /* More space reduction for sidebar elements */
    section[data-testid="stSidebar"] > div:first-child .element-container {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* More aggressive targeting of sidebar padding */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
    }
    
    section[data-testid="stSidebar"] img {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Sidebar image container */
    section[data-testid="stSidebar"] [data-testid="stImage"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    .user-message {
        background-color: #DCF8C6;
        border-radius: 12px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 70%;
        float: right;
        clear: both;
        color: black;
    }
    .bot-message {
        background-color: #F1F0F0;
        border-radius: 12px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 70%;
        float: left;
        clear: both;
        color: black;
    }

    /* Target only sidebar buttons using more specific selectors */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left !important;
        padding: 7px 8px !important;
        border: none;
        background-color: transparent;
        font-size: 13px;
        margin: 0 !important;
        line-height: 1.5;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        min-height: 0 !important;
        height: auto !important;
        border-radius: 6px !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button > div {
        text-align: left !important;
        display: inline-block;
        width: 100%;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #f0f2f6;
    }
    
    /* Additional spacing reduction for sidebar elements */
    section[data-testid="stSidebar"] .element-container {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
    section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    section[data-testid="stSidebar"] .st-emotion-cache-16idsys p {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
    }
    
    section[data-testid="stSidebar"] .stButton {
        margin-bottom: -10px !important;
        border-radius: 2px !important;
    }
    
    /* Style for delete button - modified to make it smaller */
    .delete-btn {
        color: #ff4b4b;
        background: none;
        border: none;
        cursor: pointer;
        float: right;
        padding: 0 3px;
        font-size: 12px;
        line-height: 1;
    }
    
    /* For the delete icon button in sidebar */
    section[data-testid="stSidebar"] .stButton:nth-child(2) > button {
        font-size: 10px !important;
        padding: 0 2px !important;
        min-width: 20px !important;
        height: 20px !important;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* Custom close button styling */
    .close-button {
        color: #777777 !important; /* Neutral gray color instead of red */
        font-size: 8px !important; /* Smaller font size */
        padding: 0 !important;
        min-width: 16px !important;
        height: 16px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        line-height: 1 !important;
    }
    
    /* Improved chat history row styling */
    .chat-history-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
    }
    
    /* Custom styling for sidebar column layout */
    section[data-testid="stSidebar"] div.row-widget.stHorizontal {
        display: flex;
        align-items: center;
        gap: 2px;
    }
    
    /* Chat history button in sidebar */
    section[data-testid="stSidebar"] div.row-widget.stHorizontal > div:first-child .stButton > button {
        padding: 2px 6px !important;
        min-height: 24px !important;
    }
    
    /* Delete button in sidebar */
    section[data-testid="stSidebar"] div.row-widget.stHorizontal > div:last-child .stButton > button {
        padding: 2px !important;
        min-height: 24px !important;
        min-width: 24px !important;
        width: 24px !important;
        height: 24px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-size: 12px !important;
        color: #777 !important;
    }
    
    .chat-title {
        flex-grow: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        left: 22%; /* Position after the sidebar (sidebar is typically ~22% of screen width) */
        right: 0;
        background-color: transparent;
        padding: 10px 0;
        text-align: center;
        font-size: 14px;
        color: #333;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 78%; /* Width should be 100% minus the sidebar width */
        margin-top: 20px;
        z-index: 100;
    }
    
    .footer-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    
    .footer-logo {
        height: 30px;
        width: auto;
    }
    
    .footer-text {
        font-weight: bold;
        margin: 0 10px;
    }
    
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='margin-top: 0px; margin-bottom: 10px;'>Previous Chats</h3>", unsafe_allow_html=True)

chat_histories = load_chat_histories()

if chat_histories:
    # Sort by timestamp in descending order
    sorted_histories = sorted(
        chat_histories,
        key=lambda x: x[1].get('timestamp', ''),
        reverse=True
    )
    
    for idx, (chat_file, chat_data) in enumerate(sorted_histories):
        col1, col2 = st.sidebar.columns([8, 1])  
        
        with col1:
            if st.button(
                f"{chat_data['first_query'][:30]}{'...' if len(chat_data['first_query']) > 30 else ''}",
                key=f"chat_history_{idx}",
                use_container_width=True
            ):
                st.session_state['chat_history'] = chat_data['messages']
                st.session_state['current_chat_id'] = chat_file
                st.rerun()
        
        with col2:
            if st.button("✕", key=f"delete_{idx}", help="Delete this chat history", 
                        type="secondary"):
                if delete_chat_history(chat_file):
                    st.success("Chat deleted")
                    st.rerun()
                else:
                    st.error("Failed to delete chat")
else:
    st.sidebar.info("No chat history available")

# Display welcome message if chat history is empty
if not st.session_state['chat_history']:
    st.markdown(
        f"<div class='bot-message'>"
        f"👋 Hi there, {st.session_state['username']}! I'm here to help you with coding—whether it's solving problems, building projects, or learning new languages. To get started, just type your question what you need help with, and I'll guide you through it!"
        "</div>", 
        unsafe_allow_html=True
    )

chat_container = st.container()
with chat_container:
    for message in st.session_state['chat_history']:
        role, text, code = message
        if role == "user":
            st.markdown(f"<div class='user-message'>{text}</div>", unsafe_allow_html=True)
        else:
            if code:
                st.markdown(f"<div class='bot-message'>{text}</div>", unsafe_allow_html=True)
                st.code(code, language="python")  
            else:
                st.markdown(text, unsafe_allow_html=False)  

st.markdown(f"""
    <div class="footer">
        <div class="footer-content">
            <div class="footer-text">🚀 Built by Team GYAAN | User: {st.session_state['username']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

user_input = st.chat_input("Ask me anything about coding...")

if user_input:
    st.session_state['chat_history'].append(("user", user_input, None))
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)

    # Get and display response from gyancoder.py
    bot_response = get_response(user_input)

    # Check if the response contains a code block
    if "```python" in bot_response and "```" in bot_response:
        # Extract the explanation and code block
        code_start = bot_response.find("```python") + 9
        code_end = bot_response.find("```", code_start)
        code_block = bot_response[code_start:code_end].strip()
        bot_message = bot_response.replace(f"```python\n{code_block}\n```", "").strip()

        # Add bot response to history with extracted code
        st.session_state['chat_history'].append(("assistant", bot_message, code_block))

        # Display explanation (if any) and code block
        if bot_message:
            st.markdown(bot_message, unsafe_allow_html=False)  
        st.code(code_block, language="python") 
    else:
        st.session_state['chat_history'].append(("assistant", bot_response, None))
        st.markdown(bot_response, unsafe_allow_html=False) 
    
    save_chat_history()
