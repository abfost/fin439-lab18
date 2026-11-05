"""Small, testable helpers shared by the Streamlit app and its tests."""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:[-+−]?\$?|\$[-+−]?)(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:%)?"
)


def canonical_number(token: str) -> Decimal | None:
    """Make 3,501, $3,501, and 3501 compare as the same printed number."""
    cleaned = token.replace("$", "").replace(",", "").replace("%", "").replace("−", "-")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _numbers_in(value: Any) -> set[Decimal]:
    found: set[Decimal] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            # Check labels are printed by the script too (for example, 15%).
            found.update(_numbers_in(key))
            found.update(_numbers_in(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_numbers_in(item))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        found.add(Decimal(str(value)))
    elif isinstance(value, str):
        for token in NUMBER_RE.findall(value):
            number = canonical_number(token)
            if number is not None:
                found.add(number)
    return found


def unsupported_memo_numbers(memo: str, report: dict[str, Any]) -> list[str]:
    """Return each numeric token in a memo that EDGAR script output lacks."""
    allowed = _numbers_in(report)
    unsupported: list[str] = []
    for token in NUMBER_RE.findall(memo):
        number = canonical_number(token)
        if number is not None and number not in allowed and token not in unsupported:
            unsupported.append(token)
    return unsupported
