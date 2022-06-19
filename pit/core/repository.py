import os
from .database	import Database
from .index			import Index
from .refs			import Refs
from .workspace import Workspace

class Repository:
	def __init__(self, git_path):
		self.git_path = git_path
		self.database = Database(os.path.join(self.git_path, 'objects'))
		self.index = Index(os.path.join(self.git_path, 'index'))
		self.refs = Refs(self.git_path)
		self.workspace = Workspace(os.path.dirname(self.git_path))
