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

import asyncio
import sys
import fileinput

if __name__ == '__main__':
    buffer = ['', '', '', '']                               # Always keep the last 4 typed keys
    for line in fileinput.input():                          # For each line in input
        if len(line.rstrip('\n')):                          # if the line is not only a newline
            buffer.pop(0)                                   # pop the first character in buffer (FIFO)
            buffer.append(line.rstrip('\n'))                # add the last typed key at the end of the buffer
            print('[DEBUG]' + str(buffer), file=sys.stderr) # [DEBUG] print the buffer

