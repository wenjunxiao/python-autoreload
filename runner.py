#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Runner for testing autoreload module."""

__author__="Wenjun Xiao"

import os,time

def runner():
    print "[%s]enter..." % os.getpid()
    print "[%s]Runner has changed." % os.getpid()
    while 1:
        time.sleep(1)
    print "[%s]runner." % os.getpid()

if __name__ == '__main__':
    from autoreload import run_with_reloader
    run_with_reloader(runner)
