import uuid
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement

from .entities import Phrase, translate_legacy_property_name, entity_property_map
from .overlays import OverlayPosition, OverlayType
from .utils import remove_invalid_xml_chars, serialize_xml

BOOKMARK_COLOR_NONE = "-1"
BOOKMARK_COLOR_BLUE = "0"
BOOKMARK_COLOR_GREEN = "1"
BOOKMARK_COLOR_YELLOW = "2"
BOOKMARK_COLOR_PURPLE = "3"
BOOKMARK_COLOR_RED = "4"
BOOKMARK_CLRS = {
    "none": BOOKMARK_COLOR_NONE,
    "blue": BOOKMARK_COLOR_BLUE,
    "green": BOOKMARK_COLOR_GREEN,
    "yellow": BOOKMARK_COLOR_YELLOW,
    "purple": BOOKMARK_COLOR_PURPLE,
    "red": BOOKMARK_COLOR_RED,
}

LINK_STYLE_NORMAL = "0"
LINK_STYLE_DASHED = "1"
LINK_STYLE_DOTTED = "2"
LINK_STYLE_DASHDOT = "3"
LINK_STYLES = {
    "normal": LINK_STYLE_NORMAL,
    "dashed": LINK_STYLE_DASHED,
    "dotted": LINK_STYLE_DOTTED,
    "dashdot": LINK_STYLE_DASHDOT,
}

UIM_FATAL = 'FatalError'
UIM_PARTIAL = 'PartialError'
UIM_INFORM = 'Inform'
UIM_DEBUG = 'Debug'
UIM_TYPES = {
    "fatal": UIM_FATAL,
    "partial": UIM_PARTIAL,
    "inform": UIM_INFORM,
    "debug": UIM_DEBUG,
}

ADD_FIELD_TEMPLATE = "<Field MatchingRule=\"%(matching)s\" Name=\"%(name)s\" DisplayName=\"%(display)s\"><![CDATA[%(value)s]]></Field>"
DISP_INFO_TEMPLATE = "<Label Name=\"%(name)s\" Type=\"text/html\"><![CDATA[' %(content)s ']]></Label>"
UIM_TEMPLATE = "<UIMessage MessageType=\"%(type)s\">%(text)s</UIMessage>"
OVERLAY_TEMPLATE = "<Overlay position=\"%(position)s\" propertyName=\"%(property_name)s\" type=\"%(type)s\"/>"


class MaltegoEntity(object):
    def __init__(self, type=None, value=None):
        self.entityType = type if type else Phrase
        self.value = value if value else ""

        self.weight = 100
        self.additionalFields = []
        self.displayInformation = []
        self.iconURL = ""
        self.overlays = []

    def setType(self, type=None):
        if type:
            self.entityType = type

    def setValue(self, value=None):
        if value:
            self.value = value

    def setWeight(self, weight=None):
        if weight:
            self.weight = weight

    def addDisplayInformation(self, content=None, title='Info'):
        if content:
            self.displayInformation.append([title, content])

    def addProperty(self, fieldName=None, displayName=None, matchingRule='loose', value=None):
        self.additionalFields.append([fieldName, displayName, matchingRule, value])

    def setIconURL(self, url=None):
        if url:
            self.iconURL = url

    def setLinkColor(self, color):
        self.addProperty('link#maltego.link.color', 'LinkColor', '', color)

    def setLinkStyle(self, style):
        self.addProperty('link#maltego.link.style', 'LinkStyle', '', style)

    def setLinkThickness(self, thick):
        self.addProperty('link#maltego.link.thickness', 'Thickness', '', str(thick))

    def setLinkLabel(self, label):
        self.addProperty('link#maltego.link.label', 'Label', '', label)

    def reverseLink(self):
        self.addProperty('link#maltego.link.direction', 'link#maltego.link.direction', 'loose', 'output-to-input')

    def addCustomLinkProperty(self, fieldName=None, displayName=None, value=None):
        self.addProperty('link#' + fieldName, displayName, '', value)

    def setBookmark(self, bookmark):
        self.addProperty('bookmark#', 'Bookmark', '', bookmark)

    def setNote(self, note):
        self.addProperty('notes#', 'Notes', '', note)

    def addOverlay(
            self, propertyName, position: OverlayPosition, overlayType: OverlayType
    ):
        self.overlays.append([propertyName, position.value, overlayType.value])

    def add_field_to_xml(self, additional_field):
        name, display, matching, value = additional_field
        matching = "strict" if matching.lower().strip() == "strict" else "loose"

        return ADD_FIELD_TEMPLATE % {
            "matching": matching,
            "name": name,
            "display": display,
            "value": remove_invalid_xml_chars(value),
        }

    def disp_info_to_xml(self, disp_info):
        name, content = disp_info

        return DISP_INFO_TEMPLATE % {
            "content": remove_invalid_xml_chars(content),
            "name": name,
        }

    def build_xml(self) -> Element:
        entity_xml = Element('Entity', attrib={'Type': self.entityType})

        value_xml = SubElement(entity_xml, 'Value')
        value_xml.text = str(self.value)

        weight_xml = SubElement(entity_xml, 'Weight')
        weight_xml.text = str(self.weight)

        if self.displayInformation:
            display_infos_xml = SubElement(entity_xml, 'DisplayInformation')
            for display_info in self.displayInformation:
                title, content = display_info

                display_info_xml = SubElement(display_infos_xml, 'Label', attrib={'Name': title, 'Type': "text/html"})
                # for some reason, the client accepts escaped html and renders it correctly, so we don't need CDATA
                display_info_xml.text = str(content)

        if self.additionalFields:
            properties_xml = SubElement(entity_xml, 'AdditionalFields')
            for prop in self.additionalFields:
                title, display, matching, val = prop
                matching = "strict" if matching.lower().strip() == "strict" else "loose"

                field_xml = SubElement(properties_xml, 'Field',
                                       attrib={'Name': str(title),
                                               'DisplayName': str(display),
                                               'MatchingRule': matching})
                field_xml.text = str(val)

        if self.overlays:
            overlays_xml = SubElement(entity_xml, 'Overlays')
            for overlay in self.overlays:
                property_name, position, overlay_type = overlay

                SubElement(overlays_xml, 'Overlay',
                           attrib={'propertyName': property_name,
                                   'position': position,
                                   'type': overlay_type})

        if self.iconURL:
            icon_xml = SubElement(entity_xml, 'IconURL')
            icon_xml.text = self.iconURL

        return entity_xml

    def returnEntity(self):
        return serialize_xml(self.build_xml())


class MaltegoTransform(object):
    def __init__(self):
        self.entities = []
        self.exceptions = []
        self.UIMessages = []

    def addEntity(self, type=None, value=None):
        entity = MaltegoEntity(type, value)
        self.entities.append(entity)
        return entity

    def addUIMessage(self, message, messageType="Inform"):
        self.UIMessages.append([messageType, message])

    def addException(self, exceptionString):
        self.exceptions.append(exceptionString)

    def build_exceptions_xml(self):
        message_xml = Element('MaltegoMessage')
        exceptions_message_xml = SubElement(message_xml, 'MaltegoTransformExceptionMessage')
        exceptions_xml = SubElement(exceptions_message_xml, 'Exceptions')

        for exception in self.exceptions:
            exception_xml = SubElement(exceptions_xml, 'Exception')
            exception_xml.text = exception

        return message_xml

    def throwExceptions(self):
        return serialize_xml(self.build_exceptions_xml())

    def build_xml(self) -> Element:
        message_xml = Element('MaltegoMessage')
        response_xml = SubElement(message_xml, 'MaltegoTransformResponseMessage')

        entities_xml = SubElement(response_xml, 'Entities')
        for entity in self.entities:
            entities_xml.append(entity.build_xml())

        ui_messages_xml = SubElement(response_xml, 'UIMessages')
        for ui_message in self.UIMessages:
            message_type, message_content = ui_message

            ui_message_xml = SubElement(ui_messages_xml, 'UIMessage', attrib={'MessageType': message_type})
            ui_message_xml.text = message_content

        return message_xml

    def returnOutput(self):
        return serialize_xml(self.build_xml())


class MaltegoMsg:
    @staticmethod
    def _get_text(element):
        for child in element.childNodes:
            if child.nodeType == child.TEXT_NODE:
                return child.data

    @staticmethod
    def _get_int(element, tag_name, attr_name=None):
        try:
            element = element.getElementsByTagName(tag_name)[0]
            value = MaltegoMsg._get_text(element) if not attr_name else element.getAttribute(attr_name)
            return int(value)
        except ValueError:
            print("Error: Unable to convert XML value for '%s' to an integer." % tag_name)
            return 0

    def __init__(self, MaltegoXML="", LocalArgs=[]):
        self.TransformSettings = {}
        self.Properties = {}

        if MaltegoXML:
            maltego_msg = minidom.parseString(MaltegoXML)
            entities = maltego_msg.getElementsByTagName("Entity")
            entity = entities[0]

            self.Value = self._get_text(entity.getElementsByTagName("Value")[0])
            self.Type = entity.attributes["Type"].value

            self.Weight = self._get_int(entity, "Weight")
            self.Slider = self._get_int(maltego_msg, "Limits", attr_name="SoftLimit")
            self.Genealogy = []
            genealogy_tag = maltego_msg.getElementsByTagName("Genealogy")
            genealogy_types = genealogy_tag[0].getElementsByTagName("Type") if genealogy_tag else []
            for genealogy_type_tag in genealogy_types:
                entity_type_name = genealogy_type_tag.getAttribute("Name")
                entity_type_old_name = genealogy_type_tag.getAttribute("OldName")
                entity_type = {"Name": entity_type_name,
                               "OldName": entity_type_old_name if entity_type_old_name else None}
                self.Genealogy.append(entity_type)

            # Additional Fields
            additional_fields_tag = entity.getElementsByTagName("AdditionalFields")
            additional_fields = additional_fields_tag[0].getElementsByTagName("Field") if additional_fields_tag else []
            for field in additional_fields:
                name = field.getAttribute("Name")
                value = self._get_text(field)
                self.Properties[name] = value
                for entity_type in self.Genealogy:
                    v3_property_name = translate_legacy_property_name(entity_type["Name"], name)
                    if v3_property_name is not None:
                        self.Properties[v3_property_name] = value

            # Transform Settings
            settings_tag = maltego_msg.getElementsByTagName("TransformFields")
            settings = settings_tag[0].getElementsByTagName("Field") if settings_tag else []
            for setting in settings:
                name = setting.getAttribute("Name")
                value = self._get_text(setting)
                self.TransformSettings[name] = value

        elif LocalArgs:
            self.Value = LocalArgs[0]
            self.Type = "local.Unknown"
            self.Genealogy = None

            self.Weight = 100
            self.Slider = 100

            if len(LocalArgs) > 1:
                hash_rnd = uuid.uuid4().hex.upper()[0:7]
                equals_rnd = uuid.uuid4().hex.upper()[0:7]
                bslash_rnd = uuid.uuid4().hex.upper()[0:7]
                text = LocalArgs[1] \
                    .replace("\\\\", bslash_rnd) \
                    .replace("\\#", hash_rnd) \
                    .replace("\\=", equals_rnd)

                self.buildProperties(text.split("#"), hash_rnd, equals_rnd, bslash_rnd)

    def clearLegacyProperties(self):
        to_clear = set()
        for entity_type in self.Genealogy or []:
            for prop_name in entity_property_map.get(entity_type["Name"], []):
                to_clear.add(prop_name)

        for field_name in to_clear:
            if field_name in self.Properties:
                del self.Properties[field_name]

    def buildProperties(self, key_value_array, hash_rnd, equals_rnd, bslash_rnd):
        self.Properties = {}
        for property_section in key_value_array:
            name, value = property_section.split("=", 2)
            self.Properties[name] = value \
                .replace(hash_rnd, "#") \
                .replace(equals_rnd, "=") \
                .replace(bslash_rnd, "\\")

    def getProperty(self, key):
        return self.Properties.get(key)

    def getTransformSetting(self, key):
        return self.TransformSettings.get(key)
