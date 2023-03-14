import os
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import requests
import json
import azure.cognitiveservices.speech as speechsdk
from enum import Enum
import romajitable

SPEECH_KEY = os.environ.get('SPEECH_KEY_P')
SPEECH_REGION = os.environ.get('SPEECH_REGION')

text_change_eventhandlers = []

# Translation request
translation_recognizer = None
target_language = ''
speech_translation_config = None
audio_config = None


def initialize_speech_translator():
    global speech_translation_config
    global target_language
    global audio_config
    global translation_recognizer
    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=os.environ.get('SPEECH_KEY_P'), region=os.environ.get('SPEECH_REGION'))
    speech_translation_config.speech_recognition_language = "ja-JP"

    target_language = "en"
    speech_translation_config.add_target_language(target_language)

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    translation_recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=speech_translation_config, audio_config=audio_config)


def start_translator():
    print("Speak into your microphone.")
    translation_recognition_result = translation_recognizer.recognize_once_async().get()

    if translation_recognition_result.reason == speechsdk.ResultReason.TranslatedSpeech:
        send_update_text_event(
            translation_recognition_result.translations[target_language])
        print("Recognized: {}".format(translation_recognition_result.text))
        print("""Translated into '{}': {}""".format(
            target_language,
            translation_recognition_result.translations[target_language]))
    elif translation_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(
            translation_recognition_result.no_match_details))
    elif translation_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = translation_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

    # print("Speak into your microphone.")
    # translation_recognizer.start_continuous_recognition_async()
    # translation_recognizer.recognizing.connect(
    #     lambda evt: print(evt))
    # translation_recognizer.recognized.connect(
    #     lambda evt: set_translation_text(evt.result.text))
    # translation_recognizer.canceled.connect(showReconitionErrors)

    # translation_recognizer.session_stopped.connect(showReconitionErrors)
    # translation_recognizer.canceled.connect(showReconitionErrors)

    # translation_recognizer.stop_continuous_recognition_async()


def showReconitionErrors(translation_recognition_result):
    print(translation_recognition_result)
    translation_recognition_result = translation_recognition_result.result
    if translation_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        log_message("Recognized: {}".format(
            translation_recognition_result.text))
    elif translation_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        log_message("No speech could be recognized: {}".format(
            translation_recognition_result.no_match_details))
    elif translation_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = translation_recognition_result.cancellation_details
        log_message("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            log_message("Error details: {}".format(
                cancellation_details.error_details))


def set_translation_text(text):
    print(text)


def log_message(message_text):
    print(message_text)


def send_update_text_event(text):
    print(text)
    global text_change_eventhandlers
    for eventhandler in text_change_eventhandlers:
        eventhandler(text)


initialize_speech_translator()
