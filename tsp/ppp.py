#!/bin/env python
# Copyright 2012 Karlsruhe Institute of Technology (KIT)
#
# This file is part of TSP.
#
# TSP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TSP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Script provides command line interface to the TSP python package.

"""

# at
# Author: Anton Travleev, anton.travleev@gmail.com
# Developed at INR, Karlsruhe Institute of Technology
# at

from sys import argv
from os import path
from tsp import pre_pro


def main():
    msg = """
(P)ython (P)re(P)rocessor: script from the tsp Python package. Abbreviation
"tsp" means (T)ext with (S)nippets (P)reprocessor.

Usage:

> {} [-'snippet'] [--'var list_of_values'] template

where `template' is a text file containing python snippets.  Snippets are
evaluated/executed and the snippet code is replaced with the result of
evaluation/execution. The resulting file is saved to `template.res'.

Optional argument starting with single `-` is a snippet evaluated before
processing the template. Thus, one can e.g. define in the command line a
parameter used later in the template.

Optional argument(s) starting with two minus signs, `--`, define variables for
parametric studies. The string following `--` (possibly protected with single
or double quotes) defines the name of the variable and the list of values this
variable takes. The template is processed for each variable's value; the
resulting file is written to `template._i1_i2_..._iN`, where i1 is the index of
the 1-st variable's value, i2 -- the index of the second variable's value etc.
""".format(path.basename(argv[0]))

    if len(argv) < 2 or '--help' in ''.join(argv[1:]).lower():
        print msg
    else:
        # TODO analyse the command line arguments.
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
                # this is a list of variable names, preceeded with the var.name
                tokens = a[2:].split()
                vname = tokens.pop(0)
                try:
                    vals = map(int, tokens)
                except ValueError:
                    try:
                        vals = map(float, tokens)
                    except ValueError:
                        vals = map(None, tokens)
                clp.append((vname, vals))
            elif len(a) > 1 and a[:1] == '-':
                # this is a snippet
                preamb = a[1:]
            elif path.exists(a):
                templates.append(a)
            else:
                print 'Skipping argument', repr(a)

        for t in templates:
            pre_pro(fname=t, level='main', preamb=preamb, clp=clp)


if __name__ == '__main__':
    main()
