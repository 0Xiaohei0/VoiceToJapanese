from enum import Enum
import pyaudio
from pydub import AudioSegment


OUTPUT_FILENAME = "Output/output.mp3"
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

    audio_segment.export(OUTPUT_FILENAME, format="mp3")


def stop_record():
    global recording
    recording = False
    print("Recording Stopped")

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
