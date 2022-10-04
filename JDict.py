import json, os

class JDict(dict):
	def __init__(self, jfile=None, parent=None):
		self.jfile = jfile
		self.parent = parent
		dict.__init__(self)
		self.data = {}
		if self.jfile is not None and os.path.isfile(jfile): #ha létezik a fájl
			with open(jfile, "r") as read_file:
				try:
					filedata = json.load(read_file)
					for key in filedata:
						self.__setitem__(key, filedata[key])
				except ValueError as err:
					print(f'"{jfile}" is not a valid json!')
					os._exit(0)
		else: #még nincs fájl vagy nem is kell
			self.jdump()

	def __setitem__(self, key, value):
		if type(value) == JDict: #ha JDict az érték akkor beállítjuk nála a külső containert, először Jdict-et vizsgálunk hogy ne legyen kettős másolás dict-nél
			value = value.copy()
			value.parent = self

		if type(value) == dict: #dict-et átrakjuk JDict-be hogy tudjuk majd hívni a szülő jdump-ját is
			temp = value
			value = JDict(parent=self)
			for k in temp:
				value[k] = temp[k]

		self.data[key] = value
		super().__setitem__(key, value)
		self.jdump()

	def __delitem__(self, key):
		del self.data[key]
		super().__delitem__(key)
		self.jdump()

	def copy(self):
		newself = JDict(self.jfile, self.parent)
		for k in self:
			newself[k] = self[k]
		return newself

	def jdump(self):
		if type(self.parent) == JDict: #meghívjuk a container jdumpját is
			self.parent.jdump()
		if self.jfile is not None:
			with open(self.jfile, "w") as outfile: json.dump(self.data, outfile, indent = 4)