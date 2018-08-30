import re
from six import text_type, binary_type


def name_to_path(name):
    # Convert function name to a URL path
    path = name.replace("_", "-")
    return path.lower()


def make_utf8(val):
    """
    Py2: makes variable a utf-8 encoded Unicode type
    Py3: make variable a utf-8 encoded str type
    :param val: the variable we want unicode encoded
    :return: val {Byte/Unicode}
    """
    return force_encoding(val, 'utf-8')


def make_printable(val):
    """
    Py2: makes variable a ascii encoded Unicode type
    Py3: make variable a ascii encoded str type
    :param val: the variable we want unicode encoded
    :return: val {Byte/Unicode}
    """
    return force_encoding(val, 'ascii')


def force_encoding(val, encoding):
    if type(val) == text_type:
        return val.encode(encoding, 'replace').decode(encoding, 'replace')
    elif type(val) == binary_type:
        return val.decode(encoding, 'replace')
    else:
        return text_type(val).encode(encoding, 'replace').decode(encoding, 'replace')


def remove_invalid_xml_chars(val):
    """
    Remove characters which aren't allowed in XML.
    :param val:
    :return:
    """
    val = make_utf8(val)
    val = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '?', val)
    return val