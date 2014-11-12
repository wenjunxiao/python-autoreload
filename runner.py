#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Runner for testing autoreload module."""

__author__="Wenjun Xiao"

import os,time,sys

def runner(name, debug):
    print "[%s]Enter..." % os.getpid()
    print "args:%s, debug:%s" % (name, debug)
    while 1:
        time.sleep(1)
        sys.stdout.flush()
    print "[%s]Exit." % os.getpid()

if __name__ == '__main__':
    from autoreload import run_with_reloader
    run_with_reloader(runner, 'test reloader', debug=True)
