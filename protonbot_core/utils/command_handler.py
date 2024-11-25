from .get_userid import get_userid

async def handle(bot, command, message=None, discord=None):
    """Handle commands"""
    await bot.log('Handling command', 'DEBUG')
    command_parts = command.split()
    padded_command = [word[:50] for word in command_parts]
    
    tree = str(command_parts[0]) if len(command_parts) > 0 else None
    branch = str(command_parts[1]) if len(command_parts) > 1 else None
    leaf = str(command_parts[2]) if len(command_parts) > 2 else None
    await bot.log(f'Command: {command_parts}', 'DEBUG')
    
    match tree.lower():
        case 'd': # Discord commands
            match branch.lower():
                case 'userid':
                    print('Leaf: userid')
                    if not leaf:
                        await message.reply('Please provide a username.')
                        return
                    try:
                        username = leaf
                        if username and username.startswith('<@'):
                            username = username[2:-1]
                            if username.isdigit():
                                if message:
                                    await message.reply(f'User ID: {username}')
                                    return
                            else:
                                await message.reply('Invalid user ID')
                                return
                        else:
                            userid = await get_userid(bot, username, discord)
                            await message.reply(f'User ID: {userid}') if userid else await message.reply('User not found')
                            return
                    except Exception as e:
                        await bot.log(f'Failed to get user ID: {e}', 'ERROR')
                        await message.reply('Failed to get user ID.')
                        return
    

async def command(bot, message, discord):
    """Handle incoming messages"""
    author = "<@" + str(message.author.id) + ">"
    channel_id = message.channel.id
    authorized = bot.USERS["admins"] + bot.USERS["vips"]
    print(bot.watchlist)

    if message.content.startswith('>'):
        if message.content.startswith('>listen'):
            if channel_id not in bot.watchlist:
                bot.watchlist[channel_id] = []
            if author not in bot.watchlist[channel_id]:
                await bot.log(f'{author} added to watchlist in channel {channel_id}')
                bot.watchlist[channel_id].append(author)
                await message.reply(f'Íthala, {author}. Estou te ouvindo.')
                return
            else:
                await bot.log(f'{author} already on listen in channel {channel_id}.')
                await message.reply(f'Em posição esperando comando.')
                return
        elif message.content.startswith('>deafen'):
            if channel_id in bot.watchlist and author in bot.watchlist[channel_id]:
                await bot.log(f'{author} removed from watchlist in channel {channel_id}')
                bot.watchlist[channel_id].remove(author)
                if not bot.watchlist[channel_id]:
                    del bot.watchlist[channel_id]
                await message.reply(f'Otori, {author}. Até mais tarde.')
                return
            else:
                await bot.log(f'{author} already off listen in channel {channel_id}.')
                await message.reply('Já estou descansando.')
                return

    if channel_id in bot.watchlist and author in bot.watchlist[channel_id]:
        if author in bot.USERS["admins"]:
            await handle(bot, message.content, message, discord)
            return
        elif author in bot.USERS["vips"]:
            None
            #await handle_minor(bot, message, discord)
            return
        else:
            await message.reply('Acesso negado.')
            return
