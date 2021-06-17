import os
import random

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name='random')
async def nine_nine(ctx):
    response = random.randrange(0,10)
    await ctx.send(response)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    moist_responses = ["Lovely choice of vocabulary",
		"Wow that is really interesting",
		"I like this guy",
		"Whatever you said, I agree!"]

    if 'moist' in message.content.lower():
        response = random.choice(moist_responses)
        await message.channel.send(response)
	
    await bot.process_commands(message)

bot.run(TOKEN)
