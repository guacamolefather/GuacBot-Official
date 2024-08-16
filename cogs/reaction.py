from cogs.extraclasses.jason import * # JSON file handling
from cogs.extraclasses.avocado import * # The infamous pineapple
from discord.ext import commands
import random, time, json, discord, requests, asyncio

def DIDAIMessage(message, sender, personality):
    url = "http://localhost:1337/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    name = sender.name
    if sender.id == 562372596008484875: # For Auntie
        name = "Sophie"

    brainData = FetchBrainData() # Fetch all AI data
    
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    messages = brainData[personality]["core-memory"] # Add personality specific memory
    brainData[personality]["mod-memory"].append({"role": "user", "content": f"{current_time} - {name} says: {message}"}) # Add most recent message to memory
    messages = messages + brainData[personality]["mod-memory"] # Combine personality with memory
    
    payload = {"messages" : messages} # Put all messages into payload
    payload.update(brainData[personality]["model"]) # Add model information to payload
        
    # Try to make the request and proceed accordingly
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    except:
        return "Sorry, my AI capabilities are currently offline. Please try again later."
        
    # Extracting 'content' value from response and updating Guac's memory
    result = response.json()
    content = result['choices'][0]['message']['content']
    
    if len(brainData[personality]["mod-memory"]) > 10: # If memory is too long, remove the oldest messages
        brainData[personality]["mod-memory"].pop(0)
        brainData[personality]["mod-memory"].pop(0)
    brainData[personality]["mod-memory"].append({"role": "assistant", "content": content}) # Add Guac/Salsa's response to collective memory
    UpdateBrainData(brainData)
    
    return content

botData = FetchBotData()
serverData = FetchServerData()
brainData = FetchBrainData()

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('GuacBot speech active.')

    @commands.Cog.listener()
    async def on_message(self, message):
        botData = FetchBotData()
        serverData = FetchServerData()
        brainData = FetchBrainData()

        lowerMessage = message.content.lower()
        if "not now, guac" == lowerMessage and message.author.id == 409445517509001216: # For Guac to be told to stop reacting temporarily
            botData["Reactions"]["wait_until"] = time.time() + 300.0
            UpdateBotData(botData)
            await message.channel.send("Sorry, I'll be back in five...")
            return

        if message.content.startswith("$"):
            return

        if botData["Reactions"]["wait_until"] > time.time(): # If Guac was told to stop reacting temporarily
            return
        
        if message.author == self.bot.user: # If Guac is the author of the message
            return
        
        if str(message.author.id) in botData["Reactions"]["global_blacklist"].keys(): # If the author is globally blacklisted
            return
        
        try:
            if not serverData[str(message.guild.id)]["Reactions"]["reactions"]: # If reactions are disabled in the server
                return
            
            if message.author.bot and not serverData[str(message.guild.id)]["Reactions"]["botreactions"]: # If the author is a bot and bot reactions are disabled in the server
                return
            
            if message.guild.id in botData["Reactions"]["server_blacklist"] or message.author.id in serverData[str(message.guild.id)]["Reactions"]["blacklist"]: # If the server or author is blacklisted
                return
        except:
            pass
        
        if self.bot.user.mentioned_in(message) and not message.mention_everyone and message.reference is None: # If Guac is mentioned in the message (but not in a reply or along with everyone)
            await message.channel.send("You can use my slash commands with necessary permissions, use /invite to invite me to your own server, or use this link to join the support server: https://discord.gg/2kgZazXN68")
            return
        elif self.bot.user.mentioned_in(message) and not message.mention_everyone and message.reference is not None:
            if message.author.id == 409445517509001216 and lowerMessage == "delete":
                await message.reference.resolved.delete()
                return

        ai_mentioned = False
        triggered = ""
        for personality in reversed(brainData.keys()):
            for trigger in brainData[personality]["triggers"]:
                if trigger in lowerMessage:
                    ai_mentioned = True
                    triggered = personality
                    break
            
        if (ai_mentioned or (random.randint(1, 50 - botData["Reactions"]["random_limiter"]) == 1)) and str(message.guild.id) in botData["Reactions"]["server_whitelist"].keys(): # If the message is addressed to GuacBot or SalsAI and the server is AI whitelisted
            if botData["Reactions"]["random_limiter"] == 49 or not ai_mentioned:
                botData["Reactions"]["random_limiter"] = 0
                UpdateBotData(botData)

            if triggered == "":
                triggered = "GuacBot"
            
            guacMessage = []

            if ai_mentioned:
                async with message.channel.typing():
                    guacMessage = charLimit(DIDAIMessage(message.content, message.author, triggered))
                    await asyncio.sleep(1)
            else:
                guacMessage = charLimit(DIDAIMessage(message.content, message.author, triggered))
                if guacMessage[0] == "Sorry, my AI capabilities are currently offline. Please try again later.":
                    return
            
            for segment in guacMessage:
                await message.channel.send(segment)
            return
        
        if botData["Reactions"]["random_limiter"] < 49:
            botData["Reactions"]["random_limiter"] += 1
            UpdateBotData(botData)

        if random.randint(1, 3) == 3: # 1 in 3 chance of reacting
            return
        
        speechDict = FetchSpeechData() # Fetch all speech data from JSON file
        
        punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
        uPM = message.content.lower() # Remove punctuation from message (unPunctuatedMessage)
        for char in uPM: 
            if char in punc:
                uPM = uPM.replace(char, " ") 
                
        reactions = []
        
        for trigger in speechDict["triggers"].keys(): # Check for triggers in message and add reactions to list
            if trigger in uPM:
                if uPM == trigger or (uPM.startswith(trigger) and f"{trigger} " in uPM) or (uPM.endswith(trigger) and f" {trigger}" in uPM):
                    reactions.append(speechDict["reactions"][speechDict["triggers"][trigger]])

        #Special: DadBot classic
        if "i’m " in message.content.lower():
            if "I’m" in message.content:
                reactions.append('Hello "' + message.content.split("I’m ")[1] + '", I\'m GuacBot!')
            else:
                reactions.append('Hello "' + message.content.split("i’m ")[1] + '", I\'m GuacBot!')
                
        elif "i'm " in message.content.lower():
            if "I'm" in message.content:
                reactions.append('Hello "' + message.content.split("I'm ")[1] + '", I\'m GuacBot!')
            else:
                reactions.append('Hello "' + message.content.split("i'm ")[1] + '", I\'m GuacBot!')

        elif "i am " in message.content.lower():
            if "I am" in message.content:
                reactions.append('Hello "' + message.content.split("I am ")[1] + '", I\'m GuacBot!')
            else:
                reactions.append('Hello "' + message.content.split("i am ")[1] + '", I\'m GuacBot!')

        #Special: Don't be dry
        if "lmao" == uPM or "lmfao" == uPM:
            reactions.append(message.content)

        #Special: Finishing eachothers sandwiches
        if "what" == message.content.lower():
            finishers = ["...the heck?",
            "...in the world?",
            "...in the goddamn?",
            "...the hell?",
            "...is going on here?",
            "...are you on about?",
            "...is the quadratic formula?"]
            i = len(finishers) - 1
            finisherChoice = random.randint(0, i)
            reactions.append(finishers[finisherChoice])
            
        #Special: How am I supposed to know?
        if "what?" == message.content.lower():
            finishers = ["I have no idea.",
            "Beats me.",
            "Time to get a watch... wait.",
            "Wouldn't you like to know?"]
            i = len(finishers) - 1
            finisherChoice = random.randint(0, i)
            reactions.append(finishers[finisherChoice])
                
        #Special: Love <3
        if "love you" in uPM:
            if "i love you" in uPM:
                reactions.append("I love you too, full homo")
            else:
                reactions.append("I love you too, no homo")

        #Special: NOBODY EXPECTS THE SPANISH INQUISITION
        if "spanish" in uPM:
            if random.randint(1,3) == 1:
                reactions.append("Nobody expects The Spanish Inquisition!")

        #Special: Bloodborne as fuck
        if "micolash" in uPM or "kos" in uPM or "bloodborne" in uPM:
            quotes = ["Ahh, Kos, or some say Kosm... Do you hear our prayers?",
            "No, we shall not abandon the dream.",
            "No one can catch us! No one can stop us now! *cackling*",
            "Ah hah hah ha! Ooh! Majestic! A hunter is a hunter, even in a dream. But, alas, not too fast! The nightmare swirls and churns unending!",
            "As you once did for the vacuous Rom, grant us eyes, grant us eyes. Plant eyes on our brains, to cleanse our beastly idiocy.",
            "The grand lake of mud, hidden now, from sight.",
            "The cosmos, of course!",
            "Let us sit about, and speak feverishly. Chatting into the wee hours of...",
            "Now I'm waking up, I'll forget everything...",
            "AAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHH"]
            i = len(quotes) - 1
            quotechoice = random.randint(0, i)
            reactions.append(quotes[quotechoice])

        #Special: Shakespeare as fuck
        if "shakespeare" in uPM:
            quotes = ["To be, or not to be: that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles, And by opposing end them. To die: to sleep...",
            "This above all: to thine own self be true, And it must follow, as the night the day, Thou canst not then be false to any man.",
            "Cowards die many times before their deaths; The valiant never taste of death but once.",
            "Men at some time are masters of their fates: The fault, dear Brutus, is not in our stars, But in ourselves, that we are underlings.",
            "What's in a name? That which we call a rose By any other word would smell as sweet...",
            "Good night, good night! Parting is such sweet sorrow, That I shall say good night till it be morrow.",
            "All the world's a stage, And all the men and women merely players: They have their exits and their entrances; And one man in his time plays many parts.",
            "The robbed that smiles, steals something from the thief.",
            "Uneasy lies the head that wears the crown.",
            "All that glitters is not gold."]
            i = len(quotes) - 1
            quotechoice = random.randint(0, i)
            reactions.append(quotes[quotechoice])

        #Special: Doomsday weapon
        #if (len(uPM) < 100):
            #quotes = ["fuck", "shit", "damn", "crap", "cunt", "bitch", "ass"]
            #i = len(quotes) - 1
            #quotechoice = random.randint(0, i)
            #reactions.append(quotes[quotechoice])

        #Ban condition (fuck you Daniel)
        if len(reactions) > 7:
            botData["Reactions"]["global_blacklist"].append(message.author.id)
            UpdateBotData(botData)
            await message.channel.send(f"{message.author.mention}, you have been deemed up to no good and are now global banned from my services. DM @guacamolefather if you believe this is a mistake.")
        elif len(reactions) > 0:
            reaction = reactions[random.randint(0, len(reactions) - 1)]
            for segment in charLimit(reaction):
                await message.channel.send(segment)
            
    #~~~ End of if statements ~~~

def setup(bot):
    bot.add_cog(Reaction(bot))