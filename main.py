#!/usr/bin/env python3

import json
import logging
import random
import datetime
from dateutil.parser import parse
import asyncio

import discord
import tbapy
from discord.ext import commands
from orator import Model, DatabaseManager, Schema, SoftDeletes
from orator.orm import has_many, belongs_to

# Set up automatic message logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# define classes for Orator database handling (one class per table
class League(SoftDeletes, Model):
	__dates__ = ['deleted_at']

	@has_many
	def drafts(self):
		return Draft


class Draft(SoftDeletes, Model):
	__dates__ = ['deleted_at']

	@belongs_to('draftLeague')
	def League(self):
		return League


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
		table.soft_deletes()
		table.increments('id')
		table.string('leagueName')
		table.string('channelId')
		table.boolean('private')

if not schema.has_table('drafts'):
	print("Creating Drafts Table")
	with schema.create('drafts') as table:
		table.timestamps()
		table.soft_deletes()
		table.increments('id')
		table.json('picks').nullable()
		table.json('points').nullable()
		table.datetime('startTime').nullable()
		table.string('channelId')
		table.string('draftLeague')
		table.string('eventCode')

description = "A python-based Discord bot for running a fantasy league for the FIRST Robotics Competition"

#initialize bot object
bot = commands.Bot(command_prefix='.', description=description)

tba = tbapy.TBA(credentials["tba"])
year = tba.status()['current_season']

#make commands case insensitive
async def on_message(self, message):
	ctx = await self.get_context(message)
	if ctx.prefix is not None:
		ctx.command = self.commands.get(ctx.invoked_with.lower())
	await self.invoke(ctx)

#background task to check dates
async def checkDates(self):
	await self.wait_until_ready()
	while not self.is_closed():
		print("Checking dates")
		drafts = Draft.where('startTime', '>', datetime.datetime.today() - datetime.timedelta(days=1)).get()
		for draft in drafts:
			league = League.find(draft.draftLeague)
			draftChannel = draft.eventCode + "_" + league.leagueName
			exists = False
			for channel in bot.get_all_channels():
				if draftChannel == channel.name:
					exists = True
			if exists == False:
				await initDraft(draft)
		await asyncio.sleep(5) #task runs every minute

bot.loop.create_task(checkDates(bot))

async def initDraft(draft):
	print("init")
	league = draft.League
	channel = bot.get_channel(int(league.channelId))
	name = draft.eventCode + "_" + league.leagueName
	overwrites = channel.overwrites
	newoverwrites = {}
	for overwrite in overwrites:
		newoverwrites[overwrite[0]] = overwrite[1]
	await channel.guild.create_text_channel(name,overwrites=newoverwrites)


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
async def createLeague(ctx, leagueName, private=True):
	testLeague = League.where('leagueName', leagueName).get()
	if not testLeague.is_empty():
		await ctx.channel.send("That league already exists. Please try again with a different League Name.")
		return
	elif (" " in leagueName) or ("-" in leagueName) or ("_" in leagueName):
		await ctx.channel.send("Prohibited character in league name. Try again without spaces, `_` or `-` characters.")
		return
	elif len(leagueName) > 8:
		await ctx.channel.send("Your league name is too long. Please shorten it under 9 characters.")
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
		await ctx.channel.send("League {0} created. A channel is available at {1}. Invite others to your league with `{2}inviteLeague {0} <roles>`.".format(leagueName,channel.mention,bot.command_prefix))
	else:
		await ctx.channel.send("League {0} created. A channel is available at {1}. Others can join this league with `{2}joinLeague {0}`.".format(leagueName,channel.mention,bot.command_prefix))

@bot.command()
async def inviteLeague(ctx,leagueName=None):
	if len(ctx.message.role_mentions) == 0:
		await ctx.channel.send("Please mention the team that you would like to add to this league.")
		return
	elif len(ctx.message.role_mentions) > 1:
		await ctx.channel.send("Please only mention one team.")
		return
	elif ctx.message.role_mentions[0].hoist:
		#make sure your mod roles are hoisted, as this is how it checks if that team can be added to.
		await ctx.channel.send("You are not allowed to invite that role.")
		return
	elif len(ctx.message.mentions) > 0:
		await ctx.channel.send("You cannot invite individual members to a league. Please create a team using `.createTeam <teamName>` and try again to add that individual.")
		return
	testLeague = await findLeague(ctx, leagueName)
	channel = ctx.guild.get_channel(int(testLeague.channelId))
	for member in ctx.message.role_mentions[0].members:
		if member in channel.members:
			await ctx.channel.send("There is already a user of that team in that league, and as such, they cannot join this league.")
			return
	if not ctx.author in channel.members:
		await ctx.channel.send("You are not part of that League, and as such you cannot invite people to it.")
		return
	await channel.set_permissions(ctx.message.role_mentions[0], read_messages=True)
	if not ctx.channel == channel:
		await ctx.channel.send("{0} has been added to the League {1}.".format(ctx.message.role_mentions[0].mention, testLeague.leagueName))
	await channel.send("{0} has been added to this league.".format(ctx.message.role_mentions[0].mention))


@bot.command()
async def deleteLeague(ctx, leagueName):
	testLeague = League.where('leagueName', leagueName).take(1).get()
	if len(testLeague) == 0:
		await ctx.channel.send("League not found.")
		return
	elif len(testLeague) > 1:
		await ctx.channel.send("Internal error. Contact commissioner.")
		return
	channelId = testLeague.first().channelId
	channel = ctx.guild.get_channel(int(channelId))
	permissions = ctx.author.permissions_in(channel)
	if permissions.read_messages:
		testLeague.first().delete()
		await channel.delete()
		await ctx.channel.send("League {0} deleted.".format(leagueName))
	else:
		await ctx.channel.send("You do not have permission to delete that league.")

@bot.command()
async def eventLeague(ctx, eventCode, leagueName=None):
	testLeague = await findLeague(ctx,leagueName)
	if eventCode == "*":
		await ctx.channel.trigger_typing()
		await ctx.channel.send("Adding all events is very intensive. Please wait 30 seconds or more.")
		for event in tba.events(year,True):
			draft = Draft()
			draft.draftLeague = testLeague.id
			draft.eventCode = event
			draft.save()
			print(event)
		await ctx.channel.send("All events added to league {0}.".format(testLeague.leagueName))
		return
	else:
		try:
			Draft.where("draftLeague", testLeague.id).where("eventCode",str(year) + eventCode).first_or_fail()
			await ctx.channel.send("That event is already in this league.")
			return
		except:
			pass
		#make sure the event actually exists
		try:
			tba.event(str(year) + eventCode)
		except:
			await ctx.channel.send("Event not found.")
			return
		draft = Draft()
		draft.draftLeague = testLeague.id
		draft.eventCode = str(year) + eventCode
		draft.save()
		await ctx.channel.send("Event {0} added to league {1}.".format(eventCode, testLeague.leagueName))
		return

@bot.command()
async def deleteDraft(ctx, eventCode, leagueName=None):
	testLeague = await findLeague(ctx, leagueName)
	if eventCode == "*":
		Draft.where("draftLeague", testLeague.id).delete()
		await ctx.channel.send("All drafts deleted. I hope you meant to do that.")
		return
	try:
		testDraft = Draft.where("draftLeague", testLeague.id).where("eventCode", str(year) + eventCode).first_or_fail()
		Draft.destroy(testDraft.id)
		await ctx.channel.send("Event {0} deleted from league {1}.".format(eventCode, testLeague.leagueName))
	except:
		await ctx.channel.send("Draft not found.")
		return


async def findLeague(ctx, leagueName = None):
	if leagueName is None or leagueName[0] == "<":
		channelName = ctx.channel.name
		testLeague = League.where('leagueName', channelName).take(1).get()
		if testLeague.is_empty():
			await ctx.channel.send("You did not specific a league, and this is not inside a league channel. Please try again.")
			return None
		else:
			return testLeague.first()
	else:
		return League.where('leagueName', leagueName).take(1).get().first()


async def cleanEvent(eventCode):
	if eventCode[0:1] == "20":
		return eventCode
	else:
		return str(year) + eventCode


@bot.command()
async def startDraft(ctx, eventCode, date=None, leagueName = None):
	if date == None:
		draftTime = datetime.datetime.today()+datetime.timedelta(minutes=30)
	else:
		draftTime = parse(date)
	testLeague = await findLeague(ctx, leagueName)
	eventCode = await cleanEvent(eventCode)
	testDraft = Draft.where('draftLeague', testLeague.id).where('eventCode', eventCode).first_or_fail()
	if draftTime < datetime.datetime.today():
		await ctx.channel.send("That time is before the current time.")
		return
	testDraft.startTime = draftTime
	testDraft.save()
	await ctx.channel.send("The draft for {0} will start on {1}".format(testLeague.leagueName, draftTime))


bot.run(credentials["discord"])
