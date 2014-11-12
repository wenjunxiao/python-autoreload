#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module is used to reload the modules automatically when any changes is
detected. This work in deamon-mode, when any changes occurred, the subprocess
will be killed and start new subprocess, so the work will be interrupted for a
while, depending on the creating process.

This module is only independt on system modules(os,sys,time,etc), you can use
it as simply as pass you main loop to run_with_reloader in this module.

For examples::
    1. Pass main_loop to run_with_reloader::
    ----------------------------------------

        def main_loop(*args, **kwargs):
             while 1:
                do_something()

        run_with_reloader(main_loop, *args, **kwargs)
"""
__author__="Wenjun Xiao"

__all__ = [
    "run_with_reloader",
]

import os,sys,time,subprocess,thread,signal

def _iter_module_files():
    """Iterator to module's source filename of sys.modules (built-in 
    excluded).
    """
    for module in list(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename:
            if filename[-4:] in ('.pyo', '.pyc'):
                filename = filename[:-1]
            yield filename

def _is_any_file_changed(mtimes):
    """Return 1 if there is any source file of sys.modules changed,
    otherwise 0. mtimes is dict to store the last modify time for
    comparing."""
    for filename in _iter_module_files():
        try:
            mtime = os.stat(filename).st_mtime
        except IOError:
            continue
        old_time = mtimes.get(filename, None)
        if old_time is None:
            mtimes[filename] = mtime
        elif mtime > old_time:
            return 1
    return 0

def _start_change_detector(interval = 1):
    """Check file state ervry interval. If any change is detected, exit this
    process with a special code, so that deamon will to restart a new process.
    """
    mtimes = {}
    while 1:
        if _is_any_file_changed(mtimes):
            sys.exit(3)
        time.sleep(1)

# current subprocess
_sub_proc = None

def _signal_handler(*args):
    """Signal handler for process terminated. If there is a subprocess, 
    terminate it firstly."""
    global _sub_proc
    if _sub_proc:
        _sub_proc.terminate()
    sys.exit(0)

def _restart_with_reloader():
    """Deamon for subprocess."""
    signal.signal(signal.SIGTERM, _signal_handler)
    while 1:
        args = [sys.executable] + sys.argv
        if sys.platform == "win32":
            args = ['"%s"' % arg for arg in args]
        new_env = os.environ.copy()
        new_env['RUN_FLAG'] = 'true'
        global _sub_proc
        _sub_proc = subprocess.Popen(args, env=new_env, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        _ridrect_stdout(_sub_proc.stdout)
        exit_code = _sub_proc.wait()
        if exit_code != 3:
            return exit_code

def _ridrect_stdout(stdout):
    """Redirect stdout to current stdout."""
    while 1:
        data = os.read(stdout.fileno(), 2**15)
        if len(data) > 0:
            sys.stdout.write(data)
        else:
            stdout.close()
            sys.stdout.flush()
            break

def run_with_reloader(runner, *args, **kwargs):
    """Run the runner with reloader.

    Args::
        runner: main loop function.
        args: arguments for runner.
        kwargs: arguments for runner.
    """
    if os.environ.get('RUN_FLAG') == 'true':
        thread.start_new_thread(runner, args, kwargs)
        try:
            _start_change_detector()
        except KeyboardInterrupt:
            pass
    else:
        try:
            sys.exit(_restart_with_reloader())
        except KeyboardInterrupt:
            pass
