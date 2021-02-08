import pydirectinput as pdi
import pywinusb.hid as hid
import sys
import playsound 
import threading
import os
import signal
import sys
from random import *
from time import sleep
import vlc

mayflash_port_dict = {}
# First key is port number, second key is code from the usb report
gamecube_controller_keycode_dict = {
    1: {
        0: '', 
        1: 'x', 
        2: 'a', 
        4: 'b', 
        8: 'y', 
        16: 'l',
        32: 'r'
    }, 
    2: {
        0: '', 
        1: 'x', 
        2: 'a', 
        4: 'b', 
        8: 'y', 
        16: 'l',
        32: 'r'
    }, 
    3: {
        0: '', 
        1: 'x', 
        2: 'a', 
        4: 'b', 
        8: 'y', 
        16: 'l',
        32: 'r'
    }, 
    4: {
        0: '', 
        1: 'c', 
        2: 's', 
        4: 'n', 
        8: 'u', 
        16: ';',
        32: 't'
    }, 
}

bongos_keycode_dict = {
    1: {
        0: '', 
        1: 'a',     # top right
        2: 'b',     # bottom right
        4: 'c',     # bottom left
        8: 'd',     # top left
        16: 'e',    # start
        32: 'f'     # mic
    }, 
    2: {
        0: '', 
        1: 'g',     # top right
        2: 'h',     # bottom right
        4: 'i',     # bottom left
        8: 'j',     # top lefty
        16: 'k',    # start
        32: 'l'     # mic
    }, 
    3: {
        0: '', 
        1: 'x', 
        2: 'a', 
        4: 'b', 
        8: 'y', 
    }, 
    4: {
        0: '', 
        1: 'c', 
        2: 's', 
        4: 'n', 
        8: 'u', 
    }, 
}


class Bongo():
    def __init__(self, device, port):
        self.prev_keypress = None   # Prevent multiple keypresses from being registered by one button press
        self.port = port
        self.device = device
        self.mic_threshold = 100

    def button_handler(self, data):
        #print("Raw data: {0}".format(data))
        keycode = data[1]
        start_button = data[2]
        if start_button == 2:
            keycode = 16
        #microphone = data[8]
        #if microphone > self.mic_threshold:
        #    keycode = 32
        if keycode not in bongos_keycode_dict[self.port].keys():
            print('Error, unknown keypress!')
            return
        if self.prev_keypress != bongos_keycode_dict[self.port][keycode]:
            pdi.keyDown('shift')
            pdi.press(bongos_keycode_dict[self.port][keycode])
            pdi.keyUp('shift')
            print(f'Port: {self.port}, Keypress: {bongos_keycode_dict[self.port][keycode]}')
            self.prev_keypress = bongos_keycode_dict[self.port][keycode]

    def open(self):
        self.device.open()
        self.device.set_raw_data_handler(self.button_handler)
            
    def close(self):
        self.device.close()

# Play some dk tunes in the background
def start_tunes():
    playlist = os.listdir("./dk_music")
    shuffle(playlist)
    print(f'Playlst: {playlist}')
    for song in playlist:
        print(f'Now playing: {song}')
        playsound.playsound(f'./dk_music/{song}') 
    return

# Exit program with 'ctrl + c'
def signal_handler(sig, frame):
    print('Exiting Program!')
    for device in mayflash_port_dict:
        mayflash_port_dict[device].close()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    pdi.PAUSE = 0     # Get rid of built in 0.1 second lag between pydirectinput calls for faster response
    tunes = threading.Thread(target=start_tunes, daemon=True).start()
    hid_devices = hid.find_all_hid_devices()
    port = 1
    for index, device in enumerate(hid_devices):
        if 'mayflash' in device.product_name.lower():
            mayflash_port_dict[index] = Bongo(device, port)
            mayflash_port_dict[index].open()
            port += 1
    while 1:
        sleep(1)
    return

if __name__ == '__main__':
    main()
