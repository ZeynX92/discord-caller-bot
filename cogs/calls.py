import disnake.errors
from disnake.ext import commands, tasks
from disnake import Member, VoiceState, Option, OptionType
import config
from config import channel_for_system_ping_id, channel_for_system_call_id
import time


class ButtonsView(disnake.ui.View):
    def __init__(self, parent_):
        super(ButtonsView, self).__init__(timeout=None)
        self.parent_ = parent_

    @disnake.ui.button(label='❌ОТКЛОНИТЬ', style=disnake.ButtonStyle.red)
    async def decline_call_button(self, button, inter):
        if self.parent_.call_in_progress:
            self.parent_.destination.remove(inter.author)  # TODO: Testing
            await inter.send(f"❌Звонок отклонен.", ephemeral=True)
        else:
            await inter.send("🤷🏻‍Звонка нет...", ephemeral=True)


class Calls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.destination = []
        self.call_in_progress = False
        self.count_decliners = 0
        self.thread = None
        self.local_thread = None


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        try:
            if before.channel is not self.bot.get_channel(channel_for_system_ping_id) and len(
                    after.channel.members) - 1 == 0 and after.channel.id == channel_for_system_call_id:

                embed = disnake.Embed(title='',
                                      color=disnake.Colour.from_rgb(150, 150, 150))
                embed.set_author(name=r"МИНЕРВА - ПОДФУНКЦИЯ СВЯЗИ:",
                                 icon_url=config.minerva_icon)
                embed.add_field(name='', value='```Получен запрос подфункции "Минерва"...```', inline=False)
                embed.add_field(name='', value='```Инициализация запрашиваемой подфункции...```', inline=False)
                embed.add_field(name='', value='```Подключение...```', inline=False)
                embed.add_field(name='', value='```Подфункция "Минерва" инициализирована.```', inline=False)
                embed.add_field(name='', value='', inline=False)
                embed.add_field(name='', value='', inline=False)
                embed.add_field(name='', value='', inline=False)
                embed.add_field(name='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ЗВОНОК', value='', inline=False)
                embed.add_field(name='', value=f"{member.mention} начал звонок!", inline=False)
                if member.avatar is None:
                    embed.set_image(url=config.minerva_icon)
                else:
                    embed.set_image(url=member.avatar.url)
                embed.set_footer(text='МИНЕРВА: Сигнал отправлен всем присутствующим.',
                                 icon_url=config.minerva_icon)
                embed_id = await self.bot.get_channel(channel_for_system_ping_id).send(embed=embed,
                                                                                       view=ButtonsView(self))

                fetch_for_ping = await self.bot.get_channel(channel_for_system_ping_id).fetch_message(embed_id.id)
                new_thread = await fetch_for_ping.create_thread(
                    name="Общий звонок!",
                    auto_archive_duration=60,
                )
                self.thread = new_thread

                await self.bot.get_channel(new_thread.id).send("init")

                self.destination = []
                for dst in member.guild.members:
                    if dst not in after.channel.members:
                        self.destination.append(dst)

                self.call_in_progress = True
                self.count_decliners = 0
                self.caller.start(new_thread)
        except AttributeError:
            pass

        if self.call_in_progress and after.channel.id == channel_for_system_call_id:
            if member in self.destination:
                self.destination.remove(member)
                print(member.name, "зашел")

    @tasks.loop(seconds=1.0, count=62)
    async def caller(self, new_thread):

        try:
            await self.bot.get_channel(new_thread.id).send(' '.join([i.mention for i in self.destination]))
            await self.bot.get_channel(new_thread.id).purge(limit=1)

        except disnake.errors.HTTPException:
            pass

        if len(self.destination) == 0:
            self.call_in_progress = False
            self.caller.stop()
            await new_thread.delete()

    async def personal_call(self, new_local_thread):
        try:
            await self.bot.get_channel(new_local_thread.id).send(' '.join([i.mention for i in self.destination]))
            await self.bot.get_channel(new_local_thread.id).purge(limit=1)

        except disnake.errors.HTTPException:
            pass

        if len(self.destination) == 0:
            self.call_in_progress = False
            self.caller.stop()
            await new_local_thread.delete()

    @caller.after_loop
    async def on_caller_cancel(self):
        self.call_in_progress = False
        if self.thread is not None:
            await self.thread.delete()
        if self.local_thread is not None:
            await self.local_thread.delete()
        await self.bot.get_channel(channel_for_system_ping_id).purge(limit=999)
        print("Done")

    @commands.slash_command(
        name="decline_call",
        description="Отклоняет звонок",
        options=[]
    )
    async def decline_call(self, inter):
        if self.call_in_progress:
            self.destination.remove(inter.author)
            await inter.send(f"Звонок отклонен {inter.author.mention}", ephemeral=True)
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
            await inter.send(f"`МИНЕРВА:` Сигнал {member.mention} успешно отправлен.", ephemeral=True)

            embed = disnake.Embed(title='',
                                  color=disnake.Colour.from_rgb(150, 150, 150))
            embed.set_author(name=r"МИНЕРВА - ПОДФУНКЦИЯ СВЯЗИ:",
                             icon_url=config.minerva_icon)
            embed.add_field(name='', value=f"```Сообщение инициализировано...```", inline=False)
            embed.add_field(name='⠀⠀⠀⠀⠀⠀⠀⠀⠀ЛИЧНЫЙ ЗВОНОК',
                            value=f"{member.mention}, вас вызывает {inter.author.mention}", inline=False)
            if member.avatar is None:
                embed.set_image(url=config.minerva_icon)
            else:
                embed.set_image(url=member.avatar.url)
            embed.set_footer(text='МИНЕРВА: Сигнал отправлен.',
                             icon_url=config.minerva_icon)
            embed_id = await self.bot.get_channel(channel_for_system_ping_id).send(embed=embed,
                                                                                   view=ButtonsView(self))
            local_fetch_for_ping = await self.bot.get_channel(channel_for_system_ping_id).fetch_message(
                embed_id.id)
            new_local_thread = await local_fetch_for_ping.create_thread(
                name="Вам звонят!",
                auto_archive_duration=60,
            )

            self.local_thread = new_local_thread

            await self.bot.get_channel(new_local_thread.id).send("init")

            self.caller.start(new_local_thread)
        else:
            await inter.send("Звонок уже идет...", ephemeral=True)


def setup(bot):
    bot.add_cog(Calls(bot))
