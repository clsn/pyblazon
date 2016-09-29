#!/usr/bin/env python3
"""Use this file for invocation from the command line.

Example:

python gen.py Azure a bend or.
"""

import blazon
import sys
import getopt

if __name__ == '__main__':
    (options, argv)=getopt.getopt(sys.argv[1:], "nb:", ["no-outline","base="])
    base=None
    outline=True
    for k, v in options:
        if k in ("-b", "--base"):
            base=v
        if k in ("-n", "--no-outline"):
            outline=False
    cmdlineinput = " ".join(argv)
    curblazon = blazon.Blazon(cmdlineinput,base=base,outline=outline)
    print(curblazon.GetShield())
