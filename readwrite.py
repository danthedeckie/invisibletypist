#!/usr/bin/env python
'''
    readwrite.py
    first playing test code for invisibletypist screenless wordprocessor
    Copyright (C) 2014 Daniel Fairhead

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''


import sys, tty, termios
from subprocess import call

STDIN = sys.stdin.fileno()

class DeletePrevious(Exception):
    pass

def setup():
    before = termios.tcgetattr(STDIN)
    tty.setraw(STDIN)
    return before

def getword():
    word = []
    while True:
        ch = sys.stdin.read(1)
        if ch == '\x03':
            raise KeyboardInterrupt
        elif ch == '\x04':
            raise EOFError
        elif ch == '\x1b':
            if word:
                word = []
            else:
                raise DeletePrevious()
        elif ch not in ' \n\r\t,.':
            word.append(ch)
        else:
            return ''.join(word), ch

def say(word):
    try:
        call(['espeak', word])
    except OSError:
        print word


def main():
    before = setup()

    try:
        with open('output.txt', 'a') as output:
            word = ''
            br = ''
            while True:
                try:
                    newword, newbr = getword()
                    say(newword)

                    # now write previous word.  this is delayed so that 'ESC'
                    # works to cancel previous word.

                    output.write(word)
                    if br in ' \t':
                        output.write(br)
                    else:
                        output.write('\n')
                    output.flush()
                    word = newword
                    br = newbr

                except DeletePrevious:
                    word = ''

    finally:
        termios.tcsetattr(STDIN, termios.TCSADRAIN, before)

if __name__ == '__main__':
    main()
