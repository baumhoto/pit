import os
from common.util import Constants
from common.util import PrettyType
from core.entry import Entry

class Tree(metaclass=PrettyType):
	TREE_MODE = 0o40000
	
	def __init__(self):
		self.entries = dict()
		self.oid = ''
		self.mode = Tree.TREE_MODE
		
	def build(entries):
		#sortedEntries = sorted(entries, key=lambda entry: entry.name)
		root = Tree()
		
		for entry in entries:
			root.add_entry(entry.parent_directories(), entry)
		
		return root
		
	def add_entry(self, parents, entry):
		if not parents:	#list is empty
			self.entries[entry.basename()] = entry
		else:
			if not os.path.basename(parents[0]) in self.entries:
				tree = Tree() 
				self.entries[os.path.basename(parents[0])] = tree
			else:
				tree = self.entries[os.path.basename(parents[0])]
					
			parents.pop(0)
			tree.add_entry(parents, entry)
			
	def traverse(self, func):
		for entry in self.entries.values():
			if isinstance(entry, Tree):
				entry.traverse(func)
				
		func(self)
			
	def __str__(self):
		#result = ''.join(map(lambda kv: f'{oct(kv[1].mode).lstrip("0o")} {kv[0]}\0{kv[1].oid.decode(Constants.ENCODE)}', sorted(self.entries.items(), key = lambda x: x[0])))
		result = ''
		for kv in sorted(self.entries.items(), key = lambda x: x[0]):
			result += f'{oct(kv[1].mode).lstrip("0o")} {kv[0]}\0{kv[1].id().decode(Constants.ENCODE)}'
			
		return result
		
	def id(self):
		id = self.oid
		if hasattr(id, 'encode'):
			id = bytes.fromhex(self.oid)
			
		return id
		
