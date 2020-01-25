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
(T)ext with (S)nippets (P)reprocessor.

Package provides script ppp.py and function pre_pro().

THey can be used to find python snippets in a text file,
evaluate them and replace with the evaluation result.


From the command line, templates can be preprocessed
with ppp.py script, inside a python program the
pre_pro() function can be used.

"""

from text_with_snippets import pre_pro
from utils import params

try:
    from .version import version
except ImportError:
    # When cloned directly from git, version.py is not here
    version = 'git.development'
__version__ = version
