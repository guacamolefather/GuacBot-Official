import discord, time, requests

from discord.ext import commands

from helper_classes.data import *


jason = Jason()
#bot_data = jason.fetchBotData()
#server_data = jason.fetchServerData()

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    admin = discord.commands.SlashCommandGroup("admin", "Zero shower guarantee!")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin processes active.")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @admin.command(description="Gets rid of a specified amount of messages.") # Slash command for clearing messages
    @discord.default_permissions(manage_messages=True) # User needs to have manage messages permission
    @discord.guild_only() # Only works in guilds
    async def clear_messages(self, ctx, amount: int):
        await ctx.respond(f"Clearing {amount} messages...", ephemeral=True)
        time.sleep(1)
        await ctx.channel.purge(limit=amount)
    

    @admin.command(description="Steals the given custom emoji for the server.") # Slash command for stealing an emoji
    @discord.default_permissions(manage_emojis=True) # Only full admins can use this command
    @discord.guild_only() # Only works in guilds
    async def steal_emoji(self, ctx, *, emoji):

        if not emoji.startswith("<"):
            await ctx.respond("Just a custom emoji, pls.", ephemeral=True)
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
                await ctx.respond(f"Just a custom emoji, pls.", ephemeral=True)
            else:
                await ctx.respond(f"I don't have permission to do that...", ephemeral=True)


    @admin.command(description="Returns server data on the user.") # Slash command for returning server data on the user
    @discord.guild_only() # Only works in guilds
    async def profile(self, ctx, member: discord.Member):
        bot_data = jason.fetchBotData()
        server_data = jason.fetchServerData()
        
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
            is_counter += 1
            if (channel.permissions_for(member).read_messages):
                has_counter += 1
        embed.add_field(name="Channels:",value=f"Has access to {has_counter} out of {is_counter} channels.",inline=False)
        
        # Reaction ban status:
        is_banned = False
        how = "isn't"
        if (member.id in server_data[str(ctx.guild.id)]["reaction_cog"]["blacklist"]):
            isBanned = True
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

        await ctx.respond(embed=embed, ephemeral=True)


    @admin.command(description="Counts the amount of people with certain roles.") # Slash command for counting the amount of people with certain roles
    @discord.default_permissions(manage_roles=True) # Only full admins can use this command
    @discord.guild_only() # Only works in guilds
    async def role_count(self, ctx):
        with_role = 0
        members_with_role = ""
        fields = 1

        icon_url = ctx.guild.icon.url
        embed = discord.Embed(title="Role Count", description=f"{ctx.guild.member_count} members including me :)",color=ctx.guild.owner.top_role.color)
        embed.set_thumbnail(url=icon_url)
        
        for role in ctx.guild.roles:
            for member in ctx.guild.members:
                if role in member.roles:
                    with_role += 1
                    members_with_role += " - " + member.display_name
            print(len(members_with_role))
            fields += 1
            
            embed.add_field(name=f"{role} - created on {role.created_at.strftime('%d/%m/%Y at %H:%M:%S')}:", value=f"{with_role}: ({members_with_role})", inline=False)
            with_role = 0
            members_with_role = ""
        
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Admin(bot))
