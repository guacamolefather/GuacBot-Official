import discord, os

def Avocado():
    for fileName in os.listdir('./data'):
        if fileName == 'avocadopog.png':
            tokenFile = open("E:/GUAC_TOKEN.txt", "r")
            return tokenFile.read(70)

async def is_it_me(ctx):
    return (ctx.author.id == 409445517509001216)