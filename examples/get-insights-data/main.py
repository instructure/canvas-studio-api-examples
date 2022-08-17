import os
import csv
from utils.utils import PublicAPIClient, get_commandline_arguments


def main():
    args = get_commandline_arguments(
        [
            (
                ["course_id"],
                {"type": int, "help": "id of the course to get insights for"},
            )
        ]
    )
    public_api_client = PublicAPIClient(args.subdomain)
    perspectives = fetch_course_perspectives(public_api_client, args.course_id)
    course_data = fetch_course_data(public_api_client, args.course_id)

    construct_summary(public_api_client, perspectives, course_data)
    construct_user_insights(public_api_client, perspectives, course_data)


def fetch_course_perspectives(public_api_client, course_id):
    response = public_api_client.request("get", f"courses/{course_id}/perspectives")
    return response.json()["perspectives"]


def fetch_course_data(public_api_client, course_id):
    response = public_api_client.request("get", f"courses/{course_id}")
    return response.json()["course"]


def construct_summary(public_api_client, perspectives, course):
    headers = [
        "Course ID",
        "Course Title",
        "Perspective UUID",
        "Perspective Title",
        "Views",
        "Time Viewed [min]",
        "Unique Viewers",
    ]
    csv_data = []
    for perspective in perspectives:
        perspective_data = [
            course["course_id"],
            course["name"],
            perspective["uuid"],
            perspective["title"],
        ]
        print(f"Collecting insights summary for perspective {perspective['uuid']}")
        summary_csv = list(
            get_csv(
                public_api_client,
                f"perspectives/{perspective['uuid']}/insights/overview",
            )
        )
        csv_data.append(
            perspective_data
            + [
                get_value_from_row(summary_csv[1], "Views", 0),
                get_value_from_row(summary_csv[2], "Time Viewed [min]", 0),
                get_value_from_row(summary_csv[3], "Unique Viewers", 0),
            ]
        )

    write_csv_file(
        f"summary-{public_api_client.subdomain}-{course['course_id']}.csv", headers, csv_data
    )


def construct_user_insights(public_api_client, perspectives, course):
    headers = [
        "Course ID",
        "Course Title",
        "Perspective UUID",
        "Perspective Title",
        "Name",
        "Email",
        "Role",
        "Completion rate",
    ]
    csv_data = []
    for perspective in perspectives:
        perspective_data = [
            course["course_id"],
            course["name"],
            perspective["uuid"],
            perspective["title"],
        ]
        print(f"Collecting users insights for perspective {perspective['uuid']}")
        users_csv = get_csv(
            public_api_client,
            f"perspectives/{perspective['uuid']}/insights/users",
            parsed=True,
        )
        for row in users_csv:
            csv_data.append(
                perspective_data
                + [
                    row["Name"],
                    row["Email"],
                    row["Role"],
                    row["Completion rate [%]"],
                ]
            )

    write_csv_file(
        f"users-{public_api_client.subdomain}-{course['course_id']}.csv", headers, csv_data
    )


def get_value_from_row(row, name, default_value):
    if row[0] != name:
        raise Exception("Insights API has changed. Please file a support week ticket.")
    try:
        return row[1]
    except IndexError:
        return default_value


def get_csv(public_api_client, url, parsed=False):
    response = public_api_client.request("get", url)
    content = response.content.decode("utf-8").splitlines()
    if parsed:
        return csv.DictReader(content)
    return csv.reader(content)


def write_csv_file(name, headers, data):
    with open(name, "w") as csv_file:
        print(f"Writing data to {os.path.realpath(csv_file.name)}")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(data)


if __name__ == "__main__":
    main()
