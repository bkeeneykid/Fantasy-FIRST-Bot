#!/usr/bin/env python3

import discord
from discord.ext import commands
import logging
import json
import random
import tbapy
import html
from io import StringIO

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
    await message.channel.send('Loading events...')
    events = tba.events(year,False,True)
    # print(events)
    embed = discord.Embed()
    for event in events:
        embed.add_field(name=event['name'],value=event['key'], inline=True)
        print(event)
        print(embed.to_dict())
        if len(embed.to_dict()['fields']) > 25:
            break
    edit_message = last_message('Loading events...',message.channel)
    await message.channel.send(embed=embed)
    await edit_message.delete()

def last_message(query, channel):
    for message in channel.history(limit=100):
        if message.content == query:
            return message

@bot.command()
async def createteam(message, name):
    r = await randint(0,255)
    g = await randint(0,255)
    b = await randint(0,255)
    color = await color.from_rgb(r,g,b)
    role = message.channel.guild.create_role(name=name, color = color, mentionable = true)


bot.run(credentials["discord"])
