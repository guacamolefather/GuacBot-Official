from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.ext import commands, bridge
import discord, random

class Fun(commands.Cog): # THE COG ALL ABOUT HAVING FUN (kinda depracated)

    def __init__(self, bot):
        self.bot = bot


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT HANDLERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun processes active.")
        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMMANDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    @bridge.bridge_command(description="Tests if the Fun cog is loaded.") # Bridge command for testing if the cog is loaded
    @commands.check(is_it_me) # Only Dad can use this command
    @discord.default_permissions(administrator=True) # So most people can't see this command at all
    async def funtest(self, ctx):
        await ctx.respond('Fun extension cog works!', ephemeral=True)

    @commands.slash_command(description="Guac answers your question.") # Slash command for a fortune-telling eightball
    async def eightball(self, ctx, *, question: str):
        responses = ['Hmmmm.','Ask again.',"It's possible.",'Maybe.','Perhaps.','Not sure.','Uncertain.','(͡° ͜ʖ ͡°)','No clue.','Response hazy.']
        await ctx.respond(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.slash_command(description="Rolls specified sided die a specified amount of times.") # Slash command for rolling a dice (or multiple)
    async def rolldice(self, ctx, sides=6, amount=1):
        diceList=[]
        for i in range(0, amount):
            diceList.append(random.randint(1,sides))
            i = i + 1
        await ctx.respond("Your roll(s) are:  " + str(diceList))

    @commands.slash_command(description="Play a game of Rock, Paper, Scissors against Guac!") # Slash command for playing Rock, Paper, Scissors
    async def rps(self, ctx, choice: str):
        botchoice = random.randint(0, 2)
        if botchoice == 0 and choice.lower() == "rock":
            await ctx.respond("I chose rock!  It's a tie!")
        elif botchoice == 0 and choice.lower() == "paper":
            await ctx.respond("I chose rock! You win!")
        elif botchoice == 0 and choice.lower() == "scissors":
            await ctx.respond("I chose rock! I win!")
        elif botchoice == 1 and choice.lower() == "rock":
            await ctx.respond("I chose paper!  I win!")
        elif botchoice == 1 and choice.lower() == "paper":
            await ctx.respond("I chose paper! It's a tie!")
        elif botchoice == 1 and choice.lower() == "scissors":
            await ctx.respond("I chose paper! You win!")
        elif botchoice == 2 and choice.lower() == "rock":
            await ctx.respond("I chose scissors!  You win!")
        elif botchoice == 2 and choice.lower() == "paper":
            await ctx.respond("I chose scissors! I win!")
        elif botchoice == 2 and choice.lower() == "scissors":
            await ctx.respond("I chose scissors! It's a tie!")
        else:
            await ctx.respond("Do you know how to play this game or are you bad at spelling..?")

    @commands.command(hidden=True, description="You shouldn't be able to see this...") # Definitely not a secret command
    async def secret(self, ctx):
        try:
            await ctx.channel.purge(limit=1)
        except:
            return
        await ctx.send("SHH!!!", delete_after=3)

    #https://minecraft.fandom.com/wiki/Death_messages
    @commands.slash_command(description="Kills the specified member.") # Slash command for killing a member
    async def kill(self, ctx, member : discord.Member):
        if member.id == ctx.author.id:
            await ctx.respond("Do you need a lighthouse??")
            return
        if member.id == 409445517509001216 and random.randint(1, 10) != 8:
            await ctx.respond("Dad can't be killed??")
            return
        if member.id == 582337819532460063:
            await ctx.respond("Please don't kill me...")
            return
        dead = member.display_name
        killer = ctx.author.display_name
        deaths = [f"{dead} was shot.",
        f"{dead} blew themselves up!",
        f"{dead} fell to their death...",
        f"{dead} was pummeled by {killer}.",
        f"{dead} was pricked to death via cactus!",
        f"{dead} drowned...",
        f"{dead} experienced kinetic energy...",
        f"{dead} went up in flames!",
        f"{dead} was impaled!",
        f"{dead} was squashed by {killer}...",
        f"{dead} went out with a bang!",
        f"{dead} tried to swim in lava...",
        f"{dead} discovered the floor was lava!",
        f"{dead} was struck by lightning!",
        f"{dead} froze to death...",
        f"{dead} was slain by {killer}!",
        f"{dead} took the L.",
        f"{killer} handed {dead} the L."]
        i = len(deaths) - 1
        deathchoice = random.randint(0, i)
        await ctx.respond(deaths[deathchoice])

def setup(bot):
    bot.add_cog(Fun(bot))
