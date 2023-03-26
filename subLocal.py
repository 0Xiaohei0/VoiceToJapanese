import dict
import whisper
import speech_recognition as sr
from translator import translate
import torch
from queue import Queue
import time
from threading import Thread


model = whisper.load_model("base")
text_change_eventhandlers = []
language_dict = dict.language_dict

m_phrase_time_limit = 5
input_language_name = 'Japanese'
output_language_name = 'English'
is_running = False
device_idx = None
# obtain audio from the microphone
r = sr.Recognizer()

audio_queue = Queue()


def start():
    global is_running
    is_running = True
    thread_recording = Thread(target=start_recording_loop)
    thread_recording.start()
    thread_transcription = Thread(target=start_transcription_loop)
    thread_transcription.start()


def stop():
    global is_running
    is_running = False


def check_gpu_status():
    status = torch.cuda.is_available()
    print(f'Using GPU: {torch.cuda.is_available()}')
    return status


def record_audio():
    global audio_queue
    global m_phrase_time_limit
    global device_idx
    with sr.Microphone(device_index=device_idx) as source:
        if (device_idx == None):
            print("Recording with default microphone...")
        else:
            print(f"Recording with deviceid: {device_idx}...")
        audio = r.listen(source, timeout=None,
                         phrase_time_limit=m_phrase_time_limit)
        audio_queue.put(audio)
        print("Added audio to process queue.")


def process_audio_queue():
    if (not audio_queue.empty()):
        audio = audio_queue.get()
        try:
            text = r.recognize_whisper(
                audio, translate=True, language="japanese")
            send_update_text_event(text)
        except sr.UnknownValueError:
            print("Whisper could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Whisper")


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
    while is_running:
        record_audio()


def start_transcription_loop():
    while is_running:
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
