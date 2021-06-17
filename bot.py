# bot.py
import os

import discord
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    moist_responses = ["Lovely choice of vocabulary",
		"Wow that is really interesting",
		"I like this guy",
		"Whatever you said, I agree!"]

    if 'moist' in message.content.lower():
        response = random.choice(moist_responses)
        await message.channel.send(response)

client.run(TOKEN)
