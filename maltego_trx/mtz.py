import datetime
from typing import Iterable, List
from xml.etree.ElementTree import Element, SubElement


def create_last_sync_timestamp(timestamp: datetime.datetime = None) -> str:
    timestamp = timestamp or datetime.datetime.utcnow()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def create_local_server_xml(transform_names: Iterable[str]) -> Element:
    server_xml = Element("MaltegoServer", attrib={"name": "Local",
                                                  "enabled": "true",
                                                  "description": "Local transforms hosted on this machine",
                                                  "url": "http://localhost",
                                                  })
    last_sync_xml = SubElement(server_xml, "LastSync")
    last_sync_xml.text = create_last_sync_timestamp()

    SubElement(server_xml, "Protocol", attrib={"version": "0.0"})
    SubElement(server_xml, "Authentication", attrib={"type": "none"})

    transforms_xml = SubElement(server_xml, "Transforms")
    for name in transform_names:
        SubElement(transforms_xml, "Transform", attrib={"name": name})

    SubElement(server_xml, "Seeds")

    return server_xml


def create_settings_xml(working_dir: str, command: str, params: str, debug: bool) -> Element:
    settings_xml = Element("TransformSettings",
                           attrib={"enabled": "true",
                                   "disclaimerAccepted": "false",
                                   "showHelp": "true",
                                   "runWithAll": "true",
                                   "favorite": "false",
                                   })
    properties_xml = SubElement(settings_xml, "Properties")

    command_xml = SubElement(properties_xml, "Property",
                             attrib={"name": "transform.local.command",
                                     "type": "string",
                                     "popup": "false",
                                     })
    command_xml.text = command

    parameters_xml = SubElement(properties_xml, "Property",
                                attrib={
                                    "name": "transform.local.parameters",
                                    "type": "string",
                                    "popup": "false",
                                })
    parameters_xml.text = params

    working_directory_xml = SubElement(properties_xml, "Property",
                                       attrib={
                                           "name": "transform.local.working-directory",
                                           "type": "string",
                                           "popup": "false",
                                       })
    working_directory_xml.text = working_dir

    debug_xml = SubElement(properties_xml, "Property",
                           attrib={
                               "name": "transform.local.debug",
                               "type": "boolean",
                               "popup": "false",
                           })
    debug_xml.text = "true" if debug else "false"

    return settings_xml


def create_transform_xml(name: str, display_name: str, description: str, input_entity: str, author: str) -> Element:
    transform_xml = Element("MaltegoTransform",
                            attrib={"name": name,
                                    "displayName": display_name,
                                    "abstract": "false",
                                    "template": "false",
                                    "visibility": "public",
                                    "description": description,
                                    "author": author,
                                    "requireDisplayInfo": "false",
                                    })

    adapter_xml = SubElement(transform_xml, "TransformAdapter")
    adapter_xml.text = "com.paterva.maltego.transform.protocol.v2api.LocalTransformAdapterV2"

    properties_xml = SubElement(transform_xml, "Properties")
    fields_xml = SubElement(properties_xml, "Fields")

    SubElement(fields_xml, "Property",
               attrib={"name": "transform.local.command",
                       "type": "string",
                       "nullable": "false",
                       "hidden": "false",
                       "readonly": "false",
                       "description": "The command to execute for this transform",
                       "popup": "false",
                       "abstract": "false",
                       "visibility": "public",
                       "auth": "false",
                       "displayName": "Command line",
                       })
    SubElement(fields_xml, "Property",
               attrib={"name": "transform.local.parameters",
                       "type": "string",
                       "nullable": "true",
                       "hidden": "false",
                       "readonly": "false",
                       "description": "The parameters to pass to the transform command",
                       "popup": "false",
                       "abstract": "false",
                       "visibility": "public",
                       "auth": "false",
                       "displayName": "Command parameters",
                       })
    SubElement(fields_xml, "Property",
               attrib={"name": "transform.local.working-directory",
                       "type": "string",
                       "nullable": "true",
                       "hidden": "false",
                       "readonly": "false",
                       "description": "The working directory used when invoking the executable",
                       "popup": "false",
                       "abstract": "false",
                       "visibility": "public",
                       "auth": "false",
                       "displayName": "Working directory",

                       })
    SubElement(fields_xml, "Property",
               attrib={
                   "name": "transform.local.debug",
                   "type": "boolean",
                   "nullable": "true",
                   "hidden": "false",
                   "readonly": "false",
                   "description": "When this is set, the transform's text output will be "
                                  "printed to the output window",
                   "popup": "false",
                   "abstract": "false",
                   "visibility": "public",
                   "auth": "false",
                   "displayName": "Show debug info"
               })

    input_constraints_xml = SubElement(transform_xml, "InputConstraints")
    SubElement(input_constraints_xml, "Entity",
               attrib={"type": input_entity,
                       "min": "1", "max": "1"})

    SubElement(transform_xml, "OutputEntities")
    SubElement(transform_xml, "defaultSets")

    stealth_level = SubElement(transform_xml, "StealthLevel")
    stealth_level.text = "0"

    return transform_xml


def create_transform_set_xml(name: str, description: str, transforms: List[str]) -> Element:
    set_xml = Element("TransformSet",
                      attrib={
                          "name": name,
                          "description": description
                      })

    transforms_xml = SubElement(set_xml, "Transforms")
    for transform in transforms:
        SubElement(transforms_xml,
                   "Transform",
                   attrib={
                       "name": transform
                   })

    return set_xml
