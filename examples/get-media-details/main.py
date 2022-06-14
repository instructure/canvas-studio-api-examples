import json

from utils.utils import PublicAPIClient, get_commandline_arguments


def main():
    args = get_commandline_arguments(
        [
            (["media_id"], {"type": int, "help": "the media to get details about"}),
        ]
    )
    media_id = args.media_id

    public_api_client = PublicAPIClient(args.subdomain)
    media = get_media_details(public_api_client, media_id)
    captions = get_media_details(public_api_client, media_id, "caption_files")
    courses = get_media_details(public_api_client, media_id, "courses")
    tags = get_media_details(public_api_client, media_id, "tags")
    users = get_media_details(public_api_client, media_id, "users", "user_permissions")

    response = get_subdict(
        media,
        [
            "id",
            "title",
            "description",
            "duration",
            "size",
            "created_at",
            "owner",
            "collection",
        ],
    )
    response.update(
        {
            "captions": captions,
            "courses": courses,
            "tags": tags,
            "users": users,
        }
    )

    print(
        json.dumps(
            response,
            indent=4,
            sort_keys=True,
        )
    )


def get_media_details(
    public_api_client, media_id, detail_url=None, detail_attribute=None
):
    if detail_url:
        url = f"media/{media_id}/{detail_url}"
        if detail_attribute is None:
            detail_attribute = detail_url
    else:
        url = f"media/{media_id}"
        detail_attribute = "media"
    response = public_api_client.request("get", url)
    if response.status_code != 200:
        raise Exception(f"Could not get details for {url}: {response.text}")
    return response.json()[detail_attribute]


def get_subdict(dict_, keys):
    return {key: dict_[key] for key in keys}


if __name__ == "__main__":
    main()
