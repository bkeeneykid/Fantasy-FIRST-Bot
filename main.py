#!/usr/bin/env python3

import json
import logging
import random

import discord
import tbapy
from discord.ext import commands
from orator import Model, DatabaseManager, Schema

#Set up automatic message logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#define classes for Orator database handling (one class per table)
class League(Model):
    pass

class Draft(Model):
    pass

#open config
config = open("config.json", "r")
credentials = json.load(config)
config.close()

#connect to database, put connection into models/schema for creation. Settings in config.json
db = DatabaseManager(credentials['database'])
Model.set_connection_resolver(db)
schema = Schema(db)

#Create Database is not exists
if not schema.has_table('leagues'):
    print("Creating Leagues Table")
    with schema.create('leagues') as table:
        table.timestamps()
        table.increments('id')
        table.string('leagueName')
        table.string('leagueEvents').nullable()
        table.string('channelId')
        table.boolean('private')

if not schema.has_table('drafts'):
    print("Creating Drafts Table")
    with schema.create('drafts') as table:
        table.timestamps()
        table.increments('id')
        table.string('draftLeague')
        table.string('eventCode')

description = "A python-based Discord bot for running a fantasy league for the FIRST Robotics Competition"

#initialize bot object
bot = commands.Bot(command_prefix='.', description=description)

tba = tbapy.TBA(credentials["tba"])
year = tba.status()['current_season']

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(f'Current Year:{str(year)}')

@bot.command()
async def listevents(message):
    events = tba.events(year,False,True)
    # print(events)
    embed = discord.Embed()
    for event in events:
        embed.add_field(name=event['name'],value=event['key'], inline=True)
        #print(event)
        #print(embed.to_dict())
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
        await context.channel.send("Please mention the team that you would like to add people to.")
        return
    elif len(context.message.role_mentions) > 1:
        await context.channel.send("Please only mention one team.")
        return
    elif context.message.role_mentions[0].hoist:
        #make sure your mod roles are hoisted, as this is how it checks if that team can be added to.
        await context.channel.send("You are not allowed to invite people to that team.")
        return
    elif not context.message.role_mentions[0] in context.message.author.roles:
        await context.channel.send("You are not in that team, and are not allowed to invite people to it.")
        return
    mentionList = ""
    for member in context.message.mentions:
        if member in context.message.role_mentions[0].members:
            await context.channel.send("Member {0} is already part of that team.".format(member.mention))
            continue
        await member.add_roles(context.message.role_mentions[0])
        if len(mentionList) > 0:
            mentionList += ", "
        mentionList += member.mention

    if mentionList == "":
        return
    await context.message.channel.send("Added member(s) {0} to role {1}".format(mentionList, context.message.role_mentions[0].mention))

@bot.command()
async def createLeague(ctx, leagueName, private=False):
    testLeague = League.where('leagueName', leagueName).get()
    if not testLeague.is_empty():
        await ctx.channel.send("That league already exists. Please try again with a different League Name.")
        return
    if (" " in leagueName) or ("-" in leagueName) or ("_" in leagueName):
        await ctx.channel.send("Prohibited character in league name. Try again without spaces, `_` or `-` characters.")
        return

    # setting up permissions
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
        ctx.message.author: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await ctx.guild.create_text_channel(leagueName, overwrites=overwrites)

    league = League()
    league.leagueName = leagueName
    league.private = private
    league.channelId = channel.id
    league.save()

    if private:
        await ctx.channel.send("League {0} created. A channel is available at {1}. Invite others to your league with `{2}inviteToLeague <users>`.".format(leagueName,channel.mention,bot.command_prefix))
    else:
        await ctx.channel.send("League {0} created. A channel is available at {1}. Others can join this league with `{2}joinLeague {0}`.".format(leagueName,channel.mention,bot.command_prefix))

@bot.command()
async def deleteLeague(ctx, leagueName):
    testLeague = League.where('leagueName', leagueName).take(1).get()
    if len(testLeague) == 0:
        await ctx.channel.send("League not found.")
    elif len(testLeague) > 1:
        await ctx.channel.send("Internal error. Contact commissioner.")
    channelId = testLeague.all()[0].channelId
    channel = ctx.guild.get_channel(int(channelId))
    permissions = ctx.author.permissions_in(channel)
    if permissions.read_messages:
        testLeague.first().delete()
        await channel.delete()
        await ctx.channel.send("League {0} deleted.".format(leagueName))
    else:
        await ctx.channel.send("You do not have permission to delete that league.")



bot.run(credentials["discord"])
