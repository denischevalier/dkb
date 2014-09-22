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
import time

class AsyncReader:
    def __init__(self):
        self.buffer = ['', '', '', '']                                  # We keep the 4 last keycodes 
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
        self.buffer = self.buffer[len(self.buffer)-3:len(self.buffer)]  # Delete buffer[0]
        self.buffer.append(self.charbuf)                                # Append charbuf to buffer
        self.charbuf = ''                                               # Empty charbuf
        print('[DEBUG]' + str(self.buffer), file=sys.stderr)            # Print the keycode

def SigIntHandler(signum, frame):
    print ('[WARNING]SIGINT (Ctrl+C) signal received, continuing:'
            'Please exit keylog_parser.py properly by passing "Scroll_Lock" to stdin.',
            file=sys.stderr)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, SigIntHandler)                         # Set the signal handler for SIGINT
    ar = AsyncReader()                                                  # Create the object
    ar.start()                                                          # Start the event loop

