import pyaudio
from pydub import AudioSegment
import keyboard
import requests
import os

# Define constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
OUTPUT_FILENAME = "Output/output.mp3"

PUSH_TO_RECORD_KEY = '7'

# Initialize PyAudio
audio = pyaudio.PyAudio()

while True:
    # Start recording when user presses "s" key
    keyboard.wait('7')
    print("Recording...")

    # Open audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    # Initialize frames array to store audio data
    frames = []

    # Record audio data
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if not keyboard.is_pressed('7'):
            break

    # Stop recording and close audio stream
    print("Recording stopped.")
    stream.stop_stream()
    stream.close()

    # Save recorded audio data to file
    audio_segment = AudioSegment(
        data=b''.join(frames),
        sample_width=audio.get_sample_size(FORMAT),
        frame_rate=RATE,
        channels=CHANNELS
    )

    audio_segment.export(OUTPUT_FILENAME, format="mp3")

    with open(OUTPUT_FILENAME, "rb") as file:
        url = "http://localhost:9000/asr?task=transcribe&language=en&output=txt"
        files = [
            ('audio_file', (OUTPUT_FILENAME, file, 'audio/mpeg'))
        ]
        response = requests.request("POST", url, files=files)

        print(response.text)
        if response.status_code == 200:
            print(response)
        else:
            print("Error: ", response.status_code)
            print(response)

audio.terminate()
