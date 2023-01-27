import discord
from discord.ext import commands, tasks

from src.utils import logger


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = await self.bot.fetch_channel(1068050856638939226)
        await channel.send(f":wave: {member.mention} has joined the server!")
        role = discord.utils.get(member.guild.roles, id=984539879251804211)
        await member.add_roles(role)


async def setup(bot):
    await bot.add_cog(Events(bot))
    return logger.log("Welcome Module Online.", logger.logtypes.info)

