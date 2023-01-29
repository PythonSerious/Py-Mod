import sys

import discord
from discord import app_commands
from discord.ext import commands
import json
from src.utils import logger
from src.utils.permissions import permissions_check, command
import src.utils.data as data


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    settings_group = app_commands.Group(name="settings", description="Change the bot's settings.")

    @settings_group.command(name="status", description="Change the bot's status")
    async def status(self, interaction: discord.Interaction, status_type: int, status: str):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        if status_type > 3 or status_type < 1:
            return await interaction.response.send_message("Invalid status type. Valid types are 1-3", ephemeral=True)
        full_dump = f"{status_type}0DATA_TYPE_SPLIT0{status}"
        data.update_all("guild", "'status'", f"'{full_dump}'")
        await self.bot.change_presence(status=discord.Status.online,
                                       activity=discord.Activity(type=status_type, name=status))
        await interaction.response.send_message(":white_check_mark: Status saved!")

    @settings_group.command(name="moderator-roles", description="Change the bot's moderator roles")
    async def mod_roles(self, interaction: discord.Interaction):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        await interaction.response.send_message("Please mention the roles you would like to add as moderator "
                                                "roles.\n(Seperate them by spaces)")
        message = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user)
        if not "<@&" in message.content:
            return await interaction.response.edit_message("No roles mentioned.", ephemeral=True)
        roles = message.content.replace("<@&", "").replace(">", "").split(" ")
        data.update_all("guild", "'modroles'", f"'{', '.join(roles)}'")
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        await interaction.edit_original_response(content=":white_check_mark: Moderator roles saved!")

    @settings_group.command(name="admin-roles", description="Change the bot's admin roles")
    async def admin_roles(self, interaction: discord.Interaction):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        await interaction.response.send_message("Please mention the roles you would like to add as admin "
                                                "roles.\n(Seperate them by spaces)")
        message = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user)
        if not "<@&" in message.content:
            return await interaction.response.edit_message("No roles mentioned.", ephemeral=True)
        roles = message.content.replace("<@&", "").replace(">", "").split(" ")
        data.update_all("guild", "'adminroles'", f"'{', '.join(roles)}'")
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        await interaction.edit_original_response(content=":white_check_mark: Admin roles saved!")

    @settings_group.command(name="action-logs", description="Change the bot's action logs channel")
    async def action_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        data.update_all("guild", "'actionlogs'", f"'{channel.id}'")
        await interaction.response.send_message(":white_check_mark: Action logs channel saved!")

    @settings_group.command(name="mod-logs", description="Change the bot's mod logs channel")
    async def mod_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        data.update_all("guild", "'modlogs'", f"'{channel.id}'")
        await interaction.response.send_message(":white_check_mark: Mod logs channel saved!")

    @settings_group.command(name="bot-logs", description="Change the bot status logs channel.")
    async def bot_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        # create a webhook in the channel
        try:
            webhook = await channel.create_webhook(name=f"{interaction.client.user.name} Logs")
        except discord.Forbidden:
            return await interaction.response.send_message(
                f":x: I was unable to create a webhook in {channel.mention}. "
                f"Please ensure I have the correct permissions.", ephemeral=True)
        with open("src/storage/config.json", "r") as f:
            json_file = json.load(f)
        json_file["webhook"] = webhook.url
        with open("src/storage/config.json", "w") as f:
            json.dump(json_file, f, indent=4)
        await interaction.response.send_message(":white_check_mark: Bot logs channel saved! Please restart the bot.")

    @settings_group.command(name="ticket_welcome", description="Change the message displayed when a ticket is created.")
    async def ticket_welcome(self, interaction: discord.Interaction):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        await interaction.response.send_message("Please enter the message you would like to be displayed when a ticket "
                                                "is created.")
        message = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user)
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        with open("src/storage/config.json", "r") as f:
            json_file = json.load(f)
        json_file["ticket_welcome"] = message.content
        with open("src/storage/config.json", "w") as f:
            json.dump(json_file, f, indent=4)
        await interaction.edit_original_response(content=":white_check_mark: Ticket welcome message saved!")

    @settings_group.command(name="ticket_general",
                            description="Change the prompt message displayed before a ticket is created.")
    async def ticket_general(self, interaction: discord.Interaction):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        await interaction.response.send_message(
            "Please enter the message you would like to be displayed in the pre-open embed.")
        message = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user)
        with open("src/storage/ticket_message.txt", "w") as f:
            f.write(message.content)
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        await interaction.edit_original_response(
            content=":white_check_mark: Ticket welcome message saved! (You must reboot and re-setup the ticket system)")

    @settings_group.command(name="commands", description="Enable/Disable the bot's commands")
    async def commands(self, interaction: discord.Interaction, extension: str, edit_command: str, status: bool):
        if command("settings"):
            return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
        if not permissions_check(interaction, sys._getframe().f_code.co_name):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True)
        with open("src/storage/config.json", "r") as f:
            config_file = json.load(f)
        if extension.lower() not in config_file["commands"]:
            return await interaction.response.send_message(":x: Invalid extension!", ephemeral=True)
        if edit_command.lower() not in config_file["commands"][extension.lower()]:
            return await interaction.response.send_message(":x: Invalid command!", ephemeral=True)
        config_file["commands"][extension.lower()][edit_command.lower()]["enabled"] = status
        with open("src/storage/config.json", "w") as f:
            json.dump(config_file, f, indent=4)
        await interaction.response.send_message(f":white_check_mark: {edit_command.lower()} is now "
                                                f"{'enabled' if status else 'disabled'}!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Settings(bot))
    return logger.log("Settings Commands Online.", logger.logtypes.info)
