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

import pyxhook
import time
import threading
import queue
import os
import sys
import signal

class BaseEventClass(threading.Thread):
    def __init__(self, event_queue, loggername, *args, **kwargs):
        threading.Thread.__init__(self)
        self.finished = threading.Event()

        self.q = event_queue
        self.loggername = loggername
        self.args = args
        self.kwargs = kwargs

    def cancel(self):
        self.finished.set()

    def run(self):
        while not self.finished.isSet():
                self.task_function(*self.args, **self.kwargs)

    def task_function(self):
        try:
            event = self.q.get(timeout=0.05)
            print(event, file=sys.stderr)
        except queue.Empty:
            pass
        except:
            print('[WARN]Some exception was caught in the logwriter loop...', file=sys.stderr)
            pass

class SecondStageBaseEventClass(BaseEventClass):
    def __init__(self, dir_lock, *args, **kwargs):
        BaseEventClass.__init__(self,*args,**kwargs)
        self.dir_lock = dir_lock

class DetailedLogWriterFirstStage(BaseEventClass):
    def __init__(self, *args, **kwargs):
        BaseEventClass.__init__(self, *args, **kwargs)

        self.dir_lock = threading.RLock()
        self.timer_threads = {}
        self.spawn_second_stage_thread()
        self.task_function = self.process_event

    def run(self):
        self.sst.start()
        BaseEventClass.run(self)

    def cancel(self):
        for key in list(self.timer_threads.keys()):
            self.timer_threads[key].cancel()
        self.sst.cancel()
        BaseEventClass.cancel(self)

    def process_event(self):
        try:
            event = self.q.get(timeout=0.05)
            if not event.MessageName.startswith('key down'):
                print(('[INFO]Not an useful event'), file=sys.stderr)
                return
            process_name = self.get_process_name(event)
            print((event.Key + '\n'))
            username = self.get_username()
            self.sst_q.put((process_name, username, event))
        except queue.Empty:
            pass
        except:
            print(('[WARN] Some exception was caught in the logwriter loop...'), file=sys.stderr)
            pass

    def get_process_name(self, event):
        return event.WindowProcName

    def get_username(self):
        return os.getenv('USER')

    def spawn_second_stage_thread(self):
        print(('[DEBUG]Entering second stage thread'),file=sys.stderr)
        self.sst_q = queue.Queue(0)
        self.sst = DetailedLogWriterSecondStage(self.dir_lock,
                self.sst_q, self.loggername)

class DetailedLogWriterSecondStage(SecondStageBaseEventClass):
    def __init__(self, dir_lock, *args, **kwargs):
        SecondStageBaseEventClass.__init__(self, dir_lock, *args, **kwargs)
        self.task_function = self.process_event
        self.eventlist = list(range(7))
        self.field_sep = ';'

    def process_event(self):
        try:
            (process_name, username, event) = self.q.get(timeout=0.05)
            eventlisttmp = [time.strftime('%Y%m%d'),
                    time.strftime('%H%M'),
                    process_name.replace(self.field_sep,
                        '[sep_key]'),
                    event.Window,
                    username.replace(self.field_sep,
                        '[sep_key]')]

            eventlisttmp.append(self.parse_event_value(event))

            if (self.eventlist[:6] == eventlisttmp[:6]):
                self.eventlist[-1] = self.eventlist[-1] + eventlisttmp[-1]
            else:
                self.write_to_logfile()
                self.eventlist = eventlisttmp
        except queue.Empty:
            if self.eventlist[:2] != list(range(2)) and \
                    self.eventlist[:2] != [time.strftime('%Y%m%d'),
                            time.strftime('%H%M')]:
                        self.write_to_logfile()
                        self.eventlist = list(range(7))
        except:
            pass

    def parse_event_value(self, event):
        npchrstr = "[KeyName:%keyname%]"
        npchrstr = re.sub('%keyname%', event.Key, npchrstr)

        if chr(event.Ascii) == selg.field_sep:
            return(npchrstr)

        # Backspace
        if event.Ascii == 8:
            return(npchrstr)

        # Escape
        if event.Ascii == 27:
            return(npchrstr)

        # Returns
        if event.Ascii == 13:
            return(npchrstr)

        if event.Ascii == 0:
            return(npchrstr)

        return(chr(event.Ascii))

    def write_to_logfile(self):
        if self.eventlist[:7] != list(range(7)):
            try:
                line = self.field_sep.join(self.eventlist)
                print(('[DEBUG]' + line), file=sys.stderr)
            except:
                pass

    def cancel(self):
        self.write_to_logfile()
        SecondStageBaseEventClass.cancel(self)

class DwmKeyboardBinder:
    def __init__(self):
        self.ControlKeyHash = \
                ControlKeyHash('F12')

        self.spawn_event_threads()
        self.hashchecker = ControlKeyMonitor(
                self.ControlKeyHash)

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
                DetailedLogWriterFirstStage(self.queues["General"], "General")
        except KeyError:
            print(('[WARN]Not creating thread for section General'),file=sys.stderr)
            pass

    def start(self):
        for key in list(self.event_threads.keys()):
            print(('[INFO]Starting thread ' + key),file=sys.stderr)
            self.event_threads[key].start()
        self.hashchecker.start()
        self.hm.start()

    def push_event_to_queues(self, event):
        for key in list(self.queues.keys()):
            if ( str(event.Key) == 'Scroll_Lock' ):
                self.stop()
                return
            print(('[DEBUG]KeyDown'),file=sys.stderr)
            self.queues[key].put(event)

    def OnKeyDownEvent(self, event):
        self.push_event_to_queues(event)
        self.ControlKeyHash.update(event)
        return True

    def OnKeyUpEvent(self,event):
        self.ControlKeyHash.update(event)
        return True

    def stop(self):
        self.hm.cancel()
        self.hashchecker.cancel()

        for key in list(self.event_threads.keys()):
            self.event_threads[key].cancel()
        time.sleep(0.2)
        sys.exit()

class ControlKeyHash:
    def __init__(self, controlkeysetting):
        lin_win_dict = {'Alt_l':'Lmenu',
                'Alt_r':'Rmenu',
                'Control_l':'Lcontrol',
                'Control_r':'Rcontrol',
                'Shift_l':'Lshift',
                'Shift_r':'Rshift',
                'Super_l':'Lwin',
                'Page_up':'Prior'}

        win_lin_dict = dict([(v,k) for (k,v) in list(lin_win_dict.items())])

        self.controlKeyList = controlkeysetting.split(';')

        self.controlKeyList = \
                [item.capitalize() for item in self.controlKeyList]
        self.controlKeyList = list(set(self.controlKeyList))
        for item in self.controlKeyList:
            if item in list(win_lin_dict.keys()):
                self.controlKeyList[self.controlKeyList.index(item)] = \
                        lin_win_dict[item]

        self.controlKeyHash = dict(list(zip(
            self.controlKeyList,
            [False for item in self.controlKeyList])))

    def update(self, event):
        if event.MessageName == 'key down' and \
                event.Key.capitalize() in list(self.controlKeyHash.keys()):
                    self.controlKeyHash[event.Key.capitalize()] = True
        if event.MessageName == 'key up' and \
                event.Key.capitalize() in list(self.controlKeyHash.keys()):
                    self.controlKeyHash[event.Key.capitalize()] = False

    def reset(self):
        for key in list(self.controlKeyHash.keys()):
            self.controlKeyHash[key] = False

    def check(self):
        if list(self.controlKeyHash.values()) == [True] * len(self.controlKeyHash):
            return True
        else:
            return False

    def __str__(self):
        return str(self.controlKeyHash)

class ControlKeyMonitor(threading.Thread):
    def __init__(self, controlkeyhash):
        threading.Thread.__init__(self)
        self.finished = threading.Event()

        self.ControlKeyHash = controlkeyhash

    def run(self):
        while not self.finished.isSet():
            if self.ControlKeyHash.check():
                self.ControlKeyHash.reset()
            time.sleep(0.95)

    def cancel(self):
        self.finished.set()

def SigIntHandler(signum, frame):
    print ('[WARNING]SIGINT (Ctrl+C) signal received, continuing: please exit dkb properly by pressing the Scoll_Lock keyboard key.',
            file=sys.stderr)

if __name__ == '__main__':
    # Set the signal handler for SIGINT
    signal.signal(signal.SIGINT, SigIntHandler)
    kl = DwmKeyboardBinder()
    kl.start()


