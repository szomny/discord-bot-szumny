import discord
from discord import app_commands
from discord.ext import tasks
from discord import Interaction

import asyncio
import datetime
from colorama import Fore, Style

import os
import aiohttp

import requests

# ---------{ ROLES }----------

PERKS_ROLE_ID = 1353744571074609165


# ---------{ YOUTUBE }----------

YOUTUBE_API_KEY = None
YOUTUBE_CHANNEL_ID = None
NOTIFY_YT_CHANNEL_ID = None

# ---------{ VERIFICATION }----------

NOT_VER_ROLE_ID = None
VER_ROLE_ID = None

# ---------{ RULE }----------

RULE_MESSAGE_ID = None
SIGMA_ROLE_ID = None

# ---------{ SELFROLES }----------

MAN_BOY_ROLE_ID = None
WOMAN_GIRL_ROLE_ID = None

RED_ROLE_ID = None
ORANGE_ROLE_ID = None
WHITE_ROLE_ID = None
BLACK_ROLE_ID = None
BLUE_ROLE_ID = None
GREEN_ROLE_ID = None
PURPLE_ROLE_ID = None

# ---------{ TICKETS }----------

TICKET_ROLE_ID = None

# ---------{ CHANNELS }----------


LOBBY_CHANNEL_ID = None


# ---------{ CATEGORIES }----------

TICKET_CATEGORY_ID = None


# ---------{ DATE AND TIME }----------

def aktualna_data_i_godzina():
    return datetime.datetime.now().strftime(f"{Style.BRIGHT}%Y-%m-%d %H:%M:%S")

# ---------{ BOT }----------


class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()

        intents.guilds = True
        intents.guild_messages = True
        intents.message_content = True
        intents.members = True
        intents.reactions = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

        self.player_count = 0

        self.status_index = 0

    async def on_ready(self):
        print(f"{Style.DIM}{aktualna_data_i_godzina()}{Style.NORMAL} | {Fore.GREEN}{Style.BRIGHT}Online{Fore.WHITE}, {self.user}{Style.DIM} Made by {Style.BRIGHT}szomny{Style.NORMAL}")
        
        # check_youtube.start()

        self.add_view(ButtonVer())
        self.add_view(TicketButton())
        self.add_view(CloseTicketButton())
        self.add_view(SelfRole())

        self.loop.create_task(self.pr())

        try:
            komendy = await self.tree.sync()
            print(f"{Style.DIM}{aktualna_data_i_godzina()}{Style.NORMAL} | {Fore.GREEN}{Style.BRIGHT}{len(komendy)} Commands connected!{Fore.WHITE}")

        except Exception as e:
            print(f"{Fore.RED}Błąd synchronizacji komend: {e}")


    async def fetch_roblox_data(self):

        url = "https://games.roblox.com/v1/games?universeIds=7312815635"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "data" in data and len(data["data"]) > 0:
                        self.player_count = data["data"][0].get("playing", 0)

    async def pr(self):

        await self.fetch_roblox_data() 

        self.status_index = 1 

        while True:
            if self.status_index == 1:
                activity = discord.Game(name=f"{self.player_count} players in GAME! 🎮")
            elif self.status_index == 2:
                activity = discord.Activity(type=discord.ActivityType.listening, name="© 2025 szomny")
            elif self.status_index == 3:
                activity = discord.Game(name=f"{self.player_count} players in GAME! 🎮")
            else:
                activity = discord.Activity(type=discord.ActivityType.listening, name="© 2025 szomny")

            await self.change_presence(activity=activity)

            self.status_index = (self.status_index % 4) + 1

            if self.status_index == 1:
                await self.fetch_roblox_data()

            await asyncio.sleep(20)



bot = Bot()





latest_video_id = None


async def get_latest_video():

    url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={NOTIFY_YT_CHANNEL_ID}&part=snippet,id&order=date&maxResults=1"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    if "items" in data:

        video = data["items"][0]

        if video["id"]["kind"] == "youtube#video":

            video_id = video["id"]["videoId"]

            title = video["snippet"]["title"]

            thumbnail_url = video["snippet"]["thumbnails"]["high"]["url"]

            published_at = video["snippet"]["publishedAt"]
            

            dt = datetime.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            timestamp = int(dt.timestamp())
            
            return video_id, title, thumbnail_url, timestamp
    return None, None, None, None


@tasks.loop(minutes=1)
async def check_youtube():

    global latest_video_id
    
    video_id, title, thumbnail_url, timestamp = await get_latest_video()
    
    if video_id and video_id != latest_video_id:

        latest_video_id = video_id

        url = f"https://www.youtube.com/watch?v={video_id}"
        
        embed = discord.Embed(
            title=f"🎥 | New video available on YouTube! (click me)",
            url=url,
            description=f"**New video:** {title}",
            color=discord.Color.red()
        )

        embed.set_footer(text="© 2025 szomny")
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name="📅 Published on:", value=f"<t:{timestamp}:F>")  # Formatowana data publikacji
        embed.timestamp = datetime.datetime.now(datetime.UTC)
        
        channel = bot.get_channel(NOTIFY_YT_CHANNEL_ID)

        if channel:
            await channel.send(embed=embed)

# ---------{ EVENTY }----------



# ---------{ LOBBY }----------


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild

    not_ver_role = guild.get_role(NOT_VER_ROLE_ID)

    lobby_channel = guild.get_channel(LOBBY_CHANNEL_ID)

    await member.add_roles(not_ver_role)
    await lobby_channel.send(f"👋 {member.mention} Welcome to {guild.name} server! There are already {guild.member_count} members.")


# ---------{ REAKCJA POD REGULAMINEM }----------


@bot.event
async def on_raw_reaction_add(payload):

    if payload.message_id == RULE_MESSAGE_ID and payload.emoji.name == "✅":

        guild = bot.get_guild(payload.guild_id)

        member = guild.get_member(payload.user_id)

        if member and not member.bot:

            sigma_role = guild.get_role(SIGMA_ROLE_ID)

            if sigma_role and sigma_role not in member.roles:

                await member.add_roles(sigma_role)

                try:
                    await member.send(f"{member.mention} You are now {sigma_role.name}!")
                except discord.Forbidden:
                    print(f"Nie mogę wysłać wiadomości do {member.name}, ponieważ zablokował bota.")



# ---------{ KOMENDY }----------


# ---------{ PING }----------

@bot.tree.command(name="ping", description="Bot Ping.")
async def ping(interaction: Interaction):

    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! 🏓 \nPing: {latency}ms")


# ---------{ WERYFIKACJA (ONLY OWNER) }----------


# ---------{ button }----------

class ButtonVer(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="| Verify", style=discord.ButtonStyle.success, emoji="✅",custom_id="verify_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild

        ver_role = guild.get_role(VER_ROLE_ID)
        not_ver_role = guild.get_role(NOT_VER_ROLE_ID)

        user = interaction.user

        if not_ver_role in user.roles:
            await user.remove_roles(not_ver_role)
            await user.add_roles(ver_role)
            await interaction.response.send_message("✅ | You are now <@&1352696368908472422>!", ephemeral=True)
        else:
            await user.remove_roles(ver_role)
            await user.add_roles(not_ver_role)
            await interaction.response.send_message("🆕 | You are now <@&1352695030455865425>!", ephemeral=True)

# ---------{ main }----------

@bot.tree.command(name="verification")
async def verification(interaction: Interaction):

    app_owner = (await bot.application_info()).owner

    if interaction.user == app_owner:
        kolor = int("248045", 16) # zielony

        title = "✅ | Verification"
        description = "Press button 🔽 to verify yourself!"

        embed = discord.Embed(title=title,description=description,color=kolor)
        embed.set_footer(text="© 2025 szomny")
        channel = interaction.channel
        await channel.send(embed=embed,view=ButtonVer())
    else:
        await interaction.response.send_message("❌ | You can't use this command!",ephemeral=True)




    
# ---------{ TICKETY (ONLY OWNER) }---------- 

# ---------{ buttony }----------
class CloseTicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="| Close", style=discord.ButtonStyle.success, emoji="✖️",custom_id="close_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        channel = interaction.channel

        ticket_role = guild.get_role(1353049323767730197)

        channel_name_parts = channel.name.split('-')
        user_id = int(channel_name_parts[2])
        user = guild.get_member(user_id)

        try:
            await user.remove_roles(ticket_role)
            await channel.delete()

        except Exception as e:
            print(f"{Fore.RED}Błąd: {e}")


class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, emoji="➕",custom_id="ticket_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild

        ticket_role = guild.get_role(TICKET_ROLE_ID)
        ticket_category = guild.get_channel(TICKET_CATEGORY_ID)

        user = interaction.user

        if not ticket_role in user.roles:
            await user.add_roles(ticket_role)

            overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Domyślnie wszyscy nie mają dostępu
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True,read_message_history=True,attach_files=True)  # Użytkownik ma dostęp do kanału
            }

            title=f"Welcome {user.name}!"
            description="Present us your problem as accurately as you can. You can also send files on this channel."

            embed = discord.Embed(title=title,description=description,color=discord.Color.blue())
            embed.set_footer(text="© 2025 szomny")


            new_channel = await guild.create_text_channel(name=f"{user.name}-ticket-{user.id}",category=ticket_category,slowmode_delay=1,overwrites=overwrites)

            await new_channel.send(embed=embed,view=CloseTicketButton())

            await interaction.response.send_message(f"🎫 | Ticket: {new_channel.mention}!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ | You already have a ticket!", ephemeral=True)

# ---------{ main }----------

@bot.tree.command(name="tickets")
async def tickets(interaction: Interaction):

    app_owner = (await bot.application_info()).owner

    if interaction.user == app_owner:
        title = "🎫 | Ticket"
        description = "Press button 🔽 to create ticket!"

        kolor = int("5865f2", 16) # niebieski

        embed = discord.Embed(title=title,description=description,color=kolor)
        embed.set_footer(text="© 2025 szomny")
        channel = interaction.channel
        await channel.send(embed=embed,view=TicketButton())
    else:
        await interaction.response.send_message("❌ | You can't use this command!",ephemeral=True)


# ---------{ EMBED }----------

# ---------{ main }----------

@bot.tree.command(name="embed", description="Tworzy embeda (HEX format koloru: ff0000 dla czerwonego)")
async def embed(interaction: Interaction, tytul: str, opis: str, kolor: str):
    try:
        kolor_int = int(kolor, 16)

        embed = discord.Embed(title=tytul, description=opis, color=kolor_int)
        embed.set_footer(text="© 2025 szomny")

        await interaction.response.send_message(embed=embed)
    except ValueError:
        await interaction.response.send_message("❌ Błędny format koloru! Użyj np. `ff0000` dla czerwonego.", ephemeral=True)


# ---------{ SELFROLE (ONLY OWNER) }----------

# ---------{ menu }----------

class SelfRole(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
            
        placeholder="Choose a roles ...",

        min_values=1,
        max_values=1,

        options=[
            discord.SelectOption(label="Man/Boy", emoji="👨"),
            discord.SelectOption(label="Woman/Girl", emoji="👩"),
            discord.SelectOption(label="Red", emoji="🟥"),
            discord.SelectOption(label="Orange", emoji="🟧"),
            discord.SelectOption(label="White", emoji="⬜"),
            discord.SelectOption(label="Black", emoji="⬛"),
            discord.SelectOption(label="Blue", emoji="🟦"),
            discord.SelectOption(label="Green", emoji="🟩"),
            discord.SelectOption(label="Purple", emoji="🟪"),
        ],
        
        custom_id="selfrole"
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        guild = interaction.guild
        user = interaction.user


        role_map = {

            "Man/Boy": guild.get_role(MAN_BOY_ROLE_ID),
            "Woman/Girl": guild.get_role(WOMAN_GIRL_ROLE_ID),
            "Red": guild.get_role(RED_ROLE_ID),
            "Orange": guild.get_role(ORANGE_ROLE_ID),
            "White": guild.get_role(WHITE_ROLE_ID),
            "Black": guild.get_role(BLACK_ROLE_ID),
            "Blue": guild.get_role(BLUE_ROLE_ID),
            "Green": guild.get_role(GREEN_ROLE_ID),
            "Purple": guild.get_role(PURPLE_ROLE_ID),

        }

        selected_role = role_map.get(select.values[0])

        if not selected_role in user.roles:

            await user.add_roles(selected_role)
            await interaction.response.send_message(f"✅ | Added: {selected_role.mention}!", ephemeral=True)
        else:

            await user.remove_roles(selected_role)
            await interaction.response.send_message(f"❌ | Removed: {selected_role.mention}!", ephemeral=True)

# ---------{ main }----------

@bot.tree.command(name="selfrole")
async def selfrole(interaction: discord.Interaction):
    
    app_owner = (await bot.application_info()).owner

    if interaction.user == app_owner:

        embed = discord.Embed(title="🔮 | Selfrole", description="Press menu 🔽 to choose roles!", color=discord.Color.gold())
        channel = interaction.channel
        await channel.send(embed=embed, view=SelfRole())
    else:
        await interaction.response.send_message("❌ | You can't use this command!")


# ---------{ RULES (ONLY OWNER)}----------

# ---------{ main }----------

@bot.tree.command(name="rules")
async def rules(interaction: discord.Interaction):

    kolor = int("ffffff", 16)  # biały

    with open("rules.txt", "r", encoding="utf-8") as file:
        rules_text = file.read()


    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = int(now.timestamp())

    app_owner = (await bot.application_info()).owner

    if interaction.user == app_owner:

        embed = discord.Embed(title="Szomny Studio Server Regulations", description=rules_text, color=kolor)
        embed.set_footer(text="It is forbidden to copy these regulations!\n© 2025 szomny, Rules © 2025 fanatykherbaty")
        embed.add_field(name="📅 Last update:", value=f"<t:{timestamp}:F>")

        message = await interaction.channel.send(embed=embed)

        await message.add_reaction("✅")

    else:
        await interaction.response.send_message("❌ | You can't use this command!", ephemeral=True)

# ---------{ UPDATE RULES (ADMINS)}----------

@bot.tree.command(name="update-rules")
async def update_rules(interaction: discord.Interaction):

    admin_role = interaction.guild.get_role(PERKS_ROLE_ID)

    kolor = int("ffffff", 16)  # biały

    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = int(now.timestamp())

    with open("rules.txt", "r", encoding="utf-8") as file:
        rules_text = file.read()

    if admin_role in interaction.user.roles:

        channel = interaction.channel

        try:
            message = await channel.fetch_message(RULE_MESSAGE_ID)

            new_embed = discord.Embed(title="Szomny Studio Server Regulations", description=rules_text, color=kolor)
            new_embed.set_footer(text="It is forbidden to copy these regulations!\n© 2025 szomny, Rules © 2025 fanatykherbaty")
            new_embed.add_field(name="📅 Last update:", value=f"<t:{timestamp}:F>")

            await message.edit(embed=new_embed)

        except discord.NotFound:
            print("nie znaleziono wiadomosci")
    else:
        await interaction.response.send_message(f"❌ | You don't have {admin_role.mention}!",ephemeral=True)
            
# ---------{ HELP ADMIN }----------

@bot.tree.command(name="help")
async def help_admin(interaction: discord.Interaction):

    admin_role = interaction.guild.get_role(PERKS_ROLE_ID)

    if not admin_role in interaction.user.roles:

        kolor = int("ffffff", 16)  # biały

        with open("commands.txt", "r", encoding="utf-8") as file:
            commands_text = file.read()

        embed = discord.Embed(
            title="📲 | Here are the commands:",
            description=commands_text,
            color=kolor
        )
        embed.set_footer(text="© 2025 szomny")

        return await interaction.response.send_message(embed=embed,ephemeral=True)

    else:

        with open("commands.txt", "r", encoding="utf-8") as file:
            commands_text = file.read()

        with open("admin-commands.txt", "r", encoding="utf-8") as file:
            admin_commands_text = file.read()

        embed = discord.Embed(
            title="⭐ | Here are the commands:",
            description=admin_commands_text+"\n\n📲** | And basic commands:**\n\n"+commands_text,
            color=discord.Color.gold()
        )
        embed.set_footer(text="© 2025 szomny")

        return await interaction.response.send_message(embed=embed,ephemeral=True)





bot.run(YOUR BOT TOKEN)
