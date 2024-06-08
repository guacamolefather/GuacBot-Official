from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.commands import SlashCommandGroup
from discord.ext import commands
import discord

botData = FetchBotData()
serverData = FetchServerData()

class GuacMod(commands.Cog): # Commands for moderating GuacBot

    def __init__(self, bot):
        self.bot = bot
        
    guac = SlashCommandGroup("guac", "Control GuacBot!")
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self):
        print("Guac moderation processes active.")
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @guac.command(description="Shows the json data for the server.") # Slash command for showing the json data for the server
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    async def guild_data(self, ctx):
        await ctx.respond(serverData[str(ctx.guild.id)])

    @guac.command(description="Blacklists the specified member from reactions.") # Slash command for server blacklisting a member from reactions
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    async def blacklist(self, ctx, member : discord.Member):
        if member.id in serverData[str(ctx.guild.id)]["Reactions"]["blacklist"]:
            await ctx.respond(f"{member.display_name} already blacklisted for reactions.")
            return
        serverData[str(ctx.guild.id)]["Reactions"]["blacklist"].append(member.id)
        UpdateServerData(serverData)
        await ctx.respond(f"{member.display_name} blacklisted for reactions.")

    @guac.command(description="Unblacklists the specified member from reactions.") # Slash command for server unblacklisting a member from reactions
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    async def unblacklist(self, ctx, member : discord.Member):
        indexingPurposes = serverData[str(ctx.guild.id)]["Reactions"]["blacklist"]
        if member.id not in indexingPurposes:
            await ctx.respond(f"{member.display_name} already not blacklisted for reactions.")
            return
        serverData[str(ctx.guild.id)]["Reactions"]["blacklist"].pop(indexingPurposes.index(member.id))
        UpdateServerData(serverData)
        await ctx.respond(f"{member.display_name} no longer blacklisted for reactions.")

    @guac.command(description="Flips whether GuacBot reacts to bots.")
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    async def bot_reaction_switch(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Reactions"]["reactions"]
        serverData[str(ctx.guild.id)]["Reactions"]["reactions"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Reactions on: {not duplicationPurposes}")

    @guac.command(description="Flips whether GuacBot reactions are on.")
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    async def all_reaction_switch(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Reactions"]["reactions"]
        serverData[str(ctx.guild.id)]["Reactions"]["reactions"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Reactions on: {not duplicationPurposes}")

    @guac.command(description="Flips whether GuacBot is allowing gambling.")
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    async def economy_switch(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Economy"]["economy"]
        serverData[str(ctx.guild.id)]["Economy"]["economy"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Economy on: {not duplicationPurposes}")

def setup(bot):
    bot.add_cog(GuacMod(bot))