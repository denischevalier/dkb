#!/usr/bin/python3
##########################################################################
##                                                                      ##
## dkb: Simple Python Keybinder for Linux                               ##
## Copyright (C) 2009  nanotube@users.sf.net                            ##
## Copyright (C) 2014  chevalierdenis@gmx.com                           ##
##                                                                      ##
## https://github.com/denischevalier/dkb                                ##
## Based on PyKeylogger AT http://pykeylogger.sourceforge.net           ##
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

from multiprocessing import Process
import pyxhook
import time
import os
import sys
import signal

class KeyboardLogger:
    def __init__(self):
        self.hm = pyxhook.HookManager()                             # Initialize HookManager
        self.hm.HookKeyboard()                                      # We're only interested in the keyboard events
        self.hm.KeyDown = self.OnKeyDownEvent                       # Bind self.OnKeyDownEvent() to hm.KeyDown

    def start(self):
        self.hm.start()                                              # Starting the HookManager

    def OnKeyDownEvent(self, event):
        if str(event.Key) == 'Scroll_Lock':                         # If we intercept the Scroll_Lock key (exit key)
            print('Scroll_Lock')                                    # Permit keylog_parser.py to quit properly
            self.hm.cancel()                                        # Stop the HookManager
            time.sleep(0.2)                                         # Wait for all threads to finish properly
            sys.exit(0)                                             # Exit with EXIT_SUCCESS

        self.keycode = event.Key                                    # Register the keycode internally
        p = Process(target=self.write_keycode)                      # Write the keycode asynchronously 
                                                                    # (to permit keylog_parser.py to accessit)
        p.start()                                                   # Start the process
        p.join()                                                    # Join the process with the current thread

    def write_keycode(self):
        sys.stdout.write(self.keycode + '\n')                       # Write the keycode to stdout

def SigIntHandler(signum, frame):
    print ('[WARNING]SIGINT (Ctrl+C) signal received, continuing:'
            'Please exit keyboard_logger.py properly by pressing '
            'the Scroll_Lock keyboard key.',
            file=sys.stderr)                                        # Disabling SIGINT to permit threads to finish
                                                                    # Properly by pressing Scroll_Lock

if __name__ == '__main__':
    signal.signal(signal.SIGINT, SigIntHandler)                     # Setting the signal handler for SIGINT
    kl = KeyboardLogger()                                           # Instanciating KeyboardLogger
    kl.start()                                                      # Starting the hook manager
