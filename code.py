# AramCON 2 Badge Main Firmware
from arambadge import badge
from eeprom import EEPROM
import addons
import time
import supervisor
from welcome import show_welcome
from apps.menu.main import MenuApp

print("AramCON 2 Badge Firmware")

def i2c_device_available(i2c, addr):
    if i2c.try_lock():
        try:
            return addr in i2c.scan()
        finally:
            i2c.unlock()

def main_screen():
    try:
        badge.show_bitmap('nametag.bmp')
    except:
        show_welcome()
        badge.display.refresh()

e = EEPROM(badge.i2c)
menu = MenuApp()

main_screen()

last_addon = None
while True:
    for i in range(4):
        badge.pixels[i] = (255 * badge.left, 255 * badge.up, 255 * badge.right)
    badge.vibration = badge.down

    buttons = badge.gamepad.get_pressed()
    if buttons & badge.BTN_ACTION:
        # Wait until the action button is released
        badge.vibration = True
        while badge.gamepad.get_pressed() & badge.BTN_ACTION:
            pass
        badge.vibration = False
        menu.run()

    addon = addons.read_addon_descriptor(e)
    if addon:
        if last_addon != addon['driver']:
            print("Add-on connected: {}".format(addon['name']))
            last_addon = addon['driver']
            driver = __import__('drivers/' + addon['driver'].replace('.py', ''))
            had_error = True
            try:
                driver.main(addon)
                had_error = False
            finally:
                if had_error:
                    supervisor.reload()
    else:
        last_addon = None
