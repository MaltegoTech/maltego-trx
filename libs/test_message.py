from libs.Maltego import MaltegoMsg
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


msg = test_message()
test_discovered_transform(msg)