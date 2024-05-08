import pytest

from core.config import parse_cors


@pytest.mark.parametrize(
    "variable, expected",
    [
        ("http://localhost:5000", ["http://localhost:5000"]),
        (None, ["*"]),
        (
            "http://localhost http://localhost:8000,https://google.com/",
            ["http://localhost", "http://localhost:8000", "https://google.com/"],
        ),
    ],
)
def test_parse_cors_variables(variable: str, expected: list[str]) -> None:
    assert parse_cors(variable) == expected


def test_parse_cors_variables_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        parse_cors(12)  # type: ignore[arg-type]

    assert isinstance(exc_info.value, ValueError) is True
    assert str(exc_info.value) == "12"
