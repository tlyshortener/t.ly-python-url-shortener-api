from __future__ import annotations

from tly_url_shortener import cli


class DummyClient:
    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        return None

    def __enter__(self) -> "DummyClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None

    def create_tag(self, *, tag: str) -> dict[str, str]:
        return {"tag": tag}


def test_call_rejects_non_object_json(monkeypatch, capsys) -> None:  # noqa: ANN001
    monkeypatch.setattr(cli, "TlyClient", DummyClient)

    exit_code = cli.main(["--token", "token", "call", "create_tag", "--data", "[]"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "--data must be a JSON object" in captured.err
