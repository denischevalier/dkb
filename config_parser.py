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

import json
import sys
from copy import deepcopy

class ConfigParser():
    def __init__(self, config_file):
        with open(config_file, "rt") as in_file:                                            # Open the config file in read only mode 
            text = in_file.read()                                                           # Put its content in memory
        try:
            self.config = json.loads(text)                                                  # Parse json config
        except:
            print ('[WARNING] Error loading configuration file', file=sys.stderr)           # Warn on parsing error
        self.verif_config()                                                                 # Check the parsed data for errors

    def verif_config(self):
        print ('[DEBUG]Checking config file integrity',file=sys.stderr)

        # Test the root config object
        if len(self.config) == 0:                                                           # If the object is empty, return quitely
            return
        if str(type(self.config)) != "<class 'dict'>":                                      # The result object must be of type 'dict'
            raise Exception("The root type object is " + str(type(self.config)) + 
                    " instead of <class 'dict'>")

        newconf = deepcopy(self.config)                                                     # As some elements (comments) are deleted from 
                                                                                            # self.config during iteration, make the changes
                                                                                            # on a copy that will be synced after
        # Test the sub objects
        for key in self.config:                                                             # Loop over the config object
            if str(key) == '_comment':                                                      # Don't look at comments in config file.
                del (newconf[key])                                                          # Delete the comment line from the newconf copy of
                                                                                            # self.config
                continue                                                                    # Test the next 
            if str(type(self.config[key])) != "<class 'list'>":                             # The elements of the config oject must be
                                                                                            # of type 'list'
                raise Exception('The elements of the config object must be lists.\n'
                        'They actually are ' + str(type(self.config[key])))
            if len(self.config[key]) < 1 or len(self.config[key]) > 4:                      # Each element must have a maximum of 4 members
                raise Exception('The lists in config obj can\'t be longer than 4 members.')
            for elt in self.config[key]:                                                    # Loop over subelements
                if str(type(elt)) != "<class 'str'>":                                       # They must be strings
                    raise Exception('Each sublist member must be of type <class \'str\'>.\n'
                            'Found type ' + str(type(elt)) + ' instead.')
        self.config = newconf

    def get_config_action(self, buffer):
        for action in self.config:                                                          # Loop over the config object
            if self.config[action] == buffer[4-len(self.config[action]):]:                  # Compare the len(config keybind) last items in buffer
                                                                                            # Should the order not matter ? (should I use set?)
                return action                                                               # If there is a match, return the action
        return None                                                                         # Else return None


if __name__ == '__main__':
    # For debugging purposes only
    cp = ConfigParser('config_example.json')
    action = cp.get_config_action(['x', 'Ctrl', 'Maj', 'p'])
    print ('[DEBUG]' + str(action), file=sys.stderr)
    sys.exit(0)
