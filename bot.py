from asyncio.windows_events import NULL
import os
import random
import discord

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

#Stores current bot settings
class settings:
    doKeywordRespond = True

#Keyword holds a specific phrase that the bot will respond too if it is in the message from another user
#Will only respond if doKeywordRespond is true
class keyword:
    #phrase to respond when seen in chat
    name = ""
    #list of responses to choose from
    responses = ["Lovely choice of vocabulary",
		"Wow that is really interesting",
		"I like this guy",
		"Whatever you said, I agree!"]

    # constructor
    def __init__(self,val):
        # initializing instance variable
        self.name = val

botSettings = settings()
#Initially start with keyword 'moist'
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

    #when 2 args are passed, range is between them
    if len(args) == 2:
        upper = int(args[1])
        lower = int(args[0])
    #when 1 arg is passed, range is between arg and 0
    elif len(args) == 1:
        upper = int(args[0])

    #lower cannot be greater than upper
    if (lower > upper):
        hold = lower
        lower = upper
        upper = hold

    #respond with a random number between the bounds 
    response = random.randrange(lower,upper)
    await ctx.send(response)

#Command settings allows users with administrator roles to change the settings of the bot
@bot.command(name='settings')
async def set_bot_settings(ctx, *args):
    #only allow admins to make changes to bot settings
    if (ctx.message.author.guild_permissions.administrator == False):
        ctx.send("You must have admin privallages to change bot settings")
    
    #!settings keyword_respond {True/False}
    if ((len(args) == 2)and(args[0] == "keyword_respond")):
        try:
            set_keyword_response(args[1])
        except ValueError as e:
            await ctx.send(e)
    else:
        #On invalid arguement, print the possible allowed arguements
        await print_settings_options(ctx)

#Command keyword allows users to add, remove and edit the keywords the bot responds to
@bot.command(name='keyword')
async def keyword_command(ctx, *args):
    #!keyword add {list of strings}
    if ((len(args) > 2)and(args[0] == "add")):
        await add_keyword(ctx, args[1:])
    #!keyword remove {list of strings}
    elif ((len(args) > 2)and(args[0] == "remove")):
        await remove_keyword(ctx, args[1:])
    else:
        #On invalid arguement, print the possible allowed arguements
        await print_keyword_options(ctx)

#Add a list of keywords that the bot will respond to
async def add_keyword(ctx, args):
    global keywords
    #added holds all the keywords that were added to the bot
    added = []

    if len(args) == 0:
        await ctx.send("You must provide at least one keyword to add")

    #for each keyword passed
    for item in args:
        #If there is not already a keyword with the same name
        if is_keyword(item) == False:
            #Add it
            keywords.append(keyword(str(item)))
            added.append(str(item))
        else:
            await ctx.send("Keyword " + str(item) + " already exists")

    #if new keywords were added, print them to the user
    if len(added) >0:
        await ctx.send("Succesfully added keywords: " + ' '.join(added))

#Remove a set of keywords from the bot
async def remove_keyword(ctx, args):
    global keywords
    #removed holds the keywords that were successfully removed
    removed = []

    if len(args) == 0:
        await ctx.send("You must provide at least one keyword to remove")

    #for each keyword passed
    for item in args:
        #If the keyword exists in the bot
        if is_keyword(item) == True:
            #Remove it
            keywords.remove(get_keyword(item))
            removed.append(str(item))
        else:
            await ctx.send("Keyword " + str(item) + " does not exist")

    #if keywords were removed, print them to the user
    if len(removed) > 0:
        await ctx.send("Succesfully removed keywords: " + ' '.join(removed))

#Called whenever a message is entered into chat
@bot.event
async def on_message(message):
    #If the bot sent the message, ignore it
    if message.author == bot.user:
        return

    #process bot commands before responding to keywords
    await bot.process_commands(message)

    #ingore comamnd that contain the '!' as they are commands
    #Do not respond if doKeywordRespond is false
    if ((message.content.startswith('!')) or (botSettings.doKeywordRespond ==  False)):
        return
        
    response = ""

    global keywords
    #for each keyword in the bot
    for item in keywords:
        print(item.name)
        #if the message contains the keyword
        if item.name in message.content.lower():
            #pick a response and break
            response = random.choice(item.responses)
            break

    #if no response was found, return
    if (response == ""):
        return
    
    #send the response to the chat
    await message.channel.send(response)
    
#Set whether the bot should respond to keywords in chat
def set_keyword_response(val: str):
    global botSettings
    if (val.lower == "true"):
        botSettings.doKeywordRespond == True
    elif (val.lower == "false"):
        botSettings.doKeywordRespond == False
    else:
        raise ValueError("Parameter must be 'true' or 'false'")

#send into chat the parameters for the !settings commmand
async def print_settings_options(ctx):
    await ctx.send("""
    Valid arguements are:
    keyword_respond (true/false)  -Sets whether the bot responds to set keywords being in a message
    """)

#send into chat the parameters for the !options command
async def print_keyword_options(ctx):
    await ctx.send("""
    Valid arguements are:
    add (words)    -Adds a set of words as keyphrases that the bot will respond to
    remove (words)    -Removes a set of keyphrases
    """)

#Return true if a given string is the name of a keyword
def is_keyword(keyword: str):
    global keywords
    for item in keywords:
        if item.name == keyword:
            return True
    return False

#Get the istance of a keyword with a given name
def get_keyword(keyword: str):
    global keywords
    for item in keywords:
        if item.name == keyword:
            return item
    return NULL

#Run the bot
bot.run(TOKEN)
