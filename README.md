# tly-url-shortener-api

Python SDK for the [T.LY URL Shortener API](https://t.ly).

## Features

- Typed Python client with sensible defaults.
- Built-in bearer auth handling.
- Binary or JSON responses for QR endpoints.
- CLI entry point (`tly`) for quick scripts and terminal usage.
- PyPI-ready packaging (`pyproject.toml`) and tests.

## Installation

```bash
pip install tly-url-shortener-api
```

For local development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

```python
from tly_url_shortener import TlyClient

client = TlyClient(api_token="YOUR_TLY_API_TOKEN")

created = client.create_short_link(
    long_url="https://example.com/landing-page",
    description="Campaign link",
    public_stats=True,
)
print(created["short_url"])

expanded = client.expand_short_link(short_url=created["short_url"])
print(expanded["long_url"])
```

## Endpoint Coverage

### OneLink Stats Management

- `get_onelink_stats`
- `delete_onelink_stats`

### ShortLink Management

- `create_short_link`
- `get_short_link`
- `update_short_link`
- `delete_short_link`
- `expand_short_link`
- `list_short_links`
- `bulk_shorten_links`
- `bulk_update_links`

### ShortLink Stats

- `get_link_stats`

### UTM Preset Management

- `create_utm_preset`
- `list_utm_presets`
- `get_utm_preset`
- `update_utm_preset`
- `delete_utm_preset`

### OneLink Management

- `list_onelinks`

### Pixel Management

- `create_pixel`
- `list_pixels`
- `get_pixel`
- `update_pixel`
- `delete_pixel`

### QR Code Management

- `get_qr_code`
- `update_qr_code`

### Tag Management

- `list_tags`
- `create_tag`
- `get_tag`
- `update_tag`
- `delete_tag`

## CLI Usage

Set token once:

```bash
export TLY_API_TOKEN="YOUR_TLY_API_TOKEN"
```

Create short link:

```bash
tly shorten --long-url "https://example.com"
```

Expand short link:

```bash
tly expand --short-url "https://t.ly/abc123"
```

Call any client method:

```bash
tly call create_tag --data '{"tag":"fall2026"}'
```

Retrieve QR image:

```bash
tly qr --short-url "https://t.ly/abc123" --out qr.png
```

## Development

```bash
pytest
ruff check .
python -m build
twine check dist/*
```

## Publish to PyPI

```bash
python -m build
twine check dist/*
twine upload dist/*
```

If you use trusted publishing in GitHub Actions, replace the final `twine upload` with your CI release workflow.

## License

MIT
