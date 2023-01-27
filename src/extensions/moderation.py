import datetime
import sqlite3
import sys

import discord
from discord import app_commands
from discord.ext import commands, tasks

from src.utils import pagination
from src.utils.permissions import permissions_check, u_vs_u_permission, command
import src.utils.logger as logger
import src.utils.data as data
from src.utils.math import duration_check


class ModLog:

    @staticmethod
    def write_log(user, reason, action, mod, date, duration="N/A") -> int:
        case = (data.count("moderations") + 1)
        data.write("moderations", [user, reason, action, mod, date, case, str(duration)])
        return case

    @staticmethod
    def read_log(case) -> list:
        return data.read("moderations", str(case), 'cid')[0]

    @staticmethod
    def read_all_logs(user_id) -> list:
        return data.read("moderations", user_id, 'user', True)

    @staticmethod
    def check_case(case) -> bool:
        return data.exists("moderations", str(case), 'cid')

    @staticmethod
    def delete_case(case) -> None:
        return data.delete("moderations", 'cid', str(case))

    @staticmethod
    def update_case(case, reason):
        return data.update("moderations", 'reason', f"'{reason}'", 'cid', str(case), False)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ban_check.start()

    @tasks.loop(seconds=30)
    async def ban_check(self):

        db = sqlite3.connect("src/storage/databases/bans.db")
        cursor = db.cursor()
        cursor.execute('SELECT unban_time, guild_id, member_id FROM bans')
        results = cursor.fetchall()
        for entry in results:
            try:
                parsed_data = entry[0][:-6]
                date_time_obj = datetime.datetime.strptime(parsed_data, '%Y-%m-%d %H:%M:%S.%f')
                if date_time_obj.date() <= datetime.datetime.now().date():
                    compare1 = date_time_obj.timestamp()

                    compare2 = datetime.datetime.now().timestamp()

                    if int(compare1) < int(compare2):
                        action_log = data.read("guild")[0][2]
                        if action_log == "":
                            return
                        channel = self.bot.get_channel(int(action_log))
                        guild = await self.bot.fetch_guild(int(entry[1]))
                        member = await self.bot.fetch_user(int(entry[2]))
                        try:
                            await guild.unban(member, reason="Times up!")
                        except discord.NotFound:
                            logger.log("Auto-Unban - User to unban wasn't found. (possibly deleted account)",
                                       logger.logtypes.error)
                        db = sqlite3.connect("src/storage/databases/bans.db")
                        cursor = db.cursor()
                        cursor.execute(f"DELETE FROM bans WHERE guild_id = '{entry[1]}' AND member_id = '{entry[2]}'")
                        db.commit()
                        db.close()
                        me = self.bot.user
                        embed = discord.Embed(
                            colour=discord.Colour.green(),
                            title="Automatic Unban",
                            timestamp=datetime.datetime.utcnow()

                        )
                        if member.avatar is None:
                            url = "https://cdn.discordapp.com/embed/avatars/1.png"
                        else:
                            url = member.avatar.url
                        embed.set_author(icon_url=url,
                                         name=f"{member.name}#{member.discriminator}")
                        embed.add_field(name="Moderator:", value=f"{me.name}#{me.discriminator}",
                                        inline=True)
                        embed.add_field(name="Member:", value=f"{member}",
                                        inline=True)
                        embed.add_field(name="Reason:", value="Ban was temporary", inline=False)
                        embed.set_footer(icon_url=url, text=f"ID {member.id}")
                        await channel.send(embed=embed)

                    else:
                        pass
            except Exception as err:
                logger.log(f"Auto-Unban - E01: {err}", logger.logtypes.error)
                pass

    @app_commands.command(name="warn", description="Warn a user.")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, *,
                   reason: str = "No reason provided."):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot warn yourself.", ephemeral=True)
        if not u_vs_u_permission(interaction, user, moderator=True):
            return await interaction.response.send_message("You cannot warn this user.", ephemeral=True)
        case = ModLog.write_log(user.id, reason, "Warn", interaction.user.id, datetime.datetime.now())
        await interaction.response.send_message(f"Warned {user.mention} for `{reason}`. Case #{case}", ephemeral=True)
        await logger.action_log(reason, f"Warn | Case #{case}", user, logger.logtypes.warning, interaction, True)
        try:
            await user.send(f"You have been warned in {interaction.guild.name} for `{reason}`")
        except discord.Forbidden:
            return

    @app_commands.command(name="kick", description="Kick a user.")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, *,
                   reason: str = "No reason provided."):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot kick yourself.", ephemeral=True)
        if not u_vs_u_permission(interaction, user, moderator=True):
            return await interaction.response.send_message("You cannot kick this user.", ephemeral=True)
        case = ModLog.write_log(user.id, reason, "Kick", interaction.user.id, datetime.datetime.now())
        await logger.action_log(reason, f"Kick | Case #{case}", user, logger.logtypes.warning, interaction, True)
        await interaction.response.send_message(f"Kicked {user.mention} for `{reason}`. Case #{case}", ephemeral=True)
        try:
            await user.send(f"You have been kicked from {interaction.guild.name} for `{reason}`")
        except discord.Forbidden:
            pass
        await user.kick(reason=reason)

    # softban
    @app_commands.command(name="soft-ban", description="Soft-ban a user.")
    async def soft_ban(self, interaction: discord.Interaction, user: discord.Member, *,
                       reason: str = "No reason provided."):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot soft-ban yourself.", ephemeral=True)
        if not u_vs_u_permission(interaction, user, moderator=True):
            return await interaction.response.send_message("You cannot soft-ban this user.", ephemeral=True)
        case = ModLog.write_log(user.id, reason, "Soft-ban", interaction.user.id, datetime.datetime.now())
        await logger.action_log(reason, f"Soft-ban | Case #{case}", user, logger.logtypes.warning, interaction, True)
        await interaction.response.send_message(f"Soft-banned {user.mention} for `{reason}`. Case #{case}",
                                                ephemeral=True)
        try:
            await user.send(f"You have been kicked from {interaction.guild.name} for `{reason}`")
        except discord.Forbidden:
            pass
        await user.ban(reason=reason)
        await interaction.guild.unban(user, reason=reason)

    # mute (use timeouts)
    @app_commands.command(name="mute", description="Mute a user.")
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: str, *,
                   reason: str = "No reason provided."):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot mute yourself.", ephemeral=True)
        if not u_vs_u_permission(interaction, user, moderator=True):
            return await interaction.response.send_message("You cannot mute this user.", ephemeral=True)
        if not duration_check(duration):
            return await interaction.response.send_message("Invalid duration.", ephemeral=True)
        case = ModLog.write_log(user.id, reason, "Mute", interaction.user.id, datetime.datetime.now(), duration)
        await logger.action_log(f"{reason}\n\nDuration: {duration}", f"Mute | Case #{case}", user,
                                logger.logtypes.warning, interaction, True)
        await interaction.response.send_message(f"Muted {user.mention} for `{reason}`. Case #{case}", ephemeral=True)
        try:
            await user.send(f"You have been muted in {interaction.guild.name} for `{reason}`")
        except discord.Forbidden:
            pass
        await user.timeout(duration_check(duration)[1], reason=reason)

    @app_commands.command(name="unmute", description="Unmute a user.")
    async def unmute(self, interaction: discord.Interaction, user: discord.Member, *,
                     reason: str = "N/A"):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot unmute yourself.", ephemeral=True)
        if not u_vs_u_permission(interaction, user, moderator=True):
            return await interaction.response.send_message("You cannot unmute this user.", ephemeral=True)
        case = ModLog.write_log(user.id, reason, "Unmute", interaction.user.id, datetime.datetime.now())
        await logger.action_log(f"{reason}", f"Unmute | Case #{case}", user, logger.logtypes.success, interaction,
                                True)
        await interaction.response.send_message(f"Unmuted {user.mention} for `{reason}`. Case #{case}", ephemeral=True)
        try:
            await user.send(f"You have been unmuted in {interaction.guild.name} for `{reason}`")
        except discord.Forbidden:
            pass
        await user.timeout(None, reason=reason)

    @app_commands.command(name="ban", description="Ban a user.")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, duration: str = None,
                  reason: str = "No reason provided."):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot ban yourself.", ephemeral=True)
        if not u_vs_u_permission(interaction, user, moderator=True):
            return await interaction.response.send_message("You cannot ban this user.", ephemeral=True)
        if not duration_check(duration):
            return await interaction.response.send_message("Invalid duration.", ephemeral=True)
        case = ModLog.write_log(user.id, reason, "Ban", interaction.user.id, datetime.datetime.now(), duration)
        await logger.action_log(f"{reason}\n\nDuration: {duration}", f"Ban | Case #{case}", user,
                                logger.logtypes.error, interaction, True)
        await interaction.response.send_message(f"Banned {user.mention} for `{reason}` ({duration}). Case #{case}"
                                                , ephemeral=True)
        try:
            await user.send(
                f"You have been banned from {interaction.guild.name} for `{reason}` with a duration of {duration} ")
        except discord.Forbidden:
            pass
        await user.ban(reason=reason, delete_message_days=0)
        db = sqlite3.connect("src/storage/databases/bans.db")
        cursor = db.cursor()
        cursor.execute(
            f"INSERT INTO bans(guild_id, member_id, unban_time) VALUES"
            f"('{interaction.guild.id}', '{user.id}', '{duration_check(duration)[1]}')")
        db.commit()
        db.close()

    @app_commands.command(name="unban", description="Unban a user.")
    async def unban(self, interaction: discord.Interaction, user: discord.User, *, reason: str = "N/A"):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if user.id == interaction.user.id:
            return await interaction.response.send_message("You cannot unban yourself.", ephemeral=True)
        case = ModLog.write_log(user.id, reason, "Unban", interaction.user.id, datetime.datetime.now())
        await logger.action_log(f"{reason}", f"Unban | Case #{case}", user, logger.logtypes.success, interaction, True)
        await interaction.guild.unban(user, reason=reason)
        await interaction.response.send_message(f"Unbanned {user.mention} for `{reason}`. Case #{case}", ephemeral=True)

    @app_commands.command(name="mod-log", description="View a moderation incident.")
    async def mod_log(self, interaction: discord.Interaction, case: int = None, member: discord.Member = None):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if permissions_check(interaction, sys._getframe().f_code.co_name):

            if case is None and member is None:
                await interaction.response.send_message(f":x: You must specify a case or a member.", ephemeral=True)
                return
            elif case is not None and member is not None:
                await interaction.response.send_message(f":x: You must specify only one option.", ephemeral=True)
                return
            elif case is None:
                result = ModLog.read_all_logs(str(member.id))
                values = []
                count = 0
                for entry in result:
                    count = count + 1

                    values.append(
                        f"**Case #{entry[5]}**\nDate: {entry[4].split(' ')[0]}\nModerator: <@!{entry[3]}>\nPunishment: {entry[2]}\nReason: {entry[1]}\n Duration: {entry[6]}")

                query = "\n\n".join(values)

                embed = discord.Embed(colour=discord.Colour.blue(), description=f"{query}")
                embed.set_author(
                    icon_url=member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/1.png",
                    name=f"{count} Mod logs found for: {member.name}#{member.discriminator}")
                try:
                    await interaction.response.send_message(embed=embed)
                except Exception:
                    thing = [values[i:i + 10] for i in range(0, len(values), 10)]
                    embeds = []
                    pcount = 0
                    for x in thing:
                        pcount = pcount + 1
                        tot = '\n\n'.join(x)
                        embed = discord.Embed(colour=discord.Colour.blue(),
                                              title=f"Page {pcount} out of {len(thing)}",
                                              description=f"{tot}").set_author(
                            icon_url=member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/1.png",
                            name=f"{count} Mod logs found for: {member.name}#{member.discriminator}")
                        embeds.append(embed)
                    paginator = pagination.CustomEmbedPaginator(interaction, remove_reactions=True,
                                                                timeout=120)
                    paginator.add_reaction('⏮️', "first")
                    paginator.add_reaction('⏪', "back")
                    paginator.add_reaction('⏩', "next")
                    paginator.add_reaction('⏭️', "last")
                    paginator.add_reaction('🗑️', "delete")
                    await paginator.run(embeds, 0)
            else:
                db = sqlite3.connect('src/storage/databases/moderations.db')
                cursor = db.cursor()
                cursor.execute(
                    f'SELECT * FROM moderations WHERE cid = {case}')
                result = cursor.fetchall()
                if not result:
                    await interaction.response.send_message(f":x: No case found with that ID.", ephemeral=True)
                    return
                values = []
                count = 0
                member = await self.bot.fetch_user(int(result[0][0]))
                for entry in result:
                    count = count + 1

                    values.append(
                        f"**Case #{entry[5]}**\nDate: {entry[4].split(' ')[0]}\nModerator: <@!{entry[3]}>\nPunishment:"
                        f" {entry[2]}\nReason: {entry[1]}\n Duration: {entry[6]}")

                query = "\n\n".join(values)
                embed = discord.Embed(colour=discord.Colour.blue(), description=f"{query}")
                embed.set_author(
                    icon_url=member.avatar.url if member.avatar is not None else
                    "https://cdn.discordapp.com/embed/avatars/1.png",
                    name=f"{count} Mod logs found for: {member.name}#{member.discriminator}")
                try:
                    await interaction.response.send_message(embed=embed)
                except Exception:
                    await interaction.response.send_message(":x: Result too large.", ephemeral=True)

    @app_commands.command(name="modify-log", description="Change/delete a moderation incident.")
    async def modify_log(self, interaction: discord.Interaction, case: int, reason: str = None):
        if command(sys._getframe().f_code.co_name):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if not reason:
                ModLog.delete_case(case)
                return await interaction.response.send_message(f":white_check_mark: Case #{case} has been deleted.",
                                                               ephemeral=True)
            else:
                ModLog.update_case(case, reason)
                return await interaction.response.send_message(f":white_check_mark: Case #{case} has been updated.",
                                                               ephemeral=True)
        else:
            await interaction.response.send_message(f":x: You have insufficient permissions.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
    return logger.log("Moderation Commands Online.", logger.logtypes.info)

