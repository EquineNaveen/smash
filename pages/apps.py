import streamlit as st
import base64
import os
import hashlib
import time

# --- Query Param Persistence ---
# Use only st.query_params for getting and setting query params
query_params = st.query_params
if "user" in query_params and "user" not in st.session_state:
    st.session_state["user"] = query_params["user"]
if "token" in query_params and "token" not in st.session_state:
    st.session_state["token"] = query_params["token"]
if "ts" in query_params and "ts" not in st.session_state:
    st.session_state["ts"] = query_params["ts"]

# --- Page Configuration ---
st.set_page_config(page_title="Home - Gyaan Apps", layout="wide")

# Hide sidebar, sidebar nav, sidebar arrow SVG, and sidebar collapse button
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    div[data-testid="stSidebarNav"] {display: none !important;}
    /* Hide sidebar arrow SVG by class and tag */
    svg.eyeqlp53.st-emotion-cache-1f3w014 {display: none !important;}
    /* Fallback: hide any SVG inside sidebar nav */
    [data-testid="stSidebarNav"] svg {display: none !important;}
    /* Hide sidebar collapse/expand button */
    button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;}
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
        margin: 0; /* Ensure no default body margin */
        padding: 0; /* Ensure no default body padding */
        padding-bottom: 0 !important; /* Force no bottom padding */
    }

    # Main Streamlit container
    [data-testid="stAppViewContainer"] > .main {
        min-height: 0 !important;
        height: auto !important;
        flex: unset !important;
        display: block !important;
        padding-bottom: 0 !important; /* Force no bottom padding */
        margin-bottom: 0 !important; /* Force no bottom margin */
    }

    /* Remove top padding from main block container */
    .block-container {
        padding-top: 0 !important;
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
        border-radius: 15px;
        box-shadow: 0 6px 10px rgba(17, 24, 39, 0.08);
        text-align: center;
        overflow: hidden;
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
        height: 100%;
        display: block;
        cursor: pointer;
        text-decoration: none;
        color: inherit;
        margin-bottom: 20px;
    }

    .stCard:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 20px rgba(17, 24, 39, 0.12);
        border-color: #6B7280;
    }

    .card-title {
        font-size: 1.25em;
        font-weight: 600;
        background: #4B5563;
        color: white;
        padding: 15px;
        margin: 0;
        text-align: center;
    }

    .card-image {
        width: 100%;
        padding: 15px;
        background: #F9FAFB;
        height: 200px;
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
        width: 100% !important;
        background: #fff !important;
        z-index: 9999 !important;
        margin-bottom: 0 !important; /* Ensure footer itself has no bottom margin */
    }

    .footer img {
        height: 35px;
        object-fit: contain;
    }

    .footer-text {
        font-weight: bold;
        color: #222; /* Ensure text is visible on white background */
        font-size: 1.1em; /* Slightly larger for clarity */
    }

    @keyframes slideDown {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    @keyframes pulse {
        0% { box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15); }
        50% { box-shadow: 0 4px 20px rgba(22, 163, 74, 0.25); }
        100% { box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15); }
    }

    /* Hide Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {
        height: 100vh !important;
        min-height: 100vh !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
        box-sizing: border-box;
    }
    .footer {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        position: fixed !important;
        left: 0 !important;
        bottom: 0 !important;
        width: 100% !important;
        background: #fff !important;
        z-index: 9999 !important;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- Announcement ---
st.markdown('<div class="announcement">🔔 Latest updates and announcements will appear here</div>', unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1 style='text-align: center;'>Gyaan Apps</h1>", unsafe_allow_html=True)

# Get username from session state and display it
username = st.session_state.get('user', '')

# Add this function to generate a secure token
def generate_user_token(username):
    """Generate a secure token for user authentication."""
    secret_key = "GYAAN_SECRET_KEY_2025"
    # Remove timestamp from token generation for static token
    token_string = f"{username}:{secret_key}"
    token = hashlib.sha256(token_string.encode()).hexdigest()
    # Still return a timestamp for compatibility, but it's not used for expiration
    timestamp = "STATIC"
    return token, timestamp

# If username is present, ensure token and ts are also in session state and update query params
if username:
    token, ts = generate_user_token(username)
    st.session_state["token"] = token
    st.session_state["ts"] = ts
    # Set query params so refreshes retain user, token, ts
    st.query_params.update(user=username, token=token, ts=ts)

# --- App Cards ---
cards = [
    {"name": "GYAAN CODER<br><span style='font-size:0.85em'>Gyaan Coder provides real-time answers and code solutions for user queries across any programming language.</span>", "img": "artifacts/1.jpg", "link": "http://192.168.31.13:8502"},
    {"name": "GYAAN DOC<br><span style='font-size:0.85em'>Gyaan Doc is an AI-powered app that lets you upload documents, get instant summaries, and ask questions based on their content.</span>", "img": "artifacts/doc.jpg", "link": "#"},
    {"name": "GYAAN MEETING<br><span style='font-size:0.85em'>Gyaan Meeting converts meeting audio into text, provides transcripts, and lets you query information directly from the conversation.</span>", "img": "artifacts/meeting.jpg", "link": "#"},
    {"name": "GYAAN ADMIN<br><span style='font-size:0.85em'>Gyaan Admin is a chatbot to streamline admin tasks and answer queries on operations, policies, and processes.</span>", "img": "artifacts/admin.png", "link": "#"},
]

def get_base64_image(image_path):
    # Use absolute path relative to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(script_dir, image_path)
    
    # Try with parent directory if not found (common case)
    if not os.path.isfile(absolute_path):
        parent_dir = os.path.dirname(script_dir)
        absolute_path = os.path.join(parent_dir, image_path)
    
    try:
        with open(absolute_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        # Return a base64 for a placeholder image if file not found
        placeholder = "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAMAAABOo35HAAAAQlBMVEX19fXt7e3v7+/5+fn9/f3x8fH7+/vr6+vz8/Pn5++fh4eHp6enZ2dnd3d3T09PS0tLPz8/Ly8vKysrFxcXHx8fBwcEXIuXuAAAEIUlEQVR4nO3a23KrIBSAYUDF+6H6/s/agGlrPCSNY8E15v9G47Rj2H4IKjtNU1VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUN0TjmSQ9j7vo4YxhH1HV31ylRARuEHfqmS8amYcS4T8OIptQEWYZZHnWNyaSmiqqZKrDICiyxHotyxMos2LgYhZXGciVYtuXXXLkoUjXmLGGhXcbKLMX9t8eyXOyIxd7+FCmb5oKJ1lgy0+wbcCdlpC6w4jCu6imm1GJJzcR602pFZfexGBnlzShr7WW1WEE5XX/gyqr1hBarcpoTrNXL8QlWWANykmXF1b8+FuUzVAn3X/EjluKDwUXBHaxur1HMeZZZ3xvd7kV5l5XD8wEWz7PQbuwMZ9HY81yyZNXsrkpxYVRKlspmzkMvxQx8ypKd4lorJQYvsiTH1mryXTKfDJan0c7nec8mgjX4PNvZHEXrFAsXteIeV2KtWLiU9vpFhY3C9mWdWbig7bJ3PgTvFlnVRTCLxV4+flBh7SwWe+1epwKLXQdjVlg3+o0XTqywTPC+itVtLLcRrLBKXVnGrtv7C/cBq/iYKbD88p2Y62+vc1hmqxvdV9cGZimYjhtY4R7vA4v1S6zXvj0+t5lcWO/fkWa+iBGco/Os1hxXdtGu7TBoo7iR5dZBGCzjsMhqiOSgel7G8sdfn1jsfxZNuysZrYYIcwOLLPm95v0k8BirSYos+SWco7rtDKvLmM7EkZc35zJ+mGOxLBXFsXyvWLAmuT5UG4u6cHvihmX7JTqDlfNTS7uzHksKZdvAclRdyLGRFTpFizGXFlwJrElyAlboFLVpU1pwJbBOq8xqdb8iVrgtNw15wZVY/P0UWZo6N69NsPkP1iYWUnKjl1hrykuuWSz3AEtYnFMP7r41L4lFPh6Cydyfbk4s+vEQzH73PrOaSyzaMbhf93KLWMST5Kk2mRb1JHmqdpZYfPdIYGZf8MQKdXu+7kxSPUEfajNp9Ym1+bpDrZQfs+a9p7/s85DKhWFpoT1zmVcvdrXAYrxrZbDeCnHfuPh3FttZ+/Ya65Jp2OIQHHfWvk3WnJ9O1jtry6aw9nxdj+bh9+lksSfWSyzC53PG3glKA0v3oZjf4dk8pBplcjM1s/ILdGGFlnMcZWRtcAWWG+ZiF8JJ5md/XmO5lJX5MSb+PkOucnZa8rsfTJ6CGgveHkp5ea7XeGnPq8Ty85v3NZu8aDnLX1eIy9ynp+0uTYlp2KXHyb3VLI/FfJh8Wlq5Jid7c1NokweBzXvBWGKRTMQ/lL1vOPTz8O/F9wUXuDzse6g07RrDQu1m9C+1D0Yd+F1jVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVdKf1VIv05ellcsAAAAASUVORK5CYII="
        return placeholder

# Create columns for cards - using Streamlit's column system instead of HTML grid
cols = st.columns(3)  # Adjust the number based on how many cards you want per row

# Render Cards as clickable elements
for i, card in enumerate(cards):
    with cols[i % 3]:  # This distributes cards across columns
        img_base64 = get_base64_image(card['img'])
        # Add username to links that start with http
        link = card['link']
        if link.startswith("http"):
            # Generate token for authenticated access
            token = st.session_state.get("token", "")
            ts = st.session_state.get("ts", "")
            # Properly format the URL with username parameter and token
            separator = "&" if "?" in link else "?"
            if username:
                link = f"{link}{separator}user={username}&token={token}&ts={ts}"
            
        # Debug information to verify link construction (can be removed in production)
        st.markdown(f"<div style='display:none;'>{link}</div>", unsafe_allow_html=True)
        
        # Open external links in a new tab
        target = "_blank" if link.startswith("http") else "_self"
        card_html = f'''
        <a href="{link}" class="stCard" target="{target}">
            <img src="data:image/jpeg;base64,{img_base64}" class="card-image">
            <p class="card-title">{card["name"]}</p>
        </a>
        '''
        st.markdown(card_html, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer">
    <div class="footer-text">🚀 Built by Team GYAAN</div>
</div>
""", unsafe_allow_html=True)
