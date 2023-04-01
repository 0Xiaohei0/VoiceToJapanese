# Voice To Japanese (An all-in-one tool for making your own AI Vtuber)

## Overview
Voice To Japanese is an app with UI. You can use it to:
- Host your own AI Vtuber stream. The AI can respond to stream chat.
- Translate your microphone input to Japanese voice and output to other programs (games, discord etc.).
- Have a face-to-face converstaion with an AI Vtuber, whose personality and character description can be customized to your liking.

Full demo and setup guide: https://youtu.be/qEbn44m3Ty0

(please unmute the video)

https://user-images.githubusercontent.com/24196833/229300992-edbb0cbb-fcad-43d2-bb22-805a86b3b00c.mp4

## Installation
### Method 1
1. Download the "VoiceToJapanese-exe.zip" file from the releases section (https://github.com/0Xiaohei0/VoiceToJapanese/releases) 

2. Run the .exe file inside. No additional setup is required.


### Method 2
1. Download "python3.10" from the microsoft store
2. Download "VoiceToJapanese-py.zip" from the releases section (https://github.com/0Xiaohei0/VoiceToJapanese/releases) 
3. Double click setup.bat
4. If you encounter this error, install VS2019 redist by double clicking VC_redist.x64. Then double click setup.bat again.
![image](https://user-images.githubusercontent.com/24196833/229268424-c68708da-2fae-4282-8cb5-e15c2050b961.png)
![image](https://user-images.githubusercontent.com/24196833/229268482-724ecd85-777d-4190-949b-c6a7c85ecaca.png)
5. The program should start, from now on you can use start.bat to start the program more quickly.

Noes: I would recommend downloading the -py version because anti-virus often report false-positive for .exe files. Additionally, with the -py version you can inspect and make changes to all the python code and swap out libraries for running the AI models on GPU.

## Usage
For info on how to use the program, see the full demo video: https://youtu.be/qEbn44m3Ty0 

To play the audio in other programs (discord, apex etc.) Here's a tutorial video:
https://youtu.be/cPGyEeeMxCE
## Links
We have a discord server where you can try this tool with other people, troubleshoot your issues and suggest features:
https://discord.gg/EEcDgN9wJJ

## Additional details
- This projects uses open-ai whisper for audio transcription. A translation model is bundled for translating english to Japanese (https://huggingface.co/staka/fugumt-en-ja). The Japanese voice syntheisis is done with voicevox. All three models are ran on your local machine by default, so you can use this project without an internet connection.
![image](https://user-images.githubusercontent.com/24196833/229306812-39fa6ff7-38b6-43fa-a4d2-ababafc2b33a.png)
- If you provide an api key from deepl translate in settings. Deepl can be used instead of the offline model, which can provide better, more natural translations.
- If you check the "Use voicevox on cloud" checkbox, Japanese audio syntheisis will happen on the cloud. If you do not provide an api key, the program will use the slow version of the API. If you provide a voicevox api key from https://voicevox.su-shiki.com/su-shikiapis/, the program will use the fast version of the API
- To have the ai speak english instead of Japanese, you can check the "use elevenlab on cloud" checkbox and provide an API key from here: https://beta.elevenlabs.io/speech-synthesis
# Inspiration

This project was inspired by this video：
https://youtu.be/UY7sRB60wZ4

Credit to
[@sociallyineptweeb](https://www.youtube.com/@sociallyineptweeb)
for the ideas and APIs used.
