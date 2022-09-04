from twitchio.ext import commands,routines
import json,datetime,os

def timestamp(): return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write(szoveg): print(timestamp() + " |  " + str(szoveg))
def gettext(szoveg): return input(timestamp() + " |  " + szoveg)

class Bot(commands.Bot):
	starter_keksz = 2
	minutes_to_earn_keksz = 30
	watchersdict = {}
	keksz_file = "keksz.json"
	with open(keksz_file, "r") as kekszfile:
		kekszdict = json.load(kekszfile)

	def __init__(self, username, token, channel):
		self.token = token
		self.username = username
		self.channel = "#" + channel
		super().__init__(token=token, prefix='!', initial_channels=[channel])
	
	
	@routines.routine(minutes=2)
	async def watchtimer(self):
		write("-> Watchtimer event")
		for nezoneve in [chttr.name for chttr in self.connected_channels[0].chatters if chttr.name != self.username]:
			if nezoneve in self.watchersdict:
				self.watchersdict[nezoneve] += 2
				if self.watchersdict[nezoneve] > self.minutes_to_earn_keksz:
					self.set_keksz(nezoneve, self.get_keksz(nezoneve) + 1)
					self.watchersdict[nezoneve] -= self.minutes_to_earn_keksz
					await self.connected_channels[0].send(f"NomNom Gratulálok @{nezoneve}! A  műsor {self.minutes_to_earn_keksz} perces nézésével kekszhez jutottál!")
			else: self.watchersdict[nezoneve] = 2
		for dictnev in self.watchersdict:
			if dictnev not in [chttr.name for chttr in self.connected_channels[0].chatters]: self.watchersdict.pop(dictnev)
		"""
		TO DO more testing, it doesnt seem to work really stable
		@commands.command()
    		async def keksz(self, ctx: commands.Context, arg):
        	#from urllib.request import urlopen
        message = "Jár a keksz, @" + ctx.author.name + "!"
        url = "https://tmi.twitch.tv/group/user/" + ctx.channel.__str__()[15:-1] + "/chatters"
        response = urlopen(url)
        viewersjson  = json.loads(response.read())
        if "'" + arg.lower() + "'" in viewersjson["chatters"].__str__():
            message = "Jár a keksz, @" + arg.lower() + "!"
        await ctx.send(message)
		"""

	async def event_ready(self):
		self.watchtimer.start()
		write("-> Ready event")
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

	def get_keksz(self, nev):
		if nev in self.kekszdict: return self.kekszdict[nev]
		else:
			self.set_keksz(nev, self.starter_keksz)
			return self.get_keksz(nev)
	
	def set_keksz(self, nev, darab):
		self.kekszdict[nev] = darab
		with open(self.keksz_file, "w") as kekszfile:
			json.dump(self.kekszdict, kekszfile, indent=4)
			write("-> Keksz file i/o event")

	def send_keksz(self, nev_from, nev_to, darab):
		write("-> Send keksz event")
		fromdarab = self.get_keksz(nev_from)
		self.set_keksz(nev_from, fromdarab - darab)
		todarab = self.get_keksz(nev_to)
		self.set_keksz(nev_to, todarab + darab)


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
		await ctx.send(str([chttr.name for chttr in self.connected_channels[0].chatters if chttr.name != self.username]).replace("'","")[1:-1])

	#TO DO keksz earning by viewtime
	@commands.command()
	async def keksz(self, ctx: commands.Context, arg=None, arg2=None):
		kekszekszama = self.get_keksz(ctx.author.display_name.lower())
		if arg == None: await ctx.send(f"NomNom {kekszekszama} db kekszed van, {ctx.author.mention}")
		else:
			if arg[0] == '@': arg = arg[1:]
			arg = arg.lower()
			if arg2 == None:
				if kekszekszama > 0:
					self.send_keksz(ctx.author.display_name.lower(), arg, 1)
					await ctx.send(f"NomNom Jár a keksz @{arg}!")
				else: await ctx.send(f":( Nincs sajnos hozzá elég kekszed, {ctx.author.mention}")

			elif arg2.isnumeric() and int(arg2) > 0:
				mennyit = int(arg2)
				if kekszekszama > mennyit:
					self.send_keksz(ctx.author.display_name.lower(), arg, mennyit)
					await ctx.send(f"NomNom Jár {mennyit} db keksz @{arg}!")
				else: await ctx.send(f":( Nincs sajnos hozzá elég kekszed, {ctx.author.mention}")
			else: await ctx.send(f"{ctx.author.mention} Második argumentumnak pozitív egész számot adj meg!")

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