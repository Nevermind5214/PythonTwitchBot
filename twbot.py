from twitchio.ext import commands
from urllib.request import urlopen
import json,csv,random,datetime,re,os

def timestamp(): return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write(szoveg): print(timestamp() + " |  " + str(szoveg))
def gettext(szoveg): return input(timestamp() + " |  " + szoveg)

class Bot(commands.Bot):

	def __init__(self, username, token, channel):
		self.token = token
		self.username = username
		self.channel = "#" + channel
		super().__init__(token=token, prefix='!', initial_channels=[channel])

	async def event_ready(self):
		write(f'Logged in as - {self.nick} at channel: {self.channel[1:]}')
		write(f'User id is: {self.user_id}')
		write("-" * 80)
		await self.connected_channels[0].send("Jelen!")
	
	async def event_message(self, message):
		if message.echo:
			write(self.username + ": " + message.content)
		else:
			write(message.author.display_name + ": " + message.content)
			if "@" + self.username in message.content: await self.connected_channels[0].send("Hali, " + message.author.mention + "! Én csak egy bot vagyok. Az elfogadott parancsokért írd hogy: !parancsok")
			await self.handle_commands(message)

###########################################################################

	@commands.command()
	async def parancsok(self, ctx: commands.Context):
		await ctx.send(str(["!" + parancs for parancs in self.commands]).replace("'","")[1:-1])

	@commands.command()
	async def F(self, ctx: commands.Context, arg=None):
		halalok = {
			"blade" : "I am Malenia, blade of Miquella",
			"ish" : "Meg hal-tál :(",
			"rot" : "Let your flesh be consumed. By the scarlet rot.",
			"allguys" : ":( Fall Guys rbesenHi",
			"nihil" : "NIHIL!",
			"iregiant" : "Aaargh! Aargh!",
			"oolish" : "Put these foolish ambitions to rest.",
			"cruci" : "Lecsaptak ketchupnak",
			"dog" : "OhMyDog Meg lettél kutyulva.. :( OhMyDog",
			"big" : "Úristen, very big!",
			"god" : "God is dead. God remains dead. And we have killed him. How shall we comfort ourselves, the murderers of all murderers? What was holiest and mightiest of all that the world has yet owned has bled to death under our knives: who will wipe this blood off us? What water is there for us to clean ourselves? What festivals of atonement, what sacred games shall we have to invent? Is not the greatness of this deed too great for us? Must we ourselves not become gods simply to appear worthy of it?",
			"paradontax" : "Segít megszüntetni és megelőzni a fogínyvérzést"
		}

		if arg == None: return await ctx.send("Rip in pepperoni.")
		elif arg == "help": await ctx.send(str(["!F " + halal for halal in halalok]).replace("'","")[1:-1])
		elif arg in halalok: await ctx.send(halalok[arg])
		else: await ctx.send('Rip in pepperoni. - nem ismert elhalálozás, "!F help" a halálokért')

	@commands.command()
	async def goldenrule(self, ctx: commands.Context):
		await ctx.send("THE MANY SHALL SUFFER FOR THE SINS OF THE ONE")

	@commands.command()
	async def sör(self, ctx: commands.Context):
		message = "Ma Miller sör van, kedves " + ctx.author.mention + "!"
		await ctx.send(message)

	@commands.command()
	async def nézők(self, ctx: commands.Context):
		await ctx.send(str([chttr.name for chttr in self.connected_channels[0].chatters]).replace("'","")[1:-1])

	#TO DO rewrite with cookie counter support in csv
	@commands.command()
	async def keksz(self, ctx: commands.Context, arg=None):
		if arg == None: return await ctx.send("Jár a keksz, " + ctx.author.mention + "!")
		#from urllib.request import urlopen
		message = "Jár a keksz, " + ctx.author.mention + "!"
		url = "https://tmi.twitch.tv/group/user/" + ctx.channel.__str__()[15:-1] + "/chatters"
		response = urlopen(url)
		viewersjson  = json.loads(response.read())
		if "'" + arg.lower() + "'" in viewersjson["chatters"].__str__():
			message = "Jár a keksz, @" + arg.lower() + "!"
		await ctx.send(message)

###########################################################################

def main():
	conf_file = "config.json"

	if os.path.isfile(conf_file):
		with open(conf_file, "r") as read_file:
			data = json.load(read_file)
		username = data["username"]
		token = data["token"]
		channel = gettext(f'Channel to connect to(hit enter for {data["channel"]}): ')
		if channel == "": channel = data["channel"]
		else:
			with open(conf_file, "w") as outfile: json.dump({"username": username, "token": token, "channel": channel}, outfile, indent = 4)

	else:
		write(f'"{conf_file}" config file not found')

		while True:
			createnew = gettext("Create a new one? (y/n): ")
			if createnew == 'y':
				with open(conf_file, "w") as outfile:
					username = gettext("Username: ")
					token = gettext("Twitch token: ")
					channel = gettext("Channel to connect to: ")
					json.dump({"username": username, "token": token, "channel": channel}, outfile, indent = 4)
					write(f'"{conf_file}" config file created.')
				break
			elif createnew == 'n':
				write(f'This program requires a "{conf_file}" in the same folder to function correctly.')
				os._exit(0)

	bot = Bot(username, token, channel)
	bot.run()

if __name__ == "__main__":
	main()