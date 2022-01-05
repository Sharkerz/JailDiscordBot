# bot.py
import os
import time
import discord

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix="!")
jailed = {}

# Parameters
maximum_time_non_admin_jail = 120
vocal_channel_name = "prison"
admin_users = [281126750619172874]


##################
#    COMMANDS    #
##################

@client.event
async def on_ready():
    print("Bot en ligne...")


@client.command()
async def jailinfo(ctx):
    jail_info = f"+---------------+-----------------+\n|     Pseudo        | Temps restant |"
    for user in jailed:
        jail_info += f"\n+---------------+-----------------+\n|     {str(client.get_user(user)).split('#')[0]}       |            {jailed[user]}        |\n +---------------+----------------+"
    await ctx.send(jail_info)


@client.command()
async def jail(ctx, *args):
    # Check arguments
    if len(args) != 2 or not args[1].isdigit():
        await ctx.send("commande pour mettre en prison: jail '@pseudo' 'temps en secondes'")
        return

    # Get vocal channel
    try:
        channel = discord.utils.get(ctx.guild.channels, name=vocal_channel_name)
        channel_id = channel.id
        channel = client.get_channel(channel_id)
    except Exception:
        await ctx.send("⚠️ Le salon vocal prison n'existe pas")
        return

    # Get user to jail
    try:
        member_id = ctx.message.mentions[0].id
        member = await ctx.guild.fetch_member(member_id)
    except Exception:
        await ctx.channel.send("Utilisateur non trouvé")
        return

    # Restrict time
    try:
        jail_time = int(args[1])
        if ctx.message.author.id not in admin_users and int(args[1]) > maximum_time_non_admin_jail:
            await ctx.send(f"Temps maximum: 60 secondes")
            jail_time = 60
    except Exception:
        jail_time = 60

    await ctx.send(f"{args[0]} est en prison pour {jail_time} secondes")
    jailed[member_id] = jail_time

    # Jail
    start_time = time.time()
    timetowait = start_time + int(jail_time)

    while start_time < timetowait:
        try:
            # Stop if the user is not in jail
            if member_id not in jailed:
                return
            jailed[member_id] = int(timetowait - start_time)
            await member.move_to(channel)
            time.sleep(1)
            start_time = time.time()
        except:
            pass
    jailed.pop(member_id, None)
    await ctx.send(f"{args[0]} n'est plus en prison")


@client.command()
async def unjail(ctx, *args):
    # Check arguments
    if len(args) != 1:
        await ctx.send("commande pour sortir de prison: jail '@pseudo' 'temps en secondes'")
        return

    # cancel if the user is in prison
    if ctx.message.author.id in jailed:
        await ctx.send("Refusé, tu es en prison")
        return

    # Get user to unjail
    try:
        member_id = ctx.message.mentions[0].id
    except Exception:
        await ctx.channel.send("Utilisateur non trouvé")
        return

    jailed.pop(member_id, None)
    await ctx.send(f"{args[0]} n'est plus en prison")

client.run(TOKEN)
