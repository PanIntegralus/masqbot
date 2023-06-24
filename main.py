import voltage
from voltage.ext import commands
import os
import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    name TEXT,
    imageurl TEXT,
    prefix TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

conn.close()

REVOLT_TOKEN = os.environ.get('REVOLT_TOKEN')
PREFIX = os.environ.get('PREFIX')

client = commands.CommandsClient(PREFIX)

@client.error('message')
async def on_error(error: Exception, message: voltage.Message):
    if isinstance(error, voltage.CommandNotFound):
        return await message.reply("That command doesn't exist.")

    if isinstance(error, voltage.NotEnoughArgs):
        return await message.reply("Insufficient arguments provided.")

    if isinstance(error, voltage.NotBotOwner):
        return await message.reply("That is a bot owner only command.")

    if isinstance(error, voltage.NotEnoughPerms):
        return await message.reply("You do not have enough permissions to do that...")

@client.listen('ready')
async def on_ready():
    client.add_extension('cogs.profiles')

client.run(REVOLT_TOKEN)