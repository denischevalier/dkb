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
    def __init__(self, event_queue, loggername, *args, **kwargs):
        threading.Thread.__init__(self)
        self.finished = threading.Event()

        self.q = event_queue
        self.loggername = loggername
        self.args = args
        self.kwargs = kwargs

        self.dir_lock = threading.RLock()
        self.timer_threads = {}
        self.task_function = self.process_event

    def run(self):
        while not self.finished.isSet():
            self.task_function(*self.args, **self.kwargs)

    def cancel(self):
        for key in list(self.timer_threads.keys()):
            self.timer_threads[key].cancel()
        self.finished.set() 

    def process_event(self):
        try:
            event = self.q.get(timeout=0.05)
            if not event.MessageName.startswith('key down'):
                print(('[INFO]Not an useful event'), file=sys.stderr)
                return
            process_name = self.get_process_name(event)
            self.ek = event.Key + '\n'
            p = Process(target=self.write_keycode)
            p.start()
            p.join()
            username = self.get_username()
        except queue.Empty:
            pass
        except:
            print(('[WARN] Some exception was caught in the logwriter loop...'), file=sys.stderr)
            pass

    def write_keycode(self):
        sys.stdout.write(self.ek)

    def get_process_name(self, event):
        return event.WindowProcName

    def get_username(self):
        return os.getenv('USER')

    def spawn_second_stage_thread(self):
        print(('[DEBUG]Entering second stage thread'),file=sys.stderr)
        self.sst_q = queue.Queue(0)
        self.sst = Logger(self.dir_lock,
                self.sst_q, self.loggername)

class KeyboardLogger:
    def __init__(self):
        self.spawn_event_threads()

        self.hm = pyxhook.HookManager()
        self.hm.HookKeyboard()
        self.hm.KeyDown = self.OnKeyDownEvent
        self.hm.KeyUp = self.OnKeyUpEvent

    def spawn_event_threads(self):
        self.event_threads = {}
        self.queues = {}
        try:
            self.queues["General"] = queue.Queue(0)
            self.event_threads["General"] = \
                Logger(self.queues["General"], "General")
        except KeyError:
            print(('[WARN]Not creating thread for section General'),file=sys.stderr)
            pass

    def start(self):
        for key in list(self.event_threads.keys()):
            print(('[INFO]Starting thread ' + key),file=sys.stderr)
            self.event_threads[key].start()
        self.hm.start()

    def push_event_to_queues(self, event):
        for key in list(self.queues.keys()):
            if ( str(event.Key) == 'Scroll_Lock' ):
                print('Scroll_Lock')                                                    # To permit keylog_parser.py to quit properly
                self.stop()
                return
            print(('[DEBUG]KeyDown'),file=sys.stderr)
            self.queues[key].put(event)

    def OnKeyDownEvent(self, event):
        self.push_event_to_queues(event)
        return True

    def OnKeyUpEvent(self,event):
        return True

    def stop(self):
        self.hm.cancel()

        for key in list(self.event_threads.keys()):
            self.event_threads[key].cancel()
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


