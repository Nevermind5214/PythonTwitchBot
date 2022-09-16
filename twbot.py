from twitchio.ext import commands,routines
import json,os,requests
from aioconsole import ainput

def load_json_data(data_file):
	data = {}
	if os.path.isfile(data_file):
		with open(data_file, "r") as read_file: data = json.load(read_file)
	else:
		print(f'"{data_file}" not found!')
		os._exit(0)
	return data

def write_json_data(data_file_name, data):
	with open(data_file_name, "w") as outfile: json.dump(data, outfile, indent = 4)

class Bot(commands.Bot):
	def __init__(self, botdata):
		self.botdata_file_name = botdata
		self.datajsondict = load_json_data(self.botdata_file_name)

		tempchannel = input(f'Channel to connect to(hit enter for {self.datajsondict["config"]["channel"]}): ')
		if tempchannel != "":
			self.datajsondict["config"]["channel"] = tempchannel
			write_json_data(self.botdata_file_name, self.datajsondict)

		self.token = self.datajsondict["config"]["token"]
		self.username = self.datajsondict["config"]["username"]
		self.channel = "#" + self.datajsondict["config"]["channel"]
		self.watchersdict = {}

		super().__init__(token=self.token, prefix='!', initial_channels=[self.channel])
		
	def getviewerlist(self): return sum([value for value in requests.get("http://tmi.twitch.tv/group/user/" + self.channel[1:].lower() + "/chatters").json()["chatters"].values()], [])

	async def event_ready(self):
		self.watchtimer.start()
		print(f'Logged in as - {self.nick} at channel: {self.channel[1:]}')
		print(f'User id is: {self.user_id}')
		print("-" * 80)
		await self.connected_channels[0].send("Jelen!")
		await self.consoleinputhandler()

	async def consoleinputhandler(self):
		while True:
			await self.connected_channels[0].send(await ainput())

	@routines.routine(minutes=2)
	async def watchtimer(self):
		minutes_to_earn_keksz = self.datajsondict["kekszconfig"]["minutes_to_earn_keksz"]
		currentviewerslist = self.getviewerlist()
		if self.username in currentviewerslist: currentviewerslist.remove(self.username)

		for nezoneve in currentviewerslist:
			if nezoneve in self.watchersdict:
				self.watchersdict[nezoneve] += 2
				if self.watchersdict[nezoneve] > minutes_to_earn_keksz:
					self.set_keksz(nezoneve, self.get_keksz(nezoneve) + 1)
					self.watchersdict[nezoneve] -= minutes_to_earn_keksz
					await self.connected_channels[0].send(f"NomNom Gratulálok @{nezoneve}! A  műsor {minutes_to_earn_keksz} perces nézésével kekszhez jutottál!")
			else: self.watchersdict[nezoneve] = 2

		for tempwatchernev in self.watchersdict:
			if tempwatchernev not in currentviewerslist: self.watchersdict.pop(tempwatchernev)

	async def event_message(self, message): #bug in twitcho? message.content seem to lose the first character if it is a ':'
		if message.echo:
			print(self.username + ": " + message.content)
		else:
			print(message.author.display_name + ": " + message.content)
			if "@" + self.username in message.content: await self.connected_channels[0].send("Hali, " + message.author.mention + "! Én csak egy bot vagyok. Az elfogadott parancsokért írd hogy: !parancsok")
			await self.handle_commands(message)

	def get_keksz(self, nev):
		if nev in self.datajsondict["kekszdata"]: return self.datajsondict["kekszdata"][nev]
		else:
			self.set_keksz(nev, self.datajsondict["kekszconfig"]["starter_keksz"])
			return self.get_keksz(nev)
	
	def set_keksz(self, nev, darab):
		self.datajsondict["kekszdata"][nev] = darab
		write_json_data(self.botdata_file_name, self.datajsondict)

	def send_keksz(self, nev_from, nev_to, darab):
		fromdarab = self.get_keksz(nev_from)
		self.set_keksz(nev_from, fromdarab - darab)
		todarab = self.get_keksz(nev_to)
		self.set_keksz(nev_to, todarab + darab)

	@commands.command()
	async def parancsok(self, ctx: commands.Context):
		await ctx.send(str(["!" + parancs for parancs in self.commands]).replace("'","")[1:-1])

	@commands.command()
	async def F(self, ctx: commands.Context, arg=None):
		halalok = {
			"blade" : "I am Malenia, blade of Miquella",
			"ish" : "Meg hal-tál :(",
			"rot" : "Let your flesh be consumed. By the scarlet rot.",
			"allguys" : ":( Fall Guys HeyGuys",
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
		await ctx.send(str(self.getviewerlist()).replace("'","")[1:-1])

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

def main():
	bot = Bot("bot.json")
	bot.run()

if __name__ == "__main__":
	main()