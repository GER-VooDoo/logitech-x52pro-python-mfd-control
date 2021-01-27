from __future__ import absolute_import, with_statement, print_function, division, unicode_literals

from x52pro import *
import os
import logging


class TestPageMfd(X52ProPageableMfd):
	def __init__(self):
		super().__init__()
		
	def update_mfd_data(self):
		entries = {}
		entries['Page 1'] = [
			#----------------# display width #
			"-- 1 -----------",
			"Line 1",
			"Line 2",
			"Line 3",
			"-- 2 -----------",
			"Line 1",
			"-- 3 -----------",
			"Line 1",
			#----------------# display width #
		]
		
		entries['Page 2'] = [
			#----------------# display width #
			"-- 1 -----------",
			"Line 1",
			"Line 2",
			"Line 3",
			"-- 2 -----------",
			"Line 1",
			"-- 3 -----------",
			"Line 1",
			#----------------# display width #
		]
		
		entries['Page 3'] = [
			#----------------# display width #
			"-- 1 -----------",
			"Line 1",
			"Line 2",
			"Line 3",
			"-- 2 -----------",
			"Line 1",
			"-- 3 -----------",
			"Line 1",
			#----------------# display width #
		]

		return entries


class TestListMfd(X52ProScrollableMfd):
	def __init__(self):
		super().__init__()

	def update_profile_data(self):
		return os.path.join('test.pr0')

	def update_mfd_data(self):
		entries = []
		entries.append("Entry 1 Entry 1 Entry 1")
		entries.append("Entry 2 Entry 2 Entry 2")
		entries.append("Entry 3")
		entries.append("Entry 4")
		entries.append("Entry 5")
		entries.append("Entry 6")
		return entries

if __name__ == '__main__':
	logging.root.setLevel(logging.DEBUG)
	#TestPageMfd()
	TestListMfd()
	print("press <enter> to exit")
	input()
