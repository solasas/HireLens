"""Deterministic duration-in-months calculation for resume date ranges.

Pulled out of the model's responsibility on purpose: LLMs are unreliable
at arithmetic, so duration_months is recomputed here from start_date and
end_date whenever both can be confidently parsed, overriding whatever the
model reported. A date we can't parse is left exactly as the model
returned it rather than forced to null — an unusual-but-valid format
shouldn't erase real information.
"""

from datetime import date, datetime

_ONGOING_TOKENS = {"present", "current", "now", "ongoing", "till date", "to date"}

_DATE_FORMATS = ("%Y-%m-%d", "%Y-%m", "%Y/%m", "%m/%Y", "%B %Y", "%b %Y", "%Y")


def parse_flexible_date(value: str | None) -> date | None:
    """Parse a handful of common resume date formats. Returns None,
    never raises, for anything it doesn't recognize."""
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
        return date(parsed.year, parsed.month, 1)
    return None


def compute_duration_months(start_date: str | None, end_date: str | None) -> int | None:
    """Whole months between start_date and end_date. end_date may be an
    "ongoing" marker ("Present", "Current", ...), in which case today's
    date is used. Returns None if start_date isn't parseable."""
    start = parse_flexible_date(start_date)
    if start is None:
        return None

    if end_date and end_date.strip().lower() in _ONGOING_TOKENS:
        end = date.today()
    else:
        end = parse_flexible_date(end_date)

    if end is None:
        return None

    months = (end.year - start.year) * 12 + (end.month - start.month)
    return max(months, 0)
