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
import threading
import queue
import os
import sys
import signal

class Logger(threading.Thread):
    def __init__(self, event_queue):
        threading.Thread.__init__(self)
        self.finished = threading.Event()
        self.q = event_queue

    def run(self):
        while not self.finished.isSet():
            self.process_event()

    def cancel(self):
        self.finished.set() 

    def process_event(self):
        try:
            event = self.q.get(timeout=0.05)
            self.eventkey = event.Key + '\n'
            p = Process(target=self.write_keycode)
            p.start()
            p.join()
        except queue.Empty:
            pass
        except:
            print(('[WARN] Some exception was caught in the Logger loop...'), file=sys.stderr)
            pass

    def write_keycode(self):
        sys.stdout.write(self.eventkey)

class KeyboardLogger:
    def __init__(self):
        self.queue = queue.Queue(0)
        self.event_thread = Logger(self.queue)
        self.hm = pyxhook.HookManager()
        self.hm.HookKeyboard()
        self.hm.KeyDown = self.OnKeyDownEvent

    def start(self):
        print(('[INFO]Starting Logger thread'), file=sys.stderr)
        self.event_thread.start()
        self.hm.start()

    def OnKeyDownEvent(self, event):
        if str(event.Key) == 'Scroll_Lock':
            print('Scroll_Lock')                    # Permit keylog_parser.py to quit properly
            self.stop()
            return
        self.queue.put(event)

    def stop(self):
        self.hm.cancel()
        self.event_thread.cancel()
        time.sleep(0.2)
        sys.exit()

def SigIntHandler(signum, frame):
    print ('[WARNING]SIGINT (Ctrl+C) signal received, continuing:Please exit keyboard_logger.py properly by pressing the Scroll_Lock keyboard key.',
            file=sys.stderr)

if __name__ == '__main__':
    # Set the signal handler for SIGINT
    signal.signal(signal.SIGINT, SigIntHandler)
    kl = KeyboardLogger()
    kl.start()


