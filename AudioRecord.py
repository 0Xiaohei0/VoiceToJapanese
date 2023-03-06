import os
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import keyboard
import requests
import json
import azure.cognitiveservices.speech as speechsdk
from enum import Enum


class VoiceVoxSpeaker(Enum):
    四国めたん_1 = 2
    四国めたん_2 = 0
    四国めたん_3 = 6
    四国めたん_4 = 4
    四国めたん_5 = 36
    四国めたん_6 = 37

    春日部つむぎ = 8
    雨晴はう = 10
    冥鳴ひまり = 14

    九州そら_1 = 16
    九州そら_2 = 15
    九州そら_3 = 17
    九州そら_4 = 19

    もち子さん = 20
    剣崎雌雄 = 21  # male

    ナースロボタイプ_1 = 47
    ナースロボタイプ_2 = 48
    ナースロボタイプ_3 = 49
    ナースロボタイプ_4 = 50

    小夜SAYO = 46
    櫻歌ミコ_1 = 43
    櫻歌ミコ_2 = 44
    櫻歌ミコ_3 = 45

    No7_1 = 29
    No7_2 = 30
    No7_3 = 31


SPEAKER_ID = VoiceVoxSpeaker.九州そら_1.value

# Female
# ja-JP-AoiNeural ja-JP-NanamiNeural ja-JP-MayuNeural ja-JP-ShioriNeural
# zh-CN-XiaoyiNeural zh-CN-XiaoshuangNeural

# Male
# ja-JP-KeitaNeural

# India en-IN-NeerjaNeural
# Child en-GB-MaisieNeural
# US en-US-AmberNeural
azure_tts_voice_name = 'ja-JP-AoiNeural'

use_microsoft_azure_tts = False

# input language used by transcriber
inputLanguage = 'zh'
# output language used by the translator
outputLanguage = 'ja'
# "zh": "chinese", "ja": "japanese", "en": "english", "ko": "korean"
if (use_microsoft_azure_tts):
    outputLanguage = azure_tts_voice_name[0:2]

translate = inputLanguage != outputLanguage
audio = pyaudio.PyAudio()

receive_input_from_text = False
text_input_translate = True
text = ''

repeat_in_chinese = True

if (use_microsoft_azure_tts):
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get(
        'SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = azure_tts_voice_name

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)


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

        params = {
            'task': 'transcribe',
            'language': inputLanguage,
            'output': 'txt'
        }
        files = [
            ('audio_file', (OUTPUT_FILENAME, file, 'audio/mpeg'))
        ]
        SpeechToTextResponse = requests.request(
            "POST", url, params=params, files=files)
        output = SpeechToTextResponse.text.rstrip('\n')
        print(f'Input: {output}')
        return output


def sendTextToTranslationService(text_output):
    token = os.environ.get("translation-service-api-token")
    # Send text to translation service
    headers = {
        'Authorization': f'DeepL-Auth-Key {token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'text={text_output}&target_lang={outputLanguage.upper()}'
    translationResponse = requests.post(
        'https://api-free.deepl.com/v2/translate', headers=headers, data=data.encode('utf-8'))
    responseJSON = json.loads(
        translationResponse.content.decode('utf-8'))
    if "translations" in responseJSON:
        text_output = responseJSON['translations'][0]['text']
        print(f'Translation: {text_output}')
        return text_output
    else:
        print("Error retrieving translation:")
        print(responseJSON)
        return ""


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


def CallAzureTTS(text):
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


if (receive_input_from_text):
    input_processed_text = text
    if (text_input_translate):
        input_processed_text = sendTextToTranslationService(text)

    if (use_microsoft_azure_tts):
        CallAzureTTS(input_processed_text)
    else:
        AudioResponse = sendTextToSyntheizer(input_processed_text)
        with open("audioResponse.wav", "wb") as file:
            file.write(AudioResponse.content)
        voiceLine = AudioSegment.from_wav("audioResponse.wav")
        play(voiceLine)
        if (repeat_in_chinese):
            # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
            speech_config = speechsdk.SpeechConfig(subscription=os.environ.get(
                'SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
            audio_config = speechsdk.audio.AudioOutputConfig(
                use_default_speaker=True)

            # The language of the voice that speaks.
            speech_config.speech_synthesis_voice_name = azure_tts_voice_name

            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=audio_config)
            azure_tts_voice_name = 'zh-CN-XiaoshuangNeural'
            CallAzureTTS(text)
    exit()


# Define constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
OUTPUT_FILENAME = "Output/output.mp3"


PUSH_TO_RECORD_KEY = '7'
NO_TRANSLATE_KEY = '0'

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
    input_text = sendAudioToWhisper()
    if (translate):
        input_processed_text = sendTextToTranslationService(input_text)
    else:
        input_processed_text = input_text
    if (use_microsoft_azure_tts):
        CallAzureTTS(input_processed_text)
    else:
        AudioResponse = sendTextToSyntheizer(input_processed_text)
        with open("audioResponse.wav", "wb") as file:
            file.write(AudioResponse.content)
        voiceLine = AudioSegment.from_wav("audioResponse.wav")
        play(voiceLine)
        if (repeat_in_chinese):
            if (not use_microsoft_azure_tts):
                # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
                speech_config = speechsdk.SpeechConfig(subscription=os.environ.get(
                    'SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
                audio_config = speechsdk.audio.AudioOutputConfig(
                    use_default_speaker=True)

            # The language of the voice that speaks.
            speech_config.speech_synthesis_voice_name = 'zh-CN-XiaoshuangNeural'

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config)
        CallAzureTTS(input_text)
