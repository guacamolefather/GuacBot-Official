from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.ext import commands, bridge
import discord

botData = FetchBotData()
serverData = FetchServerData()

class GuacMod(commands.Cog): # Commands for moderating GuacBot

    def __init__(self, bot):
        self.bot = bot
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self):
        print("Guac moderation processes active.")
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Tests if the GuacMod cog is loaded.") # Bridge command for testing if the cog is loaded
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def guacmodtest(self, ctx):
        await ctx.respond('Guac moderation extension cog works!', ephemeral=True)

    @commands.slash_command(description="Shows the json data for the server.") # Slash command for showing the json data for the server
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    async def guilddata(self, ctx):
        await ctx.respond(serverData[str(ctx.guild.id)])

    @commands.slash_command(description="Blacklists the specified member from reactions.") # Slash command for server blacklisting a member from reactions
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def guacblacklist(self, ctx, member : discord.Member):
        if member.id in serverData[str(ctx.guild.id)]["Reactions"]["blacklist"]:
            await ctx.respond(f"{member.display_name} already blacklisted for reactions.")
            return
        serverData[str(ctx.guild.id)]["Reactions"]["blacklist"].append(member.id)
        UpdateServerData(serverData)
        await ctx.respond(f"{member.display_name} blacklisted for reactions.")

    @commands.slash_command(description="Unblacklists the specified member from reactions.") # Slash command for server unblacklisting a member from reactions
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def guacunblacklist(self, ctx, member : discord.Member):
        indexingPurposes = serverData[str(ctx.guild.id)]["Reactions"]["blacklist"]
        if member.id not in indexingPurposes:
            await ctx.respond(f"{member.display_name} already not blacklisted for reactions.")
            return
        serverData[str(ctx.guild.id)]["Reactions"]["blacklist"].pop(indexingPurposes.index(member.id))
        UpdateServerData(serverData)
        await ctx.respond(f"{member.display_name} no longer blacklisted for reactions.")

    @commands.slash_command(description="Flips whether GuacBot reacts to bots.")
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def botreactionson(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Reactions"]["reactions"]
        serverData[str(ctx.guild.id)]["Reactions"]["reactions"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Reactions on: {not duplicationPurposes}")

    @commands.slash_command(description="Flips whether GuacBot reactions are on.")
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def reactionson(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Reactions"]["reactions"]
        serverData[str(ctx.guild.id)]["Reactions"]["reactions"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Reactions on: {not duplicationPurposes}")

    @commands.slash_command(description="Flips whether GuacBot is allowing gambling.")
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def economyon(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Economy"]["economy"]
        serverData[str(ctx.guild.id)]["Economy"]["economy"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Economy on: {not duplicationPurposes}")

def setup(bot):
    bot.add_cog(GuacMod(bot))