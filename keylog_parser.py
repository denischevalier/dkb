#!/usr/bin/python3
##########################################################################
##                                                                      ##
## dkb: Simple Python Keybinder for Linux                               ##
## Copyright (C) 2014  chevalierdenis@gmx.com                           ##
##                                                                      ##
## https://github.com/denischevalier/dkb                                ##
##                                                                      ##
## This program is free software; you can redistribute it and/or        ##
## modify it under the terms of the GNU General Public License          ##
## as published by the Free Software Foundation; either version 3       ##
## of the License, or (at your option) any later version                ##
##                                                                      ##
## This program is distributed in the hope that it will be useful,      ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of       ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         ##
## GNU General Public License for more details.                         ##
##                                                                      ##
## You should have received a copy of the GNU General Public License    ##
## along with this program. If not, see <http://www.gnu.org/licenses/>. ##
##                                                                      ##
##########################################################################

import signal
import asyncio
import sys
import os
import time

from config_parser import ConfigParser

config_path='config.json'

class AsyncReader:
    def __init__(self):
        self.buffer = ['', '', '', '']                                  # We keep the 4 last keycodes
        self.lastinputtimestamp = 0;
        self.charbuf = ''                                               # Where everything is readed

    def start(self):
        loop = asyncio.get_event_loop()                                 # Get asyncio loop
        try:
            loop.call_soon(self.catch_keycodes, loop)                   # Launch catch_keycodes()
            loop.run_forever()                                          # Loop
        finally:
            loop.close()                                                # in the end quit properly

    def catch_keycodes(self, loop):
        data = sys.stdin.read(1)                                        # Get the last character
        if data != '\n':                                                # If we're not at an EOL and there is data
            self.charbuf += data                                        # Append data to charbuf
            loop.call_soon(self.catch_keycodes, loop)                   # Loop
        elif len (self.charbuf):                                        # End of a keycode
            if self.charbuf == 'Scroll_Lock':                           # If the keycode is Scroll_Lock
                loop.call_soon_threadsafe(loop.stop())                  # Exit properly
            asyncio.Task(self.parse_buffer())                           # Call parse_buffer() asynchronously
            loop.call_soon(self.catch_keycodes, loop)                   # Loop

    @asyncio.coroutine
    def parse_buffer(self):
        if (time.time() - self.lastinputtimestamp > 0.5 and             # Authorize a maximum of 0.5s between two keystrokes
            self.buffer[0:-1] != ['', '', '']):                         # unless it's only one key in the buffer (case of single key shorcuts)
            self.buffer = ['', '', '', '']                              # If not, empty buffer
        else:                                                           # If it's user did all the keys in a short amount of time
            self.buffer = \
                self.buffer[len(self.buffer)-3:len(self.buffer)]        # Delete buffer[0]
        self.lastinputtimestamp = time.time()
        self.buffer.append(self.charbuf)                                # Append charbuf to buffer
        self.charbuf = ''                                               # Empty charbuf
        print('[DEBUG]' + str(self.buffer), file=sys.stderr)            # Print the keycode
        cp = ConfigParser(config_path)                                  # ReParse the Config file as it permits user
                                                                        # to modify it on the fly
        action = cp.get_config_action(self.buffer)                      # Try the current buffer
        if action is not None:                                          # Did anything match ?
            print('[DEBUG]' + str(action), file=sys.stderr)             # Debugging informations: what did match
            os.system(action)                                           # Execute the command 
                                                                        # To execute in another child, just ad & at 
                                                                        # the end of command in config file

def SigIntHandler(signum, frame):
    print ('[WARNING]SIGINT (Ctrl+C) signal received, continuing:'
            'Please exit keylog_parser.py properly by passing "Scroll_Lock" to stdin.',
            file=sys.stderr)                                            # Cancel SIGINT to avoid bad multithreads/process/coroutine termination

if __name__ == '__main__':
    signal.signal(signal.SIGINT, SigIntHandler)                         # Set the signal handler for SIGINT
    ar = AsyncReader()                                                  # Create the object
    ar.start()                                                          # Start the event loop

