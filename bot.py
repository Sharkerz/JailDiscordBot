import os
import time
import discord

from discord.ext import commands
from boto.s3.connection import S3Connection

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
jailed = {}

# Parameters
maximum_time_non_admin_jail = 1000
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
    if len(jailed) == 0:
        jail_info = "La prison est vide"
    else:
        jail_info = f"+---------------+-----------------+\n|     Pseudo        | Temps restant |"
        for user in jailed:
            jail_info += f"\n+---------------+-----------------+\n|     {str(client.get_user(user)).split('#')[0]}       |            {jailed[user]}        |\n +---------------+----------------+"
    await ctx.send(jail_info)


@client.command()
async def jail(ctx, *args):
    # Help command
    if args[0] == "help":
        await ctx.send(f"Commandes: \n - `!jail @user (time)` => Mettre en prison \n - `!unjail @user` => Sortir de prison \n - `!jailinfo` => Voir qui est en prison \n\n ℹ️ Temps maximum: {maximum_time_non_admin_jail} secondes")
        return

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

    # Check if the user is not already jailed
    if member_id in jailed:
        await ctx.channel.send(f"{args[1]} est deja en prison !")
        return

    # Get channel where the user to jail was
    old_channel = None if not member.voice else member.voice.channel

    # Restrict time
    try:
        jail_time = int(args[1])
        if ctx.message.author.id not in admin_users and int(args[1]) > maximum_time_non_admin_jail:
            await ctx.send(f"Temps maximum: {maximum_time_non_admin_jail} secondes")
            jail_time = 60
    except Exception:
        jail_time = 60

    await ctx.send(f"{args[0]} est en prison pour {jail_time} secondes")
    jailed[member_id] = {'time': jail_time, 'froma': 'from'}

    # Jail
    start_time = time.time()
    timetowait = start_time + int(jail_time)

    while start_time < timetowait:
        try:
            # Stop if the user is not in jail
            if member_id not in jailed:
                return
            jailed[member_id]['time'] = int(timetowait - start_time)
            await member.move_to(channel)
            time.sleep(1)
            start_time = time.time()
        except:
            pass
    jailed.pop(member_id, None)

    if old_channel is not None:
        await member.move_to(client.get_channel(old_channel.id))
        await ctx.send(f"{args[0]} n'est plus en prison    ➡️  retour dans le channel {old_channel}")
    else:
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

# User not in jailed join the jail channel
@client.event
async def on_voice_state_update(member, before, after):
    if after.channel.name == vocal_channel_name and member.id not in jailed:
        await member.move_to(before.channel)

client.run(os.environ['DISCORD_TOKEN'])
