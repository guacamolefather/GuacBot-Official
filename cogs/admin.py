from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.ext import commands, bridge
import discord, time, requests

botData = FetchBotData()
serverData = FetchServerData()

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin processes active.")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Tests if the Admin cog is loaded.") # Bridge command for testing if the cog is loaded
    @commands.check(is_it_me) # Only dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def admintest(self, ctx):
        await ctx.respond('Admin extension cog works!', ephemeral=True)

    @commands.slash_command(description="Gets rid of a specified amount of messages.") # Slash command for clearing messages
    @discord.default_permissions(manage_messages=True) # User needs to have manage messages permission
    async def message_clear(self, ctx, amount: int):
        await ctx.respond(f"Clearing {amount} messages...", ephemeral=True)
        time.sleep(1)
        await ctx.channel.purge(limit=amount)

    @commands.slash_command(description="Softbans the specified member (with opt reason).") # Slash command for softbanning a member
    @discord.default_permissions(ban_members=True) # Only full admins can use this command
    async def softban(self, ctx, member: discord.Member, *, reason="A good one, trust me."):
        await member.ban(reason=reason)
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.respond(f'Softbanned {member.mention}.\nReason: {reason}.')
                return
    
    @commands.slash_command(description="Steals the given custom emoji for the server.") # Slash command for stealing an emoji
    @discord.default_permissions(manage_emojis=True) # Only full admins can use this command
    async def stealemoji(self, ctx, *, emoji):

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

    @commands.slash_command(description="Returns server data on the user.") # Slash command for returning server data on the user
    async def adminprofile(self, ctx, member: discord.Member):
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

        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(description="Counts the amount of people with certain roles.") # Slash command for counting the amount of people with certain roles
    @discord.default_permissions(manage_roles=True) # Only full admins can use this command
    async def rolecount(self, ctx):
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
            
            embed.add_field(name=f"{role} members:",value=str(withrole) + ": (" + memberswithrole + ")", inline=False)
            withrole = 0
            memberswithrole = ""
        
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Admin(bot))
