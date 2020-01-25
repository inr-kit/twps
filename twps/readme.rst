(P)ython (P)re(P)rocessor
===========================

This script is part of the ``twps`` Python package. Abbreviation "twps" means (T)ext (w)ith (P)ython (S)nippets preprocessor.

Usage:

   > ppp.py template.t [-'snippet'] [--'name1 vals1' --'name2 vals2' ...]

where ``template.t`` is a text file containing python snippets. Snippets are evaluated/executed and the snippet code is replaced with the result of evaluation/execution. The resulting file is saved to ``template.res.t``.

When optional command argument ``snippet`` is given, it is evaluated or executed before the snippets in the template file. If the snippet contains spaces, protect them with quotes, i.e. ``-'a = 5'``.

In the command line one can provide variable names and a set of their values.  The template will be processed  with all possible combinations of the variables. For example, if one argument starting with two dashes is given, :

   >ppp.py template.t --'v 1 2 3'
   
three resulting files will be created, named ``template._0.t``, ``template._1.t`` etc. The ``v`` variable will be set subsequently to each of the given values. If more than one ``--`` options are given, they constitute nested loops.

