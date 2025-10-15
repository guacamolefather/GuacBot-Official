import discord, time, random, os, sys, subprocess

from discord.ext import bridge, commands, tasks
from itertools import cycle

from helper_classes.data import *


class HQ:
    def __init__(self):
        intents = discord.Intents.all()
        self.bot = bridge.Bot(
            command_prefix='$',
            intents=intents,
            help_command=None,
            case_insensitive=True,
            activity=discord.Game("Only legends see this.")
        )

        self.jason = Jason()
        self.bot_data = self.jason.initBotData()

        # Register handlers
        self.registerEvents()
        self.registerCommands()

        # Load cogs
        for f in os.listdir('./cogs'):
            if f.endswith('.py') and not f.startswith('_'):
                self.bot.load_extension(f'cogs.{f[:-3]}')

        default = self.bot_data["hq"]["possible_statuses"]
        randomized = random.sample(default, len(default))
        self.statuses = cycle(randomized)

        self.animation_states = cycle([
            "[#                  ]", "[##                 ]", "[###                ]", "[####               ]",
            "[#####              ]", "[######             ]", "[#######            ]", "[########           ]",
            "[#########          ]", "[##########         ]", "[###########        ]", "[############       ]",
            "[#############      ]", "[##############     ]", "[###############    ]", "[################   ]",
            "[#################  ]", "[################## ]", "[###################]", "[        >:)        ]"
        ])

        self.bot.run(self.jason.avocado())

    def registerEvents(self):
        @self.bot.event
        async def on_ready():
            print("Main bot processes active.")
            self.jason.refreshServerData(self.bot)
            self.change_status.start()
            self.animation.start()

        @self.bot.event
        async def on_guild_join(guild):
            self.jason.refreshServerData(self.bot)

        @self.bot.event
        async def on_guild_remove(guild):
            self.jason.refreshServerData(self.bot)

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.respond("We don't do that anymore...")
            elif isinstance(error, (commands.CommandInvokeError, discord.errors.ApplicationCommandInvokeError)):
                if isinstance(error.original, discord.Forbidden):
                    await ctx.respond("I don't have the permissions to do that here...", ephemeral=True)
            elif isinstance(error, (commands.CheckFailure, discord.errors.CheckFailure)):
                if not await is_it_me(ctx):
                    await ctx.respond("Sorry, that command is only for dad.")
                else:
                    await ctx.respond("Sorry, you don't have permission to do that...")
            else:
                channel = await ctx.bot.fetch_channel(1037298707705634917)
                await channel.send(f"Error {type(error)} on command ${ctx.command}: {error}")
    
    def plural(self, num, word):
        if num == 1:
            return f"{num} {word}"
        else:
            return f"{num} {word}s"

    def timeConvert(self, sec):
        sec = round(sec, 3)
        mins = 0
        hours = 0
        days = 0
        years = 0

        if sec >= 60:
            mins = int(sec // 60)
            sec = round(sec % 60, 3)
            if mins >= 60:
                hours = int(mins // 60)
                mins = mins % 60
                if hours >= 24:
                    days = int(hours // 24)
                    hours = hours % 24
                    if days >= 365:
                        years = int(days // 365)
                        days = days % 365
        
        converted = ""
        unit_keys = ["year", "day", "hour", "minute", "second"]
        unit_values = [years, days, hours, mins, sec]
        for i in range(0, 4):
            if unit_values[i] != 0:
                converted += self.plural(unit_values[i], unit_keys[i]) + ", "
        converted += self.plural(unit_values[4], unit_keys[4])

        return converted

    def registerCommands(self):
        @self.bot.command()
        async def help(ctx):
            if is_it_me:
                await ctx.respond("```$die\n$restart\n$refreshServerData\n$load [cog]\n$unload [cog]\n$reload [cog]\n$change_status [listen/watch/stream/custom/(blank for play)] [status]\n$global_blacklist [member]\n$global_unblacklist [member]\n$read_blacklist\n$locate_id [member id]\n$ping\n$wipe_brain [personality]\n$to_do [task]\n$fetch_to_do\n$patch [major/minor/misc] [info]\n$nickname [addition]```")
            else:
                await ctx.respond("No more prefix commands here! You are welcome to use my slash commands though :)")

        @self.bot.command(hidden=True)
        @commands.check(is_it_me)
        async def die(ctx):
            await self.bot.change_presence(activity=discord.Game("Goodbye."))
            await ctx.respond("Goodbye, father.")

            os._exit(0)

        @self.bot.command(hidden=True)
        @commands.check(is_it_me)
        async def restart(ctx):
            await ctx.respond("Restarting!", ephemeral=True)

            python = sys.executable
            script = os.path.abspath(sys.argv[0])

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            os.system('cls')
            print(f"[        ...        ]\nGuacBot is restarting\nTime since:  {current_time}")

            # Launch new process
            subprocess.Popen([python, script])

            # Kill current process
            os._exit(0)

        @self.bot.command(name="refreshServerData", hidden=True)
        @commands.check(is_it_me)
        async def refresh_server_data(ctx):
            self.jason.refreshServerData(self.bot)
            await ctx.respond("Refreshing server data!", ephemeral=True)

        @self.bot.command(hidden=True)
        @commands.check(is_it_me)
        async def load(ctx, extension):
            try:
                extension = extension.lower()
                self.bot.load_extension(f'cogs.{extension}')
                await ctx.respond(f'Extension "{extension}" loaded!', ephemeral=True)
            except:
                await ctx.respond(f"Couldn't load {extension} extension.", ephemeral=True)

        @self.bot.command(hidden=True)
        @commands.check(is_it_me)
        async def unload(ctx, extension):
            try:
                extension = extension.lower()
                self.bot.unload_extension(f'cogs.{extension}')
                await ctx.respond(f'Extension "{extension}" unloaded!', ephemeral=True)
            except:
                await ctx.respond(f"Couldn't unload {extension} extension.", ephemeral=True)

        @self.bot.command(hidden=True)
        @commands.check(is_it_me)
        async def reload(ctx, extension):
            try:
                extension = extension.lower()
                self.bot.unload_extension(f'cogs.{extension}')
                self.bot.load_extension(f'cogs.{extension}')
                await ctx.respond(f'Extension "{extension}" reloaded!', ephemeral=True)
            except:
                await ctx.respond(f"Couldn't reload {extension} extension.", ephemeral=True)

        # "show" slash command group
        show = self.bot.create_group("show", "Vanilla as heck!")

        @show.command(description="Displays my uptime and when it was last checked!")
        async def uptime(ctx):
            bot_data = self.jason.fetchBotData()
            uptime_elapsed = time.time() - bot_data["hq"]["start_time"]
            time_since_checked = time.time() - bot_data["hq"]["time_checked"]
            bot_data["hq"]["time_checked"] = time.time()
            self.bot_data = bot_data
            self.jason.updateBotData(self.bot_data)
            await ctx.respond(f"\nUptime: {self.time_convert(uptime_elapsed)}\nLast Checked: {self.time_convert(time_since_checked)} ago.")

        @show.command(description="Displays the bot's current version!")
        async def version(ctx):
            await ctx.respond(f"Current version: {self.botData["hq"]["version"]}")

        @show.command(description="Guac will send his link and a link to his server!")
        async def invite(ctx):
            await ctx.respond("Link to bot: https://discord.com/api/oauth2/authorize?client_id=582337819532460063&permissions=8&scope=bot\nLink to support server: https://discord.gg/2kgZazXN68")

    @tasks.loop(seconds=300)
    async def change_status(self):
        new_status = next(self.statuses)
        activity_type = new_status["type"]
        activity_text = new_status["status"]
        if activity_type == "game":
            await self.bot.change_presence(activity=discord.Game(activity_text))
        elif activity_type == "stream":
            await self.bot.change_presence(activity=discord.Streaming(name=activity_text, url="https://www.twitch.tv/guacamolefather"))
        elif activity_type == "watch":
            await self.bot.change_presence(activity=discord.Activity(name=activity_text, type=discord.ActivityType.watching))
        elif activity_type == "listen":
            await self.bot.change_presence(activity=discord.Activity(name=activity_text, type=discord.ActivityType.listening))

    @tasks.loop(seconds=1)
    async def animation(self):
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        os.system('cls')
        print(f"{next(self.animation_states)}\n~ GuacBot is active ~\nThe time is: {current_time}")

if __name__ == "__main__":
    try:
        hq = HQ()
    except Exception as e:
        with open("E:/guac_data/crashlog.txt", "a") as f:
            t = time.localtime()
            current_time = time.strftime("%m/%d/%Y, %H:%M:%S", t)
            f.write(f"\n[{current_time}] {e}\n\n")
