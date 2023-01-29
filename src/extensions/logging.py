import discord, datetime, time
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import time
from itertools import cycle
import sqlite3
import json
import asyncio
import os
import random
import re
import urllib.request
import src.utils.data as data
from src.utils import logger


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return

        if message.guild is None:
            return

        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel = self.bot.get_channel(int(action_log))
        final = message.created_at - datetime.timedelta(hours=4)
        cret = final.strftime("%b-%d-%Y | %I:%M:%S %p")
        embed = discord.Embed(
            colour=discord.Colour.red(),
            title="Message deleted",
            timestamp=datetime.datetime.now(),

            description=f"sent at: {cret} EST."
        )
        embed.set_author(
            icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if message.author.avatar is None else message.author.avatar.url,
            name=f"{message.author.name}#{message.author.discriminator}")
        embed.add_field(name="Message content:", value=f"{message.content}")
        embed.add_field(name="Channel:", value=f"{message.channel.mention}")
        embed.set_footer(text=f"Time of deletion:", )
        await channel.send(embed=embed)
        return

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel2 = self.bot.get_channel(int(action_log))
        embed = discord.Embed(colour=discord.Colour.green(), title=f"A channel was created!",
                              timestamp=datetime.datetime.now())
        embed.add_field(name="Channel:", value=f"{channel.mention}")

        await channel2.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        try:
            action_log = data.read("guild")[0][3]
            if action_log == "":
                return
            channel2 = self.bot.get_channel(int(action_log))
            embed = discord.Embed(colour=discord.Colour.red(), title=f"A channel was deleted!",
                                  timestamp=datetime.datetime.now())
            embed.add_field(name="Channel:", value=f"#{channel.name}")

            await channel2.send(embed=embed)
        except:
            return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            channel = await self.bot.fetch_channel(680579048162066452)
            if not before.channel and after.channel.id is not None:
                embed = discord.Embed(colour=discord.Colour.green(),
                                      title=f"{member.name} joined a Voice Channel",
                                      timestamp=datetime.datetime.now())
                embed.set_footer(text=f"ID: {member.id}")
                embed.set_author(
                    icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if member.avatar is None else member.avatar.url,
                    name=F"{member.name}#{member.discriminator}")
                embed.add_field(name="Channel:", value=f"{after.channel.name}")

                await channel.send(embed=embed)
            if before.channel.id is not None and not after.channel:
                embed = discord.Embed(colour=discord.Colour.red(), title=f"{member.name} left a Voice Channel",
                                      timestamp=datetime.datetime.now())
                embed.set_footer(text=f"ID: {member.id}")
                embed.set_author(
                    icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if member.avatar is None else member.avatar.url,
                    name=F"{member.name}#{member.discriminator}")
                embed.add_field(name="Channel:", value=f"{before.channel.name}")

                await channel.send(embed=embed)
            if before.channel.id is not None and after.channel.id is not None and not before.channel.id == after.channel.id:
                embed = discord.Embed(colour=discord.Colour.gold(),
                                      title=f"{member.name} moved to a different Voice Channel",
                                      timestamp=datetime.datetime.now())
                embed.set_footer(text=f"ID: {member.id}")
                embed.add_field(name="Old Channel:", value=f"{before.channel.name}")
                embed.add_field(name="New Channel:", value=f"{after.channel.name}")
                embed.set_author(
                    icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if member.avatar is None else member.avatar.url,
                    name=F"{member.name}#{member.discriminator}")
                await channel.send(embed=embed)
            else:
                pass
        except:
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.content == '':
            return
        if before.author.bot:
            return

        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel = self.bot.get_channel(int(action_log))

        embed = discord.Embed(
            colour=discord.Colour.gold(),
            title="Message edited",
            timestamp=datetime.datetime.now()
        )
        embed.set_author(
            icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if before.author.avatar is None else before.author.avatar.url,
            name=f"{before.author.name}#{before.author.discriminator}")
        embed.add_field(name=f"Pre-edit content:",
                        value=f"{before.content}",
                        inline=True)
        embed.add_field(name=f"Post-edit content:",
                        value=f"{after.content}",
                        inline=True)
        embed.add_field(name=f"Channel:",
                        value=f"{before.channel.mention}",
                        inline=False)
        embed.add_field(name=f"Message:",
                        value=f"[Jump to edited message.]({before.jump_url})",
                        inline=False)
        embed.set_footer(text=f"Time of edit:",
                         )
        await channel.send(embed=embed)
        return

    @commands.Cog.listener()
    async def on_guild_create_role(self, role):

        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel = self.bot.get_channel(int(action_log))
        embed = discord.Embed(color=discord.Colour.green(), title="Role was created")
        embed.add_field(name=f"info:", value=f"{role.name}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_delete_role(self, role):

        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel = self.bot.get_channel(int(action_log))
        embed = discord.Embed(color=discord.Colour.red(), title="Role was deleted")
        embed.add_field(name=f"info:", value=f"{role.name}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.name != after.name:

            action_log = data.read("guild")[0][3]
            if action_log == "":
                return
            channel = self.bot.get_channel(int(action_log))
            if before.name != after.name:
                embed = discord.Embed(colour=discord.Colour.gold(), title=f"A role name was changed",
                                      timestamp=datetime.datetime.now())

                embed.add_field(name=f"Before:", value=f"{before.name}")
                embed.add_field(name=f"After:", value=f"{after.name}")
                embed.set_footer(text=f"role ID: {before.id}")

                await channel.send(embed=embed)
        if before.color != after.color:
            action_log = data.read("guild")[0][3]
            if action_log == "":
                return
            channel = self.bot.get_channel(int(action_log))
            embed = discord.Embed(color=after.color, title=f"A role color was changed",
                                  timestamp=datetime.datetime.now())
            embed.add_field(name="Role name:", value=before.name, inline=False)
            embed.add_field(name=f"Before:", value=f"{before.color}")
            embed.add_field(name=f"After:", value=f"{after.color}")
            embed.set_footer(text=f"role ID: {before.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel = self.bot.get_channel(int(action_log))
        if before.nick != after.nick:
            embed = discord.Embed(colour=discord.Colour.gold(), title=f"{before.name}'s nickname was changed",
                                  timestamp=datetime.datetime.now())
            embed.set_author(
                icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if before.avatar is None else before.avatar.url,
                name=f"{before.name}#{before.discriminator}")

            embed.add_field(name=f"Before:", value=f"{before.nick}")
            embed.add_field(name=f"After:", value=f"{after.nick}")
            embed.set_footer(text=f"ID: {before.id}")

            await channel.send(embed=embed)
        if before.nick == after.nick and before.roles != after.roles:
            bef = [role.name for role in before.roles if not role.is_default()]
            aft = [role.name for role in after.roles if not role.is_default()]

            if len(before.roles) > len(after.roles):
                action = "removed"
            if len(before.roles) < len(after.roles):
                action = "added"

            def predifference(bef, aft):
                return (list(set(bef) - set(aft)))

            def postdifference(bef, aft):
                return (list(set(aft) - set(bef)))

            if len(before.roles) > len(after.roles):
                repl = str(predifference(bef, aft))
            if len(before.roles) < len(after.roles):
                repl = str(postdifference(bef, aft))

            repl1 = repl.replace('[', '', 1)
            repl2 = repl1.replace(']', '', 1)
            repl3 = repl2.replace("'", '', 2)
            role = discord.utils.get(before.guild.roles, name=str(repl3))
            embed = discord.Embed(colour=discord.Colour.gold(), title=f"{before.name}'s roles were updated",
                                  timestamp=datetime.datetime.now())
            embed.set_author(
                icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if before.avatar is None else before.avatar.url,
                name=f"{before.name}#{before.discriminator}")

            embed.add_field(name=f"Role {action}:", value=f"{role.mention}")

            embed.set_footer(text=f"ID: {before.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel = self.bot.get_channel(int(action_log))

        embed = discord.Embed(color=discord.Colour.green(),
                              timestamp=datetime.datetime.now(),
                              description=f"{member.mention} has joined the server!")
        embed.set_author(
            icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if member.avatar is None else member.avatar.url,
            name=f"{member.name}#{member.discriminator}")
        embed.add_field(name="User info",
                        value=f"{member.name}#{member.discriminator} (**{member.id}**)")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/embed/avatars/1.png" if member.avatar is None else member.avatar.url)
        embed.add_field(name="Account Created",
                        value=member.created_at.strftime("%A, %b %d %Y"), inline=False)
        embed.add_field(name="Member count:",
                        value=member.guild.member_count, inline=False)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        action_log = data.read("guild")[0][3]
        if action_log == "":
            return
        channel = self.bot.get_channel(int(action_log))
        embed = discord.Embed(color=member.top_role.color,
                              timestamp=datetime.datetime.now())
        embed.set_author(
            icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if member.avatar is None else member.avatar.url,
            name=f"{member.name} has left the server!")
        embed.add_field(name="User info",
                        value=f"{member.name}#{member.discriminator} (**{member.id}**)", inline=False)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/embed/avatars/1.png" if member.avatar is None else member.avatar.url)
        embed.add_field(name="Created at:",
                        value=member.created_at.strftime("%A, %b %d %Y"), inline=True)
        embed.add_field(name="Joined at:",
                        value=member.joined_at.strftime("%A, %b %d %Y"), inline=True)
        embed.add_field(name="Member count:",
                        value=member.guild.member_count, inline=False)
        embed.add_field(name="Top role:",
                        value=member.top_role.mention, inline=True)

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logging(bot))
    return logger.log("Event Logging Online.", logger.logtypes.info)

