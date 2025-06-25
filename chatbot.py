import json
import re
import asyncio
import traceback
from openai import OpenAI # Updating Client Method
import requests
import queue
import threading
import STTSLocal as STTS
from PyCharacterAI import Client
from PyCharacterAI.exceptions import SessionClosedError

# "GPT", "CHARACTER_AI"
chat_model = "GPT"
openai_api_key = ''
AI_RESPONSE_FILENAME = 'ai-response.txt'
character_limit = 3000
lore = ''
message_log = []
character_id = "scsnOOq2jDNHqRpA9Inuckrb5HHqyQZgtxPFQyPJ-eQ"
logging_eventhandlers = []
use_character_ai_token = False
character_ai_token = ""
history_webui = {'internal': [], 'visible': []}
chat = None
message_queue = queue.Queue()

main_asyncio_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_asyncio_loop)

def run_event_loop(loop): # Run async thread
    asyncio.set_event_loop(loop)
    loop.run_forever()

event_loop_thread = threading.Thread(target=run_event_loop, args=(main_asyncio_loop,), daemon=True)
event_loop_thread.start()


async def initialize():
    global chat_model, chat, client, character_id, character_ai_token
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
        client = Client() #New CharacterAI client!
        try:
            log_message(f'setting character_id to: {character_id}')
            print('Authenticating...')
            await client.authenticate(token=character_ai_token)
            me = await client.account.fetch_me()
            print(f"Authenticated as @{me.username}")
            if chat is None:
                chat_obj, greeting_message = await client.chat.create_chat(character_id)
                chat = chat_obj
                print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")
            return
        except SessionClosedError as e:
            log_message(f"Error in authenticating your account! Error: {e}")
    return


def change_chat_model(model):
    global chat_model
    chat_model = model
    future = asyncio.run_coroutine_threadsafe(
        initialize(),
        main_asyncio_loop
    )
    return future.result()

async def send_user_input(user_input):
    global message_log
    global openai_api_key
    if (chat_model == "GPT"):
        log_message(f"GPTuser: {user_input}")
        client_ = OpenAI(api_key=openai_api_key) # Instantiate via the new OpenAI client method.

        print(f"Sending: {user_input}")
        message_log.append({"role": "user", "content": user_input})
        print(message_log)
        total_characters = sum(len(message['content'])
                               for message in message_log)
        print(f"total_characters: {total_characters}")
        while total_characters > character_limit and len(message_log) > 1:
            print(f"total_characters {total_characters} exceed limit of {character_limit}, removing oldest message")
            total_characters -= len(message_log[1]["content"])
            message_log.pop(1)

        try:
            completion = client_.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message_log
            )
        except Exception as e:
            log_message("Error during OpenAI API call")
            log_message(str(e))
            return
        text = completion.choices[0].message.content
        message_log.append({"role": "assistant", "content": text})
        log_message(f'AI: {text}')
        with open(AI_RESPONSE_FILENAME, "w", encoding="utf-8") as file:
            separated_text = separate_sentences(text)
            file.write(separated_text)
        return text
    elif (chat_model == "GPT_proxy(china only)"):
        log_message(f"GPTuser: {user_input}")
        client_ = OpenAI(api_key=openai_api_key)
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
        return text_response
    elif (chat_model == "CHARACTER_AI"):
        global chat
        log_message(f'user: {user_input}')
        if chat is None:
            print("Chat session failed!")
            return
        turn = await client.chat.send_message(character_id, chat.chat_id, user_input)
        text_response = turn.get_primary_candidate().text
        print(f"[{turn.author_name}]: {text_response}")
        log_message(f'{turn.author_name}: {text_response}')
        with open(AI_RESPONSE_FILENAME, "w", encoding="utf-8") as file:
            separated_text = separate_sentences(text_response)
            file.write(separated_text)
        return text_response
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

def queue_watcher(): # NEW message queue system so the system does not override itself following FIFO
    while True:
        user_input = message_queue.get()
        if user_input is None:
            break
        try:
            future = asyncio.run_coroutine_threadsafe(
                send_user_input(user_input),
                main_asyncio_loop
            )
            text_response = future.result()
            STTS.start_TTS_pipeline(text_response)
        except Exception as e:
            import traceback
            print(f"Error processing message: {e}")
            traceback.print_exc()

worker_thread = threading.Thread(target=queue_watcher, daemon=True)
worker_thread.start()

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
