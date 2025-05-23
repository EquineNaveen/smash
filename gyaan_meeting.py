import streamlit as st
import os
import time
from datetime import datetime
import json
from pathlib import Path
from video_to_text.transcription import transcribe_video
import asyncio
import aiohttp
from typing import List, AsyncGenerator
import textwrap
import logging
import base64
from transcript_cleaner import TranscriptCleaner
import nest_asyncio
import re
import hashlib
nest_asyncio.apply()


# Authentication functions
def get_url_params():
    """Extract URL query parameters from st.query_params"""
    # Get query_params and handle them correctly
    query_params = st.query_params
    user = query_params.get("user", [""])[0] if isinstance(query_params.get("user"), list) else query_params.get("user", "")
    token = query_params.get("token", [""])[0] if isinstance(query_params.get("token"), list) else query_params.get("token", "")
    timestamp = query_params.get("ts", [""])[0] if isinstance(query_params.get("ts"), list) else query_params.get("ts", "")
    return user, token, timestamp

def validate_token(username, token, timestamp):
    """Validate the token matches the username"""
    if not username or not token:
        st.error(f"Missing authentication parameters: user={username}, token={token[:10]}..., ts={timestamp}")
        return False
    try:
        # Remove timestamp/expiration check for static token
        secret_key = "GYAAN_SECRET_KEY_2025"
        token_string = f"{username}:{secret_key}"
        expected_token = hashlib.sha256(token_string.encode()).hexdigest()
        if token != expected_token:
            st.error(f"Token mismatch: expected={expected_token[:10]}..., got={token[:10]}...")
        return token == expected_token
    except Exception as e:
        st.error(f"Error validating token: {str(e)}")
        return False

# Check authentication at the beginning
user, token, timestamp = get_url_params()
is_authenticated = validate_token(user, token, timestamp)

if not is_authenticated:
    st.error("⚠️ Authentication required. Please access this application through the main portal.")
    st.stop()

logger = logging.getLogger(__name__)

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


# Constants for token limits
MAX_INPUT_TOKENS = 8000
MAX_CHUNK_SIZE = 4000

# Add new constants for UI
SIDEBAR_WIDTH = 300
TRANSCRIPT_PREVIEW_LENGTH = 50  # Characters to show in sidebar

def estimate_tokens(text: str) -> int:
    return len(text) // 4

def chunk_text(text: str) -> List[str]:
    chunks = textwrap.wrap(text, width=MAX_CHUNK_SIZE, break_long_words=False, break_on_hyphens=False)
    return chunks

def truncate_text(text: str, max_length: int) -> str:
    """Helper function to truncate text with ellipsis"""
    return text[:max_length] + "..." if len(text) > max_length else text

def get_navigation_html():
    """Helper function to generate navigation HTML"""
    return """
        <style>
        .nav-button {
            background-color: #1e3d59;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin: 0 10px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .nav-button:hover {
            background-color: #2b5480;
            transform: scale(1.05);
        }
        
        .nav-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        </style>
    """

def add_sidebar_navigation(current_page):
    st.sidebar.markdown("### 🧭 Navigation")
    
    if current_page == "transcribe":
        if st.sidebar.button("🏠 Go to Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
        if st.sidebar.button("💬 Go to Chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
        if st.sidebar.button("🏢 Conference Transcripts", use_container_width=True):
            st.session_state.page = "conference"
            st.rerun()
    
    elif current_page == "chat":
        if st.sidebar.button("🏠 Go to Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
        if st.sidebar.button("📝 Go to Transcribe", use_container_width=True):
            st.session_state.page = "transcribe"
            st.rerun()
        if st.sidebar.button("🏢 Conference Transcripts", use_container_width=True):
            st.session_state.page = "conference"
            st.rerun()
    
    elif current_page == "conference":
        if st.sidebar.button("🏠 Go to Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
        if st.sidebar.button("📝 Go to Transcribe", use_container_width=True):
            st.session_state.page = "transcribe"
            st.rerun()
        if st.sidebar.button("💬 Go to Chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    
    st.sidebar.markdown("---")


async def custom_llm_complete(prompt: str, max_tokens: int = 1000):
    """Async function to communicate with LLM API"""
    url = "http://localhost:9000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "ibnzterrell/Meta-Llama-3.3-70B-Instruct-AWQ-INT4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.4,
        "top_p": 0.95,
        "n": 1,
        "stream": True
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                line = line.decode('utf-8').strip()
                                if line.startswith("data: "):
                                    json_line = json.loads(line[6:])
                                    if 'choices' in json_line and len(json_line['choices']) > 0:
                                        chunk = json_line['choices'][0].get('delta', {}).get('content', '')
                                        if chunk:
                                            yield chunk
                            except:
                                continue
                else:
                    raise Exception(f"Error: {response.status}, {await response.text()}")
    except Exception as e:
        st.error(f"Error connecting to LLM: {str(e)}")
        yield "Error: Could not connect to LLM service"

async def get_full_response(prompt: str) -> str:
    """Get complete response from LLM"""
    full_response = ""
    try:
        async for chunk in custom_llm_complete(prompt):
            full_response += chunk
        return full_response
    except Exception as e:
        st.error(f"Error getting response from LLM: {str(e)}")
        return "Error generating response"

async def process_large_transcript(transcript: str, prompt_template: str) -> str:
    """Process large transcripts in chunks and combine responses"""
    chunks = chunk_text(transcript)
    responses = []
    
    progress_bar = st.progress(0)
    for i, chunk in enumerate(chunks):
        chunk_prompt = prompt_template.format(transcript=chunk)
        chunk_response = await get_full_response(chunk_prompt)
        responses.append(chunk_response)
        
        # Update progress
        progress = (i + 1) / len(chunks)
        progress_bar.progress(progress)
    
    # Combine responses
    combined_response = " ".join(responses)
    
    # If multiple chunks, generate a final summary
    if len(chunks) > 1:
        final_summary_prompt = f"Summarize the following points into a coherent response:\n{combined_response}"
        combined_response = await get_full_response(final_summary_prompt)
    
    return combined_response

def create_system_prompt(transcript: str) -> str:
    return f"""You are an AI assistant analyzing a meeting transcript. Your role is to provide accurate and relevant information based solely on the content of the transcript. Here's the transcript:

{transcript}

Please provide clear, concise answers based only on the information contained in this transcript. If a question cannot be answered using the transcript content, please indicate that."""


def load_css():
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 5px;
            color: #1e3d59;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e9ecef;
            color: #1e3d59;
        }
        
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            animation: fadeIn 0.5s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .transcript-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stTextInput > div > div > input {
            background-color: white;
            padding: 10px 15px;
            border-radius: 5px;
            border: 1px solid #dee2e6;
        }
        
        .stSpinner {
            text-align: center;
            padding: 20px;
        }
        
        .stButton > button {
            background-color: #1e3d59;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #2b5480;
            transform: translateY(-2px);
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
        
        .transcript-item {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            transition: all 0.3s ease;
        }
        
        .transcript-item:hover {
            background-color: #e9ecef;
            border-color: #1e3d59;
            transform: translateX(5px);
        }
        
        .summary-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
                
        .mom-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .user-message {
            background-color: #e3f2fd;
            margin-left: 20%;
            border-left: 4px solid #1e3d59;
        }
        
        .assistant-message {
            background-color: #f5f5f5;
            margin-right: 20%;
            border-right: 4px solid #1e3d59;
        }
        
        .transcript-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        
        .processing-step {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        
        .step-complete {
            color: #28a745;
        }
        
        .step-error {
            color: #dc3545;
        }
        
        /* Conference card styling */
        .conference-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .conference-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            border-color: #1e3d59;
        }
        
        .conference-date {
            color: #1e3d59;
            font-weight: bold;
        }
        
        .conference-time {
            color: #555;
        }
        
        .conference-duration {
            color: #777;
            font-style: italic;
        }
        
        .conference-speakers {
            color: #1e3d59;
            margin-top: 5px;
        }
        
        /* Conference metrics */
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #dee2e6;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #1e3d59;
            margin: 10px 0;
        }
        
        .metric-label {
            color: #555;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

def add_footer():
    st.markdown(f"""
        <div class="footer">
            <div class="footer-content">
                <img src="data:image/png;base64,{ursc_logo}" class="footer-logo" />
                <p class="footer-text">Built by Team GYAAN</p>
                <img src="data:image/png;base64,{isro_logo}" class="footer-logo" />
            </div>
        </div>
    """, unsafe_allow_html=True)



class TranscriptionApp:
    def __init__(self):
        self.base_dir = Path("data")
        self.uploads_dir = self.base_dir / "uploads"
        # Convert string paths to Path objects
        self.transcripts_dir = Path("conference_transcripts")
        self.conference_dir = Path("conference_transcripts")
        self.initialize_directories()

    def initialize_directories(self):
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.conference_dir.mkdir(parents=True, exist_ok=True)

    def save_uploaded_file(self, uploaded_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.uploads_dir / f"{timestamp}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path

    def get_transcript_path(self, video_filename):
        base_name = Path(video_filename).stem
        return self.transcripts_dir / f"{base_name}_transcript.txt"

    def get_all_transcripts(self):
        transcripts = []
        for file in self.transcripts_dir.glob("*_transcript.txt"):
            try:
                with open(file, "r", encoding='utf-8') as f:
                    content = f.read()
                    
                    # Split content into sections
                    main_parts = content.split("=== Complete Transcript ===")
                    main_transcript = main_parts[0].strip()
                    complete_transcript = main_parts[1].strip() if len(main_parts) > 1 else main_transcript
                    
                    # Extract summary if exists
                    summary_parts = complete_transcript.split("### SUMMARY ###")
                    complete_transcript = summary_parts[0].strip()
                    summary = summary_parts[1].strip() if len(summary_parts) > 1 else None
                    
                    # Extract MoM if exists
                    mom_parts = complete_transcript.split("### MINUTES OF MEETING ###")
                    complete_transcript = mom_parts[0].strip()
                    mom = mom_parts[1].strip() if len(mom_parts) > 1 else None
                
                transcripts.append({
                    "name": file.stem,
                    "path": file,
                    "content": main_transcript,
                    "complete_transcript": complete_transcript,
                    "summary": summary,
                    "mom": mom,
                    "date": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                logger.error(f"Error reading transcript {file}: {str(e)}")
                continue
                    
        return sorted(transcripts, key=lambda x: x["date"], reverse=True)
    
    def get_all_conference_transcripts(self):
        """Get all conference transcripts from the conference_transcripts folder"""
        conference_transcripts = []
        for file in Path(self.conference_dir).glob("*.txt"):
            try:
                # Skip files that end with "_transcript.txt" as they're processed differently
                if file.name.endswith("_transcript.txt"):
                    continue
                    
                with open(file, "r", encoding='utf-8') as f:
                    content = f.read()
                    
                    # Parse metadata from the file content
                    date = "Unknown"
                    time_range = "Unknown"
                    duration = "Unknown"
                    num_speakers = "Unknown"
                    
                    metadata_match = re.search(r"Date: (.*?)\nTime: (.*?)\nDuration: (.*?)\nNumber of Speakers: (.*?)\n", content)
                    if metadata_match:
                        date = metadata_match.group(1)
                        time_range = metadata_match.group(2)
                        duration = metadata_match.group(3)
                        num_speakers = metadata_match.group(4)
                    
                    # Split content into sections
                    cleaned_parts = content.split("=== Cleaned Transcript ===")
                    cleaned_transcript = cleaned_parts[1].split("=== Complete Transcript ===")[0].strip() if len(cleaned_parts) > 1 else ""
                    
                    complete_parts = content.split("=== Complete Transcript ===")
                    complete_transcript = complete_parts[1].strip() if len(complete_parts) > 1 else content
                    
                    # Create a human-readable display name
                    display_name = file.name
                    if display_name.startswith("Conference_"):
                        # Format: Conference_2025-04-30_17:31:28-22:30:58.txt
                        # Transform to: Conference on April 30, 2025 (17:31-22:30)
                        name_parts = display_name.replace(".txt", "").split("_")
                        if len(name_parts) >= 2:
                            try:
                                date_obj = datetime.strptime(date, "%Y-%m-%d")
                                formatted_date = date_obj.strftime("%B %d, %Y")
                                time_parts = time_range.split("-")
                                short_time = f"{time_parts[0].split(':')[0]}:{time_parts[0].split(':')[1]}-{time_parts[1].split(':')[0]}:{time_parts[1].split(':')[1]}"
                                display_name = f"Conference on {formatted_date} ({short_time})"
                            except:
                                # If parsing fails, use the original filename
                                pass
                
                conference_transcripts.append({
                    "name": display_name,
                    "filename": file.name,
                    "path": file,
                    "date": date,
                    "time_range": time_range,
                    "duration": duration,
                    "num_speakers": num_speakers,
                    "cleaned_transcript": cleaned_transcript,
                    "complete_transcript": complete_transcript,
                    "file_date": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                logger.error(f"Error reading conference transcript {file}: {str(e)}")
                continue
                    
        return sorted(conference_transcripts, key=lambda x: x["date"], reverse=True)

    def process_video(self, video_path):
        transcript_path = self.get_transcript_path(video_path.name)
        
        # Show processing steps
        steps = st.empty()
        steps.markdown("""
        <div class='processing-steps'>
            <div class='processing-step'>
                <span class='step-icon'>⚙️</span>
                <span>Initializing transcription...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Transcribe video
        transcribe_video(str(video_path), str(transcript_path))
        
        steps.markdown("""
        <div class='processing-steps'>
            <div class='processing-step step-complete'>
                <span class='step-icon'>✅</span>
                <span>Transcription complete</span>
            </div>
            <div class='processing-step'>
                <span class='step-icon'>🧠</span>
                <span>Cleaning transcript with GYAAN AI...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Clean transcript
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            
            cleaner = TranscriptCleaner()
            cleaned_data = asyncio.run(cleaner.clean_transcript(transcript_text))
            
            # Save cleaned transcript
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_data["cleaned_transcript"])
                f.write("\n\n=== Complete Transcript ===\n")
                f.write(cleaned_data["complete_transcript"])
            
            steps.markdown("""
            <div class='processing-steps'>
                <div class='processing-step step-complete'>
                    <span class='step-icon'>✅</span>
                    <span>Transcription complete</span>
                </div>
                <div class='processing-step step-complete'>
                    <span class='step-icon'>✅</span>
                    <span>Transcript cleaned and enhanced</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error cleaning transcript: {str(e)}")
            steps.markdown("""
            <div class='processing-steps'>
                <div class='processing-step step-complete'>
                    <span class='step-icon'>✅</span>
                    <span>Transcription complete</span>
                </div>
                <div class='processing-step step-error'>
                    <span class='step-icon'>❌</span>
                    <span>Error cleaning transcript</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        return transcript_path


    def save_summary(self, transcript_path: Path, summary: str):
        with open(transcript_path, "r") as f:
            content = f.read()
            # Check if summary already exists
            if "### SUMMARY ###" not in content:
                with open(transcript_path, "w") as f:
                    f.write(f"{content}\n\n### SUMMARY ###\n{summary}")

    def save_mom(self, transcript_path: Path, mom: str):
        """Save minutes of meeting to transcript file"""
        try:
            with open(transcript_path, "r", encoding='utf-8') as f:
                content = f.read()
                
            if "### MINUTES OF MEETING ###" not in content:
                with open(transcript_path, "w", encoding='utf-8') as f:
                    f.write(f"{content}\n\n### MINUTES OF MEETING ###\n{mom}")
            else:
                parts = content.split("### MINUTES OF MEETING ###")
                with open(transcript_path, "w", encoding='utf-8') as f:
                    f.write(f"{parts[0]}\n\n### MINUTES OF MEETING ###\n{mom}")
                    
        except Exception as e:
            logger.error(f"Error saving minutes of meeting: {str(e)}")
            raise


def conference_page(app):
    st.markdown("<h2 class='section-header'>Conference Hall Transcripts</h2>", unsafe_allow_html=True)
    
    # Add navigation
    st.markdown(get_navigation_html(), unsafe_allow_html=True)
    add_sidebar_navigation("conference")
    
    # Sidebar for transcript selection
    with st.sidebar:
        st.markdown("<h3>🏢 Conference Transcripts</h3>", unsafe_allow_html=True)
        
        # Get all conference transcripts
        conference_transcripts = app.get_all_conference_transcripts()
        
        if not conference_transcripts:
            st.warning("No conference transcripts available.")
            return
        
        # Add search box for transcripts
        search_term = st.text_input("🔍 Search conferences", "")
        
        filtered_transcripts = conference_transcripts
        if search_term:
            filtered_transcripts = [t for t in conference_transcripts 
                                  if search_term.lower() in t["name"].lower() 
                                  or search_term.lower() in t["date"].lower()
                                  or search_term.lower() in t["cleaned_transcript"].lower()]
        
        for transcript in filtered_transcripts:
            # Create a nice card for each transcript
            st.markdown(
                f"""
                <div class='transcript-item'>
                    <div class='conference-date'>{transcript["name"]}</div>
                    <div class='conference-time'>Duration: {transcript["duration"]}</div>
                    <div class='conference-speakers'>Speakers: {transcript["num_speakers"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if st.button("📄 View", key=f"view_conf_{transcript['filename']}"):
                st.session_state.selected_conference = transcript
                st.rerun()

    # Main content area
    if not hasattr(st.session_state, 'selected_conference') or st.session_state.selected_conference is None:
        # Show a welcome message and conference stats if no transcript is selected
        st.markdown("<h3>Welcome to Conference Hall Transcripts</h3>", unsafe_allow_html=True)
        st.markdown("Select a conference transcript from the sidebar to view its details.")
        
        # Show some statistics
        if conference_transcripts:
            st.markdown("<h4>Conference Statistics</h4>", unsafe_allow_html=True)
            
            # Calculate stats
            total_conferences = len(conference_transcripts)
            total_speakers = sum(int(t["num_speakers"]) for t in conference_transcripts if t["num_speakers"].isdigit())
            avg_duration = "N/A"
            
            # Try to calculate average duration
            try:
                durations = []
                for t in conference_transcripts:
                    if ":" in t["duration"]:
                        parts = t["duration"].split(":")
                        if len(parts) == 3:  # HH:MM:SS
                            duration_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                            durations.append(duration_seconds)
                        elif len(parts) == 2:  # MM:SS
                            duration_seconds = int(parts[0]) * 60 + int(parts[1])
                            durations.append(duration_seconds)
                
                if durations:
                    avg_seconds = sum(durations) / len(durations)
                    hours = int(avg_seconds // 3600)
                    minutes = int((avg_seconds % 3600) // 60)
                    seconds = int(avg_seconds % 60)
                    avg_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            except:
                avg_duration = "N/A"
            
            # Display metrics in a row
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(
                    f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Total Speakers</div>
                        <div class='metric-value'>{total_speakers}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col3:
                st.markdown(
                    f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Average Duration</div>
                        <div class='metric-value'>{avg_duration}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Show recent conferences
            st.markdown("<h4>Recent Conferences</h4>", unsafe_allow_html=True)
            
            recent_conferences = conference_transcripts[:3]  # Get the 3 most recent
            for conf in recent_conferences:
                st.markdown(
                    f"""
                    <div class='conference-card'>
                        <h4>{conf["name"]}</h4>
                        <div class='conference-date'>Date: {conf["date"]}</div>
                        <div class='conference-time'>Time: {conf["time_range"]}</div>
                        <div class='conference-duration'>Duration: {conf["duration"]}</div>
                        <div class='conference-speakers'>Speakers: {conf["num_speakers"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        return
    
    # Display the selected conference transcript
    selected_conference = st.session_state.selected_conference
    
    # Add a back button
    if st.button("← Back to Conference List"):
        st.session_state.selected_conference = None
        st.rerun()
    
    # Display transcript details in tabs
    tabs = st.tabs(["📝 Transcript", "📊 Conference Info", "💬 Chat"])
    
    with tabs[0]:
        # Main transcript tab
        st.markdown(f"### 📝 Transcript: {selected_conference['name']}")
        
        # Add transcript sections with expandable sections
        col1, col2 = st.columns([3, 1])
        
        with col1:
            cleaned_expander = st.expander("Cleaned Transcript", expanded=True)
            with cleaned_expander:
                st.text_area(
                    "",
                    selected_conference["cleaned_transcript"],
                    height=400,
                    key="conf_cleaned_transcript"
                )
            
            complete_expander = st.expander("Complete Transcript")
            with complete_expander:
                st.text_area(
                    "",
                    selected_conference["complete_transcript"],
                    height=400,
                    key="conf_complete_transcript"
                )
        
        with col2:
            # Conference metadata
            st.markdown("### Conference Details")
            
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Date</div>
                    <div class='metric-value' style='font-size: 1.2rem;'>{selected_conference["date"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Time</div>
                    <div class='metric-value' style='font-size: 1.2rem;'>{selected_conference["time_range"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Duration</div>
                    <div class='metric-value' style='font-size: 1.2rem;'>{selected_conference["duration"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Speakers</div>
                    <div class='metric-value' style='font-size: 1.2rem;'>{selected_conference["num_speakers"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Download buttons
            st.download_button(
                "⬇️ Download Transcript",
                selected_conference["cleaned_transcript"],
                file_name=f"{selected_conference['filename']}_cleaned.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.download_button(
                "⬇️ Download Full Transcript",
                selected_conference["complete_transcript"],
                file_name=f"{selected_conference['filename']}_complete.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    with tabs[1]:
        # Conference info tab
        st.markdown(f"### 📊 Conference Information: {selected_conference['name']}")
        
        # Extract speakers from transcript
        speakers = set()
        for line in selected_conference["cleaned_transcript"].split('\n'):
            if ':' in line:
                speaker = line.split(':')[0].strip()
                if speaker.startswith("SPEAKER_"):
                    speakers.add(speaker)
        
        # Display speaker information
        st.subheader("Participants")
        speaker_cols = st.columns(min(3, len(speakers)) if speakers else 1)
        
        for i, speaker in enumerate(speakers):
            with speaker_cols[i % len(speaker_cols)]:
                st.markdown(
                    f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Speaker ID</div>
                        <div class='metric-value' style='font-size: 1.2rem;'>{speaker}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        if not speakers:
            st.info("No speaker information available in the transcript.")
        
        # Word count and other analytics
        st.subheader("Transcript Analytics")
        
        word_count = len(selected_conference["cleaned_transcript"].split())
        line_count = len(selected_conference["cleaned_transcript"].split('\n'))
        
        analytics_cols = st.columns(3)
        
        with analytics_cols[0]:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Word Count</div>
                    <div class='metric-value'>{word_count}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with analytics_cols[1]:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Line Count</div>
                    <div class='metric-value'>{line_count}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with analytics_cols[2]:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Speaker Count</div>
                    <div class='metric-value'>{len(speakers)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
    with tabs[2]:
        # Chat interface for conference transcript
        st.markdown(f"### 💬 Chat about Conference: {selected_conference['name']}")
        
        # Initialize conference chat messages if not already done
        if 'conference_chat_messages' not in st.session_state:
            st.session_state.conference_chat_messages = []
            
        # Create a container for chat history
        chat_container = st.container()
        
        # Create a container for input field at the bottom
        input_container = st.container()
        
        # Handle input first (but it will appear at the bottom)
        with input_container:
            conf_prompt = st.chat_input("Ask about this conference transcript...")
        
        # Display chat history in the container
        with chat_container:
            for message in st.session_state.conference_chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Handle the chat logic
        if conf_prompt:
            # Add user message
            st.session_state.conference_chat_messages.append({"role": "user", "content": conf_prompt})
            # Display user message
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(conf_prompt)
                # Generate response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    try:
                        # Create context-aware prompt for conference transcript
                        system_prompt = create_system_prompt(selected_conference["cleaned_transcript"])
                        full_prompt = f"{system_prompt}\n\nUser: {conf_prompt}\nAssistant:"
                        # Use asyncio with nest_asyncio
                        loop = asyncio.get_event_loop()
                        full_response = ""
                        async def process_response():
                            nonlocal full_response
                            async for chunk in custom_llm_complete(full_prompt):
                                full_response += chunk
                                message_placeholder.markdown(full_response + "▌")
                            message_placeholder.markdown(full_response)
                        loop.run_until_complete(process_response())
                        # Add to chat history
                        st.session_state.conference_chat_messages.append({
                            "role": "assistant",
                            "content": full_response
                        })
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")


def chat_page(app):
    st.markdown("<h2 class='section-header'>GYAAN AI Chat Assistant</h2>", unsafe_allow_html=True)
    
    # Add navigation
    st.markdown(get_navigation_html(), unsafe_allow_html=True)
    add_sidebar_navigation("chat")
    
    # Initialize session states
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'summary' not in st.session_state:
        st.session_state.summary = None

    # Sidebar for transcript selection
    with st.sidebar:
        st.markdown("<h3>📚 Available Transcripts</h3>", unsafe_allow_html=True)
        transcripts = app.get_all_transcripts()
        
        if not transcripts:
            st.warning("No transcripts available. Please create a transcription first.")
            return
        
        # Add search box for transcripts
        search_term = st.text_input("🔍 Search transcripts", "")
        
        filtered_transcripts = transcripts
        if search_term:
            filtered_transcripts = [t for t in transcripts 
                                  if search_term.lower() in t["content"].lower() 
                                  or search_term.lower() in t["name"].lower()]
        
        for transcript in filtered_transcripts:
            preview = truncate_text(transcript["content"], TRANSCRIPT_PREVIEW_LENGTH)
            with st.container():
                st.markdown(
                    f"""
                    <div class='transcript-item' onclick='select_transcript("{transcript["name"]}")'>
                        <div class='transcript-title'>{transcript["name"]}</div>
                        <div class='transcript-date'>{transcript["date"]}</div>
                        <div class='transcript-preview'>{preview}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("📄 Select", key=f"select_{transcript['name']}"):
                    st.session_state.selected_transcript = transcript
                    st.session_state.messages = []
                    st.rerun()

    # Main chat interface
    if not hasattr(st.session_state, 'selected_transcript') or st.session_state.selected_transcript is None:
        st.info("👈 Please select a transcript from the sidebar")
        return

    selected_transcript = st.session_state.selected_transcript
    
    # Add transcript viewer with tabs
    tabs = st.tabs(["💬 Chat", "📝 Transcript", "📊 Summary", "📋 Minutes of Meeting"])
    # tabs = st.tabs(["💬 Chat", "📝 Transcript", "📊 Summary"])
    
    with tabs[0]:
        # Chat interface
        st.markdown("### Chat with GYAAN AI about this transcript")
        
        # Create a container for chat history
        chat_container = st.container()
        
        # Create a container for input field at the bottom
        input_container = st.container()
        
        # Handle input first (but it will appear at the bottom)
        with input_container:
            prompt = st.chat_input("Ask about the transcript...")
        
        # Display chat history in the container
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Handle the chat logic
        if prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                # Generate response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    try:
                        # Create context-aware prompt
                        system_prompt = create_system_prompt(selected_transcript["content"])
                        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
                        # Use asyncio with nest_asyncio
                        loop = asyncio.get_event_loop()
                        full_response = ""
                        async def process_response():
                            nonlocal full_response
                            async for chunk in custom_llm_complete(full_prompt):
                                full_response += chunk
                                message_placeholder.markdown(full_response + "▌")
                            message_placeholder.markdown(full_response)
                        loop.run_until_complete(process_response())
                        # Add to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": full_response
                        })
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
                        
    with tabs[1]:
        # Transcript viewer
        st.markdown("### 📝 Original Transcript")
        st.markdown("<div class='transcript-container'>", unsafe_allow_html=True)
        
        # Add transcript sections
        col1, col2 = st.columns([2, 1])
        with col1:
            st.text_area(
                "Main Transcript",
                selected_transcript["content"],
                height=400,
                key="main_transcript"
            )
        with col2:
            st.markdown("### Key Points")
            # Extract and display key points
            speakers = set([line.split(':')[0].strip() for line in 
                        selected_transcript["content"].split('\n') 
                        if ':' in line])
            
            st.markdown("**Speakers:**")
            for speaker in speakers:
                st.markdown(f"- {speaker}")
            
            st.markdown("**Length:**")
            st.markdown(f"- {len(selected_transcript['content'].split())} words")

    with tabs[2]:
        # Summary tab
        st.markdown("### 📊 Summary")
        
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                try:
                    mom_prompt = f"""As an expert meeting analyst, provide a comprehensive and structured summary of the following meeting transcript:

                    {selected_transcript["content"]}

                    Please organize the summary in the following sections:

                    1. MEETING OVERVIEW
                    - Date and Time (if mentioned)
                    - Meeting Purpose/Topic
                    - Total Duration

                    2. PARTICIPANTS
                    - List all speakers and their roles (if mentioned)
                    - Note any key stakeholders or decision-makers

                    3. KEY DISCUSSIONS
                    - Main topics covered
                    - Critical points raised
                    - Important decisions made
                    - Challenges or concerns discussed

                    4. ACTION ITEMS
                    - List all tasks/actions agreed upon
                    - Assigned responsibilities
                    - Deadlines or timelines mentioned
                    - Follow-up requirements

                    5. NEXT STEPS
                    - Upcoming milestones
                    - Scheduled follow-up meetings
                    - Dependencies identified

                    Please provide specific details and direct references from the transcript where possible."""
                    
                    summary = asyncio.run(process_large_transcript(
                        selected_transcript["content"], 
                        mom_prompt
                    ))
                    app.save_summary(selected_transcript["path"], summary)
                    
                    # Refresh transcript data
                    transcripts = app.get_all_transcripts()
                    st.session_state.selected_transcript = next(
                        t for t in transcripts if t["path"] == selected_transcript["path"]
                    )
                    
                    st.markdown("<div class='summary-section'>", unsafe_allow_html=True)
                    st.markdown(summary)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
        
        # Display existing summary
        elif selected_transcript.get("summary"):
            st.markdown("<div class='summary-section'>", unsafe_allow_html=True)
            st.markdown(selected_transcript["summary"])
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No summary generated yet. Click the button above to generate one.")

    with tabs[3]:
        # Minutes of Meeting tab
        st.markdown("### 📋 Minutes of Meeting")
        
        if st.button("Generate Minutes of Meeting"):
            with st.spinner("Generating Minutes of Meeting..."):
                try:
                    mom_prompt = f"""As a professional meeting secretary, create detailed minutes of meeting from this transcript:

                    {selected_transcript["content"]}

                    Please format the minutes as follows:

                    MINUTES OF MEETING

                    1. Meeting Details
                    - Date and Time
                    - Location/Platform
                    - Meeting Type

                    2. Attendees
                    - Present
                    - Apologies
                    - Chair/Facilitator

                    3. Agenda Items
                    - List all topics discussed
                    - Key points under each topic
                    - Decisions made

                    4. Action Items
                    - Task description
                    - Person responsible
                    - Deadline
                    - Status

                    5. Next Meeting
                    - Date and time
                    - Key agenda items
                    - Required preparations

                    6. Additional Notes
                    - Important observations
                    - Follow-up requirements
                    - Documentation needs
                    
                    Follow the Above format when generating your response.
                    """
                    
                    mom = asyncio.run(process_large_transcript(
                        selected_transcript["content"], 
                        mom_prompt
                    ))
                    app.save_mom(selected_transcript["path"], mom)
                    
                    # Refresh transcript data
                    transcripts = app.get_all_transcripts()
                    st.session_state.selected_transcript = next(
                        t for t in transcripts if t["path"] == selected_transcript["path"]
                    )
                    
                    st.markdown("<div class='mom-section'>", unsafe_allow_html=True)
                    st.markdown(mom)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error generating minutes of meeting: {str(e)}")
        
        # Display existing MoM
        elif selected_transcript.get("mom"):
            st.markdown("<div class='mom-section'>", unsafe_allow_html=True)
            st.markdown(selected_transcript["mom"])
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No Minutes of Meeting generated yet. Click the button above to generate one.")


def format_message_with_speaker(message):
    """Format message with speaker information"""
    if "speaker" in message:
        return f"**{message['speaker']}**: {message['text']}"
    return message['text']



def landing_page():
    if gyaan_logo:
        st.markdown(f"""
            <div class="header-logo">
                <img src="data:image/jpeg;base64,{gyaan_logo}" style="max-height: 100px;" />
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your Intelligent AI Assistant</p>", unsafe_allow_html=True)

    # Add navigation
    st.markdown(get_navigation_html(), unsafe_allow_html=True)

    # Add this CSS to load_css() function
    st.markdown("""
        <style>
        .feature-card {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px;
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid #f5f5f5;
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            border-color: #1e3d59;
        }
        
        .feature-icon {
            font-size: 3em;
            margin-bottom: 15px;
            color: #1e3d59;
        }
        
        .feature-card h3 {
            color: #1e3d59;
            margin-bottom: 15px;
        }
        
        .feature-card p {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon'>📝</div>
                <h3>Video to Transcription</h3>
                <p>Convert your meeting recordings into transcriptions with our advanced GYAAN AI</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Transcription", key="transcribe_btn"):
            st.session_state.page = "transcribe"
            st.rerun()

    with col2:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon'>🤖</div>
                <h3>AI Chat Assistant</h3>
                <p>Analyze and discuss your meeting transcripts with GYAAN AI</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Chat with GYAAN AI", key="chat_btn"):
            st.session_state.page = "chat"
            st.rerun()
            
    with col3:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon'>🏢</div>
                <h3>Conference Hall Transcripts</h3>
                <p>Access and analyze conference hall discussion transcripts</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Conference Transcripts", key="conference_btn"):
            st.session_state.page = "conference"
            st.rerun()


def transcription_page(app):
    st.markdown("<h2 class='section-header'>Video Transcription</h2>", unsafe_allow_html=True)
    
    # Add navigation
    st.markdown(get_navigation_html(), unsafe_allow_html=True)
    add_sidebar_navigation("transcribe")

    # Improved sidebar with transcript list
    with st.sidebar:
        st.markdown("<h3>📚 Previous Transcriptions</h3>", unsafe_allow_html=True)
        transcripts = app.get_all_transcripts()
        
        for transcript in transcripts:
            with st.container():
                st.markdown(
                    f"""
                    <div class='transcript-item'>
                        <div class='transcript-title'>{transcript["name"]}</div>
                        <div class='transcript-date'>{transcript["date"]}</div>
                        <div class='transcript-preview'>{truncate_text(transcript["content"], TRANSCRIPT_PREVIEW_LENGTH)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # if st.button("📄 View", key=f"view_{transcript['name']}"):
                #     st.session_state.selected_transcript = transcript
                #     st.rerun()

    # Main content area with improved layout
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    # Upload Section
    st.markdown("<h3>📤 Upload Video</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a video file", type=["webm", "mp4"])

    if uploaded_file:
        st.video(uploaded_file)
        
        if st.button("🎯 Start Transcription", use_container_width=True):
            with st.spinner("🎥 Processing your video..."):
                try:
                    # Save and process video
                    video_path = app.save_uploaded_file(uploaded_file)
                    
                    # Show transcription progress
                    progress_text = st.empty()
                    progress_text.markdown("⚙️ Transcribing video...")
                    transcript_path = app.process_video(video_path)
                    
                    # Clean transcript with LLM
                    progress_text.markdown("🧠 Cleaning transcript with GYAAN AI...")
                    with open(transcript_path, "r", encoding='utf-8') as f:
                        transcript_text = f.read()
                    
                    # Initialize cleaner and clean transcript
                    cleaner = TranscriptCleaner()
                    cleaned_data = asyncio.run(cleaner.clean_transcript(transcript_text))
                    
                    # Save cleaned transcript
                    with open(transcript_path, "w", encoding='utf-8') as f:
                        f.write(cleaned_data["cleaned_transcript"])
                        f.write("\n\n=== Complete Transcript ===\n")
                        f.write(cleaned_data["complete_transcript"])
                    
                    progress_text.markdown("✨ Processing complete!")
                    
                    # Update session state
                    st.session_state.current_transcript = {
                        "name": transcript_path.stem,
                        "path": transcript_path,
                        "content": cleaned_data["cleaned_transcript"],
                        "complete_transcript": cleaned_data["complete_transcript"],
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.success("✨ Transcription and cleaning completed successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing video: {str(e)}")

    # Transcript Display Section
    st.markdown("<h3>📝 Transcript</h3>", unsafe_allow_html=True)
    
    transcript_to_show = None
    if hasattr(st.session_state, 'current_transcript'):
        transcript_to_show = st.session_state.current_transcript
    elif hasattr(st.session_state, 'selected_transcript'):
        transcript_to_show = st.session_state.selected_transcript

    if transcript_to_show:
        # Improved transcript display
        st.markdown(
            f"""
            <div class='transcript-container'>
                <div class='transcript-header'>
                    <div class='transcript-info'>
                        <span class='transcript-date'>📅 {transcript_to_show['date']}</span>
                        <span class='transcript-file'>📄 {transcript_to_show['name']}</span>
                    </div>
                </div>
                <div class='transcript-content'>
                    {transcript_to_show['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇️ Download Transcript",
                transcript_to_show['content'],
                file_name=f"{transcript_to_show['name']}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("🤖 Analyze with GYAAN AI", use_container_width=True):
                st.session_state.page = "chat"
                st.session_state.selected_transcript = transcript_to_show
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="GYAAN AI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    
    # Initialize nest_asyncio
    nest_asyncio.apply()
    
    load_css()
    app = TranscriptionApp()

    # Initialize session states
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'current_transcript' not in st.session_state:
        st.session_state.current_transcript = None
    if 'selected_transcript' not in st.session_state:
        st.session_state.selected_transcript = None
    if 'conference_chat_messages' not in st.session_state:
        st.session_state.conference_chat_messages = []
    if 'selected_conference' not in st.session_state:
        st.session_state.selected_conference = None

    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = "landing"

    # Render appropriate page
    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "transcribe":
        transcription_page(app)
    elif st.session_state.page == "chat":
        chat_page(app)
    elif st.session_state.page == "conference":
        conference_page(app)

    # Add footer
    add_footer()
    
    # Add help tooltip
    st.sidebar.markdown("---")
    with st.sidebar.expander("ℹ️ Help & Information"):
        st.markdown("""
        ### About GYAAN AI
        GYAAN AI is your intelligent meeting assistant that helps you:
        - Transcribe video recordings
        - Generate summaries and Minutes of Meeting
        - Chat with AI about the content
        - Access conference hall transcripts
        
        ### Network Access
        - This app is accessible within your local network
        - Users can upload videos from their computers
        - All transcripts and chats are stored locally
        
        ### File Support
        - Supported video formats: MP4, WebM
        - Transcripts are stored as text files
        - Conference transcripts can be accessed in the dedicated section
        
        ### Need Help?
        Contact the GYAAN AI team for support or issues.
        """)


if __name__ == "__main__":
    main()