import streamlit as st
# from helper_functions.tools import local_query_generator
import base64
import os
import hashlib
import time
from urllib.parse import parse_qs
import re
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import altair as alt

# Authentication functions
def get_url_params():
    """Extract URL query parameters from st.query_params"""
    # Streamlit's query_params provides direct access to parameters without indexing
    # They're attributes, not dictionary keys with arrays
    query_params = st.query_params
    user = query_params.get("user", "") if "user" in query_params else ""
    token = query_params.get("token", "") if "token" in query_params else ""
    timestamp = query_params.get("ts", "") if "ts" in query_params else ""
    return user, token, timestamp

def validate_token(username, token, timestamp):
    """Validate the token matches the username"""
    if not username or not token:
        return False
    try:
        # Remove timestamp/expiration check for static token
        secret_key = "GYAAN_SECRET_KEY_2025"
        token_string = f"{username}:{secret_key}"
        expected_token = hashlib.sha256(token_string.encode()).hexdigest()
        return token == expected_token
    except:
        return False

# Check authentication at the beginning
user, token, timestamp = get_url_params()
is_authenticated = validate_token(user, token, timestamp)

if not is_authenticated:
    st.error("⚠️ Authentication required. Please access this application through the main portal.")
    st.stop()

# Define some knowledge base configurations
knowledge_bases = {
    "Administration": {"color": "#FF6347", "variable": "./graphrag_admin"},
    "Purchase": {"color": "#4682B4", "variable": "./purchase"},
}

# Initialize session state for selected knowledge base, user input, and chat history
if 'selected_kb' not in st.session_state:
    st.session_state['selected_kb'] = "Administration"
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""
if 'submit_query' not in st.session_state:
    st.session_state['submit_query'] = False
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
# Add new session state variables for chat management
if 'username' not in st.session_state:
    st.session_state['username'] = user  # Use the authenticated username
if 'current_chat_id' not in st.session_state:
    st.session_state['current_chat_id'] = ""

# Function to change the selected knowledge base
def switch_kb(selected_kb):
    st.session_state['selected_kb'] = selected_kb

# Callback for handling input submission
def handle_input():
    if st.session_state['input_field'] != "":
        st.session_state['user_input'] = st.session_state['input_field']
        st.session_state['submit_query'] = True
        st.session_state['input_field'] = ""  # Clear the input field after submission

# Function to load and encode images
def get_image(path):
    try:
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except Exception as e:
        st.error(f"Could not load image from {path}: {str(e)}")
        return None

# Encode the logos
assets_dir = "assets"  # Update this path if your assets are stored elsewhere
gyaan_logo = get_image(os.path.join(assets_dir, "GYaan_logo.jpeg"))
ursc_logo = get_image(os.path.join(assets_dir, "ursc_light.png"))
isro_logo = get_image(os.path.join(assets_dir, "ISROLogo.png"))

# Custom CSS for styling
st.markdown("""
    <style>
    /* Main container layout */
    .main .block-container {
        padding-bottom: 100px !important;
    }
    
    /* Header logo container */
    .header-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
        padding-top: 20px;
    }
    
    /* Message styling */
    .chat-message {
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        width: 100%;
        box-sizing: border-box;
    }
    
    .user-message {
        background-color: #F0F7FF;
        border-left: 4px solid #3B82F6;
        margin-left: auto;
    }
    
    .assistant-message {
        background-color: #F0FDF4;
        border-left: 4px solid #10B981;
        margin-right: auto;
    }
    
    /* Chat input container fixed at bottom */
    .chat-input {
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        max-width: 800px;
        z-index: 100;
        background: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 15px 0;
        background-color: white;
        border-top: 1px solid #E2E8F0;
        z-index: 99;
    }
    
    .footer-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
    }
    
    .footer-text {
        margin: 0;
        padding: 0;
    }
    
    .footer-logo {
        height: 40px;
    }

    /* Align text to the left for chat title buttons in the sidebar */
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton button {
        text-align: left !important;
        /* The button itself is often a flex container, so align its items (like the text label) to the start */
        justify-content: flex-start !important; 
    }
    </style>
""", unsafe_allow_html=True)

# Define the chat history management functions before using them
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
        if message["role"] == "user":
            first_query = message["content"]
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

def get_user_stats():
    """Get statistics about users, questions, and answers."""
    users_dir = Path("./user_chats")
    if not users_dir.exists():
        return 0, 0, 0

    user_count = sum(1 for item in users_dir.iterdir() if item.is_dir())
    question_count = 0
    answer_count = 0

    for user_dir in users_dir.iterdir():
        if user_dir.is_dir():
            for chat_file in user_dir.glob('*.json'):
                try:
                    with open(chat_file, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                        messages = chat_data.get('messages', [])
                        for message in messages:
                            # message is a dict with "role" key
                            if message.get("role") == "user":
                                question_count += 1
                            elif message.get("role") == "assistant":
                                answer_count += 1
                except Exception:
                    continue

    return user_count, question_count, answer_count

def create_stats_chart():
    """Create a bar chart with user statistics (Interactions = max(questions, answers))."""
    user_count, question_count, answer_count = get_user_stats()
    interactions = max(question_count, answer_count)
    answer_pct = (answer_count / interactions * 100) if interactions else 0

    data = pd.DataFrame({
        'Category': ['Users', 'Interactions'],
        'Count': [user_count, interactions],
        'Extra': ['', f"{answer_pct:.1f}% answers"]
    })
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Category', title=None),
        y=alt.Y('Count:Q', title=None, axis=alt.Axis(format='d'), scale=alt.Scale(zero=True)),
        color=alt.Color('Category', legend=None, 
                      scale=alt.Scale(domain=['Users', 'Interactions'],
                                    range=['#4C72B0', '#55A868'])),
        tooltip=['Category', 'Count', alt.Tooltip('Extra', title='Answers %')]
    ).properties(
        height=200
    ).configure_title(
        fontSize=14,
        anchor='middle'
    )
    return chart

# Sidebar with title and knowledge base buttons
st.sidebar.title("Knowledge Bases")
if st.sidebar.button("Administration"):
    switch_kb("Administration")
if st.sidebar.button("Purchase"):
    switch_kb("Purchase")

# Add statistics chart to sidebar (move above chat history)
st.sidebar.markdown("---")
with st.sidebar.expander("📊 Platform Statistics", expanded=False):
    user_count, question_count, answer_count = get_user_stats()
    st.markdown(
        f"""
        <b>Users:</b> {user_count}<br>
        <b>Interactions:</b> {question_count}
        """,
        unsafe_allow_html=True
    )

# Add chat history section to sidebar (move below statistics)
st.sidebar.markdown("---")
# Place "Chat History" and "New Chat" button on the same row
chat_header_col1, chat_header_col2 = st.sidebar.columns([5, 1])
with chat_header_col1:
    st.markdown("<h3 style='margin-bottom:0.2rem;'>Chat History</h3>", unsafe_allow_html=True)
with chat_header_col2:
    st.button("➕", key="new_chat", help="New Chat", use_container_width=True)

# New chat button logic (keep outside columns for correct behavior)
if st.session_state.get("new_chat"):
    st.session_state['chat_history'] = []
    st.session_state['current_chat_id'] = ""
    st.rerun()

# Load and display available chat histories
chat_histories = load_chat_histories()
if chat_histories:
    for chat_file, chat_data in chat_histories:
        # Create a readable chat label
        chat_title = chat_data.get("first_query", "Untitled Chat")
        if len(chat_title) > 30:
            chat_title = chat_title[:27] + "..."
        # Display as a clickable button with a delete option, aligned horizontally
        chat_row_col1, chat_row_col2 = st.sidebar.columns([5, 1])
        with chat_row_col1:
            if st.button(f"{chat_title}", key=f"chat_{chat_file}", use_container_width=True):
                st.session_state['chat_history'] = chat_data.get("messages", [])
                st.session_state['current_chat_id'] = chat_file
                st.rerun()
        with chat_row_col2:
            if st.button("✖", key=f"del_{chat_file}"):
                delete_chat_history(chat_file)
                if st.session_state['current_chat_id'] == chat_file:
                    st.session_state['chat_history'] = []
                    st.session_state['current_chat_id'] = ""
                st.rerun()
else:
    st.sidebar.write("No previous chats")

# Add header with Gyaan logo
if gyaan_logo:
    st.markdown(f"""
        <div class="header-logo">
            <img src="data:image/jpeg;base64,{gyaan_logo}" style="max-height: 100px;" />
        </div>
    """, unsafe_allow_html=True)

# Get current knowledge base settings
current_kb = st.session_state['selected_kb']
kb_color = knowledge_bases[current_kb]["color"]
kb_variable = knowledge_bases[current_kb]["variable"]

# Main content area
st.markdown(f"<h2 style='color:{kb_color}'>Current: {current_kb}</h2>", unsafe_allow_html=True)

# Create a container for chat messages
chat_container = st.container()

with chat_container:
    # Display previous chat messages
    for message in st.session_state['chat_history']:
        if message["role"] == "user":
            st.markdown(f"""
                <div class="chat-message user-message">
                    <b>You:</b> {message["content"]}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message assistant-message">
                    <b>Assistant:</b> {message["content"]}
                </div>
            """, unsafe_allow_html=True)

# Process the query if submitted
if st.session_state['submit_query']:
    # Display user message
    st.markdown(f"""
        <div class="chat-message user-message">
            <b>You:</b> {st.session_state['user_input']}
        </div>
    """, unsafe_allow_html=True)
    
    # Add user message to chat history
    st.session_state['chat_history'].append({"role": "user", "content": st.session_state['user_input']})
    
    # Create a placeholder for the assistant's response
    response_placeholder = st.empty()
    
    # Show thinking animation
    response_placeholder.markdown("""
        <div class="chat-message assistant-message">
            <b>Assistant:</b> <div class="thinking">Thinking<span>.</span><span>.</span><span>.</span></div>
        </div>
        <style>
            .thinking span {
                opacity: 0;
                animation: dots 1.5s infinite;
            }
            .thinking span:nth-child(1) {
                animation-delay: 0s;
            }
            .thinking span:nth-child(2) {
                animation-delay: 0.5s;
            }
            .thinking span:nth-child(3) {
                animation-delay: 1s;
            }
            @keyframes dots {
                0% { opacity: 0; }
                50% { opacity: 1; }
                100% { opacity: 0; }
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize empty response
    response = ""
    
    # Rest of your streaming code remains the same
    for chunk in local_query_generator(query=st.session_state['user_input'], root=kb_variable):
        response += chunk
        # Update the message with the current response
        response_placeholder.markdown(
            f'<div class="chat-message assistant-message"><b>Gyaan:</b> {response}</div>',
            unsafe_allow_html=True
        )
    
    # Add assistant response to chat history
    st.session_state['chat_history'].append({"role": "assistant", "content": response})
    
    # Save chat history after each interaction
    save_chat_history()
    
    # Reset submission flag
    st.session_state['submit_query'] = False

# Add spacing before the input field
# st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)

# Create a container for the input field - positioned at the bottom
input_container = st.container()

# Apply custom styling to position the input field at the bottom
# st.markdown('<div class="chat-input">', unsafe_allow_html=True)
# Text input with on_change callback to handle Enter key press
st.text_input(
    "Enter your question:", 
    key="input_field", 
    on_change=handle_input
)


# Add footer with URSC and ISRO logos
st.markdown(f"""
    <div class="footer">
        <div class="footer-content">
            <img src="data:image/png;base64,{ursc_logo}" class="footer-logo" />
            <p class="footer-text">Built by Team GYAAN</p>
            <img src="data:image/png;base64,{isro_logo}" class="footer-logo" />
        </div>
    </div>
""", unsafe_allow_html=True)


