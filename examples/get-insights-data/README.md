# Get viewership insights of all the videos in a course

This script collects and saves the following information about videos into two csv files:
- Summary file:
  - Course ID - id of the course in Canvas LMS
  - Course Title - Name of the course in Canvas LMS
  - Perspective UUID - Unique id string of the video
  - Perspective Title - Title of the video
  - Views - The number of views of the video
  - Time Viewed [min] - The accumulated time spent watching the video
  - Unique Viewers - The number of unique users who watched the video

- Users file:
  - Course ID - id of the course in Canvas LMS
  - Course Title - Name of the course in Canvas LMS
  - Perspective UUID - Unique id string of the video
  - Perspective Title - Title of the video
  - Name - Name of the user
  - Email - Email of the user
  - Role - Role(s) of the user
  - Completion rate - Percentage of how much of the video did this user watch

## How to use

Before using this script, don't forget to configure your OAuth credentials (see [here](../../README.md#authorization)).

```bash
bin/run examples/get-insights-data/main.py <course_id>
```
