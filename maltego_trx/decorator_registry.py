import logging
import os
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import List, Optional, Dict, Iterable, Tuple

from maltego_trx.mtz import (
    create_local_server_xml,
    create_settings_xml,
    create_transform_xml,
    create_transform_set_xml,
)
from maltego_trx.utils import (
    filter_unique,
    pascal_case_to_title,
    escape_csv_fields,
    export_as_csv,
    serialize_bool,
    name_to_path,
    serialize_xml,
)

TRANSFORMS_CSV_HEADER = (
    "Owner,Author,Disclaimer,Description,Version,"
    "Name,UIName,URL,entityName,"
    "oAuthSettingId,transformSettingIDs,seedIDs"
)
SETTINGS_CSV_HEADER = "Name,Type,Display,DefaultValue,Optional,Popup"


@dataclass(frozen=True)
class TransformSet:
    name: str
    description: str


@dataclass()
class TransformMeta:
    class_name: str
    display_name: str
    input_entity: str
    description: str
    output_entities: List[str]
    disclaimer: str
    transform_set: TransformSet


@dataclass(frozen=True)
class TransformSetting:
    name: str
    display_name: str
    setting_type: str  # Literal['string', 'boolean', 'date', 'datetime', 'daterange', 'url', 'double', 'int']

    default_value: Optional[str] = ""
    optional: bool = False
    popup: bool = False
    global_setting: bool = False

    @property
    def id(self) -> str:
        """this setting's full id for reference"""
        if self.global_setting:
            return "global#" + self.name
        return self.name


@dataclass(eq=False)
class TransformRegistry:
    owner: str
    author: str

    host_url: str
    seed_ids: List[str]

    version: str = "0.1"
    display_name_suffix: str = ""

    global_settings: List[TransformSetting] = field(default_factory=list)
    oauth_settings_id: Optional[str] = ""

    transform_metas: Dict[str, TransformMeta] = field(init=False, default_factory=dict)
    transform_settings: Dict[str, List[TransformSetting]] = field(
        init=False, default_factory=dict
    )
    transform_sets: Dict[TransformSet, List[str]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )

    def register_transform(
        self,
        display_name: str,
        input_entity: str,
        description: str,
        settings: List[TransformSetting] = None,
        output_entities: List[str] = None,
        disclaimer: str = "",
        transform_set: TransformSet = None,
    ):
        """This method can be used as a decorator on transform classes. The data will be used to fill out csv config
        files to be imported into a TDS.
        """

        def decorated(transform_callable: object):
            cleaned_transform_name = name_to_path(transform_callable.__name__)
            display = display_name or pascal_case_to_title(transform_callable.__name__)

            meta = TransformMeta(
                cleaned_transform_name,
                display,
                input_entity,
                description,
                output_entities or [],
                disclaimer,
                transform_set=transform_set,
            )
            self.transform_metas[cleaned_transform_name] = meta

            if settings:
                self.transform_settings[cleaned_transform_name] = settings

            if transform_set:
                self.transform_sets[transform_set].append(cleaned_transform_name)

            return transform_callable

        return decorated

    def _create_transforms_config(self) -> Iterable[str]:
        global_settings_full_names = [gs.id for gs in self.global_settings]

        for transform_name, transform_meta in self.transform_metas.items():
            meta_settings = [
                setting.id
                for setting in self.transform_settings.get(transform_name, [])
            ]

            transform_row = [
                self.owner,
                self.author,
                transform_meta.disclaimer,
                transform_meta.description,
                self.version,
                transform_name,
                transform_meta.display_name + self.display_name_suffix,
                os.path.join(self.host_url, "run", transform_name),
                transform_meta.input_entity,
                ";".join(self.oauth_settings_id),
                # combine global and transform scoped settings
                ";".join(chain(meta_settings, global_settings_full_names)),
                ";".join(self.seed_ids),
            ]

            escaped_fields = escape_csv_fields(*transform_row)
            yield ",".join(escaped_fields)

    def write_transforms_config(
        self, config_path: str = "./transforms.csv", csv_line_limit: int = 100
    ):
        """Exports the collected transform metadata as a csv-file to config_path"""

        csv_lines = self._create_transforms_config()

        export_as_csv(
            TRANSFORMS_CSV_HEADER, tuple(csv_lines), config_path, csv_line_limit
        )

    def _create_settings_config(self) -> Iterable[str]:
        chained_settings = chain(
            self.global_settings, *list(self.transform_settings.values())
        )
        unique_settings: Iterable[TransformSetting] = filter_unique(
            lambda s: s.name, chained_settings
        )

        for setting in unique_settings:
            setting_row = [
                setting.id,
                setting.setting_type,
                setting.display_name,
                setting.default_value or "",
                serialize_bool(setting.optional, "True", "False"),
                serialize_bool(setting.popup, "Yes", "No"),
            ]

            escaped_fields = escape_csv_fields(*setting_row)
            yield ",".join(escaped_fields)

    def write_settings_config(
        self, config_path: str = "./settings.csv", csv_line_limit: int = 100
    ):
        """Exports the collected settings metadata as a csv-file to config_path"""

        csv_lines = self._create_settings_config()

        export_as_csv(
            SETTINGS_CSV_HEADER, tuple(csv_lines), config_path, csv_line_limit
        )

    def _create_local_mtz(
        self,
        working_dir: str = ".",
        command: str = "python3",
        params: str = "project.py",
        debug: bool = True,
    ) -> Iterable[Tuple[str, str]]:
        working_dir = os.path.abspath(working_dir)
        if self.global_settings:
            logging.warning(
                f"Settings are not supported with local transforms. "
                f"Global settings are: {', '.join(map(lambda s: s.name, self.global_settings))}"
            )

        """Creates an .mtz for bulk importing local transforms"""
        server_xml = create_local_server_xml(self.transform_metas.keys())

        server_xml_str = serialize_xml(server_xml)
        yield "Servers/Local.tas", server_xml_str

        for name, meta in self.transform_metas.items():
            settings_xml = create_settings_xml(
                working_dir, command, f"{params} local {name}", debug
            )
            settings_xml_str = serialize_xml(settings_xml)

            tx_settings = self.transform_settings.get(name)
            if tx_settings:
                logging.warning(
                    "Settings are not supported with local transforms. "
                    f"Transform '{meta.display_name}' has: {', '.join(map(lambda s: s.name, tx_settings))}"
                )

            xml = create_transform_xml(
                name,
                meta.display_name,
                meta.description,
                meta.input_entity,
                self.author,
            )

            xml_str = serialize_xml(xml)

            yield f"TransformRepositories/Local/{name}.transform", xml_str
            yield f"TransformRepositories/Local/{name}.transformsettings", settings_xml_str

        for transform_set, transforms in self.transform_sets.items():
            set_xml = create_transform_set_xml(
                transform_set.name, transform_set.description, transforms
            )

            set_xml_str = serialize_xml(set_xml)

            yield f"TransformSets/{transform_set.name}.set", set_xml_str

    def write_local_mtz(
        self,
        mtz_path: str = "./local.mtz",
        working_dir: str = ".",
        command: str = "python3",
        params: str = "project.py",
        debug: bool = True,
    ):

        with zipfile.ZipFile(mtz_path, "w") as mtz:
            for path, content in self._create_local_mtz(
                working_dir, command, params, debug
            ):
                mtz.writestr(path, content)
