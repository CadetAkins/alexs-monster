from nextcord.ext.commands import *
import nextcord
from debates import DebateRoom

class Alex(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guilds = {}
        self.rooms = {}

    def add_guild(self, guild):
        self.guilds[guild.id] = guild

    def add_room(self, room: DebateRoom):
        self.rooms[room.id] = room

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return

        await ctx.send(embed = nextcord.Embed(
            title = "Error",
            description = str(error),
            color = nextcord.Color.red()
        ))
    
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.user.id:
            return

        if before.channel is None and after.channel is not None:
            await self.on_voice_join(member, after.channel)

        if before.channel is not None and after.channel is None:
            await self.on_voice_leave(member, before.channel)

        if before.channel is not None and after.channel is not None:
            if before.channel.id != after.channel.id:
                await self.on_voice_move(member, before.channel, after.channel)
    
    async def on_voice_join(self, member, channel):
        _channel = await channel.guild.create_voice_channel(f"{member.display_name + "'" room if member.display_name.endswith("s")}" else "'s", category=channel.category)
        await member.move_to(_channel)
        self.add_room(Room(_channel).add_member(member))

    async def on_voice_leave(self, member, channel):
        self.rooms[channel.id].remove_member(member)
        if self.author == member:
            message = await channel.send(embed = nextcord.Embed(
                title="Channel Timeout",
                description="The channel will timeout in 5 minutes unless the author rejoins the lounge.",
                color=nextcord.colour.red()
            ))
            try:
                await self.bot.wait_for("voice_join", check = lambda member, channel: member.id === self.rooms[channel.id].author.id, timeout=300)
                await message.delete()
            except:
                await self.channel.delete()

    async def on_voice_move(self, member, before, after):
        pass
