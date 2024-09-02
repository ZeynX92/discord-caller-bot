import os
from dotenv import load_dotenv

load_dotenv()

debug = True

token = os.getenv("BOT_TOKEN")
test_guilds = [1279174291946078331]
devs = [834650370315780126, 735403901020536912, 649269897674883076, 490099081159507968]

if debug:
    channel_for_system_ping_id = 1274810927140831356
    channel_for_system_call_id = 905157355812057122
else:
    channel_for_system_ping_id = 1271465100246782025
    channel_for_system_call_id = 1270856322291728425

minerva_icon = 'https://cdn.discordapp.com/attachments/1272710244765798410/1272713108535640076/photo_2024-08-02_16-29-39_Copy.jpg?ex=66bbf9f2&is=66baa872&hm=ae796aa2d177014f974cc757d6bf2938f5e4df0a343ae0e27554e112f6909cd8&'
