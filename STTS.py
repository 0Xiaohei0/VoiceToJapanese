import os
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import keyboard
import requests
import json
import azure.cognitiveservices.speech as speechsdk
from enum import Enum


MIC_OUTPUT_FILENAME = "Output/output.mp3"
audio = pyaudio.PyAudio()

recording = False


def start_record():
    print("Recording...")

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

    audio_segment.export(MIC_OUTPUT_FILENAME, format="mp3")


def stop_record():
    global recording
    recording = False
    print("Recording Stopped")
    start_STTS_pipeline(
        azure_tts_voice_name='ja-JP-AoiNeural', SPEAKER_ID=VoiceVoxSpeaker.九州そら_1.value, inputLanguage='zh', outputLanguage='ja'
    )


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
        print(f'Input: {output}')
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
        print(f'Translation: {text_output}')
        return text_output
    else:
        print("Error retrieving translation:")
        print(responseJSON)
        return ""


def sendTextToSyntheizer(text, speaker_id):
    url = f"http://127.0.0.1:50021/audio_query?text={text}&speaker={speaker_id}"

    VoiceTextResponse = requests.request("POST", url)

    url = f"http://127.0.0.1:50021/synthesis?speaker={speaker_id}"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = VoiceTextResponse
    AudioResponse = requests.request(
        "POST", url, data=payload)
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


def PlayAudio(audioBytes):
    with open("audioResponse.wav", "wb") as file:
        file.write(audioBytes)
    voiceLine = AudioSegment.from_wav("audioResponse.wav")
    play(voiceLine)


def start_STTS_pipeline(
        azure_tts_voice_name='ja-JP-AoiNeural', SPEAKER_ID=VoiceVoxSpeaker.九州そら_1.value, inputLanguage='zh', outputLanguage='ja'
):

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
        AudioResponse = sendTextToSyntheizer(input_processed_text,SPEAKER_ID)
        PlayAudio(AudioResponse.content)
