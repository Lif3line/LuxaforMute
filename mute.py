from array import array
import usb.core  # pyusb
import usb.util
import os

BRIGHTNESS_MOD = 0.1
MUTED_COLOUR = [0, 128, 0]
NOT_MUTED_COLOUR = [255, 0, 0]

MODDED_MUTE_COLOUR = [int(round(x * BRIGHTNESS_MOD)) for x in MUTED_COLOUR]
MODDED_NOT_MUTED_COLOUR = [int(round(x * BRIGHTNESS_MOD)) for x in NOT_MUTED_COLOUR]


dev = usb.core.find(idVendor=0x04D8, idProduct=0xF372)

if dev is None:
    print("Luxafor Mute is not connected")
    exit
try:
    dev.detach_kernel_driver(0)
except usb.core.USBError:
    pass
try:
    dev.set_configuration()
except usb.core.USBError:
    print(
        "If you receive this error, it is likely you haven't configured the rule for the Luxafor device "
        + "or it is in use by another program"
    )
    exit

dev.set_configuration()
while True:
    data = dev.read(0x81, 0x8, 0)

    if data == array("B", [131, 1, 0, 0, 0, 0, 0, 0]):
        # Run pactl list and grep by input to find your microphone source, mine is 2 - yours could be different
        # The command bellow toggles the mute flag
        os.system("pactl set-source-mute @DEFAULT_SOURCE@ toggle")
        # This command gets the mute status of all devices, finds the final mute in the output and uses this to
        # figure out the current mute status of the microphone
        mute = os.popen(
            'CURRENT_SOURCE=$(pactl info | grep "Default Source" | cut -f3 -d" ");'
            + 'pactl list sources | grep -A 10 $CURRENT_SOURCE | grep "Mute: yes"'
        ).read()

        # Just a bit of logic to handle the colour of the light dependant on mute status
        # This part of the write command contains 8 bytes of data:
        # [1, 1, 255, 0, 0, 0, 0, 0]
        # Byte 1: Always set to 1 (Think this means solid colour)
        # Byte 2: Value is set as 1-6 for each LED in the device
        # Byte 3-5: RGB value for the colour you want to select
        # Byte 6-8: Not sure what these are for, likely to be flash patterns etc

        if "Mute: yes" in mute:
            for led_idx in range(1, 7):
                dev.write(1, [1, led_idx] + MODDED_MUTE_COLOUR + [0, 0, 0])

        else:
            for led_idx in range(1, 7):
                dev.write(1, [1, led_idx] + MODDED_NOT_MUTED_COLOUR + [0, 0, 0])
