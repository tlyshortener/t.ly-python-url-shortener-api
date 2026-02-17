from __future__ import annotations

from typing import Any


class TlyError(Exception):
    """Base exception for package errors."""


class TlyAPIError(TlyError):
    """Raised when the API returns a non-success status code."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_body: Any = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        super().__init__(f"T.LY API error ({status_code}): {message}")
