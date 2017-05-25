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

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

@bot.event
async def on_ready():
    print('Logged in as')
    # print(bot.user.name)
    print(bot.user.id)
    print('------')
    # print(tbastatus)
    print('Current Year:'+year)

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command()
async def listevents():
    await bot.say('Loading events...')
    events = tba.events(2017, False)
    print(events)
    await bot.say(html_escape(events))

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

bot.run(credentials["discord"])
