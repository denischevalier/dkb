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

class ConfigParser():
    def __init__(self, config_file):
        with open(config_file, "rt") as in_file:                                           # Open the config file in read only mode 
            text = in_file.read()                                                           # Put its content in memory
        self.config = json.loads(text)                                                      # Parse json config
        self.verif_config()                                                                 # Check the parsed data for errors

    def verif_config(self):
        print ('[DEBUG]Checking config file integrity',file=sys.stderr)

        # Test the root config object
        if len(self.config) == 0:                                                           # If the object is empty, return quitely
            return
        if str(type(self.config)) != "<class 'dict'>":                                           # The result object must be of type 'dict'
            raise Exception("The root type object is " + str(type(self.config)) + 
                    " instead of <class 'dict'>")

        # Test the sub objects
        for val in self.config:                                                             # Loop over the config object
            if str(type(val)) != "<class 'list'>":                                               # The elements of the config oject must be
                                                                                            # of type 'list'
                raise Exception('The elements of the config object must be lists.\n'
                        'They actually are ' + str(type(val)))
            if len(val) < 1 and len(val) > 4:                                               # Each element must have a maximum of 4 members
                raise Exception('The lists in config obj can\'t be longer than 4 members.')
            for elt in val:                                                                 # Loop over subelements
                if str(type(elt)) != "<class 'str'>":                                            # They must be strings
                    raise Exception('Each sublist member must be of type <class \'str\'>.\n'
                            'Found type ' + str(type(elt)) + ' instead.')

    def get_config_action(self, buffer):
        for action in self.config:                                                          # Loop over the config object
            if len(self.config[action]) == 1:                                               # A keybind can be of either 1, 2, 3 or 4 keys
                if buffer[4] == self.config[action]:                                        # Return action if the actual buffer matches the
                    return action                                                           # config.
            if len(self.config[action]) == 2:
                if buffer[3:4] == self.config[action]:
                    return action
            if len(self.config[action]) == 3:
                if buffer[2:4] == self.config[action]:
                    return action
            if len(self.config[action]) == 4:
                if buffer == self.config[action]:
                    return action
        return None                                                                         # Else return None


if __name__ == '__main__':
    # For debugging purposes only
    cp = ConfigParser('config_example.json')
    print (cp.get_config_action(['x', 'Ctrl', 'Maj', 'p']))
    sys.exit(0)
