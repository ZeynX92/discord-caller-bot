import json
from time import sleep

import disnake
from disnake import Option, OptionType, Member, VoiceState
from disnake.ext import commands, tasks
from config import devs
import asyncio


class VoiceStateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.exceptions_file = "exceptions.json"
        self.exceptions = []
        with open(self.exceptions_file, "r") as f:
            data = json.load(f)
            self.exceptions = data.get("exceptions", [])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if after.channel is not None:
            if member.id not in self.exceptions:
                await asyncio.sleep(300)
                try:
                    await member.edit(mute=False, deafen=False)
                except:
                    pass

    @commands.slash_command(
        name="unmute_all",
        description="Размутить всех кроме исключений",
        options=[]
    )
    async def unmutе_all(self, inter, exceptions: disnake.Member = None):
        if inter.author.id in devs:
            voice_channel = inter.author.voice.channel
            for member in voice_channel.members:
                if member.id not in self.exceptions:
                    await member.edit(mute=False, deafen=False)
                await inter.send("Команда успешно выполнена", ephemeral=True)
        else:
            await inter.send("У вас нет прав для использования этой команды.", ephemeral=True)

    @commands.slash_command(
        name="exception_add",
        description="Добавить исключение авторазмута",
        options=[
            Option(
                name="member",
                description="Участник который будет добавлен",
                type=OptionType.user,
                required=True
            )]
    )
    async def exception_add(self, inter, member: disnake.Member):
        if inter.author.id in devs:
            if member.id in self.exceptions:
                await inter.response.send_message(f"{member.mention} уже в списке.", ephemeral=True)
            else:
                self.exceptions.append(member.id)
                self.save_exceptions(self.exceptions)
                await inter.response.send_message(f"{member.mention} был добавлен.", ephemeral=True)
        else:
            await inter.send("У вас нет прав для использования этой команды.", ephemeral=True)

    @commands.slash_command(
        name="exception_remove",
        description="Удалить исключение авторазмута",
        options=[
            Option(
                name="member",
                description="Участник который будет удалён",
                type=OptionType.user,
                required=True
            )]
    )
    async def exception_remove(self, inter, member: disnake.Member):
        if inter.author.id in devs:
            if member.id in self.exceptions:
                self.exceptions.remove(member.id)
                self.save_exceptions(self.exceptions)
                await inter.response.send_message(f"{member.mention} был удалён.", ephemeral=True)
            else:
                await inter.response.send_message(f"{member.mention} нет в списке.", ephemeral=True)
        else:
            await inter.send("У вас нет прав для использования этой команды.", ephemeral=True)

    def save_exceptions(self, exceptions):
        with open(self.exceptions_file, "w") as f:
            json.dump({"exceptions": exceptions}, f)


def setup(bot):
    bot.add_cog(VoiceStateCog(bot))
