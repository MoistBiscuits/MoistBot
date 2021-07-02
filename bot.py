from asyncio.windows_events import NULL
import os
import random
import discord
import re
import xml.etree.ElementTree as ET
from discord.message import PartialMessage

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
    print(args)
    #!keyword add {list of strings}
    if ((len(args) > 1)and(args[0] == 'add')):
        await add_keyword(ctx, args[1:])
    #!keyword remove {list of strings}
    elif ((len(args) > 1)and(args[0] == 'remove')):
        await remove_keyword(ctx, args[1:])
    #!keyword clear {list of strings}
    elif ((len(args) > 1)and(args[0] == 'clear')):
        await clear_keyword(ctx, args[1:])
    elif ((len(args) > 1)and(args[0] == 'edit')):
        await edit_keyword(ctx, args[1:])
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
            parse_add_keyword(keyword(str(item)))
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
            parse_remove_keyword(get_keyword(item))
            removed.append(str(item))
        else:
            await ctx.send("Keyword " + str(item) + " does not exist")

    #if keywords were removed, print them to the user
    if len(removed) > 0:
        await ctx.send("Succesfully removed keywords: " + ' '.join(removed))

#Removes all phrases associated with a set of keywords
async def clear_keyword(ctx, args):
    #list of cleared keywords
    cleared=[]

    if len(args) == 0:
        await ctx.send("You must provide at least one keyword to clear")

    #for each keyword passed
    for item in args:
        #If the keyword exists in the bot
        if is_keyword(item) == True:
            #Clear it
            get_keyword(item).responses = []
            parse_remove_keyword(get_keyword(item))
            parse_add_keyword(get_keyword(item))
            cleared.append(str(item))
        else:
            await ctx.send("Keyword " + str(item) + " does not exist")

    #if keywords were cleared, print them to the user
    if len(cleared) > 0:
        await ctx.send("Succesfully cleared phrases of keywords: " + ' '.join(cleared))

#Command tree for editing keywords
async def edit_keyword(ctx, args):
    #!keyword edit add {keyword} {phrase}
    if ((len(args) > 1)and(args[0] == 'add')):
        await add_keyphrase(ctx, args[1:])
    #!keyword edit remove {keyword} {phrase}
    elif ((len(args) > 1)and(args[0] == 'remove')):
        await remove_keyphrase(ctx, args[1:])
    else:
        await print_edit_options(ctx)

#Adds a new phrase to a keyword
async def add_keyphrase(ctx, args):
    global keywords

    if (len(args) < 2):
        await ctx.send("You must provide a keyword and a response to add to it")
        return
    
    if (len(args) > 2):
        await ctx.send('Too many arguements, expected (keyword) "(phrase)"')
        return
    
    keyword = args[0]

    if (is_keyword(keyword) == True):
        keyword = get_keyword(keyword)
    else:
        await ctx.send("Keyword " + keyword + " does not exist")
        return

    #discord library groups agurements encased in quotes so we dont have to
    phrase = args[1]

    if (phrase == ''):
        await ctx.send("Could not add phrase: " + str(args[1]))
    else:
        #Add phrase
        keyword.responses.append(phrase)
        parse_remove_keyword(keyword)
        parse_add_keyword(keyword)
        await ctx.send("Added phrase: " + phrase)

#remove a keyphrase from a keyword
async def remove_keyphrase(ctx, args):
    global keywords

    if (len(args) < 2):
        await ctx.send("You must provide a keyword and a response to remove")
        return
    
    if (len(args) > 2):
        await ctx.send('Too many arguements, expected (keyword) "(phrase)"')
        return
    
    keyword = args[0]

    if (is_keyword(keyword) == True):
        keyword = get_keyword(keyword)
    else:
        await ctx.send("Keyword " + keyword + " does not exist")
        return

    #discord library groups agurements encased in quotes so we dont have to
    phrase = args[1]
    
    for response in keyword.responses:
        #if the phrase is a response
        if (phrase == str(response)):
            #remove it and return
            keyword.responses.remove(response)
            parse_remove_keyword(keyword)
            parse_add_keyword(keyword)
            await ctx.send("Removed phrase succesfully")
            return
    
    #if phrase is not found
    ctx.send("Response does not exist in keyword: " + keyword.name)



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
        if (item.name in message.content.lower()) and (item.responses != []):
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
    add (words)    -Adds a set of words as keywords that the bot will respond to
    remove (words)    -Removes a set of keywords
    clear (words)    -Clears all responses of a given set of keywords
    edit (params)    -Edit an existing keyword     
    """)

#send into chat the paramters for !keyword edit command
async def print_edit_options(ctx):
    await ctx.send("""
    Valid arguements are:
    add (keyword) (text)    -Add a phrase to a keyword
    remove (keyword) (text)    -Remove a phrase from a keyword
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

#Load keywords from xml file
def load_keywords(filename):
    global keywords

    file = open(filename)
    tree = ET.parse(file)
    root = tree.getroot()
    for child in root.findall('keyword'):
        word = keyword(child.get('name'))
        word.responses = []
        for phrase in child.find('phrases').findall('phrase'):
            word.responses.append(phrase.text)

        keywords.append(word)

#Save a keyword to the xml file
def parse_add_keyword(word: keyword):
    global filename
    #open xml
    file = open(filename)
    tree = ET.parse(file)
    root = tree.getroot()

    #create new child keyword
    new=ET.SubElement(root,'keyword')
    new.set('name', word.name)

    #give it a phrases child node
    phrases=ET.SubElement(new,'phrases')

    #fill it with the phrases of the keyword
    for item in word.responses:
        phrase=ET.SubElement(phrases,'phrase')
        phrase.text=item
    
    tree.write(filename)
        
#remove a keyword from the xml file
def parse_remove_keyword(word: keyword):
    global filename
    #open xml
    file = open(filename)
    tree = ET.parse(file)
    root = tree.getroot()

    #find and remove keyword
    for node in root.findall('keyword'):
        if node.get('name') == word.name:
            root.remove(node)
            break
    
    tree.write(filename)



#Init bot settings
botSettings = settings()
keywords = []
print(os.getcwd())
path = "C:/Users/Aqeel Little/Documents/Python projects/discord bot/MoistBot"
os.chdir(path)
filename = 'data.xml'
load_keywords(filename)

#Run the bot
bot.run(TOKEN)
