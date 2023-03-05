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
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
OUTPUT_FILENAME = "Output/output.mp3"

PUSH_TO_RECORD_KEY = '7'
NO_TRANSLATE_KEY = '0'
SPEAKER_ID = '0'

translate = True
audio = pyaudio.PyAudio()


def recordAudio():
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
        if not keyboard.is_pressed(PUSH_TO_RECORD_KEY):
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


def sendAudioToWhisper():
    with open(OUTPUT_FILENAME, "rb") as file:
        url = "http://localhost:9000/asr"
        AudioLanguage = 'EN'
        if (not translate):
            AudioLanguage = 'JA'

        params = {
            'task': 'transcribe',
            'language': AudioLanguage,
            'output': 'txt'
        }
        files = [
            ('audio_file', (OUTPUT_FILENAME, file, 'audio/mpeg'))
        ]
        SpeechToTextResponse = requests.request(
            "POST", url, params=params, files=files)

        print(f'Input: {SpeechToTextResponse.text}')
        return SpeechToTextResponse.text


def sendTextToTranslationService(text_output):
    token = os.environ.get("translation-service-api-token")
    # Send text to translation service
    headers = {
        'Authorization': f'DeepL-Auth-Key {token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'text={text_output}&target_lang=JA'
    translationResponse = requests.post(
        'https://api-free.deepl.com/v2/translate', headers=headers, data=data.encode('utf-8'))
    translation = translationResponse.content.decode('utf-8')
    text_output = json.loads(translation)['translations'][0]['text']
    print(f'Japanese: {text_output}')
    return text_output


def sendTextToSyntheizer(text_output):
    url = f"http://127.0.0.1:50021/audio_query?text={text_output}&speaker={SPEAKER_ID}"

    VoiceTextResponse = requests.request("POST", url)

    url = f"http://127.0.0.1:50021/synthesis?speaker={SPEAKER_ID}"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = VoiceTextResponse
    AudioResponse = requests.request(
        "POST", url, data=payload)
    return AudioResponse


while True:
    # Start recording when user presses "s" key
    a = keyboard.read_key()
    if (a == NO_TRANSLATE_KEY):
        translate = not translate
        print(f"Translate = {translate}")
        while (keyboard.is_pressed(NO_TRANSLATE_KEY)):
            continue
        continue
    elif (a == PUSH_TO_RECORD_KEY):
        print(f"Recording... (translate = {translate})")
    else:
        continue
    recordAudio()
    text_output = sendAudioToWhisper()
    if (translate):
        text_output = sendTextToTranslationService(text_output)
    AudioResponse = sendTextToSyntheizer(text_output)
    with open("audioResponse.wav", "wb") as file:
        file.write(AudioResponse.content)
    voiceLine = AudioSegment.from_wav("audioResponse.wav")
    play(voiceLine)
