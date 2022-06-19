import os
import sys

class Lockfile:
	def __init__(self, path, binary = False):
		self.file_path = path
		self.lock_path = self.file_path + ".lock"
		self.lock = None
		self.binary = binary

	def hold_for_update(self):
		mode = 'x'
		if self.binary:
			mode = 'xb'
		try:
			if self.lock is None:
				# why is x (exclusive opening) not working
				if os.path.exists(self.lock_path):
					raise LockDenied(f'Unable to create {self.lock_path}: File exists.') 
				self.lock = open(self.lock_path, mode) 
			return True
		except LockDenied:
			raise
		except FileNotFoundError as err:
			raise MissingParent(err.message)
		except PermissionError as err:
			raise NoPermission(err.message)
		except:
			sys.stderr.write(f'Unexpected error: {sys.exc_info()[0]}\n')
			raise

	def write(self, data):
		self.raise_stale_lock()
		self.lock.write(data)
			
	def commit(self):
		self.raise_stale_lock()

		self.lock.close()
		os.rename(self.lock_path, self.file_path)
		lock = None
	
	def rollback(self):
		self.raise_stale_lock()
		
		self.lock.close()
		self.lock = None

	def raise_stale_lock(self):
		if self.lock is None:
			raise StaleLock(f'Not holding lock on file: {self.lock_path}')

class MissingParent(Exception):
	pass

class NoPermission(Exception):
	pass

class StaleLock(Exception):
	pass
	
class LockDenied(Exception):
	pass
