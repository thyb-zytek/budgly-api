import re

from models.account import AccountCreate, AccountUpdate


async def test_account_create() -> None:
    payload = AccountCreate(name="Test Account", color="#A1B2C3")

    assert payload.model_dump(mode="json")["color"] == "#A1B2C3"


async def test_account_update() -> None:
    payload = AccountUpdate.model_validate({"name": "Test Account"}).model_dump(
        exclude_unset=True
    )

    assert "color" not in payload.keys()

    payload = AccountUpdate.model_validate({"color": "#A1B2C3"}).model_dump(
        exclude_unset=True
    )

    assert payload["color"] == "#A1B2C3"

    payload = AccountUpdate.model_validate(
        {"color": None, "image": "https://example.com/image.png"}
    ).model_dump(exclude_unset=True)

    assert payload["color"] is None

    payload = AccountUpdate.model_validate({"color": None, "image": None}).model_dump(
        exclude_unset=True
    )

    assert payload["color"] is not None
    assert re.match("#[0-9A-F]{6}", payload["color"])
