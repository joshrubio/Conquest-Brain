#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awake_until.py — keep Windows from idle-sleeping until the given process(es) exit.

  python tools/awake_until.py PID [PID ...]

For a long job that was already started WITHOUT mediabin.keep_awake() (its code was loaded
before that existed, so it cannot ask for it itself). It only holds a normal "system required"
request, the same one keep_awake() makes: it changes no power settings, and it stops when the
processes are gone. Does not stop a manual sleep or a lid close. No-op off Windows.
"""
import sys

from mediabin import keep_awake


def _wait(pid):
    import ctypes
    k = ctypes.windll.kernel32
    SYNCHRONIZE, INFINITE = 0x00100000, 0xFFFFFFFF
    h = k.OpenProcess(SYNCHRONIZE, False, int(pid))
    if not h:                                    # already gone
        return
    try:
        k.WaitForSingleObject(h, INFINITE)
    finally:
        k.CloseHandle(h)


if __name__ == "__main__":
    pids = [a for a in sys.argv[1:] if a.isdigit()]
    if not pids or sys.platform != "win32":
        sys.exit(__doc__)
    with keep_awake():
        for pid in pids:
            _wait(pid)
