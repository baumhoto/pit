#!/usr/bin/env python3

import sys
import os
import locale
import pytz
from pytz 				import timezone
from datetime 		import datetime as dt
from pathlib 			import Path

from core.workspace 		import MissingFile, NoPermission
from core.entry 				import Entry
from core.lockfile			import LockDenied
from core.repository		import Repository
from database.blob 			import Blob
from database.tree 			import Tree
from database.author		import Author
from database.commit		import Commit

if len(sys.argv) == 1:
	print('No command specified')
	sys.exit(0)

command = sys.argv[1]
if command == 'init':
	path = Path.cwd()

	root_path = path.expanduser()
	if len(sys.argv) == 3:
		root_path = root_path.joinpath(sys.argv[2])
	
	git_path = root_path.joinpath('.git')

	dirs = ['objects', 'refs']
	try:
		for dir in dirs:
			os.makedirs(git_path.joinpath(dir))
	except OSError as err:
		sys.stderr.write(f'fatal: {err}\n')
		sys.exit(1)
	except:
		sys.stderr.write(f'Unexpected error: {sys.exc_info()[0]}')
		raise
		
	sys.stdout.write(f'Initialized empty Pit repository in {git_path}\n')
	sys.exit(0)
elif command == 'commit':
	root_path = os.getcwd()
	repo = Repository(os.path.join(root_path, '.git'))
	
	repo.index.load()
	
	treeItems = repo.index.each_entry(None)
	root = Tree.build(treeItems)
	root.traverse(repo.database.store)
	
	parent = repo.refs.read_head()
	name	= os.environ['GIT_AUTHOR_NAME']
	email = os.environ['GIT_AUTHOR_EMAIL']
	author = Author(name, email, dt.now(tz=timezone('utc')))
	message = sys.stdin.read()
	
	commit = Commit(parent, root.oid, author, message)
	repo.database.store(commit)
	repo.refs.update_head(commit.oid)

	first_line = message.split("\n")[0]
	is_root = '(root-commit)' if parent is None else ''
	sys.stdout.write(f'{is_root} { commit.oid }] { first_line }\n')
	sys.exit(0)
	
elif command == 'add':
	root_path = os.getcwd()
	repo = Repository(os.path.join(root_path, '.git'))
	
	try:
		repo.index.load_for_update()
	except LockDenied as err:
		sys.stderr.write(f'{err}\n')
		sys.stderr.write(f'Another pit process seems to be running in this repository. Please make sure all processes are terminated then try again. If it still fails, a pit process may have crashed int this repository earlier: remove the file manually to continue.\n')
		sys.exit(128)
	
	paths = list()
	try:
		for path in sys.argv[2:]:
			paths.extend(repo.workspace.list_files(path))
	except MissingFile as err:
		sys.stderr.write(f'fatal: {err}\n')
		repo.index.release_lock()
		sys.exit(128)
	
	try:
		for file in	paths:
			data = repo.workspace.read_file(file)
			stat = repo.workspace.stat_file(file)
			blob = Blob(data)
			repo.database.store(blob)
			repo.index.add(file, blob.oid, stat)
	except NoPermission as err:
		sys.stderr.write(f'error: {err}\n')
		sys.stderr.write(f'fatal: adding files failed\n')
		repo.index.release_lock()
		sys.exit(128)
	
	repo.index.write_updates()
	sys.exit(0)
	
else:
	sys.stderr.write(f'pit:{sys.argv[1]} is not a pit command.\n')
	sys.exit(1)
	
