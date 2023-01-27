import json

import discord
from discord.app_commands import AppCommandError
from discord.ext import commands

from src.storage.config import token, non_slash_prefix
from src.utils import logger
import src.utils.data as data


class BOT(commands.Bot):
    def __init__(self, application_id: int):
        super().__init__(non_slash_prefix, intents=discord.Intents.all(), application_id=application_id)

    async def extension_handler(self, action: str, extension: str):
        if action == "load":
            try:
                await self.load_extension(f"src.extensions.{extension}")
                await self.tree.sync()
                logger.log(f"Loaded extension {extension}.", logtype=logger.logtypes.success)
                return f"Loaded extension {extension}."
            except Exception as e:
                logger.log(f"Failed to load extension {extension}. - {e}", logtype=logger.logtypes.error)
                return f"Failed to load extension {extension}. - {e}"
        elif action == "unload":
            try:
                await self.unload_extension(f"src.extensions.{extension}")
                await self.tree.sync()
                logger.log(f"Unloaded extension {extension}.", logtype=logger.logtypes.success)
                return f"Unloaded extension {extension}."
            except Exception as e:
                logger.log(f"Failed to unload extension {extension}. - {e}", logtype=logger.logtypes.error)
                return f"Failed to unload extension {extension}. - {e}"
        elif action == "reload":
            try:
                await self.unload_extension(f"src.extensions.{extension}")
                await self.load_extension(f"src.extensions.{extension}")
                await self.tree.sync()
                logger.log(f"Reloaded extension {extension}.", logtype=logger.logtypes.success)
                return f"Reloaded extension {extension}."
            except Exception as e:
                logger.log(f"Failed to reload extension {extension}. - {e}", logtype=logger.logtypes.error)
                return f"Failed to reload extension {extension}. - {e}"

    async def setup_hook(self) -> None:
        await self.load_extension("src.extensions.utilities")
        await self.load_extension("src.extensions.settings")
        await self.load_extension("src.extensions.moderation")
        await self.load_extension("src.extensions.logging")
        await self.load_extension("src.extensions.events")
        await self.load_extension("src.extensions.tickets")
        # DEVELOPER COMMANDS #
        await self.load_extension("src.extensions.developer")
        await self.tree.sync()




    async def on_ready(self):
        status_type, status = data.read("guild")[0][1].split("0DATA_TYPE_SPLIT0")
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(type=int(status_type), name=status, ))
        logger.log(f"Connected.", logtype=logger.logtypes.success)


def start(application_id):
    bot = BOT(application_id)
    logger.log("Booting...", logtype=logger.logtypes.info)
    bot.run(token, reconnect=True, log_level=0)


if __name__ == "__main__":
    print("DO NOT RUN THIS FILE. RUN MAIN.PY INSTEAD.")

# AUTHOR: python#0001 | https://github.com/pythonserious
