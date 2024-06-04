from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
# from twitchAPI.helper import first

import asyncio
import json
import os

# async def twitch_example(app_id:str='', app_secret:str=''):
#     twitch = await Twitch(app_id=app_id, app_secret=app_secret)
#     print(twitch.user)
#     user = await first(twitch.get_users(logins='riigess'))
#     print(user.id, user.display_name)

#TODO: update target_channel to be more capable than just one channel
async def on_ready(ready_event: EventData, target_channel:str="riigess"):
    print("Bot is ready for work. Joining channels")
    await ready_event.chat.join_room(target_channel)

async def on_message(msg: ChatMessage):
    print(f"in {msg.room.name}, {msg.user.name} said: {msg.text}")

async def on_sub(sub:ChatSub):
    print(f"New subscription in {sub.room.name}:\n\tType: {sub.sub_plan}\n\tMessage: {sub.sub_message}")

async def test_command(cmd:ChatCommand):
    print("input:", cmd.parameter, len(cmd.parameter), cmd.room.name, cmd.room.room_id)
    if len(cmd.parameter) == 0:
        await cmd.reply("You did not give me an argument")
    else:
        try:
            if int(cmd.parameter) % 2 == 0:
                await cmd.reply("That's an even number.")
            else:
                await cmd.reply("That's an odd number.")
        except:
            await cmd.reply("That's not a number. Please pass exactly 1 number without any extra characters.")

async def run(app_id:str="", app_secret:str="", user_scope:list[AuthScope]=[], target_channel:str=""):
    twitch = await Twitch(app_id=app_id, app_secret=app_secret)
    auth = UserAuthenticator(twitch, user_scope)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, user_scope, refresh_token)

    chat = await Chat(twitch)

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.register_event(ChatEvent.SUB, on_sub)

    chat.register_command('reply', test_command)

    chat.start()

    try:
        input("Press ENTER to stop...")
    finally:
        chat.stop()
        await twitch.close()

def write_to_file(d:dict, config_filename:str):
    with open(config_filename, 'w') as f:
        f.write(json.dumps(d, indent=4, separators=(',',':')))
    print(f"Please set up {os.getcwd()}/{config_filename} before proceeding.")

if __name__ == "__main__":
    user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
    config_filename = "config.json"
    if os.path.exists(os.getcwd() + f"/{config_filename}"):
        with open(config_filename, "r") as f:
            d = json.loads(f.read())
            if 'app_id' in d:
                app_id = d['app_id']
            if 'app_secret' in d:
                app_secret = d['app_secret']
            if 'app_id' not in d:
                d.update({'app_id': ''})
            if 'app_secret' not in d:
                d.update({'app_secret': ''})
        if len(d['app_id']) == 0 or len(d['app_secret']) == 0:
            write_to_file(d, config_filename)
    else:
        d = {'app_id': '', 'app_secret': ''}
        write_to_file(d, config_filename)
    target_channel = 'riigess'
    asyncio.run(run(app_id, app_secret, user_scope, target_channel))
    # asyncio.run(twitch_example(app_id=app_id, app_secret=app_secret))
