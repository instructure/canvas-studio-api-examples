from pathlib import Path
import logging
from datetime import datetime
from requests import HTTPError

from utils.utils import PublicAPIClient, get_commandline_arguments


def main():
    args = get_commandline_arguments(
        [
            (
                ["--root_dir"],
                {"type": str, "help": "Root directory for the dump", "required": True},
            ),
            (["--log_to_file"], {"action": "store_true", "help": "Create a log file"}),
            (
                ["--dry_run"],
                {
                    "action": "store_true",
                    "help": "Don't download, just create the directory structure locally",
                },
            ),
        ]
    )
    print(args)
    mediaDownloader = MediaDownloader(
        args.config, args.root_dir, args.log_to_file, args.dry_run
    )

    print("Getting all media ids")
    media_ids = mediaDownloader.get_all_media_ids_in_account()
    print(f"Found {len(media_ids)} media in the account")

    print("Getting collection and caption information for all media")
    media_objects = mediaDownloader.enrich_all_media_with_collection_and_captions(
        media_ids
    )
    print("Getting collection, course and caption information for all media")

    print("Start download")
    mediaDownloader.download_all_media(media_objects)
    print("Download is complete")


class MediaDownloader:
    def __init__(self, config, root_dir, log_to_file, dry_run):
        self.public_api_client = PublicAPIClient(config)
        self.log_to_file = log_to_file
        self.dry_run = dry_run
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

        if log_to_file:
            logfile_path = f"{root_dir}/media_dump_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.log"
            log_format = "%(asctime)s - %(levelname)s - %(message)s"
            logging.basicConfig(
                filename=logfile_path, level=logging.INFO, format=log_format
            )
        self.logger = logging.getLogger(__name__)

    def get_all_media_ids_in_account(self):
        response = self.search_media(1)
        media_ids = [
            media["id"]
            for media in response.json()["media"]
            if MediaDownloader.is_media_downloadable(media)
        ]
        last_page = response.json()["meta"]["last_page"]
        total_count = response.json()["meta"]["total_count"]
        self.logger.info(f"There are {total_count} videos on {last_page} page.")
        if last_page > 1:
            for page in range(2, last_page + 1):
                response = self.search_media(page)
                media_ids.extend(
                    [
                        media["id"]
                        for media in response.json()["media"]
                        if MediaDownloader.is_media_downloadable(media)
                    ]
                )
        self.logger.info(f"Found media ids: {media_ids}")
        return media_ids

    def search_media(self, page):
        self.logger.info(f"Getting {page}. page")
        response = self.public_api_client.request(
            "get", "media/search", params={"page": page, "per_page": 50}
        )
        if not response.ok:
            self.logger.error(f"Could not get all media on page {page}.")
            response.raise_for_status()
        return response

    @staticmethod
    def is_media_downloadable(media):
        return media["transcoding_status"] == "transcoding_finished"

    def enrich_all_media_with_collection_and_captions(self, media_ids):
        media_objects = []
        for id in media_ids:
            media_with_details = self.get_details_of_media(id)
            if media_with_details:
                media_with_details.update(self.get_captions_of_media(id))
                media_with_details.update(self.get_courses_of_media(id))
                media_objects.append(media_with_details)
        return media_objects

    def get_details_of_media(self, media_id):
        self.logger.info(f"Getting details of media: {media_id}")
        try:
            response = self.public_api_client.request("get", f"media/{media_id}")
            if not response.ok:
                self.logger.error(f"Could not get details for media with id {media_id}")
                response.raise_for_status()
        except HTTPError as e:
            print(e)
            return False
        return response.json()["media"]

    def get_courses_of_media(self, media_id):
        try:
            response = self.public_api_client.request(
                "get", f"media/{media_id}/courses"
            )
            if not response.ok:
                self.logger.error(f"Could not get courses for media with id {media_id}")
                response.raise_for_status()
        except HTTPError as e:
            print(e)
            return {"courses": []}
        return response.json()

    def get_captions_of_media(self, media_id):
        self.logger.info(f"Getting caption data for media: {media_id}")
        try:
            response = self.public_api_client.request(
                "get", f"media/{media_id}/caption_files"
            )
            if not response.ok:
                self.logger.error(
                    f"Could not get caption files for media with id {media_id}"
                )
                response.raise_for_status()
            captions = [
                caption
                for caption in response.json()["caption_files"]
                if (caption["status"] == "published" or caption["status"] == "uploaded")
            ]

        except HTTPError as e:
            print(e)
            captions = []

        return {"caption_files": captions}

    def download_all_media(self, media_objects):
        if self.dry_run:
            print("--dry_run was on: creating directory structure only")

        for media in media_objects:
            user_name = media["owner"]["full_name"]

            for directory in self.get_directory_names(media):
                collection_path = self.root_dir / user_name / directory
                collection_path.mkdir(parents=True, exist_ok=True)

                if not self.dry_run:
                    self.download_a_media(collection_path, media)

    def get_directory_names(self, media):
        names = [course["name"] for course in media["courses"]]
        if not names:
            return [media["collection"]["name"]]
        if media["collection"]["type"] != "user":
            names.append(media["collection"]["name"])
        return set(names)

    def download_a_media(self, path, media):
        title = media["title"].replace("/", "").replace(":", "").replace("\n", " ")

        if media["caption_files"]:
            for caption in media["caption_files"]:
                self.download_a_caption(path, caption, title)

        media_path = path / (title + ".mp4")
        self.logger.info(f"Downloading media with id: {media['id']}")
        try:
            response = self.public_api_client.request(
                "get", f"media/{media['id']}/download"
            )
            if not response.ok:
                self.logger.error(f"Could not download media {media['id']}")
                response.raise_for_status()
            open(media_path, "wb").write(response.content)
            self.logger.info(f"Media saved to: {media_path}")
        except HTTPError as e:
            print(e)

    def download_a_caption(self, path, caption, media_title):
        caption_path = path / ".".join(
            [media_title, caption["srclang"], caption["subtitle_format"]]
        )
        self.logger.info(f"Downloading caption with id: {caption['id']}")
        try:
            response = self.public_api_client.request(
                "get", f"caption_files/{caption['id']}/download"
            )
            if not response.ok:
                self.logger.error(f"Could not download caption {caption['id']}")
                response.raise_for_status()

            open(caption_path, "wb").write(response.content)
            self.logger.info(f"Caption saved to: {caption_path}")
        except HTTPError as e:
            print(e)


if __name__ == "__main__":
    main()
