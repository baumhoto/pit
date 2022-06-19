import os	
import stat

import common.util as util


class Entry:
	REGULAR_MODE		= 0o100644
	EXECUTABLE_MODE	= 0o100755
	DIRECTORY_MODE 	= 0o40000
	
	def __init__(self, name, oid, stat):
		self.name = name
		self.oid 	= oid
		self.stat = stat
		
	def mode(self):
		mode = self.stat[stat.ST_MODE]
		return Entry.EXECUTABLE_MODE if mode & stat.S_IXUSR else Entry.REGULAR_MODE
			
	def parent_directories(self):
		result = list()
		currentPath = ''
		pathParts = util.splitall(self.name)
		for part in pathParts[:-1]:
			currentPath = os.path.join(currentPath, part)
			result.append(currentPath)
		
		return result
		
	def basename(self):
		return os.path.basename(self.name)
			


