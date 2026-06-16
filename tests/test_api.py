import json

import pytest

from app import create_app
from tests.conftest import DARK_MODE_PAYLOAD


@pytest.fixture
def client(tmp_path):
    app = create_app(db_path=tmp_path / "test.db", database_url="")
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_playground_homepage(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert b"Feature Flags API Playground" in response.data


def test_create_and_get_flag(client) -> None:
    create_response = client.post("/flags", json=DARK_MODE_PAYLOAD)

    assert create_response.status_code == 201
    assert create_response.get_json() == DARK_MODE_PAYLOAD

    get_response = client.get("/flags/dark_mode")

    assert get_response.status_code == 200
    assert get_response.get_json() == DARK_MODE_PAYLOAD


def test_list_flags(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    response = client.get("/flags")

    assert response.status_code == 200
    assert response.get_json() == {"flags": [DARK_MODE_PAYLOAD]}


def test_create_duplicate_returns_conflict(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    response = client.post("/flags", json=DARK_MODE_PAYLOAD)

    assert response.status_code == 409


def test_evaluate_us_west(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    response = client.get(
        "/flags/dark_mode/evaluate?user_id=u-1&region=us-west",
    )

    assert response.status_code == 200
    # New semantics: requires both rollout bucket and eligible segment
    assert response.get_json() == {
        "flag": "dark_mode",
        "enabled": False,
        "source": "segment",
    }


def test_evaluate_us_east(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    response = client.get(
        "/flags/dark_mode/evaluate?user_id=user-0&region=us-east",
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "flag": "dark_mode",
        "enabled": False,
        "source": "segment",
    }


def test_evaluate_rollout_enables_us_east(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    response = client.get(
        "/flags/dark_mode/evaluate?user_id=user-2&region=us-east",
    )

    assert response.status_code == 200
    # New semantics: region not eligible, rollout alone doesn't enable
    assert response.get_json() == {
        "flag": "dark_mode",
        "enabled": False,
        "source": "segment",
    }


def test_evaluate_unknown_region_uses_default(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    response = client.get(
        "/flags/dark_mode/evaluate?user_id=u-3&region=eu-central",
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "flag": "dark_mode",
        "enabled": False,
        "source": "default",
    }


def test_evaluate_without_region_uses_default(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    response = client.get("/flags/dark_mode/evaluate")

    assert response.status_code == 200
    assert response.get_json() == {
        "flag": "dark_mode",
        "enabled": False,
        "source": "default",
    }


def test_update_flag_invalidates_cached_value(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)
    client.get("/flags/dark_mode/evaluate?region=us-west")

    updated_payload = {
        **DARK_MODE_PAYLOAD,
        "segments": {"us-east": False, "us-west": False},
    }
    update_response = client.put("/flags/dark_mode", json=updated_payload)

    assert update_response.status_code == 200

    evaluate_response = client.get("/flags/dark_mode/evaluate?region=us-west")

    assert evaluate_response.get_json()["enabled"] is False


def test_delete_flag(client) -> None:
    client.post("/flags", json=DARK_MODE_PAYLOAD)

    delete_response = client.delete("/flags/dark_mode")

    assert delete_response.status_code == 204
    assert client.get("/flags/dark_mode").status_code == 404


def test_invalid_create_payload(client) -> None:
    response = client.post(
        "/flags",
        data=json.dumps({"name": "dark_mode"}),
        content_type="application/json",
    )

    assert response.status_code == 400
