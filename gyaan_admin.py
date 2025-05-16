import streamlit as st
from helper_functions.tools import local_query_generator
import base64
import os
import hashlib
import time
from urllib.parse import parse_qs
import re

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
    """Validate the token matches the username and is not expired"""
    if not username or not token or not timestamp:
        return False
    
    try:
        # Convert timestamp to int and check expiration (24 hour validity)
        ts = int(timestamp)
        current_ts = int(time.time() // 3600)
        if current_ts - ts > 24:  # Token expired after 24 hours
            return False
            
        # Recreate token for validation using same logic as in apps.py
        secret_key = "GYAAN_SECRET_KEY_2025"
        token_string = f"{username}:{timestamp}:{secret_key}"
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
        max-width: 85%;
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
    </style>
""", unsafe_allow_html=True)

# Sidebar with title and knowledge base buttons
st.sidebar.title("Knowledge Bases")
if st.sidebar.button("Administration"):
    switch_kb("Administration")
if st.sidebar.button("Purchase"):
    switch_kb("Purchase")

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


