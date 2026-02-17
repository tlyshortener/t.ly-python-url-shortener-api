from __future__ import annotations

from typing import Any

import pytest

from tly_url_shortener import TlyAPIError, TlyClient


class DummyResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        json_data: Any = None,
        text: str = "",
        headers: dict[str, str] | None = None,
        content: bytes = b"",
    ) -> None:
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = headers or {"Content-Type": "application/json"}
        self.content = content

    def json(self) -> Any:
        if self._json_data is not None:
            return self._json_data
        raise ValueError("No JSON")


class DummySession:
    def __init__(self, response: DummyResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> DummyResponse:
        self.calls.append(kwargs)
        return self.response

    def close(self) -> None:
        return None


def test_create_short_link_payload() -> None:
    session = DummySession(DummyResponse(json_data={"short_url": "https://t.ly/abc"}))
    client = TlyClient(api_token="token", session=session)

    result = client.create_short_link(long_url="https://example.com", description="d")

    assert result["short_url"] == "https://t.ly/abc"
    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.t.ly/api/v1/link/shorten"
    assert call["json"]["long_url"] == "https://example.com"
    assert call["json"]["description"] == "d"
    assert call["headers"]["Authorization"] == "Bearer token"


def test_create_short_link_allows_non_mapping_meta() -> None:
    session = DummySession(DummyResponse(json_data={"short_url": "https://t.ly/abc"}))
    client = TlyClient(api_token="token", session=session)

    client.create_short_link(long_url="https://example.com", meta=[[]])

    call = session.calls[0]
    assert call["json"]["meta"] == [[]]


def test_list_short_links_uses_indexed_arrays() -> None:
    session = DummySession(DummyResponse(json_data={"data": []}))
    client = TlyClient(api_token="token", session=session)

    client.list_short_links(tag_ids=[1, 2], pixel_ids=[8], domains=[3, 4])

    params = session.calls[0]["params"]
    assert ("tag_ids[0]", "1") in params
    assert ("tag_ids[1]", "2") in params
    assert ("pixel_ids[0]", "8") in params
    assert ("domains[0]", "3") in params
    assert ("domains[1]", "4") in params


def test_get_qr_code_binary() -> None:
    session = DummySession(
        DummyResponse(
            headers={"Content-Type": "image/png"},
            content=b"\x89PNG",
            text="",
        )
    )
    client = TlyClient(api_token="token", session=session)

    data = client.get_qr_code("https://t.ly/abc", output="image")

    assert isinstance(data, bytes)
    assert data == b"\x89PNG"


def test_get_qr_code_base64_json() -> None:
    session = DummySession(DummyResponse(json_data={"base64": "data:image/png;base64,AAAA"}))
    client = TlyClient(api_token="token", session=session)

    data = client.get_qr_code("https://t.ly/abc", output="base64")

    assert isinstance(data, dict)
    assert "base64" in data


def test_api_error_raised() -> None:
    session = DummySession(
        DummyResponse(status_code=422, json_data={"message": "Validation failed"}, text='{"message":"Validation failed"}')
    )
    client = TlyClient(api_token="token", session=session)

    with pytest.raises(TlyAPIError) as exc:
        client.create_tag("bad")

    assert exc.value.status_code == 422
    assert "Validation failed" in str(exc.value)
