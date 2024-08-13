import os
from dotenv import load_dotenv

load_dotenv()

debug = True

devs = [834650370315780126, 735403901020536912]
token = os.getenv("BOT_TOKEN")
test_guilds = [1228301704340967454]

channel_for_system_ping_id = 1272671680686198846
channel_for_system_call_id = 1228301704340967459
