from typing import List

import discord
from discord import app_commands, ui
from discord import Interaction
from discord.ext import commands
from discord.utils import get
import ast
import datetime
import os
import sys
import requests

from src.utils import logger
from src.utils.permissions import permissions_check, command


class Development(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokens = {}
        self.previous_image = None

    class eval_modal(ui.Modal, title="Execute Code"):
        def insert_returns(self, body):
            # insert return stmt if the last expression is a expression statement
            if isinstance(body[-1], ast.Expr):
                body[-1] = ast.Return(body[-1].value)
                ast.fix_missing_locations(body[-1])

            # for if statements, we insert returns into the body and the orelse
            if isinstance(body[-1], ast.If):
                self.insert_returns(body[-1].body)
                self.insert_returns(body[-1].orelse)

            # for with blocks, again we insert returns into the body
            if isinstance(body[-1], ast.With):
                self.insert_returns(body[-1].body)

        async def execute(self, code, interaction: discord.Interaction) -> str:
            fn_name = "_eval_expr"

            cmd = self.code.value

            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            self.insert_returns(body)

            env = {
                'client': interaction.client,
                'bot': interaction.client,
                'discord': discord,
                'commands': commands,
                'interaction': interaction,
                '__import__': __import__,
                'datetime': datetime,
                'os': os,
                'get': get,
                'req': requests
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))
            if result is None:
                return "No code output."
            else:
                return result

        code = ui.TextInput(label="Code:", placeholder="Enter code here...", style=discord.TextStyle.paragraph,
                            required=True)

        async def on_submit(self, interaction: Interaction) -> None:
            await interaction.response.defer(ephemeral=False, thinking=False)
            embed = discord.Embed(color=discord.Color.green(), title="Code Execution", description="")
            embed.set_author(name=interaction.client.user.name, icon_url=interaction.client.user.avatar.url)
            embed.set_footer(
                text=f"Requested by {interaction.user.name}#{interaction.user.discriminator} ({interaction.user.id})",
                icon_url=interaction.user.avatar.url)
            embed.add_field(name="Output", value="```\nExecuting...\n```", inline=False)
            msg = await interaction.channel.send(embed=embed)
            try:
                result = await self.execute(self.code.value, interaction)
            except Exception as e:
                embed = discord.Embed(color=discord.Color.red(), title="Code Execution", description="")
                embed.set_author(name=interaction.client.user.name, icon_url=interaction.client.user.avatar.url)
                embed.set_footer(
                    text=f"Requested by {interaction.user.name}#{interaction.user.discriminator} ({interaction.user.id})",
                    icon_url=interaction.user.avatar.url)
                embed.add_field(name="Output: errored", value=f"```\n{e}\n```", inline=False)
                await msg.edit(embed=embed)
                return
            embed.remove_field(0)
            file = False
            if len(str(result)) > 950:
                file = True
                with open("src/storage/developer/evaloutput.txt", "w") as f:
                    f.write(str(result))

                embed.add_field(name="Output: success",
                                value=f"```\nOutput too large to display. Saved to "
                                      f"src/storage/developer/evaloutput.txt\n```",
                                inline=False)
            else:
                embed.add_field(name="Output: success", value=f"```\n{result}\n```", inline=False)
            await msg.edit(embed=embed)
            if file:
                await interaction.channel.send(file=discord.File("src/storage/developer/evaloutput.txt"))

    @app_commands.command(name="eval")
    async def eval_command(self, interaction: discord.Interaction):

        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if command(sys._getframe().f_code.co_name):
                return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
            await interaction.response.send_modal(self.eval_modal())
        else:
            await interaction.response.send_message(":x: You do not have permission to use this command.",
                                                    ephemeral=True)

    @app_commands.command(name="extension")
    async def extension_command(self, interaction: discord.Interaction, action: str, extension: str):
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if command(sys._getframe().f_code.co_name):
                return await interaction.response.send_message(":x: This command is disabled.", ephemeral=True)
            msg = await self.bot.extension_handler(action, extension)
            return await interaction.channel.send(msg)
        else:
            await interaction.response.send_message(":x: You do not have permission to use this command.",
                                                    ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Development(bot))
    return logger.log("Developer Commands Online.", logger.logtypes.info)

