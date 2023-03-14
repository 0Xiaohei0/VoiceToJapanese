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


# def initialize_speech_recognizer():
#     global speech_recognizer
#     speech_config = speechsdk.SpeechConfig(
#         subscription=SPEECH_KEY, region=SPEECH_REGION)
#     speech_config.speech_recognition_language = language_dict[input_language_name]
#     audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
#     speech_recognizer = speechsdk.SpeechRecognizer(
#         speech_config=speech_config, audio_config=audio_config)
#     # speech_recognizer.recognizing.connect(
#     #     lambda evt: print(f'RECOGNIZING: {evt.result.text}'))
#     speech_recognizer.recognized.connect(
#         lambda evt: start_TTS_pipeline(evt.result.text))
#     speech_recognizer.canceled.connect(showReconitionErrors)

#     speech_recognizer.session_stopped.connect(stop_record_auto)
#     speech_recognizer.canceled.connect(stop_record_auto)
