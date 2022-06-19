import os

class PrettyType(type):
	def __repr__(self):
		return self.__name__.lower()
		
class Constants:
	ENCODE = 'raw_unicode_escape'
	
	
def splitall(path):
	allparts = []
	while 1:
		parts = os.path.split(path)
		if parts[0] == path:  # sentinel for absolute path
			allparts.insert(0, parts[0])
			break
		elif parts[1] == path: # sentinel for relative paths
			allparts.insert(0, parts[1])
			break
		else:
			path = parts[0]
			allparts.insert(0, parts[1])
	return allparts

