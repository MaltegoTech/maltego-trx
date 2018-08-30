# Updated Maltego Python library
# 2018/06/05
# See TRX documentation
from xml.dom import minidom
from .utils import remove_invalid_xml_chars
from .entities import Phrase

VERSION = "1.1"

BOOKMARK_COLOR_NONE = "-1"
BOOKMARK_COLOR_BLUE = "0"
BOOKMARK_COLOR_GREEN = "1"
BOOKMARK_COLOR_YELLOW = "2"
BOOKMARK_COLOR_ORANGE = "3"
BOOKMARK_COLOR_RED = "4"
BOOKMARK_CLRS = {
    "none": BOOKMARK_COLOR_NONE,
    "blue": BOOKMARK_COLOR_BLUE,
    "green": BOOKMARK_COLOR_GREEN,
    "yellow": BOOKMARK_COLOR_YELLOW,
    "orange": BOOKMARK_COLOR_ORANGE,
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

ADD_FIELD_TEMPLATE = "<Field MatchingRule=\"%(matching)s\" Name=\"%(name)s\" DisplayName=\"%(display)s\">%(value)s</Field>"
DISP_INFO_TEMPLATE = "<Label Name=\"%(name)s\" Type=\"text/html\"><![CDATA[' %(content)s ']]></Label>"
UIM_TEMPLATE = "<UIMessage MessageType=\"%(type)s\">%(text)s</UIMessage>"


class MaltegoEntity(object):
    def __init__(self, type=None, value=None):
        self.entityType = type if type else Phrase
        self.value = value if value else ""

        self.weight = 100
        self.additionalFields = []
        self.displayInformation = []
        self.iconURL = ""

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

    def setBookmark(self, bookmark):
        self.addProperty('bookmark#', 'Bookmark', '', bookmark)

    def setNote(self, note):
        self.addProperty('notes#', 'Notes', '', note)

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

    def returnEntity(self):
        lines = []
        lines.append("<Entity Type=\"%s\">" % str(self.entityType))
        lines.append("<Value>%s</Value>" % str(self.value))
        lines.append("<Weight>%s</Weight>" % str(self.weight))
        if self.displayInformation:
            lines.append("<DisplayInformation>")
            for disp_info in self.displayInformation:
                lines.append(self.disp_info_to_xml(disp_info))
            lines.append("</DisplayInformation>")

        if self.additionalFields:
            lines.append("<AdditionalFields>")
            for additional_field in self.additionalFields:
                lines.append(self.add_field_to_xml(additional_field))
            lines.append("</AdditionalFields>")

        if self.iconURL:
            lines.append("<IconURL>%s</IconURL>" % self.iconURL)

        lines.append("</Entity>")
        return "".join(lines)


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

    def throwExceptions(self):
        lines = []
        lines.append("<MaltegoMessage>")
        lines.append("<MaltegoTransformExceptionMessage>")
        lines.append("<Exceptions>")

        for exception in self.exceptions:
            lines.append("<Exception>%s</Exceptions>" % remove_invalid_xml_chars(exception))

        lines.append("</Exceptions>")
        lines.append("</MaltegoTransformExceptionMessage>")
        lines.append("</MaltegoMessage>")
        return "".join(lines)

    def returnOutput(self):
        lines = []
        lines.append("<MaltegoMessage>")
        lines.append("<MaltegoTransformResponseMessage>")

        lines.append("<Entities>")
        for entity in self.entities:
            lines.append(entity.returnEntity())
        lines.append("</Entities>")

        lines.append("<UIMessages>")
        for message in self.UIMessages:
            text, type = message
            lines.append(UIM_TEMPLATE % {"text": text, "type": type})
        lines.append("</UIMessages>")

        lines.append("</MaltegoTransformResponseMessage>")
        lines.append("</MaltegoMessage>")
        return "".join(lines)


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

    def __init__(self, MaltegoXML=""):
        maltego_msg = minidom.parseString(MaltegoXML)
        entities = maltego_msg.getElementsByTagName("Entity")
        entity = entities[0]

        self.Value = self._get_text(entity.getElementsByTagName("Value")[0])
        self.Type = entity.attributes["Type"].value

        self.Weight = self._get_int(entity, "Weight")
        self.Slider = self._get_int(maltego_msg, "Limits", attr_name="SoftLimit")

        # Additional Fields
        self.Properties = {}
        additional_fields_tag = entity.getElementsByTagName("AdditionalFields")
        additional_fields = additional_fields_tag[0].getElementsByTagName("Field") if additional_fields_tag else []
        for field in additional_fields:
            name = field.getAttribute("Name")
            value = self._get_text(field)
            self.Properties[name] = value

        # Transform Settings
        self.TransformSettings = {}
        settings_tag = maltego_msg.getElementsByTagName("TransformFields")
        settings = settings_tag[0].getElementsByTagName("Field") if settings_tag else []
        for setting in settings:
            name = setting.getAttribute("Name")
            value = self._get_text(setting)
            self.TransformSettings[name] = value

    def getProperty(self, key):
        return self.Properties.get(key)

    def getTransformSetting(self, key):
        return self.TransformSettings.get(key)