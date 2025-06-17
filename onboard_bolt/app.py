import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.event("team_join")
def ask_for_introduction(event, say):
    welcome_channel_id = "D0903V0Q9MM"
    user_id = event["user"]
    text = f"안녕하세요. <@{user_id}>! 🎉 이 채널에서 온보딩에 필요한 정보들을 물어보세요."
    say(text=text, channel=welcome_channel_id)


def is_im_message(event):
    return event.get("channel_type", "") == "im"


@app.event(event={
    "type": "message",
    "subtype": None,
}, matchers=[is_im_message])
def message_im_event(event, say):
    print(event)


@app.event(event={
    "type": "message",
    "subtype": "message_changed",
}, matchers=[is_im_message])
def message_im_change_event(event, say):
    print(event)

@app.event("message")
def handle_message(event, say):
    print(event)

if __name__ == "__main__":
    SocketModeHandler(app, os.getenv('SLACK_APP_TOKEN')).start()