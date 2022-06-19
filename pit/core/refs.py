import os
from core.lockfile import Lockfile

class Refs:
	def __init__(self, pathname):
		self.pathname = pathname

	def update_head(self, oid):
		lockfile = Lockfile(self.head_path())

		lockfile.hold_for_update()
		lockfile.write(oid)
		lockfile.write('\n')
		lockfile.commit()

	def head_path(self):
		return os.path.join(self.pathname, 'HEAD')

	def read_head(self):
		if os.path.exists(self.head_path()):
			with open(self.head_path()) as file:
				return file.read()



class LockDenied(Exception):
	pass
