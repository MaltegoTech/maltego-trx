import importlib
import logging
import os
import pkgutil
import re
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import List, Literal, Optional, Dict, Generator, Sized

TRANSFORMS_CSV_HEADER = "Owner,Author,Disclaimer,Description,Version,Name,UIName,URL,entityName,oAuthSettingId," \
                        "transformSettingIDs,seedIDs"
SETTINGS_CSV_HEADER = "Name,Type,Display,DefaultValue,Optional,Popup"


@dataclass()
class TransformMeta:
    class_name: str
    display_name: str
    input_entity: str
    description: str


@dataclass()
class TransformSetting:
    name: str
    setting_type: Literal['string', 'boolean', 'date', 'datetime', 'daterange', 'url', 'double', 'int']
    display_name: str
    default_value: Optional[str] = None
    optional: bool = False
    popup: bool = False
    global_setting: bool = False

    @property
    def fullname(self) -> str:
        if self.global_setting:
            return "global#" + self.name
        return self.name


def chunk_list(data: Sized, max_chunk_size: int) -> Generator[list, None, None]:
    # rather use smaller, even lists than maxed out lists and a small tail
    number_of_chunks = len(data) // max_chunk_size + 1

    # if it's a perfect split, do it
    if len(data) % max_chunk_size == 0:
        number_of_chunks -= 1

    chunk_size = len(data) // number_of_chunks + 1

    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


@dataclass()
class TransformRegistry:
    owner: str
    author: str

    disclaimer: str
    host_url: str
    seed_ids: List[str]

    version: str = '0.1'
    prefix: str = ""
    suffix: str = ""

    _settings: Dict[str, TransformSetting] = field(default_factory=lambda: defaultdict(list))
    global_settings: List[TransformSetting] = field(default_factory=list)
    settings_prefix: str = field(default="")

    oauth_settings_id: Optional[str] = field(default="")

    metas: List[TransformMeta] = field(init=False, default_factory=list)
    transform_settings: Dict = field(default_factory=dict)

    transform_classes: dict[str, object] = field(default_factory=dict)

    @staticmethod
    def scan_for_transforms(*modules):
        """This method just imports modules recursively to run the decorators 'register' and 'uses_settings'"""
        for module in modules:
            prefix = module.__name__ + "."  # transform.
            for importer, modname, ispkg in pkgutil.walk_packages(module.__path__, prefix):
                if not ispkg:
                    importlib.import_module(modname)

    @property
    def settings(self) -> List[TransformSetting]:
        return list(self._settings.values())

    @settings.setter
    def settings(self, settings: List[TransformSetting]):
        self._settings = {setting.name: setting for setting in settings}

    @staticmethod
    def pascal_case_to_title(name: str):
        # https://stackoverflow.com/a/1176023
        name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', name)

    def register(self, display_name: str, input_entity: str, description: str):
        def decorated(transform_class: object):
            self.transform_classes[transform_class.__name__.lower()] = transform_class

            display = display_name or self.pascal_case_to_title(transform_class.__name__)
            self.metas.append(TransformMeta(transform_class.__name__, display, input_entity, description))

            return transform_class

        return decorated

    def uses_settings(self, *settings: str):
        def decorated(transform_class: object):
            self.transform_settings[transform_class.__name__] = list(settings)

            return transform_class

        return decorated

    def write_transforms_config(self, config_path: str = "./transforms.csv", max_transforms_per_file: int = 100):
        lines = []

        global_settings_fullnames = [gs.fullname for gs in self.global_settings]

        for transform_meta in self.metas:
            meta_settings = list()
            for setting in self.transform_settings.get(transform_meta.class_name, []):
                if transform_setting := self._settings.get(setting):
                    meta_settings.append(transform_setting.fullname)
                else:
                    logging.warning(
                            f"Setting {setting} is not registered. Please add to {self.__class__.__name__}.settings")

            # combine global and transform-scoped settings
            datum = [
                    self.owner,
                    self.author,
                    self.disclaimer,
                    transform_meta.description,
                    self.version,
                    transform_meta.class_name,
                    self.prefix + transform_meta.display_name + self.suffix,
                    os.path.join(self.host_url, "run", transform_meta.class_name),
                    transform_meta.input_entity,
                    self.oauth_settings_id,
                    ";".join(chain(meta_settings, global_settings_fullnames)),
                    ";".join(self.seed_ids)
            ]

            lines.append(",".join(datum))

        if len(lines) <= max_transforms_per_file:
            with open(config_path, "w+") as transforms_config:
                transforms_config.write(TRANSFORMS_CSV_HEADER + "\n")
                transforms_config.writelines(map(lambda x: x + "\n", lines))

            return

        # split file to speed-up import
        chunks = list(chunk_list(lines, max_transforms_per_file))
        for idx, chunk in enumerate(chunks):
            path, extension = config_path.rsplit(".", 1)
            chunked_config_path = f"{path}_{idx}-{len(chunks)}.{extension}"

            with open(chunked_config_path, "w+") as transforms_config:
                transforms_config.write(TRANSFORMS_CSV_HEADER + "\n")
                transforms_config.writelines(map(lambda x: x + "\n", chunk))

    def write_settings_config(self, config_path: str = "./settings.csv"):
        settings = []

        for setting in chain(self.global_settings, self.settings):
            settings.append(",".join([
                    setting.name,
                    setting.setting_type,
                    setting.display_name,
                    setting.default_value or "",
                    "true" if setting.optional else "false",
                    "true" if setting.popup else "false"
            ]))

        with open(config_path, "w+") as settings_config:
            settings_config.write(SETTINGS_CSV_HEADER + "\n")
            settings_config.writelines(map(lambda x: x + "\n", settings))
