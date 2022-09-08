# Canvas Studio API examples

In this repository, we collect example scripts that can be useful for the team and Studio account administrators to access the public API of Canvas Studio (documentation can be found at https://tw.instructuremedia.com/api/public/docs/)

## Prerequisites

To run python scripts inside `examples` directory you should first run the installer script:

```bash
bin/install
```

This will handle installing the required packages into virtualenv and create template for the configuration file.

### Authorization

In order to authorize the requests, please add your credentials and subdomain in `JSON` format into the `config.json` file created by install script.

You can generate the necessary credentials as described [here](https://community.canvaslms.com/t5/The-Product-Blog/Connecting-Studio-OAuth-via-Postman/ba-p/259739)

Once you have them in config.json, you won't have to deal with them anymore: the example scripts automatically handle renewing expired tokens.

Note: if you access Studio under `yourschoolname.instructuremedia.com`, then subdomain in config.json should be `yourschoolname`.

### Testing

In order to confirm your credentials, please run:

```bash
bin/run examples/test/main.py
```

## Usage

After the installation, you can run the scripts using `bin/run` script:

```bash
bin/run <path_to_script_file> <arguments>
```

# Advanced topics
## Multiple schools, multiple config files

If you want to use these scripts for multiple schools, you can have multiple config files. All of them should start with `config` and end with `.json`, e.g. `config-otherschool.json`. When you run a script that should use this other config, don't forget to specify it:

```bash
bin/run examples/test/main.py --config config-otherschool.json
```

## Overriding domain and scheme

If you want to use these scripts in other (development) environments, you can also change the domain and the url scheme in the config file. For local development, it would look like this:

```json
{
    "subdomain": "tw",
    "domain": "arc.docker",
    "scheme": "http",
    ...
}
```

## Studio public API client

With `bin/cli` you can discover what capabilities the public API has and prototype the workflows based on the API from UNIX commandline: it downloads the API schema, maps endpoints/methods to commands, for example GET `/media/{media_id}` to `show_media --media_id`.
The script currently does not support commands with parameters in the body of the HTTP request - such as `transfer_media`.

### API discovery

If you run the script in itself, it will list all supported commands with a brief description.
Note that the script supports the `--config` parameter described above.

If you run the script with a command with `--help` it will return with a help about the commands parameters.

```
❯ bin/cli show_media  --help
usage: cli.py show_media [-h] --media_id MEDIA_ID

optional arguments:
  -h, --help           show this help message and exit
  --media_id MEDIA_ID  The ID of the media.
```

### Running a command

If you run a command with all necessary parameters then it will return with payload (can be JSON/CSV output).

```
❯ bin/cli show_media --media_id 2
{
  "media": {
    "id": 2,
    "title": "iphone_front_camera",
    "description": null,
    "duration": 3.042,
    "created_at": "2020-09-18T14:27:40Z",
```