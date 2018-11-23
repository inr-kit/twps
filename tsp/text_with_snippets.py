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
The module defines function :func:`pre_pro`, which evaluates or executes python
snippets inside a text file, and replace snippet code with the
evaluation/execution result.

See detailed description in 'doc' directory of the source distribution.

.. todo::

    Optional parameter to prepro to indent all resulting text. (Thus,
    indentation will be defined in the parent template, not in the child
    template)

"""

# Author: Anton Travleev, anton.travleev@gmail.com
# Developed at INR, Karlsruhe Institute of Technology

import re
from textwrap import dedent
import sys
from os import path, chmod, getcwd, utime
from stat import S_IREAD, S_IWRITE


class _WritableObject:
    """
    Auxiliary class with a write method.  See
    http://stefaanlippens.net/redirect_python_print

    Instance of this class can be used to catch print outputs.  To redirect the
    print output, set sys.stdout to an instance of this class.

    Do not forget to set it back to sys.__stdout__
    """
    def __init__(self):
        self.content = []

    def write(self, string):
        self.content.append(string)


# ml = logger.MyLogger()

# if a link is used, one has to ensure that python still searches local
# directory for the modules. The local directory will be searched first.
sys.path.insert(0, getcwd())


# Options that modify positioning of snippet's result.
_OptionsList = [
    '-r',  # adjust right
    '-l',  # adjust left
    '-c',  # center
    '-d',  # delete snippet code, i.e. put to resulting file only result
    '-s',  # skip the snippet evaluation. Just leave its text representation
    '-D',  # default. Do not preserve snippet place.
    ]

messageError1line1 = """
ERROR in template: The first line of template must specify
                    optional comment string,  starting  and
                    ending delimiters,  i.e.  be at least 2
                    characters long."""
messageError1line2 = """
WARNING: the delimiter specified on the first line of
         the template, is alpha-numeric or blank.

         COMMENTING STRING: {0}
         STARTING DELIMITER: {1}
         ENDING DELIMITER: {2}"""


def firstline(l1):
    """
    Get commenting string, default key and delimiters from the 1-st line ``l``.
    """
    # Check the first line with comment and insertion marks.
    # Default parameters of the first line:
    TemplateOpt = '-D'
    Cchar = ''
    if len(l1) < 2:
        raise SystemExit(messageError1line1)
    else:
        # read the delimiters:
        Schar, Echar = l1[-2:]
        l1 = l1[:-2]
        if len(l1) > 0:
            # check if default snippet key is given in the first line:
            TemplateOpt = '-D'  # default option means do not preserve place.
            it = iter(l1)
            cprev = next(it)
            for c in it:
                if cprev + c in _OptionsList:
                    TemplateOpt = cprev + c
                    l1 = l1.replace(TemplateOpt, '')
                    break
                cprev = c
            # the rest in the 1st line is the string of commenting characters:
            Cchar = l1[:]  # empy indices to make copy of l1.

    # perform some check of the Schar and Echar:
    for char in [Schar, Echar]:
        if char.isalnum() or char == ' ':
            print >>sys.__stdout__, messageError1line2.format(Cchar, Schar, Echar)
            break  # one warning is enough

    # issue warning, if commenting char is empty:
    if Cchar == '':
        print >>sys.__stdout__, 'WARNING: string of commenting characters'
        print >>sys.__stdout__, '         is empty.  Multi-line  snippets'
        print >>sys.__stdout__, '         will not be commented out'
    return TemplateOpt, Cchar, Schar, Echar


def is_snippet(t, sch, ech):
    """
    Returns if ``t`` is a snippet. A snippet must start with sch and end
    with ech.
    """
    if t and t[0] == sch and t[-1] == ech:
        return True
    else:
        return False


def removeOpt(t, default):
    """
    Remove option of the next snippet from the text ``t`` preceeding it.
    """
    # Find options for the next snippet, remember them and remove them
    # from result:
    if t[-2:] in _OptionsList:
        SnippetOpt = t[-2:]
        if SnippetOpt == '-d':
            # just remove option from result. The following snippet
            # will be also removed.
            t = t[:-2]
        elif SnippetOpt == '-s':
            pass              # Do not remove snippet option.
        else:
            t = t[:-2] + '  '  # instead of option put spaces
    else:
        SnippetOpt = default
    return t, SnippetOpt


def pre_pro(fname, level='default', preamb=''):
    """
    Preprocess template file fname.

    :arg fname:

        String, name of the template file to be processed.

    :arg level:

        level is necessary to distinguish the top-level template from templates
        called from withing the top or above templates. Only for the top-level
        template (which has level not equal to 'default') all resulting strings
        are written to resulting file.

    :arg preamb:

        A string representing the snippet to be evaluated/executed before
        snippets in the file. This is to allow snippets in the command line.

    ``fname`` is a text file with python snippets. The function evaluates or
    executes snippets and replace the snippet code with the evaluation or
    execution result.

    If ``level`` is equal to ``default``, ther resulting text is returned as a
    list of strings. Otherwise, the resulting text will be written to file with
    the name ``fname + '.res'``, and the modification time of the resulting
    file will set to the modification time of the template.

    Before writing the resulting file, its modification time is compared with
    the modification time of the template. If the template is older (i.e. the
    resulting file was changed after it was generated with ``pre_pro``), the
    resulting file name will be prefixed with current date and time. Thus,
    changes introduced into resulting file (for example when a user accidentaly
    edits the resulting file instead of template) will not get lost.

    The template's first line must contain the two characters, used to denote
    the beginning and the end of snippets. Optionnaly, one can specify also in
    the first line the commenting string and snippet default key.

    """
    tfile = open(fname, 'rb')
    # check template and resulting files modification time with seconds
    # precision. More precision is not needed.
    tmtime = int(path.getmtime(tfile.name))
    tatime = int(path.getatime(tfile.name))
    s = tfile.read()
    print >>sys.__stdout__, 'Process file {0}'.format(tfile.name)

    # this is the 1-st line, without trailing spaces.  Do not put this line to
    # the resulting file. '+1' to avoid empty line at the begining of the
    # resulting file.
    l1 = s[:s.index('\n')].rstrip()
    s = s[s.index('\n')+1:]
    print >>sys.__stdout__, l1
    print >>sys.__stdout__, s
    TemplateOpt, Cchar, Schar, Echar = firstline(l1)

    # Regular expression to match insertions:
    t_ins = re.compile('(' + Schar + '.*?' + Echar + ')', re.DOTALL)

    # Add command line snippet as the first snippet to the file:
    if preamb:
        s = '-d{}{}{}'.format(Schar, preamb, Echar) + s

    # find all insertions in the file:
    # this splits the text into parts matching and not matching the pattern.
    spl = t_ins.split(s)
    print >>sys.__stdout__, spl

    #  define line numbers, where all spl elements start:
    nl_spl = [2]  # list of the line numbers
    for t in spl:
        nl_spl.append(nl_spl[-1] + t.count('\n'))

    # check for the unpaired delimiters. If they are,
    # the last element of spl should have one.
    if Schar in spl[-1] or Echar in spl[-1]:
        print >>sys.__stdout__, 'WARNING: there are unpaired delimiters.'

    # try to evaluate and to execute. Snippets are evaluated or executed in the
    # global namespace, which is returned by globals() function.  This ensures
    # that variables defined in one template will be visible in another
    # template.

    res = []  # resulting strings.
    for n, t in zip(nl_spl, spl):
        # If the first and last characters of the string in spl are
        # respectively Schar and Echar, this is a snippet string. Try to
        # evaluate or execute it.

        if not is_snippet(t, Schar, Echar):
            # this is not a snippet.

            # Find options for the next snippet, remember them and remove them
            # from result:
            t, SnippetOpt = removeOpt(t, TemplateOpt)
            # Just copy it to the resulting file.
            res.append(t)
        else:
            # if snippet option set to -s, skip the snippet, i.e., do not
            # evaluate it and put its string to the result
            if SnippetOpt == '-s':
                res.append(t)
            else:
                # this is a snippet. Evaluate or execute it.
                # Strip delimiters:
                snippet = t[1:-1]

                # prepare stdout capturer:
                # To separate outputs from different snippets, their stdouts
                # redirected to localy created instances of _WritableObject.
                # To ensure that execution of prepro does not change stdout for
                # parent scopes, sys.stdout is saved.

                pCatcher = _WritableObject()
                # save current stdout and stderr:
                curStdout = sys.stdout
                curStderr = sys.stderr
                # redirect output to local variables
                sys.stdout = pCatcher
                sys.stderr = pCatcher
                try:
                    # try to evaluate:
                    print >> sys.__stdout__,  'Evaluating ', snippet
                    tmp = eval(snippet, globals())
                    print >> sys.__stdout__, 'Evalueation result:', tmp
                    et = str(tmp)
                    # if the snippet can be evaluated, substitute it with the
                    # result of evaluation.  If the result is shorter than the
                    # snippet string, positioning of the result depends on
                    # SnippetOpt:
                    d = len(t) - len(et)
                    if d > 0:
                        if   SnippetOpt == '-l':
                            # adjust left:
                            et = et + ' '*d
                        elif SnippetOpt == '-r':
                            # adjust right:
                            et = ' '*d + et
                        elif SnippetOpt == '-c':
                            # center:
                            dl = d / 2
                            dr = d - dl
                            et = ' '*dl + et + ' '*dr

                    # add snippet evaluation result if no -d option is given.
                    if SnippetOpt != '-d':
                        res.append(et)
                except NameError as err:
                    # The NameError exception raises when e.g. expression is an
                    # undefined variable.  Issue a warning
                    print >>sys.__stdout__, 'WARNING: Snippet on line {0} in {1} caused evaluation error:'.format(n, fname)
                    print >>sys.__stdout__, '        ', err
                    # In this case, put the snippet itself to the output file:
                    res.append(t)
                except SyntaxError:
                    # If there is syntax error in evaluation, I try to execute
                    # the snippet.  If snippet is a multi-line snippet, it must
                    # be prepared for execution: indentation possibly used in
                    # the input file should be removed.
                    snippet = dedent(snippet)

                    # If snippet is multi-line, comment the snippet strings.
                    # Copy snippet to the result (do not copy if option -d is
                    # specified):
                    if SnippetOpt != '-d':
                        res.append(t.replace('\n', '\n'+Cchar))
                    try:
                        # try to execute the snippet:
                        exec(snippet, globals())
                    except:
                        exctype, excvalue = sys.exc_info()[:2]
                        print >>sys.__stdout__, 'WARNING: Snippet on line {0} in {1} caused execution error:'.format(n, fname)
                        print >>sys.__stdout__, '        ', excvalue
                        print >>sys.__stdout__, '        ', exctype
                except:
                    # evaluation can fail for some other reason. Try to catch
                    # it and report about it
                    exctype, excvalue = sys.exc_info()[:2]
                    print >>sys.__stdout__, 'WARNING: Snippet on line {0} in {1} caused evaluation error:'.format(n, fname)
                    print >>sys.__stdout__, '        ', excvalue
                    print >>sys.__stdout__, '        ', exctype
                    res.append(t)

                # if there were some outputs in snippet, add it to ther
                # resulting strings:
                res += pCatcher.content
                # return old stdout and stderr. Sys module belongs to globals,
                # therefore changing it inside a function will interfer also
                # parent functions. By setting it back, this interference is
                # avoided.
                sys.stdout = curStdout
                sys.stderr = curStderr

    if level != 'default':
        # if the level is not default, i.e. corresponds to the main template,
        # print resulting strings into file:
        rname = tfile.name + '.res'
        try:
            rfile = open(rname, 'w')
        except IOError as err:
            if err.errno == 13:
                # this is 'permission denied error', meaning that file exists
                # and cannot be rewritten.  Check that the template and rfile
                # have the same timestamps. If they are the same, it will be
                # assumed that the resulting file was created from template
                # without any other modifications and thus can be safely
                # rewritten again.
                rmtime = int(path.getmtime(rname))
                if tmtime >= rmtime:
                    chmod(rname, S_IWRITE)
                    rfile = open(rname, 'w')
                else:
                    # if timestamps of template and result differ, put new
                    # result to another file.
                    print >>sys.__stdout__, 'File {0} exists and is newer than the template.'.format(rname)
                    from datetime import datetime
                    tstmp = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
                    rfile = open(rname + tstmp, 'w')

        rfile.write(''.join(res))
        rfile.close()
        print >>sys.__stdout__, 'Result is written to {0}'.format(rfile.name)
        # Often, a user starts to change the resulting file instead of changing
        # the template, and all the changes went when the template is
        # processed. To warn user if he tries to change the resulting file, the
        # permission is set to 'read-only'.
        utime(rfile.name, (tatime, tmtime))
        chmod(rfile.name, S_IREAD)
    else:
        # when a template is included with the direct call to pre_pro,
        # the last line of the included template ands with the new-line
        # character. It is not needed.
        while res[-1][-1] in '\n\r':
            res[-1] = res[-1][:-1]
        return ''.join(res)


if __name__ == '__main__':
    from sys import argv
    pre_pro(fname=argv[1], level='main')

