import traceback
from transformers import pipeline
import requests
import json
import os

use_deepl = False
deepl_api_key = ""
fugu_translator = None


def initialize():
    global fugu_translator
    fugu_translator = pipeline(
        "translation",
        model="./models--staka--fugumt-en-ja/snapshots/2d6da1c7352386e12ddd46ce3d0bbb2310200fcc",
    )


def translate(text, from_code, to_code):
    if use_deepl:
        DEEPL_TOKEN = deepl_api_key
        if not DEEPL_TOKEN:
            DEEPL_TOKEN = os.getenv("DEEPL_API_KEY")
        # Send text to translation service
        print(f"Calling deepl with apikey: {DEEPL_TOKEN}")
        headers = {
            "Authorization": f"DeepL-Auth-Key {DEEPL_TOKEN}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = f"text={text}&target_lang={to_code.upper()}"
        translationResponse = requests.post(
            "https://api-free.deepl.com/v2/translate",
            headers=headers,
            data=data.encode("utf-8"),
        )
        # print(translationResponse.content)
        try:
            responseJSON = json.loads(translationResponse.content.decode("utf-8"))
            if "translations" in responseJSON:
                text_output = responseJSON["translations"][0]["text"]
                return text_output
        except:
            print("Could not load json response from deepl.")
            print(f"Response content: {translationResponse}")
            print(f"Response content: {translationResponse.content}")
            print(traceback.format_exc())
            return ""

    else:
        # if from_code == "en" and to_code == "ja":
        global fugu_translator
        if fugu_translator == None:
            fugu_translator = pipeline(
                "translation",
                model="./models--staka--fugumt-en-ja/snapshots/2d6da1c7352386e12ddd46ce3d0bbb2310200fcc",
            )
        return fugu_translator(text)[0]["translation_text"]
        # else:
        # print(f"no avaliable model to translate from{from_code} to {to_code}")
        # return ""
