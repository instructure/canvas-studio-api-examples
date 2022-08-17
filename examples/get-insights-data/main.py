import os
import sys
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
    construct_student_insights(public_api_client, perspectives, course_data)


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
            course["id"],
            course["name"],
            perspective["uuid"],
            perspective["title"],
        ]
        summary_csv = get_csv(
            public_api_client, f"perspectives/{perspective['uuid']}/insights/overview"
        )
        for row in summary_csv:
            if "Views" in row:
                perspective_data.append(row[1])
            elif "Time Viewed [min]" in row:
                perspective_data.append(row[1])
            elif "Unique Viewers" in row and len(row) == 2:
                perspective_data.append(row[1])
        csv_data.append(perspective_data)

    write_csv_file(
        f"summary-{public_api_client.subdomain}-{course['id']}.csv", headers, csv_data
    )


def construct_student_insights(public_api_client, perspectives, course):
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
            course["id"],
            course["name"],
            perspective["uuid"],
            perspective["title"],
        ]
        users_csv = get_csv(
            public_api_client,
            f"perspectives/{perspective['uuid']}/insights/users",
            parsed=True,
        )
        for row in users_csv:
            perspective_data.append(row["Name"])
            perspective_data.append(row["Email"])
            perspective_data.append(row["Role"])
            perspective_data.append(row["Completion rate [%]"])
        csv_data.append(perspective_data)

    write_csv_file(
        f"student-{public_api_client.subdomain}-{course['id']}.csv", headers, csv_data
    )


def get_csv(public_api_client, url, parsed=False):
    response = public_api_client.request("get", url)
    content = response.content.decode("utf-8").splitlines()
    if parsed:
        return csv.DictReader(content)
    return csv.reader(content)


def write_csv_file(name, headers, data):
    with open(name, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(data)


if __name__ == "__main__":
    main()
