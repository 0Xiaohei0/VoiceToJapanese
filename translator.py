from transformers import pipeline
import requests
import json

use_deepl = False
deepl_api_key = ''
fugu_translator = None


def initialize():
    global fugu_translator
    fugu_translator = pipeline(
        'translation', model='./models--staka--fugumt-en-ja/snapshots/2d6da1c7352386e12ddd46ce3d0bbb2310200fcc')


def translate(text, from_code, to_code):
    if (use_deepl):
        DEEPL_TOKEN = deepl_api_key
        # Send text to translation service
        print(f"Calling deepl with apikey: {DEEPL_TOKEN}")
        headers = {
            'Authorization': f'DeepL-Auth-Key {DEEPL_TOKEN}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = f'text={text}&target_lang={to_code.upper()}'
        translationResponse = requests.post(
            'https://api-free.deepl.com/v2/translate', headers=headers, data=data.encode('utf-8'))
        # print(translationResponse.content)
        try:
            responseJSON = json.loads(
                translationResponse.content.decode('utf-8'))
            if "translations" in responseJSON:
                text_output = responseJSON['translations'][0]['text']
                return text_output
        except:
            print("Could not load json response from deepl.")
            print(f'Response content: {translationResponse.content}')
            return ''

    else:
        if (from_code == 'en' and to_code == 'ja'):
            global fugu_translator
            if (fugu_translator == None):
                fugu_translator = pipeline(
                    'translation', model='./models--staka--fugumt-en-ja/snapshots/2d6da1c7352386e12ddd46ce3d0bbb2310200fcc')
            return fugu_translator(text)[0]['translation_text']
        else:
            print(
                f"no avaliable model to translate from{from_code} to {to_code}")
            return ''
    # DEEPL_TOKEN = os.environ.get("translation-service-api-token")
    # # Send text to translation service
    # headers = {
    #     'Authorization': f'DeepL-Auth-Key {DEEPL_TOKEN}',
    #     'Content-Type': 'application/x-www-form-urlencoded',
    # }
    # data = f'text={text}&target_lang={to_code.upper()}'
    # translationResponse = requests.post(
    #     'https://api-free.deepl.com/v2/translate', headers=headers, data=data.encode('utf-8'))
    # # print(translationResponse.content)
    # responseJSON = json.loads(
    #     translationResponse.content.decode('utf-8'))
    # if "translations" in responseJSON:
    #     text_output = responseJSON['translations'][0]['text']
    #     return text_output

    # # Download and install Argos Translate package
    # argostranslate.package.update_package_index()
    # available_packages = argostranslate.package.get_available_packages()
    # package_to_install = next(
    #     filter(
    #         lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    #     )
    # )
    # argostranslate.package.install_from_path(package_to_install.download())

    # # print(f'{from_code}, {to_code}')
    # # Translate
    # translatedText = argostranslate.translate.translate(
    #     text, from_code, to_code)
    # return translatedText
