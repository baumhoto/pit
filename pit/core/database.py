import zlib
import hashlib
import os
import string
import random
from common.util import Constants
from database.blob import Blob

class Database:
	TEMP_CHARS = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(string.digits)
		
	def __init__(self, pathname):
		self.pathname = pathname
			
	def store(self, object):
		string = str(object)
		content = f'{ type(object) } { len(string) }\0{ string }'.encode(Constants.ENCODE)
		m = hashlib.sha1()
		m.update(content)
		object.oid = m.hexdigest()
		self._write_object(object.oid, content)
		#print(f'oid: {object.oid} type: {type(object)} \n')
						
	def _write_object(self, oid, content):
		oid_array = list(oid)
		object_path = os.path.join(self.pathname, "".join(oid_array[:2]), "".join(oid_array[2:]))
		if os.path.exists(object_path):
			return
		
		dirname 		= os.path.dirname(object_path)
		temp_path		= os.path.join(dirname, Database.generate_temp_name())
		compressed 	= zlib.compress(content, 1)
		try:
			with open(temp_path, 'xb') as file:
				file.write(compressed)
				os.rename(temp_path, object_path)
		except FileNotFoundError:
			os.makedirs(dirname)
			with open(temp_path, 'xb') as file:
				file.write(compressed)
				os.rename(temp_path, object_path)
		except OSError as err:
			sys.stderr.write(f'fatal: {err}\n')
			sys.exit(1)
		except:
			sys.stderr.write(f'Unexpected error: {sys.exc_info()[0]}')
			raise
		
	def generate_temp_name():
		return f'tmp_obj_{"".join(map(lambda x: random.choice(Database.TEMP_CHARS), range(0,6)))}'
