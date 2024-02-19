from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.ext import commands, bridge
import discord


class Utility(commands.Cog): # Commands for general utility purposes (usually stats or other info gathering stuff)

    def __init__(self, bot): # Cog bot context requierment
        self.bot = bot


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self): # Tells OS that the utility cog is active
        print("Utility processes active.")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Tests if the Utility cog is loaded.") # Bridge command for testing if the cog is loaded
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def utilitytest(self, ctx):
        await ctx.respond('Utility extension cog works!', ephemeral=True)

    @bridge.bridge_command(description="Pings Guac.") # Bridge command for pinging the bot to check latency
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def ping(self, ctx):
        await ctx.respond(f'Latency: {round(self.bot.latency * 1000)}ms.', ephemeral=True)

    @commands.slash_command(description="Shows the avatar of the given member (or user if not given).") # Slash command for showing the avatar of a given member (or the user if none given)
    async def avatar(self, ctx, member : discord.Member=None):
        if (member == None):
            member = ctx.author
        await ctx.respond(f"{member.avatar.url}", ephemeral=True)
    
    @commands.slash_command(description="Returns an image of the given custom emoji.") # Slash command for returning an image of the given custom emoji
    async def emojiimage(self, ctx, *, msg):
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
    
    @commands.slash_command(description="Shows total + human + online/DND member count.") # Slash command for showing how many members are in the server
    async def rolecall(self, ctx):
        notbots = 0
        online = 0
        icon_url = ctx.guild.icon.url
        embed = discord.Embed(title="Rolecall", description=f"{ctx.guild.member_count} members including me :)")
        embed.set_thumbnail(url=icon_url)

        # Not bot members
        for member in ctx.guild.members:
            if not member.bot:
                notbots += 1
        embed.add_field(name='"Human" Member(s):',value=notbots, inline=False)
        
        # Online members
        for member in ctx.guild.members:
            if (str(member.status) == "online" or str(member.status) == "dnd") and not member.bot:
                online += 1
        embed.add_field(name='"Human" Member(s) Online/DND:',value=online, inline=False)

        await ctx.respond(embed=embed)
        
    @commands.slash_command(description="Returns server data on the user.") # Slash command for returning server data on the user
    async def profile(self, ctx):
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
        hasCounter = 0
        isCounter = 0
        for channel in ctx.guild.text_channels:
            isCounter = isCounter + 1
            if (channel.permissions_for(member).read_messages):
                hasCounter = hasCounter + 1
        embed.add_field(name="Channels:",value=f"Has access to {hasCounter} out of {isCounter} channels.",inline=False)

        # Admin profile notification:
        embed.add_field(name="Regular profile",value="This is the regular profile command. For the admin command (other user), use /adminprofile (with admin priviledges).", inline=False)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))
