from __future__ import absolute_import, with_statement, print_function, division, unicode_literals

import ctypes
import ctypes.wintypes
import logging
import os
import sys
import platform
from time import (sleep, time)
import re
import json

"""
Saitek / Logitech functions listed in the DLL:

DirectOutput_Initialize
DirectOutput_Deinitialize
DirectOutput_AddPage
DirectOutput_DeleteFile
DirectOutput_DisplayFile
DirectOutput_Enumerate
DirectOutput_GetDeviceInstance
DirectOutput_GetDeviceType
DirectOutput_RegisterDeviceCallback
DirectOutput_RegisterPageCallback
DirectOutput_RegisterSoftButtonCallback
DirectOutput_RemovePage
DirectOutput_SaveFile
DirectOutput_SendServerFile
DirectOutput_SendServerMsg
DirectOutput_SetImage
DirectOutput_SetImageFromFile
DirectOutput_SetLed
DirectOutput_SetProfile
DirectOutput_SetString
DirectOutput_StartServer
DirectOutput_CloseServer
"""

S_OK = 0x00000000
E_HANDLE = 0x80070006
E_INVALIDARG = 0x80070057
E_OUTOFMEMORY = 0x8007000E
E_PAGENOTACTIVE = -0xfbffff        # Something munges it from it's actual value
E_BUFFERTOOSMALL = -0xfc0000
E_NOTIMPL = 0x80004001
ERROR_DEV_NOT_EXIST = 55

SOFTBUTTON_SELECT = 0x00000001
SOFTBUTTON_UP = 0x00000002
SOFTBUTTON_DOWN = 0x00000004


"""
Errors
"""


class MissingDeviceError(Exception):
	"""
		Throw when no instance of a device cannot be found.
	"""
	pass


class DLLError(Exception):
	def __init__(self, error_code):
		self.error_code = error_code
		if error_code == 126:
			self.msg = "specified file does not exist"
		elif error_code == 193:
			self.msg = "possible 32/64 bit mismatch between Python interpreter and DLL. Make sure you have installed both the 32- and 64-bit driver from Saitek's website"
		else:
			self.msg = "unspecified error"

	def __str__(self):
		return "Unable to load DirectOutput.dll - " + self.msg


class DirectOutputError(Exception):
	Errors = {
		E_HANDLE: "Invalid device handle specified.",
		E_INVALIDARG: "An argument is invalid, and I don't mean it has a poorly leg.",
		E_OUTOFMEMORY: "Download more RAM.",
		E_PAGENOTACTIVE: "Page not active, stupid page.",
		E_BUFFERTOOSMALL: "Buffer used was too small. Use a bigger buffer. See also E_OUTOFMEMORY.",
		E_NOTIMPL: "Feature not implemented, allegedly"
	}

	def __init__(self, error_code):
		self.error_code = error_code
		if error_code in self.Errors:
			self.msg = self.Errors[error_code]
		else:
			self.msg = "Unspecified DirectOutput Error - " + str(hex(error_code))

	def __str__(self):
		return self.msg


class DeviceNotFoundError(Exception):
	def __str__(self):
		return "No Compatible Device Found"


"""
DLL Mapping classes
"""


class DirectOutput(object):
	def __init__(self, dll_path):
		"""
		Creates python object to interact with DirecOutput.dll

		Required Arguments:
		dll_path -- String containing DirectOutput.dll location.

		"""
		logging.debug("DirectOutput.__init__")
		self.DirectOutputDLL = ctypes.WinDLL(dll_path, use_last_error=True)

		hmod = ctypes.wintypes.HMODULE

		self.DirectOutputDLL.DirectOutput_Initialize.argtypes = [hmod]
		self.DirectOutputDLL.DirectOutput_Deinitialize.argtypes = []
		self.DirectOutputDLL.DirectOutput_RegisterDeviceCallback.argtypes = [hmod, hmod]
		self.DirectOutputDLL.DirectOutput_Enumerate.argtypes = [hmod, hmod]
		self.DirectOutputDLL.DirectOutput_RegisterSoftButtonCallback.argtypes = [hmod, hmod, hmod]
		self.DirectOutputDLL.DirectOutput_RegisterPageCallback.argtypes = [hmod, hmod, hmod]
		self.DirectOutputDLL.DirectOutput_SetProfile.argtypes = [hmod, hmod, hmod]
		self.DirectOutputDLL.DirectOutput_AddPage.argtypes = [hmod, hmod, hmod]
		self.DirectOutputDLL.DirectOutput_RemovePage.argtypes = [hmod, hmod]
		self.DirectOutputDLL.DirectOutput_SetLed.argtypes = [hmod, hmod, hmod, hmod]
		self.DirectOutputDLL.DirectOutput_SetString.argtypes = [hmod, hmod, hmod, hmod, hmod]

	def Initialize(self, application_name):
		"""
		Function to call DirectOutput_Initialize

		Required Arguments:
		application_name -- String representing name of applicaiton - must be unique per-application

		Returns:
		S_OK: The call completed sucesfully
		E_OUTOFMEMORY: There was insufficient memory to complete this call.
		E_INVALIDARG: The argument is invalid
		E_HANDLE: The DirectOutputManager process could not be found

		"""
		logging.debug("DirectOutput.Initialize")
		return self.DirectOutputDLL.DirectOutput_Initialize(ctypes.wintypes.LPWSTR(application_name))

	def Deinitialize(self):
		"""
		Direct function call to DirectOutput_Deinitialize

		Returns:
		S_OK: The call completed successfully.
		E_HANDLE:  DirectOutput was not initialized or was already deinitialized.
		"""
		logging.debug("DirectOutput.Deinitialize")
		return self.DirectOutputDLL.DirectOutput_Deinitialize()

	def RegisterDeviceCallback(self, function):
		"""
		Registers self.DeviceCallback to be called when devices get registered

		Required Arugments:
		function -- Function to call when a device registers

		Returns:
		S_OK: The call completed successfully
		E_HANDLE: DirectOutput was not initialized.

		"""
		logging.debug("DirectOutput.RegisterDeviceCallback")
		return self.DirectOutputDLL.DirectOutput_RegisterDeviceCallback(function, 0)

	def Enumerate(self, function):
		"""
		Direct call to DirectOutput_Enumerate

		Returns:
		S_OK: The call completed successfully
		E_HANDLE: DirectOutput was not initialized.

		"""
		logging.debug("DirectOutput.Enumerate")
		return self.DirectOutputDLL.DirectOutput_Enumerate(function, 0)

	def RegisterSoftButtonCallback(self, device_handle, function):
		"""
		Registers a function to be called when a soft button changes

		Required Arugments:
		device_handle -- ID of device
		function -- Function to call when a soft button changes

		Returns:
		S_OK: The call completed successfully.
		E_HANDLE: The device handle specified is invalid.

		"""
		logging.debug("DirectOutput.RegisterSoftButtonCallback({}, {})".format(device_handle, function))
		return self.DirectOutputDLL.DirectOutput_RegisterSoftButtonCallback(device_handle, function, 0)

	def RegisterPageCallback(self, device_handle, function):
		"""
		Registers a function to be called when page changes

		Required Arugments:
		device_handle -- ID of device
		function -- Function to call when a page changes

		Returns:
		S_OK: The call completed successfully.
		E_HANDLE: The device handle specified is invalid.
		"""
		logging.debug("DirectOutput.RegisterPageCallback({}, {})".format(device_handle, function))
		return self.DirectOutputDLL.DirectOutput_RegisterPageCallback(device_handle, function, 0)

	def SetProfile(self, device_handle, profile):
		"""
		Sets the profile used on the device.

		Required Arguments:
		device_handle -- ID of device
		profile -- full path of the profile to activate. passing None will clear the profile.
		"""
		logging.debug("DirectOutput.SetProfile({}, {})".format(device_handle, profile))
		if profile:
			return self.DirectOutputDLL.DirectOutput_SetProfile(device_handle, len(profile), ctypes.wintypes.LPWSTR(profile))
		else:
			return self.DirectOutputDLL.DirectOutput_SetProfile(device_handle, 0, 0)

	def AddPage(self, device_handle, page, name, active):
		"""
		Adds a page to the MFD

		Required Arguments:
		device_handle -- ID of device
		page -- page ID to add
		name -- String specifying page name
		active -- True if page is to become the active page, if False this will not change the active page

		Returns:
		S_OK: The call completed successfully.
		E_OUTOFMEMORY: Insufficient memory to complete the request.
		E_INVALIDARG: The dwPage parameter already exists.
		E_HANDLE: The device handle specified is invalid.

		"""
		logging.debug("DirectOutput.AddPage({}, {}, {}, {})".format(device_handle, page, name, active))
		return self.DirectOutputDLL.DirectOutput_AddPage(device_handle, page, active)

	def RemovePage(self, device_handle, page):
		"""
		Removes a page from the MFD

		Required Arguments:
		device_handle -- ID of device
		page -- page ID to remove

		Returns:
		S_OK: The call completed successfully.
		E_INVALIDARG: The dwPage argument does not reference a valid page id.
		E_HANDLE: The device handle specified is invalid.

		"""
		logging.debug("DirectOutput.RemovePage({}, {})".format(device_handle, page))
		return self.DirectOutputDLL.DirectOutput_RemovePage(device_handle, page)

	def SetLed(self, device_handle, page, led, value):
		"""
		Sets LED state on a given page

		Required Arguments:
		device_handle -- ID of device
		page -- page number
		led -- ID of LED to change
		value -- value to set LED (1 = on, 0 = off)

		Returns:
		S_OK: The call completes successfully.
		E_INVALIDARG: The dwPage argument does not reference a valid page id, or the dwLed argument does not specifiy a valid LED id.
		E_HANDLE: The device handle specified is invalid

		"""
		logging.debug("DirectOutput.SetLed({}, {}, {}, {})".format(device_handle, page, led, value))
		return self.DirectOutputDLL.DirectOutput_SetLed(device_handle, page, led, value)

	def SetString(self, device_handle, page, line, string):
		"""
		Sets a string to display on the MFD

		Required Arguments:
		device_handle -- ID of device
		page -- the ID of the page to add the string to
		line -- the line to display the string on (0 = top, 1 = middle, 2 = bottom)
		string -- the string to display

		Returns:
		S_OK: The call completes successfully.
		E_INVALIDARG: The dwPage argument does not reference a valid page id, or the dwString argument does not reference a valid string id.
		E_OUTOFMEMORY: Insufficient memory to complete the request.
		E_HANDLE: The device handle specified is invalid.

		"""
		logging.debug("DirectOutput.SetString({}, {}, {}, {})".format(device_handle, page, line, string))
		return self.DirectOutputDLL.DirectOutput_SetString(device_handle, page, line, len(string),
														   ctypes.wintypes.LPWSTR(string))


class DirectOutputDevice(object):
	class Buttons(object):
		select, up, down = False, False, False
		def __init__(self, bitmask):
			self.bitmask = bitmask
			if bitmask == 1:
				self.select = True
			elif bitmask == 2:
				self.up = True
			elif bitmask == 3:
				self.up = True
				self.select = True
			elif bitmask == 4:
				self.down = True
			elif bitmask == 5:
				self.down = True
				self.select = True
			elif bitmask == 6:
				self.up = True
				self.down = True
			elif bitmask == 7:
				self.up = True
				self.down = True
				self.select = True

		def __repr__(self):
			return "Select: " + str(self.select) + " Up: " + str(self.up) + " Down: " + str(self.down)

	application_name = "GenericDevice"
	device_handle = None
	direct_output = None
	debug_level = 0

	def __init__(self, debug_level=0, name=None):
		"""
		Initialises device, creates internal state (device_handle) and registers callbacks.
		"""
		logging.info("DirectOutputDevice.__init__")

		prog_dir = os.environ["ProgramFiles"]
		if platform.machine().endswith('86'):
			# 32-bit machine, nothing to worry about
			pass
		elif platform.machine().endswith('64'):
			# 64-bit machine, are we a 32-bit python?
			if platform.architecture()[0] == '32bit':
				prog_dir = os.environ["ProgramFiles(x86)"]
		dll_path = os.path.join(prog_dir, "Logitech\\DirectOutput\\DirectOutput.dll")

		if os.path.isfile(dll_path) == False:
			dll_path = os.path.join('.\\', "Logitech\\DirectOutput\\DirectOutput.dll")

		self.application_name = name or DirectOutputDevice.application_name
		self.debug_level = debug_level

		try:
			logging.debug("DirectOutputDevice -> DirectOutput: {}".format(dll_path))
			self.direct_output = DirectOutput(dll_path)
			logging.debug("direct_output = {}".format(self.direct_output))
		except WindowsError as e:
			logging.warning("DLLError: {}: {}".format(dll_path, e.winerror))
			raise DLLError(e.winerror) from None

		result = self.direct_output.Initialize(self.application_name)
		if result != S_OK:
			logging.warning("direct_output.Initialize returned {}".format(result))
			raise DirectOutputError(result)

		logging.info("Creating callback closures.")
		self.onDevice_closure = self._OnDeviceClosure()
		logging.debug("onDevice_closure is {}".format(self.onDevice_closure))
		self.onEnumerate_closure = self._OnEnumerateClosure()
		logging.debug("onEnumerate_closure is {}".format(self.onEnumerate_closure))
		self.onPage_closure = self._OnPageClosure()
		logging.debug("onPage_closure is {}".format(self.onPage_closure))
		self.onSoftButton_closure = self._OnSoftButtonClosure()
		logging.debug("onSoftButton_closure is {}".format(self.onSoftButton_closure))

		result = self.direct_output.RegisterDeviceCallback(self.onDevice_closure)
		if result != S_OK:
			logging.warning("RegisterDeviceCallback failed: {}".format(result))
			self.finish()
			raise DirectOutputError(result)

		result = self.direct_output.Enumerate(self.onEnumerate_closure)
		if result != S_OK:
			logging.warning("Enumerate failed: {}".format(result))
			self.finish()
			raise DirectOutputError(result)

		if not self.device_handle:
			logging.warning("No device handle")
			self.finish()
			raise MissingDeviceError()

		result = self.direct_output.RegisterSoftButtonCallback(self.device_handle, self.onSoftButton_closure)
		if result != S_OK:
			logging.warning("RegisterSoftButtonCallback failed")
			self.finish()
			raise DirectOutputError(result)

		result = self.direct_output.RegisterPageCallback(self.device_handle, self.onPage_closure)
		if result != S_OK:
			logging.warning("RegisterPageCallback failed")
			self.finish()
			raise DirectOutputError(result)

	def __del__(self, *args, **kwargs):
		logging.debug("DirectOutputDevice.__del__")
		self.finish()

	def finish(self):
		"""
		De-initializes DLL. Must be called before program exit
		"""
		if self.direct_output:
			logging.info("DirectOutputDevice deinitializing")
			self.direct_output.Deinitialize()
			self.direct_output = None
		else:
			logging.debug("nothing to do in finish()")

	def _OnDeviceClosure(self):
		"""
		Returns a pointer to function that calls self._OnDevice method. This allows class methods to be called from within DirectOutput.dll
		http://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes
		"""
		OnDevice_Proto = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p)

		def func(hDevice, bAdded, pvContext):
			logging.info("device callback closure func: {}, {}, {}".format(hDevice, bAdded, pvContext))
			self._OnDevice(hDevice, bAdded, pvContext)

		return OnDevice_Proto(func)

	def _OnEnumerateClosure(self):
		"""
		Returns a pointer to function that calls self._OnEnumerate method. This allows class methods to be called from within DirectOutput.dll
		http://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes
		"""
		OnEnumerate_Proto = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)

		def func(hDevice, pvContext):
			logging.info("enumerate callback closure func: {}, {}".format(hDevice, pvContext))
			self._OnEnumerate(hDevice, pvContext)

		return OnEnumerate_Proto(func)

	def _OnPageClosure(self):
		"""
		Returns a pointer to function that calls self._OnPage method. This allows class methods to be called from within DirectOutput.dll
		http://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes
		"""
		OnPage_Proto = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.c_bool, ctypes.c_void_p)

		def func(hDevice, dwPage, bActivated, pvContext):
			logging.info("page callback closure: {}, {}, {}, {}".format(hDevice, dwPage, bActivated, pvContext))
			self._OnPage(hDevice, dwPage, bActivated, pvContext)

		return OnPage_Proto(func)

	def _OnSoftButtonClosure(self):
		"""
		Returns a pointer to function that calls self._OnSoftButton method. This allows class methods to be called from within DirectOutput.dll
		http://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes
		"""
		OnSoftButton_Proto = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.c_void_p)

		def func(hDevice, dwButtons, pvContext):
			logging.info("soft button callback closure: {}, {}, {}".format(hDevice, dwButtons, pvContext))
			self._OnSoftButton(hDevice, dwButtons, pvContext)

		return OnSoftButton_Proto(func)

	def _OnDevice(self, hDevice, bAdded, pvContext):
		"""
		Internal function to register device handle
		"""
		if not bAdded:
			raise NotImplementedError("Received a message that a device went away.")
		if self.device_handle and self.device_handle != hDevice:
			raise IndexError("Too many Saitek devices present")
		logging.info("_OnDevice")
		self.device_handle = hDevice

	def _OnEnumerate(self, hDevice, pvContext):
		"""
		Internal function to process a device enumeration
		"""
		logging.info("_OnEnumerate")
		self._OnDevice(hDevice, True, pvContext)

	def _OnPage(self, hDevice, dwPage, bActivated, pvContext):
		"""
		Method called when page changes. Calls self.OnPage to hide hDevice and pvContext from end-user
		"""
		logging.info("_OnPage")
		self.OnPage(dwPage, bActivated)

	def _OnSoftButton(self, hDevice, dwButtons, pvContext):
		"""
		Method called when soft button changes. Calls self.OnSoftButton to hide hDevice and pvContext from end-user. Also hides change of page softbutton and press-up.
		"""
		logging.info("_OnSoftButton")
		self.OnSoftButton(self.Buttons(dwButtons))

	def OnPage(self, page, activated):
		"""
		Method called when a page changes. This should be overwritten by inheriting class
		Required Arguments:
		page -- page_id passed to AddPage
		activated -- true if this page has become the active page, false if this page was the active page
		"""
		logging.info("OnPage({}, {})".format(page, activated))

	def OnSoftButton(self, buttons):
		"""
		Method called when a soft button changes. This should be overwritten by inheriting class
		Required Arguments:
		buttons - Buttons object representing button state
		"""
		logging.info("OnSoftButton({})".format(buttons))

	def SetProfile(self, profile):
		"""
		Sets the profile used on the device.
		Required Arguments:
		device_handle -- ID of device
		profile -- full path of the profile to activate. passing None will clear the profile.
		"""
		logging.debug("SetProfile({})".format(profile))
		return self.direct_output.SetProfile(self.device_handle, profile)

	def AddPage(self, page, name, active):
		"""
		Adds a page to the MFD. If overriden by a derived class, you should
		call super().AddPage(*args, **kwargs)
		Required Arguments:
		page -- page ID to add
		name -- String specifying page name
		active -- True if page is to become the active page, if False this will not change the active page
		"""
		logging.info("AddPage({}, {}, {})".format(page, name, active))
		self.direct_output.AddPage(self.device_handle, page, name, active)

	def RemovePage(self, page):
		"""
		Removes a page from the MFD
		Required Arguments:
		page -- page ID to remove
		"""
		logging.info("RemovePage({})".format(page))
		result = self.direct_output.RemovePage(self.device_handle, page)
		if result != S_OK:
			logging.error("RemovePage failed: {}".format(result))
			self.finish()
			raise DirectOutputError(result)

	def SetString(self, page, line, string):
		"""
		Sets a string to display on the MFD
		Required Arguments:
		page -- the ID of the page to add the string to
		line -- the line to display the string on (0 = top, 1 = middle, 2 = bottom)
		string -- the string to display
		"""
		logging.debug("SetString({}, {}, {})".format(page, line, string))
		result = self.direct_output.SetString(self.device_handle, page, line, string)
		if result != S_OK:
			logging.warning("SetString failed: {}".format(result))
			self.finish()
			raise DirectOutputError(result)

	def SetLed(self, page, led, value):
		"""
		Sets LED state on a given page
		Required Arguments:
		page -- page number
		led -- ID of LED to change
		value -- value to set LED (1 = on, 0 = off)
		"""
		logging.debug("SetLed({}, {}, {})".format(page, led, value))
		result = self.direct_output.SetLed(self.device_handle, page, led, value)
		if result != S_OK:
			logging.warning("SetLed failed: {}".format(result))
			self.finish()
			raise DirectOutputError(result)


class X52ProOutputDevice(DirectOutputDevice):
	class Page(object):
		_lines = [ str(), str(), str() ]
		_leds  = dict()

		def __init__(self, device, page_id, name, active):
			self.device = device
			self.page_id = page_id
			self.name = name
			self.device.AddPage(self.page_id, name, 1 if active else 0)
			self.active = active

		def __del__(self, *args, **kwargs):
			try:
				self.device.RemovePage(self.page_id)
			except AttributeError:
				pass

		def __getitem__(self, key):
			return self._lines[key]

		def __setitem__(self, key, value):
			self._lines[key] = value
			if self.active:
				self.device.SetString(self.page_id, key, value)

		def activate(self):
			if self.active == True:
				return
			self.device.AddPage(self.page_id, self.name, 1)

		def refresh(self):
			# Resend strings to the display
			for lineNo, string in enumerate(self._lines):
				self.device.SetString(self.page_id, lineNo, string)
			for led, value in self._leds:
				self.device.SetLed(self.page_id, led, 1 if value else 0)

		def set_led(self, led, value):
			self._leds[led] = value
			if self.active:
				self.device.SetLed(self.page_id, led, 1 if value else 0)

		def set_led_colour(self, value, led_red, led_green):
			if value == "red":
				self.set_led(led_red, 1)
				self.set_led(led_green, 0)
			elif value == "green":
				self.set_led(led_red, 0)
				self.set_led(led_green, 1)
			elif value == "orange":
				self.set_led(led_red, 1)
				self.set_led(led_green, 1)
			elif value == "off":
				self.set_led(led_red, 0)
				self.set_led(led_green, 0)

		def fire(self, value):
			self.set_led(0, value)

		def fire_a(self, value):
			self.set_led_colour(value, 1, 2)

		def fire_b(self, value):
			self.set_led_colour(value, 3, 4)

		def fire_d(self, value):
			self.set_led_colour(value, 5, 6)

		def fire_e(self, value):
			self.set_led_colour(value, 7, 8)

		def toggle_1_2(self, value):
			self.set_led_colour(value, 9, 10)

		def toggle_3_4(self, value):
			self.set_led_colour(value, 11, 12)

		def toggle_5_6(self, value):
			self.set_led_colour(value, 13, 14)

		def pov_2(self, value):
			self.set_led_colour(value, 15, 16)

		def clutch(self, value):
			self.set_led_colour(value, 17, 18)

		def throttle_axis(self, value):
			self.set_led(19, value)

	def __init__(self):
		self.pages = {}
		self._page_counter = 0
		super().__init__()

	def add_page(self, name, active=True):
		page = self.pages[name] = self.Page(self, self._page_counter, name, active=active)
		self._page_counter += 1
		return page

	def remove_page(self, name):
		del self.pages[name]

	def OnPage(self, page_id, activated):
		for page in self.pages.values():
			if page.page_id == page_id:
				print("Found the page", page_id, activated)
				if activated:
					page.refresh()
				else:
					page.active = False
				return

	def OnSoftButton(self, *args, **kwargs):
		print("*** ON SOFT BUTTON", args, kwargs)

	def finish(self):
		for page in self.pages:
			del page
		super().finish()


"""
Driver classes
"""


class DummyMfdDriver(object):
	def __init__(self):
		pass

	def finish(self):
		"""
			Close down the driver.
		"""
		pass

	def display(self, line1, line2="", line3="", delay=None):
		"""
			Display data to the MFD.
			Arguments: 1-3 lines of text plus optional pause in seconds.
		"""
		pass

	def attention(self, duration):
		"""
			Draw the user's attention.
		"""
		print("\a")


class X52ProMfdDriver(DummyMfdDriver):
	def __init__(self, doObj=None):
		super().__init__()
		try:
			if doObj is None:
				doObj = X52ProMfd()
			self.doObj = doObj
		except MissingDeviceError:
			print("{}: error: Could not find any X52 Pro devices attached to the system - please ensure your device is connected and drivers are installed.".format(__name__))
			sys.exit(1)
		except DLLError as e:
			print("{}: error#{}: Unable to initialize the Saitek X52 Pro module: {}".format(__name__, e.error_code, e.msg), file=sys.stderr)
			sys.exit(1)

		self.page = self.doObj.add_page('TD')
		self.display('TradeDangerous', 'INITIALIZING')


	def finish(self):
		self.doObj.finish()


	def display(self, line1, line2="", line3="", delay=None):
		self.page[0], self.page[1], self.page[2] = line1, line2, line3
		if delay:
			sleep(delay)

	def attention(self, duration):
		page = self.page
		iterNo = 0
		cutoff = time() + duration
		while time() <= cutoff:
			for ledNo in range(0, 20):
				page.set_led(ledNo, (iterNo + ledNo) % 4)
			iterNo += 1
			sleep(0.02)


"""
MFD classes
"""


class X52ProMfd(X52ProOutputDevice):
	def __init__(self):
		super().__init__()
		self.mfd_driver = X52ProMfdDriver(self)
		sleep(1)
		self.mfd_driver.doObj.PageShow()
	
	def display(self, line1, line2="", line3="", delay=None):
		self.mfd_driver.display(line1, line2, line3, delay)


class X52ProActionMfd(X52ProMfd):
	def __init__(self):
		self.lastinput = self.nowmillis()
		super().__init__()

	def nowmillis(self):
		millis = int(round(time() * 1000))
		return millis
	
	def addToClipBoard(text):
		command = 'echo ' + text.strip() + '| clip'
		os.system(command)

	def OnPage(self, page_id, activated):
		if page_id == 0 and activated:
			self.PageShow()

	def OnSoftButton(self, *args, **kwargs):
		if self.lastinput > self.nowmillis() - 200:
			return
		self.lastinput = self.nowmillis()

		if args[0].select:
			self.onScrollSelect()
		if args[0].up:
			self.onScrollUp()
		if args[0].down:
			self.onScrollDown()

		if (args[0].select or args[0].up or args[0].down):
			self.PageShow()
	
	def onScrollUp(self):
		pass
	
	def onScrollDown(self):
		pass

	def onScrollSelect(self):
		pass


class X52ProProfileMfd(X52ProActionMfd):
	def __init__(self):
		self.profile = self.update_profile_data()
		super().__init__()
		self.update_profile_data()

	def update_profile_data(self):
		self.profile = ''

	def use_profile_data(self):
		if self.profile is not None and self.profile.strip() != '':
			self.SetProfile(os.path.abspath(self.profile))


class X52ProScrollableMfd(X52ProProfileMfd):
	def __init__(self):
		self.cursor = 0
		self.entries = self.update_mfd_data()
		super().__init__()

	def update_mfd_data(self):
		return []

	def onScrollUp(self):
		self.cursor = (self.cursor - 1) % len(list(self.entries))
	
	def onScrollDown(self):
		self.cursor = (self.cursor + 1) % len(list(self.entries))

	def onScrollSelect(self):
		lines = list(self.entries)
		lines.sort()
		self.entry = lines[self.cursor]
		self.cursor = 0			

	def PageShow(self):
		lines = list(self.entries)
		lines.sort()
		cursor = self.cursor
		self.display(lines[(cursor - 1) % len(lines)], "> " + lines[(cursor + 0) % len(lines)], lines[(cursor + 1) % len(lines)])


class X52ProPageableMfd(X52ProProfileMfd):
	def __init__(self):
		self.cursor = 0
		self.mode = '0'
		self.entries = self.update_mfd_data()
		self.entry = ''
		super().__init__()

	def update_mfd_data(self):
		return {}

	def onScrollUp(self):
		if self.mode == '1':
			self.cursor = (self.cursor - 1) % len(self.entries[self.entry])
		else:
			self.cursor = (self.cursor - 1) % len(list(self.entries))
	
	def onScrollDown(self):
		if self.mode == '1':
			self.cursor = (self.cursor + 1) % len(self.entries[self.entry])
		else:
			self.cursor = (self.cursor + 1) % len(list(self.entries))

	def onScrollSelect(self):
		if self.mode == '1':
			# if in detail view, switch to system view and focus current system
			lines = list(self.entries)
			lines.sort()
			self.cursor = lines.index(self.entry);
			self.mode = '0'
		else:
			# else if main view, switch to detail for selected and jump to line 0
			lines = list(self.entries)
			lines.sort()
			self.entry = lines[self.cursor]
			self.mode = '1'
			self.cursor = 0

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


"""
Testing
"""


def test_direct_output_device():
	# If you want it to go to a file?
	# logging.basicConfig(filename='directoutput.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(name)s [%(filename)s:%(lineno)d] %(message)s')
	# If you want less verbose logging?
	# logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s [%(filename)s:%(lineno)d] %(message)s')
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s [%(filename)s:%(lineno)d] %(message)s')

	device = DirectOutputDevice(debug_level=1)
	print("Device initialized")

	device.AddPage(0, "Test", True)
	print("Test Page added")

	device.SetString(0, 0, "Test String")
	print("Test String added")

	device.AddPage(1, "Other", False)
	device.AddPage(2, "Another", False)

	while True:
		try:
			time.sleep(1)
		except:
			# This is used to catch Ctrl+C, calling finish method is *very* important to de-initalize device.
			device.finish()
			sys.exit()


def test_x52_pro_output_device():
	x52 = X52ProOutputDevice(debug_level=1)
	print("X52 Connected")

	x52.add_page("Page1")
	print("Page1 page added")

	x52.pages["Page1"][0] = "Test String"
	try:
		x52.pages["Page1"][5] = "FAIL"
		raise ValueError("Your stick thinks it has 5 lines of MFD, I think it lies.")
	except IndexError:
		print("Your MFD has the correct number of lines of text")

	x52.pages["Page1"][1] = "-- Page 1 [0]"

	fireToggle = False
	x52.pages["Page1"].fire(fireToggle)
	x52.pages["Page1"].fire_a("amber")
	x52.pages["Page1"].toggle_3_4("red")
	x52.pages["Page1"].throttle_axis(~fireToggle)

	print("Adding second page")
	x52.add_page("Page2", active=False)
	x52.pages["Page2"][0] = "Second Page Is Right Here"
	x52.pages["Page2"][1] = "-- Page 2 [1]"
	print("Looping")

	loopNo = 0
	while True:
		try:
			loopNo += 1
			x52.pages["Page1"][2] = "Loop #" + str(loopNo)
			sleep(0.25)
			x52.pages["Page1"].fire_a("red")
			sleep(0.25)
			x52.pages["Page1"].fire_a("orange")
			sleep(0.25)
			x52.pages["Page1"].fire_a("green")
			sleep(0.25)
			x52.pages["Page1"].fire_a("off")
			fireToggle = ~fireToggle
			x52.pages["Page1"].fire(fireToggle)
			x52.pages["Page1"].throttle_axis(~fireToggle)
		except Exception as e:
			print(e)
			x52.finish()
			sys.exit()


if __name__ == '__main__':
	# test_direct_output_device()
	# test_x52_pro_output_device()
	pass

