"""Generic text hygiene, with no dependency on the DB, HTTP, or any LLM
provider — usable from the PDF parser, request schemas, and the LLM
prompt layer alike, so this exists in exactly one place.
"""

import unicodedata

_ALLOWED_WHITESPACE = {"\n", "\t"}


def strip_control_characters(text: str) -> str:
    """Drop Unicode control/format/surrogate/private-use characters
    (categories starting with "C"), keeping plain newline and tab.

    Category Cf specifically includes zero-width characters and
    bidirectional-override characters (e.g. U+202E RIGHT-TO-LEFT
    OVERRIDE) — a known technique for hiding text from a human
    reviewing a document while it's still fully processed by software
    (including an LLM) reading the same bytes.
    """
    return "".join(
        ch
        for ch in text
        if ch in _ALLOWED_WHITESPACE or not unicodedata.category(ch).startswith("C")
    )
