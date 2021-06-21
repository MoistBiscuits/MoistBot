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
    doKeywordRespond = True

class keyword:
    name = ""
    responses = ["Lovely choice of vocabulary",
		"Wow that is really interesting",
		"I like this guy",
		"Whatever you said, I agree!"]

    # constructor
    def __init__(self,val):
        # initializing instance variable
        self.name = val

botSettings = settings()
keywords = [keyword("moist")]

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
    
    if ((len(args) == 2)and(args[0] == "keyword_respond")):
        try:
            set_keyword_response(args[1])
        except ValueError as e:
            await ctx.send(e)
    else:
        await print_settings_options(ctx)

@bot.command(name='add')
async def add_keyword(ctx, *args):
    global keywords
    added = [""]

    if len(args) == 0:
        await ctx.send("You must provide at least one keyword to add")

    for item in args:
        if is_keyword(item) == False:
            keywords.append(keyword(item))
            added.append(item)
        else:
            await ctx.send("Keyword " + item + " already exists")

    await ctx.send("Succesfully addes keywords:" + ' '.join(added))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    #ingore comamnd that contain keyphrase
    if ((message.content.startswith('!')) or (botSettings.doKeywordRespond ==  False)):
        return
        
    response = ""

    global keywords
    for item in keywords:
        print(item.name)
        if item.name in message.content.lower():
            response = random.choice(item.responses)
            break

    if (response == ""):
        return
    
    await message.channel.send(response)
    
   

def set_keyword_response(val: str):
    global botSettings
    if (val.lower == "true"):
        botSettings.doKeywordRespond == True
    elif (val.lower == "false"):
        botSettings.doKeywordRespond == False
    else:
        raise ValueError("Parameter must be 'true' or 'false'")

async def print_settings_options(ctx):
    await ctx.send("""
    Valid arguements are:
    keyword_respond (true/false)  -Sets whether the bot responds to set keywords being in a message
    """)

def is_keyword(keyword: str):
    global keywords
    for item in keywords:
        if item.name == keyword:
            return True
    return False


bot.run(TOKEN)
