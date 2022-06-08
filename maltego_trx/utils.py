import math
import re
import sys
from typing import TypeVar, Callable, Hashable, Iterable, Generator, Sequence
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

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
    Py2: makes variable an ascii encoded Unicode type
    Py3: make variable an ascii encoded str type
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


T = TypeVar('T')


def filter_unique(get_identifier: Callable[[T], Hashable], collection: Iterable[T]) -> Generator[T, None, None]:
    seen = set()
    for item in collection:
        identifier = get_identifier(item)

        if identifier in seen:
            continue

        seen.add(identifier)

        yield item


def chunk_list(data: Sequence[T], max_chunk_size: int) -> Generator[Sequence[T], None, None]:
    # math.ceil:
    #   number_of_chunks: decimal-places == 0 -> perfect split
    #   number_of_chunks: decimal-places  > 0 -> need one more list to keep len(chunk) <= max_chunk_size

    number_of_chunks = math.ceil(len(data) / max_chunk_size)
    chunk_size = math.ceil(len(data) / number_of_chunks)

    for idx in range(0, len(data), chunk_size):
        yield data[idx:idx + chunk_size]


def pascal_case_to_title(name: str) -> str:
    # https://stackoverflow.com/a/1176023
    name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', name)


def escape_csv_fields(*fields: str, separator: str = ',') -> Generator[str, None, None]:
    """if a field contains the separator, it will be quoted"""
    for f in fields:
        yield f'"{f}"' if separator in f else f


def export_as_csv(header: str, lines: Sequence[str], export_file_path: str, csv_line_limit: int = -1):
    """export a file in as many files as needed to stay below the csv_line_limit (plus header)"""
    if csv_line_limit == -1 or len(lines) <= csv_line_limit:
        with open(export_file_path, "w+") as csv_file:
            csv_file.write(header + "\n")
            csv_file.writelines(map(lambda x: x + "\n", lines))

        return

    # split file to speed-up import into pTDS, iTDS
    chunks = list(chunk_list(lines, csv_line_limit))
    for idx, chunk in enumerate(chunks, 1):
        path, extension = export_file_path.rsplit(".", 1)
        chunked_config_path = f"{path}_{idx}-{len(chunks)}.{extension}"

        with open(chunked_config_path, "w+") as csv_file:
            csv_file.write(header + "\n")
            csv_file.writelines(map(lambda x: x + "\n", chunk))


def serialize_bool(boolean: bool, serialized_true: str, serialized_false: str) -> str:
    return serialized_true if boolean else serialized_false


def serialize_xml(xml: Element) -> str:
    # options are needed to have same xml output for py < 3.8 and py >= 3.8
    output = ElementTree.tostring(xml, encoding='unicode', short_empty_elements=False)

    if sys.version_info[1] >= 8:
        output = ElementTree.canonicalize(output)

    return output
