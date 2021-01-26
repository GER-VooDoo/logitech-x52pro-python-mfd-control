from __future__ import absolute_import, with_statement, print_function, division, unicode_literals

from x52pro_extended import PageableX52ProMfd
import logging


class TestMfd(PageableX52ProMfd):
	def __init__(self):
		super().__init__()
		
	def update_mfd_data(self):
		self.entries = {}
		self.entries['Page 1'] = [
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
		
		self.entries['Page 2'] = [
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
		
		self.entries['Page 3'] = [
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


if __name__ == '__main__':
	logging.root.setLevel(logging.DEBUG)
	doObj = TestMfd()
	print("press <enter> to exit")
	input()
