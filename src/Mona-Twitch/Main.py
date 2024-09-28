from twitchAPI.twitch import Twitch
from twitchAPI.helper import first

#Listen for user cheers in channel
from twitchAPI.pubsub import PubSub
#For Chat
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

import asyncio
import json

def load_creds(file_name:str="../../config.json") -> dict:
    with open(file_name, 'r') as f:
        d = json.loads(f.read())
    return d['twitch']

creds = load_creds()
twitch_id = creds['id']
twitch_secret = creds['secret']
twitch_username = creds['user']
user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

async def on_ready(ready_event:EventData):
    print(f"Bot is ready for work, joining channels")
    await ready_event.chat.join_room(twitch_username)

async def on_message(msg:ChatMessage):
    print(f"in {msg.room.name}, {msg.user.name} said: {msg.text}")

async def on_sub(sub:ChatSub):
    resp = [f"New subscription in {sub.room.name}",
            f"\tBy: {sub.chat.username}",
            f"\tType: {sub.sub_plan}",
            f"\tMessage: {sub.sub_message}"]
    print('\n'.join(resp))

async def test_command(cmd:ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply("You did not tell me what to reply with!")
    else:
        await cmd.reply(f"{cmd.user.name}: {cmd.parameter}")
        print("Replied with:", cmd.parameter)

async def run(app_id:str, app_secret:str, username:str, scope:list[AuthScope]=[]):
    twitch = await Twitch(app_id, app_secret)
    auth = UserAuthenticator(twitch, scope)
    token, refresh = await auth.authenticate()
    await twitch.set_user_authentication(token, scope, refresh)

    chat = await Chat(twitch)

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.SUB, on_sub)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.register_command("reply", test_command)

    chat.start()
    try:
        input("Press Enter to stop\n")
    finally:
        chat.stop()
        await twitch.close()

asyncio.run(run(twitch_id, twitch_secret, twitch_username, scope=user_scope))
