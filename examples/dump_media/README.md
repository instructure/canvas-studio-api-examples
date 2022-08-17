# Download all media from a Studio account

This script downloads all media in a file / directory hierarchy:

- every user has a separated folder
- every custom collection is downloaded into a separate folder
- every course collection is downloaded into a separate folder
- the media will be downloaded multiple times, if it's embedded into more than one course
- media in "My library" goes directly to the user's folder
- if the media is embedded into a course, it will only be downloaded into the course folder, but not in the user's folder
- captions (if exists) are next to the media
- the language of the caption is on the end of the filename
- the highest available quality gets downloaded

## How to use

Before using this script, don't forget to configure your OAuth credentials (see [here](../../README.md#authorization)).

```bash
bin/run examples/dump_media/main.py  --root_dir <folder name>
```

## Optional parameters

- --dry-run: creates the folder hierarchy, but does not download anything
- --log_to_file: creates a log file with detailed log
