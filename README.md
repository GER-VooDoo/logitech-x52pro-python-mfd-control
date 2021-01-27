# logitech-x52pro-python-mfd-control

A easy-to-use python3 package to utilize the MFD on the Throttle of the Logitech X52 Pro, based on an older Saitek version of [headprogrammingczar](https://github.com/headprogrammingczar): [headprogrammingczar/mahon-mfd](https://github.com/headprogrammingczar/mahon-mfd)

## Usage:

* edit the main.py file
* execute the `run.bat` file

## Modes

### JSON mode

JSON file support is still in development

### List mode

See the `main.py` file with the TestListMfd class

Example File:
```python
from x52pro import *
import os


class TestListMfd(X52ProScrollableMfd):
	def __init__(self):
		super().__init__()
	
    def update_profile_data(self):
        return os.path.join('test.pr0')
        # return ''
        
	def update_mfd_data(self):
        entries = []
        entries.append("Entry 1")
        entries.append("Entry 2")
        entries.append("Entry 3")
        entries.append("Entry 4")
        entries.append("Entry 5")
        entries.append("Entry 6")
        return entries


if __name__ == '__main__':
	TestListMfd()
	print("press <enter> to exit")
	input()
```

### Page mode

See the `main.py` file with the TestPageMfd class

Example File:
```python
from x52pro import *
import os

class TestPageMfd(X52ProPageableMfd):
	def __init__(self):
		super().__init__()
	
    def update_profile_data(self):
        return os.path.join('test.pr0')
        # return ''
    
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

        
if __name__ == '__main__':
	TestPageMfd()
	print("press <enter> to exit")
	input()
```

## Changes:

### v0.0.1

* renamed files and cahnged file adn directory structure
* fixed ctypes function argtypes
* simplyfied classes and classnames
