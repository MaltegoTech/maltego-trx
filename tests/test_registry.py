import os
import random
from typing import NamedTuple, List

import petname
import pytest as pytest

from maltego_trx.decorator_registry import TransformSetting, TransformRegistry, TRANSFORMS_CSV_HEADER, \
    SETTINGS_CSV_HEADER
from maltego_trx.server import app
from maltego_trx.utils import name_to_path, serialize_bool


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def registry():
    registry: TransformRegistry = TransformRegistry(owner="Maltego Technologies GmbH",
                                                    author="Maltego Support",
                                                    host_url="localhost",
                                                    seed_ids=["demo"])
    return registry


def make_transform_setting():
    name = petname.generate()
    setting_type = random.choice(['string', 'boolean', 'date', 'datetime', 'daterange', 'url', 'double', 'int'])

    return TransformSetting(name=name,
                            display_name=name.title(),
                            setting_type=random.choice(setting_type),
                            default_value=petname.generate(),
                            optional=random.choice([True, False]),
                            popup=random.choice([True, False]),
                            global_setting=random.choice([True, False]))


def make_transform(registry: TransformRegistry, settings: List[TransformSetting] = None):
    display_name = petname.generate(separator=" ")
    input_entity = petname.generate(separator=".")
    description = petname.generate(words=10, separator=" ").title() + "."
    settings = settings or [make_transform_setting(), make_transform_setting()]
    output_entities = petname.generate(3).split("-")
    disclaimer = petname.generate(words=10, separator=" ").title() + "."

    @registry.register_transform(display_name, input_entity, description, settings, output_entities, disclaimer)
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

    @registry.register_transform(display_name, input_entity, description, test_settings, output_entities, disclaimer)
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


class SettingCsvLine(NamedTuple):
    name: str
    setting_type: str
    display_name: str
    default: str
    optional: str
    popup: str


def test_transform_to_csv(registry):
    random_class = make_transform(registry)

    path_name = name_to_path(random_class.__name__)

    tx_meta = registry.transform_metas.get(path_name)
    tx_settings = registry.transform_settings.get(path_name, [])

    registry.write_transforms_config()

    with open("./transforms.csv") as transforms_csv:
        header = next(transforms_csv)
        assert header.rstrip("\n") == TRANSFORMS_CSV_HEADER

        line = next(transforms_csv).rstrip("\n")
        data: TransformCsvLine = TransformCsvLine(*line.split(','))

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


def test_setting_to_csv(registry):
    local_setting = make_transform_setting()
    local_setting.global_setting = False

    global_setting = make_transform_setting()
    global_setting.global_setting = True

    registry.global_settings.append(global_setting)

    @registry.register_transform("", "", "", settings=[local_setting])
    class TestClass:
        pass

    registry.write_settings_config()
    with open("./settings.csv") as settings_csv:
        header = next(settings_csv)
        assert header.rstrip("\n") == SETTINGS_CSV_HEADER

        for line, setting in zip(settings_csv.readlines(), [global_setting, local_setting]):
            line = line.rstrip("\n")
            data: SettingCsvLine = SettingCsvLine(*line.split(','))

            assert data.name == setting.id
            assert data.setting_type == setting.setting_type
            assert data.display_name == setting.display_name
            assert data.default == setting.default_value
            assert data.optional == serialize_bool(setting.optional, 'True', 'False')
            assert data.popup == serialize_bool(setting.popup, 'Yes', 'No')
