import discord, os

def Avocado():
    for fileName in os.listdir('./data'):
        if fileName == 'avocadopog.png':
            tokenFile = open("E:/GuacData/GUAC_TOKEN.txt", "r")
            return tokenFile.read(70)

def charLimit(bigMessage): # Splits the message into 2000 character segments for Discord character limit
    if (len(bigMessage) > 2000):
        splitList = []
        loops = (int) (len(bigMessage) / 2000)
        x = 0
        for i in range(loops + 1):
            splitList.append(bigMessage[x:x + 2000])
            x = x + 2000
        return splitList
    else:
        return [bigMessage]

async def is_it_me(ctx):
    return (ctx.author.id == 409445517509001216)