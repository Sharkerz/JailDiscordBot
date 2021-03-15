# bot.py
import os
import time

import discord
from dotenv import load_dotenv
from discord.utils import get

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_message(message):
    free = True

    if message.author == client.user:
     return


    #jail
    if message.content.lower().startswith('jail'):
        list_word = str(message.content).split()

        if(len(list_word) == 1):
            await message.channel.send("commande pour mettre en prison: jail '@pseudo' 'temps en secondes'")

        else:
            # pseudo
            user = list_word[1]

            # time en prison
            if (len(list_word) == 3):
                time_to_decrypt = list_word[2]
                timeC = ""

                for i in time_to_decrypt:
                    if i.isdigit():
                        timeC += i
                if (timeC == ""):
                    timeC = "60"

                if(int(timeC) > 1000):
                    await message.channel.send("Sale fou c'est 1000 secondes maximum")
                    timeC = "60"

            else:
                timeC = "60"

            channel = discord.utils.get(message.guild.channels, name="prison")
            channel_id = channel.id
            channel = client.get_channel(channel_id)
            try:
                member_id = message.mentions[0].id
                member = await message.guild.fetch_member(member_id)
            except:
                await message.channel.send("@ mieux bouffon")
                return

            await message.channel.send(user + " est en prison pour " + timeC + " secondes")

            start = time.time()
            timetowait = start + int(timeC)

            while start < timetowait:
                try:
                    await member.move_to(channel)
                    time.sleep(1)
                    start = time.time()
                except:
                    pass
                # # unjail
                # if message.content == 'unjail ':
                #     list_word = str(message.content).split()
                #
                #     if (len(list_word) == 1):
                #         await message.channel.send("commande pour sortir de prison: unjail '@pseudo'")
                #
                #     if(list_word[1] == user):
                #         await message.channel.send(user + "n'est plus en prison")
                #         break

            await message.channel.send(user + "n'est plus en prison")


client.run(TOKEN)

