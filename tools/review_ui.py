# -*- coding: utf-8 -*-
"""
review_ui.py — thin compatibility shim over tools/theme.py.

The whole design system moved to `theme.py` (one file, presentation only).
This module keeps the old import names working so callers don't churn:

    from review_ui import STYLE, HELPERS, page

New code should import from `theme` directly (`CSS`, `HELPERS`, `shell`).
Do not add CSS here — it belongs in `theme.py`.
"""
from theme import CSS as STYLE, HELPERS, shell  # noqa: F401


def page(title, header_html, body_html, script_html):
    return shell(title, header_html, body_html, script_html)
