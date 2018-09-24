### DEVELOPMENT IS STOPPED, NOW USING DIGIMEND DRIVERS

### Pen tablet functionality seems to be broken after a system update on Archlinux. Driver still works on Ubuntu 16.04. Seems to be an issue with the newer Linux kernel and how uinput interprets BTN\_TOOL\_PEN. Downgrading the kernel doesn't seem to fix the issue, may have to recompile the uinput module from an older kernel (<4.11) manually.

# pinspiroy 950

pinspiroy 950 is a linux driver workaround for the [HUION H950P (8192)](https://www.huiontablet.com/all-products/graphic-tablets/huion-h950p.html) forked from [pinspiroy](https://github.com/dannytaylor/pinspiroy). Note that this is not kernel-level driver, it is a user land implementation that creates virtual devices with uinput to mimic the tablet functionality.

All features of the tablet are working with this, but it isn't an ideal fix. Also I'm not too familiar with python so this might be implemented poorly. Hopefully this could be helpful for someone smarter than me to make a proper driver.

## Requirements
- [pyusb](https://walac.github.io/pyusb/) (pip install pyusb)
- [python-evdev](https://github.com/gvalkov/python-evdev) (pip install evdev)
- some things that should be already installed (libusb1.0, uinput) 

## Usage
_$ sudo python pinspiroy.py_

Configuration values are found in config.py. Currently it's just bools for rotating axes for left-handed. The pad buttons are setup to change positions when rotated also.
Added options for simple pressure curves and pressure needed for a full stroke. Defaults are linear pressure and 100% force for full pressure. I'd recommend using your art programs pressure adjustments instead of these options if you can.

Button and gesture bindings are found in bindings.py. Note: If you're adding new keys to your bindings you will have to add them to the virtual button pad capabilities: see 'cap_btn' in pinspiroy.py

## Configuring

I have the button and gesture bindings set up with the following for defaults

![](https://github.com/mhdchehade/pinspiroy/blob/master/docs/buttons.png)

Buttons clockwise from top left of trackpad:
```
button1: left control (hold)	# eyedropper
button2: E			# eraser tool
button3: spacebar (hold)	# pan tool
button4: shift (hold)		# brush resizer
button5: ctrl + shift + z	# redo
button6: wheel forward		# zoom in
button7: wheel backward		# zoom out
button8: ctrl + z		# undo
``


## Troubleshooting
This program requires the uinput module to be loaded. Either manually (_sudo modprobe uinput_)
or automatically on boot; [see the Arch wiki](https://wiki.archlinux.org/index.php/Kernel_modules).

**Insufficient permissions:** This program requires root access to read USB data (pyusb/libusb). You could add this to your sudoers file to run at start without password entry, but that is not recommended for security reasons.

**Pen not moving on contact, buttons and trackpad working:** This seems to be a problem with libinput requiring a pen resolution; changing the resolution with python-evdev doesn't seem to work. Check that you don't have a libinput driver catchall rule for tablets in your xorg.conf.d/. You may need a evdev driver catchall rule for tablets.

**Key error: NUM:** Run the debug.py file to see the array data the tablet is sending. The first array value should be 8. If it isn't (probably will be 10) the tablet isn't in full tablet mode. See usage section.

Still working out some of the problems, but feel free to tweet @ me or open an issue.

## TODO:
- load config by argument for program specific bindings
- add configuration for multiple monitors and irregular resolutions
