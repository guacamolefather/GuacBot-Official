from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.ext import bridge, commands, tasks # Discord.py commands and tasks
from itertools import cycle # For cycling through statuses
import discord, time, os, random # Standard libraries


intents = discord.Intents.all() # Intents for the bot
bot = discord.ext.bridge.Bot(command_prefix = '$', intents=intents, help_command=None, case_insensitive=True, activity=discord.Game("Only legends see this.")) # Bot object with default prefix and activity


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@bot.event
async def on_ready(): # Tells OS the bot is ready, refreshes the json with server data, and starts the status and animation loops
    print("Main bot processes active.")
    RefreshServerData(bot)
    change_status.start()
    animation.start()

@bot.event
async def on_guild_join(guild): # Refreshes the server data when the bot joins a server
    RefreshServerData(bot)
    channel = await bot.get_channel(1206496203768860693)
    await channel.send(f"Joined a new server! {guild}") # Send the notification to the bot's audit log channel

@bot.event
async def on_guild_remove(guild): # Refreshes the server data when the bot leaves a server
    RefreshServerData(bot)
    channel = await bot.get_channel(1206496203768860693)
    await channel.send(f"Left a server... {guild}") # Send the notification to the bot's audit log channel

@bot.event
async def on_command_error(ctx, error): # Error handling for commands and various fail states
    if isinstance(error, commands.CommandNotFound): # If the command isn't found, tell the user
        await ctx.respond("We don't do that anymore...")
        return
    elif isinstance(error, commands.CommandInvokeError) or isinstance(error, discord.errors.ApplicationCommandInvokeError): # If GuacBot couldn't execute a command, tell the user
        if isinstance(error.original, discord.Forbidden): # If GuacBot couldn't execute the command due to his permissions, tell the user
            await ctx.respond("I don't have the permissions to do that here...", ephemeral=True)
            return
    elif isinstance(error, commands.CheckFailure) or isinstance(error, discord.errors.CheckFailure): # If GuacBot couldn't execute the command due to the user's permissions, tell the user
        if (not await is_it_me(ctx)): # If GuacBot couldn't execute the command due to the user not being dad, tell the user
            await ctx.respond("Sorry, that command is only for dad.")
        else: # If GuacBot couldn't execute the command for any other permission reason, tell the user
            await ctx.respond("Sorry, you don't have permission to do that...")
        return
    else:
        channel = await ctx.bot.fetch_channel(1037298707705634917)
        await channel.send(f"Error {type(error)} on command ${ctx.command}: {error}") # Send the error to the bot's error channel


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MY HQ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@bot.command() # Command to display that there are no more prefix commands
async def help(ctx):
    if not ctx.author.id == 409445517509001216:
        await ctx.respond("No more prefix commands here! You are welcome to use my slash commands though :)")
    else:
        await ctx.respond("```$die\n$restart\n$refresh_server_data\n$load [cog]\n$unload [cog]\n$reload [cog]\n$change_status  [listen/watch/stream/custom/(blank for play)] [status]\n$global_blacklist [member]\n$global_unblacklist [member]\n$read_blacklist\n$locate_id [member id]\n$ping\n$wipe_brain [personality]\n$to_do [task]\n$fetch_to_do\n$patch [major/minor/misc] [info]\n$nickname [addition]```")


@bot.command(hidden=True,description="Kills me.") # Command to kill the bot
@commands.check(is_it_me) # Only dad can use this command
async def die(ctx):
    await ctx.respond("Goodbye, father.")
    await bot.change_presence(activity=discord.Game("Goodbye."))
    quit()

@bot.command(hidden=True,description="Restarts me.") # Command to restart the bot
@commands.check(is_it_me) # Only dad can use this command
async def restart(ctx):
    await ctx.respond("Restarting!", ephemeral=True)
    os.startfile(__file__)
    os._exit(1)

@bot.command(hidden=True,description="Refreshes server_data.json") # Command to refresh the server data
@commands.check(is_it_me) # Only dad can use this command
async def refresh_server_data(ctx):
    RefreshServerData(bot)
    await ctx.respond("Refreshing server data!", ephemeral=True)

@bot.command(hidden=True,description="Loads the given cog.") # Command to load a cog (case insensitive arg)
@commands.check(is_it_me) # Only dad can use this command
async def load(ctx, extension):
    try:
        extension = extension.lower()
        bot.load_extension(f'cogs.{extension}')
        await ctx.respond(f'Extension "{extension}" loaded!', ephemeral=True)
    except:
        try:
            extension = extension.lower()
            bot.load_extension(f'cogs.{extension}')
            await ctx.respond(f'Extension "{extension}" loaded!', ephemeral=True)
        except:
            await ctx.respond(f"Couldn't load {extension} extension.", ephemeral=True)

@bot.command(hidden=True,description="Unloads the given cog.") # Command to unload a cog (case insensitive arg)
@commands.check(is_it_me) # Only dad can use this command
async def unload(ctx, extension):
    try:
        extension = extension.lower()
        bot.unload_extension(f'cogs.{extension}')
        await ctx.respond(f'Extension "{extension}" unloaded!', ephemeral=True)
    except:
        try:
            extension = extension.lower()
            bot.unload_extension(f'cogs.{extension}')
            await ctx.respond(f'Extension "{extension}" unloaded!', ephemeral=True)
        except:
            await ctx.respond(f"Couldn't unload {extension} extension.", ephemeral=True)

@bot.command(hidden=True,description="Reloads the given cog.") # Command to reload a cog (case insensitive arg)
@commands.check(is_it_me) # Only dad can use this command
async def reload(ctx, extension):
    try:
        extension = extension.lower()
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.respond(f'Extension "{extension}" reloaded!', ephemeral=True)
    except:
        try:
            extension = extension.lower()
            bot.unload_extension(f'cogs.{extension}')
            bot.load_extension(f'cogs.{extension}')
            await ctx.respond(f'Extension "{extension}" reloaded!', ephemeral=True)
        except:
            await ctx.respond(f"Couldn't reload {extension} extension.", ephemeral=True)
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GENERAL HQ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        
show = bot.create_group("show", "Vanilla as heck!")
    
def time_convert(sec):
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return f"{int(hours)} hours, {int(mins)} minutes, {sec} seconds"

@show.command(description="Displays my uptime and when it was last checked!") # Slash command to display the bot's uptime and when it was last checked
async def uptime(ctx):
    time_elapsed = time.time() - botData["HQ"]["start_time"] # Calculate the time elapsed since the bot started
    time_checked = time.time() - botData["HQ"]["time_checked"] # Calculate the time elapsed since the bot's uptime was last checked
    botData["HQ"]["time_checked"] = time.time()
    UpdateBotData(botData)
    await ctx.respond(f"Uptime: {time_convert(time_elapsed)}\nLast Checked: {time_convert(time_checked)} ago.")

@show.command(description="Displays the bot's current version!") # Slash command to display the bot's current version
async def version(ctx):
    await ctx.respond(f"Current version: {guac_version}")

@show.command(description="Guac will send his link and a link to his server!") # Slash command to display the bot's invite link and support server link
async def invite(ctx):
    await ctx.respond("Link to bot: https://discord.com/api/oauth2/authorize?client_id=582337819532460063&permissions=8&scope=bot\nLink to support server: https://discord.gg/2kgZazXN68")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FINAL INITIALIZATION PROCESSES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
#Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and not filename.startswith("_"):
        bot.load_extension(f'cogs.{filename[:-3]}')

#Initialize bot data JSON file
botData = InitBotData()
guac_version = botData["HQ"]["version"] # major.minor.bugfix

#Status loop possibilities from bot data
possiblestatuses = botData["HQ"]["possible_statuses"]

def NewOrder(iterable): # Randomizes the order of an iterable object (for new status order)
    order = []
    indices = list(random.sample(range(len(iterable)), len(iterable)))
    for i in indices:
        order.append(iterable[i])
    return order

status = cycle(NewOrder(possiblestatuses))
@tasks.loop(seconds=300) # Change status every 5 minutes
async def change_status():
    newStatus = next(status)
    activityType = newStatus["type"]
    activityText = newStatus["status"]
    if activityType == "game":
        await bot.change_presence(activity=discord.Game(activityText)) # Changes the bot's status to "Playing {activityText}"
    elif activityType == "stream":
        await bot.change_presence(activity=discord.Streaming(name=activityText, url="https://www.twitch.tv/guacamolefather")) # Changes the bot's status to "Streaming {activityText}"
    elif activityType == "watch":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activityText)) # Changes the bot's status to "Watching {activityText}"
    elif activityType == "listen":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activityText)) # Changes the bot's status to "Listening to {activityText}"

# Animation cycle
animationStates = cycle(["[#                  ]", "[##                 ]", "[###                ]", "[####               ]",
                         "[#####              ]", "[######             ]", "[#######            ]", "[########           ]",
                         "[#########          ]", "[##########         ]", "[###########        ]", "[############       ]",
                         "[#############      ]", "[##############     ]", "[###############    ]", "[################   ]",
                         "[#################  ]", "[################## ]", "[###################]", "[        >:)        ]"])

@tasks.loop(seconds=1) # Updates the bot's animation frame with current time every second
async def animation():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    os.system('cls')
    print(f"{next(animationStates)}\n~ GuacBot is active ~\nThe time is: {current_time}")

# Start bot with token in json file (if avocado is present)
bot.run(Avocado())
