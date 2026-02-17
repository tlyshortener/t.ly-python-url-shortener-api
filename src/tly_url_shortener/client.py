from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any, Union
from urllib.parse import urljoin

import requests

from .exceptions import TlyAPIError

JSONScalar = Union[str, int, float, bool, None]
JSONValue = Union[JSONScalar, dict[str, "JSONValue"], list["JSONValue"]]


def _as_iso(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _add_indexed_params(
    target: list[tuple[str, str]],
    key: str,
    values: Sequence[int | str] | None,
) -> None:
    if not values:
        return
    for idx, value in enumerate(values):
        target.append((f"{key}[{idx}]", str(value)))


class TlyClient:
    """Python client for the T.LY URL Shortener API."""

    def __init__(
        self,
        api_token: str,
        *,
        base_url: str = "https://api.t.ly",
        timeout: float = 30.0,
        user_agent: str = "tly-url-shortener-api/0.1.0",
        session: requests.Session | None = None,
    ) -> None:
        if not api_token:
            raise ValueError("api_token is required")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.default_headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": user_agent,
        }

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "TlyClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def _build_headers(self, headers: Mapping[str, str] | None) -> dict[str, str]:
        merged = dict(self.default_headers)
        if headers:
            merged.update(dict(headers))
        return merged

    def _normalize_path(self, path: str) -> str:
        return path if path.startswith("/") else f"/{path}"

    def _extract_error_message(self, response: requests.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text or "Request failed"

        if isinstance(payload, dict):
            if isinstance(payload.get("message"), str):
                return payload["message"]
            if isinstance(payload.get("error"), str):
                return payload["error"]
            if isinstance(payload.get("errors"), (dict, list)):
                return str(payload["errors"])
        return str(payload)

    def _parse_response(self, response: requests.Response, expect_binary: bool) -> Any:
        if expect_binary:
            return response.content

        text = response.text.strip()
        if not text:
            return {}
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/json" in content_type or text.startswith(("{", "[")):
            return response.json()
        return text

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
        json_body: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        expect_binary: bool = False,
    ) -> Any:
        normalized_path = self._normalize_path(path)
        url = urljoin(f"{self.base_url}/", normalized_path.lstrip("/"))
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json_body,
            headers=self._build_headers(headers),
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise TlyAPIError(
                status_code=response.status_code,
                message=self._extract_error_message(response),
                response_body=response.text,
            )
        return self._parse_response(response, expect_binary=expect_binary)

    def get_onelink_stats(
        self,
        short_url: str,
        *,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> dict[str, Any]:
        params = {"short_url": short_url}
        if start_date is not None:
            params["start_date"] = _as_iso(start_date)
        if end_date is not None:
            params["end_date"] = _as_iso(end_date)
        return self.request("GET", "/api/v1/onelink/stats", params=params)

    def delete_onelink_stats(self, short_url: str) -> dict[str, Any]:
        return self.request(
            "DELETE",
            "/api/v1/onelink/stat",
            json_body={"short_url": short_url},
        )

    def create_short_link(
        self,
        long_url: str,
        *,
        domain: str | None = None,
        expire_at_datetime: date | datetime | str | None = None,
        description: str | None = None,
        public_stats: bool | None = None,
        meta: JSONValue | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"long_url": long_url}
        if domain is not None:
            payload["domain"] = domain
        if expire_at_datetime is not None:
            payload["expire_at_datetime"] = _as_iso(expire_at_datetime)
        if description is not None:
            payload["description"] = description
        if public_stats is not None:
            payload["public_stats"] = public_stats
        if meta is not None:
            payload["meta"] = meta
        return self.request("POST", "/api/v1/link/shorten", json_body=payload)

    def get_short_link(self, short_url: str) -> dict[str, Any]:
        return self.request("GET", "/api/v1/link", params={"short_url": short_url})

    def update_short_link(
        self,
        short_url: str,
        *,
        long_url: str | None = None,
        expire_at_datetime: date | datetime | str | None = None,
        description: str | None = None,
        public_stats: bool | None = None,
        meta: JSONValue | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"short_url": short_url}
        if long_url is not None:
            payload["long_url"] = long_url
        if expire_at_datetime is not None:
            payload["expire_at_datetime"] = _as_iso(expire_at_datetime)
        if description is not None:
            payload["description"] = description
        if public_stats is not None:
            payload["public_stats"] = public_stats
        if meta is not None:
            payload["meta"] = meta
        return self.request("PUT", "/api/v1/link", json_body=payload)

    def delete_short_link(self, short_url: str) -> dict[str, Any]:
        return self.request(
            "DELETE",
            "/api/v1/link",
            json_body={"short_url": short_url},
        )

    def expand_short_link(
        self,
        short_url: str,
        *,
        password: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"short_url": short_url}
        if password is not None:
            payload["password"] = password
        return self.request("POST", "/api/v1/link/expand", json_body=payload)

    def list_short_links(
        self,
        *,
        search: str | None = None,
        tag_ids: Sequence[int | str] | None = None,
        pixel_ids: Sequence[int | str] | None = None,
        domains: Sequence[int | str] | None = None,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> dict[str, Any]:
        params: list[tuple[str, str]] = []
        if search is not None:
            params.append(("search", search))
        _add_indexed_params(params, "tag_ids", tag_ids)
        _add_indexed_params(params, "pixel_ids", pixel_ids)
        _add_indexed_params(params, "domains", domains)
        if start_date is not None:
            params.append(("start_date", _as_iso(start_date) or ""))
        if end_date is not None:
            params.append(("end_date", _as_iso(end_date) or ""))
        return self.request("GET", "/api/v1/link/list", params=params)

    def bulk_shorten_links(
        self,
        links: Sequence[Mapping[str, Any]] | str,
        *,
        domain: str | None = None,
        tags: Sequence[int | str] | None = None,
        pixels: Sequence[int | str] | None = None,
    ) -> Any:
        payload: dict[str, Any] = {"links": links}
        if domain is not None:
            payload["domain"] = domain
        if tags is not None:
            payload["tags"] = list(tags)
        if pixels is not None:
            payload["pixels"] = list(pixels)
        return self.request("POST", "/api/v1/link/bulk", json_body=payload)

    def bulk_update_links(
        self,
        links: Sequence[Mapping[str, Any]] | str,
        *,
        tags: Sequence[int | str] | None = None,
        pixels: Sequence[int | str] | None = None,
    ) -> Any:
        payload: dict[str, Any] = {"links": links}
        if tags is not None:
            payload["tags"] = list(tags)
        if pixels is not None:
            payload["pixels"] = list(pixels)
        return self.request("POST", "/api/v1/link/bulk/update", json_body=payload)

    def get_link_stats(
        self,
        short_url: str,
        *,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> dict[str, Any]:
        params = {"short_url": short_url}
        if start_date is not None:
            params["start_date"] = _as_iso(start_date)
        if end_date is not None:
            params["end_date"] = _as_iso(end_date)
        return self.request("GET", "/api/v1/link/stats", params=params)

    def create_utm_preset(
        self,
        *,
        name: str,
        source: str,
        medium: str,
        campaign: str,
        content: str | None = None,
        term: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": name,
            "source": source,
            "medium": medium,
            "campaign": campaign,
        }
        if content is not None:
            payload["content"] = content
        if term is not None:
            payload["term"] = term
        return self.request("POST", "/api/v1/link/utm-preset", json_body=payload)

    def list_utm_presets(self) -> list[dict[str, Any]]:
        return self.request("GET", "/api/v1/link/utm-preset")

    def get_utm_preset(self, preset_id: int | str) -> dict[str, Any]:
        return self.request("GET", f"/api/v1/link/utm-preset/{preset_id}")

    def update_utm_preset(
        self,
        preset_id: int | str,
        *,
        name: str,
        source: str,
        medium: str,
        campaign: str,
        content: str | None = None,
        term: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": name,
            "source": source,
            "medium": medium,
            "campaign": campaign,
        }
        if content is not None:
            payload["content"] = content
        if term is not None:
            payload["term"] = term
        return self.request("PUT", f"/api/v1/link/utm-preset/{preset_id}", json_body=payload)

    def delete_utm_preset(self, preset_id: int | str) -> dict[str, Any]:
        return self.request("DELETE", f"/api/v1/link/utm-preset/{preset_id}")

    def list_onelinks(self, *, page: int | None = 1) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        return self.request("GET", "/api/v1/onelink/list", params=params)

    def create_pixel(
        self,
        *,
        name: str,
        pixel_id: str,
        pixel_type: str,
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            "/api/v1/link/pixel",
            json_body={"name": name, "pixel_id": pixel_id, "pixel_type": pixel_type},
        )

    def list_pixels(self) -> list[dict[str, Any]]:
        return self.request("GET", "/api/v1/link/pixel")

    def get_pixel(self, pixel_id: int | str) -> dict[str, Any]:
        return self.request("GET", f"/api/v1/link/pixel/{pixel_id}")

    def update_pixel(
        self,
        pixel_record_id: int | str,
        *,
        name: str,
        pixel_id: str,
        pixel_type: str,
    ) -> dict[str, Any]:
        return self.request(
            "PUT",
            f"/api/v1/link/pixel/{pixel_record_id}",
            json_body={"id": pixel_record_id, "name": name, "pixel_id": pixel_id, "pixel_type": pixel_type},
        )

    def delete_pixel(self, pixel_id: int | str) -> dict[str, Any]:
        return self.request("DELETE", f"/api/v1/link/pixel/{pixel_id}")

    def get_qr_code(
        self,
        short_url: str,
        *,
        output: str = "image",
        fmt: str = "png",
    ) -> bytes | dict[str, Any]:
        params = {"short_url": short_url, "output": output, "format": fmt}
        expect_binary = output == "image"
        headers = None
        if expect_binary:
            headers = {"Accept": "image/png,*/*"}
        return self.request(
            "GET",
            "/api/v1/link/qr-code",
            params=params,
            expect_binary=expect_binary,
            headers=headers,
        )

    def update_qr_code(
        self,
        short_url: str,
        *,
        image: str | None = None,
        background_color: str | None = None,
        corner_dots_color: str | None = None,
        dots_color: str | None = None,
        dots_style: str | None = None,
        corner_style: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"short_url": short_url}
        if image is not None:
            payload["image"] = image
        if background_color is not None:
            payload["background_color"] = background_color
        if corner_dots_color is not None:
            payload["corner_dots_color"] = corner_dots_color
        if dots_color is not None:
            payload["dots_color"] = dots_color
        if dots_style is not None:
            payload["dots_style"] = dots_style
        if corner_style is not None:
            payload["corner_style"] = corner_style
        return self.request("PUT", "/api/v1/link/qr-code", json_body=payload)

    def list_tags(self) -> list[dict[str, Any]]:
        return self.request("GET", "/api/v1/link/tag")

    def create_tag(self, tag: str) -> dict[str, Any]:
        return self.request("POST", "/api/v1/link/tag", json_body={"tag": tag})

    def get_tag(self, tag_id: int | str) -> dict[str, Any]:
        return self.request("GET", f"/api/v1/link/tag/{tag_id}")

    def update_tag(self, tag_id: int | str, tag: str) -> dict[str, Any]:
        return self.request("PUT", f"/api/v1/link/tag/{tag_id}", json_body={"tag": tag})

    def delete_tag(self, tag_id: int | str) -> dict[str, Any]:
        return self.request("DELETE", f"/api/v1/link/tag/{tag_id}")
