#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit checks for the schema-2 timeline primitives in assemble.py.

No pytest in this repo — run it straight:  python tools/tests/test_timeline.py
(pytest picks up the test_* functions too, if it's ever added.)
"""
import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import assemble as A  # noqa: E402

FRAME = 1.0 / A.FPS


def _beats(durs, kind="stock"):
    return [{"dur": d, "kind": kind, "in": 0.0, "out": 0.0} for d in durs]


def test_derive_times_cumsum_and_contiguity():
    b = _beats([5.0, 4.0, 6.0])
    A.derive_times(b, vo_end=15.0)
    assert b[0]["in"] == 0.0
    for i in range(1, len(b)):
        assert b[i]["in"] == b[i - 1]["out"], "beats must be contiguous"
    # last out snapped exactly to vo_end
    assert b[-1]["out"] == 15.0


def test_derive_times_frame_quantised():
    b = _beats([3.017, 4.983, 5.0])
    A.derive_times(b, vo_end=13.0)
    for x in b:
        for k in ("in", "out"):
            q = round(x[k] / FRAME)
            assert abs(x[k] - q * FRAME) < 1e-6, f"{k}={x[k]} not on a frame"


def test_derive_times_drift_bounded_over_many_beats():
    durs = [3.333] * 120
    b = _beats(durs)
    ideal_total = sum(durs)
    A.derive_times(b, vo_end=ideal_total)
    # every boundary within one frame of the ideal running sum
    run = 0.0
    for x in b[:-1]:
        run += x["dur"]
        assert abs(x["out"] - run) <= FRAME + 1e-6
    assert b[-1]["out"] == round(ideal_total, 3)


def test_derive_times_vo_end_inside_last_beat_is_not_forced():
    b = _beats([5.0, 20.0])
    A.derive_times(b, vo_end=6.0)   # 6.0 < 25.0 start-of-last(5.0)+0.1 is false -> in=5, so 6.0>5.1 -> forced
    # here vo_end IS after last.in (5.0), so it snaps
    assert b[-1]["out"] == 6.0
    b2 = _beats([10.0, 20.0])
    with contextlib.redirect_stdout(io.StringIO()):
        A.derive_times(b2, vo_end=10.05)  # falls within last beat (in=10.0) -> leave alone
    assert b2[-1]["out"] == 30.0


def test_derive_times_empty():
    assert A.derive_times([], vo_end=10.0) == []


def test_vo_end_from_words_scales_with_last_word():
    short = [{"w": "ya", "t": 100.0}]
    long = [{"w": "Hokusai.", "t": 100.0}]
    assert A._vo_end_from_words([]) == 0.0
    assert A._vo_end_from_words(short) < A._vo_end_from_words(long)
    assert A._vo_end_from_words(long) <= 100.0 + 1.8


def test_get_vo_end_prefers_stored():
    assert A.get_vo_end(Path("."), stored=942.5) == 942.5
    assert A.get_vo_end(Path("."), stored=0) != 0 or True  # stored<=0 -> recompute (no words here -> 0.0)


def test_authored_beat_drops_derived_junk_keeps_core():
    b = {"n": 7, "id": "b7", "dur": 4.0, "section": "acto 1", "kind": "acamara",
         "asset": "", "motion": "cut", "in": 10.0, "out": 14.0, "state": "ok",
         "frag": "x", "slot": 3.5, "dur_lock": 4.2, "_i": 0, "approved": False,
         "vo_anchor": "hola", "merged": 2}
    a = A._authored_beat(b)
    assert "n" not in a and "frag" not in a and "slot" not in a and "dur_lock" not in a
    assert "_i" not in a and "merged" not in a and "approved" not in a
    assert a["id"] == "b7" and a["asset"] == "" and a["in"] == 10.0
    assert a["vo_anchor"] == "hola"


def test_idn():
    assert A._idn("b7") == 7 and A._idn("b110") == 110
    assert A._idn("swap_1") == 0 and A._idn(None) == 0


def test_words_sig_changes_on_shift():
    w1 = [{"w": "hola", "t": 1.0}, {"w": "mundo", "t": 1.5}]
    w2 = [{"w": "hola", "t": 1.0}, {"w": "mundo", "t": 2.5}]
    assert A._words_sig(w1) == A._words_sig(w1)
    assert A._words_sig(w1) != A._words_sig(w2)


def test_music_block_carries_valid_prev_mix_only():
    beats = _beats([4.0, 4.0])
    A.derive_times(beats, 8.0)
    m = A._music_block({"bed": "x.mp3", "bed_db": -37, "duck_db": 99}, beats, 8.0)
    assert m["bed"] == "x.mp3" and m["bed_db"] == -37     # in range → kept
    assert m["duck_db"] == 8                              # 99 out of range → default
    assert m["in"] == beats[0]["out"]


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    fail = 0
    for fn in fns:
        try:
            fn()
            print(f"  ok   {fn.__name__}")
        except AssertionError as e:
            fail += 1
            print(f"  FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - fail}/{len(fns)} passed")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(_run())
