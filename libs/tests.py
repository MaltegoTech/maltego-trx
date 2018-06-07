from libs.Maltego import MaltegoMsg, MaltegoEntity, LINK_STYLES
from libs.entities import Domain
from server import all_transforms
from legacy_example import dns_to_ip


def test_message():
    with open("libs/request_body.xml") as f:
        xml = f.read()
    msg = MaltegoMsg(xml)
    assert msg.Value == "baidu.com"
    assert msg.Type == "Domain"
    assert msg.Weight == 87
    assert msg.Slider == 12
    assert len(msg.Properties) == 1
    assert len(msg.TransformSettings) == 1
    return msg


def test_discovered_transform(msg):
    legacy_transform = dns_to_ip
    discovered_transform = all_transforms["dnstoip"]
    legacy_xml = legacy_transform(msg)
    discovered_xml = discovered_transform.run_transform(msg)
    assert legacy_xml == discovered_xml


def test_entity_xml():
    ent = MaltegoEntity(Domain, "pàterva.com")  # Test unicode a
    ent.setWeight(10)
    ent.setIconURL("https://www.paterva.com/web7/img/logo.png")
    ent.setLinkColor("000000")
    ent.setLinkStyle(LINK_STYLES["dotted"])
    ent.addDisplayInformation("<a href='%s'>Website</a>" % "https://www.paterva.com/", title="Website")
    xml = ent.returnEntity()
    with open("libs/test_entity.xml") as f:
        correct_xml = f.read()

    assert xml == correct_xml


msg = test_message()
test_discovered_transform(msg)
test_entity_xml()