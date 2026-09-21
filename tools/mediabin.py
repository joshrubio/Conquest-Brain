# -*- coding: utf-8 -*-
"""
mediabin.py — locate ffmpeg / ffprobe.

Order: the system PATH, then the `static-ffmpeg` package (bundled binaries),
then `imageio-ffmpeg` (ffmpeg only). Import `FFMPEG` / `FFPROBE` and use them
in place of the bare "ffmpeg" / "ffprobe" strings in subprocess calls.

  pip install static-ffmpeg     # ffmpeg + ffprobe, no admin, no PATH edit
"""
import contextlib
import shutil
import sys


def cpu_threads(share=None):
    """How many CPU threads a long job may use: a share of the logical cores (default 60 %, at least 2), so
    the laptop keeps headroom for everything else. CONQUEST_CPU_SHARE (0.1-1.0) overrides it."""
    import os
    try:
        share = float(os.environ.get("CONQUEST_CPU_SHARE", share if share is not None else 0.6))
    except ValueError:
        share = 0.6
    return max(2, int((os.cpu_count() or 4) * max(0.1, min(1.0, share))))


def lower_priority():
    """Run this process below normal priority; child processes (ffmpeg) inherit it. A multi-hour render or
    transcription then yields to whatever the person is doing instead of making the laptop sluggish.
    Call it at the top of a long job's main."""
    import os
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            k = ctypes.windll.kernel32
            k.GetCurrentProcess.restype = wintypes.HANDLE             # untyped, the -1 pseudo-handle is truncated
            k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]   # to 32 bits and the call fails (err 6)
            k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000)     # BELOW_NORMAL_PRIORITY_CLASS
        except Exception:
            pass
    else:
        try:
            os.nice(10)
        except Exception:
            pass


@contextlib.contextmanager
def keep_awake():
    """Ask Windows not to idle-sleep while a long job runs (it's what killed an overnight
    4K master mid-bake, and stalled a 4K trim for 3 h). Released on exit / crash; does not
    stop a manual sleep, a laptop lid close, or non-Windows hosts (no-op there).
    SetThreadExecutionState is per-thread: hold it from the thread that waits for the job."""
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    set_state = None
    if sys.platform == "win32":
        try:
            import ctypes
            set_state = ctypes.windll.kernel32.SetThreadExecutionState
            set_state(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        except Exception:
            set_state = None
    try:
        yield
    finally:
        if set_state is not None:
            with contextlib.suppress(Exception):
                set_state(ES_CONTINUOUS)


def _resolve():
    ff, fp = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if ff and fp:
        return ff, fp
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()          # prepends its bin/ to this process's PATH
        ff = ff or shutil.which("ffmpeg")
        fp = fp or shutil.which("ffprobe")
    except Exception:
        pass
    if not ff:
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return ff or "ffmpeg", fp or "ffprobe"


FFMPEG, FFPROBE = _resolve()
HAVE_FFMPEG = FFMPEG != "ffmpeg" or shutil.which("ffmpeg") is not None
