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
from twps import pre_pro, params


def main():
    msg = """
(P)ython (P)re(P)rocessor: script from the twps Python package. Abbreviation
"twps" means (T)ext with (S)nippets (P)reprocessor.

Usage:

> {} template.t [-'snippet'] [--'name1 vals1' --'name2 vals2' ...]

where `template.t' is a text file containing python snippets.  Snippets are
evaluated/executed and the snippet code is replaced with the result of
evaluation/execution. The resulting file is saved to `template.res.t'.

When optional `snippet` is given, it is evaluated or executed before the
snippets in `template.t`. If the snippet contains spaces, protect them with
quotes, i.e. -'a = 5'.

One can provide variable names and set of their values. The template will be
processed  with all possible combinations. For example, if one argument
starting with two dashes is given, i.e. --'v 1 2 3', three resulting files will
be created, named `template._0.t', `template._1.t' etc. The `v' variable will
be set subsequently to each of the given values. If more than one `--' options
are given, they constitute nested loops.

""".format(path.basename(argv[0]))

    if len(argv) < 2 or '--help' in ''.join(argv[1:]).lower():
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
                nvi = params(a[2:])
                clp.append(nvi)
            elif len(a) > 1 and a[:1] == '-':
                # this is a snippet
                preamb = a[1:]
            elif path.exists(a):
                templates.append(a)
            else:
                print 'Skipping argument', repr(a)

        if clp:
            print 'Parameters:', clp
        if preamb:
            print 'Command-line snippet:', preamb
        for t in templates:
            pre_pro(fname=t, level='main', preamb=preamb, clp=clp)


if __name__ == '__main__':
    main()
