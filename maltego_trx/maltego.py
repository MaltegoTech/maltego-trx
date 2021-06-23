import uuid
from dataclasses import dataclass, field
from typing import AnyStr, TypedDict, Literal
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from .entities import translate_legacy_property_name
from .overlays import OverlayType, OverlayPosition


@dataclass()
class DisplayInfo:
    name: str
    content: str

    def build_xml(self) -> Element:
        return Element('Label', attrib={'Name': self.name, 'Content': self.content})


@dataclass()
class EntityProperty:
    name: str
    display: str
    value: str
    matching: str = field(default=None)

    def build_xml(self) -> Element:
        field_xml = Element('Field', attrib={'Name':         self.name,
                                             'DisplayName':  self.display,
                                             'MatchingRule': self.matching})

        field_xml.text = f'<![CDATA[{self.value}]]>'
        return field_xml


@dataclass()
class EntityOverlay:
    property_name: str
    position: OverlayPosition
    overlay_type: OverlayType

    def build_xml(self) -> Element:
        return Element('Overlay', attrib={'propertyName': self.property_name,
                                          'position':     self.position,
                                          'type':         self.overlay_type})


@dataclass()
class UiMessage:
    message: str
    message_type: Literal['Inform', 'Debug', 'FatalError', 'PartialError'] = field(default='Inform')

    def build_xml(self) -> Element:
        ui_message = Element('UIMessage', attrib={'MessageType': self.message_type})
        ui_message.text = self.message

        return ui_message


@dataclass()
class CleanMaltegoEntity:
    entity_type: str
    value: str

    weight: int = field(default=100)

    display_information: list[DisplayInfo] = field(default_factory=list)
    icon_url: str = field(default="")

    properties: list[EntityProperty] = field(default_factory=list)
    overlays: list[EntityOverlay] = field(default_factory=list)

    def add_properties(self, *properties: EntityProperty):
        self.properties.extend(properties)

    def add_overlays(self, *overlays: EntityOverlay):
        self.overlays.extend(overlays)

    def build_xml(self) -> Element:
        entity = Element('Entity')
        value = Element('Value')
        value.text = f'<![CDATA[{self.entity_type}]]>'

        weight = Element('Weight')
        weight.text = f'<![CDATA[{self.weight}]]>'

        display_info_xml = Element('DisplayInformation')
        for display_info in self.display_information:
            display_info_xml.append(display_info.build_xml())

        properties_xml = Element('AdditionalFields')
        for prop in self.properties:
            properties_xml.append(prop.build_xml())

        overlays_xml = Element('Overlays')
        for overlay in self.overlays:
            overlays_xml.append(overlay.build_xml())

        icon_xml = Element('IconURL')
        icon_xml.text = self.icon_url

        return entity


@dataclass()
class MaltegoResponse:
    entities: list[CleanMaltegoEntity] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)
    ui_messages: list[UiMessage] = field(default_factory=list)

    def build_exceptions_xml(self) -> Element:
        exceptions_xml = Element('Exceptions')
        for exception in self.exceptions:
            exception_xml = Element('Exception')
            exception_xml.text = exception

            exceptions_xml.append(exception_xml)

        response_message = Element('MaltegoTransformResponseMessage')
        response_message.append(exceptions_xml)

        message = Element('MaltegoMessage')
        message.append(response_message)

        return message

    def build_xml(self) -> Element:
        entities_xml = Element('Entities')
        for entity in self.entities:
            entities_xml.append(entity.build_xml())

        ui_message_xml = Element('UIMessages')
        for ui_message in self.ui_messages:
            ui_message_xml.append(ui_message.build_xml())

        response_message = Element('MaltegoTransformResponseMessage')
        response_message.append(entities_xml)
        response_message.append(ui_message_xml)

        message = Element('MaltegoMessage')
        message.append(response_message)

        return message


class Genealogy(TypedDict):
    name: str
    old_name: str


class MaltegoRequest:
    value: str
    properties: dict[str, str]
    type: str

    weight: int
    slider: int

    genealogy: list[Genealogy]
    settings: dict[str, str]

    @staticmethod
    def _parse_entity(entity: Element, genealogy: list[Genealogy]) -> dict[str, str]:
        properties = dict()
        for prop in entity.iter("Field"):
            name = prop.attrib.get("Name")

            properties[name] = prop.text

            for entity_type in genealogy:
                v3_property_name = translate_legacy_property_name(entity_type["name"], name)
                if v3_property_name is not None:
                    properties[v3_property_name] = prop.text

        return properties

    @staticmethod
    def _parse_genealogy(genealogy_xml: Element) -> list[Genealogy]:
        genealogy = list()
        for genealogy_type in genealogy_xml.iter('Type'):
            entity_type_name = genealogy_type.attrib.get("Name")
            entity_type_old_name = genealogy_type.attrib.get("OldName", None)

            genealogy.append(Genealogy(name=entity_type_name, old_name=entity_type_old_name))

        return genealogy

    @staticmethod
    def _parse_settings(settings_xml: Element) -> dict[str, str]:
        settings = {}
        for setting in settings_xml.iter('Field'):
            name = setting.attrib.get('Name')
            settings[name] = setting.text

        return settings

    @classmethod
    def from_xml(cls, xml_string: AnyStr) -> 'MaltegoRequest':
        request: Element = ElementTree.fromstring(xml_string)

        message = MaltegoRequest()

        message.type = request.find('Type')
        message.value = request.findtext('Value')
        message.slider = int(request.findtext('Slider'))

        limit = request.find('Limits').attrib.get('SoftLimit')
        message.weight = int(limit)

        genealogy_xml = request.find('Genealogy')
        message.genealogy = cls._parse_genealogy(genealogy_xml)

        entity_xml = next(request.iter('Entity'))
        message.entity = cls._parse_entity(entity_xml, message.genealogy)

        settings_xml = request.find('TransformFields')
        message.settings = cls._parse_settings(settings_xml)

        return message

    @classmethod
    def from_local_args(cls, local_args: list) -> 'MaltegoRequest':
        message = MaltegoRequest()

        message.value = local_args[0]

        message.type = "local.Unknown"
        message.genealogy = None

        message.weight = 100
        message.slider = 100

        # don't know what this does
        if len(local_args) > 1:
            hash_rnd = uuid.uuid4().hex.upper()[0:7]
            equals_rnd = uuid.uuid4().hex.upper()[0:7]
            bslash_rnd = uuid.uuid4().hex.upper()[0:7]
            text = local_args[1] \
                .replace("\\\\", bslash_rnd) \
                .replace("\\#", hash_rnd) \
                .replace("\\=", equals_rnd)

            properties = {}
            for property_section in text.split("#"):
                name, value = property_section.split("=", 2)
                properties[name] = value \
                    .replace(hash_rnd, "#") \
                    .replace(equals_rnd, "=") \
                    .replace(bslash_rnd, "\\")

            message.properties = properties
            message.settings = {}

        return message
