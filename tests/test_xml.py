from xml.etree.ElementTree import Element

from maltego_trx.maltego import MaltegoTransform
from maltego_trx.overlays import OverlayType, OverlayPosition
from maltego_trx.utils import serialize_xml


def _serialize_xml(xml: Element) -> str:
    # we need to use canonical XML (python3.8+), because python3.6 and python3.7 sort the attrs alphabetically
    return serialize_xml(xml, indent=False, canonicalize=True, short_empty_elements=False)


def test_entity_with_value(snapshot):
    response = MaltegoTransform()
    response.addEntity("maltego.Phrase", "Hello Spencer!")
    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_entity_with_none_value(caplog, snapshot):
    response = MaltegoTransform()
    response.addEntity("maltego.Phrase", None)
    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot

    captured = caplog.messages
    assert captured == snapshot


def test_entity_with_none_type_is_phrase(caplog, snapshot):
    response = MaltegoTransform()
    response.addEntity(None, "Value")
    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot

    captured = caplog.messages
    assert captured == snapshot


def test_entity_property_with_no_field_name_gets_skipped(caplog, snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addProperty(fieldName=None, displayName="displayNameTest", value="valueTest",
                       matchingRule="loose")

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot

    captured = caplog.messages
    assert captured == snapshot


def test_entity_property_with_no_display_name_gets_field_name(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addProperty(fieldName="fieldNameTest", displayName=None, value="valueTest",
                       matchingRule="loose")

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_entity_property_with_no_matching_rule_gets_loose_matching_rule(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addProperty(fieldName="fieldNameTest", displayName="displayNameTest", matchingRule=None, value="valueTest")

    response_xml = response.build_xml()
    assert _serialize_xml(response_xml) == snapshot


def test_entity_property_with_no_value_gets_empty_value(caplog, snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addProperty(fieldName="fieldNameTest", displayName="displayNameTest", value=None, matchingRule="loose")

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_entity_with_properties(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addProperty(fieldName="fieldNameTest", displayName=None, value="valueTest",
                       matchingRule="loose")
    entity.addProperty(fieldName="fieldNameTest2", displayName="displayNameTest2", value="valueTest2",
                       matchingRule="strict")

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_entity_with_display_information(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addDisplayInformation(title="Display Info Title", content="<p>Display Info Content</p>")

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_entity_with_icon(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.setIconURL(url="https://www.maltego.com/img/maltego-logo/maltego-horizontal.png")

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_entity_with_overlays(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addOverlay('#45e06f', OverlayPosition.NORTH_WEST, OverlayType.COLOUR)

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_response_with_ui_message(snapshot):
    response = MaltegoTransform()
    response.addUIMessage("Test Message", messageType="inform")

    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_response_with_exception(snapshot):
    response = MaltegoTransform()
    response.addException("Test Exception")

    response_xml = response.build_exceptions_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_exception_message(snapshot):
    response = MaltegoTransform()
    response.addUIMessage("Test Exception", "PartialError")
    response_xml = response.build_xml()

    assert _serialize_xml(response_xml) == snapshot


def test_all_null_values(caplog, snapshot):
    response = MaltegoTransform()
    entity = response.addEntity(None, None)
    entity.addProperty(fieldName=None, displayName=None, value=None,
                       matchingRule=None)

    entity.addDisplayInformation(title=None, content=None)
    entity.setIconURL(url=None)

    entity.addOverlay(propertyName=None, position=OverlayPosition.NORTH_WEST, overlayType=OverlayType.COLOUR)

    entity.setLinkLabel(None)
    entity.setLinkThickness(None)
    entity.setLinkColor(None)
    entity.setLinkStyle(None)
    entity.setType(None)
    entity.setWeight(None)
    entity.addCustomLinkProperty(None, None, None)
    entity.setNote(None)
    entity.setValue(None)

    response.addUIMessage(None, messageType=None)
    response.addException(None)

    response_xml = response.build_xml()
    assert _serialize_xml(response_xml) == snapshot

    captured = caplog.messages
    assert captured == snapshot
