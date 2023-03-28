from threading import Thread
import time
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
from voicevox import vboxclient
from timer import Timer
import whisper

VOICE_VOX_URL_HIGH_SPEED = "https://api.su-shiki.com/v2/voicevox/audio/"
VOICE_VOX_URL_LOW_SPEED = "https://api.tts.quest/v1/voicevox/"
VOICE_VOX_URL_LOCAL = "127.0.0.1"

VOICE_OUTPUT_FILENAME = "audioResponse.wav"

use_cloud_voice_vox = False
voice_vox_api_key = ''
speakersResponse = None
vboxapp = None
speaker_id = 1
mic_mode = 'open mic'
MIC_OUTPUT_FILENAME = "PUSH_TO_TALK_OUTPUT_FILE.wav"
PUSH_TO_RECORD_KEY = '5'

whisper_filter_list = ['you', 'thank you.', 'thanks for watching.']
pipeline_elapsed_time = 0
TTS_pipeline_start_time = 0
pipeline_timer = Timer()
step_timer = Timer()
model = None


def initialize_model():
    global model
    model = whisper.load_model("base")


def start_voicevox_server():
    global vboxapp
    if (vboxapp != None):
        return
    # start voicevox server
    vboxapp = vboxclient.voiceclient()  # Class「voiceclient」を利用可能にする
    # vboxapp.vbox_dl()  # インストーラーをダウンロード&実行
    vboxapp.app(exepass="VOICEVOX\\run.exe")


def initialize_speakers():
    global speakersResponse
    global vboxapp
    if (vboxapp == None):
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


def stop_record_auto():
    global auto_recording
    auto_recording = False
    log_message("Recording Stopped")


def cloud_synthesize(text, speaker_id, api_key=''):
    global pipeline_elapsed_time
    url = ''
    if (api_key == ''):
        print('No api key detected, sending request to low speed server.')
        url = f"{VOICE_VOX_URL_LOW_SPEED}?text={text}&speaker={speaker_id}"
    else:
        print(
            f'Api key {api_key} detected, sending request to high speed server.')
        url = f"{VOICE_VOX_URL_HIGH_SPEED}?text={text}&speaker={speaker_id}&key={api_key}"
    print(f"Sending POST request to: {url}")
    response = requests.request(
        "POST", url)
    print(f'response: {response}')
    # print(f'response.content: {response.content}')
    wav_bytes = None
    if (api_key == ''):
        response_json = response.json()
        # print(response_json)

        try:
            # download wav file from response
            wav_url = response_json['wavDownloadUrl']
        except:
            print("Failed to get wav download link.")
            print(response_json)
            return
        print(f"Downloading wav response from {wav_url}")
        wav_bytes = requests.get(wav_url).content
    else:
        wav_bytes = response.content

    with open(VOICE_OUTPUT_FILENAME, "wb") as file:
        file.write(wav_bytes)


def syntheize_audio(text, speaker_id):
    global use_cloud_voice_vox
    global voice_vox_api_key
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


def PlayAudio():
    voiceLine = AudioSegment.from_wav(VOICE_OUTPUT_FILENAME)
    play(voiceLine)


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


def start_STTS_pipeline():
    global pipeline_elapsed_time
    global step_timer
    global pipeline_timer
    global mic_mode
    audio = None
    if (mic_mode == 'open mic'):
        # record audio
        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            # log_message("Adjusting for ambient noise...")
            # r.adjust_for_ambient_noise(source)
            log_message("Say something!")
            audio = r.listen(source)

        global auto_recording
        if not auto_recording:
            return

        with open(MIC_OUTPUT_FILENAME, "wb") as file:
            file.write(audio.get_wav_data())

        log_message("recording compelete, sending to whisper")
    elif (mic_mode == 'push to talk'):
        push_to_talk()

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
        options = whisper.DecodingOptions(
            language=input_language_name.lower(), without_timestamps=True, fp16=False if model.device == 'cpu' else None)
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
    start_TTS_pipeline(input_text)


def start_TTS_pipeline(input_text):
    global voice_name
    global speaker_id
    global pipeline_elapsed_time
    pipeline_timer.start()
    inputLanguage = language_dict[input_language_name][:2]
    outputLanguage = 'ja'
    # print(f"inputLanguage: {inputLanguage}, outputLanguage: {outputLanguage}")
    translate = inputLanguage != outputLanguage
    if (translate):
        step_timer.start()
        input_processed_text = translator.translate(
            input_text, inputLanguage, outputLanguage)
        log_message(
            f'Translation: {input_processed_text} ({step_timer.end()}s)')
    else:
        input_processed_text = input_text

    with open("translation.txt", "w", encoding="utf-8") as file:
        file.write(input_processed_text)
    step_timer.start()
    syntheize_audio(
        input_processed_text, speaker_id)
    log_message(
        f"Speech synthesized for text [{input_processed_text}] ({step_timer.end()}s)")
    log_message(
        f'Total time: ({round(pipeline_elapsed_time + pipeline_timer.end(),2)}s)')
    PlayAudio()

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
    syntheize_audio(text_ja, last_voice_param)
    log_message(f'playing input: {text_ja}')


def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)


def change_input_language(input_lang_name):
    global input_language_name
    input_language_name = input_lang_name
