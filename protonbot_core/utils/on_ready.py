from aiofiles import open as aiopen  
from json import loads  
import discord  
from datetime import datetime  

global USERS, BOT

async def is_patreon():
    return False

async def load_users(bot):
    """
    Load users from the database.
    
    This function reads the users' data from a JSON file asynchronously and 
    assigns the loaded data to the bot's USERS attribute.
    
    Args:
        bot (discord.Client): The instance of the bot.
    """
    try:
        async with aiopen('protonbot_core/database/users.json', 'r') as file:
            content = await file.read()  # Asynchronously read the content of the file
            bot.USERS = loads(content)  # Load the JSON content and assign it to bot.USERS
            await bot.log('Users loaded successfully', 'SYSTEM')  # Log the successful loading of users
    except Exception as e:
        await bot.log('Failed to load users', 'ERROR')  # Log an system error if the users fail to load
        await bot.log(str(e), 'ERROR')  # Log the error message

async def morning_checkup(bot):
    """
    Assign 'Espectador' role to users without any roles.
    
    This function iterates through all guilds (servers) the bot is in, checks for the 
    'Espectador' role, and assigns it to members who have no role. The function also
    assigns the Patreon role to members who are Patreons.
    
    Args:
        bot (discord.Client): The instance of the bot.
    """
    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name='Espectador')  # Get the 'Espectador' role
        if role:
            members_without_role = [member for member in guild.members if len(member.roles) == 1]
            if members_without_role:
                for member in members_without_role:
                    if not await is_patreon():
                        await member.add_roles(role)  # Assign the 'Espectador' role to the member if not patreon
                        await bot.log(f'{member} was given the role "Espectador"')  
                    else:
                        None  # Assign the 'Patreon' role to the member if patreon
                        bot.log(f'{member} was given the role "Patreon"')
            else:
                await bot.log(f'No unmanaged members without the "Espectador" role in {guild.name}.')  # Log if no members found without the role
        else:
            await bot.log(f'Role "Espectador" not found in guild {guild.name}', 'WARNING')  # Log a warning if the role is not found

async def startup(bot, load_time):
    """
    Handle startup tasks when bot is ready.
    
    This function performs various startup tasks such as loading users, performing 
    morning checkup, and logging the startup process.
    
    Args:
        bot (discord.Client): The instance of the bot.
        load_time (float): The time taken to load the bot.
    """
    bot.watchlist = {}  # Initialize the watchlist attribute
    start_time = datetime.now()  # Record the start time of the startup tasks

    await load_users(bot)  # Load users from the database
    await morning_checkup(bot)  # Perform the morning checkup

    end_time = datetime.now()  # Record the end time of the startup tasks
    bot.load_time += (end_time - start_time).total_seconds()  # Calculate and update the total load time
    
    await bot.log(f'{bot.BOT["name"]} has connected', 'LOGIN')  # Log the bot connection
    await bot.log(f'Logged on as {bot.user}')  # Log the bot's user information
    await bot.log(f'Loaded in {load_time} seconds')  # Log the load time
    await bot.log('All startup tasks completed')  # Log the completion of all startup tasks