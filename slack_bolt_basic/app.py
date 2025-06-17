import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from backend import lol_chain

from openai import APIError

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("안녕")
def message_hello(message, say):
    message_text = message["text"]
    response = lol_chain(message_text, [])
    say(response, thread_ts=message["ts"])

@app.event("app_mention")
def lol_player(event, say):
    print(event)
    thread_ts = event.get("thread_ts") or event["ts"]
    text = event["text"]
    conversations = app.client.conversations_replies(channel=event['channel'], ts=thread_ts)
    context = [
        ('ai' if msg['user'] == 'U0903V0P47R' else 'human', msg['text'])
        for msg in conversations.data['messages']
    ][:-1]

    try:
        response = lol_chain(text, context)
    except APIError as e:
        response = f"API error: {e}"
        return say(blocks=error_template(e)['blocks'], thread_ts=thread_ts)

    say(text=response, thread_ts=thread_ts) 


def error_template(error: APIError):
    notification_template = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "An error occurred in the API:"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Message:*\n{error.message}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Status Code:* {error.status_code}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Request ID:* {error.request_id if error.request_id else 'N/A'}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Code:* {error.code if error.code else 'None'}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "For more details, please check the logs or contact support."
                    }
                ]
            }
        ]
    }
    return notification_template


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()