#!/bin/env python
# Copyright 2012 Karlsruhe Institute of Technology (KIT)
#
# This file is part of TWPS.
#
# TWPS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWPS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Script provides command line interface to the TWPS python package.

"""

# at
# Author: Anton Travleev, anton.travleev@gmail.com
# Developed at INR, Karlsruhe Institute of Technology
# at

from sys import argv
from os import path
import twps  # from twps import pre_pro, params


def main():
    if len(argv) < 2 or '--help' in ''.join(argv[1:]).lower():
        readme = path.join(path.dirname(twps.__file__), 'readme.rst')
        with open(readme, 'r') as f:
            msg = f.read()
        print msg
    else:
        # All arguments starting with '--' are variable names, which list of
        # values is given as the next argument. The remaining argument is
        # considered as the 1-st snippet to evaluate.
        # --'a 1 2 3 4' --'b 6 7 8' -'c = 5'

        # Names and values of the parameter variables
        clp = []
        preamb = ''
        templates = []
        for a in argv[1:]:
            if len(a) > 2 and a[:2] == '--':
                nvi = twps.params(a[2:])
                clp.append(nvi)
            elif len(a) > 1 and a[:1] == '-':
                # this is a snippet
                preamb = a[1:]
            elif path.exists(a):
                templates.append(a)
            else:
                print 'Skipping argument (neither existing file nor recognized option)', repr(a)

        if clp:
            print 'Parameters:', clp
        if preamb:
            print 'Command-line snippet:', preamb
        for t in templates:
            twps.pre_pro(fname=t, level='main', preamb=preamb, clp=clp)


if __name__ == '__main__':
    main()
