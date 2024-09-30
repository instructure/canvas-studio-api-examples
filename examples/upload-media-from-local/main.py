import os

from utils.utils import PublicAPIClient, request_with_retry, get_commandline_arguments


def main():
    args = get_commandline_arguments(
        [
            (["files"], {"nargs": "+", "help": "path to the media file(s)"}),
            (["--collection-id"], {"type": int, "help": "upload into a collection"}),
            (["--user-id"], {"type": int, "help": "upload on behalf of a user"}),
        ]
    )

    public_api_client = PublicAPIClient(args.config)
    for media_file in args.files:
        media_filename = os.path.basename(media_file)
        print(f"Uploading {media_filename}")
        with open(media_file, "rb") as f:
            media_id, presigned_url = create_media(public_api_client, args.user_id, args.collection_id)
            upload_file(presigned_url, f)
            mark_media_as_uploaded(public_api_client, media_id, media_filename)
        print(f"Uploaded {media_filename}")


def create_media(public_api_client, user_id, collection_id):
    params={}
    if collection_id:
      params["collection_id"] = collection_id
    if user_id:
      params["user_id"] = user_id

    response = public_api_client.request(
        "post",
        "media/uploads",
        params,
    )
    if response.status_code != 201:
        raise Exception(f"Could not create media: {response.text}")
    response_body = response.json()
    return (
        response_body["upload"]["id"],
        response_body["upload"]["url"],
    )


def upload_file(presigned_url, f):
    response = request_with_retry(
        "put",
        presigned_url,
        data=f,
    )
    if response.status_code != 200:
        raise Exception(f"Could not upload file: {response.text}")


def mark_media_as_uploaded(public_api_client, media_id, media_filename):
    response = public_api_client.request(
        "post", f"media/uploads/{media_id}/complete", params={"title": media_filename}
    )
    if response.status_code != 200:
        raise Exception(f"Could not mark media as uploaded: {response.text}")


if __name__ == "__main__":
    main()
