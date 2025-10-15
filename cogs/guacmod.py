import discord

from discord.commands import SlashCommandGroup
from discord.ext import commands

from helper_classes.data import *


jason = Jason()
#bot_data = jason.fetchBotData()
#server_data = jason.fetchServerData()

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
    @discord.guild_only()
    async def guild_data(self, ctx):
        server_data = jason.fetchServerData()
        await ctx.respond(server_data[str(ctx.guild.id)])

    @guac.command(description="Blacklists the specified member from reactions.") # Slash command for server blacklisting a member from reactions
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    @discord.guild_only()
    async def blacklist(self, ctx, member : discord.Member):
        server_data = jason.fetchServerData()
        if member.id in server_data[str(ctx.guild.id)]["reaction_cog"]["blacklist"]:
            await ctx.respond(f"{member.display_name} already blacklisted for reactions.")
            return
        server_data[str(ctx.guild.id)]["reaction_cog"]["blacklist"].append(member.id)
        jason.updateServerData(server_data)
        await ctx.respond(f"{member.display_name} blacklisted for reactions.")

    @guac.command(description="Unblacklists the specified member from reactions.") # Slash command for server unblacklisting a member from reactions
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    @discord.guild_only()
    async def unblacklist(self, ctx, member : discord.Member):
        server_data = jason.fetchServerData()
        indexing_purposes = server_data[str(ctx.guild.id)]["reaction_cog"]["blacklist"]
        if member.id not in indexing_purposes:
            await ctx.respond(f"{member.display_name} already not blacklisted for reactions.")
            return
        server_data[str(ctx.guild.id)]["reaction_cog"]["blacklist"].pop(indexing_purposes.index(member.id))
        jason.updateServerData(server_data)
        await ctx.respond(f"{member.display_name} no longer blacklisted for reactions.")

    @guac.command(description="Flips whether GuacBot reacts to bots.")
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    @discord.guild_only()
    async def bot_reaction_switch(self, ctx):
        server_data = jason.fetchServerData()
        duplication_purposes = server_data[str(ctx.guild.id)]["reaction_cog"]["reactions"]
        server_data[str(ctx.guild.id)]["reaction_cog"]["reactions"] = not duplication_purposes
        jason.updateServerData(server_data)
        await ctx.respond(f"Reactions on: {not duplication_purposes}")

    @guac.command(description="Flips whether GuacBot reactions are on.")
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    @discord.guild_only()
    async def all_reaction_switch(self, ctx):
        server_data = jason.fetchServerData()
        duplication_purposes = server_data[str(ctx.guild.id)]["reaction_cog"]["reactions"]
        server_data[str(ctx.guild.id)]["reaction_cog"]["reactions"] = not duplication_purposes
        jason.updateServerData(server_data)
        await ctx.respond(f"Reactions on: {not duplication_purposes}")

    @guac.command(description="Flips whether GuacBot is allowing gambling.")
    @discord.default_permissions(administrator=True) # Only full admins can use this command
    @discord.guild_only()
    async def economy_switch(self, ctx):
        server_data = jason.fetchServerData()
        duplication_purposes = server_data[str(ctx.guild.id)]["economy_cog"]["economy"]
        server_data[str(ctx.guild.id)]["economy_cog"]["economy"] = not duplication_purposes
        jason.updateServerData(server_data)
        await ctx.respond(f"Economy on: {not duplication_purposes}")

def setup(bot):
    bot.add_cog(GuacMod(bot))