import os
from dotenv import load_dotenv

load_dotenv()

debug = True

devs = [834650370315780126, 735403901020536912]
token = os.getenv("BOT_TOKEN")
test_guilds = [1270856038685610055]

channel_for_system_ping_id = 1271465100246782025
channel_for_system_call_id = 1270856322291728425
