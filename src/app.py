import json
import os
from datetime import datetime, timezone, timedelta

import boto3
import requests

ATCODER_USERNAME = os.environ["ATCODER_USERNAME"]
NOTIFY_TOPIC_ARN = os.environ["NOTIFY_TOPIC_ARN"]
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

TIMEZONE = timezone(timedelta(hours=9))  # JST


def lambda_handler(event, context):
    message = get_atcoder_results()
    notify(f"AtCoder Results", message)


def get_atcoder_results():
    r = requests.get(f"https://kenkoooo.com/atcoder/atcoder-api/results?user={ATCODER_USERNAME}")
    if r.status_code != 200:
        return "Failed"
    response = r.json()

    # count daily accepted
    acs = {}
    for problem in response:
        if problem["result"] != "AC":
            continue
        resolve_date = datetime.fromtimestamp(problem["epoch_second"], TIMEZONE).strftime("%Y-%m-%d")
        if resolve_date not in acs:
            acs[resolve_date] = 0
        acs[resolve_date] += 1
    accepted = sum(acs.values())

    (streak, today_accepted) = get_current_streak(acs)
    longest_streak = get_longest_streak(acs)

    message = \
        f"Accepted: {accepted}\n" + \
        f"Longest Streak: {longest_streak} days\n" + \
        f"Current Streak: {streak} days"
    if not today_accepted:
        message += " (Not Accepted today !!!)"
    message += f"\nhttps://kenkoooo.com/atcoder/#/user/{ATCODER_USERNAME}\n"
    return message


def get_current_streak(acs):
    streak = 0
    today_accepted = False
    now = datetime.now(TIMEZONE)
    if now.strftime("%Y-%m-%d") in acs:
        today_accepted = True
        streak = 1
    d = now - timedelta(days=1)
    while True:
        date = d.strftime("%Y-%m-%d")
        if date not in acs:
            break
        streak += 1
        d -= timedelta(days=1)

    return streak, today_accepted


def get_longest_streak(acs):
    longest_streak = 0
    streak = 0
    first_date = min(acs.keys())
    d = datetime.now(TIMEZONE)
    while True:
        date = d.strftime("%Y-%m-%d")
        if date in acs:
            streak += 1
        else:
            longest_streak = max(longest_streak, streak)
            streak = 0
        d -= timedelta(days=1)
        if date == first_date:
            break
    return longest_streak


def notify(title, message):
    if len(NOTIFY_TOPIC_ARN) > 0:
        notify_sns(NOTIFY_TOPIC_ARN, title, message)
    if len(SLACK_WEBHOOK_URL) > 0:
        notify_slack(SLACK_WEBHOOK_URL, title, message)


def notify_slack(url, title, message):
    requests.post(url, data=json.dumps({
        "attachments": [
            {
                "color": "#36a64f",
                "pretext": title,
                "text": message
            }
        ]
    }))


def notify_sns(topic, title, message):
    sns_client = boto3.client("sns")
    sns_client.publish(
        TopicArn=topic,
        Subject=title,
        Message=message
    )
