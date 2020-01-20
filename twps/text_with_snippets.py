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
The module defines function :func:`pre_pro`, which evaluates or executes python
snippets inside a text file, and replace snippet code with the
evaluation/execution result.

See detailed description in 'doc' directory of the source distribution.

.. todo::


    * Indentation:

     Optional parameter to prepro to indent all resulting text. (Thus,
     indentation will be defined in the parent template, not in the child
     template)


    * Sequence of values for parametric studies

     Command line parameter specifying a seequence of input parameters.
     Generates several resulting files. Possible command line syntax:

        --ParameterName "python expression for sequence"

     i.e one can specify arbitrary variable name. If several ranges are given,
     the number of resulting files is N1 x N2 x ... Nm, where Ni -- number of
     values for i-th variable.

        --a "range(10)" --b "np.arange(0.01, 0.05, 10)"

"""

# Author: Anton Travleev, anton.travleev@gmail.com
# Developed at INR, Karlsruhe Institute of Technology

import re
from textwrap import dedent
import sys
import os
import traceback
from os import path, chmod, getcwd, utime
from stat import S_IREAD, S_IWRITE
from twps.utils import variants

# Log level:
#       0 -- errors
#       1 -- errors and warnings
#       2 -- errors, warnings and info
#       3 -- errors, warnings, info and debug.
_logLevel = 1  # 0 -- output at least.


class _Log(object):
    """
    To print out log information. Implemented as a class to contain
    snippet-specific information as instance properties.
    """
    def __init__(self, tname, level):
        """
        ``tname`` -- The current template filename
        ``level`` -- The log level. The bigger this value, the more
        information is printed out.
        """
        self.tname = tname  # Current template filename
        self.level = level  # Log level
        return

    def __call__(self, *args, **kwargs):
        self.log(*args, **kwargs)

    def log(self, mlev, msg, line=None, snippet=None):
        """
        Print message ``msg`` of the level ``mlev``. The message is actualy
        printed only if the message level is below the log level.

        When ``line`` and ``snippet`` are given, they are printed out too,
        to identify the snipped, to which the message corresponds.
        """
        sign = 'Message {} from {}'.format(mlev, self.tname)
        if line:
            sign += '\n    line {}'.format(line)
        if snippet:
            sign += '\n    snippet {}'.format(snippet)

        if mlev <= self.level:
            print >> sys.__stdout__, sign, msg


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
    'r',  # adjust right
    'l',  # adjust left
    'c',  # center
    'd',  # delete snippet code, i.e. put to resulting file only result
    's',  # skip the snippet evaluation. Just leave its text representation
    'D',  # default. Do not preserve snippet place.
    ]


def firstline(l1, _log):
    """
    Get commenting string, default key and delimiters from the 1-st line
    ``l1``.

    ``_log`` is a logger, used to print out warnings etc.
    """
    # Check the first line with comment and insertion marks.
    # Default parameters of the first line:
    TemplateOpt = '-D'
    Cchar = ''
    if len(l1) < 2:
        msg = """
        ERROR:
            The first line of template must specify optional comment string,
            starting  and ending delimiters,  i.e.  be at least 2 characters
            long."""
        msg = dedent(msg[1:])
        _log(0, msg, line=1)
        raise SystemExit(msg)
    else:
        # read the delimiters:
        Schar, Echar = l1[-2:]
        l1 = l1[:-2]
        # Read the default option, if given:
        if len(l1) >= 2:
            # 1st line can contain the default option in its first two chars.
            # Find the 1-st match of the option:
            r = re.compile('-[{}]'.format(''.join(_OptionsList)))
            f = r.findall(l1)
            if f:
                TemplateOpt = f[0]
                l1 = l1.replace(TemplateOpt, '')
        # read the commenting string, if given:
        if l1:
            Cchar = l1[:]

    # perform some check of the Schar and Echar:
    for char in [Schar, Echar]:
        if char.isalnum() or char == ' ':
            msg = """
            WARNING:
                the delimiter specified on the first line of
                the template, is alpha-numeric or blank.

                COMMENTING STRING: {0}
                STARTING DELIMITER: {1}
                ENDING DELIMITER: {2}""".format(Cchar, Schar, Echar)
            msg = dedent(msg[1:])
            _log(1, msg, line=1)
            break  # one warning is enough

    # issue warning, if commenting char is empty:
    if Cchar == '':
        msg = """
        WARNING:
            string of commenting characters is empty.
            Multi-line  snippets remain uncommented."""
        msg = dedent(msg[1:])
        _log(1, msg, line=1)
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
    if len(t) > 1 and t[-2] == '-' and t[-1] in _OptionsList:
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


# Global scope for all pre_pro calls.
gld = {}


def pre_pro(fname, level='default', preamb='', clp=[], **kwargs):
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

    :arg clp:

        A list of (name, vals) tuples, defining parameters for parametric
        studies.

    :arg kwargs:

        All other keyword arguments are valiable names and their set of values.
        Similar to ``clp``, but the order cannot be guarantied.

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
    _log = _Log(fname, _logLevel)
    # check template and resulting files modification time with seconds
    # precision. More precision is not needed.
    tmtime = int(path.getmtime(tfile.name))
    tatime = int(path.getatime(tfile.name))
    s = tfile.read()
    _log(0, 'Start processing')

    # this is the 1-st line, without trailing spaces.  Do not put this line to
    # the resulting file. '+1' to avoid empty line at the begining of the
    # resulting file.
    l1 = s[:s.index('\n')].rstrip()
    s = s[s.index('\n')+1:]
    TemplateOpt, Cchar, Schar, Echar = firstline(l1, _log)
    _log(3, 'First line: {0}'.format(l1))
    _log(3, 'Default option: {0}'.format(TemplateOpt))
    _log(3, 'Commenting str: {0}'.format(Cchar))
    _log(3, 'Delimiters    : {0} {1}'.format(Schar, Echar))

    # Regular expression to match insertions:
    t_ins = re.compile('(' + Schar + '.*?' + Echar + ')', re.DOTALL)

    # Add command line snippet as the first snippet to the file:
    if preamb:
        s = '-d{}{}{}'.format(Schar, preamb, Echar) + s

    # find all insertions in the file:
    # this splits the text into parts matching and not matching the pattern.
    spl = t_ins.split(s)

    #  define line numbers, where all spl elements start:
    nl_spl = [2]  # list of the line numbers
    for t in spl:
        nl_spl.append(nl_spl[-1] + t.count('\n'))
    nl_spl.pop(-1)
    _log(3, 'List of line numbers: {}'.format(nl_spl))
    _log(3, 'Text parts: {}'.format(spl))

    # check for the unpaired delimiters. If they are,
    # the last element of spl should have one.
    if Schar in spl[-1] or Echar in spl[-1]:
        _log(1, 'WARNING: there are unpaired delimiters.')

    # try to evaluate and to execute. Snippets are evaluated or executed in the
    # global namespace, which is returned by globals() function.  This ensures
    # that variables defined in one template will be visible in another
    # template.

    # Global scope for evaluating/execution of snippets.
    gld['pre_pro'] = pre_pro

    # Add parameter values from kwargs to clp
    clp = clp + kwargs.items()
    res = []  # resulting strings.
    _log(3, 'Complete set of parameters: {}'.format(clp))
    for pidx, Plst in variants(clp):
        _log(3, 'Current parameters: ' + repr(pidx) + repr(Plst))
        gld.update(dict(Plst))
        _log(3, 'Eval/exec scope: {}'.format(gld))

        for n, t in zip(nl_spl, spl):
            # If the first and last characters of the string in spl are
            # respectively Schar and Echar, this is a snippet string. Try
            # to evaluate or execute it.
            _log(3, 'Starting with', line=n, snippet=t)

            if not is_snippet(t, Schar, Echar):
                # this is not a snippet.

                # Find options for the next snippet, remember them and
                # remove them from result:
                t, SnippetOpt = removeOpt(t, TemplateOpt)
                # Just copy it to the resulting file.
                res.append(t)
                _log(3, 'Not a snippet')
            else:
                # if snippet option set to -s, skip the snippet, i.e., do
                # not evaluate it and put its string to the result
                if SnippetOpt == '-s':
                    _log(3, 'Skipping snippet evaluation')
                    res.append(t)
                else:
                    # this is a snippet. Evaluate or execute it.
                    # Strip delimiters:
                    snippet = t[1:-1]

                    # prepare stdout capturer:
                    # To separate outputs from different snippets, their
                    # stdouts redirected to localy created instances of
                    # _WritableObject.  To ensure that execution of prepro
                    # does not change stdout for parent scopes, sys.stdout
                    # is saved.

                    pCatcher = _WritableObject()
                    # save current stdout and stderr:
                    curStdout = sys.stdout
                    curStderr = sys.stderr
                    # redirect output to local variables
                    sys.stdout = pCatcher
                    sys.stderr = pCatcher
                    try:
                        # try to evaluate:
                        _log(3, 'Startnig snippet evaluation',
                                line=n, snippet=snippet)
                        tmp = eval(snippet, gld)
                        _log(3, 'Result: {}'.format(repr(tmp)))
                        et = str(tmp)
                        # if the snippet can be evaluated, substitute it
                        # with the result of evaluation.  If the result is
                        # shorter than the snippet string, positioning of
                        # the result depends on SnippetOpt:
                        d = len(t) - len(et)
                        if d > 0:
                            if SnippetOpt == '-l':
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

                        # add snippet evaluation result if no -d option is
                        # given.
                        if SnippetOpt != '-d':
                            res.append(et)
                    except NameError as err:
                        # The NameError exception raises when e.g.
                        # expression is an undefined variable.  Issue a
                        # warning
                        _log(1,
                             'WARNING: Snippet caused evaluation error',
                             line=n)
                        _log(1, err)
                        # In this case, put the snippet itself to the
                        # output file:
                        res.append(t)
                    except SyntaxError:
                        # If there is syntax error in evaluation, I try to
                        # execute the snippet.  If snippet is a multi-line
                        # snippet, it must be prepared for execution:
                        # indentation possibly used in the input file
                        # should be removed.
                        snippet = dedent(snippet)
                        _log(3,
                             'Executing snippet',
                             line=n, snippet=repr(snippet))

                        # If snippet is multi-line, comment the snippet
                        # strings.  Copy snippet to the result (do not copy
                        # if option -d is specified):
                        if SnippetOpt != '-d':
                            res.append(t.replace('\n', '\n'+Cchar))
                        try:
                            # try to execute the snippet:
                            exec(snippet, gld)
                        except Exception as ee:
                            exctype, excvalue = sys.exc_info()[:2]
                            _log(1, 'WARNING: '
                                    'Snippet caused execution error:',
                                    line=n, snippet=repr(snippet))
                            _log(3, ee)
                    except Exception as ee:
                        # evaluation can fail for some other reason. Try to
                        # catch it and report about it
                        exct, excv, tb = sys.exc_info()
                        _log(1, 'WARNING: '
                                'Snippet caused evaluation error:',
                                line=n, snippet=repr(snippet))
                        _log(3, ee)
                        traceback.print_tb(tb)
                        res.append(t)
                    # if there were some outputs in snippet, add it to ther
                    # resulting strings:
                    res += pCatcher.content
                    # return old stdout and stderr. Sys module belongs to
                    # globals, therefore changing it inside a function will
                    # interfer also parent functions. By setting it back,
                    # this interference is avoided.
                    sys.stdout = curStdout
                    sys.stderr = curStderr

        if level != 'default':
            # if the level is not default, i.e. corresponds to the main
            # template, print resulting strings into file.
            #
            # Note about the choice of resulting file name: Originally, I
            # used extension ``.t`` for the template files and added suffix
            # ``.res`` to the resulting filename, so that for a template
            # file ``inp.t`` the file ``inp.t.res`` was created. The
            # problem with this approach is that the template as well as
            # the resulting file extensions are not relevant for the syntax
            # highlighting scheme of vim. Another approach, currently
            # implemented is to preserve the extension of the template file
            # (which should be chosen to get the most relevantvim syntax
            # highlighting scheme) and optionally change the basename. For
            # example, for the result of preprocessing template
            # ``model.serp`` is ``model.r.serp`` or ``model.rN.serp``,
            # where ``N`` is the index for parametric studies.

            bname, extname = os.path.splitext(fname)
            pname = ('_{}'*len(pidx)).format(*pidx)
            if not pname:
                pname = 'res'
            rname = '{}.{}{}'.format(bname, pname, extname)
            _log(3, 'Output file:' + repr(rname))
            try:
                rfile = open(rname, 'w')
            except IOError as err:
                if err.errno == 13:
                    # this is 'permission denied error', meaning that file
                    # exists and cannot be rewritten.  Check that the
                    # template and rfile have the same timestamps. If they
                    # are the same, it will be assumed that the resulting
                    # file was created from template without any other
                    # modifications and thus can be safely rewritten again.
                    rmtime = int(path.getmtime(rname))
                    if tmtime >= rmtime:
                        chmod(rname, S_IWRITE)
                        rfile = open(rname, 'w')
                    else:
                        # if timestamps of template and result differ, put
                        # new result to another file.
                        _log(0, 'File exists and is newer than template')
                        from datetime import datetime
                        ts = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
                        rfile = open(rname + ts, 'w')

            rfile.write(''.join(res))
            rfile.close()
            res = []
            _log(0, 'Result is written to {0}'.format(rfile.name))
            # Often, a user starts to change the resulting file instead of
            # changing the template, and all the changes went when the
            # template is processed. To warn user if he tries to change the
            # resulting file, the permission is set to 'read-only'.
            utime(rfile.name, (tatime, tmtime))
            chmod(rfile.name, S_IREAD)
        else:
            # when a template is included with the direct call to pre_pro,
            # the last line of the included template ends with the new-line
            # character. It is not needed.
            res[-1] = res[-1][:-1]
    if level == 'default':
        # Return string for all input vlaues
        while res[-1] and res[-1][-1] in '\n\r':
            res[-1] = res[-1][:-1]
        return ''.join(res)


if __name__ == '__main__':
    from sys import argv
    pre_pro(fname=argv[1], level='main')
