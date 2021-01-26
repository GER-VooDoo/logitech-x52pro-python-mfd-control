from __future__ import absolute_import, with_statement, print_function, division, unicode_literals

from x52pro import X52ProMfd
from time import (sleep, time)
import re
import os
import json
import logging


class PageableX52ProMfd(X52ProMfd):
	def __init__(self):
		self.lastinput = self.nowmillis()
		self.cursor = 0
		self.mode = '0'
		self.entries = {}
		self.entry = ''
		# call update data function
		self.update_mfd_data()
		super().__init__()

	def update_mfd_data(self):
		self.entries = {}

	def nowmillis(self):
		millis = int(round(time() * 1000))
		return millis

	def addToClipBoard(text):
		command = 'echo ' + text.strip() + '| clip'
		os.system(command)

	def OnSoftButton(self, *args, **kwargs):
		if self.lastinput > self.nowmillis() - 200:
			return
		self.lastinput = self.nowmillis()
		select = False
		up = False
		down = False

		if args[0].select:
			select = True
		if args[0].up:
			up = True
		if args[0].down:
			down = True
		
		if (up):
			if self.mode == '1':
				self.cursor = (self.cursor - 1) % len(self.entries[self.entry])
			else:
				self.cursor = (self.cursor - 1) % len(list(self.entries))
		if (down):
			if self.mode == '1':
				self.cursor = (self.cursor + 1) % len(self.entries[self.entry])
			else:
				self.cursor = (self.cursor + 1) % len(list(self.entries))
		if select:
			if self.mode == '1':
				# if in route view, switch to system view and focus current system
				lines = list(self.entries)
				lines.sort()
				self.cursor = lines.index(self.entry);
				self.mode = '0'
			else:
				# else if system view, switch to route for selected and jump to line 0
				lines = list(self.entries)
				lines.sort()
				self.entry = lines[self.cursor]
				self.mode = '1'
				self.cursor = 0
		if (select or up or down):
			self.PageShow()
	
	def OnPage(self, page_id, activated):
		if page_id == 0 and activated:
			self.PageShow()

	def PageShow(self):
		if self.mode == '1':
			lines = self.entries[self.entry]
			cursor = self.cursor
			self.display(lines[(cursor + 0) % len(lines)], lines[(cursor + 1) % len(lines)], lines[(cursor + 2) % len(lines)])
			#for x in range(-1, 1):
				#if re.match(r'^-- \d', lines[(cursor + x) % len(lines)]):
					#addToClipBoard(lines[(cursor + x + 1) % len(lines)])
		else:
			lines = list(self.entries)
			lines.sort()
			cursor = self.cursor
			self.display(lines[(cursor - 1) % len(lines)], "> " + lines[(cursor + 0) % len(lines)], lines[(cursor + 1) % len(lines)])