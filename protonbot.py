# ------------------- MODULES -------------------
from datetime import datetime
start_time = datetime.now()  # Start timer
import discord, os, sys, signal
from aiofiles import open as aiopen
from json import loads
from discord.ext import commands
from dotenv import load_dotenv
from protonbot_core.utils import *
from getpass import getpass
import logging
import ctypes
from colorama import init, Fore, Style, Back

# Initialize colorama for Windows
init()

# Configure logging to only show errors
logging.getLogger('discord').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)
logging.getLogger('discord.client').setLevel(logging.ERROR)
logging.getLogger('discord').disabled = True
# -----------------------------------------------


# ------------ CORE INITIALIZATION --------------
global BOT, USERS, load_time

# Load bot configuration from JSON file
with open('protonbot_core/database/bot.json', 'r') as file:
    content = file.read()
    BOT = loads(content)

def signal_handler(sig, frame):
    """
    Handle SIGINT signal.
    """
    print('Otori! Goodbye.')
    print('User interrupted the process.')
    sys.exit(0)

# Disable pycache (development only)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Load environment variables from .env file
load_dotenv()
encrypted_token = os.getenv('ENCRYPTED_TOKEN')

# Set Discord intents to all
intents = discord.Intents.all()

# Calculate load time
end_time = datetime.now()
load_time = (end_time - start_time).total_seconds()
# -----------------------------------------------


# --------------------- BOT ---------------------
class ProtonBot(commands.AutoShardedBot):
    """
    A class representing the ProtonBot, a Discord bot using the discord.py library.
    Inherits from commands.AutoShardedBot.
    """

    def display_banner(self):
        """
        Displays a banner with bot information in the console.
        """
        environment = "Production" if self.BOT['is_production'] == "True" else "Development"
        banner = f"""{Fore.CYAN}
        ╔═══════════════════════════════════════════╗
        ║  ██████╗ ██████╗  ██████╗ ████████╗ ██████╗ ███╗   ██╗  
        ║  ██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗████╗  ██║  
        ║  ██████╔╝██████╔╝██║   ██║   ██║   ██║   ██║██╔██╗ ██║  
        ║  ██╔═══╝ ██╔══██╗██║   ██║   ██║   ██║   ██║██║╚██╗██║  
        ║  ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║  
        ║  ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝  
        ╚═══════════════════════════════════════════╝
        {Style.BRIGHT}     Discord Bot Framework v{self.BOT['version']} ({environment}){Style.RESET_ALL}
        {Fore.YELLOW}     \033[4m{self.BOT['name']}\033[0m{Style.RESET_ALL}
        {Fore.GREEN}     Developed by {self.BOT['author']}{Style.RESET_ALL}
        {Fore.BLUE}     GitHub: \033[4m{self.BOT['github']}\033[0m{Style.RESET_ALL}
        """
        print(banner)

    def __init__(self, **options):
        """
        Initializes the ProtonBot instance.
        """
        start_time = datetime.now()
        super().__init__(command_prefix=None, intents=intents, shard_count=1, **options)
        self.load_time = load_time + (datetime.now() - start_time).total_seconds()
        self.BOT, self.USERS = BOT, {}
        self.shard_id = None
        self.display_banner()

    async def log(self, content, type="INFO", hearbeat=None):
        """
        Logs messages with different types and colors.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        match type:
            case "ERROR":
                type_colored = f"{Back.RED}{Fore.BLACK}{type}{Style.RESET_ALL}{Back.RED}"
                content = f"{Back.RED}{timestamp} [{type_colored}] {content}{Style.RESET_ALL}"
            case "WARNING":
                type_colored = f"{Fore.YELLOW}{type}{Style.RESET_ALL}"
                content = f"{timestamp} {Style.RESET_ALL}[{type_colored}] {content}"
            case "SYSTEM":
                type_colored = f"{Fore.GREEN}{type}{Style.RESET_ALL}"
                content = f"{timestamp} {Style.RESET_ALL}[{type_colored}] {content}"
            case "LOGIN":
                type_colored = f"{Fore.BLUE}{type}{Style.RESET_ALL}"
                content = f"{timestamp} {Style.RESET_ALL}[{type_colored}] {content}"
            case "INFO":
                type_colored = f"{Fore.LIGHTBLACK_EX}{type}{Style.RESET_ALL}"
                content = f"{timestamp} {Style.RESET_ALL}[{type_colored}] {content}"
            case "DEBUG":
                type_colored = f"{Fore.CYAN}{type}{Style.RESET_ALL}"
                content = f"{timestamp} {Style.RESET_ALL}[{type_colored}] {content}"
            case _:
                content = f"{timestamp} [{type}] {content}"
        print(content)

    async def on_shard_ready(self, shard_id):
        """
        Event handler for when a shard is ready.
        """
        self.shard_id = shard_id
        if shard_id == 0:
            self.start_time = datetime.now()
        await self.log(f'{self.BOT["name"]} shard {shard_id} is ready', 'SYSTEM')

    async def on_ready(self):
        """
        Event handler for when the bot is ready.
        """
        self.load_time = self.load_time + (datetime.now() - self.start_time).total_seconds()
        await startup(self, self.load_time)
        await self.log(f'{self.BOT["name"]} is ready', 'SYSTEM')
        await self.log(f'ERROR test', 'ERROR')
        await self.log(f'WARNING test', 'WARNING')
        await self.log(f'INFO test', 'INFO')
        await self.log(f'SYSTEM test', 'SYSTEM')

    async def on_command_error(self, context, exception):
        """
        Event handler for command errors.
        """
        return await super().on_command_error(context, exception)

    async def on_reconnect(self):
        """
        Event handler for when the bot reconnects.
        """
        try:
            shard_id = self.shard_id if self.shard_id is not None else 'Unknown'
            await self.log(f'{self.BOT["name"]} shard {shard_id} has reconnected', 'SYSTEM')
        except Exception as e:
            await self.log(f'Error during reconnect:', 'ERROR')

    async def on_disconnect(self):
        """
        Event handler for when the bot disconnects.
        """
        try:
            shard_id = self.shard_id if self.shard_id is not None else 'Unknown'
            await self.log(f'{self.BOT["name"]} shard {shard_id} has disconnected', 'SYSTEM')
        except Exception as e:
            await self.log(f'Error during disconnect:', 'ERROR')

    async def on_resumed(self):
        """
        Event handler for when the bot resumes.
        """
        try:
            shard_id = self.shard_id if self.shard_id is not None else 'Unknown'
            await self.log(f'{self.BOT["name"]} shard {shard_id} has resumed', 'SYSTEM')
        except Exception as e:
            await self.log(f'Error during resume:', 'ERROR')

    async def on_message(self, message):
        """
        Event handler for when a message is received.
        """
        author = "<@" + str(message.author.id) + ">"

        if message.author.bot:
            return
        
        if not message.content == '':
            if author not in self.USERS["admins"]:
                if author not in self.USERS["vips"]:
                    return
                return
            await command(self, message, discord)

    async def on_message_edit(self, before, after):
        """
        Event handler for when a message is edited.
        """
        if before.author.bot:
            return
        return

    async def on_message_delete(self, message):
        """
        Event handler for when a message is deleted.
        """
        if message.author.bot:
            return
        return
    
    async def on_raw_message_edit(self, payload):
        """
        Event handler for when a raw message is edited.
        """
        return
    
    async def on_raw_message_delete(self, payload):
        """
        Event handler for when a raw message is deleted.
        """
        return
    
    async def on_raw_reaction_add(self, payload):
        """
        Event handler for when a raw reaction is added.
        """
        return
    
    async def on_raw_reaction_remove(self, payload):
        """
        Event handler for when a raw reaction is removed.
        """
        return
    
    async def on_raw_reaction_clear(self, payload):
        """
        Event handler for when raw reactions are cleared.
        """
        return
    
    async def on_raw_reaction_clear_emoji(self, payload):
        """
        Event handler for when a raw reaction emoji is cleared.
        """
        return
    
    async def on_raw_bulk_message_delete(self, payload):
        """
        Event handler for when bulk messages are deleted.
        """
        return
    
    async def on_member_join(self, member):
        """
        Event handler for when a member joins the server.
        """
        role = discord.utils.get(member.guild.roles, name='Espectador')
        if role:
            await member.add_roles(role)
            await self.log(f'{member} has joined the server and was given the role "Espectador"')
        else:
            await self.log(f'{member} has joined the server but the role "Espectador" was not found', 'WARNING')
        return
    
    async def on_member_remove(self, member):
        """
        Event handler for when a member leaves the server.
        """
        return
    
    async def on_member_update(self, before, after):
        """
        Event handler for when a member is updated.
        """
        return
    
    async def on_user_update(self, before, after):
        """
        Event handler for when a user is updated.
        """
        return
    
    async def on_guild_join(self, guild):
        """
        Event handler for when the bot joins a guild.
        """
        return
    
    async def on_guild_remove(self, guild):
        """
        Event handler for when the bot leaves a guild.
        """
        return
    
    async def on_guild_update(self, before, after):
        """
        Event handler for when a guild is updated.
        """
        return
    
    async def on_guild_role_create(self, role):
        """
        Event handler for when a guild role is created.
        """
        return
    
    async def on_guild_role_delete(self, role):
        """
        Event handler for when a guild role is deleted.
        """
        return
    
    async def on_guild_role_update(self, before, after):
        """
        Event handler for when a guild role is updated.
        """
        return
    
    async def on_guild_emojis_update(self, guild, before, after):
        """
        Event handler for when guild emojis are updated.
        """
        return
    
    async def on_guild_channel_create(self, channel):
        """
        Event handler for when a guild channel is created.
        """
        return
    
    async def on_guild_channel_delete(self, channel):
        """
        Event handler for when a guild channel is deleted.
        """
        return
    
    async def on_guild_channel_update(self, before, after):
        """
        Event handler for when a guild channel is updated.
        """
        return
    
    async def on_guild_channel_pins_update(self, channel, last_pin):
        """
        Event handler for when guild channel pins are updated.
        """
        return
    
    async def on_guild_integrations_update(self, guild):
        """
        Event handler for when guild integrations are updated.
        """
        return
    
    async def on_webhooks_update(self, channel):
        """
        Event handler for when webhooks are updated.
        """
        return
    
    async def on_invite_create(self, invite):
        """
        Event handler for when an invite is created.
        """
        return
    
    async def on_invite_delete(self, invite):
        """
        Event handler for when an invite is deleted.
        """
        return
    
    async def on_group_join(self, channel, user):
        """
        Event handler for when a user joins a group.
        """
        return
    
    async def on_group_remove(self, channel, user):
        """
        Event handler for when a user leaves a group.
        """
        return
    
    async def on_relationship_add(self, relationship):
        """
        Event handler for when a relationship is added.
        """
        return
    
    async def on_relationship_remove(self, relationship):
        """
        Event handler for when a relationship is removed.
        """
        return
    
    async def on_relationship_update(self, before, after):
        """
        Event handler for when a relationship is updated.
        """
        return
    
    async def on_application_command_create(self, command):
        """
        Event handler for when an application command is created.
        """
        return
    
    async def on_application_command_update(self, before, after):
        """
        Event handler for when an application command is updated.
        """
        return
    
    async def on_application_command_delete(self, command):
        """
        Event handler for when an application command is deleted.
        """
        return
    
    async def on_application_command_error(self, context, exception):
        """
        Event handler for application command errors.
        """
        return
    
    async def on_application_command(self, context):
        """
        Event handler for when an application command is executed.
        """
        return
    
    async def on_interaction_create(self, interaction):
        """
        Event handler for when an interaction is created.
        """
        return
    
    async def on_interaction_update(self, before, after):
        """
        Event handler for when an interaction is updated.
        """
        return
    
    async def on_interaction_delete(self, interaction):
        """
        Event handler for when an interaction is deleted.
        """
        return
    
    async def on_socket_raw_receive(self, msg):
        """
        Event handler for when a raw socket message is received.
        """
        return
    
    async def on_socket_raw_send(self, payload):
        """
        Event handler for when a raw socket message is sent.
        """
        return
    
    async def on_typing(self, channel, user, when):
        """
        Event handler for when a user starts typing.
        """
        return
    
    async def on_message_create(self, message):
        """
        Event handler for when a message is created.
        """
        return
    
    async def on_message_update(self, before, after):
        """
        Event handler for when a message is updated.
        """
        return
    
    async def on_message_delete(self, message):
        """
        Event handler for when a message is deleted.
        """
        return
    
    async def on_message_delete_bulk(self, messages):
        """
        Event handler for when bulk messages are deleted.
        """
        return
    
    async def on_message_reaction_add(self, reaction, user):
        """
        Event handler for when a reaction is added to a message.
        """
        return
    
    async def on_message_reaction_remove(self, reaction, user):
        """
        Event handler for when a reaction is removed from a message.
        """
        return
    
    async def on_message_reaction_clear(self, message, reactions):
        """
        Event handler for when reactions are cleared from a message.
        """
        return
    
    async def on_message_reaction_clear_emoji(self, reaction):
        """
        Event handler for when a reaction emoji is cleared from a message.
        """
        return

# -----------------------------------------------

def set_window_properties():
    """
    Sets the window properties for the console.
    """
    if sys.platform == 'win32':
        # Set window title
        ctypes.windll.kernel32.SetConsoleTitleW("ProtonBot Discord")

# ------------- SCRIPT ENTRY POINT --------------
if __name__ == '__main__':
    # Set window properties
    set_window_properties()
    signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv) > 1:
        # Use first argument as password
        password = sys.argv[1]
    else:
        try:
            print("If you don't know the password to run this bot, please get your token and encrypt using the encrypt_token.py script.")
            password = getpass("Enter the password to decrypt the token: ")
            if not password:
                print("Password cannot be empty.\n")
                sys.exit(0)
            os.system('cls' if os.name == 'nt' else 'clear')
        except KeyboardInterrupt:
            print('Otori! Goodbye.')
            sys.exit(0)
try:
    token = decrypt_token(encrypted_token, password)
    client = ProtonBot()
    client.run(token)
except Exception as e:
    if str(e) == '':
        print('Failed to decrypt the token. Please check your password and try again.')
    else:
        print(f'An exception occurred: {e}')
# -----------------------------------------------