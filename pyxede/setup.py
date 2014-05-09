############################################################################
#
# wxgui.py
#
# Copyright 2004-6 Donour Sizemore (donour@cs.uchicago.edu)
#
# This file is part of pyXede.
#
# pyXede is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyXede is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyXede; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
############################################################################

import sys
if sys.platform == "win32":
    from distutils.core import setup
    import py2exe

    setup(
        options = { 'py2exe' : {
        'excludes': ['javax.comm', 'wxversion'],
        'optimize': 2,
        }

        },
        version="0.5",
        name = "pyXede",
        windows = ["wxgui.py"],
        )

    import shutil
    shutil.copyfile("COPYING", "dist\COPYING")


SRCS = [
    "arch",
    "dyno",
    "gnuplot",
    "smooth",
    "pyxede"
    ]

import pydoc, os
for module in SRCS:
    pydoc.writedoc(module)
    os.rename(module+".html", "docs/"+module+".html")
