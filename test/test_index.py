import unittest
import secrets
import os
import sys
#print(os.path.join(os.path.dirname(os.path.expanduser(__file__)), '../pit'))
sys.path.append(os.path.join(os.path.dirname(os.path.expanduser(__file__)), '../pit'))

from core.index import Index




class TestIndexMethods(unittest.TestCase):
	def setUp(self):
		self.tmp_path = os.path.expanduser(os.path.join('../tmp', __file__))
		self.index_path = os.path.join(self.tmp_path, 'index')
		self.index = Index(self.index_path)
		self.stat = os.stat(__file__)
		self.oid = secrets.token_hex(20)
		
	def test_add_single_file(self):
		#print(self.tmp_path)
		self.index.add('alice.txt', self.oid, self.stat)
		self.assertEqual(['alice.txt'], list(map(lambda x: x.path, self.index.entries.values())))
		
	def test_replace_file_with_directory(self):
		self.index.add('alice.txt', self.oid, self.stat)
		self.index.add('bob.txt', self.oid, self.stat)
		self.index.add('alice.txt/nested.txt', self.oid, self.stat)
		self.assertEqual(['bob.txt', 'alice.txt/nested.txt'],
			list(map(lambda x: x.path, self.index.entries.values())))
			
	def test_replace_directory_with_file(self):
		self.index.add('alice.txt', self.oid, self.stat)
		self.index.add('nested/bob.txt', self.oid, self.stat)
		self.index.add('nested/inner/claire.txt', self.oid, self.stat)
		
		self.index.add('nested', self.oid, self.stat)
		
		self.assertEqual(['alice.txt', 'nested'],
			list(map(lambda x: x.path, self.index.entries.values())))
		
		
		
if __name__ == '__main__':
	unittest.main()
		

