import disnake.errors
from disnake.ext import commands, tasks
from disnake import Member, VoiceState, Option, OptionType
from config import channel_for_system_ping_id, channel_for_system_call_id


class Calls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.destination = []
        self.call_in_progress = False

    @tasks.loop(seconds=1.0, count=62)
    async def caller(self):
        try:
            await self.bot.get_channel(channel_for_system_ping_id).send(' '.join([i.mention for i in self.destination]))
        except disnake.errors.HTTPException:
            pass

        if len(self.destination) == 0:
            self.call_in_progress = False
            self.caller.stop()

    @caller.after_loop
    async def on_caller_cancel(self):
        self.call_in_progress = False
        await self.bot.get_channel(channel_for_system_ping_id).purge(limit=60)
        print("Done")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        try:
            if before.channel is not self.bot.get_channel(channel_for_system_ping_id) and len(
                    after.channel.members) - 1 == 0 and after.channel.id == channel_for_system_call_id:
                await self.bot.get_channel(channel_for_system_ping_id).send(f"{member.mention} начал звонок!")

                self.destination = []
                for dst in member.guild.members:
                    if dst not in after.channel.members:
                        self.destination.append(dst)

                self.call_in_progress = True
                self.caller.start()
        except AttributeError:
            pass

        if self.call_in_progress and after.channel.id == channel_for_system_call_id:
            if member in self.destination:
                self.destination.remove(member)
                print(member.name, "зашел")

    @commands.slash_command(
        name="decline_call",
        description="Отклоняет звонок",
        options=[]
    )
    async def decline_call(self, inter):
        if self.call_in_progress:
            self.destination.remove(inter.author)  # TODO: Testing
            await inter.send(f"Звонок отклонен {inter.author.mention}")
        else:
            await inter.send("Звонка нет...")

    @commands.slash_command(
        name="call_for_member",
        description="Зовет конкретного участника",
        options=[
            Option(
                name="member",
                description="Участник который будет позван",
                type=OptionType.user,
                required=True
            )]
    )
    async def call_for_member(self, inter, member: Member):
        if not self.call_in_progress:
            self.destination = [member]
            self.call_in_progress = True
            await inter.send(f"Зову {member.mention}")
            self.caller.start()
        else:
            await inter.send("Звонок уже идет...")


def setup(bot):
    bot.add_cog(Calls(bot))
