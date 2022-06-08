from maltego_trx import VERSION
from .maltego import MaltegoMsg
from .registry import mapping
from .server import print_transforms, run_transform, get_exception_message

"""
Receive commands run inside a project folder.
"""


def handle_run(name, args, app, port=8080, ssl_context=None, debug=False):
    if name == "__main__":
        if len(args) >= 2:
            command = args[1].lower()
            if command == "runserver":
                print("\n=== Maltego Transform Server: v%s ===\n" % VERSION)
                print_transforms()
                app.run(host="0.0.0.0", port=port, debug=debug, ssl_context=ssl_context)
            elif command == "list":
                print_transforms()
            elif command == "local" and len(args) > 3:
                transform_name = args[2].lower()
                if transform_name in mapping:
                    client_msg = MaltegoMsg(LocalArgs=args[3:])
                    print(run_transform(transform_name, client_msg)[0])
                else:
                    print(get_exception_message(msg="Unable to find a transform matching '%s'." % transform_name))

        else:
            commands = ["list", "local", "runserver"]
            print("Command not recognised. Available commands are:\r\n{0}".format("\r\n".join(commands)))
