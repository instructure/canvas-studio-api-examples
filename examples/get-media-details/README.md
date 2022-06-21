# Get detailed information about media

This script collects and prints the following information about a media:
- basic details: id, title, description, duration, size, created_at
- owner: the owner of the media
- collection: the collection where the media is uploaded to
- captions: list of captions the media has
- courses: list of courses where the media is embedded into
- tags: list of tags the media has
- users: list of users whom the media is shared with (either directly or indirectly) and the permission they have to the media

## How to use

Before using this script, don't forget to configure your OAuth credentials (see [here](../../README.md#authorization)).

```bash
bin/run examples/get-media-details/main.py --subdomain <school_subdomain> <media_id>
```
