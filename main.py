#!/usr/bin/env python3

import discord
from discord.ext import commands
import logging
import json
import random
import tbapy
import html
from io import StringIO
import time

config = open("config.txt", "r")
credentials = json.load(config)
config.close()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = "A python-based Discord bot for running a fantasy league for the FIRST Robotics Competition"

bot = commands.Bot(command_prefix='.', description=description, pm_help=True)

tba = tbapy.TBA(credentials["tba"])
tbastatus = tba.status()
year = tbastatus['current_season']

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    # print(tbastatus)
    print('Current Year:'+ str(year))

@bot.command()
async def listevents(message):
    with message.channel.typing():
        events = tba.events(year,False,True)
        # print(events)
        embed = discord.Embed()
        for event in events:
            embed.add_field(name=event['name'],value=event['key'], inline=True)
            print(event)
            print(embed.to_dict())
            if len(embed.to_dict()['fields']) > 25:
                break
        await message.channel.send(embed=embed)


@bot.command()
async def createteam(message, name):
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    roleColor = discord.Color.from_rgb(r,g,b)
    newRole = await message.channel.guild.create_role(name=name, color = roleColor, mentionable = True)
    await message.author.add_roles(newRole)
    await message.channel.send("Created team {0}. Please invite others to the team with {1}inviteTeam {0} <username>".format(newRole.mention, bot.command_prefix))

@bot.command()
async def inviteteam(context):
    if len(context.message.role_mentions) == 0:
        await context.message.channel.send("Please mention the team that you would like to add people to.")
        return
    elif len(context.message.role_mentions) > 1:
        await context.message.channel.send("Please only mention one team.")
        return
    elif context.message.role_mentions[0].hoist:
        #make sure your mod roles are hoisted, as this is how it checks if that team can be added to.
        await context.message.channel.send("You are not allowed to invite people to that role.")
        return
    elif not context.message.role_mentions[0] in context.message.author.roles:
        await context.message.channel.send("You are not in that team, and are not allowed to invite people to it.")
        return
    mentionList = ""
    for member in context.message.mentions:
        if member in context.message.role_mentions[0].members:
            await context.message.channel.send("Member {0} already has that role.".format(member.mention))
            continue
        await member.add_roles(context.message.role_mentions[0])
        if len(mentionList) > 0:
            mentionList += ", "
        mentionList += member.mention

    if mentionList == "":
        return
    await context.message.channel.send("Added member(s) {0} to role {1}".format(mentionList, context.message.role_mentions[0].mention))

bot.run(credentials["discord"])
