import json
import os
import re
import time
import traceback
import openai
import requests
import STTSLocal as STTS

# "GPT", "CHARACTER_AI"
chat_model = "GPT"
openai_api_key = ''
AI_RESPONSE_FILENAME = 'ai-response.txt'
character_limit = 3000
lore = ''
character_ai_endpoint = "http://127.0.0.1:3000"
message_log = []
character_id = "scsnOOq2jDNHqRpA9Inuckrb5HHqyQZgtxPFQyPJ-eQ"
logging_eventhandlers = []
use_character_ai_token = False
character_ai_token = ""
history_webui = {'internal': [], 'visible': []}


def initialize():
    global chat_model
    if (chat_model == "GPT" or chat_model == "GPT_proxy(china only)"):
        global lore, message_log
        try:
            with open('./lore.txt', 'r', encoding='utf-8') as file:
                lore = file.read()
        except Exception:
            print("error when reading lore.txt")
            print(traceback.format_exc())
        lore = lore.replace('\n', '')
        message_log = [
            {"role": "system", "content": lore},
        ]

    elif (chat_model == "CHARACTER_AI"):
        url = ""
        global use_character_ai_token, character_ai_token
        if (use_character_ai_token):
            log_message(
                f'Authenticating character-ai with token:{character_ai_token}...')
            url = f"{character_ai_endpoint}/authenticateToken?token={character_ai_token}"
        else:
            log_message(f'Authenticating character-ai as guest...')
            url = f"{character_ai_endpoint}/authenticate"
        print(f"Sending POST request to: {url}")
        try:
            response = send_request_with_retry(url)
            print(f'response: {response}')
            global character_id
            characterai_set_character(
                character_id)
        except requests.exceptions.Timeout:
            log_message(
                "Request timed out. May be caused by a queue at character-ai servers.")


def change_chat_model(model):
    global chat_model
    chat_model = model
    initialize()


def send_request_with_retry(url, max_retries=20, retry_delay=2, timeout=5):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.request(
                'POST', url, timeout=timeout)
            # Process the response as needed
            return response
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout
        except:
            print("Waiting for character-ai server to start. Retrying in {} seconds...".format(
                retry_delay))
            time.sleep(retry_delay)
            retries += 1
    # If all retries fail, raise an exception or handle the error accordingly
    raise Exception(
        "Failed to establish a connection with the server after multiple attempts.")


def characterai_set_character(characterid):
    log_message(f'setting character_id to: {characterid}')
    url = f"{character_ai_endpoint}/setCharacter?characterId={characterid}"
    print(f"Sending POST request to: {url}")
    response = requests.request(
        "POST", url)
    print(f'response: {response}')


def send_user_input(user_input):
    global message_log
    global openai_api_key
    if (chat_model == "GPT"):
        log_message(f"GPTuser: {user_input}")
        
        if (openai_api_key == ''):
            openai_api_key = os.getenv("OPENAI_API_KEY")

        openai.api_key = openai_api_key
        print(f"Sending: {user_input}")
        message_log.append({"role": "user", "content": user_input})
        print(message_log)
        total_characters = sum(len(message['content'])
                               for message in message_log)
        print(f"total_characters: {total_characters}")
        while total_characters > character_limit and len(message_log) > 1:
            print(
                f"total_characters {total_characters} exceed limit of {character_limit}, removing oldest message")
            total_characters -= len(message_log[1]["content"])
            message_log.pop(1)

        response = None
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message_log
            )
        except Exception:
            log_message("Error when loading api key from environment variable")
            log_message(
                "You need an API key from https://platform.openai.com/ stored in an environment variable with name \"OPENAI_API_KEY\" to use the chat feature")
            print(traceback.format_exc())
            return
        text_response = response['choices'][0]['message']['content']
        message_log.append({"role": "assistant", "content": text_response})
        log_message(f'AI: {text_response}')
        with open(AI_RESPONSE_FILENAME, "w", encoding="utf-8") as file:
            separated_text = separate_sentences(text_response)
            file.write(separated_text)
        STTS.start_TTS_pipeline(text_response)
    elif (chat_model == "GPT_proxy(china only)"):
        log_message(f"GPTuser: {user_input}")
        if (openai_api_key == ''):
            openai_api_key = os.getenv("OPENAI_API_KEY")

        openai.api_key = openai_api_key
        print(f"Sending: {user_input}")
        message_log.append({"role": "user", "content": user_input})
        print(message_log)
        total_characters = sum(len(message['content'])
                               for message in message_log)
        print(f"total_characters: {total_characters}")
        while total_characters > character_limit and len(message_log) > 1:
            print(
                f"total_characters {total_characters} exceed limit of {character_limit}, removing oldest message")
            total_characters -= len(message_log[1]["content"])
            message_log.pop(1)

        response = None
        try:
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=message_log
            # )
            response = requests.post("https://api.openai-proxy.com/v1/chat/completions",
                                     json={"model": "gpt-3.5-turbo", "messages": message_log},
                                     headers={"Authorization": "Bearer " + openai_api_key},verify=False)
            response = response.json()
        except Exception:
            log_message("Error when loading api key from environment variable")
            log_message(
                "You need an API key from https://platform.openai.com/ stored in an environment variable with name \"OPENAI_API_KEY\" to use the chat feature")
            print(traceback.format_exc())
            return
        text_response = response['choices'][0]['message']['content']
        message_log.append({"role": "assistant", "content": text_response})
        log_message(f'AI: {text_response}')
        with open(AI_RESPONSE_FILENAME, "w", encoding="utf-8") as file:
            separated_text = separate_sentences(text_response)
            file.write(separated_text)
        STTS.start_TTS_pipeline(text_response)
    elif (chat_model == "CHARACTER_AI"):
        log_message(f'user: {user_input}')
        url = f"{character_ai_endpoint}/sendChat?text={user_input}"
        print(f"Sending POST request to: {character_ai_endpoint}")
        response = requests.request(
            "POST", url)
        print(f'response: {response}')
        response_json = json.loads(response.text)
        text = response_json['text']
        log_message(f'AI: {text}')
        with open(AI_RESPONSE_FILENAME, "w", encoding="utf-8") as file:
            separated_text = separate_sentences(text)
            file.write(separated_text)
        STTS.start_TTS_pipeline(text)
    elif (chat_model == "oogabooga_webui"):
        run_webui(user_input, history_webui)


def run_webui(user_input, history):
    log_message(f"webui_user: {user_input}")
    request = {
        'user_input': user_input,
        'max_new_tokens': 50,
        'auto_max_new_tokens': False,
        'history': history,
        'mode': 'chat',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'character': 'Awkward Questions FM',
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
        'your_name': 'You',
        # 'name1': 'name of user', # Optional
        # 'name2': 'name of character', # Optional
        # 'context': 'character context', # Optional
        # 'greeting': 'greeting', # Optional
        # 'name1_instruct': 'You', # Optional
        # 'name2_instruct': 'Assistant', # Optional
        # 'context_instruct': 'context_instruct', # Optional
        # 'turn_template': 'turn_template', # Optional
        'regenerate': False,
        '_continue': False,
        'chat_instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'repetition_penalty_range': 0,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'guidance_scale': 1,
        'negative_prompt': '',

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    HOST = 'localhost:5000'
    URI = f'http://{HOST}/api/v1/chat'
    response = requests.post(URI, json=request)
    print(response)
    if response.status_code == 200:
        print(response.json())
        result = response.json()['results'][0]['history']
        print(json.dumps(result, indent=4))
        print()
        text_response = result['visible'][-1][1]
        log_message(f"Ai:{text_response}")
        global history_webui
        history_webui = result
        with open(AI_RESPONSE_FILENAME, "w", encoding="utf-8") as file:
            separated_text = separate_sentences(text_response)
            file.write(separated_text)
        STTS.start_TTS_pipeline(text_response)


def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)


def separate_sentences(text):
    # Define common sentence-ending punctuation marks
    sentence_enders = re.compile(r'[.!?]+')

    # Replace any newline characters with spaces
    text = text.replace('\n', ' ')

    # Split text into list of strings at each sentence-ending punctuation mark
    sentences = sentence_enders.split(text)

    # Join sentences with newline character
    result = '\n'.join(sentences)

    return result
