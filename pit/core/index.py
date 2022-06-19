from .lockfile				import Lockfile
from index.entry 			import Entry
import common.util
from collections			import namedtuple
import struct
import hashlib

class Index:
	HEADER_SIZE 	= 12
	HEADER_FORMAT	= '>4s2i'
	SIGNATURE			= b'DIRC'
	VERSION				= 2
	
	ENTRY_FORMAT		= '>10I20sH{}sx'
	ENTRY_BLOCK			= 8
	ENTRY_MIN_SIZE 	= 64
	  
	def __init__(self, pathname):
		self.pathname = pathname
		self.lockfile = Lockfile(pathname, binary=True)
		self.clear()
		
	def clear(self):
		self.entries = dict()
		self.parents = dict()
		self.changed = False
		
	def open_index_file(self):
		try:
			return open(self.pathname, 'r+b')
		except FileNotFoundError:
			return None
			
	def read_header(reader):
		data = reader.read(Index.HEADER_SIZE)
		signature, version, count = struct.unpack(Index.HEADER_FORMAT, data)
		
		if not signature == Index.SIGNATURE:
			raise Invalid(f'Signature: expected {Index.SIGNATURE} but found {signature}')
		if not version == Index.VERSION:
			raise Invalid(f'Version: expected {Index.VERSION} but found {version}')
			
		return count
		
	def read_entries(self, reader, count):
		for i in list(range(count)):
			entry_bytes = reader.read(Index.ENTRY_MIN_SIZE)
			
			while not entry_bytes[-1:] == b'\x00':
				entry_bytes += reader.read(Index.ENTRY_BLOCK)
				
			entry = Entry.parse(entry_bytes)
			self.store_entry(entry)
				
	def store_entry(self, entry):	
		self.entries[entry.key()] = entry
		
		for dir in entry.parent_directories():
			if not dir in self.parents:
				self.parents[dir] = set()
				
			self.parents[dir].add(entry.key())
		
	def add(self, pathname, oid, stat):
		entry = Entry(pathname, oid, stat)
		self.discard_conflicts(entry)
		self.store_entry(entry)
		self.changed = True
		
	def discard_conflicts(self, entry):
		for parent in entry.parent_directories():
			self.remove_entry(parent)
		self.remove_children(entry.key())
				
	def remove_children(self, path):
		if path in self.parents:
			children = self.parents[path].copy()
			for child in children:
				self.remove_entry(child)
	
	def remove_entry(self, pathname):
		if pathname in self.entries:
			entry = self.entries[pathname]
			del self.entries[entry.key()]
			
			for dir in entry.parent_directories():
				self.parents[dir].discard(entry.key())
				if len(self.parents[dir]) == 0:
					del self.parents[dir]
	
	def each_entry(self, function):
		if function is None:
			sorted_items = sorted(self.entries.items(), key = lambda x: x[0])
			result = map(lambda x: x[1], sorted_items)
		else:
			result = map(lambda x: function(self.entries[x].asBytes()), sorted(self.entries))
		
		return list(result)
				
	def write_updates(self):
		if not self.changed:
			return self.lockfile.rollback()
		
		writer = Checksum(self.lockfile)
		
		header = struct.pack(Index.HEADER_FORMAT, Index.SIGNATURE, 2, len(self.entries))
					
		writer.write(header)
		self.each_entry(writer.write)
		
		writer.write_checksum()
		self.lockfile.commit()
		self.changed = False
		
	def load_for_update(self):
		self.lockfile.hold_for_update()
		self.load()
			
	def load(self):
		self.clear()
		try:
			with self.open_index_file() as file:
				if file:
					reader = Checksum(file)
					count = Index.read_header(reader)
					self.read_entries(reader, count)
					reader.verify_checksum()
		except AttributeError:
			pass	#OK if index file does not exist
			
	def release_lock(self):
		self.lockfile.rollback()
		
		
class Checksum:
	CHECKSUM_SIZE = 20
	
	def __init__(self, file):
		self.file = file
		self.digest = hashlib.sha1()
	
	def read(self, size):
		data = self.file.read(size)
		
		if len(data) < size:
			raise EndOfFile('Unexpected end-of-file while reading index')
		
		self.digest.update(data)
		return data
	
	def verify_checksum(self):
		sum = self.file.read(Checksum.CHECKSUM_SIZE)
		if not sum == self.digest.digest():
			raise Invalid('Checksum does not match value stored on disk')
			
	def write(self, bytes):
		self.file.write(bytes)
		self.digest.update(bytes)
		
	def write_checksum(self):
		hex_bytes = bytes.fromhex(self.digest.hexdigest())
		self.file.write(hex_bytes)
	

class EndOfFile(Exception):
	pass
	
class Invalid(Exception):
	pass
		
	
