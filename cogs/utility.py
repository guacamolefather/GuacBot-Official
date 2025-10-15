import discord

from discord.commands import SlashCommandGroup
from discord.ext import commands

from helper_classes.data import *

jason = Jason()
#bot_data = jason.fetchBotData()
#server_data = jason.fetchServerData()

class Utility(commands.Cog): # Commands for general utility purposes (usually stats or other info gathering stuff)

    def __init__(self, bot): # Cog bot context requierment
        self.bot = bot
        
    utility = SlashCommandGroup("utility", "Useful AND sentimental!")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self): # Tells OS that the utility cog is active
        print("Utility processes active.")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @utility.command(description="Shows the avatar of the given member (or user if not given).") # Slash command for showing the avatar of a given member (or the user if none given)
    async def avatar(self, ctx, member : discord.Member=None):
        if (member == None):
            member = ctx.author
        await ctx.respond(f"{member.avatar.url}", ephemeral=True)
    
    @utility.command(description="Returns an image of the given custom emoji.") # Slash command for returning an image of the given custom emoji
    async def emoji_image(self, ctx, *, msg):
        if not msg.startswith("<"):
            await ctx.respond("Just a custom emoji, pls.", ephemeral=True)
            return
        
        try:
            _id = msg.split(":") # Split by ":"
            if "<a" == _id[0]: # Animated emojis structure <a:name:id>
                ext = "gif"
            else:
                ext = "png" # Normal emojis structure <name:id>
            e_id = _id[2].split(">")[0].strip()# Get the id
            # URL for an emoji is like this
            url = f"https://cdn.discordapp.com/emojis/{e_id}.{ext}"

            await ctx.respond(f"**Name**: :{_id[1]}:\n**Link**: {url}", ephemeral=True)
            
        except:
            await ctx.respond("Just a custom emoji, pls.", ephemeral=True)
    
    @utility.command(description="Shows total + human + online/DND member count.") # Slash command for showing how many members are in the server
    @discord.guild_only()
    async def role_call(self, ctx):
        not_bots = 0
        online = 0
        icon_url = ctx.guild.icon.url
        embed = discord.Embed(title="Rolecall", description=f"{ctx.guild.member_count} members including me :)")
        embed.set_thumbnail(url=icon_url)

        # Not bot members
        for member in ctx.guild.members:
            if not member.bot:
                not_bots += 1
        embed.add_field(name='"Human" Member(s):',value=not_bots, inline=False)
        
        # Online members
        for member in ctx.guild.members:
            if (str(member.status) == "online" or str(member.status) == "dnd") and not member.bot:
                online += 1
        embed.add_field(name='"Human" Member(s) Online/DND:',value=online, inline=False)

        await ctx.respond(embed=embed)
        
    @utility.command(description="Returns server data on the user.") # Slash command for returning server data on the user
    @discord.guild_only()
    async def profile(self, ctx):
        bot_data = jason.fetchBotData()
        server_data = jason.fetchServerData()
        
        member = ctx.author
        embed = discord.Embed(title=str(member), description="Member data:", colour=member.top_role.color, url="https://github.com/guacamolefather?tab=repositories")
        embed.set_thumbnail(url=member.avatar.url)
        
        # Member's ID:
        embed.add_field(name="ID:",value=member.id, inline=False)
        
        # Member's spawn date:
        embed.add_field(name="Account created on:",value=member.created_at.strftime("%d/%m/%Y at %H:%M:%S"), inline=False)
        
        # Member's join date:
        embed.add_field(name="Joined server on:",value=member.joined_at.strftime("%d/%m/%Y at %H:%M:%S"), inline=False)

        # Member's roles:
        member_roles = []
        fancy_roles_list = ""
        if (len(member.roles) > 1):
            raw_list = [role.mention for role in member.roles]
            raw_list.pop(0)
            for i in raw_list:
                member_roles.insert(0, i)
            for role in member_roles:
                fancy_roles_list = fancy_roles_list + "- " + role + "\n"
        else:
            fancy_roles_list = "None"
        embed.add_field(name="Role(s):",value=fancy_roles_list, inline=False)
        
        # How many channels member has access to:
        has_counter = 0
        is_counter = 0
        for channel in ctx.guild.text_channels:
            is_counter = is_counter + 1
            if (channel.permissions_for(member).read_messages):
                has_counter = has_counter + 1
        embed.add_field(name="Channels:",value=f"Has access to {has_counter} out of {is_counter} channels.",inline=False)
        
        # Reaction ban status:
        is_banned = False
        how = "isn't"
        if (member.id in server_data[str(ctx.guild.id)]["reaction_cog"]["blacklist"]):
            is_banned = True
            how = "individually, by an admin."
        for banned in server_data[str(ctx.guild.id)]["reaction_cog"]["role_blacklist"]:
            for role in member.roles:
                if (role.id == banned):
                    is_banned = True
                    how = "via a role."
        if (str(member.id) in bot_data["reaction_cog"]["global_blacklist"].keys()):
            is_banned = True
            how = "globally, by my dad."
            
        if (is_banned):
            embed.add_field(name="Reactions status:",value=f"Banned {how}",inline=False)
        else:
            embed.add_field(name="Reactions status:",value="Available! Feel free to talk to me (GuacBot) :)",inline=False)

        # Admin profile notification:
        embed.add_field(name="Regular profile",value="This is the regular profile command. For the admin version, use /profile from the admin section.", inline=False)

        await ctx.respond(embed=embed)

    @utility.command(description="Shows info about a role.") # Slash command for showing info about a role
    @discord.guild_only()
    async def role_info(self, ctx, role: discord.Role):
        embed = discord.Embed(title=f"{role.name}", description="Role data:", colour=role.color, url="https://github.com/guacamolefather?tab=repositories")
        embed.set_thumbnail(url=role.guild.icon.url)
        embed.add_field(name="ID:",value=role.id, inline=False)
        embed.add_field(name="Created on:",value=str(role.created_at.strftime('%d/%m/%Y at %H:%M:%S')), inline=False)
        embed.add_field(name="Members with this role:",value=len(role.members), inline=False)
        
        await ctx.respond(embed=embed)
    
def setup(bot):
    bot.add_cog(Utility(bot))
