import streamlit as st
import yt_dlp, json, os, requests, tempfile, base64, time
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import Video_Converter


# Override Video_Converter's module-level credentials with st.secrets
Video_Converter.API_KEY = st.secrets["API_KEY"]
Video_Converter.API_ENDPOINT = st.secrets["API_ENDPOINT"]

# Streamlit Application 

st.set_page_config(page_title="Video Converter", page_icon="🎬")

try:
    base_64_img = base64.b64encode(open("static/Cadence_Background.jpg", "rb").read()).decode()
    page_elements = f'''
    <style>
        [data-testid="stAppViewContainer"] {{
            background: url(data:image/jpg;base64,{base_64_img});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        [data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0) !important;
        }}
        
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }}
        
        .main h1 {{
            color: #ff4444 !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
            padding: 15px;
            border-radius: 15px;
            backdrop-filter: blur(5px);
        }}
        
        /* Text input styling */
        .stTextInput input {{
            background-color: rgba(255, 255, 255, 0.85) !important;
            color: #333333 !important;
            border-radius: 8px !important;
        }}
        .stTextInput input::placeholder {{
            color: #888888 !important;
            opacity: 1 !important;
        }}
    </style>
    '''
    st.markdown(page_elements, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Background image not found")

st.title("🎬 :red[Video Processor] :sunglasses:")
st.markdown(":information_source: :blue[Download YouTube videos or upload MP4 files → get MP4 & MP3 → auto-upload to Jasper KB]")
    # Display logo and header
try:
    filename = "static/Cadence_Logo_Red_185_Reg.png"
    img_path = os.path.join(os.path.dirname(__file__), filename)
    img = Image.open(img_path)
    st.logo(img,
            size="large",
            link="https://www.cadence.com/en_US/home.html",
            icon_image=None)
except FileNotFoundError:
    st.warning("Logo image not found")

tab1, tab2 = st.tabs(["🔗 YouTube URL", "📁 Upload MP4"])

# --- Tab 1: YouTube ---
@st.fragment
def youtube_downloads():
    # Manage session for persisting download buttons after processing a YouTube video
    if "yt_result" not in st.session_state:
        return
    result = st.session_state["yt_result"]
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(":material/download: Download MP4", result["mp4_data"],
                           file_name=f"{result['title']}.mp4", mime="video/mp4")
    with col2:
        st.download_button(":material/download: Download MP3", result["mp3_data"],
                           file_name=f"{result['title']}.mp3", mime="audio/mpeg")

with tab1:
    url = st.text_input("Paste a YouTube URL", placeholder="https://www.youtube.com/watch?v=...",)
    if st.button("🚀 Process YouTube Video", disabled=not url):
        tmp_dir = tempfile.mkdtemp()
        try:
            with st.status("Getting video data...", expanded=True) as status:
                st.write("⬇️ Downloading video...")
                mp4_path, title = Video_Converter.direct_youtube_video_download(url, tmp_dir)
                time.sleep(5)  # Simulate waiting time

                st.write("🔄 Converting to MP3...")
                mp3_path = Video_Converter.convert_video_to_mp3(mp4_path)
                time.sleep(5)  # Simulate waiting time

                st.write("☁️ Uploading to Jasper Knowledge Base...")
                time.sleep(5)  # Simulate waiting time
                Video_Converter.call_jasper_api(mp3_path) #uncomment for testing purposes

                status.update(label="✅ Done!", state="complete", expanded=False)

            st.success(f"**{title}** processed successfully! Please check your Jasper Knowledge Base for the new entry.")

            # Read file bytes into session_state so they persist across reruns
            with open(mp4_path, "rb") as f:
                mp4_data = f.read()
            with open(mp3_path, "rb") as f:
                mp3_data = f.read()
            st.session_state["yt_result"] = {"mp4_data": mp4_data, "mp3_data": mp3_data, "title": title}

        except Exception as e:
            st.error(f"❌ Error: {e}")

    youtube_downloads()

# --- Tab 2: Upload MP4 ---
@st.fragment
def upload_downloads():
    # Manage session for persisting download buttons after processing an uploaded file
    if "upload_result" not in st.session_state:
        return
    result = st.session_state["upload_result"]
    col1 = st.columns(2)
    with col1[0]:
        st.download_button(":material/download: Download MP3", result["mp3_data"],
                           file_name=f"{result['title']}.mp3", mime="audio/mpeg")

with tab2:
    uploaded = st.file_uploader("Upload an MP4 file", type=["mp4"])
    if uploaded and st.button("🚀 Process Uploaded Video"):
        tmp_dir = tempfile.mkdtemp()
        try:
            mp4_path = os.path.join(tmp_dir, uploaded.name)
            with open(mp4_path, "wb") as f:
                f.write(uploaded.read())

            with st.status("Getting video data...", expanded=True) as status:
                st.write("🔄 Converting to MP3...") 
                mp3_path = Video_Converter.convert_video_to_mp3(mp4_path)
                time.sleep(5) # Simulate waiting time

                st.write("☁️ Uploading to Jasper Knowledge Base...")
                time.sleep(5)  # Simulate waiting time
                Video_Converter.call_jasper_api(mp3_path) #uncomment for testing purposes
                
                status.update(label="✅ Done!", state="complete", expanded=False)

            title = os.path.splitext(uploaded.name)[0]
            st.success(f"**{title}** processed successfully! Please check your Jasper Knowledge Base for the new entry.")

            # Read file bytes into session_state so they persist across reruns
            with open(mp3_path, "rb") as f:
                mp3_data = f.read()
            st.session_state["upload_result"] = {"mp3_data": mp3_data, "title": title}

        except Exception as e:
            st.error(f"❌ Error: {e}")

    upload_downloads()


# ----- End -------------

