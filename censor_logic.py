import whisper
from transformers import pipeline
from pydub import AudioSegment
from pydub.generators import Sine
import re
import os
from moviepy import VideoFileClip, AudioFileClip
print("movie")


def extract_audio_from_video(video_path, output_audio_path="output_audio.wav"):
    """Extract audio from video file"""
    print("Extracting audio from video...")
    video_clip = VideoFileClip(video_path)
    video_clip.audio.write_audiofile(output_audio_path)
    print(f"Audio extracted and saved to {output_audio_path}")
    return output_audio_path


def transcribe_audio(audio_path, model_size="base"):
    """Transcribe audio using Whisper with word-level timestamps"""
    print("Loading Whisper model...")
    model = whisper.load_model(model_size)

    print("Transcribing audio with word-level timestamps...")
    result = model.transcribe(audio_path, word_timestamps=True)

    transcription_path = "transcription.txt"
    with open(transcription_path, "w", encoding="utf-8") as file:
        file.write(result['text'])
    print(f"Transcription saved to {transcription_path}")

    return result


def detect_toxicity(text, classifier):
    """Detect toxic content in text"""
    profanity_words = [
        "fuck", "motherfucker", "bitch", "assholes", "dammit", "goddammit", "dunce",
        "whore", "bastard", "fucking", "kill", "murder", "shit", "cunt", "piss", "ass"
    ]
    insult_words = [
        "stupid", "idiot", "dumb", "moron", "retard", "loser", "worthless", "useless",
        "asshole", "fuckhead", "douchebag", "jackass", "prick"
    ]

    toxic_words_found = []
    for word in profanity_words + insult_words:
        if re.search(rf'\b{word}\b', text, re.IGNORECASE):
            toxic_words_found.append(word)

    classification = classifier(text)
    return toxic_words_found, classification


def highlight_profanity(text, toxic_words):
    """Highlight profanity in the text"""
    highlighted_text = text
    for word in toxic_words:
        highlighted_text = re.sub(
            rf'\b{word}\b',
            f'**{word}**',
            highlighted_text,
            flags=re.IGNORECASE
        )
    return highlighted_text

def merge_audio_with_video(video_path, audio_path, output_path):
    """Combine censored/uncensored audio back into the original video."""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    print(f"✅ Merged video saved as {output_path}")
    return output_path

def create_beep(duration_ms=500, frequency=1000):
    """Create a beep sound for censorship"""
    return Sine(frequency).to_audio_segment(duration=duration_ms)


def censor_audio(audio_path, toxic_timestamps, output_path="censored_audio.wav"):
    """Censor audio by adding beeps at toxic word timestamps"""
    audio = AudioSegment.from_wav(audio_path)

    #Reverse sort timestamps so editing doesn’t shift later segments
    for start_time, end_time, word in sorted(toxic_timestamps, key=lambda x: x[0], reverse=True):
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)

        beep = create_beep(duration_ms=(end_ms - start_ms))

        # Replace segment with beep
        audio = audio[:start_ms] + beep + audio[end_ms:]

    audio.export(output_path, format="wav")
    print(f"Censored audio saved as {output_path}")
    return output_path


def main():
    # Asking user for video file path (instead of Colab upload)
    video_filename = input("Enter path to your video file: ").strip()

    if not os.path.exists(video_filename):
        print("Error: File not found.")
        return

    # Step 1: Extract audio
    audio_path = extract_audio_from_video(video_filename)

    # Step 2: Transcribe audio
    transcription_result = transcribe_audio(audio_path)

    # Step 3: Load toxicity classifier
    print("Loading toxicity classifier...")
    toxic_classifier = pipeline("text-classification", model="unitary/toxic-bert")

    toxic_timestamps = []
    highlighted_segments = []

    print("Detecting toxic content...")
    for segment in transcription_result['segments']:
        segment_text = segment['text']
        toxic_words, classification = detect_toxicity(segment_text, toxic_classifier)

        if toxic_words or (classification[0]['label'].lower() == 'toxic' and classification[0]['score'] > 0.7):
            highlighted_text = highlight_profanity(segment_text, toxic_words)
            highlighted_segments.append(highlighted_text)

            for word_info in segment.get('words', []):
                word = word_info['word']
                if any(toxic_word in word.lower() for toxic_word in toxic_words):
                    toxic_timestamps.append((
                        word_info['start'],
                        word_info['end'],
                        word
                    ))
                    print(f"Toxic word detected: '{word}' at {word_info['start']:.2f}-{word_info['end']:.2f}s")

    #Save highlighted transcript
    highlighted_transcription_path = "highlighted_transcription.txt"
    with open(highlighted_transcription_path, "w", encoding="utf-8") as file:
        file.write("\n\n".join(highlighted_segments))
    print(f"Highlighted transcription saved to {highlighted_transcription_path}")

    # Step 4: Censor audio
    if toxic_timestamps:
        censored_audio_path = censor_audio(audio_path, toxic_timestamps)
        print(f"✅ Censoring complete! Files saved:\n- {highlighted_transcription_path}\n- {censored_audio_path}")
    else:
        print("No toxic content detected. No censorship needed.")


if __name__ == "__main__":
    main()
