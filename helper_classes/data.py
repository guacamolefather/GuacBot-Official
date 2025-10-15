import time, os, json


def charLimit(big_message): # Splits the message into 2000 character segments for Discord character limit
    if (len(big_message) > 2000):
        split_list = []
        loops = (int) (len(big_message) / 2000)
        x = 0
        for i in range(loops + 1):
            split_list.append(big_message[x:x + 2000])
            x = x + 2000
        return split_list
    else:
        return [big_message]

async def is_it_me(ctx):
    return (ctx.author.id == 409445517509001216)

class Jason:
    def __init__(self):
        self.path = "E:/guac_data/bot_files"
        self.bot_path = self.path + "/system_data"
        self.speech_path = self.path + "/speech_data"

    def avocado(self):
        if "avocado_pog.png" in os.listdir(self.path):
            token_file = open(f"{self.path}/GUAC_TOKEN.txt", "r")
            return token_file.read(70)

    # System data functions

    def initBotData(self):
        data = {}
        with open(f'{self.bot_path}/bot_data.json', 'r') as f:
            data = json.load(f)
            data["hq"]["start_time"] = time.time()
            with open(f'{self.bot_path}/bot_data.json', 'w') as g:
                json.dump(data, g, indent = 4, sort_keys=True)
        return data

    def fetchBotData(self):
        data = {}
        with open(f'{self.bot_path}/bot_data.json', 'r') as f:
            data = json.load(f)
        return data

    def updateBotData(self, data):
        with open(f'{self.bot_path}/bot_data.json', 'w') as g:
            json.dump(data, g, indent = 4, sort_keys=True)

    def fetchServerData(self):
        data = {}
        with open(f'{self.bot_path}/server_data.json', 'r') as f:
            data = json.load(f)
        return data

    def updateServerData(self, data):
        with open(f'{self.bot_path}/server_data.json', 'w') as g:
            json.dump(data, g, indent = 4, sort_keys=True)

    def refreshServerData(self, bot):
        with open(f'{self.bot_path}/server_data.json', 'r') as f:
            data = json.load(f)
            server_id_list = []
            with open(f'{self.bot_path}/server_data.json', 'w') as g:
                for server in bot.guilds:
                    server_id_list.append(str(server.id))
                    if str(server.id) in data.keys():
                        if data[str(server.id)]["hq"]["owner"] != server.owner.name:
                            data[str(server.id)]["hq"]["owner"] = server.owner.name
                        if data[str(server.id)]["hq"]["name"] != str(server.name):
                            data[str(server.id)]["hq"]["name"] = str(server.name)
                    if str(server.id) not in data.keys():
                        data[str(server.id)] = { "hq": { "name": str(server.name), "owner": server.owner.name }, "reaction_cog": { "reactions": True, "bot_reactions": False, "blacklist": [], "role_blacklist": [] }, "economy_cog": { "economy": True } }
                keys_to_pop = []
                for key in data.keys():
                    if key not in server_id_list:
                        keys_to_pop.append(key)
                for pop in keys_to_pop:
                    data.pop(pop)
                json.dump(data, g, indent = 4, sort_keys=True)

    def fetchBankData(self):
        data = {}
        with open(f'{self.bot_path}/bank_data.json', 'r') as f:
            data = json.load(f)
        return data

    def updateBankData(self, data):
        with open(f'{self.bot_path}/bank_data.json', 'w') as g:
            json.dump(data, g, indent = 4, sort_keys=True)

    def verifyBankData(self, member):
        data = {}
        with open(f'{self.bot_path}/bank_data.json', 'r') as f:
            data = json.load(f)

        if str(member.id) not in data["accounts"].keys():
            data["accounts"][str(member.id)] = 5

            with open(f'{self.bot_path}/bank_data.json', 'w') as g:
                json.dump(data, g, indent = 4, sort_keys=True)


    # Speech data functions

    def fetchSpeechData(self):
        data = {}
        with open(f'{self.speech_path}/speech_data.json', 'r') as f:
            data = json.load(f)
        return data

    def updateSpeechData(self, data):
        with open(f'{self.speech_path}/speech_data.json', 'w') as g:
            json.dump(data, g, indent = 4, sort_keys=True)

    def fetchBrainData(self):
        data = {}
        with open(f'{self.speech_path}/DID_data.json', 'r') as f:
            data = json.load(f)
        return data

    def updateBrainData(self, data):
        with open(f'{self.speech_path}/DID_data.json', 'w') as g:
            json.dump(data, g, indent = 4, sort_keys=True)