import os
import re
import traceback
import openai
import STTSLocal as STTS


openai_api_key = ''
AI_RESPONSE_FILENAME = 'ai-response.txt'
character_limit = 3000

lore = ''
try:
    with open('./lore.txt', 'r', encoding='utf-8') as file:
        lore = file.read()
except Exception:
    print("error when reading lore.txt")
    print(traceback.format_exc())
lore = lore.replace('\n', '')

message_log = [
    {"role": "system", "content": lore},
    {"role": "user", "content": lore},
]

logging_eventhandlers = []


def send_user_input(user_input):
    log_message(f'user: {user_input}')
    global message_log
    global openai_api_key
    if (openai_api_key == ''):
        openai_api_key = os.getenv("OPENAI_API_KEY")

    openai.api_key = openai_api_key
    print(f"Sending: {user_input}")
    message_log.append({"role": "user", "content": user_input})
    print(message_log)
    total_characters = sum(len(message['content']) for message in message_log)
    print(f"total_characters: {total_characters}")
    while total_characters > character_limit and len(message_log) > 1:
        print(
            f"total_characters {total_characters} exceed limit of {character_limit}, removing oldest message")
        total_characters -= len(message_log[2]["content"])
        message_log.pop(2)

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
