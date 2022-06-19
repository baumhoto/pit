import os
from common.util import Constants

class Workspace:
	IGNORE = ['.git', '__pycache__', '.', '..']
	def __init__(self, pathname):
		self.pathname = pathname
		
	def list_files(self, path = None):
		result = list()
		
		if path is None:
			path = self.pathname
			
		if os.path.isdir(path):
			dirEntries = list(filter(lambda x: (x not in Workspace.IGNORE), os.listdir(path)))
			for dirEntry in dirEntries:
				filePath = os.path.join(path, dirEntry)
				result.extend(self.list_files(filePath))
			#map(lambda x: self.list_files(os.path.join(path, x)), dirEntries)
		elif os.path.isfile(path):
			result.append(os.path.relpath(path, self.pathname))
		else:
			raise MissingFile(f'pathspec {path} did not match any files')
		
		return result
		
	def read_file(self, path):
		try:
			with open(os.path.join(self.pathname, path), 'r') as file:
				return file.read()
		except PermissionError:
			raise NoPermission(f'open {path}: Permission denied')
			
	def stat_file(self, path):
		try:
			return os.stat(os.path.join(self.pathname, path))
		except PermissionError:
			raise NoPermission(f'stat {path}: Permission denied')
			
		
class MissingFile(Exception):
	pass
	
class NoPermission(Exception):
	pass

	
	
	
	
	
