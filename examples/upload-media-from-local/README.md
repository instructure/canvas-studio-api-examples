# Upload media from local

This is a script that can upload media files to Studio from local.

## How to use

Before using this script, don't forget to configure your OAuth credentials (see [here](../../README.md#authorization)).

- To upload a single file:

  ```bash
  bin/run examples/upload-media-from-local/main.py --subdomain <subdomain> /Users/some_user/Desktop/media/file.mp4
  ```

- To upload multiple files:

  ```bash
  bin/run examples/upload-media-from-local/main.py --subdomain <subdomain> /Users/some_user/Desktop/media/*
  ```

- To upload on behalf of another user:

  ```bash
  bin/run examples/upload-media-from-local/main.py --subdomain <subdomain> /Users/some_user/Desktop/media/file.mp4 --user-id 3
  ```
