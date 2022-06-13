from utils.utils import PublicAPIClient, get_standard_arguments


def main():
    args = get_standard_arguments()

    public_api_client = PublicAPIClient(args.subdomain)
    public_api_client.refresh_tokens()
    response = public_api_client.request("get", "ping")

    if response.status_code == 200 and response.text == "pong":
        print("You have successfully configured your public API access.")
    else:
        print("Error happened during public API access test")
        print("status_code:", response.status_code)
        print("response body:", response.text)


if __name__ == "__main__":
    main()
