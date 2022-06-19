from common.util import PrettyType

class Commit(metaclass=PrettyType):
	def __init__(self, parent, tree, author, message):
		self.parent = parent
		self.tree = tree
		self.author = author
		self.message = message
		self.oid = ''
		
	def __str__(self):
		lines = []
		lines.append(f'tree { self.tree }')
		if not self.parent is None:
			lines.append(f'parent { self.parent }')
		lines.append(f'author { self.author }')
		lines.append(f'committer { self.author}')
		lines.append('')
		lines.append(self.message)
			
		return '\n'.join(lines)
	
