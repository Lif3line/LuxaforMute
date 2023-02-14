# Luxafor Mute for Linux

This Python script will allow you to use your Luxafor Mute button with Linux.  I have tested this with ```Ubuntu 21.04```

## Pre requisites

### System

You will need to create a rule on your local machine before the script can be run, this allows your user access to the USB device.

Create a `luxafor.rules` file in `/etc/udev/rules.d/` containing:

``
SUBSYSTEM=="usb", ATTR{idVendor}=="04d8", ATTR{idProduct}=="f372" MODE="0664", OWNER="{Your user}"
``

Replace `{Your user}` with your Linux user.

Once this rule is in place you will need to run these commands to restart `udev`:

``
sudo udevadm control --reload
sudo udevadm trigger
``

### Script

I am using the `pactl` command to toggle the mute setting on the microphone.  This involves locating the microphone source, on my machine, the source is '2' - yours could be different.

To find your source, this command could help:

`pactl list | grep -e Source -e input`

In the script, replace the number 2 on this line, with the number of the source matching your microphone:

`            os.system("pactl set-source-mute 2 toggle")`

If you add a new input device to your machine, you'll have to update the script manually.  For example, if I add in wireless headphones - I have to update my source to '8'

## Running the Script

Setup a pipenv virtual env and then from command line run:

`python -m mute.py`

The script polls for input from the USB device in the background.

When the device is lit up red - your are muted.
When the device is lit up green - you are not muted.

The device will not show a colour until it is first tapped (using three fingers as per Luxafor documentation).

## Run on Boot

- `systemctl --user --force --full edit luxaformute.service`
- Needs to be `--user` to work with PulseAudio environment variables

```ini
[Unit]
Description=Luxafor Button Mute Service
After=default.target

[Service]
ExecStart=/usr/bin/python3 /home/lif3line/repos/LuxaforMute/mute.py

[Install]
WantedBy=default.target
```

- `systemctl --user enable --now luxaformute.service`
- `systemctl --user status luxaformute.service`
- Review outputs: `journalctl -b -e`
- `systemctl --user restart luxaformute.service`
