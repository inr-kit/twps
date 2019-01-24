

Examples
==========

This section shows how the TSP package can be applied to tasks that often arise during preparation of 
complex input files. This covers inclusion of external files and templates and generation of a set of input 
files that differ by some parameter (for e.g. parametric studies).


Inclusion of external files
----------------------------
The TSP package provides no special mechanism to include external files into the resulting
file, however, one can use standard Python capabilities. In the following
example, an external file is read by the ``open`` [#]_ Python function and its
content is printed to the standard output. Since the standard output of the
snippet execution appears right after the snippet code, the file content will
appear in the resulting file.

.. [#] http://docs.python.org/library/functions.html#open

.. list-table::
    :header-rows: 1

    * - Template
      - Resulting file
    * - .. literalinclude:: examples/incl1.t

        where ``incl.txt`` has the following content: 
        
        .. literalinclude:: examples/incl.txt
     
      - .. literalinclude:: examples/incl1.res.t

The ``open`` function returns a file object that can be iterated line by line;
in the example above, the ``for`` loop iterates over all lines of the opened
file.  The file is opened with ``"r"`` key that means that the file is open
only for reading. Each line of the opened file is printed out. Note that the
print statement ends with the comma, this prevents extra empty lines in
the output. The snippet starts with the empty print statement, it adds a new
line just after the snippet's end marker in the resulting file, so that the
included file starts on the new line.


Inclusion of other templates
----------------------------
While in the above example inclusion of text file without any preprocessing is
shown, often it is necessary to include another template that needs first to be
preprocessed. To accomplish this task one needs to use directly the function
:func:`pre_pro` from the module :mod:`text_with_snippets` of the TSP package.
In simple situations this function is called by the preprocessor ``ppp.py`` so
that a user does not use it directly; this example shows how to use this
function directly in a template (or in a Python script).


The :func:`pre_pro` function  takes the name of a template file as argument and
returns the corresponding resulting file content as a multiline string.  This
function is imported by the script ``ppp.py`` and thus is accessible inside
snippets by default. To include the result of evaluation of another template,
simply call this function and print out its result:

.. list-table::
    :header-rows: 1

    * - Template 
      - Resulting file 
    * - .. literalinclude:: examples/incl2.t

        where ``itempl.txt`` has the following content: 
        
        .. literalinclude:: examples/itempl.txt

      - .. literalinclude:: examples/incl2.res.t

In this example, the snippet code is removed from the resulting file by
applying the ``-d`` snippet key. The snippet's output -- the result of
preprocessing of the template ``itempl.txt`` is thus written instead of the
snippet. To remove the extra new-line after the inserted template, the
``print`` statement is ended with comma. THe second snippet shows that the
``print`` statement is actually not necessary while the snippet is substituted
with its evaluation -- in this case with the result of preprocessing
``itempl.txt``, but here the ``-d`` would prevent the output completely. 

      
Multiple resulting files for parametric studies
------------------------------------------------
Sometime it is necessary to prepare many input files differing from each other
by some parameter(s). This task can be automatized without writing many template
files or manually changing parameters in the template.

The command line argument preceeded with single minus sign is considered as a
snippet and is processed before the template. Thus, one can set a variable in
the command line and use it inside the template. Calling preprocessor on the
same template with different command line snippet thus will result in different
resulting files. 

.. list-table::
    :header-rows: 1

    * - Template
      - Result of ``ppp.py param1.t``
      - Result of ``ppp.py -"a = 5"``

    * - .. literalinclude:: examples/param1.t

      - .. literalinclude:: examples/param1.res0.t

      - .. literalinclude:: examples/param1.res.t

When called without the snippet in the command line, the ``a`` variable is
undefined and the snippet raises an error. In the second call ``a`` is defined
in the command line snippet and the template processed without errors. The
preprocessor output is shown in the next table:

.. list-table::
    :header-rows: 1

    * - Result of ``ppp.py param1.t``
      - Result of ``ppp.py -"a = 5"``

    * - .. literalinclude:: examples/log.param1.t

      - .. literalinclude:: examples/log.param1-.t

One can also specify a list of values for a variable.

.. todo:: 

    Finish example with two lists of parameters.

