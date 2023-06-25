import voltage
from voltage.ext import commands
import sqlite3

conn = sqlite3.connect('database.db')

def obtainProfileByPrefix(prefix):
    sanitized = prefix.split()[0]
    cursor = conn.execute('SELECT name, imageurl, prefix FROM profiles WHERE prefix = ?', (sanitized,))
    profile = cursor.fetchone()
    return profile


def setup(client) -> commands.Cog:
    profiles = commands.Cog(
        'Profiles',
        'Profiles management.'
    )

    @profiles.command('createnew', 'Create a new profile')
    async def createnew(ctx: commands.CommandContext, name: str, *, imageurl: str, prefix: str):
        user_id = ctx.author.id
        if not name.startswith('"'):
            await ctx.reply(f'The name must be enclosed in quotation marks (for example: "Johnny John").')
            return

        name = name.strip('"')
        prefix = prefix.replace(" ", "", 1)
        

        # Check if profile with same name or prefix already exist
        cursor = conn.execute('SELECT * FROM profiles WHERE user_id = ? AND (name = ? OR prefix = ?)', (user_id, name, prefix))
        existsing_profile = cursor.fetchone()
        if existsing_profile:
            await ctx.reply(f'A profile with the same name or prefix already exists.')
            return

        cursor = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if cursor.fetchone() is None:
            try:
                conn.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
            except sqlite3.Error as error:
                print('ERR: ', error)
                return
            conn.commit()
            print(f"User was registered in the database.")

        conn.execute('INSERT INTO profiles (user_id, name, imageurl, prefix) VALUES (?, ?, ?, ?)',
                     (user_id, name, imageurl, prefix))

        conn.commit()
        print('Profile created successfully.')
        await ctx.reply(f'Profile created successfully! You can start using it writing `{prefix}` at the start of any message.')
    
    
    @profiles.command('deleteprofile', 'Deletes an existing profile')
    async def deleteprofile(ctx: commands.CommandContext, profileName: str):
        userid = ctx.author.id
        try:
            cursor = conn.execute('SELECT * FROM profiles WHERE name = ?', (profileName,))
            profile = cursor.fetchone()

            if profile is None:
                await ctx.reply("That profile doesn't exist.")
            else:
                conn.execute('DELETE FROM profiles WHERE name = ?', (profileName,))
                conn.commit()
                await ctx.reply(f'Profile deleted successfully.')

        except sqlite3.Error as error:
            print('ERR: ', error)

    @profiles.command('listprofiles', 'List all of your profiles')
    async def listprofiles(ctx: commands.CommandContext):
        user_id = ctx.author.id
        try:
            cursor = conn.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
            userProfiles = cursor.fetchall()

            response = "Your profiles:\n"
            for profile in userProfiles:
                response += f'"{profile[2]}", with prefix "`{profile[4]}`"\n'
            await ctx.reply(response)
        
        except sqlite3.Error as error:
            print('ERR: ', error)
    
    @profiles.listen('message')
    async def profileMessage(message):
        if message.author.id == client.user.id:
            return
        
        content = message.content
        profile = obtainProfileByPrefix(content)

        if profile is not None:
            await message.delete()
            messageRemainder = content[len(profile[2])+1:]
            await message.channel.send(messageRemainder, masquerade=voltage.MessageMasquerade(profile[0], profile[1]))
            
    return profiles