import dict
import whisper
import pyaudio
from pydub import AudioSegment
import speech_recognition as sr
from translate import translate
from threading import Thread

model = whisper.load_model("base")
text_change_eventhandlers = []
language_dict = dict.language_dict

input_language_name = 'Japanese'
output_language_name = 'English'

# obtain audio from the microphone
r = sr.Recognizer()


def record_audio():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = r.listen(source, phrase_time_limit=5)
        send_audio_to_whisper(audio)


def send_audio_to_whisper(audio):
    print("recording compelete, sending to whisper")
    # recognize speech using Google Speech Recognition
    try:
        text = r.recognize_whisper(audio)
        print("Whisper thinks you said " + text)
        translated_text = translate(
            text, dict.language_dict[input_language_name][:2], dict.language_dict[output_language_name][:2])
        send_update_text_event(translated_text)
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Whisper")


def start_translator():
    while True:
        record_audio()


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
