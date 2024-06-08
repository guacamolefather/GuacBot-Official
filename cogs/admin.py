from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.commands import SlashCommandGroup
from discord.ext import commands
import discord, time, requests

botData = FetchBotData()
serverData = FetchServerData()

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    admin = SlashCommandGroup("admin", "Zero shower guarantee!")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin processes active.")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @admin.command(description="Gets rid of a specified amount of messages.") # Slash command for clearing messages
    @discord.default_permissions(manage_messages=True) # User needs to have manage messages permission
    async def clear_messages(self, ctx, amount: int):
        await ctx.respond(f"Clearing {amount} messages...", ephemeral=True)
        time.sleep(1)
        await ctx.channel.purge(limit=amount)
    

    @admin.command(description="Steals the given custom emoji for the server.") # Slash command for stealing an emoji
    @discord.default_permissions(manage_emojis=True) # Only full admins can use this command
    async def steal_emoji(self, ctx, *, emoji):

        if not emoji.startswith("<"):
            await ctx.respond("Just an emoji, pls.", ephemeral=True)
            return
        
        try:
            _id = emoji.split(":") # split by ":"
            if "<a" == _id[0]: # animated emojis structure <a:name:id>
                ext = "gif"
            else:
                ext = "png" # normal emojis structure <name:id>
            e_id = _id[2].split(">")[0].strip()# get the id
            # url for a emoji is like this
            url = f"https://cdn.discordapp.com/emojis/{e_id}.{ext}"

            img_data = requests.get(url).content
            emoji_name = _id[1]

            await ctx.guild.create_custom_emoji(name=emoji_name, image=img_data)
            await ctx.respond("Done!", ephemeral=True)
            
        except Exception as e:
            if not isinstance(e, discord.Forbidden):
                await ctx.respond(f"Just an emoji, pls.", ephemeral=True)
            else:
                await ctx.respond(f"I don't have permission to do that...", ephemeral=True)


    @admin.command(description="Returns server data on the user.") # Slash command for returning server data on the user
    async def profile(self, ctx, member: discord.Member):
        botData = FetchBotData()
        serverData = FetchServerData()
        
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
        
        # Reaction ban status:
        isBanned = False
        how = "isn't"
        if (member.id in serverData[str(ctx.guild.id)]["Reactions"]["blacklist"]):
            isBanned = True
            how = "individually, by an admin."
        for banned in serverData[str(ctx.guild.id)]["Reactions"]["roleblacklist"]:
            for role in member.roles:
                if (role.id == banned):
                    isBanned = True
                    how = "via a role."
        if (str(member.id) in botData["Reactions"]["global_blacklist"].keys()):
            isBanned = True
            how = "globally, by my dad."
            
        if (isBanned):
            embed.add_field(name="Reactions status:",value=f"Banned {how}",inline=False)
        else:
            embed.add_field(name="Reactions status:",value="Available! Feel free to talk to me :)",inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


    @admin.command(description="Counts the amount of people with certain roles.") # Slash command for counting the amount of people with certain roles
    @discord.default_permissions(manage_roles=True) # Only full admins can use this command
    async def role_count(self, ctx):
        withrole = 0
        memberswithrole = ""
        fields = 1

        icon_url = ctx.guild.icon.url
        embed = discord.Embed(title="Role Count", description=f"{ctx.guild.member_count} members including me :)",color=ctx.guild.owner.top_role.color)
        embed.set_thumbnail(url=icon_url)
        
        for role in ctx.guild.roles:
            for member in ctx.guild.members:
                if role in member.roles:
                    withrole += 1
                    memberswithrole += " - " + member.display_name
            print(len(memberswithrole))
            fields += 1
            
            embed.add_field(name=f"{role} - created on {role.created_at.strftime('%d/%m/%Y at %H:%M:%S')}:",value=str(withrole) + ": (" + memberswithrole + ")", inline=False)
            withrole = 0
            memberswithrole = ""
        
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Admin(bot))
