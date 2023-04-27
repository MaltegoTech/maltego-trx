import logging
import os
import random
import tempfile
import zipfile
from typing import NamedTuple, List

import petname
import pytest as pytest
from pytest_mock import MockerFixture

from maltego_trx.decorator_registry import (
    TransformSetting,
    TransformRegistry,
    TRANSFORMS_CSV_HEADER,
    LEGACY_TRANSFORMS_CSV_HEADER,
    SETTINGS_CSV_HEADER,
    TransformSet,
)
from maltego_trx.server import app
from maltego_trx.utils import name_to_path, serialize_bool
from tests.test_xml import _serialize_xml


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def registry():
    registry: TransformRegistry = TransformRegistry(
        owner="Maltego Technologies GmbH",
        author="Maltego Support",
        host_url="localhost",
        seed_ids=["demo"],
    )
    return registry


def make_transform_setting(global_setting: bool = None):
    name = petname.generate()
    setting_type = random.choice(
        ["string", "boolean", "date", "datetime", "daterange", "url", "double", "int"]
    )

    return TransformSetting(
        name=name,
        display_name=name.title(),
        setting_type=random.choice(setting_type),
        default_value=petname.generate(),
        optional=random.choice([True, False]),
        popup=random.choice([True, False]),
        global_setting=global_setting or random.choice([True, False]),
    )


def make_transform(
    registry: TransformRegistry, settings: List[TransformSetting] = None
):
    display_name = petname.generate(separator=" ")
    input_entity = petname.generate(separator=".")
    description = petname.generate(words=10, separator=" ").title() + "."
    settings = settings or [make_transform_setting(), make_transform_setting()]
    output_entities = petname.generate(3).split("-")
    disclaimer = petname.generate(words=10, separator=" ").title() + "."

    @registry.register_transform(
        display_name, input_entity, description, settings, output_entities, disclaimer
    )
    class TestClass:
        pass

    return TestClass


def test_register_transform_decorator(registry):
    test_settings = [make_transform_setting(), make_transform_setting()]

    display_name = petname.generate(separator=" ")
    input_entity = petname.generate(separator=".")
    description = petname.generate(words=10, separator=" ").title() + "."
    output_entities = petname.generate(3).split("-")
    disclaimer = petname.generate(words=10, separator=" ").title() + "."

    @registry.register_transform(
        display_name,
        input_entity,
        description,
        test_settings,
        output_entities,
        disclaimer,
    )
    class TestClass:
        pass

    path_name = name_to_path(TestClass.__name__)

    tx_meta = registry.transform_metas.get(path_name)

    assert tx_meta
    assert tx_meta.display_name == display_name
    assert tx_meta.input_entity == input_entity
    assert tx_meta.description == description
    assert tx_meta.disclaimer == disclaimer

    assert test_settings == registry.transform_settings[path_name]


class TransformCsvLine(NamedTuple):
    owner: str
    author: str
    disclaimer: str
    description: str
    version: str
    name: str
    display_name: str
    host: str
    input_entity: str
    oauth_id: str
    settings_ids: str
    seed_ids: str
    output_entities: str

class LegacyTransformCsvLine(NamedTuple):
    owner: str
    author: str
    disclaimer: str
    description: str
    version: str
    name: str
    display_name: str
    host: str
    input_entity: str
    oauth_id: str
    settings_ids: str
    seed_ids: str

class SettingCsvLine(NamedTuple):
    name: str
    setting_type: str
    display_name: str
    default: str
    optional: str
    popup: str


def test_transform_to_csv(registry: TransformRegistry):
    random_class = make_transform(registry)

    path_name = name_to_path(random_class.__name__)

    tx_meta = registry.transform_metas.get(path_name)
    tx_settings = registry.transform_settings.get(path_name, [])

    output_path = "./transforms_with_output_entities.csv"
    registry.write_transforms_config(config_path=output_path,include_output_entities=True)

    with open(output_path) as transforms_csv:
        header = next(transforms_csv)
        assert header.rstrip("\n") == TRANSFORMS_CSV_HEADER

        line = next(transforms_csv).rstrip("\n")
        data: TransformCsvLine = TransformCsvLine(*line.split(","))

        assert data.owner == registry.owner
        assert data.author == registry.author
        assert data.disclaimer == tx_meta.disclaimer
        assert data.description == tx_meta.description
        assert data.version == registry.version
        assert data.name == tx_meta.class_name
        assert data.display_name == tx_meta.display_name
        assert data.host == os.path.join(registry.host_url, "run", path_name)
        assert data.input_entity == tx_meta.input_entity
        assert data.oauth_id == registry.oauth_settings_id
        assert data.settings_ids.split(";") == [s.id for s in tx_settings]
        assert data.seed_ids.split(";") == registry.seed_ids
        assert data.output_entities.split(";") == tx_meta.output_entities

def test_transform_to_legacy_csv(registry: TransformRegistry):
    random_class = make_transform(registry)

    path_name = name_to_path(random_class.__name__)

    tx_meta = registry.transform_metas.get(path_name)
    tx_settings = registry.transform_settings.get(path_name, [])

    output_path = "./transforms_no_output_entities.csv"
    registry.write_transforms_config(config_path=output_path,include_output_entities=False)

    with open(output_path) as transforms_csv:
        header = next(transforms_csv)
        assert header.rstrip("\n") == LEGACY_TRANSFORMS_CSV_HEADER

        line = next(transforms_csv).rstrip("\n")
        data: LegacyTransformCsvLine = LegacyTransformCsvLine(*line.split(","))

        assert data.owner == registry.owner
        assert data.author == registry.author
        assert data.disclaimer == tx_meta.disclaimer
        assert data.description == tx_meta.description
        assert data.version == registry.version
        assert data.name == tx_meta.class_name
        assert data.display_name == tx_meta.display_name
        assert data.host == os.path.join(registry.host_url, "run", path_name)
        assert data.input_entity == tx_meta.input_entity
        assert data.oauth_id == registry.oauth_settings_id
        assert data.settings_ids.split(";") == [s.id for s in tx_settings]
        assert data.seed_ids.split(";") == registry.seed_ids

def test_setting_to_csv(registry: TransformRegistry):
    local_setting = make_transform_setting(global_setting=False)

    global_setting = make_transform_setting(global_setting=True)

    registry.global_settings.append(global_setting)

    @registry.register_transform("", "", "", settings=[local_setting])
    class TestClass:
        pass

    registry.write_settings_config()
    with open("./settings.csv") as settings_csv:
        header = next(settings_csv)
        assert header.rstrip("\n") == SETTINGS_CSV_HEADER

        for line, setting in zip(
            settings_csv.readlines(), [global_setting, local_setting]
        ):
            line = line.rstrip("\n")
            data: SettingCsvLine = SettingCsvLine(*line.split(","))

            assert data.name == setting.id
            assert data.setting_type == setting.setting_type
            assert data.display_name == setting.display_name
            assert data.default == setting.default_value
            assert data.optional == serialize_bool(setting.optional, "True", "False")
            assert data.popup == serialize_bool(setting.popup, "Yes", "No")


def test_write_local_mtz_emit_global_settings_warning(
    registry: TransformRegistry, caplog, snapshot
):
    registry.global_settings = [
        TransformSetting(
            name="test", display_name="test", setting_type="string", global_setting=True
        )
    ]

    with caplog.at_level(logging.WARNING):
        list(registry._create_local_mtz())

    assert caplog.messages == snapshot


def test_write_local_mtz_emit_settings_warning(
    registry: TransformRegistry, caplog, snapshot
):
    local_setting = TransformSetting(
        name="test",
        display_name="test",
        setting_type="string",
        global_setting=True,
    )

    @registry.register_transform("", "", "", settings=[local_setting])
    class TestClass:
        pass

    with caplog.at_level(logging.WARNING):
        list(registry._create_local_mtz())

    assert caplog.messages == snapshot


def test_write_local_mtz(registry: TransformRegistry, mocker: MockerFixture, snapshot):
    mocker.patch(
        "maltego_trx.mtz.create_last_sync_timestamp",
        return_value="2022-08-10 07:52:45 UTC",
    )
    mocker.patch("maltego_trx.decorator_registry.serialize_xml", _serialize_xml)

    transform_set = TransformSet(name="test", description="Test Transform Set")

    @registry.register_transform("", "", "", transform_set=transform_set)
    class TestClass:
        pass

    mtz_files = list(registry._create_local_mtz(working_dir="/home/maltego"))

    assert mtz_files == snapshot

    files = [path for path, content in mtz_files]

    assert files == snapshot


def test_write_local_mtz_file(registry: TransformRegistry, mocker: MockerFixture, snapshot):
    mocker.patch(
        "maltego_trx.mtz.create_last_sync_timestamp",
        return_value="2022-08-10 07:52:45 UTC",
    )
    mocker.patch("maltego_trx.decorator_registry.serialize_xml", _serialize_xml)

    transform_set = TransformSet(name="test", description="Test Transform Set")

    @registry.register_transform("", "", "", transform_set=transform_set)
    class TestClass:
        pass

    with tempfile.TemporaryDirectory() as working_dir:
        mtz_path = os.path.join(working_dir, "local.mtz")

        registry.write_local_mtz(mtz_path=mtz_path)

        assert os.path.exists(mtz_path), "Local mtz file not created"

        with zipfile.ZipFile(mtz_path) as local_mtz:
            assert all(
                file.file_size > 0 for file in local_mtz.infolist()
            ), "Empty files in local mtz"
