# Fantasy-FIRST-Bot
A python-based Discord bot for running a fantasy league for the FIRST Robotics Competition

You can view the latest documentation for the bot below. It's not guaranteed that these commands will work, these are 
the ideal commands if/when the bot is fully functional.

This bot is designed to be used on the official discord server. You can join this server [here](http://www.discord.gg/3EfyXd7). 
While it will probably work on other servers, I will not provide support for other servers and will only test it on the 
official server.

## Commands
### `.commandName <requiredParameter> (optionalParameter)`
### `.createTeam <TeamName> (color)`
Creates a role for you. You can have as many teams as you would like. If your team name is more than one word, put it in
double quotes (“). Color is a hexadecimal value (eg. #FFFFFF). NOTE. Color is currently not implemented, and it just 
randomly chooses a color. If you want your color changed, please contact the commissioner.
### `.editTeam <TeamMention> (TeamName) (color)`
Similar to create team, you can edit your team’s name and color here. First, mention your team you’d like to edit with a 
@, then put the name or color in any order. Your team name in this command must be surrounded by quotes, and the color 
value must start with #. NOTE. This command is currently not implemented. If you need your team changed, please contact 
the commissioner.
### `.inviteTeam <TeamMention> <User(s)>`
Invites members to a team you are apart of. First, mention your team you’d like to invite someone to using @, then 
mention all the users you’d like to invite to that team. It does not matter whether the team or the user is mentioned 
first.
### `.createLeague <LeagueCode> <Private>`
Creates a league. This by itself doesn’t do anything, you have to add events to your league with the .eventLeague 
command. The league code must be 8 characters or less and have no spaces. You must create a league for any draft,
even if the league only will have one event.
### `.deleteLeague <LeagueCode>`
Pretty self explanatory. You can only delete a league if you're in it. It only soft-deletes, so if someone's an idiot,
the admins will be able to reinitalize it with the prior data.
### `.eventLeague <LeagueCode> <EventCode>`
Adds events to a league which you are in. Event code must be the event code listed on TBA or FIRST’s website, with or 
without the year. You can also add district codes to add all of that district’s events or a championship’s code to add 
all of that championship’s divisions. An asterisk adds all events. Don't be dumb and add events you don't mean to, cause
it's a pain to remove. Also don't add an event twice. 
### `.joinLeague (TeamMention) <LeagueCode>`
Adds yourself to a league. You cannot join a league after the drafts have started. You must state your team if you have 
joined more than one. You cannot have a person be in multiple teams in the same league, however people can still be in 
more than one league as long as any of their teams do not join the same league.
### `.startDraft <DraftCode>`
Starts a draft for a specific draft. Draft codes are formatting like the following. `leagueCode.eventCode`. Event code 
is without year, since you must be drafting the current year. This will create a channel for the draft and start on the 
next hour. The bot will tag the teams in the draft when it is their draft.
### `.draftTeam <DraftCode> <teamNumber>`
This command must be used inside a draft channel, created by .startDraft or use the draft code identifier. This will 
pick the team you have chosen. If it is not your turn to pick, it will attempt to pick that team when it becomes your 
turn, and if it cannot, it will tag you to pick a new team. If the team has already been picked, you will have to 
execute this command again with a new team.
### `.updateDraft (DraftCode)`
This command must be used inside a draft channel, created by .startDraft or use the draft code identifier. This command 
will pull the latest data from The Blue Alliance and update the teams attending, and if the event has ended, will score 
the event. This will then print out the latest information about the draft, whether be the current team list that has 
been picked and hasn’t been picked, or the scoring for the event.
### `.swapTeam (DraftCode) <PickedTeam> <NewTeam>`
This command must be used inside a draft channel, created by .startDraft or use the draft code identifier. You must have 
picked the first team or this will return an error. To swap a team with another team, you must create a dummy team that 
you will swap out, as there’s no way currently to swap with another picked team.
### `.leagueStandings (LeagueCode)`
This command must either be executed inside a channel associated with a league, either a draft channel or league channel 
or use a League code. This will generate a leaderboard for all the teams in a league.
## League/Draft Channel Info
When you create a league, a central channel for that league will be created. All bot commands should be put in there 
relating to that league. This is also for league-related discussion too. Whenever you start a draft, a channel will be 
created for that draft with the channel name as the draft code (outlined above). When the draft has finished, that draft 
channel will be deleted. Even if the draft channel is deleted, you can still use the .swapTeam and .updateDraft commands 
to modify the draft. Both these commands will print out the draft standings when executed.
