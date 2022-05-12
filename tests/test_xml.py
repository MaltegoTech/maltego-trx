import os
from xml.etree import ElementTree

from maltego_trx.maltego import MaltegoTransform
from maltego_trx.overlays import OverlayType, OverlayPosition
from maltego_trx.server import build_exception_message

XML_SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'xml_samples')


def test_entity_with_value():
    response = MaltegoTransform()
    response.addEntity("maltego.Phrase", "Hello Spencer!")
    response_xml = response.returnOutput()

    with open(os.path.join(XML_SAMPLES_DIR, "simple_entity.response.xml"), "r") as response_xml_file:
        sample_xml = ElementTree.canonicalize(response_xml_file.read(), strip_text=True)

    assert response_xml == sample_xml


def test_entity_with_properties():
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addProperty(fieldName="fieldNameTest", displayName="displayNameTest", value="valueTest",
                       matchingRule="loose")
    entity.addProperty(fieldName="fieldNameTest2", displayName="displayNameTest2", value="valueTest2",
                       matchingRule="strict")

    response_xml = response.returnOutput()

    with open(os.path.join(XML_SAMPLES_DIR, "entity_with_properties.response.xml"), "r") as response_xml_file:
        sample_xml = response_xml_file.read()
        sample_xml = ElementTree.canonicalize(sample_xml, strip_text=True)

    assert response_xml == sample_xml


def test_entity_with_display_information():
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addDisplayInformation(title="Display Info Title", content="<p>Display Info Content</p>")

    response_xml = response.returnOutput()

    with open(os.path.join(XML_SAMPLES_DIR, "entity_with_display_information.response.xml"), "r") as response_xml_file:
        sample_xml = response_xml_file.read()
        sample_xml = ElementTree.canonicalize(sample_xml, strip_text=True)

    assert response_xml == sample_xml


def test_entity_with_icon():
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.setIconURL(url="https://www.maltego.com/img/maltego-logo/maltego-horizontal.png")

    response_xml = response.returnOutput()

    with open(os.path.join(XML_SAMPLES_DIR, "entity_with_icon_url.response.xml"), "r") as response_xml_file:
        sample_xml = response_xml_file.read()
        sample_xml = ElementTree.canonicalize(sample_xml, strip_text=True)

    assert response_xml == sample_xml


def test_entity_with_overlays():
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addOverlay('#45e06f', OverlayPosition.NORTH_WEST, OverlayType.COLOUR)

    response_xml = response.returnOutput()

    with open(os.path.join(XML_SAMPLES_DIR, "entity_with_overlay.response.xml"), "r") as response_xml_file:
        sample_xml = response_xml_file.read()
        sample_xml = ElementTree.canonicalize(sample_xml, strip_text=True)

    assert response_xml == sample_xml


def test_response_with_ui_message():
    response = MaltegoTransform()
    response.addUIMessage("Test Message", messageType="inform")

    response_xml = response.returnOutput()

    with open(os.path.join(XML_SAMPLES_DIR, "ui_message.response.xml"), "r") as response_xml_file:
        sample_xml = response_xml_file.read()
        sample_xml = ElementTree.canonicalize(sample_xml, strip_text=True)

    assert response_xml == sample_xml


def test_response_with_exception():
    response = MaltegoTransform()
    response.addException("Test Exception")

    response_xml = response.throwExceptions()

    with open(os.path.join(XML_SAMPLES_DIR, "exception.response.xml"), "r") as response_xml_file:
        sample_xml = response_xml_file.read()
        sample_xml = ElementTree.canonicalize(sample_xml, strip_text=True)

    assert response_xml == sample_xml


def test_exception_message():
    response_xml = build_exception_message("Test Exception")

    response_xml_canonicalize = ElementTree.tostring(response_xml, short_empty_elements=False)
    response_xml_canonicalize = ElementTree.canonicalize(response_xml_canonicalize)

    with open(os.path.join(XML_SAMPLES_DIR, "server_exception.response.xml"), "r") as response_xml_file:
        sample_xml = response_xml_file.read()
        sample_xml = ElementTree.canonicalize(sample_xml, strip_text=True)

    assert response_xml == sample_xml_canonicalize
