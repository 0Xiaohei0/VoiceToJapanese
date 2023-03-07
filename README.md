# Voice To Japanese
(Please unmute the video)


https://user-images.githubusercontent.com/24196833/223325680-87ec37f3-7f15-4b83-a288-2d753ca4b4a3.mp4

Voice To Japanese is a python script that turns your microphone input into synthesized audio in Japanese. The Japanese audio output can redirected to your in-game voice chat, discord etc. via a virtual audio cable. It uses OpenAI Whisper API to transcribe microphone input into text. The text is then passed to DeepL Translate to convert into Japanese. Lastly Voice Vox is used to synthesize the Japanese audio output. 

## Installation

### Step 1: Run two docker containers for VoiceVox and Whisper:
Download docker: 
[https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

Open command prompt and type this to start VoiceVox:
```cmd
docker run --rm --gpus all -p 50021:50021 --name=voicevox  -m 4g voicevox/voicevox_engine:nvidia-ubuntu20.04-latest
```

Open a new command prompt and type this to start Whisper:
```cmd
docker run -d --gpus all -p 9000:9000 --name=whisper-medium  -m 8g -e ASR_MODEL=medium onerahmet/openai-whisper-asr-webservice:latest-gpu
```

### Step 2: Setup DeepL translate API key (optional)
(If you skip this step, toggle translation off during use)

Sign up for a DeepL account and get the API key: 
[https://www.deepl.com/translator](https://www.deepl.com/translator)

Create a system environment variables called ```translation-service-api-token``` and set the value to your API key.

## Usage
Run the python script with 
```
python audioRecord.py
```

Hold the record key to start recording (default key is 7)

Release the record key to stop recording.

The result of text-to-speech and translation will be printed to the console.

The audio file in Japanese will be created in the current directory and played through your default audio output device.

Console output:
```
Recording... (translate = True)
Recording stopped.
Input: Hello everyone.
Japanese: みなさん、こんにちは。
```

You can toggle the translation function by pressing the toggle translate key to to  (default key is 0)

# Inspiration

This project was inspired by this video：
https://youtu.be/UY7sRB60wZ4

Credit to
[@sociallyineptweeb](https://www.youtube.com/@sociallyineptweeb)
for the ideas and APIs used.
