import pyaudio
import wave
import keyboard
import requests

# Define constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "Output/output.wav"

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
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))

    with open(WAVE_OUTPUT_FILENAME, "rb") as f:
        file_content = f.read()

    headers = {
        "Content-Type": "multipart/form-data; boundary={}'.format(boundary) "}
    data = {"audio_file": (WAVE_OUTPUT_FILENAME, file_content, "audio/wav")}
    response = requests.post(
        "http://localhost:9000/asr?task=transcribe&language=en&output=txt", headers=headers, data=file_content)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print("Error: ", response.status_code)
        data = response.json()
        print(data)

    waveFile.close()

audio.terminate()
