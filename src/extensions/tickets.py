# TICKET SYSTEM #
import asyncio
import io
import sys
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, button
from src.utils.permissions import permissions_check
import src.utils.logger as logger
import src.utils.data as data
import chat_exporter


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("src/storage/ticket_message.txt", "r", encoding="utf8") as f:
            self.default_message = str(f.read())

    class ticketCreate(View):
        def __init__(self):
            self.welcome = "A staff member will be with you shortly to assist you."
            super().__init__(timeout=None)

        @button(label="Open Ticket", style=discord.ButtonStyle.primary, emoji="📩")
        async def openTicket(self, interaction: discord.Interaction, buttonIN: discord.ui.Button):
            if buttonIN:
                pass
            if data.exists("tickets", str(interaction.user.id), "user"):
                return await interaction.response.send_message(f":x: You already have an open ticket.", ephemeral=True)
            else:
                await interaction.response.defer()
                parent_config = data.read("tickets", "CONFIG", "parent")
                parent_category = await interaction.client.fetch_channel(int(parent_config[0]))
                ticket_id = parent_config[1]
                ticket = await interaction.guild.create_text_channel(f"ticket-{int(ticket_id) + 1}",
                                                                     category=parent_category)
                role = discord.utils.get(interaction.guild.roles, name="@everyone")
                await ticket.set_permissions(role, send_messages=False, read_messages=False, add_reactions=False,
                                             embed_links=False, attach_files=False, read_message_history=False,
                                             external_emojis=False)
                await ticket.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True, attach_files=True,
                                             read_message_history=True, external_emojis=True)
                welcome = discord.Embed(colour=discord.Colour.green(), description=self.welcome)
                welcome.set_footer(text="ID: " + str(interaction.user.id), icon_url=interaction.client.user.avatar.url)
                msg = await ticket.send(content=f"Greetings, {interaction.user.mention}", embed=welcome)
                data.write("tickets",
                           [str(interaction.user.id), str(int(ticket_id) + 1), "open", str(ticket.id),
                            str(msg.id)])
                data.update("tickets", "tid", str(int(ticket_id) + 1), "parent", "'CONFIG'", False)

    @app_commands.command(name="setup", description="Setup the ticket system.")
    async def setup(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            # Check for existing ticket system.
            status = data.exists("tickets", "CONFIG", "parent")
            if status:
                return await interaction.response.send_message(f":x: I detected an existing config.", ephemeral=True)
            ticket_category = category
            if ticket_category is None:
                return await interaction.response.send_message(f":x: I could not find the category.", ephemeral=True)
            # Create the ticket system.
            await interaction.response.send_message(f"⚠️ Building...")
            embed = discord.Embed(colour=discord.Colour.green(), description=self.default_message)
            parent_message = await interaction.channel.send(embed=embed, view=self.ticketCreate())
            data.write("tickets", [ticket_category.id, 0, interaction.channel.id, "CONFIG", parent_message.id])
            await interaction.edit_original_response(content=f":white_check_mark: Ticket system has been setup.")

        else:
            await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                    ephemeral=True)

    @app_commands.command(name="close", description="Closes the ticket.")
    async def close(self, interaction: discord.Interaction):
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if data.exists("tickets", str(interaction.channel.id), "parent"):
                ticket_data = data.read("tickets", str(interaction.channel.id), "parent")
                print(ticket_data)
                ticket_owner = await interaction.client.fetch_user(int(ticket_data[0]))
                data.update("tickets", "status", "'closed'", "user", str(interaction.user.id), False)
                await interaction.channel.set_permissions(ticket_owner, send_messages=False, read_messages=False,
                                                          add_reactions=False, embed_links=False, attach_files=False,
                                                          read_message_history=False, external_emojis=False)
                await interaction.response.send_message(content=f":white_check_mark: Ticket has been closed.")
            else:
                await interaction.response.send_message(content=f":x: No ticket data found for this channel.")
        else:
            await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                    ephemeral=True)

    @app_commands.command(name="re-open", description="Re-opens the ticket.")
    async def re_open(self, interaction: discord.Interaction):
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if data.exists("tickets", str(interaction.channel.id), "parent"):
                ticket_data = data.read("tickets", str(interaction.channel.id), "parent")
                ticket_owner = await interaction.client.fetch_user(int(ticket_data[0]))
                data.update("tickets", "status", "'open'", "user", str(interaction.user.id), False)
                await interaction.channel.set_permissions(ticket_owner, send_messages=True, read_messages=True,
                                                          add_reactions=True, embed_links=True, attach_files=True,
                                                          read_message_history=True, external_emojis=True)
                await interaction.response.send_message(content=f":white_check_mark: Ticket has been re-opened.")
            else:
                await interaction.response.send_message(content=f":x: No ticket data found for this channel.")
        else:
            await interaction.response.send_message(f":x: You do not have permission to use this command.",
                                                    ephemeral=True)

    @app_commands.command(name="delete", description="Deletes the ticket.")
    async def delete(self, interaction: discord.Interaction, send_transcript: bool):
        if permissions_check(interaction, sys._getframe().f_code.co_name):
            if "ticket-" in interaction.channel.name:
                pass
            else:
                return await interaction.response.send_message(f":x: This is not a ticket.")
            await interaction.response.defer()
            messages = [message async for message in interaction.channel.history(limit=None)]
            user_mentions = []
            for msg in messages:
                if msg.author.mention in user_mentions:
                    continue
                user_mentions.append(msg.author.mention)
            query = "\n".join(user_mentions)
            pre_tr = discord.Embed(color=0x1b893b,
                                   description=f"Saving transcript...")
            ticket_data = data.read("tickets", str(interaction.channel.id), "parent")
            try:
                ticket_owner = await interaction.client.fetch_user(int(ticket_data[0]))
            except:
                ticket_owner = None
            if ticket_owner is None or ticket_data is None:
                await interaction.channel.send(f":x: No ticket data found. Deleting...")
                await interaction.channel.delete()

            need_edit = await interaction.channel.send(embed=pre_tr)
            transcript = await chat_exporter.export(interaction.channel)
            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                           filename=f"transcript-{interaction.channel.name}.html")
            action_log = data.read("guild")[0][2]
            if action_log == "":
                return
            channel = await self.bot.fetch_channel(int(action_log))
            transcript_log = await self.bot.fetch_channel(int(action_log))

            msg = await transcript_log.send(file=transcript_file)
            embed = discord.Embed(color=0x1b893b)
            embed.add_field(name="Ticket Owner", value=ticket_owner.mention)
            embed.add_field(name="Ticket Name", value=interaction.channel.name)
            url = msg.attachments[0].url
            embed.add_field(name=f"Direct Transcript",
                            value=f"[Direct Transcript](https://tickets.pythn.tech?turl={url})", inline=False)
            embed.add_field(name="Users in transcript", value=query)
            embed.set_author(
                icon_url="https://cdn.discordapp.com/embed/avatars/1.png" if ticket_owner.avatar is None else ticket_owner.avatar.url,
                name=f"{ticket_owner.name}#{ticket_owner.discriminator}")
            embed2 = discord.Embed(color=0x1b893b,
                                   description=f"Transcript saved!")
            await channel.send(embed=embed)
            await need_edit.edit(embed=embed2)
            deleted_embed = discord.Embed(color=0xa33b3b,
                                          description="<:no:825954081624555552> Ticket will be deleted shortly.")
            await interaction.channel.send(embed=deleted_embed)
            await asyncio.sleep(0.2)
            data.delete("tickets", "user", str(ticket_owner.id))
            await interaction.channel.delete()
            try:
                await ticket_owner.send(
                    f"Your ticket has been deleted.\n\n"
                    f"{'' if not send_transcript else f'You can view your transcript here: https://tickets.pythn.tech?turl={url}'}")
            except:
                pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ticket(bot))
    if data.exists("tickets", "CONFIG", "parent"):
        config_data = data.read("tickets", "CONFIG", "parent")
        message_channel = await bot.fetch_channel(int(config_data[2]))
        message = await message_channel.fetch_message(int(config_data[4]))
        await message.edit(view=Ticket.ticketCreate())
        return logger.log("Ticket System Online - Hooked Interaction.", logger.logtypes.info)

    else:
        return logger.log("Ticket System Online - Not Setup.", logger.logtypes.info)
