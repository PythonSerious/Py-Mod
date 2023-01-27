import json

import src.utils.data as data
import discord


def get_roles():
    guild_data = data.read("guild")[0]
    mod_roles = guild_data[4].split(",")
    admin_roles = guild_data[5].split(", ")
    return [mod_roles, admin_roles]


def command(name: str):
    with open("src/storage/config.json", "r") as f:
        config_file = json.load(f)
    for cog in config_file["commands"]:
        if config_file["commands"][cog].get(name):
            if not config_file["commands"][cog].get(name)["enabled"]:
                return True
    return False


def permissions_check(interaction: discord.Interaction, name: str):
    moderator = False
    admin = False
    owner = False
    with open("src/storage/config.json", "r") as f:
        config_file = json.load(f)
    for cog in config_file["commands"]:
        if config_file["commands"][cog].get(name):
            permission = config_file["commands"][cog].get(name)["permission"]
            if permission == "moderator":
                moderator = True
            elif permission == "admin":
                admin = True
            elif permission == "owner":
                owner = True

    if moderator is False and admin is False and owner is False:
        return True

    mod_roles, admin_roles = get_roles()
    mod = False
    user_admin = False
    for role in interaction.user.roles:
        if str(role.id) in mod_roles:
            print("User is moderator.")
            mod = True
            break
        elif str(role.id) in admin_roles:
            print("Admin")
            user_admin = True
            break

    if interaction.guild.owner_id == interaction.user.id:
        # Guild owner has all permissions.
        return True
    if moderator == mod or moderator == user_admin and not moderator is False:
        # If the user is a moderator or an admin, return True.
        return
    if admin == user_admin and not admin is False:
        # If the user is an admin and the permission is admin, return True.
        return True
    else:
        # User does not have the required permissions.
        return False


def u_vs_u_permission(interaction: discord.Interaction, user: discord.Member, moderator: bool = False,
                      admin: bool = False, owner: bool = False):
    mod_roles, admin_roles = get_roles()
    level = 0

    vs_level = 0

    if interaction.guild.owner_id == interaction.user.id:
        return True

    for role in interaction.user.roles:
        if str(role.id) in mod_roles:
            level = 1
            break
        elif str(role.id) in admin_roles:
            level = 2
            break

    for role in user.roles:
        if str(role.id) in mod_roles:
            vs_level = 1
            break
        elif str(role.id) in admin_roles:
            vs_level = 2
            break

    if vs_level >= level:
        return False
    else:
        return True
