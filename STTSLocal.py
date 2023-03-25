from threading import Thread
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


VOICE_VOX_URL = "20.85.153.114"
VOICE_VOX_URL_LOCAL = "127.0.0.1"
use_local_voice_vox = False
speakersResponse = None
vboxapp = None
speaker_id = 1
mic_mode = 'open mic'
PUSH_TO_TALK_OUTPUT_FILENAME = "PUSH_TO_TALK_OUTPUT_FILE.wav"
PUSH_TO_RECORD_KEY = '5'


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
    speakersResponse = requests.request("GET", url).json()


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


def sendTextToSyntheizer(text, speaker_id):
    current_voicevox_url = VOICE_VOX_URL
    if (use_local_voice_vox):
        current_voicevox_url = VOICE_VOX_URL_LOCAL
    url = f"http://{current_voicevox_url}:50021/audio_query?text={text}&speaker={speaker_id}"

    VoiceTextResponse = requests.request("POST", url)

    url = f"http://{current_voicevox_url}:50021/synthesis?speaker={speaker_id}"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = VoiceTextResponse
    AudioResponse = requests.request(
        "POST", url, data=payload)
    log_message("Speech synthesized for text [{}]".format(text))
    return AudioResponse


def play_audio_from_local_syntheizer(text, speaker_id):
    vboxapp.run(text=text, speaker=speaker_id,
                filename="audioResponse.wav")  # textとfilenameは好きに変更できます
    voiceLine = AudioSegment.from_wav("audioResponse.wav")
    play(voiceLine)


def PlayAudio(audioBytes):
    with open("audioResponse.wav", "wb") as file:
        file.write(audioBytes)
    voiceLine = AudioSegment.from_wav("audioResponse.wav")
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

            audio_segment.export(PUSH_TO_TALK_OUTPUT_FILENAME, format="wav")
            break


def start_STTS_loop():
    global auto_recording
    while auto_recording:
        start_STTS_pipeline()


def start_STTS_pipeline():
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

        # send audio to whisper
        global input_language_name
        input_text = ''
        log_message("recording compelete, sending to whisper")
    elif (mic_mode == 'push to talk'):
        push_to_talk()
        r = sr.Recognizer()
        with sr.AudioFile(PUSH_TO_TALK_OUTPUT_FILENAME) as source:
            audio = r.record(source)
    try:
        input_text = r.recognize_whisper(
            audio, language=input_language_name.lower())
    except sr.UnknownValueError:
        log_message("Whisper could not understand audio")
    except sr.RequestError as e:
        log_message("Could not request results from Whisper")
    if (input_text == ''):
        return
    log_message(f'Input: {input_text}')
    with open("Input.txt", "w", encoding="utf-8") as file:
        file.write(input_text)
    start_TTS_pipeline(input_text)


def start_TTS_pipeline(input_text):
    global voice_name
    global speaker_id
    inputLanguage = language_dict[input_language_name][:2]
    outputLanguage = 'ja'
    # print(f"inputLanguage: {inputLanguage}, outputLanguage: {outputLanguage}")
    translate = inputLanguage != outputLanguage
    if (translate):
        input_processed_text = translator.translate(
            input_text, inputLanguage, outputLanguage)
        log_message(f'Translation: {input_processed_text}')
    else:
        input_processed_text = input_text

    with open("translation.txt", "w", encoding="utf-8") as file:
        file.write(input_processed_text)
    play_audio_from_local_syntheizer(
        input_processed_text, speaker_id)

    global last_input_text
    last_input_text = input_text
    global last_input_language
    last_input_language = inputLanguage
    global last_voice_param
    last_voice_param = speaker_id


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
    play_audio_from_local_syntheizer(text_ja, last_voice_param)
    log_message(f'playing input: {text_ja}')


def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)


def change_input_language(input_lang_name):
    global input_language_name
    input_language_name = input_lang_name
