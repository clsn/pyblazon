#!/usr/bin/python
"""Use this file for invocation from the command line.

Example:

python gen.py Azure a bend or.
"""

import blazon
import sys
import getopt

if __name__ == '__main__':
    (options, argv)=getopt.getopt(sys.argv[1:], "b:", ["base="])
    base=None
    for k, v in options:
        if k in ("-b", "--base"):
            base=v
    cmdlineinput = " ".join(argv)
    curblazon = blazon.Blazon(cmdlineinput,base=base)
    print curblazon.GetShield()
