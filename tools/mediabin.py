# -*- coding: utf-8 -*-
"""
mediabin.py — locate ffmpeg / ffprobe.

Order: the system PATH, then the `static-ffmpeg` package (bundled binaries),
then `imageio-ffmpeg` (ffmpeg only). Import `FFMPEG` / `FFPROBE` and use them
in place of the bare "ffmpeg" / "ffprobe" strings in subprocess calls.

  pip install static-ffmpeg     # ffmpeg + ffprobe, no admin, no PATH edit
"""
import shutil


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
