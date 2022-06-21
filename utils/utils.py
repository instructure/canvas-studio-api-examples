import argparse
import json
import os
import requests
import time


class PublicAPIClient:
    def __init__(self, subdomain):
        self.subdomain = subdomain
        self.config_path = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "..", "config.json")
        )
        self._load_config()

    def request(self, method, url, params=None, data=None):
        response = request_with_retry(
            method,
            f"https://{self.subdomain}.instructuremedia.com/api/public/v1/{url}",
            headers={
                "Authorization": f"Bearer {self.config['access_token']}",
            },
            params=params,
            data=data,
        )
        if response.status_code == 401:
            self.refresh_tokens()
            response = self.request(method, url, params=params, data=data)
        return response

    def refresh_tokens(self):
        response = request_with_retry(
            "post",
            f"https://{self.subdomain}.instructuremedia.com/api/public/oauth/token",
            data={
                "client_id": self.config["client_id"],
                "client_secret": self.config["client_secret"],
                "refresh_token": self.config["refresh_token"],
                "grant_type": "refresh_token",
            },
        )
        if response.status_code != 200:
            raise Exception(f"Could not refresh tokens: {response.text}")
        self.config.update(
            {
                "access_token": response.json()["access_token"],
                "refresh_token": response.json()["refresh_token"],
            }
        )
        self._save_config()

    def _load_config(self):
        with open(self.config_path, "rt") as f:
            try:
                self.config = json.load(f)
            except json.decoder.JSONDecodeError:
                raise Exception("config.json is invalid, please format it as JSON")
        for required_key in [
            "access_token",
            "client_id",
            "client_secret",
            "refresh_token",
        ]:
            if required_key not in self.config:
                raise Exception(
                    f"Required configuration parameter '{required_key}' missing from config.json"
                )

    def _save_config(self):
        with open(self.config_path, "wt") as f:
            json.dump(self.config, f, indent=4, sort_keys=True)


def request_with_retry(method, url, headers=None, params=None, data=None, retry=3):
    response = getattr(requests, method)(url, headers=headers, params=params, data=data)
    if response.status_code >= 500:
        if retry > 0:
            time.sleep(3)
            response = request_with_retry(
                method,
                url,
                headers=headers,
                params=params,
                data=data,
                retry=retry - 1,
            )
    return response


def get_commandline_arguments(additional_arguments=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subdomain", type=str, required=True, help="subdomain of the Studio account"
    )
    if additional_arguments:
        for args, kwargs in additional_arguments:
            parser.add_argument(*args, **kwargs)
    return parser.parse_args()
