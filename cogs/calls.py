import disnake.errors
from disnake.ext import commands, tasks
from disnake import Member, VoiceState, Option, OptionType

import config
from config import channel_for_system_ping_id, channel_for_system_call_id


class ButtonsView(disnake.ui.View):
    def __init__(self, parent_):
        super(ButtonsView, self).__init__(timeout=None)
        self.parent_ = parent_

    @disnake.ui.button(label='❌ОТКЛОНИТЬ', style=disnake.ButtonStyle.red)
    async def decline_call_button(self, button, inter):
        if self.parent_.call_in_progress:
            self.parent_.destination.remove(inter.author)  # TODO: Testing
            await inter.send(f"Звонок отклонен {inter.author.mention}")
            self.parent_.count_decliners += 1
            await self.bot.get_channel(channel_for_system_ping_id).purge(limit=1)
        else:
            await inter.send("🤷🏻‍Звонка нет...", ephemeral=True)


class Calls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.destination = []
        self.call_in_progress = False
        self.count_decliners = 0

    @tasks.loop(seconds=1.0, count=62)
    async def caller(self):
        try:
            await self.bot.get_channel(channel_for_system_ping_id).send(' '.join([i.mention for i in self.destination]))
            await self.bot.get_channel(channel_for_system_ping_id).purge(limit=1)

        except disnake.errors.HTTPException:
            pass

        if len(self.destination) == 0:
            self.call_in_progress = False
            self.caller.stop()

    @caller.after_loop
    async def on_caller_cancel(self):
        self.call_in_progress = False
        await self.bot.get_channel(channel_for_system_ping_id).purge(limit=1)
        print("Done")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        try:
            if before.channel is not self.bot.get_channel(channel_for_system_ping_id) and len(
                    after.channel.members) - 1 == 0 and after.channel.id == channel_for_system_call_id:

                embed = disnake.Embed(title='',
                                      color=disnake.Colour.from_rgb(150, 150, 150))
                embed.set_author(name=r"МИНЕРВА - ПОДФУНКЦИЯ СВЯЗИ:",
                                 icon_url=config.Minerva_icon)
                embed.add_field(name='', value='```Получен запрос подфункции "Минерва"...```', inline=False)
                embed.add_field(name='', value='```Инициализация запрашиваемой функции...```', inline=False)
                embed.add_field(name='', value='```Подключение...```', inline=False)
                embed.add_field(name='', value='```Подфункция "Минерва" инициализирована.```', inline=False)
                embed.add_field(name='', value='', inline=False)
                embed.add_field(name='', value='', inline=False)
                embed.add_field(name='', value='', inline=False)
                embed.add_field(name='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ЗВОНОК', value='', inline=False)
                embed.add_field(name='', value=f"⠀⠀⠀⠀⠀⠀⠀{member.mention} начал звонок!", inline=False)
                embed.set_image(url=member.avatar.url)
                embed.set_footer(text='МИНЕРВА: Сигнал отправлен всем присутствующим.',
                                 icon_url=config.Minerva_icon)
                await self.bot.get_channel(channel_for_system_ping_id).send(embed=embed,
                                                                            view=ButtonsView(self))

                self.destination = []
                for dst in member.guild.members:
                    if dst not in after.channel.members:
                        self.destination.append(dst)

                self.call_in_progress = True
                self.count_decliners = 0
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
