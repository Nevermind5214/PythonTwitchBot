import requests
from twitchio.ext import commands,routines
from datetime import datetime
from aioconsole import ainput
from JDict import JDict

old_print = print
def timestamped_print(*args, **kwargs): old_print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " |  ", *args, **kwargs)
print = timestamped_print

class Bot(commands.Bot):
	def __init__(self, botconfig, kekszdata):
		self.config = JDict(botconfig)
		self.kekszdata = JDict(kekszdata)

		tempchannel = input(f'Channel to connect to(hit enter for {self.config["channel"]}): ')
		if tempchannel != "": self.config["channel"] = tempchannel

		self.viewersdict = {}
		self.kekszetkaptak = []
		self.kekszannouncementcounter = 0

		super().__init__(token=self.config["token"], prefix='!', initial_channels=["#" + self.config["channel"]])

	def getviewerlist(self): return sum([value for value in requests.get("http://tmi.twitch.tv/group/user/" + self.config["channel"].lower() + "/chatters").json()["chatters"].values()], [])

	async def event_ready(self):
		self.watchtimer.start()
		print(f'Logged in as - {self.nick} at channel: {self.config["channel"]}')
		print(f'User id is: {self.user_id}')
		print("-" * 80)
		#await self.connected_channels[0].send("Jelen!")
		await self.consoleinputhandler()

	async def consoleinputhandler(self):
		while True:
			await self.connected_channels[0].send(await ainput())

	@routines.routine(minutes=2)
	async def watchtimer(self):
		currentviewerslist = self.getviewerlist()
		if self.config["username"].lower() in currentviewerslist: currentviewerslist.remove(self.config["username"])
		if self.config["channel"].lower() in currentviewerslist: currentviewerslist.remove(self.config["channel"])
		

		for nezoneve in currentviewerslist:
			self.viewersdict[nezoneve] = self.viewersdict.get(nezoneve, 0) + 2
			if self.viewersdict[nezoneve] > self.config["minutes_to_earn_keksz"]:
				self.kekszdata[nezoneve] = self.kekszdata.get(nezoneve, self.config["starter_keksz"]) + 1
				self.viewersdict[nezoneve] -= self.config["minutes_to_earn_keksz"]
				self.kekszetkaptak.append("@" + nezoneve)

		self.kekszannouncementcounter += 1
		#keksz announcement
		if self.kekszannouncementcounter >= self.config["minutes_to_earn_keksz"]:
			self.kekszannouncementcounter = 0

			if len(self.kekszetkaptak) > 0:
				self.kekszetkaptak = str(self.kekszetkaptak).replace("'","")[1:-1]
				await self.connected_channels[0].send(f'NomNom Gratulálok {self.kekszetkaptak}! A {self.config["minutes_to_earn_keksz"]} perces jelenléteddel kekszhez jutottál!')
			
			self.kekszetkaptak = []

		tempviewersdict = self.viewersdict.copy()
		for tempviewer in tempviewersdict:
			if tempviewer not in currentviewerslist: del self.viewersdict[tempviewer]

	async def event_message(self, message): #bug in twitcho? message.content seem to lose the first character if it is a ':'
		if message.echo:
			print(self.config["username"] + ": " + message.content)
		else:
			print(message.author.display_name + ": " + message.content)
			if "@" + self.config["username"] in message.content:
				await self.connected_channels[0].send("Hali, " + message.author.mention + "! Én csak egy bot vagyok. Az elfogadott parancsokért írd hogy: !parancsok")
			await self.handle_commands(message)

	def send_keksz(self, nev_from, nev_to, darab):
		if nev_to not in self.kekszdata: self.kekszdata[nev_to] = self.config["starter_keksz"]
		self.kekszdata[nev_from] -= darab
		self.kekszdata[nev_to] += darab

	@commands.command()
	async def keksz(self, ctx: commands.Context, arg=None, arg2=None):
		if ctx.author.display_name.lower() not in self.kekszdata: self.kekszdata[ctx.author.display_name.lower()] = self.config["starter_keksz"]
		kekszekszama = self.kekszdata[ctx.author.display_name.lower()]
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

	@commands.command()
	async def givekeksz(self, ctx: commands.Context, arg=None, arg2=None):
		if ctx.author.display_name.lower() in [self.config["channel"],self.config["username"],"nevermind5214"]:
			if arg == None: await ctx.send(f"Használat: !givekeksz kinek (mennyit)")
			else:
				if arg[0] == '@': arg = arg[1:]
				arg = arg.lower()
				if arg2 == None:
					if arg in self.kekszdata: self.kekszdata[arg] += 1
					else: self.kekszdata[arg] = 1
					await ctx.send(f"NomNom Simon mondja: Jár a keksz @{arg}!")

				elif arg2.isnumeric() and int(arg2) > 0:
					mennyit = int(arg2)
					if arg in self.kekszdata: self.kekszdata[arg] += mennyit
					else: self.kekszdata[arg] = mennyit
					await ctx.send(f"NomNom Simon mondja: Jár {mennyit} db keksz @{arg}!")
				else: await ctx.send(f"{ctx.author.mention} Második argumentumnak pozitív egész számot adj meg!")
		else: await ctx.send(f"{ctx.author.mention} Nem vagy jogosult a parancs használatára!")

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
	async def parancsok(self, ctx: commands.Context):
		await ctx.send(str(["!" + parancs for parancs in self.commands]).replace("'","")[1:-1])

	@commands.command()
	async def nézők(self, ctx: commands.Context):
		await ctx.send(str(self.getviewerlist()).replace("'","")[1:-1])

	@commands.command()
	async def goldenrule(self, ctx: commands.Context):
		await ctx.send("THE MANY SHALL SUFFER FOR THE SINS OF THE ONE")

	@commands.command()
	async def sör(self, ctx: commands.Context):
		message = "Ma Miller sör van, kedves " + ctx.author.mention + "!"
		await ctx.send(message)

def main():
	bot = Bot("config.json", "kekszdata.json")
	bot.run()

if __name__ == "__main__":
	main()