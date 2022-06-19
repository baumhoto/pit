import struct
import os
import stat
import sys
import binascii
from common.util 	import Constants
from common 			import util

class Entry:
	REGULAR_MODE 		= 0o100644
	EXECUTABLE_MODE =	0o100755
	MAX_PATH_SIZE		= 0xfff
	BLOCK_SIZE			= 8
	
	def __init__(self, pathname, oid, fstat):
		self.path = pathname
		self.oid = oid
		
		if fstat is None:
			return 
		
		temp = fstat.st_mode
		self.mode = Entry.EXECUTABLE_MODE if temp & stat.S_IXUSR else Entry.REGULAR_MODE
		self.flags = min(len(self.path), Entry.MAX_PATH_SIZE)
		
		self.ctime = int(fstat.st_ctime)
		self.ctime_nsec = 0 #int(fstat.st_ctime_ns) to big for 32bit int
		self.mtime = int(fstat.st_mtime)
		self.mtime_nsec = 0 #int(fstat.st_mtime_ns) to big for 32bit int
		self.dev = fstat.st_dev
		self.ino = fstat.st_ino
		self.uid = fstat.st_uid
		self.gid = fstat.st_gid
		self.size = fstat.st_size
		self.oid = oid
		
	def create(ctime, ctime_nsec, mtime, mtime_nsec, dev, ino, mode, uid, gid, size, oid, flags, path):
		entry = Entry(path, oid, None)
		entry.oid = oid #.hex()
		entry.path = path #.decode(Constants.ENCODE)
		entry.ctime = ctime
		entry.ctime_nsec = ctime_nsec
		entry.mtime = mtime
		entry.mtime_nsec = mtime_nsec
		entry.dev = dev
		entry.ino = ino
		entry.mode = mode
		entry.uid = uid
		entry.gid = gid
		entry.size = size
		entry.flags = flags
		return entry
		
	def parse(data):
		length = len(data) - 63
		ctime, ctime_nsec, mtime, mtime_nsec, dev, ino, mode, uid, gid, size, oid, flags, path = struct.unpack(f'>10I20sH{length}sx', data)
		return Entry.create(ctime, ctime_nsec, mtime, mtime_nsec, dev, ino, mode, uid, gid, size, oid, flags, path)
		
	def asBytes(self):
		
		data = struct.pack(f'>10I20sH{len(self.path)}sx',
			self.ctime, 
			self.ctime_nsec, 
			self.mtime, 
			self.mtime_nsec, 
			self.dev,
			self.ino, 
			self.mode,
			self.uid,
			self.gid,
			self.size,
			self.id(),
			self.flags,
			self.key().encode(Constants.ENCODE))
				
		#print(f'{self.path}: {len(data)}') #{struct.calcsize(f">10I20sH{len(self.path)}s")}')
		while not len(data) % Entry.BLOCK_SIZE == 0:
			data = data + b'\0'
		
		return data
		
	def __str__(self):
		return self.asBytes().decode(Constants.ENCODE)
		
	def parent_directories(self):
		result = list()
		currentPath = ''
		pathParts = util.splitall(self.key())
		for part in pathParts[:-1]:
			currentPath = os.path.join(currentPath, part)
			result.append(currentPath)
		
		return result
		
	def basename(self):
		return os.path.basename(self.key())
		
	def key(self):
		key = self.path
		if hasattr(key, 'decode'):
			key = key.decode(Constants.ENCODE)
			
		key = key.rstrip('\x00')
		
		return key
		
	def id(self):
		id = self.oid
		if hasattr(id, 'encode'):
			id = bytes.fromhex(self.oid)
			
		return id
		
		
		
	
		

