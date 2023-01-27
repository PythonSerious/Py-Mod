import sys

import discord
from discord import app_commands
from discord.ext import commands

from src.utils import logger, data
from src.utils.permissions import permissions_check, command
from src.utils.modal import Modal
from src.utils import pagination



class Utilities(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Am I alive?")
    async def ping(self, interaction: discord.Interaction):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)

        await interaction.response.send_message(f"Pong!")

    @app_commands.command(name="clean", description="Remove bots messages from a channel.")
    async def clean(self, interaction: discord.Interaction, amount: int) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            messages = [message async for message in interaction.channel.history(limit=amount)]
            tobedeleted = []
            for msg in messages:
                if msg.author.bot or msg.content.startswith('!'):
                    tobedeleted.append(msg)
            if len(tobedeleted) >= 100:
                return await interaction.response.send_message(f":x: I can't delete more than 100 messages at once.",
                                                               ephemeral=True)
            await interaction.channel.delete_messages(tobedeleted)
            try:
                await interaction.response.send_message(
                    f":white_check_mark: I have deleted {len(tobedeleted)} bot messages.",
                    ephemeral=True)
            except:
                logger.log("Could not send message confirmation.", logger.logtypes.error)
        else:
            return await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                           ephemeral=True)

    @app_commands.command(name="purge", description="Purge a channel of all messages.")
    async def purge(self, interaction: discord.Interaction, amount: int) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            await interaction.response.send_message(f":white_check_mark: Deleting messages...", ephemeral=True)
            if amount > 100:
                await interaction.channel.purge(limit=amount)
                return await interaction.response.send_message(
                    f"<:yes:825954068014563368> {amount} message{'s' if amount > 1 else ''} were purged!",
                    ephemeral=True)

            else:

                messages = [message async for message in interaction.channel.history(limit=amount)]
                tbd = []
                for msg in messages:
                    tbd.append(msg)
                await interaction.channel.delete_messages(tbd)

                action_log = data.read("guild")[0][2]
                if action_log == "":
                    return
                channel = self.bot.get_channel(int(action_log))

                embed = discord.Embed(
                    colour=discord.Colour.blue(),
                    title="Purge",
                )
                embed.set_author(icon_url=interaction.user.avatar.url,
                                 name=f"{interaction.user.name}#{interaction.user.discriminator}")
                embed.add_field(name="Moderator:", value=f"{interaction.user.name}#{interaction.user.discriminator}",
                                inline=True)
                embed.add_field(name="Messages cleared:", value=f"{amount}", inline=True)
                embed.add_field(name="Channel:", value=f"{interaction.channel.mention}",
                                inline=False)
                await channel.send(embed=embed)
        else:
            return await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                           ephemeral=True)

    @app_commands.command(name="av", description="Get users avatar.")
    async def av(self, interaction: discord.Interaction, user: discord.Member) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if user.avatar is None:
                return await interaction.response.send_message(f":x: User has no avatar.", ephemeral=True)
            else:
                embed = discord.Embed(color=user.top_role.color)
                embed.set_author(icon_url=user.avatar.url, name=f"{user.name}#{user.discriminator}")
                embed.set_image(url=user.avatar.url)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            return await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                           ephemeral=True)

    @app_commands.command(name="members", description="Get Members of a role.")
    async def members(self, interaction: discord.Interaction, role: discord.Role) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            mem_list = []
            for member in role.members:
                statuses = {
                    "online": ":green_circle:",
                    "dnd": ":red_circle:",
                    "idle": ":yellow_circle:",
                    "offline": ":black_circle:"
                }
                emoji2 = statuses.get(str(member.status), "<:invisible:829928428819972106>")
                mem_list.append(f"{emoji2} **{member.name}#{member.discriminator}** (`{member.id}`)")

            thing = [mem_list[i:i + 15] for i in range(0, len(mem_list), 15)]
            embeds = []
            p_count = 0
            for x in thing:
                p_count += 1
                tot = '\n'.join(x)
                embed = discord.Embed(color=role.color, title=f"Page {p_count} out of {len(thing)}",
                                      description=f"\n{tot}").set_author(icon_url=interaction.guild.icon.url,
                                                                         name=f"Showing members in {role.name}")
                embeds.append(embed)
            paginator = pagination.CustomEmbedPaginator(interaction, remove_reactions=True, timeout=120, resp=0)
            paginator.add_reaction('⏮️', "first")
            paginator.add_reaction('⏪', "back")
            paginator.add_reaction('⏩', "next")
            paginator.add_reaction('⏭️', "last")
            paginator.add_reaction('🗑️', "delete")
            await paginator.run(embeds, send_to=0)
        else:
            return await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                           ephemeral=True)

    @app_commands.command(name="say", description="Make the bot say something.")
    async def say(self, interaction: discord.Interaction, embedded: bool) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        async def action(s, i, answers, user):
            if not s:
                pass
            if not user:
                pass
            if len(answers) > 1:
                title = answers[0]
                description = answers[1]
                color = answers[2]
                c = discord.Colour
                colorTable = {
                    "red": c.red(),
                    "blue": c.blue(),
                    "yellow": c.gold(),
                    "green": c.green(),
                    "purple": c.purple(),
                    "orange": c.orange()
                }
                try:
                    embed = discord.Embed(
                        title=title,
                        colour=colorTable[color],
                        description=description
                    )
                    await i.channel.send(embed=embed)
                except:
                    try:
                        hexValue = color.strip("#")
                        hexValue = hexValue.strip("0x")
                        color = int(f"0x{hexValue}", 16)
                        embed = discord.Embed(color=color, title=title, description=description)
                        await i.channel.send(embed=embed)
                    except:
                        return await i.response.send_message(f":x: Invalid color.", ephemeral=True)
            else:
                await i.channel.send(answers[0])
            return await i.response.send_message(f":white_check_mark:", ephemeral=True)

        if permissions_check(interaction, sys._getframe().f_code.co_name):
            questions = [discord.ui.TextInput(label='Content:', style=discord.TextStyle.long,
                                              required=True)]
            if embedded:
                questions = [discord.ui.TextInput(label='Title:', style=discord.TextStyle.short, required=True),
                             discord.ui.TextInput(label='Description:', style=discord.TextStyle.long, required=True),
                             discord.ui.TextInput(label='Color:', style=discord.TextStyle.short, required=True)]

            await Modal(f"Say {'' if not embedded else 'Embed'}", questions, action, interaction,
                        interaction.user).fireModal(False)

        else:
            await interaction.response.send_message(f":x: You have insufficient permissions.", ephemeral=True)

    @app_commands.command(name="slow-mode", description="Sets the slow-mode for the current channel.")
    async def slow_mode(self, interaction: discord.Interaction, amount: int) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            await interaction.channel.edit(slowmode_delay=amount)
            await interaction.response.send_message(f":white_check_mark: Set slow-mode to `{amount}` seconds.",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                    ephemeral=True)

    @app_commands.command(name="profile", description="View a user's profile.")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                    ephemeral=True)
        if not user:
            user = interaction.user
        image_user = await interaction.client.fetch_user(user.id)

        if image_user.banner:
            banner = image_user.banner.url
        else:
            banner = "https://cdn.discordapp.com/attachments/916849586230939658/1046008717801431080/image.png"

        if image_user.avatar:
            avatar = image_user.avatar.url
        else:
            avatar = interaction.guild.icon.url

        if user.premium_since:
            boost = user.premium_since.strftime("%B %d, %Y")
        else:
            boost = "Not a booster."
        embed = discord.Embed(color=image_user.accent_color, title=f"{user.name}'s Profile")
        embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.set_image(url=banner)
        embed.add_field(name="ID", value="`" + str(user.id) + "`", inline=False)
        embed.add_field(name="Account Created", value="`" + user.created_at.strftime("%B %d, %Y") + "`", inline=False)
        embed.add_field(name="Joined Server", value="`" + user.joined_at.strftime("%B %d, %Y") + "`", inline=False)
        embed.add_field(name="Boosting Since", value="`" + boost + "`", inline=False)
        roles = []
        for role in user.roles:
            roles.append(role.mention)

        roles.pop(0)
        roles.reverse()
        embed.add_field(name="Roles", value=" ".join(roles), inline=False)
        activity_member = interaction.guild.get_member(user.id)
        embed.add_field(name="Status", value="`" + str(activity_member.status) + "`", inline=False)

        if activity_member.activity:
            if activity_member.activity.name == "Spotify":
                embed.add_field(name="Spotify", value="`" + str(activity_member.activity.title) + " | " + str(
                    activity_member.activity.artist) + "`", inline=False)
            else:
                if hasattr(activity_member.activity, "details"):
                    embed.add_field(name="Activity", value="`" + str(activity_member.activity.name) + " | " + str(
                        activity_member.activity.details) + "`", inline=False)
                else:
                    embed.add_field(name="Activity", value="`" + str(activity_member.activity.name) + "`", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quote", description="Quote a message.")
    async def quote(self, interaction: discord.Interaction, url: str) -> None:
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)

        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if not "https://" and not "discord.com/channels/" in url:
                return await interaction.response.send_message(":x: Invalid message URL.", ephemeral=True)
            try:

                mounts = url.split("/")
                channel = await self.bot.fetch_channel(int(mounts[5]))
                msg = await channel.fetch_message(int(mounts[6]))
                emb_dict = msg.embeds[0]
                def_emb = discord.Embed(color=0x2f3136,
                                        description=f"**Sent in** {channel.mention} [Jump to Message]({msg.jump_url})")
                def_emb.set_author(icon_url=msg.author.avatar.url, name=f"{msg.author.name}#{msg.author.discriminator}")
                await interaction.response.send_message(embed=def_emb)

                await interaction.channel.send(embed=emb_dict)
            except Exception:
                try:
                    mounts = url.split("/")
                    channel = await self.bot.fetch_channel(int(mounts[5]))
                    msg = await channel.fetch_message(int(mounts[6]))
                    def_emb = discord.Embed(color=0x2f3136,
                                            description=f"**Sent in** {channel.mention} [Jump to Message]({msg.jump_url})")
                    def_emb.set_author(icon_url=msg.author.avatar.url,
                                       name=f"{msg.author.name}#{msg.author.discriminator}")
                    def_emb.add_field(name="Content", value=msg.content)
                    await interaction.response.send_message(embed=def_emb)

                except Exception:
                    mounts = url.split("/")
                    channel = await self.bot.fetch_channel(int(mounts[5]))
                    msg = await channel.fetch_message(int(mounts[6]))
                    def_emb = discord.Embed(color=0x2f3136,
                                            description=f"**Sent in** {channel.mention} [Jump to Message]({msg.jump_url})\n\n**Content**\n{msg.content}")
                    def_emb.set_author(icon_url=msg.author.avatar.url,
                                       name=f"{msg.author.name}#{msg.author.discriminator}")
                    await interaction.response.send_message(embed=def_emb)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utilities(bot))
    return logger.log("Utilities Commands Online.", logger.logtypes.info)
