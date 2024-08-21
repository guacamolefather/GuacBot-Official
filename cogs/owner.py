from re import M
from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.commands import SlashCommandGroup
from discord.ext import commands
import discord, time

botData = FetchBotData()
serverData = FetchServerData()

class Owner(commands.Cog): # Commands just for me :)

    def __init__(self, bot): # Cog bot context requierment
        self.bot = bot

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self):
        print("Owner processes active.")
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HQ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.command(hidden=True, description="Changes Guac's status.") # Command for changing Guac's status
    @commands.check(is_it_me) # Only dad can use this command
    async def change_status(self, ctx, activity: str, *, status: str):
        # Setting "Listening" status
        if "listen" == activity.lower():
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))

        # Setting "Watching" status
        elif "watch" == activity.lower():
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))

        # Setting "Streaming" status
        elif "stream" == activity.lower():
            await self.bot.change_presence(activity=discord.Streaming(name=status, url="https://www.twitch.tv/thememesareallreal"))

        # Setting broken custom status
        elif "custom" == activity.lower():
            await self.bot.change_presence(activity=discord.CustomActivity(name=status))
            
        # Setting "Playing" status
        else:
            await self.bot.change_presence(activity=discord.Game(f'{activity} {status}'))

        await ctx.respond("Status changed!", ephemeral=True)
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DATA COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.command(hidden=True, description="Globally Guac blacklists the specified member.") # Command for globally blacklisting a member
    @commands.check(is_it_me) # Only dad can use this command
    async def global_blacklist(self, ctx, member : discord.Member):
        botData = FetchBotData()
        try:
            botData["Reactions"]["global_blacklist"][f"{member.id}"] = member.name
        except:
            await ctx.respond("Member already on the global blacklist.", ephemeral=True)
            return
        UpdateBotData(botData)
        await ctx.respond(f"{member.name} now on Guac global blacklist.")

    @commands.command(hidden=True, description="Globally Guac unblacklists the specified member.") # Command for globally unblacklisting a member
    @commands.check(is_it_me) # Only dad can use this command
    async def global_unblacklist(self, ctx, member : discord.Member):
        botData = FetchBotData()
        try:
            del botData["Reactions"]["global_blacklist"][f"{member.id}"]
        except:
            await ctx.respond("Member not on the global blacklist.", ephemeral=True)
            return
        UpdateBotData(botData)
        await ctx.respond(f"{member.name} bailed from Guac global blacklist :rolling_eyes:")

    @commands.command(hidden=True, description="Shows global blacklist.") # Command for showing the global blacklist
    @commands.check(is_it_me) # Only dad can use this command
    async def read_blacklist(self, ctx):
        botData = FetchBotData()
        message = "Global blacklist:\n"
        for loser in botData["Reactions"]["global_blacklist"].values():
            message += f"- {loser}\n"
        await ctx.respond(message)

    @commands.command(hidden=True, description="Locates the member based on their ID.") # Command for locating a member based on their ID")
    @commands.check(is_it_me) # Only dad can use this command
    async def locate_id(self, ctx, member_id):
        member = None
        try:
            member = await self.bot.fetch_user(int(member_id))
        except:
            pass
        
        if member is None:
            await ctx.respond("Member not found.", ephemeral=True)
        else:
            await ctx.respond(f"Member ID is for: {member.name}", ephemeral=True)
            
    
    @commands.command(hidden=True, description="Pings Guac.") # Command for pinging the bot to check latency
    @commands.check(is_it_me) # Only dad can use this command
    async def ping(self, ctx):
        await ctx.respond(f'Latency: {round(self.bot.latency * 1000)}ms.', ephemeral=True)
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BRAIN COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.command(hidden=True, description="Empties GuacBot's short-term memory.") # Command for emptying GuacBot's short-term memory
    @commands.check(is_it_me) # Only dad can use this command
    async def wipe_brain(self, ctx, personality: str):
        if personality == "GuacBot" or personality == "SalsAI":
            brainData = FetchBrainData()
            brainData[personality]["mod-memory"] = []
            UpdateBrainData(brainData)
            await ctx.respond(f"{personality}'s memory wiped!", ephemeral=True)
        else:
            await ctx.respond("Invalid personality.", ephemeral=True)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PERSONAL COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.command(hidden=True, description="Adds something to the to-do list.") # Command for adding something to the to-do list
    @commands.check(is_it_me) # Only dad can use this command
    async def to_do(self, ctx, *, do: str):
        channel = self.bot.get_channel(813974138581942282)
        await channel.send(f"- {do}")
        
        await ctx.respond('Added to the list!', ephemeral=True)
        
        messages = await channel.history(limit=100).flatten()
        messages.reverse()

        validReaction = False
        todo_list = "Pending tasks:"
        for message in messages:
            for reaction in message.reactions:
                if (reaction.emoji == "❌" or reaction.emoji == "❔" or reaction.emoji == "✅"):
                    validReaction = True
            if not validReaction:
                todo_list += f"\n{message.content}"
            validReaction = False
        for chunk in charLimit(todo_list):
            await ctx.respond(chunk, ephemeral=True)
        
        with open('z_ToDoList.txt', 'w', encoding='utf-8') as writer:
            writer.write(todo_list)
        writer.close()
        await ctx.respond("To-do list saved to file.", ephemeral=True)
    
    @commands.command(hidden=True, description="Fetches pending to-do list items.") # Command for collecting unreacted messages in #guacbot-to-do
    @commands.check(is_it_me) # Only dad can use this command
    async def fetch_to_do(self, ctx):
        channel = self.bot.get_channel(813974138581942282)
        messages = await channel.history(limit=100).flatten()
        messages.reverse()

        validReaction = False
        todo_list = "Pending tasks:"
        for message in messages:
            for reaction in message.reactions:
                if (reaction.emoji == "❌" or reaction.emoji == "❔" or reaction.emoji == "✅"):
                    validReaction = True
            if not validReaction:
                todo_list += f"\n{message.content}"
            validReaction = False
        for chunk in charLimit(todo_list):
            await ctx.respond(chunk, ephemeral=True)
        
        with open('z_ToDoList.txt', 'w', encoding='utf-8') as writer:
            writer.write(todo_list)
        writer.close()
        await ctx.respond("To-do list saved to file.", ephemeral=True)

    @commands.command(hidden=True, description="Updates the patch notes + version and sends them to the announcements channel.") # Command for updating the patch notes and version
    @commands.check(is_it_me) # Only dad can use this command
    async def patch(self, ctx, patch_type: str, *, patch_info: str):
        
        last_version = botData["HQ"]["version"]
        if patch_type.startswith("major"):
            split_version = last_version.split(".")
            new_version = f"{int(split_version[0]) + 1}.0.0"
        elif patch_type.startswith("minor"):
            split_version = last_version.split(".")
            new_version = f"{split_version[0]}.{int(split_version[1]) + 1}.0"
        else:
            split_version = last_version.split(".")
            new_version = f"{split_version[0]}.{split_version[1]}.{int(split_version[2]) + 1}"
        
        botData["HQ"]["version"] = new_version
        UpdateBotData(botData)
        
        current_date = time.strftime("%m/%d/%Y")
        patch = ""
        if patch_type.lower().startswith("a"):
            patch = f'- {current_date}: GuacBot{new_version} (an {patch_type} update)\n{patch_info}'
        else:
            patch = f'- {current_date}: GuacBot{new_version} (a {patch_type} update)\n{patch_info}'
        
        with open('z_PatchNotes.txt', 'a', encoding='utf-8') as writer:
            writer.write(f"\n\n{patch}")
        writer.close()

        channel = self.bot.get_channel(1205982934255804417)
        await channel.send(f"{patch}")
        
        await ctx.respond('Added to the notes!', ephemeral=True)
        
    @commands.command(hidden=True, description="Adds a new nickname to the list.") # Command for adding a new nickname to the list
    @commands.check(is_it_me) # Only dad can use this command
    async def nickname(self, ctx, *, name: str):
        with open('E:/z_Nicknames.txt', 'a', encoding='utf-8') as writer:
            writer.write(f"\n- {name}")
        writer.close()
        
        await ctx.respond(f'Added "{name}" to the list!')

def setup(bot):
    bot.add_cog(Owner(bot))