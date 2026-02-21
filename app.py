import streamlit as st
import os
from censor_logic import extract_audio_from_video, transcribe_audio, censor_audio
from moviepy import VideoFileClip

# ---------- CONFIG ----------
st.set_page_config(page_title="Video Censorship Studio", page_icon="🎞️", layout="wide")

VIDEO_FOLDER = "videos"
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

for folder in [VIDEO_FOLDER, UPLOAD_FOLDER, PROCESSED_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ---------- HEADER ----------
st.markdown("""
    <h1 style="text-align:center; color:#3a86ff;">🎬 Video Censorship Studio</h1>
    <p style="text-align:center; font-size:18px; color:gray;">
    Watch, upload, and automatically censor videos with AI.
    </p>
    <hr>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("🎞️ Navigation")
choice = st.sidebar.radio("Go to:", ["Pre-uploaded Videos", "Upload New Video"])

# ---------- PRE-UPLOADED VIDEOS ----------
if choice == "Pre-uploaded Videos":
    st.header("📁 Pre-uploaded Videos")

    videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith((".mp4", ".mov", ".mkv"))]

    if not videos:
        st.warning("No pre-uploaded videos found in the 'videos' folder.")
    else:
        selected_video = st.selectbox("Select a video to play:", videos)
        video_path = os.path.join(VIDEO_FOLDER, selected_video)

        st.video(video_path)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔊 Original (Uncensored)")
            original_audio_path = os.path.join(PROCESSED_FOLDER, selected_video.replace(".mp4", "_original.wav"))
            if not os.path.exists(original_audio_path):
                extract_audio_from_video(video_path, original_audio_path)
            st.audio(original_audio_path)

        with col2:
            st.subheader("🔇 Censored")
            censored_audio_path = os.path.join(PROCESSED_FOLDER, selected_video.replace(".mp4", "_censored.wav"))
            if os.path.exists(censored_audio_path):
                st.audio(censored_audio_path)
            else:
                if st.button("Generate Censored Audio"):
                    st.info("Processing and censoring... this might take a few minutes ⏳")
                    audio_path = extract_audio_from_video(video_path)
                    result = transcribe_audio(audio_path)

                    toxic_timestamps = []
                    for seg in result['segments']:
                        for word in seg.get('words', []):
                            if any(x in word['word'].lower() for x in ["fuck", "shit", "bitch", "asshole"]):
                                toxic_timestamps.append((word['start'], word['end'], word['word']))

                    if toxic_timestamps:
                        censor_audio(audio_path, toxic_timestamps, output_path=censored_audio_path)
                        st.success("✅ Censored audio generated!")
                        st.audio(censored_audio_path)
                    else:
                        st.info("No toxic content found.")

# ---------- USER UPLOAD ----------
elif choice == "Upload New Video":
    st.header("⬆️ Upload Your Video")

    uploaded_file = st.file_uploader("Upload a video file (mp4/mov/mkv)", type=["mp4", "mov", "mkv"])

    if uploaded_file is not None:
        save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ Uploaded: {uploaded_file.name}")

        st.video(save_path)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔊 Original (Uncensored)")
            original_audio_path = os.path.join(PROCESSED_FOLDER, uploaded_file.name.replace(".mp4", "_original.wav"))
            if not os.path.exists(original_audio_path):
                extract_audio_from_video(save_path, original_audio_path)
            st.audio(original_audio_path)

        with col2:
            st.subheader("🔇 Censored")
            censored_audio_path = os.path.join(PROCESSED_FOLDER, uploaded_file.name.replace(".mp4", "_censored.wav"))

            if st.button("Generate Censored Version"):
                st.info("Processing and censoring your uploaded video... please wait ⏳")

                audio_path = extract_audio_from_video(save_path)
                result = transcribe_audio(audio_path)

                toxic_timestamps = []
                for seg in result['segments']:
                    for word in seg.get('words', []):
                        if any(x in word['word'].lower() for x in ["fuck", "shit", "bitch", "asshole"]):
                            toxic_timestamps.append((word['start'], word['end'], word['word']))

                if toxic_timestamps:
                    censor_audio(audio_path, toxic_timestamps, output_path=censored_audio_path)
                    st.success("✅ Censored audio generated successfully!")
                    st.audio(censored_audio_path)
                else:
                    st.info("No toxic content detected — clean audio 🎧")

# ---------- FOOTER ----------
st.markdown("""
    <hr>
    <p style="text-align:center; color:gray; font-size:14px;">
    Built by <b>Ritesh and Deepthi</b> | Powered by Whisper and Transformers models 🚀
    </p>
""", unsafe_allow_html=True)
