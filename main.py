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
print(credentials)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = "A python-based Discord bot for running a fantasy league for the FIRST Robotics Competition"

bot = commands.Bot(command_prefix=':', description=description)

tba = tbapy.TBA(credentials["tba"])
tbastatus = tba.status()
year = tbastatus['current_season']

@bot.event
async def on_ready():
    print('Logged in as')
    # print(bot.user.name)
    print(bot.user.id)
    print('------')
    # print(tbastatus)
    print('Current Year:'+ str(year))

@bot.command()
async def listevents():
    await bot.say('Loading events...')
    events = tba.events(year, True)
    total = ""
    for event in events:
        total = total + event
    print(total)
    await bot.say(total)


bot.run(credentials["discord"])
