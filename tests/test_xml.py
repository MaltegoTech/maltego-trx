from maltego_trx.maltego import MaltegoTransform
from maltego_trx.overlays import OverlayType, OverlayPosition


def test_entity_with_value(snapshot):
    response = MaltegoTransform()
    response.addEntity("maltego.Phrase", "Hello Spencer!")
    response_xml = response.returnOutput()

    assert response_xml == snapshot


def test_entity_with_properties(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addProperty(fieldName="fieldNameTest", displayName="displayNameTest", value="valueTest",
                       matchingRule="loose")
    entity.addProperty(fieldName="fieldNameTest2", displayName="displayNameTest2", value="valueTest2",
                       matchingRule="strict")

    response_xml = response.returnOutput()

    assert response_xml == snapshot


def test_entity_with_display_information(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addDisplayInformation(title="Display Info Title", content="<p>Display Info Content</p>")

    response_xml = response.returnOutput()

    assert response_xml == snapshot


def test_entity_with_icon(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.setIconURL(url="https://www.maltego.com/img/maltego-logo/maltego-horizontal.png")

    response_xml = response.returnOutput()

    assert response_xml == snapshot


def test_entity_with_overlays(snapshot):
    response = MaltegoTransform()
    entity = response.addEntity("maltego.Phrase", "Hello Spencer!")
    entity.addOverlay('#45e06f', OverlayPosition.NORTH_WEST, OverlayType.COLOUR)

    response_xml = response.returnOutput()

    assert response_xml == snapshot


def test_response_with_ui_message(snapshot):
    response = MaltegoTransform()
    response.addUIMessage("Test Message", messageType="inform")

    response_xml = response.returnOutput()

    assert response_xml == snapshot


def test_response_with_exception(snapshot):
    response = MaltegoTransform()
    response.addException("Test Exception")

    response_xml = response.throwExceptions()

    assert response_xml == snapshot


def test_exception_message(snapshot):
    transform_run = MaltegoTransform()
    transform_run.addUIMessage("Test Exception", "PartialError")
    response_xml = transform_run.returnOutput()

    assert response_xml == snapshot
