import os
import math
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from gtts import gTTS

API_KEY = 'API_Key'
article_text = "Text"
query = "query"

# Generate voice-over using gTTS
tts = gTTS(text=article_text, lang='en')
tts.save("voice_over.mp3")
audio = AudioFileClip("voice_over.mp3")
audio_duration = audio.duration

# Calculate the number of 5-second clips needed
clip_duration = 5  # seconds
num_clips_needed = math.ceil(audio_duration / clip_duration)

# Fetch videos from Pexels
url = "https://api.pexels.com/videos/search"
headers = {"Authorization": API_KEY}
response = requests.get(url, params={"query": query, "per_page": num_clips_needed}, headers=headers)
videos = response.json()['videos']

# Download and load video clips
clips = []
for i, video in enumerate(videos):
    video_url = video['video_files'][0]['link']
    filename = f"{video['id']}.mp4"
    with open(filename, 'wb') as f:
        f.write(requests.get(video_url).content)
    clip = VideoFileClip(filename).subclip(0, clip_duration)
    clips.append(clip)
    if i + 1 == num_clips_needed:
        break

# Concatenate video clips and adjust the length to match the voice-over
final_clip = concatenate_videoclips(clips, method="compose")
final_clip = final_clip.subclip(0, audio_duration)
final_clip = final_clip.set_audio(audio)

# Write the final output
final_clip.write_videofile("final_output.mp4")

# Clean up downloaded video files
for video in videos:
    filename = f"{video['id']}.mp4"
    os.remove(filename)

#remove the voice-over file
os.remove("voice_over.mp3")
