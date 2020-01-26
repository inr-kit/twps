TWPS: (T)ext (W)ith (P)ython (S)nippets
==========================================

A python package to preprocess text files with embedded Python code snippets:
evaluate or execute them and replace with the result of evaluation/execution.

This package provides the ``ppp.py`` script. The script reads the file
specified in the command line, finds python snippets, evaluates or executes
them and writes out the file with the pyhton code replaced with the
evaluateion/execution result. 

The following example shows a template file (i.e. the file to be processed with ppp.py) and the result.

.. list-table::
    :header-rows: 1

    * - Template (test/t1.t)
      - Resulting file (test/t1.res.t)
    * - ::

         ``
         The  characters on the 1-st line define
         the delimiters, used to mark the python
         snippets. In this case, both the begin
         of the snippet and its end are denoted
         with the backtick. 

         This is an evaluation snippet: `2*7`,
         and this is an execution snippet: 
         `from math import pi; pi2=pi*2`.

         Check that the definitions made in the
         previous snippets are accessible: `pi2`.

      - ::

         The  characters on the 1-st line define
         the delimiters, used to mark the python
         snippets. In this case, both the begin
         of the snippet and its end are denoted
         with the backtick. 

         This is an evaluation snippet: 14,
         and this is an execution snippet: 
         `from math import pi; pi2=pi*2`.

         Check that the definitions made in the
         previous snippets are accessible: 6.28318530718.


Install
----------
The package is published on PyPI: https://pypi.org/project/twps/. The preffered way to install is:

  >pip install twps

Getting help
--------------
For command line options see ``readme.rst`` in the ``twps`` folder or run the
script without command line arguemnt. 

General description with examples (somewhat outdated) can be found in the
``docs`` folder. 

