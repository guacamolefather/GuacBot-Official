from re import M
from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.ext import commands, bridge
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
    @bridge.bridge_command(description="Tests if the Owner cog is loaded.") # Bridge command for testing if the cog is loaded
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def ownertest(self, ctx):
        await ctx.respond('Owner extension cog works!', ephemeral=True)
    
    @bridge.bridge_command(description="Makes Guac send a TTS message with the specified words.") # Bridge command for making Guac send a TTS message with the specified words
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def faketts(self, ctx, *, words: commands.clean_content):
        await ctx.respond(words, tts=True, ephemeral=True)
    
    @bridge.bridge_command(description="Changes Guac's status.") # Bridge command for changing Guac's status
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def changestatus(self, ctx, activity: str, *, status: str):
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
            await self.bot.change_presence(activity=discord.Game(status))

        await ctx.respond("Status changed!", ephemeral=True)
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DATA COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Globally Guac blacklists the specified member.") # Bridge command for globally blacklisting a member
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def globalblacklist(self, ctx, member : discord.Member):
        botData = FetchBotData()
        try:
            botData["Reactions"]["global_blacklist"][f"{member.id}"] = member.name
        except:
            await ctx.respond("Member already on the global blacklist.", ephemeral=True)
            return
        UpdateBotData(botData)
        await ctx.respond(f"{member.name} now on Guac global blacklist.")

    @bridge.bridge_command(description="Globally Guac unblacklists the specified member.") # Bridge command for globally unblacklisting a member
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def globalunblacklist(self, ctx, member : discord.Member):
        botData = FetchBotData()
        try:
            del botData["Reactions"]["global_blacklist"][f"{member.id}"]
        except:
            await ctx.respond("Member not on the global blacklist.", ephemeral=True)
            return
        UpdateBotData(botData)
        await ctx.respond(f"{member.name} bailed from Guac global blacklist :rolling_eyes:")

    @bridge.bridge_command(description="Shows global blacklist.") # Bridge command for showing the global blacklist
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def readblacklist(self, ctx):
        botData = FetchBotData()
        message = "Global blacklist:\n"
        for loser in botData["Reactions"]["global_blacklist"].values():
            message += f"- {loser}\n"
        await ctx.respond(message)

    @bridge.bridge_command(description="Locates the member based on their ID.") # Bridge command for locating a member based on their ID")
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def locateid(self, ctx, member_id):
        member = None
        try:
            member = await self.bot.fetch_user(int(member_id))
        except:
            pass
        
        if member is None:
            await ctx.respond("Member not found.", ephemeral=True)
        else:
            await ctx.respond(f"Member ID is for: {member.name}", ephemeral=True)
            

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BRAIN COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Empties GuacBot's short-term memory.") # Bridge command for emptying GuacBot's short-term memory
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def wipebrain(self, ctx, personality: str):
        if personality == "GuacBot" or personality == "SalsAI":
            brainData = FetchBrainData()
            brainData[personality]["memory"] = []
            UpdateBrainData(brainData)
            await ctx.respond(f"{personality}'s memory wiped!", ephemeral=True)
        else:
            await ctx.respond("Invalid personality.", ephemeral=True)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PERSONAL COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Adds something to the to-do list.") # Bridge command for adding something to the to-do list
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def todo(self, ctx, *, do: str):
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
    
    @bridge.bridge_command(description="Fetches pending to-do list items.") # Bridge command for collecting unreacted messages in #guacbot-to-do
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def fetchtodo(self, ctx):
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

    @bridge.bridge_command(description="Updates the patch notes + version and sends them to the announcements channel.") # Bridge command for updating the patch notes and version
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def patch(self, ctx, patch_type: str, patch_info: str):
        
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
        
    @bridge.bridge_command(description="Adds a new nickname to the list.") # Bridge command for adding a new nickname to the list
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def nickname(self, ctx, *, name: str):
        with open('E:/z_Nicknames.txt', 'a', encoding='utf-8') as writer:
            writer.write(f"\n- {name}")
        writer.close()
        
        await ctx.respond(f'Added "{name}" to the list!')

def setup(bot):
    bot.add_cog(Owner(bot))