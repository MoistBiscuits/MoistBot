import os
import random

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

<<<<<<< HEAD
#Gives a rabdom number between 2 given values
#If only 1 arguement is passed, from 0 to X
#if none, from 0 to 10
@bot.command(name='random', help='Gives a random number between 2 values')
async def random_number(ctx, *args):
    lower = 0
    upper = 10

    if len(args) > 2:
        ctx.send("Invalid number of arguements, expected 0 to 2")
        return

    for val in args:
        if (val.isdecimal == False):
            ctx.send("Arguements must be postive integers")
            return


    if len(args) == 2:
        upper = int(args[1])
        lower = int(args[0])
    elif len(args) == 1:
        upper = int(args[0])

    response = random.randrange(lower,upper)
    await ctx.send(response)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

=======
@bot.command(name='random')
async def nine_nine(ctx):
    response = random.randrange(0,10)
    await ctx.send(response)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

>>>>>>> 8ddff542a4d7c9c5d44c19ba103ab165e36755e9
    moist_responses = ["Lovely choice of vocabulary",
		"Wow that is really interesting",
		"I like this guy",
		"Whatever you said, I agree!"]

    if 'moist' in message.content.lower():
        response = random.choice(moist_responses)
        await message.channel.send(response)
	
    await bot.process_commands(message)

bot.run(TOKEN)
