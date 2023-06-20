import json
import os
import re
import time
import traceback
import openai
import requests
import STTSLocal as STTS

# "GPT", "CHARACTER_AI"
chat_model = "CHARACTER_AI"
openai_api_key = ''
AI_RESPONSE_FILENAME = 'ai-response.txt'
character_limit = 3000
lore = ''
character_ai_endpoint = "http://127.0.0.1:3000"
message_log = []

logging_eventhandlers = []


def initialize():
    global chat_model
    if (chat_model == "GPT"):
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
        log_message(f'Authenticating character-ai...')
        url = f"{character_ai_endpoint}/authenticate"
        print(f"Sending POST request to: {url}")
        response = send_request_with_retry(url)
        print(f'response: {response}')
        characterai_set_character(
            "RQrrOj-UNdEV2_PC5D03US-27MZ7EUtaRH_husjbRQA")


def send_request_with_retry(url, max_retries=20, retry_delay=2):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.request(
                'POST', url)
            # Process the response as needed
            return response
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
    if (chat_model == "GPT"):
        log_message(f"GPTuser: {user_input}")
        global message_log
        global openai_api_key
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
