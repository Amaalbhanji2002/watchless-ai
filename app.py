import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
import re
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="WatchLessAI", layout="centered")

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #F5F7FA;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 800px;
            margin: auto;
        }
        .title {
            font-size: 3rem;
            font-weight: bold;
            color: #4F46E5;
        }
        .summary-box {
            background-color: #ffffff;
            border-left: 6px solid #4F46E5;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
            margin-top: 1rem;
            white-space: pre-wrap;
        }
        .url-box input {
            height: 3rem !important;
            font-size: 1rem !important;
        }
        .button {
            background-color: #4F46E5;
            color: white;
            border: none;
            padding: 0.7rem 1.2rem;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

# Header Layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 class='title'>📺 WatchLessAI</h1>", unsafe_allow_html=True)
    st.write("Get quick summaries of YouTube videos in seconds!")

# Input Section
st.markdown("#### Paste a YouTube video URL:")
url = st.text_input("", placeholder="https://www.youtube.com/watch?v=example", label_visibility="collapsed")

# Select summary type
summary_type = st.selectbox(
    "Choose output type:",
    ["Summary", "Key Points", "Keywords"]
)

# Show summary length options only if "Summary" is selected
if summary_type == "Summary":
    summary_length = st.selectbox(
        "Choose summary length:",
        ["Short", "Medium", "Detailed"]
    )

# Language selection
language = st.selectbox(
    "Select a language:",
    ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Hindi", "Portuguese", "Russian"]
)

# Extract video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# Get transcript from YouTube
def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([entry["text"] for entry in transcript])

# Map summary length to max tokens for summary
length_to_tokens = {
    "Short (1-2 sentences)": 100,
    "Medium": 200,
    "Detailed": 300
}

# Main summarization button logic
if st.button("Summarize", help="Click to generate a quick summary"):
    if url:
        video_id = extract_video_id(url)
        if video_id:
            with st.spinner("🔄 Generating summary..."):
                try:
                    transcript = get_transcript(video_id)

                    # Build prompt based on user choices
                    if summary_type == "Summary":
                        max_tokens = length_to_tokens[summary_length]
                        length_desc = summary_length.split(" ")[0].lower()  # e.g., "short", "medium", "detailed"
                        prompt = (
                            f"Write a {length_desc} summary of the following text in {language}.\n\n{transcript}"
                        )
                    elif summary_type == "Key Points":
                        max_tokens = 300
                        prompt = (f"Extract the key points as bullet points from the following text in {language}:\n\n{transcript}")
                    else:  # Keywords
                        max_tokens = 100
                        prompt = (f"List the main topics and keywords from the following text, separated by commas, in {language}:\n\n{transcript}")

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.5,
                    )
                    output = response.choices[0].message.content

                    # Output results with proper headers and styling
                    if summary_type == "Summary":
                        st.markdown("#### 📝 Summary")
                    elif summary_type == "Key Points":
                        st.markdown("#### 📌 Key Points")
                    else:
                        st.markdown("#### 🗝️ Keywords")

                    st.markdown(f"<div class='summary-box'>{output}</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Invalid YouTube URL.")
    else:
        st.warning("Please enter a YouTube URL.")

# Footer
st.markdown("""
<hr style="margin-top: 3rem;"/>
<p style='text-align: center; font-size: 0.9rem; color: gray;'>
    Built with ❤️ by WatchLessAI · Powered by OpenAI
</p>
""", unsafe_allow_html=True)
