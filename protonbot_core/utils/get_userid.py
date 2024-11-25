async def get_userid(bot, username, discord):
    """Get user ID from username"""
    user = discord.utils.get(bot.get_all_members(), name=username, discriminator='0')
    return user.id if user else None