from common.util import PrettyType

class Blob(metaclass=PrettyType):
	def __init__(self, data):
		self.data = data
		self.oid = ''
	
	def __str__(self):
		return f'{self.data}'
		
