import streamlit as st
from helper_functions.tools import local_query_generator
import base64
import os
import uuid
import datetime

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
# Chat history management
if 'conversations' not in st.session_state:
    st.session_state['conversations'] = []
if 'current_conversation_id' not in st.session_state:
    st.session_state['current_conversation_id'] = None

# Function to change the selected knowledge base
def switch_kb(selected_kb):
    st.session_state['selected_kb'] = selected_kb

# Function to create a new conversation
def create_new_conversation():
    conversation_id = str(uuid.uuid4())
    current_date = datetime.datetime.now().strftime("%b %d")
    
    new_conversation = {
        "id": conversation_id,
        "title": "New conversation",
        "date": current_date,
        "messages": []
    }
    
    st.session_state['conversations'].append(new_conversation)
    st.session_state['current_conversation_id'] = conversation_id
    st.session_state['chat_history'] = []
    
    return conversation_id

# Function to select an existing conversation
def select_conversation(conversation_id):
    # Save current conversation messages
    if st.session_state['current_conversation_id']:
        for conv in st.session_state['conversations']:
            if conv["id"] == st.session_state['current_conversation_id']:
                conv["messages"] = st.session_state['chat_history']
                break
    
    # Load selected conversation
    st.session_state['current_conversation_id'] = conversation_id
    for conv in st.session_state['conversations']:
        if conv["id"] == conversation_id:
            st.session_state['chat_history'] = conv["messages"]
            break

# Function to delete a conversation
def delete_conversation(conversation_id):
    st.session_state['conversations'] = [c for c in st.session_state['conversations'] if c["id"] != conversation_id]
    
    # If the deleted conversation was the current one, create a new conversation
    if conversation_id == st.session_state['current_conversation_id']:
        create_new_conversation()

# Function to rename a conversation
def rename_conversation(conversation_id, new_title):
    for conv in st.session_state['conversations']:
        if conv["id"] == conversation_id:
            conv["title"] = new_title
            break

# Initialize with a conversation if none exists
if not st.session_state['current_conversation_id'] and len(st.session_state['conversations']) == 0:
    create_new_conversation()

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
    
    /* Chat history sidebar styling */
    .chat-history {
        margin-bottom: 20px;
    }
    
    .history-title {
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 1.2em;
    }
    
    .conversation-item {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: background-color 0.2s ease;
        border: 1px solid transparent;
        position: relative;
    }
    
    .conversation-item:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
    
    .conversation-item.active {
        border-color: #3B82F6;
        background-color: rgba(59, 130, 246, 0.1);
    }
    
    .conversation-title {
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .conversation-date {
        font-size: 0.8em;
        color: #666;
        margin-top: 2px;
    }
    
    .delete-btn {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0;
        transition: opacity 0.2s;
        color: #666;
        background: none;
        border: none;
        cursor: pointer;
        font-size: 16px;
        padding: 0;
    }
    
    .conversation-item:hover .delete-btn {
        opacity: 1;
    }
    
    .delete-btn:hover {
        color: #f44336;
    }
    
    .new-chat-btn {
        width: 100%;
        background-color: #3B82F6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 15px;
        cursor: pointer;
        transition: background-color 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .new-chat-btn:hover {
        background-color: #2563EB;
    }
    
    /* Divider */
    .section-divider {
        border-top: 1px solid #e0e0e0;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar with title and knowledge base buttons
with st.sidebar:
    # New Chat button - styled as a blue button
    if st.button("➕ New chat", key="new_chat_button_blue", use_container_width=True, 
                type="primary", help="Start a new conversation"):
        create_new_conversation()
    
    # Chat History
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    st.markdown('<div class="history-title">Chat History</div>', unsafe_allow_html=True)
    
    # List conversations
    for i, conv in enumerate(st.session_state['conversations']):
        is_active = conv["id"] == st.session_state['current_conversation_id']
        
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            if st.button(
                f"{conv['title']}",
                key=f"conv_{i}",
                help=f"Conversation from {conv['date']}",
                use_container_width=True
            ):
                select_conversation(conv["id"])
                
        with col2:
            if st.button("🗑️", key=f"del_{i}", help="Delete this conversation"):
                delete_conversation(conv["id"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
    
    # Knowledge Bases
    st.subheader("Knowledge Bases")
    if st.button("Administration", use_container_width=True):
        switch_kb("Administration")
    if st.button("Purchase", use_container_width=True):
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
        
        # Update conversation in the conversations list
        for conv in st.session_state['conversations']:
            if conv["id"] == st.session_state['current_conversation_id']:
                conv["messages"] = st.session_state['chat_history']
                # Update title with first user message if it's still the default
                if conv["title"] == "New conversation" and len(st.session_state['chat_history']) > 0:
                    for msg in st.session_state['chat_history']:
                        if msg["role"] == "user":
                            conv["title"] = (msg["content"][:25] + "...") if len(msg["content"]) > 25 else msg["content"]
                            break
                break
        
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


