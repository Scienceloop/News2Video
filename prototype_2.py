import os
import math
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from gtts import gTTS
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

API_KEY = 'API_Key'

# Ask user to input folder name and article text
folder_name = input("Enter the folder name where the videos and audio will be saved: ")
article_text = input("Enter the article text: ")

# Create directory to save videos and audio
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Extract keywords from the article text
words = article_text.split()
keywords = set(words) - set(ENGLISH_STOP_WORDS)

# Generate voice-over using gTTS
tts = gTTS(text=article_text, lang='en')
audio_file_path = os.path.join(folder_name, "voice_over.mp3")
tts.save(audio_file_path)
audio = AudioFileClip(audio_file_path)
audio_duration = audio.duration

# Calculate the number of 5-second clips needed
clip_duration = 5  # seconds
num_clips_needed = math.ceil(audio_duration / clip_duration)

# Define the desired size (width, height)
desired_size = (1920, 1080)  # Example: Full HD

# Fetch videos from Pexels for each keyword
clips = []
for keyword in keywords:
    if len(clips) >= num_clips_needed:
        break
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": API_KEY}
    response = requests.get(url, params={"query": keyword, "per_page": num_clips_needed - len(clips)}, headers=headers)
    videos = response.json().get('videos', [])

    # Download, load, and resize video clips
    for video in videos:
        if len(clips) >= num_clips_needed:
            break
        video_url = video['video_files'][0]['link']
        filename = os.path.join(folder_name, f"{video['id']}.mp4")
        with open(filename, 'wb') as f:
            f.write(requests.get(video_url).content)

        # Load and resize or crop the clip
        clip = VideoFileClip(filename).subclip(0, clip_duration)
        clip = clip.resize(newsize=desired_size)  # Resize
        # Or, to crop instead of resizing, uncomment the following line and comment the above line
        # clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=desired_size[0], height=desired_size[1])

        clips.append(clip)

# Concatenate video clips and adjust the length to match the voice-over
final_clip = concatenate_videoclips(clips, method="compose")
final_clip = final_clip.subclip(0, audio_duration)
final_clip = final_clip.set_audio(audio)

# Write the final output
final_clip.write_videofile(os.path.join(folder_name, "final_output.mp4"))
