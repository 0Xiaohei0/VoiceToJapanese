import os
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import keyboard
import requests
import json

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

    # Send audio to whisper backend
    with open(OUTPUT_FILENAME, "rb") as file:
        url = "http://localhost:9000/asr?task=transcribe&language=en&output=txt"
        files = [
            ('audio_file', (OUTPUT_FILENAME, file, 'audio/mpeg'))
        ]
        SpeechToTextResponse = requests.request("POST", url, files=files)

        print(f'English: {SpeechToTextResponse.text}')
        # if SpeechToTextResponse.status_code == 200:
        #     print(SpeechToTextResponse)
        # else:
        #     print("Error: ", SpeechToTextResponse.status_code)
        #     print(SpeechToTextResponse)

    token = os.environ.get("translation-service-api-token")
    # Send text to translation service
    headers = {
        'Authorization': f'DeepL-Auth-Key {token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'text={SpeechToTextResponse.text}&target_lang=JA'

    translationResponse = requests.post(
        'https://api-free.deepl.com/v2/translate', headers=headers, data=data)

    translation = translationResponse.content.decode('utf-8')
    translation_text = json.loads(translation)['translations'][0]['text']
    text_file = open("sample.txt", "w", encoding='utf-8')
    n = text_file.write(translation_text)
    text_file.close()
    print(f'Japanese: {translation_text}')
    url = f"http://127.0.0.1:50021/audio_query?text={translation_text}&speaker=0"

    VoiceTextResponse = requests.request("POST", url, headers=headers)

    url = "http://127.0.0.1:50021/synthesis?speaker=0"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = VoiceTextResponse
    AudioResponse = requests.request(
        "POST", url, headers=headers, data=payload)

    with open("audioResponse.wav", "wb") as file:
        file.write(AudioResponse.content)
    voiceLine = AudioSegment.from_wav("audioResponse.wav")
    play(voiceLine)
audio.terminate()
