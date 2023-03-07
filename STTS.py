import os
import time
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import requests
import json
import azure.cognitiveservices.speech as speechsdk
from enum import Enum
import romajitable


MIC_OUTPUT_FILENAME = "Output/output.mp3"
audio = pyaudio.PyAudio()

recording = False
auto_recording = False
logging_eventhandlers = []

voice_name = '四国めたん'
input_language_name = 'English'

# Stores variable for play original function
last_input_text = ''
last_voice_param = None
last_input_language = ''


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


class VoiceType(Enum):
    MICROSOFT_AZURE = 0
    VOICE_VOX = 1


class Voice():
    def __init__(self, voice_type, voice_id, voice_language):
        self.voice_type = voice_type
        self.voice_id = voice_id
        self.voice_language = voice_language


voicename_to_callparam_dict = {
    "四国めたん": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.四国めたん_1.value, "Japanese"),
    "四国めたん_2": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.四国めたん_2.value, "Japanese"),
    "四国めたん_3": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.四国めたん_3.value, "Japanese"),
    "四国めたん_4": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.四国めたん_4.value, "Japanese"),
    "四国めたん_5": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.四国めたん_5.value, "Japanese"),
    "四国めたん_6": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.四国めたん_6.value, "Japanese"),
    "春日部つむぎ": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.春日部つむぎ.value, "Japanese"),
    "雨晴はう": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.雨晴はう.value, "Japanese"),
    "冥鳴ひまり": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.冥鳴ひまり.value, "Japanese"),
    "九州そら_1": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.九州そら_1.value, "Japanese"),
    "九州そら_2": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.九州そら_2.value, "Japanese"),
    "九州そら_3": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.九州そら_3.value, "Japanese"),
    "九州そら_4": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.九州そら_4.value, "Japanese"),
    "もち子さん": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.もち子さん.value, "Japanese"),
    "ナースロボタイプ_1": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.ナースロボタイプ_1.value, "Japanese"),
    "ナースロボタイプ_2": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.ナースロボタイプ_2.value, "Japanese"),
    "ナースロボタイプ_3": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.ナースロボタイプ_3.value, "Japanese"),
    "ナースロボタイプ_4": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.ナースロボタイプ_4.value, "Japanese"),
    "小夜SAYO": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.小夜SAYO.value, "Japanese"),
    "櫻歌ミコ_1": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.櫻歌ミコ_1.value, "Japanese"),
    "櫻歌ミコ_2": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.櫻歌ミコ_2.value, "Japanese"),
    "櫻歌ミコ_3": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.櫻歌ミコ_3.value, "Japanese"),
    "No7_1": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.No7_1.value, "Japanese"),
    "No7_2": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.No7_2.value, "Japanese"),
    "No7_3": Voice(VoiceType.VOICE_VOX.value, VoiceVoxSpeaker.No7_3.value, "Japanese"),
    "JP-Aoi": Voice(VoiceType.MICROSOFT_AZURE.value, "ja-JP-AoiNeural", "Japanese"),
    "CN-Xiaoyi": Voice(VoiceType.MICROSOFT_AZURE.value, "zh-CN-XiaoyiNeural", "Chinese"),
}

language_dict = {'English': "en-US",
                 "Japanese": "ja-JP",
                 "Chinese": "zh-CN"}

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get(
    'SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
speech_config.speech_recognition_language = language_dict[input_language_name]
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config, audio_config=audio_config)
# speech_recognizer.recognizing.connect(
#     lambda evt: print(f'RECOGNIZING: {evt.result.text}'))
speech_recognizer.recognized.connect(
    lambda evt: start_TTS_pipeline(evt.result.text))


def start_record():
    log_message("Recording...")

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    # Initialize frames array to store audio data
    frames = []

    # Record audio data
    global recording
    recording = True
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if not recording:
            break

    # Stop recording and close audio stream
    log_message("Recording stopped.")
    stream.stop_stream()
    stream.close()

    # Save recorded audio data to file
    audio_segment = AudioSegment(
        data=b''.join(frames),
        sample_width=audio.get_sample_size(FORMAT),
        frame_rate=RATE,
        channels=CHANNELS
    )

    audio_segment.export(MIC_OUTPUT_FILENAME, format="mp3")


def stop_record():
    global recording
    recording = False
    log_message("Recording Stopped")
    start_STTS_pipeline(
        azure_tts_voice_name='ja-JP-AoiNeural', SPEAKER_ID=VoiceVoxSpeaker.九州そら_1.value, inputLanguage='zh', outputLanguage='ja'
    )


def start_record_auto():
    log_message("Recording...")
    global auto_recording
    global speech_recognizer
    auto_recording = True
    speech_recognizer.start_continuous_recognition()
    while auto_recording:
        speech_config.speech_recognition_language = language_dict[input_language_name]
        time.sleep(.5)


def stop_record_auto():
    global auto_recording
    global speech_recognizer
    auto_recording = False
    speech_recognizer.stop_continuous_recognition()
    log_message("Recording Stopped")


speech_recognizer.session_stopped.connect(stop_record_auto)
speech_recognizer.canceled.connect(stop_record_auto)


def sendAudioToWhisper(file_name, input_language):
    with open(file_name, "rb") as file:
        url = "http://localhost:9000/asr"

        params = {
            'task': 'transcribe',
            'language': input_language,
            'output': 'txt'
        }
        files = [
            ('audio_file', (MIC_OUTPUT_FILENAME, file, 'audio/mpeg'))
        ]
        SpeechToTextResponse = requests.request(
            "POST", url, params=params, files=files)
        output = SpeechToTextResponse.text.rstrip('\n')
        log_message(f'Input: {output}')
        return output


def sendTextToTranslationService(text, outputLanguage):
    token = os.environ.get("translation-service-api-token")
    # Send text to translation service
    headers = {
        'Authorization': f'DeepL-Auth-Key {token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'text={text}&target_lang={outputLanguage.upper()}'
    translationResponse = requests.post(
        'https://api-free.deepl.com/v2/translate', headers=headers, data=data.encode('utf-8'))
    responseJSON = json.loads(
        translationResponse.content.decode('utf-8'))
    if "translations" in responseJSON:
        text_output = responseJSON['translations'][0]['text']
        log_message(f'Translation: {text_output}')
        return text_output
    else:
        log_message("Error retrieving translation:")
        log_message(responseJSON)
        return ""


def sendTextToSyntheizer(text, speaker_id):
    url = f"http://20.246.162.198:50021/audio_query?text={text}&speaker={speaker_id}"

    VoiceTextResponse = requests.request("POST", url)

    url = f"http://20.246.162.198:50021/synthesis?speaker={speaker_id}"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = VoiceTextResponse
    AudioResponse = requests.request(
        "POST", url, data=payload)
    log_message("Speech synthesized for text [{}]".format(text))
    return AudioResponse


def CallAzureTTS(text, azure_tts_voice_name):
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get(
        'SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    audio_config = speechsdk.audio.AudioOutputConfig(
        use_default_speaker=True)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = azure_tts_voice_name

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        log_message("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        log_message("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                log_message("Error details: {}".format(
                    cancellation_details.error_details))
                log_message(
                    "Did you set the speech resource key and region values?")


def PlayAudio(audioBytes):
    with open("audioResponse.wav", "wb") as file:
        file.write(audioBytes)
    voiceLine = AudioSegment.from_wav("audioResponse.wav")
    play(voiceLine)

    # Examples of azure_tts_voice_name:
    # Female
    # ja-JP-AoiNeural ja-JP-NanamiNeural ja-JP-MayuNeural ja-JP-ShioriNeural
    # zh-CN-XiaoyiNeural zh-CN-XiaoshuangNeural
    # India en-IN-NeerjaNeural
    # Child en-GB-MaisieNeural
    # US en-US-AmberNeural
    #
    # Male
    # ja-JP-KeitaNeural

    # example of language codes
    # "zh": "chinese", "ja": "japanese", "en": "english", "ko": "korean"


def start_STTS_pipeline(
        azure_tts_voice_name='ja-JP-AoiNeural', SPEAKER_ID=VoiceVoxSpeaker.九州そら_1.value, inputLanguage='zh', outputLanguage='ja'
):
    use_microsoft_azure_tts = False

    input_text = sendAudioToWhisper(MIC_OUTPUT_FILENAME, inputLanguage)
    translate = inputLanguage != outputLanguage

    if (translate):
        input_processed_text = sendTextToTranslationService(
            input_text, outputLanguage)
    else:
        input_processed_text = input_text

    if (use_microsoft_azure_tts):
        CallAzureTTS(input_processed_text, azure_tts_voice_name)
    else:
        AudioResponse = sendTextToSyntheizer(input_processed_text, SPEAKER_ID)
        PlayAudio(AudioResponse.content)
    log_message('')


def start_TTS_pipeline(input_text):
    if (input_text == ''):
        return
    log_message(f'Input: {input_text}')
    global voice_name
    inputLanguage = language_dict[input_language_name][:2]
    voiceparam = voicename_to_callparam_dict[voice_name]
    outputLanguage = language_dict[voiceparam.voice_language][:2]
    # print(f"inputLanguage: {inputLanguage}, outputLanguage: {outputLanguage}")
    use_microsoft_azure_tts = voiceparam.voice_type == VoiceType.MICROSOFT_AZURE.value
    translate = inputLanguage != outputLanguage
    if (translate):
        input_processed_text = sendTextToTranslationService(
            input_text, outputLanguage)
    else:
        input_processed_text = input_text
    if (use_microsoft_azure_tts):
        CallAzureTTS(input_processed_text, voiceparam.voice_id)
    else:
        AudioResponse = sendTextToSyntheizer(
            input_processed_text, voiceparam.voice_id)
        PlayAudio(AudioResponse.content)

    global last_input_text
    last_input_text = input_text
    global last_input_language
    last_input_language = inputLanguage
    global last_voice_param
    last_voice_param = voiceparam


def playOriginal():
    global last_input_text
    global last_voice_param
    global last_input_language
    last_input_text_processed = ''
    if (last_input_language != 'en'):
        last_input_text_processed = sendTextToTranslationService(
            last_input_text, 'en')
    else:
        last_input_text_processed = last_input_text
    text_ja = romajitable.to_kana(last_input_text_processed).katakana
    text_ja = text_ja.replace('・', '')
    if (last_voice_param.voice_type == VoiceType.MICROSOFT_AZURE.value):
        CallAzureTTS(text_ja, last_voice_param.voice_id)
    else:
        PlayAudio(sendTextToSyntheizer(
            text_ja, last_voice_param.voice_id).content)
    log_message(f'playing input: {text_ja}')


def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)
