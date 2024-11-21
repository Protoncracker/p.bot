import discord, os, asyncio, aiofiles, base64
from discord.ext import commands
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
os.environ['PYTHONDONTWRITEBYTECODE'] = '1' # Unable pycache (development only)

load_dotenv()
encrypted_token = os.getenv('ENCRYPTED_TOKEN')

def decrypt_token(encrypted_token, password):
    data = base64.urlsafe_b64decode(encrypted_token.encode())
    salt, iv, tag, ciphertext = data[:16], data[16:28], data[28:44], data[44:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    decrypted_token = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_token.decode()

permissions_integer = 1759110961823591

intents = discord.Intents.default()
intents.value = permissions_integer

class PCBots(commands.AutoShardedBot):
    global watching
    watching = []
    log_file = None

    def __init__(self, **options):
        super().__init__(command_prefix=None, intents=intents, shard_count=4, **options)

    def load_admins(self):
        global admins
        admins = []
        with open('admins.txt', 'r') as file:
            for line in file:
                admins.append(line.strip())
        return admins
    
    def load_trustedUsers(self):
        global trusted_users
        trusted_users = []
        with open('trusted_users.txt', 'r') as file:
            for line in file:
                trusted_users.append(line.strip())
        return trusted_users

    async def log(self, content_log, ismf=False):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f'{timestamp} {content_log}' #if ismf == False else log_message = f'{timestamp} '
        print(log_message)

        if PCBots.log_file is None:
            PCBots.open_log_file()

        PCBots.log_file.write(log_message + '\n')
        PCBots.log_file.flush()  # Ensure that the log is written to the file immediately

    async def save_admin(self, who):
        global admins
        admins = []
        try:
            with open('admins.txt', 'a') as file:
                file.write(who+'\n')
            return True
        except Exception as e:
            return e

    async def log_latency(self):
        while not self.is_closed():
            await self.log(f'Heartbeat latency: {round(self.latency * 1000, 2)}ms')
            await asyncio.sleep(60)  # Loga a latência a cada 60 segundos


    @staticmethod
    def open_log_file():
        if not os.path.exists('logs'):
            os.makedirs('logs')
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_path = f'logs/{current_date}.txt'
        PCBots.log_file = open(file_path, 'a')

    @staticmethod
    def close_log_file():
        if PCBots.log_file is not None:
            PCBots.log_file.close()
            PCBots.log_file = None

    async def on_ready(self):
        await self.log(f'Logged on as {self.user}')
        self.loop.create_task(self.log_latency())

    async def on_disconnect(self):
        await self.log('Disconnecting...')
        PCBots.close_log_file()

    async def get_userid(self, tagline):
        user = discord.utils.get(self.get_all_members(), name=tagline.split('#')[0], discriminator=tagline.split('#')[1])
        if user:
            return f'<@{user.id}>'
        return 'User not found'

    async def on_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        author = await self.get_userid(message.author.name + "#" + message.author.discriminator)
        admins = self.load_admins()
        trusted_users = self.load_trustedUsers() + admins

        # If in watchlist:
        if author in watching:
            if message.content.startswith('>deafen'):
                watching.remove(author)
                await self.log(f'{self.user} is now deafen to {message.author}.') # type: ignore
                await message.channel.send(f'Otori, {message.author.mention}. Te vejo mais tarde.')

            if author in admins:
                if message.content:
                    command = message.content.split()[0] # grab command tree
                else:
                    command = "null"
                match command:
                    case 'd.userid': # Displays user id
                        user = message.content.split()[1]
                        if '#' in message.content:
                            userid = await self.get_userid(message.content.split()[1])
                            if userid == 'User not found':
                                await message.channel.send(f'Usuário {message.content.split()[1]} não encontrado.')
                            else:
                                await message.channel.send(f'`{userid}`')
                        else:
                            await message.channel.send(f'Nome de usuário inválido. Há uma tagline?')

                        
                    case '>checkf':
                        await self.log('Checkfunction')
                    case '>add_admin':
                        user = message.content.split()[1]
                        result = 0
                        if user.startswith ('<@'):
                            result = await self.save_admin(f'{message.content.split()[1]}')
                            if result == True:
                                await message.channel.send(f'Novo admin adicionado: {message.content.split()[1]}.')
                                await self.log(f'New admin added: {message.content.split()[1]}')
                            else:
                                await message.channel.send(f'Erro ao adicionar admin.')
                                await self.log(result)
                        else:
                            if '#' in message.content:
                                userid = await self.get_userid(message.content.split()[1])
                                if userid != 'User not found':
                                    result = await self.save_admin(f'{userid}')
                                    if result == True:
                                        await message.channel.send(f'Novo admin adicionado: {userid}')
                                        await self.log(f'New admin added: {userid}')
                                    else:
                                        await message.channel.send(f'Erro ao adicionar admin.')
                                        await self.log(result)
                                else:
                                    await message.channel.send(f'Usuário {message.content.split()[1]} não encontrado.')
                                    await self.log(result)
                            else:
                                await message.channel.send(f'Nome de usuário inválido. Há uma tagline?')
                                await self.log(result)

        if author in watching:
            await self.log(f'{message.author} is being heard. He says: {message.content}')

        if author in trusted_users:
            if message.content:
                command = message.content.split()[0] # grab command tree
            else:
                command = "null"
            match command: #search for command tree
                case '>nul':
                        await message.channel.send('.')
                        await message.channel.send(f'Shard ID: {message.guild.shard_id}\nTotal Shards: {self.shard_count}')
                case '>listen':
                    watching.append(author)
                    await self.log(f'Started to listen to {message.author}.')
                    await message.channel.send(f'Íthala, {message.author.mention}. Estou te ouvindo.')

    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="Espectador")
        if role:
            await member.add_roles(role)
            await self.log(f'Assigned role {role.name} to <@{member.id}>: "{member.name}"')
        else:
            await self.log(f'Role {role} not found in the server')


print ("If you don't know the password to run this bot, please get your token and encrypt using the encrypt_token.py script.")
password = input("Enter the password to decrypt the token: ")
try:
    token = decrypt_token(encrypted_token, password)
    client = PCBots()
    client.run(token)
except Exception as e:
    print("Failed to decrypt the token. Please check your password and try again.")


