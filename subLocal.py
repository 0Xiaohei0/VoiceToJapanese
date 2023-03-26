import dict
import whisper
import speech_recognition as sr
from translator import translate
import torch
from queue import Queue
import time

model = whisper.load_model("base")
text_change_eventhandlers = []
language_dict = dict.language_dict

phrase_time_limit = 5
input_language_name = 'Japanese'
output_language_name = 'English'

# obtain audio from the microphone
r = sr.Recognizer()

audio_queue = Queue()


def check_gpu_status():
    status = torch.cuda.is_available()
    print(f'Using GPU: {torch.cuda.is_available()}')
    return status


def record_audio():
    global audio_queue
    global phrase_time_limit
    with sr.Microphone() as source:
        audio = r.listen(source, phrase_time_limit)
        audio_queue.put(audio)


def process_audio_queue():
    if (not audio_queue.empty()):
        audio = audio_queue.get()
        text = r.recognize_whisper(audio, translate=True, language="japanese")
        send_update_text_event(text)


def send_audio_to_whisper(audio):
    print("recording compelete, sending to whisper")
    # recognize speech using Google Speech Recognition
    try:
        text = r.recognize_whisper(audio, translate=True, language="japanese")
        print("Whisper thinks you said " + text)
        send_update_text_event(text)
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Whisper")


def start_recording_loop():
    while True:
        record_audio()


def start_transcription_loop():
    while True:
        process_audio_queue()
        time.sleep(0.1)


def set_translation_text(text):
    print(text)


def log_message(message_text):
    print(message_text)


def send_update_text_event(text):
    print(text)
    global text_change_eventhandlers
    for eventhandler in text_change_eventhandlers:
        eventhandler(text)


def change_input_language(input_lang_name):
    global input_language_name
    input_language_name = input_lang_name


def change_output_language(output_lang_name):
    global output_language_name
    output_language_name = output_lang_name
