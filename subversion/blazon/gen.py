#!/usr/bin/python
import blazon
import sys

if __name__ == '__main__':
    cmdlineinput = " ".join(sys.argv[1:])
    curblazon = blazon.Blazon(cmdlineinput)
    print curblazon.GetShield()
