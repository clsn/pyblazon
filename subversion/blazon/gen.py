#!/usr/bin/python
"""Use this file for invocation from the command line.

Example:

python gen.py Azure a bend or.
"""

import blazon
import sys

if __name__ == '__main__':
    cmdlineinput = " ".join(sys.argv[1:])
    curblazon = blazon.Blazon(cmdlineinput)
    print curblazon.GetShield()
