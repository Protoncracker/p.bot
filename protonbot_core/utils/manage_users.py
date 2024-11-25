from aiofiles import open as aiopen
global admins, trusted_users

async def manage_users(action, user_type=None, user=None):
    global admins, trusted_users
    if action == 'save' and user and user_type:
        try:
            file_name = 'admins.txt' if user_type == 'admin' else 'trusted_users.txt'
            async with aiopen(file_name, 'a') as file:
                await file.write(user + '\n')
            return True
        except Exception as e:
            return str(e)
    elif action == 'load' and user_type:
        users = []
        try:
            file_name = 'admins.txt' if user_type == 'admin' else 'trusted_users.txt'
            async with aiopen(file_name, 'r') as file:
                async for line in file:
                    users.append(line.strip())
            return users
        except Exception as e:
            return []
    else:
        return []