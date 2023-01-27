# LOGGER #
import discord
import termcolor
import requests
import datetime
from src.storage.config import debug, webhook
import src.utils.data as data


class logtypes:
    info = ["INFO", "cyan", 0x327FBA]
    warning = ["WARNING", "yellow", 0xab7209]
    error = ["ERROR", "red", 0xe32e33]
    success = ["SUCCESS", "green", 0x158c06]
    debug = ["DEBUG", "magenta", 0x562687]
    boot = ["BOOT", "blue", 0x04075e]


async def action_log(message, title, user: discord.User | discord.Member, color, interaction: discord.Interaction, mod=False):
    action_logs, mod_logs = data.read("guild")[0][2:4]
    if action_logs == "" and mod is False:
        return
    elif mod_logs == "" and mod is True:
        return
    channel = await interaction.client.fetch_channel(int(action_logs) if not mod else int(mod_logs))
    embed = discord.Embed(color=color[2], title=title, description=message, timestamp=datetime.datetime.now())
    embed.set_author(name=f"{user.name}#{user.discriminator}",
                     icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if user.avatar is None else user.avatar.url)
    await channel.send(embed=embed)


def log(message, logtype, mdtype=None):
    if debug is False and logtype[0] == "DEBUG":
        return
    print("[ " + termcolor.colored(logtype[0], logtype[1]) + " ]" + " - " + message + " - " + str(
        datetime.datetime.now().strftime("%Y-%m-%d @ %H:%M:%S")))
    embed = {
        "embeds": [
            {
                "title": logtype[0],
                "description": f"```{mdtype}\n{message}```",
                "color": logtype[2],
                "timestamp": str(datetime.datetime.now().isoformat("T")) + "Z"
            }
        ]
    }
    if webhook:
        requests.post(webhook, json=embed)


if debug:
    log("DEBUG MODE IS ENABLED", logtypes.debug)
