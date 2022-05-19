import os
import sys
import typing
import zipfile
from dataclasses import dataclass, field
from itertools import chain
from typing import List, Optional, Dict, Iterable, Type, Set
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from maltego_trx.protocol.entities import MaltegoEntityType, MaltegoEntityTypeMeta, generate_meta, EntityFieldType, \
    generate_field
from maltego_trx.protocol.mtz import create_entity_type_xml
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

    namespace: str = None

    transform_metas: Dict[str, TransformMeta] = field(init=False, default_factory=dict)
    transform_settings: Dict[str, List[TransformSetting]] = field(init=False, default_factory=dict)

    entity_metas: Dict[str, Type[MaltegoEntityType]] = field(init=False, default_factory=dict)
    entity_categories: Set[str] = field(init=False, default_factory=set)

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

    def register_entity(self,
                        namespace: str = None,
                        name: str = None,
                        display_name: str = None,
                        display_name_plural: str = None,
                        description: str = None,
                        category: str = None,
                        small_icon_resource: str = None,
                        large_icon_resource: str = None,
                        allowed_root: bool = True,
                        conversion_order: int = 2147483647,
                        visible: bool = True,
                        base_entities: list[str] = None,
                        value_field: str = None,
                        display_value_field: str = None):
        # get all arguments
        kwargs = locals()
        kwargs.pop("self")
        kwargs['namespace'] = kwargs['namespace'] or self.namespace

        def decorated(cls: Type[MaltegoEntityType]) -> MaltegoEntityType:

            default = MaltegoEntityTypeMeta(**kwargs)
            meta = getattr(cls, '__meta__', default)
            meta = generate_meta(cls.__name__, meta)
            cls.__meta__ = meta

            if meta.category:
                self.entity_categories.add(meta.category)

            field_metas = {}
            for field_name, field_type in typing.get_type_hints(cls).items():
                if field_name.startswith("__"):
                    continue

                sample = None
                field_meta = None
                if value := getattr(cls, field_name, None):
                    if isinstance(value, EntityFieldType):
                        field_meta = value
                    else:
                        sample = value

                field_meta = generate_field(field_name, sample, field_meta)
                setattr(cls, field_name, field_meta)
                field_metas[field_name] = field_meta

            if not meta.value_field:
                meta.value_field = list(field_metas.keys())[0]
            if not meta.display_value_field:
                meta.display_value_field = meta.value_field

            self.entity_metas[meta.id] = cls
            cls.__fields__ = field_metas
            return cls

        return decorated

    def write_transforms_config(self, config_path: str = "./transforms.csv", csv_line_limit: int = 100):
        """Exports the collected transform meta data as a csv-file to config_path"""
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
        """Exports the collected settings meta data as a csv-file to config_path"""
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

    def write_mtz(self, mtz_path: str):
        with zipfile.ZipFile(mtz_path, "w") as mtz:
            for name, entity_meta in self.entity_metas.items():
                entity_xml = create_entity_type_xml(entity_meta)
                if sys.version_info.minor >= 9:
                    ElementTree.indent(entity_xml)

                entity_xml_str = ElementTree.tostring(entity_xml)
                mtz.writestr(f"Entities/{name}.entity", entity_xml_str)

            for category in self.entity_categories:
                category_xml = Element("EntityCategory", attrib={"name": category})
                category_xml_str = ElementTree.tostring(category_xml)
                mtz.writestr(f"EntityCategories/{category.lower()}.category", category_xml_str)
