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


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ OWNER COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
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
    async def locateid(self, ctx, member_id: int):
        member = None
        try:
            member = await self.bot.fetch_user(member_id)
        except:
            pass
        
        if member is None:
            await ctx.respond("Member not found.", ephemeral=True)
        else:
            await ctx.respond(f"Member ID is for: {member.name}", ephemeral=True)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PERSONAL COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Adds something to the to-do list.")
    @commands.check(is_it_me)
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def todo(self, ctx, *, do: str):
        with open('z_ToDoList.txt', 'a', encoding='utf-8') as writer:
            writer.write(f"\n - {do}")
        writer.close()

        channel = self.bot.get_channel(813974138581942282)
        await channel.send(f"- {do}")
        
        await ctx.respond('Added to the list!', ephemeral=True)

    @bridge.bridge_command(description="Updates the patch notes + version and sends them to the announcements channel.")
    @commands.check(is_it_me)
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
        
    @bridge.bridge_command(description="Adds a new nickname to the list.")
    @commands.check(is_it_me)
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def nickname(self, ctx, *, name: str):
        with open('z_Nicknames.txt', 'a', encoding='utf-8') as writer:
            writer.write(f"\n- {name}")
        writer.close()
        
        await ctx.respond(f'Added "{name}" to the list!')

def setup(bot):
    bot.add_cog(Owner(bot))