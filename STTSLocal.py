from threading import Thread
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import requests
from enum import Enum
import romajitable
import dict
import translator
from voicevox import vboxclient

# start voicevox server
vboxapp = vboxclient.voiceclient()  # Class「voiceclient」を利用可能にする
# vboxapp.vbox_dl()  # インストーラーをダウンロード&実行
vboxapp.app(exepass="VOICEVOX\\run.exe")

VOICE_VOX_URL = "20.85.153.114"
VOICE_VOX_URL_LOCAL = "127.0.0.1"
use_local_voice_vox = False


recording = False
auto_recording = False
logging_eventhandlers = []

voice_name = '四国めたん'
input_language_name = 'English'

# Stores variable for play original function
last_input_text = ''
last_voice_param = None
last_input_language = ''

speech_recognizer = None


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


def start_STTS_loop():
    global auto_recording
    while auto_recording:
        start_STTS_pipeline()


def start_STTS_pipeline():
    # record audio
    audio = None
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
    start_TTS_pipeline(input_text)


def start_TTS_pipeline(input_text):
    global voice_name
    inputLanguage = language_dict[input_language_name][:2]
    voiceparam = voicename_to_callparam_dict[voice_name]
    outputLanguage = language_dict[voiceparam.voice_language][:2]
    # print(f"inputLanguage: {inputLanguage}, outputLanguage: {outputLanguage}")
    translate = inputLanguage != outputLanguage
    if (translate):
        input_processed_text = translator.translate(
            input_text, inputLanguage, outputLanguage)
        log_message(f'Translation: {input_processed_text}')
    else:
        input_processed_text = input_text

    play_audio_from_local_syntheizer(
        input_processed_text, voiceparam.voice_id)

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
    play_audio_from_local_syntheizer(text_ja, last_voice_param.voice_id)
    log_message(f'playing input: {text_ja}')


def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)


def change_input_language(input_lang_name):
    global input_language_name
    input_language_name = input_lang_name
