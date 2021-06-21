import os
import random
import discord

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

class settings:
    doMoistRespond = True

botSettings = settings()

#Gives a rabdom number between 2 given values
#If only 1 arguement is passed, from 0 to X
#if none, from 0 to 10
@bot.command(name='random')
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

@bot.command(name='settings')
async def set_bot_settings(ctx, *args):
    if (ctx.message.author.guild_permissions.administrator == False):
        ctx.send("You must have admin privallages to change bot settings")
    
    if ((len(args) == 2)and(args[0] == "moist_respond")):
        try:
            set_moist_response(args[1])
        except ValueError as e:
            ctx.send(e)
    else:
        await print_settings_options(ctx)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await message.channel.send(response)

    #ingore comamnd that contain keyphrase
    if message.content.startswith('!'):
        return

    moist_responses = ["Lovely choice of vocabulary",
		"Wow that is really interesting",
		"I like this guy",
		"Whatever you said, I agree!"]

    if (('moist' in message.content.lower()) & (botSettings.doMoistRespond)):
        response = random.choice(moist_responses)
	
    

def set_moist_response(val: str):
    global botSettings
    if (val.lower == "true"):
        botSettings.doMoistRespond == True
    elif (val.lower == "false"):
        botSettings.doMoistRespond == False
    else:
        raise ValueError("Parameter must be 'true' or 'false'")

async def print_settings_options(ctx):
    await ctx.send("""
    Valid arguements are:
    moist_respond (true/false)  -Sets whether the bot responds to 'moist' being in a message
    """)


bot.run(TOKEN)
