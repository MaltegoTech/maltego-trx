from dataclasses import dataclass, field
from typing import Any

from maltego_trx.utils import pascal_case_to_title


@dataclass
class MaltegoEntityTypeMeta:
    namespace: str = None
    name: str = None

    display_name: str = None
    display_name_plural: str = None

    description: str = None
    category: str = None

    small_icon_resource: str = None
    large_icon_resource: str = None

    allowed_root: bool = True
    conversion_order: int = 2147483647
    visible: bool = True

    base_entities: list[str] = field(default_factory=list)

    value_field: str = None
    display_value_field: str = None

    @property
    def id(self):
        if self.namespace:
            return f"{self.namespace}.{self.name}"

        return self.name


@dataclass
class EntityFieldType:
    name: str = None
    type: str = 'string'
    nullable: bool = True
    hidden: bool = False
    readonly: bool = False
    description: str = None
    display_name: str = None
    sample_value: str = None
    evaluator: str = None


class MaltegoEntityType:
    __meta__: MaltegoEntityTypeMeta
    __fields__: dict[str, EntityFieldType]


def generate_meta(class_name: str, base: MaltegoEntityTypeMeta = None) -> MaltegoEntityTypeMeta:
    meta = base or MaltegoEntityTypeMeta()

    meta.name = meta.name or class_name

    meta.display_name = meta.display_name or pascal_case_to_title(meta.name)
    meta.display_name_plural = meta.display_name_plural or meta.display_name + "s"

    meta.description = meta.description or f"A {meta.display_name} entity"

    return meta


def generate_field(field_name: str, sample: Any = None, base: EntityFieldType = None) -> EntityFieldType:
    base = base or EntityFieldType()
    field_meta = EntityFieldType()

    field_meta.name = base.name or field_name
    field_meta.type = base.type or 'string'

    field_meta.nullable = base.nullable
    field_meta.hidden = base.hidden

    field_meta.readonly = base.readonly
    field_meta.description = base.description

    field_meta.display_name = base.display_name or field_name.replace("_", " ").title()
    field_meta.sample_value = base.sample_value or sample

    return field_meta
