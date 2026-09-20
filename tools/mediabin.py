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
