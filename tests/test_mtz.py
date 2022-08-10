import re

import pytest

from maltego_trx.mtz import (
    create_local_server_xml,
    create_settings_xml,
    create_transform_xml,
    create_transform_set_xml,
)
from tests.test_xml import _serialize_xml


def test_create_local_server_xml(mocker, snapshot):
    mocker.patch(
        "maltego_trx.mtz.create_last_sync_timestamp",
        return_value="2022-08-10 07:52:45 UTC",
    )

    transforms = ["to_lower", "to_upper", "to_title"]

    server_xml = create_local_server_xml(transforms)
    server_xml_str = _serialize_xml(server_xml)

    assert server_xml_str == snapshot


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "working_dir": ".",
            "command": "python3",
            "params": "project.py",
            "debug": True,
        },
        {
            "working_dir": "~/project/maltego",
            "command": "venv/bin/python3",
            "params": "main.py",
            "debug": False,
        },
    ],
)
def test_create_settings_xml(kwargs, snapshot):
    settings_xml = create_settings_xml(**kwargs)
    settings_xml_str = _serialize_xml(settings_xml)

    assert settings_xml_str == snapshot


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "name": "to_lower",
            "display_name": "To Lower",
            "description": "Converts the input to lowercase",
            "input_entity": "maltego.Phrase",
            "author": "Maltego Team",
        },
        {
            "name": "to_upper",
            "display_name": "To Upper",
            "description": "Converts the input to uppercase",
            "input_entity": "maltego.Text",
            "author": "Maltego Organization",
        },
    ],
)
def test_create_transform_xml(kwargs, snapshot):
    transform_xml = create_transform_xml(**kwargs)
    transform_xml_str = _serialize_xml(transform_xml)

    assert transform_xml_str == snapshot


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "name": "text_transforms",
            "description": "Basic text transforms",
            "transforms": ["to_lower", "to_upper", "to_title"],
        },
        {
            "name": "name_transforms",
            "description": "Name Transforms",
            "transforms": ["remove_lastname", "expand_middle_name", "to_initials"],
        },
    ],
)
def test_create_transform_set_xml(kwargs, snapshot):
    transform_set_xml = create_transform_set_xml(**kwargs)
    transform_set_xml_str = _serialize_xml(transform_set_xml)

    assert transform_set_xml_str == snapshot
