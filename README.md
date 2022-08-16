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

## Advanced topic: multiple schools, multiple config files

If you want to use these scripts for multiple schools, you can have multiple config files. All of them should start with `config` and end with `.json`, e.g. `config-otherschool.json`. When you run a script that should use this other config, don't forget to specify it:

```
bin/run examples/test/main.py --config config-otherschool.json
```
