import asyncio
import traceback
import pytchat
import chatbot
import time
from twitchio.ext import commands
from threading import Thread

read_chat_youtube_thread = None
read_chat_youtube_thread_running = False

twitchbot = None
read_chat_twitch_thread = None
read_chat_twitch_thread_running = False

youtube_video_id = ''

twitch_access_token = ''
twitch_channel_name = ''

logging_eventhandlers = []


def read_chat_youtube():
    log_message("startinging chat fetching...")
    global read_chat_youtube_thread_running, youtube_video_id
    chat = None
    try:
        chat = pytchat.create(video_id=youtube_video_id)
    except:
        log_message("failed to fetch chat")
        print(traceback.format_exc())
        return
    read_chat_youtube_thread = Thread(target=read_chat_loop, args=[chat,])
    read_chat_youtube_thread.start()
    read_chat_youtube_thread_running = True


def read_chat_loop(chat):
    log_message("Chat fetching started")
    global read_chat_youtube_thread_running
    while read_chat_youtube_thread_running and chat.is_alive():
        for c in chat.get().sync_items():
            log_message(f"{c.datetime} [{c.author.name}]- {c.message}")
            chatbot.send_user_input(c.message)
            # print(response)
            time.sleep(1)
    log_message("Chat fetching ended")


def stop_read_chat_youtube():
    log_message("stopping chat fetching...")
    global read_chat_youtube_thread_running
    read_chat_youtube_thread_running = False
    print("Process stopped.")


class Bot(commands.Bot):

    def __init__(self, token, initial_channels):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=token,
                         prefix='?', initial_channels=initial_channels)

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        log_message(f'Logged in as | {self.nick}')
        log_message(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message)
        log_message(message.content)
        chatbot.send_user_input(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')


def read_chat_twitch():
    log_message("startinging chat fetching...")
    global twitchbot
    global read_chat_twitch_thread_running, read_chat_twitch_thread
    global twitch_access_token, twitch_channel_name
    twitchbot = Bot(twitch_access_token, [twitch_channel_name])
    read_chat_twitch_thread = Thread(target=runbot)
    read_chat_twitch_thread.start()
    read_chat_twitch_thread_running = True


def runbot():
    log_message("Chat fetching started")
    twitchbot.run()


def stop_read_chat_twitch():
    log_message("Twitch fetching can only be stopped by closing the program.")


def log_message(message_text):
    print(message_text)
    global logging_eventhandlers
    for eventhandler in logging_eventhandlers:
        eventhandler(message_text)
