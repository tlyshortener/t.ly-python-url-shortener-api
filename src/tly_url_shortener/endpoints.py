from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    group: str
    label: str


ENDPOINTS: dict[str, Endpoint] = {
    "get_onelink_stats": Endpoint(
        method="GET",
        path="/api/v1/onelink/stats",
        group="OneLink Stats Management",
        label="api/v1/onelink/stats",
    ),
    "delete_onelink_stats": Endpoint(
        method="DELETE",
        path="/api/v1/onelink/stat",
        group="OneLink Stats Management",
        label="Delete OneLink Stats",
    ),
    "create_short_link": Endpoint(
        method="POST",
        path="/api/v1/link/shorten",
        group="ShortLink Management",
        label="Create Short Link",
    ),
    "get_short_link": Endpoint(
        method="GET",
        path="/api/v1/link",
        group="ShortLink Management",
        label="Get Short Link",
    ),
    "update_short_link": Endpoint(
        method="PUT",
        path="/api/v1/link",
        group="ShortLink Management",
        label="Update Short Link",
    ),
    "delete_short_link": Endpoint(
        method="DELETE",
        path="/api/v1/link",
        group="ShortLink Management",
        label="Delete Short Link",
    ),
    "expand_short_link": Endpoint(
        method="POST",
        path="/api/v1/link/expand",
        group="ShortLink Management",
        label="Expand Short Link",
    ),
    "list_short_links": Endpoint(
        method="GET",
        path="/api/v1/link/list",
        group="ShortLink Management",
        label="List Short Links",
    ),
    "bulk_shorten_links": Endpoint(
        method="POST",
        path="/api/v1/link/bulk",
        group="ShortLink Management",
        label="Bulk Shorten Links",
    ),
    "bulk_update_links": Endpoint(
        method="POST",
        path="/api/v1/link/bulk/update",
        group="ShortLink Management",
        label="Bulk Update Links",
    ),
    "get_link_stats": Endpoint(
        method="GET",
        path="/api/v1/link/stats",
        group="ShortLink Stats",
        label="Stats",
    ),
    "create_utm_preset": Endpoint(
        method="POST",
        path="/api/v1/link/utm-preset",
        group="UTM Preset Management",
        label="Create UTM Preset",
    ),
    "list_utm_presets": Endpoint(
        method="GET",
        path="/api/v1/link/utm-preset",
        group="UTM Preset Management",
        label="List UTM Presets",
    ),
    "get_utm_preset": Endpoint(
        method="GET",
        path="/api/v1/link/utm-preset/{id}",
        group="UTM Preset Management",
        label="Get UTM Preset",
    ),
    "update_utm_preset": Endpoint(
        method="PUT",
        path="/api/v1/link/utm-preset/{id}",
        group="UTM Preset Management",
        label="Update UTM Preset",
    ),
    "delete_utm_preset": Endpoint(
        method="DELETE",
        path="/api/v1/link/utm-preset/{id}",
        group="UTM Preset Management",
        label="Delete UTM Preset",
    ),
    "list_onelinks": Endpoint(
        method="GET",
        path="/api/v1/onelink/list",
        group="OneLink Management",
        label="List OneLinks",
    ),
    "create_pixel": Endpoint(
        method="POST",
        path="/api/v1/link/pixel",
        group="Pixel Management",
        label="Create Pixel",
    ),
    "list_pixels": Endpoint(
        method="GET",
        path="/api/v1/link/pixel",
        group="Pixel Management",
        label="List Pixel",
    ),
    "get_pixel": Endpoint(
        method="GET",
        path="/api/v1/link/pixel/{id}",
        group="Pixel Management",
        label="Get Pixel",
    ),
    "update_pixel": Endpoint(
        method="PUT",
        path="/api/v1/link/pixel/{id}",
        group="Pixel Management",
        label="Update Pixel",
    ),
    "delete_pixel": Endpoint(
        method="DELETE",
        path="/api/v1/link/pixel/{id}",
        group="Pixel Management",
        label="Delete Pixel",
    ),
    "get_qr_code": Endpoint(
        method="GET",
        path="/api/v1/link/qr-code",
        group="QR Code Management",
        label="Get QR Code",
    ),
    "update_qr_code": Endpoint(
        method="PUT",
        path="/api/v1/link/qr-code",
        group="QR Code Management",
        label="Update QR Code",
    ),
    "list_tags": Endpoint(
        method="GET",
        path="/api/v1/link/tag",
        group="Tag Management",
        label="List Tag",
    ),
    "create_tag": Endpoint(
        method="POST",
        path="/api/v1/link/tag",
        group="Tag Management",
        label="Create Tag",
    ),
    "get_tag": Endpoint(
        method="GET",
        path="/api/v1/link/tag/{id}",
        group="Tag Management",
        label="Get Tag",
    ),
    "update_tag": Endpoint(
        method="PUT",
        path="/api/v1/link/tag/{id}",
        group="Tag Management",
        label="Update Tag",
    ),
    "delete_tag": Endpoint(
        method="DELETE",
        path="/api/v1/link/tag/{id}",
        group="Tag Management",
        label="Delete Tag",
    ),
}


SUPPORTED_METHODS: tuple[str, ...] = tuple(ENDPOINTS.keys())
