from typing import Type
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from maltego_trx.protocol.entities import MaltegoEntityType, EntityFieldType
from maltego_trx.utils import serialize_bool


def create_entity_type_xml(entity: Type[MaltegoEntityType]) -> Element:
    meta = entity.__meta__
    entity_xml = Element("MaltegoEntity", attrib={
        "id": meta.id,
        "displayName": meta.display_name,
        "displayNamePlural": meta.display_name_plural,
        "description": meta.description,
        "category": meta.category or "",
        "smallIconResource": meta.small_icon_resource or "",
        "largeIconResource": meta.large_icon_resource or "",
        "allowedRoot": serialize_bool(meta.allowed_root),
        "conversionOrder": str(meta.conversion_order),
        "visible": serialize_bool(meta.visible)
    })

    if meta.base_entities:
        base_entities_xml = SubElement(entity_xml, "BaseEntities")
        for base_entity in meta.base_entities:
            base_entity_xml = SubElement(base_entities_xml, "BaseEntity")
            base_entity_xml.text = base_entity

    properties_xml = SubElement(entity_xml, "Properties",
                                attrib={"value": meta.value_field,
                                        "displayValue": meta.display_value_field})

    SubElement(properties_xml, "Groups")
    fields_xml = SubElement(properties_xml, "Fields")

    field_meta: EntityFieldType
    for name, field_meta in entity.__fields__.items():
        field_xml = SubElement(fields_xml, "Field", attrib={
            "name": field_meta.name,
            "type": field_meta.type,
            "nullable": serialize_bool(field_meta.nullable),
            "hidden": serialize_bool(field_meta.hidden),
            "readonly": serialize_bool(field_meta.readonly),
            "description": field_meta.description or "",
            "evaluator": field_meta.evaluator or "",
            "displayName": field_meta.display_name,
        })

        sample = SubElement(field_xml, "SampleValue")
        sample.text = field_meta.sample_value or ""

    return entity_xml

