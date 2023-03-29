import os
import traceback
import openai
import STTSLocal as STTS

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
    api_key = os.getenv("OPENAI_API_KEY")

    openai.api_key = api_key
    print(f"Sending: {user_input} with api key :{api_key}")
    print(message_log)
    message_log.append({"role": "user", "content": user_input})
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
    STTS.start_TTS_pipeline(text_response)


def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)
