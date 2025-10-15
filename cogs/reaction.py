import time, random #, asyncio

from discord.ext import commands
from llama_cpp import Llama

from helper_classes.data import *
from helper_classes.nlp import *


jason = Jason()
#bot_data = jason.fetchBotData()
#server_data = jason.fetchServerData()
#brain_data = jason.fetchBrainData()

def llmMessage(message, personality, sending_message):
    name = message.author.name
    if message.author.id == 562372596008484875: # For Auntie
        name = "Sophie"

    brain_data = jason.fetchBrainData() # fetch all AI data
    
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    content = "Sorry, something must have gone wrong. Please try again later."

    for loop_personality in brain_data.keys():
        if loop_personality != "lookup":
            brain_data[loop_personality]["mod_memory"].append({"role": "user", "content": f"{current_time} - {message.guild} server in the #{message.channel} channel - {name} says: {message.content}"}) # Add most recent message to memory

    if sending_message:
        NLP_intent = Testing().response(message.content) # Look into resource impact of this
        online = False
        lookup = ""
        if NLP_intent.startswith("lookup"):
            online = True

            query_words = [
                word for word in message.content.lower().split()
                if not any(word.startswith(trigger) for trigger in brain_data[personality]["triggers"])
                ]
            query = " ".join(query_words)
            
            if NLP_intent.endswith("simple"):
                lookup = search(message.content, 1)
            elif NLP_intent.endswith("complex"):
                lookup = search(message.content, 2)

            brain_data[personality]["mod_memory"].append({"role":"user","content":f"""The following website content from query "{query}" is only visible to you, {personality}, and is to be used to help answer the question: {lookup}"""})

        messages = brain_data[personality]["core_memory"] # Add personality specific memory
        messages = messages + brain_data[personality]["mod_memory"] # Combine personality memory with contemporary memory
        
        try:
            if online:
                pass # Using a separate model for lookup summaries is currently disabled

                #model_path = "E:/guac_data/llm_files/" + brain_data["lookup"]["model_info"]["model"]
                #llm = Llama(model_path=model_path,
                #        n_gpu_layers=brain_data["lookup"]["model_info"]["gpu_layers"],
                #        n_ctx=brain_data["lookup"]["model_info"]["context_size"],
                #        seed=random.random())
                #summary = llm.create_chat_completion(messages=brain_data["lookup"]["core_memory"] + [{"role":"user","content":lookup}])
                #messages = messages + [{"role":"user", "content":f"The following information is only visible to you, {personality}, and is to be used to help answer the question: {summary['choices'][0]['message']['content']}"}]

            model_path = "E:/guac_data/llm_files/" + brain_data[personality]["model_info"]["model"]
            
            llm = Llama(model_path=model_path,
                        n_gpu_layers=brain_data[personality]["model_info"]["gpu_layers"],
                        n_ctx=brain_data[personality]["model_info"]["context_size"],
                        seed=random.random())

            response = llm.create_chat_completion(messages=messages)
        except Exception as e:
            return f"Sorry, my AI capabilities are currently offline. Exception: {e}"
        
        # Extracting 'content' value from response and updating Guac's memory
        content = response['choices'][0]['message']['content']

        for loop_personality in brain_data.keys():
            if loop_personality != "lookup":
                if loop_personality == personality:
                    brain_data[personality]["mod_memory"].append({"role": "assistant", "content": content}) # Add Guac/Salsa's response to their own contemporary memory
                else:
                    brain_data[loop_personality]["mod_memory"].append({"role": "user", "content": f"{current_time} - {message.guild} server in the #{message.channel} channel - {personality} says: {content}"}) # Add Guac/Salsa's response to other AIs' contemporary memory

    for loop_personality in brain_data.keys():
        if loop_personality != "lookup":
            mod_len = len(brain_data[loop_personality]["mod_memory"])
            if mod_len > 20: # If memory is too long, remove the oldest messages
                for i in range(mod_len - 20):
                    brain_data[loop_personality]["mod_memory"].pop(0)

    jason.updateBrainData(brain_data)
    return content

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        #Trainer().buildAndTrainModel() # Need to figure out how to run this only when intents.json is updated
        print('GuacBot speech active.')

    @commands.Cog.listener()
    async def on_message(self, message):
        bot_data = jason.fetchBotData()
        server_data = jason.fetchServerData()
        brain_data = jason.fetchBrainData()

        lower_message = message.content.lower()
        if "not now, guac" == lower_message and message.author.id == 409445517509001216: # For Guac to be told to stop reacting temporarily
            bot_data["reaction_cog"]["wait_until"] = time.time() + 300.0
            jason.updateBotData(bot_data)
            await message.channel.send("Sorry, I'll be back in five...")
            return

        if message.content.startswith("$") and message.author.id == 409445517509001216:
            return

        if bot_data["reaction_cog"]["wait_until"] > time.time(): # If Guac was told to stop reacting temporarily
            return
        
        if message.author == self.bot.user: # If Guac is the author of the message
            return
        
        if str(message.author.id) in bot_data["reaction_cog"]["global_blacklist"].keys(): # If the author is globally blacklisted
            return
        
        try:
            if not server_data[str(message.guild.id)]["reaction_cog"]["reactions"]: # If reactions are disabled in the server
                return
            
            if message.author.bot and not server_data[str(message.guild.id)]["reaction_cog"]["bot_reactions"]: # If the author is a bot and bot reactions are disabled in the server
                return
            
            if message.guild.id in bot_data["reaction_cog"]["server_blacklist"] or message.author.id in server_data[str(message.guild.id)]["reaction_cog"]["blacklist"]: # If the server or author is blacklisted
                return
        except:
            pass
        
        if self.bot.user.mentioned_in(message) and not message.mention_everyone and message.reference is None: # If Guac is mentioned in the message (but not in a reply or along with everyone)
            await message.channel.send("You can use my slash commands with necessary permissions, use /invite to invite me to your own server, or use this link to join the support server: https://discord.gg/2kgZazXN68")
            return
        elif self.bot.user.mentioned_in(message) and not message.mention_everyone and message.reference is not None:
            if message.author.id == 409445517509001216 and lower_message == "delete":
                await message.reference.resolved.delete()
                return

        personality_mentioned = False
        triggered = ""
        for personality in reversed(brain_data.keys()):
            for trigger in brain_data[personality]["triggers"]:
                if trigger in lower_message:
                    personality_mentioned = True
                    triggered = personality
                    break
            
        if (personality_mentioned or (random.randint(1, 50 - bot_data["reaction_cog"]["random_limiter"]) == 1)) and str(message.guild.id) in bot_data["reaction_cog"]["server_whitelist"].keys(): # If the message is addressed to GuacBot or SalsAI and the server is AI whitelisted
            if bot_data["reaction_cog"]["random_limiter"] == 49 or not personality_mentioned:
                bot_data["reaction_cog"]["random_limiter"] = 0
                jason.updateBotData(bot_data)

            if triggered == "":
                triggered = "GuacBot"
            
            personality_message = []

            if personality_mentioned:
                async with message.channel.typing():
                    personality_message = charLimit(llmMessage(message, triggered, True))
                    #await asyncio.sleep(1) # Simulate typing for at least 1 second, but may not be necessary with more intensive LLM calls
            else:
                personality_message = charLimit(llmMessage(message, triggered, True))
                if personality_message[0] == "Sorry, my AI capabilities are currently offline. Please try again later.":
                    return
            
            for segment in personality_message:
                await message.channel.send(segment)
            return
        else:
            llmMessage(message, "GuacBot", False)
        
        if bot_data["reaction_cog"]["random_limiter"] < 49:
            bot_data["reaction_cog"]["random_limiter"] += 1
            jason.updateBotData(bot_data)

        if random.randint(1, 3) == 3: # 1 in 3 chance of reacting
            return
        
        speech_dict = jason.fetchSpeechData() # fetch all speech data from JSON file
        
        punc = r"""!()-[]{};:'"\, <>./?@#$%^&*_~"""
        unpunc_lower_message = message.content.lower() # Remove punctuation from message (unPunctuatedMessage)
        for char in unpunc_lower_message: 
            if char in punc:
                unpunc_lower_message = unpunc_lower_message.replace(char, " ") 
                
        reactions = []
        
        for trigger in speech_dict["triggers"].keys(): # Check for triggers in message and add reactions to list
            if trigger in unpunc_lower_message:
                if unpunc_lower_message == trigger or (unpunc_lower_message.startswith(trigger) and f"{trigger} " in unpunc_lower_message) or (unpunc_lower_message.endswith(trigger) and f" {trigger}" in unpunc_lower_message):
                    reactions.append(speech_dict["reactions"][speech_dict["triggers"][trigger]])

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
        if "lmao" == unpunc_lower_message or "lmfao" == unpunc_lower_message:
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
            finisher_choice = random.randint(0, i)
            reactions.append(finishers[finisher_choice])
            
        #Special: How am I supposed to know?
        if "what?" == message.content.lower():
            finishers = ["I have no idea.",
            "Beats me.",
            "Time to get a watch... wait.",
            "Wouldn't you like to know?"]
            i = len(finishers) - 1
            finisher_choice = random.randint(0, i)
            reactions.append(finishers[finisher_choice])
                
        #Special: Love <3
        if "love you" in unpunc_lower_message:
            if "i love you" in unpunc_lower_message:
                reactions.append("I love you too, full homo")
            else:
                reactions.append("I love you too, no homo")

        #Special: NOBODY EXPECTS THE SPANISH INQUISITION
        if "spanish" in unpunc_lower_message:
            if random.randint(1,3) == 1:
                reactions.append("Nobody expects The Spanish Inquisition!")

        #Special: Bloodborne as fuck
        if "micolash" in unpunc_lower_message or "kos" in unpunc_lower_message or "bloodborne" in unpunc_lower_message:
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
            quote_choice = random.randint(0, i)
            reactions.append(quotes[quote_choice])

        #Special: Shakespeare as fuck
        if "shakespeare" in unpunc_lower_message:
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
            quote_choice = random.randint(0, i)
            reactions.append(quotes[quote_choice])

        #Special: Doomsday weapon
        #if (len(unpunc_lower_message) < 100):
            #quotes = ["fuck", "shit", "damn", "crap", "cunt", "bitch", "ass"]
            #i = len(quotes) - 1
            #quote_choice = random.randint(0, i)
            #reactions.append(quotes[quote_choice])

        #Ban condition (fuck you Daniel)
        if len(reactions) > 7:
            bot_data["reaction_cog"]["global_blacklist"].append(message.author.id)
            jason.updateBotData(bot_data)
            await message.channel.send(f"{message.author.mention}, you have been deemed up to no good and are now globally banned from my services. DM @guacamolefather if you believe this is a mistake.")
        elif len(reactions) > 0:
            reaction = reactions[random.randint(0, len(reactions) - 1)]
            for segment in charLimit(reaction):
                await message.channel.send(segment)
            
    #~~~ End of if statements ~~~

def setup(bot):
    bot.add_cog(Reaction(bot))