import os
from dataclasses import dataclass, field
from itertools import chain
from typing import List, Optional, Dict, Iterable

from maltego_trx.utils import filter_unique, pascal_case_to_title, escape_csv_fields, export_as_csv, serialize_bool, \
    name_to_path

TRANSFORMS_CSV_HEADER = "Owner,Author,Disclaimer,Description,Version," \
                        "Name,UIName,URL,entityName," \
                        "oAuthSettingId,transformSettingIDs,seedIDs"
SETTINGS_CSV_HEADER = "Name,Type,Display,DefaultValue,Optional,Popup"


@dataclass()
class TransformMeta:
    class_name: str
    display_name: str
    input_entity: str
    description: str
    output_entities: List[str]
    disclaimer: str


@dataclass()
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

    version: str = '0.1'
    display_name_suffix: str = ""

    global_settings: List[TransformSetting] = field(default_factory=list)
    oauth_settings_id: Optional[str] = ""

    transform_metas: Dict[str, TransformMeta] = field(init=False, default_factory=dict)
    transform_settings: Dict[str, List[TransformSetting]] = field(init=False, default_factory=dict)

    def register_transform(self, display_name: str, input_entity: str, description: str,
                           settings: List[TransformSetting] = None, output_entities: List[str] = None,
                           disclaimer: str = ""):
        """ This method can be used as a decorator on transform classes. The data will be used to fill out csv config
            files to be imported into a TDS.
        """

        def decorated(transform_callable: object):
            cleaned_transform_name = name_to_path(transform_callable.__name__)
            display = display_name or pascal_case_to_title(transform_callable.__name__)

            meta = TransformMeta(cleaned_transform_name,
                                 display, input_entity,
                                 description,
                                 output_entities or [],
                                 disclaimer)
            self.transform_metas[cleaned_transform_name] = meta

            if settings:
                self.transform_settings[cleaned_transform_name] = settings

            return transform_callable

        return decorated

    def write_transforms_config(self, config_path: str = "./transforms.csv", csv_line_limit: int = 100):
        """Exports the collected transform metadata as a csv-file to config_path"""
        global_settings_full_names = [gs.id for gs in self.global_settings]

        csv_lines = []
        for transform_name, transform_meta in self.transform_metas.items():
            meta_settings = [setting.id for setting in
                             self.transform_settings.get(transform_name, [])]

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
                    ";".join(self.seed_ids)
            ]

            escaped_fields = escape_csv_fields(*transform_row)
            csv_lines.append(",".join(escaped_fields))

        export_as_csv(TRANSFORMS_CSV_HEADER, csv_lines, config_path, csv_line_limit)

    def write_settings_config(self, config_path: str = "./settings.csv", csv_line_limit: int = 100):
        """Exports the collected settings metadata as a csv-file to config_path"""
        chained_settings = chain(self.global_settings, *list(self.transform_settings.values()))
        unique_settings: Iterable[TransformSetting] = filter_unique(lambda s: s.name, chained_settings)

        csv_lines = []
        for setting in unique_settings:
            setting_row = [
                    setting.id,
                    setting.setting_type,
                    setting.display_name,
                    setting.default_value or "",
                    serialize_bool(setting.optional, 'True', 'False'),
                    serialize_bool(setting.popup, 'Yes', 'No')
            ]

            escaped_fields = escape_csv_fields(*setting_row)
            csv_lines.append(",".join(escaped_fields))

        export_as_csv(SETTINGS_CSV_HEADER, csv_lines, config_path, csv_line_limit)
