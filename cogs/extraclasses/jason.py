import json
import time
import discord
import discord.ext

def InitBotData():
    data = {}
    with open('data/bot_data.json', 'r') as file:
        data = json.load(file)
        data["HQ"]["start_time"] = time.time()
        with open('data/bot_data.json', 'w') as fileO:
            json.dump(data, fileO, indent = 4, sort_keys=True)
        fileO.close()
    file.close()
    return data

def FetchBotData():
    data = {}
    with open('data/bot_data.json', 'r') as file:
        data = json.load(file)
    file.close()
    return data

def UpdateBotData(data):
    with open('data/bot_data.json', 'w') as fileO:
        json.dump(data, fileO, indent = 4, sort_keys=True)
    fileO.close()

def FetchSpeechData():
    data = {}
    with open('data/speech_data.json', 'r') as file:
        data = json.load(file)
    file.close()
    return data

def UpdateSpeechData(data):
    with open('data/speech_data.json', 'w') as fileO:
        json.dump(data, fileO, indent = 4, sort_keys=True)
    fileO.close()

def FetchBrainData():
    data = {}
    with open('data/DID_data.json', 'r') as file:
        data = json.load(file)
    file.close()
    return data

def UpdateBrainData(data):
    with open('data/DID_data.json', 'w') as fileO:
        json.dump(data, fileO, indent = 4, sort_keys=True)
    fileO.close()

def FetchServerData():
    data = {}
    with open('data/server_data.json', 'r') as file:
        data = json.load(file)
    file.close()
    return data

def UpdateServerData(data):
    with open('data/server_data.json', 'w') as fileO:
        json.dump(data, fileO, indent = 4, sort_keys=True)
    fileO.close()

def RefreshServerData(bot):
    with open('data/server_data.json', 'r') as file:
        data = json.load(file)
        serverIDs = []
        with open('data/server_data.json', 'w') as fileO:
            for server in bot.guilds:
                serverIDs.append(str(server.id))
                if str(server.id) in data.keys():
                    if data[str(server.id)]["HQ"]["owner"] != server.owner.name:
                        data[str(server.id)]["HQ"]["owner"] = server.ownerr.name
                    if data[str(server.id)]["HQ"]["name"] != str(server.name):
                        data[str(server.id)]["HQ"]["name"] = str(server.name)
                if str(server.id) not in data.keys():
                    data[str(server.id)] = { "HQ": { "name": str(server.name), "owner": server.owner.name }, "Reactions": { "reactions": True, "botreactions": False, "blacklist": [], "roleblacklist": [] }, "Economy": { "economy": True } }
            keysToPop = []
            for key in data.keys():
                if key not in serverIDs:
                    keysToPop.append(key)
            for pop in keysToPop:
                data.pop(pop)
            json.dump(data, fileO, indent = 4, sort_keys=True)
        fileO.close()
    file.close()

def FetchBankData():
    data = {}
    with open('data/bank_data.json', 'r') as file:
        data = json.load(file)
    file.close()
    return data

def UpdateBankData(data):
    with open('data/bank_data.json', 'w') as fileO:
        json.dump(data, fileO, indent = 4, sort_keys=True)
    fileO.close()

def HasBankAccount(member):
    data = {}
    with open('data/bank_data.json', 'r') as file:
        data = json.load(file)
    file.close()

    if str(member.id) not in data["accounts"].keys():
        data["accounts"][str(member.id)] = 5

        with open('data/bank_data.json', 'w') as fileO:
            json.dump(data, fileO, indent = 4, sort_keys=True)
        fileO.close()