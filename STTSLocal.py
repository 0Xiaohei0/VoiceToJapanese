import io
import os
import subprocess
from threading import Thread
import time
import traceback
import wave
import keyboard
import pyaudio
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import requests
from enum import Enum
import romajitable
import dict
import translator
from timer import Timer
import whisper
import chatbot
import json
import streamChat
import soundfile as sf
import re


def load_config():
    try:
        with open("config.json", "r") as json_file:
            data = json.load(json_file)

            translator.deepl_api_key = data['deepl_api_key']
            translator.use_deepl = data['use_deepl']
            chatbot.openai_api_key = data['openai_api_key']
            global voice_vox_api_key
            voice_vox_api_key = data['voice_vox_api_key']
            global use_cloud_voice_vox
            use_cloud_voice_vox = data['use_cloud_voice_vox']
            global use_elevenlab
            use_elevenlab = data['use_elevenlab']
            global elevenlab_api_key
            elevenlab_api_key = data['elevenlab_api_key']
            streamChat.twitch_access_token = data['twitch_access_token']
            streamChat.twitch_channel_name = data['twitch_channel_name']
            streamChat.youtube_video_id = data['youtube_video_id']
            chatbot.use_character_ai_token = data['use_character_ai_token']
            chatbot.character_ai_token = data['character_ai_token']

            if (elevenlab_api_key == ''):
                elevenlab_api_key = os.getenv("ELEVENLAB_API_KEY")

    except:
        print("Unable to load JSON file.")
        print(traceback.format_exc())

def save_config(key, value):
    config = None
    try:
        with open("config.json", "r") as json_file:
            config = json.load(json_file)
            config[key] = value
        with open("config.json", "w") as json_file:
            json_object = json.dumps(config, indent=4)
            json_file.write(json_object)
    except:
        print("Unable to load JSON file.")
        print(traceback.format_exc())


input_device_id = None
output_device_id = None

VOICE_VOX_URL_HIGH_SPEED = "https://api.su-shiki.com/v2/voicevox/audio/"
VOICE_VOX_URL_LOW_SPEED = "https://api.tts.quest/v3/voicevox/synthesis"
VOICE_VOX_URL_LOCAL = "127.0.0.1"

VOICE_OUTPUT_FILENAME = "audioResponse.wav"

use_elevenlab = False
elevenlab_api_key = ''
elevenlab_voiceid = ''
use_cloud_voice_vox = False
voice_vox_api_key = ''
speakersResponse = None
voicevox_server_started = False
speaker_id = 3
mic_mode = 'open mic'
MIC_OUTPUT_FILENAME = "PUSH_TO_TALK_OUTPUT_FILE.wav"
PUSH_TO_RECORD_KEY = '5'
use_ingame_push_to_talk_key = False
ingame_push_to_talk_key = 'f'

whisper_filter_list = ['you', 'thank you.',
                       'thanks for watching.', "Thank you for watching."]
pipeline_elapsed_time = 0
TTS_pipeline_start_time = 0
pipeline_timer = Timer()
step_timer = Timer()
model = None

ambience_adjusted = False


def initialize_model():
    global model
    model = whisper.load_model("base")


def start_voicevox_server():
    global voicevox_server_started
    if (voicevox_server_started):
        return
    # start voicevox server
    subprocess.Popen("VOICEVOX\\vv-engine\\run.exe")
    voicevox_server_started = True

def initialize_speakers():
    global speakersResponse
    if (not voicevox_server_started):
        start_voicevox_server()
    url = f"http://{VOICE_VOX_URL_LOCAL}:50021/speakers"
    while True:
        try:
            response = requests.request("GET", url)
            break
        except:
            print("Waiting for voicevox to start... ")
            time.sleep(0.5)
    speakersResponse = response.json()


def get_speaker_names():
    global speakersResponse
    if (speakersResponse == None):
        initialize_speakers()
    speakerNames = list(
        map(lambda speaker: speaker['name'],  speakersResponse))
    return speakerNames


def get_speaker_styles(speaker_name):
    global speakersResponse
    if (speakersResponse == None):
        initialize_speakers()
    speaker_styles = next(
        speaker['styles'] for speaker in speakersResponse if speaker['name'] == speaker_name)

    print(speaker_styles)
    return speaker_styles

def download_wav_file(wav_url, filename):
    r = requests.get(wav_url, stream=True)
    if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('audio'):
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(4096):
                f.write(chunk)
        print("Audio file saved.")
        return True
    else:
        print("Download did not return an audio file!")
        return False
    
def wait_for_audio(audio_status_url, max_wait=10):
    waited = 0
    while waited < max_wait:
        status_resp = requests.get(audio_status_url)
        try:
            status_data = status_resp.json()
            if status_data.get('isAudioReady'):
                return True
            if status_data.get('isAudioError'):
                print("Audio generation failed.")
                return False
        except Exception as e:
            print(f"Failed to parse audio status: {e}")
            return False
        time.sleep(1)
        waited += 1
    print("Timed out waiting for audio.")
    return False

recording = False
auto_recording = False
logging_eventhandlers = []

voice_name = '四国めたん'
input_language_name = 'English'

# Stores variable for play original function
last_input_text = ''
last_voice_param = None
last_input_language = ''

language_dict = dict.language_dict


def start_record_auto():
    log_message("Recording...")
    global auto_recording
    auto_recording = True
    thread = Thread(target=start_STTS_loop)
    thread.start()


def start_record_auto_chat():
    log_message("Recording...")
    global auto_recording
    auto_recording = True
    thread = Thread(target=start_STTS_loop_chat)
    thread.start()


def stop_record_auto():
    global auto_recording, ambience_adjusted
    auto_recording = False
    log_message("Recording Stopped")
    ambience_adjusted = False


def cloud_synthesize(text, speaker_id, api_key=''):
    global pipeline_elapsed_time
    url = ''
    new_text = text.replace('"', '').replace("'", "").strip()
    if api_key == '':
        print('No api key detected, sending request to low speed server.')
        url = f"{VOICE_VOX_URL_LOW_SPEED}?text={new_text}&speaker={speaker_id}"
    else:
        print(f'Api key {api_key} detected, sending request to high speed server.')
        url = f"{VOICE_VOX_URL_HIGH_SPEED}?text={new_text}&speaker={speaker_id}&key={api_key}"
    print(f"Sending POST request to: {url}")
    response = requests.post(url)
    print(f'response: {response}')
    if api_key == '':
        response_json = response.json()
        if not response_json.get("success"):
            print("Synthesis API did not succeed.")
            print(response_json)
            return False
        audio_status_url = response_json.get('audioStatusUrl')
        wav_url = response_json.get('wavDownloadUrl')
        if not audio_status_url or not wav_url:
            print("Missing audioStatusUrl or wavDownloadUrl.")
            return False
        if not wait_for_audio(audio_status_url):
            print("Audio file was not ready.")
            return False
        # Download the audio file
        if not download_wav_file(wav_url, VOICE_OUTPUT_FILENAME):
            print("Failed to save audio file.")
            return False
    else:
        if response.status_code == 200 and 'audio' in response.headers.get('Content-Type', ''):
            wav_bytes = response.content
            with open(VOICE_OUTPUT_FILENAME, "wb") as file:
                file.write(wav_bytes)
        else:
            print("Did not receive audio data from high speed server!")
            return False

    return True

def synthesize_audio(text, speaker_id):
    global use_cloud_voice_vox, voice_vox_api_key
    global use_elevenlab
    if (use_elevenlab):
        elevenlab_synthesize(text)
    else:
        if (use_cloud_voice_vox):
            cloud_synthesize(text, speaker_id, api_key=voice_vox_api_key)
        else:
            local_synthesize(text, speaker_id)


def local_synthesize(text, speaker_id):
    VoiceTextResponse = requests.request(
        "POST", f"http://127.0.0.1:50021/audio_query?text={text}&speaker={speaker_id}")
    AudioResponse = requests.request(
        "POST", f"http://127.0.0.1:50021/synthesis?speaker={speaker_id}", data=VoiceTextResponse)

    with open(VOICE_OUTPUT_FILENAME, "wb") as file:
        file.write(AudioResponse.content)


def elevenlab_synthesize(message):
    global elevenlab_api_key
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{elevenlab_voiceid}/stream'
    headers = {
        'accept': '*/*',
        'xi-api-key': elevenlab_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': message,
        'model_id': "eleven_multilingual_v1",
        'voice_settings': {
            'stability': 0.75,
            'similarity_boost': 0.75,
            'style': .75, # Available on Multilingual models
            'use_speaker_boost': True, # Boost the similarity of the synthesized speech and the voice at the cost of some generation speed.
            "speed": 1.0  # If you plan to use speed later
        }
    }
    print(f"Sending POST request to: {url}")
    response = requests.post(url, headers=headers, json=data, stream=True)
    print(response)
    audio_content = AudioSegment.from_file(
        io.BytesIO(response.content), format="mp3")
    audio_content.export(VOICE_OUTPUT_FILENAME, 'wav')

def PlayAudio():
    # voiceLine = AudioSegment.from_wav(VOICE_OUTPUT_FILENAME)
    # play(voiceLine)
    # open the file for reading.
    wf = wave.open(VOICE_OUTPUT_FILENAME, 'rb')

    # create an audio object
    p = pyaudio.PyAudio()

    global output_device_id
    # length of data to read.
    chunk = 1024
    # open stream based on the wave object which has been input.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=output_device_id)

    # read data (based on the chunk size)
    data = wf.readframes(chunk)

    # play stream (looping from beginning of file to the end)
    while data:
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)

    # cleanup stuff.
    wf.close()
    stream.close()
    p.terminate()


def push_to_talk():
    while True:
        a = keyboard.read_key()
        if (a == PUSH_TO_RECORD_KEY):
            log_message(f"push to talk started...")
            audio = pyaudio.PyAudio()
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            # Open audio stream
            global input_device_id
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK, input_device_index=input_device_id)

            # Initialize frames array to store audio data
            frames = []

            # Record audio data
            while True:
                data = stream.read(CHUNK)
                frames.append(data)
                if not keyboard.is_pressed(PUSH_TO_RECORD_KEY):
                    break

            # Stop recording and close audio stream
            log_message("push to talk ended")
            stream.stop_stream()
            stream.close()

            # Save recorded audio data to file
            audio_segment = AudioSegment(
                data=b''.join(frames),
                sample_width=audio.get_sample_size(FORMAT),
                frame_rate=RATE,
                channels=CHANNELS
            )

            audio_segment.export(MIC_OUTPUT_FILENAME, format="wav")
            break


def start_STTS_loop():
    global auto_recording
    while auto_recording:
        start_STTS_pipeline()


def start_STTS_loop_chat():
    global auto_recording
    while auto_recording:
        start_STTS_pipeline(use_chatbot=True)

import asyncio

def start_STTS_pipeline(use_chatbot=False):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    global pipeline_elapsed_time
    global step_timer
    global pipeline_timer
    global mic_mode
    audio = None
    if (mic_mode == 'open mic'):
        # record audio
        # obtain audio from the microphone
        r = sr.Recognizer()
        global input_device_id, ambience_adjusted
        with sr.Microphone(device_index=input_device_id) as source:
            if (not ambience_adjusted):
                log_message("Adjusting for ambient noise...")
                r.adjust_for_ambient_noise(source)
                ambience_adjusted = True
            log_message("Say something!")
            audio = r.listen(source)

        global auto_recording
        if not auto_recording:
            return

        with open(MIC_OUTPUT_FILENAME, "wb") as file:
            file.write(audio.get_wav_data())
    elif (mic_mode == 'push to talk'):
        push_to_talk()
    log_message("recording compelete, sending to whisper")

    # send audio to whisper
    pipeline_timer.start()
    step_timer.start()
    input_text = ''
    try:
        global model
        if (model == None):
            initialize_model()
        global input_language_name
        print(input_language_name)
        audio = whisper.load_audio(MIC_OUTPUT_FILENAME)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        if (input_language_name == "Auto"):
            lanuguage = None
        else:
            lanuguage = input_language_name.lower()
        options = whisper.DecodingOptions(task='transcribe' if input_language_name == "Japanese" else 'translate',
                                          language=lanuguage, without_timestamps=True, fp16=False if model.device == 'cpu' else None)
        result = whisper.decode(model, mel, options)
        input_text = result.text
    except sr.UnknownValueError:
        log_message("Whisper could not understand audio")
    except sr.RequestError as e:
        log_message("Could not request results from Whisper")
    global whisper_filter_list
    if (input_text == ''):
        return
    log_message(f'Input: {input_text} ({step_timer.end()}s)')

    print(f'looking for {input_text.strip().lower()} in {whisper_filter_list}')
    if (input_text.strip().lower() in whisper_filter_list):
        log_message(f'Input {input_text} was filtered.')
        return
    with open("Input.txt", "w", encoding="utf-8") as file:
        file.write(input_text)
    pipeline_elapsed_time += pipeline_timer.end()
    if (use_chatbot):
        log_message("recording compelete, sending to chatbot")
        loop.run_until_complete(chatbot.message_queue.put(input_text))
    else:
        start_TTS_pipeline(input_text)


def start_TTS_pipeline(input_text):
    global voice_name
    global speaker_id
    global pipeline_elapsed_time
    # remove text between astrisks
    input_text = re.sub(r'\*.*?\*', '', input_text)
    # remove emojis
    input_text = re.sub(r'[^\w\s,.!?]', '', input_text)
    # Remove text between brackets
    input_text = re.sub(r'\(.*?\)', '', input_text)
    print(f"filtered input: {input_text}")
    pipeline_timer.start()
    if (use_elevenlab):
        outputLanguage = 'en'
    else:
        outputLanguage = 'ja'
    global input_language_name
    if (input_language_name == "Japanese"):
        inputLanguage = 'ja'
    else:
        inputLanguage = 'en'
    print(f"inputLanguage: {inputLanguage}, outputLanguage: {outputLanguage}")
    translate = inputLanguage != outputLanguage
    if (translate):
        step_timer.start()
        input_processed_text = translator.translate(
            input_text, inputLanguage, outputLanguage)
        if outputLanguage == 'ja':
            input_processed_text = input_processed_text.replace(' ', '')
        log_message(
            f'Translation: {input_processed_text} ({step_timer.end()}s)')
    else:
        input_processed_text = input_text

    # filter special characters
    filtered_text = ''
    for char in input_processed_text:
        if char != "*":
            filtered_text += char

    with open("translation.txt", "w", encoding="utf-8") as file:
        file.write(filtered_text)
    step_timer.start()
    synthesize_audio(
        filtered_text, speaker_id)
    log_message(
        f"Speech synthesized for text [{filtered_text}] ({step_timer.end()}s)")
    log_message(
        f'Total time: ({round(pipeline_elapsed_time + pipeline_timer.end(),2)}s)')
    print(f"ingame_push_to_talk_key: {ingame_push_to_talk_key}")
    global use_ingame_push_to_talk_key
    if (use_ingame_push_to_talk_key and ingame_push_to_talk_key != ''):
        keyboard.press(ingame_push_to_talk_key)
    PlayAudio()
    if (use_ingame_push_to_talk_key and ingame_push_to_talk_key != ''):
        keyboard.release(ingame_push_to_talk_key)
    global last_input_text
    last_input_text = input_text
    global last_input_language
    last_input_language = inputLanguage
    global last_voice_param
    last_voice_param = speaker_id
    pipeline_elapsed_time = 0


def playOriginal():
    global last_input_text
    global last_voice_param
    global last_input_language
    global input_language_name
    inputLanguage = language_dict[input_language_name][:2]
    last_input_text_processed = ''
    if (last_input_language != 'en'):
        last_input_text_processed = translator.translate(
            last_input_text, inputLanguage, 'en')
    else:
        last_input_text_processed = last_input_text
    text_ja = romajitable.to_kana(last_input_text_processed).katakana
    text_ja = text_ja.replace('・', '')
    synthesize_audio(text_ja, last_voice_param)
    log_message(f'playing input: {text_ja}')

def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)

def change_input_language(input_lang_name):
    global input_language_name
    input_language_name = input_lang_name
