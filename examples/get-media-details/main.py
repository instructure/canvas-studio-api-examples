import json

from utils.utils import PublicAPIClient, get_commandline_arguments


def main():
    args = get_commandline_arguments(
        [
            (["media_id"], {"type": int, "help": "the media to get details about"}),
        ]
    )

    media_detailer = MediaDetailer(args.config, args.media_id)
    media = media_detailer.get()

    captions = media_detailer.get("caption_files")
    courses = media_detailer.get("courses")
    tags = media_detailer.get("tags")
    users = media_detailer.get("users", "user_permissions")

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


class MediaDetailer:
    def __init__(self, config, media_id):
        self.public_api_client = PublicAPIClient(config)
        self.media_id = media_id

    def get(self, detail_url=None, detail_attribute=None):
        if detail_url:
            url = f"media/{self.media_id}/{detail_url}"
            if detail_attribute is None:
                detail_attribute = detail_url
        else:
            url = f"media/{self.media_id}"
            detail_attribute = "media"
        response = self.public_api_client.request("get", url)
        if response.status_code != 200:
            raise Exception(f"Could not get details for {url}: {response.text}")
        return response.json()[detail_attribute]


def get_subdict(dict_, keys):
    return {key: dict_[key] for key in keys}


if __name__ == "__main__":
    main()
