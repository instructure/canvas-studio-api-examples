import argparse
import csv
import sys
import json
import io
import tabulate
import uuid

# This script will implement cli for Studio public API.
# Originally wanted to mimick aws cli with
# "studio media show" like syntax, but aws cli heavily
# customizes argparse, see
# https://github.com/aws/aws-cli/blob/45b0063b2d0b245b17a57fd9eebd9fcc87c4426a/awscli/argparser.py

from utils.utils import PublicAPIClient, add_default_arguments, enable_debug_logs


def main():
    parser = argparse.ArgumentParser(add_help=False)
    add_default_arguments(parser)
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="enable debug logs for the requests library",
    ),
    parser.add_argument(
        "--table_format",
        type=str,
        required=False,
        help="tabulated formats",
        choices=list(tabulate._table_formats.keys()),
    )

    args, unprocessed_args = parser.parse_known_args()

    if args.debug:
        enable_debug_logs()

    # We need it for the commands
    subparsers = parser.add_subparsers(help="sub-command help")

    studio_cli = StudioCli(args.config)
    studio_cli.build_commands(subparsers)

    if not unprocessed_args:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    command = unprocessed_args[0]

    response = studio_cli.execute(command, args)

    print(response)


class StudioCli:
    def __init__(self, config):
        self.public_api_client = PublicAPIClient(config)
        self.schema = self._get_schema()
        self.commands = {}

    def build_commands(self, subparsers):
        for path, methods in self.schema["paths"].items():
            for method, data in methods.items():
                command = Command(path, method, data, self.public_api_client)
                if self._is_valid_command(command):
                    self.commands[command.name] = command
                    self._extend_subparsers(command, subparsers)

    def execute(self, command_name, args):
        command = self.commands[command_name]
        return command.execute(args)

    # https://tw.instructuremedia.com/api/public/apidocs
    def _get_schema(self):
        response = self.public_api_client.request("get", "apidocs", version_prefix="")

        if response.status_code != 200:
            raise Exception(
                f"Could not get details for {response.url}: {response.text}"
            )

        return response.json()

    _type_to_type = {
        "integer": int,
        "string": str,
        # not sure about these
        "object": str,
        "array": str,
        "file": str,
    }

    def _is_valid_command(self, command):
        missing_params = [
            parameter
            for parameter in command.path_params
            if parameter not in command.parameter_names()
        ]

        if missing_params:
            sys.stderr.write(
                f"Skipping {command.name} for {command.path}, params not defined: {missing_params}\n"
            )
            return False

        if any([param["in"] in ["body", "formData"] for param in command.parameters()]):
            # commands in body parameters are not supported atm.
            # same for file/formData parameters
            return False

        return True

    def _extend_subparsers(self, command, subparsers):
        command_parser = subparsers.add_parser(command.name, help=command.summary())

        for param in command.parameters():
            command_parser.add_argument(
                f"--{param['name']}",
                type=StudioCli._type_to_type[param.get("type", "string")],
                required=param.get("required", False),
                choices=param.get("enum", None),
                help=param["description"],
            )


class Command:
    _method_to_command = {
        "delete": "delete",
        "get": "show",
        "post": "add",
        "put": "update",
    }

    def __init__(self, path, method, data, public_api_client):
        self.path = path
        self.method = method
        self.data = data
        self.public_api_client = public_api_client

        self.path_params = [
            parameter[1:-1]
            for parameter in self.path.split("/")
            if (parameter and parameter[0] == "{")
        ]
        path_entities = [
            parameter
            for parameter in path.split("/")
            if (parameter and parameter[0] != "{")
        ]

        self.name = self._create_command_name(method, path_entities)

    def execute(self, args):
        params = {
            name: value
            for name, value in vars(args).items()
            if (name in self.parameter_names() and name not in self.path_params)
        }

        response = self.public_api_client.request(
            self.method, self.path.format(**vars(args)), params=params
        )

        if response.ok:
            return self._process_response(response, args)

        error_message = (
            f"{response.status_code}: {json.loads(response.content.decode())['error']}"
        )

        raise Exception(error_message)

    def parameter_names(self):
        return [parameter["name"] for parameter in self.parameters()]

    def summary(self):
        return self.data["summary"]

    def parameters(self):
        return self.data.get("parameters", {})

    def _is_singular(self):
        if self.method == "post":
            # /media/permissions or /collections/permissions
            if self.path.endswith("permissions"):
                return False

            return True

        if self.method != "get":
            return False

        # "/media/{media_id}/download": {
        if "200" not in self.data["responses"]:
            return False

        return_ok = self.data["responses"]["200"]

        # /perspectives/{perspective_id}/insights/overview
        if "schema" not in return_ok:
            return False

        #     "/media/search": {
        schema = return_ok["schema"]
        props = schema.get("properties", None) or schema["allOf"][0].get(
            "properties", None
        )

        # "/collections/{collection_id}": {
        return_types = [value.get("type", "") for _, value in props.items()]

        return any([return_type != "array" for return_type in return_types])

    def _create_command_name(self, method, path_entities):
        if path_entities[-1] in [
            "search",
            "download",
            "complete",
            "ping",
            "transfer_media",
        ]:
            return "_".join([path_entities[-1]] + path_entities[:-1])
        else:
            command_name = (
                f"{Command._method_to_command[method]}_{'_'.join(path_entities)}"
            )
            if command_name[-1] == "s" and self._is_singular():
                return command_name[:-1]
            else:
                return command_name

    def _is_csv_command(self):
        return self.name in [
            "show_perspectives_insights_overview",
            "show_perspectives_insights_users",
        ]

    def _process_response(self, response, args):
        # can be 'application/json; charset=utf-8' or 'video/mp4'
        content_type = response.headers["Content-Type"].split(";")
        if content_type[0] == "application/json":
            return json.dumps(response.json(), indent=2)

        if self.name.startswith("download_"):
            if content_type[0] in ["video/mp4", "audio/mp4"]:
                extension = "mp4"
            else:
                # for captions it's text/plain
                extension = "str"

            output_filename = f"{str(uuid.uuid4())}.{extension}"
            with open(output_filename, "wb") as tf:
                tf.write(response.content)

            return f"Downloaded {content_type} content to {output_filename}"

        if self._is_csv_command() and args.table_format:
            result = []

            csv_string = response.content.decode()
            reader = csv.reader(io.StringIO(csv_string))

            header = next(reader)
            for row in reader:
                result.append(row)

            # https://github.com/astanin/python-tabulate#table-format
            return tabulate.tabulate(result, headers=header, tablefmt=args.table_format)

        if self.method != "get" and not response.content:
            message = self.data["responses"].get(str(response.status_code), "")
            return f"{response.status_code}: {message}"

        return response.content.decode()


if __name__ == "__main__":
    main()
