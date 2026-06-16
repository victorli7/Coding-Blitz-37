import os

import pytest

from app import create_app
from feature_flags.store import PostgresFlagStore, create_flag_store
from tests.conftest import DARK_MODE_PAYLOAD

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to run Postgres integration tests",
)


@pytest.fixture
def postgres_store() -> PostgresFlagStore:
    store = create_flag_store(database_url=TEST_DATABASE_URL)
    assert isinstance(store, PostgresFlagStore)
    store.delete("dark_mode")
    yield store
    store.delete("dark_mode")


@pytest.fixture
def postgres_client():
    app = create_app(database_url=TEST_DATABASE_URL)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    create_flag_store(database_url=TEST_DATABASE_URL).delete("dark_mode")


def test_postgres_store_crud(postgres_store: PostgresFlagStore) -> None:
    from feature_flags.models import FeatureFlag

    flag = FeatureFlag(**DARK_MODE_PAYLOAD)
    postgres_store.create(flag)

    loaded = postgres_store.get("dark_mode")
    assert loaded == flag

    assert len(postgres_store.list_all()) == 1

    updated = FeatureFlag(
        name="dark_mode",
        default_state=False,
        segment_key="region",
        segments={"us-east": False, "us-west": False},
    )
    postgres_store.update(updated)
    assert postgres_store.get("dark_mode") == updated

    assert postgres_store.delete("dark_mode") is True
    assert postgres_store.get("dark_mode") is None


def test_postgres_api_create_and_evaluate(postgres_client) -> None:
    create_response = postgres_client.post("/flags", json=DARK_MODE_PAYLOAD)
    assert create_response.status_code == 201

    evaluate_response = postgres_client.get(
        "/flags/dark_mode/evaluate?region=us-west",
    )
    assert evaluate_response.status_code == 200
    assert evaluate_response.get_json() == {
        "flag": "dark_mode",
        "enabled": True,
        "source": "segment",
    }

    list_response = postgres_client.get("/flags")
    assert list_response.status_code == 200
    assert list_response.get_json() == {"flags": [DARK_MODE_PAYLOAD]}
