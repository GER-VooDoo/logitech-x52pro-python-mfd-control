# logitech-x52pro-python-wrapper

A easy-to-use python package to utilize the MFD on the Throttle of the Logitech X52 Pro, based on an older Saitek version of [headprogrammingczar](https://github.com/headprogrammingczar): [headprogrammingczar/mahon-mfd](https://github.com/headprogrammingczar/mahon-mfd)

## Usage:

Currently you have to modify the main.py file to edit the entries, JSON file support is in progress

```python
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
```

afterwards execute the `run.bat` file

## Changes:

### v0.0.1

* renamed files and cahnged file adn directory structure
* fixed ctypes function argtypes
* simplyfied classes and classnames
